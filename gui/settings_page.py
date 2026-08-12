import json
import os
import subprocess
import sys

from PySide6.QtCore import Qt

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
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
    QVBoxLayout,
    QWidget
)

from core.ai_mode import (
    load_ai_settings,
    save_ai_settings
)

from core.paths import (
    user_file
)

from gui.theme_manager import (
    DEFAULT_THEME,
    emit_theme_preview,
    load_theme,
    save_theme as persist_theme,
    theme_bus
)


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


class SettingsPage(QWidget):

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "JARVIS Settings"
        )

        self.resize(
            950,
            720
        )

        self.alias_inputs = {}
        self.app_rows = []
        self.contact_rows = []

        self.theme = load_theme()

        self.build_ui()

        self.apply_settings_theme(
            self.theme
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )


    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

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
    # APPS
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

        self.save_aliases_button = QPushButton(
            "Save Aliases"
        )

        self.refresh_button.clicked.connect(
            self.load_apps
        )

        self.rescan_button.clicked.connect(
            self.rescan_apps
        )

        self.save_aliases_button.clicked.connect(
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
            self.save_aliases_button
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

        self.apps_scroll = QScrollArea()

        self.apps_scroll.setWidgetResizable(
            True
        )

        self.apps_container = QWidget()

        self.apps_layout = QVBoxLayout(
            self.apps_container
        )

        self.apps_scroll.setWidget(
            self.apps_container
        )

        layout.addWidget(
            self.apps_scroll
        )

        self.load_apps()


    def clear_app_list(self):
        while self.apps_layout.count():
            item = (
                self.apps_layout
                .takeAt(
                    0
                )
            )

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

        reverse_aliases = {
            target: alias
            for alias, target
            in aliases.items()
        }

        for (
            app_name,
            app_path
        ) in sorted(
            detected.items(),
            key=lambda item:
            item[0].lower()
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


    def filter_apps(
        self,
        text
    ):
        search = (
            text
            .lower()
            .strip()
        )

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
                aliases
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
                f"Could not save aliases:\n"
                f"{error}"
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
                f"App scan failed:\n"
                f"{error}"
            )


    # =========================================================
    # AI
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

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose which Ollama model "
            "JARVIS uses for Normal Mode "
            "and Think Mode."
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
                "gemma3:4b"
            ]
        )

        self.normal_model_combo.setCurrentText(
            settings[
                "normal_model"
            ]
        )

        normal_row.addWidget(
            self.normal_model_combo,
            2
        )

        layout.addLayout(
            normal_row
        )

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
                "qwen2.5:1.5b"
            ]
        )

        self.think_model_combo.setCurrentText(
            settings[
                "think_model"
            ]
        )

        think_row.addWidget(
            self.think_model_combo,
            2
        )

        layout.addLayout(
            think_row
        )

        temp_row = QHBoxLayout()

        temp_row.addWidget(
            QLabel(
                "Temperature"
            )
        )

        temp_row.addStretch()

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
                settings[
                    "temperature"
                ]
            )
        )

        temp_row.addWidget(
            self.temperature_input
        )

        layout.addLayout(
            temp_row
        )

        explanation = QLabel(
            "Lower temperature = more "
            "focused and predictable.\n"
            "Higher temperature = more "
            "creative and varied."
        )

        explanation.setWordWrap(
            True
        )

        layout.addWidget(
            explanation
        )

        layout.addSpacing(
            25
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

        if (
            not normal_model
            or not think_model
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Both AI model fields must "
                "contain a model name."
            )

            return

        try:
            save_ai_settings(
                {
                    "normal_model":
                    normal_model,

                    "think_model":
                    think_model,

                    "temperature":
                    self.temperature_input.value()
                }
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
                f"Could not save AI settings:\n"
                f"{error}"
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
    # EMAIL
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

        gmail_title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            gmail_title
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

        description = QLabel(
            "Save contacts so you can "
            "type a name instead of a "
            "full email address."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
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
            1
        )

        add_row.addWidget(
            self.contact_email_input,
            2
        )

        add_row.addWidget(
            add_button
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

        self.contacts_scroll.setWidgetResizable(
            True
        )

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


    def update_gmail_status(self):
        self.gmail_status.setText(
            "Configured ✓"
            if os.path.exists(
                GMAIL_TOKEN_FILE
            )
            else "Not configured"
        )


    def clear_contacts(self):
        while self.contacts_layout.count():
            item = (
                self.contacts_layout
                .takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.contact_rows.clear()


    def load_contacts(self):
        self.clear_contacts()

        contacts = self.load_json(
            CONTACTS_FILE
        )

        for (
            name,
            email
        ) in sorted(
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
                self.contacts_layout.count()
                - 1
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

        if (
            not name
            or not email
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter both a contact "
                "name and email."
            )

            return

        if "@" not in email:
            QMessageBox.warning(
                self,
                "JARVIS",
                "That does not look like "
                "a valid email address."
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
            if contact[
                0
            ] is row:
                self.contact_rows.remove(
                    contact
                )

                break

        row.deleteLater()


    def save_contacts(self):
        contacts = {}

        for (
            _,
            name_input,
            email_input
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
                    "One or more contacts "
                    "has an invalid name "
                    "or email."
                )

                return

            contacts[
                name
            ] = email

        try:
            self.save_json(
                CONTACTS_FILE,
                contacts
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
                f"Could not save contacts:\n"
                f"{error}"
            )


    # =========================================================
    # APPEARANCE
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

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Change the JARVIS background "
            "and accent colors. Changes are "
            "previewed across the main window, "
            "orb, Help, and Settings."
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

        (
            self.color_1_value,
            self.color_1_preview,
            self.color_1_button
        ) = self.make_color_row(
            layout,
            "Color 1 - Background",
            self.theme[
                "color_1"
            ],
            self.choose_color_1
        )

        (
            self.color_2_value,
            self.color_2_preview,
            self.color_2_button
        ) = self.make_color_row(
            layout,
            "Color 2 - Accent",
            self.theme[
                "color_2"
            ],
            self.choose_color_2
        )

        layout.addSpacing(
            30
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
        callback
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
            40
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
            button
        )


    def choose_color_1(self):
        color = QColorDialog.getColor(
            QColor(
                self.theme[
                    "color_1"
                ]
            ),
            self,
            "Choose Background Color"
        )

        if color.isValid():
            self.theme[
                "color_1"
            ] = color.name()

            self.update_color_previews()

            self.apply_settings_theme(
                self.theme
            )

            emit_theme_preview(
                self.theme
            )


    def choose_color_2(self):
        color = QColorDialog.getColor(
            QColor(
                self.theme[
                    "color_2"
                ]
            ),
            self,
            "Choose Accent Color"
        )

        if color.isValid():
            self.theme[
                "color_2"
            ] = color.name()

            self.update_color_previews()

            self.apply_settings_theme(
                self.theme
            )

            emit_theme_preview(
                self.theme
            )


    def update_color_previews(self):
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


    def save_theme_clicked(self):
        try:
            self.theme = persist_theme(
                self.theme
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "Theme saved and "
                "applied everywhere."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                f"Could not save theme:\n"
                f"{error}"
            )


    def reset_theme(self):
        self.theme = (
            DEFAULT_THEME.copy()
        )

        self.update_color_previews()

        self.apply_settings_theme(
            self.theme
        )

        emit_theme_preview(
            self.theme
        )


    def on_theme_changed(
        self,
        theme
    ):
        self.theme = theme.copy()

        if hasattr(
            self,
            "color_1_value"
        ):
            self.update_color_previews()

        self.apply_settings_theme(
            self.theme
        )


    # =========================================================
    # JSON
    # =========================================================

    def load_json(
        self,
        path
    ):
        if not os.path.exists(
            path
        ):
            return {}

        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(
                    file
                )

        except Exception as error:
            print(
                f"Settings load error: "
                f"{error}"
            )

            return {}


    def save_json(
        self,
        path,
        data
    ):
        os.makedirs(
            os.path.dirname(
                path
            ),
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


    # =========================================================
    # THEME
    # =========================================================

    def apply_settings_theme(
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