# -*- coding: utf-8 -*-
"""Фігури до теми «Вимірювання струму мотора».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def sw(cx, cy, on=False, label=""):
    """Спрощений значок ключа (MOSFET): квадрат, зелений якщо відкритий."""
    w = 30
    fill = "#e8f7ee" if on else FILL
    stroke = FIELD if on else LINE
    out = rect(cx - w / 2, cy - w / 2, w, w, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 4, "вкл" if on else "вим", size=10,
                color=FIELD if on else MUTED, bold=on)
    if label:
        out += text(cx, cy - w / 2 - 6, label, size=10, color=MUTED)
    return out


def shunt(x0, y0, x1, y1, label="Rш", col=POS):
    """Прямокутник-шунт на відрізку (горизонтальний або вертикальний)."""
    out = ""
    if abs(x1 - x0) >= abs(y1 - y0):     # горизонтальний
        cx = (x0 + x1) / 2
        out += line(x0, y0, cx - 16, y0, color=LINE, sw=2)
        out += rect(cx - 16, y0 - 8, 32, 16, fill="#fdecea", stroke=col, sw=2)
        out += line(cx + 16, y0, x1, y1, color=LINE, sw=2)
        out += text(cx, y0 - 14, label, size=12, color=col, bold=True)
    else:                                # вертикальний
        cy = (y0 + y1) / 2
        out += line(x0, y0, x0, cy - 16, color=LINE, sw=2)
        out += rect(x0 - 8, cy - 16, 16, 32, fill="#fdecea", stroke=col, sw=2)
        out += line(x0, cy + 16, x1, y1, color=LINE, sw=2)
        out += text(x0 + 14, cy + 4, label, size=12, color=col, bold=True, anchor="start")
    return out


# ── 1. Три місця для шунта в мостовому драйвері ──────────────────────────────
def fig_where():
    W, H = 760, 430
    f = [text(W / 2, 26, "Три місця, куди врізають шунт у драйвері мотора", size=16, bold=True)]

    def leg(x0, y0, title, desc, col):
        out = [text(x0, y0, title, size=12, bold=True, color=col, anchor="start")]
        nlines = desc.count("\n") + 1
        out.append(fitbox(x0, y0 + 8, 300, 18 + nlines * 15, desc, size=11, color=MUTED,
                          stroke=col, fill="#ffffff"))
        return out

    # спільна рамка півмоста ліворуч
    topY, botY = 92, 300
    lX, rX = 150, 330
    # шини
    f.append(line(110, topY, 380, topY, color=POS, sw=2.4))
    f.append(plus(110, topY, 10))
    f.append(text(140, topY - 8, "+V батареї", size=12, color=POS, bold=True, anchor="start"))
    f.append(line(110, botY, 380, botY, color=NEG, sw=2.4))
    f.append(minus(110, botY, 10))
    f.append(text(140, botY + 20, "земля", size=12, color=NEG, bold=True, anchor="start"))

    # два півмости (фаза A і фаза B), мотор між середніми точками
    midY = (topY + botY) / 2
    for X, ph in ((lX, "A"), (rX, "B")):
        f.append(sw(X, topY + 40, on=(X == lX), label="верх " + ph))
        f.append(sw(X, botY - 40, on=(X == rX), label="низ " + ph))
        f.append(line(X, topY, X, topY + 25, color=LINE, sw=1.8))
        f.append(line(X, topY + 55, X, midY, color=LINE, sw=1.8))
        f.append(line(X, botY - 55, X, midY, color=LINE, sw=1.8))
    # мотор
    f.append(line(lX, midY, 214, midY, color=LINE, sw=1.8))
    f.append(line(rX, midY, 266, midY, color=LINE, sw=1.8))
    f.append(circle(240, midY, 24, fill="#eef2f7", stroke=LINE, sw=2))
    f.append(text(240, midY + 5, "M", size=16, bold=True))

    # (1) high-side / DC-link — у плюсовому проводі
    f.append(shunt(110 + 30, topY, 148, topY, label="1", col=POS))
    f.append(text(90, topY - 26, "1", size=15, bold=True, color=POS))

    # (2) low-side per-phase — під нижнім ключем фази B, в окремому проводі до землі
    f.append(line(rX, botY - 25, rX, botY - 18, color=LINE, sw=1.8))
    f.append(rect(rX - 8, botY - 18, 16, 26, fill="#fdecea", stroke=FIELD, sw=2))
    f.append(line(rX, botY + 8, rX, botY, color=LINE, sw=1.8))
    f.append(text(rX + 16, botY - 6, "2", size=13, bold=True, color=FIELD, anchor="start"))

    # (3) inline — у самому проводі до мотора (фаза A)
    f.append(rect((lX + 214) / 2 - 8, midY - 22, 16, 12, fill="#fdecea", stroke=NEG, sw=2))
    f.append(line((lX + 214) / 2, midY, (lX + 214) / 2, midY - 10, color=NEG, sw=1.6))
    f.append(text((lX + 214) / 2, midY - 28, "3", size=13, bold=True, color=NEG))

    # легенда праворуч
    f += leg(430, 90, "1  Ланка постійного струму (DC-link)",
             "У плюсовому проводі до всього моста.\nОдин шунт бачить сумарний струм —\nале не окрему фазу без реконструкції.", POS)
    f += leg(430, 195, "2  Низька сторона фази (low-side)",
             "Під нижнім ключем плеча, у проводі\nдо землі. Дешево й просто, але видно\nструм лише поки нижній ключ відкритий.", FIELD)
    f += leg(430, 300, "3  У розрив фази (inline)",
             "Прямо у проводі до обмотки. Бачить\nсправжній струм фази щомиті, та висить\nна комутованій напрузі — дорогий підсилювач.", NEG)

    f.append(text(W / 2, 418, "Місце шунта визначає, ЩО ви бачите й ЯК складно це підсилити — це головний вибір теми",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "where-shunt.svg"), W, H, *f)


# ── 2. Пиляста форма струму й точка відліку ─────────────────────────────────
def fig_sampling():
    W, H = 760, 400
    f = [text(W / 2, 26, "Струм у моторі — пиляста хвиля; важить, КОЛИ взяти відлік", size=16, bold=True)]

    x0, x1 = 90, 690
    topY, midY, botY = 70, 150, 300     # midY — середній струм; ripple навколо нього
    # осі
    f.append(line(x0, botY, x1, botY, color=MUTED, sw=1))
    f.append(text(x0 - 6, botY + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 6, midY + 4, "I_сер", size=11, color=POS, anchor="end"))
    f.append(line(x0, midY, x1, midY, color=POS, sw=1.6, dash="6 5"))

    # ── верхня доріжка: ШІМ нижнього ключа (коли шунт «бачить» струм) ──
    pwmBase, pwmTop = 355, 320
    f.append(text(x0 - 6, 338, "ключ", size=11, color=MUTED, anchor="end"))
    period = (x1 - x0) / 4.0
    duty = 0.55
    for k in range(4):
        xs = x0 + k * period
        on_w = period * duty
        f.append(line(xs, pwmBase, xs, pwmTop, color=INK, sw=1.8))
        f.append(line(xs, pwmTop, xs + on_w, pwmTop, color=INK, sw=1.8))
        f.append(line(xs + on_w, pwmTop, xs + on_w, pwmBase, color=INK, sw=1.8))
        f.append(line(xs + on_w, pwmBase, xs + period, pwmBase, color=INK, sw=1.8))
        f.append(text(xs + on_w / 2, pwmTop - 4, "вкл", size=9, color=FIELD, anchor="middle"))

    # ── пиляста хвиля струму: росте при «вкл», спадає при «вим» ──
    amp = 42
    pts = []
    for k in range(4):
        xs = x0 + k * period
        on_w = period * duty
        # у сегменті «вкл» струм зростає від (mid-amp) до (mid+amp)? спрощено — трикутник навколо mid
        pts.append((xs, midY + amp))
        pts.append((xs + on_w, midY - amp))
        pts.append((xs + period, midY + amp))
    d = "M%.1f %.1f" % pts[0] + "".join(" L%.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    f.append(text(x1 + 6, midY - amp, "пік", size=10, color=NEG, anchor="start"))
    f.append(text(x1 + 6, midY + amp + 4, "дно", size=10, color=NEG, anchor="start"))

    # точка правильного відліку — у середині сегмента «вкл» (там струм = середній)
    for k in range(4):
        xs = x0 + k * period
        xm = xs + period * duty / 2.0      # центр увімкненого вікна
        f.append(circle(xm, midY, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text((x0 + period * duty / 2.0), midY - 16, "● відлік у центрі імпульсу",
                  size=11, color=FIELD, bold=True, anchor="start"))

    # «сліпий» вузький імпульс праворуч зверху — підпис
    f.append(fitbox(x0, 360, 300, 30,
                    "Відлік по центру «вкл» ловить СЕРЕДНІЙ струм, а не пік/дно пульсації",
                    size=11, color=FIELD, stroke=FIELD, fill="#ffffff"))
    f.append(fitbox(x0 + 315, 360, 300, 30,
                    "Відлік не в центрі — зчитаєш випадкову точку пилки: похибка з нічого",
                    size=11, color=POS, stroke=POS, fill="#ffffff"))
    render(os.path.join(IMG, "sampling.svg"), W, H, *f)


# ── 3. Один шунт у DC-link: різні фази у різних вікнах + сліпа зона ──────────
def fig_single_shunt():
    W, H = 760, 380
    f = [text(W / 2, 26, "Один шунт у ланці постійного струму бачить фази ПО ЧЕРЗІ", size=16, bold=True)]

    x0, x1 = 90, 690
    baseY = 250
    f.append(line(x0, baseY, x1, baseY, color=MUTED, sw=1))
    f.append(text(x0 - 6, baseY + 4, "0", size=11, color=MUTED, anchor="end"))

    # період ШІМ поділено на вікна векторів; у різних вікнах через шунт тече різний фазний струм
    seg = (x1 - x0) / 7.0
    labels = ["0", "+i_A", "−i_C", "0", "−i_C", "+i_A", "0"]
    heights = [0, 70, 40, 0, 40, 70, 0]
    cols =    [MUTED, POS, NEG, MUTED, NEG, POS, MUTED]
    for k in range(7):
        xs = x0 + k * seg
        h = heights[k]
        c = cols[k]
        if h > 0:
            f.append(rect(xs + 4, baseY - h, seg - 8, h, fill="#f4f6f8", stroke=c, sw=1.8))
            f.append(text(xs + seg / 2, baseY - h - 6, labels[k], size=11, color=c, bold=True))
            f.append(text(xs + seg / 2, baseY - h / 2 + 4, "✓", size=13, color=FIELD, bold=True))
        else:
            f.append(text(xs + seg / 2, baseY - 10, "0", size=11, color=MUTED))

    f.append(text(x0, baseY + 26, "струм у шунті за один період ШІМ", size=11, color=MUTED, anchor="start"))
    f.append(fitbox(x0, baseY + 40, 600, 30,
                    "Два активні вікна за період дають два фазні струми (i_A та i_C); третій — із правила i_A+i_B+i_C=0",
                    size=11, color=INK, stroke=LINE, fill="#ffffff"))

    # сліпа зона: вузьке вікно, коли фронти зійшлися
    f.append(text(x0, 320, "Коли шпаруватості близькі, активне вікно коротшає за час на відлік →",
                  size=11, color=POS, anchor="start"))
    f.append(text(x0, 340, "струм не встигає «показатися»: сліпа зона, потрібне зсування фронтів ШІМ.",
                  size=11, color=POS, anchor="start"))
    render(os.path.join(IMG, "single-shunt.svg"), W, H, *f)


# ── 4. Пусковий струм диктує крихітний шунт ─────────────────────────────────
def fig_stall():
    W, H = 720, 340
    f = [text(W / 2, 26, "Мотор диктує малий шунт: пусковий струм у рази більший за робочий", size=16, bold=True)]

    # дві шкали струму
    f.append(text(150, 80, "Робочий струм", size=13, bold=True))
    f.append(rect(70, 96, 90, 26, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(115, 114, "2 A", size=12, color="#ffffff", bold=True))

    f.append(text(430, 80, "Пусковий (застряг ротор)", size=13, bold=True))
    f.append(rect(300, 96, 360, 26, fill=POS, stroke=POS, sw=1))
    f.append(text(480, 114, "20 A і більше", size=12, color="#ffffff", bold=True))

    # наслідок для шунта
    f.append(fitbox(70, 160, 280, 120,
                    "Шунт мусить пережити ПІК струму без перегріву й без насичення входу підсилювача.\n"
                    "P = I²·R гріє з квадратом струму — на піку в 10× тепло в 100×.",
                    size=12, color=INK, stroke=POS, fill="#ffffff"))
    f.append(fitbox(380, 160, 280, 120,
                    "Тому беруть шунт у міліомах: 5 мΩ при 20 A дає 100 мВ (влазить у вхід)\n"
                    "і 2 Вт тепла (терпимо), а при 2 A — лише 10 мВ і 20 мВт.",
                    size=12, color=INK, stroke=FIELD, fill="#ffffff"))

    f.append(text(W / 2, 315, "Опір шунта підбирають під ПІК, а не під робочий струм — інакше вхід «зашкалить» на пуску",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "stall-current.svg"), W, H, *f)


# ── 5. Стан ключів → яка фаза тече крізь шунт у вікні (вставка proj) ─────────
def fig_recon_windows():
    W, H = 780, 470
    f = [text(W / 2, 26, "Стан ключів визначає, яка фаза тече крізь шунт", size=16, bold=True)]

    x0, x1 = 150, 700
    T = x1 - x0
    # центрований період: половина «розкриття» до центру, половина назад.
    # три фази зі шпаруватостями dA>dB>dC (симетрично навколо центру)
    dA, dB, dC = 0.80, 0.50, 0.24
    def onspan(d):                     # інтервал «верхній ключ вкл» (центрований)
        half = d / 2.0
        return (0.5 - half) * T + x0, (0.5 + half) * T + x0
    Aa, Ab = onspan(dA)
    Ba, Bb = onspan(dB)
    Ca, Cb = onspan(dC)

    # три доріжки верхніх ключів A,B,C
    rowY = [70, 108, 146]
    rh = 22
    for (ya, name, (sa, sb), col) in ((rowY[0], "верх A", (Aa, Ab), POS),
                                      (rowY[1], "верх B", (Ba, Bb), FIELD),
                                      (rowY[2], "верх C", (Ca, Cb), NEG)):
        f.append(text(x0 - 12, ya + rh - 6, name, size=11, color=col, anchor="end", bold=True))
        f.append(line(x0, ya + rh, x1, ya + rh, color=MUTED, sw=1))          # рівень «вим»
        f.append(rect(sa, ya, sb - sa, rh, fill="#eef7f0" if col == FIELD else
                      ("#fdecea" if col == POS else "#eaf0fd"), stroke=col, sw=1.6))
        f.append(text((sa + sb) / 2, ya + rh - 6, "вкл", size=10, color=col, bold=True))

    # межі вікон (фронти) — вертикальні пунктири
    edges = sorted(set([Aa, Ab, Ba, Bb, Ca, Cb]))
    yTop, yBot = rowY[0] - 6, 300
    for e in edges:
        f.append(line(e, yTop, e, yBot, color=MUTED, sw=0.8, dash="3 4"))

    # доріжка струму шунта: сходинки за вікнами (від краю до центру)
    baseY, unit = 300, 26
    f.append(line(x0, baseY, x1, baseY, color=MUTED, sw=1))
    f.append(text(x0 - 12, baseY + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 12, baseY - 4, "i_шунта", size=11, color=INK, anchor="end", bold=True))

    # значення струму по інтервалах між фронтами (перша половина періоду):
    # [x0..Aa]:0(нуль-вектор V0) → [Aa..Ba]: тільки A вкл → i_A (+2u)
    # [Ba..Ca]: A,B вкл → тільки C вим → −i_C (+1u)
    # [Ca..центр..]: усі вкл → нуль-вектор V7 (0)
    center = x0 + T / 2
    segs = [(x0, Aa, 0, "V0", MUTED),
            (Aa, Ba, 2, "+i_A", POS),
            (Ba, Ca, 1, "−i_C", NEG),
            (Ca, center, 0, "V7", MUTED)]
    for (sa, sb, lvl, lbl, col) in segs:
        y = baseY - lvl * unit
        if lvl > 0:
            f.append(rect(sa, y, sb - sa, lvl * unit, fill="#f4f6f8", stroke=col, sw=1.8))
            f.append(text((sa + sb) / 2, y - 6, lbl, size=11, color=col, bold=True))
        else:
            f.append(text((sa + sb) / 2, baseY - 10, lbl, size=10, color=MUTED))

    # дві точки відліку — у центрі двох активних вікон
    s1 = (Aa + Ba) / 2.0
    s2 = (Ba + Ca) / 2.0
    for (xm, lvl, col) in ((s1, 2, POS), (s2, 1, NEG)):
        f.append(circle(xm, baseY - lvl * unit, 5, fill=INK, stroke="#ffffff", sw=1.4))
    f.append(text(s1, baseY - 2 * unit - 22, "відлік 1", size=10, color=INK, bold=True))
    f.append(text(s2, baseY - 1 * unit - 40, "відлік 2", size=10, color=INK, bold=True))

    f.append(line(center, yTop, center, baseY + 14, color=INK, sw=1.2, dash="5 4"))
    f.append(text(center, baseY + 28, "центр періоду (дзеркало)", size=10, color=MUTED))

    f.append(fitbox(x0, baseY + 44, T, 30,
                    "Два активні вікна дають +i_A та −i_C; третю фазу — з i_A + i_B + i_C = 0. "
                    "Вікно тим ширше, чим більша різниця сусідніх шпаруватостей.",
                    size=11, color=INK, stroke=LINE, fill="#ffffff"))
    f.append(fitbox(x0, baseY + 82, T, 62,
                    "Таблиця «активний вектор → фаза в шунті»: увімкнено рівно один верхній ключ → "
                    "струм = +тієї фази; вимкнено рівно один верхній → струм = −тієї фази.\n"
                    "Нуль-вектори (усі верхні вкл або всі вим) дають у шунті нуль — фаз не видно.",
                    size=11, color=INK, stroke=LINE, fill="#fbfbfb"))
    render(os.path.join(IMG, "recon-windows.svg"), W, H, *f)


# ── 6. Сліпа зона й розсування фронтів ШІМ ──────────────────────────────────
def fig_blind_shift():
    W, H = 780, 360
    f = [text(W / 2, 26, "Вузьке вікно → розсунути фронти ШІМ до вимірного", size=16, bold=True)]

    Tmin_w = 74           # ширина, що відповідає T_min (мінімальне вимірне вікно), px
    colBAD, colOK = POS, FIELD

    def scene(cx, title, gap, ok):
        out = [text(cx, 60, title, size=12, bold=True,
                    color=colOK if ok else colBAD)]
        x0 = cx - 150
        x1 = cx + 150
        yA, yB, rh = 90, 122, 20
        # верхні ключі A і B з майже рівними шпаруватостями (вузьке вікно між фронтами)
        Aa, Ab = x0 + 40, x1 - 30
        # фронт B зсунуто ліворуч на gap від фронта A → вікно завширшки gap
        Ba, Bb = x0 + 40 - gap, x1 - 30 - gap
        out.append(text(x0 - 6, yA + rh - 5, "A", size=11, color=INK, anchor="end", bold=True))
        out.append(rect(Aa, yA, Ab - Aa, rh, fill="#fdecea", stroke=POS, sw=1.5))
        out.append(text((Aa + Ab) / 2, yA + rh - 5, "вкл", size=9, color=POS))
        out.append(text(x0 - 6, yB + rh - 5, "B", size=11, color=INK, anchor="end", bold=True))
        out.append(rect(Ba, Bb - Ba, rh, 0, fill="none", stroke="none"))  # noop
        out.append(rect(Ba, yB, Bb - Ba, rh, fill="#eef7f0", stroke=FIELD, sw=1.5))
        out.append(text((Ba + Bb) / 2, yB + rh - 5, "вкл", size=9, color=FIELD))

        # вікно виміру = між лівими фронтами A і B (де тече рівно одна фаза)
        wx0, wx1 = min(Aa, Ba), max(Aa, Ba)
        wy0, wy1 = yA - 14, yB + rh + 14
        out.append(rect(wx0, wy0, max(wx1 - wx0, 2), wy1 - wy0, fill="none",
                        stroke=(colOK if ok else colBAD), sw=1.8, rx=3))
        out.append(text((wx0 + wx1) / 2, wy1 + 16, "вікно", size=10,
                        color=(colOK if ok else colBAD), bold=True))
        # позначка T_min для порівняння
        out.append(line(cx - Tmin_w / 2, wy1 + 34, cx + Tmin_w / 2, wy1 + 34,
                        color=MUTED, sw=1.4))
        out.append(line(cx - Tmin_w / 2, wy1 + 30, cx - Tmin_w / 2, wy1 + 38, color=MUTED, sw=1.4))
        out.append(line(cx + Tmin_w / 2, wy1 + 30, cx + Tmin_w / 2, wy1 + 38, color=MUTED, sw=1.4))
        out.append(text(cx, wy1 + 50, "T_min (бланкінг+відлік)", size=10, color=MUTED))
        return out

    f += scene(210, "Було: фронти зійшлися", 10, ok=False)
    f += scene(560, "Стало: фронт B зсунуто", Tmin_w + 8, ok=True)

    # стрілка переходу
    f.append(arrow(372, 150, 398, 150, color=INK, sw=2))

    f.append(fitbox(60, 300, 660, 46,
                    "Вузьке вікно (ліворуч) коротше за T_min — струм не встигає показатися, сліпа зона. "
                    "Зсуваємо один фронт (праворуч), доки вікно ≥ T_min. Сумарна ширина «вкл» не змінюється — "
                    "середня напруга фази ціла; спотворюється лише МИТТЄВА форма, тож ціна зсуву — крихітна пульсація.",
                    size=11, color=INK, stroke=LINE, fill="#ffffff"))
    render(os.path.join(IMG, "blind-shift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_where()
    fig_sampling()
    fig_single_shunt()
    fig_stall()
    fig_recon_windows()
    fig_blind_shift()
    print("Готово: 6 фігур у", IMG)
