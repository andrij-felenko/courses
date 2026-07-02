# -*- coding: utf-8 -*-
"""Фігури до теми «Практикум даташитів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


def _legend_row(f, cx, y, color, label):
    f.append(rect(cx, y - 7, 16, 13, fill=color, stroke=color, sw=1, rx=2))
    f.append(text(cx + 22, y + 4, label, size=10.5, color=MUTED, anchor="start"))


def _row(f, x, y, w, name, color, fill, expl, val):
    """Один рядок-параметр: кольорова плашка з назвою + пояснення + значення."""
    f.append(rect(x, y, 120, 40, fill=fill, stroke=color, sw=1.6, rx=6))
    f.append(text(x + 60, y + 18, name, size=12, color=color, bold=True))
    fs = fit_font(expl, 200, 10)
    f.append(text(x + 132, y + 16, expl, size=fs, color=INK, anchor="start"))
    f.append(text(x + 132, y + 32, val, size=10.5, color=MUTED, anchor="start"))


# ── 1. Даташит діода: критичні рядки ─────────────────────────────────────────
def fig_diode():
    W, H = 720, 300
    f = [text(W / 2, 28, "Даташит діода: рядки, що вирішують вибір", size=16, bold=True)]
    _legend_row(f, 60, 50, RED, "абсолютний максимум")
    _legend_row(f, 300, 50, GRN, "робоча межа")
    _legend_row(f, 520, 50, BLU, "параметр")
    x, y, dy = 50, 72, 44
    _row(f, x, y + 0 * dy, W, "VRRM", RED, "#fdecea",
         "найбільша зворотна напруга до пробою", "беруть із запасом ≥ 2× до шини")
    _row(f, x, y + 1 * dy, W, "IFSM", RED, "#fdecea",
         "піковий одиничний струм-кидок", "важить при ввімкненні на ємність")
    _row(f, x, y + 2 * dy, W, "IF(av)", GRN, "#eafaf1",
         "тривалий прямий струм без перегріву", "має перекривати робочий струм")
    _row(f, x, y + 3 * dy, W, "VF", BLU, "#eaf0fd",
         "пряме падіння при заданому струмі", "втрати й нагрів P ≈ VF·IF, колонка max")
    _row(f, x, y + 4 * dy, W, "trr", BLU, "#eaf0fd",
         "час відновлення (швидкість)", "вирішальний лише у швидкій комутації")
    render(os.path.join(IMG, "diode.svg"), W, H, *f)


# ── 2. Даташит MOSFET: критичні рядки + дві пастки ───────────────────────────
def fig_mosfet():
    W, H = 720, 330
    f = [text(W / 2, 28, "Даташит MOSFET: рядки керування й силові межі", size=16, bold=True)]
    _legend_row(f, 60, 50, RED, "абсолютний максимум")
    _legend_row(f, 300, 50, GRN, "робоча межа")
    _legend_row(f, 520, 50, BLU, "параметр")
    x, y, dy = 50, 72, 38
    _row(f, x, y + 0 * dy, W, "VDS", RED, "#fdecea",
         "макс. напруга стік–витік (блокування)", "запас до напруги шини")
    _row(f, x, y + 1 * dy, W, "VGS", RED, "#fdecea",
         "макс. напруга затвора, часто ±20 В", "перевищиш — пробій ізолятора")
    _row(f, x, y + 2 * dy, W, "ID", GRN, "#eafaf1",
         "тривалий струм стоку", "прив'язаний до температури кристала")
    _row(f, x, y + 3 * dy, W, "Rds(on)", BLU, "#eaf0fd",
         "опір відкритого каналу, втрати I²·R", "дають за великого VGS і холодним")
    _row(f, x, y + 4 * dy, W, "VGS(th)", BLU, "#eaf0fd",
         "поріг: канал лише починає текти", "це НЕ напруга повного відкриття")
    _row(f, x, y + 5 * dy, W, "Qg", BLU, "#eaf0fd",
         "заряд затвора на одне відкриття", "задає драйвер і втрати перемикання")
    render(os.path.join(IMG, "mosfet.svg"), W, H, *f)


# ── 3. Даташит ОП: критичний рядок залежить від задачі ───────────────────────
def fig_opamp():
    W, H = 720, 340
    f = [text(W / 2, 28, "Даташит ОП: який рядок критичний — диктує задача", size=16, bold=True)]

    # верхня плашка: спільний для всіх перший крок
    b, _, _ = textbox(W / 2, 64, "Спершу для будь-якої задачі — діапазон живлення: чи влізе ОП у твою шину",
                      size=12, fill=FILL, stroke=LINE)
    f.append(b)

    # дві колонки задач
    colw, top = 320, 96
    lx, rx = 40, 40 + colw + 20
    f.append(rect(lx, top, colw, 196, fill="#eafaf1", stroke=GRN, sw=1.8, rx=10))
    f.append(rect(rx, top, colw, 196, fill="#eaf0fd", stroke=BLU, sw=1.8, rx=10))
    f.append(text(lx + colw / 2, top + 24, "Точний вимірювач (постійний сигнал)", size=12.5, bold=True, color=GRN))
    f.append(text(rx + colw / 2, top + 24, "Швидкий сигнал (звук, відео)", size=12.5, bold=True, color=BLU))

    left = [("Vos", "зсув — паразитна похибка на вході"),
            ("Ib", "вхідний струм — б'є по високоомному"),
            ("дрейф", "як зсув повзе з температурою")]
    right = [("GBW", "добуток підсилення на смугу"),
             ("SR", "швидкість наростання виходу"),
             ("на спокої", "Vos і Ib майже байдужі")]
    for i, (nm, ex) in enumerate(left):
        yy = top + 50 + i * 44
        f.append(rect(lx + 16, yy, 78, 32, fill=BG, stroke=GRN, sw=1.4, rx=5))
        f.append(text(lx + 55, yy + 21, nm, size=12, color=GRN, bold=True))
        fs = fit_font(ex, colw - 112, 10, min_size=9)
        f.append(text(lx + 104, yy + 20, ex, size=fs, color=INK, anchor="start"))
    for i, (nm, ex) in enumerate(right):
        yy = top + 50 + i * 44
        f.append(rect(rx + 16, yy, 78, 32, fill=BG, stroke=BLU, sw=1.4, rx=5))
        f.append(text(rx + 55, yy + 21, nm, size=12, color=BLU, bold=True))
        fs = fit_font(ex, colw - 112, 10, min_size=9)
        f.append(text(rx + 104, yy + 20, ex, size=fs, color=INK, anchor="start"))

    f.append(text(W / 2, top + 222, "RRIO — розмах від рейки до рейки: критичний на низькій напрузі живлення",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "opamp.svg"), W, H, *f)


# ── 4. Єдиний маршрут читання даташита ───────────────────────────────────────
def fig_workflow():
    W, H = 720, 300
    f = [text(W / 2, 28, "Один маршрут для діода, MOSFET чи ОП", size=16, bold=True)]
    steps = [
        ("1", "Перша сторінка", "це взагалі потрібний клас приладу?", "#fdf1dc"),
        ("2", "Absolute Maximum", "мої напруги, струми, піки не вб'ють?", "#fdecea"),
        ("3", "Recommended", "робоча точка всередині, із запасом?", "#fff3e0"),
        ("4", "Electrical Char.", "критичний параметр — по гарантованому краю", "#eafaf1"),
        ("5", "Графіки", "як він попливе саме в моїх умовах?", "#eaf0fd"),
        ("6", "Дрібний шрифт", "виноски, умови тестів, errata", "#f3e9f3"),
    ]
    x, y0, bh, gap = 50, 54, 32, 6
    for i, (n, name, q, fill) in enumerate(steps):
        y = y0 + i * (bh + gap)
        f.append(rect(x, y, 34, bh, fill=BG, stroke="#9bb0c2", sw=1.4, rx=6))
        f.append(text(x + 17, y + bh / 2 + 5, n, size=14, color=INK, bold=True))
        f.append(rect(x + 40, y, 200, bh, fill=fill, stroke="#9bb0c2", sw=1.3, rx=6))
        f.append(text(x + 52, y + bh / 2 + 4, name, size=11.5, color=INK, anchor="start", bold=True))
        f.append(rect(x + 248, y, 372, bh, fill=BG, stroke="#c9d3dc", sw=1.2, rx=6))
        fs = fit_font(q, 348, 11)
        f.append(text(x + 262, y + bh / 2 + 4, q, size=fs, color=INK, anchor="start"))
        if i < len(steps) - 1:
            f.append(line(x + 17, y + bh, x + 17, y + bh + gap, color=MUTED, sw=1.4))
    f.append(text(W / 2, y0 + 6 * (bh + gap) + 8,
                  "Змінюється лише, який параметр критичний на кроці 4.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "workflow.svg"), W, H, *f)


# ── 5. Анатомія числа: розкид по партії + колонка умов (детальна) ────────────
def fig_number_anatomy():
    import math
    W, H = 720, 320
    f = [text(W / 2, 28, "Анатомія одного числа: розкид по партії й умови", size=16, bold=True)]

    # ліва частина — крива розкиду (нормальний дзвін)
    ox, oy, gw, gh = 60, 250, 380, 150
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.6))          # вісь параметра
    f.append(text(ox + gw / 2, oy + 34, "значення параметра по всіх приладах партії",
                  size=10.5, color=MUTED))
    # дзвін
    mu, sig = ox + gw * 0.5, gw * 0.13
    pts = []
    x = ox + 20
    while x <= ox + gw - 20:
        z = (x - mu) / sig
        y = oy - gh * math.exp(-0.5 * z * z)
        pts.append("%.1f,%.1f" % (x, y))
        x += 3
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), NEG))
    # min / typ / max вертикалі
    x_min, x_max = mu - 2.4 * sig, mu + 2.4 * sig
    for xx, col, lab, sub in [(x_min, GRN, "min", "гарантовано"),
                              (mu, MUTED, "typ", "центр (медіана)"),
                              (x_max, RED, "max", "гарантовано")]:
        f.append(line(xx, oy, xx, oy - gh - 6, color=col, sw=1.6, dash="4 3"))
        f.append(text(xx, oy - gh - 14, lab, size=12, color=col, bold=True))
        f.append(text(xx, oy - gh - 1, sub, size=8.5, color=MUTED))
    # заштрихована «половина гірша за typ»
    f.append(text(mu + 1.0 * sig, oy - gh * 0.30, "пів партії\nгірше за typ", size=8.5, color=MUTED, anchor="start"))

    # права частина — колонка умов
    cx = 500
    b, bw, bh = textbox(cx + 100, 90, "колонка умов", size=12, bold=True, fill=FILL, stroke=LINE, min_w=200)
    f.append(b)
    conds = ["Rds(on) max — при 25 °C",
             "Ib max — при 25 °C",
             "→ у гарячому кристалі",
             "   ще треба перерахувати"]
    for i, c in enumerate(conds):
        col = RED if i >= 2 else INK
        f.append(text(cx, 128 + i * 26, c, size=11, color=col, anchor="start",
                      bold=(i >= 2)))
    render(os.path.join(IMG, "number-anatomy.svg"), W, H, *f)


# ── 6. Крива заряду затвора з плато Міллера (детальна) ───────────────────────
def fig_gate_charge():
    W, H = 720, 340
    f = [text(W / 2, 28, "Заряд затвора: три ділянки й вікно втрат", size=16, bold=True)]
    ox, oy, gw, gh = 70, 250, 480, 170

    # осі
    f.append(line(ox, oy, ox, oy - gh - 10, color=INK, sw=1.6))   # Vgs
    f.append(line(ox, oy, ox + gw + 10, oy, color=INK, sw=1.6))   # заряд/час
    f.append(text(ox - 8, oy - gh - 6, "Vgs", size=11, color=INK, anchor="end", bold=True))
    f.append(text(ox + gw + 6, oy + 18, "заряд Qg  (= час · I_G)", size=10.5, color=MUTED, anchor="end"))

    # три ділянки: підйом до порога, плато, підйом до повної
    x0 = ox
    x1 = ox + gw * 0.28        # кінець першого підйому (поріг)
    x2 = ox + gw * 0.62        # кінець плато
    x3 = ox + gw * 0.92        # повна напруга
    y_full = oy - gh
    y_th = oy - gh * 0.34      # рівень порога
    y_plateau = oy - gh * 0.52 # рівень плато (трохи вище порога)

    # заливка вікна втрат (плато)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none"/>' % (x1, y_full, x2 - x1, oy - y_full))
    # крива Vgs(Qg)
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (x0, oy, x1, y_plateau, x2, y_plateau, x3, y_full, NEG))

    # позначки рівнів
    f.append(line(ox, y_th, x1, y_th, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(ox - 6, y_th + 4, "VGS(th)", size=9.5, color=MUTED, anchor="end"))
    f.append(line(ox, y_full, x3, y_full, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(ox - 6, y_full + 4, "повна", size=9.5, color=MUTED, anchor="end"))

    # підписи ділянок під віссю
    def seg(xa, xb, lab, col):
        xm = (xa + xb) / 2
        f.append(line(xa, oy + 6, xb, oy + 6, color=col, sw=1.4))
        fs = fit_font(lab, xb - xa + 40, 10)
        f.append(text(xm, oy + 20, lab, size=fs, color=col))
    seg(x0, x1, "заряд Cgs", GRN)
    seg(x1, x2, "плато Міллера (Qgd)", RED)
    seg(x2, x3, "дозаряд", NEG)

    # анотація вікна втрат
    b, bw, bh = textbox((x1 + x2) / 2, y_full - 26,
                        "тут V на ключі падає, а струм уже повний\n→ вікно втрат перемикання",
                        size=10, fill="#fff", stroke=RED, color=INK)
    f.append(b)
    f.append(text(W / 2, oy + 46, "довжина плато = Qgd / I_G — слабкий драйвер розтягує вікно",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gate-charge.svg"), W, H, *f)


# ── 7. Замкнена теплова петля й умова розгону (детальна) ─────────────────────
def fig_thermal_loop():
    W, H = 720, 300
    f = [text(W / 2, 28, "Теплова петля: втрати ⇄ температура кристала", size=16, bold=True)]

    # два вузли петлі
    cxL, cxR, cy = 210, 510, 120
    bL, wL, hL = textbox(cxL, cy, "тепловиділення\nP = I²·R (+ перемикання)",
                         size=12, fill="#eafaf1", stroke=FIELD, color=INK, bold=False)
    bR, wR, hR = textbox(cxR, cy, "температура кристала\nTj = T_amb + P·Rθ",
                         size=12, fill="#fdecea", stroke=POS, color=INK, bold=False)
    f.append(bL)
    f.append(bR)

    # стрілки петлі
    f.append(arrow(cxL + wL / 2 + 4, cy - 16, cxR - wR / 2 - 4, cy - 16, color=INK, sw=1.8))
    f.append(text((cxL + cxR) / 2, cy - 24, "гріє", size=10.5, color=INK))
    f.append(arrow(cxR - wR / 2 - 4, cy + 16, cxL + wL / 2 + 4, cy + 16, color=POS, sw=1.8))
    f.append(text((cxL + cxR) / 2, cy + 30, "гарячий опір/витік ↑ → P ↑", size=10.5, color=POS))

    # підпис: розв'язок і умова розгону
    b1, _, _ = textbox(cxL, cy + 118,
                       "стабільно: ітерація Tj → P → Tj\nзбігається",
                       size=11, fill="#eafaf1", stroke=FIELD, color=INK)
    f.append(b1)
    b2, _, _ = textbox(cxR, cy + 118,
                       "розгін: dP/dTj > 1/Rθ\nпетля не збігається",
                       size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(b2)
    render(os.path.join(IMG, "thermal-loop.svg"), W, H, *f)


# ── 8. Трикутник перекриття V·I під час фронту (вставка switching-loss) ───────
def fig_switching_overlap():
    W, H = 720, 340
    f = [text(W / 2, 26, "Вмикання: перекриття напруги й струму — площа втрат", size=16, bold=True)]
    ox, oy, gw, gh = 70, 250, 500, 150
    # осі
    f.append(line(ox, oy, ox, oy - gh - 12, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + gw + 12, oy, color=INK, sw=1.6))
    f.append(text(ox + gw + 8, oy + 18, "час", size=10.5, color=MUTED, anchor="end"))

    # два підінтервали фронту: [x0,x1] струм наростає (V повна), [x1,x2] V падає (I повний)
    x0 = ox + gw * 0.10
    x1 = ox + gw * 0.42
    x2 = ox + gw * 0.74
    y_hi = oy - gh          # рівень «повна величина»
    y_lo = oy               # нуль

    # струм I_D (зелений): 0 до повного на [x0,x1], далі повний
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox, y_lo, x0, y_lo, x1, y_hi, x2 + gw * 0.12, y_hi, FIELD))
    # напруга V_DS (червоний): повна до x1, потім спад до нуля на [x1,x2]
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox, y_hi, x1, y_hi, x2, y_lo, x2 + gw * 0.12, y_lo, POS))

    # заштрихована площа перекриття (обидва підінтервали) — світла заливка
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.85"/>'
             % (x0, y_lo, x1, y_hi, x1, y_lo))               # трикутник струму (V повна)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.85"/>'
             % (x1, y_hi, x2, y_lo, x1, y_lo))               # трикутник напруги (I повний)

    # рівні
    f.append(line(ox, y_hi, ox + gw, y_hi, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(ox - 6, y_hi + 4, "повна", size=9.5, color=MUTED, anchor="end"))

    # позначки кривих
    f.append(text(x2 + gw * 0.13, y_hi + 4, "I_D", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(x2 + gw * 0.13, y_lo - 4, "V_DS", size=12, color=POS, anchor="start", bold=True))

    # підінтервали під віссю
    def seg(xa, xb, lab, col):
        f.append(line(xa, oy + 6, xb, oy + 6, color=col, sw=1.4))
        fs = fit_font(lab, xb - xa + 60, 10)
        f.append(text((xa + xb) / 2, oy + 20, lab, size=fs, color=col))
    seg(x0, x1, "струм наростає (V повна)", FIELD)
    seg(x1, x2, "напруга падає (I повний)", POS)

    b, _, _ = textbox((x0 + x2) / 2, y_hi - 24,
                      "заштриховане = енергія в тепло\nE ≈ ½·V_DS·I_D·t",
                      size=10.5, fill="#fff", stroke=POS, color=INK)
    f.append(b)
    f.append(text(W / 2, oy + 46,
                  "ідеальний ключ (миттєвий фронт) площі не мав би; реальний — завжди має",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "switching-overlap.svg"), W, H, *f)


# ── 9. Частота рівноваги: провідні vs перемикання vs сумарні ──────────────────
def fig_loss_crossover():
    W, H = 720, 330
    f = [text(W / 2, 26, "Частота рівноваги: де перемикання переганяє опір", size=16, bold=True)]
    ox, oy, gw, gh = 70, 250, 520, 160
    f.append(line(ox, oy, ox, oy - gh - 12, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + gw + 12, oy, color=INK, sw=1.6))
    f.append(text(ox - 8, oy - gh - 6, "втрати P", size=10.5, color=INK, anchor="end", bold=True))
    f.append(text(ox + gw + 8, oy + 18, "частота f_sw", size=10.5, color=MUTED, anchor="end"))

    # провідні — горизонталь на рівні Pc
    y_cond = oy - gh * 0.40
    f.append(line(ox, y_cond, ox + gw, y_cond, color=FIELD, sw=2.6))
    f.append(text(ox + gw * 0.05, y_cond - 8, "провідні  I²·Rds(on)  (не залежать від f)",
                  size=11, color=FIELD, anchor="start", bold=True))

    # перемикання — похила з нуля; на x_cross перетинає провідні
    x_cross = ox + gw * 0.52
    # P_sw(x) лінійна: 0 у ox, y_cond у x_cross
    def psw_y(x):
        return oy - (oy - y_cond) * (x - ox) / (x_cross - ox)
    x_end = ox + gw
    f.append(line(ox, oy, x_end, psw_y(x_end), color=POS, sw=2.6))
    f.append(text(x_end - 4, psw_y(x_end) - 8, "перемикання  ∝ f",
                  size=11, color=POS, anchor="end", bold=True))

    # сумарні — сума двох; пунктир, зверху
    pts = []
    x = ox
    while x <= x_end:
        # сумарні = провідні + перемикання; глибини від осі oy складаються
        depth = (oy - y_cond) + (oy - psw_y(x))
        pts.append("%.1f,%.1f" % (x, oy - depth))
        x += 6
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="5 3"/>'
             % (" ".join(pts), INK))
    f.append(text(ox + gw * 0.30, oy - ((oy - y_cond) + (oy - psw_y(ox + gw * 0.30))) - 8,
                  "сумарні", size=10.5, color=INK, anchor="start", bold=True))

    # вертикаль частоти рівноваги
    f.append(line(x_cross, oy, x_cross, y_cond, color=MUTED, sw=1.4, dash="4 3"))
    f.append(circle(x_cross, y_cond, 4, fill=BG, stroke=INK, sw=1.6))
    f.append(text(x_cross, oy + 20, "f_рівн", size=12, color=INK, bold=True))

    # зони ліворуч/праворуч
    f.append(text((ox + x_cross) / 2, oy - gh - 2, "керує Rds(on)", size=10, color=FIELD))
    f.append(text((x_cross + x_end) / 2, oy - gh - 2, "керує Qgd", size=10, color=POS))
    render(os.path.join(IMG, "loss-crossover.svg"), W, H, *f)


if __name__ == "__main__":
    fig_diode()
    fig_mosfet()
    fig_opamp()
    fig_workflow()
    fig_number_anatomy()
    fig_gate_charge()
    fig_thermal_loop()
    fig_switching_overlap()
    fig_loss_crossover()
    print("OK: 9 figures ->", IMG)
