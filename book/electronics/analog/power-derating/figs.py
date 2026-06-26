# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Класична крива derating ───────────────────────────────────────────────
def fig_curve():
    W, H = 660, 420
    # система координат графіка
    ox, oy = 90, 330          # початок осей (нижній лівий)
    pw, ph = 470, 250         # розмір поля графіка
    Tmin, Tmax = 0, 175       # вісь температури
    rated_T = 70              # до цієї температури — повні 100 %
    zero_T = 155             # тут крива сягає нуля (max робоча)

    def X(T): return ox + (T - Tmin) / (Tmax - Tmin) * pw
    def Y(pct): return oy - pct / 100.0 * ph

    frags = []
    # підкладка поля
    frags.append(rect(ox, oy - ph, pw, ph, fill="#fbfcfd", stroke="#dfe3e8", sw=1))
    # горизонтальні сітки 0/25/50/75/100 %
    for pct in (25, 50, 75, 100):
        frags.append(line(ox, Y(pct), ox + pw, Y(pct), color="#e6e9ee", sw=1))
        frags.append(text(ox - 10, Y(pct) + 5, "%d%%" % pct, size=12, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, Y(0) + 5, "0", size=12, color=MUTED, anchor="end"))

    # осі
    frags.append(arrow(ox, oy, ox, oy - ph - 12, color=INK, sw=1.8))
    frags.append(arrow(ox, oy, ox + pw + 12, oy, color=INK, sw=1.8))
    frags.append(text(ox - 56, oy - ph / 2, "частка", size=12, color=INK, anchor="middle"))
    frags.append(text(ox - 56, oy - ph / 2 + 16, "потужності", size=12, color=INK, anchor="middle"))
    frags.append(text(ox + pw / 2, oy + 44, "температура середовища, °C", size=13, color=INK))

    # позначки температури на осі
    for T in (25, 70, 100, 125, 155):
        frags.append(line(X(T), oy, X(T), oy + 5, color=INK, sw=1.4))
        frags.append(text(X(T), oy + 22, str(T), size=12, color=MUTED))

    # крива: пласка ділянка + спадна пряма
    frags.append(line(X(Tmin), Y(100), X(rated_T), Y(100), color=POS, sw=3))
    frags.append(line(X(rated_T), Y(100), X(zero_T), Y(0), color=POS, sw=3))
    # за нулем — заборонена зона (пунктир по осі)
    frags.append(line(X(zero_T), Y(0), X(Tmax), Y(0), color="#b9c0c9", sw=2, dash="5,5"))

    # точка зламу
    frags.append(circle(X(rated_T), Y(100), 4.5, fill=POS, stroke=POS))
    # вертикалі-орієнтири
    frags.append(line(X(rated_T), oy, X(rated_T), Y(100), color="#c9ced6", sw=1, dash="4,4"))
    frags.append(line(X(zero_T), oy, X(zero_T), Y(0), color="#c9ced6", sw=1, dash="4,4"))

    # підпис «100 % — повна паспортна» над пласкою
    b, w, h = textbox(X(35), Y(100) - 26, "повна паспортна", size=12,
                      fill="#fdecea", stroke=POS, color=POS)
    frags.append(b)

    # підпис «лінійний спад» уздовж нахилу
    frags.append(text(X(118), Y(46) - 4, "лінійний спад", size=12, color=POS, bold=True))

    # точка-приклад на 125 °C
    # частка на 125: (155-125)/(155-70)=30/85≈0.353
    pct125 = (zero_T - 125) / (zero_T - rated_T) * 100
    frags.append(circle(X(125), Y(pct125), 4.5, fill=NEG, stroke=NEG))
    frags.append(line(ox, Y(pct125), X(125), Y(pct125), color=NEG, sw=1, dash="4,4"))
    b, w, h = textbox(X(125) + 8, Y(pct125) - 22, "≈ 35 %", size=12,
                      fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b)

    render(os.path.join(IMG, "derating-curve.svg"), W, H, *frags,
           title="Крива зниження допустимої потужності")


# ── 2. Чому з'являється нахил: тепловий ланцюжок ─────────────────────────────
def fig_why():
    W, H = 680, 320
    frags = []

    # ліворуч: «термометр» переходу зі стелею Tj_max
    tx = 120
    top, bot = 70, 270
    scale_h = bot - top
    # стовпчик
    frags.append(rect(tx - 16, top, 32, scale_h, fill="#fbfcfd", stroke=LINE, sw=1.5))
    # стеля Tj_max
    frags.append(line(tx - 30, top, tx + 30, top, color=POS, sw=2.5))
    b, w, h = textbox(tx + 92, top, "стеля переходу  Tj(max)", size=12,
                      fill="#fdecea", stroke=POS, color=POS)
    frags.append(b)

    # два сценарії: прохолодне і гаряче середовище
    def column(cx, Ta_frac, P_frac, label, cool):
        col = []
        amb_y = bot - Ta_frac * scale_h          # рівень середовища
        jun_y = amb_y - P_frac * scale_h         # перехід = середовище + підйом
        # рівень середовища
        col.append(line(cx - 22, amb_y, cx + 22, amb_y, color=NEG, sw=2.2))
        # стовпчик підйому P·Rθ
        cc = "#fde9c7" if cool else "#f7c9b8"
        col.append(rect(cx - 14, jun_y, 28, amb_y - jun_y, fill=cc, stroke="#c8a99a", sw=1))
        # точка переходу
        col.append(circle(cx, jun_y, 4, fill=POS, stroke=POS))
        return col, amb_y, jun_y

    # прохолодне середовище: низький Ta, можна великий підйом → велика P
    c1, amb1, jun1 = column(tx, 0.12, 0.74, "прохолодно", True)
    # гаряче середовище: високий Ta, лишилось мало запасу → мала P
    c2, amb2, jun2 = column(0, 0, 0, "", True)  # placeholder, не використовуємо

    frags += c1
    # горизонтальна стеля через увесь графік як орієнтир
    frags.append(line(tx - 30, top, 560, top, color=POS, sw=1, dash="5,5"))

    # другий стовпчик праворуч
    rx = 360
    top2, bot2 = top, bot
    frags.append(rect(rx - 16, top2, 32, bot2 - top2, fill="#fbfcfd", stroke=LINE, sw=1.5))
    # гаряче середовище
    amb_hot = bot2 - 0.55 * scale_h
    frags.append(line(rx - 22, amb_hot, rx + 22, amb_hot, color=NEG, sw=2.2))
    # запас до стелі малий → підйом малий
    jun_hot = top2 + 6
    frags.append(rect(rx - 14, jun_hot, 28, amb_hot - jun_hot, fill="#f7c9b8", stroke="#c8a99a", sw=1))
    frags.append(circle(rx, jun_hot, 4, fill=POS, stroke=POS))

    # підписи середовища
    b, w, h = textbox(tx, bot + 26, "прохолодне Ta", size=12, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b)
    b, w, h = textbox(rx, bot + 26, "гаряче Ta", size=12, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b)

    # стрілки-підписи «підйом = P·Rθ»
    frags.append(text(tx + 70, (amb1 + jun1) / 2, "підйом", size=12, color=INK, anchor="start"))
    frags.append(text(tx + 70, (amb1 + jun1) / 2 + 16, "= P·Rθ", size=12, color=INK, anchor="start"))
    frags.append(text(rx + 56, (amb_hot + jun_hot) / 2 + 6, "малий запас", size=12, color=MUTED, anchor="start"))
    frags.append(text(rx + 56, (amb_hot + jun_hot) / 2 + 22, "→ мала P", size=12, color=POS, anchor="start", bold=True))

    render(os.path.join(IMG, "why-slope.svg"), W, H, *frags,
           title="Чому допустима потужність падає: стеля переходу одна")


# ── 3. Запас на старіння: робоча точка нижче кривої ──────────────────────────
def fig_margin():
    W, H = 640, 380
    ox, oy = 80, 300
    pw, ph = 460, 230
    Tmin, Tmax = 0, 175
    rated_T, zero_T = 70, 155

    def X(T): return ox + (T - Tmin) / (Tmax - Tmin) * pw
    def Y(pct): return oy - pct / 100.0 * ph
    def curve(T):
        if T <= rated_T: return 100.0
        if T >= zero_T: return 0.0
        return (zero_T - T) / (zero_T - rated_T) * 100

    frags = []
    frags.append(rect(ox, oy - ph, pw, ph, fill="#fbfcfd", stroke="#dfe3e8", sw=1))
    for pct in (50, 100):
        frags.append(line(ox, Y(pct), ox + pw, Y(pct), color="#e6e9ee", sw=1))
        frags.append(text(ox - 10, Y(pct) + 5, "%d%%" % pct, size=12, color=MUTED, anchor="end"))
    frags.append(arrow(ox, oy, ox, oy - ph - 12, color=INK, sw=1.8))
    frags.append(arrow(ox, oy, ox + pw + 12, oy, color=INK, sw=1.8))
    frags.append(text(ox + pw / 2, oy + 40, "температура середовища, °C", size=13))

    for T in (25, 70, 125, 155):
        frags.append(line(X(T), oy, X(T), oy + 5, color=INK, sw=1.4))
        frags.append(text(X(T), oy + 22, str(T), size=12, color=MUTED))

    # паспортна крива (стеля)
    frags.append(line(X(Tmin), Y(100), X(rated_T), Y(100), color=POS, sw=2.5))
    frags.append(line(X(rated_T), Y(100), X(zero_T), Y(0), color=POS, sw=2.5))
    b, w, h = textbox(X(120), Y(curve(120)) + 22, "паспортна межа", size=12,
                      fill="#fdecea", stroke=POS, color=POS)
    frags.append(b)

    # робоча крива на 0.6 від паспортної (60 % derating)
    k = 0.6
    frags.append(line(X(Tmin), Y(100 * k), X(rated_T), Y(100 * k), color=FIELD, sw=2.5, dash="6,4"))
    frags.append(line(X(rated_T), Y(100 * k), X(zero_T), Y(0), color=FIELD, sw=2.5, dash="6,4"))
    b, w, h = textbox(X(40), Y(100 * k) - 22, "робоча межа (із запасом)", size=12,
                      fill="#eafaf0", stroke=FIELD, color=FIELD)
    frags.append(b)

    # вертикальна стрілка-«запас» при 70 °C
    frags.append(arrow(X(70) + 22, Y(100), X(70) + 22, Y(60), color=INK, sw=1.6))
    frags.append(arrow(X(70) + 22, Y(60), X(70) + 22, Y(100), color=INK, sw=1.6))
    b, w, h = textbox(X(70) + 92, (Y(100) + Y(60)) / 2, "запас на\nстаріння й піки", size=12,
                      fill="#f4f6f8", stroke=LINE)
    frags.append(b)

    render(os.path.join(IMG, "margin.svg"), W, H, *frags,
           title="Працюй нижче кривої: запас на старіння й кидки")


if __name__ == "__main__":
    fig_curve()
    fig_why()
    fig_margin()
    print("OK figs written to", IMG)
