# -*- coding: utf-8 -*-
"""Фігури до теми «Вибори лідера як прикладний патерн»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM   = "#fdecea"   # небезпека / старий зомбі-лідер / відхилення
COOL   = "#eaf0fd"   # клієнти / координатор / нейтральне
GOOD   = "#e8f6ee"   # успіх / активний лідер / валідна дія
ACCENT = "#fff3cd"   # очікування / стендбай / перевірка


# ── 1. Архітектура прикладних виборів лідера через координатор ───────────────
def fig_app_leader_architecture():
    W, H = 1000, 600
    f = []

    # Заголовок зони воркерів
    f.append(rect(30, 20, 940, 210, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
    f.append(fitbox(45, 30, 910, 30, "Кластер екземплярів прикладного сервісу (Stateless Worker Pods)", size=13, bold=True, fill=COOL, stroke=NEG))

    # Три вузли воркерів
    # Вузол 1: Активний лідер
    f.append(rect(50, 70, 280, 145, fill=GOOD, stroke=FIELD, sw=2, rx=6))
    f.append(fitbox(60, 80, 260, 32, "Вузол 1 (АКТИВНИЙ ЛІДЕР)", size=12, bold=True, fill=BG, color=FIELD))
    f.append(fitbox(60, 118, 260, 88, "Стан: LEADER\nУтримує лізу: lease_id=0xFA1\nТокен епохи: epoch=42\nВиконує монопольні фонові задачі", size=11, fill=FILL))

    # Вузол 2: Стендбай-претендент
    f.append(rect(360, 70, 280, 145, fill=ACCENT, stroke=MUTED, sw=1.5, rx=6))
    f.append(fitbox(370, 80, 260, 32, "Вузол 2 (STANDBY / FOLLOWER)", size=12, bold=True, fill=BG, color=INK))
    f.append(fitbox(370, 118, 260, 88, "Стан: CANDIDATE\nОчікує лізу (Watch / Poll)\nЗвичайні HTTP-запити: ТАК\nФонові монопольні задачі: НІ", size=11, fill=FILL))

    # Вузол 3: Стендбай-претендент
    f.append(rect(670, 70, 280, 145, fill=ACCENT, stroke=MUTED, sw=1.5, rx=6))
    f.append(fitbox(680, 80, 260, 32, "Вузол 3 (STANDBY / FOLLOWER)", size=12, bold=True, fill=BG, color=INK))
    f.append(fitbox(680, 118, 260, 88, "Стан: CANDIDATE\nОчікує лізу (Watch / Poll)\nЗвичайні HTTP-запити: ТАК\nФонові монопольні задачі: НІ", size=11, fill=FILL))

    # Середній шар: блок передачі дій
    f.append(fitbox(50, 240, 280, 35, "Keep-Alive серцебиття (3 с)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(190, 215, 190, 240, color=FIELD, sw=2))
    f.append(arrow(190, 275, 190, 300, color=FIELD, sw=2))

    f.append(fitbox(530, 240, 420, 35, "Монопольний запис + Fencing Token (e=42)", size=11.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(290, 215, 600, 240, color=FIELD, sw=2))
    f.append(arrow(740, 275, 740, 300, color=FIELD, sw=2))

    # Нижній шар 1: Розподілений координатор консенсусу
    f.append(rect(30, 300, 450, 135, fill=COOL, stroke=NEG, sw=2, rx=8))
    f.append(fitbox(45, 310, 420, 32, "Зовнішній координатор (etcd / ZooKeeper / K8s Lease)", size=12, bold=True, fill=BG, color=NEG))
    f.append(fitbox(45, 348, 420, 75, "Ключ: /service/leader-lock\nВласник: Вузол 1 | TTL: 10 с | Ревізія епохи: 42\nЗабезпечує лінеаризований консенсус", size=11, fill=FILL))

    # Стендбай-стрілки до координатора
    f.append(arrow(500, 215, 410, 300, color=MUTED, sw=1.5))
    f.append(arrow(810, 215, 460, 300, color=MUTED, sw=1.5))

    # Нижній шар 2: Захищене цільове сховище з перевіркою токена
    f.append(rect(510, 300, 460, 135, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(fitbox(525, 310, 430, 32, "Цільове сховище даних (PostgreSQL / S3 / Kafka)", size=12, bold=True, fill=BG, color=FIELD))
    f.append(fitbox(525, 348, 430, 75, "Таблиця стану: last_fencing_token = 42\nІнваріант: UPDATE ... WHERE token >= last_token\nВідхиляє мутації з токенами e < 42", size=11, fill=FILL))

    # Підсумковий блок переваг патерну
    f.append(rect(30, 455, 940, 125, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(45, 465, 910, 105,
                    "АРХІТЕКТУРНИЙ ПРИНЦИП:\n"
                    "1. Додаток не реалізує складний консенсус усередині кожного контейнера, а делегує вибори лідера координатору.\n"
                    "2. Ліза гарантує автоматичне зняття повноважень при відмові лідера через спливання TTL.\n"
                    "3. Фенсинговий токен (Fencing Token / Epoch) захищає сховище від застарілих дій зомбі-лідера при GC-паузах.",
                    size=11.5, fill=BG))

    render(os.path.join(OUT, 'app-leader-architecture.svg'), W, H, *f)


# ── 2. Часова шкала лізи, GC-паузи та фенсингового токена ────────────────────
def fig_lease_timeline_fencing():
    W, H = 1040, 580
    f = []

    # Часова вісь знизу
    y_t = 510
    f.append(line(80, y_t, 960, y_t, color=LINE, sw=2))
    f.append(arrow(950, y_t, 970, y_t, color=LINE, sw=2))
    f.append(text(980, y_t + 5, "час t", size=12, anchor="start"))

    # Часові позначки
    t1, t2, t3, t4, t5 = 180, 360, 540, 720, 900

    f.append(text(t1, y_t + 22, "t₁ (старт лізи)", size=10.5, color=MUTED))
    f.append(text(t2, y_t + 22, "t₂ (GC-пауза В1)", size=10.5, color=MUTED))
    f.append(text(t3, y_t + 22, "t₃ (TTL вичерпано)", size=10.5, color=MUTED))
    f.append(text(t4, y_t + 22, "t₄ (В2 бере лізу)", size=10.5, color=MUTED))
    f.append(text(t5, y_t + 22, "t₅ (пробудження В1)", size=10.5, color=MUTED))

    # Смуги сутностей
    y_v1 = 90
    y_coord = 200
    y_v2 = 310
    y_db = 420

    f.append(fitbox(20, y_v1 - 18, 110, 36, "Вузол 1 (В1)", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_coord - 18, 110, 36, "Координатор", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_v2 - 18, 110, 36, "Вузол 2 (В2)", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_db - 18, 110, 36, "Сховище (БД)", size=12, bold=True, fill=COOL))

    # Вертикальні лінії для часових точок (не проходять крізь блоки)
    f.append(line(t1, 120, t1, 175, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t1, 230, t1, y_t - 15, color=MUTED, sw=1, dash="4,4"))

    f.append(line(t3, 60, t3, 170, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t3, 235, t3, y_t - 15, color=MUTED, sw=1, dash="4,4"))

    f.append(line(t4, 60, t4, 170, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t4, 235, t4, 280, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t4, 345, t4, 390, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t4, 455, t4, y_t - 15, color=MUTED, sw=1, dash="4,4"))

    f.append(line(t5, 120, t5, 390, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t5, 455, t5, y_t - 15, color=MUTED, sw=1, dash="4,4"))

    # Подія 1: В1 отримує лізу на 10с з токеном e=101
    f.append(fitbox(t1 - 65, y_coord - 22, 130, 44, "Видано лізу В1\nТокен e = 101", size=11, fill=GOOD, stroke=FIELD))
    f.append(arrow(t1, y_coord - 22, t1, y_v1 + 22, color=FIELD, sw=1.5))
    f.append(fitbox(t1 - 65, y_v1 - 25, 130, 44, "Лідер В1 (e=101)\nЗапускає задачі", size=11, fill=GOOD, stroke=FIELD))

    # Подія 2: В1 засинає на GC pause / freeze
    f.append(rect(t2 - 20, y_v1 - 25, 520, 46, fill=WARM, stroke=POS, sw=2, rx=6))
    f.append(fitbox(t2 - 15, y_v1 - 20, 510, 36, "ГЛИБОКА ПАУЗА ЗБИРАЧА СМІТТЯ (GC STW / VM Freeze) — 15 секунд", size=11, bold=True, color=POS, fill=BG))

    # Подія 3: Координатор фіксує таймаут лізи (10с без Keep-Alive)
    f.append(fitbox(t3 - 75, y_coord - 25, 150, 50, "Таймаут TTL!\nЛізу В1 анульовано\nКлюч звільнено", size=11, bold=True, fill=WARM, stroke=POS))

    # Подія 4: В2 виграє вибори і стає лідером з токеном e=102
    f.append(fitbox(t4 - 70, y_coord - 25, 140, 50, "Нова ліза для В2\nТокен e = 102", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(t4, y_coord + 25, t4, y_v2 - 22, color=FIELD, sw=1.5))
    f.append(fitbox(t4 - 70, y_v2 - 22, 140, 44, "Лідер В2 (e=102)\nПрацює штатно", size=11, fill=GOOD, stroke=FIELD))

    # В2 робить запис у БД з токеном 102
    f.append(arrow(t4 + 30, y_v2 + 22, t4 + 30, y_db - 22, color=FIELD, sw=1.8))
    f.append(fitbox(t4 - 40, y_db - 22, 140, 44, "БД: прийнято!\nlast_token = 102", size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Подія 5: В1 прокидається, вважає себе лідером і шле запис зі старим токеном 101
    f.append(fitbox(t5 - 75, y_v1 + 25, 150, 44, "В1 прокинувся!\nШле запис (e=101)", size=11, fill=WARM, stroke=POS))
    f.append(arrow(t5, y_v1 + 69, t5, y_db - 22, color=POS, sw=2))

    # БД відхиляє старий запис В1
    f.append(fitbox(t5 - 80, y_db - 22, 160, 44, "ВІДХИЛЕНО!\n101 < 102 (захист)", size=11, bold=True, color=POS, fill=WARM, stroke=POS))

    render(os.path.join(OUT, 'lease-timeline-fencing.svg'), W, H, *f)


# ── 3. Шторм пробудження проти ланцюгового спостереження (ZooKeeper Recipe) ──
def fig_zookeeper_watcher_chain():
    W, H = 1000, 520
    f = []

    # Ліва половина: Наївний підхід (Thundering Herd)
    f.append(rect(30, 25, 450, 465, fill=WARM, stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(45, 35, 420, 36, "НАЇВНИЙ ПІДХІД: Шторм пробудження (Thundering Herd)", size=12, bold=True, color=POS, fill=BG))

    f.append(fitbox(155, 90, 200, 45, "Єдиний ключ: /app/leader\nВласник: Вузол 1", size=11.5, bold=True, fill=GOOD, stroke=FIELD))

    # N-1 воркерів слухають один ключ
    for i, (name, y_pos) in enumerate([("Вузол 2 (Watch)", 180), ("Вузол 3 (Watch)", 245), ("Вузол N (Watch)", 310)]):
        f.append(fitbox(70, y_pos, 140, 36, name, size=11, fill=COOL))
        f.append(arrow(210, y_pos + 18, 250, 135, color=POS, sw=1.5))

    f.append(fitbox(45, 370, 420, 105,
                    "НАСЛІДОК ПАДІННЯ ЛІДЕРА:\n"
                    "• Координатор одночасно надсилає N-1 сповіщень.\n"
                    "• Усі N-1 вузлів миттєво шлють запити на створення ключа.\n"
                    "• Складність: O(N) сповіщень, O(N²) навантаження на мережу.\n"
                    "• Ризик колапсу координатора при великих кластерах.",
                    size=11, color=POS, fill=BG))

    # Права половина: Елегантний ланцюжок (ZooKeeper / Sequential Chain)
    f.append(rect(510, 25, 460, 465, fill=GOOD, stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(525, 35, 430, 36, "ОПТИМАЛЬНИЙ ПАТЕРН: Ланцюг послідовних вузлів", size=12, bold=True, color=FIELD, fill=BG))

    # Послідовні вузли
    f.append(fitbox(535, 95, 190, 42, "/election/node_001 (ЛІДЕР)\nНайменший номер -> Вузол 1", size=10.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 165, 190, 42, "/election/node_002 (STANDBY)\nВузол 2", size=10.5, fill=COOL))
    f.append(fitbox(535, 235, 190, 42, "/election/node_003 (STANDBY)\nВузол 3", size=10.5, fill=COOL))
    f.append(fitbox(535, 305, 190, 42, "/election/node_004 (STANDBY)\nВузол 4", size=10.5, fill=COOL))

    # Ланцюжок Watch (кожен слухає лише попередника)
    f.append(arrow(725, 186, 725, 137, color=FIELD, sw=2))
    f.append(fitbox(740, 145, 200, 30, "Watch: ТІЛЬКИ node_001", size=10.5, bold=True, fill=BG, color=FIELD))

    f.append(arrow(725, 256, 725, 207, color=FIELD, sw=2))
    f.append(fitbox(740, 215, 200, 30, "Watch: ТІЛЬКИ node_002", size=10.5, bold=True, fill=BG, color=FIELD))

    f.append(arrow(725, 326, 725, 277, color=FIELD, sw=2))
    f.append(fitbox(740, 285, 200, 30, "Watch: ТІЛЬКИ node_003", size=10.5, bold=True, fill=BG, color=FIELD))

    f.append(fitbox(525, 370, 430, 105,
                    "ПЕРЕВАГА ЛАНЦЮГОВОГО СПОСТЕРЕЖЕННЯ:\n"
                    "• При падінні лідера (node_001) прокидається РІВНО ОДИН вузол (node_002).\n"
                    "• При падінні проміжного вузла прокидається лише його наступник.\n"
                    "• Складність: строго O(1) подій на подію відмови.\n"
                    "• Ідеальне масштабування на сотні й тисячі вузлів.",
                    size=11, color=FIELD, fill=BG))

    render(os.path.join(OUT, 'zookeeper-watcher-chain.svg'), W, H, *f)


if __name__ == '__main__':
    fig_app_leader_architecture()
    fig_lease_timeline_fencing()
    fig_zookeeper_watcher_chain()
    print("Усі фігури згенеровано успішно.")
