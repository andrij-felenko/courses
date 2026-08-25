# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK,
            lh=1.5, dash=None, anchor="middle"):
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
        out += mono(px, cy + i * size * lh, ln, size=size, color=color, anchor=anchor)
    return out


# ── 1. Кваліфікатори після дужок проти названого параметра ─────────────────
# Серце теми: об'єкт завжди був аргументом, але його тип писали кваліфікаторами,
# а кваліфікатор не виводиться — звідси й чотири тіла замість одного.
def fig_object_parameter():
    W, H = 1120, 500
    p = []

    p.append(line(560, 56, 560, 452, color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(285, 48, "тип об'єкта записано кваліфікаторами", size=13.5, bold=True, color=POS))
    p.append(text(845, 48, "тип об'єкта записано параметром", size=13.5, bold=True, color=FIELD))

    # ліва панель
    p.append(monobox(40, 78, 480, 62,
                     ["аргумент об'єкта є, але імені не має:",
                      "його тип виводити нема з чого"],
                     size=11.5, fill="#fdecea", stroke=POS, sw=1.6, color=POS, dash="7 5"))
    sigs = [
        "std::string&        get() &",
        "const std::string&  get() const&",
        "std::string&&       get() &&",
        "const std::string&& get() const&&",
    ]
    for i, s in enumerate(sigs):
        p.append(monobox(40, 174 + i * 56, 480, 44, [s], size=12, anchor="start",
                         fill=FILL, stroke=LINE, sw=1.4))
    p.append(text(280, 432, "чотири оголошення — один і той самий текст тіла",
                  size=12, color=POS))

    # права панель
    p.append(monobox(600, 78, 480, 62,
                     ["self — звичайний параметр:",
                      "його тип виводиться, як у будь-якого шаблона"],
                     size=11.5, fill="#eef7f0", stroke=FIELD, sw=1.6, color=FIELD))
    p.append(monobox(600, 202, 480, 100,
                     ["template <class Self>",
                      "auto&& get(this Self&& self)",
                      "{ return std::forward<Self>(self).val; }"],
                     size=12, anchor="start", fill="#eef7f0", stroke=FIELD, sw=2.2))
    p.append(text(840, 344, "одне тіло покриває всі чотири випадки", size=12, color=FIELD))
    p.append(text(840, 376, "виклик не змінюється: b.get()", size=11.5, color=MUTED))
    p.append(text(840, 432, "кваліфікаторів після дужок більше немає —", size=11.5, color=MUTED))
    p.append(text(840, 454, "вони переїхали в тип параметра", size=11.5, color=MUTED))

    render(os.path.join(OUT, "object-parameter.svg"), W, H,
           title="Об'єкт як аргумент: безіменний і названий", *p)


# ── 2. Що саме виводиться в Self для кожного виразу виклику ────────────────
# Таблиця, без якої тема лишається на рівні гасла: категорія й константність
# виразу виклику перетворюються на різницю в Self і доживають до значення, що повертають.
def fig_self_deduction():
    W = 1180
    cols = 5
    x0, cw, gap = 34, 208, 20
    xs = [x0 + i * (cw + gap) for i in range(cols)]

    heads = [
        ["вираз виклику"],
        ["аргумент", "об'єкта"],
        ["Self", "виводиться як"],
        ["Self&&", "після згортання"],
        ["тип, що", "повертають"],
    ]
    rows = [
        (NEG, "#eef3ff", [
            ["b.get()"],
            ["lvalue типу Box"],
            ["Box&"],
            ["Box& && → Box&"],
            ["std::string&"],
        ]),
        (NEG, "#eef3ff", [
            ["cb.get()"],
            ["const lvalue"],
            ["const Box&"],
            ["const Box&"],
            ["const std::string&"],
        ]),
        (FIELD, "#eef7f0", [
            ["std::move(b).get()"],
            ["xvalue типу Box"],
            ["Box"],
            ["Box&&"],
            ["std::string&&"],
        ]),
        (FIELD, "#eef7f0", [
            ["std::move(cb).get()"],
            ["const xvalue"],
            ["const Box"],
            ["const Box&&"],
            ["const std::string&&"],
        ]),
    ]

    top, rh, vgap = 96, 62, 24
    H = top + len(rows) * (rh + vgap) + 84
    p = []
    for i, h in enumerate(heads):
        p.append(mtext(xs[i] + cw / 2, 62, h, size=11.5, color=MUTED, lh=1.35))

    for r, (accent, bg, cells) in enumerate(rows):
        ry = top + r * (rh + vgap)
        for i, lines in enumerate(cells):
            edge = accent if i in (0, 4) else LINE
            fl = bg if i in (0, 4) else FILL
            p.append(monobox(xs[i], ry, cw, rh, lines, size=12,
                             fill=fl, stroke=edge, sw=2.0 if i in (0, 4) else 1.3))
            if i < cols - 1:
                p.append(arrow(xs[i] + cw + 3, ry + rh / 2, xs[i + 1] - 3, ry + rh / 2,
                               color=accent, sw=1.5))

    p.append(text(W / 2, H - 46, "категорія й константність виразу виклику доходять до тіла всередині Self",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 22, "звернення до члена rvalue-об'єкта саме є xvalue — тому передається й член",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "self-deduction.svg"), W, H,
           title="Один шаблон, чотири інстанції", *p)


# ── 3. CRTP проти виведеного Self ──────────────────────────────────────────
# Показує, що зникає саме обов'язок автора бази назвати похідний тип наперед.
def fig_crtp_vs_self():
    W, H = 1120, 520
    p = []

    p.append(text(300, 62, "CRTP: похідний тип називають руками", size=13.5, bold=True, color=POS))
    p.append(text(820, 62, "Явний параметр: Self виводиться", size=13.5, bold=True, color=FIELD))

    left = [
        "template <class D>",
        "struct Printable {",
        "  void print() const {",
        "    std::cout <<",
        "      static_cast<const D&>(*this).text();",
        "  }",
        "};",
        "",
        "struct Note : Printable<Note> { ... };",
    ]
    right = [
        "struct Printable {",
        "  void print(this const auto& self) {",
        "    std::cout << self.text();",
        "  }",
        "};",
        "",
        "",
        "",
        "struct Note : Printable { ... };",
    ]
    p.append(monobox(40, 86, 520, 224, left, size=11.5, anchor="start",
                     fill="#fdecea", stroke=POS, sw=2.0, lh=1.6))
    p.append(monobox(580, 86, 500, 224, right, size=11.5, anchor="start",
                     fill="#eef7f0", stroke=FIELD, sw=2.0, lh=1.6))

    lbul = [
        "база — шаблон: Printable<Note> і Printable<Tag>",
        "різні типи, спільної бази немає",
        "автор бази пише приведення сам",
    ]
    rbul = [
        "база — один звичайний тип для всіх нащадків",
        "Self = Note постає з типу виразу виклику",
        "приведення робить виведення аргументів",
    ]
    for i, s in enumerate(lbul):
        p.append(text(56, 348 + i * 26, "· " + s, size=11.5, color=INK, anchor="start"))
    for i, s in enumerate(rbul):
        p.append(text(596, 348 + i * 26, "· " + s, size=11.5, color=INK, anchor="start"))

    p.append(monobox(230, 442, 660, 54,
                     ["Note n;  n.print();  — обидва варіанти статичні:",
                      "функцію обирає тип виразу, а не таблиця віртуальних методів"],
                     size=11.5, fill=FILL, stroke=MUTED, sw=1.4, lh=1.5))

    render(os.path.join(OUT, "crtp-vs-self.svg"), W, H,
           title="Хто називає похідний тип", *p)


# ── 4. Хронологія паперу P0847 і підтримки в компіляторах (для hist-вставки) ─
# Показує головну дивину історії: реалізація в MSVC вийшла раніше за стандарт,
# а дві інші — на два роки пізніше за нього.
def fig_p0847_timeline():
    W = 1160
    rows = [
        ("2018-02-12", "P0847R0", "перша редакція; синтаксис Self&& this self", NEG),
        ("2018-06", "Rapperswil", "доповідь в EWG; синтаксис зсунуто на this Self&& self", NEG),
        ("2018-11", "R1, San Diego", "порівняння чотирьох синтаксисів і схем пошуку імен", NEG),
        ("2019-01", "R2, Kona", "FAQ: відгук авторів бібліотек, рекурсивні лямбди", NEG),
        ("2019-11", "R3, Belfast", "EWG вимагає формулювань стандарту й реалізації", NEG),
        ("2020", "R4", "формулювання й реалізація; static, неявний виклик", NEG),
        ("2021", "R5", "повернуто розділ про відкинуті синтаксиси", NEG),
        ("2021-07-12", "R7", "остання правка формулювань після телеконференції CWG", NEG),
        ("2021-10", "пленум WG21", "CWG-голосування 3: P0847R7 внесено в чернетку C++23", FIELD),
        ("2022-05", "MSVC 17.2", "перша реалізація — за півтора року до виходу C++23", FIELD),
        ("2024-03", "Clang 18", "реалізовано, але без макроса __cpp_explicit_this_parameter", FIELD),
        ("2024-05", "GCC 14", "остання з трійки великих реалізацій", FIELD),
    ]

    top, rh, gap = 74, 46, 14
    H = top + len(rows) * (rh + gap) + 46
    xd, wd = 34, 168
    xk, wk = 222, 214
    xt = 460
    p = []

    p.append(text(W / 2, 42, "Вісім редакцій, один пленум, три компілятори",
                  size=13.5, bold=True, color=INK))
    p.append(line(xd + wd / 2, top + 8, xd + wd / 2, top + len(rows) * (rh + gap) - 18,
                  color=MUTED, sw=1.2, dash="5 5"))

    for i, (date, key, what, accent) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(monobox(xd, y, wd, rh, [date], size=12, fill="#f4f6fa",
                         stroke=accent, sw=1.8, color=INK))
        p.append(monobox(xk, y, wk, rh, [key], size=12, fill=FILL,
                         stroke=LINE, sw=1.3, color=accent))
        p.append(arrow(xd + wd + 3, y + rh / 2, xk - 3, y + rh / 2, color=accent, sw=1.4))
        p.append(text(xt, y + rh / 2 + 4, what, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "p0847-timeline.svg"), W, H,
           title="Шлях P0847 від задачі до компіляторів", *p)


if __name__ == "__main__":
    fig_object_parameter()
    fig_self_deduction()
    fig_crtp_vs_self()
    fig_p0847_timeline()
    print("ok")
