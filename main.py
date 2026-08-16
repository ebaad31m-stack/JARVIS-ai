import sys
import threading

from PySide6.QtWidgets import (
    QApplication
)

from core.paths import (
    initialize_user_data
)

from core.setup_manager import (
    is_setup_complete
)

from core.assistant import (
    start_assistant
)

from gui.main_window import (
    JarvisWindow
)

from gui.setup_wizard import (
    SetupWizard
)


def run_assistant():
    start_assistant()


class JarvisApplication:

    def __init__(self):
        self.app = QApplication(
            sys.argv
        )

        self.app.setQuitOnLastWindowClosed(
            False
        )

        self.main_window = None
        self.setup_window = None

        self.start_minimized = (
            "--minimized"
            in sys.argv
        )


    def start(self):
        initialize_user_data()

        if is_setup_complete():
            self.launch_jarvis()

        else:
            self.launch_setup()

        sys.exit(
            self.app.exec()
        )


    def launch_setup(self):
        self.setup_window = SetupWizard()

        self.setup_window.finished.connect(
            self.launch_jarvis
        )

        self.setup_window.show()

        self.setup_window.raise_()

        self.setup_window.activateWindow()


    def launch_jarvis(self):
        if self.main_window is not None:
            if self.main_window.isVisible():
                return

            self.main_window.showNormal()
            self.main_window.raise_()
            self.main_window.activateWindow()

            return

        self.main_window = JarvisWindow()

        # =====================================================
        # NORMAL START
        # =====================================================

        if not self.start_minimized:
            self.main_window.show()

        # =====================================================
        # WINDOWS STARTUP
        # =====================================================

        else:
            self.main_window.hide()

            print(
                "JARVIS started minimized to system tray."
            )

        # =====================================================
        # ASSISTANT THREAD
        # =====================================================

        assistant_thread = threading.Thread(
            target=run_assistant,
            daemon=True
        )

        assistant_thread.start()


def main():
    jarvis = JarvisApplication()

    jarvis.start()


if __name__ == "__main__":
    main()