# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми «Гальмування мотора: вибіг, динамічне, рекуперація»."""

import os
import sys
import math

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT,
    esc, text, mtext, line, arrow, rect, circle, fitbox, textbox, render
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_four_braking_modes():
    """Чотири режими гальмування H-моста: Вибіг, Динамічне, Рекуперація, Протиувімкнення."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 28, "Порівняння чотирьох режимів гальмування приводу в H-мості", size=17, bold=True))

    panels = [
        ("1. Вільний вибіг (Coasting)", 20, 50, 205, 395, [
            ("Стан ключів", "Усі 4 MOSFET закриті (Hi-Z)"),
            ("Струм", "I = 0 (після спаду в L)"),
            ("Гальмівний момент", "Лише тертя й навантаження"),
            ("Куди дівається енергія", "Механічні втрати, вибіг"),
            ("Ризик", "Неконтрольований рух")
        ], MUTED),
        ("2. Динамічне гальмування", 235, 50, 205, 395, [
            ("Стан ключів", "Нижні ключі Q3, Q4 ON"),
            ("Струм", "Замкнений у контурі моста"),
            ("Гальмівний момент", "Tb = (kt·ke·ω) / R_tot"),
            ("Куди дівається енергія", "Тепло в обмотках (I²·R)"),
            ("Ризик", "Нагрів мотора, слабне при ω→0")
        ], FIELD),
        ("3. Рекуперативне гальмування", 450, 50, 205, 395, [
            ("Стан ключів", "ШІМ нижніх + діоди/синхр."),
            ("Струм", "Тече назад у шину VBUS"),
            ("Гальмівний момент", "Керований ШІМ / FOC"),
            ("Куди дівається енергія", "Повертається в батарею / Cbus"),
            ("Ризик", "Перенапруга шини (Overvoltage)")
        ], NEG),
        ("4. Протиувімкнення (Plugging)", 665, 50, 215, 395, [
            ("Стан ключів", "Подача зворотної діагоналі"),
            ("Струм", "I = (VBUS + E_bemf) / R"),
            ("Гальмівний момент", "Максимальний (ударний)"),
            ("Куди дівається енергія", "Величезне тепло в моторі"),
            ("Ризик", "I ≈ 2·Istall, пробій, удар редуктора")
        ], POS),
    ]

    for title_text, px, py, pw, ph, rows, border_col in panels:
        frags.append(rect(px, py, pw, ph, fill=FILL, stroke=border_col, sw=2, rx=6))
        tb_svg, _, _ = textbox(px + pw / 2, py + 22, title_text, size=11, bold=True, color=border_col, fill="#ffffff", stroke=border_col, pad=6)
        frags.append(tb_svg)

        curr_y = py + 56
        for label_text, val_text in rows:
            frags.append(text(px + 10, curr_y, label_text + ":", size=11, bold=True, color=INK, anchor="start"))
            frags.append(text(px + 10, curr_y + 16, val_text, size=10, color=MUTED, anchor="start"))
            curr_y += 36

        box_y = py + 240
        frags.append(rect(px + 10, box_y, pw - 20, 140, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        
        cx = px + pw / 2
        frags.append(circle(cx, box_y + 65, 20, fill=FILL, stroke=INK, sw=2))
        frags.append(text(cx, box_y + 70, "M", size=13, bold=True))

        if "Coasting" in title_text:
            frags.append(text(cx, box_y + 24, "Q1 [Вимк]    Q2 [Вимк]", size=9, color=MUTED))
            frags.append(text(cx, box_y + 112, "Q3 [Вимк]    Q4 [Вимк]", size=9, color=MUTED))
            frags.append(text(cx, box_y + 130, "Коло розірване (Hi-Z)", size=9, bold=True, color=MUTED))
        elif "Динамічне" in title_text:
            frags.append(text(cx, box_y + 24, "Q1 [Вимк]    Q2 [Вимк]", size=9, color=MUTED))
            frags.append(text(cx, box_y + 112, "Q3 [УВІМК] ═══ Q4 [УВІМК]", size=9, bold=True, color=FIELD))
            frags.append(arrow(cx - 25, box_y + 92, cx + 25, box_y + 92, color=FIELD, sw=2))
            frags.append(text(cx, box_y + 130, "Замкнене коло гальмування", size=9, bold=True, color=FIELD))
        elif "Рекуперативне" in title_text:
            frags.append(text(cx, box_y + 24, "D1 [Діод]  ──►  VBUS", size=9, bold=True, color=NEG))
            frags.append(text(cx, box_y + 112, "Q3 [ШІМ-Boost]   Q4", size=9, color=INK))
            frags.append(arrow(cx, box_y + 44, cx, box_y + 30, color=NEG, sw=2))
            frags.append(text(cx, box_y + 130, "Струм качається у VBUS", size=9, bold=True, color=NEG))
        else:
            frags.append(text(cx, box_y + 24, "+VBUS ──► Q2 [УВІМК]", size=9, bold=True, color=POS))
            frags.append(text(cx, box_y + 112, "Q3 [УВІМК] ◄── GND", size=9, bold=True, color=POS))
            frags.append(text(cx, box_y + 130, "V_tot = VBUS + E_bemf !", size=9, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "four-braking-modes.svg"), w, h, *frags)


def fig_dynamic_braking_circuit():
    """Еквівалентна електрична схема динамічного гальмування та експоненційний спад швидкості."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Динамічне реостатне гальмування: еквівалентне коло та спад швидкості", size=16, bold=True))

    left_x, left_y, left_w, left_h = 20, 50, 450, 350
    frags.append(rect(left_x, left_y, left_w, left_h, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(left_x + left_w / 2, left_y + 24, "Еквівалентна схема генератора при Q3, Q4 ON", size=13, bold=True))

    mx, my = left_x + 90, left_y + 160
    frags.append(circle(mx, my, 28, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(mx, my + 5, "E(ω)", size=12, bold=True, color=FIELD))
    frags.append(text(mx, my - 35, "Генератор протиЕРС", size=10, color=MUTED))

    rx, ry = left_x + 180, left_y + 160
    frags.append(rect(rx - 25, ry - 14, 50, 28, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(rx, ry + 4, "Ra", size=11, bold=True))
    frags.append(text(rx, ry - 20, "Опір якоря", size=9, color=MUTED))

    lx, ly = left_x + 280, left_y + 160
    frags.append(rect(lx - 25, ly - 14, 50, 28, fill="#ffffff", stroke=INK, sw=1.5, rx=8))
    frags.append(text(lx, ly + 4, "La", size=11, bold=True))
    frags.append(text(lx, ly - 20, "Індуктивність", size=9, color=MUTED))

    frags.append(line(mx + 28, my, rx - 25, ry, color=INK, sw=2))
    frags.append(line(rx + 25, ry, lx - 25, ly, color=INK, sw=2))
    frags.append(line(lx + 25, ly, left_x + 380, ly, color=INK, sw=2))

    sw_x = left_x + 380
    frags.append(line(sw_x, ly, sw_x, ly + 90, color=FIELD, sw=2))
    frags.append(rect(sw_x - 35, ly + 35, 70, 26, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(sw_x, ly + 52, "2·Rds(on)", size=10, bold=True, color=FIELD))

    frags.append(line(sw_x, ly + 90, mx, my + 90, color=FIELD, sw=2))
    frags.append(line(mx, my + 90, mx, my + 28, color=FIELD, sw=2))

    frags.append(arrow(sw_x - 40, ly + 90, sw_x - 140, ly + 90, color=FIELD, sw=2.5))
    frags.append(text(left_x + 230, ly + 115, "Гальмівний струм I_brake = E(ω) / R_total", size=11, bold=True, color=FIELD))

    tb_msg1, _, _ = textbox(left_x + left_w / 2, left_y + 305,
                            "Гальмівний момент: T_b = k_t · I_brake = (k_t · k_e · ω) / (R_a + 2·R_ds)\n"
                            "При ω → 0 момент T_b → 0 (мотор не утримує вал у спокої)",
                            size=10, bold=False, color=INK, fill="#ffffff", stroke=FIELD, pad=8)
    frags.append(tb_msg1)

    right_x, right_y, right_w, right_h = 490, 50, 370, 350
    frags.append(rect(right_x, right_y, right_w, right_h, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(right_x + right_w / 2, right_y + 24, "Динаміка швидкості ω(t) та моменту T(t)", size=13, bold=True))

    gx, gy, gw, gh = right_x + 55, right_y + 220, 270, 150
    frags.append(arrow(gx, gy, gx + gw + 20, gy, color=LINE, sw=1.5))
    frags.append(arrow(gx, gy, gx, gy - gh - 20, color=LINE, sw=1.5))
    frags.append(text(gx + gw + 15, gy + 18, "Час t", size=10, color=MUTED))
    frags.append(text(gx - 10, gy - gh - 15, "ω, I, T", size=10, bold=True, color=INK))

    pts_curve = []
    for step in range(30):
        t_norm = step / 29.0
        px_val = gx + t_norm * gw
        py_val = gy - gh * math.exp(-3.0 * t_norm)
        pts_curve.append(f"{px_val:.1f},{py_val:.1f}")

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_curve), NEG))
    frags.append(text(gx + 105, gy - 75, "ω(t) = ω₀ · e^(-t / τ_mech)", size=11, bold=True, color=NEG))

    t1_x = gx + gw / 3.0
    frags.append(line(t1_x, gy, t1_x, gy - gh * math.exp(-1.0), color=MUTED, sw=1, dash="4,3"))
    frags.append(text(t1_x, gy + 16, "t = τ_mech (36.8%)", size=9, color=MUTED))

    tb_msg2, _, _ = textbox(right_x + right_w / 2, right_y + 305,
                            "Механічна стала часу: τ_mech = (J · R_total) / (k_t · k_e)\n"
                            "Енергія обертання 0.5·J·ω₀² розсіюється в тепло обмоток",
                            size=10, color=INK, fill="#ffffff", stroke=LINE, pad=8)
    frags.append(tb_msg2)

    render(os.path.join(IMG_DIR, "dynamic-braking-circuit.svg"), w, h, *frags)


def fig_regen_boost_action():
    """Рекуперативне гальмування: механізм Boost-перетворювача в H-мості."""
    w, h = 900, 420
    frags = []

    frags.append(text(w / 2, 28, "Рекуперація як підвищувальний (Boost) перетворювач у силі H-моста", size=16, bold=True))

    p1_x, p1_y, p1_w, p1_h = 20, 50, 420, 350
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill=FILL, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "Фаза 1: Нижній ключ ON (ШІМ накачування L)", size=12, bold=True, color=NEG))

    cx1 = p1_x + 90
    frags.append(circle(cx1, p1_y + 130, 24, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(cx1, p1_y + 134, "E_bemf", size=10, bold=True))

    lx1 = p1_x + 180
    frags.append(rect(lx1 - 20, p1_y + 118, 40, 24, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(lx1, p1_y + 134, "L", size=11, bold=True))

    frags.append(line(p1_x + 280, p1_y + 60, p1_x + 400, p1_y + 60, color=POS, sw=2))
    frags.append(text(p1_x + 340, p1_y + 52, "+VBUS (Шина)", size=10, bold=True, color=POS))

    frags.append(rect(p1_x + 260, p1_y + 75, 40, 25, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    frags.append(text(p1_x + 280, p1_y + 92, "D1 (OFF)", size=9, color=MUTED))

    frags.append(rect(p1_x + 260, p1_y + 135, 50, 30, fill="#ffffff", stroke=FIELD, sw=2, rx=4))
    frags.append(text(p1_x + 285, p1_y + 154, "Q3 [ON]", size=10, bold=True, color=FIELD))
    frags.append(line(p1_x + 285, p1_y + 165, p1_x + 285, p1_y + 200, color=LINE, sw=2))
    frags.append(text(p1_x + 285, p1_y + 215, "GND", size=10, bold=True))

    frags.append(line(cx1 + 24, p1_y + 130, lx1 - 20, p1_y + 130, color=INK, sw=2))
    frags.append(line(lx1 + 20, p1_y + 130, p1_x + 260, p1_y + 150, color=INK, sw=2))
    frags.append(line(cx1, p1_y + 154, cx1, p1_y + 200, color=LINE, sw=2))
    frags.append(line(cx1, p1_y + 200, p1_x + 285, p1_y + 200, color=LINE, sw=2))

    frags.append(arrow(lx1 - 30, p1_y + 110, lx1 + 40, p1_y + 110, color=NEG, sw=2.5))
    frags.append(text(p1_x + 160, p1_y + 98, "Струм I зростає: dI/dt = E/L", size=10, bold=True, color=NEG))

    tb_p1, _, _ = textbox(p1_x + p1_w / 2, p1_y + 285,
                          "• ПротиЕРС мотора E_bemf менша за напругу VBUS (E < VBUS)\n"
                          "• Нижній ключ замикає котушку L на землю\n"
                          "• Струм зростає, запасаючи енергію у магнітному полі: E = 0.5·L·I²\n"
                          "• Верхній діод D1 закритий зворотною напругою шини",
                          size=9.5, color=INK, fill="#ffffff", stroke=NEG, pad=8)
    frags.append(tb_p1)

    p2_x, p2_y, p2_w, p2_h = 460, 50, 420, 350
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill=FILL, stroke=POS, sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "Фаза 2: Нижній ключ OFF (Викид L + E у VBUS)", size=12, bold=True, color=POS))

    cx2 = p2_x + 90
    frags.append(circle(cx2, p2_y + 130, 24, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(cx2, p2_y + 134, "E_bemf", size=10, bold=True))

    lx2 = p2_x + 180
    frags.append(rect(lx2 - 20, p2_y + 118, 40, 24, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(lx2, p2_y + 134, "L", size=11, bold=True))

    frags.append(line(p2_x + 280, p2_y + 60, p2_x + 400, p2_y + 60, color=POS, sw=2.5))
    frags.append(text(p2_x + 340, p2_y + 52, "+VBUS (Зростає!)", size=10, bold=True, color=POS))

    cap_x = p2_x + 360
    frags.append(line(cap_x, p2_y + 60, cap_x, p2_y + 110, color=POS, sw=1.5))
    frags.append(rect(cap_x - 15, p2_y + 110, 30, 20, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(cap_x, p2_y + 124, "Cbus", size=9, bold=True))
    frags.append(line(cap_x, p2_y + 130, cap_x, p2_y + 200, color=LINE, sw=1.5))

    frags.append(rect(p2_x + 260, p2_y + 75, 55, 30, fill="#ffffff", stroke=POS, sw=2, rx=4))
    frags.append(text(p2_x + 287, p2_y + 94, "D1 [ON]", size=10, bold=True, color=POS))
    frags.append(line(p2_x + 287, p2_y + 75, p2_x + 287, p2_y + 60, color=POS, sw=2))

    frags.append(rect(p2_x + 260, p2_y + 145, 50, 25, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    frags.append(text(p2_x + 285, p2_y + 162, "Q3 [OFF]", size=9, color=MUTED))

    frags.append(line(cx2 + 24, p2_y + 130, lx2 - 20, p2_y + 130, color=INK, sw=2))
    frags.append(line(lx2 + 20, p2_y + 130, p2_x + 287, p2_y + 105, color=POS, sw=2))
    frags.append(line(cx2, p2_y + 154, cx2, p2_y + 200, color=LINE, sw=2))
    frags.append(line(cx2, p2_y + 200, cap_x, p2_y + 200, color=LINE, sw=2))

    frags.append(arrow(p2_x + 287, p2_y + 105, p2_x + 287, p2_y + 65, color=POS, sw=2.5))
    frags.append(text(p2_x + 215, p2_y + 85, "U = E + L·(dI/dt) > VBUS", size=10, bold=True, color=POS))

    tb_p2, _, _ = textbox(p2_x + p2_w / 2, p2_y + 285,
                          "• Нижній ключ розмикається, індуктивність L підтримує струм\n"
                          "• Сумарна напруга E_bemf + V_L перевищує рівень VBUS\n"
                          "• Струм крізь діод D1 заряджає конденсатор Cbus та живить джерело\n"
                          "• Ризик: без споживача напруга VBUS неконтрольовано зростає!",
                          size=9.5, color=INK, fill="#ffffff", stroke=POS, pad=8)
    frags.append(tb_p2)

    render(os.path.join(IMG_DIR, "regen-boost-action.svg"), w, h, *frags)


def fig_brake_chopper_circuit():
    """Схема гальмівного переривача (Brake Chopper) з баластним резистором та гістерезисом."""
    w, h = 900, 440
    frags = []

    frags.append(text(w / 2, 28, "Гальмівний переривач (Brake Chopper) захисту шини VBUS від перенапруги", size=16, bold=True))

    sx, sy, sw, sh = 20, 50, 490, 370
    frags.append(rect(sx, sy, sw, sh, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(sx + sw / 2, sy + 24, "Принципова схема гальмівного переривача", size=13, bold=True))

    frags.append(line(sx + 30, sy + 60, sx + 460, sy + 60, color=POS, sw=2.5))
    frags.append(text(sx + 80, sy + 50, "+VBUS (Шина живлення)", size=11, bold=True, color=POS))

    frags.append(line(sx + 30, sy + 320, sx + 460, sy + 320, color=LINE, sw=2.5))
    frags.append(text(sx + 80, sy + 338, "GND (Силова земля)", size=11, bold=True))

    frags.append(rect(sx + 35, sy + 80, 80, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(sx + 75, sy + 100, ["AC/DC", "Блок живлення"], size=9, bold=True))
    frags.append(line(sx + 75, sy + 80, sx + 75, sy + 60, color=POS, sw=2))
    frags.append(line(sx + 75, sy + 130, sx + 75, sy + 320, color=LINE, sw=1.5))

    cx = sx + 150
    frags.append(rect(cx - 15, sy + 130, 30, 40, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    frags.append(text(cx, sy + 155, "C_bus", size=10, bold=True))
    frags.append(line(cx, sy + 60, cx, sy + 130, color=POS, sw=1.5))
    frags.append(line(cx, sy + 170, cx, sy + 320, color=LINE, sw=1.5))

    dx = sx + 225
    frags.append(rect(dx - 12, sy + 90, 24, 30, fill="#ffffff", stroke=INK, sw=1, rx=2))
    frags.append(text(dx, sy + 108, "R1", size=9))
    frags.append(rect(dx - 12, sy + 160, 24, 30, fill="#ffffff", stroke=INK, sw=1, rx=2))
    frags.append(text(dx, sy + 178, "R2", size=9))
    frags.append(line(dx, sy + 60, dx, sy + 90, color=POS, sw=1))
    frags.append(line(dx, sy + 120, dx, sy + 160, color=INK, sw=1))
    frags.append(line(dx, sy + 190, dx, sy + 320, color=LINE, sw=1))

    k_x, k_y = sx + 300, sy + 140
    frags.append(rect(k_x - 35, k_y - 25, 70, 50, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(mtext(k_x, k_y - 5, ["Компаратор", "гістерезису"], size=9.5, bold=True, color=FIELD))
    frags.append(line(dx, sy + 140, k_x - 35, k_y, color=INK, sw=1))

    bx = sx + 410
    frags.append(rect(bx - 20, sy + 85, 40, 45, fill="#ffffff", stroke=POS, sw=2, rx=4))
    frags.append(mtext(bx, sy + 103, ["R_brake", "Баласт"], size=9, bold=True, color=POS))
    frags.append(line(bx, sy + 60, bx, sy + 85, color=POS, sw=2))

    frags.append(rect(bx + 28, sy + 92, 20, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=2))
    frags.append(text(bx + 38, sy + 110, "D", size=9, color=MUTED))
    frags.append(line(bx, sy + 75, bx + 38, sy + 75, color=MUTED, sw=1))
    frags.append(line(bx + 38, sy + 75, bx + 38, sy + 92, color=MUTED, sw=1))
    frags.append(line(bx + 38, sy + 122, bx + 38, sy + 140, color=MUTED, sw=1))
    frags.append(line(bx, sy + 140, bx + 38, sy + 140, color=MUTED, sw=1))

    frags.append(rect(bx - 22, sy + 165, 44, 40, fill="#ffffff", stroke=FIELD, sw=2, rx=4))
    frags.append(mtext(bx, sy + 183, ["Q_chop", "MOSFET"], size=9, bold=True, color=FIELD))
    frags.append(line(bx, sy + 130, bx, sy + 165, color=POS, sw=2))
    frags.append(line(bx, sy + 205, bx, sy + 320, color=LINE, sw=2))

    frags.append(arrow(k_x + 30, sy + 185, bx - 22, sy + 185, color=FIELD, sw=1.5))
    frags.append(text(sx + 345, sy + 175, "GATE", size=9, bold=True, color=FIELD))

    frags.append(text(sx + sw / 2, sy + 355, "Струм баласту скидає енергію в тепло: P = VBUS² / R_brake", size=10, bold=True, color=POS))

    rx, ry, rw, rh = 525, 50, 355, 370
    frags.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(rx + rw / 2, ry + 24, "Гістерезисна стабілізація VBUS", size=13, bold=True))

    gx, gy, gw, gh = rx + 45, ry + 250, 260, 170
    frags.append(arrow(gx, gy, gx + gw + 25, gy, color=LINE, sw=1.5))
    frags.append(arrow(gx, gy, gx, gy - gh - 20, color=LINE, sw=1.5))
    frags.append(text(gx + gw + 15, gy + 16, "t", size=11, color=MUTED))
    frags.append(text(gx - 10, gy - gh - 15, "VBUS", size=11, bold=True, color=INK))

    v_ov = gy - 160
    v_on = gy - 130
    v_off = gy - 95
    v_nom = gy - 40

    frags.append(line(gx, v_ov, gx + gw, v_ov, color=POS, sw=1.5, dash="4,3"))
    frags.append(text(gx + gw + 2, v_ov + 4, "V_max (Аварія OVP)", size=9, bold=True, color=POS, anchor="start"))

    frags.append(line(gx, v_on, gx + gw, v_on, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(text(gx + gw + 2, v_on + 4, "V_chop_ON", size=9, bold=True, color=FIELD, anchor="start"))

    frags.append(line(gx, v_off, gx + gw, v_off, color=NEG, sw=1.5, dash="4,3"))
    frags.append(text(gx + gw + 2, v_off + 4, "V_chop_OFF", size=9, bold=True, color=NEG, anchor="start"))

    frags.append(line(gx, v_nom, gx + gw, v_nom, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(gx + gw + 2, v_nom + 4, "V_nominal", size=9, color=MUTED, anchor="start"))

    wave_pts = [
        f"{gx:.1f},{v_nom:.1f}", f"{gx + 30:.1f},{v_nom:.1f}",
        f"{gx + 60:.1f},{v_on:.1f}", f"{gx + 75:.1f},{v_off:.1f}",
        f"{gx + 95:.1f},{v_on:.1f}", f"{gx + 110:.1f},{v_off:.1f}",
        f"{gx + 130:.1f},{v_on:.1f}", f"{gx + 145:.1f},{v_off:.1f}",
        f"{gx + 175:.1f},{v_nom + 10:.1f}", f"{gx + 240:.1f},{v_nom:.1f}"
    ]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(wave_pts), POS))

    frags.append(text(gx + 100, gy + 32, "◄── Рекуперація: Chopper скидає надлишок ──►", size=9.5, bold=True, color=FIELD))

    tb_chop, _, _ = textbox(rx + rw / 2, ry + 325,
                            "• VBUS досягає V_chop_ON → ключ Q_chop вмикається\n"
                            "• Енергія розсіюється на R_brake, напруга спадає до V_chop_OFF\n"
                            "• Гістерезис ΔV запобігає брязкоту компаратора",
                            size=9, color=INK, fill="#ffffff", stroke=LINE, pad=6)
    frags.append(tb_chop)

    render(os.path.join(IMG_DIR, "brake-chopper-circuit.svg"), w, h, *frags)


def fig_plug_braking_stress():
    """Порівняння теплового та механічного навантаження при протиувімкненні (Plugging) та інших режимах."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Гальмування протиувімкненням (Plugging): електричні та механічні перевантаження", size=16, bold=True))

    lx, ly, lw, lh = 20, 50, 400, 350
    frags.append(rect(lx, ly, lw, lh, fill=FILL, stroke=POS, sw=1.5, rx=6))
    frags.append(text(lx + lw / 2, ly + 24, "Складання напруг джерела та протиЕРС", size=13, bold=True, color=POS))

    frags.append(text(lx + 20, ly + 60, "1. Звичайний робочий хід:", size=11, bold=True, anchor="start"))
    frags.append(arrow(lx + 30, ly + 85, lx + 230, ly + 85, color=POS, sw=3))
    frags.append(text(lx + 130, ly + 78, "+VBUS (24 В)", size=10, bold=True, color=POS))
    frags.append(arrow(lx + 230, ly + 105, lx + 50, ly + 105, color=NEG, sw=3))
    frags.append(text(lx + 140, ly + 120, "E_bemf (-20 В)", size=10, bold=True, color=NEG))
    frags.append(text(lx + 250, ly + 95, "V_net = 24 - 20 = 4 В\nI = 4 В / 0.5 Ом = 8 А", size=9.5, color=INK, anchor="start"))

    frags.append(line(lx + 20, ly + 140, lx + lw - 20, ly + 140, color=MUTED, sw=1, dash="3,3"))

    frags.append(text(lx + 20, ly + 165, "2. Гальмування протиувімкненням (Реверс на ходу):", size=11, bold=True, color=POS, anchor="start"))
    frags.append(arrow(lx + 30, ly + 195, lx + 210, ly + 195, color=POS, sw=3))
    frags.append(text(lx + 120, ly + 188, "V_reverse (24 В)", size=10, bold=True, color=POS))
    frags.append(arrow(lx + 210, ly + 195, lx + 360, ly + 195, color=POS, sw=3))
    frags.append(text(lx + 285, ly + 188, "E_bemf (20 В)", size=10, bold=True, color=POS))
    frags.append(text(lx + 20, ly + 230, "Сумарна напруга на обмотці: V_tot = VBUS + E_bemf = 44 В !", size=10, bold=True, color=POS, anchor="start"))
    frags.append(text(lx + 20, ly + 250, "Піковий струм: I_plug = 44 В / 0.5 Ом = 88 А (у 2× вище пускового!)", size=9.5, bold=True, color=POS, anchor="start"))

    tb_plug, _, _ = textbox(lx + lw / 2, ly + 300,
                            "Теплові втрати P = I²·R зростають у 100+ разів порівняно з нормою!\n"
                            "Критичний ризик розмагнічування магнітів ротора та удару зубів.",
                            size=9, color=INK, fill="#ffffff", stroke=POS, pad=6)
    frags.append(tb_plug)

    rx, ry, rw, rh = 440, 50, 420, 350
    frags.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(rx + rw / 2, ry + 24, "Порівняння пікового струму та теплових втрат", size=13, bold=True))

    bars = [
        ("Вибіг (Coasting)", 5, 0, MUTED),
        ("Динамічне", 40, 35, FIELD),
        ("Рекуперація", 45, 10, NEG),
        ("Протиувімкнення", 100, 100, POS)
    ]

    bx_start = rx + 25
    by_start = ry + 65

    frags.append(text(bx_start, by_start, "Режим", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(bx_start + 130, by_start, "Піковий струм", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(bx_start + 260, by_start, "Тепловий стрес", size=10, bold=True, color=INK, anchor="start"))

    curr_y = by_start + 25
    for mode_name, i_val, heat_val, bar_col in bars:
        frags.append(text(bx_start, curr_y + 12, mode_name, size=10, bold=True, color=bar_col, anchor="start"))

        frags.append(rect(bx_start + 120, curr_y, 100, 16, fill="#e5e7eb", stroke=LINE, sw=0.5, rx=2))
        if i_val > 0:
            frags.append(rect(bx_start + 120, curr_y, i_val, 16, fill=bar_col, stroke=bar_col, sw=0.5, rx=2))
        frags.append(text(bx_start + 225, curr_y + 12, f"{i_val}%", size=9, color=MUTED, anchor="start"))

        frags.append(rect(bx_start + 260, curr_y, 100, 16, fill="#e5e7eb", stroke=LINE, sw=0.5, rx=2))
        if heat_val > 0:
            frags.append(rect(bx_start + 260, curr_y, heat_val, 16, fill=bar_col, stroke=bar_col, sw=0.5, rx=2))
        frags.append(text(bx_start + 365, curr_y + 12, f"{heat_val}%", size=9, color=MUTED, anchor="start"))

        curr_y += 38

    tb_concl, _, _ = textbox(rx + rw / 2, ry + 295,
                             "Висновки для проектування:\n"
                             "• Протиувімкнення припустиме лише як АВАРІЙНЕ (Emergency Stop)\n"
                             "• Потребує вимкнення при ω = 0 (інакше реверс на повній швидкості)\n"
                             "• Штатними режимами є динамічне та рекуперативне гальмування",
                             size=9, color=INK, fill="#ffffff", stroke=LINE, pad=6)
    frags.append(tb_concl)

    render(os.path.join(IMG_DIR, "plug-braking-stress.svg"), w, h, *frags)


def main():
    fig_four_braking_modes()
    fig_dynamic_braking_circuit()
    fig_regen_boost_action()
    fig_brake_chopper_circuit()
    fig_plug_braking_stress()
    print("All figures successfully generated in img/")


if __name__ == "__main__":
    main()
