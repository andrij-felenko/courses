# -*- coding: utf-8 -*-
"""Фігури для теми «NULL і тризначна логіка SQL» (root/eng/sf-data/sql-null-three-valued)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig1_sentinel_vs_null():
    """fig1-sentinel-vs-null.svg: Сигнальні значення (Sentinel) проти бітової карти NULL."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Сигнальні значення (Sentinel) проти явного маркера NULL", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: Сигнальні значення (Дефект)
    frags.append(rect(30, 60, 370, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(215, 85, "Підхід 1: Сигнальні значення (Sentinel)", size=13, bold=True, color="#991b1b"))

    b_s1, _, _ = textbox(215, 130, "Поле Age: -1 або 999\nПоле Salary: -9999.00\nПоле Date: '9999-12-31'", size=11, pad=8, fill="#ffffff", stroke=RED_S, min_w=330)
    frags.append(b_s1)

    b_s2, _, _ = textbox(215, 230, "Катастрофічні наслідки для аналітики:\n• AVG(Salary) враховує -9999 → спотворено\n• WHERE Age > 60 включає 999 → помилка\n• Змішування домену даних із метаданими", size=10.5, pad=8, fill="#ffffff", stroke=RED_S, min_w=330)
    frags.append(b_s2)

    b_s3, _, _ = textbox(215, 335, "Залежність від довільних конвенцій,\nруйнування агрегатів та діапазонних вибірок", size=10, pad=6, fill=RED_F, stroke=RED_S, color="#991b1b", bold=True, min_w=330)
    frags.append(b_s3)

    # Права колонка: Метадані NULL та бітова карта (Рішення)
    frags.append(rect(440, 60, 370, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(625, 85, "Підхід 2: Явний реляційний маркер NULL", size=13, bold=True, color="#166534"))

    b_n1, _, _ = textbox(625, 130, "Значення відсутнє на рівні метаданих\nNull Bitmap у заголовку кортежу: 1 біт на колонку\nКорисне навантаження (payload) займає 0 байтів", size=11, pad=8, fill="#ffffff", stroke=GREEN_S, min_w=330)
    frags.append(b_n1)

    b_n2, _, _ = textbox(625, 230, "Математично коректна поведінка агрегатів:\n• AVG(Salary) ігнорує NULL → чисте середнє\n• Домен значень лишається непорушеним\n• Введення тризначної логіки (3VL: T, F, U)", size=10.5, pad=8, fill="#ffffff", stroke=GREEN_S, min_w=330)
    frags.append(b_n2)

    b_n3, _, _ = textbox(625, 335, "Чистота типів даних та збереження\nматематичного змісту реляційного відношення", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, color="#166534", bold=True, min_w=330)
    frags.append(b_n3)

    render(os.path.join(IMG, "fig1-sentinel-vs-null.svg"), W, H, *frags)

def fig2_three_valued_logic_lattice():
    """fig2-three-valued-logic-lattice.svg: Решітка тризначної логіки Клини (3VL)."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Решітка тризначної логіки Клини (3VL) та обчислення операторів", size=15, bold=True, color="#1e293b"))

    # Решітка (Ліва частина)
    frags.append(rect(30, 60, 280, 370, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=8))
    frags.append(text(170, 85, "Частковий порядок істинності", size=12, bold=True, color="#1e293b"))

    b_true, _, _ = textbox(170, 130, "TRUE (1)\nНайвищий ступінь", size=11, pad=6, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=180)
    b_unk, _, _ = textbox(170, 230, "UNKNOWN (1/2)\nНевизначений стан", size=11, pad=6, fill=AMBER_F, stroke=AMBER_S, bold=True, min_w=180)
    b_false, _, _ = textbox(170, 330, "FALSE (0)\nНайнижчий ступінь", size=11, pad=6, fill=RED_F, stroke=RED_S, bold=True, min_w=180)
    frags.extend([b_true, b_unk, b_false])

    frags.append(arrow(170, 205, 170, 155, color=GREEN_S, sw=2))
    frags.append(arrow(170, 305, 170, 255, color=AMBER_S, sw=2))
    frags.append(text(170, 400, "Впорядкування: FALSE < UNKNOWN < TRUE", size=10, bold=True, color="#475569"))

    # Формули та закони (Права частина)
    frags.append(rect(330, 60, 480, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(570, 85, "Алгебраїчні правила 3VL (Клини)", size=13, bold=True, color="#1e293b"))

    b_ops, _, _ = textbox(570, 150, "Оператори мінімуму, максимуму та доповнення:\n• A AND B = min(val(A), val(B))\n• A OR B  = max(val(A), val(B))\n• NOT A   = 1 - val(A)", size=11, pad=8, fill=BLUE_F, stroke=BLUE_S, min_w=440)
    frags.append(b_ops)

    b_laws, _, _ = textbox(570, 260, "Ключові наслідки для SQL:\n• UNKNOWN AND FALSE = FALSE  (бо min(1/2, 0) = 0)\n• UNKNOWN OR TRUE   = TRUE   (бо max(1/2, 1) = 1)\n• UNKNOWN AND TRUE  = UNKNOWN (бо min(1/2, 1) = 1/2)\n• NOT UNKNOWN       = UNKNOWN (бо 1 - 1/2 = 1/2)", size=10.5, pad=8, fill=PURPLE_F, stroke=PURPLE_S, min_w=440)
    frags.append(b_laws)

    b_trap, _, _ = textbox(570, 370, "Руйнування закону виключеного третього:\nUNKNOWN OR NOT UNKNOWN = UNKNOWN (не TRUE!)\np OR NOT p не є тавтологією в SQL!", size=10.5, pad=8, fill=RED_F, stroke=RED_S, bold=True, min_w=440)
    frags.append(b_trap)

    render(os.path.join(IMG, "fig2-three-valued-logic-lattice.svg"), W, H, *frags)

def fig3_tuple_null_bitmap_layout():
    """fig3-tuple-null-bitmap-layout.svg: Фізичне представлення NULL у сторінці та кортежі."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Фізичне розміщення NULL у заголовку кортежу (PostgreSQL Heap Tuple)", size=15, bold=True, color="#1e293b"))

    # Заголовок кортежу (HeapTupleHeaderData)
    frags.append(rect(40, 70, 760, 70, fill="#334155", stroke="#1e293b", sw=1.5, rx=6))
    frags.append(text(420, 95, "Заголовок кортежу (HeapTupleHeaderData, 23 байти фіксованого розміру)", size=12, bold=True, color="#ffffff"))

    # Поля заголовка
    frags.append(rect(50, 105, 140, 26, fill="#475569", stroke="#1e293b", sw=1, rx=3))
    frags.append(text(120, 122, "t_xmin / t_xmax", size=10, color="#ffffff"))

    frags.append(rect(200, 105, 110, 26, fill="#475569", stroke="#1e293b", sw=1, rx=3))
    frags.append(text(255, 122, "t_cid / t_ctid", size=10, color="#ffffff"))

    frags.append(rect(320, 105, 160, 26, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=3))
    frags.append(text(400, 122, "t_infomask (HEAP_HASNULL)", size=9.5, bold=True, color="#9a3412"))

    frags.append(rect(490, 105, 130, 26, fill="#475569", stroke="#1e293b", sw=1, rx=3))
    frags.append(text(555, 122, "t_hoff (зсув даних)", size=10, color="#ffffff"))

    frags.append(rect(630, 105, 160, 26, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=3))
    frags.append(text(710, 122, "t_bits[] (Null Bitmap)", size=10, bold=True, color="#166534"))

    # Бітова карта NULL детально
    frags.append(rect(40, 160, 760, 110, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=6))
    frags.append(text(420, 185, "Деталізація Null Bitmap: 1 біт на кожну колонку схеми таблиці", size=12, bold=True, color="#1e293b"))

    cols = [
        ("Col 1 (ID)", "Біт = 1 (NOT NULL)", GREEN_F, GREEN_S, 115),
        ("Col 2 (Name)", "Біт = 1 (NOT NULL)", GREEN_F, GREEN_S, 270),
        ("Col 3 (Email)", "Біт = 0 (IS NULL)", RED_F, RED_S, 425),
        ("Col 4 (Phone)", "Біт = 0 (IS NULL)", RED_F, RED_S, 580),
        ("Col 5 (Created)", "Біт = 1 (NOT NULL)", GREEN_F, GREEN_S, 725),
    ]

    for title, desc, f_clr, s_clr, cx in cols:
        b_col, _, _ = textbox(cx, 230, title + "\n" + desc, size=9.5, pad=5, fill=f_clr, stroke=s_clr, bold=True, min_w=135)
        frags.append(b_col)

    # Корисні дані кортежу (Payload Data)
    frags.append(rect(40, 290, 760, 120, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(420, 315, "Фізичні байти корисного навантаження кортежу (Payload)", size=12, bold=True, color="#1e293b"))

    payloads = [
        ("ID = 42\n(4 байти)", GREEN_F, GREEN_S, 140),
        ("Name = 'Тарас'\n(10 байтів з varlena)", GREEN_F, GREEN_S, 330),
        ("Email = NULL\n(0 байтів у payload!)", RED_F, RED_S, 520),
        ("Created = 2026-08-25\n(8 байтів timestamp)", GREEN_F, GREEN_S, 700),
    ]

    for title, f_clr, s_clr, cx in payloads:
        b_pay, _, _ = textbox(cx, 365, title, size=10, pad=6, fill=f_clr, stroke=s_clr, bold=True, min_w=155)
        frags.append(b_pay)

    render(os.path.join(IMG, "fig3-tuple-null-bitmap-layout.svg"), W, H, *frags)

def fig4_predicate_acceptance_trap():
    """fig4-predicate-acceptance-trap.svg: Пастка предикатів WHERE проти CHECK."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Пастка обробки UNKNOWN: фільтрація WHERE проти обмежень CHECK", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: WHERE / HAVING / ON
    frags.append(rect(30, 60, 370, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(215, 85, "WHERE / HAVING / ON: Фільтрація", size=13, bold=True, color="#1e40af"))

    b_w1, _, _ = textbox(215, 130, "Правило: Accept ONLY TRUE\n(Пропускати кортеж лише якщо результат строго TRUE)", size=10.5, pad=6, fill="#ffffff", stroke=BLUE_S, bold=True, min_w=330)
    frags.append(b_w1)

    b_w2, _, _ = textbox(215, 220, "Оцінка для кортежу з Age = NULL:\n• WHERE Age > 18 → UNKNOWN → ВІДКИДАЄТЬСЯ\n• WHERE NOT (Age > 18) → UNKNOWN → ВІДКИДАЄТЬСЯ\n• Кортеж не потрапляє у вибірку в ОБОХ випадках!", size=10, pad=8, fill="#ffffff", stroke=BLUE_S, min_w=330)
    frags.append(b_w2)

    b_w3, _, _ = textbox(215, 335, "Рядки з UNKNOWN тихо зникають\nіз результатів запиту", size=10.5, pad=6, fill=BLUE_F, stroke=BLUE_S, color="#1e40af", bold=True, min_w=330)
    frags.append(b_w3)

    # Права колонка: CHECK constraints
    frags.append(rect(440, 60, 370, 330, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(625, 85, "CHECK Constraint: Цілісність", size=13, bold=True, color="#9a3412"))

    b_c1, _, _ = textbox(625, 130, "Правило: Reject ONLY FALSE\n(Відхиляти вставку лише якщо результат строго FALSE)", size=10.5, pad=6, fill="#ffffff", stroke=AMBER_S, bold=True, min_w=330)
    frags.append(b_c1)

    b_c2, _, _ = textbox(625, 220, "Оцінка для вставки Salary = NULL:\n• CHECK (Salary > 0) → UNKNOWN → ДОЗВОЛЕНО!\n• CHECK (Salary > 0 AND Salary < 1000) → UNKNOWN → ДОЗВОЛЕНО!\n• Рядок успішно вставляється в таблицю!", size=10, pad=8, fill="#ffffff", stroke=AMBER_S, min_w=330)
    frags.append(b_c2)

    b_c3, _, _ = textbox(625, 335, "CHECK без NOT NULL не захищає від NULL!\nКритичне джерело порушення інваріантів", size=10.5, pad=6, fill=AMBER_F, stroke=AMBER_S, color="#9a3412", bold=True, min_w=330)
    frags.append(b_c3)

    render(os.path.join(IMG, "fig4-predicate-acceptance-trap.svg"), W, H, *frags)

def fig5_not_in_null_trap():
    """fig5-not-in-null-trap.svg: Пастка NOT IN з NULL у підзапиті."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Покрокове розгортання та крах виразу NOT IN за наявності NULL", size=15, bold=True, color="#1e293b"))

    # Вираз запиту
    b_query, _, _ = textbox(420, 80, "Запит: SELECT * FROM items WHERE id NOT IN (10, 20, NULL);", size=12, pad=8, fill=GRAY_F, stroke=GRAY_S, bold=True, min_w=740)
    frags.append(b_query)

    # Крок 1: Еквівалентне розгортання в кон'юнкцію
    b_step1, _, _ = textbox(420, 160, "Крок 1: За стандартом SQL x NOT IN (a, b, c) розгортається в:\n(id <> 10) AND (id <> 20) AND (id <> NULL)", size=11, pad=8, fill=BLUE_F, stroke=BLUE_S, min_w=740)
    frags.append(b_step1)

    # Крок 2: Оцінка для будь-якого id (наприклад, id = 5)
    b_step2, _, _ = textbox(420, 250, "Крок 2: Оцінка порівнянь для довільного кортежу (нехай id = 5):\n(5 <> 10) → TRUE\n(5 <> 20) → TRUE\n(5 <> NULL) → UNKNOWN", size=11, pad=8, fill=PURPLE_F, stroke=PURPLE_S, min_w=740)
    frags.append(b_step2)

    # Крок 3: Підсумок кон'юнкції та фільтр WHERE
    b_step3, _, _ = textbox(420, 350, "Крок 3: Обчислення кінцевого предиката:\nTRUE AND TRUE AND UNKNOWN = UNKNOWN\nОскільки WHERE вимагає строго TRUE — жоден рядок таблиці не повертається!\n(Порожній результат для всієї вибірки, хоча 5 не дорівнює ні 10, ні 20)", size=10.5, pad=8, fill=RED_F, stroke=RED_S, bold=True, min_w=740)
    frags.append(b_step3)

    render(os.path.join(IMG, "fig5-not-in-null-trap.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_sentinel_vs_null()
    fig2_three_valued_logic_lattice()
    fig3_tuple_null_bitmap_layout()
    fig4_predicate_acceptance_trap()
    fig5_not_in_null_trap()
    print("Всі фігури успішно згенеровано.")
