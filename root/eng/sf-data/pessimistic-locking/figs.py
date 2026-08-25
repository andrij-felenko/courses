# -*- coding: utf-8 -*-
"""Фігури теми «Песимістичне блокування». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Двофазне блокування (Strict 2PL) та життєвий цикл транзакції ───────────
def fig_2pl_phases():
    W, H = 1040, 520
    f = []

    f.append(text(520, 30, "Двофазне блокування (2PL та Strict 2PL): фази захоплення та звільнення замків",
                  size=15, bold=True, color=INK))

    # Вісь часу
    f.append(arrow(70, 440, 970, 440, color=LINE, sw=1.8))
    f.append(text(970, 465, "Час (t)", size=12, color=MUTED, anchor="end"))

    # Лінії фаз (вертикальні розділювачі)
    f.append(line(380, 70, 380, 440, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(690, 70, 690, 440, color=MUTED, sw=1.2, dash="4,4"))

    # Заголовки фаз
    b_phase1, _, _ = textbox(225, 80, "ФАЗА ЗРОСТАННЯ (Growing Phase)\n• Захоплення нових замків (Lock Acquisition)\n• Жоден замок НЕ відпускається",
                             size=11, fill="#eff6ff", stroke=NEG, sw=1.5, pad=8, bold=True)
    f.append(b_phase1)

    b_phase2, _, _ = textbox(535, 80, "ТОЧКА БЛОКУВАННЯ (Lock Point)\n• Усі необхідні ресурси захоплено\n• Виконання обчислень та модифікація даних",
                             size=11, fill="#fefce8", stroke="#ca8a04", sw=1.5, pad=8, bold=True)
    f.append(b_phase2)

    b_phase3, _, _ = textbox(835, 80, "ФАЗА СПАДАННЯ (Shrinking Phase)\n• Звільнення замків (Lock Release)\n• Нові замки брати ЗАБОРОНЕНО",
                             size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, pad=8, bold=True)
    f.append(b_phase3)

    # Графік кількості утримуваних замків для Classic 2PL
    f.append(line(100, 400, 380, 220, color=NEG, sw=2.5))
    f.append(line(380, 220, 690, 220, color="#ca8a04", sw=2.5))
    f.append(line(690, 220, 920, 400, color=FIELD, sw=2.5, dash="6,4"))

    f.append(text(230, 290, "Класичний 2PL: поступове скидання замків", size=11, color=NEG, bold=True))
    f.append(text(810, 290, "Ризик каскадних відкатів (Cascading Aborts)", size=10, color=POS, bold=True))

    # Strict 2PL (утримання до COMMIT)
    f.append(line(690, 220, 890, 220, color=POS, sw=2.5))
    f.append(line(890, 220, 890, 400, color=POS, sw=2.5))
    f.append(circle(890, 220, 4, fill=POS, stroke=POS))

    b_strict, _, _ = textbox(810, 185, "STRICT 2PL (Сучасний стандарт СУБД):\nУсі ексклюзивні замки утримуються до COMMIT/ROLLBACK!",
                             size=10, fill="#fef2f2", stroke=POS, sw=1.5, pad=6, bold=True)
    f.append(b_strict)

    # Події на осі
    events = [
        (100, "BEGIN"),
        (200, "SELECT ... FOR SHARE (R1)"),
        (320, "SELECT ... FOR UPDATE (R2)"),
        (535, "UPDATE R2 / Обчислення"),
        (690, "Lock Point"),
        (890, "COMMIT (Всі замки знято)"),
    ]
    for ex, etxt in events:
        f.append(circle(ex, 440, 4, fill=INK, stroke=INK))
        f.append(line(ex, 430, ex, 445, color=INK, sw=1.2))
        f.append(mtext(ex, 465, etxt, size=10, color=INK, bold=True))

    # Вісь Y: Кількість замків
    f.append(arrow(70, 440, 70, 150, color=LINE, sw=1.8))
    f.append(text(55, 160, "Кількість замків", size=11, color=MUTED, anchor="end"))

    render(out("fig-2pl-phases.svg"), W, H, *f,
           title="Двофазне блокування (2PL та Strict 2PL)")


# ── 2. Ієрархія блокувань та замки наміру (Intent Locks) ─────────────────────
def fig_lock_hierarchy_intent():
    W, H = 1040, 560
    f = []

    f.append(text(520, 30, "Ієрархія гранулярності блокувань та замки наміру (Intent Locks: IS / IX / SIX)",
                  size=15, bold=True, color=INK))

    # Дерево ієрархії (Зліва) - без заливки зовнішньої рамки
    f.append(rect(40, 60, 450, 470, fill="none", stroke=LINE, sw=1.2, rx=8))
    f.append(text(265, 88, "Ієрархічна структура ресурсів бази даних", size=13, bold=True, color=INK))

    # Вузол База Даних
    b_db, _, _ = textbox(265, 135, "База даних (Database)\nЗамки: IS, IX, S, X", size=11, fill="#eff6ff", stroke=NEG, sw=1.5, pad=8, bold=True)
    f.append(b_db)

    # Вузол Таблиця
    b_tbl, _, _ = textbox(265, 230, "Таблиця (Relation / Table)\nЗамки: IS, IX, S, SIX, X", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, pad=8, bold=True)
    f.append(b_tbl)
    f.append(arrow(265, 165, 265, 200, color=LINE, sw=1.5))

    # Вузли Сторінки
    b_p1, _, _ = textbox(165, 330, "Сторінка 1 (Page)\nЗамки: IS, IX, S, X", size=10, fill="#ffffff", stroke=LINE, pad=6)
    b_p2, _, _ = textbox(365, 330, "Сторінка 2 (Page)\nЗамки: IS, IX, S, X", size=10, fill="#ffffff", stroke=LINE, pad=6)
    f.append(b_p1); f.append(b_p2)
    f.append(arrow(220, 265, 175, 300, color=LINE, sw=1.2))
    f.append(arrow(310, 265, 355, 300, color=LINE, sw=1.2))

    # Вузли Рядки (Кортежі)
    b_r1, _, _ = textbox(115, 430, "Рядок 1\n(S / X Lock)", size=10, fill="#fee2e2", stroke=POS, sw=1.2, pad=6, bold=True)
    b_r2, _, _ = textbox(215, 430, "Рядок 2\n(S / X Lock)", size=10, fill="#fee2e2", stroke=POS, sw=1.2, pad=6, bold=True)
    b_r3, _, _ = textbox(365, 430, "Рядок 3\n(S / X Lock)", size=10, fill="#fee2e2", stroke=POS, sw=1.2, pad=6, bold=True)
    f.append(b_r1); f.append(b_r2); f.append(b_r3)
    f.append(arrow(150, 360, 125, 400, color=LINE, sw=1.2))
    f.append(arrow(180, 360, 205, 400, color=LINE, sw=1.2))
    f.append(arrow(365, 360, 365, 400, color=LINE, sw=1.2))

    # Пояснення правила протоколу
    b_rule, _, _ = textbox(265, 495, "Протокол наміру: Щоб узяти X-lock на Рядок 1,\nтранзакція мусить спершу отримати IX на Базу, Таблицю і Сторінку!",
                           size=10, fill="#fffbeb", stroke="#d97706", sw=1.2, pad=6, color="#92400e")
    f.append(b_rule)

    # Матриця сумісності замків (Справа) - без заливки зовнішньої рамки
    f.append(rect(510, 60, 490, 470, fill="none", stroke=LINE, sw=1.2, rx=8))
    f.append(text(755, 88, "Матриця сумісності режимів блокувань (Compatibility Matrix)", size=12, bold=True, color=INK))

    headers = ["Режим", "IS", "IX", "S", "SIX", "X"]
    matrix_data = [
        ("IS (Intent Shared)",     ["OK", "OK", "OK", "OK", "Ні"], "#eff6ff"),
        ("IX (Intent Exclusive)",  ["OK", "OK", "Ні", "Ні", "Ні"], "#fff7ed"),
        ("S  (Shared Read)",       ["OK", "Ні", "OK", "Ні", "Ні"], "#f0fdf4"),
        ("SIX (Shared + Intent X)",["OK", "Ні", "Ні", "Ні", "Ні"], "#faf5ff"),
        ("X  (Exclusive Write)",   ["Ні", "Ні", "Ні", "Ні", "Ні"], "#fef2f2"),
    ]

    col_w = [140, 60, 60, 60, 60, 60]
    m_xs = [530]
    for w in col_w:
        m_xs.append(m_xs[-1] + w)

    # Заголовок матриці
    y_m = 120
    f.append(rect(m_xs[0], y_m, m_xs[-1] - m_xs[0], 35, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    for i, h in enumerate(headers):
        cx = (m_xs[i] + m_xs[i+1]) / 2
        f.append(text(cx, y_m + 22, h, size=11, bold=True, color=INK))

    y_cur = y_m + 35
    row_h = 42
    for r_title, cells, r_fill in matrix_data:
        f.append(rect(m_xs[0], y_cur, m_xs[-1] - m_xs[0], row_h, fill=r_fill, stroke=LINE, sw=1, rx=0))
        f.append(text(m_xs[0] + 70, y_cur + 25, r_title, size=10, bold=True, color=INK))
        for c_idx, val in enumerate(cells):
            cx = (m_xs[c_idx+1] + m_xs[c_idx+2]) / 2
            col = FIELD if val == "OK" else POS
            bg = "#dcfce7" if val == "OK" else "#fee2e2"
            b_c, _, _ = textbox(cx, y_cur + 21, val, size=10, pad=4, fill=bg, stroke=col, color=col, bold=True)
            f.append(b_c)
        y_cur += row_h

    b_why, _, _ = textbox(755, 430, "Чому це працює за O(1):\nКоли транзакція хоче заблокувати всю таблицю (LOCK TABLE ... IN EXCLUSIVE MODE),\nрушію не треба сканувати мільйони рядків — достатньо перевірити, чи є IX на таблиці!",
                          size=10, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8, color=INK)
    f.append(b_why)

    render(out("fig-lock-hierarchy-intent.svg"), W, H, *f,
           title="Ієрархія блокувань та матриця сумісності замків наміру")


# ── 3. Взаємне блокування (Deadlock) та Граф очікування (Wait-For Graph) ──────
def fig_deadlock_wait_for_graph():
    W, H = 1040, 520
    f = []

    f.append(text(520, 30, "Анатомія взаємного блокування (Deadlock) та граф очікування (Wait-For Graph)",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Хронологія конфлікту - без заливки зовнішньої рамки
    f.append(rect(40, 60, 460, 430, fill="none", stroke=LINE, sw=1.2, rx=8))
    f.append(text(270, 88, "Послідовність подій у часі (Timeline)", size=13, bold=True, color=INK))

    steps = [
        (135, "t1: Транзакція T1 бере X-lock на Рядок A (id=1)", "#eff6ff", NEG),
        (195, "t2: Транзакція T2 бере X-lock на Рядок B (id=2)", "#fee2e2", POS),
        (255, "t3: T1 запитує X-lock на Рядок B ──► ЧЕКАЄ НА T2!", "#fff7ed", "#ea580c"),
        (315, "t4: T2 запитує X-lock на Рядок A ──► ЧЕКАЄ НА T1!", "#fef2f2", POS),
        (385, "t5: DEADLOCK: T1 чекає на T2, а T2 чекає на T1.\nЖодна транзакція не може рухатись вперед!", "#fee2e2", POS),
    ]
    for y_pos, stxt, sfill, sstroke in steps:
        b_s, _, _ = textbox(270, y_pos, stxt, size=10, fill=sfill, stroke=sstroke, sw=1.2, pad=6, bold=True)
        f.append(b_s)

    f.append(arrow(270, 155, 270, 175, color=MUTED, sw=1.2))
    f.append(arrow(270, 215, 270, 235, color=MUTED, sw=1.2))
    f.append(arrow(270, 275, 270, 295, color=MUTED, sw=1.2))
    f.append(arrow(270, 335, 270, 360, color=POS, sw=1.5))

    # Права колонка: Граф очікування (WFG) - без заливки зовнішньої рамки
    f.append(rect(520, 60, 480, 430, fill="none", stroke=LINE, sw=1.2, rx=8))
    f.append(text(760, 88, "Граф очікування транзакцій (Wait-For Graph)", size=13, bold=True, color=INK))

    # Вузол T1
    b_node_t1, _, _ = textbox(630, 210, "Транзакція T1\n• Утримує: Рядок A\n• Чекає на: Рядок B",
                              size=11, fill="#eff6ff", stroke=NEG, sw=2, pad=10, bold=True)
    f.append(b_node_t1)

    # Вузол T2
    b_node_t2, _, _ = textbox(890, 210, "Транзакція T2\n• Утримує: Рядок B\n• Чекає на: Рядок A",
                              size=11, fill="#fee2e2", stroke=POS, sw=2, pad=10, bold=True)
    f.append(b_node_t2)

    # Стрілка очікування T1 -> T2 (зверху)
    f.append(arrow(710, 185, 810, 185, color=POS, sw=2.5))
    f.append(text(760, 170, "Чекає (Lock B)", size=10, color=POS, bold=True))

    # Стрілка очікування T2 -> T1 (знизу)
    f.append(arrow(810, 235, 710, 235, color=POS, sw=2.5))
    f.append(text(760, 255, "Чекає (Lock A)", size=10, color=POS, bold=True))

    # Виявлення циклу детектором СУБД
    b_detector, _, _ = textbox(760, 340, "Детектор взаємних блокувань (Deadlock Detector):\nФоновий процес СУБД сканує граф WFG кожні deadlock_timeout (1 с).\nВиявлено цикл (Cycle in Directed Graph): T1 ──► T2 ──► T1",
                               size=10, fill="#fffbeb", stroke="#d97706", sw=1.5, pad=8, color="#92400e", bold=True)
    f.append(b_detector)

    b_victim, _, _ = textbox(760, 435, "РІШЕННЯ: Вибір жертви (Victim Selection)\nСУБД примусово перериває T2 з помилкою SQLSTATE 40P01 (deadlock_detected),\nвиконує ROLLBACK і дозволяє T1 успішно завершити транзакцію!",
                             size=10, fill="#dcfce7", stroke=FIELD, sw=1.5, pad=8, color="#166534", bold=True)
    f.append(b_victim)

    render(out("fig-deadlock-wait-for-graph.svg"), W, H, *f,
           title="Анатомія взаємного блокування та граф очікування")


# ── 4. Черга завдань: FOR UPDATE проти SKIP LOCKED ───────────────────────────
def fig_skip_locked_queue():
    W, H = 1040, 550
    f = []

    f.append(text(520, 30, "Конкурентна обробка черги завдань: блокування FOR UPDATE проти SKIP LOCKED",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Класичний FOR UPDATE - без заливки зовнішньої рамки
    f.append(rect(40, 60, 460, 390, fill="none", stroke=POS, sw=1.5, rx=8))
    f.append(text(270, 88, "Стандартний SELECT ... FOR UPDATE", size=13, bold=True, color=POS))

    b_bad_queue, _, _ = textbox(270, 145, "Таблиця черги завдань:\n[Завдання #1 (status=new)]  ──►  Заблоковано Worker 1\n[Завдання #2 (status=new)]  ──►  Вільне\n[Завдання #3 (status=new)]  ──►  Вільне",
                                size=10, fill="#ffffff", stroke=LINE, pad=8)
    f.append(b_bad_queue)

    b_w1_bad, _, _ = textbox(150, 245, "Worker 1\nОбробляє #1\n(Утримує X-lock)", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    b_w2_bad, _, _ = textbox(390, 245, "Worker 2\nSELECT ... FOR UPDATE\nLIMIT 1", size=10, fill="#fee2e2", stroke=POS, pad=6)
    f.append(b_w1_bad); f.append(b_w2_bad)

    f.append(arrow(320, 245, 225, 245, color=POS, sw=2))
    f.append(text(270, 230, "БЛОКУВАННЯ!", size=10, color=POS, bold=True))

    b_bad_res, _, _ = textbox(270, 360, "КАТАСТРОФІЧНИЙ РЕЗУЛЬТАТ:\nWorker 2 зупиняється і чекає на завершення Worker 1,\nхоча завдання #2 та #3 абсолютно вільні!\nЧерга перетворюється на строго однопотокове вузьке горло.",
                              size=10, fill="#ffffff", stroke=POS, sw=1.2, pad=8, color=POS, bold=True)
    f.append(b_bad_res)

    # Права колонка: SELECT ... FOR UPDATE SKIP LOCKED - без заливки зовнішньої рамки
    f.append(rect(540, 60, 460, 390, fill="none", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(770, 88, "Оптимізований FOR UPDATE SKIP LOCKED", size=13, bold=True, color=FIELD))

    b_good_queue, _, _ = textbox(770, 145, "Таблиця черги завдань:\n[Завдання #1 (status=new)]  ──►  Заблоковано Worker 1\n[Завдання #2 (status=new)]  ──►  Заблоковано Worker 2\n[Завдання #3 (status=new)]  ──►  Заблоковано Worker 3",
                                 size=10, fill="#ffffff", stroke=LINE, pad=8)
    f.append(b_good_queue)

    b_w1_good, _, _ = textbox(630, 245, "Worker 1\nЗахопив #1\n(Працює)", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    b_w2_good, _, _ = textbox(770, 245, "Worker 2\nПропустив #1\nЗахопив #2!", size=10, fill="#dcfce7", stroke=FIELD, sw=1.5, pad=6, bold=True)
    b_w3_good, _, _ = textbox(910, 245, "Worker 3\nПропустив #1, #2\nЗахопив #3!", size=10, fill="#dcfce7", stroke=FIELD, sw=1.5, pad=6, bold=True)
    f.append(b_w1_good); f.append(b_w2_good); f.append(b_w3_good)

    f.append(arrow(630, 190, 630, 215, color=NEG, sw=1.5))
    f.append(arrow(770, 190, 770, 215, color=FIELD, sw=1.5))
    f.append(arrow(910, 190, 910, 215, color=FIELD, sw=1.5))

    b_good_res, _, _ = textbox(770, 360, "ІДЕАЛЬНИЙ ПАРАЛЕЛЬНИЙ ПОТІК:\nКожен воркер миттєво бере наступний вільний рядок,\nігноруючи зайняті транзакціями записи.\nНульовий час очікування замків (Zero Lock Contention)!",
                               size=10, fill="#ffffff", stroke=FIELD, sw=1.2, pad=8, color="#166534", bold=True)
    f.append(b_good_res)

    b_bottom_note, _, _ = textbox(520, 490, "Ключове правило: SKIP LOCKED перетворює звичайну таблицю реляційної СУБД на високопродуктивну чергу повідомлень (Message Broker).",
                                  size=10, fill="#eff6ff", stroke=NEG, sw=1.2, pad=6, bold=True)
    f.append(b_bottom_note)

    render(out("fig-skip-locked-queue.svg"), W, H, *f,
           title="Порівняння обробки черги з FOR UPDATE та SKIP LOCKED")


if __name__ == "__main__":
    fig_2pl_phases()
    fig_lock_hierarchy_intent()
    fig_deadlock_wait_for_graph()
    fig_skip_locked_queue()
    print("Всі 4 фігури успішно згенеровано у ./img/")
