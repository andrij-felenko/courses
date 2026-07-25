# -*- coding: utf-8 -*-
"""Фігури до вставок про масив пар Дарлінгтона (api-darlington-array.md, proj-darlington-array-relay.md).
Окремий генератор у теці теми (поряд із figs.py), щоб не зачіпати спільний figs.py.
Три фігури:
  array-channel.svg  — [api] що всередині ОДНОГО каналу: базовий R → Дарлінгтон → гасильний діод на COM
  array-pinout.svg   — [api] типова розпіновка: входи ліворуч, виходи дзеркально праворуч, COM, GND
  array-relay.svg    — [proj] «перший байт»: реле між +V і OUTn, COM на +V, діод гасить викид
Запуск:  python figs_array.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── спрощений значок NPN (як у figs.py, локальна копія для незалежності) ─────
def npn(cx, cy, r=26, label=None, lblcolor=INK):
    parts = [circle(cx, cy, r, fill=BG, stroke=INK, sw=2)]
    bx = cx - r * 0.35
    parts.append(line(bx, cy - r * 0.55, bx, cy + r * 0.55, color=INK, sw=2.4))
    parts.append(line(cx - r, cy, bx, cy, color=INK, sw=2))
    parts.append(line(bx, cy - r * 0.28, cx + r * 0.5, cy - r * 0.62, color=INK, sw=2))
    parts.append(line(cx + r * 0.5, cy - r * 0.62, cx + r * 0.5, cy - r - 6, color=INK, sw=2))
    ex, ey = cx + r * 0.5, cy + r * 0.62
    parts.append(line(bx, cy + r * 0.28, ex, ey, color=INK, sw=2))
    parts.append(line(ex, ey, ex, cy + r + 6, color=INK, sw=2))
    ax, ay = (bx + ex) / 2 + 2, (cy + r * 0.28 + ey) / 2 + 1
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        ax, ay, ax - 7, ay - 1, ax - 2, ay - 7, INK))
    if label:
        parts.append(text(cx + r + 4, cy - r * 0.2, label, size=14, color=lblcolor, bold=True, anchor="start"))
    pts = {"b": (cx - r, cy), "c": (cx + r * 0.5, cy - r - 6), "e": (cx + r * 0.5, cy + r + 6)}
    return "".join(parts), pts


# ════════════════════════════════════════════════════════════════════════════
# 1. array-channel.svg — що всередині ОДНОГО каналу масиву
# ════════════════════════════════════════════════════════════════════════════
def fig_array_channel():
    W, H = 780, 360
    f = []
    # межа однієї «комірки» каналу
    f.append(rect(150, 70, 480, 250, fill="#fafbfc", stroke="#cccccc", sw=1.5, rx=10))
    f.append(text(390, 92, "один канал масиву — їх 7 чи 8 однакових", size=12.5,
                  color=MUTED, italic=True))
    # вхід INn ліворуч
    f.append(line(55, 175, 110, 175, color=NEG, sw=2.4))
    f.append(circle(55, 175, 4, fill=NEG, stroke=NEG))
    f.append(text(50, 165, "INn", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(50, 198, "від логіки", size=11, color=MUTED, anchor="start"))
    # вбудований базовий резистор (горизонтальний)
    f.append(line(110, 175, 178, 175, color=INK, sw=2))
    f.append(rect(178, 163, 58, 24, fill="#fff4e6", stroke=LINE))
    f.append(text(207, 156, "≈2.7 кΩ", size=11.5, color=INK))
    f.append(text(207, 205, "базовий R", size=11, color=MUTED))
    f.append(line(236, 175, 272, 175, color=INK, sw=2))
    # Дарлінгтон (два NPN)
    q1, p1 = npn(312, 150, r=24, label="Q1")
    q2, p2 = npn(398, 232, r=28, label="Q2")
    f.append(q1)
    f.append(q2)
    # база Q1 від резистора
    f.append(line(272, 175, p1["b"][0], 175, color=INK, sw=2))
    f.append(line(p1["b"][0], p1["b"][1], p1["b"][0], 175, color=INK, sw=2))
    # E1 -> B2
    f.append(line(p1["e"][0], p1["e"][1], p1["e"][0], p2["b"][1], color=INK, sw=1.8))
    f.append(line(p1["e"][0], p2["b"][1], p2["b"][0], p2["b"][1], color=INK, sw=1.8))
    f.append(circle(p2["b"][0], p2["b"][1], 3, fill=INK, stroke=INK))
    # резистор-злив на базі Q2 (вбудований) — коротка позначка вниз до емітера
    f.append(line(p2["b"][0], p2["b"][1], p2["b"][0], p2["b"][1] + 20, color=LINE, sw=1.6))
    f.append(rect(p2["b"][0] - 9, p2["b"][1] + 20, 18, 28, fill="#fff4e6", stroke=LINE))
    f.append(text(p2["b"][0] - 13, p2["b"][1] + 66, "злив", size=10.5, color=MUTED, anchor="end"))
    f.append(line(p2["b"][0], p2["b"][1] + 48, p2["b"][0], 300, color=LINE, sw=1.6))
    # колектори обох -> вихід OUTn (відкритий колектор)
    cxo = 490
    f.append(line(p1["c"][0], p1["c"][1], p1["c"][0], 122, color=INK, sw=1.8))
    f.append(line(p2["c"][0], p2["c"][1], p2["c"][0], 122, color=INK, sw=1.8))
    f.append(line(p1["c"][0], 122, cxo, 122, color=INK, sw=1.8))
    f.append(circle(p2["c"][0], 122, 3, fill=INK, stroke=INK))
    f.append(line(cxo, 122, cxo, 175, color=INK, sw=2))
    f.append(line(cxo, 175, 720, 175, color=INK, sw=2.4))
    f.append(circle(720, 175, 4, fill=INK, stroke=INK))
    f.append(text(690, 165, "OUTn", size=13, color=INK, anchor="start", bold=True))
    f.append(text(636, 200, "відкритий", size=11, color=MUTED, anchor="start"))
    f.append(text(636, 215, "колектор", size=11, color=MUTED, anchor="start"))
    # гасильний діод від OUTn (анод) до COM (катод) — угору
    f.append(line(cxo, 175, cxo, 132, color=POS, sw=1.8))
    dy = 132
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8"/>' % (
        cxo - 8, dy, cxo + 8, dy, cxo, dy - 14, POS))
    f.append(line(cxo - 8, dy - 14, cxo + 8, dy - 14, color=POS, sw=2))  # смужка катода
    f.append(line(cxo, dy - 14, cxo, 100, color=POS, sw=1.8))
    f.append(text(cxo + 12, 116, "гасильний діод", size=11, color=POS, anchor="start"))
    # шина COM згори
    f.append(line(560, 100, 720, 100, color=POS, sw=2.2))
    f.append(circle(720, 100, 4, fill=POS, stroke=POS))
    f.append(text(690, 92, "COM", size=13, color=POS, anchor="start", bold=True))
    # спільний емітер -> GND знизу
    f.append(line(p2["e"][0], p2["e"][1], p2["e"][0], 300, color=INK, sw=2))
    f.append(line(170, 300, 720, 300, color=INK, sw=2.4))
    f.append(circle(720, 300, 4, fill=INK, stroke=INK))
    f.append(text(690, 322, "GND", size=13, color=INK, anchor="start", bold=True))
    f.append(text(176, 322, "спільна земля всіх каналів", size=11.5, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, "array-channel.svg"), W, H, *f,
                  title="Усередині одного каналу: базовий R, Дарлінгтон, гасильний діод на COM")


# ════════════════════════════════════════════════════════════════════════════
# 2. array-pinout.svg — типова розпіновка: входи ліворуч, виходи дзеркально праворуч
# ════════════════════════════════════════════════════════════════════════════
def fig_array_pinout():
    W, H = 660, 450
    f = []
    bx0, by0, bw, bh = 240, 70, 180, 320
    f.append(rect(bx0, by0, bw, bh, fill="#f4f6f8", stroke=INK, sw=2, rx=8))
    # ключ-виямка згори
    f.append('<path d="M %.1f %.1f a 12 12 0 0 0 24 0" fill="%s" stroke="%s" stroke-width="2"/>' % (
        bx0 + bw / 2 - 12, by0, BG, INK))
    f.append(mtext(bx0 + bw / 2, by0 + bh / 2 - 8, ["масив", "7 каналів"], size=13, color=MUTED))
    n = 8
    pitch = (bh - 30) / (n - 1)
    for i in range(n):
        yy = by0 + 15 + i * pitch
        f.append(line(bx0 - 26, yy, bx0, yy, color=INK, sw=2))
        f.append(circle(bx0 - 26, yy, 3.2, fill=NEG, stroke=NEG))
        f.append(line(bx0 + bw, yy, bx0 + bw + 26, yy, color=INK, sw=2))
        f.append(circle(bx0 + bw + 26, yy, 3.2, fill=INK, stroke=INK))
        if i < 7:
            f.append(text(bx0 - 32, yy + 4, "IN%d" % (i + 1), size=12.5, color=NEG, anchor="end", bold=True))
            f.append(text(bx0 + 8, yy + 4, "%d" % (i + 1), size=10.5, color=MUTED, anchor="start"))
        else:
            f.append(text(bx0 - 32, yy + 4, "GND", size=12.5, color=INK, anchor="end", bold=True))
            f.append(text(bx0 + 8, yy + 4, "8", size=10.5, color=MUTED, anchor="start"))
        if i < 7:
            f.append(text(bx0 + bw + 32, yy + 4, "OUT%d" % (i + 1), size=12.5, color=INK, anchor="start", bold=True))
            f.append(text(bx0 + bw - 8, yy + 4, "%d" % (16 - i), size=10.5, color=MUTED, anchor="end"))
        else:
            f.append(text(bx0 + bw + 32, yy + 4, "COM", size=12.5, color=POS, anchor="start", bold=True))
            f.append(text(bx0 + bw - 8, yy + 4, "9", size=10.5, color=MUTED, anchor="end"))
    f.append(text(bx0 - 72, by0 - 26, "входи від логіки", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(bx0 + bw + 6, by0 - 26, "виходи до навантажень", size=12, color=INK, anchor="start", bold=True))
    f.append(text(bx0 + bw / 2, by0 + bh + 30,
                  "INk навпроти OUTk — канал це рівний прохід крізь корпус", size=11.5, color=MUTED))
    f.append(text(bx0 + bw / 2, by0 + bh + 50,
                  "COM (катоди гасильних діодів) — на + живлення навантажень", size=11.5, color=POS))
    return render(os.path.join(IMG, "array-pinout.svg"), W, H, *f,
                  title="Типова розпіновка масиву: входи ліворуч, виходи дзеркально праворуч")


# ════════════════════════════════════════════════════════════════════════════
# 3. array-relay.svg — «перший байт»: реле між +V і OUTn, COM на +V
# ════════════════════════════════════════════════════════════════════════════
def fig_array_relay():
    W, H = 740, 360
    f = []
    # шина +V згори
    f.append(line(70, 64, 660, 64, color=POS, sw=2.6))
    f.append(text(60, 54, "+V (живлення навантажень)", size=12, color=POS, anchor="start", bold=True))
    f.append(plus(675, 64, r=9))
    # корпус масиву (частина)
    f.append(rect(120, 150, 150, 150, fill="#f4f6f8", stroke=INK, sw=2, rx=8))
    f.append(text(195, 138, "масив", size=12.5, color=MUTED))
    # вхід INn
    f.append(line(40, 200, 120, 200, color=NEG, sw=2.2))
    f.append(circle(40, 200, 4, fill=NEG, stroke=NEG))
    f.append(text(36, 190, "INn (логіка)", size=11.5, color=NEG, anchor="start", bold=True))
    # GND масиву
    f.append(line(195, 300, 195, 330, color=INK, sw=2.2))
    f.append(line(150, 330, 240, 330, color=INK, sw=2.2))
    f.append(line(175, 338, 215, 338, color=INK, sw=1.8))
    f.append(line(183, 345, 207, 345, color=INK, sw=1.6))
    f.append(text(248, 332, "GND", size=11.5, color=INK, anchor="start", bold=True))
    # вихід OUTn
    f.append(line(270, 200, 360, 200, color=INK, sw=2.4))
    f.append(text(280, 190, "OUTn", size=12, color=INK, anchor="start", bold=True))
    f.append(text(280, 222, "тягне до землі", size=11, color=MUTED, anchor="start"))
    # COM на +V
    f.append(line(270, 170, 470, 170, color=POS, sw=2))
    f.append(line(470, 170, 470, 64, color=POS, sw=2))
    f.append(circle(470, 64, 3.5, fill=POS, stroke=POS))
    f.append(text(276, 162, "COM", size=12, color=POS, anchor="start", bold=True))
    # реле: котушка між +V і OUTn
    f.append(line(360, 64, 360, 110, color=INK, sw=2))
    f.append(circle(360, 64, 3.5, fill=POS, stroke=POS))
    coil = "M 360 110"
    yy = 110
    for k in range(5):
        coil += " q 16 10 0 20"
        yy += 20
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (coil, INK))
    f.append(line(360, yy, 360, 200, color=INK, sw=2))
    f.append(text(384, 148, "котушка реле", size=11, color=INK, anchor="start"))
    f.append(text(384, 164, "(індуктивне", size=11, color=INK, anchor="start"))
    f.append(text(384, 180, "навантаження)", size=11, color=INK, anchor="start"))
    # гасильний діод усередині масиву (від OUTn до COM) — позначка-рамка
    f.append(rect(285, 238, 168, 52, fill="#fff4e6", stroke=POS, sw=1.4, rx=6))
    f.append(mtext(369, 258, ["вбудований діод", "OUTn → COM гасить викид"], size=10.5, color=POS))
    # пояснення збоку
    f.append(mtext(500, 120, ["При вимкненні струм", "котушки замикається",
                              "через діод на COM —", "сплеск гаситься."], size=11.5, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, "array-relay.svg"), W, H, *f,
                  title="«Перший байт»: реле між +V і OUTn, COM на +V, діод гасить викид")


if __name__ == "__main__":
    fig_array_channel()
    fig_array_pinout()
    fig_array_relay()
    print("OK: 3 фігури масиву у", IMG)
