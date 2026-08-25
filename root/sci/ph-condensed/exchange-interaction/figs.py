# -*- coding: utf-8 -*-
"""Фігури до теми «Обмінна взаємодія».
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

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Квантовомеханічна природа обмінної взаємодії ───────────────────
def fig_coulomb_vs_exchange():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Фізична природа обмінної взаємодії: Принцип Паулі та Кулонівська енергія", size=15, bold=True, color=INK))

    w_card = 350
    h_card = 340
    y_card = 55

    # Ліва картка: Тріплетний стан (паралельні спіни ↑↑)
    x1 = 30
    f.append(rect(x1, y_card, w_card, h_card, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    f.append(text(x1 + w_card / 2, y_card + 25, "Тріплетний стан S = 1 (Спіни паралельні ↑↑)", size=13, bold=True, color="#0369a1"))
    
    # Спінові стрілки
    f.append(rect(x1 + 30, y_card + 45, 130, 45, fill="#ffffff", stroke="#0284c7", sw=1, rx=4))
    f.append(arrow(x1 + 65, y_card + 82, x1 + 65, y_card + 52, color="#2563eb", sw=2.5))
    f.append(arrow(x1 + 125, y_card + 82, x1 + 125, y_card + 52, color="#2563eb", sw=2.5))
    f.append(text(x1 + 95, y_card + 68, "↑ ↑", size=14, bold=True, color="#2563eb"))

    f.append(fitbox(x1 + 175, y_card + 45, 145, 45, "Спінова ФУ:\nсиметрична", size=11, bold=True, color="#0369a1", fill="#ffffff", stroke="#0284c7"))

    # Графік ймовірності знаходження двох електронів на відстані r12
    x_g1 = x1 + 40
    y_g1 = y_card + 210
    w_g = 270
    h_g = 100

    f.append(line(x_g1, y_g1, x_g1 + w_g, y_g1, color=INK, sw=1.2))
    f.append(line(x_g1, y_g1, x_g1, y_g1 - h_g, color=INK, sw=1.2))
    f.append(text(x_g1 + w_g - 20, y_g1 + 16, "r₁₂", size=11, bold=True, italic=True, color=INK))
    f.append(text(x_g1 - 15, y_g1 - h_g + 10, "|ψ|²", size=11, bold=True, italic=True, color=INK))

    # Крива для тріплету: густина ймовірності прямує до 0 при r12 -> 0 (ферміонова дірка Паулі)
    pts_trip = []
    for px in range(0, int(w_g)):
        r = px / w_g * 4.0
        val = (r**2) * math.exp(-r) * 1.4
        py = y_g1 - min(val * (h_g - 15), h_g - 5)
        pts_trip.append((x_g1 + px, py))
    d_trip = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_trip)
    f.append(path_svg(d_trip, stroke="#2563eb", sw=2.5))

    f.append(circle(x_g1, y_g1, 4, fill="#dc2626", stroke="#dc2626"))
    f.append(text(x_g1 + 65, y_g1 - 12, "Дірка Паулі: ψ_A(r,r) = 0", size=10, bold=True, color="#dc2626"))

    f.append(fitbox(x1 + 20, y_card + 235, 310, 85, "Електрони уникають один одного за принципом Паулі.\nСередня відстань <r₁₂> більша → кулонівське відштовхування менше!\nЕнергія стану: E_T = E₀ + K - J", size=10, color="#1e293b", fill="#ffffff", stroke="#94a3b8"))


    # Права картка: Синглетний стан (антипаралельні спіни ↑↓)
    x2 = 400
    f.append(rect(x2, y_card, w_card, h_card, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    f.append(text(x2 + w_card / 2, y_card + 25, "Синглетний стан S = 0 (Спіни антипаралельні ↑↓)", size=13, bold=True, color="#b91c1c"))

    # Спінові стрілки
    f.append(rect(x2 + 30, y_card + 45, 130, 45, fill="#ffffff", stroke="#ef4444", sw=1, rx=4))
    f.append(arrow(x2 + 65, y_card + 82, x2 + 65, y_card + 52, color="#dc2626", sw=2.5))
    f.append(arrow(x2 + 125, y_card + 52, x2 + 125, y_card + 82, color="#2563eb", sw=2.5))
    f.append(text(x2 + 95, y_card + 68, "↑ ↓", size=14, bold=True, color="#dc2626"))

    f.append(fitbox(x2 + 175, y_card + 45, 145, 45, "Спінова ФУ:\nантисиметрична", size=11, bold=True, color="#b91c1c", fill="#ffffff", stroke="#ef4444"))

    # Графік ймовірності для синглету
    x_g2 = x2 + 40
    y_g2 = y_card + 210

    f.append(line(x_g2, y_g2, x_g2 + w_g, y_g2, color=INK, sw=1.2))
    f.append(line(x_g2, y_g2, x_g2, y_g2 - h_g, color=INK, sw=1.2))
    f.append(text(x_g2 + w_g - 20, y_g2 + 16, "r₁₂", size=11, bold=True, italic=True, color=INK))
    f.append(text(x_g2 - 15, y_g2 - h_g + 10, "|ψ|²", size=11, bold=True, italic=True, color=INK))

    # Крива для синглету: максимум ймовірності при малих r12
    pts_sing = []
    for px in range(0, int(w_g)):
        r = px / w_g * 4.0
        val = math.exp(-r * 0.9) * 1.1
        py = y_g2 - min(val * (h_g - 15), h_g - 5)
        pts_sing.append((x_g2 + px, py))
    d_sing = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_sing)
    f.append(path_svg(d_sing, stroke="#dc2626", sw=2.5))

    f.append(text(x_g2 + 75, y_g2 - 75, "ψ_S(r,r) ≠ 0 (не нуль!)", size=10, bold=True, color="#dc2626"))

    f.append(fitbox(x2 + 20, y_card + 235, 310, 85, "Просторова хвильова функція симетрична.\nЕлектрони можуть зближуватись → кулонівське відштовхування вище!\nЕнергія стану: E_S = E₀ + K + J", size=10, color="#1e293b", fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(IMG_DIR, 'coulomb-vs-exchange.svg'), W, H, "\n".join(f))


# ── Фігура 2: Різновиди обмінної взаємодії ────────────────────────────────────
def fig_exchange_mechanisms():
    W, H = 780, 480
    f = []

    f.append(text(W / 2, 25, "Основні типи квантової обмінної взаємодії у речовині", size=15, bold=True, color=INK))

    w_box = 355
    h_box = 200

    # 1. Прямий обмін (Direct Exchange)
    x1, y1 = 25, 50
    f.append(rect(x1, y1, w_box, h_box, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=6))
    f.append(text(x1 + w_box / 2, y1 + 18, "1. Прямий обмін (Direct Exchange)", size=12, bold=True, color="#1d4ed8"))
    
    # Атоми й d-орбіталі
    cx1, cy1 = x1 + 100, y1 + 65
    cx2, cy2 = x1 + 255, y1 + 65
    f.append(circle(cx1, cy1, 15, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    f.append(circle(cx2, cy2, 15, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    f.append(text(cx1, cy1 + 4, "Fe", size=11, bold=True, color="#1e40af"))
    f.append(text(cx2, cy2 + 4, "Fe", size=11, bold=True, color="#1e40af"))
    f.append(arrow(cx1, cy1 - 22, cx1, cy1 - 38, color="#2563eb", sw=2))
    f.append(arrow(cx2, cy2 - 22, cx2, cy2 - 38, color="#2563eb", sw=2))

    # Перекриття орбіталей
    f.append(ellipse_svg(cx1 + 20, cy1, 24, 12, fill="#93c5fd", stroke="#2563eb", sw=1, dash="2,2"))
    f.append(ellipse_svg(cx2 - 20, cy2, 24, 12, fill="#93c5fd", stroke="#2563eb", sw=1, dash="2,2"))

    f.append(fitbox(x1 + 15, y1 + 115, 325, 72, "Безпосереднє перекриття електронних оболонок (d-орбіталей) сусідніх магнітних іонів.\nДіє на малих відстанях між атомами.", size=10, color="#334155", fill="#ffffff", stroke="#cbd5e1"))

    # 2. Суперобмін (Super-exchange)
    x2, y2 = 400, 50
    f.append(rect(x2, y2, w_box, h_box, fill="#f8fafc", stroke="#059669", sw=1.5, rx=6))
    f.append(text(x2 + w_box / 2, y2 + 18, "2. Непрямий суперобмін (Superexchange)", size=12, bold=True, color="#047857"))

    cxa, cya = x2 + 75, y2 + 65
    cxo, cyo = x2 + 177, y2 + 65
    cxb, cyb = x2 + 280, y2 + 65
    f.append(circle(cxa, cya, 15, fill="#d1fae5", stroke="#059669", sw=1.5))
    f.append(circle(cxo, cyo, 18, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(circle(cxb, cyb, 15, fill="#d1fae5", stroke="#059669", sw=1.5))
    f.append(text(cxa, cya + 4, "Mn³⁺", size=10, bold=True, color="#047857"))
    f.append(text(cxo, cyo + 4, "O²⁻", size=11, bold=True, color="#b45309"))
    f.append(text(cxb, cyb + 4, "Mn³⁺", size=10, bold=True, color="#047857"))
    
    f.append(arrow(cxa, cya - 22, cxa, cya - 38, color="#059669", sw=2))
    f.append(arrow(cxb, cyb - 38, cxb, cyb - 22, color="#dc2626", sw=2)) # Антипаралельний

    f.append(fitbox(x2 + 15, y2 + 115, 325, 72, "Опосередкована взаємодія через проміжний немагнітний аніон (наприклад O²⁻).\nПравила Гуденафа — Канаморі дають антиферомагнетизм.", size=10, color="#334155", fill="#ffffff", stroke="#cbd5e1"))

    # 3. Подвійний обмін (Double Exchange)
    x3, y3 = 25, 265
    f.append(rect(x3, y3, w_box, h_box, fill="#f8fafc", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(x3 + w_box / 2, y3 + 18, "3. Подвійний обмін (Double Exchange)", size=12, bold=True, color="#b45309"))

    cxa3, cya3 = x3 + 75, y3 + 65
    cxo3, cyo3 = x3 + 177, y3 + 65
    cxb3, cyb3 = x3 + 280, y3 + 65
    f.append(circle(cxa3, cya3, 15, fill="#ffedd5", stroke="#ea580c", sw=1.5))
    f.append(circle(cxo3, cyo3, 18, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(circle(cxb3, cyb3, 15, fill="#ffedd5", stroke="#ea580c", sw=1.5))
    f.append(text(cxa3, cya3 + 4, "Mn³⁺", size=10, bold=True, color="#c2410c"))
    f.append(text(cxo3, cyo3 + 4, "O²⁻", size=11, bold=True, color="#b45309"))
    f.append(text(cxb3, cyb3 + 4, "Mn⁴⁺", size=10, bold=True, color="#c2410c"))

    # Стрілки переносу електрона зі збереженням спіну
    f.append(arrow(cxo3 - 8, cyo3 - 22, cxa3 + 12, cya3 - 22, color="#ea580c", sw=2))
    f.append(arrow(cxa3, cya3 - 22, cxa3, cya3 - 38, color="#ea580c", sw=2))
    f.append(arrow(cxb3, cyb3 - 22, cxb3, cyb3 - 38, color="#ea580c", sw=2))

    f.append(fitbox(x3 + 15, y3 + 115, 325, 72, "Одночасний перескок електрона між іонами різної валентності (Mn³⁺/Mn⁴⁺).\nМожливий лише при ПАРАЛЕЛЬНИХ спінах катіонів!", size=10, color="#334155", fill="#ffffff", stroke="#cbd5e1"))

    # 4. Взаємодія РККЙ (RKKY Interaction)
    x4, y4 = 400, 265
    f.append(rect(x4, y4, w_box, h_box, fill="#f8fafc", stroke="#7c3aed", sw=1.5, rx=6))
    f.append(text(x4 + w_box / 2, y4 + 18, "4. Взаємодія РККЙ (RKKY)", size=12, bold=True, color="#6d28d9"))

    cxa4, cya4 = x4 + 75, y4 + 65
    cxb4, cyb4 = x4 + 280, y4 + 65
    f.append(circle(cxa4, cya4, 15, fill="#ede9fe", stroke="#7c3aed", sw=1.5))
    f.append(circle(cxb4, cyb4, 15, fill="#ede9fe", stroke="#7c3aed", sw=1.5))
    f.append(text(cxa4, cya4 + 4, "4f", size=11, bold=True, color="#5b21b6"))
    f.append(text(cxb4, cyb4 + 4, "4f", size=11, bold=True, color="#5b21b6"))

    # Осцилювальна хвиля електронів провідності
    pts_rkky_wave = []
    for px in range(int(cxa4 + 18), int(cxb4 - 18)):
        phi = (px - (cxa4 + 18)) / (cxb4 - cxa4 - 36) * 3 * math.pi
        py = cya4 - math.sin(phi) * 16
        pts_rkky_wave.append((px, py))
    d_rkky_w = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_rkky_wave)
    f.append(path_svg(d_rkky_w, stroke="#7c3aed", sw=1.8, dash="3,2"))

    f.append(fitbox(x4 + 15, y4 + 115, 325, 72, "Далекодійна осцилювальна взаємодія через море електронів провідності.\nПов'язує 4f-спіни рідкісноземельних металів.", size=10, color="#334155", fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(IMG_DIR, 'exchange-mechanisms.svg'), W, H, "\n".join(f))


# ── Фігура 3: Типи спинового впорядкування Гейзенберга ────────────────────────
def fig_heisenberg_spin_alignments():
    W, H = 780, 360
    f = []

    f.append(text(W / 2, 25, "Магнітні структури та типи спінового впорядкування", size=15, bold=True, color=INK))

    w_card = 170
    h_card = 270
    y_card = 55
    dx = 185

    # 1. Феромагнетик
    x1 = 20
    f.append(rect(x1, y_card, w_card, h_card, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    f.append(text(x1 + w_card / 2, y_card + 22, "Феромагнетик", size=12, bold=True, color="#1e40af"))
    f.append(text(x1 + w_card / 2, y_card + 40, "J > 0", size=12, bold=True, color="#2563eb"))

    # Спіновий ланцюжок
    for i in range(4):
        sy = y_card + 75 + i * 45
        f.append(circle(x1 + w_card / 2, sy, 10, fill="#3b82f6", stroke="#1d4ed8", sw=1))
        f.append(arrow(x1 + w_card / 2, sy + 15, x1 + w_card / 2, sy - 22, color="#1e40af", sw=2.5))
    f.append(text(x1 + w_card / 2, y_card + 250, "Паралельні\n↑ ↑ ↑ ↑", size=10, bold=True, color="#1e40af"))

    # 2. Антиферомагнетик
    x2 = x1 + dx
    f.append(rect(x2, y_card, w_card, h_card, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    f.append(text(x2 + w_card / 2, y_card + 22, "Антиферомагнетик", size=12, bold=True, color="#991b1b"))
    f.append(text(x2 + w_card / 2, y_card + 40, "J < 0", size=12, bold=True, color="#dc2626"))

    for i in range(4):
        sy = y_card + 75 + i * 45
        f.append(circle(x2 + w_card / 2, sy, 10, fill="#ef4444", stroke="#b91c1c", sw=1))
        if i % 2 == 0:
            f.append(arrow(x2 + w_card / 2, sy + 15, x2 + w_card / 2, sy - 22, color="#991b1b", sw=2.5))
        else:
            f.append(arrow(x2 + w_card / 2, sy - 15, x2 + w_card / 2, sy + 22, color="#991b1b", sw=2.5))
    f.append(text(x2 + w_card / 2, y_card + 250, "Антипаралельні\n↑ ↓ ↑ ↓", size=10, bold=True, color="#991b1b"))

    # 3. Ферримагнетик
    x3 = x2 + dx
    f.append(rect(x3, y_card, w_card, h_card, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6))
    f.append(text(x3 + w_card / 2, y_card + 22, "Ферримагнетик", size=12, bold=True, color="#9a3412"))
    f.append(text(x3 + w_card / 2, y_card + 40, "J < 0 (різні підґратки)", size=10, color="#ea580c"))

    for i in range(4):
        sy = y_card + 75 + i * 45
        f.append(circle(x3 + w_card / 2, sy, 10, fill="#f97316", stroke="#c2410c", sw=1))
        if i % 2 == 0:
            f.append(arrow(x3 + w_card / 2, sy + 18, x3 + w_card / 2, sy - 25, color="#9a3412", sw=3.0)) # Великий момент
        else:
            f.append(arrow(x3 + w_card / 2, sy - 10, x3 + w_card / 2, sy + 14, color="#9a3412", sw=1.8)) # Малий момент
    f.append(text(x3 + w_card / 2, y_card + 250, "Некомпенсовані\n↑ ⤓ ↑ ⤓", size=10, bold=True, color="#9a3412"))

    # 4. Скошений / Дзялошинського-Морія
    x4 = x3 + dx
    f.append(rect(x4, y_card, w_card, h_card, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    f.append(text(x4 + w_card / 2, y_card + 22, "Скошений / ДМІ", size=12, bold=True, color="#854d0e"))
    f.append(text(x4 + w_card / 2, y_card + 40, "D · (S₁ × S₂)", size=11, bold=True, color="#ca8a04"))

    for i in range(4):
        sy = y_card + 75 + i * 45
        cx_c = x4 + w_card / 2
        f.append(circle(cx_c, sy, 10, fill="#eab308", stroke="#a16207", sw=1))
        angle = (i - 1.5) * 0.35
        dx_a = math.sin(angle) * 22
        dy_a = math.cos(angle) * 22
        f.append(arrow(cx_c, sy, cx_c + dx_a, sy - dy_a, color="#854d0e", sw=2.5))
    f.append(text(x4 + w_card / 2, y_card + 250, "Неколінеарна\nспіраль / скірміон", size=10, bold=True, color="#854d0e"))

    render(os.path.join(IMG_DIR, 'heisenberg-spin-alignments.svg'), W, H, "\n".join(f))


# ── Фігура 4: Графік осциляцій обмінного інтеграла РККЙ ───────────────────────
def fig_rkky_oscillation():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 25, "Залежність інтеграла РККЙ-обміну J_RKKY(R) від відстані R", size=15, bold=True, color=INK))

    x0 = 80
    x_max = 680
    y0 = 200 # Вісь нульової енергії
    y_top = 65
    y_bot = 330

    # Осі координат
    f.append(arrow(x0 - 20, y0, x_max + 30, y0, color=INK, sw=1.5))
    f.append(text(x_max + 40, y0 + 4, "R", size=13, bold=True, italic=True, color=INK))

    f.append(arrow(x0, y_bot, x0, y_top - 15, color=INK, sw=1.5))
    f.append(text(x0 - 15, y_top - 15, "J_RKKY", size=12, bold=True, italic=True, color=INK))

    # Зони FM (J > 0) та AFM (J < 0)
    f.append(rect(x0 + 5, y_top + 10, x_max - x0 + 20, y0 - y_top - 10, fill="#eff6ff", stroke="none"))
    f.append(rect(x0 + 5, y0, x_max - x0 + 20, y_bot - y0, fill="#fef2f2", stroke="none"))
    
    f.append(text(x_max - 50, y0 - 55, "J > 0 (Феромагнітна зв'язність)", size=11, bold=True, color="#2563eb"))
    f.append(text(x_max - 50, y0 + 55, "J < 0 (Антиферомагнітна зв'язність)", size=11, bold=True, color="#dc2626"))

    # Побудова затухаючої осцилюючої кривої J_RKKY(x) ~ (x cos x - sin x) / x^4
    pts_rkky = []
    for px in range(15, x_max - x0):
        x_val = px / 32.0 # аргумент 2*kF*R
        if x_val < 0.1:
            val = 0.5
        else:
            val = (x_val * math.cos(x_val) - math.sin(x_val)) / (x_val**3.2) * 1.8
        
        py = y0 - val * 90
        py = max(y_top + 10, min(y_bot - 10, py))
        pts_rkky.append((x0 + px, py))

    d_rkky = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_rkky)
    f.append(path_svg(d_rkky, stroke="#7c3aed", sw=2.8))

    # Вертикальні пунктири періоду осциляцій λ_F / 2
    zeros_px = [int(4.49 * 32.0), int(7.72 * 32.0), int(10.90 * 32.0), int(14.06 * 32.0)]
    labels_z = ["π/2k_F", "3π/2k_F", "5π/2k_F", "7π/2k_F"]
    for idx, zx in enumerate(zeros_px):
        if x0 + zx < x_max:
            f.append(line(x0 + zx, y_top + 15, x0 + zx, y_bot - 10, color="#94a3b8", sw=1.2, dash="3,3"))
            f.append(text(x0 + zx, y0 + 16, labels_z[idx], size=10, bold=True, color="#475569"))

    f.append(fitbox(x0 + 180, y_bot - 45, 380, 40, "Період осциляцій визначається Фермі-імпульсом: λ_F / 2 = π / k_F.\nЗнакозмінна зв'язність дає спінове скло в розведених сплавах.", size=10, color="#1e293b", fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(IMG_DIR, 'rkky-oscillation.svg'), W, H, "\n".join(f))


def main():
    fig_coulomb_vs_exchange()
    fig_exchange_mechanisms()
    fig_heisenberg_spin_alignments()
    fig_rkky_oscillation()
    print("Фігури для exchange-interaction успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
