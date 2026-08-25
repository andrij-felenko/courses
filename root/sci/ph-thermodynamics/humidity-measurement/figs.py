# -*- coding: utf-8 -*-
"""Фігури для теми «Вимірювання вологості» (book/physics/thermal-statistical/humidity-measurement)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
RED_F, RED_S = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S = "#f8fafc", "#475569"

def polyline(pts, color="#333333", sw=1.5, fill="none"):
    pts_str = " ".join("%g,%g" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, color, sw)

def fig_sensor_principles():
    """sensor-principles.svg: Три принципи вимірювання вологості (психрометричний, конденсаційний, сорбційно-ємнісний)."""
    W, H = 880, 440
    frags = []

    # Загальне тло
    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Фізичні принципи вимірювання вологості повітря", size=16, bold=True, color="#1e293b"))

    # Блок 1: Психрометр (лівий)
    frags.append(rect(25, 55, 265, 360, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(157, 78, "Психрометричний метод", size=13, bold=True, color=BLUE_S))

    # Сухий термометр
    frags.append(rect(65, 110, 14, 180, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=7))
    frags.append(circle(72, 300, 14, fill=RED_S, stroke="#b91c1c", sw=1.5))
    frags.append(line(72, 120, 72, 300, color=RED_S, sw=3))
    frags.append(text(72, 100, "T", size=12, bold=True, color=RED_S))
    frags.append(text(72, 330, "Сухий", size=11, color="#334155"))

    # Вологий термометр з ґнотом
    frags.append(rect(215, 110, 14, 180, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=7))
    frags.append(circle(222, 300, 14, fill=BLUE_S, stroke="#1d4ed8", sw=1.5))
    frags.append(line(222, 160, 222, 300, color=RED_S, sw=3))
    frags.append(text(222, 100, "T_w", size=12, bold=True, color=BLUE_S))
    frags.append(text(222, 330, "Вологий", size=11, color="#334155"))

    # Вологий ґніт (тканина) навколо резервуара
    frags.append(rect(204, 282, 36, 36, fill="#dbeafe", stroke=BLUE_S, sw=1.5, rx=4))
    frags.append(rect(208, 318, 28, 30, fill="#bfdbfe", stroke=BLUE_S, sw=1))
    frags.append(text(222, 360, "Вологий ґніт", size=10, color=BLUE_S))

    # Потік повітря та випаровування
    frags.append(line(125, 200, 180, 200, color="#0284c7", sw=2))
    frags.append(line(170, 194, 180, 200, color="#0284c7", sw=2))
    frags.append(line(170, 206, 180, 200, color="#0284c7", sw=2))
    frags.append(text(147, 190, "v > 2.5 м/с", size=10, color="#0284c7"))
    frags.append(text(157, 395, "Охолодження випаровуванням: T_w < T", size=10, italic=True, color="#475569"))

    # Блок 2: Охолоджуване дзеркало (середній)
    frags.append(rect(307, 55, 265, 360, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(439, 78, "Конденсаційне дзеркало", size=13, bold=True, color=GREEN_S))

    # Корпус та дзеркало
    frags.append(rect(347, 210, 184, 16, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    frags.append(rect(377, 204, 124, 6, fill="#f8fafc", stroke="#0284c7", sw=1.5)) # поліроване дзеркало
    frags.append(text(439, 195, "Поліроване дзеркало", size=10, color="#0284c7"))

    # Краплі роси на дзеркалі
    for dx in [395, 415, 435, 455, 475]:
        frags.append(circle(dx, 202, 3, fill="#38bdf8", stroke="#0284c7", sw=1))

    # Елемент Пельтьє під дзеркалом
    frags.append(rect(387, 226, 104, 24, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=3))
    frags.append(text(439, 242, "Модуль Пельтьє", size=11, bold=True, color="#dc2626"))

    # Термометр опору Pt100 у дзеркалі
    frags.append(rect(419, 250, 40, 12, fill="#fef08a", stroke="#ca8a04", sw=1, rx=2))
    frags.append(text(439, 259, "Pt100 (T_d)", size=9, bold=True, color="#854d0e"))

    # Світлодіод та фотодіод
    frags.append(circle(357, 130, 10, fill="#fef08a", stroke="#eab308", sw=1.5))
    frags.append(text(357, 112, "Світлодіод", size=10, color="#ca8a04"))
    frags.append(line(363, 138, 410, 200, color="#eab308", sw=1.5)) # промінь до дзеркала

    frags.append(circle(521, 130, 10, fill="#dcfce7", stroke="#22c55e", sw=1.5))
    frags.append(text(521, 112, "Фотодіод", size=10, color="#16a34a"))
    frags.append(line(468, 200, 515, 138, color="#22c55e", sw=1.5)) # відбитий промінь

    frags.append(text(439, 290, "Система зворотного зв'язку PID", size=10, bold=True, color="#334155"))
    frags.append(text(439, 395, "Оптичний контроль плівки роси T = T_d", size=10, italic=True, color="#475569"))

    # Блок 3: Ємнісний полімерний датчик (правий)
    frags.append(rect(590, 55, 265, 360, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(722, 78, "Ємнісний сорбційний", size=13, bold=True, color=PURPLE_S))

    # Підкладка
    frags.append(rect(620, 280, 205, 20, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    frags.append(text(722, 294, "Керамічна підкладка", size=10, color="#475569"))

    # Нижні зустрічно-штирьові електроди
    for ex in range(640, 810, 25):
        frags.append(rect(ex, 260, 12, 20, fill="#fbbf24", stroke="#d97706", sw=1))
    frags.append(text(722, 272, "Нижні електроди", size=9, color="#b45309"))

    # Гігроскопічний полімерний шар
    frags.append(rect(630, 200, 185, 60, fill="#f3e8ff", stroke="#a855f7", sw=1.5, rx=4))
    frags.append(text(722, 230, "Полімер (ε_p ≈ 3.5)", size=11, bold=True, color="#7e22ce"))
    frags.append(text(722, 248, "Поглинає H₂O (ε_H₂O ≈ 80)", size=10, color="#6b21a8"))

    # Пористий верхній електрод
    frags.append(rect(630, 188, 185, 12, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(722, 197, "Пористий Au-електрод (проникний)", size=9, bold=True, color="#854d0e"))

    # Молекули води, що входять
    for wx in [650, 690, 730, 770, 800]:
        frags.append(circle(wx, 160, 4, fill="#38bdf8", stroke="#0284c7", sw=1))
        frags.append(line(wx, 166, wx, 184, color="#0284c7", sw=1.2))

    frags.append(text(722, 340, "C(RH) = C₀ · (1 + α · RH)", size=11, bold=True, color="#581c87"))
    frags.append(text(722, 395, "Зміна ємності від поглинання води", size=10, italic=True, color="#475569"))

    render(os.path.join(IMG, "sensor-principles.svg"), W, H, *frags)

def fig_psychrometric_chart():
    """psychrometric-chart.svg: Психрометрична діаграма вологого повітря."""
    W, H = 880, 520
    frags = []

    frags.append(rect(10, 10, 860, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Психрометрична діаграма вологого повітря (P = 101.325 кПа)", size=16, bold=True, color="#1e293b"))

    # Сітка та осі
    ox, oy = 80, 440
    w_w, w_h = 740, 370

    frags.append(rect(ox, oy - w_h, w_w, w_h, fill="#ffffff", stroke="#94a3b8", sw=1.5))

    # Підписи осей
    frags.append(text(450, oy + 42, "Температура сухого термометра T (°C)", size=12, bold=True, color="#1e293b"))
    frags.append('<text x="%f" y="%f" transform="rotate(-90 %f %f)" font-family="%s" font-size="12" font-weight="bold" fill="#1e293b" text-anchor="middle">Влаговміст w (г/кг сухого повітря)</text>' % (ox - 45, oy - w_h / 2, ox - 45, oy - w_h / 2, FONT))

    # Шкала X: T від 0 до 50 °C
    for t in range(0, 51, 10):
        x = ox + (t / 50.0) * w_w
        frags.append(line(x, oy, x, oy + 6, color="#475569", sw=1.5))
        frags.append(text(x, oy + 22, "%d" % t, size=11, color="#334155"))
        if t > 0 and t < 50:
            frags.append(line(x, oy, x, oy - w_h, color="#f1f5f9", sw=1))

    # Шкала Y: w від 0 до 30 г/кг
    for w in range(0, 31, 5):
        y = oy - (w / 30.0) * w_h
        frags.append(line(ox - 6, y, ox, y, color="#475569", sw=1.5))
        frags.append(text(ox - 15, y + 4, "%d" % w, size=11, color="#334155", anchor="end"))
        if w > 0 and w < 30:
            frags.append(line(ox, y, ox + w_w, y, color="#f1f5f9", sw=1))

    # Криві відносної вологості (100%, 70%, 50%, 30%)
    import math
    def get_w_sat(t_c):
        ps = 0.6112 * math.exp(17.67 * t_c / (243.5 + t_c))
        return (0.622 * ps / (101.325 - ps)) * 1000.0

    rh_list = [(1.0, RED_S, "RH = 100% (Лінія насичення)", 2.5),
               (0.7, AMBER_S, "70%", 1.5),
               (0.5, GREEN_S, "50%", 1.5),
               (0.3, BLUE_S, "30%", 1.5)]

    for rh, color, label, sw_val in rh_list:
        pts = []
        for t_i in range(0, 51, 2):
            w_val = rh * get_w_sat(t_i)
            if w_val <= 30.0:
                px = ox + (t_i / 50.0) * w_w
                py = oy - (w_val / 30.0) * w_h
                pts.append((px, py))
        frags.append(polyline(pts, color=color, sw=sw_val))
        if pts:
            lx, ly = pts[-1]
            if lx < ox + w_w - 20:
                frags.append(text(lx + 8, ly + 4, label, size=10, bold=True, color=color))

    # Процес охолодження до точки роси (Точка A: 30°C, 50% RH -> w ≈ 13.3 г/кг)
    t_A, rh_A = 30.0, 0.5
    w_A = rh_A * get_w_sat(t_A) # ~13.3
    xA = ox + (t_A / 50.0) * w_w
    yA = oy - (w_A / 30.0) * w_h

    # Точка роси B (перетин w_A з 100% RH -> T_d ≈ 18.4°C)
    t_B = 18.4
    xB = ox + (t_B / 50.0) * w_w
    yB = yA

    # Лінія ізобаричного охолодження (горизонтальна)
    frags.append(line(xA, yA, xB, yB, color=PURPLE_S, sw=2, dash="4,4"))
    frags.append(circle(xA, yA, 5, fill=BLUE_S, stroke="#1e293b", sw=1.5))

    # Використовуємо fitbox / textbox для підписів без перетинів з лініями
    box_A, _, _ = textbox(xA + 70, yA + 25, "Стан А (30°C, 50% RH)", size=10, fill="#ffffff", stroke=BLUE_S, pad=4)
    frags.append(box_A)

    frags.append(circle(xB, yB, 5, fill=RED_S, stroke="#1e293b", sw=1.5))
    box_B, _, _ = textbox(xB - 75, yB - 22, "Точка роси B (T_d = 18.4°C)", size=10, fill="#ffffff", stroke=RED_S, pad=4)
    frags.append(box_B)

    # Пунктир опускання T_d на ос X
    frags.append(line(xB, yB, xB, oy, color=RED_S, sw=1.2, dash="3,3"))
    frags.append(text(xB, oy + 22, "18.4°C", size=10, bold=True, color=RED_S))

    # Лінія мокрого термометра (ізоентальпійне випаровування) від А до кривої 100% (T_w ≈ 22°C)
    t_w = 22.0
    w_w_val = get_w_sat(t_w)
    xW = ox + (t_w / 50.0) * w_w
    yW = oy - (w_w_val / 30.0) * w_h

    frags.append(line(xA, yA, xW, yW, color=GREEN_S, sw=2, dash="4,4"))
    frags.append(circle(xW, yW, 5, fill=GREEN_S, stroke="#1e293b", sw=1.5))

    box_W, _, _ = textbox(xW - 85, yW - 25, "Вологий термометр C (T_w = 22°C)", size=10, fill="#ffffff", stroke=GREEN_S, pad=4)
    frags.append(box_W)

    render(os.path.join(IMG, "psychrometric-chart.svg"), W, H, *frags)

def fig_saturation_vapor_pressure():
    """saturation-vapor-pressure.svg: Залежність тиску насиченої пари P_s(T)."""
    W, H = 880, 480
    frags = []

    frags.append(rect(10, 10, 860, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Крива тиску насиченої водяної пари P_s(T) за формулою Магнуса", size=16, bold=True, color="#1e293b"))

    ox, oy = 80, 400
    w_w, w_h = 740, 330

    frags.append(rect(ox, oy - w_h, w_w, w_h, fill="#ffffff", stroke="#94a3b8", sw=1.5))

    frags.append(text(450, oy + 42, "Температура T (°C)", size=12, bold=True, color="#1e293b"))
    frags.append('<text x="%f" y="%f" transform="rotate(-90 %f %f)" font-family="%s" font-size="12" font-weight="bold" fill="#1e293b" text-anchor="middle">Парціальний тиск пари P (кПа)</text>' % (ox - 45, oy - w_h / 2, ox - 45, oy - w_h / 2, FONT))

    import math
    def get_ps(t_c):
        return 0.6112 * math.exp(17.62 * t_c / (243.12 + t_c)) # в кПа

    # Шкала X: 0 до 50 °C
    for t in range(0, 51, 10):
        x = ox + (t / 50.0) * w_w
        frags.append(line(x, oy, x, oy + 6, color="#475569", sw=1.5))
        frags.append(text(x, oy + 22, "%d" % t, size=11, color="#334155"))
        if t > 0 and t < 50:
            frags.append(line(x, oy, x, oy - w_h, color="#f1f5f9", sw=1))

    # Шкала Y: 0 до 12 кПа
    for p in range(0, 13, 2):
        y = oy - (p / 12.0) * w_h
        frags.append(line(ox - 6, y, ox, y, color="#475569", sw=1.5))
        frags.append(text(ox - 15, y + 4, "%d" % p, size=11, color="#334155", anchor="end"))
        if p > 0 and p < 12:
            frags.append(line(ox, y, ox + w_w, y, color="#f1f5f9", sw=1))

    # Графік P_s(T)
    pts = []
    for t_i in range(0, 51):
        ps_val = get_ps(t_i)
        px = ox + (t_i / 50.0) * w_w
        py = oy - (ps_val / 12.0) * w_h
        pts.append((px, py))
    frags.append(polyline(pts, color=BLUE_S, sw=2.5))

    # Конкретна точка: T = 30°C -> P_s(30) ≈ 4.24 кПа
    t_curr = 30.0
    ps_30 = get_ps(t_curr) # 4.24 кПа
    pv_curr = 0.5 * ps_30 # 2.12 кПа

    # Проєкції
    x_curr = ox + (t_curr / 50.0) * w_w
    y_ps = oy - (ps_30 / 12.0) * w_h
    y_pv = oy - (pv_curr / 12.0) * w_h

    # Точка роси T_d де P_s(T_d) = 2.12 кПа -> T_d ≈ 18.4°C
    t_d = 18.4
    x_td = ox + (t_d / 50.0) * w_w

    # Вертикаль T = 30°C
    frags.append(line(x_curr, oy, x_curr, y_ps, color="#64748b", sw=1.2, dash="4,4"))
    frags.append(circle(x_curr, y_ps, 5, fill=BLUE_S, stroke="#1e293b", sw=1.5))

    box_ps, _, _ = textbox(x_curr + 70, y_ps - 15, "P_s(30°C) = 4.24 кПа", size=10, fill="#ffffff", stroke=BLUE_S, pad=4)
    frags.append(box_ps)

    # Точка виміряного тиску P_v
    frags.append(circle(x_curr, y_pv, 5, fill=GREEN_S, stroke="#1e293b", sw=1.5))
    box_pv, _, _ = textbox(x_curr + 80, y_pv + 20, "P_v = 2.12 кПа (Ф = 50%)", size=10, fill="#ffffff", stroke=GREEN_S, pad=4)
    frags.append(box_pv)

    # Горизонталь P_v від T=30°C ліворуч до кривої в точці роси
    frags.append(line(x_curr, y_pv, x_td, y_pv, color=RED_S, sw=1.8, dash="3,3"))
    frags.append(circle(x_td, y_pv, 5, fill=RED_S, stroke="#1e293b", sw=1.5))

    box_td, _, _ = textbox(x_td - 75, y_pv - 20, "Точка роси T_d = 18.4°C", size=10, fill="#ffffff", stroke=RED_S, pad=4)
    frags.append(box_td)

    # Пунктир від T_d до осі X
    frags.append(line(x_td, y_pv, x_td, oy, color=RED_S, sw=1.2, dash="3,3"))

    render(os.path.join(IMG, "saturation-vapor-pressure.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_sensor_principles()
    fig_psychrometric_chart()
    fig_saturation_vapor_pressure()
    print("Всі фігури згенеровано успішно.")
