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
    QColorDialog
)


DETECTED_FILE = "data/apps_detected.json"
ALIASES_FILE = "data/apps.json"
THEME_FILE = "data/theme.json"


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

        self.theme = self.load_theme()

        self.build_ui()
        self.apply_settings_theme()

    # =========================
    # BUILD UI
    # =========================

    def build_ui(self):
        main_layout = QVBoxLayout(self)

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

        self.back_button = QPushButton("← Back")
        self.back_button.setFixedWidth(100)

        self.back_button.clicked.connect(
            self.close
        )

        title = QLabel("JARVIS SETTINGS")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        top_bar.addWidget(
            self.back_button
        )

        top_bar.addStretch()

        top_bar.addWidget(
            title
        )

        top_bar.addStretch()

        spacer = QWidget()
        spacer.setFixedWidth(100)

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
        self.appearance_tab = QWidget()

        self.tabs.addTab(
            self.apps_tab,
            "Apps"
        )

        self.tabs.addTab(
            self.appearance_tab,
            "Appearance"
        )

        main_layout.addWidget(
            self.tabs
        )

        self.build_apps_tab()
        self.build_appearance_tab()

    # =========================
    # APPS TAB
    # =========================

    def build_apps_tab(self):
        layout = QVBoxLayout(
            self.apps_tab
        )

        # Search
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

        # Buttons
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

        # Headers
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

        # Scroll area
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

    # =========================
    # APPEARANCE TAB
    # =========================

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

        layout.addSpacing(25)

        # =========================
        # COLOR 1
        # =========================

        color_1_row = QHBoxLayout()

        color_1_label = QLabel(
            "Color 1 - Background"
        )

        self.color_1_value = QLabel(
            self.theme["color_1"]
        )

        self.color_1_button = QPushButton(
            "Choose Color"
        )

        self.color_1_preview = QLabel()
        self.color_1_preview.setFixedSize(
            40,
            40
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

        # =========================
        # COLOR 2
        # =========================

        color_2_row = QHBoxLayout()

        color_2_label = QLabel(
            "Color 2 - Accent"
        )

        self.color_2_value = QLabel(
            self.theme["color_2"]
        )

        self.color_2_button = QPushButton(
            "Choose Color"
        )

        self.color_2_preview = QLabel()
        self.color_2_preview.setFixedSize(
            40,
            40
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

        layout.addSpacing(30)

        # =========================
        # THEME BUTTONS
        # =========================

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

    # =========================
    # JSON
    # =========================

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

    # =========================
    # APP LIST
    # =========================

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

            existing_alias = reverse_aliases.get(
                app_path,
                ""
            )

            alias_input.setText(
                existing_alias
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

            if (
                search in app_name
                or search in app_path
            ):
                row.show()

            else:
                row.hide()

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

    # =========================
    # THEME
    # =========================

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
        self.theme = (
            DEFAULT_THEME.copy()
        )

        self.update_color_previews()
        self.apply_settings_theme()

    # =========================
    # SETTINGS WINDOW THEME
    # =========================

    def apply_settings_theme(self):
        background = (
            self.theme["color_1"]
        )

        accent = (
            self.theme["color_2"]
        )

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

            QLineEdit {{
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