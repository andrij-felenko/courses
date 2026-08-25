# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо (чотири рівні вгору від book/programming/systems/process-vs-thread)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. process-vs-thread-layout: адресний простір процесу проти потоків ──────
def fig_process_vs_thread_layout():
    W, H = 840, 400
    p = []

    # Велика рамка: Процес A (адресний простір та ресурси)
    px, py, pw, ph = 40, 45, 760, 325
    p.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=LINE, sw=2, rx=12))
    p.append(text(px + 20, py + 26, "Процес (одиниця володіння ресурсами та ізоляції пам'яті)", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(px + pw - 20, py + 26, "Власний кореневий регістр CR3 / таблиця сторінок", size=11, color=MUTED, anchor="end", italic=True))

    # Ліва частина: Спільні ресурси процесу
    sx, sy, sw, sh = px + 20, py + 45, 300, 260
    p.append(rect(sx, sy, sw, sh, fill="#edf2f7", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(sx + sw / 2, sy + 22, "Спільний простір і ресурси процесу", size=12, color=INK, bold=True))

    shared_items = [
        ("Сегмент коду (.text)", "спільні машинні інструкції програми", "#e2e8f0"),
        ("Глобальні дані й BSS", "статичні та глобальні змінні", "#e2e8f0"),
        ("Динамічна пам'ять (купа / heap)", "malloc / new, спільні структури", "#dbeafe"),
        ("Таблиця дескрипторів файлів", "відкриті файли, сокети, канали", "#fef3c7"),
        ("Обробники сигналів та оточення", "сигнальні диспозиції, PID, UID, CWD", "#f1f5f9"),
    ]
    iy = sy + 38
    for title_txt, desc_txt, bg_col in shared_items:
        p.append(rect(sx + 10, iy, sw - 20, 38, fill=bg_col, stroke="#94a3b8", sw=1, rx=5))
        p.append(text(sx + 18, iy + 16, title_txt, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(sx + 18, iy + 30, desc_txt, size=9.5, color=MUTED, anchor="start"))
        iy += 43

    # Права частина: Потоки всередині процесу
    tx, ty, tw, th = px + 340, py + 45, 400, 260
    p.append(rect(tx, ty, tw, th, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(tx + tw / 2, ty + 22, "Потоки виконання (одиниці планування процесора)", size=12, color=INK, bold=True))

    threads = [
        ("Потік 1 (Main Thread)", "TID: 1040", NEG, [
            ("Регістри ядра: PC, SP, R0..R15", NEG),
            ("Власний стек (локальні змінні)", "#eff6ff"),
            ("TLS (локальна пам'ять потоку)", "#f8fafc")
        ]),
        ("Потік 2 (Worker Thread)", "TID: 1041", FIELD, [
            ("Регістри ядра: PC, SP, R0..R15", FIELD),
            ("Власний стек (локальні змінні)", "#f0fdf4"),
            ("TLS (локальна пам'ять потоку)", "#f8fafc")
        ])
    ]

    th_w = (tw - 30) / 2
    th_x = tx + 10
    for tname, tid_lbl, col, boxes in threads:
        p.append(rect(th_x, ty + 36, th_w, th - 48, fill="#ffffff", stroke=col, sw=1.4, rx=6))
        p.append(text(th_x + th_w / 2, ty + 54, tname, size=11, color=col, bold=True))
        p.append(text(th_x + th_w / 2, ty + 69, tid_lbl, size=10, color=MUTED))

        by = ty + 78
        for b_name, b_fill in boxes:
            b_stroke = col if b_fill == col else "#cbd5e1"
            b_txt_col = "#ffffff" if b_fill == col else INK
            p.append(rect(th_x + 8, by, th_w - 16, 36, fill=b_fill, stroke=b_stroke, sw=1, rx=4))
            p.append(mtext(th_x + th_w / 2, by + 14, [b_name.split(":")[0], b_name.split(":")[-1].strip() if ":" in b_name else ""], size=9.5, color=b_txt_col, bold=False))
            by += 42
        th_x += th_w + 10

    # Стрілки спільного доступу
    p.append(arrow(tx + 10, sy + 130, sx + sw, sy + 130, color=POS, sw=1.6))
    p.append(text(px + 330, sy + 122, "прямий доступ", size=9, color=POS, bold=True))

    p.append(text(W / 2, H - 12, "Усі потоки ділять єдиний адресний простір, але кожен має незалежний стек і регістри", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "process-vs-thread-layout.svg"), W, H, *p,
           title="Анатомія процесу та потоків у пам'яті")


# ── 2. clone-flags-spectrum: спектр розділення ресурсів через clone() ─────────
def fig_clone_flags_spectrum():
    W, H = 820, 360
    p = []

    p.append(text(W / 2, 25, "Спектр розділення ресурсів в ОС: від повної ізоляції до повного злиття", size=13, color=INK, bold=True))

    cols = [
        ("fork()", "Повний процес", POS, "#fff1f2", [
            ("Пам'ять (VM):", "Повна копія (COW)"),
            ("Дескриптори:", "Копія таблиці"),
            ("Файлова система:", "Копія стану"),
            ("Сигнали:", "Копія обробників"),
            ("Група потоків:", "Новий TGID (PID)")
        ], "Окрема програма\n(повна ізоляція)"),

        ("vfork() / rfork()", "Тимчасовий спільник", "#d97706", "#fffbeb", [
            ("Пам'ять (VM):", "Спільна (батько спить)"),
            ("Дескриптори:", "Спільні/копія"),
            ("Файлова система:", "Спільна/копія"),
            ("Сигнали:", "Копія"),
            ("Група потоків:", "Новий TGID")
        ], "Оптимізація під\nшвидкий execve()"),

        ("pthread_create()", "Класичний потік", NEG, "#eff6ff", [
            ("Пам'ять (VM):", "CLONE_VM (спільна)"),
            ("Дескриптори:", "CLONE_FILES (спільні)"),
            ("Файлова система:", "CLONE_FS (спільна)"),
            ("Сигнали:", "CLONE_SIGHAND"),
            ("Група потоків:", "CLONE_THREAD (той самий TGID)")
        ], "Паралельні обчислення\nу спільній пам'яті"),

        ("unshare / clone3", "Контейнеризація", FIELD, "#f0fdf4", [
            ("Пам'ять (VM):", "Ізольована"),
            ("Простір назв:", "CLONE_NEWPID / NET"),
            ("Монтування:", "CLONE_NEWNS"),
            ("Користувачі:", "CLONE_NEWUSER"),
            ("Контрольні групи:", "CLONE_NEWCGROUP")
        ], "Ізоляція ресурсів\n(Namespaces / Cgroups)")
    ]

    card_w = 175
    gap = 20
    start_x = (W - (4 * card_w + 3 * gap)) / 2
    cy = 50

    for i, (title_txt, sub_txt, col, bg_col, rows, footer_txt) in enumerate(cols):
        cx = start_x + i * (card_w + gap)
        p.append(rect(cx, cy, card_w, 260, fill=bg_col, stroke=col, sw=1.6, rx=8))
        p.append(text(cx + card_w / 2, cy + 22, title_txt, size=12, color=col, bold=True))
        p.append(text(cx + card_w / 2, cy + 38, sub_txt, size=10, color=MUTED, italic=True))
        p.append(line(cx + 8, cy + 46, cx + card_w - 8, cy + 46, color=col, sw=1))

        ry = cy + 62
        for rk, rv in rows:
            p.append(text(cx + 10, ry, rk, size=9.5, color=INK, bold=True, anchor="start"))
            p.append(text(cx + 10, ry + 13, rv, size=9, color=MUTED, anchor="start"))
            ry += 28

        p.append(line(cx + 8, cy + 208, cx + card_w - 8, cy + 208, color="#cbd5e1", sw=1))
        p.append(mtext(cx + card_w / 2, cy + 224, footer_txt, size=9.5, color=col, bold=True))

    p.append(text(W / 2, H - 12, "Системний виклик clone() сприймає процес і потік як точки на єдиній шкалі прапорців спільності", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "clone-flags-spectrum.svg"), W, H, *p,
           title="Спектр прапорців clone в ядрі")


# ── 3. cost-breakdown: вартість перемикання та роботи (процес vs потік) ───────
def fig_cost_breakdown():
    W, H = 820, 360
    p = []

    p.append(text(W / 2, 25, "Анатомія витрат: перемикання контексту процесу проти потоку", size=13, color=INK, bold=True))

    # Лівий блок: Перемикання двох потоків одного процесу
    lx, ly, lw, lh = 50, 50, 340, 260
    p.append(rect(lx, ly, lw, lh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "Перемикання між ПОТОКАМИ", size=13, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, ly + 40, "(в межах одного процесу)", size=10.5, color=MUTED))

    t_steps = [
        ("1. Зберегти регістри CPU (PC, SP, R0..R15)", "кілька десятків наносекунд"),
        ("2. Залишити таблицю сторінок (CR3 без змін)", "0 нс (той самий адресний простір)"),
        ("3. Зберегти кеш трансляцій (TLB валідний)", "немає скидання або промахів"),
        ("4. Кеш інструкцій та даних L1/L2 лишається теплим", "дані й код спільні"),
        ("Підсумок: дешева операція ~100–300 нс", "мінімальні непрямі втрати")
    ]
    ty = ly + 60
    for s_txt, s_cost in t_steps:
        is_summary = "Підсумок" in s_txt
        bg = "#dcfce7" if is_summary else "#ffffff"
        strk = FIELD if is_summary else "#bbf7d0"
        p.append(rect(lx + 12, ty, lw - 24, 34, fill=bg, stroke=strk, sw=1.2, rx=5))
        p.append(text(lx + 20, ty + 15, s_txt, size=10, color=(FIELD if is_summary else INK), bold=is_summary, anchor="start"))
        p.append(text(lx + 20, ty + 28, s_cost, size=9, color=MUTED, anchor="start"))
        ty += 38

    # Правий блок: Перемикання двох різних процесів
    rx, ry, rw, rh = 430, 50, 340, 260
    p.append(rect(rx, ry, rw, rh, fill="#fff1f2", stroke=POS, sw=1.8, rx=10))
    p.append(text(rx + rw / 2, ry + 24, "Перемикання між ПРОЦЕСАМИ", size=13, color=POS, bold=True))
    p.append(text(rx + rw / 2, ry + 40, "(різні адресні простори)", size=10.5, color=MUTED))

    p_steps = [
        ("1. Зберегти регістри CPU (PC, SP, R0..R15)", "кілька десятків наносекунд"),
        ("2. Завантажити новий CR3 / таблицю сторінок", "зміна кореня трансляції MMU"),
        ("3. Інвалідація TLB (або фільтрація за PCID)", "промахи на кожному звертанні до RAM"),
        ("4. Охолодження L1/L2 кешів (cache pollution)", "нова програма витісняє старі рядки"),
        ("Підсумок: дорога операція ~1000–3000 нс + штраф кешу", "значні непрямі накладні витрати")
    ]
    py2 = ry + 60
    for s_txt, s_cost in p_steps:
        is_summary = "Підсумок" in s_txt
        bg = "#ffe4e6" if is_summary else "#ffffff"
        strk = POS if is_summary else "#fecdd3"
        p.append(rect(rx + 12, py2, rw - 24, 34, fill=bg, stroke=strk, sw=1.2, rx=5))
        p.append(text(rx + 20, py2 + 15, s_txt, size=10, color=(POS if is_summary else INK), bold=is_summary, anchor="start"))
        p.append(text(rx + 20, py2 + 28, s_cost, size=9, color=MUTED, anchor="start"))
        py2 += 38

    p.append(text(W / 2, H - 12, "Головна ціна зміни процесу — не збереження регістрів, а перемикання MMU й спустошення кешів", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cost-breakdown.svg"), W, H, *p,
           title="Порівняння вартості перемикання контексту")


# ── 4. architectural-choice-matrix: архітектурний вибір процеси проти потоків ─
def fig_architectural_choice_matrix():
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 25, "Архітектурний компроміс: ізоляція надійності проти ефективності спільного доступу", size=13, color=INK, bold=True))

    # Стовпчик 1: Багатопроцесна модель
    m1_x, m1_y, m1_w, m1_h = 50, 50, 355, 280
    p.append(rect(m1_x, m1_y, m1_w, m1_h, fill="#faf5ff", stroke="#9333ea", sw=1.8, rx=10))
    p.append(text(m1_x + m1_w / 2, m1_y + 24, "Багатопроцесна модель (Multi-Process)", size=12.5, color="#9333ea", bold=True))
    p.append(text(m1_x + m1_w / 2, m1_y + 40, "Chrome, PostgreSQL, Nginx, мікросервіси", size=10.5, color=MUTED, italic=True))

    p_pros = [
        ("Ізоляція збоїв (Fault Isolation)", "падіння однієї вкладки не вбиває весь браузер", FIELD),
        ("Безпека та пісочниця (Sandboxing)", "обмеження прав через seccomp, namespaces", FIELD),
        ("Простота очищення пам'яті", "ядро гарантовано звільняє ресурси при exit()", FIELD),
        ("Висока ціна комунікації (IPC)", "потрібні сокети, канали або спільна пам'ять", POS),
        ("Більший розхід RAM", "кожен процес має власні таблиці сторінок", POS)
    ]
    py_pos = m1_y + 54
    for title_txt, desc_txt, col in p_pros:
        p.append(rect(m1_x + 12, py_pos, m1_w - 24, 38, fill="#ffffff", stroke="#e9d5ff", sw=1, rx=5))
        p.append(text(m1_x + 20, py_pos + 15, title_txt, size=10.5, color=col, bold=True, anchor="start"))
        p.append(text(m1_x + 20, py_pos + 30, desc_txt, size=9.5, color=MUTED, anchor="start"))
        py_pos += 43

    # Стовпчик 2: Багатопотокова модель
    m2_x, m2_y, m2_w, m2_h = 435, 50, 355, 280
    p.append(rect(m2_x, m2_y, m2_w, m2_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=10))
    p.append(text(m2_x + m2_w / 2, m2_y + 24, "Багатопотокова модель (Multi-Threaded)", size=12.5, color=NEG, bold=True))
    p.append(text(m2_x + m2_w / 2, m2_y + 40, "Ігрові рушії, СУБД (MySQL), обчислювальні пули", size=10.5, color=MUTED, italic=True))

    t_pros = [
        ("Нульова ціна спільного доступу", "читання/запис за прямими покажчиками", FIELD),
        ("Швидке створення та перемикання", "пул потоків працює з мікросекундними затримками", FIELD),
        ("Мінімальний оверхед пам'яті", "лише стек (кілька КБ/МБ) без дублювання структур", FIELD),
        ("Спільна зона ураження (No blast radius)", "Segmentation fault в одному потоці вбиває процес", POS),
        ("Складність синхронізації", "перегони даних, дедлоки, потреба в замках", POS)
    ]
    ty_pos = m2_y + 54
    for title_txt, desc_txt, col in t_pros:
        p.append(rect(m2_x + 12, ty_pos, m2_w - 24, 38, fill="#ffffff", stroke="#bfdbfe", sw=1, rx=5))
        p.append(text(m2_x + 20, ty_pos + 15, title_txt, size=10.5, color=col, bold=True, anchor="start"))
        p.append(text(m2_x + 20, ty_pos + 30, desc_txt, size=9.5, color=MUTED, anchor="start"))
        ty_pos += 43

    p.append(text(W / 2, H - 12, "Вибір між процесами й потоками — це баланс між захистом від збоїв та швидкістю обміну даними", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "architectural-choice-matrix.svg"), W, H, *p,
           title="Порівняння багатопроцесної та багатопотокової архітектури")


if __name__ == "__main__":
    fig_process_vs_thread_layout()
    fig_clone_flags_spectrum()
    fig_cost_breakdown()
    fig_architectural_choice_matrix()
    print("Всі фігури згенеровано успішно.")
