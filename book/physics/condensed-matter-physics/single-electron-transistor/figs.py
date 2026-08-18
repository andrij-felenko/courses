# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def path(d_str, stroke=INK, sw=1.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Схема одноелектронного транзистора та тунельних бар'єрів
# ════════════════════════════════════════════════════════════════════════════
def fig_set_structure():
    W, H = 840, 420
    f = []
    
    # Фони та розмежування панелей
    f.append(rect(10, 10, 405, 400, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    f.append(rect(425, 10, 405, 400, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    
    # ── Ліва панель: Електрична еквівалентна схема SET ──
    f.append(text(212, 35, "Електрична еквівалентна схема SET", size=14, bold=True, color=INK))
    
    # Електрод Витоку (Source)
    f.append(rect(30, 180, 80, 50, fill="#d6eaf8", stroke="#2980b9", sw=2, rx=4))
    f.append(text(70, 210, "Source", size=12, bold=True, color="#1b4f72"))
    f.append(text(70, 225, "V_ds / 2", size=10, color="#2980b9"))
    
    # Перший тунельний перехід (C1, R_T1)
    f.append(line(110, 205, 140, 205, color="#2980b9", sw=2))
    # Ємність C1
    f.append(line(140, 190, 140, 220, color="#e74c3c", sw=2.5))
    f.append(line(148, 190, 148, 220, color="#e74c3c", sw=2.5))
    f.append(line(148, 205, 180, 205, color="#2980b9", sw=2))
    f.append(text(144, 180, "C₁", size=11, bold=True, color="#c0392b"))
    f.append(text(144, 235, "R_T1", size=10, color="#7f8c8d"))
    
    # Квантовий острівець (Island)
    f.append(circle(220, 205, 38, fill="#fdebd0", stroke="#d35400", sw=2.5))
    f.append(text(220, 200, "Острівець", size=12, bold=True, color="#a04000"))
    f.append(text(220, 216, "Заряд: n·e", size=10.5, color="#7e5109"))
    
    # Другий тунельний перехід (C2, R_T2)
    f.append(line(258, 205, 290, 205, color="#2980b9", sw=2))
    # Ємність C2
    f.append(line(290, 190, 290, 220, color="#e74c3c", sw=2.5))
    f.append(line(298, 190, 298, 220, color="#e74c3c", sw=2.5))
    f.append(line(298, 205, 330, 205, color="#2980b9", sw=2))
    f.append(text(294, 180, "C₂", size=11, bold=True, color="#c0392b"))
    f.append(text(294, 235, "R_T2", size=10, color="#7f8c8d"))
    
    # Електрод Стоку (Drain)
    f.append(rect(330, 180, 70, 50, fill="#d6eaf8", stroke="#2980b9", sw=2, rx=4))
    f.append(text(365, 210, "Drain", size=12, bold=True, color="#1b4f72"))
    f.append(text(365, 225, "-V_ds / 2", size=10, color="#2980b9"))
    
    # Керувальний затвор (Gate) зверху
    f.append(rect(170, 60, 100, 35, fill="#e8daef", stroke="#8e44ad", sw=2, rx=4))
    f.append(text(220, 82, "Gate (V_g)", size=11.5, bold=True, color="#512e5f"))
    
    # Затворна ємність C_g
    f.append(line(220, 95, 220, 125, color="#8e44ad", sw=2))
    f.append(line(205, 125, 235, 125, color="#8e44ad", sw=2.5))
    f.append(line(205, 133, 235, 133, color="#8e44ad", sw=2.5))
    f.append(line(220, 133, 220, 167, color="#8e44ad", sw=2))
    f.append(text(248, 130, "C_g", size=11.5, bold=True, color="#6c3483"))
    
    # Загальне пояснення ємності
    f.append(rect(30, 275, 365, 120, fill="#f2f4f4", stroke="#bdc3c7", sw=1, rx=4))
    f.append(text(212, 295, "Параметри та умови функціонування:", size=11, bold=True, color=INK))
    f.append(text(45, 318, "• Повна ємність: C_Σ = C₁ + C₂ + C_g", size=10.5, color=DARK, anchor="start"))
    f.append(text(45, 338, "• Кулонівська енергія: E_C = e² / (2 C_Σ)", size=10.5, color=DARK, anchor="start"))
    f.append(text(45, 358, "• Термічна умова: E_C >> k_B · T", size=10.5, color=DARK, anchor="start"))
    f.append(text(45, 378, "• Квантова умова: R_T1, R_T2 >> h / e² ≈ 25.8 кОм", size=10.5, color=DARK, anchor="start"))
    
    # ── Права панель: Потенціальний профіль та тунелювання ──
    f.append(text(627, 35, "Енергетичний профіль системи", size=14, bold=True, color=INK))
    
    # Фермі-рівень Витоку (Source)
    f.append(rect(445, 140, 75, 130, fill="#d6eaf8", stroke="#2980b9", sw=2))
    f.append(line(445, 190, 520, 190, color="#1b4f72", sw=2, dash="4 2"))
    f.append(text(482, 182, "E_FS", size=11, bold=True, color="#1b4f72"))
    f.append(text(482, 215, "Source", size=11, color="#2980b9"))
    
    # Перший тунельний бар'єр
    f.append(rect(520, 100, 25, 210, fill="#fadbd8", stroke="#e74c3c", sw=1.5))
    f.append(text(532, 205, "Бар'єр 1", size=9.5, color="#c0392b"))
    
    # Острівець з дискретними рівнями енергії
    f.append(rect(545, 130, 90, 150, fill="#fef9e7", stroke="#f39c12", sw=2))
    f.append(text(590, 148, "Острівець", size=11, bold=True, color="#d35400"))
    
    # Рівні зарядових станів N, N+1
    f.append(line(555, 240, 625, 240, color="#27ae60", sw=2))
    f.append(text(590, 232, "E(N)", size=10.5, bold=True, color="#1e8449"))
    
    f.append(line(555, 175, 625, 175, color="#e67e22", sw=2))
    f.append(text(590, 167, "E(N+1)", size=10.5, bold=True, color="#d35400"))
    
    # Двосторонній стрелочний вимір Кулонівської щілини E_C
    f.append(line(565, 177, 565, 238, color="#c0392b", sw=1.5, dash="2 2"))
    f.append(text(550, 210, "E_C", size=11, bold=True, color="#c0392b"))
    
    # Другий тунельний бар'єр
    f.append(rect(635, 100, 25, 210, fill="#fadbd8", stroke="#e74c3c", sw=1.5))
    f.append(text(647, 205, "Бар'єр 2", size=9.5, color="#c0392b"))
    
    # Фермі-рівень Стоку (Drain)
    f.append(rect(660, 150, 75, 120, fill="#d6eaf8", stroke="#2980b9", sw=2))
    f.append(line(660, 200, 735, 200, color="#1b4f72", sw=2, dash="4 2"))
    f.append(text(697, 192, "E_FD", size=11, bold=True, color="#1b4f72"))
    f.append(text(697, 225, "Drain", size=11, color="#2980b9"))
    
    # Стрілка тунелювання електронів
    f.append(line(490, 175, 545, 175, color="#27ae60", sw=2))
    f.append(polygon([(545, 175), (537, 170), (537, 180)], fill="#27ae60"))
    f.append(text(515, 163, "e⁻ тунелювання", size=9.5, bold=True, color="#27ae60"))
    
    # Пояснення режимів справа
    f.append(rect(445, 320, 375, 75, fill="#ebf5fb", stroke="#7fb3d5", sw=1, rx=4))
    f.append(text(632, 340, "Кулонівське блокування перенесення:", size=10.5, bold=True, color="#1b4f72"))
    f.append(text(455, 360, "Заряд додається тільки дискретними квантами e.", size=10, color=DARK, anchor="start"))
    f.append(text(455, 378, "При E_FS < E(N+1) тунелювання заборонене закон. збереження.", size=10, color=DARK, anchor="start"))
    
    render(os.path.join(OUT, "single-electron-transistor-structure.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Діаграма стабільності: Ромби Кулона та осциляції провідності
# ════════════════════════════════════════════════════════════════════════════
def fig_coulomb_diamonds():
    W, H = 840, 440
    f = []
    
    f.append(rect(10, 10, 520, 420, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    f.append(rect(545, 10, 285, 420, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    
    # ── Ліва панель: Площина (V_g, V_ds) з ромбами Кулона ──
    f.append(text(265, 35, "Діаграма стабільності: Ромби Кулона", size=14, bold=True, color=INK))
    
    # Осі координат
    ox, oy = 60, 220
    f.append(line(40, oy, 490, oy, color=DARK, sw=1.5)) # Вісь V_g
    f.append(polygon([(495, oy), (485, oy - 5), (485, oy + 5)], fill=DARK))
    f.append(text(475, oy + 22, "V_g", size=12, bold=True, color=INK))
    
    f.append(line(ox, 390, ox, 60, color=DARK, sw=1.5)) # Вісь V_ds
    f.append(polygon([(ox, 55), (ox - 5, 65), (ox + 5, 65)], fill=DARK))
    f.append(text(ox - 25, 70, "V_ds", size=12, bold=True, color=INK))
    
    # Ромби Кулона (Coulomb Diamonds)
    # Ромб 1 (N - 1 електронів)
    d1 = [(60, 220), (130, 130), (200, 220), (130, 310)]
    f.append(polygon(d1, fill="#ebf5fb", stroke="#2980b9", sw=2))
    f.append(text(130, 225, "N - 1", size=13, bold=True, color="#1b4f72"))
    f.append(text(130, 243, "I_ds = 0", size=10.5, color="#5499c7"))
    
    # Ромб 2 (N електронів)
    d2 = [(200, 220), (270, 130), (340, 220), (270, 310)]
    f.append(polygon(d2, fill="#e8f8f5", stroke="#16a085", sw=2))
    f.append(text(270, 225, "N", size=13, bold=True, color="#0e6251"))
    f.append(text(270, 243, "I_ds = 0", size=10.5, color="#16a085"))
    
    # Ромб 3 (N + 1 електронів)
    d3 = [(340, 220), (410, 130), (480, 220), (410, 310)]
    f.append(polygon(d3, fill="#fef9e7", stroke="#f39c12", sw=2))
    f.append(text(410, 225, "N + 1", size=13, bold=True, color="#7e5109"))
    f.append(text(410, 243, "I_ds = 0", size=10.5, color="#f39c12"))
    
    # Позначення меж ромбів та нахилів
    f.append(line(200, 220, 270, 130, color="#c0392b", sw=2))
    f.append(text(220, 160, "dV_ds/dV_g = -C_g/C₁", size=10, bold=True, color="#c0392b"))
    
    f.append(line(270, 130, 340, 220, color="#8e44ad", sw=2))
    f.append(text(310, 160, "C_g/(C₁+C₂+C_g)", size=10, bold=True, color="#8e44ad"))
    
    # Висота ромба (Кулонівська щілина)
    f.append(line(270, 130, 270, 310, color="#e74c3c", sw=1.5, dash="3 3"))
    f.append(text(278, 145, "e / C_Σ", size=11, bold=True, color="#c0392b"))
    
    # Період осциляцій по затвору
    f.append(line(200, 335, 340, 335, color="#16a085", sw=1.5))
    f.append(line(200, 328, 200, 342, color="#16a085", sw=1.5))
    f.append(line(340, 328, 340, 342, color="#16a085", sw=1.5))
    f.append(text(270, 355, "ΔV_g = e / C_g", size=11, bold=True, color="#16a085"))
    
    # Провідна зона поза ромбами (струм протікає)
    f.append(text(270, 95, "Зона провідності (I_ds ≠ 0)", size=11, bold=True, color="#c0392b"))
    f.append(text(270, 385, "Зона провідності (I_ds ≠ 0)", size=11, bold=True, color="#c0392b"))
    
    # ── Права панель: Кулонівські осциляції провідності G(V_g) ──
    f.append(text(685, 35, "Кулонівські осциляції G(V_g)", size=14, bold=True, color=INK))
    f.append(text(685, 55, "При малій напрузі V_ds -> 0", size=11, color=MUTED))
    
    # Осі графіка провідності
    gx, gy = 580, 340
    f.append(line(gx, gy, 810, gy, color=DARK, sw=1.5))
    f.append(polygon([(815, gy), (805, gy - 4), (805, gy + 4)], fill=DARK))
    f.append(text(800, gy + 20, "V_g", size=11, bold=True, color=INK))
    
    f.append(line(gx, gy, gx, 90, color=DARK, sw=1.5))
    f.append(polygon([(gx, 85), (gx - 4, 95), (gx + 4, 95)], fill=DARK))
    f.append(text(gx - 20, 100, "G", size=11, bold=True, color=INK))
    
    # Крива осциляцій провідності (піки при виродженні n_g = N + 1/2)
    # Рівні V_g відповідають вершинам ромбів: 60, 200, 340, 480 -> масштабовані до праву панель
    # Затворні токи виродження: x1 = 635, x2 = 705, x3 = 775
    peak_path = (
        "M 580,338 Q 610,338 625,320 Q 635,110 645,320 Q 660,338 695,338 "
        "Q 710,320 720,110 Q 730,320 765,338 Q 780,320 790,110 Q 800,320 810,338"
    )
    f.append(path(peak_path, stroke="#27ae60", sw=2.5, fill="none"))
    
    # Вершини піків провідності
    for px, label in [(640, "N-1 <-> N"), (720, "N <-> N+1"), (790, "N+1 <-> N+2")]:
        f.append(circle(px, 115, 3.5, fill="#e74c3c", stroke="#922b21", sw=1))
        f.append(text(px, 95, label, size=9.5, bold=True, color="#c0392b"))
    
    f.append(rect(570, 365, 245, 55, fill="#f2f4f4", stroke="#bdc3c7", sw=1, rx=4))
    f.append(text(692, 383, "Піки спостерігаються при:", size=10, bold=True, color=INK))
    f.append(text(692, 403, "C_g · V_g = (N + 1/2) · e", size=10.5, bold=True, color="#27ae60"))
    
    render(os.path.join(OUT, "coulomb-diamonds-stability.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Порівняння дискретизації рівня квантового та класичного острівців
# ════════════════════════════════════════════════════════════════════════════
def fig_coulomb_energy_levels():
    W, H = 840, 380
    f = []
    
    f.append(rect(10, 10, 405, 360, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    f.append(rect(425, 10, 405, 360, fill="#fcfcfc", stroke="#d5dbdb", sw=1.5, rx=6))
    
    # ── Ліва панель: Класичний металевий острівець (ΔE_level << k_B T) ──
    f.append(text(212, 35, "Металевий острівець (Класична межа)", size=13.5, bold=True, color=INK))
    f.append(text(212, 55, "Неперервний квантовий спектр носіїв", size=11, color=MUTED))
    
    # Енергетична зона з густим континуумом станів
    f.append(rect(60, 90, 305, 200, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=4))
    for y in range(105, 280, 8):
        f.append(line(75, y, 350, y, color="#a9cce3", sw=1))
    
    # Кулонівський гап E_C між зарядовими станами N та N+1
    f.append(rect(60, 165, 305, 50, fill="#fadbd8", stroke="#e74c3c", sw=1.5))
    f.append(text(212, 195, "Кулонівська щілина E_C = e² / (2 C_Σ)", size=11.5, bold=True, color="#c0392b"))
    
    f.append(text(212, 315, "Особливості транспорту:", size=10.5, bold=True, color=INK))
    f.append(text(212, 335, "Відстань між рівнями ΔE << k_B T, домінує E_C", size=10, color=DARK))
    
    # ── Права панель: Полупровідникова квантова точка (ΔE_level ~ E_C) ──
    f.append(text(627, 35, "Квантова точка (Квантово-розмірна межа)", size=13.5, bold=True, color=INK))
    f.append(text(627, 55, "Дискретні квантові рівні енергії (0D)", size=11, color=MUTED))
    
    f.append(rect(475, 90, 305, 200, fill="#fef9e7", stroke="#f39c12", sw=2, rx=4))
    
    # Дискретні рівні енергії 1s, 1p, 1d...
    levels = [
        (260, "1s стан", "#27ae60"),
        (225, "1p стан", "#27ae60"),
        (160, "2s стан (Заряд N+1)", "#d35400"),
        (115, "2p стан", "#d35400")
    ]
    for ly, label, col in levels:
        f.append(line(495, ly, 760, ly, color=col, sw=2.5))
        f.append(text(627, ly - 8, label, size=10.5, bold=True, color=col))
    
    # Показуємо додавання енергій E_C та ΔE_level
    f.append(line(520, 225, 520, 160, color="#c0392b", sw=1.5, dash="3 3"))
    f.append(text(505, 195, "E_C + ΔE", size=10.5, bold=True, color="#c0392b"))
    
    f.append(text(627, 315, "Особливості транспорту:", size=10.5, bold=True, color=INK))
    f.append(text(627, 335, "Повна енергія додання: E_add = E_C + ΔE_level", size=10, color=DARK))
    
    render(os.path.join(OUT, "coulomb-blockade-energy.svg"), W, H, *f)

if __name__ == "__main__":
    fig_set_structure()
    fig_coulomb_diamonds()
    fig_coulomb_energy_levels()
    print("Згенеровано фігури для single-electron-transistor в ./img/")
