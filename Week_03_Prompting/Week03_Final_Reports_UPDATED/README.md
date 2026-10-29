# Week 03 — Final reports

This folder contains the **completed** reports and charts for the university Week 03 Text-to-SQL prompting assignment. All four tasks are documented, and the underlying predictions, scripts and detailed analyses are committed in the sibling `../week03_starter/` directory. This is not a standalone source-data archive.

## Reports

- [Task 1 — Prompt selection](Task_1_Report.md): CO-STAR, RTF and ICIO; sources, full prompt design and expected trade-offs.
- [Task 2 — Text-to-SQL comparison](Task_2_Report.md): 155 questions per framework, saved model outputs, executable SQL, accuracy, latency and examples.
- [Task 3 — New metric](Task_3_Report.md): name-only execution accuracy (NEA), balanced NEA, implementation and limitations.
- [Task 4 — Statistical comparison](Task_4_Report.md): paired significance tests, figures, model/prompt/coding-agent factors and validity threats.

The `figures/` directory contains the report charts. `final_summary.csv` contains rounded summary results; **the exact numerical means** are in `../week03_starter/analysis/metrics.csv`. `prompts_reference.json` is a reference copy of the actual `../week03_starter/prompts.json`.

## Final verified results

| Framework | Successful calls | Official exact result matches | Name-only result matches | Mean API latency |
|---|---:|---:|---:|---:|
| CO-STAR | 155/155 | 43/155 (27.74%) | 119/155 (76.77%) | 5.055 s |
| RTF | 155/155 | 43/155 (27.74%) | 116/155 (74.84%) | 2.095 s |
| ICIO | 155/155 | 43/155 (27.74%) | 114/155 (73.55%) | 1.758 s |

The unmodified assignment evaluator **was run on all three final prediction files** and reported `Accuracy: 0.2774 (27.74%)`, `Correct: 43/155` for each. See [official validation transcript](../official_validation_results.md). Both local analyzers' metrics and raw CSV files are preserved alongside the report package.

The benchmark's reference IDs are inconsistent with the supplied SQLite database (just 3 of 13,235 gold ID/name pairs exist verbatim), so all three frameworks correctly match 43 empty gold results but none of the nonempty full ID/name result sets. Name-only matching adds a useful, weaker measure. Cochran's Q gives name-only `p = 0.281769`; no Holm-adjusted pairwise McNemar test shows a significant difference at 0.05.

## Reproducibility and caveats

From `../week03_starter/`, with Python 3.10+ and `matplotlib`:

```powershell
python analyze_results.py --results-dir results
python analyze_name_accuracy.py --results-dir results
```

All 465 final `meta_*.csv` rows are marked `ok`. Some successful rows contain the error message from a **prior failed retry attempt** (32 records total); the final status is successful, and the saved latency is the duration of the last successful request rather than total wall-clock retry time. No API credentials are committed.

Full sources and assignment instructions: [Week 03 overview](../README.md).
