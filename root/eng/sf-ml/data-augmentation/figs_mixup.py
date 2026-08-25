# -*- coding: utf-8 -*-
"""Фігури до вставки «math-mixup». Окремий модуль (щоб не чіпати спільний figs.py).
Чистий Python, svgkit зі scripts/. Вивід — у ./img/ поряд з рештою фігур теми."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _blend_swatch(x, y, w, h, lam):
    """Квадрат-«кадр»: гарячий клас A і холодний клас B, накладені як
    λ·A + (1−λ)·B — двома напівпрозорими шарами (imітація змішування пікселів)."""
    out = [rect(x, y, w, h, fill=BG, stroke=LINE, sw=1.5, rx=6)]
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
               'fill="%s" fill-opacity="%.3f"/>' % (x, y, w, h, POS, round(lam, 3)))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
               'fill="%s" fill-opacity="%.3f"/>' % (x, y, w, h, NEG, round(1 - lam, 3)))
    return "".join(out)


def fig_mixup_line():
    """Опукла комбінація: два приклади — кінці відрізка, λ ковзає між ними;
    і пікселі, і ярлик рухаються тим самим кроком λ."""
    W, H = 760, 380
    frags = [text(W/2, 26, "mixup: один важіль λ рухає і кадр, і ярлик", size=17, bold=True)]
    ax, bx, yline = 120, 640, 150
    sq = 84
    frags.append(_blend_swatch(ax - sq/2, yline - sq/2, sq, sq, 1.0))
    frags.append(text(ax, yline - sq/2 - 12, "приклад i", size=13, bold=True, color=POS))
    frags.append(text(ax, yline + sq/2 + 20, "yᵢ = кіт", size=12, bold=True, color=POS))
    frags.append(_blend_swatch(bx - sq/2, yline - sq/2, sq, sq, 0.0))
    frags.append(text(bx, yline - sq/2 - 12, "приклад j", size=13, bold=True, color=NEG))
    frags.append(text(bx, yline + sq/2 + 20, "yⱼ = пес", size=12, bold=True, color=NEG))
    axisY = 300
    frags.append(line(ax, axisY, bx, axisY, color=INK, sw=2))
    frags.append(text(ax, axisY + 26, "λ = 1", size=12, bold=True, color=POS))
    frags.append(text(bx, axisY + 26, "λ = 0", size=12, bold=True, color=NEG))
    frags.append(text(W/2, axisY + 46, "важіль λ (з бета-розподілу): один на пару, керує обома рядками одразу",
                      size=11, color=MUTED))
    for lam, lbl in [(0.75, "λ=0.75"), (0.5, "λ=0.5"), (0.25, "λ=0.25")]:
        px = ax + (1 - lam) * (bx - ax)
        s2 = 62
        frags.append(_blend_swatch(px - s2/2, yline - s2/2 + 6, s2, s2, lam))
        frags.append(line(px, yline + s2/2 + 12, px, axisY, color=MUTED, sw=1.2, dash="3,3"))
        frags.append(circle(px, axisY, 4, fill=INK, stroke=INK))
        frags.append(text(px, axisY - 12, lbl, size=10, bold=True, color=MUTED))
    box, _, _ = textbox(W/2, 352, "x̃ = λ·xᵢ + (1−λ)·xⱼ      ỹ = λ·yᵢ + (1−λ)·yⱼ",
                        size=13, bold=True, fill="#fdf6e3", stroke=POS)
    frags.append(box)
    render(os.path.join(OUT, 'mixup-line.svg'), W, H, *frags)


def fig_mix_family():
    """mixup / Cutout / CutMix — як кожен поєднує два кадри і що стає з ярликом."""
    W, H = 760, 340
    frags = [text(W/2, 26, "Родина змішувань: чим різняться mixup, Cutout, CutMix", size=16, bold=True)]
    cw, ch = 150, 130
    gy = 74
    cols = [
        (130, "mixup", "усюди прозоро|накладені два кадри", "ỹ = 0.6·кіт + 0.4·пес", "mix", POS),
        (380, "Cutout", "вирізаний|чорний квадрат", "y = кіт (не змінився)", "cut", FIELD),
        (630, "CutMix", "вставлена латка|з чужого кадру", "ỹ = 0.75·кіт + 0.25·пес", "cutmix", POS),
    ]
    for cx, name, how, ylabel, kind, ycol in cols:
        x0 = cx - cw/2
        if kind == "mix":
            frags.append(_blend_swatch(x0, gy, cw, ch, 0.6))
        elif kind == "cut":
            frags.append(rect(x0, gy, cw, ch, fill="#fdecea", stroke=LINE, sw=1.5, rx=6))
            frags.append(rect(cx - 26, gy + ch/2 - 26, 52, 52, fill=INK, stroke=INK, rx=4))
        else:  # cutmix
            frags.append(rect(x0, gy, cw, ch, fill="#fdecea", stroke=LINE, sw=1.5, rx=6))
            frags.append('<rect x="%.1f" y="%.1f" width="52" height="52" rx="4" '
                         'fill="%s" fill-opacity="0.85"/>' % (x0 + cw - 62, gy + ch - 62, NEG))
        frags.append(text(cx, gy - 10, name, size=14, bold=True))
        top, bot = how.split("|")
        frags.append(text(cx, gy + ch + 20, top, size=10, color=MUTED))
        frags.append(text(cx, gy + ch + 34, bot, size=10, color=MUTED))
        frags.append(fitbox(cx - cw/2, gy + ch + 46, cw, 32, ylabel, size=11, bold=True,
                            fill=BG, stroke=ycol, color=INK))
    render(os.path.join(OUT, 'mix-family.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_mixup_line()
    fig_mix_family()
    print("mixup figs done")
