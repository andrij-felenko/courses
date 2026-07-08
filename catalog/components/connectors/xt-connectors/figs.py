# -*- coding: utf-8 -*-
"""Фігури до статті «Родина силових роз'ємів XT (AMASS: XT30/60/90/120)».
Вивід — ./img/*.svg. Запуск: python figs.py  (швидко, без залежностей)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GOLD   = "#d4a017"     # позолочений контакт
GOLD_D = "#a67c00"     # темніша кромка золота
NYLON  = "#e6e2d8"     # світлий нейлон корпусу
NYLON_D= "#b8b2a0"     # кромка нейлону
COPPER = "#b5651d"     # мідна жила
POSRED = "#c0392b"
NEGBLU = "#2457d6"


# ── Фігура 1: устрій пари XT — корпус, кулькові контакти, чашка під пайку, ключ
def fig_anatomy():
    W, H = 780, 470
    p = []

    # -- верх: пара в розрізі, «тато» ліворуч заходить у «маму» праворуч --
    y = 120
    p.append(text(W/2, 34, "Пара XT у розрізі: два кулькові контакти + ключ форми", size=15, bold=True))

    # МАМА (female) праворуч — приймає, з чашками під дріт назад
    fx = 470
    # корпус мами: скошений кут згори (ключ), рівний знизу
    fh_top, fh_bot = 108, 108
    # намалюємо трапецію-корпус як polygon: скіс лише зверху
    fbody = ('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d" '
             'fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        fx, y-54,            # ліво-верх (вхід)
        fx+150, y-54,        # право-верх
        fx+150, y+54,        # право-низ
        fx, y+54,            # ліво-низ
        fx-22, y+30,         # скіс: ліво-низ виступ (ключ-паз внизу зрізаний)
        NYLON, NYLON_D))
    # простіше й чистіше: прямокутник зі зрізаним НИЖНІМ-ЛІВИМ кутом як ключ
    fbody = ('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        fx,      y-54,
        fx+150,  y-54,
        fx+150,  y+54,
        fx+26,   y+54,
        fx,      y+28,
        NYLON, NYLON_D))
    p.append(fbody)
    # два жіночі гнізда (заглиблені золоті втулки з отвором)
    for yy in (y-24, y+24):
        p.append(rect(fx+6, yy-11, 26, 22, fill="#7a5c10", stroke=GOLD_D, sw=1.4, rx=3))
        p.append(circle(fx+19, yy, 6.5, fill="#3d2f08", stroke=GOLD, sw=2))
    # чашки під пайку ззаду мами + дроти
    for yy, col in ((y-24, POSRED), (y+24, NEGBLU)):
        p.append(rect(fx+150, yy-9, 20, 18, fill=GOLD, stroke=GOLD_D, sw=1.4, rx=3))   # solder cup
        p.append(rect(fx+170, yy-6, 74, 12, fill=col, stroke=None, sw=0, rx=6))         # ізоляція дроту
        # мідна жила в чашці
        for k in range(3):
            p.append(line(fx+152, yy-4+k*4, fx+168, yy-4+k*4, color=COPPER, sw=1.4))

    # ТАТО (male) ліворуч — суцільні кулькові штирі, що заходять у мами
    mx = 300
    mbody = ('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        mx-150,  y-54,
        mx,      y-54,
        mx,      y+28,
        mx-26,   y+54,
        mx-150,  y+54,
        NYLON, NYLON_D))
    p.append(mbody)
    # два штирі-кульки, що виступають праворуч до мами
    for yy in (y-24, y+24):
        p.append(rect(mx, yy-6.5, 44, 13, fill=GOLD, stroke=GOLD_D, sw=1.4, rx=6))   # тіло штиря
        p.append(circle(mx+44, yy, 6.5, fill=GOLD, stroke=GOLD_D, sw=1.6))            # заокруглений носик
    # чашки під пайку ззаду тата + дроти
    for yy, col in ((y-24, POSRED), (y+24, NEGBLU)):
        p.append(rect(mx-170, yy-9, 20, 18, fill=GOLD, stroke=GOLD_D, sw=1.4, rx=3))
        p.append(rect(mx-244, yy-6, 74, 12, fill=col, stroke=None, sw=0, rx=6))
        for k in range(3):
            p.append(line(mx-168, yy-4+k*4, mx-152, yy-4+k*4, color=COPPER, sw=1.4))

    # знаки полярності біля контактів (на тілі тата)
    p.append(text(mx-92, y-24+5, "+", size=20, color=POSRED, bold=True))
    p.append(text(mx-92, y+24+6, "−", size=22, color=NEGBLU, bold=True))

    # підписи-виноски (поза корпусами, з запасом)
    p.append(text(mx-207, y-58, "чашка під пайку", size=11.5, color=MUTED, anchor="middle"))
    p.append(text(mx-207, y+74, "дроти + / −", size=11.5, color=MUTED, anchor="middle"))
    p.append(text(mx+22, y-66, "штир-кулька (тато)", size=11.5, color=MUTED, anchor="start"))
    p.append(text(fx+8, y-66, "гніздо-втулка (мама)", size=11.5, color=MUTED, anchor="start"))
    # стрілка «заходить»
    p.append(arrow(mx+58, y, fx-4, y, color=INK, sw=2))

    # виноска на ключ (зрізаний кут)
    p.append(line(mx-13, y+41, mx-13, y+92, color=NYLON_D, sw=1.2, dash="4 3"))
    b,_,_ = textbox(mx+30, y+108, "зрізаний кут — «ключ» форми:\nпара сходиться лише правильним боком",
                    size=11, pad=8, fill="#f4f6f8", stroke=NYLON_D, sw=1.4)
    p.append(b)

    render(os.path.join(OUT, 'anatomy.svg'), W, H, *p)


# ── Фігура 2: родина за зростанням — розмір, кулька, струм, дріт ────────────
def fig_family():
    W, H = 860, 430
    p = []
    p.append(text(W/2, 32, "Родина XT: більший струм — товща кулька, грубший дріт", size=15, bold=True))

    # чотири члени; висота стовпчика умовно ~ фізичному розміру корпусу
    members = [
        # (назва, відносна_ширина_корпусу, підпис_кульки, тривалий_струм, пік, дріт, колір)
        ("XT30",  46,  "кулька 2.0 мм",  "≈ 15 А", "30 А",  "16 AWG", FIELD),
        ("XT60",  64,  "кулька 3.5 мм",  "≈ 30 А", "60 А",  "12 AWG", "#0f8a8a"),
        ("XT90",  86,  "кулька 4.5 мм",  "≈ 45 А", "90 А",  "10 AWG", "#7a5cd6"),
        ("XT120", 104, "кулька 5.5 мм",  "≈ 60 А", "120 А", "8 AWG",  POSRED),
    ]
    n = len(members)
    base_y = 300                      # спільна лінія «стола», на якій стоять корпуси
    x0 = 70
    slot = (W - 120) / n
    p.append(line(x0-10, base_y, W-40, base_y, color="#d0d0d0", sw=1.5))

    for i, (name, bw, ball, cont, peak, awg, col) in enumerate(members):
        cx = x0 + slot*i + slot/2
        bh = 44 + bw*0.55            # трохи вища при ширшому — умовний ріст габариту
        bx = cx - bw/2
        by = base_y - bh
        # корпус (нейлон) із двома золотими кульками
        p.append(rect(bx, by, bw, bh, fill=NYLON, stroke=NYLON_D, sw=1.6, rx=6))
        # дві кульки-контакти; діаметр росте з номером
        ball_d = 8 + i*3
        for dx in (-bw*0.22, bw*0.22):
            p.append(circle(cx+dx, by+bh-16, ball_d/2, fill=GOLD, stroke=GOLD_D, sw=1.6))
        # назва — над корпусом, у рамці кольору члена
        b,_,_ = textbox(cx, by-20, name, size=15, bold=True, pad=8,
                        fill="#ffffff", stroke=col, sw=2.2)
        p.append(b)
        # характеристики — під лінією стола, вертикальним стосом, рознесені
        rows = [ball, "тривало " + cont, "пік " + peak, "дріт " + awg]
        for j, r in enumerate(rows):
            p.append(text(cx, base_y + 26 + j*22, r, size=12.5,
                          color=INK if j == 0 else MUTED, anchor="middle"))

    render(os.path.join(OUT, 'family.svg'), W, H, *p)


if __name__ == '__main__':
    fig_anatomy()
    fig_family()
    print("OK: anatomy.svg, family.svg")
