# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми vector-clocks-vs-crdt."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_vector_clock_causality():
    """Фігура 1: Відстеження причинності за допомогою векторних годинників та виявлення паралелізму."""
    w, h = 820, 430
    body = rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1)

    # Заголовок зверху
    b_title, _, _ = textbox(410, 30, "Відстеження причинності векторними годинниками (3 вузли: A, B, C)", size=16, bold=True, fill="#eef2f7", stroke="#2457d6")
    body += b_title

    # Горизонтальні осі часу для вузлів A, B, C
    y_a = 100
    y_b = 205
    y_c = 310

    # Підписи вузлів зліва
    body += rect(20, y_a - 20, 85, 40, fill="#f4f6f8", stroke=LINE, sw=1.5)
    body += text(62, y_a + 5, "Вузол A", size=14, bold=True, color=INK)

    body += rect(20, y_b - 20, 85, 40, fill="#f4f6f8", stroke=LINE, sw=1.5)
    body += text(62, y_b + 5, "Вузол B", size=14, bold=True, color=INK)

    body += rect(20, y_c - 20, 85, 40, fill="#f4f6f8", stroke=LINE, sw=1.5)
    body += text(62, y_c + 5, "Вузол C", size=14, bold=True, color=INK)

    # Лінії часу (стрілки праворуч)
    body += arrow(115, y_a, 780, y_a, color=MUTED, sw=1.5)
    body += arrow(115, y_b, 780, y_b, color=MUTED, sw=1.5)
    body += arrow(115, y_c, 780, y_c, color=MUTED, sw=1.5)

    # Події на вузлі A
    # Початковий стан e_a0: [0,0,0]
    body += circle(150, y_a, 6, fill="#2457d6", stroke=LINE)
    b_a0, _, _ = textbox(150, y_a - 30, "e₀: [0, 0, 0]", size=12, fill="#f0f4fc", stroke="#2457d6")
    body += b_a0

    # Подія e_a1: локальний запис [1, 0, 0]
    body += circle(280, y_a, 6, fill="#27ae60", stroke=LINE)
    b_a1, _, _ = textbox(280, y_a - 30, "e₁: [1, 0, 0]\n(запис на A)", size=12, fill="#eefaf1", stroke="#27ae60")
    body += b_a1

    # Подія на вузлі B: отримання повідомлення від A
    # Початковий стан на B: [0,0,0]
    body += circle(150, y_b, 6, fill="#2457d6", stroke=LINE)
    b_b0, _, _ = textbox(150, y_b - 30, "[0, 0, 0]", size=12, fill="#f0f4fc", stroke="#2457d6")
    body += b_b0

    # Стрілка надсилання повідомлення від A до B
    body += arrow(280, y_a + 6, 440, y_b - 6, color="#2457d6", sw=2)
    b_msg, _, _ = textbox(365, 148, "msg: [1, 0, 0]", size=11, bold=True, fill="#ffffff", stroke="#2457d6")
    body += b_msg

    # Подія e_b1: отримання повідомлення на B + локальний крок
    body += circle(440, y_b, 6, fill="#27ae60", stroke=LINE)
    b_b1, _, _ = textbox(440, y_b + 32, "e₂: [1, 1, 0]\n(max + tick B)", size=12, fill="#eefaf1", stroke="#27ae60")
    body += b_b1

    # Події на вузлі C: локальний запис без отримання повідомлень
    # Початковий стан на C: [0,0,0]
    body += circle(150, y_c, 6, fill="#2457d6", stroke=LINE)
    b_c0, _, _ = textbox(150, y_c - 30, "[0, 0, 0]", size=12, fill="#f0f4fc", stroke="#2457d6")
    body += b_c0

    # Локальний запис на C: e_c1
    body += circle(440, y_c, 6, fill="#c0392b", stroke=LINE)
    b_c1, _, _ = textbox(440, y_c + 32, "e₃: [0, 0, 1]\n(запис на C)", size=12, fill="#fdecea", stroke="#c0392b")
    body += b_c1

    # Порівняльний блок праворуч
    body += rect(560, 80, 230, 290, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8)
    body += text(675, 105, "Матриця відношень", size=14, bold=True, color=INK)
    body += line(575, 118, 775, 118, color=MUTED, sw=1)

    # Причинна залежність
    body += text(675, 140, "1. Причинний зв'язок (e₁ → e₂):", size=12, bold=True, color="#2457d6")
    body += text(675, 160, "[1, 0, 0] ≤ [1, 1, 0] (A ≤ B)", size=12, color=INK)
    body += text(675, 180, "Подія e₁ спричинила e₂", size=11, italic=True, color=MUTED)

    body += line(575, 195, 775, 195, color="#e0e0e0", sw=1)

    # Конкурентність / Конфлікт
    body += text(675, 220, "2. Конкурентність (e₂ ∥ e₃):", size=12, bold=True, color="#c0392b")
    body += text(675, 240, "[1, 1, 0] ≰ [0, 0, 1]", size=12, color=INK)
    body += text(675, 260, "[0, 0, 1] ≰ [1, 1, 0]", size=12, color=INK)
    body += text(675, 285, "Конфлікт гілок!", size=12, bold=True, color="#c0392b")
    body += text(675, 305, "Потрібне злиття на рівні", size=11, color=MUTED)
    body += text(675, 322, "застосунку або CRDT", size=11, color=MUTED)

    # Нижній висновок
    body += rect(20, 375, 520, 42, fill="#fff9db", stroke="#f59f00", sw=1.2, rx=6)
    body += text(280, 400, "Векторний годинник виявляє конфлікт e₂ ∥ e₃, але не вміє його злити сам", size=12, bold=True, color="#7d5a00")

    render(os.path.join(OUT_DIR, 'vector-clock-causality.svg'), w, h, body)


def fig_crdt_semilattice_merge():
    """Фігура 2: Об'єднавча напівґратка (Join-Semilattice) та монотонне злиття станів."""
    w, h = 820, 440
    body = rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1)

    b_title, _, _ = textbox(410, 30, "Об'єднавча напівґратка (Join-Semilattice) у CvRDT", size=16, bold=True, fill="#eef2f7", stroke="#2457d6")
    body += b_title

    # Діаграма Хассе напівґратки (Hasse diagram)
    # Нижній елемент (Bottom ⊥)
    cx_bot, cy_bot = 230, 360
    b_bot, _, _ = textbox(cx_bot, cy_bot, "Початковий стан ⊥\ns₀ = { A: 0, B: 0 }", size=12, fill="#f4f6f8", stroke=LINE)
    body += b_bot

    # Ліва гілка (State s1 на вузлі A)
    cx_left, cy_left = 120, 210
    b_left, _, _ = textbox(cx_left, cy_left, "Вузол A: стан s₁\n{ A: 3, B: 1 }", size=13, bold=True, fill="#eefaf1", stroke="#27ae60")
    body += b_left

    # Права гілка (State s2 на вузлі B)
    cx_right, cy_right = 340, 210
    b_right, _, _ = textbox(cx_right, cy_right, "Вузол B: стан s₂\n{ A: 1, B: 4 }", size=13, bold=True, fill="#f0f4fc", stroke="#2457d6")
    body += b_right

    # Верхній елемент (Least Upper Bound ⊔)
    cx_top, cy_top = 230, 80
    b_top, _, _ = textbox(cx_top, cy_top, "Точна верхня межа (LUB)\ns₁ ⊔ s₂ = { A: max(3,1), B: max(1,4) }\n= { A: 3, B: 4 }", size=13, bold=True, fill="#fff9db", stroke="#f59f00")
    body += b_top

    # Стрілки часткового порядку ⊑
    body += arrow(cx_bot - 40, cy_bot - 25, cx_left + 20, cy_left + 25, color="#27ae60", sw=2)
    body += text(125, 305, "s₀ ⊑ s₁", size=12, bold=True, color="#27ae60")

    body += arrow(cx_bot + 40, cy_bot - 25, cx_right - 20, cy_left + 25, color="#2457d6", sw=2)
    body += text(335, 305, "s₀ ⊑ s₂", size=12, bold=True, color="#2457d6")

    body += arrow(cx_left + 30, cy_left - 25, cx_top - 40, cy_top + 32, color=LINE, sw=2)
    body += text(130, 135, "s₁ ⊑ (s₁ ⊔ s₂)", size=12, bold=True, color=INK)

    body += arrow(cx_right - 30, cy_right - 25, cx_top + 40, cy_top + 32, color=LINE, sw=2)
    body += text(330, 135, "s₂ ⊑ (s₁ ⊔ s₂)", size=12, bold=True, color=INK)

    # Правий блок: Алгебраїчні аксіоми збіжності
    body += rect(470, 60, 330, 350, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8)
    body += text(635, 88, "Алгебраїчні закони злиття (⊔)", size=14, bold=True, color=INK)
    body += line(485, 102, 785, 102, color=MUTED, sw=1)

    # Комутативність
    body += text(500, 125, "1. Комутативність (Commutativity):", size=12, bold=True, color="#2457d6", anchor="start")
    body += text(520, 145, "x ⊔ y = y ⊔ x", size=13, color=INK, anchor="start")
    body += text(520, 163, "Порядок прибуття пакетів не має значення", size=11, italic=True, color=MUTED, anchor="start")

    # Асоціативність
    body += text(500, 195, "2. Асоціативність (Associativity):", size=12, bold=True, color="#2457d6", anchor="start")
    body += text(520, 215, "(x ⊔ y) ⊔ z = x ⊔ (y ⊔ z)", size=13, color=INK, anchor="start")
    body += text(520, 233, "Групування пакетів не впливає на результат", size=11, italic=True, color=MUTED, anchor="start")

    # Ідемпотентність
    body += text(500, 265, "3. Ідемпотентність (Idempotence):", size=12, bold=True, color="#2457d6", anchor="start")
    body += text(520, 285, "x ⊔ x = x", size=13, color=INK, anchor="start")
    body += text(520, 303, "Дублікати повідомлень та повтори безпечні", size=11, italic=True, color=MUTED, anchor="start")

    # Підсумок монотонності
    body += line(485, 325, 785, 325, color="#e0e0e0", sw=1)
    body += text(500, 348, "Монотонне зростання:", size=12, bold=True, color="#27ae60", anchor="start")
    body += text(500, 370, "Стан системи в часі лише зростає вздовж ⊑,", size=11, color=INK, anchor="start")
    body += text(500, 388, "гарантуючи детерміновану збіжність (SEC).", size=11, color=INK, anchor="start")

    render(os.path.join(OUT_DIR, 'crdt-semilattice-merge.svg'), w, h, body)


def fig_or_set_causal_lifecycle():
    """Фігура 3: Життєвий цикл елемента в Observed-Remove Set (OR-Set) та розв'язання конфлікту видалення/додавання."""
    w, h = 820, 440
    body = rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1)

    b_title, _, _ = textbox(410, 30, "Життєвий цикл елемента в Observed-Remove Set (OR-Set)", size=16, bold=True, fill="#eef2f7", stroke="#2457d6")
    body += b_title

    # Ліва колонка: Проблема простого 2P-Set (пастка надгробків)
    body += rect(20, 65, 370, 355, fill="#fdf8f8", stroke="#c0392b", sw=1.5, rx=8)
    body += text(205, 92, "Пастка простого 2P-Set (Add/Remove)", size=13, bold=True, color="#c0392b")
    body += line(35, 105, 375, 105, color="#f5c6cb", sw=1)

    b_p1, _, _ = textbox(205, 135, "1. Додавання елемента «X»\nAddSet = { «X» }, RemSet = { }", size=11, fill="#ffffff", stroke=LINE)
    body += b_p1

    body += arrow(205, 160, 205, 185, color=MUTED, sw=1.5)

    b_p2, _, _ = textbox(205, 215, "2. Видалення елемента «X»\nAddSet = { «X» }, RemSet = { «X» }\n(«X» переміщено в надгробки)", size=11, fill="#ffffff", stroke=LINE)
    body += b_p2

    body += arrow(205, 248, 205, 273, color=MUTED, sw=1.5)

    b_p3, _, _ = textbox(205, 305, "3. Спроба повторно додати «X»\nAddSet = { «X» }, RemSet = { «X» }\nСтан = AddSet \\ RemSet = ∅", size=11, fill="#fdecea", stroke="#c0392b")
    body += b_p3

    body += text(205, 370, "Помилка: елемент назавжди заблокований!", size=12, bold=True, color="#c0392b")
    body += text(205, 392, "2P-Set не дозволяє повторне додавання", size=11, italic=True, color=MUTED)

    # Права колонка: Рішення в OR-Set через причинні теги (Dots)
    body += rect(420, 65, 380, 355, fill="#f8fcf9", stroke="#27ae60", sw=1.5, rx=8)
    body += text(610, 92, "Розв'язання в OR-Set (унікальні теги / dots)", size=13, bold=True, color="#27ae60")
    body += line(435, 105, 785, 105, color="#c3e6cb", sw=1)

    b_o1, _, _ = textbox(610, 135, "1. Вузол A додає «X» із тегом t₁ = (A, 1)\nЕлементи: { («X», t₁) }", size=11, fill="#ffffff", stroke=LINE)
    body += b_o1

    body += arrow(610, 160, 610, 185, color=MUTED, sw=1.5)

    b_o2, _, _ = textbox(610, 215, "2. Вузол B бачить t₁ і видаляє «X»\nВидаляються лише спостережені теги { t₁ }\nЕлементи: ∅, Видалені теги: { t₁ }", size=11, fill="#ffffff", stroke=LINE)
    body += b_o2

    body += arrow(610, 252, 610, 277, color=MUTED, sw=1.5)

    b_o3, _, _ = textbox(610, 310, "3. Конкурентно вузол A знову додає «X»\nГенерується новий унікальний тег t₂ = (A, 2)\nЕлементи: { («X», t₂) }", size=11, fill="#eefaf1", stroke="#27ae60")
    body += b_o3

    # Підсумок злиття для OR-Set
    body += rect(435, 355, 350, 52, fill="#eefaf1", stroke="#27ae60", sw=1.2, rx=6)
    body += text(610, 375, "Результат злиття: { («X», t₂) } ∈ Стан!", size=12, bold=True, color="#27ae60")
    body += text(610, 395, "Нове додавання t₂ вижило, оскільки B видалив лише t₁", size=10, color=INK)

    render(os.path.join(OUT_DIR, 'or-set-causal-lifecycle.svg'), w, h, body)


def fig_architecture_comparison():
    """Фігура 4: Порівняння архітектурних конвеєрів: Векторні годинники vs CRDT."""
    w, h = 820, 440
    body = rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1)

    b_title, _, _ = textbox(410, 30, "Архітектурний конвеєр: Векторні годинники vs CRDT", size=16, bold=True, fill="#eef2f7", stroke="#2457d6")
    body += b_title

    # Ліва колонка: Конвеєр векторних годинників
    body += rect(20, 65, 370, 355, fill="#fcfcfc", stroke="#2457d6", sw=1.5, rx=8)
    body += text(205, 92, "Конвеєр векторних годинників (Dynamo / Riak)", size=13, bold=True, color="#2457d6")
    body += line(35, 105, 375, 105, color="#cce5ff", sw=1)

    # Кроки лівої колонки
    b_v1, _, _ = textbox(205, 130, "Клієнтський запис payload + Vector Clock\nVC = [A:1, B:0]", size=11, fill="#ffffff", stroke=LINE)
    body += b_v1
    body += arrow(205, 150, 205, 170, color=MUTED, sw=1.5)

    b_v2, _, _ = textbox(205, 192, "Реплікація та виявлення конкурентності\nVC₁ ≰ VC₂ та VC₂ ≰ VC₁ → Конфлікт (∥)", size=11, fill="#fdecea", stroke="#c0392b")
    body += b_v2
    body += arrow(205, 218, 205, 238, color=MUTED, sw=1.5)

    b_v3, _, _ = textbox(205, 265, "Розгалуження версій (Siblings explosion)\nБаза даних зберігає обидві гілки", size=11, fill="#ffffff", stroke=LINE)
    body += b_v3
    body += arrow(205, 288, 205, 308, color=MUTED, sw=1.5)

    b_v4, _, _ = textbox(205, 355, "Ручне злиття в коді застосунку\n(Клієнт або сервіс вирішує бізнес-конфлікт\nі надсилає новий спільний вектор)", size=11, bold=True, fill="#fff9db", stroke="#f59f00")
    body += b_v4

    # Права колонка: Конвеєр CRDT
    body += rect(420, 65, 380, 355, fill="#fcfcfc", stroke="#27ae60", sw=1.5, rx=8)
    body += text(610, 92, "Конвеєр CRDT (Automerge / Yjs / Redis-CRDT)", size=13, bold=True, color="#27ae60")
    body += line(435, 105, 785, 105, color="#c3e6cb", sw=1)

    # Кроки правої колонки
    b_c1, _, _ = textbox(610, 130, "Локальна монотонна мутація CRDT\n(стан переходить у новий елемент ґратки)", size=11, fill="#ffffff", stroke=LINE)
    body += b_c1
    body += arrow(610, 150, 610, 175, color=MUTED, sw=1.5)

    b_c2, _, _ = textbox(610, 200, "Асинхронне поширення стану / дельти\n(мережевий порядок пакетів довільний)", size=11, fill="#ffffff", stroke=LINE)
    body += b_c2
    body += arrow(610, 222, 610, 248, color=MUTED, sw=1.5)

    b_c3, _, _ = textbox(610, 275, "Автоматичне алгебраїчне злиття\ns_merged = s_local ⊔ s_remote", size=11, fill="#eefaf1", stroke="#27ae60")
    body += b_c3
    body += arrow(610, 298, 610, 325, color=MUTED, sw=1.5)

    b_c4, _, _ = textbox(610, 360, "Гарантована детермінована збіжність (SEC)\nНуль конфліктів для бізнес-коду,\nстан усіх реплік 100% ідентичний", size=11, bold=True, fill="#eefaf1", stroke="#27ae60")
    body += b_c4

    render(os.path.join(OUT_DIR, 'architecture-comparison.svg'), w, h, body)


if __name__ == '__main__':
    fig_vector_clock_causality()
    fig_crdt_semilattice_merge()
    fig_or_set_causal_lifecycle()
    fig_architecture_comparison()
    print("Всі 4 фігури успішно згенеровано у папку img/")
