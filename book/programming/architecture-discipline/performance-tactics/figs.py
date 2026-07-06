# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: анатомія часу відгуку — робота + чекання ──────────────────────
def fig_anatomy():
    W, H = 900, 300
    frags = []

    # вісь часу
    x0, x1 = 90, W - 90
    y = 150
    band_h = 46

    # позначки початку й кінця
    frags.append(line(x0, y - 70, x0, y + 90, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(x1, y - 70, x1, y + 90, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(x0, y - 80, "подія прийшла", size=12, bold=True, color=INK, anchor="middle"))
    frags.append(text(x1, y - 80, "відповідь готова", size=12, bold=True, color=INK, anchor="middle"))

    # смуга часу відгуку: чергуються ділянки роботи (POS) і чекання (NEG)
    # частки в px (сума = x1-x0)
    total = x1 - x0
    segs = [
        ("робота", 0.16, POS, "#fdecea"),
        ("чекання", 0.30, NEG, "#eaf0fd"),
        ("робота", 0.12, POS, "#fdecea"),
        ("чекання", 0.28, NEG, "#eaf0fd"),
        ("робота", 0.14, POS, "#fdecea"),
    ]
    cx = x0
    for name, frac, col, fill in segs:
        w = total * frac
        frags.append(rect(cx, y - band_h / 2, w, band_h, fill=fill, stroke=col, sw=1.8, rx=4))
        frags.append(text(cx + w / 2, y + 5, name, size=11, bold=True, color=col, anchor="middle"))
        cx += w

    # дужка «час відгуку» під смугою
    by = y + band_h / 2 + 22
    frags.append(line(x0, by, x1, by, color=INK, sw=1.4))
    frags.append(line(x0, by - 6, x0, by + 6, color=INK, sw=1.4))
    frags.append(line(x1, by - 6, x1, by + 6, color=INK, sw=1.4))
    frags.append(text((x0 + x1) / 2, by + 22, "час відгуку", size=13, bold=True, color=INK, anchor="middle"))

    # легенда двох частин угорі, рознесена по боках — щоб не накрити смугу
    lb1, w1, h1 = textbox(x0 + 130, 44, "робота: рахуємо (процесор, пам'ять)",
                          size=12, fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    frags.append(lb1)
    lb2, w2, h2 = textbox(x1 - 150, 44, "чекання: стоїмо в черзі (заблокований час)",
                          size=12, fill="#eaf0fd", stroke=NEG, sw=1.6, pad=8)
    frags.append(lb2)

    render(os.path.join(IMG, 'response-anatomy.svg'), W, H, *frags,
           title="Час відгуку = робота + чекання")


# ── Фігура 2: дві родини тактик продуктивності ──────────────────────────────
def fig_tree():
    W, H = 940, 520
    frags = []

    # корінь
    root, rw, rh = textbox(W / 2, 62, "Скоротити час відгуку", size=16, bold=True,
                           fill="#f0f0f0", stroke=INK, sw=2, pad=14)
    frags.append(root)

    # дві родини — широкі колонки, з великим запасом між ними
    fam = [
        (W * 0.27, "Керувати попитом\n(менше РОБОТИ)", POS, "#fdecea", [
            "Ефективніший алгоритм",
            "Менше накладних витрат",
            "Рідші заміри / події",
            "Відкидати й пріоритезувати",
            "Обмежити час і чергу",
        ]),
        (W * 0.73, "Керувати ресурсами\n(менше ЧЕКАННЯ)", NEG, "#eaf0fd", [
            "Паралельність",
            "Кілька копій / кеш",
            "Більше ресурсу",
            "Розумний розклад",
        ]),
    ]

    top_y = 168
    for cx, head, col, hf, items in fam:
        # лінія від кореня до голови родини
        frags.append(line(W / 2, 62 + rh / 2, cx, top_y - 30, color=MUTED, sw=1.5))
        hb, hw, hh = textbox(cx, top_y, head, size=14, bold=True, fill=hf,
                             stroke=col, sw=2.2, pad=12, min_w=300)
        frags.append(hb)
        yy = top_y + hh / 2 + 26
        for it in items:
            box_w = 320
            frags.append(fitbox(cx - box_w / 2, yy, box_w, 40, it, size=13,
                                fill=FILL, stroke=col, sw=1.4))
            yy += 50

    render(os.path.join(IMG, 'tactic-tree.svg'), W, H, *frags,
           title="Дві родини тактик продуктивності")


# ── Фігура 3 (для вставки math): смуга роботи — послідовна + паралельна ──────
def fig_amdahl_band():
    W, H = 900, 470
    frags = []

    x0, x1 = 120, W - 120
    total = x1 - x0
    band_h = 52
    seq_frac = 0.30                      # послідовна частка (1-p)
    par_frac = 1.0 - seq_frac            # паралельна частка p
    seq_w = total * seq_frac

    # ── Ряд 1: один виконавець (s = 1) ──────────────────────────────────────
    y1 = 120
    frags.append(text(x0 - 24, y1 + 5, "s = 1", size=13, bold=True, color=INK, anchor="end"))
    frags.append(rect(x0, y1 - band_h / 2, seq_w, band_h,
                      fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    frags.append(text(x0 + seq_w / 2, y1 + 5, "послідовна (1−p)",
                      size=11, bold=True, color=NEG, anchor="middle"))
    frags.append(rect(x0 + seq_w, y1 - band_h / 2, total - seq_w, band_h,
                      fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    frags.append(text(x0 + seq_w + (total - seq_w) / 2, y1 + 5, "паралельна (p)",
                      size=11, bold=True, color=POS, anchor="middle"))

    # ── Ряд 2: багато виконавців (s велике) — паралельна частка стиснута ─────
    y2 = 300
    shrink = 0.24                        # p/s: паралельна майже вигризена
    par_w2 = (total - seq_w) * shrink
    frags.append(text(x0 - 24, y2 + 5, "s → ∞", size=13, bold=True, color=INK, anchor="end"))
    # послідовна — та сама ширина, нерухома
    frags.append(rect(x0, y2 - band_h / 2, seq_w, band_h,
                      fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    frags.append(text(x0 + seq_w / 2, y2 + 5, "послідовна (1−p)",
                      size=11, bold=True, color=NEG, anchor="middle"))
    # паралельна — стиснута до p/s
    frags.append(rect(x0 + seq_w, y2 - band_h / 2, par_w2, band_h,
                      fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    frags.append(text(x0 + seq_w + par_w2 / 2, y2 - band_h / 2 - 12, "p/s → 0",
                      size=11, bold=True, color=POS, anchor="middle"))

    # пунктирні напрямні: куди «сповзла» права межа паралельної частки
    old_end = x1
    new_end = x0 + seq_w + par_w2
    frags.append(line(old_end, y1 + band_h / 2, old_end, y2 - band_h / 2 - 30,
                      color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(new_end, y2 - band_h / 2, new_end, y2 + band_h / 2 + 34,
                      color=MUTED, sw=1.2, dash="4,4"))
    # дужка нового (коротшого) часу під рядом 2
    by = y2 + band_h / 2 + 30
    frags.append(line(x0, by, new_end, by, color=INK, sw=1.4))
    frags.append(line(x0, by - 6, x0, by + 6, color=INK, sw=1.4))
    frags.append(line(new_end, by - 6, new_end, by + 6, color=INK, sw=1.4))
    stub, sw_, sh_ = textbox((x0 + new_end) / 2, by + 30,
                             "новий час → (1−p): далі не стиснути",
                             size=12, bold=True, fill="#f0f0f0", stroke=INK, sw=1.6, pad=8)
    frags.append(stub)

    render(os.path.join(IMG, 'amdahl-band.svg'), W, H, *frags,
           title="Стелю ставить нерухома послідовна частка")


# ── Фігура 4 (для вставки hist): два числа з двох чужих кімнат ───────────────
def fig_two_rooms():
    W, H = 960, 480
    frags = []

    col_l = W * 0.27
    col_r = W * 0.73
    top = 92

    # заголовки двох «кімнат» — звідки прийшло кожне число
    hl, hlw, hlh = textbox(col_l, top, "1967 · конференція AFIPS\nсуперечка про суперкомп'ютери",
                           size=13, bold=True, fill="#fdecea", stroke=POS, sw=2, pad=11, min_w=360)
    hr, hrw, hrh = textbox(col_r, top, "1961 · дослідження операцій\nвиклик знайти виняток",
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, pad=11, min_w=360)
    frags.append(hl)
    frags.append(hr)

    # стос під кожною кімнатою: хто → що зробив → яке число лишив
    def stack(cx, col, rows, y0):
        yy = y0
        for txt in rows:
            frags.append(fitbox(cx - 185, yy, 370, 48, txt, size=12,
                                fill=FILL, stroke=col, sw=1.4))
            yy += 60
        return yy

    yL = stack(col_l, POS, [
        "Джин Амдал — фізик, архітектор System/360",
        "заперечив мрію про 64 процесори:\nчастина роботи неподільно послідовна",
        "стеля прискорення:  1 / (1 − p)",
    ], top + hlh / 2 + 22)

    yR = stack(col_r, NEG, [
        "Джон Літтл — докторант Філіпа Морса, MIT",
        "довів народну формулу черги\nяк теорему за загальних умов",
        "формула черги:  L = λ · W",
    ], top + hrh / 2 + 22)

    # спільний підсумок — одна широка смуга внизу, добре відділена від стосів
    yb = max(yL, yR) + 10
    sb, sbw, sbh = textbox(W / 2, yb + 24,
                           "у словник архітектора: Амдал — межа РОБОТИ (паралельність), Літтл — оцінка ЧЕКАННЯ (черга)",
                           size=13, bold=True, fill="#f0f0f0", stroke=INK, sw=2, pad=12, min_w=W - 90)
    # стрілки від обох стосів у підсумок — повз написи, до верхніх кутів смуги
    frags.append(line(col_l, yL - 14, W / 2 - sbw / 2 + 46, yb + 24 - sbh / 2, color=MUTED, sw=1.4))
    frags.append(line(col_r, yR - 14, W / 2 + sbw / 2 - 46, yb + 24 - sbh / 2, color=MUTED, sw=1.4))
    frags.append(sb)

    render(os.path.join(IMG, 'two-rooms.svg'), W, H, *frags,
           title="Два числа прийшли не з програмування")


if __name__ == "__main__":
    fig_anatomy()
    fig_tree()
    fig_amdahl_band()
    fig_two_rooms()
    print("figures written to", IMG)
