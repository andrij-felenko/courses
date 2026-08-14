# -*- coding: utf-8 -*-
"""Фігури до теми «CRTP: статичний поліморфізм»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_crtp_dispatch():
    """Порівняння динамічної диспетчеризації (vtable) та статичної (CRTP)."""
    W, H = 1040, 380
    out = []

    # Ліва частина — Динамічний поліморфізм
    lx = 260
    b_dyn_title, _, _ = textbox(lx, 60, "Динамічний поліморфізм (Virtual Dispatch)", size=15, pad=12, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_dyn_title)

    b1, _, _ = textbox(lx, 130, "Об'єкт у пам'яті: [ vptr | data ]", size=13, pad=10, fill="#ffffff", stroke=LINE)
    b2, _, _ = textbox(lx, 210, "Таблиця vtable: [ &Derived::draw ]", size=13, pad=10, fill="#ffffff", stroke=LINE)
    b3, _, _ = textbox(lx, 290, "Виклик: ptr->draw()\n(непрямий перехід через vtable)", size=13, pad=10, fill="#fdecea", stroke=POS)
    out.append(b1)
    out.append(b2)
    out.append(b3)
    out.append(arrow(lx, 150, lx, 190, color=POS))
    out.append(arrow(lx, 230, lx, 270, color=POS))

    # Розділювальна лінія
    out.append(line(520, 40, 520, 350, color=MUTED, dash="4,4"))

    # Права частина — Статичний поліморфізм (CRTP)
    rx = 780
    b_crtp_title, _, _ = textbox(rx, 60, "Статичний поліморфізм (CRTP)", size=15, pad=12, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_crtp_title)

    b4, _, _ = textbox(rx, 130, "Об'єкт Derived: [ data ] (без vptr!)", size=13, pad=10, fill="#ffffff", stroke=LINE)
    b5, _, _ = textbox(rx, 210, "Base<Derived>::draw():\nstatic_cast<Derived*>(this)->impl()", size=13, pad=10, fill="#ffffff", stroke=LINE)
    b6, _, _ = textbox(rx, 290, "Прямий виклик / Інлайнінг:\nDerived::draw_impl() (0 тактів індирекції)", size=13, pad=10, fill="#eaf7ee", stroke=FIELD)
    out.append(b4)
    out.append(b5)
    out.append(b6)
    out.append(arrow(rx, 150, rx, 190, color=FIELD))
    out.append(arrow(rx, 230, rx, 270, color=FIELD))

    render(os.path.join(IMG, 'crtp-dispatch.svg'), W, H, *out,
           title="Порівняння накладних витрат: vtable проти CRTP")


def fig_crtp_hierarchy():
    """Схема успадкування й інстанціювання CRTP-шаблону."""
    W, H = 980, 340
    out = []

    b_base, _, _ = textbox(490, 80, ["template <typename Derived>", "class Base {", "  void process() { static_cast<Derived*>(this)->impl(); }", "};"],
                           size=13, pad=14, fill="#eef4ff", stroke=NEG)
    out.append(b_base)

    b_d1, _, _ = textbox(240, 240, ["class DerivedA :", "  public Base<DerivedA> {", "  void impl();", "};"],
                         size=13, pad=12, fill="#ffffff", stroke=LINE)
    b_d2, _, _ = textbox(740, 240, ["class DerivedB :", "  public Base<DerivedB> {", "  void impl();", "};"],
                         size=13, pad=12, fill="#ffffff", stroke=LINE)
    out.append(b_d1)
    out.append(b_d2)

    out.append(arrow(240, 190, 380, 130, color=NEG))
    out.append(arrow(740, 190, 600, 130, color=NEG))

    out.append(text(310, 150, "Base<DerivedA>", size=12, color=MUTED))
    out.append(text(670, 150, "Base<DerivedB>", size=12, color=MUTED))

    render(os.path.join(IMG, 'crtp-hierarchy.svg'), W, H, *out,
           title="Генерація окремих типів Base<T> для кожного похідного класу")


def fig_crtp_vs_deducing_this():
    """Еволюція від класичного CRTP до C++23 deducing this."""
    W, H = 1000, 340
    out = []

    b1, _, _ = textbox(250, 100, "C++98 .. C++20: CRTP Mixin", size=15, pad=12, fill="#eef4ff", stroke=NEG, bold=True)
    b2, _, _ = textbox(250, 220, ["template <typename Derived>", "struct Printable {", "  void print() const {", "    static_cast<const Derived*>(this)->format();", "  }", "};", "struct Item : Printable<Item> {};"],
                       size=12, pad=12, fill="#ffffff", stroke=LINE)
    out.append(b1)
    out.append(b2)

    out.append(arrow(470, 160, 530, 160, color=LINE))
    out.append(text(500, 140, "C++23", size=13, color=MUTED, bold=True))

    b3, _, _ = textbox(750, 100, "C++23: Explicit Object Parameter", size=15, pad=12, fill="#eaf7ee", stroke=FIELD, bold=True)
    b4, _, _ = textbox(750, 220, ["struct Printable {", "  void print(this const auto& self) {", "    self.format();", "  }", "};", "struct Item : Printable {}; // Звичайне успадкування!"],
                       size=12, pad=12, fill="#ffffff", stroke=LINE)
    out.append(b3)
    out.append(b4)

    render(os.path.join(IMG, 'crtp-vs-deducing-this.svg'), W, H, *out,
           title="Спрощення міксинів у C++23 завдяки deducing this")


if __name__ == '__main__':
    fig_crtp_dispatch()
    fig_crtp_hierarchy()
    fig_crtp_vs_deducing_this()
    print("ok")
