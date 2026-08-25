# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def wave(x0, y_hi, y_lo, period, seq, color=INK, sw=2.2):
    """Цифрова хвиля за списком рівнів seq (0/1). Повертає SVG-ламану."""
    pts = []
    x = x0
    prev = seq[0]
    y = y_lo if prev == 0 else y_hi
    pts.append((x, y))
    for lvl in seq:
        ny = y_lo if lvl == 0 else y_hi
        if ny != y:
            pts.append((x, ny))  # вертикальний фронт
        y = ny
        x += period
        pts.append((x, y))
    d = " ".join(("%s%.1f,%.1f" % ("M" if i == 0 else "L", px, py))
                 for i, (px, py) in enumerate(pts))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── Фігура 1: рукостискання VALID/READY ─────────────────────────────────────
def fig_handshake():
    W, H = 720, 300
    x0, per = 150, 55
    n = 9
    clk_hi, clk_lo = 70, 95
    v_hi, v_lo = 140, 165
    r_hi, r_lo = 205, 230

    frags = [text(W / 2, 26, "Одне рукостискання: перенесення на спільному фронті", size=17, bold=True)]

    # такт
    clk = []
    for i in range(n):
        clk += [1, 0]
    frags.append(wave(x0, clk_hi, clk_lo, per / 2, clk, color=MUTED))
    frags.append(text(x0 - 20, (clk_hi + clk_lo) / 2 + 4, "CLK", size=13, color=MUTED, anchor="end"))

    # VALID: джерело підняло рано і тримає
    valid = [0, 1, 1, 1, 1, 0, 0, 0, 0]
    frags.append(wave(x0, v_hi, v_lo, per, valid, color=POS))
    frags.append(text(x0 - 20, (v_hi + v_lo) / 2 + 4, "VALID", size=13, color=POS, anchor="end"))

    # READY: приймач готовий пізніше
    ready = [0, 0, 0, 1, 1, 0, 0, 0, 0]
    frags.append(wave(x0, r_hi, r_lo, per, ready, color=NEG))
    frags.append(text(x0 - 20, (r_hi + r_lo) / 2 + 4, "READY", size=13, color=NEG, anchor="end"))

    # момент перенесення: обидва високі на фронті такту (такт 4 -> між 3 і 4)
    xh = x0 + per * 3
    frags.append(line(xh, 55, xh, 250, color=FIELD, sw=2, dash="5,4"))
    box, bw, bh = textbox(xh, 272, "тут VALID=1 і READY=1 → перенос стався", size=12,
                          color=FIELD, stroke=FIELD, fill="#eafaf0")
    frags.append(box)
    return render(os.path.join(IMG, 'handshake.svg'), W, H, *frags)


# ── Фігура 2: п'ять каналів між ведучим і веденим ───────────────────────────
def fig_channels():
    W, H = 720, 420
    frags = [text(W / 2, 26, "П'ять незалежних каналів: три на запис, два на читання", size=17, bold=True)]

    mx, my, mw, mh = 40, 80, 150, 280
    sx = W - 40 - mw
    frags.append(rect(mx, my, mw, mh))
    frags.append(text(mx + mw / 2, my - 10, "Ведучий (master)", size=13, bold=True))
    frags.append(text(mx + mw / 2, my + mh / 2, "процесор /\nDMA", size=13))
    frags.append(rect(sx, my, mw, mh))
    frags.append(text(sx + mw / 2, my - 10, "Ведений (slave)", size=13, bold=True))
    frags.append(text(sx + mw / 2, my + mh / 2, "памʼять /\nпериферія", size=13))

    chans = [
        ("AW  адреса запису", POS, "→"),
        ("W   дані запису", POS, "→"),
        ("B   відповідь запису", POS, "←"),
        ("AR  адреса читання", NEG, "→"),
        ("R   дані читання", NEG, "←"),
    ]
    y = my + 34
    dy = (mh - 60) / 4
    xa, xb = mx + mw + 8, sx - 8
    for label, col, dirc in chans:
        yy = y
        if dirc == "→":
            frags.append(arrow(xa, yy, xb, yy, color=col))
        else:
            frags.append(arrow(xb, yy, xa, yy, color=col))
        frags.append(text((xa + xb) / 2, yy - 8, label, size=12.5, color=col, bold=True))
        y += dy
    frags.append(text(W / 2, my + mh + 34,
                      "Кожна стрілка — свій канал зі своєю парою VALID/READY; усі йдуть паралельно.",
                      size=12, color=MUTED))
    return render(os.path.join(IMG, 'channels.svg'), W, H, *frags)


# ── Фігура 3: пакет — одна адреса, багато порцій ────────────────────────────
def fig_burst():
    W, H = 720, 260
    frags = [text(W / 2, 26, "Пакет (burst): одна адреса — багато порцій підряд", size=17, bold=True)]

    # ліворуч: одна адреса + довжина
    ax, ay = 40, 70
    b, bw, bh = textbox(ax + 95, ay + 55, "AR: адреса = 0x1000\nдовжина = 4\nрозмір = 4 байти",
                        size=12.5, color=NEG, stroke=NEG, fill="#eaf0fd")
    frags.append(b)
    frags.append(text(ax + 95, ay + 5, "1 адреса", size=13, bold=True, color=NEG))

    # праворуч: чотири порції даних
    startx = 300
    cw, gap = 90, 12
    yb = 120
    addrs = ["0x1000", "0x1004", "0x1008", "0x100C"]
    for i in range(4):
        x = startx + i * (cw + gap)
        frags.append(rect(x, yb, cw, 56, fill="#eaf0fd", stroke=NEG))
        frags.append(text(x + cw / 2, yb + 24, "порція %d" % (i + 1), size=12.5, bold=True))
        frags.append(text(x + cw / 2, yb + 44, addrs[i], size=11.5, color=MUTED))
    frags.append(arrow(ax + 195, yb + 28, startx - 8, yb + 28, color=NEG))
    frags.append(text((ax + 195 + startx) / 2, yb + 16, "R×4", size=12, color=NEG, bold=True))
    frags.append(text(W / 2, 235,
                      "Адресу шлемо раз; ведений сам крокує адресами і віддає порції потоком.",
                      size=12, color=MUTED))
    return render(os.path.join(IMG, 'burst.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_handshake()
    fig_channels()
    fig_burst()
    print("figs done")
