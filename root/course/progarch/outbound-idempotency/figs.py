# -*- coding: utf-8 -*-
"""Фігури до кроку «Ідемпотентність вихідної розмови»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

A_FILL = "#dfe9fb"
B_FILL = "#eafaf0"
GRAY_FILL = "#f0f0f2"
RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
AMBER_FILL = "#fff8e6"

def fig_timeout_dilemma():
    """Дилема мережевого таймауту при вихідному HTTP POST: 3 різні точки відмови виглядають однаково."""
    W, H = 1040, 520
    frags = []

    # Хедер
    frags.append(text(W / 2, 40, "Дилема вихідного таймауту: однакова симптоматика трьох різних станів", size=16, bold=True, color=INK))

    # Стовпчик 1: Відправник (DH Gateway)
    t1 = fitbox(60, 100, 220, 70, "Відправник (DH)\nPOST /v1/charges", size=14, bold=True, fill=A_FILL, stroke=FIELD)

    # Стовпчик 2: Мережа (3 варіанти відмови)
    frags.append(text(520, 90, "Мережева межа (HTTP / TCP)", size=13, bold=True, color=MUTED))

    # Варіант 1: Запит втрачено
    t_c1 = fitbox(360, 130, 320, 60, "1. Втрата запиту (Request Loss)\nПровайдер НЕ побачив виклику", size=12, fill=GRAY_FILL, stroke=MUTED)
    # Варіант 2: Виконано на сервері
    t_c2 = fitbox(360, 220, 320, 60, "2. Успіх на провайдері (Execution)\nПлатіж проведено, гроші знято", size=12, fill=AMBER_FILL, stroke=MUTED)
    # Варіант 3: Відповідь втрачено
    t_c3 = fitbox(360, 310, 320, 60, "3. Втрата відповіді (Response Loss)\n200 OK зник під час збігу мережі", size=12, fill=RED_FILL, stroke=NEG)

    # Стовпчик 3: Отримувач (Платіжний провайдер)
    t2 = fitbox(760, 100, 220, 70, "Провайдер (Stripe)\nОбробка платежу", size=14, bold=True, fill=B_FILL, stroke=POS)

    # Зв'язки
    frags.append(line(280, 160, 360, 160, color=MUTED, sw=2, dash="4,4"))
    frags.append(line(280, 250, 360, 250, color=INK, sw=2))
    frags.append(line(280, 340, 360, 340, color=NEG, sw=2))

    frags.append(line(680, 160, 760, 160, color=MUTED, sw=2, dash="4,4"))
    frags.append(line(680, 250, 760, 250, color=POS, sw=2))
    frags.append(line(680, 340, 760, 340, color=NEG, sw=2, dash="4,4"))

    # Висновок відправника
    bot_box = fitbox(140, 410, 760, 70, "Результат для відправника: Timeout (504 / ECONNRESET)\nБез Idempotency-Key: Сліпий повтор → Подвійне списання! | Відмова → Неоплачене замовлення!", size=13, bold=True, fill=RED_FILL, stroke=NEG)

    frags.extend([t1, t2, t_c1, t_c2, t_c3, bot_box])

    render(os.path.join(IMG, "outbound-timeout-dilemma.svg"), W, H, *frags, title="Дилема мережевого таймауту")

def fig_idempotency_lifecycle():
    """Сценарій роботи Idempotency-Key на боці зовнішнього провайдера."""
    W, H = 1060, 480
    frags = []

    frags.append(text(W / 2, 35, "Життєвий цикл ключа ідемпотентності на боці провайдера API", size=16, bold=True, color=INK))

    b_in = fitbox(50, 100, 180, 65, "Вхідний HTTP POST\nIdempotency-Key: k_991", size=13, bold=True, fill=A_FILL, stroke=FIELD)

    # Перевірка в кеші
    b_chk = fitbox(270, 100, 170, 65, "Перевірка Key Store\n(Redis / DB)", size=13, bold=True, fill=GRAY_FILL, stroke=MUTED)

    # Гілка 1: Новий ключ
    b_new = fitbox(500, 90, 240, 65, "Ключ відсутній\nЗапис стану IN_FLIGHT\nВиконання бізнес-логіки", size=12, fill=B_FILL, stroke=POS)
    b_res = fitbox(790, 90, 210, 65, "Збереження HTTP 200\nBody + Headers\nПовернення 200 OK", size=12, fill=B_FILL, stroke=POS)

    # Гілка 2: Повторний ключ (Виконано)
    b_dup = fitbox(500, 210, 240, 65, "Ключ знайдено: COMPLETED\nЗвірка Payload Fingerprint", size=12, fill=AMBER_FILL, stroke=MUTED)
    b_replay = fitbox(790, 210, 210, 65, "Відтворення кешованої\nвідповіді 200 OK\n(Без нової дії)", size=12, fill=AMBER_FILL, stroke=MUTED)

    # Гілка 3: Конфлікт або In-Flight
    b_inflight = fitbox(500, 330, 240, 65, "Ключ знайдено: IN_FLIGHT\n(Попередній виклик триває)", size=12, fill=RED_FILL, stroke=NEG)
    b_err = fitbox(790, 330, 210, 65, "Повернення 409 Conflict\n/ 422 Payload Mismatch", size=12, fill=RED_FILL, stroke=NEG)

    # Лінії
    frags.append(line(230, 132, 270, 132, color=INK, sw=2))
    frags.append(line(440, 122, 500, 122, color=POS, sw=2))
    frags.append(line(740, 122, 790, 122, color=POS, sw=2))

    # До гілки 2
    frags.append(line(460, 132, 460, 242, color=MUTED, sw=2))
    frags.append(line(460, 242, 500, 242, color=MUTED, sw=2))
    frags.append(line(740, 242, 790, 242, color=MUTED, sw=2))

    # До гілки 3
    frags.append(line(460, 242, 460, 362, color=NEG, sw=2))
    frags.append(line(460, 362, 500, 362, color=NEG, sw=2))
    frags.append(line(740, 362, 790, 362, color=NEG, sw=2))

    frags.extend([b_in, b_chk, b_new, b_res, b_dup, b_replay, b_inflight, b_err])

    render(os.path.join(IMG, "idempotency-key-lifecycle.svg"), W, H, *frags, title="Життєвий цикл ключа ідемпотентності")

def fig_gateway_architecture():
    """Архітектура вихідного ідемпотентного шлюзу на боці клієнта."""
    W, H = 1040, 460
    frags = []

    frags.append(text(W / 2, 35, "Архітектура вихідного шлюзу: від локальної БД до зовнішнього API", size=16, bold=True, color=INK))

    box1 = fitbox(40, 120, 260, 110, "Доменний сервіс (DH)\n1. Відкрити DB Tx\n2. Зберегти замовлення\n3. Створити Outbox-подію\n+ deterministic idempotency_key", size=12, fill=A_FILL, stroke=FIELD)

    box2 = fitbox(360, 120, 310, 110, "Outbound Gateway Worker\n1. Прочитати Outbox\n2. HTTP POST з Idempotency-Key\n3. Обробка таймаутів / 5xx\n4. Авто-повтор (Exponential Backoff)", size=12, fill=AMBER_FILL, stroke=MUTED)

    box3 = fitbox(740, 120, 250, 110, "Зовнішнє API (Stripe/Push)\n1. Перевірка Idempotency-Key\n2. Виконання або Replay\n3. Повернення 200 OK", size=12, fill=B_FILL, stroke=POS)

    # Зв'язки
    frags.append(line(300, 175, 360, 175, color=INK, sw=2))
    frags.append(line(670, 175, 740, 175, color=POS, sw=2))

    # Нижній шар: Гарантії
    bot1 = fitbox(80, 310, 400, 75, "Локальна межа консистентності:\nЗапис стану і дедуп-ключа атомарний з БД", size=12, fill=GRAY_FILL, stroke=MUTED)

    bot2 = fitbox(560, 310, 400, 75, "Мережева межа стійкості:\nБезпечний ретрай при збоях мережі без дублів", size=12, fill=GREEN_FILL, stroke=POS)

    frags.extend([box1, box2, box3, bot1, bot2])

    render(os.path.join(IMG, "outbound-gateway-architecture.svg"), W, H, *frags, title="Архітектура вихідного шлюзу")

def main():
    fig_timeout_dilemma()
    fig_idempotency_lifecycle()
    fig_gateway_architecture()
    print("Figures generated successfully.")

if __name__ == "__main__":
    main()
