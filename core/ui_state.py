from PySide6.QtCore import QObject, Signal


class UIState(QObject):
    state_changed = Signal(str)
    shutdown_requested = Signal()


ui_state = UIState()

current_state = "IDLE"


def set_state(state):
    global current_state

    current_state = state.upper()
    ui_state.state_changed.emit(current_state)


def get_state():
    return current_state


def request_shutdown():
    ui_state.shutdown_requested.emit()