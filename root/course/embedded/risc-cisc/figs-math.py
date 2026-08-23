# -*- coding: utf-8 -*-
# Фігури до вставки math-iron-law.md (залізний закон і точка перелому).
# Окремий файл, щоб не чіпати figs.py / figs-d.py теми.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = "#1f47b5"   # CISC
GREEN  = "#1f8a3b"   # RISC
F_BLUE = "#f3f5fd"
F_GRN  = "#eef7ee"
F_GREY = "#f4f5f7"


# ── law-factors: розклад часу на три множники, дві протилежні ставки ───────────
# Ідея: показати той самий добуток N×CPI×T як шкалу з трьома блоками,
# і стрілками — куди тисне кожна філософія (CISC ↓N, RISC ↓CPI ↓T).
def fig_law_factors():
    W, H = 760, 330
    p = []
    p.append(text(W / 2, 42, "Один добуток — три множники, дві протилежні ставки", size=14, bold=True))

    # центральний рядок-формула з трьох блоків
    y = 120
    bx, bw, gap = 120, 150, 20
    labels = [("N", "команд\nу програмі", INK),
              ("CPI", "тактів\nна команду", INK),
              ("T", "тривалість\nтакту", INK)]
    xs = []
    for i, (sym, sub, col) in enumerate(labels):
        x = bx + i * (bw + gap)
        xs.append(x + bw / 2)
        p.append(rect(x, y, bw, 66, fill=F_GREY, stroke=INK, sw=2, rx=8))
        p.append(text(x + bw / 2, y + 30, sym, size=20, bold=True))
        p.append(mtext(x + bw / 2, y + 48, sub, size=9.5, color=MUTED))
        if i < 2:
            p.append(text(x + bw + gap / 2, y + 38, "×", size=20, bold=True))
    p.append(text(bx - 26, y + 40, "час =", size=15, bold=True, anchor="end"))

    # стрілки-ставки: CISC тисне N; RISC тисне CPI і T
    # CISC — згори, синім
    p.append(text(W / 2, y - 30, "CISC: тисну N (одна потужна команда замість п'яти)",
                  size=11, color=BLUE, bold=True))
    p.append(arrow(xs[0], y - 16, xs[0], y - 2, color=BLUE, sw=2))
    # RISC — знизу, зеленим
    p.append(arrow(xs[1], y + 82, xs[1], y + 68, color=GREEN, sw=2))
    p.append(arrow(xs[2], y + 82, xs[2], y + 68, color=GREEN, sw=2))
    p.append(text(W / 2, y + 104, "RISC: тисну CPI і T (прості команди · просте швидке залізо)",
                  size=11, color=GREEN, bold=True))

    p.append(text(W / 2, y + 150, "CISC виграє один множник і платить двома; RISC — навпаки.",
                  size=11.5, bold=True))
    p.append(text(W / 2, y + 174,
                  "Хто переможе — вирішує, наскільки сильно кожен множник піддається.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "iron-factors.svg"), W, H, *p)


# ── worked bars: розкладені стовпчики часу CISC vs RISC ───────────────────────
# Ідея: кожен стовпчик — площа = N×CPI×T, підписана трьома числами; поруч висновок.
def fig_worked():
    W, H = 720, 430
    p = []
    p.append(text(W / 2, 40, "Той самий обсяг роботи: рахуємо час обома шляхами", size=13.5, bold=True))

    base = 300          # нульова лінія стовпчиків
    scale = 245.0 / 560 # 560 — найбільший час; лишаємо зверху місце під підпис
    p.append(line(70, base, 690, base, color=INK, sw=1.6))
    p.append(text(48, base, "0", size=10, color=MUTED, anchor="end"))

    def bar(cx, t, color, fill, title, nums):
        h = t * scale
        p.append(rect(cx - 70, base - h, 140, h, fill=fill, stroke=color, sw=2, rx=6))
        p.append(text(cx, base - h - 12, "%.0f од. часу" % t, size=13, bold=True, color=color))
        p.append(text(cx, base + 20, title, size=12.5, bold=True, color=color))
        p.append(text(cx, base + 40, nums, size=10.5, color=MUTED))

    bar(230, 560, BLUE, F_BLUE, "CISC", "N=100 · CPI=4 · T=1.4")
    bar(500, 143, GREEN, F_GRN, "RISC", "N=130 · CPI=1.1 · T=1.0")

    # висновок
    p.append(text(W / 2, base + 74,
                  "RISC утричі з половиною швидший (560 / 143 ≈ 3.9),",
                  size=12, bold=True))
    p.append(text(W / 2, base + 96,
                  "хоча виконує на 30% БІЛЬШЕ команд.", size=12, bold=True, color=GREEN))
    p.append(text(W / 2, base + 118,
                  "Програш у N (×1.3) розчинився у виграші CPI·T (×5.1).",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "iron-worked.svg"), W, H, *p)


# ── inequality line: числова вісь із точкою перелому ──────────────────────────
# Ідея: горизонтальна вісь — відношення роботи (CPIc·Tc)/(CPIr·Tr).
# Зліва від точки N_ratio виграє CISC, справа — RISC. Показуємо, де стоїть приклад.
def fig_breakeven():
    W, H = 760, 300
    p = []
    p.append(text(W / 2, 40, "Точка перелому: коли виграш CPI·T переважує програш N", size=13.5, bold=True))

    ax0, ax1, ay = 90, 690, 150
    p.append(arrow(ax0 - 10, ay, ax1 + 20, ay, color=INK, sw=1.8))
    p.append(text(ax1 + 24, ay + 4, "виграш\nу роботі", size=9.5, color=INK, anchor="start"))

    # позначка N_ratio = 1.3 (поріг перелому для цього прикладу)
    def tick(val, x, lab, col, up=True):
        p.append(line(x, ay - 7, x, ay + 7, color=col, sw=2))
        dy = -16 if up else 26
        p.append(text(x, ay + dy, lab, size=11, color=col, bold=True))

    # шкала: 1.0 .. 5.5
    lo, hi = 1.0, 5.5
    def X(v):
        return ax0 + (v - lo) / (hi - lo) * (ax1 - ax0)
    for v in (1, 2, 3, 4, 5):
        p.append(line(X(v), ay - 4, X(v), ay + 4, color=MUTED, sw=1))
        p.append(text(X(v), ay + 20, "%d×" % v, size=9.5, color=MUTED))

    # поріг = N_ratio
    xb = X(1.3)
    p.append(line(xb, ay - 40, xb, ay + 40, color=INK, sw=2, dash="4,4"))
    p.append(text(xb, ay - 48, "поріг = приріст N (×1.3)", size=10.5, bold=True))

    # зони
    p.append(rect(ax0, ay - 34, xb - ax0, 26, fill=F_BLUE, stroke=BLUE, sw=1.3, rx=5))
    p.append(text((ax0 + xb) / 2, ay - 16, "виграє CISC", size=10.5, color=BLUE, bold=True))
    p.append(rect(xb, ay - 34, ax1 - xb, 26, fill=F_GRN, stroke=GREEN, sw=1.3, rx=5))
    p.append(text((xb + ax1) / 2, ay - 16, "виграє RISC", size=10.5, color=GREEN, bold=True))

    # де стоїть приклад: 5.1×
    xe = X(5.09)
    p.append(circle(xe, ay, 7, fill=GREEN, stroke=INK, sw=1.5))
    p.append(text(xe, ay + 30, "наш приклад: 5.1×", size=10.5, color=GREEN, bold=True))
    p.append(text(xe, ay + 48, "далеко у зоні RISC", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 26,
                  "RISC виграє ⟺ (виграш CPI·T)  >  (приріст N). Тут 5.1 > 1.3 — з великим запасом.",
                  size=11.5, bold=True))
    render(os.path.join(OUT, "iron-breakeven.svg"), W, H, *p)


# ── flip: два сценарії, де нерівність перевертається ──────────────────────────
# Ідея: дві панелі — (1) CPI·T зрівнялися → лишився тільки N, виграє CISC;
# (2) I-fetch-bound: час = байти коду, щільніший CISC виграє.
def fig_flip():
    W, H = 780, 330
    p = []
    p.append(text(W / 2, 40, "Два випадки, де терези хиляться до CISC", size=14, bold=True))

    def panel(x0, title, sub, cisc_t, risc_t, unit):
        w = 340
        p.append(rect(x0, 66, w, 210, fill=F_GREY, stroke=INK, sw=1.6, rx=10))
        p.append(text(x0 + w / 2, 90, title, size=12.5, bold=True))
        p.append(text(x0 + w / 2, 110, sub, size=10, color=MUTED, italic=True))
        # два міні-стовпчики
        base = 240
        sc = 120.0 / max(cisc_t, risc_t)
        for cx, t, col, fill, lab in ((x0 + 110, cisc_t, BLUE, F_BLUE, "CISC"),
                                      (x0 + 230, risc_t, GREEN, F_GRN, "RISC")):
            h = t * sc
            p.append(rect(cx - 40, base - h, 80, h, fill=fill, stroke=col, sw=2, rx=5))
            p.append(text(cx, base - h - 10, "%g" % t, size=11.5, bold=True, color=col))
            p.append(text(cx, base + 18, lab, size=11, bold=True, color=col))
        winner = "CISC" if cisc_t < risc_t else "RISC"
        p.append(text(x0 + w / 2, 266, "виграє %s (%s)" % (winner, unit),
                      size=11, bold=True, color=BLUE if winner == "CISC" else GREEN))

    panel(30, "1. CPI·T зрівнялися (обидва конвеєрні, та сама частота)",
          "тоді час ∝ N — лишається сам приріст команд",
          100, 130, "менший N")
    panel(410, "2. Час з'їдає вибірка коду з повільної пам'яті",
          "важать байти коду N×розмір — щільніший CISC",
          300, 520, "щільніший код")

    p.append(text(W / 2, H - 26,
                  "Урок: RISC перемагає не завжди — лише поки його виграш у CPI·T переважує приріст N.",
                  size=11.5, bold=True))
    render(os.path.join(OUT, "iron-flip.svg"), W, H, *p)


if __name__ == "__main__":
    fig_law_factors()
    fig_worked()
    fig_breakeven()
    fig_flip()
    print("OK: math figures written to", OUT)
