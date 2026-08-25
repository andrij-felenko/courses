# -*- coding: utf-8 -*-
# Фігури для вставки math-contract-rules.md (окремий скрипт, щоб не колідувати з
# паралельним figs.py тієї самої теми). Пише у ./img/, як і головний figs.py.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура: напрям варіантності сигнатури ────────────────────────────────────
# Клієнт передає аргумент і бере результат. Безпечно, якщо нащадок приймає
# ШИРШИЙ тип аргументу (контраваріантно — проти напряму <:) і повертає
# ВУЖЧИЙ тип результату (коваріантно — за напрямом <:).
def fig_variance():
    W, H = 820, 400
    p = []

    cb, cw, ch = textbox(135, 200, ["Клієнт", "знає лише тип T"],
                         size=14, pad=14, min_w=200)
    p.append(cb)

    # аргумент: контраваріантно (верхній рівень)
    p.append(text(520, 66, "тип АРГУМЕНТУ — контраваріантний", size=14, bold=True, color=NEG))
    ba, baw, bah = textbox(400, 122, ["база приймає", "U"], size=13, pad=12,
                           fill=FILL, min_w=170)
    p.append(ba)
    na, naw, nah = textbox(660, 122, ["нащадок мусить", "U або ШИРШЕ"], size=13, pad=12,
                           fill="#eaf7ee", stroke=FIELD, sw=2, min_w=210)
    p.append(na)
    p.append(arrow(492, 122, 550, 122, color=FIELD))
    p.append(text(520, 176, "клієнт шле аргумент типу U — нащадок мусить його стерпіти",
                  size=12, color=MUTED))

    # результат: коваріантно (нижній рівень)
    p.append(text(520, 258, "тип РЕЗУЛЬТАТУ — коваріантний", size=14, bold=True, color=POS))
    br, brw, brh = textbox(400, 314, ["база обіцяє", "R"], size=13, pad=12,
                           fill=FILL, min_w=170)
    p.append(br)
    nr, nrw, nrh = textbox(660, 314, ["нащадок може", "R або ВУЖЧЕ"], size=13, pad=12,
                           fill="#eaf7ee", stroke=FIELD, sw=2, min_w=210)
    p.append(nr)
    p.append(arrow(492, 314, 550, 314, color=FIELD))
    p.append(text(520, 368, "клієнт чекає результат типу R — вужчий результат теж підходить",
                  size=12, color=MUTED))

    p.append(line(200, 178, 312, 132, color=MUTED, dash="4 4"))
    p.append(line(200, 222, 312, 304, color=MUTED, dash="4 4"))

    render(os.path.join(IMG, 'variance.svg'), W, H, *p,
           title="Сигнатура нащадка: вхід ширший, вихід вужчий")


# ── Фігура: чотири правила поведінкової підтипізації ─────────────────────────
# Передумова ↓ (послабити), постумова ↑ (посилити), інваріант = (зберегти),
# історія — обмеження на переходи стану.
def fig_four_rules():
    W, H = 780, 440
    p = []

    rows = [
        ("Передумова", "можна лише ПОСЛАБИТИ", "приймай не менше входів, ніж база", NEG),
        ("Постумова", "можна лише ПОСИЛИТИ", "гарантуй не менше, ніж база", POS),
        ("Інваріант", "треба ЗБЕРЕГТИ", "усі інваріанти супертипу лишаються", FIELD),
        ("Історія", "не додавай нових переходів", "жодних змін стану, неможливих над базою", INK),
    ]
    y = 78
    step = 82
    lx = 55
    boxw = 670
    for name, rule, why, col in rows:
        p.append(rect(lx, y, boxw, 60, fill="#f7f9fc", stroke=col, sw=2))
        p.append(text(lx + 22, y + 25, name, size=15, bold=True, color=col, anchor="start"))
        p.append(text(lx + 22, y + 46, rule, size=13, color=INK, anchor="start"))
        p.append(text(lx + 360, y + 36, why, size=11, color=MUTED, anchor="start"))
        y += step

    p.append(text(W / 2, y + 8, "усі чотири разом  ⟺  S — поведінковий підтип T   (S <: T)",
                  size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'four-rules.svg'), W, H, *p,
           title="Чотири правила чесного підтипу")


if __name__ == '__main__':
    fig_variance()
    fig_four_rules()
    print("math figures written")
