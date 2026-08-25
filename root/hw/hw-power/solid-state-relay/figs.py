# -*- coding: utf-8 -*-
"""Фігури до вставки «Модуль твердотільного реле (SSR-xxDA)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_inside():
    """Що під заливкою модуля: керування / оптична межа / детектор нуля / силовий ключ / підошва."""
    W, H = 860, 420
    f = []

    # ── керувальний бік (ліворуч) ──
    lx, ly, lw, lh = 40, 70, 300, 290
    f.append(rect(lx, ly, lw, lh, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(lx + lw / 2, ly - 8, "керування (вхід DC)", size=13, color=NEG, bold=True))
    # вивід 3 (+) і 4 (−)
    f.append(line(lx - 26, ly + 36, lx, ly + 36, color=INK, sw=2))
    f.append(text(lx - 30, ly + 40, "3  DC+", size=11, color=POS, anchor="end", bold=True))
    f.append(line(lx - 26, ly + 76, lx, ly + 76, color=INK, sw=2))
    f.append(text(lx - 30, ly + 80, "4  DC−", size=11, color=NEG, anchor="end", bold=True))
    # вбудований резистор
    f.append(rect(lx + 30, ly + 50, 70, 24, fill=BG, stroke=INK, sw=1.4))
    f.append(text(lx + 65, ly + 67, "R вбуд.", size=11, color=INK))
    f.append(text(lx + lw / 2, ly + 110, "обмежує струм →", size=11, color=MUTED))
    f.append(text(lx + lw / 2, ly + 128, "≈ 10 мА від 3–32 В", size=11, color=MUTED))
    # світлодіод оптопари
    f.append(circle(lx + lw / 2, ly + 188, 26, fill="#fff6e0", stroke="#b9770e", sw=1.8))
    f.append(text(lx + lw / 2, ly + 193, "LED", size=13, color="#9c6a16", bold=True))
    f.append(text(lx + lw / 2, ly + 240, "світлодіод світить", size=11, color=MUTED))
    f.append(text(lx + lw / 2, ly + 258, "крізь оптичну межу", size=11, color=MUTED))

    # ── оптична межа (по центру) ──
    mx = lx + lw + 40
    f.append(line(mx, ly - 4, mx, ly + lh + 4, color=FIELD, sw=2.4, dash="7 5"))
    f.append(text(mx, ly - 22, "оптична межа", size=12, color=FIELD, bold=True))
    f.append(text(mx, ly - 6, "(гальванічна розв'язка)", size=10, color=MUTED))
    # промінь світла через межу
    f.append(arrow(lx + lw / 2 + 30, ly + 188, mx + 60, ly + 188, color="#b9770e", sw=2))

    # ── силовий бік (праворуч) ──
    rx = mx + 40
    rw, ry, rh = W - rx - 40, ly, lh
    f.append(rect(rx, ry, rw, rh, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(rx + rw / 2, ry - 8, "сила (вихід ~)", size=13, color=POS, bold=True))
    # фотоприймач
    f.append(circle(rx + 50, ry + 50, 20, fill=BG, stroke=INK, sw=1.6))
    f.append(text(rx + 50, ry + 55, "фото", size=10, color=INK))
    f.append(arrow(rx + 4, ry + 50, rx + 28, ry + 50, color="#b9770e", sw=1.8))
    # детектор нуля
    f.append(rect(rx + 90, ry + 36, 90, 30, fill=BG, stroke=INK, sw=1.4))
    f.append(text(rx + 135, ry + 56, "детектор 0", size=10, color=INK))
    # силовий ключ (симістор)
    f.append(rect(rx + 30, ry + 110, 120, 50, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(rx + 90, ry + 132, "симістор", size=12, color=POS, bold=True))
    f.append(text(rx + 90, ry + 150, "(або 2 SCR)", size=10, color=MUTED))
    # RC-снабер
    f.append(rect(rx + 170, ry + 110, 70, 50, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(rx + 205, ry + 132, "RC", size=11, color=INK))
    f.append(text(rx + 205, ry + 150, "снабер", size=9, color=MUTED))
    # силові виводи 1,2
    f.append(line(rx + rw, ry + 130, rx + rw + 26, ry + 130, color=INK, sw=2.4))
    f.append(text(rx + rw + 30, ry + 118, "1 ~", size=11, color=INK, anchor="start", bold=True))
    f.append(text(rx + rw + 30, ry + 150, "2 ~", size=11, color=INK, anchor="start", bold=True))
    f.append(line(rx + rw, ry + 158, rx + rw + 26, ry + 158, color=INK, sw=2.4))
    # тепловідвідна підошва
    f.append(rect(rx + 16, ry + rh - 44, rw - 32, 26, fill="#d9dee3", stroke=INK, sw=1.6))
    f.append(text(rx + rw / 2, ry + rh - 26, "металева підошва (тепловідвід)", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "inside.svg"), W, H, *f,
           title="Що під заливкою модуля SSR")


def fig_heat():
    """Чому номінальний струм вимагає радіатора: P = 1.2 В × I; стовпчики тепла й межа корпусу."""
    W, H = 820, 430
    f = []

    f.append(text(W / 2, 52, "P_тепло = 1.2 В × I_навантаження", size=15, color=INK, bold=True))

    # осі стовпчастого
    bx0, by0, plot_w, plot_h = 90, 350, 640, 240
    f.append(line(bx0, by0, bx0 + plot_w, by0, color=INK, sw=1.8))            # вісь X
    f.append(line(bx0, by0, bx0, by0 - plot_h, color=INK, sw=1.8))            # вісь Y
    f.append(text(bx0 - 12, by0 - plot_h + 4, "P, Вт", size=11, color=MUTED, anchor="end"))

    # межа корпусу без радіатора ~3 Вт
    pmax = 50.0
    y_limit = by0 - (3.0 / pmax) * plot_h
    f.append(line(bx0, y_limit, bx0 + plot_w, y_limit, color=FIELD, sw=1.6, dash="6 5"))
    f.append(text(bx0 + plot_w, y_limit - 6, "межа корпусу без радіатора ≈ 3 Вт",
                  size=10, color=FIELD, anchor="end", italic=True))

    bars = [(2.5, "2.5 А", "сам корпус"), (10, "10 А", "12 Вт"),
            (25, "25 А", "30 Вт"), (40, "40 А", "48 Вт")]
    n = len(bars)
    slot = plot_w / (n + 0.5)
    bw = slot * 0.5
    for i, (amp, lab, note) in enumerate(bars):
        cx = bx0 + slot * (i + 0.7)
        p = 1.2 * amp
        bh = (p / pmax) * plot_h
        col = FIELD if p <= 3.0 else (POS if p >= 24 else "#b9770e")
        f.append(rect(cx - bw / 2, by0 - bh, bw, bh, fill=col, stroke=INK, sw=1.2, rx=3))
        f.append(text(cx, by0 - bh - 8, "%.0f Вт" % p, size=12, color=INK, bold=True))
        f.append(text(cx, by0 + 18, lab, size=12, color=INK, bold=True))
        f.append(text(cx, by0 + 34, note, size=9, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Номінал «40 А» = 48 Вт у кристалі — лише з масивним радіатором (часто й з обдувом).",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "heat.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_heat()
    print("OK: inside.svg, heat.svg")
