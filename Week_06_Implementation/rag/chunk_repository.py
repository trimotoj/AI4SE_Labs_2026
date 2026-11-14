"""Create semantic JSON chunks from a Python repository using the standard AST."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MAX_LINES = 120
DEFINITION_NODES = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def node_start(node: ast.AST) -> int:
    """Return the first source line, including decorators."""
    decorators = getattr(node, "decorator_list", [])
    return min([node.lineno, *(item.lineno for item in decorators)])


def node_kind(node: ast.AST) -> str:
    if isinstance(node, ast.ClassDef):
        return "class"
    if isinstance(node, ast.AsyncFunctionDef):
        return "async_function"
    if isinstance(node, ast.FunctionDef):
        return "function"
    return "module_context"


def line_windows(start: int, end: int, max_lines: int) -> Iterable[tuple[int, int]]:
    current = start
    while current <= end:
        window_end = min(current + max_lines - 1, end)
        yield current, window_end
        current = window_end + 1


def class_signature(lines: list[str], node: ast.ClassDef) -> str:
    """Keep the class declaration as useful context on split class chunks."""
    header_end = node.body[0].lineno - 1 if node.body else node.end_lineno
    return "\n".join(lines[node_start(node) - 1 : header_end]).rstrip()


def semantic_regions(tree: ast.Module, lines: list[str], max_lines: int) -> list[dict[str, Any]]:
    """Return AST-aware regions, splitting only structures over max_lines."""
    regions: list[dict[str, Any]] = []
    definitions = [node for node in tree.body if isinstance(node, DEFINITION_NODES)]
    first_definition = min((node_start(node) for node in definitions), default=len(lines) + 1)

    if first_definition > 1 and any(line.strip() for line in lines[: first_definition - 1]):
        for part, (start, end) in enumerate(
            line_windows(1, first_definition - 1, max_lines), start=1
        ):
            regions.append({
                "kind": "module_context",
                "symbol": "<module>",
                "start": start,
                "end": end,
                "part": part,
                "part_count": None,
            })

    for node in definitions:
        start, end = node_start(node), node.end_lineno
        if end - start + 1 <= max_lines:
            regions.append({
                "kind": node_kind(node),
                "symbol": node.name,
                "start": start,
                "end": end,
            })
            continue

        if isinstance(node, ast.ClassDef):
            members = [item for item in node.body if isinstance(item, DEFINITION_NODES)]
            signature = class_signature(lines, node)
            first_member = node_start(members[0]) if members else end + 1
            if first_member > start:
                regions.append({
                    "kind": "class_context",
                    "symbol": node.name,
                    "class_name": node.name,
                    "class_signature": signature,
                    "start": start,
                    "end": first_member - 1,
                })

            group: list[ast.AST] = []
            for member in members:
                member_start, member_end = node_start(member), member.end_lineno
                if member_end - member_start + 1 > max_lines:
                    if group:
                        regions.append(member_group(node.name, signature, group))
                        group = []
                    windows = list(line_windows(member_start, member_end, max_lines))
                    for part, (window_start, window_end) in enumerate(windows, start=1):
                        regions.append({
                            "kind": "class_member",
                            "symbol": f"{node.name}.{member.name}",
                            "class_name": node.name,
                            "member_names": [member.name],
                            "class_signature": signature,
                            "start": window_start,
                            "end": window_end,
                            "part": part,
                            "part_count": len(windows),
                        })
                elif group and member_end - node_start(group[0]) + 1 > max_lines:
                    regions.append(member_group(node.name, signature, group))
                    group = [member]
                else:
                    group.append(member)
            if group:
                regions.append(member_group(node.name, signature, group))
        else:
            windows = list(line_windows(start, end, max_lines))
            for part, (window_start, window_end) in enumerate(windows, start=1):
                regions.append({
                    "kind": node_kind(node),
                    "symbol": node.name,
                    "start": window_start,
                    "end": window_end,
                    "part": part,
                    "part_count": len(windows),
                })

    return regions


def member_group(class_name: str, signature: str, members: list[ast.AST]) -> dict[str, Any]:
    names = [member.name for member in members]
    return {
        "kind": "class_members",
        "symbol": f"{class_name}.{'_to_'.join(names)}",
        "class_name": class_name,
        "member_names": names,
        "class_signature": signature,
        "start": node_start(members[0]),
        "end": members[-1].end_lineno,
    }


def chunk_file(path: Path, repository: Path, max_lines: int) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines()
    relative_path = path.relative_to(repository).as_posix()
    category = "test" if "tests" in path.relative_to(repository).parts else "source"
    chunks = []

    for index, region in enumerate(semantic_regions(tree, lines, max_lines), start=1):
        start, end = region.pop("start"), region.pop("end")
        code = "\n".join(lines[start - 1 : end])
        identity = f"{relative_path}:{start}:{end}:{region['kind']}"
        chunks.append({
            "id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
            "file_path": relative_path,
            "category": category,
            "chunk_index": index,
            "kind": region.pop("kind"),
            "symbol": region.pop("symbol"),
            "start_line": start,
            "end_line": end,
            "line_count": end - start + 1,
            **region,
            "source_code": code,
        })
    return chunks


def build_chunks(repository: Path, max_lines: int) -> tuple[list[dict[str, Any]], list[str]]:
    files = sorted(path for path in repository.rglob("*.py") if path.is_file())
    chunks: list[dict[str, Any]] = []
    processed: list[str] = []
    for path in files:
        chunks.extend(chunk_file(path, repository, max_lines))
        processed.append(path.relative_to(repository).as_posix())
    return chunks, processed


def parse_args() -> argparse.Namespace:
    implementation_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=implementation_root / "AI4SE_Playground",
        help="Python repository to chunk",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "chunks.json",
        help="Destination JSON file",
    )
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = args.repository.resolve()
    if not repository.is_dir():
        raise SystemExit(f"Repository does not exist: {repository}")
    if args.max_lines < 1:
        raise SystemExit("--max-lines must be a positive integer")

    chunks, files = build_chunks(repository, args.max_lines)
    payload = {
        "schema_version": 1,
        "repository": repository.name,
        "strategy": "Python AST semantic chunks with bounded line windows",
        "max_lines": args.max_lines,
        "includes_tests": True,
        "file_count": len(files),
        "chunk_count": len(chunks),
        "files": files,
        "chunks": chunks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Processed {len(files)} Python files and generated {len(chunks)} chunks.")
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
