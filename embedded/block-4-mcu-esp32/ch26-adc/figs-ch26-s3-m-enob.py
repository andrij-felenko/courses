# -*- coding: utf-8 -*-
"""
Фігури для вставки 4.8.3m — «Скільки біт справжні: SNR, ENOB і виграш √N».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

fig-26-3m-1-averaging-bits.svg — виграш усереднення: приріст ENOB як ½·log₂N.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.3m.1 — виграш усереднення: приріст ENOB як ½·log₂N
# ═══════════════════════════════════════════════════════════════════════════════
def fig_averaging_bits():
    W, H = 680, 400

    # ── Область графіка ──
    LX, RX = 80, 580
    BY, TY = 340, 50
    GW = RX - LX   # 500
    GH = BY - TY   # 290

    # Значення по X (N) — логарифмічна шкала з основою 4
    N_vals = [1, 4, 16, 64, 256]
    # ENOB gain = ½·log₂N = log₂(√N)
    enob_gain = [0.5 * math.log2(n) for n in N_vals]  # [0, 1, 2, 3, 4]
    db_gain   = [10 * math.log10(n) for n in N_vals]   # [0, 6.02, 12.04, 18.06, 24.08]

    # Позиція по X: рівномірно (кроки log₄N = 0,1,2,3,4)
    def gx(n):
        if n <= 0:
            return LX
        lv = math.log(n, 4)  # 0..4
        return LX + lv / 4.0 * GW

    # Позиція по Y (ENOB gain 0..4)
    def gy_enob(eg):
        return BY - eg / 4.0 * GH

    frags = []

    # ── Фон графіка ──
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#f8f9fa" stroke="%s" stroke-width="1.2" rx="4"/>'
                 % (LX, TY, GW, GH, MUTED))

    # ── Горизонтальні лінії сітки (ENOB 0..4) ──
    for eg in range(5):
        yg = gy_enob(eg)
        frags.append(line(LX, yg, RX, yg, color=MUTED, sw=0.8, dash="4 3"))
        # Ліва вісь: біти
        frags.append(text(LX - 10, yg + 5, "+%d біт" % eg, size=11,
                          color=INK, anchor="end"))
        # Права вісь: дБ
        db_label = "+%.0f дБ" % db_gain[eg] if eg < len(db_gain) else ""
        # знайдемо відповідне значення
        # eg = 0->0 дБ, 1->6, 2->12, 3->18, 4->24
        db_approx = eg * 6.02
        frags.append(text(RX + 10, yg + 5, "+%.0f дБ" % db_approx,
                          size=11, color=NEG, anchor="start"))

    # ── Вертикальні лінії (N: 1,4,16,64,256) ──
    for n in N_vals:
        xg = gx(n)
        frags.append(line(xg, TY, xg, BY, color=MUTED, sw=0.8, dash="4 3"))
        frags.append(text(xg, BY + 18, "N=%d" % n, size=11, color=INK, anchor="middle"))

    # ── Крива ½·log₂N — гладка (через проміжні точки) ──
    curve_pts = []
    n_steps = 200
    for i in range(n_steps + 1):
        # N від 1 до 256 в логарифмічній шкалі
        t = i / n_steps  # 0..1
        lv = t * 4.0     # log₄(N): 0..4
        n  = 4.0 ** lv   # 1..256
        eg = 0.5 * math.log2(max(n, 1.0))
        curve_pts.append((gx(n), gy_enob(eg)))

    poly = " ".join("%.1f,%.1f" % p for p in curve_pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" '
                 'stroke-width="2.8"/>' % (poly, FIELD))

    # ── Ключові точки (кружки) з підписами ──
    annotations = [
        (1,   0,   "N=1\n0 біт"),
        (4,   1,   "N=4\n+1 біт"),
        (16,  2,   "N=16\n+2 біти"),
        (64,  3,   "N=64\n+3 біти"),
        (256, 4,   "N=256\n+4 біти"),
    ]
    for n, eg, label in annotations:
        xp = gx(n)
        yp = gy_enob(eg)
        frags.append(circle(xp, yp, 6, fill=FIELD, stroke=FIELD, sw=2))
        frags.append(circle(xp, yp, 3, fill=BG, stroke=FIELD, sw=1.5))

    # Підписи праворуч від точок (або зі зсувом)
    label_offsets = [(-45, -22), (12, -22), (12, -22), (12, -22), (-62, -22)]
    for (n, eg, label), (dx, dy) in zip(annotations, label_offsets):
        xp = gx(n)
        yp = gy_enob(eg)
        tb, _, _ = textbox(xp + dx + 30, yp + dy, label, size=10,
                           fill="#eef6ef", stroke=FIELD, pad=5)
        frags.append(tb)

    # ── Стрілки «×4 → +1 біт» між кроками ──
    arrow_color = "#8b5e3c"
    for i in range(len(N_vals) - 1):
        n0, n1 = N_vals[i], N_vals[i + 1]
        x0, x1 = gx(n0), gx(n1)
        ym = gy_enob(i + 0.5)  # між двома рівнями
        # горизонтальна стрілка внизу
        y_arr = BY + 34
        frags.append(arrow(x0 + 4, y_arr, x1 - 4, y_arr, color=arrow_color, sw=1.4))
        frags.append(text((x0 + x1) / 2, y_arr - 4, "×4", size=10,
                          color=arrow_color, anchor="middle"))

    # ── Осі ──
    frags.append(arrow(LX, BY, LX, TY - 10, color=INK, sw=1.6))
    frags.append(arrow(LX, BY, RX + 15, BY, color=INK, sw=1.6))

    # ── Заголовок осей ──
    frags.append(text(LX - 14, TY - 16, "+ENOB, біт", size=12,
                      color=INK, anchor="middle"))
    frags.append(text(RX + 50, TY - 16, "+SNR, дБ", size=12,
                      color=NEG, anchor="middle"))

    # ── Підпис осі X ──
    frags.append(text((LX + RX) / 2, BY + 56, "N — кількість усереднених відліків",
                      size=12, color=MUTED, anchor="middle"))

    # ── Формула в рамці ──
    tb_formula, _, _ = textbox(440, 110,
                                "ΔENOB = ½·log₂N\nΔSNR = 10·log₁₀N дБ",
                                size=12, fill="#eef6ef", stroke=FIELD, pad=10, bold=False)
    frags.append(tb_formula)

    # ── Легенда-коментар ──
    tb_hint, _, _ = textbox(220, 185,
                             "Кожне ×4 відліків\n= +1 чесний біт",
                             size=11, fill="#fff8e1", stroke="#c8922a", pad=8)
    frags.append(tb_hint)

    # ── Підпис рисунка ──
    frags.append(text(W // 2, H - 12,
                      "Рис. 4.8.3m.1. Виграш усереднення: кожне ×4 відліків додає рівно +1 ефективний біт; крива насичується — 256 відліків дають лише +4 біти",
                      size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-3m-1-averaging-bits.svg"), W, H, *frags,
           title="Виграш від усереднення: ½·log₂N біт, або +6 дБ на ×4 відліків")


if __name__ == "__main__":
    fig_averaging_bits()
    print("fig-26-3m-1-averaging-bits.svg — OK")
