# -*- coding: utf-8 -*-
"""Фігури до вставки «proj-choose-by-budget»: вибір варіанта моделі за
ВИМІРЯНИМ бюджетом латентності (мс/кадр) і перевіркою влізання у Flash/арену.
Запуск:  python figs-choose.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Сито вибору: найбільший варіант, що ще лізе в усі три межі ─────────────
def fig_sieve():
    """Алгоритм каркаса. Кандидати n→x відсортовані за ВИМІРЯНИМ часом проходу
    (від найбільшого до найменшого). Кожен мусить пройти три ворота: час ≤ дедлайн,
    ваги ≤ Flash, арена ≤ RAM. Беремо ПЕРШИЙ (найбільший), що проходить усі три;
    якщо й найменший не пройшов — чесна відмова."""
    W, H = 900, 470
    f = [text(W / 2, 30, "Сито вибору: найбільший варіант, що проходить усі три ворота", size=17, bold=True)]

    # три ворота-колонки (заголовки)
    gates = [("час ≤ дедлайн", "виміряний прохід", NEG),
             ("ваги ≤ Flash", "int8-модель", FIELD),
             ("арена ≤ RAM", "активації", POS)]
    gx = [430, 590, 750]
    for (g, sub, col), x in zip(gates, gx):
        f.append(text(x, 78, g, size=12, bold=True, color=col))
        f.append(text(x, 94, sub, size=9, color=MUTED))

    # рядки-кандидати: (мітка, час, проходить-час, проходить-flash, проходить-ram)
    rows = [
        ("x  найточніший", "210 мс", False, True,  True),
        ("l",              "150 мс", False, True,  True),
        ("m",              " 95 мс", False, True,  False),
        ("s  ← ОБРАНО",    " 55 мс", True,  True,  True),
        ("n  найменший",   " 28 мс", True,  True,  True),
    ]
    ry0, rh = 116, 58
    deadline = "дедлайн 60 мс"
    for i, (lab, t, ok_t, ok_f, ok_r) in enumerate(rows):
        y = ry0 + i * rh
        chosen = "ОБРАНО" in lab
        boxcol = FIELD if chosen else (MUTED if not ok_t else LINE)
        fillc = "#eef6ef" if chosen else BG
        f.append(rect(50, y, 330, rh - 12, fill=fillc, stroke=boxcol, sw=2.2 if chosen else 1.4))
        f.append(text(70, y + 22, lab, size=13, bold=chosen,
                      color=FIELD if chosen else INK, anchor="start"))
        f.append(text(70, y + 39, "виміряно " + t.strip(), size=10, color=MUTED, anchor="start"))
        # три позначки воріт
        for (ok, x) in ((ok_t, gx[0]), (ok_f, gx[1]), (ok_r, gx[2])):
            if ok:
                f.append(text(x, y + 30, "✓", size=20, bold=True, color=FIELD))
            else:
                f.append(text(x, y + 30, "✗", size=20, bold=True, color=POS))

    # лінія дедлайну між m і s
    yl = ry0 + 3 * rh - 6
    f.append(line(40, yl, gx[0] + 30, yl, color=NEG, sw=2, dash="6 4"))
    f.append(text(44, yl - 6, deadline, size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(gx[0] + 36, yl - 6, "сканування згори вниз спиняється тут", size=10, color=NEG, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "сортуй за виміряним часом спадаюче → бери ПЕРШИЙ, що проходить час, Flash і арену",
                  size=12, color=INK))
    return render(os.path.join(IMG, "choose-sieve.svg"), W, H, *f)


# ── 2. Пастка «найточніша за замовчуванням» ──────────────────────────────────
def fig_trap():
    """Чому 'бери найточнішу' валить реальний час. Стовпчики — ВИМІРЯНИЙ на
    цьому чипі час проходу для n…x; горизонталь — дедлайн кадру. Варіант x
    (за замовчуванням 'найкращий') стоїть високо над лінією — апарат сліпне.
    Найбільший, що влазить, — s. Лінива відповідь 'x' = провал у повітрі."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Пастка: «найточніша за замовчуванням» валить реальний час", size=17, bold=True)]

    ox, oy = 90, 360            # початок осей
    ax, ay = 760, 70
    f.append(line(ox, oy, ax, oy, color=LINE, sw=1.6))   # X
    f.append(line(ox, oy, ox, ay, color=LINE, sw=1.6))   # Y
    f.append(text(ox - 64, (oy + ay) / 2, "час проходу", size=12, color=INK, anchor="middle"))
    f.append(text(ox - 64, (oy + ay) / 2 + 16, "мс/кадр", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox - 64, (oy + ay) / 2 + 32, "(виміряно)", size=10, color=MUTED, anchor="middle"))

    # дедлайн 60 мс
    deadline_ms = 60.0
    top_ms = 230.0             # масштаб осі
    def y_of(ms): return oy - (ms / top_ms) * (oy - ay)

    yd = y_of(deadline_ms)
    f.append(line(ox, yd, ax, yd, color=NEG, sw=2, dash="6 4"))
    f.append(text(ax, yd - 8, "дедлайн 60 мс/кадр", size=12, bold=True, color=NEG, anchor="end"))

    bars = [("n", 28, "влазить"), ("s", 55, "← найбільший,\nщо влазить"),
            ("m", 95, ""), ("l", 150, ""), ("x", 210, "«найкраща»\nза замовч.")]
    bw, gap = 84, 34
    x0 = ox + 40
    for i, (lab, ms, note) in enumerate(bars):
        x = x0 + i * (bw + gap)
        ytop = y_of(ms)
        fits = ms <= deadline_ms
        col = FIELD if fits else POS
        fill = "#eef6ef" if fits else "#fdecea"
        f.append(rect(x, ytop, bw, oy - ytop, fill=fill, stroke=col, sw=2))
        f.append(text(x + bw / 2, ytop - 8, "%d мс" % ms, size=12, bold=True, color=col))
        f.append(text(x + bw / 2, oy + 20, lab, size=14, bold=True, color=INK))
        if note:
            anc_y = ytop + 22 if fits else ytop + 26
            f.append(mtext(x + bw / 2, anc_y, note, size=10,
                           color=FIELD if fits else POS, bold=True))

    f.append(text(W / 2, H - 14,
                  "x точніший на крихту, але втричі за дедлайн — апарат реагує на застаріле минуле",
                  size=12, color=INK))
    return render(os.path.join(IMG, "choose-trap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sieve()
    fig_trap()
    print("OK: 2 фігури у", IMG)
