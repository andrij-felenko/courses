# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зближення ентропійних кривих при T -> 0 K (Теорема Нернста)
# ════════════════════════════════════════════════════════════════════════════
def fig_nernst_entropy_curves():
    W, H = 780, 480
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 28, "Поведінка ентропії при наближенні до абсолютного нуля T -> 0 K", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 410
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Температура T (К)", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 15, 52, "Ентропія S", size=12.5, bold=True, color=DARK, anchor="end"))

    # Крива 1 (стан X1, наприклад B=0 або p1)
    path_s1 = "M %d %d C 250 %d 450 200 680 110" % (ox, oy, oy)
    # Крива 2 (стан X2, наприклад B>0 або p2)
    path_s2 = "M %d %d C 250 %d 450 290 680 230" % (ox, oy, oy)

    # Заповнення області між кривими
    path_fill = "M %d %d C 250 %d 450 200 680 110 L 680 230 C 450 290 250 %d %d %d Z" % (ox, oy, oy, oy, ox, oy)
    f.append(svg_path(path_fill, stroke="none", sw=0, fill="#ebf5fb"))

    # Малювання кривих
    f.append(svg_path(path_s1, stroke="#c0392b", sw=3.0))
    f.append(svg_path(path_s2, stroke="#2457d6", sw=3.0))

    # Класичне екстраполювання (пунктир від 220,375 до 90,300, відведено від основного тексту)
    f.append(svg_path("M 220 375 C 160 350 120 320 90 300", stroke="#8e44ad", sw=2.0, dash="4 4"))
    f.append(circle(90, 300, 4, fill="#8e44ad", stroke="#ffffff", sw=1.5))
    f.append(text(82, 290, "S_0' (класика)", size=11, color="#8e44ad", anchor="end"))

    # Позначки точок та підписи кривих
    f.append(text(690, 105, "S(T, X_1) [напр. B=0]", size=12, bold=True, color="#c0392b", anchor="start"))
    f.append(text(690, 225, "S(T, X_2) [напр. B > 0]", size=12, bold=True, color="#2457d6", anchor="start"))

    # Дотичний акцент у T = 0 у рамці textbox чи над кривими
    f.append(circle(ox, oy, 6, fill="#27ae60", stroke="#ffffff", sw=2.0))
    box_s0, _, _ = textbox(210, 130, "S(0) = 0 (теорема Нернста)\nlim ΔS = 0 при T -> 0 K", size=11, pad=8, fill="#e8f8f5", stroke="#27ae60", sw=1.5, color="#145a32", bold=True)
    f.append(box_s0)
    f.append(line(210, 160, ox + 10, oy - 10, color="#27ae60", sw=1.5, dash="2 2"))

    # Подвійна стрілка ΔS при вищій температурі
    x_ds = 470
    y1_ds, y2_ds = 185, 280
    f.append(line(x_ds, y1_ds, x_ds, y2_ds, color=DARK, sw=1.5))
    f.append(line(x_ds - 5, y1_ds, x_ds + 5, y1_ds, color=DARK, sw=1.5))
    f.append(line(x_ds - 5, y2_ds, x_ds + 5, y2_ds, color=DARK, sw=1.5))
    f.append(text(x_ds + 10, (y1_ds + y2_ds) // 2 + 4, "ΔS(T) > 0", size=11.5, bold=True, color=DARK, anchor="start"))

    # Пояснювальна рамка
    box_info, _, _ = textbox(590, 360, "• Класична фізика: ΔS(0) ≠ 0 (невизначеність)\n• Квантова фізика: Ω_0 = 1 => S(0) = k_B ln 1 = 0\n• Обов'язкова умова: C_p, C_v -> 0 при T -> 0 K", size=10.5, pad=10, fill="#f8f9f9", stroke=MUTED, sw=1.0, color=INK)
    f.append(box_info)

    render(os.path.join(OUT, "nernst-entropy-curves.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Принцип недосяжності абсолютного нуля (кроки охолодження)
# ════════════════════════════════════════════════════════════════════════════
def fig_cooling_unattainability_steps():
    W, H = 780, 500
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 28, "Принцип недосяжності 0 K: послідовність кріогенних циклів", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 420
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Температура T", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 15, 52, "Ентропія S", size=12.5, bold=True, color=DARK, anchor="end"))

    # Дві криві ентропії, що змикаються в (ox, oy)
    path_b1 = "M %d %d C 250 %d 480 180 680 100" % (ox, oy, oy)
    path_b2 = "M %d %d C 250 %d 480 300 680 240" % (ox, oy, oy)

    f.append(svg_path(path_b1, stroke="#c0392b", sw=2.5))
    f.append(svg_path(path_b2, stroke="#2457d6", sw=2.5))

    f.append(text(690, 95, "S(T, B=0)", size=12, bold=True, color="#c0392b", anchor="start"))
    f.append(text(690, 235, "S(T, B > 0)", size=12, bold=True, color="#2457d6", anchor="start"))

    # Кроки адіабатичного розмагнічування
    # Крок 1: Isothermal magnetization at T1 (600px): from curve B1 (130px) to B2 (260px)
    t1_x = 600
    s_b1_t1, s_b2_t1 = 130, 260
    f.append(line(t1_x, s_b1_t1, t1_x, s_b2_t1, color="#27ae60", sw=2.5))
    f.append(polygon([(t1_x - 5, s_b2_t1 - 10), (t1_x, s_b2_t1), (t1_x + 5, s_b2_t1 - 10)], fill="#27ae60"))
    f.append(text(t1_x + 10, (s_b1_t1 + s_b2_t1) // 2, "Ізотерма (T_1)", size=10.5, color="#27ae60"))

    # Adiabatic demagnetization S=const: from T1 (600px) to T2 (380px) at S=260px
    t2_x = 380
    f.append(line(t1_x, s_b2_t1, t2_x, s_b2_t1, color="#8e44ad", sw=2.5))
    f.append(polygon([(t2_x + 10, s_b2_t1 - 5), (t2_x, s_b2_t1), (t2_x + 10, s_b2_t1 + 5)], fill="#8e44ad"))
    f.append(text((t1_x + t2_x) // 2, s_b2_t1 - 14, "Адіабата (S=const)", size=10.5, color="#8e44ad", anchor="middle"))

    # Крок 2: Isothermal magnetization at T2 (380px): from curve B1 (230px) to B2 (330px)
    s_b1_t2, s_b2_t2 = 230, 330
    f.append(line(t2_x, s_b1_t2, t2_x, s_b2_t2, color="#27ae60", sw=2.0))
    f.append(polygon([(t2_x - 4, s_b2_t2 - 8), (t2_x, s_b2_t2), (t2_x + 4, s_b2_t2 - 8)], fill="#27ae60"))

    # Adiabatic demagnetization from T2 (380px) to T3 (220px) at S=330px
    t3_x = 220
    f.append(line(t2_x, s_b2_t2, t3_x, s_b2_t2, color="#8e44ad", sw=2.0))
    f.append(polygon([(t3_x + 8, s_b2_t2 - 4), (t3_x, s_b2_t2), (t3_x + 8, s_b2_t2 + 4)], fill="#8e44ad"))

    # Крок 3: дрібніший крок до T4 (150px)
    s_b2_t3 = 360
    t4_x = 150
    f.append(line(t3_x, 310, t3_x, s_b2_t3, color="#27ae60", sw=1.5))
    f.append(line(t3_x, s_b2_t3, t4_x, s_b2_t3, color="#8e44ad", sw=1.5))

    # Пунктири температур до осі T
    f.append(line(t1_x, s_b2_t1, t1_x, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(t2_x, s_b2_t2, t2_x, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(t3_x, s_b2_t3, t3_x, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(t4_x, s_b2_t3, t4_x, oy, color=MUTED, sw=1.0, dash="3 3"))

    f.append(text(t1_x, oy + 16, "T_1", size=11, bold=True, color=DARK, anchor="middle"))
    f.append(text(t2_x, oy + 16, "T_2", size=11, bold=True, color=DARK, anchor="middle"))
    f.append(text(t3_x, oy + 16, "T_3", size=11, bold=True, color=DARK, anchor="middle"))
    f.append(text(t4_x, oy + 16, "T_4", size=11, bold=True, color=DARK, anchor="middle"))
    f.append(text(ox, oy + 16, "T=0 K", size=11, bold=True, color="#c0392b", anchor="middle"))

    # Пояснювальний текстовий напис через textbox
    box_unattain, _, _ = textbox(570, 390, "• Оскільки ΔS -> 0 при T -> 0 K, кроки ΔT зменшуються\n• Кількість циклів N -> ∞ для досягнення T = 0 K\n• Абсолютний нуль термодинамічно недосяжний за N < ∞", size=10.0, pad=10, fill="#f4ecf7", stroke="#8e44ad", sw=1.0, color=INK)
    f.append(box_unattain)

    render(os.path.join(OUT, "cooling-unattainability-steps.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Залишкова ентропія кристалічного льоду (Модель Полінга)
# ════════════════════════════════════════════════════════════════════════════
def fig_pauling_ice_microstates():
    W, H = 760, 460
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 28, "Мікроскопічний вигляд залишкової ентропії льоду (Правила Бернала-Фаулера)", size=14, bold=True, color=INK, anchor="middle"))

    # Схема тетраедричного вузла Оксигену з 4 водневими зв'язками
    cx, cy = 240, 240
    r_o = 24

    # Зв'язки до 4 сусідів
    neighbors = [
        (cx - 120, cy - 100, "O_1"),
        (cx + 120, cy - 100, "O_2"),
        (cx - 120, cy + 100, "O_3"),
        (cx + 120, cy + 100, "O_4")
    ]

    # Малювання зв'язків та протонів (H)
    h_positions = [
        (cx - 45, cy - 38, True),   # Близький H (ковалентний)
        (cx + 45, cy - 38, True),   # Близький H (ковалентний)
        (cx - 85, cy + 70, False),  # Далекий H (водневий зв'язок)
        (cx + 85, cy + 70, False)   # Далекий H (водневий зв'язок)
    ]

    for (nx, ny, nlabel), (hx, hy, is_near) in zip(neighbors, h_positions):
        # Лінія зв'язку
        f.append(line(cx, cy, nx, ny, color=MUTED, sw=2.0, dash="4 4"))

        # Протон H
        f.append(circle(hx, hy, 10, fill="#c0392b" if is_near else "#2457d6", stroke=DARK, sw=1.5))
        f.append(text(hx, hy + 3.5, "H", size=10, bold=True, color="#ffffff", anchor="middle"))

        # Сусідній оксиген
        f.append(circle(nx, ny, 18, fill="#e8f8f5", stroke="#27ae60", sw=1.8))
        f.append(text(nx, ny + 4, nlabel, size=11, bold=True, color="#145a32", anchor="middle"))

    # Центральний оксиген
    f.append(circle(cx, cy, r_o, fill="#ebf5fb", stroke="#2980b9", sw=2.5))
    f.append(text(cx, cy + 5, "O", size=14, bold=True, color="#1b4f72", anchor="middle"))

    # Легенда та вивід Полінга праворуч через textbox
    box_p, _, _ = textbox(585, 240, "Комбінаторика Полінга\n───────────────────────\n1. Кожен O має 4 зв'язки\n2. Всього H-атомів: 2N на N молів O\n3. На кожному зв'язку — 2 позиції (2^2N)\n4. З 16 варіантів оточення O лише 6\n   задовольняють правилу H2O (6/16 = 3/8)\n───────────────────────\nКількість мікростанів:\nΩ = 2^(2N) · (3/8)^N = (3/2)^N\n───────────────────────\nЗалишкова ентропія при T = 0 K:\nS_0 = k_B ln Ω = N k_B ln(3/2)\nS_0 ≈ 0.85 R = 3.37 Дж/(моль·К)\n(Експеримент: 3.41 Дж/(моль·К))", size=11.0, pad=12, fill="#f8f9f9", stroke=MUTED, sw=1.2, color=INK)
    f.append(box_p)

    render(os.path.join(OUT, "pauling-ice-microstates.svg"), W, H, *f)


if __name__ == '__main__':
    fig_nernst_entropy_curves()
    fig_cooling_unattainability_steps()
    fig_pauling_ice_microstates()
    print("Figures generated successfully.")
