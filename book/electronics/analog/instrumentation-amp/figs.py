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


if __name__ == "__main__":
    fig_problem()
    fig_three_opamp()
    fig_one_vs_three()
    print("OK: figures ->", IMG)
