# -*- coding: utf-8 -*-
"""Фігури до теми «std::span та суцільні зрізи пам'яті»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Динамічний vs Статичний extent у std::span ────────────────────────────
def fig_span_layout():
    W, H = 940, 440
    f = []

    f.append(text(50, 35, "Макет пам'яті std::span: Dynamic Extent проти Static Extent", size=16, color=INK, anchor="start", bold=True))

    # Верхня панель: Dynamic Extent
    f.append(text(50, 70, "1. Динамічний розмір: std::span<int> (Extent = std::dynamic_extent, sizeof = 16 байтів)", size=13, color=FIELD, anchor="start", bold=True))
    
    # Об'єкт span (стек)
    f.append(fitbox(50, 90, 240, 110, "std::span<int>\nptr: 0x7fff... ──┐\nsize: 4       │\n(розмір у runtime) │", size=12, fill="#eef2f7", stroke=LINE))
    
    # Стрілка на масив
    f.append(arrow(290, 145, 470, 145, color=NEG, sw=2))

    # Суцільний масив пам'яті
    f.append(fitbox(475, 90, 415, 110, "Суцільний масив у пам'яті (C-array / vector / array)\n[10] | [20] | [30] | [40]\n0x7fff00 | 0x7fff04 | 0x7fff08 | 0x7fff0C", size=12, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 215, "Зберігає вказівник data() та довжину size() у полях об'єкта.", size=11, color=MUTED))

    # Розділювач
    f.append(line(40, 235, 900, 235, color=MUTED, sw=1, dash="6 5"))

    # Нижня панель: Static Extent
    f.append(text(50, 260, "2. Статичний розмір: std::span<int, 4> (Extent = 4, sizeof = 8 байтів)", size=13, color=POS, anchor="start", bold=True))

    # Об'єкт span зі статичним розміром (стек)
    f.append(fitbox(50, 280, 240, 110, "std::span<int, 4>\nptr: 0x7fff... ──┐\n(без поля size!) │\n(розмір у типі)   │", size=12, fill="#fff7e6", stroke=POS))

    # Стрілка на масив
    f.append(arrow(290, 335, 470, 335, color=POS, sw=2))

    # Суцільний масив пам'яті
    f.append(fitbox(475, 280, 415, 110, "Суцільний масив у пам'яті (статична довжина відома компілятору)\n[10] | [20] | [30] | [40]\n0x7fff00 | 0x7fff04 | 0x7fff08 | 0x7fff0C", size=12, fill="#f4f6f8", stroke=LINE))

    f.append(text(470, 405, "Нульові накладні витрати на довжину: sizeof дорівнює одному вказівнику (8 байтів).", size=11, color=MUTED))

    render(os.path.join(OUT, 'span-layout.svg'), W, H, *f,
           title="Макет пам'яті std::span з динамічним та статичним розміром")


# ── 2. Нуль-копіювальне зрізання (subspan) ──────────────────────────────────
def fig_subspan_view():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Вікно перегляду subspan(): зріз буфера за O(1) без виділення пам'яті", size=16, color=INK, anchor="start", bold=True))

    # Оригінальний буфер
    f.append(fitbox(50, 70, 840, 85, "Оригінальний буфер даних (std::vector<uint8_t> / std::array / C-array)\n[ Byte 0 ] [ Byte 1 ] [ Byte 2 ] [ Byte 3 ] [ Byte 4 ] [ Byte 5 ] [ Byte 6 ] [ Byte 7 ] [ Byte 8 ] [ Byte 9 ]", size=12, fill="#f0f4f8", stroke=LINE))

    # Головний span
    f.append(fitbox(50, 180, 840, 60, "Головний view: std::span<uint8_t> (offset = 0, size = 10)", size=12, fill="#e2f0d9", stroke=FIELD))
    f.append(arrow(100, 180, 100, 155, color=FIELD, sw=2))

    # Зріз subspan(2, 5)
    f.append(fitbox(218, 280, 420, 60, "Зріз subspan(2, 5): std::span<uint8_t> (offset = 2, size = 5)", size=12, fill="#fff2cc", stroke=POS))
    f.append(arrow(428, 280, 428, 240, color=POS, sw=2))

    f.append(text(50, 385, "Створення subspan лише змінює вказівник data() і лічильник size(). Дані в пам'яті не копіюються.", size=12, color=MUTED))

    render(os.path.join(OUT, 'subspan-view.svg'), W, H, *f,
           title="Нуль-копіювальне зрізання масиву через subspan")


# ── 3. Суцільна пам'ять проти фрагментованої ────────────────────────────────
def fig_contiguous_vs_strided():
    W, H = 940, 440
    f = []

    f.append(text(50, 35, "Вимога std::span: Суцільна пам'ять (Contiguous Memory Layout)", size=16, color=INK, anchor="start", bold=True))

    # Верхня частина: Суцільна пам'ять (Підтримується std::span)
    f.append(text(50, 70, "1. Суцільний масив (std::vector, std::array, C-array, std::string)", size=13, color=POS, anchor="start", bold=True))
    
    # Елементи поспіль
    for i in range(5):
        f.append(fitbox(50 + i*160, 95, 145, 75, f"Elem {i}\n&E[{i}] = base + {i}*S", size=12, fill="#e8f6ee", stroke=POS))
        if i < 4:
            f.append(arrow(195 + i*160, 132, 210 + i*160, 132, color=POS, sw=2))

    f.append(text(50, 190, "Адреси елементів розташовані строго послідовно: addr(i) = base + i * sizeof(T). Сумісно з std::span.", size=11, color=MUTED))

    # Розділювач
    f.append(line(40, 210, 900, 210, color=MUTED, sw=1, dash="6 5"))

    # Нижня частина: Фрагментована або зв'язана пам'ять (Не підтримується std::span)
    f.append(text(50, 235, "2. Фрагментована або зв'язана пам'ять (std::deque, std::list, стрічкові матриці)", size=13, color=NEG, anchor="start", bold=True))

    # Вузли ліста або деку
    coords = [(50, 260), (260, 290), (490, 265), (710, 285)]
    for idx, (x, y) in enumerate(coords):
        f.append(fitbox(x, y, 140, 75, f"Node {idx}\nPtr: 0x{1000 + idx*0x840:X}", size=12, fill="#fce4d6", stroke=NEG))

    f.append(arrow(190, 297, 260, 327, color=NEG, sw=2))
    f.append(arrow(400, 327, 490, 302, color=NEG, sw=2))
    f.append(arrow(630, 302, 710, 322, color=NEG, sw=2))

    f.append(text(50, 405, "Елементи розкидані по купі або блоках. Вказівник T* не охоплює весь діапазон — std::span НЕМОЖЛИВИЙ.", size=11, color=MUTED))

    render(os.path.join(OUT, 'contiguous-vs-strided.svg'), W, H, *f,
           title="Суцільне розташування пам'яті проти фрагментованого")


# ── 4. Переінтерпретація байтів через as_bytes та as_writable_bytes ───────────
def fig_byte_reinterpretation():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Безпечна переінтерпретація пам'яті: std::as_bytes та std::as_writable_bytes", size=16, color=INK, anchor="start", bold=True))

    # Вихідний типизований span
    f.append(text(50, 75, "Типизований зріз: std::span<const uint32_t, 2>", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 100, 380, 80, "Value 0: 0x12345678 (4 байти)\n[ 0x78 | 0x56 | 0x34 | 0x12 ]", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(450, 100, 380, 80, "Value 1: 0xABCDEF01 (4 байти)\n[ 0x01 | 0xEF | 0xCD | 0xAB ]", size=12, fill="#eef2f7", stroke=LINE))

    # Стрілка приведення
    f.append(arrow(440, 200, 440, 235, color=FIELD, sw=2))
    f.append(text(460, 218, "std::as_bytes(span)", size=12, color=FIELD, anchor="start", bold=True))

    # Результат переінтерпретації у std::byte
    f.append(text(50, 245, "Байтовий зріз: std::span<const std::byte, 8> (size_bytes() = 8)", size=13, color=POS, anchor="start", bold=True))
    
    # 8 окремих байтів
    for i in range(8):
        f.append(fitbox(50 + i*105, 270, 95, 75, f"B[{i}]\nstd::byte", size=12, fill="#e8f6ee", stroke=POS))

    f.append(text(50, 385, "Дозволяє читати/писати сирі байти структур без порушення strict aliasing rules або reinterpret_cast.", size=11, color=MUTED))

    render(os.path.join(OUT, 'byte-reinterpretation.svg'), W, H, *f,
           title="Переінтерпретація типів у байтовий зріз")


if __name__ == '__main__':
    fig_span_layout()
    fig_subspan_view()
    fig_contiguous_vs_strided()
    fig_byte_reinterpretation()
    print("Всі фігури успішно згенеровано.")
