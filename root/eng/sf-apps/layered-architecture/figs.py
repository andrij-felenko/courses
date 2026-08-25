# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: стос шарів і правило залежності (стрілки лише вниз) ────────────
def fig_dependency_rule():
    W, H = 820, 560
    frags = []

    layers = [
        ("Представлення", "UI, HTTP, CLI — як говоримо зі світом", "#eef4ff"),
        ("Застосунок", "сценарії: що по кроках робить система", "#eaf7ef"),
        ("Домен", "правила предметної області — серце", "#fff6e6"),
        ("Інфраструктура", "БД, мережа, файли, чужі сервіси", "#f2f2f5"),
    ]
    bx = 150
    bw = 380
    bh = 78
    gap = 26
    top = 92

    # заголовок над стосом
    frags.append(text(bx + bw / 2, top - 30, "Стрілка залежності — тільки ВНИЗ",
                      size=15, bold=True))

    ys = []
    for i, (nm, desc, fill) in enumerate(layers):
        yy = top + i * (bh + gap)
        ys.append(yy)
        frags.append(rect(bx, yy, bw, bh, fill=fill, stroke=INK, sw=1.8, rx=9))
        frags.append(text(bx + 20, yy + 30, nm, size=15, bold=True, anchor="start"))
        frags.append(text(bx + 20, yy + 54, desc, size=11.5, color=MUTED, anchor="start"))

    # дозволені стрілки вниз (по лівому краю, повз написи)
    ax = bx - 34
    for i in range(len(layers) - 1):
        frags.append(arrow(ax, ys[i] + bh - 8, ax, ys[i + 1] + 8, color=FIELD, sw=2.4))
    frags.append(text(ax - 20, top + 2 * (bh + gap) - gap / 2, "можна",
                      size=11.5, bold=True, color=FIELD, anchor="middle"))

    # заборонена стрілка вгору (по правому краю) — перекреслена
    rxp = bx + bw + 34
    y_from = ys[3] + 8          # від інфраструктури
    y_to = ys[0] + bh - 8       # до представлення
    frags.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.4" marker-end="url(#arrow)"/>'
                  % (rxp, y_from, rxp, y_to, POS)))
    # перекреслення
    frags.append(line(rxp - 16, (y_from + y_to) / 2 + 12,
                      rxp + 16, (y_from + y_to) / 2 - 12, color=POS, sw=3.2))
    frags.append(text(rxp + 22, (y_from + y_to) / 2, "не",
                      size=11.5, bold=True, color=POS, anchor="middle"))
    frags.append(text(rxp + 22, (y_from + y_to) / 2 + 16, "можна",
                      size=11.5, bold=True, color=POS, anchor="middle"))

    # підпис-суть під стосом
    note, nw, nh = textbox(W / 2, ys[3] + bh + 46,
                           "Нижнє нічого не знає про верхнє — тому його можна замінити,\n"
                           "не чіпаючи домен. Верхнє гукає нижнє лише через його інтерфейс.",
                           size=12, pad=12, fill="#ffffff", stroke="#d0d5db", sw=1.4)
    frags.append(note)

    render(os.path.join(IMG, 'dependency-rule.svg'), W, H, *frags)


# ── Фігура 2: спектр стилів — від моноліта до подієвих ───────────────────────
def fig_styles_spectrum():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 44, "Той самий поділ на шари — різна ФОРМА розгортання",
                      size=15, bold=True))

    styles = [
        ("Моноліт", "один процес,\nодне розгортання",
         "просто, швидкий старт", "усе злипається з ростом", "#eef4ff"),
        ("Модульний\nмоноліт", "один процес,\nтверді межі модулів",
         "межі без мережі", "спокуса зазирнути в сусіда", "#eaf7ef"),
        ("Мікросервіси", "багато процесів,\nмережа між ними",
         "незалежне розгортання", "мережа, дані, супровід", "#fff6e6"),
        ("Подієві", "спілкування через\nповідомлення-події",
         "слабке зчеплення в часі", "важко простежити потік", "#fdeef0"),
    ]
    n = len(styles)
    col_w = 236
    gap = 22
    total = n * col_w + (n - 1) * gap
    x0 = (W - total) / 2
    top = 96
    box_h = 96

    # вісь під колонками
    axis_y = top + box_h + 150
    frags.append(line(x0, axis_y, x0 + total, axis_y, color=INK, sw=2))
    frags.append(text(x0, axis_y + 26, "менше рухомих частин",
                      size=11.5, color=MUTED, anchor="start"))
    frags.append(text(x0 + total, axis_y + 26, "більше незалежності й масштабу",
                      size=11.5, color=MUTED, anchor="end"))

    for i, (nm, sub, pro, con, fill) in enumerate(styles):
        cx = x0 + i * (col_w + gap) + col_w / 2
        xx = x0 + i * (col_w + gap)
        # головна коробка стилю
        frags.append(rect(xx, top, col_w, box_h, fill=fill, stroke=INK, sw=1.8, rx=9))
        frags.append(mtext(cx, top + 34, nm, size=15, bold=True))
        frags.append(mtext(cx, top + (72 if "\n" in nm else 58), sub,
                           size=11.5, color=MUTED))

        # плюс і мінус нижче
        py = top + box_h + 20
        frags.append(plus(xx + 16, py + 4, r=8))
        frags.append(text(xx + 32, py + 8, pro, size=11, color=INK, anchor="start"))
        my = py + 34
        frags.append(minus(xx + 16, my + 4, r=8))
        frags.append(text(xx + 32, my + 8, con, size=11, color=INK, anchor="start"))

        # позначка на осі
        frags.append(circle(cx, axis_y, 5, fill=INK, stroke=INK))

    render(os.path.join(IMG, 'styles-spectrum.svg'), W, H, *frags)


# ── Фігура 3 (вставка hist): ідея пластів народжувалася тричі ────────────────
def fig_layers_reborn():
    W, H = 1120, 500
    frags = []

    frags.append(text(W / 2, 40, "Пласти народжувалися тричі — у різних головах, з різних потреб",
                      size=15, bold=True))

    # три віхи на часовій осі
    axis_y = 200
    x0, x1 = 120, W - 120
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))

    milestones = [
        (1968, "ОС «THE»",
         "Едсґер Дейкстра\nрівні 0–5",
         "потреба: ДОВЕСТИ,\nщо система коректна",
         "#eef4ff"),
        (1992, "три пласти (three-tier)",
         "доба клієнт-сервер\nекран · логіка · дані",
         "потреба: РОЗІРВАТИ\nтовстого клієнта",
         "#eaf7ef"),
        (2002, "PoEAA",
         "Мартін Фаулер\npresentation · domain · data source",
         "потреба: НАЗВАТИ\nспільний взір у застосунках",
         "#fff6e6"),
    ]
    n = len(milestones)
    for i, (year, name, what, why, fill) in enumerate(milestones):
        cx = x0 + (x1 - x0) * i / (n - 1)
        frags.append(circle(cx, axis_y, 7, fill=INK, stroke=INK))
        frags.append(text(cx, axis_y - 22, str(year), size=15, bold=True))

        # картка «що» — над віссю
        b_what, ww, wh = textbox(cx, axis_y - 78, what, size=11.5, pad=10,
                                 fill=fill, stroke="#c8ccd2", sw=1.4, min_w=210)
        frags.append(b_what)
        frags.append(text(cx, axis_y - 78 - wh / 2 - 8, name, size=13, bold=True))

        # картка «навіщо» — під віссю
        b_why, yw, yh = textbox(cx, axis_y + 96, why, size=11.5, pad=10,
                                fill="#ffffff", stroke="#d0d5db", sw=1.4, min_w=210)
        frags.append(b_why)

    # підсумкова смуга внизу
    note, nw, nh = textbox(W / 2, axis_y + 230,
                           "Одна ідея — розкласти по горизонтальних пластах і пустити залежність\n"
                           "лише вниз — щоразу винаходилася наново під новий біль, а не передавалася естафетою.",
                           size=12, pad=13, fill="#f7f8fa", stroke="#c8ccd2", sw=1.4)
    frags.append(note)

    render(os.path.join(IMG, 'layers-reborn.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_dependency_rule()
    fig_styles_spectrum()
    fig_layers_reborn()
    print("figures written to", IMG)
