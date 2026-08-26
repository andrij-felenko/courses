# -*- coding: utf-8 -*-
"""figs.py — Генерація SVG-ілюстрацій для теми «Сирі відліки у фізичну величину».

Ілюстрації:
1. alignment-and-sign-extension.svg — структура 16-бітного регістра: ліве та праве вирівнювання 12-бітних даних і знакове розширення.
2. calibration-polynomial-surface.svg — 2D-компенсація: залежність сирих відліків тиску від температури та відновлення величини в SI.
3. fixed-point-q-format-multiplication.svg — математика множення у форматі Q16.16 із 64-бітним проміжним акумулятором та округленням.
"""

import sys
import os

# scripts/ у корені репо (4 рівні вгору від root/course/embedded/slug)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_alignment_sign_ext():
    """Фігура 1: Вирівнювання та знакове розширення."""
    w, h = 820, 480
    frags = []

    # Заголовок блоку лівого вирівнювання
    frags.append(rect(20, 40, 780, 180, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(40, 68, "Ліве вирівнювання (Left-aligned, наприклад 12 біт у 16-бітному кадрі)", size=14, bold=True, anchor="start", color="#1e293b"))
    frags.append(text(40, 90, "Знаковий біт S на позиції біта 15 (MSB). Молодші 4 біти — нулі або службові прапорці.", size=12, color=MUTED, anchor="start"))

    # Бітова сітка для Left-aligned
    bx0, by0 = 40, 115
    bit_w = 46
    bit_h = 36

    # 12 біт даних
    for i in range(12):
        bit_idx = 15 - i
        fill_col = "#fee2e2" if bit_idx == 15 else "#e0f2fe"
        border_col = POS if bit_idx == 15 else "#0284c7"
        lbl = "S (b15)" if bit_idx == 15 else ("b%d" % bit_idx)
        frags.append(rect(bx0 + i * bit_w, by0, bit_w, bit_h, fill=fill_col, stroke=border_col, rx=3))
        frags.append(text(bx0 + i * bit_w + bit_w / 2, by0 + 22, lbl, size=11, bold=(bit_idx == 15), color=INK))

    # 4 молодші нульові біти
    for i in range(12, 16):
        bit_idx = 15 - i
        frags.append(rect(bx0 + i * bit_w, by0, bit_w, bit_h, fill="#f1f5f9", stroke="#94a3b8", rx=3))
        frags.append(text(bx0 + i * bit_w + bit_w / 2, by0 + 22, "0 (b%d)" % bit_idx, size=10, color=MUTED))

    # Пояснення операції зсуву
    frags.append(text(bx0, by0 + 60, "Арифметичний зсув праворуч: ( (int16_t)raw ) >> 4  -> зберігає знак числа", size=12, bold=True, anchor="start", color="#0f766e"))

    # Заголовок блоку правого вирівнювання
    frags.append(rect(20, 240, 780, 215, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(40, 268, "Праве вирівнювання (Right-aligned) та знакове розширення у 16/32 біти", size=14, bold=True, anchor="start", color="#1e293b"))
    frags.append(text(40, 290, "Знаковий біт S на позиції біта 11. Якщо S = 1 (число від'ємне), старші біти мають стати одиницями.", size=12, color=MUTED, anchor="start"))

    by1 = 315
    # Старші 4 біти в сирому регістрі
    for i in range(4):
        bit_idx = 15 - i
        frags.append(rect(bx0 + i * bit_w, by1, bit_w, bit_h, fill="#f1f5f9", stroke="#94a3b8", rx=3))
        frags.append(text(bx0 + i * bit_w + bit_w / 2, by1 + 22, "0 (b%d)" % bit_idx, size=10, color=MUTED))

    # 12 біт даних
    for i in range(4, 16):
        bit_idx = 15 - i
        fill_col = "#fee2e2" if bit_idx == 11 else "#e0f2fe"
        border_col = POS if bit_idx == 11 else "#0284c7"
        lbl = "S (b11)" if bit_idx == 11 else ("b%d" % bit_idx)
        frags.append(rect(bx0 + i * bit_w, by1, bit_w, bit_h, fill=fill_col, stroke=border_col, rx=3))
        frags.append(text(bx0 + i * bit_w + bit_w / 2, by1 + 22, lbl, size=11, bold=(bit_idx == 11), color=INK))

    # Стрілка розширення знаку
    frags.append(text(40, 385, "Знакове розширення (Sign Extension):", size=12, bold=True, anchor="start", color=INK))
    frags.append(text(40, 408, "Якщо raw & 0x0800 != 0 (від'ємне), заповнюємо старші біти 15..12 одиницями: raw |= 0xF000", size=12, color=POS, anchor="start"))
    frags.append(text(40, 430, "Або апаратно в один такт: ( (int16_t)(raw << 4) ) >> 4  чи інструкцією ARM SBFX", size=12, color="#0f766e", anchor="start"))

    render(os.path.join(OUT_DIR, "alignment-and-sign-extension.svg"), w, h, *frags, title="Вирівнювання бітів у регістрі та знакове розширення (Sign Extension)")


def fig_calibration_surface():
    """Фігура 2: Заводська калібровка та компенсація перехресної чутливості."""
    w, h = 820, 460
    frags = []

    # Ліва колонка: Сирі відліки з перехресною залежністю
    frags.append(rect(25, 45, 360, 385, fill="#fef2f2", stroke="#f87171", rx=8))
    frags.append(text(205, 75, "Сирі відліки з АЦП датчика", size=15, bold=True, color="#991b1b"))
    frags.append(text(205, 98, "Дрейф, нелінійність і температурний вплив", size=12, color=MUTED))

    # Графік сирих даних (криві)
    gx, gy, gw, gh = 55, 125, 300, 160
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", rx=4))
    # Осі
    frags.append(line(gx + 30, gy + gh - 25, gx + gw - 20, gy + gh - 25, color=LINE, sw=1.2))
    frags.append(line(gx + 30, gy + gh - 25, gx + 30, gy + 20, color=LINE, sw=1.2))
    frags.append(text(gx + gw - 15, gy + gh - 10, "Тиск P", size=10, anchor="end", color=MUTED))
    frags.append(text(gx + 25, gy + 15, "Відліки ADC", size=10, anchor="start", color=MUTED))

    # Криві при різних T
    # T = +85 C (вигнута вгору)
    frags.append(line(gx + 40, gy + 115, gx + 110, gy + 90, color="#ef4444", sw=2))
    frags.append(line(gx + 110, gy + 90, gx + 200, gy + 65, color="#ef4444", sw=2))
    frags.append(line(gx + 200, gy + 65, gx + 270, gy + 45, color="#ef4444", sw=2))
    frags.append(text(gx + 275, gy + 45, "+85 °C", size=10, color="#ef4444", anchor="start", bold=True))

    # T = +25 C
    frags.append(line(gx + 40, gy + 125, gx + 110, gy + 105, color="#f59e0b", sw=2))
    frags.append(line(gx + 110, gy + 105, gx + 200, gy + 82, color="#f59e0b", sw=2))
    frags.append(line(gx + 200, gy + 82, gx + 270, gy + 65, color="#f59e0b", sw=2))
    frags.append(text(gx + 275, gy + 65, "+25 °C", size=10, color="#f59e0b", anchor="start", bold=True))

    # T = -40 C
    frags.append(line(gx + 40, gy + 140, gx + 110, gy + 125, color="#3b82f6", sw=2))
    frags.append(line(gx + 110, gy + 125, gx + 200, gy + 105, color="#3b82f6", sw=2))
    frags.append(line(gx + 200, gy + 105, gx + 270, gy + 90, color="#3b82f6", sw=2))
    frags.append(text(gx + 275, gy + 90, "−40 °C", size=10, color="#3b82f6", anchor="start", bold=True))

    frags.append(text(205, 315, "Кожен екземпляр чіпа має власний зсув,", size=11, color=INK))
    frags.append(text(205, 333, "індивідуальний кут нахилу та вигин кривої.", size=11, color=INK))
    frags.append(text(205, 355, "Без компенсації похибка досягає 20..50%!", size=11, color=POS, bold=True))
    frags.append(text(205, 380, "Параметри записані на заводі в OTP/ROM", size=11, color=MUTED))

    # Центральна стрілка перетворення
    frags.append(arrow(395, 235, 430, 235, color="#0f766e", sw=3))
    frags.append(text(413, 215, "Калібрувальна", size=11, bold=True, color="#0f766e"))
    frags.append(text(413, 227, "матриця", size=11, bold=True, color="#0f766e"))
    frags.append(text(413, 255, "OTP ROM", size=10, color=MUTED))

    # Права колонка: Відновлена фізична величина в SI
    frags.append(rect(435, 45, 360, 385, fill="#f0fdf4", stroke="#86efac", rx=8))
    frags.append(text(615, 75, "Калібровані фізичні величини у SI", size=15, bold=True, color="#166534"))
    frags.append(text(615, 98, "Температурна компенсація та лінеаризація", size=12, color=MUTED))

    # Графік ідеальної прямої
    frags.append(rect(gx + 410, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(line(gx + 440, gy + gh - 25, gx + 410 + gw - 20, gy + gh - 25, color=LINE, sw=1.2))
    frags.append(line(gx + 440, gy + gh - 25, gx + 440, gy + 20, color=LINE, sw=1.2))
    frags.append(text(gx + 410 + gw - 15, gy + gh - 10, "Справжній тиск P (Па)", size=10, anchor="end", color=MUTED))
    frags.append(text(gx + 435, gy + 15, "Розрахований P (Па)", size=10, anchor="start", color=MUTED))

    # Єдина пряма лінія для всіх T
    frags.append(line(gx + 455, gy + gh - 40, gx + 410 + gw - 40, gy + 35, color=FIELD, sw=2.5))
    frags.append(text(gx + 480, gy + 35, "Ідеальна пряма y = x", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(gx + 480, gy + 52, "не залежить від температури", size=10, color=MUTED, anchor="start"))

    frags.append(text(615, 315, "1) T = f(raw_T, dig_T1..T3) -> точна T (0.01 °C)", size=11, color=INK))
    frags.append(text(615, 335, "2) Offset(T) = поліном 2-го порядку від T", size=11, color=INK))
    frags.append(text(615, 355, "3) Sens(T) = масштабування з корекцією T", size=11, color=INK))
    frags.append(text(615, 378, "Результат: Паскалі (Па), м/с², °C з точністю 0.1%", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "calibration-polynomial-surface.svg"), w, h, *frags, title="Компенсація перехресної температурної чутливості та лінеаризація")


def fig_fixed_point_q():
    """Фігура 3: Множення у форматі Q16.16 та збереження розрядності."""
    w, h = 820, 470
    frags = []

    # Вхідні числа
    frags.append(rect(40, 50, 340, 100, fill="#eff6ff", stroke="#3b82f6", rx=6))
    frags.append(text(210, 75, "Вхід X (Формат Q16.16)", size=13, bold=True, color="#1e40af"))
    frags.append(text(210, 95, "32-бітне ціле число: 16 біт цілих, 16 біт дробових", size=11, color=MUTED))
    frags.append(text(210, 115, "Значення: X_real = X_raw / 65536.0", size=11, bold=True, color=INK))

    frags.append(rect(440, 50, 340, 100, fill="#eff6ff", stroke="#3b82f6", rx=6))
    frags.append(text(610, 75, "Коефіцієнт K (Формат Q16.16)", size=13, bold=True, color="#1e40af"))
    frags.append(text(610, 95, "Масштаб чутливості LSB (наприклад, 0.061 мг/LSB)", size=11, color=MUTED))
    frags.append(text(610, 115, "Значення: K_fixed = (uint32_t)(K_real * 65536)", size=11, bold=True, color=INK))

    # Стрілки до блоку множення
    frags.append(arrow(210, 150, 360, 195, color=LINE, sw=1.8))
    frags.append(arrow(610, 150, 460, 195, color=LINE, sw=1.8))

    # Блок 64-бітного множення
    frags.append(rect(240, 195, 340, 95, fill="#fefce8", stroke="#eab308", rx=6))
    frags.append(text(410, 220, "64-бітне множення (SMULL / int64_t)", size=14, bold=True, color="#854d0e"))
    frags.append(text(410, 240, "Формат добутку: Q32.32 (64 біти)", size=12, bold=True, color=POS))
    frags.append(text(410, 260, "prod = (int64_t)X * K  (без переповнення!)", size=12, color=INK))

    # Стрілка вниз
    frags.append(arrow(410, 290, 410, 320, color=LINE, sw=1.8))

    # Блок округлення та зсуву
    frags.append(rect(180, 320, 460, 115, fill="#f0fdf4", stroke="#22c55e", rx=6))
    frags.append(text(410, 345, "Округлення та нормалізація назад до Q16.16", size=13, bold=True, color="#15803d"))
    frags.append(text(410, 368, "Додавання половини LSB: prod += (1ULL << 15)  [Round to Nearest]", size=11, color=INK))
    frags.append(text(410, 390, "Арифметичний зсув: result = (int32_t)(prod >> 16)", size=12, bold=True, color="#047857"))
    frags.append(text(410, 412, "Швидкість: 1..2 такти на Cortex-M, нуль викликів float-емуляції", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "fixed-point-q-format-multiplication.svg"), w, h, *frags, title="Множення з фіксованою комою у форматі Q16.16 та округлення")


if __name__ == "__main__":
    fig_alignment_sign_ext()
    fig_calibration_surface()
    fig_fixed_point_q()
    print("Згенеровано 3 фігури у", OUT_DIR)
