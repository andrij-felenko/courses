# -*- coding: utf-8 -*-
"""Фігури до теми «Монітор струму».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Тракт вимірювання: шунт → підсилювач → АЦП → число ────────────────────
def fig_chain():
    W, H = 760, 330
    f = [text(W / 2, 28, "Струм → спад на шунті → підсилення → число", size=16, bold=True)]

    # силова лінія: джерело → шунт → навантаження
    yb = 110
    f.append(text(70, yb - 26, "джерело", size=12, color=MUTED))
    f.append(rect(40, yb - 14, 60, 30, fill="#eef3f9", stroke=LINE, sw=1.5))
    f.append(text(70, yb + 6, "+V", size=13, bold=True, color=POS))
    # товстий силовий провід
    f.append(line(100, yb, 250, yb, color=POS, sw=4))
    # шунт
    f.append(rect(250, yb - 16, 70, 32, fill="#fff3e0", stroke="#b8860b", sw=2))
    f.append(text(285, yb + 5, "R_ш", size=13, bold=True, color=INK))
    f.append(text(285, yb - 26, "1 мΩ", size=11, color=MUTED))
    f.append(line(320, yb, 470, yb, color=POS, sw=4))
    # навантаження
    f.append(rect(470, yb - 20, 80, 40, fill="#eef3f9", stroke=LINE, sw=1.5))
    f.append(text(510, yb - 1, "наванта-", size=11))
    f.append(text(510, yb + 13, "ження", size=11))
    f.append(line(550, yb, 620, yb, color=POS, sw=4))
    f.append(text(635, yb + 5, "I", size=15, bold=True, color=POS, italic=True))
    f.append(arrow(150, yb - 30, 210, yb - 30, color=POS))
    f.append(text(180, yb - 38, "струм I", size=11, color=POS))

    # сенсорні відводи з тіла шунта вниз до підсилювача
    f.append(line(258, yb + 16, 258, 190, color=NEG, sw=1.6))
    f.append(line(312, yb + 16, 312, 190, color=NEG, sw=1.6))
    f.append(text(225, 178, "спад V = I·R", size=11, color=NEG))

    # підсилювач (трикутник)
    ax, ay = 285, 215
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#eef6ef" stroke="%s" stroke-width="1.8"/>'
             % (ax - 45, ay - 28, ax - 45, ay + 28, ax + 50, ay, FIELD))
    f.append(text(ax - 12, ay + 5, "×G", size=15, bold=True, color=INK))
    f.append(text(ax - 5, ay + 40, "підсилювач струму (CSA)", size=11, color=MUTED))

    # до АЦП
    f.append(arrow(335, ay, 420, ay, color=LINE))
    b, w, h = textbox(470, ay, "АЦП", size=14, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    f.append(arrow(508, ay, 580, ay, color=LINE))
    b2, w2, h2 = textbox(645, ay, "I = код\n у МК", size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b2)

    render(os.path.join(IMG, "sense-chain.svg"), W, H, *f)


# ── 2. Верхня vs нижня сторона ───────────────────────────────────────────────
def fig_high_low():
    W, H = 760, 360
    f = [text(W / 2, 26, "Де ставити шунт: висока сторона vs низька сторона", size=16, bold=True)]

    def rail(x0, title, hi):
        # рамка панелі
        f.append(rect(x0, 50, 330, 280, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
        f.append(text(x0 + 165, 74, title, size=14, bold=True))
        topy, boty = 110, 250
        cx_src, cx_load = x0 + 70, x0 + 235
        # шина живлення (зверху) і земля (знизу)
        f.append(line(x0 + 30, topy, x0 + 300, topy, color=POS, sw=3))
        f.append(text(x0 + 30, topy - 10, "+V живлення", size=11, color=POS, anchor="start"))
        f.append(line(x0 + 30, boty, x0 + 300, boty, color=NEG, sw=3))
        f.append(text(x0 + 30, boty + 22, "земля (GND)", size=11, color=NEG, anchor="start"))
        # навантаження — вертикальний прямокутник посередині
        f.append(rect(cx_load - 26, topy + 18, 52, boty - topy - 36, fill="#eef3f9", stroke=LINE, sw=1.5))
        f.append(text(cx_load, (topy + boty) / 2 + 4, "наван-", size=10))
        f.append(text(cx_load, (topy + boty) / 2 + 16, "таження", size=10))
        if hi:
            # шунт у плюсовому проводі (зверху)
            f.append(line(cx_load, topy, cx_load, topy + 18, color=POS, sw=3))
            f.append(rect(cx_src - 18, topy - 13, 36, 26, fill="#fff3e0", stroke="#b8860b", sw=2))
            f.append(text(cx_src, topy + 5, "R_ш", size=12, bold=True))
            f.append(line(x0 + 30, topy, cx_src - 18, topy, color=POS, sw=3))
            f.append(line(cx_src + 18, topy, cx_load, topy, color=POS, sw=3))
            f.append(line(cx_load, boty, cx_load, boty - 18, color=NEG, sw=3))
            note = "шунт «висить» на +V:\nвхід підсилювача бачить\nсинфазно майже все живлення"
            ncol = POS
        else:
            # шунт у землі (знизу)
            f.append(line(cx_load, topy, cx_load, topy + 18, color=POS, sw=3))
            f.append(line(cx_load, boty, cx_load, boty - 18, color=NEG, sw=3))
            f.append(rect(cx_src - 18, boty - 13, 36, 26, fill="#fff3e0", stroke="#b8860b", sw=2))
            f.append(text(cx_src, boty + 5, "R_ш", size=12, bold=True))
            f.append(line(x0 + 30, boty, cx_src - 18, boty, color=NEG, sw=3))
            f.append(line(cx_src + 18, boty, cx_load, boty, color=NEG, sw=3))
            note = "шунт біля землі:\nсигнал близько до 0 В —\nале «земля» вже не нуль"
            ncol = NEG
        f.append(text(x0 + 165, 300, note.split("\n")[0], size=10.5, color=ncol))
        f.append(text(x0 + 165, 314, note.split("\n")[1], size=10.5, color=ncol))
        f.append(text(x0 + 165, 328, note.split("\n")[2], size=10.5, color=ncol))

    rail(30, "Висока сторона (high-side)", True)
    rail(400, "Низька сторона (low-side)", False)
    render(os.path.join(IMG, "high-low-side.svg"), W, H, *f)


# ── 3. Вибір опору шунта: сигнал ↑ vs втрати ↑ ──────────────────────────────
def fig_tradeoff():
    W, H = 720, 400
    f = [text(W / 2, 28, "Вибір R_ш: більший опір → кращий сигнал, але більші втрати", size=15, bold=True)]
    # осі
    ox, oy = 90, 320
    aw, ah = 560, 240
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))   # X
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))   # Y
    f.append(text(ox + aw / 2, oy + 42, "опір шунта R_ш  →", size=12, color=MUTED))
    f.append(text(ox - 60, oy - ah / 2, "величина", size=12, color=MUTED, anchor="middle"))

    import math
    # сигнал V = I·R — лінійно росте (добре)
    pts_v = []
    for i in range(0, 101):
        rx = i / 100.0
        px = ox + rx * aw
        py = oy - rx * (ah - 30)
        pts_v.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts_v), FIELD))
    f.append(text(ox + aw - 4, oy - (ah - 30) - 8, "сигнал V = I·R  (легше міряти)", size=11.5, color=FIELD, anchor="end"))

    # втрати: на робочому струмі тримаємо V у межах входу, тож зі зростанням R
    # струм, який ще «вкладається», падає — а даремне тепло на шунті росте крутіше:
    # штрафна крива свідомо опукла вгору, щоб показати, що втрати «виграють гонку».
    pts_p = []
    for i in range(0, 101):
        rx = i / 100.0
        px = ox + rx * aw
        py = oy - (rx ** 0.62) * (ah - 6)
        pts_p.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,5"/>'
             % (" ".join(pts_p), POS))
    f.append(text(ox + aw - 4, oy - (ah - 6) + 18, "втрати/тепло P = I²R  (штраф)", size=11.5, color=POS, anchor="end"))

    # робоча зона — компроміс посередині-ліворуч
    zx = ox + 0.30 * aw
    f.append(line(zx, oy, zx, oy - ah + 8, color=MUTED, sw=1.2, dash="3,4"))
    b, w, h = textbox(zx, oy - ah + 28, "робоча зона:\nдосить сигналу,\nприйнятні втрати",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "shunt-tradeoff.svg"), W, H, *f)


# ── 4. Звідки беруться похибки монітора струму ───────────────────────────────
def fig_errors():
    W, H = 720, 380
    f = [text(W / 2, 28, "Що псує показ струму: ланцюг похибок", size=16, bold=True)]
    items = [
        ("Опір шунта R_ш", "допуск ±1% і дрейф із t° (TCR):\nрахуємо I = V/R, а R «попливе»", "#fff3e0", "#b8860b"),
        ("Зміщення нуля (offset)", "підсилювач додає кілька мкВ навіть\nпри I = 0 — фатально на малому струмі", "#eaf0fd", NEG),
        ("Підсилення G", "похибка коефіцієнта ×G\nмасштабує весь показ", "#eef6ef", FIELD),
        ("Синфазна напруга", "на high-side вхід «висить» на +V;\nскінченний CMRR протікає в сигнал", "#fdecea", POS),
        ("АЦП", "крок кванта, своє зміщення\nй нелінійність на хвості тракту", "#f0f0f3", MUTED),
    ]
    y = 70
    for name, desc, fill, stroke in items:
        f.append(rect(40, y, 250, 50, fill=fill, stroke=stroke, sw=1.6, rx=6))
        f.append(text(165, y + 22, name, size=13, bold=True))
        f.append(text(165, y + 40, "↓ додається до бюджету", size=10, color=MUTED))
        f.append(text(310, y + 20, desc.split("\n")[0], size=11.5, anchor="start"))
        f.append(text(310, y + 36, desc.split("\n")[1], size=11.5, anchor="start", color=MUTED))
        y += 62
    render(os.path.join(IMG, "error-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_high_low()
    fig_tradeoff()
    fig_errors()
    print("OK: figures written to", IMG)
