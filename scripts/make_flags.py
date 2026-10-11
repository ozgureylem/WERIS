import math, os
from PIL import Image, ImageDraw, ImageFont

GF = '/usr/share/fonts/truetype/google-fonts/'


def pick(*names):
    for n in names:
        p = GF + n
        if os.path.exists(p):
            return p
    raise SystemExit('font missing')


HEAVY = pick('Poppins-Black.ttf', 'Poppins-ExtraBold.ttf', 'Poppins-Bold.ttf')
BOLD = pick('Poppins-Bold.ttf')
REG = pick('Poppins-Medium.ttf', 'Poppins-Regular.ttf', 'Poppins-Bold.ttf')

S = 2
W, H = 400, 1100
PAD = 8
DARK = (30, 30, 30)


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


def draw_pot(d, cx, ty, w, h, body, steam, bg):
    sw = max(4, int(0.05 * w))
    for k, off in enumerate((-0.22, 0.0, 0.22)):
        top = ty + (0.0 if k == 1 else 0.07 * h)
        bot = ty + 0.33 * h
        pts = []
        for i in range(41):
            u = i / 40
            y = bot - u * (bot - top)
            x = cx + off * w + 0.04 * w * math.sin(u * 2 * math.pi * 1.5 + k)
            pts.append((x, y))
        d.line(pts, fill=steam, width=sw, joint='curve')
        for (x, y) in (pts[0], pts[-1]):
            d.ellipse((x - sw / 2, y - sw / 2, x + sw / 2, y + sw / 2), fill=steam)
    # lid
    d.rounded_rectangle((cx - 0.50 * w, ty + 0.38 * h, cx + 0.50 * w, ty + 0.50 * h), radius=0.05 * h, fill=body)
    # body
    d.rounded_rectangle((cx - 0.42 * w, ty + 0.48 * h, cx + 0.42 * w, ty + h), radius=0.16 * h, fill=body,
                        corners=(False, False, True, True))
    # handles
    d.rounded_rectangle((cx - 0.54 * w, ty + 0.58 * h, cx - 0.38 * w, ty + 0.68 * h), radius=0.05 * h, fill=body)
    d.rounded_rectangle((cx + 0.38 * w, ty + 0.58 * h, cx + 0.54 * w, ty + 0.68 * h), radius=0.05 * h, fill=body)
    # stripe
    d.rectangle((cx - 0.42 * w, ty + 0.70 * h, cx + 0.42 * w, ty + 0.75 * h), fill=bg)


def make_flag(layout, bg, c_hero, c_name):
    W2, H2 = (W + 2 * PAD) * S, (H + 2 * PAD) * S
    ox = oy = PAD * S
    N = 600
    pts = [(ox + prof(i / N) * W * S, oy + (i / N) * H * S) for i in range(N + 1)]
    mask = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    fab = Image.new('RGBA', (W2, H2), bg)
    d = ImageDraw.Draw(fab)

    if layout == 'A':
        yc, L1, L2 = 0.47 * H, 690, 610
    else:
        yc, L1, L2 = 0.555 * H, 520, 450

    hero = vtext('LA WELIS', fit_font(HEAVY, 'LA WELIS', L1 * S), c_hero)
    name = vtext('COMIDA CASERA', fit_font(HEAVY, 'COMIDA CASERA', L2 * S), c_name)
    gap = 34 * S
    gw = hero.width + gap + name.width
    t_b = (yc + L1 / 2) / H
    left = 26 * S
    right = prof(t_b) * W * S - 22 * S
    avail = right - left
    print(layout, 'group width', gw / S, 'avail', avail / S)
    startx = ox + left + max(0, (avail - gw) / 2)
    fab.paste(hero, (int(startx), int(oy + yc * S - hero.height / 2)), hero)
    fab.paste(name, (int(startx + hero.width + gap), int(oy + yc * S - name.height / 2)), name)

    if layout == 'B':
        cx = startx + gw / 2
        draw_pot(d, cx, oy + 0.095 * H * S, 180 * S, 170 * S, c_hero, c_name, bg)

    layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    layer.paste(fab, (0, 0), mask)
    ImageDraw.Draw(layer).line(pts + [pts[0]], fill=DARK + (255,), width=7, joint='curve')
    return layer.resize((W2 // S, H2 // S), Image.LANCZOS)


RED = dict(bg=(214, 40, 40), hero=(255, 244, 220), name=(255, 195, 0))
YEL = dict(bg=(255, 195, 0), hero=(27, 27, 27), name=(196, 18, 31))

CW, CH = 2200, 1780
canvas = Image.new('RGB', (CW, CH), (238, 236, 230))
d = ImageDraw.Draw(canvas)

fT = ImageFont.truetype(HEAVY, 70)
fS = ImageFont.truetype(REG, 30)
fH = ImageFont.truetype(BOLD, 38)
fL = ImageFont.truetype(REG, 30)

d.text((100, 50), 'LA WELIS', font=fT, fill=DARK)
d.text((100, 140), 'Feather flag mockups v2  ·  the name is the hero, the menu changes daily', font=fS, fill=(95, 95, 95))

flags = [
    ('A', RED, '1A  ·  Red'),
    ('A', YEL, '1B  ·  Yellow'),
    ('B', RED, '2A  ·  Red + pot icon'),
    ('B', YEL, '2B  ·  Yellow + pot icon'),
]
Y0 = 340
POLE_BOTTOM = Y0 + H + 170

for i, (lay, col, label) in enumerate(flags):
    x0 = 200 + i * 500
    # base + pole
    d.ellipse((x0 - 115, POLE_BOTTOM - 8, x0 + 115, POLE_BOTTOM + 22), fill=(205, 203, 195))
    d.rounded_rectangle((x0 - 95, POLE_BOTTOM - 4, x0 + 95, POLE_BOTTOM + 12), radius=6, fill=(55, 55, 55))
    fl = make_flag(lay, col['bg'], col['hero'], col['name'])
    canvas.paste(fl, (x0 - PAD, Y0 - PAD), fl)
    d.rectangle((x0 - 5, Y0 - 34, x0 + 5, POLE_BOTTOM), fill=(45, 45, 45))
    d.ellipse((x0 - 10, Y0 - 44, x0 + 10, Y0 - 24), fill=(45, 45, 45))
    tw = d.textlength(label, font=fL)
    d.text((x0 + 150 - tw / 2, POLE_BOTTOM + 50), label, font=fL, fill=DARK)

for title, xa, xb in (('OPTION 1  ·  Wordmark only', 200, 1100), ('OPTION 2  ·  Wordmark + icon', 1200, 2100)):
    tw = d.textlength(title, font=fH)
    d.text(((xa + xb) / 2 - tw / 2, 230), title, font=fH, fill=DARK)
    d.line((xa, 290, xb, 290), fill=(170, 168, 160), width=3)

out = '/home/claude/la_welis_flag_options_v2.png'
canvas.save(out)
print('saved', out, canvas.size)
