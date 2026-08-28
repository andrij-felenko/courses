# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_wind_triangle_geometry():
    """
    Векторний навігаційний трикутник швидкостей:
    V_g (Ground Speed) = V_a (True Airspeed) + W (Wind Velocity).
    Показує північний напрямок (North), курс орієнтації psi (Heading),
    шляховий кут chi (Course/Track), кут крабування alpha_c = chi - psi,
    напрямок вітру psi_w.
    """
    W_w, H_h = 820, 520
    frags = []

    # Фонова картка
    frags.append(rect(10, 10, W_w - 20, H_h - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    ox, oy = 180.0, 430.0  # Початок векторів

    psi_deg = 18.0
    chi_deg = 46.0
    psi_rad = math.radians(psi_deg)
    chi_rad = math.radians(chi_deg)

    len_va = 270.0  # Повітряна швидкість V_a
    va_x = len_va * math.sin(psi_rad)
    va_y = -len_va * math.cos(psi_rad)

    # Кінець вектора V_a
    p_va_x = ox + va_x
    p_va_y = oy + va_y

    len_vg = 370.0
    vg_x = len_vg * math.sin(chi_rad)
    vg_y = -len_vg * math.cos(chi_rad)

    # Кінець вектора V_g
    p_vg_x = ox + vg_x
    p_vg_y = oy + vg_y

    # 1. Північна вісь (North) з точки O
    n_len = 390.0
    frags.append(line(ox, oy, ox, oy - n_len, color="#94a3b8", sw=1.5, dash="6 4"))
    frags.append(arrow(ox, oy, ox, oy - n_len, color="#64748b", sw=1.8))
    frags.append(text(ox, oy - n_len - 14, "Північ (North / 0°)", size=13, color="#475569", bold=True))

    # Додаткова північна лінія у точці p_va для кута вітру
    frags.append(line(p_va_x, p_va_y, p_va_x, p_va_y - 100, color="#cbd5e1", sw=1.2, dash="4 4"))

    # 2. Дуги кутів
    # Дуга курсу psi (між Північчю та V_a)
    r_psi = 130.0
    arc_psi_p1_x = ox
    arc_psi_p1_y = oy - r_psi
    arc_psi_p2_x = ox + r_psi * math.sin(psi_rad)
    arc_psi_p2_y = oy - r_psi * math.cos(psi_rad)
    frags.append('<path d="M %.1f,%.1f A %.1f,%.1f 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (arc_psi_p1_x, arc_psi_p1_y, r_psi, r_psi, arc_psi_p2_x, arc_psi_p2_y, NEG))
    frags.append(text(ox + 32, oy - 145, "ψ (Heading)", size=12, color=NEG, bold=True))

    # Дуга шляхового кута chi (між Північчю та V_g)
    r_chi = 185.0
    arc_chi_p1_x = ox
    arc_chi_p1_y = oy - r_chi
    arc_chi_p2_x = ox + r_chi * math.sin(chi_rad)
    arc_chi_p2_y = oy - r_chi * math.cos(chi_rad)
    frags.append('<path d="M %.1f,%.1f A %.1f,%.1f 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (arc_chi_p1_x, arc_chi_p1_y, r_chi, r_chi, arc_chi_p2_x, arc_chi_p2_y, FIELD))
    frags.append(text(ox + 100, oy - 165, "χ (Track)", size=12, color=FIELD, bold=True))

    # Дуга кута крабування alpha_c = chi - psi (між V_a та V_g)
    r_alpha = 235.0
    arc_a1_x = ox + r_alpha * math.sin(psi_rad)
    arc_a1_y = oy - r_alpha * math.cos(psi_rad)
    arc_a2_x = ox + r_alpha * math.sin(chi_rad)
    arc_a2_y = oy - r_alpha * math.cos(chi_rad)
    frags.append('<path d="M %.1f,%.1f A %.1f,%.1f 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="3 3"/>' %
                 (arc_a1_x, arc_a1_y, r_alpha, r_alpha, arc_a2_x, arc_a2_y, POS))
    frags.append(text(ox + 130, oy - 230, "α_c = χ − ψ (Crab)", size=12, color=POS, bold=True))

    # 3. Вектор повітряної швидкості V_a (синій)
    frags.append(arrow(ox, oy, p_va_x, p_va_y, color=NEG, sw=3.0))
    mid_va_x = (ox + p_va_x) / 2
    mid_va_y = (oy + p_va_y) / 2
    frags.append(text(mid_va_x - 35, mid_va_y + 10, "V_a (Airspeed)", size=13, color=NEG, bold=True))

    # 4. Вектор вітру W (пурпурово-червоний)
    frags.append(arrow(p_va_x, p_va_y, p_vg_x, p_vg_y, color=POS, sw=3.0))
    mid_w_x = (p_va_x + p_vg_x) / 2
    mid_w_y = (p_va_y + p_vg_y) / 2
    frags.append(text(mid_w_x + 15, mid_w_y - 18, "W (Wind Vector)", size=13, color=POS, bold=True))

    # 5. Результуючий вектор шляхової швидкості V_g (зелений)
    frags.append(arrow(ox, oy, p_vg_x, p_vg_y, color=FIELD, sw=3.5))
    mid_vg_x = (ox + p_vg_x) / 2
    mid_vg_y = (oy + p_vg_y) / 2
    frags.append(text(mid_vg_x + 45, mid_vg_y + 25, "V_g = V_a + W (Ground Speed)", size=13, color=FIELD, bold=True))

    # Точки O, A, B
    frags.append(circle(ox, oy, 5, fill=INK, stroke="#ffffff", sw=1.5))
    frags.append(text(ox - 16, oy + 12, "O (Старт)", size=12, color=INK, bold=True))

    frags.append(circle(p_va_x, p_va_y, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(circle(p_vg_x, p_vg_y, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    frags.append(text(p_vg_x + 15, p_vg_y + 6, "Фактичний рух", size=12, color=FIELD, bold=True, anchor="start"))

    # Інформаційний блок праворуч
    info_x, info_y = 570.0, 110.0
    tb, _, _ = textbox(
        info_x, info_y,
        "Векторне рівняння:\n"
        "V_g = V_a + W\n\n"
        "Кути орієнтації:\n"
        "• ψ (Heading) — кут осі носа\n"
        "• χ (Track) — напрямок руху по землі\n"
        "• α_c = χ − ψ — кут крабування\n"
        "• W — швидкість і напрямок вітру",
        size=12, pad=12, fill="#f8fafc", stroke="#94a3b8", sw=1.2, min_w=220
    )
    frags.append(tb)

    render(os.path.join(OUT, "wind-triangle-geometry.svg"), W_w, H_h, *frags)


def fig_crab_vs_sideslip():
    """
    Порівняння двох стратегій утримання лінії шляху при боковому вітрі:
    1) Крабування (Crabbing): beta = 0, симетричне обтікання, ніс довернуто назустріч вітру.
    2) Аеродинамічне ковзання (Sideslip): psi = chi, beta != 0, ніс дивиться вздовж шляху,
       вітер набігає під кутом на борт, політ із постійним креном і високим опором.
    """
    W_w, H_h = 860, 480
    frags = []

    frags.append(rect(10, 10, W_w - 20, H_h - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # Розділювач панелей
    mid_sep = W_w / 2
    frags.append(line(mid_sep, 30, mid_sep, H_h - 30, color="#cbd5e1", sw=1.5, dash="6 4"))

    # ── Ліва панель: Крабування (Crabbing) ──────────────────────────────────
    cx1 = 215.0
    frags.append(text(cx1, 45, "1. Крабування (Crabbing)", size=16, color=FIELD, bold=True))
    frags.append(text(cx1, 68, "Поворот усього фюзеляжу на кут α_c (β = 0)", size=12, color="#475569", italic=True))

    # Задана лінія шляху (вертикальна пряма вгору)
    line_x1 = cx1
    frags.append(line(line_x1, 95, line_x1, 315, color="#94a3b8", sw=2.0, dash="5 4"))
    frags.append(text(line_x1 + 8, 305, "Бажана лінія шляху (Track)", size=11, color="#64748b", anchor="start"))

    drone_y1 = 205.0
    crab_angle = -22.0  # градуси
    crab_rad = math.radians(crab_angle)

    body_len = 65.0
    dx_nose = -body_len * math.sin(crab_rad)
    dy_nose = -body_len * math.cos(crab_rad)

    # Вісь літака
    frags.append(line(line_x1 - dx_nose * 0.4, drone_y1 - dy_nose * 0.4,
                      line_x1 + dx_nose * 0.6, drone_y1 + dy_nose * 0.6, color=NEG, sw=3.5))

    # Крила літака
    wing_span = 75.0
    wx1 = line_x1 + wing_span * 0.5 * math.cos(crab_rad)
    wy1 = drone_y1 - wing_span * 0.5 * math.sin(crab_rad)
    wx2 = line_x1 - wing_span * 0.5 * math.cos(crab_rad)
    wy2 = drone_y1 + wing_span * 0.5 * math.sin(crab_rad)
    frags.append(line(wx1, wy1, wx2, wy2, color=NEG, sw=2.8))

    # Стрілка вектора повітряної швидкості V_a (вздовж осі носа)
    frags.append(arrow(line_x1, drone_y1, line_x1 + dx_nose * 0.9, drone_y1 + dy_nose * 0.9, color=NEG, sw=2.2))
    frags.append(text(line_x1 + dx_nose * 0.9 - 28, drone_y1 + dy_nose * 0.9 - 8, "V_a (Ніс)", size=11, color=NEG, bold=True))

    # Стрілка бокового вітру W (дме зліва направо)
    frags.append(arrow(line_x1 - 85, drone_y1, line_x1 - 15, drone_y1, color=POS, sw=2.2))
    frags.append(text(line_x1 - 60, drone_y1 - 10, "Вітер W", size=11, color=POS, bold=True))

    # Вектор шляхової швидкості V_g (строго вгору вздовж лінії шляху)
    frags.append(arrow(line_x1, drone_y1, line_x1, drone_y1 - 95, color=FIELD, sw=2.8))
    frags.append(text(line_x1 + 10, drone_y1 - 80, "V_g (Шлях)", size=11, color=FIELD, bold=True, anchor="start"))

    # Пояснювальний бокс унизу зліва
    frags.append(fitbox(
        35, 330, 360, 115,
        "• Обтікання симетричне: кут ковзання β = 0\n"
        "• Мінімальний аеродинамічний опір\n"
        "• Відсутні бокові сили на кіль і фюзеляж\n"
        "• Основний режим автопілота в круїзі",
        size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.2
    ))

    # ── Права панель: Аеродинамічне ковзання (Sideslip) ─────────────────────
    cx2 = 645.0
    frags.append(text(cx2, 45, "2. Бокове ковзання (Sideslip)", size=16, color=POS, bold=True))
    frags.append(text(cx2, 68, "Ніс уздовж лінії, компенсація креном (β ≠ 0)", size=12, color="#475569", italic=True))

    # Задана лінія шляху
    line_x2 = cx2
    frags.append(line(line_x2, 95, line_x2, 315, color="#94a3b8", sw=2.0, dash="5 4"))
    frags.append(text(line_x2 + 8, 305, "Бажана лінія шляху (Track)", size=11, color="#64748b", anchor="start"))

    drone_y2 = 205.0
    # Корпус строго вертикальний
    frags.append(line(line_x2, drone_y2 + 25, line_x2, drone_y2 - 40, color=NEG, sw=3.5))
    # Крила горизонтальні
    frags.append(line(line_x2 - 38, drone_y2, line_x2 + 38, drone_y2, color=NEG, sw=2.8))

    # Стрілка вектора орієнтації носа V_a (строго вгору)
    frags.append(arrow(line_x2, drone_y2, line_x2, drone_y2 - 65, color=NEG, sw=2.2))
    frags.append(text(line_x2 + 10, drone_y2 - 50, "Ніс ψ = χ", size=11, color=NEG, bold=True, anchor="start"))

    # Стрілка бокового вітру W
    frags.append(arrow(line_x2 - 85, drone_y2, line_x2 - 15, drone_y2, color=POS, sw=2.2))
    frags.append(text(line_x2 - 60, drone_y2 - 10, "Вітер W", size=11, color=POS, bold=True))

    # Набігаючий потік (Relative Wind) під кутом beta
    frags.append(arrow(line_x2 - 55, drone_y2 + 55, line_x2 - 12, drone_y2 + 12, color="#ea580c", sw=2.0))
    frags.append(mtext(line_x2 - 75, drone_y2 + 42, ["Набігаючий потік", "(Ковзання β > 0)"], size=10, color="#ea580c", bold=True, anchor="end"))

    # Пояснювальний бокс унизу справа
    frags.append(fitbox(
        465, 330, 360, 115,
        "• Вітер обдуває літак збоку: β ≠ 0\n"
        "• Високий паразитна сила та перевитрата енергії\n"
        "• Потребує постійного крену та керма напрямку\n"
        "• Застосовується лише перед торканням ЗПС",
        size=12, pad=10, fill="#fef2f2", stroke=POS, sw=1.2
    ))

    render(os.path.join(OUT, "crab-vs-sideslip.svg"), W_w, H_h, *frags)


def fig_ekf_wind_fusion_flow():
    """
    Архітектура оцінювача вітру EKF та контуру компенсації зносу:
    Сенсори (GNSS, Pitot, IMU) -> Фільтр Калмана (EKF Wind State) ->
    Вектор вітру W -> Контур наведення (L1/Track Controller) -> Heading setpoint.
    """
    W_w, H_h = 860, 480
    frags = []

    frags.append(rect(10, 10, W_w - 20, H_h - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # Заголовок схеми
    frags.append(text(W_w / 2, 35, "Архітектура оцінки вітру (EKF) та формування кута крабування", size=15, bold=True))

    # 1. Колонка сенсорів зліва
    bx_s1 = fitbox(30, 65, 190, 65, "GNSS Приймач\n• Шляхова швидкість V_g\n• Координати (X, Y)", size=11, fill="#eff6ff", stroke=NEG)
    bx_s2 = fitbox(30, 145, 190, 65, "Трубка Піто (Airspeed)\n• Динамічний тиск q\n• Повітряна швидкість V_a", size=11, fill="#eff6ff", stroke=NEG)
    bx_s3 = fitbox(30, 225, 190, 65, "IMU / AHRS\n• Орієнтація (q_att / Euler)\n• Кутова швидкість ω", size=11, fill="#eff6ff", stroke=NEG)
    frags.extend([bx_s1, bx_s2, bx_s3])

    # 2. Центральний блок: EKF Wind & States Estimator
    ekf_x, ekf_y, ekf_w, ekf_h = 275, 75, 270, 225
    frags.append(rect(ekf_x, ekf_y, ekf_w, ekf_h, fill="#f8fafc", stroke="#334155", sw=2.0, rx=8))
    frags.append(text(ekf_x + ekf_w / 2, ekf_y + 24, "Бортовий фільтр EKF", size=13, bold=True))
    frags.append(line(ekf_x + 15, ekf_y + 34, ekf_x + ekf_w - 15, ekf_y + 34, color="#cbd5e1", sw=1.0))

    ekf_text = (
        "Вектор стану: x = [W_N, W_E, k_scale]^T\n\n"
        "Прогноз: Ẇ = 0 + w_wind\n"
        "Вимірювання:\n"
        "z = V_g − R_b^n · [k · V_a, 0, 0]^T\n"
        "Інновація: y = z − W"
    )
    frags.append(fitbox(ekf_x + 10, ekf_y + 45, ekf_w - 20, 165, ekf_text, size=11, fill="#ffffff", stroke="#94a3b8", sw=1.0))

    # Стрілки від сенсорів до EKF
    frags.append(arrow(220, 97, ekf_x, 120, color=NEG, sw=1.8))
    frags.append(arrow(220, 177, ekf_x, 177, color=NEG, sw=1.8))
    frags.append(arrow(220, 257, ekf_x, 235, color=NEG, sw=1.8))

    # 3. Блок розрахунку крабування та наведення
    ctrl_x, ctrl_y, ctrl_w, ctrl_h = 585, 75, 245, 225
    frags.append(rect(ctrl_x, ctrl_y, ctrl_w, ctrl_h, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=8))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 24, "Контур наведення (L1)", size=13, color=FIELD, bold=True))
    frags.append(line(ctrl_x + 15, ctrl_y + 34, ctrl_x + ctrl_w - 15, ctrl_y + 34, color="#bbf7d0", sw=1.0))

    ctrl_text = (
        "1. Бажаний шлях: χ_cmd\n"
        "2. Кут крабування:\n"
        "   α_c = arcsin( W_cross / V_a )\n"
        "3. Цільовий курс носа:\n"
        "   ψ_cmd = χ_cmd − α_c\n"
        "4. Команда крену / рискання"
    )
    frags.append(fitbox(ctrl_x + 10, ctrl_y + 45, ctrl_w - 20, 165, ctrl_text, size=11, fill="#ffffff", stroke="#86efac", sw=1.0))

    # Стрілка від EKF до Контуру наведення
    frags.append(arrow(ekf_x + ekf_w, 175, ctrl_x, 175, color=POS, sw=2.2))
    frags.append(text((ekf_x + ekf_w + ctrl_x) / 2, 162, "Вектор W", size=11, color=POS, bold=True))

    # 4. Фінальний вихід: до контуру керування кутами
    frags.append(arrow(ctrl_x + ctrl_w / 2, ctrl_y + ctrl_h, ctrl_x + ctrl_w / 2, 395, color=FIELD, sw=2.2))
    frags.append(fitbox(
        ctrl_x - 10, 395, ctrl_w + 20, 55,
        "Контур кутової стабілізації\n(Уставка курсу ψ_cmd → Елерони / Руль)",
        size=11, fill="#eff6ff", stroke="#2563eb", sw=1.5
    ))

    # Блок синтетичного вітру знизу
    frags.append(fitbox(
        30, 355, 510, 95,
        "Оцінка без трубки Піто (Synthetic Wind Observer):\n"
        "Під час віражів та маневрів модуль V_g модулюється за курсом ψ:\n"
        "V_g(t) = V_a + W_N·cos(ψ) + W_E·sin(ψ). Фільтр відновлює W та V_a без датчика тиску.",
        size=11, pad=10, fill="#fefce8", stroke="#ca8a04", sw=1.2
    ))

    render(os.path.join(OUT, "ekf-wind-fusion-flow.svg"), W_w, H_h, *frags)


if __name__ == "__main__":
    fig_wind_triangle_geometry()
    fig_crab_vs_sideslip()
    fig_ekf_wind_fusion_flow()
    print("Figures generated successfully.")
