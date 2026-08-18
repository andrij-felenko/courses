# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Утворення енергетичних зон із дискретних атомних рівнів
# ════════════════════════════════════════════════════════════════════════════
def fig_band_formation():
    W, H = 820, 480
    f = []

    f.append(text(410, 25, "Утворення енергетичних зон при зближенні атомів у кристалі", size=15, bold=True, color=INK))

    # Вісі
    f.append(line(60, 430, 780, 430, color=LINE, sw=1.5))
    f.append(line(60, 430, 60, 50, color=LINE, sw=1.5))
    f.append(text(410, 462, "Відстань між атомами, r →", size=12, color=INK))
    f.append(text(25, 230, "Енергія, E →", size=12, color=INK))

    # Вертикальна пунктирна лінія рівноважної відстані a_0
    f.append(line(320, 50, 320, 430, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(320, 445, "a₀ (кристал)", size=11, bold=True, color=INK))
    f.append(text(680, 445, "Ізольовані атоми (r → ∞)", size=11, color=MUTED))

    # Ліва частина (кристал at a0): Зона провідності
    f.append(rect(80, 90, 240, 70, fill="#ebf5fb", stroke="none"))
    f.append(text(200, 125, "Зона провідності", size=12, bold=True, color=POS))

    # Заборонена зона Eg
    f.append(rect(80, 160, 240, 100, fill="#fdedec", stroke="none"))
    f.append(line(340, 160, 340, 260, color="#c0392b", sw=1.5))
    f.append(line(335, 160, 345, 160, color="#c0392b", sw=1.5))
    f.append(line(335, 260, 345, 260, color="#c0392b", sw=1.5))
    f.append(text(375, 215, "Заборонена зона, E_g", size=12, bold=True, color="#c0392b"))

    # Валентна зона
    f.append(rect(80, 260, 240, 80, fill="#e8f8f5", stroke="none"))
    f.append(text(200, 300, "Валентна зона", size=12, bold=True, color=NEG))

    # Заповнена внутрішня зона
    f.append(rect(80, 370, 240, 40, fill="#eaeded", stroke="none"))
    f.append(text(200, 393, "Глибокі остовні зони", size=11, bold=True, color=MUTED))

    # Керві розщеплення рівнів (від r=750 до r=320 і далі до r=80)
    # Рівень 2 (верхній валентний)
    f.append(line(550, 125, 750, 125, color=POS, sw=2.0))
    f.append(text(755, 128, "2p level", size=11, color=POS))

    # Верхня межа верхньої зони
    p_u1 = "M 550 125 C 450 125, 380 90, 320 90 L 80 90"
    # Нижня межа верхньої зони
    p_u2 = "M 550 125 C 450 125, 380 160, 320 160 L 80 160"
    f.append(svg_path(p_u1, stroke=POS, sw=2.0))
    f.append(svg_path(p_u2, stroke=POS, sw=2.0))

    # Рівень 1 (нижній валентний) E = 280
    f.append(line(550, 280, 750, 280, color=NEG, sw=2.0))
    f.append(text(755, 283, "2s level", size=11, color=NEG))

    p_l1 = "M 550 280 C 450 280, 380 260, 320 260 L 80 260"
    p_l2 = "M 550 280 C 450 280, 380 340, 320 340 L 80 340"
    f.append(svg_path(p_l1, stroke=NEG, sw=2.0))
    f.append(svg_path(p_l2, stroke=NEG, sw=2.0))

    # Глибокий рівень 1s (слабке розщеплення) E = 390
    f.append(line(550, 390, 750, 390, color=MUTED, sw=2.0))
    f.append(text(755, 393, "1s level", size=11, color=MUTED))
    p_c1 = "M 550 390 C 450 390, 380 370, 320 370 L 80 370"
    p_c2 = "M 550 390 C 450 390, 380 410, 320 410 L 80 410"
    f.append(svg_path(p_c1, stroke=MUTED, sw=1.5))
    f.append(svg_path(p_c2, stroke=MUTED, sw=1.5))

    render(os.path.join(OUT, "band-formation.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Дисперсійний спектр E(k) та зони Бріллюена
# ════════════════════════════════════════════════════════════════════════════
def fig_brillouin_zones_dispersion():
    W, H = 820, 480
    f = []

    f.append(text(410, 25, "Енергетичний спектр E(k): Парабола вільного електрона та зонні щілини", size=15, bold=True, color=INK))

    # Вісі
    f.append(line(410, 430, 410, 50, color=LINE, sw=1.5)) # Ось E
    f.append(line(70, 400, 750, 400, color=LINE, sw=1.5)) # Ось k

    f.append(text(410, 42, "Енергія E", size=12, color=INK))
    f.append(text(755, 404, "k", size=12, color=INK))

    # Межі зон Бріллюена: k = +-pi/a (x = 250, 570), +-2pi/a (x = 110, 710)
    f.append(line(250, 50, 250, 400, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(570, 50, 570, 400, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(250, 420, "-π/a", size=11, bold=True, color=INK))
    f.append(text(570, 420, "+π/a", size=11, bold=True, color=INK))

    f.append(line(110, 50, 110, 400, color=MUTED, sw=1.0, dash="2 2"))
    f.append(line(710, 50, 710, 400, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(110, 420, "-2π/a", size=10, color=MUTED))
    f.append(text(710, 420, "+2π/a", size=10, color=MUTED))
    f.append(text(410, 420, "0", size=11, color=INK))

    # Парабола вільних електронів (пунктир) E ~ (x-410)^2
    pts_free = []
    for x in range(110, 711, 5):
        dx = (x - 410) / 160.0
        y = 400 - 180 * (dx ** 2)
        if 50 <= y <= 400:
            pts_free.append((x, y))
    p_free = "M " + " L ".join("%.1f %.1f" % p for p in pts_free)
    f.append(svg_path(p_free, stroke=MUTED, sw=1.5, dash="3 3"))
    f.append(text(620, 150, "Вільний електрон E ∝ k²", size=11, color=MUTED))

    # Реальний спектр із щілинами (Блох / Кроніґ-Пенні)
    # Зона 1 (нижня)
    pts_b1 = []
    for x in range(250, 571, 2):
        k = (x - 410) / 160.0 # -1 to +1
        y = 400 - 100 * (1 - math.cos(math.pi * k)) / 2
        pts_b1.append((x, y))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_b1), stroke=NEG, sw=2.5))

    # Щілина 1 при +-pi/a
    f.append(rect(240, 280, 20, 20, fill="#fdedec", stroke="none"))
    f.append(rect(560, 280, 20, 20, fill="#fdedec", stroke="none"))
    f.append(text(490, 290, "Перша щілина E_g1", size=11, bold=True, color="#c0392b"))
    f.append(line(570, 280, 570, 300, color="#c0392b", sw=1.5))

    # Зона 2
    pts_b2_r = []
    for x in range(570, 711, 2):
        k = (x - 410) / 160.0 # 1 to 1.875
        y = 280 - 110 * (1 - math.cos(math.pi * (k - 1))) / 2
        pts_b2_r.append((x, y))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_b2_r), stroke=POS, sw=2.5))

    pts_b2_l = []
    for x in range(110, 251, 2):
        k = (x - 410) / 160.0
        y = 280 - 110 * (1 - math.cos(math.pi * (k + 1))) / 2
        pts_b2_l.append((x, y))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_b2_l), stroke=POS, sw=2.5))

    # Щілина 2 при +-2pi/a
    f.append(rect(100, 150, 20, 20, fill="#fdedec", stroke="none"))
    f.append(rect(700, 150, 20, 20, fill="#fdedec", stroke="none"))
    f.append(text(620, 160, "Друга щілина E_g2", size=11, bold=True, color="#c0392b"))

    # Позначення першої зони Бріллюена
    f.append(rect(250, 392, 320, 16, fill="#eaf2f8", stroke="none"))
    f.append(text(410, 404, "1-ша зона Бріллюена", size=11, bold=True, color=POS))

    render(os.path.join(OUT, "brillouin-zones-dispersion.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Класифікація твердих тіл: Метал, Напівпровідник, Діелектрик
# ════════════════════════════════════════════════════════════════════════════
def fig_material_classification():
    W, H = 840, 440
    f = []

    f.append(text(420, 25, "Зонна діаграма металів, напівпровідників та діелектриків при T = 0 K", size=15, bold=True, color=INK))

    # ── Панель 1: Метал ──
    f.append(text(140, 60, "Метал", size=14, bold=True, color=INK))
    f.append(text(140, 78, "Перекриття / неповна зона", size=11, color=MUTED))

    # Зона провідності / валентна (частково заповнена)
    f.append(rect(70, 120, 140, 110, fill="#ebf5fb", stroke=POS, sw=1.5)) # порожня частина
    f.append(rect(70, 230, 140, 120, fill="#aed6f1", stroke=POS, sw=1.5)) # заповнена електронним газом
    f.append(line(50, 230, 230, 230, color="#c0392b", sw=2.0, dash="5 3"))
    f.append(text(250, 234, "E_F", size=12, bold=True, color="#c0392b"))
    f.append(text(140, 170, "Вільні стани", size=11, color=POS))
    f.append(text(140, 280, "Заповнені стани", size=11, bold=True, color="#1b4f72"))
    f.append(text(140, 380, "Висока σ без активації", size=11, color=INK))

    # Роздільник 1-2
    f.append(line(290, 50, 290, 410, color=MUTED, sw=1.0, dash="4 4"))

    # ── Панель 2: Напівпровідник ──
    f.append(text(430, 60, "Напівпровідник", size=14, bold=True, color=INK))
    f.append(text(430, 78, "Вузька заборонена зона E_g ≤ 2-3 eV", size=11, color=MUTED))

    # Зона провідності
    f.append(rect(360, 120, 140, 70, fill="#ebf5fb", stroke=POS, sw=1.5))
    f.append(text(430, 155, "Зона провідності (порожня)", size=10, bold=True, color=POS))

    # Заборонена зона Eg
    f.append(rect(360, 190, 140, 80, fill="#fdedec", stroke="none"))
    f.append(line(510, 190, 510, 270, color="#c0392b", sw=1.5))
    f.append(text(545, 234, "E_g ≈ 1 eV", size=11, bold=True, color="#c0392b"))

    # Рівень Фермі посередині Eg
    f.append(line(340, 230, 520, 230, color="#c0392b", sw=1.5, dash="5 3"))

    # Валентна зона
    f.append(rect(360, 270, 140, 80, fill="#d5f5e3", stroke=NEG, sw=1.5))
    f.append(text(430, 310, "Валентна зона (повна)", size=10, bold=True, color=NEG))
    f.append(text(430, 380, "Термічне збудження при T > 0 K", size=11, color=INK))

    # Роздільник 2-3
    f.append(line(580, 50, 580, 410, color=MUTED, sw=1.0, dash="4 4"))

    # ── Панель 3: Діелектрик ──
    f.append(text(710, 60, "Діелектрик", size=14, bold=True, color=INK))
    f.append(text(710, 78, "Широка заборонена зона E_g > 4 eV", size=11, color=MUTED))

    # Зона провідності
    f.append(rect(640, 110, 140, 50, fill="#ebf5fb", stroke=POS, sw=1.5))
    f.append(text(710, 135, "Зона провідності", size=10, color=POS))

    # Заборонена зона Eg (велика)
    f.append(rect(640, 160, 140, 130, fill="#fdedec", stroke="none"))
    f.append(line(790, 160, 790, 290, color="#c0392b", sw=1.5))
    f.append(text(815, 230, "E_g > 4 eV", size=11, bold=True, color="#c0392b"))

    # Рівень Фермі
    f.append(line(620, 225, 795, 225, color="#c0392b", sw=1.5, dash="5 3"))

    # Валентна зона
    f.append(rect(640, 290, 140, 60, fill="#d5f5e3", stroke=NEG, sw=1.5))
    f.append(text(710, 320, "Валентна зона", size=10, color=NEG))
    f.append(text(710, 380, "Струм відсутній (ізолятор)", size=11, color=INK))

    render(os.path.join(OUT, "material-classification.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Ефективна маса, групова швидкість та кривина E(k)
# ════════════════════════════════════════════════════════════════════════════
def fig_effective_mass_dispersion():
    W, H = 840, 460
    f = []

    f.append(text(420, 25, "Зв'язок кривини зонного спектра E(k), групової швидкості та ефективної маси m*", size=15, bold=True, color=INK))

    # ── Верхній графік: E(k) ──
    f.append(text(140, 55, "1. Дисперсія E(k)", size=13, bold=True, color=INK))
    f.append(line(50, 220, 380, 220, color=LINE, sw=1.2)) # ось k
    f.append(line(215, 240, 215, 70, color=LINE, sw=1.2)) # ось E

    pts_e = []
    for x in range(70, 361, 4):
        k = (x - 215) / 100.0 # -1.45 to +1.45
        y = 150 - 60 * math.cos(k * math.pi / 1.45)
        pts_e.append((x, y))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_e), stroke=POS, sw=2.5))
    f.append(text(215, 65, "E", size=11, color=INK))

    # Точка інфлексії k_inf
    f.append(circle(288, 150, 4, fill="#c0392b"))
    f.append(text(300, 145, "d²E/dk² = 0", size=10, color="#c0392b"))

    # ── Середній графік: v_g = (1/ħ) dE/dk ──
    f.append(text(560, 55, "2. Групова швидкість v_g ∝ dE/dk", size=13, bold=True, color=INK))
    f.append(line(470, 150, 800, 150, color=LINE, sw=1.2)) # ось k
    f.append(line(635, 230, 635, 70, color=LINE, sw=1.2)) # ось v

    pts_v = []
    for x in range(490, 781, 4):
        k = (x - 635) / 100.0
        y = 150 - 60 * math.sin(k * math.pi / 1.45)
        pts_v.append((x, y))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_v), stroke=NEG, sw=2.5))
    f.append(text(635, 65, "v_g", size=11, color=INK))
    f.append(text(710, 85, "Максимум швидкості", size=10, color=NEG))

    # ── Нижній графік: m* = ħ^2 / (d^2E/dk^2) ──
    f.append(text(420, 265, "3. Ефективна маса m* = ħ² / (d²E / dk²)", size=13, bold=True, color=INK))
    f.append(line(100, 360, 740, 360, color=LINE, sw=1.2)) # ось k
    f.append(line(420, 440, 420, 285, color=LINE, sw=1.2)) # ось m*

    f.append(rect(340, 310, 160, 45, fill="#d5f5e3", stroke="none"))
    f.append(text(420, 335, "m* > 0 (електроноподібний рух)", size=11, bold=True, color="#1e8449"))

    f.append(rect(140, 370, 140, 45, fill="#fdedec", stroke="none"))
    f.append(text(210, 395, "m* < 0 (діркові стани)", size=11, bold=True, color="#c0392b"))

    f.append(rect(540, 370, 140, 45, fill="#fdedec", stroke="none"))
    f.append(text(610, 395, "m* < 0 (діркові стани)", size=11, bold=True, color="#c0392b"))

    f.append(line(288, 275, 288, 430, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(552, 275, 552, 430, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(288, 442, "m* → ∞", size=10, bold=True, color=MUTED))
    f.append(text(552, 442, "m* → ∞", size=10, bold=True, color=MUTED))

    render(os.path.join(OUT, "effective-mass-dispersion.svg"), W, H, *f)

if __name__ == "__main__":
    fig_band_formation()
    fig_brillouin_zones_dispersion()
    fig_material_classification()
    fig_effective_mass_dispersion()
    print("Figures generated successfully.")
