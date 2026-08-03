# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: розтин вертикального силового MOSFET — дрейфова область як головний опір ──
def fig_drift_region():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Звідки береться опір: дрейфова область", size=17, bold=True))

    # два стовпчики: 100 В (тонкий шар) vs 600 В (товстий шар)
    def stack(x0, w, dh, label, vlabel, ntxt):
        top = 70
        # верхні шари (виток+, канал) — тонкі
        f.append(rect(x0, top, w, 22, fill="#eaf0fd", stroke=LINE))
        f.append(text(x0 + w/2, top + 15, "виток + канал", size=11, color=NEG))
        # дрейфова область — головна
        dy = top + 22
        f.append(rect(x0, dy, w, dh, fill="#eafaf0", stroke=FIELD, sw=2))
        f.append(text(x0 + w/2, dy + dh/2 - 6, "дрейфова", size=12, color=FIELD, bold=True))
        f.append(text(x0 + w/2, dy + dh/2 + 10, "область", size=12, color=FIELD, bold=True))
        f.append(text(x0 + w/2, dy + dh/2 + 26, ntxt, size=10, color=MUTED))
        # підкладка (стік)
        by = dy + dh
        f.append(rect(x0, by, w, 22, fill="#fdecea", stroke=LINE))
        f.append(text(x0 + w/2, by + 15, "стік (підкладка)", size=11, color=POS))
        # підпис знизу
        f.append(text(x0 + w/2, by + 46, label, size=13, bold=True))
        f.append(text(x0 + w/2, by + 64, vlabel, size=11, color=MUTED))
        return dy, dh, by

    dy1, dh1, by1 = stack(120, 150, 60, "низьковольтний", "≈100 В: тонка й густа", "тонка, легована густо")
    dy2, dh2, by2 = stack(450, 150, 150, "високовольтний", "≈600 В: товста й рідка", "товста, легована рідко")

    # стрілки товщини
    f.append(line(96, dy1, 96, dy1+dh1, color=FIELD, sw=1.5))
    f.append(text(78, dy1+dh1/2, "d", size=13, color=FIELD, italic=True))
    f.append(line(426, dy2, 426, dy2+dh2, color=FIELD, sw=1.5))
    f.append(text(408, dy2+dh2/2, "d↑", size=13, color=FIELD, italic=True, bold=True))

    # нижній підсумок
    box = fitbox(150, 322, 420, 40,
                 "Вища робоча напруга → товща й рідша дрейфова область → більший опір",
                 size=13, fill="#fff8e1", stroke="#d0a000")
    f.append(box)
    render(os.path.join(IMG, 'drift-region.svg'), W, H, *f)


# ── Фігура 2: Ron·A проти напруги — кремнієва межа й широкозонні матеріали ──
def fig_silicon_limit():
    W, H = 720, 460
    f = []
    f.append(text(W/2, 26, "Питомий опір Ron·A проти робочої напруги", size=17, bold=True))

    # осі (лог-лог схематично)
    L, R, T, B = 110, 660, 70, 360
    f.append(line(L, T, L, B, color=INK, sw=2))          # вісь Y
    f.append(line(L, B, R, B, color=INK, sw=2))          # вісь X
    f.append(text((L+R)/2, B+44, "робоча напруга BV  (10 → 100 → 1000 В)", size=12))
    f.append(text(L-14, (T+B)/2, "Ron·A", size=13, italic=True, anchor="middle"))
    f.append(text(L-14, (T+B)/2+18, "(мОм·см²)", size=10, color=MUTED, anchor="middle"))

    import math
    # осі в декадах: X від 10 до 3000 В, Y — питомий опір
    def X(v):   # v у вольтах, лог
        return L + (math.log10(v) - 1) / (math.log10(3000) - 1) * (R - L)
    def Y(r):   # r у мОм·см², лог, від 0.01 до 3000
        return B - (math.log10(r) - math.log10(0.01)) / (math.log10(3000) - math.log10(0.01)) * (B - T)

    # засічки X
    for v in (10, 100, 1000):
        f.append(line(X(v), B, X(v), B+5, color=INK))
        f.append(text(X(v), B+20, str(v), size=11, color=MUTED))

    # кремнієва межа: Ron·A[Ом·см²] = 8.3e-9 · BV^2.5  → у мОм·см²: ·1e3
    def si(v):  # мОм·см²
        return 8.3e-9 * (v**2.5) * 1e3
    pts_si = " ".join("%.1f,%.1f" % (X(v), Y(si(v))) for v in (30, 60, 100, 200, 400, 700, 1200, 2000))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts_si, POS))
    f.append(text(X(1500), Y(si(1500))-14, "кремнієва межа", size=12, color=POS, bold=True))
    f.append(text(X(1500), Y(si(1500))+2, "∝ BV²·⁵", size=11, color=POS, italic=True))

    # SiC/GaN: ~ у 300–1000 разів нижче (тут показуємо ×0.003 як орієнтир)
    def sic(v):
        return si(v) * 0.003
    pts_sic = " ".join("%.1f,%.1f" % (X(v), Y(sic(v))) for v in (100, 200, 400, 700, 1200, 2000))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts_sic, FIELD))
    f.append(text(X(300), Y(sic(300))-12, "SiC / GaN", size=12, color=FIELD, bold=True))
    f.append(text(X(300), Y(sic(300))+4, "нижче межі", size=10, color=FIELD, italic=True))

    # суперперехід: ламає нахил — майже лінійно (пунктир)
    def sj(v):
        return si(400)*0.5 * (v/400.0)  # ~лінійно
    pts_sj = " ".join("%.1f,%.1f" % (X(v), Y(sj(v))) for v in (200, 400, 700, 1000))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="7,4"/>' % (pts_sj, NEG))
    f.append(text(X(750), Y(sj(750))+16, "суперперехід (Si)", size=11, color=NEG, bold=True))
    f.append(text(X(750), Y(sj(750))+30, "нахил зламано", size=10, color=NEG, italic=True))

    # стрілка «вниз = краще»
    f.append(arrow(R-30, T+20, R-30, T+70, color=MUTED))
    f.append(text(R-30, T+12, "краще", size=10, color=MUTED))

    box = fitbox(120, 396, 480, 44,
                 "Чим нижче лінія, тим менший опір на ту саму напругу й площу. "
                 "Матеріал і геометрія опускають лінію нижче кремнієвої межі.",
                 size=12, fill="#f4f6f8", stroke=LINE)
    f.append(box)
    render(os.path.join(IMG, 'silicon-limit.svg'), W, H, *f)


# ── Фігура 3: суперперехід — стовпці p/n вирівнюють поле ──
def fig_superjunction():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Суперперехід: зарядовий баланс вирівнює поле", size=17, bold=True))

    # ЛІВОРУЧ: звичайна дрейфова — трикутне поле
    lx, ly, lw, lh = 90, 70, 200, 170
    f.append(text(lx+lw/2, ly-14, "звичайна дрейфова", size=13, bold=True))
    f.append(rect(lx, ly, lw, lh, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(lx+lw/2, ly+lh/2, "n⁻  (рідке легування)", size=11, color=FIELD))
    # епюра поля — трикутник праворуч від блоку
    ex = lx+lw+18
    f.append(line(ex, ly, ex, ly+lh, color=INK, sw=1.5))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (ex, ly+lh, ex+70, ly+lh, ex, ly, POS))
    f.append(text(ex+40, ly+lh+18, "E(x)", size=11, color=POS, italic=True))
    f.append(text(ex+58, ly+8, "Emax", size=10, color=POS))
    f.append(text(ex+30, ly-2, "пік на переході", size=9, color=MUTED))

    # ПРАВОРУЧ: суперперехід — стовпці, поле майже прямокутне
    rx, ry, rw, rh = 400, 70, 200, 170
    f.append(text(rx+rw/2, ry-14, "суперперехід", size=13, bold=True))
    # чергування n/p стовпців
    ncol = 6
    cw = rw/ncol
    for i in range(ncol):
        col = "#eafaf0" if i % 2 == 0 else "#eaf0fd"
        stk = FIELD if i % 2 == 0 else NEG
        f.append(rect(rx+i*cw, ry, cw, rh, fill=col, stroke=stk, sw=1.2, rx=0))
        f.append(text(rx+i*cw+cw/2, ry+rh/2, "n" if i % 2 == 0 else "p", size=11,
                      color=stk, bold=True))
    f.append(text(rx+rw/2, ry+rh+16, "густіше легування, заряди врівноважені", size=10, color=MUTED))
    # епюра поля — майже прямокутна
    ex2 = rx+rw+18
    f.append(line(ex2, ry, ex2, ry+rh, color=INK, sw=1.5))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#eafaf0" stroke="%s" stroke-width="2"/>'
             % (ex2, ry+rh, ex2+55, ry+rh, ex2+55, ry+6, ex2, ry, FIELD))
    f.append(text(ex2+30, ry+rh+18, "E(x)", size=11, color=FIELD, italic=True))
    f.append(text(ex2+30, ry-2, "рівне поле", size=9, color=MUTED))

    box = fitbox(90, 322, 510, 40,
                 "Рівне поле тримає ту саму напругу коротшим шляхом і дозволяє легувати густіше — опір падає.",
                 size=12, fill="#fff8e1", stroke="#d0a000")
    f.append(box)
    render(os.path.join(IMG, 'superjunction.svg'), W, H, *f)


# ── Фігура 4 (для math-вставки): трикутне поле — дві умови пробою разом ──
def fig_field_triangle():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Дві умови пробою задають і товщину, і легування", size=16, bold=True))

    # осі: x — глибина 0..d, y — поле E
    Lx, Rx = 110, 470          # вісь глибини
    Ty, By = 70, 300           # верх/низ поля
    Emax_y = Ty + 18           # рівень піку поля
    f.append(line(Lx, By, Rx+30, By, color=INK, sw=2))     # вісь x (глибина)
    f.append(line(Lx, By, Lx, Ty, color=INK, sw=2))        # вісь y (поле)
    f.append(text(Rx+8, By+22, "глибина x", size=12, color=MUTED))
    f.append(text(Lx-8, Ty-2, "поле E", size=12, color=MUTED, anchor="end"))

    # трикутник поля: пік Ec на переході (x=0), лінійно до 0 на x=d
    xd = Rx            # x = d
    tri = "%d,%d %d,%d %d,%d" % (Lx, Emax_y, Lx, By, xd, By)
    f.append('<polygon points="%s" fill="#eafaf0" stroke="%s" stroke-width="2.5"/>' % (tri, FIELD))

    # пік Ec
    f.append(line(Lx-5, Emax_y, Lx+5, Emax_y, color=POS, sw=2))
    f.append(text(Lx-10, Emax_y+4, "Ec", size=13, color=POS, bold=True, italic=True, anchor="end"))
    f.append(text(Lx+60, Emax_y+2, "пік = критичне поле", size=11, color=POS))

    # нахил = q·Nd/ε (Пуассон)
    f.append(text(Lx+150, By-70, "нахил = q·Nd/ε", size=12, color=NEG, italic=True))
    f.append(text(Lx+150, By-54, "(що густіше — то крутіше)", size=10, color=MUTED))
    f.append(arrow(Lx+145, By-66, Lx+95, By-40, color=NEG, sw=1.4))

    # площа = BV
    f.append(text((Lx+xd)/2, (Emax_y+By)/2+18, "площа = BV", size=13, color=FIELD, bold=True))
    f.append(text((Lx+xd)/2, (Emax_y+By)/2+34, "(∫E·dx = напруга)", size=10, color=MUTED))

    # товщина d
    f.append(line(Lx, By+16, xd, By+16, color=INK, sw=1.2))
    f.append(line(Lx, By+11, Lx, By+21, color=INK, sw=1.2))
    f.append(line(xd, By+11, xd, By+21, color=INK, sw=1.2))
    f.append(text((Lx+xd)/2, By+34, "d = 2·BV/Ec", size=12, color=INK, bold=True))

    # праворуч: дві умови -> два невідомих
    bx = 500
    frag, bw, bh = textbox(bx+95, 130,
        "Дві умови:\n"
        "• пік = Ec\n"
        "• площа = BV\n"
        "задають ОБИДВА:\n"
        "товщину d і\n"
        "легування Nd",
        size=12, fill="#fff8e1", stroke="#d0a000", pad=12)
    f.append(frag)

    box = fitbox(110, 352, 480, 52,
                 "Трикутник: висота впирається в Ec, площа мусить дорівнювати BV.\n"
                 "Звідси одразу d = 2·BV/Ec і Nd = ε·Ec²/(2·q·BV) — усе для опору.",
                 size=12, fill="#f4f6f8", stroke=LINE)
    f.append(box)
    render(os.path.join(IMG, 'field-triangle.svg'), W, H, *f)


# ── Фігура 5 (для hist-вставки baliga-fom): BFOM матеріалів відносно кремнію ──
def fig_bfom_bars():
    import math
    W, H = 720, 400
    f = []
    f.append(text(W/2, 26, "Фігура якості Байґи: у скільки разів кращий за кремній",
                  size=16, bold=True))

    # матеріали й типові множники BFOM відносно Si (Si = 1); лог-шкала
    # (типові інженерні орієнтири; алмаз обрізаємо стрілкою «поза шкалою»)
    data = [
        ("германій\nGe",       0.1,    MUTED, "×0.1"),
        ("кремній\nSi",        1.0,    POS,   "×1"),
        ("GaAs",               13.0,   NEG,   "×13"),
        ("4H-SiC",             340.0,  FIELD, "×340"),
        ("GaN",                870.0,  FIELD, "×870"),
        ("алмаз\nC",           3000.0, INK,   "поза шкалою"),
    ]

    L, R, T, B = 80, 660, 78, 300
    # лог-вісь від 0.05 до 1000 (германій дає короткий стовпчик; алмаз вилітає — стрілкою)
    lo, hi = 0.05, 1000.0
    def Y(v):
        v = max(v, lo)
        return B - (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (B - T)

    # горизонтальні лінії-декади + підписи
    for dec in (0.1, 1, 10, 100, 1000):
        yy = Y(dec)
        f.append(line(L, yy, R, yy, color="#e2e6ea", sw=1))
        lbl = ("%g" % dec) if dec >= 1 else "0.1"
        f.append(text(L-10, yy+4, lbl, size=10, color=MUTED, anchor="end"))
    # лінія кремнію — виділити
    f.append(line(L, Y(1), R, Y(1), color=POS, sw=1.5, dash="5,4"))

    n = len(data)
    slot = (R - L) / n
    bw = slot * 0.52
    for i, (name, val, col, tag) in enumerate(data):
        cx = L + slot * (i + 0.5)
        x0 = cx - bw/2
        top = Y(val)
        clipped = val > hi                 # алмаз обрізаємо на верхній межі
        top_draw = Y(hi) if clipped else top
        f.append(rect(x0, top_draw, bw, B - top_draw, fill=col, stroke=col, sw=1, rx=3))
        if clipped:
            f.append(arrow(cx, top_draw+2, cx, top_draw-16, color=col))
        # значення над стовпчиком
        f.append(text(cx, top_draw - (22 if clipped else 8), tag, size=11,
                      color=col, bold=True))
        # назва матеріалу під віссю
        for j, ln in enumerate(name.split("\n")):
            f.append(text(cx, B + 18 + j*14, ln, size=11, color=INK,
                          bold=(j == 0)))

    box = fitbox(80, 340, 560, 46,
                 "BFOM = ε·μ·Ec³, нормовано на кремній (лог-шкала).\n"
                 "Вирішує критичне поле Ec у кубі — широкозонні виграють тисячократно.",
                 size=13, fill="#f4f6f8", stroke=LINE)
    f.append(box)
    render(os.path.join(IMG, 'bfom-bars.svg'), W, H, *f)


if __name__ == '__main__':
    fig_drift_region()
    fig_silicon_limit()
    fig_superjunction()
    fig_field_triangle()
    fig_bfom_bars()
    print("figs done")
