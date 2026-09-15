"""Patrón Strategy: Estrategias desacopladas para el envío de mensajes en WhatsApp Web.

El algoritmo general de ejecución y verificación reside en la clase base (BaseSendStrategy).
Las subclases concretas definen únicamente el mecanismo de apertura y preparación del chat.
Cero código repetido.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pages.chat_page import ChatPage


class BaseSendStrategy(ABC):
    """Clase base para la estrategia de envío.
    
    Define el algoritmo plantilla (Template Method dentro de la Estrategia) para preparar,
    despachar y verificar el envío del mensaje.
    """

    def execute(self, chat_page: ChatPage, phone: str, message: str) -> bool:
        """Algoritmo base: Prepara la interfaz del chat, envía el mensaje y verifica."""
        strategy_name = self.__class__.__name__
        print(f"\n[Strategy] >>> Ejecutando estrategia: {strategy_name}")
        
        is_ready = self.prepare_chat(chat_page, phone, message)
        if not is_ready:
            print(f"[Strategy] ❌ No se pudo preparar el chat usando la estrategia: {strategy_name}")
            return False

        return self.dispatch_and_verify(chat_page, message)

    @abstractmethod
    def prepare_chat(self, chat_page: ChatPage, phone: str, message: str) -> bool:
        """Mecanismo específico de cada subclase para localizar y abrir el chat."""
        pass

    def dispatch_and_verify(self, chat_page: ChatPage, message: str) -> bool:
        """Despacha y valida el mensaje en la interfaz activa."""
        return chat_page.send_message(message)


class DirectUrlStrategy(BaseSendStrategy):
    """Estrategia 1: Envío mediante URL directa (web.whatsapp.com/send?phone=...).
    
    Abre directamente la conversación sin depender de la interacción previa con el buscador.
    """

    def prepare_chat(self, chat_page: ChatPage, phone: str, message: str) -> bool:
        # Abre la ventana de conversación con el número de teléfono
        return chat_page.open_direct_chat(phone=phone, text="")


class SearchContactStrategy(BaseSendStrategy):
    """Estrategia 2: Envío interactivo mediante la barra de búsqueda de WhatsApp Web.
    
    Escribe el número en el campo de búsqueda de la barra lateral y selecciona el resultado.
    """

    def prepare_chat(self, chat_page: ChatPage, phone: str, message: str) -> bool:
        return chat_page.search_and_open_chat(phone_or_name=phone)


def get_strategy(strategy_name: str) -> BaseSendStrategy:
    """Fábrica utilitaria para obtener la instancia de estrategia por nombre."""
    strategies: dict[str, type[BaseSendStrategy]] = {
        "direct": DirectUrlStrategy,
        "search": SearchContactStrategy,
    }
    normalized = strategy_name.strip().lower()
    strategy_cls = strategies.get(normalized, DirectUrlStrategy)
    return strategy_cls()
