# -*- coding: utf-8 -*-
"""Фігури до статті «Типи як дизайн». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_type_is_a_set():
    """Тип = множина можливих значень. Показуємо, як звуження множини
    викидає незаконні стани ЗА межу типу — їх стає неможливо записати."""
    W, H = 760, 400
    frags = []

    # Ліворуч: широкий тип (int) — уся площина, легальних лише жменя
    lx, ly, lw, lh = 60, 90, 300, 250
    frags.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(lx + lw / 2, ly - 16, "int для «місяць»", size=15, bold=True))
    frags.append(text(lx + lw / 2, ly + 26, "усі 4 млрд значень — легальні",
                      size=12, color=MUTED))
    # маленька зелена цятка легального
    frags.append(circle(lx + lw / 2, ly + 150, 30, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(lx + lw / 2, ly + 154, "1..12", size=13, color=FIELD, bold=True))
    frags.append(text(lx + lw / 2, ly + 215, "−7, 0, 13, 999 …", size=12, color=POS))
    frags.append(text(lx + lw / 2, ly + 234, "теж «проходять»", size=11, color=POS))

    # Праворуч: вузький тип (Month) — множина = рівно легальні значення
    rx, ry, rw, rh = 440, 150, 260, 130
    frags.append(rect(rx, ry, rw, rh, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(rx + rw / 2, ry - 16, "enum Month { Jan..Dec }", size=15, bold=True))
    frags.append(text(rx + rw / 2, ry + rh / 2 - 6, "рівно 12 значень", size=13, color=FIELD, bold=True))
    frags.append(text(rx + rw / 2, ry + rh / 2 + 16, "інше НЕ записати", size=12, color=INK))

    # стрілка «звузити тип»
    frags.append(arrow(lx + lw + 12, 215, rx - 12, 215, color=INK, sw=2))
    b, bw, bh = textbox((lx + lw + rx) / 2, 185, "звузити\nтип", size=12, bold=True,
                        fill=BG, stroke=INK)
    frags.append(b)

    render(os.path.join(IMG, "type-is-a-set.svg"), W, H, *frags)


def fig_product_vs_sum():
    """Добуток (усі поля разом = И) проти суми (рівно один випадок = АБО).
    Ліворуч — «мішок nullable-полів» (хибно), праворуч — сума-стан (чесно)."""
    W, H = 780, 430
    frags = []

    # Ліворуч: struct із трьома nullable-полями — 8 комбінацій, легальних 3
    lx, lw = 50, 320
    frags.append(text(lx + lw / 2, 40, "Мішок полів (добуток): И", size=15, bold=True))
    frags.append(text(lx + lw / 2, 62, "loading × error × data — 8 комбінацій",
                      size=12, color=MUTED))
    rows = [
        ("loading=true,  error=?,  data=?", POS, "суперечка"),
        ("loading=false, error=set, data=set", POS, "і те, і те?"),
        ("loading=false, error=none, data=none", POS, "порожньо"),
        ("loading=true,  error=none, data=none", FIELD, "чекаємо"),
    ]
    y = 92
    for txt, col, note in rows:
        frags.append(rect(lx, y, lw, 44, fill="#fdecea" if col == POS else "#eafaf1",
                          stroke=col, sw=1.5))
        frags.append(text(lx + 12, y + 20, txt, size=12, color=INK, anchor="start"))
        frags.append(text(lx + 12, y + 37, note, size=11, color=col, anchor="start"))
        y += 54

    # Праворуч: sum type — рівно один випадок активний
    rx, rw = 470, 260
    frags.append(text(rx + rw / 2, 40, "Стан (сума): АБО", size=15, bold=True))
    frags.append(text(rx + rw / 2, 62, "рівно один випадок живий", size=12, color=MUTED))
    cases = [
        ("Loading", "— без полів"),
        ("Error(msg)", "— лише текст"),
        ("Ready(data)", "— лише дані"),
    ]
    y = 100
    for name, tail in cases:
        frags.append(rect(rx, y, rw, 56, fill="#eafaf1", stroke=FIELD, sw=1.8))
        frags.append(text(rx + rw / 2, y + 24, name, size=15, bold=True, color=INK))
        frags.append(text(rx + rw / 2, y + 44, tail, size=12, color=MUTED))
        y += 74

    # роздільник-думка між колонками
    frags.append(line((lx + lw + rx) / 2, 90, (lx + lw + rx) / 2, 360,
                      color=MUTED, sw=1, dash="4 4"))

    render(os.path.join(IMG, "product-vs-sum.svg"), W, H, *frags)


def fig_null_lineage():
    """Нитка ідеї «типи проти незаконних станів»: від дірки (null, 1965)
    до гасла й реалізацій. Вертикальний хребет; кожна подія — картка."""
    W, H = 760, 520
    frags = []

    frags.append(text(W / 2, 34, "Нитка ідеї: від дірки до гасла",
                      size=16, bold=True))

    # вертикальний хребет часу
    spine_x = 150
    top, bot = 70, 480
    frags.append(line(spine_x, top, spine_x, bot, color=MUTED, sw=2))

    # події: (рік, підпис-ліворуч, заголовок, суть, колір-крапки)
    events = [
        ("1965", "ALGOL W", "null пробиває будь-який тип",
         "Гоар додає null-посилання — бо легко реалізувати", POS),
        ("2009", "QCon London", "«мільярдна помилка»",
         "Гоар публічно кається за той null", POS),
        ("2010", "Effective ML", "make illegal states unrepresentable",
         "Мінскі кристалізує гасло на прикладі OCaml", FIELD),
        ("2016", "elm-conf", "Making Impossible States Impossible",
         "Фелдман несе ідею в широкий фронтенд (Elm)", FIELD),
        ("2019", "Haskell-есей", "parse, don't validate",
         "Кінг робить гасло робочим методом", FIELD),
    ]

    n = len(events)
    y0, dy = 92, (bot - 92 - 20) / (n - 1)
    card_x, card_w = 190, 540
    card_h = 62
    for i, (year, where, head, body, dot) in enumerate(events):
        cy = y0 + i * dy
        # крапка на хребті
        frags.append(circle(spine_x, cy, 8, fill=("#fdecea" if dot == POS else "#eafaf1"),
                            stroke=dot, sw=2.5))
        # рік ліворуч від хребта
        frags.append(text(spine_x - 22, cy - 8, year, size=15, bold=True,
                          color=dot, anchor="end"))
        frags.append(text(spine_x - 22, cy + 10, where, size=11, color=MUTED,
                          anchor="end"))
        # коротка поличка від хребта до картки
        frags.append(line(spine_x + 8, cy, card_x, cy, color=MUTED, sw=1.2))
        # картка з заголовком і суттю
        frags.append(rect(card_x, cy - card_h / 2, card_w, card_h,
                          fill=("#fdecea" if dot == POS else "#eafaf1"),
                          stroke=dot, sw=1.6))
        frags.append(text(card_x + 16, cy - 8, head, size=14, bold=True,
                          color=INK, anchor="start"))
        frags.append(text(card_x + 16, cy + 14, body, size=12, color=MUTED,
                          anchor="start"))

    render(os.path.join(IMG, "null-lineage.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_type_is_a_set()
    fig_product_vs_sum()
    fig_null_lineage()
    print("ok")
