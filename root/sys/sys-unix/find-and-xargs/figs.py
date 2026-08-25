# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_find_stream_vs_glob(path):
    frags = []

    # Title & Subtitle
    frags.append(text(460, 25, "Розгортання маски оболонки vs Потоковий обхід find", size=16, color=INK, bold=True))

    # Left Container - Shell Globbing
    frags.append(rect(20, 50, 420, 360, fill="#fdf7f7", stroke="#c0392b", sw=1.5, rx=8))
    frags.append(text(230, 75, "1. Жадібне розгортання оболонки (rm *.log)", size=13, color="#c0392b", bold=True))

    # Steps in left box
    frags.append(rect(35, 95, 390, 65, fill="#ffffff", stroke="#e74c3c", sw=1, rx=4))
    frags.append(text(230, 115, "1. Сканування всього каталогу в пам'ять", size=12, color=INK, bold=True))
    frags.append(text(230, 135, "Оболонка будує масив argv[0...N] в ОЗП", size=11, color=MUTED))
    frags.append(text(230, 150, "Блокує виконання до повного зчитування всіх імен", size=10, color=MUTED))

    frags.append(rect(35, 175, 390, 85, fill="#fdecea", stroke="#c0392b", sw=1.2, rx=4))
    frags.append(text(230, 195, "2. Перевірка ліміту ядра: ARG_MAX / _STK_LIM", size=12, color="#c0392b", bold=True))
    frags.append(text(230, 215, "Розмір масиву argv + environ > 2–6 МБ", size=11, color="#c0392b"))
    frags.append(text(230, 235, "execve() повертає -1 (errno = E2BIG)", size=11, color="#c0392b", bold=True))
    frags.append(text(230, 250, "Argument list too long — повна відмова команди", size=10, color="#c0392b"))

    frags.append(rect(35, 275, 390, 120, fill="#ffffff", stroke="#95a5a6", sw=1, rx=4))
    frags.append(text(230, 295, "Наслідки для великих файлових систем:", size=11, color=INK, bold=True))
    frags.append(text(230, 315, "• Споживання пам'яті: O(N) де N — кількість файлів", size=11, color=POS))
    frags.append(text(230, 335, "• Велика затримка (latency) до появи першого файлу", size=11, color=POS))
    frags.append(text(230, 355, "• Неможливість обробки мільйонів записів", size=11, color=POS))
    frags.append(text(230, 375, "• Ризик вичерпання стеку та аварії процесу", size=10, color=MUTED))

    # Right Container - find Streaming
    frags.append(rect(480, 50, 420, 360, fill="#f4faf6", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(690, 75, "2. Лінивий потоковий обхід find (find . -name ...)", size=13, color="#27ae60", bold=True))

    # Steps in right box
    frags.append(rect(495, 95, 390, 65, fill="#ffffff", stroke="#2ecc71", sw=1, rx=4))
    frags.append(text(690, 115, "1. Пакетне читання getdents64() у фіксований буфер", size=12, color=INK, bold=True))
    frags.append(text(690, 135, "Зчитування порціями по 32 KB без повного завантаження", size=11, color=MUTED))
    frags.append(text(690, 150, "Миттєва передача знайденого імені на фільтрацію", size=10, color=MUTED))

    frags.append(rect(495, 175, 390, 85, fill="#e8f8f0", stroke="#27ae60", sw=1.2, rx=4))
    frags.append(text(690, 195, "2. Потокова фільтрація предикатів (AST)", size=12, color="#27ae60", bold=True))
    frags.append(text(690, 215, "Обчислення виразів: -type, -name, -mtime, -perm", size=11, color="#27ae60"))
    frags.append(text(690, 235, "Відсутність виклику execve() на етапі пошуку", size=11, color="#27ae60", bold=True))
    frags.append(text(690, 250, "Нульовий ризик переповнення ARG_MAX під час виводу", size=10, color="#27ae60"))

    frags.append(rect(495, 275, 390, 120, fill="#ffffff", stroke="#95a5a6", sw=1, rx=4))
    frags.append(text(690, 295, "Переваги для великих файлових систем:", size=11, color=INK, bold=True))
    frags.append(text(690, 315, "• Споживання пам'яті: O(depth) — лише стек глибини дерева", size=11, color=FIELD))
    frags.append(text(690, 335, "• Нульова затримка: перший результат віддається одразу", size=11, color=FIELD))
    frags.append(text(690, 355, "• Масштабування на сотні мільйонів файлів у дереві", size=11, color=FIELD))
    frags.append(text(690, 375, "• Повний контроль над порядком і глибиною обходу", size=10, color=MUTED))

    render(path, 920, 430, *frags)

def build_find_exec_vs_xargs_batching(path):
    frags = []

    # Title & Subtitle
    frags.append(text(460, 25, "Стратегії виконання дій: поодинокий запуск, пакетування та пул процесів", size=15, color=INK, bold=True))

    # Row 1: find -exec {} \;
    frags.append(rect(20, 50, 880, 95, fill="#fdf7f7", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(text(40, 75, "find . -name '*.log' -exec rm {} \\;", size=12, color="#c0392b", bold=True, anchor="start"))
    frags.append(text(880, 75, "Поодинокий виклик (1:1)", size=12, color="#c0392b", bold=True, anchor="end"))

    frags.append(rect(40, 90, 140, 42, fill="#ffffff", stroke="#e74c3c", rx=4))
    frags.append(text(110, 115, "1. fork() + execve()", size=11, color=INK))

    frags.append(arrow(185, 111, 220, 111, color="#c0392b"))

    frags.append(rect(225, 90, 140, 42, fill="#ffffff", stroke="#e74c3c", rx=4))
    frags.append(text(295, 115, "2. rm file1.log", size=11, color=INK))

    frags.append(arrow(370, 111, 405, 111, color="#c0392b"))

    frags.append(rect(410, 90, 140, 42, fill="#ffffff", stroke="#e74c3c", rx=4))
    frags.append(text(480, 115, "3. waitpid() (вихід)", size=11, color=INK))

    frags.append(text(710, 115, "N файлів = N процесів (наприклад, 100 000 fork/exec)", size=11, color="#c0392b", bold=True))

    # Row 2: find -exec {} + / xargs
    frags.append(rect(20, 160, 880, 95, fill="#f4faf6", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(text(40, 185, "find . -name '*.log' -exec rm {} +   або   find ... -print0 | xargs -0 rm", size=12, color="#27ae60", bold=True, anchor="start"))
    frags.append(text(880, 185, "Пакетування аргументів (1:K)", size=12, color="#27ae60", bold=True, anchor="end"))

    frags.append(rect(40, 200, 200, 42, fill="#ffffff", stroke="#2ecc71", rx=4))
    frags.append(text(140, 225, "Буферизація аргументів", size=11, color=INK))

    frags.append(arrow(245, 221, 280, 221, color="#27ae60"))

    frags.append(rect(285, 200, 265, 42, fill="#ffffff", stroke="#2ecc71", rx=4))
    frags.append(text(417, 225, "rm file1.log file2.log ... file1000.log", size=11, color=INK))

    frags.append(arrow(555, 221, 590, 221, color="#27ae60"))

    frags.append(rect(595, 200, 130, 42, fill="#ffffff", stroke="#2ecc71", rx=4))
    frags.append(text(660, 225, "1 вихід (wait)", size=11, color=INK))

    frags.append(text(800, 225, "Економія CPU 99%+", size=11, color="#27ae60", bold=True))

    # Row 3: xargs -P 4
    frags.append(rect(20, 270, 880, 135, fill="#f0f4fa", stroke="#2457d6", sw=1.5, rx=6))
    frags.append(text(40, 295, "find ... -print0 | xargs -0 -n 1000 -P 4 worker_cmd", size=12, color="#2457d6", bold=True, anchor="start"))
    frags.append(text(880, 295, "Пул паралельних воркерів (-P 4)", size=12, color="#2457d6", bold=True, anchor="end"))

    # Worker boxes
    w_labels = ["Воркер 1 (PID 101)\nПакет 1 (1...1000)",
                "Воркер 2 (PID 102)\nПакет 2 (1001...2000)",
                "Воркер 3 (PID 103)\nПакет 3 (2001...3000)",
                "Воркер 4 (PID 104)\nПакет 4 (3001...4000)"]
    for i in range(4):
        bx = 40 + i * 215
        frags.append(rect(bx, 315, 200, 50, fill="#ffffff", stroke="#3498db", rx=4))
        frags.append(text(bx + 100, 335, w_labels[i].split("\n")[0], size=11, color="#2457d6", bold=True))
        frags.append(text(bx + 100, 353, w_labels[i].split("\n")[1], size=10, color=MUTED))

    frags.append(text(460, 390, "Паралельне завантаження 4 ядер CPU | Окремі пакети | Автоматичне донаповнення черги", size=11, color=INK, bold=True))

    render(path, 920, 420, *frags)

def build_nul_byte_stream_safety(path):
    frags = []

    # Title & Subtitle
    frags.append(text(460, 25, "Безпека потоку даних: розділювач Newline vs Нульовий байт NUL", size=15, color=INK, bold=True))

    # Top: Newline / space splitting (Vulnerable)
    frags.append(rect(20, 50, 880, 165, fill="#fdf7f7", stroke="#c0392b", sw=1.5, rx=8))
    frags.append(text(40, 75, "1. Небезпечний конвеєр з розділювачем \\n / пробіл (find | xargs)", size=13, color="#c0392b", bold=True, anchor="start"))

    frags.append(rect(40, 90, 260, 55, fill="#ffffff", stroke="#e74c3c", rx=4))
    frags.append(text(170, 110, "Імена файлів у файловій системі:", size=11, color=INK, bold=True))
    frags.append(text(170, 130, "\"my report 2026.pdf\", \"-rf\", \"doc's.txt\"", size=10, color="#c0392b"))

    frags.append(arrow(305, 117, 345, 117, color="#c0392b"))

    frags.append(rect(350, 90, 250, 55, fill="#ffffff", stroke="#e74c3c", rx=4))
    frags.append(text(475, 110, "Токенізація xargs (за замовчуванням):", size=11, color=INK, bold=True))
    frags.append(text(475, 130, "Розбиття за пробілами, \\t, \\n та лапками", size=10, color=MUTED))

    frags.append(arrow(605, 117, 645, 117, color="#c0392b"))

    frags.append(rect(650, 90, 230, 55, fill="#fdecea", stroke="#c0392b", sw=1.2, rx=4))
    frags.append(text(765, 110, "Помилки та вразливості:", size=11, color="#c0392b", bold=True))
    frags.append(text(765, 130, "Пошкодження імен / Ін'єкція прапорців", size=10, color="#c0392b"))

    # Explanation bullets below top flow
    frags.append(text(40, 165, "• 'my report 2026.pdf' розбивається на 3 аргументи: 'my', 'report', '2026.pdf' (помилка No such file)", size=11, color="#c0392b", anchor="start"))
    frags.append(text(40, 185, "• Непарна лапка в імені 'doc\\'s.txt' викликає фатальну зупинку: xargs: unmatched single quote", size=11, color="#c0392b", anchor="start"))
    frags.append(text(40, 203, "• Файл з ім'ям '-rf' сприймається утилітою як прапорець (option injection), а не шлях до файлу", size=11, color="#c0392b", anchor="start"))

    # Bottom: NUL-delimited stream (Safe)
    frags.append(rect(20, 230, 880, 175, fill="#f4faf6", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(40, 255, "2. Безпечний конвеєр з нульовим байтом (find -print0 | xargs -0)", size=13, color="#27ae60", bold=True, anchor="start"))

    frags.append(rect(40, 270, 260, 55, fill="#ffffff", stroke="#2ecc71", rx=4))
    frags.append(text(170, 290, "Вивід find -print0:", size=11, color=INK, bold=True))
    frags.append(text(170, 310, "./my report 2026.pdf\\0./-rf\\0./doc's.txt\\0", size=10, color="#27ae60"))

    frags.append(arrow(305, 297, 345, 297, color="#27ae60"))

    frags.append(rect(350, 270, 250, 55, fill="#ffffff", stroke="#2ecc71", rx=4))
    frags.append(text(475, 290, "Читання xargs -0 (--null):", size=11, color=INK, bold=True))
    frags.append(text(475, 310, "Розділювач — виключно байт 0x00 (NUL)", size=10, color=MUTED))

    frags.append(arrow(605, 297, 645, 297, color="#27ae60"))

    frags.append(rect(650, 270, 230, 55, fill="#e8f8f0", stroke="#27ae60", sw=1.2, rx=4))
    frags.append(text(765, 290, "Гарантований результат:", size=11, color="#27ae60", bold=True))
    frags.append(text(765, 310, "100% збереження байтового образу", size=10, color="#27ae60"))

    # Explanation bullets below bottom flow
    frags.append(text(40, 345, "• Байт 0x00 (NUL) та 0x2F (/) — єдині заборонені байти в іменах файлів за стандартом POSIX", size=11, color="#27ae60", anchor="start"))
    frags.append(text(40, 365, "• Пробіли, табуляції, лапки та символи перенесення рядків передаються як атомарні частини одного шляху", size=11, color="#27ae60", anchor="start"))
    frags.append(text(40, 385, "• Префікс './' або розділювач аргументів '--' повністю унеможливлює ін'єкцію прапорців", size=11, color="#27ae60", anchor="start"))

    render(path, 920, 420, *frags)

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    build_find_stream_vs_glob(os.path.join(img_dir, 'find-stream-vs-glob.svg'))
    build_find_exec_vs_xargs_batching(os.path.join(img_dir, 'find-exec-vs-xargs-batching.svg'))
    build_nul_byte_stream_safety(os.path.join(img_dir, 'nul-byte-stream-safety.svg'))
    print("Figures generated successfully.")
