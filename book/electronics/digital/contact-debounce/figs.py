# -*- coding: utf-8 -*-
"""Фігури до вставки «Антибрязкіт у коді» (тема «Брязкіт контактів»).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # «автомат» — тепла, але темна (читабельна на світлому)


# ── three.svg : три ідіоми антибрязкоту поряд ───────────────────────────────
def fig_three():
    W, H = 900, 320
    f = [text(W / 2, 30, "Антибрязкіт у коді: три підходи до того самого", size=18, bold=True),
         text(W / 2, 52, "усі вважають пачку дрижань за одну подію — лише міряють «устоявся» по-різному",
              size=11, color=MUTED, italic=True)]

    cw, gap = 250, 40
    x0 = (W - (3 * cw + 2 * gap)) / 2
    top = 78
    bh = 168

    def card(x, stroke, fill, title, body, holds):
        f.append(rect(x, top, cw, bh, fill=fill, stroke=stroke, sw=2, rx=12))
        f.append(text(x + cw / 2, top + 30, title, size=14, bold=True, color=stroke))
        f.append(mtext(x + cw / 2, top + 58, body, size=11, color=INK, lh=1.35))
        f.append(line(x + 18, top + bh - 36, x + cw - 18, top + bh - 36,
                      color="#d6dde6", sw=1.2))
        f.append(text(x + cw / 2, top + bh - 16, holds, size=10.5, color=MUTED, bold=True))

    card(x0, NEG, "#e9eefb", "Лічильник",
         ["рахуй однакові відліки", "поспіль; набралось N —", "рівень устояв, приймай"],
         "тримає: число відліків")
    card(x0 + cw + gap, FIELD, "#eef6ef", "Мітка часу",
         ["запам'ятай час зміни;", "не чіпай рівень, поки", "не мине вікно T"],
         "тримає: час останньої зміни")
    card(x0 + 2 * (cw + gap), GOLD, "#fbf3e0", "Автомат станів",
         ["явні стани: стабільний →", "під підозрою → знову", "стабільний; решта — там само"],
         "тримає: стан + час")

    f.append(text(W / 2, 296,
                  "Простіше — лічильник; не блокує цикл — мітка часу; найнадійніше — автомат.",
                  size=11.5, bold=True))
    render(os.path.join(IMG, "three.svg"), W, H, *f)


# ── fsm.svg : автомат антибрязкоту, дрижання застрягає «під підозрою» ────────
def fig_fsm():
    W, H = 900, 300
    f = [text(W / 2, 30, "Автомат антибрязкоту: не вірити першій зміні", size=18, bold=True),
         text(W / 2, 52, "дочекатися, поки рівень устоїться за час T, і лише тоді визнати подію",
              size=11, color=MUTED, italic=True)]

    cy = 158
    r = 58
    xs = 168          # СТАБІЛЬНИЙ
    xm = 450          # ПІД ПІДОЗРОЮ
    xe = 732          # СТАБІЛЬНИЙ′ / подія

    f.append(circle(xs, cy, r, fill="#eef6ef", stroke=FIELD, sw=2.2))
    f.append(text(xs, cy - 4, "СТАБІЛЬНИЙ", size=11, bold=True, color=FIELD))
    f.append(text(xs, cy + 16, "рівень тримається", size=9.5, color=MUTED))

    f.append(circle(xm, cy, r, fill="#fbf3e0", stroke=GOLD, sw=2.2))
    f.append(text(xm, cy - 4, "ПІД ПІДОЗРОЮ", size=10.5, bold=True, color=GOLD))
    f.append(text(xm, cy + 16, "чекаємо час T", size=9.5, color=MUTED))

    f.append(circle(xe, cy, r, fill="#eef6ef", stroke=FIELD, sw=2.2))
    f.append(text(xe, cy - 8, "СТАБІЛЬНИЙ′", size=11, bold=True, color=FIELD))
    f.append(text(xe, cy + 12, "подія!", size=10, bold=True, color=POS))

    # стабільний → під підозрою (зміна помічена)
    f.append(arrow(xs + r, cy - 8, xm - r, cy - 8, color=INK, sw=2))
    f.append(text((xs + xm) / 2, cy - 20, "зміна помічена", size=10, color=INK))
    # під підозрою → подія (T минув, рівень той самий)
    f.append(arrow(xm + r, cy - 8, xe - r, cy - 8, color=FIELD, sw=2))
    f.append(text((xm + xe) / 2, cy - 20, "T минув, рівень той самий", size=9.5, color=FIELD))
    # під підозрою → стабільний (хибна тривога) — дуга знизу
    f.append('<path d="M%.0f,%.0f Q %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (xm - r * 0.6, cy + r * 0.8, (xs + xm) / 2, cy + 96,
                xs + r * 0.6, cy + r * 0.8, POS))
    f.append(text((xs + xm) / 2, cy + 104, "рівень повернувся — хибна тривога, назад",
                  size=9.5, color=POS))

    f.append(text(W / 2, 290,
                  "Дрижання застрягає «під підозрою» й до події не доходить — саме цього ми й хотіли.",
                  size=11, bold=True))
    render(os.path.join(IMG, "fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three()
    fig_fsm()
    print("OK: 2 figures ->", IMG)
