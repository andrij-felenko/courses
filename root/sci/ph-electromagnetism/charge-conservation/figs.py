# -*- coding: utf-8 -*-
"""Фігури до теми «Закон збереження заряду».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі spільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: межа-бухгалтерія ──────────────────────────────────────────────
# Три сцени всередині однієї ізольованої межі; у кожній сума «до» = сума «після».
def fig_ledger():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # зовнішня межа «ізольована система»
    f.append(rect(16, 44, W - 32, H - 60, fill="#fcfdff", stroke=FIELD, sw=2.2, rx=14))
    f.append(text(W / 2, 32, "Ізольована межа: крізь неї заряд не проходить", size=15, bold=True))
    f.append(text(W / 2, H - 8, "у кожній сцені:  сума ДО  =  сума ПІСЛЯ", size=13, color=MUTED))

    # три колонки-сцени
    col_w = (W - 32 - 4 * 16) / 3          # ширина однієї сцени
    x0 = 16 + 16
    titles = ["розділення тертям", "нейтралізація", "народження пари"]
    sums = ["0  →  (+N·e) + (−N·e) = 0",
            "(+Q) + (−Q) = 0  →  0",
            "0  →  (−e) + (+e) = 0"]
    cols_x = []
    for i in range(3):
        cx = x0 + i * (col_w + 16) + col_w / 2
        cols_x.append(cx)
        # роздільники між сценами
        if i > 0:
            sep = x0 + i * (col_w + 16) - 8
            f.append(line(sep, 60, sep, H - 70, color="#d6dde6", sw=1.2, dash="4,5"))
        f.append(text(cx, 66, titles[i], size=13, bold=True, color=INK))

    cy_top, cy_bot = 110, 168     # рядки «до» і «після»
    # позначки рядів
    f.append(text(x0 - 4, cy_top + 4, "до", size=11, color=MUTED, anchor="start"))
    f.append(text(x0 - 4, cy_bot + 4, "після", size=11, color=MUTED, anchor="start"))

    # сцена 1: тертя — два нейтральні тіла → + і −
    c = cols_x[0]
    f.append(plus(c - 26, cy_top, 8)); f.append(minus(c - 8, cy_top, 8))
    f.append(plus(c + 8, cy_top, 8)); f.append(minus(c + 26, cy_top, 8))
    f.append(plus(c - 26, cy_bot, 8)); f.append(plus(c - 8, cy_bot, 8))
    f.append(minus(c + 8, cy_bot, 8)); f.append(minus(c + 26, cy_bot, 8))

    # сцена 2: нейтралізація — (+ і −) розведені → перемішані (нейтрально)
    c = cols_x[1]
    f.append(plus(c - 24, cy_top, 8)); f.append(plus(c - 6, cy_top, 8))
    f.append(minus(c + 12, cy_top, 8)); f.append(minus(c + 30, cy_top, 8))
    f.append(plus(c - 24, cy_bot, 8)); f.append(minus(c - 6, cy_bot, 8))
    f.append(plus(c + 12, cy_bot, 8)); f.append(minus(c + 30, cy_bot, 8))

    # сцена 3: народження пари — фотон (хвиля) → e⁻ та e⁺
    c = cols_x[2]
    f.append(text(c, cy_top + 5, "γ", size=22, bold=True, color=MUTED))
    f.append(text(c, cy_top + 22, "(заряд 0)", size=10, color=MUTED))
    f.append(minus(c - 14, cy_bot, 8)); f.append(plus(c + 14, cy_bot, 8))

    # стрілки «до → після» в кожній сцені
    for c in cols_x:
        f.append(arrow(c, cy_top + 30, c, cy_bot - 16, color=LINE, sw=1.6))

    # рядок суми під кожною сценою
    for i, c in enumerate(cols_x):
        body, w, h = textbox(c, 232, sums[i], size=11, pad=7, fill="#eef6ef",
                             stroke=FIELD, sw=1.2)
        f.append(body)

    return render(os.path.join(IMG, "conservation-ledger.svg"), W, H, *f)


# ── Фігура 2: тертя розділяє, а не творить ──────────────────────────────────
def fig_friction():
    W, H = 700, 300
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Тертя переганяє електрони — заряду не додає", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 56, midx, H - 26, color="#d6dde6", sw=1.4, dash="5,6"))
    f.append(text(midx / 2, 52, "ДО натирання", size=13, bold=True, color=MUTED))
    f.append(text(midx + midx / 2, 52, "ПІСЛЯ натирання", size=13, bold=True, color=MUTED))

    bw, bh = 120, 90
    yb = 84

    def body(cx, label, charge_label, charge_color, pluses, minuses):
        # «+» — верхній ряд, «−» — нижній ряд (до 4 у ряду)
        out = rect(cx - bw / 2, yb, bw, bh, fill=FILL, stroke=LINE, sw=1.6)
        out += text(cx, yb - 8, label, size=12, color=INK)
        xs = [cx - 30, cx - 10, cx + 10, cx + 30]
        for k in range(pluses):
            out += plus(xs[k], yb + 28, 8)
        for k in range(minuses):
            out += minus(xs[k], yb + 54, 8)
        out += text(cx, yb + bh + 18, charge_label, size=13, bold=True, color=charge_color)
        return out

    # ДО: обидва нейтральні (по 3 «+» і 3 «−»)
    cxL1, cxL2 = midx / 2 - 78, midx / 2 + 78
    f.append(body(cxL1, "бурштин", "сумарно 0", MUTED, 3, 3))
    f.append(body(cxL2, "шерсть", "сумарно 0", MUTED, 3, 3))

    # ПІСЛЯ: бурштин −N·e, шерсть +N·e
    cxR1, cxR2 = midx + midx / 2 - 78, midx + midx / 2 + 78
    # бурштин: 3 «+» і 5 «−» (прихопив 2 електрони)
    f.append(rect(cxR1 - bw / 2, yb, bw, bh, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(cxR1, yb - 8, "бурштин", size=12))
    for k, x in enumerate([cxR1 - 30, cxR1 - 10, cxR1 + 10]):
        f.append(plus(x, yb + 28, 8))
    for k, x in enumerate([cxR1 - 30, cxR1 - 10, cxR1 + 10, cxR1 + 30]):
        f.append(minus(x, yb + 54, 8))
    f.append(minus(cxR1 + 30, yb + 28, 8))
    f.append(text(cxR1, yb + bh + 18, "−2e", size=14, bold=True, color=NEG))

    # шерсть: 3 «+» і 1 «−» (віддала 2 електрони)
    f.append(rect(cxR2 - bw / 2, yb, bw, bh, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(cxR2, yb - 8, "шерсть", size=12))
    for k, x in enumerate([cxR2 - 30, cxR2 - 10, cxR2 + 10]):
        f.append(plus(x, yb + 28, 8))
    f.append(minus(cxR2 - 30, yb + 54, 8))
    f.append(text(cxR2, yb + bh + 18, "+2e", size=14, bold=True, color=POS))

    # стрілка переходу електронів між тілами «після»
    f.append(arrow(cxR2 - bw / 2 - 2, yb + bh / 2, cxR1 + bw / 2 + 2, yb + bh / 2,
                   color=NEG, sw=2.0))
    f.append(text((cxR1 + cxR2) / 2, yb + bh / 2 - 8, "2 e⁻", size=12, bold=True, color=NEG))

    # підсумкові рамки сум
    bL, wL, hL = textbox(midx / 2, H - 14, "сума:  0 + 0 = 0", size=12, pad=6,
                         fill="#eef6ef", stroke=FIELD, sw=1.2)
    f.append(bL)
    bR, wR, hR = textbox(midx + midx / 2, H - 14, "сума:  (−2e) + (+2e) = 0", size=12,
                         pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2)
    f.append(bR)
    return render(os.path.join(IMG, "friction-not-creation.svg"), W, H, *f)


# ── Фігура 3: баланс у вузлі ────────────────────────────────────────────────
def fig_node():
    W, H = 640, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Вузол: що втекло — те й витекло", size=16, bold=True))

    nx, ny = W / 2, H / 2 + 6      # сам вузол
    f.append(circle(nx, ny, 9, fill=INK, stroke=INK, sw=1))

    # дві втічні гілки (зліва) і дві витічні (справа)
    # втічні
    f.append(arrow(70, ny - 70, nx - 9, ny - 9, color=POS, sw=2.2))
    f.append(arrow(70, ny + 70, nx - 9, ny + 9, color=POS, sw=2.2))
    # витічні
    f.append(arrow(nx + 9, ny - 9, W - 70, ny - 70, color=NEG, sw=2.2))
    f.append(arrow(nx + 9, ny + 9, W - 70, ny + 70, color=NEG, sw=2.2))

    # підписи струмів
    f.append(text(90, ny - 80, "I₁", size=15, bold=True, color=POS, anchor="start"))
    f.append(text(90, ny + 92, "I₂", size=15, bold=True, color=POS, anchor="start"))
    f.append(text(W - 90, ny - 80, "I₃", size=15, bold=True, color=NEG, anchor="end"))
    f.append(text(W - 90, ny + 92, "I₄", size=15, bold=True, color=NEG, anchor="end"))

    f.append(text(120, ny + 4, "втікає", size=12, color=POS, anchor="middle"))
    f.append(text(W - 120, ny + 4, "витікає", size=12, color=NEG, anchor="middle"))

    # рівняння балансу
    b, w, h = textbox(nx, H - 26, "I₁ + I₂ = I₃ + I₄", size=15, pad=9,
                      fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    f.append(text(nx, 52, "заряд у вузлі не накопичується й не зникає", size=12, color=MUTED))
    return render(os.path.join(IMG, "continuity-node.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_ledger()
    p2 = fig_friction()
    p3 = fig_node()
    print("written:")
    for p in (p1, p2, p3):
        print("  ", p)
