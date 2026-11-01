from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys, os

FD = os.path.join(os.path.dirname(__file__), "fonts")
W, H = 1000, 1500
NAVY = (13, 43, 62)
NAVY2 = (19, 58, 82)
GOLD = (201, 162, 39)
GOLD_L = (232, 200, 110)
CREAM = (251, 247, 238)
TEXT = (51, 51, 51)

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
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
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

def make(out, label, title, subtitle, bullets, cta, site, note):
    img = Image.new("RGB", (W, H), NAVY)
    # vertical gradient
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY2[i] * (1 - t) + NAVY[i] * t) for i in range(3))
        gd.line([(0, y), (W, y)], fill=c)
    img = grad
    # soft golden glow ("nour" = light)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([W - 480, -260, W + 260, 480], fill=(60, 110, 145, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)

    # thin gold frame
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=26, outline=GOLD + (255,), width=2)

    # label with side rules
    lf = inter(28, "SemiBold")
    y = 140
    lw = center_text(d, y, label, lf, GOLD, spacing=5)
    ly = y + 18
    d.line([(W / 2 - lw / 2 - 90, ly), (W / 2 - lw / 2 - 24, ly)], fill=GOLD, width=2)
    d.line([(W / 2 + lw / 2 + 24, ly), (W / 2 + lw / 2 + 90, ly)], fill=GOLD, width=2)

    # title
    tf = lora(96, 700)
    lines = [l for part in title.split('\n') for l in wrap(d, part, tf, W - 170)]
    y = 240
    for ln in lines:
        center_text(d, y, ln, tf, CREAM)
        y += 112
    # subtitle
    sf = lora(56, 500, italic=True)
    y += 8
    for ln in wrap(d, subtitle, sf, W - 170):
        center_text(d, y, ln, sf, GOLD_L)
        y += 70

    # divider diamond
    y += 30
    d.line([(W / 2 - 110, y), (W / 2 - 16, y)], fill=GOLD, width=2)
    d.line([(W / 2 + 16, y), (W / 2 + 110, y)], fill=GOLD, width=2)
    d.polygon([(W / 2, y - 8), (W / 2 + 8, y), (W / 2, y + 8), (W / 2 - 8, y)], fill=GOLD)
    y += 50

    # cream card with checklist
    size = 40
    bf = inter(size, "Medium")
    while max(d.textlength(b, font=bf) for b in bullets) > (W - 220 - 124 - 40) and size > 30:
        size -= 1
        bf = inter(size, "Medium")
    row_h = 92
    card_h = 60 + row_h * len(bullets)
    cx0, cx1 = 110, W - 110
    d.rounded_rectangle([cx0, y, cx1, y + card_h], radius=28, fill=CREAM)
    ry = y + 38
    for b in bullets:
        cy = ry + 24
        d.ellipse([cx0 + 50, cy - 24, cx0 + 98, cy + 24], fill=GOLD)
        # check mark
        d.line([(cx0 + 62, cy + 1), (cx0 + 71, cy + 11), (cx0 + 88, cy - 10)], fill=NAVY, width=6, joint="curve")
        d.text((cx0 + 124, cy - 26), b, font=bf, fill=NAVY)
        ry += row_h
    y += card_h + 80

    # CTA pill
    cf = inter(42, "SemiBold")
    cw = d.textlength(cta, font=cf)
    pw, ph = cw + 110, 96
    px0 = (W - pw) / 2
    d.rounded_rectangle([px0, y, px0 + pw, y + ph], radius=ph / 2, fill=GOLD)
    d.text((px0 + 55, y + 22), cta, font=cf, fill=NAVY)
    y += ph + 40

    # book mention
    mf = lora(34, 400, italic=True)
    center_text(d, y, note, mf, CREAM)

    # footer anchored at bottom
    fy = H - 150
    d.line([(W / 2 - 60, fy), (W / 2 + 60, fy)], fill=GOLD, width=2)
    wf = inter(34, "Medium")
    center_text(d, fy + 30, site, wf, GOLD_L, spacing=3)

    img.convert("RGB").save(out, quality=92)
    print("saved", out, "last y", y)

if __name__ == "__main__" and len(sys.argv) > 2:
    import json
    for spec in json.load(open(sys.argv[2], encoding="utf-8")):
        make(os.path.join(sys.argv[1], spec["file"]), spec["label"], spec["title"], spec["subtitle"],
             spec["bullets"], spec["cta"], "nourpages.com", spec["note"])
elif __name__ == "__main__":
    make(sys.argv[1],
         "SANTÉ & BIEN-ÊTRE",
         "Pourquoi les régimes ne marchent pas",
         "(et quoi faire à la place)",
         ["Comprendre l’effet yo-yo", "8 habitudes durables", "Sans interdits ni privation"],
         "Lire l’article  →",
         "nourpages.com",
         "Inspiré du livre « Ventre Plat Sans Régime Miracle »")
