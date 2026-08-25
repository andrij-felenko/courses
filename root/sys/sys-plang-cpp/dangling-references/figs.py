# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'dangling-references'."""

import sys
import os

# scripts/ лежить на 4 рівні вище:
# dangling-references -> lifetime -> cpp-standards -> reference -> courses/scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_stack_frame_dangling():
    """Фігура 1: Руйнування стекового кадру та перезапис пам'яті новим викликом."""
    w, h = 820, 360
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    s.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Заголовок / дві фази
    s.append(text(210, 30, "Фаза 1: виклик make_widget()", size=15, bold=True, color=INK))
    s.append(text(610, 30, "Фаза 2: повернення та виклик compute()", size=15, bold=True, color=POS))

    # Розділювач
    s.append(line(410, 20, 410, 340, color=MUTED, sw=1.0, dash="4,4"))

    # --- ЛІВА ПАНЕЛЬ ---
    # Кадр main
    tb, _, _ = textbox(210, 80, "Кадр main()\nWidget* ptr;", size=12, pad=8, fill=FILL, stroke=LINE, min_w=280)
    s.append(tb)

    # Кадр make_widget
    tb, _, _ = textbox(210, 175, "Кадр make_widget()\nWidget local_w { .id = 42 };  [0x7ffd10]\n(адреса активна, пам'ять валідна)",
                       size=12, pad=8, fill="#e8f4fc", stroke=NEG, min_w=280)
    s.append(tb)

    # Вказівник ptr -> local_w
    s.append(line(120, 95, 120, 145, color=NEG, sw=2.0))
    s.append(line(120, 145, 140, 145, color=NEG, sw=2.0))
    s.append('<polygon points="140,140 150,145 140,150" fill="%s"/>' % NEG)
    s.append(text(210, 240, "ptr = &local_w; return ptr; (поки що коректно)", size=11, color=MUTED))

    # Стан стека
    s.append(text(210, 290, "Вказівник стека RSP дивиться нижче [0x7ffd10]", size=11, bold=True, color=FIELD))
    s.append(line(70, 310, 350, 310, color=FIELD, sw=2.0))
    s.append(text(210, 330, "Пам'ять кадру make_widget() гарантовано цілісна", size=10, color=MUTED))

    # --- ПРАВА ПАНЕЛЬ ---
    # Кадр main
    tb, _, _ = textbox(610, 80, "Кадр main()\nWidget* ptr = 0x7ffd10; (висячий вказівник!)", size=12, pad=8, fill=FILL, stroke=POS, min_w=280)
    s.append(tb)

    # Новий кадр compute() на тому самому місці
    tb, _, _ = textbox(610, 175, "Новий кадр compute()\ndouble buffer[64];  [0x7ffd10]\n(перезаписав пам'ять local_w сміттям)",
                       size=12, pad=8, fill="#fdeeed", stroke=POS, min_w=280)
    s.append(tb)

    # Вказівник ptr -> стара адреса, де вже лежить double
    s.append(line(500, 95, 500, 145, color=POS, sw=2.0))
    s.append(line(500, 145, 520, 145, color=POS, sw=2.0))
    s.append('<polygon points="520,140 530,145 520,150" fill="%s"/>' % POS)

    s.append(text(610, 240, "Звернення ptr->id читає біти числа double (UB)", size=11, bold=True, color=POS))

    # Стан стека
    s.append(text(610, 290, "RSP змістився: старий кадр звільнено і перекрито", size=11, bold=True, color=POS))
    s.append(line(470, 310, 750, 310, color=POS, sw=2.0))
    s.append(text(610, 330, "Звернення до мертвого стека руйнує дані наступних викликів", size=10, color=MUTED))

    s.append("</svg>")
    path = os.path.join(IMG_DIR, "stack-frame-dangling.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print("Created:", path)


def fig_temporary_lifetime_break():
    """Фігура 2: Подовження життя тимчасового об'єкта та точки, де ланцюг рветься."""
    w, h = 820, 380
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    s.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    s.append(text(210, 30, "Пряме зв'язування: подовження ДІЄ", size=14, bold=True, color=FIELD))
    s.append(text(610, 30, "Опосередкований виклик: подовження НЕ діє", size=14, bold=True, color=POS))
    s.append(line(410, 20, 410, 360, color=MUTED, sw=1.0, dash="4,4"))

    # --- ЛІВА ПАНЕЛЬ ---
    tb, _, _ = textbox(210, 80, "const std::string& ref = get_name();", size=12, pad=8, fill="#eafaf1", stroke=FIELD, min_w=320)
    s.append(tb)

    tb, _, _ = textbox(210, 160, "Тимчасовий рядок std::string\n(матеріалізований prvalue)", size=12, pad=8, fill="#f4f6f8", stroke=LINE, min_w=280)
    s.append(tb)

    s.append(line(210, 105, 210, 130, color=FIELD, sw=2.0))
    s.append('<polygon points="205,130 210,140 215,130" fill="%s"/>' % FIELD)
    s.append(text(300, 120, "зв'язує безпосередньо", size=10, color=FIELD))

    # Смуга життя
    s.append(rect(50, 230, 320, 36, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=4))
    s.append(text(210, 252, "Час життя тимчасового = часу життя ref", size=11, bold=True, color=FIELD))

    tb, _, _ = textbox(210, 315, "Деструктор тимчасового об'єкта викличеться\nлише наприкінці блоку, де оголошено ref",
                       size=11, pad=6, fill=FILL, stroke=LINE, min_w=320)
    s.append(tb)

    # --- ПРАВА ПАНЕЛЬ ---
    tb, _, _ = textbox(610, 80, "const auto& ref = std::min(get_a(), get_b());", size=12, pad=8, fill="#fdeeed", stroke=POS, min_w=320)
    s.append(tb)

    tb, _, _ = textbox(610, 160, "std::min(const T& a, const T& b) повертає 'const T&'\n(компілятор не аналізує тіло функції)",
                       size=11, pad=6, fill="#f4f6f8", stroke=POS, min_w=320)
    s.append(tb)

    s.append(line(610, 105, 610, 130, color=POS, sw=2.0))
    s.append('<polygon points="605,130 610,140 615,130" fill="%s"/>' % POS)

    # Смуга життя
    s.append(rect(450, 230, 150, 36, fill="#fadbd8", stroke=POS, sw=1.5, rx=4))
    s.append(text(525, 252, "Живий до крапки з комою ';'", size=10, bold=True, color=POS))

    s.append('<rect x="605.0" y="230.0" width="165.0" height="36.0" rx="4" fill="#eaecee" stroke="%s" stroke-width="1.0" stroke-dasharray="3,3"/>' % MUTED)
    s.append(text(687, 252, "Мертвий об'єкт (dangling!)", size=10, bold=True, color=POS))

    tb, _, _ = textbox(610, 315, "ref вказує на зруйнований об'єкт уже на наступному рядку:\nчитання через ref — невизначена поведінка (UB)",
                       size=11, pad=6, fill="#fdeeed", stroke=POS, min_w=340)
    s.append(tb)

    s.append("</svg>")
    path = os.path.join(IMG_DIR, "temporary-lifetime-break.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print("Created:", path)


def fig_vector_reallocation_invalidation():
    """Фігура 3: Інвалідація посилань та ітераторів при зростанні буфера std::vector."""
    w, h = 820, 360
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    s.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    s.append(text(410, 30, "Інвалідація посилань при std::vector::push_back() (size == capacity)", size=15, bold=True, color=INK))

    # Стан 1: До вставки
    s.append(text(120, 75, "1. До вставки:", size=13, bold=True, color=INK))
    s.append(text(120, 95, "capacity = 2, size = 2", size=11, color=MUTED))

    # Комірки буфера 1
    s.append(rect(240, 65, 90, 45, fill="#e8f4fc", stroke=NEG, sw=1.5))
    s.append(text(285, 92, "item 0", size=12, bold=True, color=INK))

    s.append(rect(330, 65, 90, 45, fill="#e8f4fc", stroke=NEG, sw=1.5))
    s.append(text(375, 92, "item 1", size=12, bold=True, color=INK))

    # Посилання ref на item 0
    tb, _, _ = textbox(160, 160, "auto& ref = vec[0];\n(адреса 0x1000)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=140)
    s.append(tb)
    s.append(line(210, 140, 260, 115, color=NEG, sw=1.8))
    s.append('<polygon points="255,112 265,112 262,122" fill="%s"/>' % NEG)

    # Дія
    s.append(text(410, 175, "vec.push_back(item2); → перевиділення пам'яті (capacity = 4)", size=12, bold=True, color=POS))
    s.append(line(100, 195, 720, 195, color=MUTED, sw=1.0, dash="3,3"))

    # Стан 2: Після вставки
    s.append(text(120, 240, "2. Після вставки:", size=13, bold=True, color=INK))

    # Старий буфер - звільнений (dead)
    s.append('<rect x="240.0" y="220.0" width="180.0" height="45.0" rx="6" fill="#fbeee6" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % POS)
    s.append(text(330, 247, "Старий буфер: ЗВІЛЬНЕНО (delete[])", size=11, bold=True, color=POS))

    # Новий буфер
    s.append(rect(480, 220, 80, 45, fill="#eafaf1", stroke=FIELD, sw=1.5))
    s.append(text(520, 247, "item 0", size=11, bold=True, color=FIELD))

    s.append(rect(560, 220, 80, 45, fill="#eafaf1", stroke=FIELD, sw=1.5))
    s.append(text(600, 247, "item 1", size=11, bold=True, color=FIELD))

    s.append(rect(640, 220, 80, 45, fill="#eafaf1", stroke=FIELD, sw=1.5))
    s.append(text(680, 247, "item 2", size=11, bold=True, color=FIELD))

    s.append(rect(720, 220, 80, 45, fill="#f4f6f8", stroke=MUTED, sw=1.0))
    s.append(text(760, 247, "вільно", size=11, color=MUTED))

    # Старе посилання дивиться на звільнену пам'ять
    s.append(line(160, 190, 250, 220, color=POS, sw=2.0))
    s.append('<polygon points="245,212 255,220 248,225" fill="%s"/>' % POS)

    tb, _, _ = textbox(410, 320, "Посилання ref (та всі старі ітератори) вказують на 0x1000 — Use-After-Free!",
                       size=12, pad=6, fill="#fdeeed", stroke=POS, min_w=620)
    s.append(tb)

    s.append("</svg>")
    path = os.path.join(IMG_DIR, "vector-reallocation-invalidation.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print("Created:", path)


def fig_asan_shadow_memory():
    """Фігура 4: Відображення оперативної пам'яті в тіньову пам'ять AddressSanitizer."""
    w, h = 860, 400
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    s.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    s.append(text(430, 28, "Архітектура Shadow Memory в AddressSanitizer (масштаб 8:1)", size=15, bold=True, color=INK))

    # Схема відображення
    s.append(text(430, 58, "ShadowAddr = (AppAddr &gt;&gt; 3) + 0x7fff8000 (x86-64 Linux)", size=12, bold=True, color=NEG))

    # Ліва частина: Звичайна пам'ять (8 байтів)
    s.append(text(220, 95, "Пам'ять програми (8 байтів)", size=13, bold=True, color=INK))

    # 8 байтних блоків
    for i in range(8):
        bx = 80 + i * 35
        s.append(rect(bx, 115, 35, 45, fill="#e8f4fc", stroke=LINE, sw=1.2))
        s.append(text(bx + 17.5, 142, "+%d" % i, size=11, color=INK))

    s.append(text(220, 180, "Блок адреси 0x7ffd10..0x7ffd17", size=11, color=MUTED))

    # Стрілка масштабування
    s.append(line(380, 137, 470, 137, color=NEG, sw=2.0))
    s.append('<polygon points="465,132 475,137 465,142" fill="%s"/>' % NEG)
    s.append(text(425, 125, "стиснення 8:1", size=11, color=NEG))

    # Права частина: 1 тіньовий байт
    s.append(text(620, 95, "Тіньовий байт (1 байт)", size=13, bold=True, color=INK))
    s.append(rect(570, 115, 100, 45, fill="#d4efdf", stroke=FIELD, sw=2.0))
    s.append(text(620, 142, "0x00", size=14, bold=True, color=FIELD))
    s.append(text(620, 180, "Усі 8 байтів доступні", size=11, color=FIELD))

    # Таблиця значень тіньових байтів
    s.append(line(50, 210, 810, 210, color=MUTED, sw=1.0))
    s.append(text(430, 230, "Значення тіньового байта при виявленні висячих вказівників:", size=12, bold=True, color=INK))

    states = [
        ("0x00", "Доступний", "Усі 8 байтів валідні\nдля читання/запису", "#d4efdf", FIELD),
        ("0x01..07", "Частковий", "Лише перші k байтів\nвалідні в буфері", "#fcf3cf", "#b7950b"),
        ("0xFD", "Heap UAF", "Пам'ять купи звільнена\nчерез delete / free", "#fadbd8", POS),
        ("0xF5", "Stack UAR", "Кадр стека помер\n(use-after-return)", "#fadbd8", POS),
        ("0xF1 / 0xF3", "Redzone", "Червона зона стека\n(межа між змінними)", "#fadbd8", POS)
    ]

    centers = [110, 270, 430, 590, 750]
    for i, (code, title, desc, fcolor, scolor) in enumerate(states):
        cx = centers[i]
        s.append(rect(cx - 70, 250, 140, 125, fill=fcolor, stroke=scolor, sw=1.2, rx=4))
        s.append(text(cx, 272, code, size=13, bold=True, color=scolor))
        s.append(text(cx, 292, title, size=11, bold=True, color=INK))
        lines = desc.split("\n")
        s.append(text(cx, 318, lines[0], size=10, color=INK))
        if len(lines) > 1:
            s.append(text(cx, 334, lines[1], size=10, color=MUTED))

    s.append("</svg>")
    path = os.path.join(IMG_DIR, "asan-shadow-memory.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print("Created:", path)


if __name__ == "__main__":
    fig_stack_frame_dangling()
    fig_temporary_lifetime_break()
    fig_vector_reallocation_invalidation()
    fig_asan_shadow_memory()
