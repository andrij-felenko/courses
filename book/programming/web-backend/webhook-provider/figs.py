# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: Проблема подвійного запису проти Transactional Outbox ─────────
def fig_outbox_dual_write():
    W, H = 1000, 520
    p = []
    p.append(text(W / 2, 28, 'Проблема подвійного запису проти патерну Transactional Outbox', size=17, bold=True))

    p.append(line(40, 260, W - 40, 260, color=MUTED, sw=1, dash='6 6'))

    # ---- ВЕРХ: ПРЯМИЙ ПОДВІЙНИЙ ЗАПИС (НЕНАДІЙНО) ----
    p.append(text(70, 52, '1. Прямий виклик або публікація (Dual-Write): ризик неузгодженості', size=13, bold=True, color=NEG, anchor='start'))

    app1, w1, h1 = box_at(160, 140, 'Застосунок\n(Бекенд)', size=13, bold=True, min_w=140)
    db1, dw1, dh1 = box_at(500, 100, 'База даних\nINSERT orders\n(COMMIT ✓)', size=12, fill='#eaf7ef', stroke=POS, min_w=170)
    ext1, ew1, eh1 = box_at(840, 180, 'Сервер клієнта\nабо Брокер черги\n(HTTP 504 / Падіння ✗)', size=12, fill='#fdecea', stroke=NEG, min_w=190)

    for b in (app1, db1, ext1):
        p.append(b)

    p.append(arrow(160 + w1, 125, 500 - dw1, 100, color=POS, sw=1.8))
    p.append(text(310, 95, '1. Транзакція успішна', size=11, color=POS, bold=True))

    p.append(arrow(160 + w1, 155, 840 - ew1, 180, color=NEG, sw=1.8))
    p.append(text(460, 190, '2. Мережевий збій або креш між кроками', size=11, color=NEG, bold=True))
    p.append(text(500, 235, 'НАСЛІДОК: замовлення створено, але подію втрачено назавжди (або навпаки)', size=12, italic=True, color=NEG))

    # ---- НИЗ: TRANSACTIONAL OUTBOX (АТОМАРНО) ----
    p.append(text(70, 290, '2. Transactional Outbox: єдина локальна транзакція БД', size=13, bold=True, color=FIELD, anchor='start'))

    app2, w2, h2 = box_at(150, 390, 'Застосунок\n(Бекенд)', size=13, bold=True, min_w=130)
    db_box, dbw, dbh = box_at(440, 390, 'База даних (Єдина транзакція)\n[Таблиця orders] + [Таблиця outbox]\n(Атомарний COMMIT)', size=12, fill='#eaf7ef', stroke=POS, min_w=240)
    relay, rw, rh = box_at(710, 390, 'Outbox Relay\n(CDC / Poller)\nSKIP LOCKED', size=12, fill='#eaf0fd', stroke=FIELD, min_w=140)
    queue, qw, qh = box_at(900, 390, 'Черга задач\n(RabbitMQ / Kafka / Redis)', size=12, fill='#f5f0ff', stroke=ACCENT if 'ACCENT' in dir() else NEG, min_w=130)

    for b in (app2, db_box, relay, queue):
        p.append(b)

    p.append(arrow(150 + w2, 390, 440 - dbw, 390, color=POS, sw=2))
    p.append(text(285, 375, 'Єдиний COMMIT', size=11, color=POS, bold=True))

    p.append(arrow(440 + dbw, 390, 710 - rw, 390, color=FIELD, sw=1.8))
    p.append(text(575, 375, 'Читання подій', size=11, color=FIELD))

    p.append(arrow(710 + rw, 390, 900 - qw, 390, color=NEG, sw=1.8))
    p.append(text(805, 375, 'Публікація', size=11, color=NEG))

    p.append(text(500, 485, 'Подія гарантовано зберігається разом із бізнес-даними; relay передає її в чергу', size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, 'outbox-dual-write.svg'), W, H, *p)


# ── Фігура 2: Повний конвеєр доставки вебхуків ──────────────────────────────
def fig_provider_pipeline():
    W, H = 1020, 560
    p = []
    p.append(text(W / 2, 28, 'Архітектура надійного провайдера вебхуків', size=17, bold=True))

    y_main = 140
    b_outbox, w_ob, _ = box_at(100, y_main, 'Outbox Table\n(БД подій)', size=12, bold=True, min_w=130)
    b_relay, w_rel, _ = box_at(270, y_main, 'Outbox Relay\n(CDC / Poller)', size=12, fill='#eaf0fd', stroke=FIELD, min_w=130)
    b_queue, w_q, _ = box_at(450, y_main, 'Брокер черг\n(Delayed / Fair)', size=12, fill='#f5f0ff', stroke=NEG, min_w=130)
    b_worker, w_w, _ = box_at(660, y_main, 'Пул HTTP-воркерів\n+ Circuit Breaker', size=12, fill='#eaf7ef', stroke=POS, min_w=160)
    b_client, w_c, _ = box_at(900, y_main, 'Ендпоінт клієнта\n(HTTPS POST)', size=12, bold=True, min_w=140)

    for b in (b_outbox, b_relay, b_queue, b_worker, b_client):
        p.append(b)

    p.append(arrow(100 + w_ob, y_main, 270 - w_rel, y_main, sw=1.7))
    p.append(arrow(270 + w_rel, y_main, 450 - w_q, y_main, sw=1.7))
    p.append(arrow(450 + w_q, y_main, 660 - w_w, y_main, sw=1.7))
    p.append(arrow(660 + w_w, y_main, 900 - w_c, y_main, color=FIELD, sw=2))

    # 1. Успіх (2xx)
    p.append(arrow(900, y_main + 35, 900, 270, color=POS, sw=1.8))
    b_ok, wok, _ = box_at(900, 305, 'HTTP 2xx (Ack)\nЗапис у журнал успіху', size=12, fill='#eaf7ef', stroke=POS, min_w=160)
    p.append(b_ok)

    # 2. Тимчасовий збій (5xx / Timeout / 429) -> Ретрай з backoff
    p.append(arrow(820, y_main + 35, 650, 365, color=NEG, sw=1.8))
    b_retry, wr, _ = box_at(520, 390, 'Ретрай-планувальник\nExponential Backoff + Jitter\nt = 2ⁿ · t₀ + rand()', size=12, fill='#fff9db', stroke='#d97706', min_w=220)
    p.append(b_retry)
    p.append(text(760, 260, '5xx / Timeout / 429', size=11, color=NEG, bold=True))

    p.append(arrow(520 - wr, 390, 450, 200, color='#d97706', sw=1.8))
    p.append(text(385, 310, 'Відкладена черга', size=11, color='#d97706'))

    # 3. Безнадійні збої -> DLQ
    b_dlq, wdlq, _ = box_at(160, 480, 'Dead-Letter Queue (DLQ)\nЗбереження помилок + Алерти\n+ UI/API ручного повтору', size=12, fill='#fdecea', stroke=NEG, min_w=240)
    p.append(b_dlq)

    p.append(arrow(520, 435, 160 + wdlq, 480, color=NEG, sw=1.8))
    p.append(text(410, 475, 'Вичерпано спроби (attempts > max)', size=11, color=NEG))

    p.append(text(510, 535, 'Конвеєр ізолює збої зовнішніх сервісів і забезпечує гарантію At-Least-Once', size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'provider-pipeline.svg'), W, H, *p)


# ── Фігура 3: Ретрай-криві: чистий Backoff проти Backoff з Jitter ───────────
def fig_backoff_jitter():
    W, H = 980, 480
    p = []
    p.append(text(W / 2, 28, 'Синхронізація ретраїв (Thundering Herd) проти рандомізації з Jitter', size=16, bold=True))

    p.append(line(W / 2, 55, W / 2, 435, color=MUTED, sw=1, dash='6 6'))

    # ---- ЛІВОРУЧ: ЧИСТИЙ EXPONENTIAL BACKOFF ----
    p.append(text(245, 60, 'ЧИСТИЙ BACKOFF (БЕЗ JITTER)', size=13, bold=True, color=NEG))
    p.append(text(245, 82, 'Ретраї клієнтів синхронізуються у вузькі піки', size=11, color=MUTED))

    p.append(arrow(60, 360, 440, 360, color=MUTED, sw=1.5))
    p.append(text(440, 380, 'Час (t)', size=11, color=MUTED))

    p.append(arrow(60, 360, 60, 110, color=MUTED, sw=1.5))
    p.append(text(50, 105, 'RPS', size=11, color=MUTED))

    spikes = [(100, 130, 't = 1s'), (170, 150, 't = 2s'), (250, 180, 't = 4s'), (350, 220, 't = 8s')]
    for x, h_top, lbl in spikes:
        p.append(rect(x - 12, h_top, 24, 360 - h_top, rx=3, fill='#fdecea', stroke=NEG, sw=1.5))
        p.append(text(x, h_top - 10, 'Пік!', size=10, color=NEG, bold=True))
        p.append(text(x, 375, lbl, size=10, color=MUTED))

    p.append(text(245, 420, 'Усі воркери б\'ють одночасно → новий колапс', size=11, italic=True, color=NEG))

    # ---- ПРАВОРУЧ: BACKOFF + FULL JITTER ----
    p.append(text(735, 60, 'BACKOFF + FULL JITTER', size=13, bold=True, color=POS))
    p.append(text(735, 82, 'Випадковий зсув t = rand(0, 2ⁿ · t₀) розмазує трафік', size=11, color=MUTED))

    p.append(arrow(550, 360, 930, 360, color=MUTED, sw=1.5))
    p.append(text(930, 380, 'Час (t)', size=11, color=MUTED))

    p.append(arrow(550, 360, 550, 110, color=MUTED, sw=1.5))
    p.append(text(540, 105, 'RPS', size=11, color=MUTED))

    regions = [(570, 80, 280, '0–1s'), (660, 110, 295, '0–2s'), (740, 180, 315, '0–4s')]
    for rx_pos, rw_val, top_y, lbl in regions:
        p.append(rect(rx_pos, top_y, rw_val, 360 - top_y, rx=4, fill='#eaf7ef', stroke=POS, sw=1.4))
        p.append(text(rx_pos + rw_val / 2, top_y - 8, lbl, size=10, color=POS))

    p.append(text(735, 420, 'Навантаження плавне → сервер встигає відновитися', size=11, italic=True, color=POS))

    render(os.path.join(IMG, 'backoff-jitter-curves.svg'), W, H, *p)


# ── Фігура 4: Ізоляція клієнтів: Head-of-Line Blocking проти Fair Queueing ──
def fig_fair_queueing():
    W, H = 1000, 520
    p = []
    p.append(text(W / 2, 28, 'Ізоляція черг: блокування пулу (Head-of-Line) проти Fair-Share', size=16, bold=True))

    p.append(line(40, 260, W - 40, 260, color=MUTED, sw=1, dash='6 6'))

    # ---- ВЕРХ: ЄДИНА FIFO ЧЕРГА (HEAD-OF-LINE BLOCKING) ----
    p.append(text(60, 55, '1. Спільна FIFO-черга: повільний клієнт А захоплює всі слоти воркерів', size=12, bold=True, color=NEG, anchor='start'))

    q_box, qw, qh = box_at(220, 140, 'Спільна черга FIFO\n[Подія А] [Подія А] [Подія А] [Подія Б] [Подія В]', size=11, fill='#fdecea', stroke=NEG, min_w=300)
    p.append(q_box)

    w_pool, wpw, wph = box_at(620, 140, 'Пул HTTP-воркерів (4/4 зайняті)\nВоркер 1: чекає А (таймаут 30s)...\nВоркер 2: чекає А (таймаут 30s)...\nВоркер 3: чекає А (таймаут 30s)...\nВоркер 4: чекає А (таймаут 30s)...', size=11, fill='#fdecea', stroke=NEG, min_w=270)
    p.append(w_pool)

    fast_box, fbw, _ = box_at(900, 140, 'Клієнти Б і В\n(Швидкі)\nЗАБЛОКОВАНІ ✗', size=11, fill='#fff0f0', stroke=NEG, min_w=130)
    p.append(fast_box)

    p.append(arrow(220 + qw, 140, 620 - wpw, 140, color=NEG, sw=1.8))
    p.append(arrow(620 + wpw, 140, 900 - fbw, 140, color=MUTED, sw=1.4))
    p.append(text(500, 230, 'Один висячий бекенд блокує доставку тисячам здорових клієнтів', size=11, italic=True, color=NEG))

    # ---- НИЗ: FAIR-SHARE / TENANT ISOLATION ----
    p.append(text(60, 290, '2. Fair-Share Queueing: окремі черги або ліміти за клієнтами', size=12, bold=True, color=POS, anchor='start'))

    q_fair, qfw, qfh = box_at(220, 395, 'Черги за тенантами (Leaky / Fair)\nЧерга А (ліміт: 1 слот/с)\nЧерга Б (ліміт: 10 слотів/с)\nЧерга В (ліміт: 10 слотів/с)', size=11, fill='#eaf0fd', stroke=FIELD, min_w=300)
    p.append(q_fair)

    w_fair, wfw, wfh = box_at(620, 395, 'Пул HTTP-воркерів (розділені слоти)\nСлот 1: Клієнт А (ізольований)\nСлот 2: Клієнт Б (відправлено ✓)\nСлот 3: Клієнт В (відправлено ✓)\nСлот 4: Вільний резерв', size=11, fill='#eaf7ef', stroke=POS, min_w=270)
    p.append(w_fair)

    fast_ok, fokw, _ = box_at(900, 395, 'Клієнти Б і В\n(Швидкі)\nДОСТАВЛЕНО ✓', size=11, fill='#eaf7ef', stroke=POS, min_w=130)
    p.append(fast_ok)

    p.append(arrow(220 + qfw, 395, 620 - wfw, 395, color=POS, sw=1.8))
    p.append(arrow(620 + wfw, 395, 900 - fokw, 395, color=POS, sw=1.8))
    p.append(text(500, 490, 'Квота клієнта А обмежена; клієнти Б і В отримують події без затримок', size=11, italic=True, color=POS))

    render(os.path.join(IMG, 'fair-queueing-isolation.svg'), W, H, *p)


# ── Фігура 5: Автомат станів Circuit Breaker для ендпоінтів ────────────────
def fig_circuit_breaker():
    W, H = 960, 460
    p = []
    p.append(text(W / 2, 28, 'Автомат станів Circuit Breaker для зовнішнього ендпоінта', size=16, bold=True))

    c_box, cw, ch = box_at(180, 200, 'CLOSED\n(Нормальний стан)\nУсі події відправляються\nРахується відсоток помилок', size=12, bold=True, fill='#eaf7ef', stroke=POS, min_w=220)
    p.append(c_box)

    o_box, ow, oh = box_at(780, 200, 'OPEN\n(Запобіжник розімкнуто)\nДоставка призупинена\nПодії йдуть у retry-чергу\nБез мережевих викликів', size=12, bold=True, fill='#fdecea', stroke=NEG, min_w=220)
    p.append(o_box)

    h_box, hw, hh = box_at(480, 380, 'HALF-OPEN\n(Пробний стан)\nВідправляється 1 пробний запит', size=12, bold=True, fill='#fff9db', stroke='#d97706', min_w=220)
    p.append(h_box)

    p.append(arrow(180 + cw, 180, 780 - ow, 180, color=NEG, sw=2))
    p.append(text(480, 160, 'Помилки > 50% або 5 таймаутів поспіль', size=11, color=NEG, bold=True))

    p.append(arrow(780, 200 + oh, 480 + hw, 380, color='#d97706', sw=1.8))
    p.append(text(690, 330, 'Таймер охолодження (напр. 60s)', size=11, color='#d97706', bold=True))

    p.append(arrow(480 - hw, 380, 180, 200 + ch, color=POS, sw=2))
    p.append(text(270, 330, 'Пробний HTTP 2xx ✓', size=11, color=POS, bold=True))

    p.append(arrow(480 + hw - 40, 360, 780 - ow + 40, 200 + oh, color=NEG, sw=1.8))
    p.append(text(570, 270, 'Пробний запит ✗ (5xx/Timeout)', size=11, color=NEG))

    p.append(text(W / 2, 435, 'Запобіжник зберігає ресурси воркерів і не спамить лежачий сервер споживача', size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'circuit-breaker-states.svg'), W, H, *p)


if __name__ == '__main__':
    fig_outbox_dual_write()
    fig_provider_pipeline()
    fig_backoff_jitter()
    fig_fair_queueing()
    fig_circuit_breaker()
    print('Всі фігури згенеровано успішно.')
