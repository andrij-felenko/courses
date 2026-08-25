# -*- coding: utf-8 -*-
"""Фігури до теми «Струм, заклинювання й нагрів мотора».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Струм росте з навантаженням: проти-ЕРС падає → I=(V−E)/R ───────────────
def fig_load_current():
    W, H = 720, 410
    f = [text(W / 2, 28, "Навантаження гальмує ротор → проти-ЕРС падає → струм росте",
              size=16, bold=True)]
    ox, oy = 95, 330
    ax_w, ax_h = 540, 244
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 44, "навантаження на валу  (момент опору)  →",
                  size=12, color=INK))
    f.append(mtext(ox - 66, oy - ax_h / 2 - 10, ["струм", "I", "обмотки"],
                   size=11, color=INK, lh=1.2))

    # позначки осі X: холості → робоче → стопор
    for frac, lab in [(0.0, "0\n(холості)"), (0.5, "робоче"), (1.0, "стопор")]:
        x = ox + frac * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(mtext(x, oy + 20, lab, size=10.5, color=MUTED, lh=1.1))

    # лінія струму: від малого (холості) до V/R (стопор) — росте лінійно з моментом
    x0, y0 = ox, oy - 0.10 * ax_h
    x1, y1 = ox + ax_w, oy - 1.0 * ax_h
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.8"/>'
             % (x0, y0, x1, y1, NEG))
    # рівень V/R угорі
    f.append(line(ox, y1, ox + ax_w, y1, color=POS, sw=1.4, dash="6,5"))
    f.append(text(ox + 6, y1 - 8, "I = V/R  — стеля струму (стопорний)", size=11.5,
                  color=POS, anchor="start", bold=True))

    def dot(frac, ipct, col):
        x = ox + frac * ax_w
        y = oy - ipct / 100.0 * ax_h
        f.append(circle(x, y, 5, fill=BG, stroke=col, sw=2.4))
        return x, y

    dx, dy = dot(0.0, 10, NEG)
    b, _, _ = textbox(dx + 86, dy - 4, "холості: E≈V,\nструм майже нуль", size=11,
                      fill="#eaf0fd", stroke=NEG)
    f.append(b)
    dx, dy = dot(0.5, 55, "#e08a3c")
    b, _, _ = textbox(dx + 4, dy + 30, "робоча точка:\nстільки струму, скільки\nвимагає навантаження", size=11,
                      fill=FILL, stroke="#e08a3c")
    f.append(b)
    dx, dy = dot(1.0, 100, POS)
    b, _, _ = textbox(dx - 96, dy + 30, "стопор: E=0,\nструм максимальний", size=11,
                      fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "load-current.svg"), W, H, *f)


# ── 2. Чому нагрів ∝ I²: квадрат струму, і чому стопор пече ───────────────────
def fig_i2r_heat():
    W, H = 720, 420
    f = [text(W / 2, 28, "Тепло росте як КВАДРАТ струму: P = I²R",
              size=16, bold=True)]
    ox, oy = 95, 340
    ax_w, ax_h = 540, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "струм  I  (частка від стопорного V/R)  →",
                  size=12, color=INK))
    f.append(mtext(ox - 66, oy - ax_h / 2 - 10, ["тепло", "P = I²R", "(частка", "макс.)"],
                   size=11, color=INK, lh=1.2))

    for frac, lab in [(0.0, "0"), (0.5, "½"), (1.0, "1")]:
        x = ox + frac * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(text(x, oy + 20, lab, size=10.5, color=MUTED))
    for pv, lab in [(0, "0"), (25, "¼"), (50, "½"), (100, "1")]:
        y = oy - pv / 100.0 * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 20, y + 4, lab, size=10.5, color=MUTED))

    # парабола P = I²
    pts = []
    N = 60
    for i in range(N + 1):
        fr = i / float(N)
        x = ox + fr * ax_w
        y = oy - (fr * fr) * ax_h
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), POS))

    # двократний струм → чотирикратне тепло (наочно)
    def vmark(fr, col, lab, dxl, dyl):
        x = ox + fr * ax_w
        y = oy - (fr * fr) * ax_h
        f.append(line(x, oy, x, y, color=col, sw=1.3, dash="4,4"))
        f.append(line(ox, y, x, y, color=col, sw=1.3, dash="4,4"))
        f.append(circle(x, y, 5, fill=BG, stroke=col, sw=2.4))
        b, _, _ = textbox(x + dxl, y + dyl, lab, size=11, fill="#fff", stroke=col)
        f.append(b)

    vmark(0.5, NEG, "пів-струму\n→ чверть тепла", 96, 8)
    vmark(1.0, POS, "стопор: повний струм\n→ повне (макс.) тепло", -120, 44)
    # підпис до квадратичності
    b, _, _ = textbox(ox + 150, oy - 220, "вдвічі більший струм\n= вчетверо більше тепла",
                      size=12, fill="#fdecea", stroke=POS, bold=True, min_w=250)
    f.append(b)
    render(os.path.join(IMG, "i2r-heat.svg"), W, H, *f)


# ── 3. Тепловий баланс: приплив I²R vs відведення; теплова стала ──────────────
def fig_thermal_balance():
    W, H = 720, 400
    f = [text(W / 2, 28, "Температура встановлюється там, де відведення зрівняє приплив тепла",
              size=16, bold=True)]

    # ліва панель — баланс «приплив / відведення»
    cx, cy = 200, 210
    f.append(circle(cx, cy, 64, fill="#fdf1ee", stroke=POS, sw=2))
    f.append(mtext(cx, cy - 6, ["обмотка", "T"], size=13, color=INK, lh=1.25, bold=True))
    # приплив тепла — стрілка всередину
    f.append(arrow(cx - 150, cy, cx - 70, cy, color=POS, sw=2.6))
    b, _, _ = textbox(cx - 150, cy - 40, "приплив\nP = I²R", size=12, fill="#fdecea",
                      stroke=POS, bold=True)
    f.append(b)
    # відведення — стрілки назовні
    for ang in (-50, 0, 50):
        a = math.radians(ang)
        x2 = cx + math.cos(a) * 140
        y2 = cy + math.sin(a) * 140
        x1 = cx + math.cos(a) * 70
        y1 = cy + math.sin(a) * 70
        f.append(arrow(x1, y1, x2, y2, color=NEG, sw=2.2))
    b, _, _ = textbox(cx + 150, cy + 92, "відведення\n∝ (T − T_довк.)", size=12,
                      fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b)
    b, _, _ = textbox(cx, cy + 150, "рівновага: приплив = відведення → стала T",
                      size=11.5, fill=FILL, stroke=MUTED, min_w=300)
    f.append(b)

    # права панель — нагрів у часі з тепловою сталою τ
    ox, oy = 430, 300
    ax_w, ax_h = 250, 210
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    f.append(text(ox + ax_w / 2, oy + 30, "час  →", size=11, color=INK))
    f.append(mtext(ox - 30, oy - ax_h + 8, ["T"], size=12, color=INK))

    # робочий струм — виходить на безпечне плато
    pts1 = []
    for i in range(61):
        t = i / 60.0
        y = oy - (1 - math.exp(-3 * t)) * ax_h * 0.42
        pts1.append("%.1f,%.1f" % (ox + t * ax_w, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts1), NEG))
    f.append(line(ox, oy - ax_h * 0.42, ox + ax_w, oy - ax_h * 0.42,
                  color=NEG, sw=1, dash="4,4"))
    f.append(text(ox + ax_w - 4, oy - ax_h * 0.42 - 6, "робочий: безпечне плато",
                  size=10, color=NEG, anchor="end"))

    # стопор — лізе вгору за межу за секунди
    pts2 = []
    for i in range(61):
        t = i / 60.0
        y = oy - (1 - math.exp(-3.4 * t)) * ax_h * 1.9
        y = max(y, oy - ax_h)
        pts2.append("%.1f,%.1f" % (ox + t * ax_w, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts2), POS))
    # лінія допустимої межі
    f.append(line(ox, oy - ax_h * 0.82, ox + ax_w, oy - ax_h * 0.82,
                  color=INK, sw=1.4, dash="7,4"))
    f.append(text(ox + 4, oy - ax_h * 0.82 - 6, "межа ізоляції", size=10,
                  color=INK, anchor="start"))
    f.append(text(ox + ax_w - 4, oy - ax_h + 14, "стопор: вгору за секунди",
                  size=10, color=POS, anchor="end"))
    render(os.path.join(IMG, "thermal-balance.svg"), W, H, *f)


# ── 4. Робоча точка й вікно захисту: робочий / пік / стопор по струму ─────────
def fig_protection_window():
    W, H = 720, 360
    f = [text(W / 2, 28, "Драйвер і захист живуть між робочим струмом і стопорним",
              size=16, bold=True)]

    # горизонтальна вісь струму
    ox, oy = 70, 200
    ax_w = 580
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(text(ox + ax_w + 4, oy + 5, "I →", size=13, color=INK, anchor="start"))

    def band(x0, x1, col, fill):
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="4" '
                 'fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (ox + x0, oy - 11, x1 - x0, fill, col))

    # зони: робоча (зелена), пік (жовта), небезпека (червона)
    band(0, 200, FIELD, "#e8f6ec")
    band(200, 330, "#e08a3c", "#fbeede")
    band(330, ax_w, POS, "#fdecea")

    def tick(xx, lab, sub, col):
        x = ox + xx
        f.append(line(x, oy - 16, x, oy + 16, color=col, sw=2))
        f.append(circle(x, oy, 4.5, fill=BG, stroke=col, sw=2.2))
        b, _, _ = textbox(x, oy - 56, lab, size=12, fill="#fff", stroke=col, bold=True)
        f.append(b)
        f.append(text(x, oy + 40, sub, size=10.5, color=MUTED))

    tick(120, "робочий\nI_роб", "звичайна робота", FIELD)
    tick(265, "пік / пуск", "коротко OK", "#e08a3c")
    tick(420, "стопорний\nI = V/R", "тривало → горить", POS)

    # підписи зон
    f.append(mtext(ox + 110, oy + 64, ["тепло помірне,", "відводиться"], size=10.5,
                   color=FIELD, lh=1.2))
    f.append(mtext(ox + 265, oy + 64, ["перевантаження —", "лише на секунди"], size=10.5,
                   color="#cf7a2a", lh=1.2))
    f.append(mtext(ox + 455, oy + 64, ["захист мусить", "вимкнути ТУТ"], size=10.5,
                   color=POS, lh=1.2, bold=True))

    # підсумкове правило
    b, _, _ = textbox(W / 2, 314,
                      "правило: драйвер тримає I_роб тривало, пік — коротко;\n"
                      "стопорний струм має бути в межах драйвера або його ріже захист",
                      size=11.5, fill=FILL, stroke=MUTED, min_w=560)
    f.append(b)
    render(os.path.join(IMG, "protection-window.svg"), W, H, *f)


if __name__ == "__main__":
    fig_load_current()
    fig_i2r_heat()
    fig_thermal_balance()
    fig_protection_window()
    print("OK: 4 figures ->", IMG)
