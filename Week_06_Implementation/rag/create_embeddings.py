"""Create and cache OpenAI embeddings for the Task 2 repository chunks."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable


MODEL = "text-embedding-3-small"
ENCODING_NAME = "cl100k_base"
MODEL_MAX_TOKENS = 8192
FORMAT_VERSION = 1
DEFAULT_BATCH_SIZE = 64
MAX_BATCH_TOKENS = 250_000  # Below the API's 300,000-token request limit.
MAX_RETRIES = 4


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def chunk_metadata(chunk: dict[str, Any]) -> dict[str, Any]:
    """Keep retrieval metadata without duplicating source text in the vector store."""
    keys = (
        "file_path",
        "category",
        "chunk_index",
        "kind",
        "symbol",
        "start_line",
        "end_line",
        "line_count",
        "class_name",
        "class_signature",
        "member_names",
        "part",
        "part_count",
    )
    return {key: chunk[key] for key in keys if key in chunk}


def embedding_text(repository: str, chunk: dict[str, Any]) -> str:
    """Build the exact representation used for both indexing and cache hashing."""
    metadata = chunk_metadata(chunk)
    header = [
        f"Repository: {repository}",
        f"File: {metadata['file_path']}",
        f"Category: {metadata['category']}",
        f"Kind: {metadata['kind']}",
        f"Symbol: {metadata['symbol']}",
        f"Lines: {metadata['start_line']}-{metadata['end_line']}",
    ]
    if metadata.get("class_name"):
        header.append(f"Class: {metadata['class_name']}")
    if metadata.get("member_names"):
        header.append("Members: " + ", ".join(metadata["member_names"]))
    return "\n".join([*header, "Source code:", chunk["source_code"]])


def content_hash(text: str) -> str:
    material = f"format={FORMAT_VERSION}\nmodel={MODEL}\n{text}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def prepare_chunks(payload: dict[str, Any], encoding: Any) -> list[dict[str, Any]]:
    repository = str(payload.get("repository", "unknown"))
    raw_chunks = payload.get("chunks")
    if not isinstance(raw_chunks, list):
        raise ValueError("chunks.json must contain a 'chunks' list")

    seen: set[str] = set()
    prepared = []
    for chunk in raw_chunks:
        chunk_id = chunk.get("id")
        source = chunk.get("source_code")
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("Every chunk must have a nonempty string ID")
        if chunk_id in seen:
            raise ValueError(f"Duplicate chunk ID: {chunk_id}")
        seen.add(chunk_id)
        if not isinstance(source, str) or not source.strip():
            continue

        text = embedding_text(repository, chunk)
        tokens = encoding.encode(text)
        embedded_tokens = tokens[:MODEL_MAX_TOKENS]
        prepared.append({
            "chunk_id": chunk_id,
            "content_hash": content_hash(text),
            "metadata": chunk_metadata(chunk),
            "token_count": len(tokens),
            "embedded_token_count": len(embedded_tokens),
            "truncated": len(tokens) > MODEL_MAX_TOKENS,
            "input": encoding.decode(embedded_tokens),
        })
    return prepared


def is_finite_vector(value: Any, dimension: int | None = None) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and (dimension is None or len(value) == dimension)
        and all(isinstance(number, (int, float)) and math.isfinite(number) for number in value)
    )


def reusable_entries(output: dict[str, Any], prepared: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if output.get("model") != MODEL or output.get("format_version") != FORMAT_VERSION:
        return {}
    dimension = output.get("embedding_dimension")
    if not isinstance(dimension, int) or dimension < 1:
        return {}
    expected_hashes = {item["chunk_id"]: item["content_hash"] for item in prepared}
    reusable = {}
    for entry in output.get("embeddings", []):
        chunk_id = entry.get("chunk_id")
        if (
            chunk_id in expected_hashes
            and entry.get("content_hash") == expected_hashes[chunk_id]
            and is_finite_vector(entry.get("embedding"), dimension)
        ):
            reusable[chunk_id] = entry
    return reusable


def batches(items: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    batch: list[dict[str, Any]] = []
    token_total = 0
    for item in items:
        item_tokens = item["embedded_token_count"]
        if batch and (len(batch) >= batch_size or token_total + item_tokens > MAX_BATCH_TOKENS):
            yield batch
            batch, token_total = [], 0
        batch.append(item)
        token_total += item_tokens
    if batch:
        yield batch


def request_embeddings(client: Any, batch: list[dict[str, Any]]) -> list[list[float]]:
    """Call the API with bounded exponential backoff for transient failures."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model=MODEL,
                input=[item["input"] for item in batch],
                encoding_format="float",
            )
            ordered = sorted(response.data, key=lambda item: item.index)
            if len(ordered) != len(batch):
                raise RuntimeError("Embedding API returned an unexpected result count")
            return [item.embedding for item in ordered]
        except Exception as error:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"Embedding request failed after {MAX_RETRIES} attempts: "
                    f"{type(error).__name__}: {error}"
                ) from error
            delay = min(2**attempt + random.random(), 10.0)
            print(
                f"Embedding request failed ({type(error).__name__}); retrying in {delay:.1f}s...",
                file=sys.stderr,
            )
            time.sleep(delay)
    raise AssertionError("unreachable")


def make_entry(item: dict[str, Any], vector: list[float]) -> dict[str, Any]:
    return {
        "chunk_id": item["chunk_id"],
        "content_hash": item["content_hash"],
        "metadata": item["metadata"],
        "token_count": item["token_count"],
        "embedded_token_count": item["embedded_token_count"],
        "truncated": item["truncated"],
        "embedding": vector,
    }


def build_output(
    source_path: Path,
    prepared: list[dict[str, Any]],
    entries: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ordered = [entries[item["chunk_id"]] for item in prepared if item["chunk_id"] in entries]
    dimensions = {len(entry["embedding"]) for entry in ordered}
    dimension = next(iter(dimensions)) if len(dimensions) == 1 else None
    token_counts = [item["token_count"] for item in prepared]
    return {
        "format_version": FORMAT_VERSION,
        "source_chunks_file": source_path.name,
        "model": MODEL,
        "tokenizer": ENCODING_NAME,
        "model_max_tokens": MODEL_MAX_TOKENS,
        "embedding_dimension": dimension,
        "source_chunk_count": len(prepared),
        "embedding_count": len(ordered),
        "token_statistics": {
            "total": sum(token_counts),
            "minimum": min(token_counts, default=0),
            "maximum": max(token_counts, default=0),
            "mean": round(statistics.fmean(token_counts), 2) if token_counts else 0,
            "truncated_chunks": sum(item["truncated"] for item in prepared),
        },
        "embeddings": ordered,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def validate_output(payload: dict[str, Any], expected_ids: set[str] | None = None) -> tuple[int, int]:
    entries = payload.get("embeddings")
    dimension = payload.get("embedding_dimension")
    if not isinstance(entries, list) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("Output has no complete embedding collection or consistent dimension")
    ids = [entry.get("chunk_id") for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Output contains duplicate chunk IDs")
    if expected_ids is not None and set(ids) != expected_ids:
        missing = expected_ids - set(ids)
        extra = set(ids) - expected_ids
        raise ValueError(f"Embedding coverage mismatch: missing={len(missing)}, extra={len(extra)}")
    if not all(is_finite_vector(entry.get("embedding"), dimension) for entry in entries):
        raise ValueError("Output contains a non-finite, non-numeric, empty, or inconsistent vector")
    if payload.get("embedding_count") != len(entries):
        raise ValueError("embedding_count does not match stored entries")
    return len(entries), dimension


def print_token_statistics(prepared: list[dict[str, Any]]) -> None:
    counts = [item["token_count"] for item in prepared]
    print(f"Nonempty chunks: {len(prepared)}")
    print(
        "Token statistics: "
        f"total={sum(counts)}, min={min(counts, default=0)}, "
        f"max={max(counts, default=0)}, "
        f"mean={statistics.fmean(counts):.2f}" if counts else "Token statistics: no inputs"
    )
    print(f"Chunks requiring truncation: {sum(item['truncated'] for item in prepared)}")


def parse_args() -> argparse.Namespace:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=directory / "chunks.json")
    parser.add_argument("--output", type=Path, default=directory / "embeddings.json")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate chunks and report token counts without using credentials or the API",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate an existing complete embedding store without using the API",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1 or args.batch_size > 2048:
        raise SystemExit("--batch-size must be between 1 and 2048")
    if args.validate_only:
        count, dimension = validate_output(load_json(args.output))
        print(f"Valid embedding store: {count} embeddings, dimension {dimension}.")
        return

    try:
        import tiktoken
    except ImportError as error:
        raise SystemExit("Missing dependency: install requirements from rag/requirements.txt") from error

    source_payload = load_json(args.chunks)
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    prepared = prepare_chunks(source_payload, encoding)
    print_token_statistics(prepared)
    if args.dry_run:
        print("Dry run complete; no API request was made and no embeddings were written.")
        return

    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise SystemExit("OPENAI_API_KEY is not set; no API request was made.")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit("Missing dependency: install requirements from rag/requirements.txt") from error

    existing = load_json(args.output) if args.output.exists() else {}
    entries = reusable_entries(existing, prepared)
    pending = [item for item in prepared if item["chunk_id"] not in entries]
    print(f"Reusing {len(entries)} cached embeddings; generating {len(pending)}.")

    client = OpenAI()
    for number, batch in enumerate(batches(pending, args.batch_size), start=1):
        vectors = request_embeddings(client, batch)
        known_dimensions = {len(entry["embedding"]) for entry in entries.values()}
        batch_dimensions = {len(vector) for vector in vectors}
        dimensions = known_dimensions | batch_dimensions
        if len(dimensions) != 1 or not all(is_finite_vector(vector) for vector in vectors):
            raise RuntimeError("API returned non-finite or inconsistent embedding vectors")
        for item, vector in zip(batch, vectors):
            entries[item["chunk_id"]] = make_entry(item, vector)
        atomic_write_json(args.output, build_output(args.chunks, prepared, entries))
        print(f"Saved batch {number}: {len(entries)}/{len(prepared)} embeddings available.")

    output = build_output(args.chunks, prepared, entries)
    atomic_write_json(args.output, output)
    count, dimension = validate_output(output, {item["chunk_id"] for item in prepared})
    print(f"Verified {count} embeddings with consistent dimension {dimension}.")
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
