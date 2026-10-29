# Week 03 — Prompting techniques: Text-to-SQL

This directory contains the completed assignments and reproducible experiment comparing **CO-STAR, RTF and ICIO** prompting frameworks for restaurant-related SQL generation using Google Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`).

## Navigation

| Assignment | Report | Evidence / implementation |
|---|---|---|
| Task 1 — Prompt selection | [Task 1 report](Week03_Final_Reports_UPDATED/Task_1_Report.md) | [Exact prompt templates](week03_starter/prompts.json) |
| Task 2 — SQL predictions and measurements | [Task 2 report](Week03_Final_Reports_UPDATED/Task_2_Report.md) | [Results and metadata](week03_starter/results/), [runner](week03_starter/run_experiments.py) |
| Task 3 — Supplementary metric | [Task 3 report](Week03_Final_Reports_UPDATED/Task_3_Report.md) | [Implementation](week03_starter/analyze_name_accuracy.py), [metric outputs](week03_starter/analysis_name/) |
| Task 4 — Detailed statistical comparison | [Task 4 report](Week03_Final_Reports_UPDATED/Task_4_Report.md) | [Analysis outputs](week03_starter/analysis/), [visualizations](Week03_Final_Reports_UPDATED/figures/) |

Also see [experiment and reproduction instructions](week03_starter/README.md), [final report package overview](Week03_Final_Reports_UPDATED/README.md), and [recorded independent course-validator results](official_validation_results.md).

## Verified final outcome

| Framework | Predictions / successful API calls | Official validator | Supplementary name-only accuracy | Mean recorded API latency |
|---|---:|---:|---:|---:|
| CO-STAR | 155 / 155 | 43/155 (27.74%) | 76.77% | 5.055 s |
| RTF | 155 / 155 | 43/155 (27.74%) | 74.84% | 2.095 s |
| ICIO | 155 / 155 | 43/155 (27.74%) | 73.55% | 1.758 s |

**Interpretation:** The dataset's reference restaurant IDs disagree with the supplied database, limiting the usefulness of exact ID/name accuracy. The name-only metric complements, but does not replace, the official result comparison. On name-only matching, CO-STAR ranked first descriptively, without statistically significant improvement (Cochran's Q `p=0.281769`; Holm-adjusted McNemar `p>0.05`). All 465 final model calls succeeded; some metadata rows preserve a historical error from a previous retry. Read the reports for limitations.

Original university task descriptions and input datasets remain in [Assignments](Assignments/). Generated SQL outputs and reference labels were not altered to inflate accuracy.
