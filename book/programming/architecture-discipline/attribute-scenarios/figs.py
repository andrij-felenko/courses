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


# ── 4. Загальний сценарій як породжувальна таблиця ────────────────────────────
def fig_general_generator():
    W, H = 1000, 560
    p = [text(W / 2, 26, "Загальний сценарій — таблиця значень; конкретний — один шлях крізь неї",
              size=16, bold=True)]

    rows = [
        ("Джерело",    ["користувач", "сусідній сервіс", "апаратний збій"], 2),
        ("Стимул",     ["запит на читання", "сплеск ×10", "падіння вузла"], 2),
        ("Артефакт",   ["уся система", "сервіс замовлень", "канал реплікації"], 1),
        ("Середовище", ["норма", "пік", "деградований стан"], 1),
        ("Відповідь",  ["обслуговує як є", "перемикається на репліку", "відкидає з 503"], 1),
        ("Міра",       ["200 мс, p95", "перерва ≤ 30 с", "99.9% часу"], 1),
    ]
    lx, lw = 30, 180
    cx0, cw, cgap = 225, 245, 8
    ch = 46
    for i, (label, vals, pick) in enumerate(rows):
        top = 70 + i * 62
        p.append(fitbox(lx, top, lw, ch, label, size=13, fill=F_BLUE, stroke=NEG, sw=1.4, bold=True))
        for j, v in enumerate(vals):
            x = cx0 + j * (cw + cgap)
            if j == pick:
                p.append(fitbox(x, top, cw, ch, v, size=13, fill=F_GRN, stroke=FIELD, sw=2, bold=True))
            else:
                p.append(fitbox(x, top, cw, ch, v, size=12, fill=F_GREY, stroke=MUTED, sw=1.1))

    # стрілка вниз до складеного сценарію
    p.append(arrow(W / 2, 452, W / 2, 476, color=INK, sw=2))
    p.append(fitbox(70, 482, 860, 62,
                    "апаратний збій валить вузол сервісу замовлень у пік →\n"
                    "система перемикається на репліку, перерва ≤ 30 с",
                    size=14, fill=F_GLD, stroke="#b8860b", sw=1.8, bold=True))
    render(os.path.join(OUT, "general-scenario-generator.svg"), W, H, *p)


# ── 5. Хвіст на масштабі: частка «повільних» запитів росте з віялом ────────────
def fig_tail_at_scale():
    W, H = 900, 470
    p = [text(W / 2, 26, "Хвіст на масштабі: 1 повільний бекенд зі 100 — і повільно стає нормою",
              size=16, bold=True)]

    x0, x1 = 95, 850
    yt, yb = 70, 390
    nmax = 220
    q = 0.01

    def px(n):
        return x0 + (n / nmax) * (x1 - x0)

    def py(v):
        return yb - v * (yb - yt)

    # осі
    p.append(line(x0, yt, x0, yb, color=INK, sw=1.6))
    p.append(line(x0, yb, x1, yb, color=INK, sw=1.6))
    # y-поділки
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        yy = py(frac)
        p.append(line(x0 - 5, yy, x0, yy, color=INK, sw=1.2))
        p.append(text(x0 - 12, yy + 4, "%d%%" % int(frac * 100), size=11, color=MUTED, anchor="end"))
    # x-поділки
    for n in (0, 50, 100, 150, 200):
        xx = px(n)
        p.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.2))
        p.append(text(xx, yb + 22, str(n), size=11, color=MUTED))
    p.append(text((x0 + x1) / 2, yb + 46, "кількість бекендів у віялі (n), кожен повільний у 1% випадків",
                  size=12, color=MUTED))
    p.append(text((x0 + x1) / 2, 52, "частка запитів, що впираються хоч в один повільний бекенд",
                  size=12, color=MUTED))

    # крива 1 − 0.99^n
    pts = []
    n = 0
    while n <= nmax:
        pts.append("%.1f,%.1f" % (px(n), py(1 - (1 - q) ** n)))
        n += 2
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))

    # виноска n = 100 → 63%
    v100 = 1 - (1 - q) ** 100
    p.append(line(px(100), yb, px(100), py(v100), color=MUTED, sw=1, dash="4,4"))
    p.append(line(x0, py(v100), px(100), py(v100), color=MUTED, sw=1, dash="4,4"))
    p.append(circle(px(100), py(v100), 4, fill=POS, stroke=POS))
    p.append(text(px(100) - 12, py(v100) - 12, "n = 100  →  63%", size=13, color=INK, anchor="end", bold=True))
    # виноска n = 10 → 10%
    v10 = 1 - (1 - q) ** 10
    p.append(circle(px(10), py(v10), 3.5, fill=POS, stroke=POS))
    p.append(text(px(10) + 10, py(v10) - 10, "n = 10 → 10%", size=12, color=INK, anchor="start"))
    render(os.path.join(OUT, "tail-at-scale.svg"), W, H, *p)


# ── 6. Складання доступності: послідовність точить нулі, резерв множить ────────
def fig_availability_composition():
    W, H = 960, 400
    p = [text(W / 2, 26, "Як складається доступність: послідовність точить нулі, резерв їх множить",
              size=16, bold=True)]
    p.append(line(480, 62, 480, 362, color=MUTED, sw=1, dash="5,5"))

    # ── ліва панель: послідовність ──
    p.append(text(240, 62, "Послідовність (залежність)", size=14, bold=True, color=POS))
    p.append(text(240, 86, "три по 99.9%, запит проходить крізь усі", size=12, color=MUTED))
    cxs = [110, 240, 370]
    boxes = []
    for cxx in cxs:
        b, w, h = textbox(cxx, 150, "99.9%", size=15, fill=F_BLUE, stroke=NEG, bold=True, min_w=84)
        boxes.append((b, w, h))
        p.append(b)
    p.append(arrow(cxs[0] + 42, 150, cxs[1] - 42, 150, color=INK, sw=1.8))
    p.append(arrow(cxs[1] + 42, 150, cxs[2] - 42, 150, color=INK, sw=1.8))
    p.append(arrow(240, 172, 240, 214, color=INK, sw=2))
    p.append(textbox(240, 250, "0.999³ = 0.997\n→ 99.7%", size=14,
                     fill=F_GLD, stroke="#b8860b", bold=True, min_w=170)[0])
    p.append(text(240, 318, "нулі тануть із довжиною ланцюга", size=12, color=MUTED, italic=True))

    # ── права панель: резерв ──
    p.append(text(720, 62, "Резерв (паралель)", size=14, bold=True, color=FIELD))
    p.append(text(720, 86, "дві репліки по 99%, досить однієї живої", size=12, color=MUTED))
    r1, w1, h1 = textbox(625, 120, "99%", size=15, fill=F_GRN, stroke=FIELD, bold=True, min_w=78)
    r2, w2, h2 = textbox(625, 182, "99%", size=15, fill=F_GRN, stroke=FIELD, bold=True, min_w=78)
    p += [r1, r2]
    mb, mw, mh = textbox(795, 151, "жива, якщо\nхоч одна", size=12, fill=F_GREY, stroke=LINE, min_w=110)
    p.append(mb)
    p.append(arrow(625 + w1 / 2, 122, 795 - mw / 2 - 4, 146, color=INK, sw=1.8))
    p.append(arrow(625 + w2 / 2, 180, 795 - mw / 2 - 4, 156, color=INK, sw=1.8))
    p.append(arrow(795, 151 + mh / 2, 728, 214, color=INK, sw=2))
    p.append(textbox(700, 250, "1 − 0.01² = 0.9999\n→ 99.99%", size=14,
                     fill=F_GLD, stroke="#b8860b", bold=True, min_w=180)[0])
    p.append(text(720, 318, "резерв підносить недоступність до степеня", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "availability-composition.svg"), W, H, *p)


# ── 7. Дерево корисності: сценарії-листя, драйвери — (високо, високо) ──────────
def fig_utility_tree():
    W, H = 1000, 470
    p = [text(W / 2, 26, "Дерево корисності: драйвери — це листя (важливо, важко)", size=16, bold=True)]

    root, rw, rh = textbox(500, 72, "Корисність\nсистеми", size=14, fill=F_BLUE, stroke=NEG, bold=True, min_w=150)
    p.append(root)

    attrs = [(200, "Продуктивність"), (500, "Доступність"), (800, "Змінюваність")]
    ay = 180
    for axx, name in attrs:
        p.append(line(500, 72 + rh / 2, axx, ay - 20, color=MUTED, sw=1.4))
        p.append(textbox(axx, ay, name, size=13, fill=F_GREY, stroke=LINE, bold=True, min_w=120)[0])

    # листя: (cx, текст, драйвер?, батько_x)
    leaves = [
        (118, "профіль\n200 мс p95\n(В, В)", True, 200),
        (300, "звіт < 5 с\n(С, Н)", False, 200),
        (500, "failover\n≤ 30 с\n(В, В)", True, 500),
        (800, "нова валюта\n≤ 2 дні\n(В, С)", False, 800),
    ]
    ly = 330
    for cx, txt, drv, par in leaves:
        p.append(line(par, ay + 20, cx, ly - 30, color=MUTED, sw=1.2))
        if drv:
            p.append(textbox(cx, ly, txt, size=12, fill=F_GRN, stroke=FIELD, sw=2, bold=True, min_w=126)[0])
        else:
            p.append(textbox(cx, ly, txt, size=12, fill=F_GREY, stroke=MUTED, min_w=126)[0])

    p.append(text(W / 2, 438,
                  "(Важливість, Складність): В — високо, С — середньо, Н — низько.  "
                  "Драйвери (зелені) = листя (В, В).",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "utility-tree.svg"), W, H, *p)


# ── 8. Родовід сценарію: що кожен крок додав до нього як інструмента ───────────
def fig_scenario_lineage():
    W, H = 1040, 470
    p = [text(W / 2, 26, "Родовід сценарію: що кожен крок додав до нього як мірила",
              size=17, bold=True)]

    cxs = [155, 400, 645, 890]
    spine_y = 178

    # спина з напрямком часу
    p.append(line(50, spine_y, 968, spine_y, color=MUTED, sw=2))
    p.append(arrow(966, spine_y, 992, spine_y, color=MUTED, sw=2))

    tops = [
        ("SAAM\n1994", F_BLUE, NEG),
        ("ATAM\n2000", F_GRN, FIELD),
        ("QAW\n2001", F_GLD, "#b8860b"),
        ("Канон\n2003 → 2011", F_BLUE, NEG),
    ]
    descs = [
        "Сценарій уперше —\nмірило, а не смак.\nОдна якість:\nзмінюваність.",
        "Дерево корисності\nранжує сценарії за\nважливістю й складністю.\nТочки чутливості й\nкомпромісу, ризики.\nЯкості — навхрест.",
        "Сценарії збирають\nще ДО архітектури —\nвід стейкхолдерів.\nНема що оцінювати —\nє що з'ясувати.",
        "Шість частин сценарію\n(SAiP, 2-ге вид.).\nСпільний словник\nякостей —\nISO/IEC 25010.",
    ]
    for cx, (name, fill, stroke), desc in zip(cxs, tops, descs):
        b, w, h = textbox(cx, 96, name, size=13, fill=fill, stroke=stroke, sw=1.8,
                          bold=True, min_w=150)
        p.append(line(cx, 96 + h / 2, cx, spine_y - 9, color=MUTED, sw=1.3))
        p.append(circle(cx, spine_y, 8, fill=fill, stroke=stroke, sw=2))
        p.append(line(cx, spine_y + 9, cx, 232, color=MUTED, sw=1.3))
        p.append(b)
        p.append(fitbox(cx - 106, 232, 212, 152, desc, size=12,
                        fill=F_GREY, stroke=MUTED, sw=1.2))

    p.append(text(W / 2, 452,
                  "Одна лінія крізь усе: та сама одиниця — сценарій — щоразу бере на себе більше ваги.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "scenario-lineage.svg"), W, H, *p)


# ── 9. Чому добуток, а не сума: сітка важливість × складність ──────────────────
def fig_product_vs_sum():
    W, H = 900, 560
    p = [text(W / 2, 28, "Чому ДОБУТОК, а не сума: на діагоналі сума однакова, добуток — ні",
              size=16, bold=True)]

    cw, chh = 120, 96
    x0, y0 = 250, 100
    inner_w, inner_h = cw - 8, chh - 8

    def cx(i):                      # важливість 0..2 (Н,С,В) зліва направо
        return x0 + i * cw
    def cy(j):                      # складність 0..2 (Н,С,В) знизу вгору
        return y0 + (2 - j) * chh

    for i in range(3):
        for j in range(3):
            imp, dif = i + 1, j + 1
            x, y = cx(i), cy(j)
            if imp == 3 and dif == 3:
                fill, stroke, sw = F_GRN, FIELD, 2.6
            else:
                fill, stroke, sw = F_GREY, MUTED, 1.2
            p.append(rect(x, y, inner_w, inner_h, fill=fill, stroke=stroke, sw=sw, rx=8))
            p.append(text(x + inner_w / 2, y + 20, "%d×%d" % (imp, dif), size=12, color=MUTED))
            p.append(text(x + inner_w / 2, y + inner_h / 2 + 20, str(imp * dif),
                          size=30, bold=True, color=INK))

    # анти-діагональ сума=4: клітини (imp1,dif3),(imp2,dif2),(imp3,dif1) — червона рамка
    for i, j in [(0, 2), (1, 1), (2, 0)]:
        p.append(rect(cx(i), cy(j), inner_w, inner_h, fill="none", stroke=POS, sw=2.4, rx=8))

    # драйвер-тег над кутом (В,В)
    p.append(text(cx(2) + inner_w / 2, y0 - 12, "драйвер", size=13, bold=True, color=FIELD))

    # осі
    for i, r in enumerate(("Н", "С", "В")):
        p.append(text(cx(i) + inner_w / 2, y0 + 3 * chh + 6, r, size=14, bold=True, color=NEG))
    p.append(text(x0 + 1.5 * cw - 4, y0 + 3 * chh + 32, "важливість →", size=13, bold=True, color=NEG))
    for j, r in enumerate(("Н", "С", "В")):
        p.append(text(x0 - 22, cy(j) + inner_h / 2 + 5, r, size=14, bold=True, color=POS, anchor="end"))
    p.append(text(x0 - 8, y0 - 16, "складність ↑", size=13, bold=True, color=POS, anchor="end"))

    p.append(fitbox(150, y0 + 3 * chh + 50, 600, 44,
                    "На червоній діагоналі сума = 4 в усіх трьох; добутки 3 · 4 · 3 їх розрізняють:\n"
                    "вільний виграш (3×1), чесна середина (2×2), важке-нікому (1×3).",
                    size=13, fill=F_GLD, stroke="#b8860b", sw=1.6))
    render(os.path.join(OUT, "product-vs-sum.svg"), W, H, *p)


# ── 10. Парето-фронт: верхня оболонка, коли кут (В,В) порожній ─────────────────
def fig_pareto_front():
    W, H = 820, 520
    p = [text(W / 2, 28, "Парето-фронт: кут (В,В) порожній — квадрант дає 0, фронт ні",
              size=16, bold=True)]

    x0, y0 = 150, 92
    ax_w, ax_h = 540, 330

    def gx(imp):
        return x0 + (imp - 1) / 2 * ax_w
    def gy(dif):
        return y0 + (3 - dif) / 2 * ax_h

    for v in (1, 2, 3):
        p.append(line(gx(v), y0, gx(v), y0 + ax_h, color="#e5e7eb", sw=1))
        p.append(line(x0, gy(v), x0 + ax_w, gy(v), color="#e5e7eb", sw=1))
    for v, r in zip((1, 2, 3), ("Н", "С", "В")):
        p.append(text(gx(v), y0 + ax_h + 26, r, size=14, bold=True, color=NEG))
        p.append(text(x0 - 22, gy(v) + 5, r, size=14, bold=True, color=POS, anchor="end"))
    p.append(text(x0 + ax_w / 2, y0 + ax_h + 50, "важливість →", size=13, bold=True, color=NEG))
    p.append(text(x0 + 6, y0 - 16, "складність ↑", size=13, bold=True, color=POS, anchor="start"))

    front = {(3, 2), (2, 3)}
    # порожній кут (В,В)
    p.append(circle(gx(3), gy(3), 13, fill="none", stroke=MUTED, sw=1.6))
    p.append(text(gx(3) + 16, gy(3) - 16, "(В,В) порожній", size=12, color=MUTED, anchor="start"))
    # сходинка фронту крізь порожній кут
    p.append(line(gx(2), gy(3), gx(3), gy(3), color=FIELD, sw=2.4, dash="6,4"))
    p.append(line(gx(3), gy(3), gx(3), gy(2), color=FIELD, sw=2.4, dash="6,4"))

    # точки-сценарії (без (3,3)); підпис зсунуто в середину клітини, геть від ліній сітки
    pts = [(3, 2, "профіль 200 мс", 18, 20, "start"),
           (2, 3, "нова схема БД", -18, 20, "end"),
           (3, 1, "звіт < 5 с", 18, -16, "start"),
           (2, 2, "журнал подій", 18, 20, "start"),
           (1, 3, "рефактор ядра", 18, 20, "start"),
           (1, 1, "тултіпи", 18, -16, "start"),
           (2, 1, "експорт CSV", 18, -16, "start")]
    for imp, dif, lab, dx, dy, anch in pts:
        on = (imp, dif) in front
        p.append(circle(gx(imp), gy(dif), 9 if on else 6,
                        fill=F_GRN if on else "#eef0f2",
                        stroke=FIELD if on else MUTED, sw=2.4 if on else 1.4))
        p.append(text(gx(imp) + dx, gy(dif) + dy, lab, size=11,
                      color=INK if on else MUTED, anchor=anch, bold=on))
    p.append(text(W / 2, H - 12,
                  "Зелені — Парето-фронт: сценарій, якого не домінує жоден інший (не гірший за обома осями).",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "pareto-front.svg"), W, H, *p)


# ── Фігури вставки math-response-measures.md ──────────────────────────────────
def fig_skew_percentiles():
    import math
    GOLD, PURP = "#b8860b", "#7d3c98"
    W, H = 920, 470
    MU, SIG = math.log(50.0), 0.8

    def dens(x):
        if x <= 0:
            return 0.0
        return (1.0 / (x * SIG * math.sqrt(2 * math.pi))) * \
               math.exp(-((math.log(x) - MU) ** 2) / (2 * SIG * SIG))

    p = [text(W / 2, 26, "Чому середнє бреше: маса ліворуч, а біль — у правому хвості",
              size=16, bold=True)]
    PL, PR, yt, yb = 75, 770, 70, 400
    XMAX = 380.0

    def px(ms):
        return PL + ms / XMAX * (PR - PL)

    dmax = max(dens(x) for x in range(1, int(XMAX)))

    def py(d):
        return yb - (d / dmax) * (yb - yt - 12)

    p.append(line(PL, yt - 6, PL, yb, color=INK, sw=1.6))
    p.append(line(PL, yb, PR + 6, yb, color=INK, sw=1.6))
    for ms in (0, 50, 100, 150, 200, 250, 300, 350):
        p.append(line(px(ms), yb, px(ms), yb + 5, color=INK, sw=1.1))
        p.append(text(px(ms), yb + 21, str(ms), size=11, color=MUTED))
    p.append(text((PL + PR) / 2, yb + 42, "час відповіді, мс", size=12, color=MUTED))

    top = ["%.1f,%.1f" % (px(x), py(dens(x))) for x in range(1, int(XMAX) + 1)]
    p.append('<polyline points="%s %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none" opacity="0.5"/>'
             % (" ".join(top), px(XMAX), yb, px(1), yb, "#e8edfb"))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(top), NEG))

    for ms, col in [(50, NEG), (69, POS), (186, GOLD), (321, PURP)]:
        p.append(line(px(ms), yb, px(ms), py(dens(ms)), color=col, sw=2.2, dash="3,3"))
        p.append(circle(px(ms), py(dens(ms)), 3.5, fill=col, stroke=col))

    p.append(text(px(18), 372, "маса швидких", size=12, color=MUTED))
    p.append(text(px(255), 330, "довгий хвіст повільних →", size=12, color=MUTED))

    lx, tx = 600, 620
    rows = [(NEG, "p50 медіана — 50 мс"), (POS, "середнє — 69 мс (тягне хвіст)"),
            (GOLD, "p95 — 186 мс"), (PURP, "p99 — 321 мс")]
    for i, (col, s) in enumerate(rows):
        yy = 104 + i * 27
        p.append(circle(lx, yy - 4, 5, fill=col, stroke=col))
        p.append(text(tx, yy, s, size=13, color=INK, anchor="start"))
    render(os.path.join(OUT, "skew-percentiles.svg"), W, H, *p)


def fig_max_of_fanout():
    import math
    W, H = 940, 475
    MU, SIG = math.log(50.0), 0.8

    def Phi(z):
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2)))

    def F(t):
        return 0.0 if t <= 0 else Phi((math.log(t) - MU) / SIG)

    p = [text(W / 2, 26, "Час запиту — це максимум із n бекендів: віяло тягне весь розподіл управо",
              size=15, bold=True)]
    PL, PR, yt, yb = 80, 880, 80, 400
    TMAX = 600.0

    def px(t):
        return PL + t / TMAX * (PR - PL)

    def py(v):
        return yb - v * (yb - yt)

    p.append(line(PL, yt - 6, PL, yb, color=INK, sw=1.6))
    p.append(line(PL, yb, PR + 6, yb, color=INK, sw=1.6))
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        p.append(line(PL - 5, py(v), PL, py(v), color=INK, sw=1.1))
        p.append(text(PL - 11, py(v) + 4, "%.2f" % v, size=11, color=MUTED, anchor="end"))
    for t in (0, 100, 200, 300, 400, 500, 600):
        p.append(line(px(t), yb, px(t), yb + 5, color=INK, sw=1.1))
        p.append(text(px(t), yb + 21, str(t), size=11, color=MUTED))
    p.append(text((PL + PR) / 2, yb + 42, "час відповіді бекенда, мс", size=12, color=MUTED))
    p.append(line(PL, py(0.5), PR, py(0.5), color=MUTED, sw=1, dash="5,4"))

    curves = [(1, NEG, "n = 1 · один бекенд"), (10, INK, "n = 10 · віяло вдесятеро"),
              (100, POS, "n = 100 · віяло всоте")]
    for (n, col, lab), gx in zip(curves, [95, 400, 660]):
        p.append(line(gx, 54, gx + 26, 54, color=col, sw=3))
        p.append(text(gx + 32, 58, lab, size=12, color=INK, anchor="start"))

    def cross(n):
        lo, hi = 1.0, TMAX
        for _ in range(60):
            m = (lo + hi) / 2
            if F(m) ** n < 0.5:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2

    for n, col, _ in curves:
        pts = ["%.1f,%.1f" % (px(t), py(F(t) ** n)) for t in range(1, int(TMAX) + 1, 2)]
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), col))
        p.append(circle(px(cross(n)), py(0.5), 4, fill=col, stroke=col))

    for (n, ms), (nn, col, _) in zip([(1, "50 мс"), (10, "166 мс"), (100, "358 мс")], curves):
        p.append(text(px(cross(n)), py(0.5) - 12, "медіана: " + ms, size=12, color=col,
                      anchor="middle", bold=True))
    p.append(text(W / 2, 452,
                  "Медіана 100-бекендового запиту (358 мс) сидить на p99.3 одного бекенда — "
                  "рідкість стала нормою.", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "max-of-fanout.svg"), W, H, *p)


def fig_queue_knee():
    W, H = 900, 470
    p = [text(W / 2, 26, "Коліно черги: біля повного завантаження затримка летить у нескінченність",
              size=15, bold=True)]
    PL, PR, yt, yb = 80, 820, 70, 400
    RMAX, YMAX = 1.08, 21.0

    def px(r):
        return PL + r / RMAX * (PR - PL)

    def py(v):
        return yb - v / YMAX * (yb - yt)

    p.append(line(PL, yt - 6, PL, yb, color=INK, sw=1.6))
    p.append(line(PL, yb, PR + 6, yb, color=INK, sw=1.6))
    for r in (0, 0.25, 0.5, 0.75, 1.0):
        p.append(line(px(r), yb, px(r), yb + 5, color=INK, sw=1.1))
        p.append(text(px(r), yb + 21, "%.2f" % r, size=11, color=MUTED))
    for v in (0, 5, 10, 15, 20):
        p.append(line(PL - 5, py(v), PL, py(v), color=INK, sw=1.1))
        p.append(text(PL - 11, py(v) + 4, "%d×" % v, size=11, color=MUTED, anchor="end"))
    p.append(text((PL + PR) / 2, yb + 42, "завантаженість ρ = λ / μ", size=12, color=MUTED))
    p.append(text(150, 60, "W / час обслуговування", size=12, color=MUTED, anchor="start"))

    p.append(line(px(1.0), yt, px(1.0), yb, color=POS, sw=1.2, dash="5,4"))
    p.append(text(px(1.0) - 8, 96, "ρ → 1", size=13, color=POS, anchor="end", bold=True))
    p.append(text(px(1.0) - 8, 116, "W → ∞", size=13, color=POS, anchor="end", bold=True))

    pts = []
    r = 0.0
    while r <= 0.955:
        v = 1.0 / (1.0 - r)
        if v > YMAX:
            break
        pts.append("%.1f,%.1f" % (px(r), py(v)))
        r += 0.004
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))

    p.append(circle(px(0.75), py(4.0), 4.5, fill=NEG, stroke=NEG))
    p.append(text(px(0.5), 300, "коліно ≈ 0.7–0.8", size=13, color=INK, bold=True))
    p.append(text(px(0.5), 320, "далі кожен % коштує все дорожче", size=11, color=MUTED))

    for i, s in enumerate(["ρ = 0.5  →  W = 2× обслуговування", "ρ = 0.8  →  5×",
                           "ρ = 0.9  →  10×", "ρ = 0.95 →  20×"]):
        p.append(text(108, 150 + i * 24, s, size=12, color=INK, anchor="start"))
    render(os.path.join(OUT, "queue-knee.svg"), W, H, *p)


if __name__ == "__main__":
    fig_anatomy()
    fig_wish_vs_scenario()
    fig_funnel()
    fig_general_generator()
    fig_tail_at_scale()
    fig_availability_composition()
    fig_utility_tree()
    fig_scenario_lineage()
    fig_product_vs_sum()
    fig_pareto_front()
    fig_skew_percentiles()
    fig_max_of_fanout()
    fig_queue_knee()
    print("figs done ->", OUT)
