import sys
import threading

from PySide6.QtWidgets import QApplication

from core.assistant import start_assistant
from gui.main_window import JarvisWindow


def run_assistant():
    start_assistant()


def main():
    app = QApplication(sys.argv)

    window = JarvisWindow()
    window.show()

    assistant_thread = threading.Thread(
        target=run_assistant,
        daemon=True
    )

    assistant_thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()