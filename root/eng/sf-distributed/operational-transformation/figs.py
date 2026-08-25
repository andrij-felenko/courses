# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Розходження індексів без OT та збіжність з OT ────────────────────────
def fig_index_shift():
    W, H = 960, 560
    p = []

    # Ліва колонка: Без OT (розходження)
    p.append(rect(24, 50, 440, 485, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    p.append(text(244, 76, "Без перетворення (наївний обмін)", size=14, color=POS, bold=True))

    # Стан S0
    p.append(fitbox(144, 98, 200, 32, "Початковий текст: «CAT»", size=12, fill="#ffffff", stroke=LINE, bold=True))

    # Дії А та В
    p.append(fitbox(44, 150, 180, 52, "Клієнт A:\nDel(1, 'A') → «CT»", size=11.5, fill="#fdf2ee", stroke=POS, color=INK, bold=True))
    p.append(fitbox(264, 150, 180, 52, "Клієнт B:\nIns(0, 'H') → «HCAT»", size=11.5, fill="#fdf2ee", stroke=POS, color=INK, bold=True))

    p.append(arrow(190, 132, 134, 148, color=MUTED))
    p.append(arrow(298, 132, 354, 148, color=MUTED))

    # Перехресне надсилання без OT
    p.append(arrow(134, 204, 300, 260, color=POS, sw=1.6))
    p.append(arrow(354, 204, 188, 260, color=POS, sw=1.6))
    p.append(textbox(244, 230, "сирі операції", size=11, pad=4, fill="#ffffff", stroke=POS, color=POS, bold=True)[0])

    # Застосування сирих операцій
    p.append(fitbox(44, 275, 180, 68, "A застосовує Ins(0, 'H'):\n'H' на поз. 0 у «CT»\n→ «HCT»", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(264, 275, 180, 68, "B застосовує Del(1):\nвидаляє 'C' у «HCAT»\n→ «HAT» (помилка!)", size=11, fill="#ffffff", stroke=POS, color=POS, bold=True))

    # Фінал без OT
    p.append(fitbox(44, 365, 400, 150, "РЕЗУЛЬТАТ: РОЗХОДЖЕННЯ ТА ВТРАТА НАМІРУ\n\n• Клієнт A бачить «HCT», Клієнт B бачить «HAT»\n• Символ 'A' лишився в тексті на вузлі B\n• Символ 'C' помилково видалено через зсув індексу\n• Копії документів розійшлися назавжди",
                    size=11, fill="#fdf0ed", stroke=POS, color=POS, bold=True))

    # Права колонка: З OT (збіжність)
    p.append(rect(496, 50, 440, 485, fill="#f9fcf9", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(716, 76, "З операційним перетворенням (OT)", size=14, color=FIELD, bold=True))

    # Стан S0
    p.append(fitbox(616, 98, 200, 32, "Початковий текст: «CAT»", size=12, fill="#ffffff", stroke=LINE, bold=True))

    # Дії А та В
    p.append(fitbox(516, 150, 180, 52, "Клієнт A:\nDel(1, 'A') → «CT»", size=11.5, fill="#f2f8f3", stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(736, 150, 180, 52, "Клієнт B:\nIns(0, 'H') → «HCAT»", size=11.5, fill="#f2f8f3", stroke=FIELD, color=INK, bold=True))

    p.append(arrow(662, 132, 606, 148, color=MUTED))
    p.append(arrow(770, 132, 826, 148, color=MUTED))

    # Перехресне надсилання з перетворенням
    p.append(arrow(606, 204, 772, 260, color=FIELD, sw=1.6))
    p.append(arrow(826, 204, 660, 260, color=FIELD, sw=1.6))
    p.append(textbox(716, 230, "T(op1, op2)", size=11, pad=4, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)[0])

    # Застосування трансформованих операцій
    p.append(fitbox(516, 275, 180, 68, "A отримує Ins'(0, 'H'):\n0 <= 1 → без зсуву\n→ «HCT»", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(736, 275, 180, 68, "B отримує Del'(2, 'A'):\n1 >= 0 → зсув на +1\n→ «HCT» (коректно!)", size=11, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True))

    # Фінал з OT
    p.append(fitbox(516, 365, 400, 150, "РЕЗУЛЬТАТ: ПОВНА ЗБІЖНІСТЬ ТА ЗБЕРЕЖЕННЯ НАМІРУ\n\n• Обидва клієнти мають однаковий текст «HCT»\n• Символ 'A' видалено на обох вузлах\n• Символ 'H' коректно вставлено на позицію 0\n• Намір кожного автора повністю збережено",
                    size=11, fill="#edf7ee", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "index-shift-divergence.svg"), W, H, *p,
           title="Дилема зміщення індексів у спільному тексті")


# ── Фіг. 2: Матриця перетворення операцій включення (Inclusion Transformation) ───
def fig_transform_matrix():
    W, H = 960, 560
    p = []

    p.append(text(W / 2, 48, "Як змінюються параметри операції op1 після врахування паралельної op2", size=12, color=MUTED))

    cases = [
        ("Ins(p1, c1) проти Ins(p2, c2)",
         "Дві паралельні вставки символів",
         "• Якщо p1 < p2 : p1' = p1 (вставка лівіше, індекс без змін)\n\n"
         "• Якщо p1 > p2 : p1' = p1 + 1 (чужа вставка зсунула текст на +1)\n\n"
         "• Якщо p1 == p2 : тай-брейк за ID клієнта (детермінований вибір)",
         30, 75, 435, 220, FIELD),

        ("Ins(p1, c1) проти Del(p2)",
         "Вставка символу проти паралельного видалення",
         "• Якщо p1 <= p2 : p1' = p1 (видалення правіше або в тій же точці)\n\n"
         "• Якщо p1 > p2 : p1' = p1 - 1 (чуже видалення зсунуло текст на -1)\n\n"
         "• Символ c1 гарантовано потрапляє у збережену позицію наміру",
         495, 75, 435, 220, NEG),

        ("Del(p1) проти Ins(p2, c2)",
         "Видалення символу проти паралельної вставки",
         "• Якщо p1 < p2 : p1' = p1 (вставка відбулася правіше видалення)\n\n"
         "• Якщо p1 >= p2 : p1' = p1 + 1 (чужа вставка зсунула цільовий символ на +1)\n\n"
         "• Видаляється саме той символ, на який спочатку вказував автор",
         30, 315, 435, 220, NEG),

        ("Del(p1) проти Del(p2)",
         "Два паралельні видалення символів",
         "• Якщо p1 < p2 : p1' = p1 (видалення правого символу не зміщує лівий)\n\n"
         "• Якщо p1 > p2 : p1' = p1 - 1 (лівий символ зник, цільовий зсунувся на -1)\n\n"
         "• Якщо p1 == p2 : op1' = NoOp() (символ уже видалено паралельно)",
         495, 315, 435, 220, POS)
    ]

    for title, subtitle, rules_text, x, y, w, h, accent in cases:
        p.append(rect(x, y, w, h, fill="#fdfdfd", stroke="#d8dde3", sw=1.4, rx=8))
        p.append(rect(x, y, w, 32, fill="#f4f6f8", stroke="#d8dde3", sw=1.4, rx=8))
        p.append(text(x + w / 2, y + 21, title, size=12.5, color=accent, bold=True))
        p.append(text(x + 16, y + 54, subtitle, size=11, color=MUTED, anchor="start", italic=True))
        p.append(fitbox(x + 10, y + 68, w - 20, h - 76, rules_text, size=11, fill="none", stroke="none", color=INK))

    render(os.path.join(OUT, "inclusion-transformation-matrix.svg"), W, H, *p,
           title="Матриця функцій перетворення включення: T(op1, op2)")


# ── Фіг. 3: Умови коректності трансформацій TP1 та TP2 ───────────────────────────
def fig_properties_tp1_tp2():
    W, H = 960, 480
    p = []

    # Ліва панель: TP1 (Diamond / Ромб)
    p.append(rect(24, 55, 440, 400, fill="#fbfdff", stroke="#d0d7de", sw=1.4, rx=8))
    p.append(text(244, 82, "Властивість TP1: Збіжність для пари операцій", size=13, color=NEG, bold=True))
    p.append(text(244, 104, "S ∘ op1 ∘ T(op2, op1) ≡ S ∘ op2 ∘ T(op1, op2)", size=11.5, color=MUTED))

    # Ромб станів
    p.append(fitbox(204, 130, 80, 34, "Стан S", size=12, fill="#eef2f7", stroke=LINE, bold=True))
    p.append(fitbox(64, 230, 95, 34, "S ∘ op1", size=11.5, fill="#fdf2ee", stroke=POS, bold=True))
    p.append(fitbox(324, 230, 95, 34, "S ∘ op2", size=11.5, fill="#fdf2ee", stroke=POS, bold=True))
    p.append(fitbox(194, 330, 100, 34, "Кінцевий S'", size=12, fill="#edf7ee", stroke=FIELD, bold=True))

    # Стрілки ромба
    p.append(arrow(210, 160, 140, 225, color=POS, sw=1.8))
    p.append(text(150, 185, "op1", size=11.5, color=POS, bold=True))

    p.append(arrow(278, 160, 348, 225, color=POS, sw=1.8))
    p.append(text(338, 185, "op2", size=11.5, color=POS, bold=True))

    p.append(arrow(140, 270, 210, 330, color=FIELD, sw=1.8))
    p.append(text(135, 310, "T(op2, op1)", size=11, color=FIELD, bold=True))

    p.append(arrow(348, 270, 278, 330, color=FIELD, sw=1.8))
    p.append(text(355, 310, "T(op1, op2)", size=11, color=FIELD, bold=True))

    p.append(fitbox(44, 385, 400, 56, "Обидва шляхи трансформації приводять до ідентичного стану S'.\nДостатня умова для систем із центральним сервером (Jupiter).",
                    size=11, fill="#f7f9fa", stroke="#d0d7de", color=INK))

    # Права панель: TP2 (Шляхонезалежність для 3 операцій)
    p.append(rect(496, 55, 440, 400, fill="#fbfdff", stroke="#d0d7de", sw=1.4, rx=8))
    p.append(text(716, 82, "Властивість TP2: Незалежність від шляху (3 операції)", size=13, color=POS, bold=True))
    p.append(text(716, 104, "T(T(op3, op1), T(op2, op1)) ≡ T(T(op3, op2), T(op1, op2))", size=11, color=MUTED))

    # Візуалізація куба/шляхів
    p.append(fitbox(666, 130, 100, 34, "Операція op3", size=12, fill="#eef2f7", stroke=LINE, bold=True))

    p.append(fitbox(526, 210, 140, 34, "Через op1: T(op3, op1)", size=11, fill="#fef8f0", stroke="#d97706", bold=True))
    p.append(fitbox(766, 210, 140, 34, "Через op2: T(op3, op2)", size=11, fill="#fef8f0", stroke="#d97706", bold=True))

    p.append(arrow(686, 168, 616, 206, color=MUTED, sw=1.5))
    p.append(arrow(746, 168, 816, 206, color=MUTED, sw=1.5))

    p.append(fitbox(516, 290, 160, 44, "T( T(op3, op1),\n   T(op2, op1) )", size=10.5, fill="#edf7ee", stroke=FIELD, bold=True))
    p.append(fitbox(756, 290, 160, 44, "T( T(op3, op2),\n   T(op1, op2) )", size=10.5, fill="#edf7ee", stroke=FIELD, bold=True))

    p.append(arrow(596, 248, 596, 286, color=FIELD, sw=1.8))
    p.append(arrow(836, 248, 836, 286, color=FIELD, sw=1.8))

    p.append(line(680, 312, 752, 312, color=FIELD, sw=2.2, dash="4,4"))
    p.append(text(716, 306, "≡", size=18, color=FIELD, bold=True))

    p.append(fitbox(516, 385, 400, 56, "Трансформована op3 однакова незалежно від порядку врахування op1 та op2.\nКритично необхідна умова для децентралізованих (P2P) алгоритмів OT.",
                    size=11, fill="#fdf2ee", stroke=POS, color=POS))

    render(os.path.join(OUT, "transformation-properties-tp1-tp2.svg"), W, H, *p,
           title="Властивості коректності перетворень: TP1 та TP2")


# ── Фіг. 4: Архітектура Jupiter (Google Docs / Клієнт-Серверна модель) ────────────
def fig_jupiter_protocol():
    W, H = 960, 540
    p = []

    p.append(text(W / 2, 48, "Як лінеаризація на сервері зводить складність до TP1 та усуває потребу в TP2", size=12, color=MUTED))

    cx_a = 150
    cx_s = 480
    cx_b = 810

    # Заголовки акторів
    p.append(fitbox(cx_a - 90, 68, 180, 38, "Клієнт A", size=13, fill="#eef2f7", stroke=LINE, bold=True))
    p.append(fitbox(cx_s - 100, 68, 200, 38, "Сервер (Арбітр ревізій)", size=13, fill="#fdf2ee", stroke=POS, bold=True))
    p.append(fitbox(cx_b - 90, 68, 180, 38, "Клієнт B", size=13, fill="#eef2f7", stroke=LINE, bold=True))

    # Сегментовані вертикальні лінії для Клієнта A
    p.append(line(cx_a, 108, cx_a, 150, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_a, 184, cx_a, 400, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_a, 436, cx_a, 465, color="#d0d7de", sw=1.5, dash="4,4"))

    # Сегментовані вертикальні лінії для Клієнта B
    p.append(line(cx_b, 108, cx_b, 170, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_b, 204, cx_b, 400, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_b, 446, cx_b, 465, color="#d0d7de", sw=1.5, dash="4,4"))

    # Сегментовані вертикальні лінії для Сервера
    p.append(line(cx_s, 108, cx_s, 118, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_s, 144, cx_s, 195, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_s, 231, cx_s, 275, color="#d0d7de", sw=1.5, dash="4,4"))
    p.append(line(cx_s, 327, cx_s, 465, color="#d0d7de", sw=1.5, dash="4,4"))

    # Хронологія подій
    p.append(fitbox(cx_s - 75, 118, 150, 26, "Сервер: Ревізія 0", size=11, fill="#ffffff", stroke=LINE))

    p.append(fitbox(cx_a - 110, 150, 105, 34, "A: opA (rev 0)\nзастосовано", size=10.5, fill="#edf7ee", stroke=FIELD))
    p.append(arrow(cx_a, 165, cx_s - 105, 195, color=FIELD, sw=1.8))
    p.append(textbox(280, 168, "Надіслано opA (rev 0)", size=10, pad=3, fill="#ffffff", stroke=FIELD, color=FIELD)[0])

    p.append(fitbox(cx_b + 5, 170, 105, 34, "B: opB (rev 0)\nзастосовано", size=10.5, fill="#edf7ee", stroke=FIELD))
    p.append(arrow(cx_b, 185, cx_s + 105, 235, color=POS, sw=1.8))
    p.append(textbox(670, 198, "Надіслано opB (rev 0)", size=10, pad=3, fill="#ffffff", stroke=POS, color=POS)[0])

    p.append(fitbox(cx_s - 100, 195, 200, 36, "Прийнято opA → Ревізія 1\nЛог сервера: [opA]", size=11, fill="#fdf2ee", stroke=POS, bold=True))

    p.append(arrow(cx_s - 105, 225, cx_a, 255, color=FIELD, sw=1.5))
    p.append(textbox(280, 235, "ACK opA (rev 1)", size=10.5, pad=3, fill="#ffffff", stroke=FIELD, color=FIELD)[0])

    p.append(arrow(cx_s + 105, 230, cx_b, 275, color=MUTED, sw=1.5))
    p.append(textbox(670, 248, "Трансляція opA (rev 1)", size=10.5, pad=3, fill="#ffffff", stroke=MUTED, color=INK)[0])

    p.append(fitbox(cx_s - 130, 275, 260, 52, "Отримано opB (rev 0). Сервер на rev 1!\nТрансформація: opB' = T(opB, opA)\nЗапис у лог → Ревізія 2",
                    size=10.5, fill="#fff8e6", stroke="#d97706", bold=True))

    p.append(arrow(cx_s + 105, 335, cx_b, 375, color=POS, sw=1.5))
    p.append(textbox(670, 348, "ACK opB' (rev 2)", size=10.5, pad=3, fill="#ffffff", stroke=POS, color=POS)[0])

    p.append(arrow(cx_s - 105, 340, cx_a, 390, color=MUTED, sw=1.5))
    p.append(textbox(280, 360, "Трансляція opB' (rev 2)", size=10.5, pad=3, fill="#ffffff", stroke=MUTED, color=INK)[0])

    p.append(fitbox(cx_a - 110, 400, 110, 36, "A застосовує opB'\nСтан: rev 2", size=10.5, fill="#edf7ee", stroke=FIELD, bold=True))
    p.append(fitbox(cx_b - 5, 400, 120, 46, "B отримує opA,\nтрансформує буфер:\nopA' = T(opA, opB)", size=10, fill="#edf7ee", stroke=FIELD, bold=True))

    p.append(fitbox(50, 475, 860, 48, "СЕРВЕРНА ЛІНЕАРИЗАЦІЯ:\nКожна операція трансформується суто попарно проти лінійного логу сервера. Достатньо лише TP1!",
                    size=11.5, fill="#edf7ee", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "jupiter-client-server-protocol.svg"), W, H, *p,
           title="Клієнт-серверна модель Jupiter (Google Docs / Wave)")


if __name__ == "__main__":
    fig_index_shift()
    fig_transform_matrix()
    fig_properties_tp1_tp2()
    fig_jupiter_protocol()
    print("All figures generated successfully.")
