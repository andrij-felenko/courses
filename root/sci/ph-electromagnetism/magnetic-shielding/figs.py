# -*- coding: utf-8 -*-
"""Фігури до теми «Магнітне екранування».
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

# ── Фігура 1: Порівняння механізмів екранування ─────────────────────────────
def fig_shielding_mechanisms():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Фундаментальні механізми магнітного екранування", size=16, bold=True, color=INK))

    panel_w = 360
    panel_h = 330
    y0 = 50

    # Ліва панель: Пасивне екранування (Феромагнетик μ_r >> 1)
    x1 = 20
    f.append(rect(x1, y0, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(x1 + panel_w / 2, y0 + 25, "Пасивний феромагнітний екран (μ_r ≫ 1)", size=14, bold=True, color="#1e293b"))
    f.append(text(x1 + panel_w / 2, y0 + 43, "Переспрямування силових ліній у товщу стінки", size=11, italic=True, color=MUTED))

    cx1, cy1 = x1 + panel_w / 2, y0 + 175
    r_out, r_in = 85, 60

    # Малювання кільця екрана
    ring_path = f"M {cx1-r_out},{cy1} A {r_out},{r_out} 0 1,0 {cx1+r_out},{cy1} A {r_out},{r_out} 0 1,0 {cx1-r_out},{cy1} M {cx1-r_in},{cy1} A {r_in},{r_in} 0 1,1 {cx1+r_in},{cy1} A {r_in},{r_in} 0 1,1 {cx1-r_in},{cy1}"
    f.append(path_svg(ring_path, fill="#e2e8f0", stroke="#475569", sw=2))
    f.append(text(cx1, cy1 + 4, "B_int ≈ 0", size=13, bold=True, color="#16a34a"))

    # Силові лінії для пасивного екрана (викривляються у стінку)
    for y_offset in [-120, -80, -40, 0, 40, 80, 120]:
        y_start = cy1 + y_offset
        if abs(y_offset) > r_out + 10:
            # Пряма лінія зовні
            f.append(line(x1 + 15, y_start, x1 + panel_w - 15, y_start, color="#2563eb", sw=1.8))
        else:
            # Силова лінія, що втягується у стінку екрана
            sign = 1 if y_offset >= 0 else -1
            bend = 35 * sign
            d_str = f"M {x1+15},{y_start} C {cx1-70},{y_start} {cx1-50},{cy1+y_offset+bend} {cx1},{cy1+y_offset+bend} C {cx1+50},{cy1+y_offset+bend} {cx1+70},{y_start} {x1+panel_w-15},{y_start}"
            f.append(path_svg(d_str, fill="none", stroke="#2563eb", sw=1.8))

    f.append(text(x1 + panel_w / 2, y0 + panel_h - 20, "Магнітний опір стінки R_m → 0", size=11, bold=True, color="#1e293b"))

    # Права панель: Надпровідне екранування (Ефект Мейснера χ = -1)
    x2 = 400
    f.append(rect(x2, y0, panel_w, panel_h, fill="#f0fdf4", stroke=BORDER, rx=8))
    f.append(text(x2 + panel_w / 2, y0 + 25, "Надпровідний екран (ефект Мейснера, χ = -1)", size=14, bold=True, color="#15803d"))
    f.append(text(x2 + panel_w / 2, y0 + 43, "Повне виштовхування магнітного потоку", size=11, italic=True, color=MUTED))

    cx2, cy2 = x2 + panel_w / 2, y0 + 175
    r_sc = 75

    # Суцільний або порожнистий надпровідник
    sc_ring_path = f"M {cx2-r_sc},{cy2} A {r_sc},{r_sc} 0 1,0 {cx2+r_sc},{cy2} A {r_sc},{r_sc} 0 1,0 {cx2-r_sc},{cy2} M {cx2-r_in},{cy2} A {r_in},{r_in} 0 1,1 {cx2+r_in},{cy2} A {r_in},{r_in} 0 1,1 {cx2-r_in},{cy2}"
    f.append(path_svg(sc_ring_path, fill="#bbf7d0", stroke="#16a34a", sw=2))
    f.append(text(cx2, cy2 + 4, "B_int = 0", size=13, bold=True, color="#15803d"))

    # Силові лінії для надпровідника (обгинають зовні)
    for y_offset in [-120, -80, -40, 0, 40, 80, 120]:
        y_start = cy2 + y_offset
        if abs(y_offset) > r_sc + 20:
            f.append(line(x2 + 15, y_start, x2 + panel_w - 15, y_start, color="#2563eb", sw=1.8))
        else:
            sign = -1 if y_offset < 0 else (1 if y_offset > 0 else -1)
            push = 45 * sign
            d_str = f"M {x2+15},{y_start} C {cx2-80},{y_start} {cx2-60},{cy2+y_offset+push} {cx2},{cy2+y_offset+push} C {cx2+60},{cy2+y_offset+push} {cx2+80},{y_start} {x2+panel_w-15},{y_start}"
            f.append(path_svg(d_str, fill="none", stroke="#2563eb", sw=1.8))

    # Поверхневі екрануючі струми
    f.append(text(cx2, cy2 - r_sc - 10, "Поверхневі струми j_s (шар λ_L)", size=11, bold=True, color="#dc2626"))

    f.append(text(x2 + panel_w / 2, y0 + panel_h - 20, "Ідеальний діамагнетизм μ_r = 0", size=11, bold=True, color="#15803d"))

    f.append(text(W / 2, H - 12, "Ліворуч: втягування поля у високоефективний магнітопровід. Праворуч: виштовхування поля поверневими струмами.", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'shielding-mechanism-comparison.svg'), W, H, "\n".join(f))

# ── Фігура 2: Багатошарове екранування ───────────────────────────────────────
def fig_multilayer_shielding_decay():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 25, "Згасання магнітного поля у багатошаровому циліндричному екрані", size=16, bold=True, color=INK))

    x0, y0 = 60, 60
    w_graph, h_graph = 640, 280

    # Фон графіка
    f.append(rect(x0, y0, w_graph, h_graph, fill="#f8fafc", stroke=BORDER, rx=4))

    # Осі
    f.append(line(x0 + 50, y0 + h_graph - 40, x0 + w_graph - 20, y0 + h_graph - 40, color=INK, sw=1.5))
    f.append(line(x0 + 50, y0 + 20, x0 + 50, y0 + h_graph - 40, color=INK, sw=1.5))

    f.append(text(x0 + w_graph - 60, y0 + h_graph - 15, "Радіус r від центра", size=12, bold=True, color=INK))
    f.append(text(x0 + 20, y0 + 30, "Поле B (Тл, логарифмічна шкала)", size=11, bold=True, color=INK))

    # Зони шарів
    # Шари: r1_in..r1_out (Шар 1 Мю-метал), air gap, r2_in..r2_out (Шар 2 Мю-метал), air gap, r3_in..r3_out (Шар 3 Сталь)
    x_start = x0 + 50
    x_end = x0 + w_graph - 40
    graph_w = x_end - x_start

    # Позиції рубежів
    r_center = x_start
    r1_in = x_start + graph_w * 0.25
    r1_out = x_start + graph_w * 0.35
    r2_in = x_start + graph_w * 0.55
    r2_out = x_start + graph_w * 0.65
    r3_in = x_start + graph_w * 0.82
    r3_out = x_start + graph_w * 0.92

    # Заливка шарів мю-металу
    f.append(rect(r1_in, y0 + 20, r1_out - r1_in, h_graph - 60, fill="#dbeafe", stroke="#3b82f6", sw=1))
    f.append(text((r1_in + r1_out)/2, y0 + 40, "Шар 1\nμ-метал", size=10, bold=True, color="#1d4ed8"))

    f.append(rect(r2_in, y0 + 20, r2_out - r2_in, h_graph - 60, fill="#dbeafe", stroke="#3b82f6", sw=1))
    f.append(text((r2_in + r2_out)/2, y0 + 40, "Шар 2\nμ-метал", size=10, bold=True, color="#1d4ed8"))

    f.append(rect(r3_in, y0 + 20, r3_out - r3_in, h_graph - 60, fill="#fef3c7", stroke="#d97706", sw=1))
    f.append(text((r3_in + r3_out)/2, y0 + 40, "Шар 3\nСталь", size=10, bold=True, color="#b45309"))

    # Крива згасання поля B(r) - логарифмічна крива
    # Зовні: B0 (високе)
    y_b0 = y0 + 50
    y_b1 = y0 + 110
    y_b2 = y0 + 130
    y_b3 = y0 + 190
    y_b4 = y0 + 210
    y_b5 = y0 + 260

    pts = [
        (x_end, y_b0),
        (r3_out, y_b0),
        (r3_in, y_b1),     # Стрімке падіння у шарі 3
        (r2_out, y_b2),    # Повільне падіння у зазорі
        (r2_in, y_b3),     # Стрімке падіння у шарі 2
        (r1_out, y_b4),    # Повільне падіння у зазорі
        (r1_in, y_b5),     # Стрімке падіння у шарі 1
        (r_center, y_b5)   # Внутрішнє захищене поле
    ]

    path_d = "M " + " L ".join([f"{px:.1f},{py:.1f}" for px, py in pts])
    f.append(path_svg(path_d, fill="none", stroke="#dc2626", sw=3))

    # Точки та підписи
    f.append(circle(x_end - 10, y_b0, 4, fill="#dc2626", stroke="none"))
    f.append(text(x_end - 40, y_b0 - 8, "B_ext", size=12, bold=True, color="#dc2626"))

    f.append(circle(r_center + 40, y_b5, 4, fill="#dc2626", stroke="none"))
    f.append(text(r_center + 70, y_b5 - 8, "B_int (S = S₁·S₂·S₃)", size=12, bold=True, color="#16a34a"))

    f.append(text(W / 2, H - 12, "Стрімкі спади B-поля відбуваються у стінках мю-металу, а зазори розв'язують потенціали шарів.", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'multilayer-shielding-decay.svg'), W, H, "\n".join(f))

# ── Фігура 3: Частотна залежність екранування ──────────────────────────────
def fig_frequency_dependent_shielding():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 25, "Частотна залежність коефіцієнта екранування S(f)", size=16, bold=True, color=INK))

    x0, y0 = 60, 60
    w_graph, h_graph = 640, 280

    f.append(rect(x0, y0, w_graph, h_graph, fill="#f8fafc", stroke=BORDER, rx=4))

    # Осі
    f.append(line(x0 + 50, y0 + h_graph - 40, x0 + w_graph - 20, y0 + h_graph - 40, color=INK, sw=1.5))
    f.append(line(x0 + 50, y0 + 20, x0 + 50, y0 + h_graph - 40, color=INK, sw=1.5))

    f.append(text(x0 + w_graph - 80, y0 + h_graph - 15, "Частота f (Гц, лог. шкала)", size=11, bold=True, color=INK))
    f.append(text(x0 + 20, y0 + 30, "Коефіцієнт екранування S (дБ)", size=11, bold=True, color=INK))

    # Шкала частот
    f.append(text(x0 + 90, y0 + h_graph - 25, "0 (DC)", size=10, color=MUTED))
    f.append(text(x0 + 220, y0 + h_graph - 25, "50 Гц", size=10, color=MUTED))
    f.append(text(x0 + 380, y0 + h_graph - 25, "10 кГц", size=10, color=MUTED))
    f.append(text(x0 + 540, y0 + h_graph - 25, "1 МГц", size=10, color=MUTED))

    # Крива 1: Мю-метал (високий DC, падіння на середніх частотах через вихрові струми, підйом на високих)
    # Початок 80 дБ, спад до 50 дБ на 1 кГц, зростання за рахунок скін-ефекту
    pts_mu = [
        (x0 + 50, y0 + 70),
        (x0 + 180, y0 + 70),
        (x0 + 300, y0 + 140),
        (x0 + 420, y0 + 120),
        (x0 + 580, y0 + 40)
    ]
    path_mu = "M " + " L ".join([f"{px:.1f},{py:.1f}" for px, py in pts_mu])
    f.append(path_svg(path_mu, fill="none", stroke="#2563eb", sw=2.5))
    f.append(text(x0 + 140, y0 + 58, "Мю-метал (μ_r ≫ 1)", size=11, bold=True, color="#2563eb"))

    # Крива 2: Мідь / Алюміній (0 дБ на DC, стрімке зростання на високих частотах через скін-ефект)
    pts_cu = [
        (x0 + 50, y0 + h_graph - 40),
        (x0 + 220, y0 + h_graph - 45),
        (x0 + 360, y0 + 150),
        (x0 + 480, y0 + 80),
        (x0 + 580, y0 + 30)
    ]
    path_cu = "M " + " L ".join([f"{px:.1f},{py:.1f}" for px, py in pts_cu])
    f.append(path_svg(path_cu, fill="none", stroke="#d97706", sw=2.5, dash="6,4"))
    f.append(text(x0 + 320, y0 + h_graph - 60, "Мідь / Алюміній (σ ≫ 1)", size=11, bold=True, color="#d97706"))

    # Зони домінування
    f.append(line(x0 + 260, y0 + 20, x0 + 260, y0 + h_graph - 40, color="#94a3b8", sw=1, dash="4,4"))
    f.append(text(x0 + 150, y0 + h_graph - 70, "Зона 1: Магнітостатичне\nперешунтування (μ_r)", size=10, bold=True, color="#1e293b"))
    f.append(text(x0 + 440, y0 + h_graph - 70, "Зона 2: Вихрові струми\nта скін-ефект (σ, δ = √(2/ωμσ))", size=10, bold=True, color="#1e293b"))

    f.append(text(W / 2, H - 12, "На низьких частотах працює переспрямування погляду мю-металом; на високих — скін-ефект у провіднику.", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'frequency-dependent-shielding.svg'), W, H, "\n".join(f))


if __name__ == "__main__":
    fig_shielding_mechanisms()
    fig_multilayer_shielding_decay()
    fig_frequency_dependent_shielding()
    print("Успішно згенеровано фігури у", IMG_DIR)
