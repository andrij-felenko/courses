# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Теорема рекурсії Кліні»."""

import os
import sys

# Шлях до спільних скриптів у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def draw_fig1():
    """Фігура 1: Парадокс нескінченного регресу та двокомпонентне розв'язання."""
    w, h = 900, 420
    frags = []

    # Заголовок блоків
    frags.append(text(220, 30, "Наївна спроба (нескінченний регрес)", size=15, bold=True, color=POS))
    frags.append(text(670, 30, "Двокомпонентна схема (Кліні / Квайн)", size=15, bold=True, color=FIELD))

    # Ліва частина: Нескінченний регрес
    frags.append(rect(20, 50, 400, 340, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    
    tb1, _, _ = textbox(220, 90, "Програма P намагається містити власний текст:\nP = \"print(\\\"\" + P + \"\\\")\"", size=12, pad=8, fill="#ffffff", stroke=POS)
    frags.append(tb1)

    tb2, _, _ = textbox(220, 160, "Рядок всередині вимагає копії рядка:\nP = \"print(\\\"print(\\\"\" + P + \"\\\")\\\")\"", size=12, pad=8, fill="#ffffff", stroke=POS)
    frags.append(tb2)

    tb3, _, _ = textbox(220, 230, "Нескінченне вкладення (довжина коду → ∞):\nP = \"print(\\\"print(\\\"print(...\\\")\\\")\\\")\"", size=12, pad=8, fill="#ffffff", stroke=POS)
    frags.append(tb3)

    tb_err, _, _ = textbox(220, 320, "Тупик: неможливо зберегти нескінченний текст\nу скінченній пам'яті комп'ютера", size=12, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(tb_err)

    # Права частина: Двокомпонентне розв'язання
    frags.append(rect(450, 50, 430, 340, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))

    tb_part_a, _, _ = textbox(550, 95, "Частина A: Дані (D)\n(Закодований текст B)", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_part_a)

    tb_part_b, _, _ = textbox(770, 95, "Частина B: Алгоритм-конструктор\n(Форматує та дублює)", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_part_b)

    frags.append(arrow(550, 130, 610, 175, color=FIELD, sw=1.8))
    frags.append(arrow(770, 130, 710, 175, color=FIELD, sw=1.8))

    tb_exec, _, _ = textbox(665, 225, "Виконання алгоритму B над даними D:\n1. Друкує B як виконуваний код\n2. Друкує D як закодовані дані\n3. Відтворює повний вихідний код P", size=12, pad=10, fill="#ffffff", stroke=FIELD)
    frags.append(tb_exec)

    tb_ok, _, _ = textbox(665, 320, "Результат: скінченний код відновлює сам себе\nбез регресу через подвійне використання даних", size=11, pad=8, fill="#e8f5e9", stroke=FIELD, color=FIELD, bold=True)
    frags.append(tb_ok)

    render(os.path.join(IMG_DIR, "fig1-self-reference-paradox.svg"), w, h, *frags)


def draw_fig2():
    """Фігура 2: Механізм s-m-n теореми (спеціалізація параметрів)."""
    w, h = 880, 360
    frags = []

    # Вхідна функція двох аргументів
    frags.append(rect(20, 40, 240, 180, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(140, 65, "Програма φ[e]", size=14, bold=True))
    frags.append(text(140, 90, "Приймає 2 параметри: (x, y)", size=12, color=MUTED))
    
    frags.append(textbox(140, 145, "Обчислення:\nz = φ[e](x, y)", size=13, pad=8, fill="#ffffff", stroke=LINE)[0])

    # Входи
    frags.append(arrow(5, 130, 20, 130, color=LINE, sw=1.8))
    frags.append(text(12, 120, "x", size=12, bold=True))
    frags.append(arrow(5, 160, 20, 160, color=LINE, sw=1.8))
    frags.append(text(12, 150, "y", size=12, bold=True))

    # Центральний блок s-m-n
    frags.append(rect(300, 40, 250, 180, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(425, 65, "s-m-n конструктор s(e, x)", size=14, bold=True, color=NEG))
    frags.append(textbox(425, 115, "Алгоритмічне «вшивання»\nконстанти x у тіло\nпрограми з номером e", size=12, pad=6, fill="#ffffff", stroke=NEG)[0])
    frags.append(textbox(425, 180, "Новий індекс: e' = s(e, x)", size=12, pad=6, fill="#dbeafe", stroke=NEG, color=NEG, bold=True)[0])

    frags.append(arrow(260, 130, 300, 130, color=NEG, sw=1.8))
    frags.append(text(280, 118, "e, x", size=12, bold=True, color=NEG))

    # Вихідна спеціалізована одномісна функція
    frags.append(rect(590, 40, 250, 180, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(715, 65, "Програма φ[e'] = φ[s(e, x)]", size=14, bold=True, color=FIELD))
    frags.append(text(715, 90, "Приймає 1 параметр: y", size=12, color=MUTED))
    frags.append(textbox(715, 145, "Обчислення:\nz = φ[s(e, x)](y)", size=13, pad=8, fill="#ffffff", stroke=FIELD)[0])

    frags.append(arrow(550, 130, 590, 130, color=FIELD, sw=1.8))
    frags.append(text(570, 118, "e'", size=12, bold=True, color=FIELD))

    # Підсумкова еквівалентність
    tb_eq, _, _ = textbox(430, 290, "Фундаментальна тотожність s-m-n теореми:\n∀x ∀y ( φ[s(e, x)](y) ≡ φ[e](x, y) )", size=13, pad=12, fill="#f8fafc", stroke=LINE, bold=True)
    frags.append(tb_eq)

    render(os.path.join(IMG_DIR, "fig2-s-m-n-mechanics.svg"), w, h, *frags)


def draw_fig3():
    """Фігура 3: Конструкція нерухомої точки Кліні."""
    w, h = 880, 400
    frags = []

    # Крок 1: Трансформація f
    frags.append(rect(20, 35, 240, 135, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(140, 60, "1. Довільне перетворення f", size=13, bold=True, color="#d97706"))
    frags.append(textbox(140, 115, "Обчислювана функція f : ℕ → ℕ\nПеретворює код однієї\nпрограми на код іншої", size=11, pad=6, fill="#ffffff", stroke="#d97706")[0])

    # Крок 2: Допоміжна функція u(v, x)
    frags.append(rect(300, 35, 260, 135, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(430, 60, "2. Побудова u(v, x)", size=13, bold=True, color=NEG))
    frags.append(textbox(430, 115, "u(v, x) = φ[f(s(v, v))](x)\nОбчислює s-m-n діагональ s(v, v),\nзастосовує f та виконує код", size=11, pad=6, fill="#ffffff", stroke=NEG)[0])

    frags.append(arrow(260, 102, 300, 102, color=LINE, sw=1.8))

    # Крок 3: Індекс v0
    frags.append(rect(600, 35, 240, 135, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, rx=8))
    frags.append(text(720, 60, "3. Фіксація індексу v₀", size=13, bold=True, color="#7c3aed"))
    frags.append(textbox(720, 115, "Оскільки u(v, x) обчислювана,\nвона має фіксований номер v₀:\nφ[v₀](v, x) ≡ u(v, x)", size=11, pad=6, fill="#ffffff", stroke="#7c3aed")[0])

    frags.append(arrow(560, 102, 600, 102, color=LINE, sw=1.8))

    # Крок 4: Діагоналізація e* = s(v0, v0)
    frags.append(rect(160, 200, 540, 80, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(430, 225, "4. Діагональний крок: покладаємо e* = s(v₀, v₀)", size=14, bold=True, color=FIELD))
    frags.append(text(430, 255, "Індекс e* спеціалізує функцію v₀ її власним номером v₀", size=12, color=INK))

    frags.append(arrow(720, 170, 560, 200, color=FIELD, sw=1.8))

    # Крок 5: Ланцюг тотожностей
    tb_chain, _, _ = textbox(430, 340, "Ланцюг тотожностей доведення:\nφ[e*](x) ≡ φ[s(v₀, v₀)](x) ≡ φ[v₀](v₀, x) ≡ u(v₀, x) ≡ φ[f(s(v₀, v₀))](x) ≡ φ[f(e*)](x)", size=12, pad=10, fill="#f8fafc", stroke=LINE, bold=True)
    frags.append(tb_chain)

    render(os.path.join(IMG_DIR, "fig3-kleene-fixed-point-construction.svg"), w, h, *frags)


def draw_fig4():
    """Фігура 4: Доведення теореми Райса через теорему рекурсії."""
    w, h = 880, 360
    frags = []

    # Припущення від супротивного
    frags.append(rect(20, 30, 390, 140, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(215, 55, "Припущення: семантична властивість P розв'язна", size=12, bold=True, color=POS))
    frags.append(textbox(215, 110, "Існує класифікатор D(e):\nD(e) = 1, якщо φ[e] ∈ P\nD(e) = 0, якщо φ[e] ∉ P", size=12, pad=8, fill="#ffffff", stroke=POS)[0])

    # Побудова перетворювача-інвертора f(e)
    frags.append(rect(450, 30, 410, 140, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(655, 55, "Конструкція інвертора коду f(e)", size=12, bold=True, color=NEG))
    frags.append(textbox(655, 110, "Нехай a ∈ P, b ∉ P (властивість нетривіальна).\nf(e) = b, якщо D(e) = 1 (тобто φ[e] ∈ P)\nf(e) = a, якщо D(e) = 0 (тобто φ[e] ∉ P)", size=12, pad=8, fill="#ffffff", stroke=NEG)[0])

    frags.append(arrow(410, 100, 450, 100, color=NEG, sw=1.8))

    # Застосування теореми рекурсії
    frags.append(rect(100, 195, 680, 65, fill="#f5f3ff", stroke="#7c3aed", sw=1.8, rx=8))
    frags.append(text(440, 220, "Застосування теореми рекурсії Кліні", size=13, bold=True, color="#7c3aed"))
    frags.append(text(440, 245, "Існує нерухома точка e*: програма e* та f(e*) обчислюють однакову функцію: φ[e*] ≡ φ[f(e*)]", size=12, color=INK))

    frags.append(arrow(655, 170, 540, 195, color="#7c3aed", sw=1.8))

    # Протиріччя
    tb_contra, _, _ = textbox(440, 310, "Неминуче логічне протиріччя:\nφ[e*] ∈ P ⇔ D(e*) = 1 ⇒ f(e*) = b ⇒ φ[f(e*)] ∉ P (але ж φ[e*] ≡ φ[f(e*)])!\nОтже, алгоритмічного класифікатора D(e) не існує.", size=11, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(tb_contra)

    render(os.path.join(IMG_DIR, "fig4-rice-via-kleene.svg"), w, h, *frags)


if __name__ == "__main__":
    draw_fig1()
    draw_fig2()
    draw_fig3()
    draw_fig4()
    print("All figures generated successfully.")
