# -*- coding: utf-8 -*-
"""Фігури до теми «Стандарти кодування конденсаторів (EIA, IEC 60062)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Анатомія тризначного коду EIA та допусків IEC 60062 ────────────
def fig_eia_three_digit_anatomy():
    W, H = 820, 480
    f = [
        text(W / 2, 28, "Анатомія тризначного коду ємності EIA та літерного допуску IEC 60062",
             size=16, bold=True, color=INK)
    ]

    # Верхній блок: великий приклад «104K»
    # Рамка чіпа або корпусу
    chip_x, chip_y, chip_w, chip_h = 40, 60, 240, 110
    f.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#f9fbfd", stroke=LINE, sw=2, rx=8))
    f.append(text(chip_x + chip_w / 2, chip_y + 24, "Керамічний / плівковий корпус", size=12, color=MUTED))
    f.append(text(chip_x + chip_w / 2, chip_y + 75, "104K", size=36, bold=True, color=INK))

    # Стрілки та блоки пояснення для кожної цифри
    # '10' -> Мантиса
    box_m, _, _ = textbox(410, 80, "«10» — значущі цифри (мантиса)\nДві перші цифри утворюють число: 10",
                          size=12, pad=8, fill="#eef6ff", stroke=NEG, color=INK)
    f.append(box_m)
    f.append(arrow(150, 105, 300, 80, color=NEG, sw=1.5))

    # '4' -> Множник 10^4
    box_exp, _, _ = textbox(410, 150, "«4» — показник степеня (множник 10⁴)\nКількість нулів: 10⁴ = 10 000\nБазова одиниця — завжди пікофарад (пФ)",
                            size=12, pad=8, fill="#f4fbf4", stroke=FIELD, color=INK)
    f.append(box_exp)
    f.append(arrow(185, 125, 300, 150, color=FIELD, sw=1.5))

    # 'K' -> Допуск ±10%
    box_tol, _, _ = textbox(675, 115, "«K» — допуск номіналу (IEC 60062)\nK = ±10% (стандарт X7R/X5R)\nJ = ±5%, M = ±20%, F = ±1%",
                            size=12, pad=8, fill="#fff8ee", stroke="#d97706", color=INK)
    f.append(box_tol)
    f.append(arrow(215, 115, 560, 115, color="#d97706", sw=1.5))

    # Розділювальна лінія
    f.append(line(40, 215, W - 40, 215, color=MUTED, sw=1, dash="4 4"))

    # Нижня частина: спеціальні випадки (R як кома, 4-значний код, європейський стиль)
    f.append(text(40, 240, "Спеціальні форми запису та розширення стандарту", size=14, bold=True, anchor="start", color=INK))

    # Колонка 1: Субпікофарадні (R)
    c1_x, c1_y, c1_w, c1_h = 40, 260, 235, 195
    f.append(rect(c1_x, c1_y, c1_w, c1_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(c1_x + c1_w / 2, c1_y + 22, "Дробові номінали з «R»", size=13, bold=True, color=INK))
    f.append(mtext(c1_x + 12, c1_y + 48,
                   ["«R» замінює десяткову крапку:",
                    "• 2R2 = 2.2 пФ",
                    "• R47 = 0.47 пФ",
                    "• 0R5 = 0.5 пФ",
                    "Використовується для C < 10 пФ,",
                    "де третя цифра множника не потрібна."],
                   size=11, color=INK, anchor="start", lh=1.35))

    # Колонка 2: Чотиризначний EIA
    c2_x, c2_y, c2_w, c2_h = 292, 260, 235, 195
    f.append(rect(c2_x, c2_y, c2_w, c2_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(c2_x + c2_w / 2, c2_y + 22, "4-значний прецизійний код", size=13, bold=True, color=INK))
    f.append(mtext(c2_x + 12, c2_y + 48,
                   ["Три цифри мантиси + множник:",
                    "• 1002 = 100 · 10² пФ = 10 нФ",
                    "• 4751 = 475 · 10¹ пФ = 4.75 нФ",
                    "• 1000 = 100 · 10⁰ пФ = 100 пФ",
                    "Застосовується для рядів E96/E192",
                    "з допуском ±1% (F) або ±0.5% (D)."],
                   size=11, color=INK, anchor="start", lh=1.35))

    # Колонка 3: Буквений стиль IEC
    c3_x, c3_y, c3_w, c3_h = 545, 260, 235, 195
    f.append(rect(c3_x, c3_y, c3_w, c3_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(c3_x + c3_w / 2, c3_y + 22, "Буквений префіксний код", size=13, bold=True, color=INK))
    f.append(mtext(c3_x + 12, c3_y + 48,
                   ["Буква вказує базу і кому:",
                    "• 4n7 = 4.7 нФ (n = 10⁻⁹ Ф)",
                    "• 2u2 = 2.2 мкФ (u = 10⁻⁶ Ф)",
                    "• n47 = 0.47 нФ = 470 пФ",
                    "• 33p = 33 пФ (p = 10⁻¹² Ф)",
                    "Виключає стирання або пропуск",
                    "десяткової крапки при друку."],
                   size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(IMG, "eia-three-digit-anatomy.svg"), W, H, *f)


# ── Фігура 2: Матриця температурних класів кераміки за EIA RS-198 ────────────
def fig_temperature_classes_matrix():
    W, H = 840, 520
    f = [
        text(W / 2, 26, "Температурна класифікація керамічних конденсаторів за EIA RS-198",
             size=16, bold=True, color=INK)
    ]

    # Верхній блок: Клас I (C0G / NP0)
    k1_x, k1_y, k1_w, k1_h = 40, 52, 760, 115
    f.append(rect(k1_x, k1_y, k1_w, k1_h, fill="#f2faf5", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(60, k1_y + 24, "Клас I: Ультрастабільні параелектрики (C0G / NP0)", size=14, bold=True, anchor="start", color=FIELD))
    f.append(mtext(60, k1_y + 48,
                   ["Код C0G: C = 0.0 ppm/°C (мантиса)  |  0 = множник ×(-1)  |  G = допуск ТКЄ ±30 ppm/°C",
                    "Діапазон: −55 °C ... +125 °C  |  Дрейф: 0 ± 30 ppm/°C (абсолютно лінійний, ΔC < 0.3% у всьому діапазоні)",
                    "Властивості: нульовий ефект старіння, відсутність DC-bias провалу ємності, нульовий п'єзошум."],
                   size=11.5, color=INK, anchor="start", lh=1.35))

    # Нижній блок: Клас II та III (X7R, X5R, Y5V, Z5U)
    k2_x, k2_y, k2_w, k2_h = 40, 185, 760, 315
    f.append(rect(k2_x, k2_y, k2_w, k2_h, fill="none", stroke="#b45309", sw=1.8, rx=8))
    f.append(text(60, k2_y + 24, "Клас II / III: Сегнетоелектрики високої ємності (трисимвольний код EIA)", size=14, bold=True, anchor="start", color="#b45309"))

    # Таблиця розшифровки трьох символів
    # Стовпець 1: Нижня межа (літера)
    t1_x, t1_y = 60, k2_y + 42
    f.append(rect(t1_x, t1_y, 225, 140, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    f.append(text(t1_x + 112, t1_y + 20, "1-й символ: мін. темп.", size=12, bold=True, color=INK))
    f.append(mtext(t1_x + 15, t1_y + 42,
                   ["X = −55 °C  (промисловий)",
                    "Y = −30 °C  (помірний)",
                    "Z = +10 °C  (комерційний)"],
                   size=11, color=INK, anchor="start", lh=1.4))

    # Стовпець 2: Верхня межа (цифра)
    t2_x, t2_y = 305, k2_y + 42
    f.append(rect(t2_x, t2_y, 225, 140, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    f.append(text(t2_x + 112, t2_y + 20, "2-й символ: макс. темп.", size=12, bold=True, color=INK))
    f.append(mtext(t2_x + 15, t2_y + 42,
                   ["5 = +85 °C   (споживчий)",
                    "7 = +125 °C  (промисловий)",
                    "8 = +150 °C  (автомобільний)"],
                   size=11, color=INK, anchor="start", lh=1.4))

    # Стовпець 3: Максимальне відхилення ΔC (літера)
    t3_x, t3_y = 550, k2_y + 42
    f.append(rect(t3_x, t3_y, 230, 140, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    f.append(text(t3_x + 115, t3_y + 20, "3-й символ: дрейф ΔC/C", size=12, bold=True, color=INK))
    f.append(mtext(t3_x + 15, t3_y + 42,
                   ["P = ±10%",
                    "R = ±15%   (стандартний X7R/X5R)",
                    "U = +22% / −56%  (Z5U)",
                    "V = +22% / −82%  (Y5V, критичний)"],
                   size=11, color=INK, anchor="start", lh=1.4))

    # Порівняльна підсумкова плашка
    summary_y = k2_y + 195
    f.append(rect(60, summary_y, 720, 100, fill="#f8fafc", stroke=LINE, sw=1, rx=5))
    f.append(text(75, summary_y + 22, "Типові комбінації в інженерній практиці:", size=12, bold=True, anchor="start", color=INK))
    f.append(mtext(75, summary_y + 44,
                   ["• X7R: −55 °C...+125 °C, ΔC = ±15%  →  універсальний вибір для аналогових і цифрових кіл",
                    "• X5R: −55 °C...+85 °C, ΔC = ±15%   →  компактні плати з високою ємністю (смартфони, IoT)",
                    "• Y5V: −30 °C...+85 °C, ΔC = +22%/−82%  →  висока щільність ємності, але падіння до 5 разів на морозі!"],
                   size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(IMG, "temperature-classes-matrix.svg"), W, H, *f)


# ── Фігура 3: Полярність та коди номінальної напруги ─────────────────────────
def fig_polarity_and_voltage_codes():
    W, H = 840, 500
    f = [
        text(W / 2, 26, "Маркування полярності та буквено-цифрові коди напруги EIA / JIS",
             size=16, bold=True, color=INK)
    ]

    # Ліва половина: Контраст маркування полярності
    p_x, p_y, p_w, p_h = 40, 55, 380, 420
    f.append(rect(p_x, p_y, p_w, p_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    f.append(text(p_x + p_w / 2, p_y + 24, "Конвенції маркування полярності", size=14, bold=True, color=INK))

    # Тантал SMD
    t_y = p_y + 45
    f.append(rect(p_x + 20, t_y, 110, 55, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    # Смуга плюса
    f.append(rect(p_x + 20, t_y, 22, 55, fill="#fde68a", stroke=POS, sw=2, rx=4))
    f.append(text(p_x + 31, t_y + 34, "+", size=20, bold=True, color=POS))
    f.append(text(p_x + 75, t_y + 34, "476", size=14, bold=True, color=INK))
    f.append(text(p_x + 145, t_y + 22, "Танталовий SMD-чіп", size=12, bold=True, anchor="start", color=POS))
    f.append(mtext(p_x + 145, t_y + 38,
                   ["Смуга = АНОД (+)",
                    "Реверс напруги > 0.5 В викликає",
                    "пробій діелектрика Ta₂O₅ і пожежу."],
                   size=10.5, color=INK, anchor="start", lh=1.25))

    # Алюмінієва банка THT
    a_y = t_y + 80
    f.append(rect(p_x + 20, a_y, 110, 60, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=6))
    # Смуга мінуса
    f.append(rect(p_x + 20, a_y, 24, 60, fill="#cbd5e1", stroke=NEG, sw=2, rx=6))
    f.append(mtext(p_x + 32, a_y + 18, ["−", "−", "−"], size=12, bold=True, color=NEG, lh=1.1))
    f.append(text(p_x + 75, a_y + 36, "470µF", size=12, bold=True, color=INK))
    f.append(text(p_x + 145, a_y + 22, "Алюмінієвий радіальний (THT)", size=12, bold=True, anchor="start", color=NEG))
    f.append(mtext(p_x + 145, a_y + 38,
                   ["Смуга = КАТОД (−), коротша ніжка (−)",
                    "Реверс викликає закипання електроліту",
                    "та спрацювання насічного клапана."],
                   size=10.5, color=INK, anchor="start", lh=1.25))

    # Алюмінієвий SMD (вертикальна банка)
    s_y = a_y + 85
    f.append(circle(p_x + 75, s_y + 35, 28, fill="#e2e8f0", stroke="#475569", sw=1.5))
    # Чорний сектор (півмісяць)
    f.append(rect(p_x + 47, s_y + 7, 28, 56, fill="#334155", stroke="#334155", sw=1, rx=2))
    f.append(text(p_x + 85, s_y + 39, "100", size=11, bold=True, color=INK))
    f.append(text(p_x + 145, s_y + 22, "Алюмінієвий SMD («банка»)", size=12, bold=True, anchor="start", color=NEG))
    f.append(mtext(p_x + 145, s_y + 38,
                   ["Чорний сектор зверху = КАТОД (−)",
                    "Скошені кути підкладки = АНОД (+)",
                    "Пряме маркування ємності та напруги."],
                   size=10.5, color=INK, anchor="start", lh=1.25))

    # Підсумкове попередження
    w_y = s_y + 90
    box_warn, _, _ = textbox(p_x + p_w / 2, w_y + 25,
                             "⚠️ КРИТИЧНЕ ПРАВИЛО:\nСмуга на танталі (+) протилежна за змістом смузі на алюмінії (−)!",
                             size=11, pad=8, fill="#fef2f2", stroke=POS, color=POS, bold=True)
    f.append(box_warn)

    # Права половина: Коди номінальної напруги EIA / JIS
    v_x, v_y, v_w, v_h = 440, 55, 360, 420
    f.append(rect(v_x, v_y, v_w, v_h, fill="none", stroke=LINE, sw=1.5, rx=8))
    f.append(text(v_x + v_w / 2, v_y + 24, "Буквено-цифрові коди напруги EIA / JIS", size=14, bold=True, color=INK))

    # Таблиця напруг
    f.append(text(v_x + 20, v_y + 55, "Код = [множник 10ⁿ] + [буква базової напруги]", size=11, bold=True, anchor="start", color=MUTED))

    volt_data = [
        ("0J", "6.3 В", "Цифрові шини 3.3 В і 5 В"),
        ("1A", "10 В", "Шина 5 В з подвійним запасом"),
        ("1C", "16 В", "Стандарт для автомобільних шин 12 В"),
        ("1E", "25 В", "Шини живлення 18...20 В, DC-DC"),
        ("1V", "35 В", "Промислові шини 24 В"),
        ("1H", "50 В", "Аналогові підсилювачі, шини 36 В"),
        ("2A", "100 В", "Високовольтні драйвери, PoE"),
        ("2E", "250 В", "Мережеві фільтри 110/230 В"),
    ]

    row_y = v_y + 75
    for code, volt, desc in volt_data:
        f.append(rect(v_x + 18, row_y, 50, 24, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
        f.append(text(v_x + 43, row_y + 16, code, size=11.5, bold=True, color=NEG))

        f.append(rect(v_x + 74, row_y, 62, 24, fill="#f1f5f9", stroke=LINE, sw=0.8, rx=3))
        f.append(text(v_x + 105, row_y + 16, volt, size=11.5, bold=True, color=INK))

        f.append(text(v_x + 144, row_y + 16, desc, size=10.5, color=MUTED, anchor="start"))
        row_y += 30

    # Однолітерні коди танталу
    f.append(line(v_x + 18, row_y + 8, v_x + v_w - 18, row_y + 8, color=MUTED, sw=0.8, dash="3 3"))
    f.append(text(v_x + 20, row_y + 26, "Однолітерні коди на крихітних SMD (тантал/MLCC):", size=10.5, bold=True, anchor="start", color=INK))
    f.append(mtext(v_x + 20, row_y + 44,
                   ["e = 2.5V | G = 4.0V | J = 6.3V | A = 10V",
                    "C = 16V  | D = 20V  | E = 25V  | V = 35V | H = 50V"],
                   size=10.5, color=INK, anchor="start", lh=1.35))

    render(os.path.join(IMG, "polarity-and-voltage-codes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_eia_three_digit_anatomy()
    print("OK: img/eia-three-digit-anatomy.svg")
    fig_temperature_classes_matrix()
    print("OK: img/temperature-classes-matrix.svg")
    fig_polarity_and_voltage_codes()
    print("OK: img/polarity-and-voltage-codes.svg")
