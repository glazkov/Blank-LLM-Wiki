import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RootScaffoldTest(unittest.TestCase):
    def test_required_root_files_exist(self):
        required = [
            ROOT / "LLM Wiki.md",
            ROOT / "README.md",
            ROOT / ".gitignore",
        ]
        missing = [str(path.name) for path in required if not path.exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
