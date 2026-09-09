"""Object Type Generator for Construct 3 clipboard JSON.

Builds ``object-types`` clipboard payloads from simplified plugin specs.
The item shapes follow the templates in docs/object-templates.md, which
tests/test_objects_generator.py compares against key by key.
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
    "Arr", "Dictionary", "BinaryData", "JSON", "XML",
})

# World plugins whose item carries a single ``image`` block instead of
# ``animations``. Tilemap additionally carries ``tile-collision-polys``.
WORLD_IMAGE_PLUGINS: frozenset[str] = frozenset({"TiledBg", "NinePatch", "Tilemap"})

# World plugins with neither ``animations`` nor ``image`` (Text is the
# template-backed one; the rest are assumed to match it).
WORLD_NO_IMAGE_PLUGINS: frozenset[str] = frozenset({
    "Text", "SpriteFont", "Particles",
    "HTMLElement", "TextInput", "Button", "ProgressBar", "SliderBar",
    "DrawingCanvas",
})

# ---------------------------------------------------------------------------
# Default image structures
# ---------------------------------------------------------------------------

BLANK_FRAME: dict[str, Any] = {
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
}

BLANK_ANIMATION: dict[str, Any] = {
    "items": [{
        "frames": [BLANK_FRAME],
        "name": "Default",
        "isLooping": False, "isPingPong": False,
        "repeatCount": 1, "repeatTo": 0, "speed": 5,
    }],
    "subfolders": [],
    "name": "Animations",
}

BLANK_IMAGE: dict[str, Any] = {
    "width": 32, "height": 32,
    "originX": 0.5, "originY": 0.5,
    "originalSource": "",
    "exportFormat": "lossless",
    "exportQuality": 0.8,
    "fileType": "image/png",
    "imageDataIndex": 0,
    "useCollisionPoly": True,
    "tag": "",
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
        properties: dict[str, Any] | None = None,
    ) -> dict:
        """Return a single object type item dict.

        Args:
            name: The object type name.
            plugin_id: The C3 plugin identifier (e.g. ``"Sprite"``, ``"Keyboard"``).
            behaviors: Optional list of behavior type dicts (world only).
            effects: Optional list of effect type dicts (world only).
            instance_variables: Optional list of instance variable dicts (world only).
            is_global: Whether the object is marked global (world/nonworld only).
            properties: Plugin properties for the ``singleglobal-inst`` /
                ``nonworld-inst`` block; empty when omitted.
        """
        if plugin_id in SINGLETON_PLUGINS:
            return self._build_singleton(name, plugin_id, properties=properties)
        if plugin_id in NONWORLD_PLUGINS:
            return self._build_nonworld(
                name, plugin_id, is_global=is_global, properties=properties,
            )
        return self._build_world(
            name, plugin_id,
            behaviors=behaviors,
            effects=effects,
            instance_variables=instance_variables,
            is_global=is_global,
        )

    # ------------------------------------------------------------------
    # Category builders
    # ------------------------------------------------------------------

    @staticmethod
    def _instance_block(name: str, properties: dict[str, Any] | None) -> dict:
        return {
            "type": name,
            "properties": dict(properties) if properties else {},
            "tags": "",
        }

    def _build_singleton(
        self, name: str, plugin_id: str, *, properties: dict[str, Any] | None,
    ) -> dict:
        return {
            "name": name,
            "plugin-id": plugin_id,
            "singleglobal-inst": self._instance_block(name, properties),
        }

    def _build_nonworld(
        self,
        name: str,
        plugin_id: str,
        *,
        is_global: bool,
        properties: dict[str, Any] | None,
    ) -> dict:
        return {
            "name": name,
            "plugin-id": plugin_id,
            "isGlobal": is_global,
            "nonworld-inst": self._instance_block(name, properties),
        }

    def _build_world(
        self,
        name: str,
        plugin_id: str,
        *,
        behaviors: list[dict] | None,
        effects: list[dict] | None,
        instance_variables: list[dict] | None,
        is_global: bool,
    ) -> dict:
        item: dict[str, Any] = {
            "name": name,
            "plugin-id": plugin_id,
            "isGlobal": is_global,
            "editorNewInstanceIsReplica": True,
            "instanceVariables": list(instance_variables) if instance_variables else [],
            "behaviorTypes": list(behaviors) if behaviors else [],
            "effectTypes": list(effects) if effects else [],
        }
        if plugin_id in WORLD_IMAGE_PLUGINS:
            item["image"] = copy.deepcopy(BLANK_IMAGE)
            if plugin_id == "Tilemap":
                item["tile-collision-polys"] = {}
        elif plugin_id not in WORLD_NO_IMAGE_PLUGINS:
            item["animations"] = copy.deepcopy(BLANK_ANIMATION)
        return item

    # ------------------------------------------------------------------
    # Clipboard envelope
    # ------------------------------------------------------------------

    def build_clipboard(
        self,
        items: list[dict],
        *,
        image_data: list[str] | None = None,
    ) -> dict:
        """Wrap items in a C3 object-types clipboard envelope.

        Args:
            items: List of object type item dicts (built by :meth:`build`).
            image_data: Optional list of PNG data URIs; items reference them
                by ``imageDataIndex``.
        """
        extra: dict[str, Any] = {
            "families": [],
            "folders": [],
        }
        if image_data is not None:
            extra["imageData"] = list(image_data)

        return wrap_clipboard("object-types", items, **extra)
