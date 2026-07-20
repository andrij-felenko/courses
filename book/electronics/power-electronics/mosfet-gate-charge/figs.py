# -*- coding: utf-8 -*-
"""Фігури для статті «Заряд затвора MOSFET і час перемикання».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── карта заряду: угорі Vgs(Q), унизу Id та Vds на тій самій осі заряду ──────────
# Серце теми. Кожна ділянка заряду = окрема фаза переходу:
# Qgs — струм наростає; Qgd (плато Міллера) — напруга стоку валиться; перезаряд — Rds(on).
def fig_gate_charge_map():
    W, H = 800, 570
    L, R = 108, 706
    tT, tB = 84, 252          # верхня панель — Vgs
    bT, bB = 328, 492         # нижня панель — Id, Vds
    span = R - L
    fth, fq1, fq2 = 0.15, 0.34, 0.66     # межі: поріг, кінець Qgs, кінець плато
    vth, vpl, vdr = 0.34, 0.50, 0.92     # рівні напруги затвора (нормовані)

    def X(fq): return L + fq * span
    def Yt(v): return tB - v * (tB - tT)
    def Yb(v): return bB - v * (bB - bT)

    p = []
    # смуга плато крізь обидві панелі (найдорожча фаза)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fbe9e7" stroke="none"/>'
             % (X(fq1), tT, X(fq2) - X(fq1), bB - tT))

    # заголовки панелей
    p.append(text(L, tT - 18, "Напруга на затворі  Vgs", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(L, bT - 16, "Стік:  струм Id  і  напруга Vds", size=13, color=INK, bold=True, anchor="start"))

    # осі
    p.append(line(L, tT, L, tB, color=INK, sw=2))
    p.append(line(L, tB, R + 10, tB, color=INK, sw=2))
    p.append(line(L, bT, L, bB, color=INK, sw=2))
    p.append(line(L, bB, R + 10, bB, color=INK, sw=2))
    p.append(text(R + 8, bB + 24, "заряд Qg →", size=12, color=INK, italic=True, anchor="end"))

    # крива Vgs
    def vgs(fq):
        if fq <= fth: return (fq / fth) * vth
        if fq <= fq1: return vth + (fq - fth) / (fq1 - fth) * (vpl - vth)
        if fq <= fq2: return vpl
        return vpl + (fq - fq2) / (1 - fq2) * (vdr - vpl)

    fs = [i / 240.0 for i in range(0, 241)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Yt(vgs(f))) for f in fs), INK))

    # рівні напруги — пунктир + підпис ліворуч
    for v, lab in [(vth, "Vth"), (vpl, "Vpl"), (vdr, "Vdrive")]:
        p.append(line(L, Yt(v), R, Yt(v), color=MUTED, sw=1.0, dash="4,4"))
        p.append(text(L - 10, Yt(v) + 4, lab, size=11, color=MUTED, anchor="end"))

    # нижні криві: Id (наростає в Qgs) і Vds (валиться на плато)
    def idc(fq):
        if fq <= fth: return 0.0
        if fq <= fq1: return (fq - fth) / (fq1 - fth)
        return 1.0

    def vds(fq):
        if fq <= fq1: return 1.0
        if fq <= fq2: return 1.0 - (fq - fq1) / (fq2 - fq1) * (1.0 - 0.06)
        return 0.06

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Yb(vds(f))) for f in fs), FIELD))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Yb(idc(f))) for f in fs), NEG))
    p.append(text(X(0.05), Yb(1.0) + 18, "Vds", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(X(0.90), Yb(1.0) + 18, "Id", size=12, color=NEG, bold=True, anchor="start"))

    # вертикальні пунктирні межі крізь обидві панелі
    for fb in [fth, fq1, fq2]:
        p.append(line(X(fb), tT, X(fb), bB, color=MUTED, sw=1.0, dash="3,4"))

    # підписи ділянок під нижньою панеллю (в проміжках, повз лінії)
    def reglab(fa, fb, l1, l2):
        cx = X((fa + fb) / 2)
        p.append(text(cx, bB + 42, l1, size=12, color=INK, bold=True))
        p.append(text(cx, bB + 60, l2, size=11, color=MUTED))

    reglab(0.0, fq1, "Qgs", "струм наростає")
    reglab(fq1, fq2, "Qgd — плато Міллера", "напруга валиться")
    reglab(fq2, 1.0, "перезаряд", "Rds(on) добиває")

    render(os.path.join(OUT, "gate-charge-map.svg"), W, H, *p,
           title="Крива заряду затвора — карта переходу")


# ── механізм плато: увесь струм затвора йде в Cgd, поки Vds валиться ─────────────
# Ідея: Cgd з'єднує затвор із падаючим стоком; поки Vds валиться, весь Ig годує Cgd,
# а не піднімає Vgs — тому затвор «прибитий» до Vpl = Vth + Id/gm.
def fig_plateau_mechanism():
    W, H = 780, 440
    p = []

    Gx, Gy = 372, 176            # вузол затвора
    Dx = 566                     # вузол стоку
    rail = 322                   # витік (нижня шина)

    def cap_h(cx, cy, lab, labside="up"):
        """Горизонтальна ємність (пластини вертикальні) на горизонтальному дроті."""
        out = [line(cx - 5, cy - 15, cx - 5, cy + 15, color=INK, sw=3),
               line(cx + 5, cy - 15, cx + 5, cy + 15, color=INK, sw=3)]
        if labside == "up":
            out.append(text(cx, cy - 24, lab, size=12, color=INK, bold=True))
        else:
            out.append(text(cx + 22, cy + 4, lab, size=12, color=INK, bold=True, anchor="start"))
        return out

    def cap_v(cx, cy, lab):
        """Вертикальна ємність (пластини горизонтальні) на вертикальному дроті."""
        out = [line(cx - 15, cy - 5, cx + 15, cy - 5, color=INK, sw=3),
               line(cx - 15, cy + 5, cx + 15, cy + 5, color=INK, sw=3),
               text(cx + 22, cy + 4, lab, size=12, color=INK, bold=True, anchor="start")]
        return out

    # драйвер
    p.append(fitbox(58, 150, 96, 54, "драйвер\nVdrive", size=12, fill="#eaf0fd",
                    stroke=NEG, color=NEG, bold=True))
    # драйвер → Rg → затвор
    p.append(line(154, Gy, 196, Gy, color=INK, sw=2))
    p.append(rect(196, Gy - 15, 60, 30, fill=FILL, stroke=INK, sw=1.8, rx=5))
    p.append(text(226, Gy + 4, "Rg", size=12, color=INK, bold=True))
    p.append(line(256, Gy, Gx, Gy, color=INK, sw=2))
    # струм Ig
    p.append(arrow(286, Gy - 34, 336, Gy - 34, color=POS, sw=2.2))
    p.append(text(311, Gy - 42, "Ig", size=12, color=POS, bold=True))

    # вузол затвора
    p.append(circle(Gx, Gy, 4, fill=INK, stroke=INK))
    p.append(text(Gx - 12, Gy + 22, "затвор", size=11, color=MUTED, anchor="end"))

    # Cgs: затвор → витік (донизу)
    p.append(line(Gx, Gy, Gx, rail, color=INK, sw=2))
    p += cap_v(Gx, (Gy + rail) / 2 + 6, "Cgs")
    # шина витоку + земля
    p.append(line(150, rail, Dx, rail, color=INK, sw=2))
    p.append(line(Dx - 16, rail, Dx - 16, rail, color=INK, sw=2))
    for i, wdt in enumerate([26, 16, 8]):
        p.append(line(Gx - wdt / 2, rail + 8 + i * 5, Gx + wdt / 2, rail + 8 + i * 5, color=INK, sw=2))
    p.append(line(Gx, rail, Gx, rail + 6, color=INK, sw=2))

    # Cgd: затвор → стік (праворуч), гарячий шлях струму
    p.append(line(Gx, Gy, Dx, Gy, color=POS, sw=3))
    p.append(arrow(Gx + 16, Gy, Gx + 68, Gy, color=POS, sw=2.4))
    p += cap_h((Gx + Dx) / 2, Gy, "Cgd (Міллерова)")
    p.append(text(Gx + 120, Gy + 34, "весь Ig — у Cgd", size=11, color=POS, bold=True, anchor="start"))

    # вузол стоку + падіння Vds
    p.append(circle(Dx, Gy, 4, fill=INK, stroke=INK))
    p.append(line(Dx, Gy, Dx, 96, color=INK, sw=2))
    p.append(text(Dx, 86, "стік", size=11, color=MUTED))
    p.append(arrow(Dx + 44, 120, Dx + 44, 250, color=FIELD, sw=2.6))
    p.append(text(Dx + 54, 190, "Vds", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(Dx + 54, 208, "валиться", size=11, color=FIELD, anchor="start"))

    # нижні пояснення — рамками (textbox/fitbox)
    p.append(fitbox(70, 356, 400, 62,
                    "Плато: Vds падає → крізь Cgd тече весь струм\nзатвора → напруга на Cgs (тобто Vgs) завмерла",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    p.append(fitbox(492, 356, 216, 62,
                    "Ig = Cgd · dV/dt\nVpl = Vth + Id/gm",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(OUT, "plateau-mechanism.svg"), W, H, *p,
           title="Чому напруга затвора завмирає на плато Міллера")


# ── перехід у часі: Vgs, Id, Vds і спалах потужності на чотирьох фазах ───────────
# Ідея: той самий перехід по осі часу; спалах P = Vds·Id — на наростанні струму й на
# плато (перекидання напруги), тож саме ці дві фази й треба вкоротити.
def fig_transition_timeline():
    W, H = 800, 476
    L, R = 108, 706
    T, B = 78, 336
    span = R - L
    t1, t2, t3, t4 = 0.12, 0.30, 0.58, 0.72     # межі фаз
    vth, vpl, vdr = 0.30, 0.55, 0.95

    def X(f): return L + f * span
    def Y(v): return B - v * (B - T)

    def vgs(f):
        if f <= t1: return f / t1 * vth
        if f <= t2: return vth + (f - t1) / (t2 - t1) * (vpl - vth)
        if f <= t3: return vpl
        if f <= t4: return vpl + (f - t3) / (t4 - t3) * (vdr - vpl)
        return vdr

    def idc(f):
        if f <= t1: return 0.0
        if f <= t2: return (f - t1) / (t2 - t1)
        return 1.0

    def vds(f):
        if f <= t2: return 1.0
        if f <= t3: return 1.0 - (f - t2) / (t3 - t2) * (1.0 - 0.04)
        return 0.04

    def powr(f): return 0.9 * vds(f) * idc(f)

    p = []
    # осі
    p.append(line(L, T - 6, L, B, color=INK, sw=2))
    p.append(line(L, B, R + 10, B, color=INK, sw=2))
    p.append(text(R + 8, B + 24, "час →", size=12, color=INK, italic=True, anchor="end"))

    # смуги двох «гарячих» фаз (наростання струму + плато)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdf3f2" stroke="none"/>'
             % (X(t1), T - 6, X(t3) - X(t1), B - (T - 6)))

    fs = [i / 300.0 for i in range(0, 301)]
    # спалах потужності — заливка + контур
    poly = ["%.1f,%.1f" % (X(t1), Y(0))]
    poly += ["%.1f,%.1f" % (X(f), Y(powr(f))) for f in fs if t1 <= f <= t3]
    poly.append("%.1f,%.1f" % (X(t3), Y(0)))
    p.append('<polygon points="%s" fill="#fbe0dc" stroke="none"/>' % " ".join(poly))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Y(powr(f))) for f in fs), POS))

    # криві
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Y(vds(f))) for f in fs), FIELD))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Y(idc(f))) for f in fs), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % (X(f), Y(vgs(f))) for f in fs), INK))

    # підписи кривих у чистих місцях
    p.append(text(X(0.44), Y(vpl) + 16, "Vgs", size=12, color=INK, bold=True))
    p.append(text(X(0.05), Y(1.0) - 8, "Vds", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(X(0.90), Y(1.0) - 8, "Id", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(X(0.205), Y(powr(t2)) - 12, "P = Vds·Id", size=12, color=POS, bold=True))

    # фазовий рядок під віссю
    for tb in [t1, t2, t3, t4]:
        p.append(line(X(tb), B, X(tb), B + 8, color=INK, sw=1.2))

    def phlab(fa, fb, l1, l2):
        cx = X((fa + fb) / 2)
        p.append(text(cx, B + 42, l1, size=11, color=INK, bold=True))
        p.append(text(cx, B + 59, l2, size=10, color=MUTED))

    phlab(0.0, t1, "t_d", "затримка")
    phlab(t1, t2, "t_ri", "струм ↑")
    phlab(t2, t3, "t_fv", "напруга ↓ (плато)")
    phlab(t3, t4, "t_ov", "перезаряд")

    render(os.path.join(OUT, "transition-timeline.svg"), W, H, *p,
           title="Перехід у часі: спалах потужності на струмі й на плато")


# ── звідки Vpl: лінеаризована передатна крива Id(Vgs) ────────────────────────
# Для вставки math-switching-phases. Ідея: у насиченні Id ≈ gm·(Vgs−Vth) — пряма
# від порога з нахилом gm. Навантаження фіксує Id, тож Vgs пришпилений: обертаємо
# пряму на рівні струму навантаження → Vpl = Vth + Id/gm. Прямокутний трикутник:
# горизонтальний катет (Vpl−Vth) = Id/gm.
def fig_transfer_plateau():
    W, H = 780, 430
    L, Rx = 122, 520          # вісь Vgs: 0..6 В
    T, B = 74, 340            # вісь Id: верх .. нуль
    Vmax = 6.0
    vth, vpl = 3.0, 4.0
    hload = 0.58 * (B - T)    # висота рівня струму навантаження в пікселях
    fcap = (B - T) / hload    # максимальна частка f, що ще влазить у панель

    def X(v): return L + v / Vmax * (Rx - L)
    def Yid(f): return B - f * hload        # f у одиницях I_load (1.0 = навантаження)

    p = []
    # осі
    p.append(line(L, T - 6, L, B, color=INK, sw=2))
    p.append(line(L, B, Rx + 60, B, color=INK, sw=2))
    p.append(text(Rx + 58, B + 24, "Vgs →", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(L - 12, T + 4, "Id ↑", size=12, color=INK, italic=True, anchor="end"))

    # реальна (квадратична) передатна крива — блідо, «як воно насправді»
    sq = []
    v = vth
    while v <= vpl + 0.05:
        f = ((v - vth) / (vpl - vth)) ** 2
        if f <= fcap:
            sq.append("%.1f,%.1f" % (X(v), Yid(f)))
        v += 0.03
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.7" stroke-dasharray="2,3"/>'
             % (" ".join(sq), MUTED))
    p.append(text(X(4.28), Yid(0.42), "реальна крива", size=10, color=MUTED, anchor="start"))
    p.append(text(X(4.28), Yid(0.42) + 14, "Id ≈ k(Vgs−Vth)²", size=10, color=MUTED, anchor="start"))

    # лінеаризація: пряма від (Vth,0) з нахилом gm, що проходить (Vpl, I_load)
    fend = 1.62                       # де обірвати пряму, щоб не вилізла вгору
    vend = vth + fend * (vpl - vth)
    p.append(line(X(vth), Yid(0.0), X(vend), Yid(fend), color=INK, sw=3))
    p.append(text(X(4.75), 100, "Id ≈ gm·(Vgs−Vth)", size=12, color=INK, bold=True, anchor="start"))

    # рівень струму навантаження
    p.append(line(L, Yid(1.0), X(vpl), Yid(1.0), color=NEG, sw=1.4, dash="5,4"))
    p.append(text(L - 10, Yid(1.0) + 4, "Id", size=12, color=NEG, bold=True, anchor="end"))
    p.append(text(X(1.05), Yid(1.0) - 9, "струм навантаження", size=11, color=NEG, anchor="middle"))

    # обертання: униз від робочої точки на Vpl
    p.append(line(X(vpl), Yid(1.0), X(vpl), B, color=FIELD, sw=1.6, dash="5,4"))
    p.append(circle(X(vpl), Yid(1.0), 4.5, fill=FIELD, stroke=FIELD))

    # прямокутний трикутник Vth→Vpl (горизонтальний катет = Id/gm)
    p.append(line(X(vth), B, X(vpl), B, color=FIELD, sw=3))
    p.append(arrow(X(vth) + 3, B - 15, X(vpl) - 3, B - 15, color=FIELD, sw=1.6))
    p.append(arrow(X(vpl) - 3, B - 15, X(vth) + 3, B - 15, color=FIELD, sw=1.6))
    p.append(text((X(vth) + X(vpl)) / 2, B - 22, "Id/gm", size=12, color=FIELD, bold=True))

    # позначки Vth, Vpl на осі
    for v, lab, col in [(vth, "Vth", INK), (vpl, "Vpl", FIELD)]:
        p.append(line(X(v), B - 4, X(v), B + 5, color=col, sw=2))
        p.append(text(X(v), B + 22, lab, size=12, color=col, bold=True))

    # висновок-рамка
    p.append(fitbox(Rx + 84, 156, 152, 70,
                    "Vpl = Vth + Id/gm\n(Vgs, за якої канал\nведе саме Id)",
                    size=12, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(OUT, "transfer-plateau.svg"), W, H, *p,
           title="Звідки береться напруга плато: обертаємо передатну криву")


# ── асиметрія: рушійна напруга затвора на плато при вмиканні й вимиканні ──────
# На вмиканні драйвер штовхає затвор угору «залишком» (Vdrive − Vpl); на вимиканні
# тягне вниз усім Vpl. Довжина стрілки = напруга на Rg = струм затвора на плато.
def fig_drive_asymmetry():
    W, H = 820, 430
    Cx = 412
    yB, yT = 356, 78          # Vgs = 0 .. Vdrive
    Vdrive, vth, vpl = 10.0, 3.0, 4.0

    def Y(v): return yB - v / Vdrive * (yB - yT)

    p = []
    # вертикальна шкала Vgs
    p.append(line(Cx, yT - 6, Cx, yB + 8, color=INK, sw=2))
    p.append(text(Cx, yT - 14, "Vgs", size=13, color=INK, bold=True))
    for v, lab in [(0, "0"), (vth, "Vth"), (vpl, "Vpl"), (Vdrive, "Vdrive")]:
        p.append(line(Cx - 5, Y(v), Cx + 5, Y(v), color=INK, sw=2))
        p.append(text(Cx + 12, Y(v) + 4, lab, size=11, color=MUTED, anchor="start"))

    # рівень плато — тонка лінія через усе
    p.append(line(150, Y(vpl), 680, Y(vpl), color=MUTED, sw=1.0, dash="4,5"))

    # ── ВМИКАННЯ: штовхає від Vpl угору до Vdrive (ліворуч) ──
    xon = 300
    p.append(line(xon - 10, Y(vpl), xon + 10, Y(vpl), color=FIELD, sw=1.6))
    p.append(line(xon - 10, Y(Vdrive), xon + 10, Y(Vdrive), color=FIELD, sw=1.6))
    p.append(arrow(xon, Y(vpl), xon, Y(Vdrive), color=FIELD, sw=2.6))
    p.append(text(xon - 24, (Y(vpl) + Y(Vdrive)) / 2 - 14, "ВМИКАННЯ", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(text(xon - 24, (Y(vpl) + Y(Vdrive)) / 2 + 4, "штовхає Vdrive−Vpl", size=11, color=INK, anchor="end"))
    p.append(text(xon - 24, (Y(vpl) + Y(Vdrive)) / 2 + 20, "= 6 В  →  Ig = 6/Rg", size=11, color=INK, anchor="end"))

    # ── ВИМИКАННЯ: тягне від Vpl униз до 0 (праворуч) ──
    xoff = 524
    p.append(line(xoff - 10, Y(vpl), xoff + 10, Y(vpl), color=NEG, sw=1.6))
    p.append(line(xoff - 10, Y(0), xoff + 10, Y(0), color=NEG, sw=1.6))
    p.append(arrow(xoff, Y(vpl), xoff, Y(0), color=NEG, sw=2.6))
    p.append(text(xoff + 24, (Y(vpl) + Y(0)) / 2 - 14, "ВИМИКАННЯ", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(xoff + 24, (Y(vpl) + Y(0)) / 2 + 4, "тягне Vpl", size=11, color=INK, anchor="start"))
    p.append(text(xoff + 24, (Y(vpl) + Y(0)) / 2 + 20, "= 4 В  →  Ig = 4/Rg", size=11, color=INK, anchor="start"))

    # висновок унизу
    p.append(fitbox(150, 384, 520, 34,
                    "штовх (6 В) > тяг (4 В)  →  Ig(вимк) < Ig(вмик)  →  вимикання зазвичай повільніше",
                    size=12, fill=FILL, stroke=LINE, color=INK, bold=True))

    render(os.path.join(OUT, "drive-asymmetry.svg"), W, H, *p,
           title="Асиметрія: чим драйвер жене затвор на плато")


# ── коло затвора для калькулятора: ланцюг опорів і два шляхи струму ──────────────
# Модель, яку рахує вставка-проєкт proj-driver-sizing: драйвер (Rdrv_src↑ / Rdrv_snk↓)
# + Rg_ext + Rg_int у ряд. Заряд тече крізь Rtot(on), розряд — крізь Rtot(off);
# піковий струм = (Vdrive−Voff)/Rtot має вкладатися в паспортну стелю драйвера.
def fig_gate_drive_loop():
    W, H = 860, 500
    p = []
    Vd_y = 116          # Vdrive-шина
    src_y = 366         # витік / Voff (низ)
    wire_y = 196        # головний дріт затвора
    Ox = 176            # вихід драйвера (вертикаль Rdrv)
    Gx = 456            # вузол затвора
    Dx = 600            # вузол стоку (для Cgd)

    def resbox_h(cx, cy, lab, color=INK, w=68, h=26):
        return (rect(cx - w/2, cy - h/2, w, h, fill=FILL, stroke=color, sw=1.8)
                + text(cx, cy + 4, lab, size=11, color=color, bold=True))

    def resbox_v(cx, cy, lab, color=INK, w=26, h=54):
        return (rect(cx - w/2, cy - h/2, w, h, fill=FILL, stroke=color, sw=1.8)
                + text(cx + w/2 + 8, cy + 4, lab, size=11, color=color, bold=True, anchor="start"))

    def cap_v(cx, cy, lab, color=INK):
        return (line(cx - 16, cy - 5, cx + 16, cy - 5, color=color, sw=3)
                + line(cx - 16, cy + 5, cx + 16, cy + 5, color=color, sw=3)
                + text(cx + 24, cy + 4, lab, size=12, color=color, bold=True, anchor="start"))

    def cap_h(cx, cy, lab, color=INK):
        return (line(cx - 5, cy - 15, cx - 5, cy + 15, color=color, sw=3)
                + line(cx + 5, cy - 15, cx + 5, cy + 15, color=color, sw=3)
                + text(cx, cy - 24, lab, size=12, color=color, bold=True))

    # шини
    p.append(line(100, Vd_y, 330, Vd_y, color=INK, sw=2))
    p.append(text(100, Vd_y - 20, "Vdrive", size=12, color=INK, bold=True, anchor="start"))
    p.append(line(100, src_y, Dx + 30, src_y, color=INK, sw=2))
    p.append(text(100, src_y + 22, "Voff = витік (0 В)", size=12, color=MUTED, bold=True, anchor="start"))
    for i, wd in enumerate([28, 18, 8]):
        p.append(line(Gx - wd/2, src_y + 8 + i*5, Gx + wd/2, src_y + 8 + i*5, color=INK, sw=2))
    p.append(line(Gx, src_y, Gx, src_y + 6, color=INK, sw=2))

    # драйвер: Rdrv_src (↑, зелений) і Rdrv_snk (↓, синій), вихід O
    p.append(text(Ox - 30, Vd_y + 18, "драйвер", size=12, color=MUTED, bold=True, anchor="end"))
    p.append(line(Ox, Vd_y, Ox, wire_y, color=INK, sw=2))
    p.append(resbox_v(Ox, (Vd_y + wire_y) / 2, "Rdrv_src", color=FIELD))
    p.append(line(Ox, wire_y, Ox, src_y, color=INK, sw=2))
    p.append(resbox_v(Ox, (wire_y + src_y) / 2, "Rdrv_snk", color=NEG))
    p.append(circle(Ox, wire_y, 4, fill=INK, stroke=INK))

    # головний ланцюг: O → Rg_ext → Rg_int → G
    p.append(line(Ox, wire_y, 246, wire_y, color=INK, sw=2))
    p.append(resbox_h(282, wire_y, "Rg_ext"))
    p.append(line(316, wire_y, 356, wire_y, color=INK, sw=2))
    p.append(resbox_h(392, wire_y, "Rg_int"))
    p.append(line(426, wire_y, Gx, wire_y, color=INK, sw=2))
    p.append(circle(Gx, wire_y, 4, fill=INK, stroke=INK))
    p.append(text(Gx, wire_y - 14, "затвор", size=11, color=MUTED))

    # Cgs: G → витік
    p.append(line(Gx, wire_y, Gx, src_y, color=INK, sw=2))
    p.append(cap_v(Gx, (wire_y + src_y) / 2, "Cgs"))
    # Cgd: G → стік
    p.append(line(Gx, wire_y, Dx, wire_y, color=INK, sw=2))
    p.append(cap_h((Gx + Dx) / 2 + 10, wire_y, "Cgd"))
    p.append(circle(Dx, wire_y, 4, fill=INK, stroke=INK))
    p.append(line(Dx, wire_y, Dx, Vd_y + 8, color=INK, sw=2))
    p.append(text(Dx, Vd_y - 2, "стік (Vds)", size=11, color=MUTED))

    # струми: заряд (зелений) над дротом, розряд (синій) під дротом
    p.append(arrow(Ox + 34, wire_y - 20, Gx - 44, wire_y - 20, color=FIELD, sw=2.4))
    p.append(text((Ox + Gx) / 2, wire_y - 28, "Ig заряд (джерело)", size=11, color=FIELD, bold=True))
    p.append(arrow(Gx - 44, wire_y + 22, Ox + 34, wire_y + 22, color=NEG, sw=2.4))
    p.append(text((Ox + Gx) / 2, wire_y + 40, "Ig розряд (стік)", size=11, color=NEG, bold=True))

    # формули (два боки)
    p.append(fitbox(100, 414, 344, 70,
                    "Заряд:  Rtot(on) = Rdrv_src + Rg_ext + Rg_int\nIpk(on) = (Vdrive − Voff) / Rtot(on)  ≤  Isrc_max",
                    size=12, fill="#eafaf0", stroke=FIELD, color=INK))
    p.append(fitbox(468, 414, 344, 70,
                    "Розряд:  Rtot(off) = Rdrv_snk + Rg_ext + Rg_int\nIpk(off) = (Vdrive − Voff) / Rtot(off)  ≤  Isnk_max",
                    size=12, fill="#eef2fb", stroke=NEG, color=INK))

    render(os.path.join(OUT, "gate-drive-loop.svg"), W, H, *p,
           title="Коло затвора: ланцюг опорів і два шляхи струму")


# ── паразитне вмикання: dV/dt сусіда крізь Cgd піднімає затвор закритого ключа ────
# Пастка «швидше — небезпечніше»: різкий перехід одного ключа дає велике dV/dt на
# спільному вузлі; крізь Cgd закритого ключа тече Icgd = Cgd·dV/dt і піднімає його Vgs.
# Понад Vth → напівмостовий наскрізний струм.
def fig_parasitic_turnon():
    W, H = 820, 500
    p = []
    busy = 92
    gnd = 402
    xstk = 250
    SWy = 250
    QGx = 470

    # шини
    p.append(line(120, busy, 470, busy, color=INK, sw=2))
    p.append(text(120, busy - 10, "Vbus", size=12, color=INK, bold=True, anchor="start"))
    p.append(line(120, gnd, 640, gnd, color=INK, sw=2))
    for i, wd in enumerate([28, 18, 8]):
        p.append(line(xstk - wd/2, gnd + 8 + i*5, xstk + wd/2, gnd + 8 + i*5, color=INK, sw=2))
    p.append(line(xstk, gnd, xstk, gnd + 6, color=INK, sw=2))

    # Q1 верхній — вмикається (зелений)
    p.append(rect(xstk - 60, 116, 120, 62, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(mtext(xstk, 142, ["Q1 (верхній)", "вмикається"], size=12, color=INK, bold=True))
    p.append(line(xstk, busy, xstk, 116, color=INK, sw=2))
    p.append(line(xstk, 178, xstk, SWy, color=INK, sw=2))
    p.append(circle(xstk, SWy, 4, fill=INK, stroke=INK))
    p.append(text(xstk - 12, SWy - 8, "вузол", size=10, color=MUTED, anchor="end"))

    # dV/dt угору
    p.append(arrow(xstk - 44, SWy + 28, xstk - 44, SWy - 42, color=FIELD, sw=3))
    p.append(mtext(xstk - 54, SWy - 4, ["dV/dt", "швидко ↑"], size=12, color=FIELD, bold=True, anchor="end"))

    # Q2 нижній — закритий, під загрозою (червоний)
    p.append(rect(xstk - 60, 300, 120, 62, fill="#fdecea", stroke=POS, sw=2))
    p.append(mtext(xstk, 326, ["Q2 (нижній)", "закритий — загроза"], size=12, color=INK, bold=True))
    p.append(line(xstk, SWy, xstk, 300, color=INK, sw=2))
    p.append(line(xstk, 362, xstk, gnd, color=INK, sw=2))

    # затвор Q2
    p.append(line(xstk + 60, 331, QGx, 331, color=INK, sw=2))
    p.append(circle(QGx, 331, 4, fill=INK, stroke=INK))
    p.append(text(QGx - 12, 331 - 12, "затвор Q2", size=10, color=MUTED, anchor="end"))

    # Cgd Q2 (червоний шлях): вузол → затвор
    p.append(line(xstk, SWy, QGx, SWy, color=POS, sw=2.4))
    p.append(line(QGx, SWy, QGx, 331, color=POS, sw=2.4))
    cy = 291
    p.append(line(QGx - 15, cy - 5, QGx + 15, cy - 5, color=POS, sw=3))
    p.append(line(QGx - 15, cy + 5, QGx + 15, cy + 5, color=POS, sw=3))
    p.append(text(QGx + 22, cy + 4, "Cgd (Q2)", size=12, color=POS, bold=True, anchor="start"))
    p.append(arrow(QGx + 48, SWy + 4, QGx + 48, cy - 12, color=POS, sw=2.2))
    p.append(text(QGx + 58, 236, "Icgd = Cgd·dV/dt", size=11, color=POS, bold=True, anchor="start"))

    # Cgs Q2: затвор → земля
    p.append(line(QGx, 331, QGx, gnd, color=INK, sw=2))
    p.append(line(QGx - 15, 372 - 5, QGx + 15, 372 - 5, color=INK, sw=3))
    p.append(line(QGx - 15, 372 + 5, QGx + 15, 372 + 5, color=INK, sw=3))
    p.append(text(QGx + 22, 372 + 4, "Cgs", size=12, color=INK, bold=True, anchor="start"))

    # Rg_off → драйвер (Voff)
    p.append(line(QGx, 331, 590, 331, color=INK, sw=2))
    p.append(rect(590, 331 - 13, 62, 26, fill=FILL, stroke=INK, sw=1.8, rx=5))
    p.append(text(621, 331 + 4, "Rg_off", size=11, color=INK, bold=True))
    p.append(line(652, 331, 694, 331, color=INK, sw=2))
    p.append(fitbox(694, 331 - 24, 100, 48, "драйвер\nтримає Voff", size=11,
                    fill="#eef2fb", stroke=NEG, color=NEG, bold=True))

    # підсумкова формула
    p.append(fitbox(120, 434, 574, 52,
                    "Стрибок затвора:  Vgs ≈ Cgd·(dV/dt)·Rg_off   —   якщо Vgs > Vth, Q2 прочиняється → наскрізний струм",
                    size=13, fill="#fdf3f2", stroke=POS, color=INK, bold=True))

    render(os.path.join(OUT, "parasitic-turnon.svg"), W, H, *p,
           title="Паразитне вмикання: dV/dt крізь Cgd піднімає затвор закритого ключа")


if __name__ == "__main__":
    fig_gate_charge_map()
    fig_plateau_mechanism()
    fig_transition_timeline()
    fig_transfer_plateau()
    fig_drive_asymmetry()
    fig_gate_drive_loop()
    fig_parasitic_turnon()
    print("OK: figures written to", OUT)
