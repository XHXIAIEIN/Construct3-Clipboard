"""Tests for ObjectTypeGenerator."""
import json
import re
from pathlib import Path

import pytest

from src.generator.objects import ObjectTypeGenerator
from src.validator.structural import StructuralValidator


@pytest.fixture
def gen():
    return ObjectTypeGenerator()


# ---------------------------------------------------------------------------
# build() tests
# ---------------------------------------------------------------------------

def test_sprite_object(gen):
    """Sprite (world + animated) should have animations and effectTypes."""
    obj = gen.build("Player", "Sprite")

    assert obj["plugin-id"] == "Sprite"
    assert "animations" in obj
    assert isinstance(obj["animations"]["items"], list)
    assert obj["animations"]["items"][0]["name"] == "Default"
    assert isinstance(obj["effectTypes"], list)
    assert isinstance(obj["behaviorTypes"], list)
    assert isinstance(obj["instanceVariables"], list)
    # world objects should NOT have singleglobal-inst or nonworld-inst
    assert "singleglobal-inst" not in obj
    assert "nonworld-inst" not in obj


def test_singleton_object(gen):
    """Keyboard is singleton — name, plugin-id and singleglobal-inst only."""
    obj = gen.build("Keyboard", "Keyboard")

    assert obj["name"] == "Keyboard"
    assert obj["plugin-id"] == "Keyboard"
    assert obj["singleglobal-inst"] == {"type": "Keyboard", "properties": {}, "tags": ""}
    assert "nonworld-inst" not in obj
    assert "animations" not in obj
    assert "behaviorTypes" not in obj
    assert "effectTypes" not in obj
    assert "instanceVariables" not in obj


def test_nonworld_object(gen):
    """Arr (non-world) should have nonworld-inst, no animations."""
    obj = gen.build("MyArray", "Arr", properties={"width": 10, "height": 1, "depth": 1})

    assert obj["name"] == "MyArray"
    assert obj["plugin-id"] == "Arr"
    assert obj["nonworld-inst"] == {
        "type": "MyArray",
        "properties": {"width": 10, "height": 1, "depth": 1},
        "tags": "",
    }
    assert "singleglobal-inst" not in obj
    assert "animations" not in obj
    # non-world doesn't get behaviorTypes / effectTypes / instanceVariables
    assert "behaviorTypes" not in obj
    assert "effectTypes" not in obj
    assert "instanceVariables" not in obj


def test_text_object(gen):
    """Text is world-without-animations — has effectTypes but no animations."""
    obj = gen.build("Label", "Text")

    assert obj["plugin-id"] == "Text"
    assert "animations" not in obj
    assert isinstance(obj["effectTypes"], list)
    assert isinstance(obj["behaviorTypes"], list)
    assert "singleglobal-inst" not in obj
    assert "nonworld-inst" not in obj


def test_with_behaviors(gen):
    """behaviorTypes kwarg should populate the behaviorTypes array."""
    behaviors = [{"id": "Platform", "plugin-id": "Platform"}]
    obj = gen.build("Hero", "Sprite", behaviors=behaviors)

    assert obj["behaviorTypes"] == behaviors


def test_with_instance_variables(gen):
    """instance_variables kwarg should populate instanceVariables."""
    ivars = [{"name": "health", "type": "number", "initialValue": "100"}]
    obj = gen.build("Hero", "Sprite", instance_variables=ivars)

    assert obj["instanceVariables"] == ivars


def test_animations_are_deep_copied(gen):
    """Each Sprite build should get an independent animation object."""
    obj1 = gen.build("A", "Sprite")
    obj2 = gen.build("B", "Sprite")

    # Mutating one should not affect the other
    obj1["animations"]["items"][0]["name"] = "MUTATED"
    assert obj2["animations"]["items"][0]["name"] == "Default"


def test_is_global_flag_world(gen):
    """is_global flag should be reflected on world objects."""
    obj = gen.build("GlobalSprite", "Sprite", is_global=True)
    assert obj["isGlobal"] is True


def test_is_global_flag_nonworld(gen):
    """is_global flag should be reflected on non-world objects."""
    obj = gen.build("GlobalArr", "Arr", is_global=True)
    assert obj["isGlobal"] is True


def test_singleton_ignores_is_global(gen):
    """Singleton objects don't expose isGlobal (they're always global)."""
    obj = gen.build("Keyboard", "Keyboard", is_global=True)
    assert "isGlobal" not in obj


# ---------------------------------------------------------------------------
# build_clipboard() tests
# ---------------------------------------------------------------------------

def test_build_clipboard_validates(gen):
    """Wrapped output should pass StructuralValidator."""
    items = [
        gen.build("Player", "Sprite"),
        gen.build("Keyboard", "Keyboard"),
        gen.build("MyArr", "Arr"),
    ]
    clipboard = gen.build_clipboard(items)

    validator = StructuralValidator()
    result = validator.validate(clipboard)
    assert result.passed, f"Validation errors: {result.errors}"


def test_build_clipboard_envelope(gen):
    """Clipboard envelope should have correct type and required fields."""
    items = [gen.build("Player", "Sprite")]
    clipboard = gen.build_clipboard(items)

    assert clipboard["is-c3-clipboard-data"] is True
    assert clipboard["type"] == "object-types"
    assert clipboard["families"] == []
    assert clipboard["folders"] == []
    assert len(clipboard["items"]) == 1


def test_build_clipboard_with_image_data(gen):
    """imageData is a list of data URIs referenced by imageDataIndex."""
    items = [gen.build("Player", "Sprite")]
    fake_png = "data:image/png;base64,abc123"
    clipboard = gen.build_clipboard(items, image_data=[fake_png])

    assert clipboard["imageData"] == [fake_png]


def test_effects_kwarg(gen):
    """effects kwarg should populate effectTypes on world objects."""
    effects = [{"id": "Bloom", "name": "Bloom"}]
    obj = gen.build("Player", "Sprite", effects=effects)
    assert obj["effectTypes"] == effects


# ---------------------------------------------------------------------------
# Key sets must match the templates in docs/object-templates.md
# ---------------------------------------------------------------------------

TEMPLATES_DOC = Path(__file__).resolve().parent.parent / "docs" / "object-templates.md"


def _template_items() -> dict[str, dict]:
    """Return {plugin-id: item} for every object-types template in the doc."""
    text = TEMPLATES_DOC.read_text(encoding="utf-8")
    text = re.sub(r"\{(WIDTH|HEIGHT)\}", "32", text)
    text = re.sub(r"\{[A-Z_]+\}", "X", text)
    items: dict[str, dict] = {}
    for block in re.findall(r"```json\n(.*?)\n```", text, flags=re.S):
        block = block.strip()
        if not block.startswith('{"is-c3-clipboard-data"'):
            continue
        for item in json.loads(block)["items"]:
            items[item["plugin-id"]] = item
    return items


TEMPLATE_ITEMS = _template_items()


def _key_tree(node):
    """Nested structure of dict keys, ignoring leaf values."""
    if isinstance(node, dict):
        return {k: _key_tree(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_key_tree(node[0])] if node else []
    return None


@pytest.mark.parametrize("plugin_id", sorted(TEMPLATE_ITEMS))
def test_generated_keys_match_template(gen, plugin_id):
    template = TEMPLATE_ITEMS[plugin_id]
    obj = gen.build(template["name"], plugin_id, properties=_template_properties(template))
    assert _key_tree(obj) == _key_tree(template), plugin_id


def _template_properties(template: dict) -> dict | None:
    inst = template.get("singleglobal-inst") or template.get("nonworld-inst")
    return inst["properties"] if inst else None


def test_templates_cover_every_category():
    assert {"Sprite", "TiledBg", "NinePatch", "Tilemap", "Text", "Keyboard", "Arr"} <= set(TEMPLATE_ITEMS)
