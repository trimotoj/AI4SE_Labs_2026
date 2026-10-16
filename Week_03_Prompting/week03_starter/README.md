# Week 03 — Text-to-SQL experiment starter

This is a reproducible **starter implementation**, not a completed experiment. It does not include generated predictions or measured model scores: those require real API calls. It does not copy the labels into model prompts or hard-code solutions.

## Place the files

Copy this entire `week03_starter` folder into your fork as:

```text
AI4SE_Labs_2026/
└── Week_03_Prompting/
    ├── Assignments/
    │   ├── Task_1/Task_1.md
    │   ├── Task_2/data/
    │   │   ├── restaurants_dataset.csv
    │   │   ├── restaurants-schema.csv
    │   │   ├── restaurants-db.txt
    │   │   └── evaluate_retrieval_predictions.py
    │   └── ...
    └── week03_starter/
        ├── prompts.json
        ├── TASK1_REPORT.md
        ├── run_experiments.py
        ├── analyze_results.py
        └── README.md
```

Requires Python 3.10+ and `matplotlib` for figures. The generation script uses only Python's standard library and an **OpenAI-compatible chat-completions HTTP endpoint** (not necessarily OpenAI's models). This is distinct from ChatGPT's UI subscription. Choose an endpoint/model you can access. Never commit an API key.

```bash
python -m pip install matplotlib
```

## Generate predictions (Task 2)

Example for an OpenAI-compatible API endpoint:

```bash
export LLM_API_KEY='YOUR_API_KEY'        # PowerShell: $env:LLM_API_KEY='YOUR_API_KEY'
cd Week_03_Prompting/week03_starter
python run_experiments.py --model YOUR_MODEL_ID --base-url https://api.example.com/v1 --temperature 0
```

Use `--temperature 0` **only if the model supports that option**; otherwise omit it. For local Ollama with a compatible endpoint, try `--base-url http://localhost:11434/v1 --model MODEL_NAME` (assuming the model is available there).

First verify basic connectivity and output shape with a smoke test:

```bash
python run_experiments.py --model YOUR_MODEL_ID --base-url https://api.example.com/v1 --limit 3 --out-dir smoke_test
```

Do not use the smoke-test output for your final evaluation. For the complete run, choose a fresh output directory or `--resume` to continue an interrupted run. Each framework is called separately; each question uses an independent message. The output includes model name, framework ID, version of the prompt, UTC timestamp and latency.

Files:
- `results/predictions_co_star.csv`, `predictions_rtf.csv`, `predictions_icio.csv` — **exact** `question,predicted_sql` CSV format for the original validator.
- `results/meta_co_star.csv` etc. — prompt/model identifiers, inference time, request status and error details.

On failures, the script records a blank prediction and an error. It deliberately does **not** insert an always-empty SQL query as a fake success. Correct API/model failures before the final official evaluation.

## Verify against the official evaluator

Only after generating all 155 queries for a framework:

```bash
# Run this from Week_03_Prompting/week03_starter
cp results/predictions_co_star.csv ../Assignments/Task_2/data/restaurants_dataset_predictions.csv
python ../Assignments/Task_2/data/evaluate_retrieval_predictions.py
```

Repeat for `rtf` and `icio`. On Windows PowerShell, use `Copy-Item` instead of `cp` if preferred. The official script will stop at the first invalid SQL query, so inspect/resolve errors if needed; do not alter questions or copy `result` labels into predictions. Do not accidentally commit the temporary `restaurants_dataset_predictions.csv` in multiple versions.

## Additional metrics, figures and statistical tests (Tasks 3–4)

```bash
python analyze_results.py
```

The analyzer **uses the original repository's database loader**, executes each query against an in-memory SQLite database, protects the connection from writes, and compares rows as multisets like the official script. Invalid SQL is counted incorrect rather than aborting the whole analysis. A 3-second per-query timeout and 100,000-row cap protect against unexpectedly expensive queries; document any differences if these constraints affect an official result.

It creates:
- `analysis/metrics.csv`
- `analysis/question_level_analysis.csv` (for reviewing failures)
- `analysis/paired_tests.csv`
- `analysis/accuracy_comparison.png`, `analysis/latency_boxplot.png`
- `analysis/report.md` (generated results plus prompts for your manual interpretation)

The additional metric is **balanced execution accuracy**: the mean of execution accuracy on gold-empty and gold-nonempty questions. It complements ordinary execution accuracy by giving equal weight to both classes. Across 155 labels, 43 are empty and 112 nonempty (verified on the repository at preparation time).

Task 4 uses **Cochran's Q test** for 3 correlated accuracy vectors and paired **exact McNemar tests with Holm multiple-testing correction**. This is more appropriate than comparing independent proportions, because each prompt answers the same questions. Interpret statistical significance cautiously: one run/model does not establish generality across models/seeds.

Complete the `analysis/report.md` discussion with manually inspected failure examples, trade-offs, exact API model/version, generation parameters, coding agent used, and reasons why the prompts might differ. Do not claim a statistically significant difference unless the calculated test supports it.

## Fairness and anti-leakage safeguards

1. Keep the 3 few-shot demonstrations identical across frameworks. None may include actual label results.
2. Never pass the `result` column from `restaurants_dataset.csv` into generation prompts.
3. Avoid hand-editing individual SQL outputs to force matches; change the **general prompt or implementation** and rerun the complete experiment instead.
4. Save all predictions, prompts, model IDs and metadata, including failed cases, and describe any manual steps.
5. If prompts are tuned using a development subset, reserve a separate untouched evaluation subset for unbiased comparison; the official provided benchmark can still be reported separately.
