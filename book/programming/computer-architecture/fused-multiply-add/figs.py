# -*- coding: utf-8 -*-
"""Фігури до теми «FMA: суміщене множення-додавання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
GOLD   = "#b9770e"
PALE_R = "#fdecea"
PALE_B = "#eaf0fd"
PALE_G = "#eaf7ee"
PALE_Y = "#fbf4e6"
PALE_V = "#f3e8fd"
PURPLE = "#7b2cbf"


# ── 1. Порівняння конвеєрів: роздільні MUL + ADD проти FMA ────────────────────
def fig_pipeline_comparison():
    W, H = 840, 480
    f = []

    # Заголовок колонок
    f.append(text(215, 30, "Роздільні MUL + ADD (дві інструкції)", size=15, color=POS, bold=True))
    f.append(text(625, 30, "Суміщене FMA (одна апаратна операція)", size=15, color=FIELD, bold=True))

    # Розділювальна лінія
    f.append(line(420, 20, 420, 430, color=LINE, sw=1.2, dash="4,4"))

    # Ліва колонка: Роздільні MUL + ADD
    # Входи A, B
    f.append(fitbox(70, 55, 120, 32, "Операнди A, B", size=12, fill=PALE_B, stroke=NEG))
    f.append(arrow(130, 87, 130, 105, color=LINE))

    # Множник
    f.append(fitbox(50, 105, 160, 34, "Множник мантис\n(дерево Уоллеса)", size=11, fill=FILL, stroke=LINE))
    f.append(arrow(130, 139, 130, 155, color=LINE))

    # Перший CPA
    f.append(fitbox(50, 155, 160, 30, "Суматор з переносом (CPA 1)", size=11, fill=FILL, stroke=LINE))
    f.append(arrow(130, 185, 130, 200, color=LINE))

    # Нормалізація 1 + Округлення 1
    f.append(fitbox(50, 200, 160, 38, "Нормалізація 1 +\nОкруглення 1 (втрата бітів!)", size=11, fill=PALE_R, stroke=POS))
    f.append(arrow(130, 238, 130, 255, color=LINE))

    # Проміжний регістр
    f.append(fitbox(50, 255, 160, 30, "Регістровий файл (tmp = A×B)", size=11, fill=PALE_Y, stroke=GOLD))
    f.append(arrow(130, 285, 130, 305, color=LINE))

    # Вхід C + Додавання
    f.append(fitbox(230, 255, 130, 30, "Операнд C", size=12, fill=PALE_B, stroke=NEG))
    f.append(arrow(295, 285, 220, 305, color=LINE))

    # Вирівнювач + Другий CPA
    f.append(fitbox(50, 305, 230, 34, "Вирівнювання порядку C +\nСуматор з переносом (CPA 2)", size=11, fill=FILL, stroke=LINE))
    f.append(arrow(165, 339, 165, 355, color=LINE))

    # Нормалізація 2 + Округлення 2
    f.append(fitbox(50, 355, 230, 38, "Нормалізація 2 +\nОкруглення 2 (подвійна похибка)", size=11, fill=PALE_R, stroke=POS))
    f.append(arrow(165, 393, 165, 410, color=LINE))

    # Підсумок лівої колонки
    f.append(fitbox(50, 410, 230, 30, "Результат: 2 CPA, 2 округлення (~6–8 тактів)", size=10, fill=PALE_R, stroke=POS, bold=True))

    # Права колонка: FMA
    # Входи A, B, C
    f.append(fitbox(470, 55, 120, 32, "Операнди A, B", size=12, fill=PALE_B, stroke=NEG))
    f.append(fitbox(660, 55, 120, 32, "Операнд C", size=12, fill=PALE_B, stroke=NEG))

    f.append(arrow(530, 87, 530, 115, color=LINE))
    f.append(arrow(720, 87, 720, 115, color=LINE))

    # Блоки множення і паралельного вирівнювання
    f.append(fitbox(460, 115, 150, 44, "Множення A × B\n(без округлення, 106 бітів)", size=11, fill=PALE_G, stroke=FIELD))
    f.append(fitbox(645, 115, 150, 44, "Вирівнювання мантиси C\n(паралельно з множенням)", size=11, fill=PALE_G, stroke=FIELD))

    f.append(arrow(535, 159, 580, 185, color=LINE))
    f.append(arrow(720, 159, 670, 185, color=LINE))

    # Спільне дерево суматорів CSA
    f.append(fitbox(470, 185, 310, 46, "Матриця суматорів збереження переносу (3:2 CSA)\nДоданок C вливається прямо в дерево часткових добутків", size=11, fill=PALE_G, stroke=FIELD))
    f.append(arrow(625, 231, 625, 255, color=LINE))

    # Єдиний CPA + LZA
    f.append(fitbox(470, 255, 310, 44, "Єдиний фінальний CPA (суматор з переносом)\n+ Паралельний передбачувач старших нулів (LZA)", size=11, fill=FILL, stroke=LINE))
    f.append(arrow(625, 299, 625, 325, color=LINE))

    # ОДНА нормалізація + ОДНЕ округлення
    f.append(fitbox(470, 325, 310, 44, "Єдина нормалізація (за даними LZA) +\nЄдине точне округлення IEEE 754", size=12, fill=PALE_G, stroke=FIELD, bold=True))
    f.append(arrow(625, 369, 625, 395, color=LINE))

    # Підсумок правої колонки
    f.append(fitbox(470, 395, 310, 34, "Результат: 1 CPA, 1 округлення (~4–5 тактів, 0 проміжної похибки)", size=11, fill=PALE_G, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "pipeline-comparison.svg"), W, H, *f,
           title="Порівняння конвеєрів: роздільні MUL + ADD проти суміщеного FMA")


# ── 2. Механізм подвійного округлення ─────────────────────────────────────────
def fig_double_rounding():
    W, H = 800, 340
    f = []

    # Заголовок
    f.append(text(400, 30, "Проблема подвійного округлення (Double Rounding)", size=16, color=INK, bold=True))

    # Числова вісь (неперервна)
    f.append(line(80, 110, 720, 110, color=LINE, sw=2))
    f.append(arrow(715, 110, 730, 110, color=LINE))
    f.append(text(740, 114, "R", size=13, color=MUTED, italic=True))

    # Сітка розрядів цільового формату
    # Мітка x0
    f.append(line(160, 95, 160, 125, color=NEG, sw=2))
    f.append(text(160, 85, "x₀ (репрезентоване)", size=12, color=NEG, bold=True))

    # Поріг половини (tie-threshold)
    f.append(line(380, 100, 380, 120, color=GOLD, sw=1.5, dash="3,3"))
    f.append(text(380, 85, "поріг 0.5 ULP", size=11, color=GOLD))

    # Мітка x1
    f.append(line(600, 95, 600, 125, color=NEG, sw=2))
    f.append(text(600, 85, "x₁ (наступне число)", size=12, color=NEG, bold=True))

    # Точне математичне значення
    f.append(circle(370, 110, 5, fill=FIELD, stroke=FIELD, sw=2))
    f.append(text(370, 142, "Точне значення a×b+c\n(трохи ЛІВІШЕ порогу 0.5)", size=11, color=FIELD, bold=True))

    # Проміжне округлення 1 (зміщує праворуч через розширений проміжний формат)
    f.append(circle(390, 110, 5, fill=POS, stroke=POS, sw=2))
    f.append(text(460, 175, "Округлений проміжний добуток round₁(a×b) + c\n(помилково перескочив ПРАВОРУЧ порогу)", size=11, color=POS, bold=True))
    f.append(arrow(370, 120, 388, 112, color=POS, sw=1.5))

    # Стрілки фінальних округлень
    # FMA: точне округлення веде до x0
    f.append(arrow(368, 110, 165, 110, color=FIELD, sw=2.2))
    f.append(text(240, 130, "FMA: Одне округлення → x₀ (ВІРНО)", size=12, color=FIELD, bold=True))

    # MUL+ADD: друге округлення веде до x1
    f.append(arrow(392, 110, 595, 110, color=POS, sw=2.2))
    f.append(text(515, 130, "MUL+ADD: Друге округлення → x₁ (ПОМИЛКА)", size=12, color=POS, bold=True))

    # Пояснювальний підсумок
    f.append(fitbox(70, 220, 660, 95,
                    "Перше округлення спотворює молодші біти й переносить значення через поріг половини розряду.\n"
                    "Друге округлення спирається на вже спотворену точку й вибирає хибного сусіда (+1 ULP).\n"
                    "FMA тримає повну мантису в акумуляторі, тому округлює один-єдиний раз прямо до x₀.",
                    size=12, fill=PALE_Y, stroke=GOLD))

    render(os.path.join(IMG, "double-rounding.svg"), W, H, *f,
           title="Механізм подвійного округлення")


# ── 3. Розрядність внутрішнього тракту FMA (IEEE 754 Float64) ────────────────
def fig_datapath_widths():
    W, H = 820, 380
    f = []

    # Заголовок
    f.append(text(410, 28, "Внутрішній тракт FMA для подвійної точності (float64)", size=15, color=INK, bold=True))

    y = 60
    # Входи мантис A і B
    f.append(fitbox(80, y, 220, 36, "Мантиса A: 53 біти (1 + 52)", size=11, fill=PALE_B, stroke=NEG))
    f.append(fitbox(320, y, 220, 36, "Мантиса B: 53 біти (1 + 52)", size=11, fill=PALE_B, stroke=NEG))

    f.append(arrow(190, y + 36, 290, y + 70, color=LINE))
    f.append(arrow(430, y + 36, 330, y + 70, color=LINE))

    # Точний добуток
    y2 = y + 70
    f.append(fitbox(80, y2, 460, 38, "Точний незрізаний добуток A × B: 106 бітів (53 × 53)", size=12, fill=PALE_G, stroke=FIELD, bold=True))

    # Мантиса C
    f.append(fitbox(570, y, 200, 36, "Мантиса C: 53 біти", size=11, fill=PALE_B, stroke=NEG))
    f.append(arrow(670, y + 36, 670, y2, color=LINE))
    f.append(fitbox(570, y2, 200, 38, "Вирівнювальний зсув\n(−53 ... +106 розрядів)", size=11, fill=PALE_V, stroke=PURPLE))

    # Внутрішній розширений акумулятор
    y3 = y2 + 75
    f.append(text(410, y3 - 8, "Повний внутрішній акумулятор (161+ бітів без втрати розрядів)", size=13, color=FIELD, bold=True))

    # Секції акумулятора
    bx = 70
    f.append(rect(bx, y3, 160, 48, fill=PALE_V, stroke=PURPLE, sw=1.5))
    f.append(text(bx + 80, y3 + 20, "53 біти зліва", size=11, color=PURPLE, bold=True))
    f.append(text(bx + 80, y3 + 36, "якщо порядок C > A×B", size=9, color=MUTED))

    bx += 160
    f.append(rect(bx, y3, 300, 48, fill=PALE_G, stroke=FIELD, sw=2))
    f.append(text(bx + 150, y3 + 20, "106 бітів точного добутку", size=12, color=FIELD, bold=True))
    f.append(text(bx + 150, y3 + 36, "основне поле множення A × B", size=10, color=INK))

    bx += 300
    f.append(rect(bx, y3, 220, 48, fill=PALE_Y, stroke=GOLD, sw=1.5))
    f.append(text(bx + 110, y3 + 20, "Guard, Round, Sticky (3 біти)", size=11, color=GOLD, bold=True))
    f.append(text(bx + 110, y3 + 36, "усі відкинуті молодші одиниці", size=9, color=MUTED))

    # Стрілка вниз до нормалізації і виходу
    y4 = y3 + 68
    f.append(arrow(410, y3 + 48, 410, y4, color=LINE))
    f.append(fitbox(180, y4, 460, 42,
                    "LZA (передбачення нулів) → Зсув нормалізації → Округлення до 53 бітів\n"
                    "Результат float64: точний, ніби обчислено з нескінченною точністю",
                    size=11, fill=PALE_G, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "datapath-widths.svg"), W, H, *f,
           title="Розрядність внутрішнього тракту FMA для float64")


# ── 4. Тріада FMA3 і порівняння з FMA4 ────────────────────────────────────────
def fig_fma_isa_triad():
    W, H = 820, 360
    f = []

    # Заголовок
    f.append(text(410, 26, "Кодування FMA в системі команд x86: тріада FMA3 проти FMA4", size=15, color=INK, bold=True))

    # FMA3 блоки: 132, 213, 231
    y = 52
    w_card = 220
    h_card = 145

    # 132
    f.append(fitbox(60, y, w_card, h_card,
                    "VFMADD132PS dst, s2, s3\n\n"
                    "dst = (dst × s3) + s2\n\n"
                    "Цифри 1-3-2 означають:\n"
                    "Множимо 1-й (dst) на 3-й (s3)\n"
                    "Додаємо 2-й (s2)",
                    size=11, fill=PALE_B, stroke=NEG))

    # 213
    f.append(fitbox(300, y, w_card, h_card,
                    "VFMADD213PS dst, s2, s3\n\n"
                    "dst = (s2 × dst) + s3\n\n"
                    "Цифри 2-1-3 означають:\n"
                    "Множимо 2-й (s2) на 1-й (dst)\n"
                    "Додаємо 3-й (s3)",
                    size=11, fill=PALE_Y, stroke=GOLD))

    # 231
    f.append(fitbox(540, y, w_card, h_card,
                    "VFMADD231PS dst, s2, s3\n\n"
                    "dst = (s2 × s3) + dst\n\n"
                    "Цифри 2-3-1 означають:\n"
                    "Множимо 2-й (s2) на 3-й (s3)\n"
                    "Додаємо 1-й (dst — акумулятор!)",
                    size=11, fill=PALE_G, stroke=FIELD))

    # Нижній блок порівняння: Чому FMA3 виграв у FMA4
    y_bot = y + h_card + 20
    f.append(fitbox(60, y_bot, 700, 115,
                    "FMA4 (AMD): 4 операнди (VFMADDPS dst, s1, s2, s3) — чисто, без перезапису, але вимагає довшого VEX/XOP кодування.\n"
                    "FMA3 (Intel / AMD Zen): 3 операнди з перезаписом dst — економить біти команди, ідеально для накопичувача.\n"
                    "Найчастіша інструкція в матричному множенні (GEMM) — VFMADD231: акумулятор тримає проміжну суму (dst),\n"
                    "а нові множники (s2, s3) безперервно підвантажуються з пам'яті чи векторних регістрів.",
                    size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "fma-isa-triad.svg"), W, H, *f,
           title="Тріада інструкцій FMA3 і порівняння з FMA4")


if __name__ == "__main__":
    fig_pipeline_comparison()
    fig_double_rounding()
    fig_datapath_widths()
    fig_fma_isa_triad()
    print("Всі 4 SVG-фігури успішно згенеровано.")
