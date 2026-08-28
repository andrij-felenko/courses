# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. loss-breakdown: Розподіл теплових втрат у силовій установці ──────────
def fig_loss_breakdown():
    W, H = 880, 520
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 28, "Джерела розсіювання тепла в силовій установці BLDC + ESC", size=16, bold=True, color=INK))

    # Ліва колонка: BLDC Мотор
    p.append(rect(30, 60, 390, 420, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(225, 88, "Електродвигун (BLDC Motor)", size=14, bold=True, color=INK))

    # 1.1 Мідні втрати
    b_cu, _, _ = textbox(225, 155, "Омічні втрати в міді (Copper Losses)\nP_cu = 3/2 · I_phase² · R_phase(T)\n• Нагрів збільшує опір міді: +0.393%/°C\n• Домінують при великій тязі й перегазовках",
                         size=10, bold=False, fill="#fdecea", stroke=POS, sw=1.8, pad=8)
    p.append(b_cu)

    # 1.2 Магнітні втрати (залізо)
    b_fe, _, _ = textbox(225, 275, "Магнітні втрати в статорі (Iron/Core Losses)\nP_fe = P_hysteresis + P_eddy\n• Гістерезис: перемагнічування сталі ~ f_elec · B^1.6\n• Вихрові струми Фуко: ~ f_elec² · B² · d_lam²\n• Ростуть з обертами (RPM) навіть без тяги",
                         size=10, bold=False, fill="#fef9e7", stroke="#e67e22", sw=1.8, pad=8)
    p.append(b_fe)

    # 1.3 Механічні втрати
    b_mech, _, _ = textbox(225, 395, "Механічні й аеродинамічні втрати\nP_mech = P_bearing + P_windage\n• Тертя в кулькових підшипниках\n• Аеродинамічний опір ротора / дзвона",
                           size=10, bold=False, fill="#f4f6f8", stroke=MUTED, sw=1.5, pad=8)
    p.append(b_mech)

    # Права колонка: ESC Регулятор
    p.append(rect(460, 60, 390, 420, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(655, 88, "Регулятор швидкості (ESC)", size=14, bold=True, color=INK))

    # 2.1 Втрати провідності
    b_cond, _, _ = textbox(655, 155, "Втрати провідності ключів (Conduction)\nP_cond = 2 · I_rms² · R_DS(on)(T_j)\n• R_DS(on) подвоюється при нагріванні до 150°C\n• Пряме джоулеве тепло відкритого каналу",
                           size=10, bold=False, fill="#fdecea", stroke=POS, sw=1.8, pad=8)
    p.append(b_cond)

    # 2.2 Комутаційні втрати
    b_sw, _, _ = textbox(655, 275, "Динамічні комутаційні втрати (Switching)\nP_sw = V_in · I_out · f_pwm · (t_rise + t_fall)\n• Енергія розсіювання під час перемикання V·I\n• Залежать від ємності затвора Q_g та драйвера\n• Зростають лінійно з частотою ШІМ (24→48→96 кГц)",
                         size=10, bold=False, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=8)
    p.append(b_sw)

    # 2.3 Додаткові втрати (Dead-time, ESR)
    b_misc, _, _ = textbox(655, 395, "Втрати мертвого часу та конденсаторів\n• Провідність body-діода під час dead-time\n• Втрати заряду затвора P_gate = Q_g · V_gs · f_pwm\n• Пульсації струму на ESR електролітів шини",
                           size=10, bold=False, fill="#f4f6f8", stroke=MUTED, sw=1.5, pad=8)
    p.append(b_misc)

    p.append(text(W / 2, 500, "Тепловий баланс: мотор страждає від пікового струму й високих обертів, а регулятор — від перегріву R_DS(on) і частоти ШІМ",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "loss-breakdown.svg"), W, H, *p)


# ── 2. demagnetization-curve: Температурне розмагнічування магнітів NdFeB ───
def fig_demagnetization():
    W, H = 860, 480
    p = []

    p.append(text(W / 2, 28, "Криві розмагнічування та втрата коерцитивної сили NdFeB при нагріванні", size=15, bold=True, color=INK))

    # Графік B-H у 2-му квадранті
    gx0, gy0, gw, gh = 80, 70, 440, 320
    p.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#cccccc", sw=1.0, rx=4))

    # Сітка
    for y_val in [gy0 + 80, gy0 + 160, gy0 + 240]:
        p.append(line(gx0, y_val, gx0 + gw, y_val, color="#eef0f2", sw=1.0, dash="3,3"))
    for x_val in [gx0 + 110, gx0 + 220, gx0 + 330]:
        p.append(line(x_val, gy0, x_val, gy0 + gh, color="#eef0f2", sw=1.0, dash="3,3"))

    # Осі
    p.append(line(gx0, gy0 + gh - 40, gx0 + gw, gy0 + gh - 40, color=LINE, sw=1.8)) # Вісь H
    p.append(line(gx0 + gw - 40, gy0, gx0 + gw - 40, gy0 + gh, color=LINE, sw=1.8)) # Вісь B

    p.append(text(gx0 + gw - 35, gy0 + 20, "B [Тл]", size=11, bold=True, anchor="start"))
    p.append(text(gx0 + 20, gy0 + gh - 46, "−H [кА/м]", size=11, bold=True, anchor="start"))
    p.append(text(gx0 + gw - 32, gy0 + gh - 24, "0", size=10, color=MUTED))

    # Криві 20°C, 80°C, 120°C, 150°C
    # 20°C (холодний, лінійний робочий діапазон)
    p.append(line(gx0 + gw - 40, gy0 + 40, gx0 + 120, gy0 + 65, color=FIELD, sw=2.5))
    p.append(line(gx0 + 120, gy0 + 65, gx0 + 70, gy0 + gh - 40, color=FIELD, sw=2.0, dash="4,2"))
    p.append(text(gx0 + 140, gy0 + 55, "20 °C (N52 лінійний)", size=10, bold=True, color=FIELD, anchor="start"))

    # 80°C (поява коліна розмагнічування для N52)
    p.append(line(gx0 + gw - 40, gy0 + 75, gx0 + 210, gy0 + 100, color="#e67e22", sw=2.5))
    p.append(line(gx0 + 210, gy0 + 100, gx0 + 160, gy0 + gh - 40, color="#e67e22", sw=2.0, dash="4,2"))
    p.append(text(gx0 + 225, gy0 + 92, "80 °C (N52 критична межа)", size=10, bold=True, color="#e67e22", anchor="start"))

    # 130°C (критичне падіння Br і коерцитивної сили)
    p.append(line(gx0 + gw - 40, gy0 + 120, gx0 + 310, gy0 + 140, color=POS, sw=2.5))
    p.append(line(gx0 + 310, gy0 + 140, gx0 + 260, gy0 + gh - 40, color=POS, sw=2.0, dash="4,2"))
    p.append(text(gx0 + 320, gy0 + 130, "130 °C (незворотна втрата)", size=10, bold=True, color=POS, anchor="start"))

    # Точка коліна (Knee point)
    p.append(circle(gx0 + 210, gy0 + 100, 5, fill=POS, stroke="#900c3f", sw=1.5))
    p.append(text(gx0 + 210, gy0 + 125, "Коліно перегину (Knee Point)", size=9, bold=True, color=POS))

    # Права інформаційна панель: Марки неодимових магнітів
    b_grades, _, _ = textbox(690, 160, "Температурні класи NdFeB:\n\n• N52 (Standard): T_max = 80 °C\n  Дешеві мотори; швидке розмагнічування\n• N52H (High Temp): T_max = 120 °C\n  Оптимальний вибір для фристайлу/FPV\n• N52SH (Super High): T_max = 150 °C\n  Важкі дрони, витривалість під навантаженням\n• N52UH / EH: T_max = 180–200 °C\n  Спеціальні індустріальні приводи\n\nТочка Кюрі T_c ≈ 310–320 °C (повний нуль поля)",
                             size=10, bold=False, fill="#fdfefe", stroke=LINE, sw=1.5, pad=10)
    p.append(b_grades)

    b_conseq, _, _ = textbox(690, 345, "Наслідки перегріву ротора:\n1. Падіння залишкової індукції B_r → дрейф K_v вгору\n2. Зниження крутного моменту: τ = k_t · I_phase\n3. Необоротне розмагнічування від зустрічного\n   магнітного поля статора при перегазовках",
                             size=10, bold=False, fill="#fdecea", stroke=POS, sw=1.6, pad=9)
    p.append(b_conseq)

    p.append(text(W / 2, 455, "Коли температура магніту перевищує робочу межу марки, зустрічне поле статора необоротно зсуває робочу точку за коліно перегину",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "demagnetization-curve.svg"), W, H, *p)


# ── 3. cooling-airflow: Аеродинаміка охолодження мотора та регулятора ───────
def fig_cooling_airflow():
    W, H = 880, 480
    p = []

    p.append(text(W / 2, 28, "Шляхи розсіювання тепла: обдування гвинтом та відцентрова вентиляція", size=15, bold=True, color=INK))

    # Секція А: Мотор із відцентровими вентиляційними отворами
    p.append(rect(30, 60, 400, 370, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(230, 88, "Охолодження BLDC мотора", size=13, bold=True, color=INK))

    # Дзвін ротора та статор
    p.append(rect(100, 120, 260, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(230, 148, "Обертовий дзвін ротора (Bell)", size=11, bold=True, color=NEG))

    p.append(rect(130, 185, 200, 70, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(230, 210, "Статор та мідні обмотки", size=11, bold=True, color=POS))
    p.append(text(230, 235, "Головний генератор тепла (I²R + Iron)", size=9, color=MUTED))

    # Стрілки повітряного потоку
    p.append(arrow(60, 145, 95, 145, color=FIELD, sw=2.2))
    p.append(text(75, 132, "Вхід", size=9, bold=True, color=FIELD))

    p.append(arrow(230, 172, 230, 183, color=FIELD, sw=2.0))
    p.append(arrow(332, 220, 375, 220, color=FIELD, sw=2.2))
    p.append(text(360, 208, "Вихід", size=9, bold=True, color=FIELD))

    b_mot_notes, _, _ = textbox(230, 335, "Конструктивні фактори охолодження:\n• Відцентрові крильчатки в базі дзвона (Centrifugal Vents)\n• Набігаючий потік від гвинта (Prop Wash / Slipstream)\n• Теплопровідність до карбонового променя рами\n• Режим висіння (Hover): потік малий, нагрів максимальний",
                                size=10, bold=False, fill="#f4f6f8", stroke=LINE, sw=1.5, pad=8)
    p.append(b_mot_notes)

    # Секція Б: Регулятор ESC на промені
    p.append(rect(450, 60, 400, 370, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(650, 88, "Охолодження регулятора (ESC)", size=13, bold=True, color=INK))

    # Структура ESC: Радіатор + MOSFET + Плата
    p.append(rect(520, 120, 260, 25, fill="#e8f8f5", stroke=FIELD, sw=1.6, rx=2))
    p.append(text(650, 136, "Алюмінієвий радіатор / Heatsink", size=10, bold=True, color=FIELD))

    p.append(rect(540, 150, 220, 20, fill="#fef9e7", stroke="#e67e22", sw=1.5, rx=2))
    p.append(text(650, 163, "Термопрокладка / Thermal Pad (θ_CS)", size=9, color="#e67e22"))

    p.append(rect(520, 175, 260, 30, fill="#fdecea", stroke=POS, sw=1.8, rx=2))
    p.append(text(650, 193, "Силові MOSFET ключі (Junction T_j)", size=10, bold=True, color=POS))

    p.append(rect(500, 210, 300, 35, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=2))
    p.append(text(650, 226, "Багатошарова друкована плата (2–4 oz міді + Vias)", size=9, color=INK))
    p.append(text(650, 238, "Тепловий розподіл по внутрішніх шарах", size=9, color=MUTED))

    # Стрілка обдування
    p.append(arrow(470, 132, 515, 132, color=FIELD, sw=2.2))
    p.append(text(485, 120, "Обдув", size=9, bold=True, color=FIELD))

    b_esc_notes, _, _ = textbox(650, 335, "Правила монтажу ESC:\n• Розміщення прямо під струменем гвинта на промені\n• Термоусадка (Heatshrink) ізолює тепло — робити вікно!\n• Товсті мідні шари (3 oz / 105 мкм) знижують опір плати\n• ESC 4-в-1 у закритому фюзеляжі перегрівається в 2.5 рази швидше",
                                size=10, bold=False, fill="#f4f6f8", stroke=LINE, sw=1.5, pad=8)
    p.append(b_esc_notes)

    p.append(text(W / 2, 455, "Прямий набігаючий потік від лопатей знижує тепловий опір у повітря R_θ у 3–5 разів порівняно зі стоячим повітрям",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cooling-airflow.svg"), W, H, *p)


# ── 4. thermal-rc-network: Еквівалентна теплова RC-схема мотора і регулятора 
def fig_thermal_rc():
    W, H = 880, 460
    p = []

    p.append(text(W / 2, 28, "Еквівалентна багатоланкова теплова RC-модель (Motor & ESC Thermal Model)", size=15, bold=True, color=INK))

    # Верхній ланцюг: Мотор (Обмотка → Сердечник → Корпус → Довкілля)
    p.append(text(70, 75, "Мотор:", size=13, bold=True, color=INK, anchor="start"))

    # Джерело тепла обмоток P_cu
    p.append(circle(140, 130, 22, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(140, 134, "P_cu", size=11, bold=True, color=POS))
    p.append(text(140, 95, "Втрати міді", size=9, color=MUTED))

    # Вузол T_winding + C_th_wind
    p.append(line(162, 130, 240, 130, color=LINE, sw=1.8))
    p.append(circle(240, 130, 4, fill=LINE, stroke=LINE, sw=1))
    p.append(text(240, 115, "T_wind", size=10, bold=True, color=POS))

    p.append(line(240, 130, 240, 175, color=LINE, sw=1.5))
    b_cw, _, _ = textbox(240, 195, "C_th_wind\n(Ємність міді)", size=9, fill="#fef9e7", stroke=LINE, pad=5)
    p.append(b_cw)

    # Опір R_th_wi (обмотка -> залізо)
    b_rwi, _, _ = textbox(330, 130, "R_th_wi\n(Ізоляція)", size=9, fill="#ffffff", stroke=LINE, pad=5)
    p.append(b_rwi)
    p.append(line(240, 130, 290, 130, color=LINE, sw=1.8))
    p.append(line(370, 130, 430, 130, color=LINE, sw=1.8))

    # Вузол T_iron + P_iron + C_th_iron
    p.append(circle(430, 130, 4, fill=LINE, stroke=LINE, sw=1))
    p.append(text(430, 115, "T_iron", size=10, bold=True, color="#e67e22"))

    p.append(line(430, 130, 430, 175, color=LINE, sw=1.5))
    b_ci, _, _ = textbox(430, 195, "C_th_iron\n(Ємність сталі)", size=9, fill="#fef9e7", stroke=LINE, pad=5)
    p.append(b_ci)

    # Опір R_th_ia (залізо -> корпус/повітря)
    b_ria, _, _ = textbox(530, 130, "R_th_ia\n(Конвекція)", size=9, fill="#ffffff", stroke=FIELD, pad=5)
    p.append(b_ria)
    p.append(line(430, 130, 490, 130, color=LINE, sw=1.8))
    p.append(line(570, 130, 640, 130, color=FIELD, sw=1.8))

    # Вузол T_amb
    p.append(circle(640, 130, 4, fill=NEG, stroke=NEG, sw=1))
    p.append(text(640, 115, "T_amb", size=10, bold=True, color=NEG))
    p.append(text(640, 148, "Довкілля", size=9, color=MUTED))


    # Розділювальна лінія
    p.append(line(50, 240, W - 50, 240, color="#e0e4e8", sw=1.2, dash="4,4"))

    # Нижній ланцюг: ESC MOSFET (Кристал → Радіатор → Довкілля)
    p.append(text(70, 265, "ESC MOSFET:", size=13, bold=True, color=INK, anchor="start"))

    # Джерело тепла P_mosfet
    p.append(circle(140, 320, 22, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(140, 324, "P_mos", size=11, bold=True, color=POS))
    p.append(text(140, 285, "P_cond + P_sw", size=9, color=MUTED))

    # Вузол T_j (Junction) + C_th_j
    p.append(line(162, 320, 250, 320, color=LINE, sw=1.8))
    p.append(circle(250, 320, 4, fill=LINE, stroke=LINE, sw=1))
    p.append(text(250, 305, "T_j (Кристал)", size=10, bold=True, color=POS))

    p.append(line(250, 320, 250, 365, color=LINE, sw=1.5))
    b_cj, _, _ = textbox(250, 385, "C_th_j\n(Кристал ~мс)", size=9, fill="#fef9e7", stroke=LINE, pad=5)
    p.append(b_cj)

    # Опір R_th_jc (кристал -> корпус)
    b_rjc, _, _ = textbox(360, 320, "R_th_jc\n(Кристал-Корпус)", size=9, fill="#ffffff", stroke=LINE, pad=5)
    p.append(b_rjc)
    p.append(line(250, 320, 310, 320, color=LINE, sw=1.8))
    p.append(line(410, 320, 480, 320, color=LINE, sw=1.8))

    # Вузол T_case / Heatsink + C_th_hs
    p.append(circle(480, 320, 4, fill=LINE, stroke=LINE, sw=1))
    p.append(text(480, 305, "T_heatsink", size=10, bold=True, color="#e67e22"))

    p.append(line(480, 320, 480, 365, color=LINE, sw=1.5))
    b_chs, _, _ = textbox(480, 385, "C_th_hs\n(Радіатор ~секунди)", size=9, fill="#fef9e7", stroke=LINE, pad=5)
    p.append(b_chs)

    # Опір R_th_sa (радіатор -> повітря)
    b_rsa, _, _ = textbox(590, 320, "R_th_sa\n(Радіатор-Повітря)", size=9, fill="#ffffff", stroke=FIELD, pad=5)
    p.append(b_rsa)
    p.append(line(480, 320, 530, 320, color=LINE, sw=1.8))
    p.append(line(650, 320, 720, 320, color=FIELD, sw=1.8))

    # Вузол T_amb нижній
    p.append(circle(720, 320, 4, fill=NEG, stroke=NEG, sw=1))
    p.append(text(720, 305, "T_amb", size=10, bold=True, color=NEG))
    p.append(text(720, 338, "Довкілля", size=9, color=MUTED))

    p.append(text(W / 2, 440, "Мала стала часу кристала (мілісекунди) вимагає миттєвого відведення тепла у велику теплоємність радіатора",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thermal-rc-network.svg"), W, H, *p)


if __name__ == "__main__":
    fig_loss_breakdown()
    fig_demagnetization()
    fig_cooling_airflow()
    fig_thermal_rc()
    print("All figures generated successfully.")
