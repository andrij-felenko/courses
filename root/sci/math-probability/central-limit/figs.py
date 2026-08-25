# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def binom(n, k):
    """Біноміальний коефіцієнт C(n,k) — число способів дати k плюсів із n."""
    return math.comb(n, k)


# ── Фігура: збіжність суми незалежних доданків до дзвону ──────────────────────
# Той самий доданок ±1 (чесна монета) у сумі при N=1,2,4,8. Висоти стовпчиків —
# біноміальні коефіцієнти (число комбінацій, що дають дану суму). Від двох рівних
# стовпчиків монети крок за кроком виростає гаусів купол.
# Ідея, яку важко передати словами: дзвін постає НЕ з форми доданка, а з того, що
# комбінацій потрапити в середину незрівнянно більше, ніж на край. Накладена
# гаусова крива показує, до чого все стягується.
def fig_convergence():
    W, H = 660, 500
    panels = [1, 2, 4, 8]                 # значення N для чотирьох панелей
    cols = 2
    pw, ph = 300, 168                     # розмір однієї панелі
    gx0, gy0 = 30, 52                     # лівий-верхній кут сітки панелей
    gap_x, gap_y = 20, 26

    p = []

    def panel(N, px, py):
        out = []
        # рамка панелі
        out.append(rect(px, py, pw, ph, fill=BG, stroke=MUTED, sw=1.1, rx=8))
        title = "N = %d" % N
        out.append(text(px + 12, py + 20, title, 13, INK, "start", bold=True))

        # дані: висоти = біноміальні коефіцієнти C(N,k), k=0..N; нормуємо на пік
        weights = [binom(N, k) for k in range(N + 1)]
        wmax = max(weights)
        nbars = N + 1

        base_y = py + ph - 26          # рівень осі
        top_y = py + 36                # стеля стовпчиків
        plot_h = base_y - top_y
        # поле для стовпчиків
        left = px + 30
        right = px + pw - 18
        span = right - left
        # ширина й крок стовпчиків
        bw = min(34, span / nbars * 0.66)
        step = span / nbars

        def bar_cx(i):
            return left + step * (i + 0.5)

        # вісь
        out.append(line(left - 8, base_y, right + 4, base_y, color=MUTED, sw=1.1))

        # стовпчики
        for i, w in enumerate(weights):
            h = plot_h * (w / wmax)
            cx = bar_cx(i)
            out.append(rect(cx - bw / 2, base_y - h, bw, h,
                            fill="#eaf0fd", stroke=NEG, sw=1.3, rx=2))

        # накладена гаусова крива (центр посередині, σ у "стовпчиках" = √N/2·одиниця кроку)
        # сума ±1: значення k плюсів ↦ позиція i; центр у i=N/2, σ_дискр = √N/2 кроків
        mu_i = N / 2.0
        sigma_i = math.sqrt(N) / 2.0
        if sigma_i < 1e-6:
            sigma_i = 0.5
        curve = []
        t = -0.4
        while t <= N + 0.4001:
            z = (t - mu_i) / sigma_i
            g = math.exp(-0.5 * z * z)           # нормована на пік=1
            cx = bar_cx(t)
            cy = base_y - plot_h * g
            curve.append("%.1f,%.1f" % (cx, cy))
            t += 0.08
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                   % (" ".join(curve), FIELD))
        return out

    for idx, N in enumerate(panels):
        r, c = idx // cols, idx % cols
        px = gx0 + c * (pw + gap_x)
        py = gy0 + r * (ph + gap_y)
        p += panel(N, px, py)

    # легенда під сіткою
    ly = gy0 + 2 * ph + gap_y + 28
    lx = W / 2 - 150
    p.append(rect(lx, ly - 9, 16, 11, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    p.append(text(lx + 22, ly, "число комбінацій (сума ±1)", 11, INK, "start"))
    p.append(line(lx + 196, ly - 4, lx + 224, ly - 4, color=FIELD, sw=2.2))
    p.append(text(lx + 230, ly, "гаусів дзвін", 11, FIELD, "start"))

    p.append(text(W / 2, H - 12,
                  "Той самий доданок у сумі: з ростом N форма стирається, проступає той самий дзвін.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "convergence.svg"), W, H, *p,
           title="Сума незалежних доданків сходиться до дзвону")


if __name__ == "__main__":
    fig_convergence()
    print("Done.")
