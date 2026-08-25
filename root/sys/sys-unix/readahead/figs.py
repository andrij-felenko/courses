# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WAIT = "#fdecea"   # програма стоїть
WORK = "#eafaf0"   # програма працює
DEV  = "#eaf0fd"   # пристрій передає
SOFT = "#fbfcff"
WARM = "#fdf3e7"
AMBER = "#b7791f"


# ── 1. Де програма стоїть: три режими одного й того самого читання ────────────
def fig_stall_timeline():
    W, H = 1200, 600
    p = []

    LX, LW = 30, 180          # колонка з назвою режиму
    X0, LANE = 340, 830       # смуги часу
    tops = [70, 250, 420]

    labels = [
        "Без випереджувального читання:\nкожна порція — окреме звертання\nдо пристрою",
        "Тільки синхронне вікно:\nодне велике звертання\nна кожні 128 КБ",
        "Асинхронне вікно з позначкою:\nнаступне замовлення йде,\nпоки читач ще має що читати",
    ]

    def lane(x, y, w, fill, stroke, cap=None):
        out = rect(x, y, w, 34, fill=fill, stroke=stroke, sw=1.4, rx=3)
        if cap and w > 62:
            out += text(x + w / 2, y + 22, cap, size=10.5, color=MUTED)
        return out

    for i, T in enumerate(tops):
        p.append(fitbox(LX, T + 6, LW, 92, labels[i], size=11.5,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(text(X0 - 16, T + 40, "програма", size=10.5, color=MUTED, anchor="end"))
        p.append(text(X0 - 16, T + 96, "пристрій", size=10.5, color=MUTED, anchor="end"))
        p.append(rect(X0, T + 18, LANE, 34, fill="#ffffff", stroke="#d7dbe0", sw=1.0, rx=3))
        p.append(rect(X0, T + 74, LANE, 34, fill="#ffffff", stroke="#d7dbe0", sw=1.0, rx=3))

    # режим 1 — шість однакових циклів «чекання → крихітна робота»
    T = tops[0]
    x = X0
    for _ in range(6):
        p.append(lane(x, T + 18, 96, WAIT, POS))
        p.append(lane(x, T + 74, 96, DEV, NEG))
        p.append(lane(x + 96, T + 18, 42, WORK, FIELD))
        x += 138

    # режим 2 — довге чекання на межі вікна, потім довга робота
    T = tops[1]
    x = X0
    for _ in range(2):
        p.append(lane(x, T + 18, 118, WAIT, POS))
        p.append(lane(x, T + 74, 118, DEV, NEG, "128 КБ"))
        p.append(lane(x + 118, T + 18, 292, WORK, FIELD))
        x += 410

    # режим 3 — чекання лише на самому початку
    T = tops[2]
    p.append(lane(X0, T + 18, 118, WAIT, POS))
    p.append(lane(X0, T + 74, 118, DEV, NEG, "128 КБ"))
    p.append(lane(X0 + 118, T + 18, LANE - 118, WORK, FIELD))
    for k in range(3):
        tick = X0 + 180 + 240 * k
        p.append(lane(tick, T + 74, 118, DEV, NEG, "128 КБ"))
        p.append(line(tick, T + 12, tick, T + 52, color=POS, sw=2.0))
    p.append(text(X0 + 180, T - 2, "дотик до позначеної сторінки — сигнал замовити наступне вікно",
                  size=11, color=POS, anchor="start"))

    # шкала часу
    p.append(arrow(X0, H - 78, X0 + LANE, H - 78, color=MUTED, sw=1.4))
    p.append(text(X0 + LANE, H - 58, "час", size=11, color=MUTED, anchor="end"))

    # легенда
    lg = [("програма стоїть і чекає", WAIT, POS),
          ("програма опрацьовує дані", WORK, FIELD),
          ("пристрій передає порцію", DEV, NEG)]
    lx = LX
    for cap, fill, stroke in lg:
        p.append(rect(lx, H - 40, 26, 18, fill=fill, stroke=stroke, sw=1.4, rx=3))
        p.append(text(lx + 34, H - 26, cap, size=11, color=MUTED, anchor="start"))
        lx += 34 + text_width(cap, 11) + 46

    render(os.path.join(OUT, "stall-timeline.svg"), W, H, *p)


# ── 2. Будова вікна: синхронна частина, асинхронна частина, позначка ──────────
def fig_window_anatomy():
    W, H = 1180, 520
    p = []

    N, CX, CW, CY, CH = 20, 60, 53, 250, 54
    for i in range(N):
        x = CX + i * CW
        if i < 4:
            fill, stroke = "#f0f1f3", "#c3c7cc"        # прочитане раніше
        elif i < 12:
            fill, stroke = WORK, FIELD                  # вже в пам'яті
        else:
            fill, stroke = WARM, AMBER
        p.append(rect(x, CY, CW, CH, fill=fill, stroke=stroke, sw=1.4, rx=3))
    p.append(circle(CX + 12 * CW + CW / 2, CY + CH / 2, 8, fill="#fdecea", stroke=POS, sw=2.2))

    wx0, wx1 = CX + 4 * CW, CX + N * CW
    ax0 = CX + 12 * CW

    p.append(line(wx0, 170, wx1, 170, color=NEG, sw=1.8))
    p.append(line(wx0, 162, wx0, 178, color=NEG, sw=1.8))
    p.append(line(wx1, 162, wx1, 178, color=NEG, sw=1.8))
    p.append(text(wx0, 150, "вікно цього замовлення: size сторінок", size=12,
                  color=NEG, anchor="start"))

    p.append(line(ax0, 210, wx1, 210, color=AMBER, sw=1.8))
    p.append(line(ax0, 202, ax0, 218, color=AMBER, sw=1.8))
    p.append(line(wx1, 202, wx1, 218, color=AMBER, sw=1.8))
    p.append(text(ax0, 230, "асинхронна частина: async_size сторінок", size=12,
                  color=AMBER, anchor="start"))

    rx = CX + 5 * CW + CW / 2
    p.append(arrow(rx, 344, rx, 310, color=INK, sw=1.6))
    p.append(text(rx, 364, "тут читач зараз; сюди вказує prev_pos", size=11.5,
                  color=MUTED, anchor="middle"))

    mx = ax0 + CW / 2
    p.append(arrow(mx, 310, mx, 396, color=POS, sw=1.8))
    p.append(fitbox(ax0 - 40, 400, 620, 84,
                    "дотик до позначеної сторінки нікого не затримує — вона вже в пам'яті;\n"
                    "ядро знімає позначку й замовляє наступне вікно у фоні",
                    size=12, fill="#fdecea", stroke=POS, sw=1.4))

    p.append(text(CX, 106, "файл, посторінково", size=11.5, color=MUTED, anchor="start"))
    p.append(text(CX, CY + CH + 26, "прочитане", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "readahead-window.svg"), W, H, *p)


# ── 3. Що ядро бачить і що з того висновує ───────────────────────────────────
def fig_decision():
    W, H = 1180, 540
    p = []

    p.append(fitbox(310, 40, 560, 58,
                    "чергове звертання: опис відкритого файлу, зсув, скільки байтів",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.4, bold=True))

    cols = [
        (30, "зсув продовжує попереднє читання\nабо це початок файлу",
             "послідовне: відкрити вікно й нарощувати\nйого вчетверо, далі вдвічі —\nдо стелі read_ahead_kb",
             NEG, DEV),
        (420, "потрібна сторінка вже в пам'яті\nі несе позначку",
              "чекати нічого: зняти позначку\nй замовити наступне вікно,\nне зупиняючи читача",
              FIELD, WORK),
        (810, "зсув стрибнув, сусідніх сторінок\nу пам'яті немає",
              "випадкове: вікна не відкривати,\nпрочитати рівно стільки,\nскільки попросили",
              POS, WAIT),
    ]

    for x, cond, act, accent, tint in cols:
        p.append(fitbox(x, 170, 340, 84, cond, size=12.5, fill="#ffffff", stroke=accent, sw=1.6))
        p.append(arrow(x + 170, 258, x + 170, 316, color=accent, sw=1.8))
        p.append(fitbox(x, 320, 340, 104, act, size=12.5, fill=tint, stroke=accent, sw=1.6))
        p.append(arrow(590, 100, x + 170, 166, color=MUTED, sw=1.4))

    p.append(text(590, 470, "стан здогаду живе в описі відкритого файлу: "
                            "start, size, async_size, prev_pos",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "readahead-decision.svg"), W, H, *p)


# ── 4. Родовід: що додавав кожен крок і де жив стан здогаду ──────────────────
def fig_lineage():
    W, H = 1400, 690
    p = []

    LX, LW = 26, 160
    CX0, CW, GAP = 210, 280, 12

    rows = [
        (172, 74,  "епоха"),
        (272, 116, "що додав"),
        (404, 116, "яку проблему закрив"),
        (536, 112, "де живе стан здогаду"),
    ]

    eras = [
        ("1975", NEG, DEV,
         "breada\nUnix, шоста редакція",
         "наступний блок замовляють\nасинхронно — виклик на нього\nвже не чекає",
         "програма спинялася на кожному\nблоці: чекання ніяк\nне перекривалося обробкою",
         "ніде: наступний блок\nназиває сам виклик"),
        ("1991", FIELD, WORK,
         "кластерне читання\nSunOS, файлова система BSD",
         "суміжні блоки збирають\nв одне велике звертання\nдо пристрою",
         "сталу ціну звертання: вісім\nзапитів по 8 КБ коштували\nвосьмеро проти одного",
         "у розкладці файлу:\nнаскільки суцільно\nлежать його блоки"),
        ("2001–2006", AMBER, WARM,
         "поточне вікно й вікно-наперед\nLinux 2.4–2.6",
         "глибина здогаду росте сама,\nа наступне замовлення йде\nще до кінця поточного вікна",
         "стелю в один крок наперед —\nале обріс окремою латкою\nна кожен незручний випадок",
         "в окремій обліковій структурі:\nядро мусить бачити\nкожнісіньке звертання"),
        ("2007", POS, WAIT,
         "позначка PG_readahead\nLinux 2.6.23",
         "прапорець на одній сторінці\nзамість другого вікна: дотик\nдо неї й запускає наступне",
         "потребу стежити за всім —\nлатки на промахи, повтори\nй нестачу пам'яті зникли",
         "у самих даних, поряд\nзі сторінкою, якої стосується"),
    ]

    for y, h, cap in rows:
        p.append(fitbox(LX, y, LW, h, cap, size=12.5, fill=SOFT,
                        stroke=MUTED, sw=1.2, color=MUTED))

    p.append(arrow(CX0 - 24, 118, CX0 + 4 * (CW + GAP) - GAP + 16, 118, color=MUTED, sw=1.6))
    p.append(text(LX, 122, "час", size=12, color=MUTED, anchor="start"))

    for i, (year, accent, tint, name, added, closed, state) in enumerate(eras):
        x = CX0 + i * (CW + GAP)
        cx = x + CW / 2
        p.append(circle(cx, 118, 7, fill="#ffffff", stroke=accent, sw=2.4))
        p.append(text(cx, 94, year, size=13, color=accent, bold=True))
        p.append(fitbox(x, rows[0][0], CW, rows[0][1], name, size=12.5,
                        fill=tint, stroke=accent, sw=1.6, bold=True))
        p.append(fitbox(x, rows[1][0], CW, rows[1][1], added, size=12,
                        fill="#ffffff", stroke=accent, sw=1.4))
        p.append(fitbox(x, rows[2][0], CW, rows[2][1], closed, size=12,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(x, rows[3][0], CW, rows[3][1], state, size=12,
                        fill=tint, stroke=accent, sw=1.4))

    p.append(text(LX, 668, "ідея за всі півстоліття не змінилася — переїжджав лише стан здогаду: "
                           "від того, хто кличе, до розкладки на носії, звідти в облік ядра — і врешті в самі дані",
                  size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "readahead-lineage.svg"), W, H, *p)


# ── 5. Три лічильники на одному шляху читання ────────────────────────────────
def fig_counters():
    W, H = 1260, 660
    p = []

    SX, SW = 30, 300          # колонка стадій
    MX, MW = 380, 300         # що і де рахують
    RX, RW = 720, 510         # на яке питання відповідає число
    SH = 82

    stages = [
        (40,  "програма:\npread(fd, buf, 4096)", SOFT, MUTED),
        (192, "кеш сторінок", WORK, FIELD),
        (344, "блоковий рівень:\nзлиття запитів і черга", DEV, NEG),
        (496, "накопичувач", WARM, AMBER),
    ]
    for y, cap, tint, accent in stages:
        p.append(fitbox(SX, y, SW, SH, cap, size=13, fill=tint, stroke=accent, sw=1.6))

    gaps = [
        (122, 192, MUTED,
         "rchar, syscr\n/proc/self/io",
         "скільки байтів повернули виклики читання.\n"
         "Влучання в кеш рахуються теж — тому сам собою\n"
         "цей лічильник про носій не каже нічого.\n"
         "Через відображення в пам'ять він і зовсім нуль."),
        (274, 344, FIELD,
         "read_bytes\n/proc/self/io",
         "скільки байтів це завдання справді замовило\n"
         "з носія — разом із прочитаним наперед.\n"
         "У гарячому прогоні тут нуль: влучання\n"
         "в кеш сюди не доходить."),
        (426, 496, NEG,
         "поля 1 і 3\n/sys/dev/block/M:m/stat",
         "скільки вийшло ЗАПИТІВ і по скільки секторів\n"
         "у кожному — уже після злиття сусідніх.\n"
         "Рахує весь пристрій, а не лише нас:\n"
         "міряти треба на тихій машині."),
    ]
    cx = SX + SW / 2
    for y0, y1, accent, who, what in gaps:
        gc = (y0 + y1) / 2
        p.append(arrow(cx, y0, cx, y1 - 4, color=INK, sw=1.8))
        p.append(line(cx, gc, MX - 6, gc, color=accent, sw=1.3, dash="4 4"))
        p.append(fitbox(MX, gc - 43, MW, 86, who, size=12.5, fill="#ffffff",
                        stroke=accent, sw=1.6, bold=True))
        p.append(fitbox(RX, gc - 43, RW, 86, what, size=12, fill=SOFT,
                        stroke=MUTED, sw=1.2, color=INK))

    p.append(text(SX, 614, "три числа — три різні питання; саме розбіжність між ними "
                           "й міряє випереджувальне читання",
                  size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "counters-path.svg"), W, H, *p)


# ── Арифметика вікна: смуга, розгін, ціна помилки ────────────────────────────
import math

KB = 1024.0
MB = 1024.0 * 1024.0


def _polyline(pts, color, sw=2.2, dash=None):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    extra = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, color, sw, extra))


def fig_window_efficiency():
    W, H = 1180, 600
    PX, PY, PW, PH = 120, 95, 860, 320
    p = []

    def xs(w):
        return PX + PW * (math.log(w, 2) - 14.0) / 9.0

    def ys(e):
        return PY + PH - PH * e

    p.append(text(40, 44, "яку частку смуги пристрою віддає один послідовний читач "
                          "із вікном W", size=15, color=INK, anchor="start", bold=True))

    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = ys(frac)
        p.append(line(PX, y, PX + PW, y, color="#e3e6ea", sw=1.0))
        p.append(text(PX - 14, y + 4, "%d %%" % int(frac * 100), size=11,
                      color=MUTED, anchor="end"))
    p.append(line(PX, PY, PX, PY + PH, color=MUTED, sw=1.4))
    p.append(line(PX, PY + PH, PX + PW, PY + PH, color=MUTED, sw=1.4))

    caps = ["16 КБ", "32 КБ", "64 КБ", "128 КБ", "256 КБ", "512 КБ",
            "1 МБ", "2 МБ", "4 МБ", "8 МБ"]
    for i, cap in enumerate(caps):
        x = xs(2.0 ** (14 + i))
        p.append(line(x, PY + PH, x, PY + PH + 6, color=MUTED, sw=1.2))
        p.append(text(x, PY + PH + 24, cap, size=11, color=MUTED))
    p.append(text(PX + PW / 2, PY + PH + 52, "розмір вікна W", size=12, color=MUTED))

    xc = xs(128 * KB)
    p.append(line(xc, PY - 4, xc, PY + PH, color=MUTED, sw=1.2, dash="5 5"))
    p.append(text(xc, PY - 14, "типова стеля 128 КБ", size=11.5, color=MUTED))

    devs = [
        ("жорсткий диск 7200 об/хв", 18e3, INK,
         "B·T ≈ 18 КБ · вікно 128 КБ віддає 88 % смуги"),
        ("SATA-SSD", 55e3, FIELD,
         "B·T ≈ 55 КБ · вікно 128 КБ віддає 70 % смуги"),
        ("NVMe PCIe 3.0 ×4", 240e3, NEG,
         "B·T ≈ 240 КБ · вікно 128 КБ віддає 35 % смуги"),
        ("NVMe PCIe 5.0 ×4", 840e3, POS,
         "B·T ≈ 840 КБ · вікно 128 КБ віддає 13 % смуги"),
    ]

    for _name, D, col, _note in devs:
        pts = []
        for i in range(97):
            w = 2.0 ** (14.0 + 9.0 * i / 96.0)
            pts.append((xs(w), ys(w / (w + D))))
        p.append(_polyline(pts, col))
        wc = 128 * KB
        p.append(circle(xc, ys(wc / (wc + D)), 4.5, fill="#ffffff", stroke=col, sw=2.0))

    ly = 486
    for name, _D, col, note in devs:
        p.append(line(46, ly - 4, 76, ly - 4, color=col, sw=3.4))
        p.append(text(90, ly, "%s — %s" % (name, note), size=12,
                      color=INK, anchor="start"))
        ly += 26

    render(os.path.join(OUT, "window-efficiency.svg"), W, H, *p)


def fig_ramp_sum():
    W, H = 1140, 470
    p = []

    RAMP, CEIL = "#fdf3e7", "#eaf0fd"

    def panel(y0, title, ramp, ceiling, scale, note1, note2):
        out = [text(56, y0, title, size=13.5, color=INK, anchor="start", bold=True)]
        x = 56
        for n in ramp:
            w = n * scale
            out.append(rect(x, y0 + 18, w, 40, fill=RAMP, stroke=AMBER, sw=1.4, rx=3))
            if w >= 44:
                out.append(text(x + w / 2, y0 + 44, str(n), size=13, color=AMBER))
            else:
                out.append(text(x + w / 2, y0 + 12, str(n), size=10.5, color=AMBER))
            x += w
        xend = x
        out.append(rect(56, y0 + 74, ceiling * scale, 40, fill=CEIL, stroke=NEG, sw=1.4, rx=3))
        word = "сторінки" if ceiling % 10 in (2, 3, 4) and ceiling % 100 not in (12, 13, 14) else "сторінок"
        out.append(text(56 + ceiling * scale / 2, y0 + 100,
                        "стеля %d %s" % (ceiling, word), size=13, color=NEG))
        xb = 56 + ceiling * scale
        out.append(line(xend, y0 + 126, xb, y0 + 126, color=POS, sw=1.8))
        out.append(line(xend, y0 + 120, xend, y0 + 132, color=POS, sw=1.8))
        out.append(line(xb, y0 + 120, xb, y0 + 132, color=POS, sw=1.8))
        out.append(text(700, y0 + 34, note1, size=12.5, color=MUTED, anchor="start"))
        out.append(text(700, y0 + 58, note2, size=12.5, color=POS, anchor="start"))
        return out

    p += panel(58, "стеля 128 КБ (32 сторінки): множники лише ×2",
               [4, 8, 16], 32, 17.0,
               "4 + 8 + 16 = 28 сторінок = 112 КБ",
               "хвіст до стелі — рівно перше вікно")
    p += panel(268, "стеля 1 МБ (256 сторінок): спершу ×4, далі ×2",
               [4, 16, 32, 64, 128], 256, 2.1,
               "4 + 16 + 32 + 64 + 128 = 244 сторінки = 976 КБ",
               "і знову майже рівно стеля")

    render(os.path.join(OUT, "ramp-sum.svg"), W, H, *p)


def fig_window_price():
    W, H = 1080, 540
    PX, PY, PW, PH = 130, 90, 800, 330
    p = []

    def xs(e):
        return PX + PW * e / 0.95

    def ys(r):
        return PY + PH - PH * (r - 1.0) / 19.0

    p.append(text(40, 44, "чим більше смуги забирає вікно, тим дорожче обходиться "
                          "хибний здогад", size=15, color=INK, anchor="start", bold=True))

    for r in (1, 5, 10, 15, 20):
        y = ys(r)
        p.append(line(PX, y, PX + PW, y, color="#e3e6ea", sw=1.0))
        p.append(text(PX - 14, y + 4, "×%d" % r, size=11, color=MUTED, anchor="end"))
    p.append(line(PX, PY, PX, PY + PH, color=MUTED, sw=1.4))
    p.append(line(PX, PY + PH, PX + PW, PY + PH, color=MUTED, sw=1.4))
    for e in (0.0, 0.2, 0.4, 0.6, 0.8, 0.95):
        x = xs(e)
        p.append(line(x, PY + PH, x, PY + PH + 6, color=MUTED, sw=1.2))
        p.append(text(x, PY + PH + 24, "%d %%" % int(round(e * 100)), size=11, color=MUTED))
    p.append(text(PX + PW / 2, PY + PH + 52,
                  "η — частка смуги пристрою, яку віддає вікно", size=12, color=MUTED))

    pts = []
    for i in range(121):
        e = 0.95 * i / 120.0
        pts.append((xs(e), ys(1.0 / (1.0 - e))))
    p.append(_polyline(pts, NEG, sw=2.4))

    p.append(mtext(158, 128, ["NVMe PCIe 3.0 ×4:  B·T = 240 КБ",
                              "надлишок  =  1 / (1 − η)"],
                   size=12.5, color=MUTED, anchor="start"))

    D = 240e3
    for w, cap in ((128 * KB, "128 КБ"), (256 * KB, "256 КБ"), (512 * KB, "512 КБ"),
                   (1 * MB, "1 МБ"), (2 * MB, "2 МБ"), (4 * MB, "4 МБ")):
        e = w / (w + D)
        x, y = xs(e), ys(1.0 / (1.0 - e))
        p.append(circle(x, y, 5, fill="#ffffff", stroke=POS, sw=2.2))
        p.append(text(x - 12, y - 12, cap, size=11.5, color=POS, anchor="end"))

    render(os.path.join(OUT, "window-price.svg"), W, H, *p)


fig_stall_timeline()
fig_window_anatomy()
fig_decision()
fig_lineage()
fig_counters()
fig_window_efficiency()
fig_ramp_sum()
fig_window_price()
print("ok")
