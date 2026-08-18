# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика матеріалів зі зміною фазового стану (PCM)».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"
GRID_COLOR = "#e2e8f0"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Аморфна vs кристалічна фаза халкогеніду (GST) ────────────────────
def fig_pcm_phase_structure():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Структурний та фізичний контраст фаз халкогеніду GST (Ge₂Sb₂Te₅)", size=16, bold=True, color=INK))

    p_w, p_h = 350, 320
    y0 = 48

    # Ліва панель: Аморфний стан
    x_left = 20
    f.append(rect(x_left, y0, p_w, p_h, fill="#fff1f2", stroke="#f43f5e", rx=8, sw=1.5))
    f.append(text(x_left + p_w / 2, y0 + 24, "Аморфний стан (RESET / HIGH-Z)", size=14, bold=True, color="#be123c"))

    # Атоми аморфного стану (безладова сітка)
    amo_coords = [
        (60, 110, "Te", "#e11d48", 9), (110, 95, "Ge", "#0284c7", 7), (160, 120, "Sb", "#d97706", 8),
        (210, 100, "Te", "#e11d48", 9), (270, 115, "Ge", "#0284c7", 7), (320, 95, "Te", "#e11d48", 9),
        (80, 160, "Sb", "#d97706", 8), (135, 150, "Te", "#e11d48", 9), (190, 165, "Ge", "#0284c7", 7),
        (245, 155, "Te", "#e11d48", 9), (295, 160, "Sb", "#d97706", 8), (65, 215, "Ge", "#0284c7", 7),
        (115, 205, "Te", "#e11d48", 9), (175, 210, "Sb", "#d97706", 8), (230, 200, "Te", "#e11d48", 9),
        (280, 215, "Ge", "#0284c7", 7), (325, 200, "Te", "#e11d48", 9)
    ]
    # Зв'язки між близькими атомами
    for i in range(len(amo_coords)):
        for j in range(i + 1, len(amo_coords)):
            x1, y1 = amo_coords[i][0] + x_left, amo_coords[i][1]
            x2, y2 = amo_coords[j][0] + x_left, amo_coords[j][1]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < 62:
                f.append(line(x1, y1, x2, y2, color="#fda4af", sw=1.5))
    for ac in amo_coords:
        cx, cy = ac[0] + x_left, ac[1]
        f.append(circle(cx, cy, ac[4], fill=ac[3], stroke="#ffffff", sw=1))

    # Текстовий блок характеристик аморфного стану
    f.append(line(x_left + 15, y0 + 230, x_left + p_w - 15, y0 + 230, color="#fecdd3", sw=1))
    f.append(text(x_left + 20, y0 + 248, "• Порядок: Короткий (ковалентні зв'язки)", size=11, bold=True, color=INK))
    f.append(text(x_left + 20, y0 + 266, "• Германій: Тетраедричне оточення (4-коорд.)", size=11, color=INK))
    f.append(text(x_left + 20, y0 + 284, "• Питомий опір: ρ ≈ 10² – 10⁴ Ом·см (Високий)", size=11, bold=True, color="#be123c"))
    f.append(text(x_left + 20, y0 + 302, "• Оптичне відбиття: R ≈ 40% (Низьке)", size=11, color=INK))

    # Права панель: Кристалічний стан
    x_right = 410
    f.append(rect(x_right, y0, p_w, p_h, fill="#eff6ff", stroke="#2563eb", rx=8, sw=1.5))
    f.append(text(x_right + p_w / 2, y0 + 24, "Кристалічний стан (SET / LOW-Z)", size=14, bold=True, color="#1e40af"))

    # Регулярна гратка кристала (fcc rock-salt з вакансіями)
    rows_c, cols_c = 3, 5
    dx_c, dy_c = 55, 50
    ox_c, oy_c = x_right + 65, y0 + 95
    for r in range(rows_c):
        for c in range(cols_c):
            cx = ox_c + c * dx_c
            cy = oy_c + r * dy_c
            if c < cols_c - 1:
                f.append(line(cx, cy, cx + dx_c, cy, color="#93c5fd", sw=2))
            if r < rows_c - 1:
                f.append(line(cx, cy, cx, cy + dy_c, color="#93c5fd", sw=2))
            
            # Атоми за підґратками: Телурій на одній, Ge/Sb/Вакансії на іншій
            if (r + c) % 2 == 0:
                f.append(circle(cx, cy, 9, fill="#e11d48", stroke="#ffffff", sw=1.5)) # Te
            else:
                if (r * 3 + c) % 5 == 0:
                    # Вакансія на підґратці
                    f.append(path_svg(f"M {cx-7},{cy} A 7,7 0 1,0 {cx+7},{cy} A 7,7 0 1,0 {cx-7},{cy}", fill="none", stroke="#64748b", sw=1.5, dash="2,2"))
                elif (r + c) % 4 == 1:
                    f.append(circle(cx, cy, 7, fill="#0284c7", stroke="#ffffff", sw=1.5)) # Ge
                else:
                    f.append(circle(cx, cy, 8, fill="#d97706", stroke="#ffffff", sw=1.5)) # Sb

    # Текстовий блок характеристик кристалічного стану
    f.append(line(x_right + 15, y0 + 230, x_right + p_w - 15, y0 + 230, color="#bfdbfe", sw=1))
    f.append(text(x_right + 20, y0 + 248, "• Порядок: Дальній (метастібільна NaCl-гратка)", size=11, bold=True, color=INK))
    f.append(text(x_right + 20, y0 + 266, "• Германій: Октаедричне оточення (6-коорд.)", size=11, color=INK))
    f.append(text(x_right + 20, y0 + 284, "• Питомий опір: ρ ≈ 10⁻³ – 10⁻² Ом·см (Низький)", size=11, bold=True, color="#1e40af"))
    f.append(text(x_right + 20, y0 + 302, "• Оптичне відбиття: R ≈ 65% (Високе, ΔR/R ~ 30%)", size=11, color=INK))

    # Легенда елементів між панелями зверху
    f.append(circle(W / 2 - 110, H - 20, 6, fill="#e11d48", stroke="none"))
    f.append(text(W / 2 - 98, H - 16, "Te", size=11, bold=True, color=INK))
    f.append(circle(W / 2 - 40, H - 20, 5, fill="#0284c7", stroke="none"))
    f.append(text(W / 2 - 30, H - 16, "Ge", size=11, bold=True, color=INK))
    f.append(circle(W / 2 + 30, H - 20, 6, fill="#d97706", stroke="none"))
    f.append(text(W / 2 + 40, H - 16, "Sb", size=11, bold=True, color=INK))
    f.append(path_svg(f"M {W/2+90-5},{H-20} A 5,5 0 1,0 {W/2+90+5},{H-20} A 5,5 0 1,0 {W/2+90-5},{H-20}", fill="none", stroke="#64748b", sw=1.5, dash="2,2"))
    f.append(text(W / 2 + 100, H - 16, "Вакансія", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, 'pcm-phase-structure.svg'), W, H, "\n".join(f))

# ── Фігура 2: Оптики імпульсів SET/RESET та TTT-діаграма ─────────────────────
def fig_pcm_pulse_dynamics():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 25, "Температурно-часові імпульси SET/RESET та TTT-діаграма кристалізації", size=16, bold=True, color=INK))

    # Лівий графік: Профіль T(t) для RESET і SET
    gx1, gy1, gw1, gh1 = 65, 65, 300, 310
    f.append(rect(gx1, gy1, gw1, gh1, fill="#f8fafc", stroke=GRID_COLOR, rx=4))

    # Осі
    f.append(arrow(gx1 + 30, gy1 + gh1 - 30, gx1 + gw1 - 10, gy1 + gh1 - 30, color=INK, sw=1.5)) # t
    f.append(arrow(gx1 + 30, gy1 + gh1 - 30, gx1 + 30, gy1 + 10, color=INK, sw=1.5)) # T
    f.append(text(gx1 + gw1 - 25, gy1 + gh1 - 10, "Час t (нс)", size=11, color=INK))
    f.append(text(gx1 + 10, gy1 + 20, "Т (°C)", size=11, color=INK))

    # Горизонтальні лінії темп. плавлення T_m та склування T_g
    y_tm = gy1 + gh1 - 30 - 220 # ~ 600 °C
    y_tc = gy1 + gh1 - 30 - 130 # ~ 350 °C (T_c peak)
    y_tg = gy1 + gh1 - 30 - 60  # ~ 200 °C
    f.append(line(gx1 + 30, y_tm, gx1 + gw1 - 20, y_tm, color="#dc2626", sw=1, dash="4,4"))
    f.append(text(gx1 + 33, y_tm - 6, "T_m (Плавлення ~600°C)", size=10, color="#dc2626"))
    f.append(line(gx1 + 30, y_tg, gx1 + gw1 - 20, y_tg, color="#d97706", sw=1, dash="4,4"))
    f.append(text(gx1 + 33, y_tg - 6, "T_g (Склування ~200°C)", size=10, color="#d97706"))

    # Крива RESET: Короткий високий нагрів + гасіння (Quenching)
    p_reset = f"M {gx1+30},{gy1+gh1-30} L {gx1+50},{y_tm-25} L {gx1+70},{y_tm-25} L {gx1+85},{gy1+gh1-30}"
    f.append(path_svg(p_reset, stroke="#dc2626", sw=2.5))
    f.append(text(gx1 + 65, y_tm - 35, "RESET (Аморфізація)", size=11, bold=True, color="#dc2626"))
    f.append(text(gx1 + 95, gy1 + gh1 - 100, "Гасіння >10⁹ K/c", size=10, italic=True, color="#b91c1c"))

    # Крива SET: Тривалий помірний нагрів у вікні кристалізації
    p_set = f"M {gx1+30},{gy1+gh1-30} L {gx1+60},{y_tc} L {gx1+230},{y_tc} L {gx1+260},{gy1+gh1-30}"
    f.append(path_svg(p_set, stroke="#2563eb", sw=2.5))
    f.append(text(gx1 + 140, y_tc - 10, "SET (Кристалізація)", size=11, bold=True, color="#2563eb"))

    # Правий графік: Діаграма TTT (Temperature-Time-Transformation)
    gx2, gy2, gw2, gh2 = 430, 65, 310, 310
    f.append(rect(gx2, gy2, gw2, gh2, fill="#f8fafc", stroke=GRID_COLOR, rx=4))

    # Осі TTT
    f.append(arrow(gx2 + 35, gy2 + gh2 - 30, gx2 + gw2 - 10, gy2 + gh2 - 30, color=INK, sw=1.5)) # log t
    f.append(arrow(gx2 + 35, gy2 + gh2 - 30, gx2 + 35, gy2 + 10, color=INK, sw=1.5)) # T
    f.append(text(gx2 + gw2 - 60, gy2 + gh2 - 10, "log(t)", size=11, color=INK))
    f.append(text(gx2 + 10, gy2 + 20, "Т (°C)", size=11, color=INK))

    y2_tm = gy2 + gh2 - 30 - 220
    y2_tg = gy2 + gh2 - 30 - 60
    f.append(line(gx2 + 35, y2_tm, gx2 + gw2 - 20, y2_tm, color="#dc2626", sw=1, dash="4,4"))
    f.append(text(gx2 + 40, y2_tm - 6, "T_m", size=10, color="#dc2626"))
    f.append(line(gx2 + 35, y2_tg, gx2 + gw2 - 20, y2_tg, color="#d97706", sw=1, dash="4,4"))
    f.append(text(gx2 + 40, y2_tg - 6, "T_g", size=10, color="#d97706"))

    # Крива C-подібного "носа" TTT (Crystallization Nose)
    p_ttt_start = f"M {gx2+260},{y2_tm-10} C {gx2+110},{y2_tm+30} {gx2+110},{y2_tg+30} {gx2+260},{y2_tg-10}"
    p_ttt_end   = f"M {gx2+285},{y2_tm-10} C {gx2+150},{y2_tm+30} {gx2+150},{y2_tg+30} {gx2+285},{y2_tg-10}"
    f.append(path_svg(p_ttt_start, stroke="#059669", sw=2, dash="3,3"))
    f.append(path_svg(p_ttt_end, stroke="#059669", sw=2))

    # Точка "носа" (мінімальний час кристалізації t_min)
    f.append(circle(gx2 + 125, gy2 + gh2 - 30 - 140, 5, fill="#059669", stroke="#ffffff", sw=1))
    f.append(line(gx2 + 35, gy2 + gh2 - 30 - 140, gx2 + 125, gy2 + gh2 - 30 - 140, color="#059669", sw=1, dash="2,2"))
    f.append(text(gx2 + 135, gy2 + gh2 - 30 - 142, "Носик C-кривої (t_min)", size=10, bold=True, color="#059669"))
    f.append(text(gx2 + 175, gy2 + gh2 - 30 - 80, "Кристалічна фаза (X = 1)", size=11, bold=True, color="#047857"))
    f.append(text(gx2 + 50, gy2 + gh2 - 30 - 170, "Аморфна фаза", size=11, bold=True, color="#be123c"))

    # Текст унизу
    f.append(text(W / 2, H - 12, "Швидкість охолодження під час RESET повинна оминати 'ніс' TTT-кривої для запобігання кристалізації", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'pcm-pulse-dynamics.svg'), W, H, "\n".join(f))

# ── Фігура 3: Будова Mushroom Cell комірки PCRAM ──────────────────────────────
def fig_pcm_mushroom_cell_structure():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 25, "Геометрична будова та фазовий купол осередку Mushroom Cell (PCRAM)", size=16, bold=True, color=INK))

    cx = W / 2
    y0 = 60

    # Верхній електрод (Top Electrode - TE / W)
    f.append(rect(cx - 180, y0, 360, 40, fill="#cbd5e1", stroke="#475569", rx=4, sw=1.5))
    f.append(text(cx, y0 + 24, "Верхній електрод (Top Electrode: W / TiN)", size=12, bold=True, color="#1e293b"))

    # Масив халкогеніду GST (кристалічна матриця)
    gst_y = y0 + 40
    gst_h = 140
    f.append(rect(cx - 180, gst_y, 360, gst_h, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    f.append(text(cx - 110, gst_y + 30, "Кристалічний шар GST (Низький опір)", size=11, bold=True, color="#1e40af"))

    # Аморфна зона / купол (Programmable Active Volume / Melted Dome)
    dome_path = f"M {cx - 70},{gst_y + gst_h} A 70,65 0 0,1 {cx + 70},{gst_y + gst_h} Z"
    f.append(path_svg(dome_path, fill="#ffe4e6", stroke="#e11d48", sw=2))
    f.append(text(cx, gst_y + gst_h - 28, "Аморфна зона", size=12, bold=True, color="#be123c"))
    f.append(text(cx, gst_y + gst_h - 12, "(Active RESET Dome)", size=10, color="#be123c"))

    # Нижній електрод / Нагрівач (Heater plug / TiN)
    heater_w = 40
    heater_h = 80
    heater_y = gst_y + gst_h
    f.append(rect(cx - heater_w/2, heater_y, heater_w, heater_h, fill="#f97316", stroke="#c2410c", sw=1.5))
    f.append(text(cx + 85, heater_y + 42, "Нагрівач (Heater Plug: TiN)", size=11, bold=True, color="#c2410c"))
    f.append(arrow(cx + 25, heater_y + 40, cx + 5, heater_y + 40, color="#c2410c", sw=1.5))

    # Диелектрична ізоляція навколо нагрівача (SiO2 / SiN)
    f.append(rect(cx - 180, heater_y, 180 - heater_w/2, heater_h, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    f.append(rect(cx + heater_w/2, heater_y, 180 - heater_w/2, heater_h, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    f.append(text(cx - 110, heater_y + 42, "Діелектрик (SiO₂/SiN)", size=11, color="#64748b"))

    # Нижній контакт / Лінія вибору (Bottom Contact / Word Line)
    bc_y = heater_y + heater_h
    f.append(rect(cx - 180, bc_y, 360, 40, fill="#cbd5e1", stroke="#475569", rx=4, sw=1.5))
    f.append(text(cx, bc_y + 24, "Нижній контакт / Селектор (Wordline / 1T Selector)", size=12, bold=True, color="#1e293b"))

    # Позначення гарячої точки (Hotspot)
    f.append(circle(cx, heater_y, 6, fill="#facc15", stroke="#dc2626", sw=1.5))
    f.append(text(cx + 120, heater_y - 8, "Гаряча точка (Hotspot)", size=10, bold=True, color="#dc2626"))
    f.append(arrow(cx + 70, heater_y - 8, cx + 10, heater_y - 2, color="#dc2626", sw=1.5))

    render(os.path.join(IMG_DIR, 'pcm-mushroom-cell-structure.svg'), W, H, "\n".join(f))

# ── Фігура 4: Вольт-амперна характеристика та порогове перемикання ────────────
def fig_pcm_threshold_switching():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 25, "Вольт-амперна характеристика та ефект порогового перемикання (Ovshinsky Switching)", size=16, bold=True, color=INK))

    gx, gy, gw, gh = 90, 55, 580, 300
    f.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke=GRID_COLOR, rx=4))

    # Осі I-V
    f.append(arrow(gx + 30, gy + gh - 30, gx + gw - 20, gy + gh - 30, color=INK, sw=1.5)) # V
    f.append(arrow(gx + 30, gy + gh - 30, gx + 30, gy + 15, color=INK, sw=1.5)) # I (log)
    f.append(text(gx + gw - 40, gy + gh - 10, "Напруга V (В)", size=11, color=INK))
    f.append(text(gx + 10, gy + 25, "Струм I (лог)", size=11, color=INK))

    # Лінія V_th (Порогова напруга)
    v_th_x = gx + 360
    f.append(line(v_th_x, gy + 20, v_th_x, gy + gh - 30, color="#dc2626", sw=1, dash="4,4"))
    f.append(text(v_th_x, gy + 15, "V_th (Порогова напруга)", size=10, bold=True, color="#dc2626"))

    # Лінія V_hold (Напруга утримання)
    v_h_x = gx + 160
    f.append(line(v_h_x, gy + 120, v_h_x, gy + gh - 30, color="#d97706", sw=1, dash="4,4"))
    f.append(text(v_h_x - 5, gy + gh - 15, "V_hold", size=10, color="#d97706"))

    # 1. Низькопровідний OFF-стан (до V_th)
    p_off = f"M {gx+30},{gy+gh-30} C {gx+150},{gy+gh-40} {gx+300},{gy+gh-55} {v_th_x},{gy+gh-90}"
    f.append(path_svg(p_off, stroke="#be123c", sw=2.5))
    f.append(text(gx + 260, gy + gh - 38, "Аморфний OFF-стан (High-Z)", size=11, bold=True, color="#be123c"))

    # 2. Негативний диференціальний опір / Стрибок (Threshold snapback)
    p_snap = f"M {v_th_x},{gy+gh-90} L {v_h_x},{gy+140}"
    f.append(path_svg(p_snap, stroke="#dc2626", sw=2, dash="3,3"))
    f.append(text(v_th_x - 110, gy + 105, "S-подібний пробій (Ovshinsky)", size=10, bold=True, color="#dc2626"))

    # 3. Високопровідний ON-стан
    p_on_amo = f"M {v_h_x},{gy+140} L {gx+460},{gy+35}"
    f.append(path_svg(p_on_amo, stroke="#2563eb", sw=2.5))
    f.append(text(gx + 340, gy + 45, "Високопровідний ON-стан (філамент)", size=11, bold=True, color="#2563eb"))

    # 4. Крива Кристалічного стану (SET Low-Z state)
    p_cry = f"M {gx+30},{gy+gh-30} L {gx+420},{gy+35}"
    f.append(path_svg(p_cry, stroke="#15803d", sw=2.5))
    f.append(text(gx + 120, gy + 110, "Кристалічний стан SET (Low-Z)", size=11, bold=True, color="#15803d"))

    # Область зчитування (Read window)
    f.append(rect(gx + 60, gy + gh - 140, 80, 100, fill="#fef08a", stroke="#ca8a04", rx=3, sw=1))
    f.append(text(gx + 100, gy + gh - 45, "Вікно зчитування", size=9, bold=True, color="#854d0e"))

    render(os.path.join(IMG_DIR, 'pcm-threshold-switching.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_pcm_phase_structure()
    fig_pcm_pulse_dynamics()
    fig_pcm_mushroom_cell_structure()
    fig_pcm_threshold_switching()
    print("Успішно згенеровано фігури PCM у ./img/")
