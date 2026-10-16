# Task 2 — Comparing prompt frameworks for Text-to-SQL

## Goal and setup

We compared three structured prompting frameworks (**CO-STAR**, **RTF**, and **ICIO**) for translating natural-language restaurant requests into SQLite queries. The 155 questions came from the supplied `restaurants_dataset.csv`. Each framework received the same database schema, common SQL rules, three synthetic few-shot demonstrations, and the same question set. The gold `result` field was **not** included in requests. Each question was sent as an independent single-turn call, with no conversational history. ROSES and pure zero-shot prompting were not used.

The model was **Google Gemini 3.1 Flash-Lite** (`gemini-3.1-flash-lite`) through the OpenAI-compatible Gemini endpoint. The model identifier, prompt version, time and request status were logged for each record; SQL predictions were preserved per framework. The three frameworks were run in sequential blocks rather than randomized/interleaved order. No explicit sampling temperature was provided. The experiment was resumed after temporary HTTP 429/503 and connection reset errors, using retries. In the **final saved dataset all 465 calls have status `ok`** (155 per framework).

## Final results

| Metric | CO-STAR | RTF | ICIO |
|---|---:|---:|---:|
| Questions | 155 | 155 | 155 |
| Final successful API calls | **155/155** | **155/155** | **155/155** |
| Executable SQL | **155/155** | **155/155** | **155/155** |
| Official exact result matches | **43/155** | **43/155** | **43/155** |
| Official exact execution accuracy | **27.74%** | **27.74%** | **27.74%** |
| Official balanced execution accuracy | **50.00%** | **50.00%** | **50.00%** |
| Supplementary name-only matches | **119/155** | 116/155 | 114/155 |
| Supplementary name-only accuracy | **76.77%** | 74.84% | 73.55% |
| Balanced name-only accuracy | **83.93%** | 82.59% | 81.70% |
| Recorded mean latency, approx. | ~5.06 s | ~2.09 s | **~1.76 s** |

![Final accuracy](figures/accuracy_comparison.png)

![Recorded mean latency](figures/mean_latency.png)

These official-metric-equivalent figures were calculated by `analyze_results.py` using the original evaluator’s multiset comparison; running the unmodified official validation script against all three final prediction files remains a recommended independent check. The official metric cannot distinguish these frameworks: every framework matches the 43 questions with empty gold results, and none matches the 112 nonempty gold results as complete `(ID, NAME)` multisets. The separate name-only metric is therefore essential for interpreting this dataset, **but is not a substitute for the official score**. By this measure, CO-STAR is descriptively ahead of RTF by **1.94 percentage points** and ICIO by **3.23 percentage points**. This does not establish a statistically significant advantage (Task 4).

The recorded mean latency is **about 5.06 seconds for CO-STAR**, **2.09 seconds for RTF** and **1.76 seconds for ICIO**. These numbers are read from the user's truncated console display and are intentionally shown as approximations. `run_experiments.py` measures the final attempt with `time.perf_counter()`; it does **not** include waiting between requests or earlier failed attempts in the same request's recorded latency. The resumed requests, different execution times and network conditions limit causal interpretation. This is client-observed request latency, not isolated on-device inference time.

## Examples of qualitative SQL review

Early manual inspection showed that the model separated the restaurant query from distracting text (e.g. irrelevant mentions of soup, pie, or a picnic), and used `JOIN LOCATION ON RESTAURANT.ID = LOCATION.RESTAURANT_ID` for address conditions. The following exact comparisons illustrate the reference-ID problem:

| Question type | Reference result | Database result of generated SQL |
|---|---|---|
| Best Californian, Portola Valley | `(3, 'portola park')` | `(2633, 'portola park')` |
| Best eclectic, Calistoga | `(1457, 'catahoula restaurant and saloon')` | `(4808, 'catahoula restaurant and saloon')` |
| Timber Creek Dr, San Jose, rating > 1.7 | `(1503, 'lee & ginas cafe')` | `(2157, 'lee & ginas cafe')` |

The model output uses actual IDs from the provided SQLite database, whereas labels refer to different IDs. It would be inappropriate to hard-code label IDs into the SQL to obtain apparent success.

## Assessment and methodological limitations

An integrity audit found that **only 3 of 13,235** gold `(ID, NAME)` rows exist as exact ID/name pairs in the SQLite restaurant table, even though **all 13,235 gold names** appear. The current official evaluator compares complete rows and therefore severely penalizes otherwise correct queries for nonempty results. We preserve that metric without modifying data or evaluator. Name-only accuracy reports the multiset of returned names; it is vulnerable to restaurants with duplicate names and cannot prove identity.

All generated SQL statements were executable, but executability alone does not imply semantic correctness. The full experiment covers one dataset, one model and one combined run. Sequential requests, sampling defaults, API/network variability and differences in prompt length can influence performance. We did not measure a distinct coding-agent effect: ChatGPT assisted in preparing/reviewing the Python workflow, while the same local runner handled all three prompts.

## Reproduction and artifacts

- `week03_starter/prompts.json`: framework templates, fixed shared instructions and examples.
- `week03_starter/run_experiments.py`: production runner with safe checkpoint/resume and retry handling.
- `week03_starter/results/predictions_*.csv`: all 155 raw question/SQL pairs per framework.
- `week03_starter/results/meta_*.csv`: prompt/model metadata and request timing per question.
- `week03_starter/analyze_results.py`: exact multiset metric, validity and timing summaries.
- `week03_starter/analyze_name_accuracy.py`: supplementary name-only evaluation.
- `week03_starter/analysis/`, `week03_starter/analysis_name/`: detailed question-level data and figures.

**Evidence note:** Summary figures were built from the final console output supplied by the experimenter. The complete per-question CSV files and exact high-precision latency means were not available for independent re-analysis during report authoring. Those local outputs must be kept and inspected before submission.
