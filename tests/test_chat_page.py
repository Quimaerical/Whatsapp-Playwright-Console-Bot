"""Pruebas unitarias para la lógica de ChatPage y utilidades de privacidad."""

import unittest
from unittest.mock import MagicMock, patch
from pages.chat_page import ChatPage, mask_phone


class TestChatPage(unittest.TestCase):
    """Pruebas para las utilidades y flujo de confirmación de ChatPage."""

    def setUp(self):
        self.mock_page = MagicMock()
        self.chat_page = ChatPage(self.mock_page)

    def test_mask_phone(self):
        self.assertEqual(mask_phone("+584124837745"), "+584****745")
        self.assertEqual(mask_phone("+5491123456789"), "+549****789")
        self.assertEqual(mask_phone("12345"), "12345")

    def test_is_message_sent_by_delivery_selector(self):
        # Simula que el selector de entrega es visible de inmediato
        self.chat_page.is_visible = MagicMock(side_effect=lambda sel, timeout=0: sel.startswith("[data-testid"))
        result = self.chat_page.is_message_sent(message="Mensaje cualquiera", timeout=1000)
        self.assertTrue(result)

    def test_is_message_sent_by_cleared_input(self):
        # Simula que los selectores de ícono no hacen match pero la caja se vació
        self.chat_page.is_visible = MagicMock(return_value=False)
        mock_input = MagicMock()
        mock_input.is_visible.return_value = True
        mock_input.inner_text.return_value = ""
        self.mock_page.locator.return_value.first = mock_input

        result = self.chat_page.is_message_sent(message="Cualquier texto", timeout=1000)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
