import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class AgentsDocTest(unittest.TestCase):
    def test_agents_mentions_core_rules(self):
        content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        required_phrases = [
            "чат не считается долговременной памятью",
            "сначала обновить постоянные артефакты",
            "сначала перечисли допущения и что может сильно изменить ответ",
            "git init",
            "не смешивать английские слова с русскими предложениями",
            "новые вводные и контекст проекта",
            "Если ближайший шаг пуст",
            "вопрос пользователю",
            "wiki/index.md",
            "wiki/log.md",
            "wiki/operations/project-intake.md",
            "wiki/operations/project-status.md",
            "wiki/operations/next-steps.md",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
