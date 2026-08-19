# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def cell(x, y, w, h, s, size=13, fill=FILL, stroke=LINE, color=INK, bold=False):
    """Клітинка біта або блоку з написом."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.3, rx=4)
    out += text(x + w / 2.0, y + h / 2.0 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def fig_clz_ctz_anatomy():
    """Анатомія 64-бітного слова: CLZ, CTZ, виділення бітів та Popcount."""
    W, H = 840, 520
    els = []

    els.append(text(W / 2.0, 28, "Анатомія слова: пошук провідних (CLZ), кінцевих (CTZ) нулів та Popcount", size=15, bold=True))

    bits = [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0]

    bw = 43
    bh = 38
    start_x = 74
    y_reg = 100

    els.append(text(38, y_reg + 24, "Слово:", size=13, bold=True, anchor="start"))

    for i in range(16):
        idx = 15 - i
        b = bits[i]
        x = start_x + i * bw

        # Колір комірки
        if idx >= 13: # CLZ
            f_col = "#e8f4fd"
            s_col = NEG
        elif idx < 4: # CTZ
            f_col = "#eafaf1"
            s_col = FIELD
        elif b == 1:
            f_col = "#fdecea"
            s_col = POS
        else:
            f_col = FILL
            s_col = LINE

        els.append(cell(x, y_reg, bw - 4, bh, str(b), size=14, fill=f_col, stroke=s_col, bold=(b == 1)))
        els.append(text(x + (bw - 4) / 2.0, y_reg - 8, str(idx), size=11, color=MUTED))

    # Верхня дужка / лінія для CLZ
    clz_w = 3 * bw - 4
    els.append(line(start_x, y_reg - 24, start_x + clz_w, y_reg - 24, color=NEG, sw=1.8))
    els.append(line(start_x, y_reg - 28, start_x, y_reg - 20, color=NEG, sw=1.8))
    els.append(line(start_x + clz_w, y_reg - 28, start_x + clz_w, y_reg - 20, color=NEG, sw=1.8))
    els.append(text(start_x + clz_w / 2.0, y_reg - 35, "CLZ = 3 нулі", size=12, color=NEG, bold=True))

    # Верхній вказівник на LSB
    lsb_x = start_x + 11 * bw + (bw - 4) / 2.0
    els.append(arrow(lsb_x, y_reg - 30, lsb_x, y_reg - 16, color=POS, sw=1.6))
    els.append(text(lsb_x, y_reg - 36, "Молодша 1 (LSB, біт 4)", size=11, color=POS, bold=True))

    # Нижня дужка / лінія для CTZ
    ctz_start = start_x + 12 * bw
    ctz_w = 4 * bw - 4
    els.append(line(ctz_start, y_reg + bh + 20, ctz_start + ctz_w, y_reg + bh + 20, color=FIELD, sw=1.8))
    els.append(line(ctz_start, y_reg + bh + 16, ctz_start, y_reg + bh + 24, color=FIELD, sw=1.8))
    els.append(line(ctz_start + ctz_w, y_reg + bh + 16, ctz_start + ctz_w, y_reg + bh + 24, color=FIELD, sw=1.8))
    els.append(text(ctz_start + ctz_w / 2.0, y_reg + bh + 38, "CTZ = 4 нулі", size=12, color=FIELD, bold=True))

    # Нижній вказівник на MSB
    msb_x = start_x + 3 * bw + (bw - 4) / 2.0
    els.append(arrow(msb_x, y_reg + bh + 30, msb_x, y_reg + bh + 4, color=POS, sw=1.6))
    els.append(text(msb_x, y_reg + bh + 44, "Старша 1 (MSB, біт 12)", size=11, color=POS, bold=True))

    # Нижня панель: Ключові властивості та операції
    card_y = 210
    box_w = 360
    box_h = 105

    # Блок CLZ & Двійковий логарифм
    els.append(rect(40, card_y, box_w, box_h, fill="#f8fafc", stroke=NEG, sw=1.4, rx=6))
    els.append(text(40 + box_w / 2.0, card_y + 24, "CLZ та двійковий логарифм", size=13, color=NEG, bold=True))
    els.append(text(40 + 16, card_y + 50, "• Старший біт: MSB = (W - 1) - CLZ(x)", size=12, anchor="start"))
    els.append(text(40 + 16, card_y + 72, "• Цілий логарифм: ⌊log₂(x)⌋ = 15 - 3 = 12", size=12, anchor="start"))
    els.append(text(40 + 16, card_y + 92, "• Застосування: класи пам'яті, стелі 2ⁿ", size=11, color=MUTED, anchor="start"))

    # Блок CTZ & Маніпуляція LSB
    els.append(rect(440, card_y, box_w, box_h, fill="#f8fafc", stroke=FIELD, sw=1.4, rx=6))
    els.append(text(440 + box_w / 2.0, card_y + 24, "CTZ та ізоляція бітів", size=13, color=FIELD, bold=True))
    els.append(text(440 + 16, card_y + 50, "• Ізоляція молодшого біта: x & (-x) = 1 << 4", size=12, anchor="start"))
    els.append(text(440 + 16, card_y + 72, "• Скидання молодшого біта: x & (x - 1)", size=12, anchor="start"))
    els.append(text(440 + 16, card_y + 92, "• Застосування: черги задач, бітборди", size=11, color=MUTED, anchor="start"))

    # Блок Popcount
    pop_y = 335
    pop_w = 760
    pop_h = 75
    els.append(rect(40, pop_y, pop_w, pop_h, fill="#fdfbf7", stroke=POS, sw=1.4, rx=6))
    els.append(text(40 + pop_w / 2.0, pop_y + 24, "Population Count (Popcount / Вага Геммінга)", size=13, color=POS, bold=True))
    els.append(text(40 + 20, pop_y + 50, "• Підрахунок усіх встановлених бітів: popcount(x) = 5 (сума ваг усіх розрядів дорівнює 5)", size=12, anchor="start"))
    els.append(text(40 + 20, pop_y + 68, "• Відмінність від CLZ/CTZ: сканує все слово, а не лише зупиняється на першій одиниці", size=11, color=MUTED, anchor="start"))

    els.append(mtext(W / 2.0, 450, [
        "CLZ рахує нулі від старшого краю (MSB), CTZ — від молодшого (LSB).",
        "Апаратні інструкції виконують кожну з цих дій за константний час O(1) за 1 такт процесора.",
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'clz-ctz-anatomy.svg'), W, H, *els,
                  title="Анатомія бітових операцій CLZ, CTZ та Popcount")


def fig_priority_encoder_tree():
    """Ієрархічне дерево пріоритетного шифратора (Priority Encoder Tree)."""
    W, H = 840, 500
    els = []

    els.append(text(W / 2.0, 30, "Апаратне дерево пріоритетного шифратора (64-бітний CLZ за O(1))", size=15, bold=True))

    # 4 блоки 16-бітних шифраторів (Level 0)
    b_w = 165
    b_h = 100
    y_l0 = 65
    xs = [40, 235, 430, 625]
    ranges = ["[63..48]", "[47..32]", "[31..16]", "[15..0]"]

    for i, x in enumerate(xs):
        els.append(rect(x, y_l0, b_w, b_h, fill="#f0f7ff", stroke=NEG, sw=1.4, rx=6))
        els.append(text(x + b_w / 2.0, y_l0 + 22, f"PE-16 (Блок {3 - i})", size=12, color=NEG, bold=True))
        els.append(text(x + b_w / 2.0, y_l0 + 40, f"Вхід: D{ranges[i]}", size=11, color=INK))
        els.append(line(x + 10, y_l0 + 52, x + b_w - 10, y_l0 + 52, color="#c2d9f2", sw=1.0))
        els.append(text(x + 20, y_l0 + 72, "Поз. Y[3:0]", size=11, color=FIELD, anchor="start"))
        els.append(text(x + b_w - 20, y_l0 + 72, "Порожньо Z", size=11, color=POS, anchor="end"))
        els.append(text(x + b_w / 2.0, y_l0 + 90, "(4 біти)", size=10, color=MUTED))

    # Сигнали Zero-Detect (Z0..Z3) йдуть у Блок вибору групи (Level 1)
    y_l1 = 230
    els.append(rect(120, y_l1, 260, 95, fill="#fdf2f2", stroke=POS, sw=1.4, rx=6))
    els.append(text(250, y_l1 + 22, "Шифратор блоків (PE-4)", size=13, color=POS, bold=True))
    els.append(text(250, y_l1 + 44, "Аналіз нульових прапорів Z₀..Z₃", size=11, color=INK))
    els.append(text(250, y_l1 + 64, "Визначає перший ненульовий блок", size=11, color=MUTED))
    els.append(text(250, y_l1 + 84, "Старші біти результату Y[5:4]", size=11, color=POS, bold=True))

    # Мультиплексор молодших бітів (Level 1 MUX)
    els.append(rect(460, y_l1, 260, 95, fill="#f2faf4", stroke=FIELD, sw=1.4, rx=6))
    els.append(text(590, y_l1 + 22, "Мультиплексор 4:1 (MUX)", size=13, color=FIELD, bold=True))
    els.append(text(590, y_l1 + 44, "Вибір Y[3:0] активного блоку", size=11, color=INK))
    els.append(text(590, y_l1 + 64, "Керується шифратором блоків", size=11, color=MUTED))
    els.append(text(590, y_l1 + 84, "Молодші біти результату Y[3:0]", size=11, color=FIELD, bold=True))

    # Стрілки від PE-16 до Level 1
    for i, x in enumerate(xs):
        bx = x + b_w / 2.0
        # Z сигнали до шифратора блоків
        els.append(arrow(bx - 20, y_l0 + b_h, 200 + i * 35, y_l1, color=POS, sw=1.3))
        # Y сигнали до MUX
        els.append(arrow(bx + 20, y_l0 + b_h, 510 + i * 45, y_l1, color=FIELD, sw=1.3))

    # Керуюча стрілка від шифратора блоків до MUX
    els.append(arrow(380, y_l1 + 48, 460, y_l1 + 48, color=POS, sw=1.8))
    els.append(text(420, y_l1 + 40, "Вибір", size=10, color=POS, bold=True))

    # Фінальний блок складання результату (Level 2)
    y_l2 = 375
    els.append(rect(270, y_l2, 300, 65, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    els.append(text(420, y_l2 + 24, "Фінальний 6-бітний індекс CLZ", size=13, bold=True))
    els.append(text(420, y_l2 + 48, "Результат: { Y[5:4] (блок), Y[3:0] (всередині) } (0..64)", size=12, color=NEG, bold=True))

    els.append(arrow(250, y_l1 + 95, 340, y_l2, color=POS, sw=1.5))
    els.append(arrow(590, y_l1 + 95, 500, y_l2, color=FIELD, sw=1.5))

    els.append(mtext(W / 2.0, 468, [
        "Глибина комбінаційної логіки становить O(log₂ W) = 6 вентильних рівнів для 64 бітів.",
        "Сигнал проходить крізь транзистори менш ніж за 0.3 нс, забезпечуючи O(1) виконання за 1 такт АЛП.",
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'priority-encoder-tree.svg'), W, H, *els,
                  title="Ієрархічне дерево пріоритетного шифратора")


def fig_wallace_tree_popcount():
    """Апаратне дерево Воллеса (Wallace Tree / CSA) для Popcount."""
    W, H = 840, 480
    els = []

    els.append(text(W / 2.0, 30, "Апаратне компресорне дерево Воллеса для інструкції POPCNT", size=15, bold=True))

    # Спрощена схема компресії: 64 входи -> CSA компресори 3:2 -> 7-бітний підсумок
    st_y = 65
    b_w = 120
    b_h = 52

    # Рівень 0: 64 біти на вході
    els.append(rect(60, st_y, 720, 36, fill="#f0f7ff", stroke=NEG, sw=1.4, rx=4))
    els.append(text(420, st_y + 23, "Вхідний регістр: 64 одиничні біти однакової ваги (вага 2⁰ = 1)", size=12, color=NEG, bold=True))

    # Рівень 1: 21 компресор 3:2 (Carry-Save Adder)
    y1 = 130
    els.append(rect(140, y1, 560, 48, fill="#fdf6e7", stroke="#d97706", sw=1.4, rx=6))
    els.append(text(420, y1 + 20, "Рівень 1: Двадцять один повний суматор 3:2 (CSA Compressors)", size=12, color="#b45309", bold=True))
    els.append(text(420, y1 + 38, "64 входи (21 × 3 + 1) → 21 біт суми (вага 1) + 21 біт переносу (вага 2) + 1 = 43 біти", size=11, color=INK))
    els.append(arrow(420, st_y + 36, 420, y1, color=LINE, sw=1.4))

    # Рівень 2: Зведення 43 бітів
    y2 = 205
    els.append(rect(190, y2, 460, 44, fill="#fdf6e7", stroke="#d97706", sw=1.4, rx=6))
    els.append(text(420, y2 + 18, "Рівень 2: Чотирнадцять суматорів 3:2 (43 → 29 бітів)", size=12, color="#b45309", bold=True))
    els.append(text(420, y2 + 35, "Розподіл бітів за вагами 2⁰, 2¹, 2² без розповсюдження переносу", size=11, color=MUTED))
    els.append(arrow(420, y1 + 48, 420, y2, color=LINE, sw=1.4))

    # Рівні 3-5: Каскади стиснення
    y3 = 275
    els.append(rect(240, y3, 360, 44, fill="#fdf6e7", stroke="#d97706", sw=1.4, rx=6))
    els.append(text(420, y3 + 18, "Рівні 3–5: Подальша компресія (29 → 20 → 14 → 9 бітів)", size=12, color="#b45309", bold=True))
    els.append(text(420, y3 + 35, "Зведення до двох фінальних 7-бітних векторів (Сума S та Перенос C)", size=11, color=MUTED))
    els.append(arrow(420, y2 + 44, 420, y3, color=LINE, sw=1.4))

    # Фінальний суматор (7-бітний CLA)
    y4 = 345
    els.append(rect(260, y4, 320, 50, fill="#f2faf4", stroke=FIELD, sw=1.5, rx=6))
    els.append(text(420, y4 + 20, "Фінальний 7-бітний суматор (CLA Adder)", size=13, color=FIELD, bold=True))
    els.append(text(420, y4 + 38, "Результат: число 0..64 (7 бітів у цільовому регістрі)", size=11, color=INK))
    els.append(arrow(420, y3 + 44, 420, y4, color=LINE, sw=1.4))

    els.append(mtext(W / 2.0, 435, [
        "Компресори 3:2 додають розряди паралельно на кожному ярусі без затримки ripple carry.",
        "У сучасних ядрах (x86 Golden Cove, Zen 4, Apple M-серія) блок POPCNT має латентність 1 такт і темп 1 такт.",
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'wallace-tree-popcount.svg'), W, H, *els,
                  title="Апаратне дерево Воллеса для Popcount")


def fig_scheduler_bitboard_flow():
    """Застосування: Планувальник ОС O(1) та Шахові бітборди."""
    W, H = 840, 480
    els = []

    els.append(text(W / 2.0, 30, "Системні застосування бітового пошуку: Планувальник ОС та Шахові бітборди", size=15, bold=True))

    pw = 370
    ph = 370
    py = 55

    # Ліва панель: Планувальник ОС
    lx = 35
    els.append(rect(lx, py, pw, ph, fill="#fafbfc", stroke=NEG, sw=1.4, rx=6))
    els.append(text(lx + pw / 2.0, py + 26, "1. Планувальник ядра ОС (O(1) Scheduler)", size=13, color=NEG, bold=True))

    # Схема бітової карти пріоритетів
    els.append(rect(lx + 20, py + 50, pw - 40, 52, fill="#f0f7ff", stroke=NEG, sw=1.0, rx=4))
    els.append(text(lx + pw / 2.0, py + 68, "Бітова карта пріоритетів (140 черг задач)", size=11, bold=True))
    els.append(text(lx + pw / 2.0, py + 88, "unsigned long bitmap[5] (1 біт = є готова задача)", size=10, color=MUTED))

    els.append(arrow(lx + pw / 2.0, py + 102, lx + pw / 2.0, py + 125, color=NEG, sw=1.4))

    els.append(rect(lx + 20, py + 125, pw - 40, 58, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    els.append(text(lx + pw / 2.0, py + 145, "sched_find_first_bit(bitmap)", size=12, color=NEG, bold=True))
    els.append(text(lx + pw / 2.0, py + 165, "Апаратний CTZ знаходить чергу за 1 такт", size=11, color=FIELD, bold=True))

    els.append(arrow(lx + pw / 2.0, py + 183, lx + pw / 2.0, py + 205, color=NEG, sw=1.4))

    els.append(rect(lx + 20, py + 205, pw - 40, 68, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    els.append(text(lx + pw / 2.0, py + 225, "Вибір задачі з черги runqueue[prio]", size=11, bold=True))
    els.append(text(lx + pw / 2.0, py + 245, "Час вибору: O(1) константа < 1 нс", size=11, color=FIELD, bold=True))
    els.append(text(lx + pw / 2.0, py + 262, "Не залежить від загальної кількості ниток (10 чи 100 000)", size=10, color=MUTED))

    els.append(rect(lx + 20, py + 290, pw - 40, 65, fill="#fdf2f2", stroke=POS, sw=1.0, rx=4))
    els.append(text(lx + pw / 2.0, py + 310, "Перевага над циклом:", size=11, color=POS, bold=True))
    els.append(text(lx + pw / 2.0, py + 328, "Без перевірки 140 вказівників у пам'яті", size=11, color=INK))
    els.append(text(lx + pw / 2.0, py + 344, "Повна відсутність промахів передбачення переходів", size=10, color=MUTED))

    # Права панель: Шаховий рушій
    rx = 435
    els.append(rect(rx, py, pw, ph, fill="#fafbfc", stroke=FIELD, sw=1.4, rx=6))
    els.append(text(rx + pw / 2.0, py + 26, "2. Шаховий рушій (Bitboard Move Gen)", size=13, color=FIELD, bold=True))

    els.append(rect(rx + 20, py + 50, pw - 40, 52, fill="#f2faf4", stroke=FIELD, sw=1.0, rx=4))
    els.append(text(rx + pw / 2.0, py + 68, "Бітборд 64-біт: позиція фігур (uint64_t)", size=11, bold=True))
    els.append(text(rx + pw / 2.0, py + 88, "Кожен біт 0..63 відповідає клітинці дошки (a1..h8)", size=10, color=MUTED))

    els.append(arrow(rx + pw / 2.0, py + 102, rx + pw / 2.0, py + 125, color=FIELD, sw=1.4))

    els.append(rect(rx + 20, py + 125, pw - 40, 58, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    els.append(text(rx + pw / 2.0, py + 145, "sq = std::countr_zero(bitboard)", size=12, color=FIELD, bold=True))
    els.append(text(rx + pw / 2.0, py + 165, "Миттєве отримання координат наступної фігури", size=11, color=INK))

    els.append(arrow(rx + pw / 2.0, py + 183, rx + pw / 2.0, py + 205, color=FIELD, sw=1.4))

    els.append(rect(rx + 20, py + 205, pw - 40, 68, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    els.append(text(rx + pw / 2.0, py + 225, "bitboard &= (bitboard - 1)", size=12, color=POS, bold=True))
    els.append(text(rx + pw / 2.0, py + 245, "Скидання молодшого біта за 1 такт АЛП", size=11, color=INK))
    els.append(text(rx + pw / 2.0, py + 262, "Цикл виконується рівно K разів для K фігур (не 64!)", size=10, color=FIELD, bold=True))

    els.append(rect(rx + 20, py + 290, pw - 40, 65, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=4))
    els.append(text(rx + pw / 2.0, py + 310, "Перевага над скануванням 8x8:", size=11, color=FIELD, bold=True))
    els.append(text(rx + pw / 2.0, py + 328, "Генерація ходів прискорюється в 10–20 разів", size=11, color=INK))
    els.append(text(rx + pw / 2.0, py + 344, "Ключовий фактор обчислення 100+ млн вузлів/с", size=10, color=MUTED))

    els.append(mtext(W / 2.0, 452, [
        "Апаратний бітовий пошук замінює O(N) розгалужені цикли на O(1) безанкерні виклики АЛП.",
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'scheduler-bitboard-flow.svg'), W, H, *els,
                  title="Застосування: Планувальник ОС та Шахові бітборди")


if __name__ == '__main__':
    fig_clz_ctz_anatomy()
    fig_priority_encoder_tree()
    fig_wallace_tree_popcount()
    fig_scheduler_bitboard_flow()
    print("All figures generated successfully.")
