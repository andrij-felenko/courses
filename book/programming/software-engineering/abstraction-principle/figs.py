# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#c07000"
WFILL = "#fff3cd"


# ── abstraction-concept: суть принципу абстракції ──────────────────────────────
# Ідея: відокремлення сутнісного контракту від деталей реалізації.
# Зверху — чистий семантичний інтерфейс для клієнта.
# Посередині — бар'єр абстракції (захист інваріантів).
# Знизу — апаратні та структурні деталі, замкнені всередині.

def fig_abstraction_concept():
    W, H = 780, 420
    p = []

    cx = W / 2

    # Клієнтський код
    client_box, cw, ch = textbox(cx, 44,
                                 "КЛІЄНТСЬКИЙ КОД (БІЗНЕС-ЛОГІКА)\n"
                                 "Оперує сутностями завдання: sensor.read_temperature() -> float",
                                 size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=580)
    p.append(client_box)

    # Стрілка вниз до інтерфейсу
    p.append(arrow(cx, 44 + ch / 2, cx, 114, color=NEG, sw=1.8))
    p.append(text(cx + 120, 94, "виклик через контракт", size=10, color=NEG, bold=True))

    # Бар'єр абстракції / Контракт
    contract_box, kw, kh = textbox(cx, 150,
                                   "МЕЖА АБСТРАКЦІЇ (СЕМАНТИЧНИЙ КОНТРАКТ)\n"
                                   "• Чіткий набір операцій: { read(), calibrate(), status() }\n"
                                   "• Гарантовані інваріанти: температура в °C, діапазон [-40..+85]\n"
                                   "• Ізоляція від фізичного представлення та апаратного протоколу",
                                   size=11, bold=True, fill="#e8f5e9", stroke=FIELD, sw=2.0, min_w=620)
    p.append(contract_box)

    # Розділова лінія бар'єра
    p.append(line(50, 216, W - 50, 216, color=FIELD, sw=2.2, dash="6 4"))
    p.append(text(cx, 230, "▼  ДЕТАЛІ ВТІЛЕННЯ ПРИХОВАНІ ЗА МЕЖЕЮ  ▼", size=10, color=FIELD, bold=True))

    # Три приховані конкретні реалізації під капотом
    bx1, bx2, bx3 = 160, cx, W - 160
    by = 310

    impl1, w1, h1 = textbox(bx1, by,
                            "Реалізація I2C (BMP280)\n"
                            "• Адреса шини 0x76\n"
                            "• Калібрувальні коефіцієнти\n"
                            "• 20-бітні сирі регістри",
                            size=10, fill=FILL, stroke=LINE, sw=1.4, min_w=200)
    impl2, w2, h2 = textbox(bx2, by,
                            "Реалізація SPI (MAX31865)\n"
                            "• Вибірка CS, режим SPI 1\n"
                            "• PT100 терморезистор\n"
                            "• Обчислення полінома RTD",
                            size=10, fill=FILL, stroke=LINE, sw=1.4, min_w=200)
    impl3, w3, h3 = textbox(bx3, by,
                            "Імітатор SITL (Mock)\n"
                            "• Генерація синусоїди\n"
                            "• Додавання шуму Гауса\n"
                            "• Тестування без заліза",
                            size=10, fill=FILL, stroke=LINE, sw=1.4, min_w=200)

    p.append(impl1); p.append(impl2); p.append(impl3)

    # З'єднувальні лінії від межі до реалізацій
    p.append(line(cx - 180, 216, bx1, by - h1 / 2, color=MUTED, sw=1.4))
    p.append(line(cx, 216, bx2, by - h2 / 2, color=MUTED, sw=1.4))
    p.append(line(cx + 180, 216, bx3, by - h3 / 2, color=MUTED, sw=1.4))

    p.append(text(cx, H - 14,
                  "Зміна протоколу, заліза чи структури пам'яті не зачіпає клієнтський код",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "abstraction-concept.svg"), W, H, *p,
           title="Принцип абстракції: відокремлення сутнісного від випадкового")


# ── four-axes: чотири осі принципу абстракції ──────────────────────────────────
# Ідея: за Рейнольдсом і Гелернтером — усяка спільність виноситься в єдину сутність:
# 1. За значенням (Функціональна)
# 2. За представленням (Дані / ADT)
# 3. За типом (Generics / Templates)
# 4. За поведінкою (Поліморфізм)

def fig_four_axes():
    W, H = 820, 390
    p = []

    cols = [
        ("1. За значенням", "Функціональна",
         "Параметризація обчислень\nаргументами:\nsqr(x) = x · x\nЗамість дублювання формул",
         "#eaf0fd", NEG),
        ("2. За представленням", "Абстрактні типи (ADT)",
         "Приховування форми пам'яті\nза операціями:\nRingBuffer { push, pop }\nЗахист інваріантів структури",
         "#f4fbf7", FIELD),
        ("3. За типом", "Параметрична (Generics)",
         "Параметризація алгоритму\nтипом даних:\nsort<T>(span<T>)\nОдин код для int, float, T",
         "#fff8e1", WARN),
        ("4. За поведінкою", "Поліморфна",
         "Динамічна підміна втілення\nчерез інтерфейс:\nITransport -> send(pkt)\nUART, TCP, BLE на льоту",
         "#fdecea", POS),
    ]

    col_w = 180
    gap = 18
    start_x = (W - (4 * col_w + 3 * gap)) / 2 + col_w / 2

    for i, (title_axis, subtitle, desc, fill_c, stroke_c) in enumerate(cols):
        cx = start_x + i * (col_w + gap)
        cy = 190

        # Рамка категорії
        box, bw, bh = textbox(cx, cy,
                              f"{title_axis}\n"
                              f"({subtitle})\n\n"
                              f"{desc}",
                              size=10.5, bold=True, fill=fill_c, stroke=stroke_c, sw=1.6, min_w=col_w)
        p.append(box)

    # Верхній банер
    top_box, tw, th = textbox(W / 2, 54,
                              "ЄДИНЕ ПРАВИЛО: СПІЛЬНІСТЬ ВИНЕСЕНО В АБСТРАКЦІЮ, ВІДМІННОСТІ — У ПАРАМЕТРИ",
                              size=11, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.8, min_w=720)
    p.append(top_box)

    p.append(text(W / 2, H - 12,
                  "Різні механізми мови втілюють один і той самий принцип на різних рівнях виразності",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "four-axes.svg"), W, H, *p,
           title="Чотири осі принципу абстракції")


# ── leaky-abstraction: закон дірявих абстракцій Спольскі ───────────────────────
# Ідея: ідеальна абстракція обіцяє простоту, але фізична реальність проривається

def fig_leaky_abstraction():
    W, H = 780, 380
    p = []

    cx = W / 2

    # Верхня ілюзія (Обіцянка)
    p_box, pw, ph = textbox(cx, 64,
                            "ОБІЦЯНКА АБСТРАКЦІЇ (ОХАЙНА МОДЕЛЬ)\n"
                            "• «Масив — це плоска пам'ять з доступом O(1) до будь-якого елемента»\n"
                            "• «Файлова система — це локальні синхронні read()/write() без відмов»\n"
                            "• «TCP — це неперервний надійний потік байтів без втрат і затримок»",
                            size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=640)
    p.append(p_box)

    # Зона протікання
    p.append(line(50, 150, W - 50, 150, color=POS, sw=2.2, dash="7 4"))
    leak_badge, lw, lh = textbox(cx, 150,
                                 "⚡ ПРОТІКАННЯ КРІЗЬ ШВИ АБСТРАКЦІЇ (LEAKY ABSTRACTION) ⚡",
                                 size=10.5, bold=True, fill="#fdecea", stroke=POS, sw=1.8, min_w=480)
    p.append(leak_badge)

    # Нижня фізична реальність
    r_box, rw, rh = textbox(cx, 250,
                            "ФІЗИЧНА РЕАЛЬНІСТЬ (ЩО ВІДБУВАЄТЬСЯ НАСПРАВДІ)\n"
                            "• Кеш-промахи: послідовний доступ 1 нс (L1), випадковий — 80 нс (RAM) → різниця у 80 разів!\n"
                            "• NFS/Мережевий диск: витягли кабель → read() блокує потік на 120 с у стані D\n"
                            "• TCP під час втрати зв'язку: ретрансміти, буферизація в сокеті, вичерпання дескрипторів",
                            size=10.5, bold=True, fill=WFILL, stroke=WARN, sw=1.8, min_w=680)
    p.append(r_box)

    p.append(text(cx, H - 12,
                  "Абстракція спрощує мислення, але не скасовує фізичних законів роботи апаратури",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "leaky-abstraction.svg"), W, H, *p,
           title="Закон дірявих абстракцій: коли фізика прориває інтерфейс")


# ── main-sequence: головна послідовність абстрактності Мартіна ──────────────────
# Ідея: для вставки math-abstraction-metrics.md.
# Площина (I, A). Лінія балансу A + I = 1. Зона болю (0,0), зона марноти (1,1).

def fig_main_sequence():
    W, H = 640, 480
    p = []

    ox, oy = 110, 370
    size = 260

    # Сітка та фон квадрантів
    # Зона болю (біля 0,0)
    p.append(rect(ox, oy - size / 2, size / 2, size / 2, fill="#fdecea", stroke="none"))
    # Зона марноти (біля 1,1)
    p.append(rect(ox + size / 2, oy - size, size / 2, size / 2, fill="#fff3cd", stroke="none"))

    # Осі координат
    p.append(arrow(ox, oy, ox + size + 50, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - size - 40, color=INK, sw=2))

    # Підписи осей
    p.append(text(ox + size + 45, oy + 24, "Нестабільність I", size=11, color=INK, bold=True))
    p.append(text(ox - 10, oy - size - 30, "Абстрактність A", size=11, color=INK, bold=True, anchor="end"))

    # Поділки 0, 0.5, 1
    p.append(text(ox, oy + 18, "0.0", size=10, color=MUTED))
    p.append(text(ox + size / 2, oy + 18, "0.5", size=10, color=MUTED))
    p.append(text(ox + size, oy + 18, "1.0", size=10, color=MUTED))

    p.append(text(ox - 15, oy, "0.0", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 15, oy - size / 2, "0.5", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 15, oy - size, "1.0", size=10, color=MUTED, anchor="end"))

    # Лінія головної послідовності (0,1) -> (1,0)
    p.append(line(ox, oy - size, ox + size, oy, color=FIELD, sw=2.6))
    p.append(text(ox + size * 0.7, oy - size * 0.7 - 8, "Головна послідовність: A + I = 1", size=11, color=FIELD, bold=True))

    # Написи зон
    p.append(text(ox + 65, oy - 35, "ЗОНА БОЛЮ", size=11, color=POS, bold=True))
    p.append(text(ox + 65, oy - 20, "(моноліт, важко міняти)", size=9.5, color=POS))

    p.append(text(ox + size - 65, oy - size + 25, "ЗОНА МАРНОТИ", size=11, color=WARN, bold=True))
    p.append(text(ox + size - 65, oy - size + 40, "(зайві інтерфейси)", size=9.5, color=WARN))

    # Точка зразкового пакета
    px, py = ox + size * 0.35, oy - size * 0.85
    p.append(circle(px, py, 5, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(px + 10, py - 6, "Пакет P (I=0.35, A=0.85)", size=10.5, color=NEG, bold=True, anchor="start"))

    # Відрізок відстані D до лінії
    # Проекція на A + I = 1
    proj_x = ox + size * 0.25
    proj_y = oy - size * 0.75
    p.append(line(px, py, proj_x, proj_y, color=POS, sw=1.8, dash="4 3"))
    p.append(text((px + proj_x) / 2 + 16, (py + proj_y) / 2, "відстань D", size=9.5, color=POS, bold=True))

    p.append(text(W / 2, H - 12,
                  "Баланс: стійкі пакети мають бути абстрактними, мінливі — конкретними",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "main-sequence.svg"), W, H, *p,
           title="Головна послідовність Мартіна: баланс A та I")


if __name__ == "__main__":
    fig_abstraction_concept()
    fig_four_axes()
    fig_leaky_abstraction()
    fig_main_sequence()
    print("All figures generated successfully.")
