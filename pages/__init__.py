"""Módulo de Page Object Model (POM) para WhatsApp Web."""

from .base_page import BasePage
from .login_page import LoginPage
from .chat_page import ChatPage

__all__ = ["BasePage", "LoginPage", "ChatPage"]
