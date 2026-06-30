# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Мура» (аналогова електроніка, кутом теорії кіл).
Дві фігури:
  cost-curve.svg — U-подібна крива вартості одного транзистора; дно повзе праворуч щороку
  dennard.svg    — масштабування Денарда: розміри ÷κ, напруга ÷κ → густина потужності стала
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def moore_1965():
    """Графік Мура 1965: п'ять точок 1959–1965 на лог-осі, пряма до 65 000 у 1975."""
    W, H = 720, 470
    p = []
    ox, oy = 95, 360          # початок осей (лівий-нижній)
    aw, ah = 540, 280         # довжина осей

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))          # X: рік
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))          # Y: log2(складники)
    p.append(text(ox + aw / 2, oy + 44, "рік  →", size=13, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'складників на кристалі (подвоєння = +1 поділка)  →</text>'
             % (ox - 64, oy - ah / 2, FONT, INK, ox - 64, oy - ah / 2))

    year0, year1 = 1959, 1975
    def X(yr):  return ox + (yr - year0) / (year1 - year0) * aw
    # вісь Y у показниках двійки: 2^0 … 2^16
    EXP_MAX = 16
    def Y(exp): return oy - exp / EXP_MAX * (ah - 18)

    # підписи Y: степені двійки
    for e, lab in [(0, "1"), (4, "16"), (8, "256"), (12, "4 096"), (16, "65 000")]:
        yy = Y(e)
        p.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.5))
        p.append(text(ox - 12, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    # роки на осі X
    for yr in (1959, 1962, 1965, 1970, 1975):
        xx = X(yr)
        p.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.5))
        p.append(text(xx, oy + 22, str(yr), size=11, color=MUTED))

    # п'ять реальних точок 1959–1965: подвоєння щороку → exp = рік-1959
    data = [(1959, 0), (1960, 1), (1961, 2), (1962, 3), (1963, 4), (1964, 5), (1965, 6)]
    # пряма-екстраполяція до 1975 (exp=16) — пунктир
    p.append(line(X(1959), Y(0), X(1975), Y(16), color=POS, sw=2.2, dash="7 5"))
    # суцільний відрізок крізь виміряні точки 1959–1965
    p.append(line(X(1959), Y(0), X(1965), Y(6), color=INK, sw=2.6))

    for yr, e in data:
        p.append(circle(X(yr), Y(e), 5, fill=INK, stroke=INK, sw=1))
    # підпис «виміряні точки»
    p.append(text(X(1962), Y(3) - 16, "виміряно: 1959–1965", size=11.5, bold=True, anchor="start"))

    # ціль 1975
    p.append(circle(X(1975), Y(16), 6, fill="#fdecea", stroke=POS, sw=2.4))
    p.append(text(X(1975) - 6, Y(16) - 14, "65 000 складників", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(X(1975) - 6, Y(16) + 2, "екстраполяція до 1975", size=10.5, color=POS, anchor="end"))

    b, _, _ = textbox(W / 2, 440,
                      "Уся теорія Мура — пряма крізь жменьку точок: подвоєння щороку.\n"
                      "На лог-осі експонента стає прямою; продовж її — і ось 65 000 до 1975.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'moore-1965.svg'), W, H, *p,
           title="Графік 1965 року: пряма крізь п'ять точок — і прогноз на десять років")


def cost_curve():
    """Три U-подібні криві (роки) у логарифмічних осях; дно щороку зсувається праворуч."""
    W, H = 720, 430
    p = []
    ox, oy = 95, 320          # початок осей
    aw, ah = 520, 250         # довжина осей

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))          # X: складність (лог)
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))          # Y: вартість 1 транзистора (лог)
    p.append(text(ox + aw / 2, oy + 42, "число складників на кристалі  →", size=13, bold=True))
    p.append(text(ox + aw / 2, oy + 60, "(логарифмічна шкала)", size=11, color=MUTED))
    # підпис осі Y — вертикально
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'вартість одного транзистора  →</text>'
             % (ox - 60, oy - ah / 2, FONT, INK, ox - 60, oy - ah / 2))

    # три криві: кожна — парабола в лог-лог координатах, дно зсунуте праворуч і нижче
    # (вартість на дні щороку падає, оптимум зсувається праворуч → подвоєння)
    curves = [
        ("рік t",     0.30, 0.62, MUTED),     # дно зліва, вище
        ("рік t+2",   0.50, 0.42, NEG),       # дно посередині
        ("рік t+4",   0.70, 0.24, FIELD),     # дно праворуч, найнижче
    ]
    def px(fx):  return ox + 30 + (aw - 60) * fx
    def py(fy):  return oy - 20 - (ah - 40) * fy

    for lbl, x_min, y_min, col in curves:
        pts = []
        N = 60
        for k in range(N + 1):
            fx = 0.04 + 0.92 * k / N
            # парабола з вершиною (x_min, y_min); вгору розходиться в обидва боки
            fy = y_min + 3.4 * (fx - x_min) ** 2
            if fy > 0.98:
                continue
            pts.append((px(fx), py(fy)))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        # позначка дна
        bx, by = px(x_min), py(y_min)
        p.append(circle(bx, by, 4.5, fill=col, stroke=col, sw=1))
        p.append(text(px(curves[-1][1]) + 40, by + 4, lbl, size=12, bold=True, color=col, anchor="start"))

    # стрілка «дно повзе праворуч»
    y0 = py(curves[0][2])
    y2 = py(curves[2][2])
    p.append(arrow(px(curves[0][1]) + 6, y0 + 22, px(curves[2][1]) - 6, y2 + 22, color=INK, sw=2))
    p.append(text((px(curves[0][1]) + px(curves[2][1])) / 2, y2 + 50,
                  "оптимум (дно) щороку зсувається праворуч: вдвічі більше складників — найдешевше",
                  size=11.5, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 405,
                      "Закон Мура — про рух ДНА цієї кривої: найвигідніша складність подвоюється.\n"
                      "Не «можна напхати вдвічі більше», а «вдвічі більше тепер найдешевше за транзистор».",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'cost-curve.svg'), W, H, *p,
           title="Чому закон Мура — про гроші: дно кривої вартості повзе праворуч")


def dennard():
    """Масштабування Денарда: до vs після зменшення в κ; густина потужності стала."""
    W, H = 720, 470
    p = []
    cy = 150

    # ── ліворуч: «до» — один великий транзистор-комірка ──
    def cell(cx, top, side, col, fillc, glbl, vlbl):
        out = []
        out.append(rect(cx - side / 2, top, side, side, fill=fillc, stroke=col, sw=2.2))
        out.append(text(cx, top + side / 2 + 5, "C·V²·f", size=13, bold=True, color=col))
        out.append(text(cx, top - 12, glbl, size=12, bold=True))
        out.append(text(cx, top + side + 20, vlbl, size=11, color=MUTED))
        return out

    # «до»: велика комірка
    p += cell(150, 70, 120, NEG, "#eaf0fd", "до зменшення",
              "розмір L, напруга V")
    p.append(text(150, 230, "потужність  P", size=12, bold=True, color=NEG))

    # стрілка масштабування
    p.append(arrow(245, 130, 335, 130, color=INK, sw=2.4))
    p.append(text(290, 116, "÷κ розміри", size=12, bold=True))
    p.append(text(290, 152, "÷κ напруга", size=12, bold=True, color=POS))

    # «після»: чотири маленькі комірки на тій самій площі (κ=2 → ×4 штук)
    bx, by = 360, 70
    half = 58
    gap = 4
    for i in range(2):
        for j in range(2):
            x = bx + i * (half + gap)
            y = by + j * (half + gap)
            p.append(rect(x, y, half, half, fill="#eafaf0", stroke=FIELD, sw=1.8))
            p.append(text(x + half / 2, y + half / 2 + 4, "P/κ²", size=11, bold=True, color=FIELD))
    p.append(text(bx + half + gap / 2, by - 12, "після (κ=2)", size=12, bold=True))
    p.append(text(bx + half + gap / 2, by + 2 * half + gap + 20,
                  "та сама площа — але транзисторів ×κ²", size=11, color=MUTED))

    # ── розрахунок під фігурою: формула й скорочення κ² ──
    fy = 300
    p.append(line(60, fy - 22, W - 60, fy - 22, color=MUTED, sw=1, dash="4 4"))
    p.append(text(W / 2, fy, "P ≈ C · V² · f      зменшуємо: C→C/κ,  V→V/κ,  f→f·κ",
                  size=14, bold=True))
    p.append(text(W / 2, fy + 30,
                  "потужність 1 транзистора:  (C/κ)·(V/κ)²·(f·κ) = C·V²·f / κ²   (падає в κ²)",
                  size=13, color=NEG))
    p.append(text(W / 2, fy + 56,
                  "транзисторів на тій самій площі:  ×κ²        →        κ² скорочується",
                  size=13, color=FIELD))

    b, _, _ = textbox(W / 2, fy + 96,
                      "Густина потужності лишається СТАЛОЮ: вдвічі щільніше, помітно швидше —\n"
                      "і гріється не сильніше. Оце й тримало закон Мура десятиліттями.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'dennard.svg'), W, H, *p,
           title="Масштабування Денарда: чому дрібніше виходило і швидше, і не гарячіше")


def doubling_three():
    """Одна крива 2^(t/T) — три імені: кратність ×2, миттєвий темп e^(rt), річний CAGR."""
    W, H = 720, 470
    p = []
    ox, oy = 95, 330
    aw, ah = 540, 250

    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))            # X: час (роки)
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))           # Y: кратність
    p.append(text(ox + aw / 2, oy + 40, "час, роки  →", size=13, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'кратність  N/N₀  →</text>'
             % (ox - 58, oy - ah / 2, FONT, INK, ox - 58, oy - ah / 2))

    T = 2.0
    years = 6.0              # показуємо три періоди
    ymax = 8.5               # 2^3 = 8 трохи з запасом
    def px(t):  return ox + (aw - 20) * t / years
    def py(v):  return oy - (ah - 20) * v / ymax

    # сама крива 2^(t/T)
    pts = []
    N = 80
    for k in range(N + 1):
        t = years * k / N
        v = 2.0 ** (t / T)
        pts.append((px(t), py(v)))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, FIELD))

    # опорні точки подвоєнь: t=0,2,4,6 → v=1,2,4,8
    for k in range(4):
        t = 2.0 * k
        v = 2.0 ** k
        x, y = px(t), py(v)
        p.append(line(x, oy, x, y, color=MUTED, sw=1, dash="3 3"))
        p.append(circle(x, y, 4.5, fill=FIELD, stroke=FIELD, sw=1))
        p.append(text(x, y - 12, "×%d" % v, size=12, bold=True, color=FIELD))
        if k > 0:
            p.append(text(x, oy + 18, "%d р" % t, size=10.5, color=MUTED))

    # дужка «один рік = ×√2», коло t=0..1
    x0, x1 = px(0), px(1)
    yb = py(2.0 ** 0.5) - 4
    p.append(line(x0, yb, x1, yb, color=POS, sw=1.6))
    p.append(line(x0, yb, x0, yb + 7, color=POS, sw=1.6))
    p.append(line(x1, yb, x1, yb + 7, color=POS, sw=1.6))
    p.append(text(x1 + 6, yb - 5, "1 рік = ×√2 ≈ 1.41", size=11, bold=True, color=POS, anchor="start"))

    # три імені — легенда-рамка праворуч угорі
    b, _, _ = textbox(ox + aw - 165, oy - ah + 54,
                      "та сама крива, три імені:\n"
                      "•  ×2 за T = 2 роки\n"
                      "•  e^(rt),  r = ln2/T ≈ 34.7%/рік\n"
                      "•  +CAGR щороку, √2−1 ≈ 41.4%",
                      size=11.5, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    b2, _, _ = textbox(W / 2, 444,
                       "41%, а не «половина від подвоєння»: два роки дають ×2, отже один рік — √2.\n"
                       "Множники діляться навпіл коренем, а не навпіл арифметично.",
                       size=12, fill=FILL, stroke=INK)
    p.append(b2)
    render(os.path.join(OUT, 'doubling-three.svg'), W, H, *p,
           title="Одна крива подвоєння — три способи назвати її темп")


def linear_vs_exp():
    """Лінія (додаємо) проти експоненти (множимо): однаковий старт, прірва на хвості."""
    W, H = 720, 450
    p = []
    ox, oy = 95, 320
    aw, ah = 540, 250

    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    p.append(text(ox + aw / 2, oy + 40, "кроки (рівні проміжки часу)  →", size=13, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'величина  →</text>'
             % (ox - 56, oy - ah / 2, FONT, INK, ox - 56, oy - ah / 2))

    steps = 10
    ymax = 16.0
    def px(s):  return ox + (aw - 20) * s / steps
    def py(v):  return oy - (ah - 20) * min(v, ymax) / ymax

    # лінійна: +1.5 за крок (старт 1)
    linpts = [(px(s), py(1 + s * 1.5)) for s in range(steps + 1)]
    dl = "M" + " L".join("%.1f %.1f" % q for q in linpts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (dl, NEG))

    # експонента: ×√2 за крок (старт 1) — ліворуч майже збігається з лінією
    exppts = []
    for s in range(steps + 1):
        v = 2.0 ** (s / 2.0)
        if v <= ymax:
            exppts.append((px(s), py(v)))
        else:
            exppts.append((px(s), py(ymax)))
            break
    de = "M" + " L".join("%.1f %.1f" % q for q in exppts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (de, FIELD))

    # підписи кривих
    p.append(text(px(steps) - 4, py(1 + steps * 1.5) + 16, "лінія: +порція", size=12, bold=True, color=NEG, anchor="end"))
    p.append(text(px(6) + 8, py(2.0 ** 3.0), "експонента: ×коефіцієнт", size=12, bold=True, color=FIELD, anchor="start"))

    # межа «лівого краю», де криві майже збігаються
    xL = px(3)
    p.append(line(xL, oy, xL, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text((ox + xL) / 2, oy - ah + 14, "тут око їх плутає", size=10.5, color=MUTED))

    b, _, _ = textbox(W / 2, 420,
                      "Однаковий старт зліва — прірва справа. Лінія щокроку додає те саме;\n"
                      "експонента подвоює вже накопичене. Око, привчене до лівого краю, недооцінює правий.",
                      size=12, fill=FILL, stroke=INK)
    p.append(b)
    render(os.path.join(OUT, 'linear-vs-exp.svg'), W, H, *p,
           title="Сліпота до експонент: додати порцію ≠ помножити на коефіцієнт")


def present_value():
    """Спадна ціна 2^(−t/T); два проєкти зводяться до тієї самої наведеної вартості."""
    W, H = 720, 450
    p = []
    ox, oy = 95, 320
    aw, ah = 540, 250

    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    p.append(text(ox + aw / 2, oy + 40, "час до виходу виробу, роки  →", size=13, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'ціна одного транзистора  →</text>'
             % (ox - 58, oy - ah / 2, FONT, INK, ox - 58, oy - ah / 2))

    T = 2.0
    years = 6.0
    def px(t):  return ox + (aw - 20) * t / years
    def py(v):  return oy - (ah - 20) * v   # v у частках від початкової ціни (0..1)

    # крива ціни 2^(-t/T)
    pts = []
    Nn = 80
    for k in range(Nn + 1):
        t = years * k / Nn
        v = 2.0 ** (-t / T)
        pts.append((px(t), py(v)))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    p.append(text(px(years) - 4, py(2.0 ** (-years / T)) - 10, "ціна ÷2 кожні 2 роки",
                  size=11.5, bold=True, color=POS, anchor="end"))

    # дві опорні точки: зараз (t=0, ціна 1) і через 2 роки (t=2, ціна 1/2)
    for t, v, lbl in [(0.0, 1.0, "зараз: 1×ціна"), (2.0, 0.5, "за 2 роки: ½×ціна")]:
        x, y = px(t), py(v)
        p.append(line(x, oy, x, y, color=MUTED, sw=1, dash="3 3"))
        p.append(circle(x, y, 4.5, fill=POS, stroke=POS, sw=1))
        p.append(text(x + 8, y - 8, lbl, size=11, bold=True, anchor="start"))

    # рамка-висновок про два проєкти
    b, _, _ = textbox(ox + aw - 158, oy - ah + 72,
                      "Проєкт A: 1 млн транзисторів, вихід ЗАРАЗ.\n"
                      "Проєкт B: 2 млн, але вихід через 2 роки.\n"
                      "За 2 роки ціна впала ÷2 → наведена\n"
                      "вартість кремнію В ОБОХ ОДНАКОВА.",
                      size=11.5, fill="#fdecea", stroke=POS)
    p.append(b)

    b2, _, _ = textbox(W / 2, 420,
                       "Майбутню ціну зводь до сьогодні множником e^(−rt). Подвоєння потреби\n"
                       "гаситься піврозпадом ціни — порівнюй проєкти, звівши їх до спільного моменту.",
                       size=12, fill=FILL, stroke=INK)
    p.append(b2)
    render(os.path.join(OUT, 'present-value.svg'), W, H, *p,
           title="Наведена вартість: майбутній дешевий транзистор, зведений на сьогодні")


if __name__ == '__main__':
    moore_1965()
    cost_curve()
    dennard()
    doubling_three()
    linear_vs_exp()
    present_value()
    print("OK: 6 figures ->", OUT)
