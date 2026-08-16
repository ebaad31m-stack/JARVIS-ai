import base64
import io
import json
import re
import time

import pyautogui
import requests

from core.overlay_manager import (
    clear_overlay,
    highlight_box,
)

from core.personality import (
    get_current_personality,
)

from core.screen_settings import (
    capture_selected_screen,
)


OLLAMA_CHAT_URL = (
    "http://localhost:11434/api/chat"
)

VISION_MODEL = (
    "qwen3-vl:4b"
)

VISION_CONTEXT = 8192

pending_click_target = None

PENDING_TARGET_TIMEOUT = 90


# =========================================================
# IMAGE -> BASE64
# =========================================================

def image_to_base64(
    image
):
    if image is None:
        return None

    try:
        buffer = io.BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        return base64.b64encode(
            buffer.getvalue()
        ).decode(
            "utf-8"
        )

    except Exception as error:
        print(
            "Vision image encoding error:",
            error
        )

        return None


# =========================================================
# ASK VISION
# =========================================================

def ask_vision(
    prompt,
    image=None,
    temperature=0.2,
):
    if image is None:
        image, geometry = (
            capture_selected_screen()
        )

    else:
        geometry = {
            "x": 0,
            "y": 0,
        }

    if image is None:
        return (
            "I couldn't capture the selected screen."
        )

    encoded = image_to_base64(
        image
    )

    if not encoded:
        return (
            "I couldn't prepare the screenshot."
        )

    personality = (
        get_current_personality()
    )

    system_prompt = f"""
{personality}

You are using JARVIS screen vision.

Only analyze what is visible in the screenshot.

Do not invent controls, text, windows, buttons,
errors, or objects that are not visible.

Be concise and precise.
"""

    data = {
        "model": VISION_MODEL,

        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
                "images": [
                    encoded
                ],
            },
        ],

        "stream": False,

        "keep_alive": "10m",

        "options": {
            "temperature":
                temperature,

            "num_ctx":
                VISION_CONTEXT,
        },
    }

    print(
        "Vision Model:",
        VISION_MODEL
    )

    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json=data,
            timeout=240,
        )

        if not response.ok:
            print(
                "VISION HTTP STATUS:",
                response.status_code
            )

            print(
                "VISION RESPONSE:",
                response.text
            )

        response.raise_for_status()

        result = response.json()

        return (
            result
            .get(
                "message",
                {},
            )
            .get(
                "content",
                "",
            )
            .strip()
        )

    except Exception as error:
        print(
            "VISION ERROR:",
            repr(
                error
            ),
        )

        return (
            "I couldn't use screen vision. "
            f"({error})"
        )


# =========================================================
# BASIC VISION
# =========================================================

def describe_screen():
    return ask_vision(
        """
Describe what is currently visible.

Tell me:
- what application is open
- important visible content
- errors or warnings
- anything requiring attention
"""
    )


def explain_screen_error():
    return ask_vision(
        """
Inspect the screen for any error, warning,
failure, exception, or visible problem.

Explain what it means and what I should do next.
"""
    )


def inspect_screen_question(
    question
):
    return ask_vision(
        question
    )


# =========================================================
# JSON
# =========================================================

def extract_json_object(
    text
):
    if not text:
        return None

    text = re.sub(
        r"```(?:json)?",
        "",
        str(
            text
        ),
        flags=re.IGNORECASE,
    )

    text = text.replace(
        "```",
        "",
    ).strip()

    try:
        result = json.loads(
            text
        )

        if isinstance(
            result,
            dict,
        ):
            return result

    except Exception:
        pass

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )

    if (
        start >= 0
        and end > start
    ):
        try:
            return json.loads(
                text[
                    start:
                    end + 1
                ]
            )

        except Exception:
            pass

    return None


# =========================================================
# GUI TARGET
# =========================================================

def request_gui_target(
    task
):
    screenshot, geometry = (
        capture_selected_screen()
    )

    if screenshot is None:
        return None

    screenshot_width = (
        screenshot.width
    )

    screenshot_height = (
        screenshot.height
    )

    prompt = f"""
Find ONE GUI element for this task:

{task}

Screenshot dimensions:
{screenshot_width} x {screenshot_height}

Return ONLY JSON:

{{
    "found": true,
    "label": "name",
    "reason": "short reason",
    "x1": 100,
    "y1": 100,
    "x2": 300,
    "y2": 180
}}

Coordinates must be pixel coordinates INSIDE
this screenshot.

If no reliable target exists return:

{{
    "found": false,
    "label": "",
    "reason": "reason",
    "x1": 0,
    "y1": 0,
    "x2": 0,
    "y2": 0
}}
"""

    response = ask_vision(
        prompt,
        image=screenshot,
        temperature=0.0,
    )

    print(
        "VISION TARGET RESPONSE:",
        response
    )

    target = extract_json_object(
        response
    )

    if not target:
        return None

    target[
        "_screen_x"
    ] = geometry.get(
        "x",
        0,
    )

    target[
        "_screen_y"
    ] = geometry.get(
        "y",
        0,
    )

    target[
        "_width"
    ] = screenshot_width

    target[
        "_height"
    ] = screenshot_height

    return target


# =========================================================
# VALIDATE
# =========================================================

def validate_target(
    target
):
    if not isinstance(
        target,
        dict,
    ):
        return False

    if not target.get(
        "found",
        False,
    ):
        return False

    try:
        x1 = int(
            target[
                "x1"
            ]
        )

        y1 = int(
            target[
                "y1"
            ]
        )

        x2 = int(
            target[
                "x2"
            ]
        )

        y2 = int(
            target[
                "y2"
            ]
        )

        width = int(
            target[
                "_width"
            ]
        )

        height = int(
            target[
                "_height"
            ]
        )

    except Exception:
        return False

    return (
        0 <= x1 < x2 <= width
        and
        0 <= y1 < y2 <= height
    )


# =========================================================
# CONVERT SCREENSHOT -> DESKTOP COORDINATES
# =========================================================

def convert_target_to_screen(
    target
):
    offset_x = int(
        target.get(
            "_screen_x",
            0,
        )
    )

    offset_y = int(
        target.get(
            "_screen_y",
            0,
        )
    )

    return {
        "x1":
            int(
                target[
                    "x1"
                ]
            )
            + offset_x,

        "y1":
            int(
                target[
                    "y1"
                ]
            )
            + offset_y,

        "x2":
            int(
                target[
                    "x2"
                ]
            )
            + offset_x,

        "y2":
            int(
                target[
                    "y2"
                ]
            )
            + offset_y,
    }


# =========================================================
# PENDING CLICK
# =========================================================

def set_pending_click(
    target,
    label,
):
    global pending_click_target

    pending_click_target = {
        "x": int(
            (
                target[
                    "x1"
                ]
                + target[
                    "x2"
                ]
            )
            / 2
        ),

        "y": int(
            (
                target[
                    "y1"
                ]
                + target[
                    "y2"
                ]
            )
            / 2
        ),

        "label":
            str(
                label
            ),

        "created_at":
            time.time(),
    }


def clear_pending_click():
    global pending_click_target

    pending_click_target = None


# =========================================================
# LOCATE + HIGHLIGHT
# =========================================================

def locate_and_highlight(
    target_description
):
    target = request_gui_target(
        (
            "Find the GUI element described as: "
            f"{target_description}"
        )
    )

    if not validate_target(
        target
    ):
        return (
            "I couldn't confidently locate that."
        )

    screen_target = (
        convert_target_to_screen(
            target
        )
    )

    label = (
        target.get(
            "label",
            "",
        )
        or target_description
    )

    highlight_box(
        screen_target[
            "x1"
        ] - 8,

        screen_target[
            "y1"
        ] - 8,

        screen_target[
            "x2"
        ] + 8,

        screen_target[
            "y2"
        ] + 8,

        text=label,

        duration=10000,
    )

    set_pending_click(
        screen_target,
        label,
    )

    return (
        f"I found {label} and highlighted it. "
        "Say click it if you want me to click it."
    )


# =========================================================
# WHAT SHOULD I CLICK
# =========================================================

def what_should_i_click():
    target = request_gui_target(
        """
Determine the single most appropriate GUI
element the user should click next.
"""
    )

    if not validate_target(
        target
    ):
        return (
            "I couldn't confidently determine "
            "what you should click."
        )

    screen_target = (
        convert_target_to_screen(
            target
        )
    )

    label = (
        target.get(
            "label",
            "",
        )
        or "this"
    )

    highlight_box(
        screen_target[
            "x1"
        ] - 8,

        screen_target[
            "y1"
        ] - 8,

        screen_target[
            "x2"
        ] + 8,

        screen_target[
            "y2"
        ] + 8,

        text=f"Click: {label}",

        duration=10000,
    )

    set_pending_click(
        screen_target,
        label,
    )

    return (
        f"I'd click {label}. "
        "I've highlighted it. "
        "Say click it if you want me to do it."
    )


# =========================================================
# CLICK
# =========================================================

def click_pending_target():
    global pending_click_target

    if pending_click_target is None:
        return (
            "I don't currently have a target to click."
        )

    age = (
        time.time()
        - pending_click_target[
            "created_at"
        ]
    )

    if age > PENDING_TARGET_TIMEOUT:
        pending_click_target = None

        clear_overlay()

        return (
            "That target expired. "
            "Ask me to locate it again."
        )

    x = pending_click_target[
        "x"
    ]

    y = pending_click_target[
        "y"
    ]

    label = pending_click_target.get(
        "label",
        "target",
    )

    try:
        clear_overlay()

        time.sleep(
            0.2
        )

        pyautogui.click(
            x=x,
            y=y,
        )

        pending_click_target = None

        return (
            f"Clicked {label}."
        )

    except Exception as error:
        print(
            "Vision click error:",
            error
        )

        return (
            f"I couldn't click {label}."
        )


def cancel_pending_click():
    global pending_click_target

    pending_click_target = None

    clear_overlay()

    return (
        "Cancelled."
    )