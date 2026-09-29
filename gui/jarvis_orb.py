import math
import random

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import (
    QColor,
    QConicalGradient,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class JarvisOrb(QWidget):

    def __init__(
        self,
        parent=None
    ):
        super().__init__(parent)

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True,
        )

        # Large transparent canvas. The actual orb artwork stays at
        # a fixed visual size inside this space, with room around the
        # glow, particles, rings, and orbital effects.
        self.setMinimumSize(
            500,
            500,
        )

        # =====================================================
        # COLORS
        # =====================================================

        self.background = QColor(
            "#05080c"
        )

        self.accent = QColor(
            "#7fe7ff"
        )

        # =====================================================
        # STATE
        # =====================================================

        self.state = "IDLE"

        self.phase = 0.0
        self.rotation = 0.0
        self.scan = 0.0
        self.pulse = 0.0

        # =====================================================
        # PARTICLES
        # =====================================================

        rng = random.Random(
            1337
        )

        self.particles = []

        for _ in range(72):

            self.particles.append(
                {
                    "angle": rng.uniform(
                        0.0,
                        math.tau,
                    ),
                    "radius": rng.uniform(
                        0.78,
                        1.34,
                    ),
                    "speed": rng.uniform(
                        0.0007,
                        0.0022,
                    ),
                    "size": rng.uniform(
                        0.7,
                        2.0,
                    ),
                    "alpha": rng.randint(
                        55,
                        180,
                    ),
                    "phase": rng.uniform(
                        0.0,
                        math.tau,
                    ),
                }
            )

        # =====================================================
        # ANIMATION
        # =====================================================

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.animate
        )

        self.timer.start(
            16
        )

    # =========================================================
    # PUBLIC API
    # =========================================================

    def set_state(
        self,
        state,
    ):

        self.state = (
            str(
                state
                or "IDLE"
            )
            .upper()
            .strip()
            or "IDLE"
        )

        self.update()

    def set_theme(
        self,
        background,
        accent,
    ):

        self.background = QColor(
            str(background)
        )

        self.accent = QColor(
            str(accent)
        )

        self.update()

    # =========================================================
    # ANIMATION
    # =========================================================

    def animate(
        self,
    ):

        state_speed = {
            "IDLE": 0.55,
            "LISTENING": 1.55,
            "THINKING": 2.35,
            "SPEAKING": 1.85,
            "ERROR": 2.8,
        }.get(
            self.state,
            1.0,
        )

        self.phase += (
            0.045
            * state_speed
        )

        self.rotation += (
            0.018
            * state_speed
        )

        self.scan = (
            self.scan
            + 0.012
            * state_speed
        ) % 1.0

        self.pulse += (
            0.032
            * state_speed
        )

        for particle in self.particles:

            particle["angle"] += (
                particle["speed"]
                * state_speed
            )

        self.update()

    # =========================================================
    # STATE COLOR
    # =========================================================

    def state_color(
        self,
    ):

        return {
            "ERROR": QColor(
                "#ff4d6d"
            ),
            "THINKING": QColor(
                "#b98cff"
            ),
            "SPEAKING": QColor(
                "#7df9ff"
            ),
            "LISTENING": QColor(
                "#55f5bd"
            ),
        }.get(
            self.state,
            self.accent,
        )

    # =========================================================
    # COLOR MIX
    # =========================================================

    def mix(
        self,
        left,
        right,
        amount,
    ):

        amount = max(
            0.0,
            min(
                1.0,
                amount,
            ),
        )

        return QColor(
            int(
                left.red()
                * (1 - amount)
                + right.red()
                * amount
            ),
            int(
                left.green()
                * (1 - amount)
                + right.green()
                * amount
            ),
            int(
                left.blue()
                * (1 - amount)
                + right.blue()
                * amount
            ),
            int(
                left.alpha()
                * (1 - amount)
                + right.alpha()
                * amount
            ),
        )

    # =========================================================
    # ELLIPSE HELPER
    # =========================================================

    @staticmethod
    def ellipse_rect(
        cx,
        cy,
        rx,
        ry,
    ):

        return (
            int(
                cx - rx
            ),
            int(
                cy - ry
            ),
            int(
                rx * 2
            ),
            int(
                ry * 2
            ),
        )

    # =========================================================
    # GLOW
    # =========================================================

    def glow(
        self,
        painter,
        cx,
        cy,
        radius,
        color,
        alpha=90,
    ):

        gradient = QRadialGradient(
            cx,
            cy,
            radius,
        )

        center = QColor(
            color
        )

        center.setAlpha(
            alpha
        )

        edge = QColor(
            color
        )

        edge.setAlpha(
            0
        )

        gradient.setColorAt(
            0.0,
            center,
        )

        gradient.setColorAt(
            0.45,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                int(
                    alpha * 0.35
                ),
            ),
        )

        gradient.setColorAt(
            1.0,
            edge,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawEllipse(
            *self.ellipse_rect(
                cx,
                cy,
                radius,
                radius,
            )
        )

    # =========================================================
    # MAIN PAINT
    # =========================================================

    def paintEvent(
        self,
        event,
    ):

        del event

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform,
            True,
        )

        width = self.width()
        height = self.height()

        # Center the artwork in the large transparent canvas.
        # The artwork does NOT scale from the widget size, so making
        # the canvas larger never shrinks the orb.
        cx = width / 2.0
        cy = height / 2.0

        art_size = 340.0

        outer = (
            art_size * 0.46
        )

        orb = (
            art_size * 0.245
        )

        color = (
            self.state_color()
        )

        dim = self.mix(
            color,
            self.background,
            0.45,
        )

        self.draw_background(
            painter,
            cx,
            cy,
            outer,
            color,
        )

        self.draw_particles(
            painter,
            cx,
            cy,
            outer,
            color,
        )

        self.draw_hud_rings(
            painter,
            cx,
            cy,
            outer,
            color,
        )

        self.draw_orbitals(
            painter,
            cx,
            cy,
            outer,
            color,
        )

        self.draw_core(
            painter,
            cx,
            cy,
            orb,
            color,
        )

        self.draw_scanline(
            painter,
            cx,
            cy,
            orb,
            color,
        )

        self.draw_status(
            painter,
            cx,
            cy,
            outer,
            dim,
        )

        painter.end()

    # =========================================================
    # BACKGROUND
    # =========================================================

    def draw_background(
        self,
        painter,
        cx,
        cy,
        outer,
        color,
    ):

        painter.setPen(
            Qt.NoPen
        )

        gradient = QRadialGradient(
            cx,
            cy,
            outer * 1.5,
        )

        gradient.setColorAt(
            0.0,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                24,
            ),
        )

        gradient.setColorAt(
            0.42,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                7,
            ),
        )

        gradient.setColorAt(
            1.0,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                0,
            ),
        )

        painter.setBrush(
            gradient
        )

        painter.drawEllipse(
            *self.ellipse_rect(
                cx,
                cy,
                outer * 1.42,
                outer * 1.42,
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    28,
                ),
                1,
            )
        )

        for radius in (
            outer * 0.92,
            outer * 1.03,
            outer * 1.13,
        ):

            painter.drawEllipse(
                *self.ellipse_rect(
                    cx,
                    cy,
                    radius,
                    radius * 0.98,
                )
            )

    # =========================================================
    # PARTICLES
    # =========================================================

    def draw_particles(
        self,
        painter,
        cx,
        cy,
        outer,
        color,
    ):

        state_boost = {
            "IDLE": 0.0,
            "LISTENING": 0.14,
            "THINKING": 0.25,
            "SPEAKING": 0.20,
            "ERROR": 0.3,
        }.get(
            self.state,
            0.0,
        )

        painter.setPen(
            Qt.NoPen
        )

        for particle in self.particles:

            angle = (
                particle["angle"]
                + self.phase * 0.008
            )

            radius = (
                outer
                * (
                    particle["radius"]
                    + math.sin(
                        self.phase
                        + particle["phase"]
                    )
                    * 0.012
                )
            )

            x = (
                cx
                + math.cos(angle)
                * radius
            )

            y = (
                cy
                + math.sin(angle)
                * radius
                * 0.78
            )

            twinkle = (
                0.5
                + 0.5
                * math.sin(
                    self.phase * 1.7
                    + particle["phase"]
                )
            )

            alpha = int(
                min(
                    255,
                    particle["alpha"]
                    * (
                        0.55
                        + twinkle * 0.55
                        + state_boost
                    ),
                )
            )

            dot = QColor(
                color
            )

            dot.setAlpha(
                alpha
            )

            painter.setBrush(
                dot
            )

            radius = (
                particle["size"]
                * (
                    0.8
                    + twinkle * 0.45
                )
            )

            painter.drawEllipse(
                *self.ellipse_rect(
                    x,
                    y,
                    radius,
                    radius,
                )
            )

    # =========================================================
    # HUD RINGS
    # =========================================================

    def draw_hud_rings(
        self,
        painter,
        cx,
        cy,
        outer,
        color,
    ):

        painter.save()

        painter.translate(
            cx,
            cy,
        )

        painter.rotate(
            math.degrees(
                self.rotation
            )
        )

        for index, radius in enumerate(
            (
                outer * 0.98,
                outer * 0.90,
                outer * 0.80,
            )
        ):

            ring_color = QColor(
                color
            )

            ring_color.setAlpha(
                105
                - index * 18
            )

            painter.setPen(
                QPen(
                    ring_color,
                    2 if index == 0 else 1,
                )
            )

            painter.setBrush(
                Qt.NoBrush
            )

            rect = (
                self.ellipse_rect(
                    0,
                    0,
                    radius,
                    radius
                    * (
                        0.64
                        if index == 0
                        else 0.72
                    ),
                )
            )

            start = int(
                (
                    self.phase * 70
                    + index * 110
                )
                * 16
            )

            span = int(
                (
                    95
                    - index * 12
                )
                * 16
            )

            painter.drawArc(
                *rect,
                start,
                span,
            )

            painter.drawArc(
                *rect,
                start + 145 * 16,
                span // 2,
            )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    90,
                ),
                2,
            )
        )

        for index in range(
            36
        ):

            angle = (
                math.tau
                * index
                / 36.0
            )

            inner = (
                outer * 0.88
                if index % 3 == 0
                else outer * 0.92
            )

            length = (
                outer * 0.03
                if index % 3 == 0
                else outer * 0.015
            )

            x1 = (
                math.cos(angle)
                * inner
            )

            y1 = (
                math.sin(angle)
                * inner
                * 0.74
            )

            x2 = (
                math.cos(angle)
                * (
                    inner + length
                )
            )

            y2 = (
                math.sin(angle)
                * (
                    inner + length
                )
                * 0.74
            )

            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2),
            )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    155,
                ),
                3,
            )
        )

        for offset in (
            0,
            120,
            240,
        ):

            radius = (
                outer * 0.72
            )

            rect = (
                self.ellipse_rect(
                    0,
                    0,
                    radius,
                    radius * 0.48,
                )
            )

            start = int(
                (
                    self.phase * 42
                    + offset
                )
                * 16
            )

            painter.drawArc(
                *rect,
                start,
                42 * 16,
            )

        painter.restore()

    # =========================================================
    # ORBITS
    # =========================================================

    def draw_orbitals(
        self,
        painter,
        cx,
        cy,
        outer,
        color,
    ):

        painter.save()

        painter.translate(
            cx,
            cy,
        )

        orbital_colors = [
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                150,
            ),
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                105,
            ),
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                75,
            ),
        ]

        sizes = [
            (
                outer * 0.66,
                outer * 0.25,
            ),
            (
                outer * 0.59,
                outer * 0.34,
            ),
            (
                outer * 0.48,
                outer * 0.40,
            ),
        ]

        for index, (
            size_pair,
            pen_color,
        ) in enumerate(
            zip(
                sizes,
                orbital_colors,
            )
        ):

            rx, ry = size_pair

            painter.save()

            painter.rotate(
                math.degrees(
                    self.rotation
                    * (
                        1.0
                        if index != 1
                        else -0.7
                    )
                )
                + index * 31
            )

            painter.setPen(
                QPen(
                    pen_color,
                    2 if index == 0 else 1,
                )
            )

            painter.setBrush(
                Qt.NoBrush
            )

            painter.drawEllipse(
                *self.ellipse_rect(
                    0,
                    0,
                    rx,
                    ry,
                )
            )

            node_angle = (
                self.phase
                * (
                    0.8
                    + index * 0.27
                )
                + index * 2.0
            )

            nx = (
                math.cos(node_angle)
                * rx
            )

            ny = (
                math.sin(node_angle)
                * ry
            )

            self.glow(
                painter,
                nx,
                ny,
                18 + index * 2,
                color,
                35,
            )

            painter.setPen(
                Qt.NoPen
            )

            node = QColor(
                color
            )

            node.setAlpha(
                220
            )

            painter.setBrush(
                node
            )

            painter.drawEllipse(
                *self.ellipse_rect(
                    nx,
                    ny,
                    3.0,
                    3.0,
                )
            )

            painter.restore()

        painter.restore()

    # =========================================================
    # CORE
    # =========================================================

    def draw_core(
        self,
        painter,
        cx,
        cy,
        radius,
        color,
    ):

        pulse_strength = {
            "IDLE": 0.025,
            "LISTENING": 0.10,
            "THINKING": 0.06,
            "SPEAKING": 0.13,
            "ERROR": 0.12,
        }.get(
            self.state,
            0.04,
        )

        radius *= (
            1.0
            + math.sin(
                self.pulse
            )
            * pulse_strength
        )

        self.glow(
            painter,
            cx,
            cy,
            radius * 2.1,
            color,
            100,
        )

        self.glow(
            painter,
            cx,
            cy,
            radius * 1.55,
            color,
            120,
        )

        # GLASS SPHERE

        glass = QRadialGradient(
            cx - radius * 0.35,
            cy - radius * 0.42,
            radius * 1.4,
        )

        glass.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                120,
            ),
        )

        glass.setColorAt(
            0.14,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                155,
            ),
        )

        glass.setColorAt(
            0.56,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                75,
            ),
        )

        glass.setColorAt(
            1.0,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                15,
            ),
        )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    220,
                ),
                2,
            )
        )

        painter.setBrush(
            glass
        )

        painter.drawEllipse(
            *self.ellipse_rect(
                cx,
                cy,
                radius,
                radius,
            )
        )

        # WIREFRAME

        wire = QColor(
            color
        )

        wire.setAlpha(
            85
        )

        painter.setPen(
            QPen(
                wire,
                1,
            )
        )

        painter.setBrush(
            Qt.NoBrush
        )

        for squash in (
            0.22,
            0.45,
            0.68,
        ):

            painter.drawEllipse(
                *self.ellipse_rect(
                    cx,
                    cy,
                    radius,
                    radius * squash,
                )
            )

        for width_factor in (
            0.36,
            0.62,
            0.84,
        ):

            painter.drawEllipse(
                *self.ellipse_rect(
                    cx,
                    cy,
                    radius * width_factor,
                    radius,
                )
            )

        # ENERGY LENS

        lens_radius = (
            radius
            * 0.42
            * (
                1.0
                + 0.05
                * math.sin(
                    self.phase * 2.0
                )
            )
        )

        lens_gradient = QConicalGradient(
            cx,
            cy,
            math.degrees(
                self.rotation
            ),
        )

        lens_gradient.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                230,
            ),
        )

        lens_gradient.setColorAt(
            0.18,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                235,
            ),
        )

        lens_gradient.setColorAt(
            0.55,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                75,
            ),
        )

        lens_gradient.setColorAt(
            1.0,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                230,
            ),
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            lens_gradient
        )

        painter.drawEllipse(
            *self.ellipse_rect(
                cx,
                cy,
                lens_radius,
                lens_radius,
            )
        )

        # HEX CORE

        points = []

        core_radius = (
            radius * 0.20
        )

        for index in range(
            6
        ):

            angle = (
                math.radians(
                    30
                    + index * 60
                )
                + self.rotation * 0.8
            )

            points.append(
                (
                    cx
                    + math.cos(angle)
                    * core_radius,
                    cy
                    + math.sin(angle)
                    * core_radius,
                )
            )

        path = QPainterPath()

        path.moveTo(
            points[0][0],
            points[0][1],
        )

        for x, y in points[1:]:

            path.lineTo(
                x,
                y,
            )

        path.closeSubpath()

        core_fill = QRadialGradient(
            cx,
            cy,
            core_radius,
        )

        core_fill.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                245,
            ),
        )

        core_fill.setColorAt(
            0.25,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                250,
            ),
        )

        core_fill.setColorAt(
            1.0,
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                50,
            ),
        )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    230,
                ),
                1.5,
            )
        )

        painter.setBrush(
            core_fill
        )

        painter.drawPath(
            path
        )

        # ENERGY SPOKES

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    155,
                ),
                1,
            )
        )

        spoke_count = (
            16
            if self.state
            in {
                "LISTENING",
                "SPEAKING",
                "THINKING",
            }
            else 10
        )

        for index in range(
            spoke_count
        ):

            angle = (
                self.rotation * 1.8
                + math.tau
                * index
                / spoke_count
            )

            inner = (
                radius * 0.53
            )

            outer_length = (
                radius
                * (
                    0.74
                    + 0.07
                    * math.sin(
                        self.phase * 2.1
                        + index
                    )
                )
            )

            x1 = (
                cx
                + math.cos(angle)
                * inner
            )

            y1 = (
                cy
                + math.sin(angle)
                * inner
            )

            x2 = (
                cx
                + math.cos(angle)
                * outer_length
            )

            y2 = (
                cy
                + math.sin(angle)
                * outer_length
            )

            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2),
            )

    # =========================================================
    # SCAN
    # =========================================================

    def draw_scanline(
        self,
        painter,
        cx,
        cy,
        radius,
        color,
    ):

        angle = (
            self.scan
            * math.tau
        )

        x = (
            cx
            + math.cos(angle)
            * radius
            * 0.88
        )

        y = (
            cy
            + math.sin(angle)
            * radius
            * 0.88
        )

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    170,
                ),
                1,
            )
        )

        painter.drawLine(
            int(cx),
            int(cy),
            int(x),
            int(y),
        )

        painter.setPen(
            QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    70,
                ),
                1,
            )
        )

        painter.setBrush(
            Qt.NoBrush
        )

        sweep_rect = (
            self.ellipse_rect(
                cx,
                cy,
                radius * 0.86,
                radius * 0.86,
            )
        )

        painter.drawArc(
            *sweep_rect,
            int(
                self.scan
                * 360
                * 16
            ),
            40 * 16,
        )

    # =========================================================
    # STATUS
    # =========================================================

    def draw_status(
        self,
        painter,
        cx,
        cy,
        outer,
        dim,
    ):

        font = QFont(
            "Segoe UI"
        )

        font.setPointSize(
            9
        )

        font.setBold(
            True
        )

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(
                dim.red(),
                dim.green(),
                dim.blue(),
                160,
            )
        )

        painter.drawText(
            int(
                cx - outer
            ),
            int(
                cy + outer * 0.98
            ),
            int(
                outer * 2
            ),
            28,
            Qt.AlignCenter,
            f"JARVIS CORE  •  {self.state}",
        )