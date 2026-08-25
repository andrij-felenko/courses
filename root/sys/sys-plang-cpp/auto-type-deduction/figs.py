# -*- coding: utf-8 -*-
"""Фігури до теми «auto й виведення типу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_as_template():
    W, H = 960, 340
    out = []

    b1, w1, h1 = textbox(240, 120, "const auto& r = expr;", size=17, pad=16, bold=True)
    out.append(b1)
    out.append(text(240, 120 - h1 / 2 - 16, "що написано в коді", size=13, color=MUTED))

    b2, w2, h2 = textbox(710, 120,
                         ["template<class T>", "void f(const T& param);", "f(expr);"],
                         size=15, pad=16)
    out.append(b2)
    out.append(text(710, 120 - h2 / 2 - 16, "за якими правилами це читає компілятор", size=13, color=MUTED))

    out.append(arrow(240 + w1 / 2 + 14, 120, 710 - w2 / 2 - 14, 120))
    out.append(text((240 + w1 / 2 + 710 - w2 / 2) / 2, 104, "ті самі правила", size=13, color=MUTED))

    y = 250
    for cx, s in ((175, "auto  →  T"),
                  (480, "декларатор  →  тип параметра"),
                  (800, "expr  →  аргумент виклику")):
        bb, _, _ = textbox(cx, y, s, size=14, pad=12, fill="#eef4ff", stroke=NEG)
        out.append(bb)
    out.append(text(W / 2, 310, "виведене T підставляється на місце auto", size=13, color=MUTED))

    render(os.path.join(IMG, 'auto-as-template.svg'), W, H, *out,
           title="auto — не тип, а місце для типу")


def fig_forms():
    W = 1060
    M = 30
    head = ["форма", "посилання\nініціалізатора", "верхній\nconst", "масив int[5]", "const int ci  →"]
    cols = [190, 230, 150, 210, 190]
    rows = [
        ["auto x", "відкидає", "відкидає", "розпад → int*", "int"],
        ["const auto x", "відкидає", "ставить свій", "розпад → int*", "const int"],
        ["auto& x", "відкидає", "зберігає", "int (&)[5]", "const int&"],
        ["const auto& x", "відкидає", "ставить свій", "int (&)[5]", "const int&"],
        ["auto&& x", "lvalue → X&\nrvalue → X&&", "зберігає", "int (&)[5]", "const int&"],
    ]
    HH, RH, GAP = 66, 62, 6
    H = 56 + HH + len(rows) * RH + 30
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 56, c - GAP, HH - GAP, head[i], size=14, bold=True,
                          fill="#e8edf3"))
        x += c

    y = 56 + HH
    for r in rows:
        x = M
        for i, cell in enumerate(r):
            fill = "#f7f9fb" if i else "#eef4ff"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=14,
                              bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'deduction-forms.svg'), W, H, *out,
           title="Що кожна форма робить з типом ініціалізатора")


def fig_decltype():
    W, H = 980, 420
    out = []

    b0, w0, h0 = textbox(W / 2, 90, "int i = 0;   const int& r = i;", size=16, pad=14, bold=True)
    out.append(b0)

    lx, rx = 250, 720
    b1, _, h1 = textbox(lx, 190, "auto a = r;", size=15, pad=12, fill="#eef4ff", stroke=NEG)
    b2, _, h2 = textbox(rx, 190, "decltype(r) b = i;", size=15, pad=12, fill="#fdecea", stroke=POS)
    out.append(b1)
    out.append(b2)

    out.append(arrow(W / 2 - 60, 90 + h0 / 2 + 6, lx, 190 - h1 / 2 - 10))
    out.append(arrow(W / 2 + 60, 90 + h0 / 2 + 6, rx, 190 - h2 / 2 - 10))

    b3, _, h3 = textbox(lx, 290, ["a  —  це  int", "копію робимо з нуля: посилання",
                                  "й верхній const відпадають"], size=14, pad=12)
    b4, _, h4 = textbox(rx, 290, ["b  —  це  const int&", "тип узято рівно такий,",
                                  "яким його оголосили"], size=14, pad=12)
    out.append(b3)
    out.append(b4)
    out.append(arrow(lx, 190 + h1 / 2 + 4, lx, 290 - h3 / 2 - 6))
    out.append(arrow(rx, 190 + h2 / 2 + 4, rx, 290 - h4 / 2 - 6))

    b5, _, _ = textbox(W / 2, 382, "decltype((i))  —  це  int& :  (i) вже не ім'я, а вираз-lvalue",
                       size=14, pad=12, fill="#fff8e1", stroke="#b8860b")
    out.append(b5)

    render(os.path.join(IMG, 'decltype-vs-auto.svg'), W, H, *out,
           title="auto бере тип копії, decltype — тип оголошення")


def fig_tools():
    """Три способи подивитися виведений тип — і що кожен зберігає."""
    W = 1090
    M = 30
    head = ["прилад", "посилання", "верхній\nconst", "масив int[5]", "коли відповідає"]
    cols = [280, 150, 150, 200, 230]
    rows = [
        ["TD<decltype(x)>",
         "зберігає", "зберігає", "int (&)[5]", "під час компіляції\n(збірка падає)"],
        ["type_name<decltype(x)>()",
         "зберігає", "зберігає", "int (&)[5]", "під час виконання\n(рядок у консоль)"],
        ["typeid(x).name()",
         "СТИРАЄ", "СТИРАЄ", "int [5]", "під час виконання"],
    ]
    HH, RH, GAP = 62, 64, 6
    H = 56 + HH + len(rows) * RH + 34
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 56, c - GAP, HH - GAP, head[i], size=14, bold=True,
                          fill="#e8edf3"))
        x += c

    y = 56 + HH
    for ri, r in enumerate(rows):
        bad = (ri == 2)
        x = M
        for i, cell in enumerate(r):
            if i == 0:
                fill = "#fdecea" if bad else "#eef4ff"
            else:
                fill = "#fdecea" if bad and i in (1, 2) else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=14,
                              bold=(i == 0),
                              color=(POS if bad and i in (1, 2) else INK),
                              fill=fill))
            x += cols[i]
        y += RH

    out.append(text(W / 2, H - 14,
                    "перші два прилади відповідають на те саме питання, що й auto; "
                    "typeid — на інше",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'deduction-tools.svg'), W, H, *out,
           title="Чим дивитися на виведений тип")


def fig_history():
    """Паперовий слід decltype/auto: від Cfront-1984 до N3922."""
    W = 1020
    AX = 210          # вісь часу
    BX = 250          # ліва межа рамок
    BW = 730
    BH = 54
    STEP = 72
    Y0 = 76
    rows = [
        ("1984", "Cfront: виведення типу з ініціалізатора вже працює — і його прибирають",
         "перешкода — сумісність із C, де auto означало тривалість зберігання", "old"),
        ("квіт. 2003", "N1478 «Decltype and auto» — Järvi, Stroustrup, Gregor, Siek",
         "привід: тип результату шаблонної функції неможливо записати", "paper"),
        ("2003", "N1527: те саме, але вже під іменем decltype",
         "typeof зайняте розбіжними розширеннями компіляторів", "paper"),
        ("лист. 2004", "N1737, Walter E. Brown: повернути кілька деклараторів",
         "щоб можна було писати for (auto it = m.begin(), e = m.end(); …)", "paper"),
        ("квіт. 2006", "N1984 — редакція, якою auto ввійшло в чернетку C++0x",
         "auto й decltype відтоді рухаються окремими паперами", "paper"),
        ("2007", "N2337 (синтаксис auto) і N2343 (формулювання decltype)",
         "фічі перекладено мовою тексту стандарту", "paper"),
        ("лют. 2008", "N2546: старе значення auto вилучено остаточно",
         "у мільйонах рядків знайшли лише поодинокі вжитки", "paper"),
        ("верес. 2011", "C++11: auto й decltype стають частиною мови",
         "GCC 4.3 має decltype, GCC 4.4 — auto; VC++ 2010 — обидва", "std"),
        ("квіт. 2013", "N3638, Jason Merrill: тип повернення звичайних функцій і decltype(auto)",
         "реалізовано в GCC ще до ухвалення; увійшло в C++14", "paper"),
        ("лют. 2014", "N3922: нові правила виведення з фігурних дужок",
         "EWG визнала стару поведінку дефектом; чинне з C++17", "paper"),
    ]
    H = Y0 + len(rows) * STEP + 20
    out = []
    out.append(line(AX, Y0 - 8, AX, Y0 + (len(rows) - 1) * STEP + BH / 2 + 8,
                    color=MUTED, sw=2))
    colors = {"old": ("#f3f3f3", MUTED), "paper": ("#f4f6f8", LINE),
              "std": ("#eaf7ee", FIELD)}
    for i, (year, head, sub, kind) in enumerate(rows):
        y = Y0 + i * STEP
        cy = y + BH / 2
        fill, stroke = colors[kind]
        out.append(circle(AX, cy, 7, fill=fill, stroke=stroke, sw=2))
        out.append(text(AX - 22, cy + 5, year, size=14, color=INK, anchor="end", bold=True))
        out.append(fitbox(BX, y, BW, BH, [head, sub], size=14, fill=fill, stroke=stroke))
    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *out,
           title="Двадцять років двом словам: паперовий слід decltype і auto")


fig_as_template()
fig_forms()
fig_decltype()
fig_tools()
fig_history()
print("ok")
