# -*- coding: utf-8 -*-
"""Фігури до кроку «Причинність важливіша за настінний час»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

A_FILL = "#dfe9fb"      # актор A / старіше
B_FILL = "#eafaf0"      # актор B / новіше
GRAY_FILL = "#f0f0f2"
RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
AMBER = "#fff8e6"


def fig_happens_before():
    """Дві доріжки акторів, повідомлення між ними: де є ланцюжок передування,
    а де пара конкурентна (порядку немає)."""
    W, H = 1180, 560
    frags = []

    YA, YB = 205, 415
    # події акторів (x-координати добрані так, щоб підписи не наповзали)
    a1, a2, a3 = 300, 620, 940
    b1, b2 = 460, 780
    R = 9

    # ── доріжки й підписи акторів ──
    frags.append(text(96, YA + 5, "Актор A", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(96, YA + 24, "(телефон)", size=12, color=MUTED, anchor="start"))
    frags.append(text(96, YB + 5, "Актор B", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(96, YB + 24, "(хаб)", size=12, color=MUTED, anchor="start"))

    # ── стрілки власного порядку кожного актора (зелені: «передує») ──
    frags.append(arrow(a1 + R + 4, YA, a2 - R - 4, YA, color=FIELD, sw=2.0))
    frags.append(arrow(a2 + R + 4, YA, a3 - R - 4, YA, color=FIELD, sw=2.0))
    frags.append(arrow(b1 + R + 4, YB, b2 - R - 4, YB, color=FIELD, sw=2.0))

    # ── повідомлення між акторами (сірі суцільні) ──
    frags.append(arrow(a1 + 6, YA + R, b1 - 6, YB - R, color=INK, sw=1.9))
    frags.append(arrow(b2 - 6, YB - R, a3 + 6, YA + R, color=INK, sw=1.9))
    frags.append(text(352, 312, "повідомлення", size=11, italic=True, color=MUTED, anchor="middle"))
    frags.append(text(892, 312, "повідомлення", size=11, italic=True, color=MUTED, anchor="middle"))

    # ── конкурентна пара a2 ∥ b1 (червона штрихована, збоку від решти) ──
    frags.append(line(a2 - 4, YA + R, b1 + 8, YB - R, color=POS, sw=1.8, dash="7,6"))
    frags.append(text(578, 318, "∦", size=22, bold=True, color=POS, anchor="middle"))

    # ── вузли-події (кола) з підписами: A — над доріжкою, B — під доріжкою ──
    def node(x, y, above, label, fill, stroke):
        out = [circle(x, y, R, fill=fill, stroke=stroke, sw=2)]
        ly = y - 22 if above else y + 34
        out.append(text(x, ly, label, size=12.5, color=INK, anchor="middle"))
        return out

    for f in node(a1, YA, True, "правка сцени", A_FILL, NEG): frags.append(f)
    for f in node(a2, YA, True, "гортання історії", A_FILL, NEG): frags.append(f)
    for f in node(a3, YA, True, "бачить підтвердження", A_FILL, NEG): frags.append(f)
    for f in node(b1, YB, False, "хаб застосував", B_FILL, FIELD): frags.append(f)
    for f in node(b2, YB, False, "надіслав стан", B_FILL, FIELD): frags.append(f)

    # ── легенда (унизу ліворуч, у чистій зоні) ──
    ly = 512
    frags.append(line(96, ly, 138, ly, color=FIELD, sw=2.2))
    frags.append(text(146, ly + 5, "→ передує (могла вплинути)", size=12.5, color=INK, anchor="start"))
    frags.append(line(470, ly, 512, ly, color=POS, sw=1.8, dash="7,6"))
    frags.append(text(520, ly + 5, "∦ конкурентні (не могла) — істинного порядку немає",
                      size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "happens-before-vs-concurrent.svg"), W, H, *frags,
           title="Що передує чому — і що просто конкурентне")


def fig_lww_loses():
    """Дві правки з розсинхронізованими годинниками: за штампом часу — губимо справжню
    пізнішу; за причинністю — зберігаємо правильно."""
    W, H = 1180, 560
    frags = []

    S1X, RX = 470, 960
    S1W, RW = 380, 230

    # ── вхід: однакові дві правки для обох доріжок ──
    frags.append(text(W / 2, 78,
                      "Дві правки сцени «вечір»:  A о 20:00:10 (годинник +4с → штамп 14),  B о 20:00:12 (штамп 12)",
                      size=14, bold=True, color=INK))
    frags.append(text(W / 2, 100, "B справді пізніша за A на дві секунди", size=12.5, color=MUTED))

    def lane(y, header, hcolor, step, result, res_fill, res_stroke, res_color):
        frags.append(text(96, y - 62, header, size=15, bold=True, color=hcolor, anchor="start"))
        s, _, _ = textbox(S1X, y, step, size=13, fill=BG, stroke=LINE, min_w=S1W)
        rb, _, _ = textbox(RX, y, result, size=14, bold=True, fill=res_fill,
                           stroke=res_stroke, color=res_color, sw=2, min_w=RW)
        frags.append(arrow(S1X + S1W / 2 + 8, y, RX - RW / 2 - 8, y, color=res_stroke, sw=1.9))
        frags.append(s)
        frags.append(rb)

    lane(210, "Вирішує за ШТАМПОМ ЧАСУ  (last-write-wins)", POS,
         "порівнює штампи:\n14  проти  12\n→ лишає A (14 більше)",
         "результат: стан A\nсправжню зміну B\nВИКИНУТО — БРЕХНЯ",
         RED_FILL, POS, POS)

    frags.append(line(70, 320, 1110, 320, color=MUTED, sw=1, dash="6,6"))

    lane(430, "Вирішує за ПРИЧИННІСТЮ", FIELD,
         "версія одного господаря\nабо векторний годинник:\nбачить, що новіше / конкурентне",
         "результат: правильний стан\nконкурентні — обидві,\nа не тихий програш — ПРАВДА",
         GREEN_FILL, FIELD, FIELD)

    frags.append(text(W / 2, 528,
                      "Вхід однаковий — різне лише правило рішення. Штамп двох годинників бреше про порядок; причинний порядок — ні.",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "lww-loses-write.svg"), W, H, *frags,
           title="«Виграє останній за годинником» тихо губить запис")


def fig_time_ladder():
    """Драбина стратегій часу: від дешевого-брехливого настінного до дорогого-надійного
    TrueTime. Що нижче — надійніший порядок і вища ціна."""
    W, H = 1220, 580
    frags = []

    X0 = 150
    CN, CG, CC = 300, 380, 360      # ширини колонок: назва / дає / коштує
    XG, XC = X0 + CN, X0 + CN + CG

    # ── стрілка «нижче — надійніше й дорожче» (ліворуч) ──
    frags.append(arrow(96, 150, 96, 520, color=MUTED, sw=2.2))
    frags.append(text(80, 335, "надійніший порядок · дорожче", size=12, color=MUTED, anchor="middle"))
    # повернути підпис вертикально
    frags[-1] = ('<text x="80" y="335" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 80 335)">'
                 'надійніший фізичний порядок · дорожче</text>' % (FONT, MUTED))

    # ── шапка ──
    frags.append(fitbox(X0, 90, CN, 44, "стратегія часу", size=14, bold=True, fill=GRAY_FILL, stroke=LINE))
    frags.append(fitbox(XG, 90, CG, 44, "що дає", size=14, bold=True, fill=GRAY_FILL, stroke=LINE))
    frags.append(fitbox(XC, 90, CC, 44, "чим платиш", size=14, bold=True, fill=GRAY_FILL, stroke=LINE))

    rows = [
        ("Настінний час", RED_FILL, POS,
         "показати людині; дешево",
         "БРЕШЕ про порядок між машинами"),
        ("Годинник Лампорта", A_FILL, NEG,
         "повний порядок, згідний із причинністю",
         "не бачить, що дві події конкурентні"),
        ("Векторний годинник", A_FILL, NEG,
         "точно: причинне чи конкурентне",
         "росте з числом акторів"),
        ("HLC (гібридний)", GREEN_FILL, FIELD,
         "виглядає як фізичний час І тримає причинність",
         "майже задарма; не істинний фізичний"),
        ("TrueTime (Spanner)", GREEN_FILL, FIELD,
         "справжній фізичний порядок, вузька невизначеність",
         "атомні годинники + очікування на коміті"),
    ]
    y0, dy, h = 150, 74, 62
    for i, (name, nfill, ncol, gives, costs) in enumerate(rows):
        y = y0 + i * dy
        frags.append(fitbox(X0, y, CN, h, name, size=14, bold=True, fill=nfill, stroke=ncol, color=ncol))
        frags.append(fitbox(XG, y, CG, h, gives, size=13, fill=BG, stroke=LINE))
        frags.append(fitbox(XC, y, CC, h, costs, size=13, fill=BG, stroke=LINE))

    frags.append(text(W / 2, 552,
                      "Фізичний порядок між машинами не безкоштовний — його докуповують рівно там і стільки, скільки треба. Решту впорядковують причинністю.",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "time-strategies-ladder.svg"), W, H, *frags,
           title="Драбина стратегій часу: від дешевої брехні до дорогої правди")


def fig_minkowski_bridge():
    """Ізоморфізм причинності: конус світла Мінковського (ліворуч) і передування
    в розподіленій системі (праворуч). Один і той самий скелет: сигнал ↔ повідомлення,
    простороподібно розділені ↔ конкурентні."""
    W, H = 1240, 660
    frags = []

    # ── роздільник панелей ──
    frags.append(line(608, 92, 608, 556, color=MUTED, sw=1, dash="5,7"))

    # ═══ ЛІВА ПАНЕЛЬ: простір-час Мінковського ═══
    OX, OY = 340, 340
    TIP = 200                      # довжина сторони конуса
    frags.append(text(340, 74, "Простір-час Мінковського (1908)", size=15, bold=True, color=INK))

    # заливка конусів (майбутнє / минуле)
    fut = "%d,%d %d,%d %d,%d" % (OX, OY, OX - TIP, OY - TIP, OX + TIP, OY - TIP)
    pst = "%d,%d %d,%d %d,%d" % (OX, OY, OX - TIP, OY + TIP, OX + TIP, OY + TIP)
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.55"/>' % (fut, A_FILL))
    frags.append('<polygon points="%s" fill="%s" fill-opacity="0.55"/>' % (pst, A_FILL))

    # осі
    frags.append(line(150, OY, 530, OY, color=MUTED, sw=1.2))          # простір
    frags.append(line(OX, 128, OX, 552, color=MUTED, sw=1.2))          # час
    frags.append(text(OX, 118, "час", size=12, color=MUTED))
    frags.append(text(546, OY + 4, "простір", size=12, color=MUTED, anchor="start"))

    # лінії конуса світла (діагоналі 45°)
    frags.append(line(OX, OY, OX - TIP, OY - TIP, color=POS, sw=2.2))
    frags.append(line(OX, OY, OX + TIP, OY - TIP, color=POS, sw=2.2))
    frags.append(line(OX, OY, OX - TIP, OY + TIP, color=POS, sw=2.2))
    frags.append(line(OX, OY, OX + TIP, OY + TIP, color=POS, sw=2.2))

    # подія-опора О
    frags.append(circle(OX, OY, 6, fill=BG, stroke=INK, sw=2))
    frags.append(text(OX - 12, OY + 20, "О", size=13, bold=True, color=INK, anchor="end"))

    # підписи областей
    frags.append(text(OX, 206, "МАЙБУТНЄ О", size=13, bold=True, color=NEG))
    frags.append(text(OX, 226, "О може вплинути", size=12, color=MUTED))
    frags.append(text(OX, 452, "МИНУЛЕ О", size=13, bold=True, color=NEG))
    frags.append(text(OX, 472, "впливає на О", size=12, color=MUTED))

    # простороподібні («деінде») — праворуч із поясненням, ліворуч коротко
    frags.append(text(468, 322, "ДЕІНДЕ", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(468, 360, "простороподібно —", size=12, color=MUTED, anchor="start"))
    frags.append(text(468, 378, "порядок відносний", size=12, color=MUTED, anchor="start"))
    frags.append(text(212, 322, "ДЕІНДЕ", size=13, bold=True, color=FIELD, anchor="end"))

    frags.append(text(340, 578, "діагональ = промінь світла: гранична швидкість причинності",
                      size=12, italic=True, color=MUTED))

    # ═══ ПРАВА ПАНЕЛЬ: розподілена система ═══
    frags.append(text(910, 74, "Розподілена система (Лампорт, 1978)", size=15, bold=True, color=INK))

    PY, QY = 250, 440
    frags.append(text(668, PY - 22, "процес P", size=13, bold=True, color=INK, anchor="start"))
    frags.append(text(668, QY + 30, "процес Q", size=13, bold=True, color=INK, anchor="start"))

    p1, p2, p3 = 748, 936, 1104
    q1, q2 = 842, 1028
    R = 8

    # доріжки процесів (зелені стрілки власного порядку — передування)
    frags.append(arrow(p1 + R + 4, PY, p2 - R - 4, PY, color=FIELD, sw=2.0))
    frags.append(arrow(p2 + R + 4, PY, p3 - R - 4, PY, color=FIELD, sw=2.0))
    frags.append(arrow(q1 + R + 4, QY, q2 - R - 4, QY, color=FIELD, sw=2.0))

    # повідомлення (сірі — як «світло»): p1→q1, q2→p3
    frags.append(arrow(p1 + 6, PY + R, q1 - 6, QY - R, color=INK, sw=1.9))
    frags.append(arrow(q2 - 6, QY - R, p3 + 6, PY + R, color=INK, sw=1.9))
    frags.append(text(756, 352, "повідомлення", size=11, italic=True, color=MUTED, anchor="start"))
    frags.append(text(1108, 352, "= «світло»", size=11, italic=True, color=MUTED, anchor="end"))

    # конкурентна пара p2 ∥ q1 (червона штрихована — простороподібно)
    frags.append(line(p2 - 6, PY + R, q1 + 6, QY - R, color=POS, sw=1.8, dash="7,6"))
    frags.append(text(958, 356, "p₂ ∥ q₁ —", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(958, 374, "конкурентні", size=12, color=POS, anchor="start"))

    # вузли-події
    for x, lbl in [(p1, "p₁"), (p2, "p₂"), (p3, "p₃")]:
        frags.append(circle(x, PY, R, fill=B_FILL, stroke=FIELD, sw=2))
        frags.append(text(x, PY - 18, lbl, size=13, color=INK))
    for x, lbl in [(q1, "q₁"), (q2, "q₂")]:
        frags.append(circle(x, QY, R, fill=B_FILL, stroke=FIELD, sw=2))
        frags.append(text(x, QY + 30, lbl, size=13, color=INK))

    frags.append(text(910, 578,
                      "ланцюг p₁→q₁→q₂→p₃ = передування · червона пара = конкурентні",
                      size=12, italic=True, color=MUTED))

    # ═══ смуга відповідності (унизу, на всю ширину) ═══
    frags.append(mtext(W / 2, 616, [
        "Відповідність точна, не метафора:",
        "ланцюг повідомлень ↔ конус світла   ·   конкурентні ↔ простороподібно розділені   ·   швидкість повідомлень ↔ швидкість світла",
    ], size=12.5, color=INK, lh=1.4))

    render(os.path.join(IMG, "minkowski-happens-before-bridge.svg"), W, H, *frags,
           title="Один і той самий скелет причинності: конус світла ↔ передування")


def fig_hlc_trace():
    """Слід подій одного вузла: як пара (l, c) тримає монотонність, поглинає крок
    годинника назад і чому нічия «фізичний == l» цокає лічильник, а не скидає його."""
    W, H = 1260, 600
    frags = []

    X0 = 50
    widths = [100, 140, 140, 120, 150, 500]
    xs = [X0]
    for w in widths:
        xs.append(xs[-1] + w)   # xs[-1] = 1200

    heads = ["подія", "pt (фізичний)", "l (фіз. частина)", "c (лічильник)",
             "мітка  l·c", "що сталося"]
    hy, hh = 92, 46
    for i, htext in enumerate(heads):
        frags.append(fitbox(xs[i], hy, widths[i], hh, htext, size=13.5, bold=True,
                            fill=GRAY_FILL, stroke=LINE))

    rows = [
        ("e1", "10", "10", "0", "10·0", "перша подія — фізичний веде, лічильник з нуля", BG),
        ("e2", "10", "10", "1", "10·1", "той самий такт (10) — l не зрушив, лічильник цокає", BG),
        ("e3", "10", "10", "2", "10·2", "ще подія в тому ж такті — знову цок", BG),
        ("e4", "13", "13", "0", "13·0", "фізичний зрушив уперед (13) — лічильник скинуто", BG),
        ("e5", "11", "13", "1", "13·1", "NTP смикнув годинник НАЗАД (11) — мітка все одно вперед", AMBER),
        ("e6", "13", "13", "2", "13·2", "фізичний рівно наздогнав l (13) — цок, НЕ скидання", AMBER),
        ("e7", "14", "14", "0", "14·0", "фізичний обігнав l (14) — аж тепер скидання", BG),
    ]
    ry, rh, dy = 138, 50, 58
    for r, (ev, pt, l, c, st, cm, cmfill) in enumerate(rows):
        y = ry + r * dy
        frags.append(fitbox(xs[0], y, widths[0], rh, ev, size=13, bold=True, fill=BG, stroke=LINE))
        frags.append(fitbox(xs[1], y, widths[1], rh, pt, size=14, fill=BG, stroke=LINE))
        frags.append(fitbox(xs[2], y, widths[2], rh, l, size=14, fill=BG, stroke=LINE))
        frags.append(fitbox(xs[3], y, widths[3], rh, c, size=14, fill=BG, stroke=LINE))
        frags.append(fitbox(xs[4], y, widths[4], rh, st, size=14, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, color=INK))
        frags.append(fitbox(xs[5], y, widths[5], rh, cm, size=12.5, fill=cmfill, stroke=LINE))

    frags.append(text(W / 2, ry + 7 * dy + 8,
                      "Стовпчик мітки лишень зростає:  10·0 < 10·1 < 10·2 < 13·0 < 13·1 < 13·2 < 14·0  — назад ніколи.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "hlc-trace.svg"), W, H, *frags,
           title="Слід HLC одного вузла: мітка не йде назад, хоч годинник смикається")


def fig_hlc_message():
    """Повідомлення між вузлами: max на прийомі підтягує відсталий годинник приймача
    вперед, тож мітка отримання строго пізніша за відправлення — причинність збережено."""
    W, H = 1200, 560
    frags = []

    YA, YB = 150, 330
    R = 10

    frags.append(text(70, YA + 5, "Вузол A", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(70, YA + 23, "годинник = 20", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(70, YB + 5, "Вузол B", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(70, YB + 23, "годинник ВІДСТАЄ = 17", size=11.5, color=POS, anchor="start"))

    aE, aS = 320, 620
    bPrev, bR = 320, 820

    frags.append(arrow(aE + R + 4, YA, aS - R - 4, YA, color=FIELD, sw=2.0))
    frags.append(arrow(bPrev + R + 4, YB, bR - R - 4, YB, color=FIELD, sw=2.0))
    frags.append(arrow(aS + 6, YA + R, bR - 8, YB - R, color=INK, sw=2.0))
    frags.append(text(700, 300, "повідомлення", size=12,
                      italic=True, color=MUTED, anchor="middle"))

    def node(x, y, above, label, fill, stroke):
        out = [circle(x, y, R, fill=fill, stroke=stroke, sw=2)]
        ly = y - 36 if above else y + 26
        out.append(mtext(x, ly, label, size=12.5, color=INK))
        return out

    for f in node(aE, YA, True, "локальна подія\n20·0", A_FILL, NEG): frags.append(f)
    for f in node(aS, YA, True, "надсилає\n20·0", A_FILL, NEG): frags.append(f)
    for f in node(bPrev, YB, False, "мала подія\nl = 16", B_FILL, FIELD): frags.append(f)
    for f in node(bR, YB, False, "отримує\n20·1", B_FILL, FIELD): frags.append(f)

    box, _, _ = textbox(600, 475,
        "На прийомі:  l = max( l_B = 16 ,  l_отр = 20 ,  pt_B = 17 ) = 20\n"
        "l збіглося з отриманим  →  c = c_отр + 1 = 1\n"
        "мітка отримання  20·1   >   мітка відправлення  20·0",
        size=13, fill=AMBER, stroke=FIELD, sw=1.8, min_w=780)
    frags.append(box)

    render(os.path.join(IMG, "hlc-message.svg"), W, H, *frags,
           title="Причинність через кордон машини: max підтягує відсталий приймач")


def fig_hlc_bits():
    """Як пара (l, c) лягає в одне 64-бітове число: старші 48 бітів — фізичний час,
    молодші 16 — лічильник; порівняння стає звичайним цілочисловим."""
    W, H = 1120, 340
    frags = []

    bx, by, bw, bh = 110, 120, 900, 76
    split = bx + bw * 48 / 64      # 785

    frags.append(fitbox(bx, by, split - bx, bh,
                        "фізичний час  l\n(старші 48 бітів)", size=15, bold=True,
                        fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(split, by, bx + bw - split, bh,
                        "c\n16 біт", size=13, bold=True, fill=AMBER, stroke=POS))

    frags.append(text((bx + split) / 2, by + bh + 24, "≈ мілісекунди настінного часу",
                      size=12.5, color=MUTED))
    frags.append(text((split + bx + bw) / 2, by + bh + 24, "0 … 65535", size=12.5, color=MUTED))
    frags.append(text(bx, by - 14, "біт 63", size=11, color=MUTED, anchor="start"))
    frags.append(text(bx + bw, by - 14, "біт 0", size=11, color=MUTED, anchor="end"))

    frags.append(text(W / 2, 252,
                      "pack = (l ≪ 16) | c   →   одне 64-бітове число; порядок = звичайне порівняння uint64",
                      size=13.5, bold=True, color=INK))
    frags.append(text(W / 2, 288,
                      "Пакування різне: MongoDB clusterTime — 32 + 32 біти; CockroachDB тримає wall (int64) і logical (int32) окремо.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "hlc-bits.svg"), W, H, *frags,
           title="Дві частини — одне число")


if __name__ == "__main__":
    fig_happens_before()
    fig_lww_loses()
    fig_time_ladder()
    fig_minkowski_bridge()
    fig_hlc_trace()
    fig_hlc_message()
    fig_hlc_bits()
    print("OK: happens-before-vs-concurrent.svg, lww-loses-write.svg, time-strategies-ladder.svg, minkowski-happens-before-bridge.svg,")
    print("    hlc-trace.svg, hlc-message.svg, hlc-bits.svg")
