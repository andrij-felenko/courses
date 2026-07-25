# -*- coding: utf-8 -*-
"""Фігури до теми «Цілісність живлення (Power Integrity)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math, cmath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head(cx, cy, ang_deg, color, size=8):
    a = math.radians(ang_deg)
    bx, by = math.cos(a), math.sin(a)
    px, py = -by, bx
    x1, y1 = cx - bx * size + px * size * 0.55, cy - by * size + py * size * 0.55
    x2, y2 = cx - bx * size - px * size * 0.55, cy - by * size - py * size * 0.55
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
            % (cx, cy, x1, y1, x2, y2, color))


# ── Фігура 1: просідання напруги в часі ─────────────────────────────────────
def fig_droop():
    W, H = 880, 560
    P = []
    xL, xR = 95, 830
    xstep = 250

    # ── верхня панель: струм мікросхеми ──
    iy0, iy1 = 175, 100          # низький / високий рівень струму
    P.append(text(xL - 5, 66, "струм мікросхеми", size=12.5, color=MUTED, anchor="start", italic=True))
    P.append(line(xL, 200, xR, 200, color="#c9d3dc", sw=1.2))   # базова вісь
    cur = [(xL, iy0), (xstep, iy0), (xstep + 3, iy1), (xR, iy1)]
    P.append(polyline(cur, color=POS, sw=2.6))
    P.append(text(xR - 4, iy1 - 10, "високе споживання", size=11, color=POS, anchor="end"))
    P.append(text(xL + 8, iy0 - 10, "спокій", size=11, color=MUTED, anchor="start"))
    # позначка ривка Δi
    P.append(line(xstep + 22, iy1, xstep + 22, iy0, color=MUTED, sw=1.3, dash="3,3"))
    P.append(head(xstep + 22, iy1, 270, MUTED, size=6))
    P.append(head(xstep + 22, iy0, 90, MUTED, size=6))
    P.append(text(xstep + 30, (iy0 + iy1) / 2 + 4, "Δi за ~1 нс", size=11, color=INK, anchor="start", bold=True))

    # ── нижня панель: напруга на кристалі ──
    ynom = 300           # номінал
    ymin = 470           # нижня межа (збій)
    P.append(text(xL - 5, 262, "напруга на кристалі", size=12.5, color=MUTED, anchor="start", italic=True))
    # номінальна лінія
    P.append(line(xL, ynom, xR, ynom, color="#c9d3dc", sw=1.3, dash="5,4"))
    P.append(text(xR, ynom - 8, "номінал", size=11, color=MUTED, anchor="end"))
    # нижня межа
    P.append(line(xL, ymin, xR, ymin, color=POS, sw=1.6, dash="6,4"))
    P.append(text(xL + 8, ymin + 18, "нижня межа — нижче неї збій", size=11.5, color=POS, anchor="start", bold=True))

    # крива напруги: провал і східчасте відновлення
    volt = [(xL, ynom), (xstep, ynom),
            (xstep + 6, 356), (xstep + 12, 452),   # різкий індуктивний провал
            (xstep + 26, 438),                       # відскок
            (315, 402), (345, 392),                  # кераміка витягує (нс)
            (430, 366), (480, 352),                  # об'ємні (мкс)
            (600, 320), (690, 308), (760, 301), (xR, ynom)]  # стабілізатор (мс)
    P.append(polyline(volt, color=NEG, sw=2.8))

    # вертикальна прив'язка події (обидві панелі)
    P.append(line(xstep, 90, xstep, 452, color=MUTED, sw=1.2, dash="2,4"))

    # підпис провалу
    P.append(text(xstep + 40, 470, "просідання", size=12.5, color=NEG, bold=True, anchor="start"))
    P.append(line(xstep + 38, 464, xstep + 16, 450, color=NEG, sw=1.3))
    P.append(head(xstep + 16, 450, 210, NEG, size=6))

    # запас до межі
    P.append(line(xstep + 12, 452, xstep + 12, ymin, color=FIELD, sw=1.4))
    P.append(head(xstep + 12, 452, 270, FIELD, size=6))
    P.append(head(xstep + 12, ymin, 90, FIELD, size=6))
    P.append(text(xstep - 6, (452 + ymin) / 2 + 4, "запас", size=11, color=FIELD, anchor="end", bold=True))

    # хто витягує на якому масштабі часу
    def stage(x, name, t):
        return (text(x, 512, name, size=11.5, color=INK, bold=True) +
                text(x, 528, t, size=10.5, color=MUTED))
    P.append(stage(345, "кераміка", "наносекунди"))
    P.append(stage(480, "об'ємні C", "мікросекунди"))
    P.append(stage(680, "стабілізатор", "мілісекунди"))
    # легкі роздільники стадій
    for xv in (410, 560):
        P.append(line(xv, 498, xv, 534, color="#e2e8ee", sw=1.0))

    render(os.path.join(IMG, "droop.svg"), W, H, *P,
           title="Ривок струму провалює напругу — резервуари витягують її назад по черзі")


# ── Фігура 2: імпеданс мережі живлення проти частоти ────────────────────────
def fig_pdn_z():
    W, H = 880, 560
    P = []
    # межі поля (лог-лог)
    xL, xR = 100, 830
    yT, yB = 95, 480
    fmin_e, fmax_e = 3, 8          # 1 кГц … 100 МГц (десяткові степені)
    zmin_e, zmax_e = -3, 1         # 1 мОм … 10 Ом

    def X(f):
        return xL + (math.log10(f) - fmin_e) / (fmax_e - fmin_e) * (xR - xL)

    def Y(z):
        z = max(10 ** zmin_e, min(10 ** zmax_e, z))
        return yB - (math.log10(z) - zmin_e) / (zmax_e - zmin_e) * (yB - yT)

    # рамка й сітка
    P.append(rect(xL, yT, xR - xL, yB - yT, fill=BG, stroke="#c9d3dc", sw=1.4))
    xlab = {3: "1 кГц", 4: "10 кГц", 5: "100 кГц", 6: "1 МГц", 7: "10 МГц", 8: "100 МГц"}
    for e in range(fmin_e, fmax_e + 1):
        gx = X(10 ** e)
        P.append(line(gx, yT, gx, yB, color="#eef2f6", sw=1.0))
        P.append(text(gx, yB + 20, xlab[e], size=11, color=MUTED))
    ylab = {-3: "1 мОм", -2: "10 мОм", -1: "100 мОм", 0: "1 Ом", 1: "10 Ом"}
    for e in range(zmin_e, zmax_e + 1):
        gy = Y(10 ** e)
        P.append(line(xL, gy, xR, gy, color="#eef2f6", sw=1.0))
        P.append(text(xL - 10, gy + 4, ylab[e], size=11, color=MUTED, anchor="end"))
    P.append(text(xR, yB + 38, "частота", size=12, color=INK, anchor="end", italic=True))
    P.append(text(xL - 4, yT - 12, "|Z| мережі", size=12, color=INK, anchor="start", italic=True))

    # моделі конденсаторів: Z = ESR + jωL + 1/(jωC)
    def zmag(f, C, L, R):
        w = 2 * math.pi * f
        z = R + 1j * w * L + 1 / (1j * w * C)
        return abs(z)

    bulk = dict(C=100e-6, L=5e-9, R=3e-3)     # об'ємний
    cer = dict(C=1e-6, L=1.5e-9, R=2e-3)      # керамічний

    fs = [10 ** (fmin_e + i * (fmax_e - fmin_e) / 500.0) for i in range(501)]
    pb = [(X(f), Y(zmag(f, **bulk))) for f in fs]
    pc = [(X(f), Y(zmag(f, **cer))) for f in fs]

    def zpar(f):
        w = 2 * math.pi * f
        zb = bulk["R"] + 1j * w * bulk["L"] + 1 / (1j * w * bulk["C"])
        zc = cer["R"] + 1j * w * cer["L"] + 1 / (1j * w * cer["C"])
        return abs(1 / (1 / zb + 1 / zc))
    pp = [(X(f), Y(zpar(f))) for f in fs]

    # окремі «галочки» — блідо
    P.append(polyline(pb, color="#9fb4cf", sw=1.8))
    P.append(polyline(pc, color="#e3a9a2", sw=1.8))
    # спільна крива — жирно
    P.append(polyline(pp, color=INK, sw=3.0))

    # лінія цільового імпедансу
    zt = 10e-3
    P.append(line(xL, Y(zt), xR, Y(zt), color=FIELD, sw=2.2, dash="7,5"))
    P.append(text(xR - 6, Y(zt) - 8, "Z_ціль (стеля)", size=12, color="#1f6e33", anchor="end", bold=True))

    # підписи окремих кривих (на розведених ділянках)
    P.append(text(X(1.7e3), Y(zmag(1.7e3, **bulk)) - 10, "об'ємний C", size=11, color="#5a7397", anchor="start", bold=True))
    P.append(text(X(6e7), Y(zmag(6e7, **cer)) + 18, "керамічний C", size=11, color="#a85b52", anchor="middle", bold=True))

    # SRF-провали
    P.append(text(X(2.25e5), Y(zpar(2.25e5)) + 22, "SRF", size=10.5, color=MUTED))
    P.append(text(X(4.1e6), Y(zpar(4.1e6)) + 22, "SRF", size=10.5, color=MUTED))

    # антирезонансний пік
    fa = 2.25e6
    P.append(text(X(fa), Y(zpar(fa)) - 16, "антирезонанс", size=12, color=POS, bold=True))
    P.append(line(X(fa), Y(zpar(fa)) - 8, X(fa), Y(zpar(fa)) - 2, color=POS, sw=1.4))
    P.append(head(X(fa), Y(zpar(fa)) - 2, 90, POS, size=6))

    # хто тримає краї смуги
    P.append(text(X(1.3e3), yT + 20, "← стабілізатор", size=10.5, color=MUTED, anchor="start"))
    P.append(text(X(8e7), yT + 20, "кристал →", size=10.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "pdn-z.svg"), W, H, *P,
           title="Імпеданс мережі живлення: спільна крива має триматися під стелею Z_ціль")


# ── Фігура 3: історія — колапс цільового імпедансу крізь 1990-ті ─────────────
def fig_ti_history():
    W, H = 900, 660
    P = []
    xL, xR = 120, 812
    y0, y1 = 1993, 2000

    def X(yr):
        return xL + (yr - y0) / (y1 - y0) * (xR - xL)

    Atop, Abot = 100, 250          # панель напруги (лінійна)
    Btop, Bbot = 356, 512          # панель імпедансу (логарифмічна)

    def YA(v):
        return Abot - (v / 5.5) * (Abot - Atop)

    def YB(z):
        return Bbot - (math.log10(z) + 3) / 3 * (Bbot - Btop)

    # ── спільна сітка років ──
    for yr in range(y0, y1 + 1):
        gx = X(yr)
        P.append(line(gx, Atop, gx, Bbot, color="#eef2f6", sw=1.0))
        P.append(text(gx, Bbot + 22, str(yr), size=11, color=MUTED))
    P.append(text(xR, Bbot + 42, "рік", size=12, color=INK, anchor="end", italic=True))

    # ── панель А: напруга ядра ──
    P.append(text(xL - 8, 74, "напруга ядра CMOS (В)", size=12.5, color=INK, anchor="start", italic=True))
    P.append(text(xR, 90, "тактова частота ↑", size=11, color=MUTED, anchor="end"))
    for v in (5, 3.3, 1.8):
        gy = YA(v)
        P.append(line(xL, gy, xR, gy, color="#f2f5f8", sw=1.0))
        lab = ("%.1f" % v).rstrip("0").rstrip(".")
        P.append(text(xL - 10, gy + 4, lab, size=10.5, color=MUTED, anchor="end"))
    P.append(line(xL, Abot, xR, Abot, color="#c9d3dc", sw=1.2))
    volt = [(1993, 5.0), (1994, 3.3), (1996, 3.3), (1997, 2.8), (1999, 2.0), (2000, 1.7)]
    vp = [(X(a), YA(b)) for a, b in volt]
    P.append(polyline(vp, color=NEG, sw=2.8))
    for a, b in volt:
        P.append(circle(X(a), YA(b), 3.4, fill=BG, stroke=NEG, sw=2))
    clk = [(1993, "66 МГц", "start", 4), (1994, "100 МГц", "middle", 0),
           (1997, "233 МГц", "middle", 0), (2000, "1 ГГц", "end", -4)]
    vd = dict(volt)
    for a, lab, anch, dx in clk:
        P.append(text(X(a) + dx, YA(vd[a]) + 16, lab, size=10.5, color=INK, anchor=anch, bold=True))

    # ── панель Б: потрібний цільовий імпеданс (лог) ──
    P.append(text(xL - 8, 336, "потрібний Z_ціль (Ом, лог. шкала)", size=12.5, color=INK, anchor="start", italic=True))
    zlab = {-3: "1 мОм", -2: "10 мОм", -1: "100 мОм", 0: "1 Ом"}
    for e in range(-3, 1):
        gy = YB(10 ** e)
        P.append(line(xL, gy, xR, gy, color="#f2f5f8", sw=1.0))
        P.append(text(xL - 10, gy + 4, zlab[e], size=10.5, color=MUTED, anchor="end"))
    zpts = [(1993, 0.25), (1994, 0.15), (1996, 0.09), (1997, 0.05), (1999, 0.015), (2000, 0.008)]
    zp = [(X(a), YB(b)) for a, b in zpts]
    P.append(polyline(zp, color=POS, sw=3.0))
    for a, b in zpts:
        P.append(circle(X(a), YB(b), 3.4, fill=BG, stroke=POS, sw=2))

    # підпис колапсу (у порожньому лівому низу панелі Б)
    P.append(text(xL + 6, 500, "≈250 мОм → ≈8 мОм: у ~30 разів нижче за 7 років", size=11.5,
                  color="#8a2a20", anchor="start", bold=True))

    # маркер 1999 — рік формалізації методу
    xm = X(1999)
    P.append(line(xm, Atop, xm, Bbot, color=MUTED, sw=1.3, dash="4,4"))
    P.append(text(xm - 6, 92, "1999 — метод Z_ціль (Sun)", size=11, color=INK, anchor="end", bold=True))

    render(os.path.join(IMG, "ti-history.svg"), W, H, *P,
           title="Чому знадобилося одне число: колапс цільового імпедансу в 1990-х")


# ── Фігура 4: калькулятор — наївна мережа проти виправленої ──────────────────
def fig_pdn_calc():
    W, H = 900, 580
    P = []
    xL, xR = 120, 848
    yT, yB = 96, 466
    fmin_e, fmax_e = 3, 8          # 1 кГц … 100 МГц
    zmin_e, zmax_e = -3, 0         # 1 мОм … 1 Ом

    def X(f):
        return xL + (math.log10(f) - fmin_e) / (fmax_e - fmin_e) * (xR - xL)

    def Y(z):
        z = max(10 ** zmin_e, min(10 ** zmax_e, z))
        return yB - (math.log10(z) - zmin_e) / (zmax_e - zmin_e) * (yB - yT)

    # рамка й сітка
    P.append(rect(xL, yT, xR - xL, yB - yT, fill=BG, stroke="#c9d3dc", sw=1.4))
    xlab = {3: "1 кГц", 4: "10 кГц", 5: "100 кГц", 6: "1 МГц", 7: "10 МГц", 8: "100 МГц"}
    for e in range(fmin_e, fmax_e + 1):
        gx = X(10 ** e)
        P.append(line(gx, yT, gx, yB, color="#eef2f6", sw=1.0))
        P.append(text(gx, yB + 20, xlab[e], size=11, color=MUTED))
    ylab = {-3: "1 мОм", -2: "10 мОм", -1: "100 мОм", 0: "1 Ом"}
    for e in range(zmin_e, zmax_e + 1):
        gy = Y(10 ** e)
        P.append(line(xL, gy, xR, gy, color="#eef2f6", sw=1.0))
        P.append(text(xL - 10, gy + 4, ylab[e], size=11, color=MUTED, anchor="end"))
    P.append(text(xR, yB + 40, "частота", size=12, color=INK, anchor="end", italic=True))
    P.append(text(xL - 4, yT - 12, "|Z| мережі", size=12, color=INK, anchor="start", italic=True))

    # та сама модель, що й у скрипті
    vrm = dict(r=2e-3, l=6.4e-9)

    def zmag(f, elems):
        w = 2 * math.pi * f
        Y_ = 1.0 / (vrm["r"] + 1j * w * vrm["l"])
        for C, esr, L, q in elems:
            Y_ += q / (esr + 1j * w * L + 1.0 / (1j * w * C))
        return abs(1.0 / Y_)

    naive = [(100e-6, 5e-3, 3.5e-9, 1), (100e-9, 40e-3, 2.0e-9, 10)]
    fixed = [(100e-6, 5e-3, 2.8e-9, 2), (10e-6, 3e-3, 1.6e-9, 6),
             (1e-6, 8e-3, 1.4e-9, 12), (100e-9, 40e-3, 1.3e-9, 24)]

    fs = [10 ** (fmin_e + i * (fmax_e - fmin_e) / 600.0) for i in range(601)]
    pn = [(X(f), Y(zmag(f, naive))) for f in fs]
    pf = [(X(f), Y(zmag(f, fixed))) for f in fs]

    # межа плати 50 МГц (за нею естафету бере кристал)
    x50 = X(50e6)
    P.append(line(x50, yT, x50, yB, color=MUTED, sw=1.2, dash="3,4"))
    P.append(text(x50 - 8, yB - 10, "межа плати →", size=10, color=MUTED, anchor="end", italic=True))
    P.append(text(x50 + 8, yB - 10, "кристал", size=10, color=MUTED, anchor="start", italic=True))

    # лінія цілі
    zt = 10e-3
    P.append(line(xL, Y(zt), xR, Y(zt), color=FIELD, sw=2.2, dash="7,5"))
    P.append(text(xR - 8, Y(zt) + 18, "Z_ціль = 10 мОм (стеля)", size=11.5, color="#1f6e33", anchor="end", bold=True))

    # криві
    P.append(polyline(pn, color=POS, sw=2.8))
    P.append(polyline(pf, color=NEG, sw=2.8))

    # пік наївної мережі
    fa = 3.21e6
    yp = Y(zmag(fa, naive))
    P.append(line(X(fa), yp - 6, X(fa), yp - 40, color=POS, sw=1.3))
    P.append(head(X(fa), yp - 6, 90, POS, size=6))
    P.append(text(X(fa), yp - 48, "антирезонанс 328 мОм", size=12, color=POS, bold=True))
    P.append(text(X(fa), yp - 64, "33× над ціллю — FAIL", size=11, color=POS))

    # підпис виправленої (на пласкій ділянці)
    P.append(text(X(3.5e4), Y(zmag(3.5e4, fixed)) + 22, "виправлена: 44 конд. — PASS", size=12, color=NEG, bold=True))

    # легенда
    lx, ly = xL + 16, yT + 18
    P.append(line(lx, ly, lx + 26, ly, color=POS, sw=2.8))
    P.append(text(lx + 34, ly + 4, "наївна (1×100 мкФ + 10×100 нФ)", size=10.5, color=INK, anchor="start"))
    P.append(line(lx, ly + 20, lx + 26, ly + 20, color=NEG, sw=2.8))
    P.append(text(lx + 34, ly + 24, "виправлена (місток за номіналами)", size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "pdn-calc.svg"), W, H, *P,
           title="Калькулятор PDN: наївна мережа пробиває ціль, виправлена тримається під нею")


# ── Спільна модель пари конденсаторів (для math-вставки) ─────────────────────
# великий 100 мкФ (L₁=5 нГн, ESR=3 мОм) + малий 1 мкФ (L₂=1.5 нГн, ESR=2 мОм)
_BIG = dict(C=100e-6, L=5e-9, R=3e-3)
_SML = dict(C=1e-6, L=1.5e-9, R=2e-3)


def _zc(f, C, L, R):
    w = 2 * math.pi * f
    return R + 1j * w * L + 1.0 / (1j * w * C)


def _logframe(P, xL, xR, yT, yB, fmin_e, fmax_e, zmin_e, zmax_e):
    """Рамка й лог-лог сітка з підписами; повертає (X, Y)."""
    def X(f):
        return xL + (math.log10(f) - fmin_e) / (fmax_e - fmin_e) * (xR - xL)

    def Y(z):
        z = max(10 ** zmin_e, min(10 ** zmax_e, z))
        return yB - (math.log10(z) - zmin_e) / (zmax_e - zmin_e) * (yB - yT)

    P.append(rect(xL, yT, xR - xL, yB - yT, fill=BG, stroke="#c9d3dc", sw=1.4))
    xlab = {4: "10 кГц", 5: "100 кГц", 6: "1 МГц", 7: "10 МГц", 8: "100 МГц"}
    for e in range(fmin_e, fmax_e + 1):
        gx = X(10 ** e)
        P.append(line(gx, yT, gx, yB, color="#eef2f6", sw=1.0))
        P.append(text(gx, yB + 20, xlab[e], size=11, color=MUTED))
    ylab = {-3: "1 мОм", -2: "10 мОм", -1: "100 мОм", 0: "1 Ом", 1: "10 Ом"}
    for e in range(zmin_e, zmax_e + 1):
        gy = Y(10 ** e)
        P.append(line(xL, gy, xR, gy, color="#eef2f6", sw=1.0))
        P.append(text(xL - 10, gy + 4, ylab[e], size=11, color=MUTED, anchor="end"))
    P.append(text(xR, yB + 38, "частота", size=12, color=INK, anchor="end", italic=True))
    P.append(text(xL - 4, yT - 12, "|Z| пари", size=12, color=INK, anchor="start", italic=True))
    return X, Y


# ── Фігура 5: побудова антирезонансу з двох галочок ──────────────────────────
def fig_anti_build():
    W, H = 880, 560
    P = []
    xL, xR, yT, yB = 100, 830, 95, 470
    X, Y = _logframe(P, xL, xR, yT, yB, 4, 7, -3, 1)   # 10 кГц … 10 МГц

    fs = [10 ** (4 + i * 3 / 600.0) for i in range(601)]
    L1, C2 = _BIG["L"], _SML["C"]

    def zpar(f):
        return abs(1.0 / (1.0 / _zc(f, **_BIG) + 1.0 / _zc(f, **_SML)))

    # окремі галочки — блідо
    P.append(polyline([(X(f), Y(abs(_zc(f, **_BIG)))) for f in fs], color="#9fb4cf", sw=1.8))
    P.append(polyline([(X(f), Y(abs(_zc(f, **_SML)))) for f in fs], color="#e3a9a2", sw=1.8))

    # асимптоти-прямі (у лог-лог — прямі): +ωL₁ великого та 1/ωC₂ малого
    P.append(polyline([(X(f), Y(2 * math.pi * f * L1)) for f in fs],
                      color="#5a7397", sw=1.7, dash="6,5"))
    P.append(polyline([(X(f), Y(1.0 / (2 * math.pi * f * C2))) for f in fs],
                      color="#a85b52", sw=1.7, dash="6,5"))

    # спільна крива — жирно
    zp = [zpar(f) for f in fs]
    P.append(polyline([(X(f), Y(z)) for f, z in zip(fs, zp)], color=INK, sw=3.0))

    # точка перетину асимптот = характеристичний опір Z₀
    fa = 1.0 / (2 * math.pi * math.sqrt(L1 * C2))
    Z0 = math.sqrt(L1 / C2)
    P.append(line(xL, Y(Z0), X(fa), Y(Z0), color=FIELD, sw=1.4, dash="3,4"))
    P.append(circle(X(fa), Y(Z0), 4.4, fill=BG, stroke=FIELD, sw=2.4))
    P.append(text(X(1.1e5), Y(Z0) - 20, "Z₀ = √(L₁/C₂) ≈ 71 мОм", size=11.5,
                  color="#1f6e33", anchor="start", bold=True))

    # підписи асимптот (уздовж похилих, у розведених кутах)
    P.append(text(X(5.5e6), Y(2 * math.pi * 5.5e6 * L1) - 11, "+ωL₁ (велика котушка)",
                  size=11, color="#5a7397", anchor="middle", bold=True))
    P.append(text(X(2.4e4), Y(1.0 / (2 * math.pi * 2.4e4 * C2)) + 14, "1/ωC₂ (мала ємність)",
                  size=11, color="#a85b52", anchor="start", bold=True))

    # підписи галочок: великий — на лівій ємнісній вітці, малий — на правій індуктивній
    P.append(text(X(1.25e4), Y(abs(_zc(1.25e4, **_BIG))) + 19, "великий 100 мкФ",
                  size=10.5, color="#5a7397", anchor="start"))
    P.append(text(X(8.5e6), Y(abs(_zc(8.5e6, **_SML))) + 19, "малий 1 мкФ",
                  size=10.5, color="#a85b52", anchor="end"))

    # пік антирезонансу (у справжньому максимумі спільної кривої)
    ip = max(range(len(fs)), key=lambda i: zp[i])
    P.append(text(X(fs[ip]), Y(zp[ip]) - 30, "антирезонанс", size=12.5, color=POS, bold=True))
    P.append(text(X(fs[ip]), Y(zp[ip]) - 15, "|Z| ≈ Q·Z₀", size=11, color=POS))
    P.append(line(X(fs[ip]), Y(zp[ip]) - 10, X(fs[ip]), Y(zp[ip]) - 3, color=POS, sw=1.4))
    P.append(head(X(fs[ip]), Y(zp[ip]) - 3, 90, POS, size=6))

    render(os.path.join(IMG, "anti-build.svg"), W, H, *P,
           title="Антирезонанс росте там, де індуктивна вітка одного зустрічає ємнісну іншого")


# ── Фігура 6: висота піка за трьох значень ESR ───────────────────────────────
def fig_anti_damp():
    W, H = 880, 560
    P = []
    xL, xR, yT, yB = 100, 830, 95, 470
    X, Y = _logframe(P, xL, xR, yT, yB, 5, 7, -3, 1)   # 100 кГц … 10 МГц (навколо піка)

    fs = [10 ** (5 + i * 2 / 800.0) for i in range(801)]
    Z0 = math.sqrt(_BIG["L"] / _SML["C"])

    def zpar(f, k):
        zb = _zc(f, _BIG["C"], _BIG["L"], _BIG["R"] * k)
        zs = _zc(f, _SML["C"], _SML["L"], _SML["R"] * k)
        return abs(1.0 / (1.0 / zb + 1.0 / zs))

    # рівень Z₀ — куди ESR притискає пік
    P.append(line(xL, Y(Z0), xR, Y(Z0), color=FIELD, sw=2.0, dash="7,5"))
    P.append(text(xL + 8, Y(Z0) + 19, "Z₀ = √(L₁/C₂) ≈ 71 мОм — сюди тисне ESR",
                  size=11.5, color="#1f6e33", anchor="start", bold=True))

    # три криві: множник ESR 1 / 3 / 14  →  Q ≈ 14 / 4.7 / 1
    cases = [(1.0, POS, "Q ≈ 14", "малий ESR (5 мОм) — чиста кераміка"),
             (3.0, "#c98a2b", "Q ≈ 4.7", "утричі більший ESR (15 мОм)"),
             (14.0, NEG, "Q ≈ 1", "×14 ESR (70 мОм) — майже не дзвенить")]
    for k, col, qlab, _ in cases:
        z = [zpar(f, k) for f in fs]
        P.append(polyline([(X(f), Y(zz)) for f, zz in zip(fs, z)], color=col, sw=2.6))
        ip = max(range(len(fs)), key=lambda i: z[i])
        P.append(text(X(fs[ip]) - 8, Y(z[ip]) - 20, qlab, size=11.5, color=col,
                      bold=True, anchor="end"))

    # стрілка «більший ESR тисне пік донизу» (праворуч від піків, у чистому місці)
    xa = X(4.2e6)
    P.append(line(xa, Y(0.62), xa, Y(0.095), color=MUTED, sw=1.5))
    P.append(head(xa, Y(0.095), 90, MUTED, size=6.5))
    P.append(text(xa + 9, (Y(0.62) + Y(0.095)) / 2, "↑ESR ⇒ нижчий пік",
                  size=10.5, color=MUTED, anchor="start", italic=True))

    # легенда
    lx, ly = xL + 18, yT + 16
    for i, (k, col, qlab, lab) in enumerate(cases):
        yy = ly + i * 19
        P.append(line(lx, yy, lx + 26, yy, color=col, sw=2.8))
        P.append(text(lx + 34, yy + 4, lab, size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "anti-damp.svg"), W, H, *P,
           title="Та сама пара, три ESR: чим чистіші конденсатори, тим вищий і гостріший пік")


if __name__ == "__main__":
    fig_droop()
    fig_pdn_z()
    fig_ti_history()
    fig_pdn_calc()
    fig_anti_build()
    fig_anti_damp()
    print("written:", IMG)
