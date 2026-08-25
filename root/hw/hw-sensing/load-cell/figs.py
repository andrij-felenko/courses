# -*- coding: utf-8 -*-
"""Фігури до теми «Тензодавач сили (load cell)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Пружне тіло: сила гне балку, поверхня тягнеться/стискається ───────────
def fig_elastic_body():
    W, H = 720, 380
    f = [text(W / 2, 28, "Сила гне пружне тіло — поверхня розтягується й стискається", size=16, bold=True)]

    # закладена ліва опора (стіна)
    f.append(rect(40, 120, 40, 150, fill="#cfd8e2", stroke=LINE, sw=1.8))
    for y in range(128, 268, 18):
        f.append(line(40, y, 30, y + 10, color=MUTED, sw=1.4))

    # балка у спокої (пунктир) і зігнута (суцільна)
    f.append(line(80, 160, 560, 160, color=MUTED, sw=1.4, dash="5,5"))
    f.append(line(80, 230, 560, 230, color=MUTED, sw=1.4, dash="5,5"))
    # зігнута балка — верх і низ як дуги вниз
    top = " ".join("%.1f,%.1f" % (80 + t, 160 + 0.00018 * t * t) for t in range(0, 481, 20))
    bot = " ".join("%.1f,%.1f" % (80 + t, 230 + 0.00018 * t * t) for t in range(0, 481, 20))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (top, NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (bot, POS))
    f.append(line(80, 160, 80, 230, color=LINE, sw=2))
    f.append(line(560, 160 + 0.00018 * 480 * 480, 560, 230 + 0.00018 * 480 * 480, color=LINE, sw=2))

    # сила вниз на вільному кінці
    f.append(arrow(560, 70, 560, 145, color=INK, sw=2.4))
    f.append(text(575, 105, "F", size=18, bold=True, anchor="start"))

    # підписи: верх стискається, низ розтягується
    b1, _, _ = textbox(300, 120, "верхня поверхня СТИСКАЄТЬСЯ", size=12, fill="#eaf0fd", stroke=NEG)
    f.append(b1)
    b2, _, _ = textbox(300, 290, "нижня поверхня РОЗТЯГУЄТЬСЯ", size=12, fill="#fdecea", stroke=POS)
    f.append(b2)

    b3, _, _ = textbox(W / 2, 350,
                       "деформація мала (тисячні частки) і прямо пропорційна силі — закон Гука",
                       size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b3)
    render(os.path.join(IMG, "elastic-body.svg"), W, H, *f)


# ── 2. Чотири тензорезистори на балці утворюють повний міст ──────────────────
def fig_four_gauges():
    W, H = 720, 420
    f = [text(W / 2, 28, "Чотири тензорезистори на балці = повний міст Вітстона", size=16, bold=True)]

    # ── ліворуч: балка з 4 наклеєними давачами ──
    bx, by = 40, 90
    f.append(text(bx + 150, 70, "балка з 4 давачами", size=12.5, bold=True))
    f.append(rect(bx, by, 300, 60, fill="#e9edf2", stroke=LINE, sw=1.8))
    f.append(rect(bx - 24, by - 10, 24, 80, fill="#cfd8e2", stroke=LINE, sw=1.6))  # закладка
    # два зверху (стиск), два знизу (розтяг)
    def gauge(x, y, col):
        f.append(rect(x, y, 34, 16, fill="#fff", stroke=col, sw=2, rx=2))
        for k in range(4):
            f.append(line(x + 4 + k * 8, y + 3, x + 4 + k * 8, y + 13, color=col, sw=1.4))
    gauge(bx + 40, by + 6, NEG)
    gauge(bx + 226, by + 6, NEG)
    gauge(bx + 40, by + 38, POS)
    gauge(bx + 226, by + 38, POS)
    f.append(text(bx + 57, by - 6, "стиск", size=10, color=NEG))
    f.append(text(bx + 243, by - 6, "стиск", size=10, color=NEG))
    f.append(text(bx + 57, by + 78, "розтяг", size=10, color=POS))
    f.append(text(bx + 243, by + 78, "розтяг", size=10, color=POS))
    # сила
    f.append(arrow(bx + 300, by - 18, bx + 300, by + 4, color=INK, sw=2.2))
    f.append(text(bx + 312, by - 6, "F", size=15, bold=True, anchor="start"))

    b, _, _ = textbox(bx + 150, by + 150,
                      "два давачі видовжуються, два коротшають\nна ту саму величину — це й живить міст",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    # ── праворуч: ромб моста ──
    cx, cy, r = 560, 200, 95
    top_n = (cx, cy - r)
    bot_n = (cx, cy + r)
    left_n = (cx - r, cy)
    right_n = (cx + r, cy)
    # плечі
    f.append(line(*top_n, *left_n, color=LINE, sw=2))
    f.append(line(*top_n, *right_n, color=LINE, sw=2))
    f.append(line(*bot_n, *left_n, color=LINE, sw=2))
    f.append(line(*bot_n, *right_n, color=LINE, sw=2))
    # давачі-стрілки на плечах: ↑ розтяг (червоний), ↓ стиск (синій)
    def arm_label(p1, p2, sym, col):
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        f.append(circle(mx, my, 13, fill="#fff", stroke=col, sw=2))
        f.append(text(mx, my + 5, sym, size=15, bold=True, color=col))
    arm_label(top_n, left_n, "↑", POS)
    arm_label(top_n, right_n, "↓", NEG)
    arm_label(bot_n, left_n, "↓", NEG)
    arm_label(bot_n, right_n, "↑", POS)
    # вузли
    for nx, ny in (top_n, bot_n, left_n, right_n):
        f.append(circle(nx, ny, 4, fill=INK, stroke=INK))
    # живлення згори-знизу
    f.append(text(cx, cy - r - 12, "+Vзбудж", size=11, bold=True, color=POS))
    f.append(text(cx, cy + r + 22, "GND", size=11, bold=True, color=MUTED))
    # вихід з боків
    f.append(text(cx - r - 14, cy - 6, "S−", size=11, bold=True, anchor="end", color=NEG))
    f.append(text(cx + r + 14, cy - 6, "S+", size=11, bold=True, anchor="start", color=POS))
    f.append(text(cx, cy + 6, "Vвих", size=11, italic=True, color=INK))

    render(os.path.join(IMG, "four-gauges.svg"), W, H, *f)


# ── 3. Чому міст: крихітна зміна опору тоне в сталому рівні ───────────────────
def fig_why_bridge():
    W, H = 720, 380
    f = [text(W / 2, 28, "Чому міст: зміна опору крихітна — її треба відняти від великого сталого", size=15.5, bold=True)]

    ox, oy = 110, 300
    ax_w, ax_h = 500, 220
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 40, "що бачить детектор", size=12, color=INK))

    # лівий стовпчик: одиночний давач — велике R, крихітна надбавка
    x1 = ox + 80
    f.append(rect(x1 - 35, oy - 200, 70, 200, fill="#dfe6ee", stroke=LINE, sw=1.6))
    f.append(rect(x1 - 35, oy - 204, 70, 4, fill=POS, stroke=POS))  # тонкий шар ΔR
    f.append(text(x1, oy - 215, "ΔR ≈ 0.1%", size=11, bold=True, color=POS))
    f.append(text(x1, oy - 100, "сталий R", size=12, color=INK))
    f.append(text(x1, oy + 20, "один давач", size=11.5, bold=True, color=INK))
    f.append(text(x1, oy + 36, "сигнал тоне у сталому", size=10, color=MUTED))

    # права частина: міст — стале відняли, лишилась тільки зміна
    x2 = ox + 320
    f.append(line(x2 - 60, oy, x2 + 60, oy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(rect(x2 - 30, oy - 70, 60, 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(x2, oy - 82, "лишилась тільки ΔR", size=11, bold=True, color=POS))
    f.append(text(x2, oy + 20, "міст (різниця)", size=11.5, bold=True, color=INK))
    f.append(text(x2, oy + 36, "стале скоротилось", size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 350,
                      "у балансі стале віднімається → підсилюй лише корисну зміну",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "why-bridge.svg"), W, H, *f)


# ── 4. Ланцюг сигналу: мВ/В → in-amp → АЦП → число ──────────────────────────
def fig_signal_chain():
    W, H = 760, 320
    f = [text(W / 2, 28, "Шлях від сили до числа: міст → підсилювач → АЦП", size=16, bold=True)]

    y = 150
    boxes = [
        ("Тензоміст", "сила → мВ\n~2 мВ/В", "#fbeee6", POS),
        ("Інструмент.\nпідсилювач", "мВ → В\nвисокий CMRR", "#eef2f8", NEG),
        ("АЦП", "В → код\n16–24 біт", "#eef6ef", FIELD),
        ("МК", "код → грами\nкалібрування", FILL, LINE),
    ]
    n = len(boxes)
    bw, gap = 150, 50
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    cxs = []
    for i, (title, body, fl, col) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        cxs.append(x + bw / 2)
        f.append(rect(x, y - 50, bw, 100, fill=fl, stroke=col, sw=2, rx=8))
        f.append(mtext(x + bw / 2, y - 22, title, size=12.5, bold=True, color=INK, lh=1.2))
        f.append(line(x + 16, y + 2, x + bw - 16, y + 2, color=col, sw=1.1))
        f.append(mtext(x + bw / 2, y + 22, body, size=10.5, color=MUTED, lh=1.25))
    for i in range(n - 1):
        f.append(arrow(cxs[i] + bw / 2 + 4, y, cxs[i + 1] - bw / 2 - 4, y, color=INK, sw=2))

    b, _, _ = textbox(W / 2, y + 110,
                      "слабкі мілівольти НЕ можна вести прямо в АЦП — спершу підсилення близько до моста",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "signal-chain.svg"), W, H, *f)


# ── 5. Три вороги точності: повзучість, температура, нелінійність ────────────
def fig_errors():
    W, H = 740, 360
    f = [text(W / 2, 28, "Три вороги точності, які прибирають калібруванням", size=16, bold=True)]
    col_w, x0, top = 240, 12, 56

    # колонка 1 — повзучість (повільний дрейф при сталій вазі)
    c1 = x0 + col_w / 2
    f.append(text(c1, top, "Повзучість (creep)", size=13, bold=True))
    axx, axy = x0 + 30, 250
    f.append(line(axx, axy, axx + 180, axy, color=INK, sw=1.5))
    f.append(line(axx, axy, axx, axy - 120, color=INK, sw=1.5))
    # ступінь навантаження + повільне сповзання вгору
    pts = ["%.1f,%.1f" % (axx, axy)]
    pts += ["%.1f,%.1f" % (axx + 20, axy - 80), "%.1f,%.1f" % (axx + 30, axy - 80)]
    pts += ["%.1f,%.1f" % (axx + 30 + t, axy - 80 - 22 * (t / 150.0)) for t in range(0, 151, 15)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), "#e08a3c"))
    f.append(text(c1, axy + 22, "вага стала, а покази", size=10.5, color=MUTED))
    f.append(text(c1, axy + 37, "повзуть — пружина «тече»", size=10.5, color=MUTED))

    # колонка 2 — температура (зсув нуля й нахилу)
    c2 = x0 + col_w + col_w / 2
    f.append(text(c2, top, "Температура", size=13, bold=True))
    axx2, axy2 = x0 + col_w + 30, 250
    f.append(line(axx2, axy2, axx2 + 180, axy2, color=INK, sw=1.5))
    f.append(line(axx2, axy2, axx2, axy2 - 120, color=INK, sw=1.5))
    # дві прямі: холодна й тепла — різний нуль і нахил
    f.append(line(axx2, axy2 - 20, axx2 + 170, axy2 - 110, color=NEG, sw=2.2))
    f.append(line(axx2, axy2 - 5, axx2 + 170, axy2 - 80, color=POS, sw=2.2, dash="6,4"))
    f.append(text(axx2 + 150, axy2 - 116, "холодно", size=10, color=NEG, anchor="end"))
    f.append(text(axx2 + 150, axy2 - 64, "тепло", size=10, color=POS, anchor="end"))
    f.append(text(c2, axy2 + 22, "пливе нуль і нахил —", size=10.5, color=MUTED))
    f.append(text(c2, axy2 + 37, "звідси температ. компенсація", size=10.5, color=MUTED))

    # колонка 3 — нелінійність (реальна крива ≠ пряма)
    c3 = x0 + 2 * col_w + col_w / 2
    f.append(text(c3, top, "Нелінійність", size=13, bold=True))
    axx3, axy3 = x0 + 2 * col_w + 30, 250
    f.append(line(axx3, axy3, axx3 + 180, axy3, color=INK, sw=1.5))
    f.append(line(axx3, axy3, axx3, axy3 - 120, color=INK, sw=1.5))
    f.append(line(axx3, axy3, axx3 + 170, axy3 - 110, color=MUTED, sw=1.6, dash="5,4"))  # ідеал
    curve = " ".join("%.1f,%.1f" % (axx3 + t, axy3 - (110 * (t / 170.0) + 16 * ((t / 170.0) - (t / 170.0) ** 2) * 4))
                     for t in range(0, 171, 10))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (curve, POS))
    f.append(text(axx3 + 168, axy3 - 116, "ідеал", size=10, color=MUTED, anchor="end"))
    f.append(text(c3, axy3 + 22, "крива трохи відходить", size=10.5, color=MUTED))
    f.append(text(c3, axy3 + 37, "від прямої — лінеаризують", size=10.5, color=MUTED))

    render(os.path.join(IMG, "errors.svg"), W, H, *f)


if __name__ == "__main__":
    fig_elastic_body()
    fig_four_gauges()
    fig_why_bridge()
    fig_signal_chain()
    fig_errors()
    print("OK: 5 figures ->", IMG)
