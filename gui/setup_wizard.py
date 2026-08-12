import threading
import webbrowser

from PySide6.QtCore import (
    Qt,
    QObject,
    Signal
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QProgressBar,
    QMessageBox,
    QStackedWidget
)

from core.app_scanner import scan_apps

from core.gmail_manager import (
    get_gmail_service
)

from core.setup_manager import (
    get_required_models,
    gmail_connected,
    mark_setup_complete,
    model_installed,
    ollama_installed,
    pull_model
)

from core.voice_settings import (
    load_voice_settings,
    save_voice_settings
)

from gui.theme_manager import (
    load_theme,
    theme_bus
)


class SetupSignals(QObject):
    status = Signal(str)
    progress = Signal(int)

    ai_finished = Signal(bool)
    gmail_finished = Signal(bool)
    scan_finished = Signal(bool, int)


class SetupWizard(QWidget):

    finished = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "JARVIS First Run Setup"
        )

        self.resize(
            780,
            600
        )

        self.theme = load_theme()

        self.current_page = 0

        self.signals = SetupSignals()

        self.build_ui()
        self.connect_signals()

        self.apply_theme(
            self.theme
        )

        self.refresh_ai_status()
        self.refresh_gmail_status()


    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        self.title_label = QLabel(
            "WELCOME TO JARVIS"
        )

        self.title_label.setObjectName(
            "setupTitle"
        )

        self.title_label.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            self.title_label
        )

        self.step_label = QLabel()

        self.step_label.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            self.step_label
        )

        main_layout.addSpacing(
            15
        )

        self.pages = QStackedWidget()

        main_layout.addWidget(
            self.pages,
            1
        )

        self.build_welcome_page()
        self.build_ai_page()
        self.build_voice_page()
        self.build_gmail_page()
        self.build_apps_page()
        self.build_finish_page()

        # =========================
        # NAVIGATION
        # =========================

        navigation = QHBoxLayout()

        self.back_button = QPushButton(
            "← Back"
        )

        self.next_button = QPushButton(
            "Next →"
        )

        self.back_button.clicked.connect(
            self.previous_page
        )

        self.next_button.clicked.connect(
            self.next_page
        )

        navigation.addWidget(
            self.back_button
        )

        navigation.addStretch()

        navigation.addWidget(
            self.next_button
        )

        main_layout.addLayout(
            navigation
        )

        self.update_navigation()


    # =========================================================
    # PAGE 1 — WELCOME
    # =========================================================

    def build_welcome_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addStretch()

        heading = QLabel(
            "Meet JARVIS"
        )

        heading.setObjectName(
            "pageHeading"
        )

        heading.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            heading
        )

        text = QLabel(
            "This setup will prepare JARVIS for this PC.\n\n"
            "We will configure:\n\n"
            "• Local AI\n"
            "• Voice\n"
            "• Gmail\n"
            "• Installed applications\n\n"
            "Your personal settings will be stored "
            "inside your Windows user profile."
        )

        text.setAlignment(
            Qt.AlignCenter
        )

        text.setWordWrap(
            True
        )

        layout.addWidget(
            text
        )

        layout.addStretch()

        self.pages.addWidget(
            page
        )


    # =========================================================
    # PAGE 2 — AI
    # =========================================================

    def build_ai_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        heading = QLabel(
            "AI SETUP"
        )

        heading.setObjectName(
            "pageHeading"
        )

        layout.addWidget(
            heading
        )

        self.ollama_status = QLabel()
        self.normal_status = QLabel()
        self.think_status = QLabel()

        layout.addWidget(
            self.ollama_status
        )

        layout.addWidget(
            self.normal_status
        )

        layout.addWidget(
            self.think_status
        )

        layout.addSpacing(
            15
        )

        self.ai_status = QLabel()

        self.ai_status.setWordWrap(
            True
        )

        layout.addWidget(
            self.ai_status
        )

        self.ai_progress = QProgressBar()

        self.ai_progress.setRange(
            0,
            100
        )

        layout.addWidget(
            self.ai_progress
        )

        layout.addStretch()

        buttons = QHBoxLayout()

        self.get_ollama_button = QPushButton(
            "Get Ollama"
        )

        self.ai_refresh_button = QPushButton(
            "Refresh"
        )

        self.install_models_button = QPushButton(
            "Install Missing Models"
        )

        self.get_ollama_button.clicked.connect(
            self.open_ollama
        )

        self.ai_refresh_button.clicked.connect(
            self.refresh_ai_status
        )

        self.install_models_button.clicked.connect(
            self.start_ai_install
        )

        buttons.addWidget(
            self.get_ollama_button
        )

        buttons.addWidget(
            self.ai_refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.install_models_button
        )

        layout.addLayout(
            buttons
        )

        self.pages.addWidget(
            page
        )


    # =========================================================
    # PAGE 3 — VOICE
    # =========================================================

    def build_voice_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        heading = QLabel(
            "VOICE SETUP"
        )

        heading.setObjectName(
            "pageHeading"
        )

        layout.addWidget(
            heading
        )

        description = QLabel(
            "Choose how JARVIS should speak.\n\n"
            "Piper is free and runs locally.\n"
            "ElevenLabs uses your own API key."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        settings = load_voice_settings()

        layout.addSpacing(
            15
        )

        provider_row = QHBoxLayout()

        provider_row.addWidget(
            QLabel(
                "Voice Provider"
            )
        )

        self.voice_provider = QComboBox()

        self.voice_provider.addItem(
            "Piper — Free / Local",
            "piper"
        )

        self.voice_provider.addItem(
            "ElevenLabs",
            "elevenlabs"
        )

        current_provider = settings.get(
            "provider",
            "piper"
        )

        index = self.voice_provider.findData(
            current_provider
        )

        if index >= 0:
            self.voice_provider.setCurrentIndex(
                index
            )

        provider_row.addWidget(
            self.voice_provider
        )

        layout.addLayout(
            provider_row
        )

        self.api_key_label = QLabel(
            "ElevenLabs API Key"
        )

        self.api_key_input = QLineEdit()

        self.api_key_input.setEchoMode(
            QLineEdit.Password
        )

        self.api_key_input.setText(
            settings.get(
                "elevenlabs_api_key",
                ""
            )
        )

        self.api_key_input.setPlaceholderText(
            "Enter your ElevenLabs API key"
        )

        layout.addWidget(
            self.api_key_label
        )

        layout.addWidget(
            self.api_key_input
        )

        self.voice_id_label = QLabel(
            "ElevenLabs Voice ID"
        )

        self.voice_id_input = QLineEdit()

        self.voice_id_input.setText(
            settings.get(
                "elevenlabs_voice_id",
                "nPczCjzI2devNBz1zQrb"
            )
        )

        layout.addWidget(
            self.voice_id_label
        )

        layout.addWidget(
            self.voice_id_input
        )

        self.voice_provider.currentIndexChanged.connect(
            self.update_voice_fields
        )

        save_button = QPushButton(
            "Save Voice Settings"
        )

        save_button.clicked.connect(
            self.save_voice_page
        )

        layout.addWidget(
            save_button
        )

        layout.addStretch()

        self.pages.addWidget(
            page
        )

        self.update_voice_fields()


    # =========================================================
    # PAGE 4 — GMAIL
    # =========================================================

    def build_gmail_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        heading = QLabel(
            "GMAIL SETUP"
        )

        heading.setObjectName(
            "pageHeading"
        )

        layout.addWidget(
            heading
        )

        description = QLabel(
            "Connect Gmail if you want JARVIS "
            "to send emails for you.\n\n"
            "This is optional and can be configured later."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            20
        )

        self.gmail_status_label = QLabel()

        layout.addWidget(
            self.gmail_status_label
        )

        self.gmail_connect_button = QPushButton(
            "Connect Gmail"
        )

        self.gmail_connect_button.clicked.connect(
            self.connect_gmail
        )

        layout.addWidget(
            self.gmail_connect_button
        )

        layout.addStretch()

        self.pages.addWidget(
            page
        )


    # =========================================================
    # PAGE 5 — APPS
    # =========================================================

    def build_apps_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        heading = QLabel(
            "APPLICATION SCAN"
        )

        heading.setObjectName(
            "pageHeading"
        )

        layout.addWidget(
            heading
        )

        description = QLabel(
            "JARVIS can scan this PC for applications "
            "so voice commands such as \"Open Chrome\" "
            "can be configured later."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        self.app_scan_status = QLabel(
            "Application scan has not been run yet."
        )

        self.app_scan_status.setWordWrap(
            True
        )

        layout.addWidget(
            self.app_scan_status
        )

        self.scan_apps_button = QPushButton(
            "Scan Installed Apps"
        )

        self.scan_apps_button.clicked.connect(
            self.start_app_scan
        )

        layout.addWidget(
            self.scan_apps_button
        )

        layout.addStretch()

        self.pages.addWidget(
            page
        )


    # =========================================================
    # PAGE 6 — FINISH
    # =========================================================

    def build_finish_page(self):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.addStretch()

        heading = QLabel(
            "JARVIS IS READY"
        )

        heading.setObjectName(
            "pageHeading"
        )

        heading.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            heading
        )

        text = QLabel(
            "Initial setup is complete.\n\n"
            "You can change AI models, contacts, "
            "apps, appearance, and other settings "
            "later from the Settings menu."
        )

        text.setAlignment(
            Qt.AlignCenter
        )

        text.setWordWrap(
            True
        )

        layout.addWidget(
            text
        )

        self.finish_setup_button = QPushButton(
            "Launch JARVIS"
        )

        self.finish_setup_button.clicked.connect(
            self.finish_setup
        )

        layout.addWidget(
            self.finish_setup_button
        )

        layout.addStretch()

        self.pages.addWidget(
            page
        )


    # =========================================================
    # SIGNALS
    # =========================================================

    def connect_signals(self):
        self.signals.status.connect(
            self.set_ai_status
        )

        self.signals.progress.connect(
            self.ai_progress.setValue
        )

        self.signals.ai_finished.connect(
            self.ai_install_finished
        )

        self.signals.gmail_finished.connect(
            self.gmail_connect_finished
        )

        self.signals.scan_finished.connect(
            self.app_scan_finished
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )


    # =========================================================
    # NAVIGATION
    # =========================================================

    def next_page(self):
        if self.current_page < (
            self.pages.count()
            - 1
        ):
            self.current_page += 1

            self.pages.setCurrentIndex(
                self.current_page
            )

            self.update_navigation()


    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1

            self.pages.setCurrentIndex(
                self.current_page
            )

            self.update_navigation()


    def update_navigation(self):
        total = self.pages.count()

        self.step_label.setText(
            f"Step {self.current_page + 1} "
            f"of {total}"
        )

        self.back_button.setEnabled(
            self.current_page > 0
        )

        self.next_button.setVisible(
            self.current_page
            < total - 1
        )


    # =========================================================
    # AI
    # =========================================================

    def refresh_ai_status(self):
        models = get_required_models()

        normal = models[0]
        think = models[1]

        has_ollama = ollama_installed()

        normal_ready = (
            has_ollama
            and model_installed(
                normal
            )
        )

        think_ready = (
            has_ollama
            and model_installed(
                think
            )
        )

        self.ollama_status.setText(
            "✓ Ollama detected"
            if has_ollama
            else "✗ Ollama not installed"
        )

        self.normal_status.setText(
            (
                "✓ Normal model: "
                if normal_ready
                else "✗ Normal model missing: "
            )
            + normal
        )

        self.think_status.setText(
            (
                "✓ Think model: "
                if think_ready
                else "✗ Think model missing: "
            )
            + think
        )

        ready = (
            has_ollama
            and normal_ready
            and think_ready
        )

        self.get_ollama_button.setVisible(
            not has_ollama
        )

        self.install_models_button.setEnabled(
            has_ollama
            and not ready
        )

        if ready:
            self.ai_status.setText(
                "AI is ready."
            )

            self.ai_progress.setValue(
                100
            )

        elif not has_ollama:
            self.ai_status.setText(
                "Install Ollama first."
            )

            self.ai_progress.setValue(
                0
            )

        else:
            self.ai_status.setText(
                "Install the missing AI models."
            )

            self.ai_progress.setValue(
                25
            )


    def open_ollama(self):
        webbrowser.open(
            "https://ollama.com/download/windows"
        )


    def start_ai_install(self):
        self.install_models_button.setEnabled(
            False
        )

        thread = threading.Thread(
            target=self.ai_worker,
            daemon=True
        )

        thread.start()


    def ai_worker(self):
        models = []

        for model in get_required_models():
            if model not in models:
                models.append(
                    model
                )

        total = len(
            models
        )

        for index, model in enumerate(
            models,
            start=1
        ):
            if not model_installed(
                model
            ):
                self.signals.status.emit(
                    f"Downloading {model}..."
                )

                success, message = pull_model(
                    model
                )

                self.signals.status.emit(
                    message
                )

                if not success:
                    self.signals.ai_finished.emit(
                        False
                    )

                    return

            self.signals.progress.emit(
                int(
                    index
                    / total
                    * 100
                )
            )

        self.signals.ai_finished.emit(
            True
        )


    def set_ai_status(
        self,
        text
    ):
        self.ai_status.setText(
            text
        )


    def ai_install_finished(
        self,
        success
    ):
        if not success:
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "AI model installation failed."
            )

        self.refresh_ai_status()


    # =========================================================
    # VOICE
    # =========================================================

    def update_voice_fields(self):
        provider = (
            self.voice_provider
            .currentData()
        )

        is_elevenlabs = (
            provider
            == "elevenlabs"
        )

        self.api_key_label.setVisible(
            is_elevenlabs
        )

        self.api_key_input.setVisible(
            is_elevenlabs
        )

        self.voice_id_label.setVisible(
            is_elevenlabs
        )

        self.voice_id_input.setVisible(
            is_elevenlabs
        )


    def save_voice_page(self):
        provider = (
            self.voice_provider
            .currentData()
        )

        api_key = (
            self.api_key_input
            .text()
            .strip()
        )

        if (
            provider == "elevenlabs"
            and not api_key
        ):
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Enter an ElevenLabs API key "
                "or choose Piper."
            )

            return

        current = load_voice_settings()

        current[
            "provider"
        ] = provider

        current[
            "elevenlabs_api_key"
        ] = api_key

        current[
            "elevenlabs_voice_id"
        ] = (
            self.voice_id_input
            .text()
            .strip()
        )

        save_voice_settings(
            current
        )

        QMessageBox.information(
            self,
            "JARVIS",
            "Voice settings saved."
        )


    # =========================================================
    # GMAIL
    # =========================================================

    def refresh_gmail_status(self):
        connected = gmail_connected()

        self.gmail_status_label.setText(
            "✓ Gmail connected"
            if connected
            else "○ Gmail not connected"
        )

        self.gmail_connect_button.setText(
            "Reconnect Gmail"
            if connected
            else "Connect Gmail"
        )


    def connect_gmail(self):
        self.gmail_connect_button.setEnabled(
            False
        )

        thread = threading.Thread(
            target=self.gmail_worker,
            daemon=True
        )

        thread.start()


    def gmail_worker(self):
        try:
            get_gmail_service()

            self.signals.gmail_finished.emit(
                True
            )

        except Exception as error:
            print(
                "Gmail setup error:",
                error
            )

            self.signals.gmail_finished.emit(
                False
            )


    def gmail_connect_finished(
        self,
        success
    ):
        self.gmail_connect_button.setEnabled(
            True
        )

        self.refresh_gmail_status()

        if success:
            QMessageBox.information(
                self,
                "JARVIS",
                "Gmail connected successfully."
            )

        else:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Gmail connection failed."
            )


    # =========================================================
    # APPS
    # =========================================================

    def start_app_scan(self):
        self.scan_apps_button.setEnabled(
            False
        )

        self.app_scan_status.setText(
            "Scanning installed applications..."
        )

        thread = threading.Thread(
            target=self.app_scan_worker,
            daemon=True
        )

        thread.start()


    def app_scan_worker(self):
        try:
            apps = scan_apps()

            self.signals.scan_finished.emit(
                True,
                len(
                    apps
                )
            )

        except Exception as error:
            print(
                "Initial app scan error:",
                error
            )

            self.signals.scan_finished.emit(
                False,
                0
            )


    def app_scan_finished(
        self,
        success,
        count
    ):
        self.scan_apps_button.setEnabled(
            True
        )

        if success:
            self.app_scan_status.setText(
                f"✓ Found {count} applications."
            )

        else:
            self.app_scan_status.setText(
                "✗ Application scan failed."
            )


    # =========================================================
    # FINISH
    # =========================================================

    def finish_setup(self):
        if not ollama_installed():
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Ollama must be installed before "
                "setup can be completed."
            )

            return

        missing = [
            model
            for model
            in get_required_models()
            if not model_installed(
                model
            )
        ]

        if missing:
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Install the required AI models "
                "before finishing setup."
            )

            return

        try:
            self.save_voice_page()

            mark_setup_complete()

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS Setup",
                f"Could not finish setup:\n{error}"
            )

            return

        self.finished.emit()

        self.close()


    # =========================================================
    # THEME
    # =========================================================

    def on_theme_changed(
        self,
        theme
    ):
        self.theme = theme.copy()

        self.apply_theme(
            self.theme
        )


    def apply_theme(
        self,
        theme
    ):
        background = theme[
            "color_1"
        ]

        accent = theme[
            "color_2"
        ]

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {background};
                color: {accent};
            }}

            QLabel {{
                color: {accent};
                font-size: 14px;
            }}

            QLabel#setupTitle {{
                font-size: 28px;
                font-weight: bold;
            }}

            QLabel#pageHeading {{
                font-size: 20px;
                font-weight: bold;
            }}

            QPushButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 7px;
                padding: 9px 14px;
            }}

            QPushButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QPushButton:disabled {{
                color: gray;
                border-color: gray;
            }}

            QLineEdit,
            QComboBox {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 6px;
                padding: 8px;
            }}

            QProgressBar {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 6px;
                text-align: center;
                min-height: 22px;
            }}

            QProgressBar::chunk {{
                background-color: {accent};
            }}
            """
        )