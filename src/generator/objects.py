"""Object Type Generator for Construct 3 clipboard JSON.

Builds ``object-types`` clipboard payloads from simplified plugin specs.
Handles the three plugin categories (singleton, non-world, world) and
the world sub-category that requires animations (Sprite-like plugins).
"""
from __future__ import annotations

import copy
from typing import Any

from src.generator.builder import wrap_clipboard

# ---------------------------------------------------------------------------
# Plugin classification sets
# ---------------------------------------------------------------------------

SINGLETON_PLUGINS: frozenset[str] = frozenset({
    "Keyboard", "Mouse", "Touch", "Gamepad", "Audio", "Browser",
    "AJAX", "XHR2", "LocalStorage", "SessionStorage", "Multiplayer",
    "AdvancedRandom", "Date", "Cryptography", "CSV", "Internationalization",
    "PlatformInfo", "ShareDialog", "SpeechSynthesis", "SpeechRecognition",
    "Clipboard", "MIDI", "Geolocation", "Bluetooth",
})

NONWORLD_PLUGINS: frozenset[str] = frozenset({
    "Arr", "Dictionary", "BinaryData", "JSON", "XML", "Function",
})

# World plugins that do NOT get the animations field
WORLD_NO_ANIMATIONS_PLUGINS: frozenset[str] = frozenset({
    "Text", "SpriteFont", "TiledBg", "NinePatch", "Particles",
    "HTMLElement", "TextInput", "Button", "ProgressBar", "SliderBar",
    "DrawingCanvas", "Tilemap",
})

# ---------------------------------------------------------------------------
# Default animation structure for Sprite-like objects
# ---------------------------------------------------------------------------

BLANK_ANIMATION: dict[str, Any] = {
    "items": [{
        "frames": [{
            "width": 32, "height": 32,
            "originX": 0.5, "originY": 0.5,
            "originalSource": "",
            "exportFormat": "lossless",
            "exportQuality": 0.8,
            "fileType": "image/png",
            "imageDataIndex": 0,
            "useCollisionPoly": True,
            "duration": 1,
            "tag": "",
        }],
        "name": "Default",
        "isLooping": False, "isPingPong": False,
        "repeatCount": 1, "repeatTo": 0, "speed": 5,
    }],
    "subfolders": [],
}


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class ObjectTypeGenerator:
    """Build object-type items and clipboard envelopes."""

    def build(
        self,
        name: str,
        plugin_id: str,
        *,
        behaviors: list[dict] | None = None,
        effects: list[dict] | None = None,
        instance_variables: list[dict] | None = None,
        is_global: bool = False,
    ) -> dict:
        """Return a single object type item dict.

        Args:
            name: The object type name (used as a label; not embedded in the
                  dict itself — C3 puts this in the outer envelope context).
            plugin_id: The C3 plugin identifier (e.g. ``"Sprite"``, ``"Keyboard"``).
            behaviors: Optional list of behavior type dicts.
            effects: Optional list of effect type dicts.
            instance_variables: Optional list of instance variable dicts.
            is_global: Whether the object is marked global (world/nonworld only).
        """
        if plugin_id in SINGLETON_PLUGINS:
            return self._build_singleton(plugin_id)
        if plugin_id in NONWORLD_PLUGINS:
            return self._build_nonworld(
                plugin_id,
                instance_variables=instance_variables,
                is_global=is_global,
            )
        return self._build_world(
            plugin_id,
            behaviors=behaviors,
            effects=effects,
            instance_variables=instance_variables,
            is_global=is_global,
        )

    # ------------------------------------------------------------------
    # Category builders
    # ------------------------------------------------------------------

    def _build_singleton(self, plugin_id: str) -> dict:
        return {
            "plugin-id": plugin_id,
            "singleglobal-inst": {},
        }

    def _build_nonworld(
        self,
        plugin_id: str,
        *,
        instance_variables: list[dict] | None,
        is_global: bool,
    ) -> dict:
        return {
            "plugin-id": plugin_id,
            "nonworld-inst": {},
            "isGlobal": is_global,
            "editorNewInstanceIsReplica": False,
            "instanceVariables": list(instance_variables) if instance_variables else [],
        }

    def _build_world(
        self,
        plugin_id: str,
        *,
        behaviors: list[dict] | None,
        effects: list[dict] | None,
        instance_variables: list[dict] | None,
        is_global: bool,
    ) -> dict:
        item: dict[str, Any] = {
            "plugin-id": plugin_id,
            "isGlobal": is_global,
            "editorNewInstanceIsReplica": False,
            "instanceVariables": list(instance_variables) if instance_variables else [],
            "behaviorTypes": list(behaviors) if behaviors else [],
            "effectTypes": list(effects) if effects else [],
        }
        if plugin_id not in WORLD_NO_ANIMATIONS_PLUGINS:
            item["animations"] = copy.deepcopy(BLANK_ANIMATION)
        return item

    # ------------------------------------------------------------------
    # Clipboard envelope
    # ------------------------------------------------------------------

    def build_clipboard(
        self,
        items: list[dict],
        *,
        image_data: str | None = None,
    ) -> dict:
        """Wrap items in a C3 object-types clipboard envelope.

        Args:
            items: List of object type item dicts (built by :meth:`build`).
            image_data: Optional PNG data URI string to embed as ``imageData``.
        """
        extra: dict[str, Any] = {
            "families": [],
            "folders": [],
        }
        if image_data is not None:
            extra["imageData"] = image_data

        return wrap_clipboard("object-types", items, **extra)
