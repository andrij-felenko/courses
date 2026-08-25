# -*- coding: utf-8 -*-
"""Фігури до теми «Віртуальне дерево подання і звіряння (diffing)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння: Легковажний VNode проти Важковагового Real DOM ─────────────
def fig_vnode_vs_real_dom():
    W, H = 1000, 560
    f = []

    f.append(text(500, 35, "Анатомія вузлів: віртуальний об'єкт V8 проти системного DOM-вузла Blink/WebKit", size=15, bold=True))

    # Ліва колонка: Virtual Node (JS Heap)
    f.append(rect(50, 70, 420, 460, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    f.append(text(260, 100, "VIRTUAL DOM NODE (VNode)", size=14, color=FIELD, bold=True))
    f.append(text(260, 122, "Чистий об'єкт JavaScript у купі V8 (~80–120 байтів)", size=11.5, color=MUTED))

    # Складові VNode
    vnode_props = (
        "Структура VNode (Plain Old JS Object):\n"
        "• type: 'div' (рядковий тег або функція)\n"
        "• key: 'item-42' (стабільний ідентифікатор)\n"
        "• props: { className: 'card', onClick: fn }\n"
        "• children: [ vnodeA, vnodeB ] (масив посилань)\n"
        "• el: HTMLDivElement (посилання на DOM-вузол)\n"
        "• flags: 1 (ShapeFlag: Element, Stateful)"
    )
    f.append(fitbox(70, 140, 380, 165, vnode_props, size=11.5, fill="#ffffff", stroke="#86efac"))

    vnode_benefits = (
        "Властивості та ціна:\n"
        "+ Швидка алокація в молодому поколінні V8 (~наносекунди)\n"
        "+ Детермінованість і повна ізоляція від платформи\n"
        "+ Читання та зміна полів не чіпають графічний конвеєр\n"
        "+ Можливість рендерингу на сервері (SSR) чи у Worker"
    )
    f.append(fitbox(70, 325, 380, 185, vnode_benefits, size=11, fill="#ffffff", stroke=FIELD))

    # Права колонка: Real DOM Node (C++ Engine)
    f.append(rect(530, 70, 420, 460, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    f.append(text(740, 100, "REAL DOM NODE (HTMLDivElement)", size=14, color=POS, bold=True))
    f.append(text(740, 122, "Системний об'єкт C++ у ядрі браузера (~1.5–4.0 КБ)", size=11.5, color=MUTED))

    # Складові Real DOM
    dom_props = (
        "Пов'язані структури ядра Blink / WebKit:\n"
        "• Node / Element / EventTarget (ієрархія C++ класів)\n"
        "• CSSComputedStyleDeclaration (дерево стилів)\n"
        "• LayoutObject / LayoutBox (координати x, y, w, h)\n"
        "• PaintLayer / CompositedLayer (шари для GPU)\n"
        "• EventListenerMap (таблиця слухачів подій)\n"
        "• V8 Wrapper / DOM Binding (міст між JS та C++)"
    )
    f.append(fitbox(550, 140, 380, 165, dom_props, size=11.5, fill="#ffffff", stroke="#fca5a5"))

    dom_penalties = (
        "Графічний конвеєр при мутації:\n"
        "− Recalculate Style: підбір CSS-селекторів для дерева\n"
        "− Layout (Reflow): розрахунок геометрії та переносів\n"
        "− Paint & Composite: перемальовка та розбиття на тайли\n"
        "− Ризик Layout Thrashing при чергуванні читань і записів"
    )
    f.append(fitbox(550, 325, 380, 185, dom_penalties, size=11, fill="#ffffff", stroke=POS))

    # Центральна стрілка зв'язку
    f.append(arrow(475, 220, 525, 220, color=MUTED, sw=2))
    f.append(text(500, 210, "el", size=12, color=MUTED, bold=True))

    render(os.path.join(OUT, 'vnode-vs-real-dom.svg'), W, H, *f)


# ── 2. Евристичне звіряння дерев O(N) ─────────────────────────────────────────
def fig_heuristic_tree_diff():
    W, H = 1040, 580
    f = []

    f.append(text(520, 30, "Евристичний алгоритм узгодження: порівняння за рівнями та типами тегів", size=15, bold=True))

    # Ліва частина: Старе дерево
    f.append(text(210, 65, "Попередній Virtual DOM (Old Tree)", size=13, color=MUTED, bold=True))
    f.append(rect(30, 80, 360, 470, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Вузли старого дерева
    f.append(textbox(210, 125, "<div id='root'>", size=12, fill="#ffffff", stroke=LINE, bold=True)[0])
    f.append(line(210, 145, 110, 195, color=LINE, sw=1.5))
    f.append(line(210, 145, 290, 195, color=LINE, sw=1.5))

    f.append(textbox(110, 215, "<header>", size=12, fill="#ffffff", stroke=LINE)[0])
    f.append(textbox(290, 215, "<ul key='list'>", size=12, fill="#fee2e2", stroke=POS, bold=True)[0])

    f.append(line(110, 235, 110, 285, color=LINE, sw=1.5))
    f.append(textbox(110, 305, "<h1> (Title)", size=11, fill="#ffffff", stroke=LINE)[0])

    f.append(line(290, 235, 235, 285, color=LINE, sw=1.5))
    f.append(line(290, 235, 335, 285, color=LINE, sw=1.5))
    f.append(textbox(235, 305, "<li key='a'>", size=10.5, fill="#fee2e2", stroke=POS)[0])
    f.append(textbox(335, 305, "<li key='b'>", size=10.5, fill="#fee2e2", stroke=POS)[0])

    # Права частина: Нове дерево
    f.append(text(830, 65, "Новий Virtual DOM (New Tree)", size=13, color=MUTED, bold=True))
    f.append(rect(650, 80, 360, 470, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Вузли нового дерева
    f.append(textbox(830, 125, "<div id='root'>", size=12, fill="#ffffff", stroke=LINE, bold=True)[0])
    f.append(line(830, 145, 730, 195, color=LINE, sw=1.5))
    f.append(line(830, 145, 930, 195, color=LINE, sw=1.5))

    f.append(textbox(730, 215, "<header>", size=12, fill="#ffffff", stroke=LINE)[0])
    f.append(textbox(930, 215, "<p class='empty'>", size=12, fill="#dcfce7", stroke=FIELD, bold=True)[0])

    f.append(line(730, 235, 730, 285, color=LINE, sw=1.5))
    f.append(textbox(730, 305, "<h1> (New Title)", size=11, fill="#eff6ff", stroke=NEG)[0])

    f.append(line(930, 235, 930, 285, color=LINE, sw=1.5))
    f.append(textbox(930, 305, "Список порожній", size=11, fill="#dcfce7", stroke=FIELD)[0])

    # Центральна панель: Евристики та рішення
    f.append(rect(410, 80, 220, 470, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    f.append(text(520, 105, "ПРАВИЛА ДИФІНГУ", size=11, bold=True, color=INK))

    # Рівень 1: однаковий тег
    f.append(fitbox(420, 130, 200, 75, "1. Той самий тип:\n<div> == <div>\nЗвіряємо props та атрибути", size=10.5, fill="#f1f5f9", stroke="#94a3b8"))

    # Рівень 2: ліва гілка
    f.append(fitbox(420, 225, 200, 85, "2. Мутація тексту:\nTitle → New Title\nDOM: textNode.data =\nбез заміни елемента", size=10, fill="#eff6ff", stroke=NEG))

    # Рівень 2: права гілка (різні теги)
    f.append(fitbox(420, 330, 200, 135, "3. Різні теги:\n<ul> !== <p>\nЕвристика:\nстаре <ul> піддерево демонтується,\nнове <p> монтується з нуля за O(1)", size=10, fill="#fef2f2", stroke=POS))

    render(os.path.join(OUT, 'heuristic-tree-diff.svg'), W, H, *f)


# ── 3. Двосторонній алгоритм узгодження (Double-Ended Diffing) ─────────────────
def fig_double_ended_diffing():
    W, H = 1000, 580
    f = []

    f.append(text(500, 30, "Двосторонній алгоритм узгодження (Double-Ended Diffing у Snabbdom та Vue 2)", size=15, bold=True))

    # Блок пояснення покажчиків
    f.append(fitbox(50, 60, 900, 55, 
                    "Алгоритм підтримує 4 покажчики та рухається назустріч від країв до центру масивів:\n"
                    "1. oldStart == newStart  |  2. oldEnd == newEnd  |  3. oldStart == newEnd (зсув вправо)  |  4. oldEnd == newStart (зсув вліво)", size=11.5, fill="#f8fafc", stroke="#cbd5e1"))

    # Масив Old Children
    f.append(text(120, 140, "Старі діти (Old):", size=13, bold=True, anchor="start"))
    old_items = [("A", 1), ("B", 2), ("C", 3), ("D", 4)]
    x_base = 120
    for i, (name, key) in enumerate(old_items):
        cx = x_base + i * 140 + 50
        col = "#eff6ff" if i in [0, 3] else "#ffffff"
        strk = NEG if i in [0, 3] else MUTED
        f.append(rect(cx - 50, 160, 100, 55, fill=col, stroke=strk, sw=1.5, rx=6))
        f.append(text(cx, 185, f"VNode '{name}'", size=12, bold=True))
        f.append(text(cx, 203, f"key: {key}", size=11, color=MUTED))

    # Покажчики старого масиву
    f.append(text(170, 245, "▲ oldStartIdx (0)", size=11, color=NEG, bold=True))
    f.append(text(590, 245, "▲ oldEndIdx (3)", size=11, color=NEG, bold=True))

    # 4 перевірки зіставлення
    f.append(rect(60, 270, 880, 120, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(500, 292, "ПОСЛІДОВНІСТЬ 4 ЕВРИСТИЧНИХ ПОРІВНЯНЬ НА КОЖНОМУ КРОЦІ ЦИКЛУ:", size=11.5, bold=True, color=INK))

    f.append(rect(80, 310, 195, 65, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(177, 332, "1. oldStart == newStart", size=11, bold=True))
    f.append(text(177, 352, "Патч + StartIdx++", size=10.5, color=FIELD))

    f.append(rect(295, 310, 195, 65, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(392, 332, "2. oldEnd == newEnd", size=11, bold=True))
    f.append(text(392, 352, "Патч + EndIdx--", size=10.5, color=FIELD))

    f.append(rect(510, 310, 195, 65, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(607, 332, "3. oldStart == newEnd", size=11, bold=True))
    f.append(text(607, 352, "DOM: insertBefore(end.next)", size=10.5, color=NEG))

    f.append(rect(725, 310, 195, 65, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(822, 332, "4. oldEnd == newStart", size=11, bold=True))
    f.append(text(822, 352, "DOM: insertBefore(start.el)", size=10.5, color=NEG))

    # Масив New Children
    f.append(text(120, 425, "Нові діти (New):", size=13, bold=True, anchor="start"))
    new_items = [("D", 4), ("A", 1), ("C", 3), ("B", 2)]
    for i, (name, key) in enumerate(new_items):
        cx = x_base + i * 140 + 50
        col = "#eff6ff" if i in [0, 3] else "#ffffff"
        strk = NEG if i in [0, 3] else MUTED
        f.append(rect(cx - 50, 445, 100, 55, fill=col, stroke=strk, sw=1.5, rx=6))
        f.append(text(cx, 470, f"VNode '{name}'", size=12, bold=True))
        f.append(text(cx, 488, f"key: {key}", size=11, color=MUTED))

    # Покажчики нового масиву
    f.append(text(170, 530, "▼ newStartIdx (0)", size=11, color=FIELD, bold=True))
    f.append(text(590, 530, "▼ newEndIdx (3)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'double-ended-diffing.svg'), W, H, *f)


# ── 4. Звіряння списків через LIS (Longest Increasing Subsequence) ────────────
def fig_key_reordering_lis():
    W, H = 1000, 560
    f = []

    f.append(text(500, 30, "Оптимізація переміщень у DOM через найдовшу зростаючу підпослідовність (LIS у Vue 3)", size=15, bold=True))

    # 1. Початковий стан
    f.append(text(100, 75, "1. Послідовність ключів у DOM (Old):", size=12, bold=True, anchor="start"))
    old_keys = ["a", "b", "c", "d", "e", "f", "g"]
    for i, k in enumerate(old_keys):
        x = 100 + i * 115
        f.append(rect(x, 90, 85, 45, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
        f.append(text(x + 42, 112, f"key: {k}", size=12, bold=True))
        f.append(text(x + 42, 126, f"idx: {i}", size=10, color=MUTED))

    # 2. Новий стан та індекси джерел
    f.append(text(100, 170, "2. Новий порядок ключів (New) та карта зміщень (Source Array):", size=12, bold=True, anchor="start"))
    new_keys = ["a", "c", "d", "b", "g", "e", "f"]
    sources  = [0,   2,   3,   1,   6,   4,   5] # індекси старих елементів

    for i, (k, src) in enumerate(zip(new_keys, sources)):
        x = 100 + i * 115
        in_lis = src in [0, 2, 3, 4, 5]
        bg = "#dcfce7" if in_lis else "#fee2e2"
        st = FIELD if in_lis else POS
        f.append(rect(x, 185, 85, 55, fill=bg, stroke=st, sw=2, rx=4))
        f.append(text(x + 42, 208, f"key: {k}", size=12, bold=True))
        f.append(text(x + 42, 226, f"oldIdx: {src}", size=10.5, color=INK))

    # 3. Обчислення LIS
    f.append(rect(100, 265, 800, 110, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(500, 290, "РОЗРАХУНОК LIS (Longest Increasing Subsequence) ЗА O(N log N):", size=12, bold=True))
    f.append(text(500, 315, "Масив старих індексів: [ 0, 2, 3, 1, 6, 4, 5 ]", size=12, color=INK))
    f.append(text(500, 340, "Найдовша зростаюча підпослідовність: [ 0, 2, 3, 4, 5 ] (ключі: a, c, d, e, f)", size=12, color=FIELD, bold=True))
    f.append(text(500, 362, "Ці елементи вже впорядковані відносно один одного — ЇХ НЕ ПОТРІБНО ПЕРЕМІЩУВАТИ!", size=11, color=FIELD))

    # 4. Результат: які операції виконує DOM
    f.append(text(100, 410, "3. Результуючі операції з реальним DOM:", size=12, bold=True, anchor="start"))

    f.append(fitbox(100, 430, 380, 105,
                    "СТАБІЛЬНІ ЯКОРІ (У LIS):\n"
                    "• Вузли 'a', 'c', 'd', 'e', 'f'\n"
                    "• Залишаються на своїх місцях у DOM\n"
                    "• 0 викликів insertBefore!", size=11, fill="#f0fdf4", stroke=FIELD))

    f.append(fitbox(520, 430, 380, 105,
                    "ПЕРЕМІЩУВАНІ ВУЗЛИ (ПОЗА LIS):\n"
                    "• Вузол 'b' (oldIdx:1): перемістити перед 'g'\n"
                    "• Вузол 'g' (oldIdx:6): перемістити перед 'e'\n"
                    "• Рівно 2 точкові операції insertBefore замість повної перебудови!", size=11, fill="#fef2f2", stroke=POS))

    render(os.path.join(OUT, 'key-reordering-lis.svg'), W, H, *f)


# ── 5. Порівняння: VDOM проти Fine-Grained Signals ───────────────────────────
def fig_vdom_vs_signals_pipeline():
    W, H = 1000, 560
    f = []

    f.append(text(500, 35, "Архітектурний конвеєр оновлення: Virtual DOM проти Fine-Grained Signals", size=15, bold=True))

    # Верхня половина: Virtual DOM Pipeline (React, Vue)
    f.append(rect(50, 65, 900, 220, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    f.append(text(70, 95, "АРХІТЕКТУРА 1: VIRTUAL DOM (React / Vue)", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(70, 115, "Декларативний рендеринг 'UI = f(state)' з обходом дерева", size=11, color=MUTED, anchor="start"))

    # Блоки VDOM
    f.append(textbox(140, 180, "Зміна стану\nsetState()", size=11, fill="#ffffff", stroke=LINE)[0])
    f.append(arrow(200, 180, 240, 180, color=MUTED, sw=1.5))

    f.append(textbox(320, 180, "Повний виклик\nRender Component", size=11, fill="#eff6ff", stroke=NEG)[0])
    f.append(arrow(400, 180, 440, 180, color=MUTED, sw=1.5))

    f.append(textbox(520, 180, "Алокація нового\nдерева VNode", size=11, fill="#fee2e2", stroke=POS)[0])
    f.append(arrow(600, 180, 640, 180, color=MUTED, sw=1.5))

    f.append(textbox(710, 180, "Tree Diffing\nO(N) порівняння", size=11, fill="#eff6ff", stroke=NEG)[0])
    f.append(arrow(780, 180, 820, 180, color=MUTED, sw=1.5))

    f.append(textbox(880, 180, "DOM Patch\nмутації", size=11, fill="#f0fdf4", stroke=FIELD, bold=True)[0])

    f.append(text(500, 255, "Ціна: пам'ять на алокацію VNode у V8 купі + CPU час на diffing дерева при кожному тику", size=11, color=POS, italic=True))

    # Нижня половина: Fine-Grained Signals Pipeline (Solid, Svelte 5)
    f.append(rect(50, 305, 900, 220, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(70, 335, "АРХІТЕКТУРА 2: FINE-GRAINED SIGNALS (Solid.js / Svelte 5 Runes)", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(70, 355, "Реактивний граф залежностей: компілятор зв'язує сигнал безпосередньо з DOM", size=11, color=MUTED, anchor="start"))

    # Блоки Signals
    f.append(textbox(160, 420, "Мутація сигналу\ncount.set(5)", size=11, fill="#ffffff", stroke=LINE)[0])
    f.append(arrow(240, 420, 340, 420, color=FIELD, sw=2))

    f.append(textbox(470, 420, "Сповіщення прямого підписника\nEffect Subscriber Graph", size=11, fill="#dcfce7", stroke=FIELD)[0])
    f.append(arrow(600, 420, 700, 420, color=FIELD, sw=2))

    f.append(textbox(800, 420, "Точкова мутація DOM\ntextNode.data = 5", size=11, fill="#dcfce7", stroke=FIELD, bold=True)[0])

    f.append(text(500, 495, "Переваги: 0 об'єктів VNode у пам'яті, 0 порівнянь дерева (Diff = 0), складність O(1) від кількості змін", size=11, color=FIELD, italic=True))

    render(os.path.join(OUT, 'vdom-vs-signals-pipeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_vnode_vs_real_dom()
    fig_heuristic_tree_diff()
    fig_double_ended_diffing()
    fig_key_reordering_lis()
    fig_vdom_vs_signals_pipeline()
    print("All figures generated successfully.")
