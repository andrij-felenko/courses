# -*- coding: utf-8 -*-
"""Фігури до теми «Power gating і clock gating» та її вставок.
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Спеціальна палітра для схемотехніки керування живленням
C_CLK   = "#2457d6"   # синій для тактового сигналу
C_PWR   = "#c0392b"   # червоний для живлення VDD
C_GND   = "#27ae60"   # зелений для землі GND
C_CTRL  = "#8b5cf6"   # фіолетовий для сигналів керування (Enable, Sleep, Iso, Save)
C_AON   = "#d97706"   # бурштиновий для Always-On блоків і шин
C_GATE  = "#0284c7"   # блакитний для стробованого такту
C_OFF   = "#9ca3af"   # сірий для вимкненого домену
C_BOX   = "#f8fafc"   # фонова заливка блоків


# ── d-фіг.1: Стробування тактового сигналу (Naive AND vs Latch-based ICG) ────
def fig_icg_latch_timing():
    W, H = 780, 480
    f = [text(W / 2, 24, "Стробування тактового сигналу: проблема хибних імпульсів та комірка ICG",
              size=14, bold=True)]

    # Ліва колонка: Наївне стробування (AND gate) з глітчем
    f.append(rect(30, 45, 345, 415, fill=C_BOX, stroke=POS, sw=1.5, rx=6))
    f.append(text(202, 68, "Наївне стробування: елемент 2-AND", size=12, color=POS, bold=True))
    f.append(text(202, 85, "Поява хибного імпульсу (Glitch) при асинхронному Enable", size=9.5, color=MUTED))

    # Схема AND
    f.append(rect(145, 105, 75, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(182, 132, "&", size=18, bold=True))
    # Вхід CLK
    f.append(line(70, 118, 145, 118, color=C_CLK, sw=2))
    f.append(text(65, 122, "CLK", size=10, color=C_CLK, bold=True, anchor="end"))
    # Вхід EN
    f.append(line(70, 138, 145, 138, color=C_CTRL, sw=2))
    f.append(text(65, 142, "EN", size=10, color=C_CTRL, bold=True, anchor="end"))
    # Вихід GCLK
    f.append(line(220, 128, 295, 128, color=POS, sw=2))
    f.append(text(300, 132, "GCLK", size=10, color=POS, bold=True, anchor="start"))

    # Часова діаграма для AND
    t_y0 = 175
    # Лінії сітки
    for tx in [100, 150, 200, 250, 300, 350]:
        f.append(line(tx, t_y0, tx, t_y0 + 265, color="#e5e7eb", sw=1, dash="3,3"))

    # CLK сигнал
    f.append(text(90, t_y0 + 25, "CLK", size=10, color=C_CLK, bold=True, anchor="end"))
    clk_path = (f"M 100,{t_y0+35} L 125,{t_y0+35} L 125,{t_y0+10} L 150,{t_y0+10} "
                f"L 175,{t_y0+35} L 175,{t_y0+10} L 200,{t_y0+10} "
                f"L 225,{t_y0+35} L 225,{t_y0+10} L 250,{t_y0+10} "
                f"L 275,{t_y0+35} L 275,{t_y0+10} L 300,{t_y0+10} "
                f"L 325,{t_y0+35} L 325,{t_y0+10} L 350,{t_y0+10}")
    f.append(f'<path d="{clk_path}" fill="none" stroke="{C_CLK}" stroke-width="2"/>')

    # EN сигнал (перемикається під час високого CLK)
    f.append(text(90, t_y0 + 95, "EN", size=10, color=C_CTRL, bold=True, anchor="end"))
    en_path = f"M 100,{t_y0+105} L 185,{t_y0+105} L 190,{t_y0+80} L 350,{t_y0+80}"
    f.append(f'<path d="{en_path}" fill="none" stroke="{C_CTRL}" stroke-width="2"/>')

    # GCLK сигнал з глітчем
    f.append(text(90, t_y0 + 170, "GCLK", size=10, color=POS, bold=True, anchor="end"))
    gclk_path = (f"M 100,{t_y0+180} L 185,{t_y0+180} L 190,{t_y0+155} L 200,{t_y0+180} "
                 f"L 225,{t_y0+180} L 225,{t_y0+155} L 250,{t_y0+180} "
                 f"L 275,{t_y0+180} L 275,{t_y0+155} L 300,{t_y0+180} "
                 f"L 325,{t_y0+180} L 325,{t_y0+155} L 350,{t_y0+180}")
    f.append(f'<path d="{gclk_path}" fill="none" stroke="{POS}" stroke-width="2"/>')

    # Виділення глітча
    f.append(rect(182, t_y0 + 150, 24, 35, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
    f.append(text(194, t_y0 + 205, "Глітч!", size=10, color=POS, bold=True))
    f.append(text(194, t_y0 + 220, "Неповний імпульс", size=9, color=POS))
    f.append(text(194, t_y0 + 233, "→ збій тригерів", size=9, color=POS))


    # Права колонка: Інтегрована комірка ICG (Latch + AND)
    f.append(rect(405, 45, 345, 415, fill=C_BOX, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(577, 68, "Безпечна комірка ICG: Защіпка (Latch) + AND", size=12, color=FIELD, bold=True))
    f.append(text(577, 85, "Блокування зміни EN під час високого рівня CLK", size=9.5, color=MUTED))

    # Схема ICG (Latch + AND)
    # Контур комірки ICG
    f.append(rect(435, 100, 285, 58, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(445, 114, "ICG Cell", size=9, color=FIELD, bold=True, anchor="start"))

    # Latch (прозорий при низькому CLK)
    f.append(rect(480, 106, 65, 44, fill="#f0fdf4", stroke=LINE, sw=1.3, rx=3))
    f.append(text(512, 124, "LATCH", size=9.5, bold=True))
    f.append(text(512, 138, "Active-Low", size=9, color=MUTED))
    f.append(circle(480, 138, 3, fill="#ffffff", stroke=LINE, sw=1.2)) # інверсія на тактовому вході

    # AND gate
    f.append(rect(595, 106, 50, 44, fill="#f0fdf4", stroke=LINE, sw=1.3, rx=3))
    f.append(text(620, 132, "&", size=16, bold=True))

    # Входи та з'єднання
    f.append(line(440, 118, 480, 118, color=C_CTRL, sw=1.8))
    f.append(text(435, 122, "EN", size=9.5, color=C_CTRL, bold=True, anchor="end"))

    f.append(line(440, 145, 460, 145, color=C_CLK, sw=1.8))
    f.append(line(460, 145, 460, 138, color=C_CLK, sw=1.8))
    f.append(line(460, 138, 477, 138, color=C_CLK, sw=1.8))
    f.append(line(460, 145, 575, 145, color=C_CLK, sw=1.8))
    f.append(line(575, 145, 575, 138, color=C_CLK, sw=1.8))
    f.append(line(575, 138, 595, 138, color=C_CLK, sw=1.8))
    f.append(circle(460, 145, 2.5, fill=C_CLK, stroke=C_CLK))
    f.append(text(435, 149, "CLK", size=9.5, color=C_CLK, bold=True, anchor="end"))

    f.append(line(545, 118, 595, 118, color=FIELD, sw=1.8))
    f.append(text(570, 113, "EN_lat", size=9, color=FIELD))

    f.append(line(645, 128, 700, 128, color=C_GATE, sw=2))
    f.append(text(705, 132, "GCLK", size=9.5, color=C_GATE, bold=True, anchor="start"))

    # Часова діаграма для ICG
    # CLK сигнал
    f.append(text(465, t_y0 + 25, "CLK", size=10, color=C_CLK, bold=True, anchor="end"))
    clk_path2 = (f"M 475,{t_y0+35} L 500,{t_y0+35} L 500,{t_y0+10} L 525,{t_y0+10} "
                 f"L 550,{t_y0+35} L 550,{t_y0+10} L 575,{t_y0+10} "
                 f"L 600,{t_y0+35} L 600,{t_y0+10} L 625,{t_y0+10} "
                 f"L 650,{t_y0+35} L 650,{t_y0+10} L 675,{t_y0+10} "
                 f"L 700,{t_y0+35} L 700,{t_y0+10} L 725,{t_y0+10}")
    f.append(f'<path d="{clk_path2}" fill="none" stroke="{C_CLK}" stroke-width="2"/>')

    # EN сигнал (перемикається асинхронно)
    f.append(text(465, t_y0 + 80, "EN", size=10, color=C_CTRL, bold=True, anchor="end"))
    en_path2 = f"M 475,{t_y0+90} L 560,{t_y0+90} L 565,{t_y0+65} L 725,{t_y0+65}"
    f.append(f'<path d="{en_path2}" fill="none" stroke="{C_CTRL}" stroke-width="2"/>')

    # EN_lat сигнал (защіплюється на наступному спаді CLK)
    f.append(text(465, t_y0 + 135, "EN_lat", size=10, color=FIELD, bold=True, anchor="end"))
    en_lat_path = f"M 475,{t_y0+145} L 600,{t_y0+145} L 600,{t_y0+120} L 725,{t_y0+120}"
    f.append(f'<path d="{en_lat_path}" fill="none" stroke="{FIELD}" stroke-width="2"/>')

    # GCLK сигнал (чистий, без глітчів)
    f.append(text(465, t_y0 + 190, "GCLK", size=10, color=C_GATE, bold=True, anchor="end"))
    gclk_path2 = (f"M 475,{t_y0+200} L 600,{t_y0+200} L 600,{t_y0+175} L 625,{t_y0+200} "
                  f"L 650,{t_y0+200} L 650,{t_y0+175} L 675,{t_y0+200} "
                  f"L 700,{t_y0+200} L 700,{t_y0+175} L 725,{t_y0+200}")
    f.append(f'<path d="{gclk_path2}" fill="none" stroke="{C_GATE}" stroke-width="2"/>')

    # Пояснення
    f.append(text(577, t_y0 + 230, "Чистий сигнал: перемикання EN відбувається", size=9.5, color=FIELD, bold=True))
    f.append(text(577, t_y0 + 245, "лише коли CLK = 0, усуваючи будь-які глітчі", size=9.5, color=MUTED))

    render(os.path.join(IMG, "icg-latch-timing.svg"), W, H, *f)


# ── d-фіг.2: Силові ключі (Header pMOS vs Footer nMOS) ────────────────────────
def fig_header_footer_switches():
    W, H = 780, 450
    f = [text(W / 2, 24, "Силові ключі Power Gating: конфігурації Header (pMOS) та Footer (nMOS)",
              size=14, bold=True)]

    # Ліва панель: Header pMOS switch
    f.append(rect(30, 45, 345, 385, fill=C_BOX, stroke=C_PWR, sw=1.5, rx=6))
    f.append(text(202, 68, "Header Switch (pMOS на шині VDD)", size=12, color=C_PWR, bold=True))
    f.append(text(202, 85, "Комутація позитивного живлення → збереження спільної GND", size=9.5, color=MUTED))

    # Схема Header
    # Реальна шина VDD
    f.append(line(70, 110, 335, 110, color=C_PWR, sw=3))
    f.append(text(65, 114, "VDD (Always-On)", size=10, color=C_PWR, bold=True, anchor="end"))

    # pMOS транзистор (Sleep Switch)
    f.append(rect(170, 130, 65, 45, fill="#ffffff", stroke=C_PWR, sw=1.5, rx=3))
    f.append(text(202, 150, "pMOS", size=10, color=C_PWR, bold=True))
    f.append(text(202, 165, "Header", size=9, color=MUTED))
    f.append(circle(170, 152, 3, fill="#ffffff", stroke=C_PWR, sw=1.2)) # інверсія затвора pMOS
    f.append(line(202, 110, 202, 130, color=C_PWR, sw=2)) # витік на VDD

    # Сигнал SLEEP_N
    f.append(line(90, 152, 167, 152, color=C_CTRL, sw=1.8))
    f.append(text(85, 156, "SLEEP_B", size=9.5, color=C_CTRL, bold=True, anchor="end"))

    # Віртуальна шина VDD_VIRTUAL
    f.append(line(202, 175, 202, 195, color=C_AON, sw=2.5))
    f.append(line(70, 195, 335, 195, color=C_AON, sw=2.5))
    f.append(text(275, 208, "VDD_VIRTUAL", size=9.5, color=C_AON, bold=True, anchor="start"))

    # Логічний блок у керованому домені (з'єднання з віртуальною шиною зліва від тексту)
    f.append(line(130, 195, 130, 225, color=C_AON, sw=2))
    f.append(line(202, 195, 202, 225, color=C_AON, sw=2))
    f.append(rect(100, 225, 205, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(202, 248, "Логічний блок (CMOS)", size=11, bold=True))
    f.append(text(202, 265, "Ядра CPU / GPU / Логіка", size=9.5, color=MUTED))
    f.append(text(202, 282, "Низькопорогові транзистори (LVT)", size=9, color=C_GATE))

    # З'єднання з реальною землею GND
    f.append(line(202, 305, 202, 335, color=C_GND, sw=2.5))
    f.append(line(70, 335, 335, 335, color=C_GND, sw=3))
    f.append(text(65, 339, "GND (Спільна земля)", size=10, color=C_GND, bold=True, anchor="end"))

    # Переваги та особливості
    f.append(rect(45, 355, 315, 60, fill="#fef2f2", stroke=C_PWR, sw=1, rx=3))
    f.append(text(202, 375, "✓ Чиста спільна земля, відсутність шуму субстрату", size=9.5, color=INK))
    f.append(text(202, 395, "✗ Менша рухливість дірок → більша площа ключа W/L", size=9.5, color=POS))


    # Права панель: Footer nMOS switch
    f.append(rect(405, 45, 345, 385, fill=C_BOX, stroke=C_GND, sw=1.5, rx=6))
    f.append(text(577, 68, "Footer Switch (nMOS на шині GND)", size=12, color=C_GND, bold=True))
    f.append(text(577, 85, "Комутація землі → менший опір Ron та менша площа", size=9.5, color=MUTED))

    # Схема Footer
    # Реальна шина VDD
    f.append(line(445, 110, 710, 110, color=C_PWR, sw=3))
    f.append(text(715, 114, "VDD (Always-On)", size=10, color=C_PWR, bold=True, anchor="start"))

    # Логічний блок
    f.append(rect(475, 135, 205, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(577, 158, "Логічний блок (CMOS)", size=11, bold=True))
    f.append(text(577, 175, "Ядра CPU / GPU / Логіка", size=9.5, color=MUTED))
    f.append(text(577, 192, "Низькопорогові транзистори (LVT)", size=9, color=C_GATE))
    f.append(line(577, 110, 577, 135, color=C_PWR, sw=2))

    # Віртуальна земля GND_VIRTUAL
    f.append(line(577, 215, 577, 235, color=C_AON, sw=2.5))
    f.append(line(445, 235, 710, 235, color=C_AON, sw=2.5))
    f.append(text(650, 248, "GND_VIRTUAL", size=9.5, color=C_AON, bold=True, anchor="start"))

    # nMOS транзистор (Sleep Switch)
    f.append(rect(545, 255, 65, 45, fill="#ffffff", stroke=C_GND, sw=1.5, rx=3))
    f.append(text(577, 275, "nMOS", size=10, color=C_GND, bold=True))
    f.append(text(577, 290, "Footer", size=9, color=MUTED))
    f.append(line(577, 235, 577, 255, color=C_AON, sw=2)) # стік на віртуальну землю

    # Сигнал SLEEP
    f.append(line(465, 277, 545, 277, color=C_CTRL, sw=1.8))
    f.append(text(460, 281, "SLEEP", size=9.5, color=C_CTRL, bold=True, anchor="end"))

    # Реальна земля GND
    f.append(line(577, 300, 577, 335, color=C_GND, sw=2.5))
    f.append(line(445, 335, 710, 335, color=C_GND, sw=3))
    f.append(text(715, 339, "GND (Спільна земля)", size=10, color=C_GND, bold=True, anchor="start"))

    # Переваги та особливості Footer
    f.append(rect(420, 355, 315, 60, fill="#f0fdf4", stroke=C_GND, sw=1, rx=3))
    f.append(text(577, 375, "✓ Висока рухливість електронів → менша площа (в 2–3 рази)", size=9.5, color=FIELD))
    f.append(text(577, 395, "✗ Плаваючий потенціал віртуальної GND → шум підкладки", size=9.5, color=POS))

    render(os.path.join(IMG, "header-footer-switches.svg"), W, H, *f)


# ── d-фіг.3: Комірка ізоляції (Isolation Cell) ────────────────────────────────
def fig_isolation_cell_mechanism():
    W, H = 780, 440
    f = [text(W / 2, 24, "Комірка ізоляції на межі доменів: усунення наскрізного струму (Crowbar)",
              size=14, bold=True)]

    # Верхня частина: Домени та ізоляція
    # Лівий домен: Вимкнений (Power-Gated Domain)
    f.append(rect(30, 48, 270, 225, fill="#f3f4f6", stroke=C_OFF, sw=1.5, rx=6))
    f.append(text(165, 70, "Вимкнений домен (Power-Gated)", size=11.5, color=MUTED, bold=True))
    f.append(text(165, 87, "VDD_SW = 0 В (живлення відключене)", size=9.5, color=POS))

    # Правий домен: Завжди активний (Always-On Domain)
    f.append(rect(480, 48, 270, 225, fill="#eff6ff", stroke=C_CLK, sw=1.5, rx=6))
    f.append(text(615, 70, "Активний домен (Always-On)", size=11.5, color=C_CLK, bold=True))
    f.append(text(615, 87, "VDD_AON = 0.9 В (постійне живлення)", size=9.5, color=C_AON))

    # Межа між доменами (Isolation Boundary)
    f.append(line(375, 45, 375, 275, color=C_CTRL, sw=2, dash="5,5"))
    f.append(text(375, 285, "Межа живлення", size=9.5, color=C_CTRL, bold=True))

    # Вихідний каскад вимкненого домену (CMOS Inverter)
    f.append(rect(60, 110, 195, 110, fill="#ffffff", stroke=C_OFF, sw=1.2, rx=4))
    f.append(text(157, 130, "Останній логічний вентиль", size=10, color=MUTED, bold=True))
    f.append(text(157, 148, "Вимкнений інвертор CMOS", size=9.5, color=MUTED))
    f.append(text(157, 185, "Вихідний плаваючий рівень", size=9, color=POS))
    f.append(text(157, 202, "Z (Floating: ~0.4–0.5 В)", size=9.5, color=POS, bold=True))

    # Лінія зв'язку крізь межу
    f.append(line(255, 160, 315, 160, color=POS, sw=2))
    f.append(text(285, 152, "Плаваючий Z", size=9, color=POS))

    # Комірка ізоляції (Isolation Cell AND-type)
    f.append(rect(315, 105, 125, 120, fill="#ffffff", stroke=C_AON, sw=2, rx=4))
    f.append(rect(315, 105, 125, 22, fill=C_AON, stroke=C_AON, sw=1, rx=4))
    f.append(text(377, 120, "Isolation Cell (AND)", size=9.5, color="#ffffff", bold=True))

    # Схема AND всередині комірки
    f.append(rect(345, 138, 55, 45, fill="#fef3c7", stroke=C_AON, sw=1.2, rx=3))
    f.append(text(372, 165, "&", size=16, bold=True, color=C_AON))

    # Входи комірки ізоляції
    f.append(line(315, 150, 345, 150, color=POS, sw=1.8))
    f.append(line(372, 210, 372, 183, color=C_CTRL, sw=1.8))
    f.append(text(372, 220, "ISO_EN (0 = Блок)", size=9, color=C_CTRL, bold=True))

    # Живлення самої комірки ізоляції від Always-On
    f.append(line(372, 85, 372, 105, color=C_AON, sw=2))
    f.append(circle(372, 85, 3, fill=C_AON, stroke=C_AON))
    f.append(text(372, 78, "VDD_AON", size=9.5, color=C_AON, bold=True))

    # Вихід ізольованого сигналу в Always-On домен
    f.append(line(400, 160, 510, 160, color=FIELD, sw=2))
    f.append(text(455, 152, "Фіксований 0 (Clamp-0)", size=9, color=FIELD, bold=True))

    # Вхідний каскад активного домену
    f.append(rect(510, 110, 215, 110, fill="#ffffff", stroke=C_CLK, sw=1.2, rx=4))
    f.append(text(617, 130, "Вхідний приймач Always-On", size=10, color=C_CLK, bold=True))
    f.append(text(617, 152, "pMOS = Закритий, nMOS = Відкритий", size=9, color=FIELD))
    f.append(text(617, 172, "✓ Струм витоку = 0", size=9.5, color=FIELD, bold=True))
    f.append(text(617, 192, "✓ Чіткий логічний рівень '0'", size=9.5, color=FIELD))
    f.append(text(617, 208, "✓ Немає хибних перемикань", size=9, color=MUTED))

    # Нижня панель: Що було б БЕЗ комірки ізоляції (Небезпека Crowbar Current)
    f.append(rect(30, 300, 720, 120, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(390, 322, "Чому плаваючий сигнал неприпустимий (Аварія без Isolation Cell):",
                  size=11, color=POS, bold=True))
    f.append(text(390, 344, "1. Напруга ~0.5 В на затворі відкриває ОДНОЧАСНО pMOS та nMOS приймача активного домену.",
                  size=9.5, color=INK))
    f.append(text(390, 364, "2. Виникає прямий наскрізний струм короткого замикання (Crowbar Current: VDD → GND) у міліампери.",
                  size=9.5, color=INK))
    f.append(text(390, 384, "3. Наслідки: локальний перегрів, катастрофічний розряд батареї та спотворення станів логіки.",
                  size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "isolation-cell-mechanism.svg"), W, H, *f)


# ── d-фіг.4: Комірка збереження стану (Retention Flip-Flop) ───────────────────
def fig_retention_flip_flop():
    W, H = 780, 450
    f = [text(W / 2, 24, "Комірка збереження стану (Retention Flip-Flop / Balloon Latch)",
              size=14, bold=True)]

    # Загальний контур тригера збереження стану
    f.append(rect(30, 48, 720, 385, fill=C_BOX, stroke=C_CTRL, sw=1.5, rx=6))
    f.append(text(390, 72, "Retention D-Flip-Flop (RFF) з тіньовою защіпкою на Always-On живленні",
                  size=12, color=C_CTRL, bold=True))

    # Ліва секція: Основний D-тригер (комутоване живлення VDD_SW)
    f.append(rect(45, 95, 335, 230, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(rect(45, 95, 335, 24, fill="#f1f5f9", stroke=LINE, sw=1, rx=4))
    f.append(text(212, 111, "Основний Master-Slave тригер (Комутоване VDD_SW)", size=9.5, bold=True))

    # Master Latch
    f.append(rect(60, 135, 115, 105, fill="#f8fafc", stroke=LINE, sw=1.2, rx=3))
    f.append(text(117, 155, "Master Latch", size=10, bold=True))
    f.append(text(117, 173, "Комутований", size=9, color=MUTED))
    f.append(line(45, 185, 60, 185, color=LINE, sw=1.8))
    f.append(text(40, 189, "D", size=10, bold=True, anchor="end"))

    # Slave Latch
    f.append(rect(210, 135, 115, 105, fill="#f8fafc", stroke=LINE, sw=1.2, rx=3))
    f.append(text(267, 155, "Slave Latch", size=10, bold=True))
    f.append(text(267, 173, "Комутований", size=9, color=MUTED))

    # З'єднання Master -> Slave
    f.append(line(175, 185, 210, 185, color=LINE, sw=1.8))

    # Вихід Q
    f.append(line(325, 185, 380, 185, color=LINE, sw=1.8))
    f.append(line(380, 185, 700, 185, color=LINE, sw=1.8))
    f.append(text(705, 189, "Q", size=10, bold=True, anchor="start"))

    # Тактовий сигнал CLK
    f.append(line(50, 275, 117, 275, color=C_CLK, sw=1.8))
    f.append(line(117, 275, 117, 240, color=C_CLK, sw=1.8))
    f.append(line(117, 275, 267, 275, color=C_CLK, sw=1.8))
    f.append(line(267, 275, 267, 240, color=C_CLK, sw=1.8))
    f.append(text(45, 279, "CLK", size=9.5, color=C_CLK, bold=True, anchor="end"))

    # Права секція: Тіньова комірка збереження (Shadow / Balloon Latch)
    f.append(rect(455, 95, 275, 230, fill="#fffbeb", stroke=C_AON, sw=1.5, rx=4))
    f.append(rect(455, 95, 275, 24, fill=C_AON, stroke=C_AON, sw=1, rx=4))
    f.append(text(592, 111, "Тіньовий Balloon Latch (Always-On VDD_AON)", size=9.5, color="#ffffff", bold=True))

    # Тіньова защіпка
    f.append(rect(485, 135, 215, 105, fill="#ffffff", stroke=C_AON, sw=1.3, rx=3))
    f.append(text(592, 155, "Низьковитічна защіпка", size=10, color=C_AON, bold=True))
    f.append(text(592, 173, "HVT-транзистори (High Vt)", size=9, color=MUTED))
    f.append(text(592, 190, "Зберігає 1 біт уві сні", size=9, color=C_AON))

    # Канали SAVE та RESTORE (прокладені у проміжку між x=380 та x=455)
    # Канал SAVE: Slave -> Balloon
    f.append(line(290, 135, 290, 125, color=C_CTRL, sw=1.5))
    f.append(line(290, 125, 485, 125, color=C_CTRL, sw=1.5))
    f.append(line(485, 125, 485, 135, color=C_CTRL, sw=1.5))
    f.append(rect(390, 115, 52, 20, fill="#ffffff", stroke=C_CTRL, sw=1, rx=2))
    f.append(text(416, 129, "SAVE", size=9, color=C_CTRL, bold=True))

    # Канал RESTORE: Balloon -> Slave
    f.append(line(510, 240, 510, 250, color=FIELD, sw=1.5))
    f.append(line(510, 250, 290, 250, color=FIELD, sw=1.5))
    f.append(line(290, 250, 290, 240, color=FIELD, sw=1.5))
    f.append(rect(385, 240, 64, 20, fill="#ffffff", stroke=FIELD, sw=1, rx=2))
    f.append(text(417, 254, "RESTORE", size=9, color=FIELD, bold=True))

    # Нижня частина: Хід збереження і відновлення
    f.append(rect(45, 340, 685, 75, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    f.append(text(390, 358, "Послідовність роботи тригера збереження:", size=10, bold=True))
    f.append(text(390, 376, "1. Перед сном: імпульс SAVE переписує біт із Slave Latch у тіньовий Balloon Latch.", size=9.5, color=INK))
    f.append(text(390, 393, "2. Сон: VDD_SW = 0 В (Master-Slave гаснуть), а Balloon тримає біт від VDD_AON.", size=9.5, color=C_AON))
    f.append(text(390, 409, "3. Пробудження: після увімкнення VDD_SW імпульс RESTORE миттєво повертає стан у Slave.", size=9.5, color=FIELD))

    render(os.path.join(IMG, "retention-flip-flop.svg"), W, H, *f)


# ── d-фіг.5: Пусковий струм та ланцюжкове увімкнення (Daisy Chain) ───────────
def fig_inrush_daisy_chain():
    W, H = 780, 460
    f = [text(W / 2, 24, "Пускові струми (Inrush Current) та ланцюжкове керування силовою сіткою",
              size=14, bold=True)]

    # Ліва половина: Одночасне увімкнення (Supply Collapse / IR Drop)
    f.append(rect(30, 48, 345, 395, fill=C_BOX, stroke=POS, sw=1.5, rx=6))
    f.append(text(202, 70, "Одночасне вмикання ключів (Без контролю)", size=11.5, color=POS, bold=True))
    f.append(text(202, 86, "Катастрофічний пусковий струм та просідання VDD", size=9.5, color=MUTED))

    # Схема живлення з паразитними L і C
    f.append(rect(45, 102, 315, 80, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    f.append(text(202, 118, "Шина живлення (PDN) + L_package", size=9.5, color=C_PWR, bold=True))
    f.append(line(55, 135, 110, 135, color=C_PWR, sw=2.5))
    # Індуктивність
    f.append(rect(110, 127, 45, 16, fill="#fef2f2", stroke=C_PWR, sw=1.2, rx=2))
    f.append(text(132, 139, "L_pkg", size=9, color=POS, bold=True))
    f.append(line(155, 135, 340, 135, color=C_PWR, sw=2.5))
    f.append(text(260, 126, "Спільна шина VDD", size=9, color=C_PWR))

    # Силові ключі, що вмикаються разом
    for sx in [180, 230, 280]:
        f.append(rect(sx, 145, 30, 20, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
        f.append(text(sx + 15, 158, "SW", size=9, color=POS, bold=True))
        f.append(line(sx + 15, 135, sx + 15, 145, color=C_PWR, sw=1.5))
        f.append(line(sx + 15, 165, sx + 15, 175, color=C_AON, sw=1.5))

    f.append(text(202, 175, "Усі ключі вмикаються ОДНОЧАСНО", size=9, color=POS, bold=True))

    # Графіки пускового струму та напруги
    g_y0 = 200
    f.append(text(90, g_y0 + 20, "Струм I_inrush", size=9.5, color=POS, bold=True, anchor="end"))
    f.append(line(100, g_y0 + 70, 350, g_y0 + 70, color=LINE, sw=1)) # вісь t
    f.append(line(100, g_y0 + 10, 100, g_y0 + 70, color=LINE, sw=1)) # вісь I
    # Пік струму
    f.append('<path d="M 100,%d L 140,%d Q 160,%d 180,%d L 340,%d" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        g_y0 + 70, g_y0 + 70, g_y0 + 15, g_y0 + 70, g_y0 + 70, POS))
    f.append(text(160, g_y0 + 10, "I_peak = C · (dV/dt)", size=9.5, color=POS, bold=True))

    # Просідання напруги
    f.append(text(90, g_y0 + 105, "Напруга VDD", size=9.5, color=C_PWR, bold=True, anchor="end"))
    f.append(line(100, g_y0 + 155, 350, g_y0 + 155, color=LINE, sw=1))
    f.append(line(100, g_y0 + 95, 100, g_y0 + 155, color=LINE, sw=1))
    f.append('<path d="M 100,%d L 140,%d Q 160,%d 180,%d L 340,%d" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        g_y0 + 105, g_y0 + 105, g_y0 + 150, g_y0 + 105, g_y0 + 105, C_PWR))
    f.append(text(180, g_y0 + 168, "ΔV = L·(di/dt) + I·R (Supply Droop)", size=9, color=POS, bold=True))

    f.append(text(202, g_y0 + 205, "→ Збій тригерів у сусідніх активних доменах!", size=9.5, color=POS, bold=True))


    # Права половина: Ступеневе увімкнення через Daisy Chain
    f.append(rect(405, 48, 345, 395, fill=C_BOX, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(577, 70, "Ланцюжкове увімкнення (Daisy Chain)", size=11.5, color=FIELD, bold=True))
    f.append(text(577, 86, "Почергове вмикання ключів через буфери затримки", size=9.5, color=MUTED))

    # Схема Daisy Chain
    f.append(rect(420, 102, 315, 80, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    f.append(line(430, 118, 715, 118, color=C_PWR, sw=2.5))
    f.append(text(670, 110, "Шина VDD", size=9, color=C_PWR))

    # Ланцюжок ключів та буферів
    f.append(line(430, 160, 450, 160, color=C_CTRL, sw=1.8))
    f.append(text(428, 164, "SLEEP", size=9, color=C_CTRL, bold=True, anchor="end"))

    # Ступінь 1 (слабкий/перший ключ)
    f.append(rect(450, 148, 32, 24, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(466, 163, "SW 1", size=9, color=FIELD, bold=True))
    f.append(line(466, 118, 466, 148, color=C_PWR, sw=1.5))
    f.append(line(466, 172, 466, 180, color=C_AON, sw=1.5))

    # Буфер затримки 1
    f.append(line(482, 160, 500, 160, color=C_CTRL, sw=1.5))
    f.append(rect(500, 150, 24, 20, fill="#ffffff", stroke=LINE, sw=1, rx=2))
    f.append(text(512, 163, "Δt", size=9, bold=True))

    # Ступінь 2
    f.append(line(524, 160, 542, 160, color=C_CTRL, sw=1.5))
    f.append(rect(542, 148, 32, 24, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(558, 163, "SW 2", size=9, color=FIELD, bold=True))
    f.append(line(558, 118, 558, 148, color=C_PWR, sw=1.5))
    f.append(line(558, 172, 558, 180, color=C_AON, sw=1.5))

    # Буфер затримки 2
    f.append(line(574, 160, 592, 160, color=C_CTRL, sw=1.5))
    f.append(rect(592, 150, 24, 20, fill="#ffffff", stroke=LINE, sw=1, rx=2))
    f.append(text(604, 163, "Δt", size=9, bold=True))

    # Ступінь N
    f.append(line(616, 160, 634, 160, color=C_CTRL, sw=1.5))
    f.append(rect(634, 148, 32, 24, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=2))
    f.append(text(650, 163, "SW N", size=9, color=FIELD, bold=True))
    f.append(line(650, 118, 650, 148, color=C_PWR, sw=1.5))
    f.append(line(650, 172, 650, 180, color=C_AON, sw=1.5))

    # Графіки ступеневого вмикання
    f.append(text(465, g_y0 + 20, "Струм I_inrush", size=9.5, color=FIELD, bold=True, anchor="end"))
    f.append(line(475, g_y0 + 70, 725, g_y0 + 70, color=LINE, sw=1))
    f.append(line(475, g_y0 + 10, 475, g_y0 + 70, color=LINE, sw=1))
    # Ступеневий згладжений струм
    f.append('<path d="M 475,%d L 500,%d L 520,%d L 550,%d L 580,%d L 620,%d L 660,%d L 710,%d" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        g_y0 + 70, g_y0 + 70, g_y0 + 50, g_y0 + 45, g_y0 + 42, g_y0 + 45, g_y0 + 70, g_y0 + 70, FIELD))
    f.append(text(585, g_y0 + 35, "Обмежений піковий струм", size=9, color=FIELD, bold=True))

    # Згладжена напруга
    f.append(text(465, g_y0 + 105, "Напруга VDD", size=9.5, color=C_PWR, bold=True, anchor="end"))
    f.append(line(475, g_y0 + 155, 725, g_y0 + 155, color=LINE, sw=1))
    f.append(line(475, g_y0 + 95, 475, g_y0 + 155, color=LINE, sw=1))
    f.append('<path d="M 475,%d L 500,%d Q 580,%d 660,%d L 710,%d" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        g_y0 + 105, g_y0 + 105, g_y0 + 115, g_y0 + 105, g_y0 + 105, C_PWR))
    f.append(text(585, g_y0 + 130, "Мінімальне просідання (ΔV < 3%)", size=9, color=FIELD, bold=True))

    f.append(text(577, g_y0 + 205, "✓ Безпечний плавний перехід без збоїв суміжних блоків", size=9.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "inrush-daisy-chain.svg"), W, H, *f)


# ── d-фіг.6: Послідовність керування живленням (Power Sequencing FSM) ─────────
def fig_power_sequencing_fsm():
    W, H = 780, 460
    f = [text(W / 2, 24, "Часова діаграма послідовності керування живленням (Power-Down та Power-Up)",
              size=14, bold=True)]

    # Контур
    f.append(rect(30, 48, 720, 395, fill=C_BOX, stroke=LINE, sw=1.5, rx=6))

    # Фази процесу зверху
    f.append(rect(45, 60, 200, 30, fill="#e0f2fe", stroke=C_CLK, sw=1, rx=3))
    f.append(text(145, 79, "Фаза 1: Активний стан", size=10, color=C_CLK, bold=True))

    f.append(rect(250, 60, 180, 30, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    f.append(text(340, 79, "Фаза 2: Power-Down", size=10, color=POS, bold=True))

    f.append(rect(435, 60, 110, 30, fill="#f3f4f6", stroke=MUTED, sw=1, rx=3))
    f.append(text(490, 79, "Фаза 3: Сон", size=10, color=MUTED, bold=True))

    f.append(rect(550, 60, 185, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=3))
    f.append(text(642, 79, "Фаза 4: Power-Up", size=10, color=FIELD, bold=True))

    # Сигнали та часові діаграми
    t_start = 170
    t_end = 720
    s_y0 = 100

    # Вертикальні лінії ключових моментів часу
    t_steps = [250, 290, 330, 370, 420, 550, 600, 640, 680]
    for tx in t_steps:
        f.append(line(tx, s_y0, tx, s_y0 + 295, color="#e5e7eb", sw=1, dash="3,3"))

    # 1. CLK / GCLK
    f.append(text(155, s_y0 + 30, "1. GCLK", size=10, color=C_CLK, bold=True, anchor="end"))
    f.append(line(t_start, s_y0 + 40, t_start, s_y0 + 15, color=C_CLK, sw=1.5))
    clk_p = f"M {t_start},{s_y0 + 40} "
    for cx in range(t_start, 250, 20):
        clk_p += f"L {cx+5},{s_y0+15} L {cx+10},{s_y0+15} L {cx+15},{s_y0+40} L {cx+20},{s_y0+40} "
    clk_p += f"L 680,{s_y0 + 40} "
    for cx in range(680, t_end, 20):
        clk_p += f"L {cx+5},{s_y0+15} L {cx+10},{s_y0+15} L {cx+15},{s_y0+40} L {cx+20},{s_y0+40} "
    f.append(f'<path d="{clk_p}" fill="none" stroke="{C_CLK}" stroke-width="1.8"/>')

    # 2. SAVE / RESTORE
    f.append(text(155, s_y0 + 80, "2. SAVE/RESTORE", size=10, color=C_CTRL, bold=True, anchor="end"))
    save_p = (f"M {t_start},{s_y0 + 90} L 270,{s_y0 + 90} L 275,{s_y0 + 65} L 285,{s_y0 + 65} "
              f"L 290,{s_y0 + 90} L 620,{s_y0 + 90} L 625,{s_y0 + 65} L 635,{s_y0 + 65} "
              f"L 640,{s_y0 + 90} L {t_end},{s_y0 + 90}")
    f.append(f'<path d="{save_p}" fill="none" stroke="{C_CTRL}" stroke-width="1.8"/>')
    f.append(text(280, s_y0 + 60, "SAVE", size=9, color=C_CTRL, bold=True))
    f.append(text(630, s_y0 + 60, "RESTORE", size=9, color=FIELD, bold=True))

    # 3. ISO_EN
    f.append(text(155, s_y0 + 130, "3. ISO_EN", size=10, color=C_AON, bold=True, anchor="end"))
    iso_p = f"M {t_start},{s_y0 + 140} L 310,{s_y0 + 140} L 315,{s_y0 + 115} L 660,{s_y0 + 115} L 665,{s_y0 + 140} L {t_end},{s_y0 + 140}"
    f.append(f'<path d="{iso_p}" fill="none" stroke="{C_AON}" stroke-width="1.8"/>')
    f.append(text(340, s_y0 + 110, "ISO Увімкнено (Clamp)", size=9, color=C_AON, bold=True))

    # 4. RESET_N
    f.append(text(155, s_y0 + 180, "4. RESET_N", size=10, color=LINE, bold=True, anchor="end"))
    rst_p = f"M {t_start},{s_y0 + 165} L 350,{s_y0 + 165} L 355,{s_y0 + 190} L 640,{s_y0 + 190} L 645,{s_y0 + 165} L {t_end},{s_y0 + 165}"
    f.append(f'<path d="{rst_p}" fill="none" stroke="{LINE}" stroke-width="1.8"/>')
    f.append(text(390, s_y0 + 198, "Апаратний скид (Reset)", size=9, color=LINE, bold=True))

    # 5. SLEEP_EN
    f.append(text(155, s_y0 + 230, "5. SLEEP_EN", size=10, color=POS, bold=True, anchor="end"))
    slp_p = f"M {t_start},{s_y0 + 240} L 390,{s_y0 + 240} L 395,{s_y0 + 215} L 550,{s_y0 + 215} L 555,{s_y0 + 240} L {t_end},{s_y0 + 240}"
    f.append(f'<path d="{slp_p}" fill="none" stroke="{POS}" stroke-width="1.8"/>')
    f.append(text(440, s_y0 + 210, "SLEEP Активний", size=9, color=POS, bold=True))

    # 6. VDD_VIRTUAL
    f.append(text(155, s_y0 + 280, "6. VDD_VIRTUAL", size=10, color=C_PWR, bold=True, anchor="end"))
    vdd_p = (f"M {t_start},{s_y0 + 265} L 400,{s_y0 + 265} Q 420,{s_y0 + 290} 450,{s_y0 + 290} "
             f"L 555,{s_y0 + 290} Q 575,{s_y0 + 265} 600,{s_y0 + 265} L {t_end},{s_y0 + 265}")
    f.append(f'<path d="{vdd_p}" fill="none" stroke="{C_PWR}" stroke-width="2.2"/>')
    f.append(text(490, s_y0 + 285, "0 В (Вимкнено)", size=9, color=MUTED, bold=True))
    f.append(text(620, s_y0 + 260, "Стабілізація VDD", size=9, color=FIELD, bold=True))

    # Підписи кроків
    f.append(rect(45, 400, 690, 35, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    f.append(text(390, 422, "Суворий порядок: Power-Down = CLK Off → Save → Iso On → Reset → Sleep On. Power-Up = Sleep Off → VDD Ack → Restore → Reset Release → Iso Off → CLK On.",
                  size=9, bold=True))

    render(os.path.join(IMG, "power-sequencing-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_icg_latch_timing()
    fig_header_footer_switches()
    fig_isolation_cell_mechanism()
    fig_retention_flip_flop()
    fig_inrush_daisy_chain()
    fig_power_sequencing_fsm()
    print("Всі 6 фігур успішно згенеровано у ./img/")
