import json
import os
import threading

from PySide6.QtCore import (
    QObject,
    Qt,
    Signal,
)

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# =========================================================
# CORE
# =========================================================

from core.ai_mode import (
    load_ai_settings,
    save_ai_settings,
)

from core.app_scanner import (
    scan_apps,
)

from core.gmail_manager import (
    get_gmail_service,
)

from core.paths import (
    resource_file,
    user_file,
)

from core.personality import (
    get_current_personality_preset,
    get_personality_presets,
    load_personality_settings,
    save_personality_settings,
)

from core.startup_manager import (
    apply_startup_settings,
    is_windows_startup_enabled,
    load_startup_settings,
)

from core.ui_blocker import (
    block_wake,
    unblock_wake,
)

from core.voice_output import (
    preview_voice,
)

from core.voice_settings import (
    BRIAN_VOICE_ID,
    load_voice_settings,
    save_voice_settings,
)

# =========================================================
# GUI TABS
# =========================================================

from gui.commands_tab import (
    CommandsTab,
)

from gui.macros_tab import (
    MacrosTab,
)

from gui.screen_tab import (
    ScreenTab,
)

from gui.theme_manager import (
    DEFAULT_THEME,
    emit_theme_preview,
    load_theme,
    save_theme as persist_theme,
    theme_bus,
)


# =========================================================
# FILES
# =========================================================

DETECTED_FILE = user_file(
    "apps_detected.json"
)

ALIASES_FILE = user_file(
    "apps.json"
)

CONTACTS_FILE = user_file(
    "contacts.json"
)

GMAIL_TOKEN_FILE = user_file(
    "gmail_token.json"
)


# =========================================================
# SIGNALS
# =========================================================

class SettingsSignals(QObject):

    gmail_finished = Signal(
        bool,
        str,
    )

    apps_finished = Signal(
        bool,
        int,
        str,
    )


# =========================================================
# SETTINGS PAGE
# =========================================================

class SettingsPage(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "JARVIS Settings"
        )

        self.resize(
            1100,
            780,
        )

        self.alias_inputs = {}
        self.app_rows = []
        self.contact_rows = []

        self.theme = load_theme()

        self.signals = SettingsSignals()

        self.signals.gmail_finished.connect(
            self.gmail_connection_finished
        )

        self.signals.apps_finished.connect(
            self.app_scan_finished
        )

        self.build_ui()

        self.apply_settings_theme(
            self.theme
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )

    # =========================================================
    # WAKE WORD BLOCKING
    # =========================================================

    def showEvent(
        self,
        event,
    ):
        block_wake(
            "settings"
        )

        super().showEvent(
            event
        )

    def hideEvent(
        self,
        event,
    ):
        unblock_wake(
            "settings"
        )

        super().hideEvent(
            event
        )

    def closeEvent(
        self,
        event,
    ):
        unblock_wake(
            "settings"
        )

        event.accept()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(
        self
    ):
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        # =====================================================
        # HEADER
        # =====================================================

        top_bar = QHBoxLayout()

        self.back_button = QPushButton(
            "← Back"
        )

        self.back_button.setFixedWidth(
            100
        )

        self.back_button.clicked.connect(
            self.close
        )

        title = QLabel(
            "JARVIS SETTINGS"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        top_bar.addWidget(
            self.back_button
        )

        top_bar.addStretch()

        top_bar.addWidget(
            title
        )

        top_bar.addStretch()

        spacer = QWidget()

        spacer.setFixedWidth(
            100
        )

        top_bar.addWidget(
            spacer
        )

        main_layout.addLayout(
            top_bar
        )

        # =====================================================
        # TABS
        # =====================================================

        self.tabs = QTabWidget()

        self.general_tab = QWidget()

        self.apps_tab = QWidget()

        self.macros_tab = MacrosTab()

        self.commands_tab = CommandsTab()

        self.screen_tab = ScreenTab()

        self.ai_tab = QWidget()

        self.personality_tab = QWidget()

        self.voice_tab = QWidget()

        self.email_tab = QWidget()

        self.appearance_tab = QWidget()

        self.tabs.addTab(
            self.general_tab,
            "General",
        )

        self.tabs.addTab(
            self.apps_tab,
            "Apps",
        )

        self.tabs.addTab(
            self.macros_tab,
            "Macros",
        )

        self.tabs.addTab(
            self.commands_tab,
            "Commands",
        )

        self.tabs.addTab(
            self.screen_tab,
            "Screen",
        )

        self.tabs.addTab(
            self.ai_tab,
            "AI",
        )

        self.tabs.addTab(
            self.personality_tab,
            "Personality",
        )

        self.tabs.addTab(
            self.voice_tab,
            "Voice",
        )

        self.tabs.addTab(
            self.email_tab,
            "Email",
        )

        self.tabs.addTab(
            self.appearance_tab,
            "Appearance",
        )

        main_layout.addWidget(
            self.tabs
        )

        # =====================================================
        # BUILD STANDARD TABS
        # =====================================================

        self.build_general_tab()

        self.build_apps_tab()

        self.build_ai_tab()

        self.build_personality_tab()

        self.build_voice_tab()

        self.build_email_tab()

        self.build_appearance_tab()

    # =========================================================
    # GENERAL
    # =========================================================

    def build_general_tab(
        self
    ):
        layout = QVBoxLayout(
            self.general_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "Startup & Background"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Control how JARVIS starts with Windows "
            "and behaves in the background."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            25
        )

        settings = (
            load_startup_settings()
        )

        self.start_with_windows_checkbox = QCheckBox(
            "Start JARVIS automatically when Windows starts"
        )

        self.start_with_windows_checkbox.setChecked(
            is_windows_startup_enabled()
        )

        layout.addWidget(
            self.start_with_windows_checkbox
        )

        startup_description = QLabel(
            "JARVIS will launch automatically "
            "after you sign in to Windows."
        )

        startup_description.setWordWrap(
            True
        )

        layout.addWidget(
            startup_description
        )

        layout.addSpacing(
            20
        )

        self.start_minimized_checkbox = QCheckBox(
            "Start minimized to the system tray"
        )

        self.start_minimized_checkbox.setChecked(
            bool(
                settings.get(
                    "start_minimized",
                    True,
                )
            )
        )

        layout.addWidget(
            self.start_minimized_checkbox
        )

        minimized_description = QLabel(
            "The main JARVIS window stays hidden while "
            "the wake-word listener runs in the background."
        )

        minimized_description.setWordWrap(
            True
        )

        layout.addWidget(
            minimized_description
        )

        layout.addSpacing(
            25
        )

        self.startup_status_label = QLabel()

        self.startup_status_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            self.startup_status_label
        )

        self.update_startup_status()

        layout.addStretch()

        button_row = QHBoxLayout()

        button_row.addStretch()

        save_button = QPushButton(
            "Save Startup Settings"
        )

        save_button.clicked.connect(
            self.save_startup_settings_gui
        )

        button_row.addWidget(
            save_button
        )

        layout.addLayout(
            button_row
        )

    def update_startup_status(
        self
    ):
        if is_windows_startup_enabled():
            self.startup_status_label.setText(
                "Windows startup: Enabled ✓"
            )

        else:
            self.startup_status_label.setText(
                "Windows startup: Disabled"
            )

    def save_startup_settings_gui(
        self
    ):
        settings = {
            "start_with_windows":
                self.start_with_windows_checkbox.isChecked(),

            "start_minimized":
                self.start_minimized_checkbox.isChecked(),
        }

        try:
            apply_startup_settings(
                settings
            )

            self.update_startup_status()

            QMessageBox.information(
                self,
                "JARVIS",
                "Startup settings saved.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                "Could not update Windows startup.\n\n"
                f"{error}",
            )

    # =========================================================
    # APPS
    # =========================================================

    def build_apps_tab(
        self
    ):
        layout = QVBoxLayout(
            self.apps_tab
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        title = QLabel(
            "Applications"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Manage detected programs and the names "
            "you want JARVIS to recognize."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search detected apps..."
        )

        self.search_box.textChanged.connect(
            self.filter_apps
        )

        layout.addWidget(
            self.search_box
        )

        buttons = QHBoxLayout()

        refresh_button = QPushButton(
            "Refresh Apps"
        )

        self.rescan_button = QPushButton(
            "Rescan Apps"
        )

        save_button = QPushButton(
            "Save Aliases"
        )

        refresh_button.clicked.connect(
            self.load_apps
        )

        self.rescan_button.clicked.connect(
            self.rescan_apps
        )

        save_button.clicked.connect(
            self.save_aliases
        )

        buttons.addWidget(
            refresh_button
        )

        buttons.addWidget(
            self.rescan_button
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

        headers = QHBoxLayout()

        app_header = QLabel(
            "Detected App"
        )

        alias_header = QLabel(
            "JARVIS Name"
        )

        app_header.setStyleSheet(
            "font-weight: bold;"
        )

        alias_header.setStyleSheet(
            "font-weight: bold;"
        )

        headers.addWidget(
            app_header,
            2,
        )

        headers.addWidget(
            alias_header,
            1,
        )

        layout.addLayout(
            headers
        )

        self.apps_scroll = QScrollArea()

        self.apps_scroll.setWidgetResizable(
            True
        )

        self.apps_container = QWidget()

        self.apps_layout = QVBoxLayout(
            self.apps_container
        )

        self.apps_layout.setAlignment(
            Qt.AlignTop
        )

        self.apps_scroll.setWidget(
            self.apps_container
        )

        layout.addWidget(
            self.apps_scroll
        )

        self.app_scan_status = QLabel(
            ""
        )

        layout.addWidget(
            self.app_scan_status
        )

        self.load_apps()

    def clear_app_list(
        self
    ):
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.alias_inputs.clear()

        self.app_rows.clear()

    def load_apps(
        self
    ):
        self.clear_app_list()

        detected = self.load_json(
            DETECTED_FILE
        )

        aliases = self.load_json(
            ALIASES_FILE
        )

        reverse_aliases = {
            target: alias
            for alias, target
            in aliases.items()
        }

        for app_name, app_path in sorted(
            detected.items(),
            key=lambda item:
                item[0].lower(),
        ):
            row = QWidget()

            row_layout = QHBoxLayout(
                row
            )

            app_label = QLabel(
                app_name
            )

            app_label.setToolTip(
                app_path
            )

            alias_input = QLineEdit()

            alias_input.setText(
                reverse_aliases.get(
                    app_path,
                    "",
                )
            )

            alias_input.setPlaceholderText(
                "Assign name..."
            )

            row_layout.addWidget(
                app_label,
                2,
            )

            row_layout.addWidget(
                alias_input,
                1,
            )

            self.apps_layout.addWidget(
                row
            )

            self.alias_inputs[
                app_path
            ] = alias_input

            self.app_rows.append(
                (
                    app_name.lower(),
                    app_path.lower(),
                    row,
                )
            )

        self.apps_layout.addStretch()

        self.filter_apps(
            self.search_box.text()
        )

    def filter_apps(
        self,
        text,
    ):
        search = (
            text
            .lower()
            .strip()
        )

        for (
            app_name,
            app_path,
            row,
        ) in self.app_rows:

            row.setVisible(
                search in app_name
                or search in app_path
            )

    def save_aliases(
        self
    ):
        aliases = {}

        for (
            app_path,
            input_box,
        ) in self.alias_inputs.items():

            alias = (
                input_box
                .text()
                .lower()
                .strip()
            )

            if alias:
                aliases[
                    alias
                ] = app_path

        try:
            self.save_json(
                ALIASES_FILE,
                aliases,
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "App aliases saved.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save aliases:\n{error}",
            )

    def rescan_apps(
        self
    ):
        self.rescan_button.setEnabled(
            False
        )

        self.app_scan_status.setText(
            "Scanning installed applications..."
        )

        thread = threading.Thread(
            target=self.rescan_apps_worker,
            daemon=True,
        )

        thread.start()

    def rescan_apps_worker(
        self
    ):
        try:
            apps = scan_apps()

            self.signals.apps_finished.emit(
                True,
                len(
                    apps
                ),
                "",
            )

        except Exception as error:
            self.signals.apps_finished.emit(
                False,
                0,
                str(
                    error
                ),
            )

    def app_scan_finished(
        self,
        success,
        count,
        error,
    ):
        self.rescan_button.setEnabled(
            True
        )

        if success:
            self.app_scan_status.setText(
                f"✓ Found {count} applications."
            )

            self.load_apps()

        else:
            self.app_scan_status.setText(
                "✗ App scan failed."
            )

            QMessageBox.warning(
                self,
                "JARVIS",
                f"App scan failed:\n{error}",
            )

    # =========================================================
    # AI
    # =========================================================

    def build_ai_tab(
        self
    ):
        layout = QVBoxLayout(
            self.ai_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "AI Models"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose which Ollama models JARVIS uses "
            "for Normal Mode and Think Mode."
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

        settings = load_ai_settings()

        # =====================================================
        # NORMAL
        # =====================================================

        normal_row = QHBoxLayout()

        normal_row.addWidget(
            QLabel(
                "Normal Mode Model"
            )
        )

        normal_row.addStretch()

        self.normal_model_combo = QComboBox()

        self.normal_model_combo.setEditable(
            True
        )

        self.normal_model_combo.addItems(
            [
                "qwen2.5:1.5b",
                "llama3.2:3b",
                "gemma3:4b",
            ]
        )

        self.normal_model_combo.setCurrentText(
            settings.get(
                "normal_model",
                "qwen2.5:1.5b",
            )
        )

        normal_row.addWidget(
            self.normal_model_combo,
            2,
        )

        layout.addLayout(
            normal_row
        )

        # =====================================================
        # THINK
        # =====================================================

        think_row = QHBoxLayout()

        think_row.addWidget(
            QLabel(
                "Think Mode Model"
            )
        )

        think_row.addStretch()

        self.think_model_combo = QComboBox()

        self.think_model_combo.setEditable(
            True
        )

        self.think_model_combo.addItems(
            [
                "gemma3:4b",
                "llama3.2:3b",
                "qwen2.5:1.5b",
            ]
        )

        self.think_model_combo.setCurrentText(
            settings.get(
                "think_model",
                "gemma3:4b",
            )
        )

        think_row.addWidget(
            self.think_model_combo,
            2,
        )

        layout.addLayout(
            think_row
        )

        # =====================================================
        # TEMPERATURE
        # =====================================================

        temperature_row = QHBoxLayout()

        temperature_row.addWidget(
            QLabel(
                "Temperature"
            )
        )

        temperature_row.addStretch()

        self.temperature_input = QDoubleSpinBox()

        self.temperature_input.setRange(
            0.0,
            2.0,
        )

        self.temperature_input.setSingleStep(
            0.1
        )

        self.temperature_input.setDecimals(
            1
        )

        self.temperature_input.setValue(
            float(
                settings.get(
                    "temperature",
                    0.7,
                )
            )
        )

        temperature_row.addWidget(
            self.temperature_input
        )

        layout.addLayout(
            temperature_row
        )

        layout.addSpacing(
            20
        )

        buttons = QHBoxLayout()

        reset_button = QPushButton(
            "Reset Defaults"
        )

        save_button = QPushButton(
            "Save AI Settings"
        )

        reset_button.clicked.connect(
            self.reset_ai_settings
        )

        save_button.clicked.connect(
            self.save_ai_settings_gui
        )

        buttons.addWidget(
            reset_button
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

        layout.addStretch()

    def save_ai_settings_gui(
        self
    ):
        normal_model = (
            self.normal_model_combo
            .currentText()
            .strip()
        )

        think_model = (
            self.think_model_combo
            .currentText()
            .strip()
        )

        if (
            not normal_model
            or not think_model
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Both model fields are required.",
            )

            return

        save_ai_settings(
            {
                "normal_model":
                    normal_model,

                "think_model":
                    think_model,

                "temperature":
                    self.temperature_input.value(),
            }
        )

        QMessageBox.information(
            self,
            "JARVIS",
            "AI settings saved.",
        )

    def reset_ai_settings(
        self
    ):
        self.normal_model_combo.setCurrentText(
            "qwen2.5:1.5b"
        )

        self.think_model_combo.setCurrentText(
            "gemma3:4b"
        )

        self.temperature_input.setValue(
            0.7
        )

    # =========================================================
    # PERSONALITY
    # =========================================================

    def build_personality_tab(
        self
    ):
        layout = QVBoxLayout(
            self.personality_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "JARVIS Personality"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose how JARVIS responds to you. "
            "The selected personality is applied "
            "to AI conversations and screen vision."
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

        # =====================================================
        # PRESET
        # =====================================================

        preset_row = QHBoxLayout()

        preset_row.addWidget(
            QLabel(
                "Personality"
            )
        )

        preset_row.addStretch()

        self.personality_combo = QComboBox()

        presets = (
            get_personality_presets()
        )

        if isinstance(
            presets,
            dict,
        ):
            for key, value in presets.items():

                if isinstance(
                    value,
                    dict,
                ):
                    display_name = (
                        value.get(
                            "display_name"
                        )
                        or value.get(
                            "name"
                        )
                        or key.replace(
                            "_",
                            " ",
                        ).title()
                    )

                else:
                    display_name = (
                        key.replace(
                            "_",
                            " ",
                        ).title()
                    )

                self.personality_combo.addItem(
                    display_name,
                    key,
                )

        else:
            defaults = (
                "classic",
                "professional",
                "casual",
                "witty",
                "concise",
                "custom",
            )

            for preset in defaults:
                self.personality_combo.addItem(
                    preset.title(),
                    preset,
                )

        current_preset = (
            get_current_personality_preset()
        )

        index = (
            self.personality_combo.findData(
                current_preset
            )
        )

        if index >= 0:
            self.personality_combo.setCurrentIndex(
                index
            )

        preset_row.addWidget(
            self.personality_combo,
            2,
        )

        layout.addLayout(
            preset_row
        )

        layout.addSpacing(
            15
        )

        # =====================================================
        # CUSTOM
        # =====================================================

        custom_label = QLabel(
            "Custom Personality Instructions"
        )

        custom_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            custom_label
        )

        self.personality_custom_input = QTextEdit()

        self.personality_custom_input.setPlaceholderText(
            "Example: Be concise, witty, confident, "
            "and address me casually."
        )

        current_settings = (
            load_personality_settings()
        )

        if isinstance(
            current_settings,
            dict,
        ):
            custom_text = (
                current_settings.get(
                    "custom_instructions",
                    "",
                )
            )

            self.personality_custom_input.setPlainText(
                str(
                    custom_text
                )
            )

        layout.addWidget(
            self.personality_custom_input
        )

        info = QLabel(
            "Custom instructions are mainly used when "
            "the Custom personality preset is selected."
        )

        info.setWordWrap(
            True
        )

        layout.addWidget(
            info
        )

        buttons = QHBoxLayout()

        reset_button = QPushButton(
            "Reset"
        )

        save_button = QPushButton(
            "Save Personality"
        )

        reset_button.clicked.connect(
            self.reset_personality
        )

        save_button.clicked.connect(
            self.save_personality_gui
        )

        buttons.addWidget(
            reset_button
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

    def save_personality_gui(
        self
    ):
        preset = (
            self.personality_combo
            .currentData()
        )

        if not preset:
            preset = (
                self.personality_combo
                .currentText()
                .lower()
                .strip()
            )

        custom_text = (
            self.personality_custom_input
            .toPlainText()
            .strip()
        )

        try:
            save_personality_settings(
                {
                    "preset":
                        preset,

                    "custom_instructions":
                        custom_text,
                }
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "Personality settings saved.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                "Could not save personality settings.\n\n"
                f"{error}",
            )

    def reset_personality(
        self
    ):
        index = (
            self.personality_combo.findData(
                "classic"
            )
        )

        if index >= 0:
            self.personality_combo.setCurrentIndex(
                index
            )

        self.personality_custom_input.clear()

    # =========================================================
    # VOICE
    # =========================================================

    def build_voice_tab(
        self
    ):
        outer_layout = QVBoxLayout(
            self.voice_tab
        )

        outer_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        scroll.setWidget(
            container
        )

        outer_layout.addWidget(
            scroll
        )

        title = QLabel(
            "Voice"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose the voice engine and voice JARVIS uses."
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

        settings = (
            load_voice_settings()
        )

        # =====================================================
        # PROVIDER
        # =====================================================

        provider_row = QHBoxLayout()

        provider_row.addWidget(
            QLabel(
                "Voice Provider"
            )
        )

        provider_row.addStretch()

        self.voice_provider_combo = QComboBox()

        self.voice_provider_combo.addItem(
            "Piper — Free / Local",
            "piper",
        )

        self.voice_provider_combo.addItem(
            "Kokoro — High Quality / Local",
            "kokoro",
        )

        self.voice_provider_combo.addItem(
            "ElevenLabs — Cloud",
            "elevenlabs",
        )

        provider_index = (
            self.voice_provider_combo.findData(
                settings.get(
                    "provider",
                    "piper",
                )
            )
        )

        if provider_index >= 0:
            self.voice_provider_combo.setCurrentIndex(
                provider_index
            )

        provider_row.addWidget(
            self.voice_provider_combo,
            2,
        )

        layout.addLayout(
            provider_row
        )

        layout.addSpacing(
            20
        )

        # =====================================================
        # PIPER
        # =====================================================

        self.piper_label = QLabel(
            "Piper Voice"
        )

        self.piper_voice_combo = QComboBox()

        self.load_piper_voices()

        saved_piper = settings.get(
            "piper_voice",
            "en_US-lessac-medium.onnx",
        )

        piper_index = (
            self.piper_voice_combo.findData(
                saved_piper
            )
        )

        if piper_index >= 0:
            self.piper_voice_combo.setCurrentIndex(
                piper_index
            )

        layout.addWidget(
            self.piper_label
        )

        layout.addWidget(
            self.piper_voice_combo
        )

        # =====================================================
        # KOKORO
        # =====================================================

        self.kokoro_voice_label = QLabel(
            "Kokoro Voice"
        )

        self.kokoro_voice_combo = QComboBox()

        self.kokoro_voice_combo.addItem(
            "George — British Male",
            "bm_george",
        )

        self.kokoro_voice_combo.addItem(
            "Fable — British Male",
            "bm_fable",
        )

        self.kokoro_voice_combo.addItem(
            "Lewis — British Male",
            "bm_lewis",
        )

        kokoro_index = (
            self.kokoro_voice_combo.findData(
                settings.get(
                    "kokoro_voice",
                    "bm_george",
                )
            )
        )

        if kokoro_index >= 0:
            self.kokoro_voice_combo.setCurrentIndex(
                kokoro_index
            )

        layout.addWidget(
            self.kokoro_voice_label
        )

        layout.addWidget(
            self.kokoro_voice_combo
        )

        self.kokoro_speed_label = QLabel(
            "Kokoro Speech Speed"
        )

        self.kokoro_speed_input = QDoubleSpinBox()

        self.kokoro_speed_input.setRange(
            0.50,
            2.00,
        )

        self.kokoro_speed_input.setSingleStep(
            0.05
        )

        self.kokoro_speed_input.setDecimals(
            2
        )

        self.kokoro_speed_input.setSuffix(
            "x"
        )

        self.kokoro_speed_input.setValue(
            float(
                settings.get(
                    "kokoro_speed",
                    1.05,
                )
            )
        )

        layout.addWidget(
            self.kokoro_speed_label
        )

        layout.addWidget(
            self.kokoro_speed_input
        )

        # =====================================================
        # ELEVENLABS
        # =====================================================

        self.elevenlabs_voice_label = QLabel(
            "ElevenLabs Voice"
        )

        self.elevenlabs_voice_combo = QComboBox()

        self.elevenlabs_voice_combo.addItem(
            "Brian",
            BRIAN_VOICE_ID,
        )

        layout.addWidget(
            self.elevenlabs_voice_label
        )

        layout.addWidget(
            self.elevenlabs_voice_combo
        )

        self.api_key_label = QLabel(
            "ElevenLabs API Key"
        )

        self.elevenlabs_api_key_input = QLineEdit()

        self.elevenlabs_api_key_input.setEchoMode(
            QLineEdit.Password
        )

        self.elevenlabs_api_key_input.setPlaceholderText(
            "Enter your ElevenLabs API key"
        )

        self.elevenlabs_api_key_input.setText(
            settings.get(
                "elevenlabs_api_key",
                "",
            )
        )

        layout.addWidget(
            self.api_key_label
        )

        layout.addWidget(
            self.elevenlabs_api_key_input
        )

        self.voice_id_label = QLabel(
            "Voice ID"
        )

        self.elevenlabs_voice_id_input = QLineEdit()

        self.elevenlabs_voice_id_input.setText(
            settings.get(
                "elevenlabs_voice_id",
                BRIAN_VOICE_ID,
            )
        )

        layout.addWidget(
            self.voice_id_label
        )

        layout.addWidget(
            self.elevenlabs_voice_id_input
        )

        self.voice_provider_combo.currentIndexChanged.connect(
            self.update_voice_controls
        )

        self.elevenlabs_voice_combo.currentIndexChanged.connect(
            self.on_elevenlabs_voice_selected
        )

        layout.addSpacing(
            20
        )

        button_row = QHBoxLayout()

        self.preview_voice_button = QPushButton(
            "▶ Preview Voice"
        )

        self.save_voice_button = QPushButton(
            "Save Voice Settings"
        )

        self.preview_voice_button.clicked.connect(
            self.preview_selected_voice
        )

        self.save_voice_button.clicked.connect(
            self.save_voice_settings_gui
        )

        button_row.addWidget(
            self.preview_voice_button
        )

        button_row.addStretch()

        button_row.addWidget(
            self.save_voice_button
        )

        layout.addLayout(
            button_row
        )

        layout.addStretch()

        self.update_voice_controls()

    def load_piper_voices(
        self
    ):
        self.piper_voice_combo.clear()

        piper_folder = resource_file(
            "piper"
        )

        voices = []

        if os.path.exists(
            piper_folder
        ):
            try:
                for filename in os.listdir(
                    piper_folder
                ):
                    if filename.lower().endswith(
                        ".onnx"
                    ):
                        voices.append(
                            filename
                        )

            except Exception as error:
                print(
                    "Piper voice scan error:",
                    error,
                )

        if not voices:
            voices = [
                "en_US-lessac-medium.onnx"
            ]

        for voice in sorted(
            voices
        ):
            friendly = (
                voice
                .replace(
                    ".onnx",
                    "",
                )
                .replace(
                    "_",
                    " ",
                )
            )

            self.piper_voice_combo.addItem(
                friendly,
                voice,
            )

    def update_voice_controls(
        self
    ):
        provider = (
            self.voice_provider_combo
            .currentData()
        )

        using_piper = (
            provider == "piper"
        )

        using_kokoro = (
            provider == "kokoro"
        )

        using_elevenlabs = (
            provider == "elevenlabs"
        )

        self.piper_label.setVisible(
            using_piper
        )

        self.piper_voice_combo.setVisible(
            using_piper
        )

        self.kokoro_voice_label.setVisible(
            using_kokoro
        )

        self.kokoro_voice_combo.setVisible(
            using_kokoro
        )

        self.kokoro_speed_label.setVisible(
            using_kokoro
        )

        self.kokoro_speed_input.setVisible(
            using_kokoro
        )

        self.elevenlabs_voice_label.setVisible(
            using_elevenlabs
        )

        self.elevenlabs_voice_combo.setVisible(
            using_elevenlabs
        )

        self.api_key_label.setVisible(
            using_elevenlabs
        )

        self.elevenlabs_api_key_input.setVisible(
            using_elevenlabs
        )

        self.voice_id_label.setVisible(
            using_elevenlabs
        )

        self.elevenlabs_voice_id_input.setVisible(
            using_elevenlabs
        )

    def on_elevenlabs_voice_selected(
        self
    ):
        voice_id = (
            self.elevenlabs_voice_combo
            .currentData()
        )

        if voice_id:
            self.elevenlabs_voice_id_input.setText(
                voice_id
            )

    def build_current_voice_settings(
        self
    ):
        settings = (
            load_voice_settings()
        )

        settings[
            "provider"
        ] = (
            self.voice_provider_combo
            .currentData()
        )

        piper_voice = (
            self.piper_voice_combo
            .currentData()
        )

        if not piper_voice:
            piper_voice = (
                self.piper_voice_combo
                .currentText()
            )

        settings[
            "piper_voice"
        ] = piper_voice

        kokoro_voice = (
            self.kokoro_voice_combo
            .currentData()
        )

        if not kokoro_voice:
            kokoro_voice = (
                "bm_george"
            )

        settings[
            "kokoro_voice"
        ] = kokoro_voice

        settings[
            "kokoro_language"
        ] = "b"

        settings[
            "kokoro_speed"
        ] = (
            self.kokoro_speed_input.value()
        )

        settings[
            "kokoro_repo_id"
        ] = (
            "hexgrad/Kokoro-82M"
        )

        settings[
            "elevenlabs_api_key"
        ] = (
            self.elevenlabs_api_key_input
            .text()
            .strip()
        )

        settings[
            "elevenlabs_voice_name"
        ] = (
            self.elevenlabs_voice_combo
            .currentText()
        )

        settings[
            "elevenlabs_voice_id"
        ] = (
            self.elevenlabs_voice_id_input
            .text()
            .strip()
        )

        return settings

    def preview_selected_voice(
        self
    ):
        settings = (
            self.build_current_voice_settings()
        )

        if (
            settings[
                "provider"
            ] == "elevenlabs"
            and not settings[
                "elevenlabs_api_key"
            ]
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter your ElevenLabs API key first.",
            )

            return

        thread = threading.Thread(
            target=preview_voice,
            args=(
                settings,
            ),
            daemon=True,
        )

        thread.start()

    def save_voice_settings_gui(
        self
    ):
        settings = (
            self.build_current_voice_settings()
        )

        if (
            settings[
                "provider"
            ] == "elevenlabs"
            and not settings[
                "elevenlabs_api_key"
            ]
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter an ElevenLabs API key "
                "or choose another provider.",
            )

            return

        try:
            save_voice_settings(
                settings
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "Voice settings saved.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save voice settings:\n{error}",
            )

    # =========================================================
    # EMAIL
    # =========================================================

    def build_email_tab(
        self
    ):
        layout = QVBoxLayout(
            self.email_tab
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        title = QLabel(
            "Gmail"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Connect Gmail so JARVIS can send "
            "emails using your account."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        gmail_row = QHBoxLayout()

        gmail_row.addWidget(
            QLabel(
                "Connection status:"
            )
        )

        self.gmail_status = QLabel()

        gmail_row.addWidget(
            self.gmail_status
        )

        gmail_row.addStretch()

        self.gmail_connect_button = QPushButton(
            "Connect Gmail"
        )

        self.gmail_connect_button.clicked.connect(
            self.connect_gmail
        )

        gmail_row.addWidget(
            self.gmail_connect_button
        )

        layout.addLayout(
            gmail_row
        )

        self.update_gmail_status()

        layout.addSpacing(
            25
        )

        contacts_title = QLabel(
            "Contacts"
        )

        contacts_title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            contacts_title
        )

        contacts_description = QLabel(
            "Save contacts so JARVIS can resolve "
            "names when composing emails."
        )

        contacts_description.setWordWrap(
            True
        )

        layout.addWidget(
            contacts_description
        )

        add_row = QHBoxLayout()

        self.contact_name_input = QLineEdit()

        self.contact_name_input.setPlaceholderText(
            "Contact name"
        )

        self.contact_email_input = QLineEdit()

        self.contact_email_input.setPlaceholderText(
            "Email address"
        )

        add_button = QPushButton(
            "+ Add Contact"
        )

        add_button.clicked.connect(
            self.add_contact
        )

        add_row.addWidget(
            self.contact_name_input,
            1,
        )

        add_row.addWidget(
            self.contact_email_input,
            2,
        )

        add_row.addWidget(
            add_button
        )

        layout.addLayout(
            add_row
        )

        self.contacts_scroll = QScrollArea()

        self.contacts_scroll.setWidgetResizable(
            True
        )

        self.contacts_container = QWidget()

        self.contacts_layout = QVBoxLayout(
            self.contacts_container
        )

        self.contacts_layout.setAlignment(
            Qt.AlignTop
        )

        self.contacts_scroll.setWidget(
            self.contacts_container
        )

        layout.addWidget(
            self.contacts_scroll
        )

        contact_buttons = QHBoxLayout()

        reload_button = QPushButton(
            "Reload"
        )

        save_button = QPushButton(
            "Save Contacts"
        )

        reload_button.clicked.connect(
            self.load_contacts
        )

        save_button.clicked.connect(
            self.save_contacts
        )

        contact_buttons.addWidget(
            reload_button
        )

        contact_buttons.addStretch()

        contact_buttons.addWidget(
            save_button
        )

        layout.addLayout(
            contact_buttons
        )

        self.load_contacts()

    def update_gmail_status(
        self
    ):
        connected = os.path.exists(
            GMAIL_TOKEN_FILE
        )

        self.gmail_status.setText(
            "Connected ✓"
            if connected
            else "Not connected"
        )

        self.gmail_connect_button.setText(
            "Reconnect Gmail"
            if connected
            else "Connect Gmail"
        )

    def connect_gmail(
        self
    ):
        self.gmail_connect_button.setEnabled(
            False
        )

        self.gmail_status.setText(
            "Connecting..."
        )

        thread = threading.Thread(
            target=self.connect_gmail_worker,
            daemon=True,
        )

        thread.start()

    def connect_gmail_worker(
        self
    ):
        try:
            get_gmail_service()

            self.signals.gmail_finished.emit(
                True,
                "",
            )

        except Exception as error:
            self.signals.gmail_finished.emit(
                False,
                str(
                    error
                ),
            )

    def gmail_connection_finished(
        self,
        success,
        error,
    ):
        self.gmail_connect_button.setEnabled(
            True
        )

        self.update_gmail_status()

        if success:
            QMessageBox.information(
                self,
                "JARVIS",
                "Gmail connected successfully.",
            )

        else:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Gmail connection failed.\n\n"
                f"{error}",
            )

    # =========================================================
    # CONTACTS
    # =========================================================

    def clear_contacts(
        self
    ):
        while self.contacts_layout.count():
            item = self.contacts_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.contact_rows.clear()

    def load_contacts(
        self
    ):
        self.clear_contacts()

        contacts = self.load_json(
            CONTACTS_FILE
        )

        for name, email in sorted(
            contacts.items()
        ):
            self.create_contact_row(
                name,
                email,
            )

    def create_contact_row(
        self,
        name="",
        email="",
    ):
        row = QWidget()

        row_layout = QHBoxLayout(
            row
        )

        name_input = QLineEdit(
            name
        )

        email_input = QLineEdit(
            email
        )

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setFixedWidth(
            80
        )

        delete_button.clicked.connect(
            lambda:
            self.delete_contact_row(
                row
            )
        )

        row_layout.addWidget(
            name_input,
            1,
        )

        row_layout.addWidget(
            email_input,
            2,
        )

        row_layout.addWidget(
            delete_button
        )

        self.contacts_layout.addWidget(
            row
        )

        self.contact_rows.append(
            (
                row,
                name_input,
                email_input,
            )
        )

    def add_contact(
        self
    ):
        name = (
            self.contact_name_input
            .text()
            .lower()
            .strip()
        )

        email = (
            self.contact_email_input
            .text()
            .strip()
        )

        if (
            not name
            or not email
            or "@" not in email
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter a valid contact name and email.",
            )

            return

        self.create_contact_row(
            name,
            email,
        )

        self.contact_name_input.clear()

        self.contact_email_input.clear()

    def delete_contact_row(
        self,
        row,
    ):
        for contact in list(
            self.contact_rows
        ):
            if contact[
                0
            ] is row:

                self.contact_rows.remove(
                    contact
                )

                break

        self.contacts_layout.removeWidget(
            row
        )

        row.deleteLater()

    def save_contacts(
        self
    ):
        contacts = {}

        for (
            _,
            name_input,
            email_input,
        ) in self.contact_rows:

            name = (
                name_input
                .text()
                .lower()
                .strip()
            )

            email = (
                email_input
                .text()
                .strip()
            )

            if (
                not name
                and not email
            ):
                continue

            if (
                not name
                or "@" not in email
            ):
                QMessageBox.warning(
                    self,
                    "JARVIS",
                    "One or more contacts is invalid.",
                )

                return

            contacts[
                name
            ] = email

        self.save_json(
            CONTACTS_FILE,
            contacts,
        )

        QMessageBox.information(
            self,
            "JARVIS",
            "Contacts saved.",
        )

    # =========================================================
    # APPEARANCE
    # =========================================================

    def build_appearance_tab(
        self
    ):
        layout = QVBoxLayout(
            self.appearance_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "Theme Colors"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Customize the entire JARVIS interface."
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            25
        )

        (
            self.color_1_value,
            self.color_1_preview,
        ) = self.make_color_row(
            layout,
            "Background",
            self.theme[
                "color_1"
            ],
            self.choose_color_1,
        )

        (
            self.color_2_value,
            self.color_2_preview,
        ) = self.make_color_row(
            layout,
            "Accent",
            self.theme[
                "color_2"
            ],
            self.choose_color_2,
        )

        buttons = QHBoxLayout()

        reset_button = QPushButton(
            "Reset Default"
        )

        save_button = QPushButton(
            "Save Theme"
        )

        reset_button.clicked.connect(
            self.reset_theme
        )

        save_button.clicked.connect(
            self.save_theme_clicked
        )

        buttons.addWidget(
            reset_button
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

        layout.addStretch()

        self.update_color_previews()

    def make_color_row(
        self,
        parent_layout,
        label_text,
        value,
        callback,
    ):
        row = QHBoxLayout()

        label = QLabel(
            label_text
        )

        value_label = QLabel(
            value
        )

        preview = QLabel()

        preview.setFixedSize(
            40,
            40,
        )

        button = QPushButton(
            "Choose Color"
        )

        button.clicked.connect(
            callback
        )

        row.addWidget(
            label
        )

        row.addStretch()

        row.addWidget(
            value_label
        )

        row.addWidget(
            preview
        )

        row.addWidget(
            button
        )

        parent_layout.addLayout(
            row
        )

        return (
            value_label,
            preview,
        )

    def choose_color_1(
        self
    ):
        color = QColorDialog.getColor(
            QColor(
                self.theme[
                    "color_1"
                ]
            ),
            self,
            "Choose Background Color",
        )

        if color.isValid():
            self.theme[
                "color_1"
            ] = color.name()

            self.update_color_previews()

            emit_theme_preview(
                self.theme
            )

    def choose_color_2(
        self
    ):
        color = QColorDialog.getColor(
            QColor(
                self.theme[
                    "color_2"
                ]
            ),
            self,
            "Choose Accent Color",
        )

        if color.isValid():
            self.theme[
                "color_2"
            ] = color.name()

            self.update_color_previews()

            emit_theme_preview(
                self.theme
            )

    def update_color_previews(
        self
    ):
        self.color_1_value.setText(
            self.theme[
                "color_1"
            ]
        )

        self.color_2_value.setText(
            self.theme[
                "color_2"
            ]
        )

        self.color_1_preview.setStyleSheet(
            f"""
            background-color:
                {self.theme["color_1"]};

            border:
                1px solid
                {self.theme["color_2"]};
            """
        )

        self.color_2_preview.setStyleSheet(
            f"""
            background-color:
                {self.theme["color_2"]};

            border:
                1px solid
                {self.theme["color_2"]};
            """
        )

    def save_theme_clicked(
        self
    ):
        self.theme = persist_theme(
            self.theme
        )

        QMessageBox.information(
            self,
            "JARVIS",
            "Theme saved.",
        )

    def reset_theme(
        self
    ):
        self.theme = (
            DEFAULT_THEME.copy()
        )

        self.update_color_previews()

        emit_theme_preview(
            self.theme
        )

    # =========================================================
    # JSON
    # =========================================================

    def load_json(
        self,
        path,
    ):
        if not os.path.exists(
            path
        ):
            return {}

        try:
            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(
                    file
                )

        except Exception as error:
            print(
                "Settings load error:",
                error,
            )

            return {}

    def save_json(
        self,
        path,
        data,
    ):
        os.makedirs(
            os.path.dirname(
                path
            ),
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
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

        if hasattr(
            self,
            "color_1_value",
        ):
            self.update_color_previews()

        self.apply_settings_theme(
            self.theme
        )

    def apply_settings_theme(
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
            QWidget {{
                background-color: {background};
                color: {accent};
            }}

            QLabel {{
                color: {accent};
                font-size: 14px;
            }}

            QCheckBox {{
                color: {accent};
                font-size: 14px;
                spacing: 8px;
            }}

            QLineEdit,
            QTextEdit,
            QComboBox,
            QDoubleSpinBox {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 6px;
                padding: 8px;
            }}

            QPushButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 7px;
                padding: 8px 14px;
            }}

            QPushButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QPushButton:disabled {{
                color: gray;
                border-color: gray;
            }}

            QTabWidget::pane {{
                border: 1px solid {accent};
            }}

            QTabBar::tab {{
                color: {accent};
                background-color: {background};
                border: 1px solid {accent};
                padding: 9px 12px;
            }}

            QTabBar::tab:selected {{
                background-color: {accent};
                color: {background};
            }}

            QScrollArea {{
                border: 1px solid {accent};
            }}

            QScrollBar:vertical {{
                background: {background};
                width: 12px;
            }}

            QScrollBar::handle:vertical {{
                background: {accent};
                min-height: 25px;
                border-radius: 5px;
            }}

            QScrollBar:horizontal {{
                background: {background};
                height: 12px;
            }}

            QScrollBar::handle:horizontal {{
                background: {accent};
                min-width: 25px;
                border-radius: 5px;
            }}
            """
        )