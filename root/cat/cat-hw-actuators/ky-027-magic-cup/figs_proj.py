# -*- coding: utf-8 -*-
"""Фігури до вставки proj «магічна чаша» (KY-027).
Окремий файл, щоб не чіпати основний figs.py теми.
Запуск:  python figs_proj.py   → пише SVG у ./img/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Конвеєр одного такту loop(): читання → debounce → рівень → вивід ───────
def fig_loop():
    W, H = 820, 300
    f = []
    f.append(text(W / 2, 32, "Один такт loop(): від піна S до яскравості L", size=17, bold=True))

    # чотири блоки-стадії зліва направо, з ЗАПАСОМ по ширині
    stages = [
        (70,  "1. Читаємо",   ["digitalRead(A), (B)", "сирі рівні S", "(брязкіт!)"], NEG),
        (270, "2. Гасимо",    ["брязкіт:", "стабільно 25 мс", "→ чистий стан"], FIELD),
        (470, "3. Рухаємо",   ["нахил A → level+", "нахил B → level−", "по 1 за такт"], POS),
        (670, "4. Виводимо",  ["A = level", "B = 255 − level", "analogWrite(~)"], INK),
    ]
    bx0, bw, by, bh = 0, 150, 90, 96
    for x, title_, lines, col in stages:
        f.append(rect(x, by, bw, bh, fill="#ffffff", stroke=col, sw=1.8, rx=10))
        f.append(text(x + bw / 2, by + 24, title_, size=13, bold=True, color=col))
        for i, ln in enumerate(lines):
            f.append(text(x + bw / 2, by + 46 + i * 17, ln, size=10.5, color=MUTED))

    # стрілки між блоками
    for x in (220, 420, 620):
        f.append('<line x1="%d" y1="138" x2="%d" y2="138" stroke="%s" stroke-width="1.8" '
                 'marker-end="url(#arrow)"/>' % (x, x + 48, LINE))

    # петля назад: вихід 4 → назад до 1 (наступний такт)
    f.append('<path d="M745 186 L745 236 L145 236 L145 186" fill="none" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % MUTED)
    f.append(text(445, 254, "наступний такт loop() — за ~4 мс (крок посування рівня)",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'proj-loop.svg'), W, H, "".join(f))


# ── 2. Скінченний автомат debounce однієї лінії S ────────────────────────────
def fig_debounce():
    W, H = 760, 330
    f = []
    f.append(text(W / 2, 32, "Debounce: сире читання лишає слід тільки після витримки", size=16, bold=True))

    # часова вісь: сирий сигнал S зверху, «прийнятий» стан знизу
    x0, x1 = 80, 700
    yraw, yacc = 110, 240
    f.append(text(x0 - 12, yraw + 5, "сире", size=12, color=NEG, anchor="end"))
    f.append(text(x0 - 12, yraw + 20, "S", size=12, color=NEG, anchor="end"))
    f.append(text(x0 - 12, yacc + 5, "прий-", size=12, color=FIELD, anchor="end"))
    f.append(text(x0 - 12, yacc + 20, "нято", size=12, color=FIELD, anchor="end"))

    # сирий сигнал: HIGH, потім брязкіт, потім стабільний LOW, потім знову брязкіт → HIGH
    hi, lo = -22, 0  # зсув по y від базової лінії (вгору = HIGH)
    # базові рівні
    f.append(line(x0, yraw, x1, yraw, color="#cccccc", sw=1))
    f.append(line(x0, yacc, x1, yacc, color="#cccccc", sw=1))

    # намалюємо сирий як ламану (послідовність рівнів)
    raw_seq = [  # (x_start, level)  level: 1=HIGH,0=LOW
        (80, 1), (250, 1),          # спокій HIGH
        (250, 0), (262, 1), (272, 0), (285, 1), (296, 0),  # брязкіт при замиканні
        (296, 0), (470, 0),         # стабільний LOW
        (470, 1), (482, 0), (494, 1), (506, 0), (516, 1),  # брязкіт при розмиканні
        (516, 1), (700, 1),         # спокій HIGH
    ]
    pts = []
    for xx, lvl in raw_seq:
        pts.append((xx, yraw + (hi if lvl else lo)))
    d = "M%.0f %.0f" % pts[0]
    prev = pts[0]
    for p in pts[1:]:
        # спершу горизонталь до нового x на старому рівні, тоді вертикаль — «сходинки»
        d += " L%.0f %.0f" % (p[0], prev[1])
        d += " L%.0f %.0f" % (p[0], p[1])
        prev = p
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))

    # прийнятий стан: перемикається на LOW лише через 25 мс СТАБІЛЬНОСТІ після 296,
    # і назад на HIGH через 25 мс стабільності після 516
    acc_low_x = 296 + 60   # умовні «25 мс» у пікселях запасу
    acc_hi_x = 516 + 60
    accs = [(80, 1), (acc_low_x, 1), (acc_low_x, 0), (acc_hi_x, 0), (acc_hi_x, 1), (700, 1)]
    pts2 = [(xx, yacc + (hi if lvl else lo)) for xx, lvl in accs]
    d2 = "M%.0f %.0f" % pts2[0]
    prev = pts2[0]
    for p in pts2[1:]:
        d2 += " L%.0f %.0f" % (p[0], prev[1])
        d2 += " L%.0f %.0f" % (p[0], p[1])
        prev = p
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d2, FIELD))

    # зони брязкоту — легка підсвітка + підпис ЗБОКУ, не поверх ліній
    f.append('<rect x="250" y="%d" width="46" height="30" fill="%s" fill-opacity="0.10"/>' % (yraw - 26, NEG))
    f.append('<rect x="470" y="%d" width="46" height="30" fill="%s" fill-opacity="0.10"/>' % (yraw - 26, NEG))
    f.append(text(273, yraw - 32, "брязкіт", size=10, color=NEG))
    f.append(text(493, yraw - 32, "брязкіт", size=10, color=NEG))

    # стрілки «витримка 25 мс» — від кінця брязкоту до фронту прийнятого
    f.append('<line x1="300" y1="%d" x2="352" y2="%d" stroke="%s" stroke-width="1.4" '
             'stroke-dasharray="4 3" marker-end="url(#arrow)"/>' % (yacc, yacc, MUTED))
    f.append(text(326, yacc + 26, "витримка", size=10, color=MUTED))
    f.append(text(326, yacc + 40, "≈25 мс", size=10, color=MUTED))
    f.append('<line x1="520" y1="%d" x2="572" y2="%d" stroke="%s" stroke-width="1.4" '
             'stroke-dasharray="4 3" marker-end="url(#arrow)"/>' % (yacc, yacc, MUTED))
    f.append(text(546, yacc + 26, "витримка", size=10, color=MUTED))
    f.append(text(546, yacc + 40, "≈25 мс", size=10, color=MUTED))

    # підпис: короткі сплески брязкоту прийнятий стан ІГНОРУЄ
    f.append(text(W / 2, 305, "Короткі сплески не встигають протриматись 25 мс → прийнятий стан їх не бачить",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'proj-debounce.svg'), W, H, "".join(f))


if __name__ == "__main__":
    fig_loop()
    fig_debounce()
    print("OK: proj-loop.svg, proj-debounce.svg")
