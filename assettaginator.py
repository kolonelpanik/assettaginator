
#!/usr/bin/env python3
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.graphics.barcode import code128
from reportlab.lib.colors import black

PAGE_W, PAGE_H = letter
def pt_in(v): return v * inch

def grid_positions(page_w, page_h, cols, rows, lw, lh, ml, mt, hg, vg):
    return [(ml + c*(lw+hg), page_h - mt - r*(lh+vg) - lh)
            for r in range(rows) for c in range(cols)]

def draw_label(c, x, y, w, h, contact_text, asset_value,
               module_in=0.010, max_module_in=0.012, fill_pct=0.96,
               show_hash=True):
    # Transparent background: draw nothing behind the graphics/text.
    pad_side = 0.04 * w
    pad_top = 0.08 * h
    pad_bottom = 0.08 * h
    gap_top_to_bar = 2.0
    gap_bar_to_bottom = 2.0

    # Top email (shrink-to-fit to avoid overlap)
    top_font, top_size = "Helvetica-Bold", 8.5
    c.setFillColor(black)
    c.setFont(top_font, top_size)
    max_text_width = w - 2*pad_side
    text = contact_text or ""
    size = top_size
    while c.stringWidth(text, top_font, size) > max_text_width and size > 6.5:
        size -= 0.2
    c.setFont(top_font, size)
    top_baseline = y + h - pad_top - size
    c.drawCentredString(x + w/2, top_baseline, text)

    # Bottom human-readable
    bottom_font, bottom_size = "Helvetica", 8
    c.setFont(bottom_font, bottom_size)
    human = f"#{str(asset_value).strip().lstrip('#')}" if show_hash else str(asset_value)
    c.drawCentredString(x + w/2, y + pad_bottom, human)

    # Barcode height within remaining area
    available_bar_height = (top_baseline - gap_top_to_bar) - (y + pad_bottom + bottom_size + gap_bar_to_bottom)
    bar_h = max(0.4 * h, min(available_bar_height, 0.62 * h))

    # Width control
    max_bar_w = w - 2*pad_side
    payload = str(asset_value).strip().lstrip("#")
    module_width = module_in * inch
    bc = code128.Code128(payload, barHeight=bar_h, barWidth=module_width, humanReadable=False)

    if bc.width > max_bar_w:
        scale = max_bar_w / bc.width
        bc = code128.Code128(payload, barHeight=bar_h, barWidth=module_width*scale, humanReadable=False)
    else:
        # Try to fill horizontally without exceeding max module width
        target_w = max_bar_w * fill_pct
        if bc.width < target_w:
            new_module = min(module_width * (target_w / bc.width), max_module_in * inch)
            bc = code128.Code128(payload, barHeight=bar_h, barWidth=new_module, humanReadable=False)

    bar_x = x + (w - bc.width)/2
    bar_bottom = y + pad_bottom + bottom_size + gap_bar_to_bottom
    bar_top = top_baseline - gap_top_to_bar
    bar_y = bar_bottom + ( (bar_top - bar_bottom - bar_h) / 2.0 )
    bc.drawOn(c, bar_x, bar_y)

def make_pdf_v2(out_path, start=1000, count=30, contact="foundthis@boom.aero",
                cols=3, rows=10, label_w_in=2.0, label_h_in=0.75,
                left_margin_in=0.5, top_margin_in=0.6, hgap_in=0.25, vgap_in=0.25,
                module_in=0.010, max_module_in=0.012, fill_pct=0.96,
                show_hash=True, crop_marks=False):
    lw, lh = pt_in(label_w_in), pt_in(label_h_in)
    ml, mt = pt_in(left_margin_in), pt_in(top_margin_in)
    hg, vg = pt_in(hgap_in), pt_in(vgap_in)

    pos = grid_positions(PAGE_W, PAGE_H, cols, rows, lw, lh, ml, mt, hg, vg)
    per_page = cols * rows
    c = canvas.Canvas(out_path, pagesize=letter)

    for i in range(count):
        if i and i % per_page == 0:
            c.showPage()
        x, y = pos[i % per_page]
        draw_label(c, x, y, lw, lh, contact, start + i,
                   module_in=module_in, max_module_in=max_module_in, fill_pct=fill_pct,
                   show_hash=show_hash)

        if crop_marks:
            cm = 0.07*inch; c.setLineWidth(0.25)
            c.line(x, y, x+cm, y);               c.line(x, y, x, y+cm)
            c.line(x+lw, y, x+lw-cm, y);         c.line(x+lw, y, x+lw, y+cm)
            c.line(x, y+lh, x+cm, y+lh);         c.line(x, y+lh, x, y+lh-cm)
            c.line(x+lw, y+lh, x+lw-cm, y+lh);   c.line(x+lw, y+lh, x+lw, y+lh-cm)

    c.save()

def make_from_csv_v2(csv_path, out_path, id_col="asset_id", contact="foundthis@boom.aero",
                     cols=3, rows=10, label_w_in=2.0, label_h_in=0.75,
                     left_margin_in=0.5, top_margin_in=0.6, hgap_in=0.25, vgap_in=0.25,
                     module_in=0.010, max_module_in=0.012, fill_pct=0.96,
                     show_hash=True, crop_marks=False):
    lw, lh = pt_in(label_w_in), pt_in(label_h_in)
    ml, mt = pt_in(left_margin_in), pt_in(top_margin_in)
    hg, vg = pt_in(hgap_in), pt_in(vgap_in)

    pos = grid_positions(PAGE_W, PAGE_H, cols, rows, lw, lh, ml, mt, hg, vg)
    per_page = cols * rows
    c = canvas.Canvas(out_path, pagesize=letter)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows_list = list(csv.DictReader(f))

    for i, row in enumerate(rows_list):
        if i and i % per_page == 0:
            c.showPage()
        x, y = pos[i % per_page]
        asset = str(row[id_col]).strip()
        draw_label(c, x, y, lw, lh, contact, asset,
                   module_in=module_in, max_module_in=max_module_in, fill_pct=fill_pct,
                   show_hash=show_hash)

        if crop_marks:
            cm = 0.07*inch; c.setLineWidth(0.25)
            c.line(x, y, x+cm, y);               c.line(x, y, x, y+cm)
            c.line(x+lw, y, x+lw-cm, y);         c.line(x+lw, y, x+lw, y+cm)
            c.line(x, y+lh, x+cm, y+lh);         c.line(x, y+lh, x, y+lh-cm)
            c.line(x+lw, y+lh, x+lw-cm, y+lh);   c.line(x+lw, y+lh, x+lw, y+lh-cm)

    c.save()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Assettaginator v2 - Code128 asset tags (2.0x0.75\") with contact email (no logo).")
    ap.add_argument("--outfile", default="assettaginator_v2.pdf")
    ap.add_argument("--contact", default="foundthis@boom.aero")
    ap.add_argument("--start", type=int, default=1000)
    ap.add_argument("--count", type=int, default=30)
    ap.add_argument("--csv", help="CSV path for bulk; expects a column named by --id-column.")
    ap.add_argument("--id-column", default="asset_id")
    ap.add_argument("--show-hash", action="store_true", default=True)
    ap.add_argument("--no-hash", dest="show_hash", action="store_false")
    # layout
    ap.add_argument("--cols", type=int, default=3); ap.add_argument("--rows", type=int, default=10)
    ap.add_argument("--label-width-in", type=float, default=2.0)
    ap.add_argument("--label-height-in", type=float, default=0.75)
    ap.add_argument("--left-margin-in", type=float, default=0.5)
    ap.add_argument("--top-margin-in", type=float, default=0.6)
    ap.add_argument("--hgap-in", type=float, default=0.25)
    ap.add_argument("--vgap-in", type=float, default=0.25)
    ap.add_argument("--crop-marks", action="store_true")
    # barcode tuning
    ap.add_argument("--module-in", type=float, default=0.010, help="Narrowest bar/module width in inches.")
    ap.add_argument("--max-module-in", type=float, default=0.012, help="Cap module width when expanding to fill.")
    ap.add_argument("--fill-pct", type=float, default=0.96, help="Target percentage of usable width to fill (0-1).")

    args = ap.parse_args()

    if args.csv:
        make_from_csv_v2(args.csv, args.outfile, id_col=args.id_column, contact=args.contact,
                         cols=args.cols, rows=args.rows,
                         label_w_in=args.label_width_in, label_h_in=args.label_height_in,
                         left_margin_in=args.left_margin_in, top_margin_in=args.top_margin_in,
                         hgap_in=args.hgap_in, vgap_in=args.vgap_in,
                         module_in=args.module_in, max_module_in=args.max_module_in, fill_pct=args.fill_pct,
                         show_hash=args.show_hash, crop_marks=args.crop_marks)
    else:
        make_pdf_v2(args.outfile, start=args.start, count=args.count, contact=args.contact,
                    cols=args.cols, rows=args.rows,
                    label_w_in=args.label_width_in, label_h_in=args.label_height_in,
                    left_margin_in=args.left_margin_in, top_margin_in=args.top_margin_in,
                    hgap_in=args.hgap_in, vgap_in=args.vgap_in,
                    module_in=args.module_in, max_module_in=args.max_module_in, fill_pct=args.fill_pct,
                    show_hash=args.show_hash, crop_marks=args.crop_marks)
