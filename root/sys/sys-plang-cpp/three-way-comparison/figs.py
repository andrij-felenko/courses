# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to scripts/ from reference/cpp-standards/language/three-way-comparison
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK,
            lh=1.4, dash=None, anchor="middle", bold=False):
    """Рамка з кількома моноширинними рядками."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)
    if dash:
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
               'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
               % (x, y, w, h, fill, stroke, sw, dash))
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * lh / 2 + size * 0.35
    px = x + w / 2 if anchor == "middle" else x + 16
    for i, ln in enumerate(lines):
        out += mono(px, cy + i * size * lh, ln, size=size, color=color, anchor=anchor, bold=bold)
    return out


# ── 1. Категорії порівняння та їхня ієрархія ────────────────────────────────
def fig_comparison_categories():
    W, H = 1000, 480
    p = []

    # Заголовок / фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 42, "Ієрархія категорій порівняння C++20 у <compare>", size=16, bold=True, color=INK))

    # Три блоки категорій
    # 1. strong_ordering (зліва / зверху в ланцюжку)
    bx, by, bw, bh = 50, 75, 270, 350
    p.append(rect(bx, by, bw, bh, fill="#eef7ee", stroke=FIELD, sw=2, rx=8))
    p.append(text(bx + bw / 2, by + 30, "std::strong_ordering", size=14, bold=True, color=FIELD))
    p.append(text(bx + bw / 2, by + 52, "Сильний порядок (повний)", size=12, color=INK))
    p.append(line(bx + 15, by + 65, bx + bw - 15, by + 65, color=FIELD, sw=1.2))

    p.append(text(bx + 20, by + 90, "Значення:", size=12, bold=True, anchor="start", color=INK))
    p.append(mono(bx + 30, by + 112, "• less", size=12, anchor="start", color=INK))
    p.append(mono(bx + 30, by + 132, "• equal / equivalent", size=12, anchor="start", color=INK))
    p.append(mono(bx + 30, by + 152, "• greater", size=12, anchor="start", color=INK))

    p.append(text(bx + 20, by + 185, "Головна властивість:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx + 20, by + 207, "Взаємозамінність:", size=12, bold=True, anchor="start", color=FIELD))
    p.append(text(bx + 20, by + 227, "якщо a == b, то f(a) == f(b)", size=11.5, anchor="start", color=INK))
    p.append(text(bx + 20, by + 245, "для будь-якої спостережної f", size=11, italic=True, anchor="start", color=MUTED))

    p.append(text(bx + 20, by + 278, "Приклади типів:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx + 20, by + 300, "int, std::string, покажчики,", size=11.5, anchor="start", color=INK))
    p.append(text(bx + 20, by + 320, "почленні структури значень", size=11.5, anchor="start", color=INK))

    # 2. weak_ordering (посередині)
    bx2, by2, bw2, bh2 = 365, 75, 270, 350
    p.append(rect(bx2, by2, bw2, bh2, fill="#f0f4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(bx2 + bw2 / 2, by2 + 30, "std::weak_ordering", size=14, bold=True, color=NEG))
    p.append(text(bx2 + bw2 / 2, by2 + 52, "Слабкий порядок", size=12, color=INK))
    p.append(line(bx2 + 15, by2 + 65, bx2 + bw2 - 15, by2 + 65, color=NEG, sw=1.2))

    p.append(text(bx2 + 20, by2 + 90, "Значення:", size=12, bold=True, anchor="start", color=INK))
    p.append(mono(bx2 + 30, by2 + 112, "• less", size=12, anchor="start", color=INK))
    p.append(mono(bx2 + 30, by2 + 132, "• equivalent", size=12, anchor="start", color=INK))
    p.append(mono(bx2 + 30, by2 + 152, "• greater", size=12, anchor="start", color=INK))

    p.append(text(bx2 + 20, by2 + 185, "Головна властивість:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx2 + 20, by2 + 207, "Еквівалентність без рівності:", size=12, bold=True, anchor="start", color=NEG))
    p.append(text(bx2 + 20, by2 + 227, "a еквівалентне b, але", size=11.5, anchor="start", color=INK))
    p.append(text(bx2 + 20, by2 + 245, "стан f(a) і f(b) може різнитися", size=11, italic=True, anchor="start", color=MUTED))

    p.append(text(bx2 + 20, by2 + 278, "Приклади типів:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx2 + 20, by2 + 300, "Регістронезалежні рядки,", size=11.5, anchor="start", color=INK))
    p.append(text(bx2 + 20, by2 + 320, "об'єкти з кешем/неключовими полями", size=11, anchor="start", color=INK))

    # 3. partial_ordering (справа)
    bx3, by3, bw3, bh3 = 680, 75, 270, 350
    p.append(rect(bx3, by3, bw3, bh3, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(bx3 + bw3 / 2, by3 + 30, "std::partial_ordering", size=14, bold=True, color=POS))
    p.append(text(bx3 + bw3 / 2, by3 + 52, "Частковий порядок", size=12, color=INK))
    p.append(line(bx3 + 15, by3 + 65, bx3 + bw3 - 15, by3 + 65, color=POS, sw=1.2))

    p.append(text(bx3 + 20, by3 + 90, "Значення:", size=12, bold=True, anchor="start", color=INK))
    p.append(mono(bx3 + 30, by3 + 112, "• less", size=12, anchor="start", color=INK))
    p.append(mono(bx3 + 30, by3 + 132, "• equivalent", size=12, anchor="start", color=INK))
    p.append(mono(bx3 + 30, by3 + 152, "• greater", size=12, anchor="start", color=INK))
    p.append(mono(bx3 + 30, by3 + 172, "• unordered", size=12, bold=True, anchor="start", color=POS))

    p.append(text(bx3 + 20, by3 + 198, "Головна властивість:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 20, by3 + 218, "Незрівнюваність (unordered):", size=12, bold=True, anchor="start", color=POS))
    p.append(text(bx3 + 20, by3 + 238, "деякі значення не можна", size=11.5, anchor="start", color=INK))
    p.append(text(bx3 + 20, by3 + 254, "розташувати на одній осі", size=11, italic=True, anchor="start", color=MUTED))

    p.append(text(bx3 + 20, by3 + 278, "Приклади типів:", size=12, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 20, by3 + 300, "float, double (через NaN),", size=11.5, anchor="start", color=INK))
    p.append(text(bx3 + 20, by3 + 320, "вектори в просторі, множини", size=11.5, anchor="start", color=INK))

    # Стрілки неявного приведення типів
    # strong -> weak
    p.append(arrow(320, 200, 365, 200, color=LINE, sw=2))
    p.append(rect(323, 175, 40, 20, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(text(343, 189, "неявно", size=9.5, bold=True, color=LINE))

    # weak -> partial
    p.append(arrow(635, 200, 680, 200, color=LINE, sw=2))
    p.append(rect(638, 175, 40, 20, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(text(658, 189, "неявно", size=9.5, bold=True, color=LINE))

    # Дуга strong -> partial (знизу)
    p.append(
        '<path d="M 185 425 Q 500 475 815 425" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
        % LINE
    )
    p.append(rect(435, 442, 130, 22, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(500, 457, "неявне приведення", size=10, bold=True, color=LINE))

    render(os.path.join(OUT, "comparison-categories.svg"), W, H, *p)


# ── 2. Синтез переписаних кандидатів при розв'язанні перевантажень ───────────
def fig_rewritten_candidates():
    W, H = 1040, 490
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 38, "Генерація переписаних і перевернутих кандидатів у C++20", size=16, bold=True, color=INK))

    # Ліва колонка: Вираз виклику
    p.append(text(170, 75, "Вираз у коді", size=13.5, bold=True, color=INK))
    p.append(monobox(35, 95, 270, 52, ["x == y"], size=15, fill="#fff", stroke=FIELD, sw=2, bold=True, color=FIELD))
    p.append(monobox(35, 190, 270, 52, ["x != y"], size=15, fill="#fff", stroke=NEG, sw=2, bold=True, color=NEG))
    p.append(monobox(35, 285, 270, 52, ["x < y"], size=15, fill="#fff", stroke=POS, sw=2, bold=True, color=POS))
    p.append(monobox(35, 380, 270, 52, ["x >= y"], size=15, fill="#fff", stroke="#8e44ad", sw=2, bold=True, color="#8e44ad"))

    # Стрілки
    p.append(arrow(305, 121, 370, 121, color=FIELD, sw=2))
    p.append(arrow(305, 216, 370, 216, color=NEG, sw=2))
    p.append(arrow(305, 311, 370, 311, color=POS, sw=2))
    p.append(arrow(305, 406, 370, 406, color="#8e44ad", sw=2))

    # Права колонка: Набір кандидатів для Overload Resolution
    p.append(text(685, 75, "Кандидати для розв'язання перевантажень (у порядку пріоритету)", size=13.5, bold=True, color=INK))

    # Блок для ==
    p.append(rect(370, 90, 630, 64, fill="#f4faf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(mono(385, 112, "1. Прямий виклик:  x.operator==(y)  або  operator==(x, y)", size=11.5, anchor="start", bold=True, color=INK))
    p.append(mono(385, 134, "2. Перевернутий:   y.operator==(x)  або  operator==(y, x)", size=11.5, anchor="start", color=MUTED))

    # Блок для !=
    p.append(rect(370, 185, 630, 64, fill="#f0f4ff", stroke=NEG, sw=1.5, rx=6))
    p.append(mono(385, 207, "1. Прямий виклик:  x.operator!=(y)  або  operator!=(x, y)", size=11.5, anchor="start", bold=True, color=INK))
    p.append(mono(385, 229, "2. Переписаний:    !(x == y)   [шукає direct або reversed ==]", size=11.5, anchor="start", color=NEG))

    # Блок для <
    p.append(rect(370, 280, 630, 64, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(mono(385, 302, "1. Прямий виклик:  x.operator<(y)   або  operator<(x, y)", size=11.5, anchor="start", bold=True, color=INK))
    p.append(mono(385, 324, "2. Переписаний:    (x <=> y) < 0   або   0 < (y <=> x)", size=11.5, anchor="start", color=POS))

    # Блок для >=
    p.append(rect(370, 375, 630, 64, fill="#fbf5fd", stroke="#8e44ad", sw=1.5, rx=6))
    p.append(mono(385, 397, "1. Прямий виклик:  x.operator>=(y)  або  operator>=(x, y)", size=11.5, anchor="start", bold=True, color=INK))
    p.append(mono(385, 419, "2. Переписаний:    (x <=> y) >= 0  або   0 >= (y <=> x)", size=11.5, anchor="start", color="#8e44ad"))

    # Пояснення внизу
    p.append(text(W / 2, 465, "Правило відбору: точний прямий кандидат перемагає переписаного; неперевернутий перемагає перевернутого", size=11.5, italic=True, color=MUTED))

    render(os.path.join(OUT, "rewritten-candidates.svg"), W, H, *p)


# ── 3. Розділення operator== та operator<=> для продуктивності ──────────────
def fig_equality_vs_ordering():
    W, H = 1040, 480
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 38, "Чому перевірка рівності (==) відділена від тричленного порядку (<=>)", size=16, bold=True, color=INK))

    # Ліва колонка: operator== (Швидка рівність)
    p.append(rect(40, 68, 460, 380, fill="#eef7ee", stroke=FIELD, sw=2, rx=8))
    p.append(text(270, 100, "operator== (Тест на збіг)", size=15, bold=True, color=FIELD))
    p.append(text(270, 122, "Питання: чи ідентичні два об'єкти? (true / false)", size=11.5, color=INK))
    p.append(line(60, 136, 480, 136, color=FIELD, sw=1.2))

    # Кроки алгоритму для ==
    p.append(rect(60, 150, 420, 56, fill="#fff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(80, 172, "Крок 1: Швидка перевірка розміру / ємності", size=12, bold=True, anchor="start", color=FIELD))
    p.append(mono(80, 192, "if (size() != other.size()) return false;  // O(1)", size=11, anchor="start", color=INK))

    p.append(arrow(270, 206, 270, 226, color=FIELD, sw=1.8))

    p.append(rect(60, 226, 420, 56, fill="#fff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(80, 248, "Крок 2: Порівняння буфера (memcmp / SIMD)", size=12, bold=True, anchor="start", color=FIELD))
    p.append(mono(80, 268, "return memcmp(data(), other.data(), size()) == 0;", size=11, anchor="start", color=INK))

    p.append(rect(60, 305, 420, 125, fill="#e3f2e3", stroke=FIELD, sw=1, rx=6))
    p.append(text(80, 328, "Переваги для std::string / контейнерів:", size=11.5, bold=True, anchor="start", color=FIELD))
    p.append(text(80, 350, "• Якщо рядки різної довжини — миттєвий вихід O(1)", size=11, anchor="start", color=INK))
    p.append(text(80, 370, "• Не потрібно читати байти з пам'яті в купі (heap)", size=11, anchor="start", color=INK))
    p.append(text(80, 390, "• Немає навантаження на L1/L2 кеш процесора", size=11, anchor="start", color=INK))
    p.append(text(80, 410, "• Векторизація SIMD для блоків по 16/32 байти", size=11, anchor="start", color=INK))

    # Права колонка: operator<=> (Лексикографічний порядок)
    p.append(rect(540, 68, 460, 380, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(770, 100, "operator<=> (Лексикографічний порядок)", size=15, bold=True, color=POS))
    p.append(text(770, 122, "Питання: хто стоїть раніше в алфавіті? (less/equal/greater)", size=11.5, color=INK))
    p.append(line(560, 136, 980, 136, color=POS, sw=1.2))

    # Кроки алгоритму для <=>
    p.append(rect(560, 150, 420, 56, fill="#fff", stroke=POS, sw=1.2, rx=6))
    p.append(text(580, 172, "Крок 1: Побайтне порівняння префікса", size=12, bold=True, anchor="start", color=POS))
    p.append(mono(580, 192, "auto cmp = memcmp(data, o.data, min_len); // O(N)", size=11, anchor="start", color=INK))

    p.append(arrow(770, 206, 770, 226, color=POS, sw=1.8))

    p.append(rect(560, 226, 420, 56, fill="#fff", stroke=POS, sw=1.2, rx=6))
    p.append(text(580, 248, "Крок 2: Перевірка різниці префіксів", size=12, bold=True, anchor="start", color=POS))
    p.append(mono(580, 268, "if (cmp != 0) return cmp <=> 0;", size=11, anchor="start", color=INK))

    p.append(arrow(770, 282, 770, 302, color=POS, sw=1.8))

    p.append(rect(560, 302, 420, 56, fill="#fff", stroke=POS, sw=1.2, rx=6))
    p.append(text(580, 324, "Крок 3: Тайбрейкер за довжиною", size=12, bold=True, anchor="start", color=POS))
    p.append(mono(580, 344, "return size() <=> other.size();", size=11, anchor="start", color=INK))

    p.append(rect(560, 375, 420, 55, fill="#fbe6e6", stroke=POS, sw=1, rx=6))
    p.append(text(580, 395, "Чому не можна одразу дивитися на size():", size=11.5, bold=True, anchor="start", color=POS))
    p.append(text(580, 415, '"b" довжини 1 стоїть ПІЗНІШЕ за "aaaaa" довжини 5!', size=11, anchor="start", color=INK))

    render(os.path.join(OUT, "equality-vs-ordering.svg"), W, H, *p)


def main():
    fig_comparison_categories()
    fig_rewritten_candidates()
    fig_equality_vs_ordering()
    print("ok")


if __name__ == "__main__":
    main()
