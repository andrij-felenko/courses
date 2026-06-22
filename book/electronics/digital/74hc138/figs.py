# -*- coding: utf-8 -*-
"""Фігури до теми «74HC138».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Розпіновка + що всередині: адреса 011 → у нуль падає лише Y3 ───────────
# Ідея: показати три групи ніжок (адреса, дозволи, виходи) і головну пастку —
# виходи активні-низькі. Конкретний приклад 011=3 робить таблицю наочною.
def fig_pinout():
    W, H = 760, 430
    f = []

    # корпус мікросхеми
    cx0, cy0, cw, ch = 300, 70, 160, 300
    f.append(rect(cx0, cy0, cw, ch, fill="#f4f6f8", stroke=LINE, sw=2, rx=10))
    f.append(text(cx0 + cw / 2, cy0 + 26, "74HC138", size=15, bold=True, color=INK))
    f.append(text(cx0 + cw / 2, cy0 + 44, "дешифратор 3→8", size=10.5, color=MUTED))

    # ── ліворуч: адресні входи (задаємо 011 = 3) ──
    addr = [("A0", "1"), ("A1", "1"), ("A2", "0")]
    ay = cy0 + 78
    for i, (name, bit) in enumerate(addr):
        y = ay + i * 26
        f.append(line(cx0 - 80, y, cx0, y, color=NEG, sw=2))
        f.append(text(cx0 - 86, y + 4, name, size=12, color=NEG, bold=True, anchor="end"))
        f.append(circle(cx0 - 50, y, 9, fill="#eaf0fd", stroke=NEG, sw=1.6))
        f.append(text(cx0 - 50, y + 4, bit, size=11, color=NEG, bold=True))
    f.append(text(cx0 - 64, ay - 16, "адреса = 011 → 3", size=10.5, color=NEG, anchor="middle"))

    # ── ліворуч нижче: три дозволи ──
    en = [("E1", "0", "↓"), ("E2", "0", "↓"), ("E3", "1", "↑")]
    ey = cy0 + 190
    for i, (name, bit, mark) in enumerate(en):
        y = ey + i * 26
        f.append(line(cx0 - 80, y, cx0, y, color=MUTED, sw=2))
        f.append(text(cx0 - 86, y + 4, name + " " + mark, size=11, color=MUTED, anchor="end"))
        f.append(circle(cx0 - 50, y, 9, fill=FILL, stroke=MUTED, sw=1.5))
        f.append(text(cx0 - 50, y + 4, bit, size=11, color=INK, bold=True))
    f.append(text(cx0 - 64, ey - 14, "дозволи: 0·0·1 → чип увімкнено", size=9.5, color=MUTED, anchor="middle"))

    # ── праворуч: вісім виходів, активні-низькі; обраний Y3 = 0 ──
    oy = cy0 + 40
    for i in range(8):
        y = oy + i * 30
        active = (i == 3)
        col = POS if active else MUTED
        f.append(line(cx0 + cw, y, cx0 + cw + 26, y, color=col, sw=2 if active else 1.6))
        # кружок-інверсія на виході
        f.append(circle(cx0 + cw + 33, y, 6, fill=BG, stroke=col, sw=1.6))
        f.append(line(cx0 + cw + 39, y, cx0 + cw + 60, y, color=col, sw=2 if active else 1.6))
        val = "0" if active else "1"
        f.append(text(cx0 + cw + 70, y + 4, "Y%d = %s" % (i, val), size=11,
                      color=col, bold=active, anchor="start"))
    f.append(text(cx0 + cw + 95, oy - 22, "виходи активні-низькі", size=10, color=INK))

    # підсумкова рамка внизу
    b = fitbox(150, 388, 460, 34,
               "Усередині — дешифратор 3→8. Обраний вихід падає в 0, решта сім стоять у 1",
               size=11, fill="#fdecea", stroke=POS, sw=1.4)
    f.append(b)

    render(os.path.join(IMG, "pinout.svg"), W, H, *f)


# ── 2. Вибір кристала: 3 піни МК → 8 ліній ~CS на спільній шині ───────────────
# Ідея: інверсні виходи дешифратора лягають просто на інверсні ~CS — без вентилів.
# Адреса 010=2 → у нуль падає лише ~CS2, слухає пристрій 2; шина даних спільна.
def fig_chip_select():
    W, H = 760, 380
    f = []

    # МК ліворуч
    f.append(rect(40, 120, 120, 150, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(100, 150, "МК", size=13, color=NEG, bold=True))
    f.append(text(100, 172, "3 GPIO", size=11, color=INK, bold=True))
    f.append(text(100, 192, "A0 A1 A2", size=10, color=MUTED))
    f.append(text(100, 214, "= 010", size=11, color=NEG, bold=True))

    # три лінії адреси до дешифратора
    for i in range(3):
        y = 200 + i * 14
        f.append(line(160, y, 250, y, color=NEG, sw=1.8))

    # дешифратор
    f.append(rect(250, 110, 150, 170, fill="#f4f6f8", stroke=LINE, sw=2, rx=10))
    f.append(text(325, 138, "74HC138", size=12.5, bold=True, color=INK))
    f.append(text(325, 156, "3 → 8", size=10.5, color=MUTED))

    # вісім виходів ~CS до восьми пристроїв; CS2 активний
    dev_x = 560
    for i in range(8):
        y = 122 + i * 28
        active = (i == 2)
        col = POS if active else MUTED
        f.append(line(400, y, 470, y, color=col, sw=2 if active else 1.4))
        f.append(circle(477, y, 5, fill=BG, stroke=col, sw=1.5))  # інверсія
        f.append(line(484, y, dev_x - 20, y, color=col, sw=2 if active else 1.4))
        val = "0" if active else "1"
        # маленький блок-пристрій
        f.append(rect(dev_x - 20, y - 10, 150, 20,
                      fill="#fdecea" if active else BG,
                      stroke=col, sw=1.6 if active else 1.2, rx=4))
        label = "пристрій %d  ~CS=%s" % (i, val)
        if active:
            label = "пристрій 2  ~CS=0  слухає"
        f.append(text(dev_x - 12, y + 4, label, size=9.5,
                      color=col, bold=active, anchor="start"))

    # спільна шина даних знизу (паралельно до всіх)
    f.append(line(160, 320, dev_x + 130, 320, color=FIELD, sw=2))
    f.append(text(180, 314, "SCK · MOSI · MISO — спільні для всіх", size=10.5,
                  color=FIELD, bold=True, anchor="start"))
    for i in range(8):
        y = 122 + i * 28
        f.append(line(dev_x + 55, min(y + 10, 320), dev_x + 55, 320, color=FIELD, sw=1))

    b = fitbox(150, 348, 460, 28,
               "Три піни МК керують вісьмома вибірками: дешифратор сам опускає потрібний ~CS у 0",
               size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)

    render(os.path.join(IMG, "chip-select.svg"), W, H, *f)


# ── 3. Каскад: дві мікросхеми → дешифратор 4→16 без жодного вентиля ───────────
# Ідея: четвертий, старший біт A3 і його інверсія керують дозволами E двох чипів;
# у кожен момент дозволено рівно один чип — разом виходить 1 з 16.
def fig_cascade():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 36,
                  "Старший біт A3 вмикає рівно один чип — два дешифратори дають 1 з 16",
                  size=12.5, color=MUTED, italic=True))

    # спільні молодші біти A0..A2
    f.append(rect(40, 150, 110, 90, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(95, 182, "A0 A1 A2", size=11, color=NEG, bold=True))
    f.append(text(95, 204, "(спільні)", size=10, color=MUTED))

    # верхній чип: A3=0 → дозволено (виходи 0..7)
    def chip(y0, label, out_lo, enabled, e_note):
        f.append(rect(260, y0, 150, 120, fill="#f4f6f8", stroke=LINE, sw=2, rx=10))
        f.append(text(335, y0 + 26, "74HC138", size=12, bold=True, color=INK))
        f.append(text(335, y0 + 44, label, size=10, color=MUTED))
        # дозвіл
        col = FIELD if enabled else MUTED
        f.append(text(335, y0 + 66, e_note, size=10, color=col, bold=enabled))
        f.append(text(335, y0 + 86, "виходи Y%d…Y%d" % (out_lo, out_lo + 7),
                      size=10, color=INK))
        state = "увімкнено" if enabled else "вимкнено → усі 1"
        f.append(text(335, y0 + 104, state, size=9.5, color=col, bold=enabled))
        # три спільні адресні лінії
        f.append(line(150, y0 + 60, 260, y0 + 60, color=NEG, sw=1.6))

    chip(70, "молодша вісімка", 0, True, "E3=1, бо A3=0 (через інвертор)")
    chip(220, "старша вісімка", 8, False, "E1=0, бо A3=0 → чип спить")

    # A3 і його інверсія керують дозволами
    f.append(rect(150, 320, 110, 50, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(205, 342, "A3 = 0", size=12, color=POS, bold=True))
    f.append(text(205, 360, "+ інвертор", size=9.5, color=MUTED))
    f.append(arrow(205, 320, 300, 195, color=POS, sw=1.6))
    f.append(arrow(205, 320, 300, 285, color=MUTED, sw=1.4))

    b = fitbox(430, 150, 300, 120,
               "4-в-16: дві мікросхеми, нуль додаткових вентилів.\n\n"
               "5-в-32: чотири мікросхеми й один інвертор.\n\n"
               "Дозволи E саме для цього й зроблені різнополярними.",
               size=10.5, fill="#fbfbfb", stroke=MUTED, sw=1.4)
    f.append(b)

    render(os.path.join(IMG, "cascade.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pinout()
    fig_chip_select()
    fig_cascade()
    print("OK: 3 figures ->", IMG)
