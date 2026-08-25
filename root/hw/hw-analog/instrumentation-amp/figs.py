# -*- coding: utf-8 -*-
"""Фігури до теми «Інструментальний підсилювач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Задача: мілівольти різниці на вольтовому п'єдесталі ───────────────────
def fig_problem():
    W, H = 720, 380
    f = [text(W / 2, 28, "Корисне — крихітна різниця; п'єдестал і завада — спільні",
              size=16, bold=True)]

    # вісь напруги ліворуч
    ax_x = 90
    base_y, top_y = 330, 70           # 0 В унизу, рейка вгорі
    f.append(line(ax_x, top_y, ax_x, base_y, color=INK, sw=2))
    f.append(text(ax_x - 12, base_y + 4, "0 В", size=12, color=MUTED, anchor="end"))
    f.append(text(ax_x - 12, top_y + 4, "Vживл", size=12, color=MUTED, anchor="end"))

    # спільний (синфазний) рівень — широка смуга-п'єдестал
    cm_y = 215                         # ≈ половина живлення
    f.append(rect(ax_x, cm_y, 360, base_y - cm_y, fill="#eef1f5", stroke="#d6dde6", sw=1.2, rx=4))
    f.append(text(ax_x + 180, (cm_y + base_y) / 2 + 4,
                  "спільний рівень  ≈ 2.5 В  (однаковий на обох входах)",
                  size=12, color=MUTED))

    # два входи V+ і V− — майже на одному рівні, крихітна щілина між ними
    vp_y = cm_y - 26
    vm_y = cm_y - 8
    f.append(line(ax_x, vp_y, ax_x + 360, vp_y, color=POS, sw=2.4))
    f.append(line(ax_x, vm_y, ax_x + 360, vm_y, color=NEG, sw=2.4))
    f.append(text(ax_x + 368, vp_y + 4, "V+", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(ax_x + 368, vm_y + 8, "V−", size=13, color=NEG, bold=True, anchor="start"))

    # виноска: різниця = лічені мілівольти
    bx = 540
    b, bw, bh = textbox(bx + 70, vp_y - 6, "корисне:\nрізниця ≈ 10 мВ", size=12,
                        fill="#eef6ef", stroke=FIELD)
    f.append(b)
    f.append(arrow(bx + 50, vp_y - 6, ax_x + 362, (vp_y + vm_y) / 2, color=FIELD, sw=1.6))

    # завада, що однаково гойдає обидва входи (стрілки вгору-вниз на смузі)
    for dx in (60, 180, 300):
        f.append(arrow(ax_x + dx, cm_y - 2, ax_x + dx, cm_y - 40, color=MUTED, sw=1.4))
        f.append(arrow(ax_x + dx, cm_y - 2, ax_x + dx, base_y - 18, color=MUTED, sw=1.4))
    f.append(text(ax_x + 180, base_y + 26,
                  "завада від мережі гойдає обидва входи РАЗОМ → спільна",
                  size=12, color=MUTED))

    return render(os.path.join(IMG, "problem.svg"), W, H, *f)


# ── 2. Топологія «три ОП»: два буфери + Rg, тоді віднімач ────────────────────
def fig_three_opamp():
    W, H = 760, 420
    f = [text(W / 2, 28, "Три ОП: два буфери з одним Rg, тоді різницевий каскад",
              size=16, bold=True)]

    def opamp(cx, cy, label, scale=1.0):
        # трикутник вершиною праворуч
        w = 70 * scale
        h = 66 * scale
        p1 = (cx - w / 2, cy - h / 2)
        p2 = (cx - w / 2, cy + h / 2)
        p3 = (cx + w / 2, cy)
        tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" '
               'stroke-width="1.8"/>' % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], FILL, LINE))
        return tri, p1, p2, p3

    # ── вхідний каскад (зелена зона) ──
    f.append(rect(40, 64, 360, 320, fill="#f0f8f1", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(220, 86, "перший каскад: два буфери, підсилення задає Rg",
                  size=12, color=FIELD, bold=True))

    # A1 угорі, A2 унизу; інвертуючі входи дивляться всередину (до Rg між ними)
    a1x, a1y = 250, 140
    a2x, a2y = 250, 308
    t1, _, _, p1r = opamp(a1x, a1y, "A1")
    t2, _, _, p2r = opamp(a2x, a2y, "A2")
    f.append(t1)
    f.append(t2)
    f.append(text(a1x - 4, a1y + 5, "A1", size=13, bold=True))
    f.append(text(a2x - 4, a2y + 5, "A2", size=13, bold=True))

    # A1: «+» зовні (зверху), «−» всередину (знизу). A2 — дзеркально.
    p1p = (a1x - 35, a1y - 16)   # неінв. A1 (зовні)
    p1m = (a1x - 35, a1y + 16)   # інв. A1 (всередину, до Rg)
    p2p = (a2x - 35, a2y + 16)   # неінв. A2 (зовні)
    p2m = (a2x - 35, a2y - 16)   # інв. A2 (всередину, до Rg)
    f.append(plus(*p1p, 8))
    f.append(minus(*p1m, 8))
    f.append(plus(*p2p, 8))
    f.append(minus(*p2m, 8))

    # дроти входів від давача (ліворуч), на неінвертуючі входи
    f.append(line(64, p1p[1], p1p[0] - 8, p1p[1], color=POS, sw=2))
    f.append(line(64, p2p[1], p2p[0] - 8, p2p[1], color=NEG, sw=2))
    f.append(text(58, p1p[1] + 4, "V+", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(58, p2p[1] + 4, "V−", size=13, color=NEG, bold=True, anchor="end"))

    # ── ланцюг R–Rg–R по інвертуючих входах (вертикально, між A1 і A2) ──
    midx = 150                          # вертикальна шина ланцюга
    # від інв. входів углиб до шини
    f.append(line(p1m[0] - 8, p1m[1], midx, p1m[1], color=LINE, sw=1.6))
    f.append(line(p2m[0] - 8, p2m[1], midx, p2m[1], color=LINE, sw=1.6))
    # вертикальний ланцюг: R (верх) — Rg (центр) — R (низ)
    yR1a, yR1b = p1m[1], 196
    yRgA, yRgB = 196, 252
    yR2a, yR2b = 252, p2m[1]
    f.append(line(midx, yR1a, midx, yR1b, color=LINE, sw=1.6))
    f.append(line(midx, yRgA, midx, yRgB, color=LINE, sw=1.6))
    f.append(line(midx, yR2a, midx, yR2b, color=LINE, sw=1.6))
    rb1, _, _ = textbox(midx, (yR1a + yR1b) / 2, "R", size=12,
                        fill="#fff", stroke=LINE, min_w=30)
    rg, _, _ = textbox(midx, (yRgA + yRgB) / 2, "Rg", size=12,
                       fill="#fff7e6", stroke="#b8860b", min_w=36)
    rb2, _, _ = textbox(midx, (yR2a + yR2b) / 2, "R", size=12,
                        fill="#fff", stroke=LINE, min_w=30)
    f.append(rb1)
    f.append(rg)
    f.append(rb2)

    # ── виходи буферів: вузли Va (з A1) і Vb (з A2) ──
    # вихід A1 вершина праворуч
    f.append(line(p1r[0], a1y, 340, a1y, color=LINE, sw=1.6))
    f.append(text(326, a1y - 8, "Va", size=12, color=INK, anchor="middle"))
    f.append(line(p2r[0], a2y, 340, a2y, color=LINE, sw=1.6))
    f.append(text(326, a2y - 8, "Vb", size=12, color=INK, anchor="middle"))
    # зворотний зв'язок: з виходу A1 вниз до верхнього кінця ланцюга R
    f.append(line(340, a1y, 340, yR1b, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(340, yR1b, midx, yR1b, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(340, a2y, 340, yR2a, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(340, yR2a, midx, yR2a, color=MUTED, sw=1.4, dash="5,4"))

    # ── різницевий каскад (синя зона) ──
    f.append(rect(440, 150, 280, 200, fill="#eef2fc", stroke=NEG, sw=1.4, rx=8))
    f.append(text(580, 172, "другий каскад: віднімач", size=12, color=NEG, bold=True))
    a3x, a3y = 595, 255
    t3, _, _, p3r = opamp(a3x, a3y, "A3")
    f.append(t3)
    f.append(text(a3x - 4, a3y + 5, "A3", size=13, bold=True))
    p3m = (a3x - 35, a3y - 16)   # інв.
    p3p = (a3x - 35, a3y + 16)   # неінв.
    f.append(minus(*p3m, 8))
    f.append(plus(*p3p, 8))

    # Va → інв. A3, Vb → неінв. A3
    f.append(line(340, a1y, 470, a1y, color=LINE, sw=1.6))
    f.append(line(470, a1y, 470, p3m[1], color=LINE, sw=1.6))
    f.append(line(470, p3m[1], p3m[0] - 8, p3m[1], color=LINE, sw=1.6))
    f.append(line(340, a2y, 455, a2y, color=LINE, sw=1.6))
    f.append(line(455, a2y, 455, p3p[1], color=LINE, sw=1.6))
    f.append(line(455, p3p[1], p3p[0] - 8, p3p[1], color=LINE, sw=1.6))

    # вихід
    f.append(line(p3r[0], a3y, 700, a3y, color=INK, sw=2.2))
    f.append(arrow(700, a3y, 730, a3y, color=INK, sw=2.2))
    f.append(text(708, a3y - 12, "Vвих", size=13, bold=True, anchor="middle"))

    # підпис унизу
    f.append(text(W / 2, 406, "Підсилення всього приладу:  G = (1 + 2R/Rg) · (R₂/R₁)",
                  size=13, bold=True, color=INK))
    return render(os.path.join(IMG, "three-opamp.svg"), W, H, *f)


# ── 3. Чому три, а не один: вхідний опір і CMRR ─────────────────────────────
def fig_one_vs_three():
    W, H = 720, 360
    f = [text(W / 2, 28, "Один ОП проти трьох: вхідний опір і відкидання завади",
              size=16, bold=True)]

    # ліворуч — простий віднімач
    f.append(rect(40, 60, 300, 270, fill="#fdf2f2", stroke=POS, sw=1.4, rx=8))
    f.append(text(190, 84, "один ОП (простий віднімач)", size=13, bold=True, color=POS))
    b1 = fitbox(60, 104, 260, 54,
                "вхід низькоомний:\nрезистори навантажують давач", size=12,
                fill="#fff", stroke=POS)
    f.append(b1)
    b2 = fitbox(60, 168, 260, 54,
                "CMRR тримається\nлише на доборі 4 резисторів", size=12,
                fill="#fff", stroke=POS)
    f.append(b2)
    b3 = fitbox(60, 232, 260, 70,
                "0.1 % резистори →\nCMRR ≈ 54 дБ\n(завада тече далі)", size=12,
                fill="#fff", stroke=POS, bold=True)
    f.append(b3)

    # праворуч — три ОП
    f.append(rect(380, 60, 300, 270, fill="#f0f8f1", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(530, 84, "три ОП (інструментальний)", size=13, bold=True, color=FIELD))
    c1 = fitbox(400, 104, 260, 54,
                "вхід величезний:\nбуфери не вантажать давач", size=12,
                fill="#fff", stroke=FIELD)
    f.append(c1)
    c2 = fitbox(400, 168, 260, 54,
                "перший каскад підсилює різницю,\nспільне лишає в 1×", size=12,
                fill="#fff", stroke=FIELD)
    f.append(c2)
    c3 = fitbox(400, 232, 260, 70,
                "front-end множить CMRR →\n≈ 94 дБ і вище\n(завада задушена)", size=12,
                fill="#fff", stroke=FIELD, bold=True)
    f.append(c3)

    return render(os.path.join(IMG, "one-vs-three.svg"), W, H, *f)


# ── допоміжне: ОП-трикутник і синусоїда ─────────────────────────────────────
def _opamp_tri(cx, cy, w=70, h=64, label="", inv_top=True):
    """Трикутник ОП вершиною праворуч; «−»/«+» на входах, підпис усередині."""
    p1 = (cx - w / 2, cy - h / 2)
    p2 = (cx - w / 2, cy + h / 2)
    p3 = (cx + w / 2, cy)
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" '
           'stroke-width="1.8"/>' % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], FILL, LINE))
    top = (cx - w / 2 + 16, cy - h / 4)
    bot = (cx - w / 2 + 16, cy + h / 4)
    if inv_top:
        marks = minus(*top, 7) + plus(*bot, 7)
    else:
        marks = plus(*top, 7) + minus(*bot, 7)
    lab = text(cx - 2, cy + 5, label, size=13, color=MUTED, bold=True)
    return tri + marks + lab, p3

def _sine(x0, y0, span, cycles, amp, color, sw=2.2, phase=0.0):
    """Полілінія-синусоїда: span px завширшки, amp px розмаху, cycles періодів."""
    import math
    n = int(span)
    pts = []
    for i in range(n + 1):
        t = i / span
        x = x0 + i
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<path d="M %s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" L ".join(pts), color, sw))


# ── 4. Топологія для math-вставки: повна схема трьох ОП із R₁/R₂ ─────────────
def fig_inamp_topology():
    W, H = 780, 440
    f = [text(W / 2, 26, "Інструментальний підсилювач: три ОП", size=17, bold=True)]

    # зони
    f.append(rect(150, 64, 230, 312, fill="#f0f8f1", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(160, 84, "1) буфери + Rg: усе підсилення", size=12, color=FIELD,
                  bold=True, anchor="start"))
    f.append(rect(398, 96, 320, 280, fill="#eef2fc", stroke=NEG, sw=1.4, rx=10))
    f.append(text(408, 116, "2) різницевий каскад: ріже синфазне", size=12, color=NEG,
                  bold=True, anchor="start"))

    # входи
    f.append(text(40, 124, "V₊", size=16, color=POS, bold=True, anchor="start"))
    f.append(text(40, 324, "V₋", size=16, color=NEG, bold=True, anchor="start"))
    f.append(arrow(58, 120, 100, 120, color=POS, sw=2))
    f.append(arrow(58, 320, 100, 320, color=NEG, sw=2))

    # A1, A2
    a1, p1r = _opamp_tri(210, 120, label="A1", inv_top=False)
    a2, p2r = _opamp_tri(210, 320, label="A2", inv_top=True)
    f.append(a1); f.append(a2)
    f.append(line(100, 120, 175, 105, color=POS, sw=2))
    f.append(line(100, 320, 175, 335, color=NEG, sw=2))

    # виходи буферів Va, Vb
    f.append(line(245, 120, 470, 120, color=INK, sw=2))
    f.append(line(245, 320, 470, 320, color=INK, sw=2))
    f.append(text(252, 111, "Va", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(252, 338, "Vb", size=13, color=INK, bold=True, anchor="start"))

    # ланцюг R–Rg–R по вертикалі (x=320)
    f.append(circle(320, 120, 3.4, fill=INK, stroke=INK))
    f.append(line(320, 120, 320, 126, color=INK, sw=2))
    rb1, _, _ = textbox(320, 140, "R", size=12, fill="#fff", stroke=INK, min_w=22)
    f.append(rb1)
    f.append(line(320, 154, 320, 176, color=INK, sw=2))
    f.append(circle(320, 176, 3.4, fill=INK, stroke=INK))
    rg, _, _ = textbox(320, 220, "Rg", size=12, fill="#eef9f0", stroke=FIELD, min_w=26)
    f.append(rg)
    f.append(line(320, 176, 320, 200, color=INK, sw=2))
    f.append(line(320, 240, 320, 264, color=INK, sw=2))
    f.append(circle(320, 264, 3.4, fill=INK, stroke=INK))
    rb2, _, _ = textbox(320, 300, "R", size=12, fill="#fff", stroke=INK, min_w=22)
    f.append(rb2)
    f.append(line(320, 264, 320, 286, color=INK, sw=2))
    f.append(line(320, 314, 320, 320, color=INK, sw=2))
    f.append(circle(320, 320, 3.4, fill=INK, stroke=INK))
    # зворотні зв'язки буферів до ланцюга
    f.append(line(175, 135, 250, 135, color=INK, sw=2))
    f.append(line(250, 135, 250, 176, color=INK, sw=2))
    f.append(line(250, 176, 320, 176, color=INK, sw=2))
    f.append(line(175, 305, 250, 305, color=INK, sw=2))
    f.append(line(250, 305, 250, 264, color=INK, sw=2))
    f.append(line(250, 264, 320, 264, color=INK, sw=2))

    # різницевий каскад A3 з R₁/R₂
    f.append(circle(470, 120, 3.4, fill=INK, stroke=INK))
    f.append(line(470, 120, 470, 201, color=INK, sw=2))
    f.append(line(470, 201, 488, 201, color=INK, sw=2))
    r1a, _, _ = textbox(515, 201, "R₁", size=12, fill="#fff", stroke=INK, min_w=40)
    f.append(r1a)
    f.append(line(535, 201, 554, 201, color=INK, sw=2))
    f.append(circle(498, 201, 3.4, fill=INK, stroke=INK))
    f.append(circle(470, 320, 3.4, fill=INK, stroke=INK))
    f.append(line(470, 320, 470, 231, color=INK, sw=2))
    f.append(line(470, 231, 488, 231, color=INK, sw=2))
    r1b, _, _ = textbox(515, 231, "R₁", size=12, fill="#fff", stroke=INK, min_w=40)
    f.append(r1b)
    f.append(line(535, 231, 554, 231, color=INK, sw=2))
    f.append(circle(498, 231, 3.4, fill=INK, stroke=INK))
    # R₂ до землі
    f.append(line(498, 231, 498, 300, color=INK, sw=2))
    r2g, _, _ = textbox(515, 315, "R₂", size=12, fill="#fff", stroke=INK, min_w=40)
    f.append(r2g)
    f.append(line(498, 330, 498, 348, color=INK, sw=2))
    f.append(line(486, 348, 510, 348, color=INK, sw=2.4))
    f.append(line(490, 353, 506, 353, color=INK, sw=2))
    f.append(line(494, 358, 502, 358, color=INK, sw=1.6))
    # A3
    a3, p3r = _opamp_tri(590, 216, label="A3", inv_top=True)
    f.append(a3)
    f.append(line(626, 216, 670, 216, color=INK, sw=2))
    f.append(circle(652, 216, 3.4, fill=INK, stroke=INK))
    f.append(arrow(670, 216, 724, 216, color=INK, sw=2))
    f.append(text(708, 204, "Vвих", size=14, color=INK, bold=True))
    # зворотний R₂ A3
    f.append(line(652, 216, 652, 150, color=INK, sw=2))
    f.append(line(652, 150, 575, 150, color=INK, sw=2))
    r2f, _, _ = textbox(575, 150, "R₂", size=12, fill="#fff", stroke=INK, min_w=40)
    f.append(r2f)
    f.append(line(555, 150, 498, 150, color=INK, sw=2))
    f.append(line(498, 150, 498, 201, color=INK, sw=2))

    # підпис-формула
    fb = fitbox(150, 392, 484, 36,
                "G = (1 + 2R/Rg) · (R₂/R₁)   — підсилення задає один резистор Rg",
                size=14, fill="#fbf6e6", stroke="#d8c98a", bold=True)
    f.append(fb)
    return render(os.path.join(IMG, "inamp-topology.svg"), W, H, *f)


# ── 5. Синфазне проти диференційного: дві панелі з хвилями ───────────────────
def fig_inamp_cm_vs_dm():
    W, H = 760, 360
    f = [text(W / 2, 26, "Два сигнали на одному вході: що з ними робить in-amp",
              size=16, bold=True)]

    # ── ліва панель: диференційний (протифазні) ──
    f.append(rect(60, 56, 300, 280, fill="none", stroke="#c9d3dc", sw=1.4, rx=10))
    f.append(text(210, 78, "Корисний (диференційний) сигнал", size=13, color=FIELD, bold=True))
    f.append(text(78, 110, "V₊", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(78, 214, "V₋", size=13, color=NEG, bold=True, anchor="start"))
    f.append(line(100, 110, 310, 110, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(100, 190, 310, 190, color=MUTED, sw=1.2, dash="4 4"))
    f.append(_sine(100, 110, 210, 1.5, 18, POS, sw=2.2, phase=0.0))
    f.append(_sine(100, 190, 210, 1.5, 18, NEG, sw=2.2, phase=3.14159))
    f.append(text(210, 250, "різниця V₊−V₋ ≠ 0", size=12, color=FIELD, bold=True))
    f.append(arrow(210, 258, 210, 276, color=FIELD, sw=2))
    f.append(fitbox(120, 280, 180, 28, "× велике G", size=13, fill="#eef6ef",
                    stroke=FIELD, color=FIELD, bold=True))

    # ── права панель: синфазний (синхронні) ──
    f.append(rect(410, 56, 290, 280, fill="none", stroke="#c9d3dc", sw=1.4, rx=10))
    f.append(text(555, 78, "Завада (синфазна): однакова на обох", size=13, color=POS, bold=True))
    f.append(text(428, 144, "V₊", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(428, 168, "V₋", size=13, color=NEG, bold=True, anchor="start"))
    f.append(_sine(450, 154, 200, 1.5, 36, POS, sw=2.6, phase=0.0))
    f.append(_sine(450, 146, 200, 1.5, 36, NEG, sw=2.0, phase=0.0))
    f.append(text(555, 250, "різниця V₊−V₋ ≈ 0", size=12, color=POS, bold=True))
    f.append(arrow(555, 258, 555, 276, color=POS, sw=2))
    f.append(fitbox(455, 280, 200, 28, "× майже нуль (÷ CMRR)", size=12, fill="#fdecea",
                    stroke=POS, color=POS, bold=True))
    return render(os.path.join(IMG, "inamp-cm-vs-dm.svg"), W, H, *f)


# ── 6. In-amp як чип: розпіновка + мостовий давач + ADC ──────────────────────
def fig_inamp_bridge_pinout():
    W, H = 760, 420
    f = [text(W / 2, 26, "In-amp як готовий чип: міст на входах, Rg задає G, REF зсуває нуль",
              size=15, bold=True)]

    # корпус чипа
    cx, cy, cw, ch = 330, 120, 150, 200
    f.append(rect(cx, cy, cw, ch, fill="#eef2fc", stroke=NEG, sw=1.6, rx=8))
    f.append(text(cx + cw / 2, cy + ch / 2 - 6, "in-amp", size=15, color=NEG, bold=True))
    f.append(text(cx + cw / 2, cy + ch / 2 + 14, "(3 ОП усередині)", size=11, color=MUTED))

    # ліві ноги: IN+ / IN−
    f.append(line(cx - 40, cy + 40, cx, cy + 40, color=POS, sw=2))
    f.append(line(cx - 40, cy + 80, cx, cy + 80, color=NEG, sw=2))
    f.append(text(cx - 44, cy + 44, "IN+", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(cx - 44, cy + 84, "IN−", size=12, color=NEG, bold=True, anchor="end"))

    # ноги RG (дві, знизу ліворуч) із зовнішнім Rg
    f.append(line(cx + 40, cy + ch, cx + 40, cy + ch + 30, color=INK, sw=2))
    f.append(line(cx + 100, cy + ch, cx + 100, cy + ch + 30, color=INK, sw=2))
    f.append(line(cx + 40, cy + ch + 30, cx + 100, cy + ch + 30, color=INK, sw=2))
    rg, _, _ = textbox(cx + 70, cy + ch + 30, "Rg", size=12, fill="#eef9f0",
                       stroke=FIELD, min_w=30)
    f.append(rg)
    f.append(text(cx + 40, cy + ch + 16, "RG", size=11, color=MUTED, anchor="middle"))
    f.append(text(cx + 100, cy + ch + 16, "RG", size=11, color=MUTED, anchor="middle"))

    # REF знизу
    f.append(line(cx + cw / 2, cy + ch, cx + cw / 2, cy + ch + 60, color=INK, sw=2))
    f.append(text(cx + cw / 2 + 6, cy + ch + 20, "REF", size=11, color=MUTED, anchor="start"))
    f.append(line(cx + cw / 2 - 12, cy + ch + 60, cx + cw / 2 + 12, cy + ch + 60, color=INK, sw=2.4))
    f.append(line(cx + cw / 2 - 8, cy + ch + 65, cx + cw / 2 + 8, cy + ch + 65, color=INK, sw=2))

    # живлення зверху V+/V−
    f.append(line(cx + 40, cy, cx + 40, cy - 30, color=INK, sw=2))
    f.append(line(cx + 100, cy, cx + 100, cy - 30, color=INK, sw=2))
    f.append(text(cx + 40, cy - 34, "V+", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(cx + 100, cy - 34, "V−", size=12, color=NEG, bold=True, anchor="middle"))

    # права нога OUT → ADC
    f.append(line(cx + cw, cy + ch / 2, cx + cw + 60, cy + ch / 2, color=INK, sw=2))
    f.append(text(cx + cw + 6, cy + ch / 2 - 8, "OUT", size=12, color=INK, bold=True, anchor="start"))
    f.append(rect(cx + cw + 60, cy + ch / 2 - 30, 90, 60, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(cx + cw + 105, cy + ch / 2 - 4, "ADC", size=13, color=INK, bold=True))
    f.append(text(cx + cw + 105, cy + ch / 2 + 14, "MCU", size=11, color=MUTED))

    # міст ліворуч (ромб)
    bx, by = 120, cy + 60
    f.append(text(bx, by - 56, "мостовий давач", size=12, color=MUTED, bold=True))
    d = 34
    f.append(line(bx, by - d, bx + d, by, color=INK, sw=1.8))
    f.append(line(bx + d, by, bx, by + d, color=INK, sw=1.8))
    f.append(line(bx, by + d, bx - d, by, color=INK, sw=1.8))
    f.append(line(bx - d, by, bx, by - d, color=INK, sw=1.8))
    # виходи моста на IN+/IN−
    f.append(line(bx + d, by, cx - 40, cy + 40, color=POS, sw=2))
    f.append(line(bx - d, by, cx - 40, cy + 80, color=NEG, sw=2))
    f.append(text(bx, by + 4, "≈мВ", size=10, color=MUTED))

    f.append(fitbox(140, 372, 480, 34,
                    "крихітна різниця в мілівольтах → G·різниця на OUT → код у MCU",
                    size=13, fill="#fbf6e6", stroke="#d8c98a", bold=True))
    return render(os.path.join(IMG, "inamp-bridge-pinout.svg"), W, H, *f)


# ── 7. Дискретно (3 ОП + 5 точних R) проти готового чипа (1 Rg) ──────────────
def fig_inamp_bridge_discrete_vs_chip():
    W, H = 760, 360
    f = [text(W / 2, 26, "Чому платять за чип: узгодженість резисторів = CMRR",
              size=16, bold=True)]

    # ліворуч — дискретно
    f.append(rect(40, 56, 320, 280, fill="#fdf2f2", stroke=POS, sw=1.4, rx=10))
    f.append(text(200, 80, "Зібрати самому: 3 ОП", size=13, color=POS, bold=True))
    f.append(fitbox(60, 100, 280, 50,
                    "три окремі ОП\n+ п'ять ПІДІГНАНИХ резисторів", size=12,
                    fill="#fff", stroke=POS))
    f.append(fitbox(60, 162, 280, 50,
                    "CMRR = наскільки точно\nзбіглися ці резистори", size=12,
                    fill="#fff", stroke=POS))
    f.append(fitbox(60, 224, 280, 70,
                    "на 0.1% деталях →\nCMRR ≈ 60–66 дБ\n(+ температурний дрейф)", size=12,
                    fill="#fff", stroke=POS, bold=True))

    # праворуч — чип
    f.append(rect(400, 56, 320, 280, fill="#f0f8f1", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(560, 80, "Готовий in-amp: 1 корпус", size=13, color=FIELD, bold=True))
    f.append(fitbox(420, 100, 280, 50,
                    "резистори на кристалі,\nпідрізані лазером", size=12,
                    fill="#fff", stroke=FIELD))
    f.append(fitbox(420, 162, 280, 50,
                    "дрейфують РАЗОМ →\nстабільний CMRR", size=12,
                    fill="#fff", stroke=FIELD))
    f.append(fitbox(420, 224, 280, 70,
                    "CMRR ≈ 90–130 дБ «з коробки»\nлишається поставити\nодин Rg", size=12,
                    fill="#fff", stroke=FIELD, bold=True))
    return render(os.path.join(IMG, "inamp-bridge-discrete-vs-chip.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem()
    fig_three_opamp()
    fig_one_vs_three()
    fig_inamp_topology()
    fig_inamp_cm_vs_dm()
    fig_inamp_bridge_pinout()
    fig_inamp_bridge_discrete_vs_chip()
    print("OK: figures ->", IMG)
