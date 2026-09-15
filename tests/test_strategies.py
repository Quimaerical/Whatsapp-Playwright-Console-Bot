"""Pruebas unitarias para el Patrón Strategy."""

import unittest
from unittest.mock import MagicMock
from strategies.send_strategies import (
    DirectUrlStrategy,
    SearchContactStrategy,
    get_strategy,
)


class TestSendStrategies(unittest.TestCase):
    """Pruebas de comportamiento para las estrategias de envío."""

    def setUp(self):
        self.mock_chat_page = MagicMock()
        self.mock_chat_page.send_message.return_value = True

    def test_direct_url_strategy_flow(self):
        self.mock_chat_page.open_direct_chat.return_value = True
        strategy = DirectUrlStrategy()
        
        result = strategy.execute(
            chat_page=self.mock_chat_page,
            phone="+5491123456789",
            message="Tarea finalizada.",
        )

        self.assertTrue(result)
        self.mock_chat_page.open_direct_chat.assert_called_once_with(
            phone="+5491123456789", text=""
        )
        self.mock_chat_page.send_message.assert_called_once_with("Tarea finalizada.")

    def test_search_contact_strategy_flow(self):
        self.mock_chat_page.search_and_open_chat.return_value = True
        strategy = SearchContactStrategy()
        
        result = strategy.execute(
            chat_page=self.mock_chat_page,
            phone="+5491123456789",
            message="Tarea finalizada.",
        )

        self.assertTrue(result)
        self.mock_chat_page.search_and_open_chat.assert_called_once_with(
            phone_or_name="+5491123456789"
        )
        self.mock_chat_page.send_message.assert_called_once_with("Tarea finalizada.")

    def test_strategy_aborts_if_preparation_fails(self):
        self.mock_chat_page.open_direct_chat.return_value = False
        strategy = DirectUrlStrategy()
        
        result = strategy.execute(
            chat_page=self.mock_chat_page,
            phone="+5491123456789",
            message="Tarea finalizada.",
        )

        self.assertFalse(result)
        self.mock_chat_page.send_message.assert_not_called()

    def test_get_strategy_factory(self):
        self.assertIsInstance(get_strategy("direct"), DirectUrlStrategy)
        self.assertIsInstance(get_strategy("search"), SearchContactStrategy)
        self.assertIsInstance(get_strategy("unknown"), DirectUrlStrategy)


if __name__ == "__main__":
    unittest.main()
