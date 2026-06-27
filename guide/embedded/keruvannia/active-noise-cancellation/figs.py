# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def wave(x0, y0, w, amp, cycles, phase=0.0, color=INK, sw=2.0, n=160):
    """Полілінія синусоїди в межах [x0, x0+w] навколо осі y0."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── Фігура 1: принцип — анти-шум і сума ────────────────────────────────────
def fig_principle():
    W, H = 700, 430
    parts = []
    cx = W / 2
    colx, colw = 70, W - 140

    # шум
    y1 = 90
    parts.append(text(colx, y1 - 42, "шум (те, що чуємо)", size=14, color=POS, anchor="start", bold=True))
    parts.append(line(colx, y1, colx + colw, y1, color=MUTED, sw=1, dash="3,4"))
    parts.append(wave(colx, y1, colw, 32, 3, 0.0, color=POS, sw=2.4))

    # анти-шум
    y2 = 210
    parts.append(text(colx, y2 - 42, "анти-шум (дзеркало, фаза + 180°)", size=14, color=NEG, anchor="start", bold=True))
    parts.append(line(colx, y2, colx + colw, y2, color=MUTED, sw=1, dash="3,4"))
    parts.append(wave(colx, y2, colw, 32, 3, math.pi, color=NEG, sw=2.4))

    # сума = тиша
    y3 = 340
    parts.append(text(colx, y3 - 42, "сума на вусі = тиша", size=14, color=FIELD, anchor="start", bold=True))
    parts.append(line(colx, y3, colx + colw, y3, color=FIELD, sw=2))
    # майже пряма (залишок)
    pts = []
    for i in range(161):
        t = i / 160
        x = colx + t * colw
        y = y3 - 1.5 * math.sin(2 * math.pi * 3 * t)  # дрібний залишок
        pts.append("%.1f,%.1f" % (x, y))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), FIELD))

    parts.append(text(cx, H - 14,
                      "однакова амплітуда + протилежна фаза → хвилі знищують одна одну (суперпозиція)",
                      size=13, color=MUTED))
    render(os.path.join(OUT, "principle.svg"), W, H, *parts,
           title="Гасіння — це додавання дзеркальної хвилі")


# ── Фігура 2: дві топології — feedforward і feedback ───────────────────────
def fig_topologies():
    W, H = 740, 470
    parts = []

    def block(cx, cy, s, w=0, color=LINE, fill=FILL, tcolor=INK):
        b, bw, bh = textbox(cx, cy, s, size=13, pad=10, stroke=color, fill=fill, color=tcolor, min_w=w)
        parts.append(b)
        return bw, bh

    # — верх: feedforward —
    parts.append(text(W / 2, 50, "Feedforward: окремий мікрофон ловить шум ПЕРЕД вухом", size=14, bold=True, color=NEG))
    ya = 110
    block(95, ya, "опорний\nмікрофон", color=NEG)
    parts.append(arrow(150, ya, 215, ya, color=NEG))
    bw, _ = block(280, ya, "адаптивний\nфільтр W", color=NEG)
    parts.append(arrow(345, ya, 410, ya, color=NEG))
    block(470, ya, "динамік\n(анти-шум)", color=NEG)
    parts.append(arrow(530, ya, 600, ya, color=FIELD))
    block(655, ya, "вухо\n(тиша)", color=FIELD, fill="#eafaf0")
    # мікрофон помилки трохи нижче вуха
    block(655, ya + 82, "мікрофон\nпомилки", color=MUTED)
    parts.append(arrow(655, ya + 27, 655, ya + 55, color=MUTED))  # вухо -> err mic
    parts.append('<path d="M613 %.0f Q 340 %.0f 280 %.0f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
                 % (ya + 82, ya + 150, ya + 30, MUTED))
    parts.append(text(355, ya + 138, "сигнал помилки підправляє коефіцієнти W", size=12, color=MUTED))

    # роздільник
    parts.append(line(40, 270, W - 40, 270, color=MUTED, sw=1, dash="2,5"))

    # — низ: feedback —
    parts.append(text(W / 2, 312, "Feedback: лише мікрофон помилки біля вуха — фільтр сам передбачає", size=14, bold=True, color=POS))
    yb = 380
    block(140, yb, "мікрофон помилки\n(біля вуха)", color=POS)
    parts.append(arrow(235, yb, 320, yb, color=POS))
    block(390, yb, "фільтр-предиктор", color=POS)
    parts.append(arrow(470, yb, 545, yb, color=POS))
    block(610, yb, "динамік\n(анти-шум)", color=POS)
    # петля назад до вуха/мікрофона
    parts.append('<path d="M610 %.0f Q 610 %.0f 235 %.0f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
                 % (yb + 28, yb + 70, yb + 16, POS))
    render(os.path.join(OUT, "topologies.svg"), W, H, *parts,
           title="Дві схеми ANC: де стоїть мікрофон")


# ── Фігура 3: адаптивний контур FxLMS — як фільтр учиться ──────────────────
def fig_fxlms():
    W, H = 720, 420
    parts = []

    def block(cx, cy, s, w=0, color=LINE, fill=FILL, tcolor=INK, size=13):
        b, bw, bh = textbox(cx, cy, s, size=size, pad=10, stroke=color, fill=fill, color=tcolor, min_w=w)
        parts.append(b)
        return bw, bh

    yr = 110
    # опорний шум x[n]
    block(85, yr, "опорний\nшум x[n]", color=NEG)
    parts.append(arrow(140, yr, 215, yr, color=NEG))
    block(280, yr, "фільтр W\n(те, що вчимо)", color=NEG)
    parts.append(arrow(348, yr, 430, yr, color=NEG))
    # вторинний шлях
    bw, _ = block(495, yr, "вторинний шлях S\n(динамік+повітря)", color=MUTED, fill="#eef0f2")
    parts.append(arrow(575, yr, 640, yr, color=NEG))

    # суматор справа
    sx, sy = 665, 210
    parts.append(circle(sx, sy, 16, fill="#fff", stroke=INK, sw=2))
    parts.append(text(sx, sy + 5, "Σ", size=18, bold=True))
    parts.append('<path d="M640 %.0f Q 665 %.0f 665 %.0f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (yr, yr + 40, sy - 16, NEG))
    parts.append(text(648, yr + 12, "анти-шум", size=11, color=NEG, anchor="end"))

    # справжній шум (первинний шлях) згори в суматор
    block(665, 60, "первинний шум\n(акустика)", color=POS, fill="#fdecea")
    parts.append(arrow(665, 88, 665, sy - 16, color=POS))

    # помилка e[n] вниз
    parts.append(arrow(sx, sy + 16, sx, 300, color=FIELD))
    block(665, 330, "помилка e[n]\n(мікрофон)", color=FIELD, fill="#eafaf0")

    # LMS-оновлення
    lx, ly = 270, 330
    bw_u, _ = block(lx, ly, "оновлення коефіцієнтів\nW += μ · e · x′", color=FIELD, fill="#eafaf0")
    # помилка e[n] -> оновлення (від лівого краю блоку помилки до правого краю блоку оновлення)
    parts.append('<path d="M610 %.0f Q 460 %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
                 % (ly, ly + 42, lx + bw_u / 2 + 4, ly, FIELD))
    # оновлення -> фільтр W (угору)
    parts.append(arrow(lx, ly - 26, 270, yr + 26, color=FIELD))
    parts.append(text(lx, ly + 48, "x′ = опорний крізь копію S", size=11, color=MUTED))
    render(os.path.join(OUT, "fxlms.svg"), W, H, *parts,
           title="Адаптивний контур: фільтр учиться на власній помилці")


# ── Фігура 4: три рубежі захисту FxLMS від розгойдування ────────────────────
def fig_safeguards():
    W, H = 720, 470
    parts = []

    parts.append(text(W / 2, 52, "Три рубежі проти розгойдування — кожен на своїй шкалі часу",
                      size=14, bold=True, color=INK))

    # три горизонтальні смуги: leakage, клампінг, вотчдог
    rows = [
        (110, FIELD, "Leakage (щотакту)",
         "слабка тяга коефіцієнтів до 0 — не дає дрейфувати в тиші", "ЗАПОБІГАЄ"),
        (235, NEG, "Клампінг (щотакту)",
         "жорстка стеля: значення за діапазоном тиснеться до краю, а не у тріск", "ЛОКАЛІЗУЄ"),
        (360, POS, "Вотчдог (десятки мс)",
         "стало росте e[n] → скид фільтра + перевимір моделі S", "РЯТУЄ"),
    ]
    lx, lw = 60, W - 280
    for cy, col, name, desc, tag in rows:
        parts.append(rect(lx, cy - 38, lw, 76, fill=FILL, stroke=col, sw=2))
        parts.append(text(lx + 16, cy - 12, name, size=14, bold=True, color=col, anchor="start"))
        parts.append(text(lx + 16, cy + 14, desc, size=12, color=MUTED, anchor="start"))
        # ярлик-роль праворуч
        bx = lx + lw + 24
        b, bw, bh = textbox(bx + 70, cy, tag, size=13, pad=10, stroke=col, fill="#fff",
                            color=col, bold=True, min_w=130)
        parts.append(b)

    # вісь часу під трьома смугами
    ay = 420
    parts.append(arrow(60, ay, W - 60, ay, color=MUTED))
    parts.append(text(70, ay + 22, "швидко (на відлік)", size=12, color=MUTED, anchor="start"))
    parts.append(text(W - 70, ay + 22, "повільно (десятки мс)", size=12, color=MUTED, anchor="end"))
    parts.append(text(W / 2, ay - 10,
                      "запобігти  →  локалізувати  →  впіймати й відкотити",
                      size=12, color=INK))
    render(os.path.join(OUT, "safeguards.svg"), W, H, *parts,
           title="Захист FxLMS: три шари, три шкали часу")


if __name__ == "__main__":
    fig_principle()
    fig_topologies()
    fig_fxlms()
    fig_safeguards()
    print("ok: principle.svg, topologies.svg, fxlms.svg, safeguards.svg")
