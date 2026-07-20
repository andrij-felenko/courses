# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox по центру, повертає (svg, півширина, піввисота)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


def lifeline(x, y0, y1):
    return line(x, y0, x, y1, color=MUTED, sw=1.4, dash="4 7")


# ── Фігура 1: опитування проти вебхука ──────────────────────────────────────
def poll_vs_webhook():
    W, H = 980, 520
    p = []
    p.append(text(W / 2, 32, "Опитування проти вебхука", size=18, bold=True))
    p.append(line(W / 2, 55, W / 2, 495, color=MUTED, sw=1, dash="6 6"))
    p.append(text(245, 60, "ОПИТУВАННЯ (POLLING)", size=13, bold=True, color=NEG))
    p.append(text(735, 60, "ВЕБХУК (WEBHOOK)", size=13, bold=True, color=FIELD))

    # ---- ліва половина: споживач раз за разом смикає провайдера ----
    cx, px = 135, 365
    b, _, _ = box_at(cx, 90, "Споживач", size=13, bold=True, fill="#eaf0fd", stroke=NEG, min_w=130)
    p.append(b)
    b, _, _ = box_at(px, 90, "Провайдер", size=13, bold=True, min_w=130)
    p.append(b)
    p.append(lifeline(cx, 108, 478))
    p.append(lifeline(px, 108, 478))

    for y in (140, 205):
        p.append(arrow(cx + 12, y, px - 12, y, color=NEG, sw=1.6))
        p.append(text(250, y - 9, "є нове?", size=12, color=NEG))
        p.append(arrow(px - 12, y + 26, cx + 12, y + 26, color=MUTED, sw=1.4))
        p.append(text(250, y + 17, "нема", size=12, color=MUTED))
    p.append(text(250, 258, "⋮", size=20, color=MUTED))  # ⋮ — так знову й знову

    # подія стається між опитуваннями — і чекає до наступного
    p.append(circle(px, 292, 7, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(378, 296, "подія", size=12, color=POS, anchor="start"))
    p.append(arrow(cx + 12, 335, px - 12, 335, color=NEG, sw=1.6))
    p.append(text(250, 326, "є нове?", size=12, color=NEG))
    p.append(arrow(px - 12, 361, cx + 12, 361, color=POS, sw=1.7))
    p.append(text(250, 352, "є!", size=12, color=POS, bold=True))
    p.append(text(245, 452, "порожні обходи, і подія жде опитування",
                  size=12, italic=True, color=MUTED))

    # ---- права половина: провайдер кличе в мить події ----
    qx, sx = 615, 855
    b, _, _ = box_at(qx, 90, "Провайдер", size=13, bold=True, min_w=130)
    p.append(b)
    b, _, _ = box_at(sx, 90, "Споживач", size=13, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=130)
    p.append(b)
    p.append(lifeline(qx, 108, 478))
    p.append(lifeline(sx, 108, 478))

    p.append(circle(qx, 178, 7, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(573, 182, "подія", size=12, color=POS, anchor="middle"))
    p.append(arrow(qx + 12, 178, sx - 12, 178, color=FIELD, sw=2))
    p.append(text(735, 169, "POST подія", size=12, color=FIELD, bold=True))
    p.append(arrow(sx - 12, 206, qx + 12, 206, color=MUTED, sw=1.4))
    p.append(text(735, 197, "200", size=12, color=MUTED))
    p.append(text(735, 452, "один виклик, тієї ж миті",
                  size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "poll-vs-webhook.svg"), W, H, *p)


# ── Фігура 2: конвеєр приймача — два вартові, швидкий ack, обробка окремо ─────
def consumer_pipeline():
    W, H = 1000, 470
    p = []
    p.append(text(W / 2, 32, "Конвеєр приймача: прийняти швидко, обробити потім", size=18, bold=True))

    y = 150
    entry, ew, eh = box_at(105, y, "POST\n/webhooks", size=13, bold=True, min_w=150)
    g1, g1w, g1h = box_at(320, y, "перевірити\nпідпис", size=13, bold=True,
                          fill="#eaf0fd", stroke=NEG, min_w=150)
    g2, g2w, g2h = box_at(535, y, "дедуп за\nevent ID", size=13, bold=True,
                          fill="#eaf0fd", stroke=NEG, min_w=150)
    q0, q0w, q0h = box_at(720, y, "у чергу", size=13, bold=True, min_w=120)
    ack, aw, ah = box_at(890, y, "200\n(ack)", size=13, bold=True,
                         fill="#eaf7ef", stroke=FIELD, min_w=110)
    for b in (entry, g1, g2, q0, ack):
        p.append(b)
    p.append(arrow(105 + ew, y, 320 - g1w, y, sw=1.7))
    p.append(arrow(320 + g1w, y, 535 - g2w, y, sw=1.7))
    p.append(arrow(535 + g2w, y, 720 - q0w, y, sw=1.7))
    p.append(arrow(720 + q0w, y, 890 - aw, y, color=FIELD, sw=1.8))

    # відгалуження вартових — коротка відповідь прямо в запиті
    rej, rw, rh = box_at(320, 262, "401\nпідпис не той", size=12,
                         fill="#fdecea", stroke=POS, min_w=155)
    p.append(rej)
    p.append(arrow(320, y + g1h, 320, 262 - rh, color=POS, sw=1.5))
    dup, dw, dh = box_at(535, 262, "200, no-op\nдубль", size=12,
                         fill=FILL, stroke=MUTED, min_w=155)
    p.append(dup)
    p.append(arrow(535, y + g2h, 535, 262 - dh, color=MUTED, sw=1.5))

    # межа: у запиті / поза запитом
    p.append(line(40, 312, 960, 312, color=MUTED, sw=1, dash="6 6"))
    p.append(text(48, 112, "у запиті — тонко і швидко", size=12, bold=True,
                  color=MUTED, anchor="start"))
    p.append(text(952, 340, "поза запитом", size=12, bold=True,
                  color=MUTED, anchor="end"))

    # нижня смуга: черга й робітник
    yb = 385
    qb, qbw, qbh = box_at(720, yb, "черга", size=13, bold=True, min_w=120)
    wk, wkw, wkh = box_at(455, yb, "робітник\nобробляє", size=13, bold=True,
                          fill="#eaf7ef", stroke=FIELD, min_w=165)
    p.append(qb)
    p.append(wk)
    p.append(arrow(720, y + q0h, 720, yb - qbh, color=FIELD, sw=1.8))
    p.append(arrow(720 - qbw, yb, 455 + wkw, yb, color=FIELD, sw=1.7))
    p.append(text(455, yb + wkh + 22, "асинхронно, скільки треба",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "consumer-pipeline.svg"), W, H, *p)


# ── Фігура 3: at-least-once — загублений 200, повтор і дедуп ─────────────────
def at_least_once():
    W, H = 980, 560
    p = []
    p.append(text(W / 2, 32, "Доставка «щонайменше раз»: повтор і його гасіння", size=18, bold=True))

    px, sx = 280, 700
    b, _, _ = box_at(px, 82, "Провайдер", size=13, bold=True, min_w=140)
    p.append(b)
    b, _, _ = box_at(sx, 82, "Споживач", size=13, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=140)
    p.append(b)
    p.append(lifeline(px, 100, 500))
    p.append(lifeline(sx, 100, 500))

    # 1) перша доставка, споживач обробляє
    p.append(arrow(px + 14, 132, sx - 14, 132, color=INK, sw=1.8))
    p.append(text(490, 122, "POST evt_123", size=12, bold=True))
    nb, nbw, nbh = box_at(842, 168, "обробив,\nзберіг evt_123", size=12,
                          fill="#eaf7ef", stroke=FIELD, min_w=160)
    p.append(nb)

    # 2) відповідь 200 губиться в дорозі (стрілка не доходить)
    p.append(line(sx - 14, 224, 470, 224, color=POS, sw=1.7, dash="6 5"))
    p.append(text(452, 229, "✗", size=17, color=POS, bold=True))  # ✗
    p.append(text(600, 214, "200 — загублено", size=12, color=POS))

    # 3) провайдер не почув — повторює
    nb, nbw, nbh = box_at(150, 268, "не почув 200", size=12, min_w=150)
    p.append(nb)
    p.append(arrow(px + 14, 322, sx - 14, 322, color=INK, sw=1.8))
    p.append(text(490, 312, "POST evt_123 (повтор)", size=12, bold=True))

    # 4) споживач упізнає дубль — тихий 200
    nb, nbw, nbh = box_at(842, 358, "evt_123 —\nвже бачив", size=12,
                          fill="#fdf3e0", stroke=POS, min_w=160)
    p.append(nb)
    p.append(arrow(sx - 14, 412, px + 14, 412, color=FIELD, sw=1.8))
    p.append(text(490, 402, "200 — нічого не роблю", size=12, bold=True, color=FIELD))

    p.append(text(W / 2, 472, "дубль — норма моделі, а не збій", size=13, italic=True, color=MUTED))
    p.append(text(W / 2, 496, "унікальний ID гасить його без подвійного ефекту",
                  size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "at-least-once.svg"), W, H, *p)


# ── Фігура 4: архітектура стійкого приймача — тривка скринька й 4 механізми ───
def robust_architecture():
    W, H = 1080, 620
    p = []
    p.append(text(W / 2, 34, "Стійкий приймач: одна тривка істина, чотири механізми", size=18, bold=True))

    # осердя — скринька в базі
    ib, ibw, ibh = box_at(540, 300,
                          "webhook_inbox (БД)\nUNIQUE event_id\nreceived → processing → done | dead",
                          size=13, bold=True, fill="#eef6ff", stroke=NEG, sw=2, min_w=360)
    p.append(text(540, 300 + ibh + 24, "одна тривка істина — рядок скриньки",
                  size=12, italic=True, color=MUTED))

    # чотири механізми по кутах
    m1, m1w, m1h = box_at(210, 130, "①  Синхронний прийом\nпідпис · вставка-дедуп",
                          size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=270)
    p.append(m1)
    p.append(text(210, 130 + m1h + 20, "проти повторних доставок", size=11, color=MUTED))

    m2, m2w, m2h = box_at(870, 130, "②  Робітник\nстан-машина в 1 транзакції",
                          size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=270)
    p.append(m2)
    p.append(text(870, 130 + m2h + 20, "проти повторної обробки", size=11, color=MUTED))

    m3, m3w, m3h = box_at(210, 470, "③  Прибиральник\n'received' застрягле → у чергу",
                          size=12, bold=True, min_w=270)
    p.append(m3)
    p.append(text(210, 470 + m3h + 20, "проти втрати між БД і чергою", size=11, color=MUTED))

    m4, m4w, m4h = box_at(870, 470, "④  Звірка\nтягне API провайдера → вставка-дедуп",
                          size=12, bold=True, min_w=300)
    p.append(m4)
    p.append(text(870, 470 + m4h + 20, "проти облишених провайдером", size=11, color=MUTED))

    # стрілки: кожен механізм — до/від осердя (правдиве відношення читання/запису)
    p.append(arrow(210 + m1w * 0.7, 130 + m1h, 540 - ibw * 0.8, 300 - ibh, color=NEG, sw=1.7))     # ① пише
    p.append(arrow(870 - m2w * 0.7, 130 + m2h, 540 + ibw * 0.8, 300 - ibh, color=FIELD, sw=1.7))   # ② читає+пише
    p.append(arrow(540 - ibw * 0.8, 300 + ibh, 210 + m3w * 0.7, 470 - m3h, color=INK, sw=1.7))     # ③ читає
    p.append(arrow(870 - m4w * 0.7, 470 - m4h, 540 + ibw * 0.8, 300 + ibh, color=INK, sw=1.7))     # ④ пише

    render(os.path.join(IMG, "robust-architecture.svg"), W, H, *p)


# ── Фігура 5: стан-машина рядка скриньки — чому повтор нічого не псує ─────────
def inbox_state_machine():
    W, H = 1000, 560
    p = []
    p.append(text(W / 2, 34, "Життя події у скриньці: кожен перехід — заслінка проти повтору", size=17, bold=True))

    yb = 175
    rec, rw, rh = box_at(230, yb, "received", size=14, bold=True, fill=FILL, stroke=MUTED, min_w=150)
    prc, pw, ph = box_at(530, yb, "processing", size=14, bold=True, fill="#eaf0fd", stroke=NEG, min_w=150)
    dn, dw, dh = box_at(825, yb, "done", size=14, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=140)
    dead, ddw, ddh = box_at(640, 405, "dead", size=14, bold=True, fill="#fdecea", stroke=POS, min_w=140)
    for b in (rec, prc, dn, dead):
        p.append(b)

    # вхід: нова подія
    p.append(text(70, yb - 20, "нова", size=12, color=MUTED))
    p.append(arrow(72, yb, 230 - rw, yb, sw=1.6))
    p.append(text(150, yb - 20, "вставка-дедуп", size=11, color=MUTED, anchor="middle"))
    p.append(text(150, yb + 26, "(UNIQUE)", size=11, color=MUTED, anchor="middle"))

    # received → processing
    p.append(arrow(230 + rw, yb, 530 - pw, yb, color=NEG, sw=1.7))
    p.append(text(380, yb - 22, "бере FOR UPDATE", size=11, color=NEG, anchor="middle"))
    p.append(text(380, yb + 26, "лише якщо 'received'", size=11, color=NEG, anchor="middle"))

    # processing → done
    p.append(arrow(530 + pw, yb, 825 - dw, yb, color=FIELD, sw=1.7))
    p.append(text(678, yb - 22, "ефект + відмітка", size=11, color=FIELD, anchor="middle"))
    p.append(text(678, yb + 26, "в ОДНІЙ транзакції", size=11, color=FIELD, anchor="middle"))
    p.append(text(825, yb + rh + 18, "тихо ack", size=11, italic=True, color=MUTED))

    # processing → received (збій, rollback) — нижня зворотна петля
    p.append(line(490, yb + ph, 490, yb + 78, color=POS, sw=1.5))
    p.append(arrow(490, yb + 78, 230, yb + 78, color=POS, sw=1.5))
    p.append(line(230, yb + 78, 230, yb + rh, color=POS, sw=1.5))
    p.append(text(360, yb + 98, "збій → ROLLBACK · attempts+1 · назад у чергу",
                  size=11, color=POS, anchor="middle"))

    # processing → dead
    p.append(arrow(575, yb + ph, 625, 405 - ddh, color=POS, sw=1.6))
    p.append(text(655, 320, "attempts ≥ MAX", size=11, color=POS, anchor="start"))

    # dead → received (людина полагодила) — пунктир нижнім каналом, повз усі написи
    p.append(line(640 - ddw, 405, 640 - ddw, 470, color=MUTED, sw=1.4, dash="5 5"))
    p.append(line(640 - ddw, 470, 200, 470, color=MUTED, sw=1.4, dash="5 5"))
    p.append(arrow(200, 470, 200, yb + rh, color=MUTED, sw=1.4))
    p.append(text(400, 464, "людина полагодила: dead → received", size=11, color=MUTED, anchor="middle"))

    p.append(text(W / 2, 522,
                  "Повтор доставки, повтор черги, гонка робітників, рестарт — усі впираються в 'done' і виходять без ефекту.",
                  size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, "inbox-state-machine.svg"), W, H, *p)


if __name__ == "__main__":
    poll_vs_webhook()
    consumer_pipeline()
    at_least_once()
    robust_architecture()
    inbox_state_machine()
    print("figures written to", IMG)
