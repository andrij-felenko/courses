# -*- coding: utf-8 -*-
"""Фігури теми «Час у ядрі: тики, монотонний годинник і джерела часу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Два питання про час — дві апаратні здатності ─────────────────────────
def fig_two_questions():
    W, H = 1000, 600
    f = []

    lx, rx, bw = 40, 530, 430

    f.append(fitbox(lx, 60, bw, 84,
                    "Питання 1\nкотра зараз мить?", size=17, bold=True, fill="#eaf0fd"))
    f.append(fitbox(rx, 60, bw, 84,
                    "Питання 2\nвіддай керування о заданій миті", size=17, bold=True,
                    fill="#fdecea"))

    f.append(arrow(lx + bw / 2, 152, lx + bw / 2, 196))
    f.append(arrow(rx + bw / 2, 152, rx + bw / 2, 196))

    f.append(fitbox(lx, 200, bw, 84,
                    "потрібен вільнобіжний лічильник,\nякий можна прочитати", size=15))
    f.append(fitbox(rx, 200, bw, 84,
                    "потрібен компаратор, який сам\nпідніме переривання в потрібну мить", size=15))

    f.append(arrow(lx + bw / 2, 292, lx + bw / 2, 336))
    f.append(arrow(rx + bw / 2, 292, rx + bw / 2, 336))

    f.append(fitbox(lx, 340, 920, 96,
                    "ОДНЕ періодичне переривання відповідало на обидва питання\n"
                    "ціна: роздільність часу дорівнює періоду тику · переривання приходять і тоді, коли нікому не потрібні",
                    size=15, bold=True, fill="#fdf6e3"))

    f.append(arrow(lx + bw / 2, 444, lx + bw / 2, 488))
    f.append(arrow(rx + bw / 2, 444, rx + bw / 2, 488))

    f.append(fitbox(lx, 492, bw, 84,
                    "джерело часу (clocksource)\nтільки рахує, нікого не перериває", size=15,
                    fill="#eaf0fd"))
    f.append(fitbox(rx, 492, bw, 84,
                    "пристрій часових подій\nтільки перериває, нічого не рахує", size=15,
                    fill="#fdecea"))

    render(os.path.join(OUT, 'two-questions.svg'), W, H, *f)


# ── 2. Родина системних годинників на одній осі ─────────────────────────────
def fig_clock_family():
    W, H = 1020, 520
    f = []

    x0, x1 = 120, 700          # вісь часу
    y_zero = 250               # нульова похибка
    ux = (x1 - x0) / 10.0      # px на умовну секунду реального часу
    uy = 62.0                  # px на секунду похибки

    def X(t):
        return x0 + t * ux

    def Y(v):
        return y_zero - v * uy

    # смуга призупинення
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f0f0f0"/>'
             % (X(6), 96, X(7.5) - X(6), 330 - 96))

    # осі
    f.append(line(x0, 96, x0, 400, color=MUTED, sw=1.2))
    f.append(line(x0, 400, x1 + 14, 400, color=MUTED, sw=1.2))
    f.append(text(x0 - 6, 88, "показ годинника мінус справжній час, с",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(x1 + 14, 418, "реальний час →", size=12, color=MUTED, anchor="end"))

    for v in (1, 0, -1, -2):
        f.append(line(x0 - 5, Y(v), x0, Y(v), color=MUTED, sw=1.2))
        f.append(text(x0 - 10, Y(v) + 4, "%+d" % v if v else "0", size=12,
                      color=MUTED, anchor="end"))
        if v:
            f.append(line(x0, Y(v), x1, Y(v), color="#e3e3e3", sw=1))
    f.append(line(x0, Y(0), x1, Y(0), color="#cccccc", sw=1))

    def poly(pts, color, sw, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % (X(t), Y(v)) for t, v in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (s, color, sw, d))

    # BOOTTIME — рахує все, похибка нульова
    f.append(poly([(0, 0), (10, 0)], FIELD, 5.5))
    # MONOTONIC — зупиняється на час призупинення
    f.append(poly([(0, 0), (6, 0), (7.5, -1.5), (10, -1.5)], NEG, 2.6))
    # MONOTONIC_RAW — та сама зупинка плюс власний дрейф генератора
    f.append(poly([(0, 0), (6, 0.3), (7.5, -1.13), (10, -1.0)], MUTED, 2.0, dash="7,5"))
    # REALTIME — поспішав, потім його переставили назад
    f.append(poly([(0, 0.8), (3, 0.8), (3, 0), (10, 0)], POS, 2.0, dash="3,4"))

    # підписи подій під віссю
    f.append(line(X(3), 96, X(3), 400, color=MUTED, sw=1, dash="4,4"))
    f.append(text(X(3), 440, "службу синхронізації запущено:", size=12, anchor="middle"))
    f.append(text(X(3), 458, "настінний час переставлено назад", size=12, anchor="middle"))
    f.append(text(X(6.75), 440, "систему", size=12, anchor="middle"))
    f.append(text(X(6.75), 458, "призупинено", size=12, anchor="middle"))

    # легенда
    lx, ly = 752, 118
    rows = [
        (FIELD, 5.5, None, ["CLOCK_BOOTTIME", "рахує і час сну"]),
        (NEG, 2.6, None, ["CLOCK_MONOTONIC", "на час сну спиняється"]),
        (MUTED, 2.0, "7,5", ["CLOCK_MONOTONIC_RAW", "без поправки швидкости"]),
        (POS, 2.0, "3,4", ["CLOCK_REALTIME", "його переставляють"]),
    ]
    for i, (color, sw, dash, lines) in enumerate(rows):
        y = ly + i * 74
        f.append(line(lx, y, lx + 46, y, color=color, sw=sw, dash=dash))
        f.append(mtext(lx + 58, y - 4, lines, size=13, anchor="start", lh=1.45))

    render(os.path.join(OUT, 'clock-family.svg'), W, H, *f)


# ── 3. Шлях від тактів до всіх системних годинників ─────────────────────────
def fig_read_path():
    W, H = 1000, 480
    f = []

    px, pw = 40, 300
    steps = [
        "прочитати лічильник",
        "відняти базу тактів",
        "помножити на mult,\nзсунути на shift",
        "додати базу наносекунд",
    ]
    for i, s in enumerate(steps):
        y = 70 + i * 80
        f.append(fitbox(px, y, pw, 60, s, size=14))
        if i < len(steps) - 1:
            f.append(arrow(px + pw / 2, y + 60, px + pw / 2, y + 78))

    f.append(arrow(px + pw / 2, 370, px + pw / 2, 388))
    f.append(fitbox(px, 392, pw, 56, "монотонний час від старту", size=15, bold=True,
                    fill="#eaf0fd"))

    # спинна лінія до годинників
    spine = 470
    f.append(line(px + pw, 420, spine, 420, color=LINE, sw=1.8))
    f.append(line(spine, 420, spine, 102, color=LINE, sw=1.8))

    clocks = [
        ("CLOCK_MONOTONIC", "без зміщення"),
        ("CLOCK_BOOTTIME", "+ час, проведений уві сні"),
        ("CLOCK_REALTIME", "+ зміщення до 1 січня 1970 року"),
        ("CLOCK_TAI", "+ зміщення атомної шкали"),
    ]
    cx, cw = 560, 400
    for i, (name, off) in enumerate(clocks):
        y = 70 + i * 90
        f.append(arrow(spine, y + 32, cx, y + 32))
        f.append(fitbox(cx, y, cw, 64, name + "\n" + off, size=14, fill="#f4f6f8"))

    render(os.path.join(OUT, 'read-path.svg'), W, H, *f)


# ── 4. Періодичний тик проти одноразових пробуджень ─────────────────────────
def fig_tick_vs_oneshot():
    W, H = 1000, 440
    f = []

    ax0, ax1 = 90, 830

    def timeline(y, marks, title, note, color):
        out = [text(ax0, y - 34, title, size=15, bold=True, anchor="start"),
               line(ax0, y, ax1, y, color=MUTED, sw=1.4)]
        for m in marks:
            x = ax0 + (ax1 - ax0) * m
            out.append(line(x, y - 16, x, y + 16, color=color, sw=2.4))
        out.append(text(ax0, y + 46, note, size=13, color=MUTED, anchor="start"))
        return out

    f += timeline(140, [i / 25.0 for i in range(26)],
                  "періодичний тик, HZ = 250",
                  "250 переривань за секунду простою — майже жодне з них нікому не потрібне",
                  POS)

    f += timeline(290, [0.22, 0.55, 0.93],
                  "одноразові пробудження за термінами",
                  "3 переривання — рівно ті миті, на які хтось справді чекав",
                  FIELD)

    f.append(text((ax0 + ax1) / 2, 372, "одна секунда простою", size=13, color=MUTED))
    f.append(line(ax0, 388, ax1, 388, color=MUTED, sw=1.2))
    f.append(line(ax0, 382, ax0, 394, color=MUTED, sw=1.2))
    f.append(line(ax1, 382, ax1, 394, color=MUTED, sw=1.2))

    render(os.path.join(OUT, 'tick-vs-oneshot.svg'), W, H, *f)


# ── 5. Ланцюг: виміряна ціна → відповідь (для вставки hist) ─────────────────
def fig_tick_history():
    rows = [
        ("1970-ті\nPDP-11",
         "апаратура дає тільки переривання від мережі —\n50 або 60 разів на секунду, читати нічого",
         "лічити ці переривання:\nзмінна lbolt у шостій редакції Unix"),
        ("1991+\nLinux",
         "тик — і годинник, і мить, коли ядро\nгарантовано дістає керування",
         "jiffies і HZ, задане при складанні ядра"),
        ("2005\n2.6.13",
         "роздільність дорівнює періоду тику,\nа 1000 Гц коштує 8.15 Вт замість 7.59 Вт",
         "HZ стало налаштовним;\nтипове значення на i386 — 250"),
        ("2006\n2.6.16",
         "жодне єдине значення HZ не влаштовує\nі ноутбук, і студію звукозапису",
         "hrtimers: термін задають миттю\nв наносекундах, а не номером тику"),
        ("2006\n2.6.18",
         "джерело часу вшите в код кожної архітектури\nокремо, спільної основи немає",
         "узагальнений час доби (GTOD):\nодне джерело часу на всіх"),
        ("2007\n2.6.21",
         "переривання приходить і тоді,\nколи на нього ніхто не чекає",
         "шар пристроїв подій + NO_HZ_IDLE:\nу простої періодичного тику немає"),
        ("2013\n3.10",
         "на зайнятому ядрі тик псує затримку\nі вимір однозадачного навантаження",
         "NO_HZ_FULL: тик знімають і з зайнятого ядра;\nціна — приблизний облік часу"),
    ]

    W, H = 1120, 60 + len(rows) * 108
    f = []

    yx, cx, cw, ax, aw = 90, 150, 420, 630, 450
    for i, (year, cost, answer) in enumerate(rows):
        y = 40 + i * 108
        f.append(mtext(yx, y + 30, year.split("\n"), size=14, bold=True, lh=1.4))
        f.append(fitbox(cx, y, cw, 80, cost, size=13, fill="#fdecea"))
        f.append(arrow(cx + cw + 14, y + 40, ax - 14, y + 40))
        f.append(fitbox(ax, y, aw, 80, answer, size=13, fill="#eaf0fd"))

    f.append(text(cx + cw / 2, H - 22, "виміряна ціна попереднього кроку", size=13,
                  color=MUTED))
    f.append(text(ax + aw / 2, H - 22, "чим на неї відповіли", size=13, color=MUTED))

    render(os.path.join(OUT, 'tick-history.svg'), W, H, *f)


# ── Ціна одного запиту часу трьома шляхами (вставка proj-clock-lab) ─────────
def fig_cost_ladder():
    import math

    W, H = 1140, 400
    f = []

    x0, x1 = 300, 750          # 1 нс … 1000 нс
    dec = (x1 - x0) / 3.0      # px на десяткову декаду

    def X(v):
        return x0 + dec * math.log10(v)

    rows = [
        (110, 4.3, "CLOCK_MONOTONIC_COARSE", "≈4 нс", FIELD,
         ["лічильника не читає взагалі —",
          "бере готове число зі спільної сторінки"]),
        (190, 21.7, "CLOCK_MONOTONIC (vDSO)", "≈22 нс", NEG,
         ["читає лічильник, множить, зсуває —",
          "усе в просторі користувача"]),
        (270, 438.9, "syscall(SYS_clock_gettime)", "≈440 нс", POS,
         ["та сама арифметика, але з переходом",
          "у режим ядра й назад"]),
    ]

    for yc, v, label, val, color, note in rows:
        f.append(text(282, yc + 5, label, size=14, anchor="end"))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="36" rx="4" '
                 'fill="%s" opacity="0.85"/>' % (x0, yc - 18, X(v) - x0, color))
        f.append(text(X(v) + 10, yc + 5, val, size=13, bold=True, anchor="start"))
        f.append(mtext(800, yc - 4, note, size=12, color=MUTED, anchor="start", lh=1.5))

    f.append(line(x0, 320, x1 + 10, 320, color=MUTED, sw=1.2))
    for v, lab in ((1, "1"), (10, "10"), (100, "100"), (1000, "1000 нс")):
        f.append(line(X(v), 314, X(v), 326, color=MUTED, sw=1.2))
        f.append(text(X(v), 348, lab, size=12, color=MUTED))

    render(os.path.join(OUT, 'cost-ladder.svg'), W, H, *f,
           title="ціна одного запиту часу: логарифмічна шкала, менше — краще")


# ── 64 біти добутку: розряди наносекунд проти shift (вставка math) ─────────
def fig_mult_shift_budget():
    W, H = 1160, 434
    f = []

    f.append(text(W / 2, 34,
                  "такти · mult = нс · 2^shift — і цей добуток мусить улізти в 64 біти",
                  size=16, bold=True))

    barx, barw = 240, 600
    rows = [
        ("пауза до 178 с\n24 МГц, 32 біти", 38, 26,
         "mult = 2 796 202 667\nпохибка округлення +0.12 ppb"),
        ("пауза до 600 с\nTSC 3 ГГц, межа ядра", 40, 24,
         "mult = 5 592 405\nпохибка округлення −60 ppb"),
        ("пауза до 195 років\nTSC 3 ГГц без межі", 63, 1,
         "коефіцієнт вироджується в mult = 1:\nтакт зараховано в пів наносекунди"),
    ]

    for i, (label, nsb, sft, note) in enumerate(rows):
        y = 68 + i * 112
        f.append(fitbox(26, y, 196, 54, label, size=13))
        wns = barw * nsb / 64.0
        f.append(rect(barx, y + 4, wns, 44, fill="#eaf0fd", rx=3))
        f.append(rect(barx + wns, y + 4, barw - wns, 44, fill="#eafaf0", rx=3))
        f.append(text(barx + wns / 2, y + 32,
                      "наносекунди: %d розрядів" % nsb, size=13))
        if barw - wns >= 120:
            f.append(text(barx + wns + (barw - wns) / 2, y + 32,
                          "shift = %d" % sft, size=13, bold=True))
        else:
            f.append(line(barx + barw - 5, y + 48, barx + barw - 5, y + 58,
                          color=MUTED, sw=1.2))
            f.append(text(barx + barw - 12, y + 74, "shift = %d" % sft,
                          size=13, bold=True, anchor="end"))
        f.append(fitbox(870, y, 262, 54, note, size=12))

    f.append(text(W / 2, H - 16,
                  "кожне подвоєння дозволеної паузи забирає рівно один розряд у коефіцієнта",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'mult-shift-budget.svg'), W, H, *f)


# ── Кільце лишків: різниця тактів через оберт (вставка math) ────────────────
def fig_mask_wrap():
    import math

    W, H = 1060, 500
    cx, cy, r = 320, 278, 150
    f = []

    def polar(rad, deg):
        a = math.radians(deg)
        return cx + rad * math.cos(a), cy + rad * math.sin(a)

    def arc(rad, a0, a1, color, sw, marker=False):
        x0, y0 = polar(rad, a0)
        x1, y1 = polar(rad, a1)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        m = ' marker-end="url(#arrow)"' if marker else ''
        return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d 1 %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f"%s/>'
                % (x0, y0, rad, rad, large, x1, y1, color, sw, m))

    A_LAST, A_NOW = 247.5, -67.5

    f.append(arc(r, A_LAST, A_LAST + 180, FIELD, 13))
    f.append(arc(r, A_LAST + 180, A_LAST + 360, POS, 13))

    for deg, lab, ax_, ay_, anch in (
            (-90, "0 = 2³² — точка обороту", cx, cy - r - 50, "middle"),
            (0, "2³⁰", cx + r + 16, cy + 5, "start"),
            (90, "2³¹", cx, cy + r + 32, "middle"),
            (180, "3·2³⁰", cx - r - 16, cy + 5, "end")):
        tx, ty = polar(r + 9, deg)
        f.append(text(ax_, ay_, lab, size=13, color=MUTED, anchor=anch))

    lx, ly = polar(r, A_LAST)
    nx, ny = polar(r, A_NOW)
    ox, oy = polar(r, A_LAST + 180)
    f.append(line(lx, ly, ox, oy, color=MUTED, sw=1.3, dash="7,5"))
    f.append(circle(lx, ly, 7, fill=INK, stroke=INK))
    f.append(circle(nx, ny, 7, fill=INK, stroke=INK))
    f.append(circle(ox, oy, 5, fill=BG, stroke=MUTED, sw=1.5))

    tx, ty = polar(r + 34, A_LAST)
    f.append(text(tx, ty, "last", size=14, bold=True, anchor="end"))
    f.append(text(tx, ty + 18, "0xF000_0000", size=13, color=MUTED, anchor="end"))
    tx, ty = polar(r + 34, A_NOW)
    f.append(text(tx, ty, "now", size=14, bold=True, anchor="start"))
    f.append(text(tx, ty + 18, "0x1000_0000", size=13, color=MUTED, anchor="start"))
    tx, ty = polar(r + 30, A_LAST + 180)
    f.append(text(tx + 6, ty + 18, "last + 2³¹", size=13, color=MUTED, anchor="start"))

    f.append(arc(r - 28, A_LAST, A_NOW + 360, INK, 4.5, marker=True))
    tx, ty = polar(72, (A_LAST + A_NOW + 360) / 2)
    f.append(text(tx, ty, "Δ", size=20, bold=True))

    f.append(fitbox(600, 88, 430, 74,
                    "Δ = (now − last) & 0xFFFFFFFF\nдає справжню різницю попри оберт",
                    size=14, fill="#eafaf0"))
    f.append(fitbox(600, 198, 430, 74,
                    "але тільки поки Δ < 2³¹: більше —\nядро читає це як крок назад і віддає 0",
                    size=14, fill="#fdecea"))
    f.append(fitbox(600, 308, 430, 92,
                    "корисний запас — половина маски:\n2³¹ тактів на 24 МГц — це 89.5 с,\nа не 178.9 с повного оберту",
                    size=14, fill="#fdf6e3"))

    render(os.path.join(OUT, 'mask-wrap.svg'), W, H, *f)


if __name__ == '__main__':
    fig_two_questions()
    fig_clock_family()
    fig_read_path()
    fig_tick_vs_oneshot()
    fig_tick_history()
    fig_cost_ladder()
    fig_mult_shift_budget()
    fig_mask_wrap()
    print("ok")
