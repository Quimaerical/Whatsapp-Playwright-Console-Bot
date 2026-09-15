"""Gestión de credenciales del número de teléfono destino utilizando la librería Keyring."""

from __future__ import annotations

import re
import sys
import keyring
from config import KEYRING_SERVICE, KEYRING_PHONE_KEY


# ─── PHONE SANITIZATION & NORMALIZATION ───────────────────────────────────────

def normalize_phone(phone: str) -> str:
    """Limpia y valida un número de teléfono, removiendo espacios, guiones y paréntesis."""
    has_plus = phone.strip().startswith("+")
    digits = re.sub(r"\D", "", phone)
    if not digits:
        raise ValueError("El número de teléfono ingresado no contiene dígitos válidos.")

    return f"+{digits}" if has_plus else digits


# ─── KEYRING CRUD OPERATIONS ──────────────────────────────────────────────────

def get_stored_phone() -> str | None:
    """Recupera el número de teléfono almacenado en el llavero del sistema operativo."""
    try:
        phone = keyring.get_password(KEYRING_SERVICE, KEYRING_PHONE_KEY)
        return phone.strip() if phone else None
    except Exception as e:
        print(f"[Keyring] Advertencia: No se pudo leer del llavero ({e})")
        return None


def store_phone(phone: str) -> str:
    """Guarda el número de teléfono normalizado en el llavero seguro del sistema."""
    clean_phone = normalize_phone(phone)
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_PHONE_KEY, clean_phone)
        print(f"[Keyring] Número guardado de forma segura en el llavero: {clean_phone}")
    except Exception as e:
        print(f"[Keyring] Error al guardar en el llavero ({e})")

    return clean_phone


def delete_stored_phone() -> bool:
    """Elimina el número de teléfono almacenado en el llavero."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_PHONE_KEY)
        print("[Keyring] Número eliminado exitosamente del llavero.")
        return True
    except Exception:
        return False


# ─── PHONE RESOLUTION FLOW ────────────────────────────────────────────────────

def resolve_target_phone(provided_phone: str | None = None, interactive: bool = True) -> str:
    """Determina el número de destino a utilizar.
    
    1. Si se provee explícitamente vía argumento, lo guarda y utiliza.
    2. Si existe un número en Keyring, solicita confirmación interactiva.
    3. Si no existe, lo solicita por consola y lo almacena de forma persistente.
    """
    if provided_phone:
        return store_phone(provided_phone)

    stored = get_stored_phone()

    if stored:
        if not interactive:
            return stored

        print(f"\n[Keyring] Número encontrado en el llavero: {stored}")
        try:
            choice = input("¿Deseas enviar el mensaje a este número? [S/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nOperación cancelada por el usuario.")
            sys.exit(0)

        if choice in ("", "s", "si", "y", "yes"):
            return stored

    print("\n[Keyring] Configuración del número de WhatsApp de destino:")
    print("Ejemplo de formato: +5491123456789 o 5491123456789 (incluir código de país)")

    while True:
        try:
            user_input = input("Ingresa el número de teléfono: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperación cancelada.")
            sys.exit(0)

        try:
            return store_phone(user_input)
        except ValueError as err:
            print(f"Error: {err}. Intenta nuevamente.")
