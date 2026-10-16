"""Offline unit/integration tests; run: python -m unittest -v test_solution.py."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analyze_results import cochrans_q, exact_mcnemar_p, holm_adjust
from run_experiments import build_prompt, load_schema, unwrap_sql

HERE = Path(__file__).resolve().parent


class SolutionTests(unittest.TestCase):
    def test_prompt_templates_use_shared_examples(self):
        config = json.loads((HERE / "prompts.json").read_text())
        self.assertEqual(3, len(config["frameworks"]))
        self.assertEqual(3, len(config["few_shot_examples"]))
        self.assertNotIn("roses", config["frameworks"])
        for name in config["frameworks"]:
            prompt = build_prompt(config, name, "RESTAURANT(ID, NAME)", "FIND_ONLY_THIS_CITY")
            self.assertIn("FIND_ONLY_THIS_CITY", prompt)
            self.assertIn("RESTAURANT(ID, NAME)", prompt)
            for example in config["few_shot_examples"]:
                self.assertIn(example["question"], prompt)
                self.assertIn(example["sql"], prompt)

    def test_sql_unwrap(self):
        self.assertEqual("SELECT 1;", unwrap_sql("```sql\nSELECT 1;\n```"))
        self.assertEqual("SELECT 1", unwrap_sql("  SELECT 1  "))

    def test_paired_tests(self):
        self.assertEqual(1, exact_mcnemar_p(0, 0))
        self.assertEqual(0.125, exact_mcnemar_p(4, 0))
        self.assertEqual([0.03, 0.04, 0.3], holm_adjust([0.01, 0.02, 0.3]))
        stat, p = cochrans_q({"a": [1, 1, 1, 1], "b": [0, 0, 0, 0],
                               "c": [0, 1, 0, 1]})
        self.assertGreater(stat, 0)
        self.assertLess(p, 0.05)

    def test_schema(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "schema.csv"
            path.write_text("Table Name, Field Name, Is Primary Key, Is Foreign Key, Type\n"
                            "RESTAURANT, ID, y, n, int(11)\n"
                            "RESTAURANT, NAME, n, n, varchar(255)\n"
                            "-, -, -, -, -\n")
            self.assertEqual("RESTAURANT(ID int(11), NAME varchar(255))", load_schema(path))

    def test_analyzer_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data, results, report = [root / n for n in ("data", "results", "report")]
            for path in (data, results, report):
                path.mkdir()
            # A synthetic database, not a copy of the assignment labels.
            (data / "evaluate_retrieval_predictions.py").write_text(
                "import sqlite3\n"
                "def load_database():\n"
                "    db = sqlite3.connect(':memory:')\n"
                "    db.execute('CREATE TABLE RESTAURANT (ID INT, NAME TEXT)')\n"
                "    db.executemany('INSERT INTO RESTAURANT VALUES (?,?)', "
                "[(1,'Alpha'),(2,'Beta')])\n"
                "    return db\n")
            labels = [("Q1", [[1, "Alpha"]]), ("Q2", []), ("Q3", [[2, "Beta"]])]
            with (data / "restaurants_dataset.csv").open("w", newline="") as f:
                w = csv.writer(f); w.writerow(["question", "result"])
                w.writerows((question, json.dumps(expected)) for question, expected in labels)
            good1 = "SELECT ID, NAME FROM RESTAURANT WHERE ID = 1"
            good2 = "SELECT ID, NAME FROM RESTAURANT WHERE ID = -999"
            good3 = "SELECT ID, NAME FROM RESTAURANT WHERE ID = 2"
            runs = {"co_star": [good1, good2, good3],
                    "rtf": [good1, good1, good1],
                    "icio": [good3, good2, good3]}
            for framework, sqls in runs.items():
                with (results / f"predictions_{framework}.csv").open("w", newline="") as f:
                    writer = csv.writer(f); writer.writerow(["question", "predicted_sql"])
                    writer.writerows((q, sql) for (q, _), sql in zip(labels, sqls))
                with (results / f"meta_{framework}.csv").open("w", newline="") as f:
                    writer = csv.writer(f); writer.writerow(["question", "latency_seconds", "status"])
                    writer.writerows((q, 0.5, "ok") for q, _ in labels)
            subprocess.run([sys.executable, str(HERE / "analyze_results.py"),
                            "--data-dir", str(data), "--results-dir", str(results),
                            "--report-dir", str(report)], check=True, capture_output=True)
            self.assertTrue((report / "report.md").exists())
            self.assertTrue((report / "paired_tests.csv").exists())
            self.assertTrue((report / "accuracy_comparison.png").exists())
            with (report / "metrics.csv").open(newline="") as f:
                summaries = {r["framework"]: r for r in csv.DictReader(f)}
            self.assertAlmostEqual(float(summaries["co_star"]["execution_accuracy"]), 1.0)
            self.assertAlmostEqual(float(summaries["rtf"]["execution_accuracy"]), 1/3)
            self.assertAlmostEqual(float(summaries["icio"]["execution_accuracy"]), 2/3)


if __name__ == "__main__":
    unittest.main()
