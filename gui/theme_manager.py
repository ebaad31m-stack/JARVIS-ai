import json
import os

from core.paths import user_file


THEME_FILE = user_file(
    "theme.json"
)


DEFAULT_THEME = {
    "color_1": "#05080c",
    "color_2": "#7fe7ff"
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
            saved_theme = json.load(
                file
            )

        return {
            "color_1": saved_theme.get(
                "color_1",
                DEFAULT_THEME[
                    "color_1"
                ]
            ),

            "color_2": saved_theme.get(
                "color_2",
                DEFAULT_THEME[
                    "color_2"
                ]
            )
        }

    except Exception as error:
        print(
            "Theme load error:",
            error
        )

        return DEFAULT_THEME.copy()