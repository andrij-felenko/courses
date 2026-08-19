# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Архітектури резервування: N+1 проти 2N ──────────────────────────────
def fig_redundancy_topologies():
    W, H = 940, 480
    parts = []

    # Розділювач панелей
    parts.append(line(W / 2, 45, W / 2, H - 35, color=MUTED, sw=1, dash="6 6"))

    # ── Ліва панель: Схема N+1 (спільна шина, резервний блок)
    parts.append(text(W * 0.25, 36, "Архітектура N+1 (спільна шина)", size=15, bold=True, color=INK))
    
    # Блоки живлення
    psu_x = 75
    b1, _, _ = textbox(psu_x, 95, "БЖ #1 (Основний)\n12 В / 500 Вт", size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    b2, _, _ = textbox(psu_x, 185, "БЖ #2 (Основний)\n12 В / 500 Вт", size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    b3, _, _ = textbox(psu_x, 275, "БЖ #3 (+1 Резерв)\n12 В / 500 Вт", size=11, pad=8, fill="#eef2ff", stroke=NEG, color=NEG, bold=True)
    parts += [b1, b2, b3]

    # ORing елементи
    or_x = 210
    o1, _, _ = textbox(or_x, 95, "ORing #1", size=10, pad=6, fill=FILL, stroke=LINE)
    o2, _, _ = textbox(or_x, 185, "ORing #2", size=10, pad=6, fill=FILL, stroke=LINE)
    o3, _, _ = textbox(or_x, 275, "ORing #3", size=10, pad=6, fill=FILL, stroke=LINE)
    parts += [o1, o2, o3]

    # Лінії від БЖ до ORing
    parts.append(line(135, 95, 175, 95, color=LINE, sw=2))
    parts.append(line(135, 185, 175, 185, color=LINE, sw=2))
    parts.append(line(135, 275, 175, 275, color=LINE, sw=2))

    # Спільна шина живлення
    bus_x = 295
    parts.append(line(245, 95, bus_x, 95, color=LINE, sw=2))
    parts.append(line(245, 185, bus_x, 185, color=LINE, sw=2))
    parts.append(line(245, 275, bus_x, 275, color=LINE, sw=2))
    parts.append(line(bus_x, 70, bus_x, 300, color=POS, sw=4))
    parts.append(text(bus_x, 56, "Спільна шина 12 В", size=11, bold=True, color=POS))

    # Навантаження
    load_x = 380
    parts.append(line(bus_x, 185, load_x - 45, 185, color=POS, sw=3))
    ld, _, _ = textbox(load_x, 185, "Навантаження\n1000 Вт (N=2)", size=11, pad=8, fill="#fdf2e9", stroke=POS, color=INK, bold=True)
    parts.append(ld)

    # Примітка N+1
    note1, _, _ = textbox(W * 0.25, 385, "Перевага: низька вартість (+1 модуль).\nВразливість: єдина спільна шина живлення (SPOF)\nта спільний ввід мережі 230 В.", size=11, pad=10, fill=FILL, stroke=MUTED)
    parts.append(note1)

    # ── Права панель: Схема 2N (повне дублювання шляхів)
    off = W / 2
    parts.append(text(off + W * 0.25, 36, "Архітектура 2N (повне дублювання)", size=15, bold=True, color=INK))

    # Лінія A і Лінія B вводу
    parts.append(text(off + 70, 75, "Мережа Ввід A", size=11, bold=True, color=FIELD))
    parts.append(text(off + 70, 235, "Мережа Ввід B", size=11, bold=True, color=NEG))

    p_a, _, _ = textbox(off + 80, 115, "БЖ A (Шлях A)\n12 В / 1000 Вт", size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    p_b, _, _ = textbox(off + 80, 275, "БЖ B (Шлях B)\n12 В / 1000 Вт", size=11, pad=8, fill="#eef2ff", stroke=NEG, color=NEG, bold=True)
    parts += [p_a, p_b]

    # Шина A і Шина B
    bus_a_x = off + 200
    bus_b_x = off + 200
    parts.append(line(off + 145, 115, bus_a_x, 115, color=FIELD, sw=2))
    parts.append(line(off + 145, 275, bus_b_x, 275, color=NEG, sw=2))

    # Сервер / Споживач з двома вводами
    server_box, _, _ = textbox(off + 335, 195, "Серверне шасі\n(подвійний ввід живлення)\n\nORing A      ORing B\n      \\      /\n     Внутрішня шина\n     Навантаження 1000 Вт", size=11, pad=12, fill="#fdf2e9", stroke=LINE, color=INK)
    parts.append(server_box)

    parts.append(arrow(bus_a_x, 115, off + 245, 160, color=FIELD, sw=2.5))
    parts.append(arrow(bus_b_x, 275, off + 245, 230, color=NEG, sw=2.5))

    # Примітка 2N
    note2, _, _ = textbox(off + W * 0.25, 385, "Перевага: нуль єдиних точок відмови (Zero SPOF).\nРезервуються вводи 230 В, ДБЖ, кабелі та БЖ.\nЦіна: 100% надлишковість заліза.", size=11, pad=10, fill=FILL, stroke=MUTED)
    parts.append(note2)

    return render(os.path.join(OUT, 'redundancy-topologies.svg'), W, H, *parts,
                  title="Архітектури резервування N+1 та 2N")


# ── 2. Пасивний Diode-OR проти активного Active ORing на MOSFET ─────────────
def fig_diode_vs_active_oring():
    W, H = 940, 480
    parts = []

    parts.append(line(W / 2, 45, W / 2, H - 35, color=MUTED, sw=1, dash="6 6"))

    # ── Ліва панель: Пасивний Diode-OR
    parts.append(text(W * 0.25, 36, "Пасивний Diode-OR (діод Шотткі)", size=15, bold=True, color=POS))

    # Джерело
    d_src, _, _ = textbox(70, 140, "Джерело 12 В\nСтрум I = 40 A", size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK)
    parts.append(d_src)

    # Діод
    dx = 200
    dy = 140
    parts.append(line(135, dy, dx - 25, dy, color=LINE, sw=2.5))
    # Діод Шотткі символ
    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#fdecea" stroke="%s" stroke-width="2.5"/>' % (dx - 18, dy - 18, dx - 18, dy + 18, dx + 14, dy, POS))
    parts.append(line(dx + 14, dy - 18, dx + 14, dy + 18, color=POS, sw=2.5))
    # Злами катода Шотткі
    parts.append(line(dx + 14, dy - 18, dx + 8, dy - 18, color=POS, sw=2.5))
    parts.append(line(dx + 14, dy + 18, dx + 20, dy + 18, color=POS, sw=2.5))

    parts.append(line(dx + 14, dy, 320, dy, color=LINE, sw=2.5))
    parts.append(arrow(145, dy - 15, 275, dy - 15, color=POS, sw=2))
    parts.append(text(210, dy - 24, "I = 40 A", size=11, bold=True, color=POS))

    # Вихідна шина
    d_out, _, _ = textbox(380, 140, "Шина 11.55 В\n(просадка 0.45 В)", size=11, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(d_out)

    # Теплові втрати діода
    d_loss, _, _ = textbox(W * 0.25, 270, "Втрати потужності на діоді:\nP_loss = I · V_F = 40 A · 0.45 В = 18.0 Вт\n\nНаслідки:\n• Величезний масивний радіатор\n• Ризик теплового розгону (струм витоку I_R\n  експоненційно зростає з температурою)", size=11, pad=10, fill="#fff5f5", stroke=POS, color=INK)
    parts.append(d_loss)

    # ── Права панель: Активний Active ORing
    off = W / 2
    parts.append(text(off + W * 0.25, 36, "Активний Active ORing (N-MOSFET)", size=15, bold=True, color=FIELD))

    a_src, _, _ = textbox(off + 70, 140, "Джерело 12 В\nСтрум I = 40 A", size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK)
    parts.append(a_src)

    # MOSFET і контролер
    mx = off + 210
    my = 140
    parts.append(line(off + 135, my, mx - 30, my, color=LINE, sw=2.5))
    
    # MOSFET блок
    fet_box, _, _ = textbox(mx, my, "N-MOSFET\nR_ds(on) = 1.5 мОм", size=10, pad=6, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(fet_box)
    parts.append(line(mx + 30, my, off + 320, my, color=LINE, sw=2.5))

    # Контролер ідеального діода знизу
    ic_box, _, _ = textbox(mx, my + 85, "Active ORing контролер\n(компаратор + чардж-помпа)", size=10, pad=8, fill="#eef2ff", stroke=NEG, color=INK)
    parts.append(ic_box)

    # Зв'язки контролера з MOSFET
    parts.append(line(mx - 40, my, mx - 40, my + 60, color=MUTED, sw=1.5))
    parts.append(line(mx - 40, my + 60, mx - 20, my + 60, color=MUTED, sw=1.5))
    parts.append(line(mx + 40, my, mx + 40, my + 60, color=MUTED, sw=1.5))
    parts.append(line(mx + 40, my + 60, mx + 20, my + 60, color=MUTED, sw=1.5))
    parts.append(arrow(mx, my + 55, mx, my + 25, color=NEG, sw=1.8))
    parts.append(text(mx + 18, my + 45, "Gate", size=10, color=NEG, bold=True))

    # Вихідна шина
    a_out, _, _ = textbox(off + 385, 140, "Шина 11.94 В\n(просадка 0.06 В)", size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(a_out)

    # Втрати активного ORing
    a_loss, _, _ = textbox(off + W * 0.25, 305, "Втрати потужності на MOSFET:\nP_loss = I² · R_ds(on) = 40² · 0.0015 = 2.4 Вт\n\nПереваги:\n• Економія 15.6 Вт тепла на кожен канал!\n• Падіння напруги всього 60 мВ проти 450 мВ\n• Швидке блокування зворотного струму (<200 нс)", size=11, pad=10, fill="#f0fff4", stroke=FIELD, color=INK)
    parts.append(a_loss)

    return render(os.path.join(OUT, 'diode-vs-active-oring.svg'), W, H, *parts,
                  title="Порівняння пасивного Diode-OR та активного Active ORing")


# ── 3. Графік перемикання джерел та час утримання шини ───────────────────────
def fig_seamless_switchover_path():
    W, H = 900, 440
    parts = []

    ox, oy = 90, 340
    aw, ah = 740, 260

    # Осі координат
    parts.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))
    parts.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))
    parts.append(text(ox + aw - 5, oy + 25, "Час (t) →", size=12, color=INK, anchor="end"))
    parts.append(text(ox - 10, oy - ah + 15, "Напруга (В)", size=12, color=INK, anchor="end"))

    # Рівні напруги
    v_nom_y = oy - 200    # 12 В
    v_th_y = oy - 160     # 10.8 В поріг відмови
    v_uvlo_y = oy - 90    # 9.0 В UVLO перезавантаження
    v_bat_y = oy - 140    # 10.2 В батарея

    parts.append(line(ox, v_nom_y, ox + aw - 30, v_nom_y, color=MUTED, sw=1, dash="4 4"))
    parts.append(text(ox - 8, v_nom_y + 4, "V_nom (12 В)", size=11, color=INK, anchor="end"))

    parts.append(line(ox, v_th_y, ox + aw - 30, v_th_y, color=POS, sw=1, dash="4 4"))
    parts.append(text(ox - 8, v_th_y + 4, "V_fault (10.8 В)", size=11, color=POS, anchor="end"))

    parts.append(line(ox, v_bat_y, ox + aw - 30, v_bat_y, color=FIELD, sw=1, dash="4 4"))
    parts.append(text(ox - 8, v_bat_y + 4, "V_резерв (10.2 В)", size=11, color=FIELD, anchor="end"))

    parts.append(line(ox, v_uvlo_y, ox + aw - 30, v_uvlo_y, color=POS, sw=1.5, dash="2 2"))
    parts.append(text(ox - 8, v_uvlo_y + 4, "V_UVLO (9.0 В Скид)", size=11, bold=True, color=POS, anchor="end"))

    # Часові зони
    t_fail = ox + 180
    t_det = ox + 260
    t_sw = ox + 420
    t_rec = ox + 560

    # Вертикальні лінії подій
    parts.append(line(t_fail, oy, t_fail, oy - ah + 30, color=MUTED, sw=1, dash="2 2"))
    parts.append(text(t_fail, oy + 18, "t₀: Аварія мережі", size=10, color=INK, anchor="middle"))

    parts.append(line(t_det, oy, t_det, oy - ah + 30, color=MUTED, sw=1, dash="2 2"))
    parts.append(text(t_det, oy + 32, "t₁: Детектування", size=10, color=INK, anchor="middle"))

    parts.append(line(t_sw, oy, t_sw, oy - ah + 30, color=MUTED, sw=1, dash="2 2"))
    parts.append(text(t_sw, oy + 18, "t₂: Ключ резерву ON", size=10, color=INK, anchor="middle"))

    # Крива вихідної шини V_bus
    path_bus = [
        f"M {ox} {v_nom_y}",
        f"L {t_fail} {v_nom_y}",
        f"L {t_det} {v_th_y}",
        # Розряд утримуючих конденсаторів під струмом навантаження
        f"L {t_sw} {oy - 110}",
        # Підключення резерву і стабілізація на V_bat
        f"Q {t_sw + 40} {v_bat_y - 15} {t_rec} {v_bat_y}",
        f"L {ox + aw - 30} {v_bat_y}"
    ]
    parts.append(f'<path d="{" ".join(path_bus)}" fill="none" stroke="{NEG}" stroke-width="3.5"/>')
    parts.append(text(t_rec + 40, v_bat_y - 15, "Напруга шини V_bus", size=12, bold=True, color=NEG))

    # Зона розряду конденсаторів Hold-up
    parts.append(fitbox((t_det + t_sw) / 2 - 90, oy - 70, 180, 42,
                        "Розряд C_hold струмом навантаження:\nΔV = (I_load · t_trans) / C_hold",
                        size=10, fill="#fff9db", stroke="#f59f00", color=INK))

    # Запас безпеки до UVLO
    parts.append(arrow(t_sw + 10, oy - 110, t_sw + 10, v_uvlo_y, color=FIELD, sw=2))
    parts.append(arrow(t_sw + 10, v_uvlo_y, t_sw + 10, oy - 110, color=FIELD, sw=2))
    parts.append(text(t_sw + 18, (oy - 110 + v_uvlo_y) / 2 + 4, "Запас до перезавантаження", size=10, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'seamless-switchover-path.svg'), W, H, *parts,
                  title="Динаміка безрозривного перемикання на резервне живлення")


# ── 4. Hot-Swap: обмеження пускового струму та область SOA MOSFET ───────────
def fig_hotswap_inrush_soa():
    W, H = 940, 480
    parts = []

    parts.append(line(W / 2, 45, W / 2, H - 35, color=MUTED, sw=1, dash="6 6"))

    # ── Ліва панель: Схема Hot-Swap контролера
    parts.append(text(W * 0.25, 36, "Структура Hot-Swap контролера", size=15, bold=True, color=INK))

    # Вхід Backplane
    b_in, _, _ = textbox(60, 110, "Гаряча шина\n12 В (Backplane)", size=10, pad=6, fill="#f4f6f8", stroke=LINE)
    parts.append(b_in)

    # Шунт струму Rsense
    parts.append(line(115, 110, 145, 110, color=LINE, sw=2.5))
    sh_box, _, _ = textbox(170, 110, "R_sense\n5 мОм", size=10, pad=6, fill=FILL, stroke=LINE)
    parts.append(sh_box)

    # Силовий N-MOSFET
    parts.append(line(195, 110, 235, 110, color=LINE, sw=2.5))
    fet_box, _, _ = textbox(270, 110, "N-MOSFET\nКлюч dV/dt", size=10, pad=6, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(fet_box)

    # Вихід до плати та ємність
    parts.append(line(305, 110, 370, 110, color=LINE, sw=2.5))
    c_box, _, _ = textbox(370, 170, "Ємність плати\nC_load = 2200 мкФ\n(без заряду = КЗ!)", size=10, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(c_box)
    parts.append(line(370, 110, 370, 140, color=LINE, sw=2))

    # Мікросхема Hot-Swap знизу
    hs_ic, _, _ = textbox(220, 240, "Hot-Swap контролер\n• Драйвер затвора (I_gate струм)\n• Обмеження струму (I_limit луп)\n• Таймер аварії (SOA захист)\n• Сигнал PGOOD для навантаження", size=10, pad=10, fill="#eef2ff", stroke=NEG, color=INK)
    parts.append(hs_ic)

    # Сигнали керування
    parts.append(line(170, 130, 170, 195, color=MUTED, sw=1.5))
    parts.append(arrow(270, 195, 270, 130, color=NEG, sw=1.8))
    parts.append(text(285, 160, "Gate", size=10, color=NEG, bold=True))

    # ── Права панель: Область безпечної роботи (SOA) під час плавного старту
    off = W / 2
    parts.append(text(off + W * 0.25, 36, "Крива SOA та тепловий стрес", size=15, bold=True, color=INK))

    sox, soy = off + 60, 360
    saw, sah = 360, 260
    parts.append(arrow(sox, soy, sox + saw, soy, color=INK, sw=2))
    parts.append(arrow(sox, soy, sox, soy - sah, color=INK, sw=2))
    parts.append(text(sox + saw - 5, soy + 22, "Напруга V_DS (В) [логарифмічна]", size=10, color=INK, anchor="end"))
    parts.append(text(sox - 10, soy - sah + 12, "Струм I_D (А)", size=10, color=INK, anchor="end"))

    # Межа R_ds(on)
    parts.append(line(sox + 20, soy - 200, sox + 90, soy - 20, color=MUTED, sw=1.5))
    parts.append(text(sox + 40, soy - 160, "R_ds(on) ліміт", size=9, color=MUTED))

    # Лінії імпульсної потужності SOA (10 мс, 1 мс, DC)
    parts.append(line(sox + 90, soy - 200, sox + 300, soy - 130, color=FIELD, sw=2.5))
    parts.append(text(sox + 260, soy - 145, "10 мс пульс", size=10, bold=True, color=FIELD))

    parts.append(line(sox + 90, soy - 160, sox + 300, soy - 60, color=POS, sw=2, dash="4 4"))
    parts.append(text(sox + 260, soy - 75, "DC режим (статика)", size=10, bold=True, color=POS))

    # Робоча траєкторія заряджання ємності
    parts.append(circle(sox + 250, soy - 150, 5, fill=POS, stroke=POS))
    parts.append(text(sox + 250, soy - 162, "Початок заряду: V_DS=12В, I=10А (P=120 Вт!)", size=9, bold=True, color=POS, anchor="middle"))
    parts.append(arrow(sox + 240, soy - 145, sox + 60, soy - 30, color=NEG, sw=2.5))
    parts.append(circle(sox + 50, soy - 25, 4, fill=FIELD, stroke=FIELD))
    parts.append(text(sox + 85, soy - 15, "Кінець: V_DS≈0 В", size=9, color=FIELD))

    # Висновок SOA
    note_soa, _, _ = textbox(off + W * 0.25, 420, "Hot-Swap тримає заряд у межах імпульсної зони SOA.\nЯкщо час заряду перевищує таймер — аварійне відключення!", size=10, pad=6, fill=FILL, stroke=MUTED)
    parts.append(note_soa)

    return render(os.path.join(OUT, 'hotswap-inrush-soa.svg'), W, H, *parts,
                  title="Структура Hot-Swap та траєкторія заряду в зоні безпечної роботи SOA")


# ── 5. Активне балансування струмів: Share Bus проти Droop ─────────────────
def fig_current_sharing_loops():
    W, H = 940, 480
    parts = []

    parts.append(line(W / 2, 45, W / 2, H - 35, color=MUTED, sw=1, dash="6 6"))

    # ── Ліва панель: Метод нахилу характеристики (Droop Sharing)
    parts.append(text(W * 0.25, 36, "Метод нахилу характеристики (Droop)", size=15, bold=True, color=INK))

    dox, doy = 60, 240
    daw, dah = 360, 160
    parts.append(arrow(dox, doy, dox + daw, doy, color=INK, sw=2))
    parts.append(arrow(dox, doy, dox, doy - dah, color=INK, sw=2))
    parts.append(text(dox + daw - 5, doy + 20, "Струм I_out (А) →", size=10, color=INK, anchor="end"))
    parts.append(text(dox - 5, doy - dah + 10, "Напруга V (В)", size=10, color=INK, anchor="end"))

    # Дві характеристики з різним V_offset
    parts.append(line(dox + 10, doy - 130, dox + 280, doy - 50, color=FIELD, sw=2.5))
    parts.append(text(dox + 290, doy - 55, "Блок #1", size=10, color=FIELD, bold=True))

    parts.append(line(dox + 10, doy - 110, dox + 280, doy - 30, color=NEG, sw=2.5))
    parts.append(text(dox + 290, doy - 35, "Блок #2", size=10, color=NEG, bold=True))

    # Спільна напруга шини V_bus
    v_bus_line = doy - 70
    parts.append(line(dox, v_bus_line, dox + 300, v_bus_line, color=POS, sw=1.5, dash="4 4"))
    parts.append(text(dox + 15, v_bus_line - 8, "Спільна напруга V_bus", size=10, color=POS, bold=True))

    parts.append(arrow(dox + 160, doy, dox + 160, v_bus_line, color=FIELD, sw=1.5))
    parts.append(text(dox + 160, doy + 15, "I₁", size=10, color=FIELD, bold=True))

    parts.append(arrow(dox + 220, doy, doy, v_bus_line, color=NEG, sw=1.5))
    parts.append(text(dox + 220, doy + 15, "I₂", size=10, color=NEG, bold=True))

    note_droop, _, _ = textbox(W * 0.25, 360, "Принцип: штучний опір R_droop = ΔV / ΔI.\n• Плюси: немає ліній зв'язку між блоками.\n• Мінуси: напруга шини падає під навантаженням;\n  похибка розподілу залежить від різниці V_ref.", size=10, pad=8, fill=FILL, stroke=MUTED)
    parts.append(note_droop)

    # ── Права панель: Виділена аналогова шина Share Bus
    off = W / 2
    parts.append(text(off + W * 0.25, 36, "Активна шина Share Bus (Master-Slave)", size=15, bold=True, color=INK))

    # Модуль 1
    m1_box, _, _ = textbox(off + 80, 110, "Перетворювач #1\n(Master за струмом)\nI₁ = 20.2 A", size=10, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    # Модуль 2
    m2_box, _, _ = textbox(off + 80, 240, "Перетворювач #2\n(Slave підтягує V_out)\nI₂ = 19.8 A", size=10, pad=8, fill="#eef2ff", stroke=NEG, color=NEG, bold=True)
    parts += [m1_box, m2_box]

    # Спільна силова шина
    pbus_x = off + 260
    parts.append(line(off + 150, 110, pbus_x, 110, color=POS, sw=2.5))
    parts.append(line(off + 150, 240, pbus_x, 240, color=POS, sw=2.5))
    parts.append(line(pbus_x, 80, pbus_x, 270, color=POS, sw=4))
    parts.append(text(pbus_x + 10, 85, "Силова шина 12.00 В (жорстка стабілізація)", size=10, color=POS, bold=True))

    # Сигнальна лінія Share Bus
    sbus_x = off + 350
    parts.append(line(sbus_x, 80, sbus_x, 270, color="#9c27b0", sw=2.5, dash="6 3"))
    parts.append(text(sbus_x + 8, 200, "Share Bus\n(V_share ~ I_max)", size=9, color="#9c27b0", bold=True))

    # Зв'язки з Share Bus
    parts.append(arrow(off + 150, 125, sbus_x, 125, color="#9c27b0", sw=1.8))
    parts.append(arrow(sbus_x, 225, off + 150, 225, color="#9c27b0", sw=1.8))

    note_share, _, _ = textbox(off + W * 0.25, 360, "Принцип: провідний блок задає рівень V_share.\nПідлеглі блоки коригують дільник зворотного зв'язку.\n• Точність балансу: 1–3%\n• Жорстка стабілізація напруги без просадки!", size=10, pad=8, fill="#f3e5f5", stroke="#9c27b0", color=INK)
    parts.append(note_share)

    return render(os.path.join(OUT, 'current-sharing-loops.svg'), W, H, *parts,
                  title="Порівняння методів розподілу струму Droop та Active Share Bus")


# ── 6. Резервування на іоністорах (Supercapacitor Backup & Dying Gasp) ────────
def fig_supercap_backup_system():
    W, H = 940, 480
    parts = []

    # ── Блок-схема топології ДБЖ на іоністорах
    parts.append(text(W * 0.5, 36, "Архітектура ДБЖ на суперконденсаторах (Dying Gasp Backup)", size=15, bold=True, color=INK))

    # Вхід мережі та перемикач
    in_box, _, _ = textbox(70, 120, "Вхід DC\n12 В (Мережа)", size=11, pad=8, fill="#f4f6f8", stroke=LINE)
    parts.append(in_box)

    # Power Path перемикач
    sw_box, _, _ = textbox(190, 120, "Power Mux /\nActive ORing", size=10, pad=6, fill=FILL, stroke=LINE)
    parts.append(sw_box)
    parts.append(line(125, 120, 150, 120, color=LINE, sw=2))

    # Силова шина
    parts.append(line(230, 120, 360, 120, color=POS, sw=3))
    bus_node = 300
    parts.append(circle(bus_node, 120, 4, fill=POS, stroke=POS))
    parts.append(text(bus_node, 100, "Головна шина V_sys (12 В)", size=10, bold=True, color=POS))

    # Зарядний / розрядний двонаправлений перетворювач
    sc_conv, _, _ = textbox(bus_node, 230, "Двонаправлений DC-DC\n• Режим норми: Buck заряд до 5.4 В\n• Режим аварії: Boost розряд до 1.8 В", size=10, pad=8, fill="#eef2ff", stroke=NEG, color=INK)
    parts.append(sc_conv)
    parts.append(arrow(bus_node - 15, 140, bus_node - 15, 195, color=FIELD, sw=2))
    parts.append(arrow(bus_node + 15, 195, bus_node + 15, 140, color=POS, sw=2))
    parts.append(text(bus_node - 35, 165, "Заряд", size=9, color=FIELD, bold=True))
    parts.append(text(bus_node + 35, 165, "Розряд", size=9, color=POS, bold=True))

    # Блок іоністорів
    sc_bank, _, _ = textbox(bus_node, 360, "Банк іоністорів (Supercaps)\n2 × 50 Ф / 2.7 В (послідовно)\nC_eq = 25 Ф, E = 360 Дж", size=10, pad=10, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(sc_bank)
    parts.append(line(bus_node, 265, bus_node, 320, color=LINE, sw=2))

    # Споживачі: MCU та NVRAM
    mcu_box, _, _ = textbox(520, 120, "Системний MCU\n+ Пам'ять FRAM/Flash", size=10, pad=8, fill="#fff3e0", stroke="#e65100", color=INK, bold=True)
    parts.append(mcu_box)
    parts.append(arrow(360, 120, 450, 120, color=POS, sw=2.5))

    # Сигнал переривання PFI / Dying Gasp
    parts.append(line(70, 155, 70, 200, color=POS, sw=1.5))
    parts.append(line(70, 200, 450, 200, color=POS, sw=1.5, dash="5 3"))
    parts.append(arrow(450, 200, 480, 155, color=POS, sw=2))
    parts.append(text(240, 190, "Аварійний сигнал переривання (PFI / Dying Gasp NMI)", size=10, bold=True, color=POS))

    # Часова шкала порятунку даних
    t_box, _, _ = textbox(730, 230, "Хронологія аварійного циклу (500 мс):\n\n1. t = 0 мс: Вхід DC зник, PFI переривання\n2. t = 1 мс: Boost підхоплює шину 12 В\n3. t = 5 мс: MCU зупиняє периферію\n4. t = 50 мс: Скидання логів у FRAM / Flash\n5. t = 80 мс: Паркування приводів / замків\n6. t = 450 мс: Безпечний Sleep / Shutoff", size=10, pad=12, fill="#fdf2e9", stroke=LINE, color=INK)
    parts.append(t_box)

    return render(os.path.join(OUT, 'supercap-backup-system.svg'), W, H, *parts,
                  title="Резервне живлення на суперконденсаторах та протокол збереження Dying Gasp")


def main():
    fig_redundancy_topologies()
    fig_diode_vs_active_oring()
    fig_seamless_switchover_path()
    fig_hotswap_inrush_soa()
    fig_current_sharing_loops()
    fig_supercap_backup_system()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
