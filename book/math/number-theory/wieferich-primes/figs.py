# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_wieferich_congruence():
    """Порівняння звичайної теореми Ферма (mod p) та умови Віферіха (mod p²)."""
    W, H = 820, 520
    p = []

    p.append(text(W / 2, 40, "Анатомія остачі: Мала теорема Ферма проти умови Віферіха", size=16, bold=True))

    # Панель 1: Звичайна теорема Ферма (mod p)
    x1, y1, w1, h1 = 40, 75, 350, 370
    p.append(rect(x1, y1, w1, h1, fill="#f8f9fa", stroke="#d0d5dd", sw=1.5, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 30, "Мала теорема Ферма (mod p)", size=14, bold=True, color="#1d2939"))
    p.append(text(x1 + w1 / 2, y1 + 55, "Виконується для ВСІХ непарних простих p", size=11.5, color=MUTED))

    # Математичний блок
    b1, _, _ = textbox(x1 + w1 / 2, y1 + 130, [
        "2^(p-1) ≡ 1 (mod p)",
        "2^(p-1) - 1 = k · p",
        "W(p) = k  (ціле число)"
    ], size=13, pad=10, fill="#ffffff", stroke="#eaecf0")
    p.append(b1)

    # Приклади для p=7
    p.append(text(x1 + 30, y1 + 225, "Приклад p = 7:", size=13, bold=True))
    p.append(text(x1 + 30, y1 + 250, "2⁶ - 1 = 63 = 9 · 7", size=12.5))
    p.append(text(x1 + 30, y1 + 275, "Частка W(7) = 9", size=12.5))
    p.append(text(x1 + 30, y1 + 305, "Остача W(7) mod 7 = 2  (не 0!)", size=12.5, color="#d92d20", bold=True))

    # Статус
    b_stat1, _, _ = textbox(x1 + w1 / 2, y1 + 340, ["Стандартне просте число"], size=12, pad=6, fill="#fef3f2", stroke="#fda29b")
    p.append(b_stat1)

    # Панель 2: Умова Віферіха (mod p²)
    x2, y2, w2, h2 = 430, 75, 350, 370
    p.append(rect(x2, y2, w2, h2, fill="#f0f9ff", stroke="#b2ddff", sw=1.5, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 30, "Умова Віферіха (mod p²)", size=14, bold=True, color="#026aa2"))
    p.append(text(x2 + w2 / 2, y2 + 55, "Виконується лише для РІДКІСНИХ простих p", size=11.5, color=MUTED))

    # Математичний блок
    b2, _, _ = textbox(x2 + w2 / 2, y2 + 130, [
        "2^(p-1) ≡ 1 (mod p²)",
        "2^(p-1) - 1 = m · p²",
        "W(p) = m · p ≡ 0 (mod p)"
    ], size=13, pad=10, fill="#ffffff", stroke="#b2ddff")
    p.append(b2)

    # Приклади для p=1093
    p.append(text(x2 + 30, y2 + 225, "Приклад p = 1093:", size=13, bold=True))
    p.append(text(x2 + 30, y2 + 250, "2¹⁰⁹² - 1 = m · 1093²", size=12.5))
    p.append(text(x2 + 30, y2 + 275, "1093² = 1 194 649", size=12.5))
    p.append(text(x2 + 30, y2 + 305, "Остача W(1093) mod 1093 = 0!", size=12.5, color="#079455", bold=True))

    # Статус
    b_stat2, _, _ = textbox(x2 + w2 / 2, y2 + 340, ["Просте число Віферіха (p=1093, 3511)"], size=12, pad=6, fill="#ecfdf3", stroke="#6ce9a6")
    p.append(b_stat2)

    p.append(text(W / 2, 480, "Частка Віферіха W(p) = (2^(p-1)-1)/p ділиться на p тоді й лише тоді, коли p — просте Віферіха", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "wieferich-congruence.svg"), W, H, *p, title="Порівняння теореми Ферма та умови Віферіха")


def fig_flt_wieferich_pipeline():
    """Схема логічного ланцюжка теореми Віферіха в атаці на перший випадок ВТФ."""
    W, H = 840, 500
    p = []

    p.append(text(W / 2, 35, "Логічний ланцюжок Артура Віферіха (1909) для перший випадку ВТФ", size=15, bold=True))

    # Крок 1
    box1, _, _ = textbox(150, 110, [
        "Рівняння Ферма",
        "x^p + y^p = z^p",
        "Перший випадок: p ∤ xyz"
    ], size=12, pad=10, fill="#f8f9fa", stroke="#d0d5dd")
    p.append(box1)

    # Стрілка 1 -> 2
    p.append(arrow(260, 110, 310, 110, color="#667085", sw=1.5))

    # Крок 2
    box2, _, _ = textbox(440, 110, [
        "Розклад на множники",
        "(x+y)(x^(p-1) - ... + y^(p-1)) = z^p",
        "Арифметика кругових полів"
    ], size=12, pad=10, fill="#f8f9fa", stroke="#d0d5dd")
    p.append(box2)

    # Стрілка 2 -> 3
    p.append(arrow(570, 110, 620, 110, color="#667085", sw=1.5))

    # Крок 3 (Вимога Віферіха)
    box3, _, _ = textbox(730, 110, [
        "Критерій Віферіха",
        "2^(p-1) ≡ 1 (mod p²)",
        "Обов'язкова умова!"
    ], size=12, pad=10, fill="#eff8ff", stroke="#84caef")
    p.append(box3)

    # Вертикальна стрілка вниз до перевірки
    p.append(arrow(730, 170, 730, 230, color="#026aa2", sw=1.5))

    # Блок перевірки простих
    box4, _, _ = textbox(440, 280, [
        "Перевірка простих чисел p < 6.7 · 10¹⁸",
        "1. Якщо 2^(p-1) not≡ 1 (mod p²) → Перший випадок ВТФ виконано!",
        "2. Для p = 1093 та p = 3511: 3^(p-1) not≡ 1 (mod p²) (Теорема Міріманова 1910)"
    ], size=12.5, pad=12, fill="#f0fdf4", stroke="#73e2a7")
    p.append(box4)

    # Висновок
    box5, _, _ = textbox(440, 420, [
        "Висновок: Перший випадок Великої теореми Ферма повністю доведено",
        "для всіх простих чисел p у дослідженому діапазоні (і згодом для всіх p Ендрю Уайлсом)"
    ], size=13, pad=12, fill="#ecfdf3", stroke="#12b76a")
    p.append(box5)

    p.append(arrow(440, 345, 440, 375, color="#079455", sw=1.5))

    render(os.path.join(OUT, "flt-wieferich-pipeline.svg"), W, H, *p, title="Логіка теореми Віферіха в доведенні ВТФ")


def fig_search_timeline():
    """Хронологічна шкала пошуку простих чисел Віферіха та межі обчислень."""
    W, H = 840, 440
    p = []

    p.append(text(W / 2, 35, "Історія обчислювального пошуку простих чисел Віферіха", size=15, bold=True))

    # Горизонтальна вісь часу
    y_axis = 200
    p.append(line(60, y_axis, 780, y_axis, color="#475467", sw=2))

    milestones = [
        (100, 1909, "Артур Віферіх", "Довів теорему для ВТФ", "Знайшов p = 1093", "#026aa2"),
        (260, 1913, "Вальдемар Мейсснер", "Ручні обчислення", "Знайшов p = 3511", "#026aa2"),
        (420, 1971, "Бріллгарт, Тонессіа", "ЕОМ (IBM 360)", "Межа p < 3 · 10⁹", "#475467"),
        (580, 2004, "Крівенко, Родович", "Кластерні обчислення", "Межа p < 1.25 · 10¹⁵", "#475467"),
        (740, 2014, "Дораіс, Клайв (PrimeGrid)", "Розподілені мережі GPU", "Межа p < 6.7 · 10¹⁸", "#079455")
    ]

    for x, year, author, method, res, col in milestones:
        # Засічка
        p.append(circle(x, y_axis, 6, fill=col, stroke="#ffffff", sw=2))

        # Напис року
        p.append(text(x, y_axis - 18, str(year), size=13, bold=True, color=col))

        # Чергування коробок зверху/знизу
        if year in (1909, 1971, 2014):
            yb = y_axis - 90
            p.append(line(x, y_axis - 6, x, yb + 35, color=col, sw=1, dash="3,3"))
        else:
            yb = y_axis + 45
            p.append(line(x, y_axis + 6, x, yb - 5, color=col, sw=1, dash="3,3"))

        b, _, _ = textbox(x, yb, [author, method, res], size=11, pad=8, fill="#ffffff", stroke=col)
        p.append(b)

    p.append(text(W / 2, 400, "За понад століття пошуків знайдено лише ДВА числа Віферіха: 1093 та 3511", size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "search-timeline.svg"), W, H, *p, title="Хронологія пошуку простих чисел Віферіха")


if __name__ == "__main__":
    fig_wieferich_congruence()
    fig_flt_wieferich_pipeline()
    fig_search_timeline()
    print("Figures generated successfully!")
