# -*- coding: utf-8 -*-
"""Фігури до статті «Коронний розряд».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_corona_mechanism():
    """Фігура 1: Механізм коронного розряду — зона іонізації (чехол) та зона дрейфу."""
    W, H = 840, 480
    f = [text(W / 2, 28, "Структура коронного розряду: чехол іонізації та область дрейфу іонів", size=15, bold=True)]

    x_wire = 140
    y_wire = 240
    r_wire = 18
    x_plate = 720
    r_envelope = 75

    # 1. Зона іонізації (чехол корони)
    f.append(f'<circle cx="{x_wire}" cy="{y_wire}" r="{r_envelope}" fill="#3B82F6" opacity="0.18" stroke="#2563EB" stroke-width="1.5" stroke-dasharray="4 4"/>')

    # 2. Область дрейфу (між чехлом і пластиною)
    f.append(rect(x_wire + r_envelope, 80, x_plate - (x_wire + r_envelope), 320, fill="#F3F4F6", stroke=MUTED, sw=1.0))

    # Силові лінії електричного поля
    angles = [-60, -40, -20, 0, 20, 40, 60]
    for a in angles:
        rad = math.radians(a)
        x1 = x_wire + r_wire * math.cos(rad)
        y1 = y_wire + r_wire * math.sin(rad)
        x2 = x_plate
        y2 = y_wire + (x_plate - x_wire) * math.tan(rad) * 0.7
        f.append(line(x1, y1, x2, y2, color="#9CA3AF", sw=1.2, dash="2 2"))

    # Вістря / дріт (анод з високим додатним потенціалом)
    f.append(circle(x_wire, y_wire, r_wire, fill="#EF4444", stroke="#B91C1C", sw=2.5))
    f.append(text(x_wire, y_wire + 5, "+HV", size=12, bold=True, color="#FFFFFF", anchor="middle"))

    # Сяйво навколо дроту (чехол корони)
    f.append(f'<circle cx="{x_wire}" cy="{y_wire}" r="34" fill="none" stroke="#60A5FA" stroke-width="3.0" opacity="0.8"/>')
    f.append(f'<circle cx="{x_wire}" cy="{y_wire}" r="50" fill="none" stroke="#93C5FD" stroke-width="2.0" opacity="0.5"/>')

    # Лавини електронів у чехлі корони
    f.append(line(x_wire + 60, y_wire - 20, x_wire + 22, y_wire - 8, color="#DC2626", sw=2.0))
    f.append(line(x_wire + 55, y_wire + 25, x_wire + 22, y_wire + 10, color="#DC2626", sw=2.0))
    f.append(circle(x_wire + 60, y_wire - 20, 3, fill="#DC2626", stroke="#DC2626"))
    f.append(circle(x_wire + 55, y_wire + 25, 3, fill="#DC2626", stroke="#DC2626"))

    # Пластина (катод / заземлення)
    f.append(rect(x_plate, 80, 20, 320, fill="#4B5563", stroke="#1F2937", sw=2.0, rx=3))
    f.append(text(x_plate + 10, y_wire + 5, "GND (0 В)", size=11, bold=True, color="#FFFFFF", anchor="middle"))

    # Дрейфуючі додатні іони у зовнішній зоні
    ion_coords = [
        (x_wire + 120, y_wire - 60),
        (x_wire + 180, y_wire - 30),
        (x_wire + 260, y_wire - 80),
        (x_wire + 220, y_wire + 40),
        (x_wire + 310, y_wire + 10),
        (x_wire + 390, y_wire - 40),
        (x_wire + 440, y_wire + 50),
        (x_wire + 520, y_wire - 15),
        (x_wire + 600, y_wire + 35)
    ]
    for ix, iy in ion_coords:
        f.append(circle(ix, iy, 11, fill="#FEE2E2", stroke="#EF4444", sw=1.5))
        f.append(text(ix, iy + 4, "+", size=13, bold=True, color="#B91C1C", anchor="middle"))
        f.append(line(ix + 12, iy, ix + 24, iy, color="#EF4444", sw=1.5))

    # Виносні написи та роз'яснення в боксах
    b1 = fitbox(20, 70, 210, 100, "Чехол корони (r < r_i)\n• E > E_c (надпорогове поле)\n• Ударна іонізація й лавини\n• Плазмове сяйво та УФ\n• Утворення озону O₃", size=10, fill="#EFF6FF", stroke="#93C5FD", color="#1E3A8A")
    f.append(b1)
    f.append(line(130, 170, x_wire + 35, y_wire - 35, color="#2563EB", sw=1.5, dash="2 2"))

    b2 = fitbox(x_wire + 230, 400, 360, 65, "Область дрейфу іонів (r > r_i)\n• E < E_c (поверхня слабкого поля), без іонізації\n• Струм переносу додатними іонами до катода\n• Передача імпульсу повітрю (іонний вітер)", size=10, fill="#F9FAFB", stroke="#D1D5DB", color="#374151")
    f.append(b2)

    # Підписи меж - рознесено від ліній
    f.append(line(x_wire, y_wire + r_envelope + 5, x_wire, 350, color="#2563EB", sw=1.2, dash="3 3"))
    f.append(text(x_wire, 368, "r = r₀ (радіус дроту)", size=9.5, color=MUTED, anchor="middle"))
    f.append(line(x_wire + r_envelope, y_wire + r_envelope + 5, x_wire + r_envelope, 350, color="#2563EB", sw=1.2, dash="3 3"))
    f.append(text(x_wire + r_envelope, 368, "r = r_i (межа чехла)", size=9.5, color="#2563EB", anchor="middle"))

    render(os.path.join(IMG_DIR, "corona-mechanism.svg"), W, H, *f)


def fig_polarity_difference():
    """Фігура 2: Порівняння додатної та від'ємної корони."""
    W, H = 840, 460
    f = [text(W / 2, 28, "Порівняльний механізм додатної та від'ємної корони", size=15, bold=True)]

    # Ліва панель: Додатна корона
    x_left = 220
    f.append(rect(30, 60, 375, 370, fill="#FAF5FF", stroke="#C084FC", sw=1.5, rx=6))
    f.append(text(x_left, 88, "Додатна корона (+ на вістрі)", size=13, bold=True, color="#6B21A8", anchor="middle"))

    # Дріт +
    f.append(circle(x_left, 160, 20, fill="#EF4444", stroke="#B91C1C", sw=2))
    f.append(text(x_left, 165, "+HV", size=12, bold=True, color="#FFFFFF", anchor="middle"))
    f.append(f'<circle cx="{x_left}" cy="160" r="50" fill="none" stroke="#A855F7" stroke-width="2.5" opacity="0.7"/>')

    # Лавини електронів ідуть ДО дроту
    f.append(line(x_left - 70, 160, x_left - 25, 160, color="#DC2626", sw=2))
    f.append(line(x_left + 70, 160, x_left + 25, 160, color="#DC2626", sw=2))
    f.append(text(x_left - 80, 164, "e⁻", size=11, bold=True, color="#DC2626"))
    f.append(text(x_left + 80, 164, "e⁻", size=11, bold=True, color="#DC2626"))

    # Опис властивостей додатної корони
    t_pos = ("• Електрони втягуються до анода\n"
             "• Фотоіонізація газу створює нові носії\n"
             "• Рівномірне м'яке фіолетове сяйво\n"
             "• Дрейф додатних іонів (O₂⁺, N₂⁺) до землі\n"
             "• Низький рівень високочастотних завад")
    b_pos = fitbox(45, 250, 345, 160, t_pos, size=10, fill="#FFFFFF", stroke="#E9D5FF", color="#4C1D95")
    f.append(b_pos)

    # Права панель: Від'ємна корона
    x_right = 620
    f.append(rect(435, 60, 375, 370, fill="#EFF6FF", stroke="#60A5FA", sw=1.5, rx=6))
    f.append(text(x_right, 88, "Від'ємна корона (− на вістрі)", size=13, bold=True, color="#1E40AF", anchor="middle"))

    # Дріт -
    f.append(circle(x_right, 160, 20, fill="#2563EB", stroke="#1D4ED8", sw=2))
    f.append(text(x_right, 165, "−HV", size=12, bold=True, color="#FFFFFF", anchor="middle"))
    f.append(f'<circle cx="{x_right}" cy="160" r="50" fill="none" stroke="#3B82F6" stroke-width="2" stroke-dasharray="4 3"/>')

    # Лавини електронів ідуть ВІД дроту і приєднуються до O2
    f.append(line(x_right + 25, 160, x_right + 70, 160, color="#2563EB", sw=2))
    f.append(circle(x_right + 75, 160, 8, fill="#DBEAFE", stroke="#2563EB", sw=1))
    f.append(text(x_right + 75, 164, "O₂⁻", size=9, bold=True, color="#1E40AF", anchor="middle"))

    # Опис властивостей від'ємної корони
    t_neg = ("• Електрони вибиваються з катода і вилітають\n"
             "• Приєднання: e⁻ + O₂ → O₂⁻ (від'ємні іони)\n"
             "• Переривчасті імпульси Трічеля (100 кГц–1 МГц)\n"
             "• Плямисте сяйво (коронні намистини)\n"
             "• Більший вихід озону O₃ та радіозавад")
    b_neg = fitbox(450, 250, 345, 160, t_neg, size=10, fill="#FFFFFF", stroke="#BFDBFE", color="#1E3A8A")
    f.append(b_neg)

    render(os.path.join(IMG_DIR, "polarity-difference.svg"), W, H, *f)


def fig_peek_field_profile():
    """Фігура 3: Профіль напруженості електричного поля E(r) та критичне поле Піка Ec."""
    W, H = 840, 460
    f = [text(W / 2, 28, "Профіль електричного поля E(r) та межа чехла корони r_i", size=15, bold=True)]

    ox, oy = 110, 380
    top = 70
    right = 780

    # Осі
    f.append(line(ox, oy, right, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))
    f.append(text(right, oy + 26, "відстань від центру дроту r →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 15, top + 5, "E(r)", size=13, color=MUTED, anchor="end", italic=True))

    # Точки r0, ri, R
    r0_x = ox + 60
    ri_x = ox + 230
    R_x = ox + 620

    # Лінії позначення радіусів
    f.append(line(r0_x, oy, r0_x, top, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(r0_x, oy + 20, "r₀ (поверхня)", size=11, color=MUTED, anchor="middle"))

    f.append(line(ri_x, oy, ri_x, top, color="#2563EB", sw=1.2, dash="3 3"))
    f.append(text(ri_x, oy + 20, "r_i (межа корони)", size=11, color="#2563EB", anchor="middle"))

    f.append(line(R_x, oy, R_x, top, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(R_x, oy + 20, "R (зовнішній електрод)", size=11, color=MUTED, anchor="middle"))

    # Критичне поле пробою Ec (за формулою Піка)
    y_Ec = 180
    f.append(line(ox, y_Ec, right, y_Ec, color="#DC2626", sw=1.5, dash="5 4"))
    f.append(text(right - 10, y_Ec - 8, "E_c — критичне поле Піка (пробійний поріг ≈ 30 кВ/см)", size=10.5, color="#DC2626", anchor="end", bold=True))

    # Крива поля E(r) = U / (r * ln(R/r0))
    points = []
    for px in range(int(r0_x), int(R_x) + 1, 5):
        r_val = (px - ox) / 50.0
        E_val = 320.0 / r_val
        py = oy - E_val
        if py < top:
            py = top
        points.append((px, py))

    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    f.append(f'<path d="{path_d}" fill="none" stroke="#2563EB" stroke-width="3"/>')

    # Зафарбовування області E > Ec (Чехол корони)
    envelope_pts = [(r0_x, oy)] + [(px, py) for px, py in points if px <= ri_x] + [(ri_x, oy)]
    env_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in envelope_pts) + " Z"
    f.append(f'<path d="{env_d}" fill="#3B82F6" opacity="0.2"/>')

    # Написи на графіку
    f.append(text(r0_x + 15, oy - 270, "E_max = U / (r₀ ln(R/r₀))", size=11, color="#1E40AF", bold=True))

    b_info = fitbox(ri_x - 120, y_Ec - 80, 200, 60, "Область коронування (E > E_c):\nтут виникають лавини", size=10, fill="#FEF2F2", stroke="#FCA5A5", color="#B91C1C")
    f.append(b_info)

    b_drift = fitbox((ri_x + R_x) / 2 - 120, 250, 240, 70, "Зона дрейфу іонів (E < E_c):\nполя недостатньо для іонізації,\nструм стікає без лавин", size=10, fill="#F9FAFB", stroke="#E5E7EB", color="#374151")
    f.append(b_drift)

    render(os.path.join(IMG_DIR, "peek-field-profile.svg"), W, H, *f)


def fig_applications():
    """Фігура 4: Схема застосувань коронного розряду — електрофільтр та озонізатор/коротрон."""
    W, H = 840, 480
    f = [text(W / 2, 28, "Практичне застосування: електростатичний фільтр (ESP) та коротрон", size=15, bold=True)]

    # Ліва частина: Електростатичний фільтр (Electrostatic Precipitator)
    f.append(rect(30, 60, 375, 380, fill="#F9FAFB", stroke="#9CA3AF", sw=1.5, rx=6))
    f.append(text(217, 88, "Електростатичний очисник газу (ESP)", size=13, bold=True, color="#1F2937", anchor="middle"))

    # Потік брудного газу зліва
    f.append(line(45, 230, 85, 230, color="#6B7280", sw=2))
    f.append(text(45, 220, "Запилений газ", size=10, color="#4B5563"))

    # Негативний коронуючий дріт у центрі
    f.append(circle(217, 230, 8, fill="#2563EB", stroke="#1D4ED8", sw=1.5))
    f.append(text(217, 234, "−HV", size=9.5, bold=True, color="#FFFFFF", anchor="middle"))

    # Позитивні осаджувальні пластини зверху та знизу
    f.append(rect(100, 130, 235, 12, fill="#EF4444", stroke="#B91C1C", sw=1, rx=2))
    f.append(rect(100, 310, 235, 12, fill="#EF4444", stroke="#B91C1C", sw=1, rx=2))
    f.append(text(217, 122, "Осаджувальна пластина (GND / +)", size=9.5, color="#B91C1C", anchor="middle"))

    # Частинки пилу заряджаються і осідають на пластинах
    dust_particles = [
        (110, 230, False), (140, 210, True), (170, 180, True),
        (230, 160, True), (280, 146, True), (150, 250, True),
        (200, 280, True), (270, 304, True)
    ]
    for dx, dy, charged in dust_particles:
        f.append(circle(dx, dy, 5, fill="#78350F" if not charged else "#D97706", stroke="#451A03", sw=1))
        if charged:
            f.append(line(dx, dy, dx + (15 if dy < 230 else 10), dy + (-20 if dy < 230 else 20), color="#D97706", sw=1.2))

    # Очищений газ праворуч
    f.append(line(350, 230, 390, 230, color="#059669", sw=2))
    f.append(text(340, 220, "Очищений газ (>99.9%)", size=10, color="#059669"))

    b_esp = fitbox(50, 355, 335, 65, "1. Коронування створює O₂⁻ іони\n2. Іони заряджають частинки пилу\n3. Кулонівська сила притягує їх до пластин", size=9.5, fill="#FFFFFF", stroke="#E5E7EB", color="#374151")
    f.append(b_esp)

    # Права частина: Коротрон у лазерному друку / фотокопіюванню
    f.append(rect(435, 60, 375, 380, fill="#F0FDF4", stroke="#4ADE80", sw=1.5, rx=6))
    f.append(text(622, 88, "Коротрон у лазерному принтері", size=13, bold=True, color="#065F46", anchor="middle"))

    # Барабан
    f.append(circle(622, 270, 75, fill="#DCFCE7", stroke="#16A34A", sw=2))
    f.append(text(622, 275, "Фотобарабан", size=11, bold=True, color="#15803D", anchor="middle"))

    # Дріт коротрона в екрані
    f.append(f'<rect x="572" y="130" width="100" height="40" fill="none" stroke="#059669" stroke-width="1.5" stroke-dasharray="3 3"/>')
    f.append(circle(622, 150, 6, fill="#EF4444", stroke="#B91C1C", sw=1.5))
    f.append(text(622, 153, "+HV", size=9.5, color="#FFFFFF", bold=True, anchor="middle"))

    # Потік іонів на поверхню барабана
    for ix in range(592, 653, 12):
        f.append(line(ix, 160, ix, 192, color="#059669", sw=1.2))

    # Заряджений шар на барабані
    f.append(f'<circle cx="622" cy="270" r="78" fill="none" stroke="#15803D" stroke-width="2" stroke-dasharray="3 3"/>')

    b_copier = fitbox(455, 355, 335, 65, "• Нанесення рівномірного заряду на фотошар\n• Перенесення тонера на папір\n• Низький струм (мікроампери), висока стабільність", size=9.5, fill="#FFFFFF", stroke="#BBF2D0", color="#064E3B")
    f.append(b_copier)

    render(os.path.join(IMG_DIR, "applications-precipitator-copier.svg"), W, H, *f)


if __name__ == "__main__":
    fig_corona_mechanism()
    fig_polarity_difference()
    fig_peek_field_profile()
    fig_applications()
    print("Figures generated successfully in img/")
