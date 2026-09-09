# Deprecated Features

Do NOT use these. Use the alternatives instead.

## Deprecated

| Feature | Use Instead |
|---------|-------------|
| Function plugin (`objectClass: "Function"`) | Built-in Functions system |
| Pin behavior | Hierarchies (`add-child` action) |
| Fade behavior | Tween behavior (`property: "offsetOpacity"`) |

## Function Plugin → Functions System

The deprecated Function plugin was an object type named `Function` whose ACEs took the
function name as an expression. It no longer ships with Construct 3 and has no entry in the
RAG schema, so do not emit any `"objectClass": "Function"` ACE. Built-in functions replace it:
define the function with a `function-block` event and call it with a `callFunction` action.

```json
// NEW: define
{"functionName": "MyFunc", "functionDescription": "", "functionCategory": "", "functionReturnType": "number",
 "functionCopyPicked": false, "functionIsAsync": false,
 "functionParameters": [{"name": "param1", "type": "number", "initialValue": "0", "comment": ""}],
 "eventType": "function-block", "conditions": [], "actions": [...]}

// NEW: call from an actions array (positional parameters)
{"callFunction": "MyFunc", "parameters": ["100"]}

// NEW: call in an expression
"value": "Functions.MyFunc(100)"
```

## Pin → Hierarchies

```json
// OLD (deprecated)
{"id": "pin-to-object", "objectClass": "Weapon", "behaviorType": "Pin", "parameters": {...}}

// NEW (use this)
{"id": "add-child", "objectClass": "Player", "parameters": {
  "child": "Weapon", "transform-x": true, "transform-y": true, "transform-z-elevation": false, "transform-w": false, "transform-h": false, "transform-a": true, "transform-o": false, "transform-visibility": false, "destroy-with-parent": true}}
```

## Fade → Tween

```json
// OLD (deprecated)
Use Fade behavior properties

// NEW (use this)
{"id": "tween-one-property", "objectClass": "Sprite", "behaviorType": "Tween", "parameters": {
  "tags": "\"fade\"", "property": "offsetOpacity", "end-value": "0", "time": "0.5", "ease": "in-out-sine", "destroy-on-complete": "yes"}}
```
