# -*- coding: utf-8 -*-
"""Фігури до теми «Перетворювач рівнів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дві проблеми стику доменів: 5→3.3 (перенапруга) і 3.3→5 (недотяг) ──────
def fig_two_problems():
    W, H = 720, 380
    f = [text(W / 2, 28, "Два домени живлення стикаються — і кожен напрямок ламається по-своєму",
              size=15, bold=True)]

    def chip(cx, cy, label, sub, fill, stroke):
        f.append(rect(cx - 70, cy - 34, 140, 68, fill=fill, stroke=stroke, sw=2, rx=8))
        f.append(text(cx, cy - 4, label, size=14, bold=True, color=INK))
        f.append(text(cx, cy + 17, sub, size=11, color=MUTED))

    # ── верхня половина: 5 В драйвер → 3.3 В вхід (НЕБЕЗПЕКА) ──
    f.append(text(W / 2, 64, "Зверху: вихід 5 В тисне в 3.3-вольтовий вхід", size=12, bold=True, color=POS))
    chip(150, 110, "5 В логіка", "VOH ≈ 5 В", "#fdecea", POS)
    chip(570, 110, "3.3 В логіка", "макс. вхід ≈ 3.6 В", "#fdecea", POS)
    f.append(arrow(222, 110, 498, 110, color=POS, sw=2.4))
    f.append(text(360, 96, "5 В на пін, розрахований на 3.3 В", size=11, color=POS))
    b, _, _ = textbox(360, 140, "перенапруга → струм у захисний діод → деградація", size=11,
                      fill="#fdecea", stroke=POS)
    f.append(b)

    f.append(line(40, 188, W - 40, 188, color="#d6dde6", sw=1.2, dash="5,5"))

    # ── нижня половина: 3.3 В драйвер → 5 В вхід (НЕДОТЯГ) ──
    f.append(text(W / 2, 220, "Знизу: вихід 3.3 В не дотягує до порога 5-вольтового входу",
                  size=12, bold=True, color=NEG))
    chip(150, 268, "3.3 В логіка", "VOH ≈ 3.3 В", "#eaf0fd", NEG)
    chip(570, 268, "5 В логіка", "VIH ≈ 3.5 В", "#eaf0fd", NEG)
    f.append(arrow(222, 268, 498, 268, color=NEG, sw=2.4))
    f.append(text(360, 254, "3.3 В приходить на вхід, що чекає ≥ 3.5 В", size=11, color=NEG))
    b2, _, _ = textbox(360, 298, "сигнал нижче VIH → «1» не впізнається або плаває", size=11,
                       fill="#eaf0fd", stroke=NEG)
    f.append(b2)

    f.append(text(W / 2, 350,
                  "Тому між доменами потрібен посередник — перетворювач рівнів",
                  size=12.5, italic=True, color=INK))
    render(os.path.join(IMG, "two-problems.svg"), W, H, *f)


# ── 2. Три механізми: дільник, буфер, MOSFET ────────────────────────────────
def fig_three_types():
    W, H = 740, 430
    f = [text(W / 2, 28, "Три способи узгодити рівні — різні за напрямком, швидкістю, ціною",
              size=15, bold=True)]

    cw, gap = 224, 18
    x0 = (W - (3 * cw + 2 * gap)) / 2
    top = 52

    # ── картка 1: резистивний дільник ──
    x = x0
    f.append(rect(x, top, cw, 340, fill="#eef2f8", stroke=NEG, sw=1.8, rx=10))
    f.append(text(x + cw / 2, top + 24, "Дільник напруги", size=13.5, bold=True, color=INK))
    f.append(text(x + cw / 2, top + 42, "(тільки вниз: 5 → 3.3)", size=10.5, color=MUTED))
    # схемка дільника
    sx = x + cw / 2
    f.append(line(sx, top + 60, sx, top + 96, color=LINE, sw=2))           # вхід 5В
    f.append(text(sx - 30, top + 74, "5 В", size=10, color=POS, anchor="end"))
    f.append(rect(sx - 12, top + 96, 24, 34, fill=BG, stroke=LINE, sw=1.6))  # R1
    f.append(text(sx + 22, top + 116, "R1", size=10, color=MUTED, anchor="start"))
    f.append(line(sx, top + 130, sx, top + 150, color=LINE, sw=2))
    f.append(circle(sx, top + 150, 3, fill=INK, stroke=INK))               # відвід
    f.append(line(sx, top + 150, sx + 56, top + 150, color=LINE, sw=2))
    f.append(text(sx + 60, top + 146, "3.3 В", size=10, color=NEG, anchor="start"))
    f.append(rect(sx - 12, top + 150, 24, 34, fill=BG, stroke=LINE, sw=1.6))  # R2
    f.append(text(sx + 22, top + 170, "R2", size=10, color=MUTED, anchor="start"))
    f.append(line(sx, top + 184, sx, top + 204, color=LINE, sw=2))
    f.append(line(sx - 14, top + 204, sx + 14, top + 204, color=LINE, sw=2.4))  # земля
    f.append(line(sx - 9, top + 209, sx + 9, top + 209, color=LINE, sw=2))
    f.append(line(sx - 4, top + 214, sx + 4, top + 214, color=LINE, sw=1.6))
    b, _, _ = textbox(x + cw / 2, top + 252,
                      "+ копійки, два резистори\n− односторонній\n− повільний (RC)",
                      size=11, fill=BG, stroke=NEG)
    f.append(b)
    f.append(text(x + cw / 2, top + 322, "тільки повільні лінії", size=10.5, color=MUTED, italic=True))

    # ── картка 2: буфер / зсувач-мікросхема ──
    x = x0 + cw + gap
    f.append(rect(x, top, cw, 340, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(x + cw / 2, top + 24, "Буфер (мікросхема)", size=13.5, bold=True, color=INK))
    f.append(text(x + cw / 2, top + 42, "(швидкий, push-pull)", size=10.5, color=MUTED))
    # трикутник-буфер з двома живленнями
    bx, by = x + cw / 2, top + 130
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (bx - 34, by - 34, bx - 34, by + 34, bx + 40, by, BG, FIELD))
    f.append(line(bx - 70, by, bx - 34, by, color=LINE, sw=2))
    f.append(line(bx + 40, by, bx + 74, by, color=LINE, sw=2))
    f.append(text(bx - 74, by + 4, "3.3", size=10, color=NEG, anchor="end"))
    f.append(text(bx + 78, by + 4, "5", size=10, color=POS, anchor="start"))
    f.append(line(bx - 6, by - 24, bx - 6, by - 44, color=POS, sw=1.6))     # VccB
    f.append(text(bx - 6, by - 50, "5 В", size=9, color=POS))
    f.append(line(bx - 6, by + 24, bx - 6, by + 44, color=LINE, sw=1.6))    # GND
    f.append(text(bx - 6, by + 58, "GND", size=9, color=MUTED))
    b2, _, _ = textbox(x + cw / 2, top + 252,
                       "+ швидкий, чистий фронт\n+ два домени живлення\n− напрямок фіксований",
                       size=11, fill=BG, stroke=FIELD)
    f.append(b2)
    f.append(text(x + cw / 2, top + 322, "шини з відомим напрямком", size=10.5, color=MUTED, italic=True))

    # ── картка 3: MOSFET двонапрямний ──
    x = x0 + 2 * (cw + gap)
    f.append(rect(x, top, cw, 340, fill="#fbeee6", stroke=POS, sw=1.8, rx=10))
    f.append(text(x + cw / 2, top + 24, "MOSFET-ключ", size=13.5, bold=True, color=INK))
    f.append(text(x + cw / 2, top + 42, "(двонапрямний)", size=10.5, color=MUTED))
    # n-MOSFET зі стрілками в обидва боки + дві підтяжки
    mx, my = x + cw / 2, top + 120
    f.append(line(mx, top + 60, mx, top + 96, color=LINE, sw=2))            # затвор-живлення згори
    f.append(text(mx, top + 74, "затвор → 3.3 В", size=9.5, color=MUTED))
    f.append(rect(mx - 18, top + 96, 36, 48, fill=BG, stroke=LINE, sw=1.6, rx=4))
    f.append(text(mx, top + 124, "MOS", size=10, bold=True, color=INK))
    f.append(line(mx - 60, top + 120, mx - 18, top + 120, color=NEG, sw=2))
    f.append(line(mx + 18, top + 120, mx + 60, top + 120, color=POS, sw=2))
    f.append(text(mx - 64, top + 116, "3.3", size=10, color=NEG, anchor="end"))
    f.append(text(mx + 64, top + 116, "5", size=10, color=POS, anchor="start"))
    # двостороння стрілка
    f.append(arrow(mx - 40, top + 150, mx + 40, top + 150, color=INK, sw=1.8))
    f.append(arrow(mx + 40, top + 158, mx - 40, top + 158, color=INK, sw=1.8))
    # підтяжки
    f.append(text(mx, top + 180, "+ підтяжка з кожного боку", size=9.5, color=MUTED))
    b3, _, _ = textbox(x + cw / 2, top + 252,
                       "+ обидва напрямки\n+ дешевий (1 транзистор/лінію)\n− лише open-drain шини",
                       size=11, fill=BG, stroke=POS)
    f.append(b3)
    f.append(text(x + cw / 2, top + 322, "I2C та інші open-drain", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "three-types.svg"), W, H, *f)


# ── 3. Двонапрямний MOSFET: чому він пускає сигнал в обидва боки ─────────────
def fig_mosfet_bidir():
    W, H = 740, 430
    f = [text(W / 2, 26, "Двонапрямний MOSFET-ключ: один транзистор тримає обидва напрямки",
              size=15, bold=True)]

    # спільна схема зверху
    lo, hi = 150, 590                  # центри низької/високої сторін
    railY = 96
    gateY = 70
    swY = 150
    # затвор на нижче живлення
    f.append(rect(W / 2 - 24, gateY, 48, 26, fill=BG, stroke=LINE, sw=1.6, rx=4))
    f.append(text(W / 2, gateY + 17, "G", size=12, bold=True, color=INK))
    f.append(line(W / 2, gateY, W / 2, gateY - 16, color=LINE, sw=1.8))
    f.append(text(W / 2, gateY - 22, "затвор → VccA (3.3 В)", size=10.5, color=MUTED))
    f.append(line(W / 2, gateY + 26, W / 2, swY - 12, color=LINE, sw=1.8))
    f.append(rect(W / 2 - 30, swY - 12, 60, 40, fill="#f0f0f0", stroke=LINE, sw=1.6, rx=4))
    f.append(text(W / 2, swY + 13, "MOSFET", size=11, bold=True, color=INK))

    # ліва сторона (A, 3.3В), права (B, 5В)
    f.append(line(lo, swY + 8, W / 2 - 30, swY + 8, color=NEG, sw=2.4))
    f.append(line(W / 2 + 30, swY + 8, hi, swY + 8, color=POS, sw=2.4))
    f.append(text(lo, swY + 36, "сторона A", size=11, bold=True, color=NEG))
    f.append(text(lo, swY + 52, "3.3 В домен", size=10, color=MUTED))
    f.append(text(hi, swY + 36, "сторона B", size=11, bold=True, color=POS))
    f.append(text(hi, swY + 52, "5 В домен", size=10, color=MUTED))
    # підтяжки
    f.append(line(lo, swY + 8, lo, railY, color=NEG, sw=1.6))
    f.append(rect(lo - 11, railY - 30, 22, 30, fill=BG, stroke=NEG, sw=1.4))
    f.append(text(lo - 26, railY - 14, "Rp", size=9.5, color=MUTED, anchor="end"))
    f.append(line(lo, railY - 30, lo, railY - 46, color=NEG, sw=1.6))
    f.append(text(lo, railY - 52, "3.3 В", size=10, color=NEG))
    f.append(line(hi, swY + 8, hi, railY, color=POS, sw=1.6))
    f.append(rect(hi - 11, railY - 30, 22, 30, fill=BG, stroke=POS, sw=1.4))
    f.append(text(hi + 26, railY - 14, "Rp", size=9.5, color=MUTED, anchor="start"))
    f.append(line(hi, railY - 30, hi, railY - 46, color=POS, sw=1.6))
    f.append(text(hi, railY - 52, "5 В", size=10, color=POS))

    # роздільник
    f.append(line(40, 240, W - 40, 240, color="#d6dde6", sw=1.2, dash="5,5"))

    # два сценарії знизу
    cw = 320
    lx = 60
    rx = W - 60 - cw

    # лівий: A тягне вниз → MOSFET відмикається → B теж униз
    f.append(rect(lx, 256, cw, 150, fill="#eef2f8", stroke=NEG, sw=1.6, rx=8))
    f.append(text(lx + cw / 2, 278, "A тягне «0» → проходить на B", size=12, bold=True, color=NEG))
    f.append(mtext(lx + 16, 304,
                   ["сторона A сідає до 0 В,", "виток MOSFET падає нижче затвора,",
                    "канал відкривається й тягне B теж до 0 В,", "обидві сторони бачать «0»"],
                   size=10.8, color=INK, anchor="start", lh=1.35))

    # правий: B тягне вниз → через body-діод/канал A теж униз
    f.append(rect(rx, 256, cw, 150, fill="#fbeee6", stroke=POS, sw=1.6, rx=8))
    f.append(text(rx + cw / 2, 278, "B тягне «0» → проходить на A", size=12, bold=True, color=POS))
    f.append(mtext(rx + 16, 304,
                   ["сторона B сідає до 0 В,", "спершу провідний body-діод тягне A вниз,",
                    "виток просідає — канал домикає решту,", "обидві сторони бачать «0»"],
                   size=10.8, color=INK, anchor="start", lh=1.35))

    render(os.path.join(IMG, "mosfet-bidir.svg"), W, H, *f)


# ── 4. Швидкість і підтяжка: компроміс RC на open-drain лінії ────────────────
def fig_speed_pullup():
    W, H = 720, 400
    f = [text(W / 2, 28, "Підтяжка вирішує швидкість: сильна — гострий фронт, слабка — млявий",
              size=15, bold=True)]

    ox, oy = 90, 300
    ax_w, ax_h = 540, 220
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))               # X (час)
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))               # Y (напруга)
    f.append(text(ox + ax_w / 2, oy + 40, "час після відпускання лінії", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h / 2, "напруга", size=12, color=INK, anchor="middle"))

    # рівень живлення і поріг VIH
    vdd = oy - ax_h
    vih = oy - ax_h * 0.65
    f.append(line(ox, vdd, ox + ax_w, vdd, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox + ax_w + 4, vdd + 4, "Vcc", size=10, color=MUTED, anchor="start"))
    f.append(line(ox, vih, ox + ax_w, vih, color=FIELD, sw=1.4, dash="6,4"))
    f.append(text(ox + ax_w + 4, vih + 4, "VIH", size=10, color=FIELD, anchor="start"))

    import math

    def rc_curve(tau_frac, color, sw=2.6):
        # експонента 1 - e^{-t/τ}; tau_frac масштабує сталу часу
        pts = []
        for i in range(0, 201):
            t = i / 200.0
            y = 1 - math.exp(-t / tau_frac)
            pts.append("%.1f,%.1f" % (ox + t * ax_w, oy - y * ax_h))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (" ".join(pts), color, sw))

    # сильна підтяжка (мала RC) — швидко перетинає VIH
    rc_curve(0.10, NEG)
    # слабка підтяжка (велика RC) — ледь встигає
    rc_curve(0.42, POS)

    # позначки перетину VIH
    # для сильної: 1-e^{-t/0.1}=0.65 → t≈0.105
    tx1 = ox + 0.105 * ax_w
    f.append(line(tx1, vih, tx1, oy, color=NEG, sw=1.2, dash="3,3"))
    f.append(circle(tx1, vih, 4, fill=NEG, stroke=BG, sw=1.4))
    # для слабкої: 1-e^{-t/0.42}=0.65 → t≈0.44
    tx2 = ox + 0.44 * ax_w
    f.append(line(tx2, vih, tx2, oy, color=POS, sw=1.2, dash="3,3"))
    f.append(circle(tx2, vih, 4, fill=POS, stroke=BG, sw=1.4))

    f.append(text(tx1, oy + 18, "швидко", size=10.5, color=NEG, bold=True))
    f.append(text(tx2, oy + 18, "пізно", size=10.5, color=POS, bold=True))

    f.append(text(ox + ax_w * 0.30, oy - ax_h * 0.88, "сильна підтяжка (мале R·C)",
                  size=11.5, color=NEG, bold=True, anchor="start"))
    f.append(text(ox + ax_w * 0.50, oy - ax_h * 0.30, "слабка підтяжка (велике R·C)",
                  size=11.5, color=POS, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, oy + 70,
                      "сильніша підтяжка = гостріший фронт = вища швидкість, але більший струм",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "speed-pullup.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_problems()
    fig_three_types()
    fig_mosfet_bidir()
    fig_speed_pullup()
    print("OK: 4 figures ->", IMG)
