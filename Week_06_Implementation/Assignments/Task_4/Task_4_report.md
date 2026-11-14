# Task 4: Semantic retrieval

## Strategy

`rag/retrieve.py` accepts a programming task, embeds it with the same `text-embedding-3-small` model used for Task 3, and compares the query vector with all 138 stored chunk vectors. The query representation identifies the repository, labels the input as a programming task, and states the intent to find relevant source code and tests. This resembles the metadata-enriched indexing representation without inventing file or symbol metadata that the query does not contain.

The implementation joins `embeddings.json` to `chunks.json` through stable chunk IDs. Results contain similarity score, ID, file, symbol, source/test category, line range, and the original source code. It validates complete one-to-one ID coverage, the configured model, finite numeric vectors, consistent dimensions, and non-zero norms before retrieval.

## Similarity and ranking

Cosine similarity measures vector direction rather than magnitude and is the standard simple baseline for semantic embeddings. For this small index, a direct pure-Python scan is readable and fast enough, with no NumPy or vector-database dependency. Results are sorted by descending similarity; equal scores are resolved by ascending stable chunk ID, making ranking deterministic.

The top result count is configurable with `--top-n`/`-n` and defaults to 5. Baseline retrieval searches both production and test chunks without weighting. Tests can be useful because they describe behavior and edge cases, but their greater count (89 tests versus 49 source chunks) may crowd out implementation chunks. The optional `--category source` or `--category test` filter preserves both use cases without changing baseline similarity or adding reranking.

## Verification

Eleven offline unit tests pass. They cover known cosine values, zero/non-finite/non-numeric vectors, dimension mismatch, deterministic ties, correct top-n ordering and counts, category filtering, metadata/source output, query construction, mocked query embeddings, stable-ID matching, duplicate and unknown IDs, and loading the real stores. The real index loads all 138 unique vectors with dimension 1,536 and complete source-chunk coverage.

No `OPENAI_API_KEY` was available in the execution environment, so the representative tasks in `Assignments/missing_code.json` were not sent to the API and no live top-five results are claimed. The missing-key CLI path was verified to exit with a clear message before making a request.

Run the tests and retrieval from the repository root:

```text
python Week_06_Implementation/rag/test_retrieve.py
python Week_06_Implementation/rag/retrieve.py -n 5 "Implement Money.__bool__ so zero is false"
```

Live queries require `OPENAI_API_KEY` in the process environment and the dependencies in `rag/requirements.txt`. Task 5 can pass the returned source snippets to a generation model, but should manage prompt size, preserve result provenance, and consider whether production-only retrieval or lightweight source preference improves results for a particular task.
