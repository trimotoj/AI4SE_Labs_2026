# Week 03 — final report package (updated after 465 successful calls)

This package contains four editable Markdown reports and three figures reflecting the **final** experiment output provided in the conversation. In particular, all framework API failures were resolved. It supersedes **`Week03_Final_Reports.zip`**, which contained older metrics and API failures.

**Important evidence limitation:** This package was built from console excerpts and previously reviewed smoke-test cases; the full per-question results, metadata and precise untruncated latency values are **on the experimenter's computer**, not included here. Do not treat the archive as the full submission.

## What to submit

Keep your existing repository files under `Week_03_Prompting/week03_starter/`:

- The *actual* `prompts.json`, final corrected `run_experiments.py`, `analyze_results.py`, `analyze_name_accuracy.py` and other source files.
- `results/predictions_co_star.csv`, `predictions_rtf.csv`, `predictions_icio.csv` (full 155 rows each) plus `results/meta_*.csv`.
- `analysis/` and `analysis_name/` including metrics, paired tests, question-level diagnostics and figures.
- `TASK1_REPORT.md` if already present, or replace/merge with this archive's `Task_1_Report.md`.

Copy the entire **`Week03_Final_Reports_UPDATED/`** folder into `Week_03_Prompting/` so its Markdown figure links work. The bundled `prompts_reference.json` is a *reference copy only* of the original design; **do not overwrite an intentionally different final prompt configuration**. The bundled `analyze_name_accuracy.py` can be copied to the existing `week03_starter/` if missing; do not replace newer working code without comparing versions.

## Final accuracy figures

| Framework | Official matches | Name-only matches | Gold-nonempty name matches | Mean recorded latency (approx.) |
|---|---:|---:|---:|---:|
| CO-STAR | 43/155 | 119/155 | 76/112 | ~5.06 s |
| RTF | 43/155 | 116/155 | 73/112 | ~2.09 s |
| ICIO | 43/155 | 114/155 | 71/112 | ~1.76 s |

Statistical results: exact Cochran Q `p = 1.0` (identical binary vectors, no discordance), name-only Cochran Q `p = 0.281769`; no Holm-adjusted pairwise McNemar p-value is below `0.05`. **No statistically significant accuracy difference established.**

## Final verification commands (PowerShell)

From `AI4SE_Labs_2026/Week_03_Prompting/week03_starter`:

```powershell
.\.venv\Scripts\python.exe analyze_results.py --results-dir results
.\.venv\Scripts\python.exe analyze_name_accuracy.py --results-dir results
```

Optional original validator check for *each* prompt configuration:

```powershell
foreach ($f in @('co_star','rtf','icio')) {
    Copy-Item ".\results\predictions_$f.csv" "..\Assignments\Task_2\data\restaurants_dataset_predictions.csv" -Force
    Write-Host "Official validator: $f"
    .\.venv\Scripts\python.exe ..\Assignments\Task_2\data\evaluate_retrieval_predictions.py
}
Remove-Item "..\Assignments\Task_2\data\restaurants_dataset_predictions.csv"
```

The exact accuracy figures in these reports were produced by the local analyzer with official-style multiset comparison, not yet independently verified using the unmodified original evaluator. The original validator may take time to rebuild its database per run. Record its scores without altering labels or manually editing SQL IDs to chase references. This temporary `restaurants_dataset_predictions.csv` is not needed in the committed repository because three model prediction CSVs are already preserved.

## Safe commit and push

Run `git status --short` and review changes before committing. Do **not** commit `.venv`, API keys, credentials or temporary backup directories. If the work is still unfinished, annotate the repository README per the assignment. Stage the appropriate Week 03 files, commit, and `git push origin main` before the submission deadline. The **commit timestamp** and a successfully pushed repository matter for grading.
