import json
import os

from PySide6.QtCore import (
    QObject,
    Signal
)

from core.paths import user_file


THEME_FILE = user_file(
    "theme.json"
)


DEFAULT_THEME = {
    "color_1": "#05080c",
    "color_2": "#7fe7ff"
}


class ThemeBus(QObject):
    theme_changed = Signal(
        dict
    )


theme_bus = ThemeBus()


def normalize_theme(
    theme
):
    theme = (
        theme
        or {}
    )

    return {
        "color_1": theme.get(
            "color_1",
            DEFAULT_THEME[
                "color_1"
            ]
        ),

        "color_2": theme.get(
            "color_2",
            DEFAULT_THEME[
                "color_2"
            ]
        )
    }


def load_theme():
    if not os.path.exists(
        THEME_FILE
    ):
        return DEFAULT_THEME.copy()

    try:
        with open(
            THEME_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return normalize_theme(
                json.load(
                    file
                )
            )

    except Exception as error:
        print(
            "Theme load error:",
            error
        )

        return DEFAULT_THEME.copy()


def save_theme(
    theme
):
    normalized = normalize_theme(
        theme
    )

    os.makedirs(
        os.path.dirname(
            THEME_FILE
        ),
        exist_ok=True
    )

    with open(
        THEME_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            normalized,
            file,
            indent=4
        )

    theme_bus.theme_changed.emit(
        normalized.copy()
    )

    return normalized


def emit_theme_preview(
    theme
):
    theme_bus.theme_changed.emit(
        normalize_theme(
            theme
        ).copy()
    )