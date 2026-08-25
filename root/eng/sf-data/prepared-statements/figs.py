# -*- coding: utf-8 -*-
"""Фігури до теми «Підготовлені вирази: компіляція запиту один раз»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Життєвий цикл підготовленого виразу проти прямого виконання ──────────
def fig_statement_lifecycle():
    W, H = 980, 560
    frags = []

    # Верхній блок: Пряме виконання (Ad-hoc)
    top_y = 60
    frags.append(rect(30, top_y, 920, 200, rx=8, fill="#fdfaf3", stroke="#d97706", sw=1.5))
    frags.append(text(50, top_y + 28, "Пряме виконання запиту (Ad-hoc SQL, N повторів):", size=13, bold=True, color="#d97706", anchor="start"))

    adhoc_steps = [
        ("SQL Текст", "SELECT .. WHERE\nid = 42"),
        ("Парсинг", "Лексер + Парсер\nбудують AST"),
        ("Семантика", "Перевірка таблиць,\nтипів і прав"),
        ("Планувальник", "CBO розраховує\nвартість і план"),
        ("Виконання", "Ітератор читає\nрядки таблиці"),
    ]
    bx_coords = [60, 240, 420, 600, 780]
    box_w = 140
    box_h = 105
    box_y = top_y + 50

    for i, (title, desc) in enumerate(adhoc_steps):
        x = bx_coords[i]
        is_exec = (i == 4)
        col_border = FIELD if is_exec else NEG
        col_fill = "#eef9f1" if is_exec else "#eaf0fd"
        frags.append(rect(x, box_y, box_w, box_h, rx=6, fill=col_fill, stroke=col_border, sw=1.5))
        frags.append(text(x + box_w / 2, box_y + 24, title, size=12, bold=True, color=col_border))
        frags.append(line(x + 10, box_y + 35, x + box_w - 10, box_y + 35, color=MUTED, sw=1, dash="3 3"))
        frags.append(fitbox(x + 6, box_y + 42, box_w - 12, box_h - 48, desc, size=10, color=INK))
        if i < len(adhoc_steps) - 1:
            next_x = bx_coords[i + 1]
            frags.append(arrow(x + box_w + 2, box_y + box_h / 2, next_x - 4, box_y + box_h / 2, color=INK, sw=1.5))

    frags.append(text(500, top_y + 180, "Повний конвеєр (парсинг + аналіз + планування) повторюється на кожен окремий запит — 70-85% CPU на компіляцію", size=11, color=POS, italic=True))

    # Нижній блок: Підготовлені вирази (Prepared Statements)
    bot_y = 285
    frags.append(rect(30, bot_y, 920, 245, rx=8, fill="#eef9f1", stroke=FIELD, sw=1.5))
    frags.append(text(50, bot_y + 28, "Підготовлені вирази (Prepared Statements):", size=13, bold=True, color=FIELD, anchor="start"))

    # Фаза 1: PREPARE (одноразово)
    p1_x, p1_y, p1_w, p1_h = 60, bot_y + 48, 380, 160
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, rx=6, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(rect(p1_x, p1_y, p1_w, 32, rx=6, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(text(p1_x + p1_w / 2, p1_y + 21, "1. Фаза підготовки: PREPARE (один раз)", size=12, bold=True, color=INK))

    p1_nodes = [
        (p1_x + 15, p1_y + 48, 90, 85, "SQL Шаблон", "WHERE id = $1"),
        (p1_x + 135, p1_y + 48, 100, 85, "Компіляція", "Парсинг + Аналіз\n-> План у кеш"),
        (p1_x + 265, p1_y + 48, 100, 85, "Кеш сесії", "Дескриптор 'P1'\nз планом запиту"),
    ]
    for nx, ny, nw, nh, nt, nd in p1_nodes:
        frags.append(rect(nx, ny, nw, nh, rx=4, fill="#fdfaf3", stroke="#d97706", sw=1.2))
        frags.append(text(nx + nw / 2, ny + 20, nt, size=10, bold=True, color="#d97706"))
        frags.append(fitbox(nx + 4, ny + 28, nw - 8, nh - 32, nd, size=9, color=INK))

    frags.append(arrow(p1_x + 107, p1_y + 90, p1_x + 133, p1_y + 90, color=INK, sw=1.3))
    frags.append(arrow(p1_x + 237, p1_y + 90, p1_x + 263, p1_y + 90, color=INK, sw=1.3))
    frags.append(text(p1_x + p1_w / 2, p1_y + 148, "Парсинг і генерація плану відбуваються лише раз", size=10, color=MUTED, italic=True))

    # Фаза 2: BIND + EXECUTE (N разів)
    p2_x, p2_y, p2_w, p2_h = 470, bot_y + 48, 460, 160
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, rx=6, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(rect(p2_x, p2_y, p2_w, 32, rx=6, fill="#e8f8f0", stroke=FIELD, sw=1.5))
    frags.append(text(p2_x + p2_w / 2, p2_y + 21, "2. Фаза зв'язування та виконання: EXECUTE (N разів)", size=12, bold=True, color=FIELD))

    p2_nodes = [
        (p2_x + 15, p2_y + 48, 120, 85, "Параметри", "Двійкові значення:\n(id = 42, 43, 44..)"),
        (p2_x + 165, p2_y + 48, 130, 85, "Зв'язування (Bind)", "Підстановка значень\nу готові слоти плану"),
        (p2_x + 325, p2_y + 48, 120, 85, "Рушій виконання", "Прямий запуск плану\nбез репарсингу"),
    ]
    for nx, ny, nw, nh, nt, nd in p2_nodes:
        frags.append(rect(nx, ny, nw, nh, rx=4, fill="#eef9f1", stroke=FIELD, sw=1.2))
        frags.append(text(nx + nw / 2, ny + 20, nt, size=10, bold=True, color=FIELD))
        frags.append(fitbox(nx + 4, ny + 28, nw - 8, nh - 32, nd, size=9, color=INK))

    frags.append(arrow(p2_x + 137, p2_y + 90, p2_x + 163, p2_y + 90, color=FIELD, sw=1.5))
    frags.append(arrow(p2_x + 297, p2_y + 90, p2_x + 323, p2_y + 90, color=FIELD, sw=1.5))
    frags.append(text(p2_x + p2_w / 2, p2_y + 148, "Миттєве виконання: 0% витрат CPU на парсер і планувальник", size=10, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'statement-lifecycle.svg'), W, H, *frags,
                  title="Життєвий цикл запиту: пряме виконання проти підготовлених виразів")


# ── 2. Ізоляція даних від граматики в дереві AST ────────────────────────────
def fig_ast_param_isolation():
    W, H = 980, 520
    frags = []

    # Ліва панель: Конкатенація (SQL Injection)
    lx, ly, lw, lh = 35, 55, 435, 435
    frags.append(rect(lx, ly, lw, lh, rx=8, fill="#fdf3f2", stroke=POS, sw=1.8))
    frags.append(rect(lx, ly, lw, 55, rx=8, fill=POS, stroke=POS))
    frags.append(text(lx + lw / 2, ly + 24, "Конкатенація рядків (Синтаксична вразливість)", size=12, bold=True, color="#ffffff"))
    frags.append(text(lx + lw / 2, ly + 44, "\"WHERE name = '\" + input + \"'\"", size=11, color="#ffffff"))

    frags.append(text(lx + 20, ly + 80, "Вхідний рядок: admin' OR '1'='1", size=11, bold=True, color=POS, anchor="start"))

    # Дерево для конкатенації
    tree_ly = ly + 105
    frags.append(rect(lx + 155, tree_ly, 125, 36, rx=4, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(lx + 217, tree_ly + 22, "WHERE Clause", size=11, bold=True, color=INK))

    frags.append(rect(lx + 155, tree_ly + 65, 125, 36, rx=4, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(lx + 217, tree_ly + 88, "OR (BinaryOp)", size=12, bold=True, color=POS))
    frags.append(line(lx + 217, tree_ly + 36, lx + 217, tree_ly + 65, color=POS, sw=1.8))

    frags.append(rect(lx + 40, tree_ly + 130, 150, 42, rx=4, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(lx + 115, tree_ly + 155, "name = 'admin'", size=10, color=INK))

    frags.append(rect(lx + 245, tree_ly + 130, 150, 42, rx=4, fill="#fee2e2", stroke=POS, sw=1.8))
    frags.append(text(lx + 320, tree_ly + 155, "'1' = '1' (Завжди TRUE)", size=10, bold=True, color=POS))

    frags.append(line(lx + 195, tree_ly + 101, lx + 115, tree_ly + 130, color=POS, sw=1.5))
    frags.append(line(lx + 240, tree_ly + 101, lx + 320, tree_ly + 130, color=POS, sw=1.8))

    frags.append(fitbox(lx + 15, tree_ly + 200, lw - 30, 110,
                        "Синтаксичний аналізатор парсить лапки та оператор OR як граматичні елементи SQL.\n"
                        "Структура дерева AST мутує, перетворюючи предикат на тотожно істинний вираз.",
                        size=11, color=INK, fill="#ffffff", stroke=POS))

    # Права панель: Підготовлений вираз (AST Ізоляція)
    rx, ry, rw, rh = 510, 55, 435, 435
    frags.append(rect(rx, ry, rw, rh, rx=8, fill="#eef9f1", stroke=FIELD, sw=1.8))
    frags.append(rect(rx, ry, rw, 55, rx=8, fill=FIELD, stroke=FIELD))
    frags.append(text(rx + rw / 2, ry + 24, "Підготовлений вираз (AST Ізоляція)", size=12, bold=True, color="#ffffff"))
    frags.append(text(rx + rw / 2, ry + 44, "WHERE name = $1  (Параметр зв'язується окремо)", size=11, color="#ffffff"))

    frags.append(text(rx + 20, ry + 80, "Значення параметра $1: admin' OR '1'='1", size=11, bold=True, color=FIELD, anchor="start"))

    # Дерево для підготовленого виразу
    tree_ry = ry + 105
    frags.append(rect(rx + 155, tree_ry, 125, 36, rx=4, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(rx + 217, tree_ry + 22, "WHERE Clause", size=11, bold=True, color=INK))

    frags.append(rect(rx + 155, tree_ry + 65, 125, 36, rx=4, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(rx + 217, tree_ry + 88, "= (EqualOp)", size=12, bold=True, color=FIELD))
    frags.append(line(rx + 217, tree_ry + 36, rx + 217, tree_ry + 65, color=FIELD, sw=1.8))

    frags.append(rect(rx + 40, tree_ry + 130, 150, 42, rx=4, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(rx + 115, tree_ry + 155, "ColumnRef (name)", size=10, color=INK))

    frags.append(rect(rx + 245, tree_ry + 130, 150, 42, rx=4, fill="#e8f8f0", stroke=FIELD, sw=2))
    frags.append(text(rx + 320, tree_ry + 148, "ParamSlot ($1)", size=11, bold=True, color=FIELD))
    frags.append(text(rx + 320, tree_ry + 164, "типізоване значення", size=9, color=MUTED))

    frags.append(line(rx + 195, tree_ry + 101, rx + 115, tree_ry + 130, color=FIELD, sw=1.5))
    frags.append(line(rx + 240, tree_ry + 101, rx + 320, tree_ry + 130, color=FIELD, sw=1.8))

    frags.append(fitbox(rx + 15, tree_ry + 200, rw - 30, 110,
                        "Дерево AST фіксується на етапі PREPARE. Слот $1 приймає сирий рядок цілком як значення.\n"
                        "Символи лапок та ключове слово OR інтерпретуються як звичайний текст, не змінюючи логіку виразу.",
                        size=11, color=INK, fill="#ffffff", stroke=FIELD))

    return render(os.path.join(OUT, 'ast-param-isolation.svg'), W, H, *frags,
                  title="Структурна ізоляція: чому AST унеможливлює SQL-ін'єкцію")


# ── 3. Дилема планів: Generic Plan проти Custom Plan ────────────────────────
def fig_generic_vs_custom_plan():
    W, H = 980, 520
    frags = []

    # Ліва частина: Гістограма розподілу даних
    gx, gy, gw, gh = 35, 60, 360, 430
    frags.append(rect(gx, gy, gw, gh, rx=8, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(rect(gx, gy, gw, 45, rx=8, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(gx + gw / 2, gy + 27, "Скошений розподіл (Data Skew)", size=12, bold=True, color=INK))

    # Стовпчики гістограми
    hist_base_y = gy + 280
    frags.append(line(gx + 40, hist_base_y, gx + gw - 30, hist_base_y, color=INK, sw=1.5))
    frags.append(line(gx + 40, gy + 70, gx + 40, hist_base_y, color=INK, sw=1.5))
    frags.append(text(gx + 30, gy + 75, "Рядки", size=9, color=MUTED, anchor="end"))

    # Стовпець 1: 'completed' (99.9% - 10 000 000)
    frags.append(rect(gx + 70, gy + 90, 85, hist_base_y - (gy + 90), fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(gx + 112, gy + 82, "10 000 000", size=10, bold=True, color=POS))
    frags.append(text(gx + 112, hist_base_y + 18, "status = 'completed'", size=10, color=INK))
    frags.append(text(gx + 112, hist_base_y + 32, "(99.9% рядків)", size=9, color=MUTED))

    # Стовпець 2: 'pending' (0.1% - 1 000)
    frags.append(rect(gx + 210, hist_base_y - 12, 85, 12, fill="#e8f8f0", stroke=FIELD, sw=1.5))
    frags.append(text(gx + 252, hist_base_y - 18, "1 000", size=10, bold=True, color=FIELD))
    frags.append(text(gx + 252, hist_base_y + 18, "status = 'pending'", size=10, color=INK))
    frags.append(text(gx + 252, hist_base_y + 32, "(0.1% рядків)", size=9, color=MUTED))

    frags.append(fitbox(gx + 15, gy + 340, gw - 30, 75,
                        "Середня селективність (1/2 = 50%) вводить в оману:\n"
                        "для 1 000 рядків вигідний Index Scan,\n"
                        "а для 10 000 000 рядків — лише Seq Scan.",
                        size=10, color=INK, fill="#fdfaf3", stroke="#d97706"))

    # Права частина: Порівняння планів та Евристика 5 викликів
    rx, ry, rw, rh = 420, 60, 525, 430
    frags.append(rect(rx, ry, rw, rh, rx=8, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(rect(rx, ry, rw, 45, rx=8, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(rx + rw / 2, ry + 27, "Вибір між Generic Plan та Custom Plan (PostgreSQL)", size=12, bold=True, color=INK))

    # Картка Custom Plan
    frags.append(rect(rx + 20, ry + 60, 485, 80, rx=6, fill="#fdfaf3", stroke="#d97706", sw=1.2))
    frags.append(text(rx + 35, ry + 82, "Спеціалізований план (Custom Plan):", size=11, bold=True, color="#d97706", anchor="start"))
    frags.append(text(rx + 35, ry + 102, "• Генерується з підстановкою конкретного $1 (враховує гістограми MCV)", size=10, color=INK, anchor="start"))
    frags.append(text(rx + 35, ry + 122, "• Точний, але вимагає виклику планувальника на кожен EXECUTE", size=10, color=INK, anchor="start"))

    # Картка Generic Plan
    frags.append(rect(rx + 20, ry + 150, 485, 80, rx=6, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(text(rx + 35, ry + 172, "Загальний план (Generic Plan):", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(rx + 35, ry + 192, "• Генерується один раз без знання $1 (спирається на усереднену селективність)", size=10, color=INK, anchor="start"))
    frags.append(text(rx + 35, ry + 212, "• 0 витрат на планування, але ризик обрати неоптимальний оператор при Skew", size=10, color=INK, anchor="start"))

    # Алгоритм адаптації (Евристика 5 запусків)
    frags.append(rect(rx + 20, ry + 245, 485, 165, rx=6, fill="#eef9f1", stroke=FIELD, sw=1.5))
    frags.append(text(rx + 35, ry + 270, "Адаптивний вибір плану (plan_cache_mode = auto):", size=11, bold=True, color=FIELD, anchor="start"))

    steps_desc = [
        "1. Перші 5 запусків виконуються за Custom Plan, СУБД зберігає їхні оцінки вартості (C1..C5).",
        "2. На 6-й запуск оптимізатор додатково генерує Generic Plan з оцінкою вартості C_gen.",
        "3. Якщо C_gen <= Середнє(C1..C5) -> назавжди перемикається на Generic Plan (швидко).",
        "4. Якщо C_gen > Середнє(C1..C5) -> продовжує генерувати Custom Plan на кожен запит (точно)."
    ]
    for idx, s in enumerate(steps_desc):
        frags.append(text(rx + 35, ry + 298 + idx * 24, s, size=10, color=INK, anchor="start"))

    return render(os.path.join(OUT, 'generic-vs-custom-plan.svg'), W, H, *frags,
                  title="Дилема вибору плану: скошений розподіл даних та адаптивна евристика")


# ── 4. Конфлікт підготовлених виразів із пулом транзакцій ───────────────────
def fig_pooler_prepared_conflict():
    W, H = 980, 520
    frags = []

    # Клієнтська сторона
    frags.append(rect(40, 80, 160, 360, rx=8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(120, 110, "Застосунок", size=13, bold=True, color=NEG))
    frags.append(text(120, 130, "(Web App / API)", size=10, color=MUTED))

    frags.append(rect(55, 170, 130, 60, rx=4, fill="#ffffff", stroke=NEG, sw=1.2))
    frags.append(text(120, 195, "Запит 1 (Tx A)", size=11, bold=True, color=INK))
    frags.append(text(120, 215, "PREPARE 'p1'...", size=9, color=NEG))

    frags.append(rect(55, 290, 130, 60, rx=4, fill="#ffffff", stroke=NEG, sw=1.2))
    frags.append(text(120, 315, "Запит 2 (Tx B)", size=11, bold=True, color=INK))
    frags.append(text(120, 335, "EXECUTE 'p1'...", size=9, color=NEG))

    # Пул з'єднань (Transaction Pooling)
    frags.append(rect(260, 80, 220, 360, rx=8, fill="#fdfaf3", stroke="#d97706", sw=1.5))
    frags.append(text(370, 110, "Пул з'єднань", size=13, bold=True, color="#d97706"))
    frags.append(text(370, 130, "PgBouncer (Transaction Mode)", size=10, color=MUTED))

    frags.append(fitbox(275, 160, 190, 80,
                        "Транзакція A завершилась:\nз'єднання #1 повертається\nдо вільного пулу",
                        size=10, color=INK, fill="#ffffff", stroke="#d97706"))

    frags.append(fitbox(275, 280, 190, 80,
                        "Транзакція B починається:\nпулер призначає інше\nвільне з'єднання #2",
                        size=10, color=INK, fill="#ffffff", stroke="#d97706"))

    # Серверна сторона (Backend процеси)
    # Backend 1
    frags.append(rect(540, 80, 400, 165, rx=8, fill="#eef9f1", stroke=FIELD, sw=1.5))
    frags.append(text(740, 105, "PostgreSQL Backend #1 (Процес 1042)", size=12, bold=True, color=FIELD))
    frags.append(rect(560, 125, 360, 100, rx=4, fill="#ffffff", stroke=FIELD, sw=1.2))
    frags.append(text(740, 150, "Локальний кеш сесії Backend #1:", size=10, bold=True, color=INK))
    frags.append(text(740, 175, "Ім'я 'p1' -> [План SELECT id, name FROM ..]", size=10, bold=True, color=FIELD))
    frags.append(text(740, 205, "Вираз підготовлено і доступний лише тут", size=9, color=MUTED, italic=True))

    # Backend 2
    frags.append(rect(540, 275, 400, 165, rx=8, fill="#fdf3f2", stroke=POS, sw=1.5))
    frags.append(text(740, 300, "PostgreSQL Backend #2 (Процес 1043)", size=12, bold=True, color=POS))
    frags.append(rect(560, 320, 360, 100, rx=4, fill="#ffffff", stroke=POS, sw=1.2))
    frags.append(text(740, 345, "Локальний кеш сесії Backend #2:", size=10, bold=True, color=INK))
    frags.append(text(740, 375, "Кеш порожній (вираз 'p1' не знайдено!)", size=10, bold=True, color=POS))
    frags.append(text(740, 405, "ERROR: prepared statement \"p1\" does not exist", size=10, bold=True, color=POS))

    # Стрілки маршрутизації
    frags.append(arrow(185, 200, 260, 200, color=NEG, sw=1.8))
    frags.append(arrow(480, 180, 540, 160, color=FIELD, sw=1.8))

    frags.append(arrow(185, 320, 260, 320, color=NEG, sw=1.8))
    frags.append(arrow(480, 320, 540, 340, color=POS, sw=1.8))

    frags.append(text(490, 475, "Рішення: безіменні вирази (unnamed statements), клієнтський кеш підготовки або Session Pooling", size=11, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'pooler-prepared-conflict.svg'), W, H, *frags,
                  title="Конфлікт стану підготовлених виразів із пулом транзакцій")


def main():
    fig_statement_lifecycle()
    fig_ast_param_isolation()
    fig_generic_vs_custom_plan()
    fig_pooler_prepared_conflict()
    print("Усі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
