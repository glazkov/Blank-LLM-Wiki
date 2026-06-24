import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RootScaffoldTest(unittest.TestCase):
    def test_required_root_files_exist(self):
        required = [
            ROOT / "LLM Wiki.md",
            ROOT / "README.md",
            ROOT / ".gitignore",
            ROOT / "public-docs-manifest.json",
            ROOT / "public-docs" / "pages" / "index.md",
            ROOT / "public-docs" / "mkdocs.yml",
            ROOT / "public-docs" / "requirements.txt",
            ROOT / "public-docs" / "tools" / "build_public_docs.py",
            ROOT / "public-docs" / "tools" / "validate_public_docs.py",
            ROOT / ".codex" / "skills" / "llm-wiki-public" / "SKILL.md",
        ]
        missing = [str(path.name) for path in required if not path.exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
