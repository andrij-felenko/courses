# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_cross_two_worlds():
    """Крос-компілятор: виконується на host, генерує код для target — дві різні машини."""
    W, H = 700, 300
    parts = []

    # Хост-машина (ліворуч) — де компілятор ЖИВЕ й ПРАЦЮЄ
    hx = rect(40, 70, 250, 170, fill="#eaf0fd", stroke=NEG, sw=1.8)
    parts.append(hx)
    parts.append(text(165, 60, "HOST — де компілятор виконується", size=13, bold=True, color=NEG))
    inner, iw, ih = textbox(165, 130, ["Крос-компілятор", "(звичайна програма)"],
                            size=13, fill="#ffffff", stroke=NEG, bold=True)
    parts.append(inner)
    parts.append(text(165, 190, "x86-64, багато RAM,", size=12, color=MUTED))
    parts.append(text(165, 210, "клавіатура, диск", size=12, color=MUTED))

    # Таргет (праворуч) — для КОГО код
    tx = rect(410, 70, 250, 170, fill="#eafaf0", stroke=FIELD, sw=1.8)
    parts.append(tx)
    parts.append(text(535, 60, "TARGET — для кого код", size=13, bold=True, color=FIELD))
    inner2, iw2, ih2 = textbox(535, 130, ["Готовий бінарник", "для іншого процесора"],
                               size=13, fill="#ffffff", stroke=FIELD, bold=True)
    parts.append(inner2)
    parts.append(text(535, 190, "Cortex-M, 64 КБ Flash,", size=12, color=MUTED))
    parts.append(text(535, 210, "ні ОС, ні консолі", size=12, color=MUTED))

    # Стрілка «видає код для»
    parts.append(arrow(296, 155, 404, 155, color=INK, sw=2.4))
    parts.append(text(350, 143, "видає код для", size=12, color=INK, italic=True))

    render(os.path.join(OUT, 'cross-two-worlds.svg'), W, H, *parts,
           title="Крос-компілятор: працює тут, генерує код туди")


def fig_triplet():
    """Три ролі машин у збірці: build, host, target — і чотири випадки."""
    W, H = 720, 360
    parts = []

    # Верх — три ролі в ряд
    top = 74
    xs = [50, 265, 480]
    roles = [
        ("BUILD", ["де ЗБИРАЮТЬ", "сам компілятор"], "#f4f6f8", LINE),
        ("HOST", ["де компілятор", "ВИКОНУЄТЬСЯ"], "#eaf0fd", NEG),
        ("TARGET", ["для кого він", "ГЕНЕРУЄ код"], "#eafaf0", FIELD),
    ]
    for i, (name, body, fill, stroke) in enumerate(roles):
        x = xs[i]
        parts.append(rect(x, top, 190, 96, fill=fill, stroke=stroke, sw=1.8))
        parts.append(text(x + 95, top + 30, name, size=16, bold=True, color=stroke))
        for j, ln in enumerate(body):
            parts.append(text(x + 95, top + 56 + j * 20, ln, size=12.5, color=MUTED))

    # Стрілки послідовності
    ay = top + 48
    parts.append(arrow(xs[0] + 190 + 4, ay, xs[1] - 4, ay, color=MUTED, sw=1.8))
    parts.append(arrow(xs[1] + 190 + 4, ay, xs[2] - 4, ay, color=MUTED, sw=1.8))

    # Низ — таблиця чотирьох випадків
    yb = 220
    parts.append(text(360, yb - 6, "Чотири випадки — залежно від того, що з чим збігається:",
                      size=13, bold=True, color=INK))
    rows = [
        ("build = host = target", "нативний", "звичайний gcc на вашій машині"),
        ("build = host ≠ target", "крос", "arm-none-eabi-gcc на x86"),
        ("build ≠ host = target", "перенос компілятора", "готуємо gcc для нової машини"),
        ("build ≠ host ≠ target", "канадський крос", "усі три різні"),
    ]
    ry = yb + 16
    for k, (cond, name, ex) in enumerate(rows):
        yy = ry + k * 30
        col = FIELD if k == 1 else (POS if k == 3 else INK)
        parts.append(text(60, yy + 14, cond, size=12.5, anchor="start", bold=True, color=col))
        parts.append(text(340, yy + 14, name, size=12.5, anchor="start", color=col))
        parts.append(text(500, yy + 14, ex, size=11.5, anchor="start", color=MUTED, italic=True))
        if k < len(rows) - 1:
            parts.append(line(50, yy + 24, 700, yy + 24, color="#e5e7eb", sw=1))

    render(os.path.join(OUT, 'cross-triplet.svg'), W, H, *parts,
           title="build · host · target: три ролі однієї збірки")


def fig_canadian():
    """Канадський крос: три різні машини — build робить компілятор, що житиме на host і цілитиме в target."""
    W, H = 700, 330
    parts = []

    # BUILD (ліворуч, угорі) — де відбувається збірка
    parts.append(rect(40, 70, 200, 90, fill="#f4f6f8", stroke=LINE, sw=1.8))
    parts.append(text(140, 58, "BUILD (машина А)", size=12.5, bold=True, color=MUTED))
    parts.append(text(140, 105, "тут іде збірка", size=12.5, color=INK))
    parts.append(text(140, 128, "потужний сервер", size=11.5, color=MUTED, italic=True))

    # HOST (праворуч, угорі) — де готовий компілятор житиме
    parts.append(rect(460, 70, 200, 90, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(text(560, 58, "HOST (машина Б)", size=12.5, bold=True, color=NEG))
    parts.append(text(560, 105, "тут ЖИТИМЕ", size=12.5, color=INK))
    parts.append(text(560, 128, "новий компілятор", size=11.5, color=NEG, italic=True))

    # TARGET (унизу по центру) — для кого генерований код
    parts.append(rect(250, 220, 200, 90, fill="#eafaf0", stroke=FIELD, sw=1.8))
    parts.append(text(350, 208, "TARGET (машина В)", size=12.5, bold=True, color=FIELD))
    parts.append(text(350, 255, "для КОГО код", size=12.5, color=INK))
    parts.append(text(350, 278, "плата з МК", size=11.5, color=FIELD, italic=True))

    # Стрілка: build робить компілятор ДЛЯ host
    parts.append(arrow(244, 115, 456, 115, color=INK, sw=2.2))
    parts.append(text(350, 103, "А збирає компілятор, що працюватиме на Б", size=11.5,
                      color=INK, italic=True))

    # Стрілка: цей компілятор (на host) цілитиме в target
    parts.append('<path d="M560 164 Q560 250 454 265" fill="none" stroke="%s" '
                 'stroke-width="2.2" marker-end="url(#arrow)"/>' % NEG)
    parts.append(text(575, 210, "а він —", size=11, color=NEG, anchor="start", italic=True))
    parts.append(text(575, 226, "цілитиме в В", size=11, color=NEG, anchor="start", italic=True))

    render(os.path.join(OUT, 'cross-canadian.svg'), W, H, *parts,
           title="Канадський крос: три різні машини (build · host · target)")


if __name__ == '__main__':
    fig_cross_two_worlds()
    fig_triplet()
    fig_canadian()
    print("figures written to", OUT)
