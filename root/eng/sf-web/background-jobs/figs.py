# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox at center → (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: робота в обробнику (синхронно) проти роботи через чергу ──────────
def sync_vs_queue():
    W, H = 1080, 604
    parts = []
    parts.append(text(W / 2, 30, "Той самий запит: робота в обробнику проти роботи через чергу",
                      size=17, bold=True))
    parts.append(line(W / 2, 54, W / 2, H - 20, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "СИНХРОННО · робота в запиті", size=13, bold=True, color=POS))
    parts.append(text(W * 3 / 4, 56, "ЧЕРЕЗ ЧЕРГУ · робота поза запитом", size=13, bold=True, color=FIELD))

    # ── ЛІВОРУЧ: клієнт ⇄ обробник, що сам виконує повільну роботу ──
    lx = W / 4
    cli_l, lw1, lh1 = box_at(lx, 112, "клієнт", size=13, bold=True,
                             fill="#fdecea", stroke=POS, min_w=150)
    hnd_l, lw2, lh2 = box_at(lx, 262, "обробник\nкодує відео · 30 с", size=12, bold=True,
                             fill=FILL, stroke=POS, min_w=236)
    parts.append(arrow(lx - 46, 112 + lh1, lx - 46, 262 - lh2, color=POS, sw=1.8))
    parts.append(text(lx - 104, 190, "запит", size=11, color=POS, anchor="middle"))
    parts.append(arrow(lx + 46, 262 - lh2, lx + 46, 112 + lh1, color=MUTED, sw=1.6))
    parts.append(text(lx + 110, 182, "відповідь", size=11, color=MUTED, anchor="middle"))
    parts.append(text(lx + 110, 198, "через 30 с", size=11, color=MUTED, anchor="middle"))
    parts.append(cli_l)
    parts.append(hnd_l)
    for i, n in enumerate(("клієнт чекає всі 30 с",
                           "з'єднання зайняте · таймаут",
                           "перезапуск → роботу втрачено")):
        parts.append(text(lx, 372 + i * 27, "• " + n, size=12.5, italic=True, color=POS))

    # ── ПРАВОРУЧ: клієнт → обробник → черга → пул виконавців ──
    rx = W * 3 / 4
    cli_r, rw1, rh1 = box_at(rx, 104, "клієнт", size=13, bold=True,
                             fill="#eaf7ef", stroke=FIELD, min_w=150)
    hnd_r, rw2, rh2 = box_at(rx, 212, "обробник\nзаписує задачу", size=12, bold=True,
                             fill="#eaf7ef", stroke=FIELD, min_w=214)
    parts.append(arrow(rx - 46, 104 + rh1, rx - 46, 212 - rh2, color=FIELD, sw=1.8))
    parts.append(text(rx - 92, 158, "запит", size=11, color=FIELD, anchor="middle"))
    parts.append(arrow(rx + 46, 212 - rh2, rx + 46, 104 + rh1, color=FIELD, sw=1.8))
    parts.append(text(rx + 116, 150, "202 прийнято", size=11, bold=True, color=FIELD, anchor="middle"))
    parts.append(text(rx + 116, 166, "миттєво", size=11, italic=True, color=FIELD, anchor="middle"))
    parts.append(cli_r)
    parts.append(hnd_r)

    q, qw, qh = box_at(rx, 336, "черга · таблиця БД або брокер", size=12, bold=True,
                       fill=FILL, stroke=INK, min_w=300)
    parts.append(arrow(rx, 212 + rh2, rx, 336 - qh, color=FIELD, sw=1.8))
    parts.append(q)

    for wxx in (rx - 150, rx, rx + 150):
        wb, ww, wh = box_at(wxx, 466, "виконавець", size=11, bold=True,
                            fill=FILL, stroke=FIELD, min_w=132)
        parts.append(arrow(rx + (wxx - rx) * 0.28, 336 + qh, wxx, 466 - wh, color=FIELD, sw=1.5))
        parts.append(wb)
    parts.append(text(rx, 520, "пул виконавців вичерпує чергу осторонь", size=12.5, italic=True, color=FIELD))
    parts.append(text(rx, 544, "задача записана → переживе перезапуск; сплеск гасить черга",
                      size=11.5, italic=True, color=FIELD))

    render(os.path.join(IMG, "sync-vs-queue.svg"), W, H, *parts)


# ── Фігура 2: життєвий цикл однієї задачі ──────────────────────────────────────
def job_lifecycle():
    W, H = 1040, 512
    parts = []
    parts.append(text(W / 2, 30, "Життя однієї задачі: від постановки до підтвердження",
                      size=17, bold=True))

    yrow = 214
    x_q, x_claim, x_run, x_done = 156, 400, 632, 892
    q, qw, qh = box_at(x_q, yrow, "у черзі", size=13, bold=True, fill=FILL, stroke=INK, min_w=150)
    cl, clw, clh = box_at(x_claim, yrow, "взято\nвиконавцем", size=12, bold=True,
                          fill="#eaf0fd", stroke=NEG, min_w=156)
    rn, rnw, rnh = box_at(x_run, yrow, "виконується", size=13, bold=True, fill=FILL, stroke=INK, min_w=156)
    dn, dnw, dnh = box_at(x_done, yrow, "виконано ✓\n(підтверджено)", size=12, bold=True,
                          fill="#eaf7ef", stroke=FIELD, min_w=156)

    parts.append(arrow(x_q + qw, yrow, x_claim - clw, yrow, color=INK, sw=1.7))
    parts.append(text((x_q + qw + x_claim - clw) / 2, yrow - 13, "виконавець бере", size=10.5, color=MUTED))
    parts.append(arrow(x_claim + clw, yrow, x_run - rnw, yrow, color=INK, sw=1.7))
    parts.append(arrow(x_run + rnw, yrow, x_done - dnw, yrow, color=FIELD, sw=1.7))
    parts.append(text((x_run + rnw + x_done - dnw) / 2, yrow - 13, "успіх", size=10.5, bold=True, color=FIELD))
    for b in (q, cl, rn, dn):
        parts.append(b)

    # ── вузол невдачі під «виконується» + мертва черга праворуч ──
    y_fail = 344
    fl, flw, flh = box_at(x_run, y_fail, "невдача", size=13, bold=True,
                          fill="#faf3e0", stroke=POS, min_w=148)
    parts.append(arrow(x_run, yrow + rnh, x_run, y_fail - flh, color=POS, sw=1.7))
    parts.append(text(x_run + 74, (yrow + rnh + y_fail - flh) / 2 + 4, "помилка",
                      size=10.5, italic=True, color=POS, anchor="middle"))
    parts.append(fl)

    dl, dlw, dlh = box_at(x_done, y_fail, "мертва черга", size=12, bold=True,
                          fill="#fdecea", stroke=POS, min_w=168)
    parts.append(arrow(x_run + flw, y_fail, x_done - dlw, y_fail, color=POS, sw=1.7))
    parts.append(text((x_run + flw + x_done - dlw) / 2, y_fail - 13, "після N спроб",
                      size=10.5, bold=True, color=POS))
    parts.append(dl)

    # ── канал повтору ЗНИЗУ: невдача → вниз → ліворуч → вгору в чергу ──
    ych = 448
    parts.append(line(x_run, y_fail + flh, x_run, ych, color=POS, sw=1.6))
    parts.append(line(x_run, ych, x_q, ych, color=POS, sw=1.6))
    parts.append(arrow(x_q, ych, x_q, yrow + qh, color=POS, sw=1.6))
    parts.append(text((x_q + x_run) / 2, ych + 20,
                      "повтор із відступанням: чекати база·2^спроба, потім знову в чергу",
                      size=11, italic=True, color=POS))

    # ── канал «виконавець упав» ЗВЕРХУ: виконується → вгору → ліворуч → вниз у чергу ──
    ytop = 112
    parts.append(line(x_run, yrow - rnh, x_run, ytop, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(line(x_run, ytop, x_q, ytop, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(arrow(x_q, ytop, x_q, yrow - qh, color=MUTED, sw=1.4))
    parts.append(text((x_q + x_run) / 2, ytop - 10,
                      "виконавець упав → задача знову в чергу (щонайменше раз)",
                      size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "job-lifecycle.svg"), W, H, *parts)


# ── Фігура 3 (вставка hist): віконце прийому 1960-х як та сама черга ──────────
def hist_counter_loop():
    W, H = 1288, 332
    parts = []
    parts.append(text(W / 2, 32, "Черга задач 1960-х: ті самі ролі, тільки з картону й людей",
                      size=17, bold=True))

    yb = 154
    xs = (180, 420, 660, 900, 1140)
    labels = ("програміст\nздає колоду карток",
              "віконце прийому\nквитанція з номером",
              "лоток очікування\nза пріоритетом",
              "оператор\nставить колоду в машину",
              "полиця роздруківок\nпрограміст забирає")
    roles = ("клієнт ставить задачу",
             "«прийнято»\nі номер задачі",
             "довговічна черга",
             "виконавець",
             "опитування стану\nй результат")
    strokes = (NEG, FIELD, INK, FIELD, NEG)

    halves = []
    boxes = []
    for x, s, st in zip(xs, labels, strokes):
        b, hw, hh = box_at(x, yb, s, size=12, bold=True, fill=FILL, stroke=st, min_w=192)
        halves.append((hw, hh))
        boxes.append(b)

    for i in range(4):
        x1 = xs[i] + halves[i][0]
        x2 = xs[i + 1] - halves[i + 1][0]
        parts.append(arrow(x1, yb, x2, yb, color=INK, sw=1.7))
    parts.extend(boxes)

    for x, r in zip(xs, roles):
        parts.append(mtext(x, yb + halves[0][1] + 28, r, size=11.5, color=MUTED, lh=1.35))

    # зворотний канал знизу: програміст повертається по результат
    xr = xs[-1] + halves[-1][0] + 24
    xl = xs[0] - halves[0][0] - 42
    ych = 274
    parts.append(line(xs[-1] + halves[-1][0], yb, xr, yb, color=MUTED, sw=1.5, dash="6 5"))
    parts.append(line(xr, yb, xr, ych, color=MUTED, sw=1.5, dash="6 5"))
    parts.append(line(xr, ych, xl, ych, color=MUTED, sw=1.5, dash="6 5"))
    parts.append(line(xl, ych, xl, yb, color=MUTED, sw=1.5, dash="6 5"))
    parts.append(arrow(xl, yb, xs[0] - halves[0][0], yb, color=MUTED, sw=1.5))
    parts.append(text(W / 2, ych + 24,
                      "програміст іде працювати далі, а колода тим часом лежить у лотку — "
                      "перезапуск машини їй нічого не робить",
                      size=11.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "hist-counter-loop.svg"), W, H, *parts)


# ── Фігура 4 (вставка hist): чотири покоління й що кожне додало ───────────────
def hist_queue_generations():
    W, H = 1240, 664
    parts = []
    parts.append(text(W / 2, 32, "Чотири покоління однієї ідеї: що кожне додало до черги",
                      size=17, bold=True))

    c1, c2, c3 = 160, 530, 990
    parts.append(text(c1, 92, "Епоха", size=13, bold=True))
    parts.append(text(c2, 92, "Чим ставили задачу", size=13, bold=True))
    parts.append(text(c3, 92, "Що ця епоха додала", size=13, bold=True))
    parts.append(line(35, 106, W - 40, 106, color=MUTED, sw=1))

    rows = (
        ("Мейнфрейм\n1956 → 1970-ті",
         "колода карток і оператор\nGM-NAA I/O (1956) · JCL (1965)\nспулінг · HASP (1967)",
         "приймання окремо від виконання\nзадача як довговічний предмет\nпріоритет і черговість"),
        ("Unix\n1976 → 1987",
         "uucp-спул (1976)\ncron у V7 (1979) · at\nVixie cron (1987)",
         "повтор після невдачі\nвідкладення в часі\nвиконавець-демон без людини"),
        ("Корпоративні брокери\n1993 → 2008",
         "IBM MQSeries (1993) · MSMQ (1997)\nJMS (1998) як спільний API\nAMQP (2003→2006) · RabbitMQ (2007)",
         "підтвердження і повторна доставка\nмертва черга\nтранзакційна постановка"),
        ("Веб-черги задач\n2004 → 2012",
         "Amazon SQS (2004→2006) · Gearman (2005)\nbeanstalkd (2007) · delayed_job (2008)\nResque (2009) · Celery (2009) · Sidekiq (2012)",
         "черга в тій самій базі\nвидимість: панель, невдалі задачі\nбібліотека замість інфраструктури"),
    )

    y = 182
    for era, tools, gain in rows:
        b1, _, _ = box_at(c1, y, era, size=12, bold=True, fill=FILL, stroke=INK, min_w=250)
        b2, _, _ = box_at(c2, y, tools, size=11.5, fill="#ffffff", stroke=MUTED, min_w=430)
        b3, _, _ = box_at(c3, y, gain, size=11.5, fill="#eaf7ef", stroke=FIELD, min_w=420)
        parts.extend((b1, b2, b3))
        y += 130

    parts.append(text(W / 2, 640,
                      "спільне для всіх чотирьох: прийняти швидко → записати надійно → "
                      "відповісти → виконати осторонь",
                      size=12.5, italic=True, color=INK))

    render(os.path.join(IMG, "hist-queue-generations.svg"), W, H, *parts)


# ── Фігура: застовплення — SKIP LOCKED і межа видимості run_at ─────────────────
def claim_skip_locked():
    W, H = 1120, 600
    parts = []
    parts.append(text(W / 2, 32, "Застовплення: хто саме бачить рядок і хто його бере",
                      size=17, bold=True))

    TX, TW = 380, 430          # таблиця
    NX = TX + TW + 28          # колонка приміток
    rh = 46
    tops = [128, 184, 240, 322, 378, 434]
    centers = [t + rh / 2 for t in tops]

    rows = [
        ("#41 · лист · run_at 10:00:03", True),
        ("#42 · звіт · run_at 10:00:05", True),
        ("#43 · лист · run_at 10:00:07", True),
        ("#44 · відео · run_at 10:01:02", False),
        ("#45 · лист · run_at 10:04:15", False),
        ("#39 · платіж · status='dead'", False),
    ]
    parts.append(text(TX + TW / 2, 108, "таблиця jobs", size=13, bold=True, color=MUTED))
    for (label, visible), top in zip(rows, tops):
        parts.append(fitbox(TX, top, TW, rh, label, size=13, bold=visible,
                            fill="#eaf7ef" if visible else FILL,
                            stroke=FIELD if visible else MUTED,
                            color=INK if visible else MUTED))

    # межа видимості
    parts.append(line(TX - 24, 300, TX + TW + 16, 300, color=NEG, sw=1.6, dash="7 5"))
    parts.append(text(NX - 4, 304, "now()", size=12, bold=True, color=NEG, anchor="start"))

    # примітки праворуч
    parts.append(text(NX, 186, "видимі кандидати:", size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(text(NX, 206, "status = 'ready'", size=12, color=FIELD, anchor="start"))
    parts.append(text(NX, 226, "AND run_at ≤ now()", size=12, color=FIELD, anchor="start"))
    parts.append(text(NX, centers[3] + 4, "оренда виконавця D", size=12, color=MUTED, anchor="start"))
    parts.append(text(NX, centers[4] + 4, "відступання після 2-ї", size=12, color=MUTED, anchor="start"))
    parts.append(text(NX, centers[5] + 4, "мертва — не видно", size=12, color=MUTED, anchor="start"))

    # виконавці ліворуч
    for i, name in enumerate(("виконавець A", "виконавець B", "виконавець C")):
        wb, ww, wh = box_at(150, centers[i], name, size=12, bold=True,
                            fill="#eaf0fd", stroke=NEG, min_w=176)
        parts.append(arrow(150 + ww + 6, centers[i], TX - 8, centers[i], color=NEG, sw=1.7))
        parts.append(text((150 + ww + TX) / 2, centers[i] - 12,
                          "бере " + rows[i][0][:3], size=11, color=NEG))
        parts.append(wb)

    for i, ln in enumerate(("три виконавці —", "три РІЗНІ рядки:",
                            "SKIP LOCKED не дає їм", "стати в чергу за одним")):
        parts.append(text(178, 358 + i * 22, ln, size=12, italic=True, color=NEG))

    parts.append(text(W / 2, 524,
                      "FOR UPDATE SKIP LOCKED пропускає рядок, який саме зараз тримає інша транзакція,",
                      size=12.5, italic=True))
    parts.append(text(W / 2, 548,
                      "а стовпець run_at ховає ті, чий час іще не настав — оренду й відступання.",
                      size=12.5, italic=True))

    render(os.path.join(IMG, "claim-skip-locked.svg"), W, H, *parts)


# ── Фігура: оренда в часі — падіння виконавця й задача, довша за оренду ────────
def lease_timeline():
    W, H = 1120, 620
    parts = []
    parts.append(text(W / 2, 32, "Оренда: той самий run_at, тільки на 60 секунд уперед",
                      size=17, bold=True))

    X0, X1 = 180, 1020
    px = (X1 - X0) / 90.0                      # 90 секунд на всю вісь

    def at(sec):
        return X0 + sec * px

    def axis(y):
        out = [line(X0, y, X1, y, color=INK, sw=1.6)]
        for s in (0, 30, 60, 90):
            out.append(line(at(s), y - 5, at(s), y + 5, color=INK, sw=1.4))
            out.append(text(at(s), y + 32, "%d с" % s, size=11, color=MUTED))
        return out

    # ── доріжка 1: виконавець падає ──
    y1 = 200
    parts.append(text(90, 104, "СЦЕНАРІЙ 1 · виконавець падає посеред роботи",
                      size=13.5, bold=True, color=NEG, anchor="start"))
    parts.append(text(at(0), 134, "застовплення:", size=11, color=NEG))
    parts.append(text(at(0), 152, "run_at ← now()+60 с · attempts 0→1", size=11, color=NEG))
    parts.append(rect(at(0), y1 - 36, at(60) - at(0), 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    parts.append(text((at(0) + at(60)) / 2, y1 - 19, "оренда 60 с — рядок невидимий",
                      size=12, bold=True, color=NEG))
    parts.extend(axis(y1))
    parts.append(circle(at(12), y1, 7, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(at(12), y1 + 58, "виконавець упав", size=11.5, color=POS))
    parts.append(line(at(60), y1 - 44, at(60), y1 + 12, color=FIELD, sw=1.5, dash="5 4"))
    parts.append(text(at(62), y1 + 58, "оренда вичерпалась → рядок знову видимий",
                      size=11.5, color=FIELD, anchor="start"))
    parts.append(text(at(62), y1 + 78, "інший виконавець бере · attempts 1→2",
                      size=11.5, color=FIELD, anchor="start"))

    # ── доріжка 2: задача довша за оренду ──
    y2 = 424
    parts.append(text(90, 330, "СЦЕНАРІЙ 2 · задача триває довше за оренду",
                      size=13.5, bold=True, color=POS, anchor="start"))
    parts.append(text((at(0) + at(90)) / 2, 358,
                      "задача виконується — 150 с, і перший виконавець живий", size=12, color=POS))
    parts.append(arrow(at(0), 378, at(92), 378, color=POS, sw=2))
    parts.append(rect(at(0), y2 - 36, at(60) - at(0), 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    parts.append(text((at(0) + at(60)) / 2, y2 - 19, "оренда 60 с", size=12, bold=True, color=NEG))
    parts.extend(axis(y2))
    parts.append(line(at(60), y2 - 44, at(60), y2 + 12, color=POS, sw=1.5, dash="5 4"))
    parts.append(text(at(20), y2 + 58, "рядок знову видимий, хоч задача ще йде",
                      size=11.5, color=POS, anchor="start"))
    parts.append(text(at(20), y2 + 78, "другий бере ТУ САМУ задачу — подвійне виконання",
                      size=11.5, bold=True, color=POS, anchor="start"))

    cure, cw, ch = box_at(W / 2, 566,
                          "Ліки: оренда довша за найдовшу задачу · серцебиття (поки задача йде, кожні 20 с\n"
                          "зсувати run_at уперед) · дедлайн у коді коротший за оренду · закривати рядок\n"
                          "лише «якщо він досі мій»: AND locked_by = $me",
                          size=12, fill="#f7f7f5", stroke=MUTED, sw=1.3)
    parts.append(cure)

    render(os.path.join(IMG, "lease-timeline.svg"), W, H, *parts)


# ── Фігура 7: 4-ланкова архітектура черги фонових задач ───────────────────────
def queue_architecture():
    W, H = 1180, 640
    parts = []
    parts.append(text(W / 2, 32, "Чотириланкова архітектура черги фонових задач",
                      size=17, bold=True))

    # Producer
    px, py = 180, 260
    p_box, pw, ph = box_at(px, py,
                           "Producer (Постачальник)\n"
                           "Веб-сервер · API Gateway\n"
                           "Генерація task_id\n"
                           "Серіалізація аргументів (JSON)\n"
                           "Повертає клієнту 202 Accepted",
                           size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=240)
    parts.append(p_box)

    # Broker (Top Middle)
    bx, by = 580, 180
    b_box, bw, bh = box_at(bx, by,
                           "Message Broker (Брокер)\n"
                           "Redis Streams · RabbitMQ · AMQP\n"
                           "Буферизація завдань у пам'яті / на диску\n"
                           "Черги очікування (FIFO / Priority)\n"
                           "Облік непідтверджених задач (PEL / In-flight)",
                           size=11.5, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=280)
    parts.append(b_box)

    # DLQ (Bottom Middle)
    dx, dy = 580, 460
    d_box, dw, dh = box_at(dx, dy,
                           "Dead Letter Queue (DLQ)\n"
                           "Черга збійних і отруйних повідомлень\n"
                           "Збереження тіла, помилки й стек-трейсу\n"
                           "Ручний аудит · Re-drive / Replay утиліта",
                           size=11.5, bold=True, fill="#fdecea", stroke=POS, min_w=280)
    parts.append(d_box)

    # Worker Pool (Top Right)
    wx, wy = 980, 180
    w_box, ww, wh = box_at(wx, wy,
                           "Consumer (Worker Pool)\n"
                           "Master / Supervisor процес\n"
                           "Prefetch буфер · QoS обмеження\n"
                           "Пул воркерів (Fork / Threads / Async)\n"
                           "Виконання бізнес-логіки та ACK",
                           size=11.5, bold=True, fill="#faf3e0", stroke=INK, min_w=260)
    parts.append(w_box)

    # Result Backend (Bottom Right)
    rx, ry = 980, 460
    r_box, rw, rh = box_at(rx, ry,
                           "Result Backend (Сховище)\n"
                           "Redis · PostgreSQL · S3 Key-Value\n"
                           "Статус (PENDING / SUCCESS / FAILURE)\n"
                           "Результат виклику або виняток\n"
                           "TTL автоматичної утилізації ключів",
                           size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=260)
    parts.append(r_box)

    # Стрілки
    # Producer -> Broker
    parts.append(arrow(px + pw, py - 30, bx - bw, by + 20, color=NEG, sw=1.7))
    parts.append(mtext((px + pw + bx - bw) / 2 - 10, py - 52,
                       ["постановка задачі", "(XADD / basic.publish)"],
                       size=10.5, color=NEG, lh=1.3))

    # Broker <-> Worker
    parts.append(arrow(bx + bw, by - 16, wx - ww, wy - 16, color=FIELD, sw=1.7))
    parts.append(text((bx + bw + wx - ww) / 2, by - 28, "fetch / dispatch (Prefetch)",
                      size=10.5, color=FIELD))

    parts.append(arrow(wx - ww, wy + 16, bx + bw, by + 16, color=INK, sw=1.7))
    parts.append(text((bx + bw + wx - ww) / 2, by + 34, "ACK (підтвердження) / NACK",
                      size=10.5, color=INK))

    # Worker -> Result Backend
    parts.append(arrow(wx, wy + wh, rx, ry - rh, color=MUTED, sw=1.7))
    parts.append(mtext(wx + 90, (wy + wh + ry - rh) / 2 - 8,
                       ["запис результату", "(SET task:<id>)"],
                       size=10.5, color=MUTED, lh=1.3))

    # Worker -> DLQ
    parts.append(arrow(wx - ww + 20, wy + wh, dx + dw, dy - 20, color=POS, sw=1.7))
    parts.append(mtext((wx - ww + dx + dw) / 2 + 30, (wy + wh + dy) / 2 + 6,
                       ["після max_retries", "→ вивантаження в DLQ"],
                       size=10.5, color=POS, lh=1.3))

    parts.append(text(W / 2, 590,
                      "Чотири вузли повністю розв'язані в просторі й часі: веб-сервер не чекає виконання, "
                      "а воркери масштабуються незалежно від обсягу HTTP-трафіку.",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "queue-architecture.svg"), W, H, *parts)


# ── Фігура 8: повтори з відступом, джитер та таймаути ──────────────────────────
def retry_backoff_jitter():
    W, H = 1200, 560
    parts = []
    parts.append(text(W / 2, 32, "Механізм повторів: експоненційний відступ, тремтіння та таймаути",
                      size=17, bold=True))

    # Лінія повторів
    y_lane = 140
    xs = (140, 410, 720, 1040)
    
    b1, w1, h1 = box_at(xs[0], y_lane, "Спроба #1\nВиконання\nЗбій: 429 Rate Limit",
                        size=11, bold=True, fill="#faf3e0", stroke=POS, min_w=150)
    b2, w2, h2 = box_at(xs[1], y_lane, "Спроба #2\nПауза ~2–4 с\nЗбій: Lock Timeout",
                        size=11, bold=True, fill="#faf3e0", stroke=POS, min_w=150)
    b3, w3, h3 = box_at(xs[2], y_lane, "Спроба #3\nПауза ~6–10 с\nЗбій: Connection Reset",
                        size=11, bold=True, fill="#faf3e0", stroke=POS, min_w=160)
    b4, w4, h4 = box_at(xs[3], y_lane, "Вичерпано max_retries\nПеренаправлення в DLQ\nСповіщення Sentry / Alert",
                        size=11, bold=True, fill="#fdecea", stroke=POS, min_w=200)

    parts.append(arrow(xs[0] + w1, y_lane, xs[1] - w2, y_lane, color=POS, sw=1.7))
    parts.append(text((xs[0] + w1 + xs[1] - w2) / 2, y_lane - 16, "backoff #1 (2^1 · база + jitter)",
                      size=10, color=POS))

    parts.append(arrow(xs[1] + w2, y_lane, xs[2] - w3, y_lane, color=POS, sw=1.7))
    parts.append(text((xs[1] + w2 + xs[2] - w3) / 2, y_lane - 16, "backoff #2 (2^2 · база + jitter)",
                      size=10, color=POS))

    parts.append(arrow(xs[2] + w3, y_lane, xs[3] - w4, y_lane, color=POS, sw=1.7))
    parts.append(text((xs[2] + w3 + xs[3] - w4) / 2, y_lane - 16, "ліміт спроб досягнуто",
                      size=10, bold=True, color=POS))

    parts.extend((b1, b2, b3, b4))

    # Нижня частина: Таймаути (Soft vs Hard)
    y_to = 360
    sb, sw, sh = box_at(280, y_to,
                        "Soft Time Limit (М'який таймаут)\n"
                        "Сигнал SIGUSR1 / виняток SoftTimeLimitExceeded\n"
                        "Воркер перехоплює виняток у коді задачі\n"
                        "Коректне закриття транзакцій, файлів і сокетів\n"
                        "Збереження прогресу та планова реєстрація збою",
                        size=11.5, bold=True, fill="#faf3e0", stroke=INK, min_w=390)
    parts.append(sb)

    hb, hw, hh = box_at(920, y_to,
                        "Hard Time Limit (Жорсткий таймаут)\n"
                        "Сигнал ядра SIGKILL (-9) процесу воркера\n"
                        "Примусове знищення процесу без очищення\n"
                        "Master-процес виявляє падіння дочірнього воркера\n"
                        "Перезапуск нового процесу та повернення задачі",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, min_w=390)
    parts.append(hb)

    parts.append(arrow(280 + sw, y_to, 920 - hw, y_to, color=POS, sw=1.7))
    parts.append(mtext((280 + sw + 920 - hw) / 2, y_to - 30,
                       ["якщо воркер не завершився", "за Grace Period (напр. 15 с)"],
                       size=10.5, color=POS, lh=1.3))

    parts.append(text(W / 2, 510,
                      "Випадковий джитер розбиває синхронні хвилі повторів, а подвійний таймаут (Soft + Hard) "
                      "захищає пул від зависання на безкінечних циклах чи блокуючих сокетах.",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "retry-backoff-jitter.svg"), W, H, *parts)


# ── Фігура 9: періодичний планувальник і розподілений замок ───────────────────
def periodic_scheduler_lock():
    W, H = 1140, 520
    parts = []
    parts.append(text(W / 2, 32, "Архітектура періодичного планувальника (Beat) та розподілений замок",
                      size=17, bold=True))

    # Лідер і Standby
    s1, w1, h1 = box_at(220, 150,
                        "Scheduler Вузол A (Active Leader)\n"
                        "Утримує розподілений замок у Redis\n"
                        "Генерує часові такти (Tick що секунду)\n"
                        "Обчислює розклад періодичних cron-задач",
                        size=11.5, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=290)
    parts.append(s1)

    s2, w2, h2 = box_at(220, 330,
                        "Scheduler Вузол B (Standby)\n"
                        "Періодично намагається взяти замок\n"
                        "Спить, поки активний Вузол A\n"
                        "Миттєво стає лідером при збої вузла A",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=290)
    parts.append(s2)

    # Розподілений замок
    lk, lw, lh = box_at(590, 240,
                        "Розподілений замок (Redlock)\n"
                        "SET lock:scheduler <uuid> NX EX 15\n"
                        "Автопродовження оренди кожні 5 с\n"
                        "Запобігає подвійному плануванню",
                        size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=280)
    parts.append(lk)

    parts.append(arrow(220 + w1, 150, 590 - lw, 220, color=FIELD, sw=1.7))
    parts.append(text((220 + w1 + 590 - lw) / 2, 172, "утримує замок", size=10.5, color=FIELD))

    parts.append(arrow(220 + w2, 330, 590 - lw, 260, color=MUTED, sw=1.5))
    parts.append(text((220 + w2 + 590 - lw) / 2, 308, "опитує замок", size=10.5, color=MUTED))

    # Ready Queue & Worker Pool
    rq, qw, qh = box_at(950, 150,
                        "Ready Queue (Черга брокера)\n"
                        "Звичайна черга виконання задач\n"
                        "Планувальник НЕ виконує задачі сам —\n"
                        "він лише пушить task_id у чергу",
                        size=11.5, bold=True, fill="#faf3e0", stroke=INK, min_w=270)
    parts.append(rq)

    wp, ww, wh = box_at(950, 330,
                        "Worker Pool (Пул воркерів)\n"
                        "Вичерпує чергу готових задач\n"
                        "Воркери не знають, чи задача надійшла\n"
                        "від користувача, чи за cron-розкладом",
                        size=11.5, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=270)
    parts.append(wp)

    parts.append(arrow(220 + w1, 130, 950 - qw, 130, color=FIELD, sw=1.7))
    parts.append(text((220 + w1 + 950 - qw) / 2, 116, "постановка задачі в чергу (XADD / LPUSH)",
                      size=10.5, color=FIELD))

    parts.append(arrow(950, 150 + qh, 950, 330 - wh, color=INK, sw=1.7))
    parts.append(text(950 + 72, (150 + qh + 330 - wh) / 2, "fetch & execute",
                      size=10.5, color=INK, anchor="middle"))

    parts.append(text(W / 2, 470,
                      "Планувальник відокремлений від воркерів: він відповідає лише за таймінг і постановку задач, "
                      "а розподілений замок гарантує, що жодна щохвилинна задача не здублюється в кластері.",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "periodic-scheduler-lock.svg"), W, H, *parts)


# ── Фігура 10: конвеєр обробки телеметрії IoT ──────────────────────────────────
def iot_telemetry_pipeline():
    W, H = 1180, 560
    parts = []
    parts.append(text(W / 2, 32, "Конвеєр фонової обробки телеметрії IoT на базі Redis Streams",
                      size=17, bold=True))

    # Вхідний шлюз
    d_box, dw, dh = box_at(160, 200,
                           "IoT Пристрої\n"
                           "50 000 польових сенсорів\n"
                           "Пакет: device_id, seq_no,\n"
                           "temp, pressure, battery, ts",
                           size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=210)
    parts.append(d_box)

    g_box, gw, gh = box_at(420, 200,
                           "Ingestion Gateway\n"
                           "HTTP / MQTT веб-сервер\n"
                           "Валідація підпису та структури\n"
                           "XADD iot:telemetry:stream",
                           size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=210)
    parts.append(g_box)

    parts.append(arrow(160 + dw, 200, 420 - gw, 200, color=NEG, sw=1.7))
    parts.append(text((160 + dw + 420 - gw) / 2, 184, "HTTP POST / MQTT", size=10.5, color=NEG))

    # Redis Stream
    s_box, sw, sh = box_at(710, 200,
                           "Redis Stream\n"
                           "«iot:telemetry:stream»\n"
                           "Consumer Group «telemetry_workers»\n"
                           "PEL (Pending Entries List) облік\n"
                           "Гарантія At-least-once",
                           size=11.5, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=250)
    parts.append(s_box)

    parts.append(arrow(420 + gw, 200, 710 - sw, 200, color=FIELD, sw=1.7))
    parts.append(text((420 + gw + 710 - sw) / 2, 184, "XADD stream *", size=10.5, color=FIELD))

    # Вихідні гілки (Success / DLQ)
    w1_box, w1w, w1h = box_at(1020, 140,
                              "Worker · Deduplication & DB\n"
                              "SET pkg:<dev>:<seq> NX EX 3600\n"
                              "Запис у Time-Series DB (Timescale)\n"
                              "XACK повідомлення в Stream",
                              size=11, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=250)
    parts.append(w1_box)

    w2_box, w2w, w2h = box_at(1020, 330,
                              "Dead Letter Stream (DLQ)\n"
                              "«iot:telemetry:dlq»\n"
                              "Пошкоджені або отруйні пакети\n"
                              "Аудит аномалій сенсорів і алертинг",
                              size=11, bold=True, fill="#fdecea", stroke=POS, min_w=250)
    parts.append(w2_box)

    parts.append(arrow(710 + sw, 180, 1020 - w1w, 140, color=FIELD, sw=1.7))
    parts.append(text((710 + sw + 1020 - w1w) / 2, 146, "XREADGROUP / успіх", size=10.5, color=FIELD))

    parts.append(arrow(710 + sw, 220, 1020 - w2w, 330, color=POS, sw=1.7))
    parts.append(text((710 + sw + 1020 - w2w) / 2, 286, "збій після 3 спроб", size=10.5, color=POS))

    parts.append(text(W / 2, 490,
                      "Вхідний шлюз скидає пакети в Redis Stream за частки мілісекунди, а пул воркерів з дедуплікацією "
                      "надійно захищає часову базу даних від подвійних записів та перевантаження.",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "iot-telemetry-pipeline.svg"), W, H, *parts)


if __name__ == "__main__":
    sync_vs_queue()
    job_lifecycle()
    hist_counter_loop()
    hist_queue_generations()
    claim_skip_locked()
    lease_timeline()
    queue_architecture()
    retry_backoff_jitter()
    periodic_scheduler_lock()
    iot_telemetry_pipeline()
    print("figures written to", IMG)

