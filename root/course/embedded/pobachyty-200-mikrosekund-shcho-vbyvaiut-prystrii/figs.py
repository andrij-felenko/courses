# -*- coding: utf-8 -*-
"""Фігури для статті pobachyty-200-mikrosekund-shcho-vbyvaiut-prystrii.
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. multimeter-vs-scope: мультиметр проти осцилографа при 200 мкс провалі ───
def fig_multimeter_vs_scope():
    W, H = 760, 400
    p = []

    # Блок 1: Мультиметр (інтегрування за 200 мс)
    p.append(rect(20, 20, 720, 165, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    p.append(text(40, 48, "Мультиметр: інтегрування за 200 мс (NPLC = 10)", size=14, color=INK, bold=True, anchor="start"))

    # Дисплей мультиметра
    p.append(rect(45, 68, 170, 75, fill="#1c241d", stroke="#3a483c", sw=1.5, rx=4))
    p.append(text(130, 118, "3.298 V", size=24, color="#52e374", bold=True, anchor="middle"))
    p.append(text(130, 136, "DC Voltage (Auto)", size=10, color="#8cd99e", anchor="middle"))

    # Часова діаграма інтегрування
    ox, oy = 250, 130
    gw = 460
    p.append(arrow(ox, oy, ox + gw, oy, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy + 5, ox, oy - 65, color=MUTED, sw=1.2))
    p.append(text(ox + gw - 5, oy + 18, "час t (мс)", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - 55, "U (В)", size=11, color=MUTED, anchor="end"))

    # Вікно інтегрування
    p.append(rect(ox + 40, oy - 60, 360, 60, fill="#e8f4fd", stroke="#3a88c8", sw=1.0, rx=0))
    p.append(text(ox + 220, oy - 66, "Вікно інтегрування АЦП: T_int = 200 мс", size=11, color="#206095", bold=True, anchor="middle"))

    # Графік напруги в часі (з крихітним провалом)
    p.append(line(ox + 10, oy - 45, ox + 210, oy - 45, color=POS, sw=2.0))
    p.append(line(ox + 210, oy - 45, ox + 212, oy - 15, color=POS, sw=2.0))
    p.append(line(ox + 212, oy - 15, ox + 214, oy - 15, color=POS, sw=2.0))
    p.append(line(ox + 214, oy - 15, ox + 216, oy - 45, color=POS, sw=2.0))
    p.append(line(ox + 216, oy - 45, ox + gw - 20, oy - 45, color=POS, sw=2.0))

    # Виноска про невидимість
    p.append(text(ox + 220, oy - 30, "провал 200 мкс (0.1% від вікна)", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(ox + 220, oy - 14, "середнє значення = 3.298 В — провал розчинився у вибірці", size=10, color=MUTED, italic=True, anchor="start"))

    # Блок 2: Осцилограф (роздільність 1 мкс)
    p.append(rect(20, 205, 720, 175, fill="#181c24", stroke="#2f3846", sw=1.2, rx=6))
    p.append(text(40, 233, "Швидкісний осцилограф (Single Trigger, 50 мкс/под): реальна форма сигналу", size=14, color="#e0e6ed", bold=True, anchor="start"))

    # Сітка осцилографа
    sox, soy = 60, 350
    swidth = 640
    for gy in range(0, 101, 25):
        p.append(line(sox, soy - gy, sox + swidth, soy - gy, color="#263242", sw=0.8, dash="2 2"))
    for gx in range(0, swidth + 1, 80):
        p.append(line(sox + gx, soy, sox + gx, soy - 100, color="#263242", sw=0.8, dash="2 2"))

    # Рівень номіналу 3.3 В і порогу Brownout 2.7 В
    p.append(line(sox, soy - 85, sox + swidth, soy - 85, color="#52e374", sw=1.0, dash="4 4"))
    p.append(text(sox + swidth + 8, soy - 82, "3.3 В (номінал)", size=10, color="#52e374", anchor="start"))

    p.append(line(sox, soy - 50, sox + swidth, soy - 50, color="#e67e22", sw=1.2, dash="5 3"))
    p.append(text(sox + swidth + 8, soy - 47, "2.7 В (поріг BOD)", size=10, color="#e67e22", bold=True, anchor="start"))

    # Осцилограма глітчу (жовта)
    trace = [
        (sox, soy - 85),
        (sox + 180, soy - 85),
        (sox + 195, soy - 20),
        (sox + 360, soy - 20),
        (sox + 380, soy - 85),
        (sox + swidth, soy - 85)
    ]
    pts_str = " ".join("%.1f,%.1f" % pt for pt in trace)
    p.append('<polyline points="%s" fill="none" stroke="#f1c40f" stroke-width="2.5" stroke-linejoin="round"/>' % pts_str)

    # Вимірювальні маркери
    p.append(line(sox + 195, soy - 95, sox + 195, soy - 5, color="#3498db", sw=1.2, dash="3 2"))
    p.append(line(sox + 380, soy - 95, sox + 380, soy - 5, color="#3498db", sw=1.2, dash="3 2"))
    p.append(arrow(sox + 287, soy - 10, sox + 195, soy - 10, color="#3498db", sw=1.2))
    p.append(arrow(sox + 288, soy - 10, sox + 380, soy - 10, color="#3498db", sw=1.2))
    p.append(text(sox + 287, soy - 14, "Δt = 200 мкс", size=11, color="#3498db", bold=True, anchor="middle"))

    # Позначення зони аварії
    p.append(rect(sox + 205, soy - 48, 165, 26, fill="#3d2121", stroke=POS, sw=1.0, rx=3))
    p.append(text(sox + 287, soy - 32, "АВАРІЙНА ЗОНА (BOD RESET)", size=10, color="#ff7675", bold=True, anchor="middle"))

    render(os.path.join(OUT, "multimeter-vs-scope.svg"), W, H, *p)


# ── 2. probe-ground-inductance: довгий земляний дріт проти пружинного заземлення ─
def fig_probe_ground_inductance():
    W, H = 760, 360
    p = []

    # Ліва половина: Довгий дріт із крокодилом (погана практика)
    p.append(rect(20, 20, 350, 320, fill="#fdfbfb", stroke="#e0b4b4", sw=1.2, rx=6))
    p.append(text(195, 48, "Довгий дріт заземлення (12–15 см)", size=13, color=POS, bold=True, anchor="middle"))

    # Схема паразитного контуру
    p.append(rect(45, 75, 300, 110, fill="#ffffff", stroke="#d9d9d9", sw=1.0, rx=4))
    p.append(text(60, 95, "Паразитний LC-контур щупа:", size=11, color=MUTED, bold=True, anchor="start"))
    p.append(text(60, 115, "• L_петлі ≈ 120–150 нГн (дріт + крокодил)", size=11, color=INK, anchor="start"))
    p.append(text(60, 135, "• C_щупа ≈ 12–15 пФ (вхідна ємність)", size=11, color=INK, anchor="start"))
    p.append(text(60, 155, "• f_рез ≈ 120 МГц (високочастотний дзвін)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(60, 172, "• V_паразитна = L · (di/dt) спотворює сигнал", size=10, color=MUTED, italic=True, anchor="start"))

    # Осцилограма з дзвоном
    ox1, oy1 = 50, 300
    p.append(line(ox1, oy1, ox1 + 290, oy1, color=MUTED, sw=1.0))
    p.append(text(ox1 + 290, oy1 + 16, "t", size=11, color=MUTED, italic=True, anchor="end"))

    # Дзвін (Ringing + фальшиві піки)
    pts1 = [
        (ox1 + 10, oy1 - 50),
        (ox1 + 50, oy1 - 50),
        (ox1 + 60, oy1 - 90),   # викид вгору
        (ox1 + 75, oy1 - 10),   # провал глибше норми
        (ox1 + 90, oy1 - 75),
        (ox1 + 105, oy1 - 35),
        (ox1 + 120, oy1 - 58),
        (ox1 + 135, oy1 - 46),
        (ox1 + 150, oy1 - 50),
        (ox1 + 280, oy1 - 50)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts1), POS))
    p.append(text(ox1 + 100, oy1 - 78, "Фантомний дзвін", size=10, color=POS, bold=True, anchor="middle"))

    # Права половина: Пружинне заземлення Ground Spring (еталон)
    p.append(rect(390, 20, 350, 320, fill="#fbfdfb", stroke="#b4e0be", sw=1.2, rx=6))
    p.append(text(565, 48, "Пружинне заземлення (Ground Spring)", size=13, color=FIELD, bold=True, anchor="middle"))

    # Схема правильного підключення
    p.append(rect(415, 75, 300, 110, fill="#ffffff", stroke="#d9d9d9", sw=1.0, rx=4))
    p.append(text(430, 95, "Мінімальна індуктивність контуру:", size=11, color=MUTED, bold=True, anchor="start"))
    p.append(text(430, 115, "• L_петлі < 5–8 нГн (коротка пружина)", size=11, color=INK, anchor="start"))
    p.append(text(430, 135, "• Прямий контакт із землею конденсатора", size=11, color=INK, anchor="start"))
    p.append(text(430, 155, "• f_рез > 800 МГц (поза смугою вимірювання)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(430, 172, "• Чиста перехідна характеристика без шуму", size=10, color=MUTED, italic=True, anchor="start"))

    # Осцилограма чиста
    ox2, oy2 = 420, 300
    p.append(line(ox2, oy2, ox2 + 290, oy2, color=MUTED, sw=1.0))
    p.append(text(ox2 + 290, oy2 + 16, "t", size=11, color=MUTED, italic=True, anchor="end"))

    # Реальний чистий фронт
    pts2 = [
        (ox2 + 10, oy2 - 50),
        (ox2 + 50, oy2 - 50),
        (ox2 + 58, oy2 - 30),
        (ox2 + 150, oy2 - 30),
        (ox2 + 165, oy2 - 50),
        (ox2 + 280, oy2 - 50)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts2), FIELD))
    p.append(text(ox2 + 104, oy2 - 14, "Справжній профіль провалу", size=10, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "probe-ground-inductance.svg"), W, H, *p)


# ── 3. current-profile-transient: динамічний струм і перехідна відповідь LDO/DC-DC ──
def fig_current_profile_transient():
    W, H = 760, 420
    p = []

    # Тло та контур
    p.append(rect(20, 20, 720, 380, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(40, 48, "Синхронне профілювання струму й реакції стабілізатора (Joulescope / PPK2)", size=14, color=INK, bold=True, anchor="start"))

    # Графік 1: Динамічний струм споживання (I_load)
    ox, oy1 = 80, 180
    gw = 620
    p.append(arrow(ox, oy1, ox + gw, oy1, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy1 + 5, ox, oy1 - 105, color=MUTED, sw=1.2))
    p.append(text(ox - 12, oy1 - 95, "I (мА)", size=11, color=MUTED, bold=True, anchor="end"))
    p.append(text(ox + gw - 5, oy1 + 18, "час t (мкс)", size=11, color=MUTED, anchor="end"))

    # Крива струму: Сон (15 мкА) -> PLL (20 мА) -> TX Burst (280 мА) -> Сон
    cur_pts = [
        (ox, oy1 - 2),
        (ox + 120, oy1 - 2),
        (ox + 130, oy1 - 25),    # PLL запуск
        (ox + 190, oy1 - 25),
        (ox + 195, oy1 - 95),    # TX PA увімкнення (280 мА)
        (ox + 395, oy1 - 95),    # Тривалість передачі 200 мкс
        (ox + 400, oy1 - 2),     # Вимкнення
        (ox + gw - 20, oy1 - 2)
    ]
    p.append('<polyline points="%s" fill="none" stroke="#2980b9" stroke-width="2.4" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in cur_pts)))

    p.append(text(ox + 60, oy1 - 8, "Sleep (15 мкА)", size=10, color="#2980b9", anchor="middle"))
    p.append(text(ox + 160, oy1 - 32, "PLL (20 мА)", size=10, color="#2980b9", anchor="middle"))
    p.append(text(ox + 295, oy1 - 102, "Радіопередача TX: 280 мА (200 мкс)", size=11, color="#2980b9", bold=True, anchor="middle"))

    # Графік 2: Вихідна напруга живлення (V_out)
    oy2 = 360
    p.append(arrow(ox, oy2, ox + gw, oy2, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy2 + 5, ox, oy2 - 125, color=MUTED, sw=1.2))
    p.append(text(ox - 12, oy2 - 115, "U (В)", size=11, color=MUTED, bold=True, anchor="end"))
    p.append(text(ox + gw - 5, oy2 + 18, "час t (мкс)", size=11, color=MUTED, anchor="end"))

    # Рівні напруги
    p.append(line(ox, oy2 - 100, ox + gw - 20, oy2 - 100, color="#27ae60", sw=1.0, dash="4 4"))
    p.append(text(ox + gw - 15, oy2 - 97, "3.3 В (номінал)", size=10, color="#27ae60", anchor="start"))

    p.append(line(ox, oy2 - 50, ox + gw - 20, oy2 - 50, color=POS, sw=1.0, dash="4 3"))
    p.append(text(ox + gw - 15, oy2 - 47, "2.6 В (Brownout Reset)", size=10, color=POS, bold=True, anchor="start"))

    # Крива напруги з затримкою регулятора (Load Transient Sag)
    volt_pts = [
        (ox, oy2 - 100),
        (ox + 195, oy2 - 100),
        (ox + 205, oy2 - 35),   # глибокий провал через ESR/ESL конденсатора
        (ox + 260, oy2 - 60),   # петля регулятора починає відкривати прохідний транзистор (t_resp ≈ 30 мкс)
        (ox + 350, oy2 - 90),   # часткове відновлення
        (ox + 395, oy2 - 90),
        (ox + 405, oy2 - 115),  # викид вгору при скиданні навантаження (Overshoot)
        (ox + 460, oy2 - 100),
        (ox + gw - 20, oy2 - 100)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in volt_pts), POS))

    # Виноски з поясненнями
    p.append(arrow(ox + 250, oy2 - 15, ox + 210, oy2 - 32, color=POS, sw=1.2))
    p.append(text(ox + 255, oy2 - 12, "Провал нижче BOD через затримку регулятора (t_resp)", size=10, color=POS, bold=True, anchor="start"))

    p.append(arrow(ox + 440, oy2 - 130, ox + 412, oy2 - 118, color="#e67e22", sw=1.2))
    p.append(text(ox + 445, oy2 - 132, "Перенапруга при розвантаженні", size=10, color="#e67e22", anchor="start"))

    render(os.path.join(OUT, "current-profile-transient.svg"), W, H, *p)


# ── 4. pvd-early-warning: багаторівнева супервізія й часове вікно порятунку ─────
def fig_pvd_early_warning():
    W, H = 760, 390
    p = []

    # Контур
    p.append(rect(20, 20, 720, 350, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(40, 48, "Градуйований захист: часове вікно між PVD-перериванням та апаратним BOD", size=14, color=INK, bold=True, anchor="start"))

    ox, oy = 70, 330
    gw = 640
    p.append(arrow(ox, oy, ox + gw, oy, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy + 5, ox, oy - 250, color=MUTED, sw=1.2))
    p.append(text(ox - 12, oy - 240, "U (В)", size=11, color=MUTED, bold=True, anchor="end"))
    p.append(text(ox + gw - 5, oy + 18, "час t", size=11, color=MUTED, anchor="end"))

    # Рівні: Номінал 3.3 В, Поріг PVD 2.9 В, Поріг BOD 2.2 В
    p.append(line(ox, oy - 220, ox + gw - 40, oy - 220, color="#27ae60", sw=1.0, dash="5 4"))
    p.append(text(ox + gw - 30, oy - 217, "3.3 В (Норма)", size=10, color="#27ae60", anchor="start"))

    p.append(line(ox, oy - 150, ox + gw - 40, oy - 150, color="#3498db", sw=1.2, dash="4 3"))
    p.append(text(ox + gw - 30, oy - 147, "2.9 В (Поріг PVD)", size=10, color="#3498db", bold=True, anchor="start"))

    p.append(line(ox, oy - 70, ox + gw - 40, oy - 70, color=POS, sw=1.2, dash="4 3"))
    p.append(text(ox + gw - 30, oy - 67, "2.2 В (Апаратний BOD)", size=10, color=POS, bold=True, anchor="start"))

    # Зона вікна порятунку (між PVD і BOD)
    p.append(rect(ox + 100, oy - 150, 110, 80, fill="#ebf5fb", stroke="#3498db", sw=1.0, rx=0))
    p.append(text(ox + 155, oy - 165, "Вікно Δt (15–80 мкс)", size=11, color="#2980b9", bold=True, anchor="middle"))

    # Крива падіння напруги
    pts = [
        (ox, oy - 220),
        (ox + 70, oy - 220),
        (ox + 100, oy - 150),   # Точка спрацьовування PVD
        (ox + 210, oy - 70),    # Точка спрацьовування BOD (якщо не врятували)
        (ox + 250, oy - 30),
        (ox + 290, oy - 30),
        (ox + 330, oy - 220),   # Відновлення
        (ox + gw - 40, oy - 220)
    ]
    p.append('<polyline points="%s" fill="none" stroke="#2c3e50" stroke-width="2.4" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts)))

    # Дії в обробнику PVD - розміщено праворуч від кривої без перекриття блоків
    box, bw, bh = textbox(ox + 450, oy - 120,
                          "Дії обробника PVD_IRQHandler:\n1. Аварійна зупинка ШІМ/радіо (зниження струму)\n2. Запис причини у Retention SRAM\n3. Блокування запису у Flash/EEPROM",
                          size=10, color=INK, fill="#f4fbf7", stroke="#27ae60", sw=1.0, rx=4)
    p.append(box)

    # Позначення спрацьовування PVD переривання
    p.append(circle(ox + 100, oy - 150, 4, fill="#3498db", stroke="#ffffff", sw=1.5))
    p.append(text(ox + 95, oy - 135, "PVD переривання", size=10, color="#3498db", bold=True, anchor="end"))

    # Позначення апаратного ресету BOD
    p.append(circle(ox + 210, oy - 70, 4, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(ox + 220, oy - 55, "Hard Reset (BOD)", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "pvd-early-warning.svg"), W, H, *p)


if __name__ == "__main__":
    fig_multimeter_vs_scope()
    fig_probe_ground_inductance()
    fig_current_profile_transient()
    fig_pvd_early_warning()
    print("Всі фігури згенеровано успішно.")
