# -*- coding: utf-8 -*-
"""Фігури до статті «Підрахунковий фільтр Блума».
Запуск із теки теми: python figs.py
Генерує SVG-файли у теці ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 46, 42
FILLED_1 = "#eaf0fd"
FILLED_2 = "#d5e4fd"
FILLED_SAT = "#fdecea"
EMPTY = BG

def counter_cell(x, y, val_str, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.6, tcolor=INK, tsize=14, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    if val_str != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, val_str, size=tsize, color=tcolor, bold=bold)
    return out

# ── Фігура 1: Архітектура та базові операції CBF ──────────────────────────────
def fig_cbf_operations():
    W, H = 920, 480
    parts = []

    parts.append(text(W / 2, 30, "Архітектура підрахункового фільтра Блума: вставка та видалення зі спільними комірками", size=16, bold=True))

    # Ключ X (вставка)
    parts.append(rect(60, 65, 180, 44, fill="#eaf0fd", stroke=POS, sw=1.8, rx=6))
    parts.append(text(150, 92, "Ключ X (вставка)", size=13, bold=True, color=POS))

    # Ключ Y (вставка)
    parts.append(rect(370, 65, 180, 44, fill="#eaf0fd", stroke=POS, sw=1.8, rx=6))
    parts.append(text(460, 92, "Ключ Y (вставка)", size=13, bold=True, color=POS))

    # Ключ X (видалення)
    parts.append(rect(680, 65, 180, 44, fill="#fdecea", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(770, 92, "Ключ X (видалення)", size=13, bold=True, color=NEG))

    # Масив 4-бітних лічильників (14 комірок)
    ax, ay = 80, 220
    # Стан: X дав комірки 1, 4, 8 (+1); Y дав 4, 9, 12 (+1).
    # Комірка 4 має колізію -> значення 2.
    c_values = [0, 1, 0, 0, 2, 0, 0, 0, 1, 1, 0, 0, 1, 0]

    for i in range(14):
        x = ax + i * (CW + 10)
        val = c_values[i]
        val_str = str(val)
        if val == 0:
            fill_col = EMPTY
            txt_col = MUTED
            bld = False
        elif val == 1:
            fill_col = FILLED_1
            txt_col = POS
            bld = True
        else:
            fill_col = FILLED_2
            txt_col = "#1b3c99"
            bld = True

        parts.append(text(x + CW / 2, ay - 14, str(i), size=12, color=MUTED))
        parts.append(counter_cell(x, ay, val_str, w=CW, h=CH, fill=fill_col, tcolor=txt_col, bold=bld))

    parts.append(text(ax - 20, ay + CH / 2 + 5, "Лічильники:", size=13, color=INK, anchor="end", bold=True))

    # Стрілки від ключа X (вставка) -> 1, 4, 8
    x_indices = [1, 4, 8]
    for idx in x_indices:
        target_x = ax + idx * (CW + 10) + CW / 2
        parts.append(arrow(150, 109, target_x, ay - 6, color=POS, sw=1.5))
    parts.append(text(120, 155, "+1", size=13, color=POS, bold=True))

    # Стрілки від ключа Y (вставка) -> 4, 9, 12
    y_indices = [4, 9, 12]
    for idx in y_indices:
        target_x = ax + idx * (CW + 10) + CW / 2
        parts.append(arrow(460, 109, target_x, ay - 6, color=POS, sw=1.5))
    parts.append(text(495, 155, "+1", size=13, color=POS, bold=True))

    # Стрілки від ключа X (видалення) -> декремент 1, 4, 8
    for idx in x_indices:
        target_x = ax + idx * (CW + 10) + CW / 2
        parts.append(arrow(770, 109, target_x, ay - 6, color=NEG, sw=1.5))
    parts.append(text(795, 155, "−1", size=13, color=NEG, bold=True))

    # Пояснення внизу
    parts.append(rect(60, 310, 800, 130, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    parts.append(text(80, 335, "1. Вставка X: лічильники C[1], C[4], C[8] інкрементуються (стають 1).", size=12.5, anchor="start", color=INK))
    parts.append(text(80, 360, "2. Вставка Y: лічильники C[4], C[9], C[12] інкрементуються. Комірка C[4] отримує колізію і стає 2.", size=12.5, anchor="start", color=INK))
    parts.append(text(80, 385, "3. Видалення X: лічильники C[1] і C[8] повертаються до 0, а спільний лічильник C[4] зменшується до 1.", size=12.5, anchor="start", color=INK))
    parts.append(text(80, 410, "Результат: ключ X повністю видалено, а ключ Y залишається неушкодженим (усі його лічильники C[4], C[9], C[12] > 0).", size=12.5, anchor="start", color=FIELD, bold=True))

    render(os.path.join(IMG, "cbf-operations.svg"), W, H, *parts)


# ── Фігура 2: Насичення та блокування переповнення (Saturating Counter) ───────
def fig_cbf_counter_saturation():
    W, H = 880, 460
    parts = []

    parts.append(text(W / 2, 30, "Механізм насичення 4-бітного лічильника: запобігання хибнонегативним помилкам", size=16, bold=True))

    # Секція звичайного переповнення (небезпечно)
    parts.append(rect(50, 65, 370, 360, fill="#fdf4f4", stroke=POS, sw=1.5, rx=8))
    parts.append(text(235, 95, "Звичайна арифметика за модулем 16 (Помилка)", size=13.5, bold=True, color=POS))

    parts.append(rect(90, 125, 290, 40, fill=BG, stroke=LINE, sw=1.2, rx=4))
    parts.append(text(235, 150, "Поточний стан: C[i] = 15 (1111₂)", size=13, color=INK))

    parts.append(arrow(235, 165, 235, 205, color=POS, sw=1.8))
    parts.append(text(285, 188, "+1 вставка", size=12, color=POS, bold=True))

    parts.append(rect(90, 205, 290, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    parts.append(text(235, 230, "Переповнення: C[i] = 0 (0000₂)", size=13, bold=True, color=POS))

    parts.append(arrow(235, 245, 235, 285, color=POS, sw=1.8))
    parts.append(text(295, 268, "Запит наявності", size=12, color=MUTED))

    parts.append(rect(75, 285, 320, 115, fill=BG, stroke=POS, sw=1.5, rx=6))
    parts.append(text(235, 310, "КАТАСТРОФІЧНИЙ НАСЛІДОК:", size=12, bold=True, color=POS))
    parts.append(text(235, 335, "Комірка обнулилася → фільтр повертає false", size=12, color=INK))
    parts.append(text(235, 355, "для всіх 16 елементів, що туди хешувалися!", size=12, color=INK))
    parts.append(text(235, 380, "Порушено інваріант: False Negative!", size=12, bold=True, color=POS))

    # Секція насичуваної арифметики (Saturating Counters)
    parts.append(rect(460, 65, 370, 360, fill="#f2f8f4", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(645, 95, "Насичувана арифметика (Saturating Counter)", size=13.5, bold=True, color=FIELD))

    parts.append(rect(500, 125, 290, 40, fill=BG, stroke=LINE, sw=1.2, rx=4))
    parts.append(text(645, 150, "Поточний стан: C[i] = 15 (1111₂)", size=13, color=INK))

    parts.append(arrow(645, 165, 645, 205, color=FIELD, sw=1.8))
    parts.append(text(695, 188, "+1 вставка", size=12, color=FIELD, bold=True))

    parts.append(rect(500, 205, 290, 40, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(645, 230, "Насичення: C[i] = 15 (Заморожено)", size=13, bold=True, color=FIELD))

    parts.append(arrow(645, 245, 645, 285, color=FIELD, sw=1.8))
    parts.append(text(715, 268, "Видалення елемента", size=12, color=MUTED))

    parts.append(rect(485, 285, 320, 115, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(645, 310, "БЕЗПЕЧНИЙ КОМПРОМІС:", size=12, bold=True, color=FIELD))
    parts.append(text(645, 335, "Лічильник C[i] = 15 НЕ зменшується.", size=12, color=INK))
    parts.append(text(645, 355, "Комірка назавжди лишається активною (> 0).", size=12, color=INK))
    parts.append(text(645, 380, "Жодного False Negative: гарантія точності!", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "cbf-counter-saturation.svg"), W, H, *parts)


# ── Фігура 3: Розподіл навантаження на лічильники (Poisson Distribution) ───────
def fig_cbf_load_distribution():
    W, H = 840, 440
    parts = []

    parts.append(text(W / 2, 30, "Ймовірнісний розподіл навантаження на комірку CBF (Пуассон, λ = ln 2 ≈ 0.693)", size=15, bold=True))

    # Осі
    ox, oy = 80, 360
    gw, gh = 700, 280

    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    parts.append(text(ox + gw / 2, oy + 45, "Значення лічильника (кількість колізій у комірці)", size=13, bold=True))
    parts.append(text(ox - 50, oy - gh / 2, "Ймовірність P(C = c)", size=13, bold=True, anchor="middle"))

    # Значення ймовірностей Пуассона для lambda = ln(2) = 0.693147
    probs = [0.5000, 0.3466, 0.1201, 0.0278, 0.0048, 0.00067, 0.000077]
    bar_w = 42
    bar_spacing = 58
    scale_y = 500  # 0.5 * 500 = 250 px

    # Горизонтальні сітки
    for p_tick, p_lbl in [(0.1, "0.1"), (0.2, "0.2"), (0.3, "0.3"), (0.4, "0.4"), (0.5, "0.5")]:
        y_tick = oy - p_tick * scale_y
        parts.append(line(ox - 5, y_tick, ox + gw, y_tick, color="#e5e7eb", sw=1, dash="4,4"))
        parts.append(text(ox - 10, y_tick + 4, p_lbl, size=11, color=MUTED, anchor="end"))

    for c in range(len(probs)):
        p = probs[c]
        bx = ox + 35 + c * bar_spacing
        bh = p * scale_y
        by = oy - bh

        # Колір стовпчика
        b_fill = "#d5e4fd" if c <= 2 else "#fdecea"
        b_stroke = "#2457d6" if c <= 2 else POS

        parts.append(rect(bx, by, bar_w, bh, fill=b_fill, stroke=b_stroke, sw=1.5, rx=3))
        parts.append(text(bx + bar_w / 2, oy + 20, str(c), size=12, bold=True))

        # Підпис значення над стовпчиком
        if p >= 0.01:
            lbl = "%.1f%%" % (p * 100)
        elif p >= 0.001:
            lbl = "0.48%"
        else:
            lbl = "<0.1%"
        parts.append(text(bx + bar_w / 2, by - 8, lbl, size=11, color=b_stroke, bold=True))

    # Стовпчики для 7..15 показані як зона нульової ймовірності
    zone_x = ox + 35 + 7 * bar_spacing
    parts.append(rect(zone_x - 10, oy - 140, 240, 120, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(zone_x + 110, oy - 115, "Діапазон 7 ... 15:", size=12, bold=True, color=INK))
    parts.append(text(zone_x + 110, oy - 92, "P(C = 15) ≈ 1.97 × 10⁻¹⁴", size=11.5, color=MUTED))
    parts.append(text(zone_x + 110, oy - 69, "P(C ≥ 16) ≈ 1.37 × 10⁻¹⁵", size=11.5, color=POS, bold=True))
    parts.append(text(zone_x + 110, oy - 46, "4 біти (0..15) повністю достатні!", size=11.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "cbf-load-distribution.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_cbf_operations()
    fig_cbf_counter_saturation()
    fig_cbf_load_distribution()
    print("All figures generated successfully.")
