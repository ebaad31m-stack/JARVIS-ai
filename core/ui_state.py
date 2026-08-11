import threading

from PySide6.QtCore import QObject, Signal


class UIState(QObject):
    state_changed = Signal(str)

    shutdown_requested = Signal()

    text_input_requested = Signal(
        str,
        str
    )


ui_state = UIState()

current_state = "IDLE"

text_input_event = threading.Event()
text_input_result = None


def set_state(state):
    global current_state

    current_state = state.upper()

    ui_state.state_changed.emit(
        current_state
    )


def get_state():
    return current_state


def request_shutdown():
    ui_state.shutdown_requested.emit()


def request_text_input(
    title,
    message
):
    global text_input_result

    text_input_result = None

    text_input_event.clear()

    ui_state.text_input_requested.emit(
        title,
        message
    )

    text_input_event.wait()

    return text_input_result


def submit_text_input(value):
    global text_input_result

    text_input_result = value

    text_input_event.set()