import math
import random

from gui.theme_manager import load_theme

from PySide6.QtCore import QTimer
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen
)
from PySide6.QtWidgets import QWidget


class JarvisOrb(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(
            420,
            420
        )

        self.rotation = 0
        self.inner_rotation = 0
        self.pulse = 0

        self.state = "IDLE"

        theme = load_theme()

        self.background_color = theme[
            "color_1"
        ]

        self.accent_color = theme[
            "color_2"
        ]

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_animation
        )

        self.timer.start(30)


    def set_state(self, state):
        self.state = state.upper()


    def set_theme(
        self,
        background,
        accent
    ):
        self.background_color = background
        self.accent_color = accent

        self.update()


    def update_animation(self):
        speed = 0.5

        if self.state == "LISTENING":
            speed = 1.2

        elif self.state == "THINKING":
            speed = 2.2

        elif self.state == "SPEAKING":
            speed = 1.6

        self.rotation += speed

        self.inner_rotation -= (
            speed * 0.7
        )

        self.pulse += 0.08

        self.update()


    def make_accent(
        self,
        alpha=255
    ):
        color = QColor(
            self.accent_color
        )

        color.setAlpha(
            alpha
        )

        return color


    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        center_x = (
            self.width() / 2
        )

        center_y = (
            self.height() / 2
        )

        base_radius = min(
            self.width(),
            self.height()
        ) * 0.32

        pulse_amount = (
            math.sin(
                self.pulse
            ) * 5
        )

        # =========================
        # OUTER SPIKES
        # =========================

        spike_count = 72

        for i in range(
            spike_count
        ):
            angle = math.radians(
                (
                    360
                    / spike_count
                )
                * i
            )

            start_radius = (
                base_radius + 55
            )

            spike_length = 10

            if self.state == "SPEAKING":
                spike_length += (
                    random.randint(
                        5,
                        35
                    )
                )

            elif self.state == "LISTENING":
                spike_length += (
                    random.randint(
                        2,
                        12
                    )
                )

            elif self.state == "THINKING":
                spike_length += (
                    random.randint(
                        1,
                        8
                    )
                )

            x1 = (
                center_x
                + math.cos(angle)
                * start_radius
            )

            y1 = (
                center_y
                + math.sin(angle)
                * start_radius
            )

            x2 = (
                center_x
                + math.cos(angle)
                * (
                    start_radius
                    + spike_length
                )
            )

            y2 = (
                center_y
                + math.sin(angle)
                * (
                    start_radius
                    + spike_length
                )
            )

            pen = QPen(
                self.make_accent(
                    170
                )
            )

            pen.setWidth(1)

            painter.setPen(
                pen
            )

            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2)
            )

        # =========================
        # OUTER RING
        # =========================

        outer_pen = QPen(
            self.make_accent()
        )

        outer_pen.setWidth(3)

        painter.setPen(
            outer_pen
        )

        outer_radius = (
            base_radius + 40
        )

        painter.drawEllipse(
            int(
                center_x
                - outer_radius
            ),
            int(
                center_y
                - outer_radius
            ),
            int(
                outer_radius * 2
            ),
            int(
                outer_radius * 2
            )
        )

        # =========================
        # ROTATING SEGMENTS
        # =========================

        segment_pen = QPen(
            self.make_accent(
                230
            )
        )

        segment_pen.setWidth(5)

        painter.setPen(
            segment_pen
        )

        segment_radius = (
            base_radius + 25
        )

        rect_x = (
            center_x
            - segment_radius
        )

        rect_y = (
            center_y
            - segment_radius
        )

        rect_size = (
            segment_radius * 2
        )

        for i in range(8):
            start_angle = (
                self.rotation
                + i * 45
            )

            painter.drawArc(
                int(rect_x),
                int(rect_y),
                int(rect_size),
                int(rect_size),
                int(
                    start_angle * 16
                ),
                int(
                    22 * 16
                )
            )

        # =========================
        # INNER ROTATING RING
        # =========================

        inner_pen = QPen(
            self.make_accent(
                200
            )
        )

        inner_pen.setWidth(3)

        painter.setPen(
            inner_pen
        )

        inner_radius = (
            base_radius - 10
        )

        inner_x = (
            center_x
            - inner_radius
        )

        inner_y = (
            center_y
            - inner_radius
        )

        inner_size = (
            inner_radius * 2
        )

        for i in range(6):
            start_angle = (
                self.inner_rotation
                + i * 60
            )

            painter.drawArc(
                int(inner_x),
                int(inner_y),
                int(inner_size),
                int(inner_size),
                int(
                    start_angle * 16
                ),
                int(
                    30 * 16
                )
            )

        # =========================
        # CORE
        # =========================

        core_radius = (
            base_radius * 0.55
            + pulse_amount
        )

        core_pen = QPen(
            self.make_accent()
        )

        core_pen.setWidth(4)

        painter.setPen(
            core_pen
        )

        painter.drawEllipse(
            int(
                center_x
                - core_radius
            ),
            int(
                center_y
                - core_radius
            ),
            int(
                core_radius * 2
            ),
            int(
                core_radius * 2
            )
        )

        # =========================
        # CENTER RINGS
        # =========================

        small_pen = QPen(
            self.make_accent(
                170
            )
        )

        small_pen.setWidth(2)

        painter.setPen(
            small_pen
        )

        for multiplier in [
            0.25,
            0.35,
            0.45
        ]:
            radius = (
                base_radius
                * multiplier
            )

            painter.drawEllipse(
                int(
                    center_x
                    - radius
                ),
                int(
                    center_y
                    - radius
                ),
                int(
                    radius * 2
                ),
                int(
                    radius * 2
                )
            )

        painter.end()