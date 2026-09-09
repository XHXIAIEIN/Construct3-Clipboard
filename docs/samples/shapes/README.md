# Minimal shape matrix

Each `.jsonl` file holds one complete clipboard payload per line, ordered from the simplest
shape to the most involved. They are editor captures, kept single-line, and feed
`tests/test_real_samples.py`.

## `conditions.jsonl`

| Line | Shape | Fields shown |
|---:|---|---|
| 1 | one block: `every-tick` + inverted compare | `isInverted` |
| 2 | one block: two inverted conditions (AND) | several `isInverted` in one block |
| 3 | one block: inverted + normal (AND) | mixed |
| 4 | one block: inverted + normal with `isOrBlock:true` | `isOrBlock` on the block |
| 5 | one block: two normal conditions with `isOrBlock:true` | plain OR |
| 6 | two siblings: block + else-block with two conditions | `else` followed by another condition |
| 7 | two siblings: block + else-block with one condition | |
| 8 | two siblings: inverted block + else-block | `isInverted` and `else` together |

## `groups.jsonl`

| Line | Shape | Fields shown |
|---:|---|---|
| 1 | empty group | empty `children` |
| 2 | group with one block (normal condition) | |
| 3 | group with one block (`trigger-once-while-true`) | trigger condition |
| 4 | group with if/else (inverted + else) | else chain inside a group |
| 5 | three nested groups plus a sibling group | groups inside groups |

## `variables.jsonl`

| Line | Shape | Fields shown |
|---:|---|---|
| 1 | sheet-level variable + group | variable at sheet scope |
| 2 | variable inside a group + block | variable at group scope |
| 3 | variable inside a group with `isStatic:true` | `isStatic` |

Every variable line carries both `isStatic` and `isConstant`; the editor always writes them.
