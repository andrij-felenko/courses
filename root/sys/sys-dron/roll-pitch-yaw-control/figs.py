# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Керування крен-тангаж-нишпорення».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: три осі обертання апарата ──────────────────────────────────────
# Головна ідея: будь-який нахил/поворот апарата розкладається на три
# незалежні обертання навколо трьох осей тіла. Показуємо корпус (дрон зверху-
# збоку), три осі крізь центр мас і дугу-обертання навколо кожної з підписом.
def fig_three_axes():
    W, H = 940, 470
    P = []
    cx, cy = W / 2, 250

    # центр мас
    P.append(circle(cx, cy, 5, fill=INK, stroke=INK))
    P.append(text(cx, cy + 26, "центр мас", size=12, color=MUTED))

    # вісь X (поздовжня, ніс↔хвіст) — крен (roll)
    P.append(line(cx - 250, cy, cx + 250, cy, color=POS, sw=2.5))
    P.append(arrow(cx + 200, cy, cx + 260, cy, color=POS, sw=2.5))
    P.append(text(cx + 250, cy - 12, "X (ніс)", size=13, color=POS, bold=True))
    # дуга крену навколо X
    P.append('<path d="M %.0f %.0f A 60 60 0 1 1 %.0f %.0f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + 100, cy - 58, cx + 100 - 2, cy - 58, POS))
    box, bw, bh = textbox(cx + 100, cy - 105, "КРЕН (roll)\nнахил на бік", size=12, color=POS, fill="#fdecea", stroke=POS)
    P.append(box)

    # вісь Y (поперечна, крило↔крило) — тангаж (pitch)
    P.append(line(cx, cy + 150, cx, cy - 150, color=NEG, sw=2.5))
    P.append(arrow(cx, cy - 110, cx, cy - 170, color=NEG, sw=2.5))
    P.append(text(cx - 64, cy - 150, "Y (крило)", size=13, color=NEG, bold=True))
    box, bw, bh = textbox(cx - 250, cy - 60, "ТАНГАЖ (pitch)\nніс угору/вниз", size=12, color=NEG, fill="#eaf0fd", stroke=NEG)
    P.append(box)

    # вісь Z (вертикальна) — нишпорення (yaw) — рисуємо як «вглиб» косою лінією
    P.append(line(cx, cy, cx - 150, cy + 110, color=FIELD, sw=2.5))
    P.append(arrow(cx - 120, cy + 88, cx - 156, cy + 114, color=FIELD, sw=2.5))
    P.append(text(cx - 150, cy + 132, "Z (вниз)", size=13, color=FIELD, bold=True))
    box, bw, bh = textbox(cx + 250, cy + 70, "НИШПОРЕННЯ (yaw)\nповорот курсу", size=12, color=FIELD, fill="#e9f7ef", stroke=FIELD)
    P.append(box)

    return render("img/three-axes.svg", W, H, *P,
                  title="Три осі обертання апарата — три незалежні кути")


# ── Фігура 2: один контур — від похибки кута до команди мікшеру ───────────────
# Головна ідея: кожна вісь — це замкнений контур. Завдання − вимір = похибка
# кута → ПІД → команда осі → мікшер → мотори → апарат обертається → IMU міряє →
# назад. Показуємо ланцюг блоками зі стрілками й вузлом віднімання.
def fig_one_loop():
    W, H = 960, 360
    P = []
    y = 150
    # вузол суматора (завдання − вимір)
    P.append(circle(120, y, 22, fill=BG, stroke=INK, sw=2))
    P.append(text(120, y + 6, "−", size=22, color=NEG, bold=True))
    P.append(arrow(20, y, 96, y, color=INK))
    P.append(text(58, y - 12, "завдання", size=12, color=MUTED))
    P.append(text(58, y + 22, "(бажаний кут)", size=11, color=MUTED))

    # блоки ланцюга
    def blk(x, w, label, col, fill):
        P.append(fitbox(x, y - 32, w, 64, label, size=13, color=col, fill=fill, stroke=col, sw=2))
        return x + w

    nx = 175
    nx = blk(nx, 130, "ПІД осі\n(один контур)", POS, "#fdecea") + 35
    P.append(arrow(305, y, 345, y, color=INK))
    nx = blk(345, 130, "МІКШЕР\nрозподіл по моторах", NEG, "#eaf0fd") + 35
    P.append(arrow(475, y, 515, y, color=INK))
    nx = blk(515, 120, "мотори\n+ гвинти", INK, FILL) + 35
    P.append(arrow(635, y, 675, y, color=INK))
    nx = blk(675, 130, "апарат\nобертається", FIELD, "#e9f7ef")

    # зворотний зв'язок через IMU
    P.append(line(740, y + 32, 740, y + 95, color=MUTED, sw=2))
    P.append(line(740, y + 95, 120, y + 95, color=MUTED, sw=2))
    P.append(arrow(120, y + 95, 120, y + 22, color=MUTED, sw=2))
    box, bw, bh = textbox(430, y + 95, "IMU міряє фактичний кут (зворотний зв'язок)", size=12, color=MUTED, fill="#f4f6f8", stroke=MUTED)
    P.append(box)

    # підпис над суматором
    P.append(text(120, y - 40, "похибка кута e", size=12, color=INK, bold=True))
    P.append(arrow(120, y - 30, 158, y - 6, color=INK, sw=1.4))

    return render("img/one-loop.svg", W, H, *P,
                  title="Один контур осі: похибка кута → ПІД → мікшер → мотори → назад")


# ── Фігура 3: три контури → один мікшер, і зв'язок між осями ──────────────────
# Головна ідея: три ОКРЕМІ ПІД (по осі) дають три незалежні команди, але всі
# три зливаються в ОДНОМУ мікшері на спільні мотори — звідси перехресний
# вплив осей. Показуємо три контури зліва, мікшер у центрі, мотори справа.
def fig_three_loops():
    W, H = 940, 470
    P = []
    # три ПІД-контури
    rows = [
        ("ПІД крену",  "крен",        POS,   "#fdecea", 90),
        ("ПІД тангажу","тангаж",      NEG,   "#eaf0fd", 235),
        ("ПІД курсу",  "нишпорення",  FIELD, "#e9f7ef", 380),
    ]
    for label, axis, col, fill, yy in rows:
        P.append(fitbox(60, yy - 30, 150, 60, label, size=13, color=col, fill=fill, stroke=col, sw=2))
        P.append(text(135, yy - 42, "похибка %s" % axis, size=11, color=MUTED))
        P.append(arrow(210, yy, 360, yy, color=col, sw=2))
        P.append(text(285, yy - 10, "команда", size=11, color=col))

    # мікшер (центральний блок)
    mx, mw = 360, 170
    P.append(rect(mx, 70, mw, 320, fill="#fff7e6", stroke="#b8860b", sw=2.5, rx=10))
    P.append(mtext(mx + mw / 2, 150, "МІКШЕР", size=16, color="#8a6d00", bold=True))
    P.append(mtext(mx + mw / 2, 210, "складає три\nкоманди в тягу\nкожного мотора", size=12, color=INK))
    P.append(mtext(mx + mw / 2, 310, "M = база\n± крен\n± тангаж\n± курс", size=11.5, color=MUTED))

    # мотори
    motors = [("M1", 110), ("M2", 200), ("M3", 290), ("M4", 360)]
    for name, yy in motors:
        P.append(arrow(mx + mw, 230, 660, yy, color=MUTED, sw=1.6))
        P.append(circle(700, yy, 26, fill=FILL, stroke=INK, sw=2))
        P.append(text(700, yy + 5, name, size=13, color=INK, bold=True))

    # підпис-зв'язок осей
    box, bw, bh = textbox(W - 130, 430, "один мотор служить усім трьом осям →\nосі зв'язані через спільні мотори",
                          size=11.5, color="#8a6d00", fill="#fff7e6", stroke="#b8860b")
    P.append(box)

    return render("img/three-loops.svg", W, H, *P,
                  title="Три окремі ПІД зливаються в одному мікшері на спільні мотори")


if __name__ == "__main__":
    fig_three_axes()
    fig_one_loop()
    fig_three_loops()
    print("OK: 3 figures ->", os.path.abspath("img"))
