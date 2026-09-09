"""Tests for IR Renderer (src/generator/renderer.py)."""
import pytest

from src.generator.renderer import render_ir


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def event_sheet_ir():
    return {
        "type": "event_sheet",
        "variables": [
            {"name": "Score", "type": "number", "initialValue": "0", "comment": ""},
        ],
        "events": [
            {
                "conditions": [
                    {"id": "OnStart", "objectClass": "System"},
                ],
                "actions": [
                    {"id": "SetValue", "objectClass": "System",
                     "parameters": {"0": "Score", "1": "0"}},
                ],
            }
        ],
        "groups": [],
        "functions": [],
    }


@pytest.fixture
def object_types_ir():
    return {
        "type": "object_types",
        "objects": [
            {"name": "Player", "plugin": "Sprite"},
            {"name": "Enemy", "plugin": "Sprite",
             "behaviors": [{"behavior-id": "Platform"}]},
        ],
    }


# ---------------------------------------------------------------------------
# test_render_event_sheet — success, validates
# ---------------------------------------------------------------------------

def test_render_event_sheet(event_sheet_ir):
    result = render_ir(event_sheet_ir)

    assert result["success"] is True
    assert "clipboard_json" in result
    assert result["clipboard_json"]["type"] == "events"
    assert result["validation"]["passed"] is True
    assert result["validation"]["errors"] == []


# ---------------------------------------------------------------------------
# test_render_object_types — success, correct type
# ---------------------------------------------------------------------------

def test_render_object_types(object_types_ir):
    result = render_ir(object_types_ir)

    assert result["success"] is True
    assert "clipboard_json" in result
    assert result["clipboard_json"]["type"] == "object-types"
    assert result["validation"]["passed"] is True


# ---------------------------------------------------------------------------
# test_render_unknown_type — not success, has error
# ---------------------------------------------------------------------------

def test_render_unknown_type():
    result = render_ir({"type": "banana_republic"})

    assert result["success"] is False
    assert "error" in result
    assert "banana_republic" in result["error"]


def test_render_missing_type():
    result = render_ir({})

    assert result["success"] is False
    assert "error" in result


# ---------------------------------------------------------------------------
# test_render_includes_metadata — objects_created count correct
# ---------------------------------------------------------------------------

def test_render_includes_metadata(object_types_ir):
    result = render_ir(object_types_ir)

    assert result["success"] is True
    meta = result["metadata"]
    assert meta["objects_created"] == 2


def test_render_event_metadata(event_sheet_ir):
    result = render_ir(event_sheet_ir)

    assert result["success"] is True
    meta = result["metadata"]
    assert meta["variables"] == 1
    assert meta["blocks"] == 1
    assert meta["groups"] == 0
    assert meta["functions"] == 0


def test_render_collects_behaviors(object_types_ir):
    result = render_ir(object_types_ir)

    assert result["success"] is True
    assert "Platform" in result["metadata"]["behaviors"]


# ---------------------------------------------------------------------------
# include_imagedata option
# ---------------------------------------------------------------------------

def test_render_object_types_with_imagedata(object_types_ir):
    result = render_ir(object_types_ir, options={"include_imagedata": True})

    assert result["success"] is True
    assert result["metadata"]["has_imagedata"] is True
    clipboard = result["clipboard_json"]
    assert isinstance(clipboard["imageData"], list)
    assert clipboard["imageData"][0].startswith("data:image/png;base64,")


def test_render_object_types_without_imagedata(object_types_ir):
    result = render_ir(object_types_ir)

    assert result["metadata"]["has_imagedata"] is False
    assert "imageData" not in result["clipboard_json"]


# ---------------------------------------------------------------------------
# Singleton plugin (no animations → no imagedata even with option)
# ---------------------------------------------------------------------------

def test_render_singleton_no_imagedata():
    ir = {
        "type": "object_types",
        "objects": [{"name": "Keyboard", "plugin": "Keyboard"}],
    }
    result = render_ir(ir, options={"include_imagedata": True})

    assert result["success"] is True
    # Keyboard has no animations → image_data stays None
    assert result["metadata"]["has_imagedata"] is False


def test_render_tiledbg_gets_imagedata():
    ir = {
        "type": "object_types",
        "objects": [{"name": "Ground", "plugin": "TiledBg"}],
    }
    result = render_ir(ir, options={"include_imagedata": True})

    assert result["success"] is True
    assert result["metadata"]["has_imagedata"] is True
    assert "image" in result["clipboard_json"]["items"][0]
