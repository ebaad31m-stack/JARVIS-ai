from __future__ import annotations

import ctypes
import json
import re
import time
import winreg
from pathlib import Path
from typing import Any

import requests

from core.paths import user_file


COMMONS_API = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "JARVIS-Personal-Assistant/1.0"
}

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def _wallpaper_directory() -> Path:
    folder = Path(
        user_file("wallpapers")
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return folder


def _clean_topic(topic: str) -> str:
    topic = topic.strip()

    topic = re.sub(
        r"\s+",
        " ",
        topic
    )

    topic = re.sub(
        r"^(a|an|some|the)\s+",
        "",
        topic,
        flags=re.IGNORECASE
    )

    topic = re.sub(
        r"\s+(wallpaper|background|picture|image)$",
        "",
        topic,
        flags=re.IGNORECASE
    )

    if not topic:
        topic = "nature"

    return topic[:80]


def _set_fill_style() -> None:
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    ) as key:

        # 10 = Fill
        winreg.SetValueEx(
            key,
            "WallpaperStyle",
            0,
            winreg.REG_SZ,
            "10"
        )

        winreg.SetValueEx(
            key,
            "TileWallpaper",
            0,
            winreg.REG_SZ,
            "0"
        )


def set_wallpaper_file(
    file_path: str | Path
) -> bool:

    path = Path(
        file_path
    ).resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Wallpaper does not exist: {path}"
        )

    _set_fill_style()

    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        str(path),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    return bool(result)


def _search_commons(
    topic: str
) -> list[dict[str, Any]]:

    search_topic = (
        f"{topic} landscape"
    )

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": search_topic,
        "gsrnamespace": "6",
        "gsrlimit": "15",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "2560",
    }

    response = requests.get(
        COMMONS_API,
        params=params,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    pages = (
        data
        .get("query", {})
        .get("pages", {})
    )

    candidates = []

    for page in pages.values():

        image_info_list = page.get(
            "imageinfo",
            []
        )

        if not image_info_list:
            continue

        info = image_info_list[0]

        mime = str(
            info.get(
                "mime",
                ""
            )
        ).lower()

        if mime not in {
            "image/jpeg",
            "image/png"
        }:
            continue

        url = (
            info.get("thumburl")
            or info.get("url")
        )

        if not url:
            continue

        width = int(
            info.get(
                "thumbwidth",
                info.get(
                    "width",
                    0
                )
            )
            or 0
        )

        height = int(
            info.get(
                "thumbheight",
                info.get(
                    "height",
                    0
                )
            )
            or 0
        )

        if width <= 0 or height <= 0:
            continue

        ratio = width / height

        # Prefer landscape wallpapers.
        if ratio < 1.25:
            continue

        candidates.append(
            {
                "title": page.get(
                    "title",
                    ""
                ),
                "url": url,
                "source": info.get(
                    "descriptionurl",
                    ""
                ),
                "width": width,
                "height": height,
                "mime": mime,
                "score": width * height,
            }
        )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return candidates


def _download_wallpaper(
    candidate: dict[str, Any],
    topic: str
) -> Path:

    mime = candidate.get(
        "mime",
        "image/jpeg"
    )

    extension = (
        ".png"
        if mime == "image/png"
        else ".jpg"
    )

    safe_topic = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        topic
    ).strip("_")

    if not safe_topic:
        safe_topic = "wallpaper"

    filename = (
        f"{safe_topic}_"
        f"{int(time.time())}"
        f"{extension}"
    )

    destination = (
        _wallpaper_directory()
        / filename
    )

    response = requests.get(
        candidate["url"],
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    destination.write_bytes(
        response.content
    )

    return destination


def _save_metadata(
    topic: str,
    candidate: dict[str, Any],
    path: Path
) -> None:

    metadata = {
        "topic": topic,
        "file": str(path),
        "title": candidate.get(
            "title",
            ""
        ),
        "source": candidate.get(
            "source",
            ""
        ),
        "download_url": candidate.get(
            "url",
            ""
        ),
    }

    metadata_path = Path(
        user_file(
            "last_wallpaper.json"
        )
    )

    metadata_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )


def set_wallpaper_from_topic(
    topic: str
) -> dict[str, Any]:

    clean_topic = _clean_topic(
        topic
    )

    candidates = _search_commons(
        clean_topic
    )

    if not candidates:
        return {
            "success": False,
            "message": (
                f"I couldn't find a suitable "
                f"{clean_topic} wallpaper."
            )
        }

    candidate = candidates[0]

    try:
        wallpaper_path = (
            _download_wallpaper(
                candidate,
                clean_topic
            )
        )

        success = set_wallpaper_file(
            wallpaper_path
        )

        if not success:
            return {
                "success": False,
                "message": (
                    "Windows rejected the wallpaper change."
                )
            }

        _save_metadata(
            clean_topic,
            candidate,
            wallpaper_path
        )

        return {
            "success": True,
            "topic": clean_topic,
            "file": str(
                wallpaper_path
            ),
            "source": candidate.get(
                "source",
                ""
            ),
            "message": (
                f"Done. I set a "
                f"{clean_topic} wallpaper."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "message": (
                "I found a wallpaper, "
                "but couldn't apply it: "
                f"{error}"
            ),
        }