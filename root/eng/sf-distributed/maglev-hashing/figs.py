# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

ACCENT = "#2457d6"
GREEN = "#27ae60"
RED = "#c0392b"


def box(cx, cy, s, size=11, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Проблема зміни маршруту в ECMP при відмові L4-вузла ────────────
def fig_ecmp_packet_spray_problem():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 26, "Проблема зміни маршруту ECMP та колізії сесій при падінні L4-балансувальника", size=14, bold=True))

    # Ліва частина: Стабільний стан (до падіння)
    frags.append(rect(20, 50, 485, 450, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(262, 75, "Стан 1: Усі L4-вузли активні", size=12, bold=True, color=GREEN))

    frags.append(box(262, 115, "Клієнт (198.51.100.5:54321) -> VIP:443\nАктивна TCP-сесія (потік SYN/ACK вже пройдено)", size=10, fill="#ffffff", stroke=MUTED, min_w=340))

    frags.append(arrow(262, 142, 262, 172, color=INK, sw=1.5))
    frags.append(box(262, 195, "Граничний BGP-маршрутизатор (ECMP)\nhash(5-tuple) mod 3 = Слот 0", size=10, bold=True, fill="#f0f4ff", stroke=ACCENT, min_w=280))

    # Розподіл на 3 L4
    frags.append(arrow(220, 225, 120, 265, color=GREEN, sw=1.8))
    frags.append(arrow(262, 225, 262, 265, color=MUTED, sw=1.0))
    frags.append(arrow(304, 225, 404, 265, color=MUTED, sw=1.0))

    frags.append(box(120, 290, "L4 Вузол 1\n(Активний)", size=10, fill="#eefaf0", stroke=GREEN, min_w=105))
    frags.append(box(262, 290, "L4 Вузол 2\n(Активний)", size=10, fill="#ffffff", stroke=MUTED, min_w=105))
    frags.append(box(404, 290, "L4 Вузол 3\n(Активний)", size=10, fill="#ffffff", stroke=MUTED, min_w=105))

    frags.append(arrow(120, 318, 120, 360, color=GREEN, sw=1.8))
    frags.append(box(262, 395, "Пул бекенд-серверів\n[Бекенд A] <- Тримає відкритий TCP-сокет\n[Бекенд B]\n[Бекенд C]", size=10, fill="#ffffff", stroke=MUTED, min_w=320))

    frags.append(rect(35, 442, 455, 46, fill="#f4faf5", stroke=GREEN, sw=1, rx=4))
    frags.append(text(262, 469, "Результат: Пакети потоку стабільно надходять на Бекенд A", size=10, color=GREEN, bold=True))

    # Права частина: Аварія L4 Вузла 1 та зсув ECMP
    frags.append(rect(535, 50, 485, 450, fill="#fffcfc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(777, 75, "Стан 2: Вузол 1 впав -> Зсув хешу ECMP", size=12, bold=True, color=RED))

    frags.append(box(777, 115, "Клієнт (198.51.100.5:54321) -> VIP:443\nЧерговий TCP-пакет даних тієї самої сесії", size=10, fill="#ffffff", stroke=MUTED, min_w=340))

    frags.append(arrow(777, 142, 777, 172, color=INK, sw=1.5))
    frags.append(box(777, 195, "Граничний BGP-маршрутизатор (ECMP)\nhash(5-tuple) mod 2 = Слот 1 (Перенаправлено!)", size=10, bold=True, fill="#fff0f0", stroke=RED, min_w=310))

    # Розподіл на 2 L4
    frags.append(arrow(735, 225, 635, 265, color=MUTED, sw=1.0))
    frags.append(arrow(820, 225, 920, 265, color=RED, sw=1.8))

    frags.append(box(635, 290, "L4 Вузол 1\n(ВІДМОВА ✖)", size=10, fill="#fee", stroke=RED, min_w=105))
    frags.append(box(777, 290, "L4 Вузол 2\n(Активний)", size=10, fill="#ffffff", stroke=MUTED, min_w=105))
    frags.append(box(920, 290, "L4 Вузол 3\n(Отримав пакет)", size=10, fill="#fff0f0", stroke=RED, min_w=115))

    # L4 Вузол 3 скеровує на бекенд
    frags.append(arrow(920, 318, 860, 360, color=RED, sw=1.8))
    frags.append(box(777, 395, "Пул бекенд-серверів\n[Бекенд A] (Очікує пакет)\n[Бекенд B] <- Помилково отримав пакет без сесії!\n[Бекенд C]", size=10, fill="#ffffff", stroke=MUTED, min_w=330))

    frags.append(rect(550, 442, 455, 46, fill="#fdf2f2", stroke=RED, sw=1, rx=4))
    frags.append(text(777, 460, "Без Maglev: Бекенд B надсилає клієнту TCP RST (обрив сесії)", size=9, color=RED, bold=True))
    frags.append(text(777, 477, "З Maglev: Вузол 3 має ту саму таблицю і шле на Бекенд A!", size=9, color=GREEN, bold=True))

    return render(os.path.join(IMG, 'ecmp-packet-spray-problem.svg'), W, H, *frags)


# ── Фігура 2: Генерація псевдовипадкових перестановок бекендів ────────────────
def fig_maglev_permutation_generation():
    W, H = 1040, 480
    frags = []

    frags.append(text(520, 26, "Генерація псевдовипадкових перестановок комірок для кожного бекенда", size=14, bold=True))

    # Опис вхідних параметрів
    frags.append(rect(20, 50, 1000, 75, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(520, 74, "Математична основа: Розмір таблиці M = 7 (просте число), N = 3 бекенди", size=11, bold=True, color=INK))
    frags.append(text(520, 102, "Формула кроку: offset[i] = hash1(name) mod M,   skip[i] = (hash2(name) mod (M - 1)) + 1   (НСД(skip, M) = 1)", size=10, color=INK))

    # Стовпчик Бекенд 0
    frags.append(rect(20, 140, 315, 320, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    frags.append(box(177, 168, "Бекенд B0 (srv-01)\noffset = 3,  skip = 4", size=10, bold=True, fill="#e8f0fe", stroke=ACCENT, min_w=280))
    frags.append(text(177, 215, "Послідовність кандидатів j = 0..6:", size=10, bold=True, color=INK))
    
    b0_seq = [
        "j=0: (3 + 0·4) mod 7 = 3",
        "j=1: (3 + 1·4) mod 7 = 0",
        "j=2: (3 + 2·4) mod 7 = 4",
        "j=3: (3 + 3·4) mod 7 = 1",
        "j=4: (3 + 4·4) mod 7 = 5",
        "j=5: (3 + 5·4) mod 7 = 2",
        "j=6: (3 + 6·4) mod 7 = 6"
    ]
    frags.append(mtext(177, 235, b0_seq, size=10, color=INK, lh=1.45))
    frags.append(rect(35, 410, 285, 38, fill="#f0fdf4", stroke=GREEN, sw=1, rx=4))
    frags.append(text(177, 432, "Перестановка: [3, 0, 4, 1, 5, 2, 6]", size=10, bold=True, color=GREEN))

    # Стовпчик Бекенд 1
    frags.append(rect(362, 140, 315, 320, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    frags.append(box(520, 168, "Бекенд B1 (srv-02)\noffset = 0,  skip = 2", size=10, bold=True, fill="#fef3c7", stroke="#d97706", min_w=280))
    frags.append(text(520, 215, "Послідовність кандидатів j = 0..6:", size=10, bold=True, color=INK))
    
    b1_seq = [
        "j=0: (0 + 0·2) mod 7 = 0",
        "j=1: (0 + 1·2) mod 7 = 2",
        "j=2: (0 + 2·2) mod 7 = 4",
        "j=3: (0 + 3·2) mod 7 = 6",
        "j=4: (0 + 4·2) mod 7 = 1",
        "j=5: (0 + 5·2) mod 7 = 3",
        "j=6: (0 + 6·2) mod 7 = 5"
    ]
    frags.append(mtext(520, 235, b1_seq, size=10, color=INK, lh=1.45))
    frags.append(rect(377, 410, 285, 38, fill="#f0fdf4", stroke=GREEN, sw=1, rx=4))
    frags.append(text(520, 432, "Перестановка: [0, 2, 4, 6, 1, 3, 5]", size=10, bold=True, color=GREEN))

    # Стовпчик Бекенд 2
    frags.append(rect(705, 140, 315, 320, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    frags.append(box(862, 168, "Бекенд B2 (srv-03)\noffset = 5,  skip = 3", size=10, bold=True, fill="#e0e7ff", stroke="#4f46e5", min_w=280))
    frags.append(text(862, 215, "Послідовність кандидатів j = 0..6:", size=10, bold=True, color=INK))
    
    b2_seq = [
        "j=0: (5 + 0·3) mod 7 = 5",
        "j=1: (5 + 1·3) mod 7 = 1",
        "j=2: (5 + 2·3) mod 7 = 4",
        "j=3: (5 + 3·3) mod 7 = 0",
        "j=4: (5 + 4·3) mod 7 = 3",
        "j=5: (5 + 5·3) mod 7 = 6",
        "j=6: (5 + 6·3) mod 7 = 2"
    ]
    frags.append(mtext(862, 235, b2_seq, size=10, color=INK, lh=1.45))
    frags.append(rect(720, 410, 285, 38, fill="#f0fdf4", stroke=GREEN, sw=1, rx=4))
    frags.append(text(862, 432, "Перестановка: [5, 1, 4, 0, 3, 6, 2]", size=10, bold=True, color=GREEN))

    return render(os.path.join(IMG, 'maglev-permutation-generation.svg'), W, H, *frags)


# ── Фігура 3: Раундовий процес заповнення таблиці Maglev ─────────────────────
def fig_maglev_table_filling_race():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 26, "Покрокове заповнення таблиці пошуку Maglev методом циклічного суперництва", size=14, bold=True))

    # Стан 0: Порожня таблиця
    frags.append(text(120, 65, "Початковий стан:", size=10, bold=True, color=INK))
    table_x = 240
    y0 = 55
    for c in range(7):
        frags.append(rect(table_x + c * 80, y0, 72, 32, fill="#f1f5f9", stroke=MUTED, sw=1, rx=4))
        frags.append(text(table_x + c * 80 + 36, y0 + 14, f"Слот {c}", size=9, color=MUTED))
        frags.append(text(table_x + c * 80 + 36, y0 + 26, "—", size=10, bold=True, color=MUTED))

    # Раунд 1
    frags.append(rect(20, 105, 1000, 110, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    frags.append(text(100, 130, "Раунд 1 (j=0):", size=11, bold=True, color=ACCENT))
    frags.append(text(100, 155, "B0 претендує на 3 (вільно -> B0)", size=9, color=INK))
    frags.append(text(100, 175, "B1 претендує на 0 (вільно -> B1)", size=9, color=INK))
    frags.append(text(100, 195, "B2 претендує на 5 (вільно -> B2)", size=9, color=INK))

    y1 = 140
    r1_state = [("B1", "#fef3c7", "#d97706"), ("—", "#f1f5f9", MUTED), ("—", "#f1f5f9", MUTED),
                ("B0", "#e8f0fe", ACCENT), ("—", "#f1f5f9", MUTED), ("B2", "#e0e7ff", "#4f46e5"),
                ("—", "#f1f5f9", MUTED)]
    for c, (val, bg, col) in enumerate(r1_state):
        frags.append(rect(table_x + c * 80 + 100, y1, 72, 45, fill=bg, stroke=col, sw=1.2, rx=4))
        frags.append(text(table_x + c * 80 + 136, y1 + 16, f"Слот {c}", size=9, color=INK))
        frags.append(text(table_x + c * 80 + 136, y1 + 34, val, size=12, bold=True, color=col))

    # Раунд 2 (із колізіями)
    frags.append(rect(20, 230, 1000, 140, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    frags.append(text(100, 255, "Раунд 2:", size=11, bold=True, color=ACCENT))
    frags.append(text(100, 280, "B0 хоче 0 (зайнято B1!) -> бере j=2: Слот 4", size=9, color=RED))
    frags.append(text(100, 305, "B1 хоче 2 (вільно -> B1)", size=9, color=INK))
    frags.append(text(100, 330, "B2 хоче 1 (вільно -> B2)", size=9, color=INK))
    frags.append(text(100, 355, "Залишився 1 вільний слот...", size=9, color=MUTED))

    y2 = 280
    r2_state = [("B1", "#fef3c7", "#d97706"), ("B2", "#e0e7ff", "#4f46e5"), ("B1", "#fef3c7", "#d97706"),
                ("B0", "#e8f0fe", ACCENT), ("B0", "#e8f0fe", ACCENT), ("B2", "#e0e7ff", "#4f46e5"),
                ("—", "#f1f5f9", MUTED)]
    for c, (val, bg, col) in enumerate(r2_state):
        frags.append(rect(table_x + c * 80 + 100, y2, 72, 45, fill=bg, stroke=col, sw=1.2, rx=4))
        frags.append(text(table_x + c * 80 + 136, y2 + 16, f"Слот {c}", size=9, color=INK))
        frags.append(text(table_x + c * 80 + 136, y2 + 34, val, size=12, bold=True, color=col))

    # Фінальний стан
    frags.append(rect(20, 385, 1000, 115, fill="#f8fafc", stroke=GREEN, sw=1.5, rx=6))
    frags.append(text(100, 415, "Фінал (Раунд 3):", size=11, bold=True, color=GREEN))
    frags.append(text(100, 440, "B0 претендує на 1, 5, 2 (зайняті)", size=9, color=INK))
    frags.append(text(100, 460, "B0 бере слот 6 -> Таблицю заповнено!", size=9, bold=True, color=GREEN))

    y3 = 425
    r3_state = [("B1", "#fef3c7", "#d97706"), ("B2", "#e0e7ff", "#4f46e5"), ("B1", "#fef3c7", "#d97706"),
                ("B0", "#e8f0fe", ACCENT), ("B0", "#e8f0fe", ACCENT), ("B2", "#e0e7ff", "#4f46e5"),
                ("B0", "#e8f0fe", ACCENT)]
    for c, (val, bg, col) in enumerate(r3_state):
        frags.append(rect(table_x + c * 80 + 100, y3, 72, 45, fill=bg, stroke=col, sw=1.5, rx=4))
        frags.append(text(table_x + c * 80 + 136, y3 + 16, f"Слот {c}", size=9, color=INK))
        frags.append(text(table_x + c * 80 + 136, y3 + 34, val, size=12, bold=True, color=col))

    return render(os.path.join(IMG, 'maglev-table-filling-race.svg'), W, H, *frags)


# ── Фігура 4: Архітектура конвеєра Katran L4 в XDP/eBPF ─────────────────────
def fig_katran_ebpf_xdp_pipeline():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 26, "Конвеєр обробки пакетів L4-балансувальника Katran в оточенні eBPF / XDP", size=14, bold=True))

    # Вхідний пакет
    frags.append(box(90, 110, "Мережева карта (NIC)\nВхідний пакет (100 Gbps)\nRx Ring Buffer", size=10, fill="#f1f5f9", stroke=MUTED, min_w=140))

    frags.append(arrow(165, 110, 205, 110, color=ACCENT, sw=2))

    # Блок драйвера XDP
    frags.append(rect(210, 60, 620, 420, fill="#fcfdfe", stroke=ACCENT, sw=1.5, rx=6))
    frags.append(text(520, 85, "Ядро Linux: Драйверний рівень XDP (до алокації sk_buff)", size=12, bold=True, color=ACCENT))

    # Крок 1: Парсинг заголовків
    frags.append(box(320, 140, "1. Парсинг L2/L3/L4\nВилучення 5-tuple:\nSrcIP, DstIP(VIP), Port, Proto", size=9, fill="#ffffff", stroke=MUTED, min_w=170))

    frags.append(arrow(410, 140, 450, 140, color=INK, sw=1.5))

    # Крок 2: Перевірка LRU таблиці з'єднань
    frags.append(box(570, 140, "2. Пошук у BPF LRU Map\nТаблиця активних сесій\n(Flow Cache)", size=9, bold=True, fill="#e8f0fe", stroke=ACCENT, min_w=170))

    # Гілка Hit
    frags.append(arrow(660, 140, 720, 140, color=GREEN, sw=1.5))
    frags.append(text(685, 130, "Hit (є запис)", size=9, bold=True, color=GREEN))
    frags.append(box(745, 180, "Готовий бекенд\n(IP / MAC)", size=9, fill="#f0fdf4", stroke=GREEN, min_w=100))

    # Гілка Miss
    frags.append(arrow(570, 175, 570, 225, color=RED, sw=1.5))
    frags.append(text(575, 200, "Miss (новий потік або SYN)", size=9, bold=True, color=RED, anchor="start"))

    # Крок 3: Maglev Hashing Map
    frags.append(box(570, 270, "3. Обчислення Maglev Hash\nh = hash_5tuple(flow)\nСлот = h mod M (65537)\nBPF Array: maglev_lut[Слот]", size=9, bold=True, fill="#fef3c7", stroke="#d97706", min_w=190))

    frags.append(arrow(570, 315, 570, 355, color=INK, sw=1.5))
    frags.append(box(570, 380, "Оновлення LRU Map\nЗбереження обраного бекенда\nдля наступних пакетів", size=9, fill="#ffffff", stroke=MUTED, min_w=180))

    # З'єднання до інкапсуляції
    frags.append(arrow(745, 215, 745, 380, color=GREEN, sw=1.5))
    frags.append(arrow(665, 380, 700, 380, color=INK, sw=1.5))

    # Крок 4: Інкапсуляція
    frags.append(rect(230, 355, 190, 95, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(325, 375, "4. Інкапсуляція пакета", size=10, bold=True, color=INK))
    frags.append(text(325, 395, "Додавання заголовка IPIP / GUE", size=9, color=INK))
    frags.append(text(325, 415, "Підміна MAC на шлюз DSR", size=9, color=INK))
    frags.append(text(325, 435, "Дія: XDP_TX (зворот у дріт)", size=9, bold=True, color=GREEN))

    frags.append(arrow(475, 380, 425, 380, color=GREEN, sw=1.8))

    # Вихід
    frags.append(arrow(230, 400, 165, 400, color=GREEN, sw=2))
    frags.append(box(90, 400, "Мережевий комутатор (ToR)\nПакет летить на бекенд\nчерез інкапсуляцію DSR", size=10, fill="#f0fdf4", stroke=GREEN, min_w=140))

    return render(os.path.join(IMG, 'katran-ebpf-xdp-pipeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_ecmp_packet_spray_problem()
    fig_maglev_permutation_generation()
    fig_maglev_table_filling_race()
    fig_katran_ebpf_xdp_pipeline()
    print("Усі 4 фігури успішно згенеровано.")
