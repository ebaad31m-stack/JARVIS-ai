from __future__ import annotations

import ctypes
import json
import re
import time
import winreg

from io import BytesIO
from pathlib import Path
from typing import Any

import requests

from PIL import (
    Image,
    ImageOps,
    ImageStat,
)

from core.paths import user_file


# =========================================================
# CONSTANTS
# =========================================================

COMMONS_API = (
    "https://commons.wikimedia.org/w/api.php"
)

HEADERS = {
    "User-Agent":
        "JARVIS-Personal-Assistant/1.0"
}

SPI_SETDESKWALLPAPER = 20

SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


# =========================================================
# STORAGE
# =========================================================

def _wallpaper_directory() -> Path:

    folder = Path(
        user_file(
            "wallpapers"
        )
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return folder


# =========================================================
# CLEAN TOPIC
# =========================================================

def _clean_topic(
    topic: str,
) -> str:

    text = (
        str(topic)
        .strip()
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"^(a|an|some|the)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s+"
        r"(wallpaper|background|picture|image)"
        r"$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    if not text:
        text = "nature"

    return text[:80]


# =========================================================
# WINDOWS WALLPAPER STYLE
# =========================================================

def _set_fill_style(
    wallpaper_path: Path,
) -> None:

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:

        # Fill
        winreg.SetValueEx(
            key,
            "WallpaperStyle",
            0,
            winreg.REG_SZ,
            "10",
        )

        winreg.SetValueEx(
            key,
            "TileWallpaper",
            0,
            winreg.REG_SZ,
            "0",
        )

        winreg.SetValueEx(
            key,
            "Wallpaper",
            0,
            winreg.REG_SZ,
            str(wallpaper_path),
        )


# =========================================================
# IMAGE VALIDATION
# =========================================================

def _image_is_too_dark(
    image: Image.Image,
) -> bool:

    preview = image.copy()

    preview.thumbnail(
        (
            256,
            256,
        )
    )

    grayscale = preview.convert(
        "L"
    )

    stats = ImageStat.Stat(
        grayscale
    )

    average_brightness = (
        stats.mean[0]
    )

    # Only reject images that are basically black.
    return average_brightness < 6


# =========================================================
# PREPARE WINDOWS-SAFE JPG
# =========================================================

def _prepare_image(
    image_bytes: bytes,
    topic: str,
) -> Path:

    if not image_bytes:

        raise RuntimeError(
            "The downloaded image was empty."
        )

    with Image.open(
        BytesIO(
            image_bytes
        )
    ) as original:

        image = ImageOps.exif_transpose(
            original
        )

        image.load()

        width, height = (
            image.size
        )

        if (
            width < 800
            or height < 450
        ):

            raise RuntimeError(
                "The image resolution was too small."
            )

        if width <= height:

            raise RuntimeError(
                "The image was not landscape."
            )

        image = image.convert(
            "RGB"
        )

        if _image_is_too_dark(
            image
        ):

            raise RuntimeError(
                "The image was almost completely black."
            )

        # Avoid absurdly huge images.
        max_width = 3840
        max_height = 2160

        if (
            width > max_width
            or height > max_height
        ):

            image.thumbnail(
                (
                    max_width,
                    max_height,
                ),
                Image.Resampling.LANCZOS,
            )

        safe_topic = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            topic,
        ).strip(
            "_"
        )

        if not safe_topic:
            safe_topic = "wallpaper"

        destination = (
            _wallpaper_directory()
            / (
                f"jarvis_{safe_topic}_"
                f"{time.time_ns()}.jpg"
            )
        )

        image.save(
            destination,
            format="JPEG",
            quality=92,
            optimize=True,
        )

    return destination


# =========================================================
# APPLY WALLPAPER
# =========================================================

def set_wallpaper_file(
    wallpaper_path: str | Path,
) -> bool:

    path = Path(
        wallpaper_path
    ).resolve()

    if not path.exists():

        raise FileNotFoundError(
            f"Wallpaper does not exist: {path}"
        )

    _set_fill_style(
        path
    )

    user32 = ctypes.WinDLL(
        "user32",
        use_last_error=True,
    )

    user32.SystemParametersInfoW.argtypes = [
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_wchar_p,
        ctypes.c_uint,
    ]

    user32.SystemParametersInfoW.restype = (
        ctypes.c_bool
    )

    ctypes.set_last_error(
        0
    )

    result = (
        user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            str(path),
            (
                SPIF_UPDATEINIFILE
                | SPIF_SENDCHANGE
            ),
        )
    )

    if not result:

        error_code = (
            ctypes.get_last_error()
        )

        raise OSError(
            error_code,
            "Windows rejected the wallpaper.",
        )

    return True


# =========================================================
# SEARCH WIKIMEDIA COMMONS
# =========================================================

def _search_commons(
    topic: str,
) -> list[dict[str, Any]]:

    search_topic = (
        f"{topic} landscape photograph"
    )

    params = {
        "action":
            "query",

        "format":
            "json",

        "generator":
            "search",

        "gsrsearch":
            search_topic,

        "gsrnamespace":
            "6",

        "gsrlimit":
            "25",

        "prop":
            "imageinfo",

        "iiprop":
            "url|size|mime",

        "iiurlwidth":
            "2560",
    }

    response = requests.get(
        COMMONS_API,
        params=params,
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    pages = (
        data
        .get(
            "query",
            {},
        )
        .get(
            "pages",
            {},
        )
    )

    candidates = []

    for page in pages.values():

        info_list = (
            page.get(
                "imageinfo",
                [],
            )
        )

        if not info_list:
            continue

        info = info_list[0]

        mime = str(
            info.get(
                "mime",
                "",
            )
        ).lower()

        if mime not in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }:
            continue

        url = (
            info.get(
                "thumburl"
            )
            or info.get(
                "url"
            )
        )

        if not url:
            continue

        width = int(
            info.get(
                "thumbwidth",
                info.get(
                    "width",
                    0,
                ),
            )
            or 0
        )

        height = int(
            info.get(
                "thumbheight",
                info.get(
                    "height",
                    0,
                ),
            )
            or 0
        )

        if (
            width <= 0
            or height <= 0
        ):
            continue

        aspect_ratio = (
            width / height
        )

        if aspect_ratio < 1.3:
            continue

        candidates.append(
            {
                "title":
                    page.get(
                        "title",
                        "",
                    ),

                "url":
                    url,

                "source":
                    info.get(
                        "descriptionurl",
                        "",
                    ),

                "width":
                    width,

                "height":
                    height,

                "mime":
                    mime,

                "score":
                    width * height,
            }
        )

    candidates.sort(
        key=lambda candidate:
            candidate[
                "score"
            ],
        reverse=True,
    )

    return candidates


# =========================================================
# DOWNLOAD
# =========================================================

def _download_candidate(
    candidate: dict[str, Any],
) -> bytes:

    response = requests.get(
        candidate[
            "url"
        ],
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    content_type = (
        response.headers.get(
            "Content-Type",
            "",
        )
        .lower()
    )

    if (
        "image/" not in content_type
        and not response.content
    ):

        raise RuntimeError(
            "The download was not an image."
        )

    return response.content


# =========================================================
# SAVE METADATA
# =========================================================

def _save_metadata(
    topic: str,
    candidate: dict[str, Any],
    wallpaper_path: Path,
) -> None:

    metadata = {
        "topic":
            topic,

        "file":
            str(
                wallpaper_path
            ),

        "title":
            candidate.get(
                "title",
                "",
            ),

        "source":
            candidate.get(
                "source",
                "",
            ),

        "download_url":
            candidate.get(
                "url",
                "",
            ),
    }

    metadata_path = Path(
        user_file(
            "last_wallpaper.json"
        )
    )

    metadata_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )


# =========================================================
# MAIN WALLPAPER ACTION
# =========================================================

def set_wallpaper_from_topic(
    topic: str,
) -> dict[str, Any]:

    clean_topic = (
        _clean_topic(
            topic
        )
    )

    try:

        candidates = (
            _search_commons(
                clean_topic
            )
        )

    except Exception as error:

        return {
            "success":
                False,

            "message":
                (
                    "I couldn't search for "
                    "wallpapers right now: "
                    f"{error}"
                ),
        }

    if not candidates:

        return {
            "success":
                False,

            "message":
                (
                    "I couldn't find a good "
                    f"{clean_topic} wallpaper."
                ),
        }

    last_error = None

    # Try several candidates automatically.
    for candidate in candidates[:8]:

        try:

            image_bytes = (
                _download_candidate(
                    candidate
                )
            )

            wallpaper_path = (
                _prepare_image(
                    image_bytes,
                    clean_topic,
                )
            )

            set_wallpaper_file(
                wallpaper_path
            )

            _save_metadata(
                clean_topic,
                candidate,
                wallpaper_path,
            )

            return {
                "success":
                    True,

                "topic":
                    clean_topic,

                "file":
                    str(
                        wallpaper_path
                    ),

                "source":
                    candidate.get(
                        "source",
                        "",
                    ),

                "message":
                    (
                        "Done. I set a "
                        f"{clean_topic} wallpaper."
                    ),
            }

        except Exception as error:

            last_error = error
            continue

    return {
        "success":
            False,

        "message":
            (
                "I found some images, "
                "but none of them could be "
                "used as your wallpaper. "
                f"Last error: {last_error}"
            ),
    }