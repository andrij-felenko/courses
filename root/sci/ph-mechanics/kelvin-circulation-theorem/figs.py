# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Деформація рідкого контуру в часі ────────────────────────────────
def fig_material_contour():
    W, H = 720, 360
    body = []

    # Траєкторії/лінії течії (фоновий потік)
    for y_offset in [-100, -50, 0, 50, 100]:
        d_stream = f"M 40 {180 + y_offset} C 200 {170 + y_offset * 0.8}, 500 {190 + y_offset * 1.1}, 680 {180 + y_offset}"
        body.append(f'<path d="{d_stream}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4 4"/>')

    # Контур 1 у момент t1
    d_c1 = "M 120 180 C 120 130, 200 130, 220 180 C 240 230, 140 240, 120 180 Z"
    body.append(f'<path d="{d_c1}" fill="{FILL}" stroke="{POS}" stroke-width="2.2"/>')

    # Позначення контуру C(t1)
    body.append(fitbox(70, 75, 75, 32, "C(t₁)", size=13, bold=True, stroke=POS, fill=FILL, color=POS))

    # Елемент dr та вектор швидкості u на C(t1)
    body.append(arrow(180, 138, 220, 125, color=FIELD, sw=2.0))
    body.append(text(228, 118, "u", size=13, color=FIELD, bold=True))

    body.append(arrow(180, 138, 198, 132, color=POS, sw=2.5))
    body.append(text(182, 158, "dr", size=12, color=POS, bold=True))

    # Стрілка еволюції в часі
    body.append(arrow(260, 180, 420, 180, color=MUTED, sw=2.0))
    body.append(fitbox(275, 135, 130, 28, "рух за часом t", size=11, stroke=MUTED, fill=FILL, color=MUTED))

    # Контур 2 у момент t2 (витягнутий і повернутий)
    d_c2 = "M 460 180 C 470 100, 580 120, 640 170 C 680 230, 520 270, 460 180 Z"
    body.append(f'<path d="{d_c2}" fill="{FILL}" stroke="{FIELD}" stroke-width="2.2"/>')

    # Позначення контуру C(t2)
    body.append(fitbox(580, 55, 75, 32, "C(t₂)", size=13, bold=True, stroke=FIELD, fill=FILL, color=FIELD))

    # Елемент dr' та u' на C(t2)
    body.append(arrow(550, 123, 600, 125, color=FIELD, sw=2.0))
    body.append(text(610, 120, "u'", size=13, color=FIELD, bold=True))

    body.append(arrow(550, 123, 575, 124, color=FIELD, sw=2.5))
    body.append(text(555, 145, "dr'", size=12, color=FIELD, bold=True))

    # Текст збереження циркуляції внизу
    body.append(fitbox(150, 305, 420, 38, "Γ = ∮ C(t₁) u · dr = ∮ C(t₂) u' · dr' = const", size=13, bold=True, stroke=POS, fill=FILL, color=INK))

    render(os.path.join(OUT, "fig1-material-contour.svg"), W, H, "".join(body))


# ── Фігура 2: Розтягнення вихрової трубки ──────────────────────────────────────
def fig_vortex_stretching():
    W, H = 720, 360
    body = []

    # Лівий циліндр (короткий і товстий)
    body.append(f'<ellipse cx="140" cy="180" rx="35" ry="75" fill="{FILL}" stroke="{POS}" stroke-width="2"/>')
    body.append(f'<path d="M 140 105 L 260 105 A 35 75 0 0 1 260 255 L 140 255 Z" fill="{FILL}" stroke="none"/>')
    body.append(f'<line x1="140" y1="105" x2="260" y2="105" stroke="{POS}" stroke-width="2"/>')
    body.append(f'<line x1="140" y1="255" x2="260" y2="255" stroke="{POS}" stroke-width="2"/>')
    body.append(f'<ellipse cx="260" cy="180" rx="35" ry="75" fill="{BG}" stroke="{POS}" stroke-width="2"/>')

    # Вектор вихровості ω1
    body.append(arrow(140, 180, 260, 180, color=POS, sw=3.0))
    body.append(text(190, 170, "ω₁", size=15, color=POS, bold=True))

    # Розміри 1
    body.append(fitbox(220, 30, 95, 30, "Площа A₁", size=12, stroke=POS, fill=FILL, color=POS))
    body.append(fitbox(150, 275, 100, 30, "Довжина L₁", size=12, stroke=LINE, fill=FILL, color=INK))

    # Стрілка витягування
    body.append(arrow(310, 180, 400, 180, color=FIELD, sw=2.5))
    body.append(fitbox(305, 125, 105, 42, "аксіальне\nрозтягнення", size=11, stroke=FIELD, fill=FILL, color=FIELD))

    # Правий циліндр (довгий і тонкий)
    body.append(f'<ellipse cx="450" cy="180" rx="15" ry="32" fill="{FILL}" stroke="{FIELD}" stroke-width="2"/>')
    body.append(f'<path d="M 450 148 L 650 148 A 15 32 0 0 1 650 212 L 450 212 Z" fill="{FILL}" stroke="none"/>')
    body.append(f'<line x1="450" y1="148" x2="650" y2="148" stroke="{FIELD}" stroke-width="2"/>')
    body.append(f'<line x1="450" y1="212" x2="650" y2="212" stroke="{FIELD}" stroke-width="2"/>')
    body.append(f'<ellipse cx="650" cy="180" rx="15" ry="32" fill="{BG}" stroke="{FIELD}" stroke-width="2"/>')

    # Вектор вихровості ω2 (більший)
    body.append(arrow(450, 180, 650, 180, color=FIELD, sw=4.0))
    body.append(text(540, 170, "ω₂ > ω₁", size=15, color=FIELD, bold=True))

    # Розміри 2
    body.append(fitbox(565, 80, 120, 30, "Площа A₂ < A₁", size=12, stroke=FIELD, fill=FILL, color=FIELD))
    body.append(fitbox(490, 235, 125, 30, "Довжина L₂ > L₁", size=12, stroke=LINE, fill=FILL, color=INK))

    # Текст збереження інтенсивності вихрової трубки
    body.append(fitbox(190, 315, 340, 35, "Γ = ω₁ · A₁ = ω₂ · A₂ = const", size=13, bold=True, stroke=FIELD, fill=FILL, color=INK))

    render(os.path.join(OUT, "fig2-vortex-stretching.svg"), W, H, "".join(body))


# ── Фігура 3: Бароклінний момент та генерація вихровості ─────────────────────
def fig_baroclinic_torque():
    W, H = 720, 360
    body = []

    # Сітка ізобар p = const (горизонтальні нахилені лінії)
    for i, y in enumerate([80, 140, 200, 260]):
        body.append(f'<line x1="60" y1="{y}" x2="660" y2="{y - 40}" stroke="{POS}" stroke-width="1.8"/>')
        body.append(text(665, y - 42, f"p_{i}", size=11, color=POS, bold=True))

    # Градієнт тиску ∇p (перпендикулярно до ізобар)
    body.append(arrow(220, 180, 200, 100, color=POS, sw=2.5))
    body.append(text(175, 95, "∇p", size=14, color=POS, bold=True))

    # Сітка ізопікн ρ = const (похилі під іншим кутом)
    for i, y in enumerate([60, 130, 200, 270]):
        body.append(f'<line x1="60" y1="{y + 40}" x2="660" y2="{y - 80}" stroke="{FIELD}" stroke-width="1.8" stroke-dasharray="6 4"/>')
        body.append(text(665, y - 82, f"ρ_{i}", size=11, color=FIELD, bold=True))

    # Градієнт густини ∇ρ
    body.append(arrow(220, 180, 290, 110, color=FIELD, sw=2.5))
    body.append(text(300, 105, "∇ρ", size=14, color=FIELD, bold=True))

    # Кругова стрілка соленоїдального моменту ∇ρ × ∇p
    d_arc = "M 250 210 A 45 45 0 1 0 180 200"
    body.append(f'<path d="{d_arc}" fill="none" stroke="{NEG}" stroke-width="2.8"/>')
    body.append(arrow(185, 205, 178, 195, color=NEG, sw=2.8))

    body.append(fitbox(260, 215, 230, 36, "бароклінний момент (∇ρ × ∇p) / ρ²", size=11, bold=True, stroke=NEG, fill=FILL, color=NEG))

    # Пояснення
    body.append(fitbox(60, 15, 140, 28, "Ізобари p = const", size=11, stroke=POS, fill=FILL, color=POS))
    body.append(fitbox(220, 15, 140, 28, "Ізопікни ρ = const", size=11, stroke=FIELD, fill=FILL, color=FIELD))

    # Підсумкове рівняння
    body.append(fitbox(160, 310, 400, 36, "dΓ/dt = ∬ (1/ρ²) (∇ρ × ∇p) · dA ≠ 0", size=13, bold=True, stroke=LINE, fill=FILL, color=INK))

    render(os.path.join(OUT, "fig3-baroclinic-torque.svg"), W, H, "".join(body))


# ── Фігура 4: Початковий вихор при старті аеродинамічного профілю ────────────
def fig_starting_vortex():
    W, H = 720, 360
    body = []

    # Аеродинамічний профіль
    d_airfoil = "M 140 180 C 180 140, 340 140, 400 180 C 340 200, 200 200, 140 180 Z"
    body.append(f'<path d="{d_airfoil}" fill="{FILL}" stroke="{LINE}" stroke-width="2"/>')

    # Набігаючий потік (стрілки ліворуч)
    for y in [100, 140, 180, 220, 260]:
        body.append(arrow(40, y, 110, y, color=FIELD, sw=1.8))
    body.append(fitbox(30, 40, 155, 30, "набігаючий потік U", size=11, stroke=FIELD, fill=FILL, color=FIELD))

    # Замкнений контур C навколо всієї системи (профіль + початковий вихор)
    body.append(f'<rect x="90" y="80" width="560" height="225" rx="15" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    body.append(text(105, 100, "великий контур C", size=12, color=MUTED, bold=True))

    # Циркуляція навколо крила +Γ (приєднаний вихор)
    d_circ1 = "M 270 120 A 70 50 0 1 1 269 120"
    body.append(f'<path d="{d_circ1}" fill="none" stroke="{POS}" stroke-width="2.2" stroke-dasharray="4 3"/>')
    body.append(arrow(260, 120, 240, 123, color=POS, sw=2.2))
    body.append(fitbox(200, 135, 150, 32, "приєднаний вихор +Γ", size=12, bold=True, stroke=POS, fill=FILL, color=POS))

    # Початковий вихор -Γ біля задньої кромки
    d_circ2 = "M 510 160 A 35 35 0 1 0 510 230 A 35 35 0 1 0 510 160"
    body.append(f'<path d="{d_circ2}" fill="{FILL}" stroke="{NEG}" stroke-width="2.2"/>')
    body.append(arrow(510, 230, 525, 225, color=NEG, sw=2.2))
    body.append(fitbox(450, 245, 150, 32, "початковий вихор -Γ", size=12, bold=True, stroke=NEG, fill=FILL, color=NEG))

    # Текст закону збереження циркуляції
    body.append(fitbox(150, 315, 420, 35, "Γ_загальна = Γ_крила (+Γ) + Γ_початковий (-Γ) = 0", size=12, bold=True, stroke=LINE, fill=FILL, color=INK))

    render(os.path.join(OUT, "fig4-starting-vortex.svg"), W, H, "".join(body))


if __name__ == '__main__':
    fig_material_contour()
    fig_vortex_stretching()
    fig_baroclinic_torque()
    fig_starting_vortex()
    print("Figures generated successfully.")
