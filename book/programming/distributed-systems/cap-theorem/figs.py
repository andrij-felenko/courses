# -*- coding: utf-8 -*-
"""Фігури до теми «CAP-теорема й компроміс PACELC»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / аварія / розщеплення / втрата C чи A
COOL = "#eaf0fd"   # клієнти / нейтральне / мережа
GOOD = "#e8f6ee"   # узгодженість / кворум / успіх
ACCENT = "#fff3cd" # попередження / компроміс / латентність


# ── 1. Міф «Оберіть два» проти реальності фізичного розділення ─────────────
def fig_cap_triangle_myth():
    W, H = 1000, 520
    f = []

    # Ліва половина: Популярна ілюзія «Оберіть 2 з 3»
    f.append(rect(30, 25, 450, 470, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(fitbox(50, 40, 410, 36, "Популярна ілюзія: «Оберіть 2 із 3»", size=13, bold=True, fill=COOL))

    # Трикутник з вершинами C, A, P
    f.append(line(255, 110, 110, 340, color=LINE, sw=2))
    f.append(line(255, 110, 400, 340, color=LINE, sw=2))
    f.append(line(110, 340, 400, 340, color=LINE, sw=2))

    f.append(circle(255, 110, 32, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(255, 115, "C", size=18, bold=True, color=FIELD))

    f.append(circle(110, 340, 32, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(110, 345, "A", size=18, bold=True, color=FIELD))

    f.append(circle(400, 340, 32, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(400, 345, "P", size=18, bold=True, color=FIELD))

    # Хибні ребра «CA», «CP», «AP»
    f.append(fitbox(100, 200, 75, 32, "«CA»", size=11.5, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(fitbox(335, 200, 75, 32, "«CP»", size=11.5, bold=True, fill=BG))
    f.append(fitbox(215, 355, 80, 32, "«AP»", size=11.5, bold=True, fill=BG))

    f.append(fitbox(50, 400, 410, 75,
                    "ХИБНЕ ПРИПУЩЕННЯ:\n"
                    "«Можна відмовитися від P і отримати CA-систему».\n"
                    "У фізичній мережі пакети неминуче губляться, тому\n"
                    "стан «CA» в розподіленій системі фізично неможливий.",
                    size=11, bold=True, color=POS, fill=WARM))

    # Права половина: Фізична реальність — бінарний вибір під час розділення
    f.append(rect(520, 25, 450, 470, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(fitbox(540, 40, 410, 36, "Фізична реальність: бінарна дилема", size=13, bold=True, fill=COOL))

    f.append(fitbox(540, 95, 410, 52,
                    "Мережеве розділення (P) — це не вибір, а закон природи.\n"
                    "Коли лінк між вузлами рветься, вибір зводиться до двох шляхів:",
                    size=11.5, fill=BG))

    # Шлях CP
    f.append(rect(540, 165, 410, 130, fill=GOOD, stroke=FIELD, sw=1.8, rx=6))
    f.append(fitbox(555, 175, 380, 30, "Шлях CP: збереження строгої узгодженості", size=12, bold=True, fill=BG, color=FIELD))
    f.append(fitbox(555, 210, 380, 70,
                    "• Ізольований вузол відхиляє запити або чекає відновлення зв'язку.\n"
                    "• Жоден клієнт не прочитає застарілі або суперечливі дані.\n"
                    "• Ціна: втрата доступності (Availability = 0) для відрізаної зони.",
                    size=11, fill=FILL))

    # Шлях AP
    f.append(rect(540, 315, 410, 130, fill=ACCENT, stroke=POS, sw=1.8, rx=6))
    f.append(fitbox(555, 325, 380, 30, "Шлях AP: збереження повної доступності", size=12, bold=True, fill=BG, color=POS))
    f.append(fitbox(555, 360, 380, 70,
                    "• Ізольований вузол локально відповідає на всі читання і записи.\n"
                    "• Доступність 100%: жоден клієнт не отримує помилку тайм-ауту.\n"
                    "• Ціна: втрата узгодженості (Consistency = 0), стан роздвоюється.",
                    size=11, fill=FILL))

    render(os.path.join(OUT, 'cap-triangle-myth.svg'), W, H, *f)


# ── 2. Дилема мережевого розділення (Node A vs Node B) ────────────────────
def fig_network_partition_dilemma():
    W, H = 960, 520
    f = []

    # Заголовки зон
    f.append(fitbox(40, 25, 400, 46, "Дата-центр Франкфурт (Зона А)\nПочатковий стан: x = 1", size=12.5, bold=True, fill=COOL))
    f.append(fitbox(520, 25, 400, 46, "Дата-центр Дублін (Зона Б)\nПочатковий стан: x = 1", size=12.5, bold=True, fill=COOL))

    # Червона смуга аварії між ДЦ
    f.append(rect(455, 85, 50, 310, fill=WARM, stroke=POS, sw=1.5, rx=4))
    f.append(line(480, 95, 480, 385, color=POS, sw=2, dash="5,4"))
    f.append(fitbox(457, 190, 46, 100, "ОБРИВ\nЛІНКА\n(P)", size=11, bold=True, color=POS, fill=BG, stroke=POS))

    # Лівий вузол: приймає запис
    f.append(rect(60, 95, 360, 150, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(fitbox(80, 105, 320, 36, "Вузол 1 (Франкфурт)", size=12.5, bold=True, fill=BG))
    f.append(fitbox(80, 145, 320, 85,
                    "Клієнт виконує запис:\n"
                    "Write(x, 2) -> OK\n"
                    "Локальне значення оновлено: x = 2.\n"
                    "Спроба відправити реплікацію на Вузол 2 блокується обривом.",
                    size=11, fill=FILL))

    # Правий вузол: приймає читання
    f.append(rect(540, 95, 360, 150, fill=ACCENT, stroke=POS, sw=2, rx=8))
    f.append(fitbox(560, 105, 320, 36, "Вузол 2 (Дублін)", size=12.5, bold=True, fill=BG))
    f.append(fitbox(560, 145, 320, 85,
                    "Клієнт виконує читання:\n"
                    "Read(x) -> Що відповісти?\n"
                    "Вузол 2 не знає, чи був запис на Вузлі 1,\n"
                    "бо всі мережеві запити зависають на обриві.",
                    size=11, fill=FILL))

    # Стрілки клієнтських запитів
    f.append(fitbox(60, 270, 360, 45, "Клієнт А: Write(x, 2)", size=12, bold=True, fill=COOL))
    f.append(arrow(240, 270, 240, 250, color=FIELD, sw=2))

    f.append(fitbox(540, 270, 360, 45, "Клієнт Б: Read(x)", size=12, bold=True, fill=COOL))
    f.append(arrow(720, 270, 720, 250, color=POS, sw=2))

    # Нижні варіанти вирішення дилеми
    f.append(rect(60, 335, 400, 160, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(fitbox(75, 345, 370, 30, "Рішення 1: CP (Строга узгодженість)", size=12, bold=True, fill=BG, color=FIELD))
    f.append(fitbox(75, 380, 370, 100,
                    "Вузол 2 відмовляється відповідати без кворуму:\n"
                    "Read(x) -> Error 503 / Timeout.\n"
                    "✓ Лінеаризовність збережена: старий x=1 не видано.\n"
                    "✗ Втрата доступності: живий клієнт отримав збій.",
                    size=11, fill=FILL))

    f.append(rect(500, 335, 400, 160, fill=WARM, stroke=POS, sw=1.8, rx=8))
    f.append(fitbox(515, 345, 370, 30, "Рішення 2: AP (Висока доступність)", size=12, bold=True, fill=BG, color=POS))
    f.append(fitbox(515, 380, 370, 100,
                    "Вузол 2 негайно повертає локальне значення:\n"
                    "Read(x) -> 1 (OK).\n"
                    "✓ 100% доступність: клієнт отримав миттєву відповідь.\n"
                    "✗ Втрата узгодженості: повернуто застарілий x=1 після запису x=2.",
                    size=11, fill=FILL))

    render(os.path.join(OUT, 'network-partition-dilemma.svg'), W, H, *f)


# ── 3. Матриця PACELC (розширення компромісу на штатний режим) ────────────
def fig_pacelc_matrix():
    W, H = 1000, 560
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 920, 44, "Модель PACELC: Повна картина розподілених компромісів (Daniel Abadi)", size=13.5, bold=True, fill=COOL))

    # Вісь X і Y квадрантів
    f.append(rect(60, 80, 430, 205, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(rect(510, 80, 430, 205, fill=COOL, stroke=LINE, sw=1.8, rx=8))
    f.append(rect(60, 305, 430, 205, fill=ACCENT, stroke=LINE, sw=1.8, rx=8))
    f.append(rect(510, 305, 430, 205, fill=WARM, stroke=POS, sw=1.8, rx=8))

    # Квадрант 1: PC / EC
    f.append(fitbox(75, 90, 400, 32, "Квадрант PC / EC (Строгість у всьому)", size=12, bold=True, fill=BG, color=FIELD))
    f.append(fitbox(75, 125, 400, 145,
                    "• При розділенні (P): обирають Узгодженість (C).\n"
                    "• У штатному режимі (E): платять Латентністю (L) заради Узгодженості (C).\n"
                    "• Механізм: Синхронна реплікація через Raft / Paxos / 2PC.\n"
                    "• Приклади: Google Spanner, CockroachDB, HBase, etcd, ZooKeeper.",
                    size=11, fill=FILL))

    # Квадрант 2: PC / EL
    f.append(fitbox(525, 90, 400, 32, "Квадрант PC / EL (Лідер-орієнтовані з асинхронним читанням)", size=12, bold=True, fill=BG))
    f.append(fitbox(525, 125, 400, 145,
                    "• При розділенні (P): обирають Узгодженість (C) на первинному вузлі.\n"
                    "• У штатному режимі (E): читають з реплік заради низької Латентності (L).\n"
                    "• Механізм: Записи йдуть на Primary, читання — на асинхронні фоловери.\n"
                    "• Приклади: MongoDB (Secondary reads), PostgreSQL / MySQL (Read Replicas).",
                    size=11, fill=FILL))

    # Квадрант 3: PA / EC
    f.append(fitbox(75, 315, 400, 32, "Квадрант PA / EC (Синхронний спокій, аварійна доступність)", size=12, bold=True, fill=BG))
    f.append(fitbox(75, 350, 400, 145,
                    "• При розділенні (P): дозволяють локальну Доступність (A).\n"
                    "• У штатному режимі (E): тримають строгу Узгодженість (C) через 2PC.\n"
                    "• Механізм: Повна синхронність у спокійний час, перемикання на кеш при аварії.\n"
                    "• Приклади: Спеціалізовані кешуючі системи, VoltDB (у режимі екстреного читання).",
                    size=11, fill=FILL))

    # Квадрант 4: PA / EL
    f.append(fitbox(525, 315, 400, 32, "Квадрант PA / EL (Максимальна швидкість і виживання)", size=12, bold=True, fill=BG, color=POS))
    f.append(fitbox(525, 350, 400, 145,
                    "• При розділенні (P): обирають Доступність (A) у кожній зоні.\n"
                    "• У штатному режимі (E): мінімізують Латентність (L), поступаючись C.\n"
                    "• Механізм: Асинхронний мультимайстер, CRDT, векторні годинники, LWW.\n"
                    "• Приклади: Amazon DynamoDB (Eventual), Apache Cassandra, Riak, Couchbase.",
                    size=11, fill=FILL))

    # Підсумковий пояснювальний рядок
    f.append(fitbox(40, 518, 920, 30, "Формула PACELC: if Partition (choose A or C) Else (choose L or C)", size=11.5, bold=True, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'pacelc-matrix.svg'), W, H, *f)


# ── 4. Налаштовуваний кворум і перетин Read/Write ──────────────────────────
def fig_tunable_quorum_overlap():
    W, H = 960, 500
    f = []

    f.append(fitbox(40, 20, 880, 40, "Налаштовувані кворуми: гарантія свіжості проти ціни латентності", size=13, bold=True, fill=COOL))

    # Ліва колонка: Строгий кворум (R + W > N)
    f.append(rect(40, 75, 425, 395, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(fitbox(60, 90, 385, 32, "Строгий кворум: R + W > N (N = 5, W = 3, R = 3)", size=12, bold=True, fill=BG, color=FIELD))

    # Вузли 1..5
    for i in range(5):
        y_pos = 140 + i * 50
        is_w = i in [0, 1, 2] # W = 3
        is_r = i in [2, 3, 4] # R = 3
        is_overlap = i == 2   # Вузол 3 — перетин

        f.append(rect(70, y_pos, 70, 38, fill=BG, stroke=LINE, sw=1.2, rx=4))
        f.append(text(105, y_pos + 23, "Вузол %d" % (i + 1), size=11, bold=True))

        if is_w:
            f.append(rect(155, y_pos + 4, 110, 30, fill=COOL, stroke=LINE, sw=1, rx=3))
            f.append(text(210, y_pos + 23, "Запис (W=3)", size=10.5))

        if is_r:
            f.append(rect(280, y_pos + 4, 110, 30, fill=ACCENT, stroke=LINE, sw=1, rx=3))
            f.append(text(335, y_pos + 23, "Читання (R=3)", size=10.5))

        if is_overlap:
            f.append(rect(400, y_pos + 4, 55, 30, fill=WARM, stroke=POS, sw=1.5, rx=3))
            f.append(text(427, y_pos + 23, "СВІЖИЙ", size=10, bold=True, color=POS))

    f.append(fitbox(60, 400, 385, 55,
                    "Принцип Діріхле: множини запису і читання завжди перетинаються.\n"
                    "Читач гарантовано отримує найновішу версію (строга узгодженість).\n"
                    "Ціна: чекання відповідей від більшості вузлів по мережі.",
                    size=10.5, fill=FILL))

    # Права колонка: Слабкий кворум (R + W <= N)
    f.append(rect(495, 75, 425, 395, fill=WARM, stroke=POS, sw=1.8, rx=8))
    f.append(fitbox(515, 90, 385, 32, "Слабкий кворум: R + W <= N (N = 5, W = 2, R = 2)", size=12, bold=True, fill=BG, color=POS))

    for i in range(5):
        y_pos = 140 + i * 50
        is_w = i in [0, 1]     # W = 2
        is_r = i in [3, 4]     # R = 2

        f.append(rect(525, y_pos, 70, 38, fill=BG, stroke=LINE, sw=1.2, rx=4))
        f.append(text(560, y_pos + 23, "Вузол %d" % (i + 1), size=11, bold=True))

        if is_w:
            f.append(rect(610, y_pos + 4, 110, 30, fill=COOL, stroke=LINE, sw=1, rx=3))
            f.append(text(665, y_pos + 23, "Запис (W=2)", size=10.5))

        if is_r:
            f.append(rect(735, y_pos + 4, 110, 30, fill=ACCENT, stroke=LINE, sw=1, rx=3))
            f.append(text(790, y_pos + 23, "Читання (R=2)", size=10.5))

        if i == 2:
            f.append(fitbox(610, y_pos + 4, 235, 30, "НЕМАЄ ПЕРЕТИНУ МНОЖИН", size=10.5, bold=True, color=POS, fill=BG, stroke=POS))

    f.append(fitbox(515, 400, 385, 55,
                    "Множини запису і читання можуть не перетинатися.\n"
                    "Читач може отримати застаріле значення або порожнечу.\n"
                    "Вигода: наднизька латентність і стійкість до відмови більшості.",
                    size=10.5, fill=FILL))

    render(os.path.join(OUT, 'tunable-quorum-overlap.svg'), W, H, *f)


if __name__ == "__main__":
    fig_cap_triangle_myth()
    fig_network_partition_dilemma()
    fig_pacelc_matrix()
    fig_tunable_quorum_overlap()
    print("Всі 4 фігури згенеровано успішно.")
