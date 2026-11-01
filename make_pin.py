"""Générateur d'épingles Pinterest NourPages (1000 x 1500 px).

Usage : python3 make_pin.py <dossier_de_sortie> <specs.json>
specs.json : liste d'objets {file, label, title, subtitle, bullets, cta, note}.
Dans title, "\n" force un retour à la ligne.
Affiche un rapport JSON : une ligne par image, avec "ok": true si tout tient dans l'image.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import os
import sys

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
W, H = 1000, 1500
NAVY = (13, 43, 62)
NAVY2 = (19, 58, 82)
GOLD = (201, 162, 39)
GOLD_L = (232, 200, 110)
CREAM = (251, 247, 238)
FOOTER_Y = H - 150          # filet doré au-dessus de nourpages.com
NOTE_MAX_BOTTOM = FOOTER_Y - 20


def lora(size, wght=700, italic=False):
    f = ImageFont.truetype(os.path.join(FD, "Lora-Italic-Variable.ttf" if italic else "Lora-Variable.ttf"), size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def inter(size, style="SemiBold"):
    return ImageFont.truetype(os.path.join(FD, f"Inter-{style}.otf"), size)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def center_text(draw, y, text, font, fill, spacing=0):
    if spacing:
        total = sum(draw.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)
        x = (W - total) / 2
        for c in text:
            draw.text((x, y), c, font=font, fill=fill)
            x += draw.textlength(c, font=font) + spacing
        return total
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)
    return w


def fit_font(draw, texts, maker, start, minimum, maxw):
    size = start
    f = maker(size)
    while max(draw.textlength(t, font=f) for t in texts) > maxw and size > minimum:
        size -= 1
        f = maker(size)
    return f, max(draw.textlength(t, font=f) for t in texts) <= maxw


def background():
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / H
        gd.line([(0, y), (W, y)], fill=tuple(int(NAVY2[i] * (1 - t) + NAVY[i] * t) for i in range(3)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W - 480, -260, W + 260, 480], fill=(60, 110, 145, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(grad.convert("RGBA"), glow)


def render(spec, title_size):
    img = background()
    d = ImageDraw.Draw(img)
    ok = True
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=26, outline=GOLD + (255,), width=2)

    # étiquette
    lf = inter(28, "SemiBold")
    y = 140
    lw = center_text(d, y, spec["label"], lf, GOLD, spacing=5)
    d.line([(W / 2 - lw / 2 - 90, y + 18), (W / 2 - lw / 2 - 24, y + 18)], fill=GOLD, width=2)
    d.line([(W / 2 + lw / 2 + 24, y + 18), (W / 2 + lw / 2 + 90, y + 18)], fill=GOLD, width=2)

    # titre
    tf = lora(title_size, 700)
    lines = [l for part in spec["title"].split("\n") for l in wrap(d, part, tf, W - 170)]
    if any(d.textlength(l, font=tf) > W - 170 for l in lines):
        ok = False
    y = 240
    for ln in lines:
        center_text(d, y, ln, tf, CREAM)
        y += int(title_size * 1.17)

    # sous-titre
    if spec.get("subtitle"):
        sf = lora(56 if title_size >= 88 else 50, 500, italic=True)
        y += 8
        for ln in wrap(d, spec["subtitle"], sf, W - 170):
            center_text(d, y, ln, sf, GOLD_L)
            y += int(sf.size * 1.25)

    # séparateur
    y += 30
    d.line([(W / 2 - 110, y), (W / 2 - 16, y)], fill=GOLD, width=2)
    d.line([(W / 2 + 16, y), (W / 2 + 110, y)], fill=GOLD, width=2)
    d.polygon([(W / 2, y - 8), (W / 2 + 8, y), (W / 2, y + 8), (W / 2 - 8, y)], fill=GOLD)
    y += 50

    # carte crème avec la liste
    bullets = spec["bullets"]
    bf, fits = fit_font(d, bullets, lambda s: inter(s, "Medium"), 40, 30, W - 220 - 124 - 40)
    ok = ok and fits
    row_h = 92
    card_h = 60 + row_h * len(bullets)
    cx0, cx1 = 110, W - 110
    d.rounded_rectangle([cx0, y, cx1, y + card_h], radius=28, fill=CREAM)
    ry = y + 38
    for b in bullets:
        cy = ry + 24
        d.ellipse([cx0 + 50, cy - 24, cx0 + 98, cy + 24], fill=GOLD)
        d.line([(cx0 + 62, cy + 1), (cx0 + 71, cy + 11), (cx0 + 88, cy - 10)], fill=NAVY, width=6, joint="curve")
        d.text((cx0 + 124, cy - 26), b, font=bf, fill=NAVY)
        ry += row_h
    y += card_h + 80

    # bouton
    cf = inter(42, "SemiBold")
    cta = spec["cta"]
    cw = d.textlength(cta, font=cf)
    pw, ph = cw + 110, 96
    px0 = (W - pw) / 2
    d.rounded_rectangle([px0, y, px0 + pw, y + ph], radius=ph / 2, fill=GOLD)
    d.text((px0 + 55, y + 22), cta, font=cf, fill=NAVY)
    y += ph + 40

    # mention du livre
    if spec.get("note"):
        mf, fits = fit_font(d, [spec["note"]], lambda s: lora(s, 400, italic=True), 34, 24, W - 140)
        ok = ok and fits
        center_text(d, y, spec["note"], mf, CREAM)
        y += mf.size + 8

    # pied de page
    d.line([(W / 2 - 60, FOOTER_Y), (W / 2 + 60, FOOTER_Y)], fill=GOLD, width=2)
    center_text(d, FOOTER_Y + 30, "nourpages.com", inter(34, "Medium"), GOLD_L, spacing=3)
    return img, ok, y, len(lines)


def make(out_path, spec):
    for size in (96, 90, 84, 78, 72, 66, 60):
        img, ok, bottom, nlines = render(spec, size)
        if bottom <= NOTE_MAX_BOTTOM and nlines <= 4:
            break
    ok = ok and bottom <= NOTE_MAX_BOTTOM
    img.convert("RGB").save(out_path, quality=90)
    return {"file": os.path.basename(out_path), "ok": ok, "title_size": size, "title_lines": nlines}


if __name__ == "__main__":
    out_dir, specs_path = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    report = [make(os.path.join(out_dir, s["file"]), s) for s in json.load(open(specs_path, encoding="utf-8"))]
    print(json.dumps(report, ensure_ascii=False))
    sys.exit(0 if all(r["ok"] for r in report) else 1)
