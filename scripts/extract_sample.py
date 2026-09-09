"""Extract a clipboard-shaped events sample from a Scirra example project.

Reads an event sheet from a sibling clone of Scirra/Construct-Example-Projects,
selects a group or a range of events, and prints it as a single-line
``{"is-c3-clipboard-data": true, "type": "events", "items": [...]}`` payload.

The project files are not redistributable, so this script is how the samples
listed in docs/samples/official-samples.md are reproduced locally instead of
being committed.

Usage:
    python scripts/extract_sample.py PROJECT SHEET [selector] [-o FILE]

    PROJECT        folder name under example-projects, e.g. avalanche
    SHEET          event sheet file name with or without .json, e.g. CreditsEvents
    --group TITLE  first group whose title equals TITLE, searched recursively
    --path PATH    dot-separated indices; every segment but the last descends into
                   "children". The last segment may be a range a-b (inclusive).
                   Repeatable; the selected nodes are concatenated in order.
    (no selector)  the whole event sheet

Examples:
    python scripts/extract_sample.py avalanche CreditsEvents
    python scripts/extract_sample.py avalanche EnemyEvents --group HurtArea
    python scripts/extract_sample.py synth-sunset Events --path 4.6-7
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXAMPLES_DIR = REPO_ROOT.parent / "Construct-Example-Projects" / "example-projects"

# Saved project files carry a numeric "sid" on every node; the editor's
# clipboard output does not.
STRIPPED_KEYS = frozenset({"sid"})


def strip_keys(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: strip_keys(v) for k, v in node.items() if k not in STRIPPED_KEYS}
    if isinstance(node, list):
        return [strip_keys(x) for x in node]
    return node


def load_sheet(examples_dir: Path, project: str, sheet: str) -> list[dict]:
    if not examples_dir.is_dir():
        sys.exit(
            f"Example projects not found at {examples_dir}\n"
            "Clone https://github.com/Scirra/Construct-Example-Projects next to this "
            "repository, or pass --examples-dir."
        )
    project_dir = examples_dir / project
    if not project_dir.is_dir():
        sys.exit(f"Project '{project}' not found under {examples_dir}")
    sheet_file = project_dir / "eventSheets" / (sheet if sheet.endswith(".json") else f"{sheet}.json")
    if not sheet_file.is_file():
        available = sorted(p.stem for p in (project_dir / "eventSheets").glob("*.json"))
        sys.exit(f"Event sheet '{sheet}' not found in {project}. Available: {', '.join(available)}")
    data = json.loads(sheet_file.read_text(encoding="utf-8"))
    events = data.get("events")
    if not isinstance(events, list):
        sys.exit(f"{sheet_file} has no 'events' array")
    return events


def find_group(events: list[dict], title: str) -> dict | None:
    for node in events:
        if node.get("eventType") == "group" and node.get("title") == title:
            return node
        children = node.get("children")
        if isinstance(children, list):
            found = find_group(children, title)
            if found is not None:
                return found
    return None


def select_path(events: list[dict], path: str) -> list[dict]:
    segments = path.split(".")
    node_list = events
    for seg in segments[:-1]:
        idx = int(seg)
        if idx >= len(node_list):
            sys.exit(f"Path '{path}': index {idx} out of range ({len(node_list)} nodes)")
        node = node_list[idx]
        node_list = node.get("children")
        if not isinstance(node_list, list):
            sys.exit(f"Path '{path}': node {seg} has no children")
    last = segments[-1]
    if "-" in last:
        start_s, end_s = last.split("-", 1)
        start, end = int(start_s), int(end_s)
    else:
        start = end = int(last)
    if start > end or end >= len(node_list):
        sys.exit(f"Path '{path}': range {start}-{end} out of range ({len(node_list)} nodes)")
    return node_list[start : end + 1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project")
    parser.add_argument("sheet")
    parser.add_argument("--group", help="group title to extract")
    parser.add_argument("--path", action="append", default=[], help="index path, repeatable")
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES_DIR)
    parser.add_argument("-o", "--output", type=Path, help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    if args.group and args.path:
        parser.error("--group and --path are mutually exclusive")

    events = load_sheet(args.examples_dir, args.project, args.sheet)

    if args.group:
        group = find_group(events, args.group)
        if group is None:
            sys.exit(f"Group '{args.group}' not found in {args.project}/{args.sheet}")
        items = [group]
    elif args.path:
        items = []
        for p in args.path:
            items.extend(select_path(events, p))
    else:
        items = events

    payload = {"is-c3-clipboard-data": True, "type": "events", "items": strip_keys(items)}
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
