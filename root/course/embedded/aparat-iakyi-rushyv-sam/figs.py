# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. floating-gate-danger: фізика плаваючого затвора та мимовільне відкриття ─
def fig_floating_gate():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 32, "Фізика плаваючого затвора: як стан High-Z вмикає MOSFET", size=15, color=INK, bold=True))

    # Лівий блок: МК у стані скидання (High-Z)
    bx1, bw1, by, bh = 30, 220, 65, 275
    p.append(rect(bx1, by, bw1, bh, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(bx1 + bw1 / 2, by + 28, "Мікроконтролер (MCU)", size=13, color=NEG, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 48, "Стан Reset / Bootloader", size=10.5, color=MUTED, italic=True))
    
    # Вихідний каскад розімкнений
    p.append(rect(bx1 + 20, by + 75, bw1 - 40, 110, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx1 + bw1 / 2, by + 98, "GPIO каскад", size=11, color=INK, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 120, "Верхній ключ: ВИМКНЕНО", size=9.5, color=POS))
    p.append(text(bx1 + bw1 / 2, by + 138, "Нижній ключ: ВИМКНЕНО", size=9.5, color=POS))
    p.append(text(bx1 + bw1 / 2, by + 162, "Вихідний опір > 10 МОм", size=10, color=NEG, bold=True))
    
    p.append(rect(bx1 + 20, by + 200, bw1 - 40, 58, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=6))
    p.append(text(bx1 + bw1 / 2, by + 222, "Вивід у стані High-Z", size=11, color=AMBERTX, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 242, "Пін висить у повітрі", size=9.5, color=INK))

    # Центральний блок: паразитні джерела заряду на затворі
    bx2, bw2 = 280, 260
    p.append(rect(bx2, by, bw2, bh, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(bx2 + bw2 / 2, by + 28, "Затворна ємність (C_iss)", size=13, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 48, "Ізольований діелектрик SiO2", size=10.5, color=MUTED, italic=True))

    p.append(rect(bx2 + 15, by + 75, bw2 - 30, 80, fill=BG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 98, "Паразитні джерела струму:", size=10.5, color=INK, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 118, "• Струми витоку плати (I_leak)", size=9.5, color=INK))
    p.append(text(bx2 + bw2 / 2, by + 136, "• Ємність Міллера (C_gd · dV/dt)", size=9.5, color=POS, bold=True))

    p.append(rect(bx2 + 15, by + 170, bw2 - 30, 88, fill=REDBG, stroke=POS, sw=1.4, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 192, "Напруга зростає: V_gs > V_th", size=11, color=POS, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 212, "Заряд не має куди стікати", size=9.5, color=INK))
    p.append(text(bx2 + bw2 / 2, by + 232, "V_gs досягає 1.5…2.5 В", size=10, color=POS, bold=True))

    # Правий блок: Силовий MOSFET і навантаження
    bx3, bw3 = 570, 240
    p.append(rect(bx3, by, bw3, bh, fill=REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(bx3 + bw3 / 2, by + 28, "Силовий каскад", size=13, color=POS, bold=True))
    p.append(text(bx3 + bw3 / 2, by + 48, "Мотор / Соленоїд / Привід", size=10.5, color=MUTED, italic=True))

    p.append(rect(bx3 + 15, by + 75, bw3 - 30, 80, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(bx3 + bw3 / 2, by + 98, "Стан MOSFET:", size=11, color=INK, bold=True))
    p.append(text(bx3 + bw3 / 2, by + 120, "САМОВІЛЬНЕ ВІДКРИТТЯ", size=11, color=POS, bold=True))
    p.append(text(bx3 + bw3 / 2, by + 140, "Перехід у лінійний режим", size=9.5, color=POS))

    p.append(rect(bx3 + 15, by + 170, bw3 - 30, 88, fill=BG, stroke=POS, sw=1.4, rx=6))
    p.append(text(bx3 + bw3 / 2, by + 192, "АВАРІЙНИЙ НАСЛІДОК:", size=10.5, color=POS, bold=True))
    p.append(text(bx3 + bw3 / 2, by + 214, "• Раптовий ривок мотора", size=10, color=INK, bold=True))
    p.append(text(bx3 + bw3 / 2, by + 236, "• Перегрів та пробій кристала", size=9.5, color=POS))

    # Стрілки зв'язку
    p.append(arrow(bx1 + bw1 + 4, by + 228, bx2 - 4, by + 228, color=AMBERTX, sw=2.2))
    p.append(arrow(bx2 + bw2 + 4, by + 228, bx3 - 4, by + 228, color=POS, sw=2.2))

    # Нижній висновок
    p.append(rect(30, 350, 780, 30, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(W / 2, 370, "Без фізичного резистора на землю затвор є конденсатором, що заряджається шумом і вмикає привід", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "floating-gate-danger.svg"), W, H, *p,
           title="Фізика плаваючого затвора та мимовільне відкриття MOSFET")


# ── 2. mcu-boot-gpio-states: часова діаграма станів виводу МК ─────────────────
def fig_mcu_boot_states():
    W, H = 840, 380
    p = []
    p.append(text(W / 2, 32, "Часова діаграма станів GPIO під час увімкнення та скидання", size=15, color=INK, bold=True))

    # Стовпці фаз за часом
    t_cols = [
        (30, 180, "ФАЗА 1: POR / Brown-out", "0…10 мс", "Живлення нестабільне,\nядро знеструмлене.\nGPIO: High-Z", REDBG, POS),
        (220, 190, "ФАЗА 2: Reset (NRST)", "10…50 мс", "Сигнал скидання в 0,\nпериферія скинута.\nGPIO: High-Z / Floating", REDBG, POS),
        (420, 200, "ФАЗА 3: Bootloader / DFU", "50 мс…15 с", "Завантажувач у ROM,\nкористувацький код мовчить.\nGPIO: High-Z або Weak Pull", AMBERBG, AMBER),
        (630, 180, "ФАЗА 4: User Code", "Після init", "gpio_init() налаштовано,\nвихід активний.\nGPIO: Push-Pull 0/1", GREENBG, FIELD),
    ]

    by, bh = 60, 220
    for x, w, title_txt, time_txt, desc_txt, bg_col, stroke_col in t_cols:
        tagcol = AMBERTX if stroke_col == AMBER else stroke_col
        p.append(rect(x, by, w, bh, fill=bg_col, stroke=stroke_col, sw=1.8, rx=8))
        p.append(text(x + w / 2, by + 24, title_txt, size=11, color=tagcol, bold=True))
        p.append(text(x + w / 2, by + 42, time_txt, size=9.5, color=MUTED, italic=True))
        
        p.append(line(x + 10, by + 54, x + w - 10, by + 54, color=stroke_col, sw=1, dash="3,3"))
        for j, ln in enumerate(desc_txt.split("\n")):
            p.append(text(x + w / 2, by + 80 + j * 20, ln, size=10, color=INK))

    # Небезпечне вікно
    p.append(rect(30, 290, 580, 42, fill=REDBG, stroke=POS, sw=2, rx=6))
    p.append(text(320, 316, "ВІКНО СМЕРТЕЛЬНОЇ НЕБЕЗПЕКИ: GPIO НЕ КЕРУЄТЬСЯ ПРОШИВКОЮ (High-Z)", size=11, color=POS, bold=True))

    p.append(rect(630, 290, 180, 42, fill=GREENBG, stroke=FIELD, sw=2, rx=6))
    p.append(text(720, 316, "Керований стан", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, 362, "Усі фази до закінчення gpio_init() потребують виключно апаратного утримання надійною підтяжкою", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "mcu-boot-gpio-states.svg"), W, H, *p,
           title="Часова діаграма станів GPIO під час увімкнення та скидання")


# ── 3. pull-down-circuit-sizing: схема підтяжки та вибір номіналу ─────────────
def fig_pull_down_sizing():
    W, H = 840, 370
    p = []
    p.append(text(W / 2, 32, "Схема апаратної підтяжки затвора та вибір номіналу резистора", size=15, color=INK, bold=True))

    # Схема зліва
    sx, sy, sw_box, sh_box = 30, 60, 270, 265
    p.append(rect(sx, sy, sw_box, sh_box, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(sx + sw_box / 2, sy + 24, "Типова схема підключення", size=12, color=NEG, bold=True))

    p.append(rect(sx + 15, sy + 45, 75, 45, fill=BG, stroke=LINE, sw=1.4, rx=4))
    p.append(text(sx + 52, sy + 72, "MCU GPIO", size=9.5, color=INK, bold=True))

    # Послідовний резистор затвора Rg
    p.append(rect(sx + 120, sy + 55, 45, 25, fill=BG, stroke=LINE, sw=1.4, rx=3))
    p.append(text(sx + 142, sy + 71, "Rg 22Ω", size=9, color=INK))

    # Лінії
    p.append(line(sx + 90, sy + 67, sx + 120, sy + 67, color=LINE, sw=1.8))
    p.append(line(sx + 165, sy + 67, sx + 220, sy + 67, color=LINE, sw=1.8))

    # Резистор підтяжки R_pd
    p.append(rect(sx + 195, sy + 110, 28, 50, fill=AMBERBG, stroke=AMBER, sw=1.6, rx=3))
    p.append(text(sx + 209, sy + 140, "R_pd", size=10, color=AMBERTX, bold=True))
    p.append(line(sx + 209, sy + 67, sx + 209, sy + 110, color=LINE, sw=1.8))
    p.append(line(sx + 209, sy + 160, sx + 209, sy + 195, color=LINE, sw=1.8))
    
    # Земля GND
    p.append(line(sx + 195, sy + 195, sx + 223, sy + 195, color=LINE, sw=2))
    p.append(line(sx + 200, sy + 199, sx + 218, sy + 199, color=LINE, sw=1.6))
    p.append(line(sx + 205, sy + 203, sx + 213, sy + 203, color=LINE, sw=1.2))
    p.append(text(sx + 209, sy + 218, "GND", size=9, color=MUTED))

    # Транзистор MOSFET
    p.append(rect(sx + 220, sy + 50, 35, 35, fill=BG, stroke=FIELD, sw=1.5, rx=4))
    p.append(text(sx + 237, sy + 72, "FET", size=9.5, color=FIELD, bold=True))

    p.append(text(sx + sw_box / 2, sy + 248, "R_pd фіксує затвор на GND", size=10.5, color=INK, bold=True))

    # Порівняльна таблиця праворуч
    rx_t, ry_t, rw_t, rh_t = 320, 60, 490, 265
    p.append(rect(rx_t, ry_t, rw_t, rh_t, fill=BG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(rx_t + rw_t / 2, ry_t + 24, "Порівняння номіналів резистора підтяжки R_pd", size=12.5, color=INK, bold=True))

    rows = [
        ("100 кОм (Завеликий)", "Повільний розряд (τ > 200 мкс), подільник із внутрішнім pull-up (40 кОм) дає 2.3 В — транзистор ВІДКРИВАЄТЬСЯ!", REDBG, POS),
        ("100 Ом (Замалий)", "Надмірне навантаження GPIO: I = 33 мА. Вивід МК перегрівається, напруга логічної «1» просідає.", REDBG, POS),
        ("4.7…10 кОм (ОПТИМУМ)", "Струм GPIO лише 0.3…0.7 мА, швидкий розряд (τ < 10 мкс), надійне придушення наведень Міллера (dV/dt).", GREENBG, FIELD),
    ]

    for i, (nom_txt, desc_nom, fill_r, col_r) in enumerate(rows):
        row_y = ry_t + 45 + i * 70
        p.append(rect(rx_t + 15, row_y, rw_t - 30, 60, fill=fill_r, stroke=col_r, sw=1.4, rx=6))
        p.append(text(rx_t + 30, row_y + 22, nom_txt, size=11, color=col_r, bold=True, anchor="start"))
        p.append(text(rx_t + 30, row_y + 44, desc_nom, size=9.4, color=INK, anchor="start"))

    p.append(text(W / 2, 350, "Номінал 4.7…10 кОм гарантує напругу на затворі нижче 0.4 В при будь-яких внутрішніх підтяжках МК", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "pull-down-circuit-sizing.svg"), W, H, *p,
           title="Схема апаратної підтяжки затвора та вибір номіналу")


# ── 4. dynamic-charge-pump-interlock: помпа заряду та динамічний дозвіл ───────
def fig_charge_pump_interlock():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 32, "Дворівневе динамічне блокування: захист від зависання прошивки", size=15, color=INK, bold=True))

    # Схема ланцюга
    blocks = [
        (30, 165, "Генератор МК", "Safety Heartbeat\n(1…10 кГц PWM)\nЖивий цикл прошивки", BLUEBG, NEG),
        (210, 150, "Розділовий C1", "100 нФ\nБлокує постійний струм\nDC Block", AMBERBG, AMBER),
        (375, 175, "Помпа заряду", "2 діоди Шотткі + C2\nВипрямлення імпульсів\nу постійну напругу", AMBERBG, AMBER),
        (565, 125, "Реле / Gate", "Ключ живлення\nУвімкнено лише при\nнаявності сигналу", GREENBG, FIELD),
        (705, 105, "Сила", "Мотор /\nПривід", REDBG, POS),
    ]

    by, bh = 60, 100
    for x, w, h_txt, b_txt, bg_c, str_c in blocks:
        tagc = AMBERTX if str_c == AMBER else str_c
        p.append(rect(x, by, w, bh, fill=bg_c, stroke=str_c, sw=1.6, rx=8))
        p.append(text(x + w / 2, by + 24, h_txt, size=11, color=tagc, bold=True))
        for j, ln in enumerate(b_txt.split("\n")):
            p.append(text(x + w / 2, by + 48 + j * 16, ln, size=9.2, color=INK))

    # Стрілки між блоками
    p.append(arrow(195 + 4, by + bh / 2, 210 - 4, by + bh / 2, color=LINE, sw=2))
    p.append(arrow(360 + 4, by + bh / 2, 375 - 4, by + bh / 2, color=LINE, sw=2))
    p.append(arrow(550 + 4, by + bh / 2, 565 - 4, by + bh / 2, color=LINE, sw=2))
    p.append(arrow(690 + 4, by + bh / 2, 705 - 4, by + bh / 2, color=LINE, sw=2))

    # Нижні сценарії відмов
    ty = 180
    p.append(rect(30, ty, 780, 165, fill=BG, stroke=LINE, sw=1.6, rx=10))
    p.append(text(W / 2, ty + 24, "Як динамічний ключ реагує на критичні відмови системи", size=12.5, color=INK, bold=True))

    scenarios = [
        ("Процесор завис у «1» або «0»", "Постійний рівень не проходить через C1. Напруга на помпі падає до 0 В за 2 мс → Сила знеструмлюється!", REDBG, POS),
        ("Спрацював Reset / Bootloader", "Генерація частоти припиняється. Силовий ключ миттєво розмикається апаратно.", REDBG, POS),
        ("Пробій виводу GPIO на 3.3 В", "DC-напруга блокується конденсатором C1. Захист спрацьовує на 100%.", GREENBG, FIELD),
    ]

    for i, (sc_head, sc_desc, bg_sc, col_sc) in enumerate(scenarios):
        sy_row = ty + 40 + i * 38
        p.append(rect(45, sy_row, 750, 32, fill=bg_sc, stroke=col_sc, sw=1.2, rx=5))
        p.append(text(60, sy_row + 20, sc_head + ":", size=10, color=col_sc, bold=True, anchor="start"))
        p.append(text(310, sy_row + 20, sc_desc, size=9.4, color=INK, anchor="start"))

    p.append(text(W / 2, 370, "Динамічний ключ вимагає активного підтвердження працездатності: тиша або статика означає вимкнення", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "dynamic-charge-pump-interlock.svg"), W, H, *p,
           title="Дворівневе динамічне блокування: захист від зависання прошивки")


def main():
    fig_floating_gate()
    fig_mcu_boot_states()
    fig_pull_down_sizing()
    fig_charge_pump_interlock()
    print("Усі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
