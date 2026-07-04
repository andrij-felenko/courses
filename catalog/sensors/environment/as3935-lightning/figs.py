# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «DFRobot SEN0290 (AS3935) — давач блискавок».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ланцюг чуття: розряд → радіоімпульс → антена → IC → відстань ────────────
def fig_sensing_chain():
    W, H = 900, 380
    f = [text(W / 2, 30, "Що вимірює модуль: не світло й не грім, а радіоімпульс розряду",
              size=15, bold=True)]

    # блискавка ліворуч
    lx, ly = 70, 150
    f.append(text(lx, ly - 30, "розряд", size=11, color=POS, bold=True))
    # зигзаг блискавки
    zig = [(lx, ly), (lx - 14, ly + 26), (lx + 8, ly + 34), (lx - 8, ly + 66)]
    for i in range(len(zig) - 1):
        f.append(line(zig[i][0], zig[i][1], zig[i + 1][0], zig[i + 1][1], color=POS, sw=3))
    f.append(text(lx, ly + 96, "струм 30 кА", size=9.5, color=MUTED))
    f.append(text(lx, ly + 112, "за мікросекунди", size=9.5, color=MUTED))

    # радіохвиля (концентричні дуги) до антени
    wx = 200
    for r in (34, 58, 82):
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (wx, ly - r, r, r, wx, ly + r, NEG))
    f.append(text(wx + 18, ly - 60, "радіоімпульс", size=10.5, color=NEG, bold=True))
    f.append(text(wx + 18, ly - 44, "~ 500 кГц", size=10, color=NEG))

    # антена (котушка) — приймач
    ax, ay, aw, ah = 320, 108, 150, 96
    f.append(rect(ax, ay, aw, ah, fill="#eaf0fd", stroke=NEG, sw=1.9, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "антена-котушка", size=11.5, bold=True, color=NEG))
    f.append(text(ax + aw / 2, ay + 44, "Coilcraft MA5532", size=9.5, color=MUTED))
    # символ котушки
    cy = ay + 72
    for k in range(4):
        cx0 = ax + 34 + k * 22
        f.append('<path d="M %.1f %.1f a 8 8 0 1 1 16 0" fill="none" stroke="%s" stroke-width="2"/>'
                 % (cx0, cy, NEG))
    f.append(line(ax + 28, cy, ax + 34, cy, color=NEG, sw=2))
    f.append(line(ax + 34 + 4 * 22 - 6, cy, ax + aw - 22, cy, color=NEG, sw=2))

    # стрілка антена → IC
    f.append(arrow(ax + aw, ay + ah / 2, 520, ay + ah / 2, color=INK, sw=2.0))

    # мікросхема AS3935
    ix, iy, iw, ih = 522, 92, 178, 128
    f.append(rect(ix, iy, iw, ih, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(ix + iw / 2, iy + 26, "AS3935", size=13, bold=True, color=FIELD))
    f.append(text(ix + iw / 2, iy + 46, "підсилювач + алгоритм", size=9.5, color=MUTED))
    f.append(text(ix + iw / 2, iy + 74, "відсіює завади,", size=10, color=INK))
    f.append(text(ix + iw / 2, iy + 92, "рахує енергію", size=10, color=INK))
    f.append(text(ix + iw / 2, iy + 110, "оцінює відстань", size=10, color=INK, italic=True))

    # стрілка IC → результат
    f.append(arrow(ix + iw, iy + ih / 2, 760, iy + ih / 2, color=INK, sw=2.0))

    # результат
    rx, ry, rw, rh = 762, 100, 118, 112
    f.append(rect(rx, ry, rw, rh, fill="#fdecea", stroke=POS, sw=1.9, rx=10))
    f.append(text(rx + rw / 2, ry + 26, "число", size=11.5, bold=True, color=POS))
    f.append(text(rx + rw / 2, ry + 54, "до 40 км", size=13, color=INK, bold=True))
    f.append(text(rx + rw / 2, ry + 76, "у 15 сходинок", size=9.5, color=MUTED))
    f.append(text(rx + rw / 2, ry + 96, "+ енергія", size=10, color=INK))

    b, _, _ = textbox(W / 2, 356,
                      "око бачить спалах, вухо чує грім — а модуль ловить радіочастину розряду й одразу дає оцінку відстані до фронту грози",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "sensing-chain.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: SEN0290 ↔ мікроконтролер ───────────────────────────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 30, "Підключення пін-у-пін: живлення, дві лінії I²C і окремий провід переривання",
              size=14.5, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 60, 80, 250, 320
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=2, rx=12))
    f.append(text(mx + mw / 2, my + 28, "SEN0290", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 47, "Gravity-роз'єм + штирі", size=10, color=MUTED))
    # PWR-світлодіод
    f.append(circle(mx + mw - 26, my + 24, 6, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(mx + mw - 26, my + 44, "PWR", size=8, color=POS))
    # DIP-перемикач адреси
    f.append(rect(mx + 20, my + 62, 74, 26, fill=BG, stroke=MUTED, sw=1.4, rx=4))
    f.append(text(mx + 20 + 37, my + 79, "ADDR DIP", size=9, color=MUTED))

    # піни модуля (праворуч на модулі)
    pins = [("VCC", POS, "3.3–5.5 В"),
            ("GND", INK, "спільна земля"),
            ("SCL", NEG, "такт I²C"),
            ("SDA", NEG, "дані I²C"),
            ("IRQ", FIELD, "переривання")]
    py0 = my + 118
    step = 52
    pin_x = mx + mw            # правий край модуля
    for i, (name, col, _) in enumerate(pins):
        yy = py0 + i * step
        f.append(circle(pin_x, yy, 7, fill=BG, stroke=col, sw=2.2))
        f.append(text(pin_x - 20, yy + 4, name, size=11, color=col, bold=True, anchor="end"))

    # мікроконтролер праворуч
    cx, cy, cw, ch = 610, 80, 230, 320
    f.append(rect(cx, cy, cw, ch, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(cx + cw / 2, cy + 28, "мікроконтролер", size=13, bold=True, color=FIELD))
    f.append(text(cx + cw / 2, cy + 47, "ESP32 / Arduino / Pi", size=10, color=MUTED))

    cpins = [("3V3", POS),
             ("GND", INK),
             ("SCL / GPIO22", NEG),
             ("SDA / GPIO21", NEG),
             ("GPIO (вхід)", FIELD)]
    cpin_x = cx
    for i, (name, col) in enumerate(cpins):
        yy = py0 + i * step
        f.append(circle(cpin_x, yy, 7, fill=BG, stroke=col, sw=2.2))
        f.append(text(cpin_x + 20, yy + 4, name, size=10.5, color=col, bold=True, anchor="start"))

    # дроти пін→пін, кожен веде рівно, з підписом посередині у чистій смузі
    notes = ["живлення", "0 В", "підтяжка до VCC", "підтяжка до VCC", "тільки читання"]
    for i, note in enumerate(notes):
        yy = py0 + i * step
        col = pins[i][1]
        f.append(line(pin_x + 7, yy, cpin_x - 7, yy, color=col, sw=2.2))
        f.append(text((pin_x + cpin_x) / 2, yy - 9, note, size=9, color=col, italic=True))

    # підказка про підтяжки I²C
    b1, _, _ = textbox(W / 2, 432,
                       "SDA і SCL — з підтяжками ~4.7 кΩ до VCC (на Gravity-модулі вони вже стоять); IRQ активний ВИСОКИЙ — заводимо на звичайний вхід GPIO",
                       size=10.5, fill=FILL, stroke=LINE)
    f.append(b1)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Рукостискання переривання: IRQ → пауза → читання причини → гілка ────────
def fig_irq_flow():
    W, H = 880, 430
    f = [text(W / 2, 30, "Рукостискання: пін смикнувся вгору — код чекає, читає причину, розгалужується",
              size=14, bold=True)]

    # крок 1 — подія на IRQ
    def box(cx, top, w, h, title, lines, col, fill):
        f.append(rect(cx - w / 2, top, w, h, fill=fill, stroke=col, sw=1.9, rx=10))
        f.append(text(cx, top + 24, title, size=12, bold=True, color=col))
        yy = top + 46
        for ln in lines:
            f.append(text(cx, yy, ln, size=10, color=INK))
            yy += 18

    box(140, 62, 200, 96, "1 · IRQ ↑", ["чіп підняв пін", "МК будиться", "по фронту"], FIELD, "#eef6ef")

    f.append(arrow(240, 110, 300, 110, color=INK, sw=2.2))

    box(430, 62, 220, 96, "2 · пауза ~2 мс", ["чіп ще досипає", "статистику;", "читати рано — брехня"], NEG, "#eaf0fd")

    f.append(arrow(540, 110, 600, 110, color=INK, sw=2.2))

    box(730, 62, 200, 96, "3 · читаємо 0x03", ["беремо біти INT[3:0]", "— причину події", "в одному байті"], INK, FILL)

    # вниз від кроку 3 до розгалуження
    f.append(arrow(730, 158, 730, 196, color=INK, sw=2.2))
    f.append(line(730, 210, 150, 210, color=MUTED, sw=1.6))
    f.append(line(150, 210, 150, 238, color=MUTED, sw=1.6))
    f.append(line(450, 210, 450, 238, color=MUTED, sw=1.6))
    f.append(line(730, 210, 730, 238, color=MUTED, sw=1.6))

    # три гілки за значенням
    def branch(cx, code, name, note, col, fill):
        w, h = 240, 120
        top = 240
        f.append(rect(cx - w / 2, top, w, h, fill=fill, stroke=col, sw=1.9, rx=10))
        f.append(text(cx, top + 24, code, size=13, bold=True, color=col))
        f.append(text(cx, top + 46, name, size=11.5, color=INK, bold=True))
        yy = top + 68
        for ln in note:
            f.append(text(cx, yy, ln, size=9.5, color=MUTED))
            yy += 16

    branch(150, "0x01", "шум зависокий", ["поріг шуму мал.", "→ підняти рівень", "або перенести давач"], NEG, "#eaf0fd")
    branch(450, "0x04", "завада (disturber)", ["техніка поруч", "→ маскувати", "або ігнорувати"], MUTED, FILL)
    branch(730, "0x08", "БЛИСКАВКА", ["читай 0x07 — км", "і 0x04–0x06 —", "енергію розряду"], POS, "#fdecea")

    b, _, _ = textbox(W / 2, 410,
                      "один і той самий пін IRQ означає три різні речі — саме байт 0x03 каже, ЩО сталося; діяти можна лише прочитавши його",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "irq-flow.svg"), W, H, *f)


# ── 4. Калібрувальний перебір: 16 ємностей → міряй LCO → лиши найближчу ────────
def fig_cal_sweep():
    W, H = 900, 470
    f = [text(W / 2, 30, "Калібрування антени: перебираємо 16 ємностей, міряємо частоту LCO, лишаємо найближчу до 500 кГц",
              size=13.5, bold=True)]

    # ліворуч — цикл-петля
    lx, ly, lw, lh = 60, 78, 300, 300
    f.append(rect(lx, ly, lw, lh, fill=FILL, stroke=LINE, sw=1.6, rx=12))
    f.append(text(lx + lw / 2, ly + 26, "для tune = 0 … 15:", size=12.5, bold=True, color=INK))
    steps = [
        ("setTuningCaps(tune·8)", "додаємо tune·8 пФ до антени", NEG),
        ("setIRQOutputSource(3)", "вивести LCO на пін IRQ", FIELD),
        ("міряємо частоту на IRQ", "рахуємо фронти за час", INK),
        ("|f − 500 кГц| менша?", "запам'ятати цю tune", POS),
    ]
    yy = ly + 58
    for i, (a, b, col) in enumerate(steps):
        f.append(circle(lx + 30, yy + 6, 11, fill=BG, stroke=col, sw=2))
        f.append(text(lx + 30, yy + 10, str(i + 1), size=11, bold=True, color=col))
        f.append(text(lx + 52, yy + 2, a, size=11, color=col, bold=True, anchor="start"))
        f.append(text(lx + 52, yy + 20, b, size=9.5, color=MUTED, anchor="start"))
        yy += 56
    # стрілка «назад у цикл»
    f.append('<path d="M %.1f %.1f q -26 0 -26 -%.1f q 0 -%.1f 20 -%.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (lx + 24, yy - 40, (yy - 40 - (ly + 64)) / 2, (yy - 40 - (ly + 64)) / 2, (yy - 40 - (ly + 64)) / 2, MUTED))

    # праворуч — стовпчики «промах від 500 кГц» для кількох tune
    gx, gy, gw, gh = 430, 96, 410, 250
    f.append(text(gx + gw / 2, gy - 8, "промах частоти LCO від 500 кГц (менше — краще)", size=11, color=INK, bold=True))
    base = gy + gh
    f.append(line(gx, base, gx + gw, base, color=INK, sw=1.6))          # вісь X
    f.append(line(gx, gy, gx, base, color=INK, sw=1.6))                  # вісь Y
    # умовні промахи (кГц) для tune 0..7 з мінімумом на tune=5
    misses = [46, 33, 22, 14, 7, 2, 9, 18]
    n = len(misses)
    slot = gw / n
    best = misses.index(min(misses))
    for i, m in enumerate(misses):
        bh = m / 50.0 * (gh - 20)
        bx = gx + i * slot + slot * 0.22
        bw = slot * 0.56
        col = FIELD if i == best else NEG
        fill = "#eafaf0" if i == best else "#eaf0fd"
        f.append(rect(bx, base - bh, bw, bh, fill=fill, stroke=col, sw=1.8, rx=3))
        f.append(text(bx + bw / 2, base + 16, str(i), size=10, color=col, bold=(i == best)))
        if i == best:
            f.append(text(bx + bw / 2, base - bh - 10, "лишаємо", size=9.5, color=FIELD, bold=True))
    f.append(text(gx + gw / 2, base + 34, "значення tune (кожне = +8 пФ ємності)", size=9.5, color=MUTED))
    # пунктир «ціль 0»
    f.append(line(gx, base, gx + gw, base, color=FIELD, sw=1.2, dash="4 4"))

    b, _, _ = textbox(W / 2, 432,
                      "manualCal робить це перебором усередині; після нього LCO прибирають з піна (setIRQOutputSource(0)), інакше IRQ смикатиметься 500 000 разів за секунду",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "cal-sweep.svg"), W, H, *f)


# ── 5. Пастка 1/4/8 → 1/2/3: сирий регістр проти того, що віддає бібліотека ────
def fig_intsrc_map():
    W, H = 900, 430
    f = [text(W / 2, 30, "Головна пастка коду: сирі біти регістра 0x03 — це 8/4/1, а getInterruptSrc() віддає 1/2/3",
              size=13.5, bold=True)]

    # ліва колонка — сирий регістр чіпа
    lx, ly, lw = 70, 84, 330
    f.append(rect(lx, ly, lw, 288, fill="#eaf0fd", stroke=NEG, sw=1.9, rx=12))
    f.append(text(lx + lw / 2, ly + 26, "сирий регістр чіпа 0x03", size=12.5, bold=True, color=NEG))
    f.append(text(lx + lw / 2, ly + 45, "молодші 4 біти INT[3:0]", size=10, color=MUTED))
    raw = [("0b1000  = 8", "блискавка (INT_L)", POS),
           ("0b0100  = 4", "завада (INT_D)", MUTED),
           ("0b0001  = 1", "шум зависокий (INT_NH)", NEG)]
    yy = ly + 76
    for code, name, col in raw:
        f.append(rect(lx + 20, yy, lw - 40, 52, fill=BG, stroke=col, sw=1.6, rx=8))
        f.append(text(lx + 40, yy + 22, code, size=12, color=col, bold=True, anchor="start", ))
        f.append(text(lx + 40, yy + 40, name, size=10, color=INK, anchor="start"))
        yy += 66

    # права колонка — що віддає бібліотека
    rx, ryy, rw = 500, 84, 330
    f.append(rect(rx, ryy, rw, 288, fill="#eafaf0", stroke=FIELD, sw=1.9, rx=12))
    f.append(text(rx + rw / 2, ryy + 26, "getInterruptSrc() у DFRobot", size=12.5, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, ryy + 45, "перекодовує в маленькі числа", size=10, color=MUTED))
    lib = [("повертає 1", "блискавка", POS),
           ("повертає 2", "завада", MUTED),
           ("повертає 3", "шум зависокий", NEG)]
    yy2 = ryy + 76
    for code, name, col in lib:
        f.append(rect(rx + 20, yy2, rw - 40, 52, fill=BG, stroke=col, sw=1.6, rx=8))
        f.append(text(rx + 40, yy2 + 22, code, size=12, color=col, bold=True, anchor="start"))
        f.append(text(rx + 40, yy2 + 40, name, size=10, color=INK, anchor="start"))
        yy2 += 66

    # стрілки-перекодування між колонками
    ya = ly + 76 + 26
    for k in range(3):
        f.append(arrow(lx + lw + 4, ya + k * 66, rx - 4, ya + k * 66, color=INK, sw=2))
    f.append(text(W / 2, ya - 22, "перекодування", size=10, color=INK, bold=True))
    f.append(text(W / 2, ya - 7, "8→1, 4→2, 1→3", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 404,
                      "тому в скетчі порівнюй саме з 1/2/3 (те, що дає бібліотека), а не з 8/4/1; звірка з 8 «нічого не спіймає», хоч блискавка й була",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "intsrc-map.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sensing_chain()
    fig_wiring()
    fig_irq_flow()
    fig_cal_sweep()
    fig_intsrc_map()
    print("OK: 5 figures ->", IMG)
