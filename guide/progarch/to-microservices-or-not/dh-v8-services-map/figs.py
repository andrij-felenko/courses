# -*- coding: utf-8 -*-
"""Фігури до кроку «Чи різати хмару DH? Рішення через ADR»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#c77d0a"   # застереження «~» (нейтральніше за червоне)


def glyph(cx, cy, kind, size=22):
    """Клітинка матриці: 'y' зелена ✓, 'n' синій ✗, 'c' бурштиновий ~."""
    if kind == "y":
        return text(cx, cy + size * 0.34, "✓", size=size, color=FIELD, bold=True)
    if kind == "n":
        return text(cx, cy + size * 0.34, "✗", size=size, color=NEG, bold=True)
    return text(cx, cy + size * 0.30, "~", size=size + 4, color=AMBER, bold=True)


def fig_verdict_matrix():
    """Шість контекстів × чотири питання → присуд."""
    W, H = 1120, 660
    frags = []

    # ── геометрія сітки ──
    hx0 = 26          # рядок-заголовок (назва контексту): 26..262
    hx1 = 262
    col_x0 = 270      # перша крит-колонка
    col_w = 118
    col_c = [col_x0 + col_w / 2 + i * col_w for i in range(4)]   # центри 4 колонок
    vx0 = col_x0 + 4 * col_w + 8                                 # присуд
    vx1 = W - 20
    v_c = (vx0 + vx1) / 2

    head_top = 46
    head_bot = 150
    row_h = 74
    row_top = head_bot
    row_c = [row_top + row_h / 2 + i * row_h for i in range(6)]
    grid_bot = row_top + 6 * row_h

    # ── шапка колонок ──
    heads = ["Володіє\nсвоїми\nданими?",
             "Розмови\nрідкі\nй грубі?",
             "Терпить\nмережу\nна гарячому?",
             "Має власну\nпричину\nжити окремо?"]
    for c, h in zip(col_c, heads):
        frags.append(mtext(c, head_top + 20, h, size=13, color=MUTED, bold=True, lh=1.25))
    frags.append(text((hx0 + hx1) / 2, head_top + 44, "Контекст хмари", size=13,
                      color=MUTED, bold=True))
    frags.append(text(v_c, head_top + 44, "Присуд", size=14, color=INK, bold=True))

    # ── роздільники ──
    frags.append(line(hx0, head_bot, vx1, head_bot, color=MUTED, sw=1.4))
    for i in range(1, 6):
        y = row_top + i * row_h
        frags.append(line(hx0, y, vx1, y, color="#e2e5ea", sw=1))
    for x in [(hx1 + col_x0) / 2, col_x0 + col_w, col_x0 + 2 * col_w, col_x0 + 3 * col_w, vx0 - 4]:
        frags.append(line(x, head_top + 4, x, grid_bot, color="#e2e5ea", sw=1))

    # ── рядки: (назва, [клітини], присуд, колір-заливка, колір-обвід) ──
    rows = [
        ("Телеметрія",            ["y", "y", "y", "y"], "РІЗАТИ ЗАРАЗ",        "#eafaf0", FIELD),
        ("Відео",                 ["y", "y", "y", "y"], "РІЗАТИ ЗАРАЗ",        "#eafaf0", FIELD),
        ("Автоматизації",         ["c", "n", "n", "n"], "ЛИШИТИ В ЯДРІ",       "#eef2fb", NEG),
        ("Ідентичність",          ["y", "n", "c", "y"], "ВИНОСИТИ — з кешем",  "#fbf1e0", AMBER),
        ("Білінг · лічба",        ["y", "y", "y", "n"], "ЛИШИТИ МОДУЛЕМ",      "#f2f3f5", MUTED),
        ("Ядро: керування\n+ твін", ["n", "n", "n", "n"], "НЕ РІЗАТИ — серце", "#fdecea", POS),
    ]
    for i, (name, cells, verdict, fillc, strokec) in enumerate(rows):
        cy = row_c[i]
        # назва контексту (ліворуч, у дві лінії за потреби)
        nlines = name.split("\n")
        ny = cy - (len(nlines) - 1) * 15 / 2
        frags.append(mtext(hx0 + 12, ny + 5, nlines, size=14, color=INK,
                           anchor="start", bold=True, lh=1.15))
        # клітини
        for c, k in zip(col_c, cells):
            frags.append(glyph(c, cy, k))
        # присуд-чип
        b, _, _ = textbox(v_c, cy, verdict, size=13, fill=fillc, stroke=strokec,
                          sw=2, bold=True, min_w=vx1 - vx0 - 10)
        frags.append(b)

    # ── легенда ──
    ly = grid_bot + 30
    frags.append(text(hx0 + 12, ly, "✓ сприяє розрізу", size=12, color=FIELD,
                      anchor="start", bold=True))
    frags.append(text(hx0 + 190, ly, "✗ проти розрізу", size=12, color=NEG,
                      anchor="start", bold=True))
    frags.append(text(hx0 + 360, ly, "~ із застереженням", size=12, color=AMBER,
                      anchor="start", bold=True))

    render(os.path.join(IMG, "verdict-matrix.svg"), W, H, *frags,
           title="Присуд — не смак, а стовпчик відповідей")


def fig_services_topology():
    """До → після: назовні вийшли лише телеметрія й відео."""
    W, H = 1180, 600
    frags = []

    def chip(cx, cy, label, fillc, strokec=MUTED, w=150):
        b, bw, bh = textbox(cx, cy, label, size=12.5, fill=fillc, stroke=strokec,
                            sw=1.4, min_w=w)
        return b

    # ── ЛІВОРУЧ: ДО ──
    frags.append(text(250, 62, "ДО: один моноліт", size=15, bold=True, color=INK))
    # хаб у домі — вже за межею машини
    frags.append(chip(120, 120, "ДІМ · Хаб", "#fff8e1", INK, w=120))
    frags.append(line(120, 146, 210, 210, color=MUTED, sw=1.4, dash="5,6"))
    frags.append(text(78, 178, "межа машини", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(78, 193, "(вже є)", size=10.5, color=MUTED, anchor="start"))
    # коробка моноліта
    frags.append(rect(60, 210, 400, 330, fill="#f4f6f8", stroke=INK, sw=2.4))
    frags.append(text(260, 236, "ХМАРА DH", size=13, bold=True, color=INK))
    mono = ["Керування", "Твін", "Автоматизації", "Сповіщення",
            "Телеметрія", "Відео", "Білінг", "Ідентичність"]
    xs = [160, 360]
    ys = [280, 340, 400, 460]
    for i, name in enumerate(mono):
        cx = xs[i % 2]
        cy = ys[i // 2]
        hot = name in ("Телеметрія", "Відео")
        frags.append(chip(cx, cy, name, "#eef2fb" if hot else "#eaeef3",
                          NEG if hot else MUTED, w=150))

    # ── стрілка рішення ──
    frags.append(arrow(478, 375, 560, 375, color=INK, sw=2.6))
    frags.append(text(519, 358, "ADR-021", size=12, bold=True, color=INK))

    # ── ПРАВОРУЧ: ПІСЛЯ ──
    frags.append(text(880, 62, "ПІСЛЯ: ядро + два сервіси", size=15, bold=True, color=INK))
    # хаб
    frags.append(chip(650, 120, "ДІМ · Хаб", "#fff8e1", INK, w=120))
    frags.append(line(650, 146, 720, 210, color=MUTED, sw=1.4, dash="5,6"))
    # ядро-моноліт
    frags.append(rect(600, 210, 330, 330, fill="#f4fbf6", stroke=FIELD, sw=3))
    frags.append(text(765, 236, "ЯДРО-моноліт", size=13, bold=True, color=FIELD))
    core = ["Керування", "Твін", "Автоматизації", "Сповіщення", "Білінг", "Ідентичність"]
    cxs = [685, 845]
    cys = [285, 350, 415]
    for i, name in enumerate(core):
        frags.append(chip(cxs[i % 2], cys[i // 2], name, "#eafaf0", FIELD, w=140))

    # нова межа машини
    frags.append(line(965, 210, 965, 540, color=POS, sw=1.6, dash="6,6"))
    frags.append(text(965, 200, "нова межа машини", size=11, color=POS, bold=True))
    # потік подій ядро → сервіси
    frags.append(arrow(932, 330, 1010, 300, color=INK, sw=2))
    frags.append(text(985, 345, "потік подій", size=10.5, color=MUTED))

    # два винесені сервіси зі своїм сховищем
    def service(cx, cy, label):
        b, bw, bh = textbox(cx, cy, label, size=12.5, fill="#eef2fb", stroke=NEG,
                            sw=2.4, min_w=150)
        # маленький циліндр «БД»
        dbx, dby = cx, cy + bh / 2 + 22
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="20" ry="6" fill="%s" stroke="%s" stroke-width="1.4"/>' % (dbx, dby - 12, "#dfe6f6", NEG))
        frags.append('<path d="M%.1f %.1f v20 a20 6 0 0 0 40 0 v-20" fill="#dfe6f6" stroke="%s" stroke-width="1.4"/>' % (dbx - 20, dby - 12, NEG))
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="20" ry="6" fill="#eef2fb" stroke="%s" stroke-width="1.4"/>' % (dbx, dby - 12, NEG))
        frags.append(text(dbx, dby - 8, "своє", size=9.5, color=NEG))
        return b

    frags.append(service(1055, 285, "Телеметрія\n— сервіс"))
    frags.append(service(1055, 435, "Відео\n— сервіс"))

    frags.append(text(W / 2, H - 16,
                      "розріз додав рівно дві мережі, а не вісім — назовні пішло лише те, що заробило причину",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "services-topology.svg"), W, H, *frags,
           title="Що насправді змінилося після рішення")


def cellmark(cx, cy, kind, size=22):
    """Клітинка матриці правил: 'y' ✓ дозволено, 'n' ✗ заборонено, 's' · своя зона."""
    if kind == "y":
        return text(cx, cy + size * 0.34, "✓", size=size, color=FIELD, bold=True)
    if kind == "n":
        return text(cx, cy + size * 0.34, "✗", size=size, color=NEG, bold=True)
    return text(cx, cy + 4, "·", size=size + 12, color=MUTED, bold=True)


def fig_dependency_rules():
    """Матриця дозволених залежностей, яку кодує фітнес-функція (ADR-021)."""
    W, H = 900, 604
    frags = []
    zones = ["ядро", "телеметрія", "відео", "порти", "контракти"]
    # рядок — хто імпортує; стовпець — кого; y=можна, n=не можна, s=своя зона
    M = [
        ["s", "n", "n", "y", "y"],   # ядро
        ["n", "s", "n", "y", "y"],   # телеметрія
        ["n", "n", "s", "y", "y"],   # відео
        ["n", "n", "n", "s", "y"],   # порти
        ["n", "n", "n", "n", "s"],   # контракти
    ]
    lx0, lx1 = 24, 196
    gx0, cw = 200, 138
    col_c = [gx0 + cw / 2 + i * cw for i in range(5)]
    head_top, head_bot, rh = 58, 152, 74
    row_c = [head_bot + rh / 2 + i * rh for i in range(5)]
    grid_bot = head_bot + 5 * rh
    gx1 = gx0 + 5 * cw

    frags.append(text((lx0 + lx1) / 2, head_top + 6, "хто імпортує", size=12.5,
                      color=MUTED, bold=True))
    frags.append(text((lx0 + lx1) / 2, head_top + 26, "↓", size=15, color=MUTED, bold=True))
    frags.append(text(gx0 + 5 * cw / 2, 46, "кого імпортує  →", size=12.5,
                      color=MUTED, bold=True))
    for c, z in zip(col_c, zones):
        frags.append(text(c, head_top + 62, z, size=13, color=INK, bold=True))

    frags.append(line(lx0, head_bot, gx1, head_bot, color=MUTED, sw=1.4))
    for i in range(1, 5):
        frags.append(line(lx0, head_bot + i * rh, gx1, head_bot + i * rh, color="#e2e5ea", sw=1))
    for i in range(6):
        frags.append(line(gx0 + i * cw, head_top + 70, gx0 + i * cw, grid_bot, color="#e2e5ea", sw=1))
    frags.append(line(gx0 - 4, head_top + 70, gx0 - 4, grid_bot, color=MUTED, sw=1.2))

    for r, z in enumerate(zones):
        cy = row_c[r]
        frags.append(text(lx1 - 10, cy + 5, z, size=13.5, color=INK, anchor="end", bold=True))
        for cc, k in zip(col_c, M[r]):
            frags.append(cellmark(cc, cy, k))

    ly = grid_bot + 34
    frags.append(text(lx0 + 6, ly, "✓ дозволено", size=12.5, color=FIELD, anchor="start", bold=True))
    frags.append(text(lx0 + 176, ly, "✗ заборонено — сторож валить білд", size=12.5,
                      color=NEG, anchor="start", bold=True))
    frags.append(text(lx0 + 6, ly + 24, "· своя зона — вільно", size=12.5,
                      color=MUTED, anchor="start", bold=True))
    render(os.path.join(IMG, "dep-rules.svg"), W, H, *frags,
           title="Що сторож пускає, а що валить")


def fig_strangler_steps():
    """Порядок виносу телеметрії: обвити → подвійний запис → перетнути. Порт незмінний."""
    W, H = 1180, 500
    frags = []

    frags.append(rect(60, 70, 1060, 46, fill="#eef2fb", stroke=INK, sw=2))
    frags.append(text(W / 2, 98,
                      "порт  TelemetrySink.record(e)  —  форма незмінна у всіх трьох фазах",
                      size=13.5, color=INK, bold=True))

    for cx, hd in zip([220, 590, 950],
                      ["1 · обвити новим", "2 · подвійний запис", "3 · перетнути й прибрати"]):
        frags.append(text(cx, 52, hd, size=14, color=INK, bold=True))
    for x in (410, 770):
        frags.append(line(x, 132, x, H - 34, color="#e2e5ea", sw=1, dash="4,6"))

    def box(cx, cy, label, fill, stroke, w=190):
        b, _, _ = textbox(cx, cy, label, size=12.5, fill=fill, stroke=stroke, sw=2, min_w=w)
        frags.append(b)

    # ── фаза 1 ──
    frags.append(arrow(140, 116, 140, 190, color=FIELD, sw=2.4))
    box(140, 214, "InProcessSink\n(старий, у ядрі)", "#eafaf0", FIELD, w=155)
    frags.append(line(315, 116, 315, 186, color=MUTED, sw=1.4, dash="4,6"))
    box(315, 214, "RemoteSink\n(не ввімкнено)", "#f2f3f5", MUTED, w=150)
    frags.append(text(220, 434, "старий шлях працює;", size=11.5, color=MUTED))
    frags.append(text(220, 451, "новий стоїть поруч", size=11.5, color=MUTED))

    # ── фаза 2 ──
    frags.append(arrow(590, 116, 590, 190, color=AMBER, sw=2.4))
    box(590, 214, "MigratingSink\n(пише в обидва)", "#fbf1e0", AMBER, w=200)
    frags.append(arrow(556, 240, 506, 322, color=MUTED, sw=1.8))
    frags.append(arrow(624, 240, 674, 322, color=MUTED, sw=1.8))
    box(505, 348, "старе сховище\n(читаємо)", "#f2f3f5", MUTED, w=150)
    box(675, 348, "сервіс\n(пишемо теж)", "#eef2fb", NEG, w=150)
    frags.append(text(590, 434, "пишемо в обидва, звіряємо,", size=11.5, color=MUTED))
    frags.append(text(590, 451, "доганяємо історію", size=11.5, color=MUTED))

    # ── фаза 3 ──
    frags.append(arrow(950, 116, 950, 190, color=NEG, sw=2.4))
    box(950, 214, "RemoteSink\n(єдиний шлях)", "#eef2fb", NEG, w=200)
    frags.append(line(950, 240, 950, 322, color="#c9ccd2", sw=1.4, dash="4,5"))
    box(945, 348, "старе сховище\nзнято", "#f7f7f8", "#c9ccd2", w=150)
    frags.append(text(1032, 348, "✗", size=20, color=POS, bold=True))
    frags.append(text(950, 434, "старий шлях знято;", size=11.5, color=MUTED))
    frags.append(text(950, 451, "порт той самий", size=11.5, color=MUTED))

    render(os.path.join(IMG, "strangler-steps.svg"), W, H, *frags,
           title="Винос через strangler-fig: обвити, не рубати")


def fig_remonolith_timeline():
    """Хроніка суперечки «чи різати»: 2015 → 2023 (до вставки hist-remonolith)."""
    W, H = 1260, 440
    frags = []

    spine_y = 214
    x0, x1 = 60, 1190
    frags.append(line(x0, spine_y, x1, spine_y, color=MUTED, sw=2.5))
    frags.append(text(x1 - 4, spine_y - 20, "час →", size=12.5, color=MUTED,
                      anchor="end", italic=True))

    span = x1 - x0
    cx = [x0 + span * (i + 0.5) / 4 for i in range(4)]

    # (рік, колір-акцент, тінт-заливка, рядки картки)
    nodes = [
        ("2014–15", MUTED, "#f2f3f5",
         ["Пік моди:", "«ріж усе", "на сервіси»"]),
        ("червень 2015", NEG, "#eef2fb",
         ["Fowler: «моноліт", "спершу» ⇄ Tilkov:", "«не починай»", "— це ДЕБАТИ"]),
        ("липень 2018", AMBER, "#fbf1e0",
         ["Segment,", "«Goodbye", "Microservices»:", "140+ → знову моноліт"]),
        ("березень 2023", FIELD, "#eafaf0",
         ["Prime Video · VQA:", "один інструмент,", "S3 → один процес,", "−90% витрат"]),
    ]

    card_top = spine_y + 46
    for c, (year, accent, tint, lines) in zip(cx, nodes):
        frags.append(text(c, spine_y - 26, year, size=15, color=INK, bold=True))
        frags.append(circle(c, spine_y, 10, fill=tint, stroke=accent, sw=3))
        h = (len(lines) + 1) * 16.25
        card_cy = card_top + h / 2
        frags.append(line(c, spine_y + 13, c, card_top, color=accent, sw=2))
        b, _, _ = textbox(c, card_cy, lines, size=12.5, fill=tint, stroke=accent,
                          sw=2, min_w=250)
        frags.append(b)

    frags.append(text(W / 2, H - 18,
                      "мережу купують, коли контекст її заробив — а не за гаслом",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "remonolith-timeline.svg"), W, H, *frags,
           title="«Чи різати» — хроніка суперечки, 2015 → 2023")


if __name__ == "__main__":
    fig_verdict_matrix()
    fig_services_topology()
    fig_dependency_rules()
    fig_strangler_steps()
    fig_remonolith_timeline()
    print("OK: verdict-matrix.svg, services-topology.svg, dep-rules.svg, "
          "strangler-steps.svg, remonolith-timeline.svg")
