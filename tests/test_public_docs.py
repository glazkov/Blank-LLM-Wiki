import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublicDocsTest(unittest.TestCase):
    def test_manifest_has_minimal_valid_shape(self):
        manifest = json.loads((ROOT / "public-docs-manifest.json").read_text(encoding="utf-8"))

        self.assertIn("site", manifest)
        self.assertEqual(
            manifest["pages"],
            [{"source": "wiki/overview.md", "dest": "index.md"}],
        )

    def test_validate_public_docs_passes(self):
        result = subprocess.run(
            ["python3", "public-docs/tools/validate_public_docs.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("OK: public docs manifest looks valid", result.stdout)

    def test_build_public_docs_source_converts_overview(self):
        subprocess.run(
            ["python3", "public-docs/tools/build_public_docs.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        index = ROOT / "public-docs" / "build" / "docs" / "index.md"
        self.assertTrue(index.is_file())
        text = index.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Обзор проекта"))
        self.assertNotIn("source_refs:", text)


if __name__ == "__main__":
    unittest.main()
