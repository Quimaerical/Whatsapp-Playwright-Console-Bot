"""Pruebas unitarias para los Builders (MessageBuilder y BrowserBuilder)."""

import unittest
from unittest.mock import MagicMock
from pathlib import Path
from utils.message_builder import MessageBuilder
from core.browser_builder import BrowserBuilder


class TestMessageBuilder(unittest.TestCase):
    """Pruebas para verificar la construcción del mensaje requerido en la tarea."""

    def test_default_required_message(self):
        message = (
            MessageBuilder()
            .set_status("Tarea finalizada.")
            .add_pattern("Builder")
            .add_pattern("Page Object Model")
            .add_pattern("Strategy")
            .build()
        )
        expected = (
            "Tarea finalizada.\n"
            "Patrones utilizados: Builder, Page Object Model, Strategy."
        )
        self.assertEqual(message, expected)

    def test_set_patterns_list(self):
        builder = MessageBuilder()
        builder.set_patterns(["Builder", "Page Object Model", "Strategy"])
        expected = (
            "Tarea finalizada.\n"
            "Patrones utilizados: Builder, Page Object Model, Strategy."
        )
        self.assertEqual(builder.build(), expected)

    def test_duplicate_patterns_ignored(self):
        builder = MessageBuilder()
        builder.add_pattern("Builder").add_pattern("Builder").add_pattern("Strategy")
        expected = "Tarea finalizada.\nPatrones utilizados: Builder, Strategy."
        self.assertEqual(builder.build(), expected)

    def test_with_custom_footer(self):
        builder = MessageBuilder().add_pattern("Builder").with_footer("Nota adicional.")
        self.assertIn("Nota adicional.", builder.build())


class TestBrowserBuilder(unittest.TestCase):
    """Pruebas para verificar el encadenamiento fluido y la configuración de BrowserBuilder."""

    def setUp(self):
        self.mock_playwright = MagicMock()

    def test_method_chaining(self):
        builder = (
            BrowserBuilder(self.mock_playwright)
            .with_type("firefox")
            .headless(True)
            .slow_mo(200)
            .with_storage_state("auth/storage_state.json")
            .with_user_data_dir("auth/user_data")
            .with_viewport(1920, 1080)
            .with_args(["--test-arg"])
        )

        self.assertEqual(builder._browser_type, "firefox")
        self.assertTrue(builder._headless)
        self.assertEqual(builder._slow_mo, 200)
        self.assertEqual(builder._storage_state, Path("auth/storage_state.json"))
        self.assertEqual(builder._user_data_dir, Path("auth/user_data"))
        self.assertEqual(builder._viewport, {"width": 1920, "height": 1080})
        self.assertIn("--test-arg", builder._args)


if __name__ == "__main__":
    unittest.main()
