# -*- coding: utf-8 -*-
"""Фігури для теми «Ланцюжок з нуля: від питання до конвеєра» (root/course/unix/pipeline-from-scratch)."""
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
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


def fig_pipeline_mental_model():
    """pipeline-mental-model.svg: Чотириетапна модель потокової обробки даних у конвеєрі."""
    W, H = 980, 480
    frags = []

    # Заголовок
    frags.append(text(490, 32, "Потокова декомпозиція: 4 етапи трансформації даних у конвеєрі", size=16, bold=True, color="#1e293b"))

    # Джерело даних (ліворуч)
    frags.append(rect(25, 70, 160, 370, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    b_src, _, _ = textbox(105, 100, "Джерело даних\n(Data Source)", size=12, bold=True, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b_src)
    
    src_lines = [
        "access.log (50 GB)",
        "journalctl -f",
        "tcpdump / pcap",
        "stdout процесу"
    ]
    for i, s in enumerate(src_lines):
        frags.append(rect(38, 150 + i * 42, 134, 32, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        frags.append(text(105, 170 + i * 42, s, size=10, color="#334155"))

    frags.append(arrow(185, 230, 215, 230, color="#2563eb", sw=2.0))

    # Етап 1: Фільтрація
    frags.append(rect(220, 70, 165, 370, fill="#f0fdf4", stroke=GREEN_S, sw=1.5, rx=8))
    b_e1, _, _ = textbox(302, 100, "Етап 1: Фільтрація\n(Викидання шуму)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_e1)

    e1_items = [
        ("grep / ripgrep", "Пошук патернів"),
        ("grep -F / -E", "Точні / RegEx"),
        ("awk '$9 >= 500'", "Числові умови"),
        ("Обсяг: -90%", "Зменшення I/O")
    ]
    for i, (cmd, desc) in enumerate(e1_items):
        frags.append(rect(232, 150 + i * 55, 141, 46, fill="#ffffff", stroke=GREEN_S, sw=1.0, rx=4))
        frags.append(text(302, 168 + i * 55, cmd, size=11, bold=True, color="#166534"))
        frags.append(text(302, 185 + i * 55, desc, size=9.5, color="#4b5563"))

    frags.append(arrow(385, 230, 415, 230, color="#16a34a", sw=2.0))

    # Етап 2: Проєкція та нормалізація
    frags.append(rect(420, 70, 165, 370, fill="#eff6ff", stroke=BLUE_S, sw=1.5, rx=8))
    b_e2, _, _ = textbox(502, 100, "Етап 2: Проєкція\n(Виділення полів)", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_e2)

    e2_items = [
        ("cut -d' ' -f1", "Фіксовані колонки"),
        ("awk '{print $1,$7}'", "Гнучкі стовпці"),
        ("sed 's/\\?.*//'", "Очищення URI"),
        ("tr 'A-Z' 'a-z'", "Уніфікація регістру")
    ]
    for i, (cmd, desc) in enumerate(e2_items):
        frags.append(rect(432, 150 + i * 55, 141, 46, fill="#ffffff", stroke=BLUE_S, sw=1.0, rx=4))
        frags.append(text(502, 168 + i * 55, cmd, size=10.5, bold=True, color="#1e40af"))
        frags.append(text(502, 185 + i * 55, desc, size=9.5, color="#4b5563"))

    frags.append(arrow(585, 230, 615, 230, color="#2563eb", sw=2.0))

    # Етап 3: Агрегація
    frags.append(rect(620, 70, 165, 370, fill="#fffbeb", stroke=AMBER_S, sw=1.5, rx=8))
    b_e3, _, _ = textbox(702, 100, "Етап 3: Агрегація\n(Згортання даних)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_e3)

    e3_items = [
        ("sort", "Лексикографічно"),
        ("uniq -c", "Частотний облік"),
        ("sort -rn", "Числове спадання"),
        ("awk 'count[$1]++'", "Асоціативний масив")
    ]
    for i, (cmd, desc) in enumerate(e3_items):
        frags.append(rect(632, 150 + i * 55, 141, 46, fill="#ffffff", stroke=AMBER_S, sw=1.0, rx=4))
        frags.append(text(702, 168 + i * 55, cmd, size=10.5, bold=True, color="#92400e"))
        frags.append(text(702, 185 + i * 55, desc, size=9.5, color="#4b5563"))

    frags.append(arrow(785, 230, 815, 230, color="#e08a1e", sw=2.0))

    # Етап 4: Форматування
    frags.append(rect(820, 70, 135, 370, fill="#faf5ff", stroke=PURPLE_S, sw=1.5, rx=8))
    b_e4, _, _ = textbox(887, 100, "Етап 4: Відбір\n(Презентація)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_e4)

    e4_items = [
        ("head -n 10", "Top-10 записів"),
        ("column -t", "Табличний звіт"),
        ("tee report.txt", "Дублювання"),
        ("SIGPIPE", "Рання зупинка")
    ]
    for i, (cmd, desc) in enumerate(e4_items):
        frags.append(rect(828, 150 + i * 55, 119, 46, fill="#ffffff", stroke=PURPLE_S, sw=1.0, rx=4))
        frags.append(text(887, 168 + i * 55, cmd, size=10.5, bold=True, color="#6b21a8"))
        frags.append(text(887, 185 + i * 55, desc, size=9.5, color="#4b5563"))

    # Підвал: єдиний текстовий потік
    frags.append(rect(25, 450, 930, 22, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(490, 465, "Потік байтів через ядро Linux (pipe 64 KB) • Без проміжних файлів на диску • Паралельне виконання", size=10, color="#475569"))

    return render(os.path.join(IMG, "pipeline-mental-model.svg"), W, H, *frags)


def fig_pipe_kernel_buffer():
    """pipe-kernel-buffer.svg: Фізика буфера каналу в ядрі Linux та механізм зворотного тиску."""
    W, H = 960, 480
    frags = []

    # Заголовок
    frags.append(text(480, 30, "Фізика каналу в ядрі: кільцевий буфер pipe_inode_info та Backpressure", size=16, bold=True, color="#1e293b"))

    # Виробник (Producer)
    frags.append(rect(30, 65, 230, 380, fill="#f0fdf4", stroke=GREEN_S, sw=1.5, rx=8))
    b_prod, _, _ = textbox(145, 95, "Виробник (Producer)\ngrep ' 500 '", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_prod)

    prod_steps = [
        "1. Генерує потік даних",
        "2. write(fd, buf, count)",
        "3. Перевіряє вільне місце",
        "4. Якщо буфер повний (64 KB):",
        "   → потік блокується",
        "   → стан TASK_INTERRUPTIBLE",
        "   → очікує в pipe->wr_wait"
    ]
    for i, s in enumerate(prod_steps):
        col = RED_S if "блокується" in s or "повний" in s else "#334155"
        bld = True if "write" in s or "блокується" in s else False
        frags.append(text(45, 145 + i * 26, s, size=10.5, bold=bld, color=col, anchor="start"))

    frags.append(rect(45, 340, 200, 85, fill="#ffffff", stroke=GREEN_S, sw=1.0, rx=6))
    frags.append(text(145, 360, "Дескриптор FD 1 (stdout)", size=10.5, bold=True, color=GREEN_S))
    frags.append(text(145, 382, "Запис у дескриптор каналу", size=9.5, color="#64748b"))
    frags.append(text(145, 404, "Атомарно при <= 4096 B (PIPE_BUF)", size=9, color="#94a3b8"))

    frags.append(arrow(260, 230, 300, 230, color=GREEN_S, sw=2.5))

    # Ядро Linux: Структура каналу
    frags.append(rect(305, 65, 350, 380, fill="#eff6ff", stroke=BLUE_S, sw=1.5, rx=8))
    b_kern, _, _ = textbox(480, 95, "Ядро Linux: struct pipe_inode_info\nКільцевий буфер (16 сторінок x 4 KB = 64 KB)", size=11.5, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_kern)

    # 16 сторінок каналу
    frags.append(text(480, 145, "Кільцевий масив сторінок пам'яті (pipe_buffer):", size=10.5, bold=True, color="#1e3a8a"))
    
    # Сітка 4x4 або 8x2 сторінок
    for row in range(2):
        for col in range(8):
            idx = row * 8 + col
            px = 325 + col * 39
            py = 165 + row * 40
            # кілька сторінок заповнено, кілька вільно
            is_filled = idx < 9
            fcol = "#dbeafe" if is_filled else "#f8fafc"
            scol = BLUE_S if is_filled else "#cbd5e1"
            txt_col = BLUE_S if is_filled else "#94a3b8"
            frags.append(rect(px, py, 34, 32, fill=fcol, stroke=scol, sw=1.0, rx=3))
            frags.append(text(px + 17, py + 20, "4K", size=9, bold=is_filled, color=txt_col))

    frags.append(text(480, 260, "head (позиція запису) ────► сторінка 9", size=10, color=GREEN_S))
    frags.append(text(480, 280, "tail (позиція читання) ────► сторінка 0", size=10, color=PURPLE_S))
    
    # Механізм черг
    frags.append(rect(320, 310, 320, 115, fill="#ffffff", stroke=BLUE_S, sw=1.0, rx=6))
    frags.append(text(480, 330, "Черги очікування синхронізації (Wait Queues):", size=10, bold=True, color="#1e40af"))
    frags.append(text(480, 355, "• wr_wait: розбудити виробника, коли звільниться місце", size=9.5, color="#334155"))
    frags.append(text(480, 375, "• rd_wait: розбудити споживача, коли з'являться дані", size=9.5, color="#334155"))
    frags.append(text(480, 400, "• fcntl(F_SETPIPE_SZ): зміна розміру від 4 KB до 1 MB+", size=9, color="#6b7280"))

    frags.append(arrow(655, 230, 695, 230, color=PURPLE_S, sw=2.5))

    # Споживач (Consumer)
    frags.append(rect(700, 65, 230, 380, fill="#faf5ff", stroke=PURPLE_S, sw=1.5, rx=8))
    b_cons, _, _ = textbox(815, 95, "Споживач (Consumer)\nawk '{print $1}'", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_cons)

    cons_steps = [
        "1. Очікує дані з пайпу",
        "2. read(fd, buf, count)",
        "3. Якщо буфер порожній:",
        "   → потік блокується",
        "   → очікує в pipe->rd_wait",
        "4. Якщо виробник закрив FD:",
        "   → read повертає 0 (EOF)",
        "   → нормальне завершення"
    ]
    for i, s in enumerate(cons_steps):
        col = AMBER_S if "блокується" in s or "порожній" in s else "#334155"
        bld = True if "read" in s or "EOF" in s else False
        frags.append(text(715, 145 + i * 26, s, size=10.5, bold=bld, color=col, anchor="start"))

    frags.append(rect(715, 360, 200, 65, fill="#ffffff", stroke=PURPLE_S, sw=1.0, rx=6))
    frags.append(text(815, 380, "Дескриптор FD 0 (stdin)", size=10.5, bold=True, color=PURPLE_S))
    frags.append(text(815, 402, "Читання з дескриптора каналу", size=9.5, color="#64748b"))

    # Підпис знизу
    frags.append(rect(30, 452, 900, 20, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    frags.append(text(480, 466, "Механізм Backpressure гарантує: швидкий процес не переповнює оперативну пам'ять системи", size=9.5, color="#475569"))

    return render(os.path.join(IMG, "pipe-kernel-buffer.svg"), W, H, *frags)


def fig_stdio_buffering_trap():
    """stdio-buffering-trap.svg: Рівні буферизації в конвеєрі: libc проти буфера ядра."""
    W, H = 960, 480
    frags = []

    # Заголовок
    frags.append(text(480, 30, "Анатомія буферизації: чому зависає конвеєр у реальному часі", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Вивід у термінал (TTY)
    frags.append(rect(30, 65, 430, 390, fill="#f0fdf4", stroke=GREEN_S, sw=1.5, rx=8))
    b_tty, _, _ = textbox(245, 95, "Сценарій А: Вивід у термінал (isatty = true)\ntail -f app.log | grep 'ERROR'", size=11.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_tty)

    frags.append(rect(50, 140, 390, 85, fill="#ffffff", stroke=GREEN_S, sw=1.0, rx=6))
    frags.append(text(245, 160, "Простір користувача: Бібліотека C (libc stdio)", size=10.5, bold=True, color=GREEN_S))
    frags.append(text(245, 185, "Режим: _IOLBF (Line Buffered / Порядкова буферизація)", size=10, bold=True, color="#166534"))
    frags.append(text(245, 205, "Буфер скидається при кожному '\\n' (символі нового рядка)", size=9.5, color="#4b5563"))

    frags.append(arrow(245, 225, 245, 255, color=GREEN_S, sw=2.0))

    frags.append(rect(50, 255, 390, 65, fill="#ffffff", stroke=GREEN_S, sw=1.0, rx=6))
    frags.append(text(245, 275, "Дисципліна ліній TTY ядра (Terminal Driver)", size=10.5, bold=True, color="#1e293b"))
    frags.append(text(245, 298, "Миттєва передача рядка в емулятор термінала", size=9.5, color="#4b5563"))

    frags.append(arrow(245, 320, 245, 350, color=GREEN_S, sw=2.0))

    frags.append(rect(50, 350, 390, 85, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=6))
    frags.append(text(245, 375, "Результат: НУЛЬОВА ЗАТРИМКА (Real-time)", size=11, bold=True, color=GREEN_S))
    frags.append(text(245, 400, "Кожен рядок логу з'являється на екрані негайно", size=10, color="#166534"))
    frags.append(text(245, 420, "Затримка = ~0 мілісекунд", size=9, color="#6b7280"))

    # Права колонка: Вивід у пайп (Non-TTY)
    frags.append(rect(500, 65, 430, 390, fill="#fef2f2", stroke=RED_S, sw=1.5, rx=8))
    b_pipe, _, _ = textbox(715, 95, "Сценарій Б: Вивід у пайп (isatty = false)\ntail -f app.log | grep 'ERR' | awk '{print $1}'", size=11.5, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_pipe)

    frags.append(rect(520, 140, 390, 85, fill="#ffffff", stroke=RED_S, sw=1.0, rx=6))
    frags.append(text(715, 160, "Простір користувача: Бібліотека C (libc stdio)", size=10.5, bold=True, color=RED_S))
    frags.append(text(715, 185, "Режим: _IOFBF (Fully Buffered / Блокова буферизація 4096 B)", size=10, bold=True, color="#991b1b"))
    frags.append(text(715, 205, "write() викликається ЛИШЕ коли накопичиться 4 KB!", size=9.5, color="#4b5563"))

    frags.append(arrow(715, 225, 715, 255, color=RED_S, sw=2.0))

    frags.append(rect(520, 255, 390, 65, fill="#ffffff", stroke=RED_S, sw=1.0, rx=6))
    frags.append(text(715, 275, "Кільцевий буфер каналу в ядрі (Pipe Buffer)", size=10.5, bold=True, color="#1e293b"))
    frags.append(text(715, 298, "Дані взагалі не потрапляють у ядро, поки заповнюється 4 KB", size=9.5, color="#4b5563"))

    frags.append(arrow(715, 320, 715, 350, color=RED_S, sw=2.0))

    frags.append(rect(520, 350, 390, 85, fill=RED_F, stroke=RED_S, sw=1.2, rx=6))
    frags.append(text(715, 375, "Результат: ІЛЮЗІЯ ЗАВИСАННЯ (Stall / Latency)", size=11, bold=True, color=RED_S))
    frags.append(text(715, 398, "Рідкісні події (1 рядок/хв) затримуються на десятки хвилин!", size=9.5, color="#991b1b"))
    frags.append(text(715, 418, "Лікування: stdbuf -oL або grep --line-buffered", size=9.5, bold=True, color=BLUE_S))

    return render(os.path.join(IMG, "stdio-buffering-trap.svg"), W, H, *frags)


def fig_pipeline_error_propagation():
    """pipeline-error-propagation.svg: Механізм розповсюдження кодів повернення у конвеєрі та масив PIPESTATUS."""
    W, H = 960, 480
    frags = []

    # Заголовок
    frags.append(text(480, 30, "Обробка помилок у конвеєрі: дефолтний $? проти pipefail та PIPESTATUS", size=16, bold=True, color="#1e293b"))

    # Приклад конвеєра з помилкою всередині
    frags.append(rect(30, 65, 900, 65, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(480, 88, "Команда: cat missing_file.log | grep '500' | awk '{print $1}' | wc -l", size=12, bold=True, color="#0f172a"))
    frags.append(text(480, 112, "cat падає (код 1: No such file), grep знаходить 0 рядків (код 1), awk успішний (код 0), wc друкує '0' (код 0)", size=10, color="#64748b"))

    # Статуси окремих процесів
    procs = [
        ("cat missing_file.log", "Код виходу: 1", "(File Not Found)", RED_F, RED_S),
        ("grep '500'", "Код виходу: 1", "(No matches)", RED_F, RED_S),
        ("awk '{print $1}'", "Код виходу: 0", "(Success)", GREEN_F, GREEN_S),
        ("wc -l", "Код виходу: 0", "(Success: друкує 0)", GREEN_F, GREEN_S)
    ]
    for i, (name, st, desc, bg, st_col) in enumerate(procs):
        px = 30 + i * 230
        frags.append(rect(px, 145, 210, 80, fill=bg, stroke=st_col, sw=1.2, rx=6))
        frags.append(text(px + 105, 168, name, size=10.5, bold=True, color="#1e293b"))
        frags.append(text(px + 105, 190, st, size=10, bold=True, color=st_col))
        frags.append(text(px + 105, 210, desc, size=9, color="#4b5563"))

    # Порівняння 3 режимів інтерпретації результату
    # 1. Замовчуваний режим POSIX
    frags.append(rect(30, 245, 285, 215, fill="#fef2f2", stroke=RED_S, sw=1.2, rx=8))
    b_m1, _, _ = textbox(172, 275, "1. Замовчування POSIX ($?)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_m1)
    
    m1_lines = [
        "Повертає статус останньої команди:",
        "$? == 0 (успіх wc -l)",
        "",
        "Смертельна небезпека:",
        "Помилки cat і grep повністю",
        "замасковані! Скрипт вважає,",
        "що обробка пройшла успішно."
    ]
    for i, l in enumerate(m1_lines):
        bld = True if "$? == 0" in l or "небезпека" in l else False
        col = RED_S if "замасковані" in l or "$? == 0" in l else "#334155"
        frags.append(text(172, 310 + i * 18, l, size=9.5, bold=bld, color=col))

    # 2. Опція set -o pipefail
    frags.append(rect(335, 245, 290, 215, fill="#fffbeb", stroke=AMBER_S, sw=1.2, rx=8))
    b_m2, _, _ = textbox(480, 275, "2. Опція set -o pipefail", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_m2)

    m2_lines = [
        "Повертає код найбільш правої",
        "команди з ненульовим статусом:",
        "$? == 1 (збій конвеєра)",
        "",
        "Захист у production:",
        "set -e негайно зупиняє сценарій,",
        "якщо будь-який етап дав збій."
    ]
    for i, l in enumerate(m2_lines):
        bld = True if "$? == 1" in l or "Захист" in l else False
        col = AMBER_S if "$? == 1" in l or "set -e" in l else "#334155"
        frags.append(text(480, 310 + i * 18, l, size=9.5, bold=bld, color=col))

    # 3. Масив PIPESTATUS
    frags.append(rect(645, 245, 285, 215, fill="#f0fdf4", stroke=GREEN_S, sw=1.2, rx=8))
    b_m3, _, _ = textbox(787, 275, "3. Масив ${PIPESTATUS[@]}", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_m3)

    m3_lines = [
        "Вектор статусів кожного етапу:",
        "PIPESTATUS=( 1  1  0  0 )",
        "",
        "Хірургічна точність:",
        "${PIPESTATUS[0]} → помилка cat",
        "${PIPESTATUS[1]} → помилка grep",
        "Дозволяє точкову діагностику."
    ]
    for i, l in enumerate(m3_lines):
        bld = True if "PIPESTATUS=(" in l or "Хірургічна" in l else False
        col = GREEN_S if "PIPESTATUS" in l else "#334155"
        frags.append(text(787, 310 + i * 18, l, size=9.5, bold=bld, color=col))

    return render(os.path.join(IMG, "pipeline-error-propagation.svg"), W, H, *frags)


if __name__ == "__main__":
    print("Генерація SVG-фігур для теми pipeline-from-scratch...")
    fig_pipeline_mental_model()
    print("  + pipeline-mental-model.svg")
    fig_pipe_kernel_buffer()
    print("  + pipe-kernel-buffer.svg")
    fig_stdio_buffering_trap()
    print("  + stdio-buffering-trap.svg")
    fig_pipeline_error_propagation()
    print("  + pipeline-error-propagation.svg")
    print("Генерацію завершено.")
