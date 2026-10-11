"""Build SVG versions of the La Weris brand kit.
Text -> real outlined paths (fontTools). Illustrations/portrait -> traced with vtracer. Flag outline, backgrounds -> exact paths."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand2 as B
import vtracer
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

OUT = '/home/claude/weris/vector/'
TMP = '/home/claude/vtmp/'
hexc = lambda c: '#%02X%02X%02X' % tuple(c[:3])


def trace(img, name, **kw):
    p = TMP + name + '.png'
    img.save(p)
    o = TMP + name + '.svg'
    args = dict(colormode='color', hierarchical='stacked', mode='spline', filter_speckle=6, color_precision=6,
                layer_difference=14, corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=2)
    args.update(kw)
    vtracer.convert_image_to_svg_py(p, o, **args)
    s = open(o).read()
    inner = re.sub(r'^.*?<svg[^>]*>', '', s, flags=re.S).replace('</svg>', '')
    return inner.strip()


def text_path(fontfile, txt, L, x, ycenter, rot_up=True):
    """Outline `txt` scaled so its advance width = L; rotated to read upward; ink-box left edge at x, centered at ycenter.
    Returns (svg path d, ink_height)."""
    f = TTFont(fontfile)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    upm = f['head'].unitsPerEm
    names = [cmap[ord(c)] for c in txt]
    adv = sum(hmtx[n][0] for n in names)
    s = L / adv
    # ink bounds in font units (y up)
    bp = BoundsPen(gs)
    pen_x = 0
    for n in names:
        gs[n].draw(TransformPen(bp, (1, 0, 0, 1, pen_x, 0)))
        pen_x += hmtx[n][0]
    x0, y0, x1, y1 = bp.bounds
    inkw, inkh = (x1 - x0) * s, (y1 - y0) * s
    # glyph space (u,v) y-up -> reading-upward page coords: X = X0 + (v - y0)*s? rotate -90: page x = right-of-baseline-up
    # text direction (u) maps to page -y (upward); glyph up (v) maps to page -x (left). So top of letters faces LEFT.
    top = ycenter + inkw / 2
    X0 = x + (y1 - 0) * s          # page x of baseline v=0 ... v=y1 sits at x
    sp = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    pen_x = 0
    for n in names:
        # page = (X0 - v*s, top - (u+pen_x - x0)*s)
        t = (0, -s, -s, 0, 0, 0)
        # matrix mapping (u,v)->(a*u+c*v+e, b*u+d*v+f); a=0,b=-s,c=-s,d=0
        e = X0
        fy = top + x0 * s - 0
        gs[n].draw(TransformPen(sp, (0, -s, -s, 0, e, fy - 0 + (-0) + (pen_x * -s) * -1 * -1 if False else fy + pen_x * -s)))
        pen_x += hmtx[n][0]
    return sp.getCommands(), inkh


def silhouette_d(W, H):
    return ("M0,0 C%g,0 %g,0 %g,0 C%g,0 %g,%g %g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g 0,%g Z" % (
        .20 * W, .40 * W, .56 * W, .93 * W, W, .07 * H, W, .215 * H, W, .45 * H, .90 * W, .70 * H, .825 * W, .795 * H,
        .74 * W, .86 * H, .45 * W, .94 * H, H))


def svg_wrap(w, h, body, title, vb=None):
    vb = vb or '0 0 %g %g' % (w, h)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" width="%g" height="%g">'
            '<title>%s</title>\n%s\n</svg>\n' % (vb, w, h, title, body))


card, badge, block = B.load_artwork()
import numpy as np
_blk = card.crop((95, 848, 1065, 1275)).convert('RGB')
_a = np.asarray(_blk).astype(float); _bg = np.array(B.SAGE, float)
_al = np.clip((np.linalg.norm(_a - _bg, axis=2) - 26) / 54, 0, 1); _al[_al < 0.10] = 0
_fg = np.clip((_a - (1 - _al[..., None]) * _bg) / np.maximum(_al[..., None], 0.08), 0, 255)
block = Image.fromarray(np.dstack([_fg, _al * 255]).astype(np.uint8), 'RGBA')
SAGE = hexc(B.SAGE)

# ---------- badge (traced)
bd = badge.copy()
bflat = Image.new('RGB', bd.size, B.SAGE)
bflat.paste(bd, (0, 0), bd)
badge_inner = trace(bflat, 'badge', color_precision=7, layer_difference=10, filter_speckle=4)
BW = bd.width
badge_g = ('<clipPath id="bclip"><circle cx="%g" cy="%g" r="%g"/></clipPath><g id="retrato-sello" clip-path="url(#bclip)">%s</g>'
           % (BW / 2, BW / 2, BW / 2 - 3, badge_inner))

# ---------- wordmark block (traced, flat on sage)
bl = Image.new('RGB', block.size, B.SAGE)
bl.paste(block, (0, 0), block)
block_inner = trace(bl, 'block', color_precision=6, layer_difference=12, filter_speckle=4)

open(OUT + 'La_Weris_Retrato_Sello.svg', 'w').write(svg_wrap(BW, BW, badge_g, 'La Weris - retrato sello'))

# ---------- logo master 1147x1396
cw, ch = card.size
logo = ('<rect id="fondo" width="%d" height="%d" rx="60" fill="%s"/>\n<g transform="translate(%g %g)">%s</g>\n'
        '<g id="nombre-molcajete" transform="translate(95 848)">%s</g>' % (cw, ch, SAGE, 575 - BW / 2, 461 - BW / 2, badge_g, block_inner))
open(OUT + 'La_Weris_Logo_Master.svg', 'w').write(svg_wrap(cw, ch, logo, 'La Weris - logo master'))

# ---------- wordmark only, transparent (cream script on any green)
open(OUT + 'La_Weris_Nombre_Molcajete.svg', 'w').write(
    svg_wrap(970, 427, '<rect width="970" height="427" fill="%s"/>%s' % (SAGE, block_inner), 'La Weris - nombre y molcajete (fondo verde logo)'))

# ---------- profile photo 1080 (circle-safe)
pf = ('<rect width="1080" height="1080" fill="%s"/><g transform="translate(%g 90)">%s</g>'
      '<g transform="translate(255 778) scale(%g)">%s</g>' % (SAGE, (1080 - 650) / 2, badge_g.replace('id="bclip"', 'id="bclip2"').replace('url(#bclip)', 'url(#bclip2)'), 570 / 970.0, block_inner))
pf = pf.replace('<g transform="translate(215 90)">', '<g transform="translate(215 90) scale(%g)">' % (650 / BW))
open(OUT + 'La_Weris_Foto_Perfil.svg', 'w').write(svg_wrap(1080, 1080, pf, 'La Weris - foto de perfil'))

# ---------- flags
W, H = 1090, 3000
for kind, bgc, tag, fname in (('verde', B.GREEN, 'Cocina Regional', 'Verde_Agave'), ('rojo', B.CRIMSON, 'El Sabor del Chile', 'Rojo_Chile')):
    pat = B.flag_art(kind, badge, pattern_only=True)           # 2180 x 6000, transparent
    pat = pat.resize((W, H), Image.LANCZOS)
    pat_inner = trace(pat, 'pat_' + kind, colormode='color', color_precision=6, layer_difference=10, filter_speckle=8)
    yc = 0.585 * H
    x = 0.15 * W
    parts = []
    for fnt, txt, L, col, gap, tid in ((B.PLAY_BI, 'LA WERIS', .50 * H, B.FLAG_CREAM, .075, 'nombre'),
                                       (B.PLAY_B, 'COMIDA CASERA', .41 * H, B.FLAG_YELLOW, .055, 'giro'),
                                       (B.PLAY_B, tag, .39 * H, B.FLAG_CREAM, 0, 'lema')):
        d, inkh = text_path(fnt, txt, L, x, yc)
        parts.append('<path id="%s" d="%s" fill="%s"/>' % (tid, d, hexc(col)))
        x += inkh + gap * W
    bd_ = 0.54 * W
    bx, by = 0.366 * W - bd_ / 2, 0.088 * H
    body = ('<defs><clipPath id="silueta"><path d="%s"/></clipPath></defs>\n'
            '<g clip-path="url(#silueta)">\n<rect id="fondo" width="%d" height="%d" fill="%s"/>\n<g id="ilustraciones">%s</g>\n'
            '<g transform="translate(%g %g) scale(%g)">%s</g>\n<g id="texto">%s</g>\n</g>\n'
            '<path id="contorno-corte" d="%s" fill="none" stroke="#FF00FF" stroke-width="2" stroke-dasharray="12 8" opacity="0"/>'
            % (silhouette_d(W, H), W, H, hexc(bgc), pat_inner, bx, by, bd_ / BW,
               badge_g.replace('id="bclip"', 'id="bclip3"').replace('url(#bclip)', 'url(#bclip3)'), '\n'.join(parts), silhouette_d(W, H)))
    open(OUT + 'La_Weris_Bandera_%s.svg' % fname, 'w').write(svg_wrap(W, H, body, 'La Weris - bandera ' + fname))
print('ok')
