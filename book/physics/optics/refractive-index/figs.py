# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def make_phase_delay_fig():
    w, h = 760, 340
    path = os.path.join(IMG_DIR, 'refractive-index-phase-delay.svg')

    bg_vac = rect(20, 50, 240, 220, fill="#f0f4f8", stroke="#cbd5e1", sw=1.5, rx=8)
    bg_med = rect(280, 50, 460, 220, fill="#e0f2fe", stroke="#7dd3fc", sw=1.5, rx=8)

    labels = []
    labels.append(text(140, 75, "Вакуум (n = 1)", size=15, color="#1e293b", bold=True))
    labels.append(text(510, 75, "Діелектричне середовище (n > 1)", size=15, color="#0369a1", bold=True))

    interface = line(280, 50, 280, 270, color="#0284c7", sw=2.5, dash="4,4")

    atoms = []
    atom_coords = [(350, 110), (350, 210), (450, 160), (550, 110), (550, 210), (650, 160)]
    for ax, ay in atom_coords:
        atoms.append(circle(ax, ay, 12, fill="#bae6fd", stroke="#0284c7", sw=1.8))
        atoms.append(circle(ax, ay, 4, fill="#0284c7", stroke="#0284c7", sw=1))
        atoms.append(line(ax, ay - 18, ax, ay + 18, color="#0369a1", sw=1.2, dash="2,2"))

    import math
    path_vac = []
    for x in range(30, 281, 2):
        y = 160 - 35 * math.sin(2 * math.pi * (x - 30) / 80)
        path_vac.append("%s%.1f %.1f" % ("M" if x == 30 else "L", x, y))
    wave_vac = '<path d="%s" fill="none" stroke="#dc2626" stroke-width="2.2"/>' % " ".join(path_vac)

    path_med = []
    for x in range(280, 721, 2):
        y = 160 - 35 * math.sin(2 * math.pi * (x - 280) / 53.3)
        path_med.append("%s%.1f %.1f" % ("M" if x == 280 else "L", x, y))
    wave_med = '<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.2"/>' % " ".join(path_med)

    annots = []
    annots.append(arrow(100, 215, 180, 215, color="#dc2626", sw=1.5))
    annots.append(text(140, 235, "v = c, λ = λ₀", size=13, color="#b91c1c", bold=True))

    annots.append(arrow(380, 235, 460, 235, color="#2563eb", sw=1.5))
    annots.append(text(420, 255, "v = c / n,  λ = λ₀ / n", size=13, color="#1d4ed8", bold=True))

    box_mech = fitbox(40, 285, 680, 42,
                      "Механізм: зовнішня хвиля поляризує атоми → вторинні хвилі підсилюють прохідну хвилю із запізненням фази Δφ",
                      size=12, pad=6, fill="#f8fafc", stroke="#94a3b8", color="#334155")

    render(path, w, h, bg_vac, bg_med, interface, "".join(atoms), wave_vac, wave_med,
           "".join(labels), "".join(annots), box_mech,
           title="Мікроскопічний механізм затримки фазової швидкості світла")


def make_complex_index_fig():
    w, h = 760, 360
    path = os.path.join(IMG_DIR, 'complex-refractive-index.svg')

    ax_x = arrow(60, 220, 710, 220, color="#475569", sw=1.8)
    ax_y = arrow(60, 280, 60, 40, color="#475569", sw=1.8)

    labels = [
        text(725, 224, "z", size=14, color="#1e293b", bold=True),
        text(45, 30, "E(z)", size=14, color="#1e293b", bold=True),
        line(240, 50, 240, 260, color="#cbd5e1", sw=1.2, dash="3,3"),
        text(240, 275, "Межа розділу (z = 0)", size=12, color="#64748b", anchor="middle")
    ]

    m1 = fitbox(80, 60, 140, 30, "Середовище 1\n(n₁ = 1, k₁ = 0)", size=11, fill="#f1f5f9", stroke="#cbd5e1")
    m2 = fitbox(260, 60, 160, 30, "Поглинальне середовище 2\nñ₂ = n₂ + i·k₂", size=11, fill="#fef2f2", stroke="#fca5a5", color="#991b1b", bold=True)

    import math
    pts_inc = []
    for x in range(60, 241, 2):
        y = 150 - 60 * math.cos(2 * math.pi * (x - 60) / 70)
        pts_inc.append("%s%.1f %.1f" % ("M" if x == 60 else "L", x, y))
    w_inc = '<path d="%s" fill="none" stroke="#2563eb" stroke-width="2"/>' % " ".join(pts_inc)

    pts_trans = []
    pts_env_top = []
    pts_env_bot = []
    alpha = 0.0075
    for x in range(240, 701, 2):
        z = x - 240
        amp = 60 * math.exp(-alpha * z)
        y = 150 - amp * math.cos(2 * math.pi * z / 48)
        pts_trans.append("%s%.1f %.1f" % ("M" if x == 240 else "L", x, y))
        pts_env_top.append("%s%.1f %.1f" % ("M" if x == 240 else "L", x, 150 - amp))
        pts_env_bot.append("%s%.1f %.1f" % ("M" if x == 240 else "L", x, 150 + amp))

    w_trans = '<path d="%s" fill="none" stroke="#dc2626" stroke-width="2"/>' % " ".join(pts_trans)
    env_top = '<path d="%s" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4"/>' % " ".join(pts_env_top)
    env_bot = '<path d="%s" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4"/>' % " ".join(pts_env_bot)

    f1 = fitbox(470, 70, 220, 48, "Огинаюча згасання: E₀ · e⁻ᵏ⁽²ᵖⁱ z / λ₀⁾\nПоглинання Бугера: I(z) = I₀ · e⁻αᶻ", size=11, fill="#fff1f2", stroke="#fda4af", color="#9f1239")
    f2 = fitbox(470, 280, 240, 46, "Дійсна частина n → фазова швидкість v = c/n\nУявна частина k → коефіціент згасання", size=11, fill="#f0fdf4", stroke="#86efac", color="#166534")

    render(path, w, h, ax_x, ax_y, "".join(labels), m1, m2, w_inc, w_trans, env_top, env_bot, f1, f2,
           title="Комплексний показник заломлення ñ = n + i·k та згасання хвилі")


def make_dispersion_fig():
    w, h = 780, 380
    path = os.path.join(IMG_DIR, 'dispersion-curves.svg')

    ax_x = arrow(60, 300, 710, 300, color="#475569", sw=1.8)
    ax_y = arrow(60, 300, 60, 40, color="#475569", sw=1.8)

    labels = [
        text(725, 304, "Довжина хвилі λ", size=14, color="#1e293b", bold=True),
        text(45, 30, "n(λ)", size=14, color="#1e293b", bold=True),
        # Visible spectrum region
        rect(240, 70, 220, 230, fill="#fef08a", stroke="#fde047", sw=1, rx=0),
        text(350, 90, "Видимий діапазон", size=12, color="#854d0e", bold=True, anchor="middle"),
        # Resonance absorption band
        rect(550, 70, 90, 230, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=0),
        text(595, 90, "Смуга поглинання\n(Резонанс λ₀)", size=11, color="#991b1b", bold=True, anchor="middle")
    ]

    import math
    # Normal dispersion curve
    pts_norm = []
    for x in range(120, 540, 3):
        lam = (x - 60) / 100.0
        n_val = 1.30 + 0.25 / (lam * lam)
        y = 300 - (n_val - 1.0) * 160
        pts_norm.append("%s%.1f %.1f" % ("M" if x == 120 else "L", x, y))
    c_norm = '<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % " ".join(pts_norm)

    # Anomalous dispersion curve near resonance (540 to 645)
    pts_anom = []
    for x in range(540, 645, 2):
        dx = (x - 595) / 15.0
        n_val = 1.5 - 0.4 * dx / (1 + dx * dx)
        y = 300 - (n_val - 1.0) * 160
        pts_anom.append("%s%.1f %.1f" % ("M" if x == 540 else "L", x, y))
    c_anom = '<path d="%s" fill="none" stroke="#dc2626" stroke-width="2.5"/>' % " ".join(pts_anom)

    # Normal dispersion continuation after absorption (645 to 700)
    pts_after = []
    for x in range(645, 705, 3):
        lam = (x - 60) / 100.0
        n_val = 1.35 + 0.2 / (lam * lam)
        y = 300 - (n_val - 1.0) * 160
        pts_after.append("%s%.1f %.1f" % ("M" if x == 645 else "L", x, y))
    c_after = '<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % " ".join(pts_after)

    # t1 placed at left top (x=130, y=70), above curve
    t1 = fitbox(70, 70, 155, 46, "Нормальна дисперсія:\ndn/dλ < 0\n(синє заломлюється дужче)", size=10, fill="#eff6ff", stroke="#93c5fd", color="#1e40af")
    # t2 placed below axis or to the right
    t2 = fitbox(480, 318, 175, 46, "Аномальна дисперсія:\ndn/dλ > 0\n(у смузі поглинання)", size=10, fill="#fef2f2", stroke="#fca5a5", color="#991b1b")

    render(path, w, h, ax_x, ax_y, "".join(labels), c_norm, c_anom, c_after, t1, t2,
           title="Нормальна та аномальна дисперсія показника заломлення n(λ)")


def make_birefringence_fig():
    w, h = 760, 340
    path = os.path.join(IMG_DIR, 'anisotropy-birefringence.svg')

    crystal = rect(240, 80, 280, 180, fill="#f8fafc", stroke="#64748b", sw=2, rx=6)
    c_label = text(380, 105, "Одноосьовий кристал (наприклад, ісландський шпат)", size=13, color="#334155", bold=True, anchor="middle")

    opt_axis = line(260, 125, 500, 215, color="#94a3b8", sw=1.5, dash="6,4")
    opt_text = text(470, 235, "Оптична вісь кристала", size=11, color="#64748b", italic=True)

    ray_in = arrow(60, 170, 240, 170, color="#1e293b", sw=2.5)
    in_text = text(150, 155, "Неполяризований промінь", size=12, color="#1e293b", bold=True, anchor="middle")

    ray_o_inside = line(240, 170, 520, 150, color="#2563eb", sw=2)
    ray_o_out = arrow(520, 150, 700, 150, color="#2563eb", sw=2)
    t_o = text(610, 140, "Ззвичайний промінь (o-промінь, nₒ)", size=12, color="#1d4ed8", bold=True)

    ray_e_inside = line(240, 170, 520, 200, color="#dc2626", sw=2)
    ray_e_out = arrow(520, 200, 700, 200, color="#dc2626", sw=2)
    t_e = text(610, 220, "Незвичайний промінь (e-промінь, nₑ)", size=12, color="#b91c1c", bold=True)

    pol_o = circle(380, 160, 4, fill="#2563eb", stroke="#2563eb", sw=1)
    pol_e = line(380, 178, 380, 194, color="#dc2626", sw=2)

    box_summary = fitbox(100, 280, 560, 42,
                         "Подвійне променезаломлення (Δn = nₑ - nₒ): розщеплення променя на дві ортогонально поляризовані складові",
                         size=12, pad=6, fill="#f1f5f9", stroke="#cbd5e1", color="#1e293b")

    render(path, w, h, crystal, c_label, opt_axis, opt_text, ray_in, in_text,
           ray_o_inside, ray_o_out, t_o, ray_e_inside, ray_e_out, t_e, pol_o, pol_e, box_summary,
           title="Анізотропія та подвійне променезаломлення в одноосьовому кристалі")


def main():
    make_phase_delay_fig()
    make_complex_index_fig()
    make_dispersion_fig()
    make_birefringence_fig()
    print("All figures generated successfully!")


if __name__ == '__main__':
    main()
