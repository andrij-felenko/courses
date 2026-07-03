# -*- coding: utf-8 -*-
# Фігури для вставки math-von-kries-diagonal.md (тема «Баланс білого»).
# Окремий генератор, щоб не конфліктувати з паралельним редагуванням figs.py;
# пише в той самий ./img/. Запуск: python figs_vonkries.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── narrow-vs-broad: умова точної діагоналі — E'(λ)/E(λ) стале В МЕЖАХ смуги.
#    Вузька чутливість накриває клаптик, де відношення майже пласке → точно;
#    широка перекривна накриває пів-діапазону, де відношення пливе → похибка.

def _spectrum_axis(x0, y0, axw, axh):
    """Осі спектральної панелі: горизонталь λ (380..700), рамка."""
    out = [rect(x0, y0 - axh, axw, axh, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=6)]
    out.append(line(x0, y0, x0 + axw, y0, color=INK, sw=1.4))          # вісь λ
    for frac, lab in [(0.0, "380"), (0.5, "540"), (1.0, "700 нм")]:
        xx = x0 + frac * axw
        out.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.0))
        out.append(text(xx, y0 + 17, lab, size=9, color=MUTED))
    return out


def _bump(x0, y0, axw, ctr, wid, amp, col, sw=2.4):
    """Гладкий «горб» чутливості: гаусів дзвін, центр ctr(0..1), ширина wid, висота amp."""
    pts = []
    n = 44
    for i in range(n + 1):
        t = i / float(n)                     # 0..1 уздовж λ
        z = (t - ctr) / (wid * 0.5)
        v = amp * (2.718281828 ** (-z * z))  # гаусова форма
        pts.append((x0 + t * axw, y0 - v))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw))


def fig_narrow_vs_broad():
    W, H = 880, 440
    p = [text(W / 2, 24, "Чому ширина чутливості вирішує все", size=15, bold=True)]
    p.append(text(W / 2, 43, "точна діагональ ⟺ відношення E'(λ)/E(λ) стале в межах смуги кожного каналу",
                  size=10, color=MUTED))

    RC, BC = "#d64545", "#3b6fd6"
    RATIO = "#8a4fd6"   # крива відношення E'(λ)/E(λ)

    for (x0, title, narrow) in [
            (55,  "Вузькі чутливості → діагональ ТОЧНА", True),
            (470, "Широкі перекривні → діагональ ХИБИТЬ", False)]:
        axw, axh = 355, 150
        yb = 258                                # базова лінія осі λ
        p.append(text(x0 + axw / 2, 64, title, size=12, bold=True))

        p.extend(_spectrum_axis(x0, yb, axw, axh))

        # відношення освітлень E'(λ)/E(λ): пливе від 0.3 (синій край) до ~1.25 (червоний)
        rp = []
        n = 44
        for i in range(n + 1):
            t = i / float(n)
            v = 0.30 + 0.95 * t
            rp.append((x0 + t * axw, yb - v * 92))
        dR = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in rp)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                 'stroke-dasharray="5 3"/>' % (dR, RATIO))
        p.append(text(x0 + axw - 6, yb - 1.25 * 92 - 8, "E'(λ)/E(λ)", size=10,
                      color=RATIO, bold=True, anchor="end"))

        if narrow:
            p.append(_bump(x0, yb, axw, 0.30, 0.15, 120, BC))     # «синій»
            p.append(_bump(x0, yb, axw, 0.72, 0.15, 120, RC))     # «червоний»
            p.append(text(x0 + 0.30 * axw, yb - 132, "S_B", size=11, color=BC, bold=True))
            p.append(text(x0 + 0.72 * axw, yb - 132, "S_R", size=11, color=RC, bold=True))
            for ctr, col in [(0.30, BC), (0.72, RC)]:
                bx = x0 + (ctr - 0.075) * axw
                p.append(rect(bx, yb - 100, 0.15 * axw, 94, fill="none",
                              stroke=col, sw=1.0, rx=3))
            note = ("У межах вузького клаптика відношення E'/E майже пласке — "
                    "один коефіцієнт g скасовує перекіс точно.")
            p.append(fitbox(x0 + 12, 316, axw - 24, 62, note, size=10, pad=10,
                            fill="#eef7f0", stroke=FIELD, sw=1.3))
        else:
            # зона перекриття — під горбами
            ox = x0 + 0.44 * axw
            p.append(rect(ox, yb - 130, 0.14 * axw, 124, fill="#f0e6fb",
                          stroke="none", sw=0, rx=0))
            p.append(_bump(x0, yb, axw, 0.38, 0.52, 120, BC))
            p.append(_bump(x0, yb, axw, 0.64, 0.52, 120, RC))
            p.append(text(x0 + 0.16 * axw, yb - 118, "S_B", size=11, color=BC, bold=True))
            p.append(text(x0 + 0.88 * axw, yb - 118, "S_R", size=11, color=RC, bold=True))
            p.append(text(ox + 0.07 * axw, yb - 136, "перекриття", size=9,
                          color=RATIO, bold=True))
            note = ("Широка смуга накриває пів-діапазону, де E'/E встигає "
                    "змінитися — єдине g не випрямляє, потрібна матриця 3×3.")
            p.append(fitbox(x0 + 12, 316, axw - 24, 62, note, size=10, pad=10,
                            fill="#fdf3f0", stroke=POS, sw=1.3))

    render(os.path.join(OUT, "narrow-vs-broad.svg"), W, H, *p)


# ── cat-pipeline: проста камера множить сирі RGB напряму (діагональ у RGB);
#    CAT переходить у загострений колбочковий простір M, множить діагональ D,
#    повертається M⁻¹ — та сама ідея фон Кріса, лише у правильному просторі.

def _chip3(cx, cy, vals, cols, bw=16, gap=6, sc=0.34):
    """Трійка стовпчиків (R/G/B чи L/M/S) значеннями vals."""
    out = []
    base = cy + 30
    x0 = cx - (3 * bw + 2 * gap) / 2
    for i, v in enumerate(vals):
        bx = x0 + i * (bw + gap)
        out.append(rect(bx, base - v * sc, bw, v * sc, fill=cols[i], stroke=INK, sw=0.8, rx=2))
    return out


def fig_cat_pipeline():
    W, H = 900, 430
    p = [text(W / 2, 26, "Дві реалізації однієї діагоналі фон Кріса", size=15, bold=True)]

    RC, GC, BC = "#d64545", "#3aa856", "#3b6fd6"
    LC, MC, SC = "#c07818", "#2f9e6f", "#5a6fd0"   # колбочковий L/M/S простір

    def stage(cx, cy, label, sub, w=98, h=50, fill="#f4f6f8", stroke=INK):
        p.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.5, rx=8))
        p.append(text(cx, cy - 3, label, size=13, bold=True))
        p.append(text(cx, cy + 14, sub, size=8, color=MUTED))

    # ── верхній ряд: проста камера, діагональ прямо в RGB ──
    ry = 110
    p.append(text(60, ry - 56, "Проста камера", size=12, bold=True, anchor="start"))
    p.extend(_chip3(118, ry, [210, 150, 78], [RC, GC, BC]))
    p.append(text(118, ry + 40, "сирі RGB (перекіс)", size=9, color=MUTED))

    p.append(arrow(168, ry, 236, ry, color=POS, sw=2.2))
    stage(312, ry, "× діагональ", "g_R g_G g_B", fill="#f0f9f4", stroke=FIELD, w=118)
    p.append(text(312, ry - 40, "три коефіцієнти прямо в RGB", size=9, color=MUTED))

    p.append(arrow(372, ry, 452, ry, color=POS, sw=2.2))
    p.extend(_chip3(520, ry, [150, 150, 150], [RC, GC, BC]))
    p.append(text(520, ry + 40, "R=G=B, нейтраль", size=9, color=MUTED))

    p.append(fitbox(600, ry - 42, 250, 84,
                    "Працює, бо фільтри Баєра доволі вузькі — діагональ у самому RGB уже добра. "
                    "Три множення на піксель, жодного змішування каналів.",
                    size=10, pad=10, fill="#eef7f0", stroke=FIELD, sw=1.3))

    # роздільник
    p.append(line(46, 190, W - 46, 190, color=MUTED, sw=1.0, dash="4 4"))

    # ── нижній ряд: CAT — M → діагональ D → M⁻¹ ──
    cy = 292
    p.append(text(60, cy - 70, "Адаптаційне перетворення (Bradford, CAT02)", size=12,
                  bold=True, anchor="start"))

    p.extend(_chip3(104, cy, [210, 150, 78], [RC, GC, BC]))
    p.append(text(104, cy + 40, "XYZ / RGB", size=9, color=MUTED))

    p.append(arrow(142, cy, 206, cy, color=NEG, sw=2.2))
    stage(258, cy, "M", "у загострений", fill="#eef2fb", stroke=NEG, w=92)
    p.append(text(258, cy - 38, "колбочковий простір", size=8, color=MUTED))

    p.append(arrow(304, cy, 356, cy, color=INK, sw=2.0))
    p.extend(_chip3(400, cy, [180, 150, 96], [LC, MC, SC]))
    p.append(text(400, cy + 40, "L M S (не перекриті)", size=9, color=MUTED))

    p.append(arrow(444, cy, 496, cy, color=POS, sw=2.2))
    stage(548, cy, "× D", "діагональ тут", fill="#f0f9f4", stroke=FIELD, w=92)
    p.append(text(548, cy - 38, "фон Кріс: 3 числа", size=8, color=MUTED))

    p.append(arrow(594, cy, 646, cy, color=NEG, sw=2.2))
    stage(700, cy, "M⁻¹", "назад у RGB", fill="#eef2fb", stroke=NEG, w=92)

    p.append(arrow(746, cy, 800, cy, color=INK, sw=2.0))
    p.extend(_chip3(838, cy, [150, 150, 150], [RC, GC, BC]))

    p.append(fitbox(46, 358, W - 92, 56,
                    "Разом M⁻¹ · D · M — повна матриця 3×3 за формою, але вся залежність від лампи сидить у "
                    "трьох числах діагоналі D. Стала пара M / M⁻¹ (лише сенсор) розводить чутливості так, щоб "
                    "не перекривалися, — і діагональ фон Кріса знову точна.",
                    size=11, pad=10, fill="#f7f4fb", stroke="#8a4fd6", sw=1.4))

    render(os.path.join(OUT, "cat-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_narrow_vs_broad()
    fig_cat_pipeline()
    print("figs_vonkries: narrow-vs-broad.svg, cat-pipeline.svg")
