# Samples from Scirra example projects

Real editor output copied from the official Construct 3 example projects. The
[Scirra license](https://github.com/Scirra/Construct-Example-Projects/blob/main/LICENSE.txt)
does not allow redistributing that content as standalone files, so these samples are not
committed. Reproduce any of them locally with `scripts/extract_sample.py` from a sibling
clone of [Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects).

```bash
python scripts/extract_sample.py avalanche CreditsEvents
python scripts/extract_sample.py avalanche EnemyEvents --group HurtArea
python scripts/extract_sample.py synth-sunset Events --path 4.6-7
```

`--path` is a dot-separated index path into the sheet's `events` array. Every segment but the
last descends into `children`; the last segment may be an inclusive range. With no selector the
whole sheet is emitted. Saved project files carry a numeric `sid` on every node; the script strips
it because the editor's clipboard output has none.

## Sample index

| Sample | Project | Event sheet | Selector | Format points shown |
|---|---|---|---|---|
| `full-sheet` | `avalanche` | `CreditsEvents.json` | whole sheet | `eventType:"include"` with `includeSheet`; variable `isStatic` / `isConstant`; `callFunction` with positional parameters and without any; action-level `{"type":"comment"}` |
| `group` | `avalanche` | `EnemyEvents.json` | `--group HurtArea` | a single group copied alone; `customAction` with a positional parameter list |
| `sub-event` | `avalanche` | `CreditsEvents.json` | `--path 3.3.1` | a nested sub-event copied on its own (`compare-y` followed by three `set-y`) |
| `action-variants` | `avalanche` | `CreditsEvents.json` | `--path 3.1` | one block mixing action-level comments and `callFunction` calls |
| `complex-shadow` | `avalanche` | `PlayerEvents.json` | `--path 1.1` | block with empty `conditions`, nine children, `else` chains, three levels of nesting |
| `complex-enemy-ai` | `avalanche` | `EnemyEvents.json` | `--path 2.1.4-5` | `eventType:"custom-ace-block"` with `aceType` / `aceName` / `objectClass` and the `function*` fields; `customAction` without parameters; deep `children` |
| `complex-hazard-lights` | `synth-sunset` | `Events.json` | `--path 4.6-7` | block-level `eventType:"comment"` next to action-level `type:"comment"`; if/else pair |
| `action-inline-comments` | `synth-sunset` | `Events.json` | `--path 4.1` | action-level comments used as section headings inside one block |
| `complex-timeline-truck` | `robotic-loader` | `Code.json` | `--path 1-16` | `TimelineController` `play-timeline`, `on-timeline-finished-by-tags`, `on-keyframe-reached`; `add-child` / `remove-child` with boolean `transform-*` parameters; `else` followed by a further condition in the same block; `for-each` nesting |
| `complex-solar-system` | `solar-system` | `Events.json` | whole sheet | `eventType:"function-block"` with `functionName` / `functionDescription` / `functionCategory` / `functionReturnType` / `functionCopyPicked` / `functionIsAsync` / `functionParameters`; nested groups; object-valued parameter (`file`); multi-line comment text; non-empty variable `comment` |
| `timeline-controller` | `tasty-cappuccino` | `Events.json` | `--group Controls` | `TimelineController` `is-any-playing`, `on-keyframe-reached` with `match:"any-tags"`, `play-timeline-by-name`; two triggers under `isOrBlock:true`; comments between blocks |

## Where project files and clipboard output differ

Nine of the eleven extractions are byte-identical to what the editor put on the clipboard.
The remaining differences are properties of the saved project format, not of the script:

| Sample | Difference |
|---|---|
| `complex-shadow` | The clipboard carries `"pick-all-tied": false` on `pick-by-highest-lowest-value`; the saved project omits it. The editor fills in defaults for parameters that were added to an ACE after the project was saved. |
| `complex-solar-system` | The `file` parameter of `request-project-file` is the string `"BodiesData.json"` in the project and the object `{"path":"Data/BodiesData.json"}` on the clipboard. |
| `complex-timeline-truck` | Same keys and values, different key order: the clipboard lists `add-child` parameters in ACE schema order (`transform-z-elevation` right after `transform-y`); the project file keeps an older order. Only byte comparison is affected. |

All eleven extractions validate the same way as the captures did. `tests/test_real_samples.py`
runs them through the structural validator when the sibling clone is present.
