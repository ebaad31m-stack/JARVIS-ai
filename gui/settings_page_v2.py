import json
import os
import platform

from PySide6.QtCore import (
    Qt,
    QTimer,
    QUrl,
)

from PySide6.QtGui import (
    QDesktopServices,
)

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from core.paths import user_file
from core.startup_manager import (
    is_windows_startup_enabled,
)
from core.personalization import (
    get_assistant_name,
)
from gui.settings_page import (
    SettingsPage as BaseSettingsPage,
)


PREFERENCES_FILE = user_file(
    "ui_preferences.json"
)


DEFAULT_PREFERENCES = {
    "always_on_top": False,
    "remember_tab": True,
    "focus_search": False,
    "compact_mode": False,
    "show_system_status": True,
    "show_conversation_center": True,
    "show_tips": True,
    "confirm_close": False,
    "open_dashboard": True,
    "tab_position": "left",
}


class SettingsPage(
    BaseSettingsPage
):

    def __init__(
        self,
        parent=None
    ):
        self.ui_preferences = self.load_ui_preferences()

        self.settings_search = None
        self.dashboard_status = None
        self.dashboard_tip = None

        super().__init__(
            parent
        )

        self.setWindowFlags(
            Qt.Window
        )

        self.setWindowModality(
            Qt.ApplicationModal
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            False
        )

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.setWindowTitle(
            f"{get_assistant_name()} Control Center"
        )

        self.setMinimumSize(
            1180,
            760
        )

        self.build_v2_header()

        self.build_control_center()

        self.build_advanced_preferences()

        self.apply_v2_style(
            self.theme
        )

        self.apply_tab_position()

        self.apply_window_preferences()

        self.restore_last_tab()

        self.refresh_dashboard()

    # =========================================================
    # PREFERENCES
    # =========================================================

    def load_ui_preferences(
        self
    ):
        preferences = DEFAULT_PREFERENCES.copy()

        try:

            if os.path.exists(
                PREFERENCES_FILE
            ):

                with open(
                    PREFERENCES_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:

                    saved = json.load(
                        file
                    )

                if isinstance(
                    saved,
                    dict
                ):

                    preferences.update(
                        saved
                    )

        except Exception as error:

            print(
                "UI preferences load error:",
                error
            )

        return preferences

    def save_ui_preferences(
        self
    ):
        try:

            folder = os.path.dirname(
                PREFERENCES_FILE
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            with open(
                PREFERENCES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.ui_preferences,
                    file,
                    indent=4
                )

        except Exception as error:

            print(
                "UI preferences save error:",
                error
            )

    # =========================================================
    # OVERRIDE THE BASE THEME CALL
    # =========================================================

    def apply_settings_theme(
        self,
        theme
    ):
        self.apply_v2_style(
            theme
        )

    # =========================================================
    # HEADER
    # =========================================================

    def build_v2_header(
        self
    ):
        main_layout = self.layout()

        if main_layout is None:
            return

        header = QFrame()

        header.setObjectName(
            "settingsHeader"
        )

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        header_layout.setSpacing(
            12
        )

        back_button = QPushButton(
            "← BACK"
        )

        back_button.setObjectName(
            "headerButton"
        )

        back_button.clicked.connect(
            self.close
        )

        header_layout.addWidget(
            back_button
        )

        title_box = QVBoxLayout()

        title = QLabel(
            get_assistant_name()
        )

        title.setObjectName(
            "headerTitle"
        )

        subtitle = QLabel(
            "CONTROL CENTER  •  SYSTEM CONFIGURATION"
        )

        subtitle.setObjectName(
            "headerSubtitle"
        )

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_box,
            1
        )

        status = QLabel(
            "● SYSTEM ONLINE"
        )

        status.setObjectName(
            "onlineBadge"
        )

        header_layout.addWidget(
            status
        )

        main_layout.insertWidget(
            0,
            header
        )

        search_bar = QFrame()

        search_layout = QHBoxLayout(
            search_bar
        )

        search_layout.setContentsMargins(
            0,
            4,
            0,
            6
        )

        self.settings_search = QLineEdit()

        self.settings_search.setPlaceholderText(
            "Search settings..."
        )

        self.settings_search.setClearButtonEnabled(
            True
        )

        self.settings_search.textChanged.connect(
            self.filter_settings_tabs
        )

        search_layout.addWidget(
            self.settings_search
        )

        main_layout.insertWidget(
            1,
            search_bar
        )

    # =========================================================
    # CONTROL CENTER
    # =========================================================

    def build_control_center(
        self
    ):
        dashboard = QWidget()

        layout = QVBoxLayout(
            dashboard
        )

        layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        layout.setSpacing(
            18
        )

        hero = QFrame()

        hero.setObjectName(
            "dashboardHero"
        )

        hero_layout = QVBoxLayout(
            hero
        )

        hero_layout.setContentsMargins(
            24,
            22,
            24,
            22
        )

        hero_title = QLabel(
            f"{get_assistant_name().upper()} CONTROL CENTER"
        )

        hero_title.setObjectName(
            "heroTitle"
        )

        hero_subtitle = QLabel(
            "Configure your assistant, interface, voice, AI, "
            "automation and system behavior from one place."
        )

        hero_subtitle.setObjectName(
            "heroSubtitle"
        )

        hero_subtitle.setWordWrap(
            True
        )

        hero_layout.addWidget(
            hero_title
        )

        hero_layout.addWidget(
            hero_subtitle
        )

        layout.addWidget(
            hero
        )

        cards = QHBoxLayout()

        cards.setSpacing(
            12
        )

        self.dashboard_status = QLabel()

        self.dashboard_status.setObjectName(
            "dashboardCard"
        )

        self.dashboard_status.setAlignment(
            Qt.AlignCenter
        )

        self.dashboard_status.setWordWrap(
            True
        )

        cards.addWidget(
            self.dashboard_status
        )

        self.dashboard_mode = QLabel(
            "AI MODE\n\nConfigured"
        )

        self.dashboard_mode.setObjectName(
            "dashboardCard"
        )

        self.dashboard_mode.setAlignment(
            Qt.AlignCenter
        )

        cards.addWidget(
            self.dashboard_mode
        )

        self.dashboard_theme = QLabel(
            "INTERFACE\n\nTheme ready"
        )

        self.dashboard_theme.setObjectName(
            "dashboardCard"
        )

        self.dashboard_theme.setAlignment(
            Qt.AlignCenter
        )

        cards.addWidget(
            self.dashboard_theme
        )

        layout.addLayout(
            cards
        )

        quick_title = QLabel(
            "QUICK ACTIONS"
        )

        quick_title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            quick_title
        )

        quick_row = QHBoxLayout()

        refresh_button = QPushButton(
            "↻ Refresh Status"
        )

        refresh_button.clicked.connect(
            self.refresh_dashboard
        )

        quick_row.addWidget(
            refresh_button
        )

        open_data_button = QPushButton(
            "▣ Open JARVIS Data"
        )

        open_data_button.clicked.connect(
            self.open_data_folder
        )

        quick_row.addWidget(
            open_data_button
        )

        reset_button = QPushButton(
            "⟳ Reset UI Preferences"
        )

        reset_button.clicked.connect(
            self.reset_ui_preferences
        )

        quick_row.addWidget(
            reset_button
        )

        layout.addLayout(
            quick_row
        )

        self.dashboard_tip = QFrame()

        self.dashboard_tip.setObjectName(
            "tipCard"
        )

        tip_layout = QVBoxLayout(
            self.dashboard_tip
        )

        tip_title = QLabel(
            "JARVIS TIP"
        )

        tip_title.setObjectName(
            "tipTitle"
        )

        tip_text = QLabel(
            "Use the search bar above to instantly find a "
            "setting instead of digging through every tab."
        )

        tip_text.setObjectName(
            "tipText"
        )

        tip_text.setWordWrap(
            True
        )

        tip_layout.addWidget(
            tip_title
        )

        tip_layout.addWidget(
            tip_text
        )

        layout.addWidget(
            self.dashboard_tip
        )

        layout.addStretch()

        self.tabs.insertTab(
            0,
            dashboard,
            "Control Center"
        )

    # =========================================================
    # ADVANCED PREFERENCES
    # =========================================================

    def build_advanced_preferences(
        self
    ):
        self.advanced_tab = QWidget()

        layout = QVBoxLayout(
            self.advanced_tab
        )

        layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        layout.setSpacing(
            14
        )

        title = QLabel(
            "Interface & Behavior"
        )

        title.setObjectName(
            "pageTitle"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Personalize how the JARVIS control center behaves."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            10
        )

        self.always_on_top_checkbox = QCheckBox(
            "Keep the Settings window above other windows"
        )

        self.always_on_top_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "always_on_top",
                    False
                )
            )
        )

        self.always_on_top_checkbox.toggled.connect(
            self.on_always_on_top_changed
        )

        layout.addWidget(
            self.always_on_top_checkbox
        )

        self.remember_tab_checkbox = QCheckBox(
            "Remember the last Settings page I opened"
        )

        self.remember_tab_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "remember_tab",
                    True
                )
            )
        )

        self.remember_tab_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.remember_tab_checkbox
        )

        self.focus_search_checkbox = QCheckBox(
            "Focus the Settings search box when opened"
        )

        self.focus_search_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "focus_search",
                    False
                )
            )
        )

        self.focus_search_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.focus_search_checkbox
        )

        self.compact_mode_checkbox = QCheckBox(
            "Use compact controls and tighter spacing"
        )

        self.compact_mode_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "compact_mode",
                    False
                )
            )
        )

        self.compact_mode_checkbox.toggled.connect(
            self.on_compact_mode_changed
        )

        layout.addWidget(
            self.compact_mode_checkbox
        )

        self.show_status_checkbox = QCheckBox(
            "Show live system status on Control Center"
        )

        self.show_status_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "show_system_status",
                    True
                )
            )
        )

        self.show_status_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.show_status_checkbox
        )

        self.show_conversation_checkbox = QCheckBox(
            "Show conversation center on the main JARVIS window"
        )

        self.show_conversation_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "show_conversation_center",
                    True
                )
            )
        )

        self.show_conversation_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.show_conversation_checkbox
        )

        self.show_tips_checkbox = QCheckBox(
            "Show JARVIS tips on Control Center"
        )

        self.show_tips_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "show_tips",
                    True
                )
            )
        )

        self.show_tips_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.show_tips_checkbox
        )

        self.confirm_close_checkbox = QCheckBox(
            "Ask before closing Settings"
        )

        self.confirm_close_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "confirm_close",
                    False
                )
            )
        )

        self.confirm_close_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.confirm_close_checkbox
        )

        self.open_dashboard_checkbox = QCheckBox(
            "Open Control Center automatically when Settings opens"
        )

        self.open_dashboard_checkbox.setChecked(
            bool(
                self.ui_preferences.get(
                    "open_dashboard",
                    True
                )
            )
        )

        self.open_dashboard_checkbox.toggled.connect(
            self.on_preference_changed
        )

        layout.addWidget(
            self.open_dashboard_checkbox
        )

        tab_position_title = QLabel(
            "Navigation position"
        )

        tab_position_title.setObjectName(
            "fieldLabel"
        )

        layout.addWidget(
            tab_position_title
        )

        self.tab_position_combo = QComboBox()

        self.tab_position_combo.addItem(
            "Left sidebar",
            "left"
        )

        self.tab_position_combo.addItem(
            "Top navigation",
            "top"
        )

        current_position = self.ui_preferences.get(
            "tab_position",
            "left"
        )

        index = self.tab_position_combo.findData(
            current_position
        )

        if index >= 0:
            self.tab_position_combo.setCurrentIndex(
                index
            )

        self.tab_position_combo.currentIndexChanged.connect(
            self.on_tab_position_changed
        )

        layout.addWidget(
            self.tab_position_combo
        )

        layout.addSpacing(
            14
        )

        data_button = QPushButton(
            "Open JARVIS Data Folder"
        )

        data_button.clicked.connect(
            self.open_data_folder
        )

        layout.addWidget(
            data_button
        )

        layout.addStretch()

        self.tabs.addTab(
            self.advanced_tab,
            "Interface"
        )

        self.tabs.currentChanged.connect(
            self.remember_current_tab
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def filter_settings_tabs(
        self,
        text
    ):
        query = (
            str(text or "")
            .lower()
            .strip()
        )

        bar = self.tabs.tabBar()

        for index in range(
            self.tabs.count()
        ):

            label = (
                self.tabs.tabText(
                    index
                )
                .lower()
            )

            visible = (
                not query
                or query in label
            )

            bar.setTabVisible(
                index,
                visible
            )

        current = self.tabs.currentIndex()

        if current >= 0 and not bar.isTabVisible(
            current
        ):

            for index in range(
                self.tabs.count()
            ):

                if bar.isTabVisible(
                    index
                ):

                    self.tabs.setCurrentIndex(
                        index
                    )

                    break

    # =========================================================
    # TAB POSITION
    # =========================================================

    def apply_tab_position(
        self
    ):
        position = self.ui_preferences.get(
            "tab_position",
            "left"
        )

        if position == "top":

            self.tabs.setTabPosition(
                QTabWidget.North
            )

        else:

            self.tabs.setTabPosition(
                QTabWidget.West
            )

    def on_tab_position_changed(
        self
    ):
        self.ui_preferences[
            "tab_position"
        ] = self.tab_position_combo.currentData()

        self.apply_tab_position()

        self.save_ui_preferences()

    # =========================================================
    # WINDOW SETTINGS
    # =========================================================

    def apply_window_preferences(
        self
    ):
        self.on_always_on_top_changed(
            self.always_on_top_checkbox.isChecked()
        )

    def on_always_on_top_changed(
        self,
        enabled
    ):
        self.ui_preferences[
            "always_on_top"
        ] = bool(
            enabled
        )

        flags = self.windowFlags()

        if enabled:

            flags |= Qt.WindowStaysOnTopHint

        else:

            flags &= ~Qt.WindowStaysOnTopHint

        self.setWindowFlags(
            flags
        )

        self.showMaximized()

        self.save_ui_preferences()

    # =========================================================
    # PREFERENCE EVENTS
    # =========================================================

    def on_preference_changed(
        self
    ):
        self.ui_preferences.update(
            {
                "remember_tab":
                    self.remember_tab_checkbox.isChecked(),

                "focus_search":
                    self.focus_search_checkbox.isChecked(),

                "show_system_status":
                    self.show_status_checkbox.isChecked(),

                "show_conversation_center":
                    self.show_conversation_checkbox.isChecked(),

                "show_tips":
                    self.show_tips_checkbox.isChecked(),

                "confirm_close":
                    self.confirm_close_checkbox.isChecked(),

                "open_dashboard":
                    self.open_dashboard_checkbox.isChecked(),
            }
        )

        if self.dashboard_tip is not None:

            self.dashboard_tip.setVisible(
                self.ui_preferences[
                    "show_tips"
                ]
            )

        if self.dashboard_status is not None:

            self.dashboard_status.setVisible(
                self.ui_preferences[
                    "show_system_status"
                ]
            )

        self.save_ui_preferences()

    def on_compact_mode_changed(
        self,
        enabled
    ):
        self.ui_preferences[
            "compact_mode"
        ] = bool(
            enabled
        )

        self.save_ui_preferences()

        self.apply_v2_style(
            self.theme
        )

    # =========================================================
    # REMEMBER TAB
    # =========================================================

    def remember_current_tab(
        self,
        index
    ):
        if not self.ui_preferences.get(
            "remember_tab",
            True
        ):
            return

        self.ui_preferences[
            "last_tab"
        ] = self.tabs.tabText(
            index
        )

        self.save_ui_preferences()

    def restore_last_tab(
        self
    ):
        target = "Control Center"

        if self.ui_preferences.get(
            "remember_tab",
            True
        ):

            target = self.ui_preferences.get(
                "last_tab",
                target
            )

        for index in range(
            self.tabs.count()
        ):

            if self.tabs.tabText(
                index
            ) == target:

                self.tabs.setCurrentIndex(
                    index
                )

                break

        if self.ui_preferences.get(
            "open_dashboard",
            True
        ):

            self.tabs.setCurrentIndex(
                0
            )

        if self.ui_preferences.get(
            "focus_search",
            False
        ):

            QTimer.singleShot(
                300,
                self.focus_settings_search
            )

    def focus_settings_search(
        self
    ):
        if self.settings_search is not None:

            self.settings_search.setFocus()

            self.settings_search.selectAll()

    # =========================================================
    # DASHBOARD
    # =========================================================

    def refresh_dashboard(
        self
    ):
        assistant_name = get_assistant_name()

        self.setWindowTitle(
            f"{assistant_name} Control Center"
        )

        startup = (
            "ENABLED"
            if is_windows_startup_enabled()
            else "DISABLED"
        )

        self.dashboard_status.setText(
            "WINDOWS STARTUP\n\n"
            + startup
        )

        try:

            from core.ai_mode import (
                get_ai_mode_label,
            )

            mode = get_ai_mode_label()

        except Exception:

            mode = "Configured"

        self.dashboard_mode.setText(
            "AI MODE\n\n"
            + str(mode)
        )

        background = self.theme.get(
            "color_1",
            "#05080c"
        )

        accent = self.theme.get(
            "color_2",
            "#7fe7ff"
        )

        self.dashboard_theme.setText(
            "INTERFACE\n\n"
            f"{background} / {accent}"
        )

    # =========================================================
    # DATA FOLDER
    # =========================================================

    def open_data_folder(
        self
    ):
        path = os.path.dirname(
            PREFERENCES_FILE
        )

        os.makedirs(
            path,
            exist_ok=True
        )

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                path
            )
        )

    # =========================================================
    # RESET
    # =========================================================

    def reset_ui_preferences(
        self
    ):
        result = QMessageBox.question(
            self,
            "Reset JARVIS UI",
            "Reset all new Control Center preferences?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        self.ui_preferences = (
            DEFAULT_PREFERENCES.copy()
        )

        self.save_ui_preferences()

        self.always_on_top_checkbox.setChecked(
            False
        )

        self.remember_tab_checkbox.setChecked(
            True
        )

        self.focus_search_checkbox.setChecked(
            False
        )

        self.compact_mode_checkbox.setChecked(
            False
        )

        self.show_status_checkbox.setChecked(
            True
        )

        self.show_conversation_checkbox.setChecked(
            True
        )

        self.show_tips_checkbox.setChecked(
            True
        )

        self.confirm_close_checkbox.setChecked(
            False
        )

        self.open_dashboard_checkbox.setChecked(
            True
        )

        self.tab_position_combo.setCurrentIndex(
            0
        )

        self.apply_tab_position()

        self.tabs.setCurrentIndex(
            0
        )

        self.refresh_dashboard()

    # =========================================================
    # SHOW / HIDE
    # =========================================================

    def showEvent(
        self,
        event
    ):
        parent = self.parentWidget()

        if parent is not None:

            try:
                parent.hide()
            except Exception:
                pass

        super().showEvent(
            event
        )

        QTimer.singleShot(
            0,
            self._maximize_window
        )

    def _maximize_window(
        self
    ):
        try:

            self.showMaximized()

            self.raise_()

            self.activateWindow()

        except Exception:
            pass

    def closeEvent(
        self,
        event
    ):
        if (
            self.ui_preferences.get(
                "confirm_close",
                False
            )
        ):

            answer = QMessageBox.question(
                self,
                "Close Settings",
                "Close the JARVIS Control Center?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:

                event.ignore()

                return

        self.save_ui_preferences()

        try:

            super().closeEvent(
                event
            )

        finally:

            parent = self.parentWidget()

            if parent is not None:

                try:

                    parent.showNormal()

                    parent.raise_()

                    parent.activateWindow()

                except Exception:
                    pass

    # =========================================================
    # STYLE
    # =========================================================

    def apply_v2_style(
        self,
        theme
    ):
        background = theme.get(
            "color_1",
            "#05080c"
        )

        accent = theme.get(
            "color_2",
            "#7fe7ff"
        )

        compact = self.ui_preferences.get(
            "compact_mode",
            False
        )

        padding = 7 if compact else 11

        tab_height = 38 if compact else 50

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {background};
                color: {accent};
                font-family: "Segoe UI";
                font-size: 14px;
            }}

            #settingsHeader {{
                background-color: rgba(3, 14, 27, 245);
                border: 1px solid rgba(127, 231, 255, 90);
                border-radius: 18px;
            }}

            #headerTitle {{
                color: {accent};
                font-size: 25px;
                font-weight: 800;
            }}

            #headerSubtitle {{
                color: rgba(220, 245, 255, 170);
                font-size: 11px;
                letter-spacing: 1px;
            }}

            #onlineBadge {{
                color: {accent};
                background-color: rgba(0, 255, 170, 18);
                border: 1px solid rgba(0, 255, 170, 85);
                border-radius: 12px;
                padding: 8px 12px;
                font-weight: 700;
            }}

            #headerButton {{
                background-color: rgba(7, 30, 50, 230);
                border: 1px solid {accent};
                border-radius: 11px;
                padding: 9px 14px;
                color: {accent};
                font-weight: 700;
            }}

            #headerButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QLineEdit {{
                background-color: rgba(2, 11, 21, 245);
                color: white;
                border: 1px solid rgba(127, 231, 255, 100);
                border-radius: 13px;
                padding: 12px 15px;
                selection-background-color: {accent};
                selection-color: {background};
            }}

            QLineEdit:focus {{
                border: 2px solid {accent};
            }}

            #dashboardHero {{
                background-color: rgba(5, 28, 48, 240);
                border: 1px solid rgba(127, 231, 255, 110);
                border-radius: 20px;
            }}

            #heroTitle {{
                color: {accent};
                font-size: 27px;
                font-weight: 800;
            }}

            #heroSubtitle {{
                color: rgba(225, 245, 255, 185);
                font-size: 14px;
            }}

            #dashboardCard {{
                background-color: rgba(3, 17, 31, 245);
                border: 1px solid rgba(127, 231, 255, 80);
                border-radius: 17px;
                min-height: 95px;
                padding: 15px;
                font-weight: 700;
            }}

            #tipCard {{
                background-color: rgba(12, 44, 68, 230);
                border: 1px solid rgba(127, 231, 255, 90);
                border-radius: 16px;
            }}

            #tipTitle {{
                color: {accent};
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            #tipText {{
                color: white;
                font-size: 13px;
            }}

            #pageTitle {{
                color: {accent};
                font-size: 25px;
                font-weight: 800;
            }}

            #pageDescription {{
                color: rgba(220, 245, 255, 170);
            }}

            #sectionTitle {{
                color: {accent};
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            #fieldLabel {{
                color: {accent};
                font-weight: 700;
                margin-top: 8px;
            }}

            QTabWidget::pane {{
                background-color: rgba(4, 17, 31, 245);
                border: 1px solid rgba(127, 231, 255, 85);
                border-radius: 18px;
                padding: 5px;
            }}

            QTabBar {{
                background-color: transparent;
            }}

            QTabBar::tab {{
                background-color: rgba(5, 21, 36, 230);
                color: rgba(220, 245, 255, 185);
                border: 1px solid rgba(127, 231, 255, 45);
                border-radius: 11px;
                min-width: 145px;
                min-height: {tab_height}px;
                margin: 4px;
                padding: 8px 14px;
                font-weight: 700;
            }}

            QTabBar::tab:hover {{
                background-color: rgba(19, 67, 94, 230);
                color: white;
                border: 1px solid {accent};
            }}

            QTabBar::tab:selected {{
                background-color: {accent};
                color: {background};
                border: 1px solid {accent};
            }}

            QPushButton {{
                background-color: rgba(6, 25, 42, 235);
                color: {accent};
                border: 1px solid rgba(127, 231, 255, 105);
                border-radius: 11px;
                padding: {padding}px 15px;
                font-weight: 700;
            }}

            QPushButton:hover {{
                background-color: {accent};
                color: {background};
                border-color: {accent};
            }}

            QPushButton:pressed {{
                background-color: rgba(80, 190, 220, 235);
                color: {background};
            }}

            QCheckBox {{
                color: white;
                spacing: 10px;
                padding: {padding}px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 1px solid {accent};
                background-color: rgba(2, 12, 23, 245);
            }}

            QCheckBox::indicator:hover {{
                background-color: rgba(20, 70, 98, 230);
            }}

            QCheckBox::indicator:checked {{
                background-color: {accent};
                border: 1px solid {accent};
            }}

            QComboBox,
            QDoubleSpinBox,
            QTextEdit {{
                background-color: rgba(2, 12, 23, 245);
                color: white;
                border: 1px solid rgba(127, 231, 255, 95);
                border-radius: 11px;
                padding: 9px 11px;
            }}

            QComboBox:focus,
            QDoubleSpinBox:focus,
            QTextEdit:focus {{
                border: 2px solid {accent};
            }}

            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background: rgba(2, 12, 23, 110);
                width: 10px;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical {{
                background: {accent};
                border-radius: 5px;
                min-height: 35px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QMessageBox {{
                background-color: {background};
                color: white;
            }}

            QMessageBox QLabel {{
                color: white;
            }}
            """
        )

        if (
    getattr(
        self,
        "dashboard_tip",
        None
    ) is not None
        ):

            self.dashboard_tip.setVisible(
                bool(
                    self.ui_preferences.get(
                        "show_tips",
                        True
                    )
                )
            )

        if (
            getattr(
                self,
                "dashboard_status",
                None
            ) is not None
        ):

            self.dashboard_status.setVisible(
                bool(
                    self.ui_preferences.get(
                        "show_system_status",
                        True
                    )
                )
            )

    # =========================================================
    # THEME EVENTS
    # =========================================================

    def on_theme_changed(
        self,
        theme
    ):
        self.theme = theme.copy()

        self.apply_v2_style(
            self.theme
        )

        if hasattr(
            self,
            "refresh_dashboard"
        ):

            self.refresh_dashboard()