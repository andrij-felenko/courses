# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C_PC    = "#eaf0fd"; S_PC    = NEG     # фон Нейман / лічильник команд
C_DFG   = "#eaf6ef"; S_DFG   = FIELD   # Dataflow / потік даних
C_WARN  = "#fdecea"; S_WARN  = POS     # затор / підтвердження / обмеження
C_MATCH = "#fef6e7"; S_MATCH = "#d97706" # matching store / теги
C_TILE  = "#f3f4f6"; S_TILE  = LINE

# ── 1. Фон Нейман (Control Flow) проти Потоку Даних (Dataflow) ───────────────
def fig_control_flow_vs_dataflow():
    W, H = 820, 380
    p = [text(W / 2, 26, "Послідовне керування (PC) проти графа потоку даних (Dataflow)", size=16, bold=True)]

    # ── Ліва панель: Фон Нейман (Control Flow) ──
    lx = 30
    p.append(rect(lx, 50, 360, 310, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(lx + 180, 75, "Модель фон Неймана (Control Flow)", size=13, color=S_PC, bold=True))
    p.append(text(lx + 180, 93, "Виконання веде лічильник команд (PC)", size=11, color=MUTED))

    # Блок пам'яті програм
    p.append(rect(lx + 30, 115, 140, 150, fill=C_PC, stroke=S_PC, sw=1.4, rx=6))
    p.append(text(lx + 100, 135, "Пам'ять команд", size=12, color=S_PC, bold=True))
    p.append(text(lx + 100, 158, "0x100: ADD R1, a, b", size=10, color=INK))
    p.append(text(lx + 100, 180, "0x104: SUB R2, c, d", size=10, color=INK))
    p.append(text(lx + 100, 202, "0x108: MUL R3, R1, R2", size=10, color=INK))
    p.append(text(lx + 100, 224, "0x10C: STR [res], R3", size=10, color=INK))
    p.append(text(lx + 100, 248, "Послідовний потік", size=9, color=MUTED, italic=True))

    # PC вказівник
    b_pc, _, _ = textbox(lx + 270, 135, "Program Counter\n(PC = 0x100)", size=11, fill="#fff", stroke=S_PC, bold=True, min_w=120)
    p.append(b_pc)
    p.append(arrow(lx + 210, 135, lx + 172, 135, color=S_PC))

    # ALU
    b_alu, _, _ = textbox(lx + 270, 200, "ALU / Регістри\n(Виконання по черзі)", size=11, fill="#fff", stroke=LINE, min_w=120)
    p.append(b_alu)
    p.append(arrow(lx + 170, 180, lx + 210, 195, color=LINE))

    p.append(text(lx + 180, 290, "Вузьке місце: незалежні ADD і SUB", size=11, color=S_WARN, bold=True))
    p.append(text(lx + 180, 308, "вимушено чекають черги в одному потоці PC", size=10, color=MUTED))

    # ── Права панель: Dataflow (Data-Driven) ──
    rx = 430
    p.append(rect(rx, 50, 360, 310, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(rx + 180, 75, "Модель потоку даних (Dataflow)", size=13, color=S_DFG, bold=True))
    p.append(text(rx + 180, 93, "Виконання веде готовність операндів-токенів", size=11, color=MUTED))

    # Входи
    b_in1, _, _ = textbox(rx + 70, 125, "Токени: a, b", size=10, fill=C_DFG, stroke=S_DFG, min_w=80)
    b_in2, _, _ = textbox(rx + 290, 125, "Токени: c, d", size=10, fill=C_DFG, stroke=S_DFG, min_w=80)
    p.append(b_in1)
    p.append(b_in2)

    # Вузли операцій
    b_add, _, _ = textbox(rx + 70, 190, "Вузол: ADD\n(a + b)", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=90)
    b_sub, _, _ = textbox(rx + 290, 190, "Вузол: SUB\n(c − d)", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=90)
    p.append(b_add)
    p.append(b_sub)
    p.append(arrow(rx + 70, 142, rx + 70, 170, color=S_DFG))
    p.append(arrow(rx + 290, 142, rx + 290, 170, color=S_DFG))

    # Паралельне виконання напис
    p.append(text(rx + 180, 190, "Обидва стартують\nодночасно!", size=10, color=S_DFG, bold=True))

    # Вузол множення
    b_mul, _, _ = textbox(rx + 180, 260, "Вузол: MUL\n((a + b) · (c − d))", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=130)
    p.append(b_mul)
    p.append(arrow(rx + 105, 210, rx + 140, 242, color=S_DFG))
    p.append(arrow(rx + 255, 210, rx + 220, 242, color=S_DFG))

    p.append(text(rx + 180, 310, "Немає PC і глобального стану: оператор спрацьовує,", size=10, color=INK))
    p.append(text(rx + 180, 326, "щойно на його дуги прибули всі потрібні токени", size=10, color=FIELD, bold=True))

    return render(os.path.join(OUT, "in-order-vs-dataflow.svg"), W, H, *p)


# ── 2. Статичний (Денніс) проти Динамічного (теги Арвінда) ───────────────────
def fig_static_vs_dynamic_dataflow():
    W, H = 840, 420
    p = [text(W / 2, 26, "Статичний Dataflow (Денніс) проти тегованого динамічного (Арвінд)", size=16, bold=True)]

    # ── Ліворуч: Статичний dataflow ──
    lx = 25
    p.append(rect(lx, 50, 380, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(lx + 190, 75, "Статичний Dataflow (Jack Dennis)", size=13, color=INK, bold=True))
    p.append(text(lx + 190, 93, "Правило: не більше 1 токена на дузі", size=11, color=MUTED))

    # Вузол A
    b_na, _, _ = textbox(lx + 190, 135, "Оператор A (Обчислення)", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=180)
    p.append(b_na)

    # Пряма дуга з токеном
    p.append(arrow(lx + 140, 155, lx + 140, 245, color=S_DFG, sw=2))
    p.append(circle(lx + 140, 200, 7, fill=C_DFG, stroke=S_DFG, sw=2))
    p.append(text(lx + 105, 204, "Токен", size=10, color=S_DFG, bold=True, anchor="end"))

    # Зворотна дуга підтвердження (Ack)
    p.append(arrow(lx + 240, 245, lx + 240, 155, color=S_WARN, sw=1.8))
    p.append(circle(lx + 240, 200, 6, fill=C_WARN, stroke=S_WARN, sw=1.5))
    p.append(text(lx + 252, 204, "Ack (дозвіл)", size=10, color=S_WARN, bold=True, anchor="start"))

    # Вузол B
    b_nb, _, _ = textbox(lx + 190, 265, "Оператор B (Споживач)", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=180)
    p.append(b_nb)

    p.append(text(lx + 190, 315, "Проблема: дуги не мають буфера.", size=11, color=S_WARN, bold=True))
    p.append(text(lx + 190, 333, "A не може випустити новий результат для ітерації k+1,", size=10, color=INK))
    p.append(text(lx + 190, 350, "доки B не надішле сигнал Ack про споживання токена k.", size=10, color=INK))
    p.append(text(lx + 190, 372, "Конвеєризація циклів та рекурсія заблоковані.", size=10, color=POS, italic=True))

    # ── Праворуч: Динамічний тегований dataflow ──
    rx = 435
    p.append(rect(rx, 50, 380, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(rx + 190, 75, "Динамічний Tagged-Token Dataflow", size=13, color=S_MATCH, bold=True))
    p.append(text(rx + 190, 93, "Токени несуть тег: <Контекст c, Ітерація i>", size=11, color=MUTED))

    # Вхідні теговані токени
    b_tok1, _, _ = textbox(rx + 90, 130, "Токен: val=10\nТег: <ctx=1, iter=3>", size=10, fill=C_MATCH, stroke=S_MATCH, min_w=125)
    b_tok2, _, _ = textbox(rx + 290, 130, "Токен: val=25\nТег: <ctx=1, iter=3>", size=10, fill=C_MATCH, stroke=S_MATCH, min_w=125)
    p.append(b_tok1)
    p.append(b_tok2)

    # Блок співставлення токенів (Matching Store)
    b_match, _, _ = textbox(rx + 190, 205, "Token Matching Unit (Асоціативна пам'ять)\nЗіставлення за тегом <ctx, iter, dest_node>", size=11, fill=C_MATCH, stroke=S_MATCH, bold=True, min_w=310)
    p.append(b_match)
    p.append(arrow(rx + 90, 155, rx + 130, 185, color=S_MATCH))
    p.append(arrow(rx + 290, 155, rx + 250, 185, color=S_MATCH))

    # Стрілка збігу
    p.append(arrow(rx + 190, 230, rx + 190, 260, color=S_DFG, sw=2))
    p.append(text(rx + 200, 248, "Збіг тегів!", size=10, color=S_DFG, bold=True, anchor="start"))

    # Виконавчий блок ALU
    b_exec, _, _ = textbox(rx + 190, 285, "Виконавчий блок ALU\nОбчислення: ADD 10, 25 (для iter=3)", size=11, fill=C_DFG, stroke=S_DFG, bold=True, min_w=240)
    p.append(b_exec)

    p.append(text(rx + 190, 335, "Перевага: сотні ітерацій циклу та викликів", size=11, color=FIELD, bold=True))
    p.append(text(rx + 190, 353, "виконуються паралельно на одному графі.", size=10, color=INK))
    p.append(text(rx + 190, 372, "Ціна: складна асоціативна пам'ять Matching Store.", size=10, color=S_MATCH, italic=True))

    return render(os.path.join(OUT, "static-vs-dynamic-dataflow.svg"), W, H, *p)


# ── 3. Просторовий Dataflow в AI-акселераторах (Spatial Computing & Mesh) ─────
def fig_spatial_dataflow_ai():
    W, H = 820, 400
    p = [text(W / 2, 26, "Просторові Dataflow-обчислення: потоковий масив обчислювачів", size=16, bold=True)]

    # Заголовок опису
    p.append(text(W / 2, 48, "Дані течуть крізь сітку процесорних елементів (PE) без звернень до центрального регістрового файлу", size=11, color=MUTED))

    # Створення сітки 3x3 PE (Processing Elements)
    gx0, gy0 = 240, 90
    step_x, step_y = 130, 90

    # Вхідні потоки зліва (активації X)
    p.append(text(100, gy0 + 25, "Вхідні активації X\n(потік токенів)", size=11, color=S_PC, bold=True))
    for r in range(3):
        y = gy0 + r * step_y + 25
        p.append(arrow(170, y, gx0 - 15, y, color=S_PC, sw=2))
        p.append(text(195, y - 8, "x%d" % r, size=11, color=S_PC, bold=True))

    # Вхідні ваги / параметри зверху
    p.append(text(gx0 + step_x, gy0 - 25, "Потік ваг / коефіцієнтів W (або локальна SRAM)", size=11, color=S_MATCH, bold=True))
    for c in range(3):
        x = gx0 + c * step_x + 35
        p.append(arrow(x, gy0 - 10, x, gy0 + 5, color=S_MATCH, sw=2))
        p.append(text(x + 12, gy0 - 2, "w%d" % c, size=10, color=S_MATCH, bold=True))

    # Матриця PE
    for r in range(3):
        for c in range(3):
            x = gx0 + c * step_x
            y = gy0 + r * step_y
            # Рамка PE
            p.append(rect(x, y, 70, 50, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
            p.append(text(x + 35, y + 20, "PE[%d,%d]" % (r, c), size=10, color=INK, bold=True))
            p.append(text(x + 35, y + 38, "MAC / ALU", size=9, color=MUTED))

            # Горизонтальні потоки між PE
            if c < 2:
                p.append(arrow(x + 70, y + 25, x + step_x, y + 25, color=S_PC, sw=1.6))
            else:
                # вихід активацій вправо
                p.append(line(x + 70, y + 25, x + 95, y + 25, color=MUTED, sw=1.4, dash="3,3"))

            # Вертикальні потоки часткових сум
            if r < 2:
                p.append(arrow(x + 35, y + 50, x + 35, y + step_y, color=S_DFG, sw=2))
            else:
                # вихід результату знизу
                p.append(arrow(x + 35, y + 50, x + 35, y + 75, color=S_DFG, sw=2))
                p.append(text(x + 35, y + 90, "y%d" % c, size=11, color=S_DFG, bold=True))

    # Підпис результатів
    p.append(text(gx0 + step_x, gy0 + 3 * step_y + 18, "Вихідні накопичені результати Y = X · W", size=12, color=S_DFG, bold=True))

    # Права панель — переваги архітектури
    p.append(rect(650, 90, 150, 240, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(725, 115, "Чому це швидко:", size=11, color=INK, bold=True))
    p.append(text(725, 140, "1. Немає вибірки", size=10, color=S_DFG, bold=True))
    p.append(text(725, 155, "команд (Zero Fetch)", size=9, color=MUTED))
    p.append(text(725, 185, "2. Локальний обмін", size=10, color=S_DFG, bold=True))
    p.append(text(725, 200, "між сусідами (PE→PE)", size=9, color=MUTED))
    p.append(text(725, 230, "3. Мінімальні втрати", size=10, color=S_DFG, bold=True))
    p.append(text(725, 245, "енергії на шини", size=9, color=MUTED))
    p.append(text(725, 275, "4. 100% утилізація", size=10, color=S_DFG, bold=True))
    p.append(text(725, 290, "арифметичних блоків", size=9, color=MUTED))

    return render(os.path.join(OUT, "spatial-dataflow-mesh.svg"), W, H, *p)


if __name__ == "__main__":
    fig_control_flow_vs_dataflow()
    fig_static_vs_dynamic_dataflow()
    fig_spatial_dataflow_ai()
    print("Figures generated successfully in %s" % OUT)
