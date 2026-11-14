# Task 2: Repository chunking

## Strategy

The chunker uses Python's standard-library `ast` module. It processes every `.py` file in the playground, including unit tests. Tests are included because they contain concrete examples, expected behavior, edge cases, and error semantics that can help later retrieval and code generation.

Top-level functions and classes are semantic boundaries. A complete definition is kept as one chunk when it fits. The imports, module docstring, constants, and other content before the first definition form a `module_context` chunk. This gives retrieved definitions useful module-level context without repeating it in every chunk.

Large classes are divided into contiguous groups of methods whose combined span fits the size limit. Each such chunk records the class name, class declaration, and included member names. If a single function or method is itself too large, it is divided into numbered, contiguous line windows. This fallback enforces the limit while preserving source order and line metadata.

## Chunk size

The selected soft maximum is **120 source lines**. For this small, well-structured Python repository, that is large enough to preserve most production classes or related groups of methods, while avoiding very large test-class chunks. Line count is deterministic, model-independent, and easy to inspect. Token lengths will vary, so Task 3 should measure the chosen embedding model's tokenizer if it imposes a stricter token limit.

## Data and metadata

The generated `chunks.json` contains repository-level settings and one object per chunk. Each chunk has a stable content-location ID, repository-relative file path, source/test category, semantic kind and symbol, 1-based start/end lines, line count, and exact source text. Split class chunks additionally include the class name, class signature, and member names; line-window splits contain part numbers.

## Trade-offs

AST chunking preserves Python semantics better than fixed character windows and requires no external package. Grouping nearby class members limits the number of tiny chunks, while including tests improves behavioral retrieval at the cost of a larger index and possible competition with production code. The `category` field lets later retrieval filter or re-rank test chunks. Comments located only between top-level definitions are not emitted as independent chunks, although comments and docstrings inside selected structures are preserved.

## Verification results

The generator processed **27 Python files** (13 production files and 14 test/package files) and produced **138 chunks**: 49 source chunks and 89 test chunks. All 26 non-empty files have at least one chunk; `tests/__init__.py` is empty and therefore correctly produces none. Chunk IDs are unique, every stored source excerpt exactly matches its indicated lines in the original file, and the largest observed chunk is 119 lines. Parsing all files through `ast` found no syntax errors.

Representative chunks were inspected from `models.py`, `inventory.py`, and large test modules. They retain semantic names, exact line ranges, source code, and class/member context where applicable. The original playground test suite was also executed: 481 tests were discovered, with 35 failures and 17 errors caused by incomplete implementations already present in the playground (for example, methods returning `None`). The chunker does not modify or attempt to fix that source repository.

For Task 3, token counts should be measured with the selected embedding model, and retrieval should consider giving production chunks a higher rank while retaining tests as behavioral evidence. The current location-derived IDs are stable while file paths and line ranges remain unchanged; a later pipeline may prefer content hashes if it needs identity across source edits.

Run the generator from the repository root with:

```text
python Week_06_Implementation/rag/chunk_repository.py
```

The script also accepts `--repository`, `--output`, and `--max-lines` arguments.
