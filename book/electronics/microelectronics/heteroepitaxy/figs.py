# -*- coding: utf-8 -*-
"""Фігури до теми «Гетероепітаксія та неузгодженість ґраток» (book/electronics/microelectronics/heteroepitaxy)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "img")


def fig_lattice_mismatch_strain():
    """Фігура 1: Псевдоморфне зростання під напруженням та релаксація дислокаціями."""
    w, h = 900, 480
    frags = []

    # Заголовок зверху
    tb_main, _, _ = textbox(450, 25, "Механічні стани гетероепітаксійної плівки при неузгодженості ґраток", size=14, bold=True, pad=8)
    frags.append(tb_main)

    # ── Колонка 1: Псевдоморфне стиснення (Compressive) ──
    x_c1 = 155
    tb_h1, _, _ = textbox(x_c1, 65, "Псевдоморфне стиснення\na_epi > a_sub (f > 0)", size=11, bold=True, pad=6, fill="#e8f4fd", stroke="#2457d6")
    frags.append(tb_h1)

    # Підкладка
    frags.append(rect(x_c1 - 125, 250, 250, 110, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))

    # Атомні лінії підкладки (лише у верхній зоні підкладки, не перетинаючи текст)
    for i in range(-3, 4):
        frags.append(line(x_c1 + i * 35, 250, x_c1 + i * 35, 290, color="#b0b8c0", sw=1.2, dash="3,3"))

    tb_sub1, _, _ = textbox(x_c1, 325, "Підкладка (стала a_sub)", size=11, color=MUTED, fill="#f0f2f5", stroke="#7f8c8d", pad=4)
    frags.append(tb_sub1)

    # Плівка під стисненням
    frags.append(rect(x_c1 - 125, 120, 250, 130, fill="#eaf2f8", stroke="#2457d6", sw=1.8, rx=2))
    for i in range(-3, 4):
        frags.append(line(x_c1 + i * 35, 215, x_c1 + i * 35, 250, color="#2457d6", sw=1.5))

    tb_p1, _, _ = textbox(x_c1, 168, "Плівка під стисненням\na_|| = a_sub (стиснута)\nc_⊥ > a_epi (витягнута)", size=10, bold=True, color="#1e3a8a", fill="#eaf2f8", stroke="#2457d6", pad=5)
    frags.append(tb_p1)

    # Стрілки бічного стиснення плівки
    frags.append(arrow(x_c1 - 110, 230, x_c1 - 85, 230, color="#2457d6", sw=1.8))
    frags.append(arrow(x_c1 + 110, 230, x_c1 + 85, 230, color="#2457d6", sw=1.8))

    # Стрілка вертикального розширення
    frags.append(arrow(x_c1, 138, x_c1, 122, color="#2457d6", sw=1.8))

    tb_n1, _, _ = textbox(x_c1, 415, "Когерентна ґратка (h < h_c)\nЕластична енергія E ∝ h · f²\nДефектів немає, ґратка напружена", size=10, pad=6, fill="#ffffff", stroke="#2457d6")
    frags.append(tb_n1)

    # ── Колонка 2: Псевдоморфний розтяг (Tensile) ──
    x_c2 = 450
    tb_h2, _, _ = textbox(x_c2, 65, "Псевдоморфний розтяг\na_epi < a_sub (f < 0)", size=11, bold=True, pad=6, fill="#fef5e7", stroke="#d35400")
    frags.append(tb_h2)

    # Підкладка
    frags.append(rect(x_c2 - 125, 250, 250, 110, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))
    for i in range(-3, 4):
        frags.append(line(x_c2 + i * 35, 250, x_c2 + i * 35, 290, color="#b0b8c0", sw=1.2, dash="3,3"))

    tb_sub2, _, _ = textbox(x_c2, 325, "Підкладка (стала a_sub)", size=11, color=MUTED, fill="#f0f2f5", stroke="#7f8c8d", pad=4)
    frags.append(tb_sub2)

    # Плівка під розтягом
    frags.append(rect(x_c2 - 125, 140, 250, 110, fill="#fef9e7", stroke="#d35400", sw=1.8, rx=2))
    for i in range(-3, 4):
        frags.append(line(x_c2 + i * 35, 218, x_c2 + i * 35, 250, color="#d35400", sw=1.5))

    tb_p2, _, _ = textbox(x_c2, 178, "Плівка під розтягом\na_|| = a_sub (розтягнута)\nc_⊥ < a_epi (сплюснута)", size=10, bold=True, color="#a04000", fill="#fef9e7", stroke="#d35400", pad=5)
    frags.append(tb_p2)

    # Стрілки бічного розтягу плівки
    frags.append(arrow(x_c2 - 85, 230, x_c2 - 110, 230, color="#d35400", sw=1.8))
    frags.append(arrow(x_c2 + 85, 230, x_c2 + 110, 230, color="#d35400", sw=1.8))

    # Стрілка вертикального сплющування
    frags.append(arrow(x_c2, 142, x_c2, 155, color="#d35400", sw=1.8))

    tb_n2, _, _ = textbox(x_c2, 415, "Когерентна ґратка (h < h_c)\nРизик утворення мікротріщин\nпри охолодженні (CTE mismatch)", size=10, pad=6, fill="#ffffff", stroke="#d35400")
    frags.append(tb_n2)

    # ── Колонка 3: Релаксована плівка з дислокаціями (Relaxed) ──
    x_c3 = 745
    tb_h3, _, _ = textbox(x_c3, 65, "Релаксація напружень\nh > h_c (дислокації MD + TD)", size=11, bold=True, pad=6, fill="#fbeee6", stroke=POS)
    frags.append(tb_h3)

    # Підкладка
    frags.append(rect(x_c3 - 125, 250, 250, 110, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))
    for i in range(-3, 4):
        frags.append(line(x_c3 + i * 35, 250, x_c3 + i * 35, 290, color="#b0b8c0", sw=1.2, dash="3,3"))

    tb_sub3, _, _ = textbox(x_c3, 325, "Підкладка (стала a_sub)", size=11, color=MUTED, fill="#f0f2f5", stroke="#7f8c8d", pad=4)
    frags.append(tb_sub3)

    # Плівка релаксована
    frags.append(rect(x_c3 - 125, 120, 250, 130, fill="#fdedec", stroke=POS, sw=1.8, rx=2))
    for i in range(-4, 5):
        frags.append(line(x_c3 + i * 27, 195, x_c3 + i * 27, 250, color=POS, sw=1.5))

    tb_p3, _, _ = textbox(x_c3, 155, "Релаксована плівка\na_|| = a_epi (власна стала)", size=10, bold=True, color=POS, fill="#fdedec", stroke=POS, pad=5)
    frags.append(tb_p3)

    # Позначення дислокацій невідповідності на інтерфейсі (символи ⊥)
    frags.append(circle(x_c3 - 54, 250, 7, fill="#ffffff", stroke=POS, sw=1.8))
    frags.append(text(x_c3 - 54, 253, "⊥", size=12, bold=True, color=POS))

    frags.append(circle(x_c3 + 54, 250, 7, fill="#ffffff", stroke=POS, sw=1.8))
    frags.append(text(x_c3 + 54, 253, "⊥", size=12, bold=True, color=POS))

    # Пронизуючі дислокації (Threading Dislocations)
    frags.append(line(x_c3 - 54, 243, x_c3 - 75, 120, color=POS, sw=2, dash="4,2"))
    frags.append(line(x_c3 + 54, 243, x_c3 + 75, 120, color=POS, sw=2, dash="4,2"))

    tb_td1, _, _ = textbox(x_c3 - 75, 105, "Пронизуюча TD", size=9, bold=True, pad=3, fill="#ffffff", stroke=POS)
    frags.append(tb_td1)
    tb_td2, _, _ = textbox(x_c3 + 75, 105, "Пронизуюча TD", size=9, bold=True, pad=3, fill="#ffffff", stroke=POS)
    frags.append(tb_td2)

    tb_n3, _, _ = textbox(x_c3, 415, "Релаксація (h > h_c)\nДислокації невідповідності (MD, ⊥)\nПронизуючі дислокації (TD) на поверхні", size=10, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_n3)

    # Вертикальні розділювачі
    frags.append(line(295, 55, 295, 455, color="#e0e0e0", sw=1.2, dash="4,4"))
    frags.append(line(600, 55, 600, 455, color="#e0e0e0", sw=1.2, dash="4,4"))

    render(os.path.join(IMG, "lattice-mismatch-strain.svg"), w, h, *frags)


def fig_three_growth_modes():
    """Фігура 2: Три термодинамічні режими росту тонких плівок."""
    w, h = 900, 440
    frags = []

    tb_main, _, _ = textbox(450, 25, "Термодинамічні режими росту гетероепітаксійних плівок (баланс поверхневої енергії)", size=14, bold=True, pad=8)
    frags.append(tb_main)

    # ── Режим 1: Франк — ван дер Мерве ──
    x1 = 155
    tb_t1, _, _ = textbox(x1, 65, "Франк — ван дер Мерве\n(2D Шар за шаром / FM)", size=11, bold=True, pad=6, fill="#e8f8f5", stroke=FIELD)
    frags.append(tb_t1)

    # Підкладка
    frags.append(rect(x1 - 120, 230, 240, 70, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))
    frags.append(text(x1, 275, "Підкладка (γ_sub)", size=11, color=MUTED))

    # Шар 1 (повний)
    frags.append(rect(x1 - 120, 190, 240, 40, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=0))
    frags.append(text(x1, 212, "Шар 1 (повне змочування)", size=10, bold=True, color="#1e8449"))

    # Шар 2 (заповнюється моношар за моношаром)
    frags.append(rect(x1 - 120, 150, 180, 40, fill="#a9dfbf", stroke=FIELD, sw=1.5, rx=0))
    frags.append(text(x1 - 30, 172, "Шар 2 (2D ріст)", size=10, bold=True, color="#145a32"))

    tb_f1, _, _ = textbox(x1, 355, "Умова змочування:\nγ_film + γ_int ≤ γ_sub\nНизьке неузгодження (f ≈ 0)\nІдеально гладка 2D поверхня", size=10, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_f1)

    # ── Режим 2: Вольмер — Вебер ──
    x2 = 450
    tb_t2, _, _ = textbox(x2, 65, "Вольмер — Вебер\n(3D Острівцевий / VW)", size=11, bold=True, pad=6, fill="#fdedec", stroke=POS)
    frags.append(tb_t2)

    # Підкладка
    frags.append(rect(x2 - 120, 230, 240, 70, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))
    frags.append(text(x2, 275, "Підкладка (γ_sub)", size=11, color=MUTED))

    # Окремі 3D острівці (краплі)
    frags.append(rect(x2 - 100, 150, 55, 80, fill="#fadbd8", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x2 - 72, 195, "Острівець", size=10, bold=True, color=POS))

    frags.append(rect(x2 - 25, 130, 65, 100, fill="#fadbd8", stroke=POS, sw=1.5, rx=8))
    frags.append(text(x2 + 7, 185, "3D кластер", size=10, bold=True, color=POS))

    frags.append(rect(x2 + 55, 160, 50, 70, fill="#fadbd8", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x2 + 80, 200, "Острівець", size=10, bold=True, color=POS))

    tb_f2, _, _ = textbox(x2, 355, "Умова незмочування:\nγ_film + γ_int > γ_sub\nАтоми тягнуться один до одного\nШорсткість і злиття з дефектами", size=10, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_f2)

    # ── Режим 3: Странський — Крастанов ──
    x3 = 745
    tb_t3, _, _ = textbox(x3, 65, "Странський — Крастанов\n(2D Шар + 3D Острівці / SK)", size=11, bold=True, pad=6, fill="#e8eaf6", stroke=NEG)
    frags.append(tb_t3)

    # Підкладка
    frags.append(rect(x3 - 120, 230, 240, 70, fill="#f0f2f5", stroke="#7f8c8d", sw=1.5, rx=3))
    frags.append(text(x3, 275, "Підкладка (γ_sub)", size=11, color=MUTED))

    # 2D Шар змочування (Wetting layer, 1-3 моношари)
    frags.append(rect(x3 - 120, 205, 240, 25, fill="#c5cae9", stroke=NEG, sw=1.5, rx=0))
    frags.append(text(x3, 220, "2D шар змочування (Wetting layer)", size=9, bold=True, color="#1a237e"))

    # 3D Когерентні острівці / Квантові точки зверху шару змочування
    frags.append(rect(x3 - 90, 145, 50, 60, fill="#9fa8da", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x3 - 65, 178, "Квантова\nточка", size=9, bold=True, color="#1a237e"))

    frags.append(rect(x3 - 20, 135, 55, 70, fill="#9fa8da", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x3 + 7, 173, "3D острів\n(без MD)", size=9, bold=True, color="#1a237e"))

    frags.append(rect(x3 + 50, 150, 48, 55, fill="#9fa8da", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x3 + 74, 180, "Квантова\nточка", size=9, bold=True, color="#1a237e"))

    tb_f3, _, _ = textbox(x3, 355, "Пружна релаксація:\n2D ріст моношарів → ріст E_elast\nСамоорганізація 3D острівців\nРелаксація без дислокацій", size=10, pad=6, fill="#ffffff", stroke=NEG)
    frags.append(tb_f3)

    # Розділювачі
    frags.append(line(295, 55, 295, 415, color="#e0e0e0", sw=1.2, dash="4,4"))
    frags.append(line(600, 55, 600, 415, color="#e0e0e0", sw=1.2, dash="4,4"))

    render(os.path.join(IMG, "three-growth-modes.svg"), w, h, *frags)


def fig_critical_thickness_curve():
    """Фігура 3: Графік критичної товщини Метьюза — Блекслі залежно від неузгодженості ґратки."""
    w, h = 880, 440
    frags = []

    tb_main, _, _ = textbox(440, 25, "Критична товщина епітаксійного шару h_c за моделлю Метьюза — Блекслі", size=14, bold=True, pad=8)
    frags.append(tb_main)

    ox, oy = 110, 360
    gw, gh = 700, 290

    # Осі
    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Горизонтальні лінії сітки
    y_1000 = oy - gh + 20
    y_100  = oy - gh + 105
    y_10   = oy - gh + 195
    y_1    = oy - gh + 275

    frags.append(line(ox, y_1000, ox + gw, y_1000, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(ox - 10, y_1000 + 4, "1000 нм", size=10, anchor="end", color=MUTED))

    frags.append(line(ox, y_100, ox + gw, y_100, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(ox - 10, y_100 + 4, "100 нм", size=10, anchor="end", color=MUTED))

    frags.append(line(ox, y_10, ox + gw, y_10, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(ox - 10, y_10 + 4, "10 нм", size=10, anchor="end", color=MUTED))

    frags.append(line(ox, y_1, ox + gw, y_1, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(ox - 10, y_1 + 4, "1 нм", size=10, anchor="end", color=MUTED))

    # Вертикальні лінії сітки
    x_05 = ox + 100
    x_10 = ox + 260
    x_20 = ox + 450
    x_40 = ox + 640

    frags.append(line(x_05, oy - gh, x_05, oy, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(x_05, oy + 20, "0.5% (x≈0.12)", size=10, anchor="middle", color=MUTED))

    frags.append(line(x_10, oy - gh, x_10, oy, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(x_10, oy + 20, "1.0% (x≈0.24)", size=10, anchor="middle", color=MUTED))

    frags.append(line(x_20, oy - gh, x_20, oy, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(x_20, oy + 20, "2.0% (x≈0.48)", size=10, anchor="middle", color=MUTED))

    frags.append(line(x_40, oy - gh, x_40, oy, color="#e5e7eb", sw=1, dash="3,3"))
    frags.append(text(x_40, oy + 20, "4.2% (Ge/Si, x=1.0)", size=10, anchor="middle", color=MUTED))

    # Підписи осей
    frags.append(text(ox + gw / 2, oy + 45, "Невідповідність ґратки f = |a_epi - a_sub| / a_sub (частка x у сплаві Si₁₋ₓGeₓ)", size=11, bold=True, color=INK))
    frags.append(text(ox - 45, oy - gh / 2, "Критична товщина h_c", size=11, bold=True, color=INK, anchor="middle"))

    # Точки кривої
    pts = [
        (ox + 40,  oy - gh + 35),
        (ox + 100, oy - gh + 85),
        (ox + 180, oy - gh + 140),
        (ox + 260, oy - gh + 180),
        (ox + 360, oy - gh + 215),
        (ox + 450, oy - gh + 240),
        (ox + 550, oy - gh + 258),
        (ox + 640, oy - gh + 270),
        (ox + 680, oy - gh + 275)
    ]

    # Затінення областей
    path_fill_stable = f'M {pts[0][0]},{oy} L {pts[0][0]},{pts[0][1]} ' + " ".join(f"L {px:.1f},{py:.1f}" for px, py in pts[1:]) + f' L {pts[-1][0]},{oy} Z'
    frags.append(f'<path d="{path_fill_stable}" fill="#e8f8f5" opacity="0.6"/>')

    path_fill_relax = f'M {pts[0][0]},{oy-gh} L {pts[0][0]},{pts[0][1]} ' + " ".join(f"L {px:.1f},{py:.1f}" for px, py in pts[1:]) + f' L {pts[-1][0]},{oy-gh} Z'
    frags.append(f'<path d="{path_fill_relax}" fill="#fdedec" opacity="0.5"/>')

    # Лінія кривої
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    frags.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Текстові плашки в областях
    tb_st, _, _ = textbox(ox + 200, oy - 55, "ПСЕВДОМОРФНА ЗОНА (h < h_c)\n• Ґратка повністю когерентна\n• Дислокацій немає (TDD = 0)\n• Вся енергія в пружній деформації", size=10, bold=True, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_st)

    tb_rel, _, _ = textbox(ox + 500, oy - gh + 60, "РЕЛАКСОВАНА ЗОНА (h > h_c)\n• Утворення дислокацій невідповідності (MD)\n• Проростання пронизуючих дефектів (TD)\n• Релаксація пружних напружень", size=10, bold=True, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_rel)

    # Підпис біля кривої
    tb_crv, _, _ = textbox(ox + 280, oy - gh + 120, "Крива рівноваги Метьюза — Блекслі h_c(f)", size=10, bold=True, pad=4, fill="#ffffff", stroke=POS, color=POS)
    frags.append(tb_crv)

    render(os.path.join(IMG, "critical-thickness-curve.svg"), w, h, *frags)


def fig_defect_reduction_elog():
    """Фігура 4: Інженерні методи фільтрації дефектів (градієнтний буфер та ELOG)."""
    w, h = 920, 460
    frags = []

    tb_main, _, _ = textbox(460, 25, "Методи зниження густини дефектів: Градієнтні буфери та Селективна епітаксія (ELOG)", size=14, bold=True, pad=8)
    frags.append(tb_main)

    # ── Ліва частина: Градієнтний шар ──
    x_left = 225
    tb_hl, _, _ = textbox(x_left, 65, "Градієнтний буферний шар (SiGe на Si)\nСтупінчастий розподіл напружень", size=11, bold=True, pad=6, fill="#e8f4fd", stroke="#2457d6")
    frags.append(tb_hl)

    # Підкладка Si(001)
    frags.append(rect(40, 340, 370, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=0))
    frags.append(text(x_left, 375, "Кремнієва підкладка Si (x=0, бездислокаційна)", size=11, color=MUTED))

    # Ступені буфера Si_{1-x}Ge_x:
    # Шар 1: x = 0.10
    frags.append(rect(40, 290, 370, 50, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=0))
    frags.append(text(80, 320, "Si₀.₉Ge₀.₁", size=10, bold=True, color="#1e40af"))

    # Шар 2: x = 0.20
    frags.append(rect(40, 240, 370, 50, fill="#bfdbfe", stroke="#3b82f6", sw=1.2, rx=0))
    frags.append(text(80, 270, "Si₀.₈Ge₀.₂", size=10, bold=True, color="#1e40af"))

    # Шар 3: x = 0.30
    frags.append(rect(40, 190, 370, 50, fill="#93c5fd", stroke="#3b82f6", sw=1.2, rx=0))
    frags.append(text(80, 220, "Si₀.₇Ge₀.₃", size=10, bold=True, color="#1e40af"))

    # Активний релаксований шар Si₀.₇Ge₀.₃ зверху
    frags.append(rect(40, 130, 370, 60, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=0))
    frags.append(text(x_left, 165, "Активний шар надвисокої якості (TDD < 10⁵ см⁻²)", size=11, bold=True, color="#166534"))

    # Дислокації, що вигинаються в горизонтальні площини на кожному кроці
    frags.append(line(130, 340, 160, 290, color=POS, sw=1.8))
    frags.append(line(160, 290, 370, 290, color=POS, sw=1.8))
    frags.append(text(385, 287, "→ край", size=9, color=POS))

    frags.append(line(240, 290, 270, 240, color=POS, sw=1.8))
    frags.append(line(270, 240, 370, 240, color=POS, sw=1.8))
    frags.append(text(385, 237, "→ край", size=9, color=POS))

    frags.append(line(310, 240, 340, 190, color=POS, sw=1.8))
    frags.append(line(340, 190, 370, 190, color=POS, sw=1.8))
    frags.append(text(385, 187, "→ край", size=9, color=POS))

    tb_nl, _, _ = textbox(x_left, 425, "Дислокації невідповідності ковзають у боки\nі не проростають у робочу транзисторну зону", size=10, pad=5, fill="#ffffff", stroke="#2457d6")
    frags.append(tb_nl)

    # ── Права частина: Селективна епітаксія ELOG ──
    x_right = 695
    tb_hr, _, _ = textbox(x_right, 65, "Селективне заростання (ELOG для GaN)\nФільтрація дефектів діелектричною маскою", size=11, bold=True, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(tb_hr)

    # Підкладка (Сапфір / SiC)
    frags.append(rect(510, 340, 370, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=0))
    frags.append(text(x_right, 375, "Підкладка сапфір Al₂O₃ / SiC", size=11, color=MUTED))

    # Початковий дефектний GaN шар
    frags.append(rect(510, 280, 370, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=0))

    # Вертикальні пронизуючі дислокації з нижнього шару (лише в нижній зоні шару 340..325)
    for dx in [540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840]:
        frags.append(line(dx, 340, dx, 325, color=POS, sw=1.5, dash="3,2"))

    tb_seed, _, _ = textbox(x_right, 305, "Зародковий GaN (дефектний, TDD ~ 10⁹ см⁻²)", size=10, bold=True, color=POS, fill="#fee2e2", stroke=POS, pad=4)
    frags.append(tb_seed)

    # Маски SiO₂ (діелектричні смуги)
    frags.append(rect(530, 265, 110, 15, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=1))
    frags.append(text(585, 276, "Маска SiO₂", size=9, bold=True, color="#854d0e"))

    frags.append(rect(700, 265, 110, 15, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=1))
    frags.append(text(755, 276, "Маска SiO₂", size=9, bold=True, color="#854d0e"))

    # Латеральне кристалічне заростання (ELOG GaN шар)
    frags.append(rect(510, 130, 370, 135, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=2))

    # Дефекти проростають ТІЛЬКИ крізь вікна
    frags.append(line(670, 280, 670, 130, color=POS, sw=1.8, dash="3,2"))
    frags.append(line(840, 280, 840, 130, color=POS, sw=1.8, dash="3,2"))

    # Над маскою SiO₂ (Крила / Wing regions)
    frags.append(arrow(585, 260, 540, 210, color=FIELD, sw=1.8))
    frags.append(arrow(585, 260, 630, 210, color=FIELD, sw=1.8))
    frags.append(text(585, 185, "Крило (Wing)\nЧИСТИЙ GaN\nTDD < 10⁵ см⁻²", size=10, bold=True, color="#166534"))

    frags.append(arrow(755, 260, 710, 210, color=FIELD, sw=1.8))
    frags.append(arrow(755, 260, 800, 210, color=FIELD, sw=1.8))
    frags.append(text(755, 185, "Крило (Wing)\nЧИСТИЙ GaN\nTDD < 10⁵ см⁻²", size=10, bold=True, color="#166534"))

    tb_nr, _, _ = textbox(x_right, 425, "Маска SiO₂ блокує проростання TD.\nЛатеральний ріст дає бездефектні зони для лазерів", size=10, pad=5, fill="#ffffff", stroke="#d97706")
    frags.append(tb_nr)

    # Розділювач
    frags.append(line(460, 55, 460, 445, color="#e0e0e0", sw=1.2, dash="4,4"))

    render(os.path.join(IMG, "defect-reduction-elog.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_lattice_mismatch_strain()
    fig_three_growth_modes()
    fig_critical_thickness_curve()
    fig_defect_reduction_elog()
    print("All figures generated successfully.")
