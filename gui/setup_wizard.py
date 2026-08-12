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
    QMessageBox,
    QProgressBar
)

from core.setup_manager import (
    ollama_installed,
    model_installed,
    pull_model,
    get_required_models,
    mark_setup_complete
)

from gui.theme_manager import (
    load_theme,
    theme_bus
)


class SetupSignals(QObject):
    status_changed = Signal(str)
    progress_changed = Signal(int)
    setup_finished = Signal(bool)


class SetupWizard(QWidget):

    finished = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS Setup")
        self.resize(720, 540)

        self.theme = load_theme()
        self.worker_running = False

        self.signals = SetupSignals()

        self.build_ui()

        self.signals.status_changed.connect(
            self.update_status
        )

        self.signals.progress_changed.connect(
            self.progress_bar.setValue
        )

        self.signals.setup_finished.connect(
            self.on_model_setup_finished
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )

        self.apply_theme(
            self.theme
        )

        self.refresh_status()


    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            40,
            35,
            40,
            35
        )

        layout.setSpacing(15)

        title = QLabel(
            "WELCOME TO JARVIS"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setObjectName(
            "setupTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Let's prepare JARVIS for this computer."
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setWordWrap(
            True
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(20)

        section_title = QLabel(
            "AI SETUP"
        )

        section_title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            section_title
        )

        self.ollama_status = QLabel(
            "Checking Ollama..."
        )

        self.normal_model_status = QLabel(
            "Checking Normal Mode model..."
        )

        self.think_model_status = QLabel(
            "Checking Think Mode model..."
        )

        layout.addWidget(
            self.ollama_status
        )

        layout.addWidget(
            self.normal_model_status
        )

        layout.addWidget(
            self.think_model_status
        )

        layout.addSpacing(15)

        self.status_label = QLabel(
            "Checking system..."
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setTextVisible(
            True
        )

        layout.addWidget(
            self.progress_bar
        )

        layout.addStretch()

        first_row = QHBoxLayout()

        self.get_ollama_button = QPushButton(
            "Get Ollama"
        )

        self.refresh_button = QPushButton(
            "Refresh"
        )

        first_row.addWidget(
            self.get_ollama_button
        )

        first_row.addWidget(
            self.refresh_button
        )

        layout.addLayout(
            first_row
        )

        second_row = QHBoxLayout()

        self.install_models_button = QPushButton(
            "Install Missing AI Models"
        )

        self.finish_button = QPushButton(
            "Finish Setup"
        )

        second_row.addWidget(
            self.install_models_button
        )

        second_row.addWidget(
            self.finish_button
        )

        layout.addLayout(
            second_row
        )

        self.get_ollama_button.clicked.connect(
            self.open_ollama_download
        )

        self.refresh_button.clicked.connect(
            self.refresh_status
        )

        self.install_models_button.clicked.connect(
            self.start_model_setup
        )

        self.finish_button.clicked.connect(
            self.finish_setup
        )


    # =========================================================
    # STATUS LABEL
    # =========================================================

    def update_status(
        self,
        text
    ):
        self.status_label.setText(
            text
        )


    # =========================================================
    # STATUS CHECK
    # =========================================================

    def refresh_status(self):
        if self.worker_running:
            return

        models = get_required_models()

        normal_model = models[0]
        think_model = models[1]

        has_ollama = ollama_installed()

        if has_ollama:
            self.ollama_status.setText(
                "✓ Ollama detected"
            )

            self.get_ollama_button.setVisible(
                False
            )

        else:
            self.ollama_status.setText(
                "✗ Ollama is not installed"
            )

            self.get_ollama_button.setVisible(
                True
            )

        normal_ready = False
        think_ready = False

        if has_ollama:
            normal_ready = model_installed(
                normal_model
            )

            think_ready = model_installed(
                think_model
            )

        if normal_ready:
            self.normal_model_status.setText(
                f"✓ Normal Mode model: {normal_model}"
            )

        else:
            self.normal_model_status.setText(
                f"✗ Normal Mode model missing: {normal_model}"
            )

        if think_ready:
            self.think_model_status.setText(
                f"✓ Think Mode model: {think_model}"
            )

        else:
            self.think_model_status.setText(
                f"✗ Think Mode model missing: {think_model}"
            )

        all_ready = (
            has_ollama
            and normal_ready
            and think_ready
        )

        self.finish_button.setEnabled(
            all_ready
        )

        self.install_models_button.setEnabled(
            has_ollama
            and not all_ready
        )

        self.refresh_button.setEnabled(
            True
        )

        if all_ready:
            self.status_label.setText(
                "JARVIS AI is ready. "
                "You can finish setup."
            )

            self.progress_bar.setValue(
                100
            )

        elif not has_ollama:
            self.status_label.setText(
                "Ollama is required for JARVIS AI. "
                "Install Ollama, then click Refresh."
            )

            self.progress_bar.setValue(
                0
            )

        else:
            self.status_label.setText(
                "One or more AI models are missing. "
                "Click Install Missing AI Models."
            )

            self.progress_bar.setValue(
                25
            )


    # =========================================================
    # OLLAMA
    # =========================================================

    def open_ollama_download(self):
        webbrowser.open(
            "https://ollama.com/download/windows"
        )

        QMessageBox.information(
            self,
            "JARVIS Setup",
            "Install Ollama using the page that opened.\n\n"
            "When installation is complete, return to JARVIS "
            "and click Refresh."
        )


    # =========================================================
    # MODEL INSTALLATION
    # =========================================================

    def start_model_setup(self):
        if self.worker_running:
            return

        if not ollama_installed():
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Ollama must be installed first."
            )

            return

        self.worker_running = True

        self.install_models_button.setEnabled(
            False
        )

        self.refresh_button.setEnabled(
            False
        )

        self.finish_button.setEnabled(
            False
        )

        self.progress_bar.setValue(
            0
        )

        self.status_label.setText(
            "Preparing AI models..."
        )

        worker = threading.Thread(
            target=self.install_models_worker,
            daemon=True
        )

        worker.start()


    def install_models_worker(self):
        models = get_required_models()

        unique_models = []

        for model in models:
            if model not in unique_models:
                unique_models.append(
                    model
                )

        total = len(
            unique_models
        )

        if total == 0:
            self.signals.setup_finished.emit(
                False
            )

            return

        for index, model in enumerate(
            unique_models,
            start=1
        ):
            if model_installed(
                model
            ):
                self.signals.status_changed.emit(
                    f"{model} is already installed."
                )

            else:
                self.signals.status_changed.emit(
                    f"Downloading {model}...\n"
                    "This may take several minutes."
                )

                success, message = pull_model(
                    model
                )

                self.signals.status_changed.emit(
                    message
                )

                if not success:
                    self.signals.setup_finished.emit(
                        False
                    )

                    return

            progress = int(
                (
                    index
                    / total
                )
                * 100
            )

            self.signals.progress_changed.emit(
                progress
            )

        self.signals.setup_finished.emit(
            True
        )


    def on_model_setup_finished(
        self,
        success
    ):
        self.worker_running = False

        self.refresh_button.setEnabled(
            True
        )

        if success:
            self.status_label.setText(
                "AI model installation complete."
            )

            self.progress_bar.setValue(
                100
            )

        else:
            self.status_label.setText(
                "AI model installation failed. "
                "Check that Ollama is running and try again."
            )

        self.refresh_status()


    # =========================================================
    # FINISH
    # =========================================================

    def finish_setup(self):
        if self.worker_running:
            return

        if not ollama_installed():
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Ollama is not installed yet."
            )

            return

        models = get_required_models()

        missing_models = []

        for model in models:
            if not model_installed(
                model
            ):
                missing_models.append(
                    model
                )

        if missing_models:
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "JARVIS is still missing one or more "
                "required AI models."
            )

            return

        try:
            mark_setup_complete()

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS Setup",
                f"Could not save setup status:\n{error}"
            )

            return

        QMessageBox.information(
            self,
            "JARVIS",
            "Initial AI setup is complete."
        )

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
                color: {accent};
                font-size: 28px;
                font-weight: bold;
            }}

            QLabel#sectionTitle {{
                color: {accent};
                font-size: 17px;
                font-weight: bold;
            }}

            QPushButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 7px;
                padding: 10px 14px;
                font-size: 13px;
            }}

            QPushButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QPushButton:disabled {{
                color: gray;
                border: 1px solid gray;
            }}

            QProgressBar {{
                color: {accent};
                background-color: {background};
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


    # =========================================================
    # CLOSE PROTECTION
    # =========================================================

    def closeEvent(
        self,
        event
    ):
        if self.worker_running:
            QMessageBox.warning(
                self,
                "JARVIS Setup",
                "Please wait for the current model "
                "installation to finish."
            )

            event.ignore()

            return

        event.accept()