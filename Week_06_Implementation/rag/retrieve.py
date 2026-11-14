"""Retrieve repository chunks most relevant to a textual programming task."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable


MODEL = "text-embedding-3-small"
TOKENIZER = "cl100k_base"
MAX_QUERY_TOKENS = 8192
DEFAULT_TOP_N = 5


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as error:
        raise ValueError(f"Required data file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def finite_vector(value: Any, dimension: int | None = None) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and (dimension is None or len(value) == dimension)
        and all(
            isinstance(number, (int, float))
            and not isinstance(number, bool)
            and math.isfinite(number)
            for number in value
        )
    )


def vector_norm(vector: list[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in vector))


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for finite, equally sized, non-zero vectors."""
    if not finite_vector(left) or not finite_vector(right):
        raise ValueError("Cosine similarity requires nonempty finite numeric vectors")
    if len(left) != len(right):
        raise ValueError(f"Vector dimension mismatch: {len(left)} != {len(right)}")
    left_norm, right_norm = vector_norm(left), vector_norm(right)
    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("Cosine similarity is undefined for a zero-length vector")
    return math.fsum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def load_index(chunks_path: Path, embeddings_path: Path) -> dict[str, Any]:
    chunks_payload = load_json(chunks_path)
    embeddings_payload = load_json(embeddings_path)
    model = embeddings_payload.get("model")
    dimension = embeddings_payload.get("embedding_dimension")
    entries = embeddings_payload.get("embeddings")
    chunks = chunks_payload.get("chunks")

    if model != MODEL:
        raise ValueError(f"Embedding model mismatch: expected {MODEL}, found {model!r}")
    if not isinstance(dimension, int) or dimension < 1:
        raise ValueError("Embedding store has no valid embedding_dimension")
    if not isinstance(entries, list) or not isinstance(chunks, list):
        raise ValueError("Embedding and chunk stores must contain list collections")

    chunk_by_id: dict[str, dict[str, Any]] = {}
    for chunk in chunks:
        chunk_id = chunk.get("id") if isinstance(chunk, dict) else None
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("Every source chunk must have a nonempty string ID")
        if chunk_id in chunk_by_id:
            raise ValueError(f"Duplicate source chunk ID: {chunk_id}")
        chunk_by_id[chunk_id] = chunk

    indexed = []
    embedding_ids: set[str] = set()
    for entry in entries:
        chunk_id = entry.get("chunk_id") if isinstance(entry, dict) else None
        vector = entry.get("embedding") if isinstance(entry, dict) else None
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("Every embedding must have a nonempty string chunk_id")
        if chunk_id in embedding_ids:
            raise ValueError(f"Duplicate embedding chunk ID: {chunk_id}")
        if chunk_id not in chunk_by_id:
            raise ValueError(f"Embedding refers to unknown chunk ID: {chunk_id}")
        if not finite_vector(vector, dimension):
            raise ValueError(f"Invalid embedding vector for chunk {chunk_id}")
        if vector_norm(vector) == 0.0:
            raise ValueError(f"Zero-length embedding vector for chunk {chunk_id}")
        embedding_ids.add(chunk_id)
        indexed.append({"chunk_id": chunk_id, "embedding": vector, "chunk": chunk_by_id[chunk_id]})

    nonempty_ids = {
        chunk_id
        for chunk_id, chunk in chunk_by_id.items()
        if isinstance(chunk.get("source_code"), str) and chunk["source_code"].strip()
    }
    if embedding_ids != nonempty_ids:
        raise ValueError(
            "Chunk/embedding coverage mismatch: "
            f"missing={len(nonempty_ids - embedding_ids)}, extra={len(embedding_ids - nonempty_ids)}"
        )
    if embeddings_payload.get("embedding_count") != len(indexed):
        raise ValueError("embedding_count does not match the stored embedding records")
    return {"model": model, "dimension": dimension, "entries": indexed}


def build_query_text(task: str, repository: str = "AI4SE_Playground") -> str:
    if not isinstance(task, str) or not task.strip():
        raise ValueError("Programming task must be nonempty text")
    return "\n".join(
        [
            f"Repository: {repository}",
            "Category: programming task",
            "Intent: find relevant source code and tests",
            "Task:",
            task.strip(),
        ]
    )


def embed_query(client: Any, task: str, dimension: int, encoding: Any) -> list[float]:
    text = build_query_text(task)
    token_count = len(encoding.encode(text))
    if token_count > MAX_QUERY_TOKENS:
        raise ValueError(f"Query is too long: {token_count} tokens (maximum {MAX_QUERY_TOKENS})")
    response = client.embeddings.create(model=MODEL, input=text, encoding_format="float")
    if len(response.data) != 1:
        raise RuntimeError("Embedding API returned an unexpected result count")
    vector = response.data[0].embedding
    if not finite_vector(vector, dimension):
        actual = len(vector) if isinstance(vector, list) else "invalid"
        raise ValueError(f"Query embedding dimension/value mismatch: expected {dimension}, found {actual}")
    if vector_norm(vector) == 0.0:
        raise ValueError("Query embedding is a zero-length vector")
    return vector


def retrieve(
    index: dict[str, Any],
    query_embedding: list[float],
    top_n: int = DEFAULT_TOP_N,
    category: str = "all",
) -> list[dict[str, Any]]:
    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
        raise ValueError("top_n must be a positive integer")
    if category not in {"all", "source", "test"}:
        raise ValueError("category must be one of: all, source, test")
    dimension = index.get("dimension")
    if not finite_vector(query_embedding, dimension):
        raise ValueError(f"Query embedding must be a finite {dimension}-dimensional vector")
    if vector_norm(query_embedding) == 0.0:
        raise ValueError("Query embedding is a zero-length vector")

    results = []
    for entry in index.get("entries", []):
        chunk = entry["chunk"]
        if category != "all" and chunk.get("category") != category:
            continue
        results.append({
            "chunk_id": entry["chunk_id"],
            "similarity": cosine_similarity(query_embedding, entry["embedding"]),
            "file_path": chunk["file_path"],
            "symbol": chunk["symbol"],
            "category": chunk["category"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "source_code": chunk["source_code"],
        })
    # Stable chunk ID is the deterministic secondary key for equal similarities.
    results.sort(key=lambda result: (-result["similarity"], result["chunk_id"]))
    return results[:top_n]


def format_results(results: Iterable[dict[str, Any]]) -> str:
    sections = []
    for rank, result in enumerate(results, start=1):
        sections.append(
            "\n".join(
                [
                    f"[{rank}] score={result['similarity']:.6f} id={result['chunk_id']}",
                    f"    {result['file_path']}:{result['start_line']}-{result['end_line']}",
                    f"    symbol={result['symbol']} category={result['category']}",
                    "```python",
                    result["source_code"],
                    "```",
                ]
            )
        )
    return "\n\n".join(sections)


def parse_args() -> argparse.Namespace:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", nargs="+", help="Textual programming task")
    parser.add_argument("-n", "--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--category", choices=("all", "source", "test"), default="all")
    parser.add_argument("--chunks", type=Path, default=directory / "chunks.json")
    parser.add_argument("--embeddings", type=Path, default=directory / "embeddings.json")
    parser.add_argument("--json", action="store_true", help="Print results as JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    task = " ".join(args.task)
    try:
        build_query_text(task)
        if args.top_n < 1:
            raise ValueError("top_n must be a positive integer")
        index = load_index(args.chunks, args.embeddings)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise SystemExit("OPENAI_API_KEY is not set; query embedding was not generated.")
    try:
        import tiktoken
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit("Missing dependency: install requirements from rag/requirements.txt") from error

    try:
        query_embedding = embed_query(
            OpenAI(), task, index["dimension"], tiktoken.get_encoding(TOKENIZER)
        )
        results = retrieve(index, query_embedding, args.top_n, args.category)
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(results, indent=2, ensure_ascii=False) if args.json else format_results(results))


if __name__ == "__main__":
    main()
