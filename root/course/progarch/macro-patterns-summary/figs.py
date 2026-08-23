# -*- coding: utf-8 -*-
"""Генератор фігур для теми macro-patterns-summary.
Вивід — ./img/*.svg. svgkit імпортуємо з кореневої папки scripts/.
"""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *


def make_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir


def fig1_spectrum():
    """Двовимірний спектр макро-патернів: Ізоляція меж проти Фізичної розподіленості."""
    w, h = 900, 560
    img_dir = make_img_dir()
    out_path = os.path.join(img_dir, "macro-patterns-spectrum.svg")

    frags = []

    # Заголовок полотна
    frags.append(text(w / 2, 30, "Спектр макро-патернів організації систем", size=18, bold=True))

    # Вісі координат
    # X-вісь: Дисципліна й ізоляція меж (Coupling & Boundary Enforcement)
    frags.append(line(120, 480, 840, 480, color=LINE, sw=2))
    frags.append(arrow(830, 480, 850, 480, color=LINE, sw=2))
    frags.append(text(480, 520, "Дисципліна й інкапсуляція меж (від спагеті до ізольованих контекстів) →", size=13, bold=True))

    # Y-вісь: Фізична розподіленість і мережеві межі (Distribution & Infrastructure)
    frags.append(line(120, 480, 120, 70, color=LINE, sw=2))
    frags.append(arrow(120, 80, 120, 60, color=LINE, sw=2))
    frags.append(mtext(60, 250, "Фізична\nрозподіленість\n(процеси/мережі)\n↑", size=12, bold=True, anchor="middle"))

    # Сітка та квадранти
    frags.append(line(120, 275, 840, 275, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(480, 70, 480, 480, color=MUTED, sw=1, dash="4,4"))

    # Зелена зона дефолту (Модульний моноліт)
    frags.append(rect(490, 285, 340, 185, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(660, 305, "Зона дефолтного старту", size=11, color=FIELD, bold=True))

    # Червона зона небезпеки (Розподілений моноліт)
    frags.append(rect(130, 80, 340, 185, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(300, 100, "Зона високого ризику (Антипатерн)", size=11, color=POS, bold=True))

    # Карточки патернів
    # 1. Класичний моноліт (низька ізоляція, 1 процес)
    b1, _, _ = textbox(280, 380, "Класичний моноліт\n• 1 процес / 1 БД\n• Протікання моделей\n• Високий blast radius", size=12, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5)
    frags.append(b1)

    # 2. Модульний моноліт (висока ізоляція, 1 процес) - ДЕФОЛТ
    b2, _, _ = textbox(660, 380, "Модульний моноліт (Дефолт)\n• 1 процес / чисті межі\n• Нульовий податок мережі\n• Легкий рефакторинг", size=12, fill="#eaafaf", stroke=FIELD, sw=2, color="#1e8449", bold=True)
    # Correct fill to light green
    b2_correct, _, _ = textbox(660, 380, "Модульний моноліт (Дефолт)\n• 1 процес / чисті межі\n• Нульовий податок мережі\n• Легкий рефакторинг", size=12, fill="#d4efdf", stroke=FIELD, sw=2, color="#1e8449", bold=True)
    frags.append(b2_correct)

    # 3. Мікросервіси (висока ізоляція, висока розподіленість)
    b3, _, _ = textbox(660, 170, "Мікросервіси\n• N процесів / N баз даних\n• Автономія команд і деплою\n• Податок мережі та саги", size=12, fill="#e8f8f5", stroke=NEG, sw=1.5)
    frags.append(b3)

    # 4. Серверлесс (максимальна роздрібненість)
    b4, _, _ = textbox(810, 100, "Серверлесс (FaaS)\n• Функції за подією\n• Cold starts / Cascades", size=10, fill="#fef9e7", stroke="#f39c12", sw=1.5)
    frags.append(b4)

    # 5. Розподілений моноліт (низька ізоляція, висока розподіленість)
    b5, _, _ = textbox(280, 170, "Розподілений моноліт\n• Зчеплені мережеві виклики\n• Спільна БД / Каскади відмов\n• Найгірше з двох світів", size=12, fill="#fadbd8", stroke=POS, sw=2, color=POS, bold=True)
    frags.append(b5)

    # Еволюційні стрілки
    frags.append(arrow(370, 380, 520, 380, color=FIELD, sw=2))
    frags.append(text(445, 370, "Дисципліна", size=10, color=FIELD, bold=True))

    frags.append(arrow(660, 310, 660, 240, color=NEG, sw=2))
    frags.append(text(675, 275, "Драйвер росту", size=10, color=NEG, bold=True))

    frags.append(arrow(380, 380, 290, 240, color=POS, sw=1.8))
    frags.append(text(345, 300, "Поспішний розкол", size=10, color=POS, bold=True))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig2_comparison_matrix():
    """Порівняльна матриця 5 макро-патернів за ключовими інженерними вимірами."""
    w, h = 920, 520
    img_dir = make_img_dir()
    out_path = os.path.join(img_dir, "macro-patterns-comparison-matrix.svg")

    frags = []
    frags.append(text(w / 2, 28, "Аналітична матриця властивостей макро-патернів", size=18, bold=True))

    # Стовпчики Таблиці:
    # 0: Вимір
    # 1: Класичний моноліт
    # 2: Модульний моноліт
    # 3: Мікросервіси
    # 4: Серверлесс
    # 5: Розподілений моноліт

    col_x = [30, 210, 350, 490, 630, 770]
    col_w = [170, 130, 130, 130, 130, 130]
    row_y = [60, 110, 170, 230, 290, 350, 410, 470]

    headers = [
        "Архітектурна\nвластивість",
        "Класичний\nмоноліт",
        "Модульний\nмоноліт",
        "Мікросервісна\nструктура",
        "Серверлесс\n(FaaS)",
        "Розподілений\nмоноліт",
    ]

    # Шапка
    for j, h_text in enumerate(headers):
        x = col_x[j]
        cw = col_w[j]
        bg_c = "#eaecee" if j == 0 else ("#d4efdf" if j == 2 else ("#fadbd8" if j == 5 else FILL))
        frags.append(rect(x, row_y[0], cw, 42, fill=bg_c, stroke=LINE, sw=1.5, rx=4))
        frags.append(mtext(x + cw / 2, row_y[0] + 16, h_text, size=11, bold=True))

    # Дані
    rows_data = [
        ("Мережевий податок & latency", "Низький (ns)", "Низький (ns)", "Високий (ms)", "Вкрай високий", "Критичний"),
        ("Транзакційна атомарність", "Проста (ACID)", "Проста (ACID)", "Складна (Sagas)", "Подійна / Складна", "Зламано / Крихка"),
        ("Оборотність рефакторингу", "Висока", "Максимальна", "Обмежена", "Низька", "Нездійсненна"),
        ("Автономія деплою команд", "Відсутня", "Поміркована", "Висока", "Висока", "Ілюзорна (блокування)"),
        ("Операційна складність", "Мінімальна", "Низька", "Висока (K8s/Mesh)", "Середня/Managed", "Максимальне пекло"),
        ("Радіус вибуху відмов", "Повний процес", "Контрольований", "Ізольований", "Ізольований", "Повний каскад"),
        ("Дефолтна придатність", "Для стартапів", "УНІВЕРСАЛЬНИЙ", "За наявності вимог", "Для event-driven", "АНТИПАТЕРН"),
    ]

    for i, row in enumerate(rows_data):
        y = row_y[i + 1]
        metric_name = row[0]
        values = row[1:]

        # Колонка виміру
        frags.append(rect(col_x[0], y, col_w[0], 52, fill="#f4f6f8", stroke=LINE, sw=1, rx=3))
        frags.append(mtext(col_x[0] + 8, y + 22, metric_name, size=11, bold=True, anchor="start"))

        # Значення
        for j, val in enumerate(values):
            x = col_x[j + 1]
            cw = col_w[j + 1]
            fill_c = "#ffffff"
            text_c = INK
            is_bold = False

            if j == 1:  # Модульний моноліт
                fill_c = "#e8f8f5"
                text_c = "#1e8449"
                is_bold = True
            elif j == 4:  # Розподілений моноліт
                fill_c = "#fdecea"
                text_c = POS
                is_bold = True

            frags.append(rect(x, y, cw, 52, fill=fill_c, stroke=LINE, sw=1, rx=3))
            frags.append(mtext(x + cw / 2, y + 22, val, size=10.5, color=text_c, bold=is_bold))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig3_latency_cascade():
    """Порівняння каскаду затримок та транзакційних меж у чотирьох сценаріях виконання."""
    w, h = 880, 520
    img_dir = make_img_dir()
    out_path = os.path.join(img_dir, "latency-cascade-breakdown.svg")

    frags = []
    frags.append(text(w / 2, 28, "Каскад затримок та надійність виконання за макро-патернами", size=17, bold=True))

    # Сценарій 1: Модульний моноліт
    y1 = 70
    frags.append(rect(30, y1, 820, 95, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(45, y1 + 22, "1. Модульний моноліт (Виклики в пам'яті):", size=12, color="#1e8449", bold=True, anchor="start"))
    b_m1, _, _ = textbox(280, y1 + 58, "Модуль A\n(Auth)", size=11, fill="#ffffff", stroke=FIELD)
    b_m2, _, _ = textbox(480, y1 + 58, "Модуль B\n(Orders)", size=11, fill="#ffffff", stroke=FIELD)
    b_m3, _, _ = textbox(680, y1 + 58, "Модуль C\n(Inventory)", size=11, fill="#ffffff", stroke=FIELD)
    frags.extend([b_m1, b_m2, b_m3])
    frags.append(arrow(340, y1 + 58, 420, y1 + 58, color=FIELD, sw=1.5))
    frags.append(arrow(540, y1 + 58, 620, y1 + 58, color=FIELD, sw=1.5))
    frags.append(text(380, y1 + 46, "50 ns", size=10, color=FIELD, bold=True))
    frags.append(text(580, y1 + 46, "50 ns", size=10, color=FIELD, bold=True))
    frags.append(text(780, y1 + 58, "Загалом: ~2 мс\n(1 DB COMMIT)", size=11, color="#1e8449", bold=True))

    # Сценарій 2: Асинхронні / Подійно-орієнтовані мікросервіси
    y2 = 180
    frags.append(rect(30, y2, 820, 95, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(45, y2 + 22, "2. Незалежні мікросервіси (Асинхронні події / Outbox):", size=12, color=NEG, bold=True, anchor="start"))
    b_s1, _, _ = textbox(240, y2 + 58, "Сервіс A\n(БД A)", size=11, fill="#ffffff", stroke=NEG)
    b_bus, _, _ = textbox(440, y2 + 58, "Event Bus\n(Kafka / Rabbit)", size=11, fill="#d6eaf8", stroke=NEG)
    b_s2, _, _ = textbox(640, y2 + 58, "Сервіс B\n(БД B)", size=11, fill="#ffffff", stroke=NEG)
    frags.extend([b_s1, b_bus, b_s2])
    frags.append(arrow(300, y2 + 58, 380, y2 + 58, color=NEG, sw=1.5))
    frags.append(arrow(500, y2 + 58, 580, y2 + 58, color=NEG, sw=1.5))
    frags.append(text(340, y2 + 46, "Event", size=10, color=NEG))
    frags.append(text(540, y2 + 46, "Consume", size=10, color=NEG))
    frags.append(text(780, y2 + 58, "Ізольовано!\nEventual Consistency", size=11, color=NEG, bold=True))

    # Сценарій 3: Серверлесс FaaS ланцюг
    y3 = 290
    frags.append(rect(30, y3, 820, 95, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(45, y3 + 22, "3. Серверлесс ланцюжок (Cold Start + Event Pipeline):", size=12, color="#b9770e", bold=True, anchor="start"))
    b_f1, _, _ = textbox(250, y3 + 58, "Function 1\n(Cold start +250ms)", size=10, fill="#ffffff", stroke="#f39c12")
    b_f2, _, _ = textbox(460, y3 + 58, "SQS / EventBridge\n(+15ms)", size=10, fill="#ffffff", stroke="#f39c12")
    b_f3, _, _ = textbox(670, y3 + 58, "Function 2\n(Warm execution)", size=10, fill="#ffffff", stroke="#f39c12")
    frags.extend([b_f1, b_f2, b_f3])
    frags.append(arrow(320, y3 + 58, 395, y3 + 58, color="#f39c12", sw=1.5))
    frags.append(arrow(525, y3 + 58, 610, y3 + 58, color="#f39c12", sw=1.5))
    frags.append(text(780, y3 + 58, "Варіативна latency\np99 > 400 мс", size=11, color="#b9770e", bold=True))

    # Сценарій 4: Розподілений моноліт (Синхронний каскад)
    y4 = 400
    frags.append(rect(30, y4, 820, 95, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(45, y4 + 22, "4. Розподілений моноліт (Синхронний мережевий каскад):", size=12, color=POS, bold=True, anchor="start"))
    b_d1, _, _ = textbox(230, y4 + 58, "Сервіс A\nHTTP client", size=11, fill="#ffffff", stroke=POS)
    b_d2, _, _ = textbox(440, y4 + 58, "Сервіс B\nHTTP client", size=11, fill="#ffffff", stroke=POS)
    b_d3, _, _ = textbox(650, y4 + 58, "Сервіс C\n(Падіння!)", size=11, fill="#fadbd8", stroke=POS, color=POS, bold=True)
    frags.extend([b_d1, b_d2, b_d3])
    frags.append(arrow(290, y4 + 58, 380, y4 + 58, color=POS, sw=1.8))
    frags.append(arrow(500, y4 + 58, 590, y4 + 58, color=POS, sw=1.8))
    frags.append(text(335, y4 + 46, "Sync HTTP 15ms", size=9, color=POS))
    frags.append(text(545, y4 + 46, "Sync HTTP 15ms", size=9, color=POS))
    frags.append(text(780, y4 + 58, "Каскадний краш!\nA=A1·A2·A3 ↓", size=11, color=POS, bold=True))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig1_spectrum()
    fig2_comparison_matrix()
    fig3_latency_cascade()
