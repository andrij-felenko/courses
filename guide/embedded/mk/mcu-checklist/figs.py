# -*- coding: utf-8 -*-
"""Фігури до теми «Чеклист вибору МК» та її 🧮-вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit (під сімейства/критерії)
BLUE = "#2980b9"
PURP = "#8e44ad"
ORNG = "#e67e22"
GRN2 = "#1a6b3a"


# ── 1. Дерево питань: вимоги-вбивці першими ─────────────────────────────────
def fig_decision_tree():
    W, H = 760, 430
    f = [text(W / 2, 26, "Спершу вимоги, тоді чіп", size=16, bold=True)]

    # корінь
    f.append(rect(28, 188, 168, 60, fill=FILL, stroke=INK, sw=2))
    f.append(text(112, 213, "вимоги проєкту:", size=12.5, bold=True))
    f.append(text(112, 231, "проходимо осі", size=12.5, bold=True))

    # вісь 2 — зв'язок (вимога-вбивця)
    f.append(line(196, 206, 262, 92, color=NEG, sw=2))
    f.append(text(214, 132, "радіо?", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(262, 66, 238, 54, fill=FILL, stroke=NEG, sw=2))
    f.append(text(381, 88, "вимога-вбивця №1", size=12, color=NEG, bold=True))
    f.append(text(381, 106, "BLE→nRF · Wi-Fi→ESP32", size=9.5, color=MUTED, italic=True))

    # вісь 3 — живлення (вимога-вбивця)
    f.append(line(196, 214, 262, 218, color=POS, sw=2))
    f.append(text(214, 200, "батарея роками?", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(262, 192, 238, 54, fill=FILL, stroke=POS, sw=2))
    f.append(text(381, 214, "вимога-вбивця №2", size=12, color=POS, bold=True))
    f.append(text(381, 232, "мкА сну → радіо-МК", size=9.5, color=MUTED, italic=True))

    # осі 4–7 — тонке доналаштування
    f.append(line(196, 224, 262, 344, color=MUTED, sw=1.8))
    f.append(text(214, 322, "далі:", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(rect(262, 318, 238, 70, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(381, 338, "тонке доналаштування", size=11.5, color=INK, bold=True))
    f.append(text(381, 356, "периферія · продуктивність", size=9.5, color=MUTED, italic=True))
    f.append(text(381, 372, "корпус · ціна · екосистема", size=9.5, color=MUTED, italic=True))

    # стрілка-результат
    f.append(arrow(500, 93, 600, 120, color=NEG, sw=1.6))
    f.append(arrow(500, 219, 600, 210, color=POS, sw=1.6))
    f.append(arrow(500, 350, 600, 300, color=MUTED, sw=1.6))
    box, bw, bh = textbox(666, 207, "звужене\nполе → чіп", size=12.5, bold=True,
                          fill="#eef7f0", stroke=FIELD, sw=2)
    f.append(box)

    f.append(text(W / 2, 414,
                  "перші дві розвилки відсівають найбільше; решта добирає всередині",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 2. Один метод — два проєкти — два класи ─────────────────────────────────
def fig_two_projects():
    W, H = 780, 440
    f = [text(W / 2, 26, "Один метод — різні відповіді", size=16, bold=True)]

    # дві колонки-проєкти
    col = [
        (40, "Датчик повітря", "батарея · BLE", FIELD, [
            ("Зв'язок", "BLE", NEG),
            ("Живлення", "роки від CR2032", POS),
            ("Периферія", "I²C + UART", MUTED),
            ("Продуктивн.", "скромна", MUTED),
        ], "nRF-клас", "сон + радіо вирішують"),
        (408, "Драйвер двигуна", "мережа · силовий ШІМ", BLUE, [
            ("Зв'язок", "провід", MUTED),
            ("Живлення", "мережа 24 В", MUTED),
            ("Периферія", "advanced-timer", POS),
            ("Продуктивн.", "FPU/DSP", NEG),
        ], "STM32-клас", "силова периферія вирішує"),
    ]
    for x0, title, sub, accent, rows, winner, why in col:
        f.append(rect(x0, 52, 332, 326, fill=BG, stroke=accent, sw=2))
        f.append(text(x0 + 166, 78, title, size=14, bold=True, color=accent))
        f.append(text(x0 + 166, 96, sub, size=10.5, color=MUTED, italic=True))
        y = 122
        for name, val, c in rows:
            f.append(text(x0 + 22, y, name, size=11.5, anchor="start", bold=True))
            f.append(text(x0 + 310, y, val, size=11.5, anchor="end", color=c))
            f.append(line(x0 + 22, y + 10, x0 + 310, y + 10, color="#e5e7eb", sw=1))
            y += 34
        # результат
        f.append(arrow(x0 + 166, y + 4, x0 + 166, y + 30, color=accent, sw=1.8))
        box, bw, bh = textbox(x0 + 166, y + 58, winner, size=14, bold=True,
                              fill="#eef7f0" if accent == FIELD else "#eef3fb",
                              stroke=accent, sw=2, min_w=150)
        f.append(box)
        f.append(text(x0 + 166, y + 92, why, size=10, color=MUTED, italic=True))

    f.append(text(W / 2, 420, "ті самі осі — протилежний профіль — інший клас МК",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "two-projects.svg"), W, H, *f)


# ── 3. Зважені суми S (stacked) — для 🧮-вставки ────────────────────────────
def fig_decision_bars():
    W, H = 820, 420
    SCALE = 126.0  # px на 1 бал (0..5 → 150..780)
    X0 = 150.0
    crits = [("Сон", BLUE), ("Радіо", FIELD), ("Периферія", PURP),
             ("Екосистема", ORNG), ("Ціна", POS)]
    # рядки: назва, [бали по 5 критеріях], сума, жирний?
    rows = [
        ("nRF-клас",   [5, 5, 4, 3, 3], 4.30, True),
        ("ESP32",      [3, 4, 5, 5, 4], 4.05, False),
        ("STM32-клас", [4, 2, 4, 4, 3], 3.40, False),
        ("AVR-клас",   [3, 1, 3, 2, 5], 2.55, False),
        ("RP2040-клас",[2, 1, 4, 3, 4], 2.50, False),
    ]
    weights = [0.30, 0.25, 0.20, 0.15, 0.10]
    f = [text(W / 2, 32, "Зважені суми S п'яти кандидатів", size=17, bold=True)]

    # вісь зверху (0..5)
    f.append(text(465, 16, "← зважена сума S (max = 5.00) →", size=11, color=MUTED))
    f.append(line(X0, 34, X0 + 5 * SCALE, 34, color=MUTED, sw=1))
    for t in range(6):
        xt = X0 + t * SCALE
        f.append(line(xt, 34, xt, 39, color=MUTED, sw=1))
        f.append(text(xt, 30, str(t), size=11, color=MUTED))

    y = 54
    for name, scores, S, hot in rows:
        h = 32 if hot else 26
        f.append(text(126, y + h * 0.65, name, size=15 if hot else 14, anchor="end",
                      bold=hot, color=GRN2 if hot else INK))
        x = X0
        for (cl, color), sc, w in zip(crits, scores, weights):
            seg = sc * w * SCALE          # внесок критерію у зважену суму, в px
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, y, seg, h, color, BG))
            x += seg
        if hot:
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                     'fill="none" stroke="%s" stroke-width="2"/>' % (X0, y, x - X0, h, GRN2))
        f.append(text(x + 6, y + h * 0.65, "%.2f" % S, size=13, anchor="start",
                      bold=hot))
        y += 52

    # легенда
    lx = 150
    for cl, color in crits:
        f.append('<rect x="%d" y="340" width="16" height="14" fill="%s" rx="3"/>' % (lx, color))
        f.append(text(lx + 20, 351, cl, size=12, anchor="start"))
        lx += 126
    render(os.path.join(IMG, "decision-bars.svg"), W, H, *f)


# ── 4. Чутливість до зсуву ваги «сон ↔ периферія» — для 🧮-вставки ──────────
def fig_weight_sensitivity():
    W, H = 740, 400
    PX0, PY0, PW, PH = 90, 60, 590, 260   # рамка графіка
    f = [text(W / 2, 30, "Чутливість результату до зсуву ваги «сон ↔ периферія»",
              size=16, bold=True)]
    f.append(rect(PX0, PY0, PW, PH, fill="#f8fafc", stroke="#cccccc", sw=1, rx=4))

    # S-сітка 3.0..5.0
    def sy(s):
        return PY0 + PH - (s - 3.0) / (5.0 - 3.0) * PH
    for s10 in range(30, 51, 5):
        s = s10 / 10.0
        yy = sy(s)
        f.append(line(PX0, yy, PX0 + PW, yy, color="#e0e0e0", sw=1))
        f.append(text(PX0 - 6, yy + 4, "%.1f" % s, size=11, color=MUTED, anchor="end"))

    # вісь Δ від -0.10 до +0.10
    def dx(d):
        return PX0 + (d + 0.10) / 0.20 * PW
    for d10 in range(-10, 11, 5):
        d = d10 / 100.0
        xx = dx(d)
        f.append(line(xx, PY0, xx, PY0 + PH, color="#e0e0e0", sw=1))
        lab = "0" if d10 == 0 else ("%+.2f" % d)
        f.append(text(xx, PY0 + PH + 16, lab, size=11, color=MUTED))

    # лінія Δ=0
    f.append(line(dx(0), PY0, dx(0), PY0 + PH, color="#aaaaaa", sw=1.5, dash="4 3"))

    # моделі: S(чіп) = базова + Δ·(бал_сон − бал_периферія)
    # nRF: сон5, периф4 → нахил +1·Δ; ESP32: сон3, периф5 → нахил −2·Δ
    def line_pts(base, slope, color, label, ly):
        pts = []
        for i in range(21):
            d = -0.10 + i * 0.01
            pts.append("%.1f,%.1f" % (dx(d), sy(base + slope * d)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), color))
        f.append(text(PX0 + PW + 6, ly, label, size=13, color=color, anchor="start", bold=True))

    # нахили = (бал_сон − бал_периферія): nRF 5−4=+1; ESP32 3−5=−2
    line_pts(4.30, 1.0, FIELD, "nRF-клас", sy(4.30 + 1.0 * 0.10))
    line_pts(4.05, -2.0, ORNG, "ESP32", sy(4.05 - 2.0 * 0.10))

    # точка перетину: 4.30 + 1·Δ = 4.05 − 2·Δ → 3·Δ = −0.25 → Δ ≈ −0.083
    dc = -0.25 / 3.0
    f.append(circle(dx(dc), sy(4.30 + 1.0 * dc), 6, fill="#ff6b6b", stroke=POS, sw=2))
    box, bw, bh = textbox(dx(dc) + 66, sy(4.30 + 1.0 * dc) - 42,
                          "Δ≈−0.08\n(лідер змінюється)", size=11, pad=8,
                          fill="#fff3f3", stroke=POS, sw=1.5)
    f.append(box)

    # зони (перетин при Δ≈−0.08, близько до лівого краю):
    #   лівіше (менше ваги сну) — лідирує ESP32; правіше — nRF-клас
    f.append(text(dx(0.03), PY0 + 20, "nRF-клас лідирує", size=11, color=FIELD, italic=True))
    f.append(text(dx(-0.093), PY0 + 40, "ESP32", size=10, color=ORNG, italic=True, anchor="start"))

    # підписи осей
    f.append(text(W / 2, PY0 + PH + 36,
                  "Зсув ваги Δ  (w_сон = 0.30 + Δ,  w_периферія = 0.20 − Δ)",
                  size=12))
    f.append(text(40, PY0 + PH / 2, "S", size=14, bold=True))
    render(os.path.join(IMG, "weight-sensitivity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision_tree()
    fig_two_projects()
    fig_decision_bars()
    fig_weight_sensitivity()
    print("OK: 4 SVG -> ./img/")
