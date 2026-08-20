# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Векторні годинники»."""

import os
import sys

# Шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_lamport_vs_vector():
    """Порівняння логічних годинників Лампорта та векторних годинників."""
    w, h = 820, 440
    frags = []

    # Заголовок блоків
    frags.append(text(210, 35, "Скалярний годинник Лампорта (помилкова причинність)", size=13, bold=True, color=INK))
    frags.append(text(620, 35, "Векторний годинник (точна причинність)", size=13, bold=True, color=INK))

    # Розділювач колонок
    frags.append(line(410, 20, 410, 420, color=MUTED, sw=1.0, dash="4,4"))

    # ── Ліва частина: Lamport Clocks ──
    # Часові осі процесів
    y_p1, y_p2, y_p3 = 100, 210, 320
    frags.append(text(40, y_p1 + 4, "Вузол A", size=12, bold=True, anchor="end"))
    frags.append(text(40, y_p2 + 4, "Вузол B", size=12, bold=True, anchor="end"))
    frags.append(text(40, y_p3 + 4, "Вузол C", size=12, bold=True, anchor="end"))

    frags.append(arrow(50, y_p1, 380, y_p1, color=LINE, sw=1.5))
    frags.append(arrow(50, y_p2, 380, y_p2, color=LINE, sw=1.5))
    frags.append(arrow(50, y_p3, 380, y_p3, color=LINE, sw=1.5))

    # Подія a1 на A: L=1, надсилання повідомлення m1
    frags.append(circle(100, y_p1, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(100, y_p1 - 14, "L=1", size=11, bold=True, color=FIELD))

    # Подія b1 на B: отримання m1, L = max(0, 1) + 1 = 2
    frags.append(arrow(100, y_p1, 230, y_p2, color=FIELD, sw=1.5))
    frags.append(circle(230, y_p2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(230, y_p2 - 14, "L=2", size=11, bold=True, color=FIELD))

    # Подія c1 на C: локальна дія, L=2 (незалежна!)
    frags.append(circle(180, y_p3, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(180, y_p3 - 14, "L=2", size=11, bold=True, color=POS))

    # Висновок зліва
    tb_l, _, _ = textbox(215, 385, "L(a1)=1 < L(c1)=2 створює ілюзію зв'язку;\nL(b1)=2 та L(c1)=2 маскують паралельність",
                         size=11, fill="#fff2f2", stroke=POS, pad=6, min_w=340)
    frags.append(tb_l)

    # ── Права частина: Vector Clocks ──
    frags.append(text(450, y_p1 + 4, "Вузол A", size=12, bold=True, anchor="end"))
    frags.append(text(450, y_p2 + 4, "Вузол B", size=12, bold=True, anchor="end"))
    frags.append(text(450, y_p3 + 4, "Вузол C", size=12, bold=True, anchor="end"))

    frags.append(arrow(460, y_p1, 790, y_p1, color=LINE, sw=1.5))
    frags.append(arrow(460, y_p2, 790, y_p2, color=LINE, sw=1.5))
    frags.append(arrow(460, y_p3, 790, y_p3, color=LINE, sw=1.5))

    # Подія a1 на A: V=[1, 0, 0]
    frags.append(circle(510, y_p1, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(510, y_p1 - 14, "[1, 0, 0]", size=11, bold=True, color=FIELD))

    # Подія b1 на B: отримання m1 -> V=[1, 1, 0]
    frags.append(arrow(510, y_p1, 640, y_p2, color=FIELD, sw=1.5))
    frags.append(circle(640, y_p2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(640, y_p2 - 14, "[1, 1, 0]", size=11, bold=True, color=FIELD))

    # Подія c1 на C: V=[0, 0, 1]
    frags.append(circle(590, y_p3, 6, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(text(590, y_p3 - 14, "[0, 0, 1]", size=11, bold=True, color=NEG))

    # Висновок справа
    tb_r, _, _ = textbox(625, 385, "[1,0,0] || [0,0,1] — вектор доводить незалежність;\n[1,1,0] || [0,0,1] — конфлікт точно розпізнано",
                         size=11, fill="#f0f7ff", stroke=NEG, pad=6, min_w=340)
    frags.append(tb_r)

    render(os.path.join(IMG_DIR, "lamport-vs-vector-concurrency.svg"), w, h, *frags)


def fig_vector_clock_exchange():
    """Кроки оновлення векторного годинника між трьома процесами."""
    w, h = 820, 360
    frags = []

    y1, y2, y3 = 70, 180, 290
    frags.append(text(50, y1 + 4, "Процес P1", size=12, bold=True, anchor="end"))
    frags.append(text(50, y2 + 4, "Процес P2", size=12, bold=True, anchor="end"))
    frags.append(text(50, y3 + 4, "Процес P3", size=12, bold=True, anchor="end"))

    # Осі
    frags.append(arrow(60, y1, 780, y1, color=LINE, sw=1.5))
    frags.append(arrow(60, y2, 780, y2, color=LINE, sw=1.5))
    frags.append(arrow(60, y3, 780, y3, color=LINE, sw=1.5))

    # P1 e1: локальний тік [1,0,0], відправка на P2
    frags.append(circle(140, y1, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(140, y1 - 15, "e1: [1, 0, 0]", size=11, bold=True, color=FIELD))

    # P2 e2: прийом від P1. max([0,0,0], [1,0,0]) + [0,1,0] = [1,1,0]
    frags.append(arrow(140, y1, 280, y2, color=FIELD, sw=1.5))
    frags.append(circle(280, y2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(280, y2 - 15, "e2: [1, 1, 0]", size=11, bold=True, color=FIELD))

    # P2 e3: відправка на P3 з вектором [1,2,0]
    frags.append(circle(390, y2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(390, y2 - 15, "e3: [1, 2, 0]", size=11, bold=True, color=FIELD))

    # P3 e4: прийом від P2 -> [1,2,1]
    frags.append(arrow(390, y2, 540, y3, color=FIELD, sw=1.5))
    frags.append(circle(540, y3, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(540, y3 + 24, "e4: [1, 2, 1]", size=11, bold=True, color=FIELD))

    # P1 e5: локальна подія паралельно до P3 -> [2,0,0]
    frags.append(circle(480, y1, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(480, y1 - 15, "e5: [2, 0, 0]", size=11, bold=True, color=POS))

    # P3 e6: локальна подія на P3 -> [1,2,2]
    frags.append(circle(680, y3, 6, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(text(680, y3 + 24, "e6: [1, 2, 2]", size=11, bold=True, color=NEG))

    # Порівняння причинності між e5 та e6
    tb, _, _ = textbox(580, y1 + 10, "Порівняння e5 та e6:\n[2,0,0] не < [1,2,2] і [1,2,2] не < [2,0,0]\n=> e5 || e6 (конкурентні події)",
                       size=11, fill=FILL, stroke=LINE, pad=6, min_w=280)
    frags.append(tb)

    render(os.path.join(IMG_DIR, "vector-clock-message-exchange.svg"), w, h, *frags)


def fig_causal_delivery_buffer():
    """Буферизація повідомлень при порушенні причинного порядку доставки."""
    w, h = 820, 360
    frags = []

    y1, y2, y3 = 70, 170, 270
    frags.append(text(50, y1 + 4, "Вузол 1", size=12, bold=True, anchor="end"))
    frags.append(text(50, y2 + 4, "Вузол 2", size=12, bold=True, anchor="end"))
    frags.append(text(50, y3 + 4, "Вузол 3", size=12, bold=True, anchor="end"))

    frags.append(arrow(60, y1, 780, y1, color=LINE, sw=1.5))
    frags.append(arrow(60, y2, 780, y2, color=LINE, sw=1.5))
    frags.append(arrow(60, y3, 780, y3, color=LINE, sw=1.5))

    # Вузол 1 створює M1 з вектором [1,0,0] і розсилає всім
    frags.append(circle(120, y1, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(120, y1 - 14, "M1: [1,0,0]", size=11, bold=True, color=FIELD))

    # Вузол 2 отримує M1 вчасно -> оновлює локальний вектор до [1,0,0], створює M2 [1,1,0]
    frags.append(arrow(120, y1, 230, y2, color=FIELD, sw=1.5))
    frags.append(circle(230, y2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(230, y2 + 24, "Прийом M1 -> M2: [1,1,0]", size=11, bold=True, color=FIELD))

    # Вузол 2 надсилає M2 на Вузол 3 швидким каналом
    frags.append(arrow(230, y2, 380, y3, color=POS, sw=1.5))

    # Повідомлення M1 від Вузла 1 затримується в мережі до Вузла 3 (дуга або лінія в обхід)
    frags.append(line(120, y1, 190, y1 + 50, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(line(190, y1 + 50, 560, y3 - 15, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(arrow(560, y3 - 15, 580, y3, color=FIELD, sw=1.5))

    # На Вузлі 3: прибуття M2 о t=380. Локальний вектор V3 = [0,0,0].
    # Умова доставки: M2.V[2] == V3[2]+1 (1 == 0+1 ok), АЛЕ M2.V[1] <= V3[1] (1 <= 0 FALSE!).
    frags.append(circle(380, y3, 6, fill=POS, stroke=LINE, sw=1.5))
    tb_buf, _, _ = textbox(380, y3 + 45, "M2 [1,1,0] прибуло раніше M1!\nV3=[0,0,0] -> блокування в буфері",
                           size=10, fill="#fff2f2", stroke=POS, pad=5, min_w=200)
    frags.append(tb_buf)

    # Прибуття M1 на Вузол 3 о t=580 -> V3 стає [1,0,0] -> розблокування M2 -> V3 стає [1,1,0]
    frags.append(circle(580, y3, 6, fill=FIELD, stroke=LINE, sw=1.5))
    tb_deliv, _, _ = textbox(650, y3 - 40, "M1 [1,0,0] доставлено ->\nрозблокування M2 з буфера!\nV3 = [1,1,0]",
                             size=10, fill="#e8f8f0", stroke=FIELD, pad=6, min_w=190)
    frags.append(tb_deliv)

    render(os.path.join(IMG_DIR, "causal-delivery-buffer.svg"), w, h, *frags)


def fig_version_vectors_dynamo():
    """Версійні вектори в розподіленому сховищі (Dynamo/Riak) та розв'язання братів-двійників."""
    w, h = 820, 380
    frags = []

    # Початковий стан об'єкта
    tb_init, _, _ = textbox(130, 180, "Початковий запис\nKey: 'cart_1'\nVal: ['Book']\nVV: {A:1}",
                            size=11, fill=FILL, stroke=LINE, pad=8, min_w=140)
    frags.append(tb_init)

    # Гілка 1 (Репліка A)
    frags.append(arrow(210, 160, 320, 90, color=LINE, sw=1.5))
    tb_a, _, _ = textbox(420, 90, "Клієнт 1 -> Репліка A\nVal: ['Book', 'Phone']\nVV: {A:2}",
                         size=11, fill="#f0f7ff", stroke=NEG, pad=8, min_w=170)
    frags.append(tb_a)

    # Гілка 2 (Репліка B, паралельний запис)
    frags.append(arrow(210, 200, 320, 270, color=LINE, sw=1.5))
    tb_b, _, _ = textbox(420, 270, "Клієнт 2 -> Репліка B\nVal: ['Book', 'Pen']\nVV: {A:1, B:1}",
                         size=11, fill="#fff2f2", stroke=POS, pad=8, min_w=170)
    frags.append(tb_b)

    # Злиття гілок (Конфлікт / Siblings)
    frags.append(arrow(520, 90, 610, 150, color=LINE, sw=1.5))
    frags.append(arrow(520, 270, 610, 210, color=LINE, sw=1.5))

    tb_sib, _, _ = textbox(700, 180, "Читання клієнтом:\nВиявлено братів (siblings)\n{A:2} || {A:1, B:1}\nЗлиття -> ['Book','Phone','Pen']\nНовий VV: {A:3, B:1}",
                           size=10, fill="#fdfbf0", stroke="#d4ac0d", pad=8, min_w=200)
    frags.append(tb_sib)

    render(os.path.join(IMG_DIR, "version-vectors-dynamo-siblings.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_lamport_vs_vector()
    fig_vector_clock_exchange()
    fig_causal_delivery_buffer()
    fig_version_vectors_dynamo()
    print("Всі фігури успішно згенеровано.")
