import os
import re

from PIL import (
    ImageEnhance,
    ImageOps,
)

import pytesseract

from pytesseract import Output

from core.overlay_manager import (
    highlight_area,
)

from core.screen_settings import (
    capture_selected_screen,
)


DEFAULT_TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# TESSERACT
# =========================================================

def configure_tesseract():
    if os.path.exists(
        DEFAULT_TESSERACT_PATH
    ):
        pytesseract.pytesseract.tesseract_cmd = (
            DEFAULT_TESSERACT_PATH
        )


configure_tesseract()


# =========================================================
# PREPROCESS
# =========================================================

def preprocess_image(
    image
):
    if image is None:
        return None

    try:
        image = image.convert(
            "L"
        )

        image = ImageOps.autocontrast(
            image
        )

        enhancer = ImageEnhance.Contrast(
            image
        )

        return enhancer.enhance(
            1.4
        )

    except Exception as error:
        print(
            "Screen preprocessing error:",
            error
        )

        return image


# =========================================================
# READ TEXT
# =========================================================

def read_screen_text():
    screenshot, geometry = (
        capture_selected_screen()
    )

    if screenshot is None:
        return ""

    processed = preprocess_image(
        screenshot
    )

    try:
        text = pytesseract.image_to_string(
            processed,
            lang="eng",
            config="--psm 6",
        )

        return clean_ocr_text(
            text
        )

    except Exception as error:
        print(
            "Screen OCR error:",
            error
        )

        return ""


# =========================================================
# OCR DATA + REAL SCREEN COORDINATES
# =========================================================

def read_screen_data():
    screenshot, geometry = (
        capture_selected_screen()
    )

    if screenshot is None:
        return []

    processed = preprocess_image(
        screenshot
    )

    try:
        data = pytesseract.image_to_data(
            processed,
            lang="eng",
            config="--psm 6",
            output_type=Output.DICT,
        )

    except Exception as error:
        print(
            "Screen OCR data error:",
            error
        )

        return []

    results = []

    x_offset = geometry.get(
        "x",
        0,
    )

    y_offset = geometry.get(
        "y",
        0,
    )

    count = len(
        data.get(
            "text",
            []
        )
    )

    for index in range(
        count
    ):
        text = (
            str(
                data[
                    "text"
                ][
                    index
                ]
            )
            .strip()
        )

        if not text:
            continue

        try:
            confidence = float(
                data[
                    "conf"
                ][
                    index
                ]
            )

        except Exception:
            confidence = -1

        if confidence < 35:
            continue

        results.append(
            {
                "text": text,
                "confidence": confidence,

                "x":
                    int(
                        data[
                            "left"
                        ][
                            index
                        ]
                    )
                    + x_offset,

                "y":
                    int(
                        data[
                            "top"
                        ][
                            index
                        ]
                    )
                    + y_offset,

                "width":
                    int(
                        data[
                            "width"
                        ][
                            index
                        ]
                    ),

                "height":
                    int(
                        data[
                            "height"
                        ][
                            index
                        ]
                    ),
            }
        )

    return results


# =========================================================
# FIND TEXT
# =========================================================

def find_text_on_screen(
    search_text
):
    search_text = (
        str(
            search_text
        )
        .lower()
        .strip()
    )

    if not search_text:
        return None

    words = read_screen_data()

    for item in words:
        text = (
            item[
                "text"
            ]
            .lower()
        )

        if search_text in text:
            return item

    # =====================================================
    # PHRASES
    # =====================================================

    search_words = search_text.split()

    if len(
        search_words
    ) <= 1:
        return None

    for start in range(
        len(
            words
        )
    ):
        matched = []

        for offset in range(
            len(
                search_words
            )
        ):
            index = (
                start
                + offset
            )

            if index >= len(
                words
            ):
                break

            matched.append(
                words[
                    index
                ]
            )

        phrase = " ".join(
            item[
                "text"
            ].lower()
            for item in matched
        )

        if search_text in phrase:
            left = min(
                item["x"]
                for item in matched
            )

            top = min(
                item["y"]
                for item in matched
            )

            right = max(
                item["x"]
                + item["width"]
                for item in matched
            )

            bottom = max(
                item["y"]
                + item["height"]
                for item in matched
            )

            return {
                "text": search_text,
                "confidence": min(
                    item[
                        "confidence"
                    ]
                    for item in matched
                ),
                "x": left,
                "y": top,
                "width": right - left,
                "height": bottom - top,
            }

    return None


# =========================================================
# HIGHLIGHT TEXT
# =========================================================

def highlight_text_on_screen(
    search_text,
    label=None,
    duration=7000,
):
    match = find_text_on_screen(
        search_text
    )

    if match is None:
        return False

    padding = 12

    highlight_area(
        x=match[
            "x"
        ] - padding,

        y=match[
            "y"
        ] - padding,

        width=(
            match[
                "width"
            ]
            + padding * 2
        ),

        height=(
            match[
                "height"
            ]
            + padding * 2
        ),

        text=(
            label
            or f"Found: {search_text}"
        ),

        duration=duration,
    )

    return True


# =========================================================
# FIND ERROR
# =========================================================

def find_error_on_screen():
    terms = (
        "error",
        "failed",
        "failure",
        "exception",
        "traceback",
        "warning",
        "invalid",
        "denied",
        "not found",
        "missing",
        "unable",
        "cannot",
    )

    words = read_screen_data()

    for item in words:
        text = (
            item[
                "text"
            ]
            .lower()
        )

        for term in terms:
            if term in text:
                return item

    return None


def highlight_error_on_screen(
    duration=7000
):
    match = find_error_on_screen()

    if match is None:
        return False

    highlight_area(
        x=match[
            "x"
        ] - 20,

        y=match[
            "y"
        ] - 20,

        width=(
            match[
                "width"
            ]
            + 240
        ),

        height=(
            match[
                "height"
            ]
            + 90
        ),

        text="Possible error detected",

        duration=duration,
    )

    return True


# =========================================================
# CLEAN TEXT
# =========================================================

def summarize_screen_text(
    text,
    max_characters=900,
):
    text = clean_ocr_text(
        text
    )

    if len(
        text
    ) <= max_characters:
        return text

    return (
        text[
            :max_characters
        ]
        + "..."
    )


def clean_ocr_text(
    text
):
    text = str(
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()