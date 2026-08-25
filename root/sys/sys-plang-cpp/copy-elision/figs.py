# -*- coding: utf-8 -*-
"""Фігури до теми «Усунення копій і гарантований RVO»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Куди дівається повернений об'єкт ─────────────────────────────────────
def fig_return_slot():
    W, H = 960, 450
    parts = []

    parts.append(text(W / 2, 62, "Наївне читання тексту: три об'єкти, два копіювання",
                      size=15, bold=True, color=MUTED))

    cy = 130
    b1, w1, _ = textbox(170, cy, ["локальний об'єкт", "у кадрі функції"], size=14)
    b2, w2, _ = textbox(480, cy, ["повернене", "значення"], size=14)
    b3, w3, _ = textbox(790, cy, ["змінна в того,", "хто викликав"], size=14)
    parts += [b1, b2, b3]

    parts.append(arrow(170 + w1 / 2 + 12, cy, 480 - w2 / 2 - 12, cy))
    parts.append(arrow(480 + w2 / 2 + 12, cy, 790 - w3 / 2 - 12, cy))
    parts.append(text((170 + w1 / 2 + 480 - w2 / 2) / 2, cy - 20, "копія", size=13, color=POS))
    parts.append(text((480 + w2 / 2 + 790 - w3 / 2) / 2, cy - 20, "копія", size=13, color=POS))

    parts.append(line(40, 205, W - 40, 205, color=MUTED, sw=1, dash="6,6"))

    parts.append(text(W / 2, 245, "Як воно влаштоване насправді: комірка одна",
                      size=15, bold=True, color=MUTED))

    cy2 = 340
    l1, wl, _ = textbox(200, cy2, ["кадр функції:", "будує об'єкт за покажчиком"], size=14)
    r1, wr, _ = textbox(720, cy2, ["комірка під результат", "= змінна в того, хто викликав",
                                   "(одна й та сама пам'ять)"], size=14,
                        fill="#eafaf1", stroke=FIELD)
    parts += [l1, r1]

    x_from = 200 + wl / 2 + 14
    x_to = 720 - wr / 2 - 14
    parts.append(arrow(x_from, cy2, x_to, cy2, color=FIELD))
    parts.append(mtext((x_from + x_to) / 2, cy2 - 34,
                       ["прихований покажчик", "на комірку результату"],
                       size=13, color=FIELD, lh=1.25))

    render(os.path.join(IMG, 'return-slot.svg'), W, H, *parts,
           title="Куди дівається об'єкт, повернений за значенням")


# ── 2. Дві моделі prvalue ───────────────────────────────────────────────────
def fig_prvalue_model():
    W, H = 940, 420
    parts = []
    parts.append(line(470, 56, 470, 392, color=MUTED, sw=1, dash="5,5"))

    parts.append(text(235, 74, "Модель до C++17", size=15, bold=True))
    parts.append(text(705, 74, "Модель з C++17", size=15, bold=True))
    parts.append(text(235, 110, "T x = T();", size=15, color=NEG))
    parts.append(text(705, 110, "T x = T();", size=15, color=NEG))

    lb, _, lh = textbox(235, 170, ["тимчасовий об'єкт T()"], size=14)
    parts.append(lb)
    parts.append(arrow(235, 170 + lh / 2 + 8, 235, 244))
    parts.append(text(256, 214, "копія або переміщення", size=13, color=POS, anchor="start"))
    lb2, _, _ = textbox(235, 272, ["об'єкт x"], size=14, min_w=170)
    parts.append(lb2)
    parts.append(mtext(235, 340, ["копію дозволено усунути,", "але конструктор мусить існувати"],
                       size=13, color=MUTED, lh=1.3))

    rb, _, rh = textbox(705, 170, ["prvalue T() —", "рецепт ініціалізації"], size=14,
                        fill="#eafaf1", stroke=FIELD)
    parts.append(rb)
    parts.append(arrow(705, 170 + rh / 2 + 8, 705, 244, color=FIELD))
    parts.append(text(726, 214, "матеріалізація", size=13, color=FIELD, anchor="start"))
    rb2, _, _ = textbox(705, 272, ["об'єкт x — єдиний"], size=14, fill="#eafaf1", stroke=FIELD)
    parts.append(rb2)
    parts.append(mtext(705, 340, ["усувати нічого:", "другого об'єкта не було"],
                       size=13, color=MUTED, lh=1.3))

    render(os.path.join(IMG, 'prvalue-model.svg'), W, H, *parts,
           title="Що змінив C++17: не оптимізатор, а означення prvalue")


# ── 3. Драбина: що станеться з поверненим об'єктом ──────────────────────────
def fig_ladder():
    W, H = 980, 470
    parts = []
    parts.append(text(W / 2, 58, "згори вниз — від найдешевшого до найдорожчого",
                      size=13, color=MUTED))

    rows = [
        (["Гарантовано мовою (з C++17)", "нічого усувати не треба"],
         "return T(args);   T x = make();", "1 об'єкт", "#eafaf1", FIELD),
        (["Дозволено, але не обіцяно", "NRVO — воля компілятора"],
         "T a;  ...  return a;", "1 об'єкт", FILL, LINE),
        (["Неявне переміщення", "запасний хід, коли NRVO не вийшов"],
         "T a, b;  if (c) return a;  return b;", "2 об'єкти", FILL, LINE),
        (["Справжнє копіювання", "усе інше"],
         "return field_;   const T a; return a;", "2 об'єкти", "#fdecea", POS),
    ]

    x1, w1 = 30, 340
    x2, w2 = 390, 420
    x3, w3 = 830, 120
    y, rh, gap = 78, 78, 18
    for left, mid, right, fill, stroke in rows:
        parts.append(fitbox(x1, y, w1, rh, left, size=14, fill=fill, stroke=stroke))
        parts.append(fitbox(x2, y, w2, rh, [mid], size=13, fill="#f8f9fb", stroke=MUTED))
        parts.append(fitbox(x3, y, w3, rh, [right], size=13, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(IMG, 'ladder.svg'), W, H, *parts,
           title="Що фактично станеться з поверненим об'єктом")


# ── 4. Хронологія: від дозволу до обіцянки (вставка hist) ───────────────────
def fig_elision_timeline():
    rows = [
        ("1991", ["Zortech C++ Волтера Брайта: усунення копії для іменованої змінної",
                  "реалізовано без обіцяного розширення мови"]),
        ("1998", ["C++98, 12.8/15 — перший дозвіл: копію вільно не робити,",
                  "«навіть якщо конструктор чи деструктор мають побічні дії»"]),
        ("2004", ["Стенлі Ліппман публічно формулює головну ваду дозволу:",
                  "за текстом програми неможливо дізнатися, чи він застосований"]),
        ("2011", ["C++11 — неявне переміщення як запасний хід: коли усунути не вийшло,",
                  "копіювання замінюють переміщенням; об'єктів усе одно два"]),
        ("2015–16", ["P0135 Річарда Сміта: замість нового дозволу — переозначення prvalue.",
                     "R0 — вересень 2015, R1 — 20 червня 2016, ухвалено в Оулу → C++17"]),
        ("2020–21", ["P2025 Антона Жиліна: та сама гарантія для іменованої змінної.",
                     "Три редакції, статус «потребує доопрацювання», у стандарт не ввійшов"]),
    ]

    W = 1020
    x_year, w_year = 30, 150
    x_ev, w_ev = 200, 790
    rh, gap, y0 = 70, 16, 40
    H = y0 + len(rows) * (rh + gap) + 14

    parts = []
    y = y0
    for i, (year, lines) in enumerate(rows):
        if i < 4:
            fill, stroke = FILL, LINE
        elif i == 4:
            fill, stroke = "#eafaf1", FIELD
        else:
            fill, stroke = "#fdecea", POS
        parts.append(fitbox(x_year, y, w_year, rh, [year], size=17, fill=fill, stroke=stroke))
        parts.append(fitbox(x_ev, y, w_ev, rh, lines, size=13, fill="#f8f9fb", stroke=MUTED))
        y += rh + gap

    render(os.path.join(IMG, 'elision-timeline.svg'), W, H, *parts,
           title="Від дозволу не копіювати до обіцянки, що копії немає")


if __name__ == '__main__':
    fig_return_slot()
    fig_prvalue_model()
    fig_ladder()
    fig_elision_timeline()
    print("ok")
