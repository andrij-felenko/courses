# -*- coding: utf-8 -*-
"""Фігури до теми «Пряма і непряма заборонена зона».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_GRAY = "#7f8c8d"

def polyline(pts, color=LINE, sw=1.5, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'


# ── Фігура 1: Порівняння прямозонного та непрямозонного напівпровідників ──
def fig_direct_vs_indirect():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Енергетичні зони у k-просторі: прямий та непрямий напівпровідники", size=15, bold=True))

    midx = W / 2
    f.append(line(midx, 45, midx, H - 25, color="#e2e8f0", sw=1.5, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Прямозонний напівпровідник (GaAs) ---
    f.append(text(midx / 2, 52, "Пряма заборонена зона (напр. GaAs)", size=13, bold=True, color=COLOR_BLUE))

    # Осі E та k
    f.append(line(50, H - 50, 330, H - 50, color=LINE, sw=1.5))
    f.append(arrow(330, H - 50, 340, H - 50, color=LINE, sw=1.5))
    f.append(text(345, H - 46, "k", size=12, bold=True, italic=True))

    f.append(line(190, H - 40, 190, 75, color=LINE, sw=1.5))
    f.append(arrow(190, 75, 190, 65, color=LINE, sw=1.5))
    f.append(text(190, 58, "E", size=12, bold=True, italic=True))

    # Валентна зона Ev (парабола вниз, максимум при k=0)
    pts_v1 = []
    for x_i in range(70, 311, 4):
        k_val = (x_i - 190) / 45.0
        e_val = (H - 120) - 30 * (k_val ** 2)
        pts_v1.append(f"{x_i:.1f},{e_val:.1f}")
    f.append(polyline(" ".join(pts_v1), color=COLOR_GREEN, sw=2.5, fill="none"))
    f.append(text(80, H - 100, "Валентна зона (E_v)", size=11, bold=True, color=COLOR_GREEN))

    # Зона провідності Ec (парабола вгору, мінімум при k=0)
    pts_c1 = []
    for x_i in range(70, 311, 4):
        k_val = (x_i - 190) / 45.0
        e_val = 135 + 40 * (k_val ** 2)
        pts_c1.append(f"{x_i:.1f},{e_val:.1f}")
    f.append(polyline(" ".join(pts_c1), color=COLOR_BLUE, sw=2.5, fill="none"))
    f.append(text(75, 120, "Зона провідності (E_c)", size=11, bold=True, color=COLOR_BLUE))

    # Вертикальний перехід (фотон)
    f.append(arrow(190, H - 120, 190, 135, color=COLOR_RED, sw=2.2))
    f.append(circle(190, H - 120, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(circle(190, 135, 4, fill=COLOR_BLUE, stroke=LINE, sw=1))

    # Напис фотона
    f.append(text(125, 205, "hν = E_g", size=12, bold=True, color=COLOR_RED))
    f.append(text(125, 222, "Δk = 0", size=11, color=COLOR_GRAY))

    # Позначення Eg
    f.append(line(205, H - 120, 260, H - 120, color=COLOR_GRAY, sw=1, dash="3,3"))
    f.append(line(205, 135, 260, 135, color=COLOR_GRAY, sw=1, dash="3,3"))
    f.append(arrow(245, 135, 245, H - 120, color=INK, sw=1.2))
    f.append(arrow(245, H - 120, 245, 135, color=INK, sw=1.2))
    f.append(text(255, (135 + H - 120) / 2, "E_g", size=12, bold=True))

    b_left, _, _ = textbox(midx / 2, H - 22, "Перехід вертикальний: фотон здатний сам\nзабезпечити і енергію, і збереження k",
                           size=11, pad=5, fill="#eef6ff", stroke="#b3d4ff", sw=1.0)
    f.append(b_left)


    # --- ПРАВА ЧАСТИНА: Непрямозонний напівпровідник (Si) ---
    f.append(text(midx + midx / 2, 52, "Непряма заборонена зона (напр. Si)", size=13, bold=True, color=COLOR_PURPLE))

    # Осі E та k
    f.append(line(420, H - 50, 700, H - 50, color=LINE, sw=1.5))
    f.append(arrow(700, H - 50, 710, H - 50, color=LINE, sw=1.5))
    f.append(text(715, H - 46, "k", size=12, bold=True, italic=True))

    f.append(line(470, H - 40, 470, 75, color=LINE, sw=1.5))
    f.append(arrow(470, 75, 470, 65, color=LINE, sw=1.5))
    f.append(text(470, 58, "E", size=12, bold=True, italic=True))
    f.append(text(470, H - 34, "k=0 (Γ)", size=10, color=COLOR_GRAY))

    # Валентна зона Ev (максимум при k=0)
    pts_v2 = []
    for x_i in range(430, 671, 4):
        k_val = (x_i - 470) / 45.0
        e_val = (H - 120) - 30 * (k_val ** 2)
        pts_v2.append(f"{x_i:.1f},{e_val:.1f}")
    f.append(polyline(" ".join(pts_v2), color=COLOR_GREEN, sw=2.5, fill="none"))

    # Зона провідності Ec (мінімум зміщений в точку k_0, наприклад x=620)
    k_min_x = 620
    pts_c2 = []
    for x_i in range(460, 701, 4):
        k_val = (x_i - k_min_x) / 45.0
        e_val = 145 + 40 * (k_val ** 2)
        pts_c2.append(f"{x_i:.1f},{e_val:.1f}")
    f.append(polyline(" ".join(pts_c2), color=COLOR_BLUE, sw=2.5, fill="none"))
    f.append(text(k_min_x, H - 34, "k_0", size=10, bold=True, color=COLOR_GRAY))
    f.append(line(k_min_x, H - 46, k_min_x, H - 54, color=COLOR_GRAY, sw=1))

    # Двостадійний непрямий перехід: фотон вертикально + фонон горизонтально
    f.append(line(470, H - 120, 470, 145, color=COLOR_RED, sw=1.8, dash="4,4"))
    f.append(arrow(470, H - 120, 470, 145, color=COLOR_RED, sw=2))
    f.append(circle(470, H - 120, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))

    # Горизонтальний перехід фонона
    f.append(arrow(470, 145, 620, 145, color=COLOR_ORANGE, sw=2.2))
    f.append(circle(620, 145, 4, fill=COLOR_BLUE, stroke=LINE, sw=1))

    f.append(text(420, 200, "1. Фотон hν", size=11, bold=True, color=COLOR_RED))
    f.append(text(540, 130, "2. Фонон ħΩ (Δk = k_0)", size=11, bold=True, color=COLOR_ORANGE))

    # Позначення непрямої забороненої зони Eg
    f.append(line(470, H - 120, 660, H - 120, color=COLOR_GRAY, sw=1, dash="3,3"))
    f.append(line(620, 145, 660, 145, color=COLOR_GRAY, sw=1, dash="3,3"))
    f.append(arrow(650, 145, 650, H - 120, color=INK, sw=1.2))
    f.append(arrow(650, H - 120, 650, 145, color=INK, sw=1.2))
    f.append(text(660, (145 + H - 120) / 2, "E_g", size=12, bold=True))

    b_right, _, _ = textbox(midx + midx / 2, H - 22, "Перехід тричастинковий: потрібен фонон\nдля компенсації великого імпульсу Δk",
                            size=11, pad=5, fill="#fff6ee", stroke="#ffd8b3", sw=1.0)
    f.append(b_right)

    render(os.path.join(IMG, "direct-vs-indirect-band.svg"), W, H, *f)


# ── Фігура 2: Порівняння імпульсу фотона та розміру зони Бріллюена ──
def fig_k_momentum_conservation():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Масштаб квазіімпульсу: оптичний фотон проти решітки (зони Бріллюена)", size=15, bold=True))

    y_axis = 180
    left_k = 80
    right_k = 680
    center_k = 380

    # Вісь k
    f.append(line(left_k - 30, y_axis, right_k + 30, y_axis, color=LINE, sw=1.8))
    f.append(arrow(right_k + 30, y_axis, right_k + 40, y_axis, color=LINE, sw=1.8))
    f.append(text(right_k + 48, y_axis + 4, "k", size=13, bold=True, italic=True))

    # Засічки -k_ZB, 0, +k_ZB
    f.append(line(left_k, y_axis - 15, left_k, y_axis + 15, color=COLOR_PURPLE, sw=2))
    f.append(text(left_k, y_axis + 32, "-k_ZB = -π/a", size=12, bold=True, color=COLOR_PURPLE))
    f.append(text(left_k, y_axis + 48, "(≈ -6·10⁹ м⁻¹)", size=10, color=COLOR_GRAY))

    f.append(line(right_k, y_axis - 15, right_k, y_axis + 15, color=COLOR_PURPLE, sw=2))
    f.append(text(right_k, y_axis + 32, "+k_ZB = +π/a", size=12, bold=True, color=COLOR_PURPLE))
    f.append(text(right_k, y_axis + 48, "(≈ +6·10⁹ м⁻¹)", size=10, color=COLOR_GRAY))

    f.append(line(center_k, y_axis - 12, center_k, y_axis + 12, color=LINE, sw=1.5))
    f.append(text(center_k, y_axis + 32, "k = 0 (Центр зони)", size=12, bold=True))

    # Верхня стрілка зони Бріллюена
    f.append(arrow(center_k, 70, left_k, 70, color=COLOR_PURPLE, sw=1.5))
    f.append(arrow(center_k, 70, right_k, 70, color=COLOR_PURPLE, sw=1.5))
    f.append(text(center_k, 52, "Ширина першої зони Бріллюена  2k_ZB ≈ 1.2·10¹⁰ м⁻¹", size=12, bold=True, color=COLOR_PURPLE))

    # Стрілочка фотона
    f.append(line(center_k, y_axis, center_k + 8, y_axis, color=COLOR_RED, sw=3))
    f.append(circle(center_k, y_axis, 4, fill=COLOR_RED, stroke="none"))
    f.append(arrow(center_k, 130, center_k, y_axis - 10, color=COLOR_RED, sw=1.6))

    b_ph, _, _ = textbox(190, 125, "Імпульс фотона k_ph = 2π/λ ≈ 10⁷ м⁻¹\n(< 0.1% від розміру зони Бріллюена!)",
                         size=11, pad=6, fill="#ffeef0", stroke="#ffb3b8", sw=1.2)
    f.append(b_ph)

    # Стрілка фонона
    k0_pos = left_k + 0.85 * (right_k - left_k)
    f.append(arrow(center_k, y_axis + 85, k0_pos, y_axis + 85, color=COLOR_ORANGE, sw=2.5))
    f.append(line(k0_pos, y_axis - 10, k0_pos, y_axis + 95, color=COLOR_ORANGE, sw=1.2, dash="3,3"))
    f.append(text(k0_pos, y_axis + 112, "Мінімум Si (k_0 ≈ 0.85 k_ZB)", size=11, bold=True, color=COLOR_ORANGE))

    f.append(text((center_k + k0_pos) / 2, y_axis + 70, "Квазіімпульс фонона q ≈ k_0 (величезний!)", size=11, bold=True, color=COLOR_ORANGE))

    render(os.path.join(IMG, "k-momentum-conservation.svg"), W, H, *f)


# ── Фігура 3: Спектр поглинання alpha(h*nu) ──
def fig_absorption_spectrum():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Коефіцієнт оптичного поглинання α(hν) для прямого й непрямого напівпровідників", size=14, bold=True))

    x0, y0 = 90, H - 50
    w_chart, h_chart = 580, 250

    f.append(line(x0, y0, x0 + w_chart, y0, color=LINE, sw=1.5))
    f.append(arrow(x0 + w_chart, y0, x0 + w_chart + 10, y0, color=LINE, sw=1.5))
    f.append(text(x0 + w_chart + 18, y0 + 4, "hν (еВ)", size=12, bold=True, italic=True))

    f.append(line(x0, y0, x0, y0 - h_chart, color=LINE, sw=1.5))
    f.append(arrow(x0, y0 - h_chart, x0, y0 - h_chart - 10, color=LINE, sw=1.5))
    f.append(text(x0 - 40, y0 - h_chart - 10, "α (см⁻¹)", size=12, bold=True, italic=True))

    y_ticks = [
        (y0, "10⁰"),
        (y0 - 50, "10¹"),
        (y0 - 100, "10²"),
        (y0 - 150, "10³"),
        (y0 - 200, "10⁴"),
        (y0 - 250, "10⁵")
    ]
    for y_pos, label in y_ticks:
        f.append(line(x0 - 5, y_pos, x0, y_pos, color=LINE, sw=1))
        f.append(line(x0, y_pos, x0 + w_chart, y_pos, color="#e2e8f0", sw=1, dash="3,3"))
        f.append(text(x0 - 22, y_pos + 4, label, size=11, color=COLOR_GRAY))

    def x_scale(e_val):
        return x0 + (e_val - 0.8) / (3.6 - 0.8) * w_chart

    # 1) GaAs (Прямозонний, Eg = 1.42 еВ)
    x_gaas = x_scale(1.42)
    pts_gaas = [(x_gaas, y0)]
    for e_v in [1.43, 1.45, 1.5, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5]:
        x_p = x_scale(e_v)
        alpha_val = 1e4 * ((e_v - 1.42) ** 0.5) + 2000
        if alpha_val > 1e5: alpha_val = 1e5
        import math
        log_alpha = math.log10(max(alpha_val, 1))
        y_p = y0 - (log_alpha / 5.0) * 250
        pts_gaas.append((x_p, y_p))

    str_gaas = " ".join([f"{xp:.1f},{yp:.1f}" for xp, yp in pts_gaas])
    f.append(polyline(str_gaas, color=COLOR_RED, sw=3, fill="none"))
    f.append(line(x_gaas, y0 - 5, x_gaas, y0 + 5, color=COLOR_RED, sw=1.5))
    f.append(text(x_gaas, y0 + 20, "1.42 еВ (GaAs)", size=10, bold=True, color=COLOR_RED))

    # 2) Si (Непрямозонний, Eg_ind = 1.12 еВ, Eg_dir = 3.4 еВ)
    x_si = x_scale(1.12)
    x_si_dir = x_scale(3.4)
    pts_si = [(x_si, y0)]
    for e_v in [1.15, 1.2, 1.3, 1.5, 1.8, 2.2, 2.6, 3.0, 3.39]:
        x_p = x_scale(e_v)
        alpha_val = 3000 * ((e_v - 1.12) ** 2) + 20
        import math
        log_alpha = math.log10(max(alpha_val, 1))
        y_p = y0 - (log_alpha / 5.0) * 250
        pts_si.append((x_p, y_p))

    for e_v in [3.4, 3.45, 3.5, 3.6]:
        x_p = x_scale(e_v)
        alpha_val = 2e4 + 8e4 * ((e_v - 3.4) ** 0.5)
        import math
        log_alpha = math.log10(max(alpha_val, 1))
        y_p = y0 - (log_alpha / 5.0) * 250
        pts_si.append((x_p, y_p))

    str_si = " ".join([f"{xp:.1f},{yp:.1f}" for xp, yp in pts_si])
    f.append(polyline(str_si, color=COLOR_BLUE, sw=3, fill="none", dash="7,3"))
    f.append(line(x_si, y0 - 5, x_si, y0 + 5, color=COLOR_BLUE, sw=1.5))
    f.append(text(x_si - 15, y0 + 20, "1.12 еВ (Si, непрямий)", size=10, bold=True, color=COLOR_BLUE))

    f.append(line(x_si_dir, y0 - 5, x_si_dir, y0 + 5, color=COLOR_PURPLE, sw=1.5))
    f.append(text(x_si_dir - 25, y0 + 20, "3.4 еВ (Si, прямий)", size=10, bold=True, color=COLOR_PURPLE))

    f.append(text(x_scale(1.7), y0 - 220, "GaAs: Стрімке прямозонне поглинання α ~ (hν - E_g)¹/²", size=11, bold=True, color=COLOR_RED))
    f.append(text(x_scale(2.0), y0 - 110, "Si: Пологе непрямозонне поглинання α ~ (hν - E_g ∓ ℏΩ)²", size=11, bold=True, color=COLOR_BLUE))

    render(os.path.join(IMG, "absorption-spectrum.svg"), W, H, *f)


# ── Фігура 4: Тюнінг зони у GaAs_(1-x)P_x ──
def fig_gaasp_tuning():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Зміна зонної структури у сплаві GaAs_(1-x)P_x залежно від складу x", size=14, bold=True))

    x0, y0 = 90, H - 60
    w_chart, h_chart = 550, 220

    f.append(line(x0, y0, x0 + w_chart, y0, color=LINE, sw=1.5))
    f.append(arrow(x0 + w_chart, y0, x0 + w_chart + 10, y0, color=LINE, sw=1.5))
    f.append(text(x0 + w_chart + 15, y0 + 4, "х (доля P)", size=12, bold=True))

    f.append(line(x0, y0, x0, y0 - h_chart, color=LINE, sw=1.5))
    f.append(arrow(x0, y0 - h_chart, x0, y0 - h_chart - 10, color=LINE, sw=1.5))
    f.append(text(x0 - 45, y0 - h_chart - 10, "Енергія (еВ)", size=12, bold=True))

    f.append(text(x0, y0 + 20, "x = 0 (GaAs)", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(x0 + w_chart, y0 + 20, "x = 1.0 (GaP)", size=11, bold=True, color=COLOR_GREEN))

    x_cross = x0 + 0.45 * w_chart
    f.append(line(x_cross, y0, x_cross, y0 - h_chart, color=COLOR_RED, sw=1.5, dash="4,4"))
    f.append(text(x_cross, y0 + 20, "x ≈ 0.45", size=11, bold=True, color=COLOR_RED))

    f.append(rect(x0, y0 - h_chart, x_cross - x0, h_chart, fill="#eef6ff", stroke="none"))
    f.append(text(x0 + (x_cross - x0) / 2, y0 - h_chart + 20, "Прямозонний напівпровідник\n(Ефективний світлодіод)", size=11, bold=True, color=COLOR_BLUE))

    f.append(rect(x_cross, y0 - h_chart, (x0 + w_chart) - x_cross, h_chart, fill="#fff0f0", stroke="none"))
    f.append(text(x_cross + ((x0 + w_chart) - x_cross) / 2, y0 - h_chart + 20, "Непрямозонний напівпровідник\n(Потрібні домішки N)", size=11, bold=True, color=COLOR_RED))

    def y_energy(e_v):
        return y0 - (e_v - 1.2) / (2.9 - 1.2) * h_chart

    pts_gamma = []
    for step in range(101):
        x_val = step / 100.0
        e_val = 1.42 + 1.15 * x_val + 0.21 * (x_val ** 2)
        xp = x0 + x_val * w_chart
        yp = y_energy(e_val)
        pts_gamma.append(f"{xp:.1f},{yp:.1f}")

    f.append(polyline(" ".join(pts_gamma), color=COLOR_BLUE, sw=2.5, fill="none"))
    f.append(text(x0 + 40, y_energy(1.5), "Мінімум Γ (прямий)", size=11, bold=True, color=COLOR_BLUE))

    pts_x = []
    for step in range(101):
        x_val = step / 100.0
        e_val = 1.90 + 0.36 * x_val
        xp = x0 + x_val * w_chart
        yp = y_energy(e_val)
        pts_x.append(f"{xp:.1f},{yp:.1f}")

    f.append(polyline(" ".join(pts_x), color=COLOR_ORANGE, sw=2.5, fill="none", dash="6,3"))
    f.append(text(x0 + 40, y_energy(1.98), "Мінімум X (непрямий)", size=11, bold=True, color=COLOR_ORANGE))

    e_cross = 1.90 + 0.36 * 0.45
    f.append(circle(x_cross, y_energy(e_cross), 5, fill=COLOR_RED, stroke=LINE, sw=1.5))
    f.append(text(x_cross + 10, y_energy(e_cross) - 10, "Перехід пряма/непряма зона (≈ 1.98 еВ)", size=10, bold=True, color=COLOR_RED))

    render(os.path.join(IMG, "gaasp-band-tuning.svg"), W, H, *f)


if __name__ == "__main__":
    fig_direct_vs_indirect()
    fig_k_momentum_conservation()
    fig_absorption_spectrum()
    fig_gaasp_tuning()
    print("Успішно згенеровано 4 SVG фігури у ./img/")
