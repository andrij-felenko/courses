# -*- coding: utf-8 -*-
"""Фігури до кроку «Консистентність конвеєра end-to-end».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eafaf0"
REDFILL   = "#fdecea"


# ───────── Фіг. 1: один факт, багато копій ─────────
def fig_fact_fanout():
    W, H = 1000, 470
    f = []

    # джерело правди (ліворуч)
    b, _, _ = textbox(155, 235, "Джерело правди\nreading записано раз",
                      size=13, bold=True, fill=FILL, stroke=INK, sw=2)
    f.append(b)

    # смуга-конвеєр (центр)
    f.append(rect(360, 200, 150, 72, fill="#fff8e8", stroke="#c9a93b", sw=1.6))
    f.append(mtext(435, 224, ["CDC →", "трансформ →", "завантаження"],
                   size=12, color=INK, bold=True))
    f.append(arrow(250, 236, 358, 236, color=INK, sw=2.2))

    # похідні копії (праворуч) — кожна окрема копія
    derived = [
        (100, "склад даних"),
        (190, "матеріалізована в'ю\n(kWh / день)"),
        (280, "кеш"),
        (370, "індекс пошуку"),
    ]
    for yc, lab in derived:
        b, w, _ = textbox(812, yc, lab, size=12, bold=True,
                          fill=GREENFILL, stroke=FIELD, sw=1.6)
        f.append(b)
        f.append(arrow(512, 236, 812 - w / 2 - 6, yc, color=FIELD, sw=1.7))

    # брекет-дужка праворуч, що охоплює всі копії
    bx = 905
    f.append(line(bx, 84, bx, 396, color=MUTED, sw=1.5))
    f.append(line(bx - 8, 84, bx, 84, color=MUTED, sw=1.5))
    f.append(line(bx - 8, 396, bx, 396, color=MUTED, sw=1.5))
    f.append(text(bx + 8, 240, "N копій", size=12, color=MUTED,
                  anchor="start", bold=True))

    # підпис-вимога понизу
    f.append(text(W / 2, 445,
                  "усі копії мусять означати те саме, що джерело — у межах домовленої затримки",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "fact-fanout.svg"), W, H, *f,
           title="Один факт із джерела — кілька похідних копій")


# ───────── Фіг. 2: три способи, якими рветься ланцюг ─────────
def fig_three_breaks():
    W, H = 1000, 480

    def dot(cx, cy, col=FIELD, fill=GREENFILL, label=None):
        s = circle(cx, cy, 12, fill=fill, stroke=col, sw=1.8)
        if label:
            s += text(cx, cy + 4, label, size=11, color=INK, bold=True)
        return s

    def cross_dot(cx, cy):
        s = circle(cx, cy, 12, fill="#ffffff", stroke=POS, sw=1.8)
        s += line(cx - 8, cy - 8, cx + 8, cy + 8, color=POS, sw=2)
        s += line(cx + 8, cy - 8, cx - 8, cy + 8, color=POS, sw=2)
        return s

    def stage(cx, cy):
        return fitbox(cx - 52, cy - 22, 104, 44, "ланка",
                      size=13, fill=FILL, stroke=MUTED, bold=True)

    f = []

    # доріжка 1 — ВТРАТА
    y = 100
    f.append(text(88, y + 4, "ВТРАТА", size=15, color=POS, bold=True, anchor="middle"))
    for cx in (200, 234, 268):
        f.append(dot(cx, y))
    f.append(arrow(292, y, 402, y, color=INK, sw=1.8))
    f.append(stage(458, y))
    f.append(arrow(514, y, 624, y, color=INK, sw=1.8))
    f.append(dot(650, y)); f.append(dot(684, y)); f.append(cross_dot(718, y))
    f.append(text(560, y + 52, "3 зайшло, 2 вийшло — агрегат недорахований",
                  size=13, color=POS, bold=True))

    # доріжка 2 — ДУБЛЬ
    y = 240
    f.append(text(88, y + 4, "ДУБЛЬ", size=15, color=POS, bold=True))
    f.append(dot(234, y))
    f.append(arrow(258, y, 402, y, color=INK, sw=1.8))
    f.append(stage(458, y))
    # петля-повтор над ланкою
    f.append(text(512, y - 40, "повтор", size=11, color=POS, bold=True))
    f.append(line(480, y - 32, 545, y - 32, color=POS, sw=1.6))
    f.append(line(545, y - 32, 545, y - 18, color=POS, sw=1.6))
    f.append(arrow(545, y - 18, 500, y - 18, color=POS, sw=1.6))
    f.append(arrow(514, y, 624, y, color=INK, sw=1.8))
    f.append(dot(660, y, col=POS, fill=REDFILL))
    f.append(dot(694, y, col=POS, fill=REDFILL))
    f.append(text(560, y + 52, "1 зайшло, 2 вийшло — агрегат переоцінений",
                  size=13, color=POS, bold=True))

    # доріжка 3 — БЕЗЛАД
    y = 380
    f.append(text(88, y + 4, "БЕЗЛАД", size=15, color=POS, bold=True))
    for cx, lab in ((200, "1"), (234, "2"), (268, "3")):
        f.append(dot(cx, y, label=lab))
    f.append(arrow(292, y, 402, y, color=INK, sw=1.8))
    f.append(stage(458, y))
    f.append(arrow(514, y, 624, y, color=INK, sw=1.8))
    for cx, lab in ((650, "1"), (684, "3"), (718, "2")):
        f.append(dot(cx, y, col=POS, fill=REDFILL, label=lab))
    f.append(text(560, y + 52, "порядок 1, 3, 2 — стан суперечить сам собі",
                  size=13, color=POS, bold=True))

    render(os.path.join(IMG, "three-breaks.svg"), W, H, *f,
           title="Три способи, якими рветься консистентність")


# ───────── Фіг. 3: ефективно-один-раз ─────────
def fig_effectively_once():
    W, H = 1040, 450
    f = []

    def event(cx, cy, col, fill):
        return (circle(cx, cy, 16, fill=fill, stroke=col, sw=1.8) +
                text(cx, cy + 5, "0.4", size=12, color=INK, bold=True))

    # ── доріжка A: наївно ──
    yA = 148
    f.append(text(70, 92, "Наївно:  kwh += 0.4", size=15, color=POS,
                  bold=True, anchor="start"))
    f.append(event(205, yA, POS, REDFILL))
    f.append(arrow(225, yA, 322, yA, color=INK, sw=1.9))
    f.append(fitbox(322, yA - 22, 120, 44, "kwh = 0.4",
                    size=14, fill=FILL, stroke=MUTED, bold=True))
    f.append(text(548, yA - 30, "повтор тієї самої", size=11, color=POS, bold=True))
    f.append(arrow(448, yA, 560, yA, color=POS, sw=1.9))
    f.append(fitbox(566, yA - 22, 150, 44, "kwh = 0.8",
                    size=14, fill=REDFILL, stroke=POS, bold=True))
    f.append(text(736, yA + 5, "дубль подвоїв  ✗", size=13, color=POS,
                  bold=True, anchor="start"))

    # ── доріжка B: ідемпотентно ──
    yB = 300
    f.append(text(70, 244, "Ідемпотентно:  upsert за ключем (meter, ts)",
                  size=15, color=FIELD, bold=True, anchor="start"))
    f.append(event(205, yB, FIELD, GREENFILL))
    f.append(arrow(225, yB, 322, yB, color=INK, sw=1.9))
    f.append(fitbox(322, yB - 22, 178, 44, "(meter, ts) = 0.4",
                    size=13, fill=FILL, stroke=MUTED, bold=True))
    f.append(text(560, yB - 30, "повтор тієї самої", size=11, color=FIELD, bold=True))
    f.append(arrow(506, yB, 578, yB, color=FIELD, sw=1.9))
    f.append(fitbox(584, yB - 22, 178, 44, "(meter, ts) = 0.4",
                    size=13, fill=GREENFILL, stroke=FIELD, bold=True))
    f.append(text(778, yB + 5, "дубль розчинився  ✓", size=13, color=FIELD,
                  bold=True, anchor="start"))

    # ── висновок унизу ──
    f.append(fitbox(280, 396, 480, 40,
                    "«щонайменше раз» + ідемпотентно = ефективно один раз",
                    size=14, fill=FILL, stroke=INK, bold=True, sw=2))

    render(os.path.join(IMG, "effectively-once.svg"), W, H, *f,
           title="Той самий подвоєний факт крізь дві ланки")


# ───────── Фіг. 4: звірка як петля ─────────
def fig_reconcile_loop():
    W, H = 940, 450
    f = []

    # джерело (ліворуч) і похідне (праворуч)
    b, _, _ = textbox(160, 100, "Джерело\nсирі факти", size=13, bold=True,
                      fill=FILL, stroke=INK, sw=2)
    f.append(b)
    b, _, _ = textbox(770, 100, "Похідне\nагрегат", size=13, bold=True,
                      fill=GREENFILL, stroke=FIELD, sw=2)
    f.append(b)

    # контрольні тоталі
    b, _, _ = textbox(160, 205, "контрольний\nтоталь S", size=12, fill="#eef2f6")
    f.append(b)
    b, _, _ = textbox(770, 205, "контрольний\nтоталь D", size=12, fill="#eef2f6")
    f.append(b)
    f.append(arrow(160, 132, 160, 176, color=INK, sw=1.8))
    f.append(arrow(770, 132, 770, 176, color=INK, sw=1.8))

    # ромб порівняння (як рамка з товстим контуром)
    f.append(fitbox(400, 185, 140, 56, "S = D ?", size=17,
                    fill="#fff8e8", stroke="#c9a93b", bold=True, sw=2.2))
    f.append(arrow(232, 213, 398, 213, color=INK, sw=1.9))
    f.append(arrow(698, 213, 542, 213, color=INK, sw=1.9))

    # гілка «так» — дрейфу нема
    f.append(arrow(430, 241, 320, 316, color=FIELD, sw=2.1))
    f.append(text(352, 282, "так", size=13, color=FIELD, bold=True))
    f.append(fitbox(190, 318, 230, 50, "дрейфу нема — спимо спокійно",
                    size=13, fill=GREENFILL, stroke=FIELD, bold=True))

    # гілка «ні» — дрейф → перерахунок
    f.append(arrow(510, 241, 650, 316, color=POS, sw=2.1))
    f.append(text(560, 282, "ні — дрейф", size=13, color=POS, bold=True))
    f.append(fitbox(560, 318, 230, 50, "перерахувати ланку",
                    size=13, fill=REDFILL, stroke=POS, bold=True))

    # петля назад у похідне
    f.append(line(790, 318, 875, 318, color=POS, sw=1.7))
    f.append(line(875, 318, 875, 100, color=POS, sw=1.7))
    f.append(arrow(875, 100, 838, 100, color=POS, sw=1.7))
    f.append(text(884, 210, "перерахунок", size=11, color=POS,
                  bold=True, anchor="middle"))

    # девіз
    f.append(text(W / 2, 420,
                  "звірка не заважає дрейфу — вона ловить його раніше за клієнта",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "reconcile-loop.svg"), W, H, *f,
           title="Довіряй, але звіряй: контрольні тоталі джерела й похідного")


# ───────── Фіг. 5 (вставка hist): Lambda проти Kappa ─────────
def fig_lambda_kappa():
    W, H = 1080, 520
    f = []
    divx = 540
    f.append(line(divx, 62, divx, 500, color=MUTED, sw=1.2, dash="4 6"))

    # ── Панель A: Lambda (два шари) ──
    f.append(text(275, 56, "Lambda — Нейтан Марц, 2011", size=15, bold=True))
    src, sw_, _ = textbox(102, 250, "потік\nподій", size=13, bold=True,
                          fill=FILL, stroke=INK, sw=2)
    f.append(src)
    spd, spw, _ = textbox(300, 150, "швидкісний шар\nреальний час,\nприблизно",
                          size=12, fill="#fff8e8", stroke="#c9a93b", sw=1.6)
    f.append(spd)
    bat, baw, _ = textbox(300, 358, "батч-шар\nусі дані, точно,\nперерахунок з нуля",
                          size=12, fill=GREENFILL, stroke=FIELD, sw=1.6)
    f.append(bat)
    srv, srw, _ = textbox(472, 254, "обслуговчий\nшар", size=12, bold=True,
                          fill=FILL, stroke=MUTED, sw=1.6)
    f.append(srv)
    f.append(arrow(102 + sw_ / 2, 236, 300 - spw / 2 - 6, 166, color=INK, sw=1.8))
    f.append(arrow(102 + sw_ / 2, 264, 300 - baw / 2 - 6, 344, color=INK, sw=1.8))
    f.append(arrow(300 + spw / 2 + 6, 160, 472 - srw / 2 - 6, 242, color="#c9a93b", sw=1.9))
    f.append(arrow(300 + baw / 2 + 6, 350, 472 - srw / 2 - 6, 268, color=FIELD, sw=1.9))
    f.append(text(275, 470, "той самий алгоритм пишеться двічі — і батч, і швидкісний",
                  size=12.5, color=POS, bold=True))

    # ── Панель B: Kappa (один журнал) ──
    f.append(text(800, 56, "Kappa — Джей Крепс, 2014", size=15, bold=True))
    src2, sw2, _ = textbox(628, 214, "потік\nподій", size=13, bold=True,
                           fill=FILL, stroke=INK, sw=2)
    f.append(src2)
    log, lgw, _ = textbox(792, 214, "незмінний журнал\n(Kafka)", size=12, bold=True,
                          fill="#eef2f6", stroke=INK, sw=1.8)
    f.append(log)
    prc, prw, _ = textbox(962, 214, "потоковий\nшар", size=12,
                          fill=GREENFILL, stroke=FIELD, sw=1.6)
    f.append(prc)
    srv2, _, _ = textbox(962, 372, "обслуговчий\nшар", size=12, bold=True,
                         fill=FILL, stroke=MUTED, sw=1.6)
    f.append(srv2)
    f.append(arrow(628 + sw2 / 2 + 5, 214, 792 - lgw / 2 - 5, 214, color=INK, sw=1.8))
    f.append(arrow(792 + lgw / 2 + 5, 214, 962 - prw / 2 - 5, 214, color=FIELD, sw=1.8))
    f.append(arrow(962, 214 + 26, 962, 372 - 26, color=INK, sw=1.8))
    # петля перечитування: журнал → нагору → над потоковим шаром → вниз
    ry = 118
    f.append(line(792, 214 - 26, 792, ry, color="#c9a93b", sw=1.7))
    f.append(line(792, ry, 962, ry, color="#c9a93b", sw=1.7))
    f.append(arrow(962, ry, 962, 214 - 26, color="#c9a93b", sw=1.7))
    f.append(text(877, ry - 9, "перечитати журнал з початку", size=11,
                  color="#b8860b", bold=True))
    f.append(text(800, 470, "один шар, один код; перерахунок = перечитати журнал",
                  size=12.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "lambda-vs-kappa.svg"), W, H, *f,
           title="Дві архітектури руху даних")


# ───────── Фіг. 6 (вставка hist): родовід «ефективно один раз» ─────────
def fig_eo_lineage():
    W, H = 1040, 350
    f = []
    y0 = 150
    f.append(line(150, y0, 890, y0, color=MUTED, sw=2))
    f.append(arrow(232, y0, 486, y0, color=INK, sw=1.6))
    f.append(arrow(554, y0, 808, y0, color=INK, sw=1.6))
    nodes = [
        (200, "2011", "Нейтан Марц", "Lambda",
         "блог «How to beat\nthe CAP theorem»\nдва шари: точність\n+ реальний час"),
        (520, "2014", "Джей Крепс", "Kappa",
         "«Questioning the\nLambda Architecture»\nодин журнал —\nперечитати й\nперерахувати"),
        (840, "2017", "Kafka 0.11", "EOS",
         "ідемпотентність\n+ транзакції\n→ «ефективно\nодин раз»"),
    ]
    for x, yr, who, ttl, desc in nodes:
        f.append(text(x, 86, who, size=14, bold=True, color=INK))
        f.append(text(x, 106, ttl, size=13, bold=True, color=FIELD))
        f.append(circle(x, y0, 27, fill="#fff8e8", stroke="#c9a93b", sw=2.4))
        f.append(text(x, y0 + 6, yr, size=15, bold=True))
        f.append(fitbox(x - 140, 200, 280, 120, desc, size=12.5,
                        fill=FILL, stroke=MUTED))
    render(os.path.join(IMG, "eo-lineage.svg"), W, H, *f,
           title="Родовід «ефективно один раз»")


# ───────── Фіг. 7 (вставка proj): вікно лага й звірка партицій ─────────
def fig_reconcile_window():
    W, H = 1060, 470
    f = []

    # запечатані дні (звіряємо) — центри колонок
    sealed = [
        (130, "06-лип", "288", "12.41", "288", "12.41", True),
        (270, "07-лип", "288", "11.90", "288", "11.90", True),
        (410, "08-лип", "288", "12.42", "287", "12.02", False),  # дрейф
        (550, "09-лип", "288", "12.44", "288", "12.44", True),
    ]
    yS, yD = 92, 148     # рядки S і D
    bw, bh = 116, 42

    for cx, day, sn, ss, dn, ds, ok in sealed:
        f.append(text(cx, 66, day, size=13, color=INK, bold=True))
        # рядок джерела S
        f.append(fitbox(cx - bw / 2, yS, bw, bh, "S:  n=%s\nΣ=%s" % (sn, ss),
                        size=12.5, fill=FILL, stroke=MUTED, bold=True))
        # рядок похідного D
        dfill = GREENFILL if ok else REDFILL
        dstroke = FIELD if ok else POS
        f.append(fitbox(cx - bw / 2, yD, bw, bh, "D:  n=%s\nΣ=%s" % (dn, ds),
                        size=12.5, fill=dfill, stroke=dstroke, bold=True))
        # присуд — лише для збіжних; у дрейфової колонки вердикт несуть стрілки
        if ok:
            f.append(text(cx, yD + bh + 22, "= ✓", size=15, color=FIELD, bold=True))

    # дрейфова колонка 08-лип → перерахунок і назад
    dcx = 410
    f.append(arrow(dcx - 14, yD + bh, dcx - 14, 288, color=POS, sw=2.0))
    f.append(text(dcx - 62, 258, "дрейф", size=11.5, color=POS, bold=True))
    f.append(fitbox(dcx - 132, 290, 264, 48,
                    "ідемпотентний перерахунок\nпартиції (home, day) із reading",
                    size=12.5, fill="#fff8e8", stroke="#c9a93b", bold=True))
    f.append(arrow(dcx + 14, 288, dcx + 14, yD + bh, color=FIELD, sw=2.0))
    f.append(text(dcx + 66, 258, "оновлює D", size=11.5, color=FIELD, bold=True))

    # межа-watermark
    wx = 630
    f.append(line(wx, 54, wx, 210, color=MUTED, sw=1.6, dash="5 6"))
    f.append(text(wx, 48, "watermark = сьогодні − лаг", size=12,
                  color=MUTED, bold=True))

    # відкрите вікно (не звіряємо)
    f.append(rect(wx + 18, 56, 402, 150, fill="#f1f1f4", stroke=MUTED,
                  sw=1.2, rx=8))
    for cx, day in ((730, "10-лип"), (880, "11-лип · сьогодні")):
        f.append(text(cx, 66, day, size=13, color=MUTED, bold=True))
        f.append(fitbox(cx - bw / 2, yS + 8, bw, bh + 20, "ще\nдоливається",
                        size=12.5, fill="#e9e9ee", stroke=MUTED, bold=True))
    f.append(text(wx + 219, 228, "вікно лага: партиції ще неповні — НЕ звіряємо",
                  size=12.5, color=MUTED, bold=True))

    # девіз
    f.append(text(W / 2, 452,
                  "звіряємо лише запечатане; дрейф партиції гоїмо ідемпотентним "
                  "перерахунком, що не подвоює", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "reconcile-window.svg"), W, H, *f,
           title="Звірка по партиціях за межею вікна лага")


# ───────── Фіг. 8 (вставка proj): коли SUM і COUNT брешуть ─────────
def fig_sum_lies():
    W, H = 1000, 430
    f = []

    # джерело — три факти
    b, _, _ = textbox(190, 168,
                      "Джерело (партиція 42 / 09-лип)\n"
                      "08:00   0.4\n08:05   0.3\n08:10   0.5",
                      size=13, fill=FILL, stroke=INK, sw=1.8, bold=False)
    f.append(b)
    # похідне — ті самі рядки, два значення переставлені
    b, _, _ = textbox(810, 168,
                      "Похідне D (те саме вікно)\n"
                      "08:00   0.4\n08:05   0.5  ⇦ підмінено\n08:10   0.3  ⇦ підмінено",
                      size=13, fill=GREENFILL, stroke=FIELD, sw=1.8, bold=False)
    f.append(b)

    # три рядки порівняння в центрі
    rows = [
        (150, "COUNT", "3", "3", True, "="),
        (215, "Σ kwh", "1.2", "1.2", True, "="),
        (280, "hash(⟨ts,kwh⟩)", "9c…a1", "9c…f7", False, "≠"),
    ]
    for y, lab, sv, dv, ok, op in rows:
        col = FIELD if ok else POS
        f.append(text(500, y - 20, lab, size=13, color=INK, bold=True))
        f.append(fitbox(420, y - 8, 66, 34, sv, size=13, fill=FILL,
                        stroke=MUTED, bold=True))
        f.append(text(500, y + 12, op, size=16, color=col, bold=True))
        f.append(fitbox(514, y - 8, 66, 34, dv, size=13,
                        fill=(GREENFILL if ok else REDFILL),
                        stroke=col, bold=True))
        f.append(text(614, y + 12, "✓" if ok else "✗", size=16,
                      color=col, bold=True))

    # висновок
    f.append(fitbox(150, 340, 700, 56,
                    "COUNT і Σ збіглися випадково — дві помилки скомпенсували одна одну.\n"
                    "Контентний хеш відсортованих фактів ловить підміну, якої сума не бачить.",
                    size=13, fill="#fff8e8", stroke="#c9a93b", bold=True, sw=2))

    render(os.path.join(IMG, "sum-lies.svg"), W, H, *f,
           title="Коли COUNT + SUM недостатньо")


if __name__ == "__main__":
    fig_fact_fanout()
    fig_three_breaks()
    fig_effectively_once()
    fig_reconcile_loop()
    fig_lambda_kappa()
    fig_eo_lineage()
    fig_reconcile_window()
    fig_sum_lies()
    print("OK: fact-fanout.svg, three-breaks.svg, effectively-once.svg, "
          "reconcile-loop.svg, lambda-vs-kappa.svg, eo-lineage.svg, "
          "reconcile-window.svg, sum-lies.svg")
