# -*- coding: utf-8 -*-
# Фігури для детальної статті camera-interfaces-mcu-d.md
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _poly(pts, color, sw=2.4, dash=None):
    d = "M " + " L ".join("%.1f %.1f" % (x, yv) for x, yv in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, da)


def fig_dphy_lp_hs():
    """Одна пара D-PHY у двох режимах: дрімотний LP (великий розмах, 2 незалежні
    дроти) і спалах HS (крихітний диференційний розмах, гігабіти)."""
    W, H = 980, 560
    parts = [text(W / 2, 32, "Одна пара MIPI D-PHY — два режими роботи", size=18, bold=True)]

    # дві половини
    midx = W / 2
    parts.append(line(midx, 66, midx, H - 70, color="#dfe4ea", sw=1.4, dash="4 4"))

    # ── ЛІВА половина: LP ─────────────────────────────────────────────
    lx0, lx1 = 60, midx - 40
    parts.append(fitbox(lx0, 62, lx1 - lx0, 34, "LP — низьке споживання (пауза, команди)",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG))

    # два незалежні дроти, кожен зі своїм рівнем 0/1, великий розмах
    def wave(y_base, amp, seq, x0, x1, color, label):
        step = (x1 - x0) / len(seq)
        pts = []
        for k, b in enumerate(seq):
            xx = x0 + k * step
            yv = y_base - amp if b else y_base
            pts.append((xx, yv))
            pts.append((xx + step, yv))
        parts.append(_poly(pts, color, sw=2.6))
        parts.append(text(x0 - 10, y_base - amp / 2 + 4, label, size=11.5, bold=True,
                          color=color, anchor="end"))

    # рівні напруги ліворуч
    lp_top = 150
    parts.append(text(lx0, lp_top - 34, "розмах ~1.2 В (повний логічний рівень)",
                      size=11, color=MUTED, anchor="start"))
    wave(lp_top + 40, 50, [1, 0, 1, 1, 0, 0, 1, 0], lx0 + 44, lx1 - 14, NEG, "Dp")
    wave(lp_top + 140, 50, [0, 1, 1, 0, 1, 0, 0, 1], lx0 + 44, lx1 - 14, "#6b8fe0", "Dn")

    parts.append(fitbox(lx0 + 20, lp_top + 200, lx1 - lx0 - 24, 70,
                        "два дроти живуть ОКРЕМО, кожен 0 або 1:\n"
                        "4 стани LP-00 · LP-01 · LP-10 · LP-11\n"
                        "мало струму в спокої, швидкість мала",
                        size=11, fill="#f5f8ff", stroke=NEG, sw=1.4, color=INK))

    # ── ПРАВА половина: HS ────────────────────────────────────────────
    rx0, rx1 = midx + 40, W - 60
    parts.append(fitbox(rx0, 62, rx1 - rx0, 34, "HS — висока швидкість (самі пікселі)",
                        size=13, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, color="#1f7a46"))

    hs_top = 150
    parts.append(text(rx0, hs_top - 34, "розмах ~0.2 В навколо спільного рівня",
                      size=11, color=MUTED, anchor="start"))
    # диференційна пара: Dp і Dn у ПРОТИФАЗІ, малий розмах, щільно
    base_p = hs_top + 60
    amp = 16
    seq = [1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0]
    step = (rx1 - 20 - (rx0 + 44)) / len(seq)
    ptp, ptn = [], []
    x = rx0 + 44
    for b in seq:
        yp = base_p - amp if b else base_p + amp
        yn = base_p + amp if b else base_p - amp
        ptp += [(x, yp), (x + step, yp)]
        ptn += [(x, yn), (x + step, yn)]
        x += step
    # спільний рівень (пунктир)
    parts.append(line(rx0 + 44, base_p, rx1 - 20, base_p, color="#c9cfd8", sw=1, dash="3 3"))
    parts.append(_poly(ptp, FIELD, sw=2.4))
    parts.append(_poly(ptn, "#7fc59b", sw=2.4))
    parts.append(text(rx0 + 34, base_p - amp + 3, "Dp", size=11, bold=True, color=FIELD, anchor="end"))
    parts.append(text(rx0 + 34, base_p + amp + 8, "Dn", size=11, bold=True, color="#5aa87a", anchor="end"))
    parts.append(text((rx0 + rx1) / 2 + 30, base_p + 44, "протифаза → приймач бере різницю",
                      size=10.5, color=MUTED, anchor="middle"))

    parts.append(fitbox(rx0 + 20, hs_top + 200, rx1 - rx0 - 24, 70,
                        "пара стає ДИФЕРЕНЦІЙНОЮ (дроти в протифазі):\n"
                        "наводка гасне в різниці, малий розмах — швидко\n"
                        "швидкість — гігабіти на смугу",
                        size=11, fill="#f2fbf6", stroke=FIELD, sw=1.4, color=INK))

    # ── низ: перехід SoT/EoT ──
    parts.append(fitbox(60, H - 62, W - 120, 46,
                        "лінія спить у LP → сигнал SoT (старт) → спалах HS з пікселями → сигнал EoT (кінець) → знову LP.\n"
                        "Увімкнув, вистрілив, вимкнув — тому камера не гріється й не з'їдає батарею в спокої.",
                        size=11.5, bold=True, fill="#fbfcfe", stroke=MUTED, sw=1.4, color=INK))

    render(os.path.join(OUT, "dphy-lp-hs.svg"), W, H, *parts)


def fig_bandwidth_ladder():
    """Стеля пропускної здатності трьох інтерфейсів у лог-масштабі."""
    W, H = 920, 470
    parts = [text(W / 2, 32, "Стеля пропускної здатності: прірва у два порядки", size=18, bold=True)]

    # лог-вісь по X: 1 … 2000 Мбіт/с
    import math
    x_axis_l, x_axis_r = 210, W - 60
    y_top, y_bot = 80, 360
    lo, hi = math.log10(4), math.log10(2000)

    def xpos(mbit):
        return x_axis_l + (math.log10(mbit) - lo) / (hi - lo) * (x_axis_r - x_axis_l)

    # сітка декад
    for dec in [10, 100, 1000]:
        gx = xpos(dec)
        parts.append(line(gx, y_top - 6, gx, y_bot + 6, color="#e7ebf1", sw=1.2, dash="3 4"))
        lbl = "%d Мбіт/с" % dec if dec < 1000 else "1 Гбіт/с"
        parts.append(text(gx, y_bot + 26, lbl, size=10.5, color=MUTED))

    # три смуги
    rows = [
        ("SPI-камера", "8 МГц · ~8 Мбіт/с\nкілька кадрів QVGA", 8, "#c96a1b", "#fff3e6"),
        ("DVP", "24 МГц PCLK · ~400 Мбіт/с\nживе VGA-відео", 400, NEG, "#eaf0fd"),
        ("MIPI (1 пара)", "800 Мбіт/с · ×кілька смуг\nHD і 4K", 800, FIELD, "#eafaf0"),
    ]
    bar_h = 54
    gap = 30
    y = y_top
    for name, sub, val, col, fill in rows:
        cy = y + bar_h / 2
        # смуга від початку осі до значення
        bx1 = xpos(val)
        parts.append(rect(x_axis_l, y, bx1 - x_axis_l, bar_h, fill=fill, stroke=col, sw=1.8, rx=6))
        # мітка інтерфейсу ліворуч
        parts.append(fitbox(30, y, x_axis_l - 42, bar_h, name, size=13, bold=True,
                            fill="none", stroke="none", color=col))
        # підпис усередині/поряд зі смугою
        parts.append(mtext(bx1 + 12, cy - 4, sub.split("\n"), size=10.5, color=INK, anchor="start"))
        # кінцева риска-значення
        parts.append(circle(bx1, cy, 5, fill=col, stroke=BG, sw=2))
        y += bar_h + gap

    # вісь
    parts.append(line(x_axis_l, y_bot + 6, x_axis_r, y_bot + 6, color=MUTED, sw=2))
    parts.append(arrow(x_axis_r, y_bot + 6, x_axis_r + 18, y_bot + 6, color=MUTED, sw=2))
    parts.append(text(x_axis_l, y_bot + 48, "логарифмічна шкала — кожна декада вдесятеро",
                      size=10.5, color=MUTED, anchor="start"))

    parts.append(fitbox(60, H - 54, W - 120, 36,
                        "між SPI і MIPI — сто разів: саме ця прірва, а не примха, розводить камери "
                        "по різних мозках — дрібний МК тягне лише нижню сходинку",
                        size=11.5, bold=True, fill="#fbfcfe", stroke=POS, sw=1.4, color=INK))

    render(os.path.join(OUT, "bandwidth-ladder.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_dphy_lp_hs()
    fig_bandwidth_ladder()
    print("done")
