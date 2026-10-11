import math, os
from PIL import Image, ImageDraw, ImageFont

FW = '/home/claude/fontwork/node_modules/@fontsource/'
GF = '/usr/share/fonts/truetype/google-fonts/'


def fs(name):
    return FW + name + '/files/' + name + '-latin-400-normal.woff'


F = {
    'Shrikhand': fs('shrikhand'),
    'Alfa Slab One': fs('alfa-slab-one'),
    'Caveat Brush': fs('caveat-brush'),
    'Lilita One': fs('lilita-one'),
    'Lobster': fs('lobster'),
    'Permanent Marker': fs('permanent-marker'),
}
POP_B = GF + 'Poppins-Bold.ttf'
POP_M = GF + 'Poppins-Medium.ttf' if os.path.exists(GF + 'Poppins-Medium.ttf') else POP_B

# palette
GREEN = (0, 104, 71)
RED = (200, 16, 46)
CREAM = (255, 244, 220)
MARI = (255, 183, 3)
PINK = (228, 0, 124)
TEAL = (0, 150, 150)
TERRA = (196, 87, 43)
DARK = (30, 30, 30)


def fit_w(path, txt, w):
    f = ImageFont.truetype(path, 200)
    l, t, r, b = f.getbbox(txt)
    return ImageFont.truetype(path, max(8, int(200 * w / (r - l))))


def ctext(d, xy, txt, font, fill):
    d.text(xy, txt, font=font, fill=fill, anchor='mm')


def arc_text(img, txt, font, c, R, fill, top=True):
    """Place text along a circle of radius R around c. top=True: reads along the top; else along the bottom."""
    widths = [font.getlength(ch) for ch in txt]
    total = sum(widths)
    cum = 0
    for ch, w in zip(txt, widths):
        mid = cum + w / 2 - total / 2
        cum += w
        ang = mid / R  # radians
        l, t, r, b = font.getbbox(ch)
        gl = Image.new('RGBA', (int(w) + 40, int(b - t) + 40), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text((gl.width / 2, gl.height / 2), ch, font=font, fill=fill, anchor='mm')
        if top:
            x = c[0] + R * math.sin(ang)
            y = c[1] - R * math.cos(ang)
            gl = gl.rotate(-math.degrees(ang), resample=Image.BICUBIC, expand=True)
        else:
            x = c[0] + R * math.sin(ang)
            y = c[1] + R * math.cos(ang)
            gl = gl.rotate(math.degrees(ang), resample=Image.BICUBIC, expand=True)
        img.paste(gl, (int(x - gl.width / 2), int(y - gl.height / 2)), gl)


# ---------------------------------------------------------------- logo graphics
def circle_mask(size):
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    return m


def weli_graphic(bg, shawl, size=420):
    S = 4
    N = size * S
    u = N / 800.0
    lay = Image.new('RGBA', (N, N), bg)
    d = ImageDraw.Draw(lay)
    P = lambda *v: tuple(x * u for x in v)
    hair = (236, 234, 228)
    skin = (232, 178, 128)
    dk = (45, 30, 30)
    # shawl / shoulders
    d.ellipse(P(110, 560, 690, 1050), fill=shawl)
    for k, col in enumerate((CREAM, MARI)):
        d.ellipse(P(150 + 22 * k, 620 + 26 * k, 650 - 22 * k, 1060), outline=col, width=int(9 * u))
    # neck
    d.rectangle(P(360, 500, 440, 610), fill=(214, 156, 108))
    # hair back + bun
    d.ellipse(P(240, 160, 560, 480), fill=hair)
    d.ellipse(P(325, 70, 475, 220), fill=hair)
    d.arc(P(325, 70, 475, 220), 200, 340, fill=(200, 198, 192), width=int(7 * u))
    # face
    d.ellipse(P(275, 235, 525, 545), fill=skin)
    # hair front
    d.pieslice(P(268, 226, 532, 430), 180, 360, fill=hair)
    # earrings
    for ex in (268, 532):
        d.ellipse(P(ex - 12, 425, ex + 12, 449), fill=MARI)
    # cheeks
    d.ellipse(P(298, 455, 346, 492), fill=(240, 140, 128))
    d.ellipse(P(454, 455, 502, 492), fill=(240, 140, 128))
    # glasses
    gw = int(9 * u)
    d.ellipse(P(298, 362, 388, 444), outline=dk, width=gw)
    d.ellipse(P(412, 362, 502, 444), outline=dk, width=gw)
    d.line(P(388, 398, 412, 398), fill=dk, width=gw)
    # eyes
    for ex in (343, 457):
        d.ellipse(P(ex - 7, 396, ex + 7, 410), fill=dk)
    # smile
    d.arc(P(345, 425, 455, 510), 25, 155, fill=dk, width=int(9 * u))
    lay = lay.convert('RGBA')
    lay.putalpha(circle_mask(N))
    return lay.resize((size, size), Image.LANCZOS)


def chile(d, cx, cy, scale, body, stem):
    A = (cx - 80 * scale, cy - 105 * scale)
    B = (cx - 120 * scale, cy + 70 * scale)
    C = (cx + 110 * scale, cy + 115 * scale)
    pts_l, pts_r = [], []
    n = 60
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * A[0] + 2 * (1 - t) * t * B[0] + t * t * C[0]
        y = (1 - t) ** 2 * A[1] + 2 * (1 - t) * t * B[1] + t * t * C[1]
        dx = 2 * (1 - t) * (B[0] - A[0]) + 2 * t * (C[0] - B[0])
        dy = 2 * (1 - t) * (B[1] - A[1]) + 2 * t * (C[1] - B[1])
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        w = 46 * scale * (1 - t ** 1.6) ** 0.9 + 1
        pts_l.append((x + nx * w, y + ny * w))
        pts_r.append((x - nx * w, y - ny * w))
    d.polygon(pts_l + pts_r[::-1], fill=body)
    d.ellipse((A[0] - 38 * scale, A[1] - 22 * scale, A[0] + 38 * scale, A[1] + 26 * scale), fill=stem)
    d.line((A[0], A[1] - 10 * scale, A[0] - 14 * scale, A[1] - 62 * scale), fill=stem, width=int(20 * scale))


def olla_graphic(size=420):
    S = 3
    N = size * S
    u = N / 800.0
    lay = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    P = lambda *v: tuple(x * u for x in v)
    # steam
    for k, off in enumerate((-90, 0, 90)):
        pts = []
        top = 40 + (0 if k == 1 else 50)
        for i in range(41):
            t = i / 40
            y = 290 - t * (290 - top)
            x = 400 + off + 22 * math.sin(t * 2 * math.pi * 1.5 + k)
            pts.append((x * u, y * u))
        d.line(pts, fill=GREEN, width=int(20 * u), joint='curve')
        for (x, y) in (pts[0], pts[-1]):
            r = 10 * u
            d.ellipse((x - r, y - r, x + r, y + r), fill=GREEN)
    # ears (handles)
    d.arc(P(105, 430, 245, 560), 90, 270, fill=TERRA, width=int(28 * u))
    d.arc(P(555, 430, 695, 560), 270, 450, fill=TERRA, width=int(28 * u))
    # neck + rim
    d.rounded_rectangle(P(300, 290, 500, 400), radius=int(30 * u), fill=TERRA)
    d.rounded_rectangle(P(265, 270, 535, 330), radius=int(30 * u), fill=(214, 110, 62))
    # body
    d.ellipse(P(130, 330, 670, 760), fill=TERRA)
    # decorative bands
    d.rectangle(P(150, 505, 650, 525), fill=CREAM)
    d.rectangle(P(150, 580, 650, 600), fill=CREAM)
    for i in range(10):
        x0 = 195 + i * 45
        d.polygon(P(x0, 580, x0 + 22, 530, x0 + 44, 580), fill=TEAL)
    # clip band overflow to the body ellipse
    body_mask = Image.new('L', (N, N), 0)
    bm = ImageDraw.Draw(body_mask)
    bm.ellipse(P(130, 330, 670, 760), fill=255)
    bm.rounded_rectangle(P(300, 290, 500, 400), radius=int(30 * u), fill=255)
    bm.rounded_rectangle(P(265, 270, 535, 330), radius=int(30 * u), fill=255)
    bm.rectangle(P(0, 0, 800, 270), fill=255)
    bm.arc(P(105, 430, 245, 560), 90, 270, fill=255, width=int(28 * u))
    bm.arc(P(555, 430, 695, 560), 270, 450, fill=255, width=int(28 * u))
    a = lay.getchannel('A')
    from PIL import ImageChops
    lay.putalpha(ImageChops.multiply(a, body_mask))
    return lay.resize((size, size), Image.LANCZOS)


def stamp_graphic(size=520):
    S = 3
    N = size * S
    lay = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = N / 2
    d.ellipse((0, 0, N - 1, N - 1), fill=CREAM)
    m = N * 0.025
    d.ellipse((m, m, N - 1 - m, N - 1 - m), fill=GREEN)
    m2 = N * 0.075
    d.ellipse((m2, m2, N - 1 - m2, N - 1 - m2), outline=CREAM, width=int(N * 0.008))
    inner = N * 0.30
    d.ellipse((c - inner, c - inner, c + inner, c + inner), fill=CREAM)
    chile(d, c - N * 0.012, c - N * 0.004, N / 800 * 1.22, RED, GREEN)
    f_top = ImageFont.truetype(F['Alfa Slab One'], int(N * 0.088))
    f_bot = ImageFont.truetype(POP_B, int(N * 0.046))
    arc_text(lay, 'LA WELIS', f_top, (c, c), N * 0.365, CREAM, top=True)
    arc_text(lay, 'COMIDA CASERA', f_bot, (c, c), N * 0.37, CREAM, top=False)
    return lay.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- sheet
CW, CH = 2400, 2080
canvas = Image.new('RGB', (CW, CH), (238, 236, 230))
d = ImageDraw.Draw(canvas)

d.text((100, 55), 'LA WELIS', font=ImageFont.truetype(F['Alfa Slab One'], 70), fill=DARK)
d.text((100, 150), 'Lettering and logo exploration  ·  Zapopan, Jalisco', font=ImageFont.truetype(POP_M, 30), fill=(95, 95, 95))

fH = ImageFont.truetype(POP_B, 36)
fL = ImageFont.truetype(POP_M, 26)

# --- fonts
d.text((100, 230), 'A  ·  LETTERING', font=fH, fill=DARK)
d.line((100, 285, 2300, 285), fill=(170, 168, 160), width=3)
vibes = {
    'Shrikhand': 'retro, friendly, tilted',
    'Alfa Slab One': 'sturdy, reads from far away',
    'Caveat Brush': 'hand-painted, homemade',
    'Lilita One': 'rounded, cheerful, clean',
    'Lobster': 'classic script, familiar',
    'Permanent Marker': 'like the poster in your photo',
}
for i, (name, path) in enumerate(F.items()):
    col, row = i % 3, i // 3
    x = 100 + col * 740
    y = 320 + row * 330
    d.rounded_rectangle((x, y, x + 700, y + 300), radius=26, fill=CREAM, outline=(210, 205, 190), width=3)
    f = fit_w(path, 'La Welis', 540)
    ctext(d, (x + 350, y + 125), 'La Welis', f, RED)
    d.text((x + 28, y + 226), name, font=ImageFont.truetype(POP_B, 26), fill=DARK)
    d.text((x + 28, y + 258), vibes[name], font=fL, fill=(105, 105, 105))

# --- logos
d.text((100, 1010), 'B  ·  LOGO CONCEPTS', font=fH, fill=DARK)
d.line((100, 1065, 2300, 1065), fill=(170, 168, 160), width=3)

cards = [
    ('1  ·  La Weli herself', GREEN),
    ('2  ·  Olla de barro', CREAM),
    ('3  ·  Sello (stamp)', RED),
]
for i, (label, bg) in enumerate(cards):
    x = 100 + i * 740
    y = 1100
    d.rounded_rectangle((x, y, x + 700, y + 850), radius=30, fill=bg, outline=(210, 205, 190), width=3)
    if i == 0:
        g = weli_graphic(MARI, PINK, 440)
        canvas.paste(g, (x + 130, y + 40), g)
        f = fit_w(F['Shrikhand'], 'La Welis', 520)
        ctext(d, (x + 350, y + 600), 'La Welis', f, CREAM)
        ctext(d, (x + 350, y + 705), 'COMIDA CASERA', ImageFont.truetype(POP_B, 34), MARI)
    elif i == 1:
        g = olla_graphic(440)
        canvas.paste(g, (x + 130, y + 40), g)
        f = fit_w(F['Alfa Slab One'], 'La Welis', 520)
        ctext(d, (x + 350, y + 595), 'La Welis', f, RED)
        ctext(d, (x + 350, y + 705), 'COMIDA CASERA', ImageFont.truetype(POP_B, 34), GREEN)
    else:
        g = stamp_graphic(560)
        canvas.paste(g, (x + 70, y + 40), g)
        ctext(d, (x + 350, y + 700), 'ZAPOPAN, JALISCO', ImageFont.truetype(POP_B, 34), CREAM)
    d.text((x + 28, y + 790), label, font=ImageFont.truetype(POP_B, 28), fill=(DARK if bg == CREAM else CREAM))

out = '/home/claude/la_welis_lettering_logos.png'
canvas.save(out)
print('saved', out, canvas.size)
