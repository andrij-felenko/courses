# -*- coding: utf-8 -*-
"""svgkit — спільні помічники для figs.py усіх розділів курсу.
НЕ копіювати ці функції у figs.py — імпортувати:

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
    from svgkit import *

Єдиний стиль (§9 AUTHORING): білий фон, sans-serif, «+» червоний, «−» синій, поле зелене.
Головне: рамки з текстом самі підганяються під напис (textbox/fitwidth) — текст НЕ вилазить за межі.
"""

# ── Палітра (єдина між розділами) ──────────────────────────────────────────
POS   = "#c0392b"   # «+», гаряче, небезпека
NEG   = "#2457d6"   # «−», холодне
FIELD = "#27ae60"   # поле / зелене виділення
INK   = "#1a1a1a"   # основний текст і лінії
MUTED = "#6b7280"   # другорядне
LINE  = "#333333"
FILL  = "#f4f6f8"   # світла заливка рамок
BG    = "#ffffff"
FONT  = "'Segoe UI', 'DejaVu Sans', Arial, sans-serif"

def esc(s):
    s = str(s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

# ── Оцінка ширини тексту (sans-serif), щоб рамка точно вмістила напис ───────
def text_width(s, size=14, bold=False):
    """Приблизна ширина рядка в px. Свідомо з запасом, щоб текст не вилазив."""
    k = 0.62 if bold else 0.57
    return len(str(s)) * size * k

def fit_font(s, max_w, size=14, bold=False, min_size=8):
    """Зменшити шрифт, якщо текст не влазить у max_w; не нижче min_size."""
    while size > min_size and text_width(s, size, bold) > max_w:
        size -= 1
    return size

# ── Примітиви ──────────────────────────────────────────────────────────────
def text(x, y, s, size=14, color=INK, anchor="middle", bold=False, italic=False):
    w = ' font-weight="700"' if bold else ''
    it = ' font-style="italic"' if italic else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s%s>%s</text>' % (x, y, FONT, size, color, anchor, w, it, esc(s)))

def mtext(x, y, lines, size=14, color=INK, anchor="middle", lh=1.3, bold=False):
    """Багаторядковий текст через <tspan> (рядки — список або текст із \\n)."""
    if isinstance(lines, str):
        lines = lines.split("\n")
    out = ['<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
           'text-anchor="%s"%s>' % (x, y, FONT, size, color, anchor,
                                    ' font-weight="700"' if bold else '')]
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else size * lh
        out.append('<tspan x="%.1f" dy="%.1f">%s</tspan>' % (x, dy, esc(ln)))
    out.append("</text>")
    return "".join(out)

def rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.5, rx=6):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f"/>' % (x, y, w, h, rx, fill, stroke, sw))

def line(x1, y1, x2, y2, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (x1, y1, x2, y2, color, sw, d))

def arrow(x1, y1, x2, y2, color=LINE, sw=1.8):
    """Стрілка (потребує defs з marker — їх додає render())."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))

def circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (cx, cy, r, fill, stroke, sw))

# ── Рамка з текстом, що ГАРАНТОВАНО вмістить напис (§9) ──────────────────────
def textbox(cx, cy, s, size=14, pad=10, fill=FILL, stroke=LINE, sw=1.5,
            color=INK, bold=False, min_w=0, rx=6):
    """Прямокутник із центром (cx,cy), автоматично завширшки під текст + поля.
    s може бути багаторядковим (список або \\n). Повертає SVG-фрагмент.
    Текст НІКОЛИ не вилазить за рамку — ширина рахується від найдовшого рядка."""
    lines = s.split("\n") if isinstance(s, str) else list(s)
    tw = max(text_width(ln, size, bold) for ln in lines)
    w = max(min_w, tw + 2 * pad)
    h = len(lines) * size * 1.3 + 2 * pad - size * 0.3
    x, y = cx - w / 2, cy - h / 2
    body = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx)
    ty = cy - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
    body += mtext(cx, ty, lines, size=size, color=color, bold=bold)
    return body, w, h

def fitbox(x, y, w, h, s, size=14, pad=8, **kw):
    """Текст у ЗАДАНУ рамку (x,y,w,h): шрифт автоматично зменшується, щоб влізти;
    якщо й мінімальним не влазить — переноситься на рядки. Не вилазить за межі."""
    lines = s.split("\n") if isinstance(s, str) else list(s)
    fs = min(fit_font(ln, w - 2 * pad, size, kw.get("bold", False)) for ln in lines)
    out = rect(x, y, w, h, fill=kw.get("fill", FILL), stroke=kw.get("stroke", LINE),
               sw=kw.get("sw", 1.5), rx=kw.get("rx", 6))
    cy = y + h / 2 - (len(lines) - 1) * fs * 1.3 / 2 + fs * 0.35
    out += mtext(x + w / 2, cy, lines, size=fs, color=kw.get("color", INK), bold=kw.get("bold", False))
    return out

def plus(cx, cy, r=9):
    return (circle(cx, cy, r, fill="#fdecea", stroke=POS, sw=2) +
            text(cx, cy + r * 0.45, "+", size=int(r * 1.8), color=POS, bold=True))

def minus(cx, cy, r=9):
    return (circle(cx, cy, r, fill="#eaf0fd", stroke=NEG, sw=2) +
            text(cx, cy + r * 0.4, "−", size=int(r * 1.8), color=NEG, bold=True))

# ── Складання й запис ───────────────────────────────────────────────────────
def render(path, w, h, *frags, title=None):
    """Зібрати SVG (з defs-стрілкою) і записати у файл path."""
    defs = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % LINE)
    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>' % (w, h, FONT, w, h, BG))
    parts = [head, defs]
    if title:
        parts.append(text(w / 2, 26, title, size=17, bold=True))
    parts.extend(f for f in frags if f)
    parts.append("</svg>")
    import io
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return path
