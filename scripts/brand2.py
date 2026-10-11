import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FW = '/home/claude/fontwork/node_modules/@fontsource/'
GF = '/usr/share/fonts/truetype/google-fonts/'
OUT = '/home/claude/la_weris_brand_v2/'
UP = '/root/.claude/uploads/fa5a0220-cb5c-5ca5-a2e7-f57c063701d3/'
REF_LOGO = UP + '350dfde3-image.png'


def fp(pkg, w, style='normal'):
    return FW + pkg + '/files/' + pkg + '-latin-' + str(w) + '-' + style + '.woff'


PLAY_BI = fp('playfair-display', 900, 'italic')
PLAY_B = fp('playfair-display', 700)
PLAY_BLK = fp('playfair-display', 900)
PLAY_R = fp('playfair-display', 400)
PLAY_I = fp('playfair-display', 400, 'italic')
MONT_B = fp('montserrat', 700)
MONT_BLK = fp('montserrat', 900)
POP_M = GF + 'Poppins-Medium.ttf'
POP_R = GF + 'Poppins-Regular.ttf'

# palette: zip spec + colors sampled from the supplied mockup
GREEN = (27, 108, 68)
RED = (210, 38, 42)
MAIZ = (245, 176, 35)
CREAM = (242, 236, 223)
EARTH = (45, 45, 42)
SAGE = (94, 136, 85)       # logo card green in the mockup
CRIMSON = (181, 24, 38)    # red flag in the mockup
PAGE = (248, 242, 224)
FLAG_CREAM = (247, 238, 216)
FLAG_YELLOW = (248, 170, 36)


# ------------------------------------------------------------------ real artwork from the supplied mockup
def load_artwork():
    a = Image.open(REF_LOGO).convert('RGB')
    sa = a.width / 920.0
    card = a.crop((int(20 * sa), int(380 * sa), int(895 * sa), int(1445 * sa)))   # 1147 x 1396
    # paint out the caption "Logo - Verde Agave Art artesanal." with a clean strip of the same card
    patch = card.crop((40, 18, 850, 86))
    card.paste(patch, (40, 1290))
    # badge (circle) cut from the card
    cx, cy, r = 575, 461, 369
    badge = card.crop((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3)).convert('RGBA')
    m = Image.new('L', (badge.width * 4, badge.height * 4), 0)
    ImageDraw.Draw(m).ellipse((12, 12, badge.width * 4 - 12, badge.height * 4 - 12), fill=255)
    badge.putalpha(m.resize(badge.size, Image.LANCZOS))
    # wordmark block keyed off the green
    blk = card.crop((95, 830, 1065, 1200)).convert('RGB')
    arr = np.asarray(blk).astype(float)
    bg = np.array(SAGE, float)
    dist = np.linalg.norm(arr - bg, axis=2)
    alpha = np.clip((dist - 26) / (80 - 26), 0, 1)
    alpha[alpha < 0.10] = 0
    fg = (arr - (1 - alpha[..., None]) * bg) / np.maximum(alpha[..., None], 0.08)
    fg = np.clip(fg, 0, 255)
    out = np.dstack([fg, alpha * 255]).astype(np.uint8)
    block = Image.fromarray(out, 'RGBA')
    # card with rounded corners
    cardrgba = card.convert('RGBA')
    mk = Image.new('L', (card.width * 3, card.height * 3), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, card.width * 3 - 1, card.height * 3 - 1), radius=120, fill=255)
    cardrgba.putalpha(mk.resize(card.size, Image.LANCZOS))
    return cardrgba, badge, block


# ------------------------------------------------------------------ text helpers
def text_img(txt, fnt, fill, sp=0):
    l, t, r, b = fnt.getbbox(txt)
    if sp == 0:
        im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - l, 4 - t), txt, font=fnt, fill=fill)
        return im
    widths = [fnt.getlength(c) for c in txt]
    total = sum(widths) + sp * (len(txt) - 1)
    im = Image.new('RGBA', (int(total) + 8, b - t + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 4
    for c, w in zip(txt, widths):
        d.text((x, 4 - t), c, font=fnt, fill=fill)
        x += w + sp
    return im


def fit_img(path, txt, L, fill, sp_ratio=0.0):
    f = ImageFont.truetype(path, 200)
    base = f.getlength(txt) if sp_ratio == 0 else sum(f.getlength(c) for c in txt) + sp_ratio * 200 * (len(txt) - 1)
    size = max(8, int(200 * L / base))
    return text_img(txt, ImageFont.truetype(path, size), fill, sp_ratio * size)


# ------------------------------------------------------------------ illustration helpers (flags)
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def silhouette(W, H, n=140):
    segs = [((0, 0), (0.20 * W, 0), (0.40 * W, 0), (0.56 * W, 0)),
            ((0.56 * W, 0), (0.93 * W, 0), (W, 0.07 * H), (W, 0.215 * H)),
            ((W, 0.215 * H), (W, 0.45 * H), (0.90 * W, 0.70 * H), (0.825 * W, 0.795 * H)),
            ((0.825 * W, 0.795 * H), (0.74 * W, 0.86 * H), (0.45 * W, 0.94 * H), (0, H))]
    pts = []
    for s in segs:
        for i in range(n):
            pts.append(bez(*s, i / n))
    pts.append((0, H))
    return pts


def chile_layer(L, fill, outline, hi, stem=(86, 52, 36)):
    pad = int(L * 0.22)
    Wc, Hc = int(L * 1.2) + 2 * pad, int(L * 0.75) + 2 * pad
    lay = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    A = (pad + 0.10 * L, pad + 0.18 * L)
    B1 = (pad + 0.40 * L, pad + 0.60 * L)
    B2 = (pad + 0.75 * L, pad + 0.50 * L)
    C = (pad + 1.05 * L, pad + 0.38 * L)
    n = 90
    spine, nor = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(A, B1, B2, C, t)
        x2, y2 = bez(A, B1, B2, C, min(1, t + 0.01))
        x1, y1 = bez(A, B1, B2, C, max(0, t - 0.01))
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy) or 1
        nor.append((-dy / ln, dx / ln))
        spine.append((x, y))
    wmax = 0.125 * L

    def wprof(t):
        return wmax * (0.45 + 0.55 * math.sin(min(1, t / 0.30) * math.pi / 2)) * (1 - t ** 1.6) ** 0.75

    def poly(extra):
        l, r = [], []
        for i in range(n + 1):
            (x, y), (nx, ny) = spine[i], nor[i]
            w = wprof(i / n) + extra
            l.append((x + nx * w, y + ny * w))
            r.append((x - nx * w, y - ny * w))
        return l + r[::-1]

    d.polygon(poly(L * 0.014), fill=outline)
    d.polygon(poly(0), fill=fill)
    hl = []
    for i in range(int(n * 0.10), int(n * 0.78)):
        (x, y), (nx, ny) = spine[i], nor[i]
        w = wprof(i / n) * 0.45
        hl.append((x + nx * w, y + ny * w))
    d.line(hl, fill=hi, width=max(2, int(L * 0.02)), joint='curve')
    sx, sy = A
    stem_pts = [(sx, sy), (sx - 0.05 * L, sy - 0.06 * L), (sx - 0.04 * L, sy - 0.15 * L)]
    d.line(stem_pts, fill=outline, width=int(L * 0.08), joint='curve')
    d.line(stem_pts, fill=stem, width=int(L * 0.052), joint='curve')
    d.ellipse((sx - 0.055 * L, sy - 0.05 * L, sx + 0.055 * L, sy + 0.06 * L), fill=stem, outline=outline,
              width=max(2, int(L * 0.012)))
    return lay


def flame_layer(h, outline, outer, inner):
    w = int(h * 0.8)
    pad = int(h * 0.1)
    lay = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def tongue(cx, hh, ww, bend, col, out=None, ow=0):
        left, right = [], []
        for i in range(41):
            t = i / 40
            half = 0.5 * ww * (1 - t ** 1.25) ** 0.85 * (1 + 0.10 * math.sin(t * 10 + bend * 5))
            xs = cx + bend * ww * math.sin(t * math.pi * 0.85)
            y = pad + h - hh * t
            left.append((xs - half, y))
            right.append((xs + half, y))
        d.polygon(left + right[::-1], fill=col, outline=out, width=ow)

    ow = max(2, int(h * 0.025))
    c = pad + w / 2
    tongue(c - 0.20 * w, 0.62 * h, 0.40 * w, -0.20, outer, outline, ow)
    tongue(c + 0.20 * w, 0.72 * h, 0.42 * w, 0.22, outer, outline, ow)
    tongue(c, h * 0.98, 0.55 * w, 0.05, outer, outline, ow)
    tongue(c, h * 0.62, 0.30 * w, 0.04, inner)
    return lay


def bowl_layer(sz, body, rim, outline, steam=None, with_chile=False, fill_red=(150, 22, 34)):
    pad = int(sz * 0.1)
    N = sz + 2 * pad
    lay = Image.new('RGBA', (N, int(N * 0.95)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    P = lambda *v: tuple(pad + x * sz for x in v)
    ow = max(2, int(sz * 0.02))
    if steam:
        for k, x0 in enumerate((0.40, 0.55)):
            pts = [(pad + (x0 + 0.04 * math.sin(i / 30 * 2 * math.pi * 1.4 + k)) * sz, pad + (0.22 - 0.2 * i / 30) * sz)
                   for i in range(31)]
            d.line(pts, fill=steam, width=max(2, int(sz * 0.035)), joint='curve')
    for (x0, y0, x1, y1) in ((0.18, 0.70, 0.30, 0.92), (0.70, 0.70, 0.82, 0.92), (0.44, 0.76, 0.56, 0.95)):
        d.rounded_rectangle(P(x0, y0, x1, y1), radius=int(sz * 0.04), fill=body, outline=outline, width=ow)
    d.ellipse(P(0.04, 0.30, 0.96, 0.82), fill=body, outline=outline, width=ow)
    d.ellipse(P(0.09, 0.33, 0.91, 0.58), fill=rim, outline=outline, width=ow)
    if with_chile:
        cl = chile_layer(int(sz * 0.55), fill_red, (92, 12, 22), (205, 60, 62))
        cl = cl.rotate(35, resample=Image.BICUBIC, expand=True)
        lay.paste(cl, (int(pad + 0.28 * sz), int(pad - 0.02 * sz)), cl)
    return lay


def agave_layer(sz, fill, outline, rib):
    lay = Image.new('RGBA', (int(sz * 2.4), int(sz * 1.9)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = sz * 1.2, sz * 1.65
    ow = max(2, int(sz * 0.02))
    for deg in sorted(range(-75, 76, 15), key=lambda v: -abs(v)):
        a = math.radians(deg)
        v = (math.sin(a), -math.cos(a))
        nn = (math.cos(a), math.sin(a))
        L = sz * (1.05 - 0.15 * abs(deg) / 75)
        mid = (cx + 0.45 * L * v[0], cy + 0.45 * L * v[1])
        tip = (cx + L * v[0], cy + L * v[1])
        w = 0.15 * L
        d.polygon([(cx, cy), (mid[0] + nn[0] * w, mid[1] + nn[1] * w), tip, (mid[0] - nn[0] * w, mid[1] - nn[1] * w)],
                  fill=fill, outline=outline, width=ow)
        d.line([(cx, cy), (cx + 0.85 * L * v[0], cy + 0.85 * L * v[1])], fill=rib, width=max(2, int(sz * 0.015)))
    return lay


def stamp(fab, lay, cx, cy, angle=0):
    if angle:
        lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    fab.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


# ------------------------------------------------------------------ flags
FW_, FH_ = 1090, 3000


def flag_art(kind, badge, pattern_only=False):
    S = 2
    W2, H2 = FW_ * S, FH_ * S
    pts = silhouette(W2, H2)
    m4 = Image.new('L', (W2 * 2, H2 * 2), 0)
    ImageDraw.Draw(m4).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    mask = m4.resize((W2, H2), Image.LANCZOS)

    if kind == 'verde':
        bg, tag_txt = GREEN, 'Cocina Regional'
    else:
        bg, tag_txt = CRIMSON, 'El Sabor del Chile'
    fab = Image.new('RGBA', (W2, H2), (0, 0, 0, 0) if pattern_only else bg)

    badge_d = int(0.54 * W2)
    bcx, bcy = int(0.366 * W2), int(0.088 * H2 + badge_d / 2)
    text_rect = (0.14 * W2, 0.33 * H2, 0.80 * W2, 0.88 * H2)
    badge_rect = (bcx - badge_d / 2 - 40, bcy - badge_d / 2 - 40, bcx + badge_d / 2 + 40, bcy + badge_d / 2 + 40)

    def blocked(x, y):
        for (x0, y0, x1, y1) in (text_rect, badge_rect):
            if x0 < x < x1 and y0 < y < y1:
                return True
        return False

    if kind == 'rojo':
        fill, outl, hi = (152, 22, 34), (96, 12, 22), (208, 62, 64)
        chiles = [(.47, .075, .50, -12), (.10, .07, .36, -82), (.84, .19, .60, -120), (.045, .40, .36, -86),
                  (.07, .60, .50, -88), (.13, .87, .52, -42), (.37, .945, .32, 14), (.84, .775, .50, -96),
                  (.62, .12, .26, -70), (.05, .76, .34, -80), (.92, .97, .28, -30)]
        for fx, fy, ln, ang in chiles:
            cx, cy = fx * W2, fy * H2
            if blocked(cx, cy) and fx > 0.2:
                continue
            L = int(ln * W2)
            stamp(fab, chile_layer(L, fill, outl, hi), cx, cy, ang)
        fl = [(.73, .245, .17), (.975, .30, .10), (.89, .505, .30), (.64, .86, .25), (.02, .15, .12), (.04, .945, .20),
              (.01, .36, .13)]
        for fx, fy, hw in fl:
            stamp(fab, flame_layer(int(hw * 1.5 * W2), (150, 55, 20), (236, 122, 38), (252, 196, 72)), fx * W2, fy * H2)
        stamp(fab, bowl_layer(int(0.30 * W2), (122, 52, 52), (150, 78, 72), (74, 26, 28), steam=(236, 130, 50),
                              with_chile=True), 0.89 * W2, 0.405 * H2)
        stamp(fab, bowl_layer(int(0.34 * W2), (118, 50, 50), (92, 34, 36), (74, 26, 28)), 0.845 * W2, 0.58 * H2)
    else:
        fill, outl, rib = (40, 128, 86), (22, 88, 58), (78, 168, 120)
        spots = [(.12, .06, .40), (.62, .05, .34), (.92, .22, .34), (.05, .24, .30), (.97, .46, .30), (.05, .50, .34),
                 (.9, .66, .32), (.08, .74, .34), (.4, .93, .34), (.75, .86, .28), (.05, .95, .30), (.55, .31, .24)]
        for fx, fy, sz in spots:
            cx, cy = fx * W2, fy * H2
            if blocked(cx, cy) and fx > 0.2:
                continue
            stamp(fab, agave_layer(int(sz * W2), fill, outl, rib), cx, cy, 0)

    if pattern_only:
        return fab
    # type, reading upward like the mockup
    hero = fit_img(PLAY_BI, 'LA WERIS', int(0.50 * H2), FLAG_CREAM).rotate(90, expand=True)
    sub = fit_img(PLAY_B, 'COMIDA CASERA', int(0.41 * H2), FLAG_YELLOW).rotate(90, expand=True)
    tag = fit_img(PLAY_B, tag_txt, int(0.39 * H2), FLAG_CREAM).rotate(90, expand=True)
    yc = int(0.585 * H2)
    x = int(0.15 * W2)
    for part, gap in ((hero, 0.075), (sub, 0.055), (tag, 0)):
        fab.paste(part, (x, int(yc - part.height / 2)), part)
        x += part.width + int(gap * W2)
    print(kind, 'text right edge', round(x / W2, 3), 'of width')

    bb = badge.resize((badge_d, badge_d), Image.LANCZOS)
    fab.paste(bb, (int(bcx - badge_d / 2), int(bcy - badge_d / 2)), bb)

    layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    layer.paste(fab, (0, 0), mask)
    return layer


def flags_preview(fv, fr):
    CW, CH = 1900, 2150
    cv = Image.new('RGB', (CW, CH), (238, 236, 230))
    d = ImageDraw.Draw(cv)
    d.text((100, 60), 'LA WERIS', font=ImageFont.truetype(PLAY_BI, 72), fill=EARTH)
    d.text((100, 150), 'Banderas pluma  ·  vista previa', font=ImageFont.truetype(MONT_B, 28), fill=(95, 95, 95))
    th = 1560
    tw = int(th * FW_ / FH_)
    for i, (fl, label) in enumerate(((fv, 'Verde Agave'), (fr, 'Rojo Chile'))):
        x0 = 330 + i * 760
        y0 = 280
        pb = y0 + th + 90
        d.ellipse((x0 - 110, pb - 8, x0 + 110, pb + 20), fill=(205, 203, 195))
        d.rounded_rectangle((x0 - 90, pb - 4, x0 + 90, pb + 10), radius=6, fill=(55, 55, 55))
        s = fl.resize((tw, th), Image.LANCZOS)
        cv.paste(s, (x0, y0), s)
        d.rectangle((x0 - 5, y0 - 30, x0 + 5, pb), fill=(45, 45, 45))
        d.ellipse((x0 - 10, y0 - 40, x0 + 10, y0 - 20), fill=(45, 45, 45))
        lw = d.textlength(label, font=ImageFont.truetype(MONT_B, 30))
        d.text((x0 + tw / 2 - lw / 2, pb + 50), label, font=ImageFont.truetype(MONT_B, 30), fill=EARTH)
    return cv


# ------------------------------------------------------------------ profile picture
def profile_picture(badge, block, size=1080):
    rng = np.random.default_rng(3)
    base = np.full((size, size, 3), SAGE, float) + rng.normal(0, 3.0, (size, size, 1))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    bd = 650
    b = badge.resize((bd, bd), Image.LANCZOS)
    im.paste(b, ((size - bd) // 2, 55), b)
    bw = 570
    bl = block.resize((bw, int(block.height * bw / block.width)), Image.LANCZOS)
    im.paste(bl, ((size - bw) // 2, 770), bl)
    return im


# ------------------------------------------------------------------ business profile sheet
def wrap(d, txt, font, maxw):
    words = txt.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def business_profile(card, badge, block, pic, fv, fr):
    CW, CH = 2400, 3300
    cv = Image.new('RGB', (CW, CH), PAGE)
    d = ImageDraw.Draw(cv)
    d.rectangle((0, 0, CW, 210), fill=SAGE)
    d.text((100, 58), 'FICHA DE NEGOCIO', font=ImageFont.truetype(MONT_BLK, 70), fill=PAGE)
    d.text((100, 148), 'Perfil de marca  ·  La Weris, Comida Casera', font=ImageFont.truetype(PLAY_I, 36), fill=(255, 231, 160))
    d.rectangle((0, 210, CW, 222), fill=MAIZ)

    lg = card.resize((720, int(720 * card.height / card.width)), Image.LANCZOS)
    cv.paste(lg, (100, 290), lg)

    fl = ImageFont.truetype(MONT_BLK, 26)
    fv_ = ImageFont.truetype(PLAY_R, 44)
    x, y = 960, 300
    fields = [
        ('NOMBRE', 'La Weris'),
        ('GIRO', 'Comida casera'),
        ('LEMA', 'Tradición Zapopana • Sabor del Alma'),
        ('UBICACIÓN', 'Zapopan, Jalisco, México'),
        ('HORARIO', 'Fines de semana  (la bandera arriba = abierto)'),
        ('MENÚ', 'Cambia cada día: tacos de birria, bistec y chorizo · pellizcadas · sincronizadas · quesadillas · hamburguesas · lonches'),
    ]
    for lab, val in fields:
        d.text((x, y), lab, font=fl, fill=SAGE)
        y += 40
        for ln in wrap(d, val, fv_, 1340):
            d.text((x, y), ln, font=fv_, fill=EARTH)
            y += 58
        y += 26
    for lab in ('WHATSAPP', 'INSTAGRAM / FACEBOOK', 'GOOGLE MAPS'):
        d.text((x, y), lab, font=fl, fill=SAGE)
        y += 70
        d.line((x, y, x + 1340, y), fill=(150, 145, 130), width=3)
        y += 34
    d.text((x, y - 6), 'Completar con los datos reales antes de publicar.', font=ImageFont.truetype(PLAY_I, 30), fill=(120, 115, 105))

    y2 = 1500
    d.text((100, y2), 'APLICACIONES', font=ImageFont.truetype(MONT_BLK, 36), fill=SAGE)
    d.line((100, y2 + 60, 2300, y2 + 60), fill=(190, 182, 162), width=3)
    bs = 470
    bb = badge.resize((bs, bs), Image.LANCZOS)
    cv.paste(bb, (100, y2 + 110), bb)
    d.text((100, y2 + 110 + bs + 18), 'Retrato (sello)', font=ImageFont.truetype(MONT_B, 26), fill=EARTH)
    ps = 470
    pc = pic.convert('RGB').resize((ps, ps), Image.LANCZOS)
    m = Image.new('L', (ps * 3, ps * 3), 0)
    ImageDraw.Draw(m).ellipse((0, 0, ps * 3 - 1, ps * 3 - 1), fill=255)
    cv.paste(pc, (660, y2 + 110), m.resize((ps, ps), Image.LANCZOS))
    d.text((660, y2 + 110 + ps + 18), 'Foto de perfil (WhatsApp / Instagram)', font=ImageFont.truetype(MONT_B, 26), fill=EARTH)
    fh = 600
    fwid = int(fh * FW_ / FH_)
    for i, (f, nm) in enumerate(((fv, 'Bandera Verde Agave'), (fr, 'Bandera Rojo Chile'))):
        s = f.resize((fwid, fh), Image.LANCZOS)
        fx = 1290 + i * 480
        d.rectangle((fx - 4, y2 + 90, fx + 4, y2 + 110 + fh + 30), fill=EARTH)
        cv.paste(s, (fx, y2 + 110), s)
        d.text((fx - 6, y2 + 110 + fh + 48), nm, font=ImageFont.truetype(MONT_B, 24), fill=EARTH)

    y3 = 2340
    d.text((100, y3), 'PALETA DE COLOR', font=ImageFont.truetype(MONT_BLK, 36), fill=SAGE)
    d.line((100, y3 + 60, 2300, y3 + 60), fill=(190, 182, 162), width=3)
    pal = [
        ('Verde Agave', GREEN, '#1B6C44', 'C85 M20 Y85 K40', 'PANTONE 7731 C'),
        ('Rojo Chile', RED, '#D2262A', 'C10 M98 Y95 K2', 'PANTONE 1795 C'),
        ('Amarillo Maíz', MAIZ, '#F5B023', 'C0 M32 Y95 K0', 'PANTONE 1235 C'),
        ('Crema Artesanal', CREAM, '#F2ECDF', 'C5 M7 Y13 K0', 'PANTONE 7527 C'),
        ('Tierra Molcajete', EARTH, '#2D2D2A', 'C50 M40 Y50 K80', 'PANTONE 447 C'),
        ('Verde del logo', SAGE, '#5E8855', 'tomado del arte', 'logo / tarjeta'),
        ('Rojo de bandera', CRIMSON, '#B51826', 'tomado del arte', 'bandera roja'),
    ]
    sw = 280
    for i, (nm, col, hx, cm, pt) in enumerate(pal):
        sx = 100 + i * 315
        d.rounded_rectangle((sx, y3 + 100, sx + sw, y3 + 300), radius=24, fill=col, outline=(150, 145, 130), width=3)
        d.text((sx, y3 + 318), nm, font=ImageFont.truetype(MONT_BLK, 25), fill=EARTH)
        d.text((sx, y3 + 355), hx, font=ImageFont.truetype(MONT_B, 22), fill=(90, 88, 80))
        d.text((sx, y3 + 385), cm, font=ImageFont.truetype(MONT_B, 20), fill=(90, 88, 80))
        d.text((sx, y3 + 412), pt, font=ImageFont.truetype(MONT_B, 20), fill=(90, 88, 80))

    y4 = 2870
    d.text((100, y4), 'TIPOGRAFÍA', font=ImageFont.truetype(MONT_BLK, 36), fill=SAGE)
    d.line((100, y4 + 60, 2300, y4 + 60), fill=(190, 182, 162), width=3)
    chip = Image.new('RGBA', (640, 230), SAGE)
    wm = block.crop((0, 40, 780, 300))
    wm = wm.resize((int(wm.width * 0.62), int(wm.height * 0.62)), Image.LANCZOS)
    chip.paste(wm, (60, 10), wm)
    cv.paste(chip.convert('RGB'), (100, y4 + 90))
    d.text((100, y4 + 335), 'Logotipo script  ·  arte original', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))
    d.text((860, y4 + 130), 'COMIDA CASERA', font=ImageFont.truetype(POP_M, 58), fill=EARTH)
    d.text((860, y4 + 335), 'Poppins Medium  ·  giro y textos cortos', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))
    d.text((1640, y4 + 120), 'LA WERIS', font=ImageFont.truetype(PLAY_BI, 70), fill=EARTH)
    d.text((1640, y4 + 335), 'Playfair Display  ·  banderas', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))
    d.text((100, CH - 62), 'CMYK y Pantone: referencia del paquete original; validar con prueba de impresión. Colores "del arte" medidos en el mockup.',
           font=ImageFont.truetype(PLAY_I, 28), fill=(120, 115, 105))
    return cv


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    card, badge, block = load_artwork()
    card.save(OUT + 'La_Weris_Logo_Master.png')
    badge.save(OUT + 'La_Weris_Retrato_Sello.png')
    block.save(OUT + 'debug_block.png')
    print('logo ok', card.size, badge.size, block.size)
    pic = profile_picture(badge, block)
    pic.convert('RGB').save(OUT + 'La_Weris_Foto_Perfil.png')
    fv = flag_art('verde', badge)
    fv.save(OUT + 'La_Weris_Bandera_Verde_Agave.png')
    fr = flag_art('rojo', badge)
    fr.save(OUT + 'La_Weris_Bandera_Rojo_Chile.png')
    flags_preview(fv, fr).save(OUT + 'La_Weris_Banderas_Vista_Previa.png')
    business_profile(card, badge, block, pic, fv, fr).save(OUT + 'La_Weris_Ficha_de_Negocio.png')
    print('done')
