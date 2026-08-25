# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, line, arrow, rect, circle, fitbox, textbox,
    INK, MUTED, FIELD, POS, NEG, BG, FILL, LINE
)

# Створюємо теку img/, якщо її немає
img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# Фігура 1: Кут магнітного схилення (magnetic-vs-geographic-north.svg)
# -----------------------------------------------------------------------------
def gen_magnetic_vs_geographic_north():
    w, h = 720, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Геометрія магнітного схилення D", size=17, bold=True))
    
    ox, oy = 240, 250
    radius = 165
    
    # Коло компаса / горизонту
    frags.append(circle(ox, oy, radius, fill="none", stroke=MUTED, sw=1.5))
    
    # Географічний меридіан (True North - прямо вгору)
    frags.append(line(ox, oy + radius + 15, ox, oy - radius - 25, color=MUTED, sw=1.5, dash="6,3"))
    frags.append(arrow(ox, oy, ox, oy - radius - 20, color=INK, sw=2.5))
    frags.append(text(ox, oy - radius - 32, "N_geo (Географічна північ)", size=12, bold=True, color=INK))
    
    # Географічна паралель (Схід - Захід)
    frags.append(line(ox - radius - 15, oy, ox + radius + 15, oy, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(ox + radius + 25, oy + 4, "E", size=12, color=MUTED))
    frags.append(text(ox - radius - 25, oy + 4, "W", size=12, color=MUTED))
    frags.append(text(ox, oy + radius + 25, "S", size=12, color=MUTED))
    
    # Магнітний меридіан (N_mag під кутом D = +18° Східного схилення)
    d_deg = 18.0
    d_rad = math.radians(d_deg)
    
    mag_nx = ox + (radius + 20) * math.sin(d_rad)
    mag_ny = oy - (radius + 20) * math.cos(d_rad)
    
    frags.append(line(ox - radius * math.sin(d_rad), oy + radius * math.cos(d_rad), mag_nx, mag_ny, color=FIELD, sw=1.5, dash="6,3"))
    frags.append(arrow(ox, oy, mag_nx - 5 * math.sin(d_rad), mag_ny + 5 * math.cos(d_rad), color=FIELD, sw=2.5))
    frags.append(text(mag_nx + 20, mag_ny - 5, "N_mag (Магнітна північ)", size=12, bold=True, color=FIELD))
    
    # Дуга схилення D
    arc_r = 105
    arc_steps = 15
    for i in range(arc_steps):
        a1 = math.radians(-90 + i * (d_deg / arc_steps))
        a2 = math.radians(-90 + (i + 1) * (d_deg / arc_steps))
        x1 = ox + arc_r * math.cos(a1)
        y1 = oy + arc_r * math.sin(a1)
        x2 = ox + arc_r * math.cos(a2)
        y2 = oy + arc_r * math.sin(a2)
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2))
    
    arc_mid_a = math.radians(-90 + d_deg / 2)
    frags.append(text(ox + (arc_r + 30) * math.cos(arc_mid_a), oy + (arc_r + 30) * math.sin(arc_mid_a), "D (> 0, Східне)", size=12, bold=True, color=POS))
    
    # Компасна стрілка вздовж N_mag
    needle_l = 90
    n_x = ox + needle_l * math.sin(d_rad)
    n_y = oy - needle_l * math.cos(d_rad)
    s_x = ox - needle_l * math.sin(d_rad)
    s_y = oy + needle_l * math.cos(d_rad)
    
    # Половина N (червона/POS)
    frags.append(line(ox, oy, n_x, n_y, color=POS, sw=5))
    # Половина S (синя/NEG)
    frags.append(line(ox, oy, s_x, s_y, color=NEG, sw=5))
    frags.append(circle(ox, oy, 6, fill=INK, stroke="none", sw=0))
    
    # Панель пояснень праворуч
    px, py = 460, 70
    pw, ph = 240, 370
    frags.append(fitbox(px, py, pw, 35, "Векторні компоненти", size=13, bold=True, color=INK))
    
    info_text = (
        "• N_geo: Напрям на географічний Північний полюс (осі обертання Землі).\n\n"
        "• N_mag: Напрям вектора H (горизонтальної індукції поля Землі).\n\n"
        "• D (Declination): Кут від N_geo до N_mag у горизонтальній площині.\n\n"
        "• D > 0 (Східне / East): N_mag відхилена на схід від N_geo.\n\n"
        "• D < 0 (Західне / West): N_mag відхилена на захід від N_geo."
    )
    frags.append(fitbox(px, py + 45, pw, ph - 45, info_text, size=11, color=INK))
    
    render(os.path.join(img_dir, "magnetic-vs-geographic-north.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 2: Принцип ізогонічної карти та дрейф (isogonic-map-principle.svg)
# -----------------------------------------------------------------------------
def gen_isogonic_map_principle():
    w, h = 720, 450
    frags = []
    
    frags.append(text(w / 2, 25, "Ізогонічні лінії та секулярний дрейф агонічної лінії", size=17, bold=True))
    
    # Карта схематична (прямокутник)
    mx, my = 40, 60
    mw, mh = 410, 350
    frags.append(rect(mx, my, mw, mh, fill=FILL, stroke=LINE, rx=6))
    
    # Географічна сітка
    for x in range(mx + 70, mx + mw, 70):
        frags.append(line(x, my, x, my + mh, color=MUTED, sw=0.8, dash="2,4"))
    for y in range(my + 70, my + mh, 70):
        frags.append(line(mx, y, mx + mw, y, color=MUTED, sw=0.8, dash="2,4"))
        
    # Географічний та Магнітний полюси
    g_px, g_py = mx + 200, my + 50
    m_px, m_py = mx + 260, my + 70
    
    frags.append(circle(g_px, g_py, 6, fill=INK, stroke="none", sw=0))
    frags.append(text(g_px - 10, g_py - 12, "Географічний полюс", size=11, bold=True, color=INK))
    
    frags.append(circle(m_px, m_py, 6, fill=POS, stroke="none", sw=0))
    frags.append(text(m_px + 10, m_py - 5, "Магнітний полюс", size=11, bold=True, color=POS))
    
    # Агонічна лінія (D = 0°) — нульове схилення
    agonic_pts = [(mx + 110, my + mh), (mx + 160, my + 240), (mx + 200, my + 150), (g_px, g_py)]
    for i in range(len(agonic_pts) - 1):
        x1, y1 = agonic_pts[i]
        x2, y2 = agonic_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=INK, sw=2.5))
    frags.append(text(mx + 175, my + 260, "Агонічна лінія (D = 0°)", size=11, bold=True, color=INK, anchor="start"))
    
    # Східні ізогони (D = +5°, +10°) — праворуч від агонічної
    iso_e1 = [(mx + 190, my + mh), (mx + 240, my + 240), (mx + 270, my + 150), (m_px, m_py)]
    for i in range(len(iso_e1) - 1):
        frags.append(line(iso_e1[i][0], iso_e1[i][1], iso_e1[i+1][0], iso_e1[i+1][1], color=POS, sw=1.5, dash="6,3"))
    frags.append(text(mx + 280, my + 295, "D = +5° E", size=10, bold=True, color=POS, anchor="start"))
    
    iso_e2 = [(mx + 270, my + mh), (mx + 320, my + 240), (mx + 340, my + 150), (m_px + 40, m_py + 20)]
    for i in range(len(iso_e2) - 1):
        frags.append(line(iso_e2[i][0], iso_e2[i][1], iso_e2[i+1][0], iso_e2[i+1][1], color=POS, sw=1.5, dash="6,3"))
    frags.append(text(mx + 350, my + 295, "D = +10° E", size=10, bold=True, color=POS, anchor="start"))

    # Західні ізогони (D = -5°, -10°) — ліворуч від агонічної
    iso_w1 = [(mx + 50, my + mh), (mx + 90, my + 240), (mx + 130, my + 150), (g_px - 60, g_py + 20)]
    for i in range(len(iso_w1) - 1):
        frags.append(line(iso_w1[i][0], iso_w1[i][1], iso_w1[i+1][0], iso_w1[i+1][1], color=NEG, sw=1.5, dash="6,3"))
    frags.append(text(mx + 15, my + 215, "D = -5° W", size=10, bold=True, color=NEG, anchor="start"))
    
    # Секулярний дрейф — стрілка зсуву агонічної лінії за 100 років
    frags.append(arrow(mx + 160, my + 200, mx + 195, my + 195, color=FIELD, sw=2))
    frags.append(text(mx + 130, my + 185, "Дрейф за 100 років", size=10, bold=True, color=FIELD))
    
    # Панель з описом праворуч
    px, py = 475, 60
    pw, ph = 225, 350
    frags.append(fitbox(px, py, pw, 35, "Термінологія карт", size=13, bold=True, color=INK))
    
    descr = (
        "• Ізогона (Isogon): лінія на карті, що з'єднує точки з однаковим магнітним схиленням D.\n\n"
        "• Агонічна лінія (Agonic line): ізогона з D = 0°. У її точках компас показує точно на географічну північ.\n\n"
        "• Секулярний дрейф: повільне зміщення ізогон (на 0.05°–0.2° на рік) через гідродинамічні струми в рідкому ядрі Землі.\n\n"
        "• Моделі WMM/IGRF: поновлюють коефіцієнти ізогон кожні 5 років."
    )
    frags.append(fitbox(px, py + 45, pw, ph - 45, descr, size=11, color=INK))
    
    render(os.path.join(img_dir, "isogonic-map-principle.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 3: Розрахунок навігаційного курсу (compass-declination-correction.svg)
# -----------------------------------------------------------------------------
def gen_compass_declination_correction():
    w, h = 720, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Переведення магнітного курсу в істинний географічний", size=17, bold=True))
    
    cx, cy = 235, 260
    r = 155
    
    # Шкала компаса
    frags.append(circle(cx, cy, r, fill=FILL, stroke=LINE, sw=2))
    
    # Поділки шкали через 30 градусів
    for deg in range(0, 360, 30):
        rad = math.radians(deg - 90)
        x1 = cx + (r - 12) * math.cos(rad)
        y1 = cy + (r - 12) * math.sin(rad)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color=MUTED, sw=1.5))
        
        # Написи градусів
        lbl_r = r - 25
        lx = cx + lbl_r * math.cos(rad)
        ly = cy + lbl_r * math.sin(rad) + 4
        frags.append(text(lx, ly, f"{deg}°", size=10, color=MUTED))
    
    # Справжня північ N_geo (0°)
    frags.append(line(cx, cy, cx, cy - r - 20, color=INK, sw=2, dash="4,4"))
    frags.append(arrow(cx, cy, cx, cy - r - 15, color=INK, sw=2.5))
    frags.append(text(cx, cy - r - 28, "N_geo (0° Істинна північ)", size=12, bold=True, color=INK))
    
    # Магнітна північ N_mag (при D = +12° Східне)
    d_val = 12.0
    d_rad = math.radians(d_val - 90)
    mx = cx + (r + 20) * math.cos(d_rad)
    my = cy + (r + 20) * math.sin(d_rad)
    frags.append(line(cx, cy, mx, my, color=POS, sw=2, dash="4,4"))
    frags.append(arrow(cx, cy, mx, my, color=POS, sw=2.5))
    frags.append(text(mx + 15, my - 5, "N_mag (+12° Схилення D)", size=12, bold=True, color=POS))
    
    # Вектор напряму руху судна / дрона (Heading vector: Ψ_mag = 45° від N_mag)
    psi_mag = 45.0
    psi_true = psi_mag + d_val  # 57° від N_geo
    
    heading_rad = math.radians(psi_true - 90)
    hx = cx + (r - 10) * math.cos(heading_rad)
    hy = cy + (r - 10) * math.sin(heading_rad)
    
    frags.append(line(cx, cy, hx, hy, color=FIELD, sw=3))
    frags.append(arrow(cx, cy, hx, hy, color=FIELD, sw=3))
    frags.append(text(hx + 15, hy + 5, "Курс апарата", size=12, bold=True, color=FIELD))
    
    # Дуга магнітного курсу (від N_mag до Heading = 45°)
    arc_m_r = 80
    arc_m_steps = 15
    for i in range(arc_m_steps):
        a1 = math.radians((d_val - 90) + i * (psi_mag / arc_m_steps))
        a2 = math.radians((d_val - 90) + (i + 1) * (psi_mag / arc_m_steps))
        frags.append(line(cx + arc_m_r * math.cos(a1), cy + arc_m_r * math.sin(a1), cx + arc_m_r * math.cos(a2), cy + arc_m_r * math.sin(a2), color=POS, sw=1.5))
    frags.append(text(cx + 60, cy - 35, "Ψ_mag = 45°", size=11, bold=True, color=POS))
    
    # Дуга істинного курсу (від N_geo до Heading = 57°)
    arc_t_r = 125
    arc_t_steps = 15
    for i in range(arc_t_steps):
        a1 = math.radians(-90 + i * (psi_true / arc_t_steps))
        a2 = math.radians(-90 + (i + 1) * (psi_true / arc_t_steps))
        frags.append(line(cx + arc_t_r * math.cos(a1), cy + arc_t_r * math.sin(a1), cx + arc_t_r * math.cos(a2), cy + arc_t_r * math.sin(a2), color=INK, sw=1.5, dash="3,2"))
    frags.append(text(cx + 120, cy - 100, "Ψ_true = 57°", size=11, bold=True, color=INK))
    
    # Розрахункова панель праворуч
    px, py = 455, 70
    pw, ph = 245, 350
    frags.append(fitbox(px, py, pw, 35, "Навігаційне рівняння", size=13, bold=True, color=INK))
    
    eq_box = (
        "Формула зв'язку:\n"
        "  Ψ_true = Ψ_mag + D\n\n"
        "Приклад розрахунку:\n"
        "  Магнітний курс (Ψ_mag) = 45°\n"
        "  Схилення (D) = +12° (Східне)\n"
        "  -----------------------------\n"
        "  Істинний курс = 45° + 12° = 57°\n\n"
        "Західне схилення (D < 0):\n"
        "  Якщо D = -8° (Західне),\n"
        "  Істинний курс = 45° + (-8°) = 37°\n\n"
        "Нормалізація в [0°, 360°):\n"
        "  Ψ_true = (Ψ_mag + D + 360°) % 360°"
    )
    frags.append(fitbox(px, py + 45, pw, ph - 45, eq_box, size=11, color=INK))
    
    render(os.path.join(img_dir, "isogonic-map-principle.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Головний викликовий блок
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    gen_magnetic_vs_geographic_north()
    gen_isogonic_map_principle()
    gen_compass_declination_correction()
    print("Успішно згенеровано 3 SVG-фігури в ./img/")
