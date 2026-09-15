"""Punto de entrada principal para el Bot de WhatsApp con Playwright.

Orquesta la inicialización del navegador con BrowserBuilder, la interacción con la UI
mediante Page Object Model (LoginPage y ChatPage), la selección de la estrategia de envío
(Strategy) y la gestión de credenciales seguras con Keyring.
"""

from __future__ import annotations
import argparse
import os
import sys
from playwright.sync_api import sync_playwright

from config import (
    AUTH_DIR,
    DEFAULT_SLOW_MO,
    QR_SCAN_TIMEOUT,
    STORAGE_STATE_PATH,
    USER_DATA_DIR,
)
from core.browser_builder import BrowserBuilder
from pages.chat_page import ChatPage
from pages.login_page import LoginPage
from strategies.send_strategies import get_strategy
from utils.credentials import (
    delete_stored_phone,
    get_stored_phone,
    resolve_target_phone,
)
from utils.message_builder import MessageBuilder


def parse_arguments() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Bot de WhatsApp con Playwright y Patrones de Diseño (Builder, POM, Strategy)."
    )
    parser.add_argument(
        "--phone",
        type=str,
        default=None,
        help="Número de teléfono de destino (con código de país, ej. +5491123456789).",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["direct", "search"],
        default="direct",
        help="Estrategia de envío: 'direct' (URL directa) o 'search' (búsqueda en UI).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar el navegador en segundo plano (requiere sesión ya existente).",
    )
    parser.add_argument(
        "--reset-session",
        action="store_true",
        help="Borra la sesión guardada para forzar un nuevo escaneo de código QR.",
    )
    parser.add_argument(
        "--reset-phone",
        action="store_true",
        help="Borra el número de teléfono guardado en Keyring.",
    )
    return parser.parse_args()


def reset_saved_session() -> None:
    """Elimina los archivos de sesión guardados."""
    if STORAGE_STATE_PATH.exists():
        STORAGE_STATE_PATH.unlink()
        print(f"[Sesión] Archivo {STORAGE_STATE_PATH} eliminado.")
    if USER_DATA_DIR.exists():
        import shutil
        shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
        print(f"[Sesión] Directorio de sesión {USER_DATA_DIR} eliminado.")
    print("[Sesión] Sesión reiniciada con éxito.")


def main() -> None:
    args = parse_arguments()

    print("================================================================")
    print("      BOT DE WHATSAPP CON PLAYWRIGHT Y PATRONES DE DISEÑO       ")
    print("================================================================\n")

    # Manejo de reseteos de credenciales si fueron solicitados
    if args.reset_phone:
        delete_stored_phone()
        if not args.phone:
            print("Número de teléfono reseteado. Saliendo.")
            return

    if args.reset_session:
        reset_saved_session()

    # 1. Obtener el número de teléfono mediante Keyring
    try:
        target_phone = resolve_target_phone(args.phone, interactive=True)
    except Exception as err:
        print(f"[Error] No se pudo resolver el número de destino: {err}")
        sys.exit(1)

    # 2. Construcción del mensaje a enviar aplicando el Patrón Builder
    message = (
        MessageBuilder()
        .set_status("Tarea finalizada.")
        .add_pattern("Builder")
        .add_pattern("Page Object Model")
        .add_pattern("Strategy")
        .build()
    )

    print("\n[Mensaje a Enviar]:")
    print("----------------------------------------------------------------")
    print(message)
    print("----------------------------------------------------------------\n")

    # 3. Comprobación de persistencia de sesión (storage_state de Playwright)
    session_exists = STORAGE_STATE_PATH.exists()
    
    if session_exists:
        print(f"[Sesión] ✅ Se encontró sesión previa en: {STORAGE_STATE_PATH}")
        print("[Sesión] Cargando storage_state existente. Se omitirá el escaneo de QR.")
    else:
        print(f"[Sesión] ℹ️ No existe sesión previa en: {STORAGE_STATE_PATH}")
        print("[Sesión] Primera ejecución: Se abrirá el navegador para escanear el código QR.")

    headless_mode = args.headless if session_exists else False
    if args.headless and not session_exists:
        print("[Aviso] Se desactivó el modo headless porque se requiere escanear el código QR.")

    # 4. Construcción del navegador aplicando el Patrón Builder (core/browser_builder.py)
    with sync_playwright() as playwright:
        builder = (
            BrowserBuilder(playwright)
            .with_type("chromium")
            .headless(headless_mode)
            .slow_mo(DEFAULT_SLOW_MO)
            .with_user_data_dir(USER_DATA_DIR)
            .with_storage_state(STORAGE_STATE_PATH if session_exists else None)
        )

        browser, context, page = builder.build()

        try:
            # 5. Page Object Model: Manejo de autenticación con LoginPage
            login_page = LoginPage(page)
            login_page.load()

            # Verificación de sesión activa
            if session_exists:
                if not login_page.is_logged_in(timeout=15_000):
                    print("[Sesión] ⚠️ La sesión anterior no fue válida o expiró. Esperando nuevo QR...")
                    if not login_page.wait_for_login(timeout=QR_SCAN_TIMEOUT):
                        print("[Error] No se completó el inicio de sesión. Abortando.")
                        return
                    login_page.save_storage_state(STORAGE_STATE_PATH)
                else:
                    print("[Sesión] ✅ Sesión confirmada activa.")
            else:
                # Primera ejecución: esperar escaneo de QR
                if not login_page.wait_for_login(timeout=QR_SCAN_TIMEOUT):
                    print("[Error] No se escaneó el código QR dentro del tiempo permitido.")
                    return
                # Guardar storage_state inmediatamente al autenticar
                login_page.save_storage_state(STORAGE_STATE_PATH)

            # 6. Page Object Model & Patrón Strategy: Envío de mensaje
            chat_page = ChatPage(page)
            strategy = get_strategy(args.strategy)
            
            success = strategy.execute(
                chat_page=chat_page,
                phone=target_phone,
                message=message,
            )

            if success:
                print("\n================================================================")
                print(" ✅ PROCESO FINALIZADO CON ÉXITO: Mensaje enviado a WhatsApp Web ")
                print("================================================================")
            else:
                print("\n================================================================")
                print(" ❌ ADVERTENCIA: No se pudo confirmar la entrega del mensaje.   ")
                print("================================================================")

            # 7. Guardar storage_state actualizado al cerrar
            login_page.save_storage_state(STORAGE_STATE_PATH)

        finally:
            context.close()
            if browser:
                browser.close()


if __name__ == "__main__":
    main()
