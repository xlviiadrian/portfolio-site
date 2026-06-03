# XLVII MEDIA — Build Continuation Notes

This is an immersive 3D portfolio gallery site for **XLVII MEDIA** (Adrian Medina).
Stack: **Three.js + GSAP**, single self-contained `index.html`, fully static, deploy to any host.

## ▶ How to resume this build in a NEW chat
1. Upload **this whole `xlvii-gallery.zip`** (it contains everything — code + assets).
2. Upload the next **magazine PDF(s)**.
3. Say: *"Continue the XLVII MEDIA build — extract the zip and add this PDF to magazine N."*
   The assistant will unzip it, see all current code/assets, and pick up exactly here.
   (Chat memory alone does NOT carry the files — the zip is the source of truth.)

## Project structure
- `index.html` — the entire app (Three.js scene, flipbook reader, overlays). Self-contained.
- `assets/covers/magazine-01..21-cover.jpg` — 3D box cover art (also embedded inline in index.html).
- `assets/cds/cd-01..14.jpg` — CD sleeve art (also embedded inline).
- `assets/magazines/NN/pages/p-XX.jpg` — rendered flipbook pages (1280×1600 / 1200×1600).
- `assets/magazines/NN/portfolio.pdf` — compressed downloadable PDF per magazine.
- `content/index.json` — manifest listing which magazine JSON overrides to load.
- `content/magazines/magazine-NN.json` — per-magazine override (PDF wiring; merged by id).

## Status
### Magazines (21 total, real titles wired in fallbackContent())
- PDFs DONE & wired (flipbooks): **01, 02, 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21**
  - 01 = 80pp · 02 = 11pp · 03 = 17pp (special "w.i.p" cover as p-01, PDF as p-02..17)
    · 04 = 47pp · 05 = 21pp · 06 = 11pp · 13 = 10pp · 19 = 7pp · 20 = 9pp · 21 = 48pp
- **FLYERS** (single image lightbox, `flyer:true`, NOT the flipbook): **08, 17, 18**
  - 18 = FADED DECADE "STOMP" T-Shirt — flyer image is page 1 of the PDF, baked into
    `assets/covers/magazine-18-cover.jpg` AND `EMBEDDED_COVERS['magazine-18']`.
- PENDING PDFs: none outstanding except **08** (user wanted a real PDF flipbook for it
  "instead of the flyer popup", but no magazine-08 PDF was supplied — still a flyer for now).

### CDs (14, real metadata + Listen links)
- Art order assumed = upload order (cd-01..14). **User to confirm any mismatched cover↔title.**

### Tabs: Magazines · Music · Media (YouTube grid, 12 videos) · About · Contact. All mobile-responsive.

### PENDING / TODO
- Add remaining magazine PDFs (07–16, 18–21).
- Verify CD cover↔title pairing.
- **External storage refactor** (do this AFTER all PDFs are in): move `assets/magazines/NN/`
  to Cloudflare R2 (free, zero egress) or Backblaze B2; point `pagesPath`/`pdf` at the bucket URL
  so the repo stays light. Plan: add one `ASSET_BASE` constant, rewrite JSON paths, provide an
  upload script + guide. (User creates the bucket + uploads; assistant preps code/script.)

## How to add a magazine PDF (exact recipe)
```bash
N=07   # magazine number, zero-padded
mkdir -p assets/magazines/$N/pages
# rasterize to 1600px-tall page JPEGs (NOTE: use -scale-to 1600, NOT -scale-to-x)
pdftoppm -jpeg -jpegopt quality=82,optimize=y -scale-to 1600 INPUT.pdf assets/magazines/$N/pages/p
# build a compressed downloadable PDF from the rendered pages (PIL), then:
```
Create `content/magazines/magazine-$N.json`:
```json
{ "id":"magazine-07", "pdf":"assets/magazines/07/portfolio.pdf",
  "pdfPages":<count>, "pagesPath":"assets/magazines/07/pages/p-" }
```
Add its path to `content/index.json` → `magazines[]`. Re-zip. Done.

## Key technical notes
- **Spreads**: desktop shows two-page spreads (cover alone, then 2–3, 4–5…). Odd page counts are
  clamped so the book never ends on a blank back (`maxCur = even? nLeaves : nLeaves-1`).
- **Mobile**: flipbook switches to one full-width page at a time (`R.single`); `isMobile` decided at load.
- **Pan/drag range**: `computePanLimit()` derives the drag bounds from the actual grid extent per
  section, so the whole layout is reachable (esp. tall mobile grid).
- **Hover**: blended `lift` value (no tilt-stick); seamless return to the floating position.
- **Serve it**: page images/PDFs/Media thumbnails load over HTTP — must be hosted/served (not file://).
- Validate JS after edits: extract the `<script type="module">` and run `node --check`.


## Status update (this session)
- Magazine 08 -> now an 8/13-page FLIPBOOK (from MAGAZINE_8-compressed.pdf, 13pp). No longer a flyer.
- Magazine 18 -> now an 8-page FLIPBOOK (from MAGAZINE_18.pdf). No longer a flyer.
- Flyers remaining: ONLY magazine 17 (Z-RO Mo City Don).
- Manifest content/index.json now lists 01-21 except 17 (17 stays a built-in flyer; not in manifest).
