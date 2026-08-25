# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Пойкерта й доступна ємність».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут, AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Доступна ємність падає зі струмом: свинець крутіше за літій ───────────
def fig_capacity_vs_rate():
    W, H = 840, 430
    f = [text(W / 2, 28, "Доступна ємність тане зі струмом розряду", size=17, bold=True)]

    # осі
    ox, oy = 110, 350        # початок координат
    ax_w, ax_h = 640, 270
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # Y
    f.append(text(ox + ax_w / 2, oy + 48, "струм розряду (C-rate)", size=12, color=INK, bold=True))
    # вертикальний підпис Y
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 34 %.1f)">'
             'доступна ємність, %%</text>' % (oy - ax_h / 2, FONT, INK, oy - ax_h / 2))

    # мітки X: 0.05C … 5C (лог-подібна розкладка по позиції)
    xr = [(0.05, "0.05C"), (0.2, "0.2C"), (1.0, "1C"), (2.0, "2C"), (5.0, "5C")]
    def xpos(c):
        # логарифмічно між 0.05 і 5
        lo, hi = math.log10(0.05), math.log10(5.0)
        return ox + (math.log10(c) - lo) / (hi - lo) * ax_w
    for c, lab in xr:
        x = xpos(c)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, lab, size=10, color=MUTED))
    # мітки Y: 40..100%
    for pct in (40, 60, 80, 100):
        y = oy - (pct - 30) / 70 * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(text(ox - 14, y + 4, str(pct), size=10, color=MUTED, anchor="end"))
        f.append(line(ox, y, ox + ax_w, y, color="#e5e7eb", sw=1))

    def ypos(pct):
        return oy - (pct - 30) / 70 * ax_h

    # криві: доступна ємність (у % від номіналу за 0.05C) як функція C-rate
    # спрощена ілюстративна модель на базі показника Пойкерта
    def avail_pct(c, k):
        # ємність відносно повільного розряду, нормовано до 100% біля 0.05C
        base = 0.05
        return 100.0 * (base / c) ** (k - 1.0)

    cs = [0.05 * (100 ** (i / 60.0)) for i in range(61)]  # від 0.05 до 5

    # свинцевий (k≈1.25) — сильно падає
    pts_pb = " ".join("%.1f,%.1f" % (xpos(c), ypos(min(100, avail_pct(c, 1.25)))) for c in cs)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts_pb, POS))
    # літієвий (k≈1.05) — майже пласко
    pts_li = " ".join("%.1f,%.1f" % (xpos(c), ypos(min(100, avail_pct(c, 1.05)))) for c in cs)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts_li, NEG))

    # підписи кривих
    f.append(text(xpos(3.2), ypos(avail_pct(3.2, 1.05)) - 12, "літій  k≈1.05", size=11, color=NEG, bold=True))
    f.append(text(xpos(1.6), ypos(avail_pct(1.6, 1.25)) + 22, "свинець  k≈1.25", size=11, color=POS, bold=True))

    # позначка «наклейка міряється тут»
    xt = xpos(0.05)
    f.append(line(xt, oy, xt, ypos(100), color=FIELD, sw=1.5, dash="4 3"))
    box, bw, bh = textbox(xt + 92, ypos(100) - 4, "наклейку\nміряють тут\n(повільний розряд)",
                          size=9.5, color=FIELD, stroke=FIELD, fill="#eef6ef", pad=7)
    f.append(box)

    render(os.path.join(IMG, "capacity-vs-rate.svg"), W, H, *f)


# ── 2. Механізм: швидкий розряд «скручує» лише поверхню електрода ────────────
def fig_mechanism():
    W, H = 840, 400
    f = [text(W / 2, 28, "Чому швидкий розряд бере менше: реакція не встигає вглиб", size=16, bold=True)]

    # два електроди-блоки: повільний (ліворуч) і швидкий (праворуч)
    def electrode(x0, title, reacted_frac, col_title):
        y0, ew, eh = 90, 250, 210
        # рамка «пористий електрод»
        f.append(rect(x0, y0, ew, eh, fill="#f7f9fb", stroke=LINE, sw=2, rx=8))
        f.append(text(x0 + ew / 2, y0 - 14, title, size=13, color=col_title, bold=True))
        # «глибина» — вертикальні шари; прореагувала лише частина від поверхні (лівий край)
        layers = 10
        for i in range(layers):
            lx = x0 + 8 + i * (ew - 16) / layers
            lw = (ew - 16) / layers - 2
            deep = i / layers          # 0 = поверхня, →1 глибина
            if deep < reacted_frac:
                fill = "#fdecea"       # прореагувало (розряджено)
                st = POS
            else:
                fill = "#eef6ef"       # ще повний запас (не дістали)
                st = FIELD
            f.append(rect(lx, y0 + 24, lw, eh - 44, fill=fill, stroke=st, sw=1.2, rx=3))
        # підписи «поверхня» / «глибина»
        f.append(text(x0 + 14, y0 + eh + 16, "поверхня", size=9.5, color=POS, anchor="start"))
        f.append(text(x0 + ew - 14, y0 + eh + 16, "глибина пор", size=9.5, color=FIELD, anchor="end"))
        # стрілка іонів усередину
        return y0, eh

    y0, eh = electrode(70, "Повільний струм (0.1C)", 0.9, NEG)
    electrode(500, "Швидкий струм (3C)", 0.35, POS)

    # стрілки-іони: повільно встигають глибоко, швидко — лише скраю
    for i, dx in enumerate((30, 70, 120, 180, 230)):
        f.append(arrow(70 + 8, 130 + i * 12, 70 + 8 + dx, 130 + i * 12, color=NEG, sw=1.4))
    for i, dx in enumerate((22, 40, 55, 66, 74)):
        f.append(arrow(500 + 8, 130 + i * 12, 500 + 8 + dx, 130 + i * 12, color=POS, sw=1.4))

    # підсумкові плашки під кожним
    b1 = fitbox(70, 330, 250, 46,
                "іони встигають дійти вглиб →\nпрацює майже весь об'єм",
                size=10.5, color=NEG, stroke=NEG, fill="#eef2fd")
    f.append(b1)
    b2 = fitbox(500, 330, 250, 46,
                "встигає лише поверхня →\nглибина «замкнена», ємність втрачено",
                size=10.5, color=POS, stroke=POS, fill="#fdecea")
    f.append(b2)

    render(os.path.join(IMG, "mechanism.svg"), W, H, *f)


# ── 3. Пастка розрахунку часу: наївне Q/I бреше в більший бік ────────────────
def fig_runtime():
    W, H = 820, 330
    f = [text(W / 2, 28, "Пастка: наївне «ємність ÷ струм» обіцяє задовгий час", size=16, bold=True)]

    # дві горизонтальні смуги-таймлайни
    x0, bw = 150, 560
    def bar(y, frac, col, label, tval):
        f.append(rect(x0, y, bw, 34, fill="#f0f1f3", stroke=LINE, sw=1.2, rx=6))
        f.append(rect(x0, y, bw * frac, 34, fill=col, stroke=col, sw=1, rx=6))
        f.append(text(x0 - 12, y + 22, label, size=11, color=INK, anchor="end", bold=True))
        f.append(text(x0 + bw * frac + 8, y + 22, tval, size=11, color=col, anchor="start", bold=True))

    # наївний прогноз (весь такий довгий = 100% смуги)
    bar(90, 1.0, NEG, "наївно  Q/I", "= 60 хв (очікуване)")
    # реальний час коротший (Пойкерт з'їв частину)
    bar(150, 0.62, POS, "насправді", "≈ 37 хв")

    # дужка «недоотримано» між кінцем червоної та кінцем сірої
    xr = x0 + bw * 0.62
    xe = x0 + bw
    f.append(line(xr, 200, xe, 200, color=MUTED, sw=1.2))
    f.append(line(xr, 196, xr, 204, color=MUTED, sw=1.2))
    f.append(line(xe, 196, xe, 204, color=MUTED, sw=1.2))
    f.append(text((xr + xe) / 2, 220, "цих ~23 хв ніколи не буде", size=10.5, color=MUTED))

    # підпис-умова
    b = fitbox(150, 250, 560, 46,
               "пакет 5 А·год, розряд 5 А (1C), свинець k≈1.3:  наївно t=Q/I=1 год, "
               "а закон Пойкерта дає лише ~0.62 год",
               size=10.5, color=INK, stroke=MUTED, fill=FILL)
    f.append(b)

    render(os.path.join(IMG, "runtime.svg"), W, H, *f)


# ── 4. Чутливість до k: пучок кривих C/C₀ від I₀/I для різних показників ──────
def fig_k_sensitivity():
    W, H = 840, 440
    f = [text(W / 2, 28, "Доступна ємність гостро залежить від показника k", size=17, bold=True)]

    ox, oy = 100, 360           # початок координат
    ax_w, ax_h = 620, 285
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # Y
    f.append(text(ox + ax_w / 2, oy + 50, "відношення I₀ / I   (← більший струм)", size=12, color=INK, bold=True))
    f.append('<text x="30" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 30 %.1f)">'
             'C / C₀, %%</text>' % (oy - ax_h / 2, FONT, INK, oy - ax_h / 2))

    # X: відношення I0/I від 0.02 (струм у 50×) до 1 (паспортний), логарифмічно
    lo, hi = math.log10(0.02), math.log10(1.0)
    def xpos(r):
        return ox + (math.log10(r) - lo) / (hi - lo) * ax_w
    for r, lab in [(0.02, "0.02"), (0.05, "0.05"), (0.125, "0.125"), (0.3, "0.3"), (1.0, "1")]:
        x = xpos(r)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, lab, size=10, color=MUTED))
    # Y: 30..100 %
    def ypos(pct):
        return oy - (pct - 30) / 70 * ax_h
    for pct in (30, 40, 60, 80, 100):
        y = ypos(pct)
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(text(ox - 12, y + 4, str(pct), size=10, color=MUTED, anchor="end"))
        f.append(line(ox, y, ox + ax_w, y, color="#e5e7eb", sw=1))

    rs = [0.02 * (50 ** (i / 60.0)) for i in range(61)]   # 0.02 … 1
    ks = [(1.05, NEG), (1.15, "#7aa0e8"), (1.25, MUTED), (1.30, "#e08a3c"), (1.40, POS)]
    for k, col in ks:
        pts = " ".join("%.1f,%.1f" % (xpos(r), ypos(min(100.0, 100.0 * r ** (k - 1.0)))) for r in rs)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, col))
        # підпис праворуч від лівого краю кривої
        yl = ypos(min(100.0, 100.0 * rs[0] ** (k - 1.0)))
        f.append(text(xpos(rs[0]) + 34, yl + 4, "k=%.2f" % k, size=10.5, color=col, bold=True, anchor="start"))

    # вертикаль «типовий великий струм» на 0.125 і дужка розкиду
    xk = xpos(0.125)
    f.append(line(xk, ypos(100), xk, oy, color=FIELD, sw=1.3, dash="4 3"))
    ytop = ypos(100.0 * 0.125 ** (1.05 - 1.0))     # k=1.05 тут
    ybot = ypos(100.0 * 0.125 ** (1.40 - 1.0))     # k=1.40 тут
    f.append(line(xk - 6, ytop, xk - 6, ybot, color=INK, sw=1.3))
    f.append(line(xk - 10, ytop, xk - 2, ytop, color=INK, sw=1.3))
    f.append(line(xk - 10, ybot, xk - 2, ybot, color=INK, sw=1.3))
    box, bw, bh = textbox(xk - 96, (ytop + ybot) / 2, "той самий струм,\nале k від 1.05 до 1.40:\nвід ~90% до ~44%",
                          size=9.5, color=INK, stroke=MUTED, fill=FILL, pad=7)
    f.append(box)

    render(os.path.join(IMG, "k-sensitivity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_capacity_vs_rate()
    fig_mechanism()
    fig_runtime()
    fig_k_sensitivity()
    print("OK: figs written to", IMG)
