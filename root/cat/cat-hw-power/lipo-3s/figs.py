# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

CELL = "#eef2fe"   # клітинка (комірка)
PWR  = "#fdeeee"   # силовий XT60
BAL  = "#eafaf0"   # балансир JST-XH
STOR = "#fff4e6"   # зона зберігання


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: анатомія 3S-пакета — три комірки послідовно, сходинка напруг,
# два виводи (силовий XT60 + балансирний JST-XH). Головна ідея «що це».
# ─────────────────────────────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 940, 500
    frags = []
    frags.append(text(W / 2, 32, "3S-пакет: три комірки послідовно, два виводи назовні", size=16, bold=True))

    # три комірки в ряд
    cx0 = 120
    cw, ch, gap = 150, 140, 46
    cy = 96
    labels = ["Комірка 1", "Комірка 2", "Комірка 3"]
    cell_x = [cx0 + i * (cw + gap) for i in range(3)]
    pole_y = cy + ch - 22          # рівень полюсів (низ комірок)
    for i, x in enumerate(cell_x):
        frags.append(rect(x, cy, cw, ch, fill=CELL, stroke="#3b6fd4", sw=2))
        frags.append(text(x + cw / 2, cy + 32, labels[i], size=13, bold=True, color="#274b8f"))
        frags.append(text(x + cw / 2, cy + 58, "3.7 В ном.", size=13, color=INK))
        frags.append(text(x + cw / 2, cy + 80, "(3.0…4.2 В)", size=11, color=MUTED))
        frags.append(minus(x + 16, pole_y, r=9))
        frags.append(plus(x + cw - 16, pole_y, r=9))
    # з'єднання «+ однієї на − наступної» (послідовно) — у проміжках
    for i in range(2):
        xa = cell_x[i] + cw - 16 + 9
        xb = cell_x[i + 1] + 16 - 9
        frags.append(line(xa, pole_y, xb, pole_y, color=INK, sw=2.4))
        frags.append(text((cell_x[i] + cw + cell_x[i + 1]) / 2, pole_y - 12,
                          "послідовно", size=10.5, color=MUTED, italic=True))

    # координати чотирьох електричних вузлів пакета (низ→верх ланцюга)
    neg_x = cell_x[0] + 16                  # − усього пакета
    pos_x = cell_x[2] + cw - 16             # + усього пакета
    node12_x = (cell_x[0] + cw + cell_x[1]) / 2   # стик 1↔2
    node23_x = (cell_x[1] + cw + cell_x[2]) / 2   # стик 2↔3

    # ── СИЛОВИЙ ВИВІД (XT60): крайні полюси прямо вниз у широкий box ──────────
    # box під усім пакетом; − падає з лівого полюса, + з правого — без перетину тексту
    xt_y = 376
    xt_x = neg_x - 24
    xt_w = pos_x - neg_x + 48
    # силові вертикалі спершу (щоб box лежав поверх їхніх кінців)
    frags.append(line(neg_x, pole_y + 9, neg_x, xt_y + 6, color=NEG, sw=3))
    frags.append(line(pos_x, pole_y + 9, pos_x, xt_y + 6, color=POS, sw=3))
    frags.append(text(neg_x - 6, xt_y - 8, "−", size=15, color=NEG, bold=True, anchor="end"))
    frags.append(text(pos_x + 8, xt_y - 8, "+", size=15, color=POS, bold=True, anchor="start"))
    frags.append(fitbox(xt_x, xt_y, xt_w, 50,
                        "СИЛОВИЙ ВИВІД — XT60\nдва товсті дроти: весь струм пакета",
                        size=12, fill=PWR, stroke=POS, sw=1.8, bold=True))

    # ── БАЛАНСИРНИЙ ВИВІД (JST-XH): 4 тонкі дроти від 4 вузлів донизу-праворуч ─
    bal_box_x, bal_box_y, bal_box_w = 470, 372, 360
    frags.append(fitbox(bal_box_x, bal_box_y, bal_box_w, 50,
                        "БАЛАНСИРНИЙ ВИВІД — JST-XH\n4 тонкі дроти = комірок + 1 (на кожен вузол)",
                        size=12, fill=BAL, stroke=FIELD, sw=1.6, bold=True))
    # чотири вузли → чотири входи балансира, рознесені по ширині box'а
    taps = [(neg_x, NEG), (node12_x, FIELD), (node23_x, FIELD), (pos_x, POS)]
    entry_xs = [bal_box_x + 40 + j * 90 for j in range(4)]
    for j, (sx, col) in enumerate(taps):
        ex = entry_xs[j]
        drop_y = bal_box_y - 14 - j * 10     # східчасто, щоб горизонталі не злилися
        frags.append(line(sx, pole_y + 9, sx, drop_y, color=col, sw=1.5, dash="4 3"))
        frags.append(line(sx, drop_y, ex, drop_y, color=col, sw=1.5, dash="4 3"))
        frags.append(line(ex, drop_y, ex, bal_box_y, color=col, sw=1.5, dash="4 3"))

    frags.append(text(W / 2, H - 20,
                      "11.1 В номінально між крайніми полюсами (3 × 3.7 В); балансир тримає всі три комірки рівними",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'anatomy.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: вікно напруги 3S — сходи стану заряду (на комірку і на пакет),
# із зонами «повний / робота / зберігання / стій / небезпека».
# ─────────────────────────────────────────────────────────────────────────────
def fig_window():
    W, H = 820, 560
    frags = []
    frags.append(text(W / 2, 34, "Вікно напруги 3S: де повно, де стоп, де зберігати", size=16, bold=True))

    # вісь: зверху 4.2 (повний), донизу 3.0 (порожній)
    ax = 300              # вісь х
    top_y, bot_y = 80, 500
    v_top, v_bot = 4.30, 2.90   # трохи ширше за робочі межі, щоб влізли підписи
    def yv(vcell):
        return top_y + (v_top - vcell) / (v_top - v_bot) * (bot_y - top_y)

    # кольорові зони (по комірці)
    zones = [
        (4.20, 4.30, "#fdeeee", "перезаряд — НЕБЕЗПЕКА"),
        (4.20, 3.80, "#eafaf0", "повний → робочий верх"),
        (3.80, 3.30, "#eef7ff", "робоча ділянка"),
        (3.30, 3.00, "#fff4e6", "нижче — просідання під навантаж."),
        (3.00, 2.90, "#fdeeee", "розряд нижче 3.0 — псує комірки"),
    ]
    for va, vb, col, _ in zones:
        y1, y2 = yv(va), yv(vb)
        frags.append(rect(ax - 60, min(y1, y2), 120, abs(y2 - y1), fill=col, stroke="none", rx=0))
    frags.append(line(ax, top_y, ax, bot_y, color=INK, sw=2))

    # ключові рівні: (напруга комірки, напруга пакета 3S, підпис, колір)
    marks = [
        (4.20, "12.6 В", "ПОВНИЙ заряд (100%)", POS, True),
        (3.80, "11.4 В", "ЗБЕРІГАННЯ (~50%)", "#b06f1e", True),
        (3.70, "11.1 В", "номінал (середина)", INK, False),
        (3.50, "10.5 В", "час на посадку/зупинку", MUTED, False),
        (3.30, "9.9 В",  "робочий мінімум під газом", NEG, False),
        (3.00, "9.0 В",  "ПОРОЖНІЙ — далі не розряджати", NEG, True),
    ]
    for vcell, vpack, lbl, col, strong in marks:
        y = yv(vcell)
        frags.append(line(ax - 60, y, ax + 60, y, color=col, sw=2.2 if strong else 1.4,
                          dash=None if strong else "5 4"))
        # ліворуч — напруга комірки
        frags.append(text(ax - 70, y + 4, "%.2f В/комірку" % vcell, size=12,
                          color=col, anchor="end", bold=strong))
        # праворуч — напруга пакета + підпис
        frags.append(text(ax + 72, y - 3, vpack, size=13, color=col, anchor="start", bold=True))
        frags.append(text(ax + 72, y + 15, lbl, size=11.5, color=MUTED, anchor="start"))

    # підписи осі
    frags.append(text(ax, top_y - 14, "більше заряду ↑", size=11.5, color=MUTED))
    frags.append(text(ax, bot_y + 22, "менше заряду ↓", size=11.5, color=MUTED))
    frags.append(text(ax - 60, bot_y + 46, "ліворуч — на одну комірку", size=11, color=MUTED, anchor="start"))
    frags.append(text(ax + 72, bot_y + 46, "праворуч — увесь 3S-пакет (× 3)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'window.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: балансне заряджання — куди йдуть XT60 і JST-XH на зарядці,
# і ЧОМУ балансир бачить кожну комірку окремо.
# ─────────────────────────────────────────────────────────────────────────────
def fig_charging():
    W, H = 900, 540
    frags = []
    frags.append(text(W / 2, 34, "Балансне заряджання: силовий вивід ллє струм, балансир вирівнює комірки", size=15, bold=True))

    # пакет ліворуч — три комірки стовпчиком
    px, pw = 90, 150
    ctop, ch, cgap = 76, 92, 16
    cys = [ctop + i * (ch + cgap) for i in range(3)]
    for i, y in enumerate(cys):
        frags.append(rect(px, y, pw, ch, fill=CELL, stroke="#3b6fd4", sw=2))
        frags.append(text(px + pw / 2, y + 34, "Комірка %d" % (3 - i), size=13, bold=True, color="#274b8f"))
        frags.append(text(px + pw / 2, y + 58, "3.7 В", size=12, color=INK))
    frags.append(text(px + pw / 2, ctop - 14, "3S-ПАКЕТ", size=12, bold=True, color=MUTED))

    # вузли пакета: 4 точки по правому краю (низ→верх): −, 1|2, 2|3, +
    node_y = [cys[2] + ch,                 # низ (−)
              (cys[1] + ch + cys[2]) / 2,  # між 2 і 3 (у стовпчику зверху вниз K3,K2,K1)
              (cys[0] + ch + cys[1]) / 2,  # між 1 і 2
              cys[0]]                        # верх (+)
    node_col = [NEG, FIELD, FIELD, POS]

    # зарядка праворуч
    chx, chw = 680, 200
    chy, chh = 96, 250
    frags.append(rect(chx, chy, chw, chh, fill="#f4f6f8", stroke=INK, sw=2))
    frags.append(text(chx + chw / 2, chy + 28, "БАЛАНСНА ЗАРЯДКА", size=13, bold=True, color=INK))
    frags.append(text(chx + chw / 2, chy + 50, "iMAX-B6 і подібні", size=11, color=MUTED, italic=True))
    # силовий вхід угорі box'а, балансирний — нижче
    pwr_in_y = chy + 96
    bal_in_y = chy + 200
    frags.append(fitbox(chx + 16, chy + 72, chw - 32, 48,
                        "силовий канал:\nжене струм у весь пакет (XT60)",
                        size=11, fill=PWR, stroke=POS, sw=1.4))
    frags.append(fitbox(chx + 16, chy + 150, chw - 32, 76,
                        "балансир:\nміряє КОЖНУ комірку (JST-XH)\nі зливає надлишок із повніших",
                        size=11, fill=BAL, stroke=FIELD, sw=1.4))

    # ── СИЛОВІ дроти XT60: верхній коридор (над балансирними) ─────────────────
    # виходять праворуч від пакета, ведуться вгору у вільний коридор, тоді в box
    pwr_corr_y = chy - 8            # горизонтальний коридор силових — над усім
    # + (верх пакета)
    frags.append(line(px + pw, node_y[3], px + pw + 70, node_y[3], color=POS, sw=3))
    frags.append(line(px + pw + 70, node_y[3], px + pw + 70, pwr_corr_y, color=POS, sw=3))
    frags.append(line(px + pw + 70, pwr_corr_y, chx + 40, pwr_corr_y, color=POS, sw=3))
    frags.append(line(chx + 40, pwr_corr_y, chx + 40, chy, color=POS, sw=3))
    # − (низ пакета) — окремою висотою в тому ж коридорі
    frags.append(line(px + pw, node_y[0], px + pw + 50, node_y[0], color=NEG, sw=3))
    frags.append(line(px + pw + 50, node_y[0], px + pw + 50, pwr_corr_y + 14, color=NEG, sw=3))
    frags.append(line(px + pw + 50, pwr_corr_y + 14, chx + 90, pwr_corr_y + 14, color=NEG, sw=3))
    frags.append(line(chx + 90, pwr_corr_y + 14, chx + 90, chy, color=NEG, sw=3))
    frags.append(text((px + pw + chx) / 2, pwr_corr_y - 10, "XT60 — два товсті силові", size=11.5, color=POS, bold=True))

    # ── БАЛАНСИРНІ дроти JST-XH: нижній коридор (під пакетом), у box З ЛІВА ────
    bal_corr_y = cys[2] + ch + 44   # горизонтальний коридор балансирних — під пакетом
    for i in range(4):
        sy = node_y[i]
        drop_x = px + pw + 26 + i * 15      # східчастий вихід праворуч від пакета
        ty = bal_corr_y + i * 12            # кожен дріт — своя висота в коридорі
        rise_x = chx - 70 + i * 15          # піднімається ЛІВОРУЧ від box'а
        enter_y = bal_in_y - 18 + i * 12    # входить у ліву грань box'а на своїй висоті
        frags.append(line(px + pw, sy, drop_x, sy, color=node_col[i], sw=1.5, dash="4 3"))
        frags.append(line(drop_x, sy, drop_x, ty, color=node_col[i], sw=1.5, dash="4 3"))
        frags.append(line(drop_x, ty, rise_x, ty, color=node_col[i], sw=1.5, dash="4 3"))
        frags.append(line(rise_x, ty, rise_x, enter_y, color=node_col[i], sw=1.5, dash="4 3"))
        frags.append(line(rise_x, enter_y, chx, enter_y, color=node_col[i], sw=1.5, dash="4 3"))
    frags.append(text((px + pw + chx) / 2 - 20, bal_corr_y - 12, "JST-XH — 4 тонкі (на кожен вузол)",
                      size=11.5, color=FIELD, bold=True))

    # висновок унизу
    frags.append(text(W / 2, H - 22,
                      "Силовий вивід тільки ллє загальний струм і НЕ бачить окремих комірок — вирівнює лише балансир.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'charging.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (для hist-вставки): лінія часу народження LiPo — від сухого полімеру
# Армана (1978) через рідкий Li-ion Sony (1991) до гелевого пакетика Bellcore
# (патент 1994) і перших комерційних LiPo (PLiON 1996 → телефон Ericsson 1999).
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 980, 520
    frags = []
    frags.append(text(W / 2, 34, "Як народився літій-полімерний акумулятор", size=17, bold=True))

    # горизонтальна вісь часу
    ax_y = 250
    x0, x1 = 70, W - 70
    frags.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.5))
    frags.append(arrow(x1 - 2, ax_y, x1 + 14, ax_y, color=INK, sw=2.5))
    frags.append(text(x1 + 20, ax_y + 5, "час", size=12, color=MUTED, anchor="start"))

    # роки й підписи: (рік, зверху?, колір-крапки, короткий заголовок, пояснення-рядки)
    events = [
        (1978, True,  NEG,   "1978 · сухий полімер",
         ["Мішель Арман:", "ідея твердого", "полімер-електроліту", "(PEO+Li). Гарний,", "але надто повільний."]),
        (1991, False, MUTED, "1991 · рідкий Li-ion",
         ["Sony (кер. Йосіо Нісі):", "перша комерційна", "Li-ion банка —", "циліндр, рідкий", "електроліт."]),
        (1994, True,  POS,   "1994 · гель у пакетику",
         ["Bellcore (Ґодз,", "Шмуц, Тараскон):", "патент на PVDF-гель.", "Плаский м'який", "пакетик замість банки."]),
        (1996, False, FIELD, "1996 · PLiON",
         ["Bellcore називає це", "«plastic Li-ion»", "(PLiON) — вже не", "лабораторія, а", "готова технологія."]),
        (1999, True,  POS,   "1999 · у кишені",
         ["Ericsson T28s:", "перший телефон", "на LiPo. Ультратонка", "комірка 500 мА·год", "робить апарат тонким."]),
    ]

    xs = [x0 + 60 + i * ((x1 - x0 - 120) / 4) for i in range(5)]
    for (yr, up, col, head, body), cx in zip(events, xs):
        # крапка на осі
        frags.append(circle(cx, ax_y, 9, fill=col, stroke=INK, sw=1.8))
        # виносна лінія до картки
        card_gap = 120
        cw2, ch2 = 186, 100
        if up:
            frags.append(line(cx, ax_y - 9, cx, ax_y - card_gap + 4, color=col, sw=1.5, dash="3 3"))
            bx, by = cx - cw2 / 2, ax_y - card_gap - ch2
        else:
            frags.append(line(cx, ax_y + 9, cx, ax_y + card_gap - 4, color=col, sw=1.5, dash="3 3"))
            bx, by = cx - cw2 / 2, ax_y + card_gap
        # картка: заголовок + дрібне пояснення
        frags.append(rect(bx, by, cw2, ch2, fill="#f8fafc", stroke=col, sw=1.8))
        frags.append(text(cx, by + 20, head, size=12.5, color=INK, bold=True))
        frags.append(mtext(cx, by + 38, body, size=10.5, color=MUTED, lh=1.28))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_anatomy()
    fig_window()
    fig_charging()
    fig_timeline()
    print("ok")
