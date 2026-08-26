# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# Палітра
C_UNSAFE = "#c0392b"    # Червоний (Небезпека)
C_AFFIN  = "#e08a1e"    # Помаранчевий (Прив'язка)
C_COND   = "#d4ac0d"    # Жовто-золотий (Умовна безпека)
C_SAFE   = "#2457d6"    # Синій (Потокобезпечність)
C_REENT  = "#27ae60"    # Зелений (Реентрабельність)
C_BOX_BG = "#f8fafc"
C_BORDER = "#94a3b8"

# ── Фігура 1: Рівні потокової безпеки ─────────────────────────────────────────
def fig_thread_safety_levels():
    W, H = 820, 480
    frags = []

    # Заголовок зверху
    frags.append(text(W / 2, 28, "Спектр і рівні потокової безпеки коду", size=16, bold=True))

    levels = [
        ("1. Потоконебезпечний (Thread-Unsafe)",
         "Спільний мутабельний стан без синхронізації. Одночасний виклик кількома потоками призводить до перегонів даних, пошкодження пам'яті та аварійного завершення.",
         "Приклади: strtok(), asctime(), несинхронізовані глобальні лічильники.",
         C_UNSAFE, "#fdf2f2"),
        ("2. Прив'язаний до потоку (Thread-Affinity)",
         "Код або об'єкт може безпечно викликатися виключно з одного конкретного потоку (наприклад, головного потоку GUI або циклу подій). Доступ з інших потоків заборонено.",
         "Приклади: віджети Qt/GTK, OpenGL-контексти, однопотокові апартаменти COM.",
         C_AFFIN, "#fef8f0"),
        ("3. Умовно безпечний (Conditionally Thread-Safe)",
         "Різні потоки можуть одночасно працювати з різними екземплярами об'єкта. Одночасний доступ кількох потоків до одного екземпляра вимагає зовнішнього замка.",
         "Приклади: std::vector, std::string, більшість класів стандартних бібліотек.",
         C_COND, "#fefdf0"),
        ("4. Потокобезпечний (Thread-Safe)",
         "Внутрішній стан повністю синхронізовано (замками або атоміками). Довільна кількість потоків може одночасно викликати будь-які операції без зовнішніх блокувань.",
         "Приклади: concurrent_queue, std::atomic, потокобезпечні пули з'єднань.",
         C_SAFE, "#edf2fc"),
        ("5. Реентрабельний (Reentrant)",
         "Функція не використовує глобальний чи статичний стан; працює лише з локальним стеком та аргументами. Безпечна для повторного входу з обробників сигналів.",
         "Приклади: strtok_r(), memcpy(), математичні функції без побічних ефектів.",
         C_REENT, "#edfbf2")
    ]

    y_start = 55
    box_h = 75
    gap = 8

    for i, (title_text, desc_text, ex_text, color_accent, bg_fill) in enumerate(levels):
        y = y_start + i * (box_h + gap)

        # Рамка рівня
        frags.append(rect(30, y, W - 60, box_h, fill=bg_fill, stroke=color_accent, sw=1.5, rx=6))

        # Лівий колірний маркер
        frags.append(rect(30, y, 8, box_h, fill=color_accent, stroke=color_accent, sw=1, rx=2))

        # Заголовок рівня
        frags.append(text(50, y + 20, title_text, size=13, color=color_accent, bold=True, anchor="start"))

        # Опис рівня
        frags.append(text(50, y + 42, desc_text, size=11, color=INK, anchor="start"))

        # Приклади
        frags.append(text(50, y + 62, ex_text, size=10.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(OUT, 'thread-safety-levels.svg'), W, H, *frags)


# ── Фігура 2: Реентрабельність проти Потокобезпечності ─────────────────────────
def fig_reentrancy_vs_thread_safety():
    W, H = 820, 480
    frags = []

    frags.append(text(W / 2, 28, "Матриця відмінностей: реентрабельність та потокобезпечність", size=16, bold=True))

    col_w = 360
    row_h = 185
    x_left = 40
    x_right = x_left + col_w + 20
    y_top = 65
    y_bot = y_top + row_h + 15

    # Квадрант 1: [Не реентрабельний, Не потокобезпечний] (Top-Left)
    frags.append(rect(x_left, y_top, col_w, row_h, fill="#fdf2f2", stroke=C_UNSAFE, sw=1.5, rx=6))
    frags.append(text(x_left + col_w/2, y_top + 24, "НЕ реентрабельний / НЕ потокобезпечний", size=13, color=C_UNSAFE, bold=True))
    frags.append(text(x_left + 16, y_top + 54, "• Використовує глобальний статичний буфер", size=11, color=INK, anchor="start"))
    frags.append(text(x_left + 16, y_top + 76, "• Переривання сигналом руйнує проміжний стан", size=11, color=INK, anchor="start"))
    frags.append(text(x_left + 16, y_top + 98, "• Одночасний виклик потоками призводить до гонки", size=11, color=INK, anchor="start"))
    frags.append(text(x_left + 16, y_top + 130, "Приклади: strtok(), asctime(), rand()", size=10.5, color=MUTED, italic=True, anchor="start"))
    frags.append(text(x_left + 16, y_top + 154, "Статус: заборонено в багатопотокових системах", size=10.5, color=C_UNSAFE, bold=True, anchor="start"))

    # Квадрант 2: [Потокобезпечний, але НЕ реентрабельний] (Top-Right)
    frags.append(rect(x_right, y_top, col_w, row_h, fill="#edf2fc", stroke=C_SAFE, sw=1.5, rx=6))
    frags.append(text(x_right + col_w/2, y_top + 24, "Потокобезпечний, але НЕ реентрабельний", size=13, color=C_SAFE, bold=True))
    frags.append(text(x_right + 16, y_top + 54, "• Захищає спільний стан внутрішнім м'ютексом", size=11, color=INK, anchor="start"))
    frags.append(text(x_right + 16, y_top + 76, "• Безпечний для паралельних потоків ОС", size=11, color=INK, anchor="start"))
    frags.append(text(x_right + 16, y_top + 98, "• Переривання сигналом викликає дедлок", size=11, color=POS, anchor="start"))
    frags.append(text(x_right + 16, y_top + 130, "Приклади: malloc(), syslog(), функції з std::mutex", size=10.5, color=MUTED, italic=True, anchor="start"))
    frags.append(text(x_right + 16, y_top + 154, "Статус: НЕ безпечний для обробників сигналів", size=10.5, color=C_AFFIN, bold=True, anchor="start"))

    # Квадрант 3: [Реентрабельний, але УМОВНО потокобезпечний] (Bottom-Left)
    frags.append(rect(x_left, y_bot, col_w, row_h, fill="#fefdf0", stroke=C_COND, sw=1.5, rx=6))
    frags.append(text(x_left + col_w/2, y_bot + 24, "Реентрабельний, УМОВНО потокобезпечний", size=13, color=C_COND, bold=True))
    frags.append(text(x_left + 16, y_bot + 54, "• Не має глобального стану, працює з аргументами", size=11, color=INK, anchor="start"))
    frags.append(text(x_left + 16, y_bot + 76, "• Безпечний для виклику з обробника сигналу", size=11, color=INK, anchor="start"))
    frags.append(text(x_left + 16, y_bot + 98, "• Якщо 2 потоки передадуть один вказівник — гонка", size=11, color=POS, anchor="start"))
    frags.append(text(x_left + 16, y_bot + 130, "Приклади: strtok_r() зі спільним saveptr, swap(a, b)", size=10.5, color=MUTED, italic=True, anchor="start"))
    frags.append(text(x_left + 16, y_bot + 154, "Статус: вимагає ізольованих аргументів на стеку", size=10.5, color=C_COND, bold=True, anchor="start"))

    # Квадрант 4: [Реентрабельний І Потокобезпечний] (Bottom-Right)
    frags.append(rect(x_right, y_bot, col_w, row_h, fill="#edfbf2", stroke=C_REENT, sw=1.5, rx=6))
    frags.append(text(x_right + col_w/2, y_bot + 24, "Реентрабельний І Потокобезпечний", size=13, color=C_REENT, bold=True))
    frags.append(text(x_right + 16, y_bot + 54, "• Чиста функція без побічних ефектів або const", size=11, color=INK, anchor="start"))
    frags.append(text(x_right + 16, y_bot + 76, "• Безпечний паралельний виклик будь-якими потоками", size=11, color=INK, anchor="start"))
    frags.append(text(x_right + 16, y_bot + 98, "• Безпечний виклик у перериваннях і сигналах", size=11, color=INK, anchor="start"))
    frags.append(text(x_right + 16, y_bot + 130, "Приклади: sin(), strlen(), strtok_r() з локальним стеком", size=10.5, color=MUTED, italic=True, anchor="start"))
    frags.append(text(x_right + 16, y_bot + 154, "Статус: найвищий ступінь надійності в системі", size=10.5, color=C_REENT, bold=True, anchor="start"))

    render(os.path.join(OUT, 'reentrancy-vs-thread-safety.svg'), W, H, *frags)


# ── Фігура 3: Механізм гонки у strtok проти ізоляції в strtok_r ──────────────
def fig_strtok_race_vs_reentrant():
    W, H = 820, 440
    frags = []

    frags.append(text(W / 2, 28, "Анатомія гонки: внутрішній статичний буфер strtok проти стека strtok_r", size=16, bold=True))

    half_w = 370
    x1 = 30
    x2 = 420
    y_top = 55
    panel_h = 360

    # Ліва панель: strtok (Небезпека)
    frags.append(rect(x1, y_top, half_w, panel_h, fill="#fdf2f2", stroke=C_UNSAFE, sw=1.5, rx=6))
    frags.append(text(x1 + half_w/2, y_top + 24, "strtok() — Статичний спільний стан", size=13, color=C_UNSAFE, bold=True))

    # Спільна пам'ять (static char* last)
    frags.append(rect(x1 + 45, y_top + 48, 280, 50, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(x1 + half_w/2, y_top + 68, "static char* last_ptr (Глобальна пам'ять)", size=11, color=POS, bold=True))
    frags.append(text(x1 + half_w/2, y_top + 86, "Єдиний спільний вказівник на всю програму", size=10, color=INK))

    # Потік 1
    frags.append(rect(x1 + 20, y_top + 130, 155, 120, fill="#ffffff", stroke=C_SAFE, sw=1.2, rx=4))
    frags.append(text(x1 + 97, y_top + 148, "Потік 1: розбір URI", size=11, color=C_SAFE, bold=True))
    frags.append(text(x1 + 97, y_top + 170, "Рядок: \"a/b/c\"", size=10, color=INK))
    frags.append(text(x1 + 97, y_top + 195, "strtok(\"a/b/c\", \"/\")", size=9.5, color=MUTED))
    frags.append(text(x1 + 97, y_top + 215, "last_ptr = &\"b/c\"", size=9.5, color=POS, bold=True))

    # Потік 2
    frags.append(rect(x1 + 195, y_top + 130, 155, 120, fill="#ffffff", stroke=C_UNSAFE, sw=1.2, rx=4))
    frags.append(text(x1 + 272, y_top + 148, "Потік 2: розбір CSV", size=11, color=C_UNSAFE, bold=True))
    frags.append(text(x1 + 272, y_top + 170, "Рядок: \"1,2,3\"", size=10, color=INK))
    frags.append(text(x1 + 272, y_top + 195, "strtok(\"1,2,3\", \",\")", size=9.5, color=MUTED))
    frags.append(text(x1 + 272, y_top + 215, "last_ptr = &\"2,3\"", size=9.5, color=POS, bold=True))

    # Стрілки конфлікту
    frags.append(arrow(x1 + 97, y_top + 130, x1 + 120, y_top + 98, color=C_SAFE, sw=1.5))
    frags.append(arrow(x1 + 272, y_top + 130, x1 + 250, y_top + 98, color=C_UNSAFE, sw=1.5))

    # Результат аварії
    frags.append(rect(x1 + 20, y_top + 270, 330, 70, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(x1 + half_w/2, y_top + 292, "ПОШКОДЖЕННЯ ДАНИХ ТА АВАРІЯ", size=11.5, color=POS, bold=True))
    frags.append(text(x1 + half_w/2, y_top + 312, "Потік 2 затирає last_ptr Потоку 1.", size=10.5, color=INK))
    frags.append(text(x1 + half_w/2, y_top + 328, "Наступний strtok(NULL) прочитає чужий буфер!", size=10, color=MUTED))

    # Права панель: strtok_r (Безпека)
    frags.append(rect(x2, y_top, half_w, panel_h, fill="#edfbf2", stroke=C_REENT, sw=1.5, rx=6))
    frags.append(text(x2 + half_w/2, y_top + 24, "strtok_r() — Локальні стеки контексту", size=13, color=C_REENT, bold=True))

    # Потік 1
    frags.append(rect(x2 + 20, y_top + 60, 155, 190, fill="#ffffff", stroke=C_SAFE, sw=1.2, rx=4))
    frags.append(text(x2 + 97, y_top + 80, "Потік 1 (Стек A)", size=11, color=C_SAFE, bold=True))
    frags.append(rect(x2 + 30, y_top + 98, 135, 45, fill="#edf2fc", stroke=C_SAFE, sw=1, rx=3))
    frags.append(text(x2 + 97, y_top + 116, "char* saveptr_A", size=10.5, color=C_SAFE, bold=True))
    frags.append(text(x2 + 97, y_top + 132, "Вказівник у стеку 1", size=9.5, color=MUTED))
    frags.append(text(x2 + 97, y_top + 165, "strtok_r(s1, \"/\",", size=9.5, color=INK))
    frags.append(text(x2 + 97, y_top + 182, "&saveptr_A)", size=9.5, color=C_SAFE, bold=True))
    frags.append(text(x2 + 97, y_top + 215, "Ізольовано на 100%", size=10, color=C_REENT, bold=True))
    frags.append(text(x2 + 97, y_top + 233, "Чужі виклики не впливають", size=9, color=MUTED))

    # Потік 2
    frags.append(rect(x2 + 195, y_top + 60, 155, 190, fill="#ffffff", stroke=C_REENT, sw=1.2, rx=4))
    frags.append(text(x2 + 272, y_top + 80, "Потік 2 (Стек B)", size=11, color=C_REENT, bold=True))
    frags.append(rect(x2 + 205, y_top + 98, 135, 45, fill="#edfbf2", stroke=C_REENT, sw=1, rx=3))
    frags.append(text(x2 + 272, y_top + 116, "char* saveptr_B", size=10.5, color=C_REENT, bold=True))
    frags.append(text(x2 + 272, y_top + 132, "Вказівник у стеку 2", size=9.5, color=MUTED))
    frags.append(text(x2 + 272, y_top + 165, "strtok_r(s2, \",\",", size=9.5, color=INK))
    frags.append(text(x2 + 272, y_top + 182, "&saveptr_B)", size=9.5, color=C_REENT, bold=True))
    frags.append(text(x2 + 272, y_top + 215, "Ізольовано на 100%", size=10, color=C_REENT, bold=True))
    frags.append(text(x2 + 272, y_top + 233, "Чужі виклики не впливають", size=9, color=MUTED))

    # Результат надійності
    frags.append(rect(x2 + 20, y_top + 270, 330, 70, fill="#ffffff", stroke=C_REENT, sw=1.2, rx=4))
    frags.append(text(x2 + half_w/2, y_top + 292, "ПОВНА ПОТОКОВА БЕЗПЕКА ТА РЕЕНТРАБЕЛЬНІСТЬ", size=11, color=C_REENT, bold=True))
    frags.append(text(x2 + half_w/2, y_top + 312, "Кожен потік володіє власним станом на стеку.", size=10.5, color=INK))
    frags.append(text(x2 + half_w/2, y_top + 328, "Блокування відсутні, масштабування лінійне.", size=10, color=MUTED))

    render(os.path.join(OUT, 'strtok-race-vs-reentrant.svg'), W, H, *frags)


# ── Фігура 4: Чотири стратегії забезпечення потокової безпеки ──────────────────
def fig_thread_safety_strategies():
    W, H = 820, 440
    frags = []

    frags.append(text(W / 2, 28, "Фундаментальні стратегії забезпечення потокової безпеки", size=16, bold=True))

    col_w = 175
    gap = 18
    x_start = 30
    y_top = 60
    card_h = 350

    strategies = [
        ("1. Незмінність", "Immutability",
         "Дані лише для читання після ініціалізації.",
         ["• Нуль замків та очікувань", "• Максимальна швидкість кешів", "• Гонки неможливі фізично", "• Патерн Copy-on-Write"],
         "std::shared_ptr<const T>\nconst data structures",
         C_REENT, "#edfbf2"),

        ("2. Локалізація", "Thread-Local",
         "Власний екземпляр даних для кожного потоку.",
         ["• Ізоляція адресних просторів", "• Нуль між'ядерного трафіку", "• Відсутність дедлоків", "• Патерни TLS / Per-Core"],
         "thread_local T instance;\npthread_key_create()",
         C_SAFE, "#edf2fc"),

        ("3. Синхронізація", "Mutual Exclusion",
         "Блокування доступу до спільного стану.",
         ["• М'ютекси, RW-замки, семафори", "• Послідовний порядок доступу", "• Накладні витрати на черги", "• Ризик виникнення дедлоку"],
         "std::mutex / lock_guard\npthread_mutex_lock()",
         C_AFFIN, "#fef8f0"),

        ("4. Lock-Free", "Atomic Operations",
         "Неблокувальні апаратні інструкції процесора.",
         ["• Інструкції CAS (CMPXCHG)", "• Гарантія системного прогресу", "• Безпека в обробниках подій", "• Складність проектування"],
         "std::atomic<T>\nCAS / fetch_add()",
         C_UNSAFE, "#fdf2f2")
    ]

    for i, (title_uk, title_en, desc, points, code_sample, color_accent, bg_fill) in enumerate(strategies):
        x = x_start + i * (col_w + gap)

        # Картка стратегії
        frags.append(rect(x, y_top, col_w, card_h, fill=bg_fill, stroke=color_accent, sw=1.5, rx=6))

        # Заголовок
        frags.append(text(x + col_w/2, y_top + 24, title_uk, size=13, color=color_accent, bold=True))
        frags.append(text(x + col_w/2, y_top + 42, f"({title_en})", size=10.5, color=MUTED, italic=True))

        # Короткий опис
        frags.append(fitbox(x + 8, y_top + 54, col_w - 16, 42, desc, size=10.5, fill=bg_fill, stroke="none", color=INK))

        # Булети
        for j, pt in enumerate(points):
            frags.append(text(x + 10, y_top + 115 + j * 24, pt, size=10, color=INK, anchor="start"))

        # Приклад коду внизу картки
        frags.append(rect(x + 8, y_top + 235, col_w - 16, 95, fill="#ffffff", stroke=color_accent, sw=1, rx=4))
        frags.append(text(x + col_w/2, y_top + 252, "Примітиви:", size=10, color=color_accent, bold=True))
        code_lines = code_sample.split("\n")
        for k, cln in enumerate(code_lines):
            frags.append(text(x + col_w/2, y_top + 274 + k * 18, cln, size=9.5, color=INK))

    render(os.path.join(OUT, 'thread-safety-strategies.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_thread_safety_levels()
    fig_reentrancy_vs_thread_safety()
    fig_strtok_race_vs_reentrant()
    fig_thread_safety_strategies()
    print("All figures rendered successfully.")
