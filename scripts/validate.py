"""Run the structural validator on a clipboard payload.

Usage:
    python scripts/validate.py path/to/clipboard.json
    python scripts/validate.py '{"is-c3-clipboard-data":true,"type":"events","items":[]}'

Exit code 0 when the payload passes, 1 when it does not, 2 for unreadable input.
Warnings are printed but do not fail the check.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.validator.structural import StructuralValidator  # noqa: E402


def load_payload(arg: str) -> dict:
    path = Path(arg)
    text = path.read_text(encoding="utf-8") if path.is_file() else arg
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        sys.exit(f"Not valid JSON: {exc}")
    if not isinstance(data, dict):
        sys.exit("Payload must be a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    result = StructuralValidator().validate(load_payload(argv[0]))
    for w in result.warnings:
        print(f"warning: {w}")
    for e in result.errors:
        print(f"error: {e}")
    print("passed" if result.passed else "failed")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
