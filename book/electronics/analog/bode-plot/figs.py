# -*- coding: utf-8 -*-
"""Фігури до вставки «Зняти АЧХ власноруч» (proj-bode-measurement).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # тепла мідь для дротів


# ── 1. Установка: два канали, бо вхід теж пливе ──────────────────────────────
def fig_setup():
    W, H = 820, 420
    f = [text(W / 2, 30, "Установка: два канали, бо вхід теж пливе", size=17, bold=True),
         text(W / 2, 52, "ділимо виміряний вихід на виміряний вхід — характеристика генератора випадає",
              size=12, color=MUTED, italic=True)]

    line_y = 170
    # генератор
    f.append(fitbox(40, line_y - 35, 130, 70, "генератор\nсинус, лог-кроки",
                    size=12, fill=FILL, bold=True))
    # вузол входу кола (CH1)
    in_x = 250
    f.append(line(170, line_y, in_x, line_y, color=WIRE, sw=2.4))
    f.append(circle(in_x, line_y, 4.5, fill=INK, stroke=INK))
    # коло (зелене — поле/виділення)
    f.append(rect(in_x, line_y - 35, 150, 70, fill="#eaf6ee", stroke=FIELD, sw=2))
    f.append(mtext(in_x + 75, line_y - 4, ["ваше коло", "(фільтр, підсилювач…)"],
                   size=12, color=INK, bold=True, lh=1.4))
    # вузол виходу кола (CH2)
    out_x = in_x + 150 + 80
    f.append(line(in_x + 150, line_y, out_x, line_y, color=WIRE, sw=2.4))
    f.append(circle(out_x, line_y, 4.5, fill=INK, stroke=INK))
    # осцилограф / два канали
    f.append(rect(out_x, line_y - 50, 180, 130, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(out_x + 90, line_y - 28, "осцилограф / АЦП", size=12, bold=True))

    # CH1: від входу кола до приладу (синій)
    f.append(line(in_x, line_y, in_x, line_y + 70, color=NEG, sw=1.8, dash="5 4"))
    f.append(line(in_x, line_y + 70, out_x + 30, line_y + 70, color=NEG, sw=1.8, dash="5 4"))
    f.append(line(out_x + 30, line_y + 70, out_x + 30, line_y + 30, color=NEG, sw=1.8, dash="5 4"))
    f.append(text(out_x + 12, line_y - 6, "CH1: A_вх", size=11, color=NEG, bold=True, anchor="start"))
    # CH2: від виходу кола до приладу (червоний)
    f.append(line(out_x, line_y, out_x, line_y + 44, color=POS, sw=1.8, dash="5 4"))
    f.append(line(out_x, line_y + 44, out_x + 60, line_y + 44, color=POS, sw=1.8, dash="5 4"))
    f.append(line(out_x + 60, line_y + 44, out_x + 60, line_y + 30, color=POS, sw=1.8, dash="5 4"))
    f.append(text(out_x + 12, line_y + 14, "CH2: A_вих", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(out_x + 90, line_y + 60, "K = A_вих / A_вх", size=12, bold=True))

    # нижня смужка: рядок таблиці з реальними числами (RC-ФНЧ, f_c≈1 кГц)
    rowy = 300
    f.append(rect(60, rowy, 700, 70, fill=BG, stroke=LINE, sw=1.4))
    fr = ["f, Гц", "100", "300", "1к", "3к", "10к", "30к"]
    gv = ["G, дБ", "0.0", "−0.4", "−3.0", "−10.0", "−20.0", "−29.6"]
    colx = [110, 230, 320, 410, 500, 590, 685]
    for i, (a, b) in enumerate(zip(fr, gv)):
        anc = "start" if i == 0 else "middle"
        col = MUTED if i == 0 else INK
        f.append(text(colx[i] - (30 if i == 0 else 0), rowy + 28, a, size=11, color=col,
                      bold=(i == 0), anchor=anc))
        f.append(text(colx[i] - (30 if i == 0 else 0), rowy + 52, b, size=11,
                      color=(MUTED if i == 0 else POS), bold=True, anchor=anc))
    f.append(text(W / 2, rowy - 8, "кроки частоти — рівні МНОЖНИКИ (×3 тут; для гладкої — 10 точок/декаду, ×1.26)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "setup.svg"), W, H, *f)


# ── 2. Від точок до портрета: що шукати очима ───────────────────────────────
def fig_read():
    W, H = 820, 440
    f = [text(W / 2, 30, "Від точок до портрета: що шукати очима", size=17, bold=True),
         text(W / 2, 52, "полиця → рівень; −3 дБ → f_c; далекий нахил → порядок (кратний −20 дБ/дек)",
              size=12, color=MUTED, italic=True)]

    # поле графіка
    L, R, T, B = 100, 700, 90, 360
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(R, B + 24, "f (лог)", size=13, bold=True, anchor="end"))
    f.append(text(L - 6, T - 8, "G, дБ", size=13, bold=True, anchor="middle"))

    # горизонтальні сітки дБ: 0, −3, −20, −40
    db_levels = [(0, "0"), (-3, "−3"), (-20, "−20"), (-40, "−40")]
    db_top, db_bot = 0.0, -45.0
    def yv(db):
        return T + (db_top - db) / (db_top - db_bot) * (B - T)
    for db, lab in db_levels:
        y = yv(db)
        f.append(line(L, y, R, y, color="#e4e4e4", sw=1))
        f.append(text(L - 8, y + 4, lab, size=10.5, color=MUTED, anchor="end"))

    # асимптоти (пунктир): полиця 0 дБ до зламу, далі −20 дБ/дек
    x_break = L + (R - L) * 0.45     # f_c
    asym_end_db = -27.0
    f.append(line(L, yv(0), x_break, yv(0), color=MUTED, sw=1.4, dash="7 5"))
    f.append(line(x_break, yv(0), R - 30, yv(asym_end_db), color=MUTED, sw=1.4, dash="7 5"))

    # виміряна крива (ФНЧ 1-го порядку): точки + з'єднувальна лінія
    import math as _m
    pts = []
    n = 90
    for i in range(n + 1):
        fx = L + (R - L) * i / n
        # частота у декадах відносно зламу
        dec = (fx - x_break) / ((R - L) / _m.log10(10) * 0.30)  # масштаб декади
        ratio = 10 ** dec
        db = -10 * _m.log10(1 + ratio * ratio)
        pts.append((fx, yv(max(db, db_bot))))
    path = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, POS))

    # маркери-виміри (кружечки), згущені біля зламу
    mark_x = [L + (R - L) * t for t in (0.05, 0.16, 0.30, 0.40, 0.45, 0.50, 0.58, 0.72, 0.88)]
    for mx in mark_x:
        dec = (mx - x_break) / ((R - L) / _m.log10(10) * 0.30)
        ratio = 10 ** dec
        db = -10 * _m.log10(1 + ratio * ratio)
        f.append(circle(mx, yv(max(db, db_bot)), 4.2, fill=BG, stroke=POS, sw=2))

    # підписи-висновки
    f.append(text(L + 40, yv(0) - 10, "полиця: рівень підсилення", size=11.5,
                  color=FIELD, bold=True, anchor="start"))
    f.append(circle(x_break, yv(-3), 5, fill=FIELD, stroke=FIELD))
    f.append(text(x_break + 10, yv(-3) + 16, "−3 дБ від полиці → це f_c", size=11.5,
                  color=FIELD, bold=True, anchor="start"))
    f.append(text(x_break + 70, yv(-22), "нахил −20 дБ/дек", size=11.5, bold=True, anchor="start"))
    f.append(text(x_break + 70, yv(-22) + 16, "→ один полюс (1-й порядок)", size=11.5,
                  bold=True, anchor="start"))
    f.append(text(x_break - 20, B - 6, "точки згущено там, де крива гнеться",
                  size=10.5, color="#9a2b22", italic=True, anchor="middle"))

    f.append(text(W / 2, 415, "звірка з асимптотами (пунктир) — головна перевірка: "
                              "нахил не кратний 20 дБ/дек = вимір бреше",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "read.svg"), W, H, *f)


if __name__ == "__main__":
    fig_setup()
    fig_read()
    print("OK: 2 SVG -> img/")
