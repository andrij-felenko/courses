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


# ── 1. Еволюція конвеєра: від плаского байтового потоку до дерев і ndjson ─────
def fig_pipeline_evolution():
    W, H = 1200, 680
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Еволюція конвеєра: байтовий потік символів проти структурованих дерев та ndjson",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Секція 1: Класичний Unix-конвеєр (1D рядки)
    p.append(fitbox(50, 115, 520, 42,
                    "Класичний потік: роздільник 0x0A (LF), пласкі рядки",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    rows_classic = [
        "access.log  →  192.0.2.1 - GET /api/v1/user HTTP/1.1  200 142",
        "grep /api   →  знаходить підрядок байтів без розуміння меж полів",
        "cut -d' '   →  ламається, якщо поле містить пробіл або екранування",
        "awk '{print}' → не бачить вкладених списків, об'єктів і переносів рядків"
    ]
    y = 170
    for r in rows_classic:
        p.append(fitbox(50, y, 520, 44, r, size=11, fill=BG, stroke=MUTED))
        y += 50

    p.append(fitbox(50, 380, 520, 60,
                    "Обмеження: модель не має типів, вимагає однозначного "
                    "символьного роздільника й ламається на вкладених структурах",
                    size=12, fill=RED_FILL, stroke=POS))

    # Секція 2: Сучасний структурований потік (JSON, ndjson, CSV)
    p.append(fitbox(630, 115, 520, 42,
                    "Сучасний потік: ndjson / типізовані дерева на каналі",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    rows_modern = [
        '{"ip":"192.0.2.1","req":{"path":"/api/v1"},"status":200,"tags":["prod"]}',
        'jq \'.req.path\' → синтаксичний розбір дерева, збереження типів',
        'yq -o=json      → трансляція YAML <-> JSON зі збереженням структури',
        'xsv select 1,3  → розбір CSV за RFC 4180 з урахуванням лапок і ком'
    ]
    y = 170
    for r in rows_modern:
        p.append(fitbox(630, y, 520, 44, r, size=11, fill=BG, stroke=MUTED))
        y += 50

    p.append(fitbox(630, 380, 520, 60,
                    "Перевага: кожен рядок є ізольованим синтаксичним деревом, "
                    "зберігає вкладеність, типи даних та обробляється в O(1) пам'яті",
                    size=12, fill=BLUE_FILL, stroke=NEG))

    # Спільний підсумок унизу
    p.append(fitbox(50, 470, 1100, 160,
                    "Канал ядра (pipe) незмінний: це байтова труба без типів із буфером 64 КіБ (F_SETPIPE_SZ).\n"
                    "Змінюється контракт обробників: замість примітивного сканування до байта 0x0A утиліти запускають\n"
                    "потокові автомати (FSM), які розпізнають дужки, лапки, escape-послідовності та кодування UTF-8.\n"
                    "Формат ndjson повертає паралелізм: кожен рядок є валідним JSON, потік не накопичує DOM у пам'яті.",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'pipeline-evolution.svg'), W, H, *p, title="Еволюція конвеєра: від рядків до дерев")


# ── 2. Модель виконання jq: функціональний потік 0..N результатів ─────────────
def fig_jq_execution_model():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 30, 1100, 56,
                    "Функціональна модель jq: генератор потоку від одного входу до 0..N виходів",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Вхідний об'єкт
    p.append(fitbox(50, 110, 280, 240,
                    "Вхідний JSON (Input)\n\n"
                    "{\n"
                    '  "service": "auth",\n'
                    '  "events": [\n'
                    '    {"id":1, "ok":true},\n'
                    '    {"id":2, "ok":false},\n'
                    '    {"id":3, "ok":true}\n'
                    "  ]\n"
                    "}",
                    size=12, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(340, 230, 420, 230, color=MUTED))

    # Ланцюг фільтрів jq
    p.append(fitbox(430, 110, 360, 420,
                    "Ланцюг трансформацій jq\n\n"
                    ".events[]\n"
                    "↓ розгортання масиву в потік (3 об'єкти)\n\n"
                    "select(.ok == false)\n"
                    "↓ фільтрація: відкидає ok:true (0..1 вихід)\n\n"
                    "{ failed_id: .id }\n"
                    "↓ проєкція: створення нового об'єкта",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    p.append(arrow(800, 230, 880, 230, color=MUTED))

    # Вихідний потік
    p.append(fitbox(890, 110, 260, 240,
                    "Вихідний потік (Output)\n\n"
                    "{\n"
                    '  "failed_id": 2\n'
                    "}\n\n"
                    "Результат: рівно один\n"
                    "відфільтрований запис",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Пояснення режимів роботи знизу
    p.append(fitbox(50, 450, 360, 220,
                    "Режим потоку: O(1) RAM\n\n"
                    "jq '.[] | select(...)' stream.jsonl\n\n"
                    "Кожен JSON-об'єкт читається,\n"
                    "трансформується й негайно записується\n"
                    "в stdout. Пам'ять стабільна\n"
                    "навіть для гігабайтних потоків.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(430, 550, 360, 120,
                    "Пастка -s (--slurp): O(N) RAM\n\n"
                    "Вичитує весь вхідний потік у спільний масив.\n"
                    "Ламає потоковість і вичерпує оперативну пам'ять.",
                    size=12, fill=RED_FILL, stroke=POS))

    p.append(fitbox(810, 450, 340, 220,
                    "Форматування виводу\n\n"
                    "• -r (--raw-output): відкидає лапки\n"
                    "  для передачі утилітам POSIX;\n"
                    "• -c (--compact-output): генерує\n"
                    "  чистий ndjson по одному рядку;\n"
                    "• -n: стартує з null без stdin.",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'jq-execution-model.svg'), W, H, *p, title="Модель виконання фільтрів jq")


# ── 3. Архітектура індексації CSV у xsv: довільний доступ до гігабайтних даних ─
def fig_xsv_index_seek():
    W, H = 1200, 700
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Індексація великих CSV-файлів у xsv: від лінійного O(N) сканування до O(1) seek",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Ліва колонка: Великий файл CSV
    p.append(fitbox(50, 120, 480, 280,
                    "Файл даних: data.csv (10 Гб, 50 000 000 рядків)\n\n"
                    "Byte 0       : id,timestamp,user,payload\n"
                    "Byte 1048    : 1,2026-08-25T10:00:00Z,hanna,\"ok\"\n"
                    "...\n"
                    "Byte 5242880 : 1000000,2026-08-25T12:00:00Z,dmytro,\"error\"\n"
                    "...\n"
                    "Byte 10737418240: кінець файлу",
                    size=12, fill=BLUE_FILL, stroke=NEG))

    # Права колонка: Індексний файл .csv.idx
    p.append(fitbox(590, 120, 560, 280,
                    "Індексний файл: data.csv.idx (бінарна таблиця зміщень)\n\n"
                    "Header: сигнатура xsv + лічильник рядків (50M)\n"
                    "Row 0       → Offset: 0\n"
                    "Row 1 000 000 → Offset: 5242880\n"
                    "Row 2 000 000 → Offset: 10485760\n"
                    "...\n"
                    "Розмір індексу: ~400 Мб (сталі 8 байтів на запис)",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Стрілка між ними
    p.append(arrow(535, 260, 585, 260, color=MUTED))

    # Нижні блоки: Лінійний доступ vs Індексний зріз
    p.append(fitbox(50, 430, 480, 220,
                    "Без індексу: xsv slice -i 1000000 -l 10\n\n"
                    "1. Читає всі байти від 0 до 5 242 880;\n"
                    "2. Парсить 1 000 000 рядків послідовно;\n"
                    "3. Час виконання: ~15-30 секунд;\n"
                    "4. Високе навантаження на диск і CPU.",
                    size=12, fill=RED_FILL, stroke=POS))

    p.append(fitbox(590, 430, 560, 220,
                    "З індексом (xsv index): миттєвий lseek(2)\n\n"
                    "1. Зчитує зміщення для рядка 1 000 000 з .csv.idx;\n"
                    "2. Викликає lseek(fd, 5242880, SEEK_SET) і pread(2);\n"
                    "3. Читає лише потрібні 10 рядків (~1 КіБ даних);\n"
                    "4. Час виконання: < 1 мілісекунди (O(1)).",
                    size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, 'xsv-index-seek.svg'), W, H, *p, title="Індексація та довільний доступ у xsv")


# ── 4. Анатомія ін'єкції в конвеєрах: конкатенація рядків проти --arg ─────────
def fig_injection_vs_param():
    W, H = 1200, 700
    p = []

    p.append(fitbox(50, 35, 1100, 56,
                    "Безпека в конвеєрах: руйнування AST при конкатенації рядків проти строгої параметризації",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Ліва половина: Вразливість (Інтерполяція оболонки)
    p.append(fitbox(50, 115, 520, 50,
                    "Небезпечно: інтерполяція змінних оболонки в jq-вираз",
                    size=13, fill=RED_FILL, stroke=POS, bold=True))

    p.append(fitbox(50, 180, 520, 180,
                    'Вхідні дані від користувача:\n'
                    'USER_INPUT=\'admin") | .secret // ("\'\n\n'
                    'Команда зі склеюванням рядків:\n'
                    'jq ".users[] | select(.name == \\"$USER_INPUT\\")"\n\n'
                    'Сформований вираз після підстановки в bash:\n'
                    'jq \'.users[] | select(.name == "admin") | .secret // ("")\'',
                    size=11, fill=BG, stroke=MUTED))

    p.append(fitbox(50, 375, 520, 95,
                    "Наслідок: синтаксичний розрив (AST Injection).\n"
                    "Рядковий літерал закривається передчасно, вставляється новий\n"
                    "фільтр .secret, який витікає паролі або обходить авторизацію.",
                    size=12, fill=RED_FILL, stroke=POS))

    # Права половина: Безпечний підхід (Параметризація через --arg)
    p.append(fitbox(630, 115, 520, 50,
                    "Безпечно: параметризовані аргументи --arg / --argjson",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(630, 180, 520, 180,
                    'Вхідні дані від користувача:\n'
                    'USER_INPUT=\'admin") | .secret // ("\'\n\n'
                    'Команда з параметризацією:\n'
                    'jq --arg name "$USER_INPUT" \\\n'
                    '   \'.users[] | select(.name == $name)\'\n\n'
                    'Синтаксичне дерево:\n'
                    'AST зафіксовано. $name передається як літеральне значення.',
                    size=11, fill=BG, stroke=MUTED))

    p.append(fitbox(630, 375, 520, 95,
                    "Результат: абсолютний захист від ін'єкцій.\n"
                    "Спеціальні символи (\", |, //) інтерпретуються як звичайні\n"
                    "байти імені, синтаксична структура програми лишається непорушною.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Нижній блок: Матриця параметризації
    p.append(fitbox(50, 490, 1100, 160,
                    "Матриця безпечної передачі параметрів у конвеєрних утилітах:\n\n"
                    "• jq --arg k \"$v\" : передає рядок; --argjson k \"$json\" : типізований JSON (число, bool, об'єкт);\n"
                    "• jq --rawfile k path : вичитує файл як строгий рядок без інтерполяції;\n"
                    "• xmlstarlet sel --var k=\"$v\" : передає значення у вираз XPath без конкатенації рядків;\n"
                    "• xsv search -s col \"$pattern\" : передає регулярний вираз як окремий аргумент argv.",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'injection-vs-param.svg'), W, H, *p, title="Запобігання ін'єкціям у конвеєрах структурованих даних")


if __name__ == '__main__':
    fig_pipeline_evolution()
    fig_jq_execution_model()
    fig_xsv_index_seek()
    fig_injection_vs_param()
    print("All figures generated successfully.")
