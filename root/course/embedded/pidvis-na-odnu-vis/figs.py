# -*- coding: utf-8 -*-
"""Фігури для статті pidvis-na-odnu-vis («Підвіс на одну вісь: IMU, ПІД, серво»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. gimbal-topology: Мехатроніка та кінематика одноосьового підвісу ────────
def fig_gimbal_topology():
    W, H = 840, 430
    p = []

    # Заголовок / секції
    p.append(rect(20, 20, 380, 390, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))
    p.append(text(210, 48, "Механічна кінематика та шарнір", size=14, color=INK, bold=True))

    # Стійка / базова рама (зовнішній носій)
    p.append(rect(40, 340, 340, 20, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=3))
    p.append(text(210, 355, "Базова платформа (носій / корпус)", size=11, color=MUTED, bold=True))
    p.append(rect(70, 180, 24, 160, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=2))
    p.append(rect(326, 180, 24, 160, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=2))

    # Вал і підшипник
    p.append(line(70, 190, 350, 190, color=LINE, sw=3.0))
    p.append(circle(82, 190, 9, fill="#94a3b8", stroke=LINE, sw=1.5))
    p.append(circle(338, 190, 9, fill="#94a3b8", stroke=LINE, sw=1.5))
    p.append(text(210, 175, "Вісь обертання (підшипники)", size=11, color=INK, bold=True))

    # Підвішена платформа (payload)
    p.append(rect(130, 210, 160, 90, fill="#f8fafc", stroke=POS, sw=2.0, rx=6))
    p.append(text(210, 235, "Стабілізована платформа", size=12, color=POS, bold=True))
    p.append(text(210, 252, "(корисне навантаження)", size=10, color=MUTED))

    # IMU на платформі (Closed-Loop direct feedback)
    p.append(rect(170, 265, 80, 26, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    p.append(text(210, 282, "IMU 6-DOF", size=11, color=POS, bold=True))

    # Сервопривід на стійці
    p.append(rect(46, 120, 72, 60, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    p.append(text(82, 145, "Серво /", size=10, color=NEG, bold=True))
    p.append(text(82, 160, "BLDC мотор", size=10, color=NEG, bold=True))
    p.append(arrow(82, 120, 82, 90, color=NEG, sw=1.5))
    p.append(text(82, 80, "Керівний момент", size=10, color=NEG, italic=True))

    # Центр мас CoM
    p.append(circle(210, 205, 5, fill=FIELD, stroke=LINE, sw=1.2))
    p.append(text(210, 145, "Центр мас CoM на осі: r_cm ≈ 0", size=10, color=FIELD, bold=True))
    p.append(arrow(210, 155, 210, 198, color=FIELD, sw=1.2))

    # Права панель: Структура контуру зв'язку
    p.append(rect(420, 20, 400, 390, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))
    p.append(text(620, 48, "Потік вимірювань і зворотного зв'язку", size=14, color=INK, bold=True))

    # Блоки правої панелі
    b1, _, _ = textbox(620, 100, "1. Збурення носія (кут θ_base)\nТряска корпусу, нахил рами дрона", size=11, fill="#f1f5f9", stroke=MUTED, pad=8)
    p.append(b1)

    p.append(arrow(620, 125, 620, 155, color=LINE, sw=1.5))

    b2, _, _ = textbox(620, 185, "2. Платформа з IMU (Direct Sensing)\nВимірювання кутової швидкості ω та a_y, a_z", size=11, fill="#fee2e2", stroke=POS, pad=8)
    p.append(b2)

    p.append(arrow(620, 215, 620, 245, color=LINE, sw=1.5))

    b3, _, _ = textbox(620, 275, "3. Обчислювач: Фільтр + ПІД\nОцінка кута θ_filt → розрахунок похибки e", size=11, fill="#e0f2fe", stroke=NEG, pad=8)
    p.append(b3)

    p.append(arrow(620, 305, 620, 335, color=LINE, sw=1.5))

    b4, _, _ = textbox(620, 365, "4. Виконавчий привід (Серво / ШІМ)\nКомпенсаційний поворот: θ_act = -θ_base", size=11, fill="#dcfce7", stroke=FIELD, pad=8)
    p.append(b4)

    # Зворотний зв'язок стрілка вгору
    p.append(line(785, 365, 805, 365, color=FIELD, sw=1.4))
    p.append(line(805, 365, 805, 185, color=FIELD, sw=1.4))
    p.append(arrow(805, 185, 780, 185, color=FIELD, sw=1.4))
    p.append(text(800, 260, "Замикання горизонту", size=9, color=FIELD, anchor="end", italic=True))

    render(os.path.join(OUT, "gimbal-topology.svg"), W, H, *p)


# ── 2. complementary-filter-gimbal: Комплементарний фільтр у підвісі ──────────
def fig_complementary_filter():
    W, H = 840, 360
    p = []

    p.append(text(W / 2, 28, "Частотне розділення та злиття в комплементарному фільтрі", size=15, color=INK, bold=True))

    # Ліва колонка: Давачі
    b_gyro, _, _ = textbox(110, 100, "Гіроскоп (ω_x)\nКутова швидкість (°/с)\nШвидкий, без шуму, але ДРЕЙФУЄ", size=11, fill="#fee2e2", stroke=POS, pad=8)
    p.append(b_gyro)

    b_acc, _, _ = textbox(110, 240, "Акселерометр (a_y, a_z)\nВектор тяжіння g\nАбсолютний, але ШУМНИЙ у русі", size=11, fill="#e0f2fe", stroke=NEG, pad=8)
    p.append(b_acc)

    # Середня колонка: Обробка
    p.append(arrow(210, 100, 270, 100, color=POS, sw=1.6))
    b_int, _, _ = textbox(360, 100, "Дискретний інтегратор\nθ_pred = θ_prev + ω_x · Δt\n(Високочастотний тракт)", size=11, fill="#fff1f2", stroke=POS, pad=8)
    p.append(b_int)

    p.append(arrow(210, 240, 270, 240, color=NEG, sw=1.6))
    b_atan, _, _ = textbox(360, 240, "Розрахунок кута нахилу\nθ_acc = atan2(a_y, a_z)\n(Низькочастотний тракт)", size=11, fill="#f0f9ff", stroke=NEG, pad=8)
    p.append(b_atan)

    # Вагові коефіцієнти
    p.append(arrow(450, 100, 520, 140, color=POS, sw=1.6))
    p.append(text(475, 110, "вага α (0.98)", size=11, color=POS, bold=True))

    p.append(arrow(450, 240, 520, 180, color=NEG, sw=1.6))
    p.append(text(475, 225, "вага 1−α (0.02)", size=11, color=NEG, bold=True))

    # Суматор
    p.append(circle(545, 160, 20, fill="#fef08a", stroke=LINE, sw=2.0))
    p.append(text(545, 166, "+", size=20, color=LINE, bold=True))

    # Вихід
    p.append(arrow(565, 160, 650, 160, color=FIELD, sw=2.0))
    b_out, _, _ = textbox(735, 160, "Оцінка кута θ_filt\nБез дрейфу нуля\nБез тремтіння шуму", size=12, fill="#dcfce7", stroke=FIELD, pad=10)
    p.append(b_out)

    # Зворотний зв'язок інтегратора (в обхід блоків)
    p.append(line(735, 205, 735, 320, color=MUTED, sw=1.2, dash="4 3"))
    p.append(line(735, 320, 245, 320, color=MUTED, sw=1.2, dash="4 3"))
    p.append(line(245, 320, 245, 60, color=MUTED, sw=1.2, dash="4 3"))
    p.append(line(245, 60, 360, 60, color=MUTED, sw=1.2, dash="4 3"))
    p.append(arrow(360, 60, 360, 70, color=MUTED, sw=1.2))
    p.append(text(490, 335, "Повернення відфільтрованого кута на наступний такт (θ_prev)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "complementary-filter-gimbal.svg"), W, H, *p)


# ── 3. gimbal-control-loop: Повний контур ПІД-стабілізації ────────────────────
def fig_gimbal_control_loop():
    W, H = 880, 420
    p = []

    p.append(text(W / 2, 26, "Повна структура замкненого контуру стабілізації підвісу", size=15, color=INK, bold=True))

    # Задане значення Setpoint
    b_sp, _, _ = textbox(70, 170, "Уставка θ_target\n(0° горизонт)", size=11, fill="#f1f5f9", stroke=LINE, pad=8)
    p.append(b_sp)

    # Порівняльний елемент
    p.append(arrow(130, 170, 175, 170, color=LINE, sw=1.6))
    p.append(circle(190, 170, 14, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(text(190, 175, "Σ", size=14, color=LINE, bold=True))
    p.append(text(178, 160, "+", size=11, color=POS, bold=True))
    p.append(text(190, 198, "−", size=14, color=NEG, bold=True))

    p.append(arrow(204, 170, 245, 170, color=LINE, sw=1.6))
    p.append(text(225, 160, "e[k]", size=11, color=INK, italic=True))

    # Три гілки ПІД
    # P-гілка
    p.append(line(245, 170, 245, 75, color=LINE, sw=1.4))
    p.append(arrow(245, 75, 275, 75, color=LINE, sw=1.4))
    b_p, _, _ = textbox(360, 75, "П-ланка: P = K_p · e[k]\nМиттєва пружна реакція на помилку", size=10, fill="#fef3c7", stroke="#d97706", pad=6)
    p.append(b_p)

    # I-гілка з Anti-Windup
    p.append(arrow(245, 170, 275, 170, color=LINE, sw=1.4))
    b_i, _, _ = textbox(360, 170, "І-ланка: I += K_i · e[k] · Δt\n+ Clamping Anti-Windup (затискання)", size=10, fill="#dbeafe", stroke=NEG, pad=6)
    p.append(b_i)

    # D-гілка з ФНЧ
    p.append(line(245, 170, 245, 265, color=LINE, sw=1.4))
    p.append(arrow(245, 265, 275, 265, color=LINE, sw=1.4))
    b_d, _, _ = textbox(360, 265, "Д-ланка: D = -K_d · ω_gyro\n+ ФНЧ 1-го порядку (згладжування шуму)", size=10, fill="#fce7f3", stroke="#db2777", pad=6)
    p.append(b_d)

    # Зведення в суматор керування
    p.append(arrow(450, 75, 500, 155, color="#d97706", sw=1.4))
    p.append(arrow(450, 170, 485, 170, color=NEG, sw=1.4))
    p.append(arrow(450, 265, 500, 185, color="#db2777", sw=1.4))

    p.append(circle(505, 170, 16, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(text(505, 175, "Σ", size=15, color=LINE, bold=True))

    # Обмеження виходу (Limiter / Saturation)
    p.append(arrow(521, 170, 560, 170, color=LINE, sw=1.6))
    b_sat, _, _ = textbox(620, 170, "Насичення / ШІМ\n[1000…2000 мкс]\nОбмеження ходу", size=10, fill="#f1f5f9", stroke=MUTED, pad=6)
    p.append(b_sat)

    # Актюатор і підвіс
    p.append(arrow(680, 170, 720, 170, color=FIELD, sw=1.8))
    b_mech, _, _ = textbox(790, 170, "Сервопривід +\nПлатформа\nз корисним вантажем", size=11, fill="#dcfce7", stroke=FIELD, pad=8)
    p.append(b_mech)

    # Давач і фільтр у зворотному зв'язку
    p.append(line(790, 215, 790, 360, color=POS, sw=1.6))
    p.append(arrow(790, 360, 560, 360, color=POS, sw=1.6))
    b_sens, _, _ = textbox(440, 360, "IMU (акселерометр + гіроскоп) → Комплементарний фільтр (θ_filt)", size=11, fill="#fee2e2", stroke=POS, pad=8)
    p.append(b_sens)

    p.append(line(320, 360, 190, 360, color=POS, sw=1.6))
    p.append(arrow(190, 360, 190, 188, color=POS, sw=1.6))
    p.append(text(175, 280, "θ_filt", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "gimbal-control-loop.svg"), W, H, *p)


# ── 4. anti-windup-clamping: Насичення інтегратора та Clamping ─────────────────
def fig_anti_windup():
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Динаміка регулятора при насиченні: без захисту проти Clamping Anti-Windup", size=14, color=INK, bold=True))

    # Лівий графік: БЕЗ Anti-Windup
    p.append(rect(30, 50, 375, 305, fill="#fffafb", stroke=POS, sw=1.2, rx=6))
    p.append(text(217, 75, "Без Anti-Windup (катастрофічний Windup)", size=12, color=POS, bold=True))

    # Вісі лівого графіка
    p.append(arrow(55, 310, 380, 310, color=LINE, sw=1.2))  # t
    p.append(arrow(55, 310, 55, 95, color=LINE, sw=1.2))    # output
    p.append(text(375, 325, "час t", size=10, color=MUTED, italic=True))
    p.append(text(45, 95, "u(t)", size=11, color=LINE, bold=True, italic=True))

    # Рівень насичення u_max
    p.append(line(55, 140, 375, 140, color=MUTED, sw=1.0, dash="4 3"))
    p.append(text(240, 132, "Межа насичення приводу u_max", size=9, color=MUTED))

    # Крива інтегратора (йде далеко вгору)
    p.append('<path d="M 55,310 Q 110,240 140,140 Q 180,60 230,60 Q 270,60 300,140 Q 325,230 350,305" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % POS)
    p.append(text(190, 75, "I-терм роздувається", size=10, color=POS, bold=True))

    # Реальний вихід (застряг на насиченні, потім величезний провал)
    p.append('<path d="M 55,310 Q 110,240 140,140 L 300,140 Q 325,230 350,305" fill="none" stroke="%s" stroke-width="2.6"/>' % LINE)
    p.append(text(210, 160, "Вихід застряг на максимумі", size=10, color=LINE))
    p.append(text(290, 230, "Запізнілий відгук\nі переліт (overshoot)", size=10, color=POS, bold=True))

    # Правий графік: З Clamping Anti-Windup
    p.append(rect(435, 50, 375, 305, fill="#f7fef9", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(622, 75, "Із захистом Clamping Anti-Windup", size=12, color=FIELD, bold=True))

    # Вісі правого графіка
    p.append(arrow(460, 310, 785, 310, color=LINE, sw=1.2))  # t
    p.append(arrow(460, 310, 460, 95, color=LINE, sw=1.2))    # output
    p.append(text(780, 325, "час t", size=10, color=MUTED, italic=True))
    p.append(text(450, 95, "u(t)", size=11, color=LINE, bold=True, italic=True))

    # Рівень насичення u_max
    p.append(line(460, 140, 780, 140, color=MUTED, sw=1.0, dash="4 3"))
    p.append(text(645, 132, "Межа насичення приводу u_max", size=9, color=MUTED))

    # Крива з Clamping: не роздувається вище межі
    p.append('<path d="M 460,310 Q 515,240 545,140 L 630,140 Q 660,200 690,290 L 730,305" fill="none" stroke="%s" stroke-width="2.6"/>' % FIELD)
    p.append(text(595, 115, "Інтегратор заморожено (Clamped)", size=10, color=FIELD, bold=True))
    p.append(text(670, 210, "Миттєвий вихід\nіз насичення", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "anti-windup-clamping.svg"), W, H, *p)


if __name__ == "__main__":
    fig_gimbal_topology()
    fig_complementary_filter()
    fig_gimbal_control_loop()
    fig_anti_windup()
    print("Всі 4 фігури згенеровано успішно.")
