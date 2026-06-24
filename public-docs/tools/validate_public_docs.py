#!/usr/bin/env python3
"""Validate the public LLM Wiki documentation manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "public-docs-manifest.json"
BLOCKED_PREFIXES = ("raw/", "logs/", "outputs/")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_manifest() -> dict:
    if not MANIFEST.exists():
        fail("public-docs-manifest.json does not exist")
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"public-docs-manifest.json is invalid JSON: {exc}")


def validate_manifest(manifest: dict) -> None:
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        fail("manifest must contain a non-empty pages list")

    allow_operations = bool(manifest.get("allowOperations", False))
    seen_dest: set[str] = set()

    for index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            fail(f"pages[{index}] must be an object")
        source = page.get("source")
        dest = page.get("dest")
        if not isinstance(source, str) or not source:
            fail(f"pages[{index}].source must be a non-empty string")
        if not isinstance(dest, str) or not dest:
            fail(f"pages[{index}].dest must be a non-empty string")

        source_path = Path(source)
        dest_path = Path(dest)
        if source_path.is_absolute() or ".." in source_path.parts:
            fail(f"pages[{index}].source must stay inside project: {source}")
        if dest_path.is_absolute() or ".." in dest_path.parts:
            fail(f"pages[{index}].dest must stay inside public docs: {dest}")
        if dest in seen_dest:
            fail(f"duplicate public destination: {dest}")
        seen_dest.add(dest)

        normalized_source = source_path.as_posix()
        if normalized_source.startswith(BLOCKED_PREFIXES):
            fail(f"blocked source for public docs: {source}")
        if normalized_source.startswith("wiki/operations/") and not allow_operations:
            fail(f"operations pages are private by default: {source}")
        if not (ROOT / source_path).exists():
            fail(f"manifest source does not exist: {source}")
        if source_path.suffix.lower() == ".md" and dest_path.suffix.lower() != ".md":
            fail(f"markdown source must have markdown destination: {source} -> {dest}")


def main() -> None:
    validate_manifest(load_manifest())
    print("OK: public docs manifest looks valid")


if __name__ == "__main__":
    main()
