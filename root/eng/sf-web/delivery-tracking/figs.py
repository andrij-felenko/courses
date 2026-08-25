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


# ── Фігура 1: Скінченний автомат станів доставки сповіщення ──────────────────
def fig_delivery_state_machine():
    W, H = 1000, 520
    p = []
    p.append(text(W / 2, 28, 'Скінченний автомат життєвого циклу доставки сповіщення', size=16, bold=True))

    # Головний ланцюг станів (успішний шлях)
    p.append(text(80, 75, 'Успішний ланцюг переходів (монотонне зростання рангу)', size=12, bold=True, color=FIELD, anchor='start'))

    b_created, w_c, h_c = box_at(120, 150, 'CREATED\n(Outbox, ранг 0)', size=12, fill='#f4f6f8', stroke=LINE, min_w=130)
    b_disp, w_dp, h_dp = box_at(310, 150, 'DISPATCHED\n(У воркері, ранг 1)', size=12, fill='#eaf0fd', stroke=NEG, min_w=140)
    b_sent, w_s, h_s = box_at(510, 150, 'SENT\n(Шлюз прийняв, ранг 2)', size=12, fill='#eaf0fd', stroke=NEG, min_w=150)
    b_deliv, w_dv, h_dv = box_at(720, 150, 'DELIVERED\n(Пристрій підтвердив, ранг 3)', size=12, fill='#eaf7ef', stroke=FIELD, min_w=160)
    b_opened, w_op, h_op = box_at(900, 150, 'OPENED\n(Клік / Прочитано, ранг 4)', size=12, fill='#eaf7ef', stroke=FIELD, min_w=140)

    for b in (b_created, b_disp, b_sent, b_deliv, b_opened):
        p.append(b)

    p.append(arrow(120 + w_c, 150, 310 - w_dp, 150, color=LINE, sw=1.8))
    p.append(arrow(310 + w_dp, 150, 510 - w_s, 150, color=LINE, sw=1.8))
    p.append(arrow(510 + w_s, 150, 720 - w_dv, 150, color=FIELD, sw=1.8))
    p.append(arrow(720 + w_dv, 150, 900 - w_op, 150, color=FIELD, sw=1.8))

    p.append(text(215, 132, 'Вибірка з черги', size=10, color=MUTED))
    p.append(text(410, 132, 'HTTP 200 OK шлюзу', size=10, color=MUTED))
    p.append(text(615, 132, 'DSN-вебхук / ACK', size=10, color=FIELD, bold=True))
    p.append(text(810, 132, 'Піксель / Deep Link', size=10, color=FIELD, bold=True))

    # Нижні стани відмов і помилок
    p.append(line(40, 240, W - 40, 240, color=MUTED, sw=1, dash='4 4'))
    p.append(text(80, 265, 'Гілки помилок, ретраїв та вичерпання терміну придатності', size=12, bold=True, color=POS, anchor='start'))

    b_trans, w_tr, h_tr = box_at(260, 350, 'FAILED_TRANSIENT\n(Мережевий збій, 429 / 5xx)\nПовтор через Backoff + Jitter', size=11, fill='#fff8e6', stroke='#d48806', min_w=190)
    b_perm, w_pm, h_pm = box_at(590, 350, 'FAILED_PERMANENT\n(410 Dead Token, Hard Bounce)\nЗапуск Fallback-каскаду', size=11, fill='#fdecea', stroke=POS, min_w=200)
    b_exp, w_ex, h_ex = box_at(860, 350, 'EXPIRED\n(TTL вичерпано)\nСкасування доставки', size=11, fill='#f4f6f8', stroke=MUTED, min_w=160)

    for b in (b_trans, b_perm, b_exp):
        p.append(b)

    # Стрілки помилок
    p.append(arrow(310, 150 + h_dp, 260, 350 - h_tr, color='#d48806', sw=1.5))
    p.append(arrow(260 - w_tr / 2, 350 - h_tr, 310 - w_dp / 2, 150 + h_dp, color='#d48806', sw=1.5))
    p.append(text(210, 230, 'Retry', size=10, color='#d48806', bold=True))

    p.append(arrow(510, 150 + h_s, 590 - w_pm / 4, 350 - h_pm, color=POS, sw=1.5))
    p.append(text(585, 230, 'Фатальна помилка', size=10, color=POS))

    p.append(arrow(720, 150 + h_dv, 860 - w_ex / 4, 350 - h_ex, color=MUTED, sw=1.5))
    p.append(text(820, 230, 't > created + TTL', size=10, color=MUTED))

    # Нижній банер з правилом монотонності
    b_rule, _, _ = box_at(W / 2, 465, 'Правило монотонності: UPDATE notification SET status = :new WHERE id = :id AND status_rank(:new) > status_rank(status);\nЗахищає стан від пізніх вебхуків (наприклад, DSN-підтвердження доставки прийшло після кліку користувача по лінку).', size=11, fill='#f0fdf4', stroke=FIELD, min_w=860)
    p.append(b_rule)

    render(os.path.join(IMG, 'delivery-state-machine.svg'), W, H, *p)


# ── Фігура 2: Каскадне перемикання каналів (Waterfall Fallback) ───────────────
def fig_multi_channel_cascade():
    W, H = 1000, 520
    p = []
    p.append(text(W / 2, 26, 'Архітектура каскадної доставки (Waterfall Fallback)', size=16, bold=True))

    # Лівий блок — подія
    b_event, we, he = box_at(110, 260, 'Критична подія\n(2FA-код / Алертинг)\nTTL = 120 с', size=12, fill='#f4f6f8', stroke=LINE, min_w=140)
    b_router, wr, hr = box_at(290, 260, 'Cascade Router\n(Оцінка доступності\nта вартості каналів)', size=12, fill='#eaf0fd', stroke=NEG, min_w=150)

    p.append(b_event)
    p.append(b_router)
    p.append(arrow(110 + we, 260, 290 - wr, 260, color=LINE, sw=1.8))
    p.append(text(200, 245, 'Outbox Event', size=10, color=MUTED))

    # Канал 1 (Push)
    p.append(text(540, 65, 'Крок 1: Швидкий і дешевий канал (.00)', size=11, bold=True, color=FIELD, anchor='start'))
    b_ch1, w1, h1 = box_at(620, 110, 'Канал 1: Мобільний Push (APNs / FCM)\nПеревірка валідності токена пристрою', size=11, fill='#eaf7ef', stroke=FIELD, min_w=280)
    b_ok1, wok1, hok1 = box_at(890, 110, 'DELIVERED ✓\n(ACK за 2–5 с)', size=11, fill='#eaf7ef', stroke=FIELD, min_w=120)

    p.append(b_ch1)
    p.append(b_ok1)
    p.append(arrow(290 + wr, 245, 620 - w1, 110, color=FIELD, sw=1.8))
    p.append(arrow(620 + w1, 110, 890 - wok1, 110, color=FIELD, sw=1.8))
    p.append(text(790, 95, 'Отримано ACK', size=10, color=FIELD))

    # Канал 2 (SMS)
    p.append(text(540, 215, 'Крок 2: Fallback при таймауті або 410 Gone (.04/SMS)', size=11, bold=True, color='#d48806', anchor='start'))
    b_ch2, w2, h2 = box_at(620, 260, 'Канал 2: SMS / WhatsApp (Twilio / Meta)\nВідправка на підтверджений номер', size=11, fill='#fff8e6', stroke='#d48806', min_w=280)
    b_ok2, wok2, hok2 = box_at(890, 260, 'DELIVERED ✓\n(DSN за 10–20 с)', size=11, fill='#eaf7ef', stroke=FIELD, min_w=120)

    p.append(b_ch2)
    p.append(b_ok2)
    p.append(arrow(620, 110 + h1, 620, 260 - h2, color='#d48806', sw=1.8))
    p.append(text(690, 185, 'Таймаут 45 с / Нема токена', size=10, color='#d48806'))
    p.append(arrow(620 + w2, 260, 890 - wok2, 260, color=FIELD, sw=1.8))
    p.append(text(790, 245, 'DSN delivered', size=10, color=FIELD))

    # Канал 3 (Email / Voice)
    p.append(text(540, 365, 'Крок 3: Резервний канал при збої стільникової мережі', size=11, bold=True, color=POS, anchor='start'))
    b_ch3, w3, h3 = box_at(620, 410, 'Канал 3: Транзакційний Email / Voice\n(AWS SES / SMTP Gateway / Рободзвінок)', size=11, fill='#fdecea', stroke=POS, min_w=280)
    b_ok3, wok3, hok3 = box_at(890, 410, 'DELIVERED ✓\n(SMTP 250 OK)', size=11, fill='#eaf7ef', stroke=FIELD, min_w=120)

    p.append(b_ch3)
    p.append(b_ok3)
    p.append(arrow(620, 260 + h2, 620, 410 - h3, color=POS, sw=1.8))
    p.append(text(700, 335, 'SMPP failure / Таймаут 60 с', size=10, color=POS))
    p.append(arrow(620 + w3, 410, 890 - wok3, 410, color=FIELD, sw=1.8))

    # Загальний дедлайн
    b_footer, _, _ = box_at(W / 2, 485, 'Захист від дублювання: успішне підтвердження в попередньому каналі негайно скасовує заплановані таски наступних кроків каскаду.', size=11, fill='#f8fafc', stroke=MUTED, min_w=860)
    p.append(b_footer)

    render(os.path.join(IMG, 'multi-channel-cascade.svg'), W, H, *p)


if __name__ == '__main__':
    fig_delivery_state_machine()
    fig_multi_channel_cascade()
    print('Figures generated successfully!')
