"""FastAPI application for Construct3-Clipboard service."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.generator.renderer import render_ir
from src.schemas.api import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ValidateRequest,
    ValidateResponse,
    ValidationInfo,
)
from src.validator.structural import StructuralValidator

app = FastAPI(title="Construct3-Clipboard", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    ir_dict = req.intent_ir.model_dump(exclude_none=True)
    result = render_ir(ir_dict, options=req.options)

    if not result.get("success"):
        return GenerateResponse(success=False, error=result.get("error"))

    validation_raw = result.get("validation", {})
    validation = ValidationInfo(
        passed=validation_raw.get("passed", True),
        errors=validation_raw.get("errors", []),
        warnings=validation_raw.get("warnings", []),
    )

    return GenerateResponse(
        success=True,
        clipboard_json=result.get("clipboard_json"),
        validation=validation,
        metadata=result.get("metadata"),
    )


@app.post("/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest) -> ValidateResponse:
    result = StructuralValidator().validate(req.clipboard_json)
    return ValidateResponse(
        passed=result.passed,
        errors=result.errors,
        warnings=result.warnings,
    )
