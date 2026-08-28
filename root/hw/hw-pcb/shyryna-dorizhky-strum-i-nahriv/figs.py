# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Ширина доріжки, струм і нагрів»."""

import os
import sys
import math

# Додаємо scripts до шляху імпорту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


def draw_current_vs_area_dt():
    """Діаграма 1: Залежність допустимого струму від ширини та площі перерізу провідника
    при різних значеннях допустимого перегріву Delta T за стандартом IPC-2152 / IPC-2221.
    """
    w, h = 860, 540
    frags = []

    # Заголовок графіка
    t_box, _, _ = textbox(w / 2, 28, "Струмова спроможність мідного провідника (фольга 1 oz = 35 мкм)",
                          size=15, bold=True, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(t_box)

    # Область побудови графіка
    gx, gy, gw, gh = 90, 75, 520, 360

    # Фон графіка
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=2))

    # Сітка та мітки осей
    widths = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    for val in widths:
        cx = gx + (val / 5.0) * gw
        frags.append(line(cx, gy, cx, gy + gh, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(line(cx, gy + gh, cx, gy + gh + 5, color="#64748b", sw=1.2))
        frags.append(text(cx, gy + gh + 18, "%.1f" % val, size=11, color="#475569", anchor="middle"))

    frags.append(text(gx + gw / 2, gy + gh + 42, "Ширина доріжки W (мм) при товщині фольги 35 мкм (1 oz)", size=12, bold=True, color=INK, anchor="middle"))

    # Y-вісь: Струм від 0 до 16 А
    currents = [0, 2, 4, 6, 8, 10, 12, 14, 16]
    for val in currents:
        cy = gy + gh - (val / 16.0) * gh
        frags.append(line(gx, cy, gx + gw, cy, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(line(gx - 5, cy, gx, cy, color="#64748b", sw=1.2))
        frags.append(text(gx - 12, cy + 4, "%d" % val, size=11, color="#475569", anchor="end"))

    frags.append(text(28, gy + gh / 2, "Допустимий струм I (Ампери)", size=12, bold=True, color=INK, anchor="middle"))

    # Криві для різних Delta T за IPC-2152 (з урахуванням площини відведення тепла)
    curves_data = [
        {"dt": 10, "col": "#2563eb", "dash": None, "name": "ΔT = 10 °C (Прецизійний режим)"},
        {"dt": 20, "col": "#059669", "dash": None, "name": "ΔT = 20 °C (Стандартний IPC)"},
        {"dt": 30, "col": "#d97706", "dash": None, "name": "ΔT = 30 °C (Компактні плати)"},
        {"dt": 50, "col": "#dc2626", "dash": None, "name": "ΔT = 50 °C (Граничний нагрів)"},
    ]

    # Малюємо криві
    for c in curves_data:
        dt = c["dt"]
        pts = []
        for i in range(1, 51):
            w_mm = i * 0.1
            a_mils2 = w_mm * 54.25
            curr = 0.048 * math.pow(dt, 0.44) * math.pow(a_mils2, 0.725)
            if curr > 16.5:
                w_lim = math.pow(16.0 / (0.048 * math.pow(dt, 0.44)), 1.0 / 0.725) / 54.25
                px = gx + (w_lim / 5.0) * gw
                py = gy
                pts.append((px, py))
                break
            px = gx + (w_mm / 5.0) * gw
            py = gy + gh - (curr / 16.0) * gh
            pts.append((px, py))

        path_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts])
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"%s/>' %
                     (path_str, c["col"], ' stroke-dasharray="%s"' % c["dash"] if c["dash"] else ''))

    # Крива для внутрішнього шару за старим IPC-2221 (k=0.024, Delta T = 20 °C) для порівняння
    pts_int = []
    for i in range(1, 51):
        w_mm = i * 0.1
        a_mils2 = w_mm * 54.25
        curr = 0.024 * math.pow(20, 0.44) * math.pow(a_mils2, 0.725)
        if curr > 16.0:
            break
        px = gx + (w_mm / 5.0) * gw
        py = gy + gh - (curr / 16.0) * gh
        pts_int.append((px, py))
    path_int = "M " + " L ".join(["%.1f,%.1f" % p for p in pts_int])
    frags.append('<path d="%s" fill="none" stroke="#64748b" stroke-width="2.0" stroke-dasharray="4,4"/>' % path_int)

    # Легенда праворуч
    lx, ly = 635, 85
    frags.append(rect(lx, ly, 205, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(lx + 102, ly + 22, "Параметри розрахунку", size=12, bold=True, color=INK, anchor="middle"))
    frags.append(line(lx + 10, ly + 32, lx + 195, ly + 32, color="#e2e8f0", sw=1.0))

    items = [
        {"col": "#dc2626", "txt": "ΔT = 50 °C", "dash": None},
        {"col": "#d97706", "txt": "ΔT = 30 °C", "dash": None},
        {"col": "#059669", "txt": "ΔT = 20 °C (IPC)", "dash": None},
        {"col": "#2563eb", "txt": "ΔT = 10 °C", "dash": None},
        {"col": "#64748b", "txt": "Внутр. IPC-2221", "dash": "4,4"},
    ]

    for idx, it in enumerate(items):
        item_y = ly + 55 + idx * 36
        frags.append(line(lx + 15, item_y, lx + 45, item_y, color=it["col"], sw=2.5, dash=it["dash"]))
        frags.append(circle(lx + 30, item_y, 3.5, fill=it["col"], stroke="#ffffff", sw=1.0))
        frags.append(text(lx + 52, item_y + 4, it["txt"], size=11, bold=True, color="#334155", anchor="start"))

    info_box, _, _ = textbox(lx + 102, ly + 310, "Фольга: 1 oz (35 мкм)\nДіелектрик: FR-4\nT_amb = 25 °C",
                             size=10, fill="#f1f5f9", stroke="#cbd5e1", pad=6)
    frags.append(info_box)

    # Виноски на графіку
    pt1_x = gx + (2.0 / 5.0) * gw
    pt1_y = gy + gh - (5.4 / 16.0) * gh
    frags.append(circle(pt1_x, pt1_y, 4.5, fill="#059669", stroke="#ffffff", sw=1.5))
    frags.append(line(pt1_x, pt1_y, pt1_x + 35, pt1_y - 25, color="#059669", sw=1.2))
    frags.append(rect(pt1_x + 35, pt1_y - 38, 76, 22, fill="#ecfdf5", stroke="#059669", sw=1.0, rx=3))
    frags.append(text(pt1_x + 73, pt1_y - 23, "5.4 A @ 2 мм", size=10, bold=True, color="#065f46", anchor="middle"))

    pt2_x = gx + (4.0 / 5.0) * gw
    pt2_y = gy + gh - (8.9 / 16.0) * gh
    frags.append(circle(pt2_x, pt2_y, 4.5, fill="#059669", stroke="#ffffff", sw=1.5))
    frags.append(line(pt2_x, pt2_y, pt2_x + 30, pt2_y - 25, color="#059669", sw=1.2))
    frags.append(rect(pt2_x + 30, pt2_y - 38, 76, 22, fill="#ecfdf5", stroke="#059669", sw=1.0, rx=3))
    frags.append(text(pt2_x + 68, pt2_y - 23, "8.9 A @ 4 мм", size=10, bold=True, color="#065f46", anchor="middle"))

    out_path = os.path.join(IMG_DIR, "current-vs-area-dt.svg")
    render(out_path, w, h, *frags)
    print("Rendered:", out_path)


def draw_trace_thermal_profile():
    """Діаграма 2: Тепловий профіль та шляхи розсіювання тепла силовою доріжкою
    на багатошаровій друкованій платі (FR-4 + суцільні мідні полігони).
    """
    w, h = 880, 580
    frags = []

    # Головний заголовок
    t_box, _, _ = textbox(w / 2, 28, "Тепловий профіль та механізми розсіювання тепла силовим провідником",
                          size=15, bold=True, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(t_box)

    # Схема поперечного перерізу плати
    bx, by, bw, bh = 80, 195, 720, 230

    # Тіло плати (діелектрик FR-4)
    frags.append(rect(bx, by, bw, bh, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(bx + bw - 70, by + bh / 2, "FR-4 Core\nk = 0.3 Вт/(м·К)", size=11, color="#92400e", anchor="middle"))

    cx = bx + bw / 2
    track_w = 140
    track_h = 16

    # Внутрішній шар міді GND (L2 Plane)
    frags.append(rect(bx + 10, by + 90, bw - 20, 10, fill="#b45309", stroke="#78350f", sw=1.2, rx=1))

    # Нижній шар міді L4 (GND Bottom)
    frags.append(rect(bx + 10, by + bh - 14, bw - 20, 10, fill="#b45309", stroke="#78350f", sw=1.2, rx=1))
    frags.append(text(bx + 115, by + bh - 6, "Нижній полігон L4 (Bottom Cu)", size=10, bold=True, color="#ffffff", anchor="middle"))

    # Верхня мідна доріжка (Hot Trace)
    track_x = cx - track_w / 2
    track_y = by - track_h
    frags.append(rect(track_x, track_y, track_w, track_h, fill="#ea580c", stroke="#9a3412", sw=2.0, rx=2))
    frags.append(text(cx, track_y + 11, "Силова доріжка (I²·R, 85 °C)", size=11, bold=True, color="#ffffff", anchor="middle"))

    # Паяльна маска поверх доріжки
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="4" fill="#15803d" fill-opacity="0.85" rx="1"/>' % (track_x - 10, track_y - 4, track_w + 20))

    # Стрілки теплових потоків
    # 1. Конвекція вгору (Convection to air)
    frags.append(arrow(cx - 30, track_y - 6, cx - 30, track_y - 40, color="#2563eb", sw=2.0))
    frags.append(arrow(cx, track_y - 6, cx, track_y - 46, color="#2563eb", sw=2.0))
    frags.append(arrow(cx + 30, track_y - 6, cx + 30, track_y - 40, color="#2563eb", sw=2.0))

    t_conv, _, _ = textbox(cx, track_y - 75, "Вільна конвекція\nq_conv = h·A·ΔT", size=10, bold=True,
                           fill="#eff6ff", stroke="#3b82f6", color="#1e40af", pad=5)
    frags.append(t_conv)

    # 2. Теплове випромінювання (Radiation from soldermask)
    frags.append(arrow(track_x - 5, track_y - 4, track_x - 30, track_y - 30, color="#7c3aed", sw=1.8))
    frags.append(arrow(track_x + track_w + 5, track_y - 4, track_x + track_w + 30, track_y - 30, color="#7c3aed", sw=1.8))
    t_rad_l, _, _ = textbox(track_x - 90, track_y - 48, "Випромінювання\nε ≈ 0.9 (паяльна маска)", size=9,
                            fill="#faf5ff", stroke="#a855f7", color="#6b21a8", pad=4)
    frags.append(t_rad_l)

    t_rad_r, _, _ = textbox(track_x + track_w + 90, track_y - 48, "Випромінювання\nq_rad = ε·σ·A·(T⁴-T₀⁴)", size=9,
                            fill="#faf5ff", stroke="#a855f7", color="#6b21a8", pad=4)
    frags.append(t_rad_r)

    # 3. Теплопровідність у товщу FR-4 вниз (Conduction down)
    frags.append(arrow(cx - 150, by + 12, cx - 150, by + 75, color="#dc2626", sw=2.2))
    frags.append(arrow(cx + 150, by + 12, cx + 150, by + 75, color="#dc2626", sw=2.2))

    t_cond, _, _ = textbox(cx, by + 45, "Вертикальна теплопровідність FR-4\nq_z = k_FR4 · A · (ΔT / d)", size=10, bold=True,
                           fill="#fef2f2", stroke="#ef4444", color="#991b1b", pad=5)
    frags.append(t_cond)

    # 4. Латеральне розтікання тепла по мідному екрану GND (Lateral heat spreading)
    frags.append(arrow(cx - 110, by + 72, cx - 230, by + 72, color="#b45309", sw=2.5))
    frags.append(arrow(cx + 110, by + 72, cx + 230, by + 72, color="#b45309", sw=2.5))

    t_lat_l, _, _ = textbox(cx - 250, by + 130, "Латеральне розтікання\nпо міді (k = 385 Вт/м·К)", size=9, bold=True,
                            fill="#fffbeb", stroke="#d97706", color="#b45309", pad=4)
    frags.append(t_lat_l)

    t_lat_r, _, _ = textbox(cx + 250, by + 130, "Ефективна площа\nрозсіювання ×10..30", size=9, bold=True,
                            fill="#fffbeb", stroke="#d97706", color="#b45309", pad=4)
    frags.append(t_lat_r)

    # Напис на GND екрані
    t_gnd, _, _ = textbox(cx, by + 130, "Внутрішній мідний шар GND (L2) — тепловий розсіювач", size=10, bold=True,
                          fill="#fef3c7", stroke="#b45309", color="#78350f", pad=4)
    frags.append(t_gnd)

    # Блок підсумкових висновків внизу
    t_summary, _, _ = textbox(w / 2, 495,
                              "Тепловий баланс: 60–80% тепла від доріжки розсіюється крізь діелектрик у внутрішні мідні полігони,\n"
                              "і лише 20–40% віддається безпосередньо конвекцією та випромінюванням з поверхні в повітря.",
                              size=11, bold=True, fill="#f8fafc", stroke="#94a3b8", color="#1e293b", pad=8)
    frags.append(t_summary)

    # Розмірні виноски для ширини W
    frags.append(line(track_x, track_y + track_h + 8, track_x + track_w, track_y + track_h + 8, color="#475569", sw=1.0))
    frags.append(line(track_x, track_y + track_h + 4, track_x, track_y + track_h + 12, color="#475569", sw=1.0))
    frags.append(line(track_x + track_w, track_y + track_h + 4, track_x + track_w, track_y + track_h + 12, color="#475569", sw=1.0))
    frags.append(text(cx, track_y + track_h + 22, "Ширина W", size=10, bold=True, color="#334155", anchor="middle"))

    out_path = os.path.join(IMG_DIR, "trace-thermal-profile.svg")
    render(out_path, w, h, *frags)
    print("Rendered:", out_path)


if __name__ == "__main__":
    draw_current_vs_area_dt()
    draw_trace_thermal_profile()
