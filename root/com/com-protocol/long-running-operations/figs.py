# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: асинхронний обмін — прийняти швидко, віддати іншою дорогою ──────
def fig_async_flow():
    W, H = 960, 660
    xC, xA, xW = 165, 500, 815
    top, bot = 108, 620
    frags = []
    frags.append(text(W / 2, 34, "Довга операція: прийняти швидко, віддати іншою дорогою",
                      size=16, bold=True))
    frags.append(text(W / 2, 56, "запит повертається за мілісекунди, результат чекає за власним URL",
                      size=12, color=MUTED, italic=True))

    lifelines = {
        xC: [(top, bot)],
        xA: [(top, bot)],
        xW: [(top, 262), (430, bot)],
    }
    for x, spans in lifelines.items():
        for y1, y2 in spans:
            frags.append(line(x, y1, x, y2, color=MUTED, sw=1.2, dash="4 5"))

    for x, lbl in ((xC, "Клієнт"), (xA, "API"), (xW, "Черга + виконавець")):
        b, w, h = textbox(x, 86, lbl, size=13, bold=True, fill=FILL, stroke=INK, sw=1.7)
        frags.append(b)

    def msg(x1, x2, y, label, color=LINE, dash=None, lblcolor=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.9" marker-end="url(#arrow)"%s/>' % (x1, y, x2, y, color, d))
        frags.append(text((x1 + x2) / 2, y - 8, label, size=11, color=lblcolor or color))

    bw = 172
    frags.append(rect(xW - bw / 2, 262, bw, 168, fill="#fff4e6", stroke=POS, sw=1.9))
    frags.append(mtext(xW, 340, ["виконує звіт", "(хвилини)"], size=12, bold=True, color=POS))

    msg(xC, xA, 150, "POST /reports", color=INK)
    msg(xA, xC, 200, "202 · Location: /operations/op_7f3", color=FIELD, lblcolor=FIELD)
    msg(xA, xW, 248, "у чергу", color=INK)
    msg(xC, xA, 306, "GET /operations/op_7f3 · опитування", color=INK)
    msg(xA, xC, 352, "running · progress 0.35", color=MUTED, lblcolor=MUTED)
    msg(xW - bw / 2, xA, 408, "готово → операція succeeded", color=MUTED, dash="5 4", lblcolor=MUTED)
    msg(xC, xA, 462, "GET /operations/op_7f3", color=INK)
    msg(xA, xC, 508, "succeeded · result → /reports/rep_7f3", color=FIELD, lblcolor=FIELD)
    msg(xC, xA, 562, "GET /reports/rep_7f3", color=INK)
    msg(xA, xC, 606, "200 · готовий звіт", color=INK)

    render(os.path.join(IMG, "async-flow.svg"), W, H, *frags)


# ── Фігура 2: життєвий цикл операції ─────────────────────────────────────────
def fig_operation_states():
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 34, "Життєвий цикл операції", size=16, bold=True))
    frags.append(text(W / 2, 56, "status рухається цими станами; три праві — термінальні, далі не міняються",
                      size=12, color=MUTED, italic=True))

    ymid = 250
    pend, pw, ph = textbox(150, ymid, ["pending", "очікує черги"],
                           size=13, fill=BG, stroke=MUTED, sw=2.0, bold=True, color=MUTED)
    run, rw, rh = textbox(440, ymid, ["running", "виконується"],
                          size=13, fill="#eaf0fd", stroke=NEG, sw=2.3, bold=True, color=NEG)
    suc, sw2, sh = textbox(765, 150, ["succeeded", "результат готовий"],
                           size=13, fill="#eafaf1", stroke=FIELD, sw=2.3, bold=True, color=FIELD)
    fail, fw, fh = textbox(765, ymid, ["failed", "помилка + причина"],
                           size=13, fill="#fdecea", stroke=POS, sw=2.3, bold=True, color=POS)
    canc, cw, ch = textbox(765, 350, ["cancelled", "скасовано (DELETE)"],
                           size=13, fill=FILL, stroke=MUTED, sw=2.1, bold=True, color=MUTED)
    frags += [pend, run, suc, fail, canc]

    frags.append(arrow(150 + pw / 2 + 6, ymid, 440 - rw / 2 - 6, ymid, color=INK, sw=2.0))
    frags.append(text((150 + pw / 2 + 440 - rw / 2) / 2, ymid - 12, "виконавець узяв", size=11, color=MUTED))

    frags.append(arrow(440 + rw / 2 + 6, ymid - rh / 2 + 4, 765 - sw2 / 2 - 6, 150 + sh / 2 - 2, color=FIELD, sw=2.0))
    frags.append(text(618, 182, "готово", size=11, color=FIELD))

    frags.append(arrow(440 + rw / 2 + 6, ymid, 765 - fw / 2 - 6, ymid, color=POS, sw=2.0))
    frags.append(text((440 + rw / 2 + 765 - fw / 2) / 2, ymid - 12, "помилка", size=11, color=POS))

    frags.append(arrow(440 + rw / 2 + 6, ymid + rh / 2 - 4, 765 - cw / 2 - 6, 350 - ch / 2 + 2, color=MUTED, sw=2.0))
    frags.append(text(618, 322, "DELETE", size=11, color=MUTED))

    render(os.path.join(IMG, "operation-states.svg"), W, H, *frags)


# ── Фігура 3 (вставка proj): хто що пише в рядку операції ────────────────────
def fig_row_ownership():
    W, H = 1020, 560
    frags = []
    frags.append(text(W / 2, 32, "Рядок операції: у кожного стовпця один власник", size=16, bold=True))
    frags.append(text(W / 2, 54, "чотири писачі, кожен пише своє; статус-ендпойнт лише читає",
                      size=12, color=MUTED, italic=True))

    LX, LW = 30, 290
    CX, CW = 380, 330
    RX, RW = 770, 225
    y0, pitch, rh = 96, 84, 64

    rows = [
        (["Приймач POST /reports", "одна вставка, мілісекунди"],
         ["id · owner_id · input", "created_at · expires_at"], FILL, LINE),
        (["Захоплення виконавцем", "UPDATE … SKIP LOCKED"],
         ["state → running · attempt + 1", "lease_token · lease_until"], "#eaf0fd", NEG),
        (["Серцебиття виконавця", "раз на 10 с, поки живий"],
         ["progress · lease_until", "(поновлення оренди)"], "#eaf0fd", NEG),
        (["Завершення виконавця", "під охороною токена оренди"],
         ["state → succeeded / failed", "result_url · error"], "#eafaf1", FIELD),
        (["Прибиральник", "раз на хвилину"],
         ["state → failed (вигоріло)", "DELETE рядка за TTL"], FILL, MUTED),
    ]

    for i, (left, center, fill, stroke) in enumerate(rows):
        yt = y0 + i * pitch
        yc = yt + rh / 2
        frags.append(fitbox(LX, yt, LW, rh, left, size=12, fill=BG, stroke=MUTED, sw=1.6, color=INK))
        frags.append(fitbox(CX, yt, CW, rh, center, size=12, fill=fill, stroke=stroke, sw=1.9, color=INK))
        frags.append(arrow(LX + LW + 6, yc, CX - 8, yc, color=MUTED, sw=1.8))
        frags.append(line(CX + CW + 6, yc, 740, yc, color=MUTED, sw=1.2))

    ymid = (y0 + rh / 2 + y0 + (len(rows) - 1) * pitch + rh / 2) / 2
    frags.append(line(740, y0 + rh / 2, 740, y0 + (len(rows) - 1) * pitch + rh / 2, color=MUTED, sw=1.4))
    frags.append(fitbox(RX, ymid - 48, RW, 96,
                        ["GET /operations/op_7f3", "лише читає рядок", "і не пише нічого"],
                        size=12, fill=BG, stroke=INK, sw=1.9, color=INK, bold=True))
    frags.append(arrow(742, ymid, RX - 8, ymid, color=INK, sw=1.9))

    frags.append(text(W / 2, 530, "черга не зберігає стану — вона лише будить виконавця, "
                                  "а правда завжди в цьому рядку",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "row-ownership.svg"), W, H, *frags)


# ── Фігура 4 (вставка proj): токен оренди відсікає зомбі-виконавця ───────────
def fig_lease_fencing():
    W, H = 1040, 660
    xA, xR, xB = 180, 540, 880
    top, bot = 106, 630
    frags = []
    frags.append(text(W / 2, 32, "Токен оренди відсікає зомбі-виконавця", size=16, bold=True))
    frags.append(text(W / 2, 54, "A завмер і втратив оренду; його запис відкидає WHERE, а не сумління",
                      size=12, color=MUTED, italic=True))

    for x, lbl in ((xA, "Виконавець A"), (xR, "рядок operations"), (xB, "Виконавець B")):
        b, w, h = textbox(x, 82, lbl, size=13, bold=True, fill=FILL, stroke=INK, sw=1.7)
        frags.append(b)

    lifelines = {
        xA: [(top, 205), (365, bot)],
        xR: [(top, 158), (198, 370), (410, 463), (493, bot)],
        xB: [(top, 495), (565, bot)],
    }
    for x, spans in lifelines.items():
        for y1, y2 in spans:
            frags.append(line(x, y1, x, y2, color=MUTED, sw=1.2, dash="4 5"))

    def msg(x1, x2, y, label, color=LINE):
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.9" marker-end="url(#arrow)"/>' % (x1, y, x2, y, color))
        frags.append(text((x1 + x2) / 2, y - 9, label, size=11, color=color))

    msg(xA, xR, 140, "захоплює рядок · attempt = 1", INK)
    frags.append(fitbox(xR - 82, 163, 164, 30, "lease_token = A₁", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))
    frags.append(fitbox(xA - 80, 210, 160, 60, ["A рахує звіт", "серцебиття йде"],
                        size=12, fill=BG, stroke=NEG, sw=1.8, color=INK))
    frags.append(fitbox(xA - 90, 290, 180, 70, ["процес завмер:", "пауза 40 с,", "серцебиття нема"],
                        size=12, fill="#f2f2f2", stroke=MUTED, sw=1.8, color=MUTED))

    frags.append(fitbox(xR - 112, 375, 224, 30, "оренда згасла: lease_until < now()",
                        size=12, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True))

    msg(xB, xR, 430, "перезахоплює рядок · attempt = 2", INK)
    frags.append(fitbox(xR - 82, 468, 164, 30, "lease_token = B₂", size=12,
                        fill="#eafaf1", stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    frags.append(fitbox(xB - 80, 500, 160, 60, ["B рахує звіт", "з початку"],
                        size=12, fill=BG, stroke=FIELD, sw=1.8, color=INK))

    msg(xA, xR, 520, "UPDATE … WHERE lease_token = A₁", POS)
    frags.append(text((xA + xR) / 2, 545, "0 рядків — результат A відкинуто", size=11, color=POS))

    msg(xB, xR, 600, "UPDATE … WHERE lease_token = B₂ → succeeded", FIELD)

    render(os.path.join(IMG, "lease-fencing.svg"), W, H, *frags)


# ── Фігура 5: детальна діаграма послідовності асинхронного опитування ─────────
def fig_long_op_polling_sequence():
    W, H = 1000, 720
    xC, xG, xW = 160, 500, 840
    top, bot = 110, 680
    frags = []
    frags.append(text(W / 2, 34, "Послідовність асинхронного запиту, опитування та забирання результату",
                      size=16, bold=True))
    frags.append(text(W / 2, 56, "HTTP 202 Accepted · Retry-After з експоненційним затриманням · ідемпотентність",
                      size=12, color=MUTED, italic=True))

    lifelines = {
        xC: [(top, bot)],
        xG: [(top, bot)],
        xW: [(top, 240), (490, bot)],
    }
    for x, spans in lifelines.items():
        for y1, y2 in spans:
            frags.append(line(x, y1, x, y2, color=MUTED, sw=1.2, dash="4 5"))

    for x, lbl in ((xC, "Клієнт (Caller)"), (xG, "HTTP API Шлюз"), (xW, "Черга + Воркер")):
        b, w, h = textbox(x, 86, lbl, size=13, bold=True, fill=FILL, stroke=INK, sw=1.7)
        frags.append(b)

    def msg(x1, x2, y, label, color=LINE, dash=None, lblcolor=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.9" marker-end="url(#arrow)"%s/>' % (x1, y, x2, y, color, d))
        frags.append(text((x1 + x2) / 2, y - 8, label, size=11, color=lblcolor or color))

    # Воркер виконує роботу
    bw = 190
    frags.append(rect(xW - bw / 2, 240, bw, 250, fill="#fff4e6", stroke=POS, sw=1.9))
    frags.append(mtext(xW, 350, ["Фоновий виконавець:", "важкий розрахунок,", "серцебиття в базу"],
                       size=12, bold=True, color=POS))

    # Кроки протоколу
    msg(xC, xG, 145, "POST /reports · Idempotency-Key: k_9a1", color=INK)
    msg(xG, xC, 195, "202 Accepted · Location: /operations/op_7f3 · Retry-After: 2", color=FIELD, lblcolor=FIELD)
    msg(xG, xW, 235, "enqueue(task_id, payload)", color=INK)

    # Перше опитування
    msg(xC, xG, 290, "GET /operations/op_7f3  [пауза 2 с + джитер]", color=INK)
    msg(xG, xC, 335, "200 OK · {\"status\":\"running\",\"progress\":0.35}", color=MUTED, lblcolor=MUTED)

    # Друге опитування
    msg(xC, xG, 395, "GET /operations/op_7f3  [експоненційне зростання паузи: 4 с]", color=INK)
    msg(xG, xC, 440, "200 OK · {\"status\":\"running\",\"progress\":0.85}", color=MUTED, lblcolor=MUTED)

    # Воркер записує завершення
    msg(xW - bw / 2, xG, 485, "task complete → state=succeeded, result_url", color=FIELD, dash="5 4", lblcolor=FIELD)

    # Третє опитування — готово
    msg(xC, xG, 535, "GET /operations/op_7f3", color=INK)
    msg(xG, xC, 580, "200 OK · {\"status\":\"succeeded\",\"result_url\":\"/reports/rep_7f3\"}", color=FIELD, lblcolor=FIELD)

    # Забирання результату
    msg(xC, xG, 630, "GET /reports/rep_7f3", color=INK)
    msg(xG, xC, 670, "200 OK · Content-Type: application/pdf (2.4 MB)", color=INK)

    render(os.path.join(IMG, "long-op-polling-sequence.svg"), W, H, *frags)


# ── Фігура 6: автомат станів довгої операції з ідемпотентністю ────────────────
def fig_idempotent_state_machine():
    W, H = 1040, 600
    frags = []
    frags.append(text(W / 2, 34, "Автомат станів довгої операції та життєвий цикл токена ідемпотентності",
                      size=16, bold=True))
    frags.append(text(W / 2, 56, "переходи станів, захист від повторних запитів, оренда воркера та сплив TTL",
                      size=12, color=MUTED, italic=True))

    xP, yP = 170, 200
    xR, yR = 500, 200
    xS, yS = 850, 120
    xF, yF = 850, 230
    xC, yC = 850, 340
    xE, yE = 500, 480

    pend, pw, ph = textbox(xP, yP, ["PENDING", "Черга / ключ зарезервовано"],
                           size=12, fill=BG, stroke=MUTED, sw=2.0, bold=True, color=MUTED)
    run, rw, rh = textbox(xR, yR, ["RUNNING", "Виконується (активна оренда)"],
                          size=12, fill="#eaf0fd", stroke=NEG, sw=2.3, bold=True, color=NEG)
    suc, sw2, sh = textbox(xS, yS, ["SUCCEEDED", "Успіх (готовий результат)"],
                           size=12, fill="#eafaf1", stroke=FIELD, sw=2.3, bold=True, color=FIELD)
    fail, fw, fh = textbox(xF, yF, ["FAILED", "Помилка (RFC 9457 envelope)"],
                           size=12, fill="#fdecea", stroke=POS, sw=2.3, bold=True, color=POS)
    canc, cw, ch = textbox(xC, yC, ["CANCELLED", "Скасовано клієнтом (DELETE)"],
                           size=12, fill=FILL, stroke=MUTED, sw=2.1, bold=True, color=MUTED)
    exp, ew, eh = textbox(xE, yE, ["EXPIRED / TOMBSTONE", "Вичищено за строком TTL (Sweeper)"],
                          size=12, fill="#f4f6f8", stroke=MUTED, sw=1.8, bold=True, color=MUTED)

    frags += [pend, run, suc, fail, canc, exp]

    # POST (start) -> PENDING
    frags.append(arrow(30, yP, xP - pw / 2 - 6, yP, color=INK, sw=2.0))
    frags.append(text((30 + xP - pw / 2) / 2, yP - 12, "POST + Key", size=11, color=INK))

    # PENDING -> RUNNING
    frags.append(arrow(xP + pw / 2 + 6, yP, xR - rw / 2 - 6, yP, color=INK, sw=2.0))
    frags.append(text((xP + pw / 2 + xR - rw / 2) / 2, yP - 12, "Воркер захопив оренду", size=11, color=INK))

    # RUNNING loop (серцебиття)
    frags.append('<path d="M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (xR - 30, yR - rh / 2 - 4, xR - 30, yR - rh / 2 - 45, xR + 30, yR - rh / 2 - 45, xR + 30, yR - rh / 2 - 4, NEG))
    frags.append(text(xR, yR - rh / 2 - 50, "Серцебиття / поновлення оренди", size=11, color=NEG))

    # RUNNING -> PENDING (оренда згасла)
    frags.append('<path d="M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 4" marker-end="url(#arrow)"/>'
                 % (xR - 40, yR + rh / 2 + 4, xR - 40, yR + rh / 2 + 40, xP + 40, yP + ph / 2 + 40, xP + 40, yP + ph / 2 + 4, POS))
    frags.append(text((xP + xR) / 2, yR + rh / 2 + 48, "Оренда згасла (lease timeout) → повтор", size=11, color=POS))

    # RUNNING -> SUCCEEDED
    frags.append(arrow(xR + rw / 2 + 6, yR - 15, xS - sw2 / 2 - 6, yS + 10, color=FIELD, sw=2.0))
    frags.append(text(660, 140, "Успіх під токеном", size=11, color=FIELD))

    # RUNNING -> FAILED
    frags.append(arrow(xR + rw / 2 + 6, yR + 10, xF - fw / 2 - 6, yF - 5, color=POS, sw=2.0))
    frags.append(text(660, 230, "Помилка / ліміт спроб", size=11, color=POS))

    # RUNNING -> CANCELLED
    frags.append(arrow(xR + rw / 2 + 6, yR + 25, xC - cw / 2 - 6, yC - 10, color=MUTED, sw=2.0))
    frags.append(text(660, 310, "DELETE / cancel token", size=11, color=MUTED))

    # Terminal -> EXPIRED
    frags.append(line(xS + sw2 / 2, yS, 980, yS, color=MUTED, sw=1.4))
    frags.append(line(xF + fw / 2, yF, 980, yF, color=MUTED, sw=1.4))
    frags.append(line(xC + cw / 2, yC, 980, yC, color=MUTED, sw=1.4))
    frags.append(line(980, yS, 980, yE, color=MUTED, sw=1.4))
    frags.append(arrow(980, yE, xE + ew / 2 + 6, yE, color=MUTED, sw=1.8))
    frags.append(text(840, yE - 10, "Сплив TTL результату", size=11, color=MUTED))

    render(os.path.join(IMG, "idempotent-state-machine.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_async_flow()
    fig_operation_states()
    fig_row_ownership()
    fig_lease_fencing()
    fig_long_op_polling_sequence()
    fig_idempotent_state_machine()
    print("figures written")
