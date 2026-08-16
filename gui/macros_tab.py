from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget
)

from core.app_launcher import load_apps

from core.macro_manager import (
    delete_macro,
    load_macros,
    set_macro
)


ACTION_TYPES = {
    "Open App": "open_app",
    "Close App": "close_app",
    "Wait": "wait",
    "Open Website": "open_url"
}


class MacroActionRow(QWidget):

    def __init__(
        self,
        parent_tab,
        action=None
    ):
        super().__init__()

        self.parent_tab = parent_tab

        self.layout = QHBoxLayout(
            self
        )

        self.layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        # =====================================================
        # ACTION TYPE
        # =====================================================

        self.action_combo = QComboBox()

        for label, value in ACTION_TYPES.items():
            self.action_combo.addItem(
                label,
                value
            )

        self.layout.addWidget(
            self.action_combo,
            1
        )

        # =====================================================
        # APP TARGET
        # =====================================================

        self.app_combo = QComboBox()

        self.app_combo.setEditable(
            True
        )

        self.layout.addWidget(
            self.app_combo,
            2
        )

        # =====================================================
        # TEXT TARGET
        # =====================================================

        self.text_input = QLineEdit()

        self.text_input.setPlaceholderText(
            "Website URL"
        )

        self.layout.addWidget(
            self.text_input,
            2
        )

        # =====================================================
        # WAIT
        # =====================================================

        self.wait_input = QDoubleSpinBox()

        self.wait_input.setRange(
            0.0,
            60.0
        )

        self.wait_input.setDecimals(
            1
        )

        self.wait_input.setSingleStep(
            0.5
        )

        self.wait_input.setValue(
            1.0
        )

        self.wait_input.setSuffix(
            " sec"
        )

        self.layout.addWidget(
            self.wait_input,
            1
        )

        # =====================================================
        # DELETE ACTION
        # =====================================================

        self.delete_button = QPushButton(
            "✕"
        )

        self.delete_button.setFixedWidth(
            42
        )

        self.delete_button.setToolTip(
            "Remove action"
        )

        self.delete_button.clicked.connect(
            self.remove_self
        )

        self.layout.addWidget(
            self.delete_button
        )

        # =====================================================
        # EVENTS
        # =====================================================

        self.action_combo.currentIndexChanged.connect(
            self.update_controls
        )

        self.load_apps()

        if action:
            self.load_action(
                action
            )

        self.update_controls()


    # =========================================================
    # APPS
    # =========================================================

    def load_apps(self):
        current = (
            self.app_combo.currentText()
            .strip()
        )

        self.app_combo.clear()

        apps = load_apps()

        for name in sorted(
            apps.keys()
        ):
            self.app_combo.addItem(
                name
            )

        if current:
            self.app_combo.setCurrentText(
                current
            )


    # =========================================================
    # LOAD ACTION
    # =========================================================

    def load_action(
        self,
        action
    ):
        action_type = action.get(
            "action",
            "open_app"
        )

        index = self.action_combo.findData(
            action_type
        )

        if index >= 0:
            self.action_combo.setCurrentIndex(
                index
            )

        if action_type in (
            "open_app",
            "close_app"
        ):
            self.app_combo.setCurrentText(
                str(
                    action.get(
                        "target",
                        ""
                    )
                )
            )

        elif action_type == "open_url":
            self.text_input.setText(
                str(
                    action.get(
                        "target",
                        ""
                    )
                )
            )

        elif action_type == "wait":
            try:
                self.wait_input.setValue(
                    float(
                        action.get(
                            "seconds",
                            1
                        )
                    )
                )

            except Exception:
                self.wait_input.setValue(
                    1.0
                )


    # =========================================================
    # UI
    # =========================================================

    def update_controls(self):
        action_type = (
            self.action_combo.currentData()
        )

        app_action = action_type in (
            "open_app",
            "close_app"
        )

        self.app_combo.setVisible(
            app_action
        )

        self.text_input.setVisible(
            action_type == "open_url"
        )

        self.wait_input.setVisible(
            action_type == "wait"
        )


    # =========================================================
    # SERIALIZE
    # =========================================================

    def get_action(self):
        action_type = (
            self.action_combo.currentData()
        )

        if action_type in (
            "open_app",
            "close_app"
        ):
            target = (
                self.app_combo.currentText()
                .lower()
                .strip()
            )

            if not target:
                return None

            return {
                "action": action_type,
                "target": target
            }

        if action_type == "open_url":
            target = (
                self.text_input.text()
                .strip()
            )

            if not target:
                return None

            return {
                "action": "open_url",
                "target": target
            }

        if action_type == "wait":
            return {
                "action": "wait",
                "seconds": self.wait_input.value()
            }

        return None


    # =========================================================
    # REMOVE
    # =========================================================

    def remove_self(self):
        self.parent_tab.remove_action_row(
            self
        )


class MacrosTab(QWidget):

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.action_rows = []

        self.build_ui()

        self.reload_macros()


    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):
        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        # =====================================================
        # HEADER
        # =====================================================

        title = QLabel(
            "Macros"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Create voice-triggered sequences such as "
            "\"gaming mode\", \"study mode\", or "
            "\"coding mode\"."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            15
        )

        # =====================================================
        # MACRO SELECTOR
        # =====================================================

        macro_row = QHBoxLayout()

        macro_row.addWidget(
            QLabel(
                "Macro"
            )
        )

        self.macro_combo = QComboBox()

        self.macro_combo.setEditable(
            False
        )

        self.macro_combo.currentIndexChanged.connect(
            self.load_selected_macro
        )

        macro_row.addWidget(
            self.macro_combo,
            2
        )

        self.new_button = QPushButton(
            "+ New Macro"
        )

        self.new_button.clicked.connect(
            self.new_macro
        )

        macro_row.addWidget(
            self.new_button
        )

        layout.addLayout(
            macro_row
        )

        layout.addSpacing(
            12
        )

        # =====================================================
        # MACRO NAME
        # =====================================================

        name_row = QHBoxLayout()

        name_row.addWidget(
            QLabel(
                "Voice command"
            )
        )

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "gaming mode"
        )

        name_row.addWidget(
            self.name_input,
            2
        )

        layout.addLayout(
            name_row
        )

        example = QLabel(
            "Example: say \"Jarvis, gaming mode\" "
            "to run the macro."
        )

        example.setWordWrap(
            True
        )

        layout.addWidget(
            example
        )

        layout.addSpacing(
            12
        )

        # =====================================================
        # ACTIONS HEADER
        # =====================================================

        action_header = QHBoxLayout()

        actions_label = QLabel(
            "Actions"
        )

        actions_label.setStyleSheet(
            "font-weight: bold;"
        )

        action_header.addWidget(
            actions_label
        )

        action_header.addStretch()

        add_action_button = QPushButton(
            "+ Add Action"
        )

        add_action_button.clicked.connect(
            self.add_action_row
        )

        action_header.addWidget(
            add_action_button
        )

        layout.addLayout(
            action_header
        )

        # =====================================================
        # ACTION SCROLL
        # =====================================================

        self.actions_scroll = QScrollArea()

        self.actions_scroll.setWidgetResizable(
            True
        )

        self.actions_container = QWidget()

        self.actions_layout = QVBoxLayout(
            self.actions_container
        )

        self.actions_layout.setAlignment(
            Qt.AlignTop
        )

        self.actions_scroll.setWidget(
            self.actions_container
        )

        layout.addWidget(
            self.actions_scroll
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        self.delete_button = QPushButton(
            "Delete Macro"
        )

        self.delete_button.clicked.connect(
            self.delete_selected_macro
        )

        buttons.addWidget(
            self.delete_button
        )

        buttons.addStretch()

        self.save_button = QPushButton(
            "Save Macro"
        )

        self.save_button.clicked.connect(
            self.save_current_macro
        )

        buttons.addWidget(
            self.save_button
        )

        layout.addLayout(
            buttons
        )


    # =========================================================
    # RELOAD MACROS
    # =========================================================

    def reload_macros(
        self,
        select_name=None
    ):
        macros = load_macros()

        self.macro_combo.blockSignals(
            True
        )

        self.macro_combo.clear()

        for name in sorted(
            macros.keys()
        ):
            self.macro_combo.addItem(
                name
            )

        self.macro_combo.blockSignals(
            False
        )

        if select_name:
            index = self.macro_combo.findText(
                select_name
            )

            if index >= 0:
                self.macro_combo.setCurrentIndex(
                    index
                )

        if self.macro_combo.count() > 0:
            self.load_selected_macro()

        else:
            self.new_macro()


    # =========================================================
    # CLEAR ACTIONS
    # =========================================================

    def clear_actions(self):
        for row in list(
            self.action_rows
        ):
            self.actions_layout.removeWidget(
                row
            )

            row.deleteLater()

        self.action_rows.clear()


    # =========================================================
    # ADD ACTION
    # =========================================================

    def add_action_row(
        self,
        checked=False,
        action=None
    ):
        row = MacroActionRow(
            self,
            action
        )

        self.action_rows.append(
            row
        )

        self.actions_layout.addWidget(
            row
        )


    def remove_action_row(
        self,
        row
    ):
        if row in self.action_rows:
            self.action_rows.remove(
                row
            )

        self.actions_layout.removeWidget(
            row
        )

        row.deleteLater()


    # =========================================================
    # LOAD SELECTED
    # =========================================================

    def load_selected_macro(self):
        name = (
            self.macro_combo.currentText()
            .strip()
        )

        if not name:
            return

        macros = load_macros()

        actions = macros.get(
            name,
            []
        )

        self.name_input.setText(
            name
        )

        self.clear_actions()

        for action in actions:
            self.add_action_row(
                action=action
            )

        if not actions:
            self.add_action_row()


    # =========================================================
    # NEW
    # =========================================================

    def new_macro(self):
        self.macro_combo.setCurrentIndex(
            -1
        )

        self.name_input.clear()

        self.clear_actions()

        self.add_action_row()

        self.name_input.setFocus()


    # =========================================================
    # SAVE
    # =========================================================

    def save_current_macro(self):
        name = (
            self.name_input.text()
            .lower()
            .strip()
        )

        if not name:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter a macro name."
            )

            return

        actions = []

        for row in self.action_rows:
            action = row.get_action()

            if action is None:
                QMessageBox.warning(
                    self,
                    "JARVIS",
                    "One or more macro actions "
                    "is missing information."
                )

                return

            actions.append(
                action
            )

        if not actions:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Add at least one action."
            )

            return

        if not set_macro(
            name,
            actions
        ):
            QMessageBox.critical(
                self,
                "JARVIS",
                "Could not save the macro."
            )

            return

        self.reload_macros(
            select_name=name
        )

        QMessageBox.information(
            self,
            "JARVIS",
            f'Macro "{name}" saved.'
        )


    # =========================================================
    # DELETE
    # =========================================================

    def delete_selected_macro(self):
        name = (
            self.macro_combo.currentText()
            .strip()
        )

        if not name:
            return

        answer = QMessageBox.question(
            self,
            "Delete Macro",
            f'Delete "{name}"?',
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        if delete_macro(
            name
        ):
            self.reload_macros()

            QMessageBox.information(
                self,
                "JARVIS",
                f'Macro "{name}" deleted.'
            )

        else:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Could not delete that macro."
            )