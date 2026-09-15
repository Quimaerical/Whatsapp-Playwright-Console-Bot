"""Patrón Builder: Construcción fluida y desacoplada de instancias de navegador y contexto en Playwright."""

from __future__ import annotations
from pathlib import Path
from typing import Any
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


class BrowserBuilder:
    """Builder para configurar y construir instancias de navegador y páginas en Playwright.
    
    Permite encadenar métodos para configurar tipo de navegador, modo headless,
    latencia (slow_mo), persistencia de sesión con storage_state y context directory.
    """

    def __init__(self, playwright: Playwright) -> None:
        self.playwright = playwright
        self._browser_type: str = "chromium"
        self._headless: bool = False
        self._slow_mo: int = 500
        self._storage_state: str | Path | None = None
        self._user_data_dir: str | Path | None = None
        self._viewport: dict[str, int] = {"width": 1280, "height": 800}
        self._args: list[str] = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]

    def with_type(self, browser_type: str) -> BrowserBuilder:
        """Define el motor de navegador a utilizar (chromium, firefox, webkit)."""
        self._browser_type = browser_type.lower()
        return self

    def headless(self, headless: bool) -> BrowserBuilder:
        """Establece si el navegador se ejecutará en segundo plano (headless) o visible."""
        self._headless = headless
        return self

    def slow_mo(self, slow_mo: int) -> BrowserBuilder:
        """Añade una pausa en milisegundos entre cada acción para facilitar la visualización."""
        self._slow_mo = slow_mo
        return self

    def with_storage_state(self, path: str | Path | None) -> BrowserBuilder:
        """Define la ruta al archivo JSON de storage_state de Playwright para cargar cookies y almacenamiento."""
        if path is not None:
            self._storage_state = Path(path)
        else:
            self._storage_state = None
        return self

    def with_user_data_dir(self, path: str | Path | None) -> BrowserBuilder:
        """Define el directorio de perfil persistente para retener IndexedDB y credenciales de sesión."""
        if path is not None:
            self._user_data_dir = Path(path)
        else:
            self._user_data_dir = None
        return self

    def with_viewport(self, width: int, height: int) -> BrowserBuilder:
        """Configura las dimensiones del viewport."""
        self._viewport = {"width": width, "height": height}
        return self

    def with_args(self, extra_args: list[str]) -> BrowserBuilder:
        """Añade argumentos adicionales de línea de comandos al navegador."""
        self._args.extend(extra_args)
        return self

    def build(self) -> tuple[Browser | None, BrowserContext, Page]:
        """Construye y devuelve una tupla conteniendo (browser, context, page).
        
        Si se utiliza un `user_data_dir`, se genera un Persistent Context (requerido por
        WhatsApp Web para no perder claves en IndexedDB). En este caso `browser` es None
        pues el ciclo de vida lo maneja el context.
        """
        browser_launcher = getattr(self.playwright, self._browser_type)

        if self._user_data_dir is not None:
            self._user_data_dir.mkdir(parents=True, exist_ok=True)
            context = browser_launcher.launch_persistent_context(
                user_data_dir=str(self._user_data_dir),
                headless=self._headless,
                slow_mo=self._slow_mo,
                viewport=self._viewport,
                args=self._args,
                # Evita que WhatsApp detecte la automatización como bot obsoleto
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = context.pages[0] if context.pages else context.new_page()
            return None, context, page

        # Modo estándar con browser separado
        browser: Browser = browser_launcher.launch(
            headless=self._headless,
            slow_mo=self._slow_mo,
            args=self._args,
        )

        context_kwargs: dict[str, Any] = {
            "viewport": self._viewport,
            "user_agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        if self._storage_state and self._storage_state.exists():
            context_kwargs["storage_state"] = str(self._storage_state)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        return browser, context, page
