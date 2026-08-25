# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to courses root / scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_declarative_vs_imperative_model():
    W, H = 840, 430
    p = []

    # Left box: Imperative
    w_box = 370
    h_box = 320
    x_left = 35
    y_top = 65

    p.append(rect(x_left, y_top, w_box, h_box, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(x_left + w_box / 2, y_top + 24, "Імперативна парадигма (Фокус на «ЯК»)", size=12, color=POS, bold=True))
    p.append(text(x_left + w_box / 2, y_top + 42, "Покрокова зміна мутабельного стану в часі", size=10, color=MUTED, italic=True))
    p.append(line(x_left + 16, y_top + 52, x_left + w_box - 16, y_top + 52, color=POS, sw=1, dash="4 3"))

    # Steps inside imperative box
    y_s = y_top + 68
    steps = [
        "1. Вхідний стан: S0 = { i = 0, buf = [], sum = 0 }",
        "2. Цикл / переходи: if (user.age > 18) goto ...",
        "3. Мутація пам'яті: buf[i++] = user.name; sum += 1",
        "4. Керування ресурсами: manual free(ptr), unlock()"
    ]
    for s in steps:
        p.append(fitbox(x_left + 14, y_s, w_box - 28, 38, s, size=9.5, fill=BG, stroke=POS, sw=1, color=INK))
        y_s += 44

    # Bottom summary tag
    p.append(rect(x_left + 14, y_top + h_box - 46, w_box - 28, 34, fill=BG, stroke=POS, sw=1.4, rx=6))
    p.append(text(x_left + w_box / 2, y_top + h_box - 24, "Часова прив'язка, побічні ефекти, покажчики", size=9.5, color=POS, bold=True))

    # Right box: Declarative
    x_right = 435
    p.append(rect(x_right, y_top, w_box, h_box, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(x_right + w_box / 2, y_top + 24, "Декларативна парадигма (Фокус на «ЩО»)", size=12, color=FIELD, bold=True))
    p.append(text(x_right + w_box / 2, y_top + 42, "Опис цільового результату та інваріантів", size=10, color=MUTED, italic=True))
    p.append(line(x_right + 16, y_top + 52, x_right + w_box - 16, y_top + 52, color=FIELD, sw=1, dash="4 3"))

    # Steps inside declarative box
    y_s = y_top + 68
    dec_steps = [
        "1. Специфікація цілі: предикат P(x) = (age > 18)",
        "2. Трансформація: чиста функція f(x) → x.name",
        "3. Реляційне відношення: SELECT name WHERE P(x)",
        "4. Рушій виконання: оптимізує план і чергу сам"
    ]
    for s in dec_steps:
        p.append(fitbox(x_right + 14, y_s, w_box - 28, 38, s, size=9.5, fill=BG, stroke=FIELD, sw=1, color=INK))
        y_s += 44

    p.append(rect(x_right + 14, y_top + h_box - 46, w_box - 28, 34, fill=BG, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(x_right + w_box / 2, y_top + h_box - 24, "Референційна прозорість, безчасові інваріанти", size=9.5, color=FIELD, bold=True))

    p.append(text(W / 2, H - 15,
                  "Імперативний код задає алгоритм покроково; декларативний код задає властивості результату",
                  size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "declarative-vs-imperative-model.svg"), W, H, *p,
           title="Порівняння парадигм: Імперативне виконання проти Декларативної специфікації")


def fig_query_planner_pipeline():
    W, H = 840, 440
    p = []

    # 4 horizontal main blocks with arrows
    box_w = 175
    box_h = 295
    y_top = 70
    gap = 26
    start_x = 28

    stages = [
        ("1. Декларація", "Вихідний SQL-запит",
         ["SELECT name, score", "FROM users", "WHERE age >= 18", "  AND active = true"],
         "Опис сутності та обмежень",
         NEG, "#eaf0fd"),

        ("2. AST & Логічний план", "Реляційні оператори",
         ["Project [name, score]", "       ↑", "Filter [age >= 18 ∧ active]", "       ↑", "Scan [users table]"],
         "Дерево операцій реляційної алгебри",
         MUTED, FILL),

        ("3. Оптимізатор CBO", "Правила та статистика",
         ["Predicate Pushdown:", "фільтр опущено до Scan", "Index Scan вибору:", "використано індекс age_idx", "Cost: I/O + CPU min"],
         "Пошук найдешевшого плану",
         FIELD, "#eef6ef"),

        ("4. Фізичний план", "Імперативний ітератор",
         ["Volcano Iterator Model:", "Project.next()", "  -> IndexScan.next()", "CPU: покроковий цикл,", "читання сторінок з RAM"],
         "Покрокове виконання на CPU",
         POS, "#fdecea"),
    ]

    for i, (title_text, subtitle, lines_data, note, col, fill_col) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        p.append(rect(x, y_top, box_w, box_h, fill=fill_col, stroke=col, sw=1.8, rx=8))
        p.append(text(x + box_w / 2, y_top + 22, title_text, size=11, color=col, bold=True))
        p.append(text(x + box_w / 2, y_top + 38, subtitle, size=9.5, color=MUTED, italic=True))
        p.append(line(x + 10, y_top + 48, x + box_w - 10, y_top + 48, color=col, sw=1, dash="3 3"))

        # Text inside
        y_txt = y_top + 66
        for ln in lines_data:
            p.append(text(x + box_w / 2, y_txt, ln, size=9.5, color=INK, anchor="middle"))
            y_txt += 26

        # Note at bottom of card
        p.append(rect(x + 8, y_top + box_h - 48, box_w - 16, 38, fill=BG, stroke=col, sw=1, rx=5))
        p.append(fitbox(x + 10, y_top + box_h - 46, box_w - 20, 34, note, size=8.5, fill=BG, stroke=BG, color=col, bold=True))

        # Arrow to next stage
        if i < len(stages) - 1:
            arr_x1 = x + box_w + 3
            arr_x2 = arr_x1 + gap - 6
            arr_y = y_top + box_h / 2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=1.8))

    p.append(text(W / 2, H - 15,
                  "Планувальник перетворює безчасову реляційну декларацію на покроковий конвеєр викликів next()",
                  size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "query-planner-pipeline.svg"), W, H, *p,
           title="Трансляція декларативного SQL в імперативні інструкції процесора")


def fig_ui_reconciliation_loop():
    W, H = 840, 420
    p = []

    # Left: Two states
    x_st = 30
    w_st = 200
    h_st = 110

    # State A
    p.append(rect(x_st, 75, w_st, h_st, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    p.append(text(x_st + w_st / 2, 95, "Стан програми (t₀)", size=11, color=NEG, bold=True))
    p.append(text(x_st + w_st / 2, 115, "State = { count: 1, auth: true }", size=9.5, color=INK))
    p.append(rect(x_st + 12, 130, w_st - 24, 38, fill=BG, stroke=NEG, sw=1, rx=4))
    p.append(text(x_st + w_st / 2, 152, "UI = View(State) → Tree A", size=9.5, color=NEG, bold=True))

    # State B
    p.append(rect(x_st, 225, w_st, h_st, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(x_st + w_st / 2, 245, "Оновлений стан (t₁)", size=11, color=POS, bold=True))
    p.append(text(x_st + w_st / 2, 265, "State' = { count: 2, auth: true }", size=9.5, color=INK))
    p.append(rect(x_st + 12, 280, w_st - 24, 38, fill=BG, stroke=POS, sw=1, rx=4))
    p.append(text(x_st + w_st / 2, 302, "UI = View(State') → Tree B", size=9.5, color=POS, bold=True))

    # Middle box: Reconciliation Engine (Diffing)
    x_rec = 290
    w_rec = 250
    h_rec = 260
    y_rec = 75
    p.append(rect(x_rec, y_rec, w_rec, h_rec, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(x_rec + w_rec / 2, y_rec + 24, "Рушій реконсиляції (Diffing)", size=11.5, color=FIELD, bold=True))
    p.append(text(x_rec + w_rec / 2, y_rec + 42, "Порівняння двох віртуальних дерев", size=9.5, color=MUTED, italic=True))
    p.append(line(x_rec + 14, y_rec + 52, x_rec + w_rec - 14, y_rec + 52, color=FIELD, sw=1, dash="3 3"))

    rec_steps = [
        "1. Обхід дерева вузлів O(N)",
        "2. Порівняння типів і ключів key",
        "3. Виявлення змінених атрибутів",
        "4. Генерація списку патчів (Patch List):",
        "   - updateText(span_#1, '2')"
    ]
    y_rs = y_rec + 72
    for s in rec_steps:
        p.append(text(x_rec + 16, y_rs, s, size=9.5, color=INK, anchor="start"))
        y_rs += 32

    # Arrows from States to Reconciler
    p.append(arrow(x_st + w_st + 5, 130, x_rec - 8, 160, color=LINE, sw=1.6))
    p.append(arrow(x_st + w_st + 5, 280, x_rec - 8, 250, color=LINE, sw=1.6))

    # Right box: Imperative DOM / Target system
    x_dom = 600
    w_dom = 210
    h_dom = 260
    p.append(rect(x_dom, y_rec, w_dom, h_dom, fill=FILL, stroke=LINE, sw=1.8, rx=10))
    p.append(text(x_dom + w_dom / 2, y_rec + 24, "Мутабельний DOM / UI API", size=11.5, color=INK, bold=True))
    p.append(text(x_dom + w_dom / 2, y_rec + 42, "Імперативне оновлення екрана", size=9.5, color=MUTED, italic=True))
    p.append(line(x_dom + 14, y_rec + 52, x_dom + w_dom - 14, y_rec + 52, color=LINE, sw=1, dash="3 3"))

    dom_steps = [
        "Пакетний запис у браузер:",
        "element.nodeValue = '2';",
        "",
        "Уникнення повного",
        "перебудування дерева;",
        "Мінімальна кількість перемалювань",
        "(Reflow / Repaint)"
    ]
    y_ds = y_rec + 74
    for s in dom_steps:
        if s:
            p.append(text(x_dom + w_dom / 2, y_ds, s, size=9, color=INK, anchor="middle"))
        y_ds += 24

    # Arrow from Reconciler to DOM
    p.append(arrow(x_rec + w_rec + 5, y_rec + h_rec / 2, x_dom - 8, y_rec + h_rec / 2, color=LINE, sw=1.8))

    p.append(text(W / 2, H - 15,
                  "Розробник декларує вигляд UI для стану State; рушій вираховує мінімальні імперативні мутації",
                  size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "ui-reconciliation-loop.svg"), W, H, *p,
           title="Реконсиляція декларативного UI: перехід від стану до мутацій DOM")


if __name__ == "__main__":
    fig_declarative_vs_imperative_model()
    fig_query_planner_pipeline()
    fig_ui_reconciliation_loop()
    print("Figures generated successfully.")
