"""Evaluate Text-to-SQL predictions against the repository's SQLite dataset.

Adds a balanced execution accuracy metric, latency summaries, paired statistical
comparisons, charts and a reproducible Markdown report. No fabricated scores.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sqlite3
import statistics
import time
from collections import Counter
from pathlib import Path

csv.field_size_limit(1_000_000_000)

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT.parent / "Assignments" / "Task_2" / "data"
FRAMEWORKS = ("co_star", "rtf", "icio")


def load_labels(path: Path) -> dict[str, list]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    labels = {row["question"]: json.loads(row["result"]) for row in rows}
    if len(labels) != len(rows):
        raise ValueError("Duplicate label questions; a stable row ID is required")
    return labels


def load_predictions(path: Path, labels: dict[str, list]) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if any(set(("question", "predicted_sql")) - row.keys() for row in rows):
        raise ValueError(f"Missing question/predicted_sql header: {path}")
    data = {row["question"]: row["predicted_sql"] for row in rows}
    if len(data) != len(rows):
        raise ValueError(f"Repeated question in {path}")
    if set(data) != set(labels):
        raise ValueError(f"{path}: expected exactly {len(labels)} predictions, found {len(data)}. "
                         "Do not calculate final results on a --limit smoke test.")
    return data


def load_latency(path: Path) -> dict[str, float]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["question"]: float(row["latency_seconds"]) for row in rows
            if row.get("latency_seconds") and row.get("status") == "ok"}


def load_official_database(data_dir: Path) -> sqlite3.Connection:
    script = data_dir / "evaluate_retrieval_predictions.py"
    spec = importlib.util.spec_from_file_location("official_evaluator", script)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot import the repository evaluator: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    connection = module.load_database()  # Preserve the official loading semantics.
    connection.execute("PRAGMA query_only = ON")
    return connection


def execute_query(connection: sqlite3.Connection, sql: str,
                  max_seconds: float = 3.0, max_rows: int = 100_000) -> list[tuple]:
    if not sql or not sql.lstrip().upper().startswith(("SELECT ", "SELECT\n", "WITH ", "WITH\n")):
        raise ValueError("SQL is missing or is not a read-only SELECT/WITH statement")
    deadline = time.monotonic() + max_seconds
    connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 10_000)
    try:
        cursor = connection.execute(sql)
        rows = cursor.fetchmany(max_rows + 1)
        if len(rows) > max_rows:
            raise ValueError(f"More than {max_rows} rows returned; query capped for safety")
        return rows
    finally:
        connection.set_progress_handler(None, 0)


def pct(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else float("nan")


def exact_mcnemar_p(b: int, c: int) -> float:
    """Two-sided exact binomial McNemar test for discordant paired outcomes."""
    n = b + c
    if n == 0:
        return 1.0
    lower = sum(math.comb(n, k) for k in range(min(b, c) + 1))
    return min(1.0, 2.0 * lower / (2 ** n))


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Holm familywise correction; output maintains original ordering."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted = [0.0] * len(pvalues)
    prior = 0.0
    for rank, index in enumerate(order):
        prior = max(prior, min(1.0, (len(pvalues) - rank) * pvalues[index]))
        adjusted[index] = prior
    return adjusted


def cochrans_q(binary: dict[str, list[int]]) -> tuple[float, float]:
    """Paired global test of 3 frameworks, with chi-square(df=2) approximation."""
    names = list(binary)
    if len(names) != 3:
        raise ValueError("This Q-test implementation supports exactly three frameworks")
    if len(set(map(len, binary.values()))) != 1:
        raise ValueError("Predictions must use the same questions in the same order")
    k = 3
    totals = [sum(binary[name]) for name in names]
    row_sums = [sum(binary[name][i] for name in names) for i in range(len(binary[names[0]]))]
    total = sum(totals)
    denominator = k * total - sum(x*x for x in row_sums)
    if denominator == 0:
        return 0.0, 1.0
    q = (k - 1) * (k * sum(x*x for x in totals) - total*total) / denominator
    return q, math.exp(-max(0.0, q) / 2.0)  # Survival function for chi² with df=2.


def save_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def draw_charts(metrics: list[dict], latencies: dict[str, list[float]], dest: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping plots; run pip install matplotlib")
        return

    names = [row["framework"] for row in metrics]
    x = list(range(len(names)))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([v-width/2 for v in x], [100*row["execution_accuracy"] for row in metrics],
           width, label="Execution accuracy")
    ax.bar([v+width/2 for v in x], [100*row["balanced_accuracy"] for row in metrics],
           width, label="Balanced execution accuracy")
    ax.set_xticks(x, names)
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.set_title("Text-to-SQL accuracy by framework")
    fig.tight_layout()
    fig.savefig(dest / "accuracy_comparison.png", dpi=160)
    plt.close(fig)

    valid = [(name, latencies[name]) for name in names if latencies[name]]
    if valid:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.boxplot([v for _name, v in valid], tick_labels=[k for k, _v in valid])
        ax.set_ylabel("Inference latency (seconds)")
        ax.set_title("One-call latency distribution (successful requests only)")
        fig.tight_layout()
        fig.savefig(dest / "latency_boxplot.png", dpi=160)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "analysis")
    parser.add_argument("--query-timeout", type=float, default=3.0)
    args = parser.parse_args()

    labels = load_labels(args.data_dir / "restaurants_dataset.csv")
    preds = {name: load_predictions(args.results_dir / f"predictions_{name}.csv", labels)
             for name in FRAMEWORKS}
    metadata = {name: load_latency(args.results_dir / f"meta_{name}.csv")
                for name in FRAMEWORKS}
    questions = list(labels)
    details: list[dict] = []
    binary = {name: [] for name in FRAMEWORKS}
    query_success = {name: 0 for name in FRAMEWORKS}
    empty_counts = {name: {True: 0, False: 0} for name in FRAMEWORKS}
    total_counts = {True: sum(not labels[q] for q in questions),
                    False: sum(bool(labels[q]) for q in questions)}
    connection = load_official_database(args.data_dir)
    try:
        for framework in FRAMEWORKS:
            for question in questions:
                expected = labels[question]
                sql = preds[framework][question]
                correct, status, returned = 0, "valid", -1
                try:
                    rows = execute_query(connection, sql, max_seconds=args.query_timeout)
                    query_success[framework] += 1
                    returned = len(rows)
                    correct = int(Counter(map(tuple, rows)) ==
                                  Counter(map(tuple, expected)))
                except (sqlite3.Error, ValueError) as e:
                    status = f"error: {type(e).__name__}: {str(e)[:160]}"
                binary[framework].append(correct)
                empty_counts[framework][not expected] += correct
                details.append({"framework": framework, "question": question,
                                "expected_is_empty": not bool(expected),
                                "correct": correct, "query_status": status,
                                "returned_rows": returned,
                                "sql": sql})
    finally:
        connection.close()

    metrics = []
    delays = {}
    for framework in FRAMEWORKS:
        n = len(questions)
        nonempty = pct(empty_counts[framework][False], total_counts[False])
        empty = pct(empty_counts[framework][True], total_counts[True])
        balanced = (nonempty + empty) / 2
        delays[framework] = list(metadata[framework].values())
        metrics.append({
            "framework": framework,
            "correct": sum(binary[framework]), "total": n,
            "execution_accuracy": sum(binary[framework]) / n,
            "nonempty_accuracy": nonempty,
            "empty_accuracy": empty,
            "balanced_accuracy": balanced,
            "valid_sql_rate": query_success[framework] / n,
            "mean_latency_sec": (statistics.mean(delays[framework]) if delays[framework] else float("nan")),
            "median_latency_sec": (statistics.median(delays[framework]) if delays[framework] else float("nan")),
            "timed_calls": len(delays[framework]),
        })
    q_stat, q_p = cochrans_q(binary)
    comparisons = []
    for i, left in enumerate(FRAMEWORKS):
        for right in FRAMEWORKS[i+1:]:
            b = sum(x == 1 and y == 0 for x,y in zip(binary[left],binary[right]))
            c = sum(x == 0 and y == 1 for x,y in zip(binary[left],binary[right]))
            comparisons.append({"left": left, "right": right, "left_only_correct": b,
                                "right_only_correct": c, "p_raw": exact_mcnemar_p(b,c)})
    adjusted = holm_adjust([row["p_raw"] for row in comparisons])
    for row, corrected in zip(comparisons, adjusted):
        row["p_holm"] = corrected

    args.report_dir.mkdir(parents=True, exist_ok=True)
    save_csv(args.report_dir / "metrics.csv", metrics)
    save_csv(args.report_dir / "question_level_analysis.csv", details)
    save_csv(args.report_dir / "paired_tests.csv", comparisons)
    draw_charts(metrics, delays, args.report_dir)
    report = [
        "# Week 03 — Prompt comparison (generated report)", "",
        f"**Protocol:** {len(questions)} independent questions are sent to each prompt, one stateless call per question. "
        "Execution accuracy compares the multisets of result rows; row ordering is ignored.", "",
        "## Task 2 — Execution accuracy and latency", "",
        "| Framework | Correct / Total | Accuracy | Valid SQL | Mean latency (s) | Median latency (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for m in metrics:
        report.append(f"| {m['framework']} | {m['correct']} / {m['total']} | "
                      f"{m['execution_accuracy']:.2%} | {m['valid_sql_rate']:.2%} | "
                      f"{m['mean_latency_sec']:.3f} | {m['median_latency_sec']:.3f} |")
    report += ["", "![Accuracy comparison](accuracy_comparison.png)",
               "", "![Latency distribution](latency_boxplot.png)", "",
               "## Task 3 — Additional metric: balanced execution accuracy", "",
               "The published accuracy is the fraction of questions with exactly correct executed "
               "result rows. Empty answers account for "
               f"{total_counts[True]}/{len(questions)} questions. A generator could get those "
               "cases right by returning empty results without understanding the SQL request.", "",
               "**Balanced execution accuracy** is the average of (a) execution accuracy on "
               "questions whose gold result is empty and (b) execution accuracy on questions "
               "whose gold result is non-empty. Each group receives 50% weight regardless "
               "of its size. It complements — rather than replaces — ordinary execution accuracy.", "",
               "| Framework | Non-empty group | Empty group | Balanced accuracy |",
               "|---|---:|---:|---:|",
    ]
    for m in metrics:
        report.append(f"| {m['framework']} | {m['nonempty_accuracy']:.2%} | "
                      f"{m['empty_accuracy']:.2%} | {m['balanced_accuracy']:.2%} |")
    report += ["", "## Task 4 — Paired significance tests", "",
               f"Cochran's Q (three matched frameworks): Q = {q_stat:.4f}, df = 2, "
               f"asymptotic p = {q_p:.6g}.", "",
               "Pairwise exact two-sided McNemar tests, with Holm correction for "
               "three simultaneous comparisons:", "",
               "| Comparison | Left-only correct | Right-only correct | Raw p | Holm p |",
               "|---|---:|---:|---:|---:|",
    ]
    for row in comparisons:
        report.append(f"| {row['left']} vs {row['right']} | {row['left_only_correct']} | "
                      f"{row['right_only_correct']} | {row['p_raw']:.6g} | {row['p_holm']:.6g} |")
    report += ["", "**Interpretation guidance:** p < 0.05 after Holm correction gives evidence of "
               "different *execution accuracy* on these paired questions; it does not prove "
               "that a framework is universally better. Cochran's Q is an omnibus test "
               "with a chi-square approximation. Replicate with multiple seeds/model runs "
               "for a stronger conclusion about stochastic variation.", "",
               "**Limitations:** This is one dataset and one run per prompt. API/network latency "
               "contributes to measured inference times. Frameworks use identical schema, "
               "few-shot examples, model parameters, and questions where possible. "
               "Inspect invalid SQL and extreme cases manually. Do not use gold results "
               "to generate predictions. Document model, date, settings, and coding agent.", "",
               "## Manual discussion to complete before submission", "",
               "Explain the observed trade-offs, typical SQL failures, distracting clauses, "
               "and how CO-STAR (rich structure), RTF (minimal structure), and ICIO "
               "(explicit input boundary) may have influenced the results. "
               "Record the exact model and any agent used to write or run the code."
    ]
    (args.report_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Saved:", args.report_dir)
    for m in metrics:
        print(f"  {m['framework']}: accuracy {m['execution_accuracy']:.2%}; "
              f"balanced {m['balanced_accuracy']:.2%}")
    print(f"  Cochran Q p={q_p:.6g}; pairwise McNemar/Holm results in paired_tests.csv")


if __name__ == "__main__":
    main()
