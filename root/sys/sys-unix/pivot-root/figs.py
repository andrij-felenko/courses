# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"
WARM = "#b8860b"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Дві речі, які звуться коренем ────────────────────────────────────────
def fig_root_is_a_pair():
    W, H = 1200, 640
    p = []

    # рамки двох панелей
    p.append(rect(40, 56, 500, 350, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(660, 56, 500, 350, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # ── ліва панель: поля процесу ──
    p.append(text(290, 92, "поля процесу", size=15, bold=True))
    p.append(fitbox(80, 120, 420, 76,
                    "корінь\n( монтування 25  ·  dentry «/» )",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(80, 216, 420, 76,
                    "поточний каталог\n( монтування 25  ·  dentry «home/ann» )",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(text(290, 340, "кожне поле — пара, а не сам лише каталог", size=13, color=MUTED))
    p.append(text(290, 366, "монтування каже, яким входом ми сюди зайшли", size=13, color=MUTED))

    # ── права панель: дерево монтувань ──
    p.append(text(910, 92, "дерево монтувань простору", size=15, bold=True))
    fr, _, _, _, ay1 = tb(910, 152, ["монтування 25 — кореневе", "точка: немає"],
                          size=14, fill=GREEN_FILL, stroke=FIELD)
    p.append(fr)
    fr, _, _, by0, _ = tb(790, 290, ["монтування 31", "точка: /proc"],
                          size=13, fill=FILL)
    p.append(fr)
    fr, _, _, cy0, _ = tb(1035, 290, ["монтування 40", "точка: /mnt/img"],
                          size=13, fill=FILL)
    p.append(fr)
    p.append(arrow(895, ay1 + 4, 800, by0 - 6))
    p.append(arrow(928, ay1 + 4, 1022, cy0 - 6))
    p.append(text(910, 366, "корінь дерева — той вузол, у якого немає точки", size=13, color=MUTED))

    # ── нижні твердження ──
    fr, _, _, sy0, _ = tb(290, 486, ["chroot", "переписує пару в процесі —", "дерево монтувань те саме"],
                          size=14, fill=RED_FILL, stroke=POS, color=INK)
    p.append(fr)
    p.append(arrow(290, sy0 - 8, 290, 412))

    fr, _, _, sy0, _ = tb(910, 486, ["pivot_root", "переставляє кореневе монтування —", "дерево стає іншим"],
                          size=14, fill=WARM_FILL, stroke=WARM, color=INK)
    p.append(fr)
    p.append(arrow(910, sy0 - 8, 910, 412))

    p.append(text(600, 592,
                  "Перший ховає ім'я старого дерева, другий прибирає його з таблиці монтувань.",
                  size=14, color=MUTED))

    render(os.path.join(IMG, "root-is-a-pair.svg"), W, H, *p)


# ── 2. Що переставляє виклик у самих об'єктах монтування ────────────────────
def fig_pivot_root_rewire():
    W, H = 1400, 660
    p = []
    cols = [30, 490, 950]
    cw = 420
    caps = ["до виклику",
            "після pivot_root(\".\", \".\")",
            "після umount2(\".\", MNT_DETACH)"]

    for x, cap in zip(cols, caps):
        p.append(rect(x, 50, cw, 570, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
        p.append(text(x + cw / 2, 84, cap, size=15, bold=True))

    # ── колонка 1 ──
    c = cols[0] + cw / 2
    fr, _, _, _, a1 = tb(c, 165, ["монт. 25 — кореневе", "ФС машини", "точка: немає"],
                         size=13, fill=GREEN_FILL, stroke=FIELD)
    p.append(fr)
    fr, _, _, b0, _ = tb(c - 105, 315, ["монт. 31", "точка: /proc"], size=13, fill=FILL)
    p.append(fr)
    fr, _, _, d0, _ = tb(c + 108, 315, ["монт. 40 — прив'язка", "точка: /mnt/newroot"],
                         size=13, fill=BLUE_FILL, stroke=NEG)
    p.append(fr)
    p.append(arrow(c - 14, a1 + 4, c - 90, b0 - 6))
    p.append(arrow(c + 14, a1 + 4, c + 95, d0 - 6))
    p.append(text(c, 430, "образ прив'язано сам до себе —", size=12, color=MUTED))
    p.append(text(c, 452, "тільки тому там є що переставляти", size=12, color=MUTED))

    # ── колонка 2 ──
    c = cols[1] + cw / 2
    fr, _, _, _, a1 = tb(c, 165, ["монт. 40 — кореневе", "точка: немає"],
                         size=13, fill=GREEN_FILL, stroke=FIELD)
    p.append(fr)
    fr, _, _, b0, b1 = tb(c, 300, ["монт. 25 — старий корінь", "точка: /  (стосом зверху)"],
                          size=13, fill=WARM_FILL, stroke=WARM)
    p.append(fr)
    fr, _, _, d0, _ = tb(c, 430, ["монт. 31", "точка: /proc"], size=13, fill=FILL)
    p.append(fr)
    p.append(arrow(c, a1 + 4, c, b0 - 6))
    p.append(arrow(c, b1 + 4, c, d0 - 6))
    p.append(text(c, 520, "жодного монтування не створено", size=12, color=MUTED))
    p.append(text(c, 542, "й не знищено — змінено лише точки", size=12, color=MUTED))

    # ── колонка 3 ──
    c = cols[2] + cw / 2
    fr, _, _, _, _ = tb(c, 165, ["монт. 40 — кореневе", "точка: немає"],
                        size=13, fill=GREEN_FILL, stroke=FIELD)
    p.append(fr)
    p.append(rect(cols[2] + 30, 265, cw - 60, 250, fill="#fafafa", stroke=MUTED, sw=1.3, rx=10))
    p.append(text(c, 296, "від'єднане піддерево", size=13, bold=True, color=MUTED))
    fr, _, _, _, _ = tb(c, 350, ["монт. 25", "у дереві немає"], size=13,
                        fill=GREY_FILL, stroke=MUTED, color=MUTED)
    p.append(fr)
    fr, _, _, _, _ = tb(c, 430, ["монт. 31", "поїхало разом"], size=13,
                        fill=GREY_FILL, stroke=MUTED, color=MUTED)
    p.append(fr)
    p.append(text(c, 494, "живе, доки є посилання", size=12, color=MUTED))
    p.append(text(c, 552, "з нового кореня жодне ім'я", size=12, color=MUTED))
    p.append(text(c, 574, "туди не веде", size=12, color=MUTED))

    render(os.path.join(IMG, "pivot-root-rewire.svg"), W, H, *p)


# ── 3. Дорога, яка лишається повз імена ─────────────────────────────────────
def fig_leaked_fd_road():
    W, H = 1260, 600
    p = []

    # ліворуч: таблиця дескрипторів
    p.append(rect(40, 60, 380, 300, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(230, 96, "процес у новому корені", size=15, bold=True))
    p.append(fitbox(70, 120, 320, 54, "fd 0, 1, 2 — стандартні потоки",
                    size=13, fill=FILL))
    p.append(fitbox(70, 190, 320, 70,
                    "fd 7 — каталог старого кореня,\nвідкритий ДО підміни",
                    size=13, fill=RED_FILL, stroke=POS))
    p.append(text(230, 306, "корінь процесу: монтування 40", size=13, color=MUTED))
    p.append(text(230, 332, "поточний каталог: «/»", size=13, color=MUTED))

    # посередині: новий корінь
    fr, _, _, _, _ = tb(700, 150, ["новий корінь", "монтування 40"],
                        size=14, fill=GREEN_FILL, stroke=FIELD)
    p.append(fr)
    p.append(text(700, 232, "жодне ім'я звідси", size=13, color=MUTED))
    p.append(text(700, 256, "не веде назовні", size=13, color=MUTED))

    # праворуч: від'єднане дерево
    p.append(rect(900, 250, 320, 250, fill="#fafafa", stroke=MUTED, sw=1.3, rx=10))
    p.append(text(1060, 284, "від'єднане дерево машини", size=13, bold=True, color=MUTED))
    p.append(fitbox(930, 306, 260, 50, "монтування 25 — старий корінь",
                    size=12, fill=GREY_FILL, stroke=MUTED, color=MUTED))
    p.append(fitbox(930, 372, 260, 50, "усі його діти поїхали разом",
                    size=12, fill=GREY_FILL, stroke=MUTED, color=MUTED))
    p.append(text(1060, 456, "у таблиці монтувань його немає,", size=12, color=MUTED))
    p.append(text(1060, 478, "але об'єкт живий", size=12, color=MUTED))

    # червона дорога
    p.append(arrow(424, 300, 894, 396, color=POS, sw=2.2))
    fr, _, _, _, _ = tb(640, 322, ["fchdir(7)", "розбору шляху немає —", "отже, немає й перевірки"],
                        size=13, fill="#ffffff", stroke=POS, color=POS)
    p.append(fr)

    p.append(text(630, 556,
                  "MNT_DETACH прибирає ім'я, а не об'єкт: успадкований дескриптор лишається дорогою, доки його не закрити.",
                  size=14, color=MUTED))

    render(os.path.join(IMG, "leaked-fd-road.svg"), W, H, *p)


fig_root_is_a_pair()
fig_pivot_root_rewire()
fig_leaked_fd_road()
print("ok")
