"""Supplementary name-only Text-to-SQL evaluation for Week 03.

Run from week03_starter, with analyze_results.py alongside this file:
    python analyze_name_accuracy.py --results-dir results

Keeps the original exact execution metric, adds a name-only diagnostic to
expose broken reference IDs, and performs matched significance tests on both.
Does NOT modify gold labels, database, predictions, or the official validator.
"""
from __future__ import annotations

import argparse
import csv
import math
import sqlite3
from collections import Counter
from pathlib import Path

from analyze_results import (
    DEFAULT_DATA, FRAMEWORKS, ROOT,
    cochrans_q, exact_mcnemar_p, execute_query, holm_adjust,
    load_labels, load_official_database, load_predictions, save_csv,
)

csv.field_size_limit(1_000_000_000)


def names_only(rows: list[tuple] | list[list]) -> Counter:
    if not all(len(row) == 2 for row in rows):
        raise ValueError("The query must return exactly two columns: ID, NAME")
    return Counter(row[1] for row in rows)


def test_pairs(binary: dict[str, list[int]], measure: str) -> tuple[float, float, list[dict]]:
    q, p = cochrans_q(binary)
    pairs = []
    for i, left in enumerate(FRAMEWORKS):
        for right in FRAMEWORKS[i + 1:]:
            b = sum(a == 1 and c == 0 for a, c in zip(binary[left], binary[right]))
            c = sum(a == 0 and c == 1 for a, c in zip(binary[left], binary[right]))
            pairs.append({
                "metric": measure, "left": left, "right": right,
                "left_only_correct": b, "right_only_correct": c,
                "p_raw": exact_mcnemar_p(b, c),
            })
    for row, adj in zip(pairs, holm_adjust([r["p_raw"] for r in pairs])):
        row["p_holm"] = adj
    return q, p, pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "analysis_name")
    parser.add_argument("--query-timeout", type=float, default=3.0)
    args = parser.parse_args()

    labels = load_labels(args.data_dir / "restaurants_dataset.csv")
    preds = {
        f: load_predictions(args.results_dir / f"predictions_{f}.csv", labels)
        for f in FRAMEWORKS
    }
    questions = list(labels)
    empty_n = sum(not labels[q] for q in questions)
    nonempty_n = len(questions) - empty_n
    binary_exact = {f: [] for f in FRAMEWORKS}
    binary_name = {f: [] for f in FRAMEWORKS}
    details = []
    db = load_official_database(args.data_dir)
    try:
        name_counts = {
            name: n for name, n in db.execute(
                "SELECT NAME, COUNT(*) FROM RESTAURANT GROUP BY NAME"
            )
        }
        gold_rows = [r for q in questions for r in labels[q]]
        pair_lookup = set(map(tuple, db.execute("SELECT ID, NAME FROM RESTAURANT")))
        matched_id_name = sum(tuple(r) in pair_lookup for r in gold_rows)
        matched_names = sum(r[1] in name_counts for r in gold_rows)
        ambiguous_gold_rows = sum(name_counts.get(r[1], 0) > 1 for r in gold_rows)

        for framework in FRAMEWORKS:
            for question in questions:
                expected = labels[question]
                sql = preds[framework][question]
                exact, name, status, returned = 0, 0, "ok", -1
                try:
                    actual = execute_query(db, sql, max_seconds=args.query_timeout)
                    returned = len(actual)
                    exact = int(Counter(map(tuple, actual)) == Counter(map(tuple, expected)))
                    name = int(names_only(actual) == names_only(expected))
                except (sqlite3.Error, ValueError) as error:
                    status = f"{type(error).__name__}: {str(error)[:160]}"
                binary_exact[framework].append(exact)
                binary_name[framework].append(name)
                details.append({
                    "framework": framework, "question": question,
                    "gold_is_empty": not bool(expected),
                    "official_correct": exact, "name_only_correct": name,
                    "status": status, "returned_rows": returned,
                    "sql": sql,
                })
    finally:
        db.close()

    metrics = []
    for f in FRAMEWORKS:
        exact = binary_exact[f]
        names = binary_name[f]
        empties = [not labels[q] for q in questions]
        exact_e = sum(v for v, is_e in zip(exact, empties) if is_e) / empty_n if empty_n else math.nan
        exact_ne = sum(v for v, is_e in zip(exact, empties) if not is_e) / nonempty_n if nonempty_n else math.nan
        name_e = sum(v for v, is_e in zip(names, empties) if is_e) / empty_n if empty_n else math.nan
        name_ne = sum(v for v, is_e in zip(names, empties) if not is_e) / nonempty_n if nonempty_n else math.nan
        metrics.append({
            "framework": f,
            "total": len(questions),
            "official_correct": sum(exact),
            "official_accuracy": sum(exact) / len(questions),
            "official_balanced_accuracy": (exact_e + exact_ne) / 2,
            "name_correct": sum(names),
            "name_accuracy": sum(names) / len(questions),
            "name_empty_accuracy": name_e,
            "name_nonempty_accuracy": name_ne,
            "name_balanced_accuracy": (name_e + name_ne) / 2,
        })

    stats = []
    comparisons = []
    for metric_name, binary in (("official", binary_exact), ("name_only", binary_name)):
        q, p, rows = test_pairs(binary, metric_name)
        stats.append({"metric": metric_name, "cochrans_q": q, "p_approx": p})
        comparisons.extend(rows)

    args.report_dir.mkdir(parents=True, exist_ok=True)
    save_csv(args.report_dir / "metrics.csv", metrics)
    save_csv(args.report_dir / "question_level.csv", details)
    save_csv(args.report_dir / "paired_tests.csv", comparisons)
    save_csv(args.report_dir / "cochrans_q.csv", stats)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4.5))
        positions = range(len(FRAMEWORKS))
        width = .35
        ax.bar([i - width / 2 for i in positions], [100 * m["official_accuracy"] for m in metrics], width, label="Official exact")
        ax.bar([i + width / 2 for i in positions], [100 * m["name_accuracy"] for m in metrics], width, label="Name-only (supplementary)")
        ax.set_xticks(list(positions), FRAMEWORKS)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Matching questions (%)")
        ax.set_title("Exact execution vs. name-only match")
        ax.legend()
        fig.tight_layout()
        fig.savefig(args.report_dir / "accuracy_comparison.png", dpi=160)
        plt.close(fig)
    except ImportError:
        print("Install matplotlib for chart generation: pip install matplotlib")

    lines = [
        "# Supplementary analysis: inconsistent restaurant IDs", "",
        "The official execution evaluator compares complete `(ID, NAME)` result-row multisets.",
        "Its result is preserved without modification. The supplementary name-only metric",
        "compares multisets of `NAME` values, ignoring the first (ID) column. It requires",
        "two output columns. This helps diagnose changed or inconsistent IDs but cannot",
        "distinguish restaurants sharing a name. Empty results count as exact name matches.", "",
        "## Reference-data integrity audit", "",
        f"- Database restaurant rows: {len(pair_lookup)}",
        f"- Expected output rows: {len(gold_rows)}",
        f"- Existing expected `(ID, NAME)` pairs: {matched_id_name}/{len(gold_rows)}",
        f"- Expected names present in database: {matched_names}/{len(gold_rows)}",
        f"- Expected rows with a name duplicated in the database: {ambiguous_gold_rows}/{len(gold_rows)}",
        f"- Questions whose expected result is empty: {empty_n}/{len(questions)}", "",
        "**Interpretation:** Incorrect reference IDs constrain the achievable official score",
        "for ordinary queries returning true database IDs. Do not change IDs or gold labels",
        "and do not hard-code expected outputs into generated SQL.", "",
        "## Results", "",
        "| Framework | Official exact | Name-only | Name nonempty | Name empty | Balanced name-only |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for m in metrics:
        lines.append(f"| {m['framework']} | {m['official_accuracy']:.2%} | "
                     f"{m['name_accuracy']:.2%} | {m['name_nonempty_accuracy']:.2%} | "
                     f"{m['name_empty_accuracy']:.2%} | {m['name_balanced_accuracy']:.2%} |")
    lines.extend(["", "![Metric comparison](accuracy_comparison.png)", "",
                  "## Paired statistical significance", "",
                  "The same questions are used for all three frameworks. Cochran's Q is",
                  "the omnibus paired test; exact two-sided McNemar tests compare pairs,",
                  "with Holm adjustment within each family of three pairwise comparisons.", ""])
    for s in stats:
        lines.append(f"- {s['metric']}: Cochran Q={s['cochrans_q']:.4f}, approximate p={s['p_approx']:.6g}")
    lines.extend(["", "| Metric | Comparison | Left-only | Right-only | Raw p | Holm p |",
                  "|---|---|---:|---:|---:|---:|"])
    for p in comparisons:
        lines.append(f"| {p['metric']} | {p['left']} vs {p['right']} | {p['left_only_correct']} | "
                     f"{p['right_only_correct']} | {p['p_raw']:.6g} | {p['p_holm']:.6g} |")
    lines.extend(["", "## Limitations", "",
                  "Name equality does not prove correct restaurant identity when names repeat.",
                  "The supplementary metric is therefore a diagnostic, not a replacement",
                  "for the official scorer. The ID-label mismatch should be reported to",
                  "the instructor. A single run per prompt does not establish stability",
                  "across sampling seeds. Execution is protected by a timeout and row cap",
                  "and may differ from the unrestricted official evaluator.", ""])
    (args.report_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    for m in metrics:
        print(f"{m['framework']}: official={m['official_accuracy']:.2%}; name-only={m['name_accuracy']:.2%}; balanced name-only={m['name_balanced_accuracy']:.2%}")
    print(f"Full tables and plots: {args.report_dir}")


if __name__ == "__main__":
    main()
