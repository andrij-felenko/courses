# -*- coding: utf-8 -*-
"""Фігури до теми «Бортові логи апарата: завантаження й потокове передавання»
довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
WARM = "#fdf3e7"
COLD = "#eaf0fd"
GOOD = "#eaf7ef"
LOST = "#fdecea"


# ───────────── 1. Три дороги з бортової карти на землю ─────────────
def fig_three_roads():
    W, H = 1320, 720
    f = []
    f.append(text(W / 2, 36, "Той самий файл, три способи дістати його з борту", size=17, bold=True))

    # апарат
    f.append(rect(40, 70, 290, 580, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(185, 100, "апарат", size=13, color=MUTED))
    f.append(fitbox(62, 120, 246, 74, "логер прошивки\nпише під час польоту", size=13, fill=SOFT))
    f.append(fitbox(62, 214, 246, 96, "SD-карта\n09_31_14.ulg\n18.4 МБ", size=13, fill=GOOD, bold=True))
    f.append(fitbox(62, 330, 246, 74, "стек MAVLink\nвіддає по кадру", size=13, fill=SOFT))

    # станція
    f.append(rect(990, 70, 290, 580, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(1135, 100, "наземна станція", size=13, color=MUTED))
    f.append(fitbox(1012, 120, 246, 74, "перелік записів\nна екрані «Аналіз»", size=13, fill=SOFT))
    f.append(fitbox(1012, 214, 246, 96, "файл на диску\nlog_7_2026-8-2-\n09-31-14.ulg", size=13, fill=GOOD, bold=True))
    f.append(fitbox(1012, 330, 246, 74, "жодного байта\nне тлумачить", size=13, fill=SOFT))

    lanes = [
        (170, "LOG_REQUEST_DATA  →  LOG_DATA",
              "90 Б корисних у 109-байтовому кадрі",
              "після польоту; тягне станція", COLD),
        (330, "MAVFTP: перелік каталогу, читання за шляхом",
              "вікно з кількох запитів у польоті",
              "після польоту; тягне станція", COLD),
        (490, "MAV_CMD_LOGGING_START  →  LOGGING_DATA",
              "249 Б у кадрі, без повторного запиту",
              "під час польоту; штовхає апарат", WARM),
    ]
    for cy, l1, l2, l3, col in lanes:
        f.append(fitbox(356, cy - 52, 608, 104, l1 + "\n" + l2 + "\n" + l3, size=13, fill=col))
        f.append(arrow(348, cy + 76, 972, cy + 76))

    f.append(line(348, 618, 972, 618, color=MUTED, sw=1.6, dash="7,6"))
    f.append(text(660, 606, "картка в руці: найшвидша дорога, коли до апарата можна дотягтися",
                  size=13, color=MUTED))

    return render(os.path.join(OUT, 'three-roads.svg'), W, H, *f)


# ───────────── 2. Вікно, кошики й пошук дірки ─────────────
def fig_chunk_table():
    W, H = 1340, 700
    f = []
    f.append(text(W / 2, 36, "Приймач веде облік прийнятого й сам просить те, чого бракує", size=17, bold=True))

    # ── увесь файл смугою вікон
    x0, x1, y = 70, 1270, 84
    seg = (x1 - x0) / 12.0
    f.append(text(x0, y - 12, "файл 18.4 МБ — 100 вікон по 180 КіБ", size=13, color=MUTED, anchor="start"))
    for i in range(12):
        col = GOOD if i < 3 else (WARM if i == 3 else SOFT)
        f.append(rect(x0 + i * seg, y, seg, 40, fill=col, stroke="#9aa7b4", sw=1.0, rx=0))
    f.append(text(x0 + 3.5 * seg, y + 66, "поточне вікно", size=12, color=MUTED))
    f.append(text(x0 + 1.5 * seg, y + 66, "закриті", size=12, color=MUTED))
    f.append(text(x0 + 8.0 * seg, y + 66, "ще не відкриті", size=12, color=MUTED))

    # ── зум у вікно
    zy = 210
    f.append(line(x0 + 3 * seg, y + 40, 90, zy - 14, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(x0 + 4 * seg, y + 40, 1250, zy - 14, color=MUTED, sw=1.2, dash="5,5"))

    cells, cx0, cx1 = 24, 90, 1250
    cw = (cx1 - cx0) / float(cells)
    filled = set(range(0, 9)) | set(range(12, 20)) | set(range(21, 24))
    f.append(text(cx0, zy - 24, "вікно зблизька: 2048 кошиків по 90 Б, таблиця — 2048 бітів (256 Б)",
                  size=13, color=MUTED, anchor="start"))
    for i in range(cells):
        col = GOOD if i in filled else SOFT
        f.append(rect(cx0 + i * cw, zy, cw, 52, fill=col, stroke="#9aa7b4", sw=1.0, rx=0))
        f.append(text(cx0 + (i + 0.5) * cw, zy + 33, "1" if i in filled else "0",
                      size=13, color=INK if i in filled else MUTED))

    # ── дужка під діркою
    gx0, gx1 = cx0 + 9 * cw, cx0 + 12 * cw
    by = zy + 52
    f.append(line(gx0, by + 14, gx1, by + 14, color=POS, sw=2.2))
    f.append(line(gx0, by, gx0, by + 14, color=POS, sw=2.2))
    f.append(line(gx1, by, gx1, by + 14, color=POS, sw=2.2))
    f.append(text((gx0 + gx1) / 2, by + 36, "перша дірка: кошики 9…11", size=13, color=POS, bold=True))

    # ── що з неї народжується
    b, bw, bh = textbox(400, 420, [
        "перший нуль у таблиці  →  start = 9",
        "наступна одиниця       →  end   = 12",
        "ofs   = вікно·184320 + 9·90",
        "count = (12 − 9)·90 = 270",
    ], size=13, fill=SOFT, pad=14)
    f.append(b)
    f.append(arrow((gx0 + gx1) / 2, by + 48, 400, 420 - bh / 2 - 6))
    f.append(text(400, 420 + bh / 2 + 26, "LOG_REQUEST_DATA просить рівно суцільний прогін",
                  size=13, color=MUTED))

    b2, _, bh2 = textbox(1000, 420, [
        "кожен пакет лягає за своїм зсувом:",
        "file.seek(ofs)  →  file.write(data)",
        "файл наперед розтягнуто на повний розмір,",
        "тож дірки в ньому — просто ще не заповнені місця",
    ], size=13, fill=COLD, pad=14)
    f.append(b2)
    f.append(text(1000, 420 + bh2 / 2 + 26, "порядок приходу не має значення", size=13, color=MUTED))

    # ── умова закриття вікна
    f.append(fitbox(300, 560, 740, 78,
                    "усі біти таблиці = 1  →  вікно закрите  →  advanceChunk(): наступне вікно, чиста таблиця\n"
                    "пакет із чужого вікна відкидається — станція тримає відкритим рівно одне",
                    size=13, fill=WARM))

    return render(os.path.join(OUT, 'chunk-table.svg'), W, H, *f)


# ───────────── 3. Ресинхронізація потокового логу ─────────────
def fig_stream_resync():
    W, H = 1320, 680
    f = []
    f.append(text(W / 2, 36, "Загублений пакет ламає межі повідомлень — і потік каже, де вони знову є",
                  size=17, bold=True))

    py, ph = 90, 84
    packs = [
        (70, 380, "LOGGING_DATA  seq 41", "249 Б корисного вантажу", GOOD),
        (470, 380, "LOGGING_DATA  seq 42", "не долетів", LOST),
        (870, 380, "LOGGING_DATA  seq 43", "first_message_offset = 34", GOOD),
    ]
    for x, w, title, note, col in packs:
        f.append(fitbox(x, py, w, ph, title + "\n" + note, size=13, fill=col,
                        stroke=POS if col == LOST else LINE))

    f.append(text(660, py + ph + 28, "лічильник кадрів дає різницю 43 − 41 − 1 = 1 втрачений",
                  size=13, color=MUTED))

    # ── байтова стрічка пакета 43
    sy = 250
    f.append(text(870, sy - 16, "вантаж пакета 43 зблизька", size=13, color=MUTED, anchor="start"))
    f.append(rect(870, sy, 110, 54, fill=LOST, stroke=POS, sw=1.6, rx=0))
    f.append(text(925, sy + 33, "34 Б", size=13, color=POS))
    f.append(rect(980, sy, 130, 54, fill=SOFT, stroke=LINE, sw=1.4, rx=0))
    f.append(text(1045, sy + 33, "3 Б + тіло", size=12))
    f.append(rect(1110, sy, 130, 54, fill=SOFT, stroke=LINE, sw=1.4, rx=0))
    f.append(text(1175, sy + 33, "3 Б + тіло", size=12))
    f.append(line(980, sy - 8, 980, sy + 62, color=FIELD, sw=2.4))
    f.append(text(980, sy + 84, "тут починається ціле повідомлення", size=12, color=FIELD))

    # ── стрічка пакета 41
    f.append(text(70, sy - 16, "вантаж пакета 41", size=13, color=MUTED, anchor="start"))
    f.append(rect(70, sy, 130, 54, fill=SOFT, stroke=LINE, sw=1.4, rx=0))
    f.append(text(135, sy + 33, "3 Б + тіло", size=12))
    f.append(rect(200, sy, 130, 54, fill=SOFT, stroke=LINE, sw=1.4, rx=0))
    f.append(text(265, sy + 33, "3 Б + тіло", size=12))
    f.append(rect(330, sy, 110, 54, fill=WARM, stroke=LINE, sw=1.4, rx=0))
    f.append(text(385, sy + 33, "хвіст", size=12))
    f.append(text(385, sy + 84, "недописане повідомлення чекає продовження", size=12, color=MUTED))

    # ── що виходить у файлі
    fy = 440
    f.append(text(70, fy - 18, "що лягає у файл .ulg на диску станції", size=13, color=MUTED, anchor="start"))
    f.append(fitbox(70, fy, 300, 76, "повідомлення\nз пакета 41", size=13, fill=SOFT))
    f.append(fitbox(400, fy, 340, 76, "службовий запис «розрив»\n{2, 0, 79, тривалість, 0}", size=13, fill=WARM))
    f.append(fitbox(770, fy, 300, 76, "повідомлення\nз пакета 43", size=13, fill=SOFT))
    f.append(arrow(370, fy + 38, 398, fy + 38))
    f.append(arrow(740, fy + 38, 768, fy + 38))

    f.append(fitbox(70, fy + 116, 1180, 74,
                    "недописаний хвіст і 34 байти після розриву відкинуто: зібрати з них ціле повідомлення нізвідки\n"
                    "натомість у файл вписано розрив мовою самого формату — читач побачить дірку, а не тиху брехню",
                    size=13, fill=COLD))

    return render(os.path.join(OUT, 'stream-resync.svg'), W, H, *f)


# ───────────── 4. Порядок полів: як описано ↔ як летить ─────────────
def fig_field_order():
    W, H = 1340, 640
    BPX = 70          # пікселів на байт
    X0 = 300          # ліва межа смуг
    f = []
    f.append(text(W / 2, 34, "Порядок полів у навантаженні: опис і дріт — не те саме",
                  size=17, bold=True))

    # кольори однакові для того самого поля в обох смугах
    C = {
        'time_utc': "#eaf0fd", 'size': "#eaf7ef", 'id': "#fdf3e7",
        'num_logs': "#f3eafd", 'last_log_num': "#fdecea",
        'ofs': "#eaf0fd", 'count': "#eaf7ef", 'addr': "#eef2f6",
    }

    def bar(y, fields, h=54):
        """fields — список (ім'я поля, байтів, підпис)."""
        x = X0
        for key, nb, label in fields:
            f.append(fitbox(x, y, nb * BPX, h, label, size=13,
                            fill=C[key], stroke="#c8d2dc", sw=1.4, rx=4))
            x += nb * BPX
        return x

    def ruler(y, nbytes, step=2):
        f.append(line(X0, y, X0 + nbytes * BPX, y, color="#c8d2dc", sw=1.2))
        b = 0
        while b <= nbytes:
            f.append(line(X0 + b * BPX, y - 5, X0 + b * BPX, y + 5, color="#c8d2dc", sw=1.2))
            f.append(text(X0 + b * BPX, y + 22, str(b), size=12, color=MUTED))
            b += step

    # ── LOG_ENTRY (118), 14 байтів
    f.append(text(60, 84, "LOG_ENTRY (118) — 14 байтів навантаження",
                  size=14, bold=True, anchor="start"))
    f.append(text(282, 145, "порядок в описі common.xml", size=13, color=MUTED, anchor="end"))
    bar(118, [('id', 2, "id"), ('num_logs', 2, "num_logs"),
              ('last_log_num', 2, "last_log_num"),
              ('time_utc', 4, "time_utc"), ('size', 4, "size")])

    f.append(text(282, 235, "порядок у пакеті", size=13, color=MUTED, anchor="end"))
    bar(208, [('time_utc', 4, "time_utc"), ('size', 4, "size"), ('id', 2, "id"),
              ('num_logs', 2, "num_logs"), ('last_log_num', 2, "last_log_num")])
    ruler(288, 14)

    # ── LOG_REQUEST_DATA (119), 12 байтів
    f.append(text(60, 380, "LOG_REQUEST_DATA (119) — 12 байтів навантаження",
                  size=14, bold=True, anchor="start"))
    f.append(text(282, 441, "порядок в описі common.xml", size=13, color=MUTED, anchor="end"))
    bar(414, [('addr', 2, "target_system\ntarget_component"), ('id', 2, "id"),
              ('ofs', 4, "ofs"), ('count', 4, "count")])

    f.append(text(282, 531, "порядок у пакеті", size=13, color=MUTED, anchor="end"))
    bar(504, [('ofs', 4, "ofs"), ('count', 4, "count"), ('id', 2, "id"),
              ('addr', 2, "target_system\ntarget_component")])
    ruler(584, 12)

    return render(os.path.join(OUT, 'field-order.svg'), W, H, *f)


# ───────────── 5. Шари транспортів: додавали, не замінюючи ─────────────
def fig_transport_layers():
    W, H = 1280, 560
    f = []
    f.append(text(W / 2, 38, "Кожен новий шлях додавали поверх старого, а не замість нього",
                  size=17, bold=True))

    X_END = 1210
    axis_y = 452
    rows = [
        (2013, 210, 92, COLD,
         "LOG_REQUEST_LIST / LOG_ENTRY / LOG_REQUEST_DATA / LOG_DATA",
         "щоб прибрати текстову консоль APM2: 90 Б у порції, номери записів"),
        (2014, 350, 214, GOOD,
         "FILE_TRANSFER_PROTOCOL (MAVFTP)",
         "загальний доступ до файлів борту; для логів його приладнали пізніше"),
        (2016, 640, 336, WARM,
         "MAV_CMD_LOGGING_START / LOGGING_DATA / LOGGING_DATA_ACKED",
         "ULog у PX4 треба віддавати в польоті: 249 Б у кадрі MAVLink 2"),
    ]
    for year, x0, y, col, l1, l2 in rows:
        f.append(fitbox(x0, y, X_END - x0, 78, l1 + "\n" + l2, size=14, fill=col))
        f.append(line(x0, y + 78, x0, axis_y - 8, color=MUTED, sw=1.2, dash="5,5"))

    f.append(line(150, axis_y, X_END, axis_y, color=MUTED, sw=1.6))
    for year, x0, _y, _c, _a, _b in rows:
        f.append(text(x0, axis_y + 26, str(year), size=14, bold=True))
    f.append(text(X_END - 40, axis_y + 26, "сьогодні", size=14, color=MUTED))

    f.append(text(W / 2, axis_y + 74,
                  "жоден шар не прибрано — станція мусить уміти всі три, "
                  "бо прошивки в полі оновлять не всі", size=14, color=MUTED))
    return render(os.path.join(OUT, 'transport-layers.svg'), W, H, *f)


# ───────────── 6. Час на дроті: коли просити наступне ─────────────
def fig_downloader_time():
    W, H = 1340, 620
    f = []
    f.append(text(W / 2, 34, "Коли просити наступне: черга, тиша й добита дірка",
                  size=17, bold=True))

    ly, lh = 96, 46
    f.append(text(86, ly + 30, "ефір", size=13, color=MUTED, anchor="end"))
    f.append(line(100, ly + lh + 12, 1240, ly + lh + 12, color="#c8d2dc", sw=1.2))

    missing = {11, 12, 20}
    for i in range(30):
        x = 150 + i * 18
        if i in missing:
            f.append(rect(x, ly, 12, lh, fill=LOST, stroke=POS, sw=1.3, rx=2))
        else:
            f.append(rect(x, ly, 12, lh, fill=GOOD, stroke="#9aa7b4", sw=1.0, rx=2))

    f.append(rect(700, ly + 9, 120, lh - 18, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=4))
    f.append(text(760, ly + 30, "тиша", size=12, color=MUTED))

    for x in (840, 858, 900):
        f.append(rect(x, ly, 12, lh, fill=GOOD, stroke="#9aa7b4", sw=1.0, rx=2))
    f.append(text(960, ly + 30, "…", size=17, color=MUTED, anchor="start"))

    boxes = [
        (156, 120, 260, "LOG_REQUEST_DATA\nна все вікно:\ncount = 184 320 Б"),
        (760, 435, 250, "пів секунди без пакетів —\nчерга обірвалася"),
        (836, 745, 250, "перша дірка 11…12 —\nзапит рівно на 180 Б"),
        (872, 1045, 230, "прогін добито —\nзапит негайно,\nне чекаючи таймера"),
    ]
    for ex, bx, bw, label in boxes:
        f.append(fitbox(bx, 300, bw, 100, label, size=13, fill=SOFT))
        f.append(arrow(ex, ly + lh + 14, bx + bw / 2.0, 296))

    f.append(fitbox(80, 440, 600, 130,
                    "після кожної безплідної спроби чекаємо довше:\n"
                    "500 → 1000 → 1500 → … → 3000 мс (стеля)\n"
                    "20 спроб поспіль без жодного нового кошика — здаємося\n"
                    "і обрізаємо файл до першої дірки",
                    size=13, fill=COLD))

    f.append(fitbox(720, 440, 560, 130,
                    "зливати дві дірки в один запит вигідно, поки\n"
                    "g × 90 Б / 5760 Б/с  <  RTT = 0.120 с\n"
                    "g < 0.120 × 5760 / 90 ≈ 8 прийнятих кошиків\n"
                    "зайві байти дешевші за зайвий оберт",
                    size=13, fill=WARM))

    return render(os.path.join(OUT, 'downloader-time.svg'), W, H, *f)


if __name__ == '__main__':
    print(fig_transport_layers())
    print(fig_three_roads())
    print(fig_chunk_table())
    print(fig_stream_resync())
    print(fig_field_order())
    print(fig_downloader_time())
