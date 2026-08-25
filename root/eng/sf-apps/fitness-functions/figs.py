# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_rule_vs_gate():
    """Ліва панель: правило на діаграмі — зміна проходить наскрізь.
       Права панель: правило як фітнес-функція — ворота зупиняють порушення."""
    W, H = 860, 400
    frags = []

    # ── ліва панель ────────────────────────────────────────────
    lx = 40
    frags.append(text(lx + 170, 56, "Правило лише на діаграмі", size=16, bold=True))
    # діаграма-малюнок
    b, w, h = textbox(lx + 170, 150, "домен → репозиторій → база\n(намальоване правило)",
                      size=13, fill="#eef2f7", stroke=MUTED)
    frags.append(b)
    # зміна-порушник входить і проходить наскрізь
    frags.append(text(lx + 170, 235, "зміна-порушник", size=12, color=POS, bold=True))
    frags.append(arrow(lx + 170, 250, lx + 170, 320, color=POS, sw=2.2))
    b, w, h = textbox(lx + 170, 350, "проходить вільно", size=13,
                      fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b)

    # розділювач
    frags.append(line(W / 2, 80, W / 2, H - 30, color=MUTED, sw=1.2, dash="5,5"))

    # ── права панель ───────────────────────────────────────────
    rx = 490
    frags.append(text(rx + 170, 56, "Правило як фітнес-функція", size=16, bold=True))
    frags.append(text(rx + 170, 110, "зміна-порушник", size=12, color=POS, bold=True))
    frags.append(arrow(rx + 170, 124, rx + 170, 168, color=POS, sw=2.2))
    # ворота автоперевірки
    b, w, h = textbox(rx + 170, 200, "автоперевірка у складанні\n(fitness function)",
                      size=13, fill=FILL, stroke=INK, bold=True)
    frags.append(b)
    # блок: не проходить
    frags.append(text(rx + 170, 262, "×", size=26, color=POS, bold=True))
    frags.append(arrow(rx + 170, 278, rx + 170, 320, color=INK, sw=2.2))
    b, w, h = textbox(rx + 170, 350, "складання падає", size=13,
                      fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'rule-vs-gate.svg'), W, H, *frags)


def fig_axes():
    """Три незалежні осі фітнес-функцій; унизу — приклад, розкладений за ними."""
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 34, "Три осі, за якими різняться фітнес-функції", size=17, bold=True))

    ax_x = 90            # ліва межа підписів осей
    end_x = W - 60
    ys = [110, 185, 260]
    labels = ["Обсяг", "Ритм", "Результат"]
    left_pole = ["атомарна\n(одна властивість)",
                 "запускана\n(на подію)",
                 "статична\n(фіксований поріг)"]
    right_pole = ["цілісна\n(поєднання властивостей)",
                  "неперервна\n(на живій системі)",
                  "динамічна\n(поріг за контекстом)"]

    for y, lab, lp, rp in zip(ys, labels, left_pole, right_pole):
        frags.append(text(50, y + 5, lab, size=14, bold=True, anchor="start"))
        # вісь
        frags.append(line(ax_x + 130, y, end_x - 130, y, color=MUTED, sw=1.4))
        # ліва рамка
        b, w, h = textbox(ax_x + 95, y, lp, size=12, fill="#eaf0fd", stroke=NEG)
        frags.append(b)
        # права рамка
        b, w, h = textbox(end_x - 95, y, rp, size=12, fill="#fdecea", stroke=POS)
        frags.append(b)

    # приклад унизу
    frags.append(line(60, 320, W - 60, 320, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(text(W / 2, 352, "Приклад: «95-й перцентиль часу відповіді під бюджетом»",
                      size=14, bold=True))
    b, w, h = textbox(W / 2, 415, "цілісна  ·  неперервна  ·  статична або динамічна",
                      size=13, fill="#eafaf0", stroke=FIELD, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'axes.svg'), W, H, *frags)


def fig_feedback_loop():
    """Фітнес-функція як ланка зворотного зв'язку: поріг зі сценарію —
    порівняння — дія (ворота/тривога) — система (під дрейфом) — вимір — назад."""
    W, H = 900, 430
    frags = []
    frags.append(text(W / 2, 32, "Фітнес-функція як ланка зворотного зв'язку", size=17, bold=True))

    y_top = 135
    sp, w1, h1 = textbox(150, y_top, "поріг зі сценарію\n(бажаний стан)", size=13,
                         fill="#eaf0fd", stroke=NEG)
    frags.append(sp)
    # порівняння
    frags.append(circle(345, y_top, 26, fill=FILL, stroke=INK, sw=1.8))
    frags.append(text(345, y_top + 7, "≷", size=22, bold=True))
    # дія
    act, w3, h3 = textbox(560, y_top, "ворота падають /\nсигнал тривоги", size=13,
                          fill="#fdecea", stroke=POS, bold=True)
    frags.append(act)
    # система
    sysb, w4, h4 = textbox(785, y_top, "Система", size=15, fill=FILL, stroke=INK,
                           bold=True, min_w=120)
    frags.append(sysb)

    # верхні стрілки потоку
    frags.append(arrow(150 + w1 / 2, y_top, 345 - 26, y_top))
    frags.append(arrow(345 + 26, y_top, 560 - w3 / 2, y_top))
    frags.append(arrow(560 + w3 / 2, y_top, 785 - w4 / 2, y_top))

    # збурення в систему згори
    frags.append(text(785, 66, "дрейф: щоденні зміни", size=12, color=POS))
    frags.append(arrow(785, 78, 785, y_top - h4 / 2))

    # шлях зворотного зв'язку: система вниз, ліворуч крізь вимір, угору до порівняння
    y_fb = 340
    frags.append(line(785, y_top + h4 / 2, 785, y_fb, color=LINE, sw=1.8))
    fb, wf, hf = textbox(520, y_fb, "фітнес-функція\nвимірює атрибут", size=13,
                         fill="#eafaf0", stroke=FIELD, bold=True)
    frags.append(fb)
    frags.append(arrow(785, y_fb, 520 + wf / 2, y_fb))
    frags.append(line(520 - wf / 2, y_fb, 345, y_fb, color=LINE, sw=1.8))
    frags.append(arrow(345, y_fb, 345, y_top + 26))
    frags.append(text(432, y_fb - 14, "виміряний стан", size=12, color=MUTED))

    render(os.path.join(IMG, 'feedback-loop.svg'), W, H, *frags)


def fig_fitness_map():
    """Простір фітнес-функцій: рядки — що міряють, колонки-габітати —
    де перевірка природно живе (крапка = живе тут)."""
    W, H = 950, 470
    frags = []
    frags.append(text(W / 2, 30, "Простір фітнес-функцій: що міряють і де живуть", size=16, bold=True))

    cat_x = 40
    ex_x = 270
    cols = [665, 770, 875]          # центри трьох габітат-колонок
    seps = [612, 717, 822]          # вертикальні розділювачі перед колонками
    hy = 92                         # рядок заголовків
    frags.append(text(cat_x, hy, "Що міряють", size=12, bold=True, anchor="start"))
    frags.append(text(ex_x, hy, "Приклад перевірки", size=12, bold=True, anchor="start"))
    heads = ["ворота\nскладання", "стенд /\nтест", "моніторинг\nживого"]
    for cx, hh in zip(cols, heads):
        frags.append(mtext(cx, hy - 6, hh, size=11, bold=True, lh=1.2))

    rows = [
        ("Структура / залежності", "домен не тягне БД; без циклів", [True, False, False]),
        ("Метрики коду", "складність методу ≤ 10", [True, False, False]),
        ("Продуктивність", "p95 ≤ 200 мс", [False, True, True]),
        ("Безпека", "0 залежностей із CVE; 0 секретів у git", [True, False, True]),
        ("Стійкість", "переживає вбивство вузла", [False, True, True]),
        ("Вартість", "місячний рахунок ≤ бюджет", [False, False, True]),
    ]
    y0 = 128
    dy = 48
    # вертикальні розділювачі колонок
    for sx in seps:
        frags.append(line(sx, hy + 14, sx, y0 + dy * (len(rows) - 1) + 20, color=MUTED, sw=1.0))
    for i, (cat, ex, dots) in enumerate(rows):
        y = y0 + i * dy
        if i > 0:
            frags.append(line(cat_x, y - dy / 2 + 4, W - 30, y - dy / 2 + 4, color="#e2e6ea", sw=1.0))
        frags.append(text(cat_x, y, cat, size=13, bold=True, anchor="start"))
        frags.append(text(ex_x, y, ex, size=12, color=MUTED, anchor="start"))
        for cx, on in zip(cols, dots):
            if on:
                frags.append(circle(cx, y - 4, 7, fill=INK, stroke=INK, sw=1))
    frags.append(text(W / 2, H - 20, "● — тут ця перевірка природно живе",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'fitness-map.svg'), W, H, *frags)


def fig_threshold_dynamics():
    """Три способи вести планку в часі: бюджет (нерухома), храповик (тісниться
    за поступом), варена жаба (повзе за метрикою — антипатерн)."""
    W, H = 880, 372
    frags = []
    frags.append(text(W / 2, 26, "Динаміка порогу: три способи вести планку", size=16, bold=True))

    def polyline(pts, color, sw=2.2, dash=None):
        out = []
        for a, b in zip(pts[:-1], pts[1:]):
            out.append(line(a[0], a[1], b[0], b[1], color=color, sw=sw, dash=dash))
        return out

    panels = [(20, "Бюджет", "поріг зі сценарію, нерухомий"),
              (310, "Храповик", "поріг тісниться за поступом"),
              (600, "Варена жаба", "поріг повзе за метрикою")]
    ty, by = 92, 292
    for L, title, sub in panels:
        x0, xr = L + 40, L + 244
        frags.append(text(L + 142, 54, title, size=13, bold=True))
        frags.append(text(L + 142, 72, sub, size=10, color=MUTED))
        # осі
        frags.append(line(x0, ty, x0, by, color=MUTED, sw=1.2))
        frags.append(arrow(x0, by, xr, by, color=MUTED, sw=1.2))
        frags.append(text(xr, by + 16, "час", size=10, color=MUTED))

    # Панель 1 — бюджет: нерухомий поріг, метрика зі сплеском-провалом
    x0 = 60
    frags.append(line(x0, 150, x0 + 204, 150, color=MUTED, sw=1.6, dash="6,4"))
    frags.append(text(x0 - 8, 150, "поріг", size=10, color=MUTED, anchor="end"))
    m1 = [(x0, 212), (x0 + 34, 202), (x0 + 68, 216), (x0 + 102, 120),
          (x0 + 136, 206), (x0 + 170, 212), (x0 + 204, 204)]
    frags.extend(polyline(m1, NEG))
    frags.append(text(x0 + 102, 108, "×", size=20, color=POS, bold=True))
    frags.append(text(x0 + 102, 96, "провал", size=10, color=POS, bold=True))

    # Панель 2 — храповик: метрика спадає (поступ), поріг сходинками тісниться
    x0 = 350
    m2 = [(x0, 150), (x0 + 40, 176), (x0 + 82, 196), (x0 + 124, 216),
          (x0 + 166, 232), (x0 + 204, 246)]
    frags.extend(polyline(m2, NEG))
    ratchet = [(x0, 132), (x0 + 60, 132), (x0 + 60, 178), (x0 + 120, 178),
               (x0 + 120, 210), (x0 + 180, 210), (x0 + 180, 236), (x0 + 204, 236)]
    frags.extend(polyline(ratchet, MUTED, sw=1.6, dash="6,4"))

    # Панель 3 — варена жаба: метрика повзе вгору, поріг повзе слідом
    x0 = 640
    m3 = [(x0, 240), (x0 + 40, 226), (x0 + 82, 212), (x0 + 124, 198),
          (x0 + 166, 185), (x0 + 204, 172)]
    frags.extend(polyline(m3, NEG))
    c3 = [(x0, 214), (x0 + 40, 200), (x0 + 82, 187), (x0 + 124, 173),
          (x0 + 166, 160), (x0 + 204, 147)]
    frags.extend(polyline(c3, MUTED, sw=1.6, dash="6,4"))

    # легенда
    frags.append(line(120, 344, 150, 344, color=MUTED, sw=1.6, dash="6,4"))
    frags.append(text(158, 348, "поріг", size=11, color=MUTED, anchor="start"))
    frags.append(line(250, 344, 280, 344, color=NEG, sw=2.2))
    frags.append(text(288, 348, "виміряна властивість", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'threshold-dynamics.svg'), W, H, *frags)


def fig_hist_landscape():
    """Ландшафт пристосованості Райта: висота = фітнес; сліпий добір лізе вгору
    дрібним кроком і застрягає на локальній вершині, бо ландшафт нерівний."""
    import math
    W, H = 880, 450
    x0, x1 = 74, 812          # межі осі генотипів
    yb, yt = 366, 96          # низ (нуль) і верх (макс висоти)
    Hspan = yb - yt
    frags = []
    frags.append(text(W / 2, 30, "Ландшафт пристосованості: висота = фітнес", size=17, bold=True))

    def f(t):
        return (0.62 * math.exp(-((t - 0.28) / 0.10) ** 2) +
                0.96 * math.exp(-((t - 0.72) / 0.115) ** 2) +
                0.17 * math.exp(-((t - 0.50) / 0.045) ** 2) +
                0.12 * math.exp(-((t - 0.09) / 0.055) ** 2))

    def px(t):
        return x0 + t * (x1 - x0)

    def py(t):
        return yb - f(t) * Hspan

    # силует ландшафту (заливка) + контур
    n = 160
    pts = [(px(i / n), py(i / n)) for i in range(n + 1)]
    dpath = "M %.1f,%.1f " % (x0, yb)
    dpath += "".join("L %.1f,%.1f " % (x, y) for x, y in pts)
    dpath += "L %.1f,%.1f Z" % (x1, yb)
    frags.append('<path d="%s" fill="#eef2f7" stroke="none"/>' % dpath)
    # осі (поверх заливки)
    frags.append(arrow(x0, yb, x0, yt - 4, color=MUTED, sw=1.4))
    frags.append(arrow(x0, yb, x1 + 4, yb, color=MUTED, sw=1.4))
    frags.append(text(x0 + 6, yt + 2, "пристосованість", size=12, color=MUTED, anchor="start"))
    frags.append(text(x1 - 4, yb + 22, "простір генотипів", size=12, color=MUTED, anchor="end"))
    # контур ландшафту
    cpath = "M %.1f,%.1f " % pts[0] + "".join("L %.1f,%.1f " % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (cpath, INK))

    # локальна й глобальна вершини
    tl, tg = 0.28, 0.72
    frags.append(circle(px(tl), py(tl) - 9, 8, fill=POS, stroke=INK, sw=1.6))  # сліпий добір
    frags.append(mtext(px(tl) - 96, 150, "локальна вершина\n(пастка сліпого\nдобору)",
                       size=12, bold=True, anchor="middle", lh=1.25))
    frags.append(arrow(px(tl) - 60, 168, px(tl) - 8, py(tl) - 18, color=INK, sw=1.4))
    frags.append(text(px(tg), py(tg) - 16, "глобальна вершина", size=12, bold=True))

    # дуга «дрібним кроком не дійти» через долину
    frags.append('<path d="M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="6,5" '
                 'marker-end="url(#arrow)"/>' %
                 (px(tl) + 6, py(tl) - 12, (px(tl) + px(tg)) / 2, 66,
                  px(tg) - 4, py(tg) - 10, MUTED))
    frags.append(mtext((px(tl) + px(tg)) / 2, 232, "між вершинами — долина:\nдрібним кроком угору не дійти",
                       size=12, color=MUTED, anchor="middle", lh=1.25))

    # епістаз як причина нерівності
    b, w, h = textbox(W / 2, 418, "нерівність ландшафту ← епістаз: ген, добрий в одному наборі, шкідливий в іншому",
                      size=12, fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    render(os.path.join(IMG, 'hist-landscape.svg'), W, H, *frags)


def fig_hist_relay():
    """Естафета поняття «фітнес» крізь чотири станції: одна незмінна суть
    (спинний хребет-стрілка) і чотири щоразу інші «костюми» міри."""
    W, H = 1080, 398
    frags = []
    frags.append(text(W / 2, 28, "Одне слово, чотири костюми: як мандрував «фітнес»", size=17, bold=True))

    cols = [166, 410, 656, 906]
    seps = [288, 533, 781]
    years = ["1864", "1932", "1975", "2017"]
    names = ["Герберт\nСпенсер", "Сьюол\nРайт", "Джон\nГолланд", "Форд · Парсонс\n· Куа"]
    domains = ["біологія-\nгасло", "популяційна\nгенетика", "генетичні\nалгоритми", "архітектура\nПЗ"]
    forms = ["гасло:\n«виживання\nнайпристосованіших»",
             "висота-число\nна нерівному\nландшафті",
             "функція, яку\nПИШУТЬ, — плавний\nчисло-компас",
             "вирок:\nпройшло /\nне пройшло"]
    form_fill = ["#eaf0fd", "#eafaf0", "#f4f6f8", "#fdecea"]
    form_stroke = [NEG, FIELD, INK, POS]
    moves = ["назвав ідею,\nале не дав міри",
             "дав фітнесу\nгеометрію:\nвисота й вершини",
             "зробив міру\nобчислюваною —\nкомпас сліпого пошуку",
             "плавний градієнт\n→ різкий поріг"]

    for cx, sep in zip(cols, seps):
        frags.append(line(sep, 48, sep, 300, color="#d7dbe0", sw=1.0, dash="4,5"))

    for cx, yr, nm, dm, fm, ff, fs, mv in zip(cols, years, names, domains, forms,
                                              form_fill, form_stroke, moves):
        frags.append(text(cx, 66, yr, size=20, bold=True))
        frags.append(mtext(cx, 88, nm, size=13, bold=True, lh=1.2))
        frags.append(mtext(cx, 126, dm, size=11, color=MUTED, lh=1.2))
        b, w, h = textbox(cx, 194, fm, size=12, fill=ff, stroke=fs, bold=False)
        frags.append(b)
        frags.append(mtext(cx, 250, mv, size=11, color=MUTED, lh=1.25))

    # спинний хребет — те, що незмінне крізь усі переходи
    frags.append(arrow(94, 326, W - 90, 326, color=INK, sw=2.0))
    frags.append(mtext(W / 2, 352, "наскрізне крізь усі переходи: об'єктивна міра близькості до мети, "
                       "що напрямляє сліпий інкрементний добір",
                       size=12, bold=True, lh=1.25))

    render(os.path.join(IMG, 'hist-relay.svg'), W, H, *frags)


def fig_three_regressions():
    """Три регресії у графі залежностей — кожну ловить свій із трьох гейтів:
    заборонена залежність (досяжність), порушення шарів, цикл."""
    W, H = 980, 440
    frags = []
    frags.append(text(W / 2, 28, "Три регресії — кожну ловить своя перевірка", size=17, bold=True))
    for sx in (327, 654):
        frags.append(line(sx, 95, sx, 330, color="#d7dbe0", sw=1.0, dash="4,5"))

    # ── Панель A: заборонена залежність (досяжність) ──
    cx = 164
    frags.append(text(cx, 60, "Заборонена залежність", size=14, bold=True))
    frags.append(text(cx, 78, "(досяжність)", size=11, color=MUTED))
    b, _, _ = textbox(cx, 120, "orders", size=13); frags.append(b)
    b, _, _ = textbox(cx, 200, "db", size=13); frags.append(b)
    b, _, _ = textbox(cx, 280, "legacy", size=13); frags.append(b)
    frags.append(arrow(cx, 138, cx, 182, color=MUTED, sw=1.7))
    frags.append(arrow(cx, 218, cx, 262, color=POS, sw=2.6))
    frags.append(text(cx + 44, 242, "нове", size=10, color=POS, bold=True))
    frags.append(mtext(cx, 337, ["orders → db → legacy", "⇒ orders досягає legacy"],
                       size=11, color=POS, lh=1.3))

    # ── Панель B: порушення шарів ──
    cx = 490
    frags.append(text(cx, 60, "Порушення шарів", size=14, bold=True))
    frags.append(text(cx, 78, "(частковий порядок)", size=11, color=MUTED))
    b, _, _ = textbox(cx, 150, "report", size=13); frags.append(b)
    b, _, _ = textbox(cx, 285, "legacy", size=13); frags.append(b)
    frags.append(line(405, 217, 575, 217, color=MUTED, sw=1.0, dash="6,4"))
    frags.append(text(400, 150, "рівень 2", size=11, color=MUTED, anchor="end"))
    frags.append(text(400, 289, "рівень 0", size=11, color=MUTED, anchor="end"))
    frags.append(arrow(cx, 267, cx, 168, color=POS, sw=2.6))
    frags.append(text(548, 198, "вгору", size=10, color=POS, bold=True))
    frags.append(mtext(cx, 342, ["legacy (0) → report (2)", "⇒ ребро вгору крізь шар"],
                       size=11, color=POS, lh=1.3))

    # ── Панель C: цикл (взаємний імпорт) ──
    ax, bx = 755, 880
    frags.append(text(817, 60, "Цикл", size=14, bold=True))
    frags.append(text(817, 78, "(взаємний імпорт)", size=11, color=MUTED))
    frags.append(text(817, 162, "report → orders (є)", size=10, color=MUTED))
    b, _, _ = textbox(ax, 200, "orders", size=13); frags.append(b)
    b, _, _ = textbox(bx, 200, "report", size=13); frags.append(b)
    frags.append(arrow(bx - 32, 189, ax + 32, 189, color=MUTED, sw=1.7))
    frags.append(arrow(ax + 32, 213, bx - 32, 213, color=POS, sw=2.6))
    frags.append(mtext(817, 250, ["orders ⇄ report", "⇒ два модулі = один ком"],
                       size=11, color=POS, lh=1.3))

    render(os.path.join(IMG, 'three-regressions.svg'), W, H, *frags)


def fig_tricolor_dfs():
    """Трибарвний обхід у глибину ловить цикл: коли ребро веде у СІРИЙ вузол
    (той, що ще в стеку обходу) — це замкнений шлях назад, тобто цикл."""
    W, H = 920, 470
    frags = []
    frags.append(text(W / 2, 28, "Трибарвний обхід ловить цикл: ребро у сіре", size=17, bold=True))
    GRAY = "#c7ccd3"

    def node(cx, cy, label, kind):
        if kind == "black":
            return (circle(cx, cy, 26, fill=INK, stroke=INK, sw=2) +
                    text(cx, cy + 6, label, size=16, color="#ffffff", bold=True))
        fill = GRAY if kind == "gray" else FILL
        return circle(cx, cy, 26, fill=fill, stroke=INK, sw=2) + text(cx, cy + 6, label, size=16, bold=True)

    A, B, C, D, E = (250, 135), (165, 255), (335, 255), (250, 360), (110, 140)
    frags.append(arrow(A[0] - 18, A[1] + 18, B[0] + 14, B[1] - 16, color=MUTED, sw=1.7))
    frags.append(arrow(B[0] + 26, B[1], C[0] - 26, C[1], color=MUTED, sw=1.7))
    frags.append(arrow(C[0] - 6, C[1] + 22, D[0] + 18, D[1] - 16, color=MUTED, sw=1.7))
    frags.append(arrow(A[0] - 22, A[1] - 6, E[0] + 22, E[1] + 2, color=MUTED, sw=1.4))
    frags.append(arrow(C[0] - 14, C[1] - 20, A[0] + 16, A[1] + 20, color=POS, sw=2.6))
    frags.append(node(*A, "A", "gray"))
    frags.append(node(*B, "B", "gray"))
    frags.append(node(*C, "C", "gray"))
    frags.append(node(*D, "D", "black"))
    frags.append(node(*E, "E", "white"))
    frags.append(text(360, 315, "ребро назад", size=11, color=POS, bold=True))

    frags.append(text(610, 92, "стек обходу (сірі)", size=13, bold=True))
    frags.append(text(548, 134, "верх →", size=10, color=MUTED, anchor="end"))
    for lab, yy in (("C", 130), ("B", 172), ("A", 214)):
        b, _, _ = textbox(610, yy, lab, size=13, fill=GRAY, stroke=INK, min_w=110)
        frags.append(b)
    frags.append(mtext(702, 300, ["C → A веде у СІРЕ:", "A ще в стеку ⇒ цикл", "A → B → C → A"],
                       size=13, color=POS, lh=1.35))

    frags.append(circle(120, 443, 11, fill=FILL, stroke=INK))
    frags.append(text(140, 447, "біле — не чіпали", size=12, anchor="start"))
    frags.append(circle(360, 443, 11, fill=GRAY, stroke=INK))
    frags.append(text(380, 447, "сіре — у стеку обходу", size=12, anchor="start"))
    frags.append(circle(660, 443, 11, fill=INK, stroke=INK))
    frags.append(text(680, 447, "чорне — завершено", size=12, anchor="start"))

    render(os.path.join(IMG, 'tricolor-dfs.svg'), W, H, *frags)


def fig_gate_lattice():
    """Три гейти за тим, що кожному ТРЕБА на вході й що він ЛОВИТЬ:
    цикл потребує лише графа, шари — карти рівнів, заборона — названої пари."""
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 28, "Три перевірки: що кожній треба і що вона ловить", size=17, bold=True))
    frags.append(line(268, 70, 268, 325, color="#d7dbe0", sw=1.0))
    frags.append(line(90, 158, 900, 158, color="#e2e6ea", sw=1.0))
    frags.append(line(90, 250, 900, 250, color="#e2e6ea", sw=1.0))

    rows = [
        (112, "Заборонена\n(досяжність)", NEG,
         ["треба: названа пара  X ⇏ Y",
          "ловить: будь-який шлях X → … → Y",
          "     (навіть того ж рівня, навіть униз)"]),
        (204, "Шари\n(частковий порядок)", FIELD,
         ["треба: рівень кожного модуля",
          "ловить: будь-яке ребро вгору",
          "     (рівень зростає)"]),
        (296, "Цикли\n(3-колірний DFS)", POS,
         ["треба: лише граф, і все",
          "ловить: будь-який цикл",
          "     (кожен цикл має ребро вгору)"]),
    ]
    for cy, name, col, lines in rows:
        b, _, _ = textbox(150, cy, name, size=13, stroke=col, bold=True)
        frags.append(b)
        frags.append(mtext(300, cy - 14, lines, size=12, anchor="start", lh=1.3))

    b, _, _ = textbox(W / 2, 385,
                      "Кожен цикл несе ребро вгору → повні рівні вже підказують цикли;\n"
                      "а названа пара ловить те, що шари й цикли пропускають.",
                      size=12, fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    render(os.path.join(IMG, 'gate-lattice.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_rule_vs_gate()
    fig_axes()
    fig_feedback_loop()
    fig_fitness_map()
    fig_threshold_dynamics()
    fig_hist_landscape()
    fig_hist_relay()
    fig_three_regressions()
    fig_tricolor_dfs()
    fig_gate_lattice()
    print("figs done")
