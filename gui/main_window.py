import json
import os
import subprocess
import sys
import threading
import time

from PySide6.QtCore import (
    QObject,
    Qt,
    QTimer,
    Signal,
)

from PySide6.QtGui import (
    QAction,
    QFont,
)

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from core.action_manager import (
    get_action_state,
)

from core.paths import (
    user_file,
)

from core.ai_mode import (
    get_ai_mode_label,
)

from core.conversation_manager import (
    get_history_count,
    get_recent_turns,
)

from core.coding_progress import (
    read_coding_progress,
)

from core.personalization import (
    get_assistant_name,
)

from core.overlay_manager import (
    overlay_signals,
)

from core.ui_state import (
    get_state,
    set_state,
    submit_text_input,
    ui_state,
)

from core.voice_output import (
    speak,
)

from remote.remote_manager import (
    execute_remote_command,
)

from gui.help_page_v2 import HelpPage
from gui.jarvis_orb import JarvisOrb
from gui.overlay_window import OverlayWindow
from gui.settings_page_v2 import SettingsPage

from gui.theme_manager import (
    load_theme,
    theme_bus,
)


UI_PREFERENCES_FILE = user_file(
    "ui_preferences.json"
)


class CommandSignals(QObject):

    finished = Signal(
        str,
        str,
    )

    failed = Signal(
        str,
        str,
    )


class JarvisWindow(QMainWindow):

    def __init__(
        self
    ):
        super().__init__()

        self.assistant_name = get_assistant_name()

        self.setWindowTitle(
            self.assistant_name
        )

        self.resize(
            1180,
            980,
        )

        self.setMinimumSize(
            980,
            900,
        )

        self.allow_full_exit = False
        self.tray_message_shown = False

        self.settings_window = None
        self.help_window = None
        self.overlay_window = None

        self.show_conversation_center = self.load_ui_preference(
            "show_conversation_center",
            True
        )

        self.theme = load_theme()

        self.command_signals = (
            CommandSignals()
        )

        self.command_signals.finished.connect(
            self.command_finished
        )

        self.command_signals.failed.connect(
            self.command_failed
        )

        self.last_history_count = -1
        self.last_coding_status_timestamp = 0.0

        self.last_state = ""

        self.initializing_chat = True

        app = QApplication.instance()

        if app is not None:
            app.setQuitOnLastWindowClosed(
                False
            )

        # =====================================================
        # BUILD UI
        # =====================================================

        self.build_ui()

        # =====================================================
        # OVERLAY
        # =====================================================

        self.setup_overlay()

        # =====================================================
        # THEME
        # =====================================================

        self.apply_theme(
            self.theme
        )

        # =====================================================
        # TRAY
        # =====================================================

        self.setup_system_tray()

        # =====================================================
        # STATE TIMER
        # =====================================================

        self.state_timer = QTimer(
            self
        )

        self.state_timer.timeout.connect(
            self.update_jarvis_state
        )

        self.state_timer.start(
            100
        )

        # =====================================================
        # CONVERSATION TIMER
        # =====================================================

        self.refresh_timer = QTimer(
            self
        )

        self.refresh_timer.timeout.connect(
            self.refresh_dynamic_ui
        )

        self.refresh_timer.start(
            700
        )

        # =====================================================
        # SIGNALS
        # =====================================================

        ui_state.shutdown_requested.connect(
            self.shutdown_gui
        )

        ui_state.text_input_requested.connect(
            self.request_text_input
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )

        # =====================================================
        # INITIAL DATA
        # =====================================================

        self.load_conversation_history()

        self.refresh_suggestions()

        self.initializing_chat = False

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(
        self
    ):
        central_widget = QWidget()

        central_widget.setObjectName(
            "centralWidget"
        )

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        main_layout.setSpacing(
            16
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()

        header.setSpacing(
            12
        )

        # BRAND

        brand_column = QVBoxLayout()

        brand_column.setSpacing(
            2
        )

        self.brand_label = QLabel(
            self.assistant_name
        )

        brand_font = QFont(
            "Segoe UI"
        )

        brand_font.setPointSize(
            30
        )

        brand_font.setBold(
            True
        )

        self.brand_label.setFont(
            brand_font
        )

        brand_column.addWidget(
            self.brand_label
        )

        status_row = QHBoxLayout()

        status_row.setSpacing(
            7
        )

        self.online_dot = QLabel(
            "●"
        )

        online_dot_font = QFont(
            "Segoe UI"
        )

        online_dot_font.setPointSize(
            13
        )

        self.online_dot.setFont(
            online_dot_font
        )

        status_row.addWidget(
            self.online_dot
        )

        self.online_label = QLabel(
            "ONLINE"
        )

        online_font = QFont(
            "Segoe UI"
        )

        online_font.setPointSize(
            12
        )

        online_font.setBold(
            True
        )

        self.online_label.setFont(
            online_font
        )

        status_row.addWidget(
            self.online_label
        )

        status_row.addStretch()

        brand_column.addLayout(
            status_row
        )

        self.subtitle_label = QLabel(
            "Ready to assist."
        )

        subtitle_font = QFont(
            "Segoe UI"
        )

        subtitle_font.setPointSize(
            12
        )

        self.subtitle_label.setFont(
            subtitle_font
        )

        brand_column.addWidget(
            self.subtitle_label
        )

        header.addLayout(
            brand_column
        )

        header.addStretch()

        # MODE

        mode_column = QVBoxLayout()

        mode_column.setSpacing(
            4
        )

        self.mode_caption = QLabel(
            "AI MODE"
        )

        self.mode_caption.setAlignment(
            Qt.AlignRight
        )

        mode_caption_font = QFont(
            "Segoe UI"
        )

        mode_caption_font.setPointSize(
            9
        )

        mode_caption_font.setBold(
            True
        )

        self.mode_caption.setFont(
            mode_caption_font
        )

        mode_column.addWidget(
            self.mode_caption
        )

        self.mode_label = QLabel(
            get_ai_mode_label()
        )

        self.mode_label.setAlignment(
            Qt.AlignRight
        )

        mode_font = QFont(
            "Segoe UI"
        )

        mode_font.setPointSize(
            11
        )

        mode_font.setBold(
            True
        )

        self.mode_label.setFont(
            mode_font
        )

        mode_column.addWidget(
            self.mode_label
        )

        header.addLayout(
            mode_column
        )

        # HELP

        self.help_button = QPushButton(
            "?"
        )

        self.help_button.setObjectName(
            "headerButton"
        )

        self.help_button.setFixedSize(
            48,
            48
        )

        self.help_button.setToolTip(
            "Help"
        )

        self.help_button.clicked.connect(
            self.open_help
        )

        header.addWidget(
            self.help_button
        )

        # SETTINGS

        self.settings_button = QPushButton(
            "⚙"
        )

        self.settings_button.setObjectName(
            "settingsButton"
        )

        self.settings_button.setFixedSize(
            58,
            58
        )

        self.settings_button.setToolTip(
            "Settings"
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

        header.addWidget(
            self.settings_button
        )

        # MORE

        self.more_button = QPushButton(
            "⋯"
        )

        self.more_button.setObjectName(
            "headerButton"
        )

        self.more_button.setFixedSize(
            48,
            48
        )

        self.more_button.setToolTip(
            "More"
        )

        self.more_button.clicked.connect(
            self.open_more_menu
        )

        header.addWidget(
            self.more_button
        )

        main_layout.addLayout(
            header
        )

        # =====================================================
        # CODING AGENT ACTIVITY
        # =====================================================

        self.coding_activity_panel = QFrame()

        self.coding_activity_panel.setObjectName(
            "codingActivityPanel"
        )

        coding_activity_layout = QVBoxLayout(
            self.coding_activity_panel
        )

        coding_activity_layout.setContentsMargins(
            18,
            12,
            18,
            12,
        )

        coding_activity_layout.setSpacing(
            6
        )

        coding_header = QHBoxLayout()

        self.coding_stage_label = QLabel(
            "CODING AGENT"
        )

        coding_stage_font = QFont(
            "Segoe UI"
        )

        coding_stage_font.setPointSize(
            10
        )

        coding_stage_font.setBold(
            True
        )

        self.coding_stage_label.setFont(
            coding_stage_font
        )

        coding_header.addWidget(
            self.coding_stage_label
        )

        coding_header.addStretch()

        self.coding_count_label = QLabel(
            "Working..."
        )

        coding_header.addWidget(
            self.coding_count_label
        )

        coding_activity_layout.addLayout(
            coding_header
        )

        self.coding_message_label = QLabel(
            ""
        )

        self.coding_message_label.setWordWrap(
            True
        )

        coding_activity_layout.addWidget(
            self.coding_message_label
        )

        self.coding_file_label = QLabel(
            ""
        )

        self.coding_file_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        coding_activity_layout.addWidget(
            self.coding_file_label
        )

        coding_progress_row = QHBoxLayout()

        self.coding_progress = QProgressBar()

        self.coding_progress.setObjectName(
            "codingProgress"
        )

        self.coding_progress.setRange(
            0,
            100
        )

        self.coding_progress.setValue(
            0
        )

        self.coding_progress.setTextVisible(
            False
        )

        coding_progress_row.addWidget(
            self.coding_progress,
            1
        )

        self.coding_model_label = QLabel(
            ""
        )

        coding_progress_row.addWidget(
            self.coding_model_label
        )

        coding_activity_layout.addLayout(
            coding_progress_row
        )

        self.coding_activity_panel.hide()

        self.coding_activity_panel.setMinimumHeight(118)

        # =====================================================
        # HERO AREA
        # =====================================================
        # The orb gets its own full-width area.
        # It is never placed in a left/right split layout.

        orb_area = QWidget()

        orb_area.setObjectName(
            "orbArea"
        )

        orb_area.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        orb_area_layout = QVBoxLayout(
            orb_area
        )

        orb_area_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        orb_area_layout.setSpacing(
            0
        )

        # =====================================================
        # ORB CANVAS
        # =====================================================

        orb_canvas = QWidget()

        orb_canvas.setObjectName(
            "orbCanvas"
        )

        orb_canvas.setFixedSize(
            600,
            600
        )

        orb_canvas_layout = QVBoxLayout(
            orb_canvas
        )

        orb_canvas_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        orb_canvas_layout.setSpacing(
            0
        )

        self.core = JarvisOrb()

        # The widget itself is the large transparent canvas.
        # jarvis_orb.py keeps the actual artwork at its fixed design size,
        # so this does not shrink the visible orb.
        self.core.setFixedSize(
            600,
            600
        )

        orb_canvas_layout.addStretch(1)

        orb_canvas_layout.addWidget(
            self.core,
            alignment=Qt.AlignHCenter
        )

        orb_canvas_layout.addStretch(3)

        orb_area_layout.addWidget(
            orb_canvas,
            alignment=Qt.AlignCenter
        )

        # =====================================================
        # ORB STATUS CAPTION
        # =====================================================

        self.state_caption = QLabel(
            "READY TO ASSIST"
        )

        self.state_caption.setAlignment(
            Qt.AlignCenter
        )

        state_font = QFont(
            "Segoe UI"
        )

        state_font.setPointSize(
            12
        )

        state_font.setBold(
            True
        )

        self.state_caption.setFont(
            state_font
        )

        orb_area_layout.addWidget(
            self.state_caption
        )

        main_layout.addWidget(
            orb_area,
            alignment=Qt.AlignHCenter
        )

        # =====================================================
        # CONVERSATION PANEL
        # =====================================================

        conversation_panel = QFrame()

        self.conversation_panel = conversation_panel

        conversation_panel.setObjectName(
            "conversationPanel"
        )

        conversation_layout = QVBoxLayout(
            conversation_panel
        )

        conversation_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        conversation_layout.setSpacing(
            10
        )

        conversation_header = QHBoxLayout()

        self.conversation_title = QLabel(
            "CONVERSATION"
        )

        conversation_title_font = QFont(
            "Segoe UI"
        )

        conversation_title_font.setPointSize(
            13
        )

        conversation_title_font.setBold(
            True
        )

        self.conversation_title.setFont(
            conversation_title_font
        )

        conversation_header.addWidget(
            self.conversation_title
        )

        conversation_header.addStretch()

        self.conversation_status = QLabel(
            "LIVE"
        )

        conversation_status_font = QFont(
            "Segoe UI"
        )

        conversation_status_font.setPointSize(
            9
        )

        conversation_status_font.setBold(
            True
        )

        self.conversation_status.setFont(
            conversation_status_font
        )

        conversation_header.addWidget(
            self.conversation_status
        )

        conversation_layout.addLayout(
            conversation_header
        )

        # CHAT SCROLL

        self.chat_scroll = QScrollArea()

        self.chat_scroll.setWidgetResizable(
            True
        )

        self.chat_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.chat_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.chat_container = QWidget()

        self.chat_layout = QVBoxLayout(
            self.chat_container
        )

        self.chat_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        self.chat_layout.setSpacing(
            10
        )

        self.chat_layout.addStretch()

        self.chat_scroll.setWidget(
            self.chat_container
        )

        conversation_layout.addWidget(
            self.chat_scroll,
            1
        )

        # PENDING ACTION

        self.pending_panel = QFrame()

        self.pending_panel.setObjectName(
            "pendingPanel"
        )

        pending_layout = QVBoxLayout(
            self.pending_panel
        )

        pending_layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        self.pending_label = QLabel(
            ""
        )

        self.pending_label.setWordWrap(
            True
        )

        pending_layout.addWidget(
            self.pending_label
        )

        self.pending_panel.hide()

        conversation_layout.addWidget(
            self.pending_panel
        )

        conversation_panel.setVisible(
            self.show_conversation_center
        )

        main_layout.addWidget(
            conversation_panel
        )

        # =====================================================
        # QUICK ACTIONS
        # =====================================================

        self.quick_title_row = QHBoxLayout()

        self.quick_icon = QLabel(
            "⚡"
        )

        quick_icon_font = QFont(
            "Segoe UI"
        )

        quick_icon_font.setPointSize(
            18
        )

        self.quick_icon.setFont(
            quick_icon_font
        )

        self.quick_title_row.addWidget(
            self.quick_icon
        )

        self.quick_title = QLabel(
            "QUICK ACTIONS"
        )

        quick_title_font = QFont(
            "Segoe UI"
        )

        quick_title_font.setPointSize(
            12
        )

        quick_title_font.setBold(
            True
        )

        self.quick_title.setFont(
            quick_title_font
        )

        self.quick_title_row.addWidget(
            self.quick_title
        )

        self.quick_title_row.addStretch()

        self.quick_buttons_layout = QHBoxLayout()

        self.quick_buttons_layout.setSpacing(
            10
        )

        self.quick_buttons = []

        quick_actions = [
            (
                "🎮",
                "Gaming Mode",
                "gaming mode"
            ),
            (
                "🌐",
                "Chrome",
                "open chrome"
            ),
            (
                "🖥",
                "Screen",
                "look at my screen"
            ),
            (
                "♫",
                "Spotify",
                "open spotify"
            ),
        ]

        for (
            icon,
            label,
            command
        ) in quick_actions:

            button = self.create_quick_action(
                icon,
                label,
                command
            )

            self.quick_buttons.append(
                button
            )

            self.quick_buttons_layout.addWidget(
                button
            )

        quick_and_coding_row = QHBoxLayout()

        quick_and_coding_row.setSpacing(
            12
        )

        quick_actions_panel = QWidget()

        quick_actions_panel.setObjectName(
            "quickActionsPanel"
        )

        quick_actions_layout = QVBoxLayout(
            quick_actions_panel
        )

        quick_actions_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        quick_actions_layout.setSpacing(
            8
        )

        quick_actions_layout.addLayout(
            self.quick_title_row
        )

        quick_actions_layout.addLayout(
            self.quick_buttons_layout
        )

        quick_and_coding_row.addWidget(
            quick_actions_panel,
            1
        )

        quick_and_coding_row.addWidget(
            self.coding_activity_panel,
            1
        )

        main_layout.addLayout(
            quick_and_coding_row
        )

        # =====================================================
        # SUGGESTIONS
        # =====================================================

        self.suggestions_panel = QFrame()

        self.suggestions_panel.setObjectName(
            "suggestionsPanel"
        )

        suggestions_layout = QHBoxLayout(
            self.suggestions_panel
        )

        suggestions_layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        suggestions_layout.setSpacing(
            8
        )

        self.suggestions_title = QLabel(
            "Suggestions:"
        )

        suggestions_layout.addWidget(
            self.suggestions_title
        )

        self.suggestion_buttons_layout = QHBoxLayout()

        suggestions_layout.addLayout(
            self.suggestion_buttons_layout,
            1
        )

        self.suggestions_panel.hide()

        main_layout.addWidget(
            self.suggestions_panel
        )

        # =====================================================
        # INPUT AREA
        # =====================================================

        input_panel = QFrame()

        input_panel.setObjectName(
            "inputPanel"
        )

        input_layout = QVBoxLayout(
            input_panel
        )

        input_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        input_layout.setSpacing(
            10
        )

        command_row = QHBoxLayout()

        self.command_input = QLineEdit()

        self.command_input.setObjectName(
            "commandInput"
        )

        self.command_input.setPlaceholderText(
            f"Talk to {self.assistant_name}..."
        )

        self.command_input.returnPressed.connect(
            self.send_text_command
        )

        command_row.addWidget(
            self.command_input,
            1
        )

        self.send_button = QPushButton(
            "➤"
        )

        self.send_button.setObjectName(
            "sendButton"
        )

        self.send_button.setFixedSize(
            58,
            58
        )

        self.send_button.setToolTip(
            "Send command"
        )

        self.send_button.clicked.connect(
            self.send_text_command
        )

        command_row.addWidget(
            self.send_button
        )

        input_layout.addLayout(
            command_row
        )

        self.voice_status_button = QPushButton(
            "🎙   VOICE ASSISTANT ACTIVE"
        )

        self.voice_status_button.setObjectName(
            "voiceButton"
        )

        self.voice_status_button.setEnabled(
            False
        )

        input_layout.addWidget(
            self.voice_status_button
        )

        main_layout.addWidget(
            input_panel
        )

    # =========================================================
    # QUICK ACTION CREATION
    # =========================================================

    def create_quick_action(
        self,
        icon,
        label,
        command
    ):
        button = QPushButton()

        button.setObjectName(
            "quickAction"
        )

        button.setMinimumHeight(
            82
        )

        button.setSizePolicy(
            button.sizePolicy().horizontalPolicy(),
            button.sizePolicy().verticalPolicy()
        )

        button.setText(
            f"{icon}\n{label}\n{command}"
        )

        button.clicked.connect(
            lambda checked=False,
            value=command:
            self.run_background_command(
                value,
                show_user_message=False
            )
        )

        return button

    # =========================================================
    # CHAT
    # =========================================================

    def clear_chat_widgets(
        self
    ):
        while (
            self.chat_layout.count()
            > 1
        ):

            item = (
                self.chat_layout.takeAt(
                    0
                )
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

    def load_conversation_history(
        self
    ):
        self.clear_chat_widgets()

        turns = get_recent_turns(
            limit=12
        )

        if not turns:

            self.add_chat_message(
                "JARVIS",
                f"Hello. I'm {self.assistant_name}. How can I help you today?",
                scroll=False
            )

        else:

            for turn in turns:

                user_text = str(
                    turn.get(
                        "user",
                        ""
                    )
                ).strip()

                assistant_text = str(
                    turn.get(
                        "assistant",
                        ""
                    )
                ).strip()

                if user_text:

                    self.add_chat_message(
                        "YOU",
                        user_text,
                        scroll=False
                    )

                if assistant_text:

                    self.add_chat_message(
                        "JARVIS",
                        assistant_text,
                        scroll=False
                    )

        self.last_history_count = (
            get_history_count()
        )

        QTimer.singleShot(
            50,
            self.scroll_chat_to_bottom
        )

    def add_chat_message(
        self,
        role,
        text,
        scroll=True
    ):
        text = str(
            text or ""
        ).strip()

        if not text:
            return

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        row.setSpacing(
            8
        )

        avatar = QLabel(
            "J"
            if role == "JARVIS"
            else "U"
        )

        avatar.setObjectName(
            "avatarJarvis"
            if role == "JARVIS"
            else "avatarUser"
        )

        avatar.setFixedSize(
            38,
            38
        )

        avatar.setAlignment(
            Qt.AlignCenter
        )

        bubble = QFrame()

        bubble.setObjectName(
            "jarvisBubble"
            if role == "JARVIS"
            else "userBubble"
        )

        bubble_layout = QVBoxLayout(
            bubble
        )

        bubble_layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        bubble_layout.setSpacing(
            3
        )

        header_row = QHBoxLayout()

        sender = QLabel(
            self.assistant_name
            if role == "JARVIS"
            else role
        )

        sender_font = QFont(
            "Segoe UI"
        )

        sender_font.setPointSize(
            9
        )

        sender_font.setBold(
            True
        )

        sender.setFont(
            sender_font
        )

        header_row.addWidget(
            sender
        )

        header_row.addStretch()

        bubble_layout.addLayout(
            header_row
        )

        message_label = QLabel(
            text
        )

        message_label.setWordWrap(
            True
        )

        message_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        message_font = QFont(
            "Segoe UI"
        )

        message_font.setPointSize(
            11
        )

        message_label.setFont(
            message_font
        )

        bubble_layout.addWidget(
            message_label
        )

        if role == "JARVIS":

            row.addWidget(
                avatar,
                alignment=Qt.AlignTop
            )

            row.addWidget(
                bubble,
                0
            )

            row.addStretch()

        else:

            row.addStretch()

            row.addWidget(
                bubble,
                0
            )

            row.addWidget(
                avatar,
                alignment=Qt.AlignTop
            )

        self.chat_layout.insertLayout(
            self.chat_layout.count() - 1,
            row
        )

        if scroll:

            QTimer.singleShot(
                20,
                self.scroll_chat_to_bottom
            )

    def scroll_chat_to_bottom(
        self
    ):
        scrollbar = (
            self.chat_scroll.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # =========================================================
    # COMMAND HANDLING
    # =========================================================

    def send_text_command(
        self
    ):
        command = (
            self.command_input
            .text()
            .strip()
        )

        if not command:
            return

        self.command_input.clear()

        self.add_chat_message(
            "YOU",
            command
        )

        self.run_background_command(
            command,
            show_user_message=False
        )

    def run_background_command(
        self,
        command,
        show_user_message=True
    ):
        command = str(
            command or ""
        ).strip()

        if not command:
            return

        if (
            show_user_message
            and not self.initializing_chat
        ):

            self.add_chat_message(
                "YOU",
                command
            )

        self.command_input.setEnabled(
            False
        )

        self.send_button.setEnabled(
            False
        )

        thread = threading.Thread(
            target=self.command_worker,
            args=(command,),
            daemon=True
        )

        thread.start()

    def command_worker(
        self,
        command
    ):
        try:

            set_state(
                "THINKING"
            )

            response = (
                execute_remote_command(
                    command
                )
            )

            response = str(
                response or ""
            ).strip()

            if not response:

                response = (
                    "I didn't get a response."
                )

            self.command_signals.finished.emit(
                command,
                response
            )

        except Exception as error:

            self.command_signals.failed.emit(
                command,
                str(error)
            )

    def command_finished(
        self,
        command,
        response
    ):
        self.command_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        self.add_chat_message(
            "JARVIS",
            response
        )

        self.refresh_suggestions()

        self.command_input.setFocus()

        set_state(
            "SPEAKING"
        )

        speech_thread = threading.Thread(
            target=self.speak_response,
            args=(response,),
            daemon=True
        )

        speech_thread.start()

    def speak_response(
        self,
        response
    ):
        try:

            speak(
                response
            )

        except Exception as error:

            print(
                "GUI speech error:",
                error
            )

        finally:

            set_state(
                "IDLE"
            )

    def command_failed(
        self,
        command,
        error
    ):
        self.command_input.setEnabled(
            True
        )

        self.send_button.setEnabled(
            True
        )

        message = (
            "I couldn't complete that command."
        )

        if error:

            print(
                "GUI command error:",
                error
            )

        self.add_chat_message(
            "JARVIS",
            message
        )

        set_state(
            "IDLE"
        )

        self.command_input.setFocus()

    # =========================================================
    # SUGGESTIONS
    # =========================================================

    def clear_suggestion_buttons(
        self
    ):
        while (
            self.suggestion_buttons_layout.count()
            > 0
        ):

            item = (
                self.suggestion_buttons_layout.takeAt(
                    0
                )
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

    def refresh_suggestions(
        self
    ):
        state = get_action_state()

        suggestions = (
            state.get(
                "suggestions",
                []
            )
        )

        pending = (
            state.get(
                "pending"
            )
        )

        self.clear_suggestion_buttons()

        if pending:

            label = str(
                pending.get(
                    "label",
                    "Pending action"
                )
            )

            description = str(
                pending.get(
                    "description",
                    ""
                )
            )

            self.pending_label.setText(
                f"Pending: {label}"
                + (
                    f" — {description}"
                    if description
                    else ""
                )
            )

            self.pending_panel.show()

        else:

            self.pending_panel.hide()

        if not suggestions:

            self.suggestions_panel.hide()

            return

        shown = suggestions[:4]

        for index, item in enumerate(
            shown
        ):

            label = str(
                item.get(
                    "label",
                    f"Option {index + 1}"
                )
            )

            button = QPushButton(
                label
            )

            button.setObjectName(
                "suggestionButton"
            )

            button.setToolTip(
                str(
                    item.get(
                        "description",
                        ""
                    )
                )
            )

            button.clicked.connect(
                lambda checked=False,
                number=index + 1:
                self.run_background_command(
                    f"option {number}",
                    show_user_message=False
                )
            )

            self.suggestion_buttons_layout.addWidget(
                button
            )

        self.suggestions_panel.show()

    # =========================================================
    # UI PREFERENCES
    # =========================================================

    def load_ui_preference(
        self,
        key,
        default
    ):
        try:
            if not os.path.exists(
                UI_PREFERENCES_FILE
            ):
                return default

            with open(
                UI_PREFERENCES_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                preferences = json.load(file)

            if not isinstance(
                preferences,
                dict
            ):
                return default

            return preferences.get(
                key,
                default
            )

        except Exception as error:
            print(
                "UI preference load error:",
                error
            )
            return default

    # =========================================================
    # DYNAMIC UI
    # =========================================================

    def refresh_dynamic_ui(
        self
    ):
        current_name = get_assistant_name()

        if current_name != self.assistant_name:
            self.assistant_name = current_name
            self.setWindowTitle(current_name)

            if hasattr(self, "brand_label"):
                self.brand_label.setText(current_name)

            if hasattr(self, "command_input"):
                self.command_input.setPlaceholderText(
                    f"Talk to {current_name}..."
                )

        self.update_jarvis_state()

        show_conversation = bool(
            self.load_ui_preference(
                "show_conversation_center",
                True
            )
        )

        if (
            show_conversation
            != self.show_conversation_center
        ):
            self.show_conversation_center = show_conversation

            if hasattr(
                self,
                "conversation_panel"
            ):
                self.conversation_panel.setVisible(
                    show_conversation
                )

        try:

            count = (
                get_history_count()
            )

            if (
                count
                != self.last_history_count
            ):

                self.load_conversation_history()

        except Exception as error:

            print(
                "Conversation refresh error:",
                error
            )

        self.refresh_suggestions()
        self.refresh_coding_activity()

    # =========================================================
    # CODING AGENT ACTIVITY
    # =========================================================

    def refresh_coding_activity(
        self
    ):
        status = read_coding_progress()

        if not status:
            if hasattr(self, "coding_activity_panel"):
                self.coding_activity_panel.hide()
            return

        timestamp = float(
            status.get(
                "timestamp",
                0.0
            )
            or 0.0
        )

        done = bool(
            status.get(
                "done",
                False
            )
        )

        if (
            done
            and timestamp
            and time.time() - timestamp > 8
        ):
            self.coding_activity_panel.hide()
            return

        stage = str(
            status.get(
                "stage",
                "WORKING"
            )
            or "WORKING"
        ).upper()

        message = str(
            status.get(
                "message",
                "Coding Agent is working..."
            )
            or "Coding Agent is working..."
        )

        current_file = str(
            status.get(
                "current_file",
                ""
            )
            or ""
        )

        files_done = int(
            status.get(
                "files_done",
                0
            )
            or 0
        )

        files_total = int(
            status.get(
                "files_total",
                0
            )
            or 0
        )

        model = str(
            status.get(
                "model",
                ""
            )
            or ""
        )

        if hasattr(self, "coding_activity_panel"):
            self.coding_activity_panel.show()

            self.coding_stage_label.setText(
                f"CODING AGENT  •  {stage}"
            )

            self.coding_message_label.setText(
                message
            )

            if current_file:
                self.coding_file_label.setText(
                    f"FILE  {current_file}"
                )
            else:
                self.coding_file_label.setText(
                    ""
                )

            if files_total > 0:
                percent = int(
                    max(
                        0,
                        min(
                            100,
                            (
                                files_done
                                * 100
                                / files_total
                            )
                        )
                    )
                )

                self.coding_progress.setValue(
                    percent
                )

                self.coding_count_label.setText(
                    f"{files_done}/{files_total} files"
                )

            else:
                self.coding_progress.setValue(
                    0
                )

                self.coding_count_label.setText(
                    "Working..."
                )

            self.coding_model_label.setText(
                model
            )

            success = status.get(
                "success"
            )

            if done and success:
                self.coding_progress.setValue(
                    100
                )

                self.coding_count_label.setText(
                    "COMPLETE"
                )

    # =========================================================
    # STATE
    # =========================================================

    def update_jarvis_state(
        self
    ):
        state = (
            get_state()
            or "IDLE"
        )

        state = str(
            state
        ).upper()

        self.status_text_for_state(
            state
        )

        self.mode_label.setText(
            get_ai_mode_label()
        )

        self.core.set_state(
            state
        )

        if self.tray_icon is not None:

            self.tray_icon.setToolTip(
                f"{self.assistant_name} — {state}"
            )

        if state != self.last_state:

            self.last_state = state

            self.update_state_visuals(
                state
            )

    def status_text_for_state(
        self,
        state
    ):
        captions = {
            "IDLE": "READY TO ASSIST",
            "LISTENING": "LISTENING",
            "THINKING": "THINKING",
            "SPEAKING": "SPEAKING",
            "WORKING": "WORKING",
            "ERROR": "SYSTEM ERROR",
        }

        self.state_caption.setText(
            captions.get(
                state,
                state
            )
        )

        self.conversation_status.setText(
            state
        )

    def update_state_visuals(
        self,
        state
    ):
        subtitle_map = {
            "IDLE": "Ready to assist.",
            "LISTENING": "Listening for you.",
            "THINKING": "Working on your request...",
            "SPEAKING": "Speaking...",
            "WORKING": "Executing task...",
            "ERROR": "Something needs attention.",
        }

        self.subtitle_label.setText(
            subtitle_map.get(
                state,
                "Ready to assist."
            )
        )

        self.online_label.setText(
            "ONLINE"
        )

        self.online_dot.setText(
            "●"
        )

    # =========================================================
    # MORE MENU
    # =========================================================

    def open_more_menu(
        self
    ):
        menu = QMenu(
            self
        )

        restart_action = QAction(
            f"Restart {self.assistant_name}",
            self
        )

        restart_action.triggered.connect(
            self.restart_jarvis
        )

        menu.addAction(
            restart_action
        )

        menu.addSeparator()

        quit_action = QAction(
            f"Exit {self.assistant_name}",
            self
        )

        quit_action.triggered.connect(
            self.quit_jarvis
        )

        menu.addAction(
            quit_action
        )

        menu.exec(
            self.more_button.mapToGlobal(
                self.more_button.rect().bottomLeft()
            )
        )

    # =========================================================
    # OVERLAY
    # =========================================================

    def setup_overlay(
        self
    ):
        self.overlay_window = OverlayWindow()

        overlay_signals.show_center_requested.connect(
            self.overlay_window.show_center
        )

        overlay_signals.show_message_requested.connect(
            self.overlay_window.show_message
        )

        overlay_signals.show_highlight_requested.connect(
            self.overlay_window.show_highlight
        )

        overlay_signals.clear_requested.connect(
            self.overlay_window.clear_overlay
        )

        print(
            "JARVIS overlay system ready."
        )

    # =========================================================
    # SYSTEM TRAY
    # =========================================================

    def setup_system_tray(
        self
    ):
        self.tray_available = (
            QSystemTrayIcon.isSystemTrayAvailable()
        )

        if not self.tray_available:

            self.tray_icon = None

            return

        icon = self.style().standardIcon(
            QStyle.SP_ComputerIcon
        )

        self.setWindowIcon(
            icon
        )

        self.tray_icon = QSystemTrayIcon(
            icon,
            self,
        )

        self.tray_icon.setToolTip(
            self.assistant_name
        )

        tray_menu = QMenu(
            self
        )

        open_action = QAction(
            f"Open {self.assistant_name}",
            self
        )

        open_action.triggered.connect(
            self.restore_from_tray
        )

        tray_menu.addAction(
            open_action
        )

        settings_action = QAction(
            "Settings",
            self
        )

        settings_action.triggered.connect(
            self.open_settings_from_tray
        )

        tray_menu.addAction(
            settings_action
        )

        help_action = QAction(
            "Help",
            self
        )

        help_action.triggered.connect(
            self.open_help_from_tray
        )

        tray_menu.addAction(
            help_action
        )

        tray_menu.addSeparator()

        clear_overlay_action = QAction(
            "Clear Overlay",
            self
        )

        clear_overlay_action.triggered.connect(
            self.clear_overlay_from_tray
        )

        tray_menu.addAction(
            clear_overlay_action
        )

        tray_menu.addSeparator()

        restart_action = QAction(
            "Restart JARVIS",
            self
        )

        restart_action.triggered.connect(
            self.restart_jarvis
        )

        tray_menu.addAction(
            restart_action
        )

        exit_action = QAction(
            "Exit JARVIS",
            self
        )

        exit_action.triggered.connect(
            self.quit_jarvis
        )

        tray_menu.addAction(
            exit_action
        )

        self.tray_icon.setContextMenu(
            tray_menu
        )

        self.tray_icon.activated.connect(
            self.tray_icon_activated
        )

        self.tray_icon.show()

    # =========================================================
    # TRAY ACTIONS
    # =========================================================

    def tray_icon_activated(
        self,
        reason
    ):
        if (
            reason
            == QSystemTrayIcon.DoubleClick
        ):

            self.restore_from_tray()

    def restore_from_tray(
        self
    ):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def open_settings_from_tray(
        self
    ):
        self.restore_from_tray()
        self.open_settings()

    def open_help_from_tray(
        self
    ):
        self.restore_from_tray()
        self.open_help()

    def clear_overlay_from_tray(
        self
    ):
        if self.overlay_window is not None:

            self.overlay_window.clear_overlay()

    # =========================================================
    # CLOSE
    # =========================================================

    def closeEvent(
        self,
        event
    ):
        if self.allow_full_exit:

            event.accept()

            return

        if not self.tray_available:

            event.accept()

            return

        event.ignore()

        self.hide()

        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
        ):

            self.settings_window.close()

        if (
            self.help_window is not None
            and self.help_window.isVisible()
        ):

            self.help_window.close()

        if self.overlay_window is not None:

            self.overlay_window.clear_overlay()

        if (
            self.tray_icon is not None
            and not self.tray_message_shown
        ):

            self.tray_icon.showMessage(
                self.assistant_name,
                f"{self.assistant_name} is still running in the background.",
                QSystemTrayIcon.Information,
                4000,
            )

            self.tray_message_shown = True

    # =========================================================
    # QUIT
    # =========================================================

    def quit_jarvis(
        self
    ):
        print(
            f"Quitting {self.assistant_name}..."
        )

        self.allow_full_exit = True

        if self.overlay_window is not None:

            try:

                self.overlay_window.clear_overlay()
                self.overlay_window.close()

            except Exception:
                pass

        if self.settings_window is not None:

            try:

                self.settings_window.close()

            except Exception:
                pass

        if self.help_window is not None:

            try:

                self.help_window.close()

            except Exception:
                pass

        if self.tray_icon is not None:

            try:

                self.tray_icon.hide()

            except Exception:
                pass

        app = QApplication.instance()

        if app is not None:

            app.quit()

    # =========================================================
    # RESTART
    # =========================================================

    def restart_jarvis(
        self
    ):
        print(
            f"Restarting {self.assistant_name}..."
        )

        try:

            if getattr(
                sys,
                "frozen",
                False
            ):

                command = [
                    sys.executable
                ]

                working_directory = (
                    os.path.dirname(
                        sys.executable
                    )
                )

            else:

                project_root = (
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(
                                __file__
                            )
                        )
                    )
                )

                main_file = os.path.join(
                    project_root,
                    "main.py"
                )

                command = [
                    sys.executable,
                    main_file
                ]

                working_directory = (
                    project_root
                )

            subprocess.Popen(
                command,
                cwd=working_directory,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if os.name == "nt"
                    else 0
                )
            )

            self.allow_full_exit = True

            if self.overlay_window is not None:

                try:

                    self.overlay_window.clear_overlay()
                    self.overlay_window.close()

                except Exception:
                    pass

            if self.tray_icon is not None:

                try:

                    self.tray_icon.hide()

                except Exception:
                    pass

            app = QApplication.instance()

            if app is not None:

                app.quit()

        except Exception as error:

            print(
                "JARVIS restart error:",
                error
            )

    # =========================================================
    # SETTINGS
    # =========================================================

    def open_settings(
        self
    ):
        if (
            self.settings_window is None
            or not self.settings_window.isVisible()
        ):

            self.settings_window = SettingsPage(
                self
            )

        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    # =========================================================
    # HELP
    # =========================================================

    def open_help(
        self
    ):
        if (
            self.help_window is None
            or not self.help_window.isVisible()
        ):

            self.help_window = HelpPage(
                self
            )

        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    # =========================================================
    # TEXT INPUT DIALOG
    # =========================================================

    def request_text_input(
        self,
        title,
        message
    ):
        if not self.isVisible():

            self.restore_from_tray()

        text, accepted = (
            QInputDialog.getText(
                self,
                title,
                message
            )
        )

        if accepted:

            submit_text_input(
                text.strip()
            )

        else:

            submit_text_input(
                ""
            )

    # =========================================================
    # THEME
    # =========================================================

    def on_theme_changed(
        self,
        theme
    ):
        self.theme = (
            theme.copy()
        )

        self.apply_theme(
            self.theme
        )

    def apply_theme(
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

        self.setStyleSheet(
            f"""
            QMainWindow,
            QWidget#centralWidget {{
                background-color: {background};
            }}

            QLabel {{
                color: {accent};
                background: transparent;
            }}

            QFrame#conversationPanel,
            QFrame#inputPanel {{
                background-color: rgba(4, 18, 34, 210);
                border: 1px solid {accent};
                border-radius: 24px;
            }}

            QWidget#orbArea,
            QWidget#orbCanvas {{
                background-color: transparent;
                border: none;
            }}

            QFrame#orbPanel {{
                background-color: transparent;
                border: none;
            }}

            QWidget#orbCanvas {{
                background: transparent;
                border: none;
            }}

            QWidget#quickActionsPanel {{
                background: transparent;
            }}

            QFrame#codingActivityPanel {{
                background-color: rgba(4, 24, 42, 235);
                border: 1px solid {accent};
                border-radius: 16px;
            }}

            QProgressBar#codingProgress {{
                border: 1px solid {accent};
                border-radius: 6px;
                background: rgba(1, 10, 20, 220);
                height: 10px;
            }}

            QProgressBar#codingProgress::chunk {{
                background-color: {accent};
                border-radius: 5px;
            }}

            QFrame#pendingPanel,
            QFrame#suggestionsPanel {{
                background-color: rgba(5, 22, 38, 220);
                border: 1px solid {accent};
                border-radius: 14px;
            }}

            QLineEdit#commandInput {{
                color: {accent};
                background-color: rgba(1, 10, 20, 230);
                border: 1px solid {accent};
                border-radius: 18px;
                padding: 14px 18px;
                font-size: 15px;
            }}

            QLineEdit#commandInput:focus {{
                border: 2px solid {accent};
            }}

            QPushButton#headerButton,
            QPushButton#settingsButton {{
                color: {accent};
                background-color: rgba(2, 10, 20, 210);
                border: 1px solid {accent};
                border-radius: 20px;
                font-size: 18px;
            }}

            QPushButton#settingsButton {{
                border-radius: 22px;
                font-size: 25px;
            }}

            QPushButton#headerButton:hover,
            QPushButton#settingsButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QPushButton#quickAction {{
                color: {accent};
                background-color: rgba(4, 18, 34, 215);
                border: 1px solid {accent};
                border-radius: 20px;
                padding: 10px;
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton#quickAction:hover {{
                background-color: rgba(18, 63, 95, 235);
                border: 2px solid {accent};
            }}

            QPushButton#suggestionButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 13px;
                padding: 7px 12px;
            }}

            QPushButton#suggestionButton:hover {{
                background-color: {accent};
                color: {background};
            }}

            QPushButton#sendButton {{
                color: {background};
                background-color: {accent};
                border: none;
                border-radius: 29px;
                font-size: 24px;
                font-weight: bold;
            }}

            QPushButton#sendButton:hover {{
                background-color: white;
            }}

            QPushButton#voiceButton {{
                color: {accent};
                background-color: transparent;
                border: 1px solid {accent};
                border-radius: 18px;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }}

            QLabel#avatarJarvis {{
                color: {accent};
                background-color: rgba(3, 23, 42, 230);
                border: 1px solid {accent};
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }}

            QLabel#avatarUser {{
                color: {background};
                background-color: {accent};
                border-radius: 19px;
                font-size: 14px;
                font-weight: bold;
            }}

            QFrame#jarvisBubble {{
                background-color: rgba(8, 32, 57, 235);
                border: 1px solid {accent};
                border-radius: 18px;
            }}

            QFrame#userBubble {{
                background-color: rgba(12, 59, 94, 235);
                border: 1px solid {accent};
                border-radius: 18px;
            }}

            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}

            QScrollBar::handle:vertical {{
                background: {accent};
                border-radius: 4px;
                min-height: 30px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QMenu {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                padding: 6px;
            }}

            QMenu::item {{
                padding: 8px 24px;
            }}

            QMenu::item:selected {{
                background-color: {accent};
                color: {background};
            }}
            """
        )

        self.core.set_theme(
            background,
            accent
        )

    # =========================================================
    # SHUTDOWN SIGNAL
    # =========================================================

    def shutdown_gui(
        self
    ):
        self.quit_jarvis()


# =============================================================
# STANDALONE GUI MODE
# =============================================================

def start_gui():
    app = QApplication(
        sys.argv
    )

    app.setQuitOnLastWindowClosed(
        False
    )

    window = JarvisWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    start_gui()