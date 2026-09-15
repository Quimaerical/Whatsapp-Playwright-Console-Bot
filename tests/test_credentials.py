"""Pruebas unitarias para utilidades de credenciales y keyring."""

import unittest
from unittest.mock import patch
from utils.credentials import normalize_phone, store_phone, get_stored_phone


class TestCredentials(unittest.TestCase):
    """Pruebas para validación de números y operaciones de Keyring."""

    def test_normalize_phone_valid(self):
        self.assertEqual(normalize_phone("+54 9 11 2345-6789"), "+5491123456789")
        self.assertEqual(normalize_phone("5491123456789"), "5491123456789")
        self.assertEqual(normalize_phone(" +58 (412) 123-4567 "), "+584121234567")

    def test_normalize_phone_invalid(self):
        with self.assertRaises(ValueError):
            normalize_phone("abc---()")

    @patch("utils.credentials.keyring.set_password")
    def test_store_phone(self, mock_set):
        stored = store_phone("+54 9 11 1111 2222")
        self.assertEqual(stored, "+5491111112222")
        mock_set.assert_called_once_with("whatsapp_bot", "target_phone", "+5491111112222")

    @patch("utils.credentials.keyring.get_password")
    def test_get_stored_phone(self, mock_get):
        mock_get.return_value = "+5491123456789"
        result = get_stored_phone()
        self.assertEqual(result, "+5491123456789")


if __name__ == "__main__":
    unittest.main()
