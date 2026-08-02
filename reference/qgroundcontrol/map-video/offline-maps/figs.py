# -*- coding: utf-8 -*-
"""Фігури до теми «Офлайн-карти й кеш тайлів» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
GREENF = "#e8f6ee"
BLUEF = "#e9eefb"
GREYF = "#f0f2f4"


# ─────────────────────── 1. Схема сховища тайлів ────────────────────────────
def fig_schema():
    W, H = 1260, 830
    f = []

    # --- смуга таблиць ---
    f.append(fitbox(40, 70, 330, 200,
                    "TileSets — замовлення\n"
                    "setID · name · defaultSet\n"
                    "topleftLat/Lon\n"
                    "bottomRightLat/Lon\n"
                    "minZoom · maxZoom · type\n"
                    "numTiles · date",
                    size=14, fill=GREENF))

    f.append(fitbox(465, 110, 330, 120,
                    "SetTiles — зв'язок\n"
                    "setID · tileID\n"
                    "багато до багатьох",
                    size=14, fill=SOFT))

    f.append(fitbox(890, 70, 330, 200,
                    "Tiles — самі клітинки\n"
                    "tileID · hash UNIQUE\n"
                    "format · tile BLOB\n"
                    "size · type · date",
                    size=14, fill=BLUEF))

    f.append(fitbox(40, 330, 330, 130,
                    "TilesDownload — черга\n"
                    "setID · hash · type\n"
                    "x · y · z · state",
                    size=14, fill=GREYF))

    # зв'язки
    f.append(arrow(462, 170, 378, 170))
    f.append(text(420, 156, "setID", size=12, color=MUTED))
    f.append(arrow(798, 170, 882, 170))
    f.append(text(840, 156, "tileID", size=12, color=MUTED))
    f.append(arrow(205, 327, 205, 278))
    f.append(text(222, 308, "setID", size=12, color=MUTED, anchor="start"))

    f.append(mtext(465, 350, ["видалення набору прибирає рядки SetTiles",
                              "(ON DELETE CASCADE), але не рядки Tiles"],
                   size=13, color=MUTED, anchor="start"))

    # --- смуга ілюстрації перекриття ---
    f.append(line(40, 520, 1220, 520, color="#c8d2dc", sw=1.2))

    f.append(mtext(40, 570, ["Два набори на сусідні райони",
                             "перекриваються по смузі.",
                             "",
                             "Клітинка зі смуги лежить",
                             "у базі один раз, а рядків",
                             "у SetTiles на неї — два."],
                   size=14, anchor="start"))

    gx, gy, cell, cols, rows = 590, 610, 44, 10, 3
    for c in range(cols):
        for r in range(rows):
            fill = "#fdf3d8" if c in (4, 5) else SOFT
            f.append(rect(gx + c * cell, gy + r * cell, cell, cell,
                          fill=fill, stroke="#c8d2dc", sw=1.0, rx=2))

    f.append(rect(gx - 7, gy - 7, 6 * cell + 14, rows * cell + 14,
                  fill="none", stroke=FIELD, sw=2.4, rx=6))
    f.append(rect(gx + 4 * cell + 7, gy + 7, 6 * cell - 14, rows * cell - 14,
                  fill="none", stroke=NEG, sw=2.4, rx=6))

    f.append(text(gx + 3 * cell, gy - 22, "набір «Аеродром»", size=13, color=FIELD, bold=True))
    f.append(text(gx + 7 * cell, gy + rows * cell + 34, "набір «Траса»", size=13, color=NEG, bold=True))
    f.append(text(gx + 5 * cell, gy + rows * cell + 66, "жовте — спільні клітинки", size=13, color=MUTED))

    return render(os.path.join(OUT, 'schema.svg'), W, H, *f,
                  title="Сховище тайлів: чотири таблиці й зв'язок «багато до багатьох»")


# ─────────────────────── 2. Три поверхи пошуку тайла ────────────────────────
def fig_lookup():
    W, H = 1240, 700
    f = []
    cx = 340

    f.append(fitbox(150, 66, 380, 74, "рушій карти Qt\nдай клітинку z / x / y", size=14, fill=SOFT))
    f.append(fitbox(150, 196, 380, 74, "кеш у пам'яті\nстеля 128 МБ · 16 МБ на мобільному", size=13, fill=SOFT))
    f.append(fitbox(150, 336, 380, 74, "база qgcMapCache.db\nSELECT ... WHERE hash = ?", size=13, fill=SOFT))
    f.append(fitbox(150, 486, 380, 74, "мережа: GET у провайдера\nUser-Agent · Referer", size=13, fill=SOFT))

    f.append(arrow(cx, 142, cx, 192))
    f.append(arrow(cx, 272, cx, 332))
    f.append(arrow(cx, 412, cx, 482))
    f.append(text(356, 172, "промах", size=12, color=MUTED, anchor="start"))
    f.append(text(356, 306, "промах", size=12, color=MUTED, anchor="start"))
    f.append(text(356, 452, "промах", size=12, color=MUTED, anchor="start"))

    # межа ниток
    f.append(line(40, 300, 1200, 300, color=MUTED, sw=1.2, dash="7,6"))
    f.append(text(1200, 292, "межа ниток", size=12, color=MUTED, anchor="end"))

    # анотації праворуч
    f.append(mtext(700, 214, ["влучання коштує наносекунди,",
                              "нічого не блокує"], size=13, color=INK, anchor="start"))
    f.append(mtext(700, 354, ["влучання — єдине, що працює в полі;",
                              "запит іде в окремій нитці з власним",
                              "циклом і чергою задач"], size=13, color=INK, anchor="start"))
    f.append(mtext(700, 504, ["єдиний поверх, якому потрібен",
                              "інтернет"], size=13, color=INK, anchor="start"))

    # зворотний запис
    f.append(line(530, 523, 620, 523, color=LINE, sw=1.6))
    f.append(arrow(620, 523, 620, 377))
    f.append(line(620, 377, 534, 377, color=LINE, sw=1.6))
    f.append(mtext(640, 620, ["cacheTile(): байти лягають у базу",
                              "й стають частиною типового набору"],
                   size=13, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, 'lookup.svg'), W, H, *f,
                  title="Три поверхи пошуку тайла")


# ─────────────────────── 3. Що можна витісняти ──────────────────────────────
def fig_prune():
    W, H = 1120, 620
    f = []
    x0, x1 = 80, 1020
    total_mb = 2720.0
    k = (x1 - x0) / total_mb
    xe = x0 + 320 * k          # межа типового набору
    xl = x0 + 1024 * k         # стеля кеша

    # стеля
    f.append(line(xl, 150, xl, 500, color=POS, sw=2.0, dash="8,6"))
    f.append(text(xl, 138, "стеля кеша 1024 МБ", size=13, color=POS, bold=True))

    # бар 1
    f.append(text(x0, 186, "до очищення", size=14, bold=True, anchor="start"))
    f.append(rect(x0, 200, xe - x0, 76, fill=GREYF, stroke=LINE, sw=1.5, rx=4))
    f.append(rect(xe, 200, x1 - xe, 76, fill=GREENF, stroke=FIELD, sw=2.0, rx=4))

    f.append(mtext(x0, 306, ["типовий набір, 320 МБ —", "єдине, що можна викинути"],
                   size=13, color=MUTED, anchor="start"))
    f.append(mtext(x1, 306, ["іменовані набори, 2400 МБ —", "обіцяно, недоторканне"],
                   size=13, color=FIELD, anchor="end"))

    # бар 2
    xp = x0 + 2400 * k
    f.append(text(x0, 416, "після очищення", size=14, bold=True, anchor="start"))
    f.append(rect(x0, 430, xp - x0, 76, fill=GREENF, stroke=FIELD, sw=2.0, rx=4))

    f.append(mtext(x1, 546, ["база лишилася понад стелею,",
                             "бо викидати більше нема чого"],
                   size=13, color=MUTED, anchor="end"))

    return render(os.path.join(OUT, 'prune.svg'), W, H, *f,
                  title="Стеля кеша обмежує тільки те, що застосунок має право забути")


# ─────────────────────── 4. Анатомія ключа тайла ────────────────────────────
def fig_hash():
    W, H = 1200, 470
    f = []
    x0, total_w = 60, 1080
    per = total_w / 29.0

    segs = [(10, "0000000007", GREENF, FIELD, "10 цифр",
             "type — код провайдера: getMapId(), нумерація з 1 у порядку реєстрації"),
            (8, "00019162", BLUEF, NEG, "8 цифр",
             "x — номер клітинки по горизонталі"),
            (8, "00011049", "#fdeceb", POS, "8 цифр",
             "y — номер клітинки по вертикалі"),
            (3, "015", GREYF, MUTED, "3 цифри",
             "z — рівень масштабу, 0…23")]

    f.append(text(600, 70, "Bing Satellite (код 7) · z = 15 · x = 19162 · y = 11049",
                  size=15, bold=True))

    x = x0
    for n, digits, fill, stroke, cnt, _ in segs:
        w = per * n
        f.append(rect(x, 100, w, 68, fill=fill, stroke=stroke, sw=2.0, rx=5))
        f.append(text(x + w / 2, 142, digits, size=22, bold=True))
        f.append(text(x + w / 2, 196, cnt, size=13, color=MUTED))
        x += w

    ly = 250
    for n, digits, fill, stroke, cnt, label in segs:
        f.append(rect(60, ly - 12, 15, 15, fill=fill, stroke=stroke, sw=1.6, rx=2))
        f.append(text(88, ly, label, size=14, anchor="start"))
        ly += 32

    f.append(fitbox(60, 386, 1080, 52,
                    'QString::asprintf("%010d%08d%08d%03d", '
                    'hashFromProviderType(type), x, y, z)',
                    size=15, fill=SOFT))

    return render(os.path.join(OUT, 'hash-key.svg'), W, H, *f,
                  title="Двадцять дев'ять цифр ключа тайла")


# ──────────── 5. Складання .qgctiledb скриптом: кроки й пастки ──────────────
def fig_seed():
    W, H = 1320, 730
    f = []
    lx, lw = 60, 440          # смуга кроків
    rx_, rw = 560, 700        # смуга приміток
    bh, step = 64, 86
    y0 = 76

    stages = [
        "1 · прямокутник і рівні\n→ перелік клітинок z / x / y",
        "2 · качалка: рівний темп,\nодне з'єднання на робітника",
        "3 · відсів: заглушки\nй не-картинки — за борт",
        "4 · Tiles: hash, format, tile,\nsize, type, date",
        "5 · SetTiles: (setID, tileID)\nна КОЖЕН тайл",
        "6 · TileSets: numTiles =\nфактична кількість",
        "7 · PRAGMA user_version = 1\n→ файл .qgctiledb",
    ]

    notes = [
        (False, "широту затискаємо на ±85.0511°: далі tan(90°) вибухає,\n"
                "а клітинок за цією межею просто немає"),
        (False, "тисячі запитів з однієї адреси — саме те, що забороняють\n"
                "умови більшості тайлових служб"),
        (False, "«немає знімка» приходить із кодом 200; ловимо за\n"
                "повторюваністю тіла, а не за статусом відповіді"),
        (True,  "код провайдера з чужої збірки — рядок у базі є,\n"
                "але станція питає інший ключ: тайла ніби немає"),
        (True,  "без цього рядка злиття не перенесе тайл узагалі:\n"
                "імпорт іде наборами, а не таблицею Tiles"),
        (False, "не оновив — набір приїде з нулем у лічильнику\n"
                "й виглядатиме порожнім"),
        (True,  "інший номер схеми — станція скине ВЕСЬ кеш\n"
                "при першому ж запуску"),
    ]

    for i, (label, (trap, note)) in enumerate(zip(stages, notes)):
        y = y0 + i * step
        f.append(fitbox(lx, y, lw, bh, label, size=14, fill=BLUEF, stroke=NEG, sw=1.8))
        if trap:
            f.append(fitbox(rx_, y, rw, bh, note, size=13,
                            fill="#fdeceb", stroke=POS, sw=1.8))
            f.append(text(rx_ - 18, y + bh / 2 + 5, "!", size=20, color=POS, bold=True))
        else:
            f.append(fitbox(rx_, y, rw, bh, note, size=13,
                            fill=SOFT, stroke="#c8d2dc", sw=1.4))
        if i < len(stages) - 1:
            f.append(arrow(lx + lw / 2, y + bh + 3, lx + lw / 2, y + step - 4))

    return render(os.path.join(OUT, 'seed-pipeline.svg'), W, H, *f,
                  title="Сім кроків складання набору й три місця, де він тихо ламається")


if __name__ == '__main__':
    print(fig_schema())
    print(fig_lookup())
    print(fig_prune())
    print(fig_hash())
    print(fig_seed())
