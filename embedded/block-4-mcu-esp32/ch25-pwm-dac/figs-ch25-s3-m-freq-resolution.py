# -*- coding: utf-8 -*-
"""
Фігура для вставки 🧮 «Частота × роздільність = константа» (до теми 4.7.3).
fig-25-3m-1-inverse-law.svg  → Рис. 4.7.3m.1

Імпортує спільний kit; примітиви з svgkit — НЕ переписуються тут.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

CLOCK = 80_000_000  # 80 МГц — бюджет тіків/с

# Робочі точки: (частота Гц, роздільність у бітах, N тіків)
POINTS = [
    (1_000,   16, CLOCK // 1_000),     # 1 кГц / 16 біт / N=80000
    (5_000,   13, CLOCK // 5_000),     # 5 кГц / 13 біт / N=16000
    (25_000,  11, CLOCK // 25_000),    # 25 кГц / ~11 біт / N=3200
    (100_000,  9, CLOCK // 100_000),   # 100 кГц / 9 біт / N=800
    (1_000_000, 6, CLOCK // 1_000_000),# 1 МГц / 6 біт / N=80
]


def fig_inverse_law():
    W, H = 900, 520
    path = os.path.join(OUT, "fig-25-3m-1-inverse-law.svg")

    # ── область графіка ──────────────────────────────────────────────────────
    LM, RM, TM, BM = 80, 40, 50, 70
    GW = W - LM - RM   # 780
    GH = H - TM - BM   # 400

    # логарифмічна шкала: X = частота 1кГц…1МГц, Y = N тіків 60…100000
    F_MIN, F_MAX = 800, 1_300_000
    N_MIN, N_MAX = 60, 110_000

    def lx(f):
        return LM + (math.log10(f) - math.log10(F_MIN)) / (math.log10(F_MAX) - math.log10(F_MIN)) * GW

    def ly(n):
        return TM + GH - (math.log10(n) - math.log10(N_MIN)) / (math.log10(N_MAX) - math.log10(N_MIN)) * GH

    # ── SVG: header ──────────────────────────────────────────────────────────
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}">'
        f'<rect width="{W}" height="{H}" fill="{BG}"/>'
    )

    # ── фон зони графіка ─────────────────────────────────────────────────────
    parts.append(rect(LM, TM, GW, GH, fill="#f9fafb", stroke=LINE, sw=1, rx=0))

    # ── сітка X (частоти: 1к, 5к, 10к, 50к, 100к, 500к, 1М) ────────────────
    x_ticks = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000]
    x_labels = ["1 кГц", "5 кГц", "10 кГц", "50 кГц", "100 кГц", "500 кГц", "1 МГц"]
    for f, lbl in zip(x_ticks, x_labels):
        xp = lx(f)
        parts.append(line(xp, TM, xp, TM + GH, color=MUTED, sw=0.6, dash="4 3"))
        parts.append(text(xp, TM + GH + 18, lbl, size=11, color=MUTED, anchor="middle"))

    # ── сітка Y (тіки: 80, 200, 500, 1к, 2к, 5к, 10к, 20к, 50к, 80к) ───────
    y_ticks = [80, 200, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 80_000]
    y_labels = ["80", "200", "500", "1к", "2к", "5к", "10к", "20к", "50к", "80к"]
    for n, lbl in zip(y_ticks, y_labels):
        yp = ly(n)
        parts.append(line(LM, yp, LM + GW, yp, color=MUTED, sw=0.6, dash="4 3"))
        parts.append(text(LM - 7, yp + 4, lbl, size=11, color=MUTED, anchor="end"))

    # ── гіпербола f·N = 80e6 ─────────────────────────────────────────────────
    # У лог-лог осях це пряма (нахил −1). Малюємо як polyline по точках.
    curve_pts = []
    log_f_min = math.log10(F_MIN)
    log_f_max = math.log10(F_MAX)
    steps = 200
    for i in range(steps + 1):
        log_f = log_f_min + (log_f_max - log_f_min) * i / steps
        f = 10 ** log_f
        n = CLOCK / f
        if N_MIN * 0.8 <= n <= N_MAX * 1.2:
            curve_pts.append((lx(f), ly(n)))

    if curve_pts:
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in curve_pts)
        parts.append(
            f'<polyline points="{pts_str}" fill="none" stroke="{NEG}" '
            f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-dasharray="6 3"/>'
        )

    # ── підпис константи на кривій ───────────────────────────────────────────
    # Ставимо десь у середині кривої
    f_mid = 12_000
    n_mid = CLOCK / f_mid
    xm, ym = lx(f_mid), ly(n_mid)
    # поворот тексту — у лог-лог пряма з нахилом −45°
    # Щоб не ускладнювати — ставимо textbox поряд із кривою
    tb, tw, th = textbox(xm + 90, ym - 40,
                          "площа = такт\n= 80·10⁶ тіків/с",
                          size=12, fill="#eef6ef", stroke=FIELD, pad=8)
    parts.append(tb)
    # лінія від рамки до кривої
    parts.append(line(xm + 90 - tw / 2 - 2, ym - 40, xm + 8, ym - 2,
                       color=FIELD, sw=1, dash="3 2"))

    # ── робочі точки ─────────────────────────────────────────────────────────
    POINT_COLORS = [POS, NEG, FIELD, "#9b59b6", "#e67e22"]

    for i, (f, bits, n_exact) in enumerate(POINTS):
        xp = lx(f)
        yp = ly(n_exact)
        col = POINT_COLORS[i % len(POINT_COLORS)]

        # кружок точки
        parts.append(circle(xp, yp, 6, fill=col, stroke=col, sw=1.5))

        # підпис точки: частота / N біт
        f_lbl = {1_000: "1 кГц", 5_000: "5 кГц", 25_000: "25 кГц",
                 100_000: "100 кГц", 1_000_000: "1 МГц"}[f]
        label = f"{f_lbl} / {bits} біт"

        # розміщення підпису (щоб не перекривалися)
        offsets = [
            (+10, -20),   # 1 кГц
            (+10, -20),   # 5 кГц
            (+10, +22),   # 25 кГц
            (-10, +22),   # 100 кГц
            (-10, -20),   # 1 МГц
        ]
        ox, oy = offsets[i]
        anch = "start" if ox > 0 else "end"

        tb2, _, _ = textbox(xp + ox + (50 if ox > 0 else -50),
                             yp + oy,
                             label, size=11,
                             fill=BG, stroke=col, sw=1.2, pad=6)
        parts.append(tb2)
        parts.append(line(xp, yp, xp + ox // 2, yp + oy // 2,
                           color=col, sw=0.8))

    # ── осі ──────────────────────────────────────────────────────────────────
    # вісь X
    parts.append(
        f'<line x1="{LM:.1f}" y1="{TM+GH:.1f}" x2="{LM+GW:.1f}" y2="{TM+GH:.1f}" '
        f'stroke="{LINE}" stroke-width="1.8" marker-end="url(#arr)"/>'
    )
    # вісь Y
    parts.append(
        f'<line x1="{LM:.1f}" y1="{TM+GH:.1f}" x2="{LM:.1f}" y2="{TM:.1f}" '
        f'stroke="{LINE}" stroke-width="1.8" marker-end="url(#arr)"/>'
    )

    # підписи осей
    parts.append(text(LM + GW // 2, H - 10,
                       "Частота f (лог. шкала)", size=13, color=INK, anchor="middle"))
    # вертикальний підпис — через transform
    parts.append(
        f'<text transform="rotate(-90,{LM-52},{TM+GH//2})" '
        f'x="{LM-52:.1f}" y="{TM+GH//2:.1f}" '
        f'font-family="{FONT}" font-size="13" fill="{INK}" text-anchor="middle">'
        f'N — тіків у періоді (лог. шкала)</text>'
    )

    # ── заголовок ────────────────────────────────────────────────────────────
    parts.append(text(W // 2, 30, "Закон збереження: f · N = такт = const",
                       size=16, color=INK, anchor="middle", bold=True))
    parts.append(text(W // 2, 48, "У лог-лог осях гіпербола — пряма з нахилом −1; "
                       "кожне подвоєння f зсуває точку рівно на 1 біт униз",
                       size=12, color=MUTED, anchor="middle"))

    # ── defs для стрілок ─────────────────────────────────────────────────────
    # Вставляємо в самий початок (між <svg> і першим rectом)
    defs = (
        '<defs>'
        '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="{c}"/>'
        '</marker>'
        '</defs>'
    ).format(c=LINE)

    # Зберігаємо: вставляємо defs після тегу <svg>
    svg_body = "\n".join(parts)
    # замінити першу позицію після <svg ...>
    svg_final = svg_body.replace(
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        defs + f'\n<rect width="{W}" height="{H}" fill="{BG}"/>',
        1
    )
    svg_final += "\n</svg>"

    import io
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(svg_final)
    print(f"Written: {path}")
    return path


if __name__ == "__main__":
    fig_inverse_law()
    print("Done.")
