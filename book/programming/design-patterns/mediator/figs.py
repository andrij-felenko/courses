# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def pent(cx, cy, R):
    """5 вершин п'ятикутника вістрям угору."""
    return [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
            for a in (-90, -18, 54, 126, 198)]


def fig_mesh_vs_star():
    """Ядро патерна: мережа кожен-з-кожним згортається у зірку через центр."""
    W, H = 940, 520
    frags = []
    letters = "АБВГД"

    # ── Ліва панель: мережа «кожен з кожним» ──
    lcx, lcy, R = 245, 300, 132
    ln = pent(lcx, lcy, R)
    for i in range(5):                      # усі 10 ребер — спершу лінії
        for j in range(i + 1, 5):
            frags.append(line(ln[i][0], ln[i][1], ln[j][0], ln[j][1], color=POS, sw=1.5))
    for (x, y), ch in zip(ln, letters):     # вузли поверх ліній
        frags.append(circle(x, y, 23, fill="#fdecea", stroke=INK, sw=2))
        frags.append(text(x, y + 6, ch, size=17, bold=True))
    frags.append(text(lcx, 72, "Було: мережа «кожен з кожним»", size=16, bold=True, color=POS))
    frags.append(text(lcx, 470, "10 прямих зв'язків між 5 колегами", size=13, color=MUTED))
    frags.append(text(lcx, 492, "росте як n(n−1)/2 — квадратично", size=13, color=MUTED))

    # ── роздільник ──
    frags.append(line(470, 96, 470, 448, color="#d0d0d0", sw=1.5, dash="5,5"))

    # ── Права панель: зірка через посередника ──
    rcx, rcy = 695, 300
    rn = pent(rcx, rcy, R)
    for (x, y) in rn:                       # промені від центру
        frags.append(line(rcx, rcy, x, y, color=FIELD, sw=2))
    for (x, y), ch in zip(rn, letters):
        frags.append(circle(x, y, 23, fill="#eafaf1", stroke=INK, sw=2))
        frags.append(text(x, y + 6, ch, size=17, bold=True))
    m, _, _ = textbox(rcx, rcy, "Посередник", size=13, bold=True,
                      fill="#fff6e5", stroke=POS, pad=11, min_w=104)
    frags.append(m)
    frags.append(text(rcx, 72, "Стало: зірка через посередника", size=16, bold=True, color=FIELD))
    frags.append(text(rcx, 470, "5 зв'язків — кожен знає лише центр", size=13, color=MUTED))
    frags.append(text(rcx, 492, "росте як n — лінійно", size=13, color=MUTED))

    render(os.path.join(IMG, 'mesh-vs-star.svg'), W, H, *frags,
           title="Посередник згортає плутанину зв'язків у зірку")


def fig_roles_flow():
    """Три ролі й шлях однієї події: колега → посередник → інші колеги."""
    W, H = 940, 450
    frags = []

    # Колега A (ліворуч)
    a, aw, ah = textbox(150, 232, ["Колега A", "прапорець", "«та сама адреса»"],
                        size=13, fill="#eaf0fd", stroke=NEG, pad=12, min_w=196)
    frags.append(a)
    frags.append(text(150, 300, "A знає посередника", size=11.5, color=MUTED))
    frags.append(text(150, 317, "лише як інтерфейс", size=11.5, color=MUTED))

    # Посередник (центр): інтерфейс + конкретний
    frags.append(rect(372, 150, 216, 172, fill="#fff6e5", stroke=POS, sw=2, rx=10))
    frags.append(text(480, 178, "Посередник", size=15, bold=True, color=POS))
    frags.append(text(480, 200, "інтерфейс: notify(хто, подія)", size=11, color=MUTED, italic=True))
    frags.append(line(392, 214, 568, 214, color="#e0c98a", sw=1.2, dash="4,3"))
    frags.append(text(480, 236, "Діалог — конкретний посередник", size=11.5, bold=True))
    frags.append(text(480, 262, "тримає посилання на всіх колег", size=11, color=INK))
    frags.append(text(480, 282, "і містить логіку координації", size=11, color=INK))

    # Колеги B, C (праворуч)
    b, bw, bh = textbox(800, 158, ["Колега B", "поле адреси"], size=13,
                        fill="#eafaf1", stroke=FIELD, pad=12, min_w=172)
    frags.append(b)
    c, cw, ch = textbox(800, 300, ["Колега C", "кнопка OK"], size=13,
                        fill="#eafaf1", stroke=FIELD, pad=12, min_w=172)
    frags.append(c)

    # Потік: A -> M (сповіщення вгору через інтерфейс)
    frags.append(arrow(150 + aw / 2, 210, 372, 196, color=NEG, sw=2.2))
    frags.append(text(292, 176, "1. notify(A, «змінився»)", size=11.5, color=NEG, italic=True))

    # M -> B, M -> C (виклики вниз до конкретних колег)
    frags.append(arrow(588, 190, 800 - bw / 2, 168, color=INK, sw=2.2))
    frags.append(text(694, 150, "2. field.disable()", size=11.5, color=INK, italic=True))
    frags.append(arrow(588, 278, 800 - cw / 2, 300, color=INK, sw=2.2))
    frags.append(text(694, 316, "3. okButton.enable()", size=11.5, color=INK, italic=True))

    frags.append(text(W / 2, 424,
                     "Колеги не з'єднані між собою — уся взаємодія тече через посередника.",
                     size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'roles-flow.svg'), W, H, *frags,
           title="Три ролі: колега сповіщає посередника, той керує рештою")


def fig_thin_vs_god():
    """Складність не зникає — переїжджає в посередник; ризик — божественний об'єкт."""
    W, H = 940, 500
    frags = []

    # ── Ліворуч: тонкий посередник-диригент ──
    frags.append(text(230, 66, "Тонкий посередник — диригент", size=15, bold=True, color=FIELD))
    thin_nodes = [(92, 148), (92, 336), (368, 148), (368, 336)]
    for (x, y) in thin_nodes:                     # спершу промені
        frags.append(line(230, 242, x, y, color=MUTED, sw=1.5))
    for (x, y) in thin_nodes:                     # тоді вузли-колеги
        n, _, _ = textbox(x, y, "колега", size=12, fill=FILL, stroke=INK, pad=9, min_w=92)
        frags.append(n)
    tm, _, _ = textbox(230, 242, ["Посередник", "лише маршрутизує", "й координує"],
                       size=13, bold=True, fill="#eafaf1", stroke=FIELD, pad=13, min_w=184)
    frags.append(tm)                              # тонкий центр — поверх променів
    frags.append(text(230, 432, "колеги прості, легко замінні;", size=12, color=MUTED))
    frags.append(text(230, 450, "правила — в одному видимому місці", size=12, color=MUTED))

    # ── середина: деградація ──
    frags.append(arrow(452, 246, 512, 246, color=INK, sw=2.5))
    frags.append(text(482, 228, "минає рік", size=11.5, color=MUTED))
    frags.append(text(482, 272, "усе звалюють", size=11.5, color=POS))
    frags.append(text(482, 288, "в один клас", size=11.5, color=POS))

    # ── Праворуч: божественний об'єкт ──
    frags.append(text(716, 66, "Той самий посередник за рік", size=15, bold=True, color=POS))
    god_nodes = [(892, 132), (892, 250), (892, 366), (760, 402), (642, 402)]
    for (x, y) in god_nodes:                       # промені під box
        frags.append(line(717, 246, x, y, color=MUTED, sw=1.2))
    for (x, y) in god_nodes:
        frags.append(circle(x, y, 15, fill=FILL, stroke=INK, sw=1.5))
    frags.append(rect(620, 152, 194, 188, fill="#fdecea", stroke=POS, sw=2.5, rx=10))
    frags.append(text(717, 178, "Посередник", size=14, bold=True, color=POS))
    frags.append(text(717, 198, "= божественний об'єкт", size=11, color=POS, italic=True))
    god_lines = ["+ валідація", "+ мережеві виклики", "+ формат дат",
                 "+ права доступу", "+ логування", "+ ще 40 методів"]
    for i, gl in enumerate(god_lines):
        frags.append(text(634, 222 + i * 18, gl, size=11, color=INK, anchor="start"))
    frags.append(text(716, 454, "знає все, робить усе —", size=12, color=POS))
    frags.append(text(716, 472, "змінити страшно, тестувати годі", size=12, color=POS))

    render(os.path.join(IMG, 'thin-vs-god.svg'), W, H, *frags,
           title="Складність не зникає — вона переїжджає в посередника")


def fig_birth_timeline():
    """Народження патерна: DialogDirector з ET++ → дисертація Ґамми → GoF; рена́ва ролі."""
    W, H = 980, 430
    frags = []

    axis_y = 178
    xs = [210, 490, 770]
    years = ["1988", "1991", "1994"]
    boxlines = [
        ["ET++ — Цюрих", "клас DialogDirector", "координує віджети діалогу"],
        ["Дисертація Ґамми", "форми з ET++ виписано", "як повторні патерни"],
        ["GoF «Design Patterns»", "роль дістала назву", "Посередник (Mediator)"],
    ]
    details = ["Weinand · Gamma · Marty", "Erich Gamma, PhD", "«банда чотирьох»"]
    strokes = [INK, INK, FIELD]

    # вісь часу з вістрям (час тече ліворуч → праворуч)
    frags.append(arrow(120, axis_y, 866, axis_y, color=MUTED, sw=2))

    for x, yr, bl, det, st in zip(xs, years, boxlines, details, strokes):
        # рамка-віха над віссю
        box, bw, bh = textbox(x, 98, bl, size=12.5, pad=10,
                              fill=FILL, stroke=st, sw=2, min_w=250)
        # сполучник від рамки вниз до крапки на осі
        frags.append(line(x, 98 + bh / 2, x, axis_y - 7, color=MUTED, sw=1.4))
        frags.append(box)
        # крапка-віха
        frags.append(circle(x, axis_y, 7, fill=st, stroke=st, sw=1.5))
        # рік і деталь під віссю
        frags.append(text(x, axis_y + 30, yr, size=16, bold=True, color=st))
        frags.append(text(x, axis_y + 50, det, size=11, color=MUTED))

    # роздільник до нижньої смуги «рена́ва»
    frags.append(line(120, 268, 866, 268, color="#d0d0d0", sw=1.3, dash="5,5"))

    # нижня смуга: те саме поняття — дві назви
    left, lw, lh = textbox(288, 344, ["Приклад у книзі лишив", "ім'я родом з ET++:", "FontDialogDirector"],
                           size=12.5, pad=11, fill="#eaf0fd", stroke=NEG, sw=2, min_w=300)
    right, rw, rh = textbox(700, 344, ["Узагальнену роль", "у структурі названо:", "Посередник · Mediator"],
                            size=12.5, pad=11, fill="#fff6e5", stroke=POS, sw=2, min_w=300)
    frags.append(left)
    frags.append(right)
    frags.append(arrow(288 + lw / 2, 344, 700 - rw / 2, 344, color=INK, sw=2.2))
    frags.append(text(494, 330, "узагальнення", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'birth-timeline.svg'), W, H, *frags,
           title="Звідки прийшов «директор»: від діалогу ET++ до ролі GoF")


def fig_growth_curves():
    """Квадратична крива повного графа проти лінійної прямої зірки."""
    W, H = 960, 560
    frags = []
    x0, x1 = 118, 892
    y0, y1 = 486, 96
    nmax, vmax = 14, 96

    def px(n):
        return x0 + (n / nmax) * (x1 - x0)

    def py(v):
        return y0 + (v / vmax) * (y1 - y0)

    # горизонтальна сітка + мітки осі Y
    for v in range(0, 97, 20):
        yy = py(v)
        frags.append(line(x0, yy, x1, yy, color="#eeeeee", sw=1))
        frags.append(text(x0 - 12, yy + 4, str(v), size=12, color=MUTED, anchor="end"))
    # осі
    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    # мітки осі X
    for n in range(0, 15, 2):
        xx = px(n)
        frags.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.4))
        frags.append(text(xx, y0 + 24, str(n), size=12, color=MUTED))
    frags.append(text((x0 + x1) / 2, y0 + 50, "n — число колег", size=13, color=MUTED))
    frags.append(text(x0 + 2, y1 - 14, "ребер", size=13, color=MUTED, anchor="start"))

    # криві
    kpts = " ".join("%.1f,%.1f" % (px(n), py(n * (n - 1) / 2)) for n in range(0, 15))
    spts = " ".join("%.1f,%.1f" % (px(n), py(n)) for n in range(0, 15))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (kpts, POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (spts, FIELD))

    # виділені значення
    frags.append(circle(px(10), py(45), 4, fill=POS, stroke=POS))
    frags.append(text(px(10) - 8, py(45) - 8, "45", size=13, color=POS, anchor="end", bold=True))
    frags.append(circle(px(10), py(10), 4, fill=FIELD, stroke=FIELD))
    frags.append(text(px(10) + 8, py(10) + 16, "10", size=13, color=FIELD, anchor="start", bold=True))

    # точка перетину n=3
    frags.append(circle(px(3), py(3), 5, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(px(3) + 10, py(3) + 20, "n = 3: порівну (3 і 3)", size=11.5,
                      color=INK, anchor="start", italic=True))

    # легенда (верх-ліворуч, де криві низько)
    lx = x0 + 34
    frags.append(line(lx, 128, lx + 34, 128, color=POS, sw=2.8))
    frags.append(text(lx + 44, 132, "повний граф:  n(n−1)/2  =  O(n²)", size=13,
                      color=POS, anchor="start", bold=True))
    frags.append(line(lx, 156, lx + 34, 156, color=FIELD, sw=2.6))
    frags.append(text(lx + 44, 160, "зірка:  n  =  O(n)", size=13,
                      color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, 'growth-curves.svg'), W, H, *frags,
           title="Квадратичне сплетіння проти лінійної зірки")


def fig_payoff_region():
    """Межа окупності d* = 2/(n−1): дві зони на площині (n, густина)."""
    W, H = 960, 560
    frags = []
    x0, x1 = 122, 892
    y0, y1 = 486, 104
    nmin, nmax = 3, 50

    def px(n):
        return x0 + ((n - nmin) / (nmax - nmin)) * (x1 - x0)

    def py(d):
        return y0 + d * (y1 - y0)

    ns = list(range(3, 51))
    cur = [(px(n), py(min(1.0, 2.0 / (n - 1)))) for n in ns]

    # зона НАД кривою — зірка окупається (зелена)
    above = ["%.1f,%.1f" % (px(nmin), y1)]
    above += ["%.1f,%.1f" % p for p in cur]
    above += ["%.1f,%.1f" % (px(nmax), y1)]
    frags.append('<polygon points="%s" fill="#eafaf1" stroke="none"/>' % " ".join(above))
    # зона ПІД кривою — мережа дешевша (блідо-червона)
    below = ["%.1f,%.1f" % (px(nmin), y0)]
    below += ["%.1f,%.1f" % p for p in cur]
    below += ["%.1f,%.1f" % (px(nmax), y0)]
    frags.append('<polygon points="%s" fill="#fbeceb" stroke="none"/>' % " ".join(below))

    # сітка + мітки осі Y
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = py(d)
        frags.append(line(x0, yy, x1, yy, color="#e6e6e6", sw=1))
        lbl = "0" if d == 0 else ("%.2f" % d).rstrip("0").rstrip(".")
        frags.append(text(x0 - 12, yy + 4, lbl, size=12, color=MUTED, anchor="end"))
    # осі
    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for n in (5, 10, 20, 30, 40, 50):
        xx = px(n)
        frags.append(line(xx, y0, xx, y0 + 5, color=INK, sw=1.4))
        frags.append(text(xx, y0 + 24, str(n), size=12, color=MUTED))
    frags.append(text((x0 + x1) / 2, y0 + 50, "n — число колег", size=13, color=MUTED))
    frags.append(text(x0 + 2, y1 - 14, "густина d", size=13, color=MUTED, anchor="start"))

    # крива порога
    cpts = " ".join("%.1f,%.1f" % p for p in cur)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (cpts, POS))

    # підписи зон
    frags.append(text(px(31), py(0.87), "тут зірка окупається", size=15, bold=True, color=FIELD))
    frags.append(text(px(31), py(0.87) + 22, "(зв'язків досить густо)", size=12, color=FIELD))
    frags.append(text(px(11), py(0.09), "тут зірка лише додає перевалку", size=12.5, color=POS))

    # точки-приклади
    for n, lbl in ((5, "0.50"), (10, "0.22"), (20, "0.11"), (50, "0.04")):
        d = min(1.0, 2.0 / (n - 1))
        frags.append(circle(px(n), py(d), 4.5, fill="#ffffff", stroke=POS, sw=2))
        if n == 50:
            frags.append(text(px(n) - 10, py(d) - 20, "n=%d → d*=%s" % (n, lbl),
                              size=11.5, color=POS, anchor="end"))
        else:
            frags.append(text(px(n) + 10, py(d) - 20, "n=%d → d*=%s" % (n, lbl),
                              size=11.5, color=POS, anchor="start"))

    frags.append(text((x0 + x1) / 2, y1 - 14, "межа:  d* = 2/(n−1)", size=13,
                      bold=True, color=POS))

    render(os.path.join(IMG, 'payoff-region.svg'), W, H, *frags,
           title="З якої густоти взаємодій зірка окупається")


def fig_hub_concentration():
    """Лема про рукостискання: сумарний степінь зберігається, та в зірці сідає на центр."""
    W, H = 960, 548
    frags = []
    base = 424
    unit = 34  # висота стовпчика на 1 ребро

    # ── Ліворуч: густа мережа (5 колег, m=10) ──
    frags.append(text(248, 78, "Мережа: 5 колег, m = 10 ребер", size=15, bold=True, color=POS))
    xs = [92, 164, 236, 308, 380]
    for i, x in enumerate(xs):
        h = 4 * unit                       # середній степінь 2m/n = 4
        frags.append(rect(x, base - h, 46, h, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
        frags.append(text(x + 23, base - h - 8, "4", size=12.5, color=POS, bold=True))
        frags.append(text(x + 23, base + 20, "К%d" % (i + 1), size=11.5, color=MUTED))
    frags.append(line(78, base, 438, base, color=INK, sw=1.5))
    frags.append(text(248, base + 44, "кожен колега тримає ~2m/n = 4 ребра", size=12, color=MUTED))
    frags.append(text(248, base + 64, "Σ степенів = 2m = 20", size=13, color=INK, bold=True))

    # роздільник
    frags.append(line(482, 96, 482, base + 30, color="#d0d0d0", sw=1.5, dash="5,5"))

    # ── Праворуч: зірка (ті самі 5 колег + центр) ──
    frags.append(text(722, 78, "Зірка: ті самі 5 колег + центр", size=15, bold=True, color=FIELD))
    xs2 = [548, 606, 664, 722, 780]
    for i, x in enumerate(xs2):
        h = 1 * unit                       # інваріант: степінь 1
        frags.append(rect(x, base - h, 42, h, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
        frags.append(text(x + 21, base - h - 8, "1", size=12.5, color=FIELD, bold=True))
        frags.append(text(x + 21, base + 20, "К%d" % (i + 1), size=11.5, color=MUTED))
    # центр — степінь 5
    hc = 5 * unit
    frags.append(rect(842, base - hc, 58, hc, fill="#fff6e5", stroke=POS, sw=2, rx=4))
    frags.append(text(871, base - hc - 10, "5", size=13.5, color=POS, bold=True))
    frags.append(text(871, base + 20, "центр", size=11.5, color=MUTED))
    frags.append(line(536, base, 908, base, color=INK, sw=1.5))
    frags.append(text(710, base + 44, "колега: рівно 1 ребро (інваріант) · центр: n = 5", size=12, color=MUTED))
    frags.append(text(710, base + 64, "Σ степенів = 2n = 10 — але половина на центрі", size=13, color=INK, bold=True))

    # мораль
    frags.append(text(W / 2, H - 30,
                      "Лему про рукостискання виконано в обох. Зірка не знищила зв'язність —",
                      size=12.5, color=MUTED, italic=True))
    frags.append(text(W / 2, H - 12,
                      "стягнула її на один вузол: степінь n зовні, усі m правил усередині — ось божественний об'єкт.",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'hub-concentration.svg'), W, H, *frags,
           title="Складність зберігається, та в зірці осідає на центрі")


def fig_sub_mediators():
    """Складений посередник: щільні групи всередині, тонкий координатор зверху."""
    W, H = 980, 600
    frags = []

    # ── Координатор (угорі, по центру) ──
    frags.append(rect(305, 54, 370, 82, fill="#fff6e5", stroke=POS, sw=2, rx=10))
    frags.append(text(490, 84, "RegistrationDialog — координатор", size=13, bold=True, color=POS))
    frags.append(text(490, 110, "submit = creds.valid && address.valid && terms",
                      size=10.5, color=MUTED, italic=True))

    # ── terms — прямий колега координатора (під ним) ──
    t, _, th = textbox(490, 182, ["terms", "згода"], size=11,
                       fill=FILL, stroke=INK, pad=8, min_w=92)
    frags.append(line(490, 136, 490, 182 - th / 2, color=MUTED, sw=1.5))
    frags.append(t)

    # ── Група облікових даних (ліворуч) ──
    frags.append(rect(55, 250, 370, 310, fill="#f2fbf6", stroke=FIELD, sw=1.5, rx=12))
    ct, _, cth = textbox(240, 288, "CredentialsGroup — посередник", size=12, bold=True,
                         fill="#eafaf1", stroke=FIELD, pad=9, min_w=180)
    frags.append(line(240, 288 - cth / 2, 400, 136, color=FIELD, sw=1.6))
    frags.append(text(352, 206, "valid?", size=11, color=FIELD, italic=True))
    frags.append(ct)
    e1, ew, _ = textbox(150, 372, "email", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=104)
    p1, pw, _ = textbox(150, 472, "password", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=104)
    c1, cw, _ = textbox(322, 472, "confirm", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=104)
    frags.append(line(150 + pw / 2, 472, 322 - cw / 2, 472, color=INK, sw=1.6))
    frags.append(text(236, 450, "пароль = повтор", size=10, color=MUTED))
    frags.extend([e1, p1, c1])

    # ── Група доставки (праворуч) ──
    frags.append(rect(555, 250, 370, 310, fill="#f2fbf6", stroke=FIELD, sw=1.5, rx=12))
    at, _, ath = textbox(740, 288, "AddressGroup — посередник", size=12, bold=True,
                         fill="#eafaf1", stroke=FIELD, pad=9, min_w=180)
    frags.append(line(740, 288 - ath / 2, 580, 136, color=FIELD, sw=1.6))
    frags.append(text(612, 206, "valid?", size=11, color=FIELD, italic=True))
    frags.append(at)
    co, cow, _ = textbox(650, 372, "country", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=108)
    re_, rew, _ = textbox(846, 372, "region", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=108)
    ss, ssw, _ = textbox(650, 472, "shipSame", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=112)
    sh, shw, _ = textbox(846, 472, "shipping", size=11.5, fill=FILL, stroke=INK, pad=8, min_w=112)
    frags.append(arrow(650 + cow / 2, 372, 846 - rew / 2, 372, color=INK, sw=1.8))
    frags.append(text(748, 360, "області", size=10, color=MUTED))
    frags.append(arrow(650 + ssw / 2, 472, 846 - shw / 2, 472, color=INK, sw=1.8))
    frags.append(text(748, 460, "гасить адресу", size=10, color=MUTED))
    frags.extend([co, re_, ss, sh])

    frags.append(text(W / 2, 588,
                     "Густі зв'язки замкнені в групі; координатор бачить лише «група валідна?» та згоду.",
                     size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'sub-mediators.svg'), W, H, *frags,
           title="Складений посередник: групи за зв'язністю під тонким координатором")


def fig_coordinate_not_work():
    """Межа: посередник лише координує, робота живе поза ним; інакше — божественний об'єкт."""
    W, H = 980, 520
    frags = []

    # ── Тонкий посередник (ліворуч) ──
    frags.append(rect(70, 96, 300, 210, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    frags.append(text(220, 128, "Посередник — лише координує", size=13, bold=True, color=FIELD))
    for i, s in enumerate(["• маршрутизує подію", "• питає колегу: valid?",
                            "• вирішує, кого ввімкнути", "• кличе виконавця"]):
        frags.append(text(92, 164 + i * 32, s, size=11.5, color=INK, anchor="start"))

    # ── Виконавці (праворуч), яких посередник лише кличе ──
    workers = [
        (130, ["Валідатори полів", "email · пароль"]),
        (210, ["PromoService", "перевірка коду · мережа"]),
        (290, ["Форматувальник ціни", "локаль · валюта"]),
    ]
    for i, (cy, lines) in enumerate(workers):
        wbox, ww, _ = textbox(772, cy, lines, size=11.5, fill=FILL, stroke=INK, pad=10, min_w=214)
        frags.append(arrow(372, 150 + i * 52, 772 - ww / 2, cy, color=INK, sw=1.8))
        frags.append(wbox)
    frags.append(text(422, 108, "кличе", size=11, color=MUTED, italic=True))

    # ── Червона смуга: чому це не місце в notify ──
    frags.append(rect(70, 356, 840, 128, fill="#fdecea", stroke=POS, sw=2, rx=10))
    frags.append(text(160, 388, "У notify НЕ місце — це вже робота:", size=13, bold=True,
                      color=POS, anchor="start"))
    for cx, s in [(182, "регулярка"), (334, "await fetch"),
                  (488, "формат дати"), (632, "бізнес-if")]:
        box, _, _ = textbox(cx, 444, s, size=11, fill=BG, stroke=POS, pad=8, min_w=112)
        frags.append(box)
    frags.append(arrow(702, 444, 762, 444, color=POS, sw=2))
    frags.append(text(838, 448, "божественний об'єкт", size=11.5, bold=True, color=POS))

    render(os.path.join(IMG, 'coordinate-not-work.svg'), W, H, *frags,
           title="Координація проти роботи: що лишається в посереднику, а що виноситься")


if __name__ == '__main__':
    fig_mesh_vs_star()
    fig_roles_flow()
    fig_thin_vs_god()
    fig_birth_timeline()
    fig_growth_curves()
    fig_payoff_region()
    fig_hub_concentration()
    fig_sub_mediators()
    fig_coordinate_not_work()
    print("figures written")
