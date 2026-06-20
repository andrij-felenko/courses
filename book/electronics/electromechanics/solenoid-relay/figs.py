# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Соленоїд і реле».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: спільне серце — пружина проти магнітної тяги ───────────────────
# Першопричина всього класу: котушка на осерді тягне феромагнітний якір усередину,
# а пружина повертає його назад. Без струму перемагає пружина (якір зовні);
# зі струмом поле перемагає пружину (якір втягнуто). Показуємо два стани поряд,
# щоб видно було саме ЗМАГАННЯ двох сил, а не просто «котушку з залізкою».
def fig_core():
    W, H = 900, 360
    parts = []

    def panel(ox, title, energized):
        p = []
        # рамка-підпис стану
        p.append(fitbox(ox + 20, 70, 360, 30, title, size=15, bold=True,
                        fill="#eef2f7", stroke=INK))

        coil_x, coil_y, coil_w, coil_h = ox + 60, 150, 150, 120
        # осердя (нерухоме залізо) ліворуч від котушки
        p.append(rect(coil_x - 36, coil_y + 30, 36, 60, fill="#e7eaee", stroke=INK, sw=2, rx=3))
        p.append(text(coil_x - 18, coil_y + 112, "осердя", size=12, color=MUTED))

        # котушка — кілька витків
        for i in range(6):
            yy = coil_y + 10 + i * 18
            col = POS if energized else MUTED
            p.append('<ellipse cx="%.1f" cy="%.1f" rx="14" ry="8" fill="none" '
                     'stroke="%s" stroke-width="3"/>' % (coil_x + 30, yy, col))
        p.append(text(coil_x + 30, coil_y - 8, "котушка", size=12, color=MUTED))

        # якір (рухоме залізо) праворуч; коли під струмом — присунутий до осердя
        arm_x = coil_x + 96 if energized else coil_x + 140
        p.append(rect(arm_x, coil_y + 28, 34, 64, fill="#dfe4ea", stroke=INK, sw=2, rx=3))
        p.append(text(arm_x + 17, coil_y + 112, "якір", size=12, color=INK))

        # пружина (праворуч від якоря) — зигзаг
        sx = arm_x + 34
        sy = coil_y + 60
        spring = "M %.1f %.1f " % (sx, sy)
        seg = 10 if energized else 16   # під струмом пружина стиснута
        for i in range(5):
            x1 = sx + i * seg + seg / 2
            x2 = sx + (i + 1) * seg
            spring += "L %.1f %.1f L %.1f %.1f " % (x1, sy - 9, x2, sy)
        wall = sx + 5 * seg + 6
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (spring, MUTED))
        p.append(line(wall, coil_y + 24, wall, coil_y + 96, color=INK, sw=4))   # стінка-упор
        p.append(text(sx + 2.5 * seg, sy + 26, "пружина", size=12, color=MUTED))

        # стрілка домінантної сили
        if energized:
            p.append(arrow(arm_x + 17, coil_y + 18, arm_x - 22, coil_y + 18, color=POS, sw=3))
            p.append(text(arm_x - 4, coil_y + 6, "тяга поля B", size=12, color=POS, bold=True))
        else:
            p.append(arrow(arm_x + 17, coil_y + 18, arm_x + 52, coil_y + 18, color=MUTED, sw=3))
            p.append(text(arm_x + 22, coil_y + 6, "тримає", size=12, color=MUTED, bold=True))
        return p

    parts += panel(0, "Без струму: якір зовні", False)
    parts.append(line(W / 2, 60, W / 2, H - 20, color="#d0d5dd", sw=1.5, dash="5,5"))
    parts += panel(W / 2, "Під струмом: якір втягнуто", True)

    return render("img/core.svg", W, H, *parts, title="Спільне серце: пружина проти магнітної тяги")


# ── Фігура 2: один механізм — три застосунки + спільне коло керування ─────────
# Та сама котушка-якір, але до якоря причеплено РІЗНЕ: контакти (реле),
# шток (соленоїд), затвор на сідлі (клапан). Унизу — спільний триланковий
# ланцюг: вивід МК → ключ → котушка, з гасним діодом на котушці.
def fig_three():
    W, H = 900, 470
    parts = []

    col_w = W / 3
    top = 70

    # --- реле ---
    cx = col_w / 2
    parts.append(fitbox(cx - 110, top, 220, 28, "Реле: рухає контакти", size=14, bold=True,
                        fill="#eef2f7", stroke=INK))
    parts.append(circle(cx, 150, 6, fill=INK, stroke=INK))
    parts.append(text(cx - 26, 154, "COM", size=12, color=INK, anchor="end"))
    parts.append(line(cx, 150, cx + 46, 128))                       # рухомий контакт до NO
    parts.append(circle(cx + 52, 124, 6, fill=BG, stroke=FIELD, sw=2))
    parts.append(text(cx + 60, 122, "NO", size=12, color=FIELD, anchor="start"))
    parts.append(circle(cx + 52, 176, 6, fill=BG, stroke=POS, sw=2))
    parts.append(text(cx + 60, 180, "NC", size=12, color=POS, anchor="start"))
    parts.append(text(cx, 210, "слабкий сигнал →\nсильне коло", size=12, color=MUTED))

    # --- соленоїд ---
    cx = col_w + col_w / 2
    parts.append(fitbox(cx - 110, top, 220, 28, "Соленоїд: штовхає тягу", size=14, bold=True,
                        fill="#eef2f7", stroke=INK))
    parts.append(rect(cx - 40, 120, 50, 60, fill="#e7eaee", stroke=INK, sw=2, rx=4))   # корпус котушки
    parts.append(rect(cx + 10, 138, 70, 24, fill="#dfe4ea", stroke=INK, sw=2, rx=3))   # шток
    parts.append(arrow(cx + 80, 150, cx + 120, 150, color=POS, sw=3))
    parts.append(text(cx + 100, 138, "хід", size=12, color=POS, bold=True))
    parts.append(text(cx, 210, "короткий лінійний\nхід і сила", size=12, color=MUTED))

    # --- клапан ---
    cx = 2 * col_w + col_w / 2
    parts.append(fitbox(cx - 110, top, 220, 28, "Клапан: перекриває отвір", size=14, bold=True,
                        fill="#eef2f7", stroke=INK))
    parts.append(rect(cx - 60, 150, 120, 22, fill="#e7eaee", stroke=INK, sw=2, rx=3))  # труба
    parts.append(line(cx - 60, 161, cx + 60, 161, color=NEG, sw=2, dash="4,4"))        # потік
    parts.append(circle(cx, 137, 10, fill="#dfe4ea", stroke=INK, sw=2))                # плунжер/затвор
    parts.append(line(cx, 110, cx, 127, color=INK, sw=4))                              # шток
    parts.append(text(cx + 16, 130, "сідло", size=12, color=MUTED, anchor="start"))
    parts.append(text(cx, 210, "пропустити чи\nперекрити потік", size=12, color=MUTED))

    # --- спільне коло керування знизу ---
    by = 320
    parts.append(line(40, by - 26, W - 40, by - 26, color="#d0d5dd", sw=1.5))
    parts.append(text(W / 2, by - 36, "Спільне коло керування для всіх трьох", size=14, bold=True))

    mcu = fitbox(60, by, 150, 56, "вивід МК\n3.3 В", size=13, bold=True, fill=FILL, stroke=INK)
    key = fitbox(330, by, 150, 56, "ключ-драйвер", size=13, bold=True, fill=FILL, stroke=INK)
    parts.append(mcu)
    parts.append(key)
    parts.append(arrow(212, by + 28, 328, by + 28, color=INK, sw=2.2))
    parts.append(text(270, by + 18, "керує", size=12, color=MUTED))

    # котушка праворуч від ключа
    coilx = 600
    for i in range(5):
        parts.append('<ellipse cx="%.1f" cy="%.1f" rx="10" ry="20" fill="none" '
                     'stroke="%s" stroke-width="3"/>' % (coilx + i * 16, by + 28, INK))
    parts.append(text(coilx + 32, by - 6, "котушка", size=12, color=MUTED))

    # живлення котушки + ключ нижче
    parts.append(line(480, by + 28, 590, by + 28, color=INK, sw=2.2))
    parts.append(line(coilx + 72, by + 28, 760, by + 28, color=INK, sw=2.2))
    parts.append(plus(770, by + 10))
    parts.append(text(786, by + 14, "Vlive (5/12/24 В)", size=12, color=POS, anchor="start"))

    # гасний діод паралельно котушці (від кінця до кінця котушки)
    dy = by + 90
    dL, dR = 590, coilx + 72
    parts.append(line(dL, by + 48, dL, dy, color=NEG, sw=2))
    parts.append(line(dR, by + 48, dR, dy, color=NEG, sw=2))
    parts.append(line(dL, dy, dR, dy, color=NEG, sw=2))
    # символ діода (трикутник + риска) посередині
    midx = (dL + dR) / 2
    parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
                 'stroke="%s" stroke-width="2"/>' % (midx - 10, dy - 9, midx - 10, dy + 9, midx + 6, dy, NEG))
    parts.append(line(midx + 6, dy - 9, midx + 6, dy + 9, color=NEG, sw=2))
    parts.append(text(midx, dy + 26, "гасний діод", size=12, color=NEG, bold=True))

    return render("img/three.svg", W, H, *parts,
                  title="Один механізм — три застосунки")


if __name__ == "__main__":
    fig_core()
    fig_three()
    print("OK: core.svg, three.svg")
