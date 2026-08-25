# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C_QUEUE = "#eaf0fd"; S_QUEUE = NEG     # Черга токенів
C_MATCH = "#fef6e7"; S_MATCH = "#d97706" # Matching Store / ETS
C_NODE  = "#eaf6ef"; S_NODE  = FIELD   # Node Store / Граф
C_ALU   = "#fdecea"; S_ALU   = POS     # ALU / Виконання
C_ROUT  = "#f3f4f6"; S_ROUT  = LINE    # Маршрутизатор

# ── 1. Кільце виконання динамічного dataflow-рушія ────────────────────────────
def fig_dynamic_dataflow_ring():
    W, H = 840, 420
    p = [text(W / 2, 26, "Кільце виконання динамічного dataflow-рушія (Processing Ring)", size=16, bold=True)]

    # 1. Черга токенів
    p.append(rect(40, 70, 190, 100, fill=C_QUEUE, stroke=S_QUEUE, sw=1.5, rx=8))
    p.append(text(135, 95, "Вхідна черга токенів", size=13, color=S_QUEUE, bold=True))
    p.append(text(135, 115, "FIFO токенів", size=11, color=INK))
    p.append(text(135, 135, "⟨Tag, IP, Port, Val⟩", size=10, color=MUTED))
    p.append(text(135, 153, "Буферизація пакетів", size=9, color=MUTED, italic=True))

    # Стрілка 1 -> 2
    p.append(arrow(230, 120, 290, 120, color=LINE, sw=1.8))
    p.append(text(260, 110, "Токен", size=10, color=MUTED))

    # 2. Блок зіставлення операндів (Matching Unit / ETS)
    p.append(rect(290, 70, 240, 100, fill=C_MATCH, stroke=S_MATCH, sw=1.5, rx=8))
    p.append(text(410, 95, "Блок зіставлення (Matching)", size=13, color=S_MATCH, bold=True))
    p.append(text(410, 115, "Explicit Token Store / CAM", size=11, color=INK))
    p.append(text(410, 135, "1-й операнд: запис у слот", size=10, color=MUTED))
    p.append(text(410, 153, "2-й операнд: пара готова → пуск", size=9, color=POS, bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(530, 120, 590, 120, color=LINE, sw=1.8))
    p.append(text(560, 110, "Пара", size=10, color=MUTED))

    # 3. Пам'ять інструкцій графа (Node Store)
    p.append(rect(590, 70, 210, 100, fill=C_NODE, stroke=S_NODE, sw=1.5, rx=8))
    p.append(text(695, 95, "Пам'ять вузлів (Node Store)", size=13, color=S_NODE, bold=True))
    p.append(text(695, 115, "Вибірка коду операції (Opcode)", size=11, color=INK))
    p.append(text(695, 135, "Список дуг-наступників", size=10, color=MUTED))
    p.append(text(695, 153, "Цільові ⟨IP_dest, Port⟩", size=9, color=MUTED, italic=True))

    # Стрілка 3 -> 4 (вниз і вліво)
    p.append(arrow(695, 170, 695, 230, color=LINE, sw=1.8))

    # 4. Обчислювальний блок (ALU / FPU)
    p.append(rect(570, 230, 250, 100, fill=C_ALU, stroke=S_ALU, sw=1.5, rx=8))
    p.append(text(695, 255, "Арифметичний блок (ALU/FPU)", size=13, color=S_ALU, bold=True))
    p.append(text(695, 275, "Виконання операції (чиста функція)", size=11, color=INK))
    p.append(text(695, 295, "Генерація значення результату", size=10, color=MUTED))
    p.append(text(695, 313, "Без спільних регістрів і блокувань", size=9, color=MUTED, italic=True))

    # Стрілка 4 -> 5
    p.append(arrow(570, 280, 500, 280, color=LINE, sw=1.8))
    p.append(text(535, 270, "Результат", size=10, color=MUTED))

    # 5. Формувач токенів і маршрутизатор (Token Form & Network)
    p.append(rect(240, 230, 260, 100, fill=C_ROUT, stroke=S_ROUT, sw=1.5, rx=8))
    p.append(text(370, 255, "Формувач токенів / Маршрутизатор", size=13, color=INK, bold=True))
    p.append(text(370, 275, "Оновлення тегів ⟨Context, Iter⟩", size=11, color=INK))
    p.append(text(370, 295, "Розмноження токенів для дуг графа", size=10, color=MUTED))
    p.append(text(370, 313, "Маршрутизація: локально / мережа NoC", size=9, color=MUTED, italic=True))

    # Стрілка зворотного зв'язку 5 -> 1
    p.append(line(240, 280, 135, 280, color=LINE, sw=1.8))
    p.append(arrow(135, 280, 135, 170, color=LINE, sw=1.8))
    p.append(text(135, 300, "Локальне замикання кільця (новий токен)", size=10, color=S_QUEUE, bold=True))

    # Зовнішня мережа NoC
    p.append(rect(40, 335, 180, 60, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(130, 355, "Мережа NoC / Інші вузли", size=11, color=MUTED, bold=True))
    p.append(text(130, 375, "Міжядерний обмін токенами", size=9, color=MUTED))
    p.append(arrow(260, 330, 220, 350, color=MUTED, sw=1.4))
    p.append(arrow(180, 335, 180, 170, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "dynamic-dataflow-ring.svg"), W, H, *p)


# ── 2. Еволюція зіставлення токенів: CAM vs Hash vs ETS ───────────────────────
def fig_matching_store_evolution():
    W, H = 840, 380
    p = [text(W / 2, 26, "Еволюція блоку зіставлення: CAM проти хешування та Explicit Token Store (ETS)", size=15, bold=True)]

    # Стовпець 1: Асоціативна пам'ять CAM
    x1 = 30
    p.append(rect(x1, 55, 245, 300, fill="#fdf2f2", stroke=POS, sw=1.4, rx=8))
    p.append(text(x1 + 122, 80, "1. Асоціативна CAM (TTDA)", size=13, color=POS, bold=True))
    p.append(text(x1 + 122, 100, "Пошук за збігом тегів", size=11, color=MUTED))

    p.append(rect(x1 + 20, 115, 205, 95, fill="#fff", stroke=POS, sw=1, rx=6))
    p.append(text(x1 + 122, 135, "Масив компараторів", size=11, color=INK, bold=True))
    p.append(text(x1 + 122, 155, "Тег ⟨c, i, ip⟩ порівнюється", size=10, color=INK))
    p.append(text(x1 + 122, 172, "з УСІМА слотами пам'яті", size=10, color=INK))
    p.append(text(x1 + 122, 192, "Складність: O(N) апаратури", size=10, color=POS, bold=True))

    p.append(text(x1 + 122, 235, "✖ Гігантські витрати енергії", size=10, color=POS))
    p.append(text(x1 + 122, 255, "✖ Повільне масштабування", size=10, color=POS))
    p.append(text(x1 + 122, 275, "✖ Переповнення веде до дедлоку", size=10, color=POS))
    p.append(text(x1 + 122, 310, "Ранні MIT TTDA (1978–1984)", size=9, color=MUTED, italic=True))

    # Стовпець 2: Апаратне хешування
    x2 = 295
    p.append(rect(x2, 55, 245, 300, fill="#fef6e7", stroke=S_MATCH, sw=1.4, rx=8))
    p.append(text(x2 + 122, 80, "2. Хеш-таблиця (Manchester)", size=13, color=S_MATCH, bold=True))
    p.append(text(x2 + 122, 100, "Апаратне обчислення h(Tag)", size=11, color=MUTED))

    p.append(rect(x2 + 20, 115, 205, 95, fill="#fff", stroke=S_MATCH, sw=1, rx=6))
    p.append(text(x2 + 122, 135, "Хеш-генератор + SRAM", size=11, color=INK, bold=True))
    p.append(text(x2 + 122, 155, "Індекс = h(Context, IP)", size=10, color=INK))
    p.append(text(x2 + 122, 172, "Ланцюжки переповнення", size=10, color=INK))
    p.append(text(x2 + 122, 192, "Середній час: O(1) за такт", size=10, color=S_MATCH, bold=True))

    p.append(text(x2 + 122, 235, "✔ Звичайна SRAM замість CAM", size=10, color=FIELD))
    p.append(text(x2 + 122, 255, "✖ Колізії погіршують затримку", size=10, color=POS))
    p.append(text(x2 + 122, 275, "✖ Складний контролер пам'яті", size=10, color=POS))
    p.append(text(x2 + 122, 310, "Manchester Machine (1981–1985)", size=9, color=MUTED, italic=True))

    # Стовпець 3: Explicit Token Store (ETS)
    x3 = 560
    p.append(rect(x3, 55, 250, 300, fill="#eaf6ef", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(x3 + 125, 80, "3. Explicit Token Store (ETS)", size=13, color=FIELD, bold=True))
    p.append(text(x3 + 125, 100, "Пряма адресація через FP + r", size=11, color=MUTED))

    p.append(rect(x3 + 20, 115, 210, 95, fill="#fff", stroke=FIELD, sw=1, rx=6))
    p.append(text(x3 + 125, 135, "Кадр активації (Frame)", size=11, color=INK, bold=True))
    p.append(text(x3 + 125, 155, "Адреса = FP + зміщення", size=10, color=INK))
    p.append(text(x3 + 125, 172, "Біт присутності (Presence Bit)", size=10, color=INK))
    p.append(text(x3 + 125, 192, "Гарантовано 1 такт, 0 колізій", size=10, color=FIELD, bold=True))

    p.append(text(x3 + 125, 235, "✔ Жодного асоціативного пошуку", size=10, color=FIELD))
    p.append(text(x3 + 125, 255, "✔ Прямий запис у звичайну SRAM", size=10, color=FIELD))
    p.append(text(x3 + 125, 275, "✔ Кадри виділяються динамічно", size=10, color=FIELD))
    p.append(text(x3 + 125, 310, "MIT Monsoon / EM-4 (1988–1991)", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "matching-store-evolution.svg"), W, H, *p)


# ── 3. Стани та робота пам'яті I-структур (I-Structures) ─────────────────────
def fig_i_structure_states():
    W, H = 820, 350
    p = [text(W / 2, 26, "Автомат станів комірки I-структури (I-Structure Memory Cell)", size=16, bold=True)]

    # Стан 1: Порожньо (EMPTY)
    p.append(rect(40, 80, 200, 110, fill="#f3f4f6", stroke=LINE, sw=1.5, rx=8))
    p.append(text(140, 110, "EMPTY (Порожньо)", size=14, color=INK, bold=True))
    p.append(text(140, 132, "Комірка ініціалізована", size=11, color=MUTED))
    p.append(text(140, 150, "Даних немає", size=10, color=MUTED))
    p.append(text(140, 168, "Черга читачів порожня", size=9, color=MUTED))

    # Стан 2: Відкладено (DEFERRED)
    p.append(rect(310, 80, 220, 110, fill=C_MATCH, stroke=S_MATCH, sw=1.5, rx=8))
    p.append(text(420, 110, "DEFERRED (Очікування)", size=14, color=S_MATCH, bold=True))
    p.append(text(420, 132, "Читачі прийшли раніше запису", size=11, color=INK))
    p.append(text(420, 150, "Список продовжень (Continuations)", size=10, color=MUTED))
    p.append(text(420, 168, "⟨Tag_reader, IP_dest⟩ у черзі", size=9, color=S_MATCH, bold=True))

    # Стан 3: Присутнє (PRESENT)
    p.append(rect(590, 80, 190, 110, fill=C_NODE, stroke=S_NODE, sw=1.5, rx=8))
    p.append(text(685, 110, "PRESENT (Записано)", size=14, color=S_NODE, bold=True))
    p.append(text(685, 132, "Значення збережено", size=11, color=INK))
    p.append(text(685, 150, "Незмінне (Single-assignment)", size=10, color=MUTED))
    p.append(text(685, 168, "Читання віддає результат", size=9, color=FIELD, bold=True))

    # Переходи:
    # 1. READ коли EMPTY -> DEFERRED
    p.append(arrow(240, 120, 310, 120, color=S_MATCH, sw=1.8))
    p.append(text(275, 105, "READ", size=11, color=S_MATCH, bold=True))
    p.append(text(275, 140, "Додати в чергу", size=9, color=MUTED))

    # 2. WRITE коли DEFERRED -> PRESENT
    p.append(arrow(530, 120, 590, 120, color=FIELD, sw=1.8))
    p.append(text(560, 105, "WRITE", size=11, color=FIELD, bold=True))
    p.append(text(560, 140, "Розбудити всіх", size=9, color=FIELD))

    # 3. Прямий WRITE коли EMPTY -> PRESENT (дуга зверху)
    p.append(line(140, 80, 140, 50, color=FIELD, sw=1.5))
    p.append(line(140, 50, 685, 50, color=FIELD, sw=1.5))
    p.append(arrow(685, 50, 685, 80, color=FIELD, sw=1.5))
    p.append(text(410, 42, "WRITE (запис до прибуття читачів) → прямий перехід у PRESENT", size=10, color=FIELD, bold=True))

    # 4. READ коли PRESENT (петля)
    p.append(line(730, 190, 730, 230, color=FIELD, sw=1.5))
    p.append(line(730, 230, 650, 230, color=FIELD, sw=1.5))
    p.append(arrow(650, 230, 650, 190, color=FIELD, sw=1.5))
    p.append(text(690, 245, "READ → миттєва відповідь", size=10, color=FIELD))

    # 5. Повторний WRITE (помилка)
    p.append(rect(40, 240, 490, 80, fill="#fdf2f2", stroke=POS, sw=1.2, rx=6))
    p.append(text(285, 265, "Виняткова ситуація: подвійний запис (Duplicate Write Trap)", size=12, color=POS, bold=True))
    p.append(text(285, 285, "Повторний WRITE у стан PRESENT порушує інваріант одноразового присвоєння", size=10, color=INK))
    p.append(text(285, 303, "Апаратура генерує переривання/виняток, гарантуючи детермінізм програми", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "i-structure-states.svg"), W, H, *p)


# ── 4. Динамічні кадри активації в ETS ────────────────────────────────────────
def fig_frame_activation_tree():
    W, H = 840, 400
    p = [text(W / 2, 26, "Динамічні кадри активації (Activation Frames) у просторі пам'яті ETS", size=15, bold=True)]

    # Менеджер кадрів (Frame Manager / Allocator)
    p.append(rect(30, 60, 210, 110, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=8))
    p.append(text(135, 85, "Frame Allocator", size=13, color=NEG, bold=True))
    p.append(text(135, 107, "Виділення бази FP", size=11, color=INK))
    p.append(text(135, 127, "FP_0 = 0x1000 (Головна)", size=10, color=MUTED))
    p.append(text(135, 145, "FP_1 = 0x1040 (Ітерація 1)", size=10, color=MUTED))
    p.append(text(135, 160, "FP_2 = 0x1080 (Ітерація 2)", size=10, color=MUTED))

    # Стрілка від Allocator до кадрів
    p.append(arrow(240, 115, 290, 115, color=LINE, sw=1.8))
    p.append(text(265, 105, "База FP", size=10, color=MUTED))

    # Кадр 1: Головна функція
    x_f1 = 290
    p.append(rect(x_f1, 60, 240, 150, fill="#fff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(x_f1 + 120, 80, "Кадр FP_0 (Головний контекст)", size=12, color=FIELD, bold=True))
    p.append(line(x_f1, 90, x_f1 + 240, 90, color=FIELD, sw=1))
    p.append(text(x_f1 + 120, 110, "FP_0 + 0: Slot A [Bit=1, Val=42]", size=10, color=INK))
    p.append(text(x_f1 + 120, 130, "FP_0 + 1: Slot B [Bit=0, Empty]", size=10, color=MUTED))
    p.append(text(x_f1 + 120, 150, "FP_0 + 2: Slot C [Bit=1, Val=10]", size=10, color=INK))
    p.append(text(x_f1 + 120, 175, "Локальні операнди інструкцій", size=9, color=MUTED, italic=True))

    # Кадр 2: Паралельна ітерація 1
    x_f2 = 560
    p.append(rect(x_f2, 60, 250, 150, fill="#fff", stroke=S_MATCH, sw=1.4, rx=6))
    p.append(text(x_f2 + 125, 80, "Кадр FP_1 (Ітерація k=1)", size=12, color=S_MATCH, bold=True))
    p.append(line(x_f2, 90, x_f2 + 250, 90, color=S_MATCH, sw=1))
    p.append(text(x_f2 + 125, 110, "FP_1 + 0: Slot A [Bit=1, Val=100]", size=10, color=INK))
    p.append(text(x_f2 + 125, 130, "FP_1 + 1: Slot B [Bit=1, Val=200]", size=10, color=POS, bold=True))
    p.append(text(x_f2 + 125, 150, "FP_1 + 2: Slot C [Bit=0, Empty]", size=10, color=MUTED))
    p.append(text(x_f2 + 125, 175, "Обидва операнди є → Спрацьовування!", size=9, color=POS, bold=True))

    # Нижній блок: Кадр 3 (Рекурсивний виклик або Ітерація 2)
    p.append(rect(290, 235, 520, 140, fill="#fef6e7", stroke=S_MATCH, sw=1.2, rx=8))
    p.append(text(550, 258, "Паралельне розгортання вкладених викликів / ітерацій", size=13, color=S_MATCH, bold=True))
    p.append(text(550, 280, "Кожен екземпляр функції або тіла циклу отримує власний ізольований кадр у пам'яті ETS.", size=10, color=INK))
    p.append(text(550, 300, "Токен несе покажчик кадру: ⟨FP, offset, value⟩. Зіставлення відбувається без асоціативних пошуків.", size=10, color=INK))
    p.append(text(550, 320, "Після завершення обчислення кадру вся пам'ять миттєво повертається пулу (deallocate FP).", size=10, color=MUTED))
    p.append(text(550, 345, "Повна відсутність взаємних блокувань і конфліктів за спільні регістри", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "frame-activation-tree.svg"), W, H, *p)


if __name__ == "__main__":
    fig_dynamic_dataflow_ring()
    fig_matching_store_evolution()
    fig_i_structure_states()
    fig_frame_activation_tree()
    print("Figures generated successfully in img/")
