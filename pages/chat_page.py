"""Patrón Page Object Model: Página de Conversación y Envío de Mensajes en WhatsApp Web."""

from __future__ import annotations
from urllib.parse import quote_plus
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import (
    ELEMENT_TIMEOUT,
    MESSAGE_SEND_TIMEOUT,
    SELECTORS,
    WHATSAPP_SEND_URL_TEMPLATE,
)
from .base_page import BasePage


class ChatPage(BasePage):
    """Encapsula las acciones dentro de una conversación de WhatsApp Web."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open_direct_chat(self, phone: str, text: str = "") -> bool:
        """Abre un chat directamente mediante el enlace oficial de WhatsApp Web (send?phone=...)."""
        clean_phone = phone.lstrip("+")
        encoded_text = quote_plus(text) if text else ""
        url = WHATSAPP_SEND_URL_TEMPLATE.format(phone=clean_phone, text=encoded_text)
        
        print(f"[ChatPage] Abriendo conversación directa con: +{clean_phone}...")
        self.navigate(url)

        # Esperar a que la caja de texto del chat esté lista
        try:
            self.page.wait_for_selector(SELECTORS["chat_input"], timeout=ELEMENT_TIMEOUT)
            print("[ChatPage] Conversación cargada y lista para interactuar.")
            return True
        except PlaywrightTimeoutError:
            if self.is_visible(SELECTORS["invalid_phone_popup"], timeout=3000):
                print(f"[ChatPage] Error: WhatsApp indica que el número +{clean_phone} no es válido o no está registrado.")
            else:
                print("[ChatPage] Tiempo agotado esperando la carga de la conversación.")
            return False

    def search_and_open_chat(self, phone_or_name: str) -> bool:
        """Busca un contacto o número en la barra de búsqueda de WhatsApp Web y lo abre."""
        print(f"[ChatPage] Buscando contacto/número en la lista de chats: {phone_or_name}...")
        
        if not self.is_visible(SELECTORS["search_input"]):
            print("[ChatPage] Error: La barra de búsqueda no es visible.")
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
            print(f"[ChatPage] No se pudo abrir el chat para '{phone_or_name}'.")
            return False

    def type_message(self, message: str) -> None:
        """Escribe el mensaje en el campo de texto editable respetando saltos de línea con Shift+Enter."""
        print("[ChatPage] Escribiendo mensaje en el chat...")
        self.click(SELECTORS["chat_input"])
        
        lines = message.split("\n")
        for i, line in enumerate(lines):
            if line:
                self.page.keyboard.type(line, delay=20)
            if i < len(lines) - 1:
                # Shift+Enter para salto de línea sin enviar prematuramente
                self.page.keyboard.press("Shift+Enter")
        
        self.wait_for_timeout(500)

    def click_send(self) -> None:
        """Envía el mensaje haciendo clic en el botón de enviar o presionando Enter."""
        print("[ChatPage] Enviando mensaje...")
        if self.is_visible(SELECTORS["send_button"], timeout=3000):
            self.click(SELECTORS["send_button"])
        else:
            self.press_key("Enter")

    def is_message_sent(self, timeout: int = MESSAGE_SEND_TIMEOUT) -> bool:
        """Verifica que el mensaje haya sido despachado exitosamente."""
        print("[ChatPage] Verificando confirmación de entrega...")
        try:
            self.page.wait_for_selector(SELECTORS["sent_message"], timeout=timeout)
            print("[ChatPage] ¡Mensaje enviado con éxito!")
            return True
        except PlaywrightTimeoutError:
            print("[ChatPage] Advertencia: No se observó el indicador de entrega en el tiempo esperado.")
            return False

    def send_message(self, message: str) -> bool:
        """Flujo completo para escribir, enviar y verificar el mensaje."""
        self.type_message(message)
        self.click_send()
        return self.is_message_sent()
