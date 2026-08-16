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
    QWidget,
)

from core.app_launcher import (
    load_apps,
)

from core.command_manager import (
    delete_command,
    load_commands,
    run_command,
    set_command,
)

from core.macro_manager import (
    list_macros,
)


ACTION_TYPES = {
    "Open App":
        "open_app",

    "Close App":
        "close_app",

    "Open Website":
        "open_url",

    "Wait":
        "wait",

    "Run Macro":
        "run_macro",

    "Speak Text":
        "speak_text",

    "Type Text":
        "type_text",

    "Press Key / Hotkey":
        "hotkey",

    "Run Screen Vision":
        "vision",
}


class CommandActionRow(QWidget):

    def __init__(
        self,
        parent_tab,
        action=None,
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
            4,
        )

        # =====================================================
        # ACTION TYPE
        # =====================================================

        self.action_combo = QComboBox()

        for (
            label,
            value,
        ) in ACTION_TYPES.items():

            self.action_combo.addItem(
                label,
                value,
            )

        self.layout.addWidget(
            self.action_combo,
            1,
        )

        # =====================================================
        # APP
        # =====================================================

        self.app_combo = QComboBox()

        self.app_combo.setEditable(
            True
        )

        self.layout.addWidget(
            self.app_combo,
            2,
        )

        # =====================================================
        # MACRO
        # =====================================================

        self.macro_combo = QComboBox()

        self.macro_combo.setEditable(
            True
        )

        self.layout.addWidget(
            self.macro_combo,
            2,
        )

        # =====================================================
        # TEXT
        # =====================================================

        self.text_input = QLineEdit()

        self.layout.addWidget(
            self.text_input,
            3,
        )

        # =====================================================
        # WAIT
        # =====================================================

        self.wait_input = QDoubleSpinBox()

        self.wait_input.setRange(
            0.0,
            60.0,
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
            1,
        )

        # =====================================================
        # DELETE
        # =====================================================

        self.delete_button = QPushButton(
            "✕"
        )

        self.delete_button.setFixedWidth(
            42
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
        self.load_macros()

        if action:
            self.load_action(
                action
            )

        self.update_controls()

    # =========================================================
    # APPS
    # =========================================================

    def load_apps(
        self
    ):
        current = (
            self.app_combo
            .currentText()
            .strip()
        )

        self.app_combo.clear()

        try:
            apps = load_apps()

            for name in sorted(
                apps.keys()
            ):
                self.app_combo.addItem(
                    name
                )

        except Exception as error:
            print(
                "Command editor app load error:",
                error,
            )

        if current:
            self.app_combo.setCurrentText(
                current
            )

    # =========================================================
    # MACROS
    # =========================================================

    def load_macros(
        self
    ):
        current = (
            self.macro_combo
            .currentText()
            .strip()
        )

        self.macro_combo.clear()

        for name in list_macros():
            self.macro_combo.addItem(
                name
            )

        if current:
            self.macro_combo.setCurrentText(
                current
            )

    # =========================================================
    # LOAD ACTION
    # =========================================================

    def load_action(
        self,
        action,
    ):
        action_type = action.get(
            "action",
            "open_app",
        )

        index = (
            self.action_combo.findData(
                action_type
            )
        )

        if index >= 0:
            self.action_combo.setCurrentIndex(
                index
            )

        if action_type in (
            "open_app",
            "close_app",
        ):
            self.app_combo.setCurrentText(
                str(
                    action.get(
                        "target",
                        "",
                    )
                )
            )

        elif action_type == "run_macro":
            self.macro_combo.setCurrentText(
                str(
                    action.get(
                        "target",
                        "",
                    )
                )
            )

        elif action_type == "wait":
            try:
                self.wait_input.setValue(
                    float(
                        action.get(
                            "seconds",
                            1,
                        )
                    )
                )

            except Exception:
                self.wait_input.setValue(
                    1.0
                )

        else:
            self.text_input.setText(
                str(
                    action.get(
                        "target",
                        "",
                    )
                )
            )

    # =========================================================
    # UI
    # =========================================================

    def update_controls(
        self
    ):
        action_type = (
            self.action_combo
            .currentData()
        )

        self.app_combo.setVisible(
            action_type
            in (
                "open_app",
                "close_app",
            )
        )

        self.macro_combo.setVisible(
            action_type
            == "run_macro"
        )

        self.wait_input.setVisible(
            action_type
            == "wait"
        )

        text_actions = (
            "open_url",
            "speak_text",
            "type_text",
            "hotkey",
            "vision",
        )

        self.text_input.setVisible(
            action_type
            in text_actions
        )

        placeholders = {
            "open_url":
                "https://example.com",

            "speak_text":
                "What JARVIS should say",

            "type_text":
                "Text to type",

            "hotkey":
                "ctrl+shift+esc",

            "vision":
                "What should JARVIS inspect?",
        }

        self.text_input.setPlaceholderText(
            placeholders.get(
                action_type,
                "",
            )
        )

    # =========================================================
    # SERIALIZE
    # =========================================================

    def get_action(
        self
    ):
        action_type = (
            self.action_combo
            .currentData()
        )

        if action_type in (
            "open_app",
            "close_app",
        ):
            target = (
                self.app_combo
                .currentText()
                .lower()
                .strip()
            )

            if not target:
                return None

            return {
                "action":
                    action_type,

                "target":
                    target,
            }

        if action_type == "run_macro":
            target = (
                self.macro_combo
                .currentText()
                .lower()
                .strip()
            )

            if not target:
                return None

            return {
                "action":
                    "run_macro",

                "target":
                    target,
            }

        if action_type == "wait":
            return {
                "action":
                    "wait",

                "seconds":
                    self.wait_input.value(),
            }

        target = (
            self.text_input
            .text()
            .strip()
        )

        if not target:
            return None

        return {
            "action":
                action_type,

            "target":
                target,
        }

    # =========================================================
    # REMOVE
    # =========================================================

    def remove_self(
        self
    ):
        self.parent_tab.remove_action_row(
            self
        )


class CommandsTab(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.action_rows = []

        self.build_ui()

        self.reload_commands()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(
        self
    ):
        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        title = QLabel(
            "Custom Commands"
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Create your own JARVIS voice commands "
            "without editing Python."
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
        # SELECTOR
        # =====================================================

        selector_row = QHBoxLayout()

        selector_row.addWidget(
            QLabel(
                "Command"
            )
        )

        self.command_combo = QComboBox()

        self.command_combo.currentIndexChanged.connect(
            self.load_selected_command
        )

        selector_row.addWidget(
            self.command_combo,
            2,
        )

        new_button = QPushButton(
            "+ New Command"
        )

        new_button.clicked.connect(
            self.new_command
        )

        selector_row.addWidget(
            new_button
        )

        layout.addLayout(
            selector_row
        )

        layout.addSpacing(
            12
        )

        # =====================================================
        # TRIGGER
        # =====================================================

        name_row = QHBoxLayout()

        name_row.addWidget(
            QLabel(
                "Voice trigger"
            )
        )

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "school mode"
        )

        name_row.addWidget(
            self.name_input,
            2,
        )

        layout.addLayout(
            name_row
        )

        example = QLabel(
            'Example: say "Jarvis, school mode".'
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
        # ACTION HEADER
        # =====================================================

        action_header = QHBoxLayout()

        label = QLabel(
            "Actions"
        )

        label.setStyleSheet(
            "font-weight: bold;"
        )

        action_header.addWidget(
            label
        )

        action_header.addStretch()

        add_button = QPushButton(
            "+ Add Action"
        )

        add_button.clicked.connect(
            self.add_action_row
        )

        action_header.addWidget(
            add_button
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
        # BUTTON BAR
        # =====================================================

        buttons = QHBoxLayout()

        delete_button = QPushButton(
            "Delete Command"
        )

        delete_button.clicked.connect(
            self.delete_selected_command
        )

        buttons.addWidget(
            delete_button
        )

        test_button = QPushButton(
            "▶ Test Command"
        )

        test_button.clicked.connect(
            self.test_current_command
        )

        buttons.addWidget(
            test_button
        )

        buttons.addStretch()

        save_button = QPushButton(
            "Save Command"
        )

        save_button.clicked.connect(
            self.save_current_command
        )

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

    # =========================================================
    # RELOAD
    # =========================================================

    def reload_commands(
        self,
        select_name=None,
    ):
        commands = load_commands()

        self.command_combo.blockSignals(
            True
        )

        self.command_combo.clear()

        for name in sorted(
            commands.keys()
        ):
            self.command_combo.addItem(
                name
            )

        self.command_combo.blockSignals(
            False
        )

        if select_name:
            index = (
                self.command_combo.findText(
                    select_name
                )
            )

            if index >= 0:
                self.command_combo.setCurrentIndex(
                    index
                )

        if self.command_combo.count() > 0:
            self.load_selected_command()

        else:
            self.new_command()

    # =========================================================
    # ACTION ROWS
    # =========================================================

    def clear_actions(
        self
    ):
        for row in list(
            self.action_rows
        ):
            self.actions_layout.removeWidget(
                row
            )

            row.deleteLater()

        self.action_rows.clear()

    def add_action_row(
        self,
        checked=False,
        action=None,
    ):
        row = CommandActionRow(
            self,
            action,
        )

        self.action_rows.append(
            row
        )

        self.actions_layout.addWidget(
            row
        )

    def remove_action_row(
        self,
        row,
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

    def load_selected_command(
        self
    ):
        name = (
            self.command_combo
            .currentText()
            .strip()
        )

        if not name:
            return

        commands = load_commands()

        actions = commands.get(
            name,
            [],
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

    def new_command(
        self
    ):
        self.command_combo.setCurrentIndex(
            -1
        )

        self.name_input.clear()

        self.clear_actions()

        self.add_action_row()

        self.name_input.setFocus()

    # =========================================================
    # BUILD ACTIONS
    # =========================================================

    def build_actions(
        self
    ):
        actions = []

        for row in self.action_rows:
            action = row.get_action()

            if action is None:
                return None

            actions.append(
                action
            )

        return actions

    # =========================================================
    # SAVE
    # =========================================================

    def save_current_command(
        self
    ):
        name = (
            self.name_input
            .text()
            .lower()
            .strip()
        )

        if not name:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Enter a voice trigger.",
            )

            return

        actions = self.build_actions()

        if actions is None:
            QMessageBox.warning(
                self,
                "JARVIS",
                "One or more actions "
                "is missing information.",
            )

            return

        if not actions:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Add at least one action.",
            )

            return

        if not set_command(
            name,
            actions,
        ):
            QMessageBox.critical(
                self,
                "JARVIS",
                "Could not save the command.",
            )

            return

        self.reload_commands(
            select_name=name
        )

        QMessageBox.information(
            self,
            "JARVIS",
            f'Command "{name}" saved.',
        )

    # =========================================================
    # TEST
    # =========================================================

    def test_current_command(
        self
    ):
        name = (
            self.name_input
            .text()
            .lower()
            .strip()
        )

        actions = self.build_actions()

        if (
            not name
            or actions is None
            or not actions
        ):
            QMessageBox.warning(
                self,
                "JARVIS",
                "Finish the command before testing it.",
            )

            return

        set_command(
            name,
            actions,
        )

        response = run_command(
            name
        )

        QMessageBox.information(
            self,
            "Command Test",
            response
            or "Command finished.",
        )

    # =========================================================
    # DELETE
    # =========================================================

    def delete_selected_command(
        self
    ):
        name = (
            self.command_combo
            .currentText()
            .strip()
        )

        if not name:
            return

        answer = QMessageBox.question(
            self,
            "Delete Command",
            f'Delete "{name}"?',
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        if delete_command(
            name
        ):
            self.reload_commands()

            QMessageBox.information(
                self,
                "JARVIS",
                f'Command "{name}" deleted.',
            )

        else:
            QMessageBox.warning(
                self,
                "JARVIS",
                "Could not delete that command.",
            )