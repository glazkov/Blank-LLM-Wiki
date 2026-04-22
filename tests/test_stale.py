import pathlib
import tempfile
import unittest

from tools.check_stale import find_stale_issues


class StaleCheckTest(unittest.TestCase):
    def test_reports_stable_page_without_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            page = wiki / "concepts/idea.md"
            page.write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: stable\n"
                "updated: 2025-01-01\n"
                "summary: Stable page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            issues = find_stale_issues(root, today="2026-04-22")
            self.assertTrue(any("missing source_refs" in issue for issue in issues))

    def test_reports_invalid_updated_value_as_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            page = wiki / "concepts/idea.md"
            page.write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: stable\n"
                "updated: not-a-date\n"
                "summary: Stable page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            issues = find_stale_issues(root, today="2026-04-22")
            self.assertTrue(any("invalid updated date" in issue for issue in issues))

    def test_reports_stale_page_older_than_180_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            page = wiki / "concepts/idea.md"
            page.write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2025-01-01\n"
                "summary: Draft page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            issues = find_stale_issues(root, today="2026-04-22")
            self.assertTrue(any("is stale:" in issue for issue in issues))

    def test_reports_non_list_source_refs_as_invalid_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            page = wiki / "concepts/idea.md"
            page.write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: stable\n"
                "updated: 2026-04-22\n"
                "summary: Stable page.\n"
                "links: []\n"
                "source_refs: sources/source-a\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            issues = find_stale_issues(root, today="2026-04-22")
            self.assertIn(
                "wiki/concepts/idea.md field source_refs must be a list",
                issues,
            )


if __name__ == "__main__":
    unittest.main()
