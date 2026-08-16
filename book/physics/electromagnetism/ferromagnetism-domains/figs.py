# -*- coding: utf-8 -*-
"""Фігури до теми «Феромагнетизм і домени».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
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


# ── Фігура 1: Парамагнетизм проти феромагнетизму ───────────────────────────
def fig_paramagnet_vs_ferromagnet():
    W, H = 740, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Мікроскопічний стан спінів у парамагнетику та феромагнетику", size=16, bold=True, color=INK))

    bw = 330
    bh = 240
    y_top = 55

    # Ліва панель: Парамагнетик
    x1 = 25
    f.append(rect(x1, y_top, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))
    f.append(text(x1 + bw / 2, y_top + 24, "Парамагнетик (T > 0 K)", size=14, bold=True, color=INK))
    f.append(text(x1 + bw / 2, y_top + 42, "Тепловий рух хаотизує спіни (M = 0)", size=11, color=MUTED))

    angles_para = [
        45, 190, 310, 120,
        260, 15, 145, 230,
        80, 290, 175, 35,
        210, 130, 345, 100
    ]
    rows, cols = 4, 4
    dx = bw / (cols + 1)
    dy = (bh - 50) / (rows + 1)
    for r in range(rows):
        for c in range(cols):
            cx = x1 + (c + 1) * dx
            cy = y_top + 50 + (r + 1) * dy
            ang = math.radians(angles_para[r * cols + c])
            r_arrow = 18
            ex = cx + r_arrow * math.cos(ang)
            ey = cy - r_arrow * math.sin(ang)
            f.append(circle(cx, cy, 20, fill="#edf2f7", stroke="#cbd5e1", sw=1))
            f.append(arrow(cx, cy, ex, ey, color="#e11d48", sw=2))

    f.append(text(x1 + bw / 2, y_top + bh - 12, "Сумарний момент = 0", size=12, bold=True, color="#e11d48"))

    # Права панель: Феромагнетик
    x2 = 385
    f.append(rect(x2, y_top, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))
    f.append(text(x2 + bw / 2, y_top + 24, "Феромагнетик (T < T_c)", size=14, bold=True, color=INK))
    f.append(text(x2 + bw / 2, y_top + 42, "Обмінна взаємодія вирівнює спіни (M >> 0)", size=11, color=MUTED))

    for r in range(rows):
        for c in range(cols):
            cx = x2 + (c + 1) * dx
            cy = y_top + 50 + (r + 1) * dy
            ex = cx
            ey = cy - 20
            f.append(circle(cx, cy, 20, fill="#e0f2fe", stroke="#7dd3fc", sw=1))
            f.append(arrow(cx, cy + 4, ex, ey, color="#0284c7", sw=2.2))

    f.append(text(x2 + bw / 2, y_top + bh - 12, "Обмінний інтеграл J > 0 (спонтанна намагніченість)", size=12, bold=True, color="#0284c7"))

    b_box, _, _ = textbox(W / 2, H - 22, "Кулонівське відштовхування + принцип Паулі створюють обмінну енергію E_ex = -2·J·(S_i · S_j)", size=12, pad=6, fill="#f1f5f9", stroke=FIELD, sw=1)
    f.append(b_box)

    return render(os.path.join(IMG_DIR, "paramagnet-vs-ferromagnet.svg"), W, H, *f)


# ── Фігура 2: Формування доменної структури ──────────────────────────────────
def fig_domain_structure_formation():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Еволюція доменної структури для мінімізації магнітостатичної енергії", size=15, bold=True, color=INK))

    w_stage = 220
    h_stage = 220
    y_s = 55

    # Етап 1: Монодомен
    x1 = 20
    f.append(rect(x1, y_s, w_stage, h_stage, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    f.append(text(x1 + w_stage / 2, y_s + 20, "а) Монодомен", size=13, bold=True, color=INK))
    f.append(rect(x1 + 45, y_s + 50, 130, 120, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=4))
    f.append(arrow(x1 + 110, y_s + 150, x1 + 110, y_s + 70, color="#0284c7", sw=3.5))
    f.append(text(x1 + 110, y_s + 110, "M", size=16, bold=True, color="#0284c7"))
    f.append(text(x1 + 110, y_s + 42, "N N N N N", size=11, bold=True, color="#e11d48"))
    f.append(text(x1 + 110, y_s + 182, "S S S S S", size=11, bold=True, color="#1d4ed8"))
    f.append(path_svg(f"M {x1 + 40} {y_s + 50} C {x1 - 15} {y_s + 30}, {x1 - 15} {y_s + 170}, {x1 + 40} {y_s + 170}", fill="none", stroke="#e11d48", sw=1.5, dash="4,3"))
    f.append(path_svg(f"M {x1 + 180} {y_s + 50} C {x1 + 235} {y_s + 30}, {x1 + 235} {y_s + 170}, {x1 + 180} {y_s + 170}", fill="none", stroke="#e11d48", sw=1.5, dash="4,3"))
    f.append(text(x1 + w_stage / 2, y_s + h_stage - 12, "Максимальна E_ms (розсіяне поле)", size=10, bold=True, color="#e11d48"))

    # Етап 2: Два антипаралельні домени
    x2 = 260
    f.append(rect(x2, y_s, w_stage, h_stage, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    f.append(text(x2 + w_stage / 2, y_s + 20, "б) 180° домени", size=13, bold=True, color=INK))
    f.append(rect(x2 + 45, y_s + 50, 130, 120, fill="#f1f5f9", stroke=LINE, sw=2, rx=4))
    f.append(line(x2 + 110, y_s + 50, x2 + 110, y_s + 170, color="#64748b", sw=2, dash="3,3"))
    f.append(rect(x2 + 45, y_s + 50, 65, 120, fill="#e0f2fe", stroke="none"))
    f.append(arrow(x2 + 77, y_s + 145, x2 + 77, y_s + 75, color="#0284c7", sw=2.8))
    f.append(rect(x2 + 110, y_s + 50, 65, 120, fill="#fef3c7", stroke="none"))
    f.append(arrow(x2 + 143, y_s + 75, x2 + 143, y_s + 145, color="#d97706", sw=2.8))
    f.append(path_svg(f"M {x2 + 77} {y_s + 50} C {x2 + 77} {y_s + 35}, {x2 + 143} {y_s + 35}, {x2 + 143} {y_s + 50}", fill="none", stroke="#e11d48", sw=1.5, dash="3,3"))
    f.append(text(x2 + w_stage / 2, y_s + h_stage - 12, "E_ms зменшено у ~2 рази", size=10, bold=True, color="#d97706"))

    # Етап 3: Домени замикання (Closure Domains)
    x3 = 500
    f.append(rect(x3, y_s, w_stage, h_stage, fill="#fafafa", stroke=LINE, sw=1.2, rx=8))
    f.append(text(x3 + w_stage / 2, y_s + 20, "в) Домени замикання", size=13, bold=True, color=INK))
    f.append(rect(x3 + 45, y_s + 50, 130, 120, fill="#f1f5f9", stroke=LINE, sw=2, rx=4))
    f.append(line(x3 + 45, y_s + 50, x3 + 110, y_s + 85, color="#64748b", sw=1.8))
    f.append(line(x3 + 175, y_s + 50, x3 + 110, y_s + 85, color="#64748b", sw=1.8))
    f.append(line(x3 + 45, y_s + 170, x3 + 110, y_s + 135, color="#64748b", sw=1.8))
    f.append(line(x3 + 175, y_s + 170, x3 + 110, y_s + 135, color="#64748b", sw=1.8))
    f.append(line(x3 + 110, y_s + 85, x3 + 110, y_s + 135, color="#64748b", sw=1.8))

    f.append(arrow(x3 + 90, y_s + 65, x3 + 130, y_s + 65, color="#16a34a", sw=2.2))
    f.append(arrow(x3 + 130, y_s + 155, x3 + 90, y_s + 155, color="#16a34a", sw=2.2))
    f.append(arrow(x3 + 77, y_s + 140, x3 + 77, y_s + 90, color="#0284c7", sw=2.5))
    f.append(arrow(x3 + 143, y_s + 90, x3 + 143, y_s + 140, color="#d97706", sw=2.5))

    f.append(text(x3 + w_stage / 2, y_s + h_stage - 12, "E_ms = 0 (потік замкнено всередині)", size=10, bold=True, color="#16a34a"))

    b_box, _, _ = textbox(W / 2, H - 24, "Формування стінок вимагає енергії E_wall = γ_w·S, тому розмір доменів досягає мінімуму E_total = E_ms + E_wall + E_k", size=11.5, pad=6, fill="#f8fafc", stroke=FIELD, sw=1)
    f.append(b_box)

    return render(os.path.join(IMG_DIR, "domain-structure-formation.svg"), W, H, *f)


# ── Фігура 3: Структура доменної стінки Блоха ──────────────────────────────
def fig_bloch_wall_structure():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Плавне обертання векторів намагніченості у 180° доменній стінці Блоха", size=15, bold=True, color=INK))

    y_top = 55
    w_box = 690
    h_box = 210
    x_b = 25

    # Загальний фоновий блок
    f.append(rect(x_b, y_top, w_box, h_box, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))

    # Ліва і права області без накладання рамок
    f.append(text(x_b + 70, y_top + 25, "Домен 1 (M ↑)", size=13, bold=True, color="#0284c7"))
    f.append(text(x_b + w_box - 70, y_top + 25, "Домен 2 (M ↓)", size=13, bold=True, color="#d97706"))
    f.append(text(x_b + w_box / 2, y_top + 25, "Доменна стінка Блоха (товщина δ_w ≈ 10...100 нм)", size=13, bold=True, color=INK))

    num_spins = 9
    dx_spin = (w_box - 80) / (num_spins - 1)
    cy = y_top + 115

    for i in range(num_spins):
        cx = x_b + 40 + i * dx_spin
        fraction = i / (num_spins - 1)
        angle_deg = 90 - 180 * fraction
        rad = math.radians(angle_deg)

        len_s = 35
        ex = cx + len_s * math.cos(rad) * 0.3
        ey = cy - len_s * math.sin(rad)

        col = "#0284c7" if fraction < 0.3 else ("#d97706" if fraction > 0.7 else "#7c3aed")
        f.append(circle(cx, cy, 6, fill="#cbd5e1", stroke=INK, sw=1))
        f.append(arrow(cx, cy, ex, ey, color=col, sw=2.5))

        theta_str = f"{int(round(90 - angle_deg))}°"
        f.append(text(cx, cy + 30, theta_str, size=10, color=MUTED))

    # Дві пояснювальні примітки посередині
    f.append(text(x_b + w_box * 0.3, y_top + h_box - 20, "Обмінна енергія потовщує стінку (малий dθ/dx)", size=11, color="#0284c7", bold=True))
    f.append(text(x_b + w_box * 0.7, y_top + h_box - 20, "Анізотропія звужує стінку (вертикальна вісь)", size=11, color="#d97706", bold=True))

    f.append(text(W / 2, H - 16, "Рівноважна товщина: δ_w = π·√(A / K),  енергія стінки: γ_w = 4·√(A·K)", size=13, bold=True, color=INK))

    return render(os.path.join(IMG_DIR, "bloch-wall-structure.svg"), W, H, *f)


# ── Фігура 4: Петля гістерезису та ефект Баркхаузена ───────────────────────
def fig_hysteresis_barkhausen():
    W, H = 740, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Основна петля магнітного гістерезису та дискретні стрибки Баркхаузена", size=15, bold=True, color=INK))

    cx = 330
    cy = 215
    scale_h = 240
    scale_b = 140

    f.append(line(cx - scale_h - 20, cy, cx + scale_h + 30, cy, color=INK, sw=1.8))
    f.append(line(cx, cy + scale_b + 20, cx, cy - scale_b - 30, color=INK, sw=1.8))
    f.append(text(cx + scale_h + 40, cy + 4, "H (A/м)", size=13, bold=True, color=INK))
    f.append(text(cx + 15, cy - scale_b - 32, "B (Тл)", size=13, bold=True, color=INK))

    p_upper = (
        f"M {cx + scale_h} {cy - scale_b} "
        f"C {cx + scale_h * 0.4} {cy - scale_b}, {cx - scale_h * 0.2} {cy - scale_b * 0.75}, {cx - scale_h * 0.55} {cy} "
        f"C {cx - scale_h * 0.75} {cy + scale_b * 0.55}, {cx - scale_h * 0.9} {cy + scale_b}, {cx - scale_h} {cy + scale_b}"
    )
    p_lower = (
        f"M {cx - scale_h} {cy + scale_b} "
        f"C {cx - scale_h * 0.4} {cy + scale_b}, {cx + scale_h * 0.2} {cy + scale_b * 0.75}, {cx + scale_h * 0.55} {cy} "
        f"C {cx + scale_h * 0.75} {cy - scale_b * 0.55}, {cx + scale_h * 0.9} {cy - scale_b}, {cx + scale_h} {cy - scale_b}"
    )

    f.append(path_svg(p_upper, fill="none", stroke="#0284c7", sw=2.5))
    f.append(path_svg(p_lower, fill="none", stroke="#0284c7", sw=2.5))

    p_init = (
        f"M {cx} {cy} "
        f"Q {cx + 30} {cy - 20}, {cx + 60} {cy - 45} "
        f"Q {cx + 100} {cy - 90}, {cx + 160} {cy - 125} "
        f"T {cx + scale_h} {cy - scale_b}"
    )
    f.append(path_svg(p_init, fill="none", stroke="#e11d48", sw=2, dash="4,3"))

    f.append(circle(cx, cy - scale_b * 0.72, 4, fill="#16a34a", stroke=INK, sw=1))
    f.append(text(cx - 28, cy - scale_b * 0.72 + 4, "B_r", size=13, bold=True, color="#16a34a"))

    f.append(circle(cx - scale_h * 0.55, cy, 4, fill="#d97706", stroke=INK, sw=1))
    f.append(text(cx - scale_h * 0.55, cy + 18, "-H_c", size=13, bold=True, color="#d97706"))

    f.append(circle(cx + scale_h * 0.55, cy, 4, fill="#d97706", stroke=INK, sw=1))
    f.append(text(cx + scale_h * 0.55, cy - 12, "+H_c", size=13, bold=True, color="#d97706"))

    f.append(circle(cx + scale_h, cy - scale_b, 4, fill="#0284c7", stroke=INK, sw=1))
    f.append(text(cx + scale_h - 20, cy - scale_b - 10, "B_s (Насичення)", size=12, bold=True, color="#0284c7"))

    x_in = 560
    y_in = 50
    w_in = 160
    h_in = 130
    f.append(rect(x_in, y_in, w_in, h_in, fill="#ffffff", stroke="#e11d48", sw=1.5, rx=6))
    f.append(text(x_in + w_in / 2, y_in + 18, "Ефект Баркхаузена", size=11, bold=True, color="#e11d48"))

    p_step = (
        f"M {x_in + 15} {y_in + 105} "
        f"L {x_in + 35} {y_in + 105} L {x_in + 35} {y_in + 85} "
        f"L {x_in + 60} {y_in + 85} L {x_in + 60} {y_in + 60} "
        f"L {x_in + 95} {y_in + 60} L {x_in + 95} {y_in + 35} "
        f"L {x_in + 140} {y_in + 35}"
    )
    f.append(path_svg(p_step, fill="none", stroke="#e11d48", sw=2))
    f.append(text(x_in + w_in / 2, y_in + h_in - 10, "Стрибки стінок на дефектах", size=9.5, color=MUTED))

    f.append(line(cx + 80, cy - 60, x_in, y_in + h_in / 2, color="#e11d48", sw=1, dash="2,2"))

    b_loss, _, _ = textbox(110, H - 45, "Площа петлі Q = ∮ H dB відповідає енергії втрат на перемагнічування за 1 цикл (тепло)", size=11.5, pad=6, fill="#f8fafc", stroke=FIELD, sw=1)
    f.append(b_loss)

    return render(os.path.join(IMG_DIR, "hysteresis-barkhausen.svg"), W, H, *f)


# ── Фігура 5: Температурна залежність та точка Кюрі ─────────────────────────
def fig_curie_temperature():
    W, H = 700, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Залежність спонтанної намагніченості та сприйнятливості від температури", size=15, bold=True, color=INK))

    cx = 80
    cy = 250
    w_graph = 560
    h_graph = 190

    f.append(line(cx, cy, cx + w_graph + 20, cy, color=INK, sw=1.8))
    f.append(line(cx, cy, cx, cy - h_graph - 20, color=INK, sw=1.8))
    f.append(text(cx + w_graph + 25, cy + 4, "T (Температура)", size=12, bold=True, color=INK))
    f.append(text(cx - 10, cy - h_graph - 25, "M_s / M_0,  χ", size=12, bold=True, color=INK))

    x_tc = cx + w_graph * 0.6
    f.append(line(x_tc, cy + 10, x_tc, cy - h_graph - 10, color="#64748b", sw=1.5, dash="4,4"))
    f.append(text(x_tc, cy + 24, "T_c (Точка Кюрі)", size=12, bold=True, color="#e11d48"))

    p_ms = f"M {cx} {cy - h_graph}"
    steps = 40
    for i in range(steps + 1):
        t_rel = (i / steps) * 0.6
        x_pt = cx + t_rel * w_graph
        m_rel = (1.0 - (t_rel / 0.6) ** 2) ** 0.35 if t_rel < 0.6 else 0.0
        y_pt = cy - m_rel * h_graph
        p_ms += f" L {x_pt:.1f} {y_pt:.1f}"

    f.append(path_svg(p_ms, fill="none", stroke="#0284c7", sw=2.8))
    f.append(text(cx + 120, cy - h_graph + 30, "Спонтанна намагніченість M_s(T)", size=12, bold=True, color="#0284c7"))

    p_chi = ""
    for i in range(1, 30):
        t_rel = 0.6 + (i / 30) * 0.38
        x_pt = cx + t_rel * w_graph
        denom = (t_rel - 0.6) * 12.0 + 0.15
        chi_val = min(1.0, 0.12 / denom)
        y_pt = cy - chi_val * h_graph
        if i == 1:
            p_chi += f"M {x_pt:.1f} {y_pt:.1f}"
        else:
            p_chi += f" L {x_pt:.1f} {y_pt:.1f}"

    f.append(path_svg(p_chi, fill="none", stroke="#d97706", sw=2.5, dash="5,3"))
    f.append(text(x_tc + 80, cy - 80, "Закон Кюрі — Вейса: χ = C / (T - T_c)", size=11.5, bold=True, color="#d97706"))

    f.append(rect(cx + 15, cy - h_graph + 5, 140, 26, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=4))
    f.append(text(cx + 85, cy - h_graph + 22, "Феромагнітний стан", size=11, bold=True, color="#0284c7"))

    f.append(rect(x_tc + 50, cy - h_graph + 5, 140, 26, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    f.append(text(x_tc + 120, cy - h_graph + 22, "Парамагнітний стан", size=11, bold=True, color="#d97706"))

    f.append(text(W / 2, H - 12, "При T > T_c теплова енергія k_B·T долає обмінну енергію J, руйнуючи домени (фазовий перехід II роду)", size=11.5, color=INK))

    return render(os.path.join(IMG_DIR, "curie-temperature.svg"), W, H, *f)


if __name__ == '__main__':
    fig_paramagnet_vs_ferromagnet()
    fig_domain_structure_formation()
    fig_bloch_wall_structure()
    fig_hysteresis_barkhausen()
    fig_curie_temperature()
    print("Всі фігури успішно згенеровано у ./img/")
