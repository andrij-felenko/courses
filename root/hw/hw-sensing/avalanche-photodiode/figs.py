# -*- coding: utf-8 -*-
"""Фігури до теми «Лавинний режим і лічба фотонів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Мікроскопічний механізм ударної іонізації та лавини ──────────────────
def fig_impact_ionization():
    W, H = 840, 480
    f = [text(W / 2, 28, "Мікроскопічний механізм ударної іонізації в сильному полі", size=16, bold=True)]

    # Фонова область високого поля p-n переходу
    bx, by, bw, bh = 50, 60, 740, 380
    f.append(rect(bx, by, bw, bh, fill="#f9fbff", stroke=LINE, sw=1.2, rx=8))

    # Стрілка напруженості електричного поля E
    f.append(rect(70, 75, 700, 36, fill="#eef8f2", stroke=FIELD, sw=1.4, rx=4))
    f.append(line(720, 93, 120, 93, color=FIELD, sw=2.5))
    f.append('<polygon points="120,93 134,87 134,99" fill="%s"/>' % FIELD)
    f.append(text(420, 87, "Сильне електричне поле  E ≥ 3·10⁵ В/см  (сила e·E штовхає e⁻ вправо, h⁺ вліво)", size=12, bold=True, color=FIELD))

    # Початковий фотон і первинний електрон
    f.append(circle(100, 240, 8, fill="#ffe58f", stroke="#d48806", sw=1.8))
    f.append(text(100, 218, "h·ν", size=11, bold=True, color="#b8801f"))
    f.append(text(100, 275, "первинне\nпоглинання", size=10, color=MUTED))

    # Траєкторія розгону первинного електрона
    f.append(line(110, 240, 245, 240, color=NEG, sw=2.0))
    f.append('<polygon points="245,240 235,235 235,245" fill="%s"/>' % NEG)
    f.append(text(175, 215, "розгін: E_k ≥ 1.5·E_g", size=10.5, bold=True, color=NEG))

    # 1-й акт ударної іонізації: зіткнення з атомом Si в точці (265, 240)
    f.append(circle(265, 240, 16, fill="#fff1f0", stroke=POS, sw=2.0))
    f.append(text(265, 244, "Si", size=12, bold=True, color=POS))
    f.append(text(265, 175, "1-й акт іонізації\n(e⁻ → 2e⁻ + h⁺)", size=10.5, bold=True, color=INK))

    # Вихід вторинної пари: e⁻ (вправо-вгору), e⁻ (вправо-вниз), h⁺ (вліво)
    # 1) Дірка h⁺ рухається вліво-вниз
    f.append(circle(160, 360, 11, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(160, 364, "h₁⁺", size=11, bold=True, color=POS))
    f.append(line(255, 252, 172, 350, color=POS, sw=1.8))
    f.append('<polygon points="172,350 181,343 173,337" fill="%s"/>' % POS)
    f.append(text(160, 388, "дрейф до анода (p⁺)", size=10, color=POS))

    # 2) Вторинні електрони e₁⁻ та e₂⁻ рухаються вправо
    f.append(line(280, 232, 435, 165, color=NEG, sw=1.8))
    f.append('<polygon points="435,165 423,166 428,174" fill="%s"/>' % NEG)
    f.append(circle(450, 160, 11, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(450, 164, "e₁⁻", size=11, bold=True, color=NEG))

    f.append(line(280, 248, 435, 315, color=NEG, sw=1.8))
    f.append('<polygon points="435,315 428,306 423,314" fill="%s"/>' % NEG)
    f.append(circle(450, 320, 11, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(450, 324, "e₂⁻", size=11, bold=True, color=NEG))

    # 2-й каскад іонізації на (475, 160) та (475, 320)
    f.append(circle(475, 160, 13, fill="#fff1f0", stroke=POS, sw=1.6))
    f.append(text(475, 164, "Si", size=10, bold=True, color=POS))

    f.append(circle(475, 320, 13, fill="#fff1f0", stroke=POS, sw=1.6))
    f.append(text(475, 324, "Si", size=10, bold=True, color=POS))

    # Розгалуження 3-го покоління (лавинний потік)
    ys = [125, 160, 195, 285, 320, 355]
    for idx, y_pos in enumerate(ys):
        f.append(line(490, 160 if idx < 3 else 320, 630, y_pos, color=NEG, sw=1.4))
        f.append(circle(642, y_pos, 8, fill="#eaf0fd", stroke=NEG, sw=1.4))
        f.append(text(642, y_pos + 3.5, "e⁻", size=9, bold=True, color=NEG))

    # Вторинні дірки летять вліво
    f.append(line(460, 170, 370, 215, color=POS, sw=1.4, dash="3,2"))
    f.append(circle(360, 220, 8, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(360, 223.5, "h⁺", size=9, bold=True, color=POS))

    f.append(line(460, 310, 370, 265, color=POS, sw=1.4, dash="3,2"))
    f.append(circle(360, 260, 8, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(360, 263.5, "h⁺", size=9, bold=True, color=POS))

    # Резюме виходу лавини (катод)
    f.append(rect(670, 140, 105, 200, fill="#e6f4ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(722, 175, "Катод (n⁺)", size=12, bold=True, color=NEG))
    f.append(text(722, 205, "Лавинний\nструм I_out", size=11, bold=True, color=INK))
    f.append(text(722, 255, "M = 10..1000\n(APD)\nабо тригер\n(SPAD)", size=10, color=MUTED))

    return render(os.path.join(IMG, "impact-ionization-mechanism.svg"), W, H, *f)


# ── 2. Лінійний режим проти режиму Гейгера (SPAD) на ВАХ ─────────────────────
def fig_linear_vs_geiger():
    W, H = 840, 460
    f = [text(W / 2, 28, "Порівняння режимів APD: Лінійний (M < ∞) проти режиму Гейгера (SPAD)", size=16, bold=True)]

    # Графік ВАХ (зворотна гілка: напруга зсуву V_R проти струму фотодетектора I)
    ox, oy = 80, 380
    gw, gh = 700, 300

    # Осі координат
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (ox + gw, oy, ox + gw - 10, oy - 5, ox + gw - 10, oy + 5, LINE))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (ox, oy - gh, ox - 5, oy - gh + 10, ox + 5, oy - gh + 10, LINE))

    f.append(text(ox + gw - 20, oy + 28, "Зворотна напруга  V_R  [В]", size=12, bold=True, color=INK, anchor="end"))
    f.append(text(ox + 15, oy - gh + 15, "Струм детектора  I_R  [мкА / мА]", size=12, bold=True, color=INK, anchor="start"))

    # Позначки на осі V_R
    v_pin = ox + 140
    v_apd_start = ox + 260
    v_br = ox + 490
    v_spad = ox + 610

    f.append(line(v_pin, oy, v_pin, oy + 6, color=MUTED, sw=1.5))
    f.append(text(v_pin, oy + 22, "0..20 В", size=10.5, color=MUTED))

    f.append(line(v_apd_start, oy, v_apd_start, oy + 6, color=MUTED, sw=1.5))
    f.append(text(v_apd_start, oy + 22, "50..150 В", size=10.5, color=MUTED))

    f.append(line(v_br, oy, v_br, oy - gh + 40, color=POS, sw=1.8, dash="4,3"))
    f.append(text(v_br, oy + 22, "V_BR (пробій)", size=11, bold=True, color=POS))

    f.append(line(v_spad, oy, v_spad, oy + 6, color=NEG, sw=1.5))
    f.append(text(v_spad, oy + 22, "V_BR + V_ex", size=11, bold=True, color=NEG))

    # Зона 1: PIN-режим (M = 1)
    f.append(rect(ox + 5, oy - gh + 40, v_apd_start - ox - 10, gh - 45, fill="#f4f6f8", stroke="none"))
    f.append(text((ox + v_apd_start) / 2, oy - gh + 60, "Звичайний фотодіод\n(M = 1, I_ph = R·P_opt)", size=10.5, color=MUTED))

    # Зона 2: Лінійний лавинний режим (APD: M = 10..1000)
    f.append(rect(v_apd_start + 5, oy - gh + 40, v_br - v_apd_start - 10, gh - 45, fill="#e6f7ff", stroke="none"))
    f.append(text((v_apd_start + v_br) / 2, oy - gh + 60, "Лінійний APD режим\n(M = 10..500, I_out = M·I_ph)", size=11, bold=True, color=NEG))

    # Зона 3: Режим Гейгера (SPAD: V_R > V_BR)
    f.append(rect(v_br + 5, oy - gh + 40, ox + gw - v_br - 15, gh - 45, fill="#fff1f0", stroke="none"))
    f.append(text((v_br + ox + gw) / 2 - 10, oy - gh + 60, "Режим Гейгера (SPAD)\n(Самостійна лавина, M → ∞)", size=11, bold=True, color=POS))

    # Крива струму
    f.append(f'<path d="M {ox},{oy - 20} Q {v_apd_start},{oy - 30} {v_apd_start + 100},{oy - 60} T {v_br - 20},{oy - 190} L {v_br},{oy - 240}" fill="none" stroke="{NEG}" stroke-width="2.6"/>')

    # Лавина в режимі Гейгера: метастабільний стан і стрибок струму
    f.append(line(v_spad, oy - 20, v_spad, oy - 270, color=POS, sw=2.8, dash="5,3"))
    f.append(circle(v_spad, oy - 20, 6, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(v_spad + 12, oy - 20, "стан очікування (0 струму)", size=10, color=POS, anchor="start"))

    f.append(circle(v_spad, oy - 270, 7, fill=POS, stroke=POS, sw=2))
    f.append(text(v_spad + 12, oy - 270, "1 фотон → лавина I ~ 5 мА", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(line(v_spad, oy - 30, v_spad, oy - 260, color=POS, sw=2.0))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (v_spad, oy - 260, v_spad - 5, oy - 248, v_spad + 5, oy - 248, POS))

    # Стрілка V_ex (Overbias)
    f.append(line(v_br, oy + 42, v_spad, oy + 42, color=FIELD, sw=2.0))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (v_br, oy + 42, v_br + 8, oy + 38, v_br + 8, oy + 46, FIELD))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (v_spad, oy + 42, v_spad - 8, oy + 38, v_spad - 8, oy + 46, FIELD))
    f.append(text((v_br + v_spad) / 2, oy + 56, "V_ex = 2..5 В (Overbias)", size=10.5, bold=True, color=FIELD))

    return render(os.path.join(IMG, "linear-vs-geiger-mode.svg"), W, H, *f)


# ── 3. Схеми гасіння лавини: пасивне та активне (AQC) ────────────────────────
def fig_quenching_circuits():
    W, H = 840, 480
    f = [text(W / 2, 28, "Схеми гасіння лавини SPAD: Пасивне (Passive) та Активне (AQC)", size=16, bold=True)]

    # Ліва колонка: Пасивне гасіння (Passive Quenching)
    lx, ly, lw, lh = 40, 55, 365, 400
    f.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(lx + lw / 2, ly + 24, "Пасивне гасіння (Passive Quenching)", size=13, bold=True, color=INK))

    # Схема ліворуч
    # Живлення V_bias
    f.append(text(lx + 60, ly + 60, "V_bias = V_BR + V_ex", size=11, bold=True, color=POS))
    f.append(line(lx + 130, ly + 68, lx + 130, ly + 95, color=LINE, sw=1.8))

    # Баластний резистор R_q
    f.append(rect(lx + 115, ly + 95, 30, 60, fill="#ffffff", stroke=LINE, sw=1.6, rx=2))
    f.append(text(lx + 130, ly + 130, "R_q", size=11, bold=True, color=INK))
    f.append(text(lx + 190, ly + 130, "100..500 кОм", size=10, color=MUTED))

    # Вузол детекції V_spad
    f.append(line(lx + 130, ly + 155, lx + 130, ly + 185, color=LINE, sw=1.8))
    f.append(circle(lx + 130, ly + 185, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(lx + 130, ly + 185, lx + 220, ly + 185, color=LINE, sw=1.6))
    f.append(text(lx + 270, ly + 189, "Вихід V_out", size=11, bold=True, color=NEG))

    # Діод SPAD
    f.append(line(lx + 130, ly + 185, lx + 130, ly + 215, color=LINE, sw=1.8))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (lx + 112, ly + 215, lx + 148, ly + 215, lx + 130, ly + 245, "#ffffff", LINE))
    f.append(line(lx + 112, ly + 245, lx + 148, ly + 245, color=LINE, sw=2.0))
    f.append(line(lx + 112, ly + 245, lx + 112, ly + 252, color=LINE, sw=1.6))
    f.append(line(lx + 148, ly + 245, lx + 148, ly + 238, color=LINE, sw=1.6))
    f.append(text(lx + 180, ly + 235, "SPAD (C_d)", size=10.5, bold=True, color=INK))

    # Земля
    f.append(line(lx + 130, ly + 245, lx + 130, ly + 275, color=LINE, sw=1.8))
    f.append(line(lx + 115, ly + 275, lx + 145, ly + 275, color=LINE, sw=2.0))
    f.append(line(lx + 120, ly + 280, lx + 140, ly + 280, color=LINE, sw=1.6))
    f.append(line(lx + 125, ly + 285, lx + 135, ly + 285, color=LINE, sw=1.2))

    # Часова діаграма відновлення
    f.append(rect(lx + 20, ly + 295, lw - 40, 90, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(line(lx + 40, ly + 365, lx + lw - 45, ly + 365, color=MUTED, sw=1.4))
    f.append(text(lx + 40, ly + 312, "Напруга на діоді V_d(t)", size=10, bold=True, color=INK, anchor="start"))

    f.append(f'<path d="M {lx + 60},{ly + 325} L {lx + 70},{ly + 360} Q {lx + 130},{ly + 355} {lx + 220},{ly + 326} L {lx + 310},{ly + 325}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    f.append(text(lx + 150, ly + 377, "Мертвий час  t_dead ≈ 50..200 нс", size=10, bold=True, color=POS))

    # Права колонка: Активне гасіння (AQC)
    rx_col = 435
    f.append(rect(rx_col, ly, lw, lh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(rx_col + lw / 2, ly + 24, "Активне гасіння (AQC: Швидкий ключ)", size=13, bold=True, color=INK))

    # Схема праворуч
    f.append(rect(rx_col + 30, ly + 80, 95, 75, fill="#e6f7ff", stroke=NEG, sw=1.6, rx=6))
    f.append(text(rx_col + 77, ly + 105, "SPAD\nПіксель", size=11, bold=True, color=NEG))
    f.append(text(rx_col + 77, ly + 140, "C_d ≈ 10 фФ", size=9.5, color=MUTED))

    # Швидкий компаратор
    f.append(line(rx_col + 125, ly + 115, rx_col + 165, ly + 115, color=LINE, sw=1.8))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (rx_col + 165, ly + 90, rx_col + 165, ly + 140, rx_col + 215, ly + 115, "#ffffff", LINE))
    f.append(text(rx_col + 180, ly + 119, "CMP", size=10, bold=True, color=INK))

    # AQC Логіка
    f.append(line(rx_col + 215, ly + 115, rx_col + 245, ly + 115, color=LINE, sw=1.8))
    f.append(rect(rx_col + 245, ly + 80, 100, 75, fill="#eef8f2", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(rx_col + 295, ly + 108, "AQC Логіка\nта Ключі FET", size=11, bold=True, color=FIELD))
    f.append(text(rx_col + 295, ly + 140, "t_dead = 5..15 нс", size=9.5, color=MUTED))

    # Зворотний зв'язок
    f.append(line(rx_col + 295, ly + 155, rx_col + 295, ly + 185, color=FIELD, sw=1.8))
    f.append(line(rx_col + 295, ly + 185, rx_col + 77, ly + 185, color=FIELD, sw=1.8))
    f.append(line(rx_col + 77, ly + 185, rx_col + 77, ly + 155, color=FIELD, sw=1.8))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>'
             % (rx_col + 77, ly + 155, rx_col + 72, ly + 165, rx_col + 82, ly + 165, FIELD))
    f.append(text(rx_col + 186, ly + 178, "Форсоване скидання і перезаряд", size=9.5, bold=True, color=FIELD))

    # Цифровий вихід
    f.append(line(rx_col + 345, ly + 115, rx_col + 355, ly + 115, color=LINE, sw=1.8))
    f.append(text(rx_col + 300, ly + 68, "Цифровий імпульс → TDC", size=10.5, bold=True, color=INK))

    # Часова діаграма для AQC
    f.append(rect(rx_col + 20, ly + 295, lw - 40, 90, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(line(rx_col + 40, ly + 365, rx_col + lw - 45, ly + 365, color=MUTED, sw=1.4))
    f.append(text(rx_col + 40, ly + 312, "Напруга на діоді V_d(t) [AQC]", size=10, bold=True, color=INK, anchor="start"))

    f.append(f'<path d="M {rx_col + 50},{ly + 325} L {rx_col + 65},{ly + 360} L {rx_col + 120},{ly + 360} L {rx_col + 130},{ly + 325} L {rx_col + 180},{ly + 325} L {rx_col + 195},{ly + 360} L {rx_col + 250},{ly + 360} L {rx_col + 260},{ly + 325} L {rx_col + 310},{ly + 325}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')
    f.append(text(rx_col + 150, ly + 377, "Мертвий час  t_dead = 5..20 нс (активний)", size=10, bold=True, color=FIELD))

    return render(os.path.join(IMG, "quenching-circuits.svg"), W, H, *f)


# ── 4. Архітектура dToF LiDAR та TCSPC гістограма ─────────────────────────────
def fig_dtof_tcspc():
    W, H = 840, 480
    f = [text(W / 2, 28, "Архітектура dToF LiDAR на базі SPAD та накопичення гістограми TCSPC", size=16, bold=True)]

    # 1. Лазерний передавач VCSEL і оптичний хід
    f.append(rect(40, 60, 160, 140, fill="#fff1f0", stroke=POS, sw=1.6, rx=6))
    f.append(text(120, 88, "Лазер VCSEL", size=12, bold=True, color=POS))
    f.append(text(120, 110, "λ = 940 нм", size=11, color=INK))
    f.append(text(120, 135, "Імпульс: 1..2 нс\nЧастота: 10 МГц", size=10, color=MUTED))
    f.append(text(120, 182, "Синхроімпульс T_start", size=9.5, bold=True, color=POS))

    # Стрілка променя до цілі
    f.append(line(200, 100, 310, 100, color=POS, sw=2.2))
    f.append('<polygon points="310,100 298,95 298,105" fill="%s"/>' % POS)
    f.append(text(255, 90, "випромінення", size=10, color=POS))

    # Відбивний об'єкт (Ціль)
    f.append(rect(315, 60, 40, 140, fill="#d9d9d9", stroke=LINE, sw=1.6, rx=4))
    f.append(text(335, 135, "Ц\nІ\nЛ\nЬ", size=11, bold=True, color=INK))

    # Відлуння назад до SPAD
    f.append(line(310, 150, 200, 150, color="#d48806", sw=2.0, dash="4,3"))
    f.append('<polygon points="200,150 212,145 212,155" fill="%s"/>' % "#d48806")
    f.append(text(255, 168, "відлуння (dToF)", size=10, color="#b8801f"))

    # 2. Масив SPAD пікселів + TDC
    f.append(rect(40, 230, 290, 200, fill="#e6f7ff", stroke=NEG, sw=1.6, rx=8))
    f.append(text(185, 255, "Матриця SPAD + Банк TDC", size=13, bold=True, color=NEG))

    # Сітка SPAD пікселів
    for row in range(3):
        for col in range(4):
            px = 65 + col * 32
            py = 275 + row * 32
            f.append(rect(px, py, 26, 26, fill="#ffffff", stroke=NEG, sw=1.2, rx=3))
            f.append(circle(px + 13, py + 13, 6, fill="#eaf0fd", stroke=NEG, sw=1))

    f.append(text(225, 305, "SPAD масив\n(16x16 / 8x8)", size=10.5, bold=True, color=INK))

    # Блок TDC (Time-to-Digital Converter)
    f.append(rect(60, 380, 250, 38, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    f.append(text(185, 403, "TDC: квант часу Δt = 20..50 пс", size=11, bold=True, color=INK))

    # Зв'язок від TDC до TCSPC гістограми
    f.append(line(330, 330, 385, 330, color=LINE, sw=2.0))
    f.append('<polygon points="385,330 373,325 373,335" fill="%s"/>' % LINE)
    f.append(text(357, 320, "часові мітки", size=9.5, color=MUTED))

    # 3. Часова гістограма TCSPC (праворуч)
    hx, hy, hw, hh = 395, 60, 405, 370
    f.append(rect(hx, hy, hw, hh, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    f.append(text(hx + hw / 2, hy + 26, "Часова гістограма TCSPC (Накопичення)", size=13, bold=True, color=INK))

    # Осі гістограми
    g_ox, g_oy = hx + 45, hy + 310
    g_w, g_h = 330, 240
    f.append(line(g_ox, g_oy, g_ox + g_w, g_oy, color=LINE, sw=1.8))
    f.append(line(g_ox, g_oy, g_ox, g_oy - g_h, color=LINE, sw=1.8))
    f.append(text(g_ox + g_w, g_oy + 22, "Час приходу фотона t [нс]", size=10.5, color=INK, anchor="end"))
    f.append(text(g_ox + 10, g_oy - g_h + 12, "Кількість подій N", size=10.5, color=INK, anchor="start"))

    # Фоновий шум сонця (Ambient Noise Floor)
    f.append(line(g_ox + 5, g_oy - 45, g_ox + g_w - 5, g_oy - 45, color="#d48806", sw=1.4, dash="4,3"))
    f.append(text(g_ox + 60, g_oy - 52, "Фоновий сонячний шум (Poisson floor)", size=9.5, color="#b8801f", anchor="start"))

    # Стовпчики гістограми шуму + відлуння
    import random
    random.seed(42)
    num_bins = 28
    bin_w = (g_w - 20) / num_bins
    peak_idx = 14

    for b in range(num_bins):
        bx_cur = g_ox + 10 + b * bin_w
        bh_cur = 25 + (b % 4) * 4
        if abs(b - peak_idx) <= 2:
            if b == peak_idx:
                bh_cur = 190
            elif abs(b - peak_idx) == 1:
                bh_cur = 110
            elif abs(b - peak_idx) == 2:
                bh_cur = 55
            col = POS
        else:
            col = "#8c8c8c"
        f.append(rect(bx_cur, g_oy - bh_cur, bin_w - 2, bh_cur, fill=col, stroke="none", rx=1))

    # Стрілка на пік відлуння
    peak_x = g_ox + 10 + peak_idx * bin_w + bin_w / 2
    f.append(line(peak_x, g_oy - 205, peak_x, g_oy - 245, color=POS, sw=1.8))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (peak_x, g_oy - 205, peak_x - 4, g_oy - 215, peak_x + 4, g_oy - 215, POS))
    f.append(text(peak_x, g_oy - 252, "Пік сигналу t_peak = 2·d / c", size=10.5, bold=True, color=POS))
    f.append(text(peak_x, g_oy - 267, "Центроїд: похибка < 1 мм", size=10, color=MUTED))

    return render(os.path.join(IMG, "dtof-tcspc-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_impact_ionization()
    fig_linear_vs_geiger()
    fig_quenching_circuits()
    fig_dtof_tcspc()
    print("All figures generated successfully.")
