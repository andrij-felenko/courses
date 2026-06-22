# -*- coding: utf-8 -*-
"""Фігури до теми «Живлення з USB» (кут МК-розробника: скільки можна взяти й як).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Бюджет струму в часі: межі до/після конфігурації ─────────────────────
def fig_current_budget():
    W, H = 860, 470
    f = [text(W / 2, 30, "Скільки можна взяти з VBUS: межа змінюється з фазою", size=16, bold=True)]

    ax, ay0, ay1 = 80, 360, 80          # вісь x на ay0; верх графіка ay1
    axr = 780
    f.append(arrow(ax, ay0, axr + 10, ay0, color=INK, sw=2))
    f.append(text(axr + 24, ay0 + 5, "час", size=12, color=MUTED, anchor="start"))
    f.append(arrow(ax, ay0, ax, ay1 - 12, color=INK, sw=2))
    f.append(text(ax - 6, ay1 - 18, "струм", size=12, color=MUTED, anchor="end"))

    def yfor(ma):
        return ay0 - (ay0 - ay1) * (ma / 900.0)

    for ma, lab in [(100, "100 мА"), (500, "500 мА"), (900, "900 мА")]:
        yy = yfor(ma)
        f.append(line(ax - 5, yy, ax + 5, yy, color=MUTED, sw=1))
        f.append(text(ax - 9, yy + 4, lab, size=11, color=MUTED, anchor="end"))
        f.append(line(ax, yy, axr, yy, color=MUTED, sw=0.8, dash="3,4"))

    setx = 380
    f.append(line(setx, ay1, setx, ay0, color=MUTED, sw=1, dash="4,3"))
    f.append(text(setx, ay0 + 18, "SET_CONFIGURATION", size=11, color=MUTED))

    # сходинка стелі: до конфігурації 100, після — 500 (USB 2.0)
    capy0, capy1 = yfor(100), yfor(500)
    f.append(line(ax, capy0, setx, capy0, color=POS, sw=3.5))
    f.append(line(setx, capy0, setx, capy1, color=POS, sw=3.5))
    f.append(line(setx, capy1, axr, capy1, color=POS, sw=3.5))
    f.append(text((ax + setx) / 2, capy0 - 12, "стеля: 1 unit load", size=11, color=POS, bold=True))
    f.append(text((setx + axr) / 2, capy1 - 12, "стеля: bMaxPower (до 500 мА, USB 2.0)",
                  size=11, color=POS, bold=True))
    # пунктир: стеля USB 3 — 900 мА
    f.append(line(setx, yfor(900), axr, yfor(900), color=NEG, sw=1.6, dash="6,4"))
    f.append(text(axr - 4, yfor(900) - 8, "USB 3: до 900 мА", size=10, color=NEG, anchor="end"))

    # реальний профіль ESP32: сон ~20 мА, сплески Wi-Fi ~250 мА
    prof = [(ax, 20), (160, 20), (172, 250), (196, 250), (210, 30), (300, 30),
            (setx, 30), (450, 30), (462, 250), (492, 250), (510, 40),
            (630, 40), (645, 250), (672, 250), (690, 40), (axr, 40)]
    pts = " ".join("%.1f,%.1f" % (x, yfor(ma)) for x, ma in prof)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, FIELD))
    f.append(text(280, yfor(250) + 22, "ESP32: сон ~20 мА, сплеск Wi-Fi ~250 мА",
                  size=11, color=FIELD, bold=True))

    # небезпечна зона: сплеск до конфігурації пробиває стелю 100 мА
    f.append(circle(184, yfor(250), 14, fill="none", stroke=POS, sw=2))
    f.append(mtext(184, yfor(250) - 26, ["сплеск > 100 мА", "до конфігурації"],
                   size=10, color=POS, bold=True))

    f.append(fitbox(60, 410, 740, 46,
                    "Поки хост не дав SET_CONFIGURATION, стеля — один unit load. "
                    "Важкий старт (Wi-Fi) у цій фазі пробиває її → хост зріже порт.",
                    size=12, fill="#fef9ec", stroke=POS))
    return render(os.path.join(IMG, "current-budget.svg"), W, H, *f)


# ── 2. Тракт живлення VBUS 5 В → LDO → 3,3 В: де ховається brownout ─────────
def fig_vbus_ldo_chip():
    W, H = 860, 430
    f = [text(W / 2, 30, "Тракт живлення: 5 В шини стають 3,3 В чипа", size=16, bold=True)]

    y = 110
    bh = 74
    # ланцюг блоків
    boxes = [
        (60,  150, "Роз'єм\nVBUS 5 В", FILL, LINE),
        (250, 150, "Кабель + роз'єм\n(опір → просадка)", "#fef9ec", POS),
        (470, 130, "LDO\n5 В → 3,3 В", "#eaf0fd", NEG),
        (650, 150, "ESP32\n3,3 В", "#e8f6ee", FIELD),
    ]
    cxs = []
    for x, w, label, fill, stroke in boxes:
        f.append(rect(x, y, w, bh, fill=fill, stroke=stroke, sw=2))
        f.append(mtext(x + w / 2, y + 30, label.split("\n"), size=13, bold=True))
        cxs.append((x, w))
    # стрілки між блоками
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][1]
        x2 = boxes[i + 1][0]
        f.append(arrow(x1, y + bh / 2, x2, y + bh / 2, color=LINE, sw=2))

    # великий конденсатор на вході (inrush)
    capx = boxes[2][0] - 22
    f.append(line(capx, y + bh, capx, y + bh + 34, color=INK, sw=2))
    f.append(line(capx - 14, y + bh + 34, capx + 14, y + bh + 34, color=INK, sw=2.5))
    f.append(line(capx - 14, y + bh + 42, capx + 14, y + bh + 42, color=INK, sw=2.5))
    f.append(line(capx, y + bh + 42, capx, y + bh + 56, color=INK, sw=2))
    f.append(text(capx, y + bh + 74, "вхідний C\n(inrush при втиканні)".split("\n")[0],
                  size=10, color=MUTED))
    f.append(text(capx, y + bh + 88, "(inrush при втиканні)", size=10, color=MUTED))

    # позначка точки brownout перед LDO
    bx = boxes[2][0] - 6
    f.append(circle(bx, y + bh / 2, 7, fill="none", stroke=POS, sw=2.2))
    f.append(mtext(bx, y - 14, ["якщо Vin LDO просяде нижче", "мінімуму → brownout-reset"],
                   size=10, color=POS, bold=True))

    # формула просадки
    f.append(fitbox(60, 300, 740, 46,
                    "Просадка = I × R_кабелю.  Сплеск Wi-Fi 250 мА на 0,5 Ом тонкого кабелю "
                    "знімає ~0,13 В; додай inrush — і Vin LDO черкає мінімум.",
                    size=12, fill="#f4f6f8", stroke=MUTED))
    f.append(fitbox(60, 356, 740, 40,
                    "Лікування: товщий/коротший кабель, більший вхідний C, нижчий dropout LDO, "
                    "або зовнішнє живлення (self-powered).",
                    size=12, fill="#e8f6ee", stroke=FIELD))
    return render(os.path.join(IMG, "vbus-ldo-chip.svg"), W, H, *f)


if __name__ == "__main__":
    fig_current_budget()
    fig_vbus_ldo_chip()
    print("figs.py: записано 2 SVG у", IMG)
