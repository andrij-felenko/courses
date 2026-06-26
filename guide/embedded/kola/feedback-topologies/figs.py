# -*- coding: utf-8 -*-
"""Фігури до кроку «Топології зворотного зв'язку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def block(x, y, w, h, label, sub=None, fill="#eef1f5"):
    """Прямокутний блок із підписом по центру."""
    out = [rect(x, y, w, h, fill=fill, stroke=INK, sw=1.8, rx=8)]
    if sub:
        out.append(text(x + w / 2, y + h / 2 - 4, label, size=15, bold=True))
        out.append(text(x + w / 2, y + h / 2 + 15, sub, size=11, color=MUTED))
    else:
        out.append(text(x + w / 2, y + h / 2 + 5, label, size=15, bold=True))
    return "".join(out)


def summing(cx, cy, r=16):
    """Вузол-суматор (коло з ⊕)."""
    out = [circle(cx, cy, r, fill="#fff", stroke=INK, sw=1.8)]
    out.append(line(cx - r * 0.6, cy, cx + r * 0.6, cy, color=INK, sw=1.6))
    out.append(line(cx, cy - r * 0.6, cx, cy + r * 0.6, color=INK, sw=1.6))
    return "".join(out)


def pickoff(cx, cy):
    return '<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (cx, cy, INK)


# ───────────────────────── Фіг. 1: загальна петля ─────────────────────────
def fig_loop():
    W, H = 760, 360
    f = [text(W / 2, 30, "Чотири питання однієї петлі: що береться з виходу й як вертається на вхід",
              size=15, bold=True)]

    # координати
    sum_x, sum_y = 150, 150          # суматор (вхід)
    a_x, a_y, a_w, a_h = 250, 120, 150, 64   # пряма ланка A
    pick_x = 560                      # точка відбору з виходу
    out_x = 660                       # вихід
    beta_x, beta_y, beta_w, beta_h = 330, 250, 150, 56  # ланка β (зворотна)

    # вхід → суматор
    f.append(text(48, sum_y + 5, "вхід", size=13, bold=True))
    f.append(arrow(78, sum_y, sum_x - 16, sum_y, color=INK, sw=1.8))
    f.append(summing(sum_x, sum_y))
    f.append(text(sum_x - 22, sum_y - 18, "+", size=18, bold=True, color=POS))
    f.append(text(sum_x - 22, sum_y + 34, "−", size=18, bold=True, color=NEG))

    # суматор → A
    f.append(arrow(sum_x + 16, sum_y, a_x, a_y + a_h / 2, color=INK, sw=1.8))
    f.append(block(a_x, a_y, a_w, a_h, "A", "пряма ланка (підсилення)"))

    # A → вихід, з точкою відбору
    f.append(line(a_x + a_w, a_y + a_h / 2, out_x, a_y + a_h / 2, color=INK, sw=1.8))
    f.append(pickoff(pick_x, a_y + a_h / 2))
    f.append(text(out_x + 4, a_y + a_h / 2 + 5, "вихід", size=13, bold=True, anchor="start"))

    # відбір (sampling) — вниз до β
    f.append(text(pick_x + 8, a_y + a_h / 2 - 12, "ВІДБІР", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(pick_x, a_y + a_h / 2, pick_x, beta_y + beta_h / 2, color=INK, sw=1.8))
    f.append(arrow(pick_x, beta_y + beta_h / 2, beta_x + beta_w, beta_y + beta_h / 2, color=INK, sw=1.8))
    f.append(block(beta_x, beta_y, beta_w, beta_h, "β", "ланка зворотного зв'язку", fill="#eaf0fd"))

    # β → суматор (mixing)
    f.append(line(beta_x, beta_y + beta_h / 2, sum_x, beta_y + beta_h / 2, color=INK, sw=1.8))
    f.append(arrow(sum_x, beta_y + beta_h / 2, sum_x, sum_y + 16, color=INK, sw=1.8))
    f.append(text(sum_x - 8, beta_y + beta_h / 2 + 18, "ЗМІШУВАННЯ", size=11, bold=True, color=NEG, anchor="middle"))

    # формула й два питання
    box = ("Два незалежні вибори:\n"
           "ВІДБІР — стежимо за напругою (паралельно) чи за струмом (послідовно)?\n"
           "ЗМІШУВАННЯ — віднімаємо напругу (послідовно) чи струм (паралельно)?")
    f.append(fitbox(250, 300, 410, 52, box, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))
    f.append(text(660, 300, "A_зз =", size=12, anchor="start", color=MUTED))
    f.append(text(660, 320, "A/(1+Aβ)", size=13, anchor="start", bold=True))

    render(os.path.join(IMG, "feedback-loop.svg"), W, H, *f)


# ───────────────── Фіг. 2: матриця 2×2 чотирьох топологій ─────────────────
def fig_matrix():
    W, H = 780, 470
    f = [text(W / 2, 30, "Чотири топології = відбір (стовпці) × змішування (рядки)",
              size=15, bold=True)]

    # сітка
    gx, gy = 250, 70          # лівий-верхній кут зони клітинок
    cw, ch = 248, 158         # розмір клітинки
    gap = 14

    # заголовки стовпців (ВІДБІР)
    f.append(text(gx + cw / 2, gy - 30, "ВІДБІР НАПРУГИ", size=13, bold=True, color=FIELD))
    f.append(text(gx + cw / 2, gy - 14, "(паралельно виходу)", size=10, color=MUTED))
    f.append(text(gx + cw + gap + cw / 2, gy - 30, "ВІДБІР СТРУМУ", size=13, bold=True, color=FIELD))
    f.append(text(gx + cw + gap + cw / 2, gy - 14, "(послідовно з виходом)", size=10, color=MUTED))

    # заголовки рядків (ЗМІШУВАННЯ) — вертикально ліворуч
    f.append(text(70, gy + ch / 2, "ЗМІШУВАННЯ", size=13, bold=True, color=NEG))
    f.append(text(70, gy + ch / 2 + 16, "НАПРУГИ", size=12, bold=True, color=NEG))
    f.append(text(70, gy + ch / 2 + 32, "(послідовно)", size=10, color=MUTED))
    f.append(text(70, gy + ch + gap + ch / 2, "ЗМІШУВАННЯ", size=13, bold=True, color=NEG))
    f.append(text(70, gy + ch + gap + ch / 2 + 16, "СТРУМУ", size=12, bold=True, color=NEG))
    f.append(text(70, gy + ch + gap + ch / 2 + 32, "(паралельно)", size=10, color=MUTED))

    cells = [
        # (row, col, заголовок, тип підсилювача, що стабілізує, Zвх, Zвих)
        (0, 0, "ПОСЛІДОВНО-ПАРАЛЕЛЬНА", "підсилювач напруги  (V→V)",
         "стабілізує K = U_вих/U_вх", "Z_вх ↑", "Z_вих ↓"),
        (0, 1, "ПАРАЛЕЛЬНО-ПАРАЛЕЛЬНА", "трансрезистивний  (I→V)",
         "стабілізує R = U_вих/I_вх", "Z_вх ↓", "Z_вих ↓"),
        (1, 0, "ПОСЛІДОВНО-ПОСЛІДОВНА", "трансрезистивний навпаки  (V→I)",
         "стабілізує G = I_вих/U_вх", "Z_вх ↑", "Z_вих ↑"),
        (1, 1, "ПАРАЛЕЛЬНО-ПОСЛІДОВНА", "підсилювач струму  (I→I)",
         "стабілізує K = I_вих/I_вх", "Z_вх ↓", "Z_вих ↑"),
    ]
    for row, col, head, kind, stab, zin, zout in cells:
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        f.append(rect(x, y, cw, ch, fill="#fbfcfd", stroke=INK, sw=1.6, rx=10))
        f.append(text(x + cw / 2, y + 24, head, size=12, bold=True))
        f.append(text(x + cw / 2, y + 48, kind, size=11, color=MUTED))
        f.append(line(x + 18, y + 60, x + cw - 18, y + 60, color="#d6dbe0", sw=1.2))
        f.append(text(x + cw / 2, y + 82, stab, size=11, color=INK))
        # вплив на імпеданси — два чипи
        zin_c = FIELD if "↑" in zin else POS
        zout_c = FIELD if "↑" in zout else POS
        f.append(fitbox(x + 16, y + 102, (cw - 44) / 2, 34, zin, size=12,
                        fill="#f3f5f7", stroke=zin_c, color=INK, bold=True))
        f.append(fitbox(x + 28 + (cw - 44) / 2, y + 102, (cw - 44) / 2, 34, zout, size=12,
                        fill="#f3f5f7", stroke=zout_c, color=INK, bold=True))

    note = ("Послідовне змішування (на вході) ПІДНІМАЄ вхідний опір; паралельне — ОПУСКАЄ.\n"
            "Відбір напруги ОПУСКАЄ вихідний опір (тверде джерело напруги); відбір струму — ПІДНІМАЄ.")
    f.append(fitbox(gx, gy + 2 * ch + gap + 16, 2 * cw + gap, 48, note,
                    size=11, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "topology-matrix.svg"), W, H, *f)


# ─────────── Фіг. 3: дві крайні топології на ОП — наочний контраст ───────────
def opamp(x, y, w=92, h=70, inv_top=True):
    """Трикутник ОП. inv_top=True → «−» зверху, «+» знизу (як у неінверт. і трансімп.)."""
    out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#fff" stroke="%s" stroke-width="1.8"/>'
           % (x, y, x, y + h, x + w, y + h / 2, INK)]
    yt, yb = y + h * 0.28, y + h * 0.72
    if inv_top:
        out.append(text(x + 13, yt + 5, "−", size=15, bold=True, color=NEG))
        out.append(text(x + 13, yb + 5, "+", size=15, bold=True, color=POS))
    else:
        out.append(text(x + 13, yt + 5, "+", size=15, bold=True, color=POS))
        out.append(text(x + 13, yb + 5, "−", size=15, bold=True, color=NEG))
    return "".join(out), (x, yt, yb, x + w, y + h / 2)  # вузли: вх_лівий, верх, низ, вихід_x, вихід_y


def res_h(x, y, w, label):
    out = [rect(x, y - 9, w, 18, fill="#eef1f5", stroke=INK, sw=1.5, rx=3)]
    out.append(text(x + w / 2, y - 15, label, size=10, color=MUTED))
    return "".join(out)


def ground(x, y):
    out = [line(x, y, x, y + 7, color=INK, sw=1.6)]
    out.append(line(x - 11, y + 7, x + 11, y + 7, color=INK, sw=2.0))
    out.append(line(x - 6, y + 12, x + 6, y + 12, color=INK, sw=1.8))
    out.append(line(x - 2, y + 17, x + 2, y + 17, color=INK, sw=1.6))
    return "".join(out)


def fig_two_extremes():
    W, H = 800, 410
    f = [text(W / 2, 28, "Та сама петля, протилежні наслідки: послідовно-паралельна проти паралельно-паралельної",
              size=14, bold=True)]

    # ── Ліва панель: неінвертуючий = послідовно-паралельна (відбір напруги, змішування напруги) ──
    f.append(text(200, 60, "ПОСЛІДОВНО-ПАРАЛЕЛЬНА", size=13, bold=True))
    f.append(text(200, 78, "неінвертуючий: вхід — у «+», ЗЗ — у «−»", size=10, color=MUTED))
    op, (xl, yt, yb, xo, yo) = opamp(170, 110, inv_top=True)
    f.append(op)
    # вхід у «+» (низ) — послідовне змішування: сигнал і ЗЗ — РІЗНІ виводи
    f.append(arrow(70, yb, xl, yb, color=INK, sw=1.8))
    f.append(text(58, yb + 5, "U_вх", size=12, bold=True, anchor="end"))
    # вихід
    f.append(line(xo, yo, 340, yo, color=INK, sw=1.8))
    f.append(pickoff(300, yo))
    f.append(text(348, yo + 5, "U_вих", size=12, bold=True, anchor="start"))
    # дільник ЗЗ: від виходу через Rf у вузол «−», звідти Rg на землю
    nx = xl - 4            # вузол «−» (вхід зверху)
    fb_y = 250
    f.append(line(300, yo, 300, fb_y, color=INK, sw=1.8))
    f.append(res_h(232, fb_y, 56, "Rf"))
    f.append(line(232, fb_y, 150, fb_y, color=INK, sw=1.8))
    f.append(line(150, fb_y, 150, yt, color=INK, sw=1.8))
    f.append(line(150, yt, xl, yt, color=INK, sw=1.8))
    f.append(pickoff(150, fb_y))
    f.append(res_h(94, fb_y, 56, "Rg"))
    f.append(line(94, fb_y, 70, fb_y, color=INK, sw=1.8))
    f.append(ground(70, fb_y))
    # підпис-наслідок
    f.append(fitbox(60, 320, 300, 56,
                    "Відбір НАПРУГИ → Z_вих ↓ (тверда напруга).\n"
                    "Змішування ПОСЛІДОВНЕ → Z_вх ↑ (майже не вантажить джерело).",
                    size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    # роздільник
    f.append(line(W / 2 + 4, 92, W / 2 + 4, 300, color="#d6dbe0", sw=1.4, dash="5,5"))

    # ── Права панель: трансімпедансний = паралельно-паралельна (відбір напруги, змішування струму) ──
    f.append(text(600, 60, "ПАРАЛЕЛЬНО-ПАРАЛЕЛЬНА", size=13, bold=True))
    f.append(text(600, 78, "трансімпедансний: струм входить у «−»", size=10, color=MUTED))
    op2, (xl2, yt2, yb2, xo2, yo2) = opamp(560, 110, inv_top=True)
    f.append(op2)
    # «+» на землю
    f.append(line(xl2, yb2, xl2 - 26, yb2, color=INK, sw=1.8))
    f.append(ground(xl2 - 26, yb2))
    # вхідний струм у вузол «−» (верх) — паралельне змішування: сигнал-струм і ЗЗ-струм в ОДИН вузол
    nx2 = xl2
    f.append(arrow(455, yt2, nx2, yt2, color=POS, sw=2.0))
    f.append(text(450, yt2 + 5, "I_вх", size=12, bold=True, anchor="end", color=POS))
    f.append(pickoff(nx2, yt2))
    # вихід
    f.append(line(xo2, yo2, 730, yo2, color=INK, sw=1.8))
    f.append(pickoff(700, yo2))
    f.append(text(738, yo2 + 5, "U_вих", size=12, bold=True, anchor="start"))
    # Rf від виходу назад у вузол «−» (один-єдиний резистор)
    f.append(line(700, yo2, 700, 250, color=INK, sw=1.8))
    f.append(res_h(600, 250, 60, "Rf"))
    f.append(line(600, 250, nx2, 250, color=INK, sw=1.8))
    f.append(line(nx2, 250, nx2, yt2, color=INK, sw=1.8))
    f.append(fitbox(450, 320, 320, 56,
                    "Відбір НАПРУГИ → Z_вих ↓.\n"
                    "Змішування ПАРАЛЕЛЬНЕ → Z_вх ↓ (≈0, віртуальна земля — ідеальна для струму).",
                    size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "two-extremes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_matrix()
    fig_two_extremes()
    print("OK: feedback-loop.svg, topology-matrix.svg, two-extremes.svg")
