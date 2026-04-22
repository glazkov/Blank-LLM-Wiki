import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MakefileTest(unittest.TestCase):
    def parse_makefile(self):
        content = (ROOT / "Makefile").read_text(encoding="utf-8")
        targets = {}
        current_target = None
        current_commands = []
        for line in content.splitlines():
            if line.startswith(".PHONY:"):
                phony_targets = line.split(":", 1)[1].strip().split()
                targets[".PHONY"] = phony_targets
                current_target = None
                current_commands = []
                continue
            if line and not line.startswith("\t") and line.endswith(":"):
                if current_target is not None:
                    targets[current_target] = current_commands
                current_target = line[:-1]
                current_commands = []
                continue
            if line and not line.startswith("\t") and ":" in line:
                if current_target is not None:
                    targets[current_target] = current_commands
                target, dependencies = line.split(":", 1)
                targets[target] = dependencies.strip().split()
                current_target = None
                current_commands = []
                continue
            if line.startswith("\t") and current_target is not None:
                current_commands.append(line[1:])
        if current_target is not None:
            targets[current_target] = current_commands
        return targets

    def test_makefile_exposes_expected_targets_and_mappings(self):
        targets = self.parse_makefile()

        self.assertEqual(
            targets[".PHONY"],
            ["lint", "lint-struct", "lint-semantic", "status", "test"],
        )
        self.assertEqual(targets["lint"], ["lint-struct", "lint-semantic"])
        self.assertEqual(targets["lint-struct"], ["python3 tools/lint_wiki.py"])
        self.assertEqual(
            targets["lint-semantic"],
            [
                "python3 tools/check_orphans.py",
                "python3 tools/check_stale.py",
            ],
        )
        self.assertEqual(
            targets["status"],
            [
                '@echo "== wiki files =="',
                "@find wiki -type f | sort",
                '@echo ""',
                '@echo "== project intake =="',
                "@cat wiki/operations/project-intake.md",
                '@echo ""',
                '@echo "== project status =="',
                "@cat wiki/operations/project-status.md",
                '@echo ""',
                '@echo "== next steps =="',
                "@cat wiki/operations/next-steps.md",
                '@echo ""',
                '@echo "== structural lint =="',
                "@python3 tools/lint_wiki.py || true",
                '@echo ""',
                '@echo "== semantic lint =="',
                "@python3 tools/check_orphans.py || true",
                "@python3 tools/check_stale.py || true",
            ],
        )
        self.assertEqual(
            targets["test"],
            ["python3 -m unittest discover -s tests -v"],
        )


if __name__ == "__main__":
    unittest.main()
