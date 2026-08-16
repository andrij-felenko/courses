# -*- coding: utf-8 -*-
"""Фігури до теми «Теплопровідність матеріалів (λ)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольорова палітра
HOT   = "#c0392b"  # Гаряче / висока T
COLD  = "#2457d6"  # Холодне / низька T
ELECTRON = "#e74c3c" # Електрони
PHONON   = "#27ae60" # Фонони / решітка
GAS      = "#8e44ad" # Газ / молекули
METAL    = "#d35400" # Метал
GLASS    = "#7f8c8d" # Скло / аморфний
BORDER   = "#333333"

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))

# ── Фігура 1: Закон Фурьє (fourier-gradient.svg) ─────────────────────────────
def fig_fourier_gradient():
    W, H = 800, 480
    f = [text(W / 2, 28, "Закон Фурьє: Градієнт температури та тепловий потік q", size=16, bold=True)]

    sX, sY = 160, 100
    sW, sH = 260, 260
    
    f.append(rect(sX - 30, sY, 30, sH, fill="#fdecea", stroke=HOT, sw=2))
    f.append(text(sX - 15, sY + sH/2 - 10, "T₁", size=16, color=HOT, bold=True))
    f.append(text(sX - 15, sY + sH/2 + 15, "(гаряче)", size=11, color=HOT))

    f.append(rect(sX, sY, sW, sH, fill="#f8f9fa", stroke=BORDER, sw=1.5))
    f.append(text(sX + sW/2, sY + 25, "Матеріал із теплопровідністю λ", size=13, bold=True))

    f.append(rect(sX + sW, sY, 30, sH, fill="#eaf0fd", stroke=COLD, sw=2))
    f.append(text(sX + sW + 15, sY + sH/2 - 10, "T₂", size=16, color=COLD, bold=True))
    f.append(text(sX + sW + 15, sY + sH/2 + 15, "(холодне)", size=11, color=COLD))

    p1 = (sX, sY + 70)
    p2 = (sX + sW, sY + 210)
    f.append(line(p1[0], p1[1], p2[0], p2[1], color=HOT, sw=3))
    f.append(circle(p1[0], p1[1], 4, fill=HOT, stroke=HOT))
    f.append(circle(p2[0], p2[1], 4, fill=COLD, stroke=COLD))

    f.append(text(sX + sW/2 - 20, sY + 125, "dT/dx = (T₂ - T₁)/L < 0", size=12, color=INK, italic=True))

    f.append(arrow(sX + 40, sY + sH - 40, sX + sW - 40, sY + sH - 40, color=HOT, sw=3.5))
    f.append(text(sX + sW/2, sY + sH - 55, "Тепловий потік q = -λ · (dT/dx)", size=13, color=HOT, bold=True))

    f.append(arrow(sX, sY + sH + 25, sX + sW, sY + sH + 25, color=BORDER, sw=1.5))
    f.append(arrow(sX + sW, sY + sH + 25, sX, sY + sH + 25, color=BORDER, sw=1.5))
    f.append(text(sX + sW/2, sY + sH + 42, "Товщина шару L", size=12, color=BORDER))

    pX = 480
    f.append(rect(pX, sY, 280, sH + 50, fill="#ffffff", stroke="#d1d5db", sw=1.5))
    f.append(text(pX + 140, sY + 25, "Вплив величини λ", size=14, bold=True))

    f.append(text(pX + 20, sY + 65, "Висока λ (напр. мідь):", size=12, bold=True, color=FIELD))
    f.append(line(pX + 20, sY + 95, pX + 240, sY + 115, color=FIELD, sw=2.5))
    f.append(arrow(pX + 20, sY + 130, pX + 220, sY + 130, color=FIELD, sw=2.5))
    f.append(text(pX + 130, sY + 145, "Великий потік q при малому ΔT", size=11, color=FIELD))

    f.append(text(pX + 20, sY + 185, "Низька λ (напр. вата):", size=12, bold=True, color=HOT))
    f.append(line(pX + 20, sY + 205, pX + 240, sY + 265, color=HOT, sw=2.5))
    f.append(arrow(pX + 20, sY + 280, pX + 100, sY + 280, color=HOT, sw=1.8))
    f.append(text(pX + 130, sY + 295, "Малий потік q (теплоізоляція)", size=11, color=HOT))

    render(os.path.join(IMG, "fourier-gradient.svg"), W, H, *f)

# ── Фігура 2: Мікроскопічні механізми (microscopic-mechanisms.svg) ───────────
def fig_microscopic_mechanisms():
    W, H = 820, 460
    f = [text(W / 2, 28, "Мікроскопічні носії тепла у різних фазах і матеріалах", size=16, bold=True)]

    box1_x, box_y, box_w, box_h = 30, 60, 240, 360
    f.append(rect(box1_x, box_y, box_w, box_h, fill="#fff6f0", stroke=METAL, sw=1.5))
    f.append(text(box1_x + box_w/2, box_y + 25, "1. Метали (λ ~ 100–400)", size=13, color=METAL, bold=True))
    f.append(text(box1_x + box_w/2, box_y + 42, "Електронна теплопровідність", size=11, color=INK))

    for ix in [box1_x + 50, box1_x + 120, box1_x + 190]:
        for iy in [box_y + 80, box_y + 140, box_y + 200]:
            f.append(circle(ix, iy, 12, fill="#fbeee6", stroke=METAL, sw=1.5))
            f.append(text(ix, iy + 4, "+", size=12, color=METAL, bold=True))

    for ex, ey, dx, dy in [
        (box1_x + 30, box_y + 100, 35, 10),
        (box1_x + 90, box_y + 160, 40, -15),
        (box1_x + 150, box_y + 110, 30, 25),
        (box1_x + 70, box_y + 220, 45, -5)
    ]:
        f.append(circle(ex, ey, 5, fill=HOT, stroke=HOT))
        f.append(arrow(ex, ey, ex + dx, ey + dy, color=HOT, sw=1.5))

    f.append(mtext(box1_x + box_w/2, box_y + 265, 
                   ["• λ = λ_e + λ_ph (λ_e >> λ_ph)", "• Вільне електронне море", "• Закон Віддемана-Франца", "• λ/σ = L·T = const"], 
                   size=11, color=INK))

    box2_x = 290
    f.append(rect(box2_x, box_y, box_w, box_h, fill="#f0fff4", stroke=PHONON, sw=1.5))
    f.append(text(box2_x + box_w/2, box_y + 25, "2. Кристали (λ ~ 10–2000)", size=13, color=PHONON, bold=True))
    f.append(text(box2_x + box_w/2, box_y + 42, "Фононний перенос (решітка)", size=11, color=INK))

    grid_nodes = []
    for ix in [box2_x + 50, box2_x + 120, box2_x + 190]:
        for iy in [box_y + 80, box_y + 140, box_y + 200]:
            grid_nodes.append((ix, iy))
            f.append(circle(ix, iy, 10, fill="#e8f8f0", stroke=PHONON, sw=1.5))

    for i, (x1, y1) in enumerate(grid_nodes):
        for j, (x2, y2) in enumerate(grid_nodes):
            if i < j and ((abs(x1-x2) == 70 and y1 == y2) or (abs(y1-y2) == 60 and x1 == x2)):
                f.append(line(x1, y1, x2, y2, color="#a3e4d7", sw=1.5, dash="2,2"))

    f.append(path("M %d %d Q %d %d %d %d T %d %d" % 
                  (box2_x + 30, box_y + 140, box2_x + 60, box_y + 120, box2_x + 100, box_y + 140, box2_x + 180, box_y + 140),
                  fill="none", stroke=PHONON, sw=2.5))
    f.append(arrow(box2_x + 170, box_y + 140, box2_x + 210, box_y + 140, color=PHONON, sw=2))

    f.append(mtext(box2_x + box_w/2, box_y + 265, 
                   ["• λ = (1/3)·c_v·v·l", "• Кванти коливань (фонони)", "• Довжина пробігу l", "• Розсіювання Умкляппа (1/T)"], 
                   size=11, color=INK))

    box3_x = 550
    f.append(rect(box3_x, box_y, box_w, box_h, fill="#f5f0ff", stroke=GAS, sw=1.5))
    f.append(text(box3_x + box_w/2, box_y + 25, "3. Гази (λ ~ 0.01–0.15)", size=13, color=GAS, bold=True))
    f.append(text(box3_x + box_w/2, box_y + 42, "Молекулярні зіткнення", size=11, color=INK))

    for gx, gy, dx, dy in [
        (box3_x + 40, box_y + 80, 25, 30),
        (box3_x + 110, box_y + 120, -30, 20),
        (box3_x + 180, box_y + 90, -20, 40),
        (box3_x + 70, box_y + 170, 45, -25),
        (box3_x + 160, box_y + 210, -40, -30)
    ]:
        f.append(circle(gx, gy, 7, fill="#e8daef", stroke=GAS, sw=1.5))
        f.append(arrow(gx, gy, gx + dx, gy + dy, color=GAS, sw=1.5))

    f.append(mtext(box3_x + box_w/2, box_y + 265, 
                   ["• λ = (1/3)·ρ·v_avg·l·c_v", "• Незалежить від тиску P!", "• Висока у легких газах (He, H₂)", "• Вакуум: ефект Кнудсена"], 
                   size=11, color=INK))

    render(os.path.join(IMG, "microscopic-mechanisms.svg"), W, H, *f)

# ── Фігура 3: Температурна залежність λ(T) (phonon-lambda-temp.svg) ───────────
def fig_phonon_lambda_temp():
    W, H = 800, 480
    f = [text(W / 2, 28, "Залежність теплопровідності λ(T) від температури", size=16, bold=True)]

    ox, oy = 90, 390
    gx_w, gy_h = 650, 310

    f.append(arrow(ox, oy, ox + gx_w, oy, color=BORDER, sw=2))
    f.append(arrow(ox, oy, ox, oy - gy_h, color=BORDER, sw=2))

    f.append(text(ox + gx_w - 30, oy + 25, "Температура T (K)", size=13, bold=True))
    f.append(mtext(ox - 50, oy - gy_h + 30, ["Теплопровідність", "λ (Вт/(м·К))"], size=13, bold=True))

    f.append(line(ox + 120, oy, ox + 120, oy + 5, color=BORDER))
    f.append(text(ox + 120, oy + 20, "20 K", size=11))
    f.append(line(ox + 280, oy, ox + 280, oy + 5, color=BORDER))
    f.append(text(ox + 280, oy + 20, "100 K (Debye θ_D)", size=11))
    f.append(line(ox + 550, oy, ox + 550, oy + 5, color=BORDER))
    f.append(text(ox + 550, oy + 20, "300 K (кімнатна)", size=11))

    c1_path = ("M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % 
               (ox + 10, oy - 10,
                ox + 100, oy - 80, ox + 180, oy - 290, ox + 220, oy - 290,
                ox + 300, oy - 180, ox + 450, oy - 110, ox + 620, oy - 80))
    f.append(path(c1_path, fill="none", stroke=PHONON, sw=3))
    f.append(text(ox + 250, oy - 295, "Монокристал (напр. чистий Алмаз/Si)", size=12, color=PHONON, bold=True))

    f.append(text(ox + 80, oy - 120, "λ ~ T³ (межі)", size=11, color=PHONON, italic=True))
    f.append(text(ox + 380, oy - 160, "λ ~ 1/T (Умкляпп)", size=11, color=PHONON, italic=True))

    c2_path = ("M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % 
               (ox + 10, oy - 15,
                ox + 80, oy - 120, ox + 140, oy - 210, ox + 180, oy - 210,
                ox + 260, oy - 170, ox + 420, oy - 160, ox + 620, oy - 150))
    f.append(path(c2_path, fill="none", stroke=METAL, sw=2.5, dash="6,3"))
    f.append(text(ox + 460, oy - 175, "Метал (Мідь/Алюміній)", size=12, color=METAL, bold=True))

    c3_path = ("M %d %d C %d %d, %d %d, %d %d" % 
               (ox + 10, oy - 8, ox + 200, oy - 25, ox + 400, oy - 40, ox + 620, oy - 55))
    f.append(path(c3_path, fill="none", stroke=GLASS, sw=2.5))
    f.append(text(ox + 480, oy - 40, "Аморфне скло / Полімер", size=12, color=GLASS, bold=True))

    render(os.path.join(IMG, "phonon-lambda-temp.svg"), W, H, *f)

# ── Фігура 4: Температуропровідність α проти λ (thermal-diffusivity-front.svg) ─
def fig_thermal_diffusivity_front():
    W, H = 800, 480
    f = [text(W / 2, 28, "Температуропровідність α = λ / (ρ·c_p): Швидкість теплового фронту", size=16, bold=True)]

    bW, bH = 340, 360
    
    bA_x, b_y = 40, 60
    f.append(rect(bA_x, b_y, bW, bH, fill="#fffbf5", stroke=METAL, sw=1.5))
    f.append(text(bA_x + bW/2, b_y + 25, "Висока α (напр. Мідь: α ≈ 117 мм²/с)", size=13, color=METAL, bold=True))

    oxA, oyA = bA_x + 40, b_y + 240
    f.append(arrow(oxA, oyA, oxA + 260, oyA, color=BORDER, sw=1.5))
    f.append(arrow(oxA, oyA, oxA, oyA - 160, color=BORDER, sw=1.5))
    f.append(text(oxA + 230, oyA + 20, "Глибина x", size=11))
    f.append(text(oxA - 15, oyA - 150, "T", size=11, bold=True))

    f.append(path("M %d %d Q %d %d %d %d" % (oxA, oyA - 140, oxA + 30, oyA - 20, oxA + 230, oyA), fill="none", stroke=HOT, sw=1.5, dash="2,2"))
    f.append(text(oxA + 40, oyA - 65, "t₁", size=11, color=HOT))

    f.append(path("M %d %d Q %d %d %d %d" % (oxA, oyA - 140, oxA + 90, oyA - 55, oxA + 230, oyA - 30), fill="none", stroke=HOT, sw=2))
    f.append(text(oxA + 100, oyA - 80, "t₂", size=11, color=HOT))

    f.append(path("M %d %d Q %d %d %d %d" % (oxA, oyA - 140, oxA + 150, oyA - 95, oxA + 230, oyA - 75), fill="none", stroke=HOT, sw=2.5))
    f.append(text(oxA + 170, oyA - 105, "t₃ (майже вирівнялось)", size=11, color=HOT, bold=True))

    f.append(mtext(bA_x + bW/2, b_y + 280,
                   ["Тепловий фронт швидко поширюється.", "Температура вирівнюється за мілісекунди."],
                   size=11, color=INK))

    bB_x = 420
    f.append(rect(bB_x, b_y, bW, bH, fill="#f5f8ff", stroke=COLD, sw=1.5))
    f.append(text(bB_x + bW/2, b_y + 25, "Низька α (напр. Вода: α ≈ 0.14 мм²/с)", size=13, color=COLD, bold=True))

    oxB, oyB = bB_x + 40, b_y + 240
    f.append(arrow(oxB, oyB, oxB + 260, oyB, color=BORDER, sw=1.5))
    f.append(arrow(oxB, oyB, oxB, oyB - 160, color=BORDER, sw=1.5))
    f.append(text(oxB + 230, oyB + 20, "Глибина x", size=11))
    f.append(text(oxB - 15, oyB - 150, "T", size=11, bold=True))

    f.append(path("M %d %d Q %d %d %d %d" % (oxB, oyB - 140, oxB + 15, oyB - 10, oxB + 230, oyB), fill="none", stroke=COLD, sw=1.5, dash="2,2"))
    f.append(text(oxB + 25, oyB - 45, "t₁", size=11, color=COLD))

    f.append(path("M %d %d Q %d %d %d %d" % (oxB, oyB - 140, oxB + 35, oyB - 20, oxB + 230, oyB), fill="none", stroke=COLD, sw=2))
    f.append(text(oxB + 45, oyB - 75, "t₂", size=11, color=COLD))

    f.append(path("M %d %d Q %d %d %d %d" % (oxB, oyB - 140, oxB + 70, oyB - 35, oxB + 230, oyB), fill="none", stroke=COLD, sw=2.5))
    f.append(text(oxB + 85, oyB - 105, "t₃ (повільний фронт)", size=11, color=COLD, bold=True))

    f.append(mtext(bB_x + bW/2, b_y + 280,
                   ["Поверхня гаряча, а всередині ще холодно.", "Тепло поглинається ємністю c_p і застрягає."],
                   size=11, color=INK))

    render(os.path.join(IMG, "thermal-diffusivity-front.svg"), W, H, *f)

# ── Фігура 5: Температурний профіль крізь багатошарову стінку (composite-layer-profile.svg)
def fig_composite_layer_profile():
    W, H = 820, 480
    f = [text(W / 2, 28, "Усталений розподіл температури у багатошаровій стінці", size=16, bold=True)]

    wX, wY = 80, 80
    hH = 260

    l1_w, l2_w, l3_w = 200, 140, 220
    x0 = wX
    x1 = x0 + l1_w
    x2 = x1 + l2_w
    x3 = x2 + l3_w

    f.append(rect(x0, wY, l1_w, hH, fill="#fff5eb", stroke=METAL, sw=1.5))
    f.append(text(x0 + l1_w/2, wY + 30, "Шар 1: Метал", size=13, color=METAL, bold=True))
    f.append(text(x0 + l1_w/2, wY + 50, "λ₁ = 390 Вт/(м·К)", size=11, color=INK))

    f.append(rect(x1, wY, l2_w, hH, fill="#f0fff4", stroke=PHONON, sw=1.5))
    f.append(text(x1 + l2_w/2, wY + 30, "Шар 2: TIM", size=13, color=PHONON, bold=True))
    f.append(text(x1 + l2_w/2, wY + 50, "λ₂ = 5 Вт/(м·К)", size=11, color=INK))

    f.append(rect(x2, wY, l3_w, hH, fill="#f5f0ff", stroke=GLASS, sw=1.5))
    f.append(text(x2 + l3_w/2, wY + 30, "Шар 3: Ізоляція", size=13, color=GLASS, bold=True))
    f.append(text(x2 + l3_w/2, wY + 50, "λ₃ = 0.04 Вт/(м·К)", size=11, color=INK))

    f.append(arrow(x0 - 40, wY + hH - 30, x3 + 40, wY + hH - 30, color=HOT, sw=3))
    f.append(text(W/2, wY + hH - 45, "Сталий потік q = const крізь усі шари", size=12, color=HOT, bold=True))

    t0_pt = (x0, wY + 70)
    t1_pt = (x1, wY + 85)
    t2_pt = (x2, wY + 130)
    t3_pt = (x3, wY + 225)

    f.append(line(t0_pt[0], t0_pt[1], t1_pt[0], t1_pt[1], color=HOT, sw=3))
    f.append(line(t1_pt[0], t1_pt[1], t2_pt[0], t2_pt[1], color=HOT, sw=3))
    f.append(line(t2_pt[0], t2_pt[1], t3_pt[0], t3_pt[1], color=HOT, sw=3))

    for px, py in [t0_pt, t1_pt, t2_pt, t3_pt]:
        f.append(circle(px, py, 5, fill=HOT, stroke=BORDER, sw=1))

    f.append(text(t0_pt[0] + 25, t0_pt[1] - 10, "120 °C", size=12, color=HOT, bold=True))
    f.append(text(t1_pt[0], t1_pt[1] - 12, "115 °C", size=11, color=INK, bold=True))
    f.append(text(t2_pt[0], t2_pt[1] - 12, "95 °C", size=11, color=INK, bold=True))
    f.append(text(t3_pt[0] - 25, t3_pt[1] + 18, "30 °C", size=12, color=COLD, bold=True))

    f.append(text(x0 + l1_w/2, wY + 140, "Пологий нахил\n(малий перепад ΔT₁)", size=10, color=METAL, anchor="middle"))
    f.append(text(x1 + l2_w/2, wY + 165, "Помірний нахил\n(ΔT₂)", size=10, color=PHONON, anchor="middle"))
    f.append(text(x2 + l3_w/2, wY + 175, "Крутий нахил!\n(основний перепад ΔT₃)", size=10, color=GLASS, anchor="middle"))

    f.append(mtext(W/2, wY + hH + 45,
                   ["Оскільки потік q = -λ · (dT/dx) однаковий у всіх шарах, кут нахилу температури обернено пропорційний λ.",
                    "Найбільший перепад температури завжди падає на матеріал із найменшою теплопровідністю!"],
                   size=11, color=INK))

    render(os.path.join(IMG, "composite-layer-profile.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fourier_gradient()
    fig_microscopic_mechanisms()
    fig_phonon_lambda_temp()
    fig_thermal_diffusivity_front()
    fig_composite_layer_profile()
    print("Всі фігури успішно згенеровано у ./img/")
