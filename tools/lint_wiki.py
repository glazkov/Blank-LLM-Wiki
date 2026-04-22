from __future__ import annotations

import pathlib
import re
import sys
from typing import List

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.common import extract_wiki_links, iter_markdown_files, load_frontmatter, page_slug


REQUIRED_DIRS = [
    "wiki/sources",
    "wiki/entities",
    "wiki/concepts",
    "wiki/analyses",
    "wiki/operations",
]
REQUIRED_FILES = [
    "wiki/index.md",
    "wiki/log.md",
    "wiki/operations/project-intake.md",
    "wiki/operations/project-status.md",
    "wiki/operations/next-steps.md",
]
REQUIRED_FIELDS = ["title", "type", "status", "updated", "summary", "links", "source_refs"]
STRING_FIELDS = ["title", "type", "status", "updated", "summary"]
LIST_FIELDS = ["links", "source_refs"]
TYPE_BY_DIR = {
    "sources": "source",
    "entities": "entity",
    "concepts": "concept",
    "analyses": "analysis",
    "operations": "operation",
}
LOG_HEADING_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (bootstrap|ingest|query|lint|synthesis) \| .+$", re.MULTILINE)


def run_structural_lint(root: pathlib.Path) -> List[str]:
    issues: List[str] = []
    wiki_root = root / "wiki"
    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            issues.append(f"missing required directory: {relative}")

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(f"missing required file: {relative}")

    index_path = wiki_root / "index.md"
    log_path = wiki_root / "log.md"
    if log_path.is_file():
        log_text = log_path.read_text(encoding="utf-8")
        valid_heading_found = False
        for line in log_text.splitlines():
            if not line.startswith("## "):
                continue
            if LOG_HEADING_RE.fullmatch(line):
                valid_heading_found = True
            else:
                issues.append(f"wiki/log.md has invalid log heading: {line}")
        if not valid_heading_found:
            issues.append("wiki/log.md has no valid log headings")

    known_slugs = {page_slug(path, wiki_root) for path in iter_markdown_files(wiki_root)}
    index_links = extract_wiki_links(index_path.read_text(encoding="utf-8")) if index_path.exists() else set()

    for path in iter_markdown_files(wiki_root):
        if path.name in {"index.md", "log.md"}:
            continue
        data = load_frontmatter(path)
        if not data:
            issues.append(f"{path.relative_to(root)} missing frontmatter")
            continue
        for field in REQUIRED_FIELDS:
            if field not in data:
                issues.append(f"{path.relative_to(root)} missing field: {field}")
        for field in STRING_FIELDS:
            if field in data and not isinstance(data.get(field), str):
                issues.append(f"{path.relative_to(root)} field {field} must be a string")
        for field in LIST_FIELDS:
            if field in data and not isinstance(data.get(field), list):
                issues.append(f"{path.relative_to(root)} field {field} must be a list")
        parent = path.parent.name
        expected_type = TYPE_BY_DIR.get(parent)
        if expected_type and data.get("type") != expected_type:
            issues.append(f"{path.relative_to(root)} has wrong type: {data.get('type')}")
        text = path.read_text(encoding="utf-8")
        if page_slug(path, wiki_root) == "operations/next-steps":
            if _next_step_requires_follow_up(text):
                issues.append(
                    "wiki/operations/next-steps.md requires a user question or concrete options when the next step is not defined"
                )
        if data.get("status") == "stable":
            for marker in ("TODO", "TBD", "FIXME"):
                if marker in text:
                    issues.append(f"{path.relative_to(root)} contains placeholder marker: {marker}")
        source_refs = data.get("source_refs")
        if isinstance(source_refs, list):
            for ref in source_refs:
                if not _source_ref_exists(root, known_slugs, ref):
                    issues.append(f"{path.relative_to(root)} has missing source_refs target: {ref}")
        for link in extract_wiki_links(text):
            if link not in known_slugs:
                issues.append(f"{path.relative_to(root)} links to missing page: {link}")
        if page_slug(path, wiki_root) not in {"overview"} and page_slug(path, wiki_root) not in index_links:
            issues.append(f"{path.relative_to(root)} not listed in wiki/index.md")

    return issues


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    issues = run_structural_lint(root)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    print("OK: wiki structure looks valid")
    return 0


def _source_ref_exists(root: pathlib.Path, known_slugs: set[str], ref: object) -> bool:
    if not isinstance(ref, str):
        return False
    if ref in known_slugs:
        return True
    if ref.startswith("raw/"):
        return (root / ref).exists()
    return False


def _next_step_requires_follow_up(text: str) -> bool:
    sections = _extract_h2_sections(text)
    next_step = sections.get("Ближайший шаг", "")
    user_question = sections.get("Что нужно уточнить у пользователя", "")
    options = sections.get("Варианты продолжения", "")

    if not _is_placeholder_or_empty(next_step):
        return False
    if not _is_placeholder_or_empty(user_question):
        return False
    if not _is_placeholder_or_empty(options):
        return False
    return True


def _extract_h2_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_heading: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(buffer).strip()
            current_heading = line[3:].strip()
            buffer = []
            continue
        if current_heading is not None:
            buffer.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(buffer).strip()
    return sections


def _is_placeholder_or_empty(value: str) -> bool:
    normalized = " ".join(value.split()).strip(" -.")
    if not normalized:
        return True
    placeholders = {
        "Пока не определен",
        "Пока не определено",
        "Пока не требуется",
        "Пока пусто",
        "Неизвестно",
    }
    return normalized in placeholders


if __name__ == "__main__":
    sys.exit(main())
