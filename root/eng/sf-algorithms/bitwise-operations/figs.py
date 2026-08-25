# -*- coding: utf-8 -*-
"""Фігури до теми «Побітові операції та бітові маски» (bitwise-operations)
та її вставок (proj-bloom-filter, hist-bit-hacks).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори
RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
GRAY_BG  = "#f4f6f8"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"

def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)

def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ════════════════ 1. Булеві вентилі в АЛП: порозрядна паралельність ═══════════
def fig_logic_gates():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 35, "Побітові операції в АЛП: кожен розряд обчислюється незалежно", size=15, color=INK, bold=True))
    
    cols = [
        ("AND  (&)", "1 лише якщо 1 і 1", "0b1100 & 0b1010", "0b1000", FIELD, GREEN_BG),
        ("OR   (|)", "1 якщо хоч один 1", "0b1100 | 0b1010", "0b1110", NEG, BLUE_BG),
        ("XOR  (^)", "1 якщо різні (1 і 0)", "0b1100 ^ 0b1010", "0b0110", POS, RED_BG),
        ("NOT  (~)", "інверсія всіх бітів", "~0b1100 (4 біти)", "0b0011", AMBER, AMBER_BG),
    ]
    
    col_w = 195
    x_start = 30
    y_top = 65
    
    for i, (title, desc, expr, res, col, bg) in enumerate(cols):
        cx = x_start + i * (col_w + 15)
        f.append(rect(cx, y_top, col_w, 290, fill=bg, stroke=col, sw=1.8, rx=8))
        f.append(text(cx + col_w / 2, y_top + 30, title, size=15, color=col, bold=True))
        f.append(text(cx + col_w / 2, y_top + 52, desc, size=11, color=MUTED))
        f.append(line(cx + 12, y_top + 65, cx + col_w - 12, y_top + 65, color=col, sw=1, dash="3,3"))
        
        ty = y_top + 88
        f.append(text(cx + 35, ty, "A", size=12, color=INK, bold=True))
        if "NOT" not in title:
            f.append(text(cx + 80, ty, "B", size=12, color=INK, bold=True))
            f.append(text(cx + 145, ty, "Вихід", size=12, color=col, bold=True))
            f.append(line(cx + 20, ty + 8, cx + col_w - 20, ty + 8, color=LINE, sw=1))
            
            rows = [
                ("0", "0", "0"),
                ("0", "1", "1" if "OR" in title or "XOR" in title else "0"),
                ("1", "0", "1" if "OR" in title or "XOR" in title else "0"),
                ("1", "1", "1" if "AND" in title or "OR" in title else "0"),
            ]
            for r_i, (a_val, b_val, out_val) in enumerate(rows):
                ry = ty + 24 + r_i * 20
                f.append(text(cx + 35, ry, a_val, size=12, color=MUTED))
                f.append(text(cx + 80, ry, b_val, size=12, color=MUTED))
                f.append(text(cx + 145, ry, out_val, size=12, color=col, bold=True))
        else:
            f.append(text(cx + 130, ty, "Вихід (~A)", size=12, color=col, bold=True))
            f.append(line(cx + 20, ty + 8, cx + col_w - 20, ty + 8, color=LINE, sw=1))
            rows_not = [("0", "1"), ("1", "0")]
            for r_i, (a_val, out_val) in enumerate(rows_not):
                ry = ty + 32 + r_i * 26
                f.append(text(cx + 35, ry, a_val, size=13, color=MUTED))
                f.append(text(cx + 130, ry, out_val, size=13, color=col, bold=True))
        
        f.append(line(cx + 12, y_top + 195, cx + col_w - 12, y_top + 195, color=col, sw=1, dash="3,3"))
        f.append(text(cx + col_w / 2, y_top + 215, "Приклад:", size=11, color=MUTED))
        f.append(mono(cx + col_w / 2, y_top + 238, expr, size=11, color=INK, anchor="middle", bold=True))
        f.append(text(cx + col_w / 2, y_top + 258, "↓", size=13, color=col, bold=True))
        f.append(mono(cx + col_w / 2, y_top + 276, "= " + res, size=12, color=col, anchor="middle", bold=True))

    f.append(text(W / 2, 390, "Жодна операція не переносить біти між розрядами — усі N розрядів обробляються одночасно за 1 такт.", size=12, color=INK, bold=True))
    out("logic-gates-truth.svg", W, H, *f, title="Побітові операції в АЛП: булеві вентилі")


# ════════════════ 2. Порівняння бітових зсувів ════════════════════════════════
def fig_shifts():
    W, H = 880, 440
    f = []
    f.append(text(W / 2, 32, "Види бітових зсувів: логічний, арифметичний та циклічний", size=15, color=INK, bold=True))
    
    cell_w, cell_h = 32, 32
    
    def draw_reg(x, y, bits, highlight_idx=None, hl_color=FIELD):
        elems = []
        for idx, bit in enumerate(bits):
            bx = x + idx * cell_w
            is_hl = (highlight_idx is not None and idx in highlight_idx)
            bg = "#eaf6ee" if is_hl else "#ffffff"
            stroke_c = hl_color if is_hl else LINE
            elems.append(rect(bx, y, cell_w, cell_h, fill=bg, stroke=stroke_c, sw=1.5, rx=3))
            elems.append(mono(bx + cell_w / 2, y + cell_h * 0.68, bit, size=13, color=stroke_c if is_hl else INK, anchor="middle", bold=True))
        return "".join(elems)

    # 1. Логічний зсув вліво (SHL)
    y1 = 65
    f.append(rect(30, y1, 820, 75, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(48, y1 + 25, "Логічний вліво (SHL / <<)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(text(48, y1 + 45, "x << 1  (множення на 2)", size=11, color=MUTED, anchor="start"))
    f.append(draw_reg(270, y1 + 22, ["1", "0", "1", "1", "0", "0", "1", "0"]))
    f.append(arrow(545, y1 + 38, 575, y1 + 38, color=FIELD, sw=2))
    f.append(draw_reg(590, y1 + 22, ["0", "1", "1", "0", "0", "1", "0", "0"], highlight_idx=[7], hl_color=FIELD))
    f.append(text(590 + 7 * cell_w + 16, y1 + 14, "+0 справа", size=10, color=FIELD, bold=True))
    f.append(text(250, y1 + 38, "CF ← [1]", size=11, color=POS, bold=True))

    # 2. Логічний зсув вправо (SHR)
    y2 = 150
    f.append(rect(30, y2, 820, 75, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(48, y2 + 25, "Логічний вправо (SHR / >> unsigned)", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(48, y2 + 45, "u >> 1  (ділення на 2 без знаку)", size=11, color=MUTED, anchor="start"))
    f.append(draw_reg(270, y2 + 22, ["1", "0", "1", "1", "0", "0", "1", "0"]))
    f.append(arrow(545, y2 + 38, 575, y2 + 38, color=NEG, sw=2))
    f.append(draw_reg(590, y2 + 22, ["0", "1", "0", "1", "1", "0", "0", "1"], highlight_idx=[0], hl_color=NEG))
    f.append(text(575, y2 + 14, "зліва +0", size=10, color=NEG, bold=True))
    f.append(text(545, y2 + 65, "→ CF [0]", size=11, color=MUTED, bold=True))

    # 3. Арифметичний зсув вправо (SAR / ASR)
    y3 = 235
    f.append(rect(30, y3, 820, 75, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(48, y3 + 25, "Арифметичний вправо (SAR / ASR)", size=13, color=POS, anchor="start", bold=True))
    f.append(text(48, y3 + 45, "s >> 1  (дублює знаковий біт MSB)", size=11, color=MUTED, anchor="start"))
    f.append(draw_reg(270, y3 + 22, ["1", "0", "1", "1", "0", "0", "1", "0"], highlight_idx=[0], hl_color=POS))
    f.append(arrow(545, y3 + 38, 575, y3 + 38, color=POS, sw=2))
    f.append(draw_reg(590, y3 + 22, ["1", "1", "0", "1", "1", "0", "0", "1"], highlight_idx=[0, 1], hl_color=POS))
    f.append(text(575, y3 + 14, "дублює MSB", size=10, color=POS, bold=True))
    f.append(text(285, y3 + 65, "MSB = 1 (знак −)", size=10, color=POS, bold=True))

    # 4. Циклічний зсув (ротація ROR / ROL)
    y4 = 320
    f.append(rect(30, y4, 820, 75, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(48, y4 + 25, "Циклічна ротація (ROR / ROL)", size=13, color=AMBER, anchor="start", bold=True))
    f.append(text(48, y4 + 45, "std::rotr / std::rotl (без втрат)", size=11, color=MUTED, anchor="start"))
    f.append(draw_reg(270, y4 + 22, ["1", "0", "1", "1", "0", "0", "1", "0"], highlight_idx=[7], hl_color=AMBER))
    f.append(arrow(545, y4 + 38, 575, y4 + 38, color=AMBER, sw=2))
    f.append(draw_reg(590, y4 + 22, ["0", "1", "0", "1", "1", "0", "0", "1"], highlight_idx=[0], hl_color=AMBER))
    f.append(text(710, y4 + 65, "LSB [0] переходить у старший розряд MSB", size=10, color=AMBER, bold=True))

    f.append(text(W / 2, 420, "Логічний зсув вставляє нулі; арифметичний зберігає знак додаткового коду; ротація закольцовує біти.", size=12, color=INK, bold=True))
    out("shifts-comparison.svg", W, H, *f, title="Види бітових зсувів: SHL, SHR, SAR, ROL/ROR")


# ════════════════ 3. Чотири дії з бітовими масками ════════════════════════════
def fig_bitmask_ops():
    W, H = 880, 410
    f = []
    f.append(text(W / 2, 32, "Чотири канонічні операції з бітовими масками", size=15, color=INK, bold=True))

    boxes = [
        ("1. Встановити біт k (Set)", "flags |= (1U << k)", "flags | 0b00100000", "Гарантує 1 у k-му розряді", FIELD, GREEN_BG),
        ("2. Скинути біт k (Clear)", "flags &= ~(1U << k)", "flags & 0b11011111", "Гарантує 0 у k-му розряді", NEG, BLUE_BG),
        ("3. Інвертувати біт k (Toggle)", "flags ^= (1U << k)", "flags ^ 0b00100000", "Перемикає 0 ↔ 1 (керований NOT)", POS, RED_BG),
        ("4. Перевірити біт k (Test)", "(flags & (1U << k)) != 0", "flags & 0b00100000", "Повертає true якщо біт піднято", AMBER, AMBER_BG),
    ]

    bx_w = 395
    bx_h = 145
    coords = [
        (35, 60),
        (450, 60),
        (35, 220),
        (450, 220),
    ]

    for (title, code_str, mask_str, note, col, bg), (bx, by) in zip(boxes, coords):
        f.append(rect(bx, by, bx_w, bx_h, fill=bg, stroke=col, sw=1.8, rx=8))
        f.append(text(bx + 18, by + 28, title, size=14, color=col, anchor="start", bold=True))
        f.append(rect(bx + 18, by + 42, bx_w - 36, 32, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        f.append(mono(bx + 30, by + 63, code_str, size=13, color=INK, bold=True))
        f.append(text(bx + 18, by + 98, "Дія маски: ", size=11, color=MUTED, anchor="start"))
        f.append(mono(bx + 85, by + 98, mask_str, size=11, color=col, bold=True))
        f.append(text(bx + 18, by + 124, note, size=11, color=INK, anchor="start", italic=True))

    f.append(text(W / 2, 390, "Маска (1U << k) ізолює один розряд; комбінація бітів створюється через побітове OR масок.", size=12, color=INK, bold=True))
    out("bitmask-ops.svg", W, H, *f, title="Операції з бітовими масками: Set, Clear, Toggle, Test")


# ════════════════ 4. Математика трюку x & -x (Two's Complement LSB) ════════════
def fig_twos_comp_lsb():
    W, H = 880, 390
    f = []
    f.append(text(W / 2, 32, "Виділення молодшої одиниці: x & -x у додатковому коді", size=15, color=INK, bold=True))

    cell_w, cell_h = 42, 36
    x_box = 240

    def draw_row(y, label, bits, hl_idx=None, hl_col=FIELD, note=""):
        elems = []
        elems.append(text(x_box - 20, y + cell_h * 0.65, label, size=13, color=INK, anchor="end", bold=True))
        for idx, bit in enumerate(bits):
            bx = x_box + idx * cell_w
            is_hl = (hl_idx is not None and idx in hl_idx)
            bg = "#eaf6ee" if is_hl else "#ffffff"
            st = hl_col if is_hl else LINE
            elems.append(rect(bx, y, cell_w, cell_h, fill=bg, stroke=st, sw=1.5, rx=4))
            elems.append(mono(bx + cell_w / 2, y + cell_h * 0.68, bit, size=14, color=st if is_hl else INK, anchor="middle", bold=True))
        if note:
            elems.append(text(x_box + 8 * cell_w + 18, y + cell_h * 0.65, note, size=12, color=MUTED, anchor="start"))
        return "".join(elems)

    # 1. Початкове x (наприклад, 40 = 0b00101000)
    y1 = 70
    f.append(draw_row(y1, "x =", ["0", "0", "1", "0", "1", "0", "0", "0"], hl_idx=[4], hl_col=POS, note="(молодша одиниця на позиції 3)"))

    # 2. Порозрядний NOT (~x)
    y2 = 125
    f.append(draw_row(y2, "~x =", ["1", "1", "0", "1", "0", "1", "1", "1"], hl_idx=[4], hl_col=MUTED, note="(усі біти інвертовано: 1 ↔ 0)"))

    # 3. Додавання 1 (-x = ~x + 1)
    y3 = 180
    f.append(draw_row(y3, "-x (~x + 1) =", ["1", "1", "0", "1", "1", "0", "0", "0"], hl_idx=[4], hl_col=NEG, note="(перенос 1 біжить до першого нуля)"))

    # Розділювач
    f.append(line(x_box - 100, 230, x_box + 8 * cell_w + 240, 230, color=LINE, sw=2))
    f.append(text(x_box - 20, 248, "побітове AND (&)", size=12, color=FIELD, anchor="end", bold=True))

    # 4. Результат x & -x
    y4 = 260
    f.append(draw_row(y4, "x & -x =", ["0", "0", "0", "0", "1", "0", "0", "0"], hl_idx=[4], hl_col=FIELD, note="= 0b00001000 (лишився рівно 1 молодший біт!)"))

    # Пояснення
    f.append(rect(60, 315, 760, 50, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(W / 2, 336, "Чому це працює: додавання 1 до ~x перетворює всі молодші одиниці на 0, а перший 0 на 1.", size=12, color=INK, bold=True))
    f.append(text(W / 2, 353, "Старші біти залишаються протилежними (~x і x), тому при AND вони обнуляються; збігається лише цей 1 біт.", size=11, color=MUTED))

    out("twos-complement-lsb.svg", W, H, *f, title="Математика трюку x & -x у додатковому коді")


# ════════════════ 5. Організація Bitset у пам'яті ═════════════════════════════
def fig_bitset():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 32, "Структура даних Bitset: адресація 64-бітних машинних слів", size=15, color=INK, bold=True))

    # Індекс шуканого біта
    f.append(rect(50, 60, 780, 55, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(70, 93, "Шуканий біт index = 139:", size=13, color=INK, anchor="start", bold=True))
    f.append(mono(250, 93, "word_idx = 139 / 64 = 2   (індекс 64-бітного слова: 139 >> 6)", size=12, color=FIELD, bold=True))
    f.append(mono(250, 107, "bit_offset = 139 % 64 = 11  (зсув біта всередині слова: 139 & 63)", size=12, color=NEG, bold=True))

    # Масив слів uint64_t words[N]
    words_y = 140
    f.append(text(50, words_y + 20, "uint64_t words[] у пам'яті:", size=13, color=INK, anchor="start", bold=True))

    word_w = 175
    word_h = 80
    start_x = 50

    for i in range(4):
        wx = start_x + i * (word_w + 20)
        is_target = (i == 2)
        bg = GREEN_BG if is_target else "#ffffff"
        st = FIELD if is_target else LINE
        f.append(rect(wx, words_y + 35, word_w, word_h, fill=bg, stroke=st, sw=1.8 if is_target else 1.2, rx=6))
        f.append(text(wx + word_w / 2, words_y + 58, "words[%d]" % i, size=13, color=st if is_target else INK, bold=True))
        f.append(text(wx + word_w / 2, words_y + 78, "біти [%d…%d]" % (i * 64, (i + 1) * 64 - 1), size=11, color=MUTED))
        if is_target:
            f.append(text(wx + word_w / 2, words_y + 100, "★ наш біт 139 тут", size=10, color=FIELD, bold=True))

    # Деталізація слова words[2]
    det_y = 265
    f.append(rect(50, det_y, 780, 95, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(70, det_y + 25, "Збільшено words[2] (біти 128…191):", size=13, color=FIELD, anchor="start", bold=True))

    b_w = 11
    b_h = 24
    b_start_x = 70
    for b in range(64):
        bx = b_start_x + b * b_w
        is_11 = (b == 11)
        bg = POS if is_11 else "#ffffff"
        st = POS if is_11 else "#999999"
        f.append(rect(bx, det_y + 38, b_w, b_h, fill=bg, stroke=st, sw=1, rx=1))

    f.append(text(b_start_x + 11 * b_w + 5, det_y + 80, "↑ біт 11 (загальний #139: mask = 1ULL << 11)", size=11, color=POS, bold=True))
    f.append(text(b_start_x + 60 * b_w, det_y + 80, "біти 0…63", size=10, color=MUTED))

    f.append(text(W / 2, 395, "Bitset упаковує 64 булеві прапорці в одне машинне слово uint64_t, скорочуючи пам'ять у 8 разів.", size=12, color=INK, bold=True))
    out("bitset-indexing.svg", W, H, *f, title="Індексація та адресація в Bitset")


# ════════════════ 6. Фільтр Блума (Bloom Filter) ══════════════════════════════
def fig_bloom_filter():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 32, "Принцип роботи фільтра Блума на базі бітового масиву", size=15, color=INK, bold=True))

    # Вхідний ключ "alice"
    f.append(rect(50, 70, 160, 60, fill=BLUE_BG, stroke=NEG, sw=1.8, rx=6))
    f.append(text(130, 97, "Ключ: 'alice'", size=13, color=NEG, bold=True))
    f.append(text(130, 115, "вставка в фільтр", size=10, color=MUTED))

    # k хеш-функцій
    hashes = [("h₁(x) = 3", 3, FIELD), ("h₂(x) = 7", 7, POS), ("h₃(x) = 13", 13, AMBER)]
    for idx, (h_label, bit_pos, col) in enumerate(hashes):
        hy = 60 + idx * 35
        f.append(arrow(210, 100, 270, hy + 15, color=NEG, sw=1.5))
        f.append(rect(270, hy, 120, 30, fill=GRAY_BG, stroke=col, sw=1.5, rx=4))
        f.append(text(330, hy + 19, h_label, size=11, color=col, bold=True))
        target_bx = 440 + bit_pos * 24 + 12
        f.append(arrow(390, hy + 15, target_bx, 190, color=col, sw=1.5))

    # Бітовий масив фільтра (16 бітів для наочності)
    arr_y = 200
    f.append(text(W / 2, arr_y - 15, "Бітовий масив Bitset (m = 16 бітів):", size=12, color=INK, bold=True))

    arr_w = 24
    arr_h = 36
    arr_start_x = 440 - (16 * arr_w) / 2 + 100

    set_bits = [3, 7, 13]
    for b in range(16):
        bx = arr_start_x + b * arr_w
        is_set = (b in set_bits)
        bg = GREEN_BG if is_set else "#ffffff"
        st = FIELD if is_set else LINE
        f.append(rect(bx, arr_y, arr_w, arr_h, fill=bg, stroke=st, sw=1.5 if is_set else 1, rx=3))
        f.append(mono(bx + arr_w / 2, arr_y + arr_h * 0.68, "1" if is_set else "0", size=13, color=FIELD if is_set else MUTED, anchor="middle", bold=is_set))
        f.append(text(bx + arr_w / 2, arr_y + arr_h + 14, str(b), size=9, color=MUTED))

    # Перевірка наявності (Query)
    qy = 295
    f.append(rect(50, qy, 780, 85, fill=GRAY_BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(70, qy + 25, "Перевірка ключа: обчислити h₁(y), h₂(y), h₃(y) і перевірити відповідні біти", size=12, color=INK, anchor="start", bold=True))
    f.append(rect(70, qy + 40, 340, 32, fill=GREEN_BG, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(240, qy + 60, "Хоч один біт == 0 → ТОЧНО НЕМАЄ (100%)", size=11, color=FIELD, bold=True))
    f.append(rect(430, qy + 40, 380, 32, fill=AMBER_BG, stroke=AMBER, sw=1.2, rx=4))
    f.append(text(620, qy + 60, "Усі біти == 1 → МОЖЛИВО Є (false positive)", size=11, color=AMBER, bold=True))

    f.append(text(W / 2, 402, "Фільтр Блума ніколи не дає хибнонегативних відповідей, заощаджуючи дорогі дискові чи мережеві звернення.", size=12, color=INK, bold=True))
    out("bloom-filter.svg", W, H, *f, title="Фільтр Блума на базі бітового масиву")


# ════════════════ 7. Хронологія еволюції бітових трюків ════════════════════════
def fig_hakmem_timeline():
    W, H = 880, 380
    f = []
    f.append(text(W / 2, 32, "Еволюція бітових операцій: від PDP-10 до апаратних інструкцій", size=15, color=INK, bold=True))

    # Вісь часу
    f.append(line(70, 160, 810, 160, color=LINE, sw=3))
    f.append(arrow(800, 160, 830, 160, color=LINE, sw=3))

    milestones = [
        ("1972", "HAKMEM", "MIT AI Lab (PDP-6/10)\nБілер, Госпер, Шреппель\nПерші бітові хаки x & -x", 120, -110, FIELD, GREEN_BG),
        ("1987", "Superoptimizer", "Алексія Массалін\nГенерація найкоротших\nпослідовностей інструкцій", 320, 20, NEG, BLUE_BG),
        ("2002", "Hacker's Delight", "Генрі Воррен\nЕнциклопедія бітових алгоритмів\nта математичних доведень", 520, -110, POS, RED_BG),
        ("2013-2024", "BMI / Zbb у залізі", "x86 BMI1/BMI2 (BLSI, PEXT)\nRISC-V Zbb, ARM Neon\nТрюки стали 1 інструкцією", 710, 20, AMBER, AMBER_BG),
    ]

    for year, title, desc, cx, dy, col, bg in milestones:
        # Точка на осі
        f.append(circle(cx, 160, 6, fill=col, stroke="#ffffff", sw=2))
        f.append(text(cx, 160 + (18 if dy < 0 else -12), year, size=12, color=col, bold=True))
        
        # Лінія до картки
        box_y = 160 + dy
        f.append(line(cx, 160, cx, box_y + (75 if dy < 0 else 0), color=col, sw=1.2, dash="3,3"))
        
        # Картка
        f.append(rect(cx - 85, box_y, 170, 75, fill=bg, stroke=col, sw=1.5, rx=6))
        f.append(text(cx, box_y + 20, title, size=12, color=col, bold=True))
        lines = desc.split("\n")
        for l_i, l_txt in enumerate(lines):
            f.append(text(cx, box_y + 38 + l_i * 14, l_txt, size=9, color=MUTED))

    f.append(text(W / 2, 345, "Сучасні компілятори автоматично замінюють вирази x & -x на прямі інструкції процесора на зразок BLSI.", size=12, color=INK, bold=True))
    out("hakmem-timeline.svg", W, H, *f, title="Еволюція бітових трюків: від HAKMEM до апаратних інструкцій")


if __name__ == "__main__":
    fig_logic_gates()
    fig_shifts()
    fig_bitmask_ops()
    fig_twos_comp_lsb()
    fig_bitset()
    fig_bloom_filter()
    fig_hakmem_timeline()
    print("All figures generated successfully in ./img/")
