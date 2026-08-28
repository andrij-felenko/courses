# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. verification-tiers: три рівні верифікації висновків моделі ─────────────
def fig_verification_tiers():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 28, "Трирівнева ієрархія валідації гіпотез нейромережі", size=15, color=INK, bold=True))

    # Вхідний блок: Нейромережа (Гіпотеза)
    p.append(rect(25, 55, 205, 330, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(127, 84, "Джерело гіпотези", size=12.5, color=NEG, bold=True))
    p.append(text(127, 104, "Нейромережевий детектор", size=10, color=MUTED, italic=True))

    p.append(rect(40, 122, 175, 75, fill=BG, stroke=LINE, sw=1.2, rx=5))
    p.append(text(127, 144, "Вихід детектора:", size=10.5, color=INK, bold=True))
    p.append(text(127, 164, "• Bounding box (u, v, w, h)", size=9.5, color=INK))
    p.append(text(127, 182, "• Клас: «Людина»", size=9.5, color=INK))

    p.append(rect(40, 207, 175, 75, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=5))
    p.append(text(127, 230, "Впевненість (Score):", size=10.5, color=AMBERTX, bold=True))
    p.append(text(127, 250, "P(class) = 0.96", size=12, color=POS, bold=True))
    p.append(text(127, 268, "Статистична оцінка", size=9.5, color=MUTED, italic=True))

    p.append(rect(40, 292, 175, 75, fill=REDBG, stroke=POS, sw=1.2, rx=5))
    p.append(text(127, 314, "Вразливість:", size=10.5, color=POS, bold=True))
    p.append(text(127, 334, "Відблиски, текстури,", size=9.5, color=INK))
    p.append(text(127, 350, "галюцинації фону", size=9.5, color=INK))

    # Стрілка від детектора до фільтрів
    p.append(arrow(230, 220, 255, 220, color=NEG, sw=2))

    # 3 Рівні фільтрації праворуч
    tiers = [
        ("РІВЕНЬ 1: Сенсорний крос-чекінг",
         "Зіставлення з ToF / лідаром / радаром / ультразвуком",
         "Перевірка відбиття сигналу у конусі виявленого об'єкта\n"
         "Захист від малюнків, тіней та відблисків сонця",
         BLUEBG, NEG),
        ("РІВЕНЬ 2: Геометричні інваріанти",
         "Проєкційна модель камери та зв'язок розміру з дистанцією",
         "Перевірка: h_px = (f_px · H_real) / Z (кутовий розмір)\n"
         "Захист від неможливих масштабувань (2 м у 5 px на 3 м)",
         AMBERBG, AMBER),
        ("РІВЕНЬ 3: Кінематичні обмеження",
         "Закони Ньютона та еліпсоїд допустимого переміщення (Строб)",
         "Перевірка: |v| ≤ v_max, |a| ≤ a_max між кадрами\n"
         "Захист від миттєвої появи та стрибків трекера",
         GREENBG, FIELD)
    ]

    for i, (head_t, sub_t, desc_t, bg_c, str_c) in enumerate(tiers):
        ty = 55 + i * 110
        tagcol = AMBERTX if str_c == AMBER else str_c
        p.append(rect(260, ty, 440, 100, fill=bg_c, stroke=str_c, sw=1.6, rx=7))
        p.append(text(275, ty + 24, head_t, size=11.5, color=tagcol, bold=True, anchor="start"))
        p.append(text(275, ty + 42, sub_t, size=10, color=MUTED, italic=True, anchor="start"))
        
        lines = desc_t.split("\n")
        p.append(text(275, ty + 64, lines[0], size=9.5, color=INK, anchor="start"))
        p.append(text(275, ty + 82, lines[1], size=9.5, color=INK, anchor="start"))

        # Стрілка виходу з кожного рівня
        p.append(arrow(700, ty + 50, 725, ty + 50, color=str_c, sw=1.8))

    # Фінальний блок: Арбітр рішень
    p.append(rect(730, 55, 125, 330, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(text(792, 90, "Арбітраж", size=12.5, color=INK, bold=True))
    p.append(text(792, 110, "рішення", size=12.5, color=INK, bold=True))

    p.append(rect(740, 135, 105, 55, fill=GREENBG, stroke=FIELD, sw=1.4, rx=4))
    p.append(text(792, 158, "ПІДТВЕРДЖЕНО", size=9.5, color=FIELD, bold=True))
    p.append(text(792, 175, "Дія автопілота", size=9.5, color=INK))

    p.append(rect(740, 205, 105, 65, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=4))
    p.append(text(792, 226, "СУМНІВ", size=9.5, color=AMBERTX, bold=True))
    p.append(text(792, 243, "Сповільнення,", size=9.5, color=INK))
    p.append(text(792, 258, "набір кадрів", size=9.5, color=INK))

    p.append(rect(740, 285, 105, 55, fill=REDBG, stroke=POS, sw=1.4, rx=4))
    p.append(text(792, 308, "ВІДХИЛЕНО", size=9.5, color=POS, bold=True))
    p.append(text(792, 325, "Галюцинація ML", size=9.5, color=INK))

    p.append(text(W / 2, 415, "Модель машинного навчання лише генерує гіпотезу, а фізичні інваріанти виносять остаточний вердикт", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "verification-tiers.svg"), W, H, *p,
           title="Трирівнева ієрархія валідації гіпотез нейромережі")


# ── 2. sensor-cross-check: просторове зіставлення камери та ToF/радара ────────
def fig_sensor_cross_check():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 28, "Сенсорний крос-чекінг: просторове зіставлення конуса камери та давача відстані", size=14.5, color=INK, bold=True))

    # Лівий блок: Камера та 2D детекція
    p.append(rect(25, 55, 230, 295, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(140, 84, "Оптична камера (2D)", size=12.5, color=NEG, bold=True))
    p.append(text(140, 104, "Пасивне матричне зображення", size=10, color=MUTED, italic=True))

    # Ескіз кадру
    p.append(rect(45, 120, 190, 130, fill=BG, stroke=LINE, sw=1.4, rx=4))
    # Bounding box на кадрі
    p.append(rect(85, 145, 80, 85, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=2))
    p.append(text(125, 138, "bbox: [u, v, w, h]", size=9.5, color=AMBERTX, bold=True))
    p.append(text(125, 185, "Перешкода?", size=10, color=INK))
    p.append(text(125, 202, "Score: 0.94", size=10, color=POS, bold=True))

    p.append(rect(40, 265, 200, 65, fill=BG, stroke=NEG, sw=1.2, rx=5))
    p.append(text(140, 288, "Невизначеність глибини (Z):", size=10, color=NEG, bold=True))
    p.append(text(140, 310, "2D проєкція втрачає дальність!", size=9.5, color=POS, bold=True))

    # Центральний блок: Геометричне променеве перекриття
    p.append(rect(275, 55, 290, 295, fill=BG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(420, 84, "Просторове перекриття", size=12.5, color=INK, bold=True))
    p.append(text(420, 104, "Спільне поле зору (FOV)", size=10, color=MUTED, italic=True))

    # Сенсорна платформа
    p.append(rect(295, 180, 45, 50, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    p.append(text(317, 202, "Кам.", size=9.5, color=NEG, bold=True))
    p.append(text(317, 218, "ToF", size=9.5, color=FIELD, bold=True))

    # Оптичний конус зору
    p.append(line(340, 195, 545, 135, color=NEG, sw=1.5, dash="4,3"))
    p.append(line(340, 195, 545, 255, color=NEG, sw=1.5, dash="4,3"))
    p.append(text(510, 145, "FOV камери", size=9.5, color=NEG))

    # Промінь ToF / Лідара
    p.append(line(340, 215, 480, 215, color=FIELD, sw=2.5))
    p.append(circle(480, 215, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(440, 205, "Промінь ToF (Z = 3.2 м)", size=9.5, color=FIELD, bold=True))

    # Реальна перешкода у просторі
    p.append(rect(480, 175, 20, 70, fill=GREENBG, stroke=FIELD, sw=1.6, rx=3))
    p.append(text(525, 220, "Об'єкт у 3D", size=9.5, color=FIELD, bold=True))

    p.append(rect(290, 265, 260, 65, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(420, 288, "Трансформація координат:", size=10, color=INK, bold=True))
    p.append(text(420, 310, "P_cam = R · P_sensor + T", size=10.5, color=NEG, bold=True))

    # Правий блок: Результати крос-чекінгу
    p.append(rect(585, 55, 250, 295, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(710, 84, "Матриця узгодження", size=12.5, color=FIELD, bold=True))
    p.append(text(710, 104, "Порівняння двох каналів", size=10, color=MUTED, italic=True))

    cases = [
        ("Камера: ТАК | ToF: ТАК", "Об'єкт підтверджено фізично.\nВисока надійність рішення.", GREENBG, FIELD),
        ("Камера: ТАК | ToF: НІ", "Відблиск або малюнок.\nГалюцинація ВІДХИЛЯЄТЬСЯ.", REDBG, POS),
        ("Камера: НІ | ToF: ТАК", "Погана видимість / туман.\nГальмування за далекоміром!", AMBERBG, AMBERTX),
    ]

    for j, (c_head, c_desc, c_bg, c_str) in enumerate(cases):
        cy_box = 120 + j * 72
        p.append(rect(597, cy_box, 226, 64, fill=c_bg, stroke=c_str, sw=1.2, rx=5))
        p.append(text(610, cy_box + 20, c_head, size=9.5, color=c_str, bold=True, anchor="start"))
        lines_c = c_desc.split("\n")
        p.append(text(610, cy_box + 38, lines_c[0], size=9.5, color=INK, anchor="start"))
        p.append(text(610, cy_box + 54, lines_c[1], size=9.5, color=INK, anchor="start"))

    p.append(text(W / 2, 375, "Фізична диверсифікація давачів нейтралізує некорельовані моди відмов оптичних та активних каналів", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "sensor-cross-check.svg"), W, H, *p,
           title="Сенсорний крос-чекінг: просторове зіставлення конуса камери та давача відстані")


# ── 3. geometry-invariants: зв'язок розміру, фокусу та пікселів ───────────────
def fig_geometry_invariants():
    W, H = 860, 390
    p = []
    p.append(text(W / 2, 28, "Геометричний інваріант: проєкція фізичного розміру на площину сенсора", size=14.5, color=INK, bold=True))

    # Схема проєкції камери-обскури
    p.append(rect(25, 55, 490, 285, fill=BG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(270, 82, "Модель проєкції перспективи (Pinhole Model)", size=12.5, color=INK, bold=True))

    # Оптичний центр камери
    p.append(circle(70, 190, 6, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(70, 218, "Оптичний центр", size=9.5, color=NEG, bold=True))

    # Площина сенсора
    p.append(line(140, 120, 140, 260, color=LINE, sw=2))
    p.append(text(140, 110, "Сенсор камери", size=9.5, color=MUTED))
    p.append(line(70, 190, 140, 190, color=MUTED, sw=1, dash="3,2"))
    p.append(text(105, 182, "f_px", size=9.5, color=NEG, bold=True))

    # Проєкційний піксельний бокс h_px
    p.append(line(140, 160, 140, 220, color=POS, sw=3))
    p.append(text(165, 194, "h_px", size=10.5, color=POS, bold=True))

    # Промені перспективи до об'єкта
    p.append(line(70, 190, 440, 100, color=NEG, sw=1.5))
    p.append(line(70, 190, 440, 280, color=NEG, sw=1.5))

    # Фізичний об'єкт у просторі
    p.append(rect(435, 100, 12, 180, fill=GREENBG, stroke=FIELD, sw=2, rx=2))
    p.append(text(460, 190, "H_real (наприклад, 1.8 м)", size=10, color=FIELD, bold=True, anchor="start"))

    # Дистанція Z
    p.append(line(70, 300, 440, 300, color=INK, sw=1.5))
    p.append(line(70, 295, 70, 305, color=INK, sw=1.5))
    p.append(line(440, 295, 440, 305, color=INK, sw=1.5))
    p.append(text(255, 320, "Фізична дистанція: Z (метри)", size=10.5, color=INK, bold=True))

    # Права частина: Правила верифікації
    p.append(rect(535, 55, 300, 285, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(text(685, 82, "Критерій фізичної валідності", size=12.5, color=INK, bold=True))

    p.append(rect(550, 102, 270, 55, fill=BG, stroke=NEG, sw=1.4, rx=5))
    p.append(text(685, 122, "Формула інваріанта:", size=10, color=INK, bold=True))
    p.append(text(685, 142, "h_px = (f_px · H_real) / Z", size=11.5, color=NEG, bold=True))

    # Приклад аномалії
    p.append(rect(550, 167, 270, 75, fill=REDBG, stroke=POS, sw=1.4, rx=5))
    p.append(text(560, 187, "Приклад аномалії:", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(560, 204, "• Клас: «Людина» (H = 1.8 м)", size=9.5, color=INK, anchor="start"))
    p.append(text(560, 220, "• Дальність: Z = 3.0 м", size=9.5, color=INK, anchor="start"))
    p.append(text(560, 235, "• Очікувано: h ≈ 360 px | Детектор: 6 px!", size=9.5, color=POS, bold=True, anchor="start"))

    p.append(rect(550, 252, 270, 75, fill=GREENBG, stroke=FIELD, sw=1.4, rx=5))
    p.append(text(560, 272, "Дія верифікатора:", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(560, 290, "Помилка масштабу > 5000% →", size=9.5, color=INK, anchor="start"))
    p.append(text(560, 307, "МИТТЄВЕ ВІДКИДАННЯ ГІПОТЕЗИ", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(560, 321, "як геометричного абсурду", size=9.5, color=MUTED, italic=True, anchor="start"))

    p.append(text(W / 2, 365, "Закони оптики встановлюють жорстку залежність між піксельним розміром і фізичною дистанцією", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "geometry-invariants.svg"), W, H, *p,
           title="Геометричний інваріант: проєкція фізичного розміру на площину сенсора")


# ── 4. kinematic-gating: кінематичний строб та фільтр Ньютона ────────────────
def fig_kinematic_gating():
    W, H = 860, 390
    p = []
    p.append(text(W / 2, 28, "Кінематичний строб: перевірка фізичної допустимості переміщення між кадрами", size=14.5, color=INK, bold=True))

    # Схема простору руху (площина X-Y або зображення)
    p.append(rect(25, 55, 470, 285, fill=BG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(260, 82, "Еліпсоїд допустимого переміщення (Validation Gate)", size=12, color=INK, bold=True))

    # Попередня позиція об'єкта в кадрі t-1
    p.append(circle(140, 190, 14, fill=BLUEBG, stroke=NEG, sw=2))
    p.append(text(140, 195, "t-1", size=9.5, color=NEG, bold=True))
    p.append(text(140, 222, "Позиція P(t-1)", size=9.5, color=NEG))

    # Вектор передбаченої швидкості
    p.append(arrow(140, 190, 260, 160, color=MUTED, sw=1.6))
    p.append(text(205, 165, "v · Δt", size=9.5, color=MUTED, italic=True))

    # Очікувана позиція в кадрі t
    p.append(circle(260, 160, 9, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(260, 140, "Очікувана P_pred(t)", size=9.5, color=INK))

    # Еліпс стробу (допустима зона за прискоренням a_max)
    p.append('<ellipse cx="260.0" cy="160.0" rx="75.0" ry="50.0" fill="%s" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (GREENBG, FIELD))
    p.append(text(260, 185, "Строб валідації (d_M ≤ γ)", size=9.5, color=FIELD, bold=True))

    # Реальне вимірювання 1: Всередині стробу (OK)
    p.append(circle(285, 170, 8, fill=GREENBG, stroke=FIELD, sw=2))
    p.append(text(312, 174, "Детекція А (OK)", size=9.5, color=FIELD, bold=True, anchor="start"))

    # Реальне вимірювання 2: Зовні стробу (Галюцинація / Стрибок)
    p.append(circle(405, 95, 8, fill=REDBG, stroke=POS, sw=2))
    p.append(text(420, 98, "Детекція Б (Аномалія)", size=9.5, color=POS, bold=True, anchor="start"))
    p.append(line(140, 190, 405, 95, color=POS, sw=1.2, dash="3,3"))
    p.append(text(325, 115, "a > 800 м/с²!", size=9.5, color=POS, bold=True))

    # Права частина: Фізичні обмеження
    p.append(rect(515, 55, 320, 285, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(text(675, 82, "Кінематичні інваріанти", size=12.5, color=INK, bold=True))

    items = [
        ("Обмеження швидкості:",
         "• |ΔP / Δt| ≤ v_max (класова межа)\n• Захист від надшвидкісних стрибків", BLUEBG, NEG),
        ("Обмеження прискорення:",
         "• |Δv / Δt| ≤ a_max (інерція маси)\n• Поява з нізвідки дає a = ∞", AMBERBG, AMBERTX),
        ("Дистанція Махаланобіса:",
         "• d_M² = (z - ẑ)ᵀ · S⁻¹ · (z - ẑ) ≤ γ\n• Відсікає перескоки між цілями", GREENBG, FIELD),
    ]

    for k, (i_head, i_desc, i_bg, i_col) in enumerate(items):
        iy = 100 + k * 76
        p.append(rect(530, iy, 290, 68, fill=i_bg, stroke=i_col, sw=1.2, rx=5))
        p.append(text(540, iy + 19, i_head, size=10, color=i_col, bold=True, anchor="start"))
        lines_i = i_desc.split("\n")
        p.append(text(540, iy + 37, lines_i[0], size=9.5, color=INK, anchor="start"))
        p.append(text(540, iy + 52, lines_i[1], size=9.5, color=INK, anchor="start"))

    p.append(text(W / 2, 365, "Тверді тіла мають масу: будь-яке виявлення з нефізичним прискоренням є оптичним артефактом", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "kinematic-gating.svg"), W, H, *p,
           title="Кінематичний строб: перевірка фізичної допустимості переміщення між кадрами")


# ── 5. arbitration-fsm: автомат станів арбітражу та злиття ────────────────────
def fig_arbitration_fsm():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 28, "Скінченний автомат арбітражу треків: життєвий цикл перешкоди", size=14.5, color=INK, bold=True))

    # Стан 1: TENTATIVE (Кандидат)
    p.append(rect(35, 140, 155, 95, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(112, 168, "TENTATIVE", size=11.5, color=NEG, bold=True))
    p.append(text(112, 188, "Нова гіпотеза ML", size=9.5, color=MUTED, italic=True))
    p.append(text(112, 210, "Лічильник: 1 / N", size=10, color=INK, bold=True))

    # Стан 2: VALIDATING (Перевірка інваріантів)
    p.append(rect(240, 140, 175, 95, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(327, 168, "VALIDATING", size=11.5, color=AMBERTX, bold=True))
    p.append(text(327, 188, "Геометрія + Давач", size=9.5, color=MUTED, italic=True))
    p.append(text(327, 210, "Крос-чекінг інваріантів", size=9.5, color=INK))

    # Стан 3: CONFIRMED (Підтверджена перешкода)
    p.append(rect(465, 140, 175, 95, fill=GREENBG, stroke=FIELD, sw=2, rx=8))
    p.append(text(552, 168, "CONFIRMED", size=11.5, color=FIELD, bold=True))
    p.append(text(552, 188, "Активна ціль", size=9.5, color=MUTED, italic=True))
    p.append(text(552, 210, "Керує обходом / стопом", size=9.5, color=FIELD, bold=True))

    # Стан 4: COASTING (Екстраполяція при пропусках)
    p.append(rect(680, 140, 145, 95, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
    p.append(text(752, 168, "COASTING", size=11.5, color=MUTED, bold=True))
    p.append(text(752, 188, "Тимчасовий пропуск", size=9.5, color=MUTED, italic=True))
    p.append(text(752, 210, "Прогноз за фільтром", size=9.5, color=INK))

    # Стан 5: REJECTED / DROPPED (Знищено / Відхилено) - внизу
    p.append(rect(340, 290, 195, 55, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(437, 314, "DROPPED / REJECTED", size=11.5, color=POS, bold=True))
    p.append(text(437, 332, "Галюцинація або зникнення", size=9.5, color=MUTED, italic=True))

    # Стрілки переходів
    # TENTATIVE -> VALIDATING
    p.append(arrow(190, 187, 240, 187, color=NEG, sw=1.8))
    p.append(text(215, 177, "N=2", size=9.5, color=NEG, bold=True))

    # VALIDATING -> CONFIRMED
    p.append(arrow(415, 187, 465, 187, color=FIELD, sw=2))
    p.append(text(440, 177, "M з N + Інв.", size=9.5, color=FIELD, bold=True))

    # CONFIRMED -> COASTING
    p.append(arrow(640, 170, 680, 170, color=MUTED, sw=1.6))
    p.append(text(660, 158, "Пропуск", size=9.5, color=MUTED))

    # COASTING -> CONFIRMED (повернення)
    p.append(arrow(680, 205, 640, 205, color=FIELD, sw=1.6))
    p.append(text(660, 222, "Знову є", size=9.5, color=FIELD))

    # Переходи в DROPPED
    # TENTATIVE -> DROPPED (одноразовий шум)
    p.append(arrow(112, 235, 340, 305, color=POS, sw=1.4))
    p.append(text(205, 280, "Поодинокий шум", size=9.5, color=POS))

    # VALIDATING -> DROPPED (порушення інваріантів)
    p.append(arrow(327, 235, 410, 290, color=POS, sw=1.6))
    p.append(text(395, 260, "Порушення фізики", size=9.5, color=POS, bold=True))

    # COASTING -> DROPPED (таймаут втрати)
    p.append(arrow(752, 235, 535, 305, color=POS, sw=1.4))
    p.append(text(670, 280, "Таймаут (t > T_max)", size=9.5, color=POS))

    # Верхній заголовок правил
    p.append(rect(35, 55, 790, 60, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(W / 2, 78, "Правило безпеки арбітра: жоден одиничний сплеск нейромережі не потрапляє у виконавчий контур", size=10.5, color=INK, bold=True))
    p.append(text(W / 2, 98, "Підтвердження вимагає просторово-часової стабільності та відповідності законам фізики", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "arbitration-fsm.svg"), W, H, *p,
           title="Скінченний автомат арбітражу треків: життєвий цикл перешкоди")


def main():
    fig_verification_tiers()
    fig_sensor_cross_check()
    fig_geometry_invariants()
    fig_kinematic_gating()
    fig_arbitration_fsm()
    print("Усі 5 фігур успішно згенеровано.")

if __name__ == "__main__":
    main()
