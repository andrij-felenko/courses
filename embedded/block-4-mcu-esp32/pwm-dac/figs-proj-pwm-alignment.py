# -*- coding: utf-8 -*-
"""
Фігури для вставки §4.7.2a «Edge- і center-aligned ШІМ, мертвий час».
Окремий скрипт; використовує спільний svgkit зі _tools/.
Виводить: img/fig-25-2a-1-center-mechanism.svg
           img/fig-25-2a-2-deadtime.svg
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.7.2a.1 — механізм центрованого ШІМ ───────────────────────────────
def fig_2a1_center_mechanism():
    """
    Чому лічба вгору-вниз дає симетричний імпульс.
    Ліва частина: трикутна траєкторія лічильника + поріг перетинає двічі
                  → двох вертикальних пунктирів обмежують симетричний імпульс.
    Права частина (врізка): пилка (edge-aligned) + один перетин.
    """
    W, H = 920, 400
    parts = []

    # ── заголовок ──
    parts.append(text(W / 2, 28, "Центрований ШІМ: лічильник вгору-вниз перетинає поріг двічі",
                      size=16, bold=True))
    parts.append(text(W / 2, 48,
                      "крайовий — пилка, один перетин, край прив'язаний до початку; "
                      "центрований — трикут, два перетини, імпульс симетричний",
                      size=10, color=MUTED, italic=True))

    # ── осі ліва зона (центрований) ──
    LX, LY = 70, 310      # лівий нижній кут графіка
    LW = 500              # ширина зони
    LH = 210              # висота (від нуля до ВЕРХУ)
    TOP = LY - LH         # y-координата ВЕРХУ лічильника (100)
    CMP_Y = LY - int(LH * 0.55)  # поріг ≈ 55% висоти

    # осі
    parts.append(arrow(LX, LY + 10, LX, TOP - 18, LINE, 1.8))
    parts.append(arrow(LX - 8, LY, LX + LW + 10, LY, LINE, 1.8))
    parts.append(text(LX - 12, TOP - 20, "ВЕРХ", size=9, color=MUTED, anchor="end"))
    parts.append(text(LX + LW + 14, LY + 4, "час", size=9, color=MUTED, anchor="start"))
    parts.append(text(LX - 12, LY + 4, "0", size=9, color=MUTED, anchor="end"))

    # трикутний лічильник (два повних трикути)
    P = 200          # напів-період (вгору) + напів-період (вниз)
    x0 = LX + 10
    tri_pts = []
    for k in range(2):
        bx = x0 + k * P * 2
        tri_pts += [(bx, LY), (bx + P, TOP), (bx + 2 * P, LY)]
    parts.append("\n".join([
        line(tri_pts[i][0], tri_pts[i][1], tri_pts[i + 1][0], tri_pts[i + 1][1],
             FIELD, 2.5)
        for i in range(len(tri_pts) - 1)
    ]))
    parts.append(text(LX + 6, TOP - 8, "лічильник (вгору-вниз)", size=9, color=FIELD,
                      anchor="start", bold=True))

    # поріг порівняння
    parts.append(line(LX, CMP_Y, LX + LW + 5, CMP_Y, "#c08000", 1.6, "6,3"))
    parts.append(text(LX + LW + 8, CMP_Y + 4, "поріг (CMP)", size=9,
                      color="#c08000", anchor="start", bold=True))

    # два перетини на першому трикуті
    # підйом: у moment x0 + P * (1 - CMP_frac) де CMP_frac = (LY - CMP_Y) / LH
    cmp_frac = (LY - CMP_Y) / LH
    x_rise = x0 + int(P * cmp_frac)
    x_fall = x0 + int(P * (2 - cmp_frac))

    # вертикальні пунктири від перетинів до нижнього рядка імпульсу
    PW_Y0 = LY + 25    # верх імпульсного сигналу
    PW_Y1 = LY + 55    # низ імпульсного сигналу
    PW_MID = LY + 40   # середина

    parts.append(line(x_rise, CMP_Y, x_rise, PW_Y1, MUTED, 1.2, "4,3"))
    parts.append(line(x_fall, CMP_Y, x_fall, PW_Y1, MUTED, 1.2, "4,3"))

    # підсвічування ширини імпульсу
    parts.append(f'<rect x="{x_rise}" y="{PW_Y0}" width="{x_fall - x_rise}" '
                 f'height="{PW_Y1 - PW_Y0}" fill="#d4edda" stroke="{FIELD}" stroke-width="1.5" rx="2"/>')
    parts.append(text((x_rise + x_fall) / 2, PW_MID + 5, "імпульс", size=8,
                      color=FIELD, anchor="middle", bold=True))

    # мітки симетрії
    x_peak = x0 + P  # пік трикута (ВЕРХ)
    parts.append(line(x_peak, TOP, x_peak, PW_Y1, MUTED, 1.0, "3,3"))
    parts.append(text(x_peak, PW_Y1 + 14, "центр (ВЕРХ)", size=8, color=MUTED,
                      anchor="middle"))

    # двонаправлена стрілка симетрії
    hw = (x_fall - x_rise) // 2
    parts.append(line(x_rise + 2, PW_Y0 - 8, x_rise + hw - 2, PW_Y0 - 8, FIELD, 1.2))
    parts.append(line(x_rise + hw + 2, PW_Y0 - 8, x_fall - 2, PW_Y0 - 8, FIELD, 1.2))
    parts.append(text(x_peak, PW_Y0 - 15, "рівно", size=8, color=FIELD, anchor="middle"))

    # другий трикут (для природності)
    x0b = x0 + P * 2
    tri2 = [(x0b, LY), (x0b + P, TOP), (x0b + 2 * P, LY)]
    for i in range(len(tri2) - 1):
        parts.append(line(tri2[i][0], tri2[i][1], tri2[i + 1][0], tri2[i + 1][1],
                          FIELD, 2.5))
    x_rise2 = x0b + int(P * cmp_frac)
    x_fall2 = x0b + int(P * (2 - cmp_frac))
    parts.append(f'<rect x="{x_rise2}" y="{PW_Y0}" width="{x_fall2 - x_rise2}" '
                 f'height="{PW_Y1 - PW_Y0}" fill="#d4edda" stroke="{FIELD}" stroke-width="1.5" rx="2"/>')

    # підпис «два перетини»
    parts.append(text(x_rise + 8, CMP_Y - 12, "①", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(x_fall + 4, CMP_Y - 12, "②", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(x_rise + hw, CMP_Y + 18, "перетин двічі →\nдва краї дзеркальні", size=8,
                      color=INK, anchor="middle"))

    # ── врізка: крайовий (edge-aligned) ──
    RX = LX + LW + 55    # початок правої врізки
    RW = 220
    RH = 160
    RY = LY - RH

    parts.append(rect(RX - 8, RY - 32, RW + 16, RH + 52, FILL, LINE, 1.2, 8))
    parts.append(text(RX + RW / 2, RY - 18, "Крайовий (для порівняння)", size=9,
                      color=INK, anchor="middle", bold=True))

    # пилкоподібний лічильник
    E_P = 95
    E_top = RY
    E_bot = RY + RH - 10
    saw_pts = [(RX, E_bot), (RX + E_P, E_top), (RX + E_P, E_bot),
               (RX + 2 * E_P, E_top), (RX + 2 * E_P, E_bot)]
    for i in range(len(saw_pts) - 1):
        parts.append(line(saw_pts[i][0], saw_pts[i][1], saw_pts[i + 1][0], saw_pts[i + 1][1],
                          FIELD, 2.0))

    E_cmp = RY + int(RH * 0.45)
    parts.append(line(RX, E_cmp, RX + 2 * E_P + 10, E_cmp, "#c08000", 1.4, "5,3"))

    # один перетин на першому пилці
    E_x_cross = RX + int(E_P * (1 - (E_bot - E_cmp) / RH))
    parts.append(line(E_x_cross, E_cmp, E_x_cross, E_bot + 18, MUTED, 1.0, "3,3"))

    # імпульс (від початку до перетину — широкий край прибитий до старту)
    parts.append(f'<rect x="{RX}" y="{E_bot + 5}" width="{E_x_cross - RX}" '
                 f'height="14" fill="#d4edda" stroke="{FIELD}" stroke-width="1.2" rx="2"/>')
    parts.append(text(RX + 3, E_bot + 28, "← край прибитий до початку", size=7,
                      color=MUTED, anchor="start"))
    parts.append(text(RX + RW / 2, E_bot + 42, "один перетин", size=8,
                      color=POS, anchor="middle", bold=True))

    # ── підпис знизу ──
    box_txt, bw, bh = textbox(W / 2, H - 22,
                               "Висновок: без жодної доданої логіки — лише змінивши напрям лічби —\n"
                               "лічильник перетинає поріг двічі, і два краї імпульсу стають дзеркальними.\n"
                               "Так з'являється «center-aligned» автоматично.",
                               size=10, fill="#fffbea", stroke="#c08000", sw=1.2, rx=8)
    parts.append(box_txt)

    render(os.path.join(OUT, "fig-25-2a-1-center-mechanism.svg"), W, H, *parts,
           title=None)
    print("wrote fig-25-2a-1-center-mechanism.svg")


# ── Рис. 4.7.2a.2 — мертвий час між ключами ─────────────────────────────────
def fig_2a2_deadtime():
    """
    Комплементарна пара: два рядки сигналів + мертвий час t_dead між ними.
    Позначки: t_off, t_dead = 200 нс = 16 тіків, shoot-through-небезпека.
    """
    W, H = 920, 420
    parts = []

    parts.append(text(W / 2, 28, "Мертвий час: навмисна пауза між «вимкнув один» і «ввімкнув другий»",
                      size=16, bold=True))
    parts.append(text(W / 2, 48,
                      "MOSFET вимикається не миттєво (t_off); без паузи обидва ключі прочинені → shoot-through",
                      size=10, color=MUTED, italic=True))

    # ── часова вісь ──
    AX = 60       # x-початок осі
    AW = 800      # ширина осі
    AY = 380      # y-позиція осі
    parts.append(arrow(AX, AY, AX + AW + 12, AY, LINE, 1.8))
    parts.append(text(AX + AW + 16, AY + 4, "час", size=9, color=MUTED, anchor="start"))

    # ── параметри хвиль ──
    T_HIGH = 220   # ширина HIGH-ділянки (px)
    T_LOW  = 160   # ширина LOW-ділянки (px)
    T_DEAD = 22    # мертвий час у пікселях (≈200 нс в масштабі)
    T_OFF  = 14    # t_off транзистора (px)
    PERIOD = T_HIGH + T_LOW + 2 * T_DEAD
    SIG_H  = 60    # висота HIGH-прямокутника

    # рядок 1: верхній ключ (Q_top)
    R1Y_TOP = 110   # верх HIGH для Q_top
    R1Y_BOT = 170   # низ (LOW) для Q_top

    # рядок 2: нижній ключ (Q_bot)
    R2Y_TOP = 235
    R2Y_BOT = 295

    # початковий x
    x0 = AX + 30

    for rep in range(2):
        bx = x0 + rep * PERIOD

        # ── верхній ключ: HIGH → мертвий → LOW → мертвий → HIGH ──
        # HIGH фаза
        pts_top = [
            (bx, R1Y_BOT), (bx, R1Y_TOP),
            (bx + T_HIGH, R1Y_TOP), (bx + T_HIGH, R1Y_BOT),
            (bx + T_HIGH + T_DEAD + T_LOW + T_DEAD, R1Y_BOT),
            (bx + T_HIGH + T_DEAD + T_LOW + T_DEAD, R1Y_TOP) if rep < 1 else
            (bx + PERIOD, R1Y_TOP)
        ]
        # малюємо ламану для Q_top
        for i in range(len(pts_top) - 1):
            parts.append(line(pts_top[i][0], pts_top[i][1],
                              pts_top[i + 1][0], pts_top[i + 1][1], NEG, 2.5))

        # ── нижній ключ: LOW → мертвий → HIGH → мертвий → LOW ──
        x_dead_end = bx + T_HIGH + T_DEAD
        x_low_end = x_dead_end + T_LOW
        x_dead2_end = x_low_end + T_DEAD
        pts_bot = [
            (bx, R2Y_TOP), (bx, R2Y_BOT),
            (x_dead_end, R2Y_BOT), (x_dead_end, R2Y_TOP),
            (x_low_end, R2Y_TOP), (x_low_end, R2Y_BOT),
            (x_dead2_end, R2Y_BOT),
            (x_dead2_end, R2Y_TOP) if rep < 1 else (bx + PERIOD, R2Y_TOP)
        ]
        for i in range(len(pts_bot) - 1):
            parts.append(line(pts_bot[i][0], pts_bot[i][1],
                              pts_bot[i + 1][0], pts_bot[i + 1][1], POS, 2.5))

        # ── заштриховані смужки мертвого часу ──
        for dead_x in (bx + T_HIGH, x_low_end):
            parts.append(f'<rect x="{dead_x}" y="{R1Y_TOP - 4}" '
                         f'width="{T_DEAD}" height="{R2Y_BOT - R1Y_TOP + 8}" '
                         f'fill="#ffe8e8" stroke="#e07070" stroke-width="0.8" rx="2" opacity="0.7"/>')

    # ── підписи рядків ──
    parts.append(text(AX - 4, (R1Y_TOP + R1Y_BOT) / 2 + 5, "Q_top\n(верхній\nключ)",
                      size=9, color=NEG, anchor="end", bold=True))
    parts.append(text(AX - 4, (R2Y_TOP + R2Y_BOT) / 2 + 5, "Q_bot\n(нижній\nключ)",
                      size=9, color=POS, anchor="end", bold=True))
    parts.append(text(AX - 4, R1Y_TOP - 6, "HIGH", size=8, color=NEG, anchor="end"))
    parts.append(text(AX - 4, R1Y_BOT + 12, "LOW", size=8, color=MUTED, anchor="end"))
    parts.append(text(AX - 4, R2Y_TOP - 6, "HIGH", size=8, color=POS, anchor="end"))
    parts.append(text(AX - 4, R2Y_BOT + 12, "LOW", size=8, color=MUTED, anchor="end"))

    # ── стрілка t_dead із підписом (перший мертвий проміжок) ──
    dead_x1 = x0 + T_HIGH
    dead_cx = dead_x1 + T_DEAD / 2
    parts.append(line(dead_x1 + 1, R1Y_TOP - 24, dead_x1 + T_DEAD - 1, R1Y_TOP - 24, LINE, 1.2))
    parts.append(text(dead_cx, R1Y_TOP - 34, "t_dead", size=9, color=INK, anchor="middle", bold=True))
    parts.append(text(dead_cx, R1Y_TOP - 22, "= 200 нс = 16 тіків", size=8,
                      color=INK, anchor="middle"))
    parts.append(text(dead_cx, (R1Y_BOT + R2Y_TOP) / 2 + 4, "ОБИДВА\nвимкнені",
                      size=8, color="#b04000", anchor="middle", bold=True))

    # ── позначка t_off транзистора ──
    # край HIGH → Q_top вимикається; від T_HIGH до T_HIGH+T_OFF показуємо t_off
    t_off_x = x0 + T_HIGH
    parts.append(line(t_off_x, R2Y_BOT + 20, t_off_x + T_OFF, R2Y_BOT + 20, "#808000", 1.4))
    parts.append(text(t_off_x + T_OFF / 2, R2Y_BOT + 35, "t_off транзистора", size=8,
                      color="#808000", anchor="middle"))

    # ── shoot-through попередження (якби t_dead < t_off) ──
    box2, bw2, bh2 = textbox(680, 200,
                              "Якби t_dead < t_off:\nобидва частково відкриті →\nshoot-through (§4.4.1)",
                              size=9, fill="#fdecea", stroke=POS, sw=1.3, rx=6)
    parts.append(box2)
    # червона стрілка «наскрізного струму»
    parts.append(arrow(660, 215, 580, 215, POS, 1.8))

    # ── масштаб у тіках (внизу) ──
    scale_y = AY + 18
    parts.append(text(AX + 30, scale_y, "Масштаб: 1 тік = 12.5 нс  (такт 80 МГц)   |   t_dead = 200 нс → N = 16 тіків",
                      size=9, color=MUTED, anchor="start"))

    # ── висновок ──
    box3, bw3, bh3 = textbox(W / 2, H - 22,
                               "Таймер MCPWM вставляє t_dead апаратно: задаєш один раз N тіків —\n"
                               "залізо само тримає паузу щоразу при кожному перемиканні пари.\n"
                               "CPU більше не бере участі; точність — 12.5 нс на тік.",
                               size=10, fill="#fffbea", stroke="#c08000", sw=1.2, rx=8)
    parts.append(box3)

    render(os.path.join(OUT, "fig-25-2a-2-deadtime.svg"), W, H, *parts,
           title=None)
    print("wrote fig-25-2a-2-deadtime.svg")


if __name__ == "__main__":
    fig_2a1_center_mechanism()
    fig_2a2_deadtime()
    print("OK – figures for §4.7.2a generated in", OUT)
