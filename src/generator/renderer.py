"""IR Renderer — top-level dispatch from Intent IR to clipboard JSON.

Entry point: render_ir(ir, *, options=None) → result dict.
"""
from __future__ import annotations

from typing import Any

from src.generator.events import EventSheetGenerator
from src.generator.objects import ObjectTypeGenerator
from src.imagedata.generator import generate_placeholder
from src.validator.structural import StructuralValidator


def render_ir(ir: dict, *, options: dict | None = None) -> dict:
    """Render Intent IR to clipboard JSON with validation and metadata.

    Returns dict with keys:
    - success: bool
    - clipboard_json: dict  (present when success is True)
    - validation: {passed, errors, warnings}
    - metadata: dict        (type-specific stats)
    - error: str            (present when success is False)
    """
    opts = options or {}
    ir_type = ir.get("type", "")

    try:
        if ir_type == "event_sheet":
            clipboard_json = EventSheetGenerator().from_ir(ir)
            metadata = _event_metadata(clipboard_json.get("items", []))
        elif ir_type == "object_types":
            clipboard_json, metadata = _render_objects(ir, opts)
        else:
            return {
                "success": False,
                "error": f"Unknown IR type: '{ir_type}'",
                "validation": {"passed": False, "errors": [], "warnings": []},
                "metadata": {},
            }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "validation": {"passed": False, "errors": [], "warnings": []},
            "metadata": {},
        }

    # Validate
    result = StructuralValidator().validate(clipboard_json)
    validation = {
        "passed": result.passed,
        "errors": result.errors,
        "warnings": result.warnings,
    }

    return {
        "success": result.passed,
        "clipboard_json": clipboard_json,
        "validation": validation,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Object-types renderer
# ---------------------------------------------------------------------------

def _render_objects(ir: dict, opts: dict) -> tuple[dict, dict]:
    """Build object-types clipboard from IR and return (clipboard_json, metadata)."""
    gen = ObjectTypeGenerator()
    items: list[dict] = []
    image_data: list[str] | None = None

    for obj in ir.get("objects", []):
        item = gen.build(
            obj["name"],
            obj["plugin"],
            behaviors=obj.get("behaviors"),
            effects=obj.get("effects"),
            instance_variables=obj.get("instance_variables"),
            is_global=obj.get("is_global", False),
            properties=obj.get("properties"),
        )
        items.append(item)

    if opts.get("include_imagedata"):
        # Every generated frame/image uses imageDataIndex 0, so one
        # placeholder serves all items that carry animations or an image.
        if any("animations" in it or "image" in it for it in items):
            image_data = [generate_placeholder(width=32, height=32)]

    clipboard_json = gen.build_clipboard(items, image_data=image_data)

    metadata: dict[str, Any] = {
        "objects_created": len(items),
        "behaviors": _collect_behaviors(items),
        "has_imagedata": image_data is not None,
    }
    return clipboard_json, metadata


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _event_metadata(items: list[dict]) -> dict[str, Any]:
    """Count blocks, variables, groups, and function-blocks in event items."""
    blocks = 0
    variables = 0
    groups = 0
    functions = 0

    for item in items:
        t = item.get("eventType")
        if t == "block":
            blocks += 1
        elif t == "variable":
            variables += 1
        elif t == "group":
            groups += 1
        elif t == "function-block":
            functions += 1

    return {
        "blocks": blocks,
        "variables": variables,
        "groups": groups,
        "functions": functions,
    }


def _collect_behaviors(items: list[dict]) -> list[str]:
    """Return sorted unique behavior names from all item behaviorTypes lists."""
    seen: set[str] = set()
    for item in items:
        for behavior in item.get("behaviorTypes", []):
            name = behavior.get("behavior-id") or behavior.get("name", "")
            if name:
                seen.add(name)
    return sorted(seen)
