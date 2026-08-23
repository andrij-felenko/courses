# -*- coding: utf-8 -*-
"""Фігури теми «Джерело струму хвоста» (root/course/embedded/kola/tail-current-source).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми у ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── Фігура 1: резистор-хвіст проти ідеального джерела струму ─────────────────
def fig_resistor_vs_source():
    W, H = 760, 380
    f = []
    # дві осі I(V) поряд: ліворуч резистор (похила лінія), праворуч джерело (плеската)
    def axes(x0, y0, w, h, caption):
        a = []
        a.append(line(x0, y0, x0, y0 - h, INK, 1.8))          # вісь I (вгору)
        a.append(line(x0, y0, x0 + w, y0, INK, 1.8))          # вісь V (праворуч)
        a.append(text(x0 - 8, y0 - h + 4, "I", 13, MUTED, "end", italic=True))
        a.append(text(x0 + w, y0 + 18, "U на хвості", 12, MUTED, "end"))
        a.append(text(x0 + w / 2, y0 - h - 14, caption, 14, INK, "middle", bold=True))
        return a

    # ліворуч: резистор
    lx, ly, lw, lh = 90, 300, 230, 210
    f += axes(lx, ly, lw, lh, "Хвіст — резистор")
    # похила лінія I = U/R: струм помітно зростає з напругою
    f.append(line(lx, ly, lx + lw, ly - lh * 0.86, POS, 2.6))
    f.append(text(lx + lw - 6, ly - lh * 0.86 - 8, "нахил = 1/R", 11, POS, "end"))
    # позначка «струм пливе» — дві точки
    f.append(circle(lx + lw * 0.30, ly - lh * 0.86 * 0.30, 4, POS, POS))
    f.append(circle(lx + lw * 0.80, ly - lh * 0.86 * 0.80, 4, POS, POS))
    f.append(line(lx + lw * 0.80, ly - lh * 0.86 * 0.30, lx + lw * 0.80,
                  ly - lh * 0.86 * 0.80, MUTED, 1.2, "3,3"))
    f.append(text(lx + lw * 0.80 + 6, ly - lh * 0.50, "струм\nпливе", 10, MUTED, "start"))

    # праворуч: джерело струму
    rx, ry, rw, rh = 470, 300, 230, 210
    f += axes(rx, ry, rw, rh, "Хвіст — джерело струму")
    Iy = ry - rh * 0.62
    f.append(line(rx, Iy, rx + rw, Iy - rh * 0.04, FIELD, 2.6))  # майже плеската
    f.append(text(rx + rw - 6, Iy - 10, "майже плеско", 11, FIELD, "end"))
    f.append(line(rx, Iy, rx, ry, INK, 1.0, "3,3"))
    f.append(text(rx - 8, Iy + 4, "I₀", 12, FIELD, "end", italic=True))

    body, bw, bh = textbox(W / 2, 352, "Похилий нахил = малий опір = струм залежить від напруги.   "
                           "Плеско = великий опір = струм тримається.", size=12, pad=8,
                           fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(out("resistor-vs-source.svg"), W, H, *f)


# ── Фігура 2: дзеркало струму як хвіст диференційної пари ────────────────────
def fig_mirror_as_tail():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 26, "Дзеркало копіює опорний струм у хвіст пари", 15, INK, "middle", bold=True))

    # верхня шина +V
    topy = 70
    f.append(line(70, topy, 650, topy, POS, 2.2))
    f.append(text(660, topy + 5, "+V", 13, POS, "start", bold=True))

    # диференційна пара (спрощено два прямокутники-транзистори Q1,Q2)
    q1x, q2x, qy = 250, 390, 150
    f.append(fitbox(q1x - 34, qy, 68, 46, "Q1", 14, fill=FILL))
    f.append(fitbox(q2x - 34, qy, 68, 46, "Q2", 14, fill=FILL))
    f.append(line(q1x, topy, q1x, qy, LINE, 1.6))            # колектори до +V (через навантаження — спрощено)
    f.append(line(q2x, topy, q2x, qy, LINE, 1.6))
    f.append(text(q1x, topy - 8, "вихід", 11, MUTED, "middle"))
    f.append(text(q2x, topy - 8, "вихід", 11, MUTED, "middle"))
    # бази — входи
    f.append(line(q1x - 34, qy + 23, q1x - 80, qy + 23, NEG, 1.6))
    f.append(text(q1x - 86, qy + 27, "вхід −", 11, NEG, "end"))
    f.append(line(q2x + 34, qy + 23, q2x + 80, qy + 23, POS, 1.6))
    f.append(text(q2x + 86, qy + 27, "вхід +", 11, POS, "start"))

    # спільний емітерний вузол (хвіст)
    taily = 250
    f.append(line(q1x, qy + 46, q1x, taily, LINE, 1.6))
    f.append(line(q2x, qy + 46, q2x, taily, LINE, 1.6))
    f.append(line(q1x, taily, q2x, taily, LINE, 1.6))
    tailx = (q1x + q2x) / 2
    f.append(circle(tailx, taily, 3.5, LINE, LINE))
    f.append(text(tailx, taily - 8, "хвіст", 11, INK, "middle", bold=True))

    # дзеркало: опорна гілка ліворуч + вихідна під хвостом
    refx = 130
    # опорний резистор задає I_REF
    f.append(line(refx, topy, refx, 120, LINE, 1.6))
    f.append(fitbox(refx - 26, 120, 52, 38, "R", 13, fill=FILL))
    f.append(text(refx + 34, 139, "задає\nI_REF", 10, MUTED, "start"))
    # діод-увімкнений транзистор опори
    f.append(fitbox(refx - 32, 200, 64, 44, "Qоп", 13, fill=FILL))
    f.append(line(refx, 158, refx, 200, LINE, 1.6))
    # вихідний транзистор дзеркала (під хвостом)
    f.append(fitbox(tailx - 36, 300, 72, 46, "Qдзк", 13, fill="#eef7f0", stroke=FIELD))
    f.append(line(tailx, taily, tailx, 300, FIELD, 2.0))
    f.append(arrow(tailx, 296, tailx, taily + 6, FIELD, 2.0))
    f.append(text(tailx + 42, 280, "I₀ = копія I_REF", 12, FIELD, "start", bold=True))

    # земля
    gy = 360
    for bx in (refx, tailx):
        f.append(line(bx, 244 if bx == refx else 346, bx, gy, LINE, 1.6))
        f.append(line(bx - 14, gy, bx + 14, gy, INK, 2.0))
        f.append(line(bx - 9, gy + 5, bx + 9, gy + 5, INK, 1.6))
        f.append(line(bx - 4, gy + 10, bx + 4, gy + 10, INK, 1.4))
    # зв'язок баз дзеркала (символічно): база Qоп (ліворуч) → рейка → база Qдзк (ліворуч)
    by = 280
    f.append(line(refx - 32, 222, 70, 222, FIELD, 1.6))            # база Qоп вліво
    f.append(line(70, 222, 70, by, FIELD, 1.6, "4,3"))
    f.append(line(70, by, tailx - 36, by, FIELD, 1.6, "4,3"))
    f.append(line(tailx - 36, by, tailx - 36, 323, FIELD, 1.6))    # вгору до боку Qдзк (центр y=323)
    f.append(line(tailx - 36, 323, tailx - 36, 323, FIELD, 1.6))
    f.append(text((70 + tailx) / 2, by - 6, "спільна база — наказ копіювати", 10, FIELD, "middle"))

    render(out("mirror-as-tail.svg"), W, H, *f)


# ── Фігура 3: ефект Ерлі нахиляє лінію — скінченний опір джерела ─────────────
def fig_early_slope():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 26, "Чому транзистор-джерело не ідеальне: ефект Ерлі", 15, INK, "middle", bold=True))
    ox, oy, w, h = 110, 300, 470, 210
    f.append(line(ox, oy, ox, oy - h, INK, 1.8))
    f.append(line(ox, oy, ox + w, oy, INK, 1.8))
    f.append(text(ox - 8, oy - h + 4, "I колектора", 12, MUTED, "end"))
    f.append(text(ox + w, oy + 20, "U на колекторі (напруга на джерелі)", 11, MUTED, "end"))

    # реальна лінія: гентльний (реалістичний) нахил угору праворуч
    xa, xb = ox + 70, ox + w
    ya = oy - h * 0.50                         # I₀ у робочій точці
    yb = ya - h * 0.16                         # невеликий підйом праворуч
    f.append(line(xa, ya, xb, yb, POS, 2.6))
    f.append(text(xb - 6, yb - 8, "реальний транзистор", 11, POS, "end"))
    # ідеал: горизонталь через I₀
    f.append(line(xa, ya, xb, ya, FIELD, 2.0, "5,4"))
    f.append(text(xa + 4, ya - 8, "ідеал (плеско)", 11, FIELD, "start"))
    # робоча точка I₀
    f.append(line(ox, ya, xa, ya, INK, 1.0, "3,3"))
    f.append(text(ox - 8, ya + 4, "I₀", 12, INK, "end", italic=True))
    # короткий зворотний пунктир + стрілка «−U_A десь далеко ліворуч»
    slope = (yb - ya) / (xb - xa)
    ystub = ya + slope * (xa - (ox + 10))     # де лінія була б трохи лівіше xa
    f.append(line(xa, ya, ox + 10, ystub, MUTED, 1.3, "3,3"))
    f.append(arrow(ox + 24, ya + 30, ox - 2, ya + 30, MUTED, 1.4))
    f.append(text(ox + 30, ya + 34, "−U_A — далеко ліворуч", 10, MUTED, "start", italic=True))
    f.append(text(ox + 30, ya + 50, "(тому r₀ велике)", 9, MUTED, "start"))

    body, bw, bh = textbox(ox + w - 120, oy - h * 0.84, "нахил = 1 / r₀\nr₀ = U_A / I₀", size=12, pad=8,
                           fill="#fdecea", stroke=POS)
    f.append(body)
    render(out("early-slope.svg"), W, H, *f)


# ── Фігура 4: каскод піднімає опір — «щит» від коливань напруги ──────────────
def fig_cascode_stack():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 26, "Каскод: другий транзистор ховає джерело від коливань напруги", 14, INK, "middle", bold=True))

    # дві колонки: ліворуч просте джерело, праворуч каскод
    # ── ліворуч: просте джерело ──
    lx = 200
    topy, gy = 70, 360
    f.append(line(lx, topy, lx, 120, LINE, 1.6))
    f.append(text(lx, topy - 8, "сюди тече I₀", 11, MUTED, "middle"))
    f.append(arrow(lx, 116, lx, topy + 6, FIELD, 2.0))
    f.append(fitbox(lx - 40, 130, 80, 52, "транзистор\nджерела", 12, fill=FILL))
    f.append(line(lx, 182, lx, 280, LINE, 1.6))
    f.append(line(lx - 16, 280, lx + 16, 280, INK, 2.0))     # земля
    f.append(line(lx - 10, 286, lx + 10, 286, INK, 1.6))
    f.append(line(lx - 5, 292, lx + 5, 292, INK, 1.4))
    f.append(text(lx, 232, "Δ U", 12, POS, "middle", bold=True))
    f.append(text(lx, 252, "уся на ньому", 10, POS, "middle"))
    f.append(text(lx, 320, "r₀", 14, INK, "middle", italic=True))

    # ── праворуч: каскод ──
    rx = 520
    f.append(line(rx, topy, rx, 110, LINE, 1.6))
    f.append(text(rx, topy - 8, "сюди тече I₀", 11, MUTED, "middle"))
    f.append(arrow(rx, 106, rx, topy + 6, FIELD, 2.0))
    f.append(fitbox(rx - 44, 118, 88, 50, "верхній\n(щит)", 12, fill="#eef7f0", stroke=FIELD))
    f.append(text(rx + 54, 143, "тримає Δ U\nна собі", 10, FIELD, "start"))
    f.append(line(rx, 168, rx, 210, LINE, 1.6))
    f.append(circle(rx, 189, 3.0, MUTED, MUTED))
    f.append(text(rx - 12, 193, "тут — майже\nспокій", 9, MUTED, "end"))
    f.append(fitbox(rx - 44, 210, 88, 50, "нижній\n(джерело)", 12, fill=FILL))
    f.append(line(rx, 260, rx, 320, LINE, 1.6))
    f.append(line(rx - 16, 320, rx + 16, 320, INK, 2.0))
    f.append(line(rx - 10, 326, rx + 10, 326, INK, 1.6))
    f.append(line(rx - 5, 332, rx + 5, 332, INK, 1.4))

    # підсумок-рамки під колонками
    b1, w1, h1 = textbox(lx, 350, "r₀ ≈ U_A / I₀", size=13, pad=8, fill=FILL)
    f.append(b1)
    b2, w2, h2 = textbox(rx, 360, "r₀ × (gm·r₀)\nу сотні разів більше", size=12, pad=8,
                         fill="#eef7f0", stroke=FIELD)
    f.append(b2)
    render(out("cascode-stack.svg"), W, H, *f)


if __name__ == "__main__":
    fig_resistor_vs_source()
    fig_mirror_as_tail()
    fig_early_slope()
    fig_cascode_stack()
    print("OK: 4 figures ->", IMG)
