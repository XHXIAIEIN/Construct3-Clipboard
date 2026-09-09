# Clipboard samples

JSON copied out of the Construct 3 editor, kept as regression material for the validator and
the generator. Every file is a single line because that is what the editor writes; do not
reformat them, or byte comparison against fresh captures stops working.

## Files

| Path | Content |
|---|---|
| `single-block.json` | One block: `every-tick` with an empty `actions` array |
| `block-with-subevents.json` | One block with empty conditions and nested `children`, including siblings and a grandchild |
| `shapes/conditions.jsonl` | Eight combinations of `isInverted`, `isOrBlock`, and `else` |
| `shapes/groups.jsonl` | Five group shapes, from empty to three levels of nesting |
| `shapes/variables.jsonl` | Variables at sheet and group level, with `isStatic` / `isConstant` |
| `shapes/README.md` | What each `.jsonl` line contains |
| `official-samples.md` | Samples taken from Scirra example projects, reproduced locally with `scripts/extract_sample.py` |

Each `.jsonl` line is a complete clipboard payload. `tests/test_real_samples.py` validates every
file here and, when `../Construct-Example-Projects` is cloned, every sample listed in
`official-samples.md`.

## Format facts observed in editor output

Paths below name the source project under `example-projects/` in
[Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects).

**Action-level comments.** An `actions` array may contain `{"type":"comment","text":"..."}`.
The key is `type`, not `eventType`. A block-level `eventType:"comment"` and an action-level
`type:"comment"` can coexist (`synth-sunset/eventSheets/Events.json`).

**`callFunction` and `customAction` take a positional array.** `parameters` is a JSON array,
omitted when the call has no arguments. Elements can be JSON booleans.

```json
{"callFunction":"playBGM","parameters":["\"IceVillage\"",false,"0"]}
{"callFunction":"stopBGM"}
{"customAction":"Pushback","objectClass":"Player","parameters":["HurtArea.X","HurtArea.Y"]}
{"customAction":"Attack","objectClass":"EnemyMelee"}
```

Sources: `avalanche/eventSheets/CreditsEvents.json`, `avalanche/eventSheets/EnemyEvents.json`.

**`isInverted` is a condition field; `isOrBlock` is a block field.** Both are booleans and
absent when false (`shapes/conditions.jsonl`). Two triggers can share one `isOrBlock` block
(`tasty-cappuccino/eventSheets/Events.json`, group `Controls`).

**`eventType:"include"`** carries only `includeSheet` (`avalanche/eventSheets/CreditsEvents.json`).

**`eventType:"custom-ace-block"`** carries `aceType`, `aceName`, `objectClass`,
`functionDescription`, `functionCategory`, `functionReturnType`, `functionCopyPicked`,
`functionIsAsync`, `functionParameters`, plus `conditions`, `actions`, and `children`
(`avalanche/eventSheets/EnemyEvents.json`).

**`eventType:"function-block"`** carries `functionName` and the same `function*` fields as a
custom ACE block (`solar-system/eventSheets/Events.json`, functions `applyScale` and `loadInfo`).
`functionParameters` entries look like variables: `name`, `type`, `initialValue`, `comment`.

**Variables** carry `isStatic` and `isConstant` and may have a non-empty `comment`
(`shapes/variables.jsonl`, `solar-system/eventSheets/Events.json`).

**`else` does not stand alone.** A block can start with `{"id":"else","objectClass":"System"}`
and continue with further conditions (`robotic-loader/eventSheets/Code.json`).

**`add-child` / `remove-child`.** `add-child` takes `child` plus boolean `transform-x`,
`transform-y`, `transform-z-elevation`, `transform-w`, `transform-h`, `transform-a`,
`transform-o`, `transform-visibility`, `destroy-with-parent`; `remove-child` takes only `child`
(`robotic-loader/eventSheets/Code.json`).

**Parameter values can be objects.** The `file` parameter of AJAX `request-project-file` is
`{"path":"Data/BodiesData.json"}` on the clipboard (`solar-system/eventSheets/Events.json`).

**Comment text can contain `\n`** (`solar-system/eventSheets/Events.json`, first item).

**Parameter conventions seen in every sample.**

- Keys are the kebab-case parameter ids from the ACE schema (`instance-variable`, `z-elevation`,
  `image-point-optional`), not positional indices.
- `comparison` is an integer 0 to 5: equal, not equal, less, less or equal, greater, greater or equal.
- Booleans are JSON booleans (`"pick-all-tied":false`), not strings.
- String literals keep their quotes inside the JSON string (`"value":"\"dead\""`), because the
  expression language needs them.
