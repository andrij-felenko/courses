# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Завзятий бобер (busy beaver)».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # вічний цикл / гаряче / голівка
BLUE  = "#2457d6"   # припущення / холодне
GREEN = "#27ae60"   # зупинка / прийом
AMBER = "#b9770e"
CTRL  = "#eef2fb"   # заливка коробки-машини
HEAD  = "#fff2c4"   # клітинка під голівкою


def cell(cx, top, s, w=46, h=46, fill=BG, stroke=INK, tcol=INK, size=18):
    """Клітинка стрічки з центром по x = cx, верхом top."""
    x = cx - w / 2
    out = rect(x, top, w, h, fill=fill, stroke=stroke, sw=1.6, rx=3)
    out += text(cx, top + h / 2 + size * 0.35, s, size=size, color=tcol, bold=True)
    return out


def head_tri(cx, cell_top, color=RED):
    """Трикутник-голівка вістрям донизу над клітинкою."""
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (cx - 9, cell_top - 22, cx + 9, cell_top - 22, cx, cell_top - 4, color))


# ── Фігура 1: постановка гри й розгалуження доль ─────────────────────────────
def fig_game():
    W, H = 1000, 470
    P = []

    # ліворуч: чиста стрічка + машина
    tape_y = 150
    txs = [70 + 46 * i for i in range(4)]
    P.append(text(txs[0] + 69, tape_y - 30, "чиста стрічка", size=12, color=MUTED))
    for cx in txs:
        P.append(cell(cx + 23, tape_y, "·", tcol=MUTED))
    P.append(text(txs[0] - 22, tape_y + 30, "…", size=20, color=MUTED))
    P.append(text(txs[3] + 68, tape_y - 30, "…", size=20, color=MUTED))

    mbox, mw, mh = textbox(360, tape_y + 23, "n-станова\nмашина\nТюринга", size=13,
                           fill=CTRL, stroke=NEG, color=INK, bold=True)
    P.append(arrow(txs[3] + 50, tape_y + 23, 360 - mw / 2 - 8, tape_y + 23, color=INK))
    P.append(mbox)

    # розгалуження: дві долі
    gx, gy = 660, 96
    rx, ry = 660, 250
    gbox, gw, gh = textbox(gx, gy, "ЗУПИНЯЄТЬСЯ\nрахуємо цю машину", size=13,
                           fill="#eafaf0", stroke=GREEN, color=INK, bold=True)
    rbox, rw, rh = textbox(rx, ry, "крутиться ВІЧНО\nне рахуємо", size=13,
                           fill="#fdecea", stroke=RED, color=INK, bold=True)
    P.append(arrow(360 + mw / 2 + 6, tape_y + 10, gx - gw / 2 - 8, gy + 14, color=GREEN))
    P.append(arrow(360 + mw / 2 + 6, tape_y + 36, rx - rw / 2 - 8, ry - 14, color=RED))
    P.append(gbox)
    P.append(rbox)

    # чемпіон
    cbox, cw, ch = textbox(890, gy, "ЧЕМПІОН\nнайбільше 1  → Σ(n)\nнайдовше     → S(n)",
                           size=12.5, fill=BG, stroke=GREEN, color=INK, bold=True)
    P.append(arrow(gx + gw / 2 + 6, gy, 890 - cw / 2 - 8, gy, color=GREEN))
    P.append(cbox)
    P.append(text(890, gy + ch / 2 + 24, "серед усіх, що спинились —", size=11.5, color=MUTED))
    P.append(text(890, gy + ch / 2 + 42, "найзавзятіший", size=11.5, color=MUTED))

    # нижній банер про скінченність
    nb, nbw, nbh = textbox(W / 2, 410,
                           "Машин зі станами скінченно — не більш як (4n+4)²ⁿ  "
                           "(для n=2 це 20 736).  Тож максимум існує.",
                           size=13, fill=FILL, stroke=INK, color=INK, bold=True)
    P.append(nb)
    render("img/game.svg", W, H,
           text(W / 2, 30, "Гра завзятого бобра: чемпіон серед машин, що спиняються", size=16, bold=True),
           *P)


# ── Фігура 2: хід двостанового чемпіона на стрічці ───────────────────────────
def fig_bb2_run():
    W, H = 840, 500
    P = [text(W / 2, 30, "Двостановий чемпіон: 4 одиниці за 6 кроків", size=16, bold=True)]
    # (стан, клітинки[-2..1], індекс голівки, дія)
    frames = [
        ("A", ["·", "·", "·", "·"], 2, "A,0 → пиши 1, R, до B"),
        ("B", ["·", "·", "1", "·"], 3, "B,0 → пиши 1, L, до A"),
        ("A", ["·", "·", "1", "1"], 2, "A,1 → пиши 1, L, до B"),
        ("B", ["·", "·", "1", "1"], 1, "B,0 → пиши 1, L, до A"),
        ("A", ["·", "1", "1", "1"], 0, "A,0 → пиши 1, R, до B"),
        ("B", ["1", "1", "1", "1"], 1, "B,1 → пиши 1, R, ЗУПИНКА"),
    ]
    xs = [300 + 50 * j for j in range(4)]      # центри клітинок
    y0, dy, ch = 78, 60, 46
    for i, (st, cells, hidx, act) in enumerate(frames):
        top = y0 + i * dy
        P.append(text(70, top + 30, "крок %d" % i, size=13, color=MUTED, anchor="start"))
        P.append(text(170, top + 30, st, size=17, color=INK, anchor="middle", bold=True))
        for j, (cx, s) in enumerate(zip(xs, cells)):
            hit = (j == hidx)
            P.append(cell(cx, top, s, w=50, h=ch,
                          fill=HEAD if hit else BG,
                          stroke=RED if hit else "#c9ced4",
                          tcol=(RED if hit else INK) if s == "1" else MUTED))
        P.append(head_tri(xs[hidx], top, RED))
        P.append(text(xs[3] + 55, top + 30, act, size=12.5, color=INK, anchor="start"))
    # підсумок
    ty = y0 + 6 * dy + 6
    P.append(text(W / 2, ty + 16, "на стрічці лишилось чотири одиниці — Σ(2) = 4,  S(2) = 6",
                  size=13.5, color=GREEN, bold=True))
    render("img/bb2-run.svg", W, H, *P)


# ── Фігура 3: вибух значень Σ і S ────────────────────────────────────────────
def fig_explosion():
    W, H = 860, 500
    P = [text(W / 2, 30, "Вибух завзятості: значення від 1 до 6 станів", size=16, bold=True)]

    rows = [
        ("1", "1", "1", INK),
        ("2", "4", "6", INK),
        ("3", "6", "21", INK),
        ("4", "13", "107", INK),
        ("5", "4098", "47 176 870", AMBER),
        ("6", "велетенське", "> 2↑↑↑5", RED),
    ]
    # таблиця
    x_n, x_sig, x_s = 110, 240, 430
    cw_n, cw_sig, cw_s = 90, 150, 230
    y0, rh = 78, 54
    # заголовок
    hdr = ["n", "Σ(n) — одиниць", "S(n) — кроків"]
    hx = [x_n, x_sig, x_s]
    hw = [cw_n, cw_sig, cw_s]
    for hxx, hww, lab in zip(hx, hw, hdr):
        P.append(rect(hxx, y0, hww, rh, fill=FILL, stroke=INK, sw=1.4, rx=4))
        P.append(text(hxx + hww / 2, y0 + rh / 2 + 5, lab, size=12.5, color=INK, bold=True))
    for i, (n, sig, s, col) in enumerate(rows):
        top = y0 + (i + 1) * rh
        fill = "#fdecea" if col == RED else ("#fdf3e3" if col == AMBER else BG)
        P.append(rect(x_n, top, cw_n, rh, fill=fill, stroke="#c9ced4", sw=1.2, rx=4))
        P.append(rect(x_sig, top, cw_sig, rh, fill=fill, stroke="#c9ced4", sw=1.2, rx=4))
        P.append(rect(x_s, top, cw_s, rh, fill=fill, stroke="#c9ced4", sw=1.2, rx=4))
        P.append(text(x_n + cw_n / 2, top + rh / 2 + 5, n, size=13, color=INK, bold=True))
        P.append(text(x_sig + cw_sig / 2, top + rh / 2 + 5, sig, size=13, color=col,
                      bold=(col != INK)))
        P.append(text(x_s + cw_s / 2, top + rh / 2 + 5, s, size=13, color=col,
                      bold=(col != INK)))

    # пояснення праворуч
    ex = x_s + cw_s + 40
    P.append(text(ex, y0 + 96, "↑↑  — вежа степенів (тетрація):", size=11.5, color=INK,
                  anchor="start", bold=True))
    P.append(text(ex, y0 + 116, "10↑↑15 = 15 поверхів десяток", size=11.5, color=MUTED,
                  anchor="start"))
    P.append(text(ex, y0 + 150, "↑↑↑ — ітерована тетрація", size=11.5, color=INK,
                  anchor="start", bold=True))
    P.append(text(ex, y0 + 170, "(пентація): поверх над", size=11.5, color=MUTED, anchor="start"))
    P.append(text(ex, y0 + 190, "поверхами", size=11.5, color=MUTED, anchor="start"))
    P.append(arrow(ex - 20, y0 + 250, ex - 20, y0 + 96 + 60, color=RED))
    P.append(text(ex + 44, y0 + 230, "зростання обганяє", size=11.5, color=RED, anchor="start", bold=True))
    P.append(text(ex + 44, y0 + 250, "будь-яку формулу", size=11.5, color=RED, anchor="start", bold=True))

    P.append(text(W / 2, y0 + 7 * rh + 40,
                  "п'ятірку довели 2024 року (bbchallenge, Coq); шістку не притиснуто досі",
                  size=12, color=MUTED))
    render("img/explosion.svg", W, H, *P)


# ── Фігура 4: чому необчислюване (зведення до проблеми зупинки) ───────────────
def fig_uncomputable():
    W, H = 900, 580
    P = [text(W / 2, 30, "Чому завзятого бобра не обчислити ніколи", size=16, bold=True)]

    cx = W / 2
    boxes = [
        (86, BLUE, "#eaf0fd", "ПРИПУСТІМО: S(n) можна обчислити"),
        (176, INK, FILL, "Дано n-станову машину M.  Порахуй S(n)\nі проганяй M рівно S(n) кроків"),
        (286, INK, FILL, "спинилась за S(n) кроків → M зупиняється\n"
                         "не спинилась → не спиниться НІКОЛИ\n(бо S(n) — стеля для всіх, що спиняються)"),
        (398, GREEN, "#eafaf0", "Отже, ми вирішили ПРОБЛЕМУ ЗУПИНКИ\nдля будь-якої машини"),
        (480, RED, "#fdecea", "Але проблема зупинки НЕРОЗВ'ЯЗНА  ✗"),
    ]
    prev_bottom = None
    for cy, col, fill, txt in boxes:
        box, bw, bh = textbox(cx, cy, txt, size=13, fill=fill, stroke=col, color=INK, bold=True)
        if prev_bottom is not None:
            P.append(arrow(cx, prev_bottom, cx, cy - bh / 2 - 4, color=MUTED))
        P.append(box)
        prev_bottom = cy + bh / 2 + 2

    # висновок збоку — суперечність
    P.append(text(cx + 250, 480, "⇅", size=26, color=RED, bold=True))
    concl, cw2, ch2 = textbox(cx, 546,
                              "СУПЕРЕЧНІСТЬ ⇒ S(n) і Σ(n) — необчислювані:  "
                              "формули не буде ніколи",
                              size=13.5, fill="#fdf3e3", stroke=AMBER, color=INK, bold=True)
    P.append(arrow(cx, prev_bottom, cx, 546 - ch2 / 2 - 4, color=RED))
    P.append(concl)
    render("img/uncomputable.svg", W, H, *P)


# ── Фігура 5: хронологія полювання на бобра (для вставки hist) ────────────────
def fig_hunt():
    W, H = 1140, 470
    P = [text(W / 2, 32, "Полювання на завзятого бобра: 62 роки", size=16, bold=True)]

    spine_y = 235
    xs = [120, 348, 576, 804, 1018]
    # (рік, ім'я, результат, колір вузла, заливка картки, згори?)
    nodes = [
        ("1962",        "Тібор Радо",       "вводить гру",        BLUE,  "#eaf0fd", True),
        ("1963–65",     "Шень Лінь",        "Σ(3)=6 · S(3)=21",   INK,   BG,        False),
        ("1974 · 1983", "Аллен Брейді",     "Σ(4)=13 · S(4)=107", INK,   BG,        True),
        ("1989–90",     "Марксен, Бунтрок", "5 ст.: 47 176 870",  AMBER, "#fdf3e3", False),
        ("2024",        "bbchallenge · Coq","BB(5) доведено",     GREEN, "#eafaf0", True),
    ]

    # хребет часу
    P.append(line(xs[0] - 26, spine_y, xs[-1] + 26, spine_y, color="#c9ced4", sw=3))

    for (yr, who, res, col, fill, up), x in zip(nodes, xs):
        cy = 118 if up else 352
        card, cw, chh = textbox(x, cy, "%s\n%s\n%s" % (yr, who, res),
                                size=13, fill=fill, stroke=col, color=INK, bold=True)
        # з'єднувач вузол → картка
        if up:
            P.append(line(x, spine_y - 8, x, cy + chh / 2 + 2, color=col, sw=1.6))
        else:
            P.append(line(x, spine_y + 8, x, cy - chh / 2 - 2, color=col, sw=1.6))
        P.append(card)
        P.append(circle(x, spine_y, 9, fill=fill, stroke=col, sw=2.4))

    # довга тиша між 5-становою машиною та її доказом
    midx = (xs[3] + xs[4]) / 2
    P.append(text(midx, spine_y - 16, "34 роки тиші", size=12, color=MUTED, bold=True))
    P.append(text(midx, spine_y + 26, "→", size=18, color=MUTED))

    P.append(text(W / 2, 448,
                  "Від дитячої гри Радо до формального доказу минуло 62 роки; "
                  "п'ятірку знайшли 1989-го, а довели аж 2024-го.",
                  size=12.5, color=MUTED))
    render("img/hunt.svg", W, H, *P)


# ── Фігура 6: конструкція Радо (для вставки math) ────────────────────────────
def fig_domination():
    W, H = 1140, 440
    P = [text(W / 2, 32, "Конструкція Радо: n станів «називають» n, стала c робить решту",
              size=15.5, bold=True)]
    ay = 165  # вісь конвеєра

    # чиста стрічка
    for i in range(3):
        P.append(cell(80 + 38 * i, ay, "·", w=38, h=40, tcol=MUTED))
    P.append(text(80 + 38, ay - 34, "чиста стрічка", size=11.5, color=MUTED))

    # блок 1 — ланцюжок
    b1, w1, h1 = textbox(330, ay, "ЛАНЦЮЖОК\nn станів → n одиниць", size=12.5,
                         fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    P.append(arrow(80 + 38 * 2 + 20, ay, 330 - w1 / 2 - 8, ay, color=INK))
    P.append(b1)
    P.append(text(330, ay + h1 / 2 + 22, "дешево: n станів лише на n одиниць", size=11, color=MUTED))

    # стрічка: n одиниць
    xm = 565
    for i in range(3):
        P.append(cell(xm + 34 * i, ay, "1", w=34, h=40, tcol=INK, size=15))
    P.append(text(xm + 34, ay - 34, "на стрічці: n", size=11.5, color=MUTED))
    P.append(arrow(330 + w1 / 2 + 8, ay, xm - 20, ay, color=INK))

    # блок 2 — гаджет
    b2, w2, h2 = textbox(825, ay, "ГАДЖЕТ · c станів\n(СТАЛО) рахує f(2n)+1", size=12.5,
                         fill="#fdf3e3", stroke=AMBER, color=INK, bold=True)
    P.append(arrow(xm + 34 * 2 + 20, ay, 825 - w2 / 2 - 8, ay, color=INK))
    P.append(b2)
    P.append(text(825, ay + h2 / 2 + 22, "n — це ВХІД гаджета, не частина його таблиці",
                  size=11, color=MUTED))

    # стрічка: f(2n)+1 одиниць
    xr = 1010
    for i in range(3):
        P.append(cell(xr + 26 * i, ay, "1", w=26, h=40, tcol=FIELD, size=13))
    P.append(text(xr + 26, ay - 34, "f(2n)+1", size=11.5, color=FIELD, bold=True))
    P.append(arrow(825 + w2 / 2 + 8, ay, xr - 16, ay, color=FIELD))

    # банер-висновок
    bn, bw, bh = textbox(W / 2, 372,
                         "Σ(n+c) ≥ f(2n)+1 > f(n+c):  подвоєння аргументу 2n назавжди "
                         "покриває сталий борг c  (від n ≥ c)",
                         size=13, fill=FILL, stroke=INK, color=INK, bold=True)
    P.append(bn)
    render("img/domination.svg", W, H, *P)


# ── Фігура 7: двобічне зведення S ≡ Σ ≡ зупинка (для вставки math) ────────────
def fig_equivalence():
    W, H = 1160, 430
    P = [text(W / 2, 32, "S, Σ і зупинка на чистій стрічці — той самий рівень нерозв'язності",
              size=15.5, bold=True)]
    yc = 205
    nSig, wSig, hSig = textbox(160, yc, "Σ(n)\nслід на стрічці", size=14,
                               fill=FILL, stroke=INK, color=INK, bold=True)
    nS, wS, hS = textbox(560, yc, "S(n)\nчас роботи", size=14,
                         fill=FILL, stroke=INK, color=INK, bold=True)
    nH, wH, hH = textbox(1000, yc, "ПРОБЛЕМА ЗУПИНКИ\nна чистій стрічці", size=13,
                         fill="#fdecea", stroke=POS, color=INK, bold=True)

    # Σ ↔ S : подвійна стрілка + межа
    lo, ro = 160 + wSig / 2, 560 - wS / 2
    P.append(arrow(lo + 6, yc - 9, ro - 6, yc - 9, color=MUTED))
    P.append(arrow(ro - 6, yc + 9, lo + 6, yc + 9, color=MUTED))
    mo = (lo + ro) / 2
    P.append(text(mo, yc - 26, "Σ(n) ≤ S(n) < Σ(3n+6)", size=12.5, color=INK, bold=True))
    P.append(text(mo, yc + 36, "лінійний зсув аргументу", size=11.5, color=MUTED))

    # S ↔ ПЗЧС : дві напрямлені стрілки
    lh, rh = 560 + wS / 2, 1000 - wH / 2
    mh = (lh + rh) / 2
    P.append(arrow(lh + 6, yc - 22, rh - 6, yc - 22, color=NEG))
    P.append(text(mh, yc - 34, "знаю S(n) → жену машину S(n) кроків", size=11.5, color=NEG))
    P.append(arrow(rh - 6, yc + 22, lh + 6, yc + 22, color=FIELD))
    P.append(text(mh, yc + 42, "вирішувач → перебір усіх машин, лишаю спинні → S, Σ",
                  size=11, color=FIELD))

    # банер
    bn, bw, bh = textbox(W / 2, 372,
                         "Обчислити будь-яку з трьох = розв'язати проблему зупинки.  "
                         "Усі три однаково нерозв'язні.",
                         size=13, fill=FILL, stroke=INK, color=INK, bold=True)
    P.append(bn)
    render("img/equivalence.svg", W, H, *P)


# ── Фігура 8: наближення знизу без сертифіката (для вставки math) ─────────────
def fig_approx():
    W, H = 940, 560
    P = [text(W / 2, 32, "Наближати Σ(n) знизу можна — але без сертифіката, що вже досяг",
              size=15, bold=True)]
    L, R, B, T = 120, 800, 450, 120
    sigma_y = 175  # рівень справжнього Σ(n)

    # заборонена зона над Σ(n)
    P.append(rect(L, T, R - L, sigma_y - T, fill="#fdecea", stroke="none", sw=0, rx=0))
    P.append(text((L + R) / 2, T + 30, "обчислюваної стелі НЕМАЄ — наслідок теореми Радо",
                  size=13, color=POS, bold=True))

    # осі
    P.append(arrow(L, B, R + 12, B, color=INK))
    P.append(arrow(L, B, L, T - 12, color=INK))
    P.append(text(R + 8, B + 24, "s → (женемо все довше)", size=12, color=MUTED, anchor="end"))
    P.append(text(L + 4, T - 18, "одиниць", size=12, color=MUTED, anchor="start"))

    # межа Σ(n)
    P.append(line(L, sigma_y, R, sigma_y, color=INK, sw=1.6, dash="7 5"))
    P.append(text(L + 6, sigma_y + 20, "Σ(n) — справжнє значення (точно недосяжне)",
                  size=12, color=INK, bold=True, anchor="start"))

    # сходинки Σₛ(n), що повзуть угору й лишають провал під Σ(n)
    pts = [(120, 432), (210, 432), (210, 378), (300, 378), (300, 332), (395, 332),
           (395, 292), (500, 292), (500, 256), (610, 256), (610, 226), (700, 226), (700, 212)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        P.append(line(x1, y1, x2, y2, color=NEG, sw=3))

    # провал невідомої висоти між останнім щаблем і Σ(n)
    P.append(arrow(700, 210, 700, sigma_y + 3, color=POS))
    P.append(mtext(716, 190, ["провал невідомої", "висоти  (?)"], size=11, color=POS, anchor="start"))

    # підписи знизу
    P.append(text(430, 494, "Σₛ(n): жени всі машини s кроків → максимум одиниць серед спинних",
                  size=11.5, color=NEG))
    P.append(text(W / 2, 524, "сертифікат близькості = стеля на S(n) = оракул зупинки, тому його немає",
                  size=12, color=MUTED))
    render("img/approx.svg", W, H, *P)


# ── Фігура 9: конвеєр мисливця (для вставки proj) ────────────────────────────
def fig_hunter_pipeline():
    W, H = 1080, 470
    P = [text(W / 2, 30, "Мисливець на бобра: скінченна арена → симулятор → три відра", size=16, bold=True)]

    a_box, aw, ah = textbox(150, 150,
                            "АРЕНА — СКІНЧЕННА\nусі (4n+4)²ⁿ таблиць\n"
                            "n=2: 20 736\nn=3: 16 777 216",
                            size=13, fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    P.append(a_box)

    s_box, sw, sh = textbox(400, 150,
                            "СИМУЛЯТОР\nкожну — з чистої\nстрічки, стеля C кроків",
                            size=13, fill=CTRL, stroke=INK, color=INK, bold=True)
    P.append(arrow(150 + aw / 2 + 6, 150, 400 - sw / 2 - 8, 150, color=INK))
    P.append(s_box)

    g_box, gw, gh = textbox(700, 92,
                            "ЗУПИНИЛАСЬ ≤ C\nкроки й одиниці відомі",
                            size=12.5, fill="#eafaf0", stroke=GREEN, color=INK, bold=True)
    P.append(arrow(400 + sw / 2 + 6, 138, 700 - gw / 2 - 8, 100, color=GREEN))
    P.append(g_box)

    c_box, cw, ch = textbox(980, 92,
                            "ЧЕМПІОН\nmax 1 → Σ(n)\nmax кроків → S(n)",
                            size=12.5, fill=BG, stroke=GREEN, color=INK, bold=True)
    P.append(arrow(700 + gw / 2 + 6, 92, 980 - cw / 2 - 8, 92, color=GREEN))
    P.append(c_box)

    r_box, rw, rh = textbox(760, 258,
                            "ЩЕ ПРАЦЮЄ на кроці C\nспиниться чи ні — НЕВІДОМО\n"
                            "без наперед відомого S(n)\nне класифікувати",
                            size=12.5, fill="#fdecea", stroke=RED, color=INK, bold=True)
    P.append(arrow(400 + sw / 2 + 6, 168, 760 - rw / 2 - 8, 244, color=RED))
    P.append(r_box)
    P.append(text(760, 258 + rh / 2 + 22, "це і є стіна зупинки", size=11.5, color=RED, bold=True))

    nb, nbw, nbh = textbox(W / 2, 428,
                           "Арену перебрати МОЖНА — вона скінченна.  "
                           "А долю кожної машини визначити напевно — вже ні: це проблема зупинки.",
                           size=13, fill=FILL, stroke=INK, color=INK, bold=True)
    P.append(nb)
    render("img/hunter-pipeline.svg", W, H, *P)


# ── Фігура 10: стіна кроку-стелі (для вставки proj) ──────────────────────────
def fig_step_cap():
    W, H = 1000, 500
    P = [text(W / 2, 30, "Стіна стелі: машину за стелею не класифікувати", size=16, bold=True)]

    base_y = 360
    x0 = 90
    scale = 34
    bars = [(1, 30), (2, 46), (3, 60), (5, 88), (6, 100), (12, 150)]
    P.append(line(x0 - 20, base_y, x0 + 24 * scale, base_y, color=INK, sw=2))
    P.append(text(x0 + 24 * scale, base_y + 26, "кроків до зупинки →", size=12.5,
                  color=MUTED, anchor="end"))
    for k in (1, 5, 10, 15, 20, 21):
        xx = x0 + k * scale
        P.append(line(xx, base_y - 4, xx, base_y + 4, color=MUTED, sw=1.2))
        P.append(text(xx, base_y + 18, str(k), size=11, color=MUTED))
    for k, hgt in bars:
        xx = x0 + k * scale
        P.append(rect(xx - 8, base_y - hgt, 16, hgt, fill="#eafaf0", stroke=GREEN, sw=1.6, rx=2))
    xc = x0 + 21 * scale
    P.append(rect(xc - 8, base_y - 190, 16, 190, fill="#fdecea", stroke=RED, sw=2, rx=2))
    P.append(text(xc, base_y - 200, "S(3)=21", size=12.5, color=RED, bold=True))

    xcap = x0 + 20 * scale
    P.append(line(xcap, base_y - 250, xcap, base_y + 6, color=NEG, sw=2, dash="7 5"))
    cbx, cbw, cbh = textbox(xcap - 150, 96, "стеля C = 20", size=12.5,
                            fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    P.append(cbx)
    P.append(arrow(xcap - 150 + cbw / 2, 96, xcap - 4, 96, color=NEG))

    reg, rw, rh = textbox(xc + 96, 150,
                          "праворуч від стелі:\nмашина ще працює —\nспиниться чи крутиться\nВІЧНО, знати годі",
                          size=12, fill="#fdecea", stroke=RED, color=INK, bold=True)
    P.append(reg)
    P.append(arrow(xc + 96 - rw / 2 - 4, 150 + rh / 2, xc + 10, base_y - 150, color=RED))

    nb, nbw, nbh = textbox(W / 2, 456,
                           "Стелю треба брати C ≥ S(n).  Але S(n) — саме те, чого ми не знаємо наперед: "
                           "будь-яка стеля може виявитися замалою.",
                           size=12.5, fill=FILL, stroke=AMBER, color=INK, bold=True)
    P.append(nb)
    render("img/step-cap.svg", W, H, *P)


# ── Фігура 11: нормалізація першої дії (для вставки proj) ─────────────────────
def fig_start_norm():
    W, H = 980, 480
    P = [text(W / 2, 30, "Симетрія: перша дія A,0 — одна замість (4n+4)", size=16, bold=True)]

    src, srw, srh = textbox(150, 240, "старт:\nA бачить 0", size=14,
                            fill=CTRL, stroke=INK, color=INK, bold=True)
    P.append(src)

    rows = [
        (96,  RED,   "#fdecea", "пише 0  → або петля,\nабо тривіальна зупинка"),
        (176, RED,   "#fdecea", "(1,·,A)  → біжить\nправоруч ВІЧНО"),
        (256, AMBER, "#fdf3e3", "(1,·,H)  → стоп за 1 крок\n(це вже бобер n=1)"),
        (352, GREEN, "#eafaf0", "(1, R, B)  → канонічний старт\nЄДИНИЙ, що лишаємо"),
    ]
    for cy, col, fill, txt in rows:
        b, bw, bh = textbox(560, cy, txt, size=12.5, fill=fill, stroke=col, color=INK, bold=True)
        P.append(arrow(150 + srw / 2 + 6, 240, 560 - bw / 2 - 8, cy, color=col))
        P.append(b)

    P.append(text(560, 306, "(1,L,·) ≡ (1,R,·)  — дзеркало L↔R", size=11.5, color=MUTED))

    res, rw2, rh2 = textbox(825, 352,
                            "лишилась ОДНА:\nA,0 = (1,R,B)\n\nарену ділимо на (4n+4)\n"
                            "n=3: 16 777 216 ÷ 16\n= 1 048 576",
                            size=12.5, fill=BG, stroke=GREEN, color=INK, bold=True)
    P.append(arrow(560 + 145, 352, 825 - rw2 / 2 - 8, 352, color=GREEN))
    P.append(res)
    render("img/start-norm.svg", W, H, *P)


if __name__ == "__main__":
    fig_game()
    fig_bb2_run()
    fig_explosion()
    fig_uncomputable()
    fig_hunt()
    fig_domination()
    fig_equivalence()
    fig_approx()
    fig_hunter_pipeline()
    fig_step_cap()
    fig_start_norm()
    print("OK: game.svg, bb2-run.svg, explosion.svg, uncomputable.svg, hunt.svg, "
          "domination.svg, equivalence.svg, approx.svg, "
          "hunter-pipeline.svg, step-cap.svg, start-norm.svg")
