"""Shared pytest fixtures for Construct3-Clipboard tests."""
import pytest


@pytest.fixture
def valid_events_basic():
    """A minimal valid events clipboard with a variable and a block."""
    return {
        "is-c3-clipboard-data": True,
        "type": "events",
        "items": [
            {
                "type": "variable",
                "name": "score",
                "variableType": "number",
                "initialValue": "0",
                "comment": "Player score"
            },
            {
                "type": "block",
                "conditions": [
                    {
                        "id": "is-overlapping",
                        "objectClass": "Player"
                    }
                ],
                "actions": [
                    {
                        "id": "set-value",
                        "objectClass": "Player"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def valid_object_types():
    """A valid object-types clipboard with a Sprite with Platform behavior."""
    return {
        "is-c3-clipboard-data": True,
        "type": "object-types",
        "items": [
            {
                "plugin-id": "Sprite",
                "animations": [],
                "behaviorTypes": [
                    {
                        "id": "Platform",
                        "plugin-id": "Platform"
                    }
                ],
                "effectTypes": [],
                "instanceVariables": []
            }
        ]
    }


@pytest.fixture
def invalid_missing_header():
    """Clipboard missing the required is-c3-clipboard-data field."""
    return {
        "type": "events",
        "items": []
    }


@pytest.fixture
def invalid_empty_parameters():
    """A block containing an action with empty parameters dict — should warn."""
    return {
        "is-c3-clipboard-data": True,
        "type": "events",
        "items": [
            {
                "type": "block",
                "conditions": [
                    {
                        "id": "always",
                        "objectClass": "System"
                    }
                ],
                "actions": [
                    {
                        "id": "set-value",
                        "objectClass": "Player",
                        "parameters": {}
                    }
                ]
            }
        ]
    }
