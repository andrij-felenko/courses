# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Скалярний годинник Лампорта проти Векторного годинника ──────────
def fig_lamport_vs_vector():
    W, H = 960, 420
    p = []

    # Загальний фон
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))

    def panel(px, title, sub, is_vector):
        out = []
        pw, ph = 440.0, 360.0
        py = 30.0
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))
        out.append(text(px + pw / 2, py + 26, title, size=15, color=INK, bold=True))
        out.append(text(px + pw / 2, py + 48, sub, size=12, color=MUTED))

        # Дві часові лінії: Вузол A і Вузол B
        y_a = py + 120
        y_b = py + 220
        lx1, lx2 = px + 80, px + pw - 40

        # Підписи вузлів
        out.append(text(px + 40, y_a + 5, "Вузол A", size=13, color=INK, bold=True, anchor="middle"))
        out.append(text(px + 40, y_b + 5, "Вузол B", size=13, color=INK, bold=True, anchor="middle"))

        # Осі часу
        out.append(line(lx1, y_a, lx2, y_a, color=LINE, sw=1.8))
        out.append(arrow(lx2, y_a, lx2 + 20, y_a, color=LINE, sw=1.8))
        out.append(line(lx1, y_b, lx2, y_b, color=LINE, sw=1.8))
        out.append(arrow(lx2, y_b, lx2 + 20, y_b, color=LINE, sw=1.8))

        # Події e1 на A і e2 на B (конкурентні, без обміну)
        ev_x1 = px + 160
        ev_x2 = px + 300

        out.append(circle(ev_x1, y_a, 6, fill="#ffffff", stroke=POS, sw=2.5))
        out.append(text(ev_x1, y_a - 14, "подія a", size=12, color=INK, bold=True))

        out.append(circle(ev_x2, y_b, 6, fill="#ffffff", stroke=NEG, sw=2.5))
        out.append(text(ev_x2, y_b - 14, "подія b", size=12, color=INK, bold=True))

        if not is_vector:
            # Лампорт: мітки часу L(a)=1, L(b)=1 (або tie-break 1 < 2)
            tb1, _, _ = textbox(ev_x1, y_a + 28, "L(a) = 1", size=12, pad=5, fill="#fff2f0", stroke=POS, color=POS, bold=True)
            tb2, _, _ = textbox(ev_x2, y_b + 28, "L(b) = 2", size=12, pad=5, fill="#edf2ff", stroke=NEG, color=NEG, bold=True)
            out.append(tb1)
            out.append(tb2)

            res_box = fitbox(px + 20, py + 280, pw - 40, 60,
                             "L(a) < L(b) створює хибну ілюзію порядку:\nсистема вважає a → b, хоча події насправді паралельні!",
                             size=11.5, fill="#fff5f5", stroke=POS, color=POS, bold=True)
            out.append(res_box)
        else:
            # Вектор: V(a)=(1, 0), V(b)=(0, 1)
            tb1, _, _ = textbox(ev_x1, y_a + 28, "V(a) = [1, 0]", size=12, pad=5, fill="#fff2f0", stroke=POS, color=POS, bold=True)
            tb2, _, _ = textbox(ev_x2, y_b + 28, "V(b) = [0, 1]", size=12, pad=5, fill="#edf2ff", stroke=NEG, color=NEG, bold=True)
            out.append(tb1)
            out.append(tb2)

            res_box = fitbox(px + 20, py + 280, pw - 40, 60,
                             "V(a) ≰ V(b) і V(b) ≰ V(a) — вектори непорівнянні.\nСистема строго фіксує паралельність: a ∥ b.",
                             size=11.5, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=True)
            out.append(res_box)

        return out

    p.extend(panel(30, "Скалярний годинник Лампорта", "Створює лінійний штучний порядок", False))
    p.extend(panel(490, "Векторний годинник", "Зберігає істинний частковий порядок", True))

    render(os.path.join(OUT, "lamport-vs-vector.svg"), W, H, *p,
           title="Порівняння скалярного годинника Лампорта та векторного годинника")


# ── Фіг. 2: Правила поширення та оновлення векторного годинника ────────────
def fig_vector_clock_flow():
    W, H = 960, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))

    # Заголовок
    p.append(text(W / 2, 28, "Поширення векторного годинника між трьома вузлами", size=16, color=INK, bold=True))

    y_a = 90
    y_b = 230
    y_c = 370
    lx1, lx2 = 120, 880

    p.append(text(60, y_a + 5, "Вузол A", size=14, color=INK, bold=True))
    p.append(text(60, y_b + 5, "Вузол B", size=14, color=INK, bold=True))
    p.append(text(60, y_c + 5, "Вузол C", size=14, color=INK, bold=True))

    p.append(line(lx1, y_a, lx2, y_a, color=LINE, sw=1.8))
    p.append(arrow(lx2, y_a, lx2 + 20, y_a, color=LINE, sw=1.8))
    p.append(line(lx1, y_b, lx2, y_b, color=LINE, sw=1.8))
    p.append(arrow(lx2, y_b, lx2 + 20, y_b, color=LINE, sw=1.8))
    p.append(line(lx1, y_c, lx2, y_c, color=LINE, sw=1.8))
    p.append(arrow(lx2, y_c, lx2 + 20, y_c, color=LINE, sw=1.8))

    # Подія 1: A генерує подію (1,0,0)
    x1 = 190
    p.append(circle(x1, y_a, 6, fill="#ffffff", stroke=POS, sw=2.5))
    tb1, _, _ = textbox(x1, y_a - 24, "a₁: [1, 0, 0]", size=11.5, pad=4, fill="#fff5f5", stroke=POS, color=POS, bold=True)
    p.append(tb1)

    # Повідомлення від A до B
    x2 = 340
    p.append(arrow(x1, y_a, x2, y_b, color=POS, sw=2))
    p.append(circle(x2, y_b, 6, fill="#ffffff", stroke=NEG, sw=2.5))
    tb2, _, _ = textbox(x2, y_b + 28, "b₁: max + інкр. B\n[1, 1, 0]", size=11, pad=4, fill="#edf2ff", stroke=NEG, color=NEG, bold=True)
    p.append(tb2)

    # Подія на B: локальна подія b2 (1,2,0)
    x3 = 480
    p.append(circle(x3, y_b, 6, fill="#ffffff", stroke=NEG, sw=2.5))
    tb3, _, _ = textbox(x3, y_b - 24, "b₂: [1, 2, 0]", size=11.5, pad=4, fill="#edf2ff", stroke=NEG, color=NEG, bold=True)
    p.append(tb3)

    # Повідомлення від B до C
    x4 = 660
    p.append(arrow(x3, y_b, x4, y_c, color=NEG, sw=2))
    p.append(circle(x4, y_c, 6, fill="#ffffff", stroke=FIELD, sw=2.5))
    tb4, _, _ = textbox(x4, y_c + 28, "c₁: max + інкр. C\n[1, 2, 1]", size=11, pad=4, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=True)
    p.append(tb4)

    # Одночасна подія a2 на A (без зв'язку з B і C)
    x5 = 600
    p.append(circle(x5, y_a, 6, fill="#ffffff", stroke=POS, sw=2.5))
    tb5, _, _ = textbox(x5, y_a - 24, "a₂: [2, 0, 0]", size=11.5, pad=4, fill="#fff5f5", stroke=POS, color=POS, bold=True)
    p.append(tb5)

    # Пояснювальний блок знизу
    p.append(fitbox(120, 420, 760, 48,
                    "Порівняння станів: a₁ → b₁ → b₂ → c₁ (причинний ланцюг). "
                    "Паралельність: a₂ ∥ b₂, a₂ ∥ c₁ (жоден вектор не переважає інший).",
                    size=12, fill="#f8fafc", stroke=LINE, color=INK, bold=True))

    render(os.path.join(OUT, "vector-clock-flow.svg"), W, H, *p,
           title="Поширення векторного годинника між процесами")


# ── Фіг. 3: Буфер причинної доставки (Causal Delivery Buffer) ───────────────
def fig_causal_delivery():
    W, H = 960, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))
    p.append(text(W / 2, 26, "Механізм буфера причинної доставки повідомлень", size=16, color=INK, bold=True))

    # Сценарій: 3 вузли. Вузол 1 посилає m1 (1,0,0) Вузлу 2 і Вузлу 3.
    # Вузол 2 отримує m1, створює m2 (1,1,0) і шле Вузлу 3.
    # Через затримку в мережі m2 доходить до Вузла 3 РАНІШЕ за m1!
    y1, y2, y3 = 80, 200, 320
    lx1, lx2 = 100, 560

    p.append(text(50, y1 + 5, "Вузол 1", size=13, color=INK, bold=True))
    p.append(text(50, y2 + 5, "Вузол 2", size=13, color=INK, bold=True))
    p.append(text(50, y3 + 5, "Вузол 3", size=13, color=INK, bold=True))

    p.append(line(lx1, y1, lx2, y1, color=LINE, sw=1.8))
    p.append(arrow(lx2, y1, lx2 + 20, y1, color=LINE, sw=1.8))
    p.append(line(lx1, y2, lx2, y2, color=LINE, sw=1.8))
    p.append(arrow(lx2, y2, lx2 + 20, y2, color=LINE, sw=1.8))
    p.append(line(lx1, y3, lx2, y3, color=LINE, sw=1.8))
    p.append(arrow(lx2, y3, lx2 + 20, y3, color=LINE, sw=1.8))

    # Вузол 1 відправляє m1
    p.append(circle(140, y1, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(140, y1 - 14, "m₁ [1, 0, 0]", size=11, color=POS, bold=True))

    # m1 до Вузла 2 (швидкий канал)
    p.append(arrow(140, y1, 240, y2, color=POS, sw=1.8))
    p.append(circle(240, y2, 5, fill="#ffffff", stroke=POS, sw=2))

    # Вузол 2 відправляє m2
    p.append(circle(300, y2, 5, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(300, y2 - 14, "m₂ [1, 1, 0]", size=11, color=NEG, bold=True))

    # m2 приходить на Вузол 3 (швидко)
    p.append(arrow(300, y2, 380, y3, color=NEG, sw=1.8))
    p.append(circle(380, y3, 6, fill="#ffebee", stroke=POS, sw=2.5))
    p.append(text(380, y3 + 20, "m₂ прибуло", size=11, color=POS, bold=True))

    # m1 приходить на Вузол 3 (повільно)
    p.append(line(140, y1, 480, y3, color=POS, sw=1.8, dash="4,4"))
    p.append(arrow(480, y3 - 10, 500, y3, color=POS, sw=1.8))
    p.append(circle(500, y3, 6, fill="#e8f5e9", stroke=FIELD, sw=2.5))
    p.append(text(500, y3 + 20, "m₁ прибуло", size=11, color=FIELD, bold=True))

    # Панель праворуч: Буфер вузла 3
    bx, by, bw, bh = 610, 70, 320, 330
    p.append(rect(bx, by, bw, bh, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))
    p.append(text(bx + bw / 2, by + 26, "Стан Вузла 3", size=14, color=INK, bold=True))

    # Етап 1
    p.append(fitbox(bx + 15, by + 50, bw - 30, 74,
                    "1. Отримано m₂ [1, 1, 0]:\nЛокальний вектор: [0, 0, 0]\nУмова: V_msg[1] <= V_loc[1] (1 <= 0 — ХИБА!)\nРішення: Затримати m₂ у черзі!",
                    size=10.5, fill="#fff5f5", stroke=POS, color=POS, bold=True))

    # Етап 2
    p.append(fitbox(bx + 15, by + 136, bw - 30, 74,
                    "2. Нарешті прибуло m₁ [1, 0, 0]:\nУмова: 1 == 0 + 1 (ІСТИНА!)\nРішення: Доставити m₁ застосунку.\nЛокальний вектор стає: [1, 0, 0]",
                    size=10.5, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=True))

    # Етап 3
    p.append(fitbox(bx + 15, by + 222, bw - 30, 84,
                    "3. Перевірка черги буфера:\nДля m₂ тепер: V_msg[1] <= V_loc[1] (1 <= 1) і\nV_msg[2] == V_loc[2]+1 (1 == 0+1) — ІСТИНА!\nm₂ доставлено слідом за m₁.\nЛокальний вектор стає: [1, 1, 0]",
                    size=10.5, fill="#edf2ff", stroke=NEG, color=NEG, bold=True))

    render(os.path.join(OUT, "causal-delivery.svg"), W, H, *p,
           title="Буфер причинної доставки усуває порушення порядку")


# ── Фіг. 4: Версійні вектори та розв'язання конфліктів у Dynamo ────────────
def fig_version_vectors_siblings():
    W, H = 960, 430
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))
    p.append(text(W / 2, 28, "Версійні вектори в розподіленому сховищі: паралельні записи та злиття", size=15, color=INK, bold=True))

    # Крок 1: Початковий стан
    p.append(fitbox(40, 70, 200, 70,
                    "Базовий стан:\nкошик = [\"книга\"]\nвектор = {A: 1}",
                    size=11.5, fill="#f8fafc", stroke=LINE, color=INK, bold=True))

    # Стрілки розгалуження (мережеве розділення / паралельні записи)
    p.append(arrow(240, 95, 340, 65, color=POS, sw=2))
    p.append(arrow(240, 115, 340, 145, color=NEG, sw=2))

    # Крок 2: Паралельні записи на A та B
    p.append(fitbox(340, 35, 230, 65,
                    "Клієнт 1 пише на вузол A:\nкошик = [\"книга\", \"олівець\"]\nвектор = {A: 2, B: 0}",
                    size=11, fill="#fff5f5", stroke=POS, color=POS, bold=True))

    p.append(fitbox(340, 115, 230, 65,
                    "Клієнт 2 пише на вузол B:\nкошик = [\"книга\", \"зошит\"]\nвектор = {A: 1, B: 1}",
                    size=11, fill="#edf2ff", stroke=NEG, color=NEG, bold=True))

    # Злиття: стрілки сходяться до сховища/клієнта
    p.append(arrow(570, 65, 660, 95, color=POS, sw=2))
    p.append(arrow(570, 145, 660, 115, color=NEG, sw=2))

    # Крок 3: Сховище виявляє конфлікт (siblings)
    p.append(fitbox(660, 60, 260, 90,
                    "Читання сховища:\nВектори {A:2, B:0} та {A:1, B:1}\nНЕПОРІВНЯННІ (конфлікт!).\nСховище повертає обидва двійники:\nsiblings = [v₁, v₂]",
                    size=11, fill="#fef9e7", stroke="#d4ac0d", color=INK, bold=True))

    # Стрілка вниз до застосунку
    p.append(arrow(790, 150, 790, 200, color=FIELD, sw=2.2))

    # Крок 4: Застосунок об'єднує версії та записує назад
    p.append(fitbox(200, 210, 580, 80,
                    "Розв'язання на рівні застосунку (Application-level Merge):\nЗастосунок бере об'єднання кошиків: [\"книга\", \"олівець\", \"зошит\"]\nНовий версійний вектор об'єднує предків та інкрементує координатора:\n{A: 2, B: 1} → запис на A → {A: 3, B: 1}",
                    size=11.5, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=True))

    # Фінал: новий вектор домінує над обома попередніми
    p.append(fitbox(120, 315, 720, 75,
                    "Властивість домінування:\nНовий вектор {A: 3, B: 1} строго більший за {A: 2, B: 0} та {A: 1, B: 1}.\nПри наступних читаннях двійників більше немає — стан повністю узгоджений!",
                    size=12, fill="#f8fafc", stroke=LINE, color=INK, bold=True))

    render(os.path.join(OUT, "version-vectors-siblings.svg"), W, H, *p,
           title="Розв'язання розбіжностей за допомогою версійних векторів")


if __name__ == "__main__":
    fig_lamport_vs_vector()
    fig_vector_clock_flow()
    fig_causal_delivery()
    fig_version_vectors_siblings()
    print("Всі фігури згенеровано успішно.")
