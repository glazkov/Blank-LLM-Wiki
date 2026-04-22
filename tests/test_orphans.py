import pathlib
import subprocess
import tempfile
import sys
import unittest

from tools.check_orphans import find_orphans


class OrphanCheckTest(unittest.TestCase):
    def test_reports_page_without_inbound_links(self):
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
                "updated: 2026-04-22\n"
                "summary: Test page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            self.assertIn("concepts/idea", find_orphans(root))

    def test_cli_runs_without_module_import_error(self):
        result = subprocess.run(
            [sys.executable, str(pathlib.Path(__file__).resolve().parents[1] / "tools/check_orphans.py")],
            cwd=pathlib.Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        self.assertNotIn("ModuleNotFoundError", result.stderr)

    def test_frontmatter_links_count_as_inbound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            (wiki / "concepts/source.md").write_text(
                "---\n"
                "title: Source\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Source page.\n"
                "links: [concepts/idea, concepts/missing]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Source\n",
                encoding="utf-8",
            )
            (wiki / "concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Target page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            self.assertNotIn("concepts/idea", find_orphans(root))

    def test_source_refs_count_as_inbound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            (wiki / "sources").mkdir(parents=True)
            (wiki / "concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Referrer page.\n"
                "links: []\n"
                "source_refs: [sources/source-a]\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )
            (wiki / "sources/source-a.md").write_text(
                "---\n"
                "title: Source A\n"
                "type: source\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Target source page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Source A\n",
                encoding="utf-8",
            )

            self.assertNotIn("sources/source-a", find_orphans(root))

    def test_self_links_do_not_count_as_inbound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            (wiki / "concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Self-linked page.\n"
                "links: [concepts/idea]\n"
                "source_refs: [concepts/idea]\n"
                "---\n"
                "\n"
                "# Idea\n"
                "[[concepts/idea]]\n",
                encoding="utf-8",
            )

            self.assertIn("concepts/idea", find_orphans(root))


if __name__ == "__main__":
    unittest.main()
