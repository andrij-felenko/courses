# -*- coding: utf-8 -*-
"""Фігури теми «MOSFET-масив — драйвер нижнього плеча».
  mosfet-array-driver.md →
    inside.svg      — що всередині масиву: 8 DMOS-ключів + гасні діоди на COM
    drop-vs-i.svg   — падіння на ключі: I·Ron (польовий) проти майже фіксованого Vsat (Дарлінгтон)
    wiring.svg      — типове підключення: логіка → входи, навантаження між + і виходами
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8)]
    out.append(line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.4))
    out.append(line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=2.0))
    out.append(line(cx - 2.5, y + 16, cx + 2.5, y + 16, color=INK, sw=1.8))
    if label:
        out.append(text(cx, y + 30, label, size=10.5, color=INK, bold=True))
    return "".join(out)


def channel(f, cx, comY, gndY, inLabel, outLabel, detailed=False):
    """Один канал: DMOS-ключ між OUTx (угорі) і GND (унизу), затвор від INx,
    гасний діод OUTx→COM (анод на OUT, катод на COM угорі)."""
    boxTop, boxBot = 168, 244
    # DMOS-ключ
    f.append(rect(cx - 22, boxTop, 44, boxBot - boxTop, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(cx, boxTop + 24, "DMOS", size=10.5, color=FIELD, bold=True))
    f.append(text(cx, boxTop + 42, "Ron", size=10, color=MUTED))
    # OUTx: стік угору до вузла OUT (нижче COM)
    outNodeY = comY + 34
    f.append(line(cx, boxTop, cx, outNodeY, color=INK, sw=2))
    f.append(circle(cx, outNodeY, 3, fill=INK, stroke=INK))
    f.append(text(cx + 24, outNodeY - 6, outLabel, size=10, color=INK, anchor="start"))
    # витік униз на спільну землю
    f.append(line(cx, boxBot, cx, gndY, color=INK, sw=2))
    f.append(circle(cx, gndY, 3, fill=INK, stroke=INK))
    # затвор від входу INx (зліва в бік квадрата)
    f.append(line(cx - 60, boxTop + (boxBot - boxTop) / 2, cx - 22, boxTop + (boxBot - boxTop) / 2, color=INK, sw=1.8))
    f.append(text(cx - 64, boxTop + (boxBot - boxTop) / 2 + 4, inLabel, size=10, color=INK, anchor="end"))
    # гасний діод: анод на вузлі OUT, катод угорі на COM (трикутник вістрям угору)
    dx0 = cx + 30
    f.append(line(cx, outNodeY, dx0, outNodeY, color=POS, sw=1.8))         # OUT → анод
    f.append(line(dx0, outNodeY, dx0, comY + 18, color=POS, sw=1.8))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>' % (
        dx0, comY + 4, dx0 - 8, comY + 18, dx0 + 8, comY + 18, POS))     # трикутник вістрям угору
    f.append(line(dx0 - 8, comY + 4, dx0 + 8, comY + 4, color=POS, sw=2.4))  # риска-катод
    f.append(line(dx0, comY + 4, dx0, comY, color=POS, sw=1.8))            # катод → COM
    f.append(circle(dx0, comY, 3, fill=POS, stroke=POS))


# ── 1. Що всередині: два канали крупно (× N) + гасні діоди на COM ─────────────
def fig_inside():
    W, H = 720, 470
    f = [text(W / 2, 26, "MOSFET-масив зсередини: кожен канал — DMOS-ключ нижнього плеча + гасний діод на спільний COM",
              size=13.5, bold=True)]

    # рамка мікросхеми
    f.append(rect(40, 56, 640, 320, fill="#fbfcfd", stroke=LINE, sw=1.8, rx=12))
    f.append(text(58, 80, "мікросхема (× N каналів)", size=11, color=MUTED, anchor="start"))

    comY, gndY = 108, 300
    # шина COM (спільні катоди діодів)
    f.append(line(90, comY, 600, comY, color=POS, sw=2.4))
    f.append(text(606, comY + 4, "COM", size=12, color=POS, bold=True, anchor="start"))
    # спільна земля
    f.append(line(90, gndY, 600, gndY, color=INK, sw=2))
    f.append(text(606, gndY + 4, "GND", size=11, color=INK, bold=True, anchor="start"))

    channel(f, 230, comY, gndY, "IN1", "OUT1")
    channel(f, 430, comY, gndY, "IN2", "OUT2")
    # трикрапка «і так далі»
    f.append(text(545, (comY + gndY) / 2, "•  •  •", size=18, color=MUTED))

    # підпис-висновок
    b, _, _ = textbox(W / 2, 420,
                      "Вхід IN «1» → канал відкривається → OUT притягнуто до землі (нижнє плече, sink).\n"
                      "Гасний діод кожного OUT (анод на OUT, катод на COM) зведено на спільний COM.",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Падіння на ключі: I·Ron (пряма з нуля) проти майже фіксованого Vsat ────
def fig_drop_vs_i():
    W, H = 720, 420
    f = [text(W / 2, 26, "Падіння на відкритому ключі: польовий росте від нуля (I·Ron), Дарлінгтон стоїть на «сходинці» ≈1 В",
              size=13.5, bold=True)]

    # осі
    ox, oy = 90, 340       # початок координат
    axW, axH = 560, 250
    f.append(line(ox, oy, ox + axW, oy, color=INK, sw=1.8))       # X (струм)
    f.append(line(ox, oy, ox, oy - axH, color=INK, sw=1.8))       # Y (падіння)
    f.append(text(ox + axW, oy + 22, "струм каналу I →", size=11, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - axH + 4, "падіння U", size=11, color=INK, anchor="end"))

    Imax = 0.5             # 500 мА повна шкала
    def X(i): return ox + (i / Imax) * axW
    # шкала струму
    for i, lab in [(0.0, "0"), (0.2, "0.2 А"), (0.5, "0.5 А")]:
        f.append(line(X(i), oy, X(i), oy + 5, color=INK, sw=1.4))
        f.append(text(X(i), oy + 20, lab, size=10, color=MUTED))
    # шкала напруги: 0.5, 1.0 В
    def Y(v): return oy - (v / 1.3) * axH
    for v, lab in [(0.5, "0.5 В"), (1.0, "1.0 В")]:
        f.append(line(ox - 5, Y(v), ox, Y(v), color=INK, sw=1.4))
        f.append(text(ox - 12, Y(v) + 4, lab, size=10, color=MUTED, anchor="end"))
        f.append(line(ox, Y(v), ox + axW, Y(v), color="#e2e6ea", sw=1, dash="4 4"))

    # Дарлінгтон: майже горизонталь на ~1 В (лишень трохи росте)
    dpts = [(X(0.0), Y(0.75)), (X(0.05), Y(0.9)), (X(0.2), Y(1.0)), (X(0.5), Y(1.15))]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (
        " ".join("%.1f,%.1f" % p for p in dpts), POS))
    f.append(text(X(0.5) + 6, Y(1.15) + 2, "Дарлінгтон (біполярний ULN)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(X(0.5) + 6, Y(1.15) + 18, "«сходинка» ≈2 переходи, ≈1 В", size=9.5, color=POS, anchor="start"))

    # MOSFET: пряма з нуля, нахил Ron ≈ 2.5 Ом → при 0.2 А ≈0.5 В, при 0.5 А ≈1.25 В (обрізаємо)
    Ron = 2.5
    f.append(line(X(0.0), Y(0.0), X(0.5), Y(0.5 * Ron), color=FIELD, sw=2.6))
    f.append(text(X(0.42), Y(0.42 * Ron) - 8, "польовий (DMOS): U = I·Ron", size=11, color=FIELD, bold=True, anchor="end"))

    # маркер на 0.2 А: різниця 0.5 В проти 1.0 В
    f.append(circle(X(0.2), Y(0.2 * Ron), 4, fill=FIELD, stroke=FIELD))
    f.append(circle(X(0.2), Y(1.0), 4, fill=POS, stroke=POS))
    f.append(line(X(0.2), Y(0.2 * Ron), X(0.2), Y(1.0), color=MUTED, sw=1.4, dash="3 3"))
    f.append(text(X(0.2) + 10, (Y(0.5) + Y(1.0)) / 2, "виграш ≈0.5 В", size=10.5, color=INK, bold=True, anchor="start"))

    render(os.path.join(IMG, "drop-vs-i.svg"), W, H, *f)


# ── 3. Типове підключення: логіка → входи; навантаження між + і виходами ──────
def fig_wiring():
    W, H = 720, 400
    f = [text(W / 2, 26, "Підключення: входи прямо з логіки, навантаження між «плюсом» і виходами, COM на «плюс»",
              size=13.5, bold=True)]

    # мікросхема-блок
    bx, by, bw, bh = 240, 95, 190, 210
    f.append(rect(bx, by, bw, bh, fill="#fbfcfd", stroke=LINE, sw=1.8, rx=10))
    f.append(text(bx + bw / 2, by + 22, "MOSFET-масив", size=12, bold=True))
    f.append(text(bx + bw / 2, by + 40, "(нижнє плече)", size=10, color=MUTED))

    # МК ліворуч
    f.append(rect(40, 150, 120, 96, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(100, 180, "МК", size=13, bold=True))
    f.append(text(100, 204, "GPIO 3.3 В", size=10, color=INK))
    f.append(text(100, 226, "≈0 струму", size=10, color=MUTED))
    for yy in [170, 198, 226]:
        f.append(arrow(160, yy, bx, yy, color=FIELD, sw=1.8))
    f.append(text((160 + bx) / 2, 250, "IN1..INn", size=10.5, color=INK))

    # шина +V угорі
    railY = 66
    f.append(line(470, railY, 690, railY, color=POS, sw=2.4))
    f.append(text(694, railY + 4, "+V", size=12, color=POS, bold=True, anchor="start"))

    # COM з мікросхеми на +V
    comX = 500
    f.append(line(bx + bw, by + 28, comX, by + 28, color=POS, sw=2))
    f.append(text(bx + bw + 4, by + 22, "COM", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(line(comX, by + 28, comX, railY, color=POS, sw=2))
    f.append(circle(comX, railY, 3, fill=POS, stroke=POS))

    # два навантаження в РІЗНИХ стовпцях (щоб вертикальні фіди не накладались):
    # від +V униз крізь навантаження, тоді горизонтально до відповідного OUTx
    loads = [(540, 150, "реле", 78), (640, 235, "соленоїд", 118)]
    for lx, yy, lab, outDy in loads:
        f.append(line(lx, railY, lx, yy - 24, color=INK, sw=2))
        f.append(circle(lx, railY, 3, fill=INK, stroke=INK))
        f.append(rect(lx - 28, yy - 24, 56, 48, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
        f.append(text(lx, yy + 4, lab, size=10.5, color=INK))
        # від навантаження вниз, тоді ліворуч до виводу OUTx мікросхеми
        outY = by + outDy
        f.append(line(lx, yy + 24, lx, outY, color=INK, sw=2))
        f.append(line(lx, outY, bx + bw, outY, color=INK, sw=2))
        f.append(circle(bx + bw, outY, 3, fill=INK, stroke=INK))
        f.append(text(bx + bw + 4, outY - 6, "OUT", size=10, color=INK, anchor="start"))

    # земля масиву
    f.append(gnd(bx + bw / 2, by + bh + 2, "GND"))

    b, _, _ = textbox(W / 2, 372,
                      "Струм: +V → навантаження → OUTx → крізь відкритий канал → GND. Гасний діод (OUT→COM) уже всередині.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_drop_vs_i()
    fig_wiring()
    print("OK: 3 figures ->", IMG)
