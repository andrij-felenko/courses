# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Зчитування сигналу» (root/course/embedded/keruvannia).
Чотири фігури до -d.md, кожна несе вагу й НЕ дублює базову статтю:
  1) quadrature.svg  — чому шум складається «по діагоналі» (в квадратах) → закон √N
  2) tau-budget.svg  — скільки сталих часу треба, щоб усталитися нижче ½ LSB (за розрядністю)
  3) jitter.svg      — тремтіння моменту відліку Δt → похибка напруги ΔV через нахил сигналу
  4) oversampling.svg— надвибірка розсуває перехідну смугу антиаліас-фільтра

Три фігури до вставки math-robust-stats.md (робастна статистика проти викидів):
  5) breakdown.svg     — точка зламу: один викид тягне середнє в нескінченність, медіану — ні
  6) efficiency.svg    — ціна стійкості: ефективність оцінки vs точка зламу (mean/trim/median)
  7) median-net5.svg   — мережа порівнянь-обмінів для медіани з 5 (6 компараторів)
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Складання шуму «по діагоналі»: закон √N ───────────────────────────────
def fig_quadrature():
    W, H = 900, 420
    els = []
    # Ліворуч: чотири незалежні поштовхи як вектори, що складаються в квадратах.
    ox, oy = 60, 250   # початок координат лівої панелі
    els.append(text(230, 40, "Один поштовх — довжина σ; сума N поштовхів росте як √N·σ",
                    size=14, bold=True))
    # осі
    els.append(line(ox, oy, ox + 360, oy, color=MUTED, sw=1.2))
    els.append(line(ox, oy, ox, oy - 200, color=MUTED, sw=1.2))
    # чотири однакові за довжиною, різні за напрямком «поштовхи», покладені «голова до хвоста»
    import random
    seg = 70.0
    dirs = [(0.96, -0.28), (0.55, -0.84), (0.99, -0.14), (0.30, -0.95)]
    x, y = float(ox), float(oy)
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = x + dx * seg, y + dy * seg
        els.append(arrow(x, y, nx, ny, color=NEG, sw=2.2))
        els.append(text((x + nx) / 2 + 6, (y + ny) / 2 - 6, "σ", size=13, color=NEG))
        x, y = nx, ny
    # результуючий вектор
    els.append(arrow(ox, oy, x, y, color=POS, sw=3))
    R = math.hypot(x - ox, y - oy)
    els.append(text((ox + x) / 2 - 18, (oy + y) / 2 + 4, "≈ 2σ", size=15, color=POS, bold=True))
    els.append(text(ox + 200, oy + 26, "4 поштовхи по σ → сума ≈ √4·σ = 2σ", size=12, color=MUTED))

    # Праворуч: крива √N — швидко скупіє.
    px, py, pw, ph = 560, 70, 300, 250
    els.append(rect(px, py, pw, ph, fill=BG, stroke=MUTED, sw=1))
    els.append(text(px + pw / 2, py - 12, "Виграш = √N (скупий закон)", size=14, bold=True))
    # осі
    els.append(line(px + 34, py + ph - 26, px + pw - 12, py + ph - 26, color=INK, sw=1.4))
    els.append(line(px + 34, py + 14, px + 34, py + ph - 26, color=INK, sw=1.4))
    els.append(text(px + pw - 10, py + ph - 10, "N", size=12, anchor="end", color=MUTED))
    els.append(text(px + 40, py + 20, "√N", size=12, anchor="start", color=MUTED))
    # крива sqrt від N=1..100, масштаб до 10 (√100)
    x0, y0b = px + 34, py + ph - 26
    xspan, yspan = pw - 46, ph - 40
    pts = []
    for k in range(1, 101):
        gx = x0 + xspan * (k / 100.0)
        gy = y0b - yspan * (math.sqrt(k) / 10.0)
        pts.append("%.1f,%.1f" % (gx, gy))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
               % (" ".join(pts), FIELD))
    # маркери N=4,16,100
    for k, lab in [(4, "N=4→×2"), (16, "16→×4"), (100, "100→×10")]:
        gx = x0 + xspan * (k / 100.0)
        gy = y0b - yspan * (math.sqrt(k) / 10.0)
        els.append(circle(gx, gy, 3.5, fill=POS, stroke=POS))
        els.append(text(gx + (6 if k < 100 else -6), gy + (14 if k == 4 else -6),
                        lab, size=11, color=INK, anchor=("start" if k < 100 else "end")))
    render(os.path.join(IMG, "quadrature.svg"), W, H, *els)


# ── 2. Скільки τ треба, щоб усталитися нижче ½ LSB ───────────────────────────
def fig_tau_budget():
    W, H = 900, 430
    els = []
    els.append(text(W / 2, 30, "Заряд по e^(−t/τ): скільки τ треба, щоб залишок упав нижче ½ LSB",
                    size=15, bold=True))
    px, py, pw, ph = 70, 60, 560, 300
    x0, y0b = px, py + ph
    els.append(line(x0, y0b, x0 + pw, y0b, color=INK, sw=1.5))          # вісь t
    els.append(line(x0, py, x0, y0b, color=INK, sw=1.5))                # вісь залишку
    els.append(text(x0 + pw, y0b + 20, "час (у сталих часу τ)", size=12, anchor="end", color=MUTED))
    els.append(text(x0 - 8, py + 6, "залишок", size=12, anchor="end", color=MUTED))
    # крива e^{-t/tau}, t від 0 до 12τ (лог-вісь по вертикалі як частка)
    nT = 12.0
    # вертикаль: лог10 від 1 до 1e-4 (4 декади)
    def yfrac(f):
        f = max(f, 1e-4)
        return py + ph * (math.log10(1.0 / f) / 4.0)
    # лінії декад
    for d in range(0, 5):
        yy = py + ph * (d / 4.0)
        els.append(line(x0, yy, x0 + pw, yy, color="#e5e7eb", sw=1))
        els.append(text(x0 - 6, yy + 4, ["1", "0.1", "0.01", "1e-3", "1e-4"][d],
                        size=10, anchor="end", color=MUTED))
    pts = []
    for i in range(0, 241):
        t = nT * i / 240.0
        f = math.exp(-t)
        gx = x0 + pw * (t / nT)
        gy = yfrac(f)
        pts.append("%.1f,%.1f" % (gx, gy))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
               % (" ".join(pts), NEG))
    # пороги ½ LSB для різних розрядностей: залишок < 0.5/2^N від повного стрибка
    # → t/τ = ln(2^{N+1}) = (N+1)·ln2
    for bits, col in [(8, MUTED), (10, FIELD), (12, POS)]:
        need = (bits + 1) * math.log(2.0)
        gx = x0 + pw * (need / nT)
        els.append(line(gx, py, gx, y0b, color=col, sw=1.6, dash="5,4"))
        els.append(text(gx, py - 6, "%d біт: %.1fτ" % (bits, need),
                        size=12, color=col, bold=True, anchor="middle"))
    # права колонка — правило словами
    bx = px + pw + 24
    body, bw, bh = textbox(bx + 110, 150,
        ["Правило усталення:", "",
         "залишок < ½ LSB  ⇔",
         "t > (N+1)·ln2 · τ", "",
         "8 біт  → ~6.2 τ",
         "10 біт → ~7.6 τ",
         "12 біт → ~9.0 τ", "",
         "τ = (R_дж + R_on)·C_H"],
        size=13, pad=12)
    els.append(body)
    render(os.path.join(IMG, "tau-budget.svg"), W, H, *els)


# ── 3. Тремтіння моменту відліку: Δt → ΔV через нахил ────────────────────────
def fig_jitter():
    W, H = 900, 400
    els = []
    els.append(text(W / 2, 30, "Тремтіння моменту відліку Δt → похибка ΔV = (нахил сигналу)·Δt",
                    size=15, bold=True))
    px, py, pw, ph = 60, 70, 780, 260
    midy = py + ph / 2
    els.append(line(px, midy, px + pw, midy, color=MUTED, sw=1))     # вісь нуля
    els.append(line(px, py, px, py + ph, color=MUTED, sw=1))         # вісь V
    els.append(text(px + pw, midy + 18, "час", size=12, anchor="end", color=MUTED))
    # синус
    amp = ph / 2 - 16
    cyc = midy
    per = pw / 1.6
    pts = []
    for i in range(0, 401):
        t = pw * i / 400.0
        v = math.sin(2 * math.pi * t / per)
        pts.append("%.1f,%.1f" % (px + t, cyc - amp * v))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
               % (" ".join(pts), INK))
    # точка A — на крутому схилі (нуль-перехід): велика похибка
    def at(tpx):
        v = math.sin(2 * math.pi * tpx / per)
        return cyc - amp * v
    tA = per * 0.5   # нуль-перехід (найкрутіший нахил)
    xA = px + tA
    dt = 26.0
    els.append(line(xA, py, xA, py + ph, color="#e5e7eb", sw=1))
    els.append(line(xA + dt, py, xA + dt, py + ph, color="#e5e7eb", sw=1, dash="3,3"))
    els.append(circle(xA, at(tA), 4, fill=POS, stroke=POS))
    els.append(circle(xA + dt, at(tA + dt), 4, fill=POS, stroke=POS))
    # позначки Δt і ΔV
    els.append(line(xA, at(tA) + 34, xA + dt, at(tA) + 34, color=POS, sw=1.6))
    els.append(text(xA + dt / 2, at(tA) + 50, "Δt", size=13, color=POS, bold=True))
    els.append(line(xA + dt + 10, at(tA), xA + dt + 10, at(tA + dt), color=POS, sw=1.6))
    els.append(text(xA + dt + 30, (at(tA) + at(tA + dt)) / 2 + 4, "ΔV велика", size=12, color=POS, bold=True))
    els.append(text(xA, py - 6, "крутий схил", size=12, color=POS, anchor="middle"))
    # точка B — на вершині (нахил ≈ 0): похибка мала
    tB = per * 0.75  # вершина/западина, нахил малий
    # оберемо максимум (де похідна 0): t де sin= ±1 → cos=0 → tB such that 2π t/per = 3π/2 (мінімум)
    tB = per * 0.75
    xB = px + tB
    els.append(line(xB, py, xB, py + ph, color="#eef2ff", sw=1))
    els.append(line(xB + dt, py, xB + dt, py + ph, color="#eef2ff", sw=1, dash="3,3"))
    els.append(circle(xB, at(tB), 4, fill=NEG, stroke=NEG))
    els.append(circle(xB + dt, at(tB + dt), 4, fill=NEG, stroke=NEG))
    els.append(text(xB + dt / 2 + 6, at(tB) + 22, "той самий Δt →", size=11, color=NEG, anchor="middle"))
    els.append(text(xB + dt / 2 + 6, at(tB) + 38, "ΔV майже 0", size=12, color=NEG, bold=True, anchor="middle"))
    els.append(text(xB, py - 6, "пологий верх", size=12, color=NEG, anchor="middle"))
    render(os.path.join(IMG, "jitter.svg"), W, H, *els)


# ── 4. Надвибірка розсуває перехідну смугу антиаліас-фільтра ─────────────────
def fig_oversampling():
    W, H = 900, 430
    els = []
    els.append(text(W / 2, 28, "Надвибірка розсуває проміжок B…(fs−B): фільтру легше",
                    size=15, bold=True))

    def panel(ox, oy, ow, oh, fs_rel, title, tight):
        e = []
        x0, yb = ox, oy + oh
        e.append(rect(ox, oy, ow, oh, fill=BG, stroke=MUTED, sw=1))
        e.append(text(ox + ow / 2, oy - 10, title, size=13, bold=True))
        e.append(line(x0, yb, x0 + ow, yb, color=INK, sw=1.4))          # вісь f
        e.append(line(x0, oy + 12, x0, yb, color=INK, sw=1.4))          # вісь |X|
        # смуга сигналу B (частка ширини = B), і дзеркало довкола fs/2
        B = 0.16
        bx = x0 + ow * B
        # корисна смуга (0..B)
        e.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s" fill-opacity="0.85" stroke="%s"/>'
                 % (x0, yb, bx, oy + 20, x0, oy + 20, "#cfe8d6", FIELD))
        e.append(text(x0 + 6, yb + 18, "B", size=12, color=FIELD, bold=True, anchor="start"))
        # позиція fs/2 та fs
        fs = fs_rel
        fs2x = x0 + ow * (fs / 2.0)
        e.append(line(fs2x, oy + 12, fs2x, yb, color=NEG, sw=1.4, dash="5,4"))
        e.append(text(fs2x, oy + 8, "fs/2", size=11, color=NEG, anchor="middle"))
        # дзеркальний образ (аліаси) довкола fs: (fs−B .. fs)
        aR = x0 + ow * fs
        aL = x0 + ow * (fs - B)
        e.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s" fill-opacity="0.75" stroke="%s"/>'
                 % (aR, yb, aL, oy + 26, aR, oy + 26, "#f6d5cf", POS))
        e.append(text(aL - 4, yb + 18, "образ", size=11, color=POS, anchor="end"))
        # перехідна смуга B…(fs−B) — те, що має погасити фільтр
        gapL = bx
        gapR = aL
        e.append(line(gapL, yb + 30, gapR, yb + 30, color=INK, sw=1.6))
        e.append(text((gapL + gapR) / 2, yb + 44,
                      ("вузько" if tight else "широко") + ": B…(fs−B)",
                      size=12, color=(POS if tight else FIELD), bold=True, anchor="middle"))
        return e

    els += panel(70, 80, 340, 200, 0.42, "fs ≈ 2.5·B (ледь-ледь)", tight=True)
    els += panel(490, 80, 340, 200, 0.95, "fs ≈ 6·B (надвибірка)", tight=False)
    els.append(text(W / 2, 400,
                    "Вузький проміжок вимагає крутого (дорогого) фільтра; надвибірка робить проміжок широким — вистачає простого RC.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "oversampling.svg"), W, H, *els)


# ── 5. Точка зламу: викид тягне середнє, медіану — ні ────────────────────────
def fig_breakdown():
    W, H = 900, 430
    els = []
    els.append(text(W / 2, 30,
                    "Точка зламу: один викид зсуває середнє необмежено, медіану — ні",
                    size=15, bold=True))
    # числова вісь; дев'ять «чесних» читань купкою ліворуч, десяте — викид ПОЗА шкалою
    ax_y = 210
    x0, x1 = 70, 620
    els.append(line(x0, ax_y, x1 + 10, ax_y, color=INK, sw=1.4))
    els.append(text(x1 + 18, ax_y + 5, "значення", size=12, anchor="start", color=MUTED))
    # дев'ять читань довкола «істини» у лівій третині (шкала показує лише околицю купки)
    cluster = [0.06, 0.08, 0.10, 0.11, 0.12, 0.13, 0.15, 0.17, 0.19]  # медіана купки = 0.12
    outlier_real = 3.5   # величезний викид (10σ і більше) — на шкалу не влазить
    def px_of(fr):
        return x0 + (x1 - x0) * fr
    for fr in cluster:
        els.append(circle(px_of(fr), ax_y, 5, fill=NEG, stroke=NEG))
    els.append(text(px_of(0.125), ax_y + 26, "дев'ять чесних читань", size=12, color=NEG, anchor="middle"))
    # викид — за правим краєм: стрілка «за шкалу»
    els.append(arrow(x1 - 30, ax_y, x1 + 8, ax_y, color=POS, sw=2.6))
    els.append(text(x1 - 4, ax_y - 14, "викид ≫", size=12, color=POS, bold=True, anchor="end"))
    els.append(text(x1 - 4, ax_y + 20, "(далеко, поза шкалою)", size=10, color=POS, anchor="end"))
    # медіана десяти — п'яте/шосте за порядком, стоїть у самій купці (викид скраю шеренги)
    med = 0.125
    els.append(line(px_of(med), ax_y - 62, px_of(med), ax_y + 12, color=FIELD, sw=2.6))
    els.append(text(px_of(med), ax_y - 68, "медіана — у купці", size=13, color=FIELD, bold=True, anchor="middle"))
    # середнє — потягнуте викидом далеко праворуч (≈ (сума купки + 3.5)/10 ≈ 0.46)
    mean = (sum(cluster) + outlier_real) / 10.0
    els.append(line(px_of(mean), ax_y - 40, px_of(mean), ax_y + 12, color=POS, sw=2.6, dash="5,4"))
    els.append(text(px_of(mean), ax_y - 46, "середнє — потягнуте", size=13, color=POS, bold=True, anchor="middle"))
    els.append(arrow(px_of(med) + 8, ax_y + 46, px_of(mean) - 6, ax_y + 46, color=POS, sw=2))
    els.append(text((px_of(med) + px_of(mean)) / 2, ax_y + 64,
                    "один викид тягне сюди", size=11, color=POS, anchor="middle"))
    # права колонка — суть точки зламу
    body, bw, bh = textbox(770, 210,
        ["Точка зламу —", "частка «зіпсутих»,", "що зриває оцінку:", "",
         "середнє: 0%",
         "(1 викид → ∞)", "",
         "медіана: 50%",
         "(тримає, поки", "чесних більшість)"],
        size=13, pad=12)
    els.append(body)
    els.append(text(W / 2, 405,
                    "Медіана дивиться на ПОРЯДОК, тож розмір викиду їй байдужий; середнє додає його значення.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "breakdown.svg"), W, H, *els)


# ── 6. Ціна стійкості: ефективність vs точка зламу ───────────────────────────
def fig_efficiency():
    W, H = 900, 440
    els = []
    els.append(text(W / 2, 30,
                    "Ціна стійкості: що стійкіша оцінка, то менше вона «вичавлює» з чистих даних",
                    size=15, bold=True))
    # осі: X — точка зламу (0..50%), Y — ефективність на гаусі (0..100%)
    px, py, pw, ph = 90, 70, 560, 300
    x0, yb = px, py + ph
    els.append(line(x0, yb, x0 + pw, yb, color=INK, sw=1.5))
    els.append(line(x0, py, x0, yb, color=INK, sw=1.5))
    els.append(text(x0 + pw / 2, yb + 40, "точка зламу (стійкість) →", size=13, anchor="middle", color=MUTED))
    # підписи осі X
    for fr, lab in [(0.0, "0%"), (0.25, "25%"), (0.5, "50%")]:
        gx = x0 + pw * (fr / 0.5)
        els.append(line(gx, yb, gx, yb + 5, color=INK, sw=1.2))
        els.append(text(gx, yb + 20, lab, size=11, anchor="middle", color=MUTED))
    # підпис осі Y (вертикально)
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">ефективність на гаусі</text>'
               % (px - 44, py + ph / 2, FONT, MUTED, px - 44, py + ph / 2))
    for fr, lab in [(0.0, "0%"), (0.5, "50%"), (0.637, "64%"), (0.83, "83%"), (1.0, "100%")]:
        gy = yb - ph * fr
        els.append(line(x0 - 5, gy, x0, gy, color=INK, sw=1.2))
        els.append(text(x0 - 10, gy + 4, lab, size=10, anchor="end", color=MUTED))
        els.append(line(x0, gy, x0 + pw, gy, color="#eef0f3", sw=1))
    def pt(bp, eff):
        return x0 + pw * (bp / 0.5), yb - ph * eff
    # три оцінки
    mx, my = pt(0.0, 1.0)       # середнє
    tx, ty = pt(0.25, 0.83)     # усічене 20–25% (ефективність ~83%, точка зламу ~25%)
    dx, dy = pt(0.5, 0.637)     # медіана
    # сполучна лінія-компроміс
    els.append(line(mx, my, tx, ty, color=MUTED, sw=1.6, dash="4,4"))
    els.append(line(tx, ty, dx, dy, color=MUTED, sw=1.6, dash="4,4"))
    els.append(circle(mx, my, 7, fill=POS, stroke=POS))
    els.append(circle(tx, ty, 7, fill=FIELD, stroke=FIELD))
    els.append(circle(dx, dy, 7, fill=NEG, stroke=NEG))
    els.append(text(mx + 10, my - 8, "середнє", size=13, color=POS, anchor="start", bold=True))
    els.append(text(mx + 10, my + 9, "100% / злам 0%", size=11, color=POS, anchor="start"))
    els.append(text(tx + 12, ty - 8, "усічене 25%", size=13, color=FIELD, anchor="start", bold=True))
    els.append(text(tx + 12, ty + 9, "~83% / злам 25%", size=11, color=FIELD, anchor="start"))
    els.append(text(dx - 12, dy - 8, "медіана", size=13, color=NEG, anchor="end", bold=True))
    els.append(text(dx - 12, dy + 9, "64% / злам 50%", size=11, color=NEG, anchor="end"))
    # права колонка — читання графіка
    body, bw, bh = textbox(775, 220,
        ["Читати так:", "",
         "→ праворуч = стійкіше",
         "↓ нижче = дорожче",
         "  (треба більше N", "   на ту саму тишу)", "",
         "Медіана коштує ~36%:",
         "її 100 читань дають",
         "тишу ~64 читань", "середнього"],
        size=12, pad=12)
    els.append(body)
    render(os.path.join(IMG, "efficiency.svg"), W, H, *els)


# ── 7. Мережа порівнянь-обмінів для медіани з 5 (7 компараторів) ─────────────
def fig_median_net5():
    W, H = 940, 380
    els = []
    els.append(text(W / 2, 30,
                    "Мережа порівнянь-обмінів: медіана з 5 за 7 фіксованих кроків (без гілок)",
                    size=15, bold=True))
    # п'ять горизонтальних «дротів» x0..x1
    x0, x1 = 120, 720
    ys = [80, 130, 180, 230, 280]
    labs = ["a", "b", "c", "d", "e"]
    for i, y in enumerate(ys):
        els.append(line(x0, y, x1, y, color=INK, sw=1.6))
        els.append(text(x0 - 14, y + 5, labs[i], size=14, anchor="end", color=INK, bold=True))
    # компаратор: вертикаль між двома дротами + кружки-кінці (менше осідає вгору)
    def comp(col_x, ia, ib, col=NEG):
        ya, yb = ys[ia], ys[ib]
        e = [line(col_x, ya, col_x, yb, color=col, sw=2.2)]
        e.append(circle(col_x, ya, 4.5, fill=col, stroke=col))
        e.append(circle(col_x, yb, 4.5, fill=col, stroke=col))
        return e
    # ПЕРЕВІРЕНА мережа: медіана-з-5 осідає на дроті c (wire 2) за 7 compare-exchange.
    # (мінімум для oblivious-мережі; «6 порівнянь» — це адаптивний алгоритм із гілками).
    # Послідовність пар (0..4 = a..e): (0,1)(2,3)(0,2)(1,3)(1,2)(1,4)(2,4).
    xs = [165, 220, 285, 350, 420, 490, 560]
    cols = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2), (1, 4), (2, 4)]
    palette = [NEG, NEG, FIELD, FIELD, POS, MUTED, MUTED]
    for k, (ia, ib) in enumerate(cols):
        cx = xs[k]
        for frag in comp(cx, ia, ib, palette[k]):
            els.append(frag)
        els.append(text(cx, 312, str(k + 1), size=12, color=palette[k], anchor="middle", bold=True))
    els.append(text((xs[0] + xs[-1]) / 2, 334, "сім кроків (номери) — послідовність compare-exchange",
                    size=12, color=MUTED, anchor="middle"))
    # вихід: медіана на дроті c
    els.append(circle(x1, ys[2], 7, fill=FIELD, stroke=FIELD))
    els.append(text(x1 + 14, ys[2] + 5, "медіана", size=13, color=FIELD, anchor="start", bold=True))
    # легенда праворуч
    body, bw, bh = textbox(838, 120,
        ["Крок = compare-", "exchange:", "порівняй пару,",
         "менше — вгору,", "більше — вниз.", "",
         "Жодних if-гілок,", "фіксований час —",
         "ідеально для МК."],
        size=12, pad=11)
    els.append(body)
    render(os.path.join(IMG, "median-net5.svg"), W, H, *els)


if __name__ == "__main__":
    fig_quadrature()
    fig_tau_budget()
    fig_jitter()
    fig_oversampling()
    fig_breakdown()
    fig_efficiency()
    fig_median_net5()
    print("OK: quadrature, tau-budget, jitter, oversampling, breakdown, efficiency, median-net5")
