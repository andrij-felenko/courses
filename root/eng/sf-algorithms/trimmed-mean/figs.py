# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Усічене середнє» (trimmed-mean)."""

import os
import sys

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від root/eng/sf-algorithms/trimmed-mean)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_trim_mechanism():
    """Ілюстрація 1: Механізм відтинання хвостів (сортування, відкидання k найменших і k найбільших, усереднення ядра)."""
    w, h = 820, 360
    frags = []

    # Заголовок блоків
    frags.append(text(w / 2, 28, "Механізм обчислення усіченого середнього (N = 10, k = 2, α = 20%)", size=16, bold=True))

    # Крок 1: Вхідний масив відліків
    frags.append(text(90, 75, "1. Вхідні дані:", size=13, bold=True, anchor="start"))
    raw_vals = [24.1, 23.9, 120.5, 24.0, 24.2, -15.0, 23.8, 24.3, 24.0, 24.1]
    cell_w, cell_h = 62, 34
    start_x = 90
    y1 = 95
    for i, val in enumerate(raw_vals):
        cx = start_x + i * (cell_w + 8) + cell_w / 2
        cy = y1 + cell_h / 2
        # Підсвічуємо аномалії червоним
        if val > 50 or val < 0:
            fill_c = "#fdecea"
            stroke_c = POS
            txt_c = POS
        else:
            fill_c = FILL
            stroke_c = LINE
            txt_c = INK
        frags.append(rect(cx - cell_w / 2, cy - cell_h / 2, cell_w, cell_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=4))
        frags.append(text(cx, cy + 4, f"{val:.1f}", size=12, color=txt_c, bold=(val > 50 or val < 0)))

    # Стрілка переходу: сортування
    frags.append(arrow(w / 2, y1 + cell_h + 12, w / 2, y1 + cell_h + 38, color=LINE, sw=1.8))
    frags.append(text(w / 2 + 10, y1 + cell_h + 26, "Впорядкування за зростанням (сортування)", size=12, color=MUTED, anchor="start"))

    # Крок 2: Відсортований масив з зонами відтинання
    y2 = 185
    frags.append(text(90, y2 - 10, "2. Відсортований ряд і відтинання країв:", size=13, bold=True, anchor="start"))
    sorted_vals = [-15.0, 23.8, 23.9, 24.0, 24.0, 24.1, 24.1, 24.2, 24.3, 120.5]
    
    # Малюємо 3 зони підкладки
    # Ліва зона (k=2)
    left_w = 2 * (cell_w + 8) - 4
    frags.append(rect(start_x - 4, y2 - 4, left_w, cell_h + 8, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    
    # Центральна зона (N - 2k = 6)
    mid_x = start_x + 2 * (cell_w + 8) - 4
    mid_w = 6 * (cell_w + 8) - 4
    frags.append(rect(mid_x, y2 - 4, mid_w, cell_h + 8, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    
    # Права зона (k=2)
    right_x = start_x + 8 * (cell_w + 8) - 4
    right_w = 2 * (cell_w + 8) - 4
    frags.append(rect(right_x, y2 - 4, right_w, cell_h + 8, fill="#fdecea", stroke=POS, sw=1.5, rx=6))

    for i, val in enumerate(sorted_vals):
        cx = start_x + i * (cell_w + 8) + cell_w / 2
        cy = y2 + cell_h / 2
        is_trimmed = (i < 2 or i >= 8)
        txt_c = POS if is_trimmed else FIELD
        fill_cell = "#ffffff"
        stroke_cell = POS if is_trimmed else FIELD
        frags.append(rect(cx - cell_w / 2, cy - cell_h / 2, cell_w, cell_h, fill=fill_cell, stroke=stroke_cell, sw=1.2, rx=4))
        frags.append(text(cx, cy + 4, f"{val:.1f}", size=12, color=txt_c, bold=True))

    # Підписи під зонами
    frags.append(text(start_x + left_w / 2 - 2, y2 + cell_h + 22, "Відкидаємо k=2 (лівий хвіст)", size=11, color=POS, bold=True))
    frags.append(text(mid_x + mid_w / 2, y2 + cell_h + 22, "Центральне ядро (N - 2k = 6 відліків)", size=12, color=FIELD, bold=True))
    frags.append(text(right_x + right_w / 2 - 2, y2 + cell_h + 22, "Відкидаємо k=2 (правий хвіст)", size=11, color=POS, bold=True))

    # Крок 3: Результат усереднення
    y3 = 285
    frags.append(arrow(mid_x + mid_w / 2, y2 + cell_h + 30, mid_x + mid_w / 2, y3 - 10, color=FIELD, sw=2))
    
    res_box, rw, rh = textbox(
        mid_x + mid_w / 2, y3 + 22,
        "Усічене середнє = (23.9 + 24.0 + 24.0 + 24.1 + 24.1 + 24.2) ÷ 6 = 24.05°C\n"
        "(Звичайне середнє дало б 31.47°C через дикі викиди −15.0 і 120.5)",
        size=13, fill="#f4fbf7", stroke=FIELD, sw=1.8, color=INK, pad=10
    )
    frags.append(res_box)

    render(os.path.join(IMG_DIR, "trim-mechanism.svg"), w, h, *frags)


def fig_tradeoff():
    """Ілюстрація 2: Спектр робастних оцінок (Компроміс між стійкістю до викидів і ефективністю на гаусовому шумі)."""
    w, h = 820, 370
    frags = []

    frags.append(text(w / 2, 28, "Спектр оцінок центру: компроміс між стійкістю та ефективністю", size=16, bold=True))

    # Вісь параметру альфа (від 0% до 50%)
    axis_y = 100
    axis_x1 = 90
    axis_x2 = 730
    frags.append(line(axis_x1, axis_y, axis_x2, axis_y, color=LINE, sw=2))
    
    # Стрілка напрямку альфа
    frags.append(arrow(axis_x2, axis_y, axis_x2 + 25, axis_y, color=LINE, sw=2))
    frags.append(text(axis_x2 + 35, axis_y + 4, "α", size=14, bold=True, anchor="start"))

    # Позиції міток
    points = [
        {"x": 100, "alpha": "α = 0% (k = 0)", "name": "Середнє арифметичне", "bp": "Точка зламу: 0%", "eff": "Ефективність: 100%", "c": POS},
        {"x": 250, "alpha": "α = 10%", "name": "10%-усічене середнє", "bp": "Точка зламу: 10%", "eff": "Ефективність: 96%", "c": FIELD},
        {"x": 420, "alpha": "α = 20%..25%", "name": "Міжквартильне середнє", "bp": "Точка зламу: 25%", "eff": "Ефективність: 88%", "c": FIELD},
        {"x": 670, "alpha": "α = 50%", "name": "Медіана вибірки", "bp": "Точка зламу: 50%", "eff": "Ефективність: 63.7%", "c": NEG},
    ]

    for pt in points:
        px = pt["x"]
        # Засічка на осі
        frags.append(circle(px, axis_y, 6, fill=pt["c"], stroke=LINE, sw=1.5))
        frags.append(text(px, axis_y - 15, pt["alpha"], size=12, bold=True, color=pt["c"]))
        
        # Блок опису внизу
        tb, tw, th = textbox(
            px, 205,
            f"{pt['name']}\n{pt['bp']}\n{pt['eff']}",
            size=12, fill="#ffffff", stroke=pt["c"], sw=1.5, pad=8
        )
        frags.append(line(px, axis_y + 6, px, 205 - th / 2, color=pt["c"], sw=1.2, dash="3,3"))
        frags.append(tb)

    # Пояснювальні стрілки внизу: дві протилежні сили
    y_arrows = 305
    # Стрілка зростання стійкості
    frags.append(arrow(100, y_arrows, 700, y_arrows, color=NEG, sw=2))
    frags.append(text(400, y_arrows - 10, "Зростання стійкості до спайків і точки зламу (Breakdown Point: 0% → 50%)", size=12, color=NEG, bold=True))

    # Стрілка зростання статистичної ефективності
    frags.append(arrow(700, y_arrows + 32, 100, y_arrows + 32, color=POS, sw=2))
    frags.append(text(400, y_arrows + 44, "Зростання ефективності придушення гаусового шуму (ARE: 63.7% → 100%)", size=12, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "tradeoff.svg"), w, h, *frags)


def fig_noise_response():
    """Ілюстрація 3: Реакція фільтрів на комбінацію гаусового шуму, поодиноких спайків та сходинки сигналу."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 26, "Порівняння реакції оцінок на шум, спайки та зміну рівня", size=16, bold=True))

    # Сітка та графічні зони
    # 4 графіки: Вхідний сигнал, Звичайне середнє, Медіана, Усічене середнє
    plots = [
        {"title": "1. Сирий сигнал (гаусів шум + 2 дикі спайки + сходинка на кроці t=12)", "y": 70, "color": INK},
        {"title": "2. Ковзне середнє (N=7): спайки розмазані в горби, сходинка згладжена в рампу", "y": 155, "color": POS},
        {"title": "3. Ковзна медіана (N=7): спайки вибиті, сходинка різка, але лишилася дискретна сходинковість", "y": 240, "color": NEG},
        {"title": "4. Ковзне 25%-усічене середнє (N=7, k=1): спайки вибиті, шум гладенький, сходинка чиста", "y": 325, "color": FIELD},
    ]

    time_pts = 24
    dx = 28
    x_base = 110

    for p_idx, p in enumerate(plots):
        py = p["y"]
        frags.append(text(x_base - 20, py - 12, p["title"], size=12, bold=True, color=p["color"], anchor="start"))
        # Базова лінія графіка
        frags.append(line(x_base, py + 22, x_base + time_pts * dx, py + 22, color="#e5e7eb", sw=1))

        # Генерація форми хвилі
        coords = []
        for t in range(time_pts):
            cx = x_base + t * dx
            base_val = 10 if t < 12 else 26
            if p_idx == 0: # Raw
                noise = ((t * 7 + 3) % 5) - 2
                if t == 5:
                    val = 55 # Спайк вгору
                elif t == 18:
                    val = -15 # Спайк вниз
                else:
                    val = base_val + noise
            elif p_idx == 1: # Mean
                if 2 <= t <= 8:
                    val = base_val + max(0, 18 - abs(t - 5) * 5) # Розмазаний горб
                elif 15 <= t <= 21:
                    val = base_val - max(0, 14 - abs(t - 18) * 4) # Розмазана яма
                elif 10 <= t <= 14:
                    val = 10 + (t - 10) * 4 # Рампа
                else:
                    val = base_val + (((t * 7 + 3) % 5) - 2) * 0.35
            elif p_idx == 2: # Median
                if t == 5 or t == 18:
                    val = base_val # Спайк повністю відкинуто!
                elif 11 <= t <= 13:
                    val = 10 if t < 12 else 26 # Різкий перехід
                else:
                    # Медіана має дискретні сходинки
                    val = base_val + (-1 if t % 4 < 2 else 1)
            else: # Trimmed Mean
                if t == 5 or t == 18:
                    val = base_val # Спайк відкинуто!
                elif 10 <= t <= 14:
                    val = 10 + (t - 10) * 3.8 # Швидкий чистий перехід
                else:
                    # Гладке придушення шуму
                    val = base_val + (((t * 7 + 3) % 5) - 2) * 0.25

            # Переведення значення в Y координату
            cy = py + 22 - (val - 10) * 0.75
            coords.append((cx, cy))

        # Малюємо з'єднувальну лінію графіка
        for i in range(len(coords) - 1):
            frags.append(line(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1], color=p["color"], sw=1.8))
            frags.append(circle(coords[i][0], coords[i][1], 2.5, fill=p["color"], stroke=p["color"], sw=1))
        frags.append(circle(coords[-1][0], coords[-1][1], 2.5, fill=p["color"], stroke=p["color"], sw=1))

    render(os.path.join(IMG_DIR, "noise-response.svg"), w, h, *frags)


def fig_sliding_buffer():
    """Ілюстрація 4: Структура ковзного вікна усіченого середнього з індексним масивом."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Ковзне вікно: кільцевий буфер і відсортований індексний ряд", size=16, bold=True))

    # Ліва частина: Кільцевий буфер (часовий порядок)
    frags.append(text(210, 65, "Кільцевий буфер (хронологічний порядок, W=6)", size=13, bold=True))
    
    cb_vals = [24.1, 23.9, 120.0, 24.2, 23.8, 24.0]
    cb_w, cb_h = 56, 36
    cb_x0 = 45
    cb_y0 = 85

    for i, v in enumerate(cb_vals):
        bx = cb_x0 + i * (cb_w + 6)
        is_newest = (i == 2) # Найновіший спайк
        is_oldest = (i == 3) # Наступний на виліт
        f_c = "#fdecea" if is_newest else ("#fff8e1" if is_oldest else FILL)
        s_c = POS if is_newest else (LINE)
        frags.append(rect(bx, cb_y0, cb_w, cb_h, fill=f_c, stroke=s_c, sw=1.5, rx=4))
        frags.append(text(bx + cb_w / 2, cb_y0 + 22, f"{v:.1f}", size=12, bold=is_newest, color=POS if is_newest else INK))
        frags.append(text(bx + cb_w / 2, cb_y0 + cb_h + 16, f"idx={i}", size=10, color=MUTED))

    # Стрілка запису
    frags.append(arrow(cb_x0 + 2 * (cb_w + 6) + cb_w / 2, cb_y0 - 22, cb_x0 + 2 * (cb_w + 6) + cb_w / 2, cb_y0 - 2, color=POS, sw=1.8))
    frags.append(text(cb_x0 + 2 * (cb_w + 6) + cb_w / 2, cb_y0 - 28, "Новий відлік (head)", size=11, color=POS, bold=True))

    # Права частина / Нижній рівень: Впорядкований індексний масив
    frags.append(text(210, 185, "Відсортований масив індексів / значень", size=13, bold=True))
    
    # Відсортовані: idx 4 (23.8), idx 1 (23.9), idx 5 (24.0), idx 0 (24.1), idx 3 (24.2), idx 2 (120.0)
    sorted_slots = [
        {"idx": 4, "val": 23.8, "trim": True},
        {"idx": 1, "val": 23.9, "trim": False},
        {"idx": 5, "val": 24.0, "trim": False},
        {"idx": 0, "val": 24.1, "trim": False},
        {"idx": 3, "val": 24.2, "trim": False},
        {"idx": 2, "val": 120.0, "trim": True},
    ]

    sb_y0 = 205
    for i, slot in enumerate(sorted_slots):
        bx = cb_x0 + i * (cb_w + 6)
        is_trimmed = slot["trim"]
        f_c = "#fdecea" if is_trimmed else "#eafaf1"
        s_c = POS if is_trimmed else FIELD
        frags.append(rect(bx, sb_y0, cb_w, cb_h, fill=f_c, stroke=s_c, sw=1.5, rx=4))
        frags.append(text(bx + cb_w / 2, sb_y0 + 22, f"{slot['val']:.1f}", size=12, bold=True, color=POS if is_trimmed else FIELD))
        frags.append(text(bx + cb_w / 2, sb_y0 + cb_h + 16, f"[buf {slot['idx']}]", size=10, color=MUTED))

    # Виділення зони підсумовування
    sum_x1 = cb_x0 + 1 * (cb_w + 6) - 2
    sum_w = 4 * (cb_w + 6) - 2
    frags.append(rect(sum_x1, sb_y0 - 4, sum_w, cb_h + 8, fill="none", stroke=FIELD, sw=2, rx=6))
    frags.append(text(sum_x1 + sum_w / 2, sb_y0 + cb_h + 34, "Вікно підсумовування (ранги від k=1 до W-k-1=4)", size=11, color=FIELD, bold=True))

    # Права картка: Алгоритм оновлення
    card_tb, cw, ch = textbox(
        615, 180,
        "Покрокове оновлення O(W):\n"
        "1. Знайти позицію старого відліку\n"
        "   у відсортованому списку (бінпошук);\n"
        "2. Вилучити його зсувом масиву;\n"
        "3. Вставити новий відлік на належне\n"
        "   місце зі збереженням сортування;\n"
        "4. Додати елементи в межах [k, W-k-1]\n"
        "   та поділити на (W - 2k).",
        size=11, fill="#ffffff", stroke=LINE, sw=1.5, pad=10
    )
    frags.append(card_tb)

    render(os.path.join(IMG_DIR, "sliding-buffer.svg"), w, h, *frags)


def main():
    fig_trim_mechanism()
    fig_tradeoff()
    fig_noise_response()
    fig_sliding_buffer()
    print("All figures successfully generated in img/")


if __name__ == "__main__":
    main()
