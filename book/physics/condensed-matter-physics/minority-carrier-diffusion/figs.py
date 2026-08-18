# -*- coding: utf-8 -*-
"""Фігури для теми «Дифузія неосновних носіїв» (book/physics/condensed-matter-physics/minority-carrier-diffusion)."""
import sys, os
import math

# Додаємо scripts/ до шляху пошуку модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра згідно з AUTHORING.md (§5)
MAJ_COLOR = "#2563eb"   # Синій — основні носії (електрони)
MIN_COLOR = "#dc2626"   # Червоний — неосновні носії (дірки)
ACCENT_GREEN = "#16a34a"# Зелений — рекомбінація / поле
BG_PANEL = "#f8fafc"
BORDER_COLOR = "#cbd5e1"

def fig_carrier_injection():
    """carrier-injection.svg: Асиметрія відгуку основних і неосновних носіїв при ін'єкції."""
    W, H = 820, 420
    frags = []

    # Загальний фон і рамка
    frags.append(rect(10, 10, 800, 400, fill=BG_PANEL, stroke=BORDER_COLOR, sw=1.5, rx=8))
    frags.append(text(410, 36, "Асиметрія відгуку при ін'єкції надлишкових носіїв у n-кремній", size=16, bold=True, color="#1e293b"))

    # Панель 1: Основні носії (Електрони)
    frags.append(rect(30, 60, 365, 330, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(212, 85, "Основні носії: Електрони (n₀ = 10¹⁶ см⁻³)", size=13, bold=True, color=MAJ_COLOR))

    # Стовпчик для n0
    frags.append(rect(80, 140, 100, 180, fill="#dbeafe", stroke=MAJ_COLOR, sw=1.5, rx=4))
    frags.append(text(130, 230, "n₀ = 10¹⁶", size=13, bold=True, color=MAJ_COLOR))
    frags.append(text(130, 340, "Рівноважна\nконцентрація", size=11, color="#475569"))

    # Плюс
    frags.append(text(205, 230, "+", size=20, bold=True, color="#64748b"))

    # Стовпчик для Delta n
    frags.append(rect(230, 310, 60, 10, fill="#fee2e2", stroke=MIN_COLOR, sw=1.5, rx=2))
    frags.append(text(260, 295, "Δn = 10¹²", size=11, bold=True, color=MIN_COLOR))
    frags.append(text(260, 340, "Ін'єкція\n(надлишок)", size=11, color="#475569"))

    # Зміна в %
    frags.append(rect(50, 365, 325, 20, fill="#f1f5f9", stroke="#cbd5e1", rx=3))
    frags.append(text(212, 379, "Зміна концентрації: +0.01% (непомітна)", size=11, bold=True, color="#334155"))


    # Панель 2: Неосновні носії (Дірки)
    frags.append(rect(425, 60, 365, 330, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(607, 85, "Неосновні носії: Дірки (p₀ = 10⁴ см⁻³)", size=13, bold=True, color=MIN_COLOR))

    # Стовпчик для p0
    frags.append(rect(475, 318, 100, 2, fill="#fee2e2", stroke=MIN_COLOR, sw=1, rx=1))
    frags.append(text(525, 305, "p₀ = 10⁴", size=11, bold=True, color=MIN_COLOR))
    frags.append(text(525, 340, "Рівноважна\nконцентрація", size=11, color="#475569"))

    # Плюс
    frags.append(text(600, 230, "+", size=20, bold=True, color="#64748b"))

    # Стовпчик для Delta p
    frags.append(rect(625, 120, 100, 200, fill="#fca5a5", stroke=MIN_COLOR, sw=1.5, rx=4))
    frags.append(text(675, 220, "Δp = 10¹²", size=13, bold=True, color=MIN_COLOR))
    frags.append(text(675, 340, "Ін'єкція\n(надлишок)", size=11, color="#475569"))

    # Зміна в разів
    frags.append(rect(445, 365, 325, 20, fill="#fee2e2", stroke="#fca5a5", rx=3))
    frags.append(text(607, 379, "Зміна концентрації: у 100 000 000 разів (10⁸×)!", size=11, bold=True, color=MIN_COLOR))

    render(os.path.join(IMG, "carrier-injection.svg"), W, H, *frags)

def fig_diffusion_recombination_profile():
    """diffusion-recombination-profile.svg: Дифузійний профіль згасання Δp(x) = Δp(0) exp(-x/L_p)."""
    W, H = 820, 400
    frags = []

    frags.append(rect(10, 10, 800, 380, fill=BG_PANEL, stroke=BORDER_COLOR, sw=1.5, rx=8))
    frags.append(text(410, 34, "Профіль дифузії та рекомбінації неосновних носіїв Δp(x)", size=16, bold=True, color="#1e293b"))

    # Осі координат
    ox, oy = 100, 320
    length_x = 650
    height_y = 240

    frags.append(line(ox, oy, ox + length_x, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - height_y, color=INK, sw=2))
    frags.append(text(ox + length_x + 15, oy + 5, "x", size=14, bold=True, color=INK))
    frags.append(text(ox - 10, oy - height_y - 10, "Δp(x)", size=14, bold=True, color=MIN_COLOR))

    # Світлова ін'єкція у x=0
    frags.append(rect(ox - 40, oy - height_y + 10, 40, height_y, fill="#fef08a", stroke="#eab308", sw=1.5, rx=4))
    frags.append(text(ox - 20, oy - height_y / 2, "Ін'єкція\n(x = 0)", size=11, bold=True, color="#854d0e", anchor="middle"))

    # Обчислення експоненційної кривої
    L_p_px = 150
    dp0_px = 200

    pts = []
    for px in range(0, 600, 5):
        x_val = px / L_p_px
        y_val = dp0_px * math.exp(-x_val)
        pts.append((ox + px, oy - y_val))

    poly_pts = [(ox, oy)] + pts + [(ox + 595, oy)]
    poly_str = " ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in poly_pts])
    frags.append('<polygon points="%s" fill="#fee2e2" opacity="0.6"/>' % poly_str)

    path_str = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_str, MIN_COLOR))

    # Позначки на осі x
    frags.append(circle(ox, oy - dp0_px, 5, fill=MIN_COLOR, stroke="#ffffff", sw=1.5))
    frags.append(text(ox - 25, oy - dp0_px, "Δp₀", size=13, bold=True, color=MIN_COLOR))

    x1 = ox + L_p_px
    y1 = oy - dp0_px * math.exp(-1)
    frags.append(line(x1, oy, x1, y1, color=MUTED, sw=1.5, dash="4 4"))
    frags.append(circle(x1, y1, 4, fill=MIN_COLOR))
    frags.append(line(x1, oy - 5, x1, oy + 5, color=INK, sw=1.5))
    frags.append(text(x1, oy + 22, "Lₚ", size=13, bold=True, color=INK))
    frags.append(text(x1 + 45, y1 - 10, "Δp₀ / e (36.8%)", size=11, bold=True, color=MIN_COLOR))

    x2 = ox + 2 * L_p_px
    y2 = oy - dp0_px * math.exp(-2)
    frags.append(line(x2, oy, x2, y2, color=MUTED, sw=1.5, dash="4 4"))
    frags.append(circle(x2, y2, 4, fill=MIN_COLOR))
    frags.append(line(x2, oy - 5, x2, oy + 5, color=INK, sw=1.5))
    frags.append(text(x2, oy + 22, "2Lₚ", size=13, bold=True, color=INK))

    x3 = ox + 3 * L_p_px
    y3 = oy - dp0_px * math.exp(-3)
    frags.append(line(x3, oy - 5, x3, oy + 5, color=INK, sw=1.5))
    frags.append(text(x3, oy + 22, "3Lₚ", size=13, bold=True, color=INK))

    frags.append(rect(x1 + 40, oy - 160, 260, 55, fill="#ffffff", stroke=ACCENT_GREEN, sw=1.5, rx=6))
    frags.append(text(x1 + 170, oy - 140, "Дифузійна довжина Lₚ = √(Dₚ · τₚ)", size=12, bold=True, color=ACCENT_GREEN))
    frags.append(text(x1 + 170, oy - 120, "Середня відстань перед рекомбінацією", size=11, color="#334155"))

    render(os.path.join(IMG, "diffusion-recombination-profile.svg"), W, H, *frags)

def fig_haynes_shockley_setup():
    """haynes-shockley-setup.svg: Принцип експерименту Хейнса — Шоклі."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill=BG_PANEL, stroke=BORDER_COLOR, sw=1.5, rx=8))
    frags.append(text(420, 34, "Експеримент Хейнса — Шоклі: вимірювання дрейфу, дифузії та життя носіїв", size=15, bold=True, color="#1e293b"))

    bar_x, bar_y, bar_w, bar_h = 80, 80, 680, 70
    frags.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    frags.append(text(bar_x + 50, bar_y + 40, "n-тип напівпровідник", size=12, bold=True, color="#334155"))

    frags.append(arrow(bar_x + 220, bar_y + 35, bar_x + 480, bar_y + 35, color=ACCENT_GREEN, sw=3))
    frags.append(text(bar_x + 350, bar_y + 20, "Протягувальне поле E", size=12, bold=True, color=ACCENT_GREEN))

    inj_x = bar_x + 120
    frags.append(line(inj_x, bar_y - 20, inj_x, bar_y, color=MIN_COLOR, sw=2.5))
    frags.append(circle(inj_x, bar_y - 20, 5, fill=MIN_COLOR))
    frags.append(text(inj_x, bar_y - 28, "Інжектор p⁺ (t = 0)", size=11, bold=True, color=MIN_COLOR))

    det_x = bar_x + 540
    frags.append(line(det_x, bar_y - 20, det_x, bar_y, color=MAJ_COLOR, sw=2.5))
    frags.append(circle(det_x, bar_y - 20, 5, fill=MAJ_COLOR))
    frags.append(text(det_x, bar_y - 28, "Колектор p⁺ (x = d)", size=11, bold=True, color=MAJ_COLOR))

    s1_y = 230
    frags.append(line(bar_x, s1_y, bar_x + bar_w, s1_y, color="#94a3b8", sw=1))
    frags.append(text(bar_x + 30, s1_y - 25, "1. Ін'єкція (t = 0):", size=11, bold=True, color="#1e293b"))
    pts1 = []
    for px in range(-60, 61, 2):
        gw = 10
        gh = 55 * math.exp(-(px/gw)**2)
        pts1.append((inj_x + px, s1_y - gh))
    pstr1 = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts1])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pstr1, MIN_COLOR))
    frags.append(text(inj_x, s1_y + 16, "Вузький пакет", size=10, color=MIN_COLOR))

    s2_y = 320
    mid_x = bar_x + 330
    frags.append(line(bar_x, s2_y, bar_x + bar_w, s2_y, color="#94a3b8", sw=1))
    frags.append(text(bar_x + 30, s2_y - 25, "2. Дрейф і дифузія (t = t₁):", size=11, bold=True, color="#1e293b"))
    pts2 = []
    for px in range(-100, 101, 2):
        gw = 25
        gh = 35 * math.exp(-(px/gw)**2)
        pts2.append((mid_x + px, s2_y - gh))
    pstr2 = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts2])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pstr2, MIN_COLOR))
    frags.append(arrow(inj_x + 20, s2_y - 15, mid_x - 35, s2_y - 15, color=ACCENT_GREEN, sw=1.5))
    frags.append(text((inj_x + mid_x)/2, s2_y - 25, "Дрейф (v = μE)", size=10, bold=True, color=ACCENT_GREEN))
    frags.append(arrow(mid_x - 10, s2_y - 42, mid_x - 45, s2_y - 42, color=MIN_COLOR, sw=1))
    frags.append(arrow(mid_x + 10, s2_y - 42, mid_x + 45, s2_y - 42, color=MIN_COLOR, sw=1))
    frags.append(text(mid_x, s2_y - 48, "Розмиття (Дифузія D)", size=10, color=MIN_COLOR))

    s3_y = 410
    frags.append(line(bar_x, s3_y, bar_x + bar_w, s3_y, color="#94a3b8", sw=1))
    frags.append(text(bar_x + 30, s3_y - 25, "3. Детектування (t = t_d):", size=11, bold=True, color="#1e293b"))
    pts3 = []
    for px in range(-120, 121, 2):
        gw = 40
        gh = 22 * math.exp(-(px/gw)**2)
        pts3.append((det_x + px, s3_y - gh))
    pstr3 = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts3])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pstr3, MIN_COLOR))

    frags.append(rect(bar_x + 580, s2_y - 30, 170, 110, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(bar_x + 665, s2_y - 12, "Результати виміру:", size=11, bold=True, color=INK))
    frags.append(text(bar_x + 665, s2_y + 8, "• Зрушення peak → μ", size=10, color=INK))
    frags.append(text(bar_x + 665, s2_y + 28, "• Ширина peak → D", size=10, color=INK))
    frags.append(text(bar_x + 665, s2_y + 48, "• Площа peak → τ", size=10, color=INK))
    frags.append(text(bar_x + 665, s2_y + 68, "D / μ = k_B T / q", size=10, bold=True, color=ACCENT_GREEN))

    render(os.path.join(IMG, "haynes-shockley-setup.svg"), W, H, *frags)

def fig_bjt_solar_application():
    """bjt-solar-application.svg: Дифузія неосновних носіїв у PN-переході, транзисторі та сонячному елементі."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill=BG_PANEL, stroke=BORDER_COLOR, sw=1.5, rx=8))
    frags.append(text(420, 34, "Роль дифузії неосновних носіїв у приладах", size=16, bold=True, color="#1e293b"))

    frags.append(rect(30, 60, 365, 330, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(212, 85, "А. Біполярний транзистор (p-n-p)", size=13, bold=True, color="#1e293b"))

    bjt_y = 120
    frags.append(rect(60, bjt_y, 90, 80, fill="#fee2e2", stroke=MIN_COLOR, sw=1.5))
    frags.append(text(105, bjt_y + 45, "Емітер (p⁺)", size=12, bold=True, color=MIN_COLOR))

    frags.append(rect(150, bjt_y, 70, 80, fill="#dbeafe", stroke=MAJ_COLOR, sw=1.5))
    frags.append(text(185, bjt_y + 35, "База (n)", size=12, bold=True, color=MAJ_COLOR))
    frags.append(text(185, bjt_y + 55, "Wₑ ≪ Lₚ", size=11, bold=True, color=ACCENT_GREEN))

    frags.append(rect(220, bjt_y, 140, 80, fill="#fee2e2", stroke=MIN_COLOR, sw=1.5))
    frags.append(text(290, bjt_y + 45, "Колектор (p)", size=12, bold=True, color=MIN_COLOR))

    frags.append(arrow(110, bjt_y + 25, 250, bjt_y + 25, color=MIN_COLOR, sw=2.5))
    frags.append(text(185, bjt_y + 12, "Дифузія дірок", size=10, bold=True, color=MIN_COLOR))

    gr_y = 310
    frags.append(line(140, gr_y, 230, gr_y, color=INK, sw=1.5))
    frags.append(line(150, gr_y, 150, gr_y - 60, color=INK, sw=1.5))
    frags.append(line(150, gr_y - 55, 220, gr_y - 5, color=MIN_COLOR, sw=2.5))
    frags.append(text(185, gr_y - 35, "Δp(x)", size=10, bold=True, color=MIN_COLOR))
    frags.append(text(212, gr_y + 20, "Усі інжектовані дірки пролітають базу\nбез рекомбінації (коефіцієнт передачі α ≈ 1)", size=11, color="#334155"))


    frags.append(rect(425, 60, 365, 330, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(607, 85, "Б. Сонячний елемент (N⁺-P)", size=13, bold=True, color="#1e293b"))

    frags.append(arrow(470, 105, 470, 135, color="#eab308", sw=2))
    frags.append(arrow(520, 105, 520, 135, color="#eab308", sw=2))
    frags.append(arrow(570, 105, 570, 135, color="#eab308", sw=2))
    frags.append(text(520, 100, "Сонячне світло (hν)", size=11, bold=True, color="#854d0e"))

    sc_y = 140
    frags.append(rect(455, sc_y, 305, 25, fill="#dbeafe", stroke=MAJ_COLOR, sw=1.5))
    frags.append(text(607, sc_y + 17, "Тонкий n⁺-емітер", size=11, bold=True, color=MAJ_COLOR))

    frags.append(rect(455, sc_y + 25, 305, 25, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    frags.append(text(607, sc_y + 42, "Збіднена зона (Поле E)", size=11, bold=True, color=ACCENT_GREEN))

    frags.append(rect(455, sc_y + 50, 305, 120, fill="#fee2e2", stroke=MIN_COLOR, sw=1.5))
    frags.append(text(607, sc_y + 90, "Товста p-база", size=12, bold=True, color=MIN_COLOR))

    gen_y = sc_y + 110
    frags.append(circle(530, gen_y, 6, fill="#fef08a", stroke="#eab308", sw=1.5))
    frags.append(text(530, gen_y + 4, "hν", size=9, bold=True, color="#854d0e"))

    frags.append(arrow(530, gen_y - 8, 530, sc_y + 55, color=MAJ_COLOR, sw=2))
    frags.append(text(585, gen_y - 25, "Дифузія неосновних\nелектронів (Lₙ > глибина)", size=10, bold=True, color=MAJ_COLOR))

    frags.append(text(607, sc_y + 195, "Лише носії, що згенеровані на відстані < Lₙ\nвід переходу, дають фотострум!", size=11, bold=True, color=MIN_COLOR))

    render(os.path.join(IMG, "bjt-solar-application.svg"), W, H, *frags)

def main():
    fig_carrier_injection()
    fig_diffusion_recombination_profile()
    fig_haynes_shockley_setup()
    fig_bjt_solar_application()
    print("Всі 4 фігури згенеровано успішно у img/")

if __name__ == "__main__":
    main()
