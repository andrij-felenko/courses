# -*- coding: utf-8 -*-
# Фігури вставки math-nand-reliability. Окремий файл, щоб не конфліктувати з
# паралельним редагуванням figs.py; вивід у той самий ./img/.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── різкий поріг t — сторінка гине, коли помилок > t ──────────────────────────
# Ідея: біноміальний дзвін числа помилок на сторінці (центр ≈ n·p) проти жорсткого
# порогу коду t. Усе праворуч від t — збій сторінки. Видно, чому важить хвіст, а
# не середнє.
def fig_error_threshold():
    W, H = 760, 440
    frags = []
    x0, y0 = 90, 340
    x1 = 700
    frags.append(line(x0, y0, x1, y0, color=INK, sw=2))          # вісь k
    frags.append(line(x0, y0, x0, 70, color=INK, sw=2))          # вісь P
    frags.append(text((x0 + x1) / 2, 372, "кількість перевернутих бітів на сторінці k", size=12, color=INK))
    frags.append('<text x="30" y="205" font-family="%s" font-size="12" fill="%s" text-anchor="middle" transform="rotate(-90 30 205)">P(рівно k помилок)</text>' % (FONT, INK))

    mean = 300.0   # px-зсув центру дзвону від x0
    sig = 46.0
    def bx(k):
        return x0 + k
    def bell(k, peak=205):
        return y0 - peak * math.exp(-((k - mean) ** 2) / (2 * sig * sig))

    pts = []
    for kk in range(0, x1 - x0, 4):
        pts.append("%.1f,%.1f" % (bx(kk), bell(kk)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), NEG))

    # заливка хвоста праворуч від t (= збій сторінки)
    tpx = mean + 120
    tail = ["%.1f,%.1f" % (bx(tpx), y0)]
    for kk in range(int(tpx), x1 - x0, 3):
        tail.append("%.1f,%.1f" % (bx(kk), bell(kk)))
    tail.append("%.1f,%.1f" % (bx(x1 - x0 - 2), y0))
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.30" stroke="none"/>' % (" ".join(tail), POS))

    # поріг t
    frags.append(line(bx(tpx), y0, bx(tpx), 96, color=POS, sw=2.6, dash="7,5"))
    frags.append(text(bx(tpx), 88, "поріг коду t", size=13, color=POS, bold=True))
    # середнє
    frags.append(line(bx(mean), y0, bx(mean), 124, color=MUTED, sw=1.6, dash="3,4"))
    frags.append(text(bx(mean), 116, "середнє ≈ n·p", size=11, color=MUTED))

    b1, _, _ = textbox(bx(mean) - 44, 300, "≤ t помилок:\nвиправляється\nнапевно", size=11,
                       fill="#eef0fd", stroke=NEG, color=NEG, bold=True)
    frags.append(b1)
    b2, _, _ = textbox(bx(tpx) + 96, 205, "> t помилок:\nсторінка несправна\n(цей хвіст = P збою)", size=11,
                       fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b2)

    frags.append(rect(60, 396, 640, 32, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=8))
    frags.append(text(380, 416, "важить не середнє, а хвіст за t:  P(збій) ≈ C(n, t+1)·p^(t+1)  — падає як p у степені (t+1)",
                      size=11, color=INK, bold=True))

    render(os.path.join(OUT, "error-threshold.svg"), W, H, *frags,
           title="Сторінка гине, коли помилок більше за t — важить хвіст біному, не середнє")


# ── BCH-водоспад проти м'якого LDPC ───────────────────────────────────────────
# Ідея: UBER від RBER. BCH тримає ціль, тоді зривається в різкий водоспад при
# своєму порозі; LDPC із м'якими рішеннями тримає ту саму ціль до ~5× більшого
# RBER. Показує, ЧОМУ TLC/QLC змусили перейти на LDPC.
def fig_bch_vs_ldpc():
    W, H = 760, 440
    frags = []
    x0, y0, x1, ytop = 95, 350, 690, 82
    frags.append(line(x0, y0, x1, y0, color=INK, sw=2))
    frags.append(line(x0, y0, x0, ytop, color=INK, sw=2))
    frags.append(text((x0 + x1) / 2, 384, "RBER — сира частота помилок (гірше →)", size=12, color=INK))
    frags.append('<text x="30" y="216" font-family="%s" font-size="12" fill="%s" text-anchor="middle" transform="rotate(-90 30 216)">UBER після корекції (нижче = краще)</text>' % (FONT, INK))

    for frac, lab in [(0.16, "10⁻⁴"), (0.42, "10⁻³"), (0.66, "5·10⁻³"), (0.90, "10⁻²")]:
        xx = x0 + (x1 - x0) * frac
        frags.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.4))
        frags.append(text(xx, y0 + 20, lab, size=10, color=MUTED))

    ytar = 158
    frags.append(line(x0, ytar, x1, ytar, color=FIELD, sw=2, dash="7,5"))
    frags.append(text(x1 - 4, ytar - 8, "ціль UBER = 10⁻¹⁵", size=11, color=FIELD, bold=True, anchor="end"))

    # BCH — водоспад біля 10⁻³
    bch_knee = x0 + (x1 - x0) * 0.42
    bch = []
    for i in range(0, 61):
        xx = x0 + i * ((bch_knee - x0) / 60)
        bch.append("%.1f,%.1f" % (xx, 324 - i * 0.18))
    bch.append("%.1f,%.1f" % (bch_knee + 6, ytar))
    bch.append("%.1f,%.1f" % (bch_knee + 15, ytop + 6))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(bch), POS))
    frags.append(text(bch_knee - 8, 306, "BCH", size=14, color=POS, bold=True, anchor="end"))
    b3, _, _ = textbox(bch_knee + 74, 128, "різкий водоспад:\nбіт понад t —\nслово втрачено", size=10,
                       fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b3)

    # LDPC — водоспад біля 5·10⁻³
    ldpc_knee = x0 + (x1 - x0) * 0.66
    ldpc = []
    for i in range(0, 61):
        xx = x0 + i * ((ldpc_knee - x0) / 60)
        ldpc.append("%.1f,%.1f" % (xx, 334 - i * 0.16))
    ldpc.append("%.1f,%.1f" % (ldpc_knee + 6, ytar))
    ldpc.append("%.1f,%.1f" % (ldpc_knee + 15, ytop + 6))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(ldpc), NEG))
    frags.append(text(ldpc_knee + 12, 322, "LDPC", size=14, color=NEG, bold=True, anchor="start"))
    b4, _, _ = textbox(ldpc_knee + 78, 300, "м'які рішення:\nкілька читань\nіз довірою", size=10,
                       fill="#eef0fd", stroke=NEG, color=NEG, bold=True)
    frags.append(b4)

    # стрілка виграшу вздовж цілі
    frags.append(arrow(bch_knee + 4, ytar - 24, ldpc_knee - 4, ytar - 24, color=INK, sw=2))
    frags.append(text((bch_knee + ldpc_knee) / 2, ytar - 30, "виграш: до ~5× брудніший канал за ту саму ціль",
                      size=11, color=INK, bold=True))

    frags.append(rect(60, 400, 640, 30, fill="#f4f7f4", stroke=FIELD, sw=1.4, rx=8))
    frags.append(text(380, 419, "SLC/MLC живуть лівіше межі BCH; TLC/QLC заганяють RBER у зону, де тримає лише LDPC",
                      size=11, color=INK, bold=True))

    render(os.path.join(OUT, "bch-vs-ldpc.svg"), W, H, *frags,
           title="Чому TLC/QLC змусили перейти з BCH на LDPC")


if __name__ == "__main__":
    fig_error_threshold()
    fig_bch_vs_ldpc()
    print("OK: reliability figs written to", OUT)
