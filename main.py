"""Punto de entrada principal para el Bot de WhatsApp con Playwright.

Orquesta la inicialización del navegador con BrowserBuilder, la interacción con la UI
mediante Page Object Model (LoginPage y ChatPage), la selección de la estrategia de envío
(Strategy) y la gestión de credenciales seguras con Keyring.
"""

from __future__ import annotations

import argparse
import os
import shutil
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


# ─── CONFIGURATION & CLI ARGUMENT PARSING ─────────────────────────────────────

def parse_arguments() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Bot de WhatsApp con Playwright y Patrones de Diseño (Builder, POM, Strategy)."
    )

    parser.add_argument(
        "--message",
        "-m",
        type=str,
        default=None,
        help="Texto personalizado para el mensaje (si no se especifica, usa el mensaje por defecto).",
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


# ─── SESSION MAINTENANCE ──────────────────────────────────────────────────────

def reset_saved_session() -> None:
    """Elimina los archivos y directorios de sesión guardados."""
    if STORAGE_STATE_PATH.exists():
        STORAGE_STATE_PATH.unlink()
        print(f"[Sesion] Archivo {STORAGE_STATE_PATH} eliminado.")

    if USER_DATA_DIR.exists():
        shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
        print(f"[Sesion] Directorio de sesion {USER_DATA_DIR} eliminado.")

    print("[Sesion] Sesion reiniciada con exito.")


# ─── MESSAGE RESOLUTION ───────────────────────────────────────────────────────

def resolve_message(cli_message: str | None, interactive: bool = True) -> str:
    """Determina el mensaje a enviar: vía argumento CLI, entrada en terminal o mensaje por defecto."""
    default_msg = MessageBuilder.default_task_message()

    if cli_message is not None and cli_message.strip():
        clean_msg = cli_message.strip().replace("\\n", "\n")
        print("[Mensaje] Usando mensaje personalizado especificado por argumento CLI.")
        return MessageBuilder().set_custom_message(clean_msg).build()

    if not interactive:
        return default_msg

    print("\n[Mensaje por Defecto]:")
    print("----------------------------------------------------------------")
    print(default_msg)
    print("----------------------------------------------------------------")
    print("Opciones:")
    print("  - Presiona [Enter] para usar el mensaje por defecto.")
    print("  - O escribe el nuevo mensaje personalizado y presiona [Enter]:")

    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperacion cancelada por el usuario.")
        sys.exit(0)

    if not user_input:
        print("[Mensaje] Usando mensaje por defecto.")
        return default_msg

    custom_text = user_input.replace("\\n", "\n")
    print("[Mensaje] Usando mensaje personalizado ingresado en terminal.")
    return MessageBuilder().set_custom_message(custom_text).build()


# ─── MAIN ORCHESTRATION ───────────────────────────────────────────────────────

def main() -> None:
    args = parse_arguments()

    print("================================================================")
    print("      BOT DE WHATSAPP CON PLAYWRIGHT Y PATRONES DE DISENO       ")
    print("================================================================\n")

    if args.reset_phone:
        delete_stored_phone()
        if not args.phone:
            print("[Keyring] Numero de telefono reseteado. Finalizando.")
            return

    if args.reset_session:
        reset_saved_session()

    # 1. Gestion de credenciales con Keyring
    try:
        target_phone = resolve_target_phone(args.phone, interactive=True)
    except Exception as err:
        print(f"[Error] No se pudo resolver el numero de destino: {err}")
        sys.exit(1)

    # 2. Resolucion del mensaje con Builder Pattern
    message = resolve_message(args.message, interactive=True)

    print("\n[Mensaje Final a Enviar]:")
    print("----------------------------------------------------------------")
    print(message)
    print("----------------------------------------------------------------\n")

    # 3. Comprobacion de persistencia de sesion (storage_state de Playwright)
    session_exists = STORAGE_STATE_PATH.exists()

    if session_exists:
        print(f"[Sesion] [OK] Se encontro sesion previa en: {STORAGE_STATE_PATH}")
        print("[Sesion] Cargando storage_state existente. Se omitira el escaneo de QR.")
    else:
        print(f"[Sesion] [INFO] No existe sesion previa en: {STORAGE_STATE_PATH}")
        print("[Sesion] Primera ejecucion: Se abrira el navegador para escanear el codigo QR.")

    headless_mode = args.headless if session_exists else False
    if args.headless and not session_exists:
        print("[Aviso] Se desactivo el modo headless porque se requiere escanear el codigo QR.")

    # 4. Construccion del navegador con BrowserBuilder
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
            # 5. Autenticacion con Page Object Model (LoginPage)
            login_page = LoginPage(page)
            login_page.load()

            if session_exists:
                if not login_page.is_logged_in(timeout=15_000):
                    print("[Sesion] [AVISO] La sesion anterior no fue valida o expiro. Esperando nuevo QR...")
                    if not login_page.wait_for_login(timeout=QR_SCAN_TIMEOUT):
                        print("[Error] No se completo el inicio de sesion. Abortando.")
                        return
                    login_page.save_storage_state(STORAGE_STATE_PATH)
                else:
                    print("[Sesion] [OK] Sesion confirmada activa.")
            else:
                if not login_page.wait_for_login(timeout=QR_SCAN_TIMEOUT):
                    print("[Error] No se escaneo el codigo QR dentro del tiempo permitido.")
                    return
                login_page.save_storage_state(STORAGE_STATE_PATH)

            # 6. Despacho del mensaje con Page Object Model (ChatPage) y Strategy Pattern
            chat_page = ChatPage(page)
            strategy = get_strategy(args.strategy)

            success = strategy.execute(
                chat_page=chat_page,
                phone=target_phone,
                message=message,
            )

            if success:
                print("\n================================================================")
                print(" [OK] PROCESO FINALIZADO CON EXITO: Mensaje enviado a WhatsApp Web ")
                print("================================================================")
            else:
                print("\n================================================================")
                print(" [ERROR] ADVERTENCIA: No se pudo confirmar la entrega del mensaje. ")
                print("================================================================")

            # 7. Persistencia final del storage_state
            login_page.save_storage_state(STORAGE_STATE_PATH)

        finally:
            context.close()
            if browser:
                browser.close()


if __name__ == "__main__":
    main()
