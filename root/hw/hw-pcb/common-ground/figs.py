# -*- coding: utf-8 -*-
"""Фігури до теми «Спільна земля».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _box(f, cx, cy, w, h, title, sub, accent, fill):
    """Прямокутник-«пристрій» із заголовком і підписом усередині."""
    x, y = cx - w / 2, cy - h / 2
    f.append(rect(x, y, w, h, fill=fill, stroke=accent, sw=2, rx=10))
    f.append(text(cx, y + 24, title, size=14, bold=True, color=INK))
    f.append(line(x + 14, y + 34, x + w - 14, y + 34, color=accent, sw=1.2))
    f.append(mtext(cx, y + 56, sub, size=11.5, color=MUTED, lh=1.25))


def _gnd(f, x, y, color=INK, label=None):
    """Символ землі (три риски) з вершиною у (x,y)."""
    f.append(line(x, y, x, y + 10, color=color, sw=2))
    f.append(line(x - 16, y + 10, x + 16, y + 10, color=color, sw=2.4))
    f.append(line(x - 10, y + 16, x + 10, y + 16, color=color, sw=2.2))
    f.append(line(x - 5, y + 22, x + 5, y + 22, color=color, sw=2))
    if label:
        f.append(text(x, y + 38, label, size=11, color=color, bold=True))


# ── 1. Один дріт без спільної землі: значення пливе ──────────────────────────
def fig_floating():
    W, H = 760, 380
    f = [text(W / 2, 28, "Один сигнальний дріт без спільної землі — значення пливе",
              size=16, bold=True)]

    _box(f, 170, 150, 220, 110, "Давач", "видає 3 В\nвідносно ВЛАСНОЇ землі",
         NEG, "#eef2f8")
    _box(f, 590, 150, 220, 110, "Приймач", "міряє вхід\nвідносно СВОЄЇ землі",
         POS, "#fbeee6")

    # єдиний сигнальний дріт
    f.append(line(280, 130, 480, 130, color=INK, sw=2.4))
    b, _, _ = textbox(380, 112, "сигнал «3 В»", size=12, fill="#eef6ef",
                      stroke=FIELD, bold=True)
    f.append(b)

    # дві окремі землі — НЕ з'єднані
    _gnd(f, 170, 230, color=NEG, label="земля давача")
    _gnd(f, 590, 230, color=POS, label="земля приймача")

    # розрив між землями
    f.append(line(210, 252, 340, 252, color=MUTED, sw=1.6, dash="5,6"))
    f.append(line(420, 252, 550, 252, color=MUTED, sw=1.6, dash="5,6"))
    f.append(text(380, 248, "✗", size=22, bold=True, color=POS))
    b2, _, _ = textbox(380, 286, "спільної землі НЕМАЄ\nрізниця Uпл невизначена й плаває",
                       size=12, fill="#fbeee6", stroke=POS)
    f.append(b2)

    b3, _, _ = textbox(W / 2, 344,
                       "приймач читає не 3 В, а 3 В + Uпл  —  випадкове число, що дрейфує",
                       size=12.5, fill=FILL, stroke=LINE, bold=True)
    f.append(b3)
    render(os.path.join(IMG, "floating.svg"), W, H, *f)


# ── 2. Зсув землі: спад на спільному нулі ────────────────────────────────────
def fig_ground_shift():
    W, H = 760, 400
    f = [text(W / 2, 28, "Зсув землі: струм на опорі спільного нуля перекошує відлік",
              size=16, bold=True)]

    _box(f, 165, 130, 210, 96, "Передавач", "сигнал Uсиг\nвід свого нуля",
         NEG, "#eef2f8")
    _box(f, 595, 130, 210, 96, "Приймач", "читає\nUсиг − Uзс",
         POS, "#fbeee6")

    # сигнальний дріт (верхній)
    f.append(arrow(270, 112, 490, 112, color=INK, sw=2.2))
    f.append(text(380, 100, "сигнал", size=12, color=INK, bold=True))

    # спільний земляний дріт (нижній) з опором
    gy = 250
    f.append(line(165, 178, 165, gy, color=NEG, sw=2))
    f.append(line(595, 178, 595, gy, color=POS, sw=2))
    f.append(line(165, gy, 300, gy, color=INK, sw=2.4))
    f.append(line(460, gy, 595, gy, color=INK, sw=2.4))
    # резистор Rg на спільному нулі
    f.append(rect(300, gy - 12, 160, 24, fill="#fff3cd", stroke=POS, sw=1.8, rx=4))
    f.append(text(380, gy + 5, "Rg  (опір спільного нуля)", size=11.5, bold=True, color=INK))

    # зворотний струм
    f.append(arrow(470, gy + 30, 320, gy + 30, color=POS, sw=2))
    f.append(text(395, gy + 46, "Iзв  (сигнальний + живильний)", size=11.5, color=POS, bold=True))

    # формула-висновок
    b, _, _ = textbox(W / 2, gy + 92,
                      "Uзс = Iзв·Rg   піднімає нуль приймача над нулем передавача",
                      size=12.5, fill="#fbeee6", stroke=POS, bold=True)
    f.append(b)
    b2, _, _ = textbox(W / 2, gy + 130,
                       "що довший і тонший нуль і що більший струм — то більший зсув",
                       size=12, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "ground-shift.svg"), W, H, *f)


# ── 3. Шинна земля проти зоряної ─────────────────────────────────────────────
def fig_star_vs_bus():
    W, H = 760, 420
    f = [text(W / 2, 28, "Шинна земля (нуль перекошується) проти зоряної (вузли розв'язані)",
              size=16, bold=True)]
    f.append(line(W / 2, 50, W / 2, H - 20, color="#d6dde6", sw=1.2, dash="4,6"))

    def node(cx, cy, label, accent):
        f.append(circle(cx, cy, 20, fill="#eef2f8", stroke=accent, sw=2))
        f.append(text(cx, cy + 5, label, size=13, bold=True, color=accent))

    # ── ліворуч: шинна ──
    f.append(text(195, 66, "Шинна (ланцюжок)", size=14, bold=True, color=POS))
    bus_y = 300
    f.append(line(70, bus_y, 330, bus_y, color=INK, sw=3))      # спільна шина-нуль
    _gnd(f, 70, bus_y, color=INK)
    f.append(text(70, bus_y + 40, "джерело", size=10.5, color=MUTED))
    xs = [140, 220, 300]
    for i, x in enumerate(xs):
        node(x, 150, "ABC"[i], NEG)
        f.append(line(x, 170, x, bus_y, color=NEG, sw=2))
        f.append(circle(x, bus_y, 3.5, fill=INK, stroke=INK))
    # стрілки струму вздовж шини (накопичується)
    f.append(arrow(300, bus_y + 14, 80, bus_y + 14, color=POS, sw=1.8))
    f.append(text(195, bus_y + 30, "струм C тече крізь ділянки A і B", size=10.5,
                  color=POS, bold=True))
    b, _, _ = textbox(195, bus_y + 64, "нуль ближніх вузлів\nпіднятий сумою чужих спадів",
                      size=11, fill="#fbeee6", stroke=POS)
    f.append(b)

    # ── праворуч: зоряна ──
    f.append(text(575, 66, "Зоряна (одна точка)", size=14, bold=True, color=FIELD))
    star = (575, 300)
    f.append(circle(star[0], star[1], 6, fill=FIELD, stroke=INK, sw=1.6))
    _gnd(f, star[0], star[1] + 6, color=INK)
    f.append(text(star[0] + 70, star[1] + 10, "спільна точка", size=10.5, color=MUTED))
    for i, x in enumerate([460, 575, 690]):
        node(x, 150, "ABC"[i], FIELD)
        f.append(line(x, 170, star[0], star[1] - 4, color=FIELD, sw=2))
    b2, _, _ = textbox(575, star[1] + 60, "кожен платить лише за себе:\nспад Iₖ·rₖ у чужий нуль не лізе",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "star-vs-bus.svg"), W, H, *f)


# ── 4. Розділ сигнальної й силової землі ─────────────────────────────────────
def fig_split_ground():
    W, H = 760, 400
    f = [text(W / 2, 28, "Сигнальну й силову землю зводять лише в одній точці біля джерела",
              size=16, bold=True)]

    # спільна точка біля джерела (внизу по центру)
    star = (380, 320)
    f.append(circle(star[0], star[1], 7, fill=INK, stroke=INK))
    _gnd(f, star[0], star[1] + 7, color=INK)
    b0, _, _ = textbox(380, star[1] + 52, "єдина спільна точка (біля джерела живлення)",
                       size=11.5, fill=FILL, stroke=LINE, bold=True)
    f.append(b0)

    # ── силова гілка (ліворуч) ──
    _box(f, 165, 130, 210, 100, "Силовий вузол", "мотор, силовий ключ\nвеликі, імпульсні струми",
         POS, "#fbeee6")
    f.append(line(165, 180, 165, 300, color=POS, sw=3))
    f.append(line(165, 300, star[0] - 7, star[1], color=POS, sw=3))
    f.append(text(150, 250, "силова", size=11.5, color=POS, bold=True, anchor="end"))
    f.append(text(150, 266, "земля", size=11.5, color=POS, bold=True, anchor="end"))
    f.append(arrow(165, 250, 165, 296, color=POS, sw=1.6))

    # ── сигнальна гілка (праворуч) ──
    _box(f, 595, 130, 210, 100, "Сигнальний вузол", "давач, АЦП\nслабкі струми",
         FIELD, "#eef6ef")
    f.append(line(595, 180, 595, 300, color=FIELD, sw=2))
    f.append(line(595, 300, star[0] + 7, star[1], color=FIELD, sw=2))
    f.append(text(612, 250, "сигнальна", size=11.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(612, 266, "земля", size=11.5, color=FIELD, bold=True, anchor="start"))

    # підпис-висновок угорі по центру
    b, _, _ = textbox(380, 150, "брудний струм НЕ проходить\nсигнальною ділянкою —\nнуль сигналу лишається чистим",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "split-ground.svg"), W, H, *f)


if __name__ == "__main__":
    fig_floating()
    fig_ground_shift()
    fig_star_vs_bus()
    fig_split_ground()
    print("OK: 4 figures ->", IMG)
