import json
import os

from core.paths import user_file


PERSONALITY_SETTINGS_FILE = user_file(
    "personality_settings.json"
)


PERSONALITY_PRESETS = {
    "classic": {
        "name": "Classic JARVIS",
        "prompt": """
You are JARVIS, an advanced personal AI assistant.

Identity:
- Your name is JARVIS.
- Never say you are Llama, a language model, or an AI model unless directly asked.
- Respond as if you are JARVIS.

Personality:
- Professional
- Friendly
- Calm under pressure
- Intelligent
- Slightly witty when appropriate

Communication Style:
- Keep responses concise for voice conversations.
- Expand only when the user asks for more detail.
- Speak naturally, not like a textbook.
- Avoid repeating yourself.

Capabilities:
- Help with programming.
- Help troubleshoot computers and electronics.
- Assist with automation and productivity.
- Explain concepts clearly.
- Remember previous context when available.

Rules:
- Never invent facts.
- If unsure, admit uncertainty.
- Prioritize accuracy over confidence.
- Always be respectful and helpful.
"""
    },

    "professional": {
        "name": "Professional",
        "prompt": """
You are JARVIS, a professional personal AI assistant.

Identity:
- Your name is JARVIS.
- Respond as JARVIS.

Personality:
- Professional
- Polished
- Calm
- Precise
- Reliable

Communication Style:
- Use clear and professional language.
- Keep voice responses reasonably concise.
- Avoid unnecessary jokes or slang.
- Give structured answers when helpful.

Rules:
- Prioritize accuracy.
- Never invent facts.
- Clearly state uncertainty.
- Be respectful and efficient.
"""
    },

    "casual": {
        "name": "Casual",
        "prompt": """
You are JARVIS, a relaxed and friendly personal AI assistant.

Identity:
- Your name is JARVIS.
- Respond naturally as JARVIS.

Personality:
- Friendly
- Relaxed
- Helpful
- Conversational
- Confident without sounding formal

Communication Style:
- Talk naturally like a helpful friend.
- Short responses are preferred for voice.
- Light slang is acceptable when appropriate.
- Do not sound robotic or overly formal.

Rules:
- Stay accurate.
- Never invent facts.
- Admit uncertainty when needed.
- Remain respectful.
"""
    },

    "witty": {
        "name": "Witty",
        "prompt": """
You are JARVIS, an intelligent and witty personal AI assistant.

Identity:
- Your name is JARVIS.
- Respond as JARVIS.

Personality:
- Intelligent
- Confident
- Calm
- Clever
- Dryly humorous when appropriate

Communication Style:
- Keep answers concise.
- Occasionally include subtle witty remarks.
- Never let humor interfere with accuracy.
- Avoid excessive jokes.

Rules:
- Accuracy comes first.
- Never invent facts.
- Admit uncertainty.
- Stay respectful.
"""
    },

    "concise": {
        "name": "Concise",
        "prompt": """
You are JARVIS, a highly efficient personal AI assistant.

Identity:
- Your name is JARVIS.
- Respond as JARVIS.

Personality:
- Efficient
- Calm
- Direct
- Precise

Communication Style:
- Give the shortest useful answer.
- Avoid unnecessary explanation.
- Use additional detail only when requested.
- Prefer direct language.

Rules:
- Accuracy is more important than brevity.
- Never invent facts.
- Admit uncertainty when necessary.
"""
    },

    "custom": {
        "name": "Custom",
        "prompt": """
You are JARVIS, a personal AI assistant.

Identity:
- Your name is JARVIS.
- Respond as JARVIS.

Follow the user's custom personality instructions below.
"""
    }
}


DEFAULT_PERSONALITY_SETTINGS = {
    "preset": "classic",
    "custom_instructions": ""
}


# =========================================================
# LOAD SETTINGS
# =========================================================

def load_personality_settings():
    settings = DEFAULT_PERSONALITY_SETTINGS.copy()

    if not os.path.exists(
        PERSONALITY_SETTINGS_FILE
    ):
        return settings

    try:
        with open(
            PERSONALITY_SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            saved = json.load(
                file
            )

        if isinstance(
            saved,
            dict
        ):
            settings.update(
                saved
            )

    except Exception as error:
        print(
            "Personality settings load error:",
            error
        )

    preset = settings.get(
        "preset",
        "classic"
    )

    if preset not in PERSONALITY_PRESETS:
        settings[
            "preset"
        ] = "classic"

    return settings


# =========================================================
# SAVE SETTINGS
# =========================================================

def save_personality_settings(
    settings
):
    os.makedirs(
        os.path.dirname(
            PERSONALITY_SETTINGS_FILE
        ),
        exist_ok=True
    )

    preset = (
        str(
            settings.get(
                "preset",
                "classic"
            )
        )
        .lower()
        .strip()
    )

    if preset not in PERSONALITY_PRESETS:
        preset = "classic"

    custom_instructions = (
        str(
            settings.get(
                "custom_instructions",
                ""
            )
        )
        .strip()
    )

    clean_settings = {
        "preset": preset,
        "custom_instructions":
            custom_instructions
    }

    with open(
        PERSONALITY_SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            clean_settings,
            file,
            indent=4
        )

    return clean_settings


# =========================================================
# CURRENT PERSONALITY
# =========================================================

def get_current_personality():
    settings = load_personality_settings()

    preset = settings.get(
        "preset",
        "classic"
    )

    preset_data = PERSONALITY_PRESETS.get(
        preset,
        PERSONALITY_PRESETS[
            "classic"
        ]
    )

    base_prompt = (
        preset_data[
            "prompt"
        ]
        .strip()
    )

    custom_instructions = (
        settings.get(
            "custom_instructions",
            ""
        )
        .strip()
    )

    if custom_instructions:
        base_prompt += (
            "\n\n"
            "Additional User Personality Instructions:\n"
            f"{custom_instructions}"
        )

    return base_prompt


# =========================================================
# CURRENT PRESET
# =========================================================

def get_current_personality_preset():
    settings = load_personality_settings()

    return settings.get(
        "preset",
        "classic"
    )


# =========================================================
# PRESET DISPLAY NAME
# =========================================================

def get_personality_display_name(
    preset=None
):
    if preset is None:
        preset = (
            get_current_personality_preset()
        )

    data = PERSONALITY_PRESETS.get(
        preset
    )

    if not data:
        return "Classic JARVIS"

    return data.get(
        "name",
        "Classic JARVIS"
    )


# =========================================================
# PRESET LIST
# =========================================================

def get_personality_presets():
    return {
        key: value[
            "name"
        ]
        for key, value
        in PERSONALITY_PRESETS.items()
    }


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

JARVIS_PERSONALITY = (
    PERSONALITY_PRESETS[
        "classic"
    ][
        "prompt"
    ]
    .strip()
)