# Object Type Templates

## Choose the Right Object Type

| Object Type | Use Case | Example |
|-------------|----------|---------|
| **Sprite** | Single objects, characters, animated items | Player, Enemy, Coin, Bullet |
| **TiledBackground** | Large repeating textures | Ground, Water, Sky, Wall |
| **NinePatch** | Scalable UI elements | Button, Panel, Dialog box |
| **Tilemap** | Tile-based level design | Platformer terrain, RPG maps |
| **Text** | Display text | Score, Title, Instructions |

## Generate Placeholder imageData

`scripts/imagedata.py` prints a PNG data URI for a solid rectangle or circle:

```bash
# Rectangle (default shape)
python scripts/imagedata.py --color red --width 32 --height 32

# Circle
python scripts/imagedata.py --color blue --width 16 --height 16 --shape circle
```

**Colors**: red, green, blue, yellow, cyan, magenta, white, black, gray, orange, purple, brown,
pink, lime, navy, teal, gold, silver, transparent, or `#RRGGBB` / `#RRGGBBAA`.
**Shapes**: `rectangle`, `circle`. Converting an existing image file is not supported; paste
real artwork in the editor after creating the object.

## Folder Structure (recursive)

All templates below use `"folders":[]` (flat). For hierarchical organization, `folders` is **recursively nested**:

```json
"folders": [{
  "name": "Scene",
  "items": [ /* object-type at this level */ ],
  "subfolders": [{
    "name": "Enemies",
    "items": [ /* ... */ ],
    "subfolders": [ /* ...further nesting */ ]
  }]
}]
```

Each folder has exactly these 3 fields: `name` / `items` / `subfolders`. Top-level `items` array (sibling of `folders`) can stay empty when the entire tree lives under folders.

## Quick Reference

| Need | Color | Size | Shape |
|------|-------|------|-------|
| Player | blue | 32x32 | rectangle |
| Enemy | red | 32x32 | rectangle |
| Ball | yellow | 16x16 | circle |
| Paddle | green | 64x16 | rectangle |
| Wall/Ground | gray | 32x32 | rectangle |
| Bullet | orange | 8x8 | circle |
| Coin | yellow | 24x24 | circle |

## Sprite Template

Generate imageData first, then use this structure:

```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"{NAME}","plugin-id":"Sprite","isGlobal":false,"editorNewInstanceIsReplica":true,"instanceVariables":[],"behaviorTypes":[],"effectTypes":[],"animations":{"items":[{"frames":[{"width":{WIDTH},"height":{HEIGHT},"originX":0.5,"originY":0.5,"originalSource":"","exportFormat":"lossless","exportQuality":0.8,"fileType":"image/png","imageDataIndex":0,"useCollisionPoly":true,"duration":1,"tag":""}],"name":"Animation 1","isLooping":false,"isPingPong":false,"repeatCount":1,"repeatTo":0,"speed":5}],"subfolders":[],"name":"Animations"}}],"folders":[],"imageData":["{IMAGEDATA}"]}
```

**With Behavior** (add to behaviorTypes array):
```json
"behaviorTypes":[{"behaviorId":"Platform","name":"Platform"}]
"behaviorTypes":[{"behaviorId":"EightDir","name":"8Direction"}]
"behaviorTypes":[{"behaviorId":"Bullet","name":"Bullet"}]
"behaviorTypes":[{"behaviorId":"solid","name":"Solid"}]
```

---

## TiledBackground Template

For large repeating textures (ground, walls, water). Tiles seamlessly.

```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"{NAME}","plugin-id":"TiledBg","isGlobal":false,"editorNewInstanceIsReplica":true,"instanceVariables":[],"behaviorTypes":[],"effectTypes":[],"image":{"width":{WIDTH},"height":{HEIGHT},"originX":0.5,"originY":0.5,"originalSource":"","exportFormat":"lossless","exportQuality":0.8,"fileType":"image/png","imageDataIndex":0,"useCollisionPoly":true,"tag":""}}],"folders":[],"imageData":["{IMAGEDATA}"]}
```

**Note**: `scripts/imagedata.py` only makes solid fills; draw a tileable texture in the editor afterwards. Add Solid behavior if needed.

---

## NinePatch Template

For scalable UI (buttons, panels). Corners stay fixed, edges stretch.

```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"{NAME}","plugin-id":"NinePatch","isGlobal":false,"editorNewInstanceIsReplica":true,"instanceVariables":[],"behaviorTypes":[],"effectTypes":[],"image":{"width":{WIDTH},"height":{HEIGHT},"originX":0.5,"originY":0.5,"originalSource":"","exportFormat":"lossless","exportQuality":0.8,"fileType":"image/png","imageDataIndex":0,"useCollisionPoly":true,"tag":""}}],"folders":[],"imageData":["{IMAGEDATA}"]}
```

**Note**: Margins are set in the C3 editor after pasting. Image should have distinct corners.

---

## Tilemap Template

For tile-based levels. Uses a tileset image containing multiple tiles.

```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"{NAME}","plugin-id":"Tilemap","isGlobal":false,"editorNewInstanceIsReplica":true,"instanceVariables":[],"behaviorTypes":[],"effectTypes":[],"image":{"width":{WIDTH},"height":{HEIGHT},"originX":0.5,"originY":0.5,"originalSource":"","exportFormat":"lossless","exportQuality":0.8,"fileType":"image/png","imageDataIndex":0,"useCollisionPoly":true,"tag":""},"tile-collision-polys":{}}],"folders":[],"imageData":["{TILESET_IMAGEDATA}"]}
```

**Note**:
- Tileset image contains multiple tiles in a grid
- `tile-collision-polys` defines collision shapes per tile (empty `{}` = default boxes)
- Set tile size in C3 editor after pasting

---

## Single-Global Plugins (no imageData)

**Keyboard**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Keyboard","plugin-id":"Keyboard","singleglobal-inst":{"type":"Keyboard","properties":{},"tags":""}}],"folders":[]}
```

**Mouse**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Mouse","plugin-id":"Mouse","singleglobal-inst":{"type":"Mouse","properties":{},"tags":""}}],"folders":[]}
```

**Touch**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Touch","plugin-id":"Touch","singleglobal-inst":{"type":"Touch","properties":{},"tags":""}}],"folders":[]}
```

**Audio**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Audio","plugin-id":"Audio","singleglobal-inst":{"type":"Audio","properties":{"timescale-audio":false,"playback-rate-clamp-lo":0.5,"playback-rate-clamp-hi":4,"panning-model":"HRTF","distance-model":"inverse","ref-distance":600,"max-distance":10000,"rolloff-factor":1,"speed-of-sound":5000},"tags":""}}],"folders":[]}
```

---

## Non-World Objects (no imageData)

**Text**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Text","plugin-id":"Text","isGlobal":false,"editorNewInstanceIsReplica":true,"instanceVariables":[],"behaviorTypes":[],"effectTypes":[]}],"folders":[]}
```

**Array**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Array","plugin-id":"Arr","isGlobal":true,"nonworld-inst":{"type":"Array","properties":{"width":10,"height":1,"depth":1},"tags":""}}],"folders":[]}
```

**Dictionary**
```json
{"is-c3-clipboard-data":true,"type":"object-types","families":[],"items":[{"name":"Dictionary","plugin-id":"Dictionary","isGlobal":true,"nonworld-inst":{"type":"Dictionary","properties":{},"tags":""}}],"folders":[]}
```
