# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Алгоритм трекінгу об'єктів SORT»."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def dashed_rect(x, y, w, h, fill="none", stroke=LINE, sw=1.5, rx=4, dash="4,4"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (x, y, w, h, rx, fill, stroke, sw, dash))


def fig1_sort_pipeline():
    """Конвеєр обробки кадру в алгоритмі SORT."""
    w, h = 880, 480
    p = []

    # 1. Вхідні блоки
    b_det = fitbox(30, 60, 170, 70, "Детекції кадру t\n[x₁, y₁, x₂, y₂, score]\n(YOLO / RetinaNet)", fill="#eaf2f8", stroke="#2980b9")
    b_trk = fitbox(30, 240, 170, 70, "Треки з кадру t−1\nСтан x: [u, v, s, r, …]\nКоваріація P", fill="#fdf2e9", stroke="#d35400")
    p.extend([b_det, b_trk])

    # 2. Крок передбачення
    b_pred = fitbox(250, 240, 170, 70, "Фільтр Калмана:\nПередбачення (Predict)\nx̂⁻ = F·x̂,  P⁻ = FPFᵀ+Q", fill="#fef9e7", stroke="#d4ac0d")
    p.append(b_pred)
    p.append(arrow(200, 275, 250, 275, color=LINE, sw=1.8))

    # 3. Обчислення матриці вартості
    b_cost = fitbox(470, 150, 180, 80, "Матриця витрат (Cost)\nC[i, j] = 1 − IoU(Tᵢ, Dⱼ)\nВідсікання: IoU < IoU_min", fill="#e8f8f5", stroke="#16a085")
    p.append(b_cost)

    # Стрілки до матриці витрат
    p.append(arrow(200, 95, 470, 170, color=LINE, sw=1.8))
    p.append(arrow(420, 275, 470, 210, color=LINE, sw=1.8))

    # 4. Угорський алгоритм
    b_hung = fitbox(470, 290, 180, 65, "Угорський алгоритм\n(Linear Assignment)\nМінімізація сумарної ціни", fill="#f4ecf7", stroke="#8e44ad")
    p.append(b_hung)
    p.append(arrow(560, 230, 560, 290, color=LINE, sw=1.8))

    # 5. Три результати асоціації
    b_match = fitbox(700, 100, 160, 85, "Зіставлені пари\n• Калман Update (z)\n• time_since_update = 0\n• hits += 1", fill="#eafaf1", stroke=FIELD)
    b_un_det = fitbox(700, 235, 160, 75, "Незв'язані детекції\n• Створення треку\n• time_since_update = 0\n• hits = 1", fill="#ebf5fb", stroke="#2457d6")
    b_un_trk = fitbox(700, 360, 160, 85, "Незв'язані треки\n• time_since_update += 1\n• Якщо age > max_age:\n  Видалення треку", fill="#fdecea", stroke=POS)
    p.extend([b_match, b_un_det, b_un_trk])

    # Розгалуження від угорського алгоритму
    p.append(arrow(650, 310, 700, 140, color=FIELD, sw=1.8))
    p.append(arrow(650, 322, 700, 270, color="#2457d6", sw=1.8))
    p.append(arrow(650, 335, 700, 400, color=POS, sw=1.8))

    # Вихідний потік підтверджених треків
    p.append(line(780, 185, 780, 215, color=FIELD, sw=1.5, dash="4,4"))
    b_out = fitbox(250, 390, 380, 60, "Вихідний фільтр: видавати трек, лише якщо hits ≥ min_hits\nАктивні треки [ID, x₁, y₁, x₂, y₂] передаються клієнту", fill="#ffffff", stroke="#2c3e50", sw=2)
    p.append(b_out)
    p.append(arrow(700, 160, 630, 410, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "fig1-sort-pipeline.svg"), w, h, *p)


def fig2_kalman_state_box():
    """Геометрія рамки та 7-вимірний вектор стану в SORT."""
    w, h = 840, 400
    p = []

    # Рамка системи координат кадру
    p.append(rect(40, 40, 380, 320, fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=4))
    p.append(text(60, 65, "Кадр зображення (W × H)", size=12, color=MUTED, anchor="start"))

    # Осі координат
    p.append(arrow(50, 50, 130, 50, color="#7f8c8d", sw=1.5))
    p.append(text(140, 54, "x", size=12, color="#7f8c8d", anchor="start"))
    p.append(arrow(50, 50, 50, 130, color="#7f8c8d", sw=1.5))
    p.append(text(50, 145, "y", size=12, color="#7f8c8d", anchor="middle"))

    # Габаритна рамка
    bx, by, bw, bh = 140, 110, 160, 200
    p.append(rect(bx, by, bw, bh, fill="#ebf5fb", stroke="#2980b9", sw=2.5, rx=2))

    # Центр (u, v)
    cx, cy = bx + bw / 2, by + bh / 2
    p.append(circle(cx, cy, 4, fill=POS, stroke=POS))
    p.append(text(cx + 8, cy - 8, "Центр (u, v)", size=13, color=POS, bold=True, anchor="start"))

    # Розміри w та h
    p.append(line(bx, by - 12, bx + bw, by - 12, color="#2980b9", sw=1.5))
    p.append(line(bx, by - 18, bx, by - 6, color="#2980b9", sw=1.5))
    p.append(line(bx + bw, by - 18, bx + bw, by - 6, color="#2980b9", sw=1.5))
    p.append(text(cx, by - 18, "w (ширина)", size=12, color="#2980b9", anchor="middle"))

    p.append(line(bx + bw + 12, by, bx + bw + 12, by + bh, color="#2980b9", sw=1.5))
    p.append(line(bx + bw + 6, by, bx + bw + 18, by, color="#2980b9", sw=1.5))
    p.append(line(bx + bw + 6, by + bh, bx + bw + 18, by + bh, color="#2980b9", sw=1.5))
    p.append(text(bx + bw + 18, cy, "h (висота)", size=12, color="#2980b9", anchor="start"))

    # Вектор швидкості (u_dot, v_dot)
    p.append(arrow(cx, cy, cx + 55, cy + 40, color=POS, sw=2.2))
    p.append(text(cx + 60, cy + 50, "Вектор швидкості (u̇, v̇)", size=12, color=POS, bold=True, anchor="start"))

    # Права частина: формули та опис стану
    b_state = fitbox(460, 40, 350, 160,
                     "Вектор стану Калмана (7D):\n"
                     "x = [ u,  v,  s,  r,  u̇,  v̇,  ṡ ]ᵀ\n\n"
                     "• u, v — координати центра рамки\n"
                     "• s = w · h — площа (масштаб / scale)\n"
                     "• r = w / h — співвідношення сторін\n"
                     "• u̇, v̇, ṡ — лінійні швидкості (похідні)\n"
                     "• ṙ — вважається постійним (ṙ = 0)",
                     size=13, fill="#f8f9fa", stroke="#7f8c8d")
    p.append(b_state)

    b_meas = fitbox(460, 220, 350, 140,
                    "Вектор вимірів детектора (4D):\n"
                    "z = [ u,  v,  s,  r ]ᵀ\n\n"
                    "Зворотне відновлення рамки:\n"
                    "w = √(s · r),    h = √(s / r)\n"
                    "x₁ = u − w/2,    y₁ = v − h/2\n"
                    "x₂ = u + w/2,    y₂ = v + h/2",
                    size=13, fill="#eafaf1", stroke=FIELD)
    p.append(b_meas)

    render(os.path.join(OUT, "fig2-kalman-state-box.svg"), w, h, *p)


def fig3_iou_matching_matrix():
    """Принцип зіставлення детекцій і треків за метрикою IoU."""
    w, h = 860, 380
    p = []

    # Ліва панель: геометричне перекриття
    p.append(rect(30, 40, 360, 300, fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=6))
    p.append(text(210, 65, "Геометричне перекриття в кадрі", size=14, color=INK, bold=True, anchor="middle"))

    # Трек 1 (прогноз) і Детекція 1 (успішний збіг)
    p.append(dashed_rect(50, 95, 100, 110, fill="none", stroke="#2457d6", sw=1.5, dash="4,4"))
    p.append(text(55, 90, "Трек T₁ (прогноз)", size=11, color="#2457d6", anchor="start"))

    p.append(rect(75, 115, 95, 105, fill="none", stroke=FIELD, sw=2))
    p.append(text(125, 235, "Детекція D₁", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text(115, 155, "IoU = 0.72", size=12, color=FIELD, bold=True, anchor="middle"))

    # Трек 2 (прогноз) і Детекція 2 (часткове перекриття)
    p.append(dashed_rect(220, 95, 90, 100, fill="none", stroke="#2457d6", sw=1.5, dash="4,4"))
    p.append(text(220, 90, "Трек T₂", size=11, color="#2457d6", anchor="start"))

    p.append(rect(275, 125, 85, 95, fill="none", stroke="#d68910", sw=2))
    p.append(text(320, 235, "Детекція D₂", size=11, color="#d68910", bold=True, anchor="middle"))
    p.append(text(255, 150, "IoU 0.38", size=11, color="#d68910", bold=True, anchor="middle"))

    # Детекція 3 без треку (нова ціль)
    p.append(rect(50, 255, 75, 75, fill="#ebf5fb", stroke="#2980b9", sw=1.5))
    p.append(text(87, 290, "D₃ (Нова)", size=11, color="#2980b9", bold=True, anchor="middle"))
    p.append(text(87, 310, "IoU = 0.0", size=10, color="#2980b9", anchor="middle"))

    # Трек 3 без детекції (промах / оклюзія)
    p.append(dashed_rect(220, 255, 75, 75, fill="none", stroke=POS, sw=1.5, dash="4,4"))
    p.append(text(257, 290, "T₃ (Пропуск)", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(257, 310, "IoU = 0.0", size=10, color=POS, anchor="middle"))

    # Права панель: матриця витрат
    p.append(rect(420, 40, 410, 300, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=6))
    p.append(text(625, 65, "Матриця витрат C[i, j] = 1 − IoU(Tᵢ, Dⱼ)", size=13, color=INK, bold=True, anchor="middle"))

    # Таблиця
    # Заголовки стовпців (D1, D2, D3)
    p.append(text(540, 105, "D₁", size=13, color=FIELD, bold=True, anchor="middle"))
    p.append(text(630, 105, "D₂", size=13, color="#d68910", bold=True, anchor="middle"))
    p.append(text(720, 105, "D₃", size=13, color="#2980b9", bold=True, anchor="middle"))

    # Рядок T1
    p.append(text(460, 145, "T₁", size=13, color="#2457d6", bold=True, anchor="middle"))
    p.append(rect(505, 125, 70, 32, fill="#d5f5e3", stroke=FIELD, sw=1.5))
    p.append(text(540, 145, "0.28 ✓", size=12, color=FIELD, bold=True, anchor="middle"))
    p.append(rect(595, 125, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(630, 145, "1.00", size=12, color=MUTED, anchor="middle"))
    p.append(rect(685, 125, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(720, 145, "1.00", size=12, color=MUTED, anchor="middle"))

    # Рядок T2
    p.append(text(460, 195, "T₂", size=13, color="#2457d6", bold=True, anchor="middle"))
    p.append(rect(505, 175, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(540, 195, "1.00", size=12, color=MUTED, anchor="middle"))
    p.append(rect(595, 175, 70, 32, fill="#fdebd0", stroke="#d68910", sw=1.5))
    p.append(text(630, 195, "0.62 ✓", size=12, color="#d68910", bold=True, anchor="middle"))
    p.append(rect(685, 175, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(720, 195, "1.00", size=12, color=MUTED, anchor="middle"))

    # Рядок T3
    p.append(text(460, 245, "T₃", size=13, color=POS, bold=True, anchor="middle"))
    p.append(rect(505, 225, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(540, 245, "1.00", size=12, color=MUTED, anchor="middle"))
    p.append(rect(595, 225, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(630, 245, "1.00", size=12, color=MUTED, anchor="middle"))
    p.append(rect(685, 225, 70, 32, fill="#ffffff", stroke="#d5dbdb", sw=1))
    p.append(text(720, 245, "1.00", size=12, color=MUTED, anchor="middle"))

    # Пояснення під таблицею
    p.append(text(625, 290, "Поріг відсікання: IoU < 0.3  ⇒  Cost > 0.7", size=12, color=LINE, bold=True, anchor="middle"))
    p.append(text(625, 315, "Пари (T₁, D₁) та (T₂, D₂) прийнято; T₃ — пропуск; D₃ — нова ціль", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig3-iou-matching-matrix.svg"), w, h, *p)


def fig4_sort_lifecycle_edgecases():
    """Життєвий цикл треку та вразливість до перекриттів (ID switch)."""
    w, h = 860, 400
    p = []

    # Діаграма станів треку
    b_new = fitbox(40, 60, 180, 70, "1. Створення (New)\nНезв'язана детекція\nhits = 1, age = 0", fill="#ebf5fb", stroke="#2457d6")
    b_conf = fitbox(320, 60, 200, 70, "2. Підтверджено (Active)\nhits ≥ min_hits (3)\nВидається назовні", fill="#eafaf1", stroke=FIELD)
    b_miss = fitbox(600, 60, 220, 70, "3. Пропуск (Coasting)\nНемає детекції кадру t\nage += 1 (Калман predict)", fill="#fef9e7", stroke="#d4ac0d")
    b_dead = fitbox(600, 200, 220, 60, "4. Знищено (Deleted)\nage > max_age (зазвичай 1)\nПам'ять звільняється", fill="#fdecea", stroke=POS)
    p.extend([b_new, b_conf, b_miss, b_dead])

    # Переходи станів
    p.append(arrow(220, 95, 320, 95, color=FIELD, sw=1.8))
    p.append(text(270, 85, "hits++", size=11, color=FIELD, anchor="middle"))

    p.append(arrow(520, 85, 600, 85, color="#d4ac0d", sw=1.8))
    p.append(text(560, 75, "пропуск", size=11, color="#d4ac0d", anchor="middle"))

    p.append(arrow(600, 110, 520, 110, color=FIELD, sw=1.8))
    p.append(text(560, 125, "детекція", size=11, color=FIELD, anchor="middle"))

    p.append(arrow(710, 130, 710, 200, color=POS, sw=1.8))
    p.append(text(720, 165, "age > 1", size=11, color=POS, anchor="start"))

    # Нижня частина: Проблема тривалої оклюзії та перемикання ID
    p.append(rect(40, 280, 780, 100, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    p.append(text(60, 305, "Вразливість SORT: Втрата ідентифікатора при оклюзії > max_age кадрів", size=13, color=POS, bold=True, anchor="start"))

    # Таймлайн оклюзії
    p.append(text(60, 335, "Кадр t (ID 1)", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(arrow(140, 332, 200, 332, color="#7f8c8d", sw=1.5))
    p.append(text(210, 335, "Кадри t+1, t+2 (Об'єкт сховався)", size=12, color="#d4ac0d", anchor="start"))
    p.append(arrow(430, 332, 490, 332, color="#7f8c8d", sw=1.5))
    p.append(text(500, 335, "Кадр t+3 (Об'єкт знову видно)", size=12, color=POS, bold=True, anchor="start"))

    p.append(text(60, 362, "Оскільки max_age = 1, трек ID 1 знищено на кадрі t+2. На кадрі t+3 створюється новий трек ID 2 (ID Switch)!",
                  size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig4-sort-lifecycle-edgecases.svg"), w, h, *p)


if __name__ == "__main__":
    fig1_sort_pipeline()
    fig2_kalman_state_box()
    fig3_iou_matching_matrix()
    fig4_sort_lifecycle_edgecases()
    print("Всі фігури згенеровано успішно.")
