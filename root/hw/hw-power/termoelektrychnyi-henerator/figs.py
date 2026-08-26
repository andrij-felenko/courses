# -*- coding: utf-8 -*-
"""Фігури до теми «Термоелектричний генератор: ефект Зеєбека».
Запуск із теки теми: python figs.py
"""
import sys, os, math

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-linejoin="round"%s/>' % (p, color, sw, d))


def dot(cx, cy, r=5, fill=INK, stroke=BG, sw=2):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)


def axes(px, py, pw, ph, xlabel, ylabel):
    s = line(px, py, px, py + ph, color=INK, sw=2)
    s += line(px, py + ph, px + pw, py + ph, color=INK, sw=2)
    s += text(px + pw, py + ph + 28, xlabel, size=14, color=MUTED, anchor="end")
    s += text(px - 14, py - 14, ylabel, size=14, color=MUTED, anchor="start")
    return s


# ── Фігура 1: Фізика ефекту Зеєбека (дифузія носіїв у n- та p-типах) ──────────
def fig_seebeck_physics():
    W, H = 840, 480
    frags = []

    # Верхня гаряча зона
    frags.append(rect(60, 50, 720, 46, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    frags.append(text(420, 78, "Гаряча сторона  (T_hot) — висока кінетична енергія носіїв", size=15, color=POS, bold=True))

    # Нижня холодна зона
    frags.append(rect(60, 360, 720, 46, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(420, 388, "Холодна сторона  (T_cold) — низька кінетична енергія носіїв", size=15, color=NEG, bold=True))

    # Стрілка теплового градієнта ліворуч
    frags.append(arrow(100, 110, 100, 340, color=POS, sw=2.6))
    frags.append(text(90, 225, "Тепловий потік Q", size=13, color=POS, anchor="end", bold=True))

    # Стовпчик n-типу
    nx = 240
    frags.append(rect(nx, 96, 150, 264, fill="#edf4fc", stroke=NEG, sw=2, rx=4))
    frags.append(text(nx + 75, 124, "n-тип (електрони)", size=15, color=NEG, bold=True))

    # Електрони в n-стовпчику (сині кружечки з мінусом, більше внизу через дифузію)
    for ey in (160, 195, 235, 275, 305, 335):
        frags.append(circle(nx + 40, ey, 9, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(nx + 40, ey + 4, "−", size=12, color=NEG, bold=True))
    for ey in (175, 215, 255, 290, 320, 340):
        frags.append(circle(nx + 110, ey, 9, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(nx + 110, ey + 4, "−", size=12, color=NEG, bold=True))

    # Стрілка дифузії в n-стовпчику
    frags.append(arrow(nx + 75, 150, nx + 75, 320, color=NEG, sw=2.2))
    frags.append(text(nx + 75, 350, "дифузія e⁻", size=11, color=NEG, bold=True))

    # Полярність на кінцях n-стовпчика
    frags.append(plus(nx + 75, 96, r=8))
    frags.append(minus(nx + 75, 360, r=8))
    frags.append(text(nx + 75, 430, "S_n < 0  (холодний кінець «−»)", size=13, color=NEG, bold=True))

    # Стовпчик p-типу
    px = 480
    frags.append(rect(px, 96, 150, 264, fill="#fdf2f0", stroke=POS, sw=2, rx=4))
    frags.append(text(px + 75, 124, "p-тип (дірки)", size=15, color=POS, bold=True))

    # Дірки в p-стовпчику (червоні кружечки з плюсом)
    for py_pos in (160, 195, 235, 275, 305, 335):
        frags.append(circle(px + 40, py_pos, 9, fill="#fdecea", stroke=POS, sw=1.5))
        frags.append(text(px + 40, py_pos + 4, "+", size=12, color=POS, bold=True))
    for py_pos in (175, 215, 255, 290, 320, 340):
        frags.append(circle(px + 110, py_pos, 9, fill="#fdecea", stroke=POS, sw=1.5))
        frags.append(text(px + 110, py_pos + 4, "+", size=12, color=POS, bold=True))

    # Стрілка дифузії в p-стовпчику
    frags.append(arrow(px + 75, 150, px + 75, 320, color=POS, sw=2.2))
    frags.append(text(px + 75, 350, "дифузія h⁺", size=11, color=POS, bold=True))

    # Полярність на кінцях p-стовпчика
    frags.append(minus(px + 75, 96, r=8))
    frags.append(plus(px + 75, 360, r=8))
    frags.append(text(px + 75, 430, "S_p > 0  (холодний кінець «+»)", size=13, color=POS, bold=True))

    # Загальний підсумок знизу
    frags.append(text(420, 462, "Електрорушійна сила термопари:  Voc = (S_p − S_n) · (T_hot − T_cold)", size=14, color=INK, bold=True))

    return render(os.path.join(IMG, 'seebeck-physics.svg'), W, H, *frags,
                  title="Фізика ефекту Зеєбека: теплова дифузія електронів та дірок")


# ── Фігура 2: Конструкція модуля ТЕГ (послідовне електричне / паралельне теплове) ──
def fig_module_construction():
    W, H = 860, 460
    frags = []

    # Верхня кераміка (Гаряча сторона)
    frags.append(rect(90, 50, 680, 24, fill="#f5f5f5", stroke=LINE, sw=1.8, rx=3))
    frags.append(text(430, 40, "Верхня керамічна пластина (Al₂O₃ або AlN) — гаряча сторона T_hot", size=14, color=POS, bold=True))

    # Нижня кераміка (Холодна сторона)
    frags.append(rect(90, 310, 680, 24, fill="#f5f5f5", stroke=LINE, sw=1.8, rx=3))
    frags.append(text(430, 354, "Нижня керамічна пластина (Al₂O₃ або AlN) — холодна сторона T_cold", size=14, color=NEG, bold=True))

    # Мідні перемички зверху (3 штуки, з'єднують пари)
    top_straps = [(160, 260), (360, 460), (560, 660)]
    for x1, x2 in top_straps:
        frags.append(rect(x1, 74, x2 - x1, 14, fill="#e59866", stroke="#b9770e", sw=1.5, rx=2))
        frags.append(text((x1 + x2) / 2, 85, "Cu", size=11, color="#784212", bold=True))

    # Мідні перемички знизу (2 внутрішні, 2 вивідні)
    bot_straps = [(260, 360), (460, 560)]
    for x1, x2 in bot_straps:
        frags.append(rect(x1, 296, x2 - x1, 14, fill="#e59866", stroke="#b9770e", sw=1.5, rx=2))
        frags.append(text((x1 + x2) / 2, 307, "Cu", size=11, color="#784212", bold=True))

    # Вивідні контакти знизу
    frags.append(rect(140, 296, 40, 14, fill="#e59866", stroke="#b9770e", sw=1.5, rx=2))
    frags.append(rect(640, 296, 40, 14, fill="#e59866", stroke="#b9770e", sw=1.5, rx=2))

    # Дроти виводів
    frags.append(line(160, 310, 160, 390, color=POS, sw=2.8))
    frags.append(line(660, 310, 660, 390, color=NEG, sw=2.8))
    frags.append(circle(160, 395, 6, fill=POS, stroke=BG, sw=1.5))
    frags.append(circle(660, 395, 6, fill=NEG, stroke=BG, sw=1.5))
    frags.append(text(160, 420, "Вивід (+)", size=14, color=POS, bold=True))
    frags.append(text(660, 420, "Вивід (−)", size=14, color=NEG, bold=True))

    # Стовпчики p/n (6 штук: P1, N1, P2, N2, P3, N3)
    pellets = [
        (160, "p", "#fdf2f0", POS),
        (260, "n", "#edf4fc", NEG),
        (360, "p", "#fdf2f0", POS),
        (460, "n", "#edf4fc", NEG),
        (560, "p", "#fdf2f0", POS),
        (660, "n", "#edf4fc", NEG),
    ]

    for px_center, ptype, fill_c, stroke_c in pellets:
        w_pellet = 60
        frags.append(rect(px_center - w_pellet / 2, 88, w_pellet, 208, fill=fill_c, stroke=stroke_c, sw=2, rx=3))
        frags.append(text(px_center, 195, "%s-Bi₂Te₃" % ptype, size=13, color=stroke_c, bold=True))

    # Стрілки струму (електричне послідовне коло)
    # P1: струм тече вгору від (+) до гарячого
    frags.append(arrow(160, 270, 160, 120, color=POS, sw=2.4))
    # перемичка 1: праворуч
    frags.append(arrow(180, 81, 240, 81, color=INK, sw=2.0))
    # N1: струм тече вниз від гарячого до холодного
    frags.append(arrow(260, 120, 260, 270, color=NEG, sw=2.4))
    # перемичка 2 знизу: праворуч
    frags.append(arrow(280, 303, 340, 303, color=INK, sw=2.0))
    # P2: вгору
    frags.append(arrow(360, 270, 360, 120, color=POS, sw=2.4))
    # перемичка 3 зверху: праворуч
    frags.append(arrow(380, 81, 440, 81, color=INK, sw=2.0))
    # N2: вниз
    frags.append(arrow(460, 120, 460, 270, color=NEG, sw=2.4))

    # Теплові стрілки Q крізь усі стовпчики паралельно
    for px_center, _, _, _ in pellets:
        frags.append(line(px_center + 18, 100, px_center + 18, 280, color=MUTED, sw=1.4, dash="3 3"))

    frags.append(text(430, 442, "Електрично — послідовно (напруги сумуються)  |  Теплово — паралельно (тепло тече крізь усі ніжки)", size=13, color=MUTED, bold=False))

    return render(os.path.join(IMG, 'module-construction.svg'), W, H, *frags,
                  title="Конструкція термоелектричного модуля: послідовне електричне і паралельне теплове з'єднання")


# ── Фігура 3: Еквівалентна тепло-електрична схема ─────────────────────────────
def fig_thermal_electrical():
    W, H = 860, 470
    frags = []

    # Ліва половина: Тепловий домен
    frags.append(rect(40, 45, 365, 370, fill="#fcfcfd", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(222, 70, "Тепловий домен (потік Q, Вт)", size=15, color=POS, bold=True))

    ty = 110
    b_src, _, _ = textbox(222, ty, "Джерело тепла  T_src", size=13, fill="#fdecea", stroke=POS, min_w=220)
    frags.append(b_src)

    frags.append(arrow(222, ty + 18, 222, ty + 46, color=POS, sw=2))
    ty += 65
    b_thot, _, _ = textbox(222, ty, "R_th_hot  (контакт + паста)", size=12, fill=FILL, stroke=LINE, min_w=200)
    frags.append(b_thot)

    frags.append(arrow(222, ty + 18, 222, ty + 46, color=POS, sw=2))
    ty += 65
    b_teg, _, _ = textbox(222, ty, "ТЕГ модуль:  R_th_teg\nΔT_teg = Q · R_th_teg", size=13, fill="#fff8e1", stroke="#b8860b", min_w=220)
    frags.append(b_teg)

    frags.append(arrow(222, ty + 24, 222, ty + 52, color=POS, sw=2))
    ty += 70
    b_sink, _, _ = textbox(222, ty, "Радіатор:  R_th_sink\n скидання в T_amb", size=12, fill="#eaf0fd", stroke=NEG, min_w=200)
    frags.append(b_sink)

    # Зв'язок між доменами (стрілка ΔT → Voc)
    frags.append(arrow(415, 240, 465, 240, color="#b8860b", sw=3))
    frags.append(text(440, 220, "ΔT_teg", size=13, color="#b8860b", bold=True))
    frags.append(text(440, 260, "Voc = N·S·ΔT", size=12, color="#b8860b", bold=True))

    # Права половина: Електричний домен
    frags.append(rect(480, 45, 345, 370, fill="#fcfcfd", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(652, 70, "Електричний домен (Тевенін)", size=15, color=NEG, bold=True))

    # Коло Тевеніна
    ex_src = 550
    ey_top = 140
    ey_bot = 350
    ex_load = 750

    # Джерело ЕРС
    frags.append(circle(ex_src, 200, 22, fill="#fff8e1", stroke="#b8860b", sw=2))
    frags.append(text(ex_src, 205, "Voc", size=14, color="#b8860b", bold=True))
    frags.append(text(ex_src - 36, 205, "+", size=16, color=POS, bold=True))
    frags.append(text(ex_src - 36, 225, "−", size=16, color=NEG, bold=True))

    # Внутрішній опір R_int
    frags.append(line(ex_src, 178, ex_src, ey_top, color=INK, sw=2))
    b_rint, _, _ = textbox(630, ey_top, "R_int  (опір ТЕГ)", size=12, fill=FILL, stroke=LINE, min_w=120)
    frags.append(b_rint)
    frags.append(line(ex_src, ey_top, 570, ey_top, color=INK, sw=2))
    frags.append(line(690, ey_top, ex_load, ey_top, color=INK, sw=2))

    # Нижня шина
    frags.append(line(ex_src, 222, ex_src, ey_bot, color=INK, sw=2))
    frags.append(line(ex_src, ey_bot, ex_load, ey_bot, color=INK, sw=2))

    # Навантаження R_load
    b_rload, _, _ = textbox(ex_load, (ey_top + ey_bot) / 2, "R_load\n(DC-DC)", size=13, fill="#eafaf1", stroke=FIELD, min_w=100)
    frags.append(b_rload)
    frags.append(line(ex_load, ey_top, ex_load, (ey_top + ey_bot) / 2 - 24, color=INK, sw=2))
    frags.append(line(ex_load, (ey_top + ey_bot) / 2 + 24, ex_load, ey_bot, color=INK, sw=2))

    # Струм і вихідна напруга
    frags.append(arrow(700, ey_top, 730, ey_top, color=FIELD, sw=2.4))
    frags.append(text(715, ey_top - 12, "I_out", size=12, color=FIELD, bold=True))
    frags.append(text(ex_load + 20, (ey_top + ey_bot) / 2, "V_out", size=13, color=FIELD, anchor="start", bold=True))

    frags.append(text(430, 442, "Тепловий подільник формує ΔT на ТЕГ  →  ЕРС Voc живить навантаження через R_int", size=13, color=MUTED))

    return render(os.path.join(IMG, 'thermal-electrical-equivalent.svg'), W, H, *frags,
                  title="Тепло-електрична еквівалентна схема термоелектричної системи")


# ── Фігура 4: Узгодження імпедансу (ВАХ і крива потужності P(V)) ───────────────
def fig_impedance_matching():
    W, H = 840, 460
    px, py, pw, ph = 100, 70, 640, 310
    frags = [axes(px, py, pw, ph, "вихідна напруга V", "струм I  та  потужність P")]

    # Точки
    Voc_val = 1.0
    Isc_val = 1.0

    # Функція мапінгу
    def m(v, val):
        # val нормовано до 1.0 (для струму max 1.0, для потужності max 0.25 -> масштабуємо)
        return (px + pw * (v / Voc_val), py + ph - ph * val)

    # ВАХ (пряма лінія I = Isc · (1 - V/Voc))
    iv_pts = [m(v / 100.0, 1.0 - v / 100.0) for v in range(101)]
    frags.append(polyline(iv_pts, color=NEG, sw=2.6))
    frags.append(text(px + 60, py + 30, "ВАХ: I = (Voc − V) / R_int", size=14, color=NEG, bold=True))

    # Крива потужності P = V · I = V · (Voc - V) / R_int (парабола, пік 0.25 на V = 0.5)
    # масштабуємо пік потужності 0.25 на 85% висоти графіка
    pv_pts = [m(v / 100.0, (v / 100.0) * (1.0 - v / 100.0) * (0.85 / 0.25)) for v in range(101)]
    frags.append(polyline(pv_pts, color=FIELD, sw=3.0))
    frags.append(text(px + pw - 80, py + 70, "Потужність P(V)", size=14, color=FIELD, bold=True))

    # Точка MPP
    vmpp_x, vmpp_y = m(0.5, 0.85)
    frags.append(line(vmpp_x, py, vmpp_x, py + ph, color=FIELD, sw=1.6, dash="5 4"))
    frags.append(dot(vmpp_x, vmpp_y, r=6, fill=FIELD))
    frags.append(text(vmpp_x, py - 12, "MPP: V = Voc / 2  (R_load = R_int)", size=15, color=FIELD, bold=True))

    # Позначки на осях
    frags.append(text(px, py + ph + 22, "0", size=12, color=MUTED, anchor="middle"))
    frags.append(text(vmpp_x, py + ph + 22, "Voc / 2", size=13, color=FIELD, anchor="middle", bold=True))
    frags.append(text(px + pw, py + ph + 22, "Voc (ХХ)", size=13, color=MUTED, anchor="middle"))

    frags.append(text(px - 10, py + 10, "Isc (КЗ)", size=12, color=NEG, anchor="end"))
    frags.append(text(px - 10, vmpp_y, "P_max", size=13, color=FIELD, anchor="end", bold=True))

    # Підказка внизу
    frags.append(text(px + pw / 2, py + ph + 54,
                      "Максимальна потужність віддається, коли опір навантаження дорівнює внутрішньому опору ТЕГ",
                      size=13, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, 'impedance-matching-curve.svg'), W, H, *frags,
                  title="Узгодження імпедансу ТЕГ: максимум потужності при V = Voc / 2")


# ── Фігура 5: Архітектура мікропотужного підвищувача з холодним стартом ───────
def fig_cold_start_booster():
    W, H = 880, 440
    frags = []

    # Блок ТЕГ ліворуч
    b_teg, w_teg, h_teg = textbox(110, 170, "ТЕГ модуль\n20–100 мВ\n(низька напруга)",
                                  size=13, fill="#fff8e1", stroke="#b8860b", min_w=150)
    frags.append(b_teg)

    # Автогенератор холодного старту (Мейснер на JFET + трансформатор 1:100)
    b_cold, w_cold, h_cold = textbox(330, 110,
                                     "Холодний старт (20 мВ)\nТрансформатор 1:100\n+ depletion JFET",
                                     size=12, fill="#fdecea", stroke=POS, min_w=180)
    frags.append(b_cold)

    # Основний синхронний Boost
    b_main, w_main, h_main = textbox(330, 240,
                                     "Головний Boost (MPPT)\nСинхронний ШІМ\nККД до 85%",
                                     size=12, fill="#eafaf1", stroke=FIELD, min_w=180)
    frags.append(b_main)

    # Лінії від ТЕГ
    frags.append(arrow(110 + w_teg / 2, 140, 330 - w_cold / 2, 110, color="#b8860b", sw=2.2))
    frags.append(arrow(110 + w_teg / 2, 200, 330 - w_main / 2, 240, color="#b8860b", sw=2.2))

    # Проміжний накопичувач VAUX
    b_vaux, w_vaux, h_vaux = textbox(550, 110, "Резервуар VAUX\n(C_aux > 1.8 В)\nЖивлення логіки",
                                     size=12, fill="#f5f5f5", stroke=LINE, min_w=150)
    frags.append(b_vaux)
    frags.append(arrow(330 + w_cold / 2, 110, 550 - w_vaux / 2, 110, color=POS, sw=2.2))

    # Дозвіл роботи головного перетворювача
    frags.append(arrow(550, 110 + h_vaux / 2, 420, 240 - h_main / 2, color=FIELD, sw=2))
    frags.append(text(520, 180, "EN (старт ШІМ)", size=11, color=FIELD, bold=True))

    # Головний накопичувач енергії (Іоністор / Акумулятор)
    b_stor, w_stor, h_stor = textbox(580, 270, "Накопичувач\nІоністор / LTO\n(2.5–4.2 В)",
                                     size=13, fill="#eaf0fd", stroke=NEG, min_w=150)
    frags.append(b_stor)
    frags.append(arrow(330 + w_main / 2, 240, 580 - w_stor / 2, 270, color=FIELD, sw=2.4))

    # Вихідний стабілізатор (LDO / Buck) і споживач
    b_out, w_out, h_out = textbox(770, 270, "Стабілізатор 3.3 В\n+\nMCU / BLE сенсор",
                                  size=13, fill=FILL, stroke=LINE, min_w=140)
    frags.append(b_out)
    frags.append(arrow(580 + w_stor / 2, 270, 770 - w_out / 2, 270, color=INK, sw=2.2))

    frags.append(text(440, 410, "Автогенератор запускається від 20 мВ, накопичує 1.8 В у VAUX і передає керування високоефективному MPPT Boost", size=13, color=MUTED))

    return render(os.path.join(IMG, 'cold-start-booster.svg'), W, H, *frags,
                  title="Архітектура мікропотужного перетворювача: холодний старт від 20 мВ та перехід на MPPT")


# ── Фігура 6 (вставка math): Тепловий подільник і падіння температури ─────────
def fig_thermal_divider():
    W, H = 840, 460
    px, py, pw, ph = 120, 70, 620, 310
    frags = [axes(px, py, pw, ph, "шари конструкції", "температура T, °C")]

    # Шляхи температури:
    # 0: Гаряча труба (85 °C)
    # 1: Гаряча термопаста (81 °C)
    # 2: Гаряча кераміка ТЕГ (78 °C)
    # 3: Холодна кераміка ТЕГ (45 °C) — робочий ΔT_pellet = 33 K
    # 4: Холодна термопаста (42 °C)
    # 5: Основа радіатора (39 °C)
    # 6: Ребра радіатора (28 °C)
    # 7: Повітря довкілля (20 °C)

    layers = [
        ("Труба", 85.0),
        ("Паста 1", 81.0),
        ("Кераміка Г", 78.0),
        ("Кераміка Х", 45.0),
        ("Паста 2", 42.0),
        ("Основа рад.", 39.0),
        ("Ребра", 28.0),
        ("Повітря", 20.0),
    ]

    t_min, t_max = 15.0, 90.0

    def m_lyr(idx, temp):
        x = px + pw * (idx / (len(layers) - 1))
        y = py + ph - ph * ((temp - t_min) / (t_max - t_min))
        return x, y

    pts = [m_lyr(i, t) for i, (_, t) in enumerate(layers)]

    # Виділення корисної зони на напівпровіднику
    p_hot = pts[2]
    p_cold = pts[3]
    frags.append(rect(p_hot[0], p_hot[1], p_cold[0] - p_hot[0], p_cold[1] - p_hot[1],
                      fill="#fff8e1", stroke="#b8860b", sw=1.5, rx=0))
    frags.append(polyline(pts, color=POS, sw=2.8))

    # Підпис корисного градієнта над зоною (поза лінією)
    b_teg_dt, _, _ = textbox((p_hot[0] + p_cold[0]) / 2, p_hot[1] - 30,
                             "Корисний ΔT_teg = 33 °C", size=12, fill="#fff8e1", stroke="#b8860b", min_w=170)
    frags.append(b_teg_dt)

    for i, (name, temp) in enumerate(layers):
        x, y = pts[i]
        frags.append(dot(x, y, r=4.5, fill=POS))
        frags.append(text(x, py + ph + 20, name, size=11, color=MUTED, anchor="middle"))
        frags.append(text(x, y - 10, "%.0f°" % temp, size=12, color=INK, bold=True))

    # Загальний перепад
    frags.append(line(px - 30, pts[0][1], px - 30, pts[-1][1], color=MUTED, sw=1.5))
    frags.append(text(px - 38, (pts[0][1] + pts[-1][1]) / 2, "Загальний ΔT = 65 °C",
                      size=12, color=MUTED, anchor="end", bold=True))

    frags.append(text(px + pw / 2, py + ph + 54,
                      "Паразитні теплові опори пасти, кераміки та радіатора «з'їдають» половину градієнта",
                      size=13, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, 'thermal-divider.svg'), W, H, *frags,
                  title="Тепловий подільник: розподіл температур від джерела тепла до довкілля")


# ── Фігура 7 (вставка hist): Хронологія відкриттів термоелектрики ──────────────
def fig_timeline():
    W, H = 980, 460
    baseY = 230
    x0, x1 = 90, 890
    xs = [x0 + (x1 - x0) * i / 5 for i in range(6)]
    frags = []

    # Головна вісь часу
    frags.append(line(x0 - 20, baseY, x1 + 40, baseY, color=MUTED, sw=2.6))
    frags.append(arrow(x1 + 20, baseY, x1 + 50, baseY, color=MUTED, sw=2.6))
    frags.append(text(x1 + 50, baseY + 26, "час", size=13, color=MUTED, anchor="end"))

    cards = [
        (xs[0], "above", "1821",       "Томас Зеєбек\nВідкриття термоефекту\n(магнітна стрілка)",   FILL,      LINE),
        (xs[1], "below", "1834",       "Жан Пельтьє\nЗворотний ефект:\nохолодження струмом",        "#eaf0fd", NEG),
        (xs[2], "above", "1854",       "Вільям Томсон\nСпіввідношення Кельвіна\n(термодинаміка)",   FILL,      LINE),
        (xs[3], "below", "1950-ті",    "Абрам Йоффе\nНапівпровідники Bi₂Te₃\nта добротність zT",    "#fff8e1", "#b8860b"),
        (xs[4], "above", "1960–70-ті", "Космічні РІТЕГ\nЖивлення Voyager,\nSNAP та Transit",        "#fdecea", POS),
        (xs[5], "below", "2000-ні+",   "Energy Harvesting\nМікропотужні ІС,\nстарт від 20 мВ",       "#eafaf1", FIELD),
    ]

    off = 95
    for (x, side, year, label, fill, stroke) in cards:
        cy = baseY - off if side == "above" else baseY + off
        box, w, h = textbox(x, cy, label, size=12, fill=fill, stroke=stroke, min_w=150)
        if side == "above":
            frags.append(line(x, baseY - 5, x, cy + h / 2, color=stroke, sw=1.8))
            frags.append(text(x, cy - h / 2 - 10, year, size=16, color=stroke, bold=True))
        else:
            frags.append(line(x, baseY + 5, x, cy - h / 2, color=stroke, sw=1.8))
            frags.append(text(x, cy + h / 2 + 20, year, size=16, color=stroke, bold=True))
        frags.append(box)
        frags.append(dot(x, baseY, 5, fill=stroke))

    return render(os.path.join(IMG, 'timeline.svg'), W, H, *frags,
                  title="Родовід термоелектрики: від компаса Зеєбека до мікропотужних збирачів енергії")


if __name__ == "__main__":
    fig_seebeck_physics()
    fig_module_construction()
    fig_thermal_electrical()
    fig_impedance_matching()
    fig_cold_start_booster()
    fig_thermal_divider()
    fig_timeline()
    print("OK: figures generated into", IMG)
