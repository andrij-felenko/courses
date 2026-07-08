# -*- coding: utf-8 -*-
# Фігури для вставки proj-layered-refactor.md (окремо від figs.py теми).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: поворот стрілки — до і після рефакторингу ──────────────────────
def fig_arrow_flip():
    W, H = 980, 560
    frags = []

    # два стовпці: ліворуч «до», праворуч «після»
    colL = 250
    colR = 730
    box_w = 300

    frags.append(text(colL, 44, "ДО: усе злиплося", size=16, bold=True, color=POS))
    frags.append(text(colR, 44, "ПІСЛЯ: стрілка вниз", size=16, bold=True, color=FIELD))

    # ── ЛІВОРУЧ: одна грудка ──
    lx = colL - box_w / 2
    frags.append(rect(lx, 84, box_w, 150, fill="#fdeef0", stroke=POS, sw=2, rx=10))
    frags.append(mtext(colL, 120, "Контролер", size=15, bold=True))
    frags.append(mtext(colL, 150,
                       "розбір HTTP  +  правило суми\n+  відкрити SQL  +  INSERT",
                       size=11.5, color=MUTED, lh=1.35))
    frags.append(text(colL, 214, "три справи в одному тілі", size=11.5,
                      italic=True, color=POS))
    # стрілка від грудки прямо в базу
    frags.append(arrow(colL, 234, colL, 300, color=POS, sw=2.6))
    frags.append(rect(lx + 50, 300, box_w - 100, 60, fill="#f2f2f5",
                      stroke=INK, sw=1.6, rx=8))
    frags.append(mtext(colL, 336, "Postgres", size=14, bold=True))
    frags.append(text(colL, 392, "щоб перевірити суму —", size=11.5, color=INK))
    frags.append(text(colL, 410, "треба підняти базу", size=11.5, color=INK))

    # ── ПРАВОРУЧ: три шари, обидві стрілки вниз ──
    rx = colR - box_w / 2
    ys = [84, 200, 316]
    labels = [
        ("Застосунок", "диригує кроками", "#eaf7ef"),
        ("Домен", "правило суми + інтерфейс OrderRepo", "#fff6e6"),
        ("Інфраструктура", "SqlOrderRepo реалізує інтерфейс", "#f2f2f5"),
    ]
    for (nm, desc, fill), yy in zip(labels, ys):
        frags.append(rect(rx, yy, box_w, 80, fill=fill, stroke=INK, sw=1.8, rx=9))
        frags.append(text(colR, yy + 32, nm, size=14, bold=True))
        frags.append(mtext(colR, yy + 56, desc, size=11, color=MUTED))

    # стрілка застосунок → домен (гукає)
    ax = rx - 30
    frags.append(arrow(ax, ys[0] + 72, ax, ys[1] + 8, color=FIELD, sw=2.4))
    # стрілка інфраструктура → домен (реалізує інтерфейс = залежить угору по коду,
    # але стрілка ЗАЛЕЖНОСТІ все одно вниз до абстракції домену) — ведемо праворуч
    bx = rx + box_w + 30
    frags.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.4" marker-end="url(#arrow)"/>'
                  % (bx, ys[2] + 8, bx, ys[1] + 72, FIELD)))
    frags.append(text(bx + 8, (ys[1] + ys[2]) / 2 + 40, "реалізує", size=10.5,
                      color=FIELD, anchor="start"))
    frags.append(text(ax - 8, (ys[0] + ys[1]) / 2 + 40, "гукає", size=10.5,
                      color=FIELD, anchor="end"))

    note, _, _ = textbox(colR, 472,
                         "Домен не знає ні про HTTP, ні про SQL.\n"
                         "Суму перевіряє тест БЕЗ бази; базу підмінюють фальшивкою.",
                         size=11.5, pad=12, fill="#ffffff", stroke="#d0d5db", sw=1.4)
    frags.append(note)

    render(os.path.join(IMG, 'arrow-flip.svg'), W, H, *frags)


# ── Фігура 2: один шов транзакції над кількома сховищами ─────────────────────
def fig_transaction_seam():
    W, H = 900, 500
    frags = []

    frags.append(text(W / 2, 42, "Транзакція — один шов над кількома сховищами",
                      size=15, bold=True))

    # верх: сценарій застосунку
    sx, sw_ = 300, 300
    frags.append(rect(sx, 78, sw_, 74, fill="#eaf7ef", stroke=INK, sw=1.8, rx=9))
    frags.append(text(sx + sw_ / 2, 108, "PlaceOrder.run()", size=14, bold=True))
    frags.append(text(sx + sw_ / 2, 132, "відкрив одиницю роботи → закрив",
                      size=11, color=MUTED))

    # межа транзакції — пунктирна рамка навколо двох сховищ
    tx, ty, tw, th = 150, 210, 600, 150
    frags.append(rect(tx, ty, tw, th, fill="#f7fbf8", stroke=FIELD, sw=2, rx=12,
                      ))
    # робимо рамку пунктирною окремою лінією-обводкою
    frags.append(('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="12" '
                  'fill="none" stroke="%s" stroke-width="2" '
                  'stroke-dasharray="7 5"/>' % (tx, ty, tw, th, FIELD)))
    frags.append(text(tx + 14, ty - 10, "одна транзакція: або всі, або жоден",
                      size=11.5, bold=True, color=FIELD, anchor="start"))

    # два сховища всередині
    r1x = tx + 60
    r2x = tx + tw - 60 - 200
    for xx, nm, tbl in [(r1x, "OrderRepo", "orders"),
                        (r2x, "StockRepo", "stock")]:
        frags.append(rect(xx, ty + 40, 200, 70, fill="#ffffff", stroke=INK, sw=1.6, rx=8))
        frags.append(text(xx + 100, ty + 70, nm, size=13, bold=True))
        frags.append(text(xx + 100, ty + 92, "пише в " + tbl, size=11, color=MUTED))

    # стрілки від сценарію вниз до кожного
    frags.append(arrow(sx + sw_ / 2 - 60, 152, r1x + 100, ty + 38, color=INK, sw=1.8))
    frags.append(arrow(sx + sw_ / 2 + 60, 152, r2x + 100, ty + 38, color=INK, sw=1.8))

    note, _, _ = textbox(W / 2, 420,
                         "Хто відкриває шов — знає застосунок, а не домен.\n"
                         "Обидва сховища сідають на ОДНЕ з'єднання; commit — один.",
                         size=11.5, pad=12, fill="#ffffff", stroke="#d0d5db", sw=1.4)
    frags.append(note)

    render(os.path.join(IMG, 'transaction-seam.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_arrow_flip()
    fig_transaction_seam()
    print("proj figures written to", IMG)
