# -*- coding: utf-8 -*-
"""Фігури до статті «i18n як архітектура (не переклад)». Запуск із теки теми: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
BLUE_FILL  = "#eaf0fd"
PINK_FILL  = "#fdecea"
AMBER_FILL = "#fff7e6"
GREY_FILL  = "#eef0f2"


def fig_boundary():
    """Ядро без локалі → межа локалі → локалізований вивід."""
    W, H = 900, 316
    F = []

    # локаль, що входить згори в межу
    F.append(text(485, 66, "локаль із запиту (Accept-Language)", size=13,
                  color=MUTED, italic=True))
    F.append(arrow(485, 74, 485, 120, color=FIELD, sw=2.2))

    # ── ядро без локалі (ліворуч)
    F.append(text(185, 132, "ядро без локалі", size=15, bold=True))
    core, cw, ch = textbox(185, 200, "бізнес-логіка · ключі\nсирі: число, мить, сума",
                           size=14, min_w=250, pad=16)
    F.append(core)

    # ── межа локалі (посередині, виділена)
    bx, by, bw, bh = 360, 120, 250, 158
    F.append(rect(bx, by, bw, bh, fill=GREEN_FILL, stroke=FIELD, sw=2.2))
    F.append(text(bx + bw / 2, by + 32, "межа локалі", size=15, bold=True))
    F.append(mtext(bx + bw / 2, by + 66,
                   ["каталог повідомлень", "правила множини (CLDR)",
                    "формати дат · чисел · валют"], size=13, lh=1.55))

    # стрілка ядро → межа
    F.append(arrow(185 + cw / 2, 200, bx, 200, color=LINE, sw=1.8))

    # ── локалізований вивід (праворуч, три канали)
    F.append(text(765, 132, "локалізований вивід", size=14, bold=True))
    outs = [("веб-сторінка", 158), ("лист · сповіщення", 208), ("PDF-квитанція", 258)]
    ox, ow = 660, 210
    for label, cy in outs:
        F.append(fitbox(ox, cy - 20, ow, 40, label, size=13, fill=FILL))
        F.append(arrow(bx + bw, 199, ox, cy, color=LINE, sw=1.6))

    return render(os.path.join(IMG, "boundary.svg"), W, H, *F,
                  title="Локаль входить на межі — ядро її не знає")


def fig_plurals():
    """Та сама вісь кількості ділиться на різну кількість форм у різних мовах."""
    W, H = 900, 322
    F = []

    LX = 148           # права межа підписів мов
    SX = 168           # старт смуг
    SW = 720           # повна ширина смуги
    BH = 44            # висота рядка
    rows_y = [72, 132, 192, 252]

    def band(y, segments):
        """segments: список (частка_ширини, текст, колір) — сумарна частка = 1."""
        x = SX
        for frac, txt, fill in segments:
            w = SW * frac
            F.append(fitbox(x, y, w, BH, txt, size=13, fill=fill, pad=7))
            x += w

    # підписи мов + кількість форм
    langs = [
        ("японська", "1 форма"),
        ("англійська", "2 форми"),
        ("українська", "3 форми"),
        ("арабська", "до 6 форм"),
    ]
    for (name, forms), y in zip(langs, rows_y):
        cy = y + BH / 2
        F.append(text(LX, cy - 4, name, size=14, anchor="end", bold=True))
        F.append(text(LX, cy + 14, forms, size=11, anchor="end", color=MUTED))

    # японська — одна форма на будь-яке число
    band(rows_y[0], [(1.0, "будь-яке число  →  один вид слова", GREY_FILL)])
    # англійська — дві
    band(rows_y[1], [(0.5, "n = 1  →  file", GREEN_FILL),
                     (0.5, "n ≠ 1  →  files", BLUE_FILL)])
    # українська — три
    band(rows_y[2], [(1/3, "1, 21, 31…  →  файл", GREEN_FILL),
                     (1/3, "2, 3, 4…  →  файли", BLUE_FILL),
                     (1/3, "0, 5…20…  →  файлів", PINK_FILL)])
    # арабська — до шести
    six = [GREEN_FILL, BLUE_FILL, PINK_FILL, AMBER_FILL, GREY_FILL, "#f0e6fa"]
    band(rows_y[3], [(1/6, str(i + 1), six[i]) for i in range(6)])

    return render(os.path.join(IMG, "plurals.svg"), W, H, *F,
                  title="Скільки форм множини — залежить від мови")


def fig_hist_timeline():
    """Дві лінії історії: коли з'явилося скорочення й коли — самі каталоги."""
    W, H = 880, 506
    F = []

    # ── легенда двох ліній
    F.append(rect(140, 34, 16, 16, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=3))
    F.append(text(166, 47, "слово: як з'явилося скорочення", size=13,
                  anchor="start", color=MUTED))
    F.append(rect(420, 34, 16, 16, fill=BLUE_FILL, stroke=NEG, sw=1.6, rx=3))
    F.append(text(446, 47, "механізм: як з'явилися каталоги", size=13,
                  anchor="start", color=MUTED))

    rows = [
        ("1984", "Ресурси Макінтоша: рядки й меню виносять із коду у файл, який редагує перекладач", BLUE_FILL),
        ("1985", "У Digital Equipment уже вживають «i18n» — за спогадами учасників", GREEN_FILL),
        ("1988–89", "Дві пропозиції для Юнікса: gettext (Uniforum) і catgets (X/Open)", BLUE_FILL),
        ("1992", "Скорочення вперше трапляється в друкованій книжці", GREEN_FILL),
        ("1995", "GNU gettext 0.7 і Translation Project: переклад стає файлом .po", BLUE_FILL),
        ("2001", "gettext 0.10.36: ngettext і Plural-Forms — граматика стає даними", BLUE_FILL),
        ("2003", "CLDR 1.0: правила локалей стають спільним версійованим сховищем", BLUE_FILL),
    ]

    y, RH = 76, 58
    for year, label, fill in rows:
        cy = y + RH / 2
        F.append(text(118, cy + 5, year, size=14, anchor="end", bold=True))
        F.append(fitbox(140, y + 7, 720, 44, label, size=13, fill=fill,
                        stroke=(FIELD if fill == GREEN_FILL else NEG), sw=1.6))
        y += RH

    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *F,
                  title="Слово й механізм: дві лінії однієї історії")


def fig_format_pipeline():
    """Шаблон → дерево → вибір гілки за правилами локалі → готовий рядок."""
    W, H = 940, 430
    F = []

    PATTERN = ("Об'єднати {count, plural, one {# файл} few {# файли} "
               "many {# файлів} other {# файлу}}?")

    # ── шаблон із каталогу
    F.append(text(470, 58, "шаблон із каталогу · локаль uk", size=13,
                  color=MUTED, italic=True))
    F.append(fitbox(40, 68, 860, 44, PATTERN, size=13, fill=FILL))

    F.append(arrow(470, 112, 470, 148, color=LINE, sw=1.8))
    F.append(text(492, 136, "розбір — раз на ключ, дерево лягає в кеш",
                  size=12, color=MUTED, anchor="start", italic=True))

    # ── дерево: текст · вибір · текст
    F.append(fitbox(40, 158, 200, 48, "текст\n«Об'єднати »", size=12, fill=FILL))
    F.append(fitbox(260, 158, 420, 48, "вибір форми · аргумент count",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2.2, bold=True))
    F.append(fitbox(700, 158, 200, 48, "текст\n«?»", size=12, fill=FILL))

    # ── шина до гілок
    boxes = [(40, "one", "# файл", BLUE_FILL, LINE, 1.5),
             (259, "few", "# файли", GREEN_FILL, FIELD, 2.2),
             (478, "many", "# файлів", BLUE_FILL, LINE, 1.5),
             (697, "other", "# файлу", BLUE_FILL, LINE, 1.5)]
    BW = 203
    F.append(line(470, 206, 470, 236, color=LINE, sw=1.6))
    F.append(line(boxes[0][0] + BW / 2, 236, boxes[-1][0] + BW / 2, 236,
                  color=LINE, sw=1.6))
    for bx, label, content, fill, stroke, sw in boxes:
        cx = bx + BW / 2
        F.append(line(cx, 236, cx, 268, color=LINE, sw=1.6))
        F.append(fitbox(bx, 268, BW, 52, label + "\n" + content, size=13,
                        fill=fill, stroke=stroke, sw=sw))

    # ── нижній ряд: аргументи → правила локалі → готовий рядок
    F.append(fitbox(40, 344, 240, 56, "аргументи\ncount = 3 · локаль uk",
                    size=12, fill=FILL))
    F.append(arrow(282, 372, 324, 372, color=LINE, sw=1.8))
    F.append(fitbox(330, 344, 250, 56, "правила локалі\n3 → few",
                    size=13, fill=AMBER_FILL))
    F.append(arrow(582, 372, 624, 372, color=LINE, sw=1.8))
    F.append(fitbox(630, 344, 270, 56, "«Об'єднати 3 файли?»",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=2.2))

    # пунктирна вказівка від правил до обраної гілки
    F.append(line(360, 344, 360, 332, color=FIELD, sw=1.8, dash="4 4"))
    F.append(arrow(360, 334, 360, 324, color=FIELD, sw=1.8))

    return render(os.path.join(IMG, "format-pipeline.svg"), W, H, *F,
                  title="Форму обирають правила локалі, а не код")


def fig_resource_compilation():
    """Компіляція ресурсів інтернаціоналізації: від джерел до двійкового блобу у Flash."""
    W, H = 960, 470
    F = []

    # ── 1. Вхідні джерела (ліворуч)
    F.append(text(140, 42, "Вихідні текстові джерела", size=14, bold=True))
    F.append(fitbox(20, 60, 240, 78, "Каталоги перекладів\n(.po / .json / ICU .txt)\nmsgid / msgstr · контексти", size=12, fill=FILL))
    F.append(fitbox(20, 154, 240, 78, "Дані локалей CLDR\n(XML / JSON cldr-core)\nправила множини · формати", size=12, fill=FILL))
    F.append(fitbox(20, 248, 240, 78, "Конфігурація збірки\n(список цільових мов,\nобмеження Flash / RAM)", size=12, fill=FILL))

    # ── 2. Офлайн-компілятор (посередині)
    cx, cy, cw, ch = 310, 60, 290, 266
    F.append(rect(cx, cy, cw, ch, fill=AMBER_FILL, stroke=FIELD, sw=2.0))
    F.append(text(cx + cw / 2, cy + 28, "Офлайн-пакувальник ресурсів", size=14, bold=True))
    F.append(text(cx + cw / 2, cy + 46, "(i18n-compiler / msgfmt)", size=11, color=MUTED, italic=True))

    steps = [
        "1. Перевірка плейсхолдерів {0}, {name}",
        "2. Хешування ключів (MurmurHash3 / FNV-1a)",
        "3. Компіляція множин у байткод VM",
        "4. Дедуплікація однакових рядків UTF-8",
        "5. Вирівнювання адрес під 4-байтне XIP"
    ]
    sy = cy + 64
    for st in steps:
        F.append(fitbox(cx + 12, sy, cw - 24, 32, st, size=11, fill=BG, stroke=MUTED, sw=1.0))
        sy += 38

    # Стрілки від джерел до компілятора
    F.append(arrow(260, 99, 310, 99, color=LINE, sw=1.6))
    F.append(arrow(260, 193, 310, 193, color=LINE, sw=1.6))
    F.append(arrow(260, 287, 310, 287, color=LINE, sw=1.6))

    # ── 3. Двійковий блоб у Flash (праворуч)
    bx, by, bw, bh = 650, 60, 290, 266
    F.append(rect(bx, by, bw, bh, fill=BLUE_FILL, stroke=NEG, sw=2.0))
    F.append(text(bx + bw / 2, by + 28, "Двійковий образ у Flash (.bin / .mo)", size=14, bold=True))

    blob_sections = [
        ("Заголовок (Magic: 0x4931384E, версія, зміщення)", GREEN_FILL),
        ("Таблиця локалей (ID, прапорці, оффсети множин)", BG),
        ("Хеш-індекс ключів (відсортовані хеші → оффсети)", BG),
        ("Пул байткоду правил множини (CLDR bytecode)", BG),
        ("Пул рядків UTF-8 (вирівняні null-terminated)", GREEN_FILL)
    ]
    bly = by + 44
    for bname, bfill in blob_sections:
        F.append(fitbox(bx + 12, bly, bw - 24, 36, bname, size=11, fill=bfill, stroke=NEG, sw=1.2))
        bly += 42

    # Стрілка від компілятора до образу
    F.append(arrow(cx + cw, 193, bx, 193, color=LINE, sw=2.0))

    # ── Нижня зона: виконання під час роботи (Runtime Zero-RAM Copy)
    rx, ry, rw, rh = 20, 360, 920, 85
    F.append(rect(rx, ry, rw, rh, fill=GREEN_FILL, stroke=FIELD, sw=2.2))
    F.append(text(rx + 24, ry + 28, "Виконання у вбудованій системі (XIP / Zero-RAM Copy)", size=14, anchor="start", bold=True))
    F.append(mtext(rx + 24, ry + 52, [
        "• Образ відображається безпосередньо в адресний простір мікроконтролера (Memory Mapped Flash / ROM).",
        "• Пошук рядка за хешем виконується бінарним пошуком O(log N) прямо у Flash без виділення купи (heap: 0 B).",
        "• Форматувальник підставляє аргументи у статичний буфер на стеку — нуль динамічних алокацій."
    ], size=11, color=INK, anchor="start", lh=1.4))

    # Стрілка від Flash образу до Runtime
    F.append(arrow(bx + bw / 2, by + bh, bx + bw / 2, ry, color=FIELD, sw=2.2))

    return render(os.path.join(IMG, "i18n-resource-compilation.svg"), W, H, *F,
                  title="Компіляція ресурсів інтернаціоналізації для Flash")


def fig_font_atlas():
    """Розкладка шрифтового атласу та дескрипторів символів у Flash і RAM."""
    W, H = 960, 460
    F = []

    # ── Лівий блок: Структура шрифту у Flash (ROM)
    fx, fy, fw, fh = 20, 40, 440, 390
    F.append(rect(fx, fy, fw, fh, fill=FILL, stroke=LINE, sw=1.8))
    F.append(text(fx + fw / 2, fy + 26, "Шрифтовий ресурс у Flash пам'яті (ROM)", size=14, bold=True))

    sections = [
        (fy + 44, 52, "Заголовок шрифту (Font Header)\nMagic · Ascent · Descent · LineGap · BPP (1/2/4/8) · GlyphCount", BLUE_FILL),
        (fy + 104, 56, "Таблиця індексу кодових точок (Codepoint Map)\nUnicode Range / Sorted Codepoint Array → Glyph Index", GREEN_FILL),
        (fy + 168, 70, "Таблиця дескрипторів гліфів (Glyph Metrics Table)\nstruct { uint8_t w, h; int8_t off_x, off_y, adv_x; uint32_t bmp_off; }\nЗсуви, розміри бітмапу та крок курсора (Advance X)", AMBER_FILL),
        (fy + 246, 70, "Таблиця парного кернінгу (Kerning Pairs Table)\nstruct { uint16_t left, right; int8_t adjust_x; }\nОпціональні поправки між парами символів (напр. 'AV', 'To')", BG),
        (fy + 324, 54, "Пул растрових бітмапів / SDF атлас (Bitmap Stream)\nЩільно упаковані біти 1-bpp (монохром) або 4/8-bpp (згладжування)", GREEN_FILL)
    ]

    for sy, sh, label, fill in sections:
        F.append(fitbox(fx + 12, sy, fw - 24, sh, label, size=11, fill=fill, stroke=LINE, sw=1.2))

    # ── Правий блок: Геометрія гліфа та рендеринг у фреймбуфер
    rx, ry, rw, rh = 500, 40, 440, 390
    F.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.8))
    F.append(text(rx + rw / 2, ry + 26, "Геометрія гліфа та відмалювання в Display RAM", size=14, bold=True))

    # Схема метрик гліфа
    mx, my, mw, mh = rx + 30, ry + 50, 380, 200
    F.append(rect(mx, my, mw, mh, fill=BG, stroke=MUTED, sw=1.0, rx=4))

    # Базова лінія та допоміжні лінії
    base_y = my + 130
    ascent_y = my + 35
    descent_y = my + 175
    F.append(line(mx + 20, base_y, mx + mw - 20, base_y, color=NEG, sw=1.8, dash="4 3"))
    F.append(text(mx + mw - 15, base_y + 4, "Baseline", size=10, color=NEG, anchor="start", italic=True))

    F.append(line(mx + 20, ascent_y, mx + mw - 20, ascent_y, color=MUTED, sw=1.2, dash="3 3"))
    F.append(text(mx + mw - 15, ascent_y + 4, "Ascent", size=10, color=MUTED, anchor="start", italic=True))

    F.append(line(mx + 20, descent_y, mx + mw - 20, descent_y, color=MUTED, sw=1.2, dash="3 3"))
    F.append(text(mx + mw - 15, descent_y + 4, "Descent", size=10, color=MUTED, anchor="start", italic=True))

    # Рамка самого гліфа (Bounding Box)
    gx, gy, gw, gh = mx + 90, ascent_y + 20, 110, 105
    F.append(rect(gx, gy, gw, gh, fill=BLUE_FILL, stroke=FIELD, sw=2.0))
    F.append(text(gx + gw / 2, gy + gh / 2 + 16, "A", size=64, color=INK, bold=True))

    # Позначення метрик
    # Bearing X (відступ зліва)
    F.append(line(mx + 50, my + 20, mx + 50, descent_y + 10, color=POS, sw=1.5))
    F.append(arrow(mx + 50, gy + 30, gx, gy + 30, color=POS, sw=1.5))
    F.append(text(mx + 70, gy + 22, "Bearing X", size=10, color=POS))

    # Advance X
    adv_x = mx + 240
    F.append(line(adv_x, my + 20, adv_x, descent_y + 10, color=POS, sw=1.5))
    F.append(arrow(mx + 50, my + 20, adv_x, my + 20, color=POS, sw=1.5))
    F.append(text((mx + 50 + adv_x) / 2, my + 14, "Advance Width (крок курсора)", size=11, color=POS, bold=True))

    # Опис взаємодії
    F.append(fitbox(rx + 12, ry + 265, rw - 24, 110,
                    "Алгоритм виводу рядка (Display Blit Pipeline):\n"
                    "1. Декодування UTF-8 кодової точки → бінарний пошук у Codepoint Map.\n"
                    "2. Зчитування дескриптора з Flash (w, h, off_x, off_y, adv_x).\n"
                    "3. Попіксельне накладання бітів з Flash Bitmap Stream у Framebuffer.\n"
                    "4. Зсув курсора: cursor_x += (adv_x + kerning_adjust).",
                    size=11, fill=AMBER_FILL, stroke=FIELD, sw=1.5))

    # Стрілка між Flash дескриптором і рендером
    F.append(arrow(fx + fw, fy + 200, rx, ry + 150, color=FIELD, sw=2.2))

    return render(os.path.join(IMG, "font-atlas-memory-layout.svg"), W, H, *F,
                  title="Розкладка шрифтового атласу та метрик у Flash")


if __name__ == "__main__":
    p1 = fig_boundary()
    p2 = fig_plurals()
    p3 = fig_hist_timeline()
    p4 = fig_format_pipeline()
    p5 = fig_resource_compilation()
    p6 = fig_font_atlas()
    print("written:", p1)
    print("written:", p2)
    print("written:", p3)
    print("written:", p4)
    print("written:", p5)
    print("written:", p6)

