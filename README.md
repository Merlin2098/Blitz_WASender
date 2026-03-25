# Blitz WaSender

Blitz WaSender is a desktop application that automates bulk message delivery through WhatsApp Web using Selenium and a managed browser profile.

## 1. What It Is

This project provides a Windows-focused GUI for running controlled WhatsApp Web campaigns from an Excel workbook.

The application:

- reads message templates and contacts from Excel
- opens WhatsApp Web with an isolated browser profile
- validates session readiness before sending
- opens chats and sends prefilled messages automatically
- generates execution reports and session logs

The main desktop entrypoint is [`gui_app.py`](gui_app.py). The core application code lives in [`src/`](src), and static application assets live in [`src/resources/`](src/resources). A sample workbook for manual testing is available at [`docs/contactos.xlsx`](docs/contactos.xlsx).

## 2. How to Use This Project

### Clone the repository

```bash
git clone https://github.com/Merlin2098/Blitz_WASender.git
cd Blitz_WASender
```

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the desktop application

```bash
python gui_app.py
```

### Prepare WhatsApp Web before sending

1. Open the app.
2. Use `Configurar Perfil` to create the isolated browser profile if needed.
3. Use `Probar Navegador` to open WhatsApp Web with that managed profile.
4. Scan the QR code and confirm the session is fully loaded.
5. Load an Excel workbook such as [`docs/contactos.xlsx`](docs/contactos.xlsx).
6. Start a short sending test before running larger batches.

### Build the executable bundle

```bash
python build_executable.py
```

The build script generates an onedir PyInstaller bundle under `dist/BlitzWaSender`.

## 3. Architecture

The codebase follows a layered monolith structure inside [`src/`](src):

- `src/presentation`
  Handles the desktop UI, main window, user interactions, lazy loading, theming, notifications, and log panel rendering.
- `src/application`
  Coordinates use cases such as browser session setup and campaign execution.
- `src/domain`
  Defines core models and validation rules used across the application.
- `src/infrastructure`
  Contains filesystem paths, session logging, browser factory, Excel I/O, power management, and WhatsApp Web automation.
- `src/infrastructure/whatsapp_web`
  Centralizes DOM locators and browser automation against WhatsApp Web so selector changes are isolated in one place.

Supporting project areas:

- `utils/`
  Temporary compatibility wrappers that re-export from `src/`.
- `scripts/`
  Maintenance and diagnostic tools for opening the managed browser profile and recording manual WhatsApp Web sessions.
- `tests/`
  Unit tests for paths, browser setup, session logging, controller flow, campaign execution, and WhatsApp Web locators.

Repository tree map:

```text
Blitz_WASender/
├── gui_app.py
├── build_executable.py
├── requirements.txt
├── src/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   │   └── whatsapp_web/
│   ├── presentation/
│   │   └── desktop/
│   └── resources/
├── scripts/
├── tests/
├── utils/
├── docs/
│   ├── adr/
│   └── contactos.xlsx
├── logs/
└── perfiles/
```

Operational notes:

- GUI session logs are written to a fixed file: `logs/gui_app.log`
- the file is overwritten on each application start
- browser profiles are kept under `perfiles/<browser>`
- the executable bundle is generated with [`build_executable.py`](build_executable.py)

## 4. What Problem It Solves

WhatsApp Web bulk messaging workflows are fragile when handled manually or through ad hoc browser automation. This project addresses that by giving operators a repeatable process for sending large batches of messages from structured input data.

It solves three practical problems:

- **Operational scale**
  It removes the need to open chats one by one and paste messages manually.
- **Controlled browser automation**
  It uses an isolated Selenium profile so the automation session can be configured, diagnosed, and maintained independently from the user’s personal browser profile.
- **Resilience to WhatsApp Web changes**
  The WhatsApp Web integration is encapsulated under `src/infrastructure/whatsapp_web`, which makes DOM-related fixes faster when selectors change.

In short, Blitz WaSender turns a repetitive, error-prone WhatsApp Web sending process into a structured desktop workflow with logging, diagnostics, and maintainable automation boundaries.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
