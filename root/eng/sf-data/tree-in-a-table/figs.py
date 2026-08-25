# -*- coding: utf-8 -*-
"""Фігури для теми «Дерево в таблиці: список суміжності, шлях, замикання» (sf-data/tree-in-a-table)."""
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

def fig1_tree_relational_conflict():
    """fig1-tree-relational-conflict.svg: Конфлікт між графовою природою дерева та пласким відношенням."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Ієрархічна структура графа та двовимірне пласке відношення (1NF)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Графове дерево
    frags.append(rect(25, 60, 375, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(212, 85, "Ієрархія сутностей (Граф G = (V, E))", size=13, bold=True, color="#334155"))

    # Вузли дерева
    b_root, _, _ = textbox(212, 125, "1: Каталог (Root)", size=11, pad=6, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=140)
    b_c1, _, _ = textbox(115, 205, "2: Електроніка", size=11, pad=6, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=110)
    b_c2, _, _ = textbox(310, 205, "3: Одяг", size=11, pad=6, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=100)
    b_l1, _, _ = textbox(75, 295, "4: Телефони", size=10, pad=4, fill=GREEN_F, stroke=GREEN_S, min_w=75)
    b_l2, _, _ = textbox(170, 295, "5: Ноутбуки", size=10, pad=4, fill=GREEN_F, stroke=GREEN_S, min_w=75)
    b_l3, _, _ = textbox(310, 295, "6: Взуття", size=10, pad=4, fill=GREEN_F, stroke=GREEN_S, min_w=75)

    # Ребра дерева
    frags.append(arrow(180, 145, 135, 185, color=LINE, sw=1.5))
    frags.append(arrow(245, 145, 290, 185, color=LINE, sw=1.5))
    frags.append(arrow(100, 225, 80, 275, color=LINE, sw=1.5))
    frags.append(arrow(130, 225, 155, 275, color=LINE, sw=1.5))
    frags.append(arrow(310, 225, 310, 275, color=LINE, sw=1.5))

    frags.extend([b_root, b_c1, b_c2, b_l1, b_l2, b_l3])
    frags.append(text(212, 375, "Глибина довільна, рекурсивні зв'язки", size=10, italic=True, color=MUTED))

    # Стрілка перетворення
    frags.append(arrow(405, 230, 435, 230, color=AMBER_S, sw=2.5))
    frags.append(text(420, 210, "Мапування", size=11, bold=True, color=AMBER_S))

    # Права частина: Пласка таблиця
    frags.append(rect(445, 60, 370, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(630, 85, "Пласке реляційне відношення", size=13, bold=True, color="#334155"))

    # Таблиця
    frags.append(rect(455, 105, 350, 28, fill="#334155", stroke="#1e293b", sw=1.2, rx=3))
    frags.append(text(480, 124, "id", size=11, bold=True, color="#ffffff"))
    frags.append(text(560, 124, "name", size=11, bold=True, color="#ffffff"))
    frags.append(text(710, 124, "структурні атрибути?", size=11, bold=True, color="#ffffff"))

    rows = [
        ("1", "Каталог", "parent_id / path / lft-rgt?", BLUE_F, BLUE_S, 145),
        ("2", "Електроніка", "як зберігати глибину?", TEAL_F, TEAL_S, 180),
        ("3", "Одяг", "як вибрати піддерево?", PURPLE_F, PURPLE_S, 215),
        ("4", "Телефони", "як знайти всіх предків?", GREEN_F, GREEN_S, 250),
        ("5", "Ноутбуки", "як перенести гілку?", GREEN_F, GREEN_S, 285),
        ("6", "Взуття", "як уникнути N+1 запитів?", GREEN_F, GREEN_S, 320),
    ]

    for rid, rname, rdesc, f_clr, s_clr, y in rows:
        frags.append(rect(455, y - 12, 350, 26, fill=f_clr, stroke=s_clr, sw=1.0, rx=3))
        frags.append(text(480, y + 5, rid, size=11, bold=True, color="#1e293b"))
        frags.append(text(560, y + 5, rname, size=11, color="#1e293b"))
        frags.append(text(710, y + 5, rdesc, size=10, italic=True, color=s_clr))

    frags.append(text(630, 375, "1NF вимагає атомарності: немає вкладених списків", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG, "fig1-tree-relational-conflict.svg"), W, H, *frags)

def fig2_adjacency_list_and_cte():
    """fig2-adjacency-list-and-cte.svg: Список суміжності та ітеративне виконання рекурсивного CTE."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Список суміжності (Adjacency List) та рекурсивне обчислення (WITH RECURSIVE)", size=15, bold=True, color="#1e293b"))

    # Лівий блок: Таблиця суміжності
    frags.append(rect(30, 65, 340, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(200, 90, "Таблиця: categories (id, parent_id)", size=12, bold=True, color="#334155"))

    frags.append(rect(45, 110, 310, 26, fill="#334155", stroke="#1e293b", sw=1.2, rx=3))
    frags.append(text(75, 127, "id", size=11, bold=True, color="#ffffff"))
    frags.append(text(175, 127, "name", size=11, bold=True, color="#ffffff"))
    frags.append(text(295, 127, "parent_id", size=11, bold=True, color="#ffffff"))

    t_rows = [
        ("1", "Каталог", "NULL", BLUE_F, BLUE_S, 150),
        ("2", "Електроніка", "1", TEAL_F, TEAL_S, 185),
        ("3", "Одяг", "1", PURPLE_F, PURPLE_S, 220),
        ("4", "Телефони", "2", GREEN_F, GREEN_S, 255),
        ("5", "Ноутбуки", "2", GREEN_F, GREEN_S, 290),
        ("6", "Взуття", "3", GREEN_F, GREEN_S, 325),
    ]

    for rid, rname, rpid, f_clr, s_clr, y in t_rows:
        frags.append(rect(45, y - 12, 310, 26, fill=f_clr, stroke=s_clr, sw=1.0, rx=3))
        frags.append(text(75, y + 5, rid, size=11, bold=True, color="#1e293b"))
        frags.append(text(175, y + 5, rname, size=11, color="#1e293b"))
        frags.append(text(295, y + 5, rpid, size=11, bold=True, color=s_clr))

    # Стрілка зовнішнього ключа
    b_fk, _, _ = textbox(200, 385, "Foreign Key: parent_id REFERENCES categories(id)\nВставка/Переміщення: O(1) операція", size=10, pad=5, fill=AMBER_F, stroke=AMBER_S, min_w=280)
    frags.append(b_fk)

    # Правий блок: Кроки виконання CTE
    frags.append(rect(390, 65, 420, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(600, 90, "Фази обчислення Recursive CTE", size=12, bold=True, color="#334155"))

    # Фаза 1: Anchor
    b_step1, _, _ = textbox(600, 135, "Крок 0: Якірний член (Anchor Member)\nSELECT id, name, parent_id, 0 AS depth\nWHERE id = 1  →  Отримуємо: [1: Каталог, d=0]", size=10, pad=6, fill=BLUE_F, stroke=BLUE_S, min_w=390)
    frags.append(b_step1)

    frags.append(arrow(600, 168, 600, 192, color=LINE, sw=1.5))

    # Фаза 2: Рекурсивний крок 1
    b_step2, _, _ = textbox(600, 225, "Ітерація 1 (JOIN Intermediate з categories)\nЗнаходимо дітей вузла 1 (parent_id = 1):\n→ Отримуємо: [2: Електроніка, d=1], [3: Одяг, d=1]", size=10, pad=6, fill=TEAL_F, stroke=TEAL_S, min_w=390)
    frags.append(b_step2)

    frags.append(arrow(600, 260, 600, 284, color=LINE, sw=1.5))

    # Фаза 3: Рекурсивний крок 2
    b_step3, _, _ = textbox(600, 318, "Ітерація 2 (JOIN з новим Intermediate)\nЗнаходимо дітей вузлів 2 та 3:\n→ Отримуємо: [4: Телефони, d=2], [5: Ноутбуки, d=2], [6: Взуття, d=2]", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, min_w=390)
    frags.append(b_step3)

    frags.append(arrow(600, 352, 600, 375, color=LINE, sw=1.5))

    # Фаза 4: Зупинка
    b_step4, _, _ = textbox(600, 398, "Ітерація 3: Дітей немає (Intermediate = ∅) → Фіксована точка, завершення", size=10, pad=5, fill=GRAY_F, stroke=GRAY_S, min_w=390)
    frags.append(b_step4)

    render(os.path.join(IMG, "fig2-adjacency-list-and-cte.svg"), W, H, *frags)

def fig3_materialized_path():
    """fig3-materialized-path.svg: Матеріалізований шлях, вибірка піддерева та переміщення."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Матеріалізований шлях (Materialized Path): Префіксна адресація", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Схема та дані шляхів
    frags.append(rect(30, 65, 360, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(210, 90, "Шляхи у вигляді рядків (/id/path/)", size=12, bold=True, color="#334155"))

    frags.append(rect(45, 110, 330, 26, fill="#334155", stroke="#1e293b", sw=1.2, rx=3))
    frags.append(text(70, 127, "id", size=11, bold=True, color="#ffffff"))
    frags.append(text(150, 127, "name", size=11, bold=True, color="#ffffff"))
    frags.append(text(280, 127, "path (VARCHAR / ltree)", size=11, bold=True, color="#ffffff"))

    p_rows = [
        ("1", "Каталог", "/1/", BLUE_F, BLUE_S, 148),
        ("2", "Електроніка", "/1/2/", TEAL_F, TEAL_S, 182),
        ("3", "Одяг", "/1/3/", PURPLE_F, PURPLE_S, 216),
        ("4", "Телефони", "/1/2/4/", GREEN_F, GREEN_S, 250),
        ("5", "Ноутбуки", "/1/2/5/", GREEN_F, GREEN_S, 284),
        ("6", "Взуття", "/1/3/6/", GREEN_F, GREEN_S, 318),
    ]

    for rid, rname, rpath, f_clr, s_clr, y in p_rows:
        frags.append(rect(45, y - 12, 330, 26, fill=f_clr, stroke=s_clr, sw=1.0, rx=3))
        frags.append(text(70, y + 5, rid, size=11, bold=True, color="#1e293b"))
        frags.append(text(150, y + 5, rname, size=11, color="#1e293b"))
        frags.append(text(280, y + 5, rpath, size=11, bold=True, color=s_clr))

    b_idx, _, _ = textbox(210, 375, "Індекс B-Tree (text_pattern_ops) або GiST (ltree)\nПошук нащадків — префіксне сканування індексу", size=10, pad=5, fill=AMBER_F, stroke=AMBER_S, min_w=310)
    frags.append(b_idx)

    # Права частина: Операції над шляхами
    frags.append(rect(410, 65, 400, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(610, 90, "Швидкі запити та вартість оновлення", size=12, bold=True, color="#334155"))

    # Операція 1: Отримання піддерева
    b_op1, _, _ = textbox(610, 140, "1. Вибірка всього піддерева Електроніки:\nWHERE path LIKE '/1/2/%'\n→ Миттєво вибирає вузли 2, 4, 5 без рекурсії", size=10, pad=6, fill=TEAL_F, stroke=TEAL_S, min_w=360)
    frags.append(b_op1)

    # Операція 2: Отримання всіх предків
    b_op2, _, _ = textbox(610, 215, "2. Отримання хлібних крихт (предків) для Ноутбуків:\nШлях = '/1/2/5/' → ID предків = {1, 2, 5}\nWHERE id IN (1, 2, 5)  [Розбір рядка або ltree]", size=10, pad=6, fill=BLUE_F, stroke=BLUE_S, min_w=360)
    frags.append(b_op2)

    # Операція 3: Переміщення гілки
    b_op3, _, _ = textbox(610, 310, "3. Переміщення піддерева (Електроніку переносимо в Одяг):\nСтарий префікс: '/1/2/'  →  Новий префікс: '/1/3/2/'\nUPDATE categories SET path = '/1/3/2/' || SUBSTRING(path, 6)\nWHERE path LIKE '/1/2/%';\n→ Вимагає оновлення всіх k нащадків гілки (O(k))", size=10, pad=6, fill=RED_F, stroke=RED_S, min_w=360)
    frags.append(b_op3)

    render(os.path.join(IMG, "fig3-materialized-path.svg"), W, H, *frags)

def fig4_nested_sets_intervals():
    """fig4-nested-sets-intervals.svg: Вкладені множини Джо Селко, інтервальне кодування та обхід дерева."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Вкладені множини (Nested Sets): Інтервали лівого та правого ключів [lft, rgt]", size=15, bold=True, color="#1e293b"))

    # Ліва верхня частина: Граф з номерами обходу
    frags.append(rect(30, 60, 420, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(240, 80, "Ейлерів обхід дерева в глибину (DFS)", size=11, bold=True, color="#334155"))

    # Вузли графа з інтервалами
    b_n1, _, _ = textbox(240, 115, "1: Каталог [1, 12]", size=11, pad=5, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=150)
    b_n2, _, _ = textbox(140, 180, "2: Електроніка [2, 7]", size=10, pad=5, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=140)
    b_n3, _, _ = textbox(340, 180, "3: Одяг [8, 11]", size=10, pad=5, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=120)
    b_n4, _, _ = textbox(90, 245, "4: Телефони [3, 4]", size=9, pad=4, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=110)
    b_n5, _, _ = textbox(195, 245, "5: Ноутбуки [5, 6]", size=9, pad=4, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=110)
    b_n6, _, _ = textbox(340, 245, "6: Взуття [9, 10]", size=9, pad=4, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=110)

    frags.append(arrow(210, 135, 160, 162, color=LINE, sw=1.2))
    frags.append(arrow(270, 135, 320, 162, color=LINE, sw=1.2))
    frags.append(arrow(120, 198, 100, 228, color=LINE, sw=1.2))
    frags.append(arrow(160, 198, 180, 228, color=LINE, sw=1.2))
    frags.append(arrow(340, 198, 340, 228, color=LINE, sw=1.2))

    frags.extend([b_n1, b_n2, b_n3, b_n4, b_n5, b_n6])

    # Права верхня частина: Вкладення відрізків
    frags.append(rect(470, 60, 340, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(640, 80, "Геометричне вкладення інтервалів", size=11, bold=True, color="#334155"))

    # Візуальні смуги інтервалів
    # Root: [1..12]
    frags.append(rect(490, 105, 300, 26, fill=BLUE_F, stroke=BLUE_S, sw=1.2, rx=3))
    frags.append(text(505, 122, "1", size=10, bold=True, color=BLUE_S))
    frags.append(text(640, 122, "1: Каталог [1..12]", size=10, bold=True, color="#1e293b"))
    frags.append(text(775, 122, "12", size=10, bold=True, color=BLUE_S))

    # Child 1: [2..7] & Child 2: [8..11]
    frags.append(rect(515, 145, 125, 24, fill=TEAL_F, stroke=TEAL_S, sw=1.2, rx=3))
    frags.append(text(525, 161, "2", size=9, bold=True, color=TEAL_S))
    frags.append(text(578, 161, "2: Електроніка [2..7]", size=9, color="#1e293b"))
    frags.append(text(630, 161, "7", size=9, bold=True, color=TEAL_S))

    frags.append(rect(665, 145, 100, 24, fill=PURPLE_F, stroke=PURPLE_S, sw=1.2, rx=3))
    frags.append(text(675, 161, "8", size=9, bold=True, color=PURPLE_S))
    frags.append(text(715, 161, "3: Одяг [8..11]", size=9, color="#1e293b"))
    frags.append(text(755, 161, "11", size=9, bold=True, color=PURPLE_S))

    # Leaves: [3..4], [5..6], [9..10]
    frags.append(rect(540, 180, 45, 22, fill=GREEN_F, stroke=GREEN_S, sw=1.0, rx=2))
    frags.append(text(562, 195, "4 [3..4]", size=9, color="#1e293b"))

    frags.append(rect(590, 180, 45, 22, fill=GREEN_F, stroke=GREEN_S, sw=1.0, rx=2))
    frags.append(text(612, 195, "5 [5..6]", size=9, color="#1e293b"))

    frags.append(rect(690, 180, 50, 22, fill=GREEN_F, stroke=GREEN_S, sw=1.0, rx=2))
    frags.append(text(715, 195, "6 [9..10]", size=9, color="#1e293b"))

    frags.append(text(640, 235, "Критерій нащадка: P.lft < C.lft AND C.rgt < P.rgt", size=10, bold=True, color=LINE))
    frags.append(text(640, 255, "Розмір піддерева: (rgt - lft - 1) / 2", size=10, italic=True, color=MUTED))
    frags.append(text(640, 275, "Листок: rgt - lft = 1", size=10, italic=True, color=MUTED))

    # Нижня частина: Перевага читання vs Катастрофа запису
    frags.append(rect(30, 315, 780, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    b_read, _, _ = textbox(225, 385, "Швидке читання піддерева (Індексний діапазон):\nSELECT * FROM categories WHERE lft BETWEEN 2 AND 7;\n→ Миттєвий B-Tree range scan, O(log N + k)", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, min_w=370)

    b_write, _, _ = textbox(615, 385, "Катастрофічний перезапис ключів при вставці:\nВставка вузла вимагає зсуву ВСІХ наступних ключів:\nUPDATE categories SET rgt = rgt + 2 WHERE rgt >= :ins_pt;\nUPDATE categories SET lft = lft + 2 WHERE lft > :ins_pt;\n→ Блокування всієї таблиці в OLTP!", size=10, pad=6, fill=RED_F, stroke=RED_S, min_w=370)

    frags.extend([b_read, b_write])

    render(os.path.join(IMG, "fig4-nested-sets-intervals.svg"), W, H, *frags)

def fig5_closure_table():
    """fig5-closure-table.svg: Таблиця замикання (Closure Table), матриця транзитивних шляхів."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Таблиця замикання (Closure Table): Повна транзитивна матриця шляхів", size=15, bold=True, color="#1e293b"))

    # Лівий блок: Сутності та дерево
    frags.append(rect(30, 65, 330, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(195, 90, "Таблиця вузлів: nodes (id, name)", size=12, bold=True, color="#334155"))

    frags.append(rect(45, 110, 300, 24, fill="#334155", stroke="#1e293b", sw=1.2, rx=3))
    frags.append(text(90, 126, "id (PK)", size=11, bold=True, color="#ffffff"))
    frags.append(text(210, 126, "name", size=11, bold=True, color="#ffffff"))

    n_rows = [
        ("1", "Каталог (Root)", BLUE_F, BLUE_S, 145),
        ("2", "Електроніка", TEAL_F, TEAL_S, 175),
        ("3", "Одяг", PURPLE_F, PURPLE_S, 205),
        ("4", "Телефони", GREEN_F, GREEN_S, 235),
        ("5", "Ноутбуки", GREEN_F, GREEN_S, 265),
    ]

    for nid, nname, f_clr, s_clr, y in n_rows:
        frags.append(rect(45, y - 10, 300, 22, fill=f_clr, stroke=s_clr, sw=1.0, rx=3))
        frags.append(text(90, y + 5, nid, size=10, bold=True, color="#1e293b"))
        frags.append(text(210, y + 5, nname, size=10, color="#1e293b"))

    b_graph, _, _ = textbox(195, 345, "Вузли не містять parent_id!\nУсі ребра та предки винесені\nу спеціальну транзитивну таблицю-міст.", size=10, pad=5, fill=AMBER_F, stroke=AMBER_S, min_w=280)
    frags.append(b_graph)

    # Правий блок: Таблиця зв'язків tree_paths
    frags.append(rect(380, 65, 430, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(595, 90, "Таблиця замикання: tree_paths", size=12, bold=True, color="#334155"))

    frags.append(rect(395, 110, 400, 24, fill="#334155", stroke="#1e293b", sw=1.2, rx=3))
    frags.append(text(460, 126, "ancestor_id", size=11, bold=True, color="#ffffff"))
    frags.append(text(560, 126, "descendant_id", size=11, bold=True, color="#ffffff"))
    frags.append(text(650, 126, "depth", size=11, bold=True, color="#ffffff"))
    frags.append(text(740, 126, "тип", size=11, bold=True, color="#ffffff"))

    p_entries = [
        ("1", "1", "0", "Self-loop (рефлексивність)", BLUE_F, BLUE_S, 142),
        ("1", "2", "1", "Прямий зв'язок (батько)", TEAL_F, TEAL_S, 168),
        ("1", "4", "2", "Транзитивний предок (дід)", GREEN_F, GREEN_S, 194),
        ("2", "2", "0", "Self-loop", BLUE_F, BLUE_S, 220),
        ("2", "4", "1", "Прямий зв'язок (батько)", TEAL_F, TEAL_S, 246),
        ("4", "4", "0", "Self-loop", BLUE_F, BLUE_S, 272),
        ("...", "...", "...", "Всі пари (A, D)", GRAY_F, GRAY_S, 298),
    ]

    for anc, desc, dval, ptype, f_clr, s_clr, y in p_entries:
        frags.append(rect(395, y - 9, 400, 20, fill=f_clr, stroke=s_clr, sw=1.0, rx=3))
        frags.append(text(460, y + 5, anc, size=10, bold=True, color="#1e293b"))
        frags.append(text(560, y + 5, desc, size=10, bold=True, color="#1e293b"))
        frags.append(text(650, y + 5, dval, size=10, color="#1e293b"))
        frags.append(text(740, y + 5, ptype, size=9, italic=True, color=s_clr))

    b_cl_ops, _, _ = textbox(595, 365, "Піддерево: WHERE ancestor_id = :root (O(1) за індексом)\nПредки: WHERE descendant_id = :node (O(1) за індексом)\nПрямі діти: додаємо умову depth = 1", size=10, pad=5, fill=GREEN_F, stroke=GREEN_S, min_w=400)
    frags.append(b_cl_ops)

    render(os.path.join(IMG, "fig5-closure-table.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_tree_relational_conflict()
    fig2_adjacency_list_and_cte()
    fig3_materialized_path()
    fig4_nested_sets_intervals()
    fig5_closure_table()
    print("All 5 figures generated successfully.")
