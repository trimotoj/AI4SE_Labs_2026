# Task 3: Embedding generation

## Model and representation

The implementation uses OpenAI's `text-embedding-3-small` model through the official Python SDK. It provides a practical cost/quality balance for semantic code retrieval and produces 1,536-dimensional vectors by default. Task 4 queries must use this same model and the same metadata-aware representation convention.

Each embedding input contains the repository name, file path, source/test category, semantic kind, symbol, source line range, optional class/member names, and source code. Including these labels helps queries match concepts such as a file, class, test, or symbol rather than relying only on code tokens.

## Tokens, batching, and oversized input

The script uses `tiktoken` with `cl100k_base`, the tokenizer documented for third-generation embedding models. It measures the final representation rather than source code alone. Inputs are limited to 8,192 tokens. An over-limit input is truncated at a token boundary and marked with original and embedded token counts; Task 2's 120-line chunks should normally remain far below this fallback limit.

Requests are grouped into batches of at most 64 inputs and at most 250,000 tokens, below the API-wide 300,000-token batch limit. Failed requests use bounded exponential backoff for four attempts. The API key is read only from `OPENAI_API_KEY` by the SDK and is never stored or displayed.

## Storage and incremental cache

Vectors are stored in `rag/embeddings.json`, separate from the unchanged Task 2 `chunks.json`. Each record contains the stable chunk ID, retrieval metadata, token counts, representation hash, and vector. Source text remains retrievable by joining the stable ID back to `chunks.json`, avoiding a second large source copy.

The representation hash includes the model and format version. On rerun, an entry is reused only when its ID, hash, model, format, dimension, and finite numeric vector are valid. Changed or missing entries are regenerated, stale entries are omitted, and duplicates are rejected. Output is written atomically after every successful batch so interrupted runs retain completed work safely.

## Validation and trade-offs

`--dry-run` validates the chunk schema and reports exact token statistics without credentials or API calls. After generation, validation requires exactly one unique, finite, numeric, consistently sized embedding for every nonempty chunk. JSON is transparent and convenient for this educational repository, although a binary NumPy matrix or vector database would be smaller and faster at larger scale.

The credential-free dry run processed all **138 nonempty chunks**. Their metadata-enriched representations contain **42,953 tokens** in total: minimum 51, maximum 1,477, and mean 311.25 tokens. No chunk requires truncation. Local checks also covered syntax, stable-ID uniqueness, metadata inclusion, batching, cache reuse, source coverage, vector validation, and the missing-key failure path.

The subsequent authenticated generation run created `rag/embeddings.json` with **138 embeddings**, one for every chunk. All vectors use `text-embedding-3-small`, contain **1,536 finite numeric dimensions**, and retain complete stable-ID coverage without duplicates. The completed store passed the script's validation and became the fixed embedding snapshot used by Tasks 4 and 5. No API key or credential is stored in the artifact.

Install dependencies and run from the repository root:

```text
python -m pip install -r Week_06_Implementation/rag/requirements.txt
python Week_06_Implementation/rag/create_embeddings.py --dry-run
python Week_06_Implementation/rag/create_embeddings.py
python Week_06_Implementation/rag/create_embeddings.py --validate-only
```

The actual generation command requires `OPENAI_API_KEY` to be configured securely in the process environment.
