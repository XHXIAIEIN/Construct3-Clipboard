# Construct3-Clipboard

[English](README.md) | **中文**

[Construct 3](https://www.construct.net) 剪贴板 JSON 的格式参考、结构验证器，以及一个把简短意图描述转成可粘贴载荷的最小生成器。有了它，在编辑器外生成的事件、对象类型和布局可以直接粘贴进去，不用手工修格式。

## 内容

| 路径 | 内容 |
|---|---|
| [docs/clipboard-format.md](docs/clipboard-format.md) | 剪贴板外层结构、事件类型、条件与动作条目、参数规则、模板、世界实例、布局、时间线 |
| [docs/object-templates.md](docs/object-templates.md) | 各插件的 `object-types` 载荷 |
| [docs/layout-templates.md](docs/layout-templates.md) | `layouts` 载荷 |
| [docs/family-patterns.md](docs/family-patterns.md)、[docs/deprecated-features.md](docs/deprecated-features.md)、[docs/troubleshooting.md](docs/troubleshooting.md) | 家族用法、已弃用功能的替代写法、常见粘贴错误 |
| [docs/samples/](docs/samples/README.md) | 作为回归素材的编辑器捕获，以及从 Scirra 示例工程复现的样例索引 |
| `src/validator/` | `StructuralValidator`：只检查载荷结构，不查 ACE schema |
| `src/generator/` | Intent IR 到 `events` 和 `object-types` 剪贴板 JSON |
| `scripts/` | 命令行入口，见下文 |
| `playground/` | 试用 API 的浏览器页面 |

## 直接使用文档和脚本

需要 Python 3.10 或更新版本。安装一次依赖：

```bash
pip install -r requirements.txt
```

验证文件或内联字符串中的载荷，退出码 1 表示未通过：

```bash
python scripts/validate.py path/to/clipboard.json
python scripts/validate.py '{"is-c3-clipboard-data":true,"type":"events","items":[]}'
```

生成占位 PNG 的 data URI，用于 `imageData` 数组：

```bash
python scripts/imagedata.py --color blue --width 16 --height 16 --shape circle
```

从同级目录的 Scirra/Construct-Example-Projects 克隆中复现样例（完整索引见 [docs/samples/official-samples.md](docs/samples/official-samples.md)）：

```bash
python scripts/extract_sample.py avalanche CreditsEvents
python scripts/extract_sample.py avalanche EnemyEvents --group HurtArea
```

对照同级目录的 Construct3-RAG 克隆，检查 `docs/` 和 `tests/fixtures/` 里所有 ACE id 和参数键。存在未知 id 或键时退出码 1；克隆不存在时打印提示并退出 0：

```bash
python scripts/check_ace_refs.py
```

粘贴时，把 JSON 作为 `text/plain` Blob 写入剪贴板，再在编辑器对应位置粘贴。具体调用方式和粘贴位置见 [docs/clipboard-format.md](docs/clipboard-format.md)。

## 运行 API（可选）

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8766
```

`start.bat` 运行同一条命令并加上 `--reload`。服务没有鉴权，因此只绑定 `127.0.0.1`。

| 路由 | 用途 |
|---|---|
| `GET /health` | `{"status": "ok", "service": "Construct3-Clipboard", "version": "0.1.0"}` |
| `POST /validate` | 请求体 `{"clipboard_json": {...}}`，返回 `passed`、`errors`、`warnings` |
| `POST /generate` | 请求体 `{"intent_ir": {...}, "options": {...}}`，返回 `success`、`clipboard_json`、`validation`、`metadata`，失败时返回 `error` |
| `GET /` | playground 页面。`GET /docs` 是自动生成的 OpenAPI 界面 |

### Intent IR

`intent_ir.type` 为 `event_sheet` 或 `object_types`，其他值返回 `success: false`。

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

条件和动作条目使用与剪贴板格式相同的键：`id`、`objectClass`、可选的按 schema 参数 id 组织的 `parameters`、可选的 `behaviorType`，条件上可加 `isInverted`。输出顺序固定为变量、事件、分组、函数。

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

`plugin` 是 Construct 的插件 id（`Sprite`、`TiledBg`、`NinePatch`、`Tilemap`、`Text`、`Keyboard`、`Arr` 等）。`properties` 填入 `singleglobal-inst` 或 `nonworld-inst` 块。传入 `"options": {"include_imagedata": true}` 时，会为每个带 `animations` 或 `image` 的条目附上一张 32x32 的灰色占位图作为 `imageData`。

生成器不查 ACE id：只要结构合法，`/generate` 就返回成功。id 本身请用 `scripts/check_ace_refs.py` 或 RAG schema 核对。

## 哪些内容经过编辑器核对

已对照真实编辑器输出核对：

- [docs/samples/README.md](docs/samples/README.md) 中的事件表格式事实：已提交的捕获，加上来自 Scirra 工程的 11 个样例，全部通过验证器。
- `layouts` 格式，依据 `docs/layout-templates.md` 中的 Top-Down Shooter 捕获；世界实例用 `z`，图层用 `zElevation`。
- `behaviorTypes` 条目为 `{"behaviorId": ..., "name": ...}`，`behaviorId` 保留编辑器的大小写（`EightDir`、`bound`、`destroy`）。

只对照 Construct3-RAG schema 核对，未在编辑器中验证：

- `docs/` 和 `tests/fixtures/` 中的全部 ACE id 和参数键（`scripts/check_ace_refs.py`）。
- 组合参数的取值，例如 Tween 的 `property`（`offsetOpacity`）。捕获中每个组合值都与 schema id 一致，但 Tween 这几个没有实际粘贴过。

未在编辑器中验证：

- 生成器的输出。它与模板逐键一致，但还没有把生成结果粘贴回 Construct 3。
- `object-types` 模板中布局捕获没覆盖的部分：`ui-state`、Array、Dictionary 和 Audio 的属性块，以及动画名是 `Animation 1` 还是 `Default`。
- `docs/layout-templates.md` 中的 Platform 和 Breakout 布局，以及 `tests/fixtures/` 下的 fixture，这些是手写的。
- 时间线中 `name` 和 `tracks` 之外的字段。

## 样例来源与许可

`docs/samples/` 下的文件是从 Construct 3 编辑器复制出来的，随本仓库以 MIT 许可发布（[LICENSE](LICENSE)）。

来自 [Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects) 的样例不提交：其[许可](https://github.com/Scirra/Construct-Example-Projects/blob/main/LICENSE.txt)不允许把工程内容作为独立文件再分发。把该仓库克隆到同级目录，用 `scripts/extract_sample.py` 复现；索引以及工程文件与剪贴板输出之间的已知差异见 [docs/samples/official-samples.md](docs/samples/official-samples.md)。

## 相关仓库

| 仓库 | 内容 | 与本仓库的关系 |
|---|---|---|
| [XHXIAIEIN/Construct3-RAG](https://github.com/XHXIAIEIN/Construct3-RAG) | 插件、行为、特效的 JSON schema | ACE id 和参数 id 的来源。克隆到同级目录后 `scripts/check_ace_refs.py` 会读取它。 |
| [XHXIAIEIN/Construct3-Copilot](https://github.com/XHXIAIEIN/Construct3-Copilot) | 生成 Intent IR 的助手 | 调用本服务的 `/generate`、`/validate` 和 `/health`。 |
| [Scirra/Construct-Example-Projects](https://github.com/Scirra/Construct-Example-Projects) | 官方示例的文件夹工程 | 克隆到同级目录后 `scripts/extract_sample.py` 和 `tests/test_real_samples.py` 会读取它。 |

"同级目录"指与本仓库并列的目录，例如 `../Construct3-RAG` 和 `../Construct-Example-Projects`。

## 开发

```bash
python -m pytest -q
python -m compileall -q src scripts tests
python scripts/check_ace_refs.py
```

`tests/test_real_samples.py` 会验证 `docs/samples/` 下的每个文件；示例工程在同级目录时，还会验证 `official-samples.md` 列出的每个片段，否则跳过这些用例。
