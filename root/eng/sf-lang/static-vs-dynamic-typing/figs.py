# -*- coding: utf-8 -*-
import sys, os
# Path to scripts/ directory from topic directory (4 levels up)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"

def code_text(x, y, s, size=11, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── 1. Етапи перевірки типів: компіляція проти рантайму ─────────────────────────
def fig_timeline():
    W, H = 840, 430
    p = []

    # Загальний фон
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # Секція А: Статична типізація (перевірка під час компіляції)
    p.append(rect(15, 15, 810, 185, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(35, 40, "Статична типізація: верифікація до запуску (AOT)", size=13.5, color=NEG, anchor="start", bold=True))

    # Кроки статичного конвеєра
    # Крок 1: Вихідний код
    p.append(rect(35, 60, 130, 105, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(100, 80, "Вихідний код", size=11.5, color=INK, bold=True))
    p.append(code_text(45, 105, "let x: int = 5;", size=10, color=INK))
    p.append(code_text(45, 125, "let y = x + \"1\";", size=10, color=POS))
    p.append(text(100, 148, "типи у синтаксисі", size=9.5, color=MUTED))

    p.append(arrow(165, 112, 205, 112, color=LINE, sw=1.5))

    # Крок 2: Статичний верифікатор (Type Checker)
    p.append(rect(205, 55, 175, 115, fill="#eaf4fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(292, 78, "Перевірка типів", size=12, color=NEG, bold=True))
    p.append(text(292, 96, "Type Checker / AST", size=10, color=MUTED))
    p.append(line(215, 104, 370, 104, color="#bfdbfe", sw=1))
    p.append(text(292, 124, "int + string : НЕСУМІСНІ", size=9.5, color=POS, bold=True))
    p.append(text(292, 146, "Помилка компіляції!", size=10.5, color=POS, bold=True))

    p.append(arrow(380, 112, 420, 112, color=LINE, sw=1.5))

    # Крок 3: Генерація коду (Type Erasure)
    p.append(rect(420, 60, 175, 105, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(507, 80, "Генерація коду", size=11.5, color=INK, bold=True))
    p.append(text(507, 98, "Стирання типів (Erasure)", size=9.5, color=MUTED))
    p.append(code_text(435, 122, "ADD EAX, EBX", size=10, color=FIELD))
    p.append(text(507, 148, "сирі байти без тегів", size=9.5, color=MUTED))

    p.append(arrow(595, 112, 635, 112, color=LINE, sw=1.5))

    # Крок 4: Виконання процесором
    p.append(rect(635, 60, 170, 105, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(720, 82, "Цільовий процесор", size=11.5, color=FIELD, bold=True))
    p.append(text(720, 104, "Пряме виконання", size=10, color=INK))
    p.append(text(720, 124, "0 тактів на перевірки", size=9.5, color=FIELD, bold=True))
    p.append(text(720, 148, "Повний SIMD / inline", size=9.5, color=MUTED))


    # Секція Б: Динамічна типізація (перевірка під час виконання)
    p.append(rect(15, 220, 810, 195, fill="#fffbf5", stroke="#fed7aa", sw=1.5, rx=8))
    p.append(text(35, 245, "Динамічна типізація: верифікація тегів у пам'яті під час виконання", size=13.5, color=POS, anchor="start", bold=True))

    # Кроки динамічного конвеєра
    # Крок 1: Вихідний код
    p.append(rect(35, 265, 130, 135, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(100, 285, "Вихідний код", size=11.5, color=INK, bold=True))
    p.append(code_text(45, 310, "x = 5", size=10, color=INK))
    p.append(code_text(45, 330, "y = x + \"1\"", size=10, color=INK))
    p.append(text(100, 355, "змінні без типів", size=9.5, color=MUTED))
    p.append(text(100, 375, "парсер пропускає", size=9.5, color=FIELD))

    p.append(arrow(165, 330, 205, 330, color=LINE, sw=1.5))

    # Крок 2: Байткод / Інтерпретатор
    p.append(rect(205, 265, 155, 135, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(282, 285, "Байткод VM", size=11.5, color=INK, bold=True))
    p.append(code_text(215, 310, "LOAD_FAST  x", size=9.5, color=INK))
    p.append(code_text(215, 330, "LOAD_CONST '1'", size=9.5, color=INK))
    p.append(code_text(215, 350, "BINARY_ADD", size=9.5, color=POS))
    p.append(text(282, 375, "операція узагальнена", size=9.5, color=MUTED))

    p.append(arrow(360, 330, 400, 330, color=LINE, sw=1.5))

    # Крок 3: Об'єкти в купі з тегами
    p.append(rect(400, 265, 185, 135, fill="#fdf2e9", stroke=POS, sw=1.6, rx=6))
    p.append(text(492, 285, "Значення з тегами (Купа)", size=11, color=POS, bold=True))
    p.append(rect(412, 300, 160, 38, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(492, 316, "Tag: INT | Val: 5", size=9.5, color=INK))
    p.append(text(492, 330, "PyObject / Tagged Value", size=9, color=MUTED))

    p.append(rect(412, 345, 160, 38, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(492, 361, "Tag: STR | Val: '1'", size=9.5, color=INK))
    p.append(text(492, 375, "Обгортка в пам'яті (Box)", size=9, color=MUTED))

    p.append(arrow(585, 330, 625, 330, color=LINE, sw=1.5))

    # Крок 4: Перевірка тегів на кожній операції
    p.append(rect(625, 265, 180, 135, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    p.append(text(715, 285, "Runtime Tag Dispatch", size=11, color=POS, bold=True))
    p.append(text(715, 308, "if (x.tag == INT &&", size=9.5, color=INK))
    p.append(text(715, 324, "    y.tag == INT) { ... }", size=9.5, color=INK))
    p.append(line(635, 338, 795, 338, color="#fed7aa", sw=1))
    p.append(text(715, 358, "else: raise TypeError", size=10, color=POS, bold=True))
    p.append(text(715, 378, "Аварія посеред роботи", size=9.5, color=POS, italic=True))

    render(os.path.join(OUT, "type-checking-timeline.svg"), W, H, *p,
           title="Етапи перевірки типів: компіляція проти рантайму")


# ── 2. Анатомія представлення значень у динамічних мовах ────────────────────────
def fig_runtime_values():
    W, H = 840, 450
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # Заголовок та вступ
    p.append(text(W/2, 25, "Три моделі представлення динамічних значень у пам'яті", size=14, color=INK, bold=True))

    # Модель 1: Повне пакування (Boxing / PyObject)
    p.append(rect(20, 50, 250, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(145, 75, "1. Класичне пакування", size=12.5, color=NEG, bold=True))
    p.append(text(145, 93, "Boxed Object (Python, Java)", size=10, color=MUTED))
    p.append(line(35, 103, 255, 103, color="#cbd5e1", sw=1))

    # Стек: покажчик
    p.append(rect(40, 115, 210, 45, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(145, 134, "Стек: Покажчик (8 байтів)", size=10, color=NEG, bold=True))
    p.append(code_text(145, 150, "0x7FFF_DEAD_BEE0", size=9.5, color=INK, anchor="middle"))

    p.append(arrow(145, 160, 145, 185, color=NEG, sw=1.8))

    # Купа: заголовок об'єкта
    p.append(rect(40, 185, 210, 175, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(45, 192, 200, 38, fill="#eaf4fd", stroke="#bfdbfe", sw=1, rx=4))
    p.append(text(145, 208, "Refcount (8 байтів)", size=9.5, color=INK))
    p.append(text(145, 222, "лічильник посилань GC", size=9, color=MUTED))

    p.append(rect(45, 236, 200, 38, fill="#eaf4fd", stroke="#bfdbfe", sw=1, rx=4))
    p.append(text(145, 252, "Type Pointer (8 байтів)", size=9.5, color=NEG, bold=True))
    p.append(text(145, 266, "покажчик на PyTypeObject", size=9, color=MUTED))

    p.append(rect(45, 280, 200, 38, fill="#fdf2e9", stroke="#fed7aa", sw=1, rx=4))
    p.append(text(145, 296, "Payload (8–24 байти)", size=9.5, color=POS, bold=True))
    p.append(text(145, 310, "саме корисне значення", size=9, color=MUTED))

    p.append(rect(45, 324, 200, 28, fill="#f1f5f9", stroke="#e2e8f0", sw=1, rx=3))
    p.append(text(145, 342, "Разом: 24–32 байти на число!", size=9.5, color=POS, bold=True))

    p.append(text(145, 380, "Витрати: алокація в купі,", size=9.5, color=MUTED))
    p.append(text(145, 398, "розіменування, промахи L1", size=9.5, color=MUTED))
    p.append(text(145, 418, "Ціна числа: 400% пам'яті", size=9.5, color=POS, bold=True))


    # Модель 2: Теговані покажчики (Tagged Pointers)
    p.append(rect(295, 50, 250, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(420, 75, "2. Теговані покажчики", size=12.5, color=NEG, bold=True))
    p.append(text(420, 93, "Tagged Pointer (OCaml, Ruby)", size=10, color=MUTED))
    p.append(line(310, 103, 530, 103, color="#cbd5e1", sw=1))

    # Схема 64-бітного слова
    p.append(rect(310, 115, 220, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(420, 133, "64-бітне машинне слово (8B)", size=10, color=INK, bold=True))

    # Поділ на payload і tag біти
    p.append(rect(316, 145, 155, 24, fill="#eaf4fd", stroke="#bfdbfe", sw=1, rx=3))
    p.append(text(393, 161, "61-63 біти: Payload", size=9.5, color=NEG, bold=True))

    p.append(rect(474, 145, 50, 24, fill="#fef2f2", stroke="#fecaca", sw=1, rx=3))
    p.append(text(499, 161, "Tag", size=9.5, color=POS, bold=True))

    # Пояснення тегів
    p.append(rect(310, 185, 220, 135, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(420, 203, "Тег у молодших бітах (вирівнювання 8B):", size=9, color=MUTED))
    p.append(code_text(320, 225, "...000 : Heap Pointer", size=9.5, color=NEG))
    p.append(code_text(320, 245, "...001 : Fixnum (Int)", size=9.5, color=FIELD))
    p.append(code_text(320, 265, "...010 : Boolean (true/false)", size=9.5, color=INK))
    p.append(code_text(320, 285, "...011 : Symbol / Nil", size=9.5, color=MUTED))
    p.append(text(420, 308, "Int розпаковується через: val >> 1", size=9, color=FIELD, italic=True))

    p.append(text(420, 355, "Переваги: без купи для цілих,", size=9.5, color=MUTED))
    p.append(text(420, 375, "розмір рівно 8 байтів.", size=9.5, color=MUTED))
    p.append(text(420, 398, "Обмеження: цілі втрачають", size=9.5, color=MUTED))
    p.append(text(420, 418, "1–3 біти діапазону (61-біт)", size=9.5, color=POS, bold=True))


    # Модель 3: NaN-Boxing
    p.append(rect(570, 50, 250, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(695, 75, "3. NaN-Boxing", size=12.5, color=NEG, bold=True))
    p.append(text(695, 93, "IEEE 754 (JS V8/JSC, LuaJIT)", size=10, color=MUTED))
    p.append(line(585, 103, 805, 103, color="#cbd5e1", sw=1))

    # Схема 64-бітного IEEE 754
    p.append(rect(585, 115, 220, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(695, 133, "64-бітний Double / Tagged Value", size=10, color=INK, bold=True))

    # Біти NaN-box
    p.append(rect(590, 145, 75, 24, fill="#fef2f2", stroke="#fecaca", sw=1, rx=3))
    p.append(text(627, 161, "0x7FF8 (NaN)", size=9, color=POS, bold=True))

    p.append(rect(668, 145, 42, 24, fill="#fef3c7", stroke="#fde68a", sw=1, rx=3))
    p.append(text(689, 161, "Tag", size=9, color="#b45309", bold=True))

    p.append(rect(713, 145, 87, 24, fill="#eaf4fd", stroke="#bfdbfe", sw=1, rx=3))
    p.append(text(756, 161, "48-bit Ptr/Int", size=9, color=NEG, bold=True))

    # Пояснення семантики
    p.append(rect(585, 185, 220, 135, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(695, 203, "Семантика бітів NaN:", size=9.5, color=MUTED))
    p.append(text(695, 223, "• Якщо НЕ NaN -> число double", size=9, color=FIELD))
    p.append(text(695, 242, "• Якщо Quiet NaN + Tag 0 -> Покажчик", size=9, color=NEG))
    p.append(text(695, 261, "• Якщо Quiet NaN + Tag 1 -> 32-bit Int", size=9, color=INK))
    p.append(text(695, 280, "• Якщо Quiet NaN + Tag 2 -> Boolean", size=9, color=MUTED))
    p.append(text(695, 305, "48 бітів вміщують покажчик x86-64", size=9, color=NEG, italic=True))

    p.append(text(695, 355, "Переваги: арифметика double", size=9.5, color=MUTED))
    p.append(text(695, 375, "без розпакування, 8 байтів,", size=9.5, color=MUTED))
    p.append(text(695, 398, "найшвидший динамічний рушій", size=9.5, color=FIELD, bold=True))
    p.append(text(695, 418, "Ідеал для JS та Lua VM", size=9.5, color=NEG, bold=True))

    render(os.path.join(OUT, "runtime-value-representations.svg"), W, H, *p,
           title="Анатомія представлення значень у динамічних мовах")


# ── 3. Ортогональна матриця типізації (2x2) ───────────────────────────────────
def fig_typing_matrix():
    W, H = 840, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # Головна рамка координат
    p.append(text(W/2, 25, "Матриця класифікації систем типів: час перевірки проти строгості", size=14, color=INK, bold=True))

    # Підписи осей
    p.append(rect(80, 50, 350, 30, fill="#eaf4fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(255, 70, "Статична (перевірка під час компіляції)", size=12, color=NEG, bold=True))

    p.append(rect(450, 50, 350, 30, fill="#fffbf5", stroke=POS, sw=1.5, rx=6))
    p.append(text(625, 70, "Динамічна (перевірка під час виконання)", size=12, color=POS, bold=True))

    # Вісь Y: Сильна типізація
    p.append(rect(15, 90, 55, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(42, 170, "СИЛЬНА", size=12, color=FIELD, bold=True))
    p.append(text(42, 190, "Strict / Safe", size=9.5, color=MUTED))

    # Вісь Y: Слабка типізація
    p.append(rect(15, 280, 55, 175, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(42, 360, "СЛАБКА", size=12, color="#ef4444", bold=True))
    p.append(text(42, 380, "Coercive", size=9.5, color=MUTED))

    # Квадрант 1: Статична + Сильна
    p.append(rect(80, 90, 350, 175, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(255, 112, "Статична + Сильна (Strong Static)", size=12.5, color=FIELD, bold=True))
    p.append(text(255, 128, "Повна безпека типів ще до запуску бінарника", size=9.5, color=MUTED))
    p.append(line(95, 136, 415, 136, color="#cbd5e1", sw=1))
    p.append(text(255, 154, "Мови: Rust, Haskell, Swift, Ada, Scala, Java, Go", size=10.5, color=INK, bold=True))
    p.append(text(255, 174, "• Заборона неявних коерсій («\"5\" + 2» — помилка компілятора)", size=9.5, color=INK))
    p.append(text(255, 192, "• Перевірка безпеки пам'яті (Soundness / Memory Safety)", size=9.5, color=INK))
    p.append(text(255, 210, "• Нульові накладні витрати під час виконання (Zero Overhead)", size=9.5, color=FIELD))
    p.append(text(255, 230, "• Максимальний захист від багів у продакшені", size=9.5, color=FIELD, bold=True))

    # Квадрант 2: Динамічна + Сильна
    p.append(rect(450, 90, 350, 175, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(625, 112, "Динамічна + Сильна (Strong Dynamic)", size=12.5, color=NEG, bold=True))
    p.append(text(625, 128, "Суворі типи, але зв'язані зі значеннями в купі", size=9.5, color=MUTED))
    p.append(line(465, 136, 785, 136, color="#cbd5e1", sw=1))
    p.append(text(625, 154, "Мови: Python, Ruby, Erlang, Elixir, Clojure, Smalltalk", size=10.5, color=INK, bold=True))
    p.append(text(625, 174, "• Неявні перетворення заборонені («\"5\" + 2» кидає TypeError)", size=9.5, color=INK))
    p.append(text(625, 192, "• Змінна може змінювати тип під час виконання: x = 1; x = \"abc\"", size=9.5, color=INK))
    p.append(text(625, 210, "• Помилка типизації виявляється лише на активній гілці коду", size=9.5, color=POS))
    p.append(text(625, 230, "• Потребує суцільного покриття модульними тестами", size=9.5, color=POS, bold=True))

    # Квадрант 3: Статична + Слабка
    p.append(rect(80, 280, 350, 175, fill="#ffffff", stroke="#f59e0b", sw=1.8, rx=8))
    p.append(text(255, 302, "Статична + Слабка (Weak Static)", size=12.5, color="#b45309", bold=True))
    p.append(text(255, 318, "Типи відомі компілятору, але їх можна обійти", size=9.5, color=MUTED))
    p.append(line(95, 326, 415, 326, color="#cbd5e1", sw=1))
    p.append(text(255, 344, "Мови: C, C++ (низькорівневі зрізи), Assembler", size=10.5, color=INK, bold=True))
    p.append(text(255, 364, "• Дозволені небезпечні приведення: (void*), reinterpret_cast", size=9.5, color=INK))
    p.append(text(255, 382, "• Пряма арифметика покажчиків і підміна бітів у пам'яті", size=9.5, color=INK))
    p.append(text(255, 400, "• Неявні зрізання та просування цілих: int + double, signed/unsigned", size=9.5, color=POS))
    p.append(text(255, 420, "• Ризик невизначеної поведінки (UB) та дірок у безпеці", size=9.5, color=POS, bold=True))

    # Квадрант 4: Динамічна + Слабка
    p.append(rect(450, 280, 350, 175, fill="#ffffff", stroke="#ef4444", sw=1.8, rx=8))
    p.append(text(625, 302, "Динамічна + Слабка (Weak Dynamic)", size=12.5, color="#dc2626", bold=True))
    p.append(text(625, 318, "Неявне агресивне приведення типів під час виконання", size=9.5, color=MUTED))
    p.append(line(465, 326, 785, 326, color="#cbd5e1", sw=1))
    p.append(text(625, 344, "Мови: JavaScript, PHP (класичний), Perl, Bash", size=10.5, color=INK, bold=True))
    p.append(text(625, 364, "• Агресивна коерсія: «\"5\" - 2 == 3», але «\"5\" + 2 == \"52\"»", size=9.5, color=INK))
    p.append(text(625, 382, "• Складання об'єктів: «[] + {} == \"[object Object]\"»", size=9.5, color=INK))
    p.append(text(625, 400, "• Рідко падає з TypeError — замість цього тихо спотворює стан", size=9.5, color=POS))
    p.append(text(625, 420, "• Найбільш підступні логічні дефекти на продакшені", size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "typing-matrix.svg"), W, H, *p,
           title="Ортогональна матриця типізації")


# ── 4. Механізм Inline Caching (IC) у динамічних віртуальних машинах ──────────
def fig_inline_caching():
    W, H = 840, 410
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    p.append(text(W/2, 25, "Прискорення динамічного доступу: Вбудоване кешування (Inline Caching)", size=14, color=INK, bold=True))

    # Точка виклику у байткоді
    p.append(rect(30, 55, 180, 75, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(120, 78, "Місце виклику (Call Site)", size=11, color=INK, bold=True))
    p.append(code_text(50, 100, "point.get_x()", size=11, color=NEG))
    p.append(text(120, 118, "Змінний тип об'єкта point", size=9.5, color=MUTED))

    p.append(arrow(210, 92, 260, 92, color=LINE, sw=1.5))

    # Рівень 1: Мономорфний кеш (Monomorphic IC) - Найшвидший шлях
    p.append(rect(260, 50, 240, 90, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(380, 72, "1. Мономорфний кеш (Fast Path)", size=11.5, color=FIELD, bold=True))
    p.append(text(380, 90, "Порівняння: obj.shape == Shape_A", size=9.5, color=INK))
    p.append(line(275, 98, 485, 98, color="#bbf7d0", sw=1))
    p.append(text(380, 114, "СПІВПАДІННЯ (95% викликів):", size=9.5, color=FIELD, bold=True))
    p.append(text(380, 130, "Прямий стрибок за адресою без словника", size=9, color=INK))

    p.append(arrow(500, 92, 570, 92, color=FIELD, sw=1.8))

    # Виконання функції за мономорфним шляхом
    p.append(rect(570, 55, 240, 75, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(690, 78, "Прямий виклик коду", size=11, color=FIELD, bold=True))
    p.append(code_text(585, 100, "CALL 0x7FFF_0040_1020", size=10, color=FIELD))
    p.append(text(690, 118, "Швидкість майже як у C/C++ (1 такт)", size=9.5, color=FIELD, bold=True))

    # Стрілка промаху мономорфного кешу вниз
    p.append(arrow(380, 140, 380, 175, color=POS, sw=1.5))
    p.append(text(395, 162, "Промах", size=9.5, color=POS, anchor="start", bold=True))

    # Рівень 2: Поліморфний кеш (Polymorphic IC)
    p.append(rect(260, 175, 240, 100, fill="#fffbf5", stroke="#f59e0b", sw=1.6, rx=8))
    p.append(text(380, 197, "2. Поліморфний кеш (2–4 типи)", size=11, color="#b45309", bold=True))
    p.append(text(380, 214, "Таблиця пар: (Shape_B, fn_B),", size=9.5, color=INK))
    p.append(text(380, 228, "(Shape_C, fn_C), (Shape_D, fn_D)", size=9.5, color=INK))
    p.append(line(275, 236, 485, 236, color="#fde68a", sw=1))
    p.append(text(380, 252, "Лінійний пошук серед 4 записів", size=9, color=MUTED))
    p.append(text(380, 266, "Затримка: 4–10 тактів CPU", size=9, color="#b45309", bold=True))

    # Стрілка успіху поліморфного кешу
    p.append(arrow(500, 225, 570, 225, color="#f59e0b", sw=1.5))
    p.append(rect(570, 190, 240, 70, fill="#ffffff", stroke="#f59e0b", sw=1.5, rx=6))
    p.append(text(690, 212, "Непрямий виклик з таблиці", size=10.5, color="#b45309", bold=True))
    p.append(code_text(585, 232, "CALL [table + rdx*8]", size=10, color=INK))
    p.append(text(690, 248, "Помірні накладні витрати", size=9, color=MUTED))

    # Стрілка переповнення вниз до мегаморфного
    p.append(arrow(380, 275, 380, 305, color=POS, sw=1.5))
    p.append(text(395, 293, ">4 типів", size=9.5, color=POS, anchor="start", bold=True))

    # Рівень 3: Мегаморфний стан (Megamorphic Stub) - Найповільніший
    p.append(rect(260, 305, 550, 80, fill="#fef2f2", stroke="#ef4444", sw=1.6, rx=8))
    p.append(text(535, 325, "3. Мегаморфний пошук (Повний провал кешування / Slow Path)", size=11.5, color="#dc2626", bold=True))
    p.append(text(535, 345, "Глобальний хеш-пошук у словнику властивостей об'єкта або ланцюжку прототипів", size=9.5, color=INK))
    p.append(text(535, 365, "Накладні витрати: 50–200 тактів, скидання конвеєра, навантаження GC", size=9.5, color="#dc2626", bold=True))

    render(os.path.join(OUT, "inline-caching-flow.svg"), W, H, *p,
           title="Механізм Inline Caching (IC) у динамічних віртуальних машинах")


def main():
    fig_timeline()
    fig_runtime_values()
    fig_typing_matrix()
    fig_inline_caching()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
