"""API request/response models."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from src.schemas.intent_ir import IntentIR


class GenerateRequest(BaseModel):
    intent_ir: IntentIR
    ace_context: dict[str, Any] | None = None
    options: dict[str, Any] | None = None


class ValidationInfo(BaseModel):
    passed: bool
    errors: list[str] = []
    warnings: list[str] = []


class GenerateResponse(BaseModel):
    success: bool
    clipboard_json: dict[str, Any] | None = None
    validation: ValidationInfo | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None


class ValidateRequest(BaseModel):
    clipboard_json: dict[str, Any]


class ValidateResponse(BaseModel):
    passed: bool
    errors: list[str] = []
    warnings: list[str] = []


class HealthResponse(BaseModel):
    status: str
    service: str = "Construct3-Clipboard"
    version: str = "0.1.0"


class ErrorReportRequest(BaseModel):
    source: str = "user_report"
    input_ir: dict[str, Any] | None = None
    bad_json: dict[str, Any] | None = None
    error_message: str = ""
    error_type: str = ""
