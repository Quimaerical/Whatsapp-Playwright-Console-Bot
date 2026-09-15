"""Patrón Page Object Model: Clase base para páginas de Playwright."""

from __future__ import annotations

from typing import Any
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config import ELEMENT_TIMEOUT, PAGE_LOAD_TIMEOUT


# ─── BASE PAGE OBJECT ─────────────────────────────────────────────────────────

class BasePage:
    """Clase base de Page Object Model que encapsula la interacción con la instancia de Page."""

    def __init__(self, page: Page) -> None:
        self.page: Page = page

    # ─── NAVIGATION & WAITING ─────────────────────────────────────────────────

    def navigate(self, url: str, wait_until: str = "domcontentloaded", timeout: int = PAGE_LOAD_TIMEOUT) -> None:
        """Navega a la URL especificada esperando el estado de carga indicado."""
        self.page.goto(url, wait_until=wait_until, timeout=timeout)  # type: ignore

    def wait_for_selector(self, selector: str, timeout: int = ELEMENT_TIMEOUT) -> Locator:
        """Espera a que un selector esté presente en el DOM."""
        return self.page.wait_for_selector(selector, timeout=timeout)  # type: ignore

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Verifica si un selector es visible dentro del tiempo límite sin lanzar excepción."""
        try:
            loc = self.page.locator(selector).first
            return loc.is_visible(timeout=timeout)
        except (PlaywrightTimeoutError, Exception):
            return False

    def wait_for_timeout(self, milliseconds: int) -> None:
        """Pausa la ejecución durante una cantidad determinada de milisegundos."""
        self.page.wait_for_timeout(milliseconds)

    # ─── INTERACTION & INPUT ──────────────────────────────────────────────────

    def click(self, selector: str, timeout: int = ELEMENT_TIMEOUT) -> None:
        """Hace clic sobre el selector indicado."""
        self.page.locator(selector).first.click(timeout=timeout)

    def fill(self, selector: str, text: str, timeout: int = ELEMENT_TIMEOUT) -> None:
        """Rellena un campo de texto."""
        self.page.locator(selector).first.fill(text, timeout=timeout)

    def press_key(self, key: str) -> None:
        """Emula la pulsación de una tecla física del teclado."""
        self.page.keyboard.press(key)
