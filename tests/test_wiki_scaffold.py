import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WikiScaffoldTest(unittest.TestCase):
    def test_required_directories_exist(self):
        required_dirs = [
            "raw/inbox",
            "raw/sources",
            "raw/assets",
            "wiki/sources",
            "wiki/entities",
            "wiki/concepts",
            "wiki/analyses",
            "wiki/operations",
            "outputs/reports",
            "outputs/decks",
            "outputs/exports",
            "logs",
        ]
        for relative in required_dirs:
            self.assertTrue((ROOT / relative).is_dir(), relative)

    def test_core_wiki_pages_exist(self):
        required_files = [
            "wiki/index.md",
            "wiki/log.md",
            "wiki/overview.md",
            "wiki/operations/project-intake.md",
            "wiki/operations/project-status.md",
            "wiki/operations/next-steps.md",
        ]
        for relative in required_files:
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
