import math
from PIL import Image, ImageDraw, ImageFont

FW = '/home/claude/fontwork/node_modules/@fontsource/'
GF = '/usr/share/fonts/truetype/google-fonts/'
SHRI = FW + 'shrikhand/files/shrikhand-latin-400-normal.woff'
POP_B = GF + 'Poppins-Bold.ttf'
POP_M = GF + 'Poppins-Medium.ttf'

NAME = 'LA WERIS'
NAME_MIXED = 'La Weris'
GREEN = (0, 104, 71)
RED = (200, 16, 46)
CREAM = (255, 244, 220)
MARI = (255, 183, 3)
PINK = (228, 0, 124)
DARK = (30, 30, 30)

S = 2
W, H = 400, 1100
PAD = 8


def fit_font(path, txt, target_len):
    f = ImageFont.truetype(path, 200)
    l, t, r, b = f.getbbox(txt)
    return ImageFont.truetype(path, max(10, int(200 * target_len / (r - l))))


def vtext(txt, font, color):
    l, t, r, b = font.getbbox(txt)
    im = Image.new('RGBA', (r - l + 6, b - t + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - l, 3 - t), txt, font=font, fill=color)
    return im.rotate(-90, expand=True)


def prof(t):
    base = lambda x: 1 - 0.25 * (((x - 0.2) / 0.7) ** 1.8)
    if t < 0.2:
        u = (0.2 - t) / 0.2
        return math.sqrt(max(0.0, 1 - u * u))
    if t <= 0.78:
        return base(t)
    v = (t - 0.78) / 0.22
    return base(0.78) * max(0.0, 1 - v ** 1.8) ** 1.2


def weli_graphic(bg, shawl, size=420):
    SS = 4
    N = size * SS
    u = N / 800.0
    lay = Image.new('RGBA', (N, N), bg)
    d = ImageDraw.Draw(lay)
    P = lambda *v: tuple(x * u for x in v)
    hair = (236, 234, 228)
    skin = (232, 178, 128)
    dk = (45, 30, 30)
    d.ellipse(P(110, 560, 690, 1050), fill=shawl)
    for k, col in enumerate((CREAM, MARI)):
        d.ellipse(P(150 + 22 * k, 620 + 26 * k, 650 - 22 * k, 1060), outline=col, width=int(9 * u))
    d.rectangle(P(360, 500, 440, 610), fill=(214, 156, 108))
    d.ellipse(P(240, 160, 560, 480), fill=hair)
    d.ellipse(P(325, 70, 475, 220), fill=hair)
    d.ellipse(P(275, 235, 525, 545), fill=skin)
    d.pieslice(P(268, 226, 532, 430), 180, 360, fill=hair)
    for ex in (268, 532):
        d.ellipse(P(ex - 12, 425, ex + 12, 449), fill=MARI)
    d.ellipse(P(298, 455, 346, 492), fill=(240, 140, 128))
    d.ellipse(P(454, 455, 502, 492), fill=(240, 140, 128))
    gw = int(9 * u)
    d.ellipse(P(298, 362, 388, 444), outline=dk, width=gw)
    d.ellipse(P(412, 362, 502, 444), outline=dk, width=gw)
    d.line(P(388, 398, 412, 398), fill=dk, width=gw)
    for ex in (343, 457):
        d.ellipse(P(ex - 7, 396, ex + 7, 410), fill=dk)
    d.arc(P(345, 425, 455, 510), 25, 155, fill=dk, width=int(9 * u))
    m = Image.new('L', (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N - 1, N - 1), fill=255)
    lay.putalpha(m)
    return lay.resize((size, size), Image.LANCZOS)


def make_flag(bg, c_hero, c_sub, portrait_bg):
    W2, H2 = (W + 2 * PAD) * S, (H + 2 * PAD) * S
    ox = oy = PAD * S
    N = 600
    pts = [(ox + prof(i / N) * W * S, oy + (i / N) * H * S) for i in range(N + 1)]
    mask = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    fab = Image.new('RGBA', (W2, H2), bg)

    yc, L1, L2 = 0.585 * H, 565, 500
    hero = vtext(NAME, fit_font(SHRI, NAME, L1 * S), c_hero)
    sub = vtext('COMIDA CASERA', fit_font(POP_B, 'COMIDA CASERA', L2 * S), c_sub)
    gap = 34 * S
    gw = hero.width + gap + sub.width
    left = 26 * S
    right = prof((yc + L1 / 2) / H) * W * S - 22 * S
    print('group', gw / S, 'avail', (right - left) / S)
    startx = ox + left + max(0, ((right - left) - gw) / 2)
    fab.paste(hero, (int(startx), int(oy + yc * S - hero.height / 2)), hero)
    fab.paste(sub, (int(startx + hero.width + gap), int(oy + yc * S - sub.height / 2)), sub)

    pd = 210
    pg = weli_graphic(portrait_bg, PINK, pd * S)
    cx = startx + gw / 2
    fab.paste(pg, (int(cx - pd * S / 2), int(oy + 0.085 * H * S)), pg)

    layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    layer.paste(fab, (0, 0), mask)
    ImageDraw.Draw(layer).line(pts + [pts[0]], fill=DARK + (255,), width=7, joint='curve')
    return layer.resize((W2 // S, H2 // S), Image.LANCZOS)


CW, CH = 2150, 1780
canvas = Image.new('RGB', (CW, CH), (238, 236, 230))
d = ImageDraw.Draw(canvas)
d.text((100, 50), NAME, font=ImageFont.truetype(SHRI, 70), fill=DARK)
d.text((100, 140), 'Logo + flag with the Weli portrait  ·  Zapopan, Jalisco', font=ImageFont.truetype(POP_M, 30),
       fill=(95, 95, 95))

# logo card
cx0, cy0 = 100, 300
d.rounded_rectangle((cx0, cy0, cx0 + 700, cy0 + 850), radius=30, fill=GREEN, outline=(210, 205, 190), width=3)
g = weli_graphic(MARI, PINK, 440)
canvas.paste(g, (cx0 + 130, cy0 + 40), g)
f = fit_font(SHRI, NAME_MIXED, 520)
d.text((cx0 + 350, cy0 + 600), NAME_MIXED, font=f, fill=CREAM, anchor='mm')
d.text((cx0 + 350, cy0 + 705), 'COMIDA CASERA', font=ImageFont.truetype(POP_B, 34), fill=MARI, anchor='mm')
d.text((cx0 + 28, cy0 + 790), 'Logo  ·  verde', font=ImageFont.truetype(POP_B, 28), fill=CREAM)

Y0 = 300
POLE_BOTTOM = Y0 + H + 170
fL = ImageFont.truetype(POP_M, 30)
flags = [
    ('Flag  ·  Verde', GREEN, CREAM, MARI, MARI),
    ('Flag  ·  Rojo chile', RED, CREAM, MARI, MARI),
]
for i, (label, bg, hero, sub, pbg) in enumerate(flags):
    x0 = 1000 + i * 500
    d.ellipse((x0 - 115, POLE_BOTTOM - 8, x0 + 115, POLE_BOTTOM + 22), fill=(205, 203, 195))
    d.rounded_rectangle((x0 - 95, POLE_BOTTOM - 4, x0 + 95, POLE_BOTTOM + 12), radius=6, fill=(55, 55, 55))
    fl = make_flag(bg, hero, sub, pbg)
    canvas.paste(fl, (x0 - PAD, Y0 - PAD), fl)
    d.rectangle((x0 - 5, Y0 - 34, x0 + 5, POLE_BOTTOM), fill=(45, 45, 45))
    d.ellipse((x0 - 10, Y0 - 44, x0 + 10, Y0 - 24), fill=(45, 45, 45))
    tw = d.textlength(label, font=fL)
    d.text((x0 + 150 - tw / 2, POLE_BOTTOM + 50), label, font=fL, fill=DARK)

out = '/home/claude/la_weris_logo_flags.png'
canvas.save(out)
print('saved', out, canvas.size)
