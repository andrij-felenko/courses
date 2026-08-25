# -*- coding: utf-8 -*-
"""Фігури до теми «Напівпровідникові гетеропереходи та співвідношення Крьомера».
Запуск: python figs.py -> створює SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

BORDER = "#cbd5e1"

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Три типи зонного вирівнювання (Band Lineup Types) ─────────────────
def fig_band_lineup_types():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 25, "Три основні типи зонного вирівнювання в гетеропереходах", size=16, bold=True, color=INK))

    col_w = 260
    gap = 15
    y_top = 55
    panel_h = 365

    panels = [
        ("I тип: вкладений (Straddling)", "GaAs / AlGaAs", "Електрони й дірки в одному матеріалі", "#eff6ff", "#1d4ed8"),
        ("II тип: східчастий (Staggered)", "InP / GaAsSb", "Просторове розділення носіїв", "#f0fdf4", "#15803d"),
        ("III тип: розірваний (Broken-gap)", "InAs / GaSb", "Перекриття Ec1 та Ev2 без щілини", "#fff7ed", "#c2410c")
    ]

    for idx, (title, ex, desc, bg_color, accent) in enumerate(panels):
        x0 = 15 + idx * (col_w + gap)
        f.append(rect(x0, y_top, col_w, panel_h, fill=bg_color, stroke=BORDER, rx=6))

        f.append(text(x0 + col_w / 2, y_top + 22, title, size=12, bold=True, color=accent))
        f.append(text(x0 + col_w / 2, y_top + 40, f"Приклад: {ex}", size=11, color=MUTED, italic=True))

        x_mid = x0 + col_w / 2
        f.append(path_svg(f"M {x_mid} {y_top + 55} L {x_mid} {y_top + panel_h - 45}", stroke="#94a3b8", sw=1.5, dash="3,3"))
        f.append(text(x0 + 60, y_top + 65, "Матеріал 1", size=11, bold=True, color=INK))
        f.append(text(x0 + col_w - 60, y_top + 65, "Матеріал 2", size=11, bold=True, color=INK))

        y_vac = y_top + 85
        f.append(path_svg(f"M {x0 + 15} {y_vac} L {x0 + col_w - 15} {y_vac}", stroke="#64748b", sw=1.2, dash="4,4"))
        f.append(text(x0 + col_w - 35, y_vac - 6, "E_vac", size=10, color="#64748b", italic=True))

        if idx == 0:  # Type I
            ec1, ev1 = y_vac + 50, y_vac + 200
            ec2, ev2 = y_vac + 85, y_vac + 165

            f.append(line(x0 + 20, ec1, x_mid, ec1, color="#2563eb", sw=2.5))
            f.append(line(x0 + 20, ev1, x_mid, ev1, color="#dc2626", sw=2.5))
            f.append(line(x_mid, ec2, x0 + col_w - 20, ec2, color="#2563eb", sw=2.5))
            f.append(line(x_mid, ev2, x0 + col_w - 20, ev2, color="#dc2626", sw=2.5))
            f.append(line(x_mid, ec1, x_mid, ec2, color="#2563eb", sw=2, dash="2,2"))
            f.append(line(x_mid, ev1, x_mid, ev2, color="#dc2626", sw=2, dash="2,2"))

            f.append(text(x0 + 40, ec1 - 8, "E_c1", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + 40, ev1 + 14, "E_v1", size=10, bold=True, color="#dc2626"))
            f.append(text(x0 + col_w - 40, ec2 - 8, "E_c2", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + col_w - 40, ev2 + 14, "E_v2", size=10, bold=True, color="#dc2626"))

            f.append(text(x_mid + 22, (ec1 + ec2) / 2 + 3, "ΔE_c", size=10, bold=True, color="#2563eb"))
            f.append(text(x_mid + 22, (ev1 + ev2) / 2 + 3, "ΔE_v", size=10, bold=True, color="#dc2626"))

            f.append(circle(x_mid + 45, ec2 + 12, 6, fill="#3b82f6", stroke="#1d4ed8"))
            f.append(text(x_mid + 45, ec2 + 12, "e⁻", size=9, color="#ffffff", bold=True))
            f.append(circle(x_mid + 45, ev2 - 12, 6, fill="#ef4444", stroke="#b91c1c"))
            f.append(text(x_mid + 45, ev2 - 12, "h⁺", size=9, color="#ffffff", bold=True))

        elif idx == 1:  # Type II
            ec1, ev1 = y_vac + 45, y_vac + 155
            ec2, ev2 = y_vac + 95, y_vac + 205

            f.append(line(x0 + 20, ec1, x_mid, ec1, color="#2563eb", sw=2.5))
            f.append(line(x0 + 20, ev1, x_mid, ev1, color="#dc2626", sw=2.5))
            f.append(line(x_mid, ec2, x0 + col_w - 20, ec2, color="#2563eb", sw=2.5))
            f.append(line(x_mid, ev2, x0 + col_w - 20, ev2, color="#dc2626", sw=2.5))

            f.append(line(x_mid, ec1, x_mid, ec2, color="#2563eb", sw=2, dash="2,2"))
            f.append(line(x_mid, ev1, x_mid, ev2, color="#dc2626", sw=2, dash="2,2"))

            f.append(text(x0 + 40, ec1 - 8, "E_c1", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + 40, ev1 + 14, "E_v1", size=10, bold=True, color="#dc2626"))
            f.append(text(x0 + col_w - 40, ec2 - 8, "E_c2", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + col_w - 40, ev2 + 14, "E_v2", size=10, bold=True, color="#dc2626"))

            f.append(text(x_mid + 22, (ec1 + ec2) / 2 + 3, "ΔE_c", size=10, bold=True, color="#2563eb"))
            f.append(text(x_mid + 22, (ev1 + ev2) / 2 + 3, "ΔE_v", size=10, bold=True, color="#dc2626"))

            f.append(circle(x_mid + 45, ec2 + 12, 6, fill="#3b82f6", stroke="#1d4ed8"))
            f.append(text(x_mid + 45, ec2 + 12, "e⁻", size=9, color="#ffffff", bold=True))
            f.append(circle(x_mid - 45, ev1 - 12, 6, fill="#ef4444", stroke="#b91c1c"))
            f.append(text(x_mid - 45, ev1 - 12, "h⁺", size=9, color="#ffffff", bold=True))

        else:  # Type III
            ec1, ev1 = y_vac + 40, y_vac + 130
            ec2, ev2 = y_vac + 145, y_vac + 225

            f.append(line(x0 + 20, ec1, x_mid, ec1, color="#2563eb", sw=2.5))
            f.append(line(x0 + 20, ev1, x_mid, ev1, color="#dc2626", sw=2.5))
            f.append(line(x_mid, ec2, x0 + col_w - 20, ec2, color="#2563eb", sw=2.5))
            f.append(line(x_mid, ev2, x0 + col_w - 20, ev2, color="#dc2626", sw=2.5))

            f.append(line(x_mid, ec1, x_mid, ec2, color="#2563eb", sw=2, dash="2,2"))
            f.append(line(x_mid, ev1, x_mid, ev2, color="#dc2626", sw=2, dash="2,2"))

            f.append(text(x0 + 40, ec1 - 8, "E_c1", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + 40, ev1 - 8, "E_v1", size=10, bold=True, color="#dc2626"))
            f.append(text(x0 + col_w - 40, ec2 + 14, "E_c2", size=10, bold=True, color="#2563eb"))
            f.append(text(x0 + col_w - 40, ev2 + 14, "E_v2", size=10, bold=True, color="#dc2626"))

            f.append(rect(x_mid - 25, ev1, 50, ec2 - ev1, fill="#fef08a", stroke="none", rx=0))
            f.append(text(x_mid, (ev1 + ec2) / 2 + 3, "Перекриття", size=9, bold=True, color="#854d0e"))

        f.append(text(x0 + col_w / 2, y_top + panel_h - 18, desc, size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "fig1-band-lineup-types.svg"), W, H, "\n".join(f))

# ── Фігура 2: Квазіелектричні поля Крьомера ────────────────────────────────────
def fig_quasi_electric_fields():
    W, H = 820, 410
    f = []

    f.append(text(W / 2, 25, "Електростатичне поле гомопереходу vs Квазіелектричні поля гетероструктури", size=15, bold=True, color=INK))

    col_w = 380
    gap = 20
    y0 = 55
    h0 = 335

    # Left: Homojunction
    f.append(rect(15, y0, col_w, h0, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(15 + col_w / 2, y0 + 22, "Гомоперехід (однаковий напівпровідник)", size=12, bold=True, color="#1e293b"))
    f.append(text(15 + col_w / 2, y0 + 38, "Поле F(z) єдине для обох типів носіїв", size=11, color=MUTED, italic=True))

    ec_pts = f"M 35 {y0+90} C 120 {y0+90}, 150 {y0+170}, 240 {y0+170} L 375 {y0+170}"
    ev_pts = f"M 35 {y0+190} C 120 {y0+190}, 150 {y0+270}, 240 {y0+270} L 375 {y0+270}"
    f.append(path_svg(ec_pts, stroke="#2563eb", sw=2.5))
    f.append(path_svg(ev_pts, stroke="#dc2626", sw=2.5))

    f.append(text(50, y0 + 82, "E_c(z)", size=11, bold=True, color="#2563eb"))
    f.append(text(50, y0 + 182, "E_v(z)", size=11, bold=True, color="#dc2626"))

    f.append(arrow(170, y0 + 130, 110, y0 + 130, color="#2563eb", sw=2))
    f.append(text(140, y0 + 118, "F_e = -q·F", size=10, bold=True, color="#2563eb"))

    f.append(arrow(170, y0 + 230, 230, y0 + 230, color="#dc2626", sw=2))
    f.append(text(200, y0 + 218, "F_h = +q·F", size=10, bold=True, color="#dc2626"))

    f.append(rect(35, y0 + 280, col_w - 40, 42, fill="#f1f5f9", stroke="#cbd5e1", rx=4))
    f.append(text(15 + col_w / 2, y0 + 296, "Жорсткий зв'язок: F_e = -F_h", size=11, bold=True, color="#0f172a"))
    f.append(text(15 + col_w / 2, y0 + 312, "Неможливо штовхати е⁻ та h⁺ в один бік", size=10, color=MUTED))

    # Right: Graded Heterostructure
    x_r0 = 15 + col_w + gap
    f.append(rect(x_r0, y0, col_w, h0, fill="#eff6ff", stroke="#bfdbfe", rx=6))
    f.append(text(x_r0 + col_w / 2, y0 + 22, "Градний гетероперехід Крьомера", size=12, bold=True, color="#1d4ed8"))
    f.append(text(x_r0 + col_w / 2, y0 + 38, "Змінна ширина Eg(z) створює квазіполя", size=11, color="#2563eb", italic=True))

    ec_g_pts = f"M {x_r0+20} {y0+80} L {x_r0+col_w-20} {y0+180}"
    ev_g_pts = f"M {x_r0+20} {y0+250} L {x_r0+col_w-20} {y0+250}"
    f.append(path_svg(ec_g_pts, stroke="#2563eb", sw=2.5))
    f.append(path_svg(ev_g_pts, stroke="#dc2626", sw=2.5))

    f.append(text(x_r0 + 35, y0 + 72, "E_c(z)", size=11, bold=True, color="#2563eb"))
    f.append(text(x_r0 + 35, y0 + 242, "E_v(z)", size=11, bold=True, color="#dc2626"))

    f.append(arrow(x_r0 + 130, y0 + 130, x_r0 + 230, y0 + 180, color="#2563eb", sw=2.5))
    f.append(text(x_r0 + 195, y0 + 142, "F_e = -dE_c/dz > 0", size=10, bold=True, color="#2563eb"))

    f.append(text(x_r0 + 180, y0 + 268, "F_h = dE_v/dz ≈ 0", size=10, bold=True, color="#dc2626"))

    f.append(rect(x_r0 + 20, y0 + 280, col_w - 40, 42, fill="#dbeafe", stroke="#93c5fd", rx=4))
    f.append(text(x_r0 + col_w / 2, y0 + 296, "Незалежність: F_e та F_h розв'язані!", size=11, bold=True, color="#1e40af"))
    f.append(text(x_r0 + col_w / 2, y0 + 312, "Електрони прискорюються без руху дірок", size=10, color="#1d4ed8"))

    render(os.path.join(IMG_DIR, "fig2-quasi-electric-fields.svg"), W, H, "\n".join(f))

# ── Фігура 3: Формування 2DEG у HEMT ──────────────────────────────────────────
def fig_hemt_2deg_well():
    W, H = 800, 440
    f = []

    f.append(text(W / 2, 25, "Зонна діаграма N-AlGaAs / i-GaAs та двовимірний електронний газ (2DEG)", size=15, bold=True, color=INK))

    x_int = 380
    y0 = 60
    h0 = 350

    f.append(rect(30, y0, x_int - 30, h0, fill="#f1f5f9", stroke="none"))
    f.append(rect(x_int, y0, W - 30 - x_int, h0, fill="#fafaf9", stroke="none"))

    f.append(line(x_int, y0, x_int, y0 + h0, color="#94a3b8", sw=1.5, dash="4,4"))

    f.append(text(180, y0 + 25, "n-AlGaAs (широкозонний, легований)", size=12, bold=True, color="#334155"))
    f.append(text(580, y0 + 25, "нелегований i-GaAs (вузькозонний)", size=12, bold=True, color="#334155"))

    y_ef = y0 + 170
    f.append(line(50, y_ef, W - 50, y_ef, color="#16a34a", sw=1.5, dash="6,4"))
    f.append(text(W - 75, y_ef - 8, "E_F (рівень Фермі)", size=10, bold=True, color="#16a34a"))

    ec_algaas = f"M 50 {y0+100} L 240 {y0+100} C 310 {y0+100}, 360 {y0+130}, {x_int} {y0+150}"
    ec_gaas = f"M {x_int} {y0+220} L 410 {y0+240} C 440 {y0+240}, 480 {y0+145}, 650 {y0+145} L {W-50} {y0+145}"

    f.append(path_svg(ec_algaas, stroke="#2563eb", sw=2.5))
    f.append(path_svg(ec_gaas, stroke="#2563eb", sw=2.5))
    f.append(line(x_int, y0 + 150, x_int, y0 + 220, color="#2563eb", sw=2, dash="2,2"))

    f.append(text(x_int + 15, y0 + 185, "ΔE_c", size=11, bold=True, color="#2563eb"))

    ev_algaas = f"M 50 {y0+300} C 280 {y0+300}, 340 {y0+320}, {x_int} {y0+330}"
    ev_gaas = f"M {x_int} {y0+370} C 440 {y0+370}, 480 {y0+295}, 650 {y0+295} L {W-50} {y0+295}"
    f.append(path_svg(ev_algaas, stroke="#dc2626", sw=2.5))
    f.append(path_svg(ev_gaas, stroke="#dc2626", sw=2.5))
    f.append(line(x_int, y0 + 330, x_int, y0 + 370, color="#dc2626", sw=2, dash="2,2"))

    f.append(text(x_int + 15, y0 + 352, "ΔE_v", size=11, bold=True, color="#dc2626"))

    f.append(path_svg(f"M {x_int} {y_ef} L 410 {y0+240} L {x_int} {y0+220} Z", fill="#93c5fd", stroke="none"))
    f.append(text(x_int + 45, y_ef + 28, "2DEG (трикутна яма)", size=11, bold=True, color="#1e40af"))

    f.append(circle(200, y0 + 140, 7, fill="#dbeafe", stroke="#2563eb"))
    f.append(text(200, y0 + 140, "+", size=10, bold=True, color="#2563eb"))
    f.append(circle(250, y0 + 145, 7, fill="#dbeafe", stroke="#2563eb"))
    f.append(text(250, y0 + 145, "+", size=10, bold=True, color="#2563eb"))
    f.append(text(225, y0 + 170, "Позитивні іони донорів N_d⁺", size=10, color="#1e40af"))

    for ex in [x_int + 8, x_int + 16, x_int + 24]:
        f.append(circle(ex, y0 + 200, 4, fill="#1d4ed8", stroke="none"))
    f.append(arrow(x_int + 70, y0 + 220, x_int + 30, y0 + 205, color="#1d4ed8", sw=1.5))
    f.append(text(x_int + 140, y0 + 225, "Вільні електрони в чистому GaAs (без розсіювання!)", size=10, bold=True, color="#1d4ed8"))

    render(os.path.join(IMG_DIR, "fig3-hemt-2deg-well.svg"), W, H, "\n".join(f))

# ── Фігура 4: Подвійна гетероструктура (DH) ────────────────────────────────────
def fig_double_heterostructure():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 25, "Подвійна гетероструктура (DH): квантове й оптичне обмеження", size=15, bold=True, color=INK))

    x1, x2 = 250, 570
    y_top = 55
    h_band = 220

    f.append(rect(30, y_top, x1 - 30, h_band, fill="#f1f5f9", stroke="none"))
    f.append(rect(x1, y_top, x2 - x1, h_band, fill="#eff6ff", stroke="none"))
    f.append(rect(x2, y_top, W - 30 - x2, h_band, fill="#f1f5f9", stroke="none"))

    f.append(line(x1, y_top, x1, y_top + h_band, color="#94a3b8", sw=1.5, dash="3,3"))
    f.append(line(x2, y_top, x2, y_top + h_band, color="#94a3b8", sw=1.5, dash="3,3"))

    f.append(text((30 + x1) / 2, y_top + 20, "N-AlGaAs (обкладка)", size=11, bold=True, color="#475569"))
    f.append(text((x1 + x2) / 2, y_top + 20, "p-GaAs (активний шар)", size=11, bold=True, color="#1d4ed8"))
    f.append(text((x2 + W - 30) / 2, y_top + 20, "P-AlGaAs (обкладка)", size=11, bold=True, color="#475569"))

    ec_pts = f"M 40 {y_top+60} L {x1} {y_top+60} L {x1} {y_top+120} L {x2} {y_top+120} L {x2} {y_top+60} L {W-40} {y_top+60}"
    f.append(path_svg(ec_pts, stroke="#2563eb", sw=2.5))
    f.append(text(60, y_top + 52, "E_c", size=11, bold=True, color="#2563eb"))

    ev_pts = f"M 40 {y_top+200} L {x1} {y_top+200} L {x1} {y_top+155} L {x2} {y_top+155} L {x2} {y_top+200} L {W-40} {y_top+200}"
    f.append(path_svg(ev_pts, stroke="#dc2626", sw=2.5))
    f.append(text(60, y_top + 212, "E_v", size=11, bold=True, color="#dc2626"))

    f.append(circle((x1 + x2) / 2 - 40, y_top + 132, 6, fill="#3b82f6", stroke="#1d4ed8"))
    f.append(text((x1 + x2) / 2 - 40, y_top + 132, "e⁻", size=9, color="#ffffff", bold=True))
    f.append(circle((x1 + x2) / 2 + 40, y_top + 132, 6, fill="#3b82f6", stroke="#1d4ed8"))
    f.append(text((x1 + x2) / 2 + 40, y_top + 132, "e⁻", size=9, color="#ffffff", bold=True))

    f.append(circle((x1 + x2) / 2 - 40, y_top + 144, 6, fill="#ef4444", stroke="#b91c1c"))
    f.append(text((x1 + x2) / 2 - 40, y_top + 144, "h⁺", size=9, color="#ffffff", bold=True))
    f.append(circle((x1 + x2) / 2 + 40, y_top + 144, 6, fill="#ef4444", stroke="#b91c1c"))
    f.append(text((x1 + x2) / 2 + 40, y_top + 144, "h⁺", size=9, color="#ffffff", bold=True))

    f.append(text((x1 + x2) / 2, y_top + 95, "1. Потенціальна яма (обмеження носіїв)", size=11, bold=True, color="#1e40af"))

    y_opt = 300
    h_opt = 135

    f.append(rect(30, y_opt, W - 60, h_opt, fill="#f8fafc", stroke=BORDER, rx=4))
    f.append(line(x1, y_opt, x1, y_opt + h_opt, color="#cbd5e1", sw=1, dash="2,2"))
    f.append(line(x2, y_opt, x2, y_opt + h_opt, color="#cbd5e1", sw=1, dash="2,2"))

    f.append(text(120, y_opt + 20, "2. Оптичний хвилевід n(z)", size=11, bold=True, color="#0f172a"))

    n_pts = f"M 40 {y_opt+85} L {x1} {y_opt+85} L {x1} {y_opt+45} L {x2} {y_opt+45} L {x2} {y_opt+85} L {W-40} {y_opt+85}"
    f.append(path_svg(n_pts, stroke="#0284c7", sw=2))

    f.append(text((30 + x1) / 2, y_opt + 105, "n_2 ≈ 3.4 (AlGaAs)", size=10, color="#0369a1"))
    f.append(text((x1 + x2) / 2, y_opt + 32, "n_1 ≈ 3.6 (GaAs)", size=10, bold=True, color="#0369a1"))
    f.append(text((x2 + W - 30) / 2, y_opt + 105, "n_2 ≈ 3.4 (AlGaAs)", size=10, color="#0369a1"))

    opt_mode = []
    for px in range(int(x1 - 80), int(x2 + 80), 4):
        x_rel = (px - (x1 + x2) / 2) / 100.0
        val = math.exp(-x_rel**2 * 2.5)
        py = y_opt + 115 - val * 45
        opt_mode.append((px, py))

    d_opt = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in opt_mode)
    f.append(path_svg(d_opt, stroke="#eab308", sw=2.5))
    f.append(text((x1 + x2) / 2, y_opt + 125, "Оптична мода лазера (світлове пляма)", size=10, bold=True, color="#ca8a04"))

    render(os.path.join(IMG_DIR, "fig4-double-heterostructure.svg"), W, H, "\n".join(f))

if __name__ == "__main__":
    fig_band_lineup_types()
    fig_quasi_electric_fields()
    fig_hemt_2deg_well()
    fig_double_heterostructure()
    print("Всі 4 фігури гетеропереходу успішно згенеровано!")
