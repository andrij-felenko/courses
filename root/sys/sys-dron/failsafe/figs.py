# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Безпечний відмов (failsafe)».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: перелік відмов — ознака → безпечна дія ─────────────────────────
# Ідея: failsafe = наперед складена таблиця пар «як помітити збій» → «що зробити».
# Кожна біда має свою ОЗНАКУ (відсутність сигналу життя) і свою БЕЗПЕЧНУ ДІЮ.
def fig_failure_modes():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Failsafe — таблиця «ознака збою → безпечна дія»",
                  size=17, bold=True))

    # три колонки: відмова | ознака | безпечна дія
    col_fail = 165
    col_sign = W / 2
    col_act = W - 175
    head_y = 70
    P.append(text(col_fail, head_y, "ВІДМОВА", size=13, bold=True, color=INK))
    P.append(text(col_sign, head_y, "ОЗНАКА (як помітити)", size=13, bold=True, color=NEG))
    P.append(text(col_act, head_y, "БЕЗПЕЧНА ДІЯ", size=13, bold=True, color=FIELD))
    P.append(line(60, head_y + 12, W - 60, head_y + 12, color="#d0d5dd", sw=1.2))

    rows = [
        ("Втрата зв'язку", "немає серцебиття", "повернутись додому (RTL)"),
        ("Втрата GPS", "зникла фіксація", "тримати лише висоту"),
        ("Просідання живлення", "напруга падає", "посадка, доки є заряд"),
        ("Зависання коду", "поступ припинився", "скид watchdog"),
        ("Замовкання давача", "дані застаріли / абсурдні", "резерв або обережний режим"),
    ]
    y0 = head_y + 50
    dy = 66
    for i, (fail, sign, act) in enumerate(rows):
        y = y0 + i * dy
        # рамка-біда (ліворуч)
        fr, w, h = textbox(col_fail, y, fail, size=12, bold=True,
                           fill="#eef2f7", stroke=INK, min_w=210)
        P.append(fr)
        # ознака (середина, синім)
        fr, w, h = textbox(col_sign, y, sign, size=12, color=NEG,
                           fill="#eaf0fd", stroke=NEG, min_w=230)
        P.append(fr)
        # дія (праворуч, зеленим)
        fr, w, h = textbox(col_act, y, act, size=12, color=FIELD, bold=True,
                           fill="#e9f7ef", stroke=FIELD, min_w=230)
        P.append(fr)
        # стрілки ознака → дія
        P.append(arrow(col_sign + 118, y, col_act - 118, y, color=MUTED))

    render("img/failure-modes.svg", W, H, *P)


# ── Фігура 2: поетапна реакція failsafe (дві осі: тривалість × тяжкість) ─────
# Ідея: реакція наростає від попередження до негайної посадки за тривалістю
# тривоги й тяжкістю збою; коли збоїв кілька — перемагає найнебезпечніший.
def fig_escalation_levels():
    W, H = 940, 520
    P = []
    P.append(text(W / 2, 30, "Реакція failsafe наростає: тривалість × тяжкість",
                  size=17, bold=True))

    # координатні осі
    ox, oy = 130, H - 90          # початок осей
    ax_top, ax_right = 80, W - 70
    P.append(arrow(ox, oy, ox, ax_top, color=INK, sw=1.8))   # вісь тяжкості (вгору)
    P.append(arrow(ox, oy, ax_right, oy, color=INK, sw=1.8))  # вісь часу (праворуч)
    P.append(text(ox - 60, (ax_top + oy) / 2, "тяжкість", size=12.5,
                  color=INK, bold=True))
    P.append(text(ox - 60, (ax_top + oy) / 2 + 16, "збою", size=12.5,
                  color=INK, bold=True))
    P.append(text((ox + ax_right) / 2, oy + 40, "тривалість тривоги →",
                  size=12.5, color=INK, bold=True))

    # чотири рівні по діагоналі: що далі/вище — то рішучіше
    steps = [
        (0.18, 0.20, "рівень 1\nпопередити\nоператора", FIELD, "#e9f7ef"),
        (0.42, 0.42, "рівень 2\nбезпечніший режим\n(утримання висоти)", "#b08900", "#fdf6e3"),
        (0.66, 0.66, "рівень 3\nавтономне\nповернення (RTL)", "#c0560b", "#fdeede"),
        (0.88, 0.90, "рівень 4\nнегайна посадка /\nвимкнення", POS, "#fdecea"),
    ]
    span_x = ax_right - ox
    span_y = oy - ax_top
    prev = None
    for fx, fy, label, col, fill in steps:
        cx = ox + fx * span_x
        cy = oy - fy * span_y
        if prev:
            P.append(arrow(prev[0], prev[1], cx, cy, color=MUTED, sw=1.5))
        fr, w, h = textbox(cx, cy, label, size=11.5, bold=True,
                           color=col, fill=fill, stroke=col)
        P.append(fr)
        prev = (cx, cy)

    # нижня примітка про пріоритет
    fr, w, h = textbox(W / 2, H - 28,
                       "коли збоїв кілька — перемагає НАЙНЕБЕЗПЕЧНІШИЙ "
                       "(сіла батарея > втрата зв'язку)",
                       size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr)

    render("img/escalation-levels.svg", W, H, *P)


if __name__ == "__main__":
    fig_failure_modes()
    fig_escalation_levels()
    print("OK: 2 figures -> img/")
