# -*- coding: utf-8 -*-
"""
figs.py — Генерація SVG-фігур для теми "Тепловий шум (шум Джонсона — Найквіста)"
Книга: physics
Секція: condensed-matter-physics
Slug: thermal-noise
"""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, line, arrow, rect, circle, text, mtext,
    plus, minus, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def make_nyquist_transmission_line():
    """Фігура 1: Термодинамічне виведення Найквіста (лінія передачі між резисторами)."""
    w, h = 760, 360
    frags = []

    # Заголовок фігури
    frags.append(text(w / 2, 28, "Термодинамічна модель Найквіста: одновимірний резонатор", size=16, bold=True))

    # Лівий резистор R1 (Т1 = Т)
    frags.append(rect(30, 80, 130, 180, fill="#fdf2e9", stroke=POS, sw=2, rx=8))
    frags.append(text(95, 110, "Резистор R₁", size=14, bold=True, color=POS))
    frags.append(text(95, 135, "Опір: R", size=13, color=INK))
    frags.append(text(95, 160, "Температура: T", size=13, color=INK))
    frags.append(text(95, 190, "Шумова ЕРС U₁", size=13, bold=True, color=POS))
    frags.append(text(95, 215, "P₁ = k_B · T · B", size=12, color=INK))

    # Правий резистор R2 (Т2 = Т)
    frags.append(rect(600, 80, 130, 180, fill="#eaf2f8", stroke=NEG, sw=2, rx=8))
    frags.append(text(665, 110, "Резистор R₂", size=14, bold=True, color=NEG))
    frags.append(text(665, 135, "Опір: R", size=13, color=INK))
    frags.append(text(665, 160, "Температура: T", size=13, color=INK))
    frags.append(text(665, 190, "Шумова ЕРС U₂", size=13, bold=True, color=NEG))
    frags.append(text(665, 215, "P₂ = k_B · T · B", size=12, color=INK))

    # Лінія передачі (довжина L, імпеданс Z0 = R)
    frags.append(rect(160, 110, 440, 120, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(380, 135, "Безвтратна лінія передачі (хвильовий опір Z₀ = R)", size=13, bold=True, color=INK))
    frags.append(text(380, 155, "Довжина лінії L, густина мод dn/df = 2L / v", size=12, color=MUTED))

    # Моди стоячих хвиль всередині лінії
    pts1 = []
    pts2 = []
    for x_idx in range(180, 581, 5):
        y_val1 = 185 + 15 * math.sin(2 * math.pi * (x_idx - 180) / 100)
        y_val2 = 185 - 15 * math.sin(2 * math.pi * (x_idx - 180) / 100)
        pts1.append("%.1f,%.1f" % (x_idx, y_val1))
        pts2.append("%.1f,%.1f" % (x_idx, y_val2))
    
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(pts1), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(pts2), NEG))

    # Стрілки передачі потужності
    frags.append(arrow(200, 210, 360, 210, color=POS, sw=2))
    frags.append(text(280, 203, "Пряма хвиля P₁ →", size=11, bold=True, color=POS))

    frags.append(arrow(560, 210, 400, 210, color=NEG, sw=2))
    frags.append(text(480, 203, "← Зворотна хвиля P₂", size=11, bold=True, color=NEG))

    # Підсумок рівноваги знизу
    b1, _, _ = textbox(380, 305, 
                       "Термодинамічна рівновага: P_max = U_th² / (4R) = k_B · T · B  ⇒  U_th² = 4 · k_B · T · R · B", 
                       size=13, bold=True, fill="#e8f8f5", stroke=FIELD, sw=1.8, pad=10)
    frags.append(b1)

    render(os.path.join(OUT_DIR, "nyquist-transmission-line.svg"), w, h, *frags)


def make_fluctuation_dissipation():
    """Фігура 2: Двоїстість дисипації і флуктуацій та еквівалентні схеми Тевеніна й Нортона."""
    w, h = 780, 370
    frags = []

    frags.append(text(w / 2, 26, "Мікроскопічні флуктуації та шумові еквівалентні схеми", size=16, bold=True))

    # Блок 1: Мікроскопічний механізм
    frags.append(rect(20, 65, 230, 235, fill="#fef9e7", stroke="#f39c12", sw=1.8, rx=8))
    frags.append(text(135, 90, "Мікроскопічний стан", size=14, bold=True, color="#b7950b"))
    frags.append(text(135, 115, "Хаотичний рух носіїв", size=12, color=INK))
    frags.append(text(135, 135, "Теплова швидкість v_th", size=12, color=INK))
    frags.append(text(135, 155, "Час релаксації τ ~ 10⁻¹⁴ s", size=12, color=INK))

    for cx, cy, sign in [(60, 190, "+"), (110, 210, "-"), (160, 185, "-"), (200, 215, "+")]:
        if sign == "+":
            frags.append(plus(cx, cy, r=8))
        else:
            frags.append(minus(cx, cy, r=8))
    
    frags.append('<polyline points="45,240 85,255 125,235 165,260 205,245" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="2,2"/>' % MUTED)
    frags.append(text(135, 285, "Флуктуаційно-дисипативна теорема", size=11, bold=True, color=INK))

    frags.append(arrow(255, 180, 285, 180, color=LINE, sw=2))

    # Блок 2: Схема Тевеніна
    frags.append(rect(295, 65, 220, 235, fill="#fdf2e9", stroke=POS, sw=1.8, rx=8))
    frags.append(text(405, 90, "Схема Тевеніна", size=14, bold=True, color=POS))
    frags.append(text(405, 115, "Послідовний генератор", size=12, color=INK))
    
    frags.append(circle(405, 160, 18, fill="#ffffff", stroke=POS, sw=1.8))
    frags.append(text(405, 165, "~", size=20, bold=True, color=POS))
    frags.append(text(405, 195, "S_V(f) = 4 · k_B · T · R", size=12, bold=True, color=POS))
    
    frags.append(rect(370, 215, 70, 25, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(405, 232, "R (ідеальний)", size=10, bold=True, color=INK))
    frags.append(line(405, 178, 405, 215, color=LINE, sw=1.5))
    frags.append(line(405, 240, 405, 260, color=LINE, sw=1.5))

    frags.append(text(405, 285, "U_rms = √(4 · k_B · T · R · B)", size=11, bold=True, color=POS))

    # Блок 3: Схема Нортона
    frags.append(rect(535, 65, 225, 235, fill="#eaf2f8", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(647, 90, "Схема Нортона", size=14, bold=True, color=NEG))
    frags.append(text(647, 115, "Паралельний генератор", size=12, color=INK))
    
    frags.append(circle(605, 175, 18, fill="#ffffff", stroke=NEG, sw=1.8))
    frags.append(arrow(605, 188, 605, 162, color=NEG, sw=1.8))
    frags.append(rect(670, 162, 35, 26, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(687, 178, "G", size=11, bold=True, color=INK))
    
    frags.append(line(605, 140, 687, 140, color=LINE, sw=1.5))
    frags.append(line(605, 140, 605, 157, color=LINE, sw=1.5))
    frags.append(line(687, 140, 687, 162, color=LINE, sw=1.5))
    frags.append(line(605, 193, 605, 220, color=LINE, sw=1.5))
    frags.append(line(687, 188, 687, 220, color=LINE, sw=1.5))
    frags.append(line(605, 220, 687, 220, color=LINE, sw=1.5))

    frags.append(text(647, 240, "S_I(f) = 4 · k_B · T · G", size=12, bold=True, color=NEG))
    frags.append(text(647, 285, "I_rms = √(4 · k_B · T · G · B)", size=11, bold=True, color=NEG))

    b2, _, _ = textbox(w / 2, 335, 
                       "Принцип еквівалентності: обидві схеми дають однакову шумову потужність у навантаженні P = k_B · T · B",
                       size=12, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5, pad=8)
    frags.append(b2)

    render(os.path.join(OUT_DIR, "fluctuation-dissipation.svg"), w, h, *frags)


def make_planck_nyquist_spectrum():
    """Фігура 3: Спектральна щільність (класичний опис, квантова межа Планка, нульові коливання)."""
    w, h = 760, 400
    frags = []

    frags.append(text(w / 2, 26, "Спектр теплового шуму: від білого плато до квантового спаду", size=16, bold=True))

    ox, oy = 80, 320
    ax_w, ax_h = 630, 240
    
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=1.8))
    frags.append(text(ox + ax_w - 20, oy + 25, "Частота f (Гц, логарифмічний масштаб)", size=12, bold=True, color=INK))
    frags.append(text(ox - 50, oy - ax_h + 15, "СЩП S_V(f)", size=12, bold=True, color=INK))

    y_rj = oy - 140
    frags.append(line(ox, y_rj, ox + 420, y_rj, color=POS, sw=2, dash="6,4"))
    frags.append(text(220, y_rj - 10, "Класичний Найквіст: S_V = 4 · k_B · T · R (білий шум)", size=12, bold=True, color=POS))

    pts_planck = []
    pts_quantum_total = []
    for x_p in range(ox, ox + ax_w - 30, 5):
        rel_f = (x_p - ox) / 100.0
        if rel_f < 3.2:
            val_p = 1.0 / (1.0 + 0.05 * math.exp(rel_f))
        else:
            val_p = math.exp(-(rel_f - 3.2) * 1.5)
        
        y_p = oy - 140 * val_p
        pts_planck.append("%.1f,%.1f" % (x_p, y_p))

        y_zt = oy - (140 * val_p + 15 * rel_f)
        pts_quantum_total.append("%.1f,%.1f" % (x_p, y_zt))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_planck), FIELD))
    frags.append(text(460, oy - 60, "Квантовий спад Планка h f ≫ k_B T", size=12, bold=True, color=FIELD))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (" ".join(pts_quantum_total), NEG))
    frags.append(text(540, oy - 210, "+ Нульові коливання (h f / 2)", size=11, bold=True, color=NEG))

    frags.append(line(ox, oy, ox, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox, oy + 20, "1 Hz", size=11, color=MUTED))

    frags.append(line(ox + 180, oy, ox + 180, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox + 180, oy + 20, "1 GHz", size=11, color=MUTED))

    frags.append(line(ox + 360, oy, ox + 360, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox + 360, oy + 20, "f_th ≈ 6 THz (300K)", size=11, bold=True, color=INK))
    frags.append(line(ox + 360, oy - 10, ox + 360, oy - 250, color=MUTED, sw=1, dash="2,2"))

    frags.append(line(ox + 540, oy, ox + 540, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox + 540, oy + 20, "1/τ ≈ 16 THz (Друде)", size=11, bold=True, color=INK))

    b3, _, _ = textbox(360, 365, 
                       "В оптичному та кріогенному діапазонах (h f ≫ k_B T) термодинамічна формула поступається квантовій", 
                       size=12, bold=False, fill="#ffffff", stroke=LINE, sw=1.2, pad=6)
    frags.append(b3)

    render(os.path.join(OUT_DIR, "planck-nyquist-spectrum.svg"), w, h, *frags)


def make_rc_noise_bandwidth():
    """Фігура 4: Спектральне фільтрування в RC-колі та інтегральна дисперсія k_B T / C."""
    w, h = 760, 370
    frags = []

    frags.append(text(w / 2, 26, "Шум у RC-колі: еквівалентна смуга та дисперсія k_B T / C", size=16, bold=True))

    frags.append(rect(20, 65, 260, 235, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(150, 90, "Еквівалентна RC-схема", size=14, bold=True, color=INK))

    frags.append(circle(60, 160, 16, fill="#ffffff", stroke=POS, sw=1.8))
    frags.append(text(60, 165, "~", size=18, bold=True, color=POS))
    frags.append(text(60, 195, "U_th", size=11, bold=True, color=POS))

    frags.append(rect(100, 150, 50, 20, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(125, 164, "R", size=11, bold=True, color=INK))

    frags.append(line(200, 140, 200, 155, color=INK, sw=2))
    frags.append(line(185, 155, 215, 155, color=INK, sw=2))
    frags.append(line(185, 165, 215, 165, color=INK, sw=2))
    frags.append(line(200, 165, 200, 180, color=INK, sw=2))
    frags.append(text(225, 164, "C", size=11, bold=True, color=INK))

    frags.append(line(60, 144, 60, 160, color=LINE, sw=1.5))
    frags.append(line(60, 140, 100, 140, color=LINE, sw=1.5))
    frags.append(line(60, 140, 60, 144, color=LINE, sw=1.5))
    frags.append(line(150, 140, 200, 140, color=LINE, sw=1.5))
    frags.append(line(200, 140, 250, 140, color=LINE, sw=1.5))
    frags.append(line(60, 176, 60, 180, color=LINE, sw=1.5))
    frags.append(line(60, 180, 250, 180, color=LINE, sw=1.5))

    frags.append(text(150, 225, "Вихідна напруга U_out на C", size=12, bold=True, color=NEG))
    frags.append(text(150, 260, "S_out(f) = 4kTR / [1 + (2πfRC)²]", size=11, color=INK))

    ox, oy = 330, 270
    gw, gh = 400, 180
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    frags.append(text(ox + gw - 15, oy + 20, "Частота f", size=12, bold=True, color=INK))
    frags.append(text(ox - 35, oy - gh + 15, "S_out(f)", size=12, bold=True, color=INK))

    pts_lorenz = []
    for x_idx in range(0, gw - 20, 4):
        f_val = x_idx / 40.0
        s_val = 1.0 / (1.0 + f_val * f_val)
        pts_lorenz.append("%.1f,%.1f" % (ox + x_idx, oy - gh * 0.75 * s_val))

    bw_eq = 60
    frags.append(rect(ox, oy - gh * 0.75, bw_eq, gh * 0.75, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=0))
    frags.append(text(ox + 70, oy - gh * 0.4, "B_eq = 1 / (4RC)", size=11, bold=True, color=FIELD))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_lorenz), POS))

    b4, _, _ = textbox(w / 2, 335, 
                       "Інтеграл шуму по всіх частотах:  ⟨U_C²⟩ = ∫₀^∞ S_out(f) df = k_B · T / C  (не залежить від R!)", 
                       size=13, bold=True, fill="#eaf2f8", stroke=NEG, sw=1.8, pad=10)
    frags.append(b4)

    render(os.path.join(OUT_DIR, "rc-noise-bandwidth.svg"), w, h, *frags)


if __name__ == "__main__":
    make_nyquist_transmission_line()
    make_fluctuation_dissipation()
    make_planck_nyquist_spectrum()
    make_rc_noise_bandwidth()
    print("Всі 4 фігури для thermal-noise успішно згенеровано у img/")
