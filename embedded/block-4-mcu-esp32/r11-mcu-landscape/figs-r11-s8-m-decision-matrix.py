# -*- coding: utf-8 -*-
"""
figs-r11-s8-m-decision-matrix.py
Фігури до вставки 🧮 «Вибір МК ваговою матрицею» (r11-s8-m-decision-matrix.md)
Теми: §4.11.8m

fig-r11-s8m-1-decision-bars.svg  — горизонтальні stacked-смуги зважених сум S
                                     (переможець nRF-клас виділений; сегменти = критерії)
fig-r11-s8m-2-weight-sensitivity.svg — ОПЦІОНАЛЬНА: гойдалка чутливості S(nRF) vs S(ESP32)
                                        при зсуві ваги сон↔периферія ±0.10

Вивід → ./img/
Стиль (AUTHORING §9): svgkit — спільні примітиви; текст лише через textbox()/fitbox().
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Дані: бали та ваги (мусять збігатися з таблицею в .md)
# ─────────────────────────────────────────────────────────────────────────────
# Критерії і ваги
CRITERIA = ["Сон", "Радіо", "Периферія", "Екосистема", "Ціна"]
WEIGHTS  = [0.30,  0.25,   0.20,        0.15,          0.10]

# Кольори сегментів (5 критеріїв)
SEG_COLORS = ["#2980b9", "#27ae60", "#8e44ad", "#e67e22", "#c0392b"]

# Бали кожного кандидата (рядки = кандидати, стовпці = критерії)
CHIPS = [
    ("nRF-клас",    [5, 5, 4, 3, 3]),
    ("ESP32",       [3, 4, 5, 5, 4]),
    ("STM32-клас",  [4, 2, 4, 4, 3]),
    ("RP2040-клас", [2, 1, 4, 3, 4]),
    ("AVR-клас",    [3, 1, 3, 2, 5]),
]

def weighted_sum(scores):
    return sum(w * s for w, s in zip(WEIGHTS, scores))

# Розраховуємо S і сортуємо за спаданням
chips_with_s = [(name, scores, weighted_sum(scores)) for name, scores in CHIPS]
chips_sorted = sorted(chips_with_s, key=lambda x: x[2], reverse=True)

# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.8m.1 — горизонтальні stacked-смуги S
# ─────────────────────────────────────────────────────────────────────────────
def fig_decision_bars():
    W, H = 820, 420
    frags = []

    # Заголовок
    frags.append(text(W // 2, 32, "Зважені суми S п'яти кандидатів", size=17, bold=True))

    # Ліворуч — підписи; праворуч — смуги
    LABEL_W = 130    # ширина зони підписів
    BAR_X   = LABEL_W + 20    # початок смуг
    BAR_AREA= W - BAR_X - 40  # ширина зони смуг
    MAX_S   = 5.0              # максимально можлива S (всі бали = 5)
    SCALE   = BAR_AREA / MAX_S

    ROW_H   = 52
    ROW_Y0  = 70   # y верхньої смуги (центр)

    for i, (name, scores, s_val) in enumerate(chips_sorted):
        cy = ROW_Y0 + i * ROW_H
        is_winner = (i == 0)

        # Підпис кандидата
        lbl_size = 14 if not is_winner else 15
        lbl_color = "#1a1a1a" if not is_winner else "#1a6b3a"
        lbl_bold = is_winner
        frags.append(text(LABEL_W - 4, cy + 5, name, size=lbl_size,
                          color=lbl_color, anchor="end", bold=lbl_bold))

        # Stacked segments
        bar_h = 26 if not is_winner else 32
        bar_y = cy - bar_h // 2
        x_cur = BAR_X
        for j, (score, w) in enumerate(zip(scores, WEIGHTS)):
            seg_w = w * score * SCALE
            stroke_color = "#ffffff"
            frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'fill="%s" stroke="%s" stroke-width="1"/>'
                         % (x_cur, bar_y, max(seg_w, 0.5), bar_h,
                            SEG_COLORS[j], stroke_color))
            x_cur += seg_w

        # Обводка переможця
        if is_winner:
            total_w = s_val * SCALE
            frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="3" fill="none" stroke="#1a6b3a" stroke-width="2"/>'
                         % (BAR_X, bar_y, total_w, bar_h))

        # Числовий підпис S
        s_x = BAR_X + s_val * SCALE + 6
        frags.append(text(s_x, cy + 5, "%.2f" % s_val, size=13,
                          color=INK, anchor="start", bold=is_winner))

    # Легенда критеріїв
    leg_x0 = LABEL_W + 20
    leg_y  = ROW_Y0 + len(chips_sorted) * ROW_H + 10
    for j, (crit, col) in enumerate(zip(CRITERIA, SEG_COLORS)):
        lx = leg_x0 + j * 126
        frags.append('<rect x="%.0f" y="%.0f" width="16" height="14" '
                     'fill="%s" rx="3"/>' % (lx, leg_y, col))
        frags.append(text(lx + 20, leg_y + 11, crit, size=12,
                          color=INK, anchor="start"))

    # Вісь x (0 .. 5)
    ax_y = ROW_Y0 - ROW_H // 2 - 10
    frags.append(line(BAR_X, ax_y, BAR_X + 5 * SCALE, ax_y, color=MUTED, sw=1))
    for tick in [0, 1, 2, 3, 4, 5]:
        tx = BAR_X + tick * SCALE
        frags.append(line(tx, ax_y, tx, ax_y + 5, color=MUTED, sw=1))
        frags.append(text(tx, ax_y - 4, str(tick), size=11, color=MUTED))

    frags.append(text(BAR_X + 2.5 * SCALE, ax_y - 18,
                      "← зважена сума S (max = 5.00) →", size=11, color=MUTED))

    path = os.path.join(IMG, "fig-r11-s8m-1-decision-bars.svg")
    render(path, W, H, *frags)
    print("OK:", path)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.8m.2 — гойдалка чутливості (ОПЦІОНАЛЬНА)
# Показує, як S(nRF) і S(ESP32) змінюються при зсуві ваги w_сон ↔ w_периферія
# Base: w_сон=0.30, w_периферія=0.20. Зсув delta ∈ [-0.10, +0.10]
# При delta>0: w_сон += delta, w_периферія -= delta (і навпаки)
# ─────────────────────────────────────────────────────────────────────────────
def fig_weight_sensitivity():
    W, H = 740, 400

    import math

    frags = []
    frags.append(text(W // 2, 30, "Чутливість результату до зсуву ваги «сон ↔ периферія»",
                      size=16, bold=True))

    # Базові ваги та бали
    # WEIGHTS = [сон=0.30, радіо=0.25, периферія=0.20, екосистема=0.15, ціна=0.10]
    nrf_scores  = [5, 5, 4, 3, 3]
    esp_scores  = [3, 4, 5, 5, 4]

    def s_for_delta(scores, delta):
        # w_сон = 0.30 + delta, w_периферія = 0.20 - delta (решта незмінні)
        w = [0.30 + delta, 0.25, 0.20 - delta, 0.15, 0.10]
        return sum(ww * sc for ww, sc in zip(w, scores))

    DELTAS = [d / 100 for d in range(-10, 11)]  # -0.10 .. +0.10

    # Область графіка
    GX0, GY0 = 90, 60
    GX1, GY1 = W - 60, H - 80
    GW = GX1 - GX0
    GH = GY1 - GY0

    S_MIN, S_MAX = 3.0, 5.0
    D_MIN, D_MAX = -0.10, 0.10

    def px(delta):
        return GX0 + (delta - D_MIN) / (D_MAX - D_MIN) * GW

    def py(s):
        return GY1 - (s - S_MIN) / (S_MAX - S_MIN) * GH

    # Тло графіка
    frags.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" '
                 'fill="#f8fafc" stroke="#cccccc" stroke-width="1" rx="4"/>'
                 % (GX0, GY0, GW, GH))

    # Горизонтальні сітки
    for sv in [3.0, 3.5, 4.0, 4.5, 5.0]:
        gy = py(sv)
        frags.append(line(GX0, gy, GX1, gy, color="#e0e0e0", sw=1))
        frags.append(text(GX0 - 6, gy + 4, "%.1f" % sv, size=11, color=MUTED, anchor="end"))

    # Вертикальна сітка і підписи delta
    for dv in [-0.10, -0.05, 0, 0.05, 0.10]:
        gx = px(dv)
        frags.append(line(gx, GY0, gx, GY1, color="#e0e0e0", sw=1))
        frags.append(text(gx, GY1 + 16, ("%+.2f" % dv) if dv != 0 else "0",
                          size=11, color=MUTED))

    # Лінія delta=0 (базова)
    gx0_base = px(0)
    frags.append(line(gx0_base, GY0, gx0_base, GY1, color="#aaaaaa", sw=1.5, dash="4 3"))

    # Polylines для nRF і ESP32
    def polyline(scores, color, label, y_label_offset):
        points = []
        for d in DELTAS:
            sv = s_for_delta(scores, d)
            points.append("%.1f,%.1f" % (px(d), py(sv)))
        pts_str = " ".join(points)
        frags.append('<polyline points="%s" fill="none" stroke="%s" '
                     'stroke-width="2.5" stroke-linejoin="round"/>' % (pts_str, color))
        # Підпис у правому кінці
        last_d = DELTAS[-1]
        last_s = s_for_delta(scores, last_d)
        lx = px(last_d) + 6
        ly = py(last_s) + y_label_offset
        frags.append(text(lx, ly, label, size=13, color=color, anchor="start", bold=True))

    polyline(nrf_scores, "#27ae60", "nRF-клас", 4)
    polyline(esp_scores, "#e67e22", "ESP32", 4)

    # Знайти точку перетину (де S(nRF) ≈ S(ESP32))
    cross_d = None
    for i in range(len(DELTAS) - 1):
        s_nrf_a = s_for_delta(nrf_scores, DELTAS[i])
        s_esp_a = s_for_delta(esp_scores, DELTAS[i])
        s_nrf_b = s_for_delta(nrf_scores, DELTAS[i+1])
        s_esp_b = s_for_delta(esp_scores, DELTAS[i+1])
        # Перетин: знак різниці змінюється
        diff_a = s_nrf_a - s_esp_a
        diff_b = s_nrf_b - s_esp_b
        if diff_a * diff_b <= 0:
            # Лінійна інтерполяція
            t = diff_a / (diff_a - diff_b) if (diff_a - diff_b) != 0 else 0
            cross_d = DELTAS[i] + t * (DELTAS[i+1] - DELTAS[i])
            break

    if cross_d is not None:
        s_cross = s_for_delta(nrf_scores, cross_d)
        cx_px = px(cross_d)
        cy_px = py(s_cross)
        frags.append(circle(cx_px, cy_px, 6, fill="#ff6b6b", stroke="#c0392b", sw=2))
        label_cross = "Δ≈%+.2f\n(лідер змінюється)" % cross_d
        box_frag, bw, bh = textbox(cx_px + 70, cy_px - 20, label_cross,
                                   size=11, fill="#fff3f3", stroke="#c0392b")
        frags.append(box_frag)
        frags.append(line(cx_px + 6, cy_px - 8, cx_px + 70 - bw // 2, cy_px - 20,
                          color="#c0392b", sw=1, dash="3 2"))

    # Осьові підписи
    frags.append(text(GX0 + GW // 2, GY1 + 36,
                      "Зсув ваги Δ (w_сон = 0.30 + Δ,  w_периферія = 0.20 − Δ)",
                      size=12, color=INK))
    frags.append(text(GX0 - 50, GY0 + GH // 2, "S",
                      size=14, color=INK, bold=True))

    # Аннотація: ліва зона / права зона
    frags.append(text(GX0 + GW * 0.22, GY0 + 20, "nRF-клас лідирує",
                      size=11, color="#27ae60", italic=True))
    if cross_d is not None and cross_d < D_MAX:
        frags.append(text(GX0 + GW * 0.78, GY0 + 20, "ESP32 лідирує",
                          size=11, color="#e67e22", italic=True))

    path = os.path.join(IMG, "fig-r11-s8m-2-weight-sensitivity.svg")
    render(path, W, H, *frags)
    print("OK:", path)


if __name__ == "__main__":
    fig_decision_bars()
    fig_weight_sensitivity()
    print("Всі фігури згенеровано.")
