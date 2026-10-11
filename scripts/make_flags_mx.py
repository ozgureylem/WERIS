import math
from PIL import Image, ImageDraw, ImageFont

FW = '/home/claude/fontwork/node_modules/@fontsource/'
GF = '/usr/share/fonts/truetype/google-fonts/'
SLAB = FW + 'alfa-slab-one/files/alfa-slab-one-latin-400-normal.woff'
POP_B = GF + 'Poppins-Bold.ttf'
POP_M = GF + 'Poppins-Medium.ttf'

S = 2
W, H = 400, 1100
PAD = 8
DARK = (30, 30, 30)
CREAM = (255, 244, 220)


def prof(t):
    base = lambda x: 1 - 0.25 * (((x - 0.2) / 0.7) ** 1.8)
    if t < 0.2:
        u = (0.2 - t) / 0.2
        return math.sqrt(max(0.0, 1 - u * u))
    if t <= 0.78:
        return base(t)
    v = (t - 0.78) / 0.22
    return base(0.78) * max(0.0, 1 - v ** 1.8) ** 1.2


def fit_font(path, txt, target_len):
    f = ImageFont.truetype(path, 200)
    l, t, r, b = f.getbbox(txt)
    return ImageFont.truetype(path, max(10, int(200 * target_len / (r - l))))


def vtext(txt, font, color):
    l, t, r, b = font.getbbox(txt)
    im = Image.new('RGBA', (r - l + 6, b - t + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - l, 3 - t), txt, font=font, fill=color)
    return im.rotate(-90, expand=True)


def make_flag(bg, c_hero, c_sub):
    W2, H2 = (W + 2 * PAD) * S, (H + 2 * PAD) * S
    ox = oy = PAD * S
    N = 600
    pts = [(ox + prof(i / N) * W * S, oy + (i / N) * H * S) for i in range(N + 1)]
    mask = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    fab = Image.new('RGBA', (W2, H2), bg)
    yc, L1, L2 = 0.47 * H, 690, 610
    hero = vtext('LA WELIS', fit_font(SLAB, 'LA WELIS', L1 * S), c_hero)
    sub = vtext('COMIDA CASERA', fit_font(POP_B, 'COMIDA CASERA', L2 * S), c_sub)
    gap = 36 * S
    gw = hero.width + gap + sub.width
    left = 26 * S
    right = prof((yc + L1 / 2) / H) * W * S - 22 * S
    startx = ox + left + max(0, ((right - left) - gw) / 2)
    fab.paste(hero, (int(startx), int(oy + yc * S - hero.height / 2)), hero)
    fab.paste(sub, (int(startx + hero.width + gap), int(oy + yc * S - sub.height / 2)), sub)
    layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    layer.paste(fab, (0, 0), mask)
    ImageDraw.Draw(layer).line(pts + [pts[0]], fill=DARK + (255,), width=7, joint='curve')
    return layer.resize((W2 // S, H2 // S), Image.LANCZOS)


PALS = [
    ('1  ·  Verde', (0, 104, 71), CREAM, (255, 183, 3)),
    ('2  ·  Rojo chile', (200, 16, 46), CREAM, (255, 183, 3)),
    ('3  ·  Rosa mexicano', (228, 0, 124), CREAM, (255, 214, 10)),
    ('4  ·  Cempasúchil', (255, 159, 28), (0, 77, 64), (122, 0, 25)),
]

CW, CH = 2200, 1780
canvas = Image.new('RGB', (CW, CH), (238, 236, 230))
d = ImageDraw.Draw(canvas)
d.text((100, 50), 'LA WELIS', font=ImageFont.truetype(SLAB, 70), fill=DARK)
d.text((100, 140), 'Flag colorways  ·  Mexican palettes  ·  lettering shown: Alfa Slab One (still open)',
       font=ImageFont.truetype(POP_M, 30), fill=(95, 95, 95))

Y0 = 300
POLE_BOTTOM = Y0 + H + 170
fL = ImageFont.truetype(POP_M, 30)
for i, (label, bg, hero, sub) in enumerate(PALS):
    x0 = 200 + i * 500
    d.ellipse((x0 - 115, POLE_BOTTOM - 8, x0 + 115, POLE_BOTTOM + 22), fill=(205, 203, 195))
    d.rounded_rectangle((x0 - 95, POLE_BOTTOM - 4, x0 + 95, POLE_BOTTOM + 12), radius=6, fill=(55, 55, 55))
    fl = make_flag(bg, hero, sub)
    canvas.paste(fl, (x0 - PAD, Y0 - PAD), fl)
    d.rectangle((x0 - 5, Y0 - 34, x0 + 5, POLE_BOTTOM), fill=(45, 45, 45))
    d.ellipse((x0 - 10, Y0 - 44, x0 + 10, Y0 - 24), fill=(45, 45, 45))
    tw = d.textlength(label, font=fL)
    d.text((x0 + 150 - tw / 2, POLE_BOTTOM + 50), label, font=fL, fill=DARK)

out = '/home/claude/la_welis_flag_colors_mx.png'
canvas.save(out)
print('saved', out, canvas.size)
