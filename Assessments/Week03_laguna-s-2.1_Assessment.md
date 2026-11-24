# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: The submission is exceptionally thorough and complete across all four tasks. The student selected three genuine structured prompting frameworks (CO-STAR, RTF, ICIO) from frompting.com, ran 465 stateless API calls (155 questions × 3 frameworks) with full metadata and retry-safe checkpointing, implemented and calculated a new name-only execution accuracy metric, and performed paired statistical analysis (Cochran's Q, exact McNemar with Holm correction). All artifacts — prediction CSVs, metadata, analysis scripts, generated figures, and reproducible test suite — are consistent and cross-validated against the unmodified course evaluator. The student correctly diagnosed a reference-ID integrity issue in the dataset (3/13,235 gold ID/name pairs exist) and reported the supplementary metric as a diagnostic rather than a replacement.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Three structured prompting frameworks were chosen from https://frompting.com/frameworks: CO-STAR, RTF, and ICIO. ROSES and zero-shot prompting are explicitly excluded. Each framework's source URL, rationale, and expected trade-offs are documented, and the actual prompt templates (with shared schema, shared rules, and three synthetic few-shot examples) are stored in `prompts.json`. The gold `result` column is deliberately never sent to the model. All three prompts receive identical inputs (schema, rules, examples, question) for a fair comparison. Fully satisfies the Task 1 deliverables.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: The Text-to-SQL problem was solved using all three Task 1 prompts across 155 questions each (465 total calls). All outputs are stored as `predictions_*.csv` files with model/framework/prompt-version/timestamp/status/latency metadata in `meta_*.csv`. All 465 final calls succeeded with executable SQL. Results are compared across frameworks with visualizations (`accuracy_comparison.png`, `mean_latency.png`). Inference times are measured via `time.perf_counter()` and summarized per framework (5.055s / 2.095s / 1.758s). The unmodified course evaluator was independently re-run and confirmed 43/155 (27.74%) for each framework. The report includes qualitative SQL review and a data-integrity audit. Fully satisfies the Task 2 deliverables.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: A new metric — Name-only Execution Accuracy (NEA) — was proposed, formally defined, and implemented in `analyze_name_accuracy.py` using `collections.Counter` on the NAME column. The metric is well-justified: a reference-ID integrity audit found only 3/13,235 gold `(ID, NAME)` pairs exist in the database, making full-row accuracy unreliable on nonempty cases. The report explicitly discusses NEA as complementing (not replacing) the official exact-execution metric, includes a class-balanced variant (BNEA = 0.5·(NEA_empty + NEA_nonempty)), and provides a comparison table for all three frameworks. Results are verified against committed `metrics.csv` and `question_level.csv`. Fully satisfies the Task 3 deliverables.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: A detailed reiteration and analysis of Tasks 2–3 with tables and graphs (`accuracy_comparison.png`, `name_accuracy_by_class.png`, `mean_latency.png`). Statistical significance was assessed with Cochran's Q (official: Q=0, p=1.0; name-only: Q=2.53, p=0.2818) and pairwise exact two-sided McNemar tests with Holm correction (all adjusted p > 0.05) — no difference is statistically significant. The report explains the factors shaping results: prompt framework structure/length (CO-STAR vs RTF vs ICIO as confounded subcomponents), the single model used (`gemini-3.1-flash-lite`) with no explicit temperature, AI-coding-agent involvement (ChatGPT for workflow, shared local runner), and request-scheduling/latency caveats. Validity threats (construct, internal, statistical power, external, reproducibility) are enumerated, and manually inspected SQL cases illustrate the ID-mismatch pattern. Fully satisfies the Task 4 deliverables.
