# -*- coding: utf-8 -*-
"""Фігури до теми «Зіткнення (пружні й непружні)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AMBER = "#b9770e"


def ball(cx, cy, r, lab):
    return (circle(cx, cy, r, fill="#eef2fb", stroke=INK, sw=2) +
            text(cx, cy + 5, lab, size=int(r * 0.7) + 4, bold=True, color=INK))


# ── Фігура 1: коефіцієнт відновлення e як шкала від пружного до злипання ───────
def fig_restitution_scale():
    W, H = 980, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Коефіцієнт відновлення e — ручка між пружним ударом і злипанням",
                  size=16, bold=True))

    cols = [180, 490, 800]
    pw = 290
    ptop, ph = 54, 372
    heads = [("e = 1", "пружний", FIELD, "#eef6ef"),
             ("0 < e < 1", "реальний", AMBER, "#fbf3e3"),
             ("e = 0", "непружний", POS, "#fdf0ee")]

    yb = ptop + 120          # ряд «до»
    ya = ptop + 238          # ряд «після»

    for cx, (etxt, sub, col, bg) in zip(cols, heads):
        f.append(rect(cx - pw / 2, ptop, pw, ph, fill=bg, stroke=col, sw=1.7, rx=11))
        f.append(text(cx, ptop + 30, etxt, size=16, bold=True, color=col))
        f.append(text(cx, ptop + 50, sub, size=12, color=MUTED))

        # ── «до»: дві рівні кулі зближуються (однаково в усіх колонках) ──
        f.append(text(cx, yb - 54, "до", size=11, color=MUTED))
        f.append(ball(cx - 44, yb, 20, "m"))
        f.append(ball(cx + 44, yb, 20, "m"))
        f.append(arrow(cx - 62, yb - 34, cx - 26, yb - 34, color=FIELD, sw=3.0))
        f.append(arrow(cx + 62, yb - 34, cx + 26, yb - 34, color=FIELD, sw=3.0))

        # ── «після»: залежить від e ──
        f.append(text(cx, ya - 54, "після", size=11, color=MUTED))

    # e = 1 : повний відскок
    cx = cols[0]
    f.append(ball(cx - 60, ya, 20, "m"))
    f.append(ball(cx + 60, ya, 20, "m"))
    f.append(arrow(cx - 78, ya - 34, cx - 114, ya - 34, color=NEG, sw=3.0))
    f.append(arrow(cx + 78, ya - 34, cx + 114, ya - 34, color=NEG, sw=3.0))

    # 0 < e < 1 : частковий відскок
    cx = cols[1]
    f.append(ball(cx - 48, ya, 20, "m"))
    f.append(ball(cx + 48, ya, 20, "m"))
    f.append(arrow(cx - 66, ya - 34, cx - 90, ya - 34, color=NEG, sw=3.0))
    f.append(arrow(cx + 66, ya - 34, cx + 90, ya - 34, color=NEG, sw=3.0))

    # e = 0 : злиплися, стоять
    cx = cols[2]
    f.append(ball(cx - 20, ya, 20, "m"))
    f.append(ball(cx + 20, ya, 20, "m"))
    f.append(text(cx, ya + 40, "стоять разом", size=12, bold=True, color=POS))

    # ── статус-рядки під сценами ──
    stats = [(["розліт = зближення", "енергія ціла"], FIELD, "#eef6ef"),
             (["розліт = 0.6 · зближення", "частина → тепло"], AMBER, "#fbf3e3"),
             (["розліт = 0", "утрата максимальна"], POS, "#fdf0ee")]
    for cx, (lines, col, bg) in zip(cols, stats):
        b, _, _ = textbox(cx, ptop + ph - 38, lines, size=12, pad=9,
                          fill=bg, stroke=col, sw=1.3, bold=True, color=INK)
        f.append(b)

    b, _, _ = textbox(W / 2, H - 26,
                      "Той самий удар, той самий імпульс — а доля різна: усе вирішує одне число e",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "restitution-scale.svg"), W, H, *f)


# ── Фігура 2: балістичний маятник — дві події, два різні закони ────────────────
def fig_ballistic_pendulum():
    W, H = 920, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Балістичний маятник: удар рахуємо імпульсом, гойдання — енергією",
                  size=16, bold=True))

    # ── пояснювальні картки в кутах ──
    b1, _, _ = textbox(198, 150,
                       ["1 · Удар (застрягання)", "імпульс: m·v = (m+M)·V", "енергію брати НЕ можна"],
                       size=12, pad=11, fill="#fdf0ee", stroke=POS, sw=1.6, bold=True, color=INK)
    f.append(b1)
    b2, _, _ = textbox(720, 150,
                       ["2 · Гойдання вгору", "енергія: ½(m+M)V² = (m+M)g·h", "тертя нема"],
                       size=12, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True, color=INK)
    f.append(b2)

    # ── маятник ──
    P = (450, 240)                 # шарнір
    L = 210                        # довжина нитки
    rest = (450, P[1] + L)         # блок у спокої (одразу після удару)
    th = math.radians(40)
    rais = (P[0] + L * math.sin(th), P[1] + L * math.cos(th))   # блок на вершині гойдання

    # стеля
    f.append(line(390, P[1] - 12, 510, P[1] - 12, color=INK, sw=2.4))
    for hx in range(400, 505, 14):
        f.append(line(hx, P[1] - 12, hx - 8, P[1] - 22, color=MUTED, sw=1.2))
    f.append(circle(P[0], P[1], 4, fill=INK, stroke=INK, sw=1))

    # нитки: спокій (суцільна) і вершина (пунктир)
    f.append(line(P[0], P[1], rest[0], rest[1] - 33, color=INK, sw=1.6))
    f.append(line(P[0], P[1], rais[0], rais[1] - 30, color=MUTED, sw=1.4, dash="5 5"))

    # дуга гойдання (траєкторія центра блока)
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="4 5"/>'
             % (rest[0], rest[1], L, L, rais[0], rais[1], MUTED))

    # блок у спокої з застряглою кулею + швидкість V
    bw = 62
    f.append(rect(rest[0] - bw / 2, rest[1] - bw / 2, bw, bw, fill="#e8ecf5", stroke=INK, sw=2, rx=6))
    f.append(circle(rest[0] - bw / 2 + 12, rest[1], 7, fill=POS, stroke=POS, sw=1))   # куля
    f.append(text(rest[0] + 4, rest[1] + 5, "M", size=16, bold=True, color=INK))
    f.append(arrow(rest[0] + bw / 2 + 6, rest[1], rest[0] + bw / 2 + 46, rest[1], color=NEG, sw=3.0))
    f.append(text(rest[0] + bw / 2 + 26, rest[1] - 12, "V", size=14, bold=True, color=NEG))

    # блок на вершині (пунктирний контур), V = 0
    f.append(rect(rais[0] - bw / 2, rais[1] - bw / 2, bw, bw, fill="none", stroke=MUTED, sw=1.6, rx=6))
    f.append(text(rais[0], rais[1] + 5, "V=0", size=12, bold=True, color=MUTED))

    # куля влітає зліва
    f.append(arrow(150, rest[1], rest[0] - bw / 2 - 6, rest[1], color=POS, sw=3.0))
    f.append(text(250, rest[1] - 14, "куля  m, v", size=14, bold=True, color=POS))

    # висота h праворуч
    hx = rais[0] + bw / 2 + 40
    f.append(line(rais[0] + bw / 2, rais[1], hx + 8, rais[1], color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(rest[0], rest[1] + bw / 2 + 4, hx + 8, rest[1] + bw / 2 + 4, color=MUTED, sw=1.2, dash="4 4"))
    ytop, ybot = rais[1], rest[1] + bw / 2 + 4
    f.append(arrow(hx, ytop, hx, ybot, color=INK, sw=1.8))
    f.append(arrow(hx, ybot, hx, ytop, color=INK, sw=1.8))
    f.append(text(hx + 14, (ytop + ybot) / 2 + 4, "h", size=16, bold=True, italic=True, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, H - 28,
                      "Зшивши дві події, знаходимо швидкість кулі v з висоти підскоку h — без жодного датчика швидкості",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "ballistic-pendulum.svg"), W, H, *f)


# ── Фігура 3: пружний удар — три обличчя за співвідношенням мас ────────────────
def fig_elastic_regimes():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Пружний удар: три обличчя тієї самої пари формул — усе вирішують маси",
                  size=16, bold=True))

    divx = 448
    f.append(line(divx, 66, divx, 486, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(238, 92, "до удару", size=14, bold=True, color=MUTED))
    f.append(text(662, 92, "після удару", size=14, bold=True, color=MUTED))

    def vel(cx, cy, r, length, rightward):
        y = cy - r - 16
        if rightward:
            f.append(arrow(cx + r + 4, y, cx + r + 4 + length, y, color=FIELD, sw=3.0))
        else:
            f.append(arrow(cx - r - 4, y, cx - r - 4 - length, y, color=FIELD, sw=3.0))

    def rowlabel(cy, s):
        f.append(text(60, cy - 62, s, size=13, bold=True, color=INK, anchor="start"))

    def outcome(cy, s):
        f.append(text(662, cy + 66, s, size=13, bold=True, color=INK))

    # Рядок 1: рівні маси — обмін швидкостями (колиска Ньютона)
    cy = 168
    rowlabel(cy, "рівні маси   m = m")
    f.append(ball(178, cy, 21, "m")); vel(178, cy, 21, 46, True)
    f.append(ball(300, cy, 21, "m"))
    f.append(ball(586, cy, 21, "m"))
    f.append(ball(720, cy, 21, "m")); vel(720, cy, 21, 46, True)
    outcome(cy, "обмінялися швидкостями — «колиска Ньютона»")

    # Рядок 2: важке б'є легке — легке ~вдвічі швидше
    cy = 312
    rowlabel(cy, "важке б'є легке   M ≫ m")
    f.append(ball(178, cy, 27, "M")); vel(178, cy, 27, 46, True)
    f.append(ball(312, cy, 13, "m"))
    f.append(ball(584, cy, 27, "M")); vel(584, cy, 27, 40, True)
    f.append(ball(720, cy, 13, "m")); vel(720, cy, 13, 86, True)
    outcome(cy, "легке зривається вперед ~вдвічі швидше")

    # Рядок 3: легке б'є важке — відскакує назад
    cy = 456
    rowlabel(cy, "легке б'є важке   m ≪ M")
    f.append(ball(178, cy, 13, "m")); vel(178, cy, 13, 46, True)
    f.append(ball(308, cy, 27, "M"))
    f.append(ball(602, cy, 13, "m")); vel(602, cy, 13, 44, False)
    f.append(ball(728, cy, 27, "M"))
    outcome(cy, "легке відскакує назад, важке ледь рушає")

    b, _, _ = textbox(W / 2, H - 26,
                      "У пружному ударі тримаються обидва закони — і імпульс, і енергія; маси й вирішують результат",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "elastic-regimes.svg"), W, H, *f)


# ── Фігура 4 (вставка hist): чотири акти народження законів удару ──────────────
def fig_collision_laws_story():
    W, H = 980, 690
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 36, "Народження законів удару: чотири акти одного століття",
                  size=17, bold=True))

    spine_x = 120
    f.append(line(spine_x, 92, spine_x, 632, color=MUTED, sw=2.6))

    cx = 150            # лівий край карток
    cw = 780           # ширина картки
    ch = 108           # висота картки
    ys = [150, 300, 450, 600]   # центри вузлів

    cards = [
        ("1644", POS, "#fdf0ee",
         ["Рене Декарт, «Principia philosophiae»",
          "«Кількість руху» = розмір × швидкість, БЕЗ напряму; сім правил удару — частина хибні.",
          "Бракує напряму: куля, відскочивши назад, у Декартовім рахунку «зберігає» рух."]),
        ("1668–69", FIELD, "#eef6ef",
         ["Королівське товариство ставить задачу всій Європі",
          "Валліс (непружний) · Рен (пружний) · Гюйґенс (пружний) — три відповіді збіглися.",
          "Народжується закон імпульсу: зберігається m·v — тепер із напрямом."]),
        ("1656→1703", NEG, "#eef2fb",
         ["Крістіан Гюйґенс, «De Motu Corporum ex Percussione»",
          "Відносність руху (уявний човен) як інструмент; друга збережна величина — «жива сила» m·v².",
          "Розв'язав ще 1656 — повний трактат вийшов посмертно, 1703."]),
        ("1687", AMBER, "#fbf3e3",
         ["Ісаак Ньютон, «Математичні начала»",
          "Не теорія, а вимір: розгойдані кульки з вовни, сталі, корка, скла.",
          "Розліт — стала частка зближення: вовна й сталь ≈ 5/9, скло ≈ 15/16."]),
    ]

    for y, (yr, col, bg, lines) in zip(ys, cards):
        f.append(circle(spine_x, y, 8, fill=col, stroke=col, sw=2))
        f.append(text(spine_x - 22, y + 5, yr, size=14, bold=True, color=col, anchor="end"))
        f.append(rect(cx, y - ch / 2, cw, ch, fill=bg, stroke=col, sw=1.8, rx=10))
        f.append(text(cx + 18, y - ch / 2 + 26, lines[0], size=14, bold=True,
                      color=INK, anchor="start"))
        f.append(text(cx + 18, y - ch / 2 + 54, lines[1], size=13,
                      color=INK, anchor="start"))
        f.append(text(cx + 18, y - ch / 2 + 82, lines[2], size=13,
                      color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "collision-laws-story.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): човен Гюйґенса — відносність робить закон ──────────
def fig_huygens_boat():
    W, H = 980, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Човен Гюйґенса: той самий удар з двох систем відліку",
                  size=17, bold=True))

    colx = [312, 726]                 # центри «до» / «після»
    divx = 519
    f.append(line(divx, 74, divx, 512, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(colx[0], 96, "до удару", size=14, bold=True, color=MUTED))
    f.append(text(colx[1], 96, "після удару", size=14, bold=True, color=MUTED))

    r = 19

    def vlabel(cx, y, s, col):
        f.append(text(cx, y - r - 22, s, size=13, bold=True, color=col))

    # ── ряд 1: у човні — симетрія ──
    y1 = 210
    f.append(text(70, y1 - 78, "у човні (пливе →)", size=13, bold=True, color=INK, anchor="start"))
    # вода під рядом
    for cx in colx:
        f.append(line(cx - 132, y1 + 56, cx + 132, y1 + 56, color=NEG, sw=1.6))
        f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
                 'fill="#eef2fb" stroke="%s" stroke-width="1.4"/>'
                 % (cx - 74, y1 + 34, cx + 74, y1 + 34, cx + 52, y1 + 56, cx - 52, y1 + 56, NEG))
    # до: наближаються рівні
    cx = colx[0]
    f.append(ball(cx - 46, y1, r, "1")); f.append(arrow(cx - 74, y1 - r - 8, cx - 30, y1 - r - 8, color=FIELD, sw=3.0)); vlabel(cx - 46, y1, "v", FIELD)
    f.append(ball(cx + 46, y1, r, "2")); f.append(arrow(cx + 74, y1 - r - 8, cx + 30, y1 - r - 8, color=FIELD, sw=3.0)); vlabel(cx + 46, y1, "v", FIELD)
    # після: розлітаються рівні
    cx = colx[1]
    f.append(ball(cx - 52, y1, r, "1")); f.append(arrow(cx - 78, y1 - r - 8, cx - 116, y1 - r - 8, color=POS, sw=3.0)); vlabel(cx - 52, y1, "v", POS)
    f.append(ball(cx + 52, y1, r, "2")); f.append(arrow(cx + 78, y1 - r - 8, cx + 116, y1 - r - 8, color=POS, sw=3.0)); vlabel(cx + 52, y1, "v", POS)

    # ── ряд 2: з берега — правило обміну ──
    y2 = 400
    f.append(text(70, y2 - 78, "з берега (нерухомий)", size=13, bold=True, color=INK, anchor="start"))
    f.append(line(colx[0] - 150, y2 + 44, colx[1] + 150, y2 + 44, color=MUTED, sw=1.6))
    for hx in range(int(colx[0] - 150), int(colx[1] + 150), 20):
        f.append(line(hx, y2 + 44, hx - 8, y2 + 54, color=MUTED, sw=1.0))
    # до: 1 налітає, 2 спочиває
    cx = colx[0]
    f.append(ball(cx - 44, y2, r, "1")); f.append(arrow(cx - 72, y2 - r - 8, cx - 28, y2 - r - 8, color=FIELD, sw=3.0)); vlabel(cx - 44, y2, "u", FIELD)
    f.append(ball(cx + 52, y2, r, "2")); f.append(text(cx + 52, y2 - r - 20, "спокій", size=12, bold=True, color=MUTED))
    # після: 1 спиняється, 2 зривається з u
    cx = colx[1]
    f.append(ball(cx - 40, y2, r, "1")); f.append(text(cx - 40, y2 - r - 20, "спокій", size=12, bold=True, color=MUTED))
    f.append(ball(cx + 60, y2, r, "2")); f.append(arrow(cx + 86, y2 - r - 8, cx + 124, y2 - r - 8, color=POS, sw=3.0)); vlabel(cx + 60, y2, "u", POS)

    b, _, _ = textbox(W / 2, H - 44,
                      ["Симетрію в човні бачить кожен. Берег додає швидкість човна — і той самий удар",
                       "стає правилом обміну: рухома куля спиняється, нерухома зривається з її швидкістю."],
                      size=13, pad=12, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "huygens-boat.svg"), W, H, *f)


# ── Фігура 6 (вставка proj): геометрія контакту й імпульсний поштовх ───────────
def fig_impulse_resolver():
    W, H = 1000, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Резолвер контакту: один скаляр j розсуває пару тіл уздовж нормалі",
                  size=16, bold=True))

    # ── два диски, що перекрилися ──
    Ax, Ay, Ar = 330, 250, 100     # тіло 1 (налітач)
    Bx, By, Br = 530, 250, 125     # тіло 2
    f.append(circle(Ax, Ay, Ar, fill="#eef2fb", stroke=INK, sw=2))
    f.append(circle(Bx, By, Br, fill="#eef6ef", stroke=INK, sw=2))
    f.append(text(Ax - 6, Ay - 52, "тіло 1", size=14, bold=True, color=INK))
    f.append(text(Ax - 6, Ay - 34, "m₁", size=13, color=MUTED))
    f.append(text(Bx + 24, By - 66, "тіло 2", size=14, bold=True, color=INK))
    f.append(text(Bx + 24, By - 48, "m₂", size=13, color=MUTED))

    # площина контакту (пунктир) і глибина проникання d
    xC = (Ax + Ar + Bx - Br) / 2               # середина смуги перекриття
    f.append(line(xC, 108, xC, 392, color=MUTED, sw=1.3, dash="6 6"))
    xL, xR = Bx - Br, Ax + Ar                   # межі перекриття
    dy = 372
    f.append(arrow(xL, dy, xR, dy, color=POS, sw=1.8))
    f.append(arrow(xR, dy, xL, dy, color=POS, sw=1.8))
    f.append(text((xL + xR) / 2, dy + 20, "d — глибина проникання", size=12, bold=True, color=POS))

    # нормаль n: від тіла 2 до тіла 1 (ліворуч)
    ny = 158
    f.append(arrow(xC, ny, xC - 108, ny, color=INK, sw=3.2))
    f.append(text(xC - 58, ny - 12, "n", size=16, bold=True, italic=True, color=INK))
    b, _, _ = textbox(xC - 150, 122, "нормаль контакту  (від тіла 2 до тіла 1),  |n| = 1",
                      size=11, pad=7, fill="#f4f6f8", stroke=MUTED, sw=1.1, color=INK)
    f.append(b)

    # поштовх ±j·n на центри
    f.append(arrow(Ax, Ay, Ax - 150, Ay, color=POS, sw=3.6))
    f.append(text(Ax - 168, Ay - 12, "+ j·n", size=14, bold=True, color=POS, anchor="end"))
    f.append(arrow(Bx, By, Bx + 165, By, color=NEG, sw=3.6))
    f.append(text(Bx + 174, By - 12, "− j·n", size=14, bold=True, color=NEG, anchor="start"))

    # ── три кроки внизу ──
    steps = [
        (195, FIELD, "#eef6ef",
         ["1 · швидкість зближення", "vₙ = (v₁ − v₂) · n"]),
        (500, AMBER, "#fbf3e3",
         ["2 · скалярний поштовх", "j = −(1+e)·vₙ / (1/m₁ + 1/m₂)"]),
        (812, NEG, "#eef2fb",
         ["3 · розсунути швидкості", "v₁ += j·n/m₁     v₂ −= j·n/m₂"]),
    ]
    for cx, col, bg, lines in steps:
        b, _, _ = textbox(cx, 470, lines, size=13, pad=11, fill=bg, stroke=col, sw=1.5,
                          bold=True, color=INK)
        f.append(b)

    b, _, _ = textbox(W / 2, H - 32,
                      "Порахувати j за нормаллю — і розкидати ±j·n, поділивши на масу кожного тіла: імпульс пари точний, а стіна (1/m = 0) стоїть непорушно",
                      size=12, pad=10, fill="#ffffff", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "impulse-resolver.svg"), W, H, *f)


# ── Фігура 7 (вставка proj): дві латки — втоплення й дрижання ───────────────────
def fig_positional_correction():
    W, H = 1000, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Дві латки понад швидкістю: розсунути втоплене й угамувати дрижання",
                  size=16, bold=True))
    f.append(line(500, 70, 500, 476, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(262, 74, "Взаємне проникання → позиційна корекція", size=13, bold=True, color=INK))
    f.append(text(746, 74, "Спокій → поріг відскоку", size=13, bold=True, color=INK))

    # ── ЛІВА колонка: корекція положення ──
    b, _, _ = textbox(262, 132,
                      ["корекція = β · max(d − slop, 0) / (1/m₁+1/m₂)",
                       "β ≈ 0.2 (Баумгарте) · slop ≈ 1 см"],
                      size=12, pad=10, fill="#fbf3e3", stroke=AMBER, sw=1.4, bold=True, color=INK)
    f.append(b)
    # підлога
    f.append(rect(78, 372, 372, 66, fill="#e8ecf5", stroke=INK, sw=2, rx=4))
    f.append(text(264, 412, "нерухома поверхня  (1/m = 0)", size=12, bold=True, color=MUTED))
    for hx in range(90, 445, 22):
        f.append(line(hx, 372, hx - 9, 384, color=MUTED, sw=1.0))
    # диск, що втопився
    dcx, dcy, dr = 218, 344, 52
    f.append(circle(dcx, dcy, dr, fill="#fdecea", stroke=POS, sw=2))
    # смуга slop
    f.append(line(150, 384, 330, 384, color=FIELD, sw=1.4, dash="4 4"))
    f.append(text(360, 388, "slop", size=11, bold=True, color=FIELD, anchor="start"))
    # глибина проникання d (диск втоплений на 24 нижче поверхні)
    f.append(arrow(dcx + 78, 372, dcx + 78, dcy + dr, color=POS, sw=1.7))
    f.append(arrow(dcx + 78, dcy + dr, dcx + 78, 372, color=POS, sw=1.7))
    f.append(text(dcx + 90, (372 + dcy + dr) / 2 + 4, "d", size=14, bold=True, italic=True, color=POS, anchor="start"))
    # стрілка розсування вгору
    f.append(arrow(dcx, dcy, dcx, dcy - 96, color=FIELD, sw=3.4))
    f.append(text(dcx - 10, dcy - 104, "розсунути", size=12, bold=True, color=FIELD, anchor="middle"))

    # ── ПРАВА колонка: поріг відскоку ──
    b, _, _ = textbox(746, 132,
                      ["якщо |vₙ| < поріг  ⇒  e = 0 (цей контакт)",
                       "поріг ≈ 1 м/с"],
                      size=12, pad=10, fill="#eef2fb", stroke=NEG, sw=1.4, bold=True, color=INK)
    f.append(b)
    # підлога
    f.append(rect(560, 372, 372, 66, fill="#e8ecf5", stroke=INK, sw=2, rx=4))
    for hx in range(572, 928, 22):
        f.append(line(hx, 372, hx - 9, 384, color=MUTED, sw=1.0))
    # диск у спокої (лежить на поверхні)
    rcx, rcy, rr = 700, 320, 52
    f.append(circle(rcx, rcy, rr, fill="#eef6ef", stroke=INK, sw=2))
    # гравітація щокадру тисне вниз
    f.append(arrow(rcx - 78, rcy - 6, rcx - 78, rcy + 40, color=MUTED, sw=2.4))
    f.append(text(rcx - 78, rcy - 16, "g щокадру", size=11, bold=True, color=MUTED))
    # погашений мікровідскок
    f.append(line(rcx + 82, rcy + 6, rcx + 82, rcy - 46, color=POS, sw=2.2, dash="5 4"))
    f.append(text(rcx + 108, rcy - 22, "мікровідскок", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(rcx + 108, rcy - 6, "погашено", size=11, bold=True, color=POS, anchor="start"))
    # перекреслення
    f.append(line(rcx + 74, rcy - 34, rcx + 92, rcy - 16, color=POS, sw=2.4))
    f.append(line(rcx + 92, rcy - 34, rcx + 74, rcy - 16, color=POS, sw=2.4))

    b, _, _ = textbox(W / 2, H - 40,
                      ["Швидкості полагоджено — та тіла лишаються втопленими й тремтливими.",
                       "Позиційна корекція розсуває перекриття, поріг відскоку гасить вічне дрижання спокою."],
                      size=13, pad=12, fill="#ffffff", stroke=MUTED, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "positional-correction.svg"), W, H, *f)


# ── Фігура 8 (вставка math): пружний удар як віддзеркалення у V_cm ─────────────
def fig_cm_mirror():
    W, H = 1000, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Пружний удар — це віддзеркалення кожної швидкості у V_cm",
                  size=16, bold=True))

    xcm, sc = 500, 55                      # V_cm = 2 (м/с) у пікселі; масштаб px на (м/с)
    def X(v):
        return xcm + sc * (v - 2)

    yU, yV, apex = 182, 330, 256
    # дзеркало у V_cm
    f.append(line(xcm, 112, xcm, 388, color=NEG, sw=1.6, dash="6 6"))
    f.append(text(xcm, 104, "V_cm = 2  (дзеркало)", size=13, bold=True, color=NEG))

    # напрямні рядів «до» / «після»
    f.append(line(210, yU, 800, yU, color="#dfe3ea", sw=1.2))
    f.append(line(210, yV, 800, yV, color="#dfe3ea", sw=1.2))
    f.append(text(150, yU + 5, "до", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(text(140, yV + 5, "після", size=13, bold=True, color=MUTED, anchor="start"))

    # відбивні ламані: u → (дзеркало) → v
    for xu, xv in [(X(6), X(-2)), (X(0), X(4))]:
        f.append(line(xu, yU, xcm, apex, color=MUTED, sw=1.3, dash="4 5"))
        f.append(line(xcm, apex, xv, yV, color=MUTED, sw=1.3, dash="4 5"))

    # «до» — зелені вузли
    for x, lab, m in [(X(6), "u₁ = +6", "m₁ = 1"), (X(0), "u₂ = 0", "m₂ = 2")]:
        f.append(circle(x, yU, 8, fill="#eef6ef", stroke=FIELD, sw=2.4))
        f.append(text(x, yU - 20, lab, size=14, bold=True, color=FIELD))
        f.append(text(x, yU - 38, m, size=11, color=MUTED))

    # «після» — сині вузли
    for x, lab in [(X(-2), "v₁ = −2"), (X(4), "v₂ = +4")]:
        f.append(circle(x, yV, 8, fill="#eef2fb", stroke=NEG, sw=2.4))
        f.append(text(x, yV + 26, lab, size=14, bold=True, color=NEG))

    b, _, _ = textbox(W / 2, H - 30,
                      "v = 2·V_cm − u : кожна швидкість після удару — дзеркальний відбиток тієї, що до, відносно спільної V_cm",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "cm-mirror.svg"), W, H, *f)


# ── Фігура 9 (вставка math): косий пружний удар рівних мас — розліт під 90° ─────
def fig_oblique_90():
    W, H = 1040, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Косий пружний удар рівних мас: розліт точно під прямим кутом",
                  size=16, bold=True))

    r = 56
    C1 = (300, 300)
    na = math.radians(20)
    nhat = (math.cos(na), math.sin(na))
    that = (-math.sin(na), math.cos(na))
    C2 = (C1[0] + 2 * r * nhat[0], C1[1] + 2 * r * nhat[1])
    contact = (C1[0] + r * nhat[0], C1[1] + r * nhat[1])

    # нормаль (через центри) і дотична (в точці контакту)
    def seg(p, d, a, b):
        return (p[0] + d[0] * a, p[1] + d[1] * a, p[0] + d[0] * b, p[1] + d[1] * b)
    f.append(line(*seg(contact, nhat, -178, 56), color=MUTED, sw=1.4, dash="7 6"))
    f.append(line(*seg(contact, that, -150, 150), color=MUTED, sw=1.4, dash="7 6"))
    f.append(text(150, 242, "нормаль n", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(text(414, 166, "дотична t", size=13, bold=True, color=MUTED, anchor="start"))

    # диски
    f.append(circle(*C1, r, fill="#eef6ef", stroke=INK, sw=2))
    f.append(circle(*C2, r, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(C1[0], C1[1] + 6, "m", size=18, bold=True, color=INK))
    f.append(text(C2[0], C2[1] + 6, "m", size=18, bold=True, color=INK))
    f.append(text(C2[0] + 4, C2[1] - r - 12, "спокій", size=12, bold=True, color=MUTED))

    # вхідна швидкість u (тіло 1 налітає під 55°)
    ua = math.radians(55)
    uhat = (math.cos(ua), math.sin(ua))
    us = (C1[0] - 122 * uhat[0], C1[1] - 122 * uhat[1])
    f.append(arrow(us[0], us[1], C1[0], C1[1], color=FIELD, sw=3.4))
    f.append(text(us[0] - 8, us[1] - 8, "u", size=17, bold=True, italic=True, color=FIELD))

    # виходи: v₂ уздовж n (тіло 2), v₁ уздовж t (тіло 1)
    dun = uhat[0] * nhat[0] + uhat[1] * nhat[1]
    dut = uhat[0] * that[0] + uhat[1] * that[1]
    v2e = (C2[0] + 150 * dun * nhat[0], C2[1] + 150 * dun * nhat[1])
    v1e = (C1[0] + 150 * dut * that[0], C1[1] + 150 * dut * that[1])
    f.append(arrow(C2[0], C2[1], v2e[0], v2e[1], color=POS, sw=3.4))
    f.append(text(v2e[0] + 12, v2e[1] - 8, "v₂", size=15, bold=True, color=POS, anchor="start"))
    f.append(arrow(C1[0], C1[1], v1e[0], v1e[1], color=NEG, sw=3.4))
    f.append(text(v1e[0] - 12, v1e[1] + 16, "v₁", size=15, bold=True, color=NEG, anchor="end"))

    # ── права панель: чому саме 90° ──
    f.append(rect(700, 118, 318, 384, fill="#fafbfc", stroke=MUTED, sw=1.3, rx=12))
    f.append(text(859, 150, "Чому саме 90°", size=15, bold=True, color=INK))
    O = (770, 300)
    a1 = (O[0] + 104 * that[0], O[1] + 104 * that[1])
    a2 = (O[0] + 104 * nhat[0], O[1] + 104 * nhat[1])
    f.append(arrow(O[0], O[1], a1[0], a1[1], color=NEG, sw=3.0))
    f.append(arrow(O[0], O[1], a2[0], a2[1], color=POS, sw=3.0))
    f.append(text(a1[0] - 6, a1[1] + 18, "v₁", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(a2[0] + 12, a2[1] + 4, "v₂", size=13, bold=True, color=POS, anchor="start"))
    q = 19
    p1 = (O[0] + q * that[0], O[1] + q * that[1])
    p2 = (O[0] + q * nhat[0], O[1] + q * nhat[1])
    p3 = (O[0] + q * (that[0] + nhat[0]), O[1] + q * (that[1] + nhat[1]))
    f.append(line(p1[0], p1[1], p3[0], p3[1], color=INK, sw=1.6))
    f.append(line(p2[0], p2[1], p3[0], p3[1], color=INK, sw=1.6))
    f.append(text(O[0] + 2, O[1] + 74, "90°", size=15, bold=True, color=INK))
    b, _, _ = textbox(859, 448,
                      ["ціль у спокої, рівні маси", "u = v₁ + v₂", "|u|² = |v₁|² + |v₂|²",
                       "⇒  v₁·v₂ = 0  ⇒  v₁ ⟂ v₂"],
                      size=13, pad=10, fill="#fbf3e3", stroke=AMBER, sw=1.4, bold=True, color=INK)
    f.append(b)

    b2, _, _ = textbox(360, H - 30,
                       ["Гладкі тіла тиснуть лише вздовж нормалі: дотичні складові кожного не міняються,",
                        "нормальні б'ються як 1D-удар"],
                       size=12, pad=10, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b2)
    return render(os.path.join(IMG, "oblique-90.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_restitution_scale(), fig_ballistic_pendulum(), fig_elastic_regimes(),
          fig_collision_laws_story(), fig_huygens_boat(),
          fig_impulse_resolver(), fig_positional_correction(),
          fig_cm_mirror(), fig_oblique_90()]
    print("written:")
    for p in ps:
        print("  ", p)
