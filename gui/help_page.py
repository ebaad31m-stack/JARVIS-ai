from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget
)

from gui.theme_manager import (
    load_theme,
    theme_bus
)


class HelpPage(QWidget):

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "JARVIS Help"
        )

        self.resize(
            900,
            700
        )

        self.theme = load_theme()

        self.build_ui()

        self.apply_theme(
            self.theme
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )


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

        back_button = QPushButton(
            "← Back"
        )

        back_button.setFixedWidth(
            100
        )

        back_button.clicked.connect(
            self.close
        )

        title = QLabel(
            "JARVIS HELP"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        top_bar.addWidget(
            back_button
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


        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        container = QWidget()

        self.content_layout = QVBoxLayout(
            container
        )

        self.content_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        self.content_layout.setSpacing(
            18
        )

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )


        intro = QLabel(
            "JARVIS is a voice-controlled "
            "desktop assistant. Wake it, "
            "speak naturally, and use the "
            "examples below."
        )

        intro.setWordWrap(
            True
        )

        self.content_layout.addWidget(
            intro
        )


        self.add_section(
            "Wake and Sleep",

            """
Say "Jarvis" to wake the assistant.

Say:

"Jarvis go"
"Jarvis sleep"
"Go to sleep"

to return to IDLE.
"""
        )


        self.add_section(
            "Interrupt JARVIS",

            """
Say:

"Jarvis stop"

while JARVIS is speaking or thinking
to stop the current response.
"""
        )


        self.add_section(
            "AI Modes",

            """
Say:

"Normal mode"

for the fast everyday AI.

Say:

"Think mode"

for the deeper AI.

The current mode is shown above the orb.

Models and temperature can be changed in:

Settings → AI
"""
        )


        self.add_section(
            "Type on Your Screen",

            """
Place your cursor in a text field or editor.

Then say:

"Type hello world"

JARVIS pastes the requested text at
the current cursor position.
"""
        )


        self.add_section(
            "Generate Writing and Paste It",

            """
Keep your cursor where you want the result.

Examples:

"Summarize the Second World War and
paste the summary here"

"Write a paragraph about space exploration
and paste it here"

"Write an introduction about a famous
book and paste it here"

JARVIS generates the content using the
active AI mode and inserts it at the cursor.
"""
        )


        self.add_section(
            "Work With Selected Text",

            """
Highlight text first.

Then say commands such as:

"Summarize this"

"Rewrite this"

"Fix grammar"

"Make this shorter"

"Translate this to French"

"Explain this"

Rewrite, grammar, shortening and translation
commands replace the selected text.

Summary and explanation are spoken unless
you ask JARVIS to paste the result.
"""
        )


        self.add_section(
            "Coding in VS Code",

            """
Put your cursor inside VS Code.

Examples:

"Write a Python program that prints hello
when called upon"

"Write a function that sorts a list"

JARVIS generates the code and inserts it
into the active editor.

Generated code is not automatically executed.
"""
        )


        self.add_section(
            "Fix Selected Code",

            """
Highlight code.

Then say:

"Fix this code"

or:

"Add comments to this code"

JARVIS replaces the selected code with
the generated revision.
"""
        )


        self.add_section(
            "Create Coding Projects",

            """
Examples:

"Create a project for a Python calculator"

"Build an app that tracks tasks"

"Write a program for a quiz and create
the necessary files"

JARVIS creates a new project under:

Documents\\JARVIS Projects

It creates the needed text files and opens
the project in VS Code when available.

JARVIS does not automatically run
the generated project.
"""
        )


        self.add_section(
            "Apps and Websites",

            """
Examples:

"Open Chrome"

"Close Chrome"

"Open youtube.com"

"Search Google for Python tutorials"

Manage application aliases from:

Settings → Apps
"""
        )


        self.add_section(
            "Email",

            """
Say:

"Compose an email"

Type the recipient or a saved contact name.

Then dictate the subject and message.

At confirmation say:

"Confirm send"

"Edit email"

or:

"Cancel email"

After saying "Edit email", choose:

Recipient
Subject
Body

Contacts are managed in:

Settings → Email
"""
        )


        self.add_section(
            "System Information",

            """
Examples:

"What CPU do I have?"

"What GPU do I have?"

"How much RAM am I using?"

"System report"
"""
        )


        self.add_section(
            "Computer Shutdown",

            """
Say:

"Shut down my computer"

JARVIS asks for confirmation first.

Say:

"Confirm shutdown"

or:

"Cancel shutdown"
"""
        )


        self.add_section(
            "Appearance",

            """
Open:

Settings → Appearance

Background and accent changes now update:

• Main JARVIS window
• JARVIS orb
• Mode label
• State label
• Settings
• Help

Color changes are previewed immediately.

Click Save Theme to keep them for
future launches.
"""
        )


        self.add_section(
            "Orb States",

            """
Below the orb:

IDLE
LISTENING
THINKING
SPEAKING

Above the orb:

NORMAL MODE

or

THINK MODE
"""
        )


        self.add_section(
            "User Data",

            """
JARVIS stores personal data under:

%LOCALAPPDATA%\\JARVIS\\data

This includes things such as:

• AI settings
• App aliases
• Contacts
• Theme
• Gmail authorization
"""
        )


        self.add_section(
            "Exit JARVIS",

            """
Say:

"Jarvis exit"

or:

"Shut down Jarvis"

to close the assistant and GUI.
"""
        )


        self.content_layout.addStretch()


    def add_section(
        self,
        title,
        text
    ):
        section = QFrame()

        section.setObjectName(
            "helpSection"
        )

        layout = QVBoxLayout(
            section
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        heading = QLabel(
            title
        )

        heading.setObjectName(
            "helpHeading"
        )

        heading.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        body = QLabel(
            text.strip()
        )

        body.setWordWrap(
            True
        )

        body.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            body
        )

        self.content_layout.addWidget(
            section
        )


    def on_theme_changed(
        self,
        theme
    ):
        self.theme = theme.copy()

        self.apply_theme(
            self.theme
        )


    def apply_theme(
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
                border: none;
                background-color: {background};
            }}

            QFrame#helpSection {{
                border: 1px solid {accent};
                border-radius: 10px;
                background-color: {background};
            }}

            QLabel#helpHeading {{
                color: {accent};
            }}
            """
        )