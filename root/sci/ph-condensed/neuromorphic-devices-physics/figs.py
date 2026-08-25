# -*- coding: utf-8 -*-
import sys
import os

# '..' 4 рази до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def gen_fig1(out_dir):
    """Фігура 1: Пластичність STDP та фізика часово-залежної модифікації ваги."""
    w, h = 800, 420
    frags = []

    # Заголовок
    frags.append(text(w/2, 25, "Пластичність STDP (Spike-Timing-Dependent Plasticity)", size=16, bold=True))

    # Вісі координат
    ox, oy = 400, 220
    frags.append(line(50, oy, 750, oy, color=LINE, sw=1.5))
    frags.append(arrow(750, oy, 770, oy, color=LINE, sw=1.5))
    frags.append(text(760, oy + 20, "Δt = t_post − t_pre (мс)", size=11, color=INK, anchor="end", italic=True))

    frags.append(line(ox, 370, ox, 50, color=LINE, sw=1.5))
    frags.append(arrow(ox, 50, ox, 35, color=LINE, sw=1.5))
    frags.append(text(ox + 15, 45, "Зміна ваги Δw (%)", size=11, color=INK, anchor="start", italic=True))

    # Області LTP та LTD
    ltd_path = "M 80 %d Q 260 %d 380 %d" % (oy + 15, oy + 25, oy + 130)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ltd_path, NEG))

    ltp_path = "M 420 %d Q 540 %d 720 %d" % (oy - 130, oy - 25, oy - 15)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ltp_path, POS))

    # Пунктирні лінії зв'язку імпульсів
    frags.append(line(380, oy, 380, oy + 130, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(420, oy - 130, 420, oy, color=MUTED, sw=1, dash="4,4"))

    # Блоки опису процесів
    frags.append(fitbox(80, 70, 280, 110, 
                        "Довготривала депресія (LTD)\nΔt < 0 (Post спайк перед Pre)\nΔw < 0 → Зменшення провідності G\nФізика: зворотний дрейф іонів / розрив нитки", 
                        size=11, fill="#eff6ff", stroke=NEG, min_w=280))

    frags.append(fitbox(440, 70, 280, 110, 
                        "Довготривала потенціація (LTP)\nΔt > 0 (Pre спайк перед Post)\nΔw > 0 → Збільшення провідності G\nФізика: дрейф кисневих вакансій / добудова нитки", 
                        size=11, fill="#fef2f2", stroke=POS, min_w=280))

    frags.append(fitbox(150, 310, 500, 75,
                        "Рівняння пластичності: Δw = A₊ · exp(−Δt / τ₊) при Δt > 0, та Δw = −A₋ · exp(Δt / τ₋) при Δt < 0\nЧасове вікно пластичності τ₊, τ₋ визначається кінетикою міграції дефектів у диелектрику.",
                        size=10, fill="#f8fafc", stroke=MUTED, min_w=500))

    render(os.path.join(out_dir, "stdp-curve-physics.svg"), w, h, *frags)

def gen_fig2(out_dir):
    """Фігура 2: Механізм переключення опору у нитковому ReRAM/OxRAM (LRS проти HRS)."""
    w, h = 800, 420
    frags = []

    frags.append(text(w/2, 25, "Фізика резистивного переключення у OxRAM (ReRAM)", size=16, bold=True))

    # Ліва панель: LRS
    frags.append(rect(30, 55, 350, 345, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    frags.append(text(205, 80, "Стан LRS (SET): Низький опір (Вмикання)", size=13, color=FIELD, bold=True))

    frags.append(fitbox(50, 105, 310, 35, "Верхній електрод (TE: TiN / Pt) — Напруга V > 0", size=10, fill="#e2e8f0", stroke="#64748b"))
    frags.append(fitbox(50, 245, 310, 35, "Нижній електрод (BE: TiN / Pt) — Заземлення (GND)", size=10, fill="#e2e8f0", stroke="#64748b"))

    frags.append(rect(50, 140, 310, 105, fill="#fef9c3", stroke="#eab308", sw=1))
    frags.append(text(80, 155, "Оксидна матриця HfO₂ / TiO₂", size=10, color="#854d0e", anchor="start"))

    frags.append(rect(185, 140, 40, 105, fill="#b91c1c", stroke="#7f1d1d", sw=1.5, rx=2))
    frags.append(text(205, 192, "Нитка V_O", size=10, color="#ffffff", bold=True))

    frags.append(fitbox(50, 290, 310, 95, 
                        "1. Електричне поле розриває зв'язки Hf-O.\n2. Іони O²⁻ мігрують до TE, залишаючи вакансії V_Oⁿ⁺.\n3. Сформовано суцільний місток → металевий/омічний опір R_SET.", size=10, fill="#ecfdf5", stroke=FIELD, min_w=310))

    # Права панель: HRS
    frags.append(rect(420, 55, 350, 345, fill="#f8fafc", stroke=POS, sw=2, rx=8))
    frags.append(text(595, 80, "Стан HRS (RESET): Високий опір (Вимкнення)", size=13, color=POS, bold=True))

    frags.append(fitbox(440, 105, 310, 35, "Верхній електрод (TE) — Зворотна напруга V < 0", size=10, fill="#e2e8f0", stroke="#64748b"))
    frags.append(fitbox(440, 245, 310, 35, "Нижній електрод (BE) — Заземлення (GND)", size=10, fill="#e2e8f0", stroke="#64748b"))

    frags.append(rect(440, 140, 310, 105, fill="#fef9c3", stroke="#eab308", sw=1))
    frags.append(text(470, 155, "Оксидна матриця HfO₂", size=10, color="#854d0e", anchor="start"))

    frags.append(rect(575, 175, 40, 70, fill="#b91c1c", stroke="#7f1d1d", sw=1.5, rx=2))
    frags.append(rect(575, 140, 40, 35, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    frags.append(text(595, 158, "Зазор Δx", size=10, color="#854d0e", bold=True))
    frags.append(text(595, 210, "Залишок", size=9, color="#ffffff"))

    frags.append(fitbox(440, 290, 310, 95, 
                        "1. Джоулів нагрів розігріває локальну область нитки.\n2. Іони O²⁻ повертаються з TE і рекомбінують з вакансіями.\n3. Виникає тунельний діелектричний зазор → опір R_RESET.", size=10, fill="#fff1f2", stroke=POS, min_w=310))

    render(os.path.join(out_dir, "memristor-filament-switching.svg"), w, h, *frags)

def gen_fig3(out_dir):
    """Фігура 3: Аналогова матриця кросбар для множення матриці на вектор (MVM)."""
    w, h = 800, 440
    frags = []

    frags.append(text(w/2, 25, "Аналогове множення вектор-матриця (MVM) у Кросбар-матриці", size=16, bold=True))

    frags.append(line(80, 100, 680, 100, color=LINE, sw=2))
    frags.append(text(65, 100, "V₁", size=13, color=POS, bold=True))
    frags.append(line(80, 180, 680, 180, color=LINE, sw=2))
    frags.append(text(65, 180, "V₂", size=13, color=POS, bold=True))
    frags.append(line(80, 260, 680, 260, color=LINE, sw=2))
    frags.append(text(65, 260, "V₃", size=13, color=POS, bold=True))

    frags.append(line(200, 60, 200, 330, color=NEG, sw=2))
    frags.append(arrow(200, 330, 200, 355, color=NEG, sw=2))
    frags.append(text(200, 375, "I₁ = Σ V_i · G_i1", size=12, color=NEG, bold=True))

    frags.append(line(400, 60, 400, 330, color=NEG, sw=2))
    frags.append(arrow(400, 330, 400, 355, color=NEG, sw=2))
    frags.append(text(400, 375, "I₂ = Σ V_i · G_i2", size=12, color=NEG, bold=True))

    frags.append(line(600, 60, 600, 330, color=NEG, sw=2))
    frags.append(arrow(600, 330, 600, 355, color=NEG, sw=2))
    frags.append(text(600, 375, "I₃ = Σ V_i · G_i3", size=12, color=NEG, bold=True))

    nodes = [
        (200, 100, "G₁₁"), (400, 100, "G₁₂"), (600, 100, "G₁₃"),
        (200, 180, "G₂₁"), (400, 180, "G₂₂"), (600, 180, "G₂₃"),
        (200, 260, "G₃₁"), (400, 260, "G₃₂"), (600, 260, "G₃₃")
    ]

    for cx, cy, g_lbl in nodes:
        frags.append(circle(cx, cy, 18, fill="#fef08a", stroke="#ca8a04", sw=1.5))
        frags.append(text(cx, cy + 4, g_lbl, size=10, color="#854d0e", bold=True))

    frags.append(fitbox(60, 395, 320, 40, "1. Закон Ома у кожному вузлі: I_ij = V_i · G_ij", size=11, fill="#f8fafc", stroke=MUTED, min_w=320))
    frags.append(fitbox(420, 395, 320, 40, "2. 1-е правило Кірхгофа у стовпці: I_j = Σ_i I_ij", size=11, fill="#f8fafc", stroke=MUTED, min_w=320))

    render(os.path.join(out_dir, "crossbar-mvm-kirchhoff.svg"), w, h, *frags)

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out, exist_ok=True)
    gen_fig1(out)
    gen_fig2(out)
    gen_fig3(out)
    print("Figures generated successfully.")
