# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Ґеделя про неповноту» (book/algorithms/complexity-computability/godel-incompleteness)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_hilbert_vs_godel():
    """fig1-hilbert-vs-godel.svg: Парадигма Гільберта проти реальності Ґеделя."""
    W, H = 880, 420
    frags = []

    # Рамка фон
    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Формалізм Гільберта (1900) проти Теорем Ґеделя (1931)", size=16, bold=True, color="#1e293b"))

    # Лівий блок: Програма Гільберта
    frags.append(rect(30, 60, 395, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(227, 88, "Програма Давида Гільберта (1900–1928)", size=14, bold=True, color=BLUE_S))

    h_items = [
        ("1. Повнота (Completeness)", "Кожне істинне твердження T має доведення: A ⊢ T"),
        ("2. Несуперечливість (Consistency)", "Теорія не здатна вивести суперечність: A ⊬ (0 = 1)"),
        ("3. Розв'язність (Entscheidungsproblem)", "Існує алгоритм перевірки довідності будь-якої формули")
    ]
    y_pos = 125
    for title, desc in h_items:
        b, _, _ = textbox(227, y_pos + 12, title, size=12, pad=6, fill="#ffffff", stroke=BLUE_S)
        frags.append(b)
        frags.append(text(227, y_pos + 42, desc, size=11, color="#334155"))
        y_pos += 75

    # Правий блок: Відкриття Ґеделя
    frags.append(rect(455, 60, 395, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(652, 88, "Реальність: Теореми Ґеделя (1931)", size=14, bold=True, color=RED_S))

    g_items = [
        ("1-ша Теорема про неповноту", "Існують істинні арифметичні речення G, недоведені у F"),
        ("2-га Теорема про неповноту", "Сумісність теорії Consis(F) не доводиться засобами F"),
        ("Алгоритмічний наслідок", "Проблема зупинки Тюринга нерозв'язна; верифікатор обмежений")
    ]
    y_pos = 125
    for title, desc in g_items:
        b, _, _ = textbox(652, y_pos + 12, title, size=12, pad=6, fill="#ffffff", stroke=RED_S)
        frags.append(b)
        frags.append(text(652, y_pos + 42, desc, size=11, color="#334155"))
        y_pos += 75

    render(os.path.join(IMG, "fig1-hilbert-vs-godel.svg"), W, H, *frags)

def fig_godel_numbering():
    """fig2-godel-numbering.svg: Арифметизація синтаксису (Кодування Ґеделя)."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Конвеєр арифметизації синтаксису (Кодування Ґеделя)", size=16, bold=True, color="#1e293b"))

    # Крок 1: Логічна формула / Синтаксис
    b1, _, _ = textbox(130, 100, "1. Логічна формула φ\n¬ ∃ x (x = S(0))", size=11, pad=10, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b1)

    # Стрелка 1 -> 2
    frags.append(arrow(220, 100, 270, 100, color=PURPLE_S, sw=2))

    # Крок 2: Токени та базові коди
    b2, _, _ = textbox(400, 100, "2. Алфавітний код символів\n¬ → 1, ∃ → 2, x → 3, ( → 4...", size=11, pad=10, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b2)

    # Стрелка 2 -> 3
    frags.append(arrow(530, 100, 580, 100, color=TEAL_S, sw=2))

    # Крок 3: Піднесення простих чисел
    b3, _, _ = textbox(730, 100, "3. Прості числа pₖ\np₁=2, p₂=3, p₃=5, p₄=7...", size=11, pad=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b3)

    # Стрелка вниз до обчислення
    frags.append(arrow(440, 150, 440, 200, color="#475569", sw=2))

    # Крок 4: Степеновий добуток
    frags.append(rect(100, 210, 680, 80, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 235, "Обчислення Ґеделевого номера формули: g = ┌φ┐ = p₁ˢ¹ · p₂ˢ² · p₃ˢ³ · ... · pₖˢᵏ", size=13, bold=True, color="#0f172a"))
    frags.append(text(440, 265, "Приклад: ┌ ¬ ∃ x ┐ = 2¹ · 3² · 5³ = 2 · 9 · 125 = 2250 ∈ ℕ", size=12, color=BLUE_S, bold=True))

    # Стрелка вниз до властивості унікальності
    frags.append(arrow(440, 290, 440, 330, color="#475569", sw=2))

    # Крок 5: Унікальне число та декодування
    b5, _, _ = textbox(440, 370, "4. Основна теорема арифметики (Унікальна розкладність на прості множники)\nВизначення формули з числа g та алгоритмічна перевірка доведень Prov(x, y)", size=11, pad=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b5)

    render(os.path.join(IMG, "fig2-godel-numbering.svg"), W, H, *frags)

def fig_diagonalization_fixedpoint():
    """fig3-diagonalization-fixedpoint.svg: Лема про нерухому точку та діагоналізація."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Конструкція діагонального підставлення (Лема про нерухому точку)", size=16, bold=True, color="#1e293b"))

    # Блок ліворуч: Препредикат
    frags.append(rect(40, 70, 360, 140, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(220, 95, "Предикат P(v) з вільною змінною v", size=13, bold=True, color=AMBER_S))
    frags.append(text(220, 125, "Приклад: ¬Prov(v) (недовідність)", size=12, color="#334155"))
    frags.append(text(220, 155, "Предикат описує властивість номеру формули v", size=11, color="#64748b"))

    # Блок праворуч: Функція підставлення
    frags.append(rect(480, 70, 360, 140, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(660, 95, "Функція діагоналізації sub(x)", size=13, bold=True, color=PURPLE_S))
    frags.append(text(660, 125, "sub(┌A(v)┐) = ┌A(┌A(v)┐)┐", size=12, color="#334155"))
    frags.append(text(660, 155, "Підставляє номер формули замість її вільної змінної", size=11, color="#64748b"))

    # Стрелки між верхом і центром
    frags.append(arrow(220, 210, 360, 250, color=AMBER_S, sw=2))
    frags.append(arrow(660, 210, 520, 250, color=PURPLE_S, sw=2))

    # Центральний блок: Діагональна формула D(v)
    frags.append(rect(240, 250, 400, 70, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(440, 275, "Діагоналізована формула D(v) ≡ P(sub(v))", size=13, bold=True, color=BLUE_S))
    frags.append(text(440, 300, "Фіксуємо її Ґеделів номер: d = ┌D(v)┐", size=11, color="#334155"))

    # Стрелка від центра внизу до кінцевого речення G
    frags.append(arrow(440, 320, 440, 350, color=BLUE_S, sw=2))

    # Нижній блок: Фіксована точка G
    b_g, _, _ = textbox(440, 385, "Речення Ґеделя: G ≡ D(d) ≡ P(sub(d))\nОтже: PA ⊢ G ↔ P(┌G┐)    ⇒    PA ⊢ G ↔ ¬Prov(┌G┐)", size=11, pad=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_g)

    render(os.path.join(IMG, "fig3-diagonalization-fixedpoint.svg"), W, H, *frags)

def fig_incompleteness_halting_bridge():
    """fig4-incompleteness-halting-bridge.svg: Еквівалентність неповноти Ґеделя, проблема зупинки Тюринга та Колмогоров."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Тріада алгоритмічної та формальної нерозв'язності", size=16, bold=True, color="#1e293b"))

    # 1. Логічний полюс (Ґедель)
    frags.append(rect(30, 70, 255, 320, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(157, 95, "Логічна неповнота\n(Ґедель, 1931)", size=13, bold=True, color=PURPLE_S))
    b_g, _, _ = textbox(157, 160, "Речення G:\n\"G недовідне в PA\"", size=11, pad=8, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_g)
    frags.append(text(157, 230, "Причина:\nСамореференція\nчерез кодування", size=11, color="#334155"))
    frags.append(text(157, 330, "Наслідок:\nPA ⊬ G i PA ⊬ ¬G\n(Синтаксична неповнота)", size=11, bold=True, color=PURPLE_S))

    # 2. Обчислювальний полюс (Тюринг)
    frags.append(rect(312, 70, 255, 320, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(439, 95, "Алгоритмічна нерозв'язність\n(Тюринг, 1936)", size=13, bold=True, color=BLUE_S))
    b_t, _, _ = textbox(439, 160, "Проблема зупинки:\nH(M, w) - чи зупиниться M?", size=11, pad=8, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_t)
    frags.append(text(439, 230, "Причина:\nДіагоналізація\nпарадоксу заперечення", size=11, color="#334155"))
    frags.append(text(439, 330, "Наслідок:\nНе існує загального\nалгоритму верифікації", size=11, bold=True, color=BLUE_S))

    # 3. Інформаційний полюс (Колмогоров / Чейтін)
    frags.append(rect(595, 70, 255, 320, fill=TEAL_F, stroke=TEAL_S, sw=1.5, rx=8))
    frags.append(text(722, 95, "Інформаційна межа\n(Колмогоров/Чейтін, 1965)", size=13, bold=True, color=TEAL_S))
    b_k, _, _ = textbox(722, 160, "Складність K(x):\nДовжина найкоротшої прог.", size=11, pad=8, fill="#ffffff", stroke=TEAL_S)
    frags.append(b_k)
    frags.append(text(722, 230, "Причина:\nТеорія F не опише\nскладніші об'єкти за K(F)", size=11, color="#334155"))
    frags.append(text(722, 330, "Наслідок:\nБільшість чисел випадкові,\nале довести це неможливо", size=11, bold=True, color=TEAL_S))

    # Горизонтальні зв'язки
    frags.append(arrow(285, 160, 312, 160, color="#64748b", sw=1.5))
    frags.append(arrow(567, 160, 595, 160, color="#64748b", sw=1.5))

    render(os.path.join(IMG, "fig4-incompleteness-halting-bridge.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_hilbert_vs_godel()
    fig_godel_numbering()
    fig_diagonalization_fixedpoint()
    fig_incompleteness_halting_bridge()
    print("Всі фігури успішно згенеровано у img/")
