from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions


PROJECT_ROOT = Path(__file__).resolve().parents[1]

COMMON_EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def default_profile_dir() -> Path:
    return PROJECT_ROOT / "perfiles" / "edge"


def build_output_dir() -> Path:
    output_dir = PROJECT_ROOT / "logs" / "manual_action_recordings" / timestamp_slug()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def resolve_edge_path(custom_path: str | None) -> Path:
    candidates: list[Path] = []

    if custom_path:
        candidates.append(Path(custom_path))

    env_path = os.environ.get("EDGE_PATH")
    if env_path:
        candidates.append(Path(env_path))

    which_path = shutil.which("msedge")
    if which_path:
        candidates.append(Path(which_path))

    candidates.extend(COMMON_EDGE_PATHS)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("No se encontró msedge.exe. Usa --edge-path o define EDGE_PATH.")


def build_command(edge_path: Path, profile_dir: Path, args: argparse.Namespace) -> list[str]:
    command = [
        str(edge_path),
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        f"--remote-debugging-port={args.remote_debugging_port}",
    ]

    if args.new_window:
        command.append("--new-window")

    if args.start_maximized:
        command.append("--start-maximized")

    command.append(args.url)
    return command


def launch_edge(edge_path: Path, profile_dir: Path, args: argparse.Namespace) -> subprocess.Popen:
    command = build_command(edge_path, profile_dir, args)
    return subprocess.Popen(command)


def attach_to_edge(debug_port: int, attempts: int = 10, delay_seconds: int = 2):
    last_error = None
    for _ in range(attempts):
        try:
            options = EdgeOptions()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            driver = webdriver.Edge(options=options)
            return driver
        except Exception as exc:
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"No se pudo adjuntar a Edge por el puerto {debug_port}: {last_error}")


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def save_page_artifacts(driver, output_dir: Path, prefix: str) -> dict:
    screenshot_path = output_dir / f"{prefix}.png"
    html_path = output_dir / f"{prefix}.html"
    summary_path = output_dir / f"{prefix}_summary.json"

    driver.save_screenshot(str(screenshot_path))
    html_path.write_text(driver.page_source, encoding="utf-8")

    summary = driver.execute_script(
        """
        const bodyText = document.body ? document.body.innerText || '' : '';
        const inputs = Array.from(document.querySelectorAll('input, textarea')).slice(0, 20);
        const editables = Array.from(document.querySelectorAll("[contenteditable='true']")).slice(0, 20);
        return {
          title: document.title,
          url: window.location.href,
          readyState: document.readyState,
          hasPaneSide: !!document.querySelector('#pane-side'),
          hasMain: !!document.querySelector('#main'),
          hasFooter: !!document.querySelector('#main footer'),
          bodyTextSample: bodyText.slice(0, 1500),
          inputSnapshot: inputs.map((node) => ({
            tag: node.tagName,
            type: node.getAttribute('type'),
            value: (node.value || '').slice(0, 120),
            ariaLabel: node.getAttribute('aria-label'),
            placeholder: node.getAttribute('placeholder'),
            role: node.getAttribute('role'),
            dataTab: node.getAttribute('data-tab'),
          })),
          editableSnapshot: editables.map((node) => ({
            tag: node.tagName,
            text: (node.innerText || '').slice(0, 120),
            ariaLabel: node.getAttribute('aria-label'),
            role: node.getAttribute('role'),
            dataTab: node.getAttribute('data-tab'),
          })),
        };
        """
    )
    write_json(summary_path, summary)

    return {
        "screenshot": str(screenshot_path),
        "html": str(html_path),
        "summary": str(summary_path),
    }


def inject_recorder(driver, storage_key: str) -> dict:
    script = """
    const storageKey = arguments[0];

    function safeJsonParse(raw) {
      try { return JSON.parse(raw); } catch (e) { return []; }
    }

    function readLog() {
      return safeJsonParse(localStorage.getItem(storageKey) || '[]');
    }

    function writeLog(items) {
      localStorage.setItem(storageKey, JSON.stringify(items.slice(-1000)));
    }

    function cssPath(node) {
      if (!node || node.nodeType !== 1) return null;
      if (node.id) return '#' + node.id;
      const parts = [];
      let current = node;
      while (current && current.nodeType === 1 && parts.length < 6) {
        let part = current.tagName.toLowerCase();
        if (current.classList && current.classList.length) {
          part += '.' + Array.from(current.classList).slice(0, 3).join('.');
        }
        const parent = current.parentElement;
        if (parent) {
          const siblings = Array.from(parent.children).filter((el) => el.tagName === current.tagName);
          if (siblings.length > 1) {
            part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
          }
        }
        parts.unshift(part);
        current = parent;
      }
      return parts.join(' > ');
    }

    function targetInfo(node) {
      if (!node || node.nodeType !== 1) return {};
      return {
        tag: node.tagName,
        text: (node.innerText || node.value || '').slice(0, 120),
        cssPath: cssPath(node),
        id: node.id || null,
        className: typeof node.className === 'string' ? node.className.slice(0, 200) : null,
        role: node.getAttribute('role'),
        ariaLabel: node.getAttribute('aria-label'),
        title: node.getAttribute('title'),
        placeholder: node.getAttribute('placeholder'),
        dataTab: node.getAttribute('data-tab'),
        href: node.getAttribute('href'),
      };
    }

    function pushEvent(type, payload) {
      const items = readLog();
      items.push({
        timestamp: new Date().toISOString(),
        type,
        url: window.location.href,
        title: document.title,
        payload,
      });
      writeLog(items);
    }

    if (!window.__waDiagRecorderInstalled) {
      window.__waDiagRecorderInstalled = true;
      window.__waDiagStorageKey = storageKey;

      pushEvent('recorder_installed', {
        readyState: document.readyState,
        hasPaneSide: !!document.querySelector('#pane-side'),
        hasMain: !!document.querySelector('#main'),
      });

      document.addEventListener('click', (event) => {
        pushEvent('click', targetInfo(event.target));
      }, true);

      document.addEventListener('input', (event) => {
        const info = targetInfo(event.target);
        info.value = (event.target && event.target.value ? event.target.value : '').slice(0, 200);
        pushEvent('input', info);
      }, true);

      document.addEventListener('keydown', (event) => {
        pushEvent('keydown', {
          key: event.key,
          code: event.code,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          altKey: event.altKey,
          metaKey: event.metaKey,
          target: targetInfo(event.target),
        });
      }, true);

      document.addEventListener('focusin', (event) => {
        pushEvent('focusin', targetInfo(event.target));
      }, true);

      window.addEventListener('hashchange', () => {
        pushEvent('hashchange', { url: window.location.href });
      });

      window.addEventListener('beforeunload', () => {
        pushEvent('beforeunload', { url: window.location.href });
      });
    }

    return {
      installed: !!window.__waDiagRecorderInstalled,
      storageKey: storageKey,
      existingEvents: readLog().length,
      title: document.title,
      url: window.location.href,
    };
    """
    return driver.execute_script(script, storage_key)


def collect_actions(driver, storage_key: str) -> list[dict]:
    return driver.execute_script(
        """
        const storageKey = arguments[0];
        try {
          return JSON.parse(localStorage.getItem(storageKey) || '[]');
        } catch (e) {
          return [];
        }
        """,
        storage_key,
    )


def clear_actions(driver, storage_key: str) -> None:
    driver.execute_script("localStorage.removeItem(arguments[0]);", storage_key)


def wait_for_user() -> None:
    print()
    print("Acciones a realizar:")
    print("1. Usa la ventana de Edge para abrir o buscar un chat.")
    print("2. Escribe y envía manualmente un mensaje nuevo.")
    print("3. Cuando termines, vuelve a esta consola y presiona Enter.")
    input("Presiona Enter cuando hayas terminado la grabación manual... ")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lanza Edge con el perfil Selenium y graba acciones manuales para diagnóstico."
    )
    parser.add_argument("--edge-path", help="Ruta opcional a msedge.exe.")
    parser.add_argument("--profile-dir", help="Ruta opcional al perfil de Edge.")
    parser.add_argument("--url", default="https://web.whatsapp.com", help="URL inicial a abrir.")
    parser.add_argument("--remote-debugging-port", type=int, default=9222)
    parser.add_argument("--new-window", action="store_true")
    parser.add_argument("--start-maximized", action="store_true")
    parser.add_argument("--keep-browser-open", action="store_true")
    args = parser.parse_args()

    edge_path = resolve_edge_path(args.edge_path)
    profile_dir = Path(args.profile_dir).resolve() if args.profile_dir else default_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    output_dir = build_output_dir()
    storage_key = f"wa_diag_actions_{timestamp_slug()}"

    process = launch_edge(edge_path, profile_dir, args)
    driver = attach_to_edge(args.remote_debugging_port)

    try:
        time.sleep(5)
        clear_actions(driver, storage_key)
        recorder_info = inject_recorder(driver, storage_key)
        initial_artifacts = save_page_artifacts(driver, output_dir, "initial_state")

        print("Grabador listo.")
        print(f"PID Edge: {process.pid}")
        print(f"Perfil: {profile_dir}")
        print(f"Storage key: {storage_key}")
        print(f"Output dir: {output_dir}")
        print(f"URL actual: {recorder_info['url']}")
        print(f"Título actual: {recorder_info['title']}")

        wait_for_user()

        final_artifacts = save_page_artifacts(driver, output_dir, "final_state")
        actions = collect_actions(driver, storage_key)

        manifest = {
            "started_at": datetime.now().isoformat(),
            "edge_path": str(edge_path),
            "profile_dir": str(profile_dir),
            "pid": process.pid,
            "remote_debugging_port": args.remote_debugging_port,
            "storage_key": storage_key,
            "recorder_info": recorder_info,
            "action_count": len(actions),
            "initial_artifacts": initial_artifacts,
            "final_artifacts": final_artifacts,
        }

        write_json(output_dir / "actions.json", actions)
        write_json(output_dir / "manifest.json", manifest)

        print()
        print("Grabación finalizada.")
        print(f"Manifest: {output_dir / 'manifest.json'}")
        print(f"Actions:  {output_dir / 'actions.json'}")
        print(f"Final HTML: {output_dir / 'final_state.html'}")
        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass

        if not args.keep_browser_open:
            try:
                process.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
