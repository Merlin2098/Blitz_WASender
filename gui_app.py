"""
Entrypoint de la aplicación GUI.
"""

import customtkinter as ctk

from src.application.browser_session import BrowserSessionService
from src.application.campaign_execution import CampaignExecutionService
from src.infrastructure.paths import AppPaths
from src.infrastructure.session_logging import close_session_logger, create_session_logger
from src.presentation.desktop import MainWindow, get_theme_manager


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main() -> int:
    paths = AppPaths(anchor_file=__file__)
    session_log = create_session_logger(
        nombre="gui_app",
        logs_dir=paths.get_logs_dir(),
        filename="gui_app.log",
        overwrite=True,
    )

    app = None
    try:
        app = MainWindow(
            logger=session_log.logger,
            paths=paths,
            browser_service=BrowserSessionService(),
            campaign_service_factory=CampaignExecutionService,
            theme_manager=get_theme_manager(default_theme="dark"),
        )
        app.mainloop()
        return 0
    finally:
        close_session_logger(session_log.logger, "Sesión de aplicación finalizada")
        if app is not None:
            try:
                app.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
