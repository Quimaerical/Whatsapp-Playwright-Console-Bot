"""Configuración centralizada para el Bot de WhatsApp con Playwright."""

from pathlib import Path

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent
AUTH_DIR = BASE_DIR / "auth"
STORAGE_STATE_PATH = AUTH_DIR / "storage_state.json"
USER_DATA_DIR = AUTH_DIR / "user_data"

# URLs de WhatsApp Web
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
WHATSAPP_SEND_URL_TEMPLATE = "https://web.whatsapp.com/send?phone={phone}&text={text}"

# Tiempos de espera (milisegundos)
DEFAULT_SLOW_MO = 500
PAGE_LOAD_TIMEOUT = 60_000
QR_SCAN_TIMEOUT = 120_000
MESSAGE_SEND_TIMEOUT = 45_000
ELEMENT_TIMEOUT = 25_000

# Selectores CSS / Aria de WhatsApp Web
SELECTORS = {
    # Pantalla de Login / QR
    "qr_canvas": 'canvas[aria-label*="Scan"], div[data-ref]',
    "login_wrapper": 'div[data-ref], [data-testid="qrcode"]',
    
    # Pantalla Principal (Sesión Iniciada)
    "chat_list": 'div[id="side"], div[aria-label="Chat list"], div[aria-label="Lista de chats"], [data-testid="chat-list"]',
    
    # Búsqueda de Contacto
    "search_input": 'div[contenteditable="true"][data-tab="3"], div[aria-label*="Buscar"], div[aria-label*="Search"]',
    
    # Ventana de Chat & Enviar
    "chat_input": 'footer div[contenteditable="true"][data-tab="10"], footer div[contenteditable="true"], div[aria-placeholder*="mensaje"]',
    "send_button": 'button span[data-icon="send"], span[data-icon="send"], button[aria-label*="Enviar"], button[aria-label*="Send"]',
    
    # Verificación de Mensaje Enviado (Ticks de entrega o mensaje saliente)
    "sent_message": 'span[data-icon="msg-dblcheck"], span[data-icon="msg-check"], span[data-icon="msg-time"], div.message-out',
    "invalid_phone_popup": 'div[data-animate-modal-popup="true"]',
}

# Credenciales en Keyring
KEYRING_SERVICE = "whatsapp_bot"
KEYRING_PHONE_KEY = "target_phone"
