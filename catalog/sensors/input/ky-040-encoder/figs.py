# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-040 — поворотний енкодер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Квадратура: дві доріжки, зсунуті на чверть; порядок країв = напрям ────────
def fig_quadrature():
    W, H = 960, 560
    f = [text(W / 2, 30, "Дві доріжки, зсунуті на чверть кроку: хто впав першим — той і каже напрям",
              size=15, bold=True)]

    x0, x1 = 150, 470          # межі осі часу для ЛІВОЇ сцени (за годинником)
    step = 40                  # ширина півперіоду

    def track(y_hi, y_lo, phase_shift, x_start, x_end, color, seq_dir):
        """Малює квадратну доріжку; повертає список x-координат СПАДНИХ країв."""
        falls = []
        x = x_start + phase_shift
        level = y_hi
        prev_x = x_start
        # стартовий рівень
        f.append(line(x_start, level, x, level, color=color, sw=2.6))
        while x < x_end:
            nxt = min(x + step, x_end)
            new_level = y_lo if level == y_hi else y_hi
            # вертикальний фронт
            f.append(line(x, level, x, new_level, color=color, sw=2.6))
            if new_level == y_lo:      # спадний край
                falls.append(x)
            # горизонталь
            f.append(line(x, new_level, nxt, new_level, color=color, sw=2.6))
            level = new_level
            x = nxt
        return falls

    # ── ЛІВА сцена: за годинником (CLK падає першим) ──
    f.append(text((x0 + x1) / 2, 66, "За годинниковою стрілкою", size=12.5, bold=True, color=FIELD))
    clk_hi, clk_lo = 95, 135
    dt_hi, dt_lo = 185, 225
    f.append(text(x0 - 12, (clk_hi + clk_lo) / 2 + 4, "CLK", size=12, bold=True, color=NEG, anchor="end"))
    f.append(text(x0 - 12, (dt_hi + dt_lo) / 2 + 4, "DT", size=12, bold=True, color=POS, anchor="end"))
    clk_falls = track(clk_hi, clk_lo, 0, x0, x1, NEG, +1)
    dt_falls = track(dt_hi, dt_lo, step, x0, x1, POS, +1)   # DT зсунутий → падає ПІЗНІШЕ

    # позначити перший спадний край CLK і читання DT у цю мить
    if clk_falls:
        cx = clk_falls[0]
        f.append(line(cx, clk_lo + 6, cx, dt_hi - 6, color=MUTED, sw=1.1, dash="4,4"))
        f.append(circle(cx, clk_lo, 4, fill=NEG, stroke=NEG, sw=1))
        # у цю мить DT ще HIGH
        f.append(text(cx + 6, dt_hi - 12, "CLK↓ : DT ще «1» → CW", size=10, bold=True, color=FIELD, anchor="start"))

    # ── ПРАВА сцена: проти годинника (DT падає першим) ──
    xr0, xr1 = 620, 940
    f.append(text((xr0 + xr1) / 2, 66, "Проти годинникової стрілки", size=12.5, bold=True, color=POS))
    f.append(text(xr0 - 12, (clk_hi + clk_lo) / 2 + 4, "CLK", size=12, bold=True, color=NEG, anchor="end"))
    f.append(text(xr0 - 12, (dt_hi + dt_lo) / 2 + 4, "DT", size=12, bold=True, color=POS, anchor="end"))
    clk_falls_r = track(clk_hi, clk_lo, step, xr0, xr1, NEG, -1)   # тепер CLK зсунутий → падає пізніше
    dt_falls_r = track(dt_hi, dt_lo, 0, xr0, xr1, POS, -1)

    if clk_falls_r:
        cx = clk_falls_r[0]
        f.append(line(cx, clk_lo + 6, cx, dt_hi - 6, color=MUTED, sw=1.1, dash="4,4"))
        f.append(circle(cx, clk_lo, 4, fill=NEG, stroke=NEG, sw=1))
        f.append(text(cx + 6, dt_hi - 12, "CLK↓ : DT вже «0» → CCW", size=10, bold=True, color=POS, anchor="start"))

    # осі часу під кожною сценою
    f.append(line(x0, dt_lo + 60, x1, dt_lo + 60, color=MUTED, sw=1.1))
    f.append(text(x1, dt_lo + 52, "час →", size=9.5, color=MUTED, anchor="end"))
    f.append(line(xr0, dt_lo + 60, xr1, dt_lo + 60, color=MUTED, sw=1.1))
    f.append(text(xr1, dt_lo + 52, "час →", size=9.5, color=MUTED, anchor="end"))

    # правило унизу
    b, _, _ = textbox(W / 2, 430, "Обидві доріжки видають однакові прямокутники — різниця лише у ЗСУВІ на чверть кроку.\n"
                                  "Спіймав спадний край CLK і глянув на DT: DT = «1» → за годинником; DT = «0» → проти.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(W / 2, 505, "Швидше крутиш — частіше прямокутники, але їхній ПОРЯДОК не змінюється:\n"
                                  "напрям читається зі зсуву фаз, а не зі швидкості.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "quadrature-timing.svg"), W, H, *f)


# ── 2. Що всередині KY-040: EC11 + дві підтяжки 10к; підтяжка кнопки часто відсутня ─
def fig_ky040_schematic():
    W, H = 920, 560
    f = [text(W / 2, 30, "Що всередині KY-040: енкодер EC11, дві підтяжки 10 кОм і кнопка",
              size=15, bold=True)]

    bx, by, bw, bh = 110, 66, 700, 360
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-040", size=11, bold=True, color=MUTED, anchor="start"))

    # шини живлення і землі
    vcc_y = by + 52
    gnd_y = by + bh - 40
    f.append(line(bx + 40, vcc_y, bx + bw - 40, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 40, vcc_y - 10, "+  (VCC 3.3–5 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(bx + 40, gnd_y, bx + bw - 40, gnd_y, color=NEG, sw=2.2))
    f.append(text(bx + 40, gnd_y + 22, "−  (GND) = спільний вивід C енкодера", size=11, bold=True, color=NEG, anchor="start"))

    # --- корпус енкодера EC11 (лівий блок): три виводи A, C, B ---
    ec_x, ec_y, ec_w, ec_h = bx + 70, vcc_y + 44, 150, gnd_y - vcc_y - 88
    f.append(rect(ec_x, ec_y, ec_w, ec_h, fill="#eef3fb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(ec_x + ec_w / 2, ec_y + 24, "енкодер", size=12, bold=True, color=NEG))
    f.append(text(ec_x + ec_w / 2, ec_y + 42, "EC11", size=11, color=MUTED))
    f.append(text(ec_x + ec_w / 2, ec_y + ec_h - 14, "2 контакти + спільний C", size=9, color=MUTED))
    # спільний вивід C → GND
    f.append(line(ec_x + ec_w / 2, ec_y + ec_h, ec_x + ec_w / 2, gnd_y, color=NEG, sw=1.8))
    f.append(circle(ec_x + ec_w / 2, gnd_y, 3, fill=NEG, stroke=NEG, sw=1))

    # вузли A (CLK) і B (DT) — виходять праворуч від енкодера
    aY = ec_y + 26
    bY = ec_y + ec_h - 34
    f.append(line(ec_x + ec_w, aY, ec_x + ec_w + 60, aY, color=INK, sw=1.6))
    f.append(line(ec_x + ec_w, bY, ec_x + ec_w + 60, bY, color=INK, sw=1.6))
    nodeA_x = ec_x + ec_w + 60
    nodeB_x = ec_x + ec_w + 60
    f.append(circle(nodeA_x, aY, 3.2, fill=INK, stroke=INK, sw=1))
    f.append(circle(nodeB_x, bY, 3.2, fill=INK, stroke=INK, sw=1))

    # підтяжки R2 (CLK) і R3 (DT) від VCC до вузлів
    def pullup(nx, ny, label):
        f.append(line(nx, vcc_y, nx, ny - 40, color=INK, sw=1.6))
        f.append(rect(nx - 14, ny - 40, 28, 34, fill=BG, stroke=INK, sw=1.5, rx=3))
        f.append(text(nx + 22, ny - 30, label, size=10, bold=True, color=INK, anchor="start"))
        f.append(text(nx + 22, ny - 16, "10 кОм", size=9, color=MUTED, anchor="start"))
        f.append(line(nx, ny - 6, nx, ny, color=INK, sw=1.6))

    pullup(nodeA_x, aY, "R2")
    pullup(nodeB_x, bY, "R3")

    # виводи CLK і DT далі праворуч
    f.append(line(nodeA_x, aY, bx + bw - 40, aY, color=FIELD, sw=1.8))
    f.append(circle(bx + bw - 40, aY, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(bx + bw - 30, aY - 8, "CLK  (вивід A)", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(nodeB_x, bY, bx + bw - 40, bY, color=FIELD, sw=1.8))
    f.append(circle(bx + bw - 40, bY, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(bx + bw - 30, bY - 8, "DT  (вивід B)", size=11, bold=True, color=FIELD, anchor="start"))

    # --- кнопка SW (окремий вузол): між SW-піном і GND, підтяжка R1 часто ВІДСУТНЯ ---
    sw_y = (aY + bY) / 2
    swb_x = ec_x + ec_w + 250
    # кнопка (символ) від вузла SW до GND
    f.append(rect(swb_x - 18, sw_y - 12, 36, 24, fill="#fdf4ec", stroke=POS, sw=1.6, rx=4))
    f.append(text(swb_x, sw_y + 4, "SW", size=10, bold=True, color=POS))
    f.append(line(swb_x, sw_y + 12, swb_x, gnd_y, color=NEG, sw=1.6))
    f.append(circle(swb_x, gnd_y, 3, fill=NEG, stroke=NEG, sw=1))
    # місце під R1 (пунктиром — часто не запаяний): лінія від VCC до верху резистора,
    # підпис R1? — збоку від резистора, щоб пунктир його не перетинав
    f.append(line(swb_x, vcc_y, swb_x, sw_y - 40, color=MUTED, sw=1.4, dash="5,4"))
    f.append(rect(swb_x - 14, sw_y - 40, 28, 34, fill=BG, stroke=MUTED, sw=1.4, rx=3))
    f.append(text(swb_x + 22, sw_y - 18, "R1?", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(swb_x + 22, sw_y - 4, "часто нема", size=9, color=MUTED, anchor="start"))
    f.append(line(swb_x, sw_y - 6, swb_x, sw_y - 12, color=MUTED, sw=1.4, dash="5,4"))
    # вивід SW праворуч
    f.append(line(swb_x, sw_y, bx + bw - 40, sw_y, color=POS, sw=1.8))
    f.append(circle(bx + bw - 40, sw_y, 5, fill=BG, stroke=POS, sw=2))
    f.append(text(bx + bw - 30, sw_y - 8, "SW  (кнопка)", size=11, bold=True, color=POS, anchor="start"))

    # пояснення станів — окремим блоком поза схемою
    b, _, _ = textbox(W / 2, 470, "CLK і DT підтягнуті до «1»; крутиш вал → внутрішні контакти по черзі кидають їх у «0».\n"
                                  "R1 (підтяжка кнопки) на багатьох платах НЕ запаяний — тоді SW «висить»: вмикай INPUT_PULLUP.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(W / 2, 535, "Конденсаторів на платі немає — тому «сирі» краї брязкають; гасити брязкіт доводиться в коді (або доклеїти 0.1 мкФ).",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky040-schematic.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: KY-040 ↔ мікроконтролер ──────────────────────────
def fig_ky040_wiring():
    W, H = 940, 480
    f = [text(W / 2, 30, "Підключення KY-040: п'ять дротів — дві доріжки, кнопка, живлення й земля",
              size=15, bold=True)]

    # Модуль ліворуч
    mx, my, mw, mh = 70, 84, 260, 300
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=NEG, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-040", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 48, "поворотний енкодер", size=10, color=MUTED))
    pads = [("CLK", FIELD, my + 90), ("DT", FIELD, my + 135),
            ("SW", POS, my + 180), ("+", POS, my + 225), ("−", NEG, my + 270)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    # Плата праворуч
    bx, by, bw, bh = 620, 84, 250, 300
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("D2  (INT)", FIELD, by + 90, "перерив. по краю"),
            ("D3", FIELD, by + 135, "будь-який GPIO"),
            ("D4", POS, by + 180, "кнопка (pull-up!)"),
            ("3.3–5 В", POS, by + 225, "живлення"),
            ("GND", NEG, by + 270, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # п'ять дротів
    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    # застереження унизу
    b, _, _ = textbox(W / 2, 422, "CLK краще на пін із перериванням (ловити край, не проґавити оберт). SW підтяжки на платі часто нема —\n"
                                  "ставай INPUT_PULLUP. Живлення бери під логіку плати: 5 В б'є 5-вольтовими рівнями на 3.3-вольтовий вхід.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky040-wiring.svg"), W, H, *f)


# ── 4. Скінченний автомат: кільце станів (CLK,DT); один крок = повний обхід ──────
def fig_state_ring():
    W, H = 980, 620
    f = [text(W / 2, 30, "Крок = повний обхід кільця (CLK,DT): CW і CCW ідуть кільцем у протилежні боки",
              size=15, bold=True)]

    cx, cy, R = W / 2, 300, 150     # центр кільця і радіус

    # чотири стани у вершинах ромба: код (CLK,DT) як 2-бітне число
    # порядок по колу (за годинниковою на екрані): 11(top) → 01(right) → 00(bottom) → 10(left)
    nodes = [
        ("11", cx,        cy - R, "спокій\n(фіксатор)", FIELD),   # top
        ("01", cx + R,    cy,     "CLK впав\nперший",   NEG),      # right
        ("00", cx,        cy + R, "обидва\nпритиснуті", INK),      # bottom
        ("10", cx - R,    cy,     "DT впав\nперший",    POS),      # left
    ]
    pos = {}
    rad = 46
    for code, nx, ny, sub, col in nodes:
        pos[code] = (nx, ny)

    # дуги-переходи по колу малюємо ПЕРЕД вузлами, щоб кружки лягли зверху
    order = ["11", "01", "00", "10"]
    def edge(a, b, col, off, label, lx, ly, la="middle"):
        ax, ay = pos[a]; bx, by = pos[b]
        # напрямний вектор і нормаль для зсуву дуги від центрів кружків
        import math
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        # відступ від країв кружків
        sx, sy = ax + ux * (rad + 4), ay + uy * (rad + 4)
        ex, ey = bx - ux * (rad + 10), by - uy * (rad + 10)
        # невеликий вигин назовні (нормаль)
        nxv, nyv = -uy, ux
        mx, my = (sx + ex) / 2 + nxv * off, (sy + ey) / 2 + nyv * off
        f.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>' % (sx, sy, mx, my, ex, ey, col))
        f.append(text(lx, ly, label, size=11, bold=True, color=col, anchor=la))

    # CW-кільце (зелена сторона): 11→01→00→10→11, дуги вигнуті всередину
    edge("11", "01", NEG, -26, "", 0, 0)
    edge("01", "00", NEG, -26, "", 0, 0)
    edge("00", "10", NEG, -26, "", 0, 0)
    edge("10", "11", NEG, -26, "", 0, 0)
    # CCW-кільце (протилежний напрям), вигнуті назовні
    edge("11", "10", POS, -26, "", 0, 0)
    edge("10", "00", POS, -26, "", 0, 0)
    edge("00", "01", POS, -26, "", 0, 0)
    edge("01", "11", POS, -26, "", 0, 0)

    # підписи напрямів кільця — у кутах, подалі від дуг
    f.append(text(cx + R + 118, cy - R + 6, "за годинниковою (CW):", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(cx + R + 118, cy - R + 24, "11 → 01 → 00 → 10 → 11", size=11.5, color=NEG, anchor="start"))
    f.append(text(cx - R - 118, cy - R + 6, "проти (CCW):", size=12, bold=True, color=POS, anchor="end"))
    f.append(text(cx - R - 118, cy - R + 24, "11 → 10 → 00 → 01 → 11", size=11.5, color=POS, anchor="end"))

    # вузли-кружки поверх дуг
    for code, nx, ny, sub, col in nodes:
        f.append(circle(nx, ny, rad, fill=BG, stroke=col, sw=2.6))
        f.append(text(nx, ny - 4, code, size=20, bold=True, color=col))
        # дрібний підпис під кодом, у два рядки
        sub_lines = sub.split("\n")
        f.append(text(nx, ny + 15, sub_lines[0], size=9, color=MUTED))
        if len(sub_lines) > 1:
            f.append(text(nx, ny + 26, sub_lines[1], size=9, color=MUTED))

    # позначка «зарахувати крок» біля вершини «11»
    f.append(text(cx, cy - R - rad - 12, "повернулись у 11 → зарахувати +1 (CW) або −1 (CCW)",
                  size=11, bold=True, color=FIELD))

    # пояснення знизу — код Грея + інерентний дебаунс
    b, _, _ = textbox(W / 2, 500, "(CLK,DT) — двобітне число. Сусідні стани різняться РІВНО одним бітом (код Грея):\n"
                                  "стрибок «через клітину» (напр. 11→00) неможливий чистим обертом — це брязкіт, автомат його ігнорує.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(W / 2, 570, "Брязкіт лише смикає код туди-сюди між двома сусідніми станами — обхід кільця не завершується,\n"
                                  "тож зайвого кроку не буде. Дебаунс тут «вбудований» у саму структуру переходів.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "state-ring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_quadrature()
    fig_ky040_schematic()
    fig_ky040_wiring()
    fig_state_ring()
    print("KY-040 figs done ->", IMG)
