import math, random, os
from PIL import Image, ImageDraw, ImageFont

FW = '/home/claude/fontwork/node_modules/@fontsource/'
OUT = '/home/claude/la_weris_brand/'


def fp(pkg, w, style='normal'):
    return FW + pkg + '/files/' + pkg + '-latin-' + str(w) + '-' + style + '.woff'


LOBSTER = fp('lobster', 400)
MONT_B = fp('montserrat', 700)
MONT_BLK = fp('montserrat', 900)
PLAY_BI = fp('playfair-display', 900, 'italic')
PLAY_I = fp('playfair-display', 400, 'italic')
PLAY_R = fp('playfair-display', 400)

# palette from the supplied Color_Palette_Spec.json
GREEN = (27, 108, 68)      # Verde Agave   #1B6C44
RED = (210, 38, 42)        # Rojo Chile    #D2262A
MAIZ = (245, 176, 35)      # Amarillo Maiz #F5B023
CREAM = (242, 236, 223)    # Crema         #F2ECDF
EARTH = (45, 45, 42)       # Tierra Molcajete #2D2D2A
TERRA = (214, 104, 56)     # accent used on the portrait top (from the mockup)
TILE_BLUE = (47, 93, 168)  # talavera tile accent (from the mockup)


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
    if sp_ratio == 0:
        base = f.getlength(txt)
    else:
        base = sum(f.getlength(c) for c in txt) + sp_ratio * 200 * (len(txt) - 1)
    size = max(8, int(200 * L / base))
    f2 = ImageFont.truetype(path, size)
    return text_img(txt, f2, fill, sp_ratio * size)


# ------------------------------------------------------------------ illustration pieces
def draw_weli(d, u):
    """Weli portrait on an 800-unit grid (scaled by u). Background is drawn by the caller."""
    P = lambda *v: tuple(x * u for x in v)
    hair = (242, 240, 235)
    skin = (236, 184, 138)
    skin_d = (214, 156, 108)
    brown = (110, 66, 42)
    # top / shoulders
    d.ellipse(P(80, 565, 720, 1075), fill=TERRA)
    d.polygon(P(335, 560, 465, 560, 400, 660), fill=skin_d)
    # pearls
    for k in range(11):
        a = math.radians(25 + k * 13)
        x, y = 400 + 100 * math.cos(a), 575 + 62 * math.sin(a)
        d.ellipse(P(x - 11, y - 11, x + 11, y + 11), fill=(250, 246, 238), outline=(214, 206, 192), width=int(2 * u))
    # neck
    d.rectangle(P(362, 500, 438, 580), fill=skin_d)
    # hair back + bun
    d.ellipse(P(232, 150, 568, 495), fill=hair)
    d.ellipse(P(318, 58, 482, 220), fill=hair)
    # ears + earrings
    for ex in (262, 538):
        d.ellipse(P(ex - 20, 392, ex + 20, 456), fill=skin)
        d.ellipse(P(ex - 11, 452, ex + 11, 478), fill=MAIZ)
    # face
    d.ellipse(P(272, 235, 528, 552), fill=skin)
    d.pieslice(P(262, 222, 538, 432), 180, 360, fill=hair)
    # brows
    for bx in (298, 412):
        d.arc(P(bx, 336, bx + 90, 378), 205, 335, fill=(176, 170, 162), width=int(7 * u))
    # glasses
    gw = int(9 * u)
    d.ellipse(P(296, 366, 390, 450), outline=brown, width=gw)
    d.ellipse(P(410, 366, 504, 450), outline=brown, width=gw)
    d.line(P(390, 402, 410, 402), fill=brown, width=gw)
    for ex in (343, 457):
        d.ellipse(P(ex - 7, 400, ex + 7, 414), fill=(60, 40, 35))
    # nose, cheeks, smile, small laugh lines
    d.arc(P(384, 436, 416, 478), 15, 165, fill=(196, 138, 106), width=int(5 * u))
    d.ellipse(P(296, 462, 346, 500), fill=(240, 150, 135))
    d.ellipse(P(454, 462, 504, 500), fill=(240, 150, 135))
    d.arc(P(342, 430, 458, 520), 25, 155, fill=(70, 40, 35), width=int(9 * u))
    d.arc(P(286, 396, 312, 440), 100, 260, fill=(200, 142, 108), width=int(4 * u))
    d.arc(P(488, 396, 514, 440), 280, 80, fill=(200, 142, 108), width=int(4 * u))


def weli_portrait(size):
    SS = 3
    N = size * SS
    u = N / 800.0
    lay = Image.new('RGBA', (N, N), MAIZ)
    d = ImageDraw.Draw(lay)
    # soft sunburst behind her
    for k in range(18):
        a0 = k * 20
        d.pieslice((-N * 0.2, -N * 0.2, N * 1.2, N * 1.2), a0, a0 + 10, fill=(247, 188, 52))
    draw_weli(d, u)
    m = Image.new('L', (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N - 1, N - 1), fill=255)
    lay.putalpha(m)
    return lay.resize((size, size), Image.LANCZOS)


def heart(d, cx, cy, s, fill):
    d.ellipse((cx - s, cy - s * 0.9, cx, cy + s * 0.1), fill=fill)
    d.ellipse((cx, cy - s * 0.9, cx + s, cy + s * 0.1), fill=fill)
    d.polygon([(cx - s * 0.98, cy - s * 0.25), (cx + s * 0.98, cy - s * 0.25), (cx, cy + s * 1.05)], fill=fill)


def badge(size):
    """Round talavera-style frame + Weli portrait."""
    R = 1800
    u = R / 1000.0
    im = Image.new('RGBA', (R, R), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda *v: tuple(x * u for x in v)
    d.ellipse(P(0, 0, 1000, 1000), fill=CREAM, outline=EARTH, width=int(5 * u))
    d.ellipse(P(24, 24, 976, 976), fill=GREEN)
    cols = [MAIZ, RED, TILE_BLUE, CREAM]
    n = 30
    rc = 410
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        x, y = 500 + rc * math.sin(a), 500 - rc * math.cos(a)
        if abs(math.degrees(a) - 180) < 8:
            continue
        # diamond tile (rotated square)
        s = 34
        pts = []
        for da in (0, 90, 180, 270):
            ang = a + math.radians(da)
            pts.append((x + s * math.sin(ang), y - s * math.cos(ang)))
        d.polygon([(px * u, py * u) for px, py in pts], fill=cols[k % 4])
        d.ellipse(P(x - 8, y - 8, x + 8, y + 8), fill=GREEN if cols[k % 4] != GREEN else CREAM)
        # leaf between tiles
        a2 = a + math.pi / n
        lx, ly = 500 + rc * math.sin(a2), 500 - rc * math.cos(a2)
        d.ellipse(P(lx - 9, ly - 9, lx + 9, ly + 9), fill=CREAM)
    heart(d, 500 * u, (500 + rc + 10) * u, 30 * u, RED)
    d.ellipse(P(500 - 346, 500 - 346, 500 + 346, 500 + 346), outline=CREAM, width=int(9 * u))
    d.ellipse(P(500 - 472, 500 - 472, 500 + 472, 500 + 472), outline=CREAM, width=int(6 * u))
    inner = 330
    pg = weli_portrait(int(2 * inner * u))
    im.paste(pg, (int((500 - inner) * u), int((500 - inner) * u)), pg)
    return im.resize((size, size), Image.LANCZOS)


def chile(d, cx, cy, scale, body, stem):
    A = (cx - 80 * scale, cy - 105 * scale)
    B = (cx - 120 * scale, cy + 70 * scale)
    C = (cx + 110 * scale, cy + 115 * scale)
    pl, pr = [], []
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
        pl.append((x + nx * w, y + ny * w))
        pr.append((x - nx * w, y - ny * w))
    d.polygon(pl + pr[::-1], fill=body)
    d.ellipse((A[0] - 38 * scale, A[1] - 22 * scale, A[0] + 38 * scale, A[1] + 26 * scale), fill=stem)
    d.line((A[0], A[1] - 10 * scale, A[0] - 14 * scale, A[1] - 62 * scale), fill=stem, width=max(2, int(20 * scale)))


def molcajete(size, steam=(235, 230, 220)):
    SS = 3
    N = size * SS
    u = N / 1000.0
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda *v: tuple(x * u for x in v)
    for k, x0 in enumerate((420, 580)):
        pts = []
        for i in range(31):
            t = i / 30
            y = 300 - t * 230
            x = x0 + 24 * math.sin(t * 2 * math.pi * 1.4 + k * 1.5)
            pts.append((x * u, y * u))
        d.line(pts, fill=steam, width=int(22 * u), joint='curve')
    for (lx0, ly0, lx1, ly1) in ((240, 780, 340, 930), (660, 780, 760, 930), (450, 820, 550, 950)):
        d.rounded_rectangle(P(lx0, ly0, lx1, ly1), radius=int(30 * u), fill=EARTH)
    d.ellipse(P(100, 340, 900, 880), fill=EARTH)
    d.ellipse(P(140, 356, 860, 580), fill=(78, 78, 72))
    chile(d, 400 * u, 395 * u, 1.15 * u, RED, (40, 120, 70))
    chile(d, 600 * u, 385 * u, 1.15 * u, (190, 30, 34), (40, 120, 70))
    return im.resize((size, size), Image.LANCZOS)


def agave_shape(d, cx, cy, L, color):
    for deg in range(-72, 73, 12):
        a = math.radians(deg)
        v = (math.sin(a), -math.cos(a))
        n = (math.cos(a), math.sin(a))
        mid = (cx + 0.45 * L * v[0], cy + 0.45 * L * v[1])
        tip = (cx + L * v[0], cy + L * v[1])
        w = 0.13 * L
        d.polygon([(cx, cy), (mid[0] + n[0] * w, mid[1] + n[1] * w), tip, (mid[0] - n[0] * w, mid[1] - n[1] * w)], fill=color)


def stamp(fab, kind, cx, cy, size, angle, color):
    lay = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if kind == 'agave':
        agave_shape(d, size, size * 1.35, size * 1.1, color)
    else:
        chile(d, size, size, size / 115.0, color, color)
    lay = lay.rotate(angle, resample=Image.BICUBIC)
    fab.paste(lay, (int(cx - size), int(cy - size)), lay)


# ------------------------------------------------------------------ logo + profile pic
def logo_card(w=1600, h=1900, bg=GREEN, word=CREAM, sub=CREAM, tag=MAIZ, border=MAIZ, steam=(235, 230, 220)):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(w * 0.04), fill=bg)
    m = int(w * 0.025)
    d.rounded_rectangle((m, m, w - 1 - m, h - 1 - m), radius=int(w * 0.03), outline=border, width=max(3, int(w * 0.004)))
    bd = int(w * 0.58)
    b = badge(bd)
    im.paste(b, ((w - bd) // 2, int(h * 0.07)), b)
    wm = fit_img(LOBSTER, 'La Weris', int(w * 0.56), word)
    mol = molcajete(int(w * 0.17), steam)
    gap = int(w * 0.03)
    gw = wm.width + gap + mol.width
    x0 = (w - gw) // 2
    cy = int(h * 0.675)
    im.paste(wm, (x0, cy - wm.height // 2), wm)
    im.paste(mol, (x0 + wm.width + gap, cy - mol.height // 2 + int(h * 0.012)), mol)
    s = fit_img(MONT_BLK, 'COMIDA CASERA', int(w * 0.50), sub, sp_ratio=0.12)
    im.paste(s, ((w - s.width) // 2, int(h * 0.80) - s.height // 2), s)
    t = fit_img(PLAY_I, 'Tradición Zapopana • Sabor del Alma', int(w * 0.60), tag)
    im.paste(t, ((w - t.width) // 2, int(h * 0.87) - t.height // 2), t)
    return im


def profile_picture(size=1080):
    im = Image.new('RGBA', (size, size), GREEN)
    d = ImageDraw.Draw(im)
    bd = int(size * 0.68)
    b = badge(bd)
    im.paste(b, ((size - bd) // 2, int(size * 0.07)), b)
    wm = fit_img(LOBSTER, 'La Weris', int(size * 0.52), CREAM)
    im.paste(wm, ((size - wm.width) // 2, int(size * 0.815) - wm.height // 2), wm)
    s = fit_img(MONT_BLK, 'COMIDA CASERA', int(size * 0.36), MAIZ, sp_ratio=0.12)
    im.paste(s, ((size - s.width) // 2, int(size * 0.915) - s.height // 2), s)
    return im


# ------------------------------------------------------------------ flags
FW_, FH_ = 750, 3000


def prof(t):
    base = lambda x: 1 - 0.25 * (((x - 0.2) / 0.7) ** 1.8)
    if t < 0.2:
        u = (0.2 - t) / 0.2
        return math.sqrt(max(0.0, 1 - u * u))
    if t <= 0.78:
        return base(t)
    v = (t - 0.78) / 0.22
    return base(0.78) * max(0.0, 1 - v ** 1.8) ** 1.2


def vrot(img):
    return img.rotate(-90, expand=True)


def flag_art(kind):
    S = 3
    W2, H2 = FW_ * S, FH_ * S
    N = 900
    pts = [(prof(i / N) * W2, (i / N) * H2) for i in range(N + 1)]
    mask = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    if kind == 'verde':
        bg, tone, tag_txt = GREEN, (36, 124, 80), 'Cocina Regional'
        pat = 'agave'
    else:
        bg, tone, tag_txt = RED, (190, 30, 36), 'El Sabor del Chile'
        pat = 'chile'
    fab = Image.new('RGBA', (W2, H2), bg)
    rnd = random.Random(11)
    if pat == 'chile':
        step_y, step_x, ssz = 210, 190, 52
    else:
        step_y, step_x, ssz = 330, 300, 150
    for gy in range(-100, FH_ + 200, step_y):
        row = (gy // step_y) % 2
        for gx in range(-60, FW_ + 200, step_x):
            cx = (gx + (step_x // 2 if row else 0) + rnd.randint(-25, 25)) * S
            cy = (gy + rnd.randint(-25, 25)) * S
            ang = rnd.randint(-60, 60) if pat == 'chile' else rnd.randint(-12, 12)
            stamp(fab, pat, cx, cy, int(ssz * S), ang, tone)

    # text block, vertical, reading top to bottom
    yc = 1730 * S
    hero = vrot(fit_img(PLAY_BI, 'LA WERIS', 1480 * S, CREAM))
    sub = vrot(fit_img(MONT_BLK, 'COMIDA CASERA', 1340 * S, MAIZ, sp_ratio=0.08))
    tag = vrot(fit_img(PLAY_I, tag_txt, 800 * S, CREAM))
    gap = 28 * S
    gw = hero.width + gap + sub.width + gap + tag.width
    left = 44 * S
    t_b = (yc + 750 * S) / H2
    right = prof(t_b) * W2 - 30 * S
    avail = right - left
    print(kind, 'text group', round(gw / S), 'avail', round(avail / S))
    sx = left + max(0, (avail - gw) / 2)
    x = sx
    for part in (hero, sub, tag):
        fab.paste(part, (int(x), int(yc - part.height / 2)), part)
        x += part.width + gap
    cxg = sx + gw / 2

    bd = 540 * S
    b = badge(bd)
    fab.paste(b, (int(cxg - bd / 2), 300 * S), b)
    mol = molcajete(190 * S)
    fab.paste(mol, (int(cxg - mol.width / 2 - 20 * S), 2520 * S), mol)

    layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    layer.paste(fab, (0, 0), mask)
    return layer.resize((FW_ * 2, FH_ * 2), Image.LANCZOS)


def flags_preview(fv, fr):
    CW, CH = 1700, 2150
    cv = Image.new('RGB', (CW, CH), (238, 236, 230))
    d = ImageDraw.Draw(cv)
    d.text((100, 60), 'LA WERIS', font=ImageFont.truetype(PLAY_BI, 72), fill=EARTH)
    d.text((100, 150), 'Banderas pluma  ·  75 x 300 cm  ·  vista previa', font=ImageFont.truetype(MONT_B, 28), fill=(95, 95, 95))
    th = 1560
    tw = int(th * FW_ / FH_)
    for i, (fl, label) in enumerate(((fv, 'Verde Agave'), (fr, 'Rojo Chile'))):
        x0 = 330 + i * 650
        y0 = 280
        pb = y0 + th + 90
        d.ellipse((x0 - 110, pb - 8, x0 + 110, pb + 20), fill=(205, 203, 195))
        d.rounded_rectangle((x0 - 90, pb - 4, x0 + 90, pb + 10), radius=6, fill=(55, 55, 55))
        s = fl.resize((tw, th), Image.LANCZOS)
        cv.paste(s, (x0, y0), s)
        ol = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        d.rectangle((x0 - 5, y0 - 30, x0 + 5, pb), fill=(45, 45, 45))
        d.ellipse((x0 - 10, y0 - 40, x0 + 10, y0 - 20), fill=(45, 45, 45))
        lw = d.textlength(label, font=ImageFont.truetype(MONT_B, 30))
        d.text((x0 + tw / 2 - lw / 2, pb + 50), label, font=ImageFont.truetype(MONT_B, 30), fill=EARTH)
    return cv


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


def business_profile(fv, fr, logo_g, logo_c, pic):
    CW, CH = 2400, 3300
    cv = Image.new('RGB', (CW, CH), CREAM)
    d = ImageDraw.Draw(cv)
    d.rectangle((0, 0, CW, 210), fill=GREEN)
    d.text((100, 60), 'FICHA DE NEGOCIO', font=ImageFont.truetype(MONT_BLK, 70), fill=CREAM)
    d.text((100, 148), 'Perfil de marca  ·  La Weris, Comida Casera', font=ImageFont.truetype(PLAY_I, 36), fill=MAIZ)
    d.rectangle((0, 210, CW, 222), fill=MAIZ)

    lg = logo_g.resize((720, int(720 * logo_g.height / logo_g.width)), Image.LANCZOS)
    cv.paste(lg, (100, 300), lg)

    fl = ImageFont.truetype(MONT_BLK, 26)
    fv_ = ImageFont.truetype(PLAY_R, 44)
    x = 960
    y = 300
    fields = [
        ('NOMBRE', 'La Weris'),
        ('GIRO', 'Comida casera'),
        ('LEMA', 'Tradición Zapopana • Sabor del Alma'),
        ('UBICACIÓN', 'Zapopan, Jalisco, México'),
        ('HORARIO', 'Fines de semana  (la bandera arriba = abierto)'),
        ('MENÚ', 'Cambia cada día: tacos de birria, bistec y chorizo · pellizcadas · sincronizadas · quesadillas · hamburguesas · lonches'),
    ]
    for lab, val in fields:
        d.text((x, y), lab, font=fl, fill=GREEN)
        y += 40
        lines = wrap(d, val, fv_, 1340)
        for ln in lines:
            d.text((x, y), ln, font=fv_, fill=EARTH)
            y += 58
        y += 26
    for lab in ('WHATSAPP', 'INSTAGRAM / FACEBOOK', 'GOOGLE MAPS'):
        d.text((x, y), lab, font=fl, fill=GREEN)
        y += 70
        d.line((x, y, x + 1340, y), fill=(150, 145, 130), width=3)
        y += 34
    d.text((x, y - 6), 'Completar con los datos reales antes de publicar.', font=ImageFont.truetype(PLAY_I, 30), fill=(120, 115, 105))

    # row 2: variants, profile picture, flags
    y2 = 1500
    d.text((100, y2), 'VARIANTES Y APLICACIONES', font=ImageFont.truetype(MONT_BLK, 36), fill=GREEN)
    d.line((100, y2 + 60, 2300, y2 + 60), fill=(190, 182, 162), width=3)
    lc = logo_c.resize((470, int(470 * logo_c.height / logo_c.width)), Image.LANCZOS)
    cv.paste(lc, (100, y2 + 110), lc)
    d.text((100, y2 + 110 + lc.height + 18), 'Logo sobre crema', font=ImageFont.truetype(MONT_B, 26), fill=EARTH)
    ps = 470
    pcirc = pic.resize((ps, ps), Image.LANCZOS)
    m = Image.new('L', (ps, ps), 0)
    ImageDraw.Draw(m).ellipse((0, 0, ps - 1, ps - 1), fill=255)
    cv.paste(pcirc, (660, y2 + 110), m)
    d.text((660, y2 + 110 + ps + 18), 'Foto de perfil (WhatsApp / Instagram)', font=ImageFont.truetype(MONT_B, 26), fill=EARTH)
    fh = 560
    fwid = int(fh * FW_ / FH_)
    for i, (f, nm) in enumerate(((fv, 'Bandera Verde Agave'), (fr, 'Bandera Rojo Chile'))):
        s = f.resize((fwid, fh), Image.LANCZOS)
        fx = 1300 + i * 330
        d.rectangle((fx - 4, y2 + 90, fx + 4, y2 + 110 + fh + 30), fill=EARTH)
        cv.paste(s, (fx, y2 + 110), s)
        d.text((fx - 20, y2 + 110 + fh + 48), nm, font=ImageFont.truetype(MONT_B, 24), fill=EARTH)

    # palette
    y3 = 2340
    d.text((100, y3), 'PALETA DE COLOR', font=ImageFont.truetype(MONT_BLK, 36), fill=GREEN)
    d.line((100, y3 + 60, 2300, y3 + 60), fill=(190, 182, 162), width=3)
    pal = [
        ('Verde Agave', GREEN, '#1B6C44', 'C85 M20 Y85 K40', 'PANTONE 7731 C'),
        ('Rojo Chile', RED, '#D2262A', 'C10 M98 Y95 K2', 'PANTONE 1795 C'),
        ('Amarillo Maíz', MAIZ, '#F5B023', 'C0 M32 Y95 K0', 'PANTONE 1235 C'),
        ('Crema Artesanal', CREAM, '#F2ECDF', 'C5 M7 Y13 K0', 'PANTONE 7527 C'),
        ('Tierra Molcajete', EARTH, '#2D2D2A', 'C50 M40 Y50 K80', 'PANTONE 447 C'),
    ]
    sw = 400
    for i, (nm, col, hx, cm, pt) in enumerate(pal):
        sx = 100 + i * 440
        d.rounded_rectangle((sx, y3 + 100, sx + sw, y3 + 300), radius=24, fill=col, outline=(150, 145, 130), width=3)
        d.text((sx, y3 + 318), nm, font=ImageFont.truetype(MONT_BLK, 28), fill=EARTH)
        d.text((sx, y3 + 358), hx + '   ' + cm, font=ImageFont.truetype(MONT_B, 22), fill=(90, 88, 80))
        d.text((sx, y3 + 390), pt, font=ImageFont.truetype(MONT_B, 22), fill=(90, 88, 80))

    # typography
    y4 = 2870
    d.text((100, y4), 'TIPOGRAFÍA', font=ImageFont.truetype(MONT_BLK, 36), fill=GREEN)
    d.line((100, y4 + 60, 2300, y4 + 60), fill=(190, 182, 162), width=3)
    d.text((100, y4 + 90), 'La Weris', font=ImageFont.truetype(LOBSTER, 100), fill=EARTH)
    d.text((100, y4 + 215), 'Lobster  ·  nombre', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))
    d.text((820, y4 + 108), 'COMIDA CASERA', font=ImageFont.truetype(MONT_BLK, 56), fill=EARTH)
    d.text((820, y4 + 215), 'Montserrat Black  ·  giro y textos cortos', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))
    d.text((1600, y4 + 100), 'LA WERIS', font=ImageFont.truetype(PLAY_BI, 70), fill=EARTH)
    d.text((1600, y4 + 215), 'Playfair Display  ·  banderas y lema', font=ImageFont.truetype(MONT_B, 24), fill=(90, 88, 80))

    d.text((100, CH - 62), 'Valores CMYK y Pantone: referencia del paquete original; validar con una prueba de impresión.',
           font=ImageFont.truetype(PLAY_I, 28), fill=(120, 115, 105))
    return cv


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print('logo...')
    logo_g = logo_card()
    logo_g.save(OUT + 'La_Weris_Logo_Master_Verde.png')
    logo_c = logo_card(bg=CREAM, word=GREEN, sub=EARTH, tag=RED, border=GREEN, steam=(140, 135, 125))
    logo_c.save(OUT + 'La_Weris_Logo_Crema.png')
    print('profile pic...')
    pic = profile_picture()
    pic.convert('RGB').save(OUT + 'La_Weris_Foto_Perfil.png')
    print('flags...')
    fv = flag_art('verde')
    fv.save(OUT + 'La_Weris_Bandera_Verde_Agave.png')
    fr = flag_art('rojo')
    fr.save(OUT + 'La_Weris_Bandera_Rojo_Chile.png')
    flags_preview(fv, fr).save(OUT + 'La_Weris_Banderas_Vista_Previa.png')
    print('sheet...')
    business_profile(fv, fr, logo_g, logo_c, pic).save(OUT + 'La_Weris_Ficha_de_Negocio.png')
    print('done')
