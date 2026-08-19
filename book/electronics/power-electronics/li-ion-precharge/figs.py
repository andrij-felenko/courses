# -*- coding: utf-8 -*-
"""Фігури до теми «Попередній заряд літієвої комірки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Повний профіль заряду з виділеним передзарядом ────────────────────────
def fig_charge_profile():
    W, H = 880, 480
    items = []
    
    # Заголовок
    items.append(text(W / 2, 28, "Повний профіль заряду Li-ion: передзаряд (Precharge) → CC → CV",
                      size=16, bold=True))
    
    # Межі графіка
    gx0, gy0 = 80, 70
    gw, gh = 720, 310
    gx1, gy1 = gx0 + gw, gy0 + gh
    
    # Фазові зони (вертикальні смуги)
    # Зони: 0..120: Trickle (0-1.5V), 120..240: Precharge (1.5-3.0V), 240..540: CC (3.0-4.2V), 540..720: CV (4.2V drop to C/10)
    x_t0 = gx0
    x_t1 = gx0 + 90   # 170: Trickle
    x_t2 = gx0 + 230  # 310: Precharge -> CC
    x_t3 = gx0 + 510  # 590: CC -> CV
    x_t4 = gx1        # 800: CV termination
    
    # Фонова заливка фаз
    items.append(rect(x_t0, gy0, x_t2 - x_t0, gh, fill="#fff8e8", stroke="none")) # Передзаряд (Trickle + Pre)
    items.append(rect(x_t2, gy0, x_t3 - x_t2, gh, fill="#eef7f0", stroke="none")) # CC
    items.append(rect(x_t3, gy0, x_t4 - x_t3, gh, fill="#eef3fb", stroke="none")) # CV
    
    # Розділові вертикальні пунктири
    items.append(line(x_t1, gy0, x_t1, gy1, color=MUTED, sw=1.2, dash="4,4"))
    items.append(line(x_t2, gy0, x_t2, gy1, color=MUTED, sw=1.5, dash="4,4"))
    items.append(line(x_t3, gy0, x_t3, gy1, color=MUTED, sw=1.5, dash="4,4"))
    
    # Осі
    items.append(line(gx0, gy1, gx1 + 20, gy1, color=INK, sw=1.8)) # Вісь X (Час)
    items.append(line(gx0, gy1, gx0, gy0 - 15, color=NEG, sw=1.8)) # Вісь Y ліва (Напруга, V)
    items.append(line(gx1, gy1, gx1, gy0 - 15, color=POS, sw=1.8)) # Вісь Y права (Струм, A / C)
    
    # Підписи осей
    items.append(text(gx1 + 25, gy1 + 5, "Час (t)", size=12, color=INK, anchor="start", bold=True))
    items.append(text(gx0 - 10, gy0 - 10, "Напруга U (В)", size=12, color=NEG, anchor="end", bold=True))
    items.append(text(gx1 + 10, gy0 - 10, "Струм I (C-rate)", size=12, color=POS, anchor="start", bold=True))
    
    # Горизонтальні позначки напруги (ліва вісь)
    # 0V -> gy1, 1.5V -> gy1 - 50, 3.0V -> gy1 - 150, 4.2V -> gy1 - 270
    def v_to_y(v):
        return gy1 - (v / 4.5) * (gh - 30)
    
    y_4v2 = v_to_y(4.2)
    y_3v0 = v_to_y(3.0)
    y_1v5 = v_to_y(1.5)
    
    items.append(line(gx0 - 5, y_4v2, gx1, y_4v2, color="#cdd5df", sw=1.0, dash="2,2"))
    items.append(line(gx0 - 5, y_3v0, gx1, y_3v0, color="#cdd5df", sw=1.0, dash="2,2"))
    items.append(line(gx0 - 5, y_1v5, gx1, y_1v5, color="#cdd5df", sw=1.0, dash="2,2"))
    
    items.append(text(gx0 - 8, y_4v2 + 4, "4.20 В", size=11, color=NEG, anchor="end", bold=True))
    items.append(text(gx0 - 8, y_3v0 + 4, "3.00 В (V_LOWV)", size=11, color=NEG, anchor="end"))
    items.append(text(gx0 - 8, y_1v5 + 4, "1.50 В (V_SHORT)", size=11, color=NEG, anchor="end"))
    
    # Горизонтальні позначки струму (права вісь)
    # 1.0C -> y_curr_1c, 0.1C -> y_curr_01c, 0.02C -> y_curr_002c
    def i_to_y(i_val):
        return gy1 - (i_val / 1.1) * (gh - 40)
    
    y_i_1c = i_to_y(1.0)
    y_i_01c = i_to_y(0.1)
    y_i_term = i_to_y(0.05)
    
    items.append(text(gx1 + 8, y_i_1c + 4, "1.0C (I_CC)", size=11, color=POS, anchor="start", bold=True))
    items.append(text(gx1 + 8, y_i_01c + 4, "0.1C (I_PRE)", size=11, color=POS, anchor="start", bold=True))
    items.append(text(gx1 + 8, y_i_term + 4, "0.05C (Стоп)", size=11, color=POS, anchor="start"))
    
    # Крива струму (червона, штрих/лінія)
    # x_t0..x_t1: 0.02C, x_t1..x_t2: 0.1C, x_t2..x_t3: 1.0C, x_t3..x_t4: спад від 1.0C до 0.05C, далі 0
    pts_i = [
        (x_t0, i_to_y(0.02)),
        (x_t1, i_to_y(0.02)),
        (x_t1, i_to_y(0.1)),
        (x_t2, i_to_y(0.1)),
        (x_t2, i_to_y(1.0)),
        (x_t3, i_to_y(1.0)),
    ]
    # CV decay
    for step in range(25):
        frac = step / 24.0
        x_val = x_t3 + frac * (x_t4 - x_t3)
        # exponential decay from 1.0 to 0.05
        cur_val = 0.05 + 0.95 * math.exp(-3.0 * frac)
        pts_i.append((x_val, i_to_y(cur_val)))
    pts_i.append((x_t4, i_to_y(0.0)))
    pts_i.append((x_t4 + 30, i_to_y(0.0)))
    
    path_i = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_i)
    items.append(f'<path d="{path_i}" fill="none" stroke="{POS}" stroke-width="2.8" stroke-linejoin="round"/>')
    
    # Крива напруги (синя лінія)
    # Початок з 0.8V -> ріст до 1.5V (x_t1) -> ріст до 3.0V (x_t2) -> плато й ріст до 4.2V (x_t3) -> 4.2V стабільна (x_t4)
    pts_v = [
        (x_t0, v_to_y(0.8)),
        (x_t1, v_to_y(1.5)),
    ]
    # Precharge phase to 3.0V
    for step in range(1, 15):
        frac = step / 14.0
        x_val = x_t1 + frac * (x_t2 - x_t1)
        v_val = 1.5 + 1.5 * (frac ** 0.85)
        pts_v.append((x_val, v_to_y(v_val)))
    # CC phase from 3.0V to 4.2V
    for step in range(1, 25):
        frac = step / 24.0
        x_val = x_t2 + frac * (x_t3 - x_t2)
        # S-curve typical for Li-ion CC charging
        v_val = 3.0 + 1.2 * (0.15 * frac + 0.85 * (1 / (1 + math.exp(-6 * (frac - 0.45)))))
        v_val = min(v_val, 4.20)
        pts_v.append((x_val, v_to_y(v_val)))
    # CV phase (held at 4.20V)
    pts_v.append((x_t3, v_to_y(4.2)))
    pts_v.append((x_t4, v_to_y(4.2)))
    pts_v.append((x_t4 + 30, v_to_y(4.18))) # slight relaxation drop
    
    path_v = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_v)
    items.append(f'<path d="{path_v}" fill="none" stroke="{NEG}" stroke-width="2.8" stroke-linejoin="round"/>')
    
    # Назви зон зверху
    items.append(fitbox(x_t0 + 5, gy0 + 8, (x_t1 - x_t0) - 10, 36, "Wakeup / 0V\n0.01–0.02C", size=10, fill="#fff", stroke="#b8860b"))
    items.append(fitbox(x_t1 + 5, gy0 + 8, (x_t2 - x_t1) - 10, 36, "Передзаряд (Precharge)\n0.05C–0.1C", size=11, fill="#fff", stroke="#b8860b", bold=True))
    items.append(fitbox(x_t2 + 20, gy0 + 8, (x_t3 - x_t2) - 40, 36, "Сталий струм (CC)\n0.5C–1.0C (швидке наповнення)", size=11, fill="#fff", stroke=FIELD, bold=True))
    items.append(fitbox(x_t3 + 15, gy0 + 8, (x_t4 - x_t3) - 30, 36, "Стала напруга (CV)\n4.20 В (доливання хвоста)", size=11, fill="#fff", stroke=NEG, bold=True))
    
    # Виділення таймера безпеки (Safety Timer) у фазі передзаряду
    tb_y = gy1 - 32
    items.append(line(x_t0, tb_y, x_t2, tb_y, color=POS, sw=1.8))
    items.append(line(x_t0, tb_y - 5, x_t0, tb_y + 5, color=POS, sw=1.8))
    items.append(line(x_t2, tb_y - 5, x_t2, tb_y + 5, color=POS, sw=1.8))
    items.append(fitbox(x_t0 + 15, tb_y - 30, (x_t2 - x_t0) - 30, 24, "Таймер t_PRECHG ≤ 30–60 хв", size=10, fill="#fdecea", stroke=POS, bold=True))
    
    # Легенда знизу
    leg_y = H - 42
    items.append(line(240, leg_y, 280, leg_y, color=NEG, sw=2.8))
    items.append(text(290, leg_y + 4, "Напруга комірки U_cell (В)", size=12, color=INK, anchor="start", bold=True))
    items.append(line(520, leg_y, 560, leg_y, color=POS, sw=2.8))
    items.append(text(570, leg_y + 4, "Струм заряду I_chg (A)", size=12, color=INK, anchor="start", bold=True))
    
    render(os.path.join(IMG, "charge-profile.svg"), W, H, *items)


# ── 2. Фізика розчинення міді та дендритів ────────────────────────────────────
def fig_copper_dendrites():
    W, H = 880, 420
    items = []
    
    items.append(text(W / 2, 26, "Механізм деградації: розчинення міді при V < 2.0 В та дендрити",
                      size=16, bold=True))
    
    # 2 порівняльні панелі: зліва (Ударний струм 1C -> дендрити й КЗ), справа (Передзаряд 0.05C -> планарне відновлення)
    pw, ph = 400, 310
    py = 55
    
    # Панель 1 (Аварійний шлях: 1C на розряджену комірку)
    px1 = 30
    items.append(rect(px1, py, pw, ph, fill="#fdf7f7", stroke=POS, sw=1.6))
    items.append(text(px1 + pw / 2, py + 24, "❌ Помилка: струм 1C на розряджену комірку", size=13, color=POS, bold=True))
    
    # Будова шарів: Мідна фольга (зліва) -> Графіт -> Сепаратор (пористий) -> Катод
    lx_cu = px1 + 25
    lx_gr = px1 + 95
    lx_sep = px1 + 215
    lx_cat = px1 + 310
    
    # Шари Panel 1
    items.append(rect(lx_cu, py + 45, 60, 190, fill="#e8a87c", stroke="#a65c2e", sw=1.2))
    items.append(mtext(lx_cu + 30, py + 120, "Мідний\nколектор\n(Cu)", size=10, color="#5a2a0a", bold=True))
    
    items.append(rect(lx_gr, py + 45, 110, 190, fill="#7f8c8d", stroke="#34495e", sw=1.2))
    items.append(mtext(lx_gr + 55, py + 80, "Графітовий анод\n(Li-порожній)\nПотенціал > 3.5 В", size=10, color="#ffffff", bold=True))
    
    # Сепаратор
    items.append(rect(lx_sep, py + 45, 85, 190, fill="#fcf3cf", stroke="#b7950b", sw=1.2))
    items.append(mtext(lx_sep + 42, py + 75, "Сепаратор\n(пори 20 мкм)", size=10, color="#7d6608", bold=True))
    
    # Гострі мідні дендрити, що пронизують сепаратор
    # Дендрит 1
    dend1 = f"M {lx_gr + 70},{py + 140} L {lx_sep + 20},{py + 135} L {lx_sep + 50},{py + 145} L {lx_sep + 85},{py + 138}"
    items.append(f'<path d="{dend1}" fill="none" stroke="{POS}" stroke-width="3.2" stroke-linecap="round"/>')
    # Дендрит 2
    dend2 = f"M {lx_gr + 90},{py + 175} L {lx_sep + 35},{py + 180} L {lx_sep + 70},{py + 170} L {lx_sep + 85},{py + 178}"
    items.append(f'<path d="{dend2}" fill="none" stroke="{POS}" stroke-width="3.0" stroke-linecap="round"/>')
    
    # Катод
    items.append(rect(lx_cat, py + 45, 60, 190, fill="#bb8fce", stroke="#6c3483", sw=1.2))
    items.append(mtext(lx_cat + 30, py + 120, "Катод\n(LCO / NMC)", size=10, color="#ffffff", bold=True))
    
    # Спалах КЗ
    items.append(circle(lx_sep + 85, py + 138, 9, fill="#f39c12", stroke=POS, sw=1.5))
    items.append(fitbox(px1 + 15, py + 245, pw - 30, 50, "Висока перенапруга η → дифузійний ріст гострих голок Cu²⁺ → Cu⁰.\nПрокол сепаратора → внутрішнє КЗ → локальний перегрів > 150°C!", size=10, fill="#ffffff", stroke=POS))
    
    
    # Панель 2 (Безпечний шлях: Передзаряд 0.05C–0.1C)
    px2 = 450
    items.append(rect(px2, py, pw, ph, fill="#f4fbf5", stroke=FIELD, sw=1.6))
    items.append(text(px2 + pw / 2, py + 24, "✔ Безпечно: передзаряд 0.05C–0.1C", size=13, color=FIELD, bold=True))
    
    lx_cu2 = px2 + 25
    lx_gr2 = px2 + 95
    lx_sep2 = px2 + 215
    lx_cat2 = px2 + 310
    
    # Шари Panel 2
    items.append(rect(lx_cu2, py + 45, 60, 190, fill="#e8a87c", stroke="#a65c2e", sw=1.2))
    items.append(mtext(lx_cu2 + 30, py + 120, "Мідний\nколектор\n(Cu)", size=10, color="#5a2a0a", bold=True))
    
    items.append(rect(lx_gr2, py + 45, 110, 190, fill="#7f8c8d", stroke="#34495e", sw=1.2))
    items.append(mtext(lx_gr2 + 55, py + 80, "Графітовий анод\nПовільна регенерація\nSEI-шару", size=10, color="#ffffff", bold=True))
    
    # Гладкі компактні острівці Cu на поверхні графіту замість голок
    items.append(rect(lx_gr2 + 92, py + 125, 14, 25, fill="#e8a87c", stroke="#a65c2e", rx=3))
    items.append(rect(lx_gr2 + 92, py + 165, 14, 20, fill="#e8a87c", stroke="#a65c2e", rx=3))
    
    # Тонкий шар SEI
    items.append(line(lx_gr2 + 108, py + 45, lx_gr2 + 108, py + 235, color=FIELD, sw=3.0, dash="5,2"))
    
    # Сепаратор неушкоджений
    items.append(rect(lx_sep2, py + 45, 85, 190, fill="#fcf3cf", stroke="#b7950b", sw=1.2))
    items.append(mtext(lx_sep2 + 42, py + 120, "Сепаратор\nЦІЛИЙ\n(без КЗ)", size=10, color="#7d6608", bold=True))
    
    # Катод
    items.append(rect(lx_cat2, py + 45, 60, 190, fill="#bb8fce", stroke="#6c3483", sw=1.2))
    items.append(mtext(lx_cat2 + 30, py + 120, "Катод\n(LCO / NMC)", size=10, color="#ffffff", bold=True))
    
    items.append(fitbox(px2 + 15, py + 245, pw - 30, 50, "Низька перенапруга η → планарне відновлення іонів Cu²⁺ у матрицю.\nМ'яке відновлення SEI-плівки, напруга плавно піднімається до 3.0 В.", size=10, fill="#ffffff", stroke=FIELD))
    
    # Підсумковий підпис знизу
    items.append(text(W / 2, H - 18, "Розчинена мідь при V_cell < 2.0 В осаджується безпечно лише за малих струмів заряду", size=12, color=MUTED, bold=True))
    
    render(os.path.join(IMG, "copper-dendrites.svg"), W, H, *items)


# ── 3. Скінченний автомат Charger IC / BMS ────────────────────────────────────
def fig_precharge_fsm():
    W, H = 880, 440
    items = []
    
    items.append(text(W / 2, 26, "Скінченний автомат передзаряду (Charger IC / BMS FSM)",
                      size=16, bold=True))
    
    # Стан 1: IDLE
    s1_x, s1_y = 100, 100
    items.append(fitbox(s1_x, s1_y, 130, 55, "IDLE / SLEEP\nКлючі розімкнені", size=12, fill="#f4f6f8", stroke=LINE, bold=True))
    
    # Стан 2: TRICKLE (0V / Wakeup)
    s2_x, s2_y = 300, 100
    items.append(fitbox(s2_x, s2_y, 145, 55, "TRICKLE (0V)\nI = 0.01–0.02C", size=12, fill="#fff8e8", stroke="#b8860b", bold=True))
    
    # Стан 3: PRECHARGE
    s3_x, s3_y = 520, 100
    items.append(fitbox(s3_x, s3_y, 150, 55, "PRECHARGE\nI = 0.05C–0.1C\nТаймер t_PRE тікає", size=11, fill="#fff8e8", stroke=POS, bold=True))
    
    # Стан 4: FAST CHARGE (CC)
    s4_x, s4_y = 740, 100
    items.append(fitbox(s4_x, s4_y, 130, 55, "FAST CHARGE (CC)\nI = 0.5C–1.0C", size=12, fill="#eef7f0", stroke=FIELD, bold=True))
    
    # Стан 5: CONSTANT VOLTAGE (CV)
    s5_x, s5_y = 740, 240
    items.append(fitbox(s5_x, s5_y, 130, 55, "REGULATION (CV)\nU = 4.20 В, I спадає", size=11, fill="#eef3fb", stroke=NEG, bold=True))
    
    # Стан 6: CHARGE DONE
    s6_x, s6_y = 520, 240
    items.append(fitbox(s6_x, s6_y, 140, 55, "CHARGE DONE\nТермінація (I < C/10)", size=11, fill="#f4f6f8", stroke=LINE, bold=True))
    
    # Стан 7: FAULT LATCH (Аварія таймера)
    s7_x, s7_y = 300, 310
    items.append(fitbox(s7_x, s7_y, 175, 65, "PRECHARGE FAULT\nТаймер t > t_MAX\nВнутрішнє КЗ комірки!\nЗаряд НАЗАВЖДИ стоп", size=11, fill="#fdecea", stroke=POS, bold=True))
    
    # Переходи (Стрілки)
    # 1 -> 2: VBUS OK, V_bat < V_SHORT (1.5V)
    items.append(arrow(s1_x + 130, s1_y + 27, s2_x, s1_y + 27))
    items.append(text(s1_x + 130 + 35, s1_y + 15, "V < 1.5 В", size=10, color=MUTED))
    
    # 1 -> 3: VBUS OK, 1.5V <= V < 3.0V
    # вигин через верх
    # items.append(arrow(s1_x + 65, s1_y, s3_x + 75, s3_y))
    
    # 2 -> 3: V_bat >= 1.5V
    items.append(arrow(s2_x + 145, s2_y + 27, s3_x, s2_y + 27))
    items.append(text(s2_x + 145 + 35, s2_y + 15, "V ≥ 1.5 В", size=10, color=MUTED))
    
    # 3 -> 4: V_bat >= 3.0V (V_LOWV)
    items.append(arrow(s3_x + 150, s3_y + 27, s4_x, s3_y + 27, color=FIELD))
    items.append(text(s3_x + 150 + 35, s3_y + 15, "V ≥ 3.0 В", size=10, color=FIELD, bold=True))
    
    # 4 -> 5: V_bat == 4.20V
    items.append(arrow(s4_x + 65, s4_y + 55, s5_x + 65, s5_y, color=NEG))
    items.append(text(s4_x + 105, s4_y + 75, "V = 4.2 В", size=10, color=NEG))
    
    # 5 -> 6: I_chg < C/10
    items.append(arrow(s5_x, s5_y + 27, s6_x + 140, s5_y + 27))
    items.append(text(s6_x + 175, s5_y + 15, "I < C/10", size=10, color=MUTED))
    
    # 6 -> 1: Recharge trigger (V_bat < 4.05V)
    items.append(arrow(s6_x, s6_y + 27, s1_x + 65, s1_y + 55, color=MUTED))
    items.append(text(s1_x + 120, s6_y + 15, "V < 4.05 В (Recharge)", size=10, color=MUTED))
    
    # 3 -> 7: FAULT (t_PRE > 30 min)
    items.append(arrow(s3_x + 75, s3_y + 55, s7_x + 90, s7_y, color=POS))
    items.append(text(s3_x + 20, s3_y + 105, "t_PRE > t_MAX\n(V < 3.0 В)", size=10, color=POS, bold=True))
    
    # 7 -> 1: Тільки після скидання живлення VBUS
    items.append(arrow(s7_x, s7_y + 32, s1_x + 65, s1_y + 55, color=POS, sw=1.5))
    items.append(text(s1_x + 110, s7_y + 10, "Скидання VBUS (Power Cycle)", size=10, color=POS))
    
    # Підпис
    items.append(text(W / 2, H - 18, "Таймер безпеки запобігає нескінченному нагріву батареї з внутрішнім коротким замиканням", size=12, color=MUTED, bold=True))
    
    render(os.path.join(IMG, "precharge-fsm.svg"), W, H, *items)


# ── 4. Теплова пастка лінійного зарядника при передзаряді ────────────────────
def fig_thermal_dissipation():
    W, H = 880, 420
    items = []
    
    items.append(text(W / 2, 26, "Тепловий стрес лінійного зарядника: чому передзаряд рятує чип",
                      size=16, bold=True))
    
    gx0, gy0 = 90, 65
    gw, gh = 700, 270
    gx1, gy1 = gx0 + gw, gy0 + gh
    
    # Осі
    items.append(line(gx0, gy1, gx1 + 20, gy1, color=INK, sw=1.8)) # Вісь X (Напруга батареї)
    items.append(line(gx0, gy1, gx0, gy0 - 15, color=POS, sw=1.8)) # Вісь Y (Розсіювана потужність, Вт)
    
    items.append(text(gx1 + 25, gy1 + 5, "Напруга батареї U_BAT (В)", size=12, color=INK, anchor="start", bold=True))
    items.append(text(gx0 - 10, gy0 - 10, "Потужність P_loss (Вт)", size=12, color=POS, anchor="end", bold=True))
    
    # Розмітка осі X: 1.0V .. 4.2V
    def v_to_x(v):
        return gx0 + ((v - 1.0) / 3.4) * gw
    
    for v_val in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.2]:
        x_p = v_to_x(v_val)
        items.append(line(x_p, gy1, x_p, gy1 + 5, color=INK, sw=1.2))
        items.append(text(x_p, gy1 + 18, f"{v_val:.1f}", size=11, color=INK))
    
    # Розмітка осі Y: 0 .. 4.0 W
    def p_to_y(p_val):
        return gy1 - (p_val / 4.0) * gh
    
    for p_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        y_p = p_to_y(p_val)
        items.append(line(gx0 - 5, y_p, gx1, y_p, color="#e5e9f0", sw=1.0, dash="2,2"))
        items.append(text(gx0 - 8, y_p + 4, f"{p_val:.1f} Вт", size=11, color=MUTED, anchor="end"))
    
    # Зона аварійного перегріву (P > 1.5W для корпусу SOT-23 / DFN)
    y_crit = p_to_y(1.5)
    items.append(rect(gx0, gy0, gw, y_crit - gy0, fill="#fdf2f2", stroke="none"))
    items.append(line(gx0, y_crit, gx1, y_crit, color=POS, sw=1.5, dash="4,4"))
    items.append(text(gx1 - 10, y_crit - 8, "Теплова межа дрібного корпусу (~1.5 Вт без охолодження)", size=11, color=POS, anchor="end", bold=True))
    
    # Крива 1 (Гіпотетична: повний струм 1.0 А при V_in = 5.0 В без передзаряду)
    # P = (5.0 - V) * 1.0 A -> лінія від (1.0V, 4.0W) до (3.0V, 2.0W)
    pts_fatal = []
    for step in range(21):
        v = 1.0 + step * (2.0 / 20.0) # 1.0 to 3.0
        p = (5.0 - v) * 1.0
        pts_fatal.append((v_to_x(v), p_to_y(p)))
    path_fatal = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_fatal)
    items.append(f'<path d="{path_fatal}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="5,4"/>')
    
    # Крива 2 (Реальна з передзарядом: I_pre = 0.1 A при V < 3.0V, I_cc = 1.0 A при V >= 3.0V)
    pts_real = []
    # Precharge: 1.0V to 3.0V, I = 0.1A -> P = (5 - V)*0.1
    for step in range(21):
        v = 1.0 + step * (2.0 / 20.0)
        p = (5.0 - v) * 0.1
        pts_real.append((v_to_x(v), p_to_y(p)))
    # Jump at 3.0V to CC 1.0A
    v_jump = 3.0
    pts_real.append((v_to_x(v_jump), p_to_y((5.0 - v_jump) * 1.0)))
    # CC phase: 3.0V to 4.2V, I = 1.0A -> P = (5 - V)*1.0
    for step in range(1, 13):
        v = 3.0 + step * (1.2 / 12.0)
        p = (5.0 - v) * 1.0
        pts_real.append((v_to_x(v), p_to_y(p)))
        
    path_real = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_real)
    items.append(f'<path d="{path_real}" fill="none" stroke="{FIELD}" stroke-width="2.8" stroke-linejoin="round"/>')
    
    # Позначки точок
    # Точка катастрофи (1.5V, 1.0A -> 3.5W)
    items.append(circle(v_to_x(1.5), p_to_y(3.5), 5, fill=POS, stroke="#ffffff", sw=2))
    items.append(fitbox(v_to_x(1.5) + 15, p_to_y(3.5) - 25, 180, 42, "3.5 Вт на чипі при 1.5 В!\n(Тепловий пробій)", size=10, fill="#fff", stroke=POS))
    
    # Безпечна точка передзаряду (1.5V, 0.1A -> 0.35W)
    items.append(circle(v_to_x(1.5), p_to_y(0.35), 5, fill=FIELD, stroke="#ffffff", sw=2))
    items.append(fitbox(v_to_x(1.5) + 15, p_to_y(0.35) - 40, 180, 42, "Передзаряд: лише 0.35 Вт\n(Холодний кристал)", size=10, fill="#fff", stroke=FIELD, bold=True))
    
    # Легенда знизу
    leg_y = H - 35
    items.append(line(180, leg_y, 220, leg_y, color=POS, sw=2.5, dash="5,4"))
    items.append(text(230, leg_y + 4, "Без передзаряду (1.0 А постійно, V_IN = 5.0 В)", size=12, color=INK, anchor="start"))
    items.append(line(520, leg_y, 560, leg_y, color=FIELD, sw=2.8))
    items.append(text(570, leg_y + 4, "З передзарядом 0.1C (безпечний тепловий режим)", size=12, color=INK, anchor="start", bold=True))
    
    render(os.path.join(IMG, "thermal-dissipation.svg"), W, H, *items)


if __name__ == "__main__":
    fig_charge_profile()
    fig_copper_dendrites()
    fig_precharge_fsm()
    fig_thermal_dissipation()
    print("Фігури успішно згенеровано в img/")
