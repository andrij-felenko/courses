# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Мотивація: SQL розсипано по коду проти зібраного у шлюз ────────────────
def fig_scatter_vs_gather():
    W, H = 1240, 515
    f = []
    f.append(text(W / 2, 30, "Розсипаний SQL проти зібраного у шлюз", size=17, bold=True))
    f.append(line(615, 58, 615, 486, color=MUTED, sw=1.2, dash="6 6"))

    # ══ ЛІВОРУЧ: розсипано ══
    f.append(text(315, 74, "SQL розсипано по коду", size=14, color=POS, bold=True))
    callers_l = [
        (112, "Контролер", "SELECT total FROM orders"),
        (192, "Звіт", "SELECT status, total …"),
        (272, "Фонова задача", "UPDATE orders SET …"),
    ]
    for y, name, sql in callers_l:
        f.append(rect(55, y, 200, 50, fill=FILL, stroke=LINE, sw=1.4, rx=6))
        f.append(text(155, y + 20, name, size=12, color=INK, bold=True))
        f.append(text(155, y + 40, sql, size=10, color=MUTED))

    # таблиця orders (ліва)
    f.append(rect(340, 150, 205, 30, fill=FILL, stroke=LINE, sw=1.4, rx=0))
    f.append(rect(340, 180, 205, 150, fill=BG, stroke=LINE, sw=1.4, rx=0))
    f.append(text(442, 170, "orders", size=11, color=MUTED, bold=True))
    rows_l = ["41 · 350 · new", "42 · 1200 · paid", "43 · 90 · shipped"]
    for i, r in enumerate(rows_l):
        f.append(text(442, 210 + i * 50, r, size=10, color=INK))
        if i:
            f.append(line(340, 180 + i * 50, 545, 180 + i * 50, color=MUTED, sw=1))

    f.append(arrow(257, 137, 338, 200, color=MUTED, sw=1.6))
    f.append(arrow(257, 217, 338, 242, color=MUTED, sw=1.6))
    f.append(arrow(257, 297, 338, 290, color=MUTED, sw=1.6))
    f.append(text(315, 468, "назви колонок протікають у кожне місце", size=12,
                  color=MUTED, italic=True))

    # ══ ПРАВОРУЧ: зібрано ══
    f.append(text(915, 74, "SQL зібрано у шлюз", size=14, color=FIELD, bold=True))
    callers_r = [
        (110, "Контролер", "gateway.find(42)"),
        (180, "Звіт", "gateway.findByStatus(…)"),
        (250, "Фонова задача", "gateway.update(42, …)"),
    ]
    for y, name, call in callers_r:
        f.append(rect(650, y, 195, 46, fill=FILL, stroke=LINE, sw=1.4, rx=6))
        f.append(text(747, y + 19, name, size=11.5, color=INK, bold=True))
        f.append(text(747, y + 37, call, size=10, color=NEG))

    # шлюз
    f.append(rect(880, 150, 180, 150, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    f.append(text(970, 178, "OrderTableGateway", size=12, color=INK, bold=True))
    f.append(text(970, 202, "увесь SQL таблиці:", size=10.5, color=MUTED))
    f.append(text(970, 226, "SELECT · INSERT", size=10.5, color=INK))
    f.append(text(970, 246, "UPDATE · DELETE", size=10.5, color=INK))
    f.append(text(970, 272, "→ orders", size=10.5, color=MUTED, italic=True))

    f.append(arrow(847, 133, 878, 192, color=FIELD, sw=1.6))
    f.append(arrow(847, 203, 878, 218, color=FIELD, sw=1.6))
    f.append(arrow(847, 273, 878, 252, color=FIELD, sw=1.6))

    # мала таблиця праворуч від шлюзу
    f.append(rect(1085, 175, 105, 26, fill=FILL, stroke=LINE, sw=1.2, rx=0))
    f.append(rect(1085, 201, 105, 90, fill=BG, stroke=LINE, sw=1.2, rx=0))
    f.append(text(1137, 192, "orders", size=9.5, color=MUTED, bold=True))
    for i, r in enumerate(["41 · new", "42 · paid", "43 · shipped"]):
        f.append(text(1137, 220 + i * 30, r, size=9, color=INK))
        if i:
            f.append(line(1085, 201 + i * 30, 1190, 201 + i * 30, color=MUTED, sw=1))
    f.append(arrow(1062, 226, 1083, 226, color=MUTED, sw=1.6))

    f.append(text(915, 468, "увесь SQL — в одній точці", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'tdg-scatter-vs-gather.svg'), W, H, *f)


# ── 2. Анатомія: одні ворота між кодом і цілою таблицею; віддає record set ────
def fig_anatomy():
    W, H = 1180, 560
    f = []
    f.append(text(W / 2, 30,
                  "Анатомія шлюзу таблиці: одні ворота між кодом і цілою таблицею",
                  size=17, bold=True))

    # ── ЛІВОРУЧ: код-споживач ──
    f.append(rect(40, 205, 210, 70, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(145, 235, "код-споживач", size=13, color=INK, bold=True))
    f.append(text(145, 258, 'gw.findByStatus("paid")', size=11, color=NEG))
    f.append(arrow(252, 240, 328, 240, color=MUTED, sw=1.8))
    f.append(text(290, 230, "кличе метод", size=10, color=MUTED))

    # ── ЦЕНТР: шлюз ──
    GX, GY, GW_, GH = 330, 96, 430, 340
    f.append(rect(GX, GY, GW_, GH, fill=BG, stroke=FIELD, sw=2.2, rx=10))
    f.append(rect(GX, GY, GW_, 34, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(GX + GW_ / 2, GY + 22, "OrderTableGateway — один об'єкт на таблицю",
                  size=13, color=INK, bold=True))

    f.append(text(GX + 18, GY + 60, "тут увесь SQL таблиці orders", size=11,
                  color=MUTED, anchor="start"))
    f.append(rect(GX + 18, GY + 68, 394, 74, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(GX + 32, GY + 90, "SELECT … FROM orders WHERE …", size=11, color=INK, anchor="start"))
    f.append(text(GX + 32, GY + 112, "INSERT INTO orders (…) VALUES (…)", size=11, color=INK, anchor="start"))
    f.append(text(GX + 32, GY + 134, "UPDATE orders SET …    DELETE FROM orders", size=10.5, color=INK, anchor="start"))

    f.append(text(GX + 18, GY + 166, "методи — усі беруть ключ / критерій", size=11,
                  color=MUTED, anchor="start"))
    f.append(rect(GX + 18, GY + 174, 394, 60, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(GX + 32, GY + 196, "find(id)      findByStatus(status)", size=11.5, color=INK, anchor="start"))
    f.append(text(GX + 32, GY + 220, "insert(…)   update(id, …)   delete(id)", size=11.5, color=INK, anchor="start"))

    f.append(rect(GX + 18, GY + 248, 394, 40, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(GX + 32, GY + 273, "✗", size=15, color=POS, anchor="start", bold=True))
    f.append(text(GX + 54, GY + 273, "предметних правил немає", size=12, color=MUTED, anchor="start"))
    f.append(text(GX + GW_ - 18, GY + 273, "лише переносить рядки", size=10.5, color=POS,
                  anchor="end", bold=True))

    # ── ПРАВОРУЧ: таблиця orders ──
    TX, TY, TW = 830, 150, 310
    f.append(rect(TX, TY, TW, 30, fill=FILL, stroke=LINE, sw=1.4, rx=0))
    f.append(rect(TX, TY + 30, TW, 120, fill=BG, stroke=LINE, sw=1.4, rx=0))
    xs = [TX, TX + 80, TX + 200, TX + TW]
    centers = [(xs[i] + xs[i + 1]) / 2 for i in range(3)]
    for x in xs[1:-1]:
        f.append(line(x, TY, x, TY + 150, color=MUTED, sw=1))
    for c, nm in zip(centers, ["id", "total", "status"]):
        f.append(text(c, TY + 20, nm, size=10.5, color=MUTED, bold=True))
    trows = [(41, 350, "new"), (42, 1200, "paid"), (43, 90, "shipped")]
    for i, r in enumerate(trows):
        yy = TY + 30 + i * 40 + 25
        for c, v in zip(centers, r):
            f.append(text(c, yy, str(v), size=11, color=INK))
        if i:
            f.append(line(TX, TY + 30 + i * 40, TX + TW, TY + 30 + i * 40, color=MUTED, sw=1))
    f.append(arrow(762, 210, 828, 210, color=FIELD, sw=1.9))
    f.append(text(795, 197, "усі рядки", size=10, color=MUTED))
    f.append(text(TX + TW / 2, TY + 178, "один екземпляр обслуговує ВСІ рядки",
                  size=11.5, color=NEG, bold=True))

    # ── НИЗ: повертає сирий набір рядків (record set) ──
    f.append(arrow(GX + GW_ / 2, GY + GH + 4, GX + GW_ / 2, 462, color=MUTED, sw=1.8))
    RS_X, RS_Y, RS_W = 430, 462, 230
    f.append(rect(RS_X, RS_Y, RS_W, 62, fill="#eef1f4", stroke=MUTED, sw=1.3, rx=4))
    f.append(text(RS_X + RS_W / 2, RS_Y + 18, "id · total · status", size=9.5, color=MUTED, bold=True))
    f.append(line(RS_X, RS_Y + 24, RS_X + RS_W, RS_Y + 24, color=MUTED, sw=1))
    f.append(text(RS_X + RS_W / 2, RS_Y + 40, "42 · 1200 · paid", size=10, color=INK))
    f.append(text(RS_X + RS_W / 2, RS_Y + 56, "43 · 90 · shipped", size=10, color=INK))
    f.append(text(GX + GW_ / 2 + 200, 452, "повертає сирий набір рядків (record set)",
                  size=11.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(OUT, 'tdg-anatomy.svg'), W, H, *f)


# ── 3. Склеєний рядок проти параметра: де значення стає кодом ─────────────────
def fig_param_vs_glue():
    W, H = 1240, 640
    f = []
    f.append(text(W / 2, 32, "Значення як код проти значення як даних", size=17, bold=True))
    f.append(line(40, 340, 1200, 340, color=MUTED, sw=1.1, dash="7 7"))

    BAD = "paid' OR 1=1 --"

    # ══ ВЕРХНЯ СМУГА: склеєно в текст запиту ══
    f.append(text(60, 66, "Склеєно в текст запиту", size=14, color=POS,
                  bold=True, anchor="start"))

    f.append(rect(50, 88, 236, 74, fill=FILL, stroke=POS, sw=1.6, rx=8))
    f.append(text(168, 114, "що ввів користувач", size=11, color=MUTED))
    f.append(text(168, 140, BAD, size=12, color=POS, bold=True))

    f.append(arrow(290, 125, 348, 125, color=POS, sw=1.7))
    f.append(text(319, 112, "+", size=13, color=POS, bold=True))

    f.append(rect(352, 88, 480, 74, fill=BG, stroke=POS, sw=1.6, rx=8))
    f.append(text(592, 112, "один рядок, що поїхав у базу", size=11, color=MUTED))
    f.append(text(592, 140, "… WHERE status = 'paid' OR 1=1 --'", size=12, color=INK))

    f.append(arrow(836, 125, 894, 125, color=POS, sw=1.7))

    f.append(rect(898, 88, 292, 74, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(1044, 112, "парсер бачить ОДИН текст", size=11, color=MUTED))
    f.append(text(1044, 140, "і розбирає його цілком", size=12, color=INK))

    # розбір: що чим стало
    f.append(rect(352, 186, 480, 118, fill=FILL, stroke=MUTED, sw=1.3, rx=8))
    f.append(text(372, 210, "як це прочитав парсер:", size=11, color=MUTED, anchor="start"))
    f.append(text(372, 238, "status = 'paid'", size=12, color=NEG, anchor="start"))
    f.append(text(600, 238, "← дані, як і задумано", size=11, color=MUTED, anchor="start"))
    f.append(text(372, 264, "OR 1 = 1", size=12, color=POS, anchor="start", bold=True))
    f.append(text(600, 264, "← стало КОДОМ умови", size=11, color=POS, anchor="start", bold=True))
    f.append(text(372, 290, "--", size=12, color=POS, anchor="start", bold=True))
    f.append(text(600, 290, "← решту запиту вимкнено", size=11, color=POS, anchor="start"))

    f.append(rect(898, 186, 292, 62, fill=BG, stroke=POS, sw=1.6, rx=8))
    f.append(text(1044, 212, "повернулися ВСІ рядки", size=12.5, color=POS, bold=True))
    f.append(text(1044, 234, "таблиці orders", size=11, color=MUTED))

    # ══ НИЖНЯ СМУГА: окремим параметром ══
    f.append(text(60, 380, "Передано окремим параметром", size=14, color=FIELD,
                  bold=True, anchor="start"))

    f.append(rect(50, 402, 236, 74, fill=FILL, stroke=FIELD, sw=1.6, rx=8))
    f.append(text(168, 428, "той самий ввід", size=11, color=MUTED))
    f.append(text(168, 454, BAD, size=12, color=POS, bold=True))

    f.append(rect(352, 402, 480, 74, fill=BG, stroke=FIELD, sw=1.6, rx=8))
    f.append(text(592, 426, "текст запиту — сталий, від вводу не залежить", size=11, color=MUTED))
    f.append(text(592, 454, "… WHERE status = $1", size=12, color=INK))

    f.append(arrow(836, 439, 894, 439, color=FIELD, sw=1.7))
    f.append(text(865, 426, "1", size=11, color=MUTED))

    f.append(rect(898, 402, 292, 74, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(1044, 428, "парсер бачить лише текст", size=11, color=MUTED))
    f.append(text(1044, 452, "план із порожнім слотом", size=12, color=INK))

    # другий канал: значення повз парсер
    f.append(line(168, 480, 168, 542, color=FIELD, sw=1.7))
    f.append(line(168, 542, 1044, 542, color=FIELD, sw=1.7))
    f.append(arrow(1044, 542, 1044, 484, color=FIELD, sw=1.7))
    f.append(text(606, 530, "значення їде окремим каналом — його не парсять НІКОЛИ",
                  size=12, color=FIELD, bold=True))
    f.append(text(1044, 566, "2", size=11, color=MUTED))

    f.append(rect(898, 578, 292, 46, fill=BG, stroke=NEG, sw=1.5, rx=8))
    f.append(text(1044, 606, "0 рядків: такого статусу немає", size=11.5, color=NEG, bold=True))

    render(os.path.join(OUT, 'tdg-param-vs-glue.svg'), W, H, *f)


# ── 4. Межа транзакції: хто вирішує, що три виклики — одна дія ────────────────
def fig_transaction_boundary():
    W, H = 1220, 620
    f = []
    f.append(text(W / 2, 32, "Межа транзакції стоїть над шлюзом", size=17, bold=True))
    f.append(line(40, 322, 1180, 322, color=MUTED, sw=1.1, dash="7 7"))

    calls = ["gw.update(42, 'review')", "gw.insertAudit(42)", "gw.decLimit('c-7')"]

    # ══ ВЕРХНЯ СМУГА: шлюз бере з'єднання сам → кожен виклик комітить сам ══
    f.append(text(60, 66, "Шлюз бере з'єднання сам: кожен виклик — окрема транзакція",
                  size=14, color=POS, bold=True, anchor="start"))
    xs = [60, 330, 600]
    for x, c in zip(xs, calls):
        f.append(rect(x, 92, 230, 52, fill=FILL, stroke=LINE, sw=1.4, rx=8))
        f.append(text(x + 115, 123, c, size=11.5, color=INK))
        f.append(line(x + 115, 146, x + 115, 176, color=MUTED, sw=1.3))
    for x, tag, col in zip(xs, ["COMMIT", "COMMIT", "не сталося"], [FIELD, FIELD, POS]):
        f.append(rect(x + 45, 178, 140, 34, fill=BG, stroke=col, sw=1.5, rx=6))
        f.append(text(x + 115, 200, tag, size=11.5, color=col, bold=True))

    f.append(text(560, 248, "збій між другим і третім", size=12, color=POS, bold=True))
    f.append(line(715, 160, 715, 196, color=POS, sw=2.4))
    f.append(line(700, 178, 730, 178, color=POS, sw=2.4))

    f.append(rect(880, 92, 300, 120, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(1030, 122, "у базі — половина роботи", size=12.5, color=POS, bold=True))
    f.append(text(1030, 150, "статус змінено, аудит записано,", size=11, color=INK))
    f.append(text(1030, 172, "ліміт — ні. Полагодити вручну", size=11, color=INK))
    f.append(text(1030, 194, "може бути вже нікому.", size=11, color=INK))

    # ══ НИЖНЯ СМУГА: виклик тримає межу ══
    f.append(text(60, 362, "Шлюз отримує виконавця: межу тримає той, хто кличе",
                  size=14, color=FIELD, bold=True, anchor="start"))

    f.append(rect(50, 384, 800, 172, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    f.append(text(450, 410, "BEGIN … COMMIT — одна ділова дія", size=13, color=INK, bold=True))
    xs2 = [72, 340, 608]
    for x, c in zip(xs2, calls):
        f.append(rect(x, 426, 222, 52, fill=BG, stroke=LINE, sw=1.4, rx=8))
        f.append(text(x + 111, 457, c, size=11, color=INK))
    f.append(text(450, 508, "усі три — по одному й тому ж з'єднанню (tx)",
                  size=11.5, color=MUTED))
    f.append(text(450, 534, "жоден із них не комітить сам", size=11.5, color=FIELD, bold=True))

    f.append(line(760, 400, 760, 424, color=POS, sw=2.4))
    f.append(line(748, 412, 772, 412, color=POS, sw=2.4))
    f.append(text(700, 396, "збій", size=11, color=POS, bold=True))

    f.append(arrow(854, 470, 904, 470, color=NEG, sw=1.8))
    f.append(rect(908, 400, 272, 140, fill=BG, stroke=NEG, sw=1.6, rx=8))
    f.append(text(1044, 428, "ROLLBACK", size=13, color=NEG, bold=True))
    f.append(text(1044, 458, "у базі не змінилося", size=11.5, color=INK))
    f.append(text(1044, 480, "нічого — стан такий,", size=11.5, color=INK))
    f.append(text(1044, 502, "яким був до BEGIN", size=11.5, color=INK))
    f.append(text(1044, 528, "лагодити нічого", size=11, color=NEG, italic=True))

    render(os.path.join(OUT, 'tdg-transaction-boundary.svg'), W, H, *f)


if __name__ == '__main__':
    fig_scatter_vs_gather()
    fig_anatomy()
    fig_param_vs_glue()
    fig_transaction_boundary()
    print("figures written to", OUT)
