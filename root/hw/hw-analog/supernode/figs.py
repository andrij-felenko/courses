# -*- coding: utf-8 -*-
"""Фігури до статті «Суперузол» (book/electronics/analog/supernode).
Три фігури:
  idea.svg    — суть: джерело напруги між двома не-земляними вузлами рве баланс,
                суперузол обводить обидва вузли разом
  cut.svg     — що входить у рівняння: зовнішні гілки перетинають межу, внутрішнє
                джерело — ні
  recipe.svg  — три кроки: упізнати → обвести й скласти струми → додати обмеження
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def node(cx, cy, label, col=INK, r=7, lab_dy=-16):
    out = [circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.4),
           circle(cx, cy, 2.6, fill=col, stroke=col)]
    if label:
        out.append(text(cx, cy + lab_dy, label, size=14, color=col, bold=True))
    return "".join(out)


def resistor_h(x0, x1, y, label=None, lab_dy=-12):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    out.append(line(x0, y, x0 + seg, y, color=INK, sw=1.6))
    amp = 6
    xx = x0 + seg
    prev = y
    for i in range(n):
        ny = y - amp if i % 2 == 0 else y + amp
        out.append(line(xx, prev, xx + seg, ny, color=INK, sw=1.6))
        xx += seg
        prev = ny
    out.append(line(xx, prev, x1, y, color=INK, sw=1.6))
    if label:
        out.append(text((x0 + x1) / 2, y + lab_dy, label, size=12, color=INK, bold=True))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="left"):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    out.append(line(x, y0, x, y0 + seg, color=INK, sw=1.6))
    amp = 6
    yy = y0 + seg
    prevx = x
    for i in range(n):
        nx = x - amp if i % 2 == 0 else x + amp
        out.append(line(prevx, yy, nx, yy + seg, color=INK, sw=1.6))
        yy += seg
        prevx = nx
    out.append(line(prevx, yy, x, y1, color=INK, sw=1.6))
    if label:
        lx = x - 14 if side == "left" else x + 14
        an = "end" if side == "left" else "start"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=INK, bold=True, anchor=an))
    return "".join(out)


def vsrc_h(x0, x1, y, label=None, plus_left=True):
    """Ідеальне джерело напруги (дві пластини) горизонтально між (x0,y)–(x1,y)."""
    cx = (x0 + x1) / 2
    out = [line(x0, y, cx - 7, y, color=INK, sw=1.6),
           line(cx + 7, y, x1, y, color=INK, sw=1.6),
           line(cx - 7, y - 16, cx - 7, y + 16, color=INK, sw=2.6),   # довга пластина (+)
           line(cx + 7, y - 9, cx + 7, y + 9, color=INK, sw=4.0)]     # коротка (−)
    px, mx = (cx - 7, cx + 7) if plus_left else (cx + 7, cx - 7)
    out.append(text(px + (-8 if plus_left else 8), y - 20, "+", size=15, color=POS, bold=True))
    out.append(text(mx + (8 if plus_left else -8), y - 20, "−", size=15, color=NEG, bold=True))
    if label:
        out.append(text(cx, y + 30, label, size=13, color=INK, bold=True))
    return "".join(out)


def isrc(cx, cy, label=None, up=True):
    """Джерело струму: кружечок зі стрілкою (напрям струму)."""
    r = 15
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8)]
    if up:
        out.append(arrow(cx, cy + 8, cx, cy - 8, color=NEG, sw=2.2))
    else:
        out.append(arrow(cx, cy - 8, cx, cy + 8, color=NEG, sw=2.2))
    if label:
        out.append(text(cx - r - 6, cy + 4, label, size=12, color=NEG, bold=True, anchor="end"))
    return "".join(out), (cx, cy - r), (cx, cy + r)


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — біда зліва, порятунок справа
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 720, 360
    f = []

    # ── панель «біда» ──
    f.append(text(180, 44, "Біда", size=15, bold=True, color=POS))
    ax, bx, ny = 110, 250, 150
    f.append(node(ax, ny, "A", col=INK))
    f.append(node(bx, ny, "B", col=INK))
    # джерело між A і B
    f.append(vsrc_h(ax + 9, bx - 9, ny, label="E", plus_left=True))
    # резистори на землю
    f.append(resistor_v(ax, ny + 9, 270, label="R₁", side="left"))
    f.append(resistor_v(bx, ny + 9, 270, label="R₂", side="right"))
    f.append(line(ax, 270, bx, 270, color=INK, sw=1.6))
    f.append(gnd((ax + bx) / 2, 270))
    # знак питання на струмі джерела
    f.append(text(180, ny + 38, "I крізь E = ?", size=12, color=POS, bold=True))
    body, _, _ = textbox(180, 318, "Струм крізь ідеальне E невідомий →\nбаланс ні в A, ні в B не записати",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)

    # роздільник
    f.append(line(W / 2, 60, W / 2, 300, color="#d6dadf", sw=1.4, dash="5 5"))

    # ── панель «порятунок» ──
    f.append(text(540, 44, "Порятунок: суперузол", size=15, bold=True, color=FIELD))
    ax2, bx2 = 470, 610
    # бульбашка суперузла навколо A, B, E
    f.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="20" fill="#eef7f0" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="7 5"/>'
             % (ax2 - 46, ny - 44, (bx2 - ax2) + 92, 78, FIELD))
    f.append(text((ax2 + bx2) / 2, ny - 30, "суперузол", size=12, color=FIELD, bold=True))
    f.append(node(ax2, ny, "A", col=INK))
    f.append(node(bx2, ny, "B", col=INK))
    f.append(vsrc_h(ax2 + 9, bx2 - 9, ny, label="E", plus_left=True))
    f.append(resistor_v(ax2, ny + 9, 270, label="R₁", side="left"))
    f.append(resistor_v(bx2, ny + 9, 270, label="R₂", side="right"))
    f.append(line(ax2, 270, bx2, 270, color=INK, sw=1.6))
    f.append(gnd((ax2 + bx2) / 2, 270))
    body, _, _ = textbox(540, 318, "Одне рівняння струмів на всю межу\n+ обмеження  V_a − V_b = E",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. cut.svg — які гілки перетинають межу
# ════════════════════════════════════════════════════════════════════════════
def fig_cut():
    W, H = 660, 380
    f = []
    f.append(text(W / 2, 34, "Що входить у рівняння суперузла", size=16, bold=True))

    ax, bx, ny = 230, 430, 150
    # бульбашка
    f.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="22" fill="#eef7f0" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="7 5"/>'
             % (ax - 52, ny - 46, (bx - ax) + 104, 82, FIELD))
    f.append(text((ax + bx) / 2, ny - 56, "межа суперузла", size=12, color=FIELD, bold=True))

    f.append(node(ax, ny, "A", col=INK, lab_dy=-16))
    f.append(node(bx, ny, "B", col=INK, lab_dy=-16))
    # внутрішнє джерело
    f.append(vsrc_h(ax + 9, bx - 9, ny, label="E (всередині)", plus_left=True))

    # зовнішні гілки, що перетинають межу:
    # резистор A→земля
    f.append(resistor_v(ax, ny + 9, 290, label="R₁", side="left"))
    # резистор B→земля
    f.append(resistor_v(bx, ny + 9, 290, label="R₂", side="right"))
    f.append(line(ax, 290, bx, 290, color=INK, sw=1.6))
    f.append(gnd((ax + bx) / 2, 290))
    # зовнішнє джерело струму в A згори
    src, stop, sbot = isrc(ax, ny - 96, label="I", up=False)
    f.append(line(ax, ny - 46, sbot[0], sbot[1], color=INK, sw=1.6))
    f.append(src)

    # позначки перетину межі — зелені галочки на трьох зовнішніх гілках
    def cross(x, y):
        return (circle(x, y, 9, fill="#ffffff", stroke=FIELD, sw=2.2) +
                text(x, y + 4, "✓", size=12, color=FIELD, bold=True))
    f.append(cross(ax, ny - 44))          # струм I зверху перетинає межу
    f.append(cross(ax, ny + 38))          # R1 знизу
    f.append(cross(bx, ny + 38))          # R2 знизу
    # внутрішня гілка — червоний хрестик «не перетинає»
    f.append(circle((ax + bx) / 2, ny, 9, fill="#ffffff", stroke=POS, sw=2.2))
    f.append(text((ax + bx) / 2, ny + 4, "✕", size=12, color=POS, bold=True))

    body, _, _ = textbox(W / 2, 348,
                         "✓ три зовнішні гілки перетинають межу — входять у баланс\n"
                         "✕ внутрішнє E межі не перетинає — у баланс не входить",
                         size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(body)
    render(os.path.join(IMG, "cut.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. recipe.svg — три кроки
# ════════════════════════════════════════════════════════════════════════════
def fig_recipe():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 34, "Суперузол у три кроки", size=16, bold=True))

    cards = [
        ("1", "Упізнати", ["джерело напруги E", "між двома НЕ-земляними", "вузлами (плаває)"], POS),
        ("2", "Обвести й скласти", ["один баланс струмів", "для всієї межі —", "лише гілки крізь неї"], FIELD),
        ("3", "Додати обмеження", ["рівняння джерела", "V_a − V_b = E", "(знак за полярністю)"], NEG),
    ]
    cw, ch, gap = 200, 150, 30
    x0 = (W - (3 * cw + 2 * gap)) / 2
    cy = 70
    for i, (num, title_, lines, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, cy, cw, ch, fill="#ffffff", stroke=col, sw=2.2, rx=12))
        f.append(circle(x + 26, cy + 26, 15, fill=col, stroke=col))
        f.append(text(x + 26, cy + 31, num, size=16, color="#ffffff", bold=True))
        f.append(text(x + cw / 2 + 14, cy + 31, title_, size=14, color=col, bold=True))
        f.append(mtext(x + cw / 2, cy + 70, lines, size=12, color=INK))
        if i < 2:
            ax = x + cw + gap / 2
            f.append(arrow(ax - 10, cy + ch / 2, ax + 10, cy + ch / 2, color=MUTED, sw=2.4))

    f.append(text(W / 2, 268, "Дві невідомі (V_a, V_b) — два рівняння: баланс суперузла + обмеження джерела",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "recipe.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_cut()
    fig_recipe()
    print("OK: 3 фігури у", IMG)
