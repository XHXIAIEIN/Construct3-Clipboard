# Minimal Shape Matrix

每个 `.jsonl` 文件里**一行一个完整的 C3 clipboard JSON**，按"同类 shape、渐进复杂度"组织。直接喂给 validator 做 round-trip 回归测试。

> C3 里空 `conditions:[]` 的 block 和 `conditions:[{id:"every-tick",objectClass:"System"}]` 的 block **运行时行为等价** — 空条件 = 每帧触发。这给 generator 提供了一个可用的简化策略。

## `conditions.jsonl` — condition 组合矩阵

| 行 | Shape | 字段特征 |
|---:|---|---|
| 1 | 1 block：every-tick + inverted compare | 基础 `isInverted` |
| 2 | 1 block：两个 inverted (AND) | 多 inverted 默认 AND |
| 3 | 1 block：inverted + normal (AND) | 混合 inverted |
| 4 | 1 block：inverted + normal + `isOrBlock:true` | **`isOrBlock`** — block 级 OR 关系 |
| 5 | 1 block：两个 normal + `isOrBlock:true` | 纯 OR |
| 6 | 2 siblings：normal block + else-block (2 conds) | else 链基础 |
| 7 | 2 siblings：normal block + else-block (1 cond) | |
| 8 | 2 siblings：inverted block + else-block | inverted + else 组合 |

## `groups.jsonl` — group 变体

| 行 | Shape | 字段特征 |
|---:|---|---|
| 1 | 空 group | 空 `children` |
| 2 | group 含 1 block (normal cond) | |
| 3 | group 含 1 block (trigger-once-while-true) | trigger 类条件 |
| 4 | group 含 if/else (inverted + else) | group 内 else 链 |
| 5 | 嵌套 group：3 层嵌套 + 兄弟 group | **group in group** — 结构递归 |

## `variables.jsonl` — variable 位置 & 修饰符

| 行 | Shape | 字段特征 |
|---:|---|---|
| 1 | 顶层 variable + group | variable 作为 sheet-level var |
| 2 | group 内 variable + block | variable 作为 group-scoped var |
| 3 | group 内 variable with `isStatic:true` | **`isStatic`** 修饰 |

> 三行都带 `isStatic` + `isConstant` 字段 — builder 当前的 `build_variable` 没这俩字段，需要补。
