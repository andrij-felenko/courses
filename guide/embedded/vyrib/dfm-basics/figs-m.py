# -*- coding: utf-8 -*-
# Фігури ВСТАВКИ math-tombstone-balance.md. Не чіпає базові/детальні SVG.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура M1: теплова RC-ланка як електричне коло ──────────────────────────
# Дві паралельні гілки Rθ·C, спільне джерело «печі»; показує, звідки τ і чому
# гілка з великим C відстає. Усі написи — ПРАВОРУЧ від проводу (провід не ріже текст).
def fig_rc_model():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Площадка = RC-ланка: піч жене тепло крізь опір у теплоємність", size=16, bold=True))

    # ── шина «печі» (джерело сталої T) ──
    railx = 70
    f.append(line(railx, 96, railx, 410, color=POS, sw=3))
    f.append(text(railx - 6, 84, "піч", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(railx - 6, 102, "T_піч", size=12, color=POS, anchor="end"))

    # спільний вузол «маси плати» (земля)
    gndy = 430
    f.append(line(railx, gndy, 610, gndy, color=INK, sw=2))
    for gx in range(int(railx), 610, 22):
        f.append(line(gx, gndy, gx + 8, gndy + 8, color=INK, sw=1))
    f.append(text(316, gndy + 24, "спільна маса плати", size=11, color=MUTED))

    # ── одна гілка: Rθ (резистор) послідовно, C (конденсатор) до землі ──
    # Провід іде вертикально по x; УСІ підписи — праворуч, зі старт-якорем, поза проводом.
    def branch(x, label, sub, rlabel, clabel, col, tau_note):
        top = 120
        f.append(line(railx, top, x, top, color=INK, sw=1.6))     # від печі до резистора
        rh = 54
        f.append(rect(x - 24, top, 48, rh, fill="#fdecea", stroke=col, sw=2))
        f.append(text(x, top + rh / 2 + 5, rlabel, size=14, color=col, bold=True))
        f.append(text(x + 34, top + 16, "Rθ", size=12, color=MUTED, anchor="start"))
        # вузол площадки
        node = top + rh + 30
        f.append(line(x, top + rh, x, node, color=INK, sw=1.6))
        f.append(circle(x, node, 4, fill=INK, stroke=INK, sw=1))
        # підписи вузла — ПРАВОРУЧ від проводу (не на ньому)
        f.append(text(x + 16, node - 4, label, size=13, color=col, bold=True, anchor="start"))
        f.append(text(x + 16, node + 13, sub, size=11, color=MUTED, anchor="start"))
        # конденсатор C до землі
        capy = node + 44
        f.append(line(x, node, x, capy, color=INK, sw=1.6))
        f.append(line(x - 22, capy, x + 22, capy, color=col, sw=3))
        f.append(line(x - 22, capy + 9, x + 22, capy + 9, color=col, sw=3))
        f.append(text(x + 30, capy + 2, clabel, size=13, color=col, bold=True, anchor="start"))
        f.append(text(x + 30, capy + 18, "теплоємність", size=10, color=MUTED, anchor="start"))
        f.append(line(x, capy + 9, x, gndy, color=INK, sw=1.6))    # до землі
        # підпис τ — ліворуч від проводу (у власній рамці, поза проводом)
        b, bw, bh = textbox(x - 74, capy + 40, tau_note, size=11, pad=8,
                            fill="#fbfbfb", stroke=col, sw=1.4, color=INK)
        f.append(b)

    branch(190, "на доріжці", "мала маса міді",
           "мале", "C мала", NEG, "τ = Rθ·C мале\n→ гріється ШВИДКО")
    branch(470, "на заливці", "тягне полігон",
           "велике", "C велике", FIELD, "τ = Rθ·C велике\n→ гріється ПОВІЛЬНО")

    # рівняння балансу — окремою колонкою праворуч, поза схемою
    b, bw, bh = textbox(760, 200,
                        "баланс енергії вузла:\nC·dT/dt = (T_піч − T)/Rθ\n─────────────\nрозв’язок:\nT(t) = T_піч·(1 − e^(−t/τ))",
                        size=12, pad=12, fill="#eef6ff", stroke=NEG, sw=1.5, color=INK)
    f.append(b)

    render(os.path.join(OUT, 'rc-thermal-model.svg'), W, H, *f)


# ── Фігура M2: вільне тіло надгробка — меніск тягне, вага й клей тримають ────
def fig_free_body():
    import math as _m
    W, H = 900, 540
    f = []
    f.append(text(W / 2, 30, "Вільне тіло надгробка: що перекидає деталь і що її тримає", size=16, bold=True))

    # підсумкова нерівність — угорі, окремо
    b, bw, bh = textbox(W / 2, 68,
                        "перекине  ⟺   F·h   >   m·g·(L/2) + F_клей·(L/2)",
                        size=14, pad=10, fill="#fdf6ec", stroke=POS, sw=1.6, color=INK, bold=True)
    f.append(b)

    # плата
    boardY = 360
    f.append(rect(60, boardY, W - 120, 40, fill="#e8e2d0", stroke="#9a8f70", sw=1.5, rx=3))
    f.append(text(74, boardY + 25, "плата", size=11, color=MUTED, anchor="start"))

    # дві площадки (ліва — вісь/рідка; права — тверда, піднята)
    padL_x, padR_x, padw = 230, 470, 120
    f.append(rect(padL_x, boardY - 8, padw, 10, fill="#d9b06a", stroke="#8a5a1f", sw=1.4, rx=1))
    f.append(rect(padR_x, boardY - 8, padw, 10, fill="#d9b06a", stroke="#8a5a1f", sw=1.4, rx=1))

    pivot = (padL_x + padw * 0.5, boardY - 8)     # вісь обертання (припаяний кінець)
    Lpx = 232
    rad = _m.radians(-40)
    ex = pivot[0] + Lpx * _m.cos(rad)
    ey = pivot[1] + Lpx * _m.sin(rad)
    tw = 26
    nx, ny = -_m.sin(rad), _m.cos(rad)
    p1 = (pivot[0] + nx * tw / 2, pivot[1] + ny * tw / 2)
    p2 = (pivot[0] - nx * tw / 2, pivot[1] - ny * tw / 2)
    p3 = (ex - nx * tw / 2, ey - ny * tw / 2)
    p4 = (ex + nx * tw / 2, ey + ny * tw / 2)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#3a3f46" stroke="#1a1a1a" stroke-width="1.5"/>'
             % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1]))
    # підпис деталі — над корпусом з ВЕРХНЬОГО боку (−нормаль вгору-вліво), поза віссю й лінією ваги
    upx, upy = -nx, -ny   # верхня нормаль (від корпусу вгору-вліво)
    lx, ly = pivot[0] + Lpx * 0.34 * _m.cos(rad) + upx * 34, pivot[1] + Lpx * 0.34 * _m.sin(rad) + upy * 34
    f.append(text(lx, ly, "деталь 0402", size=12, color="#3a3f46", bold=True))

    # вісь обертання + підпис ЛІВОРУЧ угорі
    f.append(circle(pivot[0], pivot[1], 6, fill="#fff", stroke=POS, sw=2.5))
    f.append(text(pivot[0] - 12, pivot[1] - 30, "вісь обертання", size=11, color=POS, anchor="end"))
    f.append(text(pivot[0] - 12, pivot[1] - 15, "(припаяний кінець)", size=10, color=POS, anchor="end"))

    # меніск тягне вниз від осі — стрілка ТРОХИ ЛІВОРУЧ, підпис ще лівіше (поза стрілкою)
    max_ax = pivot[0] - 8
    f.append(arrow(max_ax, pivot[1] + 12, max_ax, pivot[1] + 78, color=POS, sw=2.6))
    f.append(text(max_ax - 12, pivot[1] + 40, "F ≈ γ·p", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(max_ax - 12, pivot[1] + 56, "меніск тягне", size=10, color=POS, anchor="end"))
    # плече h — власна рамка, нижче стрілки, поза нею
    b, bw, bh = textbox(max_ax - 4, pivot[1] + 104, "плече тяги = h\n(висота корпусу)",
                        size=10, pad=7, fill="#fff", stroke=MUTED, sw=1.1, color=MUTED)
    f.append(b)

    # вага в центрі мас — стрілка вниз, підпис ПРАВОРУЧ (поза стрілкою й корпусом)
    cmx, cmy = (pivot[0] + ex) / 2, (pivot[1] + ey) / 2
    f.append(circle(cmx, cmy, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(arrow(cmx, cmy + 4, cmx, cmy + 84, color=NEG, sw=2.6))
    f.append(text(cmx + 12, cmy + 58, "m·g", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(cmx + 12, cmy + 74, "вага (центр мас)", size=10, color=NEG, anchor="start"))
    # плече ваги L/2 — пунктир уздовж осі деталі; підпис КОЛО ОСІ (ліворуч від стрілки ваги)
    f.append(line(pivot[0], pivot[1], cmx, cmy, color=NEG, sw=1, dash="3,3"))
    f.append(text(pivot[0] + Lpx * 0.24 * _m.cos(rad) - 6, pivot[1] + Lpx * 0.24 * _m.sin(rad) - 8,
                  "плече L/2", size=10, color=NEG, anchor="end"))

    # права нога піднята — клей флюсу тримає (поки твердий)
    f.append(rect(padR_x + padw * 0.25, boardY - 20, 44, 12, fill="#cfe8d6", stroke=FIELD, sw=1.4, rx=2))
    f.append(arrow(padR_x + padw * 0.47, boardY + 44, padR_x + padw * 0.47, boardY - 6, color=FIELD, sw=2.2))
    f.append(text(padR_x + padw * 0.47, boardY + 62, "клейкість флюсу F_клей", size=10, color=FIELD))
    f.append(text(padR_x + padw * 0.47, boardY + 77, "тримає — але слабне з нагрівом", size=10, color=FIELD))

    # підписи станів площадок — низько під платою, кожен під своєю площадкою, поза стрілками
    f.append(text(padL_x + padw / 2, boardY + 132, "ЛІВА: припій РІДКИЙ", size=11, color=POS))
    f.append(text(padR_x + padw / 2 + 20, boardY + 132, "ПРАВА: припій ТВЕРДИЙ", size=11, color=NEG))

    render(os.path.join(OUT, 'tombstone-free-body.svg'), W, H, *f)


# ── Фігура M3: закон масштабу 1/k² — драбина 0402 → 0201 → 01005 ─────────────
def fig_scaling():
    W, H = 820, 470
    f = []
    f.append(text(W / 2, 30, "Закон масштабу: схильність до надгробка росте як 1/k²", size=16, bold=True))

    # три сходинки: (назва, k відносно 0402, відносна схильність = 1/k²)
    # 0402 → 0201: лінійний масштаб ≈ 0.5; 0201 → 01005 ще ≈ 0.5
    rows = [
        ("0402", 1.00, 1.0, "1.0 × 0.5 мм", NEG),
        ("0201", 0.50, 4.0, "0.6 × 0.3 мм", "#b8791f"),
        ("01005", 0.32, 9.8, "0.4 × 0.2 мм", POS),
    ]
    x0 = 120
    baseY = 400
    maxbar = 300
    colw = 200
    # шкала: висота стовпця ∝ схильності, нормуємо на 01005
    smax = rows[-1][2]
    for i, (name, k, tend, dims, col) in enumerate(rows):
        cx = x0 + i * colw
        bh = maxbar * (tend / smax)
        f.append(rect(cx - 42, baseY - bh, 84, bh, fill="#fdecea" if col == POS else "#eef2fb" if col == NEG else "#fbf1e0",
                      stroke=col, sw=2, rx=4))
        f.append(text(cx, baseY - bh - 12, "×%.1f" % tend, size=15, color=col, bold=True))
        f.append(text(cx, baseY + 24, name, size=15, color=INK, bold=True))
        f.append(text(cx, baseY + 42, dims, size=11, color=MUTED))
        f.append(text(cx, baseY + 60, "k = %.2f" % k, size=11, color=col))
    # базова лінія
    f.append(line(x0 - 60, baseY, x0 + 2 * colw + 60, baseY, color=INK, sw=2))
    f.append(text(x0 - 66, baseY + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 66, baseY - maxbar, "схильність\n(відносна)", size=11, color=MUTED, anchor="end")) if False else None

    # виведення масштабів збоку
    b, bw, bh = textbox(650, 200,
                        "момент тяги ∝ k²\n(сила ~k · плече ~k)\n\nмомент ваги ∝ k⁴\n(об’єм ~k³ · плече ~k)\n────────────\nвідношення ∝ 1/k²",
                        size=12, pad=10, fill="#f4f6f8", stroke=INK, sw=1.4, color=INK)
    f.append(b)

    render(os.path.join(OUT, 'tombstone-scaling.svg'), W, H, *f)


if __name__ == '__main__':
    fig_rc_model()
    fig_free_body()
    fig_scaling()
    print("ok")
