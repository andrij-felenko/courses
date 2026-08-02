# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK, lh=1.45):
    """Рамка з кількома моноширинними рядками, центрованими всередині."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * lh / 2 + size * 0.35
    for i, ln in enumerate(lines):
        out += mono(x + w / 2, cy + i * size * lh, ln, size=size, color=color)
    return out


# ── 1. Виведення + згортання: дві доріжки одного шаблона ────────────────────
# Серце теми: категорія аргументу перетворюється на різницю в типі T,
# доживає в ньому до тіла й розгортається назад тим самим кастом.
def fig_deduction():
    W, H = 1040, 470
    p = []
    cols = 5
    x0, cw, gap = 30, 168, 30
    xs = [x0 + i * (cw + gap) for i in range(cols)]

    heads = [
        ["місце", "виклику"],
        ["виведення", "T"],
        ["тип параметра", "після згортання"],
        ["std::forward<T>(x)", "= static_cast<T&&>"],
        ["категорія", "на вході в target"],
    ]
    for i, h in enumerate(heads):
        p.append(mtext(xs[i] + cw / 2, 62, h, size=11, color=MUTED, lh=1.35))

    rows = [
        (120, NEG, "#eef3ff", [
            ["std::string s;", "wrapper(s)", "аргумент — lvalue"],
            ["T = std::string&"],
            ["T&& = string& &&", "згортається у", "string&"],
            ["static_cast<", "std::string&>(x)"],
            ["вираз — lvalue", "target копіює"],
        ]),
        (270, FIELD, "#eef7f0", [
            ["wrapper(make())", "аргумент — prvalue", "(тимчасовий об'єкт)"],
            ["T = std::string"],
            ["T&& = string&&", "згортати нічого"],
            ["static_cast<", "std::string&&>(x)"],
            ["вираз — xvalue", "target переміщує"],
        ]),
    ]

    for ry, accent, bg, cells in rows:
        rh = 108
        for i, lines in enumerate(cells):
            st = accent if i in (0, 4) else LINE
            fl = bg if i in (0, 4) else FILL
            p.append(monobox(xs[i], ry, cw, rh, lines, size=11,
                             fill=fl, stroke=st, sw=2.0 if i in (0, 4) else 1.4))
            if i < cols - 1:
                p.append(arrow(xs[i] + cw + 5, ry + rh / 2, xs[i + 1] - 5, ry + rh / 2, color=accent))

    p.append(mono(W / 2, 412, "template <class T>  void wrapper(T&& x) { target(std::forward<T>(x)); }",
                  size=13, bold=True))
    p.append(text(W / 2, 444,
                  "один текст функції — дві різні інстанції; «універсальність» живе рівно до виведення",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "deduction-collapse.svg"), W, H, *p)


# ── 2. Комбінаторний вибух перевантажень проти одного шаблона ───────────────
def fig_explosion():
    W, H = 1010, 410
    p = []
    p.append(line(716, 50, 716, 350, color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(365, 38, "розписати всі комбінації руками", size=13, bold=True, color=POS))
    p.append(text(862, 38, "передавальне посилання", size=13, bold=True, color=FIELD))

    rows = [
        (76, "1 параметр → 2 тіла", ["c", "r"]),
        (166, "2 параметри → 4 тіла", ["cc", "cr", "rc", "rr"]),
        (256, "3 параметри → 8 тіл", ["ccc", "ccr", "crc", "crr", "rcc", "rcr", "rrc", "rrr"]),
    ]
    bw, bg_ = 66, 8
    for y, label, combos in rows:
        p.append(text(112, y, label, size=11, color=MUTED, anchor="start"))
        for i, c in enumerate(combos):
            bx = 112 + i * (bw + bg_)
            p.append(fitbox(bx, y + 10, bw, 34, c, size=13, pad=5,
                            fill="#fdecea", stroke=POS, sw=1.4, color=POS, bold=True))

    p.append(text(112, 330, "c — параметр const T&,   r — параметр T&&", size=11,
                  color=MUTED, anchor="start"))
    p.append(text(112, 352, "усі 2ᴺ тіл дослівно однакові, і для пакета аргументів їх не написати",
                  size=11, color=MUTED, anchor="start"))

    p.append(monobox(742, 150, 240, 96,
                     ["template <class... A>", "void wrapper(A&&... a);"],
                     size=12, fill="#eef7f0", stroke=FIELD, sw=2.2))
    p.append(text(862, 128, "1 тіло — будь-яка кількість", size=11, color=FIELD))
    p.append(text(862, 272, "кожен аргумент передається", size=11, color=MUTED))
    p.append(text(862, 292, "окремим std::forward<A>", size=11, color=MUTED))
    render(os.path.join(OUT, "overload-explosion.svg"), W, H, *p)


# ── 3. Чому ненажерливий шаблон виграє відбір перевантажень ─────────────────
def fig_greedy():
    W, H = 940, 440
    p = []
    p.append(mono(W / 2, 56, "Person p;   Person q{p};", size=15, bold=True))
    p.append(text(W / 2, 80, "p — неконстантне lvalue типу Person", size=12, color=MUTED))

    panels = [
        (55, 380, MUTED, FILL, "програє", MUTED, [
            "Person(const Person&)",
            "прив'язка: Person& → const Person&",
            "ранг: точний збіг",
            "ціль посилання: const Person",
        ]),
        (505, 380, FIELD, "#eef7f0", "перемагає", FIELD, [
            "Person(S&&),  S = Person&",
            "прив'язка: Person& → Person&",
            "ранг: точний збіг",
            "ціль посилання: Person",
        ]),
    ]
    for x, w, stroke, fill, tag, tagc, lines in panels:
        p.append(text(x + w / 2, 116, tag, size=12, color=tagc, bold=True))
        p.append(rect(x, 128, w, 132, fill=fill, stroke=stroke, sw=2.2, rx=10))
        p.append(mono(x + w / 2, 156, lines[0], size=13, bold=True))
        for i, ln in enumerate(lines[1:]):
            p.append(text(x + w / 2, 186 + i * 24, ln, size=11.5, color=INK))

    p.append(rect(120, 296, 700, 62, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(470, 320, "перетворень немає в обох — порівнюються самі прив'язки:", size=12, color=INK))
    p.append(text(470, 342, "менш cv-кваліфікована ціль краща, тож шаблон виграє", size=12.5,
                  color=POS, bold=True))

    p.append(text(W / 2, 390, "правило «нешаблон кращий за шаблон» сюди не доходить —", size=11.5, color=MUTED))
    p.append(text(W / 2, 412, "воно вмикається лише коли послідовності перетворень нерозрізненні", size=11.5, color=MUTED))
    render(os.path.join(OUT, "greedy-ctor.svg"), W, H, *p)


# ── 4. Дванадцять років: від Boost-обхідних шляхів до слова в стандарті ─────
# Для вставки hist-forwarding-problem.md: хроніка паперів комітету.
def fig_timeline():
    rows = [
        ("до 2002", "CWG 106", MUTED,
         "Бʼярне Строуструп: шаблони-біндери мимоволі творять посилання на посилання.",
         "Ухвалено згортання для typedef і аргументу шаблону: T& & стає T&."),
        ("09.09.2002", "N1385  «The Forwarding Problem: Arguments»", POS,
         "Дімов, Гіннант, Абрагамс: сім способів написати наскрізну обгортку, і жоден не годиться.",
         "Підраховано 2ᴺ перевантажень; названо «проблему const». Розвʼязок №7 — те, що маємо нині."),
        ("10.09.2002", "N1377  «Move Semantics Support»", NEG,
         "Ті самі троє наступного дня: токен && і чотири правила згортання посилань.",
         "У тексті прямо сказано: правила критичні і для переміщення, і для ідеального передавання."),
        ("07.09.2004", "N1690  «An Rvalue Reference to the C++ Language»", NEG,
         "Обидва папери зведено в один; стару річ T& відтоді звуть lvalue-посиланням.",
         "Обіцянка: одна перевантажена версія замість 2ᴺ, скільки б параметрів не було."),
        ("03–05.03.2005", "N1770 · N1771", NEG,
         "Формулювання для тексту стандарту — і окремий папір про наслідки для бібліотеки.",
         "Саме там зʼявляються move(), forward(), unique_ptr і move_iterator."),
        ("2011", "C++11", FIELD,
         "Риса в стандарті й у компіляторах. Назви в неї немає.",
         "Оголошення T&& у шаблоні читають за механізмом: «виведення плюс згортання»."),
        ("06.08 / 10 / 01.11.2012", "Скотт Маєрс: «universal reference»", POS,
         "Доповідь на C++ and Beyond (Ешвілл), стаття в Overload 111, передрук на isocpp.",
         "Назву вигадала спільнота, бо комітет її не дав. Вона миттєво приживається."),
        ("06.10.2014", "N4164  «Forwarding References»", FIELD,
         "Саттер, Строуструп, Дос Рейс: «universal» обіцяє «вживай усюди» — і це неправда.",
         "Згортання — механізм, передавання — суть. Дяка Маєрсові за готовність змінити назву."),
        ("C++17", "[temp.deduct.call]/3", FIELD,
         "Термін forwarding reference стоїть у самому стандарті — але не там, де просив N4164.",
         "Визначення прив'язали до виведення аргументів, а не до правил про typedef."),
    ]

    W = 1120
    top, rh = 74, 74
    H = top + len(rows) * rh + 34
    sx = 214                      # вісь часу
    bx, bw = 246, W - 246 - 26    # рамки праворуч від осі

    p = [text(W / 2, 40, "Дванадцять років від «цю функцію не написати» до слова в стандарті",
              size=15, bold=True)]
    p.append(line(sx, top - 6, sx, top + len(rows) * rh - 18, color=MUTED, sw=1.6))

    for i, (date, head, accent, l1, l2) in enumerate(rows):
        y = top + i * rh
        p.append(text(sx - 22, y + 22, date, size=11.5, color=MUTED, anchor="end"))
        p.append(circle(sx, y + 18, 6.5, fill=accent, stroke=accent, sw=1.5))
        p.append(rect(bx, y - 8, bw, 56, fill=FILL, stroke=accent, sw=1.8, rx=8))
        p.append(text(bx + 16, y + 10, head, size=12.5, color=accent, anchor="start", bold=True))
        p.append(text(bx + 16, y + 28, l1, size=11.5, color=INK, anchor="start"))
        p.append(text(bx + 16, y + 44, l2, size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "forwarding-timeline.svg"), W, H, *p)


# ── 5. Пастка проєкту: std::forward у циклі спорожнює аргумент ─────────────
# Для вставки proj-forwarding-factory.md: три знімки одного об'єкта в часі.
def fig_drain():
    W, H = 1020, 470
    cxs = [220, 520, 820]
    bw = 220

    def band(y_head, y_val, y_arrow_top, y_arrow_bot, y_rcv, cells):
        out = []
        for cx, (head, val, val_ok, label, rcv, rcv_ok) in zip(cxs, cells):
            out.append(text(cx, y_head, head, size=11, color=MUTED))
            fill_v = "#eef7f0" if val_ok else "#fdecea"
            edge_v = FIELD if val_ok else POS
            out.append(monobox(cx - bw / 2, y_val, bw, 44, [val],
                               size=12.5, fill=fill_v, stroke=edge_v, sw=2,
                               color=INK if val_ok else POS))
            out.append(arrow(cx - 64, y_arrow_top, cx - 64, y_arrow_bot,
                             color=MUTED, sw=1.8))
            out.append(text(cx - 48, (y_arrow_top + y_arrow_bot) / 2 + 4, label,
                            size=11, color=MUTED, anchor="start"))
            fill_r = "#eef7f0" if rcv_ok else "#fdecea"
            edge_r = FIELD if rcv_ok else POS
            out.append(monobox(cx - bw / 2, y_rcv, bw, 44, [rcv],
                               size=12.5, fill=fill_r, stroke=edge_r, sw=2,
                               color=INK if rcv_ok else POS))
        return out

    p = [text(W / 2, 34, "Один аргумент, три приймачі: куди дівається вміст",
              size=15, bold=True)]

    p.append(text(W / 2, 62, "forward на КОЖНІЙ ітерації — перший забирає все",
                  size=12.5, color=POS, bold=True))
    p += band(84, 94, 142, 178, 182, [
        ("ітерація 1", "value: «вітання»", True,  "переміщення", "A: «вітання»", True),
        ("ітерація 2", "value: <порожньо>", False, "переміщення", "B: <порожньо>", False),
        ("ітерація 3", "value: <порожньо>", False, "переміщення", "C: <порожньо>", False),
    ])

    p.append(line(40, 258, W - 40, 258, color=MUTED, sw=1.2, dash="7 6"))

    p.append(text(W / 2, 288, "forward лише на ОСТАННІЙ — решті копія",
                  size=12.5, color=FIELD, bold=True))
    p += band(310, 320, 368, 404, 408, [
        ("ітерація 1", "value: «вітання»", True, "копія",        "A: «вітання»", True),
        ("ітерація 2", "value: «вітання»", True, "копія",        "B: «вітання»", True),
        ("ітерація 3", "value: «вітання»", True, "переміщення",  "C: «вітання»", True),
    ])

    p.append(text(W / 2, 452,
                  "порожні приймачі — ні помилки збірки, ні падіння: дані просто зникли",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "forward-drain.svg"), W, H, *p)


fig_deduction()
fig_explosion()
fig_greedy()
fig_timeline()
fig_drain()
print("ok")
