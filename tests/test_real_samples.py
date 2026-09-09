"""Every editor capture under docs/samples must pass the structural validator.

The second half reproduces the Scirra samples listed in
docs/samples/official-samples.md through scripts/extract_sample.py and is
skipped when ../Construct-Example-Projects is not cloned alongside.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from src.validator.structural import StructuralValidator

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = REPO_ROOT / "docs" / "samples"
OFFICIAL_INDEX = SAMPLES_DIR / "official-samples.md"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract_sample.py"

validator = StructuralValidator()


def _sample_payloads() -> list[tuple[str, dict]]:
    payloads: list[tuple[str, dict]] = []
    for path in sorted(SAMPLES_DIR.rglob("*.json")):
        payloads.append((str(path.relative_to(SAMPLES_DIR)), json.loads(path.read_text(encoding="utf-8"))))
    for path in sorted(SAMPLES_DIR.rglob("*.jsonl")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                payloads.append((f"{path.relative_to(SAMPLES_DIR)}:{lineno}", json.loads(line)))
    return payloads


SAMPLE_PAYLOADS = _sample_payloads()


@pytest.mark.parametrize("payload", [p for _, p in SAMPLE_PAYLOADS], ids=[n for n, _ in SAMPLE_PAYLOADS])
def test_committed_sample_validates(payload):
    result = validator.validate(payload)
    assert result.passed, result.errors


# ---------------------------------------------------------------------------
# Official samples, reproduced from the sibling clone
# ---------------------------------------------------------------------------

ROW_RE = re.compile(
    r"^\|\s*`(?P<name>[^`]+)`\s*\|\s*`(?P<project>[^`]+)`\s*\|\s*`(?P<sheet>[^`]+)`\s*\|\s*(?P<selector>[^|]+?)\s*\|"
)


def _official_rows() -> list[tuple[str, list[str]]]:
    rows: list[tuple[str, list[str]]] = []
    for line in OFFICIAL_INDEX.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        selector = m.group("selector").strip("` ")
        argv = [m.group("project"), m.group("sheet")]
        if selector != "whole sheet":
            argv.extend(selector.split(" ", 1))
        rows.append((m.group("name"), argv))
    return rows


def _load_extract_module():
    spec = importlib.util.spec_from_file_location("extract_sample", EXTRACT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OFFICIAL_ROWS = _official_rows()


def test_official_index_has_rows():
    assert len(OFFICIAL_ROWS) == 11


@pytest.mark.parametrize("argv", [a for _, a in OFFICIAL_ROWS], ids=[n for n, _ in OFFICIAL_ROWS])
def test_official_sample_validates(argv, capsys):
    extract = _load_extract_module()
    if not extract.DEFAULT_EXAMPLES_DIR.is_dir():
        pytest.skip(f"{extract.DEFAULT_EXAMPLES_DIR} not cloned alongside")
    extract.main(argv)
    payload = json.loads(capsys.readouterr().out)
    result = validator.validate(payload)
    assert result.passed, result.errors
    assert payload["items"], "extraction returned no items"
