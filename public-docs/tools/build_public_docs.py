#!/usr/bin/env python3
"""Build MkDocs source files from a public allowlist of LLM Wiki pages."""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DOCS = ROOT / "public-docs"
DOCS = PUBLIC_DOCS / "build" / "docs"
ASSETS = PUBLIC_DOCS / "assets"
MANIFEST = ROOT / "public-docs-manifest.json"

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def page_title(path: str) -> str:
    return path.rstrip("/").split("/")[-1].replace("-", " ")


def normalize_wiki_target(target: str) -> str:
    target_path = Path(target.strip())
    if target_path.suffix != ".md":
        target_path = target_path.with_suffix(".md")
    if target_path.parts and target_path.parts[0] == "wiki":
        target_path = Path(*target_path.parts[1:])
    return (Path("wiki") / target_path).as_posix()


def markdown_target(current: Path, dest_rel: Path) -> str:
    source_dir = current.parent
    relative = Path(os.path.relpath(DOCS / dest_rel, source_dir))
    return relative.as_posix()


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("title: "):
            return line.removeprefix("title: ").strip().strip('"')
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).lstrip()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def convert_links(
    text: str,
    dest_file: Path,
    public_dest_by_source: dict[str, Path],
    titles: dict[str, str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        label = (match.group(2) or titles.get(normalize_wiki_target(target)) or page_title(target)).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            return f"[{label}]({target})"
        source_rel = normalize_wiki_target(target)
        if source_rel not in public_dest_by_source:
            return label
        return f"[{label}]({markdown_target(dest_file, public_dest_by_source[source_rel])})"

    return WIKILINK_RE.sub(replace, text)


def main() -> None:
    manifest = load_manifest()
    pages = manifest["pages"]
    public_dest_by_source = {
        page["source"]: Path(page["dest"])
        for page in pages
    }

    titles: dict[str, str] = {}
    for source_rel in public_dest_by_source:
        src = ROOT / source_rel
        if src.exists() and src.suffix.lower() == ".md":
            titles[source_rel] = extract_title(src.read_text(encoding="utf-8"), page_title(source_rel))

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    for page in pages:
        src = ROOT / page["source"]
        dest_rel = Path(page["dest"])
        dest = DOCS / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() == ".md":
            text = strip_frontmatter(src.read_text(encoding="utf-8"))
            dest.write_text(convert_links(text, dest, public_dest_by_source, titles), encoding="utf-8")
        else:
            shutil.copy2(src, dest)

    if ASSETS.exists():
        shutil.copytree(ASSETS, DOCS / "assets", dirs_exist_ok=True)

    print(f"Built public docs source: {DOCS}")


if __name__ == "__main__":
    main()
