# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Конвеєр виконання команди та точки вклинення діагностики ─────────────
def fig_shell_execution_and_trace_pipeline():
    W, H = 1200, 840
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Конвеєр обробки інструкції інтерпретатором Bash: від сирого тексту до "
                    "системного виклику й точок вклинення діагностики",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    steps = [
        ("1. Читання та синтаксичний аналіз",
         "Парсинг тексту, побудова граматичного дерева команд\n"
         "Тут діє bash -n (noexec): зупиняє конвеєр без виконання",
         WARM_FILL, WARM),
        ("2. Розгортання (Expansions)",
         "Розкриття дужок {}, параметрів $VAR, підстановка команд $(...),\n"
         "арифметика $((...)), поділ на слова IFS та розгортання масок *",
         BLUE_FILL, NEG),
        ("3. Точка перехоплення trap '...' DEBUG",
         "Виконується ПЕРЕД викликом команди. Змінна $BASH_COMMAND\n"
         "містить текст наступної інструкції до виконання",
         GREEN_FILL, FIELD),
        ("4. Трасування xtrace (set -x)",
         "Розгортання префіксу PS4 (час, файл, рядок, функція) та вивід\n"
         "повного розгорнутого вектора команди в stderr або BASH_XTRACEFD",
         WARM_FILL, WARM),
        ("5. Виконання команди",
         "Вбудована функція/builtin або виклик ядрового fork() + execve().\n"
         "Формування кінцевого коду завершення $? (0..255)",
         FILL, LINE),
        ("6. Точка перехоплення trap '...' ERR",
         "Спрацьовує автоматично при $? != 0 (якщо не в умовах if/while/||).\n"
         "Дозволяє надрукувати стек викликів та аварійний стан",
         RED_FILL, POS),
    ]

    y = 115
    RH, GAP = 86, 26
    BX, BW = 70, 1060

    for i, (title, desc, fill, stroke) in enumerate(steps):
        p.append(fitbox(BX, y, 340, RH, title, size=14, fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(BX + 355, y, BW - 355, RH, desc, size=13, fill=BG, stroke=MUTED))
        if i < len(steps) - 1:
            p.append(arrow(BX + BW / 2, y + RH + 3, BX + BW / 2, y + RH + GAP - 3, color=MUTED))
        y += RH + GAP

    p.append(fitbox(50, 755, 1100, 52,
                    "Прапорці set -T (functrace) та set -E (errtrace) змушують пастки DEBUG та ERR "
                    "успадковуватися функціями та підоболонками",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'shell-execution-and-trace-pipeline.svg'), W, H, *p,
           title="Конвеєр інтерпретації команди та точки діагностики")


# ── 2. Стекові масиви Bash при аварійній зупинці ──────────────────────────────
def fig_bash_call_stack_arrays():
    W, H = 1200, 780
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Інтроспекція стека викликів у Bash: паралельні масиви середовища "
                    "та реконструкція бектрейсу при збої",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    COLS = [(60, 140), (220, 260), (500, 260), (780, 180), (980, 180)]
    headers = [
        ("Індекс", FILL, LINE),
        ("FUNCNAME[i]", BLUE_FILL, NEG),
        ("BASH_SOURCE[i+1]", GREEN_FILL, FIELD),
        ("BASH_LINENO[i]", WARM_FILL, WARM),
        ("Роль у виклику", FILL, LINE),
    ]

    HY = 115
    for (cx, cw), (htitle, hfill, hstroke) in zip(COLS, headers):
        p.append(fitbox(cx, HY, cw, 42, htitle, size=13, fill=hfill, stroke=hstroke, bold=True))

    rows = [
        ("0", "db_query", "services.sh", "42", "Місце збою (поточна функція)", RED_FILL, POS),
        ("1", "sync_users", "worker.sh", "118", "Функція, що викликала db_query", WARM_FILL, WARM),
        ("2", "process_queue", "main.sh", "85", "Функція верхнього рівня", BG, MUTED),
        ("3", "main", "main.sh", "14", "Точка входу в скрипт", BG, MUTED),
    ]

    y = 168
    RH, GAP = 58, 12
    for idx, fn, src, line, role, fill, stroke in rows:
        p.append(fitbox(COLS[0][0], y, COLS[0][1], RH, idx, size=13, fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(COLS[1][0], y, COLS[1][1], RH, fn + "()", size=13, fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(COLS[2][0], y, COLS[2][1], RH, src, size=13, fill=BG, stroke=MUTED))
        p.append(fitbox(COLS[3][0], y, COLS[3][1], RH, "рядок " + line, size=13, fill=BG, stroke=MUTED))
        p.append(fitbox(COLS[4][0], y, COLS[4][1], RH, role, size=12, fill=BG, stroke=MUTED))
        y += RH + GAP

    p.append(fitbox(60, 465, 1100, 120,
                    "Правило адресації виклику в Bash:\n"
                    "• FUNCNAME[0] — поточна активна функція, де виникла подія;\n"
                    "• BASH_SOURCE[1] та BASH_LINENO[0] — файл і номер рядка, ЗВІДКИ її викликали;\n"
                    "• Змінна BASH_COMMAND містить сирий текст команди, яка зазнала невдачі ($? != 0).",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    p.append(fitbox(60, 605, 1100, 135,
                    "Формування текстового бектрейсу в обробнику trap '...' ERR:\n"
                    "for ((i=1; i<${#FUNCNAME[@]}; i++)); do\n"
                    "    caller_func=\"${FUNCNAME[$i]}\"\n"
                    "    caller_file=\"${BASH_SOURCE[$i]}\"\n"
                    "    caller_line=\"${BASH_LINENO[$((i-1))]}\"\n"
                    "    echo \"  at ${caller_func}() [${caller_file}:${caller_line}]\"\n"
                    "done",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'bash-call-stack-arrays.svg'), W, H, *p,
           title="Стекові масиви та реконструкція бектрейсу в Bash")


# ── 3. Архітектура аналізу AST інструментом ShellCheck ───────────────────────
def fig_shellcheck_ast_analysis():
    W, H = 1200, 780
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Статичний аналіз ShellCheck: перетворення сценарію на абстрактне синтаксичне "
                    "дерево та виявлення типових пасток",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # Схема зліва: етапи роботи ShellCheck
    p.append(fitbox(60, 115, 330, 70,
                    "Вихідний скрипт\n.sh / .bash",
                    size=14, fill=FILL, stroke=LINE, bold=True))
    p.append(arrow(225, 190, 225, 230, color=MUTED))

    p.append(fitbox(60, 235, 330, 90,
                    "Лексичний і синтаксичний аналізатор\n"
                    "Побудова AST з урахуванням діалекту\n"
                    "(sh, bash, dash, ksh)",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(225, 330, 225, 370, color=MUTED))

    p.append(fitbox(60, 375, 330, 110,
                    "Аналізатор контекстів і потоків\n"
                    "Перевірка розщеплення слів, масок,\n"
                    "маскування статусів, помилок синтаксису\n"
                    "та переносимості",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(arrow(225, 490, 225, 530, color=MUTED))

    p.append(fitbox(60, 535, 330, 90,
                    "Генератор звітів\n"
                    "Діагностика: помилка, попередження,\n"
                    "інформація, автофікс у форматі diff",
                    size=13, fill=WARM_FILL, stroke=WARM))

    # Справа: типові правила ShellCheck
    rules = [
        ("SC2086: Unquoted Variable",
         "rm -rf $DIR  →  rm -rf \"$DIR\"\n"
         "Запобігання розбиттю слів та розгортанню масок у шляхах із пробілами",
         RED_FILL, POS),
        ("SC2046: Unquoted Command Expansion",
         "for f in $(find .)  →  while IFS= read -r f; do ...\n"
         "Підстановка команди розщеплюється за символами IFS",
         WARM_FILL, WARM),
        ("SC2155: Masked Return Value",
         "local x=$(failing_cmd)  →  local x; x=$(failing_cmd)\n"
         "Оголошення local маскує ненульовий код повернення команди",
         RED_FILL, POS),
        ("SC2168: Invalid Local Scope",
         "local my_var=1 на рівні файлу поза функцією викликає помилку виконання",
         BLUE_FILL, NEG),
    ]

    RY = 115
    RH, GAP = 120, 16
    for code, desc, fill, stroke in rules:
        p.append(fitbox(430, RY, 730, RH,
                        code + "\n\n" + desc,
                        size=13, fill=fill, stroke=stroke, bold=True))
        RY += RH + GAP

    p.append(fitbox(60, 665, 1100, 75,
                    "Інтеграція в CI: `shellcheck -f gcc scripts/*.sh` повертає ненульовий код виходу "
                    "при виявленні дефектів, блокуючи злиття небезпечного коду до запуску тестів",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'shellcheck-ast-analysis.svg'), W, H, *p,
           title="Статичний аналіз сценаріїв через ShellCheck")


fig_shell_execution_and_trace_pipeline()
fig_bash_call_stack_arrays()
fig_shellcheck_ast_analysis()
print("ok")
