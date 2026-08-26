# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Колірна палітра теми:
# INK, LINE, FILL, BG - базові
# ACC: акцентний колір контрольної суми (золотаво-помаранчевий)
# POS: червоний (зворотний зв'язок, переповнення, XOR)
# NEG: синій (вхідні дані, потік байтів)
# FIELD: зелений (стан регістру, таблиця LUT)
ACC   = "#d97706"
BLUE  = "#2563eb"
GREEN = "#059669"
PURPLE = "#7c3aed"


# ── 1. lfsr-bitwise: Побітний зсувний регістр із зворотним зв'язком (LFSR) ────
def fig_lfsr_bitwise():
    W, H = 820, 260
    p = []

    # Заголовок блоку вхідного потоку
    p.append(text(730, 45, "Вхідний бітовий потік M(x)", size=12, color=BLUE, bold=True))
    p.append(arrow(770, 75, 685, 75, color=BLUE, sw=2.0))
    p.append(text(725, 65, "1 0 1 1 0 ...", size=13, color=BLUE))

    # Вхідний XOR (перед завантаженням молодшого біта)
    # Позиції комірок регістра
    # Регістр з 4 видимих комірок: [b31] ... [b2] [b1] [b0]
    box_w, box_h = 70, 44
    cells = [
        (100, 110, "b31 (MSB)"),
        (230, 110, "b30"),
        (370, 110, "b2"),
        (510, 110, "b1"),
        (650, 110, "b0 (LSB)")
    ]

    for cx, cy, label in cells:
        p.append(rect(cx - box_w/2, cy - box_h/2, box_w, box_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=4))
        p.append(text(cx, cy + 5, label, size=12, color=INK, bold=True))

    # Зсувні стрілки між комірками
    p.append(arrow(615, 110, 545, 110, color=LINE, sw=1.6))
    p.append(arrow(475, 110, 405, 110, color=LINE, sw=1.6))
    
    # Крапки між b30 і b2
    p.append(text(300, 110, "· · ·", size=18, color=MUTED, bold=True))
    p.append(arrow(265, 110, 280, 110, color=LINE, sw=1.4))
    p.append(arrow(320, 110, 335, 110, color=LINE, sw=1.4))
    p.append(arrow(195, 110, 135, 110, color=LINE, sw=1.6))

    # Зворотний зв'язок: лінія з MSB (b31) вгору
    p.append(line(65, 110, 45, 110, color=POS, sw=2.0))
    p.append(line(45, 110, 45, 200, color=POS, sw=2.0))
    p.append(line(45, 200, 770, 200, color=POS, sw=2.0))
    p.append(line(770, 200, 770, 110, color=POS, sw=2.0))
    p.append(arrow(770, 110, 685, 110, color=POS, sw=2.0))

    # Позначка зворотного біта
    p.append(text(380, 220, "Шина зворотного зв'язку (MSB == 1 -> XOR з коефіцієнтами G(x))", size=12, color=POS, bold=True))

    # Вентилі XOR (крани зворотного зв'язку)
    # XOR на вході b0
    p.append(circle(685, 110, 11, fill="#fef2f2", stroke=POS, sw=1.8))
    p.append(text(685, 114, "⊕", size=15, color=POS, bold=True))

    # XOR між b1 і b2
    p.append(circle(440, 110, 11, fill="#fef2f2", stroke=POS, sw=1.8))
    p.append(text(440, 114, "⊕", size=15, color=POS, bold=True))
    p.append(line(440, 200, 440, 121, color=POS, sw=1.6))

    # XOR між b30 і b31
    p.append(circle(165, 110, 11, fill="#fef2f2", stroke=POS, sw=1.8))
    p.append(text(165, 114, "⊕", size=15, color=POS, bold=True))
    p.append(line(165, 200, 165, 121, color=POS, sw=1.6))

    # Підпис кранів полінома
    p.append(text(165, 145, "g31", size=11, color=MUTED, italic=True))
    p.append(text(440, 145, "g2", size=11, color=MUTED, italic=True))
    p.append(text(685, 145, "g0", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lfsr-bitwise.svg"), W, H, *p)


# ── 2. lut-byte-remainder: Табличний обчислювач залишків (256 елементів LUT) ──
def fig_lut_byte_remainder():
    W, H = 820, 380
    p = []

    # Верхня частина: 32-бітний регістр CRC
    reg_x, reg_y = 350, 60
    reg_w, reg_h = 360, 46
    
    # 4 байти в регістрі
    byte_w = reg_w / 4
    labels = ["Байт 3 (MSB)", "Байт 2", "Байт 1", "Байт 0 (LSB)"]
    colors = ["#fef3c7", "#f1f5f9", "#f1f5f9", "#f1f5f9"]
    strokes = [ACC, LINE, LINE, LINE]

    for i in range(4):
        bx = reg_x - reg_w/2 + i * byte_w
        p.append(rect(bx, reg_y - reg_h/2, byte_w, reg_h, fill=colors[i], stroke=strokes[i], sw=1.8, rx=3))
        p.append(text(bx + byte_w/2, reg_y + 5, labels[i], size=11.5, color=INK, bold=(i==0)))

    p.append(text(reg_x, reg_y - 34, "Поточний 32-бітний регістр стану CRC", size=13, color=INK, bold=True))

    # Вхідний байт даних
    in_x, in_y = 70, 60
    p.append(rect(in_x - 45, in_y - 23, 90, 46, fill="#eff6ff", stroke=BLUE, sw=1.8, rx=4))
    p.append(text(in_x, in_y - 5, "Вхідний", size=11, color=BLUE, bold=True))
    p.append(text(in_x, in_y + 12, "байт даних", size=11, color=BLUE, bold=True))

    # Вузол формування 8-бітного індексу: XOR між Байт 3 та Вхідним байтом
    xor_idx_x, xor_idx_y = 120, 160
    p.append(circle(xor_idx_x, xor_idx_y, 14, fill="#fef2f2", stroke=POS, sw=2.0))
    p.append(text(xor_idx_x, xor_idx_y + 5, "⊕", size=18, color=POS, bold=True))

    # Лінії до XOR індексу
    p.append(arrow(in_x, in_y + 23, xor_idx_x - 10, xor_idx_y - 10, color=BLUE, sw=1.8))
    p.append(line(reg_x - reg_w/2 + byte_w/2, reg_y + reg_h/2, reg_x - reg_w/2 + byte_w/2, 130, color=ACC, sw=1.8))
    p.append(arrow(reg_x - reg_w/2 + byte_w/2, 130, xor_idx_x + 10, xor_idx_y - 10, color=ACC, sw=1.8))

    # Стрілка індексу до таблиці
    p.append(arrow(xor_idx_x, xor_idx_y + 14, xor_idx_x, 230, color=POS, sw=2.0))
    p.append(text(xor_idx_x + 65, 195, "8-бітний індекс (0..255)", size=11, color=POS, bold=True))

    # Таблиця LUT 256x32 біти
    lut_x, lut_y = 220, 270
    lut_w, lut_h = 240, 80
    p.append(rect(lut_x - lut_w/2, lut_y - lut_h/2, lut_w, lut_h, fill="#ecfdf5", stroke=GREEN, sw=2.0, rx=6))
    p.append(text(lut_x, lut_y - 18, "Таблиця залишків (LUT 256 × 32 біти)", size=12, color=GREEN, bold=True))
    p.append(text(lut_x, lut_y + 2, "LUT[index] = (index << 24) mod G(x)", size=11, color=INK, italic=True))
    p.append(text(lut_x, lut_y + 22, "256 попередньо обчислених залишків", size=10.5, color=MUTED))

    # Зсув регістра на 8 біт вліво (CRC << 8)
    shift_x, shift_y = 570, 160
    p.append(rect(shift_x - 110, shift_y - 20, 220, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    p.append(text(shift_x, shift_y + 5, "Зсув регістра: CRC << 8", size=12, color=INK, bold=True))
    p.append(arrow(reg_x + 40, reg_y + reg_h/2, shift_x, shift_y - 20, color=LINE, sw=1.8))

    # Фінальний XOR оновлення стану
    final_xor_x, final_xor_y = 570, 270
    p.append(circle(final_xor_x, final_xor_y, 16, fill="#fef2f2", stroke=POS, sw=2.2))
    p.append(text(final_xor_x, final_xor_y + 5, "⊕", size=20, color=POS, bold=True))

    # Входи до фінального XOR
    p.append(arrow(shift_x, shift_y + 20, final_xor_x, final_xor_y - 16, color=LINE, sw=1.8))
    p.append(arrow(lut_x + lut_w/2, lut_y, final_xor_x - 16, final_xor_y, color=GREEN, sw=2.0))
    p.append(text(445, 255, "32-бітний залишок із LUT", size=11, color=GREEN, bold=True))

    # Вихідний новий стан CRC
    p.append(arrow(final_xor_x, final_xor_y + 16, final_xor_x, 345, color=POS, sw=2.0))
    p.append(text(final_xor_x, 365, "Оновлений 32-бітний стан CRC", size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "lut-byte-remainder.svg"), W, H, *p)


# ── 3. slice-by-8: Паралельне 8-байтове обчислення Slice-by-8 ─────────────────
def fig_slice_by_8():
    W, H = 840, 460
    p = []

    p.append(text(W/2, 30, "64-бітне машинне слово (8 байтів даних B0 .. B7)", size=14, color=INK, bold=True))

    # 8 байтових блоків вхідного слова
    word_w = 720
    b_w = word_w / 8
    start_x = (W - word_w) / 2
    top_y = 70

    for i in range(8):
        bx = start_x + i * b_w
        p.append(rect(bx + 4, top_y - 18, b_w - 8, 36, fill="#eff6ff", stroke=BLUE, sw=1.5, rx=3))
        p.append(text(bx + b_w/2, top_y + 5, f"Байт B{i}", size=11.5, color=BLUE, bold=True))

    # Перші 4 байти змішуються з поточним станом CRC
    crc_mix_y = 145
    p.append(rect(start_x + 4, crc_mix_y - 18, b_w * 4 - 8, 36, fill="#fef3c7", stroke=ACC, sw=1.5, rx=4))
    p.append(text(start_x + b_w * 2, crc_mix_y + 5, "Поточний стан CRC (4 байти)", size=12, color=ACC, bold=True))

    for i in range(4):
        cx = start_x + i * b_w + b_w/2
        p.append(circle(cx, 110, 9, fill="#fef2f2", stroke=POS, sw=1.5))
        p.append(text(cx, 113, "⊕", size=12, color=POS, bold=True))
        p.append(line(cx, top_y + 18, cx, 101, color=BLUE, sw=1.4))
        p.append(line(cx, 119, cx, crc_mix_y - 18, color=POS, sw=1.4))

    # 8 паралельних таблиць T0 .. T7
    lut_y = 230
    lut_w_box = 80
    lut_h_box = 50

    p.append(text(W/2, 190, "8 паралельних таблиць залишків (LUT по 256 елементів кожна)", size=12, color=GREEN, bold=True))

    for i in range(8):
        cx = start_x + i * b_w + b_w/2
        p.append(rect(cx - lut_w_box/2, lut_y - lut_h_box/2, lut_w_box, lut_h_box, fill="#ecfdf5", stroke=GREEN, sw=1.6, rx=4))
        p.append(text(cx, lut_y - 6, f"Таблиця T{7-i}", size=11, color=GREEN, bold=True))
        p.append(text(cx, lut_y + 12, f"+{7-i} байтів", size=9.5, color=MUTED))

        # Стрілка від вхідного байта / XOR до таблиці
        from_y = crc_mix_y + 18 if i < 4 else top_y + 18
        p.append(arrow(cx, from_y, cx, lut_y - lut_h_box/2, color=LINE, sw=1.4))

    # Дерево фінального об'єднання (XOR усіх 8 результатів)
    tree_y = 330
    p.append(rect(start_x + 50, tree_y - 20, word_w - 100, 40, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(W/2, tree_y + 5, "Одночасний паралельний XOR: T7[B0^C0] ⊕ T6[B1^C1] ⊕ ... ⊕ T0[B7]", size=12, color=POS, bold=True))

    for i in range(8):
        cx = start_x + i * b_w + b_w/2
        p.append(arrow(cx, lut_y + lut_h_box/2, cx, tree_y - 20, color=GREEN, sw=1.4))

    # Вихід
    p.append(arrow(W/2, tree_y + 20, W/2, 405, color=POS, sw=2.2))
    p.append(text(W/2, 425, "Новий 32-бітний стан CRC після обробки відразу 8 байтів (1 ітерація)", size=13, color=INK, bold=True))

    render(os.path.join(OUT, "slice-by-8.svg"), W, H, *p)


# ── 4. rocksoft-parameters: Конвеєр параметричної моделі Rocksoft ─────────────
def fig_rocksoft_parameters():
    W, H = 820, 340
    p = []

    p.append(text(W/2, 30, "Параметричний конвеєр моделі Рока Вільямса (Rocksoft)", size=14, color=INK, bold=True))

    # Етапи:
    # 1. Вхідний потік -> RefIn (відбиття бітів)
    # 2. Init (початковий стан регістра)
    # 3. Основний цикл обчислення CRC (Poly, Width)
    # 4. RefOut (фінальне відбиття регістра)
    # 5. XorOut (фінальна маска XOR)
    # 6. Результуючий код CRC

    steps = [
        (90, 110, "Вхідні байти\nданих", "#eff6ff", BLUE),
        (220, 110, "RefIn\n(True / False)\nРеверс бітів байта", "#f8fafc", LINE),
        (370, 110, "Init\n(напр. 0xFFFFFFFF)\nПочаткова маска", "#fef3c7", ACC),
        (530, 110, "Ядро CRC (LUT / LFSR)\nPoly: 0x04C11DB7\nWidth: 32 біти", "#ecfdf5", GREEN),
        (690, 110, "RefOut\n(True / False)\nРеверс бітів слова", "#f8fafc", LINE),
    ]

    for cx, cy, label, fill_col, strk_col in steps:
        lines_cnt = len(label.split("\n"))
        bh = 65 if lines_cnt > 2 else 55
        p.append(rect(cx - 55, cy - bh/2, 110, bh, fill=fill_col, stroke=strk_col, sw=1.8, rx=5))
        ty = cy - (lines_cnt - 1) * 7
        for line_idx, ln in enumerate(label.split("\n")):
            p.append(text(cx, ty + line_idx * 15, ln, size=10.5, color=INK, bold=(line_idx==0)))

    # Стрілки між верхніми кроками
    p.append(arrow(145, 110, 165, 110, color=LINE, sw=1.6))
    p.append(arrow(275, 110, 315, 110, color=LINE, sw=1.6))
    p.append(arrow(425, 110, 475, 110, color=LINE, sw=1.6))
    p.append(arrow(585, 110, 635, 110, color=LINE, sw=1.6))

    # Перехід до нижнього рівня: XorOut і вихід
    p.append(arrow(690, 145, 690, 210, color=LINE, sw=1.8))

    low_steps = [
        (690, 245, "XorOut\n(напр. 0xFFFFFFFF)\nФінальна інверсія", "#fef2f2", POS),
        (450, 245, "Фінальний результат CRC\n(перевірка: '123456789' -> Check)", "#ecfdf5", GREEN),
        (180, 245, "Residue (Magic Constant)\nОстача при перевірці кадру з CRC\n(напр. 0xDEBB20E3)", "#f8fafc", MUTED)
    ]

    for cx, cy, label, fill_col, strk_col in low_steps:
        lines_cnt = len(label.split("\n"))
        bh = 65 if lines_cnt > 2 else 55
        bw = 180 if cx != 690 else 130
        p.append(rect(cx - bw/2, cy - bh/2, bw, bh, fill=fill_col, stroke=strk_col, sw=1.8, rx=5))
        ty = cy - (lines_cnt - 1) * 7
        for line_idx, ln in enumerate(label.split("\n")):
            p.append(text(cx, ty + line_idx * 15, ln, size=10.5, color=INK, bold=(line_idx==0)))

    p.append(arrow(625, 245, 540, 245, color=POS, sw=2.0))
    p.append(arrow(360, 245, 270, 245, color=MUTED, sw=1.6))

    # Пояснювальний текст унизу
    p.append(text(W/2, 315, "Будь-який стандарт CRC однозначно визначається цим набором із 6 параметрів", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "rocksoft-parameters.svg"), W, H, *p)


if __name__ == "__main__":
    fig_lfsr_bitwise()
    fig_lut_byte_remainder()
    fig_slice_by_8()
    fig_rocksoft_parameters()
    print("Всі 4 фігури згенеровано успішно.")
