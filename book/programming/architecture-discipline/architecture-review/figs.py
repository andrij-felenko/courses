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


if __name__ == '__main__':
    passive_vs_active()
    review_lineage()
    finding_with_owner()
    print("ok")
