# Assettaginator v3 — Code128 asset tags with contact email + CutContour

Print-ready, vector PDFs of **30 asset tags per page** (3×10 grid on US Letter).
Each label is **2.00" × 0.75"** with:

* Top line: contact email (e.g., `example-e-mail@email.com`)
* Middle: **Code-128** barcode
* Bottom: human-readable number (e.g., `#1000`)
* **Rounded-corner CutContour** path for contour cutting in VersaWorks (spot color `CutContour`)

No logo. No background fills (transparent/clear background so you can print on any media).

---

## Install

```bash
python -m pip install reportlab
```

(Optional but recommended: create a virtual environment first.)

---

## Quick start (CLI)

From your project folder:

```bash
python assettaginator_v3.py \
  --contact "foundthis@boom.aero" \
  --start 1000 --count 30 \
  --outfile assettaginator_v3_sheet.pdf \
  --module-in 0.009 --max-module-in 0.0105 --fill-pct 0.98 \
  --corner-radius-in 0.08 --cut-stroke-pt 0.25
```

**What this does:** generates one US-Letter page with 30 tags (#1000–#1029), using thinner bars that expand to fill the label width, with a rounded-corner `CutContour` around each tag.

---

## Bulk from CSV

Your CSV should have at least one column named `asset_id`:

```csv
asset_id
1000
1001
2000
2001
```

Run:

```bash
python assettaginator_v3.py --csv assets.csv --id-column asset_id \
  --contact "foundthis@boom.aero" \
  --outfile assettaginator_v3_bulk.pdf \
  --module-in 0.009 --max-module-in 0.0105 --fill-pct 0.98 \
  --corner-radius-in 0.08 --cut-stroke-pt 0.25
```

The same contact email is used on every tag. (If you want per-row contacts later, we can add a column and flag for that.)

---

## Key options (tunables)

* `--contact` — Text shown at the top (lost-and-found email).
* `--module-in` — Barcode module (bar) width in **inches** (smaller = thinner bars). Try `0.0085–0.011`.
* `--max-module-in` — Upper limit for module width when expanding to fill the label.
* `--fill-pct` — How much of the label’s usable width the barcode should occupy (e.g., `0.96–0.99`).
* `--corner-radius-in` — Rounded corner radius for the cut path (inches). Default `0.08`.
* `--cut-stroke-pt` — Stroke width (points) for the cut path. Default `0.25` (hairline).
* `--no-hash` — Omit the leading `#` in the human-readable number (defaults to showing it).
* **Layout controls** (if you need them): `--cols`, `--rows`, `--label-width-in`, `--label-height-in`,
  `--left-margin-in`, `--top-margin-in`, `--hgap-in`, `--vgap-in`.

> Background stays transparent: the script never draws filled rectangles behind the barcode or text.

---

## Notes for VersaSTUDIO BN2-20A / VersaWorks

* The contour cut path is a **vector stroke** with the **spot color name `CutContour`** (case-sensitive). VersaWorks will recognize it automatically.
* Keep **no fill** on the cut path (the script draws a stroke only). It is drawn **after** the barcode/text so it sits on top.
* PDFs are vector; VersaWorks rasterizes at device DPI (up to 1440 dpi).
* If scanning is finicky after print/lamination:

  * Bump `--module-in` up slightly (e.g., `0.010`) to thicken bars, **or**
  * Reduce `--fill-pct` a touch (e.g., `0.96`) to increase quiet zones on the sides.

---

## Defaults & layout

* Page size: **US Letter**; grid **3×10** = 30 labels/page.
* Label size: **2.00" × 0.75"** (19.05 mm height).
* Numbering: starts at **1000** by default; change with `--start` and `--count`.

---

## Examples

**Two pages (60 tags total), starting at #2000:**

```bash
python assettaginator_v3.py \
  --contact "foundthis@boom.aero" \
  --start 2000 --count 60 \
  --outfile assettaginator_v3_2000-2059.pdf \
  --module-in 0.0095 --max-module-in 0.011 --fill-pct 0.97 \
  --corner-radius-in 0.08 --cut-stroke-pt 0.25
```

**CSV bulk with slightly thicker bars and more quiet zone:**

```bash
python assettaginator_v3.py --csv assets.csv --id-column asset_id \
  --contact "foundthis@boom.aero" \
  --outfile assettaginator_v3_bulk_quiet.pdf \
  --module-in 0.010 --max-module-in 0.011 --fill-pct 0.96 \
  --corner-radius-in 0.1 --cut-stroke-pt 0.25
```

---

## Troubleshooting

* **“ModuleNotFoundError: reportlab”** → `python -m pip install reportlab` (or install inside a venv).
* **Email overlaps the barcode** → shouldn’t happen; the email auto-shrinks. If you use very long text, shorten it or increase `--label-width-in`.
* **Cut doesn’t trigger** → verify spot name **`CutContour`** in VersaWorks, ensure the path is a stroke (no fill), and that “Cut Contour” is enabled in your print job settings.

---

Happy tagging! 😊
