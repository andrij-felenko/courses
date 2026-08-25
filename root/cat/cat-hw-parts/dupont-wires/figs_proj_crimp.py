# -*- coding: utf-8 -*-
"""Фігури до вставки «proj-crimp-dupont» (обтиск Dupont-контакту).
Окремий генератор у теці теми (щоб не заважати паралельному figs.py);
імпортує svgkit, вивід — ./img/*.svg. Запуск: python figs_proj_crimp.py (швидко)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

METAL = "#9aa3ad"
METAL_D = "#6b7480"
STRAND = "#d4a017"     # мідна жила
STRAND_D = "#8a6d0b"
INSUL = "#27ae60"


# ── Фігура 1: розкладка дроту в контакті + торець доброго/поганого обтиску ──
def fig_crimp_layout():
    W, H = 780, 470
    p = []

    # ── СЦЕНА 1: розкладка збоку (контакт іще розкритий) ───────────────────
    p.append(text(210, 40, "Що куди лягає (контакт іще розкритий)", size=13.5, bold=True, anchor="middle"))

    yb = 150
    # тіло контакту-жолоба
    p.append(rect(150, yb - 10, 205, 20, fill=METAL, stroke=METAL_D, sw=1.6, rx=3))
    # контактна частина спереду
    p.append(rect(335, yb - 8, 44, 16, fill=METAL_D, stroke=METAL_D, sw=1, rx=2))
    p.append(text(357, yb - 20, "контактна", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(357, yb - 8, "частина", size=10.5, color=MUTED, anchor="middle"))

    # пара лапок на ЖИЛУ
    for lx in (246, 264):
        p.append(line(lx, yb - 10, lx - 5, yb - 30, color=METAL_D, sw=2.4))
        p.append(line(lx, yb + 10, lx - 5, yb + 30, color=METAL_D, sw=2.4))
    # пара лапок на ІЗОЛЯЦІЮ
    for lx in (306, 324):
        p.append(line(lx, yb - 10, lx + 5, yb - 30, color=METAL_D, sw=2.4))
        p.append(line(lx, yb + 10, lx + 5, yb + 30, color=METAL_D, sw=2.4))

    # дріт: ізоляція + оголені жилки
    p.append(rect(40, yb - 9, 116, 18, fill=INSUL, stroke="#1e7a44", sw=1.2, rx=5))
    for k in range(5):
        yy = yb - 6 + k * 3
        p.append(line(156, yy, 258, yy, color=STRAND, sw=1.6))

    # підписи зон (з великим запасом, поза лапками)
    p.append(text(255, yb + 60, "лапки на ЖИЛУ", size=11.5, bold=True, color=INK, anchor="middle"))
    p.append(text(255, yb + 76, "тиснуть у голий метал", size=10.5, color=MUTED, anchor="middle"))
    p.append(text(315, yb + 96, "лапки на ІЗОЛЯЦІЮ", size=11.5, bold=True, color=INK, anchor="middle"))
    p.append(text(315, yb + 112, "тримають за оболонку", size=10.5, color=MUTED, anchor="middle"))

    # мірка «зачистити ~3–4 мм» — над оголеними жилками
    my = yb - 42
    p.append(line(156, my, 258, my, color=POS, sw=1.4))
    p.append(line(156, my - 4, 156, my + 4, color=POS, sw=1.4))
    p.append(line(258, my - 4, 258, my + 4, color=POS, sw=1.4))
    p.append(text(207, my - 8, "зачистити ~3–4 мм", size=11, bold=True, color=POS, anchor="middle"))

    # ── СЦЕНА 2: торець доброго обтиску ────────────────────────────────────
    cx2 = 620
    gy = 150
    p.append(text(cx2, 40, "Торець доброго обтиску", size=13.5, bold=True, anchor="middle"))

    # дві щоки, загорнуті всередину (B-crimp)
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx2 - 42, gy + 34, cx2, gy - 40, cx2, gy + 6, METAL))
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx2 + 42, gy + 34, cx2, gy - 40, cx2, gy + 6, METAL))
    # дно жолоба
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx2 - 42, gy + 34, cx2, gy + 62, cx2 + 42, gy + 34, METAL_D))
    # жили — щільний пучок усередині
    for i in range(7):
        ang = -math.pi / 2 + (i - 3) * 0.34
        rr = 14
        p.append(circle(cx2 + rr * math.cos(ang) * 0.75, gy + 14 + rr * math.sin(ang) * 0.5, 4.0,
                        fill=STRAND, stroke=STRAND_D, sw=1))
    p.append(text(cx2, gy + 84, "щоки загорнуті ВСЕРЕДИНУ,", size=11, bold=True, color=INK, anchor="middle"))
    p.append(text(cx2, gy + 100, "жили в щільному пучку", size=10.5, color=MUTED, anchor="middle"))

    # ── СЦЕНА 3: торець поганого обтиску (недотиск) ────────────────────────
    by = 330
    p.append(text(cx2, by - 46, "Торець поганого обтиску", size=13.5, bold=True, color="#c0392b", anchor="middle"))
    # щоки лишились розчепірені — не зімкнулись
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="#c94b4b" stroke-width="2.6"/>'
             % (cx2 - 42, by + 20, cx2 - 14, by - 26, cx2 - 6, by - 30))
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="#c94b4b" stroke-width="2.6"/>'
             % (cx2 + 42, by + 20, cx2 + 14, by - 26, cx2 + 6, by - 30))
    p.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="#c94b4b" stroke-width="2.6"/>'
             % (cx2 - 42, by + 20, cx2, by + 40, cx2 + 42, by + 20))
    for i in range(4):
        p.append(circle(cx2 - 10 + i * 7, by + 2, 3, fill=STRAND, stroke=STRAND_D, sw=0.8))
    p.append(text(cx2, by + 62, "щоки не зімкнулись —", size=10.5, bold=True, color="#c0392b", anchor="middle"))
    p.append(text(cx2, by + 77, "жила висмикнеться", size=10, color="#c0392b", anchor="middle"))

    render(os.path.join(OUT, 'crimp-layout.svg'), W, H, *p)


# ── Фігура 2: контакт у корпусі — фіксатор клацнув / вихід голкою ───────────
def fig_housing_lock():
    W, H = 740, 340
    p = []

    def scene(ox, oy, needle, label):
        s = []
        # стінки корпусу (розріз)
        s.append(rect(ox, oy, 232, 66, fill="#eceff3", stroke="#3a3f45", sw=1.8, rx=6))
        # передня стінка з отвором
        s.append(rect(ox + 212, oy + 6, 20, 54, fill="#d5d9df", stroke="#3a3f45", sw=1.4, rx=3))
        # контакт: жолоб + боксове плече
        s.append(rect(ox + 28, oy + 24, 146, 18, fill=METAL, stroke=METAL_D, sw=1.5, rx=3))
        s.append(rect(ox + 148, oy + 18, 12, 30, fill=METAL_D, stroke=METAL_D, sw=1, rx=2))
        # штир у отвір
        s.append(rect(ox + 174, oy + 30, 44, 6, fill=METAL, stroke=METAL_D, sw=1, rx=2))
        # дріт іззаду
        s.append(rect(ox - 30, oy + 27, 58, 12, fill=POS, stroke="#8a2a20", sw=1, rx=4))

        if not needle:
            # язичок клацнув униз за плече
            s.append('<path d="M %.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="3"/>'
                     % (ox + 118, oy + 2, ox + 148, oy + 20, NEG))
            s.append(text(ox + 92, oy - 8, "язичок за плечем", size=11, bold=True, color=NEG, anchor="middle"))
            s.append(text(ox + 116, oy + 88, "назад не витягнути", size=10.5, color=MUTED, anchor="middle"))
        else:
            # язичок віджато вгору голкою
            s.append('<path d="M %.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="3"/>'
                     % (ox + 118, oy + 2, ox + 148, oy + 8, FIELD))
            s.append(line(ox + 148, oy - 26, ox + 147, oy + 8, color=INK, sw=2.4))
            s.append('<path d="M %.0f %.0f l -3 -8 l 6 0 z" fill="%s"/>' % (ox + 147, oy + 8, INK))
            s.append(text(ox + 148, oy - 34, "голка", size=10.5, color=INK, anchor="middle"))
            s.append(arrow(ox - 2, oy + 33, ox - 34, oy + 33, color=FIELD, sw=2.4))
            s.append(text(ox + 96, oy + 88, "віджав → контакт виходить", size=10.5, color=FIELD, anchor="middle"))
        s.append(text(ox + 100, oy + 108, label, size=12, bold=True, anchor="middle"))
        return "".join(s)

    p.append(scene(70, 66, False, "Зафіксовано (клац)"))
    p.append(scene(440, 66, True, "Вихід контакту голкою"))
    render(os.path.join(OUT, 'housing-lock.svg'), W, H, *p)


if __name__ == '__main__':
    fig_crimp_layout()
    fig_housing_lock()
    print("OK: crimp-layout.svg, housing-lock.svg")
