"""Event Sheet Generator for Construct 3 clipboard JSON.

Converts Intent IR (a structured dict describing an event sheet) into
clipboard-ready event blocks using the low-level builder primitives.
"""
from __future__ import annotations

from typing import Any

from src.generator.builder import (
    build_action,
    build_block,
    build_condition,
    build_function_block,
    build_group,
    build_script_action,
    build_variable,
    wrap_clipboard,
)


class EventSheetGenerator:
    """Convert an Intent IR dict to a Construct 3 clipboard events JSON."""

    def from_ir(self, ir: dict) -> dict:
        """Convert Intent IR to clipboard events JSON.

        Processing order:
          1. Variables
          2. Top-level events (as blocks)
          3. Grouped events
          4. Functions
        """
        items: list[dict] = []

        for var in ir.get("variables", []):
            items.append(self._build_variable_node(var))

        for event in ir.get("events", []):
            items.append(self._build_event_node(event))

        for group in ir.get("groups", []):
            items.append(self._build_group_node(group))

        for func in ir.get("functions", []):
            items.append(self._build_function_node(func))

        return wrap_clipboard("events", items)

    # ------------------------------------------------------------------
    # Variable
    # ------------------------------------------------------------------

    def _build_variable_node(self, var: dict) -> dict:
        return build_variable(
            name=var["name"],
            var_type=var.get("type", "number"),
            initial_value=var.get("initialValue", "0"),
            comment=var.get("comment", ""),
        )

    # ------------------------------------------------------------------
    # Event block
    # ------------------------------------------------------------------

    def _build_event_node(self, event: dict) -> dict:
        conditions = [
            self._build_condition_node(c) for c in event.get("conditions", [])
        ]
        actions = [
            self._build_action_node(a) for a in event.get("actions", [])
        ]
        children: list[dict] | None = None
        if event.get("children"):
            children = [self._build_event_node(child) for child in event["children"]]
        return build_block(conditions, actions, children=children)

    def _build_condition_node(self, cond: dict) -> dict:
        params = cond.get("parameters") or None
        if params == {}:
            params = None
        return build_condition(
            ace_id=cond["id"],
            object_class=cond["objectClass"],
            parameters=params,
            behavior_type=cond.get("behaviorType"),
            inverted=cond.get("isInverted", cond.get("inverted", False)),
        )

    def _build_action_node(self, action: dict) -> dict:
        # Script action
        if action.get("type") == "script":
            return build_script_action(
                lines=action.get("script", []),
                language=action.get("language", "javascript"),
            )

        # Function call pass-through
        if "callFunction" in action:
            node: dict[str, Any] = {"callFunction": action["callFunction"]}
            if action.get("parameters"):
                node["parameters"] = action["parameters"]
            return node

        # Regular action
        params = action.get("parameters") or None
        if params == {}:
            params = None
        return build_action(
            ace_id=action["id"],
            object_class=action["objectClass"],
            parameters=params,
            behavior_type=action.get("behaviorType"),
        )

    # ------------------------------------------------------------------
    # Group
    # ------------------------------------------------------------------

    def _build_group_node(self, group: dict) -> dict:
        children = [self._build_event_node(e) for e in group.get("events", [])]
        return build_group(
            title=group.get("title", ""),
            children=children,
            description=group.get("description", ""),
        )

    # ------------------------------------------------------------------
    # Function block
    # ------------------------------------------------------------------

    def _build_function_node(self, func: dict) -> dict:
        params: list[dict] | None = None
        if func.get("parameters"):
            params = [
                build_variable(
                    name=p["name"],
                    var_type=p.get("type", "number"),
                    initial_value=p.get("initialValue", "0"),
                    comment=p.get("comment", ""),
                )
                for p in func["parameters"]
            ]

        actions = [self._build_action_node(a) for a in func.get("actions", [])]

        return build_function_block(
            name=func["name"],
            return_type=func.get("returnType", "none"),
            parameters=params,
            actions=actions,
            description=func.get("description", ""),
            is_async=func.get("isAsync", False),
        )
