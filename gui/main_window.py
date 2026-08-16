import os
import subprocess
import sys

from PySide6.QtCore import (
    Qt,
    QTimer,
)

from PySide6.QtGui import (
    QAction,
    QFont,
)

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from core.ai_mode import (
    get_ai_mode_label,
)

from core.overlay_manager import (
    overlay_signals,
)

from core.ui_state import (
    get_state,
    submit_text_input,
    ui_state,
)

from gui.help_page import HelpPage
from gui.jarvis_orb import JarvisOrb
from gui.overlay_window import OverlayWindow
from gui.settings_page import SettingsPage

from gui.theme_manager import (
    load_theme,
    theme_bus,
)


class JarvisWindow(QMainWindow):

    def __init__(
        self
    ):
        super().__init__()

        self.setWindowTitle(
            "JARVIS"
        )

        self.resize(
            1100,
            700,
        )

        self.allow_full_exit = False
        self.tray_message_shown = False

        self.settings_window = None
        self.help_window = None
        self.overlay_window = None

        self.theme = load_theme()

        app = QApplication.instance()

        if app is not None:
            app.setQuitOnLastWindowClosed(
                False
            )

        # =====================================================
        # BUILD UI
        # =====================================================

        self.build_ui()

        # =====================================================
        # OVERLAY SYSTEM
        # =====================================================

        self.setup_overlay()

        # =====================================================
        # THEME
        # =====================================================

        self.apply_theme(
            self.theme
        )

        # =====================================================
        # SYSTEM TRAY
        # =====================================================

        self.setup_system_tray()

        # =====================================================
        # STATE TIMER
        # =====================================================

        self.state_timer = QTimer(
            self
        )

        self.state_timer.timeout.connect(
            self.update_jarvis_state
        )

        self.state_timer.start(
            100
        )

        # =====================================================
        # SIGNALS
        # =====================================================

        ui_state.shutdown_requested.connect(
            self.shutdown_gui
        )

        ui_state.text_input_requested.connect(
            self.request_text_input
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(
        self
    ):
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        # =====================================================
        # TOP BAR
        # =====================================================

        top_bar = QHBoxLayout()

        self.help_button = QPushButton(
            "?"
        )

        self.help_button.setFixedSize(
            42,
            42,
        )

        self.help_button.setToolTip(
            "Help"
        )

        self.help_button.clicked.connect(
            self.open_help
        )

        self.settings_button = QPushButton(
            "⚙"
        )

        self.settings_button.setFixedSize(
            42,
            42,
        )

        self.settings_button.setToolTip(
            "Settings"
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

        top_bar.addWidget(
            self.help_button,
            alignment=Qt.AlignLeft,
        )

        top_bar.addStretch()

        top_bar.addWidget(
            self.settings_button,
            alignment=Qt.AlignRight,
        )

        main_layout.addLayout(
            top_bar
        )

        main_layout.addStretch()

        # =====================================================
        # AI MODE
        # =====================================================

        self.mode_label = QLabel(
            get_ai_mode_label()
        )

        self.mode_label.setAlignment(
            Qt.AlignCenter
        )

        mode_font = QFont()

        mode_font.setPointSize(
            12
        )

        mode_font.setBold(
            True
        )

        self.mode_label.setFont(
            mode_font
        )

        main_layout.addWidget(
            self.mode_label
        )

        # =====================================================
        # JARVIS ORB
        # =====================================================

        self.core = JarvisOrb()

        self.core.setFixedSize(
            420,
            420,
        )

        main_layout.addWidget(
            self.core,
            alignment=Qt.AlignCenter,
        )

        # =====================================================
        # STATUS
        # =====================================================

        self.status_label = QLabel(
            "IDLE"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        status_font = QFont()

        status_font.setPointSize(
            14
        )

        status_font.setBold(
            True
        )

        self.status_label.setFont(
            status_font
        )

        main_layout.addWidget(
            self.status_label
        )

        main_layout.addStretch()

        # =====================================================
        # BOTTOM BUTTON BAR
        # =====================================================

        bottom_bar = QHBoxLayout()

        self.quit_button = QPushButton(
            "QUIT"
        )

        self.quit_button.setFixedSize(
            120,
            42,
        )

        self.quit_button.setToolTip(
            "Completely exit JARVIS"
        )

        self.quit_button.clicked.connect(
            self.quit_jarvis
        )

        self.restart_button = QPushButton(
            "RESTART"
        )

        self.restart_button.setFixedSize(
            120,
            42,
        )

        self.restart_button.setToolTip(
            "Restart JARVIS"
        )

        self.restart_button.clicked.connect(
            self.restart_jarvis
        )

        bottom_bar.addWidget(
            self.quit_button,
            alignment=Qt.AlignLeft,
        )

        bottom_bar.addStretch()

        bottom_bar.addWidget(
            self.restart_button,
            alignment=Qt.AlignRight,
        )

        main_layout.addLayout(
            bottom_bar
        )

    # =========================================================
    # SCREEN OVERLAY
    # =========================================================

    def setup_overlay(
        self
    ):
        self.overlay_window = OverlayWindow()

        overlay_signals.show_center_requested.connect(
            self.overlay_window.show_center
        )

        overlay_signals.show_message_requested.connect(
            self.overlay_window.show_message
        )

        overlay_signals.show_highlight_requested.connect(
            self.overlay_window.show_highlight
        )

        overlay_signals.clear_requested.connect(
            self.overlay_window.clear_overlay
        )

        print(
            "JARVIS overlay system ready."
        )

    # =========================================================
    # SYSTEM TRAY
    # =========================================================

    def setup_system_tray(
        self
    ):
        self.tray_available = (
            QSystemTrayIcon.isSystemTrayAvailable()
        )

        if not self.tray_available:
            self.tray_icon = None

            return

        icon = self.style().standardIcon(
            QStyle.SP_ComputerIcon
        )

        self.setWindowIcon(
            icon
        )

        self.tray_icon = QSystemTrayIcon(
            icon,
            self,
        )

        self.tray_icon.setToolTip(
            "JARVIS"
        )

        tray_menu = QMenu(
            self
        )

        # =====================================================
        # OPEN JARVIS
        # =====================================================

        open_action = QAction(
            "Open JARVIS",
            self,
        )

        open_action.triggered.connect(
            self.restore_from_tray
        )

        tray_menu.addAction(
            open_action
        )

        # =====================================================
        # SETTINGS
        # =====================================================

        settings_action = QAction(
            "Settings",
            self,
        )

        settings_action.triggered.connect(
            self.open_settings_from_tray
        )

        tray_menu.addAction(
            settings_action
        )

        # =====================================================
        # HELP
        # =====================================================

        help_action = QAction(
            "Help",
            self,
        )

        help_action.triggered.connect(
            self.open_help_from_tray
        )

        tray_menu.addAction(
            help_action
        )

        tray_menu.addSeparator()

        # =====================================================
        # CLEAR OVERLAY
        # =====================================================

        clear_overlay_action = QAction(
            "Clear Overlay",
            self,
        )

        clear_overlay_action.triggered.connect(
            self.clear_overlay_from_tray
        )

        tray_menu.addAction(
            clear_overlay_action
        )

        tray_menu.addSeparator()

        # =====================================================
        # RESTART
        # =====================================================

        restart_action = QAction(
            "Restart JARVIS",
            self,
        )

        restart_action.triggered.connect(
            self.restart_jarvis
        )

        tray_menu.addAction(
            restart_action
        )

        # =====================================================
        # EXIT
        # =====================================================

        exit_action = QAction(
            "Exit JARVIS",
            self,
        )

        exit_action.triggered.connect(
            self.quit_jarvis
        )

        tray_menu.addAction(
            exit_action
        )

        self.tray_icon.setContextMenu(
            tray_menu
        )

        self.tray_icon.activated.connect(
            self.tray_icon_activated
        )

        self.tray_icon.show()

    # =========================================================
    # TRAY ACTIONS
    # =========================================================

    def tray_icon_activated(
        self,
        reason,
    ):
        if (
            reason
            == QSystemTrayIcon.DoubleClick
        ):
            self.restore_from_tray()

    def restore_from_tray(
        self
    ):
        self.showNormal()

        self.raise_()

        self.activateWindow()

    def open_settings_from_tray(
        self
    ):
        self.restore_from_tray()

        self.open_settings()

    def open_help_from_tray(
        self
    ):
        self.restore_from_tray()

        self.open_help()

    def clear_overlay_from_tray(
        self
    ):
        if self.overlay_window is not None:
            self.overlay_window.clear_overlay()

    # =========================================================
    # MAIN WINDOW CLOSE
    # =========================================================

    def closeEvent(
        self,
        event,
    ):
        # =====================================================
        # FULL EXIT ALLOWED
        # =====================================================

        if self.allow_full_exit:
            event.accept()

            return

        # =====================================================
        # NO SYSTEM TRAY
        # =====================================================

        if not self.tray_available:
            event.accept()

            return

        # =====================================================
        # MINIMIZE TO TRAY
        # =====================================================

        event.ignore()

        self.hide()

        # Close settings so wake blocking is removed.
        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
        ):
            self.settings_window.close()

        # Close help so wake blocking is removed.
        if (
            self.help_window is not None
            and self.help_window.isVisible()
        ):
            self.help_window.close()

        # Overlay should not remain stuck on screen.
        if self.overlay_window is not None:
            self.overlay_window.clear_overlay()

        if (
            self.tray_icon is not None
            and not self.tray_message_shown
        ):
            self.tray_icon.showMessage(
                "JARVIS",
                "JARVIS is still running in the background.",
                QSystemTrayIcon.Information,
                4000,
            )

            self.tray_message_shown = True

    # =========================================================
    # QUIT JARVIS
    # =========================================================

    def quit_jarvis(
        self
    ):
        print(
            "Quitting JARVIS..."
        )

        self.allow_full_exit = True

        # =====================================================
        # CLOSE OVERLAY
        # =====================================================

        if self.overlay_window is not None:
            try:
                self.overlay_window.clear_overlay()

                self.overlay_window.close()

            except Exception:
                pass

        # =====================================================
        # CLOSE SETTINGS
        # =====================================================

        if self.settings_window is not None:
            try:
                self.settings_window.close()

            except Exception:
                pass

        # =====================================================
        # CLOSE HELP
        # =====================================================

        if self.help_window is not None:
            try:
                self.help_window.close()

            except Exception:
                pass

        # =====================================================
        # HIDE TRAY
        # =====================================================

        if self.tray_icon is not None:
            try:
                self.tray_icon.hide()

            except Exception:
                pass

        # =====================================================
        # EXIT APPLICATION
        # =====================================================

        app = QApplication.instance()

        if app is not None:
            app.quit()

    # =========================================================
    # RESTART JARVIS
    # =========================================================

    def restart_jarvis(
        self
    ):
        print(
            "Restarting JARVIS..."
        )

        try:
            # =================================================
            # PACKAGED JARVIS.EXE
            # =================================================

            if getattr(
                sys,
                "frozen",
                False,
            ):
                command = [
                    sys.executable
                ]

                working_directory = (
                    os.path.dirname(
                        sys.executable
                    )
                )

            # =================================================
            # DEVELOPMENT MODE
            # =================================================

            else:
                project_root = (
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(
                                __file__
                            )
                        )
                    )
                )

                main_file = os.path.join(
                    project_root,
                    "main.py",
                )

                command = [
                    sys.executable,
                    main_file,
                ]

                working_directory = (
                    project_root
                )

            # =================================================
            # START NEW INSTANCE
            # =================================================

            subprocess.Popen(
                command,
                cwd=working_directory,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if os.name == "nt"
                    else 0
                ),
            )

            # =================================================
            # CLOSE CURRENT INSTANCE
            # =================================================

            self.allow_full_exit = True

            if self.overlay_window is not None:
                try:
                    self.overlay_window.clear_overlay()

                    self.overlay_window.close()

                except Exception:
                    pass

            if self.tray_icon is not None:
                try:
                    self.tray_icon.hide()

                except Exception:
                    pass

            app = QApplication.instance()

            if app is not None:
                app.quit()

        except Exception as error:
            print(
                "JARVIS restart error:",
                error,
            )

    # =========================================================
    # JARVIS STATE
    # =========================================================

    def update_jarvis_state(
        self
    ):
        state = get_state()

        self.status_label.setText(
            state
        )

        self.core.set_state(
            state
        )

        self.mode_label.setText(
            get_ai_mode_label()
        )

        if self.tray_icon is not None:
            self.tray_icon.setToolTip(
                f"JARVIS — {state}"
            )

    # =========================================================
    # SETTINGS
    # =========================================================

    def open_settings(
        self
    ):
        if (
            self.settings_window is None
            or not self.settings_window.isVisible()
        ):
            self.settings_window = SettingsPage(
                self
            )

        self.settings_window.show()

        self.settings_window.raise_()

        self.settings_window.activateWindow()

    # =========================================================
    # HELP
    # =========================================================

    def open_help(
        self
    ):
        if (
            self.help_window is None
            or not self.help_window.isVisible()
        ):
            self.help_window = HelpPage(
                self
            )

        self.help_window.show()

        self.help_window.raise_()

        self.help_window.activateWindow()

    # =========================================================
    # TEXT INPUT
    # =========================================================

    def request_text_input(
        self,
        title,
        message,
    ):
        if not self.isVisible():
            self.restore_from_tray()

        text, accepted = (
            QInputDialog.getText(
                self,
                title,
                message,
            )
        )

        if accepted:
            submit_text_input(
                text.strip()
            )

        else:
            submit_text_input(
                ""
            )

    # =========================================================
    # THEME
    # =========================================================

    def on_theme_changed(
        self,
        theme,
    ):
        self.theme = (
            theme.copy()
        )

        self.apply_theme(
            self.theme
        )

    def apply_theme(
        self,
        theme,
    ):
        background = theme[
            "color_1"
        ]

        accent = theme[
            "color_2"
        ]

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {background};
            }}

            QWidget {{
                background-color: {background};
            }}

            QLabel {{
                color: {accent};
            }}

            QPushButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 20px;
                font-size: 16px;
            }}

            QPushButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QInputDialog {{
                background-color: {background};
            }}

            QLineEdit {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 6px;
                padding: 7px;
            }}

            QMenu {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                padding: 5px;
            }}

            QMenu::item {{
                padding: 7px 28px;
            }}

            QMenu::item:selected {{
                background-color: {accent};
                color: {background};
            }}
            """
        )

        self.core.set_theme(
            background,
            accent,
        )

    # =========================================================
    # ASSISTANT SHUTDOWN SIGNAL
    # =========================================================

    def shutdown_gui(
        self
    ):
        self.quit_jarvis()


# =============================================================
# START GUI
# =============================================================

def start_gui():
    app = QApplication(
        sys.argv
    )

    app.setQuitOnLastWindowClosed(
        False
    )

    window = JarvisWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    start_gui()