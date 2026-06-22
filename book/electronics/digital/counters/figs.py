# -*- coding: utf-8 -*-
"""Фігури до теми «Лічильники» та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _clock(x0, y0, n, period, hi, color=INK, sw=2.3, start_low=True):
    """Прямокутна хвиля такту: n повних періодів, кожен period завширшки.
    Повертає список точок polyline (рядок points)."""
    pts = []
    x = x0
    pts.append((x, y0))
    for _ in range(n):
        # фаза LOW (на базовій лінії y0), тоді HIGH (y0-hi)
        pts.append((x, y0))
        pts.append((x, y0 - hi))
        pts.append((x + period * 0.5, y0 - hi))
        pts.append((x + period * 0.5, y0))
        x += period
    pts.append((x, y0))
    return pts


def _square_div(x0, y0, n, period, div, hi, color=INK, sw=2.3):
    """Поділена навпіл (÷div) прямокутна хвиля над базою y0; n тактів вхідного періоду period.
    Хвиля міняє рівень кожні div/2*period? — простіше: рівень = (такт // (div/2)) парний/непарний.
    Реалізуємо як меандр з періодом div*period (півперіод = div/2 тактів)."""
    pts = [(x0, y0)]
    half = period * div / 2.0
    x = x0
    level_high = False
    total = n * period
    seg = 0
    cur = x0
    while cur < x0 + total - 1e-6:
        nxt = min(cur + half, x0 + total)
        y = y0 - hi if level_high else y0
        pts.append((cur, y))
        pts.append((nxt, y))
        cur = nxt
        level_high = not level_high
    return pts


def _poly(pts, color=INK, sw=2.3):
    s = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (s, color, sw)


def _ffbox(x, y, w, h, label):
    return rect(x, y, w, h, fill=FILL, stroke=INK, sw=1.8) + \
           text(x + w / 2, y + h / 2 + 5, label, size=14, bold=True)


# ── 1. Toggle-тригер ділить частоту на 2 ────────────────────────────────────
def fig_toggle():
    W, H = 820, 340
    f = [text(W / 2, 28, "Toggle-тригер: D з'єднано з власним Q̄ — щотакту Q перемикається",
              size=15, bold=True)]

    # тригер ліворуч
    bx, by, bw, bh = 70, 120, 110, 90
    f.append(_ffbox(bx, by, bw, bh, "T"))
    f.append(text(bx + 14, by + 28, "D", size=12, bold=True, anchor="start"))
    f.append(text(bx + bw - 12, by + 28, "Q", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(text(bx + bw - 12, by + 62, "Q̄", size=12, bold=True, color=MUTED, anchor="end"))
    # позначка фронту такту
    f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (bx, by + bh - 22, bx + 12, by + bh - 15, bx, by + bh - 8, INK))
    f.append(text(bx - 6, by + bh - 11, "такт", size=11, anchor="end"))
    f.append(line(bx - 40, by + bh - 15, bx, by + bh - 15, color=INK, sw=1.6))
    # зворотний зв'язок Q̄ → D
    f.append(line(bx + bw, by + 58, bx + bw + 22, by + 58, color=NEG, sw=1.5))
    f.append(line(bx + bw + 22, by + 58, bx + bw + 22, by + bh + 24, color=NEG, sw=1.5))
    f.append(line(bx + bw + 22, by + bh + 24, bx - 22, by + bh + 24, color=NEG, sw=1.5))
    f.append(line(bx - 22, by + bh + 24, bx - 22, by + 24, color=NEG, sw=1.5))
    f.append(arrow(bx - 22, by + 24, bx, by + 24, color=NEG, sw=1.5))
    f.append(text(bx + bw / 2, by + bh + 40, "Q̄ назад на D", size=10, color=NEG, italic=True))

    # хвилі праворуч
    x0 = 380
    period = 50
    n = 8
    # такт
    yb = 120
    f.append(text(x0 - 14, yb - 8, "такт", size=12, bold=True, anchor="end"))
    f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
    f.append(_poly(_clock(x0, yb, n, period, 24), color=INK, sw=2.3))
    for i in range(n):
        f.append(line(x0 + i * period, yb - 26, x0 + i * period, yb + 90,
                      color="#cfcfcf", sw=0.8, dash="3 3"))
    # Q (÷2)
    yb = 230
    f.append(text(x0 - 14, yb - 8, "Q", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
    f.append(_poly(_square_div(x0, yb, n, period, 2, 24), color=FIELD, sw=2.6))
    f.append(text(x0 + n * period / 2, yb + 30, "Q удвічі повільніший за такт (÷2)",
                  size=11, color=FIELD, bold=True))

    f.append(text(W / 2, H - 14,
                  "Q міняється раз на два такти — його частота вдвічі менша. Один toggle-тригер = поділ на 2.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "toggle.svg"), W, H, *f)


# ── 2. Ланцюг тригерів рахує у двійковій ─────────────────────────────────────
def fig_ripple():
    W, H = 860, 430
    f = [text(W / 2, 28, "Ланцюг toggle-тригерів: виходи разом — двійкове число, що зростає щотакту",
              size=15, bold=True)]
    x0 = 150
    period = 80
    n = 8
    # такт
    yb = 95
    f.append(text(x0 - 14, yb - 8, "такт", size=12, bold=True, anchor="end"))
    f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
    f.append(_poly(_clock(x0, yb, n, period, 22), color=INK, sw=2.2))
    for i in range(n + 1):
        f.append(line(x0 + i * period, yb - 24, x0 + i * period, 330,
                      color="#cfcfcf", sw=0.8, dash="3 3"))
    # Q0 ÷2
    yb = 160
    f.append(text(x0 - 14, yb - 8, "Q0 (÷2)", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(_poly(_square_div(x0, yb, n, period, 2, 22), color=FIELD, sw=2.4))
    # Q1 ÷4
    yb = 220
    f.append(text(x0 - 14, yb - 8, "Q1 (÷4)", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(_poly(_square_div(x0, yb, n, period, 4, 22), color=FIELD, sw=2.4))
    # Q2 ÷8
    yb = 280
    f.append(text(x0 - 14, yb - 8, "Q2 (÷8)", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(_poly(_square_div(x0, yb, n, period, 8, 22), color=FIELD, sw=2.4))
    # двійкові числа під осями
    nums = ["001", "010", "011", "100", "101", "110", "111", "000"]
    for i, s in enumerate(nums):
        f.append(text(x0 + i * period + period / 2, 320, s, size=10, color=POS, bold=True))

    # підсумкова рамка
    bx, by, bw, bh = 90, 345, 680, 60
    f.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 24, "Q2 Q1 Q0 разом — двійкове число, що зростає на 1 щотакту: 0→1→…→7→0.",
                  size=12, bold=True))
    f.append(text(W / 2, by + 46, "Молодший біт Q0 ділить такт на 2, Q1 — на 4, Q2 — на 8: біт n = такт / 2ⁿ⁺¹.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "ripple.svg"), W, H, *f)


# ── 3. Ділення частоти: швидкий такт → повільний ритм ───────────────────────
def fig_divide():
    W, H = 820, 360
    f = [text(W / 2, 28, "N-бітний лічильник: кожен наступний біт удвічі повільніший за попередній",
              size=15, bold=True)]
    rows = [("такт", 0, INK), ("Q0", 1, FIELD), ("Q1", 2, FIELD), ("Q2", 3, FIELD)]
    x0 = 130
    period = 40
    n = 16
    ytop = 80
    gap = 56
    for name, div_exp, col in rows:
        yb = ytop + div_exp * gap
        lbl = name if name == "такт" else "%s (÷%d)" % (name, 2 ** div_exp)
        f.append(text(x0 - 14, yb - 8, lbl, size=12, bold=True, color=col, anchor="end"))
        f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
        if div_exp == 0:
            f.append(_poly(_clock(x0, yb, n, period, 22), color=col, sw=2.0))
        else:
            f.append(_poly(_square_div(x0, yb, n, period, 2 ** div_exp, 22), color=col, sw=2.3))

    # стрілка-«сходинка» вправо: повільніше
    f.append(text(W / 2, ytop + 3 * gap + 36,
                  "Q9 = такт/1024,  Q23 ≈ такт/16 млн — будь-який повільніший ритм з одного кварцу.",
                  size=11, color=MUTED))
    # робочий приклад
    bx, by, bw, bh = 90, ytop + 3 * gap + 50, 640, 44
    f.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(W / 2, by + 27,
                  "16 МГц ÷ 2²⁴ ≈ 0.95 Гц — світлодіод блимає ≈ раз на секунду.",
                  size=12, bold=True))
    render(os.path.join(IMG, "divide.svg"), W, H, *f)


# ── 4. Ланцюговий проти синхронного ─────────────────────────────────────────
def fig_ripple_vs_sync():
    W, H = 880, 380
    f = [text(W / 2, 28, "Ланцюговий проти синхронного: де перенос «біжить», а де ні",
              size=15, bold=True)]
    # ліва панель
    f.append(rect(40, 70, 390, 280, fill="none", stroke="#caa24a", sw=1.6, rx=10))
    f.append(text(235, 96, "Ланцюговий (ripple)", size=13, bold=True, color="#9a7322"))
    bw, bh = 70, 50
    ys = 150
    xs = [80, 205, 330]
    for i, xx in enumerate(xs):
        f.append(_ffbox(xx, ys, bw, bh, "T%d" % i))
        f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (xx, ys + bh - 18, xx + 10, ys + bh - 12, xx, ys + bh - 6, INK))
        if i < 2:
            f.append(arrow(xx + bw, ys + bh / 2, xs[i + 1], ys + bh / 2, color=INK, sw=1.6))
    f.append(line(40, ys + bh / 2, 80, ys + bh / 2, color=INK, sw=1.6))
    f.append(text(40, ys + bh / 2 - 6, "такт", size=10, anchor="start"))
    f.append(text(235, ys + bh + 36, "такт → T0 → T1 → T2", size=11, bold=True))
    f.append(text(235, ys + bh + 56, "перенос «біжить» крізь розряди", size=10, color=MUTED, italic=True))
    f.append(text(235, ys + bh + 78, "просто, та старший біт відстає", size=11, bold=True, color=POS))
    f.append(text(235, ys + bh + 96, "на суму затримок → можливі глітчі", size=10, color=MUTED, italic=True))

    # права панель
    f.append(rect(450, 70, 390, 280, fill="none", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(645, 96, "Синхронний", size=13, bold=True, color=FIELD))
    xs2 = [500, 620, 740]
    for i, xx in enumerate(xs2):
        f.append(_ffbox(xx, ys, 66, bh, "T%d" % i))
        f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (xx, ys + bh - 18, xx + 10, ys + bh - 12, xx, ys + bh - 6, INK))
    # спільна шина такту
    f.append(line(470, ys + bh + 20, 806, ys + bh + 20, color=POS, sw=1.8))
    for xx in xs2:
        f.append(line(xx + 10, ys + bh, xx + 10, ys + bh + 20, color=POS, sw=1.2))
        f.append(circle(xx + 10, ys + bh + 20, 2.6, fill=POS, stroke=POS, sw=1))
    f.append(text(462, ys + bh + 24, "такт", size=10, color=POS, anchor="end", bold=True))
    f.append(text(645, ys + bh + 56, "усі тригери — по СПІЛЬНОМУ такту", size=11, bold=True))
    f.append(text(645, ys + bh + 76, "логіка вирішує, кому перемкнутись", size=10, color=MUTED, italic=True))
    f.append(text(645, ys + bh + 96, "складніше, зате швидко й без глітчів", size=11, bold=True, color=FIELD))

    f.append(text(W / 2, H - 14,
                  "Ланцюговий — для невибагливого; синхронний — там, де треба швидкість і чистота.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "ripple-vs-sync.svg"), W, H, *f)


# ── 5. Лічильник за модулем і застосування ──────────────────────────────────
def fig_uses():
    W, H = 860, 380
    f = [text(W / 2, 28, "Лічильник за модулем N і навіщо лічильники взагалі", size=15, bold=True)]

    # ліворуч: mod-N кільце 0..9
    cx, cy, R = 200, 210, 110
    f.append(text(cx, 74, "mod-10: лічить 0…9 по колу", size=12, bold=True))
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * 2 * math.pi / 10
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        col = POS if i == 9 else FILL
        tc = "#ffffff" if i == 9 else INK
        f.append(circle(px, py, 16, fill=("#fdecea" if i == 9 else FILL), stroke=(POS if i == 9 else LINE), sw=1.6))
        f.append(text(px, py + 5, str(i), size=12, bold=True, color=(POS if i == 9 else INK)))
    # стрілка скидання 9 → 0
    f.append(text(cx, cy + 4, "при N=10\n→ скид у 0", size=11, color=POS, bold=True))
    f.append(text(cx, cy + R + 44, "детектор скидає на числі N", size=10, color=MUTED, italic=True))

    # праворуч: три застосування
    bx = 430
    items = [
        ("⏱ Поділ частоти й час", "таймери, годинник: рахуємо відомі такти кварцу"),
        ("🔢 Лічба подій", "«скільки імпульсів прийшло» — те, чого гола логіка не вміла"),
        ("➡ Лічильник команд (PC)", "крокує адресами програми, ведучи процесор"),
    ]
    yy = 90
    for title_s, sub in items:
        f.append(rect(bx, yy, 400, 70, fill=FILL, stroke=LINE, sw=1.4, rx=8))
        f.append(text(bx + 16, yy + 28, title_s, size=13, bold=True, anchor="start"))
        f.append(text(bx + 16, yy + 52, sub, size=11, color=MUTED, anchor="start"))
        yy += 88
    render(os.path.join(IMG, "uses.svg"), W, H, *f)


# ── 6 (вставка comp). Дві «мови» лічильника-чипа ────────────────────────────
def fig_two_flavors():
    W, H = 820, 400
    f = [text(W / 2, 28, "Один такт на вході — дві «мови» рахунку на виході", size=15, bold=True)]

    # 4017 — біжучий вогник (кільце з 10 виходів)
    f.append(rect(40, 70, 360, 300, fill="none", stroke=NEG, sw=1.6, rx=10))
    f.append(text(220, 96, "74HC4017 — декадний (1-з-10)", size=13, bold=True, color=NEG))
    cx, cy, R = 220, 235, 95
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * 2 * math.pi / 10
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        on = (i == 2)
        f.append(circle(px, py, 13, fill=("#fdecea" if on else FILL),
                        stroke=(POS if on else LINE), sw=(2.2 if on else 1.3)))
        f.append(text(px, py + 4, "Q%d" % i, size=10, bold=on, color=(POS if on else MUTED)))
    f.append(text(cx, cy + 4, "вогник\nбіжить", size=11, color=POS, bold=True))
    f.append(text(220, 360, "у кожну мить «у високому» рівно один вихід", size=10, color=MUTED, italic=True))

    # 4040 — двійкове число
    f.append(rect(420, 70, 360, 300, fill="none", stroke="#caa24a", sw=1.6, rx=10))
    f.append(text(600, 96, "74HC4040 — двійковий дільник", size=13, bold=True, color="#9a7322"))
    bits = [("Q1", "÷2"), ("Q2", "÷4"), ("Q3", "÷8"), ("Q4", "÷16"),
            ("…", ""), ("Q12", "÷4096")]
    yy = 130
    for name, dv in bits:
        f.append(text(470, yy, name, size=12, bold=True, anchor="start"))
        f.append(text(560, yy, dv, size=11, color=MUTED, anchor="start"))
        yy += 36
    f.append(text(600, 360, "виходи — біти числа; кожен наступний удвічі повільніший", size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "two-flavors.svg"), W, H, *f)


# ── 7 (вставка comp). Розпіновка й схема без МК ─────────────────────────────
def fig_wiring():
    W, H = 860, 430
    f = [text(W / 2, 28, "Підключення без мікроконтролера: RC-генератор → лічильник → виходи",
              size=15, bold=True)]

    # генератор 74HC14
    gx, gy, gw, gh = 60, 150, 130, 80
    f.append(rect(gx, gy, gw, gh, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    f.append(text(gx + gw / 2, gy + 32, "74HC14", size=13, bold=True))
    f.append(text(gx + gw / 2, gy + 54, "RC-генератор", size=10, color=MUTED))
    f.append(text(gx + gw / 2, gy - 10, "такт ≈ 1/(RC)", size=11, color=POS, bold=True))

    # 4017
    ax, ay, aw, ah = 280, 110, 150, 200
    f.append(rect(ax, ay, aw, ah, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    f.append(text(ax + aw / 2, ay + 26, "74HC4017", size=14, bold=True))
    f.append(arrow(gx + gw, gy + gh / 2, ax, gy + gh / 2, color=INK, sw=2.0))
    f.append(text((gx + gw + ax) / 2, gy + gh / 2 - 8, "CLK", size=11, bold=True))
    # керівні входи притягнуті в 0
    f.append(text(ax + 10, ay + 56, "RST=0", size=11, color=NEG, anchor="start"))
    f.append(text(ax + 10, ay + 78, "CE =0", size=11, color=NEG, anchor="start"))
    f.append(text(ax + 10, ay + 100, "CO →каскад", size=10, color=MUTED, anchor="start"))
    # десять виходів → світлодіоди
    for i in range(10):
        yy = ay + 20 + i * 17
        f.append(line(ax + aw, yy, ax + aw + 30, yy, color=FIELD, sw=1.3))
        f.append(circle(ax + aw + 40, yy, 5, fill="#fdecea", stroke=POS, sw=1.3))
    f.append(text(ax + aw + 60, ay + ah / 2, "10 світлодіодів\n(через резистори)",
                  size=10, color=MUTED, anchor="start"))

    # 4040 нижче
    f.append(text(60, 360, "74HC4040: той самий такт на CLK → будь-який вихід Q — поділена частота "
                            "(Q4 = такт/16, Q12 = такт/4096).", size=11, color="#9a7322", anchor="start"))
    f.append(text(60, 388, "VDD/GND і блокувальний конденсатор 100 нФ біля ніжок живлення — обов'язкові.",
                  size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 8 (вставка comp). Часові діаграми обох чипів ────────────────────────────
def fig_waves():
    W, H = 840, 540
    f = [text(W / 2, 26, "Що видно осцилографом: вогник «біжить», біти «діляться»",
              size=15, bold=True)]
    x0 = 150
    period = 60
    n = 10
    # ── 4017 ──
    f.append(text(x0 - 14, 64, "74HC4017", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(470, 64, "кожен вихід — «1» рівно в один такт, по черзі (1-з-10)",
                  size=10, color=NEG, italic=True))
    yb = 96
    f.append(text(x0 - 14, yb - 8, "CLK", size=12, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, period, 22), color=INK, sw=2.0))
    rows017 = ["Q0", "Q1", "Q2", "Q3"]
    for r, name in enumerate(rows017):
        yb = 150 + r * 42
        f.append(text(x0 - 14, yb - 8, name, size=12, bold=True, anchor="end"))
        f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
        # один імпульс HIGH у такті r
        pts = [(x0, yb)]
        xa = x0 + r * period
        pts += [(xa, yb), (xa, yb - 22), (xa + period, yb - 22), (xa + period, yb), (x0 + n * period, yb)]
        f.append(_poly(pts, color=INK, sw=2.2))
    f.append(text(x0 + n * period, 132, "…і так до Q9, далі знову Q0", size=10, color=FIELD, italic=True, anchor="end"))

    # роздільник
    f.append(line(120, 330, x0 + n * period, 330, color="#e4e4e4", sw=1.5))

    # ── 4040 ──
    f.append(text(x0 - 14, 360, "74HC4040", size=13, bold=True, color="#9a7322", anchor="end"))
    f.append(text(470, 360, "кожен наступний біт удвічі повільніший — поділ частоти",
                  size=10, color="#9a7322", italic=True))
    yb = 392
    f.append(text(x0 - 14, yb - 8, "CLK", size=12, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, period, 22), color=INK, sw=2.0))
    rows040 = [("Q1", 2), ("Q2", 4), ("Q3", 8)]
    for r, (name, dv) in enumerate(rows040):
        yb = 446 + r * 40
        f.append(text(x0 - 14, yb - 8, name, size=12, bold=True, anchor="end"))
        f.append(text(x0 - 14, yb + 6, "÷%d" % dv, size=9, color=MUTED, anchor="end"))
        f.append(line(x0, yb, x0 + n * period, yb, color="#e4e4e4", sw=1))
        f.append(_poly(_square_div(x0, yb, n, period, dv, 22), color=INK, sw=2.3))

    f.append(text(W / 2, H - 12,
                  "Жоден вихід не потребує програми — це чиста апаратна лічба тактів.",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "waves.svg"), W, H, *f)


if __name__ == "__main__":
    fig_toggle()
    fig_ripple()
    fig_divide()
    fig_ripple_vs_sync()
    fig_uses()
    fig_two_flavors()
    fig_wiring()
    fig_waves()
    print("OK: figures written to", IMG)
