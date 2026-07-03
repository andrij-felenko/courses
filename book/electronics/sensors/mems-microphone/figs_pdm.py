# -*- coding: utf-8 -*-
"""figs_pdm.py — фігури до вставки «proj: PDM → PCM (децимація)».
Окремий файл, щоб не чіпати основний figs.py теми. Вивід у ./img/.
svgkit імпортуємо зі scripts/ (НЕ копіюємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── pdm-pipeline: увесь тракт 1 біт @ швидко → інтегратор → ÷R → гребінка → PCM ─
# Показуємо суть CIC: інтегратор біжить на високій частоті, проріджування
# посередині, гребінка — на низькій; на виході багатобітні відліки.
def fig_pipeline():
    W, H = 900, 380
    parts = []

    y = 150
    bw, bh = 150, 78

    # 1) PDM-потік 1 біт @ 3.072 МГц (щільність одиниць)
    sx = 40
    parts.append(rect(sx, y - bh / 2, 128, bh, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    parts.append(mtext(sx + 64, y - 10, "PDM\n1 біт", size=13, bold=True, color=INK))
    parts.append(text(sx + 64, y + 22, "3.072 МГц", size=11, color=MUTED))
    # маленький бітовий потік згори
    bits = "1 1 0 1 1 1 0 1"
    parts.append(text(sx + 64, y - bh / 2 - 10, bits, size=11, color=FIELD, bold=True))

    # стрілка → інтегратор
    x1 = sx + 128
    parts.append(arrow(x1 + 4, y, x1 + 40, y, color=INK, sw=1.9))

    # 2) інтегратор (біжить швидко)
    ix = x1 + 46
    parts.append(rect(ix, y - bh / 2, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    parts.append(mtext(ix + bw / 2, y - 12, "інтегратор\nacc += біт", size=12.5, bold=True, color=NEG))
    parts.append(text(ix + bw / 2, y + 24, "на КОЖНОМУ такті", size=10.5, italic=True, color=NEG))

    # стрілка з проріджуванням ÷R
    x2 = ix + bw
    parts.append(arrow(x2 + 4, y, x2 + 74, y, color=POS, sw=2.4))
    parts.append(text(x2 + 40, y - 12, "÷ R", size=15, bold=True, color=POS))
    parts.append(text(x2 + 40, y + 22, "прорідити", size=10.5, italic=True, color=POS))

    # 3) гребінка (біжить повільно)
    gx = x2 + 80
    parts.append(rect(gx, y - bh / 2, bw, bh, fill="#e9f7ef", stroke=FIELD, sw=2, rx=8))
    parts.append(mtext(gx + bw / 2, y - 12, "гребінка\ny = acc − acc_R", size=12, bold=True, color=FIELD))
    parts.append(text(gx + bw / 2, y + 24, "лише на прорідженому", size=10, italic=True, color=FIELD))

    # стрілка → PCM
    x3 = gx + bw
    parts.append(arrow(x3 + 4, y, x3 + 40, y, color=INK, sw=1.9))

    # 4) PCM багатобітний @ 48 кГц
    px = x3 + 46
    parts.append(rect(px, y - bh / 2, 128, bh, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    parts.append(mtext(px + 64, y - 10, "PCM\n16 біт", size=13, bold=True, color=INK))
    parts.append(text(px + 64, y + 22, "48 кГц", size=11, color=MUTED))

    # смуга «швидка частина» під інтегратором, «повільна» під гребінкою
    fast_l, fast_r = ix - 6, x2 + 6
    slow_l, slow_r = gx - 6, gx + bw + 6
    yb = y + bh / 2 + 26
    parts.append(line(fast_l, yb, fast_r, yb, color=NEG, sw=2))
    parts.append(text((fast_l + fast_r) / 2, yb + 16, "працює на 3.072 МГц (важко)", size=10.5, color=NEG))
    parts.append(line(slow_l, yb, slow_r, yb, color=FIELD, sw=2))
    parts.append(text((slow_l + slow_r) / 2, yb + 16, "працює на 48 кГц (легко)", size=10.5, color=FIELD))

    box, w2, h2 = textbox(W / 2, H - 30,
                          "усереднити на високій частоті → прорідити в R разів → віддати рідкі багатобітні відліки",
                          size=12.5, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/pdm-pipeline.svg", W, H, *parts,
           title="PDM → PCM: інтегратор швидко, гребінка повільно")


# ── two-mic-phase: два мікрофони на СПІЛЬНОМУ такті, фаза фронт/спад ──────────
# Стерео на одній лінії даних: лівий віддає біт по фронту такту, правий — по спаду.
def fig_two_mic():
    W, H = 860, 400
    parts = []

    # такт — прямокутна хвиля згори
    clk_y = 90
    x0, x1 = 90, 770
    period = (x1 - x0) / 6.0
    d = []
    x = x0
    hi = clk_y - 26
    lo = clk_y
    up = True
    d.append("M %.1f %.1f" % (x, lo))
    for i in range(6):
        # піднятися
        d.append("L %.1f %.1f" % (x, hi))
        d.append("L %.1f %.1f" % (x + period / 2, hi))
        d.append("L %.1f %.1f" % (x + period / 2, lo))
        d.append("L %.1f %.1f" % (x + period, lo))
        x += period
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(d), INK))
    parts.append(text(x0 - 12, clk_y - 12, "CLK", size=13, bold=True, color=INK, anchor="end"))
    parts.append(text(x0 - 12, clk_y + 4, "(спільний)", size=10, color=MUTED, anchor="end"))

    # позначки фронтів (↑ синій, лівий) і спадів (↓ зелений, правий)
    for i in range(6):
        xr = x0 + i * period               # фронт (rising)
        xf = x0 + i * period + period / 2   # спад (falling)
        parts.append(arrow(xr, clk_y + 30, xr, clk_y + 6, color=NEG, sw=1.6))
        parts.append(arrow(xf, clk_y + 30, xf, clk_y + 6, color=FIELD, sw=1.6))

    parts.append(text(x0 + period * 0.0, clk_y + 46, "↑ фронт → ЛІВИЙ", size=11, bold=True,
                      color=NEG, anchor="start"))
    parts.append(text(x0 + period * 3.0, clk_y + 46, "↓ спад → ПРАВИЙ", size=11, bold=True,
                      color=FIELD, anchor="start"))

    # лінія DATA — спільна, чергуються L і R
    data_y = clk_y + 120
    parts.append(line(x0, data_y, x1, data_y, color=INK, sw=1.4))
    parts.append(text(x0 - 12, data_y + 4, "DATA", size=13, bold=True, color=INK, anchor="end"))
    parts.append(text(x0 - 12, data_y + 20, "(спільна)", size=10, color=MUTED, anchor="end"))
    # проставити L/R біти на спільній лінії
    for i in range(6):
        xr = x0 + i * period
        xf = x0 + i * period + period / 2
        parts.append(circle(xr, data_y, 9, fill="#eaf0fd", stroke=NEG, sw=1.8))
        parts.append(text(xr, data_y + 4, "L", size=11, bold=True, color=NEG))
        parts.append(circle(xf, data_y, 9, fill="#e9f7ef", stroke=FIELD, sw=1.8))
        parts.append(text(xf, data_y + 4, "R", size=11, bold=True, color=FIELD))

    # два мікрофони — підписи джерел
    parts.append(fitbox(120, data_y + 70, 190, 54,
                        "ЛІВИЙ мік:\nпорт SELECT на GND", size=11.5, fill="#eaf0fd",
                        stroke=NEG, sw=1.8, bold=True))
    parts.append(fitbox(560, data_y + 70, 190, 54,
                        "ПРАВИЙ мік:\nпорт SELECT на живлення", size=11.5, fill="#e9f7ef",
                        stroke=FIELD, sw=1.8, bold=True))

    box, w2, h2 = textbox(W / 2, H - 26,
                          "один такт, одна лінія даних: лівий кладе біт по фронту, правий — по спаду; контролер розбирає їх нарізно",
                          size=12, pad=11, fill=FILL)
    parts.append(box)

    render("img/two-mic-phase.svg", W, H, *parts,
           title="Стерео на спільному такті: фаза розводить два мікрофони")


if __name__ == "__main__":
    fig_pipeline()
    fig_two_mic()
    print("OK: pdm-pipeline, two-mic-phase")
