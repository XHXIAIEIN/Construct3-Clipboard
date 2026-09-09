# Troubleshooting

Common mistakes when pasting generated JSON into Construct 3, and how to fix them.

## Paste Not Working

| Cause | Fix |
|-------|-----|
| Used `writeText()` | Use `ClipboardItem + Blob` (see [clipboard-format.md](clipboard-format.md)) |
| Wrong focus | Click the event sheet margin, layout view, or Project Bar folder first |
| Bad JSON | Run `scripts/validate.py` on the payload before pasting |

## ACE Errors

| Error | Fix |
|-------|-----|
| ACE not found | Use the kebab-case id from the RAG schema: `set-animation`, not `SetAnimation` |
| Wrong behavior | `behaviorType` is the behavior's name on the object as shown in the editor (`8Direction`, `Platform`), not the schema id (`eightdir`) |
| Missing behaviorType | Add `"behaviorType": "BehaviorName"` to behavior ACEs |

## Parameter Errors

| Error | Fix |
|-------|-----|
| String ignored | Add nested quotes: `"\"Walk\""` |
| Comparison fails | Use a number: `4`, not `">"` |
| Key code fails | Use a number: `87`, not `"87"` |
| Empty parameters | Omit `parameters` instead of writing `{}` |

## Variable Errors

| Error | Fix |
|-------|-----|
| Variable rejected by validator | Add a `"comment": ""` field; the editor always writes one |

## Quick Validation

Structural checks only; ACE ids are not verified against the schema.

```bash
python scripts/validate.py path/to/clipboard.json
python scripts/validate.py '{"is-c3-clipboard-data":true,"type":"events","items":[]}'
```

To check ACE ids and parameter keys in docs and fixtures against a sibling
`../Construct3-RAG` clone:

```bash
python scripts/check_ace_refs.py
```
