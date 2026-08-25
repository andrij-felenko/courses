# -*- coding: utf-8 -*-
"""Фігури до теми «Тепловий ланцюжок: θJC, θCS, θSA» та її вставок.
Генератор SVG на базі svgkit (AUTHORING §5).
Усі підписи без номерів і без «Рис.». Шляхи від кореня репо.
"""
import sys, os, math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), color, sw, d))


def fig_thermal_chain_stack():
    """Послідовний тепловий ланцюжок: фізична структура напівпровідника та еквівалентна схема."""
    W, H = 860, 480
    f = []

    # Заголовок / розділювачі зон
    f.append(text(210, 32, "Фізична структура збірки", size=15, bold=True, color=INK))
    f.append(text(640, 32, "Електротеплова еквівалентна схема", size=15, bold=True, color=INK))
    f.append(line(425, 20, 425, 460, color=LINE, sw=1.0, dash="4,4"))

    # ── Ліва частина: Фізичні шари (знизу вгору або зверху вниз)
    # Кристал (Junction / Die)
    f.append(rect(100, 60, 220, 36, fill="#ffcccc", stroke=POS, sw=1.8, rx=4))
    f.append(text(210, 83, "Кристал кремнію (Junction, Tj)", size=12, bold=True, color=POS))

    # Die attach (припій / клей)
    f.append(rect(120, 96, 180, 16, fill="#e0e0e0", stroke=LINE, sw=1.2, rx=2))
    f.append(text(210, 108, "Die attach (припій / компаунд)", size=10, color=MUTED))

    # Мідний фланець корпусу (Case)
    f.append(rect(70, 112, 280, 50, fill="#ffe0b2", stroke="#e65100", sw=1.8, rx=4))
    f.append(text(210, 137, "Мідна основа корпусу (Case, Tc)", size=12, bold=True, color="#bf360c"))
    f.append(text(210, 153, "Тепловий фланець TO-220 / D2PAK", size=10, color=MUTED))

    # Термоінтерфейс (TIM)
    f.append(rect(50, 162, 320, 24, fill="#b2dfdb", stroke="#00695c", sw=1.5, rx=3))
    f.append(text(210, 178, "Термоінтерфейс TIM (паста / прокладка)", size=11, bold=True, color="#004d40"))

    # Радіатор (Heatsink)
    # Основа радіатора
    f.append(rect(30, 186, 360, 45, fill="#cfd8dc", stroke="#37474f", sw=1.8, rx=4))
    f.append(text(210, 212, "Алюмінієвий радіатор (Sink, Ts)", size=12, bold=True, color="#263238"))

    # Ребра радіатора (Fins)
    fin_x = [45, 95, 145, 195, 245, 295, 345]
    for x in fin_x:
        f.append(rect(x, 231, 26, 85, fill="#cfd8dc", stroke="#37474f", sw=1.5, rx=2))

    # Повітряні потоки (Ambient) знизу
    f.append(arrow(110, 365, 110, 322, color=NEG, sw=1.6))
    f.append(arrow(210, 365, 210, 322, color=NEG, sw=1.6))
    f.append(arrow(310, 365, 310, 322, color=NEG, sw=1.6))
    f.append(text(210, 390, "Конвекція та випромінювання у повітря", size=11, color=NEG, bold=True))
    f.append(text(210, 412, "Навколишнє середовище (Ambient, Ta)", size=12, bold=True, color=NEG))

    # Тепловий потік стрілкою вниз
    f.append(arrow(24, 70, 24, 410, color=POS, sw=2.5))
    f.append(text(20, 240, "Потік Pd", size=12, bold=True, color=POS, anchor="end"))

    # ── Права частина: Електрична схема теплового закону Ома
    # Джерело тепла Pd (генератор струму)
    f.append(circle(640, 75, 22, fill="#fff3e0", stroke=POS, sw=2.0))
    f.append(arrow(640, 88, 640, 62, color=POS, sw=2.0))
    f.append(text(595, 78, "Pd [Вт]", size=13, bold=True, color=POS, anchor="end"))

    # Вузол Tj
    f.append(circle(640, 120, 4.5, fill=POS, stroke=POS, sw=1.0))
    f.append(line(640, 97, 640, 135, color=INK, sw=2.0))
    f.append(text(660, 124, "Tj (кристал)", size=12, bold=True, color=POS, anchor="start"))

    # Опір θJC
    f.append(rect(610, 135, 60, 45, fill="#fbe9e7", stroke=POS, sw=1.8, rx=4))
    f.append(text(640, 162, "θJC", size=13, bold=True, color=POS))
    f.append(text(685, 162, "Junction-to-Case", size=11, color=MUTED, anchor="start"))

    # Вузол Tc
    f.append(line(640, 180, 640, 215, color=INK, sw=2.0))
    f.append(circle(640, 200, 4.5, fill="#e65100", stroke="#e65100", sw=1.0))
    f.append(text(660, 204, "Tc (корпус / фланець)", size=12, bold=True, color="#bf360c", anchor="start"))

    # Опір θCS
    f.append(rect(610, 215, 60, 45, fill="#e0f2f1", stroke="#00695c", sw=1.8, rx=4))
    f.append(text(640, 242, "θCS", size=13, bold=True, color="#004d40"))
    f.append(text(685, 242, "Case-to-Sink (TIM)", size=11, color=MUTED, anchor="start"))

    # Вузол Ts
    f.append(line(640, 260, 640, 295, color=INK, sw=2.0))
    f.append(circle(640, 280, 4.5, fill="#37474f", stroke="#37474f", sw=1.0))
    f.append(text(660, 284, "Ts (радіатор)", size=12, bold=True, color="#263238", anchor="start"))

    # Опір θSA
    f.append(rect(610, 295, 60, 45, fill="#e8eaf6", stroke=NEG, sw=1.8, rx=4))
    f.append(text(640, 322, "θSA", size=13, bold=True, color=NEG))
    f.append(text(685, 322, "Sink-to-Ambient", size=11, color=MUTED, anchor="start"))

    # Вузол Ta і заземлення (опорна температура)
    f.append(line(640, 340, 640, 385, color=INK, sw=2.0))
    f.append(circle(640, 370, 4.5, fill=NEG, stroke=NEG, sw=1.0))
    f.append(text(660, 374, "Ta (повітря навколо)", size=12, bold=True, color=NEG, anchor="start"))

    # Символ опорної температури (земля)
    f.append(line(615, 385, 665, 385, color=LINE, sw=2.0))
    f.append(line(625, 392, 655, 392, color=LINE, sw=1.8))
    f.append(line(633, 399, 647, 399, color=LINE, sw=1.5))

    # Підсумок формули внизу праворуч
    f.append(rect(470, 420, 350, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(645, 445, "Tj = Ta + Pd · (θJC + θCS + θSA) ≤ Tj(max)", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "thermal-chain-stack.svg"), W, H, *f)


def fig_smd_thermal_pcb():
    """Тепловий шлях SMD-компонента на платі: thermal pad, перехідні отвори та мідні полігони."""
    W, H = 840, 440
    f = []

    f.append(text(420, 26, "Розподіл тепла SMD-компонента через друковану плату (PCB)", size=15, bold=True, color=INK))

    # SMD компонент (QFN / D2PAK)
    # Корпус пластиковий (епоксид)
    f.append(rect(290, 50, 260, 50, fill="#424242", stroke="#212121", sw=1.8, rx=4))
    f.append(text(420, 72, "Корпус чипа (QFN / DFN / PowerSO)", size=12, bold=True, color="#ffffff"))
    # Кристал всередині
    f.append(rect(360, 80, 120, 16, fill="#ff8a80", stroke=POS, sw=1.5, rx=2))
    f.append(text(420, 92, "Кристал (Tj)", size=10, bold=True, color=POS))

    # Виводи з боків
    f.append(rect(270, 90, 20, 14, fill="#b0bec5", stroke=LINE, sw=1.2))
    f.append(rect(550, 90, 20, 14, fill="#b0bec5", stroke=LINE, sw=1.2))

    # Thermal Pad під корпусом
    f.append(rect(340, 100, 160, 10, fill="#ffb74d", stroke="#e65100", sw=1.5, rx=1))
    f.append(text(420, 122, "Thermal Pad (припій)", size=10, color="#bf360c", bold=True))

    # ── Шари друкованої плати (PCB) — неперетинні блоки
    # Top Copper Layer
    f.append(rect(60, 132, 210, 16, fill="#d7ccc8", stroke="#8d6e63", sw=1.5, rx=2))
    f.append(rect(280, 132, 280, 16, fill="#ffb74d", stroke="#e65100", sw=1.5, rx=2))
    f.append(rect(570, 132, 210, 16, fill="#d7ccc8", stroke="#8d6e63", sw=1.5, rx=2))
    f.append(text(165, 144, "Верхній мідний полігон", size=10, color="#5d4037", bold=True))
    f.append(text(420, 144, "Тепловий полігон (Thermal Pad)", size=10, color="#bf360c", bold=True))
    f.append(text(675, 144, "Верхній мідний полігон", size=10, color="#5d4037", bold=True))

    # FR-4 Діелектрик (Top Core)
    f.append(rect(60, 148, 720, 70, fill="#c8e6c9", stroke="#388e3c", sw=1.5, rx=2))
    f.append(text(160, 185, "Діелектрик FR-4 (k ≈ 0.3 Вт/м·К)", size=11, color="#1b5e20", bold=True))

    # Внутрішній шар землі (GND Plane / Inner Cu)
    f.append(rect(60, 218, 720, 16, fill="#ffb74d", stroke="#e65100", sw=1.5, rx=2))
    f.append(text(180, 230, "Внутрішній шар заземлення (GND plane, 35 мкм)", size=10, color="#bf360c", bold=True))

    # FR-4 Діелектрик (Bottom Core)
    f.append(rect(60, 234, 720, 70, fill="#c8e6c9", stroke="#388e3c", sw=1.5, rx=2))
    f.append(text(160, 270, "Діелектрик FR-4 (k ≈ 0.3 Вт/м·К)", size=11, color="#1b5e20", bold=True))

    # Bottom Copper Layer
    f.append(rect(60, 304, 720, 16, fill="#ffb74d", stroke="#e65100", sw=1.5, rx=2))
    f.append(text(180, 316, "Нижній шар міді (Bottom Cu / тепловий розсіювач)", size=10, color="#bf360c", bold=True))

    # ── Масив теплових перехідних отворів (Thermal Vias) лініями
    vias_x = [360, 390, 420, 450, 480]
    for vx in vias_x:
        # Ліва і права мідні стінки гільзи
        f.append(line(vx - 4, 132, vx - 4, 320, color="#bf360c", sw=2.2))
        f.append(line(vx + 4, 132, vx + 4, 320, color="#bf360c", sw=2.2))
        # Просвіт отвору
        f.append(line(vx, 132, vx, 320, color="#ffffff", sw=2.0))

    f.append(textbox(420, 355, "Масив теплових отворів (Thermal Vias)\nмідна гільза 25 мкм, крок 1.0–1.2 мм, d = 0.3 мм", size=10, pad=6, fill="#fff3e0", stroke="#e65100")[0])

    # ── Стрілки теплових потоків
    # Вниз через перехідні отвори
    f.append(arrow(390, 155, 390, 300, color=POS, sw=2.0))
    f.append(arrow(450, 155, 450, 300, color=POS, sw=2.0))
    # Вбоки по шарах міді (розтікання)
    f.append(arrow(480, 140, 710, 140, color=POS, sw=1.8))
    f.append(arrow(360, 140, 240, 140, color=POS, sw=1.8))
    f.append(arrow(480, 226, 730, 226, color=POS, sw=1.8))
    f.append(arrow(360, 226, 220, 226, color=POS, sw=1.8))
    f.append(arrow(480, 312, 730, 312, color=POS, sw=1.8))
    f.append(arrow(360, 312, 220, 312, color=POS, sw=1.8))

    # Конвекція з поверхні плати
    f.append(arrow(650, 130, 650, 80, color=NEG, sw=1.5))
    f.append(arrow(150, 130, 150, 80, color=NEG, sw=1.5))
    f.append(text(650, 70, "Конвекція Top", size=10, color=NEG, bold=True))
    f.append(text(150, 70, "Конвекція Top", size=10, color=NEG, bold=True))

    f.append(arrow(650, 325, 650, 375, color=NEG, sw=1.5))
    f.append(arrow(150, 325, 150, 375, color=NEG, sw=1.5))
    f.append(text(650, 390, "Конвекція Bottom", size=10, color=NEG, bold=True))
    f.append(text(150, 390, "Конвекція Bottom", size=10, color=NEG, bold=True))

    # Псевдопараметри ΨJT та ΨJB
    f.append(textbox(710, 75, "ΨJT (junction-to-top)\nТвердотільна термопара\nна кришці чипа", size=9, pad=5, fill="#f5f5f5", stroke=LINE)[0])
    f.append(arrow(630, 75, 552, 75, color=LINE, sw=1.2))

    render(os.path.join(OUT, "smd-thermal-pcb.svg"), W, H, *f)


def fig_transient_zth_curves():
    """Динамічний тепловий імпеданс Zth(t) як функція тривалості імпульсу для різних duty cycle."""
    W, H = 840, 470
    f = []

    f.append(text(420, 24, "Динамічний тепловий імпеданс Zth(t) силового компонента", size=15, bold=True, color=INK))

    # Інформаційна плашка вгорі над графіком (поза сіткою)
    f.append(rect(140, 42, 560, 28, fill="#f4f6f8", stroke=LINE, sw=1.0, rx=4))
    f.append(text(420, 60, "Короткі імпульси (tp < 100 мкс): тепло поглинає кристал, Zth « θJC — вища пікова потужність", size=10, color=INK))

    L, R, T, B = 85, 780, 85, 395

    # Осі
    f.append(line(L, T, L, B, color=INK, sw=1.8))
    f.append(line(L, B, R, B, color=INK, sw=1.8))

    # Стрілки осей
    f.append(arrow(R - 10, B, R + 15, B, color=INK, sw=1.8))
    f.append(arrow(L, T + 10, L, T - 15, color=INK, sw=1.8))

    # Підписи осей
    f.append(text(R, B + 35, "Тривалість імпульсу tp [с] (лог. шкала)", size=12, bold=True, color=INK, anchor="end"))
    f.append(text(L - 10, T - 18, "Zth(t) [°C/Вт]", size=12, bold=True, color=INK, anchor="end"))

    # Сітка та мітки по X: 10^-5, 10^-4, 10^-3, 10^-2, 10^-1, 1, 10
    x_decades = [-5, -4, -3, -2, -1, 0, 1]
    def get_x(log_t):
        return L + (log_t - (-5.0)) / (1.0 - (-5.0)) * (R - L - 50)

    for d in x_decades:
        gx = get_x(d)
        f.append(line(gx, T, gx, B, color="#e0e0e0", sw=1.0, dash="2,2"))
        label = "10⁻⁵" if d == -5 else "10⁻⁴" if d == -4 else "10⁻³" if d == -3 else "10⁻²" if d == -2 else "0.1" if d == -1 else "1.0" if d == 0 else "10"
        f.append(text(gx, B + 18, label, size=11, color=MUTED))

    # Сітка та мітки по Y
    y_min_log, y_max_log = -2.3, 0.35
    def get_y(val):
        lv = math.log10(max(val, 0.005))
        return B - (lv - y_min_log) / (y_max_log - y_min_log) * (B - T)

    y_ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    for yv in y_ticks:
        gy = get_y(yv)
        f.append(line(L, gy, R - 50, gy, color="#e0e0e0", sw=1.0, dash="2,2"))
        f.append(text(L - 10, gy + 4, str(yv), size=11, color=MUTED, anchor="end"))

    def zth_func(t, D):
        r_tot = 1.8
        z_s = r_tot * (0.12 * (1.0 - math.exp(-t / 0.0001)) +
                       0.38 * (1.0 - math.exp(-t / 0.01)) +
                       0.50 * (1.0 - math.exp(-t / 0.8)))
        return D * r_tot + (1.0 - D) * z_s

    d_curves = [
        (0.5, "#d32f2f", "D = 0.5"),
        (0.2, "#f57c00", "D = 0.2"),
        (0.1, "#388e3c", "D = 0.1"),
        (0.05, "#1976d2", "D = 0.05"),
        (0.02, "#7b1fa2", "D = 0.02"),
        (0.0, "#212121", "Одиночний імпульс (Single pulse)")
    ]

    for D, col, lbl in d_curves:
        pts = []
        for i in range(120):
            lt = -5.0 + (1.0 - (-5.0)) * i / 119.0
            t_val = 10.0 ** lt
            zv = zth_func(t_val, D)
            pts.append((get_x(lt), get_y(zv)))
        
        sw = 2.4 if D == 0.0 else 1.8
        f.append(polyline(pts, color=col, sw=sw))

    # Рівень DC (постійний струм Rth)
    rth_y = get_y(1.8)
    f.append(line(L, rth_y, R - 50, rth_y, color=POS, sw=1.5, dash="5,3"))
    # Підпис розміщуємо праворуч у безпечній зоні
    f.append(text(R - 55, rth_y - 8, "Статичний θJC (DC)", size=10, bold=True, color=POS, anchor="end"))

    # Окрема чітка легенда в правому нижньому кутку
    f.append(rect(R - 250, B - 145, 235, 130, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(R - 132, B - 128, "Шпаруватість (Duty cycle D)", size=10, bold=True, color=INK))
    for idx, (D, col, lbl) in enumerate(d_curves):
        ly = B - 110 + idx * 17
        f.append(line(R - 240, ly, R - 215, ly, color=col, sw=2.2))
        f.append(text(R - 208, ly + 3, lbl, size=9, color=col, bold=(D==0.0), anchor="start"))

    render(os.path.join(OUT, "transient-zth-curves.svg"), W, H, *f)


def fig_cauer_vs_foster():
    """Порівняння RC-моделей Кауера (фізична) та Фостера (математична)."""
    W, H = 840, 420
    f = []

    f.append(text(420, 24, "Еквівалентні теплові RC-моделі для нестаціонарного аналізу", size=15, bold=True, color=INK))

    # ── Модель Кауера (Cauer Network — T-ladder)
    f.append(text(420, 60, "Модель Кауера (Cauer T-ladder) — Фізична структура", size=13, bold=True, color=POS))

    cy = 110
    # Вхідний вузол (кристал)
    f.append(circle(100, cy, 4, fill=POS, stroke=POS, sw=1.0))
    f.append(text(100, cy - 14, "Tj (Die)", size=11, bold=True, color=POS))
    f.append(arrow(50, cy, 95, cy, color=POS, sw=2.0))
    f.append(text(50, cy - 14, "Pd [Вт]", size=11, bold=True, color=POS))

    # Ланка 1: Кристал (R1, C1)
    f.append(line(100, cy, 150, cy, color=INK, sw=1.8))
    f.append(rect(150, cy - 16, 50, 32, fill="#fbe9e7", stroke=POS, sw=1.5, rx=3))
    f.append(text(175, cy + 5, "R1", size=11, bold=True, color=POS))
    f.append(line(200, cy, 270, cy, color=INK, sw=1.8))

    # Вузол 1
    f.append(circle(270, cy, 4, fill=INK, stroke=INK, sw=1.0))
    f.append(text(270, cy - 14, "T_die", size=10, color=MUTED))
    # Конденсатор C1 заземлений
    f.append(line(270, cy, 270, cy + 25, color=INK, sw=1.8))
    f.append(line(255, cy + 25, 285, cy + 25, color=INK, sw=2.0))
    f.append(line(255, cy + 32, 285, cy + 32, color=INK, sw=2.0))
    f.append(line(270, cy + 32, 270, cy + 50, color=INK, sw=1.8))
    f.append(text(295, cy + 30, "C1 (кремній)", size=10, color=POS))

    # Ланка 2: Фланець (R2, C2)
    f.append(line(270, cy, 330, cy, color=INK, sw=1.8))
    f.append(rect(330, cy - 16, 50, 32, fill="#ffe0b2", stroke="#e65100", sw=1.5, rx=3))
    f.append(text(355, cy + 5, "R2", size=11, bold=True, color="#bf360c"))
    f.append(line(380, cy, 450, cy, color=INK, sw=1.8))

    # Вузол 2
    f.append(circle(450, cy, 4, fill=INK, stroke=INK, sw=1.0))
    f.append(text(450, cy - 14, "Tc (Case)", size=10, color=MUTED))
    # Конденсатор C2 заземлений
    f.append(line(450, cy, 450, cy + 25, color=INK, sw=1.8))
    f.append(line(435, cy + 25, 465, cy + 25, color=INK, sw=2.0))
    f.append(line(435, cy + 32, 465, cy + 32, color=INK, sw=2.0))
    f.append(line(450, cy + 32, 450, cy + 50, color=INK, sw=1.8))
    f.append(text(475, cy + 30, "C2 (фланець)", size=10, color="#bf360c"))

    # Ланка 3: Радіатор (R3, C3)
    f.append(line(450, cy, 510, cy, color=INK, sw=1.8))
    f.append(rect(510, cy - 16, 50, 32, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=3))
    f.append(text(535, cy + 5, "R3", size=11, bold=True, color=NEG))
    f.append(line(560, cy, 630, cy, color=INK, sw=1.8))

    # Вузол 3
    f.append(circle(630, cy, 4, fill=INK, stroke=INK, sw=1.0))
    f.append(text(630, cy - 14, "Ts (Sink)", size=10, color=MUTED))
    # Конденсатор C3 заземлений
    f.append(line(630, cy, 630, cy + 25, color=INK, sw=1.8))
    f.append(line(615, cy + 25, 645, cy + 25, color=INK, sw=2.0))
    f.append(line(615, cy + 32, 645, cy + 32, color=INK, sw=2.0))
    f.append(line(630, cy + 32, 630, cy + 50, color=INK, sw=1.8))
    f.append(text(655, cy + 30, "C3 (радіатор)", size=10, color=NEG))

    # Вихід на Ta
    f.append(line(630, cy, 700, cy, color=INK, sw=1.8))
    f.append(circle(700, cy, 4, fill=NEG, stroke=NEG, sw=1.0))
    f.append(text(700, cy - 14, "Ta (Ambient)", size=11, bold=True, color=NEG))

    # Спільна шина землі для Кауера
    f.append(line(240, cy + 50, 660, cy + 50, color=LINE, sw=1.8))
    f.append(line(440, cy + 50, 440, cy + 62, color=LINE, sw=1.8))
    f.append(line(425, cy + 62, 455, cy + 62, color=LINE, sw=2.0))
    f.append(line(430, cy + 67, 450, cy + 67, color=LINE, sw=1.6))
    f.append(line(436, cy + 72, 444, cy + 72, color=LINE, sw=1.2))

    # Пояснення праворуч для Кауера
    f.append(text(725, cy + 20, "✓ Вузли мають фізичний сенс шарів", size=10, color="#2e7d32", anchor="start"))
    f.append(text(725, cy + 38, "✓ Ємності заземлені на Ta", size=10, color="#2e7d32", anchor="start"))

    # ── Модель Фостера (Foster Network — послідовні RC-блоки)
    fy = 290
    f.append(text(420, 240, "Модель Фостера (Foster Network) — Математична апроксимація", size=13, bold=True, color=NEG))

    f.append(circle(80, fy, 4, fill=POS, stroke=POS, sw=1.0))
    f.append(text(80, fy - 14, "Tj (Die)", size=11, bold=True, color=POS))
    f.append(arrow(35, fy, 75, fy, color=POS, sw=2.0))
    f.append(text(35, fy - 14, "Pd", size=11, bold=True, color=POS))

    # Блок 1 (R1 || C1)
    f.append(line(80, fy, 120, fy, color=INK, sw=1.8))
    # Верхня гілка (R1)
    f.append(line(120, fy, 120, fy - 22, color=INK, sw=1.5))
    f.append(line(120, fy - 22, 140, fy - 22, color=INK, sw=1.5))
    f.append(rect(140, fy - 36, 45, 28, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=3))
    f.append(text(162, fy - 18, "R1", size=11, bold=True, color=NEG))
    f.append(line(185, fy - 22, 210, fy - 22, color=INK, sw=1.5))
    f.append(line(210, fy - 22, 210, fy, color=INK, sw=1.5))
    # Нижня гілка (C1)
    f.append(line(120, fy, 120, fy + 22, color=INK, sw=1.5))
    f.append(line(120, fy + 22, 150, fy + 22, color=INK, sw=1.5))
    f.append(line(150, fy + 12, 150, fy + 32, color=INK, sw=2.0))
    f.append(line(157, fy + 12, 157, fy + 32, color=INK, sw=2.0))
    f.append(line(157, fy + 22, 210, fy + 22, color=INK, sw=1.5))
    f.append(line(210, fy + 22, 210, fy, color=INK, sw=1.5))
    f.append(text(154, fy + 44, "C1", size=10, color=NEG))

    # Блок 2 (R2 || C2)
    f.append(line(210, fy, 260, fy, color=INK, sw=1.8))
    f.append(circle(235, fy, 3, fill=MUTED, stroke=MUTED, sw=1.0))
    f.append(text(235, fy - 8, "v1", size=9, color=MUTED))
    # Верхня гілка (R2)
    f.append(line(260, fy, 260, fy - 22, color=INK, sw=1.5))
    f.append(line(260, fy - 22, 280, fy - 22, color=INK, sw=1.5))
    f.append(rect(280, fy - 36, 45, 28, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=3))
    f.append(text(302, fy - 18, "R2", size=11, bold=True, color=NEG))
    f.append(line(325, fy - 22, 350, fy - 22, color=INK, sw=1.5))
    f.append(line(350, fy - 22, 350, fy, color=INK, sw=1.5))
    # Нижня гілка (C2)
    f.append(line(260, fy, 260, fy + 22, color=INK, sw=1.5))
    f.append(line(260, fy + 22, 290, fy + 22, color=INK, sw=1.5))
    f.append(line(290, fy + 12, 290, fy + 32, color=INK, sw=2.0))
    f.append(line(297, fy + 12, 297, fy + 32, color=INK, sw=2.0))
    f.append(line(297, fy + 22, 350, fy + 22, color=INK, sw=1.5))
    f.append(line(350, fy + 22, 350, fy, color=INK, sw=1.5))
    f.append(text(294, fy + 44, "C2", size=10, color=NEG))

    # Блок 3 (R3 || C3)
    f.append(line(350, fy, 400, fy, color=INK, sw=1.8))
    f.append(circle(375, fy, 3, fill=MUTED, stroke=MUTED, sw=1.0))
    f.append(text(375, fy - 8, "v2", size=9, color=MUTED))
    # Верхня гілка (R3)
    f.append(line(400, fy, 400, fy - 22, color=INK, sw=1.5))
    f.append(line(400, fy - 22, 420, fy - 22, color=INK, sw=1.5))
    f.append(rect(420, fy - 36, 45, 28, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=3))
    f.append(text(442, fy - 18, "R3", size=11, bold=True, color=NEG))
    f.append(line(465, fy - 22, 490, fy - 22, color=INK, sw=1.5))
    f.append(line(490, fy - 22, 490, fy, color=INK, sw=1.5))
    # Нижня гілка (C3)
    f.append(line(400, fy, 400, fy + 22, color=INK, sw=1.5))
    f.append(line(400, fy + 22, 430, fy + 22, color=INK, sw=1.5))
    f.append(line(430, fy + 12, 430, fy + 32, color=INK, sw=2.0))
    f.append(line(437, fy + 12, 437, fy + 32, color=INK, sw=2.0))
    f.append(line(437, fy + 22, 490, fy + 22, color=INK, sw=1.5))
    f.append(line(490, fy + 22, 490, fy, color=INK, sw=1.5))
    f.append(text(434, fy + 44, "C3", size=10, color=NEG))

    # Вихід на Ta
    f.append(line(490, fy, 550, fy, color=INK, sw=1.8))
    f.append(circle(550, fy, 4, fill=NEG, stroke=NEG, sw=1.0))
    f.append(text(550, fy - 14, "Ta (Ambient)", size=11, bold=True, color=NEG))

    # Заземлення
    f.append(line(550, fy, 550, fy + 25, color=LINE, sw=1.8))
    f.append(line(535, fy + 25, 565, fy + 25, color=LINE, sw=2.0))
    f.append(line(540, fy + 30, 560, fy + 30, color=LINE, sw=1.6))
    f.append(line(546, fy + 35, 554, fy + 35, color=LINE, sw=1.2))

    # Пояснення праворуч для Фостера
    f.append(text(585, fy + 10, "✗ Проміжні вузли v1, v2 — суто математичні", size=10, color="#c62828", anchor="start"))
    f.append(text(585, fy + 28, "✓ Параметри легко вимірюються експериментально", size=10, color="#2e7d32", anchor="start"))

    render(os.path.join(OUT, "cauer-vs-foster.svg"), W, H, *f)


if __name__ == "__main__":
    fig_thermal_chain_stack()
    fig_smd_thermal_pcb()
    fig_transient_zth_curves()
    fig_cauer_vs_foster()
    print("All figures generated successfully.")
