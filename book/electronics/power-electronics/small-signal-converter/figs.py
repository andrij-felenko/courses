# -*- coding: utf-8 -*-
"""Фігури для теми small-signal-converter (малосигнальна модель DC/DC).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Підписи фігур живуть у Markdown, не в SVG — тут лише сама графіка."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # виділення / особлива риса


def fig_linearize():
    """Головна ідея: нелінійний перемикальний перетворювач → усереднення прибирає
    ключ → мала гойданка навколо робочої точки → лінійна модель для цієї гойданки."""
    W, H = 900, 340
    frags = []
    # ліва панель — реальність: пилчаста напруга на ключі + пульсація виходу
    frags.append(rect(30, 60, 380, 250, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    frags.append(text(220, 88, "Реальність: ключ рубає щомиті", size=13, color=POS, bold=True))
    # прямокутний сигнал ключа
    ax = 60
    top, bot = 120, 168
    frags.append(text(ax - 6, 128, "ключ", size=10, color=MUTED, anchor="end"))
    sq = []
    x = ax
    hi = True
    for i in range(9):
        y = top if hi else bot
        sq.append("%.0f,%.0f" % (x, y))
        x += 36
        sq.append("%.0f,%.0f" % (x, y))
        y2 = bot if hi else top
        sq.append("%.0f,%.0f" % (x, y2))
        hi = not hi
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(sq), INK))
    # вихід із дрібною пилкою навколо рівня
    base = 250
    frags.append(line(60, base, 388, base, color=MUTED, sw=1.2, dash="5,4"))
    frags.append(text(60, base - 34, "Vвих", size=10, color=NEG, anchor="start", bold=True))
    ripple = []
    for i in range(90):
        px = 60 + i * 3.6
        py = base - 16 * math.sin(i * 0.7) * 0.0 - (10 if (i // 5) % 2 else -10) * 0.0
        # трикутна пульсація
        phase = (i % 10) / 10.0
        tri = (phase if phase < 0.5 else 1 - phase) * 2  # 0..1..0
        py = base - 14 * (tri - 0.5)
        ripple.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(ripple), NEG))
    frags.append(text(220, 300, "нелінійно, розривно — важко рахувати", size=11,
                      color=INK, italic=True))

    # стрілка переходу
    frags.append(arrow(418, 185, 482, 185, color=FIELD, sw=3))
    frags.append(text(450, 172, "усереднити", size=11, color=FIELD, bold=True))
    frags.append(text(450, 208, "+ мала гойданка", size=10, color=FIELD))

    # права панель — модель: гладка крива робочої точки + маленьке коло-збурення
    frags.append(rect(490, 60, 380, 250, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(680, 88, "Модель: гладко навколо точки", size=13, color=FIELD, bold=True))
    # гладка крива Vвих(D) — робоча характеристика
    cx0, cy0 = 540, 260
    curve = []
    for i in range(0, 101):
        d = i / 100.0
        px = cx0 + d * 280
        py = cy0 - d * 150       # приблизно лінійна ділянка (buck: Vвих = D·Vвх)
        curve.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(curve), INK))
    frags.append(text(830, 250, "Vвих", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(820, 300, "D", size=12, color=INK, anchor="start", bold=True))
    # робоча точка
    opx, opy = cx0 + 0.55 * 280, cy0 - 0.55 * 150
    frags.append(circle(opx, opy, 6, fill=GOLD, stroke=GOLD))
    frags.append(text(opx + 10, opy - 8, "робоча точка (D, Vвих)", size=10, color=GOLD,
                      anchor="start", bold=True))
    # маленька гойданка навколо точки — дотична
    frags.append(line(opx - 40, opy + 22, opx + 40, opy - 22, color=POS, sw=2.2))
    frags.append(text(opx - 6, opy + 46, "d̂ → v̂  (нахил = підсилення)", size=10,
                      color=POS, anchor="middle"))
    render(os.path.join(OUT, "linearize.svg"), W, H, *frags,
           title="Мала-сигнальна модель: гладка гойданка навколо робочої точки")


def fig_control_to_output():
    """Ланцюг збурення: маленька зміна шпаруватості d̂ → передатна G(s) →
    маленька зміна виходу v̂. Це і є те, що моделюють."""
    W, H = 900, 240
    frags = []
    y = 120
    frags.append(fitbox(60, y - 34, 150, 68, "збурення\nшпаруватості  d̂", size=13,
                        fill="#fdecea", stroke=POS, bold=True))
    frags.append(arrow(210, y, 320, y, color=INK, sw=2.4))
    # центральний блок — сама модель
    frags.append(rect(320, y - 50, 260, 100, fill="#eef7f0", stroke=FIELD, sw=2, rx=12))
    frags.append(text(450, y - 20, "G(s) = v̂ / d̂", size=16, color=FIELD, bold=True))
    frags.append(text(450, y + 6, "«керування → вихід»", size=12, color=INK))
    frags.append(text(450, y + 30, "лінійна передатна функція", size=11, color=MUTED))
    frags.append(arrow(580, y, 690, y, color=INK, sw=2.4))
    frags.append(fitbox(690, y - 34, 160, 68, "збурення\nвиходу  v̂", size=13,
                        fill="#eaf0fd", stroke=NEG, bold=True))
    frags.append(text(450, 210, "Уся динаміка перетворювача — у формі цієї однієї функції G(s).",
                      size=12, color=INK, italic=True))
    render(os.path.join(OUT, "control-to-output.svg"), W, H, *frags,
           title="Що моделюємо: реакцію виходу на дрібну зміну керування")


def _bode_axes(x0, y0, w, h, fdec, gtop, gbot):
    """Осі Боде (лог-частота × дБ). fdec — список десяткових позначок частоти
    (label, frac 0..1). Повертає фрагменти + функцію (fx, gy)."""
    out = [rect(x0, y0, w, h, fill=BG, stroke="#e2e2e2", sw=1.6, rx=10)]
    # вісь X
    out.append(line(x0 + 46, y0 + h - 34, x0 + w - 20, y0 + h - 34, color=INK, sw=1.4))
    # вісь Y
    out.append(line(x0 + 46, y0 + 30, x0 + 46, y0 + h - 34, color=INK, sw=1.4))
    out.append(text(x0 + 30, y0 + 26, "|G|, дБ", size=11, color=INK, anchor="end"))
    out.append(text(x0 + w - 20, y0 + h - 16, "частота (лог)", size=11, color=INK, anchor="end"))
    xspan = (x0 + w - 24) - (x0 + 46)
    yspan = (y0 + h - 34) - (y0 + 34)

    def fx(frac):
        return x0 + 46 + frac * xspan

    def gy(g):
        return (y0 + h - 34) - (g - gbot) / (gtop - gbot) * yspan

    # сітка X
    for lbl, frac in fdec:
        gx = fx(frac)
        out.append(line(gx, y0 + 30, gx, y0 + h - 34, color="#eef0f2", sw=1))
        out.append(text(gx, y0 + h - 18, lbl, size=10, color=MUTED))
    # нульова лінія дБ
    if gbot < 0 < gtop:
        out.append(line(x0 + 46, gy(0), x0 + w - 24, gy(0), color=MUTED, sw=1, dash="5,4"))
        out.append(text(x0 + 52, gy(0) - 4, "0 дБ", size=9, color=MUTED, anchor="start"))
    return out, fx, gy


def fig_bode_features():
    """Схематична АЧХ керування→вихід для buck: рівний DC-виграш, подвійний
    полюс LC (−40 дБ/дек), тоді нуль ESR (повертає до −20 дБ/дек)."""
    W, H = 900, 360
    x0, y0, w, h = 30, 40, 840, 300
    gtop, gbot = 42, -34
    # частотні мітки: 100 Гц, 1к, LC, 10к, ESR, 100к
    fdec = [("100 Гц", 0.02), ("1 к", 0.20), ("10 к", 0.52), ("100 к", 0.85), ("1 М", 0.99)]
    frags, fx, gy = _bode_axes(x0, y0, w, h, fdec, gtop, gbot)

    # характерні точки в частках осі
    f_lc = 0.36     # подвійний полюс LC
    f_esr = 0.70    # нуль ESR
    g0 = 34         # DC-виграш, дБ

    # ділянка 1: рівна до LC
    p_flat = [(fx(0.03), gy(g0)), (fx(f_lc), gy(g0))]
    # ділянка 2: −40 дБ/дек від LC до ESR
    # за декаду частоти (тут ~ 0.30 частки осі) падає 40 дБ; візьмемо нахил у частках
    drop = 40 * ((f_esr - f_lc) / 0.30)     # 0.30 частки ≈ декада
    g_esr = g0 - drop
    p_slope2 = [(fx(f_lc), gy(g0)), (fx(f_esr), gy(g_esr))]
    # ділянка 3: −20 дБ/дек від ESR далі
    tail_x = 0.96
    g_tail = g_esr - 20 * ((tail_x - f_esr) / 0.30)
    p_slope3 = [(fx(f_esr), gy(g_esr)), (fx(tail_x), gy(g_tail))]

    def poly(pts, color, sw=3):
        s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"/>' % (s, color, sw))

    frags.append(poly(p_flat, NEG))
    frags.append(poly(p_slope2, NEG))
    frags.append(poly(p_slope3, NEG))

    # позначки полюса LC і нуля ESR
    frags.append(line(fx(f_lc), gy(g0) - 6, fx(f_lc), y0 + h - 34, color=GOLD, sw=1.4, dash="4,3"))
    frags.append(text(fx(f_lc), y0 + 22, "подвійний полюс LC", size=11, color=GOLD, bold=True))
    frags.append(text(fx(f_lc) + 6, gy(g0 - 12), "−40 дБ/дек", size=11, color=INK, anchor="start", bold=True))

    frags.append(line(fx(f_esr), gy(g_esr) + 6, fx(f_esr), y0 + h - 34, color=POS, sw=1.4, dash="4,3"))
    frags.append(text(fx(f_esr), y0 + h - 46, "нуль ESR", size=11, color=POS, bold=True))
    frags.append(text(fx((f_esr + tail_x) / 2), gy(g_tail) - 12, "−20 дБ/дек", size=11,
                      color=INK, bold=True))

    # DC-виграш
    frags.append(text(fx(0.10), gy(g0) - 10, "рівний DC-виграш", size=11, color=NEG, bold=True))
    render(os.path.join(OUT, "bode-features.svg"), W, H, *frags,
           title="АЧХ «керування → вихід» buck: полюс LC і нуль ESR")


def fig_rhp_zero():
    """Нуль правої півплощини в boost: щоб підняти вихід, контролер довшає фазу
    ВКЛ — і вихід спершу ПРОСІДАЄ, перш ніж піти вгору. Реакція «не в той бік»."""
    W, H = 900, 320
    frags = []
    # верх — крок шпаруватості вгору
    ax = 90
    frags.append(text(ax - 12, 92, "D", size=12, color=INK, anchor="end", bold=True))
    frags.append(line(ax, 108, 300, 108, color=POS, sw=2.4))
    frags.append(line(300, 108, 300, 78, color=POS, sw=2.4))
    frags.append(line(300, 78, 830, 78, color=POS, sw=2.4))
    frags.append(text(430, 68, "контролер довшає ВКЛ, щоб підняти вихід", size=11,
                      color=POS, anchor="middle", italic=True))
    # низ — реакція виходу: спершу вниз, тоді вгору
    base = 210
    frags.append(text(ax - 12, base + 4, "Vвих", size=12, color=NEG, anchor="end", bold=True))
    frags.append(line(ax, base, 830, base, color=MUTED, sw=1.2, dash="6,4"))
    frags.append(text(836, base + 4, "старий рівень", size=10, color=MUTED, anchor="start"))
    # крива: рівно до кроку, провал униз, тоді підйом вище рівня
    pts = [(ax, base), (300, base), (312, base + 42), (340, base + 52),
           (380, base + 30), (440, base - 6), (540, base - 40),
           (680, base - 58), (830, base - 62)]
    s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (s, NEG))
    # виділити «не в той бік»
    frags.append('<line x1="330" y1="%d" x2="330" y2="%d" stroke="%s" stroke-width="1.8" '
                 'marker-end="url(#arrow)"/>' % (base, base + 50, POS))
    frags.append(text(346, base + 40, "спершу ПРОВАЛ (не в той бік!)", size=11,
                      color=POS, anchor="start", bold=True))
    frags.append(text(700, base - 40, "аж потім підйом", size=11, color=NEG,
                      anchor="middle", bold=True))
    # пояснення внизу
    frags.append(text(450, 296,
                      "Довша фаза ВКЛ на мить відрубує котушку від виходу — енергія падає, "
                      "перш ніж зрости.",
                      size=12, color=INK, italic=True))
    render(os.path.join(OUT, "rhp-zero.svg"), W, H, *frags,
           title="Нуль правої півплощини (boost): реакція «не в той бік»")


def fig_hist_genealogy():
    """Історична вставка: родовід усередненого моделювання — Вестер (1972/73)
    заклав усереднення трьох топологій; Чуків перетворювач (1 квітня 1975)
    став приводом; доповідь PESC (червень 1976) уніфікувала все; дисертація
    (листопад 1976) звела в метод. Показуємо, що метод — кумулятивний, не з нуля."""
    W, H = 900, 300
    frags = []
    # вісь часу
    axy = 150
    frags.append(line(60, axy, 850, axy, color=INK, sw=2))
    frags.append(arrow(840, axy, 858, axy, color=INK, sw=2))
    frags.append(text(852, axy + 22, "час", size=11, color=MUTED, anchor="end"))

    # чотири віхи: (частка X, рік, підпис-верх, підпис-низ, колір)
    milestones = [
        (0.08, "1972–73", "Вестер + Мідлбрук", "усереднення buck/boost/\nbuck-boost — перший крок", NEG, "up"),
        (0.36, "1 квіт. 1975", "перетворювач Чука", "нова топологія —\nпривід для методу", GOLD, "down"),
        (0.64, "черв. 1976", "доповідь PESC", "єдиний підхід до всіх\nтопологій одразу", FIELD, "up"),
        (0.90, "лист. 1976", "дисертація Caltech", "метод зведено в\n«усереднення за станами»", POS, "down"),
    ]
    for frac, yr, top, bot, col, side in milestones:
        x = 60 + frac * 780
        frags.append(circle(x, axy, 7, fill=col, stroke=col))
        if side == "up":
            frags.append(line(x, axy - 7, x, axy - 30, color=col, sw=1.4))
            frags.append(text(x, axy - 60, yr, size=12, color=col, bold=True))
            frags.append(text(x, axy - 42, top, size=11, color=INK, bold=True))
            # нижній опис під точкою
            frags.append(mtext(x, axy + 26, bot, size=10, color=MUTED))
        else:
            frags.append(line(x, axy + 7, x, axy + 30, color=col, sw=1.4))
            frags.append(text(x, axy + 52, yr, size=12, color=col, bold=True))
            frags.append(text(x, axy + 68, top, size=11, color=INK, bold=True))
            frags.append(mtext(x, axy - 46, bot, size=10, color=MUTED))
    render(os.path.join(OUT, "hist-genealogy.svg"), W, H, *frags,
           title="Родовід усередненого моделювання: метод накопичувався, а не виник з нуля")


def fig_hist_averaging_idea():
    """Сама ідея, яку внесли Чук і Мідлбрук: дві схеми перетворювача (ключ ON /
    ключ OFF) описуються двома матрицями A₁, A₂; зважена сума з вагами D і (1−D)
    дає ОДНУ усереднену матрицю A — гладку модель без ключа."""
    W, H = 900, 320
    frags = []
    # ліворуч — дві схеми/матриці станів
    bx = 60
    frags.append(rect(bx, 70, 210, 90, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(bx + 105, 96, "ключ ВІДКРИТИЙ (частка D)", size=11, color=FIELD, bold=True))
    frags.append(text(bx + 105, 128, "ẋ = A₁·x + b₁·u", size=15, color=INK, bold=True))

    frags.append(rect(bx, 180, 210, 90, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    frags.append(text(bx + 105, 206, "ключ ЗАКРИТИЙ (частка 1−D)", size=11, color=NEG, bold=True))
    frags.append(text(bx + 105, 238, "ẋ = A₂·x + b₂·u", size=15, color=INK, bold=True))

    # стрілки до вузла зважування
    frags.append(arrow(270, 115, 360, 150, color=FIELD, sw=2.2))
    frags.append(arrow(270, 225, 360, 190, color=NEG, sw=2.2))
    # вузол «зважена сума»
    frags.append(circle(400, 170, 34, fill="#fff8e6", stroke=GOLD, sw=2.2))
    frags.append(text(400, 165, "зважити", size=11, color=GOLD, bold=True))
    frags.append(text(400, 182, "D·(…)+(1−D)·(…)", size=8, color=MUTED))
    # ваги-підписи на стрілках
    frags.append(text(320, 120, "×D", size=12, color=FIELD, bold=True))
    frags.append(text(320, 224, "×(1−D)", size=12, color=NEG, bold=True))

    # стрілка до однієї усередненої моделі
    frags.append(arrow(434, 170, 540, 170, color=INK, sw=2.6))
    frags.append(rect(540, 120, 300, 100, fill="#fdf4e3", stroke=GOLD, sw=2.2, rx=12))
    frags.append(text(690, 150, "ОДНА усереднена модель", size=13, color=GOLD, bold=True))
    frags.append(text(690, 182, "ẋ = A·x + b·u", size=17, color=INK, bold=True))
    frags.append(text(690, 206, "A = D·A₁ + (1−D)·A₂", size=12, color=MUTED))

    frags.append(text(450, 296,
                      "Дві розривні схеми ключа зливаються в одну гладку систему — "
                      "яку вже можна лінеаризувати й малювати як Боде.",
                      size=12, color=INK, italic=True))
    render(os.path.join(OUT, "hist-averaging-idea.svg"), W, H, *frags,
           title="Ідея усереднення за станами: зважити дві схеми ключа в одну")


def fig_two_networks():
    """Вставка math: ключ рве buck на дві лінійні схеми (ВКЛ/ВИМК), кожна зі своєю
    парою матриць (A,B); посередині усереднення зшиває їх у одну за часткою D.
    Показуємо саме різницю фаз (котушка живиться від входу / відрізана)."""
    W, H = 920, 380
    frags = []

    def mini_buck(x0, y0, on):
        """Мінісхема buck: вхід зліва, ключ, котушка, конденсатор+навантаження.
        on=True — фаза ВКЛ (котушка тягнеться до входу), False — ВИМК (діод)."""
        out = []
        nodec = "#c0392b" if on else MUTED     # активна гілка виділена
        # шина входу
        out.append(text(x0 + 4, y0 + 4, "Vвх", size=11, color=INK, anchor="start", bold=True))
        out.append(line(x0, y0 + 14, x0, y0 + 70, color=INK, sw=1.8))
        # ключ (верхній) — замкнений у ВКЛ, розімкнений у ВИМК
        sw_col = FIELD if on else MUTED
        out.append(line(x0, y0 + 14, x0 + 46, y0 + 14, color=INK, sw=1.8))
        if on:
            out.append(line(x0 + 46, y0 + 14, x0 + 86, y0 + 14, color=sw_col, sw=2.6))
        else:
            out.append(line(x0 + 46, y0 + 14, x0 + 78, y0 + 2, color=sw_col, sw=2.6))  # розімкнений
        out.append(circle(x0 + 46, y0 + 14, 2.4, fill=INK, stroke=INK, sw=1))
        out.append(circle(x0 + 86, y0 + 14, 2.4, fill=INK, stroke=INK, sw=1))
        out.append(text(x0 + 63, y0 + 6, "ключ", size=9, color=sw_col, anchor="middle"))
        # вузол комутації → котушка
        out.append(line(x0 + 86, y0 + 14, x0 + 108, y0 + 14, color=INK, sw=1.8))
        # котушка (три дужки)
        lx = x0 + 108
        loop = ['<path d="M%.0f %.0f' % (lx, y0 + 14)]
        for i in range(3):
            cx = lx + 12 + i * 20
            loop.append(' q 10 -13 20 0')
        loop.append('" fill="none" stroke="%s" stroke-width="2.2"/>' % INK)
        out.append("".join(loop))
        out.append(text(lx + 30, y0 + 2, "L", size=11, color=INK, bold=True))
        # діод до землі (активний у ВИМК)
        d_col = MUTED if on else FIELD
        out.append(line(x0 + 86, y0 + 14, x0 + 86, y0 + 50, color=d_col, sw=2.0 if not on else 1.4))
        out.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="%s" stroke="%s" stroke-width="1.2"/>'
                   % (x0 + 80, y0 + 44, x0 + 92, y0 + 44, x0 + 86, y0 + 34, "none", d_col))
        out.append(line(x0 + 80, y0 + 34, x0 + 92, y0 + 34, color=d_col, sw=1.6))
        out.append(text(x0 + 100, y0 + 44, "діод", size=9, color=d_col, anchor="start"))
        # вихідний вузол → конденсатор і навантаження
        ox = lx + 74
        out.append(line(ox, y0 + 14, ox + 24, y0 + 14, color=INK, sw=1.8))
        # конденсатор
        cx2 = ox + 24
        out.append(line(cx2, y0 + 14, cx2, y0 + 30, color=INK, sw=1.8))
        out.append(line(cx2 - 8, y0 + 30, cx2 + 8, y0 + 30, color=INK, sw=2.4))
        out.append(line(cx2 - 8, y0 + 36, cx2 + 8, y0 + 36, color=INK, sw=2.4))
        out.append(line(cx2, y0 + 36, cx2, y0 + 50, color=INK, sw=1.8))
        out.append(text(cx2 + 12, y0 + 30, "C", size=11, color=INK, anchor="start", bold=True))
        # навантаження R
        rx2 = ox + 60
        out.append(line(ox + 24, y0 + 14, rx2, y0 + 14, color=INK, sw=1.8))
        out.append(rect(rx2 - 6, y0 + 16, 12, 24, fill=BG, stroke=INK, sw=1.6, rx=2))
        out.append(line(rx2, y0 + 40, rx2, y0 + 50, color=INK, sw=1.8))
        out.append(text(rx2 + 10, y0 + 30, "R", size=11, color=INK, anchor="start", bold=True))
        # земля
        out.append(line(x0, y0 + 70, rx2, y0 + 70, color=INK, sw=1.8))
        out.append(line(x0, y0 + 70, x0, y0 + 70, color=INK, sw=1.8))
        out.append(line(cx2, y0 + 50, cx2, y0 + 70, color=INK, sw=1.8))
        out.append(line(rx2, y0 + 50, rx2, y0 + 70, color=INK, sw=1.8))
        out.append(line(x0 + 86, y0 + 50, x0 + 86, y0 + 70, color=d_col, sw=1.4))
        return "".join(out), rx2

    # ліва панель — фаза ВКЛ
    frags.append(rect(30, 58, 360, 132, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(210, 82, "Фаза ВКЛ (частка D): котушка живиться від входу", size=12, color=FIELD, bold=True))
    s_on, _ = mini_buck(60, 92, True)
    frags.append(s_on)
    frags.append(text(210, 178, "ẋ = A₁·x + B₁·u", size=15, color=INK, bold=True))

    # права панель — фаза ВИМК
    frags.append(rect(30, 210, 360, 132, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=12))
    frags.append(text(210, 234, "Фаза ВИМК (частка D′): вхід відрізаний, струм через діод", size=11, color=NEG, bold=True))
    s_off, _ = mini_buck(60, 244, False)
    frags.append(s_off)
    frags.append(text(210, 330, "ẋ = A₂·x + B₂·u", size=15, color=INK, bold=True))

    # стрілки усереднення до однієї моделі
    frags.append(arrow(392, 124, 470, 178, color=FIELD, sw=2.2))
    frags.append(arrow(392, 276, 470, 202, color=NEG, sw=2.2))
    frags.append(text(438, 132, "×D", size=13, color=FIELD, bold=True))
    frags.append(text(438, 274, "×D′", size=13, color=NEG, bold=True))

    frags.append(rect(478, 138, 410, 104, fill="#fdf4e3", stroke=GOLD, sw=2.4, rx=12))
    frags.append(text(683, 164, "ОДНА усереднена модель", size=13, color=GOLD, bold=True))
    frags.append(text(683, 192, "ẋ = A·x + B·u", size=17, color=INK, bold=True))
    frags.append(text(683, 218, "A = D·A₁ + D′·A₂     B = D·B₁ + D′·B₂", size=12, color=MUTED))

    frags.append(text(683, 300,
                      "У buck змінюється лише те, ЗВІДКИ живиться котушка —",
                      size=12, color=INK, italic=True))
    frags.append(text(683, 320,
                      "тож різниця фаз сидить у вхідному стовпчику B.",
                      size=12, color=INK, italic=True))
    render(os.path.join(OUT, "two-networks.svg"), W, H, *frags,
           title="Ключ рве buck на дві лінійні схеми — усереднення зшиває їх у одну")


def fig_perturbation():
    """Вставка math: лінеаризація навколо робочої точки. Вигнута крива Vвих(D),
    дотична в точці D0; мала гойданка d̂ рухає систему вздовж дотичної (лінійна
    купка ②), а відкинуті добутки d̂·x̂ — то зазор між кривою й дотичною."""
    W, H = 900, 420
    frags = []
    # осі
    ox, oy = 90, 330            # початок координат
    axw, axh = 720, 250
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))          # вісь D
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))          # вісь Vвих
    frags.append(text(ox + axw - 4, oy + 24, "D (шпаруватість)", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 14, oy - axh + 6, "Vвих", size=12, color=INK, anchor="end", bold=True))

    # нелінійна крива Vвих(D) — беремо boost-подібну Vвх/(1−D), круто вигнуту
    import math as _m
    Vin = 1.0
    pts = []
    for i in range(0, 86):                       # D від 0 до 0.85 (щоб не вибухнула)
        D = i / 100.0
        V = Vin / (1.0 - D)
        px = ox + D * (axw / 0.9)
        py = oy - (V - 1.0) * 34                 # масштаб під вигин
        if py < oy - axh + 10:
            break
        pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), INK))
    frags.append(text(ox + 0.80 * (axw / 0.9), oy - 165, "справжня крива Vвих(D)", size=12,
                      color=INK, anchor="middle", bold=True))

    # робоча точка D0
    D0 = 0.5
    V0 = Vin / (1.0 - D0)
    pxD0 = ox + D0 * (axw / 0.9)
    pyV0 = oy - (V0 - 1.0) * 34
    # похідна dV/dD = Vin/(1-D)^2 → нахил у px/py-координатах
    slope_real = Vin / (1.0 - D0) ** 2           # dV/dD
    # у пікселях: dpy/dpx = -(34*slope_real)/(axw/0.9)
    kpx = axw / 0.9
    dpy_dpx = -(34.0 * slope_real) / kpx
    # дотична — відрізок навколо точки
    tx1, tx2 = pxD0 - 150, pxD0 + 150
    ty1 = pyV0 + dpy_dpx * (tx1 - pxD0)
    ty2 = pyV0 + dpy_dpx * (tx2 - pxD0)
    frags.append(line(tx1, ty1, tx2, ty2, color=GOLD, sw=2.4, dash="7 4"))
    frags.append(text(tx2 + 4, ty2 + 4, "дотична в D₀", size=12, color=GOLD, anchor="start", bold=True))

    # велике коло — робоча точка
    frags.append(circle(pxD0, pyV0, 8, fill="#fff8e6", stroke=GOLD, sw=2.6))
    frags.append(text(pxD0 - 12, pyV0 - 14, "(X, D₀) — робоча точка", size=12, color=GOLD, anchor="end", bold=True))
    # пунктири до осей
    frags.append(line(pxD0, pyV0, pxD0, oy, color=MUTED, sw=1.2, dash="3 3"))
    frags.append(line(pxD0, pyV0, ox, pyV0, color=MUTED, sw=1.2, dash="3 3"))
    frags.append(text(pxD0, oy + 18, "D₀", size=12, color=MUTED))
    frags.append(text(ox - 10, pyV0 + 4, "V₀", size=12, color=MUTED, anchor="end"))

    # мала гойданка d̂ уздовж дотичної
    dd = 70
    gx1, gx2 = pxD0 - dd, pxD0 + dd
    gy1 = pyV0 + dpy_dpx * (gx1 - pxD0)
    gy2 = pyV0 + dpy_dpx * (gx2 - pxD0)
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3.2" '
                 'marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                 % (gx1, gy1, gx2, gy2, POS))
    frags.append(text(pxD0 + 6, pyV0 + 44, "мала гойданка d̂  →  v̂ уздовж дотичної", size=12,
                      color=POS, anchor="start", bold=True))

    # зазор між кривою й дотичною праворуч (відкинуті члени d̂·x̂)
    Dg = 0.72
    Vg = Vin / (1.0 - Dg)
    pxg = ox + Dg * kpx
    pyg_curve = oy - (Vg - 1.0) * 34
    pyg_tan = pyV0 + dpy_dpx * (pxg - pxD0)
    frags.append(line(pxg, pyg_curve, pxg, pyg_tan, color=NEG, sw=2.0))
    frags.append(text(pxg + 8, (pyg_curve + pyg_tan) / 2,
                      "зазор ≈ d̂·x̂ — відкидаємо", size=11, color=NEG, anchor="start", bold=True))

    # підпис коефіцієнта нахилу
    b, bw, bh = textbox(300, 392, "нахил дотичної = (A₁−A₂)·X + (B₁−B₂)·U  —  сила, з якою керування штовхає стан",
                        size=12, fill="#fff8e6", stroke=GOLD, sw=1.8, color=INK, pad=10)
    frags.append(b)
    render(os.path.join(OUT, "perturbation.svg"), W, H, *frags,
           title="Лінеаризація: крихітна гойданка d̂ бачить лише дотичну в робочій точці")


if __name__ == "__main__":
    fig_linearize()
    fig_control_to_output()
    fig_bode_features()
    fig_rhp_zero()
    fig_hist_genealogy()
    fig_hist_averaging_idea()
    fig_two_networks()
    fig_perturbation()
    print("ok figs")
