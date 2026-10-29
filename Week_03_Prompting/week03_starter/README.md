# Week 03 — Text-to-SQL prompting experiments

This is the **completed Week 03 experiment**, not an unfinished starter. It compares CO-STAR, RTF and ICIO on 155 restaurant Text-to-SQL questions each (465 successful API responses) using Google Gemini `gemini-3.1-flash-lite`.

The final reports and interpretation are in [../Week03_Final_Reports_UPDATED/](../Week03_Final_Reports_UPDATED/README.md). See [../README.md](../README.md) for a short submission overview.

## Files

- `prompts.json` — three structured prompting templates, common SQL instructions, schema, and three synthetic few-shot demonstrations.
- `run_experiments.py` — stateless request runner with checkpoint/resume and API retries.
- `results/predictions_{co_star,rtf,icio}.csv` — 155 question/SQL pairs per framework in the official evaluator's format.
- `results/meta_{co_star,rtf,icio}.csv` — model, framework, prompt version, timestamp, request status, and measured latency per question.
- `analyze_results.py` and `analysis/` — executable-SQL checks, official-style exact result comparison, timings, paired tests and plots.
- `analyze_name_accuracy.py` and `analysis_name/` — supplementary name-only and balanced name-only metrics, integrity audit, paired tests and plots.
- `test_solution.py` — offline tests.
- `../official_validation_results.md` — recorded output of the **unmodified course evaluator** for all three frameworks.

## Final results

| Framework | Official exact accuracy | Name-only accuracy | Mean client-observed API latency |
|---|---:|---:|---:|
| CO-STAR | 43/155 (27.74%) | 119/155 (76.77%) | 5.055 s |
| RTF | 43/155 (27.74%) | 116/155 (74.84%) | 2.095 s |
| ICIO | 43/155 (27.74%) | 114/155 (73.55%) | 1.758 s |

The original course evaluator was run independently for each framework's saved prediction CSV; it returned **43/155 (27.74%) for all three**. The low official score is substantially affected by mismatched restaurant IDs in the provided reference data. The supplementary name-only metric is diagnostic, not a replacement for official evaluation; see the Task 3–4 reports.

## Reproduce the analysis (no API key required)

From this directory, with Python 3.10+ and `matplotlib` installed:

```powershell
python -m pip install matplotlib
python analyze_results.py --results-dir results
python analyze_name_accuracy.py --results-dir results
python -m unittest -v test_solution.py
```

For the original evaluator, the input must be named `restaurants_dataset_predictions.csv` under `../Assignments/Task_2/data/`. See [../official_validation_results.md](../official_validation_results.md) for the exact recorded results. Preserve any existing file of that name before temporarily copying a framework's prediction CSV.

## Reproduce model generation (optional; incurs API usage)

Set `LLM_API_KEY` privately in the terminal, then run:

```powershell
python run_experiments.py --model gemini-3.1-flash-lite --base-url https://generativelanguage.googleapis.com/v1beta/openai --out-dir new_results --retries 8 --delay 5 --timeout 120
```

Do not commit the API key or virtual environment. Running a new generation may produce different SQL or latency values. Use `--resume` only when continuing a compatible run with the same model.

### Request metadata interpretation

All 465 final metadata rows have `status=ok`. **32 of those rows retain a nonempty `error` field** from an earlier failed attempt (e.g. HTTP 429/503) that succeeded on retry; in the submitted runner, a later successful attempt does not clear that historical error string. The `status` reflects the final outcome, while `latency_seconds` measures only the final attempt and does not include previous failed-attempt durations or retry backoff. These records are preserved as measured, not rewritten to hide transient failures.

This directory also includes automatically generated `analysis/report.md` containing generic interpretation prompts. The full interpretation and coding-agent discussion are in `../Week03_Final_Reports_UPDATED/Task_4_Report.md`.
