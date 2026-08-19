# -*- coding: utf-8 -*-
"""Фігури до теми «Статична рефлексія C++26: оператор ^^, splice і consteval-метафункції»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK,
            lh=1.5, dash=None, anchor="middle"):
    """Рамка з кількома моноширинними рядками."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)
    if dash:
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
               'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
               % (x, y, w, h, fill, stroke, sw, dash))
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * lh / 2 + size * 0.35
    px = x + w / 2 if anchor == "middle" else x + 16
    for i, ln in enumerate(lines):
        out += mono(px, cy + i * size * lh, ln, size=size, color=color, anchor=anchor)
    return out


# ── 1. Життєвий цикл рефлексії: підйом (^^), обробка (consteval) і сплайсинг ([: :]) ─
def fig_reflection_pipeline():
    W, H = 1120, 480
    p = []

    # Три головні зони
    # 1. Початковий синтаксис / AST
    p.append(rect(40, 70, 290, 320, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(185, 102, "1. Простір коду (AST)", size=14, bold=True, color=INK))
    p.append(monobox(55, 126, 260, 110,
                     ["struct User {",
                      "  std::string name;",
                      "  int age;",
                      "  double score;",
                      "};"],
                     size=11, anchor="start", fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(185, 270, "Типи, змінні, функції,", size=11, color=MUTED))
    p.append(text(185, 292, "поля та переліки в коді", size=11, color=MUTED))
    p.append(monobox(55, 320, 260, 50,
                     ["^^User   // оператор ^^",
                      "^^User::age"],
                     size=11, anchor="start", fill="#eef3ff", stroke=NEG, sw=1.8, color=NEG))

    # Стрілка Lift: ^^
    p.append(arrow(330, 230, 400, 230, color=NEG, sw=2.2))
    p.append(text(365, 212, "Lift", size=12, bold=True, color=NEG))
    p.append(mono(365, 252, "^^T", size=13, color=NEG, bold=True))

    # 2. Простір значень метаінформації (std::meta::info)
    p.append(rect(400, 70, 320, 320, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(560, 102, "2. Значення std::meta::info", size=14, bold=True, color=FIELD))
    p.append(monobox(415, 126, 290, 140,
                     ["consteval {",
                      "  info r = ^^User;",
                      "  auto m = members_of(r);",
                      "  for (info f : m) {",
                      "    name_of(f);",
                      "    type_of(f);",
                      "  }",
                      "}"],
                     size=11, anchor="start", fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(text(560, 295, "Звичайний імперативний C++:", size=11, color=INK))
    p.append(text(560, 318, "std::vector, std::ranges, алгоритми", size=11, color=MUTED))
    p.append(text(560, 340, "без створення типів у таблиці символів", size=11, color=MUTED))
    p.append(text(560, 362, "виконується в consteval", size=11, color=FIELD, bold=True))

    # Стрілка Splice: [: :]
    p.append(arrow(720, 230, 790, 230, color=POS, sw=2.2))
    p.append(text(755, 212, "Splice", size=12, bold=True, color=POS))
    p.append(mono(755, 252, "[: r :]", size=13, color=POS, bold=True))

    # 3. Розгортання в код
    p.append(rect(790, 70, 290, 320, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(935, 102, "3. Розгорнутий код", size=14, bold=True, color=POS))
    p.append(monobox(805, 126, 260, 110,
                     ["// доступ до поля:",
                      "u.[: member_info :] = 42;",
                      "",
                      "// використання типу:",
                      "[: type_info :] val;"],
                     size=11, anchor="start", fill="#ffffff", stroke=POS, sw=1.2))
    p.append(text(935, 270, "Зворотне перетворення", size=11, color=INK))
    p.append(text(935, 292, "значення у вираз, тип,", size=11, color=MUTED))
    p.append(text(935, 314, "назву члена чи базовий клас", size=11, color=MUTED))
    p.append(text(935, 350, "Zero runtime overhead", size=12, bold=True, color=POS))

    # Підсумковий напис внизу
    p.append(text(W / 2, 435, "Рефлексія перетворює код на дані (std::meta::info), опрацьовує їх у consteval, і вклеює назад оператором [: :]",
                  size=12, color=INK))

    render(os.path.join(OUT, "reflection-pipeline.svg"), W, H,
           title="Життєвий цикл рефлексії: підйом (^^), обробка (consteval) і сплайсинг ([: :])", *p)


# ── 2. П'ять контекстів сплайсингу [: ... :] ──────────────────────────────
def fig_splice_contexts():
    W = 1120
    rows = [
        ("Контекст типу", "[: ^^int :] x = 42;", "Підставляє тип замість імені; еквівалентно int x = 42", NEG),
        ("Контекст виразу / члена", "user.[: ^^User::age :] = 30;", "Доступ до поля об'єкта через рефлексивне значення члена", FIELD),
        ("Контекст простору назв", "[: ^^std :]::vector<int> v;", "Використання рефлексії простору імен для кваліфікації ідентифікаторів", INK),
        ("Контекст аргументу шаблона", "std::tuple<[: ^^int :], [: ^^double :]>", "Передавання типу чи значення в список аргументів шаблона", POS),
        ("Контекст базового класу", "struct D : public [: ^^Base :] {};", "Динамічне визначення батьківського класу на етапі компіляції", MUTED),
    ]

    top, rh, gap = 70, 58, 14
    H = top + len(rows) * (rh + gap) + 40
    p = []

    p.append(text(W / 2, 40, "Оператор сплайсингу [: r :] перетворює дескриптор info назад у синтаксичну сутність C++",
                  size=13, bold=True, color=INK))

    for i, (ctx, code_str, desc, accent) in enumerate(rows):
        y = top + i * (rh + gap)
        # Назва контексту
        p.append(monobox(40, y, 230, rh, [ctx], size=11, fill="#f8fafc", stroke=accent, sw=1.6, color=accent))
        # Код
        p.append(monobox(285, y, 360, rh, [code_str], size=11, fill="#ffffff", stroke=LINE, sw=1.3, anchor="start"))
        # Пояснення
        p.append(textbox(870, y + rh / 2, desc, size=11, fill="#ffffff", stroke=LINE, sw=1.0, min_w=420)[0])

    render(os.path.join(OUT, "splice-contexts.svg"), W, H,
           title="П'ять контекстів оператора сплайсингу [: ... :]", *p)


# ── 3. Порівняння: Шаблонне метапрограмування проти Value-Based рефлексії ──
def fig_value_vs_template_metaprog():
    W, H = 1120, 490
    p = []

    p.append(line(560, 50, 560, 440, color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(285, 42, "Шаблонне метапрограмування (C++98 — C++20)", size=13, bold=True, color=POS))
    p.append(text(845, 42, "Значеннєва рефлексія C++26 (P2996)", size=13, bold=True, color=FIELD))

    # Ліва колонка
    p.append(monobox(40, 68, 480, 110,
                     ["// Типове кодування властивостей через типи:",
                      "template <typename T>",
                      "struct inspect_fields : std::false_type {};",
                      "template <> struct inspect_fields<User> {",
                      "  using types = std::tuple<string, int>;",
                      "};"],
                     size=11, anchor="start", fill="#fdecea", stroke=POS, sw=1.6))

    l_items = [
        "Кожна мета-операція створює новий тип у таблиці символів",
        "Рекурсивне розгортання шаблонів засмічує пам'ять компілятора",
        "Неможливо дізнатися назви полів без макросів (BOOST_HANA / PFR)",
        "Помилки компіляції розгортаються на сотні рядків шаблонів",
        "Експоненційне сповільнення часу збірки для великих проектів",
    ]
    for i, item in enumerate(l_items):
        p.append(text(60, 205 + i * 44, "• " + item, size=11, color=INK, anchor="start"))

    # Права колонка
    p.append(monobox(600, 68, 480, 110,
                     ["// Значеннєве обчислення в consteval:",
                      "consteval auto get_field_names(info type) {",
                      "  std::vector<std::string_view> names;",
                      "  for (info f : nonstatic_data_members_of(type))",
                      "    names.push_back(name_of(f));",
                      "  return names;",
                      "}"],
                     size=11, anchor="start", fill="#eef7f0", stroke=FIELD, sw=1.6))

    r_items = [
        "Один скалярний тип std::meta::info для всіх метаданих",
        "Стандартні структури даних (std::vector, std::string_view) у consteval",
        "Прямий доступ до назв, типів, вирівнювання, специфікаторів доступу",
        "Зрозумілі компіляторні діагностики та звичайні помилки C++",
        "Швидкість компіляції в десятки разів вища за шаблонні рекурсії",
    ]
    for i, item in enumerate(r_items):
        p.append(text(620, 205 + i * 44, "• " + item, size=11, color=INK, anchor="start"))

    p.append(text(W / 2, 455, "Заміна обчислень у системі типів на звичайні алгоритми над значеннями info радикально спрощує метапрограмування",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "value-vs-template-metaprog.svg"), W, H,
           title="Порівняння підходів: типи проти значень", *p)


# ── 4. Покрокове розгортання полів структури під час серіалізації ──────────
def fig_struct_field_expansion():
    W, H = 1120, 480
    p = []

    # 1. Вихідний об'єкт
    p.append(rect(40, 60, 220, 360, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(150, 90, "Об'єкт у пам'яті", size=13, bold=True, color=INK))
    p.append(monobox(55, 110, 190, 120,
                     ["struct Person {",
                      "  string name;",
                      "  int age;",
                      "  double salary;",
                      "};"],
                     size=11, anchor="start", fill="#f8fafc", stroke=LINE, sw=1.2))
    p.append(monobox(55, 250, 190, 80,
                     ["Person p{",
                      "  \"Alice\",",
                      "  30,",
                      "  4500.0",
                      "};"],
                     size=11, anchor="start", fill="#f8fafc", stroke=LINE, sw=1.2))

    # Стрілка 1
    p.append(arrow(260, 240, 320, 240, color=NEG, sw=1.8))
    p.append(text(290, 225, "^^Person", size=10.5, color=NEG, bold=True))

    # 2. Масив дескрипторів info
    p.append(rect(320, 60, 240, 360, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(440, 90, "Дескриптори полів", size=13, bold=True, color=FIELD))
    p.append(text(440, 112, "nonstatic_data_members_of", size=10.5, color=MUTED))

    fields = [
        ("info #0", "name_of: \"name\"", "type_of: string"),
        ("info #1", "name_of: \"age\"", "type_of: int"),
        ("info #2", "name_of: \"salary\"", "type_of: double"),
    ]
    for i, (inf, nm, tp) in enumerate(fields):
        p.append(monobox(335, 140 + i * 85, 210, 72,
                         [inf, nm, tp],
                         size=10.5, anchor="start", fill="#ffffff", stroke=FIELD, sw=1.2))

    # Стрілка 2
    p.append(arrow(560, 240, 620, 240, color=FIELD, sw=1.8))
    p.append(text(590, 225, "template for", size=10.5, color=FIELD, bold=True))

    # 3. Розгортання доступу через [: m :]
    p.append(rect(620, 60, 230, 360, fill="#eef3ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(735, 90, "Генерація виразів", size=13, bold=True, color=NEG))
    p.append(text(735, 112, "p.[: m :]", size=10.5, color=MUTED))

    gen_steps = [
        ["// Крок 0:", "key: \"name\"", "val: p.[: #0 :] -> p.name"],
        ["// Крок 1:", "key: \"age\"", "val: p.[: #1 :] -> p.age"],
        ["// Крок 2:", "key: \"salary\"", "val: p.[: #2 :] -> p.salary"],
    ]
    for i, stp in enumerate(gen_steps):
        p.append(monobox(635, 140 + i * 85, 200, 72,
                         stp,
                         size=10.5, anchor="start", fill="#ffffff", stroke=NEG, sw=1.2))

    # Стрілка 3
    p.append(arrow(850, 240, 910, 240, color=POS, sw=1.8))
    p.append(text(880, 225, "вивід", size=10.5, color=POS, bold=True))

    # 4. Результат JSON
    p.append(rect(910, 60, 170, 360, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(995, 90, "JSON результат", size=13, bold=True, color=POS))
    p.append(monobox(920, 140, 150, 160,
                     ["{",
                      "  \"name\": \"Alice\",",
                      "  \"age\": 30,",
                      "  \"salary\": 4500.0",
                      "}"],
                     size=10.5, anchor="start", fill="#ffffff", stroke=POS, sw=1.2))
    p.append(text(995, 330, "Без макросів", size=11, bold=True, color=POS))
    p.append(text(995, 352, "Без зовнішніх генераторів", size=10.5, color=MUTED))
    p.append(text(995, 374, "Без накладних витрат", size=10.5, color=MUTED))

    p.append(text(W / 2, 450, "Цикл template for перебирає дескриптори полів у час компіляції, генеруючи прямий доступ до полів об'єкта",
                  size=12, color=INK))

    render(os.path.join(OUT, "struct-field-expansion.svg"), W, H,
           title="Покрокове розгортання полів структури під час серіалізації", *p)


if __name__ == "__main__":
    fig_reflection_pipeline()
    fig_splice_contexts()
    fig_value_vs_template_metaprog()
    fig_struct_field_expansion()
    print("ok")
