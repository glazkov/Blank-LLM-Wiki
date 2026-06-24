import json
import importlib.util
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "public-docs" / "tools" / "validate_public_docs.py"
spec = importlib.util.spec_from_file_location("validate_public_docs", VALIDATOR_PATH)
validate_public_docs = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validate_public_docs)


class PublicDocsTest(unittest.TestCase):
    def test_manifest_has_minimal_valid_shape(self):
        manifest = json.loads((ROOT / "public-docs-manifest.json").read_text(encoding="utf-8"))

        self.assertIn("site", manifest)
        self.assertEqual(
            manifest["pages"],
            [{"source": "public-docs/pages/index.md", "dest": "index.md"}],
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

    def test_build_public_docs_source_builds_public_index(self):
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
        self.assertTrue(text.startswith("# Шаблон проекта LLM Wiki"))
        self.assertNotIn("source_refs:", text)
        self.assertNotIn("wiki/operations", text)

        mkdocs = ROOT / "public-docs" / "build" / "mkdocs.yml"
        self.assertTrue(mkdocs.is_file())
        mkdocs_text = mkdocs.read_text(encoding="utf-8")
        self.assertIn("site_name: LLM Wiki Template", mkdocs_text)
        self.assertIn(
            "site_description: A project template for durable LLM-maintained knowledge bases",
            mkdocs_text,
        )
        self.assertIn("docs_dir: docs", mkdocs_text)
        self.assertIn("site_dir: site", mkdocs_text)

    def test_validate_public_docs_rejects_source_outside_project(self):
        manifest = {
            "site": {
                "name": "Public Documentation",
                "description": "Public documentation generated from selected LLM Wiki pages",
            },
            "pages": [
                {"source": "../outside.md", "dest": "index.md"},
            ],
        }

        with self.assertRaises(SystemExit):
            validate_public_docs.validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
