# -*- coding: utf-8 -*-
"""
Фігури для вставки r11-s4-c-stm32-boards.md
(🔌 Плати STM32: Nucleo-клас і «Blue Pill»-клас)

Запуск: python figs-r11-s4-c-stm32-boards.py
Вивід: ./img/fig-r11-s4c-1-nucleo-anatomy.svg
        ./img/fig-r11-s4c-2-power-jumpers.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольори для STM32-теми ─────────────────────────────────────────────────
ST_BLUE  = "#1a5276"   # ST-Link / бортовий зонд
ST_LIGHT = "#d6eaf8"   # світла заливка ST-Link-зони
TGT_COL  = "#1e8449"   # цільовий STM32
TGT_FILL = "#d5f5e3"   # заливка цільової зони
ARD_COL  = "#7d6608"   # Arduino-гребінки
DASH_COL = "#e74c3c"   # лінія розламу / попередження

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Анатомія Nucleo + контраст Blue Pill
# ─────────────────────────────────────────────────────────────────────────────
def fig1_nucleo_anatomy():
    W, H = 820, 480
    parts = []

    # ── Заголовок ──────────────────────────────────────────────────────────
    parts.append(text(W // 2, 28, "Рис. 4.11.4c.1  Анатомія Nucleo і Blue Pill", size=15, bold=True))

    # ══════════════════════════════════════════════════════════════════════
    # ЛІВА ЧАСТИНА — Nucleo (x: 20…510)
    # ══════════════════════════════════════════════════════════════════════
    # Загальна рамка плати
    parts.append(rect(20, 48, 490, 400, fill="#f8f9fa", stroke=INK, sw=2, rx=10))
    parts.append(text(265, 66, "Nucleo (дві плати в одній)", size=13, bold=True, color=INK))

    # ── Верхня зона — ST-Link-зонд ─────────────────────────────────────
    parts.append(rect(30, 76, 470, 160, fill=ST_LIGHT, stroke=ST_BLUE, sw=2, rx=7))
    parts.append(text(265, 95, "ST-Link-зонд (верхня частина плати)", size=12, bold=True, color=ST_BLUE))

    # USB-роз'єм → ST-Link MCU → SWD
    tb, _, _ = textbox(90, 148, "USB\n(до ПК)", size=11, fill="#d5e8fc", stroke=ST_BLUE, sw=1.5)
    parts.append(tb)
    parts.append(arrow(125, 148, 185, 148, color=ST_BLUE))

    tb, _, _ = textbox(225, 135, "ST-Link MCU\n(програматор)", size=11, fill=ST_LIGHT, stroke=ST_BLUE, sw=2, bold=True)
    parts.append(tb)

    # Три функції ST-Link
    tb, _, _ = textbox(225, 178, "① прошиває по SWD\n② відлагоджує (breakpoint)\n③ VCP (virtual COM port)", size=10, fill="#eaf3fb", stroke=ST_BLUE, sw=1)
    parts.append(tb)

    # SWD вниз до цілі
    parts.append(arrow(265, 206, 265, 240, color=ST_BLUE, sw=2))
    tb, _, _ = textbox(310, 223, "SWD", size=11, fill=ST_LIGHT, stroke=ST_BLUE)
    parts.append(tb)

    # ── Лінія розламу (break-apart) ────────────────────────────────────
    parts.append(line(30, 236, 500, 236, color=DASH_COL, sw=2.5, dash="8 4"))
    parts.append(text(265, 251, "✂  break-apart: відламай → окремий програматор", size=11, color=DASH_COL, bold=True))

    # ── Нижня зона — цільовий STM32 ────────────────────────────────────
    parts.append(rect(30, 258, 470, 175, fill=TGT_FILL, stroke=TGT_COL, sw=2, rx=7))
    parts.append(text(265, 274, "Цільовий STM32 (нижня частина плати)", size=12, bold=True, color=TGT_COL))

    # STM32 чип
    tb, _, _ = textbox(110, 320, "STM32\n(ціль)", size=13, fill=TGT_FILL, stroke=TGT_COL, sw=2, bold=True)
    parts.append(tb)

    # LDO
    tb, _, _ = textbox(255, 310, "LDO 3.3 В", size=11, fill="#d5f5e3", stroke=TGT_COL)
    parts.append(tb)
    parts.append(arrow(255, 326, 155, 320, color=TGT_COL))

    # Гребінки
    tb, _, _ = textbox(380, 305, "Гребінки\nArduino + Morpho\n(всі ніжки)", size=10, fill="#d5f5e3", stroke=TGT_COL)
    parts.append(tb)
    parts.append(arrow(295, 316, 335, 310, color=TGT_COL))

    # RESET + LED
    tb, _, _ = textbox(170, 400, "RESET", size=11, fill=FILL, stroke=INK)
    parts.append(tb)
    tb, _, _ = textbox(270, 400, "LED (користувача)", size=11, fill=FILL, stroke=INK)
    parts.append(tb)
    tb, _, _ = textbox(400, 400, "3.3 В логіка", size=11, fill="#d5f5e3", stroke=TGT_COL)
    parts.append(tb)

    # ══════════════════════════════════════════════════════════════════════
    # ПРАВА ЧАСТИНА — Blue Pill (x: 530…800)
    # ══════════════════════════════════════════════════════════════════════
    parts.append(rect(525, 48, 275, 400, fill="#fef9f0", stroke="#d68910", sw=2, rx=10))
    parts.append(text(662, 66, "Blue Pill", size=13, bold=True, color="#d68910"))
    parts.append(text(662, 84, "(голий чип, зонда нема)", size=11, color=MUTED))

    # STM32 чип
    tb, _, _ = textbox(662, 160, "STM32\n(той самий клас)", size=13, fill="#fdebd0", stroke="#d68910", sw=2, bold=True)
    parts.append(tb)

    # Мінімальна обв'язка
    tb, _, _ = textbox(662, 235, "Кварц + LDO\n+ 2 LED + USB-роз'єм", size=10, fill="#fef5e7", stroke="#d68910")
    parts.append(tb)

    # 4-пін SWD
    parts.append(rect(590, 285, 144, 64, fill="#fdebd0", stroke=DASH_COL, sw=2, rx=5))
    parts.append(text(662, 307, "4-пін SWD (зовні)", size=11, bold=True, color=DASH_COL))
    parts.append(text(662, 325, "SWCLK · SWDIO · GND · 3V3", size=10, color=MUTED))

    # Стрілка «підключи зонд»
    parts.append(arrow(662, 349, 662, 376, color=DASH_COL, sw=1.8))
    tb, _, _ = textbox(662, 394, "Зовнішній ST-Link\n(або від Nucleo)", size=10, fill="#fdecea", stroke=DASH_COL)
    parts.append(tb)

    # Підпис відсутнього зонда
    parts.append(text(662, 130, "❌ бортового зонда немає", size=11, color=DASH_COL, bold=True))

    # ── Підпис нижче ──────────────────────────────────────────────────────
    cap = ("Nucleo: USB → ST-Link → SWD → ціль. Відламав верхню частину → маєш програматор для Blue Pill.  "
           "Blue Pill: голий чип, SWD виведено назовні.")
    parts.append(text(W // 2, H - 8, cap, size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r11-s4c-1-nucleo-anatomy.svg"), W, H, *parts)
    print("OK fig-r11-s4c-1-nucleo-anatomy.svg")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Карта живлення Nucleo і Blue Pill
# ─────────────────────────────────────────────────────────────────────────────
def fig2_power_jumpers():
    W, H = 820, 420
    parts = []

    parts.append(text(W // 2, 26, "Рис. 4.11.4c.2  Звідки живиться чип: джемпери живлення", size=15, bold=True))

    # ══════════════════════════════════════════════════════════════════════
    # ЛІВА ЧАСТИНА — Nucleo (x: 20…390)
    # ══════════════════════════════════════════════════════════════════════
    parts.append(rect(20, 42, 375, 350, fill="#f4f6f8", stroke=INK, sw=2, rx=10))
    parts.append(text(207, 60, "Nucleo — джемпери живлення", size=13, bold=True))

    # Джерела живлення — три варіанти (позначено «перемикач»)
    src_y = [105, 160, 215]
    src_labels = ["USB → ST-Link\n(штатно)", "Зовнішнє 5 В\n(VIN)", "Зовнішнє 3.3 В\n(3V3)"]
    src_fills  = [ST_LIGHT, "#fef9f0", "#d5f5e3"]
    src_strokes= [ST_BLUE,  "#d68910", TGT_COL]

    for i, (y, lbl, fl, st) in enumerate(zip(src_y, src_labels, src_fills, src_strokes)):
        tb, bw, _ = textbox(120, y, lbl, size=11, fill=fl, stroke=st, sw=1.5)
        parts.append(tb)

    # «Перемикач» — символічна рамка
    parts.append(rect(195, 85, 44, 160, fill="#fff", stroke=INK, sw=1.5, rx=4))
    parts.append(text(217, 165, "JP", size=11, color=MUTED, bold=True))

    # Стрілки від джерел до перемикача
    for y in src_y:
        parts.append(arrow(162, y, 196, 165, color=MUTED, sw=1.2))

    # Від перемикача до STM32-цілі
    parts.append(arrow(239, 165, 285, 165, color=TGT_COL, sw=2))
    tb, _, _ = textbox(325, 165, "STM32\n(ціль)\n3.3 В", size=11, fill=TGT_FILL, stroke=TGT_COL, sw=2, bold=True)
    parts.append(tb)

    # Додатковий джемпер «відламана ціль від ST-Link»
    parts.append(line(20, 265, 395, 265, color=MUTED, sw=1, dash="4 3"))
    parts.append(text(207, 280, "Також: JP → живлення зовнішньої цілі від бортового ST-Link", size=10, color=MUTED))
    parts.append(text(207, 296, "(після відламу верхньої частини, §4.2.8c)", size=10, color=MUTED))

    # Попередження: перевернутий джемпер
    parts.append(rect(35, 315, 350, 60, fill="#fdecea", stroke=DASH_COL, sw=1.5, rx=5))
    parts.append(text(210, 338, "⚠  Перевернутий джемпер = «плата мертва»", size=11, color=DASH_COL, bold=True))
    parts.append(text(210, 357, "або «прошивається, але не стартує»", size=11, color=DASH_COL))

    # ══════════════════════════════════════════════════════════════════════
    # ПРАВА ЧАСТИНА — Blue Pill (x: 415…800)
    # ══════════════════════════════════════════════════════════════════════
    parts.append(rect(415, 42, 385, 350, fill="#fef9f0", stroke="#d68910", sw=2, rx=10))
    parts.append(text(607, 60, "Blue Pill — входи живлення", size=13, bold=True, color="#d68910"))

    # Шлях 1: USB/5V → регулятор → 3.3В
    tb, _, _ = textbox(510, 120, "USB / 5V-пін", size=11, fill="#fef5e7", stroke="#d68910")
    parts.append(tb)
    parts.append(arrow(568, 120, 620, 120, color="#d68910", sw=1.8))
    tb, _, _ = textbox(670, 120, "LDO\nрегулятор", size=11, fill="#fef5e7", stroke="#d68910")
    parts.append(tb)
    parts.append(arrow(720, 140, 720, 185, color=TGT_COL, sw=1.8))

    # Шлях 2: 3.3V-пін → прямо в чіп (в обхід)
    tb, _, _ = textbox(510, 190, "3V3-пін\n(в обхід LDO)", size=11, fill="#d5f5e3", stroke=TGT_COL)
    parts.append(tb)
    parts.append(arrow(572, 190, 620, 190, color=TGT_COL, sw=1.8))

    # STM32 (ціль)
    tb, _, _ = textbox(680, 195, "STM32\n(ціль)\n3.3 В", size=13, fill=TGT_FILL, stroke=TGT_COL, sw=2, bold=True)
    parts.append(tb)

    # «НЕ ОДНОЧАСНО» — заборона
    parts.append(rect(430, 250, 355, 70, fill="#fdecea", stroke=DASH_COL, sw=2, rx=7))
    parts.append(text(607, 272, "✖  Не подавати USB + зовнішнє одночасно!", size=12, color=DASH_COL, bold=True))
    parts.append(text(607, 291, "Конфлікт джерел → пошкодження LDO або чипа.", size=11, color=DASH_COL))

    # 5V tolerant нагадування
    parts.append(rect(430, 335, 355, 45, fill="#fff8e7", stroke="#d68910", sw=1.5, rx=5))
    parts.append(text(607, 352, "Усі рівні 3.3 В. Ніжки STM32 — не всі 5V tolerant.", size=11, color="#7d6608", bold=True))
    parts.append(text(607, 368, "Деталі — у даташиті розділу (§8).", size=10, color=MUTED))

    # Спільний підпис
    cap = "Nucleo: джемпер вибирає одне з трьох джерел. Blue Pill: два входи, але НЕ одночасно. Скрізь 3.3-вольтова логіка."
    parts.append(text(W // 2, H - 8, cap, size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r11-s4c-2-power-jumpers.svg"), W, H, *parts)
    print("OK fig-r11-s4c-2-power-jumpers.svg")


if __name__ == "__main__":
    fig1_nucleo_anatomy()
    fig2_power_jumpers()
    print("Done: both SVG figures saved to ./img/")
