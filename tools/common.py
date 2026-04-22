from __future__ import annotations

import pathlib
import re
from typing import Dict, Iterable, Set


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def load_frontmatter(path: pathlib.Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    result: Dict[str, object] = {}
    current_list_key: str | None = None
    for raw_line in match.group(1).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        if current_list_key and stripped.startswith("- "):
            value = _parse_value(stripped[2:].strip())
            existing = result.get(current_list_key)
            if not isinstance(existing, list):
                existing = []
                result[current_list_key] = existing
            existing.append(value)
            continue

        current_list_key = None
        if ":" not in raw_line:
            continue

        key, value = raw_line.split(":", 1)
        parsed_value = _parse_value(value.strip())
        result[key.strip()] = parsed_value
        if value.strip() == "":
            result[key.strip()] = ""
            current_list_key = key.strip()
    return result


def extract_wiki_links(text: str) -> Set[str]:
    return {match.group(1).strip() for match in WIKI_LINK_RE.finditer(text)}


def iter_markdown_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    for path in sorted(root.rglob("*.md")):
        if path.name.startswith("."):
            continue
        yield path


def page_slug(path: pathlib.Path, wiki_root: pathlib.Path) -> str:
    relative = path.relative_to(wiki_root).with_suffix("")
    if len(relative.parts) == 1 and relative.name == "index":
        return "index"
    if len(relative.parts) == 1 and relative.name == "overview":
        return "overview"
    return str(relative).replace("\\", "/")


def _parse_value(value: str) -> object:
    if value == "":
        return ""
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    return value.strip("'\"")
