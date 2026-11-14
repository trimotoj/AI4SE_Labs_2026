# Task 5: RAG-based source code generation

## Architecture

The completed pipeline is implemented in `rag/generate_code.py` and reuses the chunking, embedding, and retrieval components from Tasks 2–4. It processes the entries in `Assignments/missing_code.json` as follows:

1. Validate that the requested file, class, and method can be located with Python's AST.
2. Embed the textual programming task with `text-embedding-3-small`.
3. Retrieve exactly five chunks from the fixed 138-vector store using cosine similarity. Production and test chunks participate without weighting.
4. Independently extract the target method signature and surrounding class source with the AST.
5. Send the task, five retrieved chunks, and target context to `gpt-5-mini` through the OpenAI Responses API.
6. Require strict JSON containing only a replacement method body.
7. Validate the body and complete candidate file with the AST before writing or executing it.
8. Replace only the existing method-body line span, preserving decorators, signatures, imports, formatting, and unrelated code.
9. Run the complete Playground test suite and store provenance and test results in JSON.

The embedding store remains a fixed snapshot of the original incomplete repository throughout generation and repair. This avoids mixing original and generated source in the index and makes retrieval reproducible. The scripts verify the embedding hash and use atomic writes. Invalid output, unexpected source changes, incomplete API responses, and failed repair verification trigger rollback.

## Prompt and model decisions

`gpt-5-mini` was selected from the models permitted by the assignment. Generation requests use low reasoning effort and a 4,096-token output limit. The larger limit replaced an initial 1,200-token limit after an incomplete response; diagnostics now include response status, incomplete reason, input tokens, output tokens, reasoning tokens, and the configured limit.

Each normal generation prompt contains:

- the original task specification;
- the unchanged method signature and decorators;
- surrounding class context;
- five retrieved chunks with IDs, similarity scores, paths, symbols, categories, line ranges, and source;
- a strict body-only JSON output contract.

There is no unrestricted whole-file rewrite and no `ast.unparse`. The validator rejects malformed JSON, syntax errors, remaining `pass` stubs, imports, nested definitions, and scope declarations. The artifact records model response IDs, token usage, prompt hashes, retrieved chunks, generated bodies, file hashes, and test summaries.

## Initial generation run

Before generation, the complete suite ran **481 tests with 35 failures and 17 errors**. All ten missing methods were confirmed to be `pass` stubs.

The completed run generated all ten method bodies with `gpt-5-mini`. Its provenance is stored in `rag/generation_results.json`. After generation, the suite ran **481 tests with 0 failures and 7 errors**.

All seven errors originated from `BulkDiscountPricing.price`. The generated body used `base.amount`, but the repository's `Money` class exposes `cents`. The original top-five retrieval for this task consisted entirely of test chunks. Although those tests described the expected arithmetic, neither the retrieved context nor the target-class context showed the `Money` API. This allowed the model to invent a plausible but nonexistent attribute.

This result demonstrates an important limitation of similarity-only retrieval: relevant behavioral tests can rank highly while a required implementation dependency is absent.

## Targeted RAG repair

The pipeline was extended with a targeted `--repair CLASS.METHOD` mode. It repairs one method recorded in a completed artifact without restoring or regenerating the other methods. Before making an API call, it verifies:

- the original artifact has completed status;
- all generated files still match the hashes in that artifact;
- the current target body matches the previously generated body;
- the embedding snapshot is unchanged;
- the repair uses a separate artifact.

The repair of `BulkDiscountPricing.price` still performed the required five-chunk RAG retrieval. The five results again consisted entirely of tests:

| Rank | Chunk ID | Symbol | Category |
|---:|---|---|---|
| 1 | `f9e96edcd646fce1` | `BulkDiscountPriceTests` | test |
| 2 | `997b1266673c1d4b` | `_FlatPricing` | test |
| 3 | `73b5aba1bed10f69` | `BulkDiscountConstructionTests` | test |
| 4 | `8299f60bacc4da5c` | module context from `test_pricing.py` | test |
| 5 | `aa130e8c651ab468` | `FlatPricingPriceTests` | test |

To address the diagnosed context gap without replacing RAG, the repair prompt independently added AST-verified source for the complete `Money` class and `FlatPricing.price`. It also included the previous implementation, the original task, the observed `AttributeError`, and an explicit instruction not to invent APIs.

The repaired body retained the original control flow but changed the invalid accesses from `base.amount` to `base.cents`:

```python
total = sum(getattr(item, "quantity") for item in items)
base = self._base.price(items)
if total < self._threshold or self._percent_off == 0:
    return base
discount = (base.cents * self._percent_off) // 100
return Money(base.cents - discount)
```

The repair used `gpt-5-mini-2025-08-07`, with 3,363 input tokens and 219 output tokens, including 128 reasoning tokens. Its independent provenance is stored in `rag/repair_results.json`. The artifact contains the previous and new implementations, retrieval scores, dependency context, response metadata, original source, hashes, and focused/full test results. Because it snapshots only `pricing.py`, the repair is independently reversible without restoring the other nine generated methods.

## Final verification

The test progression was:

| Stage | Tests | Failures | Errors |
|---|---:|---:|---:|
| Original repository | 481 | 35 | 17 |
| Ten generated methods | 481 | 0 | 7 |
| Before targeted repair, pricing module | 34 | 0 | 6 |
| After targeted repair, pricing module | 34 | 0 | 0 |
| Final complete suite | 481 | 0 | 0 |

The completed generation and repair artifacts, fixed embedding snapshot, strict AST validation, and file hashes provide an auditable link from each task and retrieval result to the generated source and test outcome.

## Test success versus specification compliance

Passing all 481 tests does not prove that every implementation matches the written specification. `InventoryLedger.__contains__` is the known counterexample.

`missing_code.json` states that membership should indicate a SKU with **positive on-hand stock**. The generated implementation instead ends with dictionary-key membership:

```python
return sku in self._on_hand
```

A committed SKU can remain in `_on_hand` with a value of zero, so this behavior conflicts with the written requirement. However, the existing test `test_contains_present_even_if_zero_on_hand_after_commit` explicitly expects membership to remain true in that state. The test and specification therefore contradict each other. This conflict was not hidden or resolved by modifying tests, and `InventoryLedger.__contains__` was deliberately excluded from the pricing repair.

The final submission is test-clean, but this specification inconsistency remains an explicit limitation requiring a decision from the assignment owner.
