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


# ── 1. Сім фаз конвеєра розкриття ────────────────────────────────────────────
def fig_expansion_pipeline():
    W, H = 1060, 620
    p = []

    # Заголовок / Вхідний рядок
    p.append(fitbox(260, 20, 540, 42,
                    "Вхідний командний рядок: сирий потік символів від користувача",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    p.append(arrow(530, 62, 530, 95, color=LINE, sw=2.0))

    # Колонка етапів розкриття
    # Фаза 1: Brace Expansion
    p.append(fitbox(40, 95, 450, 60,
                    "1. Розкриття фігурних дужок (Brace Expansion)\n"
                    "Генерація текстових комбінацій: a{1,2}b → a1b a2b\n"
                    "(виконується ДО будь-яких перевірок змінних і файлів)",
                    size=11, fill="#fff", stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(530, 95, 490, 60,
                    "Властивість: суто синтаксичний генератор рядків.\n"
                    "Не знає про змінні чи файли; створює нові токени для конвеєра.",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(265, 155, 265, 180, color=LINE, sw=1.8))

    # Фаза 2: Tilde Expansion
    p.append(fitbox(40, 180, 450, 55,
                    "2. Розкриття тильди (Tilde Expansion)\n"
                    "Заміна префікса ~ на $HOME або домашній каталог користувача\n"
                    "~ → /home/user, ~alice → /home/alice",
                    size=11, fill="#fff", stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(530, 180, 490, 55,
                    "Властивість: замінює префікс на початку слова або після «:» у PATH.",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(265, 235, 265, 260, color=LINE, sw=1.8))

    # Фаза 3: Параметри, Команди, Арифметика
    p.append(fitbox(40, 260, 450, 75,
                    "3. Потрійна підстановка в один прохід (зліва направо)\n"
                    "• Параметри та змінні: $VAR, ${VAR:-default}\n"
                    "• Підстановка команд: $(command) або `command`\n"
                    "• Арифметичні вирази: $((x + 2 * y))",
                    size=11, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    p.append(fitbox(530, 260, 490, 75,
                    "Критичний момент: підстановки генерують новий текст.\n"
                    "Саме цей згенерований текст (якщо він НЕ в лапках) підлягає\n"
                    "наступному розбиттю на слова (Word Splitting).",
                    size=11, fill=COOL, stroke=NEG, sw=1.2, color=INK))

    p.append(arrow(265, 335, 265, 360, color=LINE, sw=1.8))

    # Фаза 4: Word Splitting
    p.append(fitbox(40, 360, 450, 65,
                    "4. Поділ на слова (Word Splitting за IFS)\n"
                    "Сканування результатів фази 3 на символи з $IFS (пробіл, TAB, LF)\n"
                    "⚠️ Відбувається ТІЛЬКИ для результатів підстановок без подвійних лапок!",
                    size=11, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(fitbox(530, 360, 490, 65,
                    "Головне джерело помилок: рядок «My Photo.jpg» без лапок\n"
                    "розривається на два незалежні аргументи «My» та «Photo.jpg».",
                    size=11, fill=WARM, stroke=POS, sw=1.2, color=INK))

    p.append(arrow(265, 425, 265, 450, color=LINE, sw=1.8))

    # Фаза 5: Globbing
    p.append(fitbox(40, 450, 450, 55,
                    "5. Розгортання імен файлів (Filename Expansion / Globbing)\n"
                    "Зіставлення незахищених масок *, ?, [...] з файлами на диску через VFS",
                    size=11, fill="#fff", stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(530, 450, 490, 55,
                    "Властивість: якщо збігів немає, за стандартом POSIX маска лишається як є.",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(265, 505, 265, 530, color=LINE, sw=1.8))

    # Фаза 6: Quote Removal
    p.append(fitbox(40, 530, 450, 55,
                    "6. Видалення лапок (Quote Removal)\n"
                    "Вилучення синтаксичних лапок (', \", \\), які захищали текст на фазах 4 і 5",
                    size=11, fill="#fff", stroke=LINE, sw=1.5, color=INK))

    p.append(fitbox(530, 530, 490, 55,
                    "Підсумок: сформовано чистий масив char *argv[] для execve(2).\n"
                    "Ядро Linux отримує готові відокремлені аргументи без лапок.",
                    size=11, fill=PALE, stroke=LINE, sw=1.5, color=INK, bold=True))

    render(os.path.join(OUT, "expansion-pipeline.svg"), W, H, *p,
           title="Сім фаз розкриття командного рядка в оболонці")


# ── 2. Матриця проникності лапок ─────────────────────────────────────────────
def fig_quoting_shields():
    W, H = 1040, 490
    p = []

    p.append(fitbox(200, 20, 640, 38,
                    "Броня лапок: що блокує і що пропускає кожен механізм цитування",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    cols = [
        ("Без лапок (Unquoted)", 40, 220, SOFT, LINE),
        ("Подвійні лапки \"...\"", 280, 230, COOL, NEG),
        ("Одинарні лапки '...'", 530, 230, WARM, POS),
        ("ANSI-C лапки $'\\n'", 780, 220, GREENF, FIELD),
    ]

    for title, x, w, bg_col, br_col in cols:
        p.append(fitbox(x, 75, w, 35, title, size=11, fill=bg_col, stroke=br_col, sw=1.8, color=INK, bold=True))

    rows = [
        ("Розгортання фігурних дужок {a,b}",
         "Дозволено", "Заблоковано (текст)", "Заблоковано (текст)", "Заблоковано (текст)"),
        ("Розгортання тильди ~",
         "Дозволено", "Заблоковано (~literal)", "Заблоковано (~literal)", "Заблоковано"),
        ("Розгортання параметрів $VAR",
         "Дозволено", "Дозволено ($ підставляється)", "Заблоковано (дослівний $)", "Заблоковано"),
        ("Підстановка команд $(cmd)",
         "Дозволено", "Дозволено (виконується)", "Заблоковано (дослівний $)", "Заблоковано"),
        ("Арифметика $((expr))",
         "Дозволено", "Дозволено (обчислюється)", "Заблоковано (дослівний $)", "Заблоковано"),
        ("Поділ на слова (Word Splitting)",
         "АКТИВНИЙ (ділить по IFS)", "ЗАБЛОКОВАНО (одне слово)", "ЗАБЛОКОВАНО (одне слово)", "ЗАБЛОКОВАНО"),
        ("Глобінг файлів (*, ?, [])",
         "АКТИВНИЙ (шукає у VFS)", "ЗАБЛОКОВАНО (символи *)", "ЗАБЛОКОВАНО (символи *)", "ЗАБЛОКОВАНО"),
        ("ESC-послідовності (\\n, \\t)",
         "Ні (дослівний слеш)", "Тільки для $, \", `, \\", "Ні (дослівний слеш)", "АКТИВНО (байтові коди)"),
    ]

    y = 120
    for r_title, c1, c2, c3, c4 in rows:
        p.append(fitbox(40, y, 220, 36, r_title + "\n" + c1, size=9, fill="#fff", stroke=LINE, sw=1.0, color=INK))
        p.append(fitbox(280, y, 230, 36, c2, size=9, fill="#fff", stroke=NEG, sw=1.0, color=INK))
        p.append(fitbox(530, y, 230, 36, c3, size=9, fill="#fff", stroke=POS, sw=1.0, color=INK))
        p.append(fitbox(780, y, 220, 36, c4, size=9, fill="#fff", stroke=FIELD, sw=1.0, color=INK))
        y += 42

    render(os.path.join(OUT, "quoting-shields.svg"), W, H, *p,
           title="Матриця проникності лапок в оболонці")


# ── 3. Трасування змінної з пробілом ──────────────────────────────────────────
def fig_word_splitting_trace():
    W, H = 1040, 500
    p = []

    p.append(fitbox(200, 20, 640, 38,
                    "Походження пастки: шлях змінної FILE=\"My Photo.jpg\"",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Ліва колонка: без лапок (катастрофа)
    p.append(fitbox(40, 75, 460, 40,
                    "НЕБЕЗПЕЧНО: rm $FILE (без лапок)",
                    size=12, fill=WARM, stroke=POS, sw=2.0, color=POS, bold=True))

    p.append(arrow(270, 115, 270, 140, color=POS, sw=1.5))

    p.append(fitbox(40, 140, 460, 50,
                    "Фаза 3 (Parameter Expansion):\n"
                    "Змінна $FILE розгортається в текст: rm My Photo.jpg",
                    size=11, fill="#fff", stroke=POS, sw=1.2, color=INK))

    p.append(arrow(270, 190, 270, 215, color=POS, sw=1.5))

    p.append(fitbox(40, 215, 460, 65,
                    "Фаза 4 (Word Splitting за IFS=' \\t\\n'):\n"
                    "Оболонка бачить незахищений пробіл у згенерованому тексті\n"
                    "→ Створює ДВА окремі токени: [\"My\"] та [\"Photo.jpg\"]!",
                    size=11, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(arrow(270, 280, 270, 305, color=POS, sw=1.5))

    p.append(fitbox(40, 305, 460, 50,
                    "Фаза 5 та 6 (Globbing & Quote Removal):\n"
                    "Токени «My» та «Photo.jpg» не є масками й лишаються без змін.",
                    size=11, fill="#fff", stroke=POS, sw=1.2, color=INK))

    p.append(arrow(270, 355, 270, 380, color=POS, sw=1.5))

    p.append(fitbox(40, 380, 460, 90,
                    "Підсумок системного виклику execve(\"/bin/rm\", argv, ...):\n"
                    "argv[0] = \"rm\"\n"
                    "argv[1] = \"My\"\n"
                    "argv[2] = \"Photo.jpg\"\n"
                    "💥 Катастрофа: rm намагається видалити два неіснуючі файли!",
                    size=10, fill=WARM, stroke=POS, sw=2.0, color=INK, bold=True))

    # Права колонка: у подвійних лапках (правильно)
    p.append(fitbox(540, 75, 460, 40,
                    "ПРАВИЛЬНО: rm \"$FILE\" (у подвійних лапках)",
                    size=12, fill=GREENF, stroke=FIELD, sw=2.0, color=FIELD, bold=True))

    p.append(arrow(770, 115, 770, 140, color=FIELD, sw=1.5))

    p.append(fitbox(540, 140, 460, 50,
                    "Фаза 3 (Parameter Expansion):\n"
                    "Змінна $FILE розгортається всередині захищеного блоку: rm \"My Photo.jpg\"",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(770, 190, 770, 215, color=FIELD, sw=1.5))

    p.append(fitbox(540, 215, 460, 65,
                    "Фаза 4 (Word Splitting):\n"
                    "ЗАБЛОКОВАНО подвійними лапками!\n"
                    "Пробіл розглядається як буквальний символ даних, а не роздільник слів.",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(arrow(770, 280, 770, 305, color=FIELD, sw=1.5))

    p.append(fitbox(540, 305, 460, 50,
                    "Фаза 6 (Quote Removal):\n"
                    "Оболонка знімає захисні лапки. Рядок лишається єдиним токеном.",
                    size=11, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    p.append(arrow(770, 355, 770, 380, color=FIELD, sw=1.5))

    p.append(fitbox(540, 380, 460, 90,
                    "Підсумок системного виклику execve(\"/bin/rm\", argv, ...):\n"
                    "argv[0] = \"rm\"\n"
                    "argv[1] = \"My Photo.jpg\"\n\n"
                    "✓ Успіх: програма rm отримує рівно один аргумент із пробілом.",
                    size=10, fill=GREENF, stroke=FIELD, sw=2.0, color=INK, bold=True))

    render(os.path.join(OUT, "word-splitting-trace.svg"), W, H, *p,
           title="Порівняння розкриття змінної з пробілом у лапках та без лапок")


# ── 4. Позиційні параметри "$@" проти "$*" ───────────────────────────────────
def fig_dollar_at_vs_dollar_star():
    W, H = 1040, 520
    p = []

    p.append(fitbox(180, 20, 680, 38,
                    "Позиційні параметри: вхід $1=\"a b\", $2=\"c\", $3=\"d e\"",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    blocks = [
        ("Конструкція \"$@\" (у лапках)",
         "Розкривається як: \"$1\" \"$2\" \"$3\"\n"
         "• Ідеально зберігає межі кожного елемента\n"
         "• Не розбиває пробіли всередині параметрів\n"
         "• Не залежить від змінної IFS\n"
         "• Генерує N окремих слів (за кількістю $#)",
         "argv[1] = \"a b\"\nargv[2] = \"c\"\nargv[3] = \"d e\"\n\n(Всього 3 аргументи)",
         40, 75, 460, GREENF, FIELD),

        ("Конструкція \"$*\" (у лапках)",
         "Розкривається як: \"$1c$2c$3\" (де c — перший символ IFS)\n"
         "• Склеює всі параметри в ОДИН суцільний рядок\n"
         "• При дефолтному IFS склеює через пробіл\n"
         "• Знищує початкові межі масиву\n"
         "• Генерує РІВНО 1 аргумент",
         "argv[1] = \"a b c d e\"\n\n(Всього 1 аргумент)",
         540, 75, 460, COOL, NEG),

        ("Конструкція $@ (без лапок)",
         "Розкривається у потік слів, після чого підлягає Word Splitting за IFS\n"
         "• Пробіли всередині «a b» розривають параметр на «a» та «b»\n"
         "• Межі елементів втрачено\n"
         "• Підлягає випадковому глобінгу, якщо в тексті є * чи ?",
         "argv[1] = \"a\"\nargv[2] = \"b\"\nargv[3] = \"c\"\nargv[4] = \"d\"\nargv[5] = \"e\"\n(Всього 5 аргументів)",
         40, 295, 460, WARM, POS),

        ("Конструкція $* (без лапок)",
         "Поводиться аналогічно $@ без лапок:\n"
         "• Спершу підставляє параметри, потім ділить на слова по IFS\n"
         "• Пробіли всередині аргументів руйнують початковий масив\n"
         "• Ніколи не використовуйте для передачі аргументів!",
         "argv[1] = \"a\"\nargv[2] = \"b\"\nargv[3] = \"c\"\nargv[4] = \"d\"\nargv[5] = \"e\"\n(Всього 5 аргументів)",
         540, 295, 460, WARM, POS),
    ]

    for title, desc, res, x, y, w, bg_col, br_col in blocks:
        p.append(fitbox(x, y, w, 32, title, size=11, fill=bg_col, stroke=br_col, sw=1.8, color=INK, bold=True))
        p.append(fitbox(x, y + 36, w - 170, 140, desc, size=10, fill="#fff", stroke=br_col, sw=1.2, color=INK))
        p.append(fitbox(x + w - 160, y + 36, 160, 140, "Результат execve:\n\n" + res,
                        size=9.5, fill=bg_col, stroke=br_col, sw=1.5, color=INK, bold=True))

    render(os.path.join(OUT, "dollar-at-vs-dollar-star.svg"), W, H, *p,
           title="Порівняння розгортання векторних параметрів")


if __name__ == "__main__":
    fig_expansion_pipeline()
    fig_quoting_shields()
    fig_word_splitting_trace()
    fig_dollar_at_vs_dollar_star()
    print("All figures generated successfully.")
