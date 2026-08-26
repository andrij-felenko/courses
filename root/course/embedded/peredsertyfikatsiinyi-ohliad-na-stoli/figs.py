# -*- coding: utf-8 -*-
"""Фігури до теми «Передсертифікаційний огляд на столі: бюджетний EMC-тест зондом ближнього поля, струмові кліщі, SDR».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ближнє й дальнє поле ───────────────────────────────────────────────────
def fig_near_far_field():
    W, H = 780, 360
    f = [text(W / 2, 24, "Ближнє й дальнє електромагнітне поле: перехідна зона та розділення E і H",
              size=15, bold=True)]

    # Зона 1: Ближнє поле
    f.append(rect(30, 48, 320, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(190, 72, "Ближнє поле (Near Field):  r < λ / (2π)", size=12.5, bold=True, color=INK))

    # Джерело E-поля (високий імпеданс, dV/dt)
    f.append(rect(50, 95, 120, 70, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    f.append(text(110, 118, "Вузол dV/dt", size=11, bold=True, color=POS))
    f.append(text(110, 134, "радіатор, тактовий пін", size=9.5, color=INK))
    f.append(text(110, 150, "Z >> 377 Ом (E-поле)", size=9.5, bold=True, color=POS))

    # E-field probe
    f.append(rect(200, 95, 130, 70, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    f.append(text(265, 118, "E-Field зонд", size=11, bold=True, color=NEG))
    f.append(text(265, 134, "ємнісний зв'язок Cp", size=9.5, color=INK))
    f.append(text(265, 150, "ловить напругу", size=9.5, color=MUTED))

    # Джерело H-поля (низький імпеданс, dI/dt)
    f.append(rect(50, 185, 120, 75, fill="#dbeafe", stroke=NEG, sw=1.4, rx=4))
    f.append(text(110, 208, "Контур dI/dt", size=11, bold=True, color=NEG))
    f.append(text(110, 224, "петля DCDC, земля", size=9.5, color=INK))
    f.append(text(110, 240, "Z << 377 Ом (H-поле)", size=9.5, bold=True, color=NEG))

    # H-field probe
    f.append(rect(200, 185, 130, 75, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    f.append(text(265, 208, "H-Field зонд (петля)", size=11, bold=True, color="#b45309"))
    f.append(text(265, 224, "індукція Фарадея", size=9.5, color=INK))
    f.append(text(265, 240, "ловить вихровий струм", size=9.5, color=MUTED))

    f.append(text(190, 310, "E та H розділені • локалізація джерел на платі", size=10.5, color=MUTED))

    # Межа r = lambda / 2*pi
    f.append(line(375, 48, 375, 338, color=FIELD, sw=2, dash="4,4"))
    f.append(text(375, 190, "r = λ / (2π)", size=11, bold=True, color=FIELD, anchor="middle"))

    # Зона 2: Дальнє поле
    f.append(rect(400, 48, 350, 290, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(575, 72, "Дальнє поле (Far Field):  r >> λ / (2π)", size=12.5, bold=True, color=INK))

    # Плоска хвиля TEM
    f.append(rect(420, 100, 140, 150, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(490, 125, "Плоска TEM-хвиля", size=11, bold=True, color=INK))
    f.append(text(490, 150, "E ⊥ H ⊥ поширення", size=10, color=MUTED))
    f.append(text(490, 180, "Z₀ = E / H ≈ 377 Ом", size=11, bold=True, color=FIELD))
    f.append(text(490, 210, "хвильовий опір", size=9.5, color=MUTED))
    f.append(text(490, 225, "вільного простору", size=9.5, color=MUTED))

    # Антена лабораторії
    f.append(rect(585, 100, 145, 150, fill="#fef2f2", stroke=POS, sw=1.4, rx=4))
    f.append(text(657, 125, "Антена в камері", size=11, bold=True, color=POS))
    f.append(text(657, 150, "дистанція 3 м / 10 м", size=10, color=INK))
    f.append(text(657, 180, "CISPR 32 / FCC Part 15", size=10, bold=True, color=INK))
    f.append(text(657, 210, "фіксація сумарного", size=9.5, color=MUTED))
    f.append(text(657, 225, "випромінювання (дБмкВ/м)", size=9.5, color=MUTED))

    f.append(text(575, 310, "Офіційний тест перевіряє тільки сумарне дальнє поле", size=10.5, color=MUTED))

    render(os.path.join(IMG, "near-vs-far-field.svg"), W, H, *f)


# ── 2. Будова екранованого H-зонда ───────────────────────────────────────────
def fig_h_field_probe():
    W, H = 760, 360
    f = [text(W / 2, 24, "Екранований зонд магнітного поля: розріз екрана та детектування струму",
              size=15, bold=True)]

    # Ліворуч: Будова петлі
    f.append(rect(30, 50, 330, 285, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(195, 75, "Будова петльового коаксіального зонда", size=12, bold=True, color=INK))

    # Зовнішнє коло (екран)
    f.append('<circle cx="195" cy="180" r="60" fill="none" stroke="#2563eb" stroke-width="8"/>')
    # Внутрішня центральна жила
    f.append('<circle cx="195" cy="180" r="60" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="4,4"/>')

    # Розріз екрана у верхній точці
    f.append(rect(183, 115, 24, 12, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=2))
    f.append(text(195, 105, "Розріз екрана (Gap)", size=10, bold=True, color=POS))

    # Магнітний потік
    f.append(text(195, 175, "Потік Φ (H-поле)", size=11, bold=True, color="#b45309"))
    f.append(text(195, 192, "V = -dΦ/dt", size=11, bold=True, color=POS))

    # Пояснення знизу
    f.append(text(195, 275, "Мідний екран блокує електричне E-поле", size=10, color=NEG))
    f.append(text(195, 292, "Розріз запобігає к.з. витку й пропускає магнітне H-поле", size=10, color=INK))
    f.append(text(195, 310, "Сигнал індукується за законом Фарадея", size=9.8, color=MUTED))

    # Праворуч: Взаємодія з провідником на платі
    f.append(rect(390, 50, 340, 285, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(560, 75, "Орієнтація зонда відносно доріжки з ВЧ-струмом", size=12, bold=True, color=INK))

    # Доріжка плати
    f.append(rect(420, 230, 280, 16, fill="#fef08a", stroke="#ca8a04", sw=1.4, rx=2))
    f.append(text(560, 242, "Доріжка PCB зі струмом I_RF (di/dt)  →", size=10.5, bold=True, color=INK))

    # Позиція 1: Паралельна площина (максимум сигналу)
    f.append(rect(420, 105, 130, 95, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(485, 125, "Паралельно доріжці", size=10.5, bold=True, color=FIELD))
    f.append(text(485, 145, "θ = 0°  (cos θ = 1)", size=10, color=INK))
    f.append(text(485, 165, "МАКСИМУМ зв'язку", size=10.5, bold=True, color=FIELD))
    f.append(text(485, 185, "потік Φ пронизує петлю", size=9.5, color=MUTED))

    # Позиція 2: Перпендикулярна площина (мінімум сигналу)
    f.append(rect(570, 105, 140, 95, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    f.append(text(640, 125, "Перпендикулярно", size=10.5, bold=True, color=POS))
    f.append(text(640, 145, "θ = 90°  (cos θ = 0)", size=10, color=INK))
    f.append(text(640, 165, "МІНІМУМ зв'язку", size=10.5, bold=True, color=POS))
    f.append(text(640, 185, "потік ковзає вздовж петлі", size=9.5, color=MUTED))

    f.append(text(560, 290, "Поворот зонда на 90° визначає точний вектор", size=10.5, color=INK))
    f.append(text(560, 310, "протікання завадного високочастотного струму", size=10.5, color=MUTED))

    render(os.path.join(IMG, "h-field-shielded-loop.svg"), W, H, *f)


# ── 3. Схема DC-LISN ─────────────────────────────────────────────────────────
def fig_dc_lisn_topology():
    W, H = 780, 360
    f = [text(W / 2, 24, "Схема еквівалента мережі DC-LISN (50 мкГн // 50 Ом) та захисний вхідний тракт",
              size=15, bold=True)]

    # Головна рамка LISN
    f.append(rect(30, 48, 720, 290, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))

    # Вхід від джерела живлення
    f.append(rect(45, 100, 100, 50, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    f.append(text(95, 122, "Джерело", size=11, bold=True, color=INK))
    f.append(text(95, 138, "живлення DC", size=10, color=MUTED))

    # Лінія живлення верхня (+)
    f.append(line(145, 125, 230, 125, color=POS, sw=2.2))
    # Блокувальний конденсатор C2 (1 мкФ) на землю
    f.append(line(185, 125, 185, 190, color=LINE, sw=1.6))
    f.append(rect(171, 190, 28, 18, fill="#ffffff", stroke=LINE, sw=1.4))
    f.append(text(185, 203, "C2", size=9.5, bold=True, color=INK))
    f.append(text(142, 203, "1 мкФ", size=9.5, color=MUTED))
    f.append(line(185, 208, 185, 250, color=LINE, sw=1.6))

    # Дросель L1 (50 мкГн) з паралельним демпфером R1 (1 кОм)
    f.append(rect(230, 95, 110, 60, fill="#ffffff", stroke="#0284c7", sw=1.4, rx=4))
    f.append(text(285, 118, "L1: 50 мкГн", size=11, bold=True, color="#0369a1"))
    f.append(text(285, 138, "// R1: 1 кОм", size=10, color=MUTED))

    # З'єднання до DUT
    f.append(line(340, 125, 430, 125, color=POS, sw=2.2))
    f.append(line(430, 125, 680, 125, color=POS, sw=2.2))

    # Блок DUT (Test Device)
    f.append(rect(610, 95, 120, 160, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    f.append(text(670, 125, "Тестований", size=11, bold=True, color="#b45309"))
    f.append(text(670, 142, "пристрій (DUT)", size=11, bold=True, color="#b45309"))
    f.append(text(670, 175, "Джерело ВЧ шуму", size=9.5, color=POS))
    f.append(text(670, 195, "DCDC, MCU, шини", size=9.5, color=INK))
    f.append(text(670, 230, "Земля DUT", size=9.5, color=MUTED))

    # Відгалуження ВЧ-вимірювання від точки DUT
    f.append(line(430, 125, 430, 170, color=POS, sw=1.8))
    # C1 (0.1 мкФ)
    f.append(rect(416, 170, 28, 18, fill="#ffffff", stroke=LINE, sw=1.4))
    f.append(text(430, 183, "C1", size=9.5, bold=True, color=INK))
    f.append(text(380, 183, "0.1 мкФ", size=9.5, color=MUTED))

    f.append(line(430, 188, 430, 220, color=LINE, sw=1.8))
    # Навантаження 50 Ом до землі
    f.append(line(430, 220, 365, 220, color=LINE, sw=1.6))
    f.append(rect(348, 220, 34, 18, fill="#ffffff", stroke=LINE, sw=1.4))
    f.append(text(365, 233, "50 Ом", size=9.5, bold=True, color=INK))
    f.append(line(365, 238, 365, 250, color=LINE, sw=1.6))

    # Вихід на Transient Limiter
    f.append(line(430, 220, 475, 220, color="#16a34a", sw=2))

    # Блок Transient Limiter
    f.append(rect(475, 195, 120, 52, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(535, 215, "Transient Limiter", size=10, bold=True, color=FIELD))
    f.append(text(535, 233, "10 дБ + діодний захист", size=9.5, color=INK))

    # До SDR
    f.append(line(535, 247, 535, 275, color="#16a34a", sw=2))
    f.append(rect(470, 275, 130, 45, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    f.append(text(535, 295, "SDR / TinySA", size=11, bold=True, color=NEG))
    f.append(text(535, 310, "Вхід RF 50 Ом", size=9.5, color=MUTED))

    # Загальна шина заземлення
    f.append(line(60, 250, 680, 250, color="#334155", sw=2.5))
    f.append(text(250, 270, "Мідна пластина заземлення (Reference Ground Plane)", size=10.5, bold=True, color="#334155"))

    # Пояснення функцій LISN
    f.append(text(250, 310, "1. Стабілізує Z = 50 Ом  •  2. Фільтрує шум БЖ  •  3. Знімає ВЧ заваду", size=10, color=MUTED))

    render(os.path.join(IMG, "dc-lisn-topology.svg"), W, H, *f)


# ── 4. Фізика струмових кліщів RF ─────────────────────────────────────────────
def fig_current_clamp():
    W, H = 780, 360
    f = [text(W / 2, 24, "RF струмові кліщі: детектування синфазного струму (I_cm) та випромінювання кабелю",
              size=15, bold=True)]

    # Ліва половина: Будова кліщів на кабелі
    f.append(rect(30, 48, 350, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(205, 72, "Трансформація струмів у фериті", size=12, bold=True, color=INK))

    # Кабель (два проводи)
    f.append(line(50, 140, 360, 140, color=POS, sw=3))
    f.append(text(75, 130, "Провід (+)  I_diff →", size=9.5, bold=True, color=POS))

    f.append(line(50, 180, 360, 180, color=NEG, sw=3))
    f.append(text(75, 195, "Провід (−)  ← I_diff", size=9.5, bold=True, color=NEG))

    # Синфазний струм стрілки
    f.append(text(300, 130, "I_cm →", size=9.5, bold=True, color="#d97706"))
    f.append(text(300, 195, "I_cm →", size=9.5, bold=True, color="#d97706"))

    # Феритовий сердечник кліщів (кільце навколо кабелю)
    f.append(rect(170, 110, 60, 100, fill="none", stroke="#475569", sw=12, rx=8))
    f.append(text(200, 100, "Феритовий тороїд", size=10, bold=True, color="#334155"))

    # Вторинна обмотка
    f.append(rect(210, 120, 20, 80, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=2))
    f.append(text(200, 228, "Вторинна обмотка (N витків)", size=9.5, color=MUTED))

    # Вихід до SDR
    f.append(line(220, 200, 220, 250, color=LINE, sw=1.6))
    f.append(rect(160, 250, 120, 40, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    f.append(text(220, 268, "V_out = Z_T · I_cm", size=11, bold=True, color=NEG))
    f.append(text(220, 282, "до SDR / аналізатора", size=9.5, color=MUTED))

    f.append(text(205, 315, "Диференційний струм взаємно віднімається (0)", size=9.5, color=MUTED))

    # Права половина: Кабель як антена
    f.append(rect(400, 48, 350, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(575, 72, "Кабель як передавальна антена", size=12, bold=True, color=INK))

    # Плата і метровий кабель
    f.append(rect(420, 120, 70, 80, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    f.append(text(455, 150, "Плата", size=11, bold=True, color="#b45309"))
    f.append(text(455, 170, "5×5 см", size=10, color=MUTED))

    f.append(line(490, 160, 680, 160, color=POS, sw=3))
    f.append(text(585, 150, "Кабель L = 1 м (монополь λ/4)", size=10, bold=True, color=INK))

    # Випромінювання хвилі
    f.append('<path d="M 600 130 Q 640 100 680 130" fill="none" stroke="#dc2626" stroke-width="2"/>')
    f.append('<path d="M 610 115 Q 650 85 690 115" fill="none" stroke="#dc2626" stroke-width="2"/>')
    f.append(text(650, 95, "E-поле (випромінювання)", size=10, bold=True, color=POS))

    # Числовий факт
    f.append(rect(420, 220, 310, 75, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    f.append(text(575, 240, "Парадокс синфазного струму:", size=11, bold=True, color=POS))
    f.append(text(575, 260, "Струм I_cm усього 5 мкА на частоті 100 МГц", size=10.5, color=INK))
    f.append(text(575, 280, "створює поле > 40 дБмкВ/м на 3 м  →  FAIL!", size=10.5, bold=True, color=POS))

    f.append(text(575, 318, "Кліщі виявляють невидимі для осцилографа мікроампери", size=9.5, color=MUTED))

    render(os.path.join(IMG, "rf-current-clamp-physics.svg"), W, H, *f)


# ── 5. Інженерний регламент перевірки ─────────────────────────────────────────
def fig_tabletop_workflow():
    W, H = 820, 360
    f = [text(W / 2, 24, "Покроковий регламент передсертифікаційного тестування плати на столі",
              size=15, bold=True)]

    steps = [
        ("1. Базовий фон", "Сканування кімнати\nбез DUT (ефір)", "#e0f2fe", "#0284c7"),
        ("2. LISN тест", "Кондуктивні завади\n150 кГц – 30 МГц", "#e0e7ff", "#4338ca"),
        ("3. H-зонд (огляд)", "Панорама плати\n30 МГц – 1 ГГц", "#fef3c7", "#d97706"),
        ("4. H/E локалізація", "Точкові піки котушок,\nчипів та швів", "#fee2e2", "#dc2626"),
        ("5. RF-кліщі", "Струм I_cm кабелів\nі роз'ємів", "#fce7f3", "#db2777"),
        ("6. Контрзаходи", "Снабери, ферити,\nекрани, slew rate", "#dcfce7", "#16a34a"),
        ("7. Дельта-контроль", "Порівняння спектрів:\nзапас ≥ 6 дБ", "#f0fdf4", "#15803d"),
    ]

    box_w = 100
    box_h = 100
    gap = 14
    start_x = (W - (len(steps) * box_w + (len(steps) - 1) * gap)) / 2
    y = 65

    for i, (title, desc, fill_c, stroke_c) in enumerate(steps):
        bx = start_x + i * (box_w + gap)
        f.append(rect(bx, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.6, rx=5))
        f.append(text(bx + box_w / 2, y + 22, title, size=10, bold=True, color=stroke_c))
        lines = desc.split("\n")
        for line_idx, line_txt in enumerate(lines):
            f.append(text(bx + box_w / 2, y + 50 + line_idx * 16, line_txt, size=9.5, color=INK))

        # Стрілка між блоками
        if i < len(steps) - 1:
            ax = bx + box_w + 2
            ay = y + box_h / 2
            f.append(line(ax, ay, ax + gap - 4, ay, color="#64748b", sw=2))
            f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#64748b"/>' %
                     (ax + gap - 4, ay - 4, ax + gap, ay, ax + gap - 4, ay + 4))

    # Нижній блок інженерних правил
    f.append(rect(start_x, 190, W - 2 * start_x, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(W / 2, 215, "Ключові принципи аудиту на лабораторному столі", size=12, bold=True, color=INK))

    rules = [
        ("Відносність вимірювань:", "Мета — не абсолютні мкВ/м, а фіксація придушення ΔдБ після кожного кроку."),
        ("Режим Max Hold:", "Завжди фіксуйте максимальні піки спектра для виявлення рідкісних імпульсних викидів."),
        ("Запас надійності (Margin):", "Домагайтеся мінімум 6–10 дБ запасу до ліній норм CISPR для гарантованого проходження."),
        ("Комплексність перевірки:", "Тиха плата з брудним кабелем провалить тест так само, як і шумна мікросхема."),
    ]

    for idx, (head_txt, body_txt) in enumerate(rules):
        ry = 240 + idx * 22
        f.append(text(start_x + 20, ry, "• " + head_txt, size=10, bold=True, color=INK, anchor="start"))
        f.append(text(start_x + 215, ry, body_txt, size=9.8, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "tabletop-emc-workflow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_near_far_field()
    fig_h_field_probe()
    fig_dc_lisn_topology()
    fig_current_clamp()
    fig_tabletop_workflow()
    print("All figures generated successfully.")
