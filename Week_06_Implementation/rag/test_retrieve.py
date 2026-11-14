"""Offline tests for the Task 4 retrieval implementation."""

from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import retrieve


class CosineSimilarityTests(unittest.TestCase):
    def test_known_vectors(self) -> None:
        self.assertAlmostEqual(retrieve.cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(retrieve.cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(retrieve.cosine_similarity([1.0, 0.0], [-1.0, 0.0]), -1.0)

    def test_rejects_dimension_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "dimension mismatch"):
            retrieve.cosine_similarity([1.0], [1.0, 2.0])

    def test_rejects_zero_nonfinite_and_nonnumeric_vectors(self) -> None:
        for invalid in ([0.0, 0.0], [math.nan, 1.0], [True, 1.0], []):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                retrieve.cosine_similarity(invalid, [1.0, 0.0])


def sample_index() -> dict:
    def entry(chunk_id: str, vector: list[float], category: str = "source") -> dict:
        return {
            "chunk_id": chunk_id,
            "embedding": vector,
            "chunk": {
                "id": chunk_id,
                "file_path": f"{chunk_id}.py",
                "symbol": chunk_id,
                "category": category,
                "start_line": 1,
                "end_line": 2,
                "source_code": f"def {chunk_id}(): pass",
            },
        }

    return {
        "model": retrieve.MODEL,
        "dimension": 2,
        "entries": [
            entry("b", [1.0, 0.0]),
            entry("a", [1.0, 0.0], "test"),
            entry("c", [0.0, 1.0]),
        ],
    }


class RankingTests(unittest.TestCase):
    def test_top_n_order_and_deterministic_tie_break(self) -> None:
        results = retrieve.retrieve(sample_index(), [1.0, 0.0], top_n=2)
        self.assertEqual([result["chunk_id"] for result in results], ["a", "b"])

    def test_configurable_result_count_and_category(self) -> None:
        self.assertEqual(len(retrieve.retrieve(sample_index(), [1.0, 0.0], 1)), 1)
        tests = retrieve.retrieve(sample_index(), [1.0, 0.0], 5, "test")
        self.assertEqual([result["chunk_id"] for result in tests], ["a"])

    def test_result_includes_source_and_metadata(self) -> None:
        result = retrieve.retrieve(sample_index(), [0.0, 1.0], 1)[0]
        self.assertEqual(result["file_path"], "c.py")
        self.assertEqual(result["symbol"], "c")
        self.assertIn("source_code", result)

    def test_rejects_invalid_arguments(self) -> None:
        for top_n in (0, -1, True):
            with self.subTest(top_n=top_n), self.assertRaises(ValueError):
                retrieve.retrieve(sample_index(), [1.0, 0.0], top_n)
        with self.assertRaises(ValueError):
            retrieve.retrieve(sample_index(), [1.0], 1)
        with self.assertRaises(ValueError):
            retrieve.retrieve(sample_index(), [1.0, 0.0], 1, "invalid")


class QueryEmbeddingTests(unittest.TestCase):
    class Encoding:
        def encode(self, text: str) -> list[int]:
            return list(text.encode("utf-8"))

    def test_metadata_aware_query_and_dimension(self) -> None:
        recorded = {}

        def create(**kwargs):
            recorded.update(kwargs)
            return SimpleNamespace(data=[SimpleNamespace(embedding=[0.5, 0.5])])

        client = SimpleNamespace(embeddings=SimpleNamespace(create=create))
        vector = retrieve.embed_query(client, "Implement Money.__bool__", 2, self.Encoding())
        self.assertEqual(vector, [0.5, 0.5])
        self.assertEqual(recorded["model"], retrieve.MODEL)
        self.assertIn("Repository: AI4SE_Playground", recorded["input"])
        self.assertIn("Category: programming task", recorded["input"])

    def test_rejects_empty_task_and_bad_api_dimension(self) -> None:
        with self.assertRaises(ValueError):
            retrieve.build_query_text("  ")
        client = SimpleNamespace(
            embeddings=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    data=[SimpleNamespace(embedding=[1.0])]
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "dimension"):
            retrieve.embed_query(client, "task", 2, self.Encoding())


class ExistingStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rag = Path(__file__).resolve().parent

    def test_existing_store_loads_and_matches_all_ids(self) -> None:
        index = retrieve.load_index(self.rag / "chunks.json", self.rag / "embeddings.json")
        self.assertEqual(index["model"], retrieve.MODEL)
        self.assertEqual(index["dimension"], 1536)
        self.assertEqual(len(index["entries"]), 138)
        self.assertEqual(len({entry["chunk_id"] for entry in index["entries"]}), 138)

    def test_loader_rejects_duplicate_or_unknown_embedding_ids(self) -> None:
        chunks = json.loads((self.rag / "chunks.json").read_text(encoding="utf-8"))
        embeddings = json.loads((self.rag / "embeddings.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chunks_path, embeddings_path = root / "chunks.json", root / "embeddings.json"
            chunks_path.write_text(json.dumps(chunks), encoding="utf-8")

            duplicate = copy.deepcopy(embeddings)
            duplicate["embeddings"].append(copy.deepcopy(duplicate["embeddings"][0]))
            duplicate["embedding_count"] += 1
            embeddings_path.write_text(json.dumps(duplicate), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate embedding"):
                retrieve.load_index(chunks_path, embeddings_path)

            unknown = copy.deepcopy(embeddings)
            unknown["embeddings"][0]["chunk_id"] = "unknown"
            embeddings_path.write_text(json.dumps(unknown), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown chunk"):
                retrieve.load_index(chunks_path, embeddings_path)


if __name__ == "__main__":
    unittest.main()
