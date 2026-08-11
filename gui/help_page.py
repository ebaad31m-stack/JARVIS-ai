from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QScrollArea
)

from gui.theme_manager import load_theme


class HelpPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("JARVIS Help")
        self.resize(850, 700)

        self.theme = load_theme()

        self.build_ui()
        self.apply_theme()


    def build_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        # =========================
        # BACK BUTTON
        # =========================

        self.back_button = QPushButton("← Back")
        self.back_button.setFixedWidth(100)

        self.back_button.clicked.connect(
            self.close
        )

        main_layout.addWidget(
            self.back_button,
            alignment=Qt.AlignLeft
        )

        # =========================
        # TITLE
        # =========================

        title = QLabel("JARVIS HELP")

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
        """)

        main_layout.addWidget(title)

        # =========================
        # SCROLL AREA
        # =========================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setSpacing(18)

        # =========================
        # HELP SECTIONS
        # =========================

        self.add_section(
            content_layout,
            "Wake JARVIS",
            """
Say "Jarvis" to wake the assistant.

After JARVIS wakes up, you can continue giving commands without repeating the wake word every time.

To put JARVIS back into idle mode, say:
• Go to sleep
• Jarvis sleep
• Jarvis go
"""
        )

        self.add_section(
            content_layout,
            "Interrupt JARVIS",
            """
While JARVIS is speaking, say:

• Jarvis stop
• Stop
• Stop talking
• Be quiet

JARVIS will stop speaking and return to listening mode.
"""
        )

        self.add_section(
            content_layout,
            "Open Apps",
            """
You can launch apps that have been assigned a JARVIS name in Settings.

Examples:

• Open Chrome
• Launch Discord
• Open Steam
• Launch FC 26

Go to:
Settings → Apps

Search for the app, assign a name, then click Save Aliases.
"""
        )

        self.add_section(
            content_layout,
            "Close Apps",
            """
JARVIS can close apps that were assigned in Settings.

Examples:

• Close Chrome
• Close Discord
• Quit Steam
"""
        )

        self.add_section(
            content_layout,
            "Websites",
            """
JARVIS can open websites directly.

Examples:

• Open youtube.com
• Open gmail.com
• Open reddit.com
• Open github.com
"""
        )

        self.add_section(
            content_layout,
            "Google Search",
            """
JARVIS can search Google for you.

Examples:

• Search Google for Python tutorials
• Search for RTX 3070 drivers
• Search for weather in Toronto
"""
        )

        self.add_section(
            content_layout,
            "System Information",
            """
Examples:

• What CPU do I have?
• What GPU do I have?
• What RAM do I have?
• What is my CPU usage?
• How much RAM am I using?
• System report
"""
        )

        self.add_section(
            content_layout,
            "Shut Down Your PC",
            """
Say:

"Shut down my computer."

JARVIS will ask you to confirm.

Say:

"Confirm shutdown."

to continue.

Say:

"Cancel shutdown."

to cancel.
"""
        )

        self.add_section(
            content_layout,
            "App Scanner",
            """
JARVIS scans your computer for installed applications.

Go to:

Settings → Apps

From there you can:

• Search detected apps
• Assign custom names
• Save aliases
• Rescan your computer

Example:

Detected app:
Discord.exe

JARVIS name:
discord

Then say:

"Launch Discord."
"""
        )

        self.add_section(
            content_layout,
            "Appearance",
            """
Go to:

Settings → Appearance

Color 1 controls the main background.

Color 2 controls the JARVIS accent color.

The accent color changes things such as:

• Orb rings
• Orb spikes
• Buttons
• Status text
• Interface highlights
"""
        )

        self.add_section(
            content_layout,
            "JARVIS States",
            """
The main screen shows what JARVIS is currently doing.

IDLE
Waiting for the wake word.

LISTENING
Listening for your command.

THINKING
Processing your request.

SPEAKING
JARVIS is talking.
"""
        )

        self.add_section(
            content_layout,
            "Exit JARVIS",
            """
Say:

• Jarvis exit
• Exit
• Shut down Jarvis

JARVIS will shut itself down and close the application.
"""
        )

        self.add_section(
            content_layout,
            "Email",
            """
Email control is coming next.

The planned system will let you:

• Compose emails by voice
• Choose contacts
• Set a subject
• Dictate the message
• Review the email
• Confirm before sending
"""
        )

        content_layout.addStretch()

        scroll.setWidget(content)

        main_layout.addWidget(
            scroll
        )


    def add_section(
        self,
        layout,
        title_text,
        body_text
    ):
        title = QLabel(title_text)

        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        body = QLabel(
            body_text.strip()
        )

        body.setWordWrap(True)

        body.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        layout.addWidget(title)
        layout.addWidget(body)


    def apply_theme(self):
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

            QScrollArea {{
                border: 1px solid {accent};
                border-radius: 6px;
            }}
            """
        )