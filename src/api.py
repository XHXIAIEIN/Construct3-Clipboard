"""FastAPI application for Construct3-Clipboard service."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import ERRORS_DIR
from src.errors.notebook import ErrorNotebook
from src.generator.renderer import render_ir
from src.schemas.api import (
    ErrorReportRequest,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ValidateRequest,
    ValidateResponse,
    ValidationInfo,
)
from src.validator.structural import VALID_CLIPBOARD_TYPES, StructuralValidator

app = FastAPI(title="Construct3-Clipboard", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notebook = ErrorNotebook(ERRORS_DIR)


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

    if not result.passed:
        notebook.report(
            source="validation_catch",
            error_message="; ".join(result.errors[:3]),
            error_type="validation_failure",
            bad_json=req.clipboard_json,
        )

    return ValidateResponse(
        passed=result.passed,
        errors=result.errors,
        warnings=result.warnings,
    )


@app.get("/format-spec")
def format_spec() -> dict:
    return {
        "valid_types": sorted(VALID_CLIPBOARD_TYPES),
        "event_types": sorted(["comment", "variable", "group", "block", "function-block"]),
        "variable_types": sorted(["number", "string", "boolean"]),
        "comparison_operators": {
            "0": "equal",
            "1": "not_equal",
            "2": "less",
            "3": "less_or_equal",
            "4": "greater",
            "5": "greater_or_equal",
        },
        "parameter_rules": {
            "empty_parameters": "omit {} entirely",
            "comparison_operator": "key '0' with int value 0-5",
        },
    }


@app.post("/errors/report")
def report_error(req: ErrorReportRequest) -> dict:
    entry_id = notebook.report(
        source=req.source,
        error_message=req.error_message,
        error_type=req.error_type,
        input_ir=req.input_ir,
        bad_json=req.bad_json,
    )
    return {"id": entry_id}


@app.get("/errors/pending")
def errors_pending() -> list:
    return notebook.get_pending()


@app.get("/errors/stats")
def errors_stats() -> dict:
    return notebook.get_stats()
