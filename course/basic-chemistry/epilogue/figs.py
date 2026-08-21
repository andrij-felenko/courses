# -*- coding: utf-8 -*-
"""Фігури до теми «Куди далі» (book/chemistry/biochemistry/epilogue)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: карта дверей ──────────────────────────────────────────────────
def fig_doors():
    W, H = 940, 540
    frags = []

    doors = [
        ("Чому на поличці саме 2, потім 8?", "квантова й комп'ютерна хімія"),
        ("Яка молекула на вигляд?", "органічний синтез, фармація"),
        ("Чому реакція взагалі йде?", "термодинаміка"),
        ("Що всередині ядра?", "радіохімія"),
        ("Як молекули складаються в живе?", "біохімія, молекулярна біологія"),
    ]

    bx, bw, bh, gap = 450, 450, 74, 22
    y0 = 42
    centers = []
    for i, (q, field) in enumerate(doors):
        y = y0 + i * (bh + gap)
        cy = y + bh / 2
        centers.append(cy)
        frags.append(rect(bx, y, bw, bh))
        frags.append(text(bx + bw / 2, cy - 4, q, size=16, bold=True))
        frags.append(text(bx + bw / 2, cy + 21, field, size=13, color=MUTED))

    # ліва рамка «звідки»
    mid = (centers[0] + centers[-1]) / 2
    body, lw, lh = textbox(160, mid, "Те, що ти вже\nрозумієш", size=17,
                           bold=True, min_w=250, fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(body)

    x_start = 160 + lw / 2 + 12
    for cy in centers:
        frags.append(arrow(x_start, mid, bx - 10, cy, color=MUTED))

    render(os.path.join(IMG, 'doors.svg'), W, H, *frags)


# ── Фігура 2: дзеркальні молекули ───────────────────────────────────────────
def fig_mirror():
    W, H = 820, 400
    AX = W / 2.0          # вісь дзеркала
    cy = 200
    frags = []

    # дзеркало
    frags.append(line(AX, 62, AX, 330, color=MUTED, sw=2, dash="7,6"))
    frags.append(text(AX, 48, "дзеркало", size=13, color=MUTED))

    groups = [
        ((0, -95), "А", "#fdecea", POS),
        ((-88, 8), "Б", "#eaf0fd", NEG),
        ((-30, 88), "В", "#e8f7ee", FIELD),
        ((85, 55), "Г", "#f2f2f2", MUTED),
    ]

    def molecule(cx, flip):
        out = []
        rc, rs = 27, 23
        # спершу зв'язки — вони обриваються на межах кружків, тож літер не чіпають
        for (dx, dy), lab, fill, stroke in groups:
            ddx = -dx if flip else dx
            d = math.hypot(ddx, dy)
            ux, uy = ddx / d, dy / d
            out.append(line(cx + ux * (rc + 2), cy + uy * (rc + 2),
                            cx + ddx - ux * (rs + 2), cy + dy - uy * (rs + 2), sw=2))
        out.append(circle(cx, cy, rc, fill="#ffffff", stroke=INK, sw=2))
        out.append(text(cx, cy + 7, "C", size=20, bold=True))
        for (dx, dy), lab, fill, stroke in groups:
            ddx = -dx if flip else dx
            out.append(circle(cx + ddx, cy + dy, rs, fill=fill, stroke=stroke, sw=2))
            out.append(text(cx + ddx, cy + dy + 6, lab, size=16, bold=True, color=stroke))
        return out

    frags += molecule(AX - 185, False)
    frags += molecule(AX + 185, True)

    frags.append(text(AX - 185, 355, "пахне м'ятою", size=15, bold=True))
    frags.append(text(AX + 185, 355, "пахне кмином", size=15, bold=True))

    render(os.path.join(IMG, 'mirror-molecules.svg'), W, H, *frags)


# ── Фігура 3 (до вставки hist-molecule-shape): дослід Пастера ───────────────
def _poly(pts, fill, stroke, sw=2.0):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, fill, stroke, sw))


def _crystal(cx, cy, hand):
    """Кристалик зі скошеним ріжком: hand=+1 — скіс праворуч, -1 — ліворуч."""
    w, h = 14.0, 21.0
    s = float(hand)
    fill, stroke = ("#fdecea", POS) if hand > 0 else ("#eaf0fd", NEG)
    pts = [
        (cx - s * w, cy - h),
        (cx + s * w * 0.30, cy - h),
        (cx + s * w, cy - h * 0.45),
        (cx + s * w, cy + h),
        (cx - s * w, cy + h),
    ]
    return _poly(pts, fill, stroke)


def _arcarrow(cx, cy, r, a0, a1, color):
    def pt(a):
        rad = math.radians(a)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)
    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    sweep = 1 if a1 > a0 else 0
    return ('<path d="M%.1f %.1f A%.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
            % (x0, y0, r, r, sweep, x1, y1, color))


def _rotator(cx, cy, tilt, color):
    """Кружок-поляриметр: пунктир — початкова площина, суцільна — повернута."""
    out = [circle(cx, cy, 34, fill="#ffffff", stroke=MUTED, sw=1.5)]
    out.append(line(cx, cy - 30, cx, cy + 30, color=MUTED, sw=1.5, dash="5,5"))
    a_top = math.radians(-90 + tilt)
    out.append(line(cx + 30 * math.cos(a_top), cy + 30 * math.sin(a_top),
                    cx - 30 * math.cos(a_top), cy - 30 * math.sin(a_top),
                    color=color, sw=3))
    out.append(_arcarrow(cx, cy, 19, -90, -90 + tilt, color))
    return out


def fig_pasteur():
    W, H = 900, 545
    frags = []

    # ── верх: одна купка ─────────────────────────────────────────────────
    frags.append(text(450, 44, "Кристали солі виноградної кислоти — одна купка",
                      size=16, bold=True))
    frags.append(rect(250, 68, 400, 118))
    mixed = [(340, 108, +1), (450, 108, -1), (560, 108, +1),
             (340, 156, -1), (450, 156, +1), (560, 156, -1)]
    for cx, cy, hand in mixed:
        frags.append(_crystal(cx, cy, hand))
    frags.append(mtext(130, 120, "склад атомів\nу всіх однаковий", size=13, color=MUTED))
    frags.append(mtext(775, 120, "розчин купки\nсвітла не повертає", size=13, color=MUTED))

    # ── розділення ───────────────────────────────────────────────────────
    frags.append(line(450, 190, 450, 208, color=MUTED, sw=2))
    body, bw, bh = textbox(450, 228, "Пастер розбирає їх пінцетом під мікроскопом",
                           size=15, fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(body)
    frags.append(arrow(450, 248, 262, 288, color=MUTED))
    frags.append(arrow(450, 248, 638, 288, color=MUTED))

    # ── дві купки + поляриметри ──────────────────────────────────────────
    for px, hand, tilt, color, lab_top, lab_bot in (
        (225, -1, -32, NEG, "скіс ліворуч у всіх", "повертає світло ліворуч"),
        (675, +1, +32, POS, "скіс праворуч у всіх", "повертає світло праворуч"),
    ):
        frags.append(rect(px - 170, 296, 340, 86))
        for dx in (-80, 0, 80):
            frags.append(_crystal(px + dx, 339, hand))
        frags.append(text(px, 404, lab_top, size=14, color=MUTED))
        frags += _rotator(px, 456, tilt, color)
        frags.append(text(px, 522, lab_bot, size=15, bold=True, color=color))

    render(os.path.join(IMG, 'pasteur-tweezers.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_doors()
    fig_mirror()
    fig_pasteur()
    print("ok")
