"""Patrón Page Object Model: Página de Conversación y Envío de Mensajes en WhatsApp Web."""

from __future__ import annotations

import time
from urllib.parse import quote_plus
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import (
    ELEMENT_TIMEOUT,
    MESSAGE_SEND_TIMEOUT,
    SELECTORS,
    WHATSAPP_SEND_URL_TEMPLATE,
)
from .base_page import BasePage


# ─── PRIVACY UTILITIES ────────────────────────────────────────────────────────

def mask_phone(phone: str) -> str:
    """Enmascara el número telefónico para preservar la privacidad en los logs de consola."""
    clean = phone.strip()
    if len(clean) > 7:
        return f"{clean[:4]}****{clean[-3:]}"
    return clean


# ─── CHAT & MESSAGING PAGE OBJECT ─────────────────────────────────────────────

class ChatPage(BasePage):
    """Encapsula las acciones dentro de una conversación de WhatsApp Web."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ─── CONVERSATION OPENING ─────────────────────────────────────────────────

    def open_direct_chat(self, phone: str, text: str = "") -> bool:
        """Abre un chat directamente mediante el enlace oficial de WhatsApp Web (send?phone=...)."""
        clean_phone = phone.lstrip("+")
        encoded_text = quote_plus(text) if text else ""
        url = WHATSAPP_SEND_URL_TEMPLATE.format(phone=clean_phone, text=encoded_text)

        print(f"[ChatPage] Abriendo conversación directa con: {mask_phone(phone)}...")
        self.navigate(url)

        try:
            self.page.wait_for_selector(SELECTORS["chat_input"], timeout=ELEMENT_TIMEOUT)
            print("[ChatPage] Conversación cargada y lista para interactuar.")
            return True
        except PlaywrightTimeoutError:
            if self.is_visible(SELECTORS["invalid_phone_popup"], timeout=3000):
                print(f"[ChatPage] [ERROR] WhatsApp indica que el número {mask_phone(phone)} no es válido o no está registrado.")
            else:
                print("[ChatPage] [TIMEOUT] Tiempo agotado esperando la carga de la conversación.")
            return False

    def search_and_open_chat(self, phone_or_name: str) -> bool:
        """Busca un contacto o número en la barra de búsqueda de WhatsApp Web y lo abre."""
        print(f"[ChatPage] Buscando contacto/número en la lista de chats: {mask_phone(phone_or_name)}...")

        if not self.is_visible(SELECTORS["search_input"]):
            print("[ChatPage] [ERROR] La barra de búsqueda no es visible.")
            return False

        self.click(SELECTORS["search_input"])
        self.fill(SELECTORS["search_input"], phone_or_name)
        self.wait_for_timeout(1500)
        self.press_key("Enter")
        self.wait_for_timeout(1500)

        try:
            self.page.wait_for_selector(SELECTORS["chat_input"], timeout=ELEMENT_TIMEOUT)
            print("[ChatPage] Chat seleccionado y abierto correctamente.")
            return True
        except PlaywrightTimeoutError:
            print(f"[ChatPage] [ERROR] No se pudo abrir el chat para '{mask_phone(phone_or_name)}'.")
            return False

    # ─── MESSAGE COMPOSITION & DISPATCH ───────────────────────────────────────

    def type_message(self, message: str) -> None:
        """Escribe el mensaje en el campo de texto editable respetando saltos de línea con Shift+Enter."""
        print("[ChatPage] Escribiendo mensaje en el chat...")
        chat_input = self.page.locator(SELECTORS["chat_input"]).first
        chat_input.click()
        chat_input.focus()

        lines = message.split("\n")
        for i, line in enumerate(lines):
            if line:
                self.page.keyboard.type(line, delay=20)
            if i < len(lines) - 1:
                self.page.keyboard.press("Shift+Enter")

        self.wait_for_timeout(500)

    def click_send(self) -> None:
        """Envía el mensaje haciendo clic en el botón de enviar o presionando Enter en la caja."""
        print("[ChatPage] Enviando mensaje...")
        send_btn = self.page.locator(SELECTORS["send_button"]).first
        if send_btn.is_visible(timeout=2000):
            send_btn.click()
        else:
            chat_input = self.page.locator(SELECTORS["chat_input"]).first
            chat_input.focus()
            chat_input.press("Enter")

        self.wait_for_timeout(500)

    # ─── DYNAMIC DELIVERY CONFIRMATION ────────────────────────────────────────

    def is_message_sent(self, message: str = "", timeout: int = MESSAGE_SEND_TIMEOUT) -> bool:
        """Verifica que el mensaje haya sido despachado exitosamente mediante detección multi-criterio.
        
        Evalúa de forma dinámica sin texto hardcodeado:
        1. Presencia de selectores de confirmación (ticks de envío, entrega o mensaje saliente).
        2. Presencia del primer renglón del mensaje dinámico en el panel de conversación.
        3. Vaciado del compose box y restauración del botón de micrófono.
        """
        print("[ChatPage] Verificando confirmación de entrega...")
        first_line = next((line.strip() for line in message.splitlines() if line.strip()), "")

        start_time = time.time()
        max_duration = timeout / 1000.0

        while time.time() - start_time < max_duration:
            # Criterio 1: Indicadores universales de entrega en el DOM
            if self.is_visible(SELECTORS["sent_message"], timeout=400):
                print("[ChatPage] [OK] Indicador de entrega detectado en el DOM.")
                return True

            # Criterio 2: Búsqueda dinámica del texto enviado dentro del panel de conversación
            if first_line:
                try:
                    main_panel = self.page.locator(SELECTORS["main_chat"]).first
                    if main_panel.is_visible(timeout=300):
                        # Escapar comillas dobles si las hubiera
                        escaped_text = first_line.replace('"', '\\"')
                        text_match = main_panel.locator(f'text="{escaped_text}"').last
                        if text_match.is_visible(timeout=300):
                            print(f"[ChatPage] [OK] Mensaje confirmado visualmente en la conversación.")
                            return True
                except Exception:
                    pass

            # Criterio 3: Vaciado del campo de texto y desaparición del botón Enviar
            try:
                chat_input = self.page.locator(SELECTORS["chat_input"]).first
                if chat_input.is_visible(timeout=300):
                    current_text = chat_input.inner_text().strip()
                    send_btn_visible = self.is_visible(SELECTORS["send_button"], timeout=200)
                    mic_btn_visible = self.is_visible(SELECTORS["mic_button"], timeout=200)

                    if current_text == "" and (not send_btn_visible or mic_btn_visible):
                        print("[ChatPage] [OK] Campo de texto vaciado y mensaje despachado.")
                        return True
            except Exception:
                pass

            self.wait_for_timeout(400)

        print("[ChatPage] [AVISO] No se observó el indicador de entrega en el tiempo esperado.")
        return False

    def send_message(self, message: str) -> bool:
        """Flujo completo para escribir, enviar y verificar el mensaje dinámico."""
        self.type_message(message)
        self.click_send()
        return self.is_message_sent(message=message)
