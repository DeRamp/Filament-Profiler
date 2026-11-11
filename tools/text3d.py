"""Turn text into manifold3d solids, for labels printed on test parts.

Uses the bundled DejaVu Sans Bold font (tools/fonts, free license) so the
output is the same on every machine.
"""
from __future__ import annotations

from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from manifold3d import CrossSection, FillRule, Manifold

FONT = Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"
_font = None


def _get_font():
    global _font
    if _font is None:
        _font = TTFont(str(FONT))
    return _font


class _PolyPen(BasePen):
    """Flattens glyph outlines into closed polygons."""

    def __init__(self, glyphset, steps=8):
        super().__init__(glyphset)
        self.polys, self.cur, self.steps = [], [], steps

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((
                mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1],
            ))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((
                mt**2 * p0[0] + 2 * mt * t * p1[0] + t**2 * p2[0],
                mt**2 * p0[1] + 2 * mt * t * p1[1] + t**2 * p2[1],
            ))

    def _closePath(self):
        if len(self.cur) > 2:
            self.polys.append(self.cur)
        self.cur = []

    _endPath = _closePath


def text_section(text: str, cap_h: float) -> CrossSection:
    """2D outline of `text`, cap height `cap_h` mm, centred on the origin."""
    font = _get_font()
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    cap = getattr(font["OS/2"], "sCapHeight", 0) or font["head"].unitsPerEm * 0.73
    s = cap_h / cap
    polys, x = [], 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = _PolyPen(gs)
        gs[name].draw(pen)
        for poly in pen.polys:
            polys.append([((px + x) * s, py * s) for px, py in poly])
        x += gs[name].width
    if not polys:
        return CrossSection()
    cs = CrossSection(polys, FillRule.NonZero)
    x0, _, x1, _ = cs.bounds()
    return cs.translate((-(x0 + x1) / 2, -cap_h / 2))


def text_width(text: str, cap_h: float) -> float:
    b = text_section(text, cap_h).bounds()
    return b[2] - b[0]


def fit_cap_height(text: str, max_w: float, cap_h: float) -> float:
    """Shrink cap height until text fits within max_w."""
    w = text_width(text, cap_h)
    return cap_h if w <= max_w else cap_h * max_w / w


def engrave_top(text: str, cx: float, cy: float, top_z: float, cap_h: float, depth: float,
                max_w: float | None = None) -> Manifold:
    """Cutter that engraves `text` into a horizontal top face at top_z."""
    if max_w:
        cap_h = fit_cap_height(text, max_w, cap_h)
    cs = text_section(text, cap_h)
    return cs.extrude(depth + 1).translate((cx, cy, top_z - depth))


def engrave_side(text: str, cx: float, cz: float, face_y: float, cap_h: float, depth: float,
                 front: bool = True, max_w: float | None = None) -> Manifold:
    """Cutter that engraves `text` into a vertical face at y = face_y.

    front=True: the face looks toward -Y (text reads correctly from the front).
    front=False: the face looks toward +Y (text reads correctly from the back).
    """
    if max_w:
        cap_h = fit_cap_height(text, max_w, cap_h)
    cs = text_section(text, cap_h)
    if not front:
        cs = cs.mirror((1, 0))
    # extrude along +Z, then rotate +90 deg about X: 2D y -> Z, extrusion -> -Y
    m = cs.extrude(depth + 1).rotate((90, 0, 0))  # occupies y in [-(depth+1), 0]
    if front:
        m = m.translate((cx, face_y + depth, cz))
    else:
        m = m.mirror((0, 1, 0)).translate((cx, face_y - depth, cz))
    return m
