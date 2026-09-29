from PySide6.QtCore import Qt
from core.ui_blocker import (
    block_wake,
    unblock_wake
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
            950,
            760
        )

        self.theme = load_theme()

        self.help_sections = []

        self.build_ui()

        self.apply_theme(
            self.theme
        )

        theme_bus.theme_changed.connect(
            self.on_theme_changed
        )


    # =========================================================
    # WAKE WORD BLOCKING
    # =========================================================

    def showEvent(
        self,
        event
    ):
        block_wake(
            "help"
        )

        super().showEvent(
            event
        )


    def hideEvent(
        self,
        event
    ):
        unblock_wake(
            "help"
        )

        super().hideEvent(
            event
        )


    def closeEvent(
        self,
        event
    ):
        unblock_wake(
            "help"
        )

        event.accept()


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

        # =========================
        # TOP BAR
        # =========================

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
            "JARVIS HELP"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            """
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
        # INTRO
        # =========================

        intro = QLabel(
            "Use the search box below to find commands, "
            "features, settings, and examples."
        )

        intro.setAlignment(
            Qt.AlignCenter
        )

        intro.setWordWrap(
            True
        )

        main_layout.addWidget(
            intro
        )

        # =========================
        # SEARCH
        # =========================

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search help... e.g. email, code, think mode, theme"
        )

        self.search_box.textChanged.connect(
            self.filter_sections
        )

        main_layout.addWidget(
            self.search_box
        )

        # =========================
        # SCROLL AREA
        # =========================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.container = QWidget()

        self.content_layout = QVBoxLayout(
            self.container
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

        self.scroll.setWidget(
            self.container
        )

        main_layout.addWidget(
            self.scroll
        )

        # =====================================================
        # GETTING STARTED
        # =====================================================

        self.add_category(
            "GETTING STARTED"
        )

        self.add_section(
            "Wake JARVIS",
            """
Say:

"Jarvis"

while JARVIS is in IDLE mode.

JARVIS will wake up, respond, and begin listening.

Once awake, you can continue giving commands without
repeating the wake word every time.
"""
        )

        self.add_section(
            "Put JARVIS to Sleep",
            """
Say any of these:

"Jarvis go"
"Jarvis sleep"
"Go to sleep"
"Stop listening"

JARVIS will return to IDLE mode and wait for
the wake word again.
"""
        )

        self.add_section(
            "Exit JARVIS",
            """
Say:

"Jarvis exit"

or:

"Shut down Jarvis"

This completely closes JARVIS and the GUI.
"""
        )

        self.add_section(
            "Interrupt JARVIS",
            """
You can interrupt JARVIS while it is speaking
or thinking.

Say:

"Jarvis stop"

The current response stops and JARVIS returns
to listening.
"""
        )

        # =====================================================
        # AI
        # =====================================================

        self.add_category(
            "AI"
        )

        self.add_section(
            "Normal Mode",
            """
Normal Mode is designed for faster everyday responses.

Good for:

• Basic questions
• General conversation
• Short explanations
• Everyday requests

Activate it by saying:

"Normal mode"

or:

"Jarvis normal mode"

The active mode appears above the JARVIS orb.
"""
        )

        self.add_section(
            "Think Mode",
            """
Think Mode is designed for more complex requests.

Good for:

• Coding
• Troubleshooting
• Planning
• Technical questions
• Longer explanations
• Complex reasoning

Activate it by saying:

"Think mode"

or:

"Jarvis think mode"
"""
        )

        self.add_section(
            "AI Settings",
            """
Open:

Settings → AI

You can configure:

• Normal Mode model
• Think Mode model
• Temperature

The model fields are editable, so other Ollama
models can be entered later.

Temperature:

Lower values make responses more focused
and predictable.

Higher values make responses more varied
and creative.
"""
        )

        # =====================================================
        # DESKTOP AGENT
        # =====================================================

        self.add_category(
            "DESKTOP AGENT"
        )

        self.add_section(
            "Type Into Any App",
            """
Click inside a text field, editor, or document.

Then say:

"Type hello world"

JARVIS pastes the requested text at the
current cursor position.

This can work in apps such as:

• Notepad
• VS Code
• Microsoft Word
• Browser text fields
• Google Docs
• Many other desktop applications
"""
        )

        self.add_section(
            "Generate Writing and Paste It",
            """
Place your cursor where the response should appear.

Examples:

"Summarize the Second World War and paste
the summary here"

"Write a paragraph about space exploration
and paste it here"

"Write an introduction about artificial
intelligence and paste it here"

JARVIS generates the content using the active
AI mode and inserts it at the cursor.
"""
        )

        self.add_section(
            "Selected Text Commands",
            """
Highlight some text first.

Then say commands such as:

"Summarize this"

"Rewrite this"

"Fix grammar"

"Make this shorter"

"Translate this to French"

"Explain this"

For editing commands such as rewrite, grammar,
translation, or shortening, JARVIS replaces the
selected text.

Summary and explanation commands are normally
spoken unless you specifically ask JARVIS to
paste the result.
"""
        )

        # =====================================================
        # CODING
        # =====================================================

        self.add_category(
            "CODING"
        )

        self.add_section(
            "Write Code Into VS Code",
            """
Open a source file in VS Code and place the cursor
where you want the code.

Examples:

"Write a Python program that prints hello
when called upon"

"Write a function that sorts a list"

"Generate code for a simple calculator"

JARVIS generates the code and inserts it directly
into the active editor.

Generated code is not automatically executed.
"""
        )

        self.add_section(
            "Fix Selected Code",
            """
Highlight code inside VS Code.

Then say:

"Fix this code"

JARVIS sends the selected code to the AI and
replaces it with the corrected version.

You can also say:

"Add comments to this code"

to automatically add useful comments.
"""
        )

        self.add_section(
            "Create Coding Projects",
            """
JARVIS can create multi-file projects.

Examples:

"Create a project for a Python calculator"

"Build an app that tracks tasks"

"Write a quiz program and create the necessary files"

Projects are created under:

Documents\\JARVIS Projects

JARVIS can create files and folders needed by
the generated project.

When possible, the project is opened in VS Code.

Generated projects are not automatically executed.
"""
        )

        # =====================================================
        # EMAIL
        # =====================================================

        self.add_category(
            "EMAIL"
        )

        self.add_section(
            "Compose an Email",
            """
Say:

"Compose an email"

JARVIS opens a recipient box.

You can type:

• A full email address

or:

• A saved contact name

After that, JARVIS asks for the subject and body
using voice.
"""
        )

        self.add_section(
            "Confirm an Email",
            """
When the email is ready, JARVIS asks what to do.

Say:

"Confirm send"

to send it.

Say:

"Cancel email"

to discard it.

Say:

"Edit email"

to make changes before sending.
"""
        )

        self.add_section(
            "Edit an Email",
            """
After saying:

"Edit email"

JARVIS asks which part you want to edit.

You can say:

"Recipient"

"Subject"

"Body"

Recipient changes use the typing box again.

Subject and body changes are controlled by voice.

After editing, JARVIS returns to the confirmation step.

You can edit multiple parts before sending.
"""
        )

        self.add_section(
            "Contacts",
            """
Open:

Settings → Email

Contacts contain:

• Name
• Email address

Example:

Name:
dad

Email:
dad@example.com

When JARVIS asks for an email recipient, you can
simply type:

dad

and JARVIS resolves the saved address automatically.
"""
        )

        # =====================================================
        # APPS / WEB
        # =====================================================

        self.add_category(
            "APPS & WEB"
        )

        self.add_section(
            "Open Apps",
            """
Examples:

"Open Chrome"

"Open calculator"

"Launch Discord"

Detected apps and custom names are managed from:

Settings → Apps
"""
        )

        self.add_section(
            "Close Apps",
            """
Examples:

"Close Chrome"

"Quit Discord"

JARVIS attempts to locate and close the corresponding
desktop process.

Some Windows system apps and browser links may not
support this feature.
"""
        )

        self.add_section(
            "App Scanner",
            """
Open:

Settings → Apps

Use:

Rescan Apps

to search the computer for installed programs.

You can assign friendly names to detected applications.

Example:

Detected:
Google Chrome

JARVIS Name:
chrome

Then say:

"Open Chrome"
"""
        )

        self.add_section(
            "Open Websites",
            """
Examples:

"Open youtube.com"

"Open gmail.com"

"Open openai.com"

JARVIS opens the site in the default web browser.
"""
        )

        self.add_section(
            "Google Search",
            """
Examples:

"Search Google for Python tutorials"

"Search for RTX 3070 drivers"

JARVIS opens the search results in the default browser.
"""
        )

        # =====================================================
        # SYSTEM
        # =====================================================

        self.add_category(
            "SYSTEM"
        )

        self.add_section(
            "System Information",
            """
Examples:

"What CPU do I have?"

"What GPU do I have?"

"What RAM do I have?"

"What Windows version am I using?"

"How much storage do I have?"

"What is my CPU usage?"

"How much RAM am I using?"

"What is my GPU status?"

"System report"
"""
        )

        self.add_section(
            "Shut Down the Computer",
            """
Say:

"Shut down my computer"

or:

"Turn off my PC"

JARVIS asks for confirmation first.

Say:

"Confirm shutdown"

to proceed.

Say:

"Cancel shutdown"

to cancel.
"""
        )

        # =====================================================
        # APPEARANCE
        # =====================================================

        self.add_category(
            "APPEARANCE"
        )

        self.add_section(
            "Change Theme",
            """
Open:

Settings → Appearance

You can change:

• Background color
• Accent color

Theme changes update the full interface including:

• Main JARVIS window
• JARVIS orb
• AI mode text
• Activity state text
• Settings
• Help

Changes can be previewed immediately.

Click:

Save Theme

to keep the selected appearance for future launches.
"""
        )

        self.add_section(
            "Orb Status",
            """
The text below the orb shows JARVIS activity.

IDLE
Waiting for the wake word.

LISTENING
Waiting for your command.

THINKING
Processing a request.

SPEAKING
Responding to you.

The text above the orb shows the active AI mode:

NORMAL MODE

or:

THINK MODE
"""
        )

        # =====================================================
        # STORAGE
        # =====================================================

        self.add_category(
            "DATA & STORAGE"
        )

        self.add_section(
            "Personal JARVIS Data",
            """
JARVIS stores personal settings separately for
each Windows user.

The data folder is:

%LOCALAPPDATA%\\JARVIS\\data

It can contain:

• AI settings
• App aliases
• Detected app information
• Contacts
• Theme settings
• Gmail authorization

This structure helps prepare JARVIS for installation
on different computers.
"""
        )

        self.add_section(
            "Generated Coding Projects",
            """
Projects generated by the coding agent are stored in:

Documents\\JARVIS Projects

JARVIS creates a separate folder for each project.

If a folder name already exists, JARVIS creates a
new uniquely numbered folder instead of overwriting
the old project.
"""
        )

        # =====================================================
        # CODING AGENT
        # =====================================================

        self.add_category(
            "CODING AGENT"
        )

        self.add_section(
            "Dedicated Coding Agent",
            """
JARVIS can build real multi-file software projects from natural-language requests.

The Coding Agent can:
• Plan the project
• Create folders and files
• Open VS Code
• Generate files live
• Validate generated code
• Run tests when available
• Repair detected errors
• Re-test after repairs

Generated projects are stored in:

Documents\\JARVIS Projects
"""
        )

        self.add_section(
            "Live Coding Progress",
            """
While a Coding Agent build is running, the Control Center can show:

PLANNING
CREATING PROJECT
OPENING VS CODE
WRITING FILE
RUNNING TESTS
FIXING ERROR
COMPLETE

The panel can also show the current file, file count, progress, model,
and current status message.
"""
        )

        self.add_section(
            "Coding Examples",
            """
Project example:

"Jarvis, build me a Python desktop task manager with PySide6 and SQLite.
Create all necessary files, open it in VS Code, generate each file live,
run the tests, fix errors automatically, and tell me when it is complete."

Single-file example:

"Write a Python program that sorts a list."
"""
        )

        # =====================================================
        # SCREEN VISION
        # =====================================================

        self.add_category(
            "SCREEN VISION"
        )

        self.add_section(
            "Screen Understanding",
            """
JARVIS can inspect the selected screen with its vision system.

Examples:

"Look at my screen"

"What is on my screen?"

"Help me understand what I'm looking at"
"""
        )

        self.add_section(
            "OCR and Visual Targets",
            """
OCR can help read visible text and identify screen targets.

For supported visual actions, JARVIS can locate a target, highlight it
with the screen overlay, and use a confirmation step before clicking.
"""
        )

        self.add_section(
            "Multiple Monitors",
            """
Screen settings can control which display is used by screen-aware features.

Open:

Settings → Screen
"""
        )

        # =====================================================
        # REMOTE COMPANION
        # =====================================================

        self.add_category(
            "REMOTE COMPANION"
        )

        self.add_section(
            "Android / Remote Control",
            """
JARVIS includes a local-network remote-control system for a companion client.

The PC exposes the JARVIS Remote API on its configured local address and port.
"""
        )

        self.add_section(
            "Pairing and Security",
            """
The remote companion uses a pairing token for authentication.

Keep the pairing token private.

Remote connections are intended for the configured local network.
"""
        )

        # =====================================================
        # PERSONALIZATION
        # =====================================================

        self.add_category(
            "PERSONALIZATION"
        )

        self.add_section(
            "Assistant Name and Wake Settings",
            """
Open:

Settings → Personalization

You can configure the assistant name, wake phrase, and wake model settings.
Custom wake-model paths can also be configured when supported.
"""
        )

        self.add_section(
            "Response Phrases",
            """
Common assistant phrases can be customized for events such as:

• Online
• Listening
• One moment
• Done
• Sleep
• Email sent
• Email cancelled
• Shutdown cancelled
"""
        )

        # =====================================================
        # PERSONALITY
        # =====================================================

        self.add_category(
            "PERSONALITY"
        )

        self.add_section(
            "Personality Presets",
            """
Open:

Settings → Personality

JARVIS supports configurable personality presets and saved personality
settings that affect how responses are presented.
"""
        )

        # =====================================================
        # VOICE
        # =====================================================

        self.add_category(
            "VOICE"
        )

        self.add_section(
            "Voice Output",
            """
Open:

Settings → Voice

JARVIS supports configurable text-to-speech providers and voices.
The available controls depend on the selected provider.
"""
        )

        self.add_section(
            "Supported Voice Providers",
            """
The current configuration can support:

• Piper
• Kokoro
• ElevenLabs

Provider-specific controls appear when that provider is selected.
"""
        )

        # =====================================================
        # MACROS
        # =====================================================

        self.add_category(
            "MACROS"
        )

        self.add_section(
            "Macro Workflows",
            """
Open:

Settings → Macros

Macros group repeated actions into a single command.

The Control Center also includes a Gaming Mode quick action that can
use a configured macro workflow.
"""
        )

        # =====================================================
        # CUSTOM COMMANDS
        # =====================================================

        self.add_category(
            "CUSTOM COMMANDS"
        )

        self.add_section(
            "Command Editor",
            """
Open:

Settings → Commands

Use the command editor to configure custom JARVIS commands and mappings.
"""
        )

        # =====================================================
        # INTERFACE
        # =====================================================

        self.add_category(
            "INTERFACE"
        )

        self.add_section(
            "Conversation Center",
            """
The main JARVIS window can display recent conversation history with
YOU and JARVIS messages.

The Conversation Center can be shown or hidden from:

Settings → Interface
"""
        )

        self.add_section(
            "Quick Actions",
            """
The Control Center provides quick actions for common commands, including:

• Gaming Mode
• Chrome
• Screen
• Spotify

The Coding Agent progress area can share the Quick Actions row.
"""
        )

        self.add_section(
            "Theme and Appearance",
            """
Open:

Settings → Appearance

Theme controls can change the JARVIS background and accent colors.
Changes can be previewed and saved for future launches.
"""
        )

        # =====================================================
        # STARTUP AND SYSTEM TRAY
        # =====================================================

        self.add_category(
            "STARTUP & SYSTEM TRAY"
        )

        self.add_section(
            "Windows Startup",
            """
Open:

Settings → General

You can configure JARVIS to start automatically with Windows.
"""
        )

        self.add_section(
            "Start Minimized",
            """
JARVIS can start minimized to the Windows system tray while its
background assistant services continue running.
"""
        )

        self.add_section(
            "System Tray",
            """
The system tray lets JARVIS continue running without keeping the
main window visible.
"""
        )

        # =====================================================
        # SETTINGS REFERENCE
        # =====================================================

        self.add_category(
            "SETTINGS REFERENCE"
        )

        self.add_section(
            "Settings Areas",
            """
General
Startup and background behavior.

Personalization
Assistant name, wake configuration, and response phrases.

Apps
Installed-app scanning and friendly app names.

Macros
Multi-action workflows.

Commands
Custom command mappings.

Screen
Screen and display settings.

AI
Normal Mode, Think Mode, coding model when configured, and temperature.

Personality
Personality presets and response style.

Voice
Speech provider, voice, speed, and provider-specific options.

Email
Gmail and contact settings.

Appearance / Interface
Theme and interface preferences.
"""
        )

        # =====================================================
        # DATA AND STORAGE
        # =====================================================

        self.add_category(
            "DATA & STORAGE"
        )

        self.add_section(
            "JARVIS User Data",
            """
JARVIS keeps user-specific settings in its local application-data area.

Depending on enabled features, this can include:

• AI settings
• Voice settings
• Theme settings
• App aliases
• Detected apps
• Contacts
• Startup settings
• Remote settings
• UI preferences
• Personalization
"""
        )

        # =====================================================
        # COMMAND QUICK REFERENCE
        # =====================================================

        self.add_category(
            "QUICK COMMAND REFERENCE"
        )

        self.add_section(
            "Useful Voice Commands",
            """
Wake:
"Jarvis"

Sleep:
"Jarvis go"

Stop response:
"Jarvis stop"

Fast AI:
"Normal mode"

Deep AI:
"Think mode"

Open app:
"Open Chrome"

Close app:
"Close Chrome"

Search:
"Search Google for..."

Email:
"Compose an email"

Type:
"Type hello"

Generate writing:
"Write a paragraph about... and paste it here"

Selected text:
"Fix grammar"

Coding:
"Write a Python program that..."

Project:
"Create a project for..."

PC shutdown:
"Shut down my computer"

Exit:
"Jarvis exit"
"""
        )

        self.no_results_label = QLabel(
            "No help sections matched your search."
        )

        self.no_results_label.setAlignment(
            Qt.AlignCenter
        )

        self.no_results_label.setVisible(
            False
        )

        self.content_layout.addWidget(
            self.no_results_label
        )

        self.content_layout.addStretch()


    # =========================================================
    # CATEGORY
    # =========================================================

    def add_category(
        self,
        title
    ):
        label = QLabel(
            title
        )

        label.setObjectName(
            "categoryHeading"
        )

        label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
            """
        )

        self.content_layout.addWidget(
            label
        )

        self.help_sections.append(
            {
                "type": "category",
                "widget": label,
                "search": title.lower()
            }
        )


    # =========================================================
    # HELP SECTION
    # =========================================================

    def add_section(
        self,
        title,
        text
    ):
        section = QFrame()

        section.setObjectName(
            "helpSection"
        )

        section_layout = QVBoxLayout(
            section
        )

        section_layout.setContentsMargins(
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
            """
            font-size: 18px;
            font-weight: bold;
            """
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

        section_layout.addWidget(
            heading
        )

        section_layout.addWidget(
            body
        )

        self.content_layout.addWidget(
            section
        )

        search_text = (
            title
            + " "
            + text
        ).lower()

        self.help_sections.append(
            {
                "type": "section",
                "widget": section,
                "search": search_text
            }
        )


    # =========================================================
    # SEARCH
    # =========================================================

    def filter_sections(
        self,
        text
    ):
        query = (
            text
            .lower()
            .strip()
        )

        visible_sections = 0

        category_visible = False

        for item in self.help_sections:

            if item[
                "type"
            ] == "category":
                item[
                    "widget"
                ].setVisible(
                    not query
                )

                continue

            match = (
                not query
                or query in item[
                    "search"
                ]
            )

            item[
                "widget"
            ].setVisible(
                match
            )

            if match:
                visible_sections += 1

        self.no_results_label.setVisible(
            visible_sections == 0
        )


    # =========================================================
    # THEME
    # =========================================================

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

            QLineEdit {{
                background-color: {background};
                color: {accent};
                border: 1px solid {accent};
                border-radius: 7px;
                padding: 10px;
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

            QLabel#categoryHeading {{
                color: {accent};
            }}
            """
        )