# -*- coding: utf-8 -*-
"""Фігури до теми «Метод Гаусса». Генерує SVG у ./img через спільний svgkit.
Запуск:  python figs.py   (з теки теми)
Перевірка:  python ../../../../scripts/svgcheck.py img
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

MONO = "'DejaVu Sans Mono', 'Consolas', monospace"


def cell(x, y, s, color=INK, size=15, bold=True):
    """Один елемент матриці, моноширинно, по центру клітинки."""
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle"%s>%s</text>' % (x, y + size * 0.35, MONO, size, color, w, esc(s)))


def matrix(ox, oy, rows, rhs, colw=34, rowh=30, bar=True, dim=None):
    """Розширена матриця: rows — список рядків коефіцієнтів, rhs — права частина.
    dim — множина (r,c) клітинок коефіцієнтів, які малюємо тьмяно (вже обнулені).
    Повертає (фрагменти, ширина, висота) для зовнішнього компонування."""
    nC = len(rows[0])
    nR = len(rows)
    W = (nC + 1) * colw + 26
    H = nR * rowh + 18
    parts = [rect(ox, oy, W, H, fill="#fff", stroke="#c7ccd1", sw=1.4)]
    for r in range(nR):
        cy = oy + 18 + r * rowh
        for c in range(nC):
            cx = ox + 22 + c * colw
            col = MUTED if (dim and (r, c) in dim) else INK
            parts.append(cell(cx, cy, rows[r][c], color=col))
        # права частина (лише якщо задана)
        if rhs[r] != "":
            parts.append(cell(ox + 22 + nC * colw + colw * 0.15, cy, rhs[r], color=NEG))
    if bar:
        bx = ox + 22 + nC * colw - colw * 0.34
        parts.append(line(bx, oy + 6, bx, oy + H - 6, color="#9aa0a6", sw=1.4))
    return parts, W, H


# ── Фігура 1: прямий хід (трикутник) + зворотний хід ─────────────────────────
# Три знімки матриці зліва направо: вихідна → перший стовпець обнулено →
# трикутна. Підписи над стрілками — самі рядкові операції. Знизу — зворотний хід.
# Ідея, яку важко передати словами: як обидва ходи разом дають числа розв'язку.

def fig_elimination():
    W, H = 900, 430
    parts = []

    m1 = [["1", "1", "1"], ["2", "3", "−1"], ["1", "−1", "2"]]
    r1 = ["6", "5", "5"]
    m2 = [["1", "1", "1"], ["0", "1", "−3"], ["0", "−2", "1"]]
    r2 = ["6", "−7", "−1"]
    m3 = [["1", "1", "1"], ["0", "1", "−3"], ["0", "0", "−5"]]
    r3 = ["6", "−7", "−15"]
    dim2 = {(1, 0), (2, 0)}
    dim3 = {(1, 0), (2, 0), (2, 1)}

    oy = 92
    p, w1, h1 = matrix(70, oy, m1, r1)
    parts += p
    p, w2, h2 = matrix(364, oy, m2, r2, dim=dim2)
    parts += p
    p, w3, h3 = matrix(658, oy, m3, r3, dim=dim3)
    parts += p

    midy = oy + h1 / 2
    parts.append(arrow(70 + w1 + 6, midy, 364 - 6, midy, color=INK, sw=2))
    parts.append(text((70 + w1 + 364) / 2, midy - 14, "R2−2R1", size=11, color=POS, bold=True))
    parts.append(text((70 + w1 + 364) / 2, midy + 24, "R3−R1", size=11, color=POS, bold=True))
    parts.append(arrow(364 + w2 + 6, midy, 658 - 6, midy, color=INK, sw=2))
    parts.append(text((364 + w2 + 658) / 2, midy - 14, "R3+2R2", size=11, color=POS, bold=True))

    parts.append(text(658 + w3 / 2, oy - 12, "трикутна", size=12, color=FIELD, bold=True))

    # зворотний хід — рамка знизу
    by = 290
    box = rect(120, by, 660, 122, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=10)
    parts.append(box)
    parts.append(text(140, by + 26, "Зворотний хід (знизу вгору):", size=13, color=INK, anchor="start", bold=True))
    steps = ["−5z = −15   →   z = 3", "y − 3·3 = −7   →   y = 2", "x + 2 + 3 = 6   →   x = 1"]
    for i, s in enumerate(steps):
        parts.append('<text x="152" y="%.0f" font-family="%s" font-size="13" fill="%s" '
                     'text-anchor="start" font-weight="700">%s</text>'
                     % (by + 54 + i * 24, MONO, NEG, esc(s)))
    rb, rw, rh = textbox(640, by + 70, "(x, y, z) =\n(1, 2, 3)", size=14, color=FIELD,
                         fill="#fff", stroke=FIELD, sw=1.6, bold=True)
    parts.append(rb)

    render(os.path.join(OUT, 'gauss.svg'), W, H, *parts,
           title='Метод Гаусса: прямий хід зводить до трикутної, зворотний дає розв\'язок')


# ── Фігура 2: підступ півота — нуль і мале число на діагоналі ────────────────
# Ліворуч: на діагоналі 0, ділити не можна → переставляємо рядки.
# Праворуч (текст-рамка): чому й мале небезпечне, часткове впорядкування, ціна.
# Ідея словами незручна: «найбільший півот» — це не примха, а захист від похибок.

def fig_pivoting():
    W, H = 860, 360
    parts = []

    parts.append(line(W / 2, 70, W / 2, H - 24, color="#e4e4e4", sw=1.5))

    parts.append(text(225, 96, "Нуль на діагоналі → переставити рядки", size=12, color=POS, bold=True))
    # матриця з нулем-півотом
    p, mw, mh = matrix(150, 116, [["0", "2"], ["3", "1"]], ["", ""], bar=False)
    parts += p
    parts.append(text(150 + mw / 2, 116 + mh + 18, "на 0 не поділиш!", size=10, color=POS, bold=True))
    parts.append(arrow(150 + mw + 8, 116 + mh / 2, 150 + mw + 60, 116 + mh / 2, color=FIELD, sw=2.2))
    parts.append(text(150 + mw + 34, 116 + mh / 2 - 10, "swap", size=9, color=FIELD, bold=True))
    p, mw2, mh2 = matrix(150 + mw + 70, 116, [["3", "1"], ["0", "2"]], ["", ""], bar=False)
    parts += p
    parts.append(text(150 + mw + 70 + mw2 / 2, 116 + mh2 + 18, "тепер півот = 3", size=10, color=FIELD, bold=True))

    # права колонка — текст
    parts.append(text(660, 96, "Чому беруть НАЙБІЛЬШИЙ", size=12, color=INK, bold=True))
    bx = rect(498, 116, 338, 200, fill="#f7f8f9", stroke="#9aa0a6", sw=1.5, rx=10)
    parts.append(bx)
    lines = [
        ("Мале число теж зле: ділення на", False),
        ("нього роздуває похибки округлення.", True),
        ("", False),
        ("Тому беруть найбільший доступний", False),
        ("півот — часткове впорядкування.", True),
        ("", False),
        ("Складність прямого ходу — O(N³),", False),
        ("і це головна ціна великих систем.", True),
    ]
    yy = 142
    for s, muted in lines:
        if not s:
            yy += 10
            continue
        parts.append(text(516, yy, s, size=11, color=(MUTED if muted else INK), anchor="start"))
        yy += 19

    render(os.path.join(OUT, 'pivoting.svg'), W, H, *parts,
           title='Підступ півота: на діагоналі не можна нуль — і небажано мале число')


# ── Фігура 3: множники виключення = матриця L (розклад LU) ───────────────────
# Показує, що числа, на які множили рядки під час прямого ходу (2, 1, −2),
# не зникають марно — вони складаються в нижню трикутну матрицю L, а підсумок
# прямого ходу — це верхня трикутна U. Звідси A = L·U. Це ядро, чому один
# розклад дає змогу швидко розв'язувати з багатьма правими частинами.

def fig_lu():
    W, H = 820, 360
    parts = []

    # A
    p, aw, ah = matrix(70, 120, [["1", "1", "1"], ["2", "3", "−1"], ["1", "−1", "2"]], ["", "", ""], bar=False)
    parts += p
    parts.append(text(70 + aw / 2, 110, "A", size=15, color=INK, bold=True))
    parts.append(text(70 + aw / 2, 120 + ah + 18, "вихідна", size=10, color=MUTED))

    parts.append(text(70 + aw + 26, 120 + ah / 2 + 5, "=", size=22, color=INK))

    # L (множники)
    lx = 70 + aw + 50
    p, lw, lh = matrix(lx, 120, [["1", "0", "0"], ["2", "1", "0"], ["1", "−2", "1"]], ["", "", ""], bar=False)
    parts += p
    parts.append(text(lx + lw / 2, 110, "L", size=15, color=POS, bold=True))
    parts.append(text(lx + lw / 2, 120 + lh + 18, "множники виключення", size=10, color=POS))

    parts.append(text(lx + lw + 20, 120 + lh / 2 + 5, "·", size=22, color=INK))

    # U (трикутна)
    ux = lx + lw + 42
    p, uw, uh = matrix(ux, 120, [["1", "1", "1"], ["0", "1", "−3"], ["0", "0", "−5"]], ["", "", ""], bar=False)
    parts += p
    parts.append(text(ux + uw / 2, 110, "U", size=15, color=FIELD, bold=True))
    parts.append(text(ux + uw / 2, 120 + uh + 18, "результат прямого ходу", size=10, color=FIELD))

    parts.append(text(W / 2, H - 26,
                      "Числа, на які множили рядки (2, 1, −2), складаються в L; підсумок — U. Тому A = L·U.",
                      size=12, color=INK))

    render(os.path.join(OUT, 'lu-decomposition.svg'), W, H, *parts,
           title='Множники виключення не зникають: вони утворюють L у розкладі A = L·U')


fig_elimination()
fig_pivoting()
fig_lu()
print('SVG figures generated in', OUT)
