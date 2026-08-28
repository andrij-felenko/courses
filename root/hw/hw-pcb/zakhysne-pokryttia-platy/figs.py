# -*- coding: utf-8 -*-
"""Фігури для теми zakhysne-pokryttia-platy (Захисне покриття плати: лак, залив, ущільнення).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра для друкованих плат і покриттів
FR4_FILL      = "#dfe6ee"
FR4_STROKE    = "#94a3b8"
COPPER_FILL   = "#e8c9a3"
COPPER_STROKE = "#b5763a"
MASK_FILL     = "#2d6a4f"
SOLDER_FILL   = "#cbd5e1"
SOLDER_STROKE = "#64748b"
IC_BODY       = "#1e293b"
IC_PIN        = "#94a3b8"
COATING_FILL  = "#38bdf8"
COATING_STROKE= "#0284c7"
POTTING_FILL  = "#e2e8f0"
POTTING_STROKE= "#64748b"
UV_GLOW       = "#3b82f6"
WARN_RED      = "#ef4444"


# ── 1. Три рівні захисту: маска, лак, повна заливка ───────────────────────────
def fig_protection_levels():
    W, H = 820, 320
    frags = []

    # Три колонки
    cols = [
        ("1. Лише паяльна маска", 35, "#fef2f2", "#f87171"),
        ("2. Конформний лак (25–75 мкм)", 295, "#f0fdf4", "#4ade80"),
        ("3. Повна заливка (Potting 5–20 мм)", 555, "#f0f9ff", "#38bdf8")
    ]

    for title_text, x0, bg_col, brd_col in cols:
        frags.append(rect(x0, 20, 230, 280, fill=bg_col, stroke=brd_col, sw=1.2, rx=8))
        frags.append(text(x0 + 115, 42, title_text, size=11, color=INK, bold=True))

    # --- Колонка 1: Маска ---
    x1 = 35
    # Плата FR-4
    frags.append(rect(x1 + 15, 180, 200, 25, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(x1 + 115, 197, "FR-4 підкладка", size=9, color=MUTED))
    # Маска
    frags.append(rect(x1 + 15, 175, 45, 6, fill=MASK_FILL, stroke=MASK_FILL, sw=0.5, rx=1))
    frags.append(rect(x1 + 80, 175, 70, 6, fill=MASK_FILL, stroke=MASK_FILL, sw=0.5, rx=1))
    frags.append(rect(x1 + 170, 175, 45, 6, fill=MASK_FILL, stroke=MASK_FILL, sw=0.5, rx=1))
    # Мідні майданчики + припій
    frags.append(rect(x1 + 60, 172, 20, 8, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=2))
    frags.append(rect(x1 + 150, 172, 20, 8, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=2))
    # SMD чіп
    frags.append(rect(x1 + 75, 140, 80, 32, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(rect(x1 + 65, 155, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x1 + 155, 155, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(text(x1 + 115, 160, "SMD IC", size=10, color="#ffffff", bold=True))
    # Відкрита волога / корозія
    frags.append(text(x1 + 70, 125, "Волога, пил, сіль", size=9, color=POS, bold=True))
    frags.append(arrow(x1 + 68, 128, x1 + 68, 150, color=POS, sw=1.5))
    frags.append(arrow(x1 + 162, 128, x1 + 162, 150, color=POS, sw=1.5))
    b1, _, _ = textbox(x1 + 115, 245, ["Паяні шви та ніжки відкриті.", "Ризик роси, корозії та КЗ."], size=9, pad=5, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b1)

    # --- Колонка 2: Конформний лак ---
    x2 = 295
    # Плата FR-4
    frags.append(rect(x2 + 15, 180, 200, 25, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(x2 + 115, 197, "FR-4 підкладка", size=9, color=MUTED))
    # SMD чіп
    frags.append(rect(x2 + 75, 140, 80, 32, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(rect(x2 + 65, 155, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x2 + 155, 155, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(text(x2 + 115, 160, "SMD IC", size=10, color="#ffffff", bold=True))
    # Конформний шар (тонка суцільна лінія-оболонка)
    frags.append(rect(x2 + 15, 174, 50, 6, fill=COATING_FILL, stroke=COATING_STROKE, sw=1.2, rx=1))
    frags.append(rect(x2 + 63, 137, 104, 38, fill="none", stroke=COATING_STROKE, sw=2.5, rx=3))
    frags.append(rect(x2 + 165, 174, 50, 6, fill=COATING_FILL, stroke=COATING_STROKE, sw=1.2, rx=1))
    frags.append(text(x2 + 115, 125, "Тонка плівка (25–75 мкм)", size=9, color=COATING_STROKE, bold=True))
    b2, _, _ = textbox(x2 + 115, 245, ["Покриває всі шви й контури.", "Захист від конденсату й солі.", "Легка вага, плата дихає."], size=9, pad=5, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b2)

    # --- Колонка 3: Повна заливка (Potting) ---
    x3 = 555
    # Корпус заливки
    frags.append(rect(x3 + 10, 75, 210, 135, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(x3 + 115, 92, "Моноліт компаунда", size=10, color="#0369a1", bold=True))
    # Плата FR-4 всередині
    frags.append(rect(x3 + 20, 175, 190, 20, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    # SMD чіп всередині
    frags.append(rect(x3 + 75, 135, 80, 32, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(rect(x3 + 65, 150, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x3 + 155, 150, 10, 17, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(text(x3 + 115, 155, "SMD IC", size=10, color="#ffffff", bold=True))
    b3, _, _ = textbox(x3 + 115, 245, ["Суцільний моноліт смоли.", "Герметичність, ударостійкість,", "тепловідвід, антивандальність."], size=9, pad=5, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b3)

    return render(os.path.join(OUT, "protection-levels-comparison.svg"), W, H, *frags)


# ── 2. Механізм електрохімічної міграції (ECM) та дендритів ───────────────────
def fig_ecm_mechanism():
    W, H = 800, 380
    frags = []

    frags.append(rect(15, 15, 770, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(400, 38, "Електрохімічна міграція (ECM) між відкритими провідниками", size=13, color=INK, bold=True))

    # Склотекстоліт FR-4
    frags.append(rect(40, 240, 720, 45, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.5, rx=3))
    frags.append(text(400, 267, "Діелектрична основа друкованої плати (FR-4)", size=11, color=MUTED))

    # Провідник 1: Анод (+24 В)
    frags.append(rect(80, 200, 140, 40, fill=COPPER_FILL, stroke=COPPER_STROKE, sw=1.5, rx=2))
    frags.append(text(150, 218, "Анод (+V)", size=12, color=POS, bold=True))
    frags.append(text(150, 233, "Cu / Sn / Ag", size=9, color=MUTED))

    # Провідник 2: Катод (GND, 0 В)
    frags.append(rect(580, 200, 140, 40, fill=COPPER_FILL, stroke=COPPER_STROKE, sw=1.5, rx=2))
    frags.append(text(650, 218, "Катод (0 В)", size=12, color=NEG, bold=True))
    frags.append(text(650, 233, "GND шина", size=9, color=MUTED))

    # Водна електролітична плівка (конденсат + солі)
    frags.append(rect(220, 232, 360, 8, fill="#93c5fd", stroke="#3b82f6", sw=1.0, rx=2))
    frags.append(text(400, 222, "Волога плівка електроліту (H2O + іони солей Cl⁻, SO4²⁻)", size=10, color="#1d4ed8", bold=True))

    # Стадії процесу
    # 1. Окиснення анода
    b_anode, _, _ = textbox(150, 120, [
        "1. Анодне розчинення:",
        "Cu → Cu²⁺ + 2e⁻",
        "Sn → Sn²⁺ + 2e⁻",
        "Метал переходить в іони"
    ], size=10, pad=6, fill="#fef2f2", stroke="#f87171")
    frags.append(b_anode)
    frags.append(arrow(150, 165, 150, 195, color=POS, sw=1.5))

    # 2. Міграція іонів під дією поля E
    frags.append(line(240, 170, 560, 170, color="#2563eb", sw=1.8, dash="5,4"))
    frags.append(circle(320, 170, 12, fill="#dbeafe", stroke="#2563eb", sw=1.2))
    frags.append(text(320, 174, "Cu²⁺", size=9, color="#1e40af", bold=True))
    frags.append(circle(440, 170, 12, fill="#dbeafe", stroke="#2563eb", sw=1.2))
    frags.append(text(440, 174, "Sn²⁺", size=9, color="#1e40af", bold=True))
    frags.append(arrow(470, 170, 540, 170, color="#2563eb", sw=1.8))
    frags.append(text(400, 150, "2. Дрейф катіонів у полі E (від + до −)", size=10, color="#1e40af"))

    # 3. Відновлення та ріст дендритів від катода
    b_kath, _, _ = textbox(650, 120, [
        "3. Відновлення металу:",
        "Cu²⁺ + 2e⁻ → Cu⁰",
        "Sn²⁺ + 2e⁻ → Sn⁰",
        "Ріст дендрита до анода"
    ], size=10, pad=6, fill="#eff6ff", stroke="#60a5fa")
    frags.append(b_kath)
    frags.append(arrow(650, 165, 650, 195, color=NEG, sw=1.5))

    # Зображення деревоподібного дендрита
    dendrite_lines = [
        (580, 236, 520, 235),
        (520, 235, 480, 232),
        (520, 235, 490, 238),
        (480, 232, 430, 230),
        (480, 232, 440, 236),
        (430, 230, 360, 234),
        (360, 234, 280, 233),
        (280, 233, 225, 235)  # майже замкнув анод
    ]
    for x1, y1, x2, y2 in dendrite_lines:
        frags.append(line(x1, y1, x2, y2, color="#dc2626", sw=2.2))
    frags.append(circle(225, 235, 4, fill="#dc2626", stroke="#991b1b", sw=1))
    frags.append(text(380, 298, "Дендритний місток замикає зазор → спалах КЗ та вигоряння доріжок", size=10, color=POS, bold=True))

    b_bot, _, _ = textbox(400, 335, [
        "Конформне покриття ізолює провідники від вологи й солей, унеможливлюючи утворення рідкого електроліту."
    ], size=10, pad=5, fill="#f0fdf4", stroke="#86efac")
    frags.append(b_bot)

    return render(os.path.join(OUT, "electrochemical-migration-mechanism.svg"), W, H, *frags)


# ── 3. Профіль покриття: рідкі лаки проти вакуумного Парилену ──────────────────
def fig_coating_profiles():
    W, H = 820, 340
    frags = []

    frags.append(rect(15, 15, 790, 310, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(410, 38, "Конформність шару: рідкі лаки (AR/UR/SR/ER) проти Парилену (XY, CVD)", size=13, color=INK, bold=True))

    # Ліва половина: Рідкі лаки
    x_l = 40
    frags.append(rect(x_l, 60, 350, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(x_l + 175, 82, "Рідкі лаки (розпилення, занурення)", size=11, color=INK, bold=True))

    # Текстоліт
    frags.append(rect(x_l + 25, 220, 300, 20, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    # IC корпус з гострою ніжкою
    frags.append(rect(x_l + 50, 150, 110, 50, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(text(x_l + 105, 180, "QFP корпус", size=10, color="#ffffff", bold=True))
    # Гостра ніжка QFP (ламані лінії)
    frags.append(rect(x_l + 160, 175, 50, 6, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x_l + 205, 181, 6, 35, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x_l + 205, 214, 25, 6, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))

    # Рідкий лак: стягується з гострих граней (стоншення до 5 мкм) і накопичується в кутах (меніск 120 мкм)
    frags.append(line(x_l + 25, 218, x_l + 325, 218, color=COATING_STROKE, sw=3.0))
    # Меніск біля пайки
    frags.append(circle(x_l + 230, 214, 6, fill=COATING_FILL, stroke=COATING_STROKE, sw=1))
    # Попередження про гострі грані
    frags.append(arrow(x_l + 240, 160, x_l + 215, 180, color=POS, sw=1.5))
    frags.append(text(x_l + 260, 155, "Стоншення на ребрі (<5 мкм)", size=9, color=POS, bold=True))
    frags.append(arrow(x_l + 105, 230, x_l + 105, 205, color=POS, sw=1.5))
    frags.append(text(x_l + 105, 245, "Тінь під корпусом: лак не затікає", size=9, color=POS))

    b_liq, _, _ = textbox(x_l + 175, 280, ["Поверхневий натяг стягує лак з гострих кутів.", "Нерівномірна товщина: 5...120 мкм."], size=9, pad=4, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b_liq)

    # Права половина: Parylene (CVD)
    x_r = 430
    frags.append(rect(x_r, 60, 350, 245, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(x_r + 175, 82, "Парилен XY (Вакуумне осадження CVD)", size=11, color="#15803d", bold=True))

    # Текстоліт
    frags.append(rect(x_r + 25, 220, 300, 20, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    # IC корпус
    frags.append(rect(x_r + 50, 150, 110, 50, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(text(x_r + 105, 180, "QFP корпус", size=10, color="#ffffff", bold=True))
    # Гостра ніжка QFP
    frags.append(rect(x_r + 160, 175, 50, 6, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x_r + 205, 181, 6, 35, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))
    frags.append(rect(x_r + 205, 214, 25, 6, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1, rx=1))

    # Париленовий шар (рівномірна товщина 15 мкм скрізь)
    frags.append(line(x_r + 25, 218, x_r + 325, 218, color="#16a34a", sw=2.5))
    frags.append(rect(x_r + 48, 147, 114, 56, fill="none", stroke="#16a34a", sw=2.0, rx=3))
    # Проникнення під корпус
    frags.append(line(x_r + 50, 201, x_r + 160, 201, color="#16a34a", sw=2.0))
    frags.append(arrow(x_r + 270, 160, x_r + 215, 180, color="#15803d", sw=1.5))
    frags.append(text(x_r + 275, 155, "Рівномірно 15 мкм на ребрі", size=9, color="#15803d", bold=True))
    frags.append(arrow(x_r + 105, 230, x_r + 105, 205, color="#15803d", sw=1.5))
    frags.append(text(x_r + 105, 245, "Газ вільно заходить під корпус", size=9, color="#15803d"))

    b_par, _, _ = textbox(x_r + 175, 280, ["Газофазна полімеризація без розчинника.", "Ідеальна товщина без пінхолів та менісків."], size=9, pad=4, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b_par)

    return render(os.path.join(OUT, "coating-profiles-comparison.svg"), W, H, *frags)


# ── 4. Термонапруження при заливці (CTE Mismatch) ──────────────────────────────
def fig_potting_cte_stress():
    W, H = 800, 350
    frags = []

    frags.append(rect(15, 15, 770, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(400, 38, "Механічні напруження при термоциклах (CTE Mismatch у компаунді)", size=13, color=INK, bold=True))

    # Верхня інформаційна панель з коефіцієнтами КТР
    frags.append(rect(35, 55, 730, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(400, 72, "Коефіцієнти теплового розширення (КТР / CTE):", size=10, color=MUTED, bold=True))
    frags.append(text(400, 88, "Кремній: 3 ppm/K  |  Кераміка MLCC: 9 ppm/K  |  FR-4 (X-Y): 14–17 ppm/K  |  Компаунд: 60–180 ppm/K", size=9, color=INK, bold=True))

    # Сцена: Охолодження моноліту заливки (-40 °C)
    x0, y0 = 40, 115

    # Заливка смолою (стискається сильніше за все)
    frags.append(rect(x0, y0, 720, 150, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(x0 + 360, y0 + 20, "Компаунд заливки (стискається в 5–10 разів сильніше за плату при -40 °C)", size=11, color="#334155", bold=True))

    # Стрілки стиснення компаунда (всередину)
    frags.append(arrow(x0 + 30, y0 + 75, x0 + 80, y0 + 75, color=NEG, sw=2.5))
    frags.append(arrow(x0 + 690, y0 + 75, x0 + 640, y0 + 75, color=NEG, sw=2.5))
    frags.append(arrow(x0 + 360, y0 + 30, x0 + 360, y0 + 60, color=NEG, sw=2.5))

    # Плата FR-4
    frags.append(rect(x0 + 100, y0 + 100, 520, 25, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(x0 + 360, y0 + 116, "Друкована плата FR-4 (CTE = 15 ppm/K)", size=10, color=MUTED))

    # Компонент 1: Керамічний конденсатор MLCC (тріскається від напруження)
    frags.append(rect(x0 + 140, y0 + 70, 70, 30, fill="#b45309", stroke="#78350f", sw=1.2, rx=2))
    frags.append(text(x0 + 175, y0 + 88, "MLCC 1206", size=9, color="#ffffff", bold=True))
    # Тріщина в кераміці
    frags.append(line(x0 + 165, y0 + 70, x0 + 180, y0 + 100, color=WARN_RED, sw=2.0))
    frags.append(arrow(x0 + 175, y0 + 45, x0 + 175, y0 + 65, color=WARN_RED, sw=1.5))
    frags.append(text(x0 + 175, y0 + 38, "Розтріскування кераміки", size=9, color=WARN_RED, bold=True))

    # Компонент 2: BGA мікросхема (зрізання паяних кульок)
    frags.append(rect(x0 + 380, y0 + 60, 180, 25, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(text(x0 + 470, y0 + 76, "BGA чип (Si, CTE = 3 ppm/K)", size=9, color="#ffffff", bold=True))
    # Кульки BGA
    for bx in range(x0 + 395, x0 + 555, 25):
        frags.append(circle(bx, y0 + 92, 4, fill=SOLDER_FILL, stroke=SOLDER_STROKE, sw=1))
    # Зрізаюче зусилля на крайніх кульках
    frags.append(arrow(x0 + 370, y0 + 92, x0 + 390, y0 + 92, color=WARN_RED, sw=2.0))
    frags.append(arrow(x0 + 570, y0 + 92, x0 + 550, y0 + 92, color=WARN_RED, sw=2.0))
    frags.append(text(x0 + 470, y0 + 50, "Зсувні напруження на паяних кульках (Shear Fatigue)", size=9, color=WARN_RED, bold=True))

    # Нижня рекомендація
    b_rec, _, _ = textbox(400, 295, [
        "Рішення: вибір еластичних компаундів (Shore A < 60), буферні силіконові підслої",
        "та компаунди з температурою склування (Tg) нижче робочого діапазону."
    ], size=9, pad=5, fill="#f0fdf4", stroke="#86efac")
    frags.append(b_rec)

    return render(os.path.join(OUT, "potting-cte-mismatch-stresses.svg"), W, H, *frags)


# ── 5. Селективне нанесення, заборонені зони та УФ-інспекція ──────────────────
def fig_selective_masking_uv():
    W, H = 820, 360
    frags = []

    frags.append(rect(15, 15, 790, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(410, 38, "Селективне нанесення лаку, Keep-out зони та контроль під УФ (365 нм)", size=13, color=INK, bold=True))

    # Ліва сцена: Топологія плати з Keep-out зонами
    x_l = 35
    frags.append(rect(x_l, 60, 360, 265, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(x_l + 180, 82, "1. Зони маскування (Keep-out zones)", size=11, color=INK, bold=True))

    # Плата
    frags.append(rect(x_l + 20, 95, 320, 180, fill="#15803d", stroke="#166534", sw=1.5, rx=4))

    # Зона 1: Роз'єм USB / Header (Заборонено!)
    frags.append(rect(x_l + 30, 110, 50, 45, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))
    frags.append(text(x_l + 55, 136, "USB", size=9, color="#ffffff", bold=True))
    frags.append(rect(x_l + 26, 106, 58, 53, fill="none", stroke=WARN_RED, sw=2.0, rx=2))
    frags.append(text(x_l + 55, 172, "Роз'єми (NO COAT)", size=9, color=WARN_RED, bold=True))

    # Зона 2: MEMS барометр / мікрофон (Заборонено!)
    frags.append(rect(x_l + 250, 110, 40, 35, fill="#cbd5e1", stroke="#64748b", sw=1.2, rx=2))
    frags.append(circle(x_l + 270, 127, 4, fill="#0f172a", stroke="#0f172a", sw=1))
    frags.append(rect(x_l + 245, 105, 50, 45, fill="none", stroke=WARN_RED, sw=2.0, rx=2))
    frags.append(text(x_l + 270, 162, "MEMS отвір", size=9, color=WARN_RED, bold=True))

    # Зона 3: Кнопка Reset (Заборонено!)
    frags.append(circle(x_l + 55, 220, 14, fill="#e2e8f0", stroke="#64748b", sw=1.2))
    frags.append(circle(x_l + 55, 220, 8, fill="#ef4444", stroke="#b91c1c", sw=1))
    frags.append(text(x_l + 55, 248, "Тактові кнопки", size=9, color=WARN_RED, bold=True))

    # Дозволена зона: MCU + пасивні компоненти
    frags.append(rect(x_l + 130, 130, 80, 80, fill=IC_BODY, stroke=LINE, sw=1.2, rx=2))
    frags.append(text(x_l + 170, 175, "MCU", size=11, color="#ffffff", bold=True))
    frags.append(text(x_l + 170, 225, "Зона селективного лакування", size=9, color="#86efac"))

    b_mask, _, _ = textbox(x_l + 180, 295, ["Лак у роз'ємах розриває контакт,", "у MEMS — закупорює акустичний канал."], size=9, pad=4, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b_mask)

    # Права сцена: УФ контроль під 365 нм лампою Вуда
    x_r = 425
    frags.append(rect(x_r, 60, 360, 265, fill="#0f172a", stroke="#334155", sw=1.2, rx=6))
    frags.append(text(x_r + 180, 82, "2. УФ-інспекція (Fluorescent Dye, 365 нм)", size=11, color="#38bdf8", bold=True))

    # Плата під УФ
    frags.append(rect(x_r + 20, 110, 320, 150, fill="#1e293b", stroke="#475569", sw=1.2, rx=4))

    # Флуоресцентне яскраве світіння лаку (блакитно-зелене)
    frags.append(rect(x_r + 100, 120, 160, 130, fill="#0369a1", stroke="#38bdf8", sw=2.0, rx=4))
    frags.append(text(x_r + 180, 185, "Лак світиться яскраво-синім", size=10, color="#e0f2fe", bold=True))

    # Дефект: Пінхол / непролакована ділянка (темна пляма)
    frags.append(circle(x_r + 140, 150, 12, fill="#0f172a", stroke="#ef4444", sw=2))
    frags.append(arrow(x_r + 100, 140, x_r + 125, 148, color="#ef4444", sw=1.5))
    frags.append(text(x_r + 85, 135, "Пінхол (дефект)", size=9, color="#ef4444", bold=True))

    # Дефект: Небажане затікання в роз'єм
    frags.append(rect(x_r + 30, 125, 45, 40, fill="#0f172a", stroke="#64748b", sw=1))
    frags.append(rect(x_r + 35, 130, 20, 15, fill="#0284c7", stroke="#38bdf8", sw=1))
    frags.append(arrow(x_r + 45, 190, x_r + 45, 155, color="#ef4444", sw=1.5))
    frags.append(text(x_r + 45, 200, "Затік у роз'єм!", size=9, color="#ef4444", bold=True))

    b_uv, _, _ = textbox(x_r + 180, 295, ["Оптичний контроль за секунди виявляє прогалини,", "бульбашки, пінхоли та затікання на контакти."], size=9, pad=4, fill="#1e293b", stroke="#0284c7", color="#e0f2fe")
    frags.append(b_uv)

    return render(os.path.join(OUT, "selective-coating-and-inspection.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_protection_levels()
    fig_ecm_mechanism()
    fig_coating_profiles()
    fig_potting_cte_stress()
    fig_selective_masking_uv()
    print("Усі фігури згенеровано успішно.")
