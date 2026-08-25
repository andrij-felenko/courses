# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Накладні витрати fork() + exec() у циклі ──────────────────────────────
def fig_fork_exec_overhead():
    W, H = 1040, 560
    p = []

    # Ліва частина: Bash у циклі (10 000 fork/exec)
    p.append(fitbox(30, 20, 460, 40,
                    "Bash: виконання утиліти в циклі (наприклад, cut або bc)",
                    size=13, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(fitbox(45, 80, 430, 55,
                    "1. Батьківський процес Shell (bash pid=1001)\n"
                    "Ітерація циклу for: підготовка команди $var=$(cut -d: -f1)",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(260, 135, 260, 160, color=LINE, sw=1.6))

    p.append(fitbox(45, 160, 430, 65,
                    "2. Системний виклик fork(2) / clone(2)\n"
                    "• Копіювання таблиць сторінок пам'яті (Page Tables, CoW)\n"
                    "• Створення нового дескриптора процесу (task_struct) у ядрі",
                    size=11, fill=WARM, stroke=POS, sw=1.4, color=INK))

    p.append(arrow(260, 225, 260, 250, color=LINE, sw=1.6))

    p.append(fitbox(45, 250, 430, 80,
                    "3. Системний виклик execve(2)\n"
                    "• Очищення адресного простору дочірнього процесу\n"
                    "• Зчитування ELF-заголовка та виклик динамічного лінкера ld.so\n"
                    "• Відображення бібліотек (libc.so) та виконання секцій .init",
                    size=11, fill=WARM, stroke=POS, sw=1.4, color=INK))

    p.append(arrow(260, 330, 260, 355, color=LINE, sw=1.6))

    p.append(fitbox(45, 355, 430, 65,
                    "4. Виконання роботи та завершення exit(0)\n"
                    "• Робота: виділення 1 рядка за 2 мікросекунди\n"
                    "• Знищення простору пам'яті, генерація сигналу SIGCHLD",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(260, 420, 260, 445, color=LINE, sw=1.6))

    p.append(fitbox(45, 445, 430, 55,
                    "5. Батьківський процес: waitpid(2) + читання каналу\n"
                    "⚠️ Ціна на 10 000 ітерацій: ~15-30 секунд CPU-часу ядра",
                    size=11, fill=WARM, stroke=POS, sw=1.6, color=POS, bold=True))

    # Права частина: Нативна мова (Python / Go / Rust / C++)
    p.append(fitbox(550, 20, 460, 40,
                    "Нативна мова: виконання всередині єдиного процесу",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(fitbox(565, 80, 430, 70,
                    "1. Єдиний процес застосунку (pid=2001)\n"
                    "Вся пам'ять, структури даних та runtime завантажені один раз\n"
                    "при запуску програми",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(780, 150, 780, 190, color=LINE, sw=1.6))

    p.append(fitbox(565, 190, 430, 110,
                    "2. Ітерація нативного циклу (10 000 проходів)\n"
                    "• Розділення рядка в пам'яті (string_view / slice / split)\n"
                    "• Нуль системних викликів ядра (нуль context switch)\n"
                    "• Нуль дублювань таблиць сторінок\n"
                    "• Дані лишаються в кеші процесора L1 / L2",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.6, color=INK, bold=True))

    p.append(arrow(780, 300, 780, 340, color=LINE, sw=1.6))

    p.append(fitbox(565, 340, 430, 70,
                    "3. Завершення обчислень\n"
                    "Результати накопичено в типізованому векторі/структурі\n"
                    "без втрати типів і без серіалізації в текст",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(780, 410, 780, 445, color=LINE, sw=1.6))

    p.append(fitbox(565, 445, 430, 55,
                    "Підсумок продуктивності:\n"
                    "⚡ Ціна на 10 000 ітерацій: менше 1-5 мілісекунд (у 1000+ разів швидше)",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))

    render(os.path.join(OUT, "fork-exec-overhead.svg"), W, H, *p)


# ── 2. Матриця інженерних критеріїв вибору середовища ────────────────────────
def fig_decision_matrix():
    W, H = 1060, 580
    p = []

    # Заголовок
    p.append(fitbox(280, 15, 500, 38,
                    "Дерево інженерних рішень: Shell чи мова загального призначення?",
                    size=13, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))

    # Крок 1: Обсяг і характер задачі
    p.append(fitbox(30, 70, 480, 60,
                    "1. Характер коду та обсяг:\n"
                    "Чи скрипт перевищує 150 рядків або містить складні розгалуження?",
                    size=11, fill="#fff", stroke=LINE, sw=1.4, color=INK))

    p.append(fitbox(550, 70, 480, 60,
                    "Так → Перехід на Python / Go\n"
                    "Ні (10-50 рядків лінійних команд) → Залишаємось у Shell",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    # Крок 2: Структури даних і формати
    p.append(fitbox(30, 150, 480, 60,
                    "2. Дані: чи є вкладений JSON/YAML, бінарні байти,\n"
                    "масиви об'єктів або хеш-таблиці зі структурами?",
                    size=11, fill="#fff", stroke=LINE, sw=1.4, color=INK))

    p.append(fitbox(550, 150, 480, 60,
                    "Так → Python (json, pydantic) або Go (struct, unmarshal)\n"
                    "Ні (суто текстові рядки та шляхи файлів) → Shell прийнятний",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    # Крок 3: Обчислення та математика
    p.append(fitbox(30, 230, 480, 60,
                    "3. Математика: чи потрібні дробові числа (float),\n"
                    "статистичні розрахунки чи цикли на 10 000+ операцій?",
                    size=11, fill="#fff", stroke=LINE, sw=1.4, color=INK))

    p.append(fitbox(550, 230, 480, 60,
                    "Так → Мова програмування (нативна арифметика CPU)\n"
                    "Ні (лише цілочисельні лічильники в межах $((-))) → Shell",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    # Крок 4: Паралелізм і надійність
    p.append(fitbox(30, 310, 480, 60,
                    "4. Паралелізм і надійність: чи потрібні пули воркерів,\n"
                    "синхронізація м'ютексами, структуровані юніт-тести?",
                    size=11, fill="#fff", stroke=LINE, sw=1.4, color=INK))

    p.append(fitbox(550, 310, 480, 60,
                    "Так → Go (goroutines), Python (asyncio/threads), Rust\n"
                    "Ні (простий конвеєр cmd1 | cmd2) → Shell ідеальний",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    # Крок 5: Розгортання та дистрибуція
    p.append(fitbox(30, 390, 480, 60,
                    "5. Дистрибуція утиліти:\n"
                    "Потрібен автономний статичний бінарник без залежностей?",
                    size=11, fill="#fff", stroke=LINE, sw=1.4, color=INK))

    p.append(fitbox(550, 390, 480, 60,
                    "Так → Go або Rust (єдиний виконуваний файл без runtime)\n"
                    "Ні (серверне середовище з наявним Python) → Python-скрипт",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    # Підсумкова плашка
    p.append(fitbox(30, 470, 1000, 80,
                    "Золоте правило системної інженерії:\n"
                    "Shell призначений для ОРКЕСТРАЦІЇ готових утиліт у лінійні конвеєри.\n"
                    "Щойно у сценарії з'являється власна складна бізнес-логіка, парсинг або маніпуляція станом — це програма мовою загального призначення.",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    render(os.path.join(OUT, "decision-matrix.svg"), W, H, *p)


# ── 3. Архітектурне порівняння просторів пам'яті ─────────────────────────────
def fig_memory_architecture():
    W, H = 1040, 520
    p = []

    # Ліва панель: Shell / Unix Pipeline
    p.append(fitbox(40, 20, 450, 40,
                    "Модель оболонки: ізольовані процеси та байтовий потік",
                    size=12, fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))

    p.append(fitbox(55, 75, 420, 80,
                    "Процес 1: grep (pid=301)\n"
                    "• Власний адресний простір, таблиці сторінок\n"
                    "• Текстовий вихід stdout через pipe(2)\n"
                    "⚠️ Немає доступу до внутрішнього стану інших процесів",
                    size=11, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    p.append(arrow(265, 155, 265, 185, color=NEG, sw=2.0))
    p.append(text(265, 175, "Канал ядра: нетипізовані байти без метаданих", size=10, color=NEG, bold=True))

    p.append(fitbox(55, 185, 420, 80,
                    "Процес 2: awk / jq (pid=302)\n"
                    "• Власний парсер тексту з нуля\n"
                    "• Втрата типів: перетворення чисел у текст і знову в числа\n"
                    "• Буферизація stdio (4 КБ / 64 КБ)",
                    size=11, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    p.append(arrow(265, 265, 265, 295, color=NEG, sw=2.0))
    p.append(text(265, 285, "Канал ядра: наступний текстовий потік", size=10, color=NEG, bold=True))

    p.append(fitbox(55, 295, 420, 80,
                    "Процес 3: sort / uniq (pid=303)\n"
                    "• Повне вичитування всього потоку до EOF перед сортуванням\n"
                    "• Блокування конвеєра при великих обсягах",
                    size=11, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    p.append(fitbox(55, 395, 420, 95,
                    "Характеристики конвеєра оболонки:\n"
                    "✓ Простота компонування готових бінарників\n"
                    "✗ Складність обробки помилок у середині ланцюга\n"
                    "✗ Нульова типізація та накладні витрати серіалізації",
                    size=11, fill=WARM, stroke=POS, sw=1.2, color=INK))

    # Права панель: Модель мови загального призначення (Python / Go / C++)
    p.append(fitbox(550, 20, 450, 40,
                    "Модель мови: єдиний адресний простір і типізована пам'ять",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK, bold=True))

    p.append(fitbox(565, 75, 420, 300,
                    "Єдиний адресний простір програми (pid=4001)\n\n"
                    "┌─────────────────────────────────────────────────────────┐\n"
                    "│ Стек викликів та потоки (Threads / Goroutines)           │\n"
                    "│ • Пул воркерів без створення процесів ядра              │\n"
                    "│ • Локальні змінні з суворою типізацією                  │\n"
                    "├─────────────────────────────────────────────────────────┤\n"
                    "│ Купа (Heap / Managed Memory)                            │\n"
                    "│ • Типізовані структури: struct Metrics { float cpu; }   │\n"
                    "│ • Хеш-таблиці, бінарні буфери, дерева об'єктів          │\n"
                    "│ • Пряме передавання вказівників без копіювання байтів   │\n"
                    "├─────────────────────────────────────────────────────────┤\n"
                    "│ Вбудовані механізми контролю                            │\n"
                    "│ • Обробка винятків (try/catch, Result<T, E>)           │\n"
                    "│ • М'ютекси, атоміки, канали синхронізації               │\n"
                    "└─────────────────────────────────────────────────────────┘",
                    size=10, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(fitbox(565, 395, 420, 95,
                    "Характеристики монолітної програми:\n"
                    "✓ Миттєвий доступ до пам'яті без IPC і серіалізації\n"
                    "✓ Сувора типізація даних на етапі компіляції/виконання\n"
                    "✓ Повний детермінізм при обробці виняткових ситуацій",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(OUT, "shell-vs-native-architecture.svg"), W, H, *p)


if __name__ == "__main__":
    fig_fork_exec_overhead()
    fig_decision_matrix()
    fig_memory_architecture()
    print("All figures generated successfully.")
