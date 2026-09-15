"""Patrón Page Object Model: Página de Autenticación y Código QR de WhatsApp Web."""

from __future__ import annotations

from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import QR_SCAN_TIMEOUT, SELECTORS, WHATSAPP_WEB_URL
from .base_page import BasePage


# ─── LOGIN & AUTHENTICATION PAGE OBJECT ───────────────────────────────────────

class LoginPage(BasePage):
    """Encapsula la interfaz de inicio de sesión, escaneo de QR y persistencia de storage_state."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ─── LIFECYCLE & STATE DETECTION ──────────────────────────────────────────

    def load(self) -> None:
        """Abre la página principal de WhatsApp Web."""
        print("[LoginPage] Accediendo a WhatsApp Web...")
        self.navigate(WHATSAPP_WEB_URL)

    def is_logged_in(self, timeout: int = 15_000) -> bool:
        """Comprueba si la sesión ya está activa verificando la presencia de la lista de chats."""
        return self.is_visible(SELECTORS["chat_list"], timeout=timeout)

    def is_qr_visible(self, timeout: int = 10_000) -> bool:
        """Comprueba si el código QR está visible en pantalla."""
        return self.is_visible(SELECTORS["qr_canvas"], timeout=timeout)

    # ─── QR HANDLING & PERSISTENCE ────────────────────────────────────────────

    def wait_for_login(self, timeout: int = QR_SCAN_TIMEOUT) -> bool:
        """Espera a que el usuario escanee el código QR y se cargue la lista de chats."""
        print("[LoginPage] Esperando que se escanee el código QR...")
        print(f"[LoginPage] Tienes hasta {timeout // 1000} segundos para escanear el QR en tu teléfono...")

        try:
            self.page.wait_for_selector(SELECTORS["chat_list"], timeout=timeout)
            print("[LoginPage] [OK] Inicio de sesión detectado exitosamente.")
            self.wait_for_timeout(3000)
            return True
        except PlaywrightTimeoutError:
            print("[LoginPage] [ERROR] Tiempo de espera agotado para el escaneo del código QR.")
            return False

    def save_storage_state(self, path: Path | str) -> None:
        """Exporta el estado de almacenamiento (cookies y localStorage) al archivo JSON especificado."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.context.storage_state(path=str(file_path))
        print(f"[LoginPage] storage_state guardado exitosamente en: {file_path}")
