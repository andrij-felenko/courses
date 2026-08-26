# -*- coding: utf-8 -*-
"""Фігури для теми koly-vynen-ne-prystrii («Коли винен не пристрій»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. floating-ground-y-capacitors: Y-конденсатори та плаваючий потенціал ────
def fig_floating_ground_y_capacitors():
    W, H = 840, 440
    p = []

    # Тло блоку живлення (SMPS)
    p.append(rect(40, 40, 440, 360, fill="none", stroke="#94a3b8", sw=1.6, rx=8))
    p.append(text(260, 68, "Імпульсне джерело живлення (SMPS)", size=14, bold=True, color=INK))

    # Мережеві клеми L, N, PE
    p.append(circle(70, 120, 6, fill=POS, stroke=POS, sw=1))
    p.append(text(70, 105, "L (230 В)", size=11, bold=True, color=POS))
    p.append(line(76, 120, 200, 120, color=POS, sw=2.2))

    p.append(circle(70, 240, 6, fill=NEG, stroke=NEG, sw=1))
    p.append(text(70, 260, "N (0 В)", size=11, bold=True, color=NEG))
    p.append(line(76, 240, 200, 240, color=NEG, sw=2.2))

    # Клема PE — обірвана (не підключена до контуру заземлення)
    p.append(circle(70, 340, 6, fill="#cbd5e1", stroke=MUTED, sw=1.5))
    p.append(text(70, 365, "PE (заземлення)", size=11, color=MUTED, bold=True))
    p.append(line(76, 340, 130, 340, color=MUTED, sw=1.8, dash="4 4"))
    # Червоний хрестик обриву
    p.append(line(135, 332, 151, 348, color=POS, sw=2.4))
    p.append(line(151, 332, 135, 348, color=POS, sw=2.4))
    b_pe, _, _ = textbox(215, 355, "Обрив PE / 2-провідна мережа:\nзаземлення відсутнє",
                         size=10, color=POS, fill="#fef2f2", stroke=POS, sw=1.2, min_w=170)
    p.append(b_pe)

    # Y-конденсатори CY1 і CY2 (ємнісний дільник напруги)
    # CY1 між L і корпусом
    p.append(line(200, 120, 200, 160, color=INK, sw=1.8))
    p.append(line(185, 160, 215, 160, color=INK, sw=2.2))
    p.append(line(185, 166, 215, 166, color=INK, sw=2.2))
    p.append(text(230, 166, "C_Y1 (2.2 нФ)", size=10, color=INK, bold=True, anchor="start"))
    p.append(line(200, 166, 200, 180, color=INK, sw=1.8))

    # CY2 між N і корпусом
    p.append(line(200, 240, 200, 200, color=INK, sw=1.8))
    p.append(line(185, 200, 215, 200, color=INK, sw=2.2))
    p.append(line(185, 194, 215, 194, color=INK, sw=2.2))
    p.append(text(230, 200, "C_Y2 (2.2 нФ)", size=10, color=INK, bold=True, anchor="start"))
    p.append(line(200, 194, 200, 180, color=INK, sw=1.8))

    # Спільна точка дільника — з'єднана з металевим корпусом / плаваючим GND
    p.append(circle(200, 180, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(200, 180, 360, 180, color=FIELD, sw=2.2))

    b_div, _, _ = textbox(360, 135, "Ємнісний дільник:\nU_chassis = 230 В / 2 = 115 В RMS",
                          size=11, color=FIELD, bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.5, min_w=190)
    p.append(b_div)

    # Металевий корпус пристрою
    p.append(rect(320, 230, 140, 140, fill="#f1f5f9", stroke="#64748b", sw=1.8, rx=4))
    p.append(text(390, 255, "Металевий корпус", size=11, bold=True, color=INK))
    p.append(text(390, 275, "пристрою 1", size=10, color=MUTED))
    p.append(text(390, 305, "Потенціал ~115 В~", size=11, bold=True, color=POS))
    p.append(text(390, 325, "відносно Землі", size=10, color=POS))

    # З'єднання дільника з корпусом
    p.append(line(360, 180, 390, 180, color=FIELD, sw=2.2))
    p.append(line(390, 180, 390, 230, color=FIELD, sw=2.2))

    # Кабель зв'язку до заземленого пристрою 2
    p.append(rect(620, 160, 180, 220, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(710, 190, "Віддалений прилад 2", size=12, bold=True, color=NEG))
    p.append(text(710, 210, "(ПК / Сервер / PLC)", size=10, color=MUTED))

    # Заземлення пристрою 2
    p.append(line(710, 380, 710, 410, color=INK, sw=2.2))
    p.append(line(695, 410, 725, 410, color=INK, sw=2.4))
    p.append(line(700, 415, 720, 415, color=INK, sw=2.0))
    p.append(line(705, 420, 715, 420, color=INK, sw=1.6))
    p.append(text(710, 435, "PE (заземлено, 0 В)", size=10, color=INK, bold=True))

    # Кабель і вирівнювальний струм
    p.append(line(460, 280, 620, 280, color=POS, sw=3.0))
    p.append(arrow(510, 280, 570, 280, color=POS, sw=3.0))
    b_curr, _, _ = textbox(540, 235, "Вирівнювальний струм I_вирівн\nчерез екран кабелю та сигнальний GND",
                           size=10, color=POS, bold=True, fill="#fef2f2", stroke=POS, sw=1.4, min_w=200)
    p.append(b_curr)
    p.append(text(540, 310, "Іскра при гарячому підключенні,", size=10, color=POS))
    p.append(text(540, 326, "вигоряння доріжок GND та трансиверів", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "floating-ground-y-capacitors.svg"), W, H, *p,
           title="Ємнісний дільник Y-конденсаторів та вирівнювальний струм")


# ── 2. ground-loop-common-mode: Земляні петлі та синфазна напруга ────────────
def fig_ground_loop_common_mode():
    W, H = 840, 440
    p = []

    # Вузол 1 (Цех А)
    p.append(rect(40, 60, 220, 260, fill="none", stroke="#64748b", sw=1.8, rx=6))
    p.append(text(150, 90, "Вузол 1 (Цех А)", size=13, bold=True, color=INK))
    b_tr1, _, _ = textbox(150, 160, "Трансивер RS-485 / CAN\nV_cm діапазон:\n-7 В ... +12 В",
                          size=10, color=NEG, fill="#eff6ff", stroke=NEG, sw=1.2, min_w=180)
    p.append(b_tr1)
    p.append(circle(150, 240, 5, fill=INK, stroke=INK, sw=1))
    p.append(text(150, 260, "GND 1 (0 В_локал)", size=10, bold=True, color=INK))

    # Заземлення 1
    p.append(line(150, 320, 150, 370, color=INK, sw=2.0))
    p.append(line(135, 370, 165, 370, color=INK, sw=2.4))
    p.append(line(140, 375, 160, 375, color=INK, sw=2.0))
    p.append(line(145, 380, 155, 380, color=INK, sw=1.6))
    p.append(text(150, 400, "Контур заземлення А", size=10, color=MUTED))

    # Вузол 2 (Цех Б)
    p.append(rect(580, 60, 220, 260, fill="none", stroke="#64748b", sw=1.8, rx=6))
    p.append(text(690, 90, "Вузол 2 (Цех Б)", size=13, bold=True, color=INK))
    b_tr2, _, _ = textbox(690, 160, "Трансивер RS-485 / CAN\nV_cm діапазон:\n-7 В ... +12 В",
                          size=10, color=NEG, fill="#eff6ff", stroke=NEG, sw=1.2, min_w=180)
    p.append(b_tr2)
    p.append(circle(690, 240, 5, fill=INK, stroke=INK, sw=1))
    p.append(text(690, 260, "GND 2 (ΔV_gnd = +25 В)", size=10, bold=True, color=POS))

    # Заземлення 2
    p.append(line(690, 320, 690, 370, color=INK, sw=2.0))
    p.append(line(675, 370, 705, 370, color=INK, sw=2.4))
    p.append(line(680, 375, 700, 375, color=INK, sw=2.0))
    p.append(line(685, 380, 695, 380, color=INK, sw=1.6))
    p.append(text(690, 400, "Контур заземлення Б", size=10, color=MUTED))

    # Лінії зв'язку (кабель 300 м)
    p.append(line(260, 135, 580, 135, color=FIELD, sw=2.2))
    p.append(text(420, 120, "Сигнальна лінія Data + (A)", size=10, color=FIELD, bold=True))

    p.append(line(260, 175, 580, 175, color=FIELD, sw=2.2))
    p.append(text(420, 190, "Сигнальна лінія Data − (B)", size=10, color=FIELD, bold=True))

    p.append(line(260, 240, 580, 240, color=INK, sw=1.8, dash="6 4"))
    p.append(text(420, 255, "Сигнальна земля кабелю (GND)", size=10, color=INK))

    # Зворотний шлях через Землю (петля заземлення)
    p.append(line(150, 370, 690, 370, color="#94a3b8", sw=2.2, dash="4 4"))
    p.append(text(420, 390, "Шлях струму крізь ґрунт / металоконструкції будівлі", size=10, color=MUTED, italic=True))

    # Магнітне поле завади (від сусіднього силового кабелю електродвигуна)
    p.append(circle(420, 310, 34, fill="#fef3c7", stroke="#d97706", sw=1.8))
    p.append(text(420, 305, "dΦ/dt", size=12, bold=True, color="#b45309"))
    p.append(text(420, 323, "B-поле двигуна", size=9, color="#b45309"))

    b_loop, _, _ = textbox(420, 50, "Велика площа петлі S → індукована ЕРС:\nV_петлі = -dΦ/dt + ΔV_gnd",
                           size=11, color=POS, bold=True, fill="#fef2f2", stroke=POS, sw=1.5, min_w=280)
    p.append(b_loop)

    render(os.path.join(OUT, "ground-loop-common-mode.svg"), W, H, *p,
           title="Земляна петля, різниця потенціалів ґрунту та синфазна напруга")


# ── 3. surge-protection-cascade-stages: Каскадний захист від сплесків ─────────
def fig_surge_protection_cascade_stages():
    W, H = 860, 420
    p = []

    # 3 Каскади: Ступінь 1, Координація, Ступінь 2, Ізоляція
    x_in = 60
    x_gdt = 200
    x_coord = 360
    x_tvs = 520
    x_iso = 680

    # Шини лінії зв'язку зверху і знизу
    p.append(line(x_in, 100, x_iso + 60, 100, color=FIELD, sw=2.4))
    p.append(line(x_in, 260, x_iso + 60, 260, color=FIELD, sw=2.4))
    p.append(text(x_in, 85, "Line A (польовий кабель)", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(x_in, 280, "Line B (польовий кабель)", size=10, bold=True, color=FIELD, anchor="start"))

    # Вхідний високовольтний сплеск
    b_surge, _, _ = textbox(110, 180, "Сплеск 4 кВ\n8/20 мкс\n(комутація/\nблискавка)",
                            size=10, color=POS, bold=True, fill="#fef2f2", stroke=POS, sw=1.5, min_w=100)
    p.append(b_surge)

    # ── Ступінь 1: Газорозрядник GDT / Варистор MOV ──
    p.append(line(x_gdt, 100, x_gdt, 145, color=INK, sw=1.8))
    p.append(circle(x_gdt, 180, 24, fill="#f8fafc", stroke=POS, sw=2.0))
    p.append(text(x_gdt, 176, "GDT", size=12, bold=True, color=POS))
    p.append(text(x_gdt, 192, "90 В", size=9, color=POS))
    p.append(line(x_gdt, 215, x_gdt, 260, color=INK, sw=1.8))
    # Заземлення GDT
    p.append(line(x_gdt, 260, x_gdt, 330, color=INK, sw=1.8))
    p.append(line(x_gdt - 15, 330, x_gdt + 15, 330, color=INK, sw=2.2))
    p.append(line(x_gdt - 10, 335, x_gdt + 10, 335, color=INK, sw=1.8))
    p.append(line(x_gdt - 5, 340, x_gdt + 5, 340, color=INK, sw=1.4))
    p.append(text(x_gdt, 360, "Earth (PE)", size=10, color=MUTED, bold=True))

    b_st1, _, _ = textbox(x_gdt, 45, "Ступінь 1 (Грубий):\nСкидання струму до 10–20 кА\nПовільний (≈1 мкс)",
                          size=9, color=POS, fill="#fff5f5", stroke=POS, sw=1.2, min_w=150)
    p.append(b_st1)

    # ── Елемент координації (PTC / Імпульсні резистори) ──
    # PTC на верхній лінії
    p.append(rect(x_coord - 25, 90, 50, 20, fill="#fef9c3", stroke="#ca8a04", sw=1.6, rx=2))
    p.append(text(x_coord, 104, "PTC 10 Ом", size=9, bold=True, color="#854d0e"))
    # PTC на нижній лінії
    p.append(rect(x_coord - 25, 250, 50, 20, fill="#fef9c3", stroke="#ca8a04", sw=1.6, rx=2))
    p.append(text(x_coord, 264, "PTC 10 Ом", size=9, bold=True, color="#854d0e"))

    b_coord, _, _ = textbox(x_coord, 180, "Координація:\nПадіння L·di/dt та R·I\nзмушує GDT спалахнути\nдо пробою TVS",
                            size=9, color="#854d0e", fill="#fefce8", stroke="#ca8a04", sw=1.2, min_w=140)
    p.append(b_coord)

    # ── Ступінь 2: TVS-діоди (Швидке обмеження) ──
    p.append(line(x_tvs, 100, x_tvs, 150, color=INK, sw=1.8))
    # Блок TVS
    p.append(rect(x_tvs - 20, 150, 40, 60, fill="#eff6ff", stroke=NEG, sw=1.6, rx=3))
    p.append(text(x_tvs, 175, "TVS", size=11, bold=True, color=NEG))
    p.append(text(x_tvs, 195, "±15 В", size=9, color=NEG))
    p.append(line(x_tvs, 210, x_tvs, 260, color=INK, sw=1.8))

    b_st2, _, _ = textbox(x_tvs, 45, "Ступінь 2 (Тонкий):\nШвидкий (<1 нс)\nОбмеження до V_clamp ≈ 15 В",
                          size=9, color=NEG, fill="#eff6ff", stroke=NEG, sw=1.2, min_w=150)
    p.append(b_st2)

    # ── Ступінь 3: Гальванічна розв'язка ──
    p.append(rect(x_iso, 80, 130, 200, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(x_iso + 65, 110, "Гальванічна", size=11, bold=True, color=FIELD))
    p.append(text(x_iso + 65, 128, "розв'язка", size=11, bold=True, color=FIELD))
    p.append(text(x_iso + 65, 160, "Цифровий", size=10, color=INK))
    p.append(text(x_iso + 65, 176, "ізолятор SiO2", size=10, bold=True, color=INK))
    p.append(text(x_iso + 65, 200, "5 кВ RMS /", size=10, color=MUTED))
    p.append(text(x_iso + 65, 216, "CMTI > 100 кВ/мкс", size=9, bold=True, color=FIELD))
    p.append(text(x_iso + 65, 250, "→ До МК / SoC", size=10, bold=True, color=INK))

    p.append(text(W / 2, H - 15,
                  "Трирівнева ієрархія захисту: GDT скидає енергію в PE → PTC обмежує струм → TVS фіксує напругу → Ізолятор блокує перекіс потенціалів",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "surge-protection-cascade-stages.svg"), W, H, *p,
           title="Багаторівневий захист інтерфейсу від комутаційних сплесків та перенапруги")


# ── 4. insulation-and-cm-monitor-circuit: Схема вимірювання синфазного шуму ───
def fig_insulation_and_cm_monitor_circuit():
    W, H = 840, 420
    p = []

    # Польові лінії A і B
    p.append(line(40, 90, 260, 90, color=FIELD, sw=2.2))
    p.append(text(50, 75, "Field Line A (RS-485+)", size=10, bold=True, color=FIELD, anchor="start"))

    p.append(line(40, 230, 260, 230, color=FIELD, sw=2.2))
    p.append(text(50, 250, "Field Line B (RS-485−)", size=10, bold=True, color=FIELD, anchor="start"))

    # Дільник для виділення синфазної напруги V_CM = (V_A + V_B)/2
    p.append(line(220, 90, 220, 130, color=INK, sw=1.6))
    p.append(rect(210, 130, 20, 30, fill=BG, stroke=INK, sw=1.4, rx=2))
    p.append(text(240, 148, "R1 (1 МОм)", size=9, color=INK, anchor="start"))

    p.append(line(220, 230, 220, 190, color=INK, sw=1.6))
    p.append(rect(210, 160, 20, 30, fill=BG, stroke=INK, sw=1.4, rx=2))
    p.append(text(240, 178, "R2 (1 МОм)", size=9, color=INK, anchor="start"))

    # Центральна точка V_CM
    p.append(circle(220, 160, 4, fill=POS, stroke=POS, sw=1))
    p.append(line(220, 160, 340, 160, color=POS, sw=2.0))
    p.append(text(280, 148, "V_CM (сира)", size=10, bold=True, color=POS))

    # Масштабування та зсув рівня (Level Shifter / Attenuator)
    p.append(rect(340, 110, 150, 100, fill="#f8fafc", stroke=NEG, sw=1.6, rx=6))
    p.append(text(415, 135, "Масштабування", size=11, bold=True, color=NEG))
    p.append(text(415, 155, "та зсув рівня", size=11, bold=True, color=NEG))
    p.append(text(415, 180, "±15 В → 0...3.3 В", size=10, color=MUTED))
    p.append(text(415, 196, "(V_ref = 1.65 В)", size=9, color=MUTED))

    # Вихід на АЦП каналу синфазної напруги
    p.append(arrow(490, 160, 580, 160, color=NEG, sw=2.2))
    p.append(text(535, 148, "ADC_CH1", size=10, bold=True, color=NEG))

    # ── Блок тестування ізоляції (Insulation Resistance Injection) ──
    p.append(rect(180, 300, 310, 95, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    p.append(text(335, 322, "Вузол інжекції тестового струму ізоляції", size=11, bold=True, color="#854d0e"))
    p.append(text(335, 342, "Високовольтний ключ + вимірювальний шунт R_shunt", size=9, color="#854d0e"))
    p.append(text(335, 362, "Виявлення витоку на PE (R_iso < 500 кОм)", size=9, bold=True, color=POS))
    p.append(text(335, 380, "Керування: GPIO_ISO_TEST від МК", size=9, color=MUTED))

    # З'єднання інжектора з лінією і виходом
    p.append(line(180, 350, 100, 350, color="#ca8a04", sw=1.6))
    p.append(line(100, 350, 100, 230, color="#ca8a04", sw=1.6))
    p.append(arrow(490, 350, 580, 350, color="#ca8a04", sw=2.2))
    p.append(text(535, 338, "ADC_CH2 (R_iso)", size=9, bold=True, color="#854d0e"))

    # Мікроконтролер (Обробка, Фільтрація, Автомат станів)
    p.append(rect(580, 90, 220, 305, fill="none", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(690, 120, "Мікроконтролер (МК)", size=13, bold=True, color=FIELD))
    b_mcu, _, _ = textbox(690, 225,
                          "Драйвер діагностики:\n• Обчислення V_CM (середнє + RMS)\n• Виявлення спектральних сплесків 50 Гц / кГц\n• Вимірювання опору ізоляції R_iso\n• Автомат станів безпеки\n• Генерація тривог та ізольований shutdown",
                          size=9, color=INK, fill=BG, stroke="#bfdbfe", sw=1.2, min_w=200)
    p.append(b_mcu)
    p.append(text(690, 360, "→ Аварійне відключення", size=10, bold=True, color=POS))
    p.append(text(690, 378, "та запис у журнал подій", size=9, color=MUTED))

    render(os.path.join(OUT, "insulation-and-cm-monitor-circuit.svg"), W, H, *p,
           title="Апаратна топологія моніторингу синфазного шуму та опору ізоляції")


if __name__ == "__main__":
    fig_floating_ground_y_capacitors()
    fig_ground_loop_common_mode()
    fig_surge_protection_cascade_stages()
    fig_insulation_and_cm_monitor_circuit()
    print("Усі 4 фігури успішно згенеровано.")
