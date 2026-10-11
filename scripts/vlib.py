"""Hand-built SVG parts for La Weris (no tracing). All coordinates are plain SVG user units."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

FW = '/home/claude/fontwork/node_modules/@fontsource/'
GF = '/usr/share/fonts/truetype/google-fonts/'


def fp(pkg, w, style='normal'):
    return FW + pkg + '/files/' + pkg + '-latin-' + str(w) + '-' + style + '.woff'


PLAY_BI, PLAY_B, PLAY_R = fp('playfair-display', 900, 'italic'), fp('playfair-display', 700), fp('playfair-display', 400)
NORICAN = fp('norican', 400)
POP_R, POP_M, POP_SB = GF + 'Poppins-Regular.ttf', GF + 'Poppins-Medium.ttf', GF + 'Poppins-SemiBold.ttf'

_cache = {}


def _font(path):
    if path not in _cache:
        f = TTFont(path)
        _cache[path] = (f, f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm)
    return _cache[path]


def n2(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def hpath(path, txt, size=None, width=None, x=0, y=0, anchor='start', tracking=0.0):
    """Outlined horizontal text. size (px) or width (fit advance). anchor start|middle|end. y = baseline.
    tracking = extra advance per glyph (px). Returns (d, advance_width)."""
    f, gs, cmap, hmtx, upm = _font(path)
    names = [cmap[ord(c)] for c in txt]
    adv = sum(hmtx[n][0] for n in names)
    if size is None:
        size = width / (adv / upm + tracking * (len(txt) - 1) / 1.0 / 1.0 * 0 + 0) * 1.0 if False else None
    s = (size / upm) if size else (width / adv)
    total = adv * s + tracking * (len(txt) - 1)
    x0 = x - (total / 2 if anchor == 'middle' else total if anchor == 'end' else 0)
    sp = SVGPathPen(gs, ntos=n2)
    px = x0
    for n in names:
        gs[n].draw(TransformPen(sp, (s, 0, 0, -s, px, y)))
        px += hmtx[n][0] * s + tracking
    return sp.getCommands(), total


def vpath(path, txt, L, x, yc):
    """Text outlined, reading upward, advance fit to L; ink-box left edge at x, centered on yc. Returns (d, ink_height)."""
    f, gs, cmap, hmtx, upm = _font(path)
    names = [cmap[ord(c)] for c in txt]
    adv = sum(hmtx[n][0] for n in names)
    s = L / adv
    bp = BoundsPen(gs)
    px = 0
    for n in names:
        gs[n].draw(TransformPen(bp, (1, 0, 0, 1, px, 0)))
        px += hmtx[n][0]
    x0, y0, x1, y1 = bp.bounds
    top = yc + (x1 - x0) * s / 2
    X0 = x + y1 * s
    sp = SVGPathPen(gs, ntos=n2)
    px = 0
    for n in names:
        gs[n].draw(TransformPen(sp, (0, -s, -s, 0, X0, top + x0 * s - px * s)))
        px += hmtx[n][0]
    return sp.getCommands(), (y1 - y0) * s


def P(pts, close=True):
    d = 'M' + ' L'.join('%s,%s' % (n2(x), n2(y)) for x, y in pts)
    return d + ('Z' if close else '')


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def rot(pts, ang, cx=0, cy=0):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


# ------------------------------------------------------------------ ring ornaments (unit local space, origin = anchor)
def agave(sz=60, fill='#2F7D50', line='#1B4D31', rib='#7CC79A', spread=70, n=7):
    out = []
    angs = [(-spread + 2 * spread * i / (n - 1)) for i in range(n)]
    for a in sorted(angs, key=lambda v: -abs(v)):
        L = sz * (1 - 0.18 * abs(a) / spread)
        w = sz * 0.16
        out.append('<path d="M0,0 Q%s,%s 0,%s Q%s,%s 0,0Z" transform="rotate(%s)" fill="%s" stroke="%s" stroke-width="1.8" stroke-linejoin="round"/>'
                   % (n2(w * 1.6), n2(-L * .5), n2(-L), n2(-w * 1.6), n2(-L * .5), n2(a), fill, line))
        out.append('<path d="M0,-2 L0,%s" transform="rotate(%s)" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % (n2(-L * .78), n2(a), rib))
    return '<g>%s</g>' % ''.join(out)


def corn(sz=64):
    h = sz
    out = ['<g>']
    # husk leaves (behind and in front)
    out.append('<path d="M0,{a} C{b},{c} {d},{e} {f},{g} C{f},{h} {i},{h} 0,{a}Z" fill="#2E7D4F" stroke="#1B4D31" stroke-width="2"/>'.format(
        a=n2(h * .1), b=n2(-h * .30), c=n2(h * .20), d=n2(h * .15), e=n2(-h * .22), f=n2(h * .62), g=n2(-h * .02), h=n2(h * .55), i=n2(h * .22)))
    out.append('<path d="M0,{a} C{b},{c} {d},{e} {f},{g} C{f},{h} {i},{h} 0,{a}Z" fill="#3C9560" stroke="#1B4D31" stroke-width="2"/>'.format(
        a=n2(h * .1), b=n2(h * .30), c=n2(h * .08), d=n2(h * .08), e=n2(-h * .28), f=n2(h * .72), g=n2(-h * .35), h=n2(h * .12), i=n2(h * .24)))
    # cob
    out.append('<ellipse cx="0" cy="%s" rx="%s" ry="%s" fill="#EDBB3E" stroke="#8A5A12" stroke-width="2"/>' % (n2(-h * .30), n2(h * .21), n2(h * .46)))
    for r in range(7):
        for c in (-1, 0, 1):
            cy = -h * .66 + r * h * .13
            wv = 1 - ((cy + h * .3) / (h * .46)) ** 2
            if wv <= 0.05:
                continue
            out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="#F6D366" stroke="#B07A1C" stroke-width="1"/>'
                       % (n2(c * h * .125 - h * .05), n2(cy), n2(h * .10), n2(h * .10)))
    out.append('</g>')
    return ''.join(out)


def tile(sz=50):
    h = sz / 2
    out = ['<rect x="%s" y="%s" width="%s" height="%s" rx="4" fill="#2D4FA0" stroke="#15245A" stroke-width="3"/>' % (n2(-h), n2(-h), n2(sz), n2(sz)),
           '<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="none" stroke="#E9DDB4" stroke-width="2"/>' % (n2(-h * .72), n2(-h * .72), n2(h * 1.44), n2(h * 1.44)),
           '<circle r="%s" fill="#E9DDB4"/>' % n2(sz * .1)]
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.append('<circle cx="%s" cy="%s" r="%s" fill="#E9DDB4"/>' % (n2(dx * h * .45), n2(dy * h * .45), n2(sz * .05)))
    out.append('<path d="M%s,0 L%s,0 M0,%s L0,%s" stroke="#E9DDB4" stroke-width="2"/>' % (n2(-h * .3), n2(h * .3), n2(-h * .3), n2(h * .3)))
    return '<g>%s</g>' % ''.join(out)


def squiggle(w=60, col='#DB8A3C'):
    pts = []
    n = 8
    for i in range(n + 1):
        pts.append((-w / 2 + w * i / n, -6 if i % 2 else 6))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="%s" cy="%s" r="2.4" fill="#2D6A44"/><circle cx="%s" cy="%s" r="2.4" fill="#2D6A44"/>'
            % (P(pts, False), col, n2(-w / 2 - 6), 12, n2(w / 2 + 6), -12))


def frond(sz=62):
    out = []
    for a, k in ((-34, .85), (0, 1.0), (34, .85)):
        L = sz * k
        out.append('<path d="M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0Z" transform="rotate(%s)" fill="#2E7D4F" stroke="#1B4D31" stroke-width="2"/>'
                   % (n2(L * .38), n2(-L * .2), n2(L * .32), n2(-L * .75), n2(-L), n2(-L * .32), n2(-L * .75), n2(-L * .38), n2(-L * .2), a))
        out.append('<path d="M0,-3 Q%s,%s 0,%s" transform="rotate(%s)" fill="none" stroke="#8BD1A5" stroke-width="1.5"/>' % (n2(L * .05), n2(-L * .5), n2(-L * .85), a))
    out.append('<circle cx="-24" cy="12" r="3" fill="#D9843A"/><circle cx="26" cy="14" r="3" fill="#2D4FA0"/>')
    return '<g>%s</g>' % ''.join(out)


def heart(w, col, line, hi=True):
    h = w * .9
    d = ("M0,{a} C{b},{c} {b},{d} {e},{f} C{g},{h} 0,{i} 0,{j} C0,{i} {k},{h} {l},{f} C{m},{d} {m},{c} 0,{a}Z").format(
        a=n2(h * .5), b=n2(-w * .60), c=n2(h * .12), d=n2(-h * .30), e=n2(-w * .30), f=n2(-h * .42), g=n2(-w * .12),
        h=n2(-h * .50), i=n2(-h * .36), j=n2(-h * .20), k=n2(w * .12), l=n2(w * .30), m=n2(w * .60))
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (d, col, line) +
            ('<path d="M%s,%s Q%s,%s %s,%s" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/>'
             % (n2(-w * .38), n2(-h * .12), n2(-w * .34), n2(-h * .30), n2(-w * .14), n2(-h * .32)) if hi else ''))


def leaf_c(w, col='#25526D', rotate=0):
    return ('<path d="M%s,0 Q0,%s %s,0 Q0,%s %s,0Z" transform="rotate(%s)" fill="%s" stroke="#14303F" stroke-width="2"/>'
            % (n2(-w), n2(-w * .55), n2(w), n2(w * .25), n2(-w), rotate, col))


def tf(inner, x, y, rotate=0, scale=1):
    return '<g transform="translate(%s %s) rotate(%s) scale(%s)">%s</g>' % (n2(x), n2(y), n2(rotate), n2(scale), inner)


# ------------------------------------------------------------------ the portrait seal, 813 x 813, center (406,406)
def portrait(uid='p'):
    cx = cy = 406
    o = []
    A = o.append
    A('<defs><clipPath id="%s-disc"><circle cx="406" cy="406" r="251"/></clipPath></defs>' % uid)
    # rings
    A('<g id="%s-anillo">' % uid)
    A('<circle cx="406" cy="406" r="373" fill="#1B5430"/><circle cx="406" cy="406" r="371" fill="none" stroke="#0E3A1F" stroke-width="2"/>')
    A('<circle cx="406" cy="406" r="358" fill="#F3E7C2"/>')
    A('<circle cx="406" cy="406" r="349" fill="none" stroke="#2E6B3F" stroke-width="2.5"/>')
    A('<circle cx="406" cy="406" r="278" fill="#123F22"/><circle cx="406" cy="406" r="274" fill="#2C7443"/><circle cx="406" cy="406" r="257" fill="#123F22"/>')
    A('<circle cx="406" cy="406" r="254" fill="#F8DDAA"/></g>')
    # ornaments
    A('<g id="%s-ornamentos">' % uid)
    A(tf(heart(26, '#C94A33', '#7A2A1A', False), 406, 78))
    for x, y, r in ((364, 82, -25), (452, 82, 25)):
        A(tf('<path d="M0,0 Q10,-14 22,-12 M0,0 Q8,6 20,4 M8,-6 L12,-18" stroke="#3E8A57" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="22" cy="-12" r="3" fill="#D9843A"/>', x, y, r, 1))
    A(tf(agave(52), 296, 140, -8)); A(tf(agave(52), 516, 140, 8))
    A(tf(frond(60), 210, 205, -28)); A(tf(frond(60), 606, 205, 28))
    A(tf(squiggle(52), 244, 135, -55)); A(tf(squiggle(52), 570, 135, 55))
    A(tf(squiggle(50), 160, 240, -125)); A(tf(squiggle(50), 656, 240, 125))
    A(tf(corn(86), 126, 330, 14)); A(tf(corn(86), 688, 330, -14))
    A(tf(squiggle(46), 96, 355, 8)); A(tf(squiggle(46), 718, 355, -8))
    A(tf(agave(50, spread=60), 94, 445, 0)); A(tf(agave(50, spread=60), 720, 445, 0))
    A(tf(squiggle(46), 96, 482, -6)); A(tf(squiggle(46), 718, 482, 6))
    A(tf(tile(54), 118, 528, -10)); A(tf(tile(54), 696, 528, 10))
    A(tf(corn(82), 192, 650, 118)); A(tf(corn(82), 622, 650, -118))
    A(tf(squiggle(48), 244, 690, -60)); A(tf(squiggle(48), 572, 690, 60))
    A(tf(leaf_c(26, '#25526D', 30), 305, 696)); A(tf(leaf_c(26, '#25526D', -30), 508, 696))
    A(tf('<ellipse rx="15" ry="11" fill="#3E5FA8" stroke="#15245A" stroke-width="2.5"/>', 284, 716))
    A(tf('<ellipse rx="15" ry="11" fill="#3E5FA8" stroke="#15245A" stroke-width="2.5"/>', 530, 716))
    A(tf('<path d="M-12,0 q6,-12 14,-4 q6,8 -4,10" stroke="#3E8A57" stroke-width="3" fill="none"/>', 345, 718))
    A(tf('<path d="M12,0 q-6,-12 -14,-4 q-6,8 4,10" stroke="#3E8A57" stroke-width="3" fill="none"/>', 468, 718))
    A(tf(heart(66, '#3F8F63', '#174D2B'), 406, 724))
    for x, y in ((150, 590), (668, 590), (205, 690), (612, 690), (150, 175), (665, 175)):
        A('<circle cx="%d" cy="%d" r="3.2" fill="#D9843A"/><circle cx="%d" cy="%d" r="2.6" fill="#3E8A57"/>' % (x, y, x + 9, y + 7))
    A('</g>')
    # portrait
    SK, SKS, OUT = '#E2A06A', '#C98450', '#4A2A1C'
    A('<g id="%s-retrato">' % uid)
    A('<g clip-path="url(#%s-disc)">' % uid)
    A('<path d="M200,700 L200,640 Q232,590 330,562 L482,562 Q580,590 612,640 L612,700Z" fill="#E8743B" stroke="#7A3516" stroke-width="4"/>')
    A('<path d="M262,615 Q290,596 330,584 M552,615 Q524,596 482,584" fill="none" stroke="#C85A28" stroke-width="4" stroke-linecap="round"/>')
    A('<path d="M362,500 L362,560 Q406,626 450,560 L450,500Z" fill="%s" stroke="%s" stroke-width="4" stroke-linejoin="round"/>' % (SK, OUT))
    A('<path d="M366,520 Q406,560 446,520 L446,545 Q406,578 366,545Z" fill="%s" opacity=".55"/>' % SKS)
    A('</g>')
    # pearls
    for i in range(13):
        t = i / 12
        a = math.radians(200 + 140 * t)
        px, py = 406 + 76 * math.cos(a), 556 + 56 * -math.sin(a) * -1
        px, py = 406 - 76 * math.sin(math.radians(-90 + 180 * t) + 0) * 0 + (-70 + 140 * t), 566 + 52 * (1 - (2 * t - 1) ** 2)
        A('<circle cx="%s" cy="%s" r="%s" fill="#FBF6EA" stroke="#6E6B63" stroke-width="2"/>' % (n2(px), n2(py), 9.5 if 3 <= i <= 9 else 8))
    # ears + earrings
    for ex in (282, 530):
        A('<ellipse cx="%d" cy="436" rx="17" ry="28" fill="%s" stroke="%s" stroke-width="4"/>' % (ex, SK, OUT))
        A('<path d="M%d,424 q%d,10 0,22" fill="none" stroke="%s" stroke-width="3"/>' % (ex + (2 if ex < 400 else -2), -7 if ex < 400 else 7, SKS))
    for ex in (288, 525):
        A('<circle cx="%d" cy="466" r="8" fill="#F6E9C8" stroke="%s" stroke-width="3"/>' % (ex, OUT))
    # face
    A('<path d="M285,400 C285,330 335,296 406,296 C477,296 527,330 527,400 C527,478 488,546 406,552 C324,546 285,478 285,400Z" fill="%s" stroke="%s" stroke-width="4.5"/>' % (SK, OUT))
    A('<path d="M296,450 C306,500 340,538 372,546 M516,450 C506,500 472,538 440,546" fill="none" stroke="%s" stroke-width="3" opacity=".5"/>' % SKS)
    # cheeks
    A('<ellipse cx="338" cy="462" rx="24" ry="16" fill="#E9806E" opacity=".55"/><ellipse cx="476" cy="462" rx="24" ry="16" fill="#E9806E" opacity=".55"/>')
    # forehead lines
    A('<path d="M366,334 Q406,326 446,334 M376,346 Q406,340 436,346" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % SKS)
    # hair mass
    hair = 'M252,398 C236,300 276,214 352,204 C380,200 396,199 406,199 C416,199 432,200 460,204 C536,214 576,300 560,398 C552,374 545,352 534,336 C506,304 460,290 406,268 C352,290 306,304 278,336 C267,352 260,374 252,398Z'
    A('<path d="%s" fill="#F6F6F4" stroke="#3B2E2A" stroke-width="4.5" stroke-linejoin="round"/>' % hair)
    for d in ('M406,268 C380,250 345,240 312,262', 'M406,268 C430,250 470,240 504,262', 'M300,250 C330,226 370,222 394,236',
              'M512,250 C482,226 442,222 418,236', 'M268,340 C262,310 276,282 296,266', 'M544,340 C550,310 536,282 516,266',
              'M290,372 C282,350 284,330 292,314', 'M522,372 C530,350 528,330 520,314', 'M360,214 C380,208 396,208 406,210'):
        A('<path d="%s" fill="none" stroke="#B9BDC4" stroke-width="3.2" stroke-linecap="round"/>' % d)
    # bun
    A('<ellipse cx="406" cy="150" rx="79" ry="54" fill="#F6F6F4" stroke="#3B2E2A" stroke-width="4.5"/>')
    for d in ('M350,150 C362,120 392,108 424,112', 'M470,160 C450,178 420,184 392,176', 'M360,176 C376,190 396,194 416,190', 'M446,110 C470,118 478,134 474,150'):
        A('<path d="%s" fill="none" stroke="#B9BDC4" stroke-width="3.2" stroke-linecap="round"/>' % d)
    # eyebrows
    A('<path d="M320,366 Q350,350 384,362" fill="none" stroke="#3B2E2A" stroke-width="11" stroke-linecap="round"/><path d="M320,366 Q350,350 384,362" fill="none" stroke="#F4F4F0" stroke-width="6" stroke-linecap="round"/>')
    A('<path d="M428,362 Q462,350 492,366" fill="none" stroke="#3B2E2A" stroke-width="11" stroke-linecap="round"/><path d="M428,362 Q462,350 492,366" fill="none" stroke="#F4F4F0" stroke-width="6" stroke-linecap="round"/>')
    # eyes
    for ex in (352, 460):
        A('<ellipse cx="%d" cy="412" rx="10" ry="8" fill="#2B1810"/><circle cx="%d" cy="409" r="2.6" fill="#fff"/>' % (ex, ex + 3))
        A('<path d="M%d,404 Q%d,396 %d,404" fill="none" stroke="#2B1810" stroke-width="3" stroke-linecap="round"/>' % (ex - 14, ex, ex + 14))
    # glasses
    A('<circle cx="352" cy="410" r="42" fill="#fff" fill-opacity=".10" stroke="#7B4313" stroke-width="7"/><circle cx="460" cy="410" r="42" fill="#fff" fill-opacity=".10" stroke="#7B4313" stroke-width="7"/>')
    A('<path d="M394,402 Q406,396 418,402" fill="none" stroke="#7B4313" stroke-width="8" stroke-linecap="round"/>')
    A('<path d="M308,404 L292,398 M504,404 L520,398" stroke="#7B4313" stroke-width="7" stroke-linecap="round"/>')
    # nose and mouth
    A('<path d="M402,428 Q392,452 400,458 Q410,462 420,454" fill="none" stroke="#9A5524" stroke-width="4" stroke-linecap="round"/>')
    A('<path d="M360,488 Q406,526 454,488" fill="none" stroke="#3A1D10" stroke-width="5.5" stroke-linecap="round"/>')
    A('<path d="M356,484 q-5,2 -6,8 M458,484 q5,2 6,8" fill="none" stroke="#9A5524" stroke-width="3.5" stroke-linecap="round"/>')
    A('<path d="M372,530 Q406,552 440,530" fill="none" stroke="%s" stroke-width="3" opacity=".7"/>' % SKS)
    A('</g>')
    return ''.join(o)


# ------------------------------------------------------------------ molcajete icon, box ~ 0..220 x 0..190
def molcajete(uid='m', steam='#EDE6B9', steam_w=5):
    o = []
    A = o.append
    A('<g id="%s">' % uid)
    for dx in (-1, 0, 1):
        pass
    # steam
    A('<path d="M92,52 C70,36 112,28 90,8 M120,56 C98,40 140,30 116,6" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (steam, steam_w))
    # legs
    for x0, x1, y0, y1 in ((46, 74, 138, 172), (150, 178, 138, 172), (100, 124, 148, 178)):
        A('<path d="M%d,%d L%d,%d Q%d,%d %d,%d Z" fill="#4A4744" stroke="#262321" stroke-width="4" stroke-linejoin="round"/>' % (x0, y0, x1, y0, x1 + 4, y1 + 4, x0 - 4, y1))
    # chile behind rim (left)
    A('<path d="M60,62 C52,44 56,30 66,22" fill="none" stroke="#3C8A4F" stroke-width="6" stroke-linecap="round"/>')
    A('<path d="M58,76 C44,56 52,36 66,28 C74,44 80,62 98,80Z" fill="#C9302C" stroke="#6A1415" stroke-width="4" stroke-linejoin="round"/>')
    # bowl
    A('<path d="M20,78 C22,128 62,150 112,150 C162,150 202,128 204,78Z" fill="#5A5653" stroke="#262321" stroke-width="5" stroke-linejoin="round"/>')
    A('<path d="M40,112 C70,134 120,140 170,126" fill="none" stroke="#7B7773" stroke-width="5" stroke-linecap="round"/>')
    A('<ellipse cx="112" cy="80" rx="94" ry="28" fill="#3A3633" stroke="#262321" stroke-width="5"/>')
    A('<ellipse cx="112" cy="82" rx="76" ry="20" fill="#7CA04A"/><ellipse cx="100" cy="82" rx="38" ry="9" fill="#9CBF5C" opacity=".8"/>')
    A('<path d="M150,60 C170,58 190,50 202,34" fill="none" stroke="#3C8A4F" stroke-width="6" stroke-linecap="round"/>')
    A('<path d="M200,40 C178,66 150,82 120,96 C132,70 162,52 200,40Z" fill="#C9302C" stroke="#6A1415" stroke-width="4" stroke-linejoin="round"/>')
    A('<path d="M140,76 C156,68 172,60 188,50" fill="none" stroke="#E5675C" stroke-width="3" stroke-linecap="round"/>')
    A('</g>')
    return ''.join(o)
