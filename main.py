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

        self.main_window = None
        self.setup_window = None


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


    def launch_jarvis(self):
        if (
            self.main_window is not None
            and self.main_window.isVisible()
        ):
            return

        self.main_window = JarvisWindow()

        self.main_window.show()

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