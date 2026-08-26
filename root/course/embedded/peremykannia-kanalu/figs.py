# -*- coding: utf-8 -*-
"""Фігури до теми «Перемикання каналу: мульти-інтерфейс і резервування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Архітектура мульти-інтерфейсного вузла ────────────────────────────────
def fig_multi_interface_topology():
    W, H = 820, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Архітектура вузла з кількома фізичними каналами зв'язку", size=16, bold=True))

    # Верхній блок: Застосунок і черга буфера
    app_w, app_h = 420, 60
    app_x, app_y = W / 2 - app_w / 2, 55
    f.append(rect(app_x, app_y, app_w, app_h, fill="#f8fafc", stroke=LINE, sw=1.5))
    f.append(text(W / 2, app_y + 24, "Застосунок і генератор телеметрії", size=14, bold=True))
    f.append(text(W / 2, app_y + 45, "Кільцевий енергонезалежний буфер черги офлайну (Flash / RAM)", size=11.5, color=MUTED))

    # Центральний блок: Диспетчер перемикання (Failover Arbiter)
    arb_w, arb_h = 580, 110
    arb_x, arb_y = W / 2 - arb_w / 2, 155
    f.append(rect(arb_x, arb_y, arb_w, arb_h, fill="#edf2f7", stroke="#2b6cb0", sw=2))
    f.append(text(W / 2, arb_y + 24, "Диспетчер інтерфейсів (Transport & Failover Manager)", size=14, bold=True, color="#2b6cb0"))

    # Внутрішні блоки диспетчера
    sub_w, sub_h = 170, 55
    # Блок 1: L1/L2 статус
    b1_x = arb_x + 15
    f.append(rect(b1_x, arb_y + 40, sub_w, sub_h, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(b1_x + sub_w / 2, arb_y + 60, "L1/L2 Link Sense", size=12, bold=True))
    f.append(text(b1_x + sub_w / 2, arb_y + 78, "PHY Interrupts / MDIO", size=10.5, color=MUTED))

    # Блок 2: L3/L7 Зонд
    b2_x = arb_x + 205
    f.append(rect(b2_x, arb_y + 40, sub_w, sub_h, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(b2_x + sub_w / 2, arb_y + 60, "L3/L7 Health Probe", size=12, bold=True))
    f.append(text(b2_x + sub_w / 2, arb_y + 78, "ICMP Echo / TLS Keepalive", size=10.5, color=MUTED))

    # Блок 3: Автомат переходів
    b3_x = arb_x + 395
    f.append(rect(b3_x, arb_y + 40, sub_w, sub_h, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(b3_x + sub_w / 2, arb_y + 60, "Автомат гістерезису", size=12, bold=True))
    f.append(text(b3_x + sub_w / 2, arb_y + 78, "Hold-down & Fallback delay", size=10.5, color=MUTED))

    # Стрілка між Застосунком і Диспетчером
    f.append(arrow(W / 2, app_y + app_h, W / 2, arb_y, color=LINE, sw=1.8))

    # Ліва гілка: Основний канал (Ethernet / Wi-Fi)
    prim_x, prim_y = 60, 310
    prim_w, prim_h = 320, 100
    f.append(rect(prim_x, prim_y, prim_w, prim_h, fill="#e6fffa", stroke="#234e52", sw=1.6))
    f.append(text(prim_x + prim_w / 2, prim_y + 24, "Основний інтерфейс (Primary: Ethernet / Wi-Fi)", size=13, bold=True, color="#234e52"))
    f.append(text(prim_x + prim_w / 2, prim_y + 46, "Висока швидкість · Нульова вартість трафіку", size=11, color=INK))
    f.append(text(prim_x + prim_w / 2, prim_y + 66, "Пріоритетна метрика маршруту (Default GW)", size=11, color=FIELD, bold=True))
    f.append(text(prim_x + prim_w / 2, prim_y + 86, "Постійний моніторинг PHY + L7 пінги", size=10.5, color=MUTED))

    # Права гілка: Резервний канал (Cellular LTE / NB-IoT)
    sec_x, sec_y = 440, 310
    sec_w, sec_h = 320, 100
    f.append(rect(sec_x, sec_y, sec_w, sec_h, fill="#fffaf0", stroke="#7b341e", sw=1.6))
    f.append(text(sec_x + sec_w / 2, sec_y + 24, "Резервний інтерфейс (Backup: Cellular LTE / NB-IoT)", size=13, bold=True, color="#7b341e"))
    f.append(text(sec_x + sec_w / 2, sec_y + 46, "Тарифікація мегабайтів · Автономне покриття", size=11, color=INK))
    f.append(text(sec_x + sec_w / 2, sec_y + 66, "Керування живленням: Cold / Warm / Hot Standby", size=11, color=POS, bold=True))
    f.append(text(sec_x + sec_w / 2, sec_y + 86, "Активація за вимогою (Failover Trigger)", size=10.5, color=MUTED))

    # Стрілки від диспетчера до каналів
    f.append(arrow(arb_x + 100, arb_y + arb_h, prim_x + prim_w / 2, prim_y, color=LINE, sw=1.6))
    f.append(arrow(arb_x + arb_w - 100, arb_y + arb_h, sec_x + sec_w / 2, sec_y, color=LINE, sw=1.6))

    # Нижній блок: Хмарний сервер / Інтернет
    net_w, net_h = 440, 50
    net_x, net_y = W / 2 - net_w / 2, 450
    f.append(rect(net_x, net_y, net_w, net_h, fill="#f7fafc", stroke=LINE, sw=1.5, rx=12))
    f.append(text(W / 2, net_y + 30, "Віддалений сервер застосунку / Хмарний брокер", size=13, bold=True))

    # Стрілки від інтерфейсів до хмари
    f.append(arrow(prim_x + prim_w / 2, prim_y + prim_h, net_x + 80, net_y, color=FIELD, sw=1.8))
    f.append(arrow(sec_x + sec_w / 2, sec_y + sec_h, net_x + net_w - 80, net_y, color=POS, sw=1.8))

    return render(os.path.join(IMG, "multi-interface-topology.svg"), W, H, *f)


# ── 2. Часова діаграма перемикання з гістерезисом ─────────────────────────────
def fig_failover_timing_diagram():
    W, H = 860, 480
    f = []

    f.append(text(W / 2, 26, "Часова діаграма перемикання та повернення каналу (Flapping Protection)", size=15, bold=True))

    ox = 170
    ex = 830
    y_base = 65

    # 1. Стан фізичного / L7 лінку Primary
    y1 = y_base + 30
    f.append(text(ox - 12, y1 + 15, "Основний канал", size=12, bold=True, anchor="end"))
    f.append(text(ox - 12, y1 + 30, "(Primary: Eth)", size=10.5, color=MUTED, anchor="end"))

    # Часові точки:
    # 170 .. 290: Primary OK (120 px)
    # 290 .. 580: Аварія L7 (290 px)
    # 580 .. 730: Карантин / Fallback delay (150 px)
    # 730 .. 830: Відновлено в роботу (100 px)
    p1 = 290  # аварія
    p2 = 580  # фізичне відновлення
    p3 = 730  # завершення fallback delay

    f.append(rect(ox, y1, p1 - ox, 32, fill="#c6f6d5", stroke="#22543d", sw=1.4))
    f.append(text(ox + (p1 - ox) / 2, y1 + 20, "Основний активний", size=11, color="#22543d", bold=True))

    f.append(rect(p1, y1, p2 - p1, 32, fill="#fed7d7", stroke="#742a2a", sw=1.4))
    f.append(text(p1 + (p2 - p1) / 2, y1 + 20, "АВАРІЯ (L7 Black Hole)", size=11, color="#742a2a", bold=True))

    f.append(rect(p2, y1, p3 - p2, 32, fill="#feebc8", stroke="#7b341e", sw=1.4))
    f.append(text(p2 + (p3 - p2) / 2, y1 + 20, "Карантин (Фонові пінги)", size=11, color="#7b341e", bold=True))

    f.append(rect(p3, y1, ex - p3, 32, fill="#c6f6d5", stroke="#22543d", sw=1.4))
    f.append(text(p3 + (ex - p3) / 2, y1 + 20, "Відновлено", size=11, color="#22543d", bold=True))

    # 2. Стан резервного модуля
    y2 = y1 + 80
    f.append(text(ox - 12, y2 + 15, "Резервний канал", size=12, bold=True, anchor="end"))
    f.append(text(ox - 12, y2 + 30, "(Backup: LTE)", size=10.5, color=MUTED, anchor="end"))

    # 170 .. 345: Сон (175 px)
    # 345 .. 405: Запуск (60 px)
    # 405 .. 730: Активний резерв (325 px)
    # 730 .. 830: Вимкнено (100 px)
    s1 = 345  # початок запуску після T_failover (290 .. 345)
    s2 = 405  # модем підключився до IP
    s3 = 730  # вимкнення модема після повернення на primary

    f.append(rect(ox, y2, s1 - ox, 32, fill="#edf2f7", stroke="#4a5568", sw=1.4))
    f.append(text(ox + (s1 - ox) / 2, y2 + 20, "Сон / Standby (0 мА)", size=11, color="#4a5568"))

    f.append(rect(s1, y2, s2 - s1, 32, fill="#e2e8f0", stroke="#4a5568", sw=1.4))
    f.append(text(s1 + (s2 - s1) / 2, y2 + 20, "Старт", size=10.5, bold=True))

    f.append(rect(s2, y2, s3 - s2, 32, fill="#feebc8", stroke="#c05621", sw=1.4))
    f.append(text(s2 + (s3 - s2) / 2, y2 + 20, "АКТИВНИЙ РЕЗЕРВ (Передача трафіку)", size=11, color="#7b341e", bold=True))

    f.append(rect(s3, y2, ex - s3, 32, fill="#edf2f7", stroke="#4a5568", sw=1.4))
    f.append(text(s3 + (ex - s3) / 2, y2 + 20, "Вимкнено", size=11, color="#4a5568"))

    # 3. Активний маршрут трафіку
    y3 = y2 + 80
    f.append(text(ox - 12, y3 + 15, "Активний маршрут", size=12, bold=True, anchor="end"))
    f.append(text(ox - 12, y3 + 30, "(Data Egress)", size=10.5, color=MUTED, anchor="end"))

    f.append(rect(ox, y3, p1 - ox, 32, fill="#ebf8ff", stroke="#2b6cb0", sw=1.4))
    f.append(text(ox + (p1 - ox) / 2, y3 + 20, "Шлюз: Primary", size=11, color="#2b6cb0", bold=True))

    f.append(rect(p1, y3, s2 - p1, 32, fill="#fff5f5", stroke="#c53030", sw=1.4))
    f.append(text(p1 + (s2 - p1) / 2, y3 + 20, "Черга офлайну", size=10.5, color="#c53030", bold=True))

    f.append(rect(s2, y3, s3 - s2, 32, fill="#feebc8", stroke="#c05621", sw=1.4))
    f.append(text(s2 + (s3 - s2) / 2, y3 + 20, "Шлюз: Backup (LTE)", size=11, color="#7b341e", bold=True))

    f.append(rect(s3, y3, ex - s3, 32, fill="#ebf8ff", stroke="#2b6cb0", sw=1.4))
    f.append(text(s3 + (ex - s3) / 2, y3 + 20, "Шлюз: Primary", size=11, color="#2b6cb0", bold=True))

    # Інтервали часу та пояснення
    y4 = y3 + 60
    # Інтервал T_failover (290 .. 345)
    f.append(line(p1, y4, s1, y4, color=POS, sw=1.8))
    f.append(line(p1, y4 - 6, p1, y4 + 6, color=POS, sw=1.5))
    f.append(line(s1, y4 - 6, s1, y4 + 6, color=POS, sw=1.5))
    f.append(text((p1 + s1) / 2, y4 + 16, "T_failover", size=11, bold=True, color=POS))
    f.append(text((p1 + s1) / 2, y4 + 28, "3 втрати L7", size=9.5, color=MUTED))

    # Інтервал T_hold_down (405 .. 555)
    hold_end = 555
    f.append(line(s2, y4, hold_end, y4, color="#4a5568", sw=1.8))
    f.append(line(s2, y4 - 6, s2, y4 + 6, color="#4a5568", sw=1.5))
    f.append(line(hold_end, y4 - 6, hold_end, y4 + 6, color="#4a5568", sw=1.5))
    f.append(text((s2 + hold_end) / 2, y4 + 16, "T_hold_down (мін. час на резерві)", size=11, bold=True, color="#4a5568"))

    # Інтервал T_fallback (580 .. 730)
    y5 = y4 + 48
    f.append(line(p2, y5, p3, y5, color=FIELD, sw=1.8))
    f.append(line(p2, y5 - 6, p2, y5 + 6, color=FIELD, sw=1.5))
    f.append(line(p3, y5 - 6, p3, y5 + 6, color=FIELD, sw=1.5))
    f.append(text((p2 + p3) / 2, y5 + 16, "T_fallback (Затримка стабілізації перед поверненням)", size=11, bold=True, color=FIELD))
    f.append(text((p2 + p3) / 2, y5 + 28, "100% успішних зондів протягом 3-5 хв", size=9.5, color=MUTED))

    # Вертикальні пунктирні лінії маркерів подій
    f.append(line(p1, y1 - 10, p1, y4 + 10, color=POS, sw=1.2, dash="3,3"))
    f.append(line(p2, y1 - 10, p2, y5 + 10, color=FIELD, sw=1.2, dash="3,3"))
    f.append(line(p3, y1 - 10, p3, y5 + 10, color="#2b6cb0", sw=1.2, dash="3,3"))

    return render(os.path.join(IMG, "failover-timing-diagram.svg"), W, H, *f)


if __name__ == "__main__":
    fig_multi_interface_topology()
    fig_failover_timing_diagram()
    print("All figures generated successfully.")
