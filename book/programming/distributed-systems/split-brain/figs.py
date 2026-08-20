# -*- coding: utf-8 -*-
"""Фігури до теми «Failover і розщеплення мозку»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / аварія / розщеплення
COOL = "#eaf0fd"   # нейтральне / клієнти / мережа
GOOD = "#e8f6ee"   # успіх / кворум / захист
ACCENT = "#fff3cd" # попередження / перевірка


# ── 1. Розщеплення кластера на дві ізольовані частини ──────────────────────
def fig_split_brain_partition():
    W, H = 960, 520
    f = []

    # Заголовок та фонові зони
    f.append(fitbox(40, 25, 410, 46, "Дата-центр А (Київ)\nІзольована половина", size=13, bold=True, fill=COOL))
    f.append(fitbox(510, 25, 410, 46, "Дата-центр Б (Львів)\nІзольована половина", size=13, bold=True, fill=COOL))

    # Зона розділення (червона смуга аварії)
    f.append(rect(460, 85, 40, 360, fill=WARM, stroke=POS, sw=1.5, rx=4))
    f.append(line(480, 95, 480, 435, color=POS, sw=2, dash="5,4"))
    f.append(fitbox(462, 220, 36, 90, "ОБРИВ\nЗВ'ЯЗКУ", size=11, bold=True, color=POS, fill=BG, stroke=POS))

    # Ліва сторона: Вузол 1
    f.append(rect(60, 95, 370, 150, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(fitbox(80, 110, 330, 40, "Вузол 1 (Старий Primary)\n«Я живий, клієнти пишуть, зв'язок є»", size=12, bold=True, fill=BG))
    f.append(fitbox(80, 160, 330, 65, "Приймає транзакцію TX-101:\nБаланс рахунку A: 1000 -> 600 грн\nЖурнал WAL: запис у позицію #450", size=11.5, fill=FILL))

    # Клієнти зліва
    f.append(fitbox(60, 280, 370, 55, "Клієнти зони А (мобільні додатки)\nШлють HTTP POST /pay -> Вузол 1", size=12, fill=COOL))
    f.append(arrow(245, 280, 245, 250, color=LINE, sw=1.8))

    # Права сторона: Вузол 2
    f.append(rect(530, 95, 370, 150, fill=WARM, stroke=POS, sw=2, rx=8))
    f.append(fitbox(550, 110, 330, 40, "Вузол 2 (Новий Primary після failover)\n«Вузол 1 мовчить >5 с -> оголошую себе лідером»", size=12, bold=True, fill=BG, color=POS))
    f.append(fitbox(550, 160, 330, 65, "Приймає транзакцію TX-102:\nБаланс рахунку A: 1000 -> 300 грн\nЖурнал WAL: запис у позицію #450", size=11.5, fill=FILL))

    # Клієнти справа
    f.append(fitbox(530, 280, 370, 55, "Клієнти зони Б (веб-портал)\nШлють HTTP POST /withdraw -> Вузол 2", size=12, fill=COOL))
    f.append(arrow(715, 280, 715, 250, color=LINE, sw=1.8))

    # Підсумковий блок катастрофи
    f.append(rect(60, 370, 840, 115, fill=WARM, stroke=POS, sw=2, rx=8))
    f.append(fitbox(80, 385, 800, 85,
                    "КАТАСТРОФА РОЗХОДЖЕННЯ ДАНИХ (SPLIT-BRAIN):\n"
                    "Обидва сервери незалежно змінили один і той самий рахунок, присвоївши конфліктні стани.\n"
                    "Після відновлення оптичного лінка автоматичне об'єднання неможливе: історія роздвоїлася,\n"
                    "транзакційні журнали взаємно суперечать один одному, дані пошкоджено.",
                    size=12, bold=True, color=POS, fill=BG))

    render(os.path.join(OUT, 'split-brain-partition.svg'), W, H, *f)


# ── 2. Часова шкала фенсингового токена (Epoch / Generation) ───────────────
def fig_fencing_token_timeline():
    W, H = 1000, 560
    f = []

    # Часова шкала
    y_t = 500
    f.append(line(80, y_t, 920, y_t, color=LINE, sw=2))
    f.append(arrow(910, y_t, 930, y_t, color=LINE, sw=2))
    f.append(text(935, y_t + 5, "час t", size=12, anchor="start"))

    # Стовпці етапів
    t1, t2, t3, t4 = 180, 400, 620, 840

    f.append(line(t1, 60, t1, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t2, 60, t2, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t3, 60, t3, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t4, 60, t4, y_t - 20, color=MUTED, sw=1, dash="4,4"))

    # Рівні сутностей: Лідер 1, Координатор, Лідер 2, Сховище
    y_L1 = 90
    y_Coord = 180
    y_L2 = 270
    y_Store = 380

    f.append(fitbox(20, y_L1 - 18, 110, 36, "Лідер 1", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_Coord - 18, 110, 36, "Координатор", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_L2 - 18, 110, 36, "Лідер 2", size=12, bold=True, fill=COOL))
    f.append(fitbox(20, y_Store - 18, 110, 36, "Сховище даних", size=12, bold=True, fill=COOL))

    # Етап 1: Лідер 1 отримує токен 41 і зависає (GC pause)
    f.append(fitbox(t1 - 70, y_L1 - 25, 140, 50, "Отримує токен e=41\nЗависає на GC pause", size=11, fill=ACCENT, stroke=POS))
    f.append(arrow(t1, y_Coord - 20, t1, y_L1 + 25, color=FIELD, sw=1.5))

    # Етап 2: Таймаут серцебиття -> Координатор обирає Лідера 2 з токеном 42
    f.append(fitbox(t2 - 75, y_Coord - 25, 150, 50, "Таймаут Л1!\nВибори: токен e=42 -> Л2", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(arrow(t2, y_Coord + 20, t2, y_L2 - 25, color=FIELD, sw=1.5))

    # Етап 3: Лідер 2 записує дані в сховище з токеном 42
    f.append(fitbox(t3 - 75, y_L2 - 25, 150, 50, "Запис у сховище\nз токеном e=42", size=11, fill=GOOD, stroke=FIELD))
    f.append(arrow(t3, y_L2 + 25, t3, y_Store - 25, color=FIELD, sw=1.8))
    f.append(fitbox(t3 - 80, y_Store - 25, 160, 50, "max_token = 42\nЗапис ПРИЙНЯТО ✓", size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Етап 4: Лідер 1 прокидається і шле старий запис з токеном 41
    f.append(fitbox(t4 - 80, y_L1 - 25, 160, 50, "Прокинувся від GC!\nШле старий запис e=41", size=11, fill=WARM, stroke=POS))
    f.append(arrow(t4, y_L1 + 25, t4, y_Store - 25, color=POS, sw=1.8))
    f.append(fitbox(t4 - 85, y_Store - 25, 170, 50, "41 < max_token (42)\nВІДХИЛЕНО (Fenced) ✗", size=11, bold=True, color=POS, fill=WARM, stroke=POS))

    # Пояснення знизу
    f.append(fitbox(140, y_t - 55, 780, 36, "Монотонний токен e гарантує: запізнілий лідер не може пошкодити стан сховища, навіть якщо вважає себе живим", size=11.5, fill=BG))

    render(os.path.join(OUT, 'fencing-token-timeline.svg'), W, H, *f)


# ── 3. Матриця кворумів: чому парна кількість вузлів не додає стійкості ───
def fig_quorum_split_matrix():
    W, H = 980, 500
    f = []

    f.append(fitbox(40, 20, 900, 42, "Матриця розділення кластера: перетин більшостей і правило N/2 + 1", size=13, bold=True, fill=COOL))

    # Рядок 1: Кластер із 3 вузлів
    y1 = 80
    f.append(rect(40, y1, 900, 115, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(fitbox(55, y1 + 15, 180, 85, "Кластер із 3 вузлів\nКворум: 2 із 3\n(Q >= 2)", size=12, bold=True, fill=BG))

    f.append(fitbox(260, y1 + 15, 300, 85, "Розділення мережі [2] та [1]:\nЧастина із 2 вузлів має кворум (2 >= 2) ✓\nЧастина із 1 вузла блокує записи (1 < 2) ✗", size=11.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(580, y1 + 15, 340, 85, "Результат:\nРобота триває без розщеплення.\nВитримує відмову f = 1 вузла.", size=11.5, fill=BG))

    # Рядок 2: Кластер із 4 вузлів (парна пастка!)
    y2 = 210
    f.append(rect(40, y2, 900, 115, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(fitbox(55, y2 + 15, 180, 85, "Кластер із 4 вузлів\nКворум: 3 із 4\n(Q >= 3)", size=12, bold=True, fill=BG, color=POS))

    f.append(fitbox(260, y2 + 15, 300, 85, "Симетричний розрив [2] та [2]:\nПерша половина: 2 < 3 (немає кворуму) ✗\nДруга половина: 2 < 3 (немає кворуму) ✗", size=11.5, fill=WARM, stroke=POS))
    f.append(fitbox(580, y2 + 15, 340, 85, "Результат:\nПовна зупинка кластера (Deadlock).\n4 вузли витримують лише f = 1 відмову!", size=11.5, fill=BG, color=POS))

    # Рядок 3: Кластер із 5 вузлів
    y3 = 340
    f.append(rect(40, y3, 900, 115, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(fitbox(55, y3 + 15, 180, 85, "Кластер із 5 вузлів\nКворум: 3 із 5\n(Q >= 3)", size=12, bold=True, fill=BG))

    f.append(fitbox(260, y3 + 15, 300, 85, "Розділення мережі [3] та [2]:\nБільшість із 3 вузлів продовжує роботу ✓\nМеншість із 2 вузлів чекає зв'язку ✗", size=11.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(580, y3 + 15, 340, 85, "Результат:\nСтійкість до f = 2 одночасних відмов.\nНайкращий баланс надійності та ціни.", size=11.5, fill=BG))

    render(os.path.join(OUT, 'quorum-split-matrix.svg'), W, H, *f)


# ── 4. Апаратний фенсинг (STONITH) проти логічного фенсингу ───────────────
def fig_stonith_vs_tokens():
    W, H = 960, 520
    f = []

    # Колонка 1: STONITH (Апаратне відсікання)
    f.append(rect(40, 25, 425, 465, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(60, 45, 385, 46, "Апаратне відсікання (STONITH)\n«Вбий інший вузол у голову»", size=13, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(60, 105, 385, 60, "1. Вузол 2 виявив зникнення серцебиття від Вузла 1.", size=11.5, fill=BG))
    f.append(fitbox(60, 180, 385, 75, "2. Вузол 2 через мережу керування шле команду\nна блок живлення (PDU) або IPMI/iLO:\nPOWER OFF / RESET Вузол 1", size=11.5, fill=ACCENT, stroke=POS))
    f.append(fitbox(60, 270, 385, 60, "3. Отримано апаратне підтвердження відключення.", size=11.5, fill=BG))
    f.append(fitbox(60, 345, 385, 65, "4. Вузол 2 безпечно перебирає спільні диски\nта IP-адресу лідера (безпека 100%).", size=11.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(60, 425, 385, 50, "Слабке місце: залежить від окремої мережі IPMI;\nзависання BMC залишає кластер заблокованим.", size=11, color=POS, fill=BG))

    # Колонка 2: Логічний фенсинг (Fencing Tokens)
    f.append(rect(495, 25, 425, 465, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(515, 45, 385, 46, "Логічний фенсинг (Fencing Tokens)\n«Перевірка версії на точці збереження»", size=13, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(515, 105, 385, 60, "1. Консенсус (etcd / Raft) обирає нового лідера\nз монотонно більшим номером терму (e = 42).", size=11.5, fill=BG))
    f.append(fitbox(515, 180, 385, 75, "2. Старий Вузол 1 НЕ вбивають фізично:\nвін може продовжувати виконувати локальний код,\nале його токен застарів (e = 41).", size=11.5, fill=BG))
    f.append(fitbox(515, 270, 385, 60, "3. Сховище даних запам'ятовує останній токен 42.", size=11.5, fill=BG))
    f.append(fitbox(515, 345, 385, 65, "4. Будь-який запис від Вузла 1 відхиляється на диску:\n41 < 42 -> помилка StaleEpoch.", size=11.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(515, 425, 385, 50, "Перевага: не потребує спец-заліза, працює в хмарі;\nвимагає підтримки токенів у сховищі/API.", size=11, color=FIELD, fill=BG))

    render(os.path.join(OUT, 'stonith-vs-tokens.svg'), W, H, *f)


# ── 5. Часова шкала лізи та сторожового таймера (Watchdog) ────────────────
def fig_lease_watchdog_timeline():
    W, H = 1000, 520
    f = []

    # Часова шкала
    y_t = 450
    f.append(line(80, y_t, 920, y_t, color=LINE, sw=2))
    f.append(arrow(910, y_t, 930, y_t, color=LINE, sw=2))
    f.append(text(935, y_t + 5, "час t", size=12, anchor="start"))

    # Стовпці часу: t0, t1 (продовження), t2 (обрив), t3 (закінчення лізи), t4 (failover)
    t0, t1, t2, t3, t4 = 150, 330, 510, 690, 870

    f.append(line(t0, 60, t0, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t1, 60, t1, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t2, 60, t2, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t3, 60, t3, y_t - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(t4, 60, t4, y_t - 20, color=MUTED, sw=1, dash="4,4"))

    f.append(text(t0, y_t + 20, "t0", size=11))
    f.append(text(t1, y_t + 20, "t1 (оновлення)", size=11))
    f.append(text(t2, y_t + 20, "t2 (втрата зв'язку)", size=11))
    f.append(text(t3, y_t + 20, "t3 (лізу вичерпано)", size=11))
    f.append(text(t4, y_t + 20, "t4 (безпечний failover)", size=11))

    # Доріжка 1: Лідер 1 (Діюча ліза та Watchdog)
    yA = 120
    f.append(fitbox(20, yA - 20, 110, 40, "Лідер 1", size=12, bold=True, fill=COOL))
    f.append(rect(t0, yA - 15, t3 - t0, 30, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text((t0 + t3) / 2, yA + 5, "Ліза чинна (TTL = 10 с) — Лідер може писати", size=11, bold=True))

    f.append(rect(t3, yA - 15, t4 + 40 - t3, 30, fill=WARM, stroke=POS, sw=1.8))
    f.append(text((t3 + t4 + 40) / 2, yA + 5, "Watchdog спрацював: Вбивство процесу / Kernel Panic", size=11, color=POS, bold=True))

    # Позначки підгодовування Watchdog
    f.append(arrow(t0 + 20, yA - 45, t0 + 20, yA - 18, color=FIELD, sw=1.5))
    f.append(text(t0 + 20, yA - 52, "ping watchdog", size=10, color=FIELD))

    f.append(arrow(t1, yA - 45, t1, yA - 18, color=FIELD, sw=1.5))
    f.append(text(t1, yA - 52, "renew lease + ping", size=10, color=FIELD))

    f.append(fitbox(t2 - 60, yA - 55, 130, 32, "Втрата зв'язку!\nНемає renew", size=10, fill=WARM, stroke=POS, color=POS))

    # Доріжка 2: Стендбай (Вузол 2)
    yB = 270
    f.append(fitbox(20, yB - 20, 110, 40, "Стендбай (В2)", size=12, bold=True, fill=COOL))
    f.append(rect(t0, yB - 15, t4 - t0, 30, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text((t0 + t4) / 2, yB + 5, "Очікування: гарантована тиша, поки триває ліза старого лідера + захисний буфер Δ", size=11, color=MUTED))

    f.append(rect(t4, yB - 15, t4 + 40 - t4 + 60, 30, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text(t4 + 50, yB + 5, "ПРОМОУШЕН: В2 стає лідером", size=11, bold=True, color=FIELD))

    # Захисний інтервал дельти часу
    f.append(rect(t3, 330, t4 - t3, 40, fill=ACCENT, stroke=LINE, sw=1.2))
    f.append(text((t3 + t4) / 2, 355, "Захисний буфер Δ (дрейф годинника)", size=11))

    # Пояснення внизу
    f.append(fitbox(100, y_t - 55, 800, 36, "Принцип лізи гарантує неперетин інтервалів активності: новий лідер піднімається ЛИШЕ ПІСЛЯ ТОГО, як старий гарантовано склав повноваження або був перезавантажений сторожовим таймером", size=11, fill=BG))

    render(os.path.join(OUT, 'lease-watchdog-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_split_brain_partition()
    fig_fencing_token_timeline()
    fig_quorum_split_matrix()
    fig_stonith_vs_tokens()
    fig_lease_watchdog_timeline()
    print("All figures generated successfully.")
