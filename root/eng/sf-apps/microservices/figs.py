# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox at center, returns (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: моноліт (виклики в процесі) проти мікросервісів (мережа) ───────
def monolith_vs_micro():
    W, H = 980, 600
    parts = []
    parts.append(text(W / 2, 32, "Один процес проти багатьох за мережею",
                      size=18, bold=True))

    # роздільна вертикаль
    parts.append(line(W / 2, 62, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 60, "МОНОЛІТ · один процес", size=13, bold=True, color=MUTED))
    parts.append(text(W * 3 / 4, 60, "МІКРОСЕРВІСИ · мережа", size=13, bold=True, color=FIELD))

    modules = ["замовлення", "оплата", "склад"]

    # ---- ЛІВА половина: рамка процесу, три модулі, прямі виклики між ними ----
    lx = W / 4
    # велика рамка «процес»
    parts.append(rect(lx - 190, 92, 380, 300, stroke=MUTED, fill="#f3f4f6", rx=10))
    parts.append(text(lx, 112, "процес застосунку", size=12, italic=True, color=MUTED))

    lpos = [(lx, 175), (lx - 105, 320), (lx + 105, 320)]
    lhalf = []
    for (cx, cy), name in zip(lpos, modules):
        b, bw, bh = box_at(cx, cy, name, size=13, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=140)
        parts.append(b)
        lhalf.append((cx, cy, bw, bh))
    # прямі виклики: замовлення→оплата, замовлення→склад
    (ox, oy, ow, oh) = lhalf[0]
    for (cx, cy, bw, bh) in lhalf[1:]:
        parts.append(arrow(ox, oy + oh, cx, cy - bh, color=NEG, sw=1.8))

    # спільна база під процесом; конектор іде збоку від модулів, не крізь підписи
    db, dbw, dbh = box_at(lx, 468, "спільна база", size=12, bold=True,
                          fill=FILL, stroke=MUTED, min_w=160)
    parts.append(db)
    parts.append(arrow(lx, 355, lx, 468 - dbh, color=MUTED, sw=1.4))
    # підписи-висновки — ПІД базою, поза шляхом конектора
    parts.append(text(lx, 512, "виклик функції: наносекунди, надійно",
                      size=12, italic=True, color=NEG))
    parts.append(text(lx, 533, "але межу легко обійти", size=12, italic=True, color=NEG))

    # ---- ПРАВА половина: три окремі процеси зі своїми базами, мережа між ними ----
    rx = W * 3 / 4
    rpos = [(rx, 165), (rx - 120, 335), (rx + 120, 335)]
    rhalf = []
    for (cx, cy), name in zip(rpos, modules):
        # процес = коробка сервісу + власна база під нею
        b, bw, bh = box_at(cx, cy, name, size=13, bold=True,
                           fill="#eaf7ef", stroke=FIELD, min_w=150)
        parts.append(b)
        rhalf.append((cx, cy, bw, bh))
        # власна база
        dby = cy + bh + 40
        d, dw, dh = box_at(cx, dby, "своя база", size=11,
                           fill=FILL, stroke=FIELD, min_w=110)
        parts.append(d)
        parts.append(arrow(cx, cy + bh, cx, dby - dh, color=FIELD, sw=1.2))

    # мережеві виклики замовлення→оплата, замовлення→склад
    # (пунктирна лінія = мережа); старт від НИЖНІХ КУТІВ коробки замовлення,
    # щоб діагоналі обходили його власну базу під ним
    (ox, oy, ow, oh) = rhalf[0]
    corner_dx = ow - 10
    for sign, (cx, cy, bw, bh) in zip((-1, 1), rhalf[1:]):
        sx = ox + sign * corner_dx
        parts.append(line(sx, oy + oh, cx, cy - bh, color=FIELD, sw=1.8, dash="5 4"))
    parts.append(text(rx, 512, "виклик по мережі: мілісекунди,",
                      size=12, italic=True, color=FIELD))
    parts.append(text(rx, 533, "може зависнути — зате межу обійти не можна",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "monolith-vs-micro.svg"), W, H, *parts)


# ── Фігура 2: дві лінії розрізу — по шарах проти по контекстах ───────────────
def slicing_lines():
    W, H = 1000, 560
    parts = []
    parts.append(text(W / 2, 32, "Дві лінії розрізу одного застосунку",
                      size=18, bold=True))
    parts.append(line(W / 2, 62, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 60, "ПО ШАРАХ (погано)", size=13, bold=True, color=POS))
    parts.append(text(W * 3 / 4, 60, "ПО КОНТЕКСТАХ (добре)", size=13, bold=True, color=FIELD))

    contexts = ["замовлення", "оплата", "склад"]
    layers = ["контролери", "логіка", "база"]

    # ── ЛІВА: горизонтальні шари, вимога перетинає всі три ──
    lx = W / 4
    grid_w = 360
    cell_w = grid_w / 3
    x0 = lx - grid_w / 2
    ly0 = 110
    row_h = 74
    # три горизонтальні смуги-шари
    for r, lname in enumerate(layers):
        cy = ly0 + r * row_h + row_h / 2
        parts.append(rect(x0, ly0 + r * row_h, grid_w, row_h - 12,
                          stroke=POS, fill="#fdecea", rx=6))
        parts.append(text(x0 - 12, cy, lname, size=11, color=POS, anchor="end"))
    # вертикальна «вимога», що прошиває всі шари
    req_x = x0 + cell_w * 1.5
    top_y = ly0 - 14
    bot_y = ly0 + 3 * row_h - 6
    parts.append(arrow(req_x, top_y, req_x, bot_y, color=INK, sw=2.6))
    parts.append(text(req_x, top_y - 10, "одна вимога", size=12, bold=True, color=INK))
    parts.append(text(lx, bot_y + 34, "зачіпає ВСІ сервіси —",
                      size=12, italic=True, color=POS))
    parts.append(text(lx, bot_y + 55, "викочувати доводиться разом",
                      size=12, italic=True, color=POS))

    # ── ПРАВА: вертикальні контексти, вимога всередині одного ──
    rx = W * 3 / 4
    rx0 = rx - grid_w / 2
    ry0 = 110
    col_h = 3 * row_h - 12
    for c, cname in enumerate(contexts):
        cxx = rx0 + c * cell_w
        parts.append(rect(cxx + 6, ry0, cell_w - 12, col_h,
                          stroke=FIELD, fill="#eaf7ef", rx=6))
        parts.append(text(cxx + cell_w / 2, ry0 - 12, cname,
                          size=11, color=FIELD))
    # вимога всередині середнього стовпця
    mid_cx = rx0 + cell_w * 1.5
    parts.append(arrow(mid_cx, ry0 + 16, mid_cx, ry0 + col_h - 16,
                       color=INK, sw=2.6))
    parts.append(text(mid_cx, ry0 + col_h + 22, "одна вимога",
                      size=12, bold=True, color=INK))
    parts.append(text(rx, ry0 + col_h + 52, "лягає в ОДИН сервіс —",
                      size=12, italic=True, color=FIELD))
    parts.append(text(rx, ry0 + col_h + 73, "викотити можна окремо",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "slicing-lines.svg"), W, H, *parts)


# ── Фігура 3 (вставка proj): наївний потік проти надійного (outbox+подія+ідемпотентність)
def order_saga_flow():
    W, H = 1040, 720
    parts = []
    parts.append(text(W / 2, 30, "Дві межі: наївний обмін проти надійного",
                      size=18, bold=True))
    parts.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "НАЇВНО · два віддалені записи", size=13, bold=True, color=POS))
    parts.append(text(W * 3 / 4, 56, "НАДІЙНО · намір → подія → дедуп", size=13, bold=True, color=FIELD))

    # ── ЛІВА половина: замовлення пише у власну базу, потім кличе склад; падіння посередині ──
    lx = W / 4
    (ord_l, w1, h1) = box_at(lx, 120, "сервіс\nзамовлень", size=13, bold=True,
                             fill="#eaf0fd", stroke=NEG, min_w=150)
    parts.append(ord_l)
    (stk_l, w2, h2) = box_at(lx, 330, "сервіс складу", size=13, bold=True,
                             fill="#eaf0fd", stroke=NEG, min_w=150)
    parts.append(stk_l)
    # база складу під ним
    (sdb_l, w3, h3) = box_at(lx, 430, "база складу", size=11,
                             fill=FILL, stroke=NEG, min_w=140)
    parts.append(sdb_l)
    parts.append(arrow(lx, 330 + h2, lx, 430 - h3, color=NEG, sw=1.2))
    # крок 1: віддалений виклик «спиши товар»
    parts.append(arrow(lx, 120 + h1, lx, 330 - h2, color=POS, sw=2.2))
    parts.append(text(lx + 12, 210, "1. спиши товар", size=12, color=POS, anchor="start"))
    parts.append(text(lx + 12, 232, "(склад списав ✓)", size=11, italic=True, color=MUTED, anchor="start"))
    # крок 2: замовлення падає, не записавши себе
    (crash, cw, ch) = box_at(lx, 545, "✗ ПАДІННЯ до запису\nзамовлення", size=12, bold=True,
                             fill="#fdecea", stroke=POS, min_w=210)
    parts.append(crash)
    parts.append(text(lx, 620, "товар списаний, замовлення НЕМА —",
                      size=12, italic=True, color=POS))
    parts.append(text(lx, 641, "одиниця зникла в нікуди",
                      size=12, italic=True, color=POS))

    # ── ПРАВА половина: outbox у власній транзакції → черга → ідемпотентний склад ──
    rx = W * 3 / 4
    # 1) замовлення: одна локальна транзакція пише замовлення + рядок outbox
    (ord_r, rw1, rh1) = box_at(rx, 118, "сервіс замовлень", size=13, bold=True,
                               fill="#eaf7ef", stroke=FIELD, min_w=170)
    parts.append(ord_r)
    (obx, obw, obh) = box_at(rx, 205, "1 транзакція:\nзамовлення + outbox", size=11, bold=True,
                             fill=FILL, stroke=FIELD, min_w=210)
    parts.append(obx)
    parts.append(arrow(rx, 118 + rh1, rx, 205 - obh, color=FIELD, sw=1.4))
    # 2) реле → черга
    (q, qw, qh) = box_at(rx, 330, "черга\n(подія OrderPlaced)", size=11, bold=True,
                         fill="#fff4e0", stroke="#b8860b", min_w=210)
    parts.append(q)
    parts.append(arrow(rx, 205 + obh, rx, 330 - qh, color=FIELD, sw=1.8))
    parts.append(text(rx + 118, 268, "реле шле", size=11, italic=True, color=MUTED, anchor="middle"))
    parts.append(text(rx + 118, 286, "асинхронно", size=11, italic=True, color=MUTED, anchor="middle"))
    # 3) склад: ідемпотентний споживач із таблицею оброблених eventId
    (stk_r, sw1, sh1) = box_at(rx, 455, "сервіс складу", size=13, bold=True,
                               fill="#eaf7ef", stroke=FIELD, min_w=170)
    parts.append(stk_r)
    parts.append(arrow(rx, 330 + qh, rx, 455 - sh1, color=FIELD, sw=1.8))
    (dedup, dw, dh) = box_at(rx, 545, "бачив цей eventId?\nтак → пропусти", size=11, bold=True,
                             fill=FILL, stroke=FIELD, min_w=210)
    parts.append(dedup)
    parts.append(arrow(rx, 455 + sh1, rx, 545 - dh, color=FIELD, sw=1.4))
    parts.append(text(rx, 620, "падіння будь-де → подія в черзі чекає;",
                      size=12, italic=True, color=FIELD))
    parts.append(text(rx, 641, "повтор доставки — дедуп ловить дубль",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "order-saga-flow.svg"), W, H, *parts)


if __name__ == "__main__":
    monolith_vs_micro()
    slicing_lines()
    order_saga_flow()
    print("figures written to", IMG)
