# -*- coding: utf-8 -*-
import sys, os
# Path to scripts/ directory from topic directory (4 levels up)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def code_text(x, y, s, size=12, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── 1. Таксономія поліморфізму Карделлі-Вегнера ──────────────────────────────
def fig_taxonomy():
    W, H = 820, 390
    p = []

    # Головний корінь
    p.append(rect(290, 16, 240, 46, fill="#0f1115", stroke=LINE, sw=2, rx=8))
    p.append(text(410, 36, "Поліморфізм", size=15, color="#ffffff", bold=True))
    p.append(text(410, 52, "один інтерфейс — багато форм", size=10.5, color="#9ca3af", italic=True))

    # Дві головні гілки: Універсальний та Спеціальний (Ad-hoc)
    p.append(arrow(360, 62, 210, 100, color=LINE, sw=1.8))
    p.append(arrow(460, 62, 610, 100, color=LINE, sw=1.8))

    # Блок: Універсальний
    p.append(rect(40, 104, 340, 54, fill="#eaf4fd", stroke=NEG, sw=2, rx=8))
    p.append(text(210, 126, "Універсальний (Universal)", size=13.5, color=NEG, bold=True))
    p.append(text(210, 146, "однакова семантика для необмеженої множини типів", size=10, color=INK))

    # Блок: Ad-hoc
    p.append(rect(440, 104, 340, 54, fill="#fdf2e9", stroke=POS, sw=2, rx=8))
    p.append(text(610, 126, "Спеціальний (Ad-hoc)", size=13.5, color=POS, bold=True))
    p.append(text(610, 146, "різна поведінка для скінченного набору окремих типів", size=10, color=INK))

    # Стрілки до 4 видів
    p.append(arrow(130, 158, 115, 196, color=NEG, sw=1.5))
    p.append(arrow(290, 158, 305, 196, color=NEG, sw=1.5))
    p.append(arrow(530, 158, 515, 196, color=POS, sw=1.5))
    p.append(arrow(690, 158, 705, 196, color=POS, sw=1.5))

    # 1. Параметричний
    p.append(rect(25, 200, 180, 160, fill=FILL, stroke=NEG, sw=1.6, rx=8))
    p.append(text(115, 222, "Параметричний", size=12.5, color=NEG, bold=True))
    p.append(text(115, 238, "Parametric", size=10, color=MUTED, italic=True))
    p.append(line(35, 246, 195, 246, color="#cbd5e1", sw=1))
    p.append(text(115, 264, "Один код для всіх типів", size=10, color=INK))
    p.append(text(115, 280, "Тип передається як аргумент", size=9.5, color=MUTED))
    p.append(code_text(115, 304, "template<typename T>", size=10, color=INK, anchor="middle"))
    p.append(code_text(115, 320, "fn sort<T>(list: &[T])", size=10, color=INK, anchor="middle"))
    p.append(text(115, 346, "Generics, Шаблони C++", size=9.5, color=NEG, bold=True))

    # 2. Підтиповий
    p.append(rect(215, 200, 180, 160, fill=FILL, stroke=NEG, sw=1.6, rx=8))
    p.append(text(305, 222, "Підтиповий", size=12.5, color=NEG, bold=True))
    p.append(text(305, 238, "Inclusion / Subtyping", size=10, color=MUTED, italic=True))
    p.append(line(225, 246, 385, 246, color="#cbd5e1", sw=1))
    p.append(text(305, 264, "Підстановка нащадка S <: T", size=10, color=INK))
    p.append(text(305, 280, "Спільний інтерфейс об'єктів", size=9.5, color=MUTED))
    p.append(code_text(305, 304, "shape.draw()", size=10.5, color=INK, anchor="middle"))
    p.append(code_text(305, 320, "Derived is-a Base", size=10.5, color=INK, anchor="middle"))
    p.append(text(305, 346, "vtable, динамічні методи", size=9.5, color=NEG, bold=True))

    # 3. Перевантаження
    p.append(rect(425, 200, 180, 160, fill=FILL, stroke=POS, sw=1.6, rx=8))
    p.append(text(515, 222, "Перевантаження", size=12.5, color=POS, bold=True))
    p.append(text(515, 238, "Overloading", size=10, color=MUTED, italic=True))
    p.append(line(435, 246, 595, 246, color="#cbd5e1", sw=1))
    p.append(text(515, 264, "Однакова назва функції", size=10, color=INK))
    p.append(text(515, 280, "Різні тіла під типи", size=9.5, color=MUTED))
    p.append(code_text(515, 304, "print(int x)", size=10, color=INK, anchor="middle"))
    p.append(code_text(515, 320, "print(string s)", size=10, color=INK, anchor="middle"))
    p.append(text(515, 346, "Статичний вибір виклику", size=9.5, color=POS, bold=True))

    # 4. Коерсивний
    p.append(rect(615, 200, 180, 160, fill=FILL, stroke=POS, sw=1.6, rx=8))
    p.append(text(705, 222, "Коерсивний", size=12.5, color=POS, bold=True))
    p.append(text(705, 238, "Coercion", size=10, color=MUTED, italic=True))
    p.append(line(625, 246, 785, 246, color="#cbd5e1", sw=1))
    p.append(text(705, 264, "Неявне приведення типів", size=10, color=INK))
    p.append(text(705, 280, "Автоматична конверсія", size=9.5, color=MUTED))
    p.append(code_text(705, 304, "double + int -> double", size=9.5, color=INK, anchor="middle"))
    p.append(code_text(705, 320, "&String -> &str", size=10, color=INK, anchor="middle"))
    p.append(text(705, 346, "Widening, deref coercion", size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "polymorphism-taxonomy.svg"), W, H, *p,
           title="Таксономія поліморфізму (Карделлі і Вегнер, 1985)")


# ── 2. Макет vtable у пам'яті та thunk зміщення ─────────────────────────────
def fig_vtable():
    W, H = 820, 390
    p = []

    # Ліва половина: Просте спадкування (одинарний vptr)
    p.append(rect(20, 48, 370, 326, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    p.append(text(205, 72, "Одинарне спадкування (Single Inheritance)", size=12.5, color=INK, bold=True))

    # Об'єкт у пам'яті
    p.append(rect(40, 96, 130, 140, fill="#ffffff", stroke=LINE, sw=1.6, rx=6))
    p.append(text(105, 116, "Об'єкт у пам'яті", size=10.5, color=MUTED, bold=True))
    p.append(rect(46, 126, 118, 32, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(code_text(105, 146, "vptr (8 B)", size=11, color="#92400e", anchor="middle", bold=True))
    p.append(rect(46, 164, 118, 28, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(code_text(105, 182, "x: int32 (4 B)", size=10, color=INK, anchor="middle"))
    p.append(rect(46, 196, 118, 28, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(code_text(105, 214, "y: int32 (4 B)", size=10, color=INK, anchor="middle"))

    # Таблиця vtable у .rodata
    p.append(rect(230, 96, 145, 150, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(302, 116, "VTable (.rodata)", size=10.5, color=FIELD, bold=True))
    p.append(rect(236, 126, 133, 26, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    p.append(code_text(302, 143, "offset_to_top: 0", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(236, 156, 133, 26, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    p.append(code_text(302, 173, "RTTI typeinfo ptr", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(236, 186, 133, 26, fill="#ecfdf5", stroke=FIELD, sw=1.4, rx=3))
    p.append(code_text(302, 203, "[0] &Circle::draw", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(rect(236, 216, 133, 26, fill="#ecfdf5", stroke=FIELD, sw=1.4, rx=3))
    p.append(code_text(302, 233, "[1] &Circle::area", size=10, color=FIELD, anchor="middle", bold=True))

    # Зв'язок vptr -> vtable
    p.append(arrow(164, 142, 234, 196, color="#d97706", sw=2))

    # Виклик в асемблері
    p.append(rect(40, 256, 335, 102, fill="#0f1115", stroke=LINE, sw=1.5, rx=6))
    p.append(text(207, 274, "Кроки виклику shape->draw():", size=10, color="#ffd479", bold=True))
    p.append(code_text(52, 296, "mov (%rdi), %rax       ; %rax = vptr", size=10.5, color="#38bdf8"))
    p.append(code_text(52, 316, "mov 0(%rax), %rdx      ; %rdx = VTable[0] (&draw)", size=10.5, color="#38bdf8"))
    p.append(code_text(52, 336, "call *%rdx             ; непрямий стрибок", size=10.5, color="#4ade80", bold=True))

    # Права половина: Множинне спадкування та Thunk
    p.append(rect(410, 48, 390, 326, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    p.append(text(605, 72, "Множинне спадкування та Adjustor Thunk", size=12.5, color=INK, bold=True))

    # Об'єктDerived у пам'яті
    p.append(rect(425, 96, 140, 160, fill="#ffffff", stroke=LINE, sw=1.6, rx=6))
    p.append(text(495, 114, "Об'єкт Derived", size=10.5, color=MUTED, bold=True))
    p.append(rect(431, 122, 128, 28, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(code_text(495, 140, "vptr_BaseA", size=10.5, color="#92400e", anchor="middle", bold=True))
    p.append(rect(431, 154, 128, 24, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(code_text(495, 170, "data_BaseA (8 B)", size=9.5, color=INK, anchor="middle"))
    p.append(rect(431, 182, 128, 28, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=4))
    p.append(code_text(495, 200, "vptr_BaseB (+16)", size=10.5, color=NEG, anchor="middle", bold=True))
    p.append(rect(431, 214, 128, 24, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(code_text(495, 230, "data_BaseB (8 B)", size=9.5, color=INK, anchor="middle"))

    # Таблиця VTable_BaseB
    p.append(rect(605, 96, 180, 80, fill="#ffffff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(695, 114, "VTable_for_BaseB", size=10.5, color=NEG, bold=True))
    p.append(rect(611, 124, 168, 24, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    p.append(code_text(695, 140, "offset_to_top: -16", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(611, 150, 168, 22, fill="#e0e7ff", stroke=NEG, sw=1.4, rx=3))
    p.append(code_text(695, 165, "[0] &non_virtual_thunk", size=9.5, color=NEG, anchor="middle", bold=True))

    p.append(arrow(559, 196, 609, 158, color=NEG, sw=1.8))

    # Блок Thunk
    p.append(rect(590, 186, 195, 70, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    p.append(text(687, 204, "Adjustor Thunk (Перехідник)", size=10, color=POS, bold=True))
    p.append(code_text(600, 224, "sub $16, %rdi   ; зсув this", size=9.5, color=POS, bold=True))
    p.append(code_text(600, 242, "jmp Derived::methodB", size=9.5, color=POS, bold=True))

    p.append(arrow(695, 172, 695, 184, color=POS, sw=1.5))

    # Пояснення внизу
    p.append(rect(425, 266, 360, 92, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(605, 286, "Коли покажчик приведено до BaseB*:", size=10, color=INK, bold=True))
    p.append(text(605, 306, "1. Адреса this зміщується на +16 байтів.", size=9.5, color=MUTED))
    p.append(text(605, 324, "2. Виклик іде у VTable_for_BaseB -> Thunk.", size=9.5, color=MUTED))
    p.append(text(605, 344, "3. Thunk повертає this назад на -16 і стрибає в Derived.", size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "vtable-layout.svg"), W, H, *p,
           title="Макет vtable: одинарне спадкування проти множинного з thunk")


# ── 3. Порівняння механізмів інтерфейсної диспетчеризації ────────────────────
def fig_itable_fat_pointer():
    W, H = 820, 360
    p = []

    # 1 колонка: C++/Java клас (прямий vptr)
    p.append(rect(20, 50, 245, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(142, 74, "1. Вбудований vptr", size=12.5, color=INK, bold=True))
    p.append(text(142, 92, "C++, Java invokevirtual", size=10, color=MUTED, italic=True))

    p.append(rect(35, 108, 215, 66, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(142, 126, "Об'єкт у купі (Heap Object)", size=10, color=MUTED, bold=True))
    p.append(rect(45, 134, 195, 30, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    p.append(code_text(142, 154, "vptr -> Class VTable", size=10.5, color="#92400e", anchor="middle", bold=True))

    p.append(arrow(142, 174, 142, 204, color="#d97706", sw=1.8))

    p.append(rect(35, 206, 215, 60, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(142, 226, "Фіксований індекс у таблиці", size=10.5, color=FIELD, bold=True))
    p.append(code_text(142, 248, "call *(vptr + SLOT_OFFSET)", size=10, color=INK, anchor="middle"))

    p.append(text(142, 294, "Швидко: 1 непрямий перехід", size=10, color=FIELD, bold=True))
    p.append(text(142, 314, "Жорсткий макет класів", size=9.5, color=MUTED))

    # 2 колонка: Таблиця інтерфейсів (JVM itable / Go interface)
    p.append(rect(285, 50, 250, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(410, 74, "2. Інтерфейсна таблиця (itable)", size=12.5, color=INK, bold=True))
    p.append(text(410, 92, "JVM invokeinterface, Go iface", size=10, color=MUTED, italic=True))

    p.append(rect(298, 108, 224, 66, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(410, 126, "Go iface: [ *itab | *data ]", size=10, color=MUTED, bold=True))
    p.append(rect(306, 134, 100, 30, fill="#e0e7ff", stroke=NEG, sw=1.4, rx=4))
    p.append(code_text(356, 154, "*itab", size=10.5, color=NEG, anchor="middle", bold=True))
    p.append(rect(414, 134, 100, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.4, rx=4))
    p.append(code_text(464, 154, "*data", size=10.5, color=INK, anchor="middle"))

    p.append(arrow(356, 174, 356, 204, color=NEG, sw=1.8))

    p.append(rect(298, 206, 224, 60, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(410, 224, "Таблиця (Interface, Type)", size=10.5, color=NEG, bold=True))
    p.append(text(410, 242, "Пошук методу / кешоване зміщення", size=9.5, color=INK))
    p.append(code_text(410, 258, "itab.fun[method_idx]", size=10, color=NEG, anchor="middle", bold=True))

    p.append(text(410, 294, "Гнучко: без єдиного предка", size=10, color=NEG, bold=True))
    p.append(text(410, 314, "Накладні на генерацію/пошук itab", size=9.5, color=MUTED))

    # 3 колонка: Жирні покажчики (Rust Trait Objects)
    p.append(rect(555, 50, 245, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(677, 74, "3. Жирний покажчик (Fat Pointer)", size=12.5, color=POS, bold=True))
    p.append(text(677, 92, "Rust &dyn Trait, Box<dyn Trait>", size=10, color=MUTED, italic=True))

    p.append(rect(568, 108, 219, 66, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(677, 126, "&dyn Trait (16 байтів на стеку)", size=10, color=MUTED, bold=True))
    p.append(rect(576, 134, 98, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.4, rx=4))
    p.append(code_text(625, 154, "data_ptr (8B)", size=9.5, color=INK, anchor="middle"))
    p.append(rect(680, 134, 98, 30, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(code_text(729, 154, "vtable_ptr (8B)", size=9.5, color=POS, anchor="middle", bold=True))

    p.append(arrow(729, 174, 729, 204, color=POS, sw=1.8))

    p.append(rect(568, 206, 219, 60, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(677, 226, "Трейт-таблиця конкретного типу", size=10, color=POS, bold=True))
    p.append(code_text(677, 248, "call *vtable_ptr->method(data_ptr)", size=9, color=INK, anchor="middle"))

    p.append(text(677, 294, "Об'єкт чистий: нуль байтів vptr!", size=10, color=POS, bold=True))
    p.append(text(677, 314, "Покажчик займає 16 байтів", size=9.5, color=MUTED))

    render(os.path.join(OUT, "itable-fat-pointer.svg"), W, H, *p,
           title="Моделі інтерфейсної диспетчеризації: vptr проти itable та fat pointers")


# ── 4. Inline Caching (стани IC) ─────────────────────────────────────────────
def fig_inline_caching():
    W, H = 820, 310
    p = []

    # 1. Мономорфний стан
    p.append(rect(30, 56, 210, 210, fill="#ecfdf5", stroke=FIELD, sw=2, rx=8))
    p.append(text(135, 82, "1. Мономорфний (Mono)", size=12.5, color=FIELD, bold=True))
    p.append(text(135, 100, "90%+ викликів у програмах", size=10, color=MUTED, italic=True))
    p.append(line(45, 108, 225, 108, color="#a7f3d0", sw=1))

    p.append(rect(42, 120, 186, 74, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(code_text(50, 140, "if (obj.class == Point) {", size=10, color=INK))
    p.append(code_text(65, 160, "call Point::draw", size=10.5, color=FIELD, bold=True))
    p.append(code_text(50, 180, "} else fallback()", size=10, color=MUTED))

    p.append(text(135, 218, "Швидкість: як прямий виклик", size=10, color=FIELD, bold=True))
    p.append(text(135, 238, "1 порівняння + 1 стрибок", size=9.5, color=MUTED))
    p.append(text(135, 254, "Можливий повний інлайнінг", size=9.5, color=FIELD))

    # Стрілка Mono -> Poly
    p.append(arrow(242, 160, 288, 160, color=LINE, sw=1.8))
    p.append(text(265, 146, "інший тип", size=9, color=MUTED, italic=True))

    # 2. Поліморфний стан
    p.append(rect(290, 56, 240, 210, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(410, 82, "2. Поліморфний (Poly / PIC)", size=12.5, color=NEG, bold=True))
    p.append(text(410, 100, "2–4 різні класи у місці виклику", size=10, color=MUTED, italic=True))
    p.append(line(305, 108, 515, 108, color="#bfdbfe", sw=1))

    p.append(rect(302, 118, 216, 86, fill="#ffffff", stroke=NEG, sw=1.2, rx=5))
    p.append(code_text(310, 136, "switch (obj.class) {", size=9.5, color=INK))
    p.append(code_text(320, 152, "case Circle: call DrawCircle", size=9.5, color=NEG, bold=True))
    p.append(code_text(320, 168, "case Rect:   call DrawRect", size=9.5, color=NEG, bold=True))
    p.append(code_text(320, 184, "case Line:   call DrawLine", size=9.5, color=NEG, bold=True))
    p.append(code_text(310, 198, "}", size=9.5, color=INK))

    p.append(text(410, 226, "Коротка лінійна перевірка", size=10, color=NEG, bold=True))
    p.append(text(410, 244, "Inline stub chain або таблиця", size=9.5, color=MUTED))

    # Стрілка Poly -> Mega
    p.append(arrow(532, 160, 578, 160, color=LINE, sw=1.8))
    p.append(text(555, 146, ">4 типів", size=9, color=MUTED, italic=True))

    # 3. Мегаморфний стан
    p.append(rect(580, 56, 210, 210, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    p.append(text(685, 82, "3. Мегаморфний (Mega)", size=12.5, color=POS, bold=True))
    p.append(text(685, 100, "5+ типів або непередбачувано", size=10, color=MUTED, italic=True))
    p.append(line(595, 108, 775, 108, color="#fecaca", sw=1))

    p.append(rect(592, 120, 186, 74, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    p.append(text(685, 142, "Глобальна хеш-таблиця", size=10, color=POS, bold=True))
    p.append(code_text(600, 162, "hash = (class ^ sel)", size=9.5, color=INK))
    p.append(code_text(600, 180, "call global_cache[hash]", size=9.5, color=POS, bold=True))

    p.append(text(685, 218, "Повільний шлях (Slow Path)", size=10, color=POS, bold=True))
    p.append(text(685, 238, "Кеш-промахи в BTB процесора", size=9.5, color=MUTED))
    p.append(text(685, 254, "Інлайнінг неможливий", size=9.5, color=POS))

    # Нижній загальний напис
    p.append(text(410, 288, "JIT-компілятор переписує машинний код на ходу (patching), адаптуючись до типів у точці виклику",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "inline-caching.svg"), W, H, *p,
           title="Стани вбудованого кешування (Inline Caching) у динамічних середовищах")


if __name__ == "__main__":
    fig_taxonomy()
    fig_vtable()
    fig_itable_fat_pointer()
    fig_inline_caching()
    print("All figures generated successfully.")
