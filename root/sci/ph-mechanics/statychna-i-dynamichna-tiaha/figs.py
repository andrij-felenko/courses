# -*- coding: utf-8 -*-
"""Фігури до теми «Статична й динамічна тяга».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

UP    = "#c0392b"   # тяга / C_T (червоний)
DOWN  = "#2457d6"   # швидкість / C_P (синій)
FIELD = "#27ae60"   # ККД / кути (зелений)


# ── Фігура 1: трикутник швидкостей для статики й польоту ────────────────────
def fig_dynamic_inflow_triangle():
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Трикутник швидкостей: статика проти поступального польоту", size=16, bold=True))

    col_w = W / 2
    cxs = [col_w * 0.5, col_w * 1.5]
    titles = ["Статичний режим (V₀ = 0)", "Поступальний рух (V₀ > 0)"]

    # Розділювач колонок
    f.append(line(col_w, 48, col_w, H - 20, color="#dfe4ea", sw=1.2, dash="4,6"))

    for i, cx in enumerate(cxs):
        f.append(text(cx, 56, titles[i], size=15, bold=True, color=UP if i == 0 else DOWN))

    # --- Ліва панель: Статика (V0 = 0) ---
    lx = 90
    ly = 240
    u_len = 220    # омега * r (вправо)
    vi_len = 65    # v_i0 (вгору по потоку відносно лопаті)

    # Вектор колової швидкості u = ω·r
    f.append(arrow(lx, ly, lx + u_len, ly, color=LINE, sw=2.2))
    f.append(text(lx + u_len / 2, ly + 20, "колова швидкість u = ω · r", size=12, color=INK))

    # Вектор осьової індукованої швидкості v_i0
    f.append(arrow(lx + u_len, ly, lx + u_len, ly - vi_len, color=DOWN, sw=2.2))
    f.append(text(lx + u_len + 12, ly - vi_len / 2 + 4, "v_i0 (індукована)", size=12, color=DOWN, anchor="start"))

    # Вектор результуючого потоку W_stat
    f.append(arrow(lx, ly, lx + u_len, ly - vi_len, color=POS, sw=2.5))
    f.append(text(lx + u_len * 0.42, ly - vi_len * 0.7 - 6, "потік W_stat", size=13, bold=True, color=POS))

    # Кут установки лопаті beta
    f.append(line(lx, ly, lx + 190, ly - 110, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(lx + 198, ly - 116, "хорда лопаті (кут β)", size=12, color=MUTED, anchor="start"))

    # Підписи кутів у статиці
    b_stat, _, _ = textbox(cxs[0], H - 56, "Мала осьова швидкість v_i0 → малий кут набігання φ\nЕфективний кут атаки α = β − φ великий → висока тяга T",
                           size=12, pad=8, fill="#fdf2f2", stroke=UP, sw=1.2)
    f.append(b_stat)

    # --- Права панель: Динаміка (V0 > 0) ---
    rx = col_w + 70
    ry = 240
    vi_dyn = 135   # V0 + v_i (набагато довший вектор)

    # Вектор колової швидкості u = ω·r
    f.append(arrow(rx, ry, rx + u_len, ry, color=LINE, sw=2.2))
    f.append(text(rx + u_len / 2, ry + 20, "колова швидкість u = ω · r", size=12, color=INK))

    # Вектор сумарної осьової швидкості V0 + v_i
    f.append(arrow(rx + u_len, ry, rx + u_len, ry - vi_dyn, color=DOWN, sw=2.6))
    f.append(text(rx + u_len + 12, ry - vi_dyn / 2 + 4, "V₀ + v_i (осьова)", size=12, bold=True, color=DOWN, anchor="start"))

    # Вектор результуючого потоку W_dyn
    f.append(arrow(rx, ry, rx + u_len, ry - vi_dyn, color=POS, sw=2.5))
    f.append(text(rx + u_len * 0.38, ry - vi_dyn * 0.65 - 8, "потік W_dyn", size=13, bold=True, color=POS))

    # Кут установки лопаті beta
    f.append(line(rx, ry, rx + 190, ry - 110, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(rx + 198, ry - 116, "хорда лопаті (кут β)", size=12, color=MUTED, anchor="start"))

    # Підписи кутів у динаміці
    b_dyn, _, _ = textbox(cxs[1], H - 56, "Зростання V₀ збільшує кут набігання φ\nКут атаки α = β − φ стрімко падає → тяга T знижується",
                          size=12, pad=8, fill="#eff6ff", stroke=DOWN, sw=1.2)
    f.append(b_dyn)

    return render(os.path.join(IMG, "dynamic-inflow-triangle.svg"), W, H, *f)


# ── Фігура 2: криві C_T(J), C_P(J), eta(J) ──────────────────────────────────
def fig_thrust_advance_ratio_curves():
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Аеродинамічні характеристики гвинта від коефіцієнта поступу J", size=16, bold=True))

    ox = 90
    oy = 320
    gw = 560
    gh = 240

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#d1d5db", sw=1.2))

    for j_val in [0.2, 0.4, 0.6, 0.8, 1.0]:
        gx = ox + j_val * (gw / 1.1)
        f.append(line(gx, oy, gx, oy - gh, color="#e5e7eb", sw=1.0, dash="3,3"))
        f.append(text(gx, oy + 18, "%.1f" % j_val, size=11, color=MUTED))

    f.append(text(ox, oy + 18, "0", size=11, color=MUTED))
    f.append(text(ox + gw / 2, oy + 36, "Коефіцієнт поступу J = V₀ / (n · D)", size=13, bold=True, color=INK))

    # Вісь Y ліворуч (C_T, C_P)
    f.append(text(ox - 48, oy - gh / 2, "C_T , C_P", size=13, bold=True, color=INK))
    f.append(text(ox - 18, oy - gh + 10, "0.12", size=11, color=MUTED))
    f.append(text(ox - 18, oy - gh / 2, "0.06", size=11, color=MUTED))
    f.append(text(ox - 18, oy - 2, "0.00", size=11, color=MUTED))

    # Вісь Y праворуч (eta)
    f.append(text(ox + gw + 48, oy - gh / 2, "ККД η (%)", size=13, bold=True, color=FIELD))
    f.append(text(ox + gw + 18, oy - gh + 10, "80%", size=11, color=FIELD))
    f.append(text(ox + gw + 18, oy - gh / 2, "40%", size=11, color=FIELD))
    f.append(text(ox + gw + 18, oy - 2, "0%", size=11, color=FIELD))

    # Крива C_T (тяга) — спадна червона дуга
    ct_pts = [(0.0, 0.110), (0.2, 0.098), (0.4, 0.080), (0.6, 0.055), (0.8, 0.024), (0.92, 0.000)]
    poly_ct = []
    for j_val, ct_val in ct_pts:
        px = ox + j_val * (gw / 1.1)
        py = oy - (ct_val / 0.12) * (gh - 30)
        poly_ct.append((px, py))
    for k in range(len(poly_ct) - 1):
        f.append(line(poly_ct[k][0], poly_ct[k][1], poly_ct[k+1][0], poly_ct[k+1][1], color=UP, sw=3.0))

    f.append(text(poly_ct[1][0] - 10, poly_ct[1][1] - 12, "C_T (тяга)", size=13, bold=True, color=UP))

    # Крива C_P (потужність) — синя полога
    cp_pts = [(0.0, 0.052), (0.2, 0.051), (0.4, 0.048), (0.6, 0.041), (0.8, 0.028), (0.92, 0.014)]
    poly_cp = []
    for j_val, cp_val in cp_pts:
        px = ox + j_val * (gw / 1.1)
        py = oy - (cp_val / 0.12) * (gh - 30)
        poly_cp.append((px, py))
    for k in range(len(poly_cp) - 1):
        f.append(line(poly_cp[k][0], poly_cp[k][1], poly_cp[k+1][0], poly_cp[k+1][1], color=DOWN, sw=2.2, dash="6,3"))

    f.append(text(poly_cp[2][0] + 35, poly_cp[2][1] + 18, "C_P (потужність)", size=12, bold=True, color=DOWN))

    # Крива eta (ККД) — зелена горбата крива
    eta_pts = [(0.0, 0.0), (0.2, 0.38), (0.4, 0.66), (0.6, 0.80), (0.75, 0.78), (0.92, 0.0)]
    poly_eta = []
    for j_val, eta_val in eta_pts:
        px = ox + j_val * (gw / 1.1)
        py = oy - eta_val * (gh - 30)
        poly_eta.append((px, py))
    for k in range(len(poly_eta) - 1):
        f.append(line(poly_eta[k][0], poly_eta[k][1], poly_eta[k+1][0], poly_eta[k+1][1], color=FIELD, sw=3.2))

    # Максимум ККД
    f.append(circle(poly_eta[3][0], poly_eta[3][1], 5, fill="#eaf7ed", stroke=FIELD, sw=2))
    f.append(text(poly_eta[3][0], poly_eta[3][1] - 14, "η_max ≈ 80%", size=13, bold=True, color=FIELD))

    # Точка нульової тяги J_zero
    j_zero_x = ox + 0.92 * (gw / 1.1)
    f.append(circle(j_zero_x, oy, 5, fill="#fdecea", stroke=UP, sw=2))
    f.append(text(j_zero_x, oy - 14, "J_zero ≈ P / D (T = 0)", size=11, bold=True, color=UP))

    # Зона вітряка
    f.append(rect(j_zero_x, oy - gh, (ox + gw) - j_zero_x, gh, fill="#fef2f2", stroke="none"))
    f.append(text(j_zero_x + 35, oy - gh + 26, "Режим гальмування / вітряка\n(T < 0 при J > J_zero)", size=11, color=UP, bold=True))

    return render(os.path.join(IMG, "thrust-advance-ratio-curves.svg"), W, H, *f)


# ── Фігура 3: порівняння низького й високого кроку ──────────────────────────
def fig_pitch_speed_characteristics():
    W, H = 820, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Порівняння кроку: низький крок (висіння) проти високого (швидкість)", size=16, bold=True))

    col_w = W / 2
    f.append(line(col_w, 48, col_w, H - 20, color="#dfe4ea", sw=1.2, dash="4,6"))

    # --- Ліва панель: Низький крок (P/D ≈ 0.4) ---
    c1 = col_w * 0.5
    f.append(text(c1, 56, "Низький крок: P/D ≈ 0.3...0.5", size=15, bold=True, color=FIELD))
    f.append(text(c1, 74, "(Мультиротори, зависання, важкі коптери)", size=12, color=MUTED))

    # Міні-графік тяги від швидкості
    gx1 = 60
    gy1 = 250
    gw1 = 300
    gh1 = 140
    f.append(rect(gx1, gy1 - gh1, gw1, gh1, fill="#fafbfc", stroke="#d1d5db", sw=1.0))
    f.append(line(gx1, gy1, gx1 + gw1, gy1, color=LINE, sw=1.2))
    f.append(line(gx1, gy1, gx1, gy1 - gh1, color=LINE, sw=1.2))

    # Крива тяги низького кроку (високий старт, крутий спад до невеликої V_max)
    f.append(line(gx1, gy1 - 120, gx1 + 70, gy1 - 100, color=FIELD, sw=3.0))
    f.append(line(gx1 + 70, gy1 - 100, gx1 + 150, gy1 - 55, color=FIELD, sw=3.0))
    f.append(line(gx1 + 150, gy1 - 55, gx1 + 220, gy1, color=FIELD, sw=3.0))

    f.append(text(gx1 + 15, gy1 - 126, "T_stat (макс)", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(circle(gx1 + 220, gy1, 4, fill=FIELD, stroke=FIELD))
    f.append(text(gx1 + 220, gy1 + 16, "V_max (помірна)", size=11, color=FIELD))

    b1, _, _ = textbox(c1, H - 42, "✓ Максимальна тяга на 1 Вт у висінні (8–14 г/Вт)\n✗ Швидке виродження тяги при розгоні вперед",
                       size=12, pad=7, fill="#f4faf6", stroke=FIELD, sw=1.2)
    f.append(b1)

    # --- Права панель: Високий крок (P/D ≈ 0.9...1.2) ---
    c2 = col_w * 1.5
    f.append(text(c2, 56, "Високий крок: P/D ≈ 0.9...1.2+", size=15, bold=True, color=POS))
    f.append(text(c2, 74, "(Швидкісні літаки, далекольоти, FPV-рейсери)", size=12, color=MUTED))

    # Міні-графік тяги від швидкості
    gx2 = col_w + 50
    gy2 = 250
    gw2 = 300
    gh2 = 140
    f.append(rect(gx2, gy2 - gh2, gw2, gh2, fill="#fafbfc", stroke="#d1d5db", sw=1.0))
    f.append(line(gx2, gy2, gx2 + gw2, gy2, color=LINE, sw=1.2))
    f.append(line(gx2, gy2, gx2, gy2 - gh2, color=LINE, sw=1.2))

    # Зона зриву на місці
    f.append(rect(gx2, gy2 - gh2, 55, gh2, fill="#fdf2f2", stroke="none"))
    f.append(text(gx2 + 28, gy2 - gh2 + 20, "Зрив на місці\n(blade stall)", size=10, color=POS))

    # Крива тяги високого кроку (плато, тривале утримання тяги до високої V_max)
    f.append(line(gx2, gy2 - 75, gx2 + 55, gy2 - 95, color=POS, sw=3.0, dash="4,3"))
    f.append(line(gx2 + 55, gy2 - 95, gx2 + 150, gy2 - 80, color=POS, sw=3.0))
    f.append(line(gx2 + 150, gy2 - 80, gx2 + 280, gy2, color=POS, sw=3.0))

    f.append(text(gx2 + 65, gy2 - 105, "Робоча зона тяги", size=11, bold=True, color=POS, anchor="start"))
    f.append(circle(gx2 + 280, gy2, 4, fill=POS, stroke=POS))
    f.append(text(gx2 + 265, gy2 + 16, "V_max (висока)", size=11, color=POS))

    b2, _, _ = textbox(c2, H - 42, "✓ Збереження тяги на високих швидкостях (до 200+ км/год)\n✗ Статичний зрив лопатей на нулі, перегрів моторів на старті",
                       size=12, pad=7, fill="#fdf2f2", stroke=POS, sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "pitch-speed-characteristics.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dynamic_inflow_triangle()
    fig_thrust_advance_ratio_curves()
    fig_pitch_speed_characteristics()
    print("All figures generated successfully.")
