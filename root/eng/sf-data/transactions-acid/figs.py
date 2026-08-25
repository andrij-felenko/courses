# -*- coding: utf-8 -*-
"""Фігури теми «Транзакції та гарантії ACID». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Матриця політик буферного пулу (Steal vs No-Steal, Force vs No-Force) ─
def fig_steal_no_force():
    W, H = 1000, 540
    f = []

    # Заголовок матриці та осі
    f.append(text(500, 32, "Матриця взаємодії пам'яті та диска: вибір між швидкістю та складністю відновлення",
                  size=15, bold=True, color=INK))

    # Вісь X: скидання сторінок даних під час Commit (Force vs No-Force)
    f.append(text(370, 75, "FORCE (примусове скидання даних)", size=13, bold=True, color=NEG))
    f.append(text(370, 95, "Commit записує всі змінені сторінки на диск", size=11, color=MUTED))

    f.append(text(740, 75, "NO-FORCE (відкладене скидання даних)", size=13, bold=True, color=FIELD))
    f.append(text(740, 95, "Commit записує лише журнал WAL; сторінки лишаються в RAM", size=11, color=MUTED))

    # Вісь Y: витиснення незафіксованих сторінок (Steal vs No-Steal)
    b_nosteal, _, _ = textbox(110, 200, "NO-STEAL\nБрудні блоки\nнезавершених змін\nне йдуть на диск",
                              size=11, fill="#f8fafc", stroke=MUTED, pad=8, bold=True)
    f.append(b_nosteal)

    b_steal, _, _ = textbox(110, 380, "STEAL\nБуферний пул\nможе скинути блок\nдля звільнення RAM",
                            size=11, fill="#f0fdf4", stroke=FIELD, pad=8, bold=True)
    f.append(b_steal)

    # Розділові лінії квадрантів
    f.append(line(210, 115, 960, 115, color=LINE, sw=1.5))
    f.append(line(210, 290, 960, 290, color=LINE, sw=1.2, dash="4,4"))
    f.append(line(210, 490, 960, 490, color=LINE, sw=1.5))

    f.append(line(210, 115, 210, 490, color=LINE, sw=1.5))
    f.append(line(560, 60, 560, 490, color=LINE, sw=1.5))
    f.append(line(960, 115, 960, 490, color=LINE, sw=1.5))

    # Квадрант 1: No-Steal + Force
    b1, _, _ = textbox(385, 200, "Журнал відновлення НЕ потрібен\n• UNDO не треба: на диску нема брудних даних\n• REDO не треба: всі дані записані до завершення\nЦіна: повільний випадковий I/O на кожен Commit,\nрозмір транзакцій обмежений обсягом RAM",
                       size=11, fill="#f8fafc", stroke=MUTED, sw=1.2, pad=10)
    f.append(b1)

    # Квадрант 2: No-Steal + No-Force
    b2, _, _ = textbox(760, 200, "Потрібен журнал REDO (повтор дій)\n• UNDO не треба: брудні сторінки не потрапляють на диск\n• REDO потрібен: відновлює втрачені з RAM сторінки\nЦіна: обсяг транзакції обмежений доступною RAM",
                       size=11, fill="#f0fdf4", stroke=FIELD, sw=1.2, pad=10)
    f.append(b2)

    # Квадрант 3: Steal + Force
    b3, _, _ = textbox(385, 390, "Потрібен журнал UNDO (скасування дій)\n• UNDO потрібен: відкочує скинуті на диск сторінки\n• REDO не треба: всі сторінки скинуто на Commit\nЦіна: катастрофічне падіння швидкості на Commit",
                       size=11, fill="#fef2f2", stroke=NEG, sw=1.2, pad=10)
    f.append(b3)

    # Квадрант 4: Steal + No-Force (Індустріальний стандарт)
    b4, _, _ = textbox(760, 390, "СТАНДАРТ СУБД (STEAL + NO-FORCE)\nПотрібні обидва журнали: UNDO + REDO (WAL / ARIES)\n• Максимальна швидкість: Commit пише лише лог у кінець файлу\n• Буферний пул повністю автономно керує сторінками в RAM",
                       size=11, fill="#dcfce7", stroke=FIELD, sw=2, pad=12, bold=True)
    f.append(b4)

    render(out("steal-no-force.svg"), W, H, *f,
           title="Матриця стратегій керування сторінками буферного пулу")


# ── 2. Порядок запису у WAL та на сторінки даних (WAL Invariants) ────────────
def fig_wal_write_order():
    W, H = 960, 480
    f = []

    f.append(text(480, 30, "Послідовність операцій запису: непорушні правила WAL (Undo Rule та Redo Rule)",
                  size=15, bold=True, color=INK))

    # Горизонтальні рівні системи
    f.append(rect(40, 55, 880, 140, fill="#eff6ff", stroke=NEG, sw=1.2, rx=8))
    f.append(text(60, 78, "ОПЕРАТИВНА ПАМ'ЯТЬ (DRAM) — Буферний пул сторінок та WAL Buffer",
                  size=12, bold=True, color=NEG, anchor="start"))

    f.append(rect(40, 240, 880, 200, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(60, 263, "ЕНЕРГОНЕЗАЛЕЖНИЙ НАКОПИЧУВАЧ (NVMe / SSD / HDD) — Файли бази та WAL",
                  size=12, bold=True, color=INK, anchor="start"))

    # Крок 1: Зміна сторінки в RAM
    b1, _, _ = textbox(200, 135, "1. Модифікація в RAM\nСторінка X (PageLSN = 42)\nЗапис логу у WAL Buffer",
                       size=11, fill="#ffffff", stroke=LINE, sw=1.2, pad=8)
    f.append(b1)

    # Крок 2: Скидання логу на диск (Undo Rule & Redo Rule)
    b2, _, _ = textbox(450, 350, "2. fsync() WAL-блоку на диск\nЗапис LSN=42 надійно на диску.\nТранзакція отримує COMMIT.",
                       size=11, fill="#dcfce7", stroke=FIELD, sw=2, pad=10, bold=True)
    f.append(b2)

    # Крок 3: Ледаче скидання сторінки даних
    b3, _, _ = textbox(770, 350, "3. Асинхронний Checkpoint\nБрудна сторінка X скидається\nу файл таблиці (тільки після WAL!)",
                       size=11, fill="#ffffff", stroke=LINE, sw=1.2, pad=10)
    f.append(b3)

    # Стрілки між кроками
    f.append(arrow(295, 135, 360, 350, color=FIELD, sw=2))
    b_ur, _, _ = textbox(305, 220, "Undo Rule:\nЛог ПЕРЕД\nданими",
                         size=10, fill="#ffffff", stroke=FIELD, pad=4, bold=True)
    f.append(b_ur)

    f.append(arrow(555, 350, 660, 350, color=LINE, sw=1.8))
    b_bg, _, _ = textbox(608, 325, "Фоновий\nзапис",
                         size=10, fill="#ffffff", stroke=MUTED, pad=4)
    f.append(b_bg)

    # Раптове знеструмлення
    b_crash, _, _ = textbox(680, 135, "Раптове знеструмлення або збій ядра\nDRAM втрачено, але лог LSN=42 на диску →\nрушій надійно відновить стан через REDO",
                            size=10, fill="#fee2e2", stroke=POS, sw=1.2, pad=8)
    f.append(b_crash)

    render(out("wal-write-order.svg"), W, H, *f,
           title="Порядок запису WAL та сторінок даних")


# ── 3. Граф станів транзакції (Transaction Lifecycle) ────────────────────────
def fig_acid_lifecycle():
    W, H = 960, 400
    f = []

    f.append(text(480, 32, "Життєвий цикл транзакції: переходи між станами виконання та відновлення",
                  size=15, bold=True, color=INK))

    # Стан 1: ACTIVE
    b_act, _, _ = textbox(150, 150, "ACTIVE\n(Активна)\nВиконання операцій\nчитання і запису",
                          size=12, fill="#eff6ff", stroke=NEG, sw=1.8, pad=12, bold=True)
    f.append(b_act)

    # Стан 2: PARTIALLY COMMITTED
    b_pcom, _, _ = textbox(480, 150, "PARTIALLY COMMITTED\n(Частково зафіксована)\nОстання операція виконана,\nйде fsync() логу на диск",
                           size=12, fill="#fef9c3", stroke="#ca8a04", sw=1.8, pad=12, bold=True)
    f.append(b_pcom)

    # Стан 3: COMMITTED
    b_com, _, _ = textbox(810, 150, "COMMITTED\n(Зафіксована)\nЗміни гарантовано на диску,\nклієнт отримує успіх",
                          size=12, fill="#dcfce7", stroke=FIELD, sw=2, pad=12, bold=True)
    f.append(b_com)

    # Стан 4: FAILED
    b_fail, _, _ = textbox(315, 300, "FAILED (Збійна)\nПомилка інваріанта, збій,\nдедлок або явний ROLLBACK",
                           size=12, fill="#fee2e2", stroke=POS, sw=1.8, pad=12, bold=True)
    f.append(b_fail)

    # Стан 5: ABORTED
    b_abort, _, _ = textbox(680, 300, "ABORTED (Відкочена)\nЖурнал UNDO застосовано,\nстан повернуто до початку",
                            size=12, fill="#f1f5f9", stroke=MUTED, sw=1.8, pad=12, bold=True)
    f.append(b_abort)

    # Стрілки переходів
    # ACTIVE -> PARTIALLY COMMITTED
    f.append(arrow(240, 150, 360, 150, color=FIELD, sw=1.8))
    f.append(text(300, 138, "Останній запит", size=10, color=MUTED))

    # PARTIALLY COMMITTED -> COMMITTED
    f.append(arrow(600, 150, 700, 150, color=FIELD, sw=2))
    f.append(text(650, 138, "fsync() успішний", size=10, bold=True, color=FIELD))

    # ACTIVE -> FAILED
    f.append(arrow(180, 205, 260, 260, color=POS, sw=1.8))
    f.append(text(190, 245, "Помилка / abort", size=10, color=POS))

    # PARTIALLY COMMITTED -> FAILED
    f.append(arrow(440, 205, 360, 260, color=POS, sw=1.8))
    f.append(text(430, 245, "Збій I/O логу", size=10, color=POS))

    # FAILED -> ABORTED
    f.append(arrow(415, 300, 580, 300, color=LINE, sw=1.8))
    f.append(text(495, 288, "Застосування UNDO", size=10, color=MUTED))

    render(out("acid-lifecycle.svg"), W, H, *f,
           title="Діаграма станів виконання транзакції")


# ── 4. Аномалії ізоляції та конфлікти доступу (Isolation Anomalies) ───────────
def fig_isolation_anomalies():
    W, H = 960, 480
    f = []

    f.append(text(480, 32, "Конфлікти паралельного доступу: втрачене оновлення (Lost Update) без ізоляції",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Транзакція 1
    f.append(text(220, 75, "Транзакція 1 (T1: +100 грн)", size=14, bold=True, color=NEG))
    # Права колонка: Транзакція 2
    f.append(text(740, 75, "Транзакція 2 (T2: +200 грн)", size=14, bold=True, color=POS))
    # Центральна колонка: Спільний стан на диску/в пам'яті
    f.append(text(480, 75, "База даних (Рахунок A)", size=14, bold=True, color=INK))

    # Вісь часу вниз
    f.append(arrow(80, 95, 80, 440, color=MUTED, sw=1.5))
    f.append(text(65, 260, "Час", size=12, color=MUTED))

    # Час t0: Початковий стан
    b_init, _, _ = textbox(480, 115, "Початковий баланс A = 500 грн", size=12, fill="#f1f5f9", stroke=LINE, sw=1.2, pad=8)
    f.append(b_init)

    # Час t1: T1 читає A
    b_t1_r, _, _ = textbox(220, 165, "t1: Читає A = 500 грн\n(обчислює 500 + 100 = 600)", size=11, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8)
    f.append(b_t1_r)
    f.append(line(310, 165, 410, 115, color=NEG, sw=1.2, dash="3,3"))

    # Час t2: T2 читає той самий A (ще не змінений T1)
    b_t2_r, _, _ = textbox(740, 215, "t2: Читає A = 500 грн\n(обчислює 500 + 200 = 700)", size=11, fill="#fee2e2", stroke=POS, sw=1.2, pad=8)
    f.append(b_t2_r)
    f.append(line(650, 215, 550, 115, color=POS, sw=1.2, dash="3,3"))

    # Час t3: T1 записує 600 і фіксується
    b_t1_w, _, _ = textbox(220, 280, "t3: Записує A = 600 грн\nCOMMIT (успіх)", size=11, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8)
    f.append(b_t1_w)
    f.append(arrow(310, 280, 410, 280, color=NEG, sw=1.5))
    b_mid, _, _ = textbox(480, 280, "Баланс A = 600 грн", size=12, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8)
    f.append(b_mid)

    # Час t4: T2 записує 700 і перетирає запис T1!
    b_t2_w, _, _ = textbox(740, 360, "t4: Записує A = 700 грн\nCOMMIT (успіх)", size=11, fill="#fee2e2", stroke=POS, sw=1.2, pad=8)
    f.append(b_t2_w)
    f.append(arrow(650, 360, 550, 360, color=POS, sw=1.8))
    b_final, _, _ = textbox(480, 360, "Кінцевий баланс A = 700 грн\n(Замість 800 грн!)", size=12, fill="#fef2f2", stroke=POS, sw=2, pad=10, bold=True)
    f.append(b_final)

    # Результат аномалії
    b_res, _, _ = textbox(480, 440, "АНОМАЛІЯ: Зміна від T1 повністю втрачена (+100 грн зникло).\nІзоляція через 2PL або MVCC змушує T2 зачекати або відхиляє її конфліктний запис.",
                          size=11, fill="#fef2f2", stroke=POS, sw=1.2, pad=8)
    f.append(b_res)

    render(out("isolation-anomalies.svg"), W, H, *f,
           title="Аномалія втраченого оновлення через відсутність ізоляції")


if __name__ == "__main__":
    fig_steal_no_force()
    fig_wal_write_order()
    fig_acid_lifecycle()
    fig_isolation_anomalies()
    print("Всі 4 фігури успішно згенеровано у ./img/")
