# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'SWIM / Gossip членство кластера'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_swim_detection_cycle():
    """Фігура 1: Цикл виявлення збоїв SWIM — прямий зонд та непрямий ping-req."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Двофазний цикл виявлення збоїв у протоколі SWIM", size=16, bold=True))

    # Ліва колонка: Фаза 1 — Прямий зонд (Direct Ping)
    frags.append(rect(20, 50, 405, 345, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(222, 76, "Фаза 1: Пряме зондування (Direct Ping)", size=13, bold=True, color=INK))

    # Вузли Фази 1
    # Node A (Probe)
    frags.append(circle(90, 160, 26, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(90, 156, "Вузол A", size=11, bold=True, color=NEG))
    frags.append(text(90, 170, "(ініціатор)", size=9.5, color=MUTED))

    # Node B (Target)
    frags.append(circle(340, 160, 26, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(340, 156, "Вузол B", size=11, bold=True, color=POS))
    frags.append(text(340, 170, "(ціль)", size=9.5, color=MUTED))

    # Стрілка Ping ->
    frags.append(arrow(120, 145, 308, 145, color=NEG, sw=1.8))
    frags.append(text(215, 137, "1. Прямий Ping (UDP)", size=10, bold=True, color=NEG))

    # Перекреслена стрілка відхиленого або втраченого Ack <-
    frags.append(line(308, 175, 120, 175, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(215, 192, "Ack втрачено або B перевантажений", size=9.5, bold=True, color=POS))
    frags.append(line(205, 168, 225, 182, color=POS, sw=2))
    frags.append(line(225, 168, 205, 182, color=POS, sw=2))

    # Пояснення внизу фази 1
    frags.append(rect(35, 245, 375, 135, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(222, 268, "Таймаут прямого зонду T_ack сплив", size=11, bold=True, color=POS))
    frags.append(text(222, 290, "• Відсутність Ack не означає смерть B", size=10, color=INK))
    frags.append(text(222, 308, "• Причина: локальна втрата пакетів на маршруті A-B", size=10, color=MUTED))
    frags.append(text(222, 326, "• Вузол B може бути повністю здоровим", size=10, color=MUTED))
    frags.append(text(222, 344, "• Рішення: непряма перевірка через посередників", size=10, bold=True, color=FIELD))

    # Права колонка: Фаза 2 — Непряме зондування (Indirect Ping-Req)
    frags.append(rect(445, 50, 415, 345, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(652, 76, "Фаза 2: Непрямий запит (Indirect Ping-Req)", size=13, bold=True, color=INK))

    # Вузли Фази 2: A, C1, C2, B
    frags.append(circle(495, 200, 24, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(495, 204, "Вузол A", size=10, bold=True, color=NEG))

    frags.append(circle(650, 125, 22, fill="#f0fdf4", stroke=FIELD, sw=1.8))
    frags.append(text(650, 129, "Посер. C₁", size=9.5, bold=True, color=FIELD))

    frags.append(circle(650, 275, 22, fill="#f0fdf4", stroke=FIELD, sw=1.8))
    frags.append(text(650, 279, "Посер. C₂", size=9.5, bold=True, color=FIELD))

    frags.append(circle(805, 200, 24, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(805, 204, "Вузол B", size=10, bold=True, color=POS))

    # Маршрут A -> C1 -> B -> C1 -> A
    frags.append(arrow(517, 185, 628, 137, color=FIELD, sw=1.4))
    frags.append(text(555, 150, "ping-req(B)", size=9.5, bold=True, color=FIELD))

    frags.append(arrow(672, 135, 783, 187, color=FIELD, sw=1.4))
    frags.append(text(745, 150, "ping", size=9.5, bold=True, color=FIELD))

    frags.append(arrow(783, 195, 672, 145, color=FIELD, sw=1.2))
    frags.append(arrow(628, 145, 517, 195, color=FIELD, sw=1.2))
    frags.append(text(595, 175, "ack (успіх)", size=9.5, bold=True, color=FIELD))

    # Маршрут A -> C2 -> B (альтернативний)
    frags.append(arrow(517, 215, 628, 263, color=MUTED, sw=1.4))
    frags.append(text(555, 255, "ping-req(B)", size=9.5, color=MUTED))

    frags.append(arrow(672, 265, 783, 213, color=MUTED, sw=1.4))

    # Висновок правої секції
    frags.append(rect(460, 315, 385, 65, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(652, 335, "Якщо бодай один посередник C отримав Ack від B:", size=10, bold=True, color=FIELD))
    frags.append(text(652, 352, "• Вузол B вважається здоровим (Alive)", size=10, color=INK))
    frags.append(text(652, 368, "• Якщо жоден не відповів за T_ping → перехід у Suspect", size=10, bold=True, color=POS))

    render(os.path.join(OUT, "swim-detection-cycle.svg"), w, h, *frags)


def fig_swim_state_machine():
    """Фігура 2: Скінченний автомат станів вузла та правила зміни інкарнацій."""
    w, h = 860, 380
    frags = []

    frags.append(text(w / 2, 28, "Скінченний автомат станів членства в SWIM / Serf", size=16, bold=True))

    # Стан 1: ALIVE (Здоровий)
    frags.append(rect(50, 120, 180, 110, fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    frags.append(text(140, 150, "ALIVE", size=16, bold=True, color=FIELD))
    frags.append(text(140, 172, "Вузол доступний", size=11, color=INK))
    frags.append(text(140, 190, "Інкарнація: i", size=11, bold=True, color=MUTED))
    frags.append(text(140, 210, "Бере участь у трафіку", size=9.5, color=MUTED))

    # Стан 2: SUSPECT (Підозрілий)
    frags.append(rect(340, 120, 180, 110, fill="#fefce8", stroke="#ca8a04", sw=2, rx=10))
    frags.append(text(430, 150, "SUSPECT", size=16, bold=True, color="#ca8a04"))
    frags.append(text(430, 172, "Зонди провалено", size=11, color=INK))
    frags.append(text(430, 190, "Таймер T_suspect запущено", size=10, bold=True, color="#b45309"))
    frags.append(text(430, 210, "Очікує спростування", size=9.5, color=MUTED))

    # Стан 3: DEAD (Мертвий)
    frags.append(rect(630, 120, 180, 110, fill="#fdecea", stroke=POS, sw=2, rx=10))
    frags.append(text(720, 150, "DEAD", size=16, bold=True, color=POS))
    frags.append(text(720, 172, "Таймаут вичерпано", size=11, color=INK))
    frags.append(text(720, 190, "Інкарнація: i", size=11, bold=True, color=MUTED))
    frags.append(text(720, 210, "Видаляється з кластера", size=9.5, color=MUTED))

    # Перехід 1: Alive -> Suspect (Провал прямих і непрямих зондів)
    frags.append(arrow(230, 155, 340, 155, color="#ca8a04", sw=2))
    frags.append(text(285, 142, "Провал ping-req", size=9.5, bold=True, color="#ca8a04"))

    # Перехід 2: Suspect -> Alive (Спростування підозри: Refutation)
    # Зворотна лінія знизу
    frags.append(line(355, 230, 310, 270, color=FIELD, sw=2))
    frags.append(line(310, 270, 250, 270, color=FIELD, sw=2))
    frags.append(arrow(250, 270, 210, 230, color=FIELD, sw=2))
    frags.append(text(285, 290, "Спростування (Refutation):", size=10, bold=True, color=FIELD))
    frags.append(text(285, 305, "Повідомлення Alive(i + 1)", size=10, bold=True, color=FIELD))

    # Перехід 3: Suspect -> Dead (Спливання таймауту T_suspect)
    frags.append(arrow(520, 175, 630, 175, color=POS, sw=2))
    frags.append(text(575, 162, "T_suspect сплив", size=10, bold=True, color=POS))

    # Стан LEFT (Добровільний вихід) зверху
    frags.append(rect(340, 20, 180, 55, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(430, 42, "LEFT (Вийшов)", size=13, bold=True, color="#475569"))
    frags.append(text(430, 60, "Коректний shutdown", size=9.5, color=MUTED))

    frags.append(line(150, 120, 340, 50, color="#475569", sw=1.5, dash="3,3"))
    frags.append(text(225, 75, "Повідомлення Leave", size=9.5, bold=True, color="#475569"))

    # Нижній блок: Пріоритет станів при однаковій інкарнації
    frags.append(rect(120, 335, 620, 35, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(430, 357, "Пріоритет станів (однакова інкарнація i):  DEAD > SUSPECT > ALIVE", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "swim-state-machine.svg"), w, h, *frags)


def fig_lifeguard_lhm():
    """Фігура 3: Механізм Lifeguard — Local Health Multiplier та динамічні таймаути."""
    w, h = 880, 410
    frags = []

    frags.append(text(w / 2, 28, "Lifeguard: Захист від помилкових підозр при деградації вузла", size=16, bold=True))

    # Ліва секція: Локальний множник здоров'я (LHM)
    frags.append(rect(20, 55, 410, 335, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 82, "1. Самооцінка вузла (Local Health Multiplier)", size=13, bold=True, color=INK))

    frags.append(circle(90, 160, 30, fill="#fefce8", stroke="#ca8a04", sw=2))
    frags.append(text(90, 156, "Вузол", size=12, bold=True, color=INK))
    frags.append(text(90, 172, "LHM = 0..8", size=10, bold=True, color="#b45309"))

    # Події, що підвищують/знижують LHM
    frags.append(rect(145, 115, 270, 95, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(280, 135, "Динаміка шкали LHM:", size=11, bold=True, color=INK))
    frags.append(text(280, 153, "• Провал власного зонду → LHM + 1", size=10, color=POS))
    frags.append(text(280, 171, "• Отримано підозру на себе → LHM + 1", size=10, color=POS))
    frags.append(text(280, 189, "• Успішний раунд зондування → LHM - 1", size=10, color=FIELD))

    frags.append(rect(35, 230, 380, 145, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(225, 252, "Адаптація поведінки вузла при LHM > 0:", size=11, bold=True, color="#b45309"))
    frags.append(text(225, 275, "1. Зонд-пауза (Probe Pause): уповільнення пінгу", size=10, color=INK))
    frags.append(text(225, 295, "2. Подовження T_ack: захист від затримок GC/CPU", size=10, color=INK))
    frags.append(text(225, 315, "3. Збільшення вікна спростування T_suspect", size=10, color=INK))
    frags.append(text(225, 345, "Вузол усвідомлює власне гальмування і не 'карає' сусідів", size=9.5, bold=True, color=FIELD))

    # Права секція: Динамічне скорочення підозри (Dogpiling)
    frags.append(rect(450, 55, 410, 335, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 82, "2. Консенсус підозр (Dogpiling / Corroboration)", size=13, bold=True, color=INK))

    # Шкала скорочення часу
    frags.append(rect(470, 115, 370, 80, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(655, 138, "Кількість незалежних підтверджень C:", size=11, bold=True, color=INK))
    frags.append(text(655, 160, "C = 0 підтверджень  →  T_suspect = T_max (макс. шанс)", size=9.5, color=MUTED))
    frags.append(text(655, 180, "C ≥ K підтверджень  →  T_suspect = T_min (швидкий крах)", size=9.5, bold=True, color=POS))

    # Візуалізація таймера
    frags.append(rect(470, 215, 370, 45, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    frags.append(rect(470, 215, 145, 45, fill="#fca5a5", stroke=POS, sw=1.5, rx=4))
    frags.append(text(542, 242, "T_min (C=K)", size=11, bold=True, color=POS))
    frags.append(text(735, 242, "Повне вікно T_max (C=0)", size=11, bold=True, color="#475569"))

    frags.append(rect(470, 280, 370, 95, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(655, 302, "Формула динамічного таймауту:", size=11, bold=True, color=INK))
    frags.append(text(655, 325, "T = T_max - (T_max - T_min) · [log(C+1) / log(K+1)]", size=10, bold=True, color=NEG))
    frags.append(text(655, 352, "Чим більше підтверджень, тим швидше вузол позначається Dead", size=9.5, color=MUTED))

    render(os.path.join(OUT, "lifeguard-lhm.svg"), w, h, *frags)


def fig_piggybacked_packet_structure():
    """Фігура 4: Структура двійкового дейтаграмного пакету з 'наїздом' пліток (piggybacking)."""
    w, h = 880, 360
    frags = []

    frags.append(text(w / 2, 28, "Двійковий макет дейтаграми SWIM: Зонд + Буфер пліток (Piggybacking)", size=16, bold=True))

    # Загальний контейнер UDP
    frags.append(rect(30, 55, 820, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 78, "UDP Datagram Payload (< MTU 1400 байтів)", size=12, bold=True, color="#475569"))

    # Блок 1: Заголовок зонда (Probe Message Header)
    frags.append(rect(50, 100, 245, 150, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    frags.append(text(172, 125, "1. Заголовок зонду", size=13, bold=True, color=NEG))
    frags.append(text(172, 145, "Тип: PING / PING-REQ / ACK", size=10, bold=True, color=INK))
    frags.append(text(172, 168, "SeqNo: 8 байтів (uint64)", size=10, color=MUTED))
    frags.append(text(172, 190, "Target: IP:Port цілі (6 байтів)", size=10, color=MUTED))
    frags.append(text(172, 212, "LHM / Прапорці (2 байти)", size=10, color=MUTED))
    frags.append(text(172, 235, "Розмір: ~18-24 байти", size=9.5, bold=True, color=NEG))

    # Плюс між блоками
    frags.append(text(310, 175, "+", size=24, bold=True, color=LINE))

    # Блок 2: Масив пліток членства (Piggybacked Membership Updates)
    frags.append(rect(330, 100, 500, 150, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    frags.append(text(580, 125, "2. Буфер подій членства (Piggybacked Gossip Updates)", size=13, bold=True, color=FIELD))

    # Окремі елементи пліток всередині
    frags.append(rect(348, 145, 145, 90, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(420, 165, "Подія 1: ALIVE", size=10, bold=True, color=FIELD))
    frags.append(text(420, 185, "Node ID: 10.0.1.5", size=9.5, color=INK))
    frags.append(text(420, 202, "Incarnation: 4", size=9.5, color=MUTED))
    frags.append(text(420, 220, "Retransmit: 2", size=9.5, color=MUTED))

    frags.append(rect(508, 145, 145, 90, fill="#ffffff", stroke="#ca8a04", sw=1, rx=4))
    frags.append(text(580, 165, "Подія 2: SUSPECT", size=10, bold=True, color="#b45309"))
    frags.append(text(580, 185, "Node ID: 10.0.2.8", size=9.5, color=INK))
    frags.append(text(580, 202, "Incarnation: 1", size=9.5, color=MUTED))
    frags.append(text(580, 220, "Retransmit: 1", size=9.5, color=MUTED))

    frags.append(rect(668, 145, 150, 90, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(743, 165, "Подія 3: DEAD / USER", size=10, bold=True, color=POS))
    frags.append(text(743, 185, "Node ID: 10.0.0.99", size=9.5, color=INK))
    frags.append(text(743, 202, "Incarnation: 2", size=9.5, color=MUTED))
    frags.append(text(743, 220, "Retransmit: 0", size=9.5, color=MUTED))

    # Підсумковий рядок внизу
    frags.append(rect(50, 265, 780, 55, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(440, 287, "Нульовий оверхед на окремі пакети: розповсюдження подій 'безкоштовно' їде на службових зондах", size=11, bold=True, color=FIELD))
    frags.append(text(440, 306, "Кожна подія передається λ · log(N) разів для гарантії епідемічного охоплення O(1) мережевого навантаження", size=10, color=MUTED))

    render(os.path.join(OUT, "piggybacked-packet-structure.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_swim_detection_cycle()
    fig_swim_state_machine()
    fig_lifeguard_lhm()
    fig_piggybacked_packet_structure()
    print("Всі фігури згенеровано успішно.")
