# -*- coding: utf-8 -*-
"""Фігури до теми «RS-485».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── 1. Чому диференційність б'є завади: спільна перешкода віднімається ────────
def fig_why_differential():
    W, H = 760, 470
    f = [text(W / 2, 28, "Диференційний приймач віднімає лінії — і завада, спільна для обох, зникає",
              size=15, bold=True)]

    ox = 90
    base_a = 130   # вісь лінії A
    base_b = 250   # вісь лінії B
    amp = 26
    span = 470

    def sig(base, color, invert, label):
        # корисний сигнал: меандр (інвертований для B) + однакова синусоїдна завада
        pts = []
        for i in range(0, 241):
            t = i / 240.0
            sq = 1.0 if (int(t * 4) % 2 == 0) else -1.0
            if invert:
                sq = -sq
            noise = 0.55 * math.sin(t * 9.0 + 0.6)   # СПІЛЬНА завада, однакова на A і B
            y = base - (sq * 0.7 + noise) * amp
            pts.append("%.1f,%.1f" % (ox + t * span, y))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), color))
        f.append(text(ox - 14, base + 4, label, size=12, bold=True, color=color, anchor="end"))

    sig(base_a, POS, False, "A")
    sig(base_b, NEG, True, "B")
    f.append(text(ox + span + 8, base_a - 30, "наведена завада", size=10, color=MUTED, anchor="start"))
    f.append(text(ox + span + 8, base_a - 14, "сидить на ОБОХ", size=10, color=MUTED, anchor="start"))

    # роздільник
    f.append(line(40, 312, W - 40, 312, color="#d6dde6", sw=1.2, dash="5,5"))

    # різниця A − B: завада скоротилась, корисний сигнал подвоївся
    base_d = 392
    f.append(text(ox - 14, base_d + 4, "A−B", size=12, bold=True, color=FIELD, anchor="end"))
    pts = []
    for i in range(0, 241):
        t = i / 240.0
        sq = 1.0 if (int(t * 4) % 2 == 0) else -1.0
        # A несе +sq, B несе −sq; завада однакова → у різниці пропадає
        diff = (sq * 0.7 + 0) - (-sq * 0.7 + 0)
        y = base_d - diff * amp * 0.85
        pts.append("%.1f,%.1f" % (ox + t * span, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), FIELD))
    f.append(line(ox, base_d, ox + span, base_d, color=MUTED, sw=1.0, dash="3,3"))

    b, _, _ = textbox(W / 2, 448,
                      "приймач читає лише різницю A−B → спільна завада віднімається, біти стоять чисто",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "why-differential.svg"), W, H, *f)


# ── 2. Багатоточкова шина: одна вита пара, багато вузлів, термінатори на кінцях ─
def fig_multidrop():
    W, H = 780, 420
    f = [text(W / 2, 28, "RS-485: одна вита пара тягнеться повз усі вузли; термінатори — лише на двох кінцях",
              size=14.5, bold=True)]

    yA, yB = 120, 168          # дві лінії пари
    x0, x1 = 70, W - 70
    # сама пара
    f.append(line(x0, yA, x1, yA, color=POS, sw=2.6))
    f.append(line(x0, yB, x1, yB, color=NEG, sw=2.6))
    f.append(text(x0 - 8, yA + 4, "A", size=12, bold=True, color=POS, anchor="end"))
    f.append(text(x0 - 8, yB + 4, "B", size=12, bold=True, color=NEG, anchor="end"))

    # термінатори RT на обох кінцях (між A і B)
    for tx, side in ((x0, "ліво"), (x1, "право")):
        f.append(rect(tx - 10, yA + 8, 20, yB - yA - 16, fill=BG, stroke=FIELD, sw=1.8, rx=3))
        lab_x = tx + (16 if side == "ліво" else -16)
        anc = "start" if side == "ліво" else "end"
        f.append(text(lab_x, (yA + yB) / 2 - 2, "RT", size=10.5, bold=True, color=FIELD, anchor=anc))
        f.append(text(lab_x, (yA + yB) / 2 + 13, "120 Ω", size=9.5, color=MUTED, anchor=anc))

    # вузли-відгалуження
    nodes = [
        (170, "Ведучий", "MCU", POS),
        (330, "Вузол", "давач", INK),
        (490, "Вузол", "привід", INK),
        (640, "Вузол", "панель", INK),
    ]
    for nx, top, sub, col in nodes:
        # коротке відгалуження вниз
        f.append(line(nx, yA, nx, 250, color=MUTED, sw=1.4))
        f.append(line(nx + 10, yB, nx + 10, 250, color=MUTED, sw=1.4))
        f.append(circle(nx, yA, 3, fill=POS, stroke=POS))
        f.append(circle(nx + 10, yB, 3, fill=NEG, stroke=NEG))
        f.append(rect(nx - 42, 250, 96, 56, fill=FILL, stroke=col, sw=1.8, rx=8))
        f.append(text(nx + 6, 272, top, size=11.5, bold=True, color=INK))
        f.append(text(nx + 6, 290, sub, size=10, color=MUTED))

    f.append(text(W / 2, 340, "до 32 стандартних навантажень на одній парі; усі чують усіх",
                  size=11.5, color=INK))
    b, _, _ = textbox(W / 2, 388,
                      "коротке відгалуження — добре; довгий «відросток» псує лінію й дає відбиття",
                      size=11, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "multidrop.svg"), W, H, *f)


# ── 3. Термінація: без RT хвиля відбивається від кінця й калічить біт ─────────
def fig_termination():
    W, H = 760, 410
    f = [text(W / 2, 26, "Термінатор гасить хвилю на кінці; без нього відбиття накладається на сигнал",
              size=14.5, bold=True)]

    cw = 330
    lx, rx = 60, W - 60 - cw
    topY = 56

    # ── ліворуч: без термінатора (відбиття, дзвін) ──
    f.append(rect(lx, topY, cw, 300, fill="#fbeee6", stroke=POS, sw=1.8, rx=10))
    f.append(text(lx + cw / 2, topY + 24, "Кінець розімкнений (немає RT)", size=12.5, bold=True, color=POS))
    # лінія з відкритим кінцем
    ly = topY + 70
    f.append(line(lx + 26, ly, lx + cw - 60, ly, color=INK, sw=2.4))
    f.append(circle(lx + cw - 60, ly, 4, fill=BG, stroke=POS, sw=2))   # розрив
    f.append(text(lx + cw - 50, ly + 4, "обрив", size=9.5, color=POS, anchor="start"))
    f.append(arrow(lx + 40, ly - 16, lx + cw - 90, ly - 16, color=NEG, sw=1.8))
    f.append(text(lx + cw / 2 - 18, ly - 22, "хвиля йде →", size=9.5, color=NEG))
    f.append(arrow(lx + cw - 90, ly + 18, lx + 40, ly + 18, color=POS, sw=1.8))
    f.append(text(lx + cw / 2 - 10, ly + 32, "← відбита назад", size=9.5, color=POS))
    # форма прийнятого сигналу: меандр зі дзвоном
    sy = topY + 200
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        sq = 1.0 if t > 0.18 else 0.0
        ring = 0.35 * math.exp(-(t - 0.18) * 8) * math.sin((t - 0.18) * 60) if t > 0.18 else 0
        y = sy - (sq + ring) * 34
        pts.append("%.1f,%.1f" % (lx + 26 + t * (cw - 52), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), POS))
    f.append(text(lx + cw / 2, topY + 270, "дзвін і сходинки → хибні біти", size=10.5, color=POS, italic=True))

    # ── праворуч: з термінатором (чистий фронт) ──
    f.append(rect(rx, topY, cw, 300, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + cw / 2, topY + 24, "Кінець на RT = опору лінії", size=12.5, bold=True, color=FIELD))
    ry = topY + 70
    f.append(line(rx + 26, ry, rx + cw - 60, ry, color=INK, sw=2.4))
    f.append(rect(rx + cw - 62, ry - 16, 16, 32, fill=BG, stroke=FIELD, sw=2, rx=3))
    f.append(text(rx + cw - 40, ry + 4, "RT", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(rx + 40, ry - 26, rx + cw - 80, ry - 26, color=NEG, sw=1.8))
    f.append(text(rx + cw / 2 - 18, ry - 32, "хвиля гасне в RT", size=9.5, color=FIELD))
    # чистий меандр
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        sq = 1.0 if t > 0.18 else 0.0
        y = (topY + 200) - sq * 34
        pts.append("%.1f,%.1f" % (rx + 26 + t * (cw - 52), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), FIELD))
    f.append(text(rx + cw / 2, topY + 270, "чистий фронт → біт читається певно", size=10.5, color=FIELD, italic=True))

    b, _, _ = textbox(W / 2, 392,
                      "RT ≈ хвильовому опору пари (≈120 Ω) → енергія хвилі поглинається, а не вертається",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "termination.svg"), W, H, *f)


# ── 4. Напівдуплекс: лінія DE перемикає трансивер між «говорити» і «слухати» ──
def fig_half_duplex():
    W, H = 760, 430
    f = [text(W / 2, 26, "Одна пара працює по черзі: сигнал DE віддає лінію передавачу або приймачу",
              size=14.5, bold=True)]

    # центр — трансивер з трьома виводами до MCU і парою A/B назовні
    tx, ty, tw, th = W / 2 - 70, 80, 140, 150
    f.append(rect(tx, ty, tw, th, fill=FILL, stroke=INK, sw=2, rx=10))
    f.append(text(tx + tw / 2, ty + 24, "Трансивер", size=12.5, bold=True, color=INK))
    f.append(text(tx + tw / 2, ty + 40, "RS-485", size=10, color=MUTED))
    # драйвер (трикутник назовні) і приймач (трикутник усередину)
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (tx + 30, ty + 70, tx + 30, ty + 110, tx + 64, ty + 90, POS))
    f.append(text(tx + 40, ty + 94, "D", size=11, bold=True, color=POS))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#eaf0fd" stroke="%s" stroke-width="1.6"/>'
             % (tx + tw - 30, ty + 70, tx + tw - 30, ty + 110, tx + tw - 64, ty + 90, NEG))
    f.append(text(tx + tw - 40, ty + 94, "R", size=11, bold=True, color=NEG))

    # виводи до MCU зліва
    mcx = 120
    f.append(rect(mcx - 50, ty + 40, 70, 70, fill="#eef2f8", stroke=NEG, sw=1.6, rx=8))
    f.append(text(mcx - 15, ty + 70, "MCU", size=11, bold=True, color=INK))
    f.append(text(mcx - 15, ty + 88, "UART", size=9.5, color=MUTED))
    f.append(line(mcx + 20, ty + 60, tx + 30, ty + 78, color=POS, sw=1.8))
    f.append(text((mcx + 20 + tx) / 2, ty + 56, "TX→D", size=9, color=POS))
    f.append(line(mcx + 20, ty + 92, tx + tw - 64, ty + 90, color=NEG, sw=1.8))
    f.append(text((mcx + 20 + tx) / 2, ty + 104, "R→RX", size=9, color=NEG))
    # КЕРУВАННЯ напрямком — лінія DE
    f.append(line(mcx + 20, ty + 124, tx + 64, ty + 124, color=FIELD, sw=2.2))
    f.append(line(tx + 64, ty + 124, tx + 64, ty + 100, color=FIELD, sw=2.2))
    f.append(text((mcx + 20 + tx) / 2, ty + 138, "DE / RE", size=10, bold=True, color=FIELD))

    # пара A/B назовні справа
    f.append(line(tx + tw, ty + 78, tx + tw + 90, ty + 78, color=POS, sw=2.4))
    f.append(line(tx + tw, ty + 102, tx + tw + 90, ty + 102, color=NEG, sw=2.4))
    f.append(text(tx + tw + 96, ty + 82, "A", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(tx + tw + 96, ty + 106, "B", size=11, bold=True, color=NEG, anchor="start"))

    # роздільник
    f.append(line(40, 262, W - 40, 262, color="#d6dde6", sw=1.2, dash="5,5"))

    # два стани: DE=1 говоримо, DE=0 слухаємо
    cw = 320
    lx2, rx2 = 60, W - 60 - cw
    f.append(rect(lx2, 278, cw, 130, fill="#fbeee6", stroke=POS, sw=1.6, rx=8))
    f.append(text(lx2 + cw / 2, 300, "DE = 1 — передаємо", size=12, bold=True, color=POS))
    f.append(mtext(lx2 + 16, 326,
                   ["драйвер D під'єднаний до пари,", "MCU виштовхує біти TX у лінію,",
                    "приймач R вимкнений — себе не слухаємо"],
                   size=10.6, color=INK, anchor="start", lh=1.4))

    f.append(rect(rx2, 278, cw, 130, fill="#eef2f8", stroke=NEG, sw=1.6, rx=8))
    f.append(text(rx2 + cw / 2, 300, "DE = 0 — приймаємо", size=12, bold=True, color=NEG))
    f.append(mtext(rx2 + 16, 326,
                   ["драйвер D у третьому стані (відпущений),", "пара вільна для іншого вузла,",
                    "приймач R віддає почуте в RX"],
                   size=10.6, color=INK, anchor="start", lh=1.4))

    render(os.path.join(IMG, "half-duplex.svg"), W, H, *f)


# ── 5. Зміщувальні резистори: тримають «спокій» у відомому стані ──────────────
def fig_bias():
    W, H = 740, 400
    f = [text(W / 2, 26, "Коли всі мовчать, пару тримають у відомому «спокої» зміщувальні резистори",
              size=14.5, bold=True)]

    cw = 320
    lx, rx = 60, W - 60 - cw
    topY = 58

    # ── ліворуч: без зсуву — лінія плаває ──
    f.append(rect(lx, topY, cw, 280, fill="#fbeee6", stroke=POS, sw=1.8, rx=10))
    f.append(text(lx + cw / 2, topY + 24, "Без зсуву: ніхто не веде", size=12.5, bold=True, color=POS))
    yA, yB = topY + 80, topY + 120
    f.append(line(lx + 30, yA, lx + cw - 30, yA, color=POS, sw=2.2))
    f.append(line(lx + 30, yB, lx + cw - 30, yB, color=NEG, sw=2.2))
    f.append(text(lx + 18, yA + 4, "A", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(lx + 18, yB + 4, "B", size=11, bold=True, color=NEG, anchor="end"))
    # хитливий рівень різниці
    pts = []
    sy = topY + 200
    for i in range(0, 201):
        t = i / 200.0
        y = sy - (0.5 + 0.45 * math.sin(t * 22) * math.exp(-((t - 0.5) ** 2) * 1.5)) * 16
        pts.append("%.1f,%.1f" % (lx + 30 + t * (cw - 60), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), POS))
    f.append(line(lx + 30, sy - 8, lx + cw - 30, sy - 8, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(lx + cw / 2, topY + 248, "A−B біля нуля → шум кидає в «0»/«1»",
                  size=10.3, color=POS, italic=True))

    # ── праворуч: зі зсувом — гарантований «спокій» = лог. 1 ──
    f.append(rect(rx, topY, cw, 280, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + cw / 2, topY + 24, "Зі зсувом: спокій = тверда «1»", size=12.5, bold=True, color=FIELD))
    yA, yB = topY + 80, topY + 120
    f.append(line(rx + 30, yA, rx + cw - 30, yA, color=POS, sw=2.2))
    f.append(line(rx + 30, yB, rx + cw - 30, yB, color=NEG, sw=2.2))
    f.append(text(rx + 18, yA + 4, "A", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(rx + 18, yB + 4, "B", size=11, bold=True, color=NEG, anchor="end"))
    # резистор вгору від A (до Vcc) і вниз від B (до GND)
    f.append(line(rx + 60, yA, rx + 60, topY + 52, color=POS, sw=1.6))
    f.append(rect(rx + 50, topY + 38, 20, 14, fill=BG, stroke=POS, sw=1.4))
    f.append(text(rx + 76, topY + 49, "↑Vcc", size=9, color=POS, anchor="start"))
    f.append(line(rx + cw - 60, yB, rx + cw - 60, topY + 150, color=NEG, sw=1.6))
    f.append(rect(rx + cw - 70, topY + 136, 20, 14, fill=BG, stroke=NEG, sw=1.4))
    f.append(text(rx + cw - 76, topY + 147, "↓GND", size=9, color=NEG, anchor="end"))
    # стабільна різниця, чітко над порогом
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        y = sy - (0.85 + 0.02 * math.sin(t * 22)) * 16
        pts.append("%.1f,%.1f" % (rx + 30 + t * (cw - 60), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), FIELD))
    f.append(line(rx + 30, sy - 4, rx + cw - 30, sy - 4, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(rx + cw - 32, sy - 8, "поріг +200 мВ", size=9.5, color=MUTED, anchor="end"))
    f.append(text(rx + cw / 2, topY + 248, "A−B > +200 мВ → стабільна «1», шум не страшний",
                  size=10.3, color=FIELD, italic=True))

    b, _, _ = textbox(W / 2, 380,
                      "підтяжка A↑ та стяжка B↓ зміщують пару так, щоб «тиша» читалась як певна «1»",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bias.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_differential()
    fig_multidrop()
    fig_termination()
    fig_half_duplex()
    fig_bias()
    print("OK: 5 figures ->", IMG)
