# La Weris — hand-built vector redraw (true SVG, no auto-tracing)

Rebuilt from scratch to match the identity board mockup. Everything is native shapes/paths: edit colors, move, scale or delete any element in Inkscape / Illustrator / Affinity / Figma.

- `La_Weris_Tablero_Identidad.svg` — full board (logo card, both flags on poles, napkin). `_vista.png` is a preview.
- `La_Weris_Logo_Master.svg`, `La_Weris_Nombre_Lockup.svg`, `La_Weris_Retrato_Sello.svg`, `La_Weris_Molcajete_Icono.svg`, `La_Weris_Foto_Perfil.svg`
- `La_Weris_Bandera_Verde_Agave.svg`, `La_Weris_Bandera_Rojo_Chile.svg` (1090×3000 units; silhouette, text, illustrations and portrait in separate groups)

Text (flags, wordmark, labels) is converted to outlines: Playfair Display (flags), Norican (script "La Weris"), Poppins (COMIDA CASERA, tagline). Fonts are SIL OFL.

Honest limits: this is a close redraw, not a pixel copy. Portrait, ornaments and molcajete are my own drawing and differ in detail from the mockup (hair texture, face, corn/agave shapes). The script is Norican, the nearest free font, not the mockup's original lettering. Green flag texture is agave only (no arches). The board omits the stock salsa-bowl photo and the small Mexican flag. No CMYK/Pantone; printer converts. Rebuild with `scripts/build_redraw.py`.
