"""Run the Task 5 RAG pipeline and safely fill selected Python method stubs."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import retrieve


GENERATION_MODEL = "gpt-5-mini"
TOP_N = 5
ARTIFACT_VERSION = 1
MAX_OUTPUT_TOKENS = 4096
REASONING_EFFORT = "low"


@dataclass(frozen=True)
class Target:
    file: str
    class_name: str
    method: str
    task_text: str

    @property
    def key(self) -> str:
        return f"{self.class_name}.{self.method}"


@dataclass
class LocatedMethod:
    path: Path
    source: str
    tree: ast.Module
    class_node: ast.ClassDef
    method_node: ast.FunctionDef | ast.AsyncFunctionDef


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_tasks(path: Path) -> list[Target]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Task file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid task JSON: {error}") from error
    if not isinstance(raw, list) or not raw:
        raise ValueError("Task file must contain a nonempty JSON list")
    targets = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Every task entry must be an object")
        values = [item.get(name) for name in ("file", "class", "method", "docstring")]
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("Every task requires nonempty file, class, method, and docstring fields")
        target = Target(values[0], values[1], values[2], values[3].strip())
        if (target.file, target.class_name, target.method) in seen:
            raise ValueError(f"Duplicate task target: {target.file}:{target.key}")
        seen.add((target.file, target.class_name, target.method))
        targets.append(target)
    return targets


def select_targets(targets: list[Target], only: list[str], task_text: str | None) -> list[Target]:
    if only:
        requested = set(only)
        selected = [target for target in targets if target.key in requested]
        missing = requested - {target.key for target in selected}
        if missing:
            raise ValueError(f"Unknown --only target(s): {', '.join(sorted(missing))}")
    else:
        selected = targets
    if task_text is not None:
        if len(selected) != 1:
            raise ValueError("--task-text requires exactly one selected target")
        if not task_text.strip():
            raise ValueError("--task-text must be nonempty")
        target = selected[0]
        selected = [Target(target.file, target.class_name, target.method, task_text.strip())]
    return selected


def locate_method(repository: Path, target: Target) -> LocatedMethod:
    path = (repository / target.file).resolve()
    try:
        path.relative_to(repository.resolve())
    except ValueError as error:
        raise ValueError(f"Target path escapes repository: {target.file}") from error
    if not path.is_file():
        raise ValueError(f"Target file does not exist: {target.file}")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == target.class_name]
    if len(classes) != 1:
        raise ValueError(f"Expected one top-level class {target.class_name} in {target.file}")
    methods = [
        node
        for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target.method
    ]
    if len(methods) != 1:
        raise ValueError(f"Expected one method {target.key} in {target.file}")
    return LocatedMethod(path, source, tree, classes[0], methods[0])


def is_pass_stub(method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return len(method.body) == 1 and isinstance(method.body[0], ast.Pass)


def source_segment(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise ValueError("Could not extract AST source segment")
    return segment


def decorator_start(method: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return min([method.lineno, *(item.lineno for item in method.decorator_list)])


def target_context(located: LocatedMethod) -> dict[str, str | int]:
    method = located.method_node
    class_node = located.class_node
    lines = located.source.splitlines()
    body_start = method.body[0].lineno
    signature = "\n".join(lines[decorator_start(method) - 1 : body_start - 1])
    return {
        "signature": signature,
        "class_source": source_segment(located.source, class_node),
        "method_source": source_segment(located.source, method),
        "start_line": decorator_start(method),
        "end_line": method.end_lineno,
    }


def task_query(target: Target) -> str:
    return (
        f"Implement the missing Python method {target.key} in {target.file}.\n"
        f"Required behavior: {target.task_text}"
    )


def build_prompt(target: Target, context: dict[str, Any], results: list[dict[str, Any]]) -> str:
    if len(results) != TOP_N:
        raise ValueError(f"Generation requires exactly {TOP_N} retrieved chunks")
    retrieved_sections = []
    for rank, result in enumerate(results, start=1):
        retrieved_sections.append(
            "\n".join(
                [
                    f"### Retrieved chunk {rank}",
                    f"ID: {result['chunk_id']}",
                    f"Similarity: {result['similarity']:.8f}",
                    f"File: {result['file_path']}",
                    f"Symbol: {result['symbol']}",
                    f"Category: {result['category']}",
                    f"Lines: {result['start_line']}-{result['end_line']}",
                    "```python",
                    result["source_code"],
                    "```",
                ]
            )
        )
    return "\n\n".join(
        [
            "# Programming task",
            task_query(target),
            "# Existing target signature (must remain unchanged)",
            "```python\n" + context["signature"] + "\n```",
            "# Surrounding target class context",
            "```python\n" + context["class_source"] + "\n```",
            "# Retrieved RAG context (exactly five chunks)",
            *retrieved_sections,
            "# Output contract",
            (
                'Return only a JSON object with one string field named "body". The string must contain '
                "only the Python statements for the method body, without the signature, decorators, Markdown, "
                "or a docstring. Use only existing imports. Do not modify any other code."
            ),
        ]
    )


def find_top_level_class_source(path: Path, class_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    matches = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(matches) != 1:
        raise ValueError(f"Expected one top-level class {class_name} in {path}")
    return source_segment(source, matches[0])


def find_class_method_source(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    methods = [
        node
        for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name
    ] if len(classes) == 1 else []
    if len(methods) != 1:
        raise ValueError(f"Expected one method {class_name}.{method_name} in {path}")
    return source_segment(source, methods[0])


def repair_dependency_context(repository: Path) -> dict[str, str]:
    package = repository / "playground" / "playground"
    return {
        "Money class": find_top_level_class_source(package / "models.py", "Money"),
        "FlatPricing.price": find_class_method_source(package / "pricing.py", "FlatPricing", "price"),
    }


def build_repair_prompt(
    target: Target,
    context: dict[str, Any],
    results: list[dict[str, Any]],
    dependencies: dict[str, str],
    previous_body: str,
    exception_context: str,
) -> str:
    base = build_prompt(target, context, results)
    dependency_sections = [
        f"## Verified dependency: {name}\n```python\n{source}\n```"
        for name, source in dependencies.items()
    ]
    return "\n\n".join(
        [
            base,
            "# Repair context",
            "Previous generated body:\n```python\n" + previous_body + "\n```",
            "Observed exception:\n" + exception_context,
            "# Independently verified dependency context",
            *dependency_sections,
            (
                "The task specification and verified dependency source are authoritative. "
                "Use only attributes, methods, and constructors visibly defined in the supplied source. "
                "Do not invent APIs. Correct only the selected method body."
            ),
            (
                'Return only a JSON object with one string field named "body". The string must contain '
                "only the replacement Python statements, without signature, decorators, Markdown, or a docstring."
            ),
        ]
    )


def request_generation(client: Any, prompt: str) -> dict[str, Any]:
    response = client.responses.create(
        model=GENERATION_MODEL,
        instructions=(
            "You implement one missing Python method using the supplied repository evidence. "
            "Follow the JSON output contract exactly and make the smallest correct implementation."
        ),
        input=prompt,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        reasoning={"effort": REASONING_EFFORT},
    )
    diagnostics = response_diagnostics(response)
    if diagnostics["status"] != "completed":
        raise RuntimeError(format_incomplete_diagnostics(diagnostics))
    output_text = getattr(response, "output_text", None)
    if not isinstance(output_text, str) or not output_text.strip():
        raise RuntimeError("Generation response contained no output text")
    return {
        "response_id": getattr(response, "id", None),
        "response_model": getattr(response, "model", GENERATION_MODEL),
        "output_text": output_text,
        "usage": usage_to_dict(getattr(response, "usage", None)),
    }


def value_from(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def response_diagnostics(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    output_details = value_from(usage, "output_tokens_details")
    incomplete_details = getattr(response, "incomplete_details", None)
    return {
        "status": getattr(response, "status", None),
        "incomplete_reason": value_from(incomplete_details, "reason"),
        "input_tokens": value_from(usage, "input_tokens"),
        "output_tokens": value_from(usage, "output_tokens"),
        "reasoning_tokens": value_from(output_details, "reasoning_tokens"),
        "configured_max_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning_effort": REASONING_EFFORT,
    }


def format_incomplete_diagnostics(diagnostics: dict[str, Any]) -> str:
    return (
        "Generation response did not complete: "
        f"status={diagnostics['status']!r}, "
        f"reason={diagnostics['incomplete_reason']!r}, "
        f"input_tokens={diagnostics['input_tokens']!r}, "
        f"output_tokens={diagnostics['output_tokens']!r}, "
        f"reasoning_tokens={diagnostics['reasoning_tokens']!r}, "
        f"configured_max_output_tokens={diagnostics['configured_max_output_tokens']}, "
        f"reasoning_effort={diagnostics['reasoning_effort']!r}"
    )


def usage_to_dict(usage: Any) -> dict[str, Any] | None:
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    result = {}
    for name in ("input_tokens", "output_tokens", "total_tokens"):
        value = getattr(usage, name, None)
        if value is not None:
            result[name] = value
    return result or None


def parse_generated_body(output_text: str) -> str:
    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"Model output is not strict JSON: {error}") from error
    if not isinstance(payload, dict) or set(payload) != {"body"}:
        raise ValueError('Model output must be exactly {"body": "..."}')
    body = payload["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("Generated method body must be nonempty text")
    body = textwrap.dedent(body).strip("\r\n")
    if not body.strip():
        raise ValueError("Generated method body must contain statements")
    try:
        wrapper = ast.parse("def _generated():\n" + textwrap.indent(body, "    "))
    except SyntaxError as error:
        raise ValueError(f"Generated method body is invalid Python: {error}") from error
    statements = wrapper.body[0].body
    if len(statements) == 1 and isinstance(statements[0], ast.Pass):
        raise ValueError("Generated method body is still a pass stub")
    forbidden = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)
    if any(isinstance(node, forbidden) for statement in statements for node in ast.walk(statement)):
        raise ValueError("Generated body contains a forbidden definition, import, or scope declaration")
    return body


def signature_fingerprint(method: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    clone = copy.deepcopy(method)
    clone.body = [ast.Pass()]
    return ast.dump(clone, include_attributes=False)


def replace_method_body(located: LocatedMethod, target: Target, generated_body: str) -> str:
    method = located.method_node
    if not method.body:
        raise ValueError(f"Target method has no AST body: {target.key}")
    lines = located.source.splitlines(keepends=True)
    start = method.body[0].lineno - 1
    end = method.body[-1].end_lineno
    original_line = lines[start]
    indent = original_line[: len(original_line) - len(original_line.lstrip(" \t"))]
    newline = "\r\n" if "\r\n" in located.source else "\n"
    replacement = "".join(
        (indent + line if line.strip() else "") + newline
        for line in generated_body.splitlines()
    )
    candidate = "".join(lines[:start]) + replacement + "".join(lines[end:])
    try:
        candidate_tree = ast.parse(candidate, filename=str(located.path))
    except SyntaxError as error:
        raise ValueError(f"Candidate file is not valid Python: {error}") from error
    candidate_classes = [
        node for node in candidate_tree.body if isinstance(node, ast.ClassDef) and node.name == target.class_name
    ]
    candidate_methods = [
        node
        for node in candidate_classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target.method
    ] if len(candidate_classes) == 1 else []
    if len(candidate_methods) != 1:
        raise ValueError("Candidate changed the target class/method structure")
    if signature_fingerprint(method) != signature_fingerprint(candidate_methods[0]):
        raise ValueError("Candidate changed the target method signature or decorators")
    return candidate


def atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".rag.tmp")
    temporary.write_text(text, encoding="utf-8", newline="")
    temporary.replace(path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def restore_from_artifact(repository: Path, artifact_path: Path) -> int:
    payload = retrieve.load_json(artifact_path)
    originals = payload.get("original_files")
    final_hashes = payload.get("final_file_hashes")
    if payload.get("status") != "completed" or not isinstance(originals, dict) or not isinstance(final_hashes, dict):
        raise ValueError("Artifact does not describe a completed, restorable generation run")
    resolved_repository = repository.resolve()
    resolved_paths = {}
    for relative, original in originals.items():
        if not isinstance(relative, str) or not isinstance(original, str) or relative not in final_hashes:
            raise ValueError("Artifact contains invalid original-file data")
        path = (resolved_repository / relative).resolve()
        try:
            path.relative_to(resolved_repository)
        except ValueError as error:
            raise ValueError(f"Artifact restore path escapes repository: {relative}") from error
        if not path.is_file() or sha256_text(path.read_text(encoding="utf-8")) != final_hashes[relative]:
            raise ValueError(f"Refusing restore because generated file changed afterward: {relative}")
        resolved_paths[path] = original
    for path, original in resolved_paths.items():
        atomic_write_text(path, original)
    payload["status"] = "restored"
    atomic_write_json(artifact_path, payload)
    return len(resolved_paths)


def run_tests(repository: Path, python: str) -> dict[str, Any]:
    project = repository / "playground"
    completed = subprocess.run(
        [python, "-m", "unittest", "discover", "-s", "tests"],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    ran = re.search(r"Ran (\d+) tests", output)
    failures = re.search(r"failures=(\d+)", output)
    errors = re.search(r"errors=(\d+)", output)
    return {
        "command": [python, "-m", "unittest", "discover", "-s", "tests"],
        "exit_code": completed.returncode,
        "tests_run": int(ran.group(1)) if ran else None,
        "failures": int(failures.group(1)) if failures else 0,
        "errors": int(errors.group(1)) if errors else 0,
        "output_tail": "\n".join(output.splitlines()[-80:]),
    }


def validate_preflight(repository: Path, targets: list[Target]) -> dict[str, LocatedMethod]:
    located = {}
    for target in targets:
        item = locate_method(repository, target)
        if not is_pass_stub(item.method_node):
            raise ValueError(f"Target is not an unimplemented pass stub: {target.file}:{target.key}")
        located[f"{target.file}:{target.key}"] = item
    return located


def generated_body_fingerprint(body: str) -> str:
    validated = parse_generated_body(json.dumps({"body": body}))
    wrapper = ast.parse("def _generated():\n" + textwrap.indent(validated, "    "))
    return ast.dump(ast.Module(body=wrapper.body[0].body, type_ignores=[]), include_attributes=False)


def current_body_fingerprint(method: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return ast.dump(ast.Module(body=method.body, type_ignores=[]), include_attributes=False)


def prepare_repair(
    repository: Path,
    artifact_path: Path,
    repair_key: str,
) -> dict[str, Any]:
    artifact = retrieve.load_json(artifact_path)
    if artifact.get("status") != "completed":
        raise ValueError("Original generation artifact must have completed status")
    records = [
        record
        for record in artifact.get("tasks", [])
        if f"{record.get('class')}.{record.get('method')}" == repair_key
    ]
    if len(records) != 1:
        raise ValueError(f"Expected one generated method record for repair target {repair_key}")
    record = records[0]
    target = Target(record["file"], record["class"], record["method"], record["task_text"])
    final_hashes = artifact.get("final_file_hashes")
    if not isinstance(final_hashes, dict):
        raise ValueError("Original artifact has no final_file_hashes")
    for relative, expected_hash in final_hashes.items():
        path = (repository / relative).resolve()
        try:
            path.relative_to(repository.resolve())
        except ValueError as error:
            raise ValueError(f"Artifact path escapes repository: {relative}") from error
        if not path.is_file() or sha256_text(path.read_text(encoding="utf-8")) != expected_hash:
            raise ValueError(f"Current source does not match original artifact hash: {relative}")
    located = locate_method(repository, target)
    if current_body_fingerprint(located.method_node) != generated_body_fingerprint(record["generated_body"]):
        raise ValueError(f"Current method body does not match original artifact: {repair_key}")
    return {
        "artifact": artifact,
        "artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        "record": record,
        "target": target,
        "located": located,
        "dependencies": repair_dependency_context(repository),
    }


def run_focused_pricing_tests(repository: Path, python: str) -> dict[str, Any]:
    project = repository / "playground"
    command = [python, "-m", "unittest", "tests.test_pricing"]
    completed = subprocess.run(command, cwd=project, text=True, capture_output=True, check=False)
    output = completed.stdout + completed.stderr
    ran = re.search(r"Ran (\d+) tests", output)
    failures = re.search(r"failures=(\d+)", output)
    errors = re.search(r"errors=(\d+)", output)
    return {
        "command": command,
        "exit_code": completed.returncode,
        "tests_run": int(ran.group(1)) if ran else None,
        "failures": int(failures.group(1)) if failures else 0,
        "errors": int(errors.group(1)) if errors else 0,
        "output_tail": "\n".join(output.splitlines()[-80:]),
    }


def execute_repair(args: argparse.Namespace, client: Any, encoding: Any) -> dict[str, Any]:
    repository = args.repository.resolve()
    prepared = prepare_repair(repository, args.artifact, args.repair)
    target: Target = prepared["target"]
    located: LocatedMethod = prepared["located"]
    original_source = located.source
    original_artifact_hash = prepared["artifact_sha256"]
    embeddings_hash = hashlib.sha256(args.embeddings.read_bytes()).hexdigest()
    index = retrieve.load_index(args.chunks, args.embeddings)
    context = target_context(located)
    baseline_focused = run_focused_pricing_tests(repository, args.python)
    baseline_full = run_tests(repository, args.python)
    repair_artifact: dict[str, Any] = {
        "artifact_version": ARTIFACT_VERSION,
        "artifact_type": "targeted_repair",
        "status": "running",
        "generation_model": GENERATION_MODEL,
        "embedding_model": index["model"],
        "top_n": TOP_N,
        "repair_target": target.key,
        "original_generation_artifact": args.artifact.name,
        "original_generation_artifact_sha256": original_artifact_hash,
        "embeddings_sha256": embeddings_hash,
        "exception_context": args.repair_error,
        "previous_implementation": prepared["record"]["generated_body"],
        "new_implementation": None,
        "dependency_context": prepared["dependencies"],
        "retrieved_chunks": [],
        "response_id": None,
        "response_model": None,
        "usage": None,
        "baseline_focused_tests": baseline_focused,
        "baseline_full_tests": baseline_full,
        "final_focused_tests": None,
        "final_full_tests": None,
        "original_files": {target.file: original_source},
        "final_file_hashes": None,
    }
    atomic_write_json(args.repair_artifact, repair_artifact)
    try:
        query = task_query(target) + "\nRepair failure: " + args.repair_error
        query_embedding = retrieve.embed_query(client, query, index["dimension"], encoding)
        results = retrieve.retrieve(index, query_embedding, TOP_N, "all")
        prompt = build_repair_prompt(
            target,
            context,
            results,
            prepared["dependencies"],
            prepared["record"]["generated_body"],
            args.repair_error,
        )
        response = request_generation(client, prompt)
        body = parse_generated_body(response["output_text"])
        candidate = replace_method_body(located, target, body)
        atomic_write_text(located.path, candidate)

        # Every file from the original run except the selected target must remain byte-for-byte unchanged.
        for relative, expected_hash in prepared["artifact"]["final_file_hashes"].items():
            if relative == target.file:
                continue
            current = (repository / relative).read_text(encoding="utf-8")
            if sha256_text(current) != expected_hash:
                raise RuntimeError(f"Unrelated generated file changed during repair: {relative}")
        if hashlib.sha256(args.artifact.read_bytes()).hexdigest() != original_artifact_hash:
            raise RuntimeError("Original generation artifact changed during repair")
        if hashlib.sha256(args.embeddings.read_bytes()).hexdigest() != embeddings_hash:
            raise RuntimeError("Embedding snapshot changed during repair")

        repair_artifact.update({
            "new_implementation": body,
            "retrieved_chunks": [
                {
                    "chunk_id": result["chunk_id"],
                    "similarity": result["similarity"],
                    "file_path": result["file_path"],
                    "symbol": result["symbol"],
                    "category": result["category"],
                }
                for result in results
            ],
            "prompt_sha256": sha256_text(prompt),
            "response_id": response["response_id"],
            "response_model": response["response_model"],
            "usage": response["usage"],
            "final_file_hashes": {target.file: sha256_text(candidate)},
        })
        repair_artifact["final_focused_tests"] = run_focused_pricing_tests(repository, args.python)
        repair_artifact["final_full_tests"] = run_tests(repository, args.python)
        focused = repair_artifact["final_focused_tests"]
        full = repair_artifact["final_full_tests"]
        if focused["exit_code"] != 0 or full["exit_code"] != 0:
            raise RuntimeError(
                "Generated repair did not pass verification: "
                f"focused failures={focused['failures']} errors={focused['errors']}; "
                f"full failures={full['failures']} errors={full['errors']}"
            )
        repair_artifact["status"] = "completed"
        atomic_write_json(args.repair_artifact, repair_artifact)
        return repair_artifact
    except Exception as error:
        atomic_write_text(located.path, original_source)
        repair_artifact["status"] = "failed_and_rolled_back"
        repair_artifact["error"] = f"{type(error).__name__}: {error}"
        atomic_write_json(args.repair_artifact, repair_artifact)
        raise


def execute(args: argparse.Namespace, client: Any, encoding: Any) -> dict[str, Any]:
    repository = args.repository.resolve()
    targets = select_targets(load_tasks(args.tasks), args.only, args.task_text)
    preflight = validate_preflight(repository, targets)
    index = retrieve.load_index(args.chunks, args.embeddings)
    original_sources = {str(item.path): item.source for item in preflight.values()}
    original_sources = dict(original_sources)  # Deduplicate files shared by targets.
    expected_sources = dict(original_sources)
    embeddings_hash_before = hashlib.sha256(args.embeddings.read_bytes()).hexdigest()
    artifact: dict[str, Any] = {
        "artifact_version": ARTIFACT_VERSION,
        "status": "running",
        "generation_model": GENERATION_MODEL,
        "embedding_model": index["model"],
        "top_n": TOP_N,
        "embeddings_sha256": embeddings_hash_before,
        "baseline_tests": run_tests(repository, args.python),
        "final_tests": None,
        "original_files": {
            Path(path).relative_to(repository).as_posix(): source
            for path, source in original_sources.items()
        },
        "final_file_hashes": None,
        "tasks": [],
    }
    atomic_write_json(args.artifact, artifact)

    try:
        for target in targets:
            located = locate_method(repository, target)
            if not is_pass_stub(located.method_node):
                raise ValueError(f"Target changed before generation: {target.file}:{target.key}")
            context = target_context(located)
            query = task_query(target)
            query_embedding = retrieve.embed_query(client, query, index["dimension"], encoding)
            results = retrieve.retrieve(index, query_embedding, TOP_N, "all")
            prompt = build_prompt(target, context, results)
            response = request_generation(client, prompt)
            body = parse_generated_body(response["output_text"])
            candidate = replace_method_body(located, target, body)
            atomic_write_text(located.path, candidate)
            expected_sources[str(located.path)] = candidate
            record = {
                "file": target.file,
                "class": target.class_name,
                "method": target.method,
                "task_text": target.task_text,
                "target_signature": context["signature"],
                "target_context_lines": [context["start_line"], context["end_line"]],
                "original_method_source": context["method_source"],
                "generated_body": body,
                "retrieved_chunks": [
                    {
                        "chunk_id": result["chunk_id"],
                        "similarity": result["similarity"],
                        "file_path": result["file_path"],
                        "symbol": result["symbol"],
                        "category": result["category"],
                    }
                    for result in results
                ],
                "prompt_sha256": sha256_text(prompt),
                "response_id": response["response_id"],
                "response_model": response["response_model"],
                "usage": response["usage"],
                "file_sha256_after": sha256_text(candidate),
                "status": "written_after_syntax_validation",
            }
            artifact["tasks"].append(record)
            atomic_write_json(args.artifact, artifact)

        for path, expected in expected_sources.items():
            if Path(path).read_text(encoding="utf-8") != expected:
                raise RuntimeError(f"Unexpected source modification detected: {path}")
        if hashlib.sha256(args.embeddings.read_bytes()).hexdigest() != embeddings_hash_before:
            raise RuntimeError("Embedding snapshot changed during generation")
        artifact["final_tests"] = run_tests(repository, args.python)
        artifact["final_file_hashes"] = {
            Path(path).relative_to(repository).as_posix(): sha256_text(expected)
            for path, expected in expected_sources.items()
        }
        artifact["status"] = "completed"
        atomic_write_json(args.artifact, artifact)
        return artifact
    except Exception as error:
        for path, source in original_sources.items():
            atomic_write_text(Path(path), source)
        artifact["status"] = "failed_and_rolled_back"
        artifact["error"] = f"{type(error).__name__}: {error}"
        atomic_write_json(args.artifact, artifact)
        raise


def parse_args() -> argparse.Namespace:
    rag = Path(__file__).resolve().parent
    implementation = rag.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=implementation / "AI4SE_Playground")
    parser.add_argument("--tasks", type=Path, default=implementation / "Assignments" / "missing_code.json")
    parser.add_argument("--chunks", type=Path, default=rag / "chunks.json")
    parser.add_argument("--embeddings", type=Path, default=rag / "embeddings.json")
    parser.add_argument("--artifact", type=Path, default=rag / "generation_results.json")
    parser.add_argument("--repair", metavar="CLASS.METHOD", help="Repair one method from --artifact")
    parser.add_argument(
        "--repair-artifact",
        type=Path,
        default=rag / "repair_results.json",
        help="Separate provenance artifact for a targeted repair",
    )
    parser.add_argument(
        "--repair-error",
        help="Observed exception or failure context supplied to targeted repair",
    )
    parser.add_argument("--python", default=sys.executable, help="Python executable used for baseline/final tests")
    parser.add_argument("--only", action="append", default=[], metavar="CLASS.METHOD")
    parser.add_argument("--task-text", help="Override task text when exactly one --only target is selected")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate stores and confirm selected targets are pass stubs without API calls or writes",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore files from a completed artifact if they have not changed afterward",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.restore:
            count = restore_from_artifact(args.repository.resolve(), args.artifact)
            print(f"Restored {count} generated source files from {args.artifact.resolve()}.")
            return
        if args.repair:
            if args.only or args.task_text:
                raise ValueError("--repair cannot be combined with --only or --task-text")
            if not args.repair_error or not args.repair_error.strip():
                raise ValueError("--repair requires nonempty --repair-error context")
            prepared = prepare_repair(args.repository.resolve(), args.artifact, args.repair)
            index = retrieve.load_index(args.chunks, args.embeddings)
            if args.check:
                print(
                    f"Repair preflight passed: {prepared['target'].key}, "
                    f"original artifact and {len(index['entries'])} embeddings verified, "
                    f"dependencies={', '.join(prepared['dependencies'])}."
                )
                return
            if not os.environ.get("OPENAI_API_KEY", "").strip():
                raise ValueError("OPENAI_API_KEY is not set; no repair or source modification occurred")
            try:
                import tiktoken
                from openai import OpenAI
            except ImportError as error:
                raise ValueError("Missing dependency: install requirements from rag/requirements.txt") from error
            result = execute_repair(args, OpenAI(), tiktoken.get_encoding(retrieve.TOKENIZER))
            print(
                f"Repaired {result['repair_target']} with {GENERATION_MODEL}; "
                f"focused tests: {result['final_focused_tests']['tests_run']} run, "
                f"full tests: {result['final_full_tests']['tests_run']} run, "
                f"{result['final_full_tests']['failures']} failures, "
                f"{result['final_full_tests']['errors']} errors."
            )
            print(f"Repair artifact: {args.repair_artifact.resolve()}")
            return
        targets = select_targets(load_tasks(args.tasks), args.only, args.task_text)
        validate_preflight(args.repository.resolve(), targets)
        index = retrieve.load_index(args.chunks, args.embeddings)
        if args.check:
            print(
                f"Preflight passed: {len(targets)} pass stubs, "
                f"{len(index['entries'])} embeddings, dimension {index['dimension']}."
            )
            return
        if not os.environ.get("OPENAI_API_KEY", "").strip():
            raise ValueError("OPENAI_API_KEY is not set; no generation or source modification occurred")
        try:
            import tiktoken
            from openai import OpenAI
        except ImportError as error:
            raise ValueError("Missing dependency: install requirements from rag/requirements.txt") from error
        result = execute(args, OpenAI(), tiktoken.get_encoding(retrieve.TOKENIZER))
        print(
            f"Generated {len(result['tasks'])} methods with {GENERATION_MODEL}; "
            f"final tests: {result['final_tests']['tests_run']} run, "
            f"{result['final_tests']['failures']} failures, {result['final_tests']['errors']} errors."
        )
        print(f"Artifact: {args.artifact.resolve()}")
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
