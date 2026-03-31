"""Tests for EventSheetGenerator — converts Intent IR to C3 clipboard JSON."""
import pytest
from src.generator.events import EventSheetGenerator
from src.validator.structural import StructuralValidator


@pytest.fixture
def gen():
    return EventSheetGenerator()


@pytest.fixture
def validator():
    return StructuralValidator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_valid(result: dict, validator: StructuralValidator) -> None:
    vr = validator.validate(result)
    assert vr.passed, f"Validation failed:\n" + "\n".join(vr.errors)


# ---------------------------------------------------------------------------
# test_empty_ir_produces_empty_events
# ---------------------------------------------------------------------------

class TestEmptyIR:
    def test_empty_ir_produces_empty_events(self, gen, validator):
        ir = {"type": "event_sheet"}
        result = gen.from_ir(ir)
        assert result["is-c3-clipboard-data"] is True
        assert result["type"] == "events"
        assert result["items"] == []
        assert_valid(result, validator)

    def test_empty_lists_ir(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "variables": [],
            "events": [],
            "groups": [],
            "functions": [],
        }
        result = gen.from_ir(ir)
        assert result["items"] == []
        assert_valid(result, validator)


# ---------------------------------------------------------------------------
# test_from_ir_events — variable + block
# ---------------------------------------------------------------------------

class TestFromIREvents:
    def test_variable_and_block(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "variables": [
                {
                    "name": "Score",
                    "type": "number",
                    "initialValue": "0",
                    "comment": "Player score",
                }
            ],
            "events": [
                {
                    "conditions": [
                        {"id": "on-start-of-layout", "objectClass": "System"}
                    ],
                    "actions": [
                        {
                            "id": "set-eventvar-value",
                            "objectClass": "System",
                            "parameters": {"0": "Score", "1": "0"},
                        }
                    ],
                }
            ],
        }
        result = gen.from_ir(ir)
        items = result["items"]

        # Variable comes first
        assert items[0]["type"] == "variable"
        assert items[0]["name"] == "Score"
        assert items[0]["variableType"] == "number"
        assert items[0]["initialValue"] == "0"
        assert items[0]["comment"] == "Player score"

        # Block second
        assert items[1]["type"] == "block"
        assert items[1]["conditions"][0]["id"] == "on-start-of-layout"
        assert items[1]["actions"][0]["id"] == "set-eventvar-value"
        assert items[1]["actions"][0]["parameters"] == {"0": "Score", "1": "0"}

        assert_valid(result, validator)

    def test_block_with_empty_params_omitted(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "events": [
                {
                    "conditions": [
                        {"id": "on-start-of-layout", "objectClass": "System", "parameters": {}}
                    ],
                    "actions": [
                        {"id": "stop", "objectClass": "System", "parameters": {}}
                    ],
                }
            ],
        }
        result = gen.from_ir(ir)
        block = result["items"][0]
        # Empty parameters dict must NOT be present
        assert "parameters" not in block["conditions"][0]
        assert "parameters" not in block["actions"][0]
        assert_valid(result, validator)

    def test_block_with_children(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "events": [
                {
                    "conditions": [
                        {"id": "is-greater-than", "objectClass": "System",
                         "parameters": {"0": "Score", "1": "10"}}
                    ],
                    "actions": [],
                    "children": [
                        {
                            "conditions": [
                                {"id": "on-start-of-layout", "objectClass": "System"}
                            ],
                            "actions": [
                                {"id": "stop", "objectClass": "System"}
                            ],
                        }
                    ],
                }
            ],
        }
        result = gen.from_ir(ir)
        block = result["items"][0]
        assert "children" in block
        assert block["children"][0]["type"] == "block"
        assert_valid(result, validator)

    def test_inverted_condition(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "events": [
                {
                    "conditions": [
                        {"id": "is-alive", "objectClass": "Player", "inverted": True}
                    ],
                    "actions": [],
                }
            ],
        }
        result = gen.from_ir(ir)
        cond = result["items"][0]["conditions"][0]
        assert cond.get("inverted") is True
        assert_valid(result, validator)

    def test_ordering_variables_before_events(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "variables": [{"name": "HP", "type": "number", "initialValue": "100", "comment": ""}],
            "events": [
                {
                    "conditions": [{"id": "on-start-of-layout", "objectClass": "System"}],
                    "actions": [],
                }
            ],
        }
        result = gen.from_ir(ir)
        assert result["items"][0]["type"] == "variable"
        assert result["items"][1]["type"] == "block"
        assert_valid(result, validator)


# ---------------------------------------------------------------------------
# test_from_ir_with_groups
# ---------------------------------------------------------------------------

class TestFromIRWithGroups:
    def test_group_wrapping_events(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "groups": [
                {
                    "title": "Movement",
                    "description": "Handles player movement",
                    "events": [
                        {
                            "conditions": [
                                {"id": "key-is-down", "objectClass": "Keyboard",
                                 "parameters": {"0": "37"}}
                            ],
                            "actions": [
                                {"id": "move-left", "objectClass": "Player"}
                            ],
                        }
                    ],
                }
            ],
        }
        result = gen.from_ir(ir)
        items = result["items"]
        assert len(items) == 1
        group = items[0]
        assert group["type"] == "group"
        assert group["title"] == "Movement"
        assert group["description"] == "Handles player movement"
        assert len(group["children"]) == 1
        assert group["children"][0]["type"] == "block"
        assert_valid(result, validator)

    def test_empty_group(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "groups": [
                {"title": "Empty Group", "description": "", "events": []}
            ],
        }
        result = gen.from_ir(ir)
        group = result["items"][0]
        assert group["type"] == "group"
        assert group["children"] == []
        assert_valid(result, validator)

    def test_multiple_groups(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "groups": [
                {
                    "title": "Group A",
                    "events": [
                        {
                            "conditions": [{"id": "on-start-of-layout", "objectClass": "System"}],
                            "actions": [],
                        }
                    ],
                },
                {
                    "title": "Group B",
                    "events": [],
                },
            ],
        }
        result = gen.from_ir(ir)
        assert result["items"][0]["title"] == "Group A"
        assert result["items"][1]["title"] == "Group B"
        assert_valid(result, validator)


# ---------------------------------------------------------------------------
# test_from_ir_with_function_blocks
# ---------------------------------------------------------------------------

class TestFromIRWithFunctionBlocks:
    def test_function_with_script_action(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "functions": [
                {
                    "name": "add",
                    "returnType": "number",
                    "parameters": [
                        {"name": "a", "type": "number", "initialValue": "0", "comment": ""},
                        {"name": "b", "type": "number", "initialValue": "0", "comment": ""},
                    ],
                    "actions": [
                        {
                            "type": "script",
                            "language": "javascript",
                            "script": ["return localVars.a + localVars.b;"],
                        }
                    ],
                    "description": "Adds two numbers",
                    "isAsync": False,
                }
            ],
        }
        result = gen.from_ir(ir)
        items = result["items"]
        assert len(items) == 1
        fb = items[0]
        assert fb["type"] == "function-block"
        assert fb["functionName"] == "add"
        assert fb["functionReturnType"] == "number"
        assert fb["isAsync"] is False
        assert fb["description"] == "Adds two numbers"

        # Script action
        script_act = fb["actions"][0]
        assert script_act["id"] == "run-script"
        assert script_act["language"] == "javascript"
        assert script_act["script"] == ["return localVars.a + localVars.b;"]

        assert_valid(result, validator)

    def test_async_function(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "functions": [
                {
                    "name": "fetchData",
                    "returnType": "any",
                    "parameters": [],
                    "actions": [],
                    "description": "",
                    "isAsync": True,
                }
            ],
        }
        result = gen.from_ir(ir)
        fb = result["items"][0]
        assert fb["isAsync"] is True
        assert fb["functionReturnType"] == "any"
        assert_valid(result, validator)

    def test_function_with_call_function_action(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "functions": [
                {
                    "name": "wrapper",
                    "returnType": "none",
                    "parameters": [],
                    "actions": [
                        {
                            "callFunction": "add",
                            "parameters": ["1", "2"],
                        }
                    ],
                    "description": "",
                    "isAsync": False,
                }
            ],
        }
        result = gen.from_ir(ir)
        act = result["items"][0]["actions"][0]
        assert act["callFunction"] == "add"
        assert act["parameters"] == ["1", "2"]
        assert_valid(result, validator)

    def test_function_no_parameters(self, gen, validator):
        ir = {
            "type": "event_sheet",
            "functions": [
                {
                    "name": "reset",
                    "returnType": "none",
                    "parameters": [],
                    "actions": [{"id": "stop", "objectClass": "System"}],
                    "description": "",
                    "isAsync": False,
                }
            ],
        }
        result = gen.from_ir(ir)
        fb = result["items"][0]
        # parameters key must not be present when empty (builder omits it)
        assert "parameters" not in fb
        assert_valid(result, validator)


# ---------------------------------------------------------------------------
# Full combined IR
# ---------------------------------------------------------------------------

class TestCombinedIR:
    def test_full_ir_ordering(self, gen, validator):
        """Variables → events → groups → functions, in that order."""
        ir = {
            "type": "event_sheet",
            "variables": [
                {"name": "Score", "type": "number", "initialValue": "0", "comment": ""}
            ],
            "events": [
                {
                    "conditions": [{"id": "on-start-of-layout", "objectClass": "System"}],
                    "actions": [],
                }
            ],
            "groups": [
                {"title": "G", "description": "", "events": []}
            ],
            "functions": [
                {
                    "name": "fn",
                    "returnType": "none",
                    "parameters": [],
                    "actions": [],
                    "description": "",
                    "isAsync": False,
                }
            ],
        }
        result = gen.from_ir(ir)
        items = result["items"]
        assert items[0]["type"] == "variable"
        assert items[1]["type"] == "block"
        assert items[2]["type"] == "group"
        assert items[3]["type"] == "function-block"
        assert_valid(result, validator)
