from __future__ import annotations

import ctypes
import os
import re
import winreg
from typing import Optional

from core.wallpaper_manager import (
    set_wallpaper_from_topic,
)


# =========================================================
# WINDOWS PERSONALIZATION
# =========================================================

PERSONALIZE_KEY = (
    r"Software\Microsoft\Windows"
    r"\CurrentVersion\Themes\Personalize"
)


# =========================================================
# WINDOWS SETTINGS PAGES
# =========================================================

SETTINGS_PAGES = {
    "display": "ms-settings:display",
    "sound": "ms-settings:sound",
    "audio": "ms-settings:sound",
    "bluetooth": "ms-settings:bluetooth",
    "wifi": "ms-settings:network-wifi",
    "wi-fi": "ms-settings:network-wifi",
    "network": "ms-settings:network",
    "wallpaper": "ms-settings:personalization-background",
    "background": "ms-settings:personalization-background",
    "personalization": "ms-settings:personalization",
    "theme": "ms-settings:themes",
    "themes": "ms-settings:themes",
    "color": "ms-settings:colors",
    "colors": "ms-settings:colors",
    "notifications": "ms-settings:notifications",
    "startup": "ms-settings:startupapps",
    "power": "ms-settings:powersleep",
    "battery": "ms-settings:batterysaver",
    "storage": "ms-settings:storagesense",
    "mouse": "ms-settings:mousetouchpad",
    "keyboard": "ms-settings:typing",
    "apps": "ms-settings:appsfeatures",
    "default apps": "ms-settings:defaultapps",
    "privacy": "ms-settings:privacy",
    "windows update": "ms-settings:windowsupdate",
}


# =========================================================
# WINDOWS REFRESH
# =========================================================

def _broadcast_settings_change() -> None:
    """
    Tell Windows that personalization settings changed.
    """

    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002

    result = ctypes.c_ulong()

    try:
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "ImmersiveColorSet",
            SMTO_ABORTIFHUNG,
            1000,
            ctypes.byref(result),
        )

    except Exception:
        pass


# =========================================================
# REGISTRY PERSONALIZATION HELPER
# =========================================================

def _write_personalize_dword(
    name: str,
    value: int,
) -> None:

    with winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER,
        PERSONALIZE_KEY,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:

        winreg.SetValueEx(
            key,
            name,
            0,
            winreg.REG_DWORD,
            int(value),
        )

    _broadcast_settings_change()


# =========================================================
# DARK / LIGHT MODE
# =========================================================

def set_dark_mode(
    enabled: bool,
) -> str:

    light_value = (
        0
        if enabled
        else 1
    )

    _write_personalize_dword(
        "AppsUseLightTheme",
        light_value,
    )

    _write_personalize_dword(
        "SystemUsesLightTheme",
        light_value,
    )

    if enabled:
        return (
            "Done. Windows is now using dark mode."
        )

    return (
        "Done. Windows is now using light mode."
    )


# =========================================================
# TRANSPARENCY
# =========================================================

def set_transparency(
    enabled: bool,
) -> str:

    _write_personalize_dword(
        "EnableTransparency",
        1 if enabled else 0,
    )

    if enabled:
        return (
            "Transparency effects are on."
        )

    return (
        "Transparency effects are off."
    )


# =========================================================
# OPEN WINDOWS SETTINGS
# =========================================================

def open_settings_page(
    category: str,
) -> str:

    clean_category = (
        category
        .lower()
        .strip()
    )

    uri = SETTINGS_PAGES.get(
        clean_category
    )

    try:

        if uri:
            os.startfile(
                uri
            )

            return (
                f"I opened {clean_category} settings."
            )

        os.startfile(
            "ms-settings:"
        )

        return (
            "I opened Windows Settings."
        )

    except Exception as error:

        return (
            "I couldn't open that settings page: "
            f"{error}"
        )


# =========================================================
# WALLPAPER TOPIC EXTRACTION
# =========================================================

def _extract_wallpaper_topic(
    command: str,
) -> str:

    text = (
        command
        .lower()
        .strip()
    )

    topic = ""

    if " to " in text:
        topic = text.split(
            " to ",
            1,
        )[1]

    elif " as " in text:
        topic = text.split(
            " as ",
            1,
        )[1]

    elif " wallpaper" in text:
        topic = text.split(
            " wallpaper",
            1,
        )[0]

    elif " background" in text:
        topic = text.split(
            " background",
            1,
        )[0]

    else:
        topic = text


    # Remove common command words.
    topic = re.sub(
        r"^(set|change|make|give me|put|use)\s+",
        "",
        topic,
    )

    topic = re.sub(
        r"^(my|the|a|an|some)\s+",
        "",
        topic,
    )

    topic = re.sub(
        r"\b(my|the)\b\s*",
        "",
        topic,
    )

    topic = re.sub(
        r"\b(wallpaper|background|image|picture)\b",
        "",
        topic,
    )

    topic = re.sub(
        r"\s+",
        " ",
        topic,
    ).strip()

    if not topic:
        topic = "nature"

    return topic


# =========================================================
# WALLPAPER COMMAND CHECK
# =========================================================

def _is_wallpaper_change(
    text: str,
) -> bool:

    has_target = any(
        word in text
        for word in (
            "wallpaper",
            "background",
        )
    )

    has_action = any(
        phrase in text
        for phrase in (
            "set ",
            "change ",
            "make ",
            "give me ",
            "put ",
            "use ",
        )
    )

    return (
        has_target
        and has_action
    )


# =========================================================
# SETTINGS HELP
# =========================================================

def _settings_help() -> str:

    return (
        "I can change your wallpaper, "
        "switch between dark and light mode, "
        "toggle transparency effects, "
        "and open Windows Settings pages "
        "like display, Bluetooth, sound, "
        "notifications, startup apps, and more."
    )


# =========================================================
# MAIN SETTINGS ROUTER
# =========================================================

def handle_settings_command(
    command: str,
) -> Optional[str]:

    if not command:
        return None

    text = (
        str(command)
        .lower()
        .strip()
    )

    if not text:
        return None


    # -----------------------------------------------------
    # REMOVE JARVIS PREFIX
    # -----------------------------------------------------

    text = re.sub(
        r"^(hey\s+jarvis|jarvis)[,\s]+",
        "",
        text,
    ).strip()


    # =====================================================
    # SETTINGS CAPABILITIES
    # =====================================================

    capability_phrases = (
        "what settings can you change",
        "what windows settings can you change",
        "what can you change in settings",
        "what system settings can you change",
        "what settings do you control",
    )

    if any(
        phrase in text
        for phrase in capability_phrases
    ):
        return _settings_help()


    # =====================================================
    # WALLPAPER
    # =====================================================

    if _is_wallpaper_change(
        text
    ):

        # If the user specifically asks to open
        # background settings, do that instead.
        if (
            "open" in text
            and "settings" in text
        ):
            return open_settings_page(
                "background"
            )

        topic = _extract_wallpaper_topic(
            text
        )

        result = set_wallpaper_from_topic(
            topic
        )

        return result.get(
            "message",
            "Wallpaper command completed.",
        )


    # =====================================================
    # DARK MODE
    # =====================================================

    if any(
        phrase in text
        for phrase in (
            "dark mode",
            "dark theme",
            "make windows dark",
            "make everything dark",
        )
    ):

        if any(
            phrase in text
            for phrase in (
                "turn off dark mode",
                "disable dark mode",
                "stop dark mode",
            )
        ):
            return set_dark_mode(
                False
            )

        return set_dark_mode(
            True
        )


    # =====================================================
    # LIGHT MODE
    # =====================================================

    if any(
        phrase in text
        for phrase in (
            "light mode",
            "light theme",
            "make windows light",
            "make everything light",
        )
    ):

        return set_dark_mode(
            False
        )


    # =====================================================
    # TRANSPARENCY
    # =====================================================

    if any(
        phrase in text
        for phrase in (
            "transparency",
            "transparent effects",
            "transparency effects",
        )
    ):

        if any(
            phrase in text
            for phrase in (
                "off",
                "turn off",
                "disable",
            )
        ):
            return set_transparency(
                False
            )

        if any(
            phrase in text
            for phrase in (
                "on",
                "turn on",
                "enable",
            )
        ):
            return set_transparency(
                True
            )


    # =====================================================
    # OPEN SETTINGS PAGE
    # =====================================================

    settings_phrases = (
        "open settings",
        "open the settings",
        "settings for",
        "go to settings",
        "take me to settings",
        "show settings",
    )

    wants_settings = any(
        phrase in text
        for phrase in settings_phrases
    )

    if (
        wants_settings
        or text.endswith(
            " settings"
        )
    ):

        categories = sorted(
            SETTINGS_PAGES.keys(),
            key=len,
            reverse=True,
        )

        for category in categories:

            if category in text:
                return open_settings_page(
                    category
                )

        return open_settings_page(
            ""
        )


    # =====================================================
    # NATURAL SETTINGS REQUESTS
    # =====================================================

    for category in sorted(
        SETTINGS_PAGES.keys(),
        key=len,
        reverse=True,
    ):

        if (
            category in text
            and any(
                word in text
                for word in (
                    "open",
                    "show",
                    "settings",
                    "change",
                )
            )
        ):

            return open_settings_page(
                category
            )


    # =====================================================
    # NOT A SETTINGS COMMAND
    # =====================================================

    return None