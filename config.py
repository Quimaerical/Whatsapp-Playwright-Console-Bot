"""Configuración centralizada para el Bot de WhatsApp con Playwright."""

from __future__ import annotations

from pathlib import Path


# ─── PATHS & STORAGE ──────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
AUTH_DIR = BASE_DIR / "auth"
STORAGE_STATE_PATH = AUTH_DIR / "storage_state.json"
USER_DATA_DIR = AUTH_DIR / "user_data"


# ─── ENDPOINTS & URL TEMPLATES ────────────────────────────────────────────────

WHATSAPP_WEB_URL = "https://web.whatsapp.com"
WHATSAPP_SEND_URL_TEMPLATE = "https://web.whatsapp.com/send?phone={phone}&text={text}"


# ─── TIMEOUTS & LATENCY (MILLISECONDS) ────────────────────────────────────────

DEFAULT_SLOW_MO = 500
PAGE_LOAD_TIMEOUT = 60_000
QR_SCAN_TIMEOUT = 120_000
MESSAGE_SEND_TIMEOUT = 12_000
ELEMENT_TIMEOUT = 25_000


# ─── DOM SELECTORS (CSS & ARIA) ───────────────────────────────────────────────

SELECTORS = {
    # Pantalla de Login / QR
    "qr_canvas": 'canvas[aria-label*="Scan"], div[data-ref], [data-testid="qrcode"]',
    "login_wrapper": 'div[data-ref], [data-testid="qrcode"]',

    # Pantalla Principal (Sesión Iniciada)
    "chat_list": 'div[id="side"], div[aria-label="Chat list"], div[aria-label="Lista de chats"], [data-testid="chat-list"]',

    # Panel de Conversación Activa
    "main_chat": '#main, [data-testid="conversation-panel-wrapper"]',

    # Búsqueda de Contacto
    "search_input": (
        'div[data-testid="chat-list-search"], '
        'div[contenteditable="true"][data-tab="3"], '
        'div[aria-label*="Buscar"], '
        'div[aria-label*="Search"]'
    ),

    # Ventana de Chat & Entrada de Texto
    "chat_input": (
        'div[data-testid="conversation-compose-box-input"], '
        'footer div[contenteditable="true"][role="textbox"], '
        'footer div[contenteditable="true"], '
        'div[aria-placeholder*="mensaje"]'
    ),

    # Botón Enviar (visible únicamente cuando hay texto en la caja)
    "send_button": (
        'button[data-testid="compose-btn-send"], '
        '[data-testid="send"], '
        'button:has(span[data-icon="send"]), '
        'span[data-icon="send"], '
        'button[aria-label*="Enviar"], '
        'button[aria-label*="Send"]'
    ),

    # Botón de Micrófono (aparece cuando la caja de texto queda vacía)
    "mic_button": (
        'button[data-testid="audio-btn-ptt"], '
        'button:has(span[data-icon="ptt"]), '
        'span[data-icon="ptt"], '
        'span[data-icon="audio-mic"]'
    ),

    # Indicadores Universales de Entrega y Estado
    "sent_message": (
        '[data-testid="msg-dblcheck"], '
        '[data-testid="msg-check"], '
        '[data-testid="msg-time"], '
        '[data-testid="status-check"], '
        '[aria-label*="Enviado"], '
        '[aria-label*="Entregado"], '
        '[aria-label*="Sent"], '
        '[aria-label*="Delivered"], '
        'span[data-icon*="check"], '
        'span[data-icon="msg-time"], '
        'div[data-id^="true_"]'
    ),

    "invalid_phone_popup": 'div[data-animate-modal-popup="true"]',
}



# ─── KEYRING CREDENTIALS ──────────────────────────────────────────────────────

KEYRING_SERVICE = "whatsapp_bot"
KEYRING_PHONE_KEY = "target_phone"
