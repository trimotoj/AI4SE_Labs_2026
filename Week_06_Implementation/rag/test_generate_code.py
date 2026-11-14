"""Credential-free tests for the Task 5 generation pipeline."""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import generate_code


class TargetLocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = Path(__file__).resolve().parent.parent
        cls.repository = cls.implementation / "AI4SE_Playground"
        cls.tasks = generate_code.load_tasks(cls.implementation / "Assignments" / "missing_code.json")

    def test_all_ten_real_targets_match_completed_artifacts(self) -> None:
        self.assertEqual(len(self.tasks), 10)
        artifact = json.loads(
            (Path(__file__).resolve().parent / "generation_results.json").read_text(encoding="utf-8")
        )
        records = {
            (record["file"], record["class"], record["method"]): record
            for record in artifact["tasks"]
        }
        repair = json.loads(
            (Path(__file__).resolve().parent / "repair_results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(records), 10)
        for target in self.tasks:
            located = generate_code.locate_method(self.repository, target)
            record = records[(target.file, target.class_name, target.method)]
            expected_body = record["generated_body"]
            if target.key == repair["repair_target"]:
                expected_body = repair["new_implementation"]
            self.assertEqual(
                generate_code.current_body_fingerprint(located.method_node),
                generate_code.generated_body_fingerprint(expected_body),
            )

    def test_property_signature_and_class_context_are_preserved(self) -> None:
        target = self.tasks[0]
        located = generate_code.locate_method(self.repository, target)
        context = generate_code.target_context(located)
        self.assertIn("@property", context["signature"])
        candidate = generate_code.replace_method_body(located, target, "return self.value == 'x'")
        tree = ast.parse(candidate)
        method = next(
            item
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == target.class_name
            for item in node.body
            if isinstance(item, ast.FunctionDef) and item.name == target.method
        )
        self.assertEqual(len(method.decorator_list), 1)
        self.assertEqual(method.args.args[0].arg, "self")


class OutputValidationTests(unittest.TestCase):
    def test_accepts_regular_and_generator_bodies(self) -> None:
        self.assertEqual(
            generate_code.parse_generated_body('{"body":"return len(self._items)"}'),
            "return len(self._items)",
        )
        body = generate_code.parse_generated_body('{"body":"for item in self._items:\\n    yield item"}')
        self.assertIn("yield item", body)

    def test_rejects_malformed_or_unsafe_output(self) -> None:
        invalid = [
            "```json\n{\"body\":\"return 1\"}\n```",
            '{"body":"pass"}',
            '{"body":"import os\\nreturn 1"}',
            '{"body":"def changed():\\n    return 1"}',
            '{"body":"return 1", "extra": true}',
        ]
        for output in invalid:
            with self.subTest(output=output), self.assertRaises(ValueError):
                generate_code.parse_generated_body(output)

    def test_replacement_changes_only_body_text(self) -> None:
        source = "class Example:\n    @staticmethod\n    def value(x: int) -> int:\n        pass\n\n    def other(self):\n        return 2\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "example.py"
            path.write_text(source, encoding="utf-8")
            target = generate_code.Target("example.py", "Example", "value", "return x")
            located = generate_code.locate_method(root, target)
            candidate = generate_code.replace_method_body(located, target, "return x")
            self.assertIn("@staticmethod\n    def value(x: int) -> int:", candidate)
            self.assertIn("def other(self):\n        return 2", candidate)
            self.assertNotIn("        pass", candidate)


class PromptAndApiTests(unittest.TestCase):
    def test_prompt_requires_exactly_five_chunks_and_contains_evidence(self) -> None:
        target = generate_code.Target("x.py", "X", "method", "Return one")
        context = {"signature": "def method(self):", "class_source": "class X: ..."}
        results = [
            {
                "chunk_id": str(index),
                "similarity": 1.0 - index / 10,
                "file_path": "x.py",
                "symbol": "X",
                "category": "source" if index == 0 else "test",
                "start_line": 1,
                "end_line": 2,
                "source_code": "code",
            }
            for index in range(5)
        ]
        prompt = generate_code.build_prompt(target, context, results)
        self.assertEqual(prompt.count("### Retrieved chunk"), 5)
        self.assertIn("def method(self):", prompt)
        self.assertIn("Return one", prompt)
        with self.assertRaises(ValueError):
            generate_code.build_prompt(target, context, results[:4])

    def test_generation_uses_permitted_model_and_response_text(self) -> None:
        recorded = {}

        def create(**kwargs):
            recorded.update(kwargs)
            return SimpleNamespace(
                id="response-1",
                model=generate_code.GENERATION_MODEL,
                status="completed",
                incomplete_details=None,
                output_text='{\"body\":\"return 1\"}',
                usage=None,
            )

        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        result = generate_code.request_generation(client, "prompt")
        self.assertEqual(recorded["model"], "gpt-5-mini")
        self.assertEqual(recorded["max_output_tokens"], 4096)
        self.assertEqual(recorded["reasoning"], {"effort": "low"})
        self.assertEqual(result["response_id"], "response-1")

    def test_incomplete_response_reports_reason_and_token_usage(self) -> None:
        response = SimpleNamespace(
            id="response-incomplete",
            model=generate_code.GENERATION_MODEL,
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            output_text="",
            usage=SimpleNamespace(
                input_tokens=2345,
                output_tokens=4096,
                output_tokens_details=SimpleNamespace(reasoning_tokens=4000),
            ),
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=lambda **kwargs: response)
        )
        with self.assertRaises(RuntimeError) as raised:
            generate_code.request_generation(client, "prompt")
        message = str(raised.exception)
        for expected in (
            "status='incomplete'",
            "reason='max_output_tokens'",
            "input_tokens=2345",
            "output_tokens=4096",
            "reasoning_tokens=4000",
            "configured_max_output_tokens=4096",
            "reasoning_effort='low'",
        ):
            self.assertIn(expected, message)

    def test_repair_prompt_contains_dependencies_error_and_no_invention_rule(self) -> None:
        target = generate_code.Target("pricing.py", "BulkDiscountPricing", "price", "Discount total")
        context = {"signature": "def price(self, items):", "class_source": "class BulkDiscountPricing: ..."}
        results = [
            {
                "chunk_id": str(index),
                "similarity": 0.9 - index / 10,
                "file_path": "test_pricing.py",
                "symbol": "Tests",
                "category": "test",
                "start_line": 1,
                "end_line": 2,
                "source_code": "assert price",
            }
            for index in range(5)
        ]
        prompt = generate_code.build_repair_prompt(
            target,
            context,
            results,
            {"Money class": "class Money:\n    @property\n    def cents(self): ...", "FlatPricing.price": "def price(self, items): ..."},
            "return base.amount",
            "AttributeError: Money has no attribute amount",
        )
        self.assertEqual(prompt.count("### Retrieved chunk"), 5)
        self.assertIn("def cents", prompt)
        self.assertIn("FlatPricing.price", prompt)
        self.assertIn("AttributeError", prompt)
        self.assertIn("Do not invent APIs", prompt)


class StoreTests(unittest.TestCase):
    def test_real_fixed_embedding_snapshot_loads(self) -> None:
        rag = Path(__file__).resolve().parent
        index = generate_code.retrieve.load_index(rag / "chunks.json", rag / "embeddings.json")
        self.assertEqual(len(index["entries"]), 138)
        self.assertEqual(index["dimension"], 1536)

    def test_real_completed_repair_and_dependency_context(self) -> None:
        rag = Path(__file__).resolve().parent
        repository = rag.parent / "AI4SE_Playground"
        repair = json.loads((rag / "repair_results.json").read_text(encoding="utf-8"))
        target = generate_code.Target(
            "playground/playground/pricing.py",
            "BulkDiscountPricing",
            "price",
            "completed repair",
        )
        located = generate_code.locate_method(repository, target)
        self.assertEqual(repair["status"], "completed")
        self.assertEqual(repair["repair_target"], target.key)
        self.assertIn("base.amount", repair["previous_implementation"])
        self.assertIn("base.cents", repair["new_implementation"])
        self.assertEqual(
            generate_code.current_body_fingerprint(located.method_node),
            generate_code.generated_body_fingerprint(repair["new_implementation"]),
        )
        self.assertIn("def cents", repair["dependency_context"]["Money class"])
        self.assertIn("subtotal.cents", repair["dependency_context"]["FlatPricing.price"])


class RestoreTests(unittest.TestCase):
    def test_guarded_restore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "module.py"
            generated = "def value():\n    return 1\n"
            original = "def value():\n    pass\n"
            source.write_text(generated, encoding="utf-8")
            artifact = root / "results.json"
            artifact.write_text(
                json.dumps({
                    "status": "completed",
                    "original_files": {"module.py": original},
                    "final_file_hashes": {"module.py": generate_code.sha256_text(generated)},
                }),
                encoding="utf-8",
            )
            self.assertEqual(generate_code.restore_from_artifact(root, artifact), 1)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(json.loads(artifact.read_text(encoding="utf-8"))["status"], "restored")


if __name__ == "__main__":
    unittest.main()
