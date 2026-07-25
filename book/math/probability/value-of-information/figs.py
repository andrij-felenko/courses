# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_TINT = "#eaf7ef"
RED_TINT   = "#fdecea"


# ── примітиви для дерева рішень ──────────────────────────────────────────────
def _sq(cx, cy, s=18, fill=FILL, stroke=INK):
    """Квадрат — вузол рішення."""
    return rect(cx - s / 2, cy - s / 2, s, s, fill=fill, stroke=stroke, sw=2, rx=0)


def _ch(cx, cy, r=16, fill="#eef2f7", stroke=INK):
    """Коло — вузол випадку."""
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=2)


# ── 1. Дерево рішень: EVPI (цінність ідеальної інформації) ────────────────────
def fig_voi_tree():
    W, H = 940, 620
    p = []

    # розділювач між двома деревами
    p.append(line(500, 96, 500, 500, color=MUTED, sw=1, dash="4,6"))
    p.append(text(250, 68, "Без перевірки — діємо на пріор", size=14.5, bold=True))
    p.append(text(720, 68, "З ясновидінням — правда наперед", size=14.5, bold=True))

    # ── ліве дерево (без інформації) ─────────────────────────────
    D1 = (95, 300)
    C1 = (285, 205)
    p.append(_sq(*D1))
    p.append(_ch(*C1))

    l0, _, _ = textbox(455, 150, "0", size=14, min_w=54, fill=GREEN_TINT, stroke=FIELD)
    l120, _, _ = textbox(455, 262, "120", size=14, min_w=54, fill=RED_TINT, stroke=POS)
    lb, _, _ = textbox(300, 442, "40", size=14, min_w=54, fill=FILL)
    p += [l0, l120, lb]

    # ребра
    p.append(line(D1[0] + 11, D1[1] - 9, C1[0] - 15, C1[1] + 9))     # D1 → C1 (купити)
    p.append(line(D1[0] + 9, D1[1] + 11, 273, 426))                 # D1 → будувати-leaf
    p.append(line(C1[0] + 14, C1[1] - 6, 428, 154))                # C1 → 0
    p.append(line(C1[0] + 14, C1[1] + 7, 428, 258))                # C1 → 120

    # підписи ребер (осторонь ліній)
    p.append(text(168, 232, "купити", size=12.5, color=MUTED))
    p.append(text(150, 392, "будувати", size=12.5, color=MUTED))
    p.append(text(360, 146, "тримає · 0.70", size=12, color=MUTED))
    p.append(text(378, 292, "падає · 0.30", size=12, color=MUTED))

    # згортки
    p.append(text(285, 176, "36", size=14, bold=True, color=POS))       # E у C1
    p.append(text(96, 348, "→ 36", size=12.5, color=INK))               # вибір у D1

    # ── праве дерево (ясновидіння) ───────────────────────────────
    C2 = (600, 232)
    p.append(_ch(*C2))
    r0, _, _ = textbox(800, 165, "0", size=14, min_w=54, fill=GREEN_TINT, stroke=FIELD)
    r40, _, _ = textbox(800, 322, "40", size=14, min_w=54, fill=FILL)
    p += [r0, r40]
    p.append(line(C2[0] + 14, C2[1] - 7, 772, 171))
    p.append(line(C2[0] + 14, C2[1] + 8, 772, 316))
    p.append(text(688, 176, "0.70 · купити", size=11.5, color=MUTED))
    p.append(text(700, 308, "0.30 · будувати", size=11.5, color=MUTED))
    p.append(text(600, 202, "12", size=14, bold=True, color=FIELD))     # E у C2

    # банер EVPI
    banner, _, _ = textbox(320, 556,
                           "EVPI = 36 − 12 = 24 люд-дні  ·  стеля ціни перевірки",
                           size=13.5, fill=GREEN_TINT, stroke=FIELD)
    p.append(banner)

    return render(os.path.join(OUT, 'voi-decision-tree.svg'), W, H, *p,
                  title="Дерево рішень: цінність ідеальної інформації (EVPI)")


# ── 2. Крива VoI(p): де перевірка цінна, а де марна ──────────────────────────
def fig_voi_curve():
    W, H = 780, 500
    p = []
    gx, gy, gw, gh = 120, 92, 560, 300
    base = gy + gh          # y осі X (VoI = 0)
    vmax = 30.0

    def X(pp):
        return gx + pp * gw

    def Y(v):
        return base - (v / vmax) * gh

    # осі
    p.append(arrow(gx, base, gx + gw + 18, base, color=MUTED))
    p.append(arrow(gx, base, gx, gy - 18, color=MUTED))
    p.append(text(gx + gw / 2, base + 42, "P(припущення хибне) →", size=13))
    p.append(mtext(48, gy + 46, ["цінність", "інфор-", "мації ↑"], size=12))

    # намет VoI(p): (0,0)–(1/3, 26.7)–(1,0)
    pk = 1.0 / 3.0
    vpk = 80 * pk           # 26.67
    p.append(line(X(0), Y(0), X(pk), Y(vpk), color=POS, sw=2.5))
    p.append(line(X(pk), Y(vpk), X(1), Y(0), color=POS, sw=2.5))

    # вертикаль байдужості
    p.append(line(X(pk), Y(vpk), X(pk), base, color=MUTED, sw=1, dash="4,6"))
    p.append(text(X(pk), base + 22, "p* = 1/3", size=12, color=MUTED))

    # наша точка p = 0.30 → 24
    p.append(circle(X(0.30), Y(24), 5, fill=INK, stroke=INK))
    p.append(text(X(0.30) - 12, Y(24) - 12, "наш кейс: 24", size=12, bold=True, anchor="end"))

    # пік і зони дій
    p.append(text(X(pk) + 4, Y(vpk) - 16, "пік — рішення на вістрі", size=12, bold=True, anchor="start"))
    p.append(text(X(0.15), Y(5.5), "обираємо: купити", size=11, color=MUTED))
    p.append(text(X(0.63), Y(5.5), "обираємо: будувати", size=11, color=MUTED))

    return render(os.path.join(OUT, 'voi-curve.svg'), W, H, *p,
                  title="Цінність інформації як функція непевності")


if __name__ == "__main__":
    fig_voi_tree()
    fig_voi_curve()
    print("ok")
