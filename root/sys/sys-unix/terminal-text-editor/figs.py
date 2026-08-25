# -*- coding: utf-8 -*-
"""Фігури до теми «Редактор у терміналі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_raw_mode_termios():
    """Порівняння канонічного режиму TTY та небуферизованого сирого режиму (Raw Mode)."""
    W, H = 1080, 520
    g = []

    g.append(text(W / 2, 38, "Трансформація потоку введення: канонічний режим проти Raw Mode",
                  size=16, bold=True))

    # Ліва колонка — Канонічний режим
    bx1, bw = 50, 460
    bh = 72
    y_starts = [75, 175, 275, 375]

    g.append(fitbox(bx1, y_starts[0], bw, 52, "Канонічний режим (за замовчуванням у TTY)",
                    size=14, bold=True, fill="#fdecea", stroke=POS))

    canon_steps = [
        ("1. Клавіатура: ввід користувача", "Символи, керуючі комбінації (^C, ^Z, ^S, Backspace)"),
        ("2. Лінійна дисципліна ядра (ICANON + ECHO + ISIG)", "Буферизує до '\\n', ехо на екран, генерація SIGINT / SIGTSTP"),
        ("3. Системний виклик read(stdin)", "Процес спить до натискання Enter, отримує готовий рядок"),
    ]

    for k, (title_s, desc_s) in enumerate(canon_steps):
        y = y_starts[k + 1]
        g.append(rect(bx1, y, bw, bh, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
        g.append(text(bx1 + 16, y + 26, title_s, size=13, bold=True, color=POS, anchor="start"))
        g.append(text(bx1 + 16, y + 50, desc_s, size=11.5, color=INK, anchor="start"))
        if k < 2:
            g.append(arrow(bx1 + bw / 2, y + bh, bx1 + bw / 2, y + bh + 24, color=POS, sw=1.5))

    # Права колонка — Сирий режим
    bx2 = 570
    g.append(fitbox(bx2, y_starts[0], bw, 52, "Сирий режим редактора (Raw Mode через termios)",
                    size=14, bold=True, fill="#eaf7ee", stroke=FIELD))

    raw_steps = [
        ("1. Клавіатура: кожен окремий байт", "Будь-які натискання, Escape-послідовності, стрілки"),
        ("2. termios: вимкнено ECHO, ICANON, ISIG, IXON, ICRNL", "Жодного ехо, сигналів чи перетворень; таймаут VMIN=0, VTIME=1"),
        ("3. Негайне читання в Event Loop", "read() повертає сирі байти за <= 100 мс, повний контроль програми"),
    ]

    for k, (title_s, desc_s) in enumerate(raw_steps):
        y = y_starts[k + 1]
        g.append(rect(bx2, y, bw, bh, fill="#f4faf5", stroke=FIELD, sw=1.2, rx=6))
        g.append(text(bx2 + 16, y + 26, title_s, size=13, bold=True, color=FIELD, anchor="start"))
        g.append(text(bx2 + 16, y + 50, desc_s, size=11.5, color=INK, anchor="start"))
        if k < 2:
            g.append(arrow(bx2 + bw / 2, y + bh, bx2 + bw / 2, y + bh + 24, color=FIELD, sw=1.5))

    g.append(fitbox(50, 468, 980, 40,
                    "Прапорці termios передають повну владу над байтами та відображенням процесу редактора",
                    size=12.5, fill="#eef2f7", stroke=MUTED, sw=1, color=INK))

    return render(os.path.join(IMG, 'raw-mode-termios.svg'), W, H, *g,
                  title="Порівняння канонічного та сирого режимів TTY")


def fig_editor_event_loop():
    """Архітектура циклу обробки подій (Event Loop) та парсера Escape-послідовностей."""
    W, H = 1080, 560
    g = []

    g.append(text(W / 2, 38, "Цикл подій редактора: від байтів у stdin до оновлення буфера й екрана",
                  size=16, bold=True))

    # Схема блоків циклу подій
    blocks = [
        (60, 80, 280, 95, "1. Зчитування stdin", "read(STDIN_FILENO, &c, 1)\nТаймаут або очікування події\nОбробка помилок та EINTR", "#eaf2f8", NEG),
        (400, 80, 300, 95, "2. Декодер клавіш", "Скінченний автомат:\nASCII -> дія, \\x1b -> перевірка CSI\nРозпізнавання стрілок, PgUp, Del", "#fef9e7", "#d4ac0d"),
        (760, 80, 260, 95, "3. Диспетчер команд", "Вставка символу в текст\nРух курсора, прокрутка\nЗбереження, пошук, вихід", "#eaf7ee", FIELD),
        (760, 255, 260, 95, "4. Модифікація тексту", "Оновлення структури даних:\nGap Buffer / Piece Table\nПерерахунок рядків і довжин", "#f4f6f8", LINE),
        (400, 255, 300, 95, "5. Розрахунок Viewport", "Відображення зміщення тексту\nОбчислення row_offset, col_offset\nПідготовка видимих рядків", "#f4f6f8", LINE),
        (60, 255, 280, 95, "6. Double-Buffered Render", "Формування кадру в abuf (пам'ять)\nКурсор, очищення рядків \\x1b[K\nЄдиний системний write(stdout)", "#fdecea", POS),
    ]

    for bx, by, bw, bh, head_s, desc_s, fill_c, strk_c in blocks:
        g.append(rect(bx, by, bw, bh, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        g.append(text(bx + bw / 2, by + 24, head_s, size=13.5, bold=True, color=strk_c if strk_c != LINE else INK))
        lines = desc_s.split("\n")
        for idx, ln in enumerate(lines):
            g.append(text(bx + bw / 2, by + 46 + idx * 17, ln, size=11.5, color=INK))

    # Стрілки по колу
    g.append(arrow(340, 127, 395, 127, color=LINE, sw=1.8))
    g.append(arrow(700, 127, 755, 127, color=LINE, sw=1.8))
    g.append(arrow(890, 175, 890, 250, color=LINE, sw=1.8))
    g.append(arrow(760, 302, 705, 302, color=LINE, sw=1.8))
    g.append(arrow(400, 302, 345, 302, color=LINE, sw=1.8))

    # Замикання циклу назад до read
    g.append(line(200, 350, 200, 420, color=LINE, sw=1.8))
    g.append(line(200, 420, 40, 420, color=LINE, sw=1.8))
    g.append(line(40, 420, 40, 127, color=LINE, sw=1.8))
    g.append(arrow(40, 127, 55, 127, color=LINE, sw=1.8))
    g.append(text(120, 435, "Очікування наступного введення", size=11.5, color=MUTED))

    # Сигнал SIGWINCH окремим блоком
    g.append(rect(400, 390, 620, 75, fill="#fdf2e9", stroke="#e67e22", sw=1.5, rx=6))
    g.append(text(710, 414, "Асинхронна подія: Сигнал SIGWINCH (зміна розміру вікна)", size=13, bold=True, color="#d35400"))
    g.append(text(710, 436, "Обробник виставляє resize_pending = 1 -> ioctl(TIOCGWINSZ) -> перерахунок Viewport", size=11.5, color=INK))
    g.append(arrow(550, 390, 550, 355, color="#e67e22", sw=1.5))

    g.append(fitbox(50, 495, 980, 42,
                    "Event Loop повністю розділяє обробку вводу, мутацію моделі тексту та пакетне малювання екрана",
                    size=12.5, fill="#eef2f7", stroke=MUTED, sw=1, color=INK))

    return render(os.path.join(IMG, 'editor-event-loop.svg'), W, H, *g,
                  title="Архітектура циклу обробки подій текстового редактора")


def fig_text_buffer_structures():
    """Порівняння структур даних: масив рядків, Gap Buffer, Piece Table, Rope."""
    W, H = 1080, 580
    g = []

    g.append(text(W / 2, 36, "Структури даних текстових буферів у пам'яті",
                  size=16, bold=True))

    cards = [
        (50, 70, 470, 215, "1. Буфер з проміжком (Gap Buffer)", "Вставка в курсор: O(1) · Рух курсора: O(N) · Пам'ять: низька (Emacs)", "gap"),
        (560, 70, 470, 215, "2. Таблиця фрагментів (Piece Table)", "Вставка/Видалення: O(log P) · Нескінченний Undo/Redo · (VS Code, vi)", "piece"),
        (50, 310, 470, 215, "3. Масив рядків (Array of Lines)", "Доступ до рядка: O(1) · Вставка рядка: O(N) · (Kilo, Micro, Nano)", "lines"),
        (560, 310, 470, 215, "4. Мотузка (Rope / B-Tree)", "Вставка/Розщеплення: O(log N) · Ідеально для гігабайтних файлів (Kakoune)", "rope"),
    ]

    for bx, by, bw, bh, title_s, subtitle_s, vtype in cards:
        g.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
        g.append(text(bx + 18, by + 26, title_s, size=13.5, bold=True, color=INK, anchor="start"))
        g.append(text(bx + 18, by + 46, subtitle_s, size=11, color=MUTED, anchor="start"))

        # Малювання візуальної структури
        vy = by + 65
        if vtype == "gap":
            cells = [("H", "#eaf7ee"), ("e", "#eaf7ee"), ("l", "#eaf7ee"), ("l", "#eaf7ee"), ("o", "#eaf7ee"),
                     ("·", "#fff2f2"), ("·", "#fff2f2"), ("·", "#fff2f2"),
                     ("w", "#eaf7ee"), ("o", "#eaf7ee"), ("r", "#eaf7ee"), ("l", "#eaf7ee"), ("d", "#eaf7ee")]
            cw = 32
            start_x = bx + 24
            for i, (ch, bg_c) in enumerate(cells):
                cx_i = start_x + i * cw
                is_gap = (5 <= i <= 7)
                g.append(rect(cx_i, vy + 20, cw, 34, fill=bg_c, stroke=POS if is_gap else FIELD, sw=1.2, rx=2))
                g.append(text(cx_i + cw / 2, vy + 42, ch, size=13, bold=True, color=POS if is_gap else INK))

            g.append(text(start_x + 2.5 * cw, vy + 75, "Текст до курсора", size=11, color=FIELD))
            g.append(text(start_x + 6.5 * cw, vy + 75, "Вільний Gap", size=11, bold=True, color=POS))
            g.append(text(start_x + 10.5 * cw, vy + 75, "Текст після", size=11, color=FIELD))
            g.append(arrow(start_x + 5 * cw, vy + 12, start_x + 5 * cw, vy + 18, color=POS, sw=1.8))
            g.append(text(start_x + 5 * cw, vy + 8, "Курсор", size=10.5, color=POS))

        elif vtype == "piece":
            g.append(rect(bx + 20, vy + 10, 180, 26, fill="#eef2f7", stroke=MUTED, sw=1, rx=3))
            g.append(text(bx + 110, vy + 27, "Original: \"Hello world\"", size=11, color=INK))

            g.append(rect(bx + 240, vy + 10, 190, 26, fill="#fef9e7", stroke=MUTED, sw=1, rx=3))
            g.append(text(bx + 335, vy + 27, "Append: \", brave new \"", size=11, color=INK))

            pieces = [
                ("Piece 1: [Orig, 0, 6]", "\"Hello \""),
                ("Piece 2: [App, 0, 12]", "\", brave new \""),
                ("Piece 3: [Orig, 6, 5]", "\"world\""),
            ]
            for pi, (p_desc, p_val) in enumerate(pieces):
                py = vy + 48 + pi * 26
                g.append(rect(bx + 20, py, 220, 22, fill="#eaf7ee", stroke=FIELD, sw=1, rx=2))
                g.append(text(bx + 130, py + 15, p_desc, size=10.5, bold=True, color=FIELD))
                g.append(text(bx + 255, py + 15, "-> " + p_val, size=11, color=INK, anchor="start"))

        elif vtype == "lines":
            line_samples = [
                "0: struct termios orig_termios;",
                "1: void enable_raw_mode() {",
                "2:     tcgetattr(STDIN_FILENO, &orig);",
                "3: }",
            ]
            for li, lstr in enumerate(line_samples):
                ly = vy + 12 + li * 28
                g.append(rect(bx + 20, ly, 430, 24, fill="#f8f9fa", stroke=MUTED, sw=1, rx=2))
                g.append(text(bx + 30, ly + 16, lstr, size=11, color=INK, anchor="start"))

        elif vtype == "rope":
            g.append(circle(bx + 235, vy + 15, 14, fill="#eaf2f8", stroke=NEG, sw=1.2))
            g.append(text(bx + 235, vy + 19, "11", size=10.5, bold=True, color=NEG))

            g.append(circle(bx + 140, vy + 55, 13, fill="#eaf2f8", stroke=NEG, sw=1.2))
            g.append(text(bx + 140, vy + 59, "5", size=10, bold=True, color=NEG))

            g.append(circle(bx + 330, vy + 55, 13, fill="#eaf2f8", stroke=NEG, sw=1.2))
            g.append(text(bx + 330, vy + 59, "6", size=10, bold=True, color=NEG))

            g.append(line(bx + 225, vy + 24, bx + 150, vy + 47, color=MUTED, sw=1.2))
            g.append(line(bx + 245, vy + 24, bx + 320, vy + 47, color=MUTED, sw=1.2))

            g.append(rect(bx + 80, vy + 85, 120, 24, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=3))
            g.append(text(bx + 140, vy + 101, "\"Hello \" (len 6)", size=10.5, bold=True, color=FIELD))

            g.append(rect(bx + 270, vy + 85, 120, 24, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=3))
            g.append(text(bx + 330, vy + 101, "\"world\" (len 5)", size=10.5, bold=True, color=FIELD))

            g.append(line(bx + 140, vy + 68, bx + 140, vy + 85, color=MUTED, sw=1.2))
            g.append(line(bx + 330, vy + 68, bx + 330, vy + 85, color=MUTED, sw=1.2))

    g.append(fitbox(50, 532, 980, 36,
                    "Вибір структури тексту визначає швидкість вставки та масштабованість редактора на великих файлах",
                    size=12, fill="#eef2f7", stroke=MUTED, sw=1, color=INK))

    return render(os.path.join(IMG, 'text-buffer-structures.svg'), W, H, *g,
                  title="Порівняння структур даних текстових буферів")


def fig_screen_render_viewport():
    """Відображення віртуального текстового буфера на фізичне вікно термінала (Viewport)."""
    W, H = 1080, 540
    g = []

    g.append(text(W / 2, 36, "Проєкція буфера тексту на фізичний екран через Viewport і зсуви",
                  size=16, bold=True))

    # Лівий блок — Весь віртуальний документ
    bx1, by1, bw1, bh1 = 50, 75, 420, 400
    g.append(rect(bx1, by1, bw1, bh1, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=6))
    g.append(text(bx1 + bw1 / 2, by1 + 25, "Віртуальний буфер тексту (10 000 рядків)", size=13.5, bold=True, color=INK))

    lines_total = [
        "0: #include <stdio.h>",
        "1: #include <termios.h>",
        "2: // ... 120 рядків коду вище ...",
        "123: void editor_refresh_screen() {",
        "124:     struct abuf ab = ABUF_INIT;",
        "125:     abuf_append(&ab, \"\\x1b[?25l\", 6);",
        "126:     abuf_append(&ab, \"\\x1b[H\", 3);",
        "127:     editor_draw_rows(&ab);",
        "128:     abuf_append(&ab, \"\\x1b[?25h\", 6);",
        "129:     write(STDOUT_FILENO, ab.b, ab.len);",
        "130: }",
        "131: // ... ще 9000 рядків далі ...",
    ]

    for li, ltext in enumerate(lines_total):
        ly = by1 + 55 + li * 27
        is_visible = (3 <= li <= 10)
        bg = "#eaf7ee" if is_visible else "none"
        if is_visible:
            g.append(rect(bx1 + 10, ly - 4, bw1 - 20, 24, fill=bg, stroke=FIELD if li == 3 or li == 10 else "none", sw=1, rx=2))
        g.append(text(bx1 + 20, ly + 12, ltext, size=11, color=FIELD if is_visible else MUTED, anchor="start", bold=is_visible))

    # Рамка Viewport на лівому блоці
    g.append(rect(bx1 + 8, by1 + 132, bw1 - 16, 222, fill="none", stroke=FIELD, sw=2, rx=4))
    g.append(text(bx1 + bw1 - 20, by1 + 148, "row_offset = 123", size=11, bold=True, color=FIELD, anchor="end"))

    # Стрілка переносу у фізичний термінал
    g.append(arrow(485, 250, 565, 250, color=FIELD, sw=2.5))
    g.append(text(525, 235, "Рендеринг", size=12, bold=True, color=FIELD))
    g.append(text(525, 270, "abuf -> write()", size=10.5, color=MUTED))

    # Правий блок — Фізичний термінал
    bx2, by2, bw2, bh2 = 580, 75, 450, 400
    g.append(rect(bx2, by2, bw2, bh2, fill="#1a1a1a", stroke=LINE, sw=2, rx=6))
    g.append(text(bx2 + bw2 / 2, by2 + 25, "Фізичний екран термінала (80 × 24)", size=13.5, bold=True, color="#ffffff"))

    term_rows = [
        ("void editor_refresh_screen() {", False),
        ("    struct abuf ab = ABUF_INIT;", False),
        ("    abuf_append(&ab, \"\\x1b[?25l\", 6);", False),
        ("    abuf_append(&ab, \"\\x1b[H\", 3);", False),
        ("    editor_draw_rows(&ab);", True),
        ("    abuf_append(&ab, \"\\x1b[?25h\", 6);", False),
        ("    write(STDOUT_FILENO, ab.b, ab.len);", False),
        ("}", False),
        ("~", False),
        ("~", False),
    ]

    for ti, (ttext, has_cursor) in enumerate(term_rows):
        ty = by2 + 55 + ti * 26
        g.append(text(bx2 + 20, ty + 12, ttext, size=11.5, color="#00ff66" if ttext.startswith("~") else "#ffffff", anchor="start"))
        if has_cursor:
            cx_pos = bx2 + 20 + text_width("    editor_draw_rows(&ab);", size=11.5)
            g.append(rect(cx_pos, ty - 2, 8, 18, fill="#ffffff", stroke="none"))

    # Статусний рядок внизу термінала
    g.append(rect(bx2, by2 + bh2 - 40, bw2, 22, fill="#ffffff", stroke="none"))
    g.append(text(bx2 + 10, by2 + bh2 - 25, "main.c - 10000 lines [Modified]", size=11, bold=True, color="#1a1a1a", anchor="start"))
    g.append(text(bx2 + bw2 - 10, by2 + bh2 - 25, "127/10000", size=11, bold=True, color="#1a1a1a", anchor="end"))

    # Командний рядок
    g.append(text(bx2 + 10, by2 + bh2 - 6, "HELP: Ctrl-S = save | Ctrl-Q = quit | Ctrl-F = find", size=10.5, color="#aaaaaa", anchor="start"))

    g.append(fitbox(50, 490, 980, 38,
                    "Viewport транслює віртуальні координати буфера у фізичні координати екрана за O(екран) часу",
                    size=12, fill="#eef2f7", stroke=MUTED, sw=1, color=INK))

    return render(os.path.join(IMG, 'screen-render-viewport.svg'), W, H, *g,
                  title="Відображення буфера на фізичний екран через Viewport")


if __name__ == '__main__':
    fig_raw_mode_termios()
    fig_editor_event_loop()
    fig_text_buffer_structures()
    fig_screen_render_viewport()
