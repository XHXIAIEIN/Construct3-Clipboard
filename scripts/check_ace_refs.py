"""Check ACE ids and parameter keys in docs and fixtures against the RAG schema.

Scans docs/**/*.md, docs/samples/**/*.json and *.jsonl, and tests/fixtures/**/*.json
for condition or action objects of the form

    {"id": ..., "objectClass": ...[, "behaviorType": ...][, "parameters": {...}]}

and looks each one up in a sibling clone of Construct3-RAG
(data/c3-schemas/en-US/{plugins,behaviors}/{id}.json). Unknown ids or parameter
keys are reported and the script exits 1. When the RAG clone is absent the
check is skipped with exit 0 so the test suite stays runnable without it.

Usage:
    python scripts/check_ace_refs.py [--rag-dir DIR] [paths...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RAG_DIR = REPO_ROOT.parent / "Construct3-RAG"
SCHEMA_SUBDIR = Path("data") / "c3-schemas" / "en-US"

DEFAULT_SCAN = [
    REPO_ROOT / "docs",
    REPO_ROOT / "tests" / "fixtures",
]

# objectClass -> plugin schema id. Anything not listed is treated as a user
# object type and searched in PLUGIN_FALLBACKS in order.
PLUGIN_BY_OBJECT_CLASS = {
    "System": "system",
    "Keyboard": "keyboard",
    "Mouse": "mouse",
    "Touch": "touch",
    "Audio": "audio",
    "AJAX": "ajax",
    "Array": "arr",
    "Arr": "arr",
    "Dictionary": "dictionary",
    "Browser": "browser",
    "LocalStorage": "localstorage",
    "Gamepad": "gamepad",
    "JSON": "json",
    "TimelineController": "timeline",
}
PLUGIN_FALLBACKS = [
    "sprite", "_common", "text", "tiledbg", "ninepatch", "tilemap",
    "spritefont2", "particles",
]

# behaviorType display name -> behavior schema id
BEHAVIOR_BY_DISPLAY_NAME = {
    "8Direction": "eightdir",
    "Platform": "platform",
    "Bullet": "bullet",
    "Tween": "tween",
    "Flash": "flash",
    "Solid": "solid",
    "Timer": "timer",
    "Sine": "sin",
    "Pin": "pin",
    "Fade": "fade",
    "LOS": "los",
    "Pathfinding": "pathfinding",
    "Anchor": "anchor",
    "DragDrop": "dragndrop",
    "ScrollTo": "scrollto",
    "BoundToLayout": "bound",
    "DestroyOutsideLayout": "destroy",
    "Physics": "physics",
    "Rotate": "rotate",
    "Orbit": "orbit",
    "MoveTo": "moveto",
    "Turret": "turret",
    "Wrap": "wrap",
    "Car": "car",
    "Persist": "persist",
    "Custom": "custom",
    "TileMovement": "tilemovement",
    "Follow": "follow",
    "JumpThru": "jumpthru",
}

ACE_RE = re.compile(
    r'\{\s*"id"\s*:\s*"(?P<id>[^"]+)"\s*,\s*"objectClass"\s*:\s*"(?P<obj>[^"]+)"'
    r'(?:\s*,\s*"behaviorType"\s*:\s*"(?P<beh>[^"]+)")?'
    r'(?:\s*,\s*"parameters"\s*:\s*\{(?P<params>[^{}]*)\})?'
)
PARAM_KEY_RE = re.compile(r'"([^"\\]+)"\s*:')


class SchemaIndex:
    """Lazy loader for {kind}/{id}.json -> {ace id: parameter key set}."""

    def __init__(self, schema_dir: Path) -> None:
        self.schema_dir = schema_dir
        self._cache: dict[tuple[str, str], dict[str, set[str]] | None] = {}

    def load(self, kind: str, schema_id: str) -> dict[str, set[str]] | None:
        key = (kind, schema_id)
        if key not in self._cache:
            path = self.schema_dir / kind / f"{schema_id}.json"
            if not path.is_file():
                self._cache[key] = None
            else:
                data = json.loads(path.read_text(encoding="utf-8"))
                aces: dict[str, set[str]] = {}
                for section in ("conditions", "actions"):
                    for ace in data.get(section, []):
                        aces[ace["id"]] = set((ace.get("params") or {}).keys())
                self._cache[key] = aces
        return self._cache[key]


def parse_param_keys(raw: str) -> set[str]:
    try:
        return set(json.loads("{" + raw + "}").keys())
    except json.JSONDecodeError:
        return set(PARAM_KEY_RE.findall(raw))


def check_text(text: str, source: str, index: SchemaIndex, errors: list[str]) -> int:
    count = 0
    for m in ACE_RE.finditer(text):
        count += 1
        ace_id, obj, beh, params = m.group("id", "obj", "beh", "params")
        line = text.count("\n", 0, m.start()) + 1
        where = f"{source}:{line}"

        if beh is not None:
            schema_id = BEHAVIOR_BY_DISPLAY_NAME.get(beh)
            if schema_id is None:
                errors.append(f"{where}: behaviorType '{beh}' has no schema mapping")
                continue
            aces = index.load("behaviors", schema_id)
            if aces is None:
                errors.append(f"{where}: behavior schema '{schema_id}.json' not found")
                continue
            if ace_id not in aces:
                errors.append(f"{where}: '{ace_id}' not in behavior '{schema_id}'")
                continue
            expected = aces[ace_id]
        else:
            schema_id = PLUGIN_BY_OBJECT_CLASS.get(obj)
            candidates = [schema_id] if schema_id else PLUGIN_FALLBACKS
            expected = None
            for cand in candidates:
                aces = index.load("plugins", cand)
                if aces is None:
                    if schema_id:
                        errors.append(f"{where}: plugin schema '{cand}.json' not found")
                    continue
                if ace_id in aces:
                    expected = aces[ace_id]
                    break
            if expected is None:
                searched = schema_id or "/".join(PLUGIN_FALLBACKS)
                errors.append(f"{where}: '{ace_id}' (objectClass {obj}) not in {searched}")
                continue

        if params is not None:
            unknown = parse_param_keys(params) - expected
            if unknown:
                errors.append(
                    f"{where}: '{ace_id}' unknown parameter keys {sorted(unknown)}; "
                    f"schema has {sorted(expected)}"
                )
    return count


def iter_files(paths: list[Path]):
    for base in paths:
        if base.is_file():
            yield base
            continue
        for p in sorted(base.rglob("*")):
            if p.suffix in (".md", ".json", ".jsonl") and p.is_file():
                yield p


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", type=Path, help="files or directories to scan")
    parser.add_argument("--rag-dir", type=Path, default=DEFAULT_RAG_DIR)
    args = parser.parse_args(argv)

    schema_dir = args.rag_dir / SCHEMA_SUBDIR
    if not schema_dir.is_dir():
        print(f"Construct3-RAG schemas not found at {schema_dir}; skipping ACE reference check.")
        return 0

    index = SchemaIndex(schema_dir)
    errors: list[str] = []
    total = 0
    for path in iter_files(args.paths or DEFAULT_SCAN):
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        total += check_text(path.read_text(encoding="utf-8"), str(rel), index, errors)

    for e in errors:
        print(e)
    print(f"{total} ACE references checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
