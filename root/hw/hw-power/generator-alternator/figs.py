# -*- coding: utf-8 -*-
"""Фігури для теми «Генератор змінного струму» (book/electronics/power-electronics/generator-alternator)."""

import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COL_A = "#c0392b"    # Фаза A (червоний)
COL_B = "#27ae60"    # Фаза B (зелений)
COL_C = "#2457d6"    # Фаза C (синій)
COL_DC = "#d35400"   # Вихідна напруга DC / шина B+
COL_ROT = "#8e44ad"  # Ротор / магнітне поле збудження
COL_WARN = "#c0392b" # Перенапруга / Load Dump
COL_SAFE = "#27ae60" # Захищений рівень


# ── 1. electromechanics-overview: будова та принцип трифазної індукції ───────
def fig_electromechanics_overview():
    W, H = 820, 480
    p = []

    # Заголовок блоку ротора ліворуч
    p.append(rect(30, 45, 340, 370, fill="#fbf9fe", stroke=COL_ROT, sw=1.5, rx=8))
    p.append(text(200, 75, "Ротор: джерело магнітного поля", size=14, color=COL_ROT, bold=True))

    # Вісь і котушка збудження
    p.append(rect(60, 105, 280, 110, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=6))
    p.append(text(200, 130, "Обмотка збудження (L_field, R_field)", size=12, color=INK, bold=True))
    p.append(text(200, 150, "Постійний струм збудження I_field = 1..5 А", size=11, color=MUTED))
    p.append(text(200, 170, "Живлення через контактні кільця й щітки", size=11, color=MUTED))
    p.append(text(200, 190, "(або безщітковий обертовий випрямляч)", size=10, color=MUTED, italic=True))

    # Полюси N і S
    p.append(rect(80, 235, 110, 75, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(135, 265, "Полюс N", size=15, color=POS, bold=True))
    p.append(text(135, 290, "Магнітний потік Φ", size=10, color=MUTED))

    p.append(rect(210, 235, 110, 75, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(265, 265, "Полюс S", size=15, color=NEG, bold=True))
    p.append(text(265, 290, "Замикання потоку", size=10, color=MUTED))

    # Стрілка обертання ротора
    p.append(arrow(140, 340, 260, 340, color=COL_ROT, sw=2.0))
    p.append(text(200, 365, "Обертання з кутовою швидкістю ω (RPM)", size=12, color=COL_ROT, bold=True))
    p.append(text(200, 390, "f_ел = (p · n) / 60  [Гц]", size=11, color=INK))

    # Стрілка магнітної взаємодії
    p.append(arrow(370, 230, 440, 230, color=LINE, sw=2.0))
    p.append(text(405, 215, "dΦ/dt", size=12, color=INK, bold=True))

    # Статор праворуч
    p.append(rect(440, 45, 350, 370, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(615, 75, "Нерухомий статор: три фази на 120°", size=14, color=FIELD, bold=True))

    # 3 фази
    p.append(rect(470, 105, 290, 75, fill="#ffffff", stroke=COL_A, sw=1.5, rx=6))
    p.append(text(615, 130, "Фаза A (0° ел.)", size=13, color=COL_A, bold=True))
    p.append(text(615, 155, "e_A(t) = E_max · sin(ωt)", size=12, color=INK))

    p.append(rect(470, 195, 290, 75, fill="#ffffff", stroke=COL_B, sw=1.5, rx=6))
    p.append(text(615, 220, "Фаза B (−120° ел.)", size=13, color=COL_B, bold=True))
    p.append(text(615, 245, "e_B(t) = E_max · sin(ωt − 120°)", size=12, color=INK))

    p.append(rect(470, 285, 290, 75, fill="#ffffff", stroke=COL_C, sw=1.5, rx=6))
    p.append(text(615, 310, "Фаза C (−240° / +120° ел.)", size=13, color=COL_C, bold=True))
    p.append(text(615, 335, "e_C(t) = E_max · sin(ωt − 240°)", size=12, color=INK))

    p.append(text(615, 390, "Сумарна миттєва потужність постійна: p(t) = 3 · V_ph · I_ph", size=11, color=FIELD, bold=True))

    # Підсумковий висновок
    b, bw, bh = textbox(W / 2, 450,
                        "Обертове поле ротора наводить 3 синусоїдні ЕРС у нерухомих обмотках статора без іскріння й комутаторів",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "electromechanics-overview.svg"), W, H, *p,
           title="Електромеханічний принцип трифазного синхронного генератора")


# ── 2. stator-connections: Зірка проти Трикутника ────────────────────────────
def fig_stator_connections():
    W, H = 820, 460
    p = []

    # Ліва половина: Зірка (Wye / Y)
    p.append(rect(30, 45, 365, 350, fill="#fdfefe", stroke=COL_A, sw=1.5, rx=8))
    p.append(text(212, 75, "З'єднання «Зірка» (Star / Wye / Y)", size=14, color=COL_A, bold=True))

    # Схема зірки: центральна нейтраль N і три промені
    p.append(circle(212, 175, 5, fill=INK, stroke=INK))
    p.append(text(212, 160, "Нейтраль (N)", size=11, color=INK, bold=True))

    p.append(line(212, 175, 120, 245, color=COL_A, sw=2.5))
    p.append(circle(120, 245, 6, fill=COL_A, stroke=COL_A))
    p.append(text(95, 248, "Фаза A", size=11, color=COL_A, bold=True))

    p.append(line(212, 175, 304, 245, color=COL_B, sw=2.5))
    p.append(circle(304, 245, 6, fill=COL_B, stroke=COL_B))
    p.append(text(335, 248, "Фаза B", size=11, color=COL_B, bold=True))

    p.append(line(212, 175, 212, 105, color=COL_C, sw=2.5))
    p.append(circle(212, 105, 6, fill=COL_C, stroke=COL_C))
    p.append(text(245, 108, "Фаза C", size=11, color=COL_C, bold=True))

    # Співвідношення для зірки
    p.append(rect(50, 275, 325, 105, fill="#f4f6f8", stroke="#bdc3c7", sw=1.0, rx=6))
    p.append(text(212, 298, "Лінійна напруга: V_line = √3 · V_phase ≈ 1.732 · V_phase", size=11, color=INK, bold=True))
    p.append(text(212, 320, "Лінійний струм: I_line = I_phase", size=11, color=INK))
    p.append(text(212, 342, "Висока напруга на холостих обертах (зарядка АКБ)", size=10, color=FIELD))
    p.append(text(212, 362, "Доступна нейтраль для зняття 3-ї гармоніки", size=10, color=FIELD))

    # Права половина: Трикутник (Delta / Δ)
    p.append(rect(425, 45, 365, 350, fill="#fdfefe", stroke=COL_C, sw=1.5, rx=8))
    p.append(text(607, 75, "З'єднання «Трикутник» (Delta / Δ)", size=14, color=COL_C, bold=True))

    # Схема трикутника: вершини A, B, C
    p.append(line(607, 115, 520, 245, color=COL_A, sw=2.5))
    p.append(line(520, 245, 694, 245, color=COL_B, sw=2.5))
    p.append(line(694, 245, 607, 115, color=COL_C, sw=2.5))

    p.append(circle(607, 115, 6, fill=COL_A, stroke=COL_A))
    p.append(text(607, 100, "Вузол A", size=11, color=COL_A, bold=True))

    p.append(circle(520, 245, 6, fill=COL_B, stroke=COL_B))
    p.append(text(485, 255, "Вузол B", size=11, color=COL_B, bold=True))

    p.append(circle(694, 245, 6, fill=COL_C, stroke=COL_C))
    p.append(text(730, 255, "Вузол C", size=11, color=COL_C, bold=True))

    # Співвідношення для трикутника
    p.append(rect(445, 275, 325, 105, fill="#f4f6f8", stroke="#bdc3c7", sw=1.0, rx=6))
    p.append(text(607, 298, "Лінійна напруга: V_line = V_phase", size=11, color=INK, bold=True))
    p.append(text(607, 320, "Лінійний струм: I_line = √3 · I_phase ≈ 1.732 · I_phase", size=11, color=INK, bold=True))
    p.append(text(607, 342, "Максимальний струм при низьких напругах", size=10, color=COL_C))
    p.append(text(607, 362, "Небезпека циркуляції струмів 3-ї гармоніки в кільці", size=10, color=COL_WARN))

    # Загальний підсумок
    b, bw, bh = textbox(W / 2, 425,
                        "Зірка дає більшу напругу (+73%) на низьких RPM; трикутник дає більший струм (+73%) без виводу нейтралі",
                        size=11, fill="#eaf0fd", stroke=COL_C, sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "stator-connections.svg"), W, H, *p,
           title="Топології з'єднання обмоток статора: Зірка (Wye) проти Трикутника (Delta)")


# ── 3. larionov-bridge: трифазний міст Ларіонова та форма вихідної пульсації ─
def fig_larionov_bridge():
    W, H = 840, 480
    p = []

    # Ліва частина: принципова схема 6-діодного моста
    p.append(rect(30, 45, 410, 370, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(235, 75, "Трифазний випрямляч Ларіонова (6 діодів)", size=13, color=INK, bold=True))

    # Шина B+ (верхня) і Шина GND (нижня)
    p.append(line(60, 110, 410, 110, color=COL_DC, sw=3.0))
    p.append(text(380, 100, "Шина B+ (+)", size=11, color=COL_DC, bold=True))

    p.append(line(60, 370, 410, 370, color=INK, sw=3.0))
    p.append(text(380, 390, "Шина GND (−)", size=11, color=INK, bold=True))

    # Три стійки моста
    xs = [120, 220, 320]
    phases = [("Фаза A", COL_A), ("Фаза B", COL_B), ("Фаза C", COL_C)]
    for i, (pname, pcol) in enumerate(phases):
        x = xs[i]
        # Верхній діод
        p.append(line(x, 110, x, 170, color=LINE, sw=1.8))
        p.append(rect(x - 22, 170, 44, 40, fill="#ffffff", stroke=pcol, sw=1.5, rx=4))
        p.append(text(x, 195, "D%d" % (i + 1), size=12, color=pcol, bold=True))
        p.append(line(x, 210, x, 270, color=LINE, sw=1.8))

        # Вхід фази
        p.append(circle(x, 240, 5, fill=pcol, stroke=pcol))
        p.append(line(x - 30, 240, x, 240, color=pcol, sw=2.0))
        p.append(text(x - 35, 235, pname, size=10, color=pcol, bold=True, anchor="end"))

        # Нижній діод
        p.append(rect(x - 22, 270, 44, 40, fill="#ffffff", stroke=pcol, sw=1.5, rx=4))
        p.append(text(x, 295, "D%d" % (i + 4), size=12, color=pcol, bold=True))
        p.append(line(x, 310, x, 370, color=LINE, sw=1.8))

    # Права частина: пульсація 6-пульсного виходу
    p.append(rect(460, 45, 350, 370, fill="#fbfcfd", stroke="#bdc3c7", sw=1.5, rx=8))
    p.append(text(635, 75, "6-пульсна вихідна напруга V_dc(t)", size=13, color=COL_DC, bold=True))

    # Осі графіка
    p.append(line(490, 340, 780, 340, color=LINE, sw=1.5))
    p.append(line(490, 340, 490, 110, color=LINE, sw=1.5))
    p.append(text(780, 358, "Час t (360°)", size=10, color=MUTED, anchor="end"))
    p.append(text(485, 115, "V", size=11, color=INK, bold=True, anchor="end"))

    # Пульсації (6 куполів синусоїди)
    arc_w = 45
    start_x = 500
    for k in range(6):
        x0 = start_x + k * arc_w
        x_mid = x0 + arc_w / 2
        x1 = x0 + arc_w
        # крива купола
        path_d = '<path d="M %.1f 180 Q %.1f 140 %.1f 180" fill="none" stroke="%s" stroke-width="2.5"/>' % (x0, x_mid, x1, COL_DC)
        p.append(path_d)

    # Рівень середньої напруги V_avg
    p.append(line(490, 160, 780, 160, color=FIELD, sw=1.5, dash="4 3"))
    p.append(text(780, 155, "V_avg = 1.35 · V_line", size=10, color=FIELD, bold=True, anchor="end"))

    # Рівень піку V_max
    p.append(line(490, 140, 780, 140, color=MUTED, sw=1.0, dash="2 2"))
    p.append(text(780, 135, "V_max = √2 · V_line", size=10, color=MUTED, anchor="end"))

    # Підписи параметрів пульсацій
    p.append(rect(480, 215, 310, 110, fill="#ffffff", stroke="#bdc3c7", sw=1.0, rx=6))
    p.append(text(635, 238, "Частота пульсацій: f_ripple = 6 · f_gen", size=11, color=INK, bold=True))
    p.append(text(635, 260, "Кожен діод проводить рівно 120° (1/3 періоду)", size=10, color=MUTED))
    p.append(text(635, 282, "Амплітуда пульсацій без фільтра: лише 13.4%", size=10, color=MUTED))
    p.append(text(635, 304, "Втрати на діодах: P = 2 · V_f · I_load (до 250 Вт при 150 А!)", size=10, color=COL_WARN, bold=True))

    # Висновок
    b, bw, bh = textbox(W / 2, 450,
                        "Міст Ларіонова відкриває діоди парами (найвищий + найнижчий потенціал), забезпечуючи 6 пульсів за період",
                        size=11, fill="#fdf6e3", stroke="#b8901f", sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "larionov-bridge.svg"), W, H, *p,
           title="Трифазний випрямляч Ларіонова та форма згладженої вихідної напруги")


# ── 4. avr-pwm-control: електронний регулятор напруги AVR та контур ШІМ ──────
def fig_avr_pwm_control():
    W, H = 840, 480
    p = []

    # Генератор зліва
    p.append(rect(30, 45, 220, 360, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=8))
    p.append(text(140, 75, "Генератор", size=14, color=INK, bold=True))

    p.append(rect(50, 105, 180, 70, fill="#ffffff", stroke=COL_ROT, sw=1.5, rx=6))
    p.append(text(140, 130, "Обмотка збудження", size=11, color=COL_ROT, bold=True))
    p.append(text(140, 155, "L_field (200 мГн, 3 Ом)", size=10, color=MUTED))

    p.append(rect(50, 205, 180, 70, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(140, 230, "Статор + Випрямляч", size=11, color=FIELD, bold=True))
    p.append(text(140, 255, "3 фази → 14.4 В DC", size=10, color=MUTED))

    p.append(text(140, 310, "Змінні оберти двигуна:", size=10, color=MUTED))
    p.append(text(140, 330, "RPM = 800 .. 6000 об/хв", size=11, color=INK, bold=True))
    p.append(text(140, 360, "Навантаження: 5 .. 180 А", size=11, color=INK, bold=True))

    # Лінія зворотного зв'язку V_out до AVR
    p.append(line(230, 240, 290, 240, color=COL_DC, sw=2.5))
    p.append(arrow(290, 240, 320, 240, color=COL_DC, sw=2.5))
    p.append(text(275, 225, "V_out", size=11, color=COL_DC, bold=True))

    # Блок AVR по центру
    p.append(rect(320, 45, 300, 360, fill="#fdfefe", stroke=COL_ROT, sw=1.8, rx=8))
    p.append(text(470, 75, "Регулятор напруги (AVR / VR)", size=14, color=COL_ROT, bold=True))

    # Дільник та опорна напруга
    p.append(rect(340, 105, 120, 60, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(400, 130, "Дільник напруги", size=10, color=INK))
    p.append(text(400, 150, "та NTC-термокомпенсація", size=9, color=MUTED))

    p.append(rect(480, 105, 120, 60, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(540, 130, "Опора V_ref", size=11, color=POS, bold=True))
    p.append(text(540, 150, "Bandgap (2.5 В)", size=9, color=MUTED))

    # Компаратор / PID
    p.append(line(400, 165, 430, 205, color=LINE, sw=1.5))
    p.append(line(540, 165, 510, 205, color=LINE, sw=1.5))
    p.append(rect(410, 205, 120, 60, fill="#ffffff", stroke=COL_ROT, sw=1.5, rx=6))
    p.append(text(470, 230, "Помилка / PID", size=11, color=COL_ROT, bold=True))
    p.append(text(470, 250, "ΔV = V_ref − V_sense", size=10, color=MUTED))

    # ШІМ драйвер та силовий MOSFET
    p.append(arrow(470, 265, 470, 295, color=LINE, sw=1.8))
    p.append(rect(350, 295, 240, 85, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(470, 320, "ШІМ-генератор + Gate Driver", size=11, color=FIELD, bold=True))
    p.append(text(470, 340, "Силовий MOSFET (Low-side або High-side)", size=10, color=INK))
    p.append(text(470, 360, "Частота f_pwm = 200..500 Гц, Duty D = 0..100%", size=9, color=MUTED))

    # Керування струмом збудження (повернення в ротор)
    p.append(line(470, 380, 470, 400, color=COL_ROT, sw=2.0))
    p.append(line(470, 400, 260, 400, color=COL_ROT, sw=2.0))
    p.append(line(260, 400, 260, 140, color=COL_ROT, sw=2.0))
    p.append(arrow(260, 140, 230, 140, color=COL_ROT, sw=2.0))
    p.append(text(330, 420, "I_field_avg = D · (V_bat / R_field)", size=11, color=COL_ROT, bold=True))

    # Права панель: реакція на зміну умов
    p.append(rect(640, 45, 170, 360, fill="#fbfcfd", stroke="#bdc3c7", sw=1.5, rx=8))
    p.append(text(725, 75, "Реакція AVR", size=13, color=INK, bold=True))

    p.append(rect(655, 105, 140, 120, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(725, 125, "Навантаження ↑", size=11, color=POS, bold=True))
    p.append(text(725, 145, "або RPM ↓ (холості):", size=9, color=MUTED))
    p.append(text(725, 170, "V_out просідає ↓", size=10, color=INK))
    p.append(text(725, 190, "AVR: ШІМ Duty ↑ (до 100%)", size=9, color=POS, bold=True))
    p.append(text(725, 210, "I_field ↑ → V_out = 14.4 В", size=9, color=FIELD))

    p.append(rect(655, 245, 140, 120, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(725, 265, "Скидання струму ↓", size=11, color=NEG, bold=True))
    p.append(text(725, 285, "або RPM ↑ (високі):", size=9, color=MUTED))
    p.append(text(725, 310, "V_out зростає ↑", size=10, color=INK))
    p.append(text(725, 330, "AVR: ШІМ Duty ↓ (до 5%)", size=9, color=NEG, bold=True))
    p.append(text(725, 350, "I_field ↓ → V_out = 14.4 В", size=9, color=FIELD))

    # Висновок
    b, bw, bh = textbox(W / 2, 450,
                        "AVR змінює середній струм збудження через ШІМ-ключ, підтримуючи 14.4 В незалежно від обертів і навантаження",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "avr-pwm-control.svg"), W, H, *p,
           title="Контур автоматичного регулювання напруги (AVR) методом ШІМ-струму збудження")


# ── 5. armature-reaction: реакція якоря при різних типах навантаження ────────
def fig_armature_reaction():
    W, H = 840, 460
    p = []

    types = [
        ("Активне навантаження (R, cos φ = 1)",
         "Поперечна реакція якоря",
         "Струм у фазі з ЕРС.",
         "Поле статора зсунуте на 90° ел.",
         "Викривляє результуюче поле,",
         "підсилює насичення зубців,",
         "незначно знижує вихідну ЕРС.",
         POS, "#fdf6e3", 30),

        ("Індуктивне навантаження (L, cos φ < 1)",
         "Поздовжньо-розмагнічувальна дія",
         "Струм відстає від ЕРС на 90°.",
         "Поле статора спрямоване строго",
         "ПРОТИ основного поля ротора.",
         "Сильно послаблює магнітний потік,",
         "викликає різку просадку напруги.",
         COL_WARN, "#fdecea", 300),

        ("Ємнісне навантаження (C, cos φ < 1)",
         "Поздовжньо-підмагнічувальна дія",
         "Струм випереджає ЕРС на 90°.",
         "Поле статора спрямоване РАЗОМ",
         "із основним полем ротора.",
         "Підсилює результуючий потік,",
         "може викликати самозбудження.",
         COL_C, "#eaf0fd", 570)
    ]

    for title, subtitle, l1, l2, l3, l4, l5, col, fill, x in types:
        p.append(rect(x, 45, 240, 350, fill=fill, stroke=col, sw=1.5, rx=8))
        p.append(text(x + 120, 75, title, size=11, color=col, bold=True))
        p.append(text(x + 120, 95, subtitle, size=11, color=INK, bold=True))

        # Векторна діаграма
        p.append(circle(x + 120, 165, 45, fill="#ffffff", stroke="#bdc3c7", sw=1.2))

        # Поле ротора B_rotor (вгору)
        p.append(arrow(x + 120, 165, x + 120, 125, color=COL_ROT, sw=2.2))
        p.append(text(x + 140, 135, "Φ_rot", size=10, color=COL_ROT, bold=True))

        if "Активне" in title:
            # Вектор статора вправо (поперечний)
            p.append(arrow(x + 120, 165, x + 160, 165, color=POS, sw=2.2))
            p.append(text(x + 165, 180, "Φ_arm", size=10, color=POS, bold=True))
            # Результуючий під кутом
            p.append(arrow(x + 120, 165, x + 155, 130, color=FIELD, sw=2.0))
            p.append(text(x + 165, 125, "Φ_рез", size=10, color=FIELD, bold=True))
        elif "Індуктивне" in title:
            # Вектор статора вниз (проти поля)
            p.append(arrow(x + 120, 165, x + 120, 200, color=COL_WARN, sw=2.2))
            p.append(text(x + 140, 195, "Φ_arm (↓)", size=10, color=COL_WARN, bold=True))
            # Результуючий короткий
            p.append(arrow(x + 115, 165, x + 115, 145, color=FIELD, sw=2.5))
            p.append(text(x + 95, 150, "Φ_рез ↓", size=10, color=FIELD, bold=True))
        else:
            # Вектор статора вгору (разом з полем)
            p.append(arrow(x + 125, 165, x + 125, 135, color=COL_C, sw=2.2))
            p.append(text(x + 145, 150, "Φ_arm (↑)", size=10, color=COL_C, bold=True))
            # Результуючий довгий
            p.append(arrow(x + 115, 165, x + 115, 110, color=FIELD, sw=2.5))
            p.append(text(x + 90, 115, "Φ_рез ↑↑", size=10, color=FIELD, bold=True))

        # Текстовий опис наслідків
        p.append(text(x + 120, 235, l1, size=10, color=INK))
        p.append(text(x + 120, 255, l2, size=10, color=INK))
        p.append(text(x + 120, 275, l3, size=10, color=INK))
        p.append(text(x + 120, 295, l4, size=10, color=INK))
        p.append(text(x + 120, 315, l5, size=10, color=INK))
        p.append(text(x + 120, 355, "Синхронний реактанс: X_s", size=10, color=MUTED, italic=True))

    # Висновок
    b, bw, bh = textbox(W / 2, 425,
                        "Струм навантаження статора створює власне поле, яке розмагнічує генератор при індуктивному навантаженні",
                        size=11, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "armature-reaction.svg"), W, H, *p,
           title="Реакція якоря синхронного генератора за різного характеру навантаження")


# ── 6. load-dump-transient: скидання навантаження Load Dump та захист ────────
def fig_load_dump_transient():
    W, H = 840, 480
    p = []

    # Графік напруги ліворуч (Без захисту vs Лавинний захист)
    p.append(rect(30, 45, 450, 365, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=8))
    p.append(text(255, 75, "Імпульс перенапруги Load Dump (ISO 16750-2)", size=13, color=INK, bold=True))

    # Осі
    p.append(line(70, 350, 450, 350, color=LINE, sw=1.5))
    p.append(line(70, 350, 70, 100, color=LINE, sw=1.5))
    p.append(text(450, 368, "Час t (мс)", size=10, color=MUTED, anchor="end"))
    p.append(text(65, 105, "V_bat (В)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки шкали напруги
    p.append(text(65, 335, "14 В", size=10, color=MUTED, anchor="end"))
    p.append(line(67, 330, 73, 330, color=MUTED, sw=1.0))

    p.append(text(65, 275, "35 В", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(line(67, 270, 73, 270, color=FIELD, sw=1.5))

    p.append(text(65, 135, "100 В", size=10, color=COL_WARN, bold=True, anchor="end"))
    p.append(line(67, 130, 73, 130, color=COL_WARN, sw=1.5))

    # Нормальний рівень 14 В
    p.append(line(70, 330, 130, 330, color=FIELD, sw=2.0))

    # Точка відриву клеми АКБ
    p.append(circle(130, 330, 4, fill=POS, stroke=POS))
    p.append(text(130, 315, "Відрив АКБ при I=150 А!", size=9, color=POS, bold=True))

    # Крива незахищеного сплеску (до 100 В, спад 400 мс)
    p.append('<path d="M 130 330 Q 140 130 170 130 T 320 220 T 440 330" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4 3"/>' % COL_WARN)
    p.append(text(210, 120, "Незахищений сплеск (80..100 В)", size=11, color=COL_WARN, bold=True))
    p.append(text(250, 140, "Смертельно для всієї бортової електроніки!", size=9, color=COL_WARN))

    # Крива обмеження лавинними діодами (Avalanche / TVS clamping на 35 В)
    p.append('<path d="M 130 330 L 140 270 L 270 270 Q 350 280 440 330" fill="none" stroke="%s" stroke-width="3.0"/>' % FIELD)
    p.append(text(240, 260, "Обмеження лавинними діодами (V_clamp ≈ 32..35 В)", size=10, color=FIELD, bold=True))

    # Позначка тривалості
    p.append(line(130, 380, 440, 380, color=MUTED, sw=1.2))
    p.append(line(130, 375, 130, 385, color=MUTED, sw=1.2))
    p.append(line(440, 375, 440, 385, color=MUTED, sw=1.2))
    p.append(text(285, 395, "Тривалість імпульсу t_d = 100 .. 400 мс", size=10, color=MUTED))

    # Права панель: фізичний механізм аварії
    p.append(rect(500, 45, 310, 365, fill="#fdfefe", stroke=POS, sw=1.5, rx=8))
    p.append(text(655, 75, "Фізика явища та захист", size=13, color=POS, bold=True))

    p.append(rect(515, 100, 280, 80, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(655, 120, "1. Енергія в індуктивності ротора", size=11, color=POS, bold=True))
    p.append(text(655, 140, "E_rot = (1/2) · L_field · I_field²", size=11, color=INK, bold=True))
    p.append(text(655, 160, "Струм I_field не може зникнути миттєво!", size=9, color=MUTED))

    p.append(rect(515, 190, 280, 95, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(655, 210, "2. Стала часу спаду поля", size=11, color=INK, bold=True))
    p.append(text(655, 230, "τ = L_field / R_field ≈ 100..300 мс", size=10, color=INK))
    p.append(text(655, 250, "Статор продовжує генерувати високу", size=9, color=MUTED))
    p.append(text(655, 268, "ЕРС без буферної ємності АКБ.", size=9, color=MUTED))

    p.append(rect(515, 295, 280, 100, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(655, 315, "3. Методи поглинання сплеску", size=11, color=FIELD, bold=True))
    p.append(text(655, 335, "• Лавинні діоди випрямляча (Avalanche)", size=9, color=INK))
    p.append(text(655, 353, "• Центральний TVS-супресор на шині", size=9, color=INK))
    p.append(text(655, 372, "• Швидке розмагнічування ротора в AVR", size=9, color=FIELD, bold=True))

    # Висновок
    b, bw, bh = textbox(W / 2, 450,
                        "Load Dump виникає через затримку спаду магнітного потоку ротора і гаситься лавинними діодами випрямляча",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "load-dump-transient.svg"), W, H, *p,
           title="Імпульс скидання навантаження Load Dump та захист бортової мережі")


def main():
    fig_electromechanics_overview()
    fig_stator_connections()
    fig_larionov_bridge()
    fig_avr_pwm_control()
    fig_armature_reaction()
    fig_load_dump_transient()
    print("Усі 6 фігур згенеровано успішно.")


if __name__ == "__main__":
    main()
