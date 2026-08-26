# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. power-tree-architecture: Архітектура розподілу живлення плати ────────
def fig_power_tree():
    W, H = 820, 480
    p = []

    p.append(text(W / 2, 28, "Двокаскадна архітектура живлення змішаної плати", size=15, bold=True, color=INK))

    b_src, _, _ = textbox(90, 220, "Джерело\nLi-Ion (3.0–4.2 В)\nабо USB (5.0 В)", size=11, bold=True,
                          fill="#fef9e7", stroke="#e67e22", sw=1.8, pad=8)
    p.append(b_src)

    b_prot, _, _ = textbox(225, 220, "Вхідний захист\n• Ключ від переполюсовки\n• eFuse / Inrush limiter", size=10,
                           fill="#f4f6f8", stroke=LINE, sw=1.5, pad=7)
    p.append(b_prot)
    p.append(arrow(145, 220, 165, 220, color=LINE, sw=1.8))

    b_buck, _, _ = textbox(380, 220, "Синхронний Buck DC-DC\n• ККД ≈ 92%\n• Вихід: шина 3.6 В / 1.5 А\n(проміжна шина)", size=11, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=2.0, pad=9)
    p.append(b_buck)
    p.append(arrow(288, 220, 305, 220, color=LINE, sw=1.8))

    p.append(circle(465, 220, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(455, 220, 465, 220, color=FIELD, sw=2.2))

    # Верхня гілка: Цифровий домен
    p.append(line(465, 220, 465, 120, color=POS, sw=2.0))
    p.append(arrow(465, 120, 520, 120, color=POS, sw=2.0))

    b_dig, _, _ = textbox(660, 120, "Цифровий домен (Шина 3.3 В):\n• Мікроконтролер (ядро + периферія)\n• Радіотрансивер (Wi-Fi / BLE / LoRa)\n• Зовнішня пам'ять SPI Flash / FRAM\n• Світлодіоди та дисплей",
                          size=10, bold=False, fill="#fdecea", stroke=POS, sw=1.8, pad=9)
    p.append(b_dig)

    # Нижня гілка: Аналоговий домен
    p.append(line(465, 220, 465, 340, color=NEG, sw=2.0))
    p.append(arrow(465, 340, 510, 340, color=NEG, sw=2.0))

    b_ldo, _, _ = textbox(570, 340, "Вторинний LDO (High PSRR)\n• Вхід: 3.6 В → Вихід: 3.3 В\n• Падіння ΔV = 0.3 В (малий нагрів)\n• Придушення шуму > 60 дБ", size=10, bold=True,
                          fill="#eaf0fd", stroke=NEG, sw=1.8, pad=8)
    p.append(b_ldo)

    p.append(arrow(645, 340, 680, 340, color=NEG, sw=2.0))

    b_ana, _, _ = textbox(745, 340, "Аналоговий тракт:\n• 16-бітний АЦП\n• Прецизійна опора Vref\n• Підсилювачі сенсорів", size=10,
                          fill="#f2ecf8", stroke="#8a5fb0", sw=1.8, pad=8)
    p.append(b_ana)

    p.append(text(W / 2, 455, "Buck бере на себе високий струм і ККД, а вторинний LDO очищає живлення аналогових кіл від комутаційного шуму",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "power-tree-architecture.svg"), W, H, *p,
           title="Архітектура розподілу живлення багатокомпонентної плати")


# ── 2. thermal-resistance-stack: Теплова модель силового компонента ──────────
def fig_thermal_stack():
    W, H = 840, 440
    p = []

    p.append(text(W / 2, 28, "Тепловий ланцюг: розсіювання тепла від кристала в довкілля", size=15, bold=True, color=INK))

    x0, y0 = 40, 60

    # 1. Кристал (Junction)
    b_die, _, _ = textbox(x0 + 160, y0 + 35, "Кристал мікросхеми (Junction)  T_j\nГенерація тепла P_loss = (V_in − V_out) · I_out",
                          size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=7)
    p.append(b_die)

    # 2. Корпус / Exposed Pad
    b_case, _, _ = textbox(x0 + 160, y0 + 95, "Теплове падло корпусу (Exposed Pad)  T_c\nТепловий опір θ_JC",
                           size=10, bold=True, fill="#fef9e7", stroke="#e67e22", sw=1.6, pad=6)
    p.append(b_case)
    p.append(arrow(x0 + 160, y0 + 58, x0 + 160, y0 + 72, color=POS, sw=2.0))

    # 3. Верхній мідний полігон плати
    b_top, _, _ = textbox(x0 + 160, y0 + 155, "Верхній мідний полігон друкованої плати (Top Copper)\nПайка припоєм до термопаду (опір θ_CS)",
                          size=10, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.6, pad=6)
    p.append(b_top)
    p.append(arrow(x0 + 160, y0 + 118, x0 + 160, y0 + 132, color="#e67e22", sw=2.0))

    # 4. Текстоліт з тепловими віасами
    b_vias, _, _ = textbox(x0 + 160, y0 + 225, "Масив теплових перехідних отворів (Thermal Vias 3×3)\nТекстоліт FR4 (товщина 1.6 мм, крок віасів 1.0 мм)",
                           size=10, bold=False, fill="#f4f6f8", stroke=LINE, sw=1.5, pad=6)
    p.append(b_vias)
    p.append(arrow(x0 + 160, y0 + 178, x0 + 160, y0 + 202, color=FIELD, sw=2.0))

    # 5. Нижній мідний земляний шар
    b_bot, _, _ = textbox(x0 + 160, y0 + 295, "Нижній суцільний мідний шар заземлення (GND Plane)\nРозсіювання тепла в повітря конвекцією (опір θ_SA)",
                          size=10, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.6, pad=6)
    p.append(b_bot)
    p.append(arrow(x0 + 160, y0 + 248, x0 + 160, y0 + 272, color=FIELD, sw=2.0))

    # 6. Довкілля
    b_amb_l, _, _ = textbox(x0 + 160, y0 + 355, "Навколишнє середовище (Ambient air)  T_a",
                            size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, pad=6)
    p.append(b_amb_l)
    p.append(arrow(x0 + 160, y0 + 318, x0 + 160, y0 + 335, color=NEG, sw=2.0))

    # Справа: еквівалентна електрична схема теплового ланцюга
    cx = 600
    p.append(text(cx, 75, "Еквівалентна теплова схема (аналог закону Ома)", size=12, bold=True, color=INK))

    b_gen, _, _ = textbox(cx, 115, "Джерело тепла P_loss = (V_in − V_out) · I_out", size=10, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.5, pad=6)
    p.append(b_gen)

    elements = [
        (cx, 175, "θ_JC (перехід − корпус)\nвнутрішній опір кристала", POS),
        (cx, 245, "θ_CS (корпус − полігон)\nтермопаста / пайка", "#e67e22"),
        (cx, 315, "θ_SA (полігон − повітря)\nплоща міді + сітка віасів", FIELD)
    ]

    py_prev = 135
    for ex, ey, elab, ecol in elements:
        p.append(line(cx, py_prev, cx, ey - 22, color=ecol, sw=2.0))
        b_el, _, _ = textbox(ex, ey, elab, size=10, bold=True, fill="#ffffff", stroke=ecol, sw=1.6, pad=6)
        p.append(b_el)
        py_prev = ey + 22

    p.append(line(cx, py_prev, cx, 370, color=NEG, sw=2.0))
    b_amb, _, _ = textbox(cx, 385, "T_a (температура довкілля)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=6)
    p.append(b_amb)

    render(os.path.join(OUT, "thermal-resistance-stack.svg"), W, H, *p,
           title="Тепловий ланцюг розсіювання потужності силового компонента")


# ── 3. pulse-profile-capacitor-hold: Динамічний піковий струм та буферизація ──
def fig_pulse_hold():
    W, H = 800, 440
    p = []

    p.append(text(W / 2, 28, "Динамічний сплеск струму та компенсація розв'язувальними конденсаторами", size=15, bold=True, color=INK))

    ox, oy = 80, 350
    aw, ah = 650, 270

    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.6))

    p.append(text(ox + aw - 10, oy + 25, "Час t →", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - ah + 10, "Струм I / Напруга V", size=11, color=MUTED, anchor="end"))

    t_start = ox + 80
    t_rise = ox + 100
    t_fall = ox + 380
    t_end = ox + 400

    y_idle = oy - 30
    y_peak = oy - 220

    i_pts = [
        f"{ox},{y_idle}", f"{t_start},{y_idle}", f"{t_rise},{y_peak}",
        f"{t_fall},{y_peak}", f"{t_end},{y_idle}", f"{ox + aw},{y_idle}"
    ]
    p.append(f'<polyline points="{" ".join(i_pts)}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-linejoin="round"/>')
    p.append(text(t_rise + 120, y_peak - 12, "Струм радіотрансивера I_peak ≈ 350 мА (TX Burst)", size=11, bold=True, color=POS))
    p.append(text(t_start - 10, y_idle - 10, "I_idle ≈ 20 мА", size=10, color=POS, anchor="end"))

    y_vnom = oy - 140
    y_vdrop_bad = oy - 50
    y_vdrop_good = oy - 120

    v_bad_pts = [
        f"{ox},{y_vnom}", f"{t_start},{y_vnom}", f"{t_rise + 30},{y_vdrop_bad}",
        f"{t_fall},{y_vdrop_bad + 15}", f"{t_end + 50},{y_vnom}", f"{ox + aw},{y_vnom}"
    ]
    p.append(f'<polyline points="{" ".join(v_bad_pts)}" fill="none" stroke="#8a5fb0" stroke-width="2.0" stroke-dasharray="5 4" stroke-linejoin="round"/>')
    p.append(text(t_rise + 180, y_vdrop_bad + 22, "Без буферної ємності: глибоке просідання → Brownout Reset (МК зависає)", size=10, bold=True, color="#8a5fb0"))

    v_good_pts = [
        f"{ox},{y_vnom}", f"{t_start},{y_vnom}", f"{t_rise + 20},{y_vdrop_good}",
        f"{t_fall},{y_vdrop_good + 5}", f"{t_end + 30},{y_vnom}", f"{ox + aw},{y_vnom}"
    ]
    p.append(f'<polyline points="{" ".join(v_good_pts)}" fill="none" stroke="{NEG}" stroke-width="2.5" stroke-linejoin="round"/>')
    p.append(text(t_rise + 180, y_vdrop_good - 12, "З розрахованою Bulk-ємністю: допустиме просідання ΔV ≤ 100 мВ", size=10, bold=True, color=NEG))

    y_bor = oy - 70
    p.append(line(ox, y_bor, ox + aw, y_bor, color=POS, sw=1.2, dash="3 3"))
    p.append(text(ox + aw - 10, y_bor - 6, "Поріг скидання Brownout Reset (V_BOR = 2.7 В)", size=9, bold=True, color=POS, anchor="end"))

    p.append(line(ox, y_vnom, ox + aw, y_vnom, color=LINE, sw=1.0, dash="2 2"))
    p.append(text(ox - 10, y_vnom + 4, "3.3 В", size=10, color=INK, anchor="end"))

    p.append(text(W / 2, 420, "Локальні конденсатори компенсують затримку реакції стабілізатора, утримуючи напругу шини вище порога Brownout",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pulse-profile-capacitor-hold.svg"), W, H, *p,
           title="Динаміка струму та стабілізація напруги розв'язувальними конденсаторами")


# ── 4. battery-discharge-and-cutoff: Розрядні криві акумуляторів та поріг відсікання
def fig_battery_cutoff():
    W, H = 800, 440
    p = []

    p.append(text(W / 2, 28, "Розрядні криві Li-Ion та LiFePO4: вплив напруги відсікання на корисну ємність", size=15, bold=True, color=INK))

    ox, oy = 80, 360
    aw, ah = 650, 280

    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.6))

    p.append(text(ox + aw - 10, oy + 28, "Віддана ємність (% від номіналу) →", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - ah + 10, "Напруга банки (В)", size=11, color=MUTED, anchor="end"))

    for v_val, v_lbl in [(2.5, "2.5 В"), (3.0, "3.0 В"), (3.3, "3.3 В"), (3.5, "3.5 В"), (3.7, "3.7 В"), (4.2, "4.2 В")]:
        y_pos = oy - (v_val - 2.0) * (ah / 2.5)
        p.append(line(ox - 5, y_pos, ox, y_pos, color=LINE, sw=1.0))
        p.append(text(ox - 10, y_pos + 4, v_lbl, size=9, color=MUTED, anchor="end"))

    for cap_val in [0, 20, 40, 60, 80, 100]:
        x_pos = ox + cap_val * (aw / 100)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=LINE, sw=1.0))
        p.append(text(x_pos, oy + 18, f"{cap_val}%", size=9, color=MUTED))

    liion_pts = []
    liion_data = [
        (0, 4.20), (5, 4.05), (10, 3.92), (20, 3.82), (30, 3.75),
        (40, 3.70), (50, 3.65), (60, 3.60), (70, 3.52), (80, 3.42),
        (90, 3.25), (95, 3.10), (100, 2.80)
    ]
    for cap, v in liion_data:
        gx = ox + cap * (aw / 100)
        gy = oy - (v - 2.0) * (ah / 2.5)
        liion_pts.append(f"{gx:.1f},{gy:.1f}")

    p.append(f'<polyline points="{" ".join(liion_pts)}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-linejoin="round"/>')
    p.append(text(ox + 200, oy - 230, "Li-Ion / Li-Po (номінал 3.7 В, діапазон 4.2 → 3.0 В)", size=11, bold=True, color=POS))

    lifepo4_pts = []
    lifepo4_data = [
        (0, 3.60), (3, 3.35), (10, 3.25), (30, 3.22), (50, 3.20),
        (70, 3.18), (85, 3.12), (92, 3.00), (97, 2.80), (100, 2.50)
    ]
    for cap, v in lifepo4_data:
        gx = ox + cap * (aw / 100)
        gy = oy - (v - 2.0) * (ah / 2.5)
        lifepo4_pts.append(f"{gx:.1f},{gy:.1f}")

    p.append(f'<polyline points="{" ".join(lifepo4_pts)}" fill="none" stroke="{FIELD}" stroke-width="2.5" stroke-linejoin="round"/>')
    p.append(text(ox + 420, oy - 148, "LiFePO4 (пласке плато 3.2 В, діапазон 3.65 → 2.5 В)", size=11, bold=True, color=FIELD))

    y_cut_ldo = oy - (3.5 - 2.0) * (ah / 2.5)
    p.append(line(ox, y_cut_ldo, ox + aw, y_cut_ldo, color="#8a5fb0", sw=1.8, dash="5 4"))
    b_ldo_cut, _, _ = textbox(ox + 450, y_cut_ldo - 18, "Поріг відсікання LDO на 3.3 В (V_in = 3.5 В): втрачається > 30% ємності Li-Ion!",
                              size=10, bold=True, fill="#f2ecf8", stroke="#8a5fb0", sw=1.5, pad=6)
    p.append(b_ldo_cut)

    y_cut_bb = oy - (3.0 - 2.0) * (ah / 2.5)
    p.append(line(ox, y_cut_bb, ox + aw, y_cut_bb, color=NEG, sw=1.8, dash="5 4"))
    b_bb_cut, _, _ = textbox(ox + 260, y_cut_bb + 22, "Поріг відсікання Buck-Boost / низьковольтного МК (3.0 В): утилізація 98% енергії",
                             size=10, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=6)
    p.append(b_bb_cut)

    p.append(text(W / 2, 420, "Правильний вибір регулятора розширює доступний діапазон напруги, вивільняючи приховану ємність акумулятора",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "battery-discharge-and-cutoff.svg"), W, H, *p,
           title="Розрядні криві та відсікання за напругою")


if __name__ == "__main__":
    fig_power_tree()
    fig_thermal_stack()
    fig_pulse_hold()
    fig_battery_cutoff()
    print("OK: figures generated successfully to", OUT)
