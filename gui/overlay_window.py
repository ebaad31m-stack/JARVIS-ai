from PySide6.QtCore import (
    QPoint,
    QRect,
    Qt,
    QTimer,
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
)

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
)


class OverlayWindow(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.highlight_rect = QRect()
        self.highlight_text = ""

        self.overlay_mode = "box"

        self.auto_hide_timer = QTimer(
            self
        )

        self.auto_hide_timer.setSingleShot(
            True
        )

        self.auto_hide_timer.timeout.connect(
            self.clear_overlay
        )

        self.setup_window()

    # =========================================================
    # WINDOW SETUP
    # =========================================================

    def setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True,
        )

        self.setAttribute(
            Qt.WA_ShowWithoutActivating,
            True,
        )

        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True,
        )

        self.hide()

    # =========================================================
    # SCREEN GEOMETRY
    # =========================================================

    def update_screen_geometry(self):
        app = QApplication.instance()

        if app is None:
            return

        screens = app.screens()

        if not screens:
            return

        combined = screens[0].geometry()

        for screen in screens[1:]:
            combined = combined.united(
                screen.geometry()
            )

        self.setGeometry(
            combined
        )

    # =========================================================
    # HIGHLIGHT RECTANGLE
    # =========================================================

    def show_highlight(
        self,
        x,
        y,
        width=300,
        height=160,
        text="Click here",
        duration=5000,
        mode="box",
    ):
        self.update_screen_geometry()

        global_position = QPoint(
            int(x),
            int(y),
        )

        local_position = global_position - self.geometry().topLeft()

        self.highlight_rect = QRect(
            local_position.x(),
            local_position.y(),
            int(width),
            int(height),
        )

        self.highlight_text = str(
            text
        )

        self.overlay_mode = mode

        self.show()

        self.raise_()

        self.update()

        self.auto_hide_timer.stop()

        if duration and duration > 0:
            self.auto_hide_timer.start(
                int(duration)
            )

    # =========================================================
    # CENTER HIGHLIGHT
    # =========================================================

    def show_center(
        self,
        text="JARVIS Overlay",
        duration=5000,
    ):
        app = QApplication.instance()

        if app is None:
            return

        screen = app.primaryScreen()

        if screen is None:
            return

        geometry = screen.geometry()

        width = 360
        height = 180

        x = (
            geometry.x()
            + (
                geometry.width()
                - width
            ) // 2
        )

        y = (
            geometry.y()
            + (
                geometry.height()
                - height
            ) // 2
        )

        self.show_highlight(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            duration=duration,
        )

    # =========================================================
    # FULL SCREEN MESSAGE
    # =========================================================

    def show_message(
        self,
        text,
        duration=5000,
    ):
        self.update_screen_geometry()

        geometry = self.geometry()

        width = 520
        height = 130

        x = (
            geometry.x()
            + (
                geometry.width()
                - width
            ) // 2
        )

        y = (
            geometry.y()
            + 80
        )

        self.show_highlight(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            duration=duration,
            mode="message",
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_overlay(self):
        self.auto_hide_timer.stop()

        self.highlight_rect = QRect()

        self.highlight_text = ""

        self.hide()

        self.update()

    # =========================================================
    # PAINT
    # =========================================================

    def paintEvent(
        self,
        event,
    ):
        if self.highlight_rect.isNull():
            return

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        accent = QColor(
            0,
            220,
            255,
        )

        glow = QColor(
            0,
            220,
            255,
            70,
        )

        dark_background = QColor(
            0,
            0,
            0,
            175,
        )

        rect = self.highlight_rect

        # =====================================================
        # GLOW
        # =====================================================

        glow_pen = QPen(
            glow
        )

        glow_pen.setWidth(
            18
        )

        painter.setPen(
            glow_pen
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawRoundedRect(
            rect,
            18,
            18,
        )

        # =====================================================
        # BORDER
        # =====================================================

        border_pen = QPen(
            accent
        )

        border_pen.setWidth(
            4
        )

        painter.setPen(
            border_pen
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawRoundedRect(
            rect,
            18,
            18,
        )

        # =====================================================
        # LABEL BACKGROUND
        # =====================================================

        if self.highlight_text:
            text_rect = QRect(
                rect.x(),
                max(
                    0,
                    rect.y() - 58,
                ),
                max(
                    260,
                    rect.width(),
                ),
                48,
            )

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                dark_background
            )

            painter.drawRoundedRect(
                text_rect,
                10,
                10,
            )

            # =================================================
            # TEXT
            # =================================================

            painter.setPen(
                accent
            )

            font = QFont()

            font.setPointSize(
                13
            )

            font.setBold(
                True
            )

            painter.setFont(
                font
            )

            painter.drawText(
                text_rect.adjusted(
                    14,
                    0,
                    -14,
                    0,
                ),
                Qt.AlignVCenter
                | Qt.AlignLeft,
                self.highlight_text,
            )

        painter.end()