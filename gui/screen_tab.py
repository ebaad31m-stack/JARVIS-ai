from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.screen_settings import (
    get_monitors,
    load_screen_settings,
    save_screen_settings,
)


class ScreenTab(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.monitors = []

        self.build_ui()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(
        self
    ):
        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "Screen Vision"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Choose which monitor JARVIS uses for "
            "AI screen vision, OCR, screen reading, "
            "error detection, and GUI highlighting."
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

        # =====================================================
        # MONITOR PICKER
        # =====================================================

        monitor_row = QHBoxLayout()

        monitor_label = QLabel(
            "Screen to Analyze"
        )

        monitor_label.setStyleSheet(
            "font-weight: bold;"
        )

        monitor_row.addWidget(
            monitor_label
        )

        monitor_row.addStretch()

        self.monitor_combo = (
            QComboBox()
        )

        self.monitor_combo.setMinimumWidth(
            420
        )

        monitor_row.addWidget(
            self.monitor_combo
        )

        layout.addLayout(
            monitor_row
        )

        layout.addSpacing(
            15
        )

        # =====================================================
        # INFORMATION
        # =====================================================

        self.monitor_info = QLabel()

        self.monitor_info.setWordWrap(
            True
        )

        layout.addWidget(
            self.monitor_info
        )

        layout.addSpacing(
            10
        )

        hint = QLabel(
            "This selection affects commands such as:\n\n"
            '• "Jarvis, look at my screen"\n'
            '• "Jarvis, read my screen"\n'
            '• "Jarvis, explain this error"\n'
            '• "Jarvis, what should I click?"\n'
            '• Screen highlights and OCR'
        )

        hint.setWordWrap(
            True
        )

        layout.addWidget(
            hint
        )

        layout.addStretch()

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        refresh_button = QPushButton(
            "Refresh Monitors"
        )

        refresh_button.clicked.connect(
            self.load_monitors
        )

        save_button = QPushButton(
            "Save Screen Settings"
        )

        save_button.clicked.connect(
            self.save_settings
        )

        buttons.addWidget(
            refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

        self.monitor_combo.currentIndexChanged.connect(
            self.update_monitor_info
        )

        self.load_monitors()

    # =========================================================
    # LOAD MONITORS
    # =========================================================

    def load_monitors(
        self
    ):
        settings = (
            load_screen_settings()
        )

        selected = str(
            settings.get(
                "monitor",
                "all",
            )
        )

        self.monitors = (
            get_monitors()
        )

        self.monitor_combo.blockSignals(
            True
        )

        self.monitor_combo.clear()

        # =====================================================
        # ALL
        # =====================================================

        self.monitor_combo.addItem(
            (
                "All Monitors "
                f"({len(self.monitors)} detected)"
            ),
            "all",
        )

        # =====================================================
        # INDIVIDUAL
        # =====================================================

        for index, monitor in enumerate(
            self.monitors,
            start=1,
        ):
            name = (
                monitor.get(
                    "name"
                )
                or monitor.get(
                    "device"
                )
                or f"Monitor {index}"
            )

            resolution = (
                f'{monitor["width"]}'
                "x"
                f'{monitor["height"]}'
            )

            primary_text = ""

            if monitor.get(
                "primary",
                False,
            ):
                primary_text = (
                    " — Primary"
                )

            label = (
                f"{name} — "
                f"{resolution}"
                f"{primary_text}"
            )

            self.monitor_combo.addItem(
                label,
                monitor.get(
                    "id"
                ),
            )

        # =====================================================
        # RESTORE SAVED SELECTION
        # =====================================================

        selected_index = (
            self.monitor_combo.findData(
                selected
            )
        )

        # Old setting compatibility:
        # "1", "2", "3"
        if (
            selected_index < 0
            and selected != "all"
        ):
            try:
                old_index = int(
                    selected
                )

                if (
                    1 <= old_index
                    <= len(
                        self.monitors
                    )
                ):
                    selected_index = (
                        old_index
                    )

            except Exception:
                pass

        if selected_index < 0:
            selected_index = 0

        self.monitor_combo.setCurrentIndex(
            selected_index
        )

        self.monitor_combo.blockSignals(
            False
        )

        self.update_monitor_info()

    # =========================================================
    # MONITOR INFO
    # =========================================================

    def update_monitor_info(
        self
    ):
        selection = (
            self.monitor_combo
            .currentData()
        )

        if selection == "all":
            self.monitor_info.setText(
                "JARVIS will capture and analyze "
                f"all {len(self.monitors)} monitors "
                "as one combined desktop."
            )

            return

        selected_monitor = None

        for monitor in self.monitors:
            if monitor.get(
                "id"
            ) == selection:
                selected_monitor = (
                    monitor
                )

                break

        if selected_monitor is None:
            self.monitor_info.setText(
                "Monitor information unavailable."
            )

            return

        name = (
            selected_monitor.get(
                "name",
                "Unknown Monitor",
            )
        )

        device = (
            selected_monitor.get(
                "device",
                "",
            )
        )

        resolution = (
            f'{selected_monitor["width"]}'
            "x"
            f'{selected_monitor["height"]}'
        )

        position = (
            f'({selected_monitor["x"]}, '
            f'{selected_monitor["y"]})'
        )

        primary = (
            "Yes"
            if selected_monitor.get(
                "primary",
                False,
            )
            else "No"
        )

        self.monitor_info.setText(
            f"Monitor: {name}\n"
            f"Windows device: {device}\n"
            f"Resolution: {resolution}\n"
            f"Desktop position: {position}\n"
            f"Primary display: {primary}"
        )

    # =========================================================
    # SAVE
    # =========================================================

    def save_settings(
        self
    ):
        selection = (
            self.monitor_combo
            .currentData()
        )

        if not selection:
            selection = "all"

        try:
            save_screen_settings(
                {
                    "monitor":
                        selection,
                }
            )

            QMessageBox.information(
                self,
                "JARVIS",
                "Screen monitor selection saved.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "JARVIS",
                "Could not save screen settings.\n\n"
                f"{error}",
            )