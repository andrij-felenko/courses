# -*- coding: utf-8 -*-
"""Фігури для теми «Індекси баз даних: від B-дерев до Hash та GiST»
(book/programming/databases/database-indexes)."""

import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра теми
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"
DARK_HDR = "#334155"


def fig1_heap_vs_index():
    """fig1-heap-vs-index.svg: Порівняння послідовного сканування купи (Seq Scan) та індексного пошуку (Index Scan)."""
    W, H = 860, 470
    frags = []

    frags.append(rect(10, 10, 840, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 34, "Шляхи вибірки даних: Послідовне сканування (Seq Scan) проти Індексного доступу", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: Послідовне сканування
    frags.append(rect(30, 60, 380, 380, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(220, 85, "Послідовне сканування (Seq Scan)", size=13, bold=True, color=RED_S))
    frags.append(text(220, 105, "Зчитування кожної сторінки диска: O(N) операцій I/O", size=11, color="#64748b"))

    # Сторінки купи (Heap Pages)
    heap_pages_left = [
        (135, "Сторінка 0 (8 КБ)\n[рядки 1..40] — перевірка умов", GRAY_F, GRAY_S),
        (195, "Сторінка 1 (8 КБ)\n[рядки 41..80] — перевірка умов", GRAY_F, GRAY_S),
        (255, "Сторінка 2 (8 КБ)\n[рядок 82 ЗБІГ! TID=(2,2)]", GREEN_F, GREEN_S),
        (315, "Сторінка 3..N (8 КБ)\n[продовження до кінця таблиці]", GRAY_F, GRAY_S),
    ]
    for y_pos, label, fill_c, strk_c in heap_pages_left:
        b_box, _, _ = textbox(220, y_pos, label, size=10, pad=6, fill=fill_c, stroke=strk_c, min_w=340)
        frags.append(b_box)

    frags.append(arrow(220, 155, 220, 175, color=RED_S, sw=1.5))
    frags.append(arrow(220, 215, 220, 235, color=RED_S, sw=1.5))
    frags.append(arrow(220, 275, 220, 295, color=RED_S, sw=1.5))

    b_cost_left, _, _ = textbox(220, 395, "100 ГБ таблиця = 12 500 000 сторінок\nЧас зчитування: десятки секунд чи хвилини", size=10, pad=6, fill=RED_F, stroke=RED_S, bold=True, min_w=340)
    frags.append(b_cost_left)

    # Права колонка: Індексний доступ
    frags.append(rect(450, 60, 380, 380, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(640, 85, "Індексний пошук через B-дерево (Index Scan)", size=13, bold=True, color=GREEN_S))
    frags.append(text(640, 105, "Логарифмічний спуск до TID: O(log N) операцій I/O", size=11, color="#64748b"))

    b_idx_root, _, _ = textbox(640, 135, "Корінь індексу (Root Page)\nКлючі: [100 | 500 | 1000]", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=300)
    b_idx_leaf, _, _ = textbox(640, 210, "Листовий вузол (Leaf Page)\nКлюч 82 ➔ Покажчик TID = (Блок 2, Зсув 2)", size=10, pad=5, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=300)
    b_heap_target, _, _ = textbox(640, 295, "Купа (Heap): Лише Блок 2 (8 КБ)\nПряме вилучення кортежу за зсувом 2", size=10, pad=5, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=300)

    frags.extend([b_idx_root, b_idx_leaf, b_heap_target])

    frags.append(arrow(640, 155, 640, 190, color=BLUE_S, sw=1.8))
    frags.append(arrow(640, 230, 640, 275, color=TEAL_S, sw=1.8))

    b_cost_right, _, _ = textbox(640, 395, "3 сторінки індексу + 1 сторінка купи = 4 зчитування\nЧас виконання: менше 1 мілісекунди", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=340)
    frags.append(b_cost_right)

    render(os.path.join(IMG, "fig1-heap-vs-index.svg"), W, H, *frags)


def fig2_btree_page_structure():
    """fig2-btree-page-structure.svg: Анатомія сторінки B+дерева та зв'язки між листовими вузлами."""
    W, H = 860, 500
    frags = []

    frags.append(rect(10, 10, 840, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 34, "Внутрішня організація сторінки B+дерева (Slotted Page) та листовий ланцюг", size=15, bold=True, color="#1e293b"))

    # Макет сторінки індексу (8 КБ блок)
    frags.append(rect(30, 60, 800, 190, fill=GRAY_F, stroke=GRAY_S, sw=1.5, rx=8))
    frags.append(text(430, 82, "Фізична структура дискової сторінки індексу (8192 байти)", size=12, bold=True, color="#1e293b"))

    # Компоненти сторінки: чітко рознесені центри без перекриттів
    b_hdr, _, _ = textbox(105, 130, "Заголовок\n(PageHeader)\nLSN, зсуви", size=10, pad=5, fill=DARK_HDR, stroke="#1e293b", color="#ffffff", bold=True, min_w=120)
    b_ptrs, _, _ = textbox(240, 130, "Масив покажчиків\n(ItemId / LinePtr)\n[Зсув 1] [2] [3]", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=130)
    b_free, _, _ = textbox(380, 130, "Вільне місце\n(Free Space)\nРосте до центру", size=10, pad=5, fill="#ffffff", stroke="#94a3b8", min_w=130)
    b_data, _, _ = textbox(540, 130, "Тіло записів індексу\n(IndexTuples: Ключ+TID)\n[Кортеж 3] [2] [1]", size=10, pad=5, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=160)
    b_spec, _, _ = textbox(720, 130, "Спеціальна зона (Opaque)\nHigh Key + RightLink\n(Lehman-Yao B-link)", size=10, pad=5, fill=AMBER_F, stroke=AMBER_S, bold=True, min_w=170)

    frags.extend([b_hdr, b_ptrs, b_free, b_data, b_spec])

    frags.append(text(430, 195, "Напрямок заповнення: Покажчики зростають зліва направо ➔ ⯈ Вільне місце ⯇ 🠔 Записи ростуть справа наліво", size=10, italic=True, color="#475569"))
    frags.append(text(430, 220, "High Key: Верхня межа значень на сторінці. RightLink: Швидкий перехід праворуч при паралельному розщепленні.", size=10, bold=True, color=AMBER_S))

    # Нижній блок: Двозв'язний ланцюг листів
    frags.append(text(430, 275, "Двозв'язний список листових вузлів для діапазонного сканування (Range Scan)", size=13, bold=True, color=DARK_HDR))

    b_leaf1, _, _ = textbox(150, 350, "Листовий вузол A\nКлючі: [10, 15, 22]\nTID: [(1,1), (1,2), (2,1)]\nHigh Key: 25", size=10, pad=6, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=190)
    b_leaf2, _, _ = textbox(430, 350, "Листовий вузол B\nКлючі: [25, 31, 40]\nTID: [(2,2), (3,1), (3,2)]\nHigh Key: 45", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=190)
    b_leaf3, _, _ = textbox(710, 350, "Листовий вузол C\nКлючі: [45, 52, 60]\nTID: [(4,1), (4,2), (5,1)]\nHigh Key: ∞", size=10, pad=6, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=190)

    frags.extend([b_leaf1, b_leaf2, b_leaf3])

    # Двосторонні стрілки між вузлами
    frags.append(arrow(250, 335, 325, 335, color=GREEN_S, sw=2.0))
    frags.append(arrow(325, 365, 250, 365, color=GREEN_S, sw=2.0))
    frags.append(arrow(535, 335, 605, 335, color=GREEN_S, sw=2.0))
    frags.append(arrow(605, 365, 535, 365, color=GREEN_S, sw=2.0))

    b_scan_note, _, _ = textbox(430, 440, "Запит 'WHERE id BETWEEN 15 AND 52': один спуск до вузла A ➔ лінійне читання праворуч до вузла C (без повернення до кореня)", size=10, pad=6, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=760)
    frags.append(b_scan_note)

    render(os.path.join(IMG, "fig2-btree-page-structure.svg"), W, H, *frags)


def fig3_gist_spatial_tree():
    """fig3-gist-spatial-tree.svg: Ієрархія мінімальних обмежувальних прямокутників (MBR) у GiST."""
    W, H = 860, 480
    frags = []

    frags.append(rect(10, 10, 840, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 34, "Узагальнене пошукове дерево (GiST): Ієрархія обмежувальних прямокутників (R-Tree)", size=15, bold=True, color="#1e293b"))

    # Лівий блок: 2D Простір геометрій
    frags.append(rect(30, 60, 370, 390, fill="#fafafa", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(215, 85, "Двовимірний простір об'єктів (2D Canvas)", size=12, bold=True, color=DARK_HDR))

    # Великі регіони R1 та R2
    frags.append(rect(50, 110, 155, 150, fill=BLUE_F, stroke=BLUE_S, sw=2.0, rx=4))
    frags.append(text(75, 130, "R1 (MBR)", size=11, bold=True, color=BLUE_S))

    frags.append(rect(225, 130, 155, 160, fill=PURPLE_F, stroke=PURPLE_S, sw=2.0, rx=4))
    frags.append(text(250, 150, "R2 (MBR)", size=11, bold=True, color=PURPLE_S))

    # Дрібні підрегіони R3, R4 всередині R1
    frags.append(rect(60, 145, 60, 45, fill="#ffffff", stroke=TEAL_S, sw=1.5, rx=2))
    frags.append(text(90, 172, "R3: Об'єкт A", size=9, bold=True, color=TEAL_S))

    frags.append(rect(130, 195, 65, 55, fill="#ffffff", stroke=TEAL_S, sw=1.5, rx=2))
    frags.append(text(162, 227, "R4: Об'єкт B", size=9, bold=True, color=TEAL_S))

    # Дрібні підрегіони R5, R6 всередині R2
    frags.append(rect(240, 175, 60, 45, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=2))
    frags.append(text(270, 202, "R5: Об'єкт C", size=9, bold=True, color=AMBER_S))

    frags.append(rect(310, 230, 60, 50, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=2))
    frags.append(text(340, 258, "R6: Об'єкт D", size=9, bold=True, color=AMBER_S))

    # Прямокутник запиту (Query Box Q)
    frags.append(f'<rect x="105.0" y="170.0" width="105.0" height="90.0" rx="4" fill="none" stroke="{RED_S}" stroke-width="2.2" stroke-dasharray="5,3"/>')
    frags.append(text(157, 185, "Запит Q (Перетин)", size=10, bold=True, color=RED_S))

    b_geo_note, _, _ = textbox(215, 395, "Запит Q перетинає прямокутник R1 та підрегіон R4.\nРегіон R2 відсікається цілком (Consistent = False)", size=10, pad=6, fill=RED_F, stroke=RED_S, bold=True, min_w=330)
    frags.append(b_geo_note)

    # Правий блок: Деревоподібна ієрархія GiST
    frags.append(rect(415, 60, 415, 390, fill="#fafafa", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(622, 85, "Ієрархічне дерево предикатів GiST", size=12, bold=True, color=DARK_HDR))

    b_g_root, _, _ = textbox(622, 125, "Корінь GiST (Root Node)\nПредикати: [ R1 | R2 ]", size=10, pad=5, fill=DARK_HDR, stroke="#1e293b", color="#ffffff", bold=True, min_w=220)

    b_g_r1, _, _ = textbox(520, 210, "Вузол R1\n[ R3 | R4 ]\nConsistent = TRUE", size=10, pad=5, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=150)
    b_g_r2, _, _ = textbox(725, 210, "Вузол R2\n[ R5 | R6 ]\nConsistent = FALSE (ВІДСІЧ)", size=10, pad=5, fill=GRAY_F, stroke=GRAY_S, bold=True, min_w=165)

    b_g_r3, _, _ = textbox(475, 310, "Лист R3 (A)\nConsistent = FALSE", size=9, pad=4, fill=GRAY_F, stroke=GRAY_S, min_w=95)
    b_g_r4, _, _ = textbox(575, 310, "Лист R4 (B)\nConsistent = TRUE ➔ TID", size=9, pad=4, fill=GREEN_F, stroke=GREEN_S, bold=True, min_w=95)

    frags.extend([b_g_root, b_g_r1, b_g_r2, b_g_r3, b_g_r4])

    frags.append(arrow(565, 145, 530, 185, color=BLUE_S, sw=2.0))
    frags.append(arrow(680, 145, 720, 185, color=GRAY_S, sw=1.2))
    frags.append(arrow(500, 240, 480, 285, color=GRAY_S, sw=1.2))
    frags.append(arrow(540, 240, 570, 285, color=GREEN_S, sw=2.0))

    b_gist_ops, _, _ = textbox(622, 400, "Методи операторного класу GiST:\nConsistent() — чи задовольняє ключ запиту\nUnion() / Compress() / Penalty() / PickSplit()", size=10, pad=6, fill=TEAL_F, stroke=TEAL_S, bold=True, min_w=370)
    frags.append(b_gist_ops)

    render(os.path.join(IMG, "fig3-gist-spatial-tree.svg"), W, H, *frags)


def fig4_index_types_matrix():
    """fig4-index-types-matrix.svg: Порівняльна матриця сімейств індексів баз даних."""
    W, H = 860, 500
    frags = []

    frags.append(rect(10, 10, 840, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(430, 34, "Спектр індексних структур у реляційних та документоорієнтованих СУБД", size=15, bold=True, color="#1e293b"))

    # Заголовок таблиці
    headers = [
        (85, "Тип індексу"),
        (225, "Структура даних"),
        (405, "Оператори"),
        (610, "Сценарій використання"),
        (775, "Розмір"),
    ]
    frags.append(rect(30, 55, 800, 32, fill=DARK_HDR, stroke="#1e293b", sw=1.5, rx=4))
    for x_c, title in headers:
        frags.append(text(x_c, 76, title, size=11, bold=True, color="#ffffff"))

    rows_data = [
        ("B-Tree", "Збалансоване дерево зі зв'язаними листами", "=, <, <=, >, >=, BETWEEN, ORDER BY", "Універсальний: первинні ключі, скаляри, сортування", "Середній (10-30%)", BLUE_F, BLUE_S),
        ("Hash", "Масив бакетів із хеш-функцією", "= (виключно точна рівність)", "Швидкий пошук унікальних ключів, UUID, точних слів", "Компактний", AMBER_F, AMBER_S),
        ("GiST", "Узагальнене дерево просторових предикатів", "&& (перетин), @> (вміщення), <-> (kNN)", "Геодані (PostGIS), геометрія, часові діапазони", "Середній/Великий", TEAL_F, TEAL_S),
        ("GIN", "Інвертований індекс (терм ➔ список TID)", "@@ (повнотекст), @> (JSONB), && (масиви)", "Повнотекстовий пошук, JSONB-документи, теги", "Великий (дорогий запис)", PURPLE_F, PURPLE_S),
        ("BRIN", "Блоковий діапазонний індекс (Min/Max)", "=, <, <=, >, >=, BETWEEN (за фізичним порядком)", "Гігантські часові ряди, append-only журнали", "Мікроскопічний (<0.1%)", GREEN_F, GREEN_S),
    ]

    y_start = 98
    for idx_name, struct_desc, ops_desc, fit_desc, size_desc, fill_c, strk_c in rows_data:
        frags.append(rect(30, y_start, 800, 62, fill=fill_c, stroke=strk_c, sw=1.2, rx=4))
        frags.append(text(85, y_start + 36, idx_name, size=12, bold=True, color="#1e293b"))
        frags.append(text(225, y_start + 36, struct_desc, size=9, color="#1e293b"))
        frags.append(text(405, y_start + 36, ops_desc, size=9, bold=True, color="#1e293b"))
        frags.append(text(610, y_start + 36, fit_desc, size=9, color="#1e293b"))
        frags.append(text(775, y_start + 36, size_desc, size=9, bold=True, color="#1e293b"))
        y_start += 68

    frags.append(text(430, 465, "Вибір типу індексу визначається формою оператора у виразі WHERE та фізичним розподілом даних на диску.", size=10, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig4-index-types-matrix.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_heap_vs_index()
    fig2_btree_page_structure()
    fig3_gist_spatial_tree()
    fig4_index_types_matrix()
    print("Всі 4 фігури успішно згенеровано.")
