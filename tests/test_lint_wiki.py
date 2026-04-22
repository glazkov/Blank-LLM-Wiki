import pathlib
import tempfile
import unittest

from tools.lint_wiki import run_structural_lint


class StructuralLintTest(unittest.TestCase):
    def write_required_operation_files(self, root: pathlib.Path) -> None:
        (root / "wiki/operations/project-intake.md").write_text(
            "---\n"
            "title: Project Intake\n"
            "type: operation\n"
            "status: draft\n"
            "updated: 2026-04-22\n"
            "summary: Project intake.\n"
            "links: [overview, operations/project-status, operations/next-steps]\n"
            "source_refs: []\n"
            "---\n"
            "\n"
            "# Project Intake\n",
            encoding="utf-8",
        )
        (root / "wiki/operations/project-status.md").write_text(
            "---\n"
            "title: Project Status\n"
            "type: operation\n"
            "status: draft\n"
            "updated: 2026-04-22\n"
            "summary: Current project state.\n"
            "links: [operations/project-intake, operations/next-steps]\n"
            "source_refs: []\n"
            "---\n"
            "\n"
            "# Project Status\n"
            "\n"
            "## Архитектурные риски и пересмотр\n"
            "\n"
            "- Пока нет.\n",
            encoding="utf-8",
        )
        (root / "wiki/operations/next-steps.md").write_text(
            "---\n"
            "title: Next Steps\n"
            "type: operation\n"
            "status: draft\n"
            "updated: 2026-04-22\n"
            "summary: Next actions.\n"
            "links: [operations/project-intake, operations/project-status]\n"
            "source_refs: []\n"
            "---\n"
            "\n"
            "# Next Steps\n"
            "\n"
            "## Ближайший шаг\n"
            "\n"
            "- Continue setup.\n"
            "\n"
            "## Почему шаг пока не определен\n"
            "\n"
            "- Not applicable.\n"
            "\n"
            "## Что нужно уточнить у пользователя\n"
            "\n"
            "- Пока пусто.\n"
            "\n"
            "## Варианты продолжения\n"
            "\n"
            "- Continue setup.\n",
            encoding="utf-8",
        )

    def test_reports_missing_required_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wiki = root / "wiki"
            (wiki / "concepts").mkdir(parents=True)
            page = wiki / "concepts" / "idea.md"
            page.write_text("# Idea\n", encoding="utf-8")
            issues = run_structural_lint(root)
            self.assertTrue(any("missing frontmatter" in issue for issue in issues))

    def test_reports_invalid_log_heading_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            (root / "wiki/index.md").write_text("- [[concepts/idea]]: Test page.\n", encoding="utf-8")
            (root / "wiki/log.md").write_text(
                "## [2026-04-22] lint | Test\n"
                "## [2026-04-22] invalid | Bad\n",
                encoding="utf-8",
            )
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            page = root / "wiki/concepts/idea.md"
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
            issues = run_structural_lint(root)
            self.assertTrue(any("wiki/log.md" in issue for issue in issues))

    def test_does_not_use_substring_match_for_index_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            (root / "wiki/index.md").write_text("- [[concepts/idea2]]: Different page.\n", encoding="utf-8")
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            page = root / "wiki/concepts/idea.md"
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
            issues = run_structural_lint(root)
            self.assertTrue(any("not listed in wiki/index.md" in issue for issue in issues))

    def test_accepts_minimal_valid_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            page = root / "wiki/concepts/idea.md"
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
            issues = run_structural_lint(root)
            self.assertEqual(issues, [])

    def test_reports_missing_source_ref_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[sources/source-a]]: Source page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/sources/source-a.md").write_text(
                "---\n"
                "title: Source A\n"
                "type: source\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Source page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Source A\n",
                encoding="utf-8",
            )
            (root / "wiki/concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Test page.\n"
                "links: []\n"
                "source_refs: [sources/source-a, sources/missing]\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn(
                "wiki/concepts/idea.md has missing source_refs target: sources/missing",
                issues,
            )

    def test_accepts_existing_raw_source_ref_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
                "raw/sources",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "raw/sources/article.md").write_text("# Raw source\n", encoding="utf-8")
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Test page.\n"
                "links: []\n"
                "source_refs: [raw/sources/article.md]\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertEqual(issues, [])

    def test_reports_non_list_links_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Test page.\n"
                "links: concepts/other\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn("wiki/concepts/idea.md field links must be a list", issues)

    def test_reports_non_list_source_refs_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Test page.\n"
                "links: []\n"
                "source_refs: sources/missing\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn("wiki/concepts/idea.md field source_refs must be a list", issues)

    def test_reports_non_string_updated_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[concepts/idea]]: Test page.\n"
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/concepts/idea.md").write_text(
                "---\n"
                "title: Idea\n"
                "type: concept\n"
                "status: draft\n"
                "updated: []\n"
                "summary: Test page.\n"
                "links: []\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Idea\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn("wiki/concepts/idea.md field updated must be a string", issues)

    def test_reports_empty_next_step_without_question_or_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: [operations/project-intake, operations/project-status, operations/next-steps]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/operations/next-steps.md").write_text(
                "---\n"
                "title: Next Steps\n"
                "type: operation\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Next actions.\n"
                "links: [operations/project-intake, operations/project-status, overview]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Next Steps\n"
                "\n"
                "## Ближайший шаг\n"
                "\n"
                "- Пока не определен.\n"
                "\n"
                "## Что нужно уточнить у пользователя\n"
                "\n"
                "- Пока пусто.\n"
                "\n"
                "## Варианты продолжения\n"
                "\n"
                "- Пока пусто.\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn(
                "wiki/operations/next-steps.md requires a user question or concrete options when the next step is not defined",
                issues,
            )

    def test_accepts_empty_next_step_when_question_or_options_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: [operations/project-intake, operations/project-status, operations/next-steps]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/operations/next-steps.md").write_text(
                "---\n"
                "title: Next Steps\n"
                "type: operation\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Next actions.\n"
                "links: [operations/project-intake, operations/project-status, overview]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Next Steps\n"
                "\n"
                "## Ближайший шаг\n"
                "\n"
                "- Пока не определен.\n"
                "\n"
                "## Что нужно уточнить у пользователя\n"
                "\n"
                "- Какой вариант продолжения считать приоритетным.\n"
                "\n"
                "## Варианты продолжения\n"
                "\n"
                "- Уточнить границы проекта.\n"
                "- Обработать первый источник.\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertEqual(issues, [])

    def test_reports_missing_architecture_review_section_in_project_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in [
                "wiki/concepts",
                "wiki/sources",
                "wiki/entities",
                "wiki/analyses",
                "wiki/operations",
            ]:
                (root / relative).mkdir(parents=True, exist_ok=True)
            self.write_required_operation_files(root)
            (root / "wiki/index.md").write_text(
                "- [[operations/project-intake]]: Intake.\n"
                "- [[operations/project-status]]: Status.\n"
                "- [[operations/next-steps]]: Next.\n",
                encoding="utf-8",
            )
            (root / "wiki/log.md").write_text("## [2026-04-22] lint | Test\n", encoding="utf-8")
            (root / "wiki/overview.md").write_text(
                "---\n"
                "title: Overview\n"
                "type: overview\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Overview.\n"
                "links: [operations/project-intake, operations/project-status, operations/next-steps]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Overview\n",
                encoding="utf-8",
            )
            (root / "wiki/operations/project-status.md").write_text(
                "---\n"
                "title: Project Status\n"
                "type: operation\n"
                "status: draft\n"
                "updated: 2026-04-22\n"
                "summary: Current project state.\n"
                "links: [overview, operations/project-intake, operations/next-steps]\n"
                "source_refs: []\n"
                "---\n"
                "\n"
                "# Project Status\n"
                "\n"
                "## Current Goal\n"
                "\n"
                "- Adapt project.\n",
                encoding="utf-8",
            )

            issues = run_structural_lint(root)

            self.assertIn(
                "wiki/operations/project-status.md missing required section: Архитектурные риски и пересмотр",
                issues,
            )


if __name__ == "__main__":
    unittest.main()
