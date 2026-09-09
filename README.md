# Construct3-Clipboard

**English** | [中文](README_CN.md)

A reference for the JSON that [Construct 3](https://www.construct.net) puts on the clipboard, a
structural validator for that JSON, and a minimal generator that turns a short intent description
into paste-ready payloads. It exists so that events, object types and layouts produced outside the
editor can be pasted in without hand-fixing the format.

## Contents

| Path | What it holds |
|---|---|
| [docs/clipboard-format.md](docs/clipboard-format.md) | Clipboard envelope, event types, condition and action entries, parameter rules, templates, world instances, layouts, timelines |
| [docs/object-templates.md](docs/object-templates.md) | `object-types` payloads per plugin |
| [docs/layout-templates.md](docs/layout-templates.md) | `layouts` payloads |
| [docs/family-patterns.md](docs/family-patterns.md), [docs/deprecated-features.md](docs/deprecated-features.md), [docs/troubleshooting.md](docs/troubleshooting.md) | Families, replacements for deprecated features, common paste errors |
| [docs/samples/](docs/samples/README.md) | Editor captures used as regression material, and the index of samples reproduced from Scirra example projects |
| `src/validator/` | `StructuralValidator`: checks the shape of a payload without consulting the ACE schema |
| `src/generator/` | Intent IR to clipboard JSON for `events` and `object-types` |
| `scripts/` | Command-line entry points, see below |
| `playground/` | Browser page for trying the API |

## Use the docs and scripts

Python 3.10 or newer. Install dependencies once:

```bash
pip install -r requirements.txt
```

Validate a payload from a file or an inline string. Exit code 1 means it failed:

```bash
python scripts/validate.py path/to/clipboard.json
python scripts/validate.py '{"is-c3-clipboard-data":true,"type":"events","items":[]}'
```

Print a placeholder PNG data URI for an `imageData` array:

```bash
python scripts/imagedata.py --color blue --width 16 --height 16 --shape circle
```

Reproduce a sample from a sibling clone of Scirra/Construct-Example-Projects
(see [docs/samples/official-samples.md](docs/samples/official-samples.md) for the full index):

```bash
python scripts/extract_sample.py avalanche CreditsEvents
python scripts/extract_sample.py avalanche EnemyEvents --group HurtArea
```

Check every ACE id and parameter key in `docs/` and `tests/fixtures/` against a sibling clone of
Construct3-RAG. Exit code 1 on any unknown id or key; a notice and exit 0 when the clone is absent:

```bash
python scripts/check_ace_refs.py
```

To paste, write the JSON to the clipboard as a `text/plain` Blob and paste into the matching
editor location. The exact call and the paste targets are in
[docs/clipboard-format.md](docs/clipboard-format.md).

## Run the API (optional)

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8766
```

`start.bat` runs the same command with `--reload`. The server binds to `127.0.0.1` because it has
no authentication.

| Route | Purpose |
|---|---|
| `GET /health` | `{"status": "ok", "service": "Construct3-Clipboard", "version": "0.1.0"}` |
| `POST /validate` | Body `{"clipboard_json": {...}}`. Returns `passed`, `errors`, `warnings` |
| `POST /generate` | Body `{"intent_ir": {...}, "options": {...}}`. Returns `success`, `clipboard_json`, `validation`, `metadata`, or `error` |
| `GET /` | The playground page. `GET /docs` is the generated OpenAPI UI |

### Intent IR

`intent_ir.type` is `event_sheet` or `object_types`. Unknown types return `success: false`.

```json
{
  "type": "event_sheet",
  "variables": [{"name": "Score", "type": "number", "initialValue": "0", "comment": ""}],
  "events": [{
    "conditions": [{"id": "on-start-of-layout", "objectClass": "System"},
                   {"id": "is-on-floor", "objectClass": "Player", "behaviorType": "Platform", "isInverted": true}],
    "actions": [{"id": "set-eventvar-value", "objectClass": "System", "parameters": {"variable": "Score", "value": "0"}},
                {"callFunction": "AddScore", "parameters": ["10"]},
                {"type": "script", "language": "javascript", "script": ["console.log('hi');"]}],
    "children": []
  }],
  "groups": [{"title": "Player", "description": "", "events": []}],
  "functions": [{"name": "AddScore", "returnType": "none", "isAsync": false, "description": "",
                 "parameters": [{"name": "amount", "type": "number", "initialValue": "0", "comment": ""}],
                 "conditions": [], "actions": []}]
}
```

Condition and action entries use the same keys as the clipboard format: `id`, `objectClass`,
optional `parameters` keyed by schema parameter id, optional `behaviorType`, and `isInverted` on
conditions. Items are emitted in the order variables, events, groups, functions.

```json
{
  "type": "object_types",
  "objects": [
    {"name": "Player", "plugin": "Sprite", "behaviors": [{"behaviorId": "Platform", "name": "Platform"}],
     "instance_variables": [], "effects": [], "is_global": false},
    {"name": "Keyboard", "plugin": "Keyboard"},
    {"name": "Data", "plugin": "Arr", "is_global": true, "properties": {"width": 10, "height": 1, "depth": 1}}
  ]
}
```

`plugin` is the Construct plugin id (`Sprite`, `TiledBg`, `NinePatch`, `Tilemap`, `Text`,
`Keyboard`, `Arr`, ...). `properties` fills the `singleglobal-inst` or `nonworld-inst` block.
With `"options": {"include_imagedata": true}` a 32x32 gray placeholder is attached as `imageData`
for every item that carries `animations` or `image`.

The generator does not look up ACE ids: `/generate` succeeds as long as the structure is valid.
Run `scripts/check_ace_refs.py` or consult the RAG schema for the ids themselves.

## What has been checked against the editor

Verified against real editor output:

- The event-sheet format facts in [docs/samples/README.md](docs/samples/README.md): committed
  captures plus the eleven samples from Scirra projects, all of which pass the validator.
- The `layouts` format, using the Top-Down Shooter capture in `docs/layout-templates.md`; world
  instances use `z`, layers use `zElevation`.
- `behaviorTypes` entries are `{"behaviorId": ..., "name": ...}`; `behaviorId` keeps the
  editor's casing (`EightDir`, `bound`, `destroy`).

Checked against the Construct3-RAG schema, not against the editor:

- Every ACE id and parameter key in `docs/` and `tests/fixtures/` (`scripts/check_ace_refs.py`).
- Combo parameter values such as Tween `property` (`offsetOpacity`); every combo value in the
  captures matches its schema id, but the Tween ones have not been pasted.

Not verified in the editor:

- Generator output. It matches the templates key for key, but no generated payload has been
  pasted back into Construct 3 yet.
- The `object-types` templates beyond what the layouts capture shows: `ui-state`, the Array,
  Dictionary and Audio property blocks, and the `Animation 1` versus `Default` animation name.
- The Platform and Breakout layouts in `docs/layout-templates.md` and the fixtures under
  `tests/fixtures/`, which were written by hand.
- Timelines beyond the top-level `name` and `tracks` fields.

## Samples and licensing

The files under `docs/samples/` were copied out of the Construct 3 editor and are covered by this
repository's MIT license ([LICENSE](LICENSE)).

Samples taken from [Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects)
are not committed: their [license](https://github.com/Scirra/Construct-Example-Projects/blob/main/LICENSE.txt)
does not permit redistributing project content as standalone files. Clone that repository alongside
this one and use `scripts/extract_sample.py`; the index and the known differences between saved
project files and clipboard output are in
[docs/samples/official-samples.md](docs/samples/official-samples.md).

## Related repositories

| Repository | What it holds | How it fits |
|---|---|---|
| [XHXIAIEIN/Construct3-RAG](https://github.com/XHXIAIEIN/Construct3-RAG) | Plugin, behavior and effect schemas as JSON | Source of ACE ids and parameter ids. `scripts/check_ace_refs.py` reads it when cloned alongside. |
| [XHXIAIEIN/Construct3-Copilot](https://github.com/XHXIAIEIN/Construct3-Copilot) | The assistant that produces Intent IR | Calls `/generate`, `/validate` and `/health` on this service. |
| [Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects) | Official example projects as folder projects | `scripts/extract_sample.py` and `tests/test_real_samples.py` read it when cloned alongside. |

"Cloned alongside" means a sibling directory of this repository, for example
`../Construct3-RAG` and `../Construct-Example-Projects`.

## Development

```bash
python -m pytest -q
python -m compileall -q src scripts tests
python scripts/check_ace_refs.py
```

`tests/test_real_samples.py` validates every file under `docs/samples/` and, when the example
projects are cloned alongside, every extraction listed in `official-samples.md`; otherwise those
cases are skipped.
