# -*- coding: utf-8 -*-
"""Фігури теми «Маршрутизатор повідомлень». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"

# ── 1. direct-vs-routed: пряме зчеплення проти маршрутизатора ───────────────
def fig_direct_vs_routed():
    W, H = 1000, 430
    f = []

    # Ліва половина: Пряме зчеплення (N * M зв'язків)
    f.append(rect(15, 15, 470, 395, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 42, "Пряме зчеплення: відправники знають адресатів", size=13, bold=True, color=POS))

    producers_y = [110, 205, 300]
    p_labels = ["Сервіс чекауту\n(Checkout)", "Мобільний шлюз\n(API Gateway)", "Складський сервіс\n(Warehouse)"]
    for y, lbl in zip(producers_y, p_labels):
        b, _, _ = textbox(100, y, lbl, size=11, bold=True, min_w=125, pad=6, fill=FILL, stroke=LINE)
        f.append(b)

    consumers_y = [85, 145, 205, 265, 325]
    c_labels = ["Платежі ЄС (GDPR)", "Платежі США (Stripe)", "Фрод-контроль (ML)", "Аналітика замовлень", "Push-сповіщення"]
    for y, lbl in zip(consumers_y, c_labels):
        b, _, _ = textbox(385, y, lbl, size=10.5, min_w=145, pad=5, fill=RED_F, stroke=POS)
        f.append(b)

    # Заплутані лінії
    for py in producers_y:
        for cy in consumers_y:
            f.append(line(165, py, 310, cy, color="#e74c3c", sw=1, dash="3,3"))

    f.append(text(250, 390, "✗ N × M жорстких зв'язків: зміна топології ламає код відправників", size=10.5, color=POS, italic=True))

    # Права половина: Маршрутизатор повідомлень (Decoupled)
    f.append(rect(515, 15, 470, 395, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 42, "Маршрутизатор: повне розчеплення топології", size=13, bold=True, color=FIELD))

    for y, lbl in zip(producers_y, p_labels):
        b, _, _ = textbox(595, y, lbl, size=11, bold=True, min_w=120, pad=6, fill=FILL, stroke=LINE)
        f.append(b)

    # Маршрутизатор по центру
    router_box, _, _ = textbox(750, 205, "МАРШРУТИЗАТОР\n(Message Router)\n\n• Аналіз заголовків\n• Предикати вмісту\n• Динамічні списки\n• Ізоляція збоїв",
                               size=11, bold=True, min_w=135, pad=8, fill=BLUE_F, stroke=NEG, sw=1.8)
    f.append(router_box)

    for y, lbl in zip(consumers_y, c_labels):
        b, _, _ = textbox(905, y, lbl, size=10.5, min_w=135, pad=5, fill=GREEN_F, stroke=FIELD)
        f.append(b)

    # Стрілки відправник -> роутер
    for py in producers_y:
        f.append(arrow(660, py, 680, 205, color=NEG, sw=1.4))

    # Стрілки роутер -> отримувачі
    for cy in consumers_y:
        f.append(arrow(820, 205, 835, cy, color=FIELD, sw=1.3))

    f.append(text(750, 390, "✓ Відправник пише в один вхідний канал; роутер обирає адресатів", size=10.5, color=FIELD, italic=True))

    render(out("direct-vs-routed.svg"), W, H, *f,
           title="Пряме підключення проти маршрутизатора повідомлень")


# ── 2. routing-patterns-taxonomy: 6 ключових патернів EIP ──────────────────
def fig_routing_patterns_taxonomy():
    W, H = 1000, 520
    f = []

    f.append(rect(10, 10, 980, 500, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Сімейство патернів маршрутизації повідомлень (Enterprise Integration Patterns)", size=14, bold=True))

    # 6 карток 2 рядки по 3
    cards = [
        ("1. Content-Based Router", "Маршрутизація за вмістом",
         "Аналізує тіло чи тип повідомлення.\nСпрямовує в один цільовий канал\nза значенням поля (напр. валюта чи регіон).",
         180, 130),
        ("2. Message Filter", "Фільтр повідомлень",
         "Перевіряє булевий предикат.\nПропускає валідні повідомлення далі;\nневідповідні відкидає або пише в аудит.",
         500, 130),
        ("3. Recipient List", "Список отримувачів",
         "Динамічно обчислює список N каналів.\nОдне вхідне повідомлення тиражується\nлише адресатам із розрахованого списку.",
         820, 130),
        ("4. Dynamic Router", "Динамічний маршрутизатор",
         "Відокремлює логіку від правил.\nТаблиця маршрутів лежить у базі/Redis\nі оновлюється на льоту без перезапуску.",
         180, 340),
        ("5. Routing Slip", "Маршрутний лист",
         "Список наступних кроків прикріплено\nдо метаданих самого повідомлення.\nКожен сервіс викреслює себе й шле далі.",
         500, 340),
        ("6. Wire Tap", "Відвід потоку (прослуховувач)",
         "Прозоро копіює потік повідомлень\nу допоміжний канал (аудит, метрики, ML)\nбез затримки та впливу на основну гілку.",
         820, 340),
    ]

    for title, subtitle, desc, cx, cy in cards:
        f.append(rect(cx - 145, cy - 65, 290, 160, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        f.append(text(cx, cy - 42, title, size=12, bold=True, color=NEG))
        f.append(text(cx, cy - 25, subtitle, size=10.5, italic=True, color=MUTED))
        f.append(line(cx - 130, cy - 15, cx + 130, cy - 15, color=MUTED, sw=0.8))
        f.append(mtext(cx, cy + 10, desc.split("\n"), size=10.5, color=INK, lh=1.35))

    render(out("routing-patterns-taxonomy.svg"), W, H, *f,
           title="Сімейство патернів маршрутизації повідомлень")


# ── 3. routing-slip-flow: життєвий цикл повідомлення з маршрутним листом ────
def fig_routing_slip_flow():
    W, H = 1000, 360
    f = []

    f.append(rect(10, 10, 980, 340, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 36, "Маршрутний лист (Routing Slip): послідовна обробка без центрального оркестратора", size=13.5, bold=True))

    steps = [
        ("1. Початок (Ingress)", "Впорскування списку\nSlip: [KYC, Fraud, Billing]", 120, 120, BLUE_F, NEG),
        ("2. Сервіс KYC", "Виконує валідацію\nSlip: [Fraud, Billing]", 370, 120, GREEN_F, FIELD),
        ("3. Фрод-контроль", "Оцінює кредитний ризик\nSlip: [Billing]", 630, 120, GREEN_F, FIELD),
        ("4. Сервіс білінгу", "Списує кошти з балансу\nSlip: [] (порожній)", 880, 120, GREEN_F, FIELD)
    ]

    for title, desc, cx, cy, fill_c, stroke_c in steps:
        f.append(rect(cx - 105, cy - 45, 210, 100, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        f.append(text(cx, cy - 22, title, size=12, bold=True, color=stroke_c))
        f.append(line(cx - 90, cy - 10, cx + 90, cy - 10, color=MUTED, sw=0.8))
        f.append(mtext(cx, cy + 15, desc.split("\n"), size=10.5, color=INK, lh=1.35))

    # Стрілки між кроками
    f.append(arrow(228, 120, 262, 120, color=LINE, sw=1.8))
    f.append(arrow(478, 120, 522, 120, color=LINE, sw=1.8))
    f.append(arrow(738, 120, 772, 120, color=LINE, sw=1.8))

    # Нижня плашка з поясненням
    f.append(rect(40, 210, 920, 115, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(500, 235, "Механіка заголовка Routing Slip на кожному етапі:", size=11.5, bold=True, color=INK))

    sub_desc = [
        "1. Вхідний шлюз формує заголовок X-Routing-Slip зі списком черг або кінцевих точок обробки.",
        "2. Сервіс зчитує повідомлення, виконує локальну дію, вилучає (pop) себе зі списку заголовка.",
        "3. Якщо в списку ще лишилися адресати — повідомлення автоматично пушиться на наступний крок.",
        "4. Коли список порожніє — конвеєр успішно завершено. Немає єдиного вузького місця оркестратора."
    ]
    f.append(mtext(500, 260, sub_desc, size=10, color=INK, lh=1.3))

    render(out("routing-slip-flow.svg"), W, H, *f,
           title="Послідовність обробки через Routing Slip")


# ── 4. router-performance-tradeoff: швидкий шлях (заголовки) vs повільний (тіло) ──
def fig_router_performance_tradeoff():
    W, H = 1000, 420
    f = []

    f.append(rect(10, 10, 980, 400, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 36, "Продуктивність та ізоляція збоїв у маршрутизаторі повідомлень", size=13.5, bold=True))

    # Ліва колонка: Fast Path (Header Routing)
    f.append(rect(30, 65, 455, 325, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(257, 95, "Швидкий шлях: маршрутизація за заголовками", size=12.5, bold=True, color=FIELD))
    f.append(line(50, 110, 465, 110, color=FIELD, sw=1))

    fast_items = [
        "• Зчитування транспортних метаданих (AMQP/Kafka headers)",
        "• Zero-copy сканування: тіло повідомлення не десеріалізується",
        "• Затримка: 2–10 мікросекунд на повідомлення",
        "• Пропускна здатність: сотні тисяч / мільйони msg/sec на ядро",
        "• Мінімальне навантаження на GC / алокатор пам'яті"
    ]
    f.append(mtext(257, 135, fast_items, size=10.5, color=INK, lh=1.4))

    fast_box, _, _ = textbox(257, 330, "Вхідний пакет → Заголовки (Тип/Регіон) → Цільова черга\n(Тіло передається як сирий зріз байтів без розбору)",
                             size=10, bold=False, min_w=415, pad=6, fill="#ffffff", stroke=FIELD)
    f.append(fast_box)

    # Права колонка: Slow Path + Dead Letter
    f.append(rect(515, 65, 455, 325, fill=WARN_F, stroke=POS, sw=1.5, rx=6))
    f.append(text(742, 95, "Глибокий аналіз вмісту та обробка аномалій", size=12.5, bold=True, color=POS))
    f.append(line(535, 110, 950, 110, color=POS, sw=1))

    slow_items = [
        "• Парсинг JSON/Protobuf/Avro для перевірки внутрішніх полів",
        "• Висока ціна CPU: десеріалізація займає 80–95% часу обробки",
        "• Ризик отруйних повідомлень (Poison Pill) при битому синтаксисі",
        "• Немаршрутизовані повідомлення скидаються в Dead Letter Queue",
        "• Зворотний тиск (Backpressure) при переповненні буфера черги"
    ]
    f.append(mtext(742, 135, slow_items, size=10.5, color=INK, lh=1.4))

    slow_box, _, _ = textbox(742, 330, "Битий JSON / Немає правила → Dead Letter Queue (DLQ)\n(Ізоляція помилок без зупинки основного конвеєра)",
                             size=10, bold=False, min_w=415, pad=6, fill="#ffffff", stroke=POS)
    f.append(slow_box)

    render(out("router-performance-tradeoff.svg"), W, H, *f,
           title="Швидкий шлях за метаданими проти глибокого аналізу вмісту")


if __name__ == '__main__':
    fig_direct_vs_routed()
    fig_routing_patterns_taxonomy()
    fig_routing_slip_flow()
    fig_router_performance_tradeoff()
    print("All figures generated successfully.")
