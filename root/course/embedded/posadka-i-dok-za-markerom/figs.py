# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Посадка й док за маркером»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку для імпорту svgkit та svgcheck
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig1_pnp_geometry():
    """Геометрія PnP: від 3D-точок маркера до 6DoF пози камери."""
    w, h = 900, 480
    frags = []

    # 1. Тло панелей
    frags.append(rect(20, 45, 270, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(310, 45, 270, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(600, 45, 280, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовки панелей
    frags.append(text(155, 75, "1. Маркер у просторі (3D)", size=15, color=INK, bold=True))
    frags.append(text(445, 75, "2. Проєкція на сенсор (2D)", size=15, color=INK, bold=True))
    frags.append(text(740, 75, "3. Розв'язок PnP (6DoF поза)", size=15, color=INK, bold=True))

    # Панель 1: Світ / Маркер
    # Квадрат маркера в перспективі
    frags.append(rect(60, 110, 190, 190, fill="#1e293b", stroke="#0f172a", sw=2, rx=4))
    frags.append(rect(85, 135, 140, 140, fill="#ffffff", stroke="#334155", sw=1.5, rx=2))
    # Внутрішня бінарна сітка маркера 3x3
    frags.append(rect(95, 145, 40, 40, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(175, 145, 40, 40, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(135, 185, 40, 40, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(95, 225, 40, 40, fill="#0f172a", stroke="#0f172a", sw=1))

    # Кутові точки P1..P4
    corners = [(60, 110), (250, 110), (250, 300), (60, 300)]
    for cx, cy in corners:
        frags.append(circle(cx, cy, 5, fill=POS, stroke="#ffffff", sw=1.5))

    frags.append(text(60, 100, "P1", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(250, 100, "P2", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(250, 318, "P3", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(60, 318, "P4", size=12, color=POS, bold=True, anchor="middle"))

    # Осі маркера в центрі
    frags.append(arrow(155, 205, 195, 205, color=POS, sw=2))
    frags.append(text(205, 209, "Xm", size=12, color=POS, bold=True))
    frags.append(arrow(155, 205, 155, 165, color=FIELD, sw=2))
    frags.append(text(155, 155, "Ym", size=12, color=FIELD, bold=True))

    box1, _, _ = textbox(155, 385, "Відома 3D геометрія:\nРозмір L × L (метри)\n4 опорні вершини\nZ_m = 0 (площина)", size=12, fill="#ffffff", stroke="#94a3b8")
    frags.append(box1)

    # Панель 2: Проєкція та внутрішні параметри камери
    # Зображення камери
    frags.append(rect(340, 120, 210, 150, fill="#0f172a", stroke="#334155", sw=2, rx=6))
    # Спотворений чотирикутник на матриці
    frags.append('<polygon points="365,150 515,135 490,245 385,230" fill="#38bdf8" fill-opacity="0.25" stroke="#38bdf8" stroke-width="2"/>')
    # Піксельні кути p1..p4
    p_corners = [(365, 150), (515, 135), (490, 245), (385, 230)]
    for px, py in p_corners:
        frags.append(circle(px, py, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(text(352, 148, "p1", size=11, color="#38bdf8", bold=True))
    frags.append(text(528, 133, "p2", size=11, color="#38bdf8", bold=True))
    frags.append(text(503, 248, "p3", size=11, color="#38bdf8", bold=True))
    frags.append(text(373, 233, "p4", size=11, color="#38bdf8", bold=True))

    # Головна точка (cx, cy)
    frags.append(line(445, 185, 445, 205, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(435, 195, 455, 195, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(445, 215, "(cx, cy)", size=11, color=MUTED))

    box2, _, _ = textbox(445, 385, "Калібрування камери K:\nФокус fx, fy (пікселі)\nОптичний центр cx, cy\nДисторсія [k1, k2, p1, p2]", size=12, fill="#ffffff", stroke="#94a3b8")
    frags.append(box2)

    # Панель 3: Вихід PnP — 6DoF поза
    frags.append(rect(625, 110, 230, 100, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(740, 135, "Вектор трансляції t (3DoF):", size=13, color=INK, bold=True))
    frags.append(text(740, 160, "t = [ X_c,  Y_c,  Z_c ]^T", size=14, color=NEG, bold=True))
    frags.append(text(740, 190, "Дистанція: Z_c (висота над міткою)", size=12, color=MUTED))

    frags.append(rect(625, 225, 230, 100, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(740, 250, "Орієнтація R (3DoF):", size=13, color=INK, bold=True))
    frags.append(text(740, 275, "R_mc (матриця) / q (кватерніон)", size=13, color=FIELD, bold=True))
    frags.append(text(740, 305, "Кути Ейлера: крен, тангаж, курс", size=12, color=MUTED))

    box3, _, _ = textbox(740, 395, "Оцінювач пози (IPPE / SQPnP):\ns·[u, v, 1]^T = K·[R|t]·[X, Y, Z, 1]^T\nМінімізація похибки перепроєкції", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(box3)

    # Стрілки зв'язку між панелями
    frags.append(arrow(295, 205, 305, 205, color=LINE, sw=2))
    frags.append(arrow(585, 205, 595, 205, color=LINE, sw=2))

    render(os.path.join(OUT_DIR, "pnp-geometry.svg"), w, h, *frags)


def fig2_nested_markers():
    """Ієрархічний багатомасштабний маркер та вирішення парадоксу поля зору (FOV)."""
    w, h = 920, 480
    frags = []

    # Ліва частина: Будова вкладеного маркера
    frags.append(rect(20, 45, 380, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(210, 75, "Конструкція вкладеного маркера", size=16, color=INK, bold=True))

    # Зовнішній великий маркер (80x80 см)
    frags.append(rect(55, 105, 310, 250, fill="#0f172a", stroke="#0f172a", sw=2, rx=4))
    frags.append(rect(75, 125, 270, 210, fill="#ffffff", stroke="#0f172a", sw=1.5))
    frags.append(text(210, 145, "Зовнішній маркер: 80 × 80 см (ID: 0)", size=12, color=MUTED, bold=True))

    # Бінарні клітинки зовнішнього маркера
    frags.append(rect(85, 160, 45, 45, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(290, 160, 45, 45, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(85, 280, 45, 45, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(290, 280, 45, 45, fill="#0f172a", stroke="#0f172a", sw=1))

    # Середній вкладений маркер (20x20 см)
    frags.append(rect(145, 175, 130, 130, fill="#0f172a", stroke="#0284c7", sw=2, rx=3))
    frags.append(rect(155, 185, 110, 110, fill="#ffffff", stroke="#0284c7", sw=1.5))
    frags.append(rect(162, 192, 28, 28, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(227, 192, 28, 28, fill="#0f172a", stroke="#0f172a", sw=1))

    # Мікромаркер (5x5 см)
    frags.append(rect(190, 225, 40, 40, fill="#0f172a", stroke="#16a34a", sw=1.5, rx=2))
    frags.append(rect(196, 231, 28, 28, fill="#ffffff", stroke="#16a34a", sw=1))
    frags.append(rect(202, 237, 16, 16, fill="#0f172a", stroke="#0f172a", sw=1))

    box_l, _, _ = textbox(210, 405, "Діапазони видимості:\n• Зовнішній 80 см: h = 3–20 м (захоплення)\n• Середній 20 см: h = 0.6–4 м (наведення)\n• Мікро 5 см: h = 0.05–0.8 м (док впритул)", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_l)

    # Права частина: Парадокс FOV на різних висотах
    frags.append(rect(420, 45, 480, 415, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(660, 75, "Кадр камери залежно від висоти", size=16, color=INK, bold=True))

    # Випадок А: Велика висота (15 м)
    frags.append(rect(440, 100, 210, 140, fill="#ffffff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(545, 120, "Висота h = 15 м (FOV = 30 м)", size=12, color=INK, bold=True))
    # Маленький маркер у центрі кадру
    frags.append(rect(530, 150, 30, 30, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(536, 156, 18, 18, fill="#ffffff", stroke="#0f172a", sw=1))
    frags.append(text(545, 205, "Зовнішній маркер: 40 px (OK)\nВкладений: < 5 px (не видно)", size=11, color=FIELD))

    # Випадок Б: Мала висота (0.3 м)
    frags.append(rect(670, 100, 210, 140, fill="#ffffff", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(775, 120, "Висота h = 0.3 м (FOV = 0.4 м)", size=12, color=INK, bold=True))
    # Обрізаний великий маркер, але чіткий мікромаркер
    frags.append('<rect x="650" y="80" width="250" height="180" rx="6" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4"/>')
    frags.append(rect(735, 135, 80, 80, fill="#0f172a", stroke="#16a34a", sw=2))
    frags.append(rect(747, 147, 56, 56, fill="#ffffff", stroke="#16a34a", sw=1.5))
    frags.append(rect(760, 160, 30, 30, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(text(775, 225, "Зовнішній маркер: ОБРІЗАНО\nВкладений/мікро: 300 px (OK)", size=11, color=POS))

    # Схема передачі естафети (Handover)
    box_r, _, _ = textbox(660, 350, "Алгоритм перемикання (Handover):\n1. Пріоритет найменшому видимому маркеру\n2. Гістерезис по висоті (проти брязкоту)\n3. Компенсація зсуву центрів: ΔX, ΔY\n4. Плавне злиття в EKF (без стрибків уставки)", size=11, fill="#ffffff", stroke="#0284c7")
    frags.append(box_r)

    render(os.path.join(OUT_DIR, "nested-markers.svg"), w, h, *frags)


def fig3_landing_trajectory_cone():
    """Траєкторія посадки, звужуваний конус безпеки та керування швидкістю."""
    w, h = 900, 500
    frags = []

    # 1. Заголовок
    frags.append(rect(20, 35, 860, 445, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # 2. Зона конуса посадки (зліва)
    frags.append(text(270, 65, "Профіль зниження та конус безпеки (Landing Cone)", size=15, color=INK, bold=True))

    # Конус безпеки (напівпрозорий зелений полігон)
    frags.append('<polygon points="120,110 420,110 300,410 240,410" fill="#22c55e" fill-opacity="0.12" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="5,5"/>')

    # Центральна вісь посадки
    frags.append(line(270, 90, 270, 420, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(270, 435, "Маркер (Z=0, X=0, Y=0)", size=12, color=FIELD, bold=True))

    # Маркер на землі
    frags.append(rect(225, 410, 90, 10, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(245, 412, 50, 6, fill="#ffffff", stroke="#0f172a", sw=1))

    # Траєкторія дрона
    frags.append('<path d="M 160,110 Q 230,160 250,220 T 268,340 L 270,410" fill="none" stroke="#2563eb" stroke-width="2.5"/>')

    # Точки етапів на траєкторії
    # Дрон на 15 м
    frags.append(circle(160, 110, 7, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(125, 105, "h = 15 м", size=12, color=POS, bold=True))
    frags.append(arrow(160, 110, 200, 125, color=POS, sw=2))

    # Дрон на 6 м
    frags.append(circle(250, 220, 7, fill="#0284c7", stroke="#ffffff", sw=2))
    frags.append(text(195, 225, "h = 6 м", size=12, color="#0284c7", bold=True))

    # Дрон на 1.5 м
    frags.append(circle(268, 340, 6, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(215, 345, "h = 1.5 м", size=12, color=FIELD, bold=True))

    # Межі конуса r_max(h)
    frags.append(line(270, 160, 395, 160, color="#16a34a", sw=1))
    frags.append(text(335, 152, "r_max(h)", size=11, color="#16a34a"))

    # 3. Права частина: Опис 4 фаз посадки
    phases = [
        ("Фаза 1: Захоплення (10–20 м)", "Детектування великого маркера. Гасіння початкового\nдрейфу GNSS. Вхід у зону безпечного конуса.", "#dbeafe", "#1d4ed8"),
        ("Фаза 2: Підхід та утримання (3–10 м)", "Горизонтальне центрування над маркером.\nШвидкість зниження vz = k·h. Компенсація вітру (I-term).", "#e0f2fe", "#0284c7"),
        ("Фаза 3: Прецизійне зниження (0.3–3 м)", "Перемикання на вкладений маркер. Зниження vz до 0.2 м/с.\nТочність утримання осі < 3 см.", "#dcfce7", "#15803d"),
        ("Фаза 4: Док і фіксація (0–0.3 м)", "Вимкнення оптики за 5 см. Механічне центрування конусами.\nЗамикання силових контактів, підтвердження заряду.", "#fef3c7", "#b45309"),
    ]

    y_pos = 95
    for title_p, desc_p, bg_c, brd_c in phases:
        frags.append(rect(480, y_pos, 380, 75, fill=bg_c, stroke=brd_c, sw=1.5, rx=6))
        frags.append(text(495, y_pos + 22, title_p, size=13, color=brd_c, bold=True, anchor="start"))
        lines = desc_p.split("\n")
        for i, line_txt in enumerate(lines):
            frags.append(text(495, y_pos + 42 + i * 16, line_txt, size=11, color=INK, anchor="start"))
        y_pos += 88

    render(os.path.join(OUT_DIR, "landing-trajectory-cone.svg"), w, h, *frags)


def fig4_docking_mechanics_contacts():
    """Механічне самоцентрування та замикання зарядних контактів док-станції."""
    w, h = 900, 460
    frags = []

    # 1. Тло панелей
    frags.append(rect(20, 35, 415, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(455, 35, 425, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    frags.append(text(227, 65, "1. Механіка самоцентрування", size=15, color=INK, bold=True))
    frags.append(text(667, 65, "2. Замикання силових контактів", size=15, color=INK, bold=True))

    # Ліва панель: Конуси та пази
    # Опора дрона (ніжка з конусним штифтом)
    frags.append(rect(200, 95, 55, 50, fill="#334155", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(text(227, 125, "Опора дрона", size=11, color="#ffffff", bold=True))
    # Конусний наконечник
    frags.append('<polygon points="205,145 250,145 227,190" fill="#64748b" stroke="#0f172a" stroke-width="1.5"/>')
    frags.append(text(227, 170, "Штифт", size=10, color="#ffffff"))

    # Стрілка опускання
    frags.append(arrow(227, 195, 227, 230, color=POS, sw=2))
    frags.append(text(245, 215, "Посадка", size=11, color=POS, bold=True))

    # Ловильний конус док-станції (V-подібна вирва)
    frags.append('<polygon points="120,240 335,240 255,310 200,310" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    frags.append(rect(200, 310, 55, 30, fill="#94a3b8", stroke="#475569", sw=1.5))
    frags.append(text(227, 275, "V-подібна напрямна вирва", size=12, color=INK, bold=True))
    frags.append(text(227, 330, "Фіксатор", size=11, color="#ffffff", bold=True))

    box_m, _, _ = textbox(227, 390, "Пасивне виправлення похибки:\n• Оптичне наведення підводить з точністю ±20 мм\n• Конічна вирва стягує штифт у центр із точністю ±0.5 мм\n• Магнітні неодимові замки фіксують від вітру", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_m)

    # Права панель: Електрична контактна група (Pogo-pins та кільця)
    # Концентричні контакти на дроні
    frags.append(rect(500, 100, 335, 35, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=4))
    frags.append(rect(525, 135, 60, 8, fill="#eab308", stroke="#ca8a04", sw=1))
    frags.append(rect(635, 135, 60, 8, fill="#3b82f6", stroke="#2563eb", sw=1))
    frags.append(rect(745, 135, 45, 8, fill="#22c55e", stroke="#16a34a", sw=1))

    frags.append(text(555, 122, "+V_BAT", size=11, color="#fef08a", bold=True))
    frags.append(text(665, 122, "GND", size=11, color="#bfdbfe", bold=True))
    frags.append(text(767, 122, "SENSE", size=11, color="#bbf7d0", bold=True))

    # Пружинні Pogo-pins на базі
    frags.append(line(555, 145, 555, 195, color="#ca8a04", sw=3))
    frags.append(line(665, 145, 665, 195, color="#2563eb", sw=3))
    frags.append(line(767, 145, 767, 195, color="#16a34a", sw=3))

    # Пружинки
    frags.append(circle(555, 210, 12, fill="#fef9c3", stroke="#ca8a04", sw=1.5))
    frags.append(circle(665, 210, 12, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(circle(767, 210, 12, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(555, 214, "+", size=12, color="#ca8a04", bold=True))
    frags.append(text(665, 214, "−", size=12, color="#2563eb", bold=True))
    frags.append(text(767, 214, "S", size=12, color="#16a34a", bold=True))

    frags.append(rect(500, 235, 335, 45, fill="#334155", stroke="#0f172a", sw=1.5, rx=4))
    frags.append(text(667, 262, "Плата керування заряджанням док-станції", size=12, color="#ffffff", bold=True))

    box_e, _, _ = textbox(667, 365, "Послідовність безпечного ввімкнення:\n1. Механічний контакт стискає пружні pogo-піни\n2. Лінія SENSE детектує підключення акумулятора дрона\n3. BMS handshake: перевірка напруги та температури\n4. Силове реле замикає лінію швидкої зарядки", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_e)

    render(os.path.join(OUT_DIR, "docking-mechanics-contacts.svg"), w, h, *frags)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    fig1_pnp_geometry()
    fig2_nested_markers()
    fig3_landing_trajectory_cone()
    fig4_docking_mechanics_contacts()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
