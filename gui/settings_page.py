import json
import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QMessageBox,
    QTabWidget,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox
)

from core.ai_mode import (
    load_ai_settings,
    save_ai_settings
)


DETECTED_FILE = "data/apps_detected.json"
ALIASES_FILE = "data/apps.json"
THEME_FILE = "data/theme.json"
CONTACTS_FILE = "data/contacts.json"
GMAIL_TOKEN_FILE = "data/gmail_token.json"


DEFAULT_THEME = {
    "color_1": "#05080c",
    "color_2": "#7fe7ff"
}


class SettingsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("JARVIS Settings")
        self.resize(950, 720)

        self.alias_inputs = {}
        self.app_rows = []
        self.contact_rows = []

        self.theme = self.load_theme()

        self.build_ui()
        self.apply_settings_theme()


    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        top_bar = QHBoxLayout()

        self.back_button = QPushButton("← Back")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.close)

        title = QLabel("JARVIS SETTINGS")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        top_bar.addWidget(title)
        top_bar.addStretch()

        spacer = QWidget()
        spacer.setFixedWidth(100)

        top_bar.addWidget(spacer)

        main_layout.addLayout(top_bar)

        # =========================
        # TABS
        # =========================

        self.tabs = QTabWidget()

        self.apps_tab = QWidget()
        self.ai_tab = QWidget()
        self.email_tab = QWidget()
        self.appearance_tab = QWidget()

        self.tabs.addTab(
            self.apps_tab,
            "Apps"
        )

        self.tabs.addTab(
            self.ai_tab,
            "AI"
        )

        self.tabs.addTab(
            self.email_tab,
            "Email"
        )

        self.tabs.addTab(
            self.appearance_tab,
            "Appearance"
        )

        main_layout.addWidget(
            self.tabs
        )

        self.build_apps_tab()
        self.build_ai_tab()
        self.build_email_tab()
        self.build_appearance_tab()


    # =========================================================
    # AI TAB
    # =========================================================

    def build_ai_tab(self):
        layout = QVBoxLayout(
            self.ai_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        title = QLabel(
            "AI Models"
        )

        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose which Ollama model JARVIS uses "
            "for Normal Mode and Think Mode."
        )

        description.setWordWrap(True)

        layout.addWidget(
            description
        )

        layout.addSpacing(
            20
        )

        ai_settings = load_ai_settings()

        # =========================
        # NORMAL MODEL
        # =========================

        normal_row = QHBoxLayout()

        normal_label = QLabel(
            "Normal Mode Model"
        )

        self.normal_model_combo = QComboBox()

        self.normal_model_combo.setEditable(
            True
        )

        self.normal_model_combo.addItems([
            "qwen2.5:1.5b",
            "llama3.2:3b",
            "gemma3:4b"
        ])

        self.normal_model_combo.setCurrentText(
            ai_settings["normal_model"]
        )

        normal_row.addWidget(
            normal_label
        )

        normal_row.addStretch()

        normal_row.addWidget(
            self.normal_model_combo,
            2
        )

        layout.addLayout(
            normal_row
        )

        layout.addSpacing(
            12
        )

        # =========================
        # THINK MODEL
        # =========================

        think_row = QHBoxLayout()

        think_label = QLabel(
            "Think Mode Model"
        )

        self.think_model_combo = QComboBox()

        self.think_model_combo.setEditable(
            True
        )

        self.think_model_combo.addItems([
            "gemma3:4b",
            "llama3.2:3b",
            "qwen2.5:1.5b"
        ])

        self.think_model_combo.setCurrentText(
            ai_settings["think_model"]
        )

        think_row.addWidget(
            think_label
        )

        think_row.addStretch()

        think_row.addWidget(
            self.think_model_combo,
            2
        )

        layout.addLayout(
            think_row
        )

        layout.addSpacing(
            20
        )

        # =========================
        # TEMPERATURE
        # =========================

        temp_row = QHBoxLayout()

        temp_label = QLabel(
            "Temperature"
        )

        self.temperature_input = QDoubleSpinBox()

        self.temperature_input.setRange(
            0.0,
            2.0
        )

        self.temperature_input.setSingleStep(
            0.1
        )

        self.temperature_input.setDecimals(
            1
        )

        self.temperature_input.setValue(
            float(
                ai_settings["temperature"]
            )
        )

        temp_row.addWidget(
            temp_label
        )

        temp_row.addStretch()

        temp_row.addWidget(
            self.temperature_input
        )

        layout.addLayout(
            temp_row
        )

        explanation = QLabel(
            "Lower temperature = more focused and predictable.\n"
            "Higher temperature = more creative and varied."
        )

        explanation.setWordWrap(True)

        layout.addWidget(
            explanation
        )

        layout.addSpacing(
            25
        )

        # =========================
        # SAVE BUTTON
        # =========================

        buttons = QHBoxLayout()

        self.reset_ai_button = QPushButton(
            "Reset Defaults"
        )

        self.save_ai_button = QPushButton(
            "Save AI Settings"
        )

        self.reset_ai_button.clicked.connect(
            self.reset_ai_settings
        )

        self.save_ai_button.clicked.connect(
            self.save_ai_settings_gui
        )

        buttons.addWidget(
            self.reset_ai_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.save_ai_button
        )

        layout.addLayout(
            buttons
        )

        layout.addStretch()


    def save_ai_settings_gui(self):
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

        temperature = (
            self.temperature_input
            .value()
        )

        if not normal_model:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Normal Mode model cannot be empty."
            )
            return

        if not think_model:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Think Mode model cannot be empty."
            )
            return

        settings = {
            "normal_model": normal_model,
            "think_model": think_model,
            "temperature": temperature
        }

        try:
            save_ai_settings(
                settings
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "AI settings saved."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save AI settings:\n{error}"
            )


    def reset_ai_settings(self):
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
    # APPS TAB
    # =========================================================

    def build_apps_tab(self):
        layout = QVBoxLayout(
            self.apps_tab
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

        button_bar = QHBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh Apps"
        )

        self.rescan_button = QPushButton(
            "Rescan Apps"
        )

        self.save_button = QPushButton(
            "Save Aliases"
        )

        self.refresh_button.clicked.connect(
            self.load_apps
        )

        self.rescan_button.clicked.connect(
            self.rescan_apps
        )

        self.save_button.clicked.connect(
            self.save_aliases
        )

        button_bar.addWidget(
            self.refresh_button
        )

        button_bar.addWidget(
            self.rescan_button
        )

        button_bar.addStretch()

        button_bar.addWidget(
            self.save_button
        )

        layout.addLayout(
            button_bar
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
            2
        )

        headers.addWidget(
            alias_header,
            1
        )

        layout.addLayout(
            headers
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.apps_container = QWidget()

        self.apps_layout = QVBoxLayout(
            self.apps_container
        )

        self.scroll.setWidget(
            self.apps_container
        )

        layout.addWidget(
            self.scroll
        )

        self.load_apps()


    # =========================================================
    # EMAIL TAB
    # =========================================================

    def build_email_tab(self):
        layout = QVBoxLayout(
            self.email_tab
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        gmail_title = QLabel(
            "Gmail"
        )

        gmail_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            gmail_title
        )

        gmail_row = QHBoxLayout()

        gmail_label = QLabel(
            "Connection status:"
        )

        self.gmail_status = QLabel()

        gmail_row.addWidget(
            gmail_label
        )

        gmail_row.addWidget(
            self.gmail_status
        )

        gmail_row.addStretch()

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

        contacts_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            contacts_title
        )

        description = QLabel(
            "Save contacts so you can type a name "
            "instead of a full email address."
        )

        description.setWordWrap(True)

        layout.addWidget(
            description
        )

        layout.addSpacing(
            10
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

        self.add_contact_button = QPushButton(
            "+ Add Contact"
        )

        self.add_contact_button.clicked.connect(
            self.add_contact
        )

        add_row.addWidget(
            self.contact_name_input,
            1
        )

        add_row.addWidget(
            self.contact_email_input,
            2
        )

        add_row.addWidget(
            self.add_contact_button
        )

        layout.addLayout(
            add_row
        )

        headers = QHBoxLayout()

        name_header = QLabel(
            "Name"
        )

        email_header = QLabel(
            "Email"
        )

        name_header.setStyleSheet(
            "font-weight: bold;"
        )

        email_header.setStyleSheet(
            "font-weight: bold;"
        )

        headers.addWidget(
            name_header,
            1
        )

        headers.addWidget(
            email_header,
            2
        )

        headers.addStretch()

        layout.addLayout(
            headers
        )

        self.contacts_scroll = QScrollArea()
        self.contacts_scroll.setWidgetResizable(True)

        self.contacts_container = QWidget()

        self.contacts_layout = QVBoxLayout(
            self.contacts_container
        )

        self.contacts_scroll.setWidget(
            self.contacts_container
        )

        layout.addWidget(
            self.contacts_scroll
        )

        contact_buttons = QHBoxLayout()

        self.reload_contacts_button = QPushButton(
            "Reload"
        )

        self.save_contacts_button = QPushButton(
            "Save Contacts"
        )

        self.reload_contacts_button.clicked.connect(
            self.load_contacts
        )

        self.save_contacts_button.clicked.connect(
            self.save_contacts
        )

        contact_buttons.addWidget(
            self.reload_contacts_button
        )

        contact_buttons.addStretch()

        contact_buttons.addWidget(
            self.save_contacts_button
        )

        layout.addLayout(
            contact_buttons
        )

        self.load_contacts()


    # =========================================================
    # APPEARANCE TAB
    # =========================================================

    def build_appearance_tab(self):
        layout = QVBoxLayout(
            self.appearance_tab
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        title = QLabel(
            "Theme Colors"
        )

        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        description = QLabel(
            "Customize the main colors used by JARVIS."
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            25
        )

        color_1_row = QHBoxLayout()

        color_1_label = QLabel(
            "Color 1 - Background"
        )

        self.color_1_value = QLabel(
            self.theme["color_1"]
        )

        self.color_1_preview = QLabel()
        self.color_1_preview.setFixedSize(
            40,
            40
        )

        self.color_1_button = QPushButton(
            "Choose Color"
        )

        color_1_row.addWidget(
            color_1_label
        )

        color_1_row.addStretch()

        color_1_row.addWidget(
            self.color_1_value
        )

        color_1_row.addWidget(
            self.color_1_preview
        )

        color_1_row.addWidget(
            self.color_1_button
        )

        layout.addLayout(
            color_1_row
        )

        color_2_row = QHBoxLayout()

        color_2_label = QLabel(
            "Color 2 - Accent"
        )

        self.color_2_value = QLabel(
            self.theme["color_2"]
        )

        self.color_2_preview = QLabel()
        self.color_2_preview.setFixedSize(
            40,
            40
        )

        self.color_2_button = QPushButton(
            "Choose Color"
        )

        color_2_row.addWidget(
            color_2_label
        )

        color_2_row.addStretch()

        color_2_row.addWidget(
            self.color_2_value
        )

        color_2_row.addWidget(
            self.color_2_preview
        )

        color_2_row.addWidget(
            self.color_2_button
        )

        layout.addLayout(
            color_2_row
        )

        layout.addSpacing(
            30
        )

        theme_buttons = QHBoxLayout()

        self.reset_theme_button = QPushButton(
            "Reset Default"
        )

        self.save_theme_button = QPushButton(
            "Save Theme"
        )

        theme_buttons.addWidget(
            self.reset_theme_button
        )

        theme_buttons.addStretch()

        theme_buttons.addWidget(
            self.save_theme_button
        )

        layout.addLayout(
            theme_buttons
        )

        layout.addStretch()

        self.color_1_button.clicked.connect(
            self.choose_color_1
        )

        self.color_2_button.clicked.connect(
            self.choose_color_2
        )

        self.save_theme_button.clicked.connect(
            self.save_theme
        )

        self.reset_theme_button.clicked.connect(
            self.reset_theme
        )

        self.update_color_previews()


    # =========================================================
    # JSON
    # =========================================================

    def load_json(self, path):
        if not os.path.exists(path):
            return {}

        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except Exception as error:
            print(
                f"Settings load error: {error}"
            )
            return {}


    # =========================================================
    # APP FUNCTIONS
    # =========================================================

    def clear_app_list(self):
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.alias_inputs.clear()
        self.app_rows.clear()


    def load_apps(self):
        self.clear_app_list()

        detected = self.load_json(
            DETECTED_FILE
        )

        aliases = self.load_json(
            ALIASES_FILE
        )

        reverse_aliases = {}

        for alias, target in aliases.items():
            reverse_aliases[target] = alias

        sorted_apps = sorted(
            detected.items(),
            key=lambda item: item[0].lower()
        )

        for app_name, app_path in sorted_apps:
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
                    ""
                )
            )

            alias_input.setPlaceholderText(
                "Assign name..."
            )

            row_layout.addWidget(
                app_label,
                2
            )

            row_layout.addWidget(
                alias_input,
                1
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
                    row
                )
            )

        self.apps_layout.addStretch()

        self.filter_apps(
            self.search_box.text()
        )


    def filter_apps(self, text):
        search = text.lower().strip()

        for (
            app_name,
            app_path,
            row
        ) in self.app_rows:

            row.setVisible(
                search in app_name
                or search in app_path
            )


    def save_aliases(self):
        aliases = {}

        for (
            app_path,
            input_box
        ) in self.alias_inputs.items():

            alias = (
                input_box.text()
                .lower()
                .strip()
            )

            if alias:
                aliases[alias] = app_path

        os.makedirs(
            "data",
            exist_ok=True
        )

        try:
            with open(
                ALIASES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    aliases,
                    file,
                    indent=4
                )

            QMessageBox.information(
                self,
                "JARVIS",
                "App aliases saved."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save aliases:\n{error}"
            )


    def rescan_apps(self):
        try:
            subprocess.run(
                [
                    sys.executable,
                    "core/app_scanner.py"
                ],
                check=True
            )

            self.load_apps()

            QMessageBox.information(
                self,
                "JARVIS",
                "App scan complete."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"App scan failed:\n{error}"
            )


    # =========================================================
    # EMAIL / CONTACT FUNCTIONS
    # =========================================================

    def update_gmail_status(self):
        if os.path.exists(
            GMAIL_TOKEN_FILE
        ):
            self.gmail_status.setText(
                "Configured ✓"
            )
        else:
            self.gmail_status.setText(
                "Not configured"
            )


    def clear_contacts(self):
        while self.contacts_layout.count():
            item = self.contacts_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.contact_rows.clear()


    def load_contacts(self):
        self.clear_contacts()

        contacts = self.load_json(
            CONTACTS_FILE
        )

        for name, email in sorted(
            contacts.items()
        ):
            self.create_contact_row(
                name,
                email
            )

        self.contacts_layout.addStretch()


    def create_contact_row(
        self,
        name="",
        email=""
    ):
        row = QWidget()

        row_layout = QHBoxLayout(
            row
        )

        name_input = QLineEdit()
        name_input.setText(
            name
        )

        email_input = QLineEdit()
        email_input.setText(
            email
        )

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setFixedWidth(
            80
        )

        delete_button.clicked.connect(
            lambda: self.delete_contact_row(
                row
            )
        )

        row_layout.addWidget(
            name_input,
            1
        )

        row_layout.addWidget(
            email_input,
            2
        )

        row_layout.addWidget(
            delete_button
        )

        self.contacts_layout.insertWidget(
            max(
                0,
                self.contacts_layout.count() - 1
            ),
            row
        )

        self.contact_rows.append(
            (
                row,
                name_input,
                email_input
            )
        )


    def add_contact(self):
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

        if not name or not email:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter both a contact name and email."
            )
            return

        if "@" not in email:
            QMessageBox.warning(
                self,
                "JARVIS",
                "That does not look like a valid email address."
            )
            return

        self.create_contact_row(
            name,
            email
        )

        self.contact_name_input.clear()
        self.contact_email_input.clear()


    def delete_contact_row(
        self,
        row
    ):
        for contact in list(
            self.contact_rows
        ):
            if contact[0] is row:
                self.contact_rows.remove(
                    contact
                )
                break

        row.deleteLater()


    def save_contacts(self):
        contacts = {}

        for (
            row,
            name_input,
            email_input
        ) in self.contact_rows:

            name = (
                name_input.text()
                .lower()
                .strip()
            )

            email = (
                email_input.text()
                .strip()
            )

            if not name and not email:
                continue

            if not name or "@" not in email:
                QMessageBox.warning(
                    self,
                    "JARVIS",
                    "One or more contacts has an invalid name or email."
                )
                return

            contacts[name] = email

        os.makedirs(
            "data",
            exist_ok=True
        )

        try:
            with open(
                CONTACTS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    contacts,
                    file,
                    indent=4
                )

            QMessageBox.information(
                self,
                "JARVIS",
                "Contacts saved."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save contacts:\n{error}"
            )


    # =========================================================
    # THEME FUNCTIONS
    # =========================================================

    def load_theme(self):
        if not os.path.exists(
            THEME_FILE
        ):
            return DEFAULT_THEME.copy()

        try:
            with open(
                THEME_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved_theme = json.load(
                    file
                )

            return {
                "color_1": saved_theme.get(
                    "color_1",
                    DEFAULT_THEME["color_1"]
                ),
                "color_2": saved_theme.get(
                    "color_2",
                    DEFAULT_THEME["color_2"]
                )
            }

        except Exception:
            return DEFAULT_THEME.copy()


    def choose_color_1(self):
        color = QColorDialog.getColor(
            QColor(
                self.theme["color_1"]
            ),
            self,
            "Choose Background Color"
        )

        if color.isValid():
            self.theme["color_1"] = (
                color.name()
            )

            self.update_color_previews()
            self.apply_settings_theme()


    def choose_color_2(self):
        color = QColorDialog.getColor(
            QColor(
                self.theme["color_2"]
            ),
            self,
            "Choose Accent Color"
        )

        if color.isValid():
            self.theme["color_2"] = (
                color.name()
            )

            self.update_color_previews()
            self.apply_settings_theme()


    def update_color_previews(self):
        self.color_1_value.setText(
            self.theme["color_1"]
        )

        self.color_2_value.setText(
            self.theme["color_2"]
        )

        self.color_1_preview.setStyleSheet(
            f"""
            background-color: {self.theme["color_1"]};
            border: 1px solid {self.theme["color_2"]};
            """
        )

        self.color_2_preview.setStyleSheet(
            f"""
            background-color: {self.theme["color_2"]};
            border: 1px solid {self.theme["color_2"]};
            """
        )


    def save_theme(self):
        os.makedirs(
            "data",
            exist_ok=True
        )

        try:
            with open(
                THEME_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.theme,
                    file,
                    indent=4
                )

            QMessageBox.information(
                self,
                "JARVIS",
                "Theme saved."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save theme:\n{error}"
            )


    def reset_theme(self):
        self.theme = DEFAULT_THEME.copy()

        self.update_color_previews()
        self.apply_settings_theme()


    # =========================================================
    # APPLY THEME
    # =========================================================

    def apply_settings_theme(self):
        background = self.theme[
            "color_1"
        ]

        accent = self.theme[
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

            QLineEdit,
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

            QTabWidget::pane {{
                border: 1px solid {accent};
            }}

            QTabBar::tab {{
                color: {accent};
                background-color: {background};
                border: 1px solid {accent};
                padding: 9px 20px;
            }}

            QTabBar::tab:selected {{
                background-color: {accent};
                color: {background};
            }}

            QScrollArea {{
                border: 1px solid {accent};
            }}
            """
        )