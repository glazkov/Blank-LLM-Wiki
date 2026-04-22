from __future__ import annotations

import datetime as dt
import pathlib
import sys
from typing import List

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.common import iter_markdown_files, load_frontmatter


def find_stale_issues(root: pathlib.Path, today: str | None = None) -> List[str]:
    wiki_root = root / "wiki"
    now = dt.date.fromisoformat(today) if today else dt.date.today()
    issues: List[str] = []
    for path in iter_markdown_files(wiki_root):
        if path.name in {"index.md", "log.md"}:
            continue
        data = load_frontmatter(path)
        if not data:
            continue
        status = data.get("status")
        updated = data.get("updated")
        source_refs = data.get("source_refs", [])
        if "source_refs" in data and not isinstance(source_refs, list):
            issues.append(f"{path.relative_to(root)} field source_refs must be a list")
            source_refs = []
        if status == "stable" and not source_refs:
            issues.append(f"{path.relative_to(root)} missing source_refs for stable page")
        if isinstance(updated, str):
            try:
                age = (now - dt.date.fromisoformat(updated)).days
            except ValueError:
                issues.append(f"{path.relative_to(root)} has invalid updated date: {updated}")
            else:
                if age > 180:
                    issues.append(f"{path.relative_to(root)} is stale: {age} days since update")
    return issues


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    issues = find_stale_issues(root)
    if issues:
        for issue in issues:
            print(f"STALE: {issue}")
        return 1
    print("OK: no stale page issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
