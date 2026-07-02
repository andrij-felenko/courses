# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── layers: три вкладені кола API ⊃ ABI ⊃ calling convention ──────────────────
# Ідея: угода про виклик — лише серцевина ширшого ABI; ABI — двійковий рівень
# усередині ще ширшого API (рівня вихідного тексту).

def fig_layers():
    W, H = 560, 460
    cx, cy = 280, 250
    p = []

    # три кола від найширшого (API) до найвужчого (угода про виклик)
    p.append(circle(cx, cy, 200, fill="#eef2f7", stroke=MUTED, sw=1.5))
    p.append(circle(cx, cy, 138, fill="#e3ecf9", stroke=NEG, sw=1.8))
    p.append(circle(cx, cy, 72, fill="#fdeeea", stroke=POS, sw=1.8))

    # підписи кіл (зверху кожного кільця)
    p.append(text(cx, 64, "API — рівень вихідного тексту", size=14, bold=True, color=MUTED))
    p.append(text(cx, 78, "(як писати код: імена, типи в мові)", size=11, color=MUTED))

    p.append(text(cx, 132, "ABI — рівень скомпільованого коду", size=14, bold=True, color=NEG))

    # вміст середнього кільця (ABI) — по боках від центрального
    b, w1, h1 = textbox(cx - 108, cy, ["розміри", "типів"], size=11, pad=7, fill=BG, stroke=NEG)
    p.append(b)
    b, w1, h1 = textbox(cx + 108, cy, ["розкладка", "структур"], size=11, pad=7, fill=BG, stroke=NEG)
    p.append(b)
    b, w1, h1 = textbox(cx, cy + 108, ["імена символів", "(name mangling)"], size=11, pad=7, fill=BG, stroke=NEG)
    p.append(b)

    # центр — угода про виклик
    p.append(text(cx, cy - 14, "угода", size=14, bold=True, color=POS))
    p.append(text(cx, cy + 4, "про виклик", size=14, bold=True, color=POS))
    p.append(text(cx, cy + 24, "аргументи · регістри", size=10, color=POS))

    render(os.path.join(OUT, "layers.svg"), W, H, *p)


# ── struct-layout: наївні 6 байтів проти реальних 12 із набивкою ─────────────
# Ідея: компілятор мовчки вставляє байти-набивку заради вирівнювання —
# розкладка структури теж частина ABI, і обидва боки мусять збігатися.

def fig_struct():
    W, H = 720, 340
    p = []
    x0 = 70
    cell = 46          # ширина байт-комірки
    yA = 110           # наївна смуга
    yB = 250           # реальна смуга
    ch = 46            # висота комірки

    def byte(x, y, label, fill, stroke=LINE, tcol=INK):
        out = rect(x, y, cell, ch, fill=fill, stroke=stroke, sw=1.5, rx=4)
        out += text(x + cell / 2, y + ch / 2 + 5, label, size=13, bold=True, color=tcol)
        return out

    def idx(x, y, n):
        return text(x + cell / 2, y - 8, str(n), size=10, color=MUTED)

    # заголовки смуг
    p.append(text(x0 - 8, yA - 34, "Наївно: 1 + 4 + 1 = 6 байтів", size=13, bold=True, anchor="start", color=MUTED))
    p.append(text(x0 - 8, yB - 34, "Реально (ABI): 12 байтів — із набивкою", size=13, bold=True, anchor="start", color=INK))

    # наївна смуга: type value(4) flag — впритул
    naive = [("type", FIELD, "type"), ("value", NEG, "value"),
             ("value", NEG, ""), ("value", NEG, ""), ("value", NEG, ""),
             ("flag", POS, "flag")]
    # намалюємо як 6 комірок, value злите в один широкий блок
    x = x0
    p.append(idx(x, yA, 0)); p.append(byte(x, yA, "type", "#d5f0e0", stroke=FIELD)); x += cell
    p.append(idx(x, yA, 1))
    p.append(rect(x, yA, cell * 4, ch, fill="#dbe6fb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(x + cell * 2, yA + ch / 2 + 5, "value (4)", size=13, bold=True, color=NEG))
    x += cell * 4
    p.append(idx(x, yA, 5)); p.append(byte(x, yA, "flag", "#fbe0da", stroke=POS)); x += cell

    # реальна смуга: type · 3 набивки · value(4) · flag · 3 набивки
    x = x0
    p.append(idx(x, yB, 0)); p.append(byte(x, yB, "type", "#d5f0e0", stroke=FIELD)); x += cell
    for n in (1, 2, 3):
        p.append(idx(x, yB, n))
        p.append(byte(x, yB, "░", "#f0f1f3", stroke=MUTED, tcol=MUTED)); x += cell
    p.append(idx(x, yB, 4))
    p.append(rect(x, yB, cell * 4, ch, fill="#dbe6fb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(x + cell * 2, yB + ch / 2 + 5, "value (4)", size=13, bold=True, color=NEG))
    x += cell * 4
    p.append(idx(x, yB, 8)); p.append(byte(x, yB, "flag", "#fbe0da", stroke=POS)); x += cell
    for n in (9, 10, 11):
        p.append(idx(x, yB, n))
        p.append(byte(x, yB, "░", "#f0f1f3", stroke=MUTED, tcol=MUTED)); x += cell

    # легенда набивки
    p.append(rect(x0, yB + ch + 24, 20, 20, fill="#f0f1f3", stroke=MUTED, sw=1.5, rx=3))
    p.append(text(x0 + 30, yB + ch + 39, "░ — набивка: невидимі байти заради вирівнювання",
                  size=12, anchor="start", color=MUTED))

    render(os.path.join(OUT, "struct-layout.svg"), W, H, *p)


# ── mangling: три перевантажені add → три різні символи; C add → простий ─────
# Ідея: перевантаження дає кілька функцій з одним іменем; mangling вшиває типи
# в символ, щоб пласка таблиця лінкера бачила різні імена.

def fig_mangling():
    W, H = 720, 380
    p = []
    lx = 60          # ліва колонка (код)
    rx = 470         # права колонка (символи)
    ys = [80, 150, 220]
    labels = [("add(int, int)", "_Z3addii"),
              ("add(double, double)", "_Z3adddd"),
              ("add(int, int, int)", "_Z3addiii")]

    p.append(text(lx + 120, 44, "C++: три функції add", size=13, bold=True, color=INK))
    p.append(text(rx + 90, 44, "три різні символи в лінкері", size=13, bold=True, color=INK))

    for (code, sym), y in zip(labels, ys):
        b, w1, h1 = textbox(lx + 120, y, code, size=13, pad=9, fill="#fdeeea", stroke=POS)
        p.append(b)
        p.append(arrow(lx + 120 + w1 / 2 + 6, y, rx + 90 - 96, y, color=MUTED))
        b, w1, h1 = textbox(rx + 90, y, sym, size=13, pad=9, fill="#e3ecf9", stroke=NEG, min_w=170)
        p.append(b)

    # роздільна лінія
    p.append(line(50, 278, W - 40, 278, color=MUTED, sw=1, dash="4,4"))

    # C: без перевантаження — простий символ
    p.append(text(lx + 120, 312, "C: одна функція add", size=13, bold=True, color=MUTED))
    b, w1, h1 = textbox(lx + 120, 344, "add(int, int)", size=13, pad=9, fill=FILL, stroke=FIELD)
    p.append(b)
    p.append(arrow(lx + 120 + w1 / 2 + 6, 344, rx + 90 - 60, 344, color=FIELD))
    b, w1, h1 = textbox(rx + 90, 344, "add", size=13, pad=9, fill="#d5f0e0", stroke=FIELD, min_w=170)
    p.append(b)

    render(os.path.join(OUT, "mangling.svg"), W, H, *p)


# ── pack-map: та сама struct із набивкою й запакована, байт за байтом ─────────
# Ідея: #pragma pack / packed прибирає невидиму набивку — sizeof падає з 12 до 6,
# але поле value тепер починається зі зсуву 1 (невирівняне).

def fig_pack_map():
    W, H = 720, 340
    p = []
    x0 = 70
    cell = 46
    ch = 46
    yA = 110          # звичайна (з набивкою)
    yB = 250          # запакована

    def byte(x, y, label, fill, stroke, tcol=INK):
        out = rect(x, y, cell, ch, fill=fill, stroke=stroke, sw=1.5, rx=4)
        out += text(x + cell / 2, y + ch / 2 + 5, label, size=13, bold=True, color=tcol)
        return out

    def idx(x, y, n):
        return text(x + cell / 2, y - 8, str(n), size=10, color=MUTED)

    def val4(x, y, note):
        out = rect(x, y, cell * 4, ch, fill="#dbe6fb", stroke=NEG, sw=1.5, rx=4)
        out += text(x + cell * 2, y + ch / 2 + 5, "value (4)", size=13, bold=True, color=NEG)
        if note:
            out += text(x + cell * 2, y + ch + 16, note, size=10, color=NEG)
        return out

    p.append(text(x0 - 8, yA - 34, "Звичайна розкладка: sizeof = 12", size=13, bold=True, anchor="start", color=INK))
    p.append(text(x0 - 8, yB - 34, "packed / #pragma pack(1): sizeof = 6", size=13, bold=True, anchor="start", color=POS))

    # звичайна: type · 3 набивки · value(4)@4 · flag · 3 набивки
    x = x0
    p.append(idx(x, yA, 0)); p.append(byte(x, yA, "type", "#d5f0e0", FIELD)); x += cell
    for n in (1, 2, 3):
        p.append(idx(x, yA, n)); p.append(byte(x, yA, "░", "#f0f1f3", MUTED, tcol=MUTED)); x += cell
    p.append(idx(x, yA, 4)); p.append(val4(x, yA, "зсув 4 — кратно 4 ✓")); x += cell * 4
    p.append(idx(x, yA, 8)); p.append(byte(x, yA, "flag", "#fbe0da", POS)); x += cell
    for n in (9, 10, 11):
        p.append(idx(x, yA, n)); p.append(byte(x, yA, "░", "#f0f1f3", MUTED, tcol=MUTED)); x += cell

    # запакована: type · value(4)@1 · flag — впритул
    x = x0
    p.append(idx(x, yB, 0)); p.append(byte(x, yB, "type", "#d5f0e0", FIELD)); x += cell
    p.append(idx(x, yB, 1)); p.append(val4(x, yB, "зсув 1 — НЕ кратно 4 ✗")); x += cell * 4
    p.append(idx(x, yB, 5)); p.append(byte(x, yB, "flag", "#fbe0da", POS)); x += cell

    render(os.path.join(OUT, "pack-map.svg"), W, H, *p)


# ── ptr-hazard: член читається побайтово (безпечно) vs адреса члена → word LDR ─
# Ідея: прямий доступ до поля запакованої структури компілятор робить побайтово
# (безпечно навіть на M0); а взяття адреси члена дає невирівняний вказівник,
# який під час розіменування піде звичайним LDR → hard fault на Cortex-M0.

def fig_ptr_hazard():
    W, H = 720, 400
    p = []
    cx = W / 2

    # запакована структура зверху: value@1
    x0, cell, ch, yS = 250, 40, 40, 60
    p.append(text(cx, yS - 18, "packed struct: value лежить зі зсуву 1", size=13, bold=True, color=INK))
    x = x0
    p.append(rect(x, yS, cell, ch, fill="#d5f0e0", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(x + cell / 2, yS + ch / 2 + 5, "t", size=12, bold=True, color=FIELD)); x += cell
    p.append(rect(x, yS, cell * 4, ch, fill="#dbe6fb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(x + cell * 2, yS + ch / 2 + 5, "value @1", size=12, bold=True, color=NEG))

    # дві гілки
    lx, rx = 185, 535
    yb = 190
    b, w1, h1 = textbox(lx, yb, ["p->value", "(прямий доступ)"], size=12, pad=9, fill=FILL, stroke=FIELD)
    p.append(b)
    b, w2, h2 = textbox(rx, yb, ["&p->value", "(взяли адресу)"], size=12, pad=9, fill="#fdeeea", stroke=POS)
    p.append(b)

    # ліва гілка — безпечно
    b, w1, h1 = textbox(lx, 280, ["компілятор → 4× LDRB", "(байт за байтом)"], size=11, pad=8, fill=BG, stroke=FIELD)
    p.append(b)
    p.append(arrow(lx, yb + h2 / 2 + 4, lx, 280 - h1 / 2 - 4, color=FIELD))
    b, w1, h1 = textbox(lx, 356, "працює на M0 ✓", size=12, pad=8, fill="#d5f0e0", stroke=FIELD, bold=True)
    p.append(b)
    p.append(arrow(lx, 280 + h1 / 2 + 4, lx, 356 - h1 / 2 - 4, color=FIELD))

    # права гілка — пастка
    b, w1, h1 = textbox(rx, 280, ["невирівняний uint32_t*", "розіменування → LDR (word)"], size=11, pad=8, fill=BG, stroke=POS)
    p.append(b)
    p.append(arrow(rx, yb + h2 / 2 + 4, rx, 280 - h1 / 2 - 4, color=POS))
    b, w1, h1 = textbox(rx, 356, "HARD FAULT на Cortex-M0 ✗", size=12, pad=8, fill="#fbe0da", stroke=POS, bold=True)
    p.append(b)
    p.append(arrow(rx, 280 + h1 / 2 + 4, rx, 356 - h1 / 2 - 4, color=POS))

    render(os.path.join(OUT, "ptr-hazard.svg"), W, H, *p)


# ── mangle-babel: одна функція → чотири несумісні символи (до стандарту) ──────
# Ідея: стандарт вимагав лише «різні символи», формат лишав компілятору —
# тож кожен компілятор калічив те саме ім'я по-своєму, і файли не лінкувались.

def fig_mangle_babel():
    W, H = 720, 400
    cx = W / 2
    p = []

    # джерело: одна функція в коді
    p.append(text(cx, 34, "Один вихідний код C++:", size=13, bold=True, color=INK))
    b, w1, h1 = textbox(cx, 70, "add(int, int)", size=14, pad=10, fill="#fdeeea", stroke=POS)
    p.append(b)

    # чотири компілятори, кожен зі своїм несумісним символом
    cols = [
        ("cfront",  "add__Fii",      FIELD, "#d5f0e0"),
        ("GNU 2.x", "add__Fii",      NEG,   "#dbe6fb"),
        ("Borland", "@add$qii",      POS,   "#fbe0da"),
        ("MSVC",    "?add@@YAHHH@Z", MUTED, "#eef0f3"),
    ]
    n = len(cols)
    slot = W / n
    ytop = 118        # де починаються стрілки
    ybox = 205        # рамки компіляторів
    ysym = 300        # символи

    for i, (name, sym, col, fill) in enumerate(cols):
        x = slot * (i + 0.5)
        # стрілка від спільного джерела вниз до компілятора
        p.append(arrow(cx, ytop, x, ybox - 22, color=MUTED))
        # рамка компілятора
        b, w1, h1 = textbox(x, ybox, name, size=13, pad=8, fill=fill, stroke=col, min_w=104)
        p.append(b)
        # стрілка вниз до символу
        p.append(arrow(x, ybox + 22, x, ysym - 20, color=col))
        # символ, який видає цей компілятор
        b, w1, h1 = textbox(x, ysym, sym, size=12, pad=8, fill=BG, stroke=col, min_w=104)
        p.append(b)

    p.append(text(cx, H - 20, "той самий код → чотири несумісні символи → об'єктні файли не лінкуються",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "mangle-babel.svg"), W, H, *p)


# ── abi-timeline: шлях від хаосу mangling до спільного Itanium C++ ABI ────────
# Ідея: ідея з cfront → хаос 1990-х → консорціум (Itanium) → GCC/Clang переймають
# → залізо Itanium помирає, а ABI живе далі на x86 та ARM.

def fig_abi_timeline():
    W, H = 780, 300
    p = []
    x0, x1 = 70, W - 40
    y = 150                       # вісь часу

    # горизонтальна вісь
    p.append(arrow(x0, y, x1, y, color=INK, sw=2))

    # віхи: (частка вздовж осі, рік, підпис[рядки], колір, зверху?)
    marks = [
        (0.02, "1983–85",  ["cfront винаходить", "mangling"],       FIELD, True),
        (0.26, "1990-ті",  ["хаос: у кожного", "своя схема"],       POS,   False),
        (0.50, "1999–2001", ["консорціум:", "Itanium C++ ABI"],     NEG,   True),
        (0.71, "2001+",    ["GCC 3.0, тоді", "Clang переймають"],   NEG,   False),
        (0.96, "2021",     ["Itanium-залізо", "вмирає — ABI живе"], MUTED, True),
    ]

    for frac, year, lines, col, above in marks:
        x = x0 + (x1 - x0) * frac
        # точка на осі
        p.append(circle(x, y, 6, fill=col, stroke=BG, sw=2))
        if above:
            p.append(line(x, y - 8, x, y - 30, color=col, sw=1.5))
            b, w1, h1 = textbox(x, y - 30 - 22, lines, size=11, pad=7, fill=BG, stroke=col)
            p.append(b)
            p.append(text(x, y - 30 - 22 - h1 / 2 - 10, year, size=12, bold=True, color=col))
        else:
            p.append(line(x, y + 8, x, y + 30, color=col, sw=1.5))
            b, w1, h1 = textbox(x, y + 30 + 22, lines, size=11, pad=7, fill=BG, stroke=col)
            p.append(b)
            p.append(text(x, y + 30 + 22 + h1 / 2 + 12, year, size=12, bold=True, color=col))

    # підпис-висновок під віссю праворуч
    p.append(text(W / 2, H - 12, "схема пережила своє залізо: x86-64 · ARM · macOS",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "abi-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_layers()
    fig_struct()
    fig_mangling()
    fig_pack_map()
    fig_ptr_hazard()
    fig_mangle_babel()
    fig_abi_timeline()
    print("figs written to", OUT)
