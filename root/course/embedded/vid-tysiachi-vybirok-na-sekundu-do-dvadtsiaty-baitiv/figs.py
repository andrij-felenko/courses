# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to root/scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. sensor-pipeline-architecture: Бортовий конвеєр стиснення й агрегації ──
def fig_pipeline_architecture():
    W, H = 940, 360
    p = []

    # Тло
    p.append(rect(10, 10, 920, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок зверху
    p.append(text(470, 35, "Конвеєр скорочення даних: від 1000 семплів/с до 20 байтів/хв", size=14, color=INK, bold=True))

    stages = [
        ("1. Сенсорний DMA", "1000 семплів/с\n16 біт на відлік\n16 000 біт/с (сирі)", POS, 100),
        ("2. CIC / FIR Дециматор", "Проріджування 10:1\nАнтиаліасинг LPF\n100 семплів/с (+1.6b)", "#d97706", 280),
        ("3. Статистичне вікно", "Акумулятор Велфорда\nRMS, Mean, Min/Max\nCF, дисперсія (1 с)", FIELD, 460),
        ("4. Фільтр SDT / Deadband", "Відсікання шуму\nДетекція трендів\nСтиснення 10:1..50:1", NEG, 640),
        ("5. Пакувальник LPWAN", "Delta-ZigZag + Varint\n20 байтів на хвилину\nLoRaWAN / NB-IoT", "#7c3aed", 820),
    ]

    for title, desc, col, cx in stages:
        # Картка етапу
        p.append(rect(cx - 75, 65, 150, 175, fill="#f8fafc", stroke=col, sw=2, rx=6))
        # Смужка кольору зверху
        p.append(rect(cx - 75, 65, 150, 26, fill=col, stroke=col, sw=1, rx=4))
        p.append(text(cx, 83, title, size=11, color="#ffffff", bold=True))
        
        # Опис всередині
        lines = desc.split("\n")
        for i, ln in enumerate(lines):
            p.append(text(cx, 125 + i * 22, ln, size=11, color=INK))

    # Стрілки між етапами
    for i in range(len(stages) - 1):
        x_from = stages[i][3] + 75
        x_to = stages[i+1][3] - 75
        p.append(arrow(x_from + 2, 152, x_to - 2, 152, color=LINE, sw=2))

    # Нижня панель порівняння швидкості / енергії
    p.append(rect(30, 260, 880, 70, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(470, 282, "Порівняння навантаження каналу й енергетичного бюджету", size=12, color=INK, bold=True))
    
    p.append(text(210, 310, "Сирий потік: 120 000 байт/хв  (Радіо 100% On, батарея 2 дні)", size=11, color=POS, bold=True))
    p.append(text(690, 310, "Після конвеєра: 20 байт/хв  (Радіо Duty 0.05%, батарея > 7 років)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "sensor-pipeline-architecture.svg"), W, H, *p,
           title="Архітектура бортового конвеєра обробки сенсорних даних")


# ── 2. aliasing-and-decimation: Децимація та небезпека аліасингу ──────────────
def fig_aliasing_decimation():
    W, H = 920, 380
    p = []

    # Загальне тло
    p.append(rect(10, 10, 900, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(460, 32, "Спектральний аналіз децимації: наївне проріджування проти антиаліасингу", size=13, color=INK, bold=True))

    # Ліва колонка: Наївне проріджування (Aliasing)
    p.append(rect(30, 50, 415, 300, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(237, 72, "Наївне проріджування 10× (без LPF)", size=12, color=POS, bold=True))

    # Графік 1: Вхідний спектр
    p.append(rect(50, 90, 375, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(line(70, 165, 410, 165, color=INK, sw=1.2)) # вісь f
    p.append(arrow(70, 165, 70, 100, color=INK, sw=1.2)) # вісь A
    p.append(text(410, 180, "f, Гц", size=10, color=MUTED))
    p.append(text(60, 105, "A", size=10, color=MUTED))

    # Сигнал (0..30 Гц)
    p.append(rect(75, 120, 45, 45, fill="#bbf7d0", stroke=FIELD, sw=1.2))
    p.append(text(97, 145, "Сигнал", size=9, color=FIELD, bold=True))

    # Високочастотний шум (80..450 Гц)
    p.append(rect(150, 140, 240, 25, fill="#fee2e2", stroke=POS, sw=1.2))
    p.append(text(270, 155, "Шум і гармоніки (80..450 Гц)", size=9, color=POS))
    p.append(text(395, 177, "500 (Fs/2)", size=9, color=MUTED))

    # Графік 2: Результат після наївного викидання відліків (Folded Aliasing)
    p.append(rect(50, 210, 375, 125, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(line(70, 305, 410, 305, color=INK, sw=1.2))
    p.append(arrow(70, 305, 70, 220, color=INK, sw=1.2))
    p.append(text(400, 320, "50 Гц (Fs_new/2)", size=10, color=MUTED))

    # Накладання: сигнал + шум поверх
    p.append(rect(75, 260, 45, 45, fill="#bbf7d0", stroke=FIELD, sw=1.2))
    p.append(rect(75, 235, 45, 25, fill="#fca5a5", stroke=POS, sw=1.2))
    p.append(text(97, 285, "Сигнал", size=9, color=FIELD, bold=True))
    p.append(text(97, 250, "+Аліасинг", size=9, color=POS, bold=True))
    p.append(text(260, 265, "Шум із 10 смуг згорнувся в 0..50 Гц", size=10, color=POS, bold=True))
    p.append(text(260, 285, "SNR впав на 10 dB! Фатальні спотворення.", size=10, color=POS))

    # Права колонка: Фільтрована децимація (CIC / FIR)
    p.append(rect(475, 50, 415, 300, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(682, 72, "Децимація з антиаліасинговим фільтром", size=12, color=FIELD, bold=True))

    # Графік 3: Фільтрація вхідного спектра
    p.append(rect(495, 90, 375, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(line(515, 165, 855, 165, color=INK, sw=1.2))
    p.append(arrow(515, 165, 515, 100, color=INK, sw=1.2))
    p.append(text(855, 180, "f, Гц", size=10, color=MUTED))

    # Сигнал + маска фільтра
    p.append(rect(520, 120, 45, 45, fill="#bbf7d0", stroke=FIELD, sw=1.2))
    p.append(text(542, 145, "Сигнал", size=9, color=FIELD, bold=True))
    # Маска LPF
    p.append(line(520, 110, 580, 110, color="#2563eb", sw=2))
    p.append(line(580, 110, 620, 165, color="#2563eb", sw=2, dash="3 2"))
    p.append(text(650, 125, "Зріз LPF (40 Гц)", size=10, color="#2563eb", bold=True))
    p.append(text(740, 155, "Шум придушено на >60 dB", size=9, color=MUTED))

    # Графік 4: Чистий спектр після децимації
    p.append(rect(495, 210, 375, 125, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(line(515, 305, 855, 305, color=INK, sw=1.2))
    p.append(arrow(515, 305, 515, 220, color=INK, sw=1.2))
    p.append(text(845, 320, "50 Гц (Fs_new/2)", size=10, color=MUTED))

    # Чистий сигнал
    p.append(rect(520, 260, 45, 45, fill="#bbf7d0", stroke=FIELD, sw=1.2))
    p.append(text(542, 285, "Чистий", size=9, color=FIELD, bold=True))
    p.append(text(690, 265, "Аліасинг відсутній у смузі Найквіста", size=10, color=FIELD, bold=True))
    p.append(text(690, 285, "Збільшення ENOB на +1.6 біта (+10 dB SNR)", size=10, color=FIELD))

    render(os.path.join(OUT, "aliasing-and-decimation.svg"), W, H, *p,
           title="Аліасинг та антиаліасингова фільтрація при децимації")


# ── 3. swing-door-trending: Алгоритм стиснення трендів Swing Door ─────────────
def fig_swing_door_trending():
    W, H = 900, 380
    p = []

    # Тло
    p.append(rect(10, 10, 880, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(450, 32, "Геометрія алгоритму Swing Door Trending (SDT)", size=13, color=INK, bold=True))

    # Фон системи координат
    p.append(rect(50, 50, 800, 280, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))

    # Осі
    p.append(arrow(90, 290, 830, 290, color=INK, sw=1.5))
    p.append(arrow(90, 290, 90, 65, color=INK, sw=1.5))
    p.append(text(830, 310, "Час (t)", size=11, color=INK, bold=True))
    p.append(text(70, 75, "Значення (y)", size=11, color=INK, bold=True))

    # Опорна точка P0 (Pivot)
    x0, y0 = 150, 200
    p.append(circle(x0, y0, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(text(x0 - 25, y0 + 5, "P_0 (Pivot)", size=11, color=POS, bold=True))

    # Коридор толерантності ±epsilon навколо P0
    eps = 35
    p.append(line(x0, y0 - eps, x0, y0 + eps, color=POS, sw=2.5))
    p.append(line(x0 - 6, y0 - eps, x0 + 6, y0 - eps, color=POS, sw=1.5))
    p.append(line(x0 - 6, y0 + eps, x0 + 6, y0 + eps, color=POS, sw=1.5))
    p.append(text(x0 - 15, y0 - eps + 4, "+ε", size=10, color=POS, bold=True))
    p.append(text(x0 - 15, y0 + eps + 4, "-ε", size=10, color=POS, bold=True))

    # Точки відліків у часі
    pts = [
        (230, 192),  # P1
        (320, 178),  # P2
        (420, 160),  # P3
        (510, 142),  # P4 (остання валідна)
        (600, 100),  # P5 (злам тренду - вихід за межі)
    ]

    for i, (px, py) in enumerate(pts):
        col = NEG if i < 4 else POS
        p.append(circle(px, py, 4, fill=col, stroke=INK, sw=1.2))
        lbl = "P_%d" % (i + 1)
        p.append(text(px, py - 12, lbl, size=10, color=col, bold=True))

    # Верхні й нижні двері (промені від P0+eps і P0-eps)
    # Верхній промінь до P4
    p.append(line(x0, y0 - eps, 550, 130, color="#2563eb", sw=1.5, dash="4 3"))
    p.append(text(340, 130, "Верхній промінь S_upper (звужується вниз)", size=10, color="#2563eb"))

    # Нижній промінь до P4
    p.append(line(x0, y0 + eps, 550, 165, color="#16a34a", sw=1.5, dash="4 3"))
    p.append(text(340, 240, "Нижній промінь S_lower (звужується вгору)", size=10, color="#16a34a"))

    # Зона дозволеного коридору між променями
    p.append(text(320, 195, "Дозволений коридор", size=10, color=MUTED, italic=True))

    # Стрибок на точці P5: нижній промінь мусить піднятися вище верхнього!
    p.append(line(x0, y0 + eps, 600, 100, color=POS, sw=1.5, dash="2 2"))
    p.append(text(680, 105, "Точка P_5: S_lower > S_upper!", size=10, color=POS, bold=True))
    p.append(text(680, 125, "Двері перетнулися — фіксація P_4", size=10, color=POS))

    # Відрізок переданого тренду (P0 -> P4)
    p.append(line(x0, y0, 510, 142, color="#7c3aed", sw=3))
    p.append(text(320, 168, "Лінійний сегмент тренду (1 передача)", size=10, color="#7c3aed", bold=True))

    # Новий pivot у P4
    p.append(circle(510, 142, 6, fill="#7c3aed", stroke=INK, sw=1.5))
    p.append(text(510, 172, "Новий Pivot P_4", size=11, color="#7c3aed", bold=True))

    render(os.path.join(OUT, "swing-door-trending.svg"), W, H, *p,
           title="Геометричний принцип стиснення Swing Door Trending")


if __name__ == "__main__":
    fig_pipeline_architecture()
    fig_aliasing_decimation()
    fig_swing_door_trending()
    print("All figures generated successfully.")
