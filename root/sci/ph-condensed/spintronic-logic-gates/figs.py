# -*- coding: utf-8 -*-
"""Фігури до теми «Спінтронні логічні елементи та інтерферометри».
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

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Спіновий польовий транзистор Датта — Даса ───────────────────────
def fig_datta_das_transistor():
    W, H = 800, 420
    f = []

    f.append(text(W / 2, 28, "Спіновий польовий транзистор Датта — Даса (Datta-Das Spin-FET)", size=16, bold=True, color=INK))

    # Top panel: Device schematic
    y0 = 60
    # FM Source
    f.append(rect(40, y0 + 60, 110, 110, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    f.append(text(95, y0 + 85, "FM Витік", size=13, bold=True, color="#1e40af"))
    f.append(text(95, y0 + 102, "(Інжектор)", size=11, color="#1e40af"))
    f.append(arrow(95, y0 + 155, 95, y0 + 118, color="#1d4ed8", sw=3))
    f.append(text(95, y0 + 163, "M_S (↑)", size=11, bold=True, color="#1d4ed8"))

    # Channel (2DEG)
    f.append(rect(150, y0 + 90, 500, 50, fill="#fef3c7", stroke="#d97706", sw=2, rx=2))
    f.append(text(400, y0 + 120, "2DEG Канал (InAs / InGaAs) — взаємодія Рашби α_R", size=12, bold=True, color="#b45309"))

    # Gate electrode
    f.append(rect(300, y0 + 20, 200, 50, fill="#f3e8ff", stroke="#7e22ce", sw=2, rx=4))
    f.append(text(400, y0 + 42, "Затвор (V_g)", size=13, bold=True, color="#6b21a8"))
    f.append(text(400, y0 + 58, "Керує полем Рашби B_R", size=10, italic=True, color="#6b21a8"))
    f.append(arrow(400, y0 + 70, 400, y0 + 90, color="#7e22ce", sw=2))

    # FM Drain
    f.append(rect(650, y0 + 60, 110, 110, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    f.append(text(705, y0 + 85, "FM Стік", size=13, bold=True, color="#1e40af"))
    f.append(text(705, y0 + 102, "(Аналізатор)", size=11, color="#1e40af"))
    f.append(arrow(705, y0 + 155, 705, y0 + 118, color="#1d4ed8", sw=3))
    f.append(text(705, y0 + 163, "M_D (↑)", size=11, bold=True, color="#1d4ed8"))

    # Precessing electron spin trajectories in channel
    f.append(text(400, y0 + 185, "Прецесія спінів уздовж каналу довжиною L", size=12, bold=True, color=INK))

    # Sub-panels for ON and OFF state comparison
    y_sub = y0 + 200

    # ON State box
    f.append(rect(40, y_sub, 340, 125, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    f.append(text(210, y_sub + 20, "Стан ВВІМКНЕНО (Логічне 1)", size=13, bold=True, color="#15803d"))
    f.append(text(210, y_sub + 38, "Δθ = 2π (V_g = V_ON) → Спін паралельний M_D", size=11, color="#166534"))

    # Spin precession arrows inside ON box
    on_spins = [(70, 0), (130, 60), (190, 180), (250, 270), (310, 360)]
    for sx, angle_deg in on_spins:
        cx = 60 + sx
        cy = y_sub + 75
        rad = math.radians(angle_deg)
        dx = 16 * math.sin(rad)
        dy = -16 * math.cos(rad)
        f.append(circle(cx, cy, 4, fill="#15803d", stroke="none"))
        f.append(arrow(cx, cy, cx + dx, cy + dy, color="#15803d", sw=2))

    f.append(text(210, y_sub + 110, "Низький опір → Високий струм I_ON", size=11, bold=True, color="#15803d"))

    # OFF State box
    f.append(rect(420, y_sub, 340, 125, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    f.append(text(590, y_sub + 20, "Стан ВИМКНЕНО (Логічне 0)", size=13, bold=True, color="#b91c1c"))
    f.append(text(590, y_sub + 38, "Δθ = π (V_g = V_OFF) → Спін антипаралельний M_D", size=11, color="#991b1b"))

    off_spins = [(70, 0), (130, 45), (190, 90), (250, 135), (310, 180)]
    for sx, angle_deg in off_spins:
        cx = 440 + sx
        cy = y_sub + 75
        rad = math.radians(angle_deg)
        dx = 16 * math.sin(rad)
        dy = -16 * math.cos(rad)
        f.append(circle(cx, cy, 4, fill="#b91c1c", stroke="none"))
        f.append(arrow(cx, cy, cx + dx, cy + dy, color="#b91c1c", sw=2))

    f.append(text(590, y_sub + 110, "Високий опір → Низький струм I_OFF", size=11, bold=True, color="#b91c1c"))

    f.append(text(W / 2, H - 12, "Модуляція ефективного поля Рашби B_R затвором V_g керує кутом прецесії спіну Δθ", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'datta-das-transistor.svg'), W, H, "\n".join(f))

# ── Фігура 2: Наномагнітний мажоритарний логічний елемент ────────────────────
def fig_spin_majority_gate():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 26, "Спіновий мажоритарний логічний елемент (Majority Gate) для AND/OR", size=16, bold=True, color=INK))

    p_w = 400
    p_h = 310
    x0, y0 = 30, 50

    f.append(rect(x0, y0, p_w, p_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x0 + p_w / 2, y0 + 22, "Наномагнітна мажоритарна комірка", size=13, bold=True, color=INK))

    # Input A (Top-Left)
    f.append(rect(x0 + 40, y0 + 60, 70, 50, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    f.append(text(x0 + 75, y0 + 80, "Вхід A", size=12, bold=True, color="#1e40af"))
    f.append(arrow(x0 + 75, y0 + 100, x0 + 75, y0 + 68, color="#1d4ed8", sw=2.5))
    f.append(text(x0 + 75, y0 + 102, "M_A", size=10, bold=True, color="#1d4ed8"))

    # Input B (Bottom-Left)
    f.append(rect(x0 + 40, y0 + 200, 70, 50, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    f.append(text(x0 + 75, y0 + 220, "Вхід B", size=12, bold=True, color="#1e40af"))
    f.append(arrow(x0 + 75, y0 + 240, x0 + 75, y0 + 208, color="#1d4ed8", sw=2.5))
    f.append(text(x0 + 75, y0 + 242, "M_B", size=10, bold=True, color="#1d4ed8"))

    # Input C (Control input, Left-Center)
    f.append(rect(x0 + 40, y0 + 130, 70, 50, fill="#fef3c7", stroke="#d97706", sw=2, rx=4))
    f.append(text(x0 + 75, y0 + 148, "Вхід C", size=12, bold=True, color="#b45309"))
    f.append(text(x0 + 75, y0 + 164, "(Керування)", size=10, color="#b45309"))

    # Coupling arrows / lines to Central Node
    f.append(path_svg(f"M {x0 + 110} {y0 + 85} L {x0 + 190} {y0 + 140}", stroke="#94a3b8", sw=2, dash="3,3"))
    f.append(path_svg(f"M {x0 + 110} {y0 + 155} L {x0 + 190} {y0 + 155}", stroke="#d97706", sw=2, dash="3,3"))
    f.append(path_svg(f"M {x0 + 110} {y0 + 225} L {x0 + 190} {y0 + 170}", stroke="#94a3b8", sw=2, dash="3,3"))

    # Central Sum Node
    f.append(circle(x0 + 210, y0 + 155, 30, fill="#e0e7ff", stroke="#4338ca", sw=2))
    f.append(text(x0 + 210, y0 + 152, "Вузол", size=11, bold=True, color="#3730a3"))
    f.append(text(x0 + 210, y0 + 166, "сумування", size=10, color="#3730a3"))

    # Dipolar / Spin Torque arrow to Output
    f.append(arrow(x0 + 240, y0 + 155, x0 + 290, y0 + 155, color="#4338ca", sw=2.5))
    f.append(text(x0 + 265, y0 + 145, "M_net", size=10, bold=True, color="#4338ca"))

    # Output Nanomagnet Y
    f.append(rect(x0 + 270, y0 + 130, 105, 50, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=4))
    f.append(text(x0 + 322, y0 + 152, "Вихід Y", size=12, bold=True, color="#15803d"))
    f.append(text(x0 + 322, y0 + 168, "Maj(A,B,C)", size=10, bold=True, color="#15803d"))

    f.append(text(x0 + p_w / 2, y0 + p_h - 20, "Магнітне дипольне зчеплення або спіновий струм", size=11, italic=True, color=MUTED))

    # Right: Logic equations & programming table
    x_r, y_r = 460, 50
    w_r, h_r = 290, 310

    f.append(rect(x_r, y_r, w_r, h_r, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    f.append(text(x_r + w_r / 2, y_r + 22, "Логічна функція та режим", size=13, bold=True, color="#7e22ce"))

    # Equation box
    f.append(rect(x_r + 15, y_r + 45, w_r - 30, 45, fill="#ffffff", stroke="#c084fc", sw=1, rx=4))
    f.append(text(x_r + w_r / 2, y_r + 65, "Y = A·B + B·C + A·C", size=13, bold=True, color="#6b21a8"))
    f.append(text(x_r + w_r / 2, y_r + 80, "(Мажоритарна більшість від 3 входів)", size=10, color=MUTED))

    # Sub-box 1: AND mode
    f.append(rect(x_r + 15, y_r + 105, w_r - 30, 80, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    f.append(text(x_r + w_r / 2, y_r + 125, "Режим AND (Вентиль І):", size=12, bold=True, color="#1d4ed8"))
    f.append(text(x_r + w_r / 2, y_r + 145, "Вхід C = 0 (намагніченість ↓)", size=11, color="#1e40af"))
    f.append(text(x_r + w_r / 2, y_r + 165, "Y = A·B + B·0 + A·0 = A · B", size=12, bold=True, color="#1d4ed8"))

    # Sub-box 2: OR mode
    f.append(rect(x_r + 15, y_r + 195, w_r - 30, 80, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    f.append(text(x_r + w_r / 2, y_r + 215, "Режим OR (Вентиль АБО):", size=12, bold=True, color="#15803d"))
    f.append(text(x_r + w_r / 2, y_r + 235, "Вхід C = 1 (намагніченість ↑)", size=11, color="#166534"))
    f.append(text(x_r + w_r / 2, y_r + 255, "Y = A·B + B·1 + A·1 = A + B", size=12, bold=True, color="#15803d"))

    f.append(text(x_r + w_r / 2, y_r + h_r - 12, "Програмування вентиля зміною сигналу C", size=10, italic=True, color=MUTED))

    f.append(text(W / 2, H - 12, "Один спіновий елемент виконує реконфігуровні логічні операції AND/OR без перебудови структури", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-majority-gate.svg'), W, H, "\n".join(f))

# ── Фігура 3: Магнонний інтерферометричний елемент ───────────────────────────
def fig_magnonic_interferometer():
    W, H = 800, 440
    f = []

    f.append(text(W / 2, 26, "Магнонний інтерферометр Маха — Цендера (Хвильова логіка XOR / AND)", size=16, bold=True, color=INK))

    y0 = 60
    # Input generator / Microstrip antenna
    f.append(rect(30, y0 + 70, 90, 100, fill="#fef3c7", stroke="#d97706", sw=2, rx=4))
    f.append(text(75, y0 + 95, "Збудник", size=12, bold=True, color="#b45309"))
    f.append(text(75, y0 + 110, "магнонів", size=12, bold=True, color="#b45309"))
    f.append(text(75, y0 + 130, "Мікросмужкова", size=10, color="#b45309"))
    f.append(text(75, y0 + 145, "антена / SOT", size=10, color="#b45309"))

    # YIG Waveguide Y-Splitter
    f.append(path_svg(f"M 120 {y0 + 120} L 200 {y0 + 120}", stroke="#0284c7", sw=12))
    f.append(path_svg(f"M 200 {y0 + 120} Q 230 {y0 + 50} 280 {y0 + 50} L 520 {y0 + 50} Q 570 {y0 + 50} 600 {y0 + 120}", stroke="#0284c7", sw=10))
    f.append(path_svg(f"M 200 {y0 + 120} Q 230 {y0 + 190} 280 {y0 + 190} L 520 {y0 + 190} Q 570 {y0 + 190} 600 {y0 + 120}", stroke="#0284c7", sw=10))
    f.append(path_svg(f"M 600 {y0 + 120} L 680 {y0 + 120}", stroke="#0284c7", sw=12))

    # YIG Waveguide label inside top arm
    f.append(text(400, y0 + 35, "Плече 1 (Магнонний хвилевід YIG / FeGa)", size=11, bold=True, color="#0369a1"))
    f.append(text(400, y0 + 205, "Плече 2 (Опорне плече, фаза φ_0)", size=11, bold=True, color="#0369a1"))

    # Phase Gate on Arm 1
    f.append(rect(340, y0 + 62, 120, 45, fill="#f3e8ff", stroke="#7e22ce", sw=2, rx=4))
    f.append(text(400, y0 + 82, "Фазовий затвор", size=11, bold=True, color="#6b21a8"))
    f.append(text(400, y0 + 97, "H_gate / VCMA (Δφ)", size=10, color="#6b21a8"))

    # Output Detector / Sensor
    f.append(rect(680, y0 + 70, 90, 100, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    f.append(text(725, y0 + 95, "Детектор", size=12, bold=True, color="#1e40af"))
    f.append(text(725, y0 + 110, "сигналу", size=12, bold=True, color="#1e40af"))
    f.append(text(725, y0 + 130, "Індуктивна", size=10, color="#1e40af"))
    f.append(text(725, y0 + 145, "петля / ISHE", size=10, color="#1e40af"))

    # Spin wave ripples drawing
    for xw in range(220, 330, 20):
        f.append(path_svg(f"M {xw} {y0 + 40} Q {xw + 5} {y0 + 50} {xw + 10} {y0 + 60}", stroke="#e0f2fe", sw=2))
    for xw in range(470, 580, 20):
        f.append(path_svg(f"M {xw} {y0 + 40} Q {xw + 5} {y0 + 50} {xw + 10} {y0 + 60}", stroke="#fae8ff", sw=2))
    for xw in range(220, 580, 25):
        f.append(path_svg(f"M {xw} {y0 + 180} Q {xw + 6} {y0 + 190} {xw + 12} {y0 + 200}", stroke="#e0f2fe", sw=2))

    # Bottom comparison
    y_b = y0 + 235

    # Box 1: Constructive (Logic 1)
    f.append(rect(40, y_b, 340, 115, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    f.append(text(210, y_b + 20, "Конструктивна інтерференція (Δφ = 0, 2π)", size=12, bold=True, color="#15803d"))
    pts_c = []
    for px in range(260):
        rad = (px / 260.0) * 4 * math.pi
        py = y_b + 65 - 22 * math.sin(rad)
        pts_c.append((80 + px, py))
    d_c = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_c)
    f.append(path_svg(d_c, stroke="#16a34a", sw=2.5))
    f.append(text(210, y_b + 100, "Максимальна амплітуда → Вихідний стан 1", size=11, bold=True, color="#15803d"))

    # Box 2: Destructive (Logic 0)
    f.append(rect(420, y_b, 340, 115, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    f.append(text(590, y_b + 20, "Деструктивна інтерференція (Δφ = π)", size=12, bold=True, color="#b91c1c"))
    f.append(path_svg(f"M 460 {y_b + 65} L 720 {y_b + 65}", stroke="#b91c1c", sw=2.5, dash="4,4"))
    f.append(text(590, y_b + 100, "Нульова амплітуда → Вихідний стан 0", size=11, bold=True, color="#b91c1c"))

    f.append(text(W / 2, H - 12, "Інтерференція магнонних хвиль реалізує логіку XOR та AND без Джоулевих втрат на перенос заряду", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'magnonic-interferometer.svg'), W, H, "\n".join(f))

def main():
    fig_datta_das_transistor()
    fig_spin_majority_gate()
    fig_magnonic_interferometer()
    print("Spintronic logic figures successfully generated in ./img/")

if __name__ == '__main__':
    main()
