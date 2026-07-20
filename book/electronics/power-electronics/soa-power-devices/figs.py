# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ORANGE = "#e67e22"
REDBG  = "#fdecea"
GRNBG  = "#eafaf1"


def poly(points, fill="none", stroke=LINE, sw=2.0, op=1.0, closed=False, dash=None):
    tag = "polygon" if closed else "polyline"
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<%s points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'fill-opacity="%.2f"%s stroke-linejoin="round" stroke-linecap="round"/>'
            % (tag, pts, fill, stroke, sw, op, d))


def vtext(x, y, s, size=14, color=INK, bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle"%s transform="rotate(-90 %.1f %.1f)">%s</text>'
            % (x, y, FONT, size, color, w, x, y, esc(s)))


# ── Фігура 1: карта SOA — чотири стіни на площині U–I (лог-лог) ──────────────
def fig_soa_map():
    W, H = 840, 600
    L, R, T, B = 104, 788, 74, 512
    pw, ph = R - L, B - T

    def X(v):  # V: 1..100, дві декади
        return L + (math.log10(v) - 0) / 2.0 * pw

    def Y(i):  # I: 0.1..100, три декади
        return B - (math.log10(i) + 1) / 3.0 * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]

    for v in [1, 10, 100]:
        f.append(line(X(v), T, X(v), B, color="#e9ebee", sw=1))
        f.append(text(X(v), B + 24, str(v), size=13, color=MUTED))
    for i in [0.1, 1, 10, 100]:
        f.append(line(L, Y(i), R, Y(i), color="#e9ebee", sw=1))
        f.append(text(L - 12, Y(i) + 4, ("%g" % i), size=13, color=MUTED, anchor="end"))

    # безпечна область (заливка)
    reg = [(1, 0.1), (1, 30), (3.333, 30), (25, 4), (60, 0.6), (60, 0.1)]
    f.append(poly([(X(v), Y(i)) for v, i in reg], fill=FIELD, stroke="none", op=0.13, closed=True))

    # верхня межа напруги — тонкий пунктир на всю висоту
    f.append(line(X(60), T, X(60), B, color=INK, sw=1.2, dash="4,5"))

    # чотири стіни
    f.append(line(X(1), Y(30), X(3.333), Y(30), color=NEG, sw=3.4))         # струм I_max
    f.append(line(X(3.333), Y(30), X(25), Y(4), color=ORANGE, sw=3.4))       # теплова P=UI
    f.append(line(X(25), Y(4), X(60), Y(0.6), color=POS, sw=3.4))            # нестійкість/2-й пробій
    f.append(line(X(60), Y(0.6), X(60), Y(0.1), color=INK, sw=3.4))          # напруга U_max

    # підписи стін (кожен у своїй порожній зоні)
    f.append(text(X(6.2), Y(30) - 15, "межа струму  I_max", size=14, color=NEG, bold=True))
    f.append(text(X(10.5), Y(17), "теплова межа:  P = U·I", size=14, color=ORANGE, bold=True))
    f.append(mtext(X(35), Y(0.62), ["теплова нестійкість,", "вторинний пробій"],
                   size=13.5, color=POS, bold=True))
    f.append(vtext(X(60) + 20, Y(4.2), "межа напруги  U_max", size=14, color=INK, bold=True))
    f.append(text(X(4.4), Y(2.0), "БЕЗПЕЧНА ОБЛАСТЬ", size=17, color="#1e7d46", bold=True))

    # осі
    f.append(text(L + pw / 2, H - 12, "U_DS, В  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(30, T + ph / 2, "I_D, А  (логарифмічна шкала)", size=14, color=INK))

    render(os.path.join(OUT, "soa-map.svg"), W, H, *f,
           title="Безпечна робоча область: чотири стіни")


# ── Фігура 2: імпульсна SOA — коротший імпульс піднімає теплову межу ─────────
def fig_pulsed_soa():
    W, H = 840, 600
    L, R, T, B = 104, 748, 74, 512
    pw, ph = R - L, B - T

    def X(v):
        return L + (math.log10(v) - 0) / 2.0 * pw

    def Y(i):
        return B - (math.log10(i) + 1) / 3.0 * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]
    for v in [1, 10, 100]:
        f.append(line(X(v), T, X(v), B, color="#e9ebee", sw=1))
        f.append(text(X(v), B + 24, str(v), size=13, color=MUTED))
    for i in [0.1, 1, 10, 100]:
        f.append(line(L, Y(i), R, Y(i), color="#e9ebee", sw=1))
        f.append(text(L - 12, Y(i) + 4, ("%g" % i), size=13, color=MUTED, anchor="end"))

    # незмінна рама: струм і напруга
    f.append(line(X(1), Y(30), X(60), Y(30), color=NEG, sw=3.0))
    f.append(line(X(60), T, X(60), B, color=INK, sw=1.2, dash="4,5"))
    f.append(line(X(60), Y(30), X(60), Y(0.1), color=INK, sw=3.0))
    f.append(text(X(6.5), Y(30) - 15, "межа струму  I_max  (незмінна)", size=13.5, color=NEG, bold=True))
    f.append(vtext(X(60) + 19, Y(3.0), "U_max  (незмінна)", size=13.5, color=INK, bold=True))

    # родина теплових меж: P = const, різні тривалості імпульсу
    fam = [(80, "DC", ORANGE), (160, "100 мс", "#d98a1f"),
           (350, "10 мс", "#cf6a1c"), (800, "1 мс", POS)]
    for P, lab, col in fam:
        v0 = P / 30.0          # де лінія сходить з I_max
        f.append(line(X(v0), Y(30), X(60), Y(P / 60.0), color=col, sw=2.8))
        f.append(text(X(60) + 12, Y(P / 60.0) + 4, lab, size=13.5, color=col, bold=True, anchor="start"))

    # стрілка «коротший імпульс → вище»
    f.append(line(X(3.2), Y(2.2), X(3.2), Y(22), color=MUTED, sw=2.0))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
             % (X(3.2), Y(20), X(3.2), Y(23), MUTED))
    f.append(mtext(X(3.2), Y(0.9), ["коротший", "імпульс", "піднімає межу"],
                   size=12.5, color=MUTED, bold=True))

    f.append(text(L + pw / 2, H - 12, "U_DS, В  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(30, T + ph / 2, "I_D, А  (логарифмічна шкала)", size=14, color=INK))

    render(os.path.join(OUT, "pulsed-soa.svg"), W, H, *f,
           title="Імпульсна SOA: тепло не встигає розповзтися")


# ── Фігура 3: точка нульового температурного коефіцієнта (ZTC) ───────────────
def fig_ztc():
    W, H = 820, 590
    L, R, T, B = 96, 756, 74, 500
    pw, ph = R - L, B - T
    VG0, VG1, IM = 2.5, 6.0, 10.0

    def X(vg):
        return L + (vg - VG0) / (VG1 - VG0) * pw

    def Y(i):
        return B - i / IM * ph

    def i_cold(vg):
        return 1.0 * max(0.0, vg - 3.0) ** 2

    def i_hot(vg):
        return 0.7 * max(0.0, vg - 2.6) ** 2

    ztc_vg, ztc_i = 5.05, 4.20

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]

    # зони: ліворуч від ZTC — нестійка, праворуч — стійка
    f.append(rect(L, T, X(ztc_vg) - L, ph, fill=REDBG, stroke="none", sw=0, rx=0))
    f.append(rect(X(ztc_vg), T, R - X(ztc_vg), ph, fill=GRNBG, stroke="none", sw=0, rx=0))

    for vg in [3, 4, 5, 6]:
        f.append(line(X(vg), T, X(vg), B, color="#e4e6e9", sw=1))
        f.append(text(X(vg), B + 24, str(vg), size=13, color=MUTED))
    for i in [0, 2, 4, 6, 8, 10]:
        f.append(line(L, Y(i), R, Y(i), color="#e4e6e9", sw=1))
        f.append(text(L - 12, Y(i) + 4, str(i), size=13, color=MUTED, anchor="end"))

    cold = [(X(vg / 20.0), Y(i_cold(vg / 20.0))) for vg in range(50, 121)]
    hot = [(X(vg / 20.0), Y(i_hot(vg / 20.0))) for vg in range(50, 121)]
    f.append(poly(cold, stroke=NEG, sw=3.2))
    f.append(poly(hot, stroke=POS, sw=3.2))

    # вертикаль ZTC + точка (підпис — ліворуч від лінії, у червоній зоні, подалі від легенди)
    f.append(line(X(ztc_vg), T, X(ztc_vg), B, color=INK, sw=1.6, dash="5,5"))
    f.append(circle(X(ztc_vg), Y(ztc_i), 6, fill=INK, stroke=BG, sw=2))
    f.append(mtext(X(ztc_vg) - 8, T + 34, ["точка нульового", "коефіцієнта (ZTC)"],
                   size=13, color=INK, bold=True, anchor="end"))

    # зонні підписи
    f.append(mtext(X(3.55), Y(8.6), ["НЕСТІЙКО", "гарячіше → більший струм"],
                   size=13, color=POS, bold=True))
    f.append(mtext(R - 10, Y(1.5), ["СТІЙКО", "гарячіше → менший струм"],
                   size=13, color="#1e7d46", bold=True, anchor="end"))

    # легенда
    lx, ly = R - 150, T + 16
    f.append(line(lx, ly, lx + 26, ly, color=NEG, sw=3.2))
    f.append(text(lx + 34, ly + 4, "25 °C  (холодний)", size=13, color=INK, anchor="start"))
    f.append(line(lx, ly + 24, lx + 26, ly + 24, color=POS, sw=3.2))
    f.append(text(lx + 34, ly + 28, "125 °C  (гарячий)", size=13, color=INK, anchor="start"))

    f.append(text(L + pw / 2, H - 12, "U_GS, В  (напруга на затворі)", size=14, color=INK))
    f.append(vtext(28, T + ph / 2, "I_D, А  (струм стоку)", size=14, color=INK))

    render(os.path.join(OUT, "ztc-crossover.svg"), W, H, *f,
           title="Чому SOA просідає: перетин при нагріві")


# ── Вставка math: два змагальні доданки ∂I_D/∂T і точка ZTC ──────────────────
def fig_tc_terms():
    W, H = 880, 610
    L, R, T, B = 118, 668, 76, 498
    pw, ph = R - L, B - T
    IM, YM = 80.0, 0.32

    ALPHA, M_MU, TK = 0.005, 1.5, 400.0     # В/К, показник рухливості, К

    def X(i):
        return L + i / IM * pw

    def Y(v):
        return B - v / YM * ph

    def destab(i, K):                        # g_m·α = 2·α·√(K·I_D)
        return 2.0 * ALPHA * math.sqrt(K * i)

    def stab(i):                             # I_D·m/T  — від щільності НЕ залежить
        return i * M_MU / TK

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]

    for i in [0, 20, 40, 60, 80]:
        f.append(line(X(i), T, X(i), B, color="#e9ebee", sw=1))
        f.append(text(X(i), B + 26, str(i), size=13, color=MUTED))
    for v in [0, 0.1, 0.2, 0.3]:
        f.append(line(L, Y(v), R, Y(v), color="#e9ebee", sw=1))
        f.append(text(L - 14, Y(v) + 4, ("%.1f" % v), size=13, color=MUTED, anchor="end"))

    # криві: спільна лінія-гальмо + дві √-криві різної щільності
    stab_pts = [(X(i / 4.0), Y(stab(i / 4.0))) for i in range(0, 321)]
    dense_pts = [(X(i / 4.0), Y(destab(i / 4.0, 8.9))) for i in range(0, 321)]
    spars_pts = [(X(i / 4.0), Y(destab(i / 4.0, 2.0))) for i in range(0, 321)]

    f.append(poly(stab_pts, stroke=NEG, sw=3.2))
    f.append(poly(dense_pts, stroke=POS, sw=3.2))
    f.append(poly(spars_pts, stroke=ORANGE, sw=3.2, dash="7,5"))

    # точки перетину = ZTC
    for i_z, col in [(63.3, POS), (14.2, ORANGE)]:
        f.append(line(X(i_z), Y(stab(i_z)), X(i_z), B, color=INK, sw=1.3, dash="4,5"))
        f.append(circle(X(i_z), Y(stab(i_z)), 6, fill=INK, stroke=BG, sw=2))

    # підписи ZTC — у смузі між горизонтальними лініями сітки 0.2 і 0.3,
    # зсунуті вбік від вертикалей сітки (I = 20 і I = 60)
    f.append(mtext(X(63.3) + 7, T + 64, ["ZTC щільного", "63 А"], size=13,
                   color=INK, bold=True, anchor="start"))
    f.append(mtext(X(20.0) + 7, T + 64, ["ZTC рідкого", "14 А"], size=13,
                   color=INK, bold=True, anchor="start"))

    # підписи кривих — праворуч від поля, у власній смузі
    f.append(mtext(R + 12, Y(0.300) + 4, ["I_D·m/T", "(гальмо: рухливість)"],
                   size=13, color=NEG, bold=True, anchor="start"))
    f.append(mtext(R + 12, Y(0.267) + 48, ["g_m·α, щільні комірки", "(розгін: поріг)"],
                   size=13, color=POS, bold=True, anchor="start"))
    f.append(mtext(R + 12, Y(0.126) + 4, ["g_m·α,", "рідкі комірки"],
                   size=13, color=ORANGE, bold=True, anchor="start"))

    # зони
    f.append(mtext(X(30), Y(0.045), ["∂I_D/∂T > 0 — НЕСТІЙКО", "(розгін бере гору)"],
                   size=13.5, color=POS, bold=True))
    f.append(mtext(X(72), Y(0.075), ["∂I_D/∂T < 0", "СТІЙКО"],
                   size=13.5, color="#1e7d46", bold=True))

    f.append(text(L + pw / 2, H - 14, "I_D, А  (струм стоку)", size=14, color=INK))
    f.append(vtext(32, T + ph / 2, "доданки ∂I_D/∂T, А/К", size=14, color=INK))

    render(os.path.join(OUT, "tc-terms.svg"), W, H, *f,
           title="Два змагальні доданки температурного коефіцієнта струму")


# ── Вставка math: підсилення петлі росте як √t і перетинає одиницю ────────────
def fig_loop_time():
    W, H = 880, 600
    L, R, T, B = 118, 690, 76, 492
    pw, ph = R - L, B - T

    def X(t):                                # 1e-6 .. 1 с — 6 декад
        return L + (math.log10(t) + 6.0) / 6.0 * pw

    def Y(m):                                # 1e-3 .. 1e2 — 5 декад
        return B - (math.log10(m) + 3.0) / 5.0 * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]

    # зона M > 1 — небезпечна
    f.append(rect(L, T, pw, Y(1.0) - T, fill=REDBG, stroke="none", sw=0, rx=0))

    tick_t = [(1e-6, "1 мкс"), (1e-5, "10 мкс"), (1e-4, "100 мкс"),
              (1e-3, "1 мс"), (1e-2, "10 мс"), (1e-1, "100 мс"), (1.0, "1 с")]
    for t, lab in tick_t:
        f.append(line(X(t), T, X(t), B, color="#e9ebee", sw=1))
        f.append(text(X(t), B + 26, lab, size=12.5, color=MUTED))
    for m in [1e-3, 1e-2, 1e-1, 1, 10, 100]:
        f.append(line(L, Y(m), R, Y(m), color="#e9ebee", sw=1))
        f.append(text(L - 14, Y(m) + 4, ("%g" % m), size=13, color=MUTED, anchor="end"))

    # M(t) = 0.1674 · U_DS · √t   (робоча точка стала, змінюємо лише U_DS)
    for U, col, tc in [(20, NEG, 0.0893), (50, ORANGE, 0.0143), (100, POS, 0.00357)]:
        pts = [(X(10 ** (-6 + k / 40.0)), Y(0.1674 * U * math.sqrt(10 ** (-6 + k / 40.0))))
               for k in range(0, 241)]
        f.append(poly(pts, stroke=col, sw=3.0))
        f.append(text(R + 10, Y(0.1674 * U * 1.0) + 4, "U_DS = %d В" % U,
                      size=13, color=col, bold=True, anchor="start"))
        # позначка часу зриву
        f.append(circle(X(tc), Y(1.0), 5.5, fill=col, stroke=BG, sw=2))

    f.append(line(L, Y(1.0), R, Y(1.0), color=INK, sw=2.0, dash="6,5"))
    f.append(text(L + 10, Y(1.0) - 10, "M = 1  — межа стійкості", size=13.5,
                  color=INK, bold=True, anchor="start"))

    # підписи часів зриву — під віссю M=1, у порожній зоні
    f.append(mtext(X(0.00357), Y(0.06), ["3.6 мс"], size=12.5, color=POS, bold=True))
    f.append(mtext(X(0.0143), Y(0.012), ["14 мс"], size=12.5, color=ORANGE, bold=True))
    f.append(mtext(X(0.0893), Y(0.0024), ["89 мс"], size=12.5, color=NEG, bold=True))

    # короткий підпис зони — щоб умістився між вертикалями сітки
    f.append(text(X(0.032), Y(39), "ЗОНА ЗРИВУ", size=13.5, color=POS, bold=True))
    f.append(text(X(1.3e-5), Y(0.0022), "нахил ½:  M ∝ √t", size=13.5,
                  color=MUTED, bold=True, anchor="start"))

    f.append(text(L + pw / 2, H - 12, "тривалість імпульсу t  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(32, T + ph / 2, "підсилення петлі M  (лог. шкала)", size=14, color=INK))

    render(os.path.join(OUT, "loop-gain-time.svg"), W, H, *f,
           title="Підсилення петлі росте як корінь із часу")


# ── Вставка math: стіна нестійкості з нахилом −2 проти теплової з нахилом −1 ──
def fig_instability_wall():
    W, H = 880, 610
    L, R, T, B = 112, 700, 76, 500
    pw, ph = R - L, B - T

    def X(v):                                # 1..100 В — дві декади
        return L + math.log10(v) / 2.0 * pw

    def Y(i):                                # 0.1..100 А — три декади
        return B - (math.log10(i) + 1.0) / 3.0 * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]
    for v in [1, 10, 100]:
        f.append(line(X(v), T, X(v), B, color="#e9ebee", sw=1))
        f.append(text(X(v), B + 26, str(v), size=13, color=MUTED))
    for i in [0.1, 1, 10, 100]:
        f.append(line(L, Y(i), R, Y(i), color="#e9ebee", sw=1))
        f.append(text(L - 14, Y(i) + 4, ("%g" % i), size=13, color=MUTED, anchor="end"))

    # втрачена через нестійкість область (щільний прилад)
    lost = [(X(11.24), Y(8.9))] \
        + [(X(11.24 * (100 / 11.24) ** (k / 30.0)),
            Y(1123.6 / (11.24 * (100 / 11.24) ** (k / 30.0)) ** 2)) for k in range(0, 31)] \
        + [(X(100), Y(1.0))] \
        + [(X(11.24 * (100 / 11.24) ** (1 - k / 30.0)),
            Y(100.0 / (11.24 * (100 / 11.24) ** (1 - k / 30.0)))) for k in range(0, 31)]
    f.append(poly(lost, fill=POS, stroke="none", op=0.11, closed=True))

    # теплова стіна P = 100 Вт, нахил −1
    f.append(line(X(1), Y(100), X(100), Y(1), color=ORANGE, sw=3.2))

    # стіна нестійкості, нахил −2: щільний (K=8.9) і рідкий (K=2) прилади
    dense = [(X(11.24 * (100 / 11.24) ** (k / 60.0)),
              Y(1123.6 / (11.24 * (100 / 11.24) ** (k / 60.0)) ** 2)) for k in range(0, 61)]
    spars = [(X(50.0 * 2.0 ** (k / 60.0)), Y(5000.0 / (50.0 * 2.0 ** (k / 60.0)) ** 2))
             for k in range(0, 61)]
    f.append(poly(dense, stroke=POS, sw=3.4))
    f.append(poly(spars, stroke=NEG, sw=3.0, dash="7,5"))

    # кути
    for u, i, col in [(11.24, 8.9, POS), (50.0, 2.0, NEG)]:
        f.append(circle(X(u), Y(i), 6, fill=col, stroke=BG, sw=2))

    f.append(mtext(X(2.0), Y(60), ["теплова стіна  P = U·I = 100 Вт", "нахил −1"],
                   size=13.5, color=ORANGE, bold=True, anchor="start"))
    f.append(mtext(X(22), Y(0.9), ["стіна нестійкості, щільні комірки", "I ∝ 1/U_DS²  — нахил −2"],
                   size=13, color=POS, bold=True, anchor="start"))
    f.append(mtext(X(58), Y(9.5), ["рідкі комірки:", "кут аж на 50 В"],
                   size=13, color=NEG, bold=True, anchor="start"))
    f.append(mtext(X(11.24), Y(23), ["кут", "11 В"], size=13, color=POS, bold=True))
    # у середині втраченої смуги (між тепловою стіною 3.33 А і стіною нестійкості 1.25 А при 30 В)
    f.append(mtext(X(30), Y(2.0), ["ВТРАЧЕНО", "через нестійкість"],
                   size=13.5, color=POS, bold=True))
    f.append(text(X(2.6), Y(0.3), "БЕЗПЕЧНО", size=15, color="#1e7d46", bold=True, anchor="start"))

    f.append(text(L + pw / 2, H - 14, "U_DS, В  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(32, T + ph / 2, "I_D, А  (логарифмічна шкала)", size=14, color=INK))

    render(os.path.join(OUT, "instability-wall.svg"), W, H, *f,
           title="Стіна нестійкості проти теплової стіни")


# ═══ Фігури до вставки proj-soa-guard ════════════════════════════════════════
# Тепловий портрет BUK7S1R0-40H: мережа Фостера, здобута точним перетворенням
# опублікованої Nexperia мережі Кауера (AN11261 Rev. 5.0, Fig. 6).
FOST_R = [0.001935, 0.002183, 0.017918, 0.123572, 0.254393]      # К/Вт
FOST_T = [0.2136e-6, 6.658e-6, 15.11e-6, 847.4e-6, 6.327e-3]     # с


def cap_sym(cx, cy, w=13, gap=7, color=LINE, sw=2.2, vertical=False):
    """Дві пластини конденсатора. vertical=True — струм тече згори вниз."""
    if vertical:
        return (line(cx - w, cy - gap / 2.0, cx + w, cy - gap / 2.0, color=color, sw=sw) +
                line(cx - w, cy + gap / 2.0, cx + w, cy + gap / 2.0, color=color, sw=sw))
    return (line(cx - gap / 2.0, cy - w, cx - gap / 2.0, cy + w, color=color, sw=sw) +
            line(cx + gap / 2.0, cy - w, cx + gap / 2.0, cy + w, color=color, sw=sw))


# ── Фігура 7: Фостер проти Кауера — де висять теплоємності ───────────────────
def fig_foster_vs_cauer():
    W, H = 900, 596
    XS = [150, 268, 386, 504, 622, 740]
    LBL = ["1", "2", "3", "", "n"]
    f = []

    # ── ФОСТЕР ──
    BASE = 196
    f.append(text(58, 60, "МЕРЕЖА ФОСТЕРА", size=16, color=POS, bold=True, anchor="start"))
    f.append(text(58, 82, "теплоємності висять МІЖ вузлами · вузли фізичного змісту не мають",
                 size=13, color=MUTED, anchor="start"))
    f.append(line(XS[0] - 44, BASE, XS[0], BASE, color=LINE, sw=1.8))
    f.append(text(XS[0] - 50, BASE + 5, "T_j", size=14, color=POS, bold=True, anchor="end"))

    for k in range(5):
        xa, xb = XS[k], XS[k + 1]
        if k == 3:
            f.append(text((xa + xb) / 2.0, BASE + 7, "· · ·", size=22, color=MUTED))
            continue
        mid = (xa + xb) / 2.0
        f.append(line(xa, BASE, xa + 22, BASE, color=LINE, sw=1.8))
        f.append(rect(xa + 22, BASE - 13, xb - xa - 44, 26, fill=BG, stroke=LINE, sw=1.8, rx=3))
        f.append(text(mid, BASE + 5, "R" + LBL[k], size=13.5, color=INK, bold=True))
        f.append(line(xb - 22, BASE, xb, BASE, color=LINE, sw=1.8))
        f.append(line(xa, BASE, xa, BASE - 54, color=LINE, sw=1.8))
        f.append(line(xa, BASE - 54, mid - 3.5, BASE - 54, color=LINE, sw=1.8))
        f.append(cap_sym(mid, BASE - 54, color=LINE))
        f.append(line(mid + 3.5, BASE - 54, xb, BASE - 54, color=LINE, sw=1.8))
        f.append(line(xb, BASE - 54, xb, BASE, color=LINE, sw=1.8))
        f.append(text(mid, BASE - 76, "C" + LBL[k], size=13.5, color=INK, bold=True))
        f.append(circle(xa, BASE, 4, fill=LINE, stroke=LINE, sw=1))

    f.append(circle(XS[5], BASE, 4, fill=LINE, stroke=LINE, sw=1))
    f.append(line(XS[5], BASE, XS[5] + 30, BASE, color=LINE, sw=1.8))
    f.append(text(XS[5] + 36, BASE + 5, "T_корп", size=14, color=NEG, bold=True, anchor="start"))
    f.append(mtext(440, BASE + 52,
                   ["Z_θ(t) = Σ Rᵢ · (1 − e^(−t/τᵢ))   — п'ять незалежних експонент;",
                    "модель дає ЛИШЕ перепад T_j − T_корп: приєднати радіатор нікуди"],
                   size=13, color=POS, lh=1.5))

    # ── КАУЕР ──
    BASE2 = 412
    GND = 506
    f.append(text(58, 322, "МЕРЕЖА КАУЕРА", size=16, color=NEG, bold=True, anchor="start"))
    f.append(text(58, 344, "теплоємності висять на СПІЛЬНІЙ землі · вузли — справжні шари кристала",
                 size=13, color=MUTED, anchor="start"))
    f.append(line(XS[0] - 44, BASE2, XS[0], BASE2, color=LINE, sw=1.8))
    f.append(text(XS[0] - 50, BASE2 + 5, "T_j", size=14, color=POS, bold=True, anchor="end"))

    for k in range(5):
        xa, xb = XS[k], XS[k + 1]
        if k == 3:
            f.append(text((xa + xb) / 2.0, BASE2 + 7, "· · ·", size=22, color=MUTED))
            continue
        mid = (xa + xb) / 2.0
        f.append(line(xa, BASE2, xa + 22, BASE2, color=LINE, sw=1.8))
        f.append(rect(xa + 22, BASE2 - 13, xb - xa - 44, 26, fill=BG, stroke=LINE, sw=1.8, rx=3))
        f.append(text(mid, BASE2 + 5, "R" + LBL[k], size=13.5, color=INK, bold=True))
        f.append(line(xb - 22, BASE2, xb, BASE2, color=LINE, sw=1.8))
        f.append(line(xa, BASE2, xa, GND - 32, color=LINE, sw=1.8))
        f.append(cap_sym(xa, GND - 26, color=NEG, vertical=True))
        f.append(line(xa, GND - 20, xa, GND, color=LINE, sw=1.8))
        f.append(text(xa - 22, GND - 22, "C" + LBL[k], size=13.5, color=INK, bold=True, anchor="end"))
        f.append(circle(xa, BASE2, 4, fill=LINE, stroke=LINE, sw=1))

    f.append(circle(XS[5], BASE2, 4, fill=LINE, stroke=LINE, sw=1))
    f.append(line(XS[5], BASE2, XS[5] + 30, BASE2, color=LINE, sw=1.8))
    f.append(text(XS[5] + 36, BASE2 + 5, "T_корп", size=14, color=NEG, bold=True, anchor="start"))
    f.append(line(120, GND, 660, GND, color=NEG, sw=2.6))
    f.append(text(670, GND + 5, "T_довкілля", size=13.5, color=NEG, bold=True, anchor="start"))
    f.append(text(400, GND + 40, "вузли справжні → сюди МОЖНА дочепити модель радіатора",
                 size=13, color=NEG))

    render(os.path.join(OUT, "foster-vs-cauer.svg"), W, H, *f,
           title="Дві RC-мережі однакової поведінки, різного змісту")


# ── Фігура 8: як п'ять експонент складаються в криву Z_θ(t) ──────────────────
def fig_zth_stages():
    W, H = 900, 600
    L, R, T, B = 108, 690, 66, 496
    pw, ph = R - L, B - T
    T0, T1 = -7.0, 0.0
    Z0, Z1 = -3.0, 0.0

    def X(t):
        return L + (math.log10(t) - T0) / (T1 - T0) * pw

    def Y(z):
        return B - (math.log10(max(z, 10 ** Z0)) - Z0) / (Z1 - Z0) * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]
    labs = {-7: "100 нс", -6: "1 мкс", -5: "10 мкс", -4: "100 мкс",
            -3: "1 мс", -2: "10 мс", -1: "100 мс", 0: "1 с"}
    for e in range(-7, 1):
        f.append(line(X(10.0 ** e), T, X(10.0 ** e), B, color="#e9ebee", sw=1))
        f.append(text(X(10.0 ** e), B + 24, labs[e], size=12.5, color=MUTED))
    for e in range(-3, 1):
        f.append(line(L, Y(10.0 ** e), R, Y(10.0 ** e), color="#e9ebee", sw=1))
        f.append(text(L - 12, Y(10.0 ** e) + 4, ("%g" % (10.0 ** e)), size=12.5, color=MUTED, anchor="end"))

    ts = [10.0 ** (T0 + (T1 - T0) * i / 400.0) for i in range(401)]

    f.append(line(L, Y(0.4), R, Y(0.4), color=INK, sw=1.6, dash="6,5"))
    f.append(text(R - 8, Y(0.4) - 11, "R_θ(j-mb) = 0.40 К/Вт", size=13, color=INK, bold=True, anchor="end"))

    cols = ["#9aa4b2", "#7f8b9c", "#5f6b7d", ORANGE, POS]
    for i in range(5):
        f.append(poly([(X(t), Y(FOST_R[i] * (1 - math.exp(-t / FOST_T[i])))) for t in ts],
                      stroke=cols[i], sw=1.9, dash="5,4"))
        f.append(circle(X(FOST_T[i]), Y(FOST_R[i] * 0.632), 3.6, fill=cols[i], stroke=BG, sw=1.4))

    f.append(poly([(X(t), Y(sum(FOST_R[i] * (1 - math.exp(-t / FOST_T[i])) for i in range(5))))
                   for t in ts], stroke=NEG, sw=3.6))

    f.append(text(X(3e-5), Y(0.42), "Z_θ(t) — сума ланок", size=15, color=NEG, bold=True))
    f.append(line(X(3e-5), Y(0.46), X(9e-5), Y(0.06), color=NEG, sw=1.2))

    tx, ty = R + 20, T + 20
    f.append(text(tx, ty, "ланки мережі", size=13.5, color=INK, bold=True, anchor="start"))
    rows = [("R₁ 0.0019", "τ₁ 0.21 мкс"), ("R₂ 0.0022", "τ₂ 6.7 мкс"),
            ("R₃ 0.0179", "τ₃ 15 мкс"), ("R₄ 0.1236", "τ₄ 847 мкс"),
            ("R₅ 0.2544", "τ₅ 6.3 мс")]
    for i, (a, b) in enumerate(rows):
        yy = ty + 30 + i * 42
        f.append(line(tx, yy - 4, tx + 20, yy - 4, color=cols[i], sw=2.6,
                      dash=None if i == 4 else "5,4"))
        f.append(text(tx + 27, yy, a, size=12.5, color=INK, anchor="start"))
        f.append(text(tx + 27, yy + 16, b, size=12.5, color=MUTED, anchor="start"))
    f.append(line(tx, ty + 248, tx + 140, ty + 248, color=MUTED, sw=1))
    f.append(text(tx, ty + 270, "Σ Rᵢ = 0.400 К/Вт", size=13, color=INK, bold=True, anchor="start"))

    f.append(text(L + pw / 2, H - 14, "тривалість імпульсу  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(30, T + ph / 2, "Z_θ(j-mb), К/Вт", size=14, color=INK))

    render(os.path.join(OUT, "zth-stages.svg"), W, H, *f,
           title="П'ять експонент складаються в Z_θ(t): BUK7S1R0-40H")


# ── Фігура 9: вартовий у ділі — той самий струм, протилежна доля ─────────────
def fig_guard_trace():
    W, H = 940, 640
    L, R = 112, 636
    TP, BP = 96, 244
    TT, BT = 312, 566
    pw = R - L
    TEND = 10e-3
    VBUS, CL, ILIM = 24.0, 2200e-6, 12.0
    TCHG = CL * VBUS / ILIM
    TCASE, TRIP, DT = 85.0, 150.0, 50e-6

    def X(t):
        return L + t / TEND * pw

    def YP(p):
        return BP - p / 330.0 * (BP - TP)

    def YT(tj):
        return BT - (tj - 60.0) / 155.0 * (BT - TT)

    def p_in(t):
        return max(0.0, (VBUS - (ILIM / CL) * t) * ILIM) if t < TCHG else 0.0

    def p_sh(t):
        return VBUS * ILIM

    def trace(pf):
        a = [math.exp(-DT / FOST_T[i]) for i in range(5)]
        g = [FOST_R[i] * (1 - a[i]) for i in range(5)]
        st, out = [0.0] * 5, []
        for k in range(int(TEND / DT) + 1):
            t = k * DT
            p = pf(t)
            s = 0.0
            for i in range(5):
                st[i] = st[i] * a[i] + p * g[i]
                s += st[i]
            out.append((t, TCASE + s))
        return out

    f = [text(L, 36, "У ОБОХ випадках струм — рівно 12 А, рівно на межі обмежувача.",
              size=15, color=INK, bold=True, anchor="start"),
         text(L, 60, "Поріг «струм більший за X» не бачить між ними ЖОДНОЇ різниці.",
              size=15, color=POS, bold=True, anchor="start")]

    # ── потужність ──
    f.append(rect(L, TP, pw, BP - TP, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0))
    for p in [0, 100, 200, 300]:
        f.append(line(L, YP(p), R, YP(p), color="#e9ebee", sw=1))
        f.append(text(L - 12, YP(p) + 4, str(p), size=12, color=MUTED, anchor="end"))
    f.append(vtext(38, (TP + BP) / 2.0, "P на ключі, Вт", size=13.5, color=INK))
    f.append(poly([(X(0), YP(288)), (X(TEND), YP(288))], stroke=POS, sw=3.2))
    steps = [i * TEND / 200.0 for i in range(201)]
    f.append(poly([(X(t), YP(p_in(t))) for t in steps], stroke=FIELD, sw=3.2))

    # ── температура ──
    f.append(rect(L, TT, pw, BT - TT, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0))
    for tj in [75, 100, 125, 150, 175, 200]:
        f.append(line(L, YT(tj), R, YT(tj), color="#e9ebee", sw=1))
        f.append(text(L - 12, YT(tj) + 4, str(tj), size=12, color=MUTED, anchor="end"))
    f.append(vtext(38, (TT + BT) / 2.0, "оцінка T_j, °C", size=13.5, color=INK))
    for t in [0, 2, 4, 6, 8, 10]:
        f.append(line(X(t * 1e-3), TT, X(t * 1e-3), BT, color="#e9ebee", sw=1))
        f.append(text(X(t * 1e-3), BT + 24, str(t), size=12.5, color=MUTED))

    f.append(rect(L, TT, pw, YT(175.0) - TT, fill=REDBG, stroke="none", sw=0, rx=0))
    f.append(line(L, YT(175.0), R, YT(175.0), color=POS, sw=2.0, dash="6,4"))
    f.append(line(L, YT(TRIP), R, YT(TRIP), color=INK, sw=1.8, dash="5,5"))

    ti, tsh = trace(p_in), trace(p_sh)
    trip_t = next(t for t, tj in tsh if tj >= TRIP)
    f.append(poly([(X(t), YT(tj)) for t, tj in tsh if t <= trip_t], stroke=POS, sw=3.4))
    f.append(poly([(X(t), YT(tj)) for t, tj in tsh if t >= trip_t], stroke=POS, sw=2.0, dash="6,5"))
    f.append(line(X(4.84e-3), TT, X(4.84e-3), BT, color=ORANGE, sw=1.8, dash="4,4"))
    f.append(poly([(X(t), YT(tj)) for t, tj in ti], stroke=FIELD, sw=3.4))
    f.append(circle(X(trip_t), YT(TRIP), 6.5, fill=POS, stroke=BG, sw=2.2))
    pk = max(tj for _, tj in ti)

    f.append(text(L + pw / 2, BT + 50, "час від замикання ключа, мс", size=14, color=INK))

    # ── колонка пояснень праворуч від полів ──
    cx = R + 22
    f.append(text(cx, TP + 14, "потужність", size=13.5, color=INK, bold=True, anchor="start"))
    f.append(line(cx, TP + 36, cx + 20, TP + 36, color=POS, sw=3.2))
    f.append(mtext(cx + 27, TP + 40, ["замикання: 288 Вт", "і не спадає нікуди"],
                   size=12.5, color=POS, anchor="start", lh=1.35))
    f.append(line(cx, TP + 92, cx + 20, TP + 92, color=FIELD, sw=3.2))
    f.append(mtext(cx + 27, TP + 96, ["штатний пуск: та сама", "288 Вт на старті, але", "спадає — банка"],
                   size=12.5, color="#1e7d46", anchor="start", lh=1.35))

    f.append(text(cx, TT + 14, "температура", size=13.5, color=INK, bold=True, anchor="start"))
    f.append(line(cx, TT + 36, cx + 20, TT + 36, color=POS, sw=1.8, dash="6,4"))
    f.append(text(cx + 27, TT + 40, "T_j,max = 175 °C", size=12.5, color=POS, bold=True, anchor="start"))
    f.append(line(cx, TT + 64, cx + 20, TT + 64, color=INK, sw=1.8, dash="5,5"))
    f.append(text(cx + 27, TT + 68, "поріг вартового 150 °C", size=12.5, color=INK, anchor="start"))

    f.append(circle(cx + 10, TT + 100, 5.5, fill=POS, stroke=BG, sw=2))
    f.append(mtext(cx + 27, TT + 96, ["ВАРТОВИЙ ВИМИКАЄ", "на %.2f мс" % (trip_t * 1e3)],
                   size=12.5, color=POS, bold=True, anchor="start", lh=1.35))
    f.append(line(cx, TT + 146, cx + 20, TT + 146, color=POS, sw=2.0, dash="6,5"))
    f.append(mtext(cx + 27, TT + 150, ["куди пішло б, якби", "не вимкнув"],
                   size=12.5, color=POS, anchor="start", lh=1.35))
    f.append(line(cx, TT + 200, cx + 20, TT + 200, color=FIELD, sw=3.2))
    f.append(mtext(cx + 27, TT + 204, ["штатний пуск:", "пік %.0f °C — вартовий" % pk, "мовчить"],
                   size=12.5, color="#1e7d46", anchor="start", lh=1.35))
    f.append(line(cx + 10, TT + 250, cx + 10, TT + 268, color=ORANGE, sw=1.8, dash="4,4"))
    f.append(mtext(cx + 27, TT + 254, ["I²t зреагував би аж", "тут: на 2.2 мс пізніше,", "коли вже 166 °C"],
                   size=12.5, color=ORANGE, bold=True, anchor="start", lh=1.35))

    render(os.path.join(OUT, "guard-trace.svg"), W, H, *f,
           title="Вартовий у ділі: однаковий струм, протилежна доля")


# ── Фігура 10: сліпа пляма — модель бачить середнє, а гине цятка ─────────────
def fig_blind_spot():
    W, H = 880, 600
    L, R, T, B = 108, 700, 100, 500
    pw, ph = R - L, B - T

    def X(v):
        return L + math.log10(v) / 2.0 * pw

    def Y(i):
        return B - (math.log10(i) + 1) / 3.0 * ph

    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]
    for v in [1, 10, 100]:
        f.append(line(X(v), T, X(v), B, color="#e9ebee", sw=1))
        f.append(text(X(v), B + 24, str(v), size=13, color=MUTED))
    for i in [0.1, 1, 10, 100]:
        f.append(line(L, Y(i), R, Y(i), color="#e9ebee", sw=1))
        f.append(text(L - 12, Y(i) + 4, ("%g" % i), size=13, color=MUTED, anchor="end"))

    PWR = 300.0
    mv = [1.5 * (100.0 / 1.5) ** (i / 80.0) for i in range(81)]

    def soa_i(v):
        p = PWR if v <= 8.0 else PWR * (8.0 / v) ** 0.85
        return min(p / v, 40.0)

    f.append(poly([(X(v), Y(PWR / v)) for v in mv if 0.1 <= PWR / v <= 100],
                  stroke=NEG, sw=3.2, dash="7,5"))
    f.append(poly([(X(v), Y(soa_i(v))) for v in mv if 0.1 <= soa_i(v) <= 100], stroke=POS, sw=3.4))

    band = [v for v in mv if v > 8.0 and 0.1 <= soa_i(v) <= 100 and 0.1 <= PWR / v <= 100]
    if band:
        f.append(poly([(X(v), Y(PWR / v)) for v in band] +
                      [(X(v), Y(soa_i(v))) for v in reversed(band)],
                      fill=POS, stroke="none", op=0.17, closed=True))

    f.append(mtext(X(1.9), Y(46), ["у що ВІРИТЬ теплова модель:", "аби середня T_j була під стелею"],
                   size=13.5, color=NEG, bold=True, anchor="start"))
    f.append(line(X(6.4), Y(33), X(14.5), Y(21), color=NEG, sw=1.2))

    f.append(mtext(X(1.15), Y(0.5), ["справжня SOA із даташита:", "при високій напрузі струм", "стягується в цятку"],
                   size=13.5, color=POS, bold=True, anchor="start"))
    f.append(line(X(9.5), Y(0.72), X(26), Y(2.4), color=POS, sw=1.2))

    f.append(mtext(X(46), Y(4.6), ["СЛІПА ПЛЯМА", "вартовий каже «ще тепло»,", "а транзистор уже мертвий"],
                   size=14, color="#8e1b0f", bold=True))

    f.append(text(L + pw / 2, H - 14, "U_DS, В  (логарифмічна шкала)", size=14, color=INK))
    f.append(vtext(32, T + ph / 2, "I_D, А  (логарифмічна шкала)", size=14, color=INK))
    f.append(text(L, 40, "Мережа Фостера рахує СЕРЕДНЮ температуру кристала.",
                 size=15, color=INK, bold=True, anchor="start"))
    f.append(text(L, 64, "Філамент, що проплавляє кристал, у це середнє не вміщається.",
                 size=15, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "guard-blind-spot.svg"), W, H, *f,
           title="Сліпа пляма теплової моделі")


# ── Вставка hist: кольорова стрілка з власною головкою ───────────────────────
def carrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=11):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    bx, by = x2 - ux * head, y2 - uy * head
    px, py = -uy, ux
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x2, y2, bx + px * head * 0.52, by + py * head * 0.52,
        bx - px * head * 0.52, by - py * head * 0.52)
    return (line(x1, y1, bx, by, color=color, sw=sw)
            + '<polygon points="%s" fill="%s"/>' % (tri, color))


# ── Вставка hist: чому пробій «вторинний» — знімок із характериографа ─────────
def fig_second_breakdown_trace():
    W, H = 880, 580
    L, R, T, B = 104, 812, 76, 496
    pw, ph = R - L, B - T

    def X(v):                                # 0..120 В, лінійна
        return L + v / 120.0 * pw

    def Y(i):                                # 0..6 А, лінійна
        return B - i / 6.0 * ph

    # осі без наскрізної сітки: це знімок ФОРМИ кривої, а не таблиця значень,
    # тож замість ліній через усе поле — короткі позначки біля самих осей
    f = [rect(L, T, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=0)]
    for v in [0, 40, 80, 120]:
        f.append(line(X(v), B - 7, X(v), B, color=MUTED, sw=1.2))
        f.append(text(X(v), B + 26, str(v), size=13, color=MUTED))
    for i in [0, 2, 4, 6]:
        f.append(line(L, Y(i), L + 7, Y(i), color=MUTED, sw=1.2))
        f.append(text(L - 14, Y(i) + 4, str(i), size=13, color=MUTED, anchor="end"))

    # активна область: струм тримається базою, напруга росте вільно
    act = [(0, 0), (1.5, 0.80), (4, 1.12), (10, 1.20), (40, 1.28), (70, 1.35)]
    f.append(poly([(X(v), Y(i)) for v, i in act], stroke=NEG, sw=3.2))

    # перший пробій — лавинний: струм злітає при майже сталій напрузі
    f.append(poly([(X(70), Y(1.35)), (X(72.5), Y(2.6))], stroke=ORANGE, sw=3.4))

    # вторинний пробій — зрив напруги ліворуч при зростанні струму
    f.append(carrow(X(72.5), Y(2.6), X(16.5), Y(2.6), color=POS, sw=4.0, head=14))

    # гілка низької напруги утримання — кристал уже гине
    f.append(poly([(X(15), Y(2.6)), (X(15.6), Y(5.6))], stroke=POS, sw=3.4))

    # підписи — кожен у своїй порожній зоні
    f.append(mtext(X(34), Y(0.5), ["активна область:", "транзистор слухається бази"],
                   size=13, color=NEG, bold=True))
    f.append(mtext(X(101), Y(1.55), ["перший пробій — лавинний", "(BV_CEO): струм росте,", "напруга тримається"],
                   size=13, color=ORANGE, bold=True))
    f.append(carrow(604, Y(1.55), X(73) + 4, Y(1.55), color=MUTED, sw=1.8, head=9))

    f.append(text(X(45), Y(2.95), "ділянка від'ємного опору", size=12.5, color=MUTED, bold=True))
    f.append(mtext(X(43), Y(2.25), ["ВТОРИННИЙ ПРОБІЙ:", "напруга падає стрибком", "за мікросекунди"],
                   size=13, color=POS, bold=True))

    f.append(mtext(X(60), Y(4.6), ["низька напруга утримання:", "струм не спинити —", "кремній уже плавиться"],
                   size=13, color=POS, bold=True))
    f.append(carrow(360, Y(4.6) - 4, X(15.6) + 7, Y(4.6) - 4, color=MUTED, sw=1.8, head=9))

    f.append(text(L + pw / 2, H - 12, "U_CE, В  (напруга колектор–емітер)", size=14, color=INK))
    f.append(vtext(30, T + ph / 2, "I_C, А  (струм колектора)", size=14, color=INK))

    render(os.path.join(OUT, "second-breakdown-trace.svg"), W, H, *f,
           title="Чому пробій «вторинний»: два зриви на одній кривій")


# ── Вставка hist: струм стягується у філамент під однією коміркою ─────────────
def fig_emitter_filament():
    W, H = 880, 560
    DX0, DXW = 210, 490                       # кристал: x від .. ширина
    NST, SW_ = 5, 54
    GAP = (DXW - NST * SW_) / (NST + 1.0)

    def stripe_x(i):
        return DX0 + GAP + i * (SW_ + GAP)

    def panel(oy, title, hot):
        g = [text(455, oy, title, size=15, color=INK, bold=True)]
        ym, ye, yb, yc = oy + 18, oy + 36, oy + 68, oy + 110

        # шари кристала
        g.append(rect(DX0, yc, DXW, 48, fill="#e8edf3", stroke=LINE, sw=1.4, rx=0))
        g.append(rect(DX0, yb, DXW, 42, fill="#f7f0e6", stroke=LINE, sw=1.4, rx=0))
        g.append(rect(DX0, ym, DXW, 18, fill="#cfd6dd", stroke=LINE, sw=1.4, rx=0))

        # комірки емітера
        for i in range(NST):
            isf = hot and i == 2
            g.append(rect(stripe_x(i), ye, SW_, 32,
                          fill=(REDBG if isf else "#e8edf3"),
                          stroke=(POS if isf else LINE), sw=(2.4 if isf else 1.4), rx=0))

        # гаряча пляма в базі під центральною коміркою
        if hot:
            cx = stripe_x(2) + SW_ / 2
            g.append('<ellipse cx="%.1f" cy="%.1f" rx="46" ry="27" fill="%s" '
                     'fill-opacity="0.28" stroke="none"/>' % (cx, oy + 95, POS))

        # струм: знизу (колектор) угору крізь базу в комірку емітера
        for i in range(NST):
            cx = stripe_x(i) + SW_ / 2
            if hot and i == 2:
                g.append(carrow(cx, oy + 152, cx, oy + 74, color=POS, sw=9.0, head=17))
            elif hot:
                g.append(carrow(cx, oy + 152, cx, oy + 74, color=MUTED, sw=1.4, head=7))
            else:
                g.append(carrow(cx, oy + 152, cx, oy + 74, color=NEG, sw=3.4, head=11))

        # підписи шарів — ліворуч від кристала, у власній смузі
        for ty, lab in [(ym + 13, "металізація емітера"), (ye + 21, "комірки емітера (n⁺)"),
                        (yb + 27, "база (p)"), (yc + 30, "колектор (n)")]:
            g.append(text(DX0 - 12, ty, lab, size=12.5, color=MUTED, anchor="end"))
        return g

    f = panel(80, "Як задумано: п'ять комірок — п'ять рівних струмів", False)
    f.append(text(455, 265, "уся площа однаково тепла — жодна комірка не виривається вперед",
                  size=13, color="#1e7d46", bold=True))

    f += panel(330, "Що стається: одна комірка забирає струм собі", True)
    f.append(text(455, 515, "середнє по кристалу ще в нормі — а філамент уже плавить кремній (1414 °C)",
                  size=13, color=POS, bold=True))

    render(os.path.join(OUT, "emitter-filament.svg"), W, H, *f,
           title="Стягування струму: середнє в нормі, цятка мертва")


# ── Вставка hist: дві ери однієї фізики ──────────────────────────────────────
def fig_soa_history():
    W, H = 900, 916
    SPX, BX, BW = 168, 190, 682

    def evbox(y, year, lines, col):
        h = len(lines) * 17 + 20
        g = rect(BX, y, BW, h, fill=BG, stroke=col, sw=1.6, rx=6)
        g += text(150, y + h / 2 + 5, year, size=14, color=col, bold=True, anchor="end")
        g += circle(SPX, y + h / 2, 5.5, fill=col, stroke=BG, sw=2)
        ty = y + h / 2 - (len(lines) - 1) * 16.9 / 2 + 4.5
        g += mtext(BX + 14, ty, lines, size=13, color=INK, anchor="start")
        return g, h + 12

    def erabar(y, lab, col, tint):
        g = rect(20, y, 852, 34, fill=tint, stroke=col, sw=1.4, rx=6)
        g += text(446, y + 22, lab, size=14.5, color=col, bold=True)
        return g, 34 + 12

    f = [line(SPX, 94, SPX, 890, color="#dfe3e8", sw=3)]
    y = 60

    g, dy = erabar(y, "ЕРА БІПОЛЯРНИХ: вторинний пробій", NEG, "#eaf0fd"); f.append(g); y += dy
    for year, lines in [
        ("1958", ["Торнтон і Сіммонс: «новий режим високого струму»",
                  "— явище описали, але зрозуміти не змогли"]),
        ("1962", ["Шафт і Френч (NBS, на запит JEDEC): перша характеризація.",
                  "Вирок: межу не задати трьома числами — потрібні енергія й час"]),
        ("1963", ["Скарлетт, Шоклі й Гайц: при критичній внутрішній температурі",
                  "струм і тепло збігаються в одну гарячу цятку"]),
        ("1967", ["Шафт: оглядова стаття у Proc. IEEE + окрема бібліографія",
                  "— підсумок дев'яти років суперечок про механізм"]),
        ("1970", ["Гауер і Редді: швидкий зрив — від лавинної інжекції, тепло тут",
                  "ні до чого → безпечну область розділяють на FBSOA і RBSOA"]),
    ]:
        g, dy = evbox(y, year, lines, NEG); f.append(g); y += dy

    g, dy = evbox(y, "40 років", ["«У MOSFET вторинного пробою немає»: опір відкритого каналу",
                                  "росте з нагрівом і сам вирівнює струм між комірками"], MUTED)
    f.append(g); y += dy

    g, dy = erabar(y, "ЕРА ПОЛЬОВИХ: те саме під новою назвою", POS, "#fdecea"); f.append(g); y += dy
    for year, lines in [
        ("1997", ["Автопром: швидкі щільні MOSFET починають гинути",
                  "в лінійному режимі — усередині паспортної SOA (за звітом NASA)"]),
        ("1999", ["Брельйо, Фрізіна, Магрі, Спіріто (ISPSD, Торонто): теплові мапи —",
                  "гаряча цятка є й у MOSFET, точно як у біполярних"]),
        ("2000", ["Консолі та ін. (IEEE Trans. Power Electron.): «аномальний механізм»,",
                  "якого немає ні в літературі, ні в даташитах виробників"]),
        ("2002", ["Спіріто, Брельйо, д'Алессандро, Рінальді (MIEL, Ніш; ISPSD, Санта-Фе):",
                  "аналітична модель і критерій → нова стіна на кривій SOA"]),
        ("2010", ["NASA (NESC-TB-10-01): «криві SOA від виробників не описували",
                  "області теплової нестійкості»"]),
    ]:
        g, dy = evbox(y, year, lines, POS); f.append(g); y += dy

    render(os.path.join(OUT, "soa-history.svg"), W, H, *f,
           title="Дві ери однієї фізики: як SOA набувала стін")


if __name__ == "__main__":
    fig_soa_map()
    fig_pulsed_soa()
    fig_ztc()
    fig_tc_terms()
    fig_loop_time()
    fig_instability_wall()
    fig_foster_vs_cauer()
    fig_zth_stages()
    fig_guard_trace()
    fig_blind_spot()
    fig_second_breakdown_trace()
    fig_emitter_filament()
    fig_soa_history()
    print("done:", sorted(os.listdir(OUT)))
