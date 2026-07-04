# -*- coding: utf-8 -*-
"""Фігури для статті KY-025 — геркон у скляній колбі."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def reed(x1, x2, y, closed=False):
    """Символ геркона: дві пелюстки в скляній колбі. closed=True — контакти зімкнені."""
    out = []
    # скляна колба
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="18" fill="#eef7ff" '
               'stroke="%s" stroke-width="1.4"/>' % ((x1 + x2) / 2, y, (x2 - x1) / 2 + 14, MUTED))
    gap = 0 if closed else 7
    mid = (x1 + x2) / 2
    # ліва пелюстка
    out.append(line(x1, y, mid - 16, y, INK, 3))
    out.append(line(mid - 16, y, mid - gap, y - 4 if not closed else y, INK, 3))
    # права пелюстка
    out.append(line(x2, y, mid + 16, y, INK, 3))
    out.append(line(mid + 16, y, mid + gap, y - 4 if not closed else y, INK, 3))
    return "".join(out)


def node(cx, cy):
    return '<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>' % (cx, cy, INK)


# ─────────────────────────── Фігура 1: устрій плати ───────────────────────────
def fig_board():
    W, H = 940, 600
    p = []

    # шини живлення
    vcc_y, gnd_y = 80, 540
    p.append(line(60, vcc_y, 880, vcc_y, POS, 2.4))
    p.append(text(60, vcc_y - 14, "+V  (3.3–5 В)", size=15, color=POS, anchor="start", bold=True))
    p.append(line(60, gnd_y, 880, gnd_y, NEG, 2.4))
    p.append(text(60, gnd_y + 28, "G  (GND, спільний нуль)", size=15, color=NEG, anchor="start", bold=True))

    node_y = 280

    # ── ліва вітка: підтяжний резистор R зверху, геркон знизу, вузол посередині ──
    reed_x = 150
    p.append(line(reed_x, vcc_y, reed_x, 150, POS, 2))
    # верхній підтяжний резистор R (від +V до вузла)
    p.append(rect(reed_x - 16, 150, 32, 66, fill=BG))
    p.append(text(reed_x - 26, 188, "R", size=15, bold=True, anchor="end"))
    p.append(line(reed_x, 216, reed_x, node_y, INK, 2))

    p.append(node(reed_x, node_y))
    p.append(text(reed_x - 22, node_y - 12, "вузол", size=12, color=MUTED, anchor="end"))

    # геркон від вузла до GND
    p.append(line(reed_x, node_y, reed_x, 330, INK, 2))
    p.append(reed(reed_x - 40, reed_x + 40, 372, closed=False))
    # підписи геркона — ЛІВОРУЧ від колби, поза зворотними дротами (x<94)
    p.append(text(reed_x - 72, 366, "геркон", size=13, bold=True, anchor="end"))
    p.append(text(reed_x - 72, 384, "норм.", size=11, color=MUTED, anchor="end"))
    p.append(text(reed_x - 72, 400, "розімкнений", size=11, color=MUTED, anchor="end"))
    p.append(line(reed_x - 56, 372, reed_x - 56, gnd_y, INK, 2))
    p.append(line(reed_x - 56, 372, reed_x - 40, 372, INK, 2))
    p.append(line(reed_x + 40, 372, reed_x + 56, 372, INK, 2))
    p.append(line(reed_x + 56, 372, reed_x + 56, gnd_y, INK, 2))
    # магніт-підказка (праворуч від колби, з запасом)
    p.append(rect(reed_x + 84, 354, 80, 40, fill="#fdf0e6", stroke=POS, sw=1.4))
    p.append(text(reed_x + 124, 371, "магніт", size=12, color=POS))
    p.append(text(reed_x + 124, 387, "змикає", size=11, color=POS))

    # відгалуження на вузол → праворуч до розгалуження
    branch_x = 340
    p.append(line(reed_x, node_y, branch_x, node_y, INK, 2))
    p.append(node(branch_x, node_y))
    # вниз до A0
    p.append(line(branch_x, node_y, branch_x, 486, INK, 2))

    # ── компаратор LM393 ──
    cx, cy = 500, node_y
    # трикутник
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (cx, cy - 50, cx, cy + 50, cx + 96, cy, "#f4f6f8", LINE))
    p.append(text(cx + 38, cy + 5, "LM393", size=13, bold=True))
    # вхід + (від вузла) — мітку ставимо ВСЕРЕДИНІ трикутника, поза вхідними лініями
    p.append(line(branch_x, node_y, cx + 4, cy - 26, INK, 2))
    p.append(text(cx + 16, cy - 20, "+", size=16, color=POS, bold=True, anchor="middle"))
    # вхід − (від движка потенціометра)
    p.append(text(cx + 16, cy + 26, "−", size=16, color=NEG, bold=True, anchor="middle"))

    # потенціометр (опора порогу) ліворуч-знизу, окремою колонкою — не під трикутником
    pot_x = 400
    p.append(line(pot_x, gnd_y, pot_x, 430, POS, 2))
    p.append(rect(pot_x - 18, 364, 36, 66, fill=BG))
    p.append(text(pot_x - 26, 402, "потенц.", size=12, color=MUTED, anchor="end"))
    p.append(line(pot_x, 364, pot_x, 336, POS, 2))
    p.append(line(pot_x, 336, cx - 14, 336, POS, 2))
    # движок-стрілка порогу до мінус-входу
    p.append(line(cx - 14, 336, cx - 14, cy + 26, POS, 2))
    p.append(arrow(cx - 14, cy + 26, cx + 4, cy + 26, POS, 2))
    p.append(text(pot_x + 26, 356, "поріг →", size=12, color=POS, anchor="start"))

    # вихід компаратора (відкритий колектор) + підтяжка до +V + D0
    out_x = cx + 96
    pull_x = 720
    p.append(line(out_x, cy, pull_x, cy, INK, 2))
    p.append(node(pull_x, cy))
    # підтяжний резистор Rp від +V
    p.append(line(pull_x, vcc_y, pull_x, 180, POS, 2))
    p.append(rect(pull_x - 16, 180, 32, 66, fill=BG))
    p.append(text(pull_x + 26, 218, "Rp", size=14, bold=True, anchor="start"))
    p.append(line(pull_x, 246, pull_x, cy, POS, 2))
    # D0 вивід
    out2_x = 830
    p.append(line(pull_x, cy, out2_x, cy, INK, 2))
    p.append(node(out2_x, cy))
    p.append(line(out2_x, cy, out2_x, 486, INK, 2))

    # виводи-таблички A0 і D0 знизу
    p.append(fitbox(branch_x - 62, 486, 124, 46, "A0\nаналог вузла", size=13, bold=True,
                    fill="#eef7ff", stroke=NEG))
    p.append(fitbox(out2_x - 62, 486, 124, 46, "D0\nцифра 0/1", size=13, bold=True,
                    fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'board.svg'), W, H, *p,
           title="Устрій KY-025: геркон-дільник, компаратор LM393, два виходи")


# ─────────────────────── Фігура 2: чому A0 не аналоговий ──────────────────────
def fig_analog():
    W, H = 820, 380
    p = []
    # осі
    ox, oy = 120, 300
    p.append(line(ox, 60, ox, oy, INK, 2))
    p.append(line(ox, oy, 760, oy, INK, 2))
    p.append(text(ox - 10, 70, "напруга A0", size=13, anchor="end", color=INK))
    p.append(text(760, oy + 26, "відстань до магніту →", size=13, anchor="end", color=INK))

    hi, lo = 90, 250  # рівні напруги (px)
    xnear, xfar = 220, 640
    p.append(line(ox, lo, xnear, lo, MUTED, 1.4, dash="5 5"))
    p.append(line(ox, hi, xnear, hi, MUTED, 1.4, dash="5 5"))
    p.append(text(ox - 10, lo + 5, "низько", size=12, anchor="end", color=NEG))
    p.append(text(ox - 10, hi + 5, "високо", size=12, anchor="end", color=POS))

    # ідеальний «аналог», якого немає (пунктир, сірий)
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="6 6"/>' % (xnear, lo, 430, hi, xfar + 40, hi, MUTED))
    p.append(text(500, 150, "як мріється (плавно) — НЕ так", size=13, color=MUTED, anchor="start"))

    # реальний крок: два рівні зі стрибком
    p.append(line(xnear, lo, 420, lo, FIELD, 3.2))
    p.append(line(420, lo, 420, hi, FIELD, 3.2))
    p.append(line(420, hi, 760, hi, FIELD, 3.2))
    p.append(text(300, lo - 14, "зімкнено", size=13, color=FIELD, bold=True, anchor="middle"))
    p.append(text(600, hi - 14, "розімкнено", size=13, color=FIELD, bold=True, anchor="middle"))
    p.append(text(438, 200, "стрибок", size=12, color=INK, anchor="start"))
    p.append(text(438, 218, "у точці змикання", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, 'analog-step.svg'), W, H, *p,
           title="Вихід A0 не плавний: геркон дає лише два рівні")


# ─────────────────────────── Фігура 3: підключення ───────────────────────────
def fig_wiring():
    W, H = 860, 470
    p = []

    # модуль KY-025 (ліворуч)
    mx, my, mw, mh = 60, 80, 230, 300
    p.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=LINE, sw=2))
    p.append(text(mx + mw / 2, my - 14, "модуль KY-025", size=15, bold=True))
    # геркон-колба на модулі
    p.append(reed(mx + 60, mx + 170, my + 66, closed=False))
    p.append(text(mx + mw / 2, my + 112, "геркон", size=12, color=MUTED))

    pins = [("G", NEG), ("+", POS), ("D0", FIELD), ("A0", "#8e44ad")]
    py0 = my + 150
    step = 42
    px = mx + mw
    # МК (праворуч)
    kx, ky, kw, kh = 600, 110, 200, 300
    p.append(rect(kx, ky, kw, kh, fill="#eef7ff", stroke=LINE, sw=2))
    p.append(text(kx + kw / 2, ky - 14, "мікроконтролер", size=15, bold=True))

    targets_y = [ky + 250, ky + 60, ky + 120, ky + 180]
    labels = ["GND", "5V", "D2", "A0 (АЦП)"]
    for i, (nm, col) in enumerate(pins):
        y = py0 + i * step
        # штирок на модулі
        p.append(rect(px - 4, y - 13, 30, 26, fill=BG, stroke=col, sw=1.8))
        p.append(text(px + 11, y + 5, nm, size=13, bold=True, color=col))
        # дріт до МК
        ty = targets_y[i]
        p.append(line(px + 26, y, kx, ty, col, 2.2))
        # клема МК
        p.append(rect(kx - 30, ty - 13, 30, 26, fill=BG, stroke=col, sw=1.8))
        p.append(text(kx - 15, ty + 5, labels[i], size=11, bold=True, color=col))

    # примітка про A0 (внизу, широка рамка з запасом)
    p.append(fitbox(60, 410, 740, 42,
                    "D0 дає готову відповідь; A0 у геркона майже даремний — два рівні, тож його зазвичай не під'єднують",
                    size=12, fill="#fff8e6", stroke="#c98a00"))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *p,
           title="Підключення KY-025: чотири дроти, а працює цифровий")


if __name__ == '__main__':
    fig_board()
    fig_analog()
    fig_wiring()
    print("OK: board.svg, analog-step.svg, wiring.svg")
