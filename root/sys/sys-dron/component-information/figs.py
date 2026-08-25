# -*- coding: utf-8 -*-
"""Фігури до теми «Відомості про компонент: метадані з борту»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def box(cx, cy, s, **kw):
    """textbox + межі рамки, щоб приєднувати стрілки."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, cx - w / 2.0, cx + w / 2.0, cy - h / 2.0, cy + h / 2.0


# ── 1. Два рівні непрямості ────────────────────────────────────────────────
def fig_indirection():
    W, H = 1220, 570
    f = []

    f.append(text(215, 92, "запит: «надішли повідомлення 397»", size=12, color=MUTED))

    b, ax0, ax1, ay0, ay1 = box(215, 140, "COMPONENT_METADATA\nuri + file_crc", size=14)
    f.append(b)

    b, bx0, bx1, by0, by1 = box(215, 300, "component_general.json.xz\nна борту, MAVFTP", size=14)
    f.append(b)

    f.append(arrow(215, ay1 + 8, 215, by0 - 8))
    f.append(text(228, (ay1 + by0) / 2.0 + 4, "адреса одного файлу", size=11,
                  color=MUTED, anchor="start"))

    # панель metadataTypes
    px, py, pw, ph = 500, 110, 340, 330
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(px + pw / 2.0, py + 34, "metadataTypes", size=16, bold=True))

    rows = [("1 PARAMETER", "mftp + запасний https\n+ адреса перекладів"),
            ("4 EVENTS", "mftp + запасний https"),
            ("5 ACTUATORS", "mftp")]
    row_y = []
    for i, (head, sub) in enumerate(rows):
        ry = py + 62 + i * 88
        f.append(fitbox(px + 20, ry, pw - 40, 72, head + "\n" + sub, size=13))
        row_y.append(ry + 36)

    f.append(arrow(bx1 + 10, 300, px - 10, 300))

    # споживачі
    dst = ["Метадані фактів", "Інтерфейс подій", "Налаштування двигунів"]
    for i, s in enumerate(dst):
        b, dx0, dx1, dy0, dy1 = box(1060, row_y[i], s, size=13)
        f.append(b)
        f.append(arrow(px + pw + 10, row_y[i], dx0 - 10, row_y[i]))

    f.append(text(W / 2.0, H - 26,
                  "сто байтів повідомлення несуть одну адресу — далі адрес скільки завгодно",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'two-level-indirection.svg'), W, H, *f,
           title="Від повідомлення до описів: два рівні непрямості")


# ── 2. Сім станів запиту одного виду ───────────────────────────────────────
def fig_request_states():
    W, H = 1080, 780
    f = []

    steps = [
        ("попросити COMPONENT_METADATA", "лише для покажчика; таймаут 5 с"),
        ("старе COMPONENT_INFORMATION", "пропуск, якщо CRC уже приїхав"),
        ("завантажити файл", "спершу кеш, потім mftp або https; таймаут 30 с"),
        ("запасна адреса", "пропуск, якщо файл уже отримано"),
        ("завантажити переклади", "пропуск, якщо адреси перекладів немає"),
        ("застосувати переклад", "англійська локаль — пропуск; таймаут 15 с"),
        ("віддати JSON споживачеві", "розібрати, покласти в кеш або видалити"),
    ]

    x0, wbox = 70, 380
    for i, (name, note) in enumerate(steps):
        cy = 100 + i * 94
        f.append(fitbox(x0, cy - 28, wbox, 56, name, size=14, bold=True))
        f.append(text(x0 + wbox + 40, cy + 5, note, size=13, color=MUTED, anchor="start"))
        if i:
            f.append(arrow(x0 + wbox / 2.0, cy - 94 + 28 + 8, x0 + wbox / 2.0, cy - 28 - 8))
        if i == 1:
            f.append(text(x0 + wbox / 2.0 + 14, cy - 40, "готово · таймаут · пропуск",
                          size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2.0, H - 28,
                  "усі виходи ведуть тільки вперед: невдача не зупиняє послідовності",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'request-states.svg'), W, H, *f,
           title="Запит одного виду опису")


# ── 3. Четверо дверей опису параметра ──────────────────────────────────────
def fig_fallback():
    W, H = 1180, 570
    f = []

    doors = [
        ("Бортовий файл (mftp)", "опис збігається з прошивкою"),
        ("Запасна адреса (https)", "опис тієї самої збірки з мережі"),
        ("База плагіна прошивки", "опис версії, з якою зібрано станцію"),
        ("Порожні метадані", "тип і група з імені — і все"),
    ]
    labels = ["немає файлу на борту", "немає мережі", "немає бази"]

    x0, wbox = 90, 390
    for i, (name, result) in enumerate(doors):
        cy = 110 + i * 112
        f.append(fitbox(x0, cy - 30, wbox, 60, name, size=15, bold=True))
        f.append(fitbox(670, cy - 28, 440, 56, result, size=13,
                        fill="#eaf3ea", stroke=FIELD))
        f.append(arrow(x0 + wbox + 12, cy, 658, cy))
        if i:
            f.append(arrow(x0 + wbox / 2.0, cy - 112 + 30 + 8, x0 + wbox / 2.0, cy - 30 - 8))
            f.append(text(x0 + wbox / 2.0 + 14, cy - 60, labels[i - 1],
                          size=11, color=POS, anchor="start"))

    f.append(text(W / 2.0, H - 26,
                  "нижчі двері дають гірший опис, але жодні не дають відмови",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'metadata-fallback.svg'), W, H, *f,
           title="Звідки береться опис параметра")


# ── 4. Дві труби CRC над тими самими байтами ───────────────────────────────
def fig_crc_pipelines():
    W, H = 1140, 560
    f = []

    b, sx0, sx1, sy0, sy1 = box(135, 275, "байти файлу\nприклад: «hello world»", size=13)
    f.append(b)

    rows = [
        (165, "zlib.crc32(data)", "регістр стартує з 0xFFFFFFFF,\nнаприкінці ще один xor",
         "0x0D4A1185", "0d4a1185_00_0", "кеш ніколи не влучає", POS),
        (390, "CRC32 метаданих", "регістр стартує з нуля,\nфінального xor немає",
         "0x66CDA069", "66cda069_00_0", "збігається з file_crc", FIELD),
    ]

    for cy, head, note, num, tag, verdict, col in rows:
        f.append(fitbox(300, cy - 42, 300, 84, head + "\n" + note, size=13))
        f.append(arrow(sx1 + 10, 275, 292, cy))

        b, nx0, nx1, ny0, ny1 = box(730, cy, num, size=15, bold=True)
        f.append(b)
        f.append(arrow(608, cy, nx0 - 10, cy))

        b, tx0, tx1, ty0, ty1 = box(960, cy, tag, size=13)
        f.append(b)
        f.append(arrow(nx1 + 10, cy, tx0 - 10, cy))

        f.append(text(960, ty1 + 26, verdict, size=12, color=col))

    f.append(text(W / 2.0, H - 24,
                  "той самий поліном і та сама таблиця — різні лише два інвертування",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'crc-two-pipelines.svg'), W, H, *f,
           title="Дві труби CRC над тими самими байтами")


# ── 5. Ціна читання файлу через MAVFTP ─────────────────────────────────────
def fig_ftp_read_cost():
    W, H = 1180, 470
    f = []

    x0, xmax, tmax = 150, 1000, 80.0          # вісь: 0…80 с
    px = (xmax - x0) / tmax

    def tx(t):
        return x0 + t * px

    # поріг обриву
    f.append(line(tx(40), 105, tx(40), 355, color=POS, sw=2, dash="7,5"))
    f.append(text(tx(40), 92, "поріг обриву: прогноз > 40 с", size=12, color=POS))

    bars = [
        (150, "ReadFile по одному: 252 обміни × 250 мс", 63.0,
         "63 с — обрив, далі uriFallback", POS, "#fdecea"),
        (270, "BurstReadFile: одна відповідь за одною, межа — смуга каналу", 25.0,
         "25 с — доходить", FIELD, "#eaf3ea"),
    ]

    for ylab, label, secs, verdict, col, fillc in bars:
        f.append(text(x0, ylab, label, size=13, anchor="start"))
        f.append(rect(x0, ylab + 15, tx(secs) - x0, 40, fill=fillc, stroke=col, sw=2))
        f.append(text(tx(secs) + 14, ylab + 41, verdict, size=12,
                      color=col, anchor="start"))

    # вісь часу
    f.append(line(x0, 380, xmax + 40, 380, color=INK, sw=2))
    for t in (0, 20, 40, 60, 80):
        f.append(line(tx(t), 380, tx(t), 390, color=INK, sw=1.5))
        f.append(text(tx(t), 410, "%d с" % t, size=12, color=MUTED))

    f.append(text(W / 2.0, H - 22,
                  "файл 60 КБ, смуга під передачу 2400 Б/с, обмін «туди-назад» 250 мс",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'mavftp-read-cost.svg'), W, H, *f,
           title="Ціна читання файлу через MAVFTP")


if __name__ == '__main__':
    fig_indirection()
    fig_request_states()
    fig_fallback()
    fig_crc_pipelines()
    fig_ftp_read_cost()
    print("ok")
