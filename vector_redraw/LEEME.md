# La Weris — hand-built vector redraw (true SVG, no auto-tracing)

Rebuilt from scratch to match the identity board mockup. Everything is native shapes/paths: edit colors, move, scale or delete any element in Inkscape / Illustrator / Affinity / Figma.

- `La_Weris_Tablero_Identidad.svg` — full board (logo card, both flags on poles, napkin). `_vista.png` is a preview.
- `La_Weris_Logo_Master.svg`, `La_Weris_Nombre_Lockup.svg`, `La_Weris_Retrato_Sello.svg`, `La_Weris_Molcajete_Icono.svg`, `La_Weris_Foto_Perfil.svg`
- `La_Weris_Bandera_Verde_Agave.svg`, `La_Weris_Bandera_Rojo_Chile.svg` (1090×3000 units; silhouette, text, illustrations and portrait in separate groups)

Text (flags, wordmark, labels) is converted to outlines: Playfair Display (flags), Norican (script "La Weris"), Poppins (COMIDA CASERA, tagline). Fonts are SIL OFL.

Portrait: uses the vector supplied by the client (`reference/portrait_user_supplied_original.svg`, 427 shapes after cropping to the seal circle; its fake checkerboard background was clipped away). The original file's metadata says it was produced with an AI tool (Recraft), so confirm usage rights before commercial use. The molcajete, flag illustrations and layout are my own drawing.

Honest limits: this is a close redraw, not a pixel copy. The script is Norican, the nearest free font, not the mockup's original lettering. Green flag texture is agave only (no arches). The board omits the stock salsa-bowl photo and the small Mexican flag. No CMYK/Pantone; printer converts. Rebuild with `scripts/build_redraw.py`.
