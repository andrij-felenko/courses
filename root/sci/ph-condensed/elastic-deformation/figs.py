# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path_svg(d_str, stroke=POS, sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Повна діаграма деформування σ - ε (крихкий vs пластичний)
# ════════════════════════════════════════════════════════════════════════════
def fig_stress_strain_curve():
    W, H = 820, 480
    f = []

    f.append(rect(10, 10, W-20, H-20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))
    
    # Осі
    ox, oy = 80, 410
    max_x, max_y = 760, 50
    f.append(arrow(ox, oy, max_x, oy, color=INK, sw=2.0))
    f.append(arrow(ox, oy, ox, max_y, color=INK, sw=2.0))
    
    f.append(text(max_x - 30, oy + 30, "Деформація ε (ΔL/L₀)", size=13, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, max_y + 15, "Напруження σ (Па)", size=13, color=INK, bold=True, anchor="start"))

    # Крива пластичного матеріалу (сталь / мідь)
    path_ductile = "M 80 410 L 220 230 Q 240 210 270 210 Q 380 120 520 120 Q 620 130 680 220"
    f.append(path_svg(path_ductile, stroke=POS, sw=3.0))

    # Крива крихкого матеріалу (скло / кераміка)
    path_brittle = "M 80 410 L 250 110"
    f.append(path_svg(path_brittle, stroke=NEG, sw=2.5, dash="6 3"))
    f.append(circle(250, 110, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(265, 105, "Крихке руйнування", size=12, color=NEG, bold=True, anchor="start"))

    # Тангенс кута нахилу (Модуль Юнга E)
    f.append(path_svg("M 150 320 L 200 320 L 200 255", stroke=MUTED, sw=1.5, dash="3 3"))
    f.append(text(215, 295, "Кут нахилу = Модуль Юнга E", size=11, color=MUTED, italic=True, anchor="start"))

    # Характеристичні точки на кривій
    # 1. Границя пропорційності / пружності
    f.append(circle(220, 230, 4.5, fill="#f39c12", stroke=INK, sw=1.5))
    f.append(line(220, 230, 220, oy, color=MUTED, sw=1.0, dash="2 2"))
    f.append(line(ox, 230, 220, 230, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(ox - 8, 234, "σ_el", size=12, color=INK, bold=True, anchor="end"))
    f.append(text(220, oy + 18, "ε_el", size=12, color=INK, bold=True, anchor="middle"))
    
    # 2. Границя плинності
    f.append(circle(270, 210, 4.5, fill="#e67e22", stroke=INK, sw=1.5))
    f.append(line(ox, 210, 270, 210, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(ox - 8, 214, "σ_y", size=12, color=INK, bold=True, anchor="end"))

    # 3. Границя міцності
    f.append(circle(520, 120, 5.0, fill=POS, stroke=INK, sw=1.5))
    f.append(line(ox, 120, 520, 120, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(ox - 8, 124, "σ_uts", size=12, color=POS, bold=True, anchor="end"))

    # 4. Точка руйнування
    f.append(circle(680, 220, 5.0, fill="#8e44ad", stroke=INK, sw=1.5))
    f.append(text(692, 224, "Руйнування (σ_f)", size=12, color="#8e44ad", bold=True, anchor="start"))

    # Пояснювальні блоки областей
    # Область 1: Пружна деформація (закон Гука)
    f.append(rect(85, 365, 130, 35, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(150, 387, "Пружна область\n(оборотна)", size=11, color=FIELD, bold=True, anchor="middle"))

    # Область 2: Плинність та зміцнення
    f.append(rect(280, 365, 180, 35, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=4))
    f.append(text(370, 387, "Пластична плинність\nта деформаційне зміцнення", size=11, color="#d35400", bold=True, anchor="middle"))

    # Область 3: Утворення "шийки"
    f.append(rect(540, 365, 120, 35, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    f.append(text(600, 387, "Утворення шийки\n(локалізація)", size=11, color=POS, bold=True, anchor="middle"))

    # Підписи під осями
    f.append(text(150, oy - 15, "Область Гука (σ = E·ε)", size=12, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "elastic-stress-strain-curve.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Міжатомний потенціал U(r) та повертальна сила F(r)
# ════════════════════════════════════════════════════════════════════════════
def fig_interatomic_potential():
    W, H = 820, 440
    f = []

    f.append(rect(10, 10, W-20, H-20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Ліва панель: Потенціал U(r)
    f.append(text(220, 35, "Потенціальна енергія U(r)", size=14, color=INK, bold=True))
    ox1, oy1 = 60, 240
    f.append(arrow(ox1, 380, ox1, 50, color=INK, sw=1.5))
    f.append(arrow(ox1, oy1, 400, oy1, color=INK, sw=1.5))
    f.append(text(390, oy1 + 20, "Міжатомна відстань r", size=11, color=INK, anchor="end"))
    f.append(text(ox1 - 10, 60, "U(r)", size=11, color=INK, anchor="end"))

    # Крива Леннард-Джонса / міжатомного потенціалу
    path_u = "M 85 70 Q 110 330 170 330 Q 240 330 380 248"
    f.append(path_svg(path_u, stroke=NEG, sw=2.5))

    # Параболічна апроксимація біля мінімуму
    path_para = "M 115 250 Q 170 410 225 250"
    f.append(path_svg(path_para, stroke=POS, sw=1.8, dash="4 3"))

    # Рівноважна відстань r0
    f.append(line(170, 50, 170, 380, color=MUTED, sw=1.2, dash="3 3"))
    f.append(circle(170, 330, 4.5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(170, oy1 + 18, "r₀ (рівновага)", size=11, color=INK, bold=True))
    f.append(text(170, 350, "U_min", size=11, color=NEG, bold=True))
    f.append(text(225, 275, "Парабола Гармонічного\nосцилятора: ½·k·(Δr)²", size=11, color=POS, bold=True, anchor="start"))

    # Права панель: Сила F(r) = -dU/dr
    f.append(text(620, 35, "Міжатомна сила F(r) = -dU/dr", size=14, color=INK, bold=True))
    ox2, oy2 = 460, 240
    f.append(arrow(ox2, 380, ox2, 50, color=INK, sw=1.5))
    f.append(arrow(ox2, oy2, 790, oy2, color=INK, sw=1.5))
    f.append(text(780, oy2 + 20, "Міжатомна відстань r", size=11, color=INK, anchor="end"))
    f.append(text(ox2 - 10, 60, "Сила F", size=11, color=INK, anchor="end"))

    # Лінія рівноваги r0
    f.append(line(570, 50, 570, 380, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(570, oy2 + 18, "r₀", size=11, color=INK, bold=True))

    # Крива сили: при r < r0 сила відштовхування (F > 0), при r > r0 сила притягання (F < 0)
    path_f = "M 485 60 Q 510 370 570 240 Q 640 100 780 230"
    f.append(path_svg(path_f, stroke=FIELD, sw=2.5))
    f.append(circle(570, 240, 5.0, fill=FIELD, stroke=INK, sw=1.5))

    # Лінійний дотичний відрізок у точці r0
    f.append(line(520, 330, 620, 150, color=POS, sw=2.0, dash="5 3"))
    f.append(text(630, 160, "Лінійна область Гука:\nF ≈ -k · Δr", size=12, color=POS, bold=True, anchor="start"))

    # Зони відштовхування та притягання
    f.append(text(510, 120, "Відштовхування\n(стиск, r < r₀)", size=11, color=NEG, bold=True, anchor="middle"))
    f.append(text(680, 280, "Притягання\n(розтяг, r > r₀)", size=11, color=POS, bold=True, anchor="middle"))

    render(os.path.join(OUT, "interatomic-potential-deformation.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Три типи деформацій (осьова, зсувна, об'ємна)
# ════════════════════════════════════════════════════════════════════════════
def fig_stress_strain_types():
    W, H = 840, 420
    f = []

    f.append(rect(10, 10, W-20, H-20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Розділювальні вертикальні лінії
    f.append(line(280, 30, 280, 390, color="#cbd5e1", sw=1.2, dash="4 4"))
    f.append(line(560, 30, 560, 390, color="#cbd5e1", sw=1.2, dash="4 4"))

    # ── Панель 1: Осьовий розтяг / стиск ──
    f.append(text(145, 45, "1. Осьовий розтяг (σ, ε)", size=13, color=INK, bold=True))
    
    # Початковий контур стержня (пунктирними лініями без rect fill)
    f.append(path_svg("M 95 140 L 195 140 L 195 260 L 95 260 Z", stroke=MUTED, sw=1.5, fill="none", dash="4 4"))
    # Деформований стержень (видовжений і звужений)
    f.append(rect(110, 90, 70, 200, fill="#e0f2fe", stroke=NEG, sw=2.0, rx=2))

    # Сили F
    f.append(arrow(145, 90, 145, 55, color=POS, sw=2.2))
    f.append(arrow(145, 290, 145, 325, color=POS, sw=2.2))
    f.append(text(145, 48, "F_N", size=12, color=POS, bold=True))
    f.append(text(145, 338, "F_N", size=12, color=POS, bold=True))

    # Позначення L0 та ΔL
    f.append(line(65, 140, 65, 260, color=INK, sw=1.2))
    f.append(text(55, 200, "L₀", size=11, color=INK, bold=True))
    f.append(line(200, 90, 200, 290, color=NEG, sw=1.2))
    f.append(text(215, 190, "L₀+ΔL", size=11, color=NEG, bold=True))

    # Формули
    tb1, _, _ = textbox(145, 368, "σ = F_N / A\nε = ΔL / L₀\nσ = E · ε", size=10, pad=5, fill="#ffffff", stroke=NEG, sw=1.2)
    f.append(tb1)

    # ── Панель 2: Зсувна деформація ──
    f.append(text(420, 45, "2. Зсув (τ, γ)", size=13, color=INK, bold=True))

    # Початковий прямокутник пунктиром
    f.append(path_svg("M 360 180 L 480 180 L 480 300 L 360 300 Z", stroke=MUTED, sw=1.5, fill="none", dash="4 4"))

    # Зсунутий паралелограм
    poly_pts = [(400, 180), (520, 180), (480, 300), (360, 300)]
    pts_str = " ".join("%.1f,%.1f" % (px, py) for px, py in poly_pts)
    f.append('<polygon points="%s" fill="#fef3c7" stroke="%s" stroke-width="2.0"/>' % (pts_str, POS))

    # Дотична сила F_T
    f.append(arrow(400, 170, 480, 170, color=POS, sw=2.2))
    f.append(text(440, 155, "F_T", size=12, color=POS, bold=True))

    # Кут зсуву γ та зсув Δx
    f.append(line(360, 180, 400, 180, color=POS, sw=1.2, dash="3 3"))
    f.append(text(380, 173, "Δx", size=11, color=POS, bold=True))
    f.append(text(378, 270, "γ", size=12, color=POS, bold=True))

    # Висота h
    f.append(line(340, 180, 340, 300, color=INK, sw=1.2))
    f.append(text(330, 245, "h", size=11, color=INK, bold=True))

    # Формули
    tb2, _, _ = textbox(420, 330, "τ = F_T / A\nγ ≈ Δx / h\nτ = G · γ", size=11, pad=6, fill="#ffffff", stroke=POS, sw=1.2)
    f.append(tb2)

    # ── Панель 3: Об'ємне стиснення ──
    f.append(text(700, 45, "3. Об'ємний стиск (p, ΔV)", size=13, color=INK, bold=True))

    # Початковий контур (пунктирне коло)
    f.append(circle(700, 220, 65, fill="none", stroke=MUTED, sw=1.5))
    # Стиснутий стан
    f.append(circle(700, 220, 45, fill="#dcfce7", stroke=FIELD, sw=2.0))

    # Радіальні сили тиску p
    arrows_p = [
        (700, 130, 700, 160), (700, 310, 700, 280),
        (610, 220, 640, 220), (790, 220, 760, 220),
        (635, 155, 660, 180), (765, 285, 740, 260),
        (635, 285, 660, 260), (765, 155, 740, 180)
    ]
    for x1, y1, x2, y2 in arrows_p:
        f.append(arrow(x1, y1, x2, y2, color=FIELD, sw=1.8))

    f.append(text(700, 224, "V₀ - ΔV", size=11, color=FIELD, bold=True))

    # Формули
    tb3, _, _ = textbox(700, 330, "p = Всебічний тиск\nΔV / V₀ = Відносний об'єм\np = -K · (ΔV / V₀)", size=11, pad=6, fill="#ffffff", stroke=FIELD, sw=1.2)
    f.append(tb3)

    render(os.path.join(OUT, "stress-strain-types.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Ефект Пуассона (поперечне стиснення при розтягу)
# ════════════════════════════════════════════════════════════════════════════
def fig_poisson_effect():
    W, H = 800, 380
    f = []

    f.append(rect(10, 10, W-20, H-20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    f.append(text(400, 38, "Ефект Пуассона: поздовжнє подовження → поперечне звуження", size=13, color=INK, bold=True))

    # Початковий зразок (пунктирний контур без fill rect)
    f.append(path_svg("M 200 130 L 600 130 L 600 250 L 200 250 Z", stroke=MUTED, sw=1.8, fill="none", dash="4 4"))
    f.append(text(400, 145, "Початковий стан: L₀, d₀", size=11, color=MUTED, bold=True))

    # Деформований зразок під дією сили F (довший і тонший) — кольоровий
    f.append(rect(120, 160, 560, 60, fill="#e0f2fe", stroke=NEG, sw=2.2, rx=4))
    f.append(text(400, 194, "Деформований стан: L₀ + ΔL, d₀ - Δd", size=12, color=NEG, bold=True))

    # Розтягуючі сили F
    f.append(arrow(120, 190, 50, 190, color=POS, sw=2.5))
    f.append(arrow(680, 190, 750, 190, color=POS, sw=2.5))
    f.append(text(35, 194, "F", size=14, color=POS, bold=True))
    f.append(text(765, 194, "F", size=14, color=POS, bold=True))

    # Розміри L0 та ΔL
    f.append(line(200, 270, 600, 270, color=MUTED, sw=1.2))
    f.append(text(400, 288, "L₀", size=11, color=MUTED, bold=True))

    f.append(line(120, 270, 200, 270, color=POS, sw=1.5))
    f.append(text(160, 288, "ΔL/2", size=11, color=POS, bold=True))

    f.append(line(600, 270, 680, 270, color=POS, sw=1.5))
    f.append(text(640, 288, "ΔL/2", size=11, color=POS, bold=True))

    # Поперечні розміри d0 та Δd
    f.append(line(695, 130, 695, 250, color=MUTED, sw=1.2))
    f.append(text(710, 140, "d₀", size=11, color=MUTED, bold=True))

    f.append(line(695, 130, 695, 160, color=NEG, sw=1.5))
    f.append(text(725, 148, "Δd/2", size=11, color=NEG, bold=True))

    # Блок математичного визначення Коефіцієнта Пуассона ν
    tb_formula = (
        "Коефіцієнт Пуассона ν = - ε_поперечна / ε_поздовжня\n"
        "ε_поздовжня = ΔL / L₀ > 0,   ε_поперечна = -Δd / d₀ < 0\n"
        "Для більшості металів: ν ≈ 0.25 ... 0.35 | Нестисливий матеріал (гума): ν = 0.5"
    )
    tb_box, _, _ = textbox(400, 335, tb_formula, size=11, pad=8, fill="#ffffff", stroke=NEG, sw=1.2)
    f.append(tb_box)

    render(os.path.join(OUT, "poisson-effect.svg"), W, H, *f)

if __name__ == "__main__":
    fig_stress_strain_curve()
    fig_interatomic_potential()
    fig_stress_strain_types()
    fig_poisson_effect()
    print("SVG generation complete.")
