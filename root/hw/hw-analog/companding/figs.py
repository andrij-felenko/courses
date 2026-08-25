# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── companding-curve: криві компресора μ-law та A-law проти лінії ─────────────
# Ідея: показати, ЧОМУ логарифмічний закон дає малим сигналам більше кодів.
# Діагональ — лінійне кодування (рівні коди на весь діапазон). Крива μ-law круто
# йде вгору при малому вході: тиха ділянка входу [0..0.1] розтягується мало не на
# пів-виходу — туди й лягає більшість із 256 кодів. A-law поруч, лише з прямою
# ланкою біля нуля. Головне на око: де крива крута, там густо кодів; де полога — рідко.

def fig_companding_curve():
    import math
    W, H = 720, 430
    p = []
    # квадрат осей (вхід x у [0..1] по горизонталі, вихід y у [0..1] вгору)
    ox, oy = 110, 360         # початок координат (лівий низ)
    sq = 300                  # сторона квадрата
    p.append(rect(ox, oy - sq, sq, sq, fill="#fbfcfd", stroke=MUTED, sw=1.0))
    p.append(arrow(ox, oy, ox + sq + 26, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - sq - 26, color=INK, sw=1.6))
    p.append(text(ox + sq / 2, oy + 34, "вхід  |x|  (частка від повної шкали)  →", size=11, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'вихід  y  (номер коду)  →</text>' % (ox - 40, oy - sq / 2, FONT, INK, ox - 40, oy - sq / 2))

    def PX(x): return ox + sq * x
    def PY(y): return oy - sq * y

    # діагональ — лінійне кодування
    p.append(line(PX(0), PY(0), PX(1), PY(1), color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(PX(0.82), PY(0.82) + 16, "лінійне", size=10, color=MUTED, italic=True, anchor="start"))

    # крива μ-law: y = ln(1+μx)/ln(1+μ)
    mu = 255.0
    pts = []
    n = 120
    for i in range(n + 1):
        x = i / n
        y = math.log(1 + mu * x) / math.log(1 + mu)
        pts.append("%.1f,%.1f" % (PX(x), PY(y)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
    p.append(text(PX(0.42), PY(0.90), "μ-law  (μ = 255)", size=11, color=POS, bold=True, anchor="middle"))

    # крива A-law: A|x|/(1+lnA) при x<1/A; (1+ln(Ax))/(1+lnA) далі
    A = 87.6
    lnA = math.log(A)
    pts = []
    for i in range(n + 1):
        x = i / n
        if x < 1.0 / A:
            y = A * x / (1 + lnA)
        else:
            y = (1 + math.log(A * x)) / (1 + lnA)
        pts.append("%.1f,%.1f" % (PX(x), PY(y)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="2 3"/>' % (" ".join(pts), NEG))
    p.append(text(PX(0.55), PY(0.66), "A-law  (A = 87.6)", size=11, color=NEG, bold=True, anchor="middle"))

    # виділити: тиха ділянка входу [0..0.1] → великий шмат виходу
    xq = 0.1
    yq = math.log(1 + mu * xq) / math.log(1 + mu)
    p.append(line(PX(xq), oy, PX(xq), PY(yq), color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(ox, PY(yq), PX(xq), PY(yq), color=FIELD, sw=1.2, dash="3 3"))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
             % (PX(0), PY(yq), PX(xq) - PX(0), oy - PY(yq), FIELD))
    p.append(text(PX(xq) + 8, PY(yq) - 6, "тихі 10 % входу…", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(PX(xq) + 8, PY(yq) + 10, "…займають ≈ " + str(round(yq * 100)) + " % кодів", size=10, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "де крива крута (тихий вхід) — туди лягає більшість кодів; де полога (гучний вхід) — кодів мало",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "companding-curve.svg"), W, H, *p,
           title="Крива компресора: μ-law та A-law проти лінійного кодування")


# ── companding-segments: 8 хорд μ-law і геометричні сходинки квантування ──────
# Ідея: реальний кодек не бере ln у залізі, а наближає криву ВІСЬМА прямими
# хордами (сегментами) на кожну полярність. Кожен наступний сегмент удвічі ширший
# за попередній по входу, але несе ту саму кількість кодів (16) — тож крок
# квантування подвоюється щосегмента. Це геометрична (експоненційна) драбина.
# Показуємо ширини сегментів стовпчиками, що подвоюються, і крок, що росте вдвічі.

def fig_companding_segments():
    import math
    W, H = 740, 400
    p = []
    ox, oy = 90, 300          # початок осей
    axw = 560                 # ширина осі входу
    # 8 сегментів: ширини по входу 1,1,2,4,8,16,32,64 (перші два рівні — біля нуля)
    widths = [1, 1, 2, 4, 8, 16, 32, 64]
    total = float(sum(widths))    # = 128 (14-бітна півшкала μ-law: 2^13 = 8192, тут у «щаблях»)
    p.append(arrow(ox, oy, ox + axw + 24, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - 250, color=INK, sw=1.6))
    p.append(text(ox + axw / 2, oy + 52, "вхід (лінійна амплітуда) — межі 8 сегментів →", size=11, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'крок квантування Δ (лог-шкала) →</text>' % (ox - 42, oy - 120, FONT, INK, ox - 42, oy - 120))

    # кольори від тихого (зелений) до гучного (червоний)
    cols = ["#1f8f4d", "#3f9a3a", "#7a9e2a", "#a8912a", "#c07f2a", "#c56a26", "#c34f24", "#b83320"]
    x = ox
    step_h0 = 22              # висота стовпчика кроку для сегмента 0
    for i, w in enumerate(widths):
        seg_w = axw * w / total
        # висота ∝ log2(крок): крок подвоюється щосегмента → лінійний приріст висоти
        bh = step_h0 * (i + 1) * 0.9
        p.append(rect(x, oy - bh, seg_w, bh, fill=cols[i], stroke=INK, sw=1.0, rx=2))
        # номер сегмента над стовпчиком
        p.append(text(x + seg_w / 2, oy - bh - 8, "S%d" % i, size=10, color=INK, bold=True))
        # ширина сегмента під віссю
        p.append(line(x, oy, x, oy + 6, color=MUTED, sw=1.0))
        x += seg_w
    p.append(line(x, oy, x, oy + 6, color=MUTED, sw=1.0))

    # підписи-виноски: кожен сегмент = 16 кодів, крок ×2
    p.append(fitbox(ox + 8, oy - 244, 214, 46,
                    "кожен сегмент = 16 рівних кодів\nширина сегмента ×2 щоразу\n⇒ крок квантування Δ ×2",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.4))
    p.append(text(ox + axw * 0.06, oy + 26, "тихо: дрібний крок, густо кодів", size=10, color="#1f8f4d", anchor="start"))
    p.append(text(ox + axw * 0.62, oy + 26, "гучно: крупний крок, рідко кодів", size=10, color="#b83320", anchor="start"))

    p.append(text(W / 2, H - 14,
                  "геометрична, тобто експоненційна, драбина кроків: рівні кроки на слух — це подвоєння на шкалі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "companding-segments.svg"), W, H, *p,
           title="Вісім хорд μ-law: геометричні сходинки квантування")


if __name__ == "__main__":
    fig_companding_curve()
    fig_companding_segments()
    print("OK: figures written to", OUT)
