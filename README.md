# XLVII — A Curated Archive

An immersive, museum-quality 3D portfolio built with **Three.js + GSAP**, no build step, deployable as a fully static site.

> This is a working first build of the brief, not a mockup. It runs today. Magazine covers, CD art, and pages currently use **procedurally generated editorial placeholders** (you said media couldn't be uploaded yet) — swapping in real images is a content-file change, not a code change.

---

## Run / Deploy

It's a static site. Nothing to compile.

- **Locally:** open `index.html` directly, or serve the folder (`python3 -m http.server`) to enable the JSON content loading.
- **GitHub Pages:** push this folder to a repo, enable Pages on the branch root. Done.
- **Netlify / Vercel:** drag-and-drop the folder, or point at the repo with no build command and the folder as the publish directory.

When opened over `file://`, browsers block `fetch()` of the JSON files, so the site **automatically falls back** to built-in placeholder content (21 magazines + 13 CDs) so it still looks complete. Served over HTTP (Pages/Netlify/Vercel/local server), it reads the real `content/` files.

---

## Information Architecture

```
Archive (single immersive scene)
├── Magazines  — 21 editions, the floating gallery wall (default view)
│     └── Edition → Focus (camera fly-in) → Open → Flipbook reader
├── Music      — 13 releases, floating collectible sleeves + discs
│     └── Release → Detail panel (artwork, notes, links)
└── Studio     — about overlay
```

Navigation **is** the objects. The top bar only switches between the two rooms (Magazines / Music) and Studio. Everything else is spatial.

## Scene Design

- **Environment:** black void with exponential fog for depth, a shadow-catching back wall, and a faint reflective floor. PBR reflections come from a `RoomEnvironment` PMREM map.
- **Layout:** magazines hang as a 3 (mobile) / 7 (desktop)-column floating grid with per-object z-jitter, rotation, and float phase. CDs use a looser square-sleeve grid with a metallic disc peeking out.
- **Camera:** a single perspective camera with a custom rig — idle drift + pointer parallax keep it alive; drag pans within clamped bounds; wheel/pinch dollies. Selecting a magazine flies the camera to a fixed presentation pose.
- **Lighting:** ambient + hemisphere base, a shadow-casting key spotlight (PCFSoft), a cool rim light, and a warm point accent. The key light target follows the pan for consistent shadows.

## Component Architecture

| Concern | Where |
| --- | --- |
| Content (JSON, with procedural fallback) | `loadContent()` / `fallbackContent()` |
| Texture pipeline (covers, spines, pages, CD art) | the canvas `*Tex()` factory |
| Scene / lights / env | scene setup block |
| Object builders | `buildMagazines()`, `buildCDs()` (lazy) |
| Selection & cinematic focus | `selectObject()` / `releaseFocus()` |
| Flipbook | `buildBook()` / `turnTo()` + drag handlers |
| Music detail | `openDetail()` |
| Room switching | `switchSection()` |
| Loader → boot | `boot()` |

## Interaction Design

- **Hover:** object lifts toward the camera, scales up, accent recolors the UI, a cursor-following label fades in.
- **Magazine select:** siblings recede and fade, the chosen edition flies forward and squares up, an "Open Edition / Back" bar appears.
- **Open:** crossfade into the DOM flipbook — click halves, drag-to-turn (forward and back), swipe on touch, arrow keys, page counter, PDF + Share actions.
- **CD select:** slide-in detail panel with artwork, spec rows, notes, and links.
- **Mobile:** touch-first — tap to select, drag to pan, pinch to dolly, swipe to turn pages; labels and dense HUD copy are suppressed for clarity.

## Performance Plan

- Pixel ratio capped at 2; shadow map scaled down on mobile.
- Shared page/edge textures across all 21 magazines (one upload, not 21).
- CD room is **built lazily** on first visit; the inactive room is hidden (culled).
- Raycasting is throttled and limited to the active room's meshes, and disabled during focus/reading.
- Procedural textures mean zero network image weight until you add real assets.

---

## Adding & editing content (no code changes)

All content lives in `content/`. To add an edition:

1. Create `content/magazines/magazine-22.json` (copy an existing one).
2. Add its path to the `magazines` array in `content/index.json`.

Same pattern for CDs via `content/cds/` and the `cds` array.

### Magazine fields
`id, issue, roman, title, category, year, accent` (hex), optional `pdf` (URL) and `link`, and a `pages` array. Page `type` is one of `cover | editorial | image | video`, with `kick, title, body, media` (label text), optional `image`, and `link`.

### CD fields
`id, catalog, title, artist, year, format, accent, art, notes, links[]`.

### Dropping in real media
The placeholders are generated in-canvas. To use real images, replace the relevant `*Tex()` function with a `THREE.TextureLoader().load(data.cover)` and point the JSON `image` / `art` paths at files you add under `assets/`. The JSON already carries the fields (`image`, `art`, `pdf`) so the structure won't change.

---

## Honest status

Implemented and working: the 3D gallery, hover/focus/selection with cinematic camera transitions, the flipbook (click + drag + swipe + keys), the music room and detail panels, mobile gestures, the loader sequence, JSON content + fallback, share/deep-link via URL hash.

Scaffolded for you to extend: real cover/art images (placeholders today), inline `<video>` and PDF embeds (the slots and buttons exist; wire to your files), and true page-curl physics (current turns are GSAP rotations with curl shading — convincing and fast; a WebGL page-bend shader can be added later if you want it). These were called out because the brief is large and I'd rather ship a real foundation than a fake demo.
