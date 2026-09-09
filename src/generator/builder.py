"""Node Builder for Construct 3 clipboard JSON.

Low-level factory functions that construct valid clipboard JSON nodes.
Every builder enforces schema rules by construction — invalid output is
impossible if you use these functions.
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# ACE nodes (conditions / actions)
# ---------------------------------------------------------------------------

def build_action(
    ace_id: str,
    object_class: str,
    *,
    parameters: dict[str, Any] | None = None,
    behavior_type: str | None = None,
) -> dict:
    """Build a single action node.

    Parameters are omitted entirely if None or empty (C3 schema rule).
    """
    node: dict[str, Any] = {
        "id": ace_id,
        "objectClass": object_class,
    }
    if parameters:  # omit if None or empty dict
        node["parameters"] = parameters
    if behavior_type is not None:
        node["behaviorType"] = behavior_type
    return node


def build_condition(
    ace_id: str,
    object_class: str,
    *,
    parameters: dict[str, Any] | None = None,
    behavior_type: str | None = None,
    inverted: bool = False,
) -> dict:
    """Build a single condition node.

    The editor writes ``isInverted`` only when it is true, so the field is
    omitted for the default.
    """
    node: dict[str, Any] = {
        "id": ace_id,
        "objectClass": object_class,
    }
    if parameters:  # omit if None or empty dict
        node["parameters"] = parameters
    if behavior_type is not None:
        node["behaviorType"] = behavior_type
    if inverted:
        node["isInverted"] = True
    return node


# ---------------------------------------------------------------------------
# Event nodes
# ---------------------------------------------------------------------------

def build_variable(
    name: str,
    var_type: str = "number",
    initial_value: str = "0",
    comment: str = "",
) -> dict:
    """Build a variable definition node.

    Always includes the `comment` field (even if empty) to satisfy the
    structural validator's rule that variable definitions should have a comment.
    """
    return {
        "eventType": "variable",
        "name": name,
        "type": var_type,
        "initialValue": initial_value,
        "comment": comment,
    }


def build_comment(text: str) -> dict:
    """Build a comment event node."""
    return {
        "eventType": "comment",
        "text": text,
    }


def build_group(
    title: str,
    *,
    children: list[dict] | None = None,
    description: str = "",
    disabled: bool = False,
    is_active_on_start: bool = True,
) -> dict:
    """Build a group event node."""
    node: dict[str, Any] = {
        "eventType": "group",
        "title": title,
        "description": description,
        "disabled": disabled,
        "isActiveOnStart": is_active_on_start,
        "children": list(children) if children else [],
    }
    return node


def build_block(
    conditions: list[dict],
    actions: list[dict],
    *,
    children: list[dict] | None = None,
) -> dict:
    """Build an event block node (conditions + actions)."""
    node: dict[str, Any] = {
        "eventType": "block",
        "conditions": list(conditions),
        "actions": list(actions),
    }
    if children:
        node["children"] = list(children)
    return node


def build_script_action(
    lines: list[str],
    language: str = "javascript",
) -> dict:
    """Build a 'run script' action node.

    Args:
        lines: Lines of script code as a list of strings.
        language: 'javascript' (default) or 'typescript'.
    """
    return {
        "type": "script",
        "language": language,
        "script": list(lines),
    }


def build_function_parameter(
    name: str,
    var_type: str = "number",
    initial_value: str = "0",
    comment: str = "",
) -> dict:
    """Build one entry of a function block's ``functionParameters`` list."""
    return {
        "name": name,
        "type": var_type,
        "initialValue": initial_value,
        "comment": comment,
    }


def build_function_block(
    name: str,
    *,
    return_type: str = "none",
    parameters: list[dict] | None = None,
    conditions: list[dict] | None = None,
    actions: list[dict] | None = None,
    description: str = "",
    category: str = "",
    copy_picked: bool = False,
    is_async: bool = False,
) -> dict:
    """Build a function-block event node.

    Field names and order follow editor output: the ``function*`` fields
    come first and ``eventType`` after them.

    Args:
        name: Function name (functionName).
        return_type: One of 'none', 'number', 'string', 'any'.
        parameters: Parameter definitions from :func:`build_function_parameter`.
        conditions: Conditions inside the function block.
        actions: Actions inside the function block.
        description: Human-readable description (functionDescription).
        category: Category shown in the editor (functionCategory).
        copy_picked: Whether the function copies picked instances (functionCopyPicked).
        is_async: Whether the function is async (functionIsAsync).
    """
    return {
        "functionName": name,
        "functionDescription": description,
        "functionCategory": category,
        "functionReturnType": return_type,
        "functionCopyPicked": copy_picked,
        "functionIsAsync": is_async,
        "functionParameters": list(parameters) if parameters else [],
        "eventType": "function-block",
        "conditions": list(conditions) if conditions is not None else [],
        "actions": list(actions) if actions is not None else [],
    }


# ---------------------------------------------------------------------------
# Clipboard envelope
# ---------------------------------------------------------------------------

def wrap_clipboard(
    clip_type: str,
    items: list[dict],
    **extra: Any,
) -> dict:
    """Wrap items in a C3 clipboard envelope.

    Args:
        clip_type: One of the valid clipboard type strings.
        items: The payload items array.
        **extra: Additional top-level fields to include in the envelope.
    """
    envelope: dict[str, Any] = {
        "is-c3-clipboard-data": True,
        "type": clip_type,
        "items": list(items),
    }
    envelope.update(extra)
    return envelope
