import json
from pathlib import Path
import pytest
from src.validator.structural import StructuralValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"
validator = StructuralValidator()

def load_fixture(subdir: str, name: str) -> dict:
    path = FIXTURES_DIR / subdir / name
    return json.loads(path.read_text(encoding="utf-8"))

class TestValidFixtures:
    @pytest.mark.parametrize("name", [
        "breakout_events.json",
        "platformer_events.json",
    ])
    def test_valid_events(self, name):
        data = load_fixture("valid", name)
        result = validator.validate(data)
        assert result.passed, f"{name}: {result.errors}"

    @pytest.mark.parametrize("name", [
        "breakout_layout.json",
        "platformer_layout.json",
    ])
    def test_valid_layouts(self, name):
        data = load_fixture("valid", name)
        result = validator.validate(data)
        assert result.passed, f"{name}: {result.errors}"

class TestInvalidFixtures:
    def test_missing_comment_warns(self):
        data = load_fixture("invalid", "missing_comment.json")
        result = validator.validate(data)
        assert any("comment" in w for w in result.warnings)

    def test_empty_parameters_warns(self):
        data = load_fixture("invalid", "empty_parameters.json")
        result = validator.validate(data)
        assert any("parameters" in w.lower() for w in result.warnings)

    def test_wrong_effecttypes_format(self):
        data = load_fixture("invalid", "wrong_behavior_id.json")
        result = validator.validate(data)
        assert not result.passed
        assert any("effectTypes" in e for e in result.errors)
