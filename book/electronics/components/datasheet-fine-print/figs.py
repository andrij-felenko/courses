# -*- coding: utf-8 -*-
"""Фігури до теми «Дрібний шрифт даташита» та її історичної вставки (hist-pentium-fdiv).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).

Усі підписи в SVG — без номерів і без «Рис.» (нумерації в book/ немає). Імена файлів —
slug-описові (не fig-XX). Запуск:  python figs.py  → пише в ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── дрібні помічники поверх svgkit ───────────────────────────────────────────
def cell(x, y, w, h, s, size=13, fill=FILL, stroke=LINE, color=INK, bold=False):
    """Клітинка таблиці з текстом по центру."""
    return fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, color=color, bold=bold)


def callout(cx, cy, s, size=13, color=INK, fill="#fff8e1", stroke="#d4a017", bold=False):
    """Виноска-хмаринка (рамка під текст)."""
    body, w, h = textbox(cx, cy, s, size=size, color=color, fill=fill, stroke=stroke, bold=bold)
    return body


# ════════════════════════════════════════════════════════════════════════════
# СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

def fig_footnote_changes_meaning():
    """Число зі значком «(1)» — і виноска внизу, що перевертає його сенс."""
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 28, "Той самий рядок: зі значком і без нього", size=16, bold=True))

    # рядок таблиці параметра
    f.append(cell(60, 70, 330, 34, "Вихідний струм", size=13, fill="#eef1f4", bold=True))
    f.append(cell(390, 70, 270, 34, "85 мА", size=14, fill="#eef1f4", bold=True))
    # значок виноски біля числа
    f.append(text(632, 66, "(1)", size=13, color=POS, bold=True))

    # стрілка вниз до виноски
    f.append(arrow(560, 108, 560, 150, color=POS, sw=2))

    # сама виноска
    f.append(callout(W / 2, 196,
                     "(1) Імпульсне значення: 300 мкс, рідкі імпульси.\n"
                     "Тривалий струм у рази менший.",
                     size=14, color=INK))

    # дві дороги-висновки
    f.append(cell(60, 258, 290, 44,
                  "Без виноски: 85 мА = постійний\nробочий струм → прилад згорить",
                  size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(cell(370, 258, 290, 44,
                  "З виноскою: постійний струм\nзакладаємо в рази нижчий → ціло",
                  size=12, fill="#eaf7ee", stroke=FIELD, color="#1e7e45", bold=True))
    return render(os.path.join(OUT, "footnote-changes-meaning.svg"), W, H, *f)


def fig_lab_vs_your_board():
    """θJA: ідеальна лабораторна плата проти реальної — звідки беруться гірші градуси."""
    W, H = 720, 330
    f = []
    f.append(text(W / 2, 28, "θJA: лабораторний еталон проти вашої плати", size=16, bold=True))

    # ── ліворуч: лабораторна плата ──
    f.append(cell(40, 60, 300, 24, "Лабораторія (число в даташиті)", size=13,
                  fill="#eaf7ee", stroke=FIELD, color="#1e7e45", bold=True))
    f.append(rect(40, 92, 300, 150, fill="#f0faf3", stroke=FIELD, sw=1.5))
    # великий мідний полігон
    f.append(rect(60, 150, 260, 70, fill="#fbe7c6", stroke="#c8922e", sw=1.2))
    f.append(text(190, 190, "великий мідний полігон", size=12, color="#8a5a12"))
    f.append(circle(190, 130, 14, fill="#d9dee3", stroke=INK, sw=1.5))
    f.append(text(190, 116, "чип", size=11, color=MUTED))
    f.append(text(190, 234, "багатошарова плата, нерухоме повітря", size=11, color=MUTED))

    # ── праворуч: реальна плата ──
    f.append(cell(380, 60, 300, 24, "Ваша плата (реальність)", size=13,
                  fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(rect(380, 92, 300, 150, fill="#fef4f3", stroke=POS, sw=1.5))
    # крихітний майданчик
    f.append(rect(495, 150, 70, 26, fill="#fbe7c6", stroke="#c8922e", sw=1.2))
    f.append(text(530, 168, "крихітний", size=10, color="#8a5a12"))
    f.append(circle(530, 130, 14, fill="#d9dee3", stroke=INK, sw=1.5))
    # гарячі сусіди
    f.append(circle(420, 130, 11, fill="#fdd0c8", stroke=POS, sw=1.5))
    f.append(circle(640, 135, 11, fill="#fdd0c8", stroke=POS, sw=1.5))
    f.append(text(530, 200, "гарячі сусіди, тісний корпус", size=11, color=MUTED))
    f.append(text(530, 220, "тепловідведення вдвічі-втричі гірше", size=11, color=POS, bold=True))

    # підсумок-стрічка
    f.append(cell(40, 262, 640, 44,
                  "θJA у даташиті описує не вашу плату, а ідеальний еталон → реальна температура вища, бери запас",
                  size=13, fill="#fff8e1", stroke="#d4a017", bold=True))
    return render(os.path.join(OUT, "lab-vs-your-board.svg"), W, H, *f)


def fig_typ_only_trap():
    """Рядок із повними min/typ/max проти рядка, де є лише typ (порожні межі)."""
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 28, "Порожні колонки = параметр не гарантовано", size=16, bold=True))

    cols = ["Параметр", "min", "typ", "max", "од."]
    xs = [50, 320, 410, 500, 590]
    ws = [270, 90, 90, 90, 80]
    # шапка
    for c, x, w in zip(cols, xs, ws):
        f.append(cell(x, 60, w, 32, c, size=13, fill="#eef1f4", bold=True))

    # рядок 1 — нормальний параметр
    row1 = ["Напруга зсуву", "0.5", "1.2", "2.0", "мВ"]
    for v, x, w in zip(row1, xs, ws):
        f.append(cell(x, 96, w, 34, v, size=13, fill=FILL))
    f.append(text(660, 117, "✓", size=18, color=FIELD, bold=True))

    # рядок 2 — лише typ
    row2 = ["Темп. дрейф", "—", "5", "—", "мкВ/°C"]
    for i, (v, x, w) in enumerate(zip(row2, xs, ws)):
        empty = v == "—"
        f.append(cell(x, 134, w, 34, v, size=13,
                      fill="#fdecea" if empty else FILL,
                      stroke=POS if empty else LINE,
                      color=POS if empty else INK,
                      bold=empty))
    f.append(text(660, 155, "✗", size=18, color=POS, bold=True))

    f.append(callout(W / 2, 214,
                     "min і max порожні → гарантованих меж НЕМАЄ.\n"
                     "Число суто довідкове: «зазвичай буває отак».",
                     size=14, color=INK))
    f.append(cell(50, 256, 620, 30,
                  "«guaranteed by design» — ручаються без виміру (сильніше); голий «typ» — лише орієнтир",
                  size=12, fill="#f4f6f8", stroke=MUTED, color=MUTED))
    return render(os.path.join(OUT, "typ-only-trap.svg"), W, H, *f)


def fig_revision_lies():
    """Ланцюг ревізій документа: стара бреше про вже виправлене."""
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 28, "Ревізія: стара версія бреше про вже виправлене", size=16, bold=True))

    revs = [
        ("Rev A", "перший випуск", FILL, LINE, INK),
        ("Rev B", "уточнили струм спокою", FILL, LINE, INK),
        ("Rev D", "виправили розпіновку!", "#eaf7ee", FIELD, "#1e7e45"),
    ]
    x = 70
    boxw, boxh, gap = 170, 70, 35
    cxs = []
    for i, (r, note, fill, stroke, col) in enumerate(revs):
        bx = x + i * (boxw + gap)
        cxs.append(bx + boxw / 2)
        f.append(rect(bx, 80, boxw, boxh, fill=fill, stroke=stroke, sw=1.8))
        f.append(text(bx + boxw / 2, 108, r, size=15, color=col, bold=True))
        f.append(text(bx + boxw / 2, 130, note, size=11, color=MUTED))
        if i < len(revs) - 1:
            ax = bx + boxw
            f.append(arrow(ax + 4, 115, ax + gap - 4, 115, color=INK, sw=2))

    # стара ревізія = пастка
    f.append(arrow(cxs[0], 152, cxs[0], 188, color=POS, sw=2))
    f.append(cell(cxs[0] - 120, 190, 240, 50,
                  "Взяв стару Rev A → розвів плату\nза НЕПРАВИЛЬНОЮ розпіновкою",
                  size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))
    # нова ревізія = вихід
    f.append(arrow(cxs[2], 152, cxs[2], 188, color=FIELD, sw=2))
    f.append(cell(cxs[2] - 120, 190, 240, 50,
                  "Найновіша з сайту виробника +\nісторія змін → числа правильні",
                  size=12, fill="#eaf7ee", stroke=FIELD, color="#1e7e45", bold=True))

    f.append(text(W / 2, 270, "«Preliminary» / «Advance Information» — цифри ще попередні",
                  size=12, color="#8a5a12"))
    return render(os.path.join(OUT, "revision-lies.svg"), W, H, *f)


def fig_errata_silicon_bugs():
    """Errata: список вад кремнію, до кожної — обхід; рятує тижні пошуку."""
    W, H = 720, 330
    f = []
    f.append(text(W / 2, 28, "Errata: вади самого кремнію — і обхід до кожної", size=16, bold=True))

    rows = [
        ("UART губить байт при виході зі сну", "скинути регістр перед першим прийомом"),
        ("Зайвий зсув на нульовому каналі АЦП", "відняти виміряний зсув у коді"),
        ("I²C зависає при розтягуванні такту", "вимкнути clock-stretching"),
    ]
    # шапки колонок
    f.append(cell(40, 64, 360, 30, "Баг кремнію (поведінка ≠ опис)", size=13,
                  fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(cell(410, 64, 270, 30, "Обхід (workaround)", size=13,
                  fill="#eaf7ee", stroke=FIELD, color="#1e7e45", bold=True))
    y = 100
    for bug, wa in rows:
        f.append(cell(40, y, 360, 40, bug, size=12, fill="#fef4f3", stroke=POS))
        f.append(arrow(402, y + 20, 408, y + 20, color=INK, sw=1.6))
        f.append(cell(410, y, 270, 40, wa, size=12, fill="#f0faf3", stroke=FIELD))
        y += 48

    f.append(callout(W / 2, 268,
                     "«Мій код правильний, а не працює» —\n"
                     "часто це відомий errata-баг. Звіряй ДО, не ПІСЛЯ.",
                     size=14, color=INK))
    f.append(text(W / 2, 314, "errata прив'язана до ревізії кремнію (дата-код на корпусі)",
                  size=11, color=MUTED))
    return render(os.path.join(OUT, "errata-silicon-bugs.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА  hist-pentium-fdiv
# ════════════════════════════════════════════════════════════════════════════

def fig_fdiv_timeline():
    """Хроніка FDIV: від наукової нотатки до першого відкликання й $475 млн."""
    W, H = 760, 470
    f = []
    f.append(text(W / 2, 30, "Хроніка FDIV: три місяці від тихого багу до відкликання", size=16, bold=True))

    # вертикальна вісь часу
    ax = 150
    f.append(line(ax, 70, ax, 400, color=MUTED, sw=2))

    events = [
        ("літо 1994", "Intel сама знаходить ваду\nй тихо править нові партії", "#fdecea", POS),
        ("30 жовт. 1994", "Т. Найслі публічно описує\nдефект листом колегам", FILL, INK),
        ("листоп. 1994", "Тім Коу дає число, де помилка\nвидна на калькуляторі — баг стає мемом", FILL, INK),
        ("груд. 1994", "IBM спиняє відвантаження ПК →\nакції й довіра падають", "#fff8e1", "#d4a017"),
        ("20 груд. 1994", "Повна заміна «no questions asked» —\nперше відкликання процесора", "#eaf7ee", "#1e7e45"),
    ]
    y = 90
    dy = 66
    for i, (date, txt, fill, col) in enumerate(events):
        cy = y + i * dy
        f.append(circle(ax, cy, 7, fill=col, stroke=INK, sw=1.5))
        f.append(text(ax - 16, cy + 4, date, size=12, color=col, anchor="end", bold=True))
        f.append(cell(ax + 24, cy - 22, 560, 44, txt, size=12, fill=fill, stroke=col))

    # підсумкова смуга
    f.append(cell(40, 414, 680, 42,
                  "Урок галузі: складний чип завжди має відомі баги — відповідальний виробник їх ПУБЛІКУЄ ($475 млн резерв)",
                  size=13, fill="#eef1f4", stroke=INK, bold=True))
    return render(os.path.join(OUT, "fdiv-timeline.svg"), W, H, *f)


def fig_fdiv_table_holes():
    """П'ять порожніх клітинок у таблиці ділення серед тисячі правильних."""
    W, H = 760, 460
    f = []
    f.append(text(W / 2, 30, "Чому баг ховався: п'ять порожніх клітинок із 1066", size=16, bold=True))

    # ── ліворуч: сітка таблиці ──
    f.append(text(195, 64, "Таблиця SRT (схематично)", size=13, bold=True))
    gx, gy = 60, 84
    cols, rowsn = 16, 14
    cw = 17
    # позиції «дірок» — умовні (ілюстрація ідеї, не топологія)
    holes = {(3, 5), (4, 5), (7, 9), (8, 9), (9, 10)}
    for r in range(rowsn):
        for c in range(cols):
            x = gx + c * cw
            yy = gy + r * cw
            if (r, c) in holes:
                f.append(rect(x, yy, cw - 2, cw - 2, fill="#e74c3c", stroke="#a01b0c", sw=1))
            else:
                f.append(rect(x, yy, cw - 2, cw - 2, fill="#cdeccd", stroke="#7bbf7b", sw=0.6))
    f.append(text(gx + 6, gy + rowsn * cw + 22, "■", size=13, color="#27ae60", anchor="start"))
    f.append(text(gx + 20, gy + rowsn * cw + 22, "1061 зашита правильно", size=12, color=MUTED, anchor="start"))
    f.append(text(gx + 6, gy + rowsn * cw + 42, "■", size=13, color="#e74c3c", anchor="start"))
    f.append(text(gx + 20, gy + rowsn * cw + 42, "5 порожніх → повертають 0 замість +2", size=12, color=POS, anchor="start"))

    # ── праворуч: що це означало ──
    rx = 400
    f.append(text(rx + 165, 64, "Що бачив користувач", size=13, bold=True))
    f.append(cell(rx, 84, 330, 52,
                  "Майже завжди ділення влучає\nв правильну клітинку → чип рахує бездоганно",
                  size=12, fill="#eaf7ee", stroke=FIELD, color="#1e7e45"))
    f.append(cell(rx, 146, 330, 52,
                  "Зрідка операнди тягнуть до «дірки» →\nхиба вже в п'ятій значущій цифрі",
                  size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(cell(rx, 208, 330, 40,
                  "≈ раз на 9 мільярдів ділень\n(оцінка журналу Byte)",
                  size=12, fill=FILL, stroke=LINE))
    f.append(cell(rx, 256, 330, 36,
                  "Рідкісний — не означає неможливий",
                  size=13, fill="#fff8e1", stroke="#d4a017", bold=True))

    f.append(text(W / 2, 432,
                  "Розташування клітинок умовне — ілюструє ідею, а не точну топологію матриці",
                  size=11, color=MUTED))
    return render(os.path.join(OUT, "fdiv-table-holes.svg"), W, H, *f)


if __name__ == "__main__":
    paths = [
        fig_footnote_changes_meaning(),
        fig_lab_vs_your_board(),
        fig_typ_only_trap(),
        fig_revision_lies(),
        fig_errata_silicon_bugs(),
        fig_fdiv_timeline(),
        fig_fdiv_table_holes(),
    ]
    for p in paths:
        print("wrote", os.path.relpath(p, os.path.dirname(__file__)))
