# -*- coding: utf-8 -*-
"""Фігури до теми «Дозрівання виходу (yield ramp)» та її вставок.
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра для компонентів напівпровідникового виробництва та аналізу дефектів
C_LINE     = "#2457d6"   # синій (Line Yield)
C_RANDOM   = "#c0392b"   # червоний (Random Defect Yield)
C_SYST     = "#d97706"   # помаранчевий (Systematic Yield)
C_PARAM    = "#7c3aed"   # фіолетовий (Parametric Yield)
C_TOTAL    = "#27ae60"   # зелений (Total Composite Yield)
C_WARN     = "#d97706"

C_BOX_BG   = "#f8fafc"
C_BOX_LINE = "#cbd5e1"
C_HIGHLIGHT= "#fef3c7"


# ── Фігура 1: Крива дозрівання виходу (Yield Learning Curve) та її компоненти ──
def fig_yield_ramp_curve():
    W, H = 860, 520
    f = [text(W / 2, 28, "Динаміка нарощування виходу при освоєнні нового техпроцесу", size=15, bold=True)]

    # Основний графік: рамка і осі
    gx, gy, gw, gh = 80, 60, 480, 360
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))

    # Горизонтальні лінії сітки (0%, 20%, 40%, 60%, 80%, 100%)
    for i, y_pct in enumerate([0, 20, 40, 60, 80, 100]):
        y_pos = gy + gh - (gh * y_pct / 100)
        f.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e8f0", sw=1.0, dash="3,3" if i > 0 else None))
        f.append(text(gx - 12, y_pos + 4, "%d%%" % y_pct, size=11, color=MUTED, anchor="end"))

    # Фази процесу по осі X
    phases = [
        ("R&D / Alpha", 0.18),
        ("Risk Production", 0.46),
        ("Pilot Ramp", 0.72),
        ("HVM (Зрілий)", 0.92)
    ]
    for name, pos_ratio in phases:
        x_pos = gx + gw * pos_ratio
        f.append(line(x_pos, gy, x_pos, gy + gh, color="#cbd5e1", sw=1.0, dash="4,4"))
        f.append(text(x_pos, gy + gh + 22, name, size=10.5, color=INK, anchor="middle", bold=True))

    f.append(text(gx + gw / 2, gy + gh + 42, "Час освоєння техпроцесу (місяці) / Накопичений обсяг пластин", size=11, color=MUTED))
    f.append(text(gx - 45, gy + gh / 2, "Вихід придатних (%)", size=11, color=INK, anchor="middle"))

    # Криві компонентів виходу
    # 1. Line Yield (Y_line: 75% -> 98%)
    p_line = "M %d %d Q %d %d %d %d" % (gx, gy + gh - gh*0.75, gx + gw*0.3, gy + gh - gh*0.94, gx + gw, gy + gh - gh*0.98)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (p_line, C_LINE))

    # 2. Parametric Yield (Y_param: 40% -> 96%)
    p_param = "M %d %d Q %d %d %d %d" % (gx, gy + gh - gh*0.40, gx + gw*0.4, gy + gh - gh*0.82, gx + gw, gy + gh - gh*0.96)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="3,3"/>' % (p_param, C_PARAM))

    # 3. Systematic Yield (Y_syst: 25% -> 95%)
    p_syst = "M %d %d Q %d %d %d %d" % (gx, gy + gh - gh*0.25, gx + gw*0.45, gy + gh - gh*0.78, gx + gw, gy + gh - gh*0.95)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_syst, C_SYST))

    # 4. Random Defect Yield (Y_rand: 30% -> 94%)
    p_rand = "M %d %d Q %d %d %d %d" % (gx, gy + gh - gh*0.30, gx + gw*0.5, gy + gh - gh*0.75, gx + gw, gy + gh - gh*0.94)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="8,3"/>' % (p_rand, C_RANDOM))

    # 5. Total Composite Yield (Y_total = Y_line * Y_rand * Y_syst * Y_param: 2% -> 85%)
    p_total = "M %d %d Q %d %d %d %d" % (gx, gy + gh - gh*0.02, gx + gw*0.55, gy + gh - gh*0.45, gx + gw, gy + gh - gh*0.85)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.6"/>' % (p_total, C_TOTAL))

    # Легенда праворуч
    lx, ly, lw, lh = 585, 60, 250, 420
    f.append(rect(lx, ly, lw, lh, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.5, rx=6))
    f.append(text(lx + lw / 2, ly + 24, "Компоненти виходу", size=13, bold=True))

    items = [
        (C_TOTAL, "Загальний вихід (Y_total)", "Добуток усіх факторів (цільовий >85%)", "solid_thick"),
        (C_LINE, "Лінійний вихід (Y_line)", "Цілісність пластин, безаварійність обладнання", "dash_wide"),
        (C_SYST, "Систематичний (Y_syst)", "Літографія, OPC, CMP, дизайн-маржі", "solid"),
        (C_RANDOM, "Випадковий (Y_rand)", "Частинки пилу, дефекти матеріалів", "dash_long"),
        (C_PARAM, "Параметричний (Y_param)", "Швидкість, витоки, розкид напруг Vth", "dash_short")
    ]

    cur_y = ly + 48
    for col, title, desc, style in items:
        # Лінія-зразок
        if style == "solid_thick":
            f.append(line(lx + 15, cur_y + 8, lx + 50, cur_y + 8, color=col, sw=3.5))
        elif style == "dash_wide":
            f.append(line(lx + 15, cur_y + 8, lx + 50, cur_y + 8, color=col, sw=2.2, dash="6,4"))
        elif style == "solid":
            f.append(line(lx + 15, cur_y + 8, lx + 50, cur_y + 8, color=col, sw=2.2))
        elif style == "dash_long":
            f.append(line(lx + 15, cur_y + 8, lx + 50, cur_y + 8, color=col, sw=2.2, dash="8,3"))
        elif style == "dash_short":
            f.append(line(lx + 15, cur_y + 8, lx + 50, cur_y + 8, color=col, sw=2.2, dash="3,3"))

        f.append(text(lx + 60, cur_y + 12, title, size=11, bold=True, anchor="start", color=INK))
        f.append(text(lx + 15, cur_y + 30, desc, size=9.5, color=MUTED, anchor="start"))
        cur_y += 50

    # Блок пояснення знизу легенди
    f.append(rect(lx + 10, cur_y + 10, lw - 20, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    f.append(text(lx + lw / 2, cur_y + 28, "Модель кривої навчання:", size=10.5, bold=True))
    f.append(text(lx + lw / 2, cur_y + 48, "D(t) = D_0 · e^(−k·t)", size=11, bold=True, color=C_TOTAL))
    f.append(text(lx + lw / 2, cur_y + 68, "де k — швидкість навчання,", size=9.5, color=MUTED))
    f.append(text(lx + lw / 2, cur_y + 84, "t — накопичений досвід/час", size=9.5, color=MUTED))

    # Виноски на графіку
    f.append(circle(gx + gw*0.18, gy + gh - gh*0.06, 4, fill=C_TOTAL, stroke="#ffffff", sw=1.5))
    f.append(circle(gx + gw*0.92, gy + gh - gh*0.84, 4, fill=C_TOTAL, stroke="#ffffff", sw=1.5))
    f.append(text(gx + gw*0.18 + 10, gy + gh - gh*0.06 - 10, "Ранній кремній (~5%)", size=9.5, color=C_TOTAL, bold=True))
    f.append(text(gx + gw*0.92 - 25, gy + gh - gh*0.84 - 12, "HVM рівень (>85%)", size=9.5, color=C_TOTAL, bold=True))

    render(os.path.join(IMG, 'yield-ramp-curve.svg'), W, H, *f)


# ── Фігура 2: Випадкові проти систематичних дефектів ──────────────────────────
def fig_random_vs_systematic_defects():
    W, H = 860, 480
    f = [text(W / 2, 28, "Порівняння дефектів: випадкові частинки проти систематичних ефектів", size=15, bold=True)]

    # Ліва колонка: Випадкові дефекти (Random Particle Contamination)
    x1, y1, w_col, h_col = 25, 55, 395, 400
    f.append(rect(x1, y1, w_col, h_col, fill="#ffffff", stroke=C_RANDOM, sw=1.5, rx=8))
    f.append(text(x1 + w_col / 2, y1 + 25, "Випадкові дефекти (Random Defects)", size=13, bold=True, color=C_RANDOM))
    f.append(text(x1 + w_col / 2, y1 + 42, "Частинки пилу, краплі емульсії, лусочки з камер", size=10, color=MUTED))

    # Схема 1: Замикання частинкою
    f.append(rect(x1 + 20, y1 + 60, w_col - 40, 140, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x1 + w_col / 2, y1 + 80, "Замикання провідників частинкою (Bridge)", size=11, bold=True))
    # Провідники
    f.append(rect(x1 + 50, y1 + 100, 110, 20, fill="#94a3b8", stroke=LINE, sw=1.0, rx=2))
    f.append(rect(x1 + 50, y1 + 140, 110, 20, fill="#94a3b8", stroke=LINE, sw=1.0, rx=2))
    f.append(rect(x1 + 210, y1 + 100, 130, 20, fill="#94a3b8", stroke=LINE, sw=1.0, rx=2))
    f.append(rect(x1 + 210, y1 + 140, 130, 20, fill="#94a3b8", stroke=LINE, sw=1.0, rx=2))
    # Частинка-дефект
    f.append(circle(x1 + 275, y1 + 130, 18, fill="#fee2e2", stroke=C_RANDOM, sw=1.8))
    f.append(text(x1 + 275, y1 + 135, "Пил", size=10, bold=True, color=C_RANDOM))
    f.append(text(x1 + 105, y1 + 175, "Нормальні лінії", size=9.5, color=MUTED))
    f.append(text(x1 + 275, y1 + 175, "Закорочено частинкою", size=9.5, color=C_RANDOM, bold=True))

    # Схема 2: Обрив через частинку на фотошаблоні/резисті
    f.append(rect(x1 + 20, y1 + 215, w_col - 40, 135, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x1 + w_col / 2, y1 + 235, "Обрив лінії через блокування світла (Open)", size=11, bold=True))
    f.append(rect(x1 + 50, y1 + 260, 260, 22, fill="#94a3b8", stroke=LINE, sw=1.0, rx=2))
    # Дефект усунення (виріз)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" stroke="%s" stroke-width="1.8" stroke-dasharray="2,2"/>' %
             (x1 + 180, y1 + 271, 14, C_RANDOM))
    f.append(text(x1 + 180, y1 + 275, "×", size=14, bold=True, color=C_RANDOM))
    f.append(text(x1 + 180, y1 + 305, "Обрив провідника (Pinhole / Void)", size=9.5, color=C_RANDOM, bold=True))
    f.append(text(x1 + w_col / 2, y1 + 332, "Характеристика: Пуассонівська статистика, знижується чистотою кімнати", size=9, color=MUTED))

    # Підсумок лівої колонки
    f.append(rect(x1 + 20, y1 + 360, w_col - 40, 30, fill="#fee2e2", stroke=C_RANDOM, sw=1.0, rx=4))
    f.append(text(x1 + w_col / 2, y1 + 380, "Метод боротьби: ISO 1 фільтрація, ультрачиста хімія, FOUP", size=9.5, bold=True, color=C_RANDOM))


    # Права колонка: Систематичні дефекти (Systematic Litho & Process Defects)
    x2 = x1 + w_col + 20
    f.append(rect(x2, y1, w_col, h_col, fill="#ffffff", stroke=C_SYST, sw=1.5, rx=8))
    f.append(text(x2 + w_col / 2, y1 + 25, "Систематичні дефекти (Systematic Defects)", size=13, bold=True, color=C_SYST))
    f.append(text(x2 + w_col / 2, y1 + 42, "Оптичні спотворення, CMP-ерозія, крайові ефекти", size=10, color=MUTED))

    # Схема 1: Оптичний ефект зближення (OPC Line-end pullback)
    f.append(rect(x2 + 20, y1 + 60, w_col - 40, 140, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x2 + w_col / 2, y1 + 80, "Оптичний розрив (Line-End Pullback / Pinch)", size=11, bold=True))
    # Задумана маска (пунктир)
    f.append('<rect x="%.1f" y="%.1f" width="110" height="20" rx="3" fill="none" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (x2 + 50, y1 + 105))
    f.append('<rect x="%.1f" y="%.1f" width="110" height="20" rx="3" fill="none" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (x2 + 180, y1 + 105))
    # Реальна літографія з заокругленням і стягуванням
    f.append('<path d="M %d %d L %d %d Q %d %d %d %d L %d %d Z" fill="#cbd5e1" stroke="%s" stroke-width="1.2"/>' %
             (x2 + 50, y1 + 107, x2 + 140, y1 + 107, x2 + 148, y1 + 115, x2 + 140, y1 + 123, x2 + 50, y1 + 123, LINE))
    f.append('<path d="M %d %d L %d %d Q %d %d %d %d L %d %d Z" fill="#cbd5e1" stroke="%s" stroke-width="1.2"/>' %
             (x2 + 290, y1 + 107, x2 + 200, y1 + 107, x2 + 192, y1 + 115, x2 + 200, y1 + 123, x2 + 290, y1 + 123, LINE))
    # Перехідний отвір (Via), що повис у повітрі
    f.append(circle(x2 + 190, y1 + 115, 6, fill="#fef08a", stroke=C_WARN, sw=1.5))
    f.append(text(x2 + 190, y1 + 145, "Втрата контакту перехідного отвору (Via unlanded)", size=9.5, color=C_WARN, bold=True))
    f.append(text(x2 + w_col / 2, y1 + 175, "Причина: дифракційне заокруглення кутів без корекції OPC", size=9, color=MUTED))

    # Схема 2: CMP Dishing & Erosion
    f.append(rect(x2 + 20, y1 + 215, w_col - 40, 135, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x2 + w_col / 2, y1 + 235, "CMP Dishing (прогин у широких металевих шинах)", size=11, bold=True))
    # Профіль оксиду
    f.append(rect(x2 + 40, y1 + 260, 60, 35, fill="#e2e8f0", stroke=LINE, sw=1.0))
    f.append(rect(x2 + 260, y1 + 260, 60, 35, fill="#e2e8f0", stroke=LINE, sw=1.0))
    # Металева шина з прогином
    dishing_path = "M %d %d L %d %d Q %d %d %d %d L %d %d L %d %d Z" % (
        x2 + 100, y1 + 295, x2 + 100, y1 + 260, x2 + 180, y1 + 278, x2 + 260, y1 + 260, x2 + 260, y1 + 295, x2 + 100, y1 + 295
    )
    f.append('<path d="%s" fill="#fed7aa" stroke="%s" stroke-width="1.2"/>' % (dishing_path, C_SYST))
    f.append(text(x2 + 180, y1 + 270, "Прогин (Dishing)", size=9.5, bold=True, color=C_SYST))
    f.append(text(x2 + 70, y1 + 280, "SiO₂", size=10, color=MUTED))
    f.append(text(x2 + 290, y1 + 280, "SiO₂", size=10, color=MUTED))
    f.append(text(x2 + w_col / 2, y1 + 315, "Наслідок: нерівномірний опір, ризик розриву наступного шару", size=9, color=MUTED))
    f.append(text(x2 + w_col / 2, y1 + 332, "Характеристика: повторюється в тих самих координатах чипа", size=9, color=MUTED))

    # Підсумок правої колонки
    f.append(rect(x2 + 20, y1 + 360, w_col - 40, 30, fill="#ffedd5", stroke=C_SYST, sw=1.0, rx=4))
    f.append(text(x2 + w_col / 2, y1 + 380, "Метод боротьби: DFM-правила, Dummy metal fill, Inverse Litho (ILT)", size=9.5, bold=True, color=C_SYST))

    render(os.path.join(IMG, 'random-vs-systematic-defects.svg'), W, H, *f)


# ── Фігура 3: Тестові структури (SRAM Yield Vehicles та Comb-Serpentine) ───────
def fig_test_structures_sram_comb():
    W, H = 860, 490
    f = [text(W / 2, 28, "Тестові структури для прискореної діагностики дефектів", size=15, bold=True)]

    # Ліва частина: Comb & Serpentine (Змійки та гребінки)
    x1, y1, w1, h1 = 25, 55, 395, 410
    f.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 25, "Змійкові та гребінчасті структури (Comb-Serpentine)", size=12, bold=True))
    f.append(text(x1 + w1 / 2, y1 + 42, "Швидкий електричний контроль замикань та обривів", size=10, color=MUTED))

    # Рисунок гребінки (Interdigitated Comb)
    f.append(rect(x1 + 20, y1 + 60, w1 - 40, 160, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x1 + w1 / 2, y1 + 80, "Гребінка (Comb): тест на бічні замикання", size=11, bold=True))

    # Шина A (синя)
    f.append(rect(x1 + 40, y1 + 95, 12, 100, fill="#93c5fd", stroke=C_LINE, sw=1.2))
    for i in range(4):
        f.append(rect(x1 + 52, y1 + 105 + i * 24, 250, 8, fill="#93c5fd", stroke=C_LINE, sw=1.2))
    f.append(text(x1 + 46, y1 + 150, "A", size=11, bold=True, color=C_LINE))

    # Шина B (помаранчева)
    f.append(rect(x1 + 320, y1 + 95, 12, 100, fill="#fed7aa", stroke=C_SYST, sw=1.2))
    for i in range(4):
        f.append(rect(x1 + 72, y1 + 117 + i * 24, 248, 8, fill="#fed7aa", stroke=C_SYST, sw=1.2))
    f.append(text(x1 + 326, y1 + 150, "B", size=11, bold=True, color=C_SYST))

    # Дефект замикання
    f.append(circle(x1 + 180, y1 + 121, 9, fill="#fee2e2", stroke=C_RANDOM, sw=1.5))
    f.append(text(x1 + 180, y1 + 125, "×", size=11, bold=True, color=C_RANDOM))
    f.append(text(x1 + w1 / 2, y1 + 205, "Струм витоку між шинами A-B фіксує мікрозамикання", size=9.5, color=C_RANDOM, bold=True))

    # Рисунок ланцюжка перехідних отворів (Via Chain)
    f.append(rect(x1 + 20, y1 + 235, w1 - 40, 160, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x1 + w1 / 2, y1 + 255, "Ланцюжок переходів (Via Chain, 1–10 млн отворів)", size=11, bold=True))

    # Метал 1 (знизу) та Метал 2 (зверху)
    for i in range(5):
        # M1 (нижній шар)
        f.append(rect(x1 + 50 + i * 60, y1 + 305, 45, 8, fill="#94a3b8", stroke=LINE, sw=1.0))
        # M2 (верхній шар)
        if i < 4:
            f.append(rect(x1 + 80 + i * 60, y1 + 280, 45, 8, fill="#cbd5e1", stroke=LINE, sw=1.0))
        # Vias (вертикальні контакти)
        f.append(rect(x1 + 85 + i * 60, y1 + 288, 10, 17, fill="#fef08a", stroke=LINE, sw=1.0))
        if i < 4:
            f.append(rect(x1 + 115 + i * 60, y1 + 288, 10, 17, fill="#fef08a", stroke=LINE, sw=1.0))

    # Дефект обриву переходу
    f.append(circle(x1 + 205, y1 + 296, 8, fill="#fee2e2", stroke=C_RANDOM, sw=1.5))
    f.append(text(x1 + 205, y1 + 300, "×", size=10, bold=True, color=C_RANDOM))
    f.append(text(x1 + w1 / 2, y1 + 345, "Високий опір або розрив виявляє дефекти травлення отворів", size=9.5, color=MUTED))
    f.append(text(x1 + w1 / 2, y1 + 375, "Розміщення: на смугах розпилу (Scribe Line) між чипами", size=9.5, bold=True, color=INK))


    # Права частина: SRAM Yield Vehicle (Адресована карта збійної пам'яті)
    x2 = x1 + w1 + 20
    f.append(rect(x2, y1, w1, h1, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x2 + w1 / 2, y1 + 25, "SRAM Yield Vehicle (Матрична локалізація)", size=12, bold=True))
    f.append(text(x2 + w1 / 2, y1 + 42, "Миттєве визначення дефектного шару за сигнатурою збою", size=10, color=MUTED))

    # Блок бітової карти (Bitmap)
    f.append(rect(x2 + 20, y1 + 60, w1 - 40, 230, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(x2 + w1 / 2, y1 + 80, "Топологічна бітова карта (SRAM Bit-Map)", size=11, bold=True))

    # Сітка комірок SRAM 8x8
    gx0, gy0, cell_s = x2 + 50, y1 + 95, 18
    for r in range(8):
        for c in range(8):
            f.append(rect(gx0 + c * cell_s, gy0 + r * cell_s, cell_s - 2, cell_s - 2, fill="#f1f5f9", stroke="#cbd5e1", sw=0.8))

    # Дефект 1: Single bit fail (координати 1,2)
    f.append(rect(gx0 + 2 * cell_s, gy0 + 1 * cell_s, cell_s - 2, cell_s - 2, fill=C_RANDOM, stroke=C_RANDOM, sw=1.0))

    # Дефект 2: Row fail (Рядок 4)
    for c in range(8):
        f.append(rect(gx0 + c * cell_s, gy0 + 4 * cell_s, cell_s - 2, cell_s - 2, fill=C_SYST, stroke=C_SYST, sw=1.0))

    # Дефект 3: Column pair fail (Колонки 5,6)
    for r in range(8):
        if r != 4:
            f.append(rect(gx0 + 5 * cell_s, gy0 + r * cell_s, cell_s - 2, cell_s - 2, fill=C_PARAM, stroke=C_PARAM, sw=1.0))
            f.append(rect(gx0 + 6 * cell_s, gy0 + r * cell_s, cell_s - 2, cell_s - 2, fill=C_PARAM, stroke=C_PARAM, sw=1.0))

    # Підписи типів сигнатур праворуч від сітки
    f.append(circle(x2 + 220, y1 + 108, 6, fill=C_RANDOM, stroke=C_RANDOM, sw=1.0))
    f.append(text(x2 + 232, y1 + 112, "Single Bit: точковий пробій", size=9.5, anchor="start", bold=True))

    f.append(circle(x2 + 220, y1 + 145, 6, fill=C_SYST, stroke=C_SYST, sw=1.0))
    f.append(text(x2 + 232, y1 + 149, "Row Fail: обрив Wordline", size=9.5, anchor="start", bold=True))

    f.append(circle(x2 + 220, y1 + 185, 6, fill=C_PARAM, stroke=C_PARAM, sw=1.0))
    f.append(text(x2 + 232, y1 + 189, "Col Pair: замикання Bitline", size=9.5, anchor="start", bold=True))

    f.append(text(x2 + w1 / 2, y1 + 265, "Адреса (X,Y) дає точні фізичні нанокоординати дефекту", size=10, bold=True, color=INK))

    # Нижній блок переваг SRAM
    f.append(rect(x2 + 20, y1 + 305, w1 - 40, 90, fill="#ecfdf5", stroke=C_TOTAL, sw=1.2, rx=6))
    f.append(text(x2 + w1 / 2, y1 + 328, "Чому саме SRAM використовують як тестовий чип:", size=10.5, bold=True, color=C_TOTAL))
    f.append(text(x2 + 30, y1 + 348, "• Найвища щільність транзисторів і найжорсткіший крок ліній", size=9.5, anchor="start", color=INK))
    f.append(text(x2 + 30, y1 + 366, "• Тестування за мілісекунди без складних ланцюгів Scan/ATPG", size=9.5, anchor="start", color=INK))
    f.append(text(x2 + 30, y1 + 384, "• Пряма кореляція з виходом майбутніх процесорних ядер", size=9.5, anchor="start", color=INK))

    render(os.path.join(IMG, 'test-structures-sram-comb.svg'), W, H, *f)


# ── Фігура 4: Конвеєр фізичного аналізу відмов (Failure Analysis Pipeline) ───
def fig_failure_analysis_flow():
    W, H = 860, 480
    f = [text(W / 2, 28, "Маршрут фізичного аналізу відмов (Physical Failure Analysis)", size=15, bold=True)]

    # 4 послідовні етапи аналізу відмов
    stages = [
        ("1. Електричний тест", "ATE & BIST", "Виявлення бракованого чипа, збереження бітової карти та тестових векторів", "#eaf0fd", C_LINE),
        ("2. Лазерна локалізація", "OBIRCH / EMMI", "Сканування ІЧ-лазером, фіксація термічних змін опору та фотовипромінювання", "#fef3c7", C_SYST),
        ("3. Іонне препарування", "FIB (Dual-Beam)", "Вирізання нанотраншеї та вилучення ультратонкої пластинки (ламелі)", "#fce8e6", C_RANDOM),
        ("4. Атомний аналіз", "TEM & EDX", "Просвічувальна мікроскопія та спектрометрія хімічного складу частинки", "#ecfdf5", C_TOTAL)
    ]

    box_w, box_h = 185, 290
    spacing = 28
    start_x = (W - (4 * box_w + 3 * spacing)) / 2
    top_y = 65

    for i, (title, tool, desc, fill_col, border_col) in enumerate(stages):
        bx = start_x + i * (box_w + spacing)
        f.append(rect(bx, top_y, box_w, box_h, fill=fill_col, stroke=border_col, sw=1.6, rx=8))

        # Заголовок етапу
        f.append(text(bx + box_w / 2, top_y + 24, title, size=11.5, bold=True, color=border_col))
        f.append(rect(bx + 15, top_y + 36, box_w - 30, 26, fill="#ffffff", stroke=border_col, sw=1.0, rx=4))
        f.append(text(bx + box_w / 2, top_y + 53, tool, size=11, bold=True, color=INK))

        # Ілюстрація для кожного кроку
        f.append(rect(bx + 15, top_y + 72, box_w - 30, 110, fill="#ffffff", stroke=C_BOX_LINE, sw=1.0, rx=4))

        if i == 0:
            # Зондова плата над чипом
            f.append(rect(bx + 35, top_y + 90, 85, 55, fill="#cbd5e1", stroke=LINE, sw=1.0))
            f.append(text(bx + box_w / 2, top_y + 115, "IC під тестом", size=9.5, bold=True))
            # Голки зонда
            f.append(line(bx + 45, top_y + 80, bx + 55, top_y + 90, color=POS, sw=1.5))
            f.append(line(bx + 110, top_y + 80, bx + 100, top_y + 90, color=POS, sw=1.5))
            f.append(text(bx + box_w / 2, top_y + 165, "Логічний FAIL", size=10, bold=True, color=POS))
        elif i == 1:
            # Лазерний промінь на кремній
            f.append(rect(bx + 35, top_y + 120, 85, 30, fill="#cbd5e1", stroke=LINE, sw=1.0))
            # Промінь лазера
            f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#fef08a" opacity="0.6"/>' %
                     (bx + box_w/2, top_y + 82, bx + box_w/2 - 18, top_y + 120, bx + box_w/2 + 18, top_y + 120))
            f.append(line(bx + box_w/2, top_y + 80, bx + box_w/2, top_y + 120, color=C_SYST, sw=1.8))
            f.append(circle(bx + box_w/2, top_y + 125, 6, fill=POS, stroke="#ffffff", sw=1.0))
            f.append(text(bx + box_w / 2, top_y + 165, "Гаряча точка (Hotspot)", size=9.5, bold=True, color=C_SYST))
        elif i == 2:
            # FIB іонний пучок вирізає ламель
            f.append(rect(bx + 30, top_y + 105, 95, 45, fill="#94a3b8", stroke=LINE, sw=1.0))
            # Виріз (траншея)
            f.append(rect(bx + 62, top_y + 105, 30, 25, fill="#ffffff", stroke=C_RANDOM, sw=1.2))
            # Ламель
            f.append(line(bx + 77, top_y + 108, bx + 77, top_y + 125, color=POS, sw=2.5))
            # Іонний пучок Ga+
            f.append(arrow(bx + box_w/2 + 25, top_y + 82, bx + 85, top_y + 110, color=C_RANDOM, sw=1.5))
            f.append(text(bx + box_w / 2, top_y + 165, "Ламель <50 нм", size=10, bold=True, color=C_RANDOM))
        elif i == 3:
            # TEM дифракція / атомна решітка
            f.append(rect(bx + 35, top_y + 85, 85, 60, fill="#0f172a", stroke=LINE, sw=1.0))
            for r in range(4):
                for c in range(5):
                    f.append(circle(bx + 48 + c * 15, top_y + 97 + r * 12, 2.5, fill="#38bdf8", stroke="none"))
            # Дефект у решітці
            f.append(circle(bx + 48 + 2 * 15, top_y + 97 + 1 * 12, 4.5, fill=POS, stroke="#ffffff", sw=1.0))
            f.append(text(bx + box_w / 2, top_y + 165, "Атомна структура", size=10, bold=True, color=C_TOTAL))

        # Опис під малюнком
        f.append(mtext(bx + box_w / 2, top_y + 195, desc, size=9.5, color=MUTED, lh=1.25))

        # Стрілка переходу до наступного етапу
        if i < 3:
            ax1 = bx + box_w + 4
            ax2 = ax1 + spacing - 8
            ay = top_y + box_h / 2
            f.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=2.0))

    # Нижній банер результату аналізу
    f.append(rect(start_x, top_y + box_h + 20, 4 * box_w + 3 * spacing, 75, fill=C_BOX_BG, stroke=C_BOX_LINE, sw=1.2, rx=6))
    f.append(text(W / 2, top_y + box_h + 44, "Кінцевий результат PFA: Встановлення першопричини (Root Cause)", size=12, bold=True, color=INK))
    f.append(text(W / 2, top_y + box_h + 65, "Приклад: «Залишок хлору після травлення металу 3 викликав корозію бар'єрного шару TiN у камері №4»", size=10, color=C_RANDOM, bold=True))
    f.append(text(W / 2, top_y + box_h + 82, "→ Інженери корегують рецепт промивки та оновлюють DFM-правила, ліквідуючи джерело дефектів", size=9.5, color=MUTED))

    render(os.path.join(IMG, 'failure-analysis-flow.svg'), W, H, *f)


if __name__ == '__main__':
    print("Генерація SVG-фігур для yield-ramp...")
    fig_yield_ramp_curve()
    fig_random_vs_systematic_defects()
    fig_test_structures_sram_comb()
    fig_failure_analysis_flow()
    print("Усі фігури успішно згенеровано.")
