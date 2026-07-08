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


# ── Фігура 1: шина в пам'яті проти брокера між сервісами ─────────────────────
def inmem_vs_broker():
    W, H = 960, 500
    parts = []
    parts.append(text(W / 2, 30, "Що змінюється, коли видавець і підписник — різні сервіси",
                      size=18, bold=True))
    parts.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "ОДИН ПРОЦЕС · ШИНА В ПАМ'ЯТІ", size=12, bold=True, color=NEG))
    parts.append(text(W * 3 / 4, 56, "РІЗНІ СЕРВІСИ · БРОКЕР", size=12, bold=True, color=FIELD))

    # ---- ліва половина: одна межа процесу, шина = об'єкт у пам'яті ----
    lx = W / 4
    # рамка процесу
    parts.append(rect(lx - 165, 82, 330, 300, fill="#fbfcfd", stroke=NEG, sw=1.5))
    parts.append(text(lx, 100, "процес застосунку", size=12, italic=True, color=NEG))

    pub, phw, phh = box_at(lx, 145, "видавець", size=13, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=140)
    parts.append(pub)
    bus, bhw, bhh = box_at(lx, 240, ["шина", "(об'єкт у пам'яті)"], size=12, bold=True,
                           fill=FILL, stroke=NEG, min_w=200)
    parts.append(bus)
    sub, shw, shh = box_at(lx, 345, "підписник", size=13, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=140)
    parts.append(sub)
    parts.append(arrow(lx, 145 + phh, lx, 240 - bhh, color=NEG, sw=1.8))
    parts.append(arrow(lx, 240 + bhh, lx, 345 - shh, color=NEG, sw=1.8))
    parts.append(text(lx, 430, "рестарт процесу — черга зникає разом", size=12,
                      italic=True, color=POS))
    parts.append(text(lx, 450, "з пам'яттю; ніщо не переживає падіння", size=12,
                      italic=True, color=POS))

    # ---- права половина: дві окремі межі + брокер поза ними ----
    rx = W * 3 / 4
    # сервіс-видавець (ліва коробка процесу)
    sx1 = rx - 130
    parts.append(rect(sx1 - 78, 105, 156, 84, fill="#fbfcfd", stroke=FIELD, sw=1.5))
    parts.append(text(sx1, 122, "сервіс A", size=11, italic=True, color=FIELD))
    pb, pbw, pbh = box_at(sx1, 158, "видавець", size=12, bold=True,
                          fill="#eaf7ef", stroke=FIELD, min_w=120)
    parts.append(pb)

    # сервіс-підписник (права коробка процесу)
    sx2 = rx + 130
    parts.append(rect(sx2 - 78, 105, 156, 84, fill="#fbfcfd", stroke=FIELD, sw=1.5))
    parts.append(text(sx2, 122, "сервіс B", size=11, italic=True, color=FIELD))
    sb, sbw, sbh = box_at(sx2, 158, "підписник", size=12, bold=True,
                          fill="#eaf7ef", stroke=FIELD, min_w=120)
    parts.append(sb)

    # брокер посередині-внизу, поза обома процесами
    broy = 300
    bro, brhw, brhh = box_at(rx, broy, ["брокер", "(журнал на диску)"], size=12, bold=True,
                             fill=FILL, stroke=FIELD, min_w=230)
    parts.append(bro)
    # видавець -> брокер (публікує)
    parts.append(arrow(sx1, 189, rx - brhw, broy - 8, color=FIELD, sw=1.8))
    parts.append(text(sx1 - 6, 250, "публікує", size=11, italic=True, color=FIELD))
    # брокер -> підписник (доставляє)
    parts.append(arrow(rx + brhw, broy - 8, sx2, 189, color=FIELD, sw=1.8))
    parts.append(text(sx2 + 6, 250, "доставляє", size=11, italic=True, color=FIELD, anchor="middle"))

    parts.append(text(rx, broy + brhh + 30, "рестарт будь-якого сервісу — брокер тримає", size=12,
                      italic=True, color=FIELD))
    parts.append(text(rx, broy + brhh + 50, "події на диску; підписник дочитає з місця, де спинився", size=12,
                      italic=True, color=FIELD))

    render(os.path.join(IMG, "inmem-vs-broker.svg"), W, H, *parts)


# ── Фігура 2: проблема подвійного запису і скринька-outbox ───────────────────
def dual_write():
    W, H = 980, 520
    parts = []
    parts.append(text(W / 2, 30, "Проблема подвійного запису та її лік — скринька",
                      size=18, bold=True))
    parts.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "ДВА ЗАПИСИ — РОЗ'ЇХАЛИСЯ", size=12, bold=True, color=POS))
    parts.append(text(W * 3 / 4, 56, "ОДИН ЗАПИС — АТОМАРНО", size=12, bold=True, color=FIELD))

    # ---- ліва: сервіс пише в базу (ок) і в брокер (впав) ----
    lx = W / 4
    svc, shw, shh = box_at(lx, 110, "сервіс", size=13, bold=True,
                           fill=FILL, stroke=INK, min_w=150)
    parts.append(svc)

    db, dbhw, dbhh = box_at(lx - 105, 250, ["база", "✓ записано"], size=12, bold=True,
                            fill="#eaf7ef", stroke=FIELD, min_w=150)
    parts.append(db)
    br, brhw, brhh = box_at(lx + 105, 250, ["брокер", "✗ не дійшло"], size=12, bold=True,
                            fill="#fdecea", stroke=POS, min_w=150)
    parts.append(br)
    parts.append(arrow(lx - 30, 110 + shh, lx - 105, 250 - dbhh, color=FIELD, sw=1.8))
    parts.append(arrow(lx + 30, 110 + shh, lx + 105, 250 - dbhh, color=POS, sw=1.8))

    # висновок розбіжності
    warn, whw, whh = box_at(lx, 400,
                            ["стан каже «сталося»,", "події немає — ніхто", "не дізнається. Розбіжність", "без транзакції, що їх обійме"],
                            size=12, fill="#fdecea", stroke=POS, min_w=270)
    parts.append(warn)

    # ---- права: одна транзакція пише і дані, і подію в скриньку ----
    rx = W * 3 / 4
    rsvc, rshw, rshh = box_at(rx, 110, "сервіс", size=13, bold=True,
                              fill=FILL, stroke=INK, min_w=150)
    parts.append(rsvc)

    # одна база, всередині — дані + скринька, обведені однією рамкою транзакції
    tx_x, tx_y, tx_w, tx_h = rx - 150, 200, 300, 120
    parts.append(rect(tx_x, tx_y, tx_w, tx_h, fill="#eaf7ef", stroke=FIELD, sw=2))
    parts.append(text(rx, tx_y + 20, "одна транзакція бази", size=12, italic=True, color=FIELD))
    d1, d1hw, d1hh = box_at(rx - 75, tx_y + 78, ["дані", "замовлення"], size=11, bold=True,
                            fill=BG, stroke=FIELD, min_w=120)
    parts.append(d1)
    d2, d2hw, d2hh = box_at(rx + 75, tx_y + 78, ["скринька:", "рядок-подія"], size=11, bold=True,
                            fill=BG, stroke=FIELD, min_w=120)
    parts.append(d2)
    parts.append(arrow(rx, 110 + rshh, rx, tx_y - 4, color=FIELD, sw=1.8))

    # окремий відправник вичитує скриньку -> брокер
    relay, rlhw, rlhh = box_at(rx, 400, "відправник читає скриньку → брокер",
                               size=12, bold=True, fill=FILL, stroke=FIELD, min_w=360)
    parts.append(relay)
    parts.append(arrow(rx, tx_y + tx_h, rx, 400 - rlhh, color=FIELD, sw=1.8))
    parts.append(text(rx, 400 + rlhh + 26, "або зберігся і факт, і намір його розіслати — або ні те, ні те",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "dual-write.svg"), W, H, *parts)


# ── Фігура 3: хореографія проти оркестрування ───────────────────────────────
def choreo_vs_orchestr():
    W, H = 980, 540
    parts = []
    parts.append(text(W / 2, 30, "Дві форми узгодження кроків між сервісами",
                      size=18, bold=True))
    parts.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "ХОРЕОГРАФІЯ", size=13, bold=True, color=NEG))
    parts.append(text(W * 3 / 4, 56, "ОРКЕСТРУВАННЯ", size=13, bold=True, color=FIELD))

    # ---- ліва: сервіси реагують на події одне одного, диригента нема ----
    lx = W / 4
    # три сервіси стовпчиком, кожен реагує на факт попереднього
    ly = [130, 270, 410]
    lnames = [["Замовлення", "→ ЗамовленняСтворено"],
              ["Оплата", "→ ОплатаПройшла"],
              ["Склад", "→ ТоварЗарезервовано"]]
    lcenters = []
    for name, y in zip(lnames, ly):
        b, bw, bh = box_at(lx, y, name, size=12, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=250)
        parts.append(b)
        lcenters.append((y, bh))
    # стрілки-факти між ними (кожен слухає попередній)
    for i in range(len(ly) - 1):
        y0 = lcenters[i][0] + lcenters[i][1]
        y1 = lcenters[i + 1][0] - lcenters[i + 1][1]
        parts.append(arrow(lx, y0, lx, y1, color=NEG, sw=1.9))
        parts.append(text(lx + 145, (y0 + y1) / 2 + 4, "факт", size=11, italic=True,
                          color=NEG, anchor="start"))
    parts.append(text(lx, 475, "диригента немає: кожен сам вирішує,", size=12,
                      italic=True, color=NEG))
    parts.append(text(lx, 495, "на який чужий факт реагувати", size=12,
                      italic=True, color=NEG))

    # ---- права: диригент шле команди й чекає відповіді ----
    rx = W * 3 / 4
    cond, chw, chh = box_at(rx, 150, ["диригент", "(сага-оркестратор)"], size=12, bold=True,
                            fill="#eaf7ef", stroke=FIELD, min_w=200)
    parts.append(cond)
    ry = [330, 420, 510]
    # три виконавці в ряд унизу
    rnames = ["Оплата", "Склад", "Доставка"]
    rcx = [rx - 150, rx, rx + 150]
    for name, cx in zip(rnames, rcx):
        b, bw, bh = box_at(cx, 360, name, size=12, bold=True,
                           fill=FILL, stroke=FIELD, min_w=120)
        parts.append(b)
        # команда вниз, відповідь угору (дві стрілки поряд)
        parts.append(arrow(rx + (cx - rx) * 0.6 - 8, 150 + chh, cx - 8, 360 - bh,
                           color=FIELD, sw=1.6))
    parts.append(text(rx, 435, "команда «зроби» вниз, «готово» вгору —", size=12,
                      italic=True, color=FIELD))
    parts.append(text(rx, 455, "хід саги знає одне місце: диригент", size=12,
                      italic=True, color=FIELD))

    render(os.path.join(IMG, "choreo-vs-orchestr.svg"), W, H, *parts)


if __name__ == "__main__":
    inmem_vs_broker()
    dual_write()
    choreo_vs_orchestr()
    print("figures written to", IMG)
