from __future__ import annotations

import pathlib
import sys
from collections import Counter
from typing import List

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.common import extract_wiki_links, iter_markdown_files, load_frontmatter, page_slug


def find_orphans(root: pathlib.Path) -> List[str]:
    wiki_root = root / "wiki"
    pages = [path for path in iter_markdown_files(wiki_root) if path.name not in {"index.md", "log.md"}]
    inbound = Counter()
    slugs = {page_slug(path, wiki_root) for path in pages}
    for path in pages:
        current_slug = page_slug(path, wiki_root)
        text = path.read_text(encoding="utf-8")
        for link in extract_wiki_links(text):
            if link in slugs and link != current_slug:
                inbound[link] += 1
        data = load_frontmatter(path)
        for field in ("links", "source_refs"):
            refs = data.get(field)
            if not isinstance(refs, list):
                continue
            for link in refs:
                if link in slugs and link != current_slug:
                    inbound[link] += 1
    return sorted(slug for slug in slugs if slug != "overview" and inbound[slug] == 0)


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    orphans = find_orphans(root)
    if orphans:
        for orphan in orphans:
            print(f"ORPHAN: {orphan}")
        return 1
    print("OK: no orphan pages found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
