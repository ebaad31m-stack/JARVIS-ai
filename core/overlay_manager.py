from PySide6.QtCore import (
    QObject,
    Signal,
)


class OverlaySignals(QObject):

    show_center_requested = Signal(
        str,
        int,
    )

    show_message_requested = Signal(
        str,
        int,
    )

    show_highlight_requested = Signal(
        int,
        int,
        int,
        int,
        str,
        int,
    )

    clear_requested = Signal()


overlay_signals = OverlaySignals()


# =========================================================
# CENTER
# =========================================================

def highlight_center(
    text="Look here",
    duration=5000,
):
    overlay_signals.show_center_requested.emit(
        str(text),
        int(duration),
    )


# =========================================================
# MESSAGE
# =========================================================

def show_overlay_message(
    text,
    duration=5000,
):
    overlay_signals.show_message_requested.emit(
        str(text),
        int(duration),
    )


# =========================================================
# CUSTOM POSITION
# =========================================================

def highlight_area(
    x,
    y,
    width=300,
    height=160,
    text="Click here",
    duration=5000,
):
    x = int(
        x
    )

    y = int(
        y
    )

    width = max(
        20,
        int(
            width
        ),
    )

    height = max(
        20,
        int(
            height
        ),
    )

    overlay_signals.show_highlight_requested.emit(
        x,
        y,
        width,
        height,
        str(text),
        int(duration),
    )


# =========================================================
# HIGHLIGHT BOX
# =========================================================

def highlight_box(
    x1,
    y1,
    x2,
    y2,
    text="Click here",
    duration=7000,
):
    x1 = int(
        x1
    )

    y1 = int(
        y1
    )

    x2 = int(
        x2
    )

    y2 = int(
        y2
    )

    left = min(
        x1,
        x2,
    )

    top = min(
        y1,
        y2,
    )

    right = max(
        x1,
        x2,
    )

    bottom = max(
        y1,
        y2,
    )

    width = max(
        20,
        right - left,
    )

    height = max(
        20,
        bottom - top,
    )

    highlight_area(
        x=left,
        y=top,
        width=width,
        height=height,
        text=text,
        duration=duration,
    )


# =========================================================
# CLEAR
# =========================================================

def clear_overlay():
    overlay_signals.clear_requested.emit()