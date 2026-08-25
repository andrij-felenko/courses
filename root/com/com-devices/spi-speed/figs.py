# -*- coding: utf-8 -*-
# Фігури теми «Швидкість SPI». Генерує SVG у ./img через спільний svgkit.
# Запуск: python figs.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CLK = NEG          # такт SCK — синій
DAT = POS          # лінія даних — червоний
OK = FIELD         # «добре» — зелений


# ── Помічник: меандр такту (cpol=0: спокій низько, перший фронт угору) ─────────
def clock(x0, ymid, amp, period, n, color=CLK, sw=2.4):
    hi, lo = ymid - amp, ymid + amp
    pts = [(x0, lo)]
    x = x0 + period * 0.5
    pts.append((x, lo))
    for _ in range(n):
        pts.append((x, hi)); x += period * 0.5; pts.append((x, hi))
        pts.append((x, lo)); x += period * 0.5; pts.append((x, lo))
    poly = " ".join("%.1f,%.1f" % q for q in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="miter" stroke-linecap="round"/>' % (poly, color, sw), x)


def dataline(x0, x1, ymid, amp, changes, level0, color=DAT, sw=2.2):
    hi, lo = ymid - amp, ymid + amp
    cur = level0; lvl = hi if cur else lo
    pts = [(x0, lvl)]
    for cx in changes:
        pts.append((cx, lvl)); cur = 1 - cur; lvl = hi if cur else lo; pts.append((cx, lvl))
    pts.append((x1, lvl))
    poly = " ".join("%.1f,%.1f" % q for q in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="miter" stroke-linecap="round"/>' % (poly, color, sw))


# ── 1. Чотири причини швидкості ────────────────────────────────────────────────
def fig_why_fast():
    W, H = 760, 330
    p = []
    cards = [
        ("двотактний вихід", ["активно жене вгору й вниз —", "різкі фронти, не повільний RC"], OK),
        ("такт у дроті", ["не треба передискретизації", "й ресинхрону, як в UART"], NEG),
        ("мінімум протоколу", ["ні адрес, ні ACK, ні старт-стопу —", "8 тактів несуть 8 біт"], MUTED),
        ("окремі лінії", ["MOSI й MISO роздільні —", "повний дуплекс"], POS),
    ]
    cw, gap = 168, 14
    x = (W - (cw * 4 + gap * 3)) / 2
    y, ch = 70, 150
    for title, body, col in cards:
        p.append(rect(x, y, cw, ch, fill=FILL, stroke=col, sw=2))
        p.append(text(x + cw / 2, y + 30, title, size=12, color=col, bold=True))
        p.append(mtext(x + cw / 2, y + 62, body, size=10, color=INK))
        x += cw + gap
    p.append(rect(60, 250, W - 120, 46, fill="#eef6ef", stroke=OK, sw=1.3))
    p.append(text(W / 2, 278, "Разом: різкі фронти + чесний такт + майже нуль накладних = найшвидша з простих шин.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "why-fast.svg"), W, H, *p,
           title="Чому SPI швидкий: чотири рішення разом")


# ── 2. Діапазон швидкостей (лог-шкала) ─────────────────────────────────────────
def fig_speed_range():
    W, H = 760, 330
    import math
    p = []
    x0, x1 = 130, 720          # 10 кГц … 100 МГц (5 декад)
    decades = [(1e4, "10 к"), (1e5, "100 к"), (1e6, "1 М"), (1e7, "10 М"), (1e8, "100 М")]
    lo, hi = math.log10(1e4), math.log10(1e8)
    def fx(hz):
        return x0 + (math.log10(hz) - lo) / (hi - lo) * (x1 - x0)
    yax = 248
    p.append(line(x0, yax, x1, yax, color=INK, sw=1.8))
    for hz, lab in decades:
        p.append(line(fx(hz), yax, fx(hz), yax + 6, color=INK, sw=1.4))
        p.append(text(fx(hz), yax + 20, lab, size=10.5, color=MUTED))
    bars = [("UART", 1e4, 5e5, INK, FILL, 110),
            ("I2C", 1e5, 3.4e6, MUTED, FILL, 150),
            ("SPI", 1e6, 6e7, OK, "#eef6ef", 190)]
    for name, a, b, col, fill, ytop in bars:
        xa, xb = fx(a), fx(b)
        p.append(rect(xa, ytop, xb - xa, 26, fill=fill, stroke=col, sw=1.8))
        p.append(text(xa - 10, ytop + 18, name, size=12, color=col, bold=True, anchor="end"))
    p.append(rect(60, 282, W - 120, 36, fill="#eef6ef", stroke=OK, sw=1.3))
    p.append(text(W / 2, 305, "SPI тягне десятки МГц там, де I2C ледь дотягує до одиниць — але цю швидкість ще треба довезти.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "speed-range.svg"), W, H, *p,
           title="Діапазон швидкостей: SPI випереджає на порядок")


# ── 3. Перекіс такт-дані на відстані ──────────────────────────────────────────
def fig_skew():
    W, H = 760, 360
    p = []
    amp, period, n = 22, 44, 4
    # ліворуч: біля ведучого — вирівняні
    p.append(text(180, 96, "біля ведучого: вирівняні", size=12, color=OK, bold=True))
    cl, xe = clock(110, 150, amp, period, n)
    p.append(cl); p.append(text(96, 154, "SCK", size=10, color=CLK, bold=True, anchor="end"))
    p.append(dataline(110, xe, 206, amp * 0.7, [110 + period * 0.5, 110 + period * 1.5], 1))
    p.append(text(96, 210, "дані", size=10, color=DAT, bold=True, anchor="end"))
    p.append(line(110 + period * 0.5, 122, 110 + period * 0.5, 232, color=OK, sw=1, dash="3 3"))
    p.append(text(110 + period * 0.5, 248, "фронт = край біта", size=9.5, color=OK, bold=True))
    # праворуч: на дальньому кінці — зсунуті
    sh = 12
    p.append(text(560, 96, "на дальньому кінці: зсунуті", size=12, color=DAT, bold=True))
    cl2, xe2 = clock(490, 150, amp, period, n)
    p.append(cl2); p.append(text(476, 154, "SCK", size=10, color=CLK, bold=True, anchor="end"))
    p.append(dataline(490, xe2, 206, amp * 0.7, [490 + period * 0.5 + sh, 490 + period * 1.5 + sh], 1))
    p.append(text(476, 210, "дані", size=10, color=DAT, bold=True, anchor="end"))
    p.append(line(490 + period * 0.5, 122, 490 + period * 0.5, 232, color=DAT, sw=1, dash="3 3"))
    p.append(text(490 + period * 0.5, 248, "фронт ловить ПЕРЕХІД", size=9.5, color=DAT, bold=True))
    p.append(rect(60, 286, W - 120, 60, fill="#fbecec", stroke=POS, sw=1.4))
    p.append(text(W / 2, 309, "Сигнал біжить ~15 см/нс; при 50 МГц біт триває лише 20 нс.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 330, "Уже метр кабелю зсуває фронт на третину біта — і вибірка влучає в перехід.",
                  size=11, color=INK))
    render(os.path.join(OUT, "skew.svg"), W, H, *p,
           title="Чому близько: на відстані такт і дані розповзаються")


# ── 4. Ємнісне навантаження валить фронт ──────────────────────────────────────
def fig_loading():
    W, H = 760, 340
    p = []
    # лівий фронт — різкий
    p.append(text(210, 100, "мала ємність — фронт різкий", size=12, color=OK, bold=True))
    p.append(line(110, 200, 200, 200, color=OK, sw=2.8))
    p.append(line(200, 200, 200, 130, color=OK, sw=2.8))
    p.append(line(200, 130, 320, 130, color=OK, sw=2.8))
    p.append(text(210, 226, "встигає за швидким тактом", size=10.5, color=OK))
    # правий фронт — завалений (експонента)
    p.append(text(560, 100, "велика ємність — фронт завалений", size=12, color=POS, bold=True))
    import math
    pts = ["%.1f,%.1f" % (460, 200), "%.1f,%.1f" % (505, 200)]
    for i in range(46):
        t = i / 45.0
        xx = 505 + t * 150
        yy = 200 - 70 * (1 - math.exp(-3.2 * t))
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))
    p.append(text(560, 226, "не встигає — доводиться знизити SCK", size=10.5, color=POS, bold=True))
    p.append(rect(60, 252, W - 120, 78, fill=FILL, stroke=MUTED, sw=1.3))
    p.append(text(W / 2, 277, "Кожен пристрій і кожен сантиметр доріжки додають ємність C; час фронту ~ R·C росте.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 298, "Тому навіть на платі гранична частота падає з довжиною ліній і числом ведених.",
                  size=11, color=INK))
    p.append(text(W / 2, 318, "Практично: коротші доріжки й менше навантаження — вища доступна частота.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "loading.svg"), W, H, *p,
           title="Ємнісне навантаження тисне на швидкість")


# ── 5. Затримка туди-назад на MISO ────────────────────────────────────────────
def fig_roundtrip():
    W, H = 760, 340
    p = []
    p.append(rect(80, 130, 130, 90, fill="#eef6ef", stroke=OK, sw=2))
    p.append(text(145, 180, "ВЕДУЧИЙ", size=11, color=OK, bold=True))
    p.append(rect(W - 210, 130, 130, 90, fill=FILL, stroke=INK, sw=2))
    p.append(text(W - 145, 180, "ВЕДЕНИЙ", size=11, color=INK, bold=True))
    p.append(arrow(210, 150, W - 210, 150, color=CLK, sw=2.2))
    p.append(text(W / 2, 140, "1) фронт SCK летить туди (затримка t)", size=10.5, color=CLK, bold=True))
    p.append(arrow(W - 210, 196, 210, 196, color=OK, sw=2.2))
    p.append(text(W / 2, 214, "2) ведений жене MISO, вона летить назад (ще t)", size=10.5, color=OK, bold=True))
    p.append(text(W / 2, 248, "разом ≈ 2t, перш ніж ведучий зможе зняти MISO", size=11.5, color=INK, bold=True))
    p.append(rect(60, 268, W - 120, 62, fill="#fbecec", stroke=POS, sw=1.4))
    p.append(text(W / 2, 292, "На високій частоті 2t стає сумірним із бітом — і MISO не встигає усталитися до вибірки.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 313, "Це окрема, ще жорсткіша межа на «швидко + далеко», ніж простий перекіс.",
                  size=11, color=INK))
    render(os.path.join(OUT, "roundtrip.svg"), W, H, *p,
           title="Затримка туди-назад: чому MISO спізнюється")


# ── 6. Однополюсний проти диференційного ──────────────────────────────────────
def fig_single_ended():
    W, H = 760, 360
    p = []
    import math
    # ліворуч: однополюсний з дзвоном
    p.append(text(220, 100, "однополюсний (SPI)", size=12, color=MUTED, bold=True))
    p.append(line(100, 190, 170, 190, color=INK, sw=2.4))
    p.append(line(170, 190, 170, 140, color=INK, sw=2.4))
    ring = ["%.1f,%.1f" % (170, 140)]
    for i in range(40):
        t = i / 39.0
        xx = 170 + t * 180
        yy = 140 + 16 * math.sin(t * 10) * math.exp(-2.5 * t)
        ring.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(ring), INK))
    p.append(text(220, 224, "дзвін/відбиття від кінця дроту", size=10, color=POS, bold=True))
    p.append(text(220, 242, "+ ловить завади (нема чим гасити)", size=9.5, color=MUTED))
    # праворуч: диференційний — дві протифазні
    p.append(text(560, 100, "диференційний (для метрів)", size=12, color=OK, bold=True))
    p.append(dataline(470, 700, 160, 18, [510, 570, 630], 1, color=OK, sw=2.4))
    p.append(dataline(470, 700, 180, 18, [510, 570, 630], 0, color=CLK, sw=2.0))
    p.append(text(560, 230, "дві протифазні лінії: завада однакова", size=9.5, color=OK, bold=True))
    p.append(text(560, 246, "на обох — у різниці гаситься", size=9.5, color=OK, bold=True))
    p.append(rect(60, 268, W - 120, 80, fill=FILL, stroke=MUTED, sw=1.3))
    p.append(text(W / 2, 292, "SPI — однополюсний і неузгоджений: чудово на короткій платі, погано на метрах кабелю.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 313, "Для відстані беруть диференційні шини (RS-485, CAN, LVDS), де завада гаситься різницею.",
                  size=11, color=INK))
    p.append(text(W / 2, 333, "SPI — житель плати: між сусідніми чіпами, а не між приладами через кабель.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "single-ended.svg"), W, H, *p,
           title="SPI однополюсний і без узгодження — не для довгих ліній")


# ── 7. Карта «швидкість × відстань» ───────────────────────────────────────────
def fig_map():
    W, H = 760, 400
    p = []
    ax, ay = 130, 320
    p.append(arrow(ax, ay, 720, ay, color=INK, sw=1.8))
    p.append(arrow(ax, ay, ax, 90, color=INK, sw=1.8))
    p.append(text(715, 342, "відстань →", size=11.5, color=INK, anchor="end"))
    p.append(text(120, 86, "швидкість", size=11.5, color=INK, anchor="end"))
    p.append(text(230, 340, "см (плата)", size=10, color=MUTED))
    p.append(text(580, 340, "метри (кабель)", size=10, color=MUTED))
    p.append(rect(140, 96, 250, 108, fill="#eef6ef", stroke=OK, sw=2))
    p.append(text(265, 138, "SPI", size=17, color=OK, bold=True))
    p.append(text(265, 164, "швидко + близько", size=11, color=INK, bold=True))
    p.append(rect(140, 226, 250, 84, fill="#fbf3df", stroke="#b08900", sw=1.8))
    p.append(text(265, 260, "I2C", size=14, color="#b08900", bold=True))
    p.append(text(265, 284, "повільніше, теж близько", size=10, color=INK))
    p.append(rect(420, 96, 300, 214, fill="#e9eefb", stroke=CLK, sw=1.8))
    p.append(text(570, 140, "диференційні шини", size=13, color=CLK, bold=True))
    p.append(text(570, 164, "(RS-485, CAN, LVDS)", size=11, color=INK))
    p.append(text(570, 240, "для метрів і завад", size=11, color=INK, bold=True))
    p.append(rect(60, 348, W - 120, 44, fill="#eef6ef", stroke=OK, sw=1.3))
    p.append(text(W / 2, 374, "SPI — десятки МГц на сантиметрах плати; на кабель чи метри бери диференційну шину.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "map.svg"), W, H, *p,
           title="Карта «швидкість × відстань»: де живе SPI")


if __name__ == "__main__":
    fig_why_fast()
    fig_speed_range()
    fig_skew()
    fig_loading()
    fig_roundtrip()
    fig_single_ended()
    fig_map()
    print("OK: figures written to", OUT)
