from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config_loader import ConfigLoader


SUPPORTED_MEDIA_TYPES = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".bmp": "image",
    ".gif": "gif",
    ".mp4": "video",
    ".mov": "video",
}


@dataclass
class AssetDescriptor:
    path: Path
    media_type: str  # image | gif | video
    category: str


class AssetManager:
    """Resolve asset paths based on configuration and optional user overrides."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None) -> None:
        self.config_loader = config_loader or ConfigLoader()

    def resolve_asset(self, category: Optional[str] = None, override_path: Optional[str | Path] = None) -> AssetDescriptor:
        if override_path:
            path = Path(override_path).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"Override asset path not found: {path}")
            media_type = self._detect_media_type(path)
            return AssetDescriptor(path=path, media_type=media_type, category=category or "override")

        category_name = category or self.config_loader.get_default_category()
        if not category_name:
            raise ValueError("No category provided and no default category configured.")

        entry = self.config_loader.get_category_entry(category_name)
        return self._resolve_from_entry(category_name, entry)

    def _resolve_from_entry(self, category: str, entry: dict) -> AssetDescriptor:
        assets_base = self.config_loader.get_assets_base()
        folder_name = entry.get("folder", "")
        if not folder_name:
            raise ValueError(f"Category '{category}' is missing a 'folder' entry in config.")

        folder_path = assets_base / folder_name
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder for category '{category}' not found at {folder_path}")

        preferred = entry.get("preferred_file") or entry.get("file") or ""
        if preferred:
            candidate = folder_path / preferred
            if not candidate.exists():
                raise FileNotFoundError(f"Preferred file for category '{category}' not found: {candidate}")
            return AssetDescriptor(path=candidate, media_type=self._detect_media_type(candidate), category=category)

        files = sorted([p for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_MEDIA_TYPES])
        if not files:
            raise FileNotFoundError(f"No supported media found in {folder_path}")

        selected = files[0]
        return AssetDescriptor(path=selected, media_type=self._detect_media_type(selected), category=category)

    @staticmethod
    def _detect_media_type(path: Path) -> str:
        media_type = SUPPORTED_MEDIA_TYPES.get(path.suffix.lower())
        if not media_type:
            raise ValueError(f"Unsupported media type for file: {path}")
        return media_type
