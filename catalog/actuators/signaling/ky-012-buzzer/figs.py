# -*- coding: utf-8 -*-
"""Фігури для статті KY-012 — активний зумер.
Дві SVG: (1) принципова схема плати (транзистор-ключ), (2) розводка пін-у-пін до МК.
Розкладка навмисне просторова — написи стоять поза чужими лініями й написами.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def schematic():
    """Принципова схема: S → 1к → база S8050; активний зумер між +V і колектором."""
    W, H = 820, 470
    f = []

    # --- вузли по сітці ---
    x_pin = 70          # вхідні контакти
    x_res = 210         # резистор
    x_base = 350        # база транзистора
    x_tr = 430          # тіло транзистора
    x_col = 560         # колектор/зумер (вертикаль)
    y_vcc = 70          # шина +V
    y_top = 130         # зумер
    y_sig = 175         # рівень сигналу S / бази
    y_tr = 250          # центр транзистора
    y_gnd = 380         # шина землі

    # шина +V
    f.append(line(x_col, y_vcc, W - 70, y_vcc, color=POS, sw=2.2))
    f.append(plus(x_col, y_vcc, 10))
    f.append(text(W - 70, y_vcc - 16, "+V  3.3–5 В", size=13, color=POS, bold=True, anchor="end"))

    # три контакти зліва
    f.append(circle(x_pin, y_sig, 11, fill="#eef2f6", stroke=INK, sw=1.6))
    f.append(text(x_pin, y_sig + 5, "S", size=15, bold=True))
    f.append(text(x_pin - 26, y_sig - 22, "сигнал", size=12, color=MUTED, anchor="start"))

    y_mid = 275
    f.append(circle(x_pin, y_mid, 11, fill="#f0f0f0", stroke=MUTED, sw=1.6))
    f.append(text(x_pin, y_mid + 5, "•", size=16, color=MUTED, bold=True))
    f.append(text(x_pin - 30, y_mid + 30, "середній — НЕ підключений", size=11.5, color=POS, anchor="start"))

    f.append(minus(x_pin, y_gnd, 11))
    f.append(text(x_pin - 26, y_gnd + 30, "земля", size=12, color=MUTED, anchor="start"))

    # S → резистор (база)
    f.append(line(x_pin + 11, y_sig, x_res, y_sig, color=INK, sw=1.8))
    f.append(rect(x_res, y_sig - 14, 80, 28, fill="#fff8e6", stroke=INK, sw=1.6, rx=4))
    f.append(text(x_res + 40, y_sig + 5, "1 кОм", size=13, bold=True))
    f.append(text(x_res + 40, y_sig - 26, "база-резистор", size=11, color=MUTED))

    # резистор → база (вниз до центру транзистора)
    f.append(line(x_res + 80, y_sig, x_base, y_sig, color=INK, sw=1.8))
    f.append(line(x_base, y_sig, x_base, y_tr, color=INK, sw=1.8))
    f.append(line(x_base, y_tr, x_tr - 30, y_tr, color=INK, sw=1.8))

    # транзистор S8050
    f.append(circle(x_tr, y_tr, 48, fill="#eef7ff", stroke=NEG, sw=2))
    f.append(text(x_tr, y_tr + 78, "S8050 · NPN-ключ", size=13, color=NEG, bold=True))
    # вертикальна пластина бази
    f.append(line(x_tr - 30, y_tr - 22, x_tr - 30, y_tr + 22, color=INK, sw=2.6))
    f.append(text(x_base - 16, y_tr - 8, "Б", size=12, bold=True, anchor="end"))
    # колектор (вгору-праворуч) → вертикаль до зумера
    f.append(line(x_tr - 8, y_tr - 16, x_col, y_tr - 40, color=INK, sw=2))
    f.append(line(x_col, y_tr - 40, x_col, y_top + 36, color=INK, sw=1.8))
    f.append(text(x_col + 16, y_tr - 34, "К", size=12, bold=True, anchor="start"))
    # емітер (вниз-праворуч) → земля
    f.append(line(x_tr - 8, y_tr + 16, x_col - 90, y_tr + 40, color=INK, sw=2))
    f.append(line(x_col - 90, y_tr + 40, x_col - 90, y_gnd, color=INK, sw=1.8))
    f.append(arrow(x_tr - 4, y_tr + 24, x_col - 90, y_tr + 40, color=INK, sw=1.5))
    f.append(text(x_col - 74, y_tr + 30, "Е", size=12, bold=True, anchor="start"))

    # активний зумер між +V і колектором
    f.append(circle(x_col, y_top, 34, fill="#f4f6f8", stroke=INK, sw=2))
    f.append(text(x_col, y_top + 6, "≈", size=24, bold=True))
    f.append(line(x_col, y_vcc, x_col, y_top - 34, color=POS, sw=1.8))
    # підпис зумера — праворуч, окремим блоком, подалі від ліній
    zx = x_col + 70
    f.append(text(zx, y_top - 16, "активний зумер", size=13, bold=True, anchor="start"))
    f.append(text(zx, y_top + 6, "власний генератор", size=11.5, color=MUTED, anchor="start"))
    f.append(text(zx, y_top + 24, "усередині → сам", size=11.5, color=MUTED, anchor="start"))
    f.append(text(zx, y_top + 42, "співає на ~2.5 кГц", size=11.5, color=MUTED, anchor="start"))

    # шина землі
    f.append(line(x_pin + 11, y_gnd, x_col - 90, y_gnd, color=NEG, sw=2.2))
    f.append(circle(x_col - 90, y_gnd, 3.5, fill=INK, stroke=INK, sw=1))

    render(os.path.join(IMG, 'schematic.svg'), W, H, *f,
           title="Що всередині KY-012: сигнал відкриває транзистор, зумер сам співає")


def wiring():
    """Розводка пін-у-пін: S → GPIO, − → GND, середній висить."""
    W, H = 760, 400
    f = []

    # --- модуль KY-012 (ліворуч) ---
    mx, my, mw, mh = 55, 95, 220, 210
    f.append(rect(mx, my, mw, mh, fill="#2f6fb0", stroke=INK, sw=2, rx=10))
    f.append(text(mx + mw / 2, my + 34, "KY-012", size=19, color="#ffffff", bold=True))
    f.append(text(mx + mw / 2, my + 58, "активний зумер", size=13, color="#dce8f5"))
    f.append(circle(mx + mw / 2, my + 135, 42, fill="#111", stroke="#000", sw=2))
    f.append(text(mx + mw / 2, my + 142, "♪", size=28, color="#8fb8e0"))

    # три штирі праворуч (порядок згори-вниз: −, середній, S; ключ — букви)
    pinx = mx + mw
    y_minus = my + 55
    y_mid = my + 105
    y_s = my + 155
    for (yy, lab, col) in [(y_minus, "−", NEG), (y_mid, "•", MUTED), (y_s, "S", INK)]:
        f.append(rect(pinx, yy - 9, 24, 18, fill="#d9b310", stroke=INK, sw=1.3, rx=3))
        f.append(text(pinx + 12, yy + 4, lab, size=13, color=col, bold=True))

    # --- плата МК (праворуч) ---
    cx, cy, cw, ch = 540, 95, 165, 210
    f.append(rect(cx, cy, cw, ch, fill="#0b6b3a", stroke=INK, sw=2, rx=10))
    f.append(text(cx + cw / 2, cy + 32, "плата МК", size=16, color="#ffffff", bold=True))
    f.append(text(cx + cw / 2, cy + 54, "Arduino / ESP32", size=12, color="#cfe8d8"))

    g_io = cy + 105
    g_gnd = cy + 165
    f.append(rect(cx - 24, g_io - 9, 24, 18, fill="#d9b310", stroke=INK, sw=1.3, rx=3))
    f.append(text(cx - 34, g_io + 4, "GPIO", size=13, color="#0b6b3a", bold=True, anchor="end"))
    f.append(rect(cx - 24, g_gnd - 9, 24, 18, fill="#d9b310", stroke=INK, sw=1.3, rx=3))
    f.append(text(cx - 34, g_gnd + 4, "GND", size=13, color="#0b6b3a", bold=True, anchor="end"))

    # --- дроти ---
    # S → GPIO (сигнал)
    f.append(line(pinx + 24, y_s, cx - 24, g_io, color=FIELD, sw=2.6))
    f.append(text((pinx + 24 + cx - 24) / 2, y_s + 26, "HIGH → пищить, LOW → тиша", size=12, color=FIELD, bold=True))
    # − → GND (веду низом, подалі від написів)
    wj = pinx + 60      # вузол повороту
    f.append(line(pinx + 24, y_minus, wj, y_minus, color=NEG, sw=2.6))
    f.append(line(wj, y_minus, wj, g_gnd + 22, color=NEG, sw=2.6))
    f.append(line(wj, g_gnd + 22, cx - 24, g_gnd + 22, color=NEG, sw=2.6))
    f.append(line(cx - 24, g_gnd + 22, cx - 24, g_gnd, color=NEG, sw=2.6))
    f.append(text(wj + 90, g_gnd + 38, "спільна земля", size=12, color=NEG, bold=True, anchor="start"))
    # середній висить
    f.append(line(pinx + 24, y_mid, pinx + 54, y_mid, color=MUTED, sw=2, dash="5,4"))
    f.append(circle(pinx + 60, y_mid, 5, fill=BG, stroke=MUTED, sw=1.6))
    f.append(text(pinx + 74, y_mid + 4, "нікуди — мертвий пад", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f,
           title="Підключення пін-у-пін: два дроти працюють, середній — ні")


def beep_patterns():
    """Чотири патерни біпів на спільній часовій осі: 1 короткий, 3 короткі, довгий, тривога."""
    W, H = 820, 430
    f = []

    x0 = 220            # ліва межа осей (після підписів)
    x1 = W - 30         # права межа
    span = x1 - x0
    unit = span / 24.0  # 24 умовні одиниці часу на всю ширину
    bar_h = 26          # висота смужки «пищить»

    def timeline(y, label, segments):
        # підпис патерна ліворуч
        f.append(text(30, y - 2, label, size=13.5, bold=True, anchor="start"))
        # базова вісь часу
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.2))
        # segments: список (start_u, len_u, on?) — заповнені = звук
        for (s_u, l_u, on) in segments:
            xa = x0 + s_u * unit
            wa = l_u * unit
            if on:
                f.append(rect(xa, y - bar_h, wa, bar_h, fill="#2f6fb0", stroke=INK, sw=1.2, rx=2))

    # ряд 1: «готово» — один короткий біп (2 од.)
    timeline(70, "готово", [(0, 2, True)])
    f.append(text(x0 + 1 * unit, 70 + 22, "один короткий", size=11, color=MUTED, anchor="middle"))

    # ряд 2: «помилка» — три короткі поспіль (біп 1.6 / пауза 1.4)
    seg = []
    t = 0.0
    for i in range(3):
        seg.append((t, 1.6, True)); t += 1.6
        if i < 2:
            seg.append((t, 1.4, False)); t += 1.4
    timeline(160, "помилка", seg)
    f.append(text(x0 + t * unit / 2, 160 + 22, "три швидкі поспіль", size=11, color=MUTED, anchor="middle"))

    # ряд 3: «увага» — один довгий (7 од.)
    timeline(250, "увага", [(0, 7, True)])
    f.append(text(x0 + 3.5 * unit, 250 + 22, "один довгий", size=11, color=MUTED, anchor="middle"))

    # ряд 4: «тривога» — довгі з паузами (4 on / 2 off, тричі)
    seg = []
    t = 0.0
    for i in range(3):
        seg.append((t, 4, True)); t += 4
        seg.append((t, 2, False)); t += 2
    timeline(340, "тривога", seg)
    f.append(text(x0 + 9 * unit, 340 + 22, "довгі з паузами (безперервно)", size=11, color=MUTED, anchor="middle"))

    # легенда під низом
    ly = 392
    f.append(rect(x0, ly - 12, 26, 16, fill="#2f6fb0", stroke=INK, sw=1.1, rx=2))
    f.append(text(x0 + 34, ly + 1, "зумер пищить (HIGH)", size=11.5, color=INK, anchor="start"))
    f.append(line(x0 + 230, ly - 4, x0 + 260, ly - 4, color=MUTED, sw=1.2))
    f.append(text(x0 + 268, ly + 1, "тиша (LOW)", size=11.5, color=MUTED, anchor="start"))
    f.append(text(x1, ly + 1, "висота тону скрізь однакова ≈ 2.5 кГц", size=11.5, color=POS, anchor="end"))

    render(os.path.join(IMG, 'beep-patterns.svg'), W, H, *f,
           title="Мова KY-012 — ритм увімкнень: сенс несе час, не висота")


def blocking_vs_nonblocking():
    """Дві осі часу: delay() спить весь час звучання; millis() лишає loop() вільним."""
    W, H = 820, 440
    f = []

    x0 = 60
    x1 = W - 40
    span = x1 - x0
    unit = span / 20.0
    bar_h = 24

    # спільний ритм біпів: біп 3 / пауза 2, двічі, тоді хвіст
    beeps = [(0, 3, True), (3, 2, False), (5, 3, True), (8, 2, False), (10, 3, True)]

    # ── верх: delay() ─────────────────────────────────────────
    yb = 95             # вісь звуку
    f.append(text(x0, yb - 54, "На delay(): ядро СПИТЬ увесь час звучання й пауз", size=14, bold=True, anchor="start"))
    f.append(line(x0, yb, x1, yb, color=MUTED, sw=1.2))
    for (s, l, on) in beeps:
        if on:
            f.append(rect(x0 + s * unit, yb - bar_h, l * unit, bar_h, fill="#2f6fb0", stroke=INK, sw=1.2, rx=2))
    # смуга «чіп сліпий» — на весь проміжок від першого до останнього
    span_end = 13
    f.append(rect(x0, yb + 10, span_end * unit, 22, fill="#f3d9d9", stroke=POS, sw=1.3, rx=4))
    f.append(text(x0 + span_end * unit / 2, yb + 25, "loop() не крутиться — кнопки й давачі не читаються", size=11.5, color=POS, anchor="middle"))
    # подія, що губиться: вертикаль лише в смузі бар↔статус, підпис — ПРАВОРУЧ від лінії
    ex = x0 + 6.5 * unit
    f.append(line(ex, yb - bar_h + 2, ex, yb + 10, color=POS, sw=1.6, dash="4,3"))
    f.append(circle(ex, yb - bar_h + 2, 3.5, fill=BG, stroke=POS, sw=1.6))
    f.append(text(ex + 10, yb - bar_h - 3, "натиск кнопки — ✗ пропав", size=11, color=POS, anchor="start", bold=True))

    # ── низ: millis() ─────────────────────────────────────────
    yn = 285
    f.append(text(x0, yn - 54, "На millis(): той самий ритм, але loop() увесь час ВІЛЬНИЙ", size=14, bold=True, anchor="start"))
    f.append(line(x0, yn, x1, yn, color=MUTED, sw=1.2))
    for (s, l, on) in beeps:
        if on:
            f.append(rect(x0 + s * unit, yn - bar_h, l * unit, bar_h, fill="#2f6fb0", stroke=INK, sw=1.2, rx=2))
    # смуга «чіп вільний»
    f.append(rect(x0, yn + 10, span_end * unit, 22, fill="#d9efe0", stroke=FIELD, sw=1.3, rx=4))
    f.append(text(x0 + span_end * unit / 2, yn + 25, "loop() пролітає тисячі разів — кнопки й давачі читаються", size=11.5, color=FIELD, anchor="middle"))
    # тики «перевірка часу» — часті стрілочки вздовж осі
    for i in range(0, span_end + 1):
        tx = x0 + i * unit
        f.append(line(tx, yn + 6, tx, yn - 6, color=FIELD, sw=1.0))
    # подія, що ловиться: вертикаль лише в смузі бар↔статус, підпис — ПРАВОРУЧ від лінії
    f.append(line(ex, yn - bar_h + 2, ex, yn + 10, color=FIELD, sw=1.6, dash="4,3"))
    f.append(circle(ex, yn - bar_h + 2, 3.5, fill=BG, stroke=FIELD, sw=1.6))
    f.append(text(ex + 10, yn - bar_h - 3, "натиск кнопки — ✓ помічено", size=11, color=FIELD, anchor="start", bold=True))

    # спільна легенда
    ly = 400
    f.append(rect(x0, ly - 12, 26, 16, fill="#2f6fb0", stroke=INK, sw=1.1, rx=2))
    f.append(text(x0 + 34, ly + 1, "зумер пищить", size=11.5, color=INK, anchor="start"))
    f.append(text(x1, ly + 1, "звук на слух однаковий — різниця в тому, чи живий чіп під час нього", size=11.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'blocking-vs-nonblocking.svg'), W, H, *f,
           title="delay() vs millis(): чи паралізує зумер решту програми")


if __name__ == '__main__':
    schematic()
    wiring()
    beep_patterns()
    blocking_vs_nonblocking()
    print("OK: schematic.svg, wiring.svg, beep-patterns.svg, blocking-vs-nonblocking.svg")
