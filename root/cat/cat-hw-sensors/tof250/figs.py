# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «TOF250 — лазерний далекомір».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Принцип часу прольоту: імпульс туди і назад ────────────────────────────
def fig_tof_principle():
    W, H = 900, 430
    f = [text(W / 2, 32, "Далекомір міряє ЧАС, а не саму відстань", size=17, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 60, 150, 130, 130
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 52, "TOF250", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 74, "лазер + приймач", size=9.5, color=MUTED))

    # стіна праворуч (ціль)
    wx = 720
    f.append(rect(wx, 110, 26, 210, fill="#e9e2d0", stroke=INK, sw=1.6, rx=4))
    f.append(text(wx + 13, 340, "ціль", size=11, color=INK))

    # промінь туди (червоний, вниз-косо) і назад (синій)
    y_out = my + 40
    y_back = my + 92
    f.append(arrow(mx + mw, y_out, wx, y_out, color=POS, sw=2.6))
    f.append(text((mx + mw + wx) / 2, y_out - 12, "спалах світла летить до цілі  (940 нм, невидимий)",
                  size=11.5, color=POS, bold=True))
    f.append(arrow(wx, y_back, mx + mw, y_back, color=NEG, sw=2.6))
    f.append(text((mx + mw + wx) / 2, y_back + 22, "відбитий спалах повертається",
                  size=11.5, color=NEG, bold=True))

    # формула-рамка внизу
    b, bw, bh = textbox(W / 2, H - 46,
                        ["світло долає ВДВІЧІ більший шлях: туди й назад",
                         "відстань = швидкість світла × час ÷ 2  =  c · t / 2"],
                        size=13, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "tof-principle.svg"), W, H, *f)


# ── 2. Що всередині: VCSEL + SPAD + МК → два канали виводу ────────────────────
def fig_inside():
    W, H = 900, 470
    f = [text(W / 2, 30, "Усередині: давач ST + власний мікроконтролер",
              size=17, bold=True)]

    # блок оптики зліва
    ox, oy, ow, oh = 60, 90, 200, 300
    f.append(rect(ox, oy, ow, oh, fill="#fafbfc", stroke=MUTED, sw=1.7, rx=12))
    f.append(text(ox + ow / 2, oy + 24, "чип ST (клас VL53L0X)", size=11.5, bold=True))
    # VCSEL
    f.append(rect(ox + 24, oy + 54, ow - 48, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(ox + ow / 2, oy + 78, "VCSEL-лазер 940 нм", size=11, color=POS, bold=True))
    f.append(text(ox + ow / 2, oy + 96, "невидимий спалах", size=9.5, color=MUTED))
    # SPAD
    f.append(rect(ox + 24, oy + 132, ow - 48, 60, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    f.append(text(ox + ow / 2, oy + 156, "SPAD-матриця", size=11, color=NEG, bold=True))
    f.append(text(ox + ow / 2, oy + 174, "лічить фотони, що вернулись", size=9, color=MUTED))
    # таймер
    f.append(rect(ox + 24, oy + 210, ow - 48, 54, fill=BG, stroke=INK, sw=1.5, rx=8))
    f.append(text(ox + ow / 2, oy + 232, "таймер: скільки летіло", size=10.5, bold=True))
    f.append(text(ox + ow / 2, oy + 250, "→ сира відстань", size=9.5, color=MUTED))

    # МК у центрі
    cx, cy, cw2, ch2 = 340, 150, 180, 180
    f.append(rect(cx, cy, cw2, ch2, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=12))
    f.append(text(cx + cw2 / 2, cy + 30, "власний МК", size=12.5, bold=True, color=FIELD))
    f.append(text(cx + cw2 / 2, cy + 54, "модуля", size=10.5, color=FIELD))
    f.append(text(cx + cw2 / 2, cy + 90, "фільтрує, усереднює,", size=10, color=INK))
    f.append(text(cx + cw2 / 2, cy + 108, "перекладає в міліметри,", size=10, color=INK))
    f.append(text(cx + cw2 / 2, cy + 126, "віддає готове число", size=10, color=INK))
    # стрілка оптика → МК
    f.append(arrow(ox + ow, oy + oh / 2, cx, cy + ch2 / 2, color=INK, sw=2.0))

    # два канали виводу праворуч
    i2c_y = 165
    uart_y = 300
    f.append(rect(640, i2c_y - 34, 210, 68, fill=BG, stroke=NEG, sw=1.7, rx=10))
    f.append(text(745, i2c_y - 12, "I2C  (адреса 0x52)", size=11.5, bold=True, color=NEG))
    f.append(text(745, i2c_y + 8, "регістр 0x00 → 2 байти", size=10, color=INK))
    f.append(text(745, i2c_y + 24, "старший·молодший = мм", size=9, color=MUTED))

    f.append(rect(640, uart_y - 34, 210, 68, fill=BG, stroke=POS, sw=1.7, rx=10))
    f.append(text(745, uart_y - 12, "UART  115200 8N1", size=11.5, bold=True, color=POS))
    f.append(text(745, uart_y + 8, "текст ASCII: «748mm»", size=10, color=INK))
    f.append(text(745, uart_y + 24, "сам шле щомиті", size=9, color=MUTED))

    f.append(arrow(cx + cw2, cy + 40, 640, i2c_y, color=NEG, sw=2.0))
    f.append(arrow(cx + cw2, cy + ch2 - 40, 640, uart_y, color=POS, sw=2.0))

    b, bw, bh = textbox(W / 2, H - 24,
                        "МК ховає всю фізику: назовні виходить готова відстань у міліметрах — двома різними шляхами",
                        size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 3. Розводка пін-у-пін: шість дротів, два способи ──────────────────────────
def fig_wiring():
    W, H = 900, 500
    f = [text(W / 2, 30, "Шість контактів: живлення + два способи спілкування",
              size=17, bold=True)]

    # модуль ліворуч з шістьма кольоровими виводами
    mx, my, mw, mh = 60, 90, 190, 340
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=INK, sw=1.8, rx=12))
    f.append(text(mx + mw / 2, my + 26, "TOF250", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 44, "6-піновий роз'єм", size=9.5, color=MUTED))

    pins = [
        ("GND", "чорний", INK, my + 84),
        ("VCC", "червоний", POS, my + 128),
        ("RX", "жовтий", "#b8860b", my + 172),
        ("TX", "білий", MUTED, my + 216),
        ("SDA", "синій", NEG, my + 260),
        ("SCL", "зелений", FIELD, my + 304),
    ]
    for nm, colour, col, y in pins:
        f.append(circle(mx + mw - 16, y, 7, fill=col, stroke=col, sw=1))
        f.append(text(mx + mw - 34, y + 5, nm, size=11.5, bold=True, color=col, anchor="end"))
        f.append(text(mx + 14, y + 5, colour, size=9.5, color=MUTED, anchor="start"))

    # МК праворуч
    kx, ky, kw, kh = 620, 90, 220, 340
    f.append(rect(kx, ky, kw, kh, fill="#eef2f8", stroke=INK, sw=1.8, rx=12))
    f.append(text(kx + kw / 2, ky + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(kx + kw / 2, ky + 44, "ESP32 / Arduino / STM32", size=9, color=MUTED))
    mk = [
        ("3V3 / 5V", POS, ky + 84),
        ("GND", INK, ky + 128),
        ("TX →", "#b8860b", ky + 172),
        ("← RX", MUTED, ky + 216),
        ("SDA", NEG, ky + 260),
        ("SCL", FIELD, ky + 304),
    ]
    for nm, col, y in mk:
        f.append(text(kx + 16, y + 5, nm, size=11.5, bold=True, color=col, anchor="start"))

    # проводка: живлення (2)
    f.append(line(mx + mw, my + 84, kx, ky + 128, color=INK, sw=1.6, dash="5 4"))   # GND→GND
    f.append(line(mx + mw, my + 128, kx, ky + 84, color=POS, sw=2.2))               # VCC→3V3/5V

    # UART-хрест: RX модуля ← TX МК; TX модуля → RX МК
    f.append(line(mx + mw, my + 172, kx, ky + 172, color="#b8860b", sw=2.2))        # RX(мод)–TX(МК)
    f.append(line(mx + mw, my + 216, kx, ky + 216, color=MUTED, sw=2.2))            # TX(мод)–RX(МК)
    f.append(text((mx + mw + kx) / 2, my + 150, "UART: навхрест TX↔RX", size=11, color="#b8860b", bold=True))

    # I2C-пара
    f.append(line(mx + mw, my + 260, kx, ky + 260, color=NEG, sw=2.2))
    f.append(line(mx + mw, my + 304, kx, ky + 304, color=FIELD, sw=2.2))
    f.append(text((mx + mw + kx) / 2, my + 336, "I2C: SDA↔SDA, SCL↔SCL", size=11, color=NEG, bold=True))

    b, bw, bh = textbox(W / 2, H - 24,
                        "живлення завжди; далі ОБИРАЙ одне — або пара UART (TX↔RX навхрест), або пара I2C (SDA/SCL прямо)",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. UART-кадр: як розбирати потік «748mm\r\n» ──────────────────────────────
def fig_uart_stream():
    W, H = 900, 470
    f = [text(W / 2, 30, "UART-потік: синхронізуйся по кінцю рядка", size=17, bold=True)]

    # стрічка байтів одного кадру
    cells = [
        ("'7'", "цифра", NEG),
        ("'4'", "цифра", NEG),
        ("'8'", "цифра", NEG),
        ("'m'", "пропуск", MUTED),
        ("'m'", "пропуск", MUTED),
        ("\\r", "код 13", "#b8860b"),
        ("\\n", "код 10", POS),
    ]
    n = len(cells)
    cw, ch = 92, 62
    x0 = (W - n * cw) / 2
    y0 = 92
    f.append(text(W / 2, y0 - 16, "модуль шле безперервно, байт за байтом  →", size=11.5, color=MUTED))
    for i, (ch_s, role, col) in enumerate(cells):
        x = x0 + i * cw
        f.append(rect(x, y0, cw - 8, ch, fill=BG, stroke=col, sw=1.8, rx=8))
        f.append(text(x + (cw - 8) / 2, y0 + 30, ch_s, size=18, bold=True, color=col))
        f.append(text(x + (cw - 8) / 2, y0 + 50, role, size=9.5, color=MUTED))

    # дужка «число» під трьома цифрами
    bx1 = x0
    bx2 = x0 + 3 * cw - 8
    by = y0 + ch + 22
    f.append(line(bx1, by, bx2, by, color=NEG, sw=2))
    f.append(line(bx1, by, bx1, by - 8, color=NEG, sw=2))
    f.append(line(bx2, by, bx2, by - 8, color=NEG, sw=2))
    f.append(text((bx1 + bx2) / 2, by + 20, "накопичуємо цифри у буфер", size=11.5, color=NEG, bold=True))

    # маркер «тут рядок готовий» під \n
    nx = x0 + 6 * cw + (cw - 8) / 2
    f.append(line(nx, y0 + ch, nx, y0 + ch + 40, color=POS, sw=2))
    f.append(text(nx, y0 + ch + 58, "\\n → рядок готовий:", size=11.5, color=POS, bold=True))
    f.append(text(nx, y0 + ch + 76, "748 → у число, буфер чистимо", size=11, color=POS))

    # застереження про обрубок
    b1, w1, h1 = textbox(W / 2, 330,
                         ["Спіймали потік із СЕРЕДИНИ? Перший рядок — обрубок:",
                          "'4' '8' 'm' 'm' \\n  →  прочитається як 48, а не 748."],
                         size=12.5, fill="#fdecea", stroke=POS)
    f.append(b1)

    b2, w2, h2 = textbox(W / 2, H - 40,
                         ["Тому НЕ віримо числу, поки не побачили \\n.",
                          "Синхронізація по роздільнику, а не по довжині → кожне число ціле."],
                         size=12.5, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "uart-stream.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tof_principle()
    fig_inside()
    fig_wiring()
    fig_uart_stream()
    print("OK: 4 figures ->", IMG)
