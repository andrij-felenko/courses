# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Зародкоутворення та спінодальний розпад'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_phase_diagram():
    """Фігура 1: Фазова діаграма T-c та залежність вільної енергії G(c) з бінодаллю й спінодаллю."""
    w, h = 840, 480
    frags = []

    frags.append(text(w / 2, 25, "Фазова діаграма T-c та крива вільної енергії G(c)", size=16, bold=True))

    # Ліва панель: Крива G(c) при T < Tc
    g_x, g_y = 65, 390
    g_w, g_h = 320, 310

    frags.append(line(g_x, g_y, g_x + g_w, g_y, color=LINE, sw=1.8))
    frags.append(line(g_x + g_w / 2, g_y, g_x + g_w / 2, g_y - g_h, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(g_x, g_y, g_x, g_y - g_h, color=LINE, sw=1.8))

    frags.append(text(g_x + g_w / 2, g_y + 24, "Концентрація c", size=12, bold=True))
    frags.append(text(g_x - 42, g_y - g_h / 2, "Вільна енергія G(c)", size=12, bold=True, anchor="middle"))

    pts_g = []
    for i in range(101):
        t_val = -1.5 + 3.0 * (i / 100.0)
        c_px = g_x + g_w / 2 + t_val * 90
        val = 0.25 * (t_val**4 - 2 * t_val**2) + 0.3
        y_px = g_y - (val + 0.3) * 180
        pts_g.append((c_px, y_px))

    for i in range(len(pts_g) - 1):
        frags.append(line(pts_g[i][0], pts_g[i][1], pts_g[i+1][0], pts_g[i+1][1], color=NEG, sw=2.5))

    tan_y = g_y - (0.25 * (-1 - 2 + 1) + 0.3) * 180
    frags.append(line(g_x + 20, tan_y, g_x + g_w - 20, tan_y, color=FIELD, sw=1.5, dash="5,4"))
    frags.append(text(g_x + g_w - 15, tan_y - 8, "Спільна дотична", size=11, color=FIELD, anchor="end"))

    c_b1_x = g_x + g_w / 2 - 1.0 * 90
    c_b2_x = g_x + g_w / 2 + 1.0 * 90
    c_s1_x = g_x + g_w / 2 - (1.0 / math.sqrt(3)) * 90
    c_s2_x = g_x + g_w / 2 + (1.0 / math.sqrt(3)) * 90

    frags.append(circle(c_b1_x, tan_y, 4, fill=FIELD, stroke=INK, sw=1.2))
    frags.append(circle(c_b2_x, tan_y, 4, fill=FIELD, stroke=INK, sw=1.2))

    y_s1 = g_y - (0.25 * (1/9 - 2/3) + 0.3) * 180
    frags.append(circle(c_s1_x, y_s1, 4, fill=POS, stroke=INK, sw=1.2))
    frags.append(circle(c_s2_x, y_s1, 4, fill=POS, stroke=INK, sw=1.2))

    frags.append(text(c_b1_x, g_y + 12, "c_α", size=11, color=FIELD, bold=True))
    frags.append(text(c_b2_x, g_y + 12, "c_β", size=11, color=FIELD, bold=True))
    frags.append(text(c_s1_x, y_s1 - 12, "d²G/dc²=0", size=10, color=POS, anchor="end"))
    frags.append(text(c_s2_x, y_s1 - 12, "d²G/dc²=0", size=10, color=POS, anchor="start"))

    frags.append(textbox(g_x + g_w / 2, g_y - g_h + 30, "Температура T < T_c\nd²G/dc² < 0 між спінодалями", size=11, fill="#eff6ff", stroke=NEG, sw=1.2)[0])


    # Права панель: Фазова діаграма T - c
    t_x, t_y = 470, 390
    t_w, t_h = 330, 310

    frags.append(line(t_x, t_y, t_x + t_w, t_y, color=LINE, sw=1.8))
    frags.append(line(t_x, t_y, t_x, t_y - t_h, color=LINE, sw=1.8))

    frags.append(text(t_x + t_w / 2, t_y + 24, "Концентрація c", size=12, bold=True))
    frags.append(text(t_x - 38, t_y - t_h / 2, "Температура T", size=12, bold=True, anchor="middle"))

    c0_x = t_x + t_w / 2
    tc_y = t_y - 250

    pts_bin = []
    pts_spin = []
    for i in range(101):
        c_val = -1.4 + 2.8 * (i / 100.0)
        px = c0_x + c_val * 90
        t_b = 250 - 110 * (c_val**2)
        if t_b >= 0:
            pts_bin.append((px, t_y - t_b))
        t_s = 250 - 330 * (c_val**2)
        if t_s >= 0:
            pts_spin.append((px, t_y - t_s))

    for i in range(len(pts_bin) - 1):
        frags.append(line(pts_bin[i][0], pts_bin[i][1], pts_bin[i+1][0], pts_bin[i+1][1], color=FIELD, sw=2.2))
    for i in range(len(pts_spin) - 1):
        frags.append(line(pts_spin[i][0], pts_spin[i][1], pts_spin[i+1][0], pts_spin[i+1][1], color=POS, sw=2.2, dash="6,3"))

    frags.append(circle(c0_x, tc_y, 5, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(c0_x, tc_y - 12, "Критична точка T_c", size=11, bold=True, color=POS))

    frags.append(text(c0_x, tc_y + 40, "Стабільна фаза (1 фаза)", size=11, color=MUTED, bold=True))
    frags.append(text(t_x + 35, t_y - 140, "Метастабільна", size=10, color=FIELD, bold=True))
    frags.append(text(t_x + t_w - 35, t_y - 140, "Метастабільна", size=10, color=FIELD, bold=True))
    frags.append(textbox(c0_x, t_y - 50, "Нестійка область\n(Спінодальний розпад)\nd²G/dc² < 0", size=11, fill="#fee2e2", stroke=POS, sw=1.2)[0])

    leg_y = h - 25
    frags.append(line(70, leg_y, 110, leg_y, color=FIELD, sw=2))
    frags.append(text(120, leg_y + 4, "Бінодаль (рівновага фаз)", size=11, anchor="start"))
    frags.append(line(360, leg_y, 400, leg_y, color=POS, sw=2, dash="6,3"))
    frags.append(text(410, leg_y + 4, "Спінодаль (межа стійкості d²G/dc²=0)", size=11, anchor="start"))

    render(os.path.join(IMG_DIR, "phase-diagram-binodal-spinodal.svg"), w, h, *frags)


def build_fig2_cnt_barrier():
    """Фігура 2: Залежність вільної енергії утворення зародка ΔG(r) від його радіуса r."""
    w, h = 760, 430
    frags = []

    frags.append(text(w / 2, 25, "Класична теорія зародкоутворення: бар'єр ΔG* та критичний радіус r*", size=15, bold=True))

    ox, oy = 80, 310
    graph_w, graph_h = 610, 240

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy - 150, ox, oy + 90, color=LINE, sw=1.8))

    frags.append(text(ox + graph_w / 2, oy + 32, "Радіус зародка r", size=12, bold=True))
    frags.append(text(ox - 45, oy - 40, "Зміна вільної енергії ΔG", size=12, bold=True, anchor="middle"))

    r_max = 2.4
    r_crit = 1.0
    pts_s = []
    pts_v = []
    pts_tot = []

    for i in range(101):
        r_val = (i / 100.0) * r_max
        px = ox + r_val * 210
        val_s = 3.0 * (r_val**2)
        val_v = -2.0 * (r_val**3)
        val_tot = val_s + val_v

        pts_s.append((px, oy - val_s * 45))
        pts_v.append((px, oy - val_v * 45))
        pts_tot.append((px, oy - val_tot * 45))

    for i in range(len(pts_s) - 1):
        if pts_s[i][1] >= oy - 160:
            frags.append(line(pts_s[i][0], pts_s[i][1], pts_s[i+1][0], pts_s[i+1][1], color=FIELD, sw=1.8, dash="4,4"))
    for i in range(len(pts_v) - 1):
        if pts_v[i][1] <= oy + 85:
            frags.append(line(pts_v[i][0], pts_v[i][1], pts_v[i+1][0], pts_v[i+1][1], color=NEG, sw=1.8, dash="4,4"))
    for i in range(len(pts_tot) - 1):
        if pts_tot[i][1] >= oy - 160 and pts_tot[i][1] <= oy + 85:
            frags.append(line(pts_tot[i][0], pts_tot[i][1], pts_tot[i+1][0], pts_tot[i+1][1], color=POS, sw=2.8))

    rx_crit = ox + r_crit * 210
    ry_crit = oy - 1.0 * 45

    frags.append(line(rx_crit, oy, rx_crit, ry_crit, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(ox, ry_crit, rx_crit, ry_crit, color=MUTED, sw=1.2, dash="3,3"))

    frags.append(circle(rx_crit, ry_crit, 5, fill=POS, stroke=INK, sw=1.5))

    frags.append(text(rx_crit, oy + 18, "r*", size=12, bold=True, color=POS))
    frags.append(text(ox - 15, ry_crit + 4, "ΔG*", size=12, bold=True, color=POS, anchor="end"))

    frags.append(text(ox + 350, oy - 125, "Поверхневий внесок: +4π r² γ (опір)", size=11, color=FIELD, anchor="start"))
    frags.append(text(ox + 350, oy + 65, "Об'ємний внесок: −(4/3)π r³ Δg_v (виграш)", size=11, color=NEG, anchor="start"))
    frags.append(text(rx_crit + 45, ry_crit - 15, "Повний бар'єр ΔG(r)", size=12, color=POS, bold=True, anchor="start"))

    frags.append(textbox(ox + 105, oy - 35, "Докритичні кластери\n(r < r*): розчиняються", size=10, fill="#fef3c7", stroke="#d97706", sw=1.2)[0])
    frags.append(textbox(ox + 335, oy - 35, "Закритичні зародки\n(r > r*): стійко ростуть", size=10, fill="#dcfce7", stroke=FIELD, sw=1.2)[0])

    frags.append(textbox(w / 2, 385, "Критичний радіус: r* = 2γ / Δg_v   │   Робота утворення: ΔG* = 16π γ³ / (3 Δg_v²)", size=12, bold=True, fill="#f1f5f9", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "cnt-barrier-radius.svg"), w, h, *frags)


def build_fig3_spinodal_vs_nucleation():
    """Фігура 3: Морфологічне порівняння: Зародкоутворення проти Спінодального розпаду."""
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 25, "Морфологічна відмінність: Зародкоутворення проти Спінодального розпаду", size=15, bold=True))

    b1_x, b1_y, b1_w, b1_h = 20, 50, 380, 300
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 24, "Зародкоутворення та ріст (Метастабільність)", size=13, bold=True, color=FIELD))
    frags.append(line(b1_x + 15, b1_y + 35, b1_x + b1_w - 15, b1_y + 35, color=MUTED, sw=1, dash="3,3"))

    cx_m, cy_m = b1_x + 85, b1_y + 125
    frags.append(rect(cx_m - 60, cy_m - 50, 120, 100, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))

    droplets = [(cx_m - 30, cy_m - 20, 10), (cx_m + 25, cy_m - 12, 12), (cx_m - 12, cy_m + 18, 9), (cx_m + 25, cy_m + 22, 11)]
    for dx, dy, dr in droplets:
        frags.append(circle(dx, dy, dr, fill=POS, stroke=INK, sw=1.2))

    frags.append(textbox(b1_x + 265, b1_y + 125, "• Ізольовані сферичні краплі\n• Чітка межа розділу одразу\n• Стрибкоподібна зміна складу\n• Вимагає бар'єру ΔG*", size=10, fill="#ffffff", stroke=FIELD, sw=1.2)[0])
    frags.append(text(b1_x + b1_w / 2, b1_y + 260, "Кінетика: очікування зародка → ріст", size=11, bold=True, color=FIELD))


    b2_x, b2_y, b2_w, b2_h = 420, 50, 380, 300
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 24, "Спінодальний розпад (Лабільність)", size=13, bold=True, color=POS))
    frags.append(line(b2_x + 15, b2_y + 35, b2_x + b2_w - 15, b2_y + 35, color=MUTED, sw=1, dash="3,3"))

    cx_s, cy_s = b2_x + 85, b2_y + 125
    frags.append(rect(cx_s - 60, cy_s - 50, 120, 100, fill="#fee2e2", stroke="#e11d48", sw=1.2, rx=4))

    path1 = "M %f %f C %f %f, %f %f, %f %f C %f %f, %f %f, %f %f" % (
        cx_s - 50, cy_s - 30, cx_s - 20, cy_s - 50, cx_s + 5, cy_s - 10, cx_s + 35, cy_s - 35,
        cx_s + 50, cy_s - 10, cx_s + 20, cy_s + 30, cx_s + 50, cy_s + 40
    )
    path2 = "M %f %f C %f %f, %f %f, %f %f" % (
        cx_s - 50, cy_s + 15, cx_s - 20, cy_s - 10, cx_s - 10, cy_s + 40, cx_s + 20, cy_s + 10
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="12" stroke-linecap="round"/>' % (path1, POS))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="10" stroke-linecap="round"/>' % (path2, POS))

    frags.append(textbox(b2_x + 265, b2_y + 125, "• Лабіринтна двобезперервна\n  структура в усьому об'ємі\n• Розмита межа на початку\n• Безперервний ріст амплітуди\n• Безбар'єрний процес", size=10, fill="#ffffff", stroke=POS, sw=1.2)[0])
    frags.append(text(b2_x + b2_w / 2, b2_y + 260, "Кінетика: одночасне сходження складу", size=11, bold=True, color=POS))

    frags.append(text(w / 2, 370, "Різниця в механізмі визначає кінцеву мікроструктуру та її механічні властивості", size=12, bold=True, color=LINE))

    render(os.path.join(IMG_DIR, "spinodal-vs-nucleation-morphology.svg"), w, h, *frags)


def build_fig4_cahn_hilliard_amplification():
    """Фігура 4: Інкремент наростання R(k) від хвильового числа k у лінійній теорії Кана—Гілліарда."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 25, "Лінійна теорія Кана—Гілліарда: коефіцієнт підсилення R(k)", size=15, bold=True))

    ox, oy = 80, 290
    graph_w, graph_h = 610, 220

    frags.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy - 140, ox, oy + 70, color=LINE, sw=1.8))

    frags.append(text(ox + graph_w / 2, oy + 32, "Хвильове число флуктуації k", size=12, bold=True))
    frags.append(text(ox - 45, oy - 35, "Інкремент наростання R(k)", size=12, bold=True, anchor="middle"))

    kc_x = ox + 1.0 * 360
    km_x = ox + 0.707 * 360
    r_max_y = oy - 0.75 * 160

    pts_r = []
    for i in range(101):
        k_val = (i / 100.0) * 1.35
        px = ox + k_val * 360
        r_val = 2 * (k_val**2) - (k_val**4)
        py = oy - r_val * 160
        pts_r.append((px, py))

    for i in range(len(pts_r) - 1):
        if pts_r[i][1] <= oy + 65 and pts_r[i+1][1] <= oy + 65:
            col = POS if pts_r[i][1] <= oy else NEG
            frags.append(line(pts_r[i][0], pts_r[i][1], pts_r[i+1][0], pts_r[i+1][1], color=col, sw=2.8))

    frags.append(line(km_x, oy, km_x, r_max_y, color=POS, sw=1.2, dash="3,3"))
    frags.append(line(ox, r_max_y, km_x, r_max_y, color=POS, sw=1.2, dash="3,3"))
    frags.append(circle(km_x, r_max_y, 5, fill=POS, stroke=INK, sw=1.5))

    frags.append(text(kc_x, oy + 18, "k_c", size=12, bold=True, color=LINE))
    frags.append(text(km_x, oy + 18, "k_m = k_c / √2", size=12, bold=True, color=POS))
    frags.append(text(ox - 12, r_max_y + 4, "R_max", size=12, bold=True, color=POS, anchor="end"))

    frags.append(textbox(ox + 130, oy - 70, "Незгасаючі моди (R > 0):\nЕкспоненційне зростання флуктуацій", size=10, fill="#fee2e2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(ox + 450, oy + 35, "Загасаючі моди (R < 0):\nГрадієнтний опір пригнічує\nкороткі хвилі", size=10, fill="#dbeafe", stroke=NEG, sw=1.2)[0])

    frags.append(textbox(w / 2, 380, "Домінантна довжина хвилі структури: λ_m = 2π / k_m = 2π √( 2κ / |f''| )", size=12, bold=True, fill="#f1f5f9", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "cahn-hilliard-amplification.svg"), w, h, *frags)


if __name__ == "__main__":
    build_fig1_phase_diagram()
    build_fig2_cnt_barrier()
    build_fig3_spinodal_vs_nucleation()
    build_fig4_cahn_hilliard_amplification()
    print("Фігури успішно згенеровано у", IMG_DIR)
