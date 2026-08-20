# -*- coding: utf-8 -*-
"""Фігури до теми «Адаптивні ліміти конкурентності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # перевантаження / відмова / небезпека
COOL = "#eaf0fd"   # нейтральне / схема
GOOD = "#e8f6ee"   # корисна робота / успіх
ACCENT = "#fbf4db" # попередження / проміжний стан


# ── 1. Зв'язок конкурентності, пропускної здатності та затримки (The Knee and the Cliff) ──
def latency_throughput_knee():
    W, H = 1180, 700
    f = []

    xa, xb = 140.0, 1100.0
    ya_t, yb_t = 100.0, 340.0  # Верхній графік: Пропускна здатність
    ya_l, yb_l = 440.0, 620.0  # Нижній графік: Затримка

    # Точка зламу (The Knee)
    x_knee = 520.0

    # Зони фону
    f.append(rect(xa, 70, x_knee - xa, 560, fill="#f8fafc", stroke="none"))
    f.append(rect(x_knee, 70, xb - x_knee, 560, fill="#fef8f8", stroke="none"))

    f.append(text((xa + x_knee) / 2, 90, "Зона недовантаження (вільні ресурси)", size=13, color=FIELD, bold=True))
    f.append(text((x_knee + xb) / 2, 90, "Зона черг та деградації (перевантаження)", size=13, color=POS, bold=True))

    # Розділювальна лінія між зонами
    f.append(line(x_knee, 70, x_knee, 630, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(x_knee, 648, "Оптимальна точка (The Knee): L_opt = λ_max · RTT_min", size=12.5, color=INK, bold=True))

    # --- Верхній графік: Throughput (RPS) ---
    f.append(line(xa, yb_t, xb, yb_t, color=INK, sw=2.0))
    f.append(line(xa, ya_t, xa, yb_t, color=INK, sw=2.0))
    f.append(text(xa - 14, ya_t + 10, "Пропускна здатність λ (RPS)", size=13, color=INK, anchor="end", bold=True))

    # Крива пропускної здатності: зростання до Knee, потім плато
    y_t_max = 140.0
    f.append(line(xa, yb_t, x_knee, y_t_max, color=FIELD, sw=3.5))
    f.append(line(x_knee, y_t_max, xb - 40, y_t_max, color=FIELD, sw=3.5))
    f.append(circle(x_knee, y_t_max, 6, fill=GOOD, stroke=FIELD, sw=2.5))
    f.append(text(x_knee + 15, y_t_max - 12, "Максимум системи (μ = λ_max)", size=12, color=FIELD, anchor="start", bold=True))

    # --- Нижній графік: Latency (RTT) ---
    f.append(line(xa, yb_l, xb, yb_l, color=INK, sw=2.0))
    f.append(line(xa, ya_l, xa, yb_l, color=INK, sw=2.0))
    f.append(text(xa - 14, ya_l + 10, "Час відповіді RTT (мс)", size=13, color=INK, anchor="end", bold=True))
    f.append(text(xb, yb_l + 25, "Паралелізм (In-flight requests L) →", size=13, color=INK, anchor="end", bold=True))

    # Крива затримки: стабільна на рівні RTT_min, після Knee зростає лінійно через чергу
    y_l_min = 580.0
    y_l_max = 460.0
    f.append(line(xa, y_l_min, x_knee, y_l_min, color=NEG, sw=3.5))
    f.append(line(x_knee, y_l_min, xb - 40, y_l_max, color=POS, sw=3.5))
    f.append(circle(x_knee, y_l_min, 6, fill=COOL, stroke=NEG, sw=2.5))
    f.append(text(xa + 20, y_l_min - 12, "Базова затримка без черг (RTT_min)", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(xb - 50, y_l_max - 12, "Зростання черги очікування (The Cliff)", size=12, color=POS, anchor="end", bold=True))

    # Пояснювальні плашки
    f.append(fitbox(170, 160, 290, 68,
                    "До Knee:\nкожен новий потік збільшує throughput,\nзатримка не змінюється",
                    size=12, bold=False, fill=GOOD, stroke=FIELD, sw=1.5))

    f.append(fitbox(700, 160, 360, 68,
                    "Після Knee:\nресурси вичерпано, throughput не росте,\nвесь додатковий паралелізм іде в затримку черги",
                    size=12, bold=False, fill=WARM, stroke=POS, sw=1.5))

    render(os.path.join(OUT, 'latency-throughput-knee.svg'), W, H, *f)


# ── 2. Контур зворотного зв'язку адаптивного лімітера (Vegas / Gradient Loop) ──
def vegas_gradient_feedback():
    W, H = 1200, 700
    f = []

    # Блок 1: Вхідний запит
    f.append(fitbox(60, 290, 160, 80, "Вхідний RPC-запит\n(Request Arrival)", size=13, bold=True, fill=FILL, stroke=LINE, sw=1.8))
    f.append(arrow(220, 330, 270, 330, color=LINE, sw=2.0))

    # Блок 2: Перевірка допуску
    f.append(fitbox(270, 280, 220, 100, "Перевірка допуску:\nin_flight < Limit?", size=13.5, bold=True, fill=COOL, stroke=NEG, sw=2.0))

    # Гілка відмови (Вниз)
    f.append(arrow(380, 380, 380, 520, color=POS, sw=2.0))
    f.append(text(395, 450, "Ні (переповнено)", size=12, color=POS, bold=True, anchor="start"))
    f.append(fitbox(280, 520, 200, 80, "Швидке скидання:\nHTTP 429 / 503\n(0 затрат ресурсів)", size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    # Гілка успішного пропуску (Вправо)
    f.append(arrow(490, 330, 560, 330, color=FIELD, sw=2.0))
    f.append(text(525, 320, "Так", size=12, color=FIELD, bold=True, anchor="middle"))

    # Блок 3: Виконання запиту
    f.append(fitbox(560, 280, 210, 100, "Обробка запиту\n(Сервіс / База даних)\nФіксація t_start, t_end", size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2.0))
    f.append(arrow(770, 330, 830, 330, color=LINE, sw=2.0))

    # Блок 4: Відповідь клієнту
    f.append(fitbox(830, 290, 150, 80, "Успішна відповідь\nклієнту", size=13, bold=True, fill=FILL, stroke=LINE, sw=1.8))

    # Контур телеметрії (Вгору від виконання)
    f.append(line(665, 280, 665, 140, color=LINE, sw=1.8))
    f.append(arrow(665, 140, 720, 140, color=LINE, sw=1.8))
    f.append(text(675, 200, "Телеметрія RTT", size=12, color=MUTED, bold=True, anchor="start"))

    # Блок 5: Оновлення метрик вікна
    f.append(fitbox(720, 90, 220, 100, "Вікно вимірювань:\nminRTT = min(RTT_i)\nsampleRTT = avg(RTT_i)", size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    f.append(arrow(940, 140, 990, 140, color=LINE, sw=1.8))

    # Блок 6: Розрахунок градієнта та оновлення Limit
    f.append(fitbox(990, 80, 180, 120, "Градієнт затримки:\ng = minRTT / sampleRTT\n\nLimit_new =\nLimit · g + headroom", size=12, bold=True, fill=ACCENT, stroke="#b45309", sw=2.0))

    # Зворотна петля на блок перевірки допуску
    f.append(line(1080, 200, 1080, 240, color="#b45309", sw=1.8))
    f.append(line(1080, 240, 380, 240, color="#b45309", sw=1.8))
    f.append(arrow(380, 240, 380, 280, color="#b45309", sw=2.0))
    f.append(text(730, 230, "Динамічне оновлення ліміту паралелізму Limit", size=12, color="#b45309", bold=True, anchor="middle"))

    # Підсумкова плашка знизу
    f.append(fitbox(100, 620, 1000, 60,
                    "Автоматичний гомеостаз: якщо sampleRTT росте через черги, g < 1 і ліміт звужується;\n"
                    "якщо затримка повертається до норми, g ≈ 1 і ліміт плавно розширюється за рахунок headroom.",
                    size=12.5, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'vegas-gradient-feedback.svg'), W, H, *f)


# ── 3. Дрейф базової затримки та вікно скидання minRTT ──────────────────────
def min_rtt_drift_reset():
    W, H = 1180, 600
    f = []

    xa, xb = 120.0, 1080.0
    ya, yb = 100.0, 480.0

    # Осі координат
    f.append(line(xa, yb, xb, yb, color=INK, sw=2.0))
    f.append(line(xa, ya, xa, yb, color=INK, sw=2.0))
    f.append(text(xb, yb + 35, "Час (хвилини) →", size=13, color=INK, anchor="end", bold=True))
    f.append(text(xa - 14, ya - 15, "Затримка RTT (мс)", size=13, color=INK, anchor="start", bold=True))

    # Вікно 1: Нормальний стан (minRTT = 20 мс)
    f.append(line(xa, 400, 480, 400, color=NEG, sw=2.5, dash="6,4"))
    f.append(text(xa + 20, 390, "Старий minRTT = 20 мс", size=12, color=NEG, bold=True))

    # Подія деградації в точці t = 480
    f.append(line(480, ya, 480, yb, color=POS, sw=1.5, dash="4,4"))
    f.append(text(480, ya + 20, "Справжня зміна середовища:\nхолодний кеш / міграція в інший ДЦ", size=11.5, color=POS, bold=True, anchor="middle"))

    # Новий базовий рівень (minRTT = 50 мс)
    f.append(line(480, 300, xb - 40, 300, color=FIELD, sw=2.5, dash="6,4"))
    f.append(text(780, 290, "Новий реальний minRTT = 50 мс", size=12, color=FIELD, bold=True))

    # Реальні вимірювання (sampleRTT): коливання навколо 20мс, потім стрибок до 50мс+
    pts_sample = [
        (xa, 395), (180, 405), (240, 390), (320, 410), (400, 395), (460, 400),
        (490, 280), (540, 295), (600, 285), (680, 310), (760, 290), (840, 305), (920, 295), (xb - 40, 300)
    ]
    for i in range(len(pts_sample) - 1):
        f.append(line(pts_sample[i][0], pts_sample[i][1], pts_sample[i+1][0], pts_sample[i+1][1], color=INK, sw=1.8))

    # Точка скидання вікна minRTT (Aging window)
    t_reset = 720.0
    f.append(line(t_reset, ya, t_reset, yb, color=FIELD, sw=2.0, dash="5,5"))
    f.append(fitbox(t_reset + 15, ya + 30, 220, 64, "Спливання вікна minRTT\n(minRTT Aging Window)\nПерерахунок базису", size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Зона пастки: без скидання minRTT
    f.append(rect(480, 320, t_reset - 480, 140, fill=WARM, stroke=POS, sw=1.0, rx=4))
    f.append(fitbox(500, 340, 200, 100, "Пастка застарілого базису:\ng = 20 / 50 = 0.4\nЛіміт постійно тиснеться до min_limit,\nхоча черг немає!", size=11, bold=True, fill=WARM, stroke=POS, sw=1.2))

    # Пояснення після скидання
    f.append(fitbox(740, 340, 280, 80, "Після адаптації базису:\nновий minRTT = 50 мс\ng = 50 / 50 = 1.0\nЛіміт повертається до оптимального", size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    f.append(fitbox(xa, 520, xb - xa, 60,
                    "Періодичне старіння minRTT (кожні 10–15 хвилин або за ковзним вікном) запобігає застряганню\n"
                    "системи в стані штучного голодування, коли фізична затримка сервісу законно змінилася.",
                    size=12.5, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'min-rtt-drift-reset.svg'), W, H, *f)


# ── 4. Збіжність алгоритмів: AIMD проти Vegas/Gradient ──────────────────────
def math_vegas_convergence():
    W, H = 1180, 580
    f = []

    xa, xb = 120.0, 1080.0
    ya, yb = 80.0, 480.0

    # Осі координат
    f.append(line(xa, yb, xb, yb, color=INK, sw=2.0))
    f.append(line(xa, ya, xa, yb, color=INK, sw=2.0))
    f.append(text(xb, yb + 35, "Час / Ітерації оновлення →", size=13, color=INK, anchor="end", bold=True))
    f.append(text(xa - 14, ya - 15, "Ліміт конкурентності (Limit)", size=13, color=INK, anchor="start", bold=True))

    # Реальна ємність системи L_opt
    y_opt = 240.0
    f.append(line(xa, y_opt, xb, y_opt, color=MUTED, sw=1.8, dash="5,5"))
    f.append(text(xa + 15, y_opt - 10, "Оптимальна ємність системи L_opt", size=12, color=MUTED, bold=True))

    # 1. Траєкторія AIMD (Пилоподібні коливання, спричиняє дропи)
    pts_aimd = [
        (xa, 440), (220, y_opt - 40), (230, 360),
        (340, y_opt - 50), (350, 370),
        (470, y_opt - 45), (480, 365),
        (600, y_opt - 55), (610, 375),
        (730, y_opt - 40), (740, 360),
        (860, y_opt - 50), (870, 370),
        (980, y_opt - 45), (990, 365), (xb - 40, y_opt - 10)
    ]
    for i in range(len(pts_aimd) - 1):
        f.append(line(pts_aimd[i][0], pts_aimd[i][1], pts_aimd[i+1][0], pts_aimd[i+1][1], color=POS, sw=2.2))

    f.append(text(340, 420, "AIMD: пилоподібні коливання,\nперіодичні таймаути та скидання", size=11.5, color=POS, bold=True))

    # 2. Траєкторія Vegas / Gradient (Плавна збіжність до L_opt)
    pts_vegas = [
        (xa, 440), (180, 360), (260, 300), (360, 265), (460, 245),
        (560, 238), (660, 242), (760, 239), (860, 241), (960, 240), (xb - 40, 240)
    ]
    for i in range(len(pts_vegas) - 1):
        f.append(line(pts_vegas[i][0], pts_vegas[i][1], pts_vegas[i+1][0], pts_vegas[i+1][1], color=FIELD, sw=3.2))

    f.append(text(660, 200, "Vegas / Gradient: плавна асимптотична збіжність\nбез штучних перевантажень і втрат запитів", size=12, color=FIELD, bold=True))

    # Підсумкова плашка
    f.append(fitbox(xa, 510, xb - xa, 55,
                    "Алгоритми на основі затримки (Vegas/Gradient) виявляють наповнення черги задовго до збоїв,\n"
                    "що забезпечує стабільну роботу на плато пропускної здатності без пилоподібної деградації.",
                    size=12.5, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, 'math-vegas-convergence.svg'), W, H, *f)


# ── 5. Хронологія еволюції керування перевантаженням ────────────────────────
def hist_evolution_timeline():
    W, H = 1180, 560
    f = []

    # Вісь часу
    y_axis = 280.0
    f.append(line(80, y_axis, 1100, y_axis, color=LINE, sw=3.0))
    f.append(arrow(1050, y_axis, 1110, y_axis, color=LINE, sw=3.0))
    f.append(text(1110, y_axis + 30, "Час →", size=13, color=INK, anchor="end", bold=True))

    milestones = [
        (130, "1988", "Колапс Інтернету\nта TCP Tahoe/Reno", "Ван Якобсон розробляє AIMD\n(реакція на втрату пакетів)", True),
        (370, "1994", "TCP Vegas\n(Brakmo, Peterson)", "Керування перевантаженням\nза затримкою RTT", False),
        (610, "2014", "Twitter Finagle\n(RPC Concurrency)", "Перші спроби перенести\nідеї TCP у рівень додатків", True),
        (840, "2018", "Netflix Concurrency Limits\n& Envoy Filter", "Гібридний Gradient2 / Vegas\nяк стандарт Service Mesh", False),
        (1040, "Сьогодні", "Adaptive Mesh / BBR", "Динамічний гомеостаз\nбез ручних лімітів потоків", True),
    ]

    for x, year, title, desc, top in milestones:
        f.append(circle(x, y_axis, 7, fill=COOL, stroke=LINE, sw=2.5))
        f.append(text(x, y_axis + (25 if top else -15), year, size=13, color=INK, bold=True))

        card_y = y_axis - 180 if top else y_axis + 45
        f.append(line(x, y_axis, x, card_y + (120 if top else 0), color=MUTED, sw=1.5, dash="3,3"))
        f.append(fitbox(x - 105, card_y, 210, 115, f"{title}\n\n{desc}", size=11.5, bold=True, fill=GOOD if "2018" in year or "Сьогодні" in year else FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'hist-evolution-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    latency_throughput_knee()
    vegas_gradient_feedback()
    min_rtt_drift_reset()
    math_vegas_convergence()
    hist_evolution_timeline()
    print("All figures rendered successfully.")
