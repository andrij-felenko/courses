# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Порівняння розміщення в пам'яті: Масив проти Зв'язаного списка ──────
def fig1_array_vs_linked_list():
    W, H = 940, 480
    p = []

    # Ліва панель: Динамічний масив (суцільний блок)
    p.append(rect(20, 50, 435, 360, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(237.5, 78, "Динамічний масив (суцільна пам'ять)", size=14, color=INK, bold=True))
    
    # Смуга масиву
    ax, ay, aw, ah = 50, 140, 375, 55
    elements = ["Ел. 0\n[0x1000]", "Ел. 1\n[0x1008]", "Ел. 2\n[0x1010]", "Ел. 3\n[0x1018]"]
    ew = aw / len(elements)
    for i, el in enumerate(elements):
        p.append(rect(ax + i * ew, ay, ew, ah, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=0))
        lines = el.split("\n")
        p.append(text(ax + i * ew + ew / 2, ay + 22, lines[0], size=12, color=INK, bold=True))
        p.append(text(ax + i * ew + ew / 2, ay + 42, lines[1], size=10, color=MUTED))

    # Стрілка індексації
    p.append(fitbox(50, 230, 375, 45, "Адреса(i) = Base + i × sizeof(T)\nДоступ за індексом O(1) за 1 операцію CPU",
                    size=12, fill="#eef7f0", stroke=FIELD, color=INK))

    # Недолік масиву
    p.append(fitbox(50, 300, 375, 85,
                    "Вставка/Видалення в середину:\nВимагає зсуву решти N-1 елементів у RAM\nЧасова складність: O(N)",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # Права панель: Зв'язаний список (розпорошені вузли)
    p.append(rect(485, 50, 435, 360, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(702.5, 78, "Зв'язаний список (вузли в купі)", size=14, color=INK, bold=True))

    # Вузли списку у довільних адресах
    nodes = [
        (515, 130, "Вузол A\n0x1040", "0x4080"),
        (720, 130, "Вузол B\n0x4080", "0x2010"),
        (580, 250, "Вузол C\n0x2010", "NULL")
    ]
    
    for nx, ny, title, nxt in nodes:
        # Вузол: дві секції (Дані | Покажчик)
        p.append(rect(nx, ny, 110, 50, fill="#ffffff", stroke="#aab4c0", sw=1.5, rx=5))
        p.append(rect(nx, ny, 60, 50, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=3))
        p.append(rect(nx + 60, ny, 50, 50, fill="#f4f6f8", stroke="#aab4c0", sw=1.3, rx=3))
        
        t_lines = title.split("\n")
        p.append(text(nx + 30, ny + 22, t_lines[0], size=11, color=INK, bold=True))
        p.append(text(nx + 30, ny + 40, t_lines[1], size=9, color=MUTED))
        p.append(text(nx + 85, ny + 30, nxt, size=9.5, color=NEG, bold=True))

    # Стрілки-покажчики
    p.append(arrow(625, 155, 720, 155, color=NEG, sw=1.8))
    p.append(arrow(775, 180, 690, 250, color=NEG, sw=1.8))

    # Перевага та недолік списку
    p.append(fitbox(515, 325, 375, 60,
                    "Вставка/Видалення вузла: O(1) перенаправленням покажчика\nПошук / Доступ за індексом: O(N) послідовним обходом",
                    size=12, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "fig1-array-vs-linked-list.svg"), W, H, *p,
           title="Структура пам'яті: Суцільний масив проти розпорошеного зв'язаного списка")


# ── Фіг. 2: Однозв'язаний та Двохзв'язаний списки ──────────────────────────────
def fig2_singly_vs_doubly():
    W, H = 920, 460
    p = []

    # Верхній блок: Однозв'язаний список
    p.append(rect(20, 50, 880, 175, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(460, 75, "Однозв'язаний список (Singly Linked List)", size=14, color=INK, bold=True))

    # Head вказівник
    p.append(rect(45, 120, 70, 45, fill="#fdf0dc", stroke="#e08a1e", sw=1.5, rx=5))
    p.append(text(80, 147, "head", size=12, color="#e08a1e", bold=True))
    p.append(arrow(115, 142.5, 160, 142.5, color="#e08a1e", sw=1.8))

    # Вузли однозв'язаного
    s_nodes = [(160, "10"), (360, "25"), (560, "42")]
    for x, val in s_nodes:
        p.append(rect(x, 120, 110, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
        p.append(rect(x, 120, 60, 45, fill="#eef7f0", stroke=FIELD, sw=1.2, rx=3))
        p.append(text(x + 30, 147, val, size=14, color=INK, bold=True))
        p.append(text(x + 85, 147, "next", size=11, color=NEG, bold=True))

    p.append(arrow(270, 142.5, 360, 142.5, color=NEG, sw=1.8))
    p.append(arrow(470, 142.5, 560, 142.5, color=NEG, sw=1.8))
    p.append(line(670, 142.5, 710, 142.5, color=NEG, sw=1.8))
    p.append(text(735, 147, "NULL", size=12, color=MUTED, bold=True))

    # Нижній блок: Двохзв'язаний список
    p.append(rect(20, 245, 880, 190, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(460, 270, "Двохзв'язаний список (Doubly Linked List)", size=14, color=INK, bold=True))

    # Head & Tail
    p.append(rect(45, 320, 65, 45, fill="#fdf0dc", stroke="#e08a1e", sw=1.5, rx=5))
    p.append(text(77.5, 347, "head", size=11.5, color="#e08a1e", bold=True))
    p.append(arrow(110, 342.5, 150, 342.5, color="#e08a1e", sw=1.8))

    d_nodes = [(150, "A"), (390, "B"), (630, "C")]
    for x, val in d_nodes:
        # Вузол з 3 полями: Prev | Data | Next
        p.append(rect(x, 320, 140, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
        p.append(rect(x, 320, 40, 45, fill="#eaf0fd", stroke=NEG, sw=1.1, rx=3))
        p.append(rect(x + 40, 320, 60, 45, fill="#eef7f0", stroke=FIELD, sw=1.1, rx=3))
        p.append(rect(x + 100, 320, 40, 45, fill="#eaf0fd", stroke=NEG, sw=1.1, rx=3))
        
        p.append(text(x + 20, 347, "prev", size=10, color=NEG))
        p.append(text(x + 70, 347, val, size=14, color=INK, bold=True))
        p.append(text(x + 120, 347, "next", size=10, color=NEG))

    # Двонапрямлені стрілки
    p.append(arrow(290, 335, 390, 335, color=NEG, sw=1.6))
    p.append(arrow(390, 350, 290, 350, color=POS, sw=1.6))

    p.append(arrow(530, 335, 630, 335, color=NEG, sw=1.6))
    p.append(arrow(630, 350, 530, 350, color=POS, sw=1.6))

    # Tail pointer
    p.append(rect(800, 320, 65, 45, fill="#fdf0dc", stroke="#e08a1e", sw=1.5, rx=5))
    p.append(text(832.5, 347, "tail", size=11.5, color="#e08a1e", bold=True))
    p.append(arrow(800, 342.5, 770, 342.5, color="#e08a1e", sw=1.8))

    render(os.path.join(OUT, "fig2-singly-vs-doubly.svg"), W, H, *p,
           title="Анатомія вузлів: Однозв'язаний та Двохзв'язаний списки")


# ── Фіг. 3: Покроковий алгоритм вставки вузла ──────────────────────────────────
def fig3_insert_after():
    W, H = 920, 500
    p = []

    # 3 Кроки вставки елемента N між A та B
    steps = [
        (30, "Крок 1: Створення нового вузла N", "N->next = A->next", "#eef2f8"),
        (325, "Крок 2: Зв'язування нового вузла", "N->next показує на B", "#eef7f0"),
        (620, "Крок 3: Перенаправлення покажчика A", "A->next = N (O(1) операція)", "#eef7f0")
    ]

    for x, title, code_note, bg_col in steps:
        p.append(rect(x, 50, 270, 420, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        p.append(fitbox(x + 10, 65, 250, 30, title, size=11.5, bold=True, fill=bg_col, stroke=FIELD, color=INK))

    # Крок 1 схеми
    p.append(rect(60, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(100, 165, "Вузол A", size=12, bold=True))
    p.append(rect(180, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(220, 165, "Вузол B", size=12, bold=True))
    p.append(arrow(140, 160, 180, 160, color=NEG, sw=1.6))
    
    # Новий вузол N під ними
    p.append(rect(120, 260, 90, 45, fill="#fdecea", stroke=POS, sw=1.6, rx=5))
    p.append(text(165, 287, "Новий N", size=12, color=POS, bold=True))
    p.append(text(165, 380, "Створено вузол N\nу пам'яті купи", size=11, color=MUTED))

    # Крок 2 схеми
    p.append(rect(355, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(395, 165, "Вузол A", size=12, bold=True))
    p.append(rect(475, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(515, 165, "Вузол B", size=12, bold=True))
    p.append(line(435, 160, 475, 160, color=MUTED, sw=1.2, dash="4 4"))

    p.append(rect(415, 260, 90, 45, fill="#fdecea", stroke=POS, sw=1.6, rx=5))
    p.append(text(460, 287, "Новий N", size=12, color=POS, bold=True))
    # Стрілка N -> B (Крок 2)
    p.append(arrow(475, 260, 505, 185, color=POS, sw=1.8))
    p.append(text(460, 380, "N->next = A->next\n(безпечний порядок!)", size=11, color=POS, bold=True))

    # Крок 3 схеми
    p.append(rect(650, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(690, 165, "Вузол A", size=12, bold=True))
    p.append(rect(770, 140, 80, 40, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(810, 165, "Вузол B", size=12, bold=True))

    p.append(rect(710, 260, 90, 45, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=5))
    p.append(text(755, 287, "Вузол N", size=12, color=FIELD, bold=True))

    # Стрілки A -> N і N -> B
    p.append(arrow(690, 180, 725, 260, color=FIELD, sw=1.8))
    p.append(arrow(770, 260, 800, 185, color=FIELD, sw=1.8))
    p.append(text(755, 380, "A->next = N\nВставку завершено!", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "fig3-insert-after.svg"), W, H, *p,
           title="Покроковий алгоритм вставки вузла за O(1) без зсуву даних")


# ── Фіг. 4: Вузол-вартовий (Dummy/Sentinel node) ──────────────────────────────
def fig4_sentinel_node():
    W, H = 920, 460
    p = []

    # Верх: Ззвичайний список з перевіркою NULL
    p.append(rect(20, 50, 880, 180, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(460, 75, "Без вартового: крайові випадки вимагають if (head == NULL)", size=13.5, color=POS, bold=True))

    p.append(rect(50, 125, 75, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    p.append(text(87.5, 152, "head", size=12, color=POS, bold=True))

    p.append(arrow(125, 147.5, 180, 147.5, color=POS, sw=1.6))

    # Окремі перевірки на NULL для порожнього списка чи першого елемента
    p.append(rect(180, 125, 110, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
    p.append(text(235, 152, "Вузол 1", size=12, bold=True))
    p.append(arrow(290, 147.5, 350, 147.5, color=NEG, sw=1.6))
    p.append(rect(350, 125, 110, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
    p.append(text(405, 152, "Вузол 2", size=12, bold=True))

    p.append(fitbox(500, 125, 380, 70,
                    "Увага: видалення head вимагає переписати саму змінну head.\nВидалення з середини вимагає перевірки prev != NULL.\nКод містить безліч гілок if/else.",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    # Низ: Список з фіктивним вузлом-вартовим
    p.append(rect(20, 250, 880, 190, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(460, 275, "З вартовим (Sentinel): head завжди вказує на фіктивний вузол", size=13.5, color=FIELD, bold=True))

    p.append(rect(50, 325, 75, 45, fill="#fdf0dc", stroke="#e08a1e", sw=1.5, rx=5))
    p.append(text(87.5, 352, "head", size=12, color="#e08a1e", bold=True))
    p.append(arrow(125, 347.5, 175, 347.5, color="#e08a1e", sw=1.6))

    # Вузол-вартовий
    p.append(rect(175, 325, 130, 45, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=5))
    p.append(text(240, 352, "SENTINEL (Dummy)", size=11, color=FIELD, bold=True))

    p.append(arrow(305, 347.5, 360, 347.5, color=FIELD, sw=1.8))
    p.append(rect(360, 325, 110, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
    p.append(text(415, 352, "Вузол 1", size=12, bold=True))
    p.append(arrow(470, 347.5, 525, 347.5, color=NEG, sw=1.6))
    p.append(rect(525, 325, 110, 45, fill="#ffffff", stroke="#aab4c0", sw=1.4, rx=5))
    p.append(text(580, 352, "Вузол 2", size=12, bold=True))

    p.append(fitbox(660, 325, 220, 70,
                    "Перевага:\nСписок ніколи не порожній!\nКожна вставка і видалення —\nце insert_after / remove_after\nбез жодного if (head == NULL).",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "fig4-sentinel-node.svg"), W, H, *p,
           title="Усунення спеціальних крайових випадків за допомогою вузла-вартового")


# ── Фіг. 5: Вплив на кеш CPU (Spatial Locality vs Pointer Chasing) ─────────────
def fig5_cache_miss_comparison():
    W, H = 940, 500
    p = []

    # Верхня панель: Кеш-лінія 64B і масив
    p.append(rect(20, 50, 900, 195, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(470, 75, "Послідовний масив: 1 Cache Miss завантажує цілу кеш-лінію (64 байти)", size=13.5, color=FIELD, bold=True))

    p.append(rect(60, 110, 820, 60, fill="#eef7f0", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(470, 125, "L1 Cache Line (64 Bytes)", size=11, color=FIELD, bold=True))

    # 8 елементів uint64 по 8 байтів
    for i in range(8):
        bx = 75 + i * 100
        p.append(rect(bx, 135, 90, 30, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
        p.append(text(bx + 45, 155, "A[%d]" % i, size=11, color=INK, bold=True))

    p.append(fitbox(60, 185, 820, 45,
                    "Результат: Перший доступ A[0] викликає промах (Cache Miss ~50 нс). Наступні 7 елементів A[1..7] вже в L1-кеші! Hit Rate = 87.5%",
                    size=11.5, fill="#eef7f0", stroke=FIELD, color=INK))

    # Нижня панель: Покажчикова гонитва (Pointer Chasing) у списку
    p.append(rect(20, 260, 900, 220, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(470, 285, "Зв'язаний список: Кожен вузол у випадковій адресі RAM (Pointer Chasing)", size=13.5, color=POS, bold=True))

    # 3 кеш-лінії в різних місцях RAM
    cl_boxes = [
        (60, 320, "RAM 0x1000\n[Вузол A | next=0x8040]\nMiss #1 (50 нс)"),
        (360, 320, "RAM 0x8040\n[Вузол B | next=0x3010]\nMiss #2 (50 нс)"),
        (660, 320, "RAM 0x3010\n[Вузол C | next=NULL]\nMiss #3 (50 нс)")
    ]

    for cx, cy, label in cl_boxes:
        p.append(rect(cx, cy, 220, 75, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
        lines = label.split("\n")
        p.append(text(cx + 110, cy + 22, lines[0], size=11, color=MUTED))
        p.append(text(cx + 110, cy + 42, lines[1], size=11.5, color=INK, bold=True))
        p.append(text(cx + 110, cy + 62, lines[2], size=11, color=POS, bold=True))

    p.append(arrow(280, 357.5, 360, 357.5, color=POS, sw=1.8))
    p.append(arrow(580, 357.5, 660, 357.5, color=POS, sw=1.8))

    p.append(fitbox(60, 410, 820, 55,
                    "Результат: CPU вимушений чекати (Stall) при кожному переході по next. 100% Cache Misses для кожного вузла!\nЗатримка обходу N вузлів у N разів більша за масив.",
                    size=11.5, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(OUT, "fig5-cache-miss-comparison.svg"), W, H, *p,
           title="Аналіз локальності даних: Послідовна кеш-лінія проти покажчикової гонитви")


# ── Фіг. 6: Внутрішньо-структурний список Ядра Linux (struct list_head) ───────
def fig6_kernel_list_head():
    W, H = 920, 480
    p = []

    p.append(rect(20, 50, 880, 400, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(460, 75, "Інтрузивний список Linux Kernel: struct list_head вбудовано в структури даних", size=13.5, color=INK, bold=True))

    # Дві структури даних типу task_struct
    task1_x, task2_x = 80, 520

    for tx, name, pid in [(task1_x, "struct task_struct (Process 1)", "PID = 1042"),
                          (task2_x, "struct task_struct (Process 2)", "PID = 1043")]:
        p.append(rect(tx, 110, 320, 240, fill="#ffffff", stroke="#aab4c0", sw=1.6, rx=8))
        p.append(text(tx + 160, 135, name, size=12.5, color=INK, bold=True))
        p.append(text(tx + 160, 155, pid, size=11, color=MUTED))
        
        # Поля структури
        p.append(rect(tx + 20, 170, 280, 30, fill="#f4f6f8", stroke="#cdd6e0", sw=1.0, rx=3))
        p.append(text(tx + 160, 190, "unsigned long state;", size=11, color=INK))
        p.append(rect(tx + 20, 210, 280, 30, fill="#f4f6f8", stroke="#cdd6e0", sw=1.0, rx=3))
        p.append(text(tx + 160, 230, "void *stack;", size=11, color=INK))

        # Вбудований list_head
        p.append(rect(tx + 20, 250, 280, 80, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=5))
        p.append(text(tx + 160, 272, "struct list_head tasks;", size=12, color=FIELD, bold=True))
        p.append(text(tx + 80, 305, "next", size=11, color=NEG, bold=True))
        p.append(text(tx + 240, 305, "prev", size=11, color=POS, bold=True))

    # Зв'язки між вбудованими list_head
    p.append(arrow( task1_x + 140, 300, task2_x + 40, 300, color=NEG, sw=2.0 ))
    p.append(arrow( task2_x + 200, 315, task1_x + 100, 315, color=POS, sw=2.0 ))

    # Пояснення container_of
    p.append(fitbox(120, 370, 680, 65,
                    "container_of(ptr, type, member):\nОбчислює адресу батьківського task_struct відніманням зміщення offsetof(type, member).\nДозволяє об'єднувати об'єкти у довільні списки без додаткового alloc для вузлів!",
                    size=12, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "fig6-kernel-list-head.svg"), W, H, *p,
           title="Архітектура інтрузивних списків у системному програмуванні")


if __name__ == "__main__":
    fig1_array_vs_linked_list()
    fig2_singly_vs_doubly()
    fig3_insert_after()
    fig4_sentinel_node()
    fig5_cache_miss_comparison()
    fig6_kernel_list_head()
    print("ALL SVGs GENERATED SUCCESSFULLY")
