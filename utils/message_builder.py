"""Patrón Builder: Constructor de mensajes formateados para el Bot de WhatsApp."""

from __future__ import annotations


class MessageBuilder:
    """Constructor paso a paso del mensaje final a enviar por WhatsApp.
    
    Permite construir el texto asegurando el cumplimiento estricto del formato:
    "Tarea finalizada.
    Patrones utilizados: Builder, Page Object Model, Strategy."
    """

    def __init__(self) -> None:
        self._status: str = "Tarea finalizada."
        self._patterns: list[str] = []
        self._footer: str | None = None
        self._custom_message: str | None = None

    def set_status(self, status: str) -> MessageBuilder:
        """Define la línea de estado inicial del mensaje."""
        self._status = status.strip()
        return self

    def add_pattern(self, pattern_name: str) -> MessageBuilder:
        """Agrega un patrón de diseño a la lista de patrones."""
        clean_name = pattern_name.strip()
        if clean_name and clean_name not in self._patterns:
            self._patterns.append(clean_name)
        return self

    def set_patterns(self, patterns: list[str]) -> MessageBuilder:
        """Sobrescribe la lista completa de patrones."""
        self._patterns = [p.strip() for p in patterns if p.strip()]
        return self

    def with_footer(self, footer: str) -> MessageBuilder:
        """Agrega un pie de mensaje opcional."""
        self._footer = footer.strip()
        return self

    def set_custom_message(self, message: str) -> MessageBuilder:
        """Establece directamente un texto personalizado para el mensaje."""
        self._custom_message = message.strip()
        return self

    def build(self) -> str:
        """Compila y retorna el mensaje como cadena de texto."""
        if self._custom_message is not None:
            return self._custom_message

        patterns_str = ", ".join(self._patterns)
        message = f"{self._status}\nPatrones utilizados: {patterns_str}."
        if self._footer:
            message += f"\n\n{self._footer}"
        return message

    @classmethod
    def default_task_message(cls) -> str:
        """Genera el mensaje por defecto requerido para la tarea."""
        return (
            cls()
            .set_status("Tarea finalizada.")
            .add_pattern("Builder")
            .add_pattern("Page Object Model")
            .add_pattern("Strategy")
            .build()
        )

