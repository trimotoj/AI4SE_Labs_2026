"""Generate Text-to-SQL predictions for each prompting framework.

No reference results are ever read by this script. Questions are handled in
independent stateless API calls (one fresh conversation per question).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Dataset contains large JSON results in CSV cells.
csv.field_size_limit(1_000_000_000)

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT.parent / "Assignments" / "Task_2" / "data"


def load_schema(path: Path) -> str:
    tables: dict[str, list[str]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for table, field, _pk, _fk, sql_type in csv.reader(f, skipinitialspace=True):
            if table.strip() == "-" or table == "Table Name":
                continue
            tables.setdefault(table.strip(), []).append(f"{field.strip()} {sql_type.strip()}")
    return "\n".join(f"{table}({', '.join(columns)})" for table, columns in tables.items())


def build_prompt(config: dict, framework: str, schema: str, question: str) -> str:
    examples = "\n".join(
        f"Question: {ex['question']}\nSQL: {ex['sql']}"
        for ex in config["few_shot_examples"]
    )
    prompt = config["frameworks"][framework]["template"]
    for token, value in {
        "{{SCHEMA}}": schema,
        "{{RULES}}": config["shared_rules"],
        "{{EXAMPLES}}": examples,
        "{{QUESTION}}": question,
    }.items():
        prompt = prompt.replace(token, value)
    return prompt


def unwrap_sql(message: str) -> str:
    text = message.strip()
    if text.startswith("```"):
        match = re.fullmatch(r"```(?:sql|sqlite)?\s*\n(.*?)\n```", text, re.I | re.S)
        if match:
            text = match.group(1).strip()
    return text


def api_call(base_url: str, api_key: str, model: str, prompt: str,
             timeout: float, temperature: float | None) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    body: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if temperature is not None:
        body["temperature"] = temperature
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(url, data=json.dumps(body).encode("utf-8"),
                      headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    content = payload["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("Model response was not plain text")
    return unwrap_sql(content)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Model ID supported by your endpoint")
    parser.add_argument("--base-url", default="https://api.openai.com/v1",
                        help="OpenAI-compatible API root, e.g. http://localhost:11434/v1")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--temperature", type=float, default=None,
                        help="Optional; omit if your model does not support temperature")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--limit", type=int, default=None,
                        help="Use only for a smoke test; not for the final evaluation")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be positive")
    if args.retries < 0:
        parser.error("--retries cannot be negative")

    config = json.loads((ROOT / "prompts.json").read_text(encoding="utf-8"))
    schema = load_schema(args.data_dir / "restaurants-schema.csv")
    # Deliberately read only question; the gold 'result' column must never enter a prompt.
    with (args.data_dir / "restaurants_dataset.csv").open(encoding="utf-8", newline="") as f:
        questions = [row["question"] for row in csv.DictReader(f)]
    if args.limit:
        questions = questions[:args.limit]
    if len(set(questions)) != len(questions):
        raise ValueError("Question IDs are needed for duplicate questions; this runner assumes unique questions")

    key = os.environ.get("LLM_API_KEY", "")
    if not key and not args.base_url.startswith(("http://localhost", "http://127.0.0.1")):
        parser.error("Set LLM_API_KEY (never commit your API key)")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for framework in config["frameworks"]:
        preds_path = args.out_dir / f"predictions_{framework}.csv"
        meta_path = args.out_dir / f"meta_{framework}.csv"
        old_predictions = {}
        old_meta = {}
        if args.resume and preds_path.exists() and meta_path.exists():
            with preds_path.open(encoding="utf-8", newline="") as f:
                old_predictions = {row["question"]: row for row in csv.DictReader(f)}
            with meta_path.open(encoding="utf-8", newline="") as f:
                old_meta = {row["question"]: row for row in csv.DictReader(f)}
            if any(row.get("model") != args.model for row in old_meta.values()):
                raise ValueError("--resume would mix different models; choose another --out-dir")
        # Keep ALL previously saved records, including those that occur after
        # the next failed question. A prefix-only checkpoint would silently
        # discard completed predictions later in the dataset on --resume.
        saved_questions = [q for q in questions if q in old_predictions and q in old_meta]
        predictions_by_question = {q: old_predictions[q] for q in saved_questions}
        metadata_by_question = {q: old_meta[q] for q in saved_questions}
        print(f"[{framework}] {len(questions)} questions", flush=True)
        for index, question in enumerate(questions):
            if question in predictions_by_question and metadata_by_question[question].get("status") == "ok":
                continue
            prompt = build_prompt(config, framework, schema, question)
            sql, status, error, latency = "", "error", "", 0.0
            for attempt in range(args.retries + 1):
                began = time.perf_counter()
                try:
                    sql = api_call(args.base_url, key, args.model, prompt,
                                   args.timeout, args.temperature)
                    latency = time.perf_counter() - began
                    status = "ok" if sql else "empty_response"
                    if status == "ok":
                        break
                except (HTTPError, URLError, KeyError, IndexError,
                        ValueError, TimeoutError, ConnectionError) as exc:
                    latency = time.perf_counter() - began
                    error = f"{type(exc).__name__}: {str(exc)[:180]}"
                if attempt < args.retries:
                    time.sleep(min(2 ** attempt, 8))
            predictions_by_question[question] = {"question": question, "predicted_sql": sql}
            metadata_by_question[question] = {
                "index": index, "question": question, "model": args.model,
                "framework": framework, "prompt_version": config["version"],
                "latency_seconds": f"{latency:.6f}", "status": status,
                "error": error, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            # Checkpoint in original dataset order. Preserve the already processed
            # records AFTER this question as well as the preceding records.
            present = [q for q in questions if q in predictions_by_question and q in metadata_by_question]
            write_csv(preds_path, ["question", "predicted_sql"],
                      [predictions_by_question[q] for q in present])
            write_csv(meta_path, ["index", "question", "model", "framework",
                                  "prompt_version", "latency_seconds", "status",
                                  "error", "timestamp_utc"],
                      [metadata_by_question[q] for q in present])
            if (index + 1) % 10 == 0:
                print(f"  {index + 1}/{len(questions)}", flush=True)
            if args.delay:
                time.sleep(args.delay)
        errors = sum(metadata_by_question[q]["status"] != "ok"
                     for q in questions if q in metadata_by_question)
        print(f"  done: {len(predictions_by_question)} predictions, API failures: {errors}")
    print("Run analyze_results.py next. API errors are NOT disguised as empty-result SQL.")


if __name__ == "__main__":
    main()
