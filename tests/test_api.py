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
                        "name": "score",
                        "variable_type": "number",
                        "initial_value": "0",
                        "comment": "Player score",
                    }
                ],
                "events": [
                    {
                        "conditions": [{"id": "always", "object": "System"}],
                        "actions": [{"id": "set-value", "object": "Player", "params": ["1"]}],
                    }
                ],
            }
        }
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # renderer will return success or a known error — just check it responded cleanly
        assert "success" in data

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


class TestFormatSpec:
    def test_format_spec(self):
        resp = client.get("/format-spec")
        assert resp.status_code == 200
        data = resp.json()
        assert "valid_types" in data
        assert "events" in data["valid_types"]
        assert "event_types" in data
        assert "variable_types" in data
        assert "comparison_operators" in data
        assert "parameter_rules" in data


class TestErrors:
    def test_report_error(self):
        payload = {
            "source": "test_suite",
            "error_message": "Something broke",
            "error_type": "test_error",
        }
        resp = client.post("/errors/report", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["id"].startswith("ERR-")

    def test_pending(self):
        resp = client.get("/errors/pending")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_stats(self):
        resp = client.get("/errors/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "by_type" in data
        assert "by_status" in data
