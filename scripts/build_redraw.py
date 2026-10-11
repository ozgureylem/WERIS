"""La Weris - hand-built vector master set (no auto-tracing). Output: /home/claude/weris/vector_redraw/"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib as V
import flags_svg as F
from vlib import n2, hpath, vpath

OUT = '/home/claude/weris/vector_redraw/'
os.makedirs(OUT, exist_ok=True)
SAGE, GREEN, CRIMSON = '#5E8855', '#1B6C44', '#B51826'
CREAM, YEL, INK = '#F7EED8', '#F8AA24', '#2D2D2A'


def svg(w, h, body, title, bg=None):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s">'
            '<title>%s</title>\n%s%s\n</svg>\n' % (n2(w), n2(h), n2(w), n2(h), title,
                                                  '<rect id="fondo-pagina" width="%s" height="%s" fill="%s"/>\n' % (n2(w), n2(h), bg) if bg else '', body))


def text(d, col, i=None, extra=''):
    return '<path%s d="%s" fill="%s"%s/>' % (' id="%s"' % i if i else '', d, col, extra)


# ---------------------------------------------------------------- wordmark lockup (970 x 445 box, same as mockup layout)
def wordmark(col=CREAM, sub='#F0EBC8'):
    d1, w1 = hpath(V.NORICAN, 'La Weris', width=735, x=10, y=232)
    o = text(d1, col, 'nombre', ' stroke="%s" stroke-width="3.2" stroke-linejoin="round"' % col)
    d2, _ = hpath(V.POP_R, 'COMIDA CASERA', width=560, x=485, y=352, anchor='middle')
    o += text(d2, sub, 'giro')
    try:
        d3, _ = hpath(V.POP_R, 'Tradición Zapopana • Sabor del Alma', width=830, x=485, y=420, anchor='middle')
    except KeyError:
        d3, _ = hpath(V.POP_R, 'Tradición Zapopana - Sabor del Alma', width=830, x=485, y=420, anchor='middle')
    o += text(d3, sub, 'lema')
    mol = '<g id="molcajete" transform="translate(762 96) scale(1.05)">%s</g>' % V.molcajete('mol')
    return '<g id="nombre-lockup">%s%s</g>' % (o, mol)


def logo_card(caption=False):
    bs = 369.0 / 373
    b = '<g id="retrato-sello" transform="translate(%s %s) scale(%s)">%s</g>' % (n2(575 - 406 * bs), n2(461 - 406 * bs), n2(bs), V.portrait('lc'))
    wm = '<g transform="translate(95 830)">%s</g>' % wordmark()
    o = '<rect id="fondo" width="1147" height="1396" rx="62" fill="%s"/>' % SAGE
    o += '<rect x="5" y="5" width="1137" height="1386" rx="58" fill="none" stroke="#C9B77A" stroke-width="3" opacity=".7"/>'
    o += b + wm
    if caption:
        d, _ = hpath(V.POP_M, 'Logo • Verde Agave Art artesanal.', width=470, x=62, y=1338)
        o += text(d, CREAM, 'leyenda')
    return o


# ---------------------------------------------------------------- flags
FWID, FHT = 1090, 3000


def silueta(W=FWID, H=FHT):
    return ("M0,0 C%s,0 %s,0 %s,0 C%s,0 %s,%s %s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,%s Z" % (
        n2(.20 * W), n2(.40 * W), n2(.56 * W), n2(.93 * W), n2(W), n2(.07 * H), n2(W), n2(.215 * H), n2(W), n2(.45 * H),
        n2(.90 * W), n2(.70 * H), n2(.825 * W), n2(.795 * H), n2(.74 * W), n2(.86 * H), n2(.45 * W), n2(.94 * H), n2(H)))


def flag(kind):
    W, H = FWID, FHT
    bcx, bd = .366 * W, .54 * W
    bcy = .088 * H + bd / 2
    text_rect = (.14 * W, .33 * H, .80 * W, .88 * H)
    badge_rect = (bcx - bd / 2 - 20, bcy - bd / 2 - 20, bcx + bd / 2 + 20, bcy + bd / 2 + 20)

    def blocked(x, y):
        return any(a < x < c and b < y < d for a, b, c, d in (text_rect, badge_rect))

    pat = ''
    if kind == 'rojo':
        bg, tag = CRIMSON, 'El Sabor del Chile'
        fill, outl, hi = (152, 22, 34), (96, 12, 22), (208, 62, 64)
        chiles = [(.47, .075, .50, -12), (.10, .07, .36, -82), (.84, .19, .60, -120), (.045, .40, .36, -86), (.07, .60, .50, -88),
                  (.13, .87, .52, -42), (.37, .945, .32, 14), (.84, .775, .50, -96), (.62, .12, .26, -70), (.05, .76, .34, -80),
                  (.92, .97, .28, -30), (.30, .20, .22, 55), (.70, .30, .24, -40), (.20, .31, .20, -20), (.93, .66, .20, -70),
                  (.22, .74, .22, 30), (.60, .965, .24, -10), (.90, .50, .22, -110), (.03, .53, .24, -95), (.58, .035, .22, 20)]
        for fx, fy, ln, ang in chiles:
            if blocked(fx * W, fy * H) and fx > .2:
                continue
            pat += F.chile(fx * W, fy * H, ln * W, ang, fill, outl, hi)
        for fx, fy, hw in [(.73, .245, .17), (.975, .30, .10), (.89, .505, .30), (.64, .86, .25), (.02, .15, .12), (.04, .945, .20), (.01, .36, .13)]:
            pat += F.flame(fx * W, fy * H, hw * 1.5 * W, (150, 55, 20), (236, 122, 38), (252, 196, 72))
        pat += F.bowl(.89 * W, .405 * H, .30 * W, (122, 52, 52), (150, 78, 72), (74, 26, 28), steam=(236, 130, 50), with_chile=True)
        pat += F.bowl(.845 * W, .58 * H, .34 * W, (118, 50, 50), (92, 34, 36), (74, 26, 28))
    else:
        bg, tag = GREEN, 'Cocina Regional'
        spots = [(.12, .06, .40), (.62, .05, .34), (.92, .22, .34), (.05, .24, .30), (.97, .46, .30), (.05, .50, .34), (.9, .66, .32),
                 (.08, .74, .34), (.4, .93, .34), (.75, .86, .28), (.05, .95, .30), (.55, .31, .24)]
        for fx, fy, sz in spots:
            if blocked(fx * W, fy * H) and fx > .2:
                continue
            pat += F.agave(fx * W, fy * H, sz * W, '#217450', '#16573A', '#2F8E62')
    yc, x = .585 * H, .15 * W
    parts = ''
    for fnt, t, L, col, gap, tid in ((V.PLAY_BI, 'LA WERIS', .50 * H, CREAM, .075, 'nombre'), (V.PLAY_B, 'COMIDA CASERA', .41 * H, YEL, .055, 'giro'),
                                     (V.PLAY_B, tag, .39 * H, CREAM, 0, 'lema')):
        d, ih = vpath(fnt, t, L, x, yc)
        parts += text(d, col, tid)
        x += ih + gap * W
    bs = bd / 746.0
    badge = '<g id="retrato-sello" transform="translate(%s %s) scale(%s)">%s</g>' % (n2(bcx - 406 * bs), n2(bcy - 406 * bs), n2(bs), V.portrait('fl' + kind))
    body = ('<defs><clipPath id="silueta-%s"><path d="%s"/></clipPath></defs>'
            '<g clip-path="url(#silueta-%s)"><rect id="fondo" width="%d" height="%d" fill="%s"/><g id="ilustraciones">%s</g>%s<g id="texto">%s</g></g>'
            % (kind, silueta(), kind, W, H, bg, pat, badge, parts))
    return body


def write(name, w, h, body, title, bg=None):
    open(OUT + name, 'w').write(svg(w, h, body, title, bg))


write('La_Weris_Retrato_Sello.svg', 813, 813, V.portrait('rs'), 'La Weris - retrato sello')
write('La_Weris_Molcajete_Icono.svg', 224, 184, V.molcajete('mi'), 'La Weris - molcajete icono')
write('La_Weris_Logo_Master.svg', 1147, 1396, logo_card(), 'La Weris - logo master')
write('La_Weris_Nombre_Lockup.svg', 970, 445, '<rect width="970" height="445" fill="%s"/>' % SAGE + wordmark(), 'La Weris - nombre (sobre verde logo)')
write('La_Weris_Bandera_Verde_Agave.svg', FWID, FHT, flag('verde'), 'La Weris - bandera verde agave')
write('La_Weris_Bandera_Rojo_Chile.svg', FWID, FHT, flag('rojo'), 'La Weris - bandera rojo chile')
bs = 650 / 746.0
write('La_Weris_Foto_Perfil.svg', 1080, 1080,
      '<rect width="1080" height="1080" fill="%s"/><g transform="translate(%s %s) scale(%s)">%s</g><g transform="translate(255 778) scale(.588)">%s</g>'
      % (SAGE, n2(540 - 406 * bs), n2(90 + 373 * bs - 406 * bs), n2(bs), V.portrait('pf'), wordmark()), 'La Weris - foto de perfil')

# ---------------------------------------------------------------- identity board (like the supplied mockup), 2272 x 1882
BW, BH = 2272, 1882
bo = ''
d, _ = hpath(V.PLAY_BI, 'LA WERIS', width=410, x=104, y=124); bo += text(d, '#1F1F1B', 'titulo')
d, _ = hpath(V.POP_R, 'Identity Redesign for a Home-Style Food Stand', width=852, x=104, y=188); bo += text(d, INK)
d, _ = hpath(V.POP_R, 'Zapopan, Jalisco - Mexico', width=478, x=104, y=232); bo += text(d, INK)
bo += ('<defs><filter id="sombra" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity=".28"/></filter></defs>')
sc = 730 / 1147.0
bo += '<g id="tarjeta-logo" transform="translate(110 320) scale(%s)" filter="url(#sombra)">%s</g>' % (n2(sc), logo_card(True))


def pole(x, ytop, ybot):
    return ('<ellipse cx="%s" cy="%s" rx="62" ry="12" fill="#CFCABD" opacity=".7"/><rect x="%s" y="%s" width="104" height="14" rx="7" fill="#37373A"/>'
            '<rect x="%s" y="%s" width="9" height="%s" fill="#2B2B2D"/><circle cx="%s" cy="%s" r="10" fill="#2B2B2D"/>'
            % (n2(x), n2(ybot + 10), n2(x - 52), n2(ybot - 6), n2(x - 4.5), n2(ytop - 22), n2(ybot - ytop + 22), n2(x), n2(ytop - 22)))


fs = 1160 / 3000.0
for kind, x, lab1, lab2 in (('verde', 1060, 'Bandera • Verde Agave & Textura', 'Hecho con orgullo zapopano'),
                            ('rojo', 1580, 'Bandera • Rojo Chile & Picante', 'Sabor auténtico de casa')):
    bo += pole(x, 322, 1664)
    bo += '<g transform="translate(%s 322) scale(%s)">%s</g>' % (n2(x), n2(fs), flag(kind).replace('silueta-', 'silueta-b-').replace('id="retrato', 'id="b-retrato'))
    d1, _ = hpath(V.POP_R, lab1, size=26, x=x - 50, y=1740); d2, _ = hpath(V.POP_R, lab2, size=26, x=x - 50, y=1782)
    bo += text(d1, INK) + text(d2, INK)

# napkin
bo += ('<g transform="translate(640 1540) rotate(-14)"><rect x="-190" y="-190" width="380" height="380" fill="#FBFAF6" filter="url(#sombra)"/>'
       '<rect x="-190" y="-190" width="380" height="380" fill="none" stroke="#E7E4DA" stroke-width="3"/>'
       '<g transform="translate(-100 -92) scale(.9)">%s</g></g>') % V.molcajete('nap', steam='#E49A3D', steam_w=6).replace('#EDE6B9', '#E49A3D')
write('La_Weris_Tablero_Identidad.svg', BW, BH, bo, 'La Weris - tablero de identidad', bg='#F7F0DE')
print('built')
