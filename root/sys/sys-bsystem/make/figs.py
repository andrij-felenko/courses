# -*- coding: utf-8 -*-
"""Фігури до теми «make: правила, цілі, змінні й чому Makefile такий»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # треба перезібрати / небезпека
CLEAN = "#eaf7ef"     # чинне / безпечно
NEUTRAL = "#f8fafc"   # нейтральна панель

# ── 1. Двофазна модель виконання GNU Make ──────────────────────────────────
def fig_phases():
    W, H = 1020, 520
    parts = []

    # Фаза 1: Читання
    parts.append(rect(40, 50, 430, 420, fill="#f0f5ff", stroke=NEG, sw=2, rx=8))
    parts.append(text(255, 84, "Фаза 1: Зчитування та розбір (Read Phase)", size=15, bold=True, color=NEG))
    
    p1_items = [
        "1. Порядкове читання Makefile та include",
        "2. Негайне розгортання змінних (:=, ::=)",
        "3. Виконання директив ifeq/ifdef/include",
        "4. Виконання команд оболонки $(shell ...)",
        "5. Побудова графа залежностей (DAG) у пам'яті",
        "6. Відкладені змінні (=) і рецепти НЕ обчислюються"
    ]
    for i, item in enumerate(p1_items):
        bg_col = BG if i < 5 else "#fff6f5"
        strk = MUTED if i < 5 else POS
        parts.append(fitbox(55, 110 + i * 54, 400, 42, item, size=13, fill=bg_col, stroke=strk))

    # Стрілка між фазами
    parts.append(arrow(475, 260, 545, 260, color=LINE, sw=2.5))
    parts.append(text(510, 240, "DAG готовий", size=12, bold=True, color=MUTED))

    # Фаза 2: Виконання
    parts.append(rect(550, 50, 430, 420, fill="#f4faf5", stroke=FIELD, sw=2, rx=8))
    parts.append(text(765, 84, "Фаза 2: Виконання та оновлення (Execute Phase)", size=15, bold=True, color=FIELD))

    p2_items = [
        "1. Вибір цілі (перша явна або передана в CLI)",
        "2. Топологічний обхід графа залежностей (DFS)",
        "3. Порівняння міток часу: mtime(prereq) > mtime(target)",
        "4. Якщо ціль застаріла: розгортання рядків рецепта",
        "5. Обчислення автоматичних змінних ($@, $<, $^, $*)",
        "6. Запуск команд окремими підпроцесами sh -c"
    ]
    for i, item in enumerate(p2_items):
        bg_col = BG if i < 3 else "#eef8f1"
        strk = MUTED if i < 3 else FIELD
        parts.append(fitbox(565, 110 + i * 54, 400, 42, item, size=13, fill=bg_col, stroke=strk))

    parts.append(text(W / 2, 495, "Makefile не виконується лінійно зверху вниз: спершу повністю будується граф, а вже потім запускаються рецепти",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "read-phase-vs-execute-phase.svg"), W, H, *parts,
           title="Двофазна модель GNU Make: зчитування проти виконання")


# ── 2. Різновиди змінних і правила їхнього розгортання ─────────────────────
def fig_variables():
    W, H = 1040, 480
    parts = []

    x0, y0 = 40, 60
    head_widths = [110, 210, 200, 250, 190]
    headers = ["Оператор", "Тип присвоєння", "Коли розгортається", "Поведінка при $(X) в тілі", "Типове застосування"]

    # Заголовки таблиці
    cur_x = x0
    for h_txt, w in zip(headers, head_widths):
        parts.append(fitbox(cur_x, y0, w, 44, h_txt, size=13.5, bold=True, fill="#eef2f7", stroke=LINE))
        cur_x += w + 6

    rows_data = [
        (":=", "Негайне (simply expanded)", "У момент зчитування рядка", "Бере поточне значення (безпечно)", "Накопичення прапорців, системні шляхи", CLEAN, FIELD),
        ("=", "Відкладене (recursively expanded)", "Щоразу під час звернення", "Нескінченна рекурсія при самопосиланні!", "Шаблони команд, динамічні списки", DIRTY, POS),
        ("?=", "Умовне (conditional)", "Під час читання, якщо порожньо", "Лишає наявне значення (з CLI/оточення)", "Значення за замовчуванням для CC, CFLAGS", NEUTRAL, MUTED),
        ("+=", "Дописування (append)", "Залежить від типу змінної (:= чи =)", "Дописує через пробіл зі збереженням типу", "Розширення списків об'єктів або ключів", NEUTRAL, MUTED),
        ("!=", "Виконання оболонки (shell)", "Негайно у фазі читання", "Запускає команду sh і читає stdout", "Отримання git-ревізії, вивід pkg-config", "#f0f5ff", NEG)
    ]

    for row_idx, r in enumerate(rows_data):
        op, kind, when, behav, use, bg_c, strk_c = r
        cur_y = y0 + 52 + row_idx * 66
        cur_x = x0

        vals = [op, kind, when, behav, use]
        for col_idx, (v, w) in enumerate(zip(vals, head_widths)):
            is_op = (col_idx == 0)
            is_behav = (col_idx == 3 and strk_c == POS)
            f_size = 14 if is_op else 12.5
            b_flag = True if is_op or is_behav else False
            c_fill = bg_c if (is_op or col_idx == 1 or is_behav) else BG
            c_stroke = strk_c if (is_op or is_behav) else MUTED
            parts.append(fitbox(cur_x, cur_y, w, 58, v, size=f_size, bold=b_flag, fill=c_fill, stroke=c_stroke))
            cur_x += w + 6

    parts.append(text(W / 2, 455, "Використання := замість = унеможливлює приховану рекурсію та повторні дорогі виклики функцій",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "make-variable-expansion.svg"), W, H, *parts,
           title="Присвоєння змінних у Make: відкладене проти негайного")


# ── 3. Зіставлення шаблонного правила й автоматичні змінні ─────────────────
def fig_pattern_rule():
    W, H = 1000, 480
    parts = []

    # Шаблонне правило
    parts.append(fitbox(50, 45, 900, 54, "Шаблонне правило:   build/%.o:  src/%.c  include/%.h", size=16, bold=True, fill="#f8fafc", stroke=LINE))
    
    # Ціль для збірки
    parts.append(fitbox(80, 130, 240, 50, "Ціль: build/parser.o", size=14, bold=True, fill="#eef4ff", stroke=NEG))
    
    # Стрілка зіставлення
    parts.append(arrow(325, 155, 415, 155, color=NEG, sw=2))
    
    # Стебло
    parts.append(fitbox(425, 130, 220, 50, "Стебло (% / $*):\n«parser»", size=14, bold=True, fill="#fef3c7", stroke="#d97706"))

    # Стрілка до пререквізитів
    parts.append(arrow(650, 155, 735, 155, color=FIELD, sw=2))

    # Пререквізити
    parts.append(fitbox(745, 120, 210, 70, "Пререквізити:\nsrc/parser.c\ninclude/parser.h", size=13, bold=True, fill="#eaf7ef", stroke=FIELD))

    # Панель автоматичних змінних
    parts.append(rect(50, 220, 900, 205, fill=BG, stroke=MUTED, sw=1.5, rx=6))
    parts.append(text(500, 248, "Автоматичні змінні у рецепті цього правила", size=15, bold=True))

    vars_info = [
        ("$@", "build/parser.o", "Ім'я цілі, яку зараз будує правило", NEG),
        ("$<", "src/parser.c", "Перший пререквізит (одиниця компіляції)", FIELD),
        ("$^", "src/parser.c include/parser.h", "Усі пререквізити через пробіл без повторів", INK),
        ("$*", "parser", "Основа (stem) — частина, що збіглася з %", "#d97706")
    ]

    for idx, (v_name, v_val, v_desc, v_col) in enumerate(vars_info):
        vy = 265 + idx * 36
        parts.append(fitbox(70, vy, 60, 30, v_name, size=14, bold=True, fill="#f4f6f8", stroke=v_col))
        parts.append(text(145, vy + 20, "→", size=14, color=MUTED))
        parts.append(fitbox(170, vy, 270, 30, v_val, size=13, bold=True, fill="#f8fafc", stroke=MUTED))
        parts.append(text(460, vy + 20, v_desc, size=13, color=MUTED, anchor="start"))

    parts.append(text(W / 2, 455, "Автоматичні змінні доступні лише всередині рядків рецепта у фазі виконання",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "pattern-rule-chain.svg"), W, H, *parts,
           title="Зіставлення шаблонного правила та значення автоматичних змінних")


# ── 4. Рекурсивний Make проти Єдиного графа (Non-recursive) ────────────────
def fig_recursive():
    W, H = 1040, 520
    parts = []

    # Ліва половина: Рекурсивний Make
    parts.append(rect(40, 50, 450, 420, fill="#fff7f7", stroke=POS, sw=2, rx=8))
    parts.append(text(265, 82, "Рекурсивний Make (make -C)", size=15, bold=True, color=POS))

    parts.append(fitbox(60, 105, 410, 40, "Головний Makefile (ізольований DAG 1)", size=13, bold=True, fill=BG, stroke=POS))
    
    parts.append(arrow(180, 150, 180, 185, color=POS, sw=2))
    parts.append(text(130, 168, "make -C lib", size=11.5, bold=True, color=POS))
    
    parts.append(arrow(350, 150, 350, 185, color=POS, sw=2))
    parts.append(text(400, 168, "make -C app", size=11.5, bold=True, color=POS))

    parts.append(fitbox(60, 190, 195, 60, "lib/Makefile\n(ізольований DAG 2)\nбудує libfoo.a", size=12, fill="#fdecea", stroke=POS))
    parts.append(fitbox(275, 190, 195, 60, "app/Makefile\n(ізольований DAG 3)\nбудує app.o", size=12, fill="#fdecea", stroke=POS))

    flaws = [
        "✖ Граф розірвано на незалежні шматки",
        "✖ Неможливо відстежити зміни між підкаталогами",
        "✖ Помилки порядку збірки та дублювання роботи",
        "✖ Неповний паралелізм (-jN не бачить всю картину)"
    ]
    for i, fl in enumerate(flaws):
        parts.append(fitbox(60, 270 + i * 44, 410, 36, fl, size=12, fill=BG, stroke=POS))

    # Права половина: Нерекурсивний Make
    parts.append(rect(550, 50, 450, 420, fill="#f4faf5", stroke=FIELD, sw=2, rx=8))
    parts.append(text(775, 82, "Нерекурсивний Make (Єдиний DAG)", size=15, bold=True, color=FIELD))

    parts.append(fitbox(570, 105, 410, 40, "Головний Makefile (включає module.mk)", size=13, bold=True, fill=BG, stroke=FIELD))

    parts.append(fitbox(570, 160, 410, 85, "Єдиний зв'язний граф залежностей:\napp : bin/app ← obj/app.o ← src/app.c\n      bin/app ← lib/libfoo.a ← obj/foo.o ← lib/foo.c", size=12, bold=True, fill="#eaf7ef", stroke=FIELD))

    benefits = [
        "✓ Точний глобальний топологічний порядок",
        "✓ Зміна lib/foo.h миттєво перезбирає і libfoo, і app",
        "✓ Ідеальне завантаження процесорних ядер (-jN)",
        "✓ Жодного зайвого виклику процесів make"
    ]
    for i, ben in enumerate(benefits):
        parts.append(fitbox(570, 270 + i * 44, 410, 36, ben, size=12, fill=BG, stroke=FIELD))

    parts.append(text(W / 2, 495, "Розбиття Make на підпроцеси робить збірку сліпою до міжмодульних залежностей",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "recursive-make-dag.svg"), W, H, *parts,
           title="Рекурсивний Make проти цілісного графа залежностей")


if __name__ == "__main__":
    fig_phases()
    fig_variables()
    fig_pattern_rule()
    fig_recursive()
    print("ok")
