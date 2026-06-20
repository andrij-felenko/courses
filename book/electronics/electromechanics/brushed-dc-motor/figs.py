# -*- coding: utf-8 -*-
"""Фігури до теми «Колекторний DC-мотор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Комутатор і щітки: перемикання струму у рамці ─────────────────────────
def fig_commutator():
    W, H = 720, 410
    f = [text(W / 2, 28, "Комутатор зі щітками перемикає струм у рамці двічі за оберт",
              size=16, bold=True)]

    def stage(x0, title, ang_deg, swap):
        cx, cy = x0 + 130, 200
        # магніти статора
        f.append(rect(cx - 120, cy - 70, 26, 140, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
        f.append(text(cx - 107, cy, "N", size=18, bold=True, color=POS))
        f.append(rect(cx + 94, cy - 70, 26, 140, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
        f.append(text(cx + 107, cy, "S", size=18, bold=True, color=NEG))
        # рамка (ротор) — нахилена
        import math
        a = math.radians(ang_deg)
        dx, dy = math.cos(a) * 70, math.sin(a) * 70
        px, py = -dy * 0.34, dx * 0.34      # півширина рамки впоперек
        ax1, ay1 = cx - dx, cy - dy
        ax2, ay2 = cx + dx, cy + dy
        # дві сторони рамки
        f.append(line(ax1 - px, ay1 - py, ax1 + px, ay1 + py, color=INK, sw=3))
        f.append(line(ax2 - px, ay2 - py, ax2 + px, ay2 + py, color=INK, sw=3))
        f.append(line(ax1, ay1, ax2, ay2, color=MUTED, sw=1.6, dash="3,3"))
        # позначка напряму струму у двох сторонах (× — від нас, • — до нас)
        s1, s2 = ("⊗", "⊙") if not swap else ("⊙", "⊗")
        f.append(text(ax1, ay1 + 5, s1, size=17, bold=True, color=FIELD))
        f.append(text(ax2, ay2 + 5, s2, size=17, bold=True, color=FIELD))
        # стрілка моменту (однакова в обох → той самий бік обертання)
        f.append(arrow(cx + 30, cy + 92, cx - 30, cy + 92, color=FIELD, sw=2.4))
        f.append(text(cx, cy + 116, "момент → той самий бік", size=11, color=FIELD))
        # колектор: дві півкільця + щітки
        ky = cy + 150
        f.append(rect(cx - 26, ky, 22, 20, fill="#f3d9b5", stroke=MUTED, sw=1.3, rx=3))
        f.append(rect(cx + 4, ky, 22, 20, fill="#f3d9b5", stroke=MUTED, sw=1.3, rx=3))
        f.append(text(cx - 56, ky + 14, "+", size=15, bold=True, color=POS))
        f.append(text(cx + 50, ky + 14, "−", size=15, bold=True, color=NEG))
        f.append(line(cx - 50, ky + 10, cx - 26, ky + 10, color=POS, sw=2.2))
        f.append(line(cx + 26, ky + 10, cx + 48, ky + 10, color=NEG, sw=2.2))
        f.append(text(cx, ky - 8, "колектор + щітки", size=10.5, color=MUTED))
        f.append(text(cx, 60, title, size=13, bold=True, color=INK))

    stage(20, "Рамка горизонтальна", 8, swap=False)
    f.append(line(W / 2, 70, W / 2, 360, color="#d6dde6", sw=1.2, dash="4,5"))
    stage(380, "Пів-оберта по тому: щітки\nперескочили на інші пластини", 8, swap=True)
    render(os.path.join(IMG, "commutator.svg"), W, H, *f)


# ── 2. Момент ∝ струм, оберти ∝ напруга; рівновага (V−E)/R ───────────────────
def fig_torque_speed():
    W, H = 720, 360
    f = [text(W / 2, 28, "Дві прості пропорції мотора і звідки вони беруться",
              size=16, bold=True)]

    # ліва панель — ланцюг із джерелом, R обмотки, проти-ЕРС
    lx = 60
    f.append(rect(lx, 80, 300, 200, fill="#fbfdff", stroke="#d6dde6", sw=1.4, rx=8))
    f.append(text(lx + 150, 104, "обмотка під напругою", size=12.5, bold=True))
    # батарея
    f.append(text(lx + 28, 150, "V", size=15, bold=True, color=INK))
    f.append(line(lx + 24, 158, lx + 24, 210, color=INK, sw=2))
    f.append(line(lx + 40, 168, lx + 40, 200, color=INK, sw=4))     # довга пластина (+)
    f.append(line(lx + 24, 184, lx + 40, 184, color=INK, sw=1.6))
    # резистор обмотки
    f.append(rect(lx + 110, 132, 90, 26, fill=FILL, stroke=LINE, sw=1.4))
    f.append(text(lx + 155, 150, "R обмотки", size=11, color=INK))
    # джерело проти-ЕРС (мотор)
    f.append(circle(lx + 250, 190, 30, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(mtext(lx + 250, 186, ["проти-", "ЕРС E"], size=11, color=FIELD, lh=1.15, bold=True))
    # дроти
    f.append(line(lx + 24, 158, lx + 24, 132, color=INK, sw=1.6))
    f.append(line(lx + 24, 132, lx + 110, 132, color=INK, sw=1.6))
    f.append(line(lx + 200, 132, lx + 250, 132, color=INK, sw=1.6))
    f.append(line(lx + 250, 132, lx + 250, 160, color=INK, sw=1.6))
    f.append(line(lx + 250, 220, lx + 250, 250, color=INK, sw=1.6))
    f.append(line(lx + 250, 250, lx + 24, 250, color=INK, sw=1.6))
    f.append(line(lx + 24, 250, lx + 24, 210, color=INK, sw=1.6))
    b, _, _ = textbox(lx + 150, 262, "струм I = (V − E) / R", size=12.5,
                      fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)

    # права панель — дві пропорції
    rx = 410
    b1, _, _ = textbox(rx + 145, 120,
                       "момент  ∝  струм\nM = kT · I", size=14,
                       fill="#fdecea", stroke=POS, bold=True, min_w=270)
    f.append(b1)
    f.append(text(rx + 145, 168, "сила на провід у полі → крутить", size=11, color=MUTED))
    b2, _, _ = textbox(rx + 145, 222,
                       "оберти  ∝  напруга\nω ≈ V / kE", size=14,
                       fill="#eaf0fd", stroke=NEG, bold=True, min_w=270)
    f.append(b2)
    f.append(text(rx + 145, 270, "розганяється, поки E не зрівняє V", size=11, color=MUTED))
    render(os.path.join(IMG, "torque-speed.svg"), W, H, *f)


# ── 3. Проти-ЕРС: струм спадає з обертами; пуск і стопор ─────────────────────
def fig_backemf():
    W, H = 720, 400
    f = [text(W / 2, 28, "Чому струм падає з обертами: проти-ЕРС віднімається від напруги",
              size=16, bold=True)]
    ox, oy = 90, 320
    ax_w, ax_h = 540, 232
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "оберти ротора  ω  (частка від холостих)",
                  size=12, color=INK))
    f.append(mtext(ox - 64, oy - ax_h / 2 - 6, ["струм", "(частка", "від пуск.)"],
                   size=11, color=INK, lh=1.15))

    # позначки осі X
    for frac, lab in [(0.0, "0\n(стопор)"), (0.5, "½"), (1.0, "1\n(холості)")]:
        x = ox + frac * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(mtext(x, oy + 20, lab, size=10.5, color=MUTED, lh=1.1))
    for pv, lab in [(0, "0"), (50, "½"), (100, "1")]:
        y = oy - pv / 100.0 * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 22, y + 4, lab, size=11, color=MUTED))

    # пряма I = (V−E)/R: від 1 (стопор, E=0) до 0 (холості, E≈V)
    x0, y0 = ox, oy - ax_h
    x1, y1 = ox + ax_w, oy
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.8"/>'
             % (x0, y0, x1, y1, POS))

    # три точки: пуск/стопор, робоча, холості
    def dot(frac, ipct, lab, col, dyl=-14):
        x = ox + frac * ax_w
        y = oy - ipct / 100.0 * ax_h
        f.append(circle(x, y, 5, fill=BG, stroke=col, sw=2.4))
        return x, y
    dx, dy = dot(0.0, 100, "", POS)
    b, _, _ = textbox(dx + 96, dy + 6, "пуск/стопор: E=0,\nструм максимальний", size=11,
                      fill="#fdecea", stroke=POS)
    f.append(b)
    dx, dy = dot(0.62, 38, "", "#e08a3c")
    b, _, _ = textbox(dx + 6, dy - 34, "робоча точка:\nструм під навантаження", size=11,
                      fill=FILL, stroke="#e08a3c")
    f.append(b)
    dx, dy = dot(1.0, 0, "", NEG)
    b, _, _ = textbox(dx - 92, dy - 24, "холості: E≈V,\nструм ≈ 0", size=11,
                      fill="#eaf0fd", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "backemf.svg"), W, H, *f)


# ── 4. ШІМ: середня напруга = шпаруватість × живлення ────────────────────────
def fig_pwm():
    W, H = 720, 380
    f = [text(W / 2, 28, "ШІМ не міняє напругу — міняє частку часу «ввімкнено»",
              size=16, bold=True)]

    def track(y0, duty, label, col):
        x0, w = 80, 470
        hi, lo = y0, y0 + 70
        f.append(text(x0 - 14, y0 - 12, label, size=12, bold=True, color=INK, anchor="start"))
        # рівень V і 0
        f.append(line(x0 - 6, hi, x0 + w, hi, color="#d6dde6", sw=1, dash="3,4"))
        f.append(line(x0 - 6, lo, x0 + w, lo, color="#d6dde6", sw=1, dash="3,4"))
        f.append(text(x0 - 16, hi + 4, "V", size=10, color=MUTED, anchor="end"))
        f.append(text(x0 - 16, lo + 4, "0", size=10, color=MUTED, anchor="end"))
        # імпульси
        period = w / 4.0
        pts = []
        x = x0
        for _ in range(4):
            on = period * duty
            pts += [(x, lo), (x, hi), (x + on, hi), (x + on, lo), (x + period, lo)]
            x += period
        d = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))
        # лінія середньої напруги
        ym = lo - (lo - hi) * duty
        f.append(line(x0, ym, x0 + w, ym, color=POS, sw=2, dash="7,5"))
        f.append(text(x0 + w + 8, ym + 4, "сер.", size=10.5, color=POS, anchor="start"))
        f.append(text(x0 + w + 8, y0 + 30, "%d%%" % int(duty * 100), size=13, bold=True,
                      color=col, anchor="start"))

    track(80, 0.25, "газ 25%", NEG)
    track(210, 0.70, "газ 70%", FIELD)
    f.append(text(W / 2, 330,
                  "пунктир — середня напруга на моторі; вона й задає оберти",
                  size=12, color=INK, italic=True))
    f.append(text(W / 2, 356,
                  "ключ устигає тисячі перемикань на секунду — мотор «бачить» лише середнє",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "pwm.svg"), W, H, *f)


# ── 5. Чому щітки зношуються: тертя + іскра на розриві ───────────────────────
def fig_brush_wear():
    W, H = 720, 360
    f = [text(W / 2, 28, "Дві причини зносу щіток: постійне тертя і іскра на розриві",
              size=16, bold=True)]

    # колектор — коло з пластин і проміжками
    cx, cy, r = 210, 195, 92
    import math
    n = 8
    for i in range(n):
        a0 = math.radians(i * 360.0 / n - 90 + 4)
        a1 = math.radians((i + 1) * 360.0 / n - 90 - 4)
        x0p, y0p = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1p, y1p = cx + r * math.cos(a1), cy + r * math.sin(a1)
        f.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="9"/>'
                 % (x0p, y0p, r, r, x1p, y1p, "#cf9b66"))
    f.append(circle(cx, cy, r - 16, fill="#fbfdff", stroke="#d6dde6", sw=1.4))
    f.append(circle(cx, cy, 6, fill=MUTED, stroke=LINE, sw=1.2))
    f.append(text(cx, cy + 4, "вал", size=10, color=BG, anchor="middle"))
    # стрілка обертання
    f.append('<path d="M%.1f %.1f A40 40 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>' % (cx + 40, cy - 24, cx + 24, cy - 40, MUTED))
    # щітка зверху, що притискається
    f.append(rect(cx - 16, cy - r - 46, 32, 40, fill="#5b5b5b", stroke=INK, sw=1.4, rx=3))
    f.append(text(cx, cy - r - 52, "щітка (графіт)", size=10.5, color=INK))
    f.append(arrow(cx, cy - r - 60, cx, cy - r - 8, color=NEG, sw=2))
    f.append(text(cx + 70, cy - r - 36, "пружина тисне", size=10, color=NEG, anchor="start"))
    # іскра на проміжку
    sx, sy = cx + r * math.cos(math.radians(-90 + 24)), cy + r * math.sin(math.radians(-90 + 24))
    f.append(text(sx + 6, sy + 4, "⚡", size=18, color=POS, anchor="start"))
    f.append(text(sx + 24, sy + 4, "іскра на розриві", size=10.5, color=POS, anchor="start"))

    # права колонка — механізм зносу
    bx = 420
    b1, _, _ = textbox(bx + 145, 96,
                       "Тертя\nграфіт треться об мідь\n→ щітка стирається", size=12,
                       fill=FILL, stroke=MUTED, min_w=260)
    f.append(b1)
    b2, _, _ = textbox(bx + 145, 188,
                       "Іскра (комутація)\nрозрив струму в котушці\n→ дуга палить контакт", size=12,
                       fill="#fdecea", stroke=POS, min_w=260)
    f.append(b2)
    b3, _, _ = textbox(bx + 145, 280,
                       "Наслідок: щітки — видаткова\nдеталь, обмежують ресурс і оберти", size=11.5,
                       fill="#eef2f8", stroke=NEG, min_w=260)
    f.append(b3)
    render(os.path.join(IMG, "brush-wear.svg"), W, H, *f)


if __name__ == "__main__":
    fig_commutator()
    fig_torque_speed()
    fig_backemf()
    fig_pwm()
    fig_brush_wear()
    print("OK: 5 figures ->", IMG)
