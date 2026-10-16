# Task 1 — Selection and design of prompting frameworks

## Goal and experimental controls

The goal is to convert free-form restaurant search questions into executable SQLite queries. Three structured prompting frameworks are compared: **CO-STAR**, **RTF**, and **ICIO**. Neither ROSES nor zero-shot prompting is used.

Every prompt receives the **same database schema**, **the same three synthetic few-shot question/SQL examples**, **the same set of shared SQL restrictions**, and **the same question**. The examples use fictional city names and were written without consulting the dataset's gold answers. For the comparison, use one fixed model and consistent generation settings. Each question is submitted as a fresh stateless request with no chat history.

The exact source of each framework and its prompt template are recorded in `prompts.json` (version 1.0).

## 1. CO-STAR (Context, Objective, Style, Tone, Audience, Response)

Source: https://frompting.com/frameworks/co-star

CO-STAR separates background information, the conversion objective, stylistic constraints, the technical tone, the downstream consumer, and the required response format. It is chosen as the most **explicit, richly structured** variant. The intended benefit is to reduce formatting drift and make the parser's expectations clear. A possible downside is that Style/Tone/Audience add tokens that may not improve SQL reasoning; that trade-off is worth measuring.

**Expectation:** consistent SQL-only answers; potentially more overhead and latency than the compact framework.

## 2. RTF (Role, Task, Format)

Source: https://frompting.com/frameworks/rtf

RTF emphasizes role, the task itself, and a precisely defined output format. It was selected as a **short, practical baseline** that still uses a genuine structured framework and few-shot examples, rather than prohibited zero-shot prompting. It is well-suited to outputs that are consumed by an automated SQL evaluator.

**Expectation:** fewer output-format violations and lower prompt overhead, but potentially less robustness to ambiguous questions.

## 3. ICIO (Instruction, Context, Input, Output)

Source: https://frompting.com/frameworks/icio

ICIO separates task instructions from database context, user-supplied question text, and machine-readable output. It was chosen because question text sometimes contains **unrelated asides and other distracting phrases**. A delimited input block makes it more explicit that this content is data to translate, not a new instruction for the system.

**Expectation:** potentially more robust behavior on distractor-containing inputs and reliable single-statement outputs.

## Design choices and limitations

- All three use the same three synthetic few-shot examples, so this is not a zero-shot experiment.
- All three specify `SELECT` output with exactly two columns: restaurant ID and name, matching the label row shape.
- The source dataset's `result` values are **not sent** to the model, to prevent answer leakage.
- Prompt text has been fixed in advance of final evaluation to reduce overfitting on the 155 public questions.
- The framework comparison is not fully causal: templates differ in ordering, length, emphasis, and delimiters. Randomness, model behavior, sampling configuration and any coding agent must be documented.
- Framework selection and expected outcomes are hypotheses. They are not measured findings until Task 2 is executed.
