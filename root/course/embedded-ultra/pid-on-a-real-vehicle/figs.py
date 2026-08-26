# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. cascade-control-loops: Двоконтурна каскадна архітектура ────────────────
def fig_cascade_control_loops():
    W, H = 980, 520
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Каскадний контур стабілізації квадрокоптера: Angle Loop та Rate Loop", size=16, color=INK, bold=True))

    # Зона 1: Зовнішній контур кута (Angle Loop, 250–500 Гц)
    frags.append(rect(30, 55, 230, 425, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(145, 80, "ЗОВНІШНІЙ КОНТУР (ANGLE)", size=13, color=FIELD, bold=True))
    frags.append(text(145, 98, "Частота оновлення: 250–500 Гц", size=11, color=MUTED))

    # Зона 2: Внутрішній контур кутової швидкості (Rate Loop, 1–8 кГц)
    frags.append(rect(280, 55, 410, 425, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(485, 80, "ВНУТРІШНІЙ КОНТУР (RATE)", size=13, color=NEG, bold=True))
    frags.append(text(485, 98, "Частота оновлення: 1–8 кГц (по DRDY гіроскопа)", size=11, color=MUTED))

    # Зона 3: Виконавчий рівень (Mixer, ESC, Motors, Dynamics)
    frags.append(rect(710, 55, 240, 425, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(830, 80, "СИЛОВИЙ ТРАКТ І ФІЗИКА", size=13, color=POS, bold=True))
    frags.append(text(830, 98, "Матриця мікшування та мотори", size=11, color=MUTED))

    # Блоки всередині Angle Loop
    # Суматор похибки кута
    frags.append(circle(65, 170, 14, fill="#ffffff", stroke=FIELD, sw=2))
    frags.append(text(65, 175, "Σ", size=15, color=FIELD, bold=True))
    frags.append(text(42, 145, "θ_sp", size=12, color=INK, bold=True))
    frags.append(arrow(10, 170, 49, 170, color=FIELD, sw=1.8))

    # Angle P/PI Controller Box
    b_ang = fitbox(105, 140, 135, 60, "Angle Controller\n(P / PI-ланка)\ne_θ = θ_sp − θ", size=12, fill="#ffffff", stroke=FIELD, bold=True)
    frags.append(b_ang)
    frags.append(arrow(80, 170, 103, 170, color=FIELD, sw=1.8))

    # Блоки всередині Rate Loop
    # Суматор похибки швидкості
    frags.append(circle(315, 170, 14, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(315, 175, "Σ", size=15, color=NEG, bold=True))
    frags.append(arrow(242, 170, 299, 170, color=FIELD, sw=1.8))
    frags.append(text(270, 160, "ω_sp", size=11, color=FIELD, bold=True))

    # Прямий зв'язок (Feedforward)
    frags.append(rect(345, 105, 110, 36, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(400, 127, "Feedforward (FF)", size=11, color=MUTED, bold=True))
    frags.append(line(265, 170, 265, 123, color=MUTED, sw=1.5))
    frags.append(arrow(265, 123, 343, 123, color=MUTED, sw=1.5))

    # Rate PID Blocks
    # P-term
    frags.append(rect(355, 152, 90, 34, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(400, 174, "P: K_p · e_ω", size=11, color=NEG, bold=True))
    frags.append(arrow(330, 170, 353, 169, color=NEG, sw=1.5))

    # I-term + Anti-Windup
    frags.append(rect(355, 196, 90, 38, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(400, 212, "I: ∫ e_ω dt", size=11, color=NEG, bold=True))
    frags.append(text(400, 226, "Anti-Windup", size=9, color=POS, bold=True))
    frags.append(line(340, 170, 340, 215, color=NEG, sw=1.5))
    frags.append(arrow(340, 215, 353, 215, color=NEG, sw=1.5))

    # D-term + Filter
    frags.append(rect(355, 244, 90, 42, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(400, 260, "D: −K_d · dω/dt", size=10.5, color=NEG, bold=True))
    frags.append(text(400, 276, "PT1 / Biquad", size=9.5, color=FIELD, bold=True))

    # PID Summing point
    frags.append(circle(480, 170, 14, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(480, 175, "Σ", size=15, color=NEG, bold=True))
    frags.append(arrow(447, 169, 464, 170, color=NEG, sw=1.5))
    frags.append(arrow(447, 215, 474, 182, color=NEG, sw=1.5))
    frags.append(arrow(447, 265, 474, 182, color=NEG, sw=1.5))
    frags.append(arrow(457, 123, 474, 158, color=MUTED, sw=1.5))

    # Output Clamping & Saturation Limits
    frags.append(rect(515, 145, 155, 52, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(592, 166, "Обмеження моменту", size=11, color=INK, bold=True))
    frags.append(text(592, 183, "Sat: [−U_max, +U_max]", size=10, color=MUTED))
    frags.append(arrow(496, 170, 513, 170, color=NEG, sw=1.8))

    # Зворотний зв'язок Anti-Windup до I-term
    frags.append(line(592, 199, 592, 230, color=POS, sw=1.3, dash="4,3"))
    frags.append(line(592, 230, 447, 230, color=POS, sw=1.3, dash="4,3"))
    frags.append(arrow(447, 230, 447, 222, color=POS, sw=1.3))
    frags.append(text(520, 242, "зворотний зв'язок насичення", size=9, color=POS))

    # Зона 3: Мікшер та Мотори
    frags.append(rect(725, 135, 210, 68, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(830, 157, "Матриця мікшування (Mixer)", size=12, color=POS, bold=True))
    frags.append(text(830, 175, "M_i = Throttle ± Roll ± Pitch ± Yaw", size=10, color=INK))
    frags.append(text(830, 192, "Пріоритет стабілізації (Air Mode)", size=9.5, color=MUTED))
    frags.append(arrow(672, 170, 723, 170, color=NEG, sw=1.8))
    frags.append(text(697, 160, "U_axis", size=10, color=NEG, bold=True))

    # ESCs & Motors Box
    frags.append(rect(735, 230, 190, 55, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(830, 252, "4× ESC + BLDC Мотори", size=12, color=INK, bold=True))
    frags.append(text(830, 271, "DShot / PWM протокол (тяги T1..T4)", size=10, color=MUTED))
    frags.append(arrow(830, 205, 830, 228, color=POS, sw=1.8))

    # Фізичне тіло квадрокоптера
    frags.append(rect(735, 315, 190, 60, fill="#ffffff", stroke=LINE, sw=2, rx=6))
    frags.append(text(830, 338, "Динаміка рами апарата", size=12, color=INK, bold=True))
    frags.append(text(830, 355, "Моменти інерції I_xx, I_yy, I_zz", size=10, color=MUTED))
    frags.append(text(830, 368, "τ = I · dω/dt", size=10, color=INK))
    frags.append(arrow(830, 287, 830, 313, color=POS, sw=1.8))

    # Сенсорний зворотний зв'язок
    # Гіроскоп (IMU Gyro)
    frags.append(rect(470, 395, 160, 55, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(550, 417, "MEMS Гіроскоп (IMU)", size=11, color=NEG, bold=True))
    frags.append(text(550, 435, "Кутова швидкість ω (1–8 кГц)", size=10, color=MUTED))

    # Оцінювач орієнтації (Attitude Estimator)
    frags.append(rect(100, 395, 160, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(180, 417, "Оцінка орієнтації", size=11, color=FIELD, bold=True))
    frags.append(text(180, 435, "Кут орієнтації θ (250–500 Гц)", size=10, color=MUTED))

    # Лінії зворотного зв'язку
    # Від фізики до гіроскопа
    frags.append(line(830, 377, 830, 422, color=LINE, sw=1.5))
    frags.append(arrow(830, 422, 632, 422, color=NEG, sw=1.8))

    # Від гіроскопа до Rate Loop суматора і до D-term
    frags.append(line(550, 393, 550, 310, color=NEG, sw=1.5))
    frags.append(line(550, 310, 315, 310, color=NEG, sw=1.5))
    frags.append(arrow(315, 310, 315, 186, color=NEG, sw=1.8))
    frags.append(text(328, 205, "−", size=14, color=NEG, bold=True))
    frags.append(text(330, 298, "ω_meas", size=10, color=NEG, bold=True))

    # Від гіроскопа до фільтра D-term
    frags.append(line(468, 310, 468, 265, color=NEG, sw=1.3))
    frags.append(arrow(468, 265, 447, 265, color=NEG, sw=1.3))

    # Від гіроскопа до Attitude Estimator
    frags.append(arrow(468, 422, 262, 422, color=FIELD, sw=1.8))
    frags.append(text(360, 414, "ω + Акселерометр", size=9.5, color=FIELD))

    # Від Attitude Estimator до Angle Loop суматора
    frags.append(line(180, 393, 180, 240, color=FIELD, sw=1.5))
    frags.append(line(180, 240, 65, 240, color=FIELD, sw=1.5))
    frags.append(arrow(65, 240, 65, 186, color=FIELD, sw=1.8))
    frags.append(text(78, 205, "−", size=14, color=FIELD, bold=True))
    frags.append(text(80, 230, "θ_meas", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "cascade-control-loops.svg"), W, H, *frags)


# ── 2. dterm-filtering: Шум диференціювання та каскад фільтрації ──────────────
def fig_dterm_filtering():
    W, H = 960, 460
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Диференціювання та фільтрація D-ланки: від сирого шуму до чистого демпфування", size=15, color=INK, bold=True))

    # Ліва панель: Частотний спектр шуму гіроскопа та АЧХ фільтрів
    frags.append(rect(30, 55, 430, 385, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(245, 80, "Частотна область: Спектр вібрацій та фільтри", size=13, color=INK, bold=True))

    # Осі графіка АЧХ
    frags.append(line(60, 380, 430, 380, color=LINE, sw=1.5))  # вісь X (частота)
    frags.append(line(60, 380, 60, 110, color=LINE, sw=1.5))   # вісь Y (амплітуда)
    frags.append(text(430, 400, "Частота f (Гц)", size=11, color=MUTED, anchor="end"))
    frags.append(text(50, 115, "|H(f)|", size=11, color=MUTED, anchor="end"))

    # Позначки частот на осі
    frags.append(text(100, 396, "20", size=10, color=MUTED))
    frags.append(text(160, 396, "80", size=10, color=MUTED))
    frags.append(text(250, 396, "200 (мотори)", size=10, color=POS))
    frags.append(text(370, 396, "500+", size=10, color=MUTED))

    # Корисна зона керування
    frags.append(rect(60, 130, 80, 250, fill="#dcfce7", stroke="none"))
    frags.append(mtext(100, 150, ["Корисний рух", "(0–30 Гц)"], size=10, color=FIELD, bold=True))

    # Зона вібрацій моторів
    frags.append(rect(200, 130, 100, 250, fill="#fee2e2", stroke="none"))
    frags.append(mtext(250, 150, ["Резонанс гвинтів", "(150–300 Гц)"], size=10, color=POS, bold=True))

    # Крива PT1 ФНЧ (Low-Pass Filter)
    frags.append(text(175, 230, "PT1 ФНЧ (f_c = 80 Гц)", size=10.5, color=FIELD, bold=True))
    frags.append(line(60, 180, 160, 185, color=FIELD, sw=2.2))
    frags.append(line(160, 185, 220, 230, color=FIELD, sw=2.2))
    frags.append(line(220, 230, 410, 340, color=FIELD, sw=2.2))

    # Крива Biquad Notch Filter (Режекторний фільтр)
    frags.append(text(285, 275, "Notch-фільтр", size=10.5, color=NEG, bold=True))
    frags.append(line(60, 200, 210, 200, color=NEG, sw=2, dash="4,2"))
    frags.append(line(210, 200, 250, 360, color=NEG, sw=2, dash="4,2"))
    frags.append(line(250, 360, 290, 200, color=NEG, sw=2, dash="4,2"))
    frags.append(line(290, 200, 410, 200, color=NEG, sw=2, dash="4,2"))

    # Права панель: Часові сигнали та небезпека диференціювання
    frags.append(rect(490, 55, 440, 385, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(710, 80, "Часова область: Еволюція сигналу D-ланки", size=13, color=INK, bold=True))

    # Блок 1: Сирий вимір гіроскопа (мікро-коливання)
    frags.append(rect(510, 100, 400, 65, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(525, 120, "1. Сирий гіроскоп ω (з шумом підшипників та рами)", size=10.5, color=INK, bold=True, anchor="start"))
    # Лінія сигналу з дрібним шумом
    frags.append(line(525, 145, 600, 145, color=INK, sw=1.5))
    frags.append(line(600, 145, 640, 133, color=INK, sw=1.5))
    frags.append(line(640, 133, 720, 155, color=INK, sw=1.5))
    frags.append(line(720, 155, 800, 140, color=INK, sw=1.5))
    frags.append(line(800, 140, 890, 145, color=INK, sw=1.5))

    # Блок 2: Нефільтрована похідна dω/dt (катастрофічний шум)
    frags.append(rect(510, 175, 400, 85, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(525, 195, "2. Нефільтрована D-ланка: −K_d · Δω / Δt", size=10.5, color=POS, bold=True, anchor="start"))
    frags.append(text(525, 210, "Високочастотний шум підсилюється у сотні разів → нагрів моторів", size=9.5, color=POS, anchor="start"))
    # Сильно зашумлений пилкоподібний графік
    noise_pts = [(525, 240), (540, 222), (555, 255), (570, 220), (585, 258), (600, 218),
                 (615, 260), (630, 225), (645, 255), (660, 220), (675, 258), (690, 218),
                 (720, 262), (750, 220), (780, 258), (810, 222), (840, 258), (890, 240)]
    for i in range(len(noise_pts) - 1):
        frags.append(line(noise_pts[i][0], noise_pts[i][1], noise_pts[i+1][0], noise_pts[i+1][1], color=POS, sw=1.5))

    # Блок 3: Фільтрована D-ланка (PT1 + Dynamic Notch)
    frags.append(rect(510, 270, 400, 80, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(525, 290, "3. Фільтрована D-ланка: PT1 + Biquad Notch", size=10.5, color=FIELD, bold=True, anchor="start"))
    frags.append(text(525, 305, "Чистий демпфувальний сигнал без перегріву ESC та обмоток", size=9.5, color=FIELD, anchor="start"))
    # Плавна синусоїда демпфування
    frags.append(line(525, 335, 600, 335, color=FIELD, sw=2.2))
    frags.append(line(600, 335, 650, 318, color=FIELD, sw=2.2))
    frags.append(line(650, 318, 730, 348, color=FIELD, sw=2.2))
    frags.append(line(730, 348, 810, 330, color=FIELD, sw=2.2))
    frags.append(line(810, 330, 890, 335, color=FIELD, sw=2.2))

    # Підсумковий висновок внизу
    frags.append(fitbox(510, 360, 400, 65, "D-on-Measurement замість D-on-Error:\nпохідна береться від виміру гіроскопа (−K_d · dω/dt),\nщо виключає 'D-kick' при стрибку завдання зі стіка пілота.", size=10, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, "dterm-filtering.svg"), W, H, *frags)


# ── 3. anti-windup-behavior: Насичення інтегратора та методи Anti-Windup ───────
def fig_anti_windup_behavior():
    W, H = 960, 490
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Насичення інтегратора (Windup) та динамічне відновлення керування", size=15, color=INK, bold=True))

    # Ліва панель: БЕЗ Anti-Windup (катастрофічний переліт і запізнення)
    frags.append(rect(30, 55, 430, 415, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    frags.append(text(245, 80, "БЕЗ Anti-Windup: Накопичення помилки", size=13, color=POS, bold=True))
    frags.append(text(245, 98, "Дрон заблоковано рукою або в траві під час зльоту", size=10.5, color=MUTED))

    # Графік ліворуч
    frags.append(line(60, 240, 430, 240, color=LINE, sw=1.2))  # вісь часу
    frags.append(line(60, 360, 60, 120, color=LINE, sw=1.2))   # вісь величини

    # Рівні обмеження мотора
    frags.append(line(60, 150, 430, 150, color=POS, sw=1.2, dash="4,3"))
    frags.append(text(420, 142, "U_max (100% газу)", size=9.5, color=POS, anchor="end"))

    # Крива I-term (росте нескінченно вгору)
    frags.append(line(60, 240, 140, 240, color=POS, sw=2))
    frags.append(line(140, 240, 260, 115, color=POS, sw=2.5))  # росте вище даху
    frags.append(line(260, 115, 340, 170, color=POS, sw=2))
    frags.append(line(340, 170, 420, 240, color=POS, sw=2))
    frags.append(text(230, 128, "Намотаний інтеграл I >> U_max", size=10, color=POS, bold=True))

    # Зона блокування
    frags.append(rect(140, 150, 120, 190, fill="#fee2e2", stroke="none"))
    frags.append(mtext(200, 275, ["Апарат утримується", "(похибка не зникає)"], size=10, color=POS))

    # Зона запізнілого розряду
    frags.append(rect(260, 150, 80, 190, fill="#fef3c7", stroke="none"))
    frags.append(mtext(300, 310, ["Затримка розряду", "(Overshoot)"], size=9.5, color="#b45309"))

    frags.append(fitbox(45, 375, 400, 80, "Наслідок: після звільнення дрон робить різкий кульбіт\nі врізається в землю через гігантський накопичений I.", size=10.5, fill="#ffffff", stroke=POS, color=POS, bold=True))

    # Права панель: З Anti-Windup (Clamping / Conditional Integration)
    frags.append(rect(490, 55, 440, 415, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(710, 80, "З Anti-Windup: Затискання та миттєва реакція", size=13, color=FIELD, bold=True))
    frags.append(text(710, 98, "Інтегратор заморожується на межі насичення мотора", size=10.5, color=MUTED))

    # Графік праворуч
    frags.append(line(520, 240, 890, 240, color=LINE, sw=1.2))  # вісь часу
    frags.append(line(520, 360, 520, 120, color=LINE, sw=1.2))   # вісь величини

    # Рівні обмеження
    frags.append(line(520, 150, 890, 150, color=FIELD, sw=1.2, dash="4,3"))
    frags.append(text(880, 142, "U_max (100% газу)", size=9.5, color=FIELD, anchor="end"))

    # Крива I-term (обмежена)
    frags.append(line(520, 240, 600, 240, color=FIELD, sw=2))
    frags.append(line(600, 240, 660, 150, color=FIELD, sw=2.5))
    frags.append(line(660, 150, 720, 150, color=FIELD, sw=2.5))  # плато на межі
    frags.append(line(720, 150, 770, 240, color=FIELD, sw=2.5))  # миттєвий спад
    frags.append(line(770, 240, 880, 240, color=FIELD, sw=2))

    frags.append(text(690, 135, "I_term затиснуто (Clamped)", size=10, color=FIELD, bold=True))

    # Зона блокування
    frags.append(rect(600, 150, 120, 190, fill="#e0f2fe", stroke="none"))
    frags.append(mtext(660, 275, ["Апарат утримується", "(I не росте вище ліміту)"], size=10, color=NEG))

    # Миттєве повернення
    frags.append(line(720, 120, 720, 340, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(mtext(765, 310, ["Миттєве відновлення", "(без кульбіту)"], size=9.5, color=FIELD, bold=True))

    frags.append(fitbox(505, 375, 410, 80, "Механізм: якщо вихід регулятора досяг ліміту,\nінтегрування похибки цього знаку примусово зупиняється.", size=10.5, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "anti-windup-behavior.svg"), W, H, *frags)


# ── 4. quad-x-mixer: Геометрія та матриця мікшування квадрокоптера X ──────────
def fig_quad_x_mixer():
    W, H = 960, 520
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Матриця мікшування квадрокоптера (X-конфігурація): Розподіл зусиль Roll, Pitch, Yaw", size=15, color=INK, bold=True))

    # Ліва частина: Схема квадрокоптера зверху
    frags.append(rect(30, 55, 410, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(235, 80, "Геометрія рами Quad-X (Вигляд зверху)", size=13, color=INK, bold=True))

    # Центр дрона
    cx, cy = 235, 265

    # Стрілка напрямку "НІС АПАРАТА"
    frags.append(arrow(cx, cy - 30, cx, cy - 130, color=POS, sw=2.5))
    frags.append(text(cx, cy - 140, "НІС (ВПЕРЕД / +PITCH)", size=11, color=POS, bold=True))

    # Промені рами (X-подібні)
    frags.append(line(cx - 100, cy - 100, cx + 100, cy + 100, color=LINE, sw=4))
    frags.append(line(cx - 100, cy + 100, cx + 100, cy - 100, color=LINE, sw=4))

    # Центральний польотний контролер
    frags.append(rect(cx - 28, cy - 28, 56, 56, fill="#ffffff", stroke=LINE, sw=2, rx=4))
    frags.append(text(cx, cy + 4, "FC", size=13, color=FIELD, bold=True))

    # Мотори
    motors = [
        # (номер, назва, x, y, колір, обертання, реактивний момент)
        ("M4", "Front-Left", cx - 100, cy - 100, "#dcfce7", "CW", "Реакція: +Yaw"),
        ("M2", "Front-Right", cx + 100, cy - 100, "#fee2e2", "CCW", "Реакція: −Yaw"),
        ("M3", "Rear-Left", cx - 100, cy + 100, "#fee2e2", "CCW", "Реакція: −Yaw"),
        ("M1", "Rear-Right", cx + 100, cy + 100, "#dcfce7", "CW", "Реакція: +Yaw"),
    ]

    for name, pos_name, mx, my, col, rot, yaw_eff in motors:
        frags.append(circle(mx, my, 32, fill=col, stroke=LINE, sw=2))
        frags.append(text(mx, my - 6, name, size=13, color=INK, bold=True))
        frags.append(text(mx, my + 10, rot, size=11, color=POS if rot == "CW" else NEG, bold=True))
        frags.append(text(mx, my + (24 if my > cy else -40), pos_name, size=9.5, color=MUTED))

    # Права частина: Матриця та рівняння мікшування
    frags.append(rect(460, 55, 470, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(695, 80, "Рівняння мікшування тяги та моментів", size=13, color=INK, bold=True))

    eq_boxes = [
        ("Мотор 1 (Rear-Right, CW)", "M1 = Throttle − Roll + Pitch + Yaw", "Зменшує крен праворуч, піднімає хвіст, крутить ніс вправо"),
        ("Мотор 2 (Front-Right, CCW)", "M2 = Throttle − Roll − Pitch − Yaw", "Зменшує крен праворуч, опускає ніс, крутить ніс вліво"),
        ("Мотор 3 (Rear-Left, CCW)", "M3 = Throttle + Roll + Pitch − Yaw", "Піднімає лівий борт, піднімає хвіст, крутить ніс вліво"),
        ("Мотор 4 (Front-Left, CW)", "M4 = Throttle + Roll − Pitch + Yaw", "Піднімає лівий борт, опускає ніс, крутить ніс вправо"),
    ]

    cur_y = 105
    for m_title, formula, desc in eq_boxes:
        frags.append(rect(480, cur_y, 430, 68, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        frags.append(text(495, cur_y + 20, m_title, size=11.5, color=INK, bold=True, anchor="start"))
        frags.append(text(495, cur_y + 40, formula, size=12, color=NEG, bold=True, anchor="start"))
        frags.append(text(495, cur_y + 58, desc, size=9.5, color=MUTED, anchor="start"))
        cur_y += 76

    # Блок пріоритету Air Mode
    frags.append(rect(480, cur_y + 5, 430, 65, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(695, cur_y + 26, "Air Mode & Dynamic Range Scaling", size=11.5, color=NEG, bold=True))
    frags.append(mtext(695, cur_y + 45, ["Якщо M_max > 1.0 або M_min < 0.0, загальний Throttle зсувається,", "щоб зберегти 100% керівних моментів стабілізації."], size=9.5, color=INK))

    render(os.path.join(OUT, "quad-x-mixer.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_cascade_control_loops()
    fig_dterm_filtering()
    fig_anti_windup_behavior()
    fig_quad_x_mixer()
    print("Всі 4 фігури згенеровано успішно.")
