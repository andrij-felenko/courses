import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_classic_pipeline_vs_awk(path):
    frags = []

    # Outer background
    frags.append(rect(10, 10, 880, 480, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(450, 35, "Архітектурне порівняння: конвеєр процесів проти внутрішньопроцесної агрегації", size=14, color="#263238", bold=True))

    # Top Section: Multi-process Pipeline
    frags.append(rect(25, 55, 850, 205, fill="#fff8e1", stroke="#ffa000", sw=1.5, rx=6))
    frags.append(text(210, 78, "1. Багатопроцесний конвеєр: cat | grep | cut | sort | uniq -c", size=13, color="#b78103", bold=True))

    stages = [
        ("cat", "PID 101", "ЧИТАННЯ"),
        ("grep", "PID 102", "ФІЛЬТР"),
        ("cut", "PID 103", "КОЛОНКИ"),
        ("sort", "PID 104", "СОРТУВАННЯ"),
        ("uniq -c", "PID 105", "ПІДРАХУНОК"),
    ]

    for i, (name, pid, role) in enumerate(stages):
        x = 40 + i * 165
        frags.append(rect(x, 95, 115, 85, fill="#ffffff", stroke="#d7ccc8", rx=5))
        frags.append(text(x + 57, 118, name, size=13, color="#212121", bold=True))
        frags.append(text(x + 57, 138, pid, size=10, color="#546e7a"))
        frags.append(rect(x + 12, 148, 91, 22, fill="#f5f5f5", stroke="#e0e0e0", rx=3))
        frags.append(text(x + 57, 163, role, size=9, color="#616161", bold=True))

        if i < len(stages) - 1:
            arrow_x1 = x + 115
            arrow_x2 = x + 165
            frags.append(arrow(arrow_x1, 137, arrow_x2, 137, color="#d32f2f", sw=2))
            frags.append(rect(arrow_x1 + 3, 115, 44, 18, fill="#ffebee", stroke="#ef9a9a", rx=3))
            frags.append(text(arrow_x1 + 25, 128, "pipe", size=9, color="#c62828", bold=True))

    # Kernel pipe layer note
    frags.append(rect(40, 195, 820, 50, fill="#fbe9e7", stroke="#ffab91", rx=4))
    frags.append(text(450, 215, "Ядро Linux: 4 канали pipe (64KB ring-buffer) • Копіювання User ↔ Kernel пам'яті • Перемикання контексту", size=10, color="#d84315", bold=True))
    frags.append(text(450, 233, "Високі накладні витрати на fork/exec, синхронізацію дескрипторів та промахи кешу L1/L2", size=9, color="#8d6e63"))

    # Bottom Section: Single AWK process
    frags.append(rect(25, 275, 850, 195, fill="#e8f5e9", stroke="#43a047", sw=1.5, rx=6))
    frags.append(text(250, 298, "2. Оптимізований монолітний фільтр: awk '{ count[$1]++ } END { ... }'", size=13, color="#1b5e20", bold=True))

    frags.append(rect(40, 315, 230, 135, fill="#ffffff", stroke="#a5d6a7", rx=5))
    frags.append(text(155, 340, "Єдиний процес awk (PID 201)", size=12, color="#1b5e20", bold=True))
    frags.append(text(155, 362, "Прямий доступ до файлу", size=10, color="#558b2f"))
    frags.append(text(155, 385, "Блоковий ввід read(64KB)", size=10, color="#37474f"))
    frags.append(text(155, 408, "Спліт рядків без пайпів", size=10, color="#37474f"))
    frags.append(text(155, 432, "Відсутність зайвих fork/exec", size=9, color="#2e7d32", bold=True))

    frags.append(arrow(275, 382, 315, 382, color="#2e7d32", sw=2))

    frags.append(rect(320, 315, 275, 135, fill="#ffffff", stroke="#a5d6a7", rx=5))
    frags.append(text(457, 340, "Хеш-таблиця у просторі процесу", size=12, color="#1b5e20", bold=True))
    frags.append(text(457, 362, "Асоціативний масив: count[key]", size=10, color="#2e7d32", bold=True))
    frags.append(rect(335, 375, 245, 60, fill="#f1f8e9", stroke="#c5e1a5", rx=4))
    frags.append(text(457, 395, "IP-адреса -> Лічильник входжень", size=9, color="#33691e"))
    frags.append(text(457, 412, "Локальність даних у RAM", size=9, color="#33691e"))
    frags.append(text(457, 427, "O(1) оновлення стану", size=9, color="#1b5e20", bold=True))

    frags.append(arrow(600, 382, 640, 382, color="#2e7d32", sw=2))

    frags.append(rect(645, 315, 215, 135, fill="#ffffff", stroke="#a5d6a7", rx=5))
    frags.append(text(752, 340, "Фінальний вивід (stdout)", size=12, color="#1b5e20", bold=True))
    frags.append(text(752, 368, "Генерація результатів", size=10, color="#37474f"))
    frags.append(text(752, 392, "в блоці END", size=10, color="#37474f"))
    frags.append(rect(660, 408, 185, 28, fill="#e8f5e9", stroke="#81c784", rx=3))
    frags.append(text(752, 426, "Економія пам'яті й CPU", size=10, color="#1b5e20", bold=True))

    render(path, 900, 500, *frags)

def build_buffering_and_stdbuf(path):
    frags = []

    # Outer background
    frags.append(rect(10, 10, 880, 420, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(450, 35, "Режими буферизації stdio у конвеєрах та ін'єкція stdbuf", size=14, color="#263238", bold=True))

    # Column 1: TTY Line Buffering
    frags.append(rect(25, 60, 265, 340, fill="#e3f2fd", stroke="#1976d2", sw=1.5, rx=6))
    frags.append(text(157, 85, "Інтерактивний TTY", size=13, color="#0d47a1", bold=True))
    frags.append(text(157, 105, "isatty(STDOUT) == 1", size=11, color="#1565c0"))

    frags.append(rect(40, 125, 235, 95, fill="#ffffff", stroke="#90caf9", rx=4))
    frags.append(text(157, 148, "Порядковий буфер (_IOLBF)", size=11, color="#0d47a1", bold=True))
    frags.append(text(157, 170, "Скидання на кожному '\\n'", size=10, color="#1b5e20"))
    frags.append(text(157, 192, "Мінімальна затримка", size=10, color="#37474f"))
    frags.append(text(157, 210, "Миттєвий вивід людині", size=9, color="#546e7a"))

    frags.append(rect(40, 235, 235, 145, fill="#ffffff", stroke="#90caf9", rx=4))
    frags.append(text(157, 258, "Поведінка команд:", size=11, color="#263238", bold=True))
    frags.append(text(157, 282, "grep, sed, awk напряму в термінал", size=9, color="#37474f"))
    frags.append(text(157, 305, "працюють без затримок", size=9, color="#1b5e20", bold=True))
    frags.append(text(157, 335, "write(1, line, len)", size=10, color="#0d47a1", bold=True))
    frags.append(text(157, 355, "після кожного рядка", size=9, color="#546e7a"))

    # Column 2: Pipe Full Buffering (The Problem)
    frags.append(rect(305, 60, 265, 340, fill="#ffebee", stroke="#d32f2f", sw=1.5, rx=6))
    frags.append(text(437, 85, "Конвеєр / Pipe (Проблема)", size=13, color="#b71c1c", bold=True))
    frags.append(text(437, 105, "isatty(STDOUT) == 0", size=11, color="#c62828"))

    frags.append(rect(320, 125, 235, 95, fill="#ffffff", stroke="#ef9a9a", rx=4))
    frags.append(text(437, 148, "Повний буфер (_IOFBF)", size=11, color="#b71c1c", bold=True))
    frags.append(text(437, 170, "Розмір: 4096 / 65536 байтів", size=10, color="#d32f2f", bold=True))
    frags.append(text(437, 192, "Скидання лише при переповненні", size=9, color="#37474f"))
    frags.append(text(437, 210, "або при закритті процесу", size=9, color="#546e7a"))

    frags.append(rect(320, 235, 235, 145, fill="#ffffff", stroke="#ef9a9a", rx=4))
    frags.append(text(437, 258, "Ефект «зависання»:", size=11, color="#b71c1c", bold=True))
    frags.append(text(437, 282, "tail -f log | grep ... | awk ...", size=9, color="#212121"))
    frags.append(text(437, 305, "Дані застрягають у буфері grep", size=9, color="#c62828", bold=True))
    frags.append(text(437, 335, "Вивід затримується на хвилини", size=9, color="#546e7a"))
    frags.append(text(437, 355, "до накопичення 4КБ/64КБ даних", size=9, color="#d32f2f"))

    # Column 3: stdbuf Override (The Solution)
    frags.append(rect(585, 60, 275, 340, fill="#e8f5e9", stroke="#388e3c", sw=1.5, rx=6))
    frags.append(text(722, 85, "Рішення: stdbuf -oL", size=13, color="#1b5e20", bold=True))
    frags.append(text(722, 105, "LD_PRELOAD=libstdbuf.so", size=11, color="#2e7d32"))

    frags.append(rect(600, 125, 245, 95, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(722, 148, "Конструктор бібліотеки", size=11, color="#1b5e20", bold=True))
    frags.append(text(722, 170, "Виклик до старту main()", size=10, color="#2e7d32"))
    frags.append(text(722, 192, "setvbuf(stdout, NULL, _IOLBF, 0)", size=9, color="#004d40", bold=True))
    frags.append(text(722, 210, "Примусове ввімкнення рядка", size=9, color="#546e7a"))

    frags.append(rect(600, 235, 245, 145, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(722, 258, "Миттєве проходження:", size=11, color="#1b5e20", bold=True))
    frags.append(text(722, 282, "stdbuf -oL grep ... | awk ...", size=9, color="#212121"))
    frags.append(text(722, 305, "Рядки надходять негайно", size=9, color="#1b5e20", bold=True))
    frags.append(text(722, 335, "Прапорці утиліт:", size=10, color="#37474f", bold=True))
    frags.append(text(722, 355, "grep --line-buffered, sed -u", size=9, color="#2e7d32"))

    render(path, 900, 440, *frags)

def build_filter_selection_matrix(path):
    frags = []

    # Outer background
    frags.append(rect(10, 10, 880, 460, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(450, 35, "Дерево прийняття рішень: вибір оптимального класичного фільтра", size=14, color="#263238", bold=True))

    # Card 1: grep
    frags.append(rect(25, 60, 200, 380, fill="#e8eaf6", stroke="#3949ab", sw=1.5, rx=6))
    frags.append(text(125, 88, "grep / egrep", size=14, color="#1a237e", bold=True))
    frags.append(text(125, 108, "Фільтрація рядків", size=11, color="#3949ab"))
    frags.append(rect(35, 125, 180, 75, fill="#ffffff", stroke="#c5cae9", rx=4))
    frags.append(text(125, 148, "Коли обирати:", size=11, color="#1a237e", bold=True))
    frags.append(text(125, 170, "• Відбір за зразком", size=10, color="#212121"))
    frags.append(text(125, 188, "• Інверсія вибірки (-v)", size=10, color="#212121"))
    frags.append(rect(35, 210, 180, 140, fill="#ffffff", stroke="#c5cae9", rx=4))
    frags.append(text(125, 230, "Характеристики:", size=11, color="#283593", bold=True))
    frags.append(text(125, 252, "• Максимальна швидкість", size=9, color="#1b5e20", bold=True))
    frags.append(text(125, 272, "• SIMD-пошук memchr", size=9, color="#37474f"))
    frags.append(text(125, 292, "• O(1) оперативна пам'ять", size=9, color="#37474f"))
    frags.append(text(125, 312, "• Без зміни структури", size=9, color="#546e7a"))
    frags.append(text(125, 332, "• Прапорці -F, -E, -P", size=9, color="#546e7a"))
    frags.append(rect(35, 360, 180, 65, fill="#e8eaf6", stroke="#9fa8da", rx=4))
    frags.append(text(125, 383, "Антипатерн:", size=10, color="#c62828", bold=True))
    frags.append(text(125, 403, "grep | cut | awk замість", size=9, color="#b71c1c"))
    frags.append(text(125, 417, "одного правила awk", size=9, color="#b71c1c"))

    # Card 2: sed / tr / cut
    frags.append(rect(235, 60, 200, 380, fill="#f3e5f5", stroke="#8e24aa", sw=1.5, rx=6))
    frags.append(text(335, 88, "sed / cut / tr", size=14, color="#4a148c", bold=True))
    frags.append(text(335, 108, "Потокова трансформація", size=11, color="#6a1b9a"))
    frags.append(rect(245, 125, 180, 75, fill="#ffffff", stroke="#e1bee7", rx=4))
    frags.append(text(335, 148, "Коли обирати:", size=11, color="#4a148c", bold=True))
    frags.append(text(335, 170, "• Заміна тексту s/old/new/", size=10, color="#212121"))
    frags.append(text(335, 188, "• Вирізання колонок (cut)", size=10, color="#212121"))
    frags.append(rect(245, 210, 180, 140, fill="#ffffff", stroke="#e1bee7", rx=4))
    frags.append(text(335, 230, "Характеристики:", size=11, color="#6a1b9a", bold=True))
    frags.append(text(335, 252, "• Потокова обробка", size=9, color="#1b5e20", bold=True))
    frags.append(text(335, 272, "• Захоплення груп (\\1)", size=9, color="#37474f"))
    frags.append(text(335, 292, "• Діапазони рядків 10,20d", size=9, color="#37474f"))
    frags.append(text(335, 312, "• Заміна символів tr a b", size=9, color="#546e7a"))
    frags.append(text(335, 332, "• Немає арифметики", size=9, color="#546e7a"))
    frags.append(rect(245, 360, 180, 65, fill="#f3e5f5", stroke="#ce93d8", rx=4))
    frags.append(text(335, 383, "Антипатерн:", size=10, color="#c62828", bold=True))
    frags.append(text(335, 403, "Багатопрохідний sed", size=9, color="#b71c1c"))
    frags.append(text(335, 417, "для складної логіки", size=9, color="#b71c1c"))

    # Card 3: awk
    frags.append(rect(445, 60, 200, 380, fill="#e8f5e9", stroke="#388e3c", sw=1.5, rx=6))
    frags.append(text(545, 88, "awk / gawk", size=14, color="#1b5e20", bold=True))
    frags.append(text(545, 108, "Таблична агрегація", size=11, color="#2e7d32"))
    frags.append(rect(455, 125, 180, 75, fill="#ffffff", stroke="#c8e6c9", rx=4))
    frags.append(text(545, 148, "Коли обирати:", size=11, color="#1b5e20", bold=True))
    frags.append(text(545, 170, "• Арифметика по стовпцях", size=10, color="#212121"))
    frags.append(text(545, 188, "• Хеш-таблиці та лічильники", size=10, color="#212121"))
    frags.append(rect(455, 210, 180, 140, fill="#ffffff", stroke="#c8e6c9", rx=4))
    frags.append(text(545, 230, "Характеристики:", size=11, color="#2e7d32", bold=True))
    frags.append(text(545, 252, "• Повноцінна мікромова", size=9, color="#1b5e20", bold=True))
    frags.append(text(545, 272, "• Стан між рядками", size=9, color="#37474f"))
    frags.append(text(545, 292, "• Роздільники $1..$NF", size=9, color="#37474f"))
    frags.append(text(545, 312, "• Блоки BEGIN / END", size=9, color="#546e7a"))
    frags.append(text(545, 332, "• Замінює 3-4 утиліти", size=9, color="#546e7a"))
    frags.append(rect(455, 360, 180, 65, fill="#e8f5e9", stroke="#a5d6a7", rx=4))
    frags.append(text(545, 383, "Антипатерн:", size=10, color="#c62828", bold=True))
    frags.append(text(545, 403, "Повне сортування в пам'яті", size=9, color="#b71c1c"))
    frags.append(text(545, 417, "для гігабайтних файлів", size=9, color="#b71c1c"))

    # Card 4: sort & uniq
    frags.append(rect(655, 60, 200, 380, fill="#fff3e0", stroke="#f57c00", sw=1.5, rx=6))
    frags.append(text(755, 88, "sort & uniq", size=14, color="#e65100", bold=True))
    frags.append(text(755, 108, "Глобальний порядок", size=11, color="#f57c00"))
    frags.append(rect(665, 125, 180, 75, fill="#ffffff", stroke="#ffe0b2", rx=4))
    frags.append(text(755, 148, "Коли обирати:", size=11, color="#e65100", bold=True))
    frags.append(text(755, 170, "• Глобальне впорядкування", size=10, color="#212121"))
    frags.append(text(755, 188, "• Дедуплікація потоку", size=10, color="#212121"))
    frags.append(rect(665, 210, 180, 140, fill="#ffffff", stroke="#ffe0b2", rx=4))
    frags.append(text(755, 230, "Характеристики:", size=11, color="#ef6c00", bold=True))
    frags.append(text(755, 252, "• Зовнішнє злиття (диск)", size=9, color="#1b5e20", bold=True))
    frags.append(text(755, 272, "• Непотоковий бар'єр O(N log N)", size=9, color="#37474f"))
    frags.append(text(755, 292, "• Числові ключі (-k, -n)", size=9, color="#37474f"))
    frags.append(text(755, 312, "• LC_ALL=C для швидкості", size=9, color="#546e7a"))
    frags.append(text(755, 332, "• Паралелізм (--parallel)", size=9, color="#546e7a"))
    frags.append(rect(665, 360, 180, 65, fill="#fff3e0", stroke="#ffcc80", rx=4))
    frags.append(text(755, 383, "Антипатерн:", size=10, color="#c62828", bold=True))
    frags.append(text(755, 403, "sort без LC_ALL=C або", size=9, color="#b71c1c"))
    frags.append(text(755, 417, "sort для вже агрегованих даних", size=9, color="#b71c1c"))

    render(path, 900, 480, *frags)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    build_classic_pipeline_vs_awk(os.path.join(out_dir, "classic-pipeline-vs-awk.svg"))
    build_buffering_and_stdbuf(os.path.join(out_dir, "buffering-and-stdbuf.svg"))
    build_filter_selection_matrix(os.path.join(out_dir, "filter-selection-matrix.svg"))
    print("Figures generated successfully.")
