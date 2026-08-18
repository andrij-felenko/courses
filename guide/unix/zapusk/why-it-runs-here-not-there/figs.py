# -*- coding: utf-8 -*-
"""Фігури для теми «Чому запускається в тебе й не запускається в них» (guide/unix/zapusk/why-it-runs-here-not-there)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S     = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S   = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S   = "#fff6e5", "#d97706"
RED_F, RED_S       = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S     = "#f8fafc", "#64748b"

def fig_execution_gateways():
    W, H = 940, 520
    frags = []

    frags.append(rect(10, 10, 920, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(470, 36, "П'ять бар'єрів виконання: де ламається переносимість бінарника", size=16, bold=True, color="#0f172a"))

    stages = [
        ("1. Ядро (execve)", "Перевірка заголовка ELF,\nрозпізнавання PT_INTERP", "Збій архітектури (ENOEXEC)\nабо брак /lib64/ld.so (ENOENT)", BLUE_F, BLUE_S),
        ("2. Завантажувач ld.so", "Ініціалізація пам'яті,\nпошук DT_NEEDED залежностей", "cannot open shared object:\nнемає бібліотеки чи хибний шлях", PURPLE_F, PURPLE_S),
        ("3. Символи та ABI", "Перевірка .gnu.version_r\nта розв'язання GOT/PLT", "version GLIBC_2.34 not found\nабо undefined symbol", RED_F, RED_S),
        ("4. C-Runtime (libc)", "Ініціалізація C-бібліотеки,\nпотоки, пам'ять, NSS", "Розбіжність glibc проти musl,\nкрах внутрішніх структур", AMBER_F, AMBER_S),
        ("5. Оточення процесу", "Конструктори .init_array,\nлокалі, PATH, дескриптори", "Збій setlocale(LC_ALL),\nне знайдено утиліту в PATH", GREEN_F, GREEN_S),
    ]

    box_w = 160
    box_h = 240
    start_x = 35
    gap_x = 22
    y_top = 70

    for i, (title, action, failure, bg_col, stroke_col) in enumerate(stages):
        x = start_x + i * (box_w + gap_x)
        cx = x + box_w / 2

        frags.append(rect(x, y_top, box_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.8, rx=8))
        frags.append(text(cx, y_top + 26, title, size=13, bold=True, color=stroke_col))
        frags.append(line(x + 10, y_top + 38, x + box_w - 10, y_top + 38, color=stroke_col, sw=1.0))

        frags.append(text(cx, y_top + 60, "Що виконується:", size=11, bold=True, color="#334155"))
        act_lines = action.split("\n")
        for j, al in enumerate(act_lines):
            frags.append(text(cx, y_top + 80 + j * 18, al, size=11, color="#1e293b"))

        frags.append(line(x + 15, y_top + 130, x + box_w - 15, y_top + 130, color="#cbd5e1", sw=1.0, dash="3,3"))

        frags.append(text(cx, y_top + 150, "Типова помилка:", size=11, bold=True, color=RED_S))
        fail_lines = failure.split("\n")
        for j, fl in enumerate(fail_lines):
            frags.append(text(cx, y_top + 172 + j * 18, fl, size=10.5, color="#7f1d1d"))

        if i < len(stages) - 1:
            arr_x1 = x + box_w + 3
            arr_x2 = arr_x1 + gap_x - 6
            frags.append(arrow(arr_x1, y_top + box_h / 2, arr_x2, y_top + box_h / 2, color="#64748b", sw=2.0))

    frags.append(rect(35, 340, 870, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(470, 368, "Результат: виконання функції main() передається тільки після подолання всіх п'яти бар'єрів", size=13, bold=True, color="#0f172a"))

    frags.append(text(180, 400, "Вхід: execve(\"./app\", argv, envp)", size=12, bold=True, color=BLUE_S))
    frags.append(arrow(295, 396, 360, 396, color=BLUE_S, sw=1.8))

    frags.append(text(470, 400, "Конвеєр завантаження та зв'язування", size=12, bold=True, color="#475569"))
    frags.append(arrow(580, 396, 645, 396, color=GREEN_S, sw=1.8))

    frags.append(text(745, 400, "Вихід: передача керування в main()", size=12, bold=True, color=GREEN_S))

    frags.append(text(470, 435, "Якщо хоча б один бар'єр не пройдено — процес негайно аварійно завершується до виконання першого рядка коду програми.", size=11.5, italic=True, color="#475569"))
    frags.append(text(470, 458, "Діагностика: file -> readelf -l/-d/-V -> ldd / LD_TRACE_LOADED_OBJECTS -> LD_DEBUG=libs,symbols", size=11, bold=True, color="#0369a1"))

    out_path = os.path.join(IMG, "fig-execution-gateways.svg")
    render(out_path, W, H, *frags)

def fig_library_search_hierarchy():
    W, H = 940, 500
    frags = []

    frags.append(rect(10, 10, 920, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(470, 36, "Ієрархія пошуку динамічних бібліотек завантажувачем ld.so", size=16, bold=True, color="#0f172a"))

    steps = [
        ("1. DT_RPATH", "Зашитий у бінарник шлях (якщо відсутній DT_RUNPATH). Перекриває навіть LD_LIBRARY_PATH!", "#fee2e2", "#b91c1c", "Найвищий пріоритет"),
        ("2. LD_LIBRARY_PATH", "Змінна середовища зі списком каталогів через двокрапку. Ігнорується для setuid (AT_SECURE).", "#fef3c7", "#b45309", "Перевизначення користувача"),
        ("3. DT_RUNPATH", "Сучасний зашитий у бінарник шлях. Перевіряється після LD_LIBRARY_PATH, підтримує .", "#ede9fe", "#6d28d9", "Шлях поставки застосунку"),
        ("4. /etc/ld.so.cache", "Бінарний кеш системного конфігуратора ldconfig (/etc/ld.so.conf). Швидкий пошук O(1).", "#e0f2fe", "#0369a1", "Системний кеш бібліотек"),
        ("5. Типові системні шляхи", "Стандартні системні каталоги: /lib64, /usr/lib64, /lib, /usr/lib або /lib/x86_64-linux-gnu.", "#f1f5f9", "#475569", "Остання лінія пошуку"),
    ]

    y_start = 68
    row_h = 62
    gap_y = 14

    for i, (title, desc, bg_col, stroke_col, badge) in enumerate(steps):
        y = y_start + i * (row_h + gap_y)

        frags.append(rect(40, y, 860, row_h, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        frags.append(text(130, y + 26, title, size=13.5, bold=True, color=stroke_col, anchor="start"))
        frags.append(text(130, y + 48, desc, size=11, color="#1e293b", anchor="start"))

        b_box, _, _ = textbox(770, y + 31, badge, size=11, pad=6, fill="#ffffff", stroke=stroke_col, sw=1.2, color=stroke_col, bold=True)
        frags.append(b_box)

        if i < len(steps) - 1:
            frags.append(arrow(85, y + row_h, 85, y + row_h + gap_y - 1, color="#64748b", sw=1.8))

    y_fail = y_start + 5 * (row_h + gap_y) + 5
    frags.append(rect(40, y_fail, 860, 36, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(470, y_fail + 23, "Якщо бібліотеку не знайдено на жодному рівні: помилка cannot open shared object file (ENOENT) і аварійний вихід", size=11.5, bold=True, color="#991b1b"))

    out_path = os.path.join(IMG, "fig-library-search-hierarchy.svg")
    render(out_path, W, H, *frags)

if __name__ == "__main__":
    fig_execution_gateways()
    fig_library_search_hierarchy()
    print("Фігури успішно згенеровано.")