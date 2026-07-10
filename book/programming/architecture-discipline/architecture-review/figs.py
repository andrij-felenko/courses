# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def passive_vs_active():
    W, H = 860, 470
    parts = []

    # роздільник між двома панелями
    parts.append(line(W / 2, 60, W / 2, H - 30, color=MUTED, sw=1, dash="4,5"))

    # заголовки панелей
    parts.append(text(W / 4, 46, "Пасивне рев'ю", size=16, color=NEG, bold=True))
    parts.append(text(3 * W / 4, 46, "Активне рев'ю", size=16, color=POS, bold=True))

    # ── ЛІВА панель: пасивне ────────────────────────────────────────────────
    lx = W / 4
    # діаграма-об'єкт
    b, bw, bh = textbox(lx, 118, "готова діаграма", size=13, pad=12,
                        fill=FILL, stroke=LINE)
    parts.append(b)
    # питання
    q, qw, qh = textbox(lx, 190, "«є заперечення?»", size=13, pad=11,
                       fill="#eaf0fd", stroke=NEG)
    parts.append(q)
    parts.append(arrow(lx, 118 + bh / 2, lx, 190 - qh / 2, color=MUTED))
    # рецензент киває
    parts.append(circle(lx, 262, 15, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(text(lx, 300, "рецензент мовчки киває", size=12, color=MUTED))
    parts.append(arrow(lx, 190 + qh / 2, lx, 247, color=MUTED))
    # вада проходить
    v, vw, vh = textbox(lx, 356, "вада проходить\nнепоміченою", size=13, pad=11,
                       fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(v)
    parts.append(arrow(lx, 315, lx, 356 - vh / 2, color=NEG))
    parts.append(minus(lx, 420, r=13))
    parts.append(text(lx, 452, "мовчання = «згода»", size=12, color=NEG))

    # ── ПРАВА панель: активне ───────────────────────────────────────────────
    rx = 3 * W / 4
    # конкретне питання за сценарієм
    q2, q2w, q2h = textbox(rx,
        118, "«проведи стоп крізь структуру:\nвкладеться в 200 мс під піком?»",
        size=12, pad=12, fill="#fdecea", stroke=POS)
    parts.append(q2)
    # рецензент простежує шлях
    parts.append(circle(rx, 200, 15, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(rx, 238, "рецензент простежує шлях", size=12, color=MUTED))
    parts.append(arrow(rx, 118 + q2h / 2, rx, 185, color=LINE))
    # ствердження
    a, aw, ah = textbox(rx, 300, "стверджує, а не заперечує", size=12, pad=11,
                       fill=FILL, stroke=LINE)
    parts.append(a)
    parts.append(arrow(rx, 253, rx, 300 - ah / 2, color=LINE))
    # вада на світлі
    v2, v2w, v2h = textbox(rx, 372, "вада — на світлі", size=13, pad=11,
                          fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(v2)
    parts.append(arrow(rx, 300 + ah / 2, rx, 372 - v2h / 2, color=LINE))
    parts.append(plus(rx, 434, r=13))
    parts.append(text(rx, 460, "питання змушує подивитися", size=12, color=FIELD))

    render(os.path.join(OUT, 'passive-vs-active.svg'), W, H, *parts)


def review_lineage():
    """Нитка рев'ю: від інспекції РЯДКА до розбору ФОРМИ за сценаріями.
    Горизонтальна вісь-стрічка з п'ятьма віхами; над віссю — рік і хто,
    під віссю — що саме додала віха. Ширина колонок з великим запасом,
    щоб довгі підписи не накладалися."""
    W, H = 1020, 430
    parts = []

    axis_y = 210
    x0, x1 = 120, W - 120
    parts.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    parts.append(arrow(x1 - 24, axis_y, x1, axis_y, color=MUTED))

    # п'ять віх: (частка осі 0..1, рік, хто/що коротко, що додало — під віссю)
    milestones = [
        (0.0, "1976", "Феґан, IBM",
         "формальна інспекція\nрядка коду й дизайну\n(пізня переробля 10–100×)"),
        (0.27, "1985", "Парнас і Вайс",
         "активне рев'ю: питай\nконкретне, проси\nСТВЕРДЖУВАТИ"),
        (0.52, "1994", "SAAM, SEI",
         "оцінка структури\nсценаріями\n(змінюваність)"),
        (0.72, "≈1998", "ATAM, SEI",
         "сценарії якості +\nкомпроміси між\nатрибутами"),
        (1.0, "2000", "ARID, Клементс",
         "активне рев'ю форми\nЗА сценаріями якості\n(злиття двох ниток)"),
    ]

    for frac, year, who, adds in milestones:
        x = x0 + frac * (x1 - x0)
        # вузол на осі
        parts.append(circle(x, axis_y, 8, fill=BG, stroke=LINE, sw=2))
        # рік — жирно над віссю
        parts.append(text(x, axis_y - 96, year, size=17, color=INK, bold=True))
        # хто — під роком
        who_box, ww, wh = textbox(x, axis_y - 60, who, size=12, pad=8,
                                  fill=FILL, stroke=LINE)
        parts.append(who_box)
        parts.append(line(x, axis_y - 60 + wh / 2, x, axis_y - 8,
                          color=MUTED, sw=1, dash="3,4"))
        # що додало — під віссю
        parts.append(line(x, axis_y + 8, x, axis_y + 40, color=MUTED, sw=1,
                          dash="3,4"))
        add_box, aw, ah = textbox(x, axis_y + 78, adds, size=11, pad=9,
                                  fill="#f7f9fc", stroke=MUTED, color=INK)
        parts.append(add_box)

    # підпис-нитка внизу
    parts.append(text(W / 2, H - 16,
        "нитка: від інспекції РЯДКА → до розбору ФОРМИ за сценаріями",
        size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, 'review-lineage.svg'), W, H, *parts)


def finding_with_owner():
    """Та сама знахідка з власником і без: ліва (мертва, сіра) vs права (жива, у реєстр)."""
    W, H = 900, 470
    parts = []

    # роздільник між двома панелями
    parts.append(line(W / 2, 64, W / 2, H - 28, color=MUTED, sw=1, dash="4,5"))

    # заголовки панелей
    parts.append(text(W / 4, 44, "знахідка БЕЗ власника", size=15, color=NEG, bold=True))
    parts.append(text(3 * W / 4, 44, "знахідка З власником", size=15, color=POS, bold=True))

    # спільний текст знахідки (щоб видно було: різниця не в тексті)
    finding = "«стоп у спільній черзі з телеметрією;\nпід піком спізнюється»"

    # ── ЛІВА панель: мертва знахідка ────────────────────────────────────────
    lx = W / 4
    # рядок знахідки — сіро, приглушено
    b, bw, bh = textbox(lx, 116, finding, size=12, pad=12,
                        fill="#eef0f2", stroke=MUTED, color=MUTED)
    parts.append(b)
    # три поля: власник / стан / дедлайн — порожні
    fields_l = [("власник:", "— (нічий)", NEG),
                ("стан:", "відкрито", MUTED),
                ("дедлайн:", "— не призначено", MUTED)]
    fy = 196
    for label, val, col in fields_l:
        parts.append(text(lx - 128, fy, label, size=12, color=MUTED, anchor="start"))
        parts.append(text(lx + 128, fy, val, size=12, color=col, anchor="end", bold=(col == NEG)))
        fy += 30
    # присуд
    parts.append(minus(lx, 320, r=13))
    parts.append(text(lx, 356, "нікуди не рухається", size=12, color=NEG))
    v, vw, vh = textbox(lx, 412, "за тиждень —\nжодного сліду", size=12, pad=11,
                       fill="#eef0f2", stroke=MUTED, color=MUTED, bold=True)
    parts.append(v)
    parts.append(arrow(lx, 372, lx, 412 - vh / 2, color=MUTED))

    # ── ПРАВА панель: жива знахідка ─────────────────────────────────────────
    rx = 3 * W / 4
    b2, b2w, b2h = textbox(rx, 116, finding, size=12, pad=12,
                          fill=FILL, stroke=LINE)
    parts.append(b2)
    fields_r = [("власник:", "Оля", FIELD),
                ("стан:", "знімається", INK),
                ("дедлайн:", "день 14", FIELD)]
    fy = 196
    for label, val, col in fields_r:
        parts.append(text(rx - 128, fy, label, size=12, color=MUTED, anchor="start"))
        parts.append(text(rx + 128, fy, val, size=12, color=col, anchor="end", bold=(col == FIELD)))
        fy += 30
    parts.append(plus(rx, 320, r=13))
    parts.append(text(rx, 356, "рухоме зобов'язання", size=12, color=FIELD))
    v2, v2w, v2h = textbox(rx, 412, "у живий реєстр →\nдоведуть до «знято»", size=12, pad=11,
                          fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(v2)
    parts.append(arrow(rx, 372, rx, 412 - v2h / 2, color=FIELD))

    render(os.path.join(OUT, 'finding-with-owner.svg'), W, H, *parts)


def review_spectrum():
    """Одне слово «рев'ю» — п'ять дуже різних практик уздовж осі формальності/ціни.
    Табличний вигляд (рядок = форма), щоб довгі підписи не накладалися."""
    W, H = 1060, 566
    parts = []

    parts.append(text(W / 2, 46,
        "згори вниз: формальність, ціна й церемонність зростають",
        size=12, color=MUTED))
    # ліва вертикальна вісь-стрілка (напрям зростання)
    parts.append(arrow(22, 96, 22, 520, color=MUTED))

    c1x, c1w = 44, 220
    c2x, c2w = 278, 356
    c3x, c3w = 650, 386

    hy, hh = 56, 30
    parts.append(fitbox(c1x, hy, c1w, hh, "форма рев'ю", size=13,
                        fill="#eef1f4", stroke=LINE, bold=True))
    parts.append(fitbox(c2x, hy, c2w, hh, "коли саме брати", size=13,
                        fill="#eef1f4", stroke=LINE, bold=True))
    parts.append(fitbox(c3x, hy, c3w, hh, "як тихо вмирає", size=13,
                        fill="#eef1f4", stroke=LINE, bold=True))

    rows = [
        ("Соло-прогін\n(сам собі)",
         "сам женеш 2–3 драйвер-сценарії\nкрізь власну схему",
         "самообман: своїх сліпих\nплям не видно"),
        ("Рев'ю рішення / ADR\n(парне)",
         "колега стверджує ОДИН сценарій\nза ОДНИМ рішенням",
         "вузьке коло: клас ризику\nбез свого фахівця мовчить"),
        ("Активне рев'ю\n(ARID-клас)",
         "мала команда жене драйвер-\nсценарії крізь незавершену форму",
         "стає судом, щойно автора\nпочинають екзаменувати"),
        ("Повне оцінювання\n(ATAM-клас)",
         "стейкхолдери, дерево корисності,\nкомпроміси — багатоденний розбір",
         "заважке для дрібного;\nобряд раз на рік"),
        ("Архітектурна рада\n(governance)",
         "централізовані ворота\nна КОЖНУ зміну",
         "вузьке місце й театр;\nкоманди обходять"),
    ]
    name_fills = ["#eaf0fd", "#eef5ef", "#fdf6ee", "#fdeee9", "#f8e0d9"]
    ry0, rh, gap = 96, 76, 12
    for i, (nm, wh, fl) in enumerate(rows):
        y = ry0 + i * (rh + gap)
        parts.append(fitbox(c1x, y, c1w, rh, nm, size=12,
                            fill=name_fills[i], stroke=LINE, bold=True))
        parts.append(fitbox(c2x, y, c2w, rh, wh, size=12, fill=BG, stroke=MUTED))
        parts.append(fitbox(c3x, y, c3w, rh, fl, size=12,
                            fill="#fbeae7", stroke=POS, color=POS))

    render(os.path.join(OUT, 'review-spectrum.svg'), W, H, *parts,
           title="Спектр рев'ю: від соло-прогону до архітектурної ради")


def sensitivity_vs_tradeoff():
    """Чутливість vs компроміс: різниця в тому, СКІЛЬКИ атрибутів тягне один гвинтик."""
    W, H = 900, 440
    parts = []

    parts.append(line(W / 2, 74, W / 2, H - 42, color=MUTED, sw=1, dash="4,5"))
    parts.append(text(W / 4, 56, "Точка ЧУТЛИВОСТІ", size=15, color=NEG, bold=True))
    parts.append(text(3 * W / 4, 56, "Точка КОМПРОМІСУ", size=15, color=POS, bold=True))

    # ── ліва: один параметр → один атрибут ──
    lx = W / 4
    p, pw, ph = textbox(lx, 134, "розмір пулу потоків", size=13, pad=11,
                        fill=FILL, stroke=LINE)
    parts.append(p)
    a, aw, ah = textbox(lx, 300, "пропускна здатність", size=13, pad=11,
                        fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(a)
    parts.append(arrow(lx, 134 + ph / 2, lx, 300 - ah / 2, color=LINE))
    parts.append(text(lx, 360, "один гвинтик → один атрибут", size=12,
                      color=FIELD, bold=True))
    parts.append(text(lx, 386, "не крутити наосліп", size=11, color=MUTED))

    # ── права: один параметр → два атрибути навхрест ──
    rx = 3 * W / 4
    p2, p2w, p2h = textbox(rx, 134, "синхронна копія бази", size=13, pad=11,
                          fill=FILL, stroke=LINE)
    parts.append(p2)
    ga, gaw, gah = textbox(rx - 96, 300, "надійність ↑", size=12, pad=10,
                          fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(ga)
    ba, baw, bah = textbox(rx + 96, 300, "латентність ↑", size=12, pad=10,
                          fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(ba)
    parts.append(arrow(rx, 134 + p2h / 2, rx - 96, 300 - gah / 2, color=LINE))
    parts.append(arrow(rx, 134 + p2h / 2, rx + 96, 300 - bah / 2, color=LINE))
    parts.append(text(rx, 360, "один гвинтик → ДВА атрибути навхрест", size=12,
                      color=POS, bold=True))
    parts.append(text(rx, 386, "не виграти все — обрати жертву", size=11, color=MUTED))

    render(os.path.join(OUT, 'sensitivity-vs-tradeoff.svg'), W, H, *parts,
           title="Один гвинтик і один атрибут — чутливість; той самий гвинтик і два навхрест — компроміс")


def view_blindspot():
    """Рев'ю ловить лише те, що показує в'ю: той самий сценарій, два різні в'ю."""
    W, H = 1000, 440
    parts = []

    sx = 150
    s, sw_, sh = textbox(sx, 215, "сценарій:\nстоп під піком\nтелеметрії",
                        size=12, pad=12, fill="#fdecea", stroke=POS)
    parts.append(s)

    tv, tvw, tvh = textbox(520, 120,
        "в'ю ПОКАЗУЄ спільну чергу\n(динамічний в'ю потоку даних)",
        size=12, pad=12, fill=FILL, stroke=LINE)
    parts.append(tv)
    bv, bvw, bvh = textbox(520, 315,
        "в'ю ХОВАЄ чергу\n(лише статичні контейнери)",
        size=12, pad=12, fill="#edeff1", stroke=MUTED, color=MUTED)
    parts.append(bv)

    oa, oaw, oah = textbox(862, 120, "вада на світлі —\nловиться", size=12, pad=11,
                          fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(oa)
    ob, obw, obh = textbox(862, 315, "сценарій хибно\n«проходить»", size=12, pad=11,
                          fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(ob)

    parts.append(arrow(sx + sw_ / 2, 192, 520 - tvw / 2, 134, color=LINE))
    parts.append(arrow(sx + sw_ / 2, 238, 520 - bvw / 2, 302, color=LINE))
    parts.append(arrow(520 + tvw / 2, 120, 862 - oaw / 2, 120, color=FIELD))
    parts.append(arrow(520 + bvw / 2, 315, 862 - obw / 2, 315, color=POS))

    parts.append(text(W / 2, H - 16,
        "той самий сценарій, різні в'ю — вада ловиться лише там, де в'ю її показує",
        size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'view-blindspot.svg'), W, H, *parts,
           title="Рев'ю бачить лише те, що показує в'ю")


def gate_vs_process():
    """Чому рада-ворота захлинається, а процес поради — ні (масштабування рев'ю).
    Ліворуч: N рішень збігаються в ОДНУ раду → черга. Праворуч: кожне рішення
    несе власну коротку розмову (зачеплені + фахівці) → місткість росте з рішеннями."""
    W, H = 1060, 520
    parts = []

    parts.append(line(W / 2, 66, W / 2, H - 26, color=MUTED, sw=1, dash="4,5"))
    parts.append(text(W / 4, 44, "Рада — одні ворота на всіх", size=15, color=NEG, bold=True))
    parts.append(text(3 * W / 4, 44, "Порада — рев'ю в кожному рішенні", size=15, color=POS, bold=True))

    # ── ЛІВА: N рішень збігаються в одну раду ────────────────────────────────
    dec_x = 92
    board_cx, board_cy = 300, 232
    board, bw, bh = textbox(board_cx, board_cy, "Архітектурна\nрада", size=13, pad=14,
                            fill="#eaf0fd", stroke=NEG, bold=True)
    for y in [112, 172, 232, 292, 352]:
        d, dw, dh = textbox(dec_x, y, "рішення", size=11, pad=8, fill=FILL, stroke=LINE)
        parts.append(d)
        parts.append(arrow(dec_x + dw / 2, y,
                           board_cx - bw / 2, board_cy + (y - board_cy) * 0.22, color=MUTED))
    parts.append(board)
    q, qw, qh = textbox(462, board_cy, "черга:\nтижні", size=12, pad=10,
                        fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(q)
    parts.append(arrow(board_cx + bw / 2, board_cy, 462 - qw / 2, board_cy, color=POS))
    parts.append(text(W / 4, 424, "1 тіло · N рішень → черга росте", size=12, color=NEG, bold=True))
    parts.append(text(W / 4, 450, "обхід · посмертна маска · театр", size=11, color=MUTED))

    # ── ПРАВА: кожне рішення — власна коротка розмова ─────────────────────────
    rx = 3 * W / 4
    parts.append(text(rx - 122, 98, "зачеплені", size=10, color=MUTED))
    parts.append(text(rx + 122, 98, "фахівці", size=10, color=MUTED))
    for y in [124, 214, 304, 394]:
        d, dw, dh = textbox(rx, y, "рішення вирішується на місці", size=11, pad=9,
                            fill="#eafaf0", stroke=FIELD)
        parts.append(d)
        parts.append(line(rx - dw / 2, y, rx - dw / 2 - 17, y, color=MUTED, sw=1))
        parts.append(line(rx + dw / 2, y, rx + dw / 2 + 17, y, color=MUTED, sw=1))
        parts.append(circle(rx - dw / 2 - 27, y, 9, fill=FILL, stroke=LINE))
        parts.append(circle(rx + dw / 2 + 27, y, 9, fill=FILL, stroke=LINE))
    parts.append(text(rx, 450, "N рішень · N розмов → місткість росте з рішеннями",
                      size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'gate-vs-process.svg'), W, H, *parts)


def advice_rule():
    """Процес поради як заміна воріт: будь-хто вирішує ⟺ спершу спитав пораду
    в (1) зачеплених і (2) фахівців; порада — не дозвіл; рішення записане."""
    W, H = 940, 470
    parts = []

    top, tw, th = textbox(W / 2, 66, "будь-хто ухвалює архітектурне рішення", size=14,
                          pad=14, fill="#eafaf0", stroke=FIELD, bold=True)
    parts.append(top)
    cond, cw, ch = textbox(W / 2, 150, "⟺ лише якщо СПЕРШУ спитав пораду в:", size=13,
                           pad=12, fill=FILL, stroke=LINE, bold=True)
    parts.append(cond)
    parts.append(arrow(W / 2, 66 + th / 2, W / 2, 150 - ch / 2, color=FIELD))

    lcx, rcx = W / 4 + 24, 3 * W / 4 - 24
    g1, g1w, g1h = textbox(lcx, 254, "усіх, кого рішення\nсуттєво зачепить", size=13,
                           pad=12, fill="#eaf0fd", stroke=NEG)
    g2, g2w, g2h = textbox(rcx, 254, "усіх, хто має фах\nу цій царині", size=13,
                           pad=12, fill="#eaf0fd", stroke=NEG)
    parts.append(g1)
    parts.append(g2)
    parts.append(arrow(W / 2 - 46, 150 + ch / 2, lcx, 254 - g1h / 2, color=LINE))
    parts.append(arrow(W / 2 + 46, 150 + ch / 2, rcx, 254 - g2h / 2, color=LINE))

    n1, n1w, n1h = textbox(lcx, 372,
                           "порада — НЕ дозвіл:\nслухай і зваж,\nрішення лишається твоїм",
                           size=12, pad=12, fill="#fdf6ee", stroke=MUTED)
    n2, n2w, n2h = textbox(rcx, 372,
                           "рішення записане\n(архітектурний запис),\nразом із почутою порадою",
                           size=12, pad=12, fill="#fdf6ee", stroke=MUTED)
    parts.append(n1)
    parts.append(n2)
    parts.append(arrow(lcx, 254 + g1h / 2, lcx, 372 - n1h / 2, color=MUTED))
    parts.append(arrow(rcx, 254 + g2h / 2, rcx, 372 - n2h / 2, color=MUTED))

    render(os.path.join(OUT, 'advice-rule.svg'), W, H, *parts)


def power_regimes():
    """Маятник форм влади над рішенням: централізована рада (ворота) ↔ повний
    децентралізм (без рев'ю); процес поради — продуктивна середина. Стрілка —
    історичний напрям хитання; знизу — хто його штовхав."""
    W, H = 1080, 560
    parts = []

    # полюси й вісь
    parts.append(text(120, 60, "владу ЗОСЕРЕДЖЕНО", size=12, color=MUTED, anchor="start"))
    parts.append(text(W - 120, 60, "владу РОЗДАНО", size=12, color=MUTED, anchor="end"))
    parts.append(text(430, 92, "маятник хитнувся сюди за ~40 років", size=11, color=INK))
    parts.append(arrow(210, 108, 560, 108, color=INK))
    ax_y = 138
    parts.append(line(120, ax_y, W - 120, ax_y, color=MUTED, sw=2))

    cols = [
        (190, "#fdeee9", POS, "ЦЕНТРАЛІЗОВАНА РАДА\n(ворота)",
         "владу зосереджено\nв одному тілі — кожне\nрішення проходить крізь нього\n\nхиба: вузьке місце й театр —\nчерга, обхід,\nпосмертна маска рішення"),
        (540, "#eafaf0", FIELD, "ПРОЦЕС ПОРАДИ\n(розмова)",
         "владу роздано — будь-хто\nвирішує; АЛЕ мусить спитати\nпораду в зачеплених і фахівців;\nзаписи, принципи, радар\nтримають рішення зв'язними\n\nрев'ю живе в КОЖНОМУ рішенні"),
        (890, "#fdeee9", POS, "ПОВНИЙ ДЕЦЕНТРАЛІЗМ\n(без рев'ю)",
         "владу роздано,\nобов'язку радитися немає —\nкожен вирішує сам\n\nхиба: дрейф і незв'язність —\nрішення розповзаються,\nніхто не бачить цілого"),
    ]
    for cx, fill, edge, head, body in cols:
        cw = 300
        x = cx - cw / 2
        parts.append(circle(cx, ax_y, 7, fill=BG, stroke=LINE, sw=2))
        parts.append(line(cx, ax_y + 7, cx, 176, color=MUTED, sw=1, dash="3,4"))
        parts.append(fitbox(x, 176, cw, 46, head, size=13, fill=fill, stroke=edge,
                            color=edge, bold=True))
        parts.append(fitbox(x, 230, cw, 176, body, size=12, fill=BG, stroke=MUTED))

    # хто штовхав маятник до середини
    parts.append(text(W / 2, 440, "хто штовхнув маятник від воріт до розмови",
                      size=12, color=FIELD, bold=True))
    parts.append(line(230, 470, 850, 470, color=MUTED, sw=1.5))
    parts.append(arrow(830, 470, 852, 470, color=MUTED))
    marks = [(300, "AES · Бакке\n1981"),
             (540, "Лалу\n2014"),
             (800, "Гармел-Ло\n2021 → 2024")]
    for mx, label in marks:
        parts.append(circle(mx, 470, 6, fill=BG, stroke=FIELD, sw=2))
        mb, mw, mh = textbox(mx, 508, label, size=11, pad=8, fill="#eafaf0",
                             stroke=FIELD, color=INK)
        parts.append(mb)

    render(os.path.join(OUT, 'power-regimes.svg'), W, H, *parts)


def review_break_even():
    """Карта рішення «збиратися чи ні» в осях (P(латентна вада), Δ = ціна_в_полі − ціна_зараз).
    Межа беззбитковості p* = R/(q·Δ) — гіпербола: для ЗВОРОТНИХ рішень (Δ→0) вона
    вилітає над одиницю (рев'ю не окупається за жодної p), для НЕЗВОРОТНИХ (Δ велике)
    падає майже до нуля (окупається навіть за крихітної p). Δ у лог-шкалі — бо саме
    порядок величини незворотності вирішує знак EV, а не точні числа."""
    import math
    W, H = 1000, 520
    parts = []
    left, right, top, bot = 120, 900, 95, 430

    def X(D):                         # лог-шкала Δ від 1 (10⁰) до 1000 (10³)
        return left + (math.log10(D) / 3.0) * (right - left)

    def Y(p):
        return bot - p * (bot - top)

    # межа p* = K/Δ (K=30): входить у кадр при p*=1 (Δ=30), спадає до 0.03 (Δ=1000)
    K = 30.0
    ds = [30, 45, 70, 110, 180, 300, 500, 750, 1000]
    pts = [(X(D), Y(K / D)) for D in ds]
    boundary = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % (x, y) for x, y in pts[1:])
    region = boundary + " L%.1f %.1f L%.1f %.1f Z" % (right, top, pts[0][0], top)
    parts.append('<path d="%s" fill="%s" fill-opacity="0.10" stroke="none"/>' % (region, FIELD))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (boundary, FIELD))

    # осі
    parts.append(line(left, bot, right, bot, color=MUTED, sw=1.5))
    parts.append(arrow(right - 20, bot, right + 8, bot, color=MUTED))
    parts.append(line(left, bot, left, top, color=MUTED, sw=1.5))
    parts.append(arrow(left, top + 20, left, top - 3, color=MUTED))

    # підписи осей
    parts.append(text(152, 82, "P(латентна вада)", size=12, color=INK))
    parts.append(text((left + right) / 2, 474,
                      "Δ = ціна в полі − ціна зараз   →   зростає незворотність (лог-шкала)",
                      size=12, color=INK))

    # мітки областей
    parts.append(mtext(772, 140, ["рев'ю окупається", "EV > 0"], size=14, color=FIELD, bold=True))
    parts.append(mtext(300, 172, ["дешевше пропустити", "EV < 0"], size=13, color=MUTED, bold=True))

    # приклад: зворотне рішення — мала Δ, навіть за помітної p точка під межею → пропустити
    parts.append(minus(250, 330, r=13))
    parts.append(text(250, 366, "зворотне рішення", size=12, color=NEG))
    # приклад: незворотне рішення — велика Δ, навіть за малої p точка над межею → рев'ю
    parts.append(plus(800, 360, r=13))
    parts.append(text(800, 330, "незворотне рішення", size=12, color=POS))

    render(os.path.join(OUT, 'review-break-even.svg'), W, H, *parts,
           title="Поріг беззбитковості рев'ю: чому вирішує незворотність (Δ)")


def review_marginal():
    """Гранична цінність зайвого рецензента — спадна віддача. Ліворуч ОДНАКОВІ
    рецензенти: гранична частка спійманого згасає геометрично (кожен наступний ловить
    дедалі рідше те, що попередні вже впіймали). Праворуч РІЗНІ класи (перспективи):
    кожен новий клас відкриває свіжий пласт вад, тож цінність тримається, доки не
    почнеш дублювати клас. Пунктир — поріг окупності c/(p·Δ): стовпці під ним зайві."""
    W, H = 1000, 560
    parts = []
    y_base = 470
    scale = 560.0                       # частка 0.5 → 280 px заввишки
    thr = 0.19                          # поріг окупності (для рішення середньої ставки)
    y_thr = y_base - thr * scale

    parts.append(line(500, 66, 500, 512, color=MUTED, sw=1, dash="4,5"))
    parts.append(text(262, 54, "однакові рецензенти", size=15, color=NEG, bold=True))
    parts.append(text(762, 54, "різні класи (перспективи)", size=15, color=POS, bold=True))

    def panel(cx0, step, bars, fill, edge):
        centers = [cx0 + i * step for i in range(len(bars))]
        bw = 54
        x_l = centers[0] - bw / 2 - 6
        x_r = centers[-1] + bw / 2 + 6
        parts.append(line(x_l, y_base, x_r, y_base, color=MUTED, sw=1.5))
        parts.append(line(x_l, y_thr, x_r, y_thr, color=POS, sw=1.5, dash="6,4"))
        for c, (val, lab) in zip(centers, bars):
            h = val * scale
            parts.append(rect(c - bw / 2, y_base - h, bw, h, fill=fill, stroke=edge, sw=1.5))
            parts.append(text(c, y_base - h - 8, "%.3f" % val, size=12, color=INK, bold=True))
            parts.append(text(c, y_base + 20, lab, size=11, color=MUTED))

    homog = [(0.500, "1-й"), (0.250, "2-й"), (0.125, "3-й"), (0.063, "4-й"), (0.031, "5-й")]
    panel(90, 86, homog, "#eaf0fd", NEG)
    distinct = [(0.50, "безпека"), (0.40, "експлуатація"), (0.34, "розробка"),
                (0.26, "швидкодія"), (0.07, "2-й безпеки")]
    panel(590, 86, distinct, "#eafaf0", FIELD)

    parts.append(text(262, 512, "після 2-го — під порогом: зайві", size=12, color=NEG, bold=True))
    parts.append(text(762, 512, "новий клас тримає цінність; дубль — ні", size=12, color=FIELD, bold=True))
    parts.append(text(W / 2, 540,
                      "пунктир — поріг окупності c/(p·Δ); стовпці під ним не варті свого часу",
                      size=12, color=MUTED))

    render(os.path.join(OUT, 'review-marginal.svg'), W, H, *parts,
           title="Гранична віддача рецензента: клони згасають, перспективи тримаються")


if __name__ == '__main__':
    passive_vs_active()
    review_lineage()
    finding_with_owner()
    review_spectrum()
    sensitivity_vs_tradeoff()
    view_blindspot()
    gate_vs_process()
    advice_rule()
    power_regimes()
    review_break_even()
    review_marginal()
    print("ok")
