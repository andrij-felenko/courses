# -*- coding: utf-8 -*-
"""Фігури до вставки math-nodal-mna.md (тема «Симуляція кіл (SPICE)»).

Окремий генератор, щоб не конфліктувати з паралельним редагуванням figs.py.
  mna-stamp.svg  — резистор «штампує» ±G у чотири клітинки матриці за номерами вузлів
  mna-block.svg  — облямована блок-система MNA: джерело напруги додає рядок і невідомий струм
Запуск:  python figs_mna.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def mna_stamp():
    """Резистор між вузлами a,b «штампує» ±G у чотири клітинки матриці провідностей."""
    W, H = 780, 400
    p = []

    # ── ліворуч: сам резистор між двома вузлами ─────────────────────────────
    ax, ay = 80, 150
    bx = 260
    p.append(circle(ax, ay, 7, fill=FIELD, stroke=INK, sw=2))
    p.append(circle(bx, ay, 7, fill=FIELD, stroke=INK, sw=2))
    p.append(text(ax, ay - 18, "вузол a", size=13, bold=True, color=FIELD))
    p.append(text(bx, ay - 18, "вузол b", size=13, bold=True, color=FIELD))
    # тіло резистора (зиґзаґ)
    zx = [ax + 20, ax + 34, ax + 52, ax + 70, ax + 88, ax + 106, ax + 124, bx - 20]
    zy = [ay, ay - 12, ay + 12, ay - 12, ay + 12, ay - 12, ay + 12, ay]
    zpts = list(zip(zx, zy))
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in zpts) +
             '" fill="none" stroke="%s" stroke-width="2.2"/>' % INK)
    p.append(line(ax + 7, ay, ax + 20, ay, color=INK, sw=2.2))
    p.append(line(bx - 20, ay, bx - 7, ay, color=INK, sw=2.2))
    p.append(text((ax + bx) / 2, ay + 34, "провідність G = 1/R", size=12, color="#b8732e", bold=True))
    p.append(text((ax + bx) / 2, ay + 52, "струм I = G·(Uₐ − U_b)", size=12, color=MUTED))

    # стрілка «штампує в матрицю»
    p.append(arrow(bx + 24, ay, 408, ay, color=POS, sw=2.2))
    p.append(text((bx + 24 + 408) / 2, ay - 12, "штампує", size=13, bold=True, color=POS))

    # ── праворуч: матриця G з чотирма клітинками ────────────────────────────
    gx, gy = 486, 92
    cell = 66
    rows = ["…", "a", "b", "…"]
    for j, c in enumerate(rows):
        p.append(text(gx + cell / 2 + j * cell, gy - 10, c, size=13, color=MUTED, bold=(c != "…")))
    for i, r in enumerate(rows):
        p.append(text(gx - 10, gy + cell / 2 + i * cell + 5, r, size=13, color=MUTED,
                      anchor="end", bold=(r != "…")))
    # клітинки (діагональ +G, позадіагональ −G)
    hot = {(1, 1): "+G", (2, 2): "+G", (1, 2): "−G", (2, 1): "−G"}
    for i in range(4):
        for j in range(4):
            x = gx + j * cell
            y = gy + i * cell
            val = hot.get((i, j))
            fc = "#fdecea" if val and val.startswith("+") else ("#eaf0fd" if val else BG)
            sc = POS if (val and val.startswith("+")) else (NEG if val else "#cfd6dd")
            p.append(rect(x, y, cell, cell, fill=fc, stroke=sc, sw=2 if val else 1, rx=4))
            if val:
                p.append(text(x + cell / 2, y + cell / 2 + 6, val, size=17, bold=True,
                              color=POS if val.startswith("+") else NEG))
    p.append(text(gx + 2 * cell, gy + 4 * cell + 22, "матриця провідностей G", size=13,
                  bold=True, color=INK))

    b, _, _ = textbox(W / 2, 378,
                      "Кожен елемент додає внесок лише в клітинки за номерами своїх вузлів — незалежно від решти.\n"
                      "Резистор кладе +G на діагональ обох вузлів і −G у дві позадіагональні клітинки. Матриця — сума таких штампів.",
                      size=12, fill="#fdf3e6", stroke="#b8732e")
    p.append(b)
    render(os.path.join(OUT, 'mna-stamp.svg'), W, H, *p,
           title="Штамп резистора: ±G у чотири клітинки матриці")


def mna_block():
    """Облямована блок-система MNA: до вузлових рівнянь додано рядок і струм джерела напруги."""
    W, H = 800, 430
    p = []

    mx, my = 150, 92
    Gw, Gh = 250, 190        # блок G (вузли × вузли)
    Bw = 78                  # ширина стовпця B / висота рядка C

    # G
    p.append(rect(mx, my, Gw, Gh, fill="#fdf3e6", stroke="#b8732e", sw=2.2))
    p.append(mtext(mx + Gw / 2, my + Gh / 2 - 8, "G", size=26, bold=True, color="#b8732e"))
    p.append(mtext(mx + Gw / 2, my + Gh / 2 + 24, "провідності вузлів\n(резистори, дотичні)", size=11, color=MUTED))
    # B (правий вузький стовпець)
    p.append(rect(mx + Gw, my, Bw, Gh, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(mtext(mx + Gw + Bw / 2, my + Gh / 2 - 2, "B", size=22, bold=True, color=NEG))
    p.append(mtext(mx + Gw + Bw / 2, my + Gh / 2 + 20, "±1", size=13, color=MUTED))
    # C (нижній вузький рядок)
    p.append(rect(mx, my + Gh, Gw, Bw, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(mtext(mx + Gw / 2, my + Gh + Bw / 2 - 2, "C", size=20, bold=True, color=NEG))
    p.append(mtext(mx + Gw / 2, my + Gh + Bw / 2 + 18, "±1 (той самий Uₐ − U_b)", size=10.5, color=MUTED))
    # D (кут)
    p.append(rect(mx + Gw, my + Gh, Bw, Bw, fill=BG, stroke=LINE, sw=1.6))
    p.append(mtext(mx + Gw + Bw / 2, my + Gh + Bw / 2 + 6, "0", size=20, bold=True, color=MUTED))

    # вектор невідомих
    p.append(text(mx + Gw + Bw + 14, my + Gh / 2 + Bw / 2, "·", size=30, color=INK))
    vx = mx + Gw + Bw + 30
    vw = 70
    p.append(rect(vx, my, vw, Gh, fill=BG, stroke=FIELD, sw=2))
    p.append(mtext(vx + vw / 2, my + Gh / 2 - 6, "v", size=22, bold=True, color=FIELD))
    p.append(mtext(vx + vw / 2, my + Gh / 2 + 18, "напруги\nвузлів", size=11, color=MUTED))
    p.append(rect(vx, my + Gh, vw, Bw, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(mtext(vx + vw / 2, my + Gh + Bw / 2 + 2, "j", size=18, bold=True, color=FIELD))

    # знак =
    ex = vx + vw + 18
    p.append(text(ex, my + Gh / 2 + Bw / 2, "=", size=30, color=INK))

    # права частина
    rx = ex + 18
    rw = 74
    p.append(rect(rx, my, rw, Gh, fill=BG, stroke=MUTED, sw=1.8))
    p.append(mtext(rx + rw / 2, my + Gh / 2 - 4, "i", size=22, bold=True, color=INK))
    p.append(mtext(rx + rw / 2, my + Gh / 2 + 20, "струми\nджерел", size=10.5, color=MUTED))
    p.append(rect(rx, my + Gh, rw, Bw, fill="#f4f6f8", stroke=MUTED, sw=1.8))
    p.append(mtext(rx + rw / 2, my + Gh + Bw / 2 + 2, "E", size=18, bold=True, color=INK))

    # підписи блоків збоку
    p.append(text(mx - 12, my + Gh / 2, "вузли", size=12, color=MUTED, anchor="end"))
    p.append(mtext(mx - 12, my + Gh + Bw / 2 - 6, "джерело\nнапруги", size=11, color=NEG, anchor="end"))

    b, _, _ = textbox(W / 2, 405,
                      "«Модифікація»: напруг вузлів (v) для джерела напруги замало — його струм j теж невідомий.\n"
                      "Тому систему облямовують: стовпець B і рядок-обмеження C (Uₐ − U_b = E). Так входить і котушка.",
                      size=12, fill="#eef2fb", stroke=NEG)
    p.append(b)
    render(os.path.join(OUT, 'mna-block.svg'), W, H, *p,
           title="Облямована система MNA: зайвий рядок і зайвий струм")


if __name__ == '__main__':
    mna_stamp()
    mna_block()
    print("OK: 2 figures ->", OUT)
