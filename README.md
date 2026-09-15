# Bot de WhatsApp con Playwright y Patrones de Diseño

Proyecto desarrollado para automatizar el envío de mensajes por **WhatsApp Web** utilizando **Python**, **Playwright** y gestión de dependencias con **PDM**. El diseño del bot aplica rigurosamente 3 patrones de diseño clásicos (**Builder**, **Page Object Model** y **Strategy**), cuenta con **persistencia de sesión** mediante `storage_state` y almacena el número de destino de forma segura usando **Keyring**.

---

## Objetivo de la Tarea

Enviar un mensaje automático por WhatsApp Web notificando la culminación del proceso y listando los patrones utilizados:

```text
Tarea finalizada.
Patrones utilizados: Builder, Page Object Model, Strategy.
```

---

## Patrones de Diseño Implementados

Siguiendo la metodología del **Taller RPA 2**, el proyecto se estructura en componentes desacoplados:

### 1. Builder (`core/browser_builder.py` y `utils/message_builder.py`)
- **`BrowserBuilder`**: Construye el navegador y el contexto de Playwright mediante métodos encadenables y fluidos:
  ```python
  BrowserBuilder(playwright)\
      .with_type("chromium")\
      .headless(False)\
      .slow_mo(500)\
      .with_user_data_dir(USER_DATA_DIR)\
      .with_storage_state(STORAGE_STATE_PATH)\
      .build()
  ```
  *Ventaja*: Permite añadir configuraciones (viewport, argumentos anti-detección, rutas de sesión) sin modificar la firma ni romper la compatibilidad.
- **`MessageBuilder`**: Constructor que garantiza el formato exacto del mensaje requerido para la entrega.

### 2. Page Object Model (`pages/`)
Separa la lógica de negocio de los selectores y la interacción con el DOM de WhatsApp Web:
- **`BasePage`** (`pages/base_page.py`): Métodos de navegación, esperas explícitas, clics y teclado.
- **`LoginPage`** (`pages/login_page.py`): Encapsula la detección del código QR, la verificación de sesión iniciada (`is_logged_in`) y la exportación del estado de sesión (`save_storage_state`).
- **`ChatPage`** (`pages/chat_page.py`): Encapsula la apertura de la conversación, el tipeo con soporte de saltos de línea (`Shift+Enter`), el botón de envío y la verificación de entrega del mensaje.

### 3. Strategy (`strategies/send_strategies.py`)
Permite intercambiar el mecanismo de envío sin duplicar lógica de despacho ni verificación:
- **`BaseSendStrategy`**: Define la plantilla del algoritmo (`execute`) que prepara el chat, despacha el mensaje y valida su entrega. Cero código repetido.
- **`DirectUrlStrategy`**: Abre la conversación directamente mediante la URL oficial `web.whatsapp.com/send?phone=...`.
- **`SearchContactStrategy`**: Utiliza el buscador interactivo de WhatsApp Web para encontrar el contacto o número y abrir el chat.

---

## Persistencia de Sesión (storage_state)

La tarea exige:
- **Primera ejecución:** Muestra el código QR para ser escaneado con la app de WhatsApp móvil. Al detectar el inicio de sesión, guarda el `storage_state` en `auth/storage_state.json`.
- **Segunda ejecución en adelante:** Detecta el archivo `auth/storage_state.json` y el contexto persistente, carga la sesión guardada y salta el escaneo del código QR, enviando el mensaje inmediatamente.

> **Nota técnica:** WhatsApp Web utiliza claves criptográficas en `IndexedDB` además de `localStorage`. El proyecto integra el guardado y carga explícita de `storage_state.json` junto con el directorio persistente (`auth/user_data`), asegurando que la sesión persista de forma real y estable.

---

## Gestión de Credenciales con Keyring

Para evitar almacenar el número de teléfono en texto plano en el código:
- Se utiliza la librería **Keyring** (`utils/credentials.py`).
- En la primera ejecución, si no hay un número guardado, el bot lo solicita interactivamente por consola (ej. `+5491123456789`) y lo almacena de forma segura en el llavero de credenciales del sistema operativo.
- En las siguientes ejecuciones, el bot recupera el número automáticamente del llavero.

---

## Estructura del Proyecto

```text
proyecto 2/
├── .gitignore              # Ignora auth/, .venv/ y archivos de sesión
├── pyproject.toml          # Configuración del proyecto y dependencias PDM
├── pdm.lock                # Bloqueo determinista de versiones
├── README.md               # Documentación completa
├── run_bot.bat             # Script de ejecución para Windows (con pause)
├── run_bot.sh              # Script de ejecución para Linux/macOS
├── config.py               # Constantes, selectores y rutas del proyecto
├── main.py                 # Orquestador principal del bot
├── core/
│   ├── __init__.py
│   └── browser_builder.py  # [Patrón Builder] Construcción de Browser/Context
├── pages/                  # [Patrón Page Object Model]
│   ├── __init__.py
│   ├── base_page.py        # POM Base
│   ├── login_page.py       # POM Login y Código QR
│   └── chat_page.py        # POM Conversación y Envíos
├── strategies/             # [Patrón Strategy]
│   ├── __init__.py
│   └── send_strategies.py  # BaseSendStrategy, DirectUrlStrategy, SearchContactStrategy
├── utils/
│   ├── __init__.py
│   ├── credentials.py      # Gestión de teléfono con Keyring
│   └── message_builder.py  # [Patrón Builder] Constructor del mensaje
└── tests/                  # Pruebas unitarias
    ├── __init__.py
    ├── test_builder.py
    ├── test_credentials.py
    └── test_strategies.py
```

---

## Requisitos e Instalación

### Requisitos Previos
- Python 3.10 o superior.
- [PDM](https://pdm-project.org/) instalado en el sistema (`pipx install pdm` o `pip install --user pdm`).

### Instalación de Dependencias
```bash
# Instalar dependencias con PDM
pdm install

# Instalar los binarios del navegador de Playwright
pdm run playwright install chromium
```

---

## Ejecución

### En Windows (Requisito de la Tarea)
Haz doble clic en el archivo `run_bot.bat` o ejecútalo desde CMD/PowerShell:
```cmd
run_bot.bat
```
*(El archivo `.bat` incluye `pause` al final para mantener abierta la consola y revisar los resultados).*

### En Linux / macOS
```bash
./run_bot.sh
```
O directamente con PDM:
```bash
pdm run python main.py
```

### Opciones de Línea de Comandos
```bash
# Enviar un mensaje personalizado directamente por CLI
pdm run python main.py --message "Hola! Este es un mensaje de prueba personalizado."

# O de forma abreviada con saltos de línea (\n)
pdm run python main.py -m "Línea 1\nLínea 2"

# Especificar o actualizar el número de destino directamente
pdm run python main.py --phone +5491123456789

# Usar la estrategia de búsqueda interactiva en lugar de URL directa
pdm run python main.py --strategy search

# Ejecución en segundo plano (headless, solo para sesiones ya autenticadas)
pdm run python main.py --headless

# Reiniciar la sesión guardada para forzar un nuevo escaneo de QR
pdm run python main.py --reset-session

# Eliminar el número guardado en Keyring
pdm run python main.py --reset-phone
```

> **Personalización interactiva en terminal:** Si ejecutas el bot sin el parámetro `--message`, te mostrará el mensaje por defecto en pantalla. Si presionas `Enter`, se enviará el mensaje por defecto. Si escribes un texto nuevo y presionas `Enter`, enviará tu texto personalizado.

---

## Pruebas Automatizadas

El proyecto incluye tests unitarios para validar los builders, las estrategias y la gestión de credenciales con Keyring:

```bash
pdm run python -m unittest discover -s tests
```

---

## Cumplimiento de Criterios de Evaluación

| Criterio | Estado | Detalle |
| :--- | :---: | :--- |
| **Envío correcto del mensaje** | Cumplido | Formato exacto con Builder: *"Tarea finalizada. Patrones utilizados: Builder, Page Object Model, Strategy."* |
| **Persistencia de sesión** | Cumplido | Guarda y carga `auth/storage_state.json`. En la 2da ejecución no solicita escanear el QR. |
| **Gestión con PDM** | Cumplido | `pyproject.toml` y `pdm.lock` con dependencias `playwright` y `keyring`. |
| **Ejecución con `.bat`** | Cumplido | `run_bot.bat` operativo con comando `pause` para no cerrar la consola. |
| **Uso de Keyring** | Cumplido | Número de teléfono almacenado en el llavero del sistema operativo sin texto plano. |
| **Patrones de Diseño** | Cumplido | **Builder** (`BrowserBuilder` / `MessageBuilder`), **POM** (`LoginPage` / `ChatPage`), **Strategy** (`DirectUrlStrategy` / `SearchContactStrategy`). |
