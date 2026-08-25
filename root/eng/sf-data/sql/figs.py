# -*- coding: utf-8 -*-
"""Фігури для теми «SQL: мова запитів до реляційних баз» (root/eng/sf-data/sql)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig1_sql_execution_pipeline():
    """fig1-sql-execution-pipeline.svg: Конвеєр виконання SQL-запиту в реляційному рушії."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Конвеєр обробки та виконання SQL-запиту в СУБД", size=16, bold=True, color="#1e293b"))

    # Фаза 1: Текст запиту
    b_sql, _, _ = textbox(110, 95, "SQL-текст запиту\nSELECT name, sum(val)\nFROM orders JOIN users...\nWHERE status = 'active'", size=10, pad=8, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=170)
    frags.append(b_sql)

    # Стрілка 1 -> 2
    frags.append(arrow(200, 95, 230, 95, color=BLUE_S, sw=1.8))

    # Фаза 2: Синтаксичний парсер і AST
    b_parser, _, _ = textbox(330, 95, "Лексичний і синтаксичний парсер\nПеревірка граматики SQL\nПобудова абстрактного дерева (AST)", size=10, pad=8, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=170)
    frags.append(b_parser)

    # Стрілка 2 -> 3
    frags.append(arrow(430, 95, 455, 95, color=TEAL_S, sw=1.8))

    # Фаза 3: Семантичний аналізатор і каталог
    b_sem, _, _ = textbox(555, 95, "Семантичний аналізатор\nПеревірка типів і схем у Каталозі\nФормування логічного дерева", size=10, pad=8, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=170)
    frags.append(b_sem)

    # Каталог метаданих (допоміжний блок праворуч)
    b_cat, _, _ = textbox(735, 95, "Системний каталог\nСхеми таблиць\nТипи колонок\nСтатистика даних", size=9, pad=6, fill=GRAY_F, stroke=GRAY_S, bold=True, min_w=130)
    frags.append(b_cat)
    frags.append(arrow(650, 95, 665, 95, color=GRAY_S, sw=1.5))

    # Стрілка вниз до оптимізатора
    frags.append(arrow(555, 140, 555, 185, color=PURPLE_S, sw=1.8))

    # Фаза 4: Вартісний оптимізатор запитів (CBO)
    frags.append(rect(40, 190, 760, 125, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(420, 212, "Вартісний оптимізатор запитів (Cost-Based Optimizer, CBO)", size=13, bold=True, color="#9a3412"))
    
    b_cbo1, _, _ = textbox(165, 262, "Алгебраїчний перепис:\nPushdown фільтрів (WHERE)\nУсунення зайвих JOIN", size=9.5, pad=6, fill="#ffffff", stroke=AMBER_S, bold=False, min_w=210)
    b_cbo2, _, _ = textbox(420, 262, "Вибір фізичних операторів:\nIndex Scan vs Seq Scan\nHash Join vs Merge Join", size=9.5, pad=6, fill="#ffffff", stroke=AMBER_S, bold=False, min_w=210)
    b_cbo3, _, _ = textbox(675, 262, "Оцінка вартості (Cost Model):\nВартість CPU: перевірка умов\nВартість I/O: читання блоків", size=9.5, pad=6, fill="#ffffff", stroke=AMBER_S, bold=False, min_w=210)
    frags.extend([b_cbo1, b_cbo2, b_cbo3])

    # Стрілка від CBO до виконання
    frags.append(arrow(420, 320, 420, 350, color=AMBER_S, sw=2.0))

    # Фаза 5: Рушій виконання (Execution Engine)
    frags.append(rect(40, 355, 760, 95, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(420, 375, "Фізичний план виконання та ітераторна модель Вулкан (Volcano Model)", size=13, bold=True, color="#166534"))

    b_ex1, _, _ = textbox(165, 412, "Оператор Aggregate\nПідсумовування значень", size=9.5, pad=5, fill="#ffffff", stroke=GREEN_S, min_w=200)
    b_ex2, _, _ = textbox(420, 412, "Оператор Hash Join\nХеш-таблиця в оперативній пам'яті", size=9.5, pad=5, fill="#ffffff", stroke=GREEN_S, min_w=200)
    b_ex3, _, _ = textbox(675, 412, "Оператор Index Scan (B-Tree)\nПошук за індексом status", size=9.5, pad=5, fill="#ffffff", stroke=GREEN_S, min_w=200)
    frags.extend([b_ex1, b_ex2, b_ex3])

    frags.append(arrow(310, 412, 275, 412, color=GREEN_S, sw=1.5))
    frags.append(arrow(565, 412, 530, 412, color=GREEN_S, sw=1.5))

    render(os.path.join(IMG, "fig1-sql-execution-pipeline.svg"), W, H, *frags)

def fig2_logical_query_order():
    """fig2-logical-query-order.svg: Логічний порядок обчислення виразів SQL проти синтаксичного."""
    W, H = 840, 500
    frags = []

    frags.append(rect(10, 10, 820, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Логічний порядок виконання секцій SQL (Dataflow Lifecycle)", size=16, bold=True, color="#1e293b"))

    steps = [
        ("1. FROM & JOIN / ON", "Формування робочого відношення, з'єднання таблиць за предикатами", BLUE_F, BLUE_S, 55),
        ("2. WHERE", "Фільтрація кортежів базових таблиць до будь-якої агрегації", TEAL_F, TEAL_S, 100),
        ("3. GROUP BY", "Розбиття множини кортежів на неперетинні групи за ключами", PURPLE_F, PURPLE_S, 145),
        ("4. HAVING", "Фільтрація згрупованих кортежів за результатами агрегатних функцій", AMBER_F, AMBER_S, 190),
        ("5. WINDOW (OVER)", "Обчислення віконних функцій над партиціями без згортання рядків", GREEN_F, GREEN_S, 235),
        ("6. SELECT", "Проекція атрибутів, обчислення виразів і призначення псевдонімів", BLUE_F, BLUE_S, 280),
        ("7. DISTINCT", "Вилучення дублікатів кортежів з результуючої множини", GRAY_F, GRAY_S, 325),
        ("8. UNION / INTERSECT", "Множинні операції над сумісними за схемою результуючими наборами", PURPLE_F, PURPLE_S, 370),
        ("9. ORDER BY", "Сортування остаточної результуючої множини за виразами або псевдонімами", AMBER_F, AMBER_S, 415),
    ]

    for title, desc, f_clr, s_clr, y in steps:
        frags.append(rect(40, y, 760, 36, fill=f_clr, stroke=s_clr, sw=1.3, rx=5))
        frags.append(text(150, y + 22, title, size=11, bold=True, color="#1e293b", anchor="middle"))
        frags.append(text(480, y + 22, desc, size=10, color="#334155", anchor="middle"))
        if y < 415:
            frags.append(arrow(420, y + 36, 420, y + 44, color="#94a3b8", sw=1.5))

    frags.append(text(420, 470, "Псевдоніми з SELECT не доступні у WHERE чи GROUP BY, бо обчислюються пізніше.", size=11, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig2-logical-query-order.svg"), W, H, *frags)

def fig3_join_types_and_algorithms():
    """fig3-join-types-and-algorithms.svg: Логічні типи операцій JOIN та фізичні алгоритми виконання."""
    W, H = 840, 520
    frags = []

    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Операції з'єднання: Логічна семантика та фізичні алгоритми", size=16, bold=True, color="#1e293b"))

    # Блок 1: Логічні JOIN (Верхня половина)
    frags.append(text(420, 64, "Логічні різновиди JOIN (Множинна семантика)", size=12, bold=True, color="#475569"))

    j_types = [
        ("INNER JOIN", "Лише кортежі зі збігом\nключа в обох таблицях", BLUE_F, BLUE_S, 130),
        ("LEFT JOIN", "Усі кортежі зліва;\nсправа NULL при незбігу", TEAL_F, TEAL_S, 320),
        ("FULL JOIN", "Усі кортежі з обох сторін;\nNULL для відсутніх пар", PURPLE_F, PURPLE_S, 510),
        ("SEMI / ANTI JOIN", "Перевірка існування (EXISTS)\nабо відсутності (NOT EXISTS)", AMBER_F, AMBER_S, 700),
    ]

    for name, desc, f_clr, s_clr, cx in j_types:
        b_j, _, _ = textbox(cx, 115, name + "\n" + desc, size=9.5, pad=6, fill=f_clr, stroke=s_clr, bold=True, min_w=170)
        frags.append(b_j)

    # Розділювальна лінія
    frags.append(line(40, 175, 800, 175, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Блок 2: Фізичні алгоритми JOIN (Нижня половина)
    frags.append(text(420, 200, "Фізичні алгоритми виконання JOIN у рушії СУБД", size=12, bold=True, color="#475569"))

    # 3 картки алгоритмів, рознесені по ширині: cx = 150, 420, 690, ширина кожної ~240px
    b_nlj, _, _ = textbox(150, 330, "Nested Loop Join (NLJ)\n\nСкладність: O(M · N) без індексу\nЗ індексом: O(M · log N)\n\nЗовнішній цикл сканує R,\nвнутрішній шукає збіги в S.\nОптимальний для малих таблиць\nабо за наявності B-Tree індексу.", size=9, pad=8, fill=BLUE_F, stroke=BLUE_S, bold=False, min_w=240)
    
    b_hj, _, _ = textbox(420, 330, "Hash Join (HJ)\n\nСкладність: O(M + N)\nПам'ять: O(min(M, N))\n\nФаза Build: будує хеш-таблицю\nв оперативній пам'яті для R.\nФаза Probe: сканує S і шукає\nвідповідні хеш-кошики.", size=9, pad=8, fill=GREEN_F, stroke=GREEN_S, bold=False, min_w=240)
    
    b_smj, _, _ = textbox(690, 330, "Sort-Merge Join (SMJ)\n\nСкладність: O(M log M + N log N)\nБез сортування: O(M + N)\n\nОбидва набори сортуються за\nключем, далі йде злиття.\nНайкращий для кластерних\nіндексів або великих обсягів.", size=9, pad=8, fill=PURPLE_F, stroke=PURPLE_S, bold=False, min_w=240)

    frags.extend([b_nlj, b_hj, b_smj])

    frags.append(text(420, 485, "Оптимізатор обирає алгоритм на основі статистики кардинальності таблиць та наявності індексів.", size=10, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig3-join-types-and-algorithms.svg"), W, H, *frags)

def fig4_window_vs_groupby():
    """fig4-window-vs-groupby.svg: Порівняння механізму агрегації GROUP BY та віконних функцій OVER."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Трансформація кардинальності: GROUP BY проти віконних функцій (OVER)", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: GROUP BY (N -> K)
    frags.append(rect(40, 60, 360, 340, fill=AMBER_F, stroke=AMBER_S, sw=1.3, rx=8))
    frags.append(text(220, 85, "Агрегація: GROUP BY (Згортання рядків)", size=12, bold=True, color="#9a3412"))

    frags.append(rect(60, 105, 320, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(220, 125, "Вхідна таблиця (6 рядків)", size=10, bold=True, color="#1e293b"))
    frags.append(text(220, 145, "dept=IT (val: 100, 200, 300)\ndept=HR (val: 150, 250, 350)", size=9, color="#475569"))

    frags.append(arrow(220, 195, 220, 230, color=AMBER_S, sw=2.0))
    frags.append(text(220, 212, "GROUP BY dept, SUM(val)", size=9, bold=True, color=AMBER_S))

    frags.append(rect(60, 240, 320, 70, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=4))
    frags.append(text(220, 260, "Результат: 2 рядки (Кардинальність N → K)", size=10, bold=True, color="#9a3412"))
    frags.append(text(220, 285, "IT  | sum = 600\nHR  | sum = 750", size=10, bold=True, color="#1e293b"))

    frags.append(text(220, 355, "Втрата деталізації окремих кортежів.\nДоступні лише ключі групування та агрегати.", size=9, color="#64748b"))

    # Права колонка: WINDOW FUNCTIONS (N -> N)
    frags.append(rect(440, 60, 360, 340, fill=TEAL_F, stroke=TEAL_S, sw=1.3, rx=8))
    frags.append(text(620, 85, "Віконна функція: OVER (Збереження рядків)", size=12, bold=True, color="#0f766e"))

    frags.append(rect(460, 105, 320, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(620, 125, "Вхідна таблиця (6 рядків)", size=10, bold=True, color="#1e293b"))
    frags.append(text(620, 145, "dept=IT (val: 100, 200, 300)\ndept=HR (val: 150, 250, 350)", size=9, color="#475569"))

    frags.append(arrow(620, 195, 620, 230, color=TEAL_S, sw=2.0))
    frags.append(text(620, 212, "SUM(val) OVER (PARTITION BY dept)", size=9, bold=True, color=TEAL_S))

    frags.append(rect(460, 240, 320, 95, fill="#ffffff", stroke=TEAL_S, sw=1.5, rx=4))
    frags.append(text(620, 258, "Результат: 6 рядків (Кардинальність N → N)", size=10, bold=True, color="#0f766e"))
    frags.append(text(620, 280, "IT | 100 | sum_dept = 600\nIT | 200 | sum_dept = 600\nIT | 300 | sum_dept = 600\nHR | 150 | sum_dept = 750 ...", size=9, bold=True, color="#1e293b"))

    frags.append(text(620, 370, "Повна деталізація кожного початкового рядка\nплюс обчислене значення по вікну (партиції).", size=9, color="#64748b"))

    render(os.path.join(IMG, "fig4-window-vs-groupby.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_sql_execution_pipeline()
    fig2_logical_query_order()
    fig3_join_types_and_algorithms()
    fig4_window_vs_groupby()
    print("All figures generated successfully.")
