# -*- coding: utf-8 -*-
"""Фігури Розділу 3.2 «Енергія: чому горить і гріє». Чистий Python без залежностей → SVG у ./img/."""
from pathlib import Path

IMG = Path(__file__).resolve().parent / "img"
IMG.mkdir(exist_ok=True)

FONT = 'font-family="Segoe UI, Arial, sans-serif"'


def svg_open(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs>\n'
            '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker>\n'
            '</defs>\n'
            '<rect width="%d" height="%d" fill="white"/>\n' % (w, h, w, h, w, h))


def text(x, y, s, size=15, anchor="middle", weight="normal", fill="#222"):
    return ('<text x="%s" y="%s" %s font-size="%s" text-anchor="%s" font-weight="%s" fill="%s">%s</text>\n'
            % (x, y, FONT, size, anchor, weight, fill, s))


def arrow(x1, y1, x2, y2, color="#444", w=2):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"/>\n' % (x1, y1, x2, y2, color, w))


def path(d, stroke="#444", w=2.5, fill="none"):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (d, fill, stroke, w)


GREEN = "#2f9e54"
REDO = "#d9533c"
ORANGE = "#e08a2c"


def fig_bond_budget():
    s = svg_open(960, 380)
    s += text(480, 34, "енергія реакції — це бухгалтерія зв'язків", size=16, weight="bold")

    # ── ліва колонка: РОЗІРВАТИ старі = вкласти ──
    s += text(230, 76, "1. розірвати старі зв'язки", size=14.5, weight="bold", fill=REDO)
    s += text(230, 98, "= ВКЛАСТИ енергію", size=13, fill=REDO)
    s += '<rect x="120" y="120" width="220" height="60" rx="10" fill="#fbe9e4" stroke="#d9533c"/>\n'
    s += arrow(150, 200, 150, 150, color=REDO, w=2)
    s += arrow(230, 200, 230, 150, color=REDO, w=2)
    s += arrow(310, 200, 310, 150, color=REDO, w=2)
    s += text(230, 152, "потрібен поштовх", size=13, fill="#7a2d20")
    s += text(230, 228, "(як розчепити зчеплені руки)", size=12, fill="#888")

    s += text(420, 150, "потім", size=13, fill="#666")
    s += arrow(395, 165, 455, 165, color="#666", w=2)

    # ── права колонка: УТВОРИТИ нові = вивільнити ──
    s += text(700, 76, "2. утворити нові зв'язки", size=14.5, weight="bold", fill=GREEN)
    s += text(700, 98, "= ВИВІЛЬНИТИ енергію", size=13, fill=GREEN)
    s += '<rect x="590" y="120" width="220" height="60" rx="10" fill="#e4f4ea" stroke="#2f9e54"/>\n'
    s += arrow(620, 150, 620, 200, color=GREEN, w=2)
    s += arrow(700, 150, 700, 200, color=GREEN, w=2)
    s += arrow(780, 150, 780, 200, color=GREEN, w=2)
    s += text(700, 228, "(руки зчепилися — стало спокійніше)", size=12, fill="#888")

    # ── підсумок: різниця ──
    s += '<line x1="80" y1="280" x2="880" y2="280" stroke="#ccc" stroke-width="1.4"/>\n'
    s += text(270, 312, "вивільнилось БІЛЬШЕ, ніж вклали", size=14, fill=GREEN, weight="bold")
    s += text(270, 336, "→ надлишок виходить теплом (екзо): горіння, грілка", size=12.5, fill="#444")
    s += text(700, 312, "вклали БІЛЬШЕ, ніж вивільнилось", size=14, fill="#1f6f9e", weight="bold")
    s += text(700, 336, "→ реакція тягне тепло ззовні (ендо): холодний пакет", size=12.5, fill="#444")

    s += "</svg>\n"
    (IMG / "fig-3-2-1-1-bond-budget.svg").write_text(s, encoding="utf-8")


def fig_activation_barrier():
    s = svg_open(960, 420)
    s += text(480, 34, "чому дрова не спалахують самі: бар'єр активації", size=16, weight="bold")

    # осі
    s += arrow(90, 360, 90, 70, color="#444", w=2)
    s += text(70, 80, "енергія", size=13, anchor="end", fill="#444")
    s += arrow(90, 360, 900, 360, color="#444", w=2)
    s += text(880, 380, "хід реакції →", size=13, anchor="end", fill="#444")

    # крива з горбом: старт високо-ліворуч (дрова+кисень), горб, фініш низько (попіл+тепло)
    s += path("M 130 200 C 260 200, 300 110, 420 110 C 540 110, 560 320, 760 320 L 850 320",
              stroke="#b3541e", w=3)

    # рівні
    s += '<line x1="120" y1="200" x2="430" y2="200" stroke="#888" stroke-width="1.2" stroke-dasharray="5,4"/>\n'
    s += text(135, 192, "дрова + кисень", size=12.5, anchor="start", fill="#555")
    s += '<line x1="430" y1="320" x2="860" y2="320" stroke="#888" stroke-width="1.2" stroke-dasharray="5,4"/>\n'
    s += text(845, 342, "попіл + дим", size=12.5, anchor="end", fill="#555")

    # бар'єр
    s += '<line x1="420" y1="110" x2="420" y2="200" stroke="#d9533c" stroke-width="2"/>\n'
    s += arrow(420, 200, 420, 116, color=REDO, w=2)
    s += text(450, 150, "бар'єр: спершу треба", size=12.5, anchor="start", fill=REDO)
    s += text(450, 168, "ВКЛАСТИ — чиркнути,", size=12.5, anchor="start", fill=REDO)
    s += text(450, 186, "піднести сірник", size=12.5, anchor="start", fill=REDO)

    # виграш
    s += '<line x1="800" y1="200" x2="800" y2="320" stroke="#2f9e54" stroke-width="2"/>\n'
    s += arrow(800, 200, 800, 314, color=GREEN, w=2)
    s += text(770, 260, "а потім скочується само —", size=12.5, anchor="end", fill=GREEN)
    s += text(770, 278, "виділяє більше, ніж вклали", size=12.5, anchor="end", fill=GREEN)

    s += text(480, 405, "дрова лежать роками: без поштовху через горб реакція не починається",
              size=12.5, fill="#777")

    s += "</svg>\n"
    (IMG / "fig-3-2-1-2-activation-barrier.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_bond_budget()
    fig_activation_barrier()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))
