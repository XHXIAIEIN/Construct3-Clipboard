"""Intent IR input model."""
from __future__ import annotations
from pydantic import BaseModel


class IntentIR(BaseModel):
    type: str  # "event_sheet" | "object_types"
    variables: list[dict] | None = None
    events: list[dict] | None = None
    groups: list[dict] | None = None
    functions: list[dict] | None = None
    objects: list[dict] | None = None
    model_config = {"extra": "allow"}
