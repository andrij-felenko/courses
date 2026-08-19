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


# ── Фігура 1: Версіонування подій і ланцюжок трансформацій ─────────────────
def version_pinning_transform():
    W, H = 960, 480
    p = []
    p.append(text(W / 2, 28, "Версіонування схем подій та фіксація версії (API Version Pinning)", size=16, bold=True))

    # Канонічна доменна подія (актуальна модель)
    cx, cy = 160, 120
    b, hw, hh = box_at(cx, cy, "Канонічна подія (v2026-03)\n{\n  event_id: 'evt_991',\n  amount: 4500,\n  currency: 'usd',\n  billing: { address: '...' }\n}", size=12, bold=False, fill="#fdfefe", stroke=LINE, min_w=240)
    p.append(b)
    p.append(text(cx, cy - hh - 12, "Доменна сутність (ядро)", size=13, bold=True, color=FIELD))

    # Маршрутизатор та реєстр підписок
    rx, ry = 480, 120
    b, rhw, rhh = box_at(rx, ry, "Реєстр підписок кінцевих точок\nЕндпоінт A: pinned_version = '2026-03'\nЕндпоінт B: pinned_version = '2024-11'\nЕндпоінт C: pinned_version = '2022-08'", size=12, bold=False, fill="#eaf0fd", stroke=NEG, min_w=270)
    p.append(b)
    p.append(text(rx, ry - rhh - 12, "Маршрутизатор та профілі клієнтів", size=13, bold=True, color=NEG))

    p.append(arrow(cx + hw + 10, cy, rx - rhw - 10, cy, color=LINE, sw=1.6))
    p.append(text((cx + hw + rx - rhw) / 2, cy - 10, "fan-out", size=11, color=MUTED))

    # Ланцюжок зворотної трансформації для старого клієнта (Ендпоінт C)
    p.append(arrow(rx, ry + rhh + 10, rx, 250, color=NEG, sw=1.6))
    p.append(text(rx + 8, 235, "для версії 2022-08", size=11, color=NEG, anchor="start"))

    t1x, t1y = 480, 290
    b1, t1hw, t1hh = box_at(t1x, t1y, "Трансформатор v2026-03 → v2024-11\n(Розгортання billing.address у плоске поле address)", size=11, fill="#fff8e7", stroke="#d48806", min_w=340)
    p.append(b1)

    p.append(arrow(t1x, t1y + t1hh + 5, t1x, t1y + t1hh + 35, color=LINE, sw=1.5))

    t2x, t2y = 480, 390
    b2, t2hw, t2hh = box_at(t2x, t2y, "Трансформатор v2024-11 → v2022-08\n(amount → amount_cents, currency → uppercase)", size=11, fill="#fff8e7", stroke="#d48806", min_w=340)
    p.append(b2)

    # Результат відправки для трьох клієнтів
    out_x = 810
    b_a, _, _ = box_at(out_x, 120, "HTTP POST → Ендпоінт A\nВерсія схеми: 2026-03\n{ amount: 4500, billing: {...} }", size=11, fill="#eaf7ef", stroke=FIELD, min_w=220)
    p.append(b_a)
    p.append(arrow(rx + rhw + 10, 120, out_x - 110, 120, color=FIELD, sw=1.6))
    p.append(text((rx + rhw + out_x - 110) / 2, 108, "без змін", size=11, color=FIELD))

    b_c, _, _ = box_at(out_x, 390, "HTTP POST → Ендпоінт C\nВерсія схеми: 2022-08\n{ amount_cents: 4500, address: '...' }", size=11, fill="#eaf7ef", stroke=FIELD, min_w=220)
    p.append(b_c)
    p.append(arrow(t2x + t2hw + 10, 390, out_x - 110, 390, color=FIELD, sw=1.6))
    p.append(text((t2x + t2hw + out_x - 110) / 2, 378, "трансформовано", size=11, color=FIELD))

    render(os.path.join(IMG, "version-pinning-transform.svg"), W, H, *p)


# ── Фігура 2: Ротація секрету та двоетапний підпис ─────────────────────────
def secret_rotation_window():
    W, H = 960, 460
    p = []
    p.append(text(W / 2, 28, "Ротація секретів без зупинки: двоетапний підпис (Dual-Signing Window)", size=16, bold=True))

    # Шкала часу
    p.append(line(80, 80, 880, 80, color=LINE, sw=2))
    p.append(arrow(870, 80, 890, 80, color=LINE, sw=2))
    p.append(text(890, 100, "Час", size=12, bold=True, anchor="end"))

    # Фази
    f1_x = 220
    f2_x = 520
    f3_x = 780

    p.append(circle(f1_x, 80, 6, fill=FIELD, stroke=FIELD))
    p.append(text(f1_x, 62, "1. Звичайна робота", size=12, bold=True, color=FIELD))

    p.append(circle(f2_x, 80, 6, fill=POS, stroke=POS))
    p.append(text(f2_x, 62, "2. Ротація: Двопідписне вікно (24-48 год)", size=12, bold=True, color=POS))

    p.append(circle(f3_x, 80, 6, fill=NEG, stroke=NEG))
    p.append(text(f3_x, 62, "3. Старий секрет відкликано", size=12, bold=True, color=NEG))

    # Пояснювальні блоки для фаз
    # Фаза 1
    b1, _, _ = box_at(f1_x, 210, "Активний секрет:\nwhsec_old\n\nЗаголовок підпису:\nStripe-Signature:\nt=1718873600,\nv1=sig(whsec_old)", size=11, fill="#fdfefe", stroke=LINE, min_w=200)
    p.append(b1)
    b1_c, _, _ = box_at(f1_x, 370, "Сервер клієнта:\nПеревіряє за whsec_old\nРезультат: OK (200)", size=11, fill="#eaf7ef", stroke=FIELD, min_w=200)
    p.append(b1_c)
    p.append(arrow(f1_x, 290, f1_x, 325, color=FIELD, sw=1.5))

    # Фаза 2
    b2, _, _ = box_at(f2_x, 210, "Активні секрети:\nwhsec_old ТА whsec_new\n\nЗаголовок підпису:\nStripe-Signature:\nt=1718873600,\nv1=sig(whsec_old),\nv1=sig(whsec_new)", size=11, fill="#fff8e7", stroke="#d48806", min_w=240)
    p.append(b2)
    b2_c, _, _ = box_at(f2_x, 370, "Сервер клієнта (в процесі деплою):\nСтарий код -> валідує sig(whsec_old)\nОновлений код -> валідує sig(whsec_new)\nРезультат: OK (0 відмов)", size=11, fill="#eaf7ef", stroke=FIELD, min_w=240)
    p.append(b2_c)
    p.append(arrow(f2_x, 290, f2_x, 325, color=FIELD, sw=1.5))

    # Фаза 3
    b3, _, _ = box_at(f3_x, 210, "Активний секрет:\nwhsec_new (старий видалено)\n\nЗаголовок підпису:\nStripe-Signature:\nt=1718873600,\nv1=sig(whsec_new)", size=11, fill="#fdfefe", stroke=LINE, min_w=200)
    p.append(b3)
    b3_c, _, _ = box_at(f3_x, 370, "Сервер клієнта:\nПеревіряє за whsec_new\nРезультат: OK (200)", size=11, fill="#eaf7ef", stroke=FIELD, min_w=200)
    p.append(b3_c)
    p.append(arrow(f3_x, 290, f3_x, 325, color=FIELD, sw=1.5))

    render(os.path.join(IMG, "secret-rotation-window.svg"), W, H, *p)


# ── Фігура 3: Анатомія запису журналу доставки та телеметрія ───────────────
def delivery_lifecycle_audit():
    W, H = 960, 500
    p = []
    p.append(text(W / 2, 28, "Анатомія журналу діагностики (Event & Delivery Logs) та телеметрія", size=16, bold=True))

    # Ліва колонка: Запит платформи
    lx = 240
    b_req, hw_r, hh_r = box_at(lx, 150, "HTTP POST /webhook\nЗаголовки:\n• User-Agent: WebhookPlatform/2.0\n• Webhook-Delivery: deliv_8912\n• Webhook-Signature: t=171887...,v1=4a2f...\n• Content-Type: application/json\n\nТіло (JSON payload):\n{\n  'id': 'evt_441',\n  'type': 'order.completed',\n  'created': 1718873600\n}", size=11, fill="#fdfefe", stroke=NEG, min_w=340)
    p.append(b_req)
    p.append(text(lx, 55, "1. Надісланий запит (Request Audit)", size=13, bold=True, color=NEG))

    # Права колонка: Отримана відповідь
    rx = 720
    b_res, hw_s, hh_s = box_at(rx, 150, "HTTP Відповідь сервера клієнта\nСтатус-код: 504 Gateway Timeout\nЗаголовки:\n• Server: nginx/1.24\n• Content-Type: text/html\n• X-Request-ID: req_c87a\n\nТіло (Truncated Excerpt):\n<html><head><title>504 Gateway\nTimeout</title></head><body>...", size=11, fill="#fdfefe", stroke=POS, min_w=340)
    p.append(b_res)
    p.append(text(rx, 55, "2. Отримана відповідь (Response Audit)", size=13, bold=True, color=POS))

    # Середня діагностична панель (Метрики часу та збою)
    mx = W / 2
    my = 360
    b_diag, _, _ = box_at(mx, my, "Телеметрія виконання спроби deliv_8912 (Event: evt_441)\n• DNS Lookup: 14 ms  |  • TLS Handshake: 42 ms  |  • TTFB: 4980 ms  |  • Загальний час: 5036 ms\n• Діагноз збою: HTTP_TIMEOUT (Перевищено ліміт 5000 ms з боку проксі-сервера клієнта)\n• Наступна автоматична спроба: через 60 с (спроба 2 з 8)", size=11, fill="#fff8e7", stroke="#d48806", min_w=780)
    p.append(b_diag)
    p.append(text(mx, 290, "3. Діагностична телеметрія та таймінги", size=13, bold=True, color="#d48806"))

    # Стрілка ручного перезапуску
    p.append(arrow(180, 440, 780, 440, color=FIELD, sw=2))
    p.append(text(mx, 462, "Ручний перезапуск (Manual Resend): надсилає ту саму evt_441 з новим deliv_8913", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "delivery-lifecycle-audit.svg"), W, H, *p)


# ── Фігура 4: Автомат станів кінцевої точки та Circuit Breaking ────────────
def endpoint_circuit_breaker():
    W, H = 960, 440
    p = []
    p.append(text(W / 2, 28, "Автомат станів кінцевої точки: відмова, сповіщення та Circuit Breaking", size=16, bold=True))

    s1_x, s1_y = 160, 150
    b1, _, _ = box_at(s1_x, s1_y, "АКТИВНИЙ (Healthy)\n• Помилок < 5%\n• Спроби без затримок\n• SLA 99.9%", size=12, fill="#eaf7ef", stroke=FIELD, min_w=200)
    p.append(b1)

    s2_x, s2_y = 480, 150
    b2, _, _ = box_at(s2_x, s2_y, "ДЕГРАДАЦІЯ (Degraded)\n• Серія помилок 5xx/Timeout\n• Експоненційний відступ\n• Сповіщення розробнику (Warning)", size=12, fill="#fff8e7", stroke="#d48806", min_w=240)
    p.append(b2)

    s3_x, s3_y = 800, 150
    b3, _, _ = box_at(s3_x, s3_y, "ВИМКНЕНО (Disabled)\n• > 100 помилок або 72 год\n• Доставку призупинено\n• Критичне сповіщення на Email", size=12, fill="#fdecea", stroke=POS, min_w=220)
    p.append(b3)

    # Переходи
    p.append(arrow(s1_x + 105, s1_y - 15, s2_x - 125, s2_y - 15, color="#d48806", sw=1.8))
    p.append(text((s1_x + s2_x) / 2, s1_y - 30, "10 помилок поспіль", size=11, color="#d48806"))

    p.append(arrow(s2_x - 125, s2_y + 25, s1_x + 105, s1_y + 25, color=FIELD, sw=1.8))
    p.append(text((s1_x + s2_x) / 2, s1_y + 42, "Успішна відповідь 2xx", size=11, color=FIELD))

    p.append(arrow(s2_x + 125, s2_y, s3_x - 115, s3_y, color=POS, sw=2))
    p.append(text((s2_x + s3_x) / 2, s2_y - 15, "Вичерпано ліміт спроб", size=11, color=POS))

    # Нижній зворотний перехід: самообслуговування
    p.append(arrow(s3_x, s3_y + 60, s3_x, 320, color=FIELD, sw=1.6))
    p.append(line(s3_x, 320, s1_x, 320, color=FIELD, sw=1.6))
    p.append(arrow(s1_x, 320, s1_x, s1_y + 60, color=FIELD, sw=1.6))
    p.append(text(W / 2, 345, "Self-Service відновлення: виправлення сервера + успішний тестовий Ping -> Активація", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "endpoint-circuit-breaker.svg"), W, H, *p)


# ── Фігура 5: Архітектура черг та ізоляція трафіку ─────────────────────────
def outbound_architecture_queues():
    W, H = 960, 480
    p = []
    p.append(text(W / 2, 28, "Архітектура диспетчера: Outbox, розділення черг та ізоляція навантаження", size=16, bold=True))

    # Джерело: Доменні сервіси + БД
    b_src, hw_src, _ = box_at(130, 130, "Доменні сервіси\n(Платежі, Замовлення)\n\nТранзакційний Outbox\n(Таблиця webhook_events)", size=11, fill="#fdfefe", stroke=LINE, min_w=180)
    p.append(b_src)

    # Маршрутизатор
    b_rtr, hw_rtr, _ = box_at(360, 130, "Outbox CDC / Poller\n+\nМаршрутизатор підписок\n(Схеми, Версіонування)", size=11, fill="#eaf0fd", stroke=NEG, min_w=180)
    p.append(b_rtr)
    p.append(arrow(130 + hw_src + 5, 130, 360 - hw_rtr - 5, 130, color=LINE, sw=1.6))

    # Розділені черги
    qx = 620
    b_q1, _, _ = box_at(qx, 80, "Пріоритетна Live-черга\n(Свіжі події, затримка < 200 ms)", size=11, fill="#eaf7ef", stroke=FIELD, min_w=240)
    b_q2, _, _ = box_at(qx, 180, "Черга повторів (Retry Backoff)\n(Відкладені спроби 1хв - 24год)", size=11, fill="#fff8e7", stroke="#d48806", min_w=240)
    b_q3, _, _ = box_at(qx, 280, "Черга ручного перевідправлення (Replay)\n(Низький пріоритет, без блокування Live)", size=11, fill="#eaf0fd", stroke=NEG, min_w=240)
    b_q4, _, _ = box_at(qx, 380, "Мертва черга (Dead Letter Queue / DLQ)\n(Незворотні збої, для розслідування)", size=11, fill="#fdecea", stroke=POS, min_w=240)
    p.append(b_q1)
    p.append(b_q2)
    p.append(b_q3)
    p.append(b_q4)

    p.append(arrow(360 + hw_rtr + 5, 130, qx - 125, 80, color=FIELD, sw=1.5))
    p.append(arrow(360 + hw_rtr + 5, 130, qx - 125, 180, color="#d48806", sw=1.5))
    p.append(arrow(360 + hw_rtr + 5, 130, qx - 125, 280, color=NEG, sw=1.5))

    # Вихідний пул воркерів з Rate Limiting
    wx = 850
    b_w, _, _ = box_at(wx, 180, "Пул HTTP-воркерів\n• Ліміт конкурентності\n  на кожен клієнтський хост\n• Підпис HMAC SHA-256\n• Аудит запиту й відповіді", size=11, fill="#fdfefe", stroke=LINE, min_w=170)
    p.append(b_w)

    p.append(arrow(qx + 125, 80, wx - 90, 150, color=FIELD, sw=1.5))
    p.append(arrow(qx + 125, 180, wx - 90, 180, color="#d48806", sw=1.5))
    p.append(arrow(qx + 125, 280, wx - 90, 210, color=NEG, sw=1.5))

    p.append(arrow(wx, 260, wx, 380, color=POS, sw=1.5))
    p.append(arrow(wx, 380, qx + 125, 380, color=POS, sw=1.5))
    p.append(text(wx + 8, 320, "вичерпано спроби", size=10, color=POS, anchor="start"))

    render(os.path.join(IMG, "outbound-architecture-queues.svg"), W, H, *p)


if __name__ == "__main__":
    version_pinning_transform()
    secret_rotation_window()
    delivery_lifecycle_audit()
    endpoint_circuit_breaker()
    outbound_architecture_queues()
    print("All figures generated successfully.")
