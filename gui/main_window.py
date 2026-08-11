import sys

from gui.jarvis_orb import JarvisOrb
from gui.settings_page import SettingsPage
from gui.help_page import HelpPage
from gui.theme_manager import load_theme

from core.ai_mode import get_ai_mode_label

from core.ui_state import (
    get_state,
    ui_state,
    submit_text_input
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QInputDialog
)


class JarvisWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.resize(1100, 700)

        self.settings_window = None
        self.help_window = None

        self.theme = load_theme()

        self.build_ui()
        self.apply_theme()

        # =========================
        # STATE TIMER
        # =========================

        self.state_timer = QTimer(self)

        self.state_timer.timeout.connect(
            self.update_jarvis_state
        )

        self.state_timer.start(100)

        # =========================
        # THEME TIMER
        # =========================

        self.theme_timer = QTimer(self)

        self.theme_timer.timeout.connect(
            self.check_theme
        )

        self.theme_timer.start(500)

        # =========================
        # SHUTDOWN SIGNAL
        # =========================

        ui_state.shutdown_requested.connect(
            self.shutdown_gui
        )

        # =========================
        # TEXT INPUT SIGNAL
        # =========================

        ui_state.text_input_requested.connect(
            self.request_text_input
        )


    # =========================
    # BUILD UI
    # =========================

    def build_ui(self):

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
            20
        )

        # =========================
        # TOP BAR
        # =========================

        top_bar = QHBoxLayout()

        self.help_button = QPushButton("?")

        self.help_button.setFixedSize(
            42,
            42
        )

        self.help_button.setToolTip(
            "Help"
        )

        self.help_button.clicked.connect(
            self.open_help
        )

        self.settings_button = QPushButton("⚙")

        self.settings_button.setFixedSize(
            42,
            42
        )

        self.settings_button.setToolTip(
            "Settings"
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

        top_bar.addWidget(
            self.help_button,
            alignment=Qt.AlignLeft
        )

        top_bar.addStretch()

        top_bar.addWidget(
            self.settings_button,
            alignment=Qt.AlignRight
        )

        main_layout.addLayout(
            top_bar
        )

        main_layout.addStretch()

        # =========================
        # AI MODE
        # =========================

        self.mode_label = QLabel(
            get_ai_mode_label()
        )

        self.mode_label.setAlignment(
            Qt.AlignCenter
        )

        mode_font = QFont()
        mode_font.setPointSize(12)
        mode_font.setBold(True)

        self.mode_label.setFont(
            mode_font
        )

        main_layout.addWidget(
            self.mode_label
        )

        # =========================
        # JARVIS ORB
        # =========================

        self.core = JarvisOrb()

        self.core.setFixedSize(
            420,
            420
        )

        main_layout.addWidget(
            self.core,
            alignment=Qt.AlignCenter
        )

        # =========================
        # STATUS
        # =========================

        self.status_label = QLabel(
            "IDLE"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)

        self.status_label.setFont(
            status_font
        )

        main_layout.addWidget(
            self.status_label
        )

        main_layout.addStretch()


    # =========================
    # LIVE JARVIS STATE
    # =========================

    def update_jarvis_state(self):

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


    # =========================
    # SETTINGS
    # =========================

    def open_settings(self):

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


    # =========================
    # HELP
    # =========================

    def open_help(self):

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


    # =========================
    # TEXT INPUT
    # =========================

    def request_text_input(
        self,
        title,
        message
    ):

        text, accepted = QInputDialog.getText(
            self,
            title,
            message
        )

        if accepted:
            submit_text_input(
                text.strip()
            )

        else:
            submit_text_input("")


    # =========================
    # THEME
    # =========================

    def apply_theme(self):

        background = self.theme[
            "color_1"
        ]

        accent = self.theme[
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
                font-size: 20px;
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
            """
        )

        self.core.set_theme(
            background,
            accent
        )


    def check_theme(self):

        new_theme = load_theme()

        if new_theme != self.theme:

            self.theme = new_theme

            self.apply_theme()


    # =========================
    # SHUTDOWN
    # =========================

    def shutdown_gui(self):

        print(
            "Closing JARVIS GUI..."
        )

        app = QApplication.instance()

        if app is not None:
            app.quit()


def start_gui():

    app = QApplication(
        sys.argv
    )

    window = JarvisWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    start_gui()