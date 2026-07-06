# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія тактики — стимул → елемент із рішенням → виміряна відповідь ──
def fig_anatomy():
    W, H = 760, 300
    p = []
    # ліворуч — стимул
    b1, w1, h1 = textbox(115, 150, ["Стимул", "запит приходить,", "коли база лежить"], size=13, pad=12)
    p.append(b1)
    # центр — елемент, у якому ухвалено ОДНЕ рішення
    ex, ey, ew, eh = 300, 95, 170, 110
    p.append(rect(ex, ey, ew, eh, fill="#eef7ff", stroke=NEG, sw=2))
    p.append(text(ex + ew / 2, ey + 24, "Елемент системи", size=13, bold=True))
    p.append(line(ex + 14, ey + 36, ex + ew - 14, ey + 36, color=MUTED, sw=1))
    p.append(mtext(ex + ew / 2, ey + 58, ["одне рішення:", "«поверни кеш,", "не чекай базу»"], size=12, color=NEG))
    # тактика — це саме ця «начинка» елемента
    p.append(text(ex + ew / 2, ey + eh + 26, "= ТАКТИКА", size=14, bold=True, color=POS))
    # праворуч — виміряна відповідь
    b3, w3, h3 = textbox(650, 150, ["Відповідь", "(вимірна)", "", "< 200 мс", "замість збою"], size=13, pad=12, stroke=FIELD, sw=2)
    p.append(b3)
    # стрілки
    p.append(arrow(115 + w1 / 2, 150, ex - 6, 150))
    p.append(arrow(ex + ew + 6, 150, 650 - w3 / 2 - 6, 150))
    render(os.path.join(OUT, 'anatomy.svg'), W, H, *p,
           title="Тактика — одне рішення, що перетворює стимул на вимірну відповідь")


# ── Фігура 2: одна турбота (доступність) фанає у сім'ї атомарних тактик ──
def fig_menu():
    W, H = 820, 430
    p = []
    # корінь — якісний атрибут
    root, rw, rh = textbox(410, 60, "Турбота: ДОСТУПНІСТЬ", size=15, pad=14, bold=True, fill="#eef7ff", stroke=NEG, sw=2)
    p.append(root)

    fams = [
        (150, "Виявити збій", ["ping/echo", "heartbeat", "таймаут", "монітор"]),
        (410, "Оговтатись", ["retry", "перемкнути", "на резерв", "відкотити стан"]),
        (670, "Не допустити", ["зняти з ротації", "обмежити доступ", "транзакція"]),
    ]
    fy = 175
    for fx, fname, tactics in fams:
        fb, fw, fh = textbox(fx, fy, fname, size=13, pad=11, bold=True, fill="#f0f0f0")
        p.append(fb)
        p.append(arrow(410, 60 + rh / 2, fx, fy - fh / 2 - 4))
        # меню атомарних тактик під сім'єю
        ty = fy + fh / 2 + 40
        for t in tactics:
            tb, tw, th = textbox(fx, ty, t, size=12, pad=8, stroke=POS, min_w=150)
            p.append(tb)
            ty += th + 12
    render(os.path.join(OUT, 'menu.svg'), W, H, *p,
           title="Атрибут → сім'ї тактик → меню атомарних рішень")


# ── Фігура 3: патерн = зібраний пакет тактик із зафіксованим компромісом ──
def fig_pattern():
    W, H = 780, 360
    p = []
    # велика рамка патерна
    px, py, pw, ph = 60, 70, 660, 220
    p.append(rect(px, py, pw, ph, fill="#f7f7f7", stroke=INK, sw=2.2))
    p.append(text(px + pw / 2, py + 30, "ПАТЕРН: «запобіжник» (circuit breaker)", size=15, bold=True))
    p.append(text(px + pw / 2, py + 52, "компроміс уже зашитий усередині — ти береш пакет цілком", size=12, color=MUTED, italic=True))

    cells = [
        ("виявити", ["таймаут на", "виклик"]),
        ("не допустити", ["полічити збої,", "розімкнути"]),
        ("оговтатись", ["пробний запит,", "замкнути назад"]),
    ]
    cw, gap = 190, 20
    total = len(cells) * cw + (len(cells) - 1) * gap
    x0 = px + (pw - total) / 2
    cy = py + 145
    for i, (fam, body) in enumerate(cells):
        cx = x0 + i * (cw + gap)
        p.append(rect(cx, cy - 45, cw, 90, fill="#eef7ff", stroke=POS, sw=1.8))
        p.append(text(cx + cw / 2, cy - 24, "тактика: " + fam, size=12, bold=True, color=POS))
        p.append(mtext(cx + cw / 2, cy + 2, body, size=12))
    render(os.path.join(OUT, 'pattern.svg'), W, H, *p,
           title="Патерн — готовий пакет із кількох тактик")


fig_anatomy()
fig_menu()
fig_pattern()
print("figs done")
