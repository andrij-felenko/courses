# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

REF  = "#7c3aed"   # опорна напруга — фіолетовий акцент
GOOD = FIELD       # відкалібровано / правда
BAD  = POS         # помилка


# ── 1. scale-shift: справжня Vref ≠ заявленої → лінійка розтягнута ────────────
# Ідея: код = Vin/Vref × макс. Якщо реальна Vref більша за заявлену 3.3 В,
# та сама лінійка «розтягується» — кожен код переводимо в занижені вольти.
def fig_scale_shift():
    W, H = 860, 360
    p = []

    # дві шкали-«лінійки» від 0 до повної шкали коду, по одному входу Vin
    x0, x1 = 120, 740
    full = 4095
    vin = 1.65            # реальний вхід, В
    code = 2048           # АЦП видав цей код (для обох — однаковий!)

    def ruler(y, vref, label, col, note):
        p.append(line(x0, y, x1, y, color=INK, sw=2))
        # поділки 0 / ½Vref / Vref
        for frac, lab in [(0.0, "0"), (0.5, "%.2f В" % (vref / 2)), (1.0, "%.2f В" % vref)]:
            xx = x0 + (x1 - x0) * frac
            p.append(line(xx, y - 6, xx, y + 6, color=INK, sw=1.6))
            p.append(text(xx, y + 22, lab, size=10, color=MUTED))
        # маркер коду 2048 — стоїть на ТІЙ САМІЙ частці шкали (½)
        xc = x0 + (x1 - x0) * (code / full)
        p.append(line(xc, y - 26, xc, y + 6, color=col, sw=2.4))
        p.append(circle(xc, y - 26, 5, fill="#fff", stroke=col, sw=2.4))
        # яким вольтам відповідає код за ЦІЄЮ Vref
        v_read = code / full * vref
        b, _, _ = textbox(xc, y - 50, "код 2048 → %.2f В" % v_read, size=11,
                          color=col, stroke=col, fill="#fff")
        p.append(b)
        p.append(text(x0 - 14, y + 4, label, size=12, color=col, bold=True, anchor="end"))
        p.append(text(x1 + 14, y + 4, note, size=10, color=MUTED, anchor="start"))

    ruler(115, 3.30, "заявлено", NEG, "Vref = 3.30 В")
    ruler(245, 3.47, "насправді", REF, "Vref = 3.47 В")

    # підпис-висновок
    b, _, _ = textbox(W / 2, 320,
                      "Та сама нога, той самий код 2048 — але переклад у вольти зсунутий на +5 %:"
                      "\nреальна Vref на 0.17 В вища, тож код «коштує» 1.74 В, а не 1.65 В.",
                      size=11.5, stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "scale-shift.svg"), W, H, *p,
           title="Помилка Vref зсуває всю лінійку — однаково для кожного коду")


# ── 2. two-point: два відомі входи → пряма (зсув+масштаб) → виправлення ───────
# Ідея: подаємо дві еталонні напруги, читаємо два сирих коди, через дві точки
# проводимо пряму корекції. Вона лагодить і зсув, і масштаб одразу.
def fig_two_point():
    W, H = 820, 430
    p = []

    ox, oy = 110, 350      # початок осей
    ax, ay = 700, 60       # дальні кінці
    # осі
    p.append(arrow(ox, oy, ox, ay - 6, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ax + 6, oy, color=INK, sw=1.8))
    p.append(text(ox - 8, ay + 4, "В (істина)", size=11, color=INK, anchor="end"))
    p.append(text(ax + 4, oy + 20, "сирий код АЦП", size=11, color=INK, anchor="middle"))

    def X(code): return ox + (ax - ox) * (code / 4095)
    def Y(v):    return oy - (oy - ay) * (v / 3.3)

    # реальна (сира) характеристика: зсунена й з іншим нахилом
    raw_lo = (300, 0.50)    # подали 0.50 В — АЦП дав код 300 (мав би ~620)
    raw_hi = (3500, 3.00)   # подали 3.00 В — АЦП дав код 3500 (мав би ~3723)

    # ідеальна пряма (сіра пунктирна) для порівняння
    p.append(line(X(0), Y(0), X(4095), Y(3.3), color=MUTED, sw=1.4, dash="6 5"))
    p.append(text(X(3700), Y(3.25), "ідеал", size=10, color=MUTED, anchor="start"))

    # дві еталонні точки
    for (c, v), lab in [(raw_lo, "точка A: 0.50 В"), (raw_hi, "точка B: 3.00 В")]:
        p.append(circle(X(c), Y(v), 6, fill="#fff", stroke=GOOD, sw=2.6))
        # пунктир до осей
        p.append(line(X(c), Y(v), X(c), oy, color=GOOD, sw=1, dash="3 4"))
        p.append(line(X(c), Y(v), ox, Y(v), color=GOOD, sw=1, dash="3 4"))
        p.append(text(X(c) + 10, Y(v) - 10, lab, size=10.5, color=GOOD, anchor="start", bold=True))

    # пряма корекції — точно через A і B, продовжена на всю шкалу коду
    k = (raw_hi[1] - raw_lo[1]) / (raw_hi[0] - raw_lo[0])   # В на код (нахил = масштаб)
    b0 = raw_lo[1] - k * raw_lo[0]                          # вільний член = зсув
    p.append(line(X(0), Y(b0 + k * 0), X(4095), Y(b0 + k * 4095), color=GOOD, sw=2.4))
    p.append(text(X(2600), Y(b0 + k * 2600) - 14, "пряма корекції", size=10.5,
                  color=GOOD, anchor="middle", bold=True))

    # підпис-висновок
    b, _, _ = textbox(W / 2, 400,
                      "Дві відомі напруги дають дві точки; пряма крізь них задає переклад "
                      "код→вольти,\nщо лагодить і зсув (де перетинає 0), і масштаб (нахил) одразу.",
                      size=11.5, stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "two-point.svg"), W, H, *p,
           title="Калібрування за двома точками: виправляємо зсув і масштаб")


# ── 3. ratiometric: давач живиться від тієї ж Vref → Vref скорочується ───────
# Ідея: якщо і дільник/міст, і АЦП беруть ОДНУ Vref, вона входить у чисельник
# і знаменник — і випадає. Точність Vref перестає впливати.
def fig_ratiometric():
    W, H = 840, 360
    p = []

    # верхня шина Vref живить і дільник, і АЦП
    railx0, railx1, raily = 90, 750, 70
    p.append(line(railx0, raily, railx1, raily, color=REF, sw=3))
    p.append(text((railx0 + railx1) / 2, raily - 12, "одна шина Vref живить ОБОХ",
                  size=12, color=REF, bold=True))

    # ── дільник/міст ліворуч ──
    dx = 230
    p.append(line(dx, raily, dx, 150, color=INK, sw=2))           # верхнє плече
    b, _, _ = textbox(dx, 150, "R1", size=11, stroke=INK); p.append(b)
    p.append(line(dx, 172, dx, 215, color=INK, sw=2))             # середній вузол
    midy = 215
    b, _, _ = textbox(dx, 237, "R2 (давач)", size=11, stroke=INK); p.append(b)
    p.append(line(dx, 259, dx, 300, color=INK, sw=2))
    p.append(line(dx, 300, dx + 0, 310, color=INK, sw=2))
    # земля
    for i, w in enumerate([18, 12, 6]):
        p.append(line(dx - w, 310 + i * 5, dx + w, 310 + i * 5, color=INK, sw=2))
    # відвід із середнього вузла на АЦП
    p.append(line(dx, midy, 480, midy, color=GOOD, sw=2.2))
    p.append(arrow(480, midy, 540, midy, color=GOOD, sw=2.2))
    p.append(text((dx + 480) / 2, midy - 10, "Vsig = Vref · R2/(R1+R2)",
                  size=10.5, color=GOOD, anchor="middle"))

    # ── АЦП праворуч ──
    ax_, ay_ = 545, 165
    p.append(rect(ax_, ay_, 150, 90, fill="#eef3fb", stroke=NEG, sw=2))
    p.append(text(ax_ + 75, ay_ + 30, "АЦП", size=14, color=NEG, bold=True))
    p.append(text(ax_ + 75, ay_ + 52, "код = Vsig/Vref", size=10.5, color=NEG))
    p.append(text(ax_ + 75, ay_ + 70, "× макс", size=10.5, color=NEG))
    # живлення АЦП від тієї ж шини
    p.append(line(ax_ + 75, raily, ax_ + 75, ay_, color=REF, sw=2))

    # ── ключова рівність унизу ──
    b, _, _ = textbox(W / 2, 322,
                      "код = (Vref · R2/(R1+R2)) / Vref × макс  =  R2/(R1+R2) × макс  →  Vref випала."
                      "\nВимір залежить ЛИШЕ від відношення резисторів — точність Vref більше не важить.",
                      size=11.5, stroke=GOOD, fill="#eefaf1")
    p.append(b)

    render(os.path.join(OUT, "ratiometric.svg"), W, H, *p,
           title="Раціометричне ввімкнення: спільна Vref скорочується")


if __name__ == "__main__":
    fig_scale_shift()
    fig_two_point()
    fig_ratiometric()
    print("OK")
