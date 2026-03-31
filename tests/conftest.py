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
                "eventType": "variable",
                "name": "Score",
                "type": "number",
                "initialValue": "0",
                "comment": "Player score",
            },
            {
                "eventType": "block",
                "conditions": [
                    {"id": "on-start-of-layout", "objectClass": "System"}
                ],
                "actions": [
                    {
                        "id": "set-eventvar-value",
                        "objectClass": "System",
                        "parameters": {"variable": "Score", "value": "0"},
                    }
                ],
            },
        ],
    }


@pytest.fixture
def valid_object_types():
    """A valid object-types clipboard with a Sprite with Platform behavior."""
    return {
        "is-c3-clipboard-data": True,
        "type": "object-types",
        "items": [
            {
                "name": "Player",
                "plugin-id": "Sprite",
                "isGlobal": False,
                "editorNewInstanceIsReplica": True,
                "instanceVariables": [],
                "behaviorTypes": [{"behaviorId": "Platform", "name": "Platform"}],
                "effectTypes": [],
                "animations": {
                    "items": [
                        {
                            "frames": [
                                {
                                    "width": 32,
                                    "height": 32,
                                    "originX": 0.5,
                                    "originY": 0.5,
                                    "imageDataIndex": 0,
                                }
                            ],
                            "name": "Default",
                        }
                    ],
                    "subfolders": [],
                },
            }
        ],
        "families": [],
        "folders": [],
    }


@pytest.fixture
def invalid_missing_header():
    """Clipboard missing the required is-c3-clipboard-data field."""
    return {"type": "events", "items": []}


@pytest.fixture
def invalid_empty_parameters():
    """A block containing an action with empty parameters dict — should warn."""
    return {
        "is-c3-clipboard-data": True,
        "type": "events",
        "items": [
            {
                "eventType": "block",
                "conditions": [{"id": "every-tick", "objectClass": "System"}],
                "actions": [
                    {
                        "id": "destroy",
                        "objectClass": "Enemy",
                        "parameters": {},
                    }
                ],
            }
        ],
    }
