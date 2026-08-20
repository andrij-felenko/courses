# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: book/programming/security/password-hashing -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. hash-speed-paradox: Асиметрія швидкості швидких і повільних гешів ─────
def fig_hash_speed_paradox():
    W, H = 840, 340
    p = []

    # Заголовок / концептуальний поділ на дві колонки
    # Ліва колонка: Швидкі криптографічні геші (Катастрофа для паролів)
    p.append(rect(30, 30, 370, 280, fill="#fdf2f2", stroke=POS, sw=2, rx=10))
    p.append(text(215, 60, "Швидкі криптогеші (SHA-256, MD5)", size=14, color=POS, bold=True))
    p.append(text(215, 80, "Оптимізовані під гігабайти/с", size=11, color=MUTED))

    # Характеристики зліва
    b1, _, _ = textbox(215, 120, "Швидкість перебору (GPU RTX 4090):\n~ 10 000 000 000 гешів/с (10 GH/s)",
                       size=11, color=POS, fill="#ffffff", stroke=POS, sw=1.2, min_w=330)
    p.append(b1)

    b2, _, _ = textbox(215, 180, "Використання пам'яті: 0 байтів RAM\n(стан повністю вміщується в регістри)",
                       size=11, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=330)
    p.append(b2)

    b3, _, _ = textbox(215, 250, "Наслідок для 8-значного пароля:\nЗлам бази займає лічені хвилини",
                       size=11, color=POS, fill="#ffffff", stroke=POS, sw=1.5, bold=True, min_w=330)
    p.append(b3)

    # Права колонка: Пам'ятевитратні повільні KDF (Argon2id, scrypt, bcrypt)
    p.append(rect(440, 30, 370, 280, fill="#edf7ee", stroke=FIELD, sw=2, rx=10))
    p.append(text(625, 60, "Пам'ятевитратні KDF (Argon2id)", size=14, color=FIELD, bold=True))
    p.append(text(625, 80, "Спеціально сповільнені для паролів", size=11, color=MUTED))

    # Характеристики справа
    b4, _, _ = textbox(625, 120, "Швидкість перебору (GPU RTX 4090):\n~ 20 - 50 гешів/с (при 64 МБ RAM)",
                       size=11, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.2, min_w=330)
    p.append(b4)

    b5, _, _ = textbox(625, 180, "Використання пам'яті: 64 МБ на спробу\n(насичує шину пам'яті GPU/ASIC)",
                       size=11, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=330)
    p.append(b5)

    b6, _, _ = textbox(625, 250, "Наслідок для 8-значного пароля:\nЗлам вимагає століть та мільйонів $",
                       size=11, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True, min_w=330)
    p.append(b6)

    render(os.path.join(OUT, "hash-speed-paradox.svg"), W, H, *p,
           title="Парадокс швидкості гешів")


# ── 2. salt-and-rainbow-defense: Сіль та руйнування веселкових таблиць ────────
def fig_salt_and_rainbow_defense():
    W, H = 840, 340
    p = []

    # Верхній блок: Без солі (однаковий пароль -> однаковий геш, готова райдужна таблиця)
    p.append(rect(30, 25, 780, 135, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    p.append(text(420, 48, "БЕЗ СОЛІ: Глобальна вразливість до попередньо обчислених словників", size=12, color=POS, bold=True))

    p.append(rect(50, 65, 180, 70, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(140, 88, "Користувач A: \"Secret1\"", size=11, color=INK))
    p.append(text(140, 112, "Користувач B: \"Secret1\"", size=11, color=INK))

    p.append(arrow(230, 100, 310, 100, color=POS, sw=2))
    p.append(text(270, 90, "SHA-256", size=10, color=MUTED))

    p.append(rect(310, 65, 190, 70, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(405, 88, "Геш A: e5c7...2b", size=11, color=POS, bold=True))
    p.append(text(405, 112, "Геш B: e5c7...2b", size=11, color=POS, bold=True))

    p.append(arrow(500, 100, 580, 100, color=POS, sw=2))
    p.append(text(540, 90, "Пошук", size=10, color=POS))

    p.append(rect(580, 65, 210, 70, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(685, 88, "Веселкова таблиця", size=11, color=POS, bold=True))
    p.append(text(685, 112, "1 запит зламує всіх одразу", size=10, color=INK))

    # Нижній блок: З криптографічною сіллю
    p.append(rect(30, 175, 780, 145, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(420, 198, "З УНІКАЛЬНОЮ СІЛЛЮ (16+ байтів CSPRNG на кожного користувача)", size=12, color=FIELD, bold=True))

    p.append(rect(50, 215, 220, 85, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(160, 238, "User A: \"Secret1\" + Сіль A", size=10, color=INK))
    p.append(text(160, 258, "User B: \"Secret1\" + Сіль B", size=10, color=INK))
    p.append(text(160, 278, "сіль генерується CSPRNG", size=9, color=MUTED, italic=True))

    p.append(arrow(270, 255, 340, 255, color=FIELD, sw=2))
    p.append(text(305, 245, "Argon2id", size=10, color=FIELD))

    p.append(rect(340, 215, 210, 85, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(445, 238, "Геш A: $argon2id$...9a1", size=10, color=FIELD, bold=True))
    p.append(text(445, 258, "Геш B: $argon2id$...7f4", size=10, color=FIELD, bold=True))
    p.append(text(445, 278, "геші цілком різні", size=9, color=MUTED, italic=True))

    p.append(arrow(550, 255, 620, 255, color=FIELD, sw=2))
    p.append(text(585, 245, "Неможливо", size=10, color=MUTED))

    p.append(rect(620, 215, 170, 85, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(705, 238, "Таблиці марні", size=11, color=FIELD, bold=True))
    p.append(text(705, 258, "Атака O(N_корист · K)", size=10, color=INK))
    p.append(text(705, 278, "окремий перебір для кожного", size=9, color=MUTED))

    render(os.path.join(OUT, "salt-and-rainbow-defense.svg"), W, H, *p,
           title="Роль унікальної солі у захисті від словникових атак")


# ── 3. memory-hard-matrix: Структура пам'яті Argon2 ───────────────────────────
def fig_memory_hard_matrix():
    W, H = 840, 350
    p = []

    # Загальний контейнер
    p.append(rect(30, 20, 780, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(420, 45, "Матриця пам'яті Argon2 (Паралелізм p = 4 смуги, Скибки S = 4)", size=13, color=INK, bold=True))

    lanes_y = [70, 125, 180, 235]
    lane_h = 42

    for i, y in enumerate(lanes_y):
        p.append(text(75, y + 26, f"Смуга {i}", size=11, color=INK, bold=True))
        # 4 скибки (slices)
        for s in range(4):
            x = 130 + s * 160
            is_active = (i == 1 and s == 2)
            bg_col = "#dbeafe" if is_active else "#ffffff"
            st_col = NEG if is_active else MUTED
            p.append(rect(x, y, 150, lane_h, fill=bg_col, stroke=st_col, sw=1.2, rx=4))
            p.append(text(x + 75, y + 18, f"Скибка {s} (Блоки 1 КБ)", size=9, color=MUTED))
            if is_active:
                p.append(text(x + 75, y + 33, "Обчислюваний блок B[i][j]", size=9, color=NEG, bold=True))

    # Стрілки залежностей (Argon2d vs Argon2i)
    # Попередній блок B[i][j-1]
    p.append(arrow(360, 146, 448, 146, color=NEG, sw=2))
    p.append(text(405, 138, "B[i][j-1]", size=9, color=NEG))

    # Псевдовипадковий референтний блок з іншої смуги
    p.append(arrow(205, 112, 450, 140, color=POS, sw=1.8))
    p.append(text(280, 110, "Референтний блок B[ref_lane][ref_idx]", size=9, color=POS, bold=True))

    # Пояснення знизу
    b_bot, _, _ = textbox(420, 298,
                          "Argon2d: ref_idx залежить від вмісту пам'яті (максимальний TMTO захист)\n"
                          "Argon2i: ref_idx залежить від лічильника (захист від сторонніх каналів кешу)\n"
                          "Argon2id: 1-й прохід - Argon2i (захист кешу), далі - Argon2d (захист TMTO)",
                          size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=740)
    p.append(b_bot)

    render(os.path.join(OUT, "memory-hard-matrix.svg"), W, H, *p,
           title="Двовимірна матриця пам'яті та взаємозв'язки блоків в Argon2")


# ── 4. hash-upgrade-lifecycle: Життєвий цикл лінивого оновлення гешів ────────
def fig_hash_upgrade_lifecycle():
    W, H = 840, 330
    p = []

    # Крок 1: Клієнт шле логін
    p.append(rect(30, 80, 140, 90, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    p.append(text(100, 110, "Клієнт (Вхід)", size=12, color=INK, bold=True))
    p.append(text(100, 130, "user + password", size=10, color=MUTED))
    p.append(text(100, 150, "відкритий TLS", size=9, color=FIELD))

    # Стрілка 1 -> 2
    p.append(arrow(170, 125, 230, 125, color=LINE, sw=1.8))
    p.append(text(200, 115, "1. POST", size=9, color=MUTED))

    # Крок 2: Сервер вичитує старий запис і перевіряє
    p.append(rect(230, 50, 180, 150, fill="#e0f2fe", stroke=NEG, sw=1.8, rx=8))
    p.append(text(320, 75, "Сервер автентифікації", size=12, color=NEG, bold=True))
    p.append(text(320, 98, "Зчитує геш із БД", size=10, color=INK))
    p.append(text(320, 120, "Перевірка пароля:", size=10, color=INK))
    p.append(text(320, 140, "verify(pass, stored_hash)", size=9, color=NEG, bold=True))
    p.append(text(320, 170, "Пароль правильний?", size=10, color=FIELD, bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(410, 125, 470, 125, color=FIELD, sw=2))
    p.append(text(440, 115, "Так", size=10, color=FIELD, bold=True))

    # Крок 3: Перевірка застарілості параметрів (needs_rehash)
    p.append(rect(470, 50, 170, 150, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(555, 75, "needs_rehash()", size=12, color="#d97706", bold=True))
    p.append(text(555, 100, "Чи застарів алгоритм?", size=10, color=INK))
    p.append(text(555, 120, "(напр. bcrypt -> Argon2id)", size=9, color=MUTED))
    p.append(text(555, 145, "Чи зросли ліміти?", size=10, color=INK))
    p.append(text(555, 165, "(m: 32MB -> 64MB)", size=9, color=MUTED))

    # Стрілка 3 -> 4 (якщо застарів)
    p.append(arrow(640, 125, 700, 125, color=FIELD, sw=2))
    p.append(text(670, 115, "Застарів", size=10, color=POS, bold=True))

    # Крок 4: Перерахунок і запис нового гешу
    p.append(rect(700, 50, 115, 150, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(757, 75, "Оновлення", size=11, color=FIELD, bold=True))
    p.append(text(757, 100, "Новий геш", size=10, color=INK))
    p.append(text(757, 120, "Argon2id", size=9, color=FIELD, bold=True))
    p.append(text(757, 145, "UPDATE db", size=10, color=INK))
    p.append(text(757, 170, "у фоні транзакції", size=9, color=MUTED))

    # Внизу: випуск сесії
    p.append(arrow(320, 200, 320, 250, color=FIELD, sw=2))
    p.append(arrow(757, 200, 757, 250, color=FIELD, sw=2))
    p.append(rect(230, 250, 585, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(522, 273, "Випуск сесійного токена (JWT / Session Cookie) для користувача", size=11, color=FIELD, bold=True))
    p.append(text(522, 292, "Користувач не помічає оновлення; база даних поступово мігрує на актуальний алгоритм", size=9, color=MUTED))

    render(os.path.join(OUT, "hash-upgrade-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл прозорого лінивого оновлення гешів під час автентифікації")


if __name__ == "__main__":
    fig_hash_speed_paradox()
    fig_salt_and_rainbow_defense()
    fig_memory_hard_matrix()
    fig_hash_upgrade_lifecycle()
    print("Всі 4 фігури згенеровано успішно.")
