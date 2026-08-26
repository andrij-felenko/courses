# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми: Стан з'єднання як автомат.
Використовує спільну бібліотеку svgkit.
"""
import sys
import os

# scripts/ лежить на 4 рівні вище: root/course/embedded/<slug>/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)


def fig_forward_lifecycle():
    """Фігура 1: Прямий маршрут станів автомата від знеструмлення до передачі даних."""
    w, h = 900, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Прямий життєвий цикл з'єднання: послідовність станів та інваріанти", size=16, bold=True))

    # Стани організовано у 2 ряди по 5 блоків
    r1_y = 105
    r2_y = 315

    col_xs = [90, 265, 440, 615, 790]
    box_w = 140
    box_h = 70

    # Ряд 1: стани 1..5
    s1 = fitbox(col_xs[0] - box_w/2, r1_y - box_h/2, box_w, box_h, "NO_POWER\n[Знеструмлено]\nFET: OFF, Vcc=0V", size=12, fill="#fdedec", stroke=POS)
    s2 = fitbox(col_xs[1] - box_w/2, r1_y - box_h/2, box_w, box_h, "POWERING_ON\n[Старт живлення]\nPWRKEY=LOW (1.2s)", size=12, fill="#fef9e7", stroke="#d4ac0d")
    s3 = fitbox(col_xs[2] - box_w/2, r1_y - box_h/2, box_w, box_h, "MODEM_READY\n[AT інтерфейс]\nAT -> OK, Echo OFF", size=12, fill="#eafaf1", stroke=FIELD)
    s4 = fitbox(col_xs[3] - box_w/2, r1_y - box_h/2, box_w, box_h, "SIM_READY\n[Перевірка SIM]\n+CPIN: READY", size=12, fill="#eafaf1", stroke=FIELD)
    s5 = fitbox(col_xs[4] - box_w/2, r1_y - box_h/2, box_w, box_h, "NET_SEARCH\n[Пошук мережі]\n+CREG: 1 (Home) / 5", size=12, fill="#eafaf1", stroke=FIELD)

    frags.extend([s1, s2, s3, s4, s5])

    # Стрілки ряду 1
    frags.append(arrow(col_xs[0] + box_w/2 + 2, r1_y, col_xs[1] - box_w/2 - 4, r1_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[0] + col_xs[1]) / 2, r1_y - 12, "FET ON", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[1] + box_w/2 + 2, r1_y, col_xs[2] - box_w/2 - 4, r1_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[1] + col_xs[2]) / 2, r1_y - 12, "AT OK", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[2] + box_w/2 + 2, r1_y, col_xs[3] - box_w/2 - 4, r1_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[2] + col_xs[3]) / 2, r1_y - 12, "CPIN OK", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[3] + box_w/2 + 2, r1_y, col_xs[4] - box_w/2 - 4, r1_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[3] + col_xs[4]) / 2, r1_y - 12, "CREG=1", size=10, color=MUTED, bold=True))

    # Перехід між рядами (від NET_SEARCH до IP_ATTACH)
    frags.append(line(col_xs[4], r1_y + box_h/2 + 2, col_xs[4], 210, color=LINE, sw=1.8))
    frags.append(line(col_xs[4], 210, col_xs[0], 210, color=LINE, sw=1.8))
    frags.append(arrow(col_xs[0], 210, col_xs[0], r2_y - box_h/2 - 4, color=LINE, sw=1.8))
    frags.append(text(w / 2, 200, "ATTACH: отримано контекст оператора (+CGATT=1)", size=11, color=INK, bold=True))

    # Ряд 2: стани 6..10
    s6 = fitbox(col_xs[0] - box_w/2, r2_y - box_h/2, box_w, box_h, "IP_ATTACH\n[Виділення IP]\nIP: 10.x.x.x (PDP)", size=12, fill="#eafaf1", stroke=FIELD)
    s7 = fitbox(col_xs[1] - box_w/2, r2_y - box_h/2, box_w, box_h, "TCP_CONNECT\n[Транспорт/TLS]\nSocket CONNECT OK", size=12, fill="#eaf2f8", stroke=NEG)
    s8 = fitbox(col_xs[2] - box_w/2, r2_y - box_h/2, box_w, box_h, "PROTOCOL_AUTH\n[Автентифікація]\nMQTT CONNACK", size=12, fill="#eaf2f8", stroke=NEG)
    s9 = fitbox(col_xs[3] - box_w/2, r2_y - box_h/2, box_w, box_h, "READY_TO_SEND\n[Готовий до даних]\nСесія активна", size=12, fill="#d5f5e3", stroke=FIELD)
    s10 = fitbox(col_xs[4] - box_w/2, r2_y - box_h/2, box_w, box_h, "SENDING\n[Передача пачки]\nTX буфер -> ACK", size=12, fill="#d4efdf", stroke=FIELD)

    frags.extend([s6, s7, s8, s9, s10])

    # Стрілки ряду 2
    frags.append(arrow(col_xs[0] + box_w/2 + 2, r2_y, col_xs[1] - box_w/2 - 4, r2_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[0] + col_xs[1]) / 2, r2_y - 12, "CIPSTART", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[1] + box_w/2 + 2, r2_y, col_xs[2] - box_w/2 - 4, r2_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[1] + col_xs[2]) / 2, r2_y - 12, "TLS/Handshake", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[2] + box_w/2 + 2, r2_y, col_xs[3] - box_w/2 - 4, r2_y, color=LINE, sw=1.8))
    frags.append(text((col_xs[2] + col_xs[3]) / 2, r2_y - 12, "Auth OK", size=10, color=MUTED, bold=True))

    frags.append(arrow(col_xs[3] + box_w/2 + 2, r2_y - 12, col_xs[4] - box_w/2 - 4, r2_y - 12, color=LINE, sw=1.8))
    frags.append(text((col_xs[3] + col_xs[4]) / 2, r2_y - 24, "SEND_REQ", size=10, color=FIELD, bold=True))

    frags.append(arrow(col_xs[4] - box_w/2 - 4, r2_y + 12, col_xs[3] + box_w/2 + 2, r2_y + 12, color=LINE, sw=1.8))
    frags.append(text((col_xs[3] + col_xs[4]) / 2, r2_y + 26, "TX_DONE", size=10, color=MUTED, bold=True))

    # Нижня плашка з легендою
    frags.append(rect(40, 410, 820, 50, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    frags.append(text(w / 2, 430, "Інваріант надійності: кожен стан контролюється власним таймаутом і лічильником спроб.", size=12, color=INK, bold=True))
    frags.append(text(w / 2, 448, "Порушення умови переходу не зупиняє систему, а переводить її на відповідну сходинку відновлення.", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "fsm-forward-lifecycle.svg"), w, h, *frags)


def fig_rollback_matrix():
    """Фігура 2: Сходинки аварійного відновлення та матриця зворотних переходів."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 28, "Матриця локалізації аварій: 4 рівні глибини відкату", size=16, bold=True))

    tiers = [
        {
            "tier": "Рівень 1: Сесійний відкат",
            "trigger": "TCP KeepAlive Timeout / FIN / RST / MQTT розрив",
            "action": "Закриття сокета (CIPCLOSE) -> повторний TCP CONNECT",
            "target": "TCP_CONNECT",
            "color": "#ebf5fb", "stroke": NEG, "time": "1..5 секунд"
        },
        {
            "tier": "Рівень 2: PDP-контекстний відкат",
            "trigger": "Деактивація PDP (+CGEV: DEACT) / втрата IP",
            "action": "Переактивація контексту (CGACT=0, CGACT=1) -> новий IP",
            "target": "IP_ATTACH",
            "color": "#eafaf1", "stroke": FIELD, "time": "5..15 секунд"
        },
        {
            "tier": "Рівень 3: Радіо-відкат (Стільниковий лінк)",
            "trigger": "CREG: 3 (Denied) / CREG: 0 / втрата вежі оператора",
            "action": "Експоненційний відкат (Backoff) -> сканування радіоефіру",
            "target": "NET_SEARCH",
            "color": "#fef9e7", "stroke": "#d4ac0d", "time": "10..120 секунд"
        },
        {
            "tier": "Рівень 4: Апаратний відкат (Зависання модуля)",
            "trigger": "3x таймаут на AT команди (UART мертвий / напруга просіла)",
            "action": "1) Імпульс RESET -> 2) Повне знеструмлення ключем FET",
            "target": "NO_POWER",
            "color": "#fdedec", "stroke": POS, "time": "1..10 хвилин"
        }
    ]

    card_w = 820
    card_h = 80
    start_y = 65

    for i, t in enumerate(tiers):
        cy = start_y + i * 95
        # Фон картки
        frags.append(rect(40, cy, card_w, card_h, fill=t["color"], stroke=t["stroke"], sw=1.8, rx=6))

        # Ліва колонка: Назва рівня та час реакції
        frags.append(text(60, cy + 28, t["tier"], size=13, color=INK, anchor="start", bold=True))
        frags.append(text(60, cy + 54, "Ціль відкату: " + t["target"] + "  (" + t["time"] + ")", size=11, color=MUTED, anchor="start"))

        # Вертикальний розділювач
        frags.append(line(310, cy + 10, 310, cy + 70, color=t["stroke"], sw=1.0, dash="3,3"))

        # Середня колонка: Причина (Симптом відмови)
        frags.append(text(330, cy + 28, "Симптом відмови:", size=11, color=MUTED, anchor="start", bold=True))
        frags.append(text(330, cy + 52, t["trigger"], size=11, color=INK, anchor="start"))

        # Вертикальний розділювач
        frags.append(line(590, cy + 10, 590, cy + 70, color=t["stroke"], sw=1.0, dash="3,3"))

        # Права колонка: Дія відновлення
        frags.append(text(610, cy + 28, "Стратегія відновлення:", size=11, color=MUTED, anchor="start", bold=True))
        frags.append(text(610, cy + 52, t["action"], size=11, color=INK, anchor="start"))

    # Пояснювальний підпис унизу
    frags.append(text(w / 2, 458, "Головне правило стійкості: не смикати апаратне живлення там, де достатньо перезапустити сокет.", size=12, color=INK, bold=True))

    render(os.path.join(OUT_DIR, "fsm-rollback-matrix.svg"), w, h, *frags)


def fig_timing_backoff():
    """Фігура 3: Часова шкала таймаутів та експоненційного відкату з джиттером."""
    w, h = 900, 460
    frags = []

    frags.append(text(w / 2, 28, "Часова шкала таймаутів та експоненційного відкату (Backoff + Jitter)", size=16, bold=True))

    # Вісь часу
    axis_y = 120
    frags.append(arrow(60, axis_y, 840, axis_y, color=LINE, sw=2.0))
    frags.append(text(855, axis_y + 4, "t", size=14, color=INK, bold=True))

    # Кроки першої спроби
    # 1. Подача живлення (0s)
    frags.append(line(80, axis_y - 15, 80, axis_y + 15, color=POS, sw=2.0))
    frags.append(text(80, axis_y - 25, "0 с", size=11, color=MUTED))
    frags.append(text(80, axis_y + 32, "FET ON\n+ PWRKEY", size=10, color=INK, bold=True))

    # 2. Модем готовий (1.5s)
    frags.append(line(160, axis_y - 15, 160, axis_y + 15, color=FIELD, sw=2.0))
    frags.append(text(160, axis_y - 25, "1.5 с", size=11, color=MUTED))
    frags.append(text(160, axis_y + 32, "AT OK\nCPIN OK", size=10, color=INK, bold=True))

    # 3. Пошук мережі - таймаут (1.5s -> 61.5s)
    frags.append(rect(160, axis_y - 10, 160, 20, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    frags.append(text(240, axis_y + 4, "NET_SEARCH: Timeout 60 s", size=10, color=INK, bold=True))

    # 4. Помилка пошуку мережі (61.5s)
    frags.append(line(320, axis_y - 15, 320, axis_y + 15, color=POS, sw=2.0))
    frags.append(text(320, axis_y - 25, "61.5 с", size=11, color=POS, bold=True))
    frags.append(text(320, axis_y + 32, "CREG Timeout!\nRetry #1", size=10, color=POS, bold=True))

    # 5. Відкат 1 (Backoff 4s + Jitter)
    frags.append(rect(320, axis_y - 10, 70, 20, fill="#fadbd8", stroke=POS, sw=1.5, rx=3))
    frags.append(text(355, axis_y + 4, "Sleep 4s", size=10, color=INK))

    # 6. Спроба 2 - знову таймаут (65.5s -> 125.5s)
    frags.append(rect(390, axis_y - 10, 120, 20, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    frags.append(text(450, axis_y + 4, "NET_SEARCH (60s)", size=10, color=INK))

    # 7. Відкат 2 (Backoff 16s + Jitter)
    frags.append(rect(510, axis_y - 10, 100, 20, fill="#fadbd8", stroke=POS, sw=1.5, rx=3))
    frags.append(text(560, axis_y + 4, "Sleep 16s + Jitter", size=10, color=INK))

    # 8. Спроба 3 - Успіх реєстрації та швидке відкриття сокета
    frags.append(rect(610, axis_y - 10, 80, 20, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(650, axis_y + 4, "CREG: 1 OK", size=10, color=FIELD, bold=True))

    frags.append(line(690, axis_y - 15, 690, axis_y + 15, color=FIELD, sw=2.0))
    frags.append(text(750, axis_y + 32, "TCP CONNECT\n+ MQTT SEND (2s)", size=10, color=FIELD, bold=True))
    frags.append(rect(690, axis_y - 10, 120, 20, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(750, axis_y + 4, "ONLINE / TX OK", size=10, color=INK, bold=True))

    # Нижня частина: порівняння фіксованого інтервалу та експоненційного з джиттером
    b_y = 230
    frags.append(rect(50, b_y, 380, 190, fill="#fdfefe", stroke=POS, sw=1.5, rx=6))
    frags.append(text(240, b_y + 25, "Наївний підхід: Фіксований інтервал (5 с)", size=13, color=POS, bold=True))
    frags.append(text(70, b_y + 55, "• 10 000 лічильників відключаються через збій БС", size=11, color=INK, anchor="start"))
    frags.append(text(70, b_y + 80, "• Усі одночасно починають штурмувати RACH кожні 5 с", size=11, color=INK, anchor="start"))
    frags.append(text(70, b_y + 105, "• Повна колізія пакетів: мережа не встигає піднятися", size=11, color=INK, anchor="start"))
    frags.append(text(70, b_y + 130, "• Акумулятор розряджається в 10 разів швидше", size=11, color=INK, anchor="start"))
    frags.append(text(70, b_y + 160, "Результат: «Лавина запитів» (Thundering Herd)", size=11, color=POS, anchor="start", bold=True))

    frags.append(rect(470, b_y, 380, 190, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(660, b_y + 25, "Стійкий підхід: Експонента + Full Jitter", size=13, color=FIELD, bold=True))
    frags.append(text(490, b_y + 55, "• Інтервал подвоюється: T_k = min(T_max, T_base · 2^k)", size=11, color=INK, anchor="start"))
    frags.append(text(490, b_y + 80, "• Додається випадковий зсув: t_sleep = rand(0, T_k)", size=11, color=INK, anchor="start"))
    frags.append(text(490, b_y + 105, "• Запити розподіляються рівномірно за часом", size=11, color=INK, anchor="start"))
    frags.append(text(490, b_y + 130, "• Базова станція плавно обслуговує чергу", size=11, color=INK, anchor="start"))
    frags.append(text(490, b_y + 160, "Результат: 99.8% пристроїв відновлюють зв'язок", size=11, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT_DIR, "fsm-timing-backoff.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_forward_lifecycle()
    fig_rollback_matrix()
    fig_timing_backoff()
    print("All figures generated successfully.")
