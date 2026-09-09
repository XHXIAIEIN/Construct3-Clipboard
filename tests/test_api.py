"""Tests for the FastAPI application endpoints."""
import pytest
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert data["service"] == "Construct3-Clipboard"


class TestValidate:
    def test_valid_events(self, valid_events_basic):
        resp = client.post("/validate", json={"clipboard_json": valid_events_basic})
        assert resp.status_code == 200
        data = resp.json()
        assert data["passed"] is True
        assert data["errors"] == []

    def test_invalid_json(self, invalid_missing_header):
        resp = client.post("/validate", json={"clipboard_json": invalid_missing_header})
        assert resp.status_code == 200
        data = resp.json()
        assert data["passed"] is False
        assert len(data["errors"]) > 0


class TestGenerate:
    def test_generate_events(self):
        payload = {
            "intent_ir": {
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
                            {"id": "on-start-of-layout", "objectClass": "System"},
                            {
                                "id": "is-timer-running",
                                "objectClass": "Player",
                                "behaviorType": "Timer",
                                "parameters": {"tag": "\"spawn\""},
                                "isInverted": True,
                            },
                        ],
                        "actions": [
                            {
                                "id": "set-eventvar-value",
                                "objectClass": "System",
                                "parameters": {"variable": "Score", "value": "0"},
                            }
                        ],
                    }
                ],
            }
        }
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True, data
        assert data["validation"]["passed"] is True
        items = data["clipboard_json"]["items"]
        assert items[0]["eventType"] == "variable"
        assert items[1]["conditions"][1]["isInverted"] is True
        assert items[1]["conditions"][1]["behaviorType"] == "Timer"

    def test_generate_object_types(self):
        payload = {
            "intent_ir": {
                "type": "object_types",
                "objects": [
                    {
                        "name": "Player",
                        "plugin": "Sprite",
                        "behaviors": [{"id": "Platform", "plugin-id": "Platform"}],
                    }
                ],
            }
        }
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["clipboard_json"] is not None

    def test_generate_unknown_type(self):
        payload = {
            "intent_ir": {
                "type": "totally_unknown_type",
            }
        }
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] is not None
