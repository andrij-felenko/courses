# -*- coding: utf-8 -*-
"""Фігури теми «Наведення проти регулятора: хто обирає уставку, хто її тримає».
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Ієрархія контурів і межа відповідальності ───────────────────────
def fig_hierarchy_guidance_control():
    W, H = 820, 520
    parts = []

    # 1. Секція Guidance (Зовнішній контур)
    parts.append(rect(30, 45, 760, 125, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    parts.append(text(50, 72, "КОНТУР НАВЕДЕННЯ (GUIDANCE / OUTER LOOP) — 10–50 Гц", size=13, color=NEG, bold=True, anchor="start"))
    parts.append(text(50, 92, "Координати: Світова система NED / ENU  ·  Давачі: GNSS, барометр, карта, лідар", size=11, color=MUTED, anchor="start"))

    b1 = fitbox(50, 105, 210, 50, "Геометрія місії\nВейпойнти, лінія шляху", size=11, fill="#ffffff", stroke=NEG)
    b2 = fitbox(290, 105, 220, 50, "Регулятор позиції й швидкості\nФормування вектора a_des", size=11, fill="#ffffff", stroke=NEG)
    b3 = fitbox(540, 105, 230, 50, "Генератор уставки (Setpoint)\nРозрахунок q_target і тяги", size=11, fill="#ffffff", stroke=NEG)
    parts.extend([b1, b2, b3])
    parts.append(arrow(260, 130, 290, 130, color=NEG, sw=1.5))
    parts.append(arrow(510, 130, 540, 130, color=NEG, sw=1.5))

    # Межа / Інтерфейс уставки
    parts.append(arrow(655, 170, 655, 205, color=LINE, sw=2.0))
    parts.append(rect(460, 205, 330, 70, fill="#fffdf0", stroke="#d97706", sw=1.8, rx=6))
    parts.append(text(625, 225, "ІНТЕРФЕЙС УСТАВКИ (SETPOINT CONTRACT)", size=11, color="#b45309", bold=True))
    parts.append(text(625, 245, "q_target (орієнтація) + T_sp (тяга) + ω_ff (випередження)", size=10, color=INK))
    parts.append(text(625, 262, "Захисти: Tilt Limiter (≤35°), Slew Rate, Watchdog (<100мс)", size=9, color=MUTED))

    # Стрілка вниз до регулятора
    parts.append(arrow(655, 275, 655, 310, color=LINE, sw=2.0))

    # 2. Секція Control (Внутрішній контур)
    parts.append(rect(30, 310, 760, 175, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    parts.append(text(50, 337, "КОНТУР РЕГУЛЮВАННЯ (CONTROL / INNER LOOP) — 250–1000 Гц", size=13, color=POS, bold=True, anchor="start"))
    parts.append(text(50, 357, "Координати: Зв'язана система Body Frame  ·  Давачі: Гіроскоп 1–8 кГц, Акселерометр", size=11, color=MUTED, anchor="start"))

    c1 = fitbox(50, 370, 200, 50, "Оцінювач кута (Attitude)\nПоточний кватерніон q_est", size=11, fill="#ffffff", stroke=POS)
    c2 = fitbox(280, 370, 210, 50, "Регулятор орієнтації (P/PID)\nЦільова кутова швидкість ω_sp", size=11, fill="#ffffff", stroke=POS)
    c3 = fitbox(520, 370, 250, 50, "Регулятор кутової швидкості (PID)\nКерівні моменти τ_x, τ_y, τ_z", size=11, fill="#ffffff", stroke=POS)
    parts.extend([c1, c2, c3])
    parts.append(arrow(250, 395, 280, 395, color=POS, sw=1.5))
    parts.append(arrow(490, 395, 520, 395, color=POS, sw=1.5))

    # Вихід на мікшер і мотори
    m1 = fitbox(280, 430, 210, 42, "Мікшер виходів (Mixer)\nРозподіл сил по моторах", size=11, fill="#ffffff", stroke=LINE)
    m2 = fitbox(520, 430, 250, 42, "Виконавчі механізми (ESC / Мотори)\nШІМ / DShot команди 1..N", size=11, fill="#ffffff", stroke=LINE)
    parts.extend([m1, m2])
    parts.append(arrow(645, 420, 645, 430, color=LINE, sw=1.5))
    parts.append(arrow(490, 451, 520, 451, color=LINE, sw=1.5))

    render(os.path.join(IMG, "hierarchy-guidance-control.svg"), W, H, *parts,
           title="Ієрархічний розподіл: Наведення (Guidance) проти Регулятора (Control)")


# ── Фігура 2: Розподіл часових шкал і смуг пропускання ───────────────────────
def fig_time_scale_separation():
    W, H = 820, 410
    parts = []

    # 4 рівні ієрархії
    layers = [
        {"x": 30, "w": 170, "name": "1. Місія і траєкторія", "bw": "0.2–1 Гц", "loop": "10–20 Гц", "tau": "τ ≈ 2–5 с", "col": NEG, "fill": "#ebf3fe"},
        {"x": 225, "w": 175, "name": "2. Позиція і швидкість", "bw": "1–3 Гц", "loop": "30–50 Гц", "tau": "τ ≈ 0.5–1 с", "col": "#0284c7", "fill": "#e0f2fe"},
        {"x": 425, "w": 175, "name": "3. Орієнтація (Attitude)", "bw": "4–8 Гц", "loop": "100–250 Гц", "tau": "τ ≈ 120–150 мс", "col": "#ea580c", "fill": "#fff7ed"},
        {"x": 625, "w": 165, "name": "4. Кутова швидкість", "bw": "20–40 Гц", "loop": "500–1000 Гц", "tau": "τ ≈ 15–25 мс", "col": POS, "fill": "#fee2e2"},
    ]

    for lay in layers:
        cx = lay["x"] + lay["w"] / 2
        parts.append(rect(lay["x"], 60, lay["w"], 125, fill=lay["fill"], stroke=lay["col"], sw=1.8, rx=6))
        parts.append(text(cx, 85, lay["name"], size=11, color=lay["col"], bold=True))
        parts.append(text(cx, 112, "Смуга: " + lay["bw"], size=11, color=INK))
        parts.append(text(cx, 134, "Контур: " + lay["loop"], size=10, color=MUTED))
        parts.append(text(cx, 158, lay["tau"], size=10, color=lay["col"], bold=True))

    # Вісь частот внизу
    L, R = 50, 770
    Y_AXIS = 260
    parts.append(line(L, Y_AXIS, R, Y_AXIS, color=LINE, sw=2.0))
    parts.append(arrow(R - 10, Y_AXIS, R, Y_AXIS, color=LINE, sw=2.0))
    parts.append(text(R, Y_AXIS - 10, "Смуга пропускання (Closed-loop Bandwidth) →", size=11, color=INK, anchor="end"))

    # Відмітки на осі (без перетину з іншими текстами)
    axis_points = [
        {"x": 115, "label": "0.5 Гц (Місія)", "col": NEG},
        {"x": 312, "label": "2 Гц (Позиція)", "col": "#0284c7"},
        {"x": 512, "label": "6 Гц (Орієнтація)", "col": "#ea580c"},
        {"x": 707, "label": "30 Гц (Швидкість)", "col": POS},
    ]
    for pt in axis_points:
        parts.append(line(pt["x"], Y_AXIS - 6, pt["x"], Y_AXIS + 6, color=pt["col"], sw=2.0))
        parts.append(circle(pt["x"], Y_AXIS, 4, fill=pt["col"], stroke=LINE, sw=1.2))
        parts.append(text(pt["x"], Y_AXIS + 20, pt["label"], size=10, color=pt["col"], bold=True))

    # Стрілка запасу між зовнішнім і внутрішнім доменами
    parts.append(fitbox(180, 300, 460, 48, "Розподіл за шкалою часу (Time-Scale Separation):\nЗапас частот ≥ 5× ... 10× виключає динамічне зчеплення і резонанс", size=11, fill="#fffbeb", stroke="#d97706", color="#b45309", bold=True))

    # Висновок внизу
    parts.append(fitbox(50, 360, 720, 34, "Внутрішній контур (Rate) реагує в 10–20 разів швидше за зовнішній (Position),\nзабезпечуючи стабільну платформу для повільного наведення.", size=10, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(IMG, "time-scale-separation.svg"), W, H, *parts,
           title="Розподіл смуг пропускання та частот дискретизації за рівнями керування")


# ── Фігура 3: Пастка безпосереднього керування моторами від GPS ───────────────
def fig_naive_direct_gps_trap():
    W, H = 800, 440
    parts = []

    # 1. Верхня половина: Наївний монолітний контур (Аварійний)
    parts.append(rect(30, 45, 740, 175, fill="#fff1f2", stroke=POS, sw=1.8, rx=8))
    parts.append(text(50, 70, "❌ НАЇВНИЙ ПІДХІД: ПРЯМЕ КЕРУВАННЯ МОТОРАМИ ВІД GPS (КАТАСТРОФА)", size=12, color=POS, bold=True, anchor="start"))

    b_err = fitbox(50, 90, 150, 55, "Помилка GPS\nΔx = x_ref − x_gps\n(Затримка 200 мс, шум 2м)", size=10, fill="#ffffff", stroke=POS)
    b_pid = fitbox(240, 90, 160, 55, "Єдиний PID-регулятор\nДиференціювання шуму D-ланкою", size=10, fill="#ffffff", stroke=POS)
    b_mot = fitbox(440, 90, 140, 55, "Мотори дрона\nШІМ команди прямо\nна ESC", size=10, fill="#ffffff", stroke=POS)
    b_fail = fitbox(615, 80, 140, 75, "НАСЛІДОК:\nФазовий зсув > 180°\nВтрата стійкості\nМиттєве сальто й краш", size=10, fill="#fde2e2", stroke=POS, color=POS, bold=True)
    parts.extend([b_err, b_pid, b_mot, b_fail])

    parts.append(arrow(200, 117, 240, 117, color=POS, sw=1.5))
    parts.append(arrow(400, 117, 440, 117, color=POS, sw=1.5))
    parts.append(arrow(580, 117, 615, 117, color=POS, sw=1.5))

    parts.append(text(50, 165, "Чому ламається: 1) Затримка GPS 200 мс з'їдає весь запас фази на 2 Гц;  2) Невідомий нахил тіла (Body vs World);", size=10, color=INK, anchor="start"))
    parts.append(text(50, 185, "3) D-ланка множить шум вимірів на тисячі; 4) Поворот по курсу обертає напрямок моторів без відома регулятора.", size=10, color=INK, anchor="start"))

    # 2. Нижня половина: Каскадна розв'язка (Стійка)
    parts.append(rect(30, 240, 740, 180, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    parts.append(text(50, 265, "✔ ПРАВИЛЬНА ІЄРАРХІЯ: КАСКАДНЕ РОЗДІЛЕННЯ (СТІЙКИЙ ПОЛІТ)", size=12, color=FIELD, bold=True, anchor="start"))

    g1 = fitbox(50, 285, 160, 55, "Повільний GPS (10 Гц)\nФільтрація в EKF\nВизначення вектора a_des", size=10, fill="#ffffff", stroke=FIELD)
    g2 = fitbox(250, 285, 160, 55, "Генератор уставки\nНахил tilt = f(a_des)\nОбмеження кута ≤ 35°", size=10, fill="#ffffff", stroke=FIELD)
    g3 = fitbox(450, 285, 160, 55, "Швидкий PID орієнтації (1 кГц)\nЗворотний зв'язок з IMU\nДемпфування за 2 мс", size=10, fill="#ffffff", stroke=FIELD)
    g4 = fitbox(645, 285, 110, 55, "Мотори\nПлавне й стійке\nвідпрацювання", size=10, fill="#ffffff", stroke=FIELD)
    parts.extend([g1, g2, g3, g4])

    parts.append(arrow(210, 312, 250, 312, color=FIELD, sw=1.5))
    parts.append(arrow(410, 312, 450, 312, color=FIELD, sw=1.5))
    parts.append(arrow(610, 312, 645, 312, color=FIELD, sw=1.5))

    parts.append(text(50, 360, "Результат: Швидкий контур на гіроскопі ізолює апарат від миттєвих збурень і поривів вітру.", size=10, color=INK, anchor="start"))
    parts.append(text(50, 380, "Повільний контур навігації оперує лише плавними нахилами цілого апарата. Запас фази > 60°.", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "naive-direct-gps-trap.svg"), W, H, *parts,
           title="Пастка безпосереднього замикання GPS на мотори проти каскадної архітектури")


# ── Фігура 4: Конвеєр формування та кондиціонування уставки ──────────────────
def fig_setpoint_interface_pipeline():
    W, H = 820, 360
    parts = []

    # Конвеєр кроків зліва направо
    steps = [
        {"x": 30, "w": 160, "title": "1. Бажане прискорення", "sub": "a_des = [ax, ay, az]\nз контуру позиції (NED)", "fill": "#eff6ff", "col": NEG},
        {"x": 225, "w": 170, "title": "2. Вектор тяги й нахил", "sub": "f_des = a_des − g\nКут tilt = acos(fz / ||f||)", "fill": "#eff6ff", "col": NEG},
        {"x": 430, "w": 175, "title": "3. Захисні бар'єри", "sub": "Tilt Limit: tilt ≤ 35°\nSlew Rate: dω/dt ≤ max\nAnti-windup зворотний зв'язок", "fill": "#fffbeb", "col": "#d97706"},
        {"x": 640, "w": 150, "title": "4. Цільовий пакет", "sub": "q_target (кватерніон)\nT_sp (нормалізована тяга)\nω_ff (кутова швидкість)", "fill": "#f0fdf4", "col": FIELD},
    ]

    for s in steps:
        parts.append(rect(s["x"], 60, s["w"], 140, fill=s["fill"], stroke=s["col"], sw=1.8, rx=6))
        parts.append(text(s["x"] + s["w"] / 2, 85, s["title"], size=11, color=s["col"], bold=True))
        lines = s["sub"].split("\n")
        for idx, ln in enumerate(lines):
            parts.append(text(s["x"] + s["w"] / 2, 115 + idx * 20, ln, size=10, color=INK))

    # Стрілки між кроками
    parts.append(arrow(190, 130, 225, 130, color=LINE, sw=1.6))
    parts.append(arrow(395, 130, 430, 130, color=LINE, sw=1.6))
    parts.append(arrow(605, 130, 640, 130, color=LINE, sw=1.6))

    # Нижня частина: Передача через потік / Сторожовий таймер
    parts.append(rect(30, 225, 760, 105, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(50, 250, "БЕЗБЛОКУВАЛЬНИЙ ТРАНСПОРТ ТА СТОРОЖ ЗАСТАРІВАННЯ (WATCHDOG)", size=12, color=INK, bold=True, anchor="start"))

    t1 = fitbox(50, 265, 220, 50, "Guidance Thread (20–50 Гц)\nЗапис у Seqlock / Double Buffer", size=10, fill="#ffffff", stroke=NEG)
    t2 = fitbox(300, 265, 220, 50, "Setpoint Watchdog\nПеревірка dt = t_now − t_sp < 100 мс", size=10, fill="#ffffff", stroke="#d97706")
    t3 = fitbox(550, 265, 220, 50, "Control Thread (500–1000 Гц)\nЧитання уставки / Fallback режим", size=10, fill="#ffffff", stroke=POS)
    parts.extend([t1, t2, t3])

    parts.append(arrow(270, 290, 300, 290, color=LINE, sw=1.5))
    parts.append(arrow(520, 290, 550, 290, color=LINE, sw=1.5))

    render(os.path.join(IMG, "setpoint-interface-pipeline.svg"), W, H, *parts,
           title="Конвеєр підготовки, обмеження та безпечної передачі уставки орієнтації й тяги")


def main():
    fig_hierarchy_guidance_control()
    fig_time_scale_separation()
    fig_naive_direct_gps_trap()
    fig_setpoint_interface_pipeline()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
