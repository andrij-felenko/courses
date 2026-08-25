# -*- coding: utf-8 -*-
"""Фігури до історичної вставки «hist-reed-switch.md» (тема KY-021).
Окремий файл, щоб не заважати основному figs.py.
Запуск:  python figs_hist.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Родовід геркона: ідея → запаяна колба → серія (різні люди, різна доказовість) ─
def fig_reed_lineage():
    W, H = 1240, 590
    f = [text(W / 2, 34, "Родовід геркона: три різні кроки, різні люди, різна доказовість",
              size=16, bold=True)]

    xs = [220, 620, 1020]
    heads = ["КРОК 1 · ІДЕЯ\nмагнітний контакт",
             "КРОК 2 · РЕАЛІЗАЦІЯ\nконтакт у запаяній колбі",
             "КРОК 3 · СЕРІЯ\nмасовий випуск"]
    for x, lab in zip(xs, heads):
        # короткий стуб-маркер доріжки ПІД заголовком (не крізь картки нижче)
        f.append(line(x, 104, x, 126, color=MUTED, sw=1.2, dash="5,7"))
        b, _, _ = textbox(x, 78, lab, size=11.5, bold=True, fill=FILL, stroke=INK)
        f.append(b)

    # стрілки між етапами (ведемо повз написи, по середній лінії)
    midy = 250
    f.append(arrow(xs[0] + 150, midy, xs[1] - 150, midy, color=INK, sw=2.0))
    f.append(arrow(xs[1] + 150, midy, xs[2] - 150, midy, color=INK, sw=2.0))

    # КРОК 1 — Коваленков (спірно)
    b, _, _ = textbox(xs[0], 250,
                      "В. Коваленков\n(V. Kovalenkov)\nПетербург, ~1922\nконтакт БЕЗ колби\n· спірно, слабко доведено ·",
                      size=10.5, fill="#fff7e6", stroke=POS)
    f.append(b)

    # КРОК 2 — дві незалежні заявки того самого 1936-го
    b, _, _ = textbox(xs[1], 196,
                      "В. Елвуд (W. B. Ellwood)\nBell Labs, США, 1936\nзапаяв контакт у колбу\nпатент US 2 264 746\n(подано 1940 · видано 1941)",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(xs[1], 350,
                      "С. Улитовський\n(S. Ulitovskii)\nЛенінград, 1936\nта сама ідея — незалежно\n· теж слабко доведено ·",
                      size=10.5, fill="#fff7e6", stroke=POS)
    f.append(b)

    # КРОК 3 — серія
    b, _, _ = textbox(xs[2], 250,
                      "Bell Labs\n~1938 — проба в коаксіалі\n1940 — перша партія\n· задокументовано ·",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # легенда кольорів унизу
    b, _, _ = textbox(W / 2, 548,
                      "зелене — задокументовано (патент, серійна партія);   "
                      "жовте — правдоподібно, але слабко доведено (без первинних джерел)",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "reed-lineage.svg"), W, H, *f)


# ── Драбина доказовості тверджень «хто перший» ─────────────────────────────────
def fig_evidence_ladder():
    W, H = 1000, 540
    f = [text(W / 2, 34, "Одному твердженню віриш, іншому — ні: драбина доказовості",
              size=16, bold=True)]

    rungs = [
        ("Патент US 2 264 746 (Елвуд, 1941)",
         "первинний документ: дата, ім'я, серійний номер, креслення",
         "#eef6ef", FIELD, "ФАКТ"),
        ("Перша серійна партія Bell, 1940",
         "збігається в кількох незалежних джерелах",
         "#eef6ef", FIELD, "ФАКТ"),
        ("Коваленков придумав магнітний контакт, 1922",
         "живе у фаховій літературі; у його ж біографії — ані слова",
         "#fff7e6", POS, "СПІРНО"),
        ("«Авторське свідоцтво СРСР № 466, 1922»",
         "рік і тип документа не сходяться з історією таких свідоцтв",
         "#fdecea", POS, "СУМНІВНО"),
        ("«Геркон — суто російський винахід»",
         "стягує чотирьох різних людей у гасло; перевірки не витримує",
         "#fdecea", POS, "МІФ"),
    ]
    y = 80
    rh = 82
    gap = 8
    for i, (title_, note, fillc, strokec, tag) in enumerate(rungs):
        yy = y + i * (rh + gap)
        f.append(rect(120, yy, 640, rh, fill=fillc, stroke=strokec, sw=1.6, rx=8))
        f.append(text(142, yy + 32, title_, size=12.5, bold=True, color=INK, anchor="start"))
        f.append(text(142, yy + 56, note, size=10.5, color=MUTED, anchor="start"))
        b, _, _ = textbox(850, yy + rh / 2, tag, size=11, bold=True,
                          fill=BG, stroke=strokec, min_w=120)
        f.append(b)

    render(os.path.join(IMG, "reed-evidence.svg"), W, H, *f)


if __name__ == "__main__":
    fig_reed_lineage()
    fig_evidence_ladder()
    print("hist figs done ->", IMG)
