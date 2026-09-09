"""Tests for Node Builder — constructs valid C3 clipboard JSON nodes."""
import pytest
from src.generator.builder import (
    build_action,
    build_condition,
    build_variable,
    build_comment,
    build_group,
    build_block,
    build_script_action,
    build_function_block,
    build_function_parameter,
    wrap_clipboard,
)
from src.validator.structural import StructuralValidator


@pytest.fixture
def validator():
    return StructuralValidator()


# ---------------------------------------------------------------------------
# build_action
# ---------------------------------------------------------------------------

class TestBuildAction:
    def test_basic_action(self):
        act = build_action("set-value", "Player")
        assert act["id"] == "set-value"
        assert act["objectClass"] == "Player"
        assert "parameters" not in act  # omitted when None/empty

    def test_action_with_parameters(self):
        act = build_action("set-value", "Player", parameters={"0": 42})
        assert act["parameters"] == {"0": 42}

    def test_action_empty_params_omitted(self):
        act = build_action("set-value", "Player", parameters={})
        assert "parameters" not in act

    def test_action_none_params_omitted(self):
        act = build_action("set-value", "Player", parameters=None)
        assert "parameters" not in act

    def test_action_with_behavior_type(self):
        act = build_action("jump", "Player", behavior_type="Platform")
        assert act["behaviorType"] == "Platform"

    def test_action_without_behavior_type_omitted(self):
        act = build_action("set-value", "Player")
        assert "behaviorType" not in act


# ---------------------------------------------------------------------------
# build_condition
# ---------------------------------------------------------------------------

class TestBuildCondition:
    def test_basic_condition(self):
        cond = build_condition("is-overlapping", "Player")
        assert cond["id"] == "is-overlapping"
        assert cond["objectClass"] == "Player"
        assert "parameters" not in cond
        assert cond.get("isInverted", False) is False

    def test_condition_inverted(self):
        cond = build_condition("is-overlapping", "Player", inverted=True)
        assert cond["isInverted"] is True

    def test_condition_not_inverted_by_default(self):
        cond = build_condition("is-overlapping", "Player")
        # isInverted=False may be omitted entirely or set to False — both are fine
        assert cond.get("isInverted", False) is False

    def test_condition_with_parameters(self):
        cond = build_condition("compare", "Player", parameters={"0": 2})
        assert cond["parameters"] == {"0": 2}

    def test_condition_empty_params_omitted(self):
        cond = build_condition("always", "System", parameters={})
        assert "parameters" not in cond

    def test_condition_with_behavior_type(self):
        cond = build_condition("is-on-floor", "Player", behavior_type="Platform")
        assert cond["behaviorType"] == "Platform"


# ---------------------------------------------------------------------------
# build_variable
# ---------------------------------------------------------------------------

class TestBuildVariable:
    def test_default_variable(self):
        var = build_variable("score")
        assert var["eventType"] == "variable"
        assert var["name"] == "score"
        assert var["type"] == "number"
        assert var["initialValue"] == "0"
        assert "comment" in var  # always included

    def test_variable_with_all_args(self):
        var = build_variable("name", var_type="string", initial_value="Alice", comment="Player name")
        assert var["type"] == "string"
        assert var["initialValue"] == "Alice"
        assert var["comment"] == "Player name"

    def test_variable_empty_comment_included(self):
        var = build_variable("hp", comment="")
        assert "comment" in var
        assert var["comment"] == ""

    def test_variable_boolean_type(self):
        var = build_variable("alive", var_type="boolean", initial_value="true")
        assert var["type"] == "boolean"


# ---------------------------------------------------------------------------
# build_comment
# ---------------------------------------------------------------------------

class TestBuildComment:
    def test_basic_comment(self):
        c = build_comment("This is a comment")
        assert c["eventType"] == "comment"
        assert c["text"] == "This is a comment"

    def test_empty_comment(self):
        c = build_comment("")
        assert c["eventType"] == "comment"
        assert c["text"] == ""


# ---------------------------------------------------------------------------
# build_group
# ---------------------------------------------------------------------------

class TestBuildGroup:
    def test_basic_group(self):
        g = build_group("My Group")
        assert g["eventType"] == "group"
        assert g["title"] == "My Group"

    def test_group_defaults(self):
        g = build_group("G")
        assert g.get("description", "") == ""
        assert g.get("disabled", False) is False
        assert g.get("isActiveOnStart", True) is True

    def test_group_with_children(self):
        child = build_comment("child")
        g = build_group("G", children=[child])
        assert child in g["children"]

    def test_group_no_children_is_empty_list_or_omitted(self):
        g = build_group("G")
        # children may be omitted or empty list — either is acceptable
        children = g.get("children", [])
        assert isinstance(children, list)
        assert len(children) == 0

    def test_group_disabled(self):
        g = build_group("G", disabled=True)
        assert g["disabled"] is True

    def test_group_not_active_on_start(self):
        g = build_group("G", is_active_on_start=False)
        assert g["isActiveOnStart"] is False


# ---------------------------------------------------------------------------
# build_block
# ---------------------------------------------------------------------------

class TestBuildBlock:
    def test_basic_block(self):
        cond = build_condition("always", "System")
        act = build_action("wait", "System")
        b = build_block([cond], [act])
        assert b["eventType"] == "block"
        assert b["conditions"] == [cond]
        assert b["actions"] == [act]

    def test_block_empty_conditions_and_actions(self):
        b = build_block([], [])
        assert b["eventType"] == "block"
        assert b["conditions"] == []
        assert b["actions"] == []

    def test_block_with_children(self):
        child_block = build_block([], [])
        b = build_block([], [], children=[child_block])
        assert child_block in b["children"]

    def test_block_no_children_omitted_or_empty(self):
        b = build_block([], [])
        children = b.get("children", [])
        assert isinstance(children, list)
        assert len(children) == 0


# ---------------------------------------------------------------------------
# build_script_action
# ---------------------------------------------------------------------------

class TestBuildScriptAction:
    def test_basic_script(self):
        act = build_script_action(["console.log('hi');"])
        assert act["script"] == ["console.log('hi');"]
        assert act["language"] == "javascript"

    def test_typescript_language(self):
        act = build_script_action(["const x: number = 1;"], language="typescript")
        assert act["language"] == "typescript"

    def test_multiline_script(self):
        lines = ["let x = 1;", "let y = 2;", "runtime.objects.Player.getFirstInstance().x = x + y;"]
        act = build_script_action(lines)
        assert act["script"] == lines

    def test_script_has_required_id_fields(self):
        act = build_script_action([""])
        # Script actions use type="script" as their identifier (not "id")
        assert act.get("type") == "script" or "id" in act


# ---------------------------------------------------------------------------
# build_function_block
# ---------------------------------------------------------------------------

class TestBuildFunctionBlock:
    def test_basic_function_block(self):
        fb = build_function_block("DoThing")
        assert fb["eventType"] == "function-block"
        assert fb["functionName"] == "DoThing"
        assert fb["functionReturnType"] == "none"
        assert isinstance(fb["conditions"], list)
        assert isinstance(fb["actions"], list)

    def test_function_block_with_return_type(self):
        fb = build_function_block("GetScore", return_type="number")
        assert fb["functionReturnType"] == "number"

    def test_function_block_with_conditions_and_actions(self):
        cond = build_condition("always", "System")
        act = build_action("set-value", "Player")
        fb = build_function_block("MyFunc", conditions=[cond], actions=[act])
        assert cond in fb["conditions"]
        assert act in fb["actions"]

    def test_function_block_async(self):
        fb = build_function_block("AsyncFunc", is_async=True)
        assert fb["functionIsAsync"] is True

    def test_function_block_with_description(self):
        fb = build_function_block("Func", description="Does stuff")
        assert fb["functionDescription"] == "Does stuff"

    def test_function_block_with_parameters(self):
        params = [build_function_parameter("x", "number", "0", "")]
        fb = build_function_block("Add", parameters=params)
        assert fb["functionParameters"] == [
            {"name": "x", "type": "number", "initialValue": "0", "comment": ""}
        ]

    def test_function_block_keys_match_editor_output(self):
        fb = build_function_block("Func")
        assert list(fb.keys()) == [
            "functionName", "functionDescription", "functionCategory",
            "functionReturnType", "functionCopyPicked", "functionIsAsync",
            "functionParameters", "eventType", "conditions", "actions",
        ]
        assert fb["functionParameters"] == []
        assert fb["functionCopyPicked"] is False
        assert fb["functionCategory"] == ""


# ---------------------------------------------------------------------------
# wrap_clipboard
# ---------------------------------------------------------------------------

class TestWrapClipboard:
    def test_wrap_events(self):
        var = build_variable("score", comment="test")
        wrapped = wrap_clipboard("events", [var])
        assert wrapped["is-c3-clipboard-data"] is True
        assert wrapped["type"] == "events"
        assert wrapped["items"] == [var]

    def test_wrap_object_types(self):
        obj = {
            "plugin-id": "Sprite",
            "animations": [],
            "behaviorTypes": [],
            "effectTypes": [],
            "instanceVariables": []
        }
        wrapped = wrap_clipboard("object-types", [obj])
        assert wrapped["type"] == "object-types"

    def test_wrap_extra_fields(self):
        wrapped = wrap_clipboard("events", [], version=1)
        assert wrapped.get("version") == 1

    def test_wrap_empty_items(self):
        wrapped = wrap_clipboard("actions", [])
        assert wrapped["items"] == []


# ---------------------------------------------------------------------------
# Integration: builders produce validator-approved output
# ---------------------------------------------------------------------------

class TestBuilderOutputPassesValidator:
    def test_events_clipboard_passes(self, validator):
        var = build_variable("score", comment="Player score")
        cond = build_condition("always", "System")
        # Use a string-valued param to avoid the comparison operator check
        act = build_action("set-value", "Player", parameters={"value": "100"})
        block = build_block([cond], [act])
        wrapped = wrap_clipboard("events", [var, block])
        result = validator.validate(wrapped)
        assert result.passed is True, f"Errors: {result.errors}"

    def test_object_types_clipboard_passes(self, validator):
        obj = {
            "plugin-id": "Sprite",
            "animations": [],
            "behaviorTypes": [],
            "effectTypes": [],
            "instanceVariables": []
        }
        wrapped = wrap_clipboard("object-types", [obj])
        result = validator.validate(wrapped)
        assert result.passed is True, f"Errors: {result.errors}"

    def test_function_block_clipboard_passes(self, validator):
        fb = build_function_block("CalcScore", return_type="number", conditions=[], actions=[])
        wrapped = wrap_clipboard("events", [fb])
        result = validator.validate(wrapped)
        assert result.passed is True, f"Errors: {result.errors}"

    def test_script_action_in_block_passes(self, validator):
        script_act = build_script_action(["runtime.callFunction('Init');"])
        block = build_block([], [script_act])
        wrapped = wrap_clipboard("events", [block])
        result = validator.validate(wrapped)
        assert result.passed is True, f"Errors: {result.errors}"
