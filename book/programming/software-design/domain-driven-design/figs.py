# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Знекровлена vs багата модель ─────────────────────────────────────────────
def fig_anemic_vs_rich():
    W, H = 1000, 560
    frags = []

    # ── ЛІВА половина: знекровлена ──
    lcx = 250
    frags.append(text(lcx, 62, "Знекровлена модель", size=17, bold=True, color=POS))

    # мішок-об'єкт із самими полями (відкритий)
    bx, by, bw, bh = 120, 96, 260, 150
    frags.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=POS, sw=1.8, rx=9))
    frags.append(text(lcx, by + 26, "Policy", size=15, bold=True, color=INK))
    frags.append(line(bx + 16, by + 40, bx + bw - 16, by + 40, color=POS, sw=1.2))
    for i, fld in enumerate(["status: string", "balance: number", "dueDate: Date"]):
        frags.append(text(bx + 22, by + 66 + i * 26, fld, size=13, color=MUTED, anchor="start"))
    frags.append(text(lcx, by + bh - 12, "самі поля, нуль поведінки", size=11, italic=True, color=POS))

    # правило збоку, в окремому сервісі
    sx, sy, sw_, sh = 120, 300, 260, 96
    frags.append(rect(sx, sy, sw_, sh, fill=FILL, stroke=MUTED, sw=1.6, rx=9))
    frags.append(text(lcx, sy + 24, "PolicyService", size=14, bold=True, color=INK))
    frags.append(text(lcx, sy + 48, "enterGracePeriod(p)", size=12, color=MUTED))
    frags.append(text(lcx, sy + 72, "правило живе ТУТ, окремо", size=11, italic=True, color=MUTED))

    # чужа стрілка лізе прямо в поле в обхід правила
    frags.append(arrow(70, 420, bx + 40, by + bh - 24, color=POS, sw=2.4))
    bad, bw2, bh2 = textbox(150, 470, "p.status = «grace»\nповз перевірку",
                            size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=9)
    frags.append(bad)

    # роздільник
    frags.append(line(W / 2, 84, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="6,6"))

    # ── ПРАВА половина: багата ──
    rcx = 750
    frags.append(text(rcx, 62, "Багата модель", size=17, bold=True, color=FIELD))

    rx, ry, rw, rh = 620, 96, 260, 210
    frags.append(rect(rx, ry, rw, rh, fill="#f2faf5", stroke=FIELD, sw=1.8, rx=9))
    frags.append(text(rcx, ry + 26, "Policy", size=15, bold=True, color=INK))
    frags.append(line(rx + 16, ry + 40, rx + rw - 16, ry + 40, color=FIELD, sw=1.2))
    # закриті поля
    for i, fld in enumerate(["− status  (закрите)", "− balance (закрите)"]):
        frags.append(text(rx + 22, ry + 64 + i * 24, fld, size=12, color=MUTED, anchor="start"))
    frags.append(line(rx + 16, ry + 122, rx + rw - 16, ry + 122, color="#cfe8d6", sw=1.0))
    # метод-двері з правилом усередині
    frags.append(text(rx + 22, ry + 148, "+ enterGracePeriod()", size=13, bold=True,
                      color=FIELD, anchor="start"))
    frags.append(text(rx + 34, ry + 172, "перевіряє стан і баланс", size=11, color=MUTED, anchor="start"))
    frags.append(text(rcx, ry + rh - 14, "правило й дані — за єдиними дверима", size=11,
                      italic=True, color=FIELD))

    # спроба зайти в обхід упирається в стіну
    frags.append(line(590, 360, 620, 360, color=POS, sw=2.4))
    frags.append(text(590, 356, "✗", size=20, bold=True, color=POS, anchor="end"))
    wall, ww, wh = textbox(720, 400, "у стан НЕ зайти\nповз метод",
                           size=11, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6, pad=9)
    frags.append(wall)

    render(os.path.join(IMG, 'anemic-vs-rich.svg'), W, H, *frags,
           title="Правило збоку від даних vs правило разом із даними")


# ── Обмежені контексти + ACL ─────────────────────────────────────────────────
def fig_bounded_contexts():
    W, H = 1020, 560
    frags = []

    # три контексти як окремі рамки з власним значенням слова
    def context(cx, top, name, term, meaning, col, fill):
        w, h = 250, 150
        x, y = cx - w / 2, top
        frags.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=11))
        frags.append(text(cx, y + 30, name, size=16, bold=True, color=col))
        frags.append(line(x + 18, y + 44, x + w - 18, y + 44, color=col, sw=1.2))
        frags.append(text(cx, y + 72, term, size=14, bold=True, color=INK))
        frags.append(text(cx, y + 100, meaning, size=12, color=MUTED))
        frags.append(text(cx, y + 128, "своя мова, своя модель", size=11, italic=True, color=col))
        return x, y, w, h

    # Продажі (ліворуч угорі)
    sxx, syy, sww, shh = context(200, 96, "Контекст: Продажі",
                                 "Client = воронка", "стадія · ймовірність", NEG, "#eaf0fd")
    # Бухгалтерія (праворуч угорі)
    bxx, byy, bww, bhh = context(820, 96, "Контекст: Бухгалтерія",
                                 "Payer = платник", "ІПН · кредитний ліміт", "#b8860b", "#fdf6e3")
    # Підтримка (внизу центр)
    context(510, 350, "Контекст: Підтримка",
            "Ticket = звернення", "канал · тон", FIELD, "#f2faf5")

    # ACL-перекладач на межі Продажі → Бухгалтерія
    acl, aw, ah = textbox(510, 150, "ACL\nперекладач",
                          size=13, bold=True, fill="#fff4e6", stroke=POS, sw=2.0, pad=12)
    frags.append(acl)
    # стрілки крізь ACL: Продажі диктують → ACL → Бухгалтерія приймає
    frags.append(arrow(sxx + sww + 6, 150, 510 - aw / 2 - 6, 150, color=INK, sw=2.2))
    frags.append(arrow(510 + aw / 2 + 6, 150, bxx - 6, 150, color=INK, sw=2.2))
    frags.append(text(510, 150 + ah / 2 + 22, "не пускає чужі поняття всередину",
                      size=11, italic=True, color=POS))

    # спільна підказка внизу
    hint, hw, hh = textbox(510, 500,
                           "одне слово «клієнт» — три різні поняття, і це нормально",
                           size=13, bold=True, fill="#eef4ff", stroke=INK, sw=1.6, pad=11)
    frags.append(hint)

    render(os.path.join(IMG, 'bounded-contexts.svg'), W, H, *frags,
           title="Одне слово — різні значення в різних контекстах")


# ── Рефакторинг: п'ять кроків від мішка до багатої моделі (для proj-вставки) ──
def fig_refactor_ladder():
    W, H = 1120, 640
    frags = []
    frags.append(text(W / 2, 30, "Знекровлений мішок у багату модель: п'ять кроків",
                      size=17, bold=True))

    steps = [
        ("1", "Закрити поля", ["публічні поля роблять", "приватними, сеттери — геть"], NEG),
        ("2", "Внести інваріант", ["правило зі стороннього", "сервісу переносимо в об'єкт"], NEG),
        ("3", "Єдині двері", ["перехід стану — лише", "через метод-команду"], FIELD),
        ("4", "Об'єкт-значення", ["суму й гроші — у свій тип,", "що сам себе стереже"], FIELD),
        ("5", "Корінь агрегату", ["позиції — лише через корінь;", "сума завжди сходиться"], FIELD),
    ]
    n = len(steps)
    bw, bh = 196, 104
    x0, y0 = 34, H - bh - 56
    dx = (W - bw - 60) / (n - 1)
    dy = (y0 - 92) / (n - 1)
    prev = None
    for i, (num, title, body, col) in enumerate(steps):
        x = x0 + i * dx
        y = y0 - i * dy
        if prev is not None:
            px, py = prev
            frags.append(arrow(px + bw - 6, py + bh / 2, x + 6, y + bh / 2, color=MUTED, sw=2.0))
        fillc = "#eaf0fd" if col == NEG else "#f2faf5"
        frags.append(rect(x, y, bw, bh, fill=fillc, stroke=col, sw=2.0, rx=10))
        frags.append(circle(x + 22, y + 24, 14, fill=col, stroke=col, sw=1))
        frags.append(text(x + 22, y + 29, num, size=15, bold=True, color="#ffffff"))
        frags.append(text(x + 44, y + 29, title, size=13, bold=True, color=INK, anchor="start"))
        for j, ln in enumerate(body):
            frags.append(text(x + bw / 2, y + 58 + j * 19, ln, size=11, color=MUTED))
        prev = (x, y)

    frags.append(text(60, 74, "нижчі кроки прибирають діри;", size=12, italic=True,
                      color=NEG, anchor="start"))
    frags.append(text(60, 92, "вищі роблять некоректний стан недосяжним", size=12, italic=True,
                      color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'refactor-ladder.svg'), W, H, *frags)


# ── Корінь агрегату — єдині двері (для proj-вставки) ──────────────────────────
def fig_aggregate_door():
    W, H = 1040, 560
    frags = []
    frags.append(text(W / 2, 30, "Корінь агрегату — єдині двері до інваріанту", size=17, bold=True))

    ax, ay, aw, ah = 120, 92, 800, 372
    frags.append(rect(ax, ay, aw, ah, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=16))
    frags.append(text(ax + aw / 2, ay + 26, "Агрегат «Поліс»", size=15, bold=True, color=FIELD))
    frags.append(text(ax + aw / 2, ay + ah - 14,
                      "межа = те, що мусить бути істинним РАЗОМ; одна транзакція — один агрегат",
                      size=11, italic=True, color=FIELD))

    rx, ry, rw, rh = 168, 150, 244, 250
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=FIELD, sw=2.0, rx=11))
    frags.append(text(rx + rw / 2, ry + 28, "Policy  (корінь)", size=14, bold=True, color=INK))
    frags.append(line(rx + 14, ry + 42, rx + rw - 14, ry + 42, color=FIELD, sw=1.2))
    for i, ln in enumerate(["− status  (закрите)", "− premium (закрите)", "− payments  (закриті)"]):
        frags.append(text(rx + 18, ry + 66 + i * 24, ln, size=12, color=MUTED, anchor="start"))
    frags.append(line(rx + 14, ry + 148, rx + rw - 14, ry + 148, color="#cfe8d6", sw=1.0))
    frags.append(text(rx + 18, ry + 172, "+ addPayment(...)", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(rx + 18, ry + 196, "+ enterGracePeriod()", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(rx + 26, ry + 220, "тут тримається інваріант", size=11, color=MUTED, anchor="start"))

    px, pw, ph = 578, 220, 60
    for i, lbl in enumerate(["Payment #1", "Payment #2", "Payment #3"]):
        yy = 158 + i * 84
        frags.append(rect(px, yy, pw, ph, fill="#eef7f0", stroke="#8fc9a3", sw=1.6, rx=8))
        frags.append(text(px + pw / 2, yy + 25, lbl, size=12, bold=True, color=INK))
        frags.append(text(px + pw / 2, yy + 45, "внутрішня частина", size=10, italic=True, color=MUTED))
        frags.append(arrow(rx + rw + 8, yy + ph / 2, px - 8, yy + ph / 2, color=FIELD, sw=1.8))

    bad, bw2, bh2 = textbox(940, 470, "напряму до частини\n— зась", size=10, bold=True,
                            fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    frags.append(line(940, 470 - bh2 / 2, px + pw / 2, 158 + ph + 6, color=POS, sw=2.2, dash="7,5"))
    frags.append(text(px + pw / 2 + 20, 158 + ph + 2, "✗", size=20, bold=True, color=POS, anchor="start"))
    frags.append(bad)

    frags.append(text(ax + 20, H - 20, "зовнішній код тримає посилання лише на корінь",
                      size=12, bold=True, color=INK, anchor="start"))

    render(os.path.join(IMG, 'aggregate-door.svg'), W, H, *frags)


# ── Часова вісь народження DDD (для hist-вставки) ─────────────────────────────
def fig_ddd_timeline():
    W, H = 1120, 560
    frags = []
    frags.append(text(W / 2, 34, "Народження DDD і як ідею згодом розклали", size=17, bold=True))

    # горизонтальна вісь часу
    ax_y = 300
    ax_x0, ax_x1 = 90, W - 60
    frags.append(line(ax_x0, ax_y, ax_x1, ax_y, color=INK, sw=2.2))
    frags.append(arrow(ax_x1 - 24, ax_y, ax_x1, ax_y, color=INK, sw=2.2))

    # дві віхи-роки на осі, з великим горизонтальним зазором між ними.
    # Рік підписуємо ЗБОКУ від точки (не під нею), щоб вертикальні гілки-виноски
    # до нижніх рамок не проходили крізь напис року.
    x2003 = 340
    x2013 = 860
    for xx, yr in [(x2003, "2003"), (x2013, "2013")]:
        frags.append(circle(xx, ax_y, 7, fill=INK, stroke=INK, sw=1))
        frags.append(text(xx + 44, ax_y + 6, yr, size=15, bold=True, color=INK, anchor="start"))

    # 2003 — «синя книжка» (над віссю)
    b1, bw1, bh1 = textbox(x2003, 150,
                           "«Синя книжка» Еванса\nDDD (Addison-Wesley)\n+ передмова Фаулера",
                           size=12, bold=True, fill="#eaf0fd", stroke=NEG, sw=2.0, pad=12)
    frags.append(b1)
    frags.append(line(x2003, 150 + bh1 / 2, x2003, ax_y - 7, color=NEG, sw=1.8))

    # 2003 — «знекровлена модель» (під віссю, той самий рік — гілка вбік, щоб не налазило)
    b2, bw2, bh2 = textbox(x2003, 452,
                           "Фаулер, 25.11.2003:\nантипатерн\n«знекровлена модель»",
                           size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=12)
    frags.append(b2)
    frags.append(line(x2003, ax_y + 7, x2003, 452 - bh2 / 2, color=POS, sw=1.8))

    # 2013 — «червона книжка» (над віссю)
    b3, bw3, bh3 = textbox(x2013, 150,
                           "«Червона книжка» Вернона\nImplementing DDD\n— як робити руками",
                           size=12, bold=True, fill="#fdecea", stroke="#b03a2e", sw=2.0, pad=12)
    frags.append(b3)
    frags.append(line(x2013, 150 + bh3 / 2, x2013, ax_y - 7, color="#b03a2e", sw=1.8))

    # 2013 — розклад на стратегічний / тактичний (під віссю, дві окремі рамки поряд)
    strat, sw_, sh_ = textbox(x2013 - 118, 452, "Стратегічний\nмежі · мова · карта",
                              size=11, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.8, pad=10)
    tact, tw_, th_ = textbox(x2013 + 118, 452, "Тактичний\nсутності · агрегати",
                             size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8, pad=10)
    frags.append(strat)
    frags.append(tact)
    frags.append(line(x2013, ax_y + 7, x2013, 452 - sh_ / 2 - 12, color=MUTED, sw=1.6))
    frags.append(line(x2013, 452 - sh_ / 2 - 12, x2013 - 118, 452 - sh_ / 2, color=FIELD, sw=1.6))
    frags.append(line(x2013, 452 - sh_ / 2 - 12, x2013 + 118, 452 - th_ / 2, color=NEG, sw=1.6))

    render(os.path.join(IMG, 'ddd-timeline.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_anemic_vs_rich()
    fig_bounded_contexts()
    fig_refactor_ladder()
    fig_aggregate_door()
    fig_ddd_timeline()
    print("figures written to", IMG)
