# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f172a"
CODE_FG = "#38bdf8"
CARD_BG = "#f8fafc"
HL_BG   = "#e0f2fe"
WARN_BG = "#fef2f2"
SUCC_BG = "#f0fdf4"


# ── 1. unification-tree: декомпозиція та уніфікація термів типів ──────────────
def fig_unification_tree():
    W, H = 860, 460
    p = []

    # Підзаголовок (головний заголовок створює render(..., title=...))
    p.append(text(W / 2, 48, "Рівняння: (α → Int) → β  =?=  (Bool → γ) → (δ → Bool)",
                  size=12, color=MUTED, italic=True))

    # Дерево 1 (Лівий тип)
    p.append(rect(30, 68, 380, 200, fill=CARD_BG, stroke=LINE, sw=1.2, rx=8))
    p.append(text(220, 92, "Лівий терм T₁: (α → Int) → β", size=13, color=INK, bold=True))

    b_root1, _, _ = textbox(220, 130, "→ (головний)", size=12, fill="#e2e8f0", stroke=LINE, bold=True)
    p.append(b_root1)

    b_left1, _, _ = textbox(125, 195, "→ (стрілка)\narg: α, res: Int", size=10.5, fill="#ede9fe", stroke="#8b5cf6")
    p.append(b_left1)

    b_right1, _, _ = textbox(315, 195, "змінна\nβ", size=10.5, fill=HL_BG, stroke=NEG, bold=True)
    p.append(b_right1)

    p.append(line(220, 145, 125, 172, color=LINE, sw=1.2))
    p.append(line(220, 145, 315, 172, color=LINE, sw=1.2))

    # Дерево 2 (Правий тип)
    p.append(rect(450, 68, 380, 200, fill=CARD_BG, stroke=LINE, sw=1.2, rx=8))
    p.append(text(640, 92, "Правий терм T₂: (Bool → γ) → (δ → Bool)", size=13, color=INK, bold=True))

    b_root2, _, _ = textbox(640, 130, "→ (головний)", size=12, fill="#e2e8f0", stroke=LINE, bold=True)
    p.append(b_root2)

    b_left2, _, _ = textbox(545, 195, "→ (стрілка)\narg: Bool, res: γ", size=10.5, fill="#ede9fe", stroke="#8b5cf6")
    p.append(b_left2)

    b_right2, _, _ = textbox(735, 195, "→ (стрілка)\narg: δ, res: Bool", size=10.5, fill="#ede9fe", stroke="#8b5cf6")
    p.append(b_right2)

    p.append(line(640, 145, 545, 172, color=LINE, sw=1.2))
    p.append(line(640, 145, 735, 172, color=LINE, sw=1.2))

    # Зв'язки декомпозиції між деревами
    p.append(arrow(220, 245, 220, 285, color=NEG, sw=1.6))
    p.append(arrow(640, 245, 640, 285, color=NEG, sw=1.6))

    # Блок результату підстановки
    p.append(rect(30, 295, 800, 145, fill=SUCC_BG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(W / 2, 320, "Покрокове виведення найбільш загального уніфікатора (MGU):",
                  size=12, color=FIELD, bold=True))

    sub_steps = [
        "1. Збіг конструкторів: обидва корені є функціональною стрілкою (→). Декомпозуємо гілки.",
        "2. Ліва гілка: α = Bool  ⇒  [α ↦ Bool],   Int = γ  ⇒  [γ ↦ Int].",
        "3. Права гілка: β = (δ → Bool)  ⇒  [β ↦ (δ → Bool)]  (перевірка occurs-check: β ∉ vars(δ → Bool) — успіх).",
        "Підсумкова підстановка σ = { α ↦ Bool, γ ↦ Int, β ↦ (δ → Bool) }. Загальний тип: (Bool → Int) → (δ → Bool)",
    ]
    for i, s in enumerate(sub_steps):
        p.append(text(50, 346 + i * 20, s, size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "unification-tree.svg"), W, H, *p,
           title="Уніфікація Робінсона: зведення двох дерев типів до спільної форми")


# ── 2. global-vs-local: Глобальне виведення HM проти локального ───────────────
def fig_global_vs_local():
    W, H = 860, 370
    p = []

    # Ліва колонка: Глобальне HM
    p.append(rect(30, 55, 385, 290, fill=CARD_BG, stroke=LINE, sw=1.4, rx=8))
    p.append(text(222, 82, "Глобальне виведення (Haskell, OCaml)", size=13, color=INK, bold=True))

    hm_boxes = [
        (222, 125, "1. Побудова графа обмежень для всього модуля\nУсі вирази отримують вільні змінні типів (α, β, γ)"),
        (222, 185, "2. Наскрізна глобальна уніфікація\nРозв'язання системи рівнянь між усіма функціями"),
        (222, 245, "3. Узагальнення схеми типів (Let-поліморфізм)\nСигнатури виводяться автоматично без анотацій"),
    ]
    for cx, cy, txt in hm_boxes:
        b, _, _ = textbox(cx, cy, txt, size=10, fill=HL_BG, stroke=NEG, pad=8, min_w=350)
        p.append(b)

    p.append(text(222, 315, "Плюс: нуль шуму в коді. Мінус: помилка в рядку 50 б'є в рядок 5.",
                  size=10, color=POS, italic=True))

    # Права колонка: Локальне виведення
    p.append(rect(445, 55, 385, 290, fill=CARD_BG, stroke=LINE, sw=1.4, rx=8))
    p.append(text(637, 82, "Локальне виведення (C++ auto, Rust let, Go :=)", size=13, color=INK, bold=True))

    local_boxes = [
        (637, 125, "1. Жорсткі контрактні межі (Сигнатури)\nТипи параметрів і повернення функцій фіксовані явно"),
        (637, 185, "2. Виведення лише всередині тіла функції\nКомпілятор іде зверху вниз / зліва направо за ініціалізатором"),
        (637, 245, "3. Ізоляція одиниць трансляції\nЗміна всередині функції не ламає типів зовнішніх клієнтів"),
    ]
    for cx, cy, txt in local_boxes:
        b, _, _ = textbox(cx, cy, txt, size=10, fill=SUCC_BG, stroke=FIELD, pad=8, min_w=350)
        p.append(b)

    p.append(text(637, 315, "Плюс: швидка збірка, локальні помилки, підтримка підтипів.",
                  size=10, color=FIELD, italic=True))

    render(os.path.join(OUT, "global-vs-local.svg"), W, H, *p,
           title="Глобальне виведення (Hindley-Milner) проти локального (C++, Rust, Go)")


# ── 3. cpp-deduction-rules: Матриця правил дедукції C++ ───────────────────────
def fig_cpp_deduction_rules():
    W, H = 860, 390
    p = []

    cols = [
        (30, 190, "auto", "За значенням (Value)", [
            "• Відкидає посилання (&, &&)",
            "• Відкидає top-level const",
            "• Масив спадає до покажчика",
            "Приклад:",
            "const int& x = 10;",
            "auto a = x;  // тип: int"
        ], "#eff6ff", NEG),
        (230, 190, "auto& / const auto&", "Lvalue-посилання", [
            "• Зберігає const / volatile",
            "• Гарантує посилання на об'єкт",
            "• Забороняє rvalue до non-const",
            "Приклад:",
            "const int x = 10;",
            "auto& b = x;  // const int&"
        ], "#f0fdf4", FIELD),
        (430, 190, "auto&&", "Універсальне посилання", [
            "• Згортання посилань:",
            "  & + & → &,   && + & → &",
            "  & + && → &,  && + && → &&",
            "• Зберігає категорію значення",
            "Приклад:",
            "auto&& c = 10; // int&&",
            "auto&& d = x;  // int&"
        ], "#fefce8", "#ca8a04"),
        (630, 200, "decltype(auto)", "Точний запит типу", [
            "• Не використовує шаблони",
            "• Застосовує decltype(expr)",
            "• Зберігає категорію виразу:",
            "  ім'я x → точний тип T",
            "  вираз (x) → T& (lvalue)",
            "Приклад:",
            "decltype(auto) r = get_ref();"
        ], "#faf5ff", "#9333ea"),
    ]

    for x, w, title, sub, lines, bg, stroke_c in cols:
        p.append(rect(x, 52, w, 320, fill=bg, stroke=stroke_c, sw=1.4, rx=8))
        p.append(text(x + w / 2, 74, title, size=13, color=stroke_c, bold=True))
        p.append(text(x + w / 2, 92, sub, size=10, color=MUTED, italic=True))
        p.append(line(x + 10, 102, x + w - 10, 102, color=stroke_c, sw=0.8))

        y = 122
        for ln in lines:
            if ln.startswith("Приклад:"):
                y += 6
                p.append(text(x + 12, y, ln, size=10, color=INK, anchor="start", bold=True))
            elif ln.startswith("auto") or ln.startswith("decltype") or ln.startswith("const int"):
                p.append(text(x + 12, y, ln, size=9.5, color="#1e293b", anchor="start", bold=True))
            else:
                p.append(text(x + 12, y, ln, size=9.5, color=INK, anchor="start"))
            y += 18

    render(os.path.join(OUT, "cpp-deduction-rules.svg"), W, H, *p,
           title="Правила виведення типів у C++: auto, посилання та decltype(auto)")


# ── 4. subtyping-undecidability: Підтипізація та неоднозначність уніфікації ───
def fig_subtyping_undecidability():
    W, H = 860, 420
    p = []

    # Ліва частина: Решітка типів (Lattice)
    p.append(rect(30, 52, 380, 345, fill=CARD_BG, stroke=LINE, sw=1.3, rx=8))
    p.append(text(220, 78, "Решітка підтипів: відсутність єдиного MGU", size=12, color=INK, bold=True))

    # Вузли решітки
    b_top, _, _ = textbox(220, 115, "Any / Object (Top тип)", size=11, fill="#f1f5f9", stroke=LINE)
    p.append(b_top)

    b_i1, _, _ = textbox(135, 185, "Інтерфейс IReader", size=11, fill=HL_BG, stroke=NEG, bold=True)
    p.append(b_i1)

    b_i2, _, _ = textbox(305, 185, "Інтерфейс ICloser", size=11, fill=HL_BG, stroke=NEG, bold=True)
    p.append(b_i2)

    b_c, _, _ = textbox(220, 265, "Клас FileStream\n(реалізує IReader та ICloser)", size=11, fill=SUCC_BG, stroke=FIELD, bold=True)
    p.append(b_c)

    p.append(arrow(220, 240, 145, 205, color=FIELD, sw=1.3))
    p.append(arrow(220, 240, 295, 205, color=FIELD, sw=1.3))
    p.append(arrow(135, 165, 205, 130, color=NEG, sw=1.3))
    p.append(arrow(305, 165, 235, 130, color=NEG, sw=1.3))

    p.append(text(220, 360, "FileStream має дві незрівнянні суперформи: IReader та ICloser",
                  size=9.5, color=MUTED, italic=True))

    # Права частина: Пояснення дилеми виведення
    p.append(rect(430, 52, 400, 345, fill=CARD_BG, stroke=LINE, sw=1.3, rx=8))
    p.append(text(630, 78, "Дилема компілятора при розв'язанні обмежень", size=12, color=INK, bold=True))

    ex_text = [
        ("Вираз: let process = \\x -> (read x, close x)", "#1e293b", True),
        ("", INK, False),
        ("В системі Гіндлі-Мілнера (без підтипів):", FIELD, True),
        ("• x повинен мати точний структурний тип.", INK, False),
        ("• Уніфікація знаходить єдиний головний тип.", INK, False),
        ("", INK, False),
        ("З підтипізацією (Java, C#, C++):", "#854d0e", True),
        ("• Обмеження: x <: IReader  ТА  x <: ICloser", INK, False),
        ("• Який тип вивести для аргументу x?", INK, False),
        ("  1) FileStream? Надто вузько для інших потоків.", INK, False),
        ("  2) Object? Втрачає методи read та close.", INK, False),
        ("  3) Перетин (IReader & ICloser)? Потребує union/inter.", INK, False),
        ("", INK, False),
        ("Висновок: глобальне виведення стає експоненційним", POS, True),
        ("або нерозв'язним без явних сигнатур функцій.", POS, True),
    ]
    y = 104
    for ln, col, bld in ex_text:
        if ln:
            p.append(text(448, y, ln, size=10, color=col, anchor="start", bold=bld))
        y += 18

    render(os.path.join(OUT, "subtyping-undecidability.svg"), W, H, *p,
           title="Підтипізація (Subtyping) та неоднозначність глобального виведення")


def main():
    fig_unification_tree()
    fig_global_vs_local()
    fig_cpp_deduction_rules()
    fig_subtyping_undecidability()
    print("Усі фігури успішно згенеровано у ./img/")


if __name__ == "__main__":
    main()
