import pathlib
import tempfile
import unittest

from tools.common import (
    extract_wiki_links,
    iter_markdown_files,
    load_frontmatter,
    page_slug,
)


class CommonToolsTest(unittest.TestCase):
    def test_load_frontmatter_reads_scalar_and_list_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "page.md"
            path.write_text(
                "---\n"
                "title: Example\n"
                "type: concept\n"
                "links: [overview, entity-a]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Page\n",
                encoding="utf-8",
            )
            data = load_frontmatter(path)
            self.assertEqual(data["title"], "Example")
            self.assertEqual(data["type"], "concept")
            self.assertEqual(data["links"], ["overview", "entity-a"])

    def test_load_frontmatter_keeps_empty_scalar_as_empty_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "page.md"
            path.write_text(
                "---\n"
                "title: \n"
                "links: []\n"
                "---\n",
                encoding="utf-8",
            )
            data = load_frontmatter(path)
            self.assertEqual(data["title"], "")
            self.assertEqual(data["links"], [])

    def test_load_frontmatter_reads_multiline_dash_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "page.md"
            path.write_text(
                "---\n"
                "title: Example\n"
                "links:\n"
                "  - concepts/topic\n"
                "  - sources/article\n"
                "---\n",
                encoding="utf-8",
            )
            data = load_frontmatter(path)
            self.assertEqual(data["title"], "Example")
            self.assertEqual(data["links"], ["concepts/topic", "sources/article"])

    def test_load_frontmatter_does_not_drop_multiline_list_items_before_next_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "page.md"
            path.write_text(
                "---\n"
                "links:\n"
                "  - overview\n"
                "  - entity-a\n"
                "type: concept\n"
                "---\n",
                encoding="utf-8",
            )
            data = load_frontmatter(path)
            self.assertEqual(data["links"], ["overview", "entity-a"])
            self.assertEqual(data["type"], "concept")

    def test_extract_wiki_links_finds_double_bracket_links(self):
        text = "See [[overview]] and [[concept-a|Concept A]]."
        self.assertEqual(extract_wiki_links(text), {"overview", "concept-a"})

    def test_iter_markdown_files_returns_sorted_visible_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "b.md").write_text("b", encoding="utf-8")
            (root / "a.md").write_text("a", encoding="utf-8")
            (root / ".hidden.md").write_text("hidden", encoding="utf-8")
            nested = root / "wiki"
            nested.mkdir()
            (nested / "c.md").write_text("c", encoding="utf-8")

            files = list(iter_markdown_files(root))

            self.assertEqual(
                [path.name for path in files],
                ["a.md", "b.md", "c.md"],
            )

    def test_page_slug_maps_special_pages_and_nested_paths(self):
        wiki_root = pathlib.Path("/tmp/wiki")

        self.assertEqual(page_slug(wiki_root / "index.md", wiki_root), "index")
        self.assertEqual(page_slug(wiki_root / "overview.md", wiki_root), "overview")
        self.assertEqual(
            page_slug(wiki_root / "concepts" / "topic.md", wiki_root),
            "concepts/topic",
        )
        self.assertEqual(
            page_slug(wiki_root / "concepts" / "index.md", wiki_root),
            "concepts/index",
        )
        self.assertEqual(
            page_slug(wiki_root / "sources" / "overview.md", wiki_root),
            "sources/overview",
        )


if __name__ == "__main__":
    unittest.main()
