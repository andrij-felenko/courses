# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── subobject-single: Одиничне спадкування та спільний початок ───────────────
def fig_subobject_single():
    W, H = 720, 280
    p = []

    p.append(text(360, 26, "Розкладка пам'яті при одиничному спадкуванні", size=15, bold=True, color=INK))

    x0 = 140
    y0 = 70
    h_box = 50
    w_base = 200
    w_derived = 220

    # Base block
    p.append(rect(x0, y0, w_base, h_box, fill="#e8f4fc", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x0 + w_base / 2, y0 + 22, "Під-об'єкт Base", size=13, bold=True, color=NEG))
    p.append(text(x0 + w_base / 2, y0 + 40, "int id (4B) · int flags (4B)", size=11, color=MUTED))

    # Derived extra fields
    p.append(rect(x0 + w_base, y0, w_derived, h_box, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(x0 + w_base + w_derived / 2, y0 + 22, "Поля Derived", size=13, bold=True, color=POS))
    p.append(text(x0 + w_base + w_derived / 2, y0 + 40, "double score (8B) · int extra (4B)", size=11, color=MUTED))

    # Full object outline
    p.append(rect(x0 - 4, y0 - 4, w_base + w_derived + 8, h_box + 8, fill="none", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(x0 + (w_base + w_derived) / 2, y0 + h_box + 22, "Повний об'єкт Derived (зсув 0..32B)", size=11, bold=True, color=INK))

    # Pointers
    # Derived* pointer
    p.append(arrow(x0 - 70, y0 + 25, x0 - 5, y0 + 25, color=POS, sw=1.8))
    p.append(text(x0 - 80, y0 + 29, "Derived*", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(x0 - 80, y0 + 45, "(адреса 0x1000)", size=10, color=MUTED, anchor="end"))

    # Base* pointer (same address)
    p.append(arrow(x0, y0 - 40, x0, y0 - 6, color=NEG, sw=1.8))
    p.append(text(x0, y0 - 46, "Base* (зсув 0 B, адреса 0x1000)", size=12, bold=True, color=NEG, anchor="start"))

    # Formula / rule at bottom
    b, _, _ = textbox(360, 220, "static_cast<Base*>(ptr_derived) == (void*)ptr_derived  [Δ = 0 байтів]\nВказівник на під-об'єкт Base збігається з адресою Derived", size=12, pad=8, fill="#f8fafc", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "subobject-single.svg"), W, H, *p)


# ── subobject-multiple: Множинне спадкування та зміщення вказівників ─────────
def fig_subobject_multiple():
    W, H = 760, 340
    p = []

    p.append(text(380, 26, "Множинне спадкування: нерівні зсуви базових під-об'єктів", size=15, bold=True, color=INK))

    x0 = 120
    y0 = 80
    h_box = 54
    w_a = 160
    w_b = 160
    w_d = 180

    # BaseA
    p.append(rect(x0, y0, w_a, h_box, fill="#e8f4fc", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x0 + w_a / 2, y0 + 22, "Під-об'єкт BaseA", size=12, bold=True, color=NEG))
    p.append(text(x0 + w_a / 2, y0 + 42, "vptr_A · int a (16B)", size=11, color=MUTED))

    # BaseB
    p.append(rect(x0 + w_a, y0, w_b, h_box, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(x0 + w_a + w_b / 2, y0 + 22, "Під-об'єкт BaseB", size=12, bold=True, color=FIELD))
    p.append(text(x0 + w_a + w_b / 2, y0 + 42, "vptr_B · int b (16B)", size=11, color=MUTED))

    # Derived
    p.append(rect(x0 + w_a + w_b, y0, w_d, h_box, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(x0 + w_a + w_b + w_d / 2, y0 + 22, "Поля Derived", size=12, bold=True, color=POS))
    p.append(text(x0 + w_a + w_b + w_d / 2, y0 + 42, "int d_val (8B)", size=11, color=MUTED))

    # Total object bracket
    p.append(rect(x0 - 4, y0 - 4, w_a + w_b + w_d + 8, h_box + 8, fill="none", stroke=MUTED, sw=1.2, rx=6))

    # Offsets indicators
    p.append(text(x0, y0 + h_box + 20, "0 B", size=11, color=MUTED))
    p.append(text(x0 + w_a, y0 + h_box + 20, "+16 B", size=11, color=FIELD, bold=True))
    p.append(text(x0 + w_a + w_b, y0 + h_box + 20, "+32 B", size=11, color=POS, bold=True))
    p.append(text(x0 + w_a + w_b + w_d, y0 + h_box + 20, "+40 B", size=11, color=MUTED))

    # Pointers
    # Derived* and BaseA*
    p.append(arrow(x0 - 60, y0 + 27, x0 - 5, y0 + 27, color=POS, sw=1.8))
    p.append(text(x0 - 70, y0 + 24, "Derived* (0x2000)", size=11, bold=True, color=POS, anchor="end"))
    p.append(text(x0 - 70, y0 + 40, "BaseA* (зсув 0 B)", size=11, color=NEG, anchor="end"))

    # BaseB* (with adjustment)
    p.append(arrow(x0 + w_a, y0 - 36, x0 + w_a, y0 - 6, color=FIELD, sw=1.8))
    p.append(text(x0 + w_a, y0 - 44, "BaseB* = ptr_derived + 16 B (адреса 0x2010)", size=11, bold=True, color=FIELD))

    # Explanatory card
    b, _, _ = textbox(380, 260, "Pointer Adjustment: перетворення Derived* → BaseB* додає зсув (+16 байтів).\nПеретворення BaseB* → Derived* (downcast) віднімає 16 байтів.\nНульовий покажчик (nullptr) лишається нулем: ptr ? (ptr + 16) : nullptr", size=11, pad=8, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "subobject-multiple.svg"), W, H, *p)


# ── diamond-problem: Ромб успадкування та подвоєння стану ────────────────────
def fig_diamond_problem():
    W, H = 720, 360
    p = []

    p.append(text(360, 24, "Ромбоподібне невіртуальне спадкування (Diamond Problem)", size=15, bold=True, color=INK))

    # Graph nodes
    # Top Base
    b_top, _, _ = textbox(360, 70, "Base\nint counter;", size=12, pad=6, fill="#f4f6f8", stroke=LINE)
    p.append(b_top)

    # Left & Right
    b_left, _, _ = textbox(210, 150, "Left : public Base\nvoid stepLeft();", size=11, pad=6, fill="#e8f4fc", stroke=NEG)
    b_right, _, _ = textbox(510, 150, "Right : public Base\nvoid stepRight();", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    p.append(b_left)
    p.append(b_right)

    # Bottom
    b_bot, _, _ = textbox(360, 240, "Bottom : public Left, public Right\nДВА екземпляри Base всередині!", size=12, pad=8, fill="#fbeee8", stroke=POS, bold=True)
    p.append(b_bot)

    # Arrows in graph
    p.append(arrow(210, 125, 305, 85, color=NEG, sw=1.5))
    p.append(arrow(510, 125, 415, 85, color=FIELD, sw=1.5))
    p.append(arrow(330, 215, 240, 175, color=POS, sw=1.5))
    p.append(arrow(390, 215, 480, 175, color=POS, sw=1.5))

    # Bottom memory breakdown
    b_mem, _, _ = textbox(360, 315, "Розкладка пам'яті Bottom: [ Left::Base (counter) | Left ] [ Right::Base (counter) | Right ] [ Bottom ]\nВиклик bottom.counter спричиняє помилку компіляції: неоднозначність (ambiguity)", size=11, pad=6, fill="#fff9e6", stroke="#d4ac0d")
    p.append(b_mem)

    render(os.path.join(OUT, "diamond-problem.svg"), W, H, *p)


# ── virtual-inheritance-layout: Розкладка з віртуальною базою ────────────────
def fig_virtual_inheritance():
    W, H = 760, 360
    p = []

    p.append(text(380, 24, "Віртуальне спадкування: єдиний спільний екземпляр через vbtable/vtable", size=15, bold=True, color=INK))

    x0 = 60
    y0 = 80
    h_box = 60

    # Derived complete object layout
    # Left subobject (with vbptr)
    w1 = 180
    p.append(rect(x0, y0, w1, h_box, fill="#e8f4fc", stroke=NEG, sw=1.6, rx=4))
    p.append(text(x0 + w1 / 2, y0 + 20, "Під-об'єкт Left", size=12, bold=True, color=NEG))
    p.append(text(x0 + w1 / 2, y0 + 38, "vbptr_Left", size=11, bold=True, color=POS))
    p.append(text(x0 + w1 / 2, y0 + 52, "int left_data (4B)", size=10, color=MUTED))

    # Right subobject (with vbptr)
    w2 = 180
    p.append(rect(x0 + w1, y0, w2, h_box, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(x0 + w1 + w2 / 2, y0 + 20, "Під-об'єкт Right", size=12, bold=True, color=FIELD))
    p.append(text(x0 + w1 + w2 / 2, y0 + 38, "vbptr_Right", size=11, bold=True, color=POS))
    p.append(text(x0 + w1 + w2 / 2, y0 + 52, "int right_data (4B)", size=10, color=MUTED))

    # Bottom fields
    w3 = 110
    p.append(rect(x0 + w1 + w2, y0, w3, h_box, fill="#fdf2e9", stroke=POS, sw=1.6, rx=4))
    p.append(text(x0 + w1 + w2 + w3 / 2, y0 + 24, "Bottom data", size=12, bold=True, color=POS))
    p.append(text(x0 + w1 + w2 + w3 / 2, y0 + 44, "int bot (4B)", size=10, color=MUTED))

    # Shared Virtual Base at end
    w4 = 170
    p.append(rect(x0 + w1 + w2 + w3, y0, w4, h_box, fill="#fbeee8", stroke=POS, sw=1.8, rx=4))
    p.append(text(x0 + w1 + w2 + w3 + w4 / 2, y0 + 20, "СПІЛЬНИЙ Virtual Base", size=11, bold=True, color=POS))
    p.append(text(x0 + w1 + w2 + w3 + w4 / 2, y0 + 38, "int counter (4B)", size=11, color=INK))
    p.append(text(x0 + w1 + w2 + w3 + w4 / 2, y0 + 52, "Один екземпляр на весь Bottom", size=9, color=MUTED))

    # Tables (vbtables / vtable offsets)
    # vbtable for Left
    x_t1 = 150
    y_t1 = 200
    p.append(rect(x_t1, y_t1, 140, 50, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(x_t1 + 70, y_t1 + 18, "vbtable (Left)", size=11, bold=True, color=NEG))
    p.append(text(x_t1 + 70, y_t1 + 38, "зсув до Base = +470 B", size=10, color=INK))

    # Arrow vbptr_Left -> vbtable Left
    p.append(arrow(x0 + w1 / 2, y0 + h_box, x_t1 + 70, y_t1 - 4, color=POS, sw=1.5))

    # vbtable for Right
    x_t2 = 330
    y_t2 = 200
    p.append(rect(x_t2, y_t2, 140, 50, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(x_t2 + 70, y_t2 + 18, "vbtable (Right)", size=11, bold=True, color=FIELD))
    p.append(text(x_t2 + 70, y_t2 + 38, "зсув до Base = +290 B", size=10, color=INK))

    # Arrow vbptr_Right -> vbtable Right
    p.append(arrow(x0 + w1 + w2 / 2, y0 + h_box, x_t2 + 70, y_t2 - 4, color=POS, sw=1.5))

    # Arrow from vbtable to shared base
    p.append(arrow(x_t2 + 140, y_t2 + 25, x0 + w1 + w2 + w3 + w4 / 2, y0 + h_box + 5, color=POS, sw=1.5))

    # Summary note
    b_foot, _, _ = textbox(380, 310, "Зсув до віртуальної бази не є фіксованою константою часу компіляції: він обчислюється динамічно\nчерез вказівник на таблицю зсувів (vbptr/vtable offset). Ціна: додаткове розіменування пам'яті.", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    p.append(b_foot)

    render(os.path.join(OUT, "virtual-inheritance-layout.svg"), W, H, *p)


# ── composition-vs-inheritance: IS-A проти HAS-A ─────────────────────────────
def fig_composition_vs_inheritance():
    W, H = 740, 320
    p = []

    p.append(text(370, 24, "Спадкування (IS-A, біла скринька) проти Композиції (HAS-A, чорна скринька)", size=15, bold=True, color=INK))

    # Left Column: Inheritance
    x_l = 190
    p.append(text(x_l, 60, "Спадкування (Біла скринька)", size=13, bold=True, color=POS))
    p.append(rect(x_l - 150, 75, 300, 160, fill="#fdf3f2", stroke=POS, sw=1.5, rx=6))

    p.append(rect(x_l - 120, 90, 240, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(x_l, 110, "Базовий клас (Base)", size=11, bold=True, color=INK))
    p.append(text(x_l, 126, "розкриває деталі реалізації нащадку", size=10, color=MUTED))

    p.append(arrow(x_l, 175, x_l, 138, color=POS, sw=1.8))

    p.append(rect(x_l - 120, 175, 240, 45, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_l, 195, "Похідний клас (Derived)", size=11, bold=True, color=POS))
    p.append(text(x_l, 211, "жорстко зв'язаний з порядком викликів Base", size=10, color=MUTED))

    p.append(text(x_l, 256, "Ламкість: зміна Base ламає Derived", size=11, color=POS, bold=True))

    # Right Column: Composition
    x_r = 550
    p.append(text(x_r, 60, "Композиція (Чорна скринька)", size=13, bold=True, color=FIELD))
    p.append(rect(x_r - 150, 75, 300, 160, fill="#f2faf5", stroke=FIELD, sw=1.5, rx=6))

    p.append(rect(x_r - 120, 90, 240, 45, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_r, 110, "Інтерфейс / Компонент", size=11, bold=True, color=FIELD))
    p.append(text(x_r, 126, "лише відкритий публічний контракт", size=10, color=MUTED))

    p.append(arrow(x_r, 175, x_r, 138, color=FIELD, sw=1.8))

    p.append(rect(x_r - 120, 175, 240, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(x_r, 195, "Клас-клієнт (Holder)", size=11, bold=True, color=INK))
    p.append(text(x_r, 211, "володіє об'єктом через поле/покажчик", size=10, color=MUTED))

    p.append(text(x_r, 256, "Гнучкість: заміна компонента без наслідків", size=11, color=FIELD, bold=True))

    # Footer
    b_foot, _, _ = textbox(370, 292, "Принцип проєктування: надавайте перевагу композиції об'єктів над спадкуванням класів", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    p.append(b_foot)

    render(os.path.join(OUT, "composition-vs-inheritance.svg"), W, H, *p)


# ── c3-linearization-graph: MRO та C3-лінеаризація ───────────────────────────
def fig_c3_linearization():
    W, H = 720, 320
    p = []

    p.append(text(360, 24, "Граф множинного спадкування та C3 MRO (Method Resolution Order)", size=15, bold=True, color=INK))

    # Graph nodes
    # Object (O)
    b_o, _, _ = textbox(360, 60, "O (Object)", size=12, pad=6, fill="#f4f6f8", stroke=LINE)
    p.append(b_o)

    # A, B
    b_a, _, _ = textbox(240, 130, "A : O", size=11, pad=6, fill="#e8f4fc", stroke=NEG)
    b_b, _, _ = textbox(480, 130, "B : O", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    p.append(b_a)
    p.append(b_b)

    # C
    b_c, _, _ = textbox(360, 200, "C : A, B", size=12, pad=6, fill="#fdf2e9", stroke=POS, bold=True)
    p.append(b_c)

    # Arrows
    p.append(arrow(240, 110, 325, 75, color=NEG, sw=1.5))
    p.append(arrow(480, 110, 395, 75, color=FIELD, sw=1.5))
    p.append(arrow(330, 180, 265, 148, color=POS, sw=1.5))
    p.append(arrow(390, 180, 455, 148, color=POS, sw=1.5))

    # Resulting Linear Order
    p.append(rect(60, 250, 600, 50, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(360, 270, "Результат лінеаризації C3(C) = [ C, A, B, O ]", size=13, bold=True, color=INK))
    p.append(text(360, 288, "Гарантує монотонність: порядок предків A і B узгоджений з порядком їхнього оголошення в C", size=10, color=MUTED))

    render(os.path.join(OUT, "c3-linearization-graph.svg"), W, H, *p)


if __name__ == "__main__":
    fig_subobject_single()
    fig_subobject_multiple()
    fig_diamond_problem()
    fig_virtual_inheritance()
    fig_composition_vs_inheritance()
    fig_c3_linearization()
    print("All figures generated successfully.")
