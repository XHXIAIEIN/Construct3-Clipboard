"""Structural validator for Construct 3 clipboard JSON.

Validates clipboard format rules that do NOT require ACE schema data.
Returns a ValidationResult with errors (blocking) and warnings (advisory).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CLIPBOARD_TYPES = {
    "events",
    "conditions",
    "actions",
    "object-types",
    "world-instances",
    "layouts",
    "event-sheets",
    "timelines",
}

VALID_EVENT_TYPES = {
    "comment", "variable", "group", "block", "function-block",
    "include", "custom-ace-block",
}
VALID_VARIABLE_TYPES = {"number", "string", "boolean"}
VALID_FUNCTION_RETURN_TYPES = {"none", "number", "string", "any"}
VALID_SCRIPT_LANGUAGES = {"javascript", "typescript"}
COMPARISON_OPERATOR_RANGE = range(6)  # 0-5 inclusive


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class StructuralValidator:
    """Validate C3 clipboard JSON structure without ACE schema data."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        self._check_header(data, result)
        clip_type = self._check_type(data, result)
        items = self._check_items(data, result)

        if result.passed and items is not None and clip_type is not None:
            self._validate_items(items, clip_type, result)

        return result

    # ------------------------------------------------------------------
    # Top-level field checks
    # ------------------------------------------------------------------

    def _check_header(self, data: dict, result: ValidationResult) -> None:
        if "is-c3-clipboard-data" not in data:
            result.add_error("Missing required field: is-c3-clipboard-data")
        elif data["is-c3-clipboard-data"] is not True:
            result.add_error("Field is-c3-clipboard-data must be true")

    def _check_type(self, data: dict, result: ValidationResult) -> str | None:
        if "type" not in data:
            result.add_error("Missing required field: type")
            return None
        clip_type = data["type"]
        if clip_type not in VALID_CLIPBOARD_TYPES:
            result.add_error(
                f"Invalid clipboard type '{clip_type}'. "
                f"Must be one of: {sorted(VALID_CLIPBOARD_TYPES)}"
            )
            return None
        return clip_type

    def _check_items(self, data: dict, result: ValidationResult) -> list | None:
        if "items" not in data:
            result.add_error("Missing required field: items")
            return None
        items = data["items"]
        if not isinstance(items, list):
            result.add_error("Field 'items' must be an array")
            return None
        return items

    # ------------------------------------------------------------------
    # Item dispatch
    # ------------------------------------------------------------------

    def _validate_items(
        self, items: list, clip_type: str, result: ValidationResult
    ) -> None:
        for idx, item in enumerate(items):
            prefix = f"Item[{idx}]"
            if clip_type in ("events", "conditions", "actions"):
                self._validate_event_item(item, prefix, result)
            elif clip_type == "object-types":
                self._validate_object_type(item, prefix, result)
            elif clip_type == "layouts":
                self._validate_layout(item, prefix, result)
            elif clip_type == "timelines":
                self._validate_timeline(item, prefix, result)
            # world-instances / event-sheets: basic existence checks only for now

    # ------------------------------------------------------------------
    # Event item validation
    # ------------------------------------------------------------------

    def _validate_event_item(
        self, item: Any, prefix: str, result: ValidationResult
    ) -> None:
        if not isinstance(item, dict):
            result.add_error(f"{prefix}: event item must be an object")
            return

        event_type = item.get("eventType")
        if event_type is None:
            result.add_error(f"{prefix}: missing 'eventType' field")
            return
        if event_type not in VALID_EVENT_TYPES:
            result.add_error(
                f"{prefix}: invalid eventType '{event_type}'. "
                f"Must be one of: {sorted(VALID_EVENT_TYPES)}"
            )
            return

        if event_type == "variable":
            self._validate_variable(item, prefix, result)
        elif event_type == "block":
            self._validate_block(item, prefix, result)
        elif event_type == "function-block":
            self._validate_function_block(item, prefix, result)
        elif event_type == "custom-ace-block":
            self._validate_custom_ace_block(item, prefix, result)
        elif event_type == "group":
            self._validate_group(item, prefix, result)
        elif event_type == "include":
            self._validate_include(item, prefix, result)
        # comment: no further required fields

        self._validate_children(item, prefix, result)

    def _validate_children(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        children = item.get("children")
        if children is None:
            return
        if not isinstance(children, list):
            result.add_error(f"{prefix}: 'children' must be an array")
            return
        for idx, child in enumerate(children):
            self._validate_event_item(child, f"{prefix}.children[{idx}]", result)

    def _check_bool(
        self, item: dict, key: str, prefix: str, result: ValidationResult
    ) -> None:
        if key in item and not isinstance(item[key], bool):
            result.add_error(
                f"{prefix}: '{key}' must be a boolean, got {type(item[key]).__name__}"
            )

    def _validate_variable(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        if "name" not in item or not item["name"]:
            result.add_error(f"{prefix} (variable): missing required field 'name'")
        if "comment" not in item:
            result.add_warning(
                f"{prefix} (variable '{item.get('name', '?')}'): "
                "missing 'comment' field — variable definitions should include a comment"
            )
        var_type = item.get("type")
        if var_type and var_type not in VALID_VARIABLE_TYPES:
            result.add_error(
                f"{prefix} (variable): invalid type '{var_type}'. "
                f"Must be one of: {sorted(VALID_VARIABLE_TYPES)}"
            )
        self._check_bool(item, "isStatic", f"{prefix} (variable)", result)
        self._check_bool(item, "isConstant", f"{prefix} (variable)", result)

    def _validate_conditions_actions(
        self, item: dict, prefix: str, label: str, result: ValidationResult, *, required: bool
    ) -> None:
        for key in ("conditions", "actions"):
            if key not in item:
                if required:
                    result.add_error(f"{prefix} ({label}): missing required field '{key}'")
                continue
            entries = item[key]
            if not isinstance(entries, list):
                result.add_error(f"{prefix} ({label}): '{key}' must be an array")
                continue
            singular = key[:-1]
            for idx, entry in enumerate(entries):
                self._validate_ace_entry(entry, f"{prefix} {singular}[{idx}]", result)

    def _validate_block(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        self._check_bool(item, "isOrBlock", f"{prefix} (block)", result)
        self._validate_conditions_actions(item, prefix, "block", result, required=True)

    def _validate_function_block(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        if "functionName" not in item or not item["functionName"]:
            result.add_error(
                f"{prefix} (function-block): missing required field 'functionName'"
            )
        self._validate_function_return_type(item, f"{prefix} (function-block)", result)
        self._validate_conditions_actions(item, prefix, "function-block", result, required=False)

    def _validate_custom_ace_block(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        label = f"{prefix} (custom-ace-block)"
        for key in ("aceType", "aceName", "objectClass"):
            if not item.get(key):
                result.add_error(f"{label}: missing required field '{key}'")
        if "functionReturnType" in item:
            self._validate_function_return_type(item, label, result)
        self._validate_conditions_actions(item, prefix, "custom-ace-block", result, required=False)

    def _validate_function_return_type(
        self, item: dict, label: str, result: ValidationResult
    ) -> None:
        return_type = item.get("functionReturnType")
        if return_type is None:
            result.add_error(f"{label}: missing required field 'functionReturnType'")
        elif return_type not in VALID_FUNCTION_RETURN_TYPES:
            result.add_error(
                f"{label}: invalid functionReturnType '{return_type}'. "
                f"Must be one of: {sorted(VALID_FUNCTION_RETURN_TYPES)}"
            )

    def _validate_group(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        # groups should have a title, but treat it as advisory
        if "title" not in item:
            result.add_warning(f"{prefix} (group): missing 'title' field")

    def _validate_include(
        self, item: dict, prefix: str, result: ValidationResult
    ) -> None:
        if not item.get("includeSheet"):
            result.add_error(f"{prefix} (include): missing required field 'includeSheet'")

    # ------------------------------------------------------------------
    # ACE entry (condition / action) validation
    # ------------------------------------------------------------------

    def _validate_ace_entry(
        self, entry: Any, prefix: str, result: ValidationResult
    ) -> None:
        if not isinstance(entry, dict):
            result.add_error(f"{prefix}: must be an object")
            return

        # Comment inside an actions array: {"type": "comment", "text": "..."}
        if entry.get("type") == "comment":
            if not isinstance(entry.get("text"), str):
                result.add_error(f"{prefix}: comment must have a string 'text' field")
            return

        # Check for script action pattern
        if "script" in entry or "language" in entry:
            self._validate_script_ace(entry, prefix, result)
            return

        self._check_bool(entry, "isInverted", prefix, result)

        # Check parameters
        params = entry.get("parameters")
        if params is not None:
            if isinstance(params, dict):
                if len(params) == 0:
                    result.add_warning(
                        f"{prefix}: empty 'parameters: {{}}' should be omitted"
                    )
                else:
                    # Check comparison operators: parameter key "0" is the operator
                    # for comparison conditions
                    for key, val in params.items():
                        if key == "0" and isinstance(val, int):
                            if val not in COMPARISON_OPERATOR_RANGE:
                                result.add_error(
                                    f"{prefix}: invalid comparison operator value {val}. "
                                    "Must be 0-5"
                                )

    def _validate_script_ace(
        self, entry: dict, prefix: str, result: ValidationResult
    ) -> None:
        """Validate a script action (run-script ACE)."""
        language = entry.get("language")
        script = entry.get("script")

        if language is None:
            result.add_error(
                f"{prefix}: script action missing required field 'language' "
                f"(must be one of: {sorted(VALID_SCRIPT_LANGUAGES)})"
            )
        elif language not in VALID_SCRIPT_LANGUAGES:
            result.add_error(
                f"{prefix}: invalid script language '{language}'. "
                f"Must be one of: {sorted(VALID_SCRIPT_LANGUAGES)}"
            )

        if script is None:
            result.add_error(f"{prefix}: script action missing required field 'script'")
        elif not isinstance(script, list):
            result.add_error(
                f"{prefix}: 'script' must be an array of strings, got {type(script).__name__}"
            )

    # ------------------------------------------------------------------
    # Object type validation
    # ------------------------------------------------------------------

    def _validate_object_type(
        self, item: Any, prefix: str, result: ValidationResult
    ) -> None:
        if not isinstance(item, dict):
            result.add_error(f"{prefix}: object-type item must be an object")
            return

        if "plugin-id" not in item:
            result.add_error(f"{prefix}: missing required field 'plugin-id'")

        # effectTypes must be array
        effect_types = item.get("effectTypes")
        if effect_types is not None and not isinstance(effect_types, list):
            result.add_error(
                f"{prefix}: 'effectTypes' must be an array, not {type(effect_types).__name__}"
            )

        # instanceVariables must be array
        inst_vars = item.get("instanceVariables")
        if inst_vars is not None and not isinstance(inst_vars, list):
            result.add_error(
                f"{prefix}: 'instanceVariables' must be an array, "
                f"not {type(inst_vars).__name__}"
            )

        # behaviorTypes must be array
        behavior_types = item.get("behaviorTypes")
        if behavior_types is not None and not isinstance(behavior_types, list):
            result.add_error(
                f"{prefix}: 'behaviorTypes' must be an array, "
                f"not {type(behavior_types).__name__}"
            )

        # imageData must be PNG data URI if present
        image_data = item.get("imageData")
        if image_data is not None:
            if not isinstance(image_data, str) or not image_data.startswith(
                "data:image/png;"
            ):
                result.add_error(
                    f"{prefix}: 'imageData' must be a PNG data URI "
                    "(e.g. 'data:image/png;base64,...')"
                )

    # ------------------------------------------------------------------
    # Layout validation
    # ------------------------------------------------------------------

    def _validate_layout(
        self, item: Any, prefix: str, result: ValidationResult
    ) -> None:
        if not isinstance(item, dict):
            result.add_error(f"{prefix}: layout item must be an object")
            return

        if "layers" not in item:
            result.add_error(f"{prefix}: layout missing required field 'layers'")
        else:
            layers = item["layers"]
            if not isinstance(layers, list):
                result.add_error(f"{prefix}: 'layers' must be an array")

    # ------------------------------------------------------------------
    # Timeline validation
    # ------------------------------------------------------------------

    def _validate_timeline(
        self, item: Any, prefix: str, result: ValidationResult
    ) -> None:
        if not isinstance(item, dict):
            result.add_error(f"{prefix}: timeline item must be an object")
            return

        if not item.get("name"):
            result.add_error(f"{prefix}: timeline missing required field 'name'")

        if "tracks" not in item:
            result.add_error(f"{prefix}: timeline missing required field 'tracks'")
        elif not isinstance(item["tracks"], list):
            result.add_error(f"{prefix}: 'tracks' must be an array")
