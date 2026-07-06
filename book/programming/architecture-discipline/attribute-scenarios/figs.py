# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
F_GREY = "#f4f6f8"


# ── 1. Анатомія сценарію: шість частин уздовж однієї стрічки ──────────────────
def fig_anatomy():
    W, H = 900, 430
    p = [text(W / 2, 28, "Шість частин одного сценарію атрибута", size=17, bold=True)]

    # Верхня стрічка: джерело → стимул → [артефакт у середовищі] → відповідь → міра
    y = 120
    # рамки-частини
    b1, w1, h1 = textbox(140, y, "Джерело\n(хто/що)", size=13, fill=F_BLUE, stroke=NEG, bold=True, min_w=150)
    b2, w2, h2 = textbox(360, y, "Стимул\n(подія)", size=13, fill=F_BLUE, stroke=NEG, bold=True, min_w=150)
    b4, w4, h4 = textbox(620, y, "Артефакт\n(що зачеплено)", size=13, fill=F_GREY, stroke=LINE, bold=True, min_w=170)
    p += [b1, b2, b4]

    # середовище — рамка-контейнер навколо артефакта
    env_x, env_w = 620 - 130, 260
    p.append(rect(env_x, y - 78, env_w, 156, fill="none", stroke=FIELD, sw=2, rx=10))
    p.append(text(620, y - 58, "Середовище (за яких умов)", size=11, color=FIELD, bold=True))

    # стрілки стимулу
    p.append(arrow(140 + w1 / 2, y, 360 - w2 / 2, y, color=INK, sw=2))
    p.append(arrow(360 + w2 / 2, y, env_x - 8, y, color=INK, sw=2))

    # нижня стрічка: відповідь + міра
    y2 = 300
    b5, w5, h5 = textbox(360, y2, "Відповідь\n(що робить система)", size=13, fill=F_GRN, stroke=FIELD, bold=True, min_w=210)
    b6, w6, h6 = textbox(660, y2, "Міра відповіді\n(скільки — число)", size=13, fill=F_GLD, stroke="#b8860b", bold=True, min_w=210)
    p += [b5, b6]

    # від артефакта вниз до відповіді
    p.append(arrow(620, y + 78 + 2, 360, y2 - h5 / 2 - 4, color=INK, sw=2))
    # від відповіді до міри
    p.append(arrow(360 + w5 / 2, y2, 660 - w6 / 2, y2, color=INK, sw=2))

    p.append(text(W / 2, 400, "Читається як речення: коли <джерело> робить <стимул>, "
                              "система <відповідь> — і це вимірюється <мірою>.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "scenario-anatomy.svg"), W, H, *p)


# ── 2. Побажання проти сценарію: те саме, але одне можна перевірити ───────────
def fig_wish_vs_scenario():
    W, H = 900, 360
    p = [text(W / 2, 28, "Одна вимога — два формулювання", size=17, bold=True)]

    # ліворуч — розмите побажання
    lx = 235
    p.append(text(lx, 66, "Розмите побажання", size=14, bold=True, color=POS))
    p.append(fitbox(lx - 195, 84, 390, 92,
                    "«Система має бути\nшвидкою й надійною»",
                    size=16, fill=F_RED, stroke=POS, sw=1.8, bold=True))
    for i, ln in enumerate(["Швидкою — для кого, коли, наскільки?",
                            "Надійною — за яких збоїв?",
                            "Перевірити не можна.",
                            "Сперечатися можна безкінечно."]):
        p.append(text(lx, 208 + i * 24, ln, size=12, color=INK))

    # праворуч — конкретний сценарій
    rx = 665
    p.append(text(rx, 66, "Конкретний сценарій", size=14, bold=True, color=FIELD))
    p.append(fitbox(rx - 195, 84, 390, 92,
                    "«У пік навантаження запит\nпрофілю віддається за 200 мс\nу 95% випадків»",
                    size=14, fill=F_GRN, stroke=FIELD, sw=1.8, bold=True))
    for i, ln in enumerate(["Джерело+стимул: пік, запит профілю.",
                            "Міра: 200 мс, 95-й перцентиль.",
                            "Тест напише сам себе.",
                            "Виконано або ні — без суперечки."]):
        p.append(text(rx, 208 + i * 24, ln, size=12, color=INK))

    # розділювач
    p.append(line(450, 60, 450, 320, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, "wish-vs-scenario.svg"), W, H, *p)


# ── 3. Лійка: багато побажань → кілька драйверних сценаріїв → рішення ─────────
def fig_funnel():
    W, H = 860, 400
    p = [text(W / 2, 28, "Від хмари побажань — до кількох, що вирішують форму", size=16, bold=True)]

    # верх: хмара розмитих «-ility»
    top_y = 92
    wishes = ["швидко", "надійно", "безпечно", "дешево", "легко міняти",
              "масштабно", "зручно", "стійко", "прозоро"]
    xs = [90, 210, 330, 450, 570, 690, 810, 260, 640]
    ys = [70, 96, 66, 100, 68, 98, 72, 128, 128]
    for wr, xx, yy in zip(wishes, xs, ys):
        b, ww, hh = textbox(xx, yy, wr, size=12, fill=F_GREY, stroke=MUTED, sw=1.2, min_w=64)
        p.append(b)
    p.append(text(W / 2, 160, "десятки побажань — усі важливі, усіх однаково не досягти",
                  size=11, color=MUTED, italic=True))

    # лійка (трапеція)
    p.append('<path d="M 200 180 L 660 180 L 540 250 L 320 250 Z" '
             'fill="%s" stroke="%s" stroke-width="1.5"/>' % (F_BLUE, NEG))
    p.append(text(W / 2, 218, "пріоритет за ризиком і бізнес-цінністю", size=12, color=NEG, bold=True))

    # середина: кілька драйверних сценаріїв
    mid_y = 300
    drivers = ["профіль за 200 мс\nу пік (95%)",
               "переживає\nвтрату вузла БД",
               "нова валюта —\nбез правки ядра"]
    dxs = [230, 430, 630]
    for dr, dx in zip(drivers, dxs):
        b, ww, hh = textbox(dx, mid_y, dr, size=12, fill=F_GRN, stroke=FIELD, sw=1.8, bold=True, min_w=170)
        p.append(b)
    p.append(text(W / 2, 348, "5–15 драйверних сценаріїв — конкретних і вимірних", size=11, color=FIELD, italic=True))

    # низ: рішення
    p.append(arrow(W / 2, 360, W / 2, 384, color=INK, sw=2.2))
    b, ww, hh = textbox(W / 2, 400 - 6, "формують рішення: кеш, реплікація, точка розширення",
                        size=12, fill=F_GLD, stroke="#b8860b", sw=1.8, bold=True)
    # трохи підняти, щоб не вилазило
    render(os.path.join(OUT, "quality-funnel.svg"), W, H,
           *p,
           fitbox(W / 2 - 245, 366, 490, 30,
                  "ці кілька — і формують рішення про архітектуру",
                  size=12, fill=F_GLD, stroke="#b8860b", sw=1.8, bold=True))


if __name__ == "__main__":
    fig_anatomy()
    fig_wish_vs_scenario()
    fig_funnel()
    print("figs done ->", OUT)
