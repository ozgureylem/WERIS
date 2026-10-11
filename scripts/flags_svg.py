"""SVG port of the flag illustrations (chiles, flames, molcajete bowls, agave) - native vector shapes."""
import math
from vlib import P, bez, n2, rot


def _g(inner, cx, cy, ang, ox, oy):
    # layer-center (ox,oy) -> placed at (cx,cy), PIL ccw rotation -> svg negative
    return '<g transform="translate(%s %s) rotate(%s) translate(%s %s)">%s</g>' % (n2(cx), n2(cy), n2(-ang), n2(-ox), n2(-oy), inner)


def chile_inner(L, fill, outline, hi, stem=(86, 52, 36)):
    pad = .22 * L
    A = (pad + .10 * L, pad + .18 * L); B1 = (pad + .40 * L, pad + .60 * L)
    B2 = (pad + .75 * L, pad + .50 * L); C = (pad + 1.05 * L, pad + .38 * L)
    n = 40
    spine, nor = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(A, B1, B2, C, t)
        x2, y2 = bez(A, B1, B2, C, min(1, t + .01)); x1, y1 = bez(A, B1, B2, C, max(0, t - .01))
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy) or 1
        nor.append((-dy / ln, dx / ln)); spine.append((x, y))
    wmax = .125 * L
    wprof = lambda t: wmax * (.45 + .55 * math.sin(min(1, t / .30) * math.pi / 2)) * (1 - t ** 1.6) ** .75
    l, r = [], []
    for i in range(n + 1):
        (x, y), (nx, ny) = spine[i], nor[i]
        w = wprof(i / n)
        l.append((x + nx * w, y + ny * w)); r.append((x - nx * w, y - ny * w))
    body = P(l + r[::-1])
    hl = []
    for i in range(int(n * .10), int(n * .78)):
        (x, y), (nx, ny) = spine[i], nor[i]
        w = wprof(i / n) * .45
        hl.append((x + nx * w, y + ny * w))
    sx, sy = A
    stp = [(sx, sy), (sx - .05 * L, sy - .06 * L), (sx - .04 * L, sy - .15 * L)]
    sc = 'rgb(%d,%d,%d)' % stem
    out = ('<path d="%s" fill="rgb(%d,%d,%d)" stroke="rgb(%d,%d,%d)" stroke-width="%s" stroke-linejoin="round"/>' % (body, *fill, *outline, n2(.028 * L)))
    out += '<path d="%s" fill="none" stroke="rgb(%d,%d,%d)" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (P(hl, False), *hi, n2(.02 * L))
    out += '<path d="%s" fill="none" stroke="rgb(%d,%d,%d)" stroke-width="%s" stroke-linecap="round"/>' % (P(stp, False), *outline, n2(.08 * L))
    out += '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (P(stp, False), sc, n2(.052 * L))
    out += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="rgb(%d,%d,%d)" stroke-width="%s"/>' % (n2(sx), n2(sy + .005 * L), n2(.055 * L), n2(.055 * L), sc, *outline, n2(.012 * L))
    return out, (.6 * L + pad, .375 * L + pad)


def chile(cx, cy, L, ang, fill, outline, hi, stem=(86, 52, 36)):
    inner, (ox, oy) = chile_inner(L, fill, outline, hi, stem)
    return _g(inner, cx, cy, ang, ox, oy)


def flame(cx, cy, h, outline, outer, inner_c):
    w = h * .8; pad = h * .1
    ox, oy = pad + w / 2, .6 * h + 0 * pad + 0.0
    ox, oy = (w + 2 * pad) / 2, (h + 2 * pad) / 2

    def tongue(c, hh, ww, bend, col, out=None, ow=0):
        left, right = [], []
        for i in range(21):
            t = i / 20
            half = .5 * ww * (1 - t ** 1.25) ** .85 * (1 + .10 * math.sin(t * 10 + bend * 5))
            xs = c + bend * ww * math.sin(t * math.pi * .85)
            y = pad + h - hh * t
            left.append((xs - half, y)); right.append((xs + half, y))
        pts = left + right[::-1]
        st = ' stroke="rgb(%d,%d,%d)" stroke-width="%s" stroke-linejoin="round"' % (*out, n2(ow)) if out else ''
        return '<path d="%s" fill="rgb(%d,%d,%d)"%s/>' % (P(pts), *col, st)

    ow = max(2, h * .025)
    c = pad + w / 2
    s = (tongue(c - .20 * w, .62 * h, .40 * w, -.20, outer, outline, ow) + tongue(c + .20 * w, .72 * h, .42 * w, .22, outer, outline, ow) +
         tongue(c, h * .98, .55 * w, .05, outer, outline, ow) + tongue(c, h * .62, .30 * w, .04, inner_c))
    return _g(s, cx, cy, 0, ox, oy)


def bowl(cx, cy, sz, body, rim, outline, steam=None, with_chile=False, red=(150, 22, 34)):
    pad = .1 * sz; N = sz + 2 * pad
    ox, oy = N / 2, N * .95 / 2
    Pp = lambda x, y: (pad + x * sz, pad + y * sz)
    ow = max(2, sz * .02)
    o = ''
    oc = 'rgb(%d,%d,%d)' % outline
    if steam:
        for k, x0 in enumerate((.40, .55)):
            pts = [(pad + (x0 + .04 * math.sin(i / 20 * 2 * math.pi * 1.4 + k)) * sz, pad + (.22 - .2 * i / 20) * sz) for i in range(21)]
            o += '<path d="%s" fill="none" stroke="rgb(%d,%d,%d)" stroke-width="%s" stroke-linecap="round"/>' % (P(pts, False), *steam, n2(max(2, sz * .035)))
    for (x0, y0, x1, y1) in ((.18, .70, .30, .92), (.70, .70, .82, .92), (.44, .76, .56, .95)):
        a, b = Pp(x0, y0); c, d = Pp(x1, y1)
        o += '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="rgb(%d,%d,%d)" stroke="%s" stroke-width="%s"/>' % (n2(a), n2(b), n2(c - a), n2(d - b), n2(sz * .04), *body, oc, n2(ow))
    a, b = Pp(.04, .30); c, d = Pp(.96, .82)
    o += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="rgb(%d,%d,%d)" stroke="%s" stroke-width="%s"/>' % (n2((a + c) / 2), n2((b + d) / 2), n2((c - a) / 2), n2((d - b) / 2), *body, oc, n2(ow))
    a, b = Pp(.09, .33); c, d = Pp(.91, .58)
    o += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="rgb(%d,%d,%d)" stroke="%s" stroke-width="%s"/>' % (n2((a + c) / 2), n2((b + d) / 2), n2((c - a) / 2), n2((d - b) / 2), *rim, oc, n2(ow))
    if with_chile:
        L = int(sz * .55)
        inner, (ocx, ocy) = chile_inner(L, red, (92, 12, 22), (205, 60, 62))
        # pasted rotated 35 deg ccw at layer origin (pad+.28sz, pad-.02sz)
        o += '<g transform="translate(%s %s) rotate(-35 %s %s)">%s</g>' % (n2(pad + .28 * sz), n2(pad - .02 * sz), n2(ocx), n2(ocy), inner)
    return _g(o, cx, cy, 0, ox, oy)


def agave(cx, cy, sz, fill, outline, rib):
    ox, oy = 1.2 * sz, .95 * sz
    ax, ay = 1.2 * sz, 1.65 * sz
    o = ''
    for deg in sorted(range(-75, 76, 15), key=lambda v: -abs(v)):
        a = math.radians(deg)
        v = (math.sin(a), -math.cos(a)); nn = (math.cos(a), math.sin(a))
        L = sz * (1.05 - .15 * abs(deg) / 75)
        mid = (ax + .45 * L * v[0], ay + .45 * L * v[1]); tip = (ax + L * v[0], ay + L * v[1]); w = .15 * L
        pts = [(ax, ay), (mid[0] + nn[0] * w, mid[1] + nn[1] * w), tip, (mid[0] - nn[0] * w, mid[1] - nn[1] * w)]
        o += '<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (P(pts), fill, outline, n2(max(2, sz * .02)))
        o += '<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (n2(ax), n2(ay), n2(ax + .85 * L * v[0]), n2(ay + .85 * L * v[1]), rib, n2(max(1.5, sz * .015)))
    return _g(o, cx, cy, 0, ox, oy)
