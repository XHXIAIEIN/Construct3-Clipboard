"""Tests for StructuralValidator — validates C3 clipboard JSON format rules."""
import pytest
from src.validator.structural import StructuralValidator, ValidationResult


@pytest.fixture
def validator():
    return StructuralValidator()


# ---------------------------------------------------------------------------
# TestBasicStructure
# ---------------------------------------------------------------------------

class TestBasicStructure:
    def test_valid_events_pass(self, validator, valid_events_basic):
        result = validator.validate(valid_events_basic)
        assert result.passed is True
        assert result.errors == []

    def test_missing_header_fails(self, validator, invalid_missing_header):
        result = validator.validate(invalid_missing_header)
        assert result.passed is False
        assert any("is-c3-clipboard-data" in e for e in result.errors)

    def test_header_false_fails(self, validator):
        data = {"is-c3-clipboard-data": False, "type": "events", "items": []}
        result = validator.validate(data)
        assert result.passed is False

    def test_invalid_type_fails(self, validator):
        data = {"is-c3-clipboard-data": True, "type": "unsupported-type", "items": []}
        result = validator.validate(data)
        assert result.passed is False
        assert any("type" in e.lower() for e in result.errors)

    def test_missing_type_fails(self, validator):
        data = {"is-c3-clipboard-data": True, "items": []}
        result = validator.validate(data)
        assert result.passed is False

    def test_items_not_array_fails(self, validator):
        data = {"is-c3-clipboard-data": True, "type": "events", "items": {}}
        result = validator.validate(data)
        assert result.passed is False
        assert any("items" in e.lower() for e in result.errors)

    def test_missing_items_fails(self, validator):
        data = {"is-c3-clipboard-data": True, "type": "events"}
        result = validator.validate(data)
        assert result.passed is False

    def test_all_valid_clipboard_types_accepted(self, validator):
        valid_types = [
            "events", "conditions", "actions", "object-types",
            "world-instances", "layouts", "event-sheets"
        ]
        for t in valid_types:
            data = {"is-c3-clipboard-data": True, "type": t, "items": []}
            result = validator.validate(data)
            # No "invalid type" error
            assert not any("invalid" in e.lower() and "type" in e.lower() for e in result.errors), \
                f"Type '{t}' should be valid but got errors: {result.errors}"


# ---------------------------------------------------------------------------
# TestEventValidation
# ---------------------------------------------------------------------------

class TestEventValidation:
    def test_variable_missing_comment_warns(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {"type": "variable", "name": "score", "variableType": "number", "initialValue": "0"}
            ]
        }
        result = validator.validate(data)
        assert result.passed is True  # warnings don't fail
        assert any("comment" in w.lower() for w in result.warnings)

    def test_variable_missing_name_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {"type": "variable", "variableType": "number", "initialValue": "0", "comment": "x"}
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("name" in e.lower() for e in result.errors)

    def test_variable_invalid_type_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {"type": "variable", "name": "x", "variableType": "float", "initialValue": "0", "comment": ""}
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_block_needs_conditions_and_actions(self, validator):
        # Missing both
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [{"type": "block"}]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("condition" in e.lower() or "action" in e.lower() for e in result.errors)

    def test_block_missing_actions_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": [{"id": "always", "objectClass": "System"}]
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_block_conditions_not_list_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": "not-a-list",
                    "actions": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_empty_parameters_warns(self, validator, invalid_empty_parameters):
        result = validator.validate(invalid_empty_parameters)
        assert result.passed is True
        assert any("parameter" in w.lower() for w in result.warnings)

    def test_valid_comparison_operators(self, validator):
        for op in range(6):  # 0-5 valid
            data = {
                "is-c3-clipboard-data": True,
                "type": "events",
                "items": [
                    {
                        "type": "block",
                        "conditions": [
                            {"id": "compare", "objectClass": "Player",
                             "parameters": {"0": op}}
                        ],
                        "actions": []
                    }
                ]
            }
            result = validator.validate(data)
            assert not any("comparison" in e.lower() for e in result.errors), \
                f"Operator {op} should be valid"

    def test_invalid_comparison_operator_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": [
                        {"id": "compare", "objectClass": "Player",
                         "parameters": {"0": 6}}  # 6 is out of range
                    ],
                    "actions": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("comparison" in e.lower() or "operator" in e.lower() for e in result.errors)

    def test_function_block_validates(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "function-block",
                    "functionName": "MyFunc",
                    "functionReturnType": "none",
                    "conditions": [],
                    "actions": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is True

    def test_function_block_missing_name_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "function-block",
                    "functionReturnType": "none",
                    "conditions": [],
                    "actions": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_function_block_invalid_return_type_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "function-block",
                    "functionName": "MyFunc",
                    "functionReturnType": "void",  # not valid
                    "conditions": [],
                    "actions": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_script_action_validates(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": [],
                    "actions": [
                        {
                            "id": "run-script",
                            "objectClass": "System",
                            "script": ["console.log('hi');"],
                            "language": "javascript"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is True

    def test_script_action_missing_language_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": [],
                    "actions": [
                        {
                            "id": "run-script",
                            "objectClass": "System",
                            "script": ["console.log('hi');"]
                            # missing language
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_script_action_script_not_list_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {
                    "type": "block",
                    "conditions": [],
                    "actions": [
                        {
                            "id": "run-script",
                            "objectClass": "System",
                            "script": "console.log('hi');",  # should be list
                            "language": "javascript"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_invalid_event_type_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "events",
            "items": [
                {"type": "unknown-event-type"}
            ]
        }
        result = validator.validate(data)
        assert result.passed is False


# ---------------------------------------------------------------------------
# TestObjectTypeValidation
# ---------------------------------------------------------------------------

class TestObjectTypeValidation:
    def test_valid_object_types_passes(self, validator, valid_object_types):
        result = validator.validate(valid_object_types)
        assert result.passed is True

    def test_missing_plugin_id_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {"animations": [], "behaviorTypes": [], "effectTypes": [], "instanceVariables": []}
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("plugin-id" in e.lower() or "plugin_id" in e.lower() for e in result.errors)

    def test_effect_types_must_be_array(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {
                    "plugin-id": "Sprite",
                    "animations": [],
                    "behaviorTypes": [],
                    "effectTypes": {"blend": {}},  # object, should be array
                    "instanceVariables": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("effecttypes" in e.lower() or "effect" in e.lower() for e in result.errors)

    def test_instance_variables_must_be_array(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {
                    "plugin-id": "Sprite",
                    "animations": [],
                    "behaviorTypes": [],
                    "effectTypes": [],
                    "instanceVariables": {"hp": 100}  # object, should be array
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("instancevariable" in e.lower() or "instance" in e.lower() for e in result.errors)

    def test_behavior_types_must_be_array(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {
                    "plugin-id": "Sprite",
                    "animations": [],
                    "behaviorTypes": {"Platform": {}},  # object, should be array
                    "effectTypes": [],
                    "instanceVariables": []
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("behaviortypes" in e.lower() or "behavior" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# TestLayoutValidation
# ---------------------------------------------------------------------------

class TestLayoutValidation:
    def test_missing_layers_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "layouts",
            "items": [
                {"name": "Level1"}  # missing layers
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("layer" in e.lower() for e in result.errors)

    def test_layers_not_list_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "layouts",
            "items": [
                {"name": "Level1", "layers": "background"}
            ]
        }
        result = validator.validate(data)
        assert result.passed is False

    def test_valid_minimal_layout_passes(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "layouts",
            "items": [
                {"name": "Level1", "layers": []}
            ]
        }
        result = validator.validate(data)
        assert result.passed is True


# ---------------------------------------------------------------------------
# TestImageDataValidation
# ---------------------------------------------------------------------------

class TestImageDataValidation:
    def test_valid_png_data_uri_passes(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {
                    "plugin-id": "Sprite",
                    "animations": [],
                    "behaviorTypes": [],
                    "effectTypes": [],
                    "instanceVariables": [],
                    "imageData": "data:image/png;base64,iVBORw0KGgo="
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is True

    def test_non_png_image_data_fails(self, validator):
        data = {
            "is-c3-clipboard-data": True,
            "type": "object-types",
            "items": [
                {
                    "plugin-id": "Sprite",
                    "animations": [],
                    "behaviorTypes": [],
                    "effectTypes": [],
                    "instanceVariables": [],
                    "imageData": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB"
                }
            ]
        }
        result = validator.validate(data)
        assert result.passed is False
        assert any("png" in e.lower() or "imagedata" in e.lower() for e in result.errors)
