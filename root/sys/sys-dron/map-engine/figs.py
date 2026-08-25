# -*- coding: utf-8 -*-
"""Фігури до теми «Рушій карти: провайдери, тайли, рівні масштабу»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

SOFT = "#eef3fb"      # те, що дає фреймворк
OWN  = "#e8f6ec"      # те, що підмінює станція
WARM = "#fdeeea"      # мережа / зовнішній світ


# ── 1. Шари рушія карти ─────────────────────────────────────────────────────
def engine_layers():
    W, H = 1020, 660
    f = []

    # верх: те, що бачить оператор
    f.append(fitbox(300, 56, 420, 54, "Карта на екрані оператора",
                    size=17, bold=True, fill=FILL))

    f.append(arrow(510, 110, 510, 140))

    # смуга фреймворку
    f.append(fitbox(60, 142, 900, 78,
                    "Геометрія і малювання — готове у фреймворку\n"
                    "які клітинки потрібні · куди їх покласти · плавний масштаб і поворот",
                    size=15, fill=SOFT, stroke=NEG))
    f.append(text(510, 240, "станція підміняє лише постачання байтів", size=14, color=MUTED))

    xs = [60, 372, 684]
    caps = [
        "Список типів карти\nякі джерела існують\nу цій збірці",
        "Добувач тайлів\nяк зробити запит\nза адресою",
        "Сховище тайлів\nде байти живуть\nміж сеансами",
    ]
    for x, cap in zip(xs, caps):
        f.append(arrow(x + 138, 252, x + 138, 282))
        f.append(fitbox(x, 284, 276, 92, cap, size=15, fill=OWN, stroke=FIELD, bold=True))

    unders = [
        "UrlFactory\nстатичний список\n≈40 правил адресації",
        "заголовки браузера\n6 паралельних\n10 с на переказ",
        "QGCMapEngine\nнитка-власник бази\nqgcMapCache.db",
    ]
    for x, cap in zip(xs, unders):
        f.append(arrow(x + 138, 378, x + 138, 410))
        f.append(fitbox(x, 412, 276, 96, cap, size=14, fill=FILL))

    # низ: зовнішній світ
    f.append(arrow(510, 510, 510, 546))
    f.append(fitbox(210, 548, 600, 76,
                    "Тайл: адресований шматок просторових даних\n"
                    "картинка джерела або сітка висот рельєфу",
                    size=15, fill=WARM, stroke=POS))

    render(os.path.join(OUT, 'engine-layers.svg'), W, H, *f,
           title="Рушій карти: що готове, а що станція пише сама")


# ── 2. Шлях одного тайла ────────────────────────────────────────────────────
def tile_read_path():
    W, H = 1020, 760
    f = []

    # смуга нитки бази
    f.append(rect(40, 236, 940, 150, fill="#f7f9fc", stroke="#c9d4e4", sw=1.2, rx=10))
    f.append(text(64, 262, "нитка бази (окремий власник файлу)",
                  size=13, color=MUTED, anchor="start"))

    # головна нитка — крок 1 і 2
    f.append(fitbox(330, 56, 360, 56, "Кадру потрібен тайл z/x/y", size=16, bold=True, fill=FILL))
    f.append(arrow(510, 112, 510, 142))
    f.append(fitbox(300, 144, 420, 56, "ключ = провайдер + x + y + z", size=16, fill=OWN, stroke=FIELD))
    f.append(text(742, 178, "задача в чергу", size=13, color=MUTED, anchor="start"))
    f.append(arrow(510, 200, 510, 288))

    # у нитці бази
    f.append(fitbox(300, 290, 420, 66,
                    "SELECT tile FROM Tiles\nWHERE hash = ключ", size=15, fill=FILL))

    # дві гілки
    f.append(arrow(390, 356, 270, 424))
    f.append(text(258, 404, "знайдено", size=13, color=FIELD, anchor="end", bold=True))
    f.append(arrow(630, 356, 760, 424))
    f.append(text(772, 404, "порожньо", size=13, color=POS, anchor="start", bold=True))

    # ліва гілка — показ
    f.append(fitbox(60, 426, 300, 62, "Байти з диска — на екран", size=15,
                    fill=OWN, stroke=FIELD))

    # права гілка — мережа
    f.append(fitbox(650, 426, 320, 62, "Запит за адресою провайдера", size=15,
                    fill=WARM, stroke=POS))
    f.append(arrow(810, 488, 810, 528))
    f.append(fitbox(650, 530, 320, 76,
                    "Перевірка відповіді\nформат · заглушка «немає тайла»",
                    size=14, fill=WARM, stroke=POS))
    f.append(arrow(810, 606, 810, 646))
    f.append(fitbox(650, 648, 320, 60, "Показ негайно", size=15, fill=OWN, stroke=FIELD))

    # запис назад у базу — пунктиром
    f.append(line(650, 678, 210, 678, color=MUTED, sw=1.5, dash="7,6"))
    f.append(line(210, 678, 210, 560, color=MUTED, sw=1.5, dash="7,6"))
    f.append(fitbox(60, 500, 300, 58, "Запис у базу\nокремою задачею, потім",
                    size=14, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, 'tile-read-path.svg'), W, H, *f,
           title="Шлях одного тайла: база перед мережею")


# ── 3. Драбина рівнів масштабу ──────────────────────────────────────────────
def zoom_ladder():
    W, H = 1040, 470
    f = []

    cols = [
        ("z = 2",  "24.9 км/пкс", "світ"),
        ("z = 8",  "389 м/пкс",   "область"),
        ("z = 12", "24.3 м/пкс",  "місто"),
        ("z = 16", "1.52 м/пкс",  "квартал"),
        ("z = 18", "0.38 м/пкс",  "розмітка"),
        ("z = 20", "9.5 см/пкс",  "межа джерел"),
        ("z = 23", "1.2 см/пкс",  "розтягнуто"),
    ]

    x0, cw, gap, y = 40, 128, 10, 214
    # смуга наявності даних
    n = len(cols)
    span_data = x0 + 6 * (cw + gap) - gap          # до z = 20 включно
    f.append(rect(x0, 116, span_data - x0, 54, fill="#eaf7ef", stroke=FIELD, sw=1.3))
    f.append(text(x0 + (span_data - x0) / 2, 149, "тайли справді існують у джерела",
                  size=14, color="#1c7a44"))

    x_over = x0 + 6 * (cw + gap)
    w_over = cw
    f.append(rect(x_over, 116, w_over, 54, fill="#fdeeea", stroke=POS, sw=1.3))
    f.append(text(x_over + w_over / 2, 143, "предок", size=13, color=POS))
    f.append(text(x_over + w_over / 2, 160, "розтягнуто", size=13, color=POS))

    for i, (z, res, what) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(fitbox(x, y, cw, 50, z, size=16, bold=True, fill=FILL))
        f.append(fitbox(x, y + 56, cw, 44, res, size=13, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(x, y + 106, cw, 44, what, size=13, fill="#ffffff", stroke=MUTED))

    f.append(text(W / 2, 396, "роздільність порахована для широти 50.45°",
                  size=13, color=MUTED))
    f.append(text(W / 2, 428, "вікно показу станції: від 2 до 23 — межі даних лежать усередині",
                  size=14, color=INK))

    render(os.path.join(OUT, 'zoom-ladder.svg'), W, H, *f,
           title="Рівні масштабу: де закінчуються дані джерела")


# ── 4. Контракт провайдера: хто що відповідає ───────────────────────────────
def provider_contract():
    W, H = 1080, 790
    f = []

    f.append(fitbox(290, 54, 500, 84,
                    "UrlFactory — статичний фасад\n"
                    "пошук за назвою або за номером карти\n"
                    "_providers: готовий список об'єктів",
                    size=15, fill=SOFT, stroke=NEG))

    f.append(arrow(540, 138, 540, 172))
    f.append(fitbox(340, 174, 400, 50, "MapProvider — базовий клас",
                    size=17, bold=True, fill=OWN, stroke=FIELD))

    # розгалуження на дві колонки
    f.append(line(540, 224, 540, 242))
    f.append(line(300, 242, 780, 242))
    f.append(arrow(300, 242, 300, 262))
    f.append(arrow(780, 242, 780, 262))

    f.append(fitbox(70, 262, 460, 182,
                    "ГОТОВЕ ДЛЯ ВСІХ\n"
                    "getTileURL(x, y, zoom)\n"
                    "getImageFormat(байти)\n"
                    "getTileCount(zoom, кути)\n"
                    "long2tileX · lat2tileY\n"
                    "tileX2long · tileY2lat",
                    size=15, fill=SOFT, stroke=NEG))

    f.append(fitbox(550, 262, 460, 182,
                    "ПОМІЧНИКИ Й ПОЛЯ\n"
                    "_tileXYToQuadKey(x, y, z)\n"
                    "_getServerNum(x, y, max)\n"
                    "_imageFormat · _averageSize\n"
                    "_language · _referrer\n"
                    "_mapId — номер із лічильника",
                    size=15, fill=FILL))

    f.append(arrow(300, 446, 462, 492))
    f.append(arrow(780, 446, 618, 492))
    f.append(fitbox(330, 494, 420, 60,
                    "єдина чиста віртуальна:\n_getURL(x, y, zoom)",
                    size=15, bold=True, fill=WARM, stroke=POS))

    f.append(arrow(430, 554, 268, 600))
    f.append(arrow(650, 554, 812, 600))

    f.append(fitbox(60, 602, 420, 148,
                    "Звичайне джерело\n"
                    "складає адресу з z/x/y\n"
                    "за потреби: getToken\n"
                    "за потреби: isBingProvider\n"
                    "приклад: OpenStreetMapProvider",
                    size=14, fill=OWN, stroke=FIELD))

    f.append(fitbox(600, 602, 420, 148,
                    "ElevationProvider\n"
                    "isElevationProvider() = true\n"
                    "додає serialize(байти) = 0\n"
                    "своя градусна сітка\n"
                    "приклад: CopernicusElevationProvider",
                    size=14, fill=OWN, stroke=FIELD))

    render(os.path.join(OUT, 'provider-contract.svg'), W, H, *f,
           title="Контракт провайдера: що дає базовий клас і що мусить дати нащадок")


# ── Гачки власного провайдера на шляху однієї клітинки ──────────────────────
def custom_source_hooks():
    W, H = 1160, 830
    f = []

    CX = 400                      # центр колонки-потоку
    BX, BW = 150, 500             # ліва межа й ширина боксів потоку
    AX, AW = 700, 400             # анотації праворуч

    def flow(y, h, s, fill=FILL, stroke=LINE, size=15, bold=False):
        f.append(fitbox(BX, y, BW, h, s, size=size, fill=fill, stroke=stroke, bold=bold))

    def note(y, h, s, fill, stroke, size=14):
        f.append(fitbox(AX, y, AW, h, s, size=size, fill=fill, stroke=stroke))

    flow(62, 56, "Фреймворк просить клітинку  z / x / y", fill=SOFT, stroke=NEG)
    f.append(arrow(CX, 118, CX, 150))

    flow(152, 116,
         "getNetworkRequest()\n"
         "адреса ← _getURL(x, y, zoom) — ваш метод\n"
         "Referer ← getReferrer() — конструктор\n"
         "User-Token ← getToken() — ваш метод",
         fill=OWN, stroke=FIELD, size=15)
    f.append(arrow(CX, 268, CX, 300))

    flow(302, 58, "адреса порожня?", fill=WARM, stroke=POS, bold=True)
    f.append(arrow(BX + BW, 331, AX, 331, color=POS))
    f.append(text((BX + BW + AX) / 2, 318, "так", size=13, color=POS))
    note(298, 66, "ні запиту, ні читання з бази\nкарта розтягує предка",
         fill="#fdeeea", stroke=POS)

    f.append(arrow(CX, 360, CX, 392))
    f.append(text(CX + 24, 380, "ні", size=13, color=MUTED, anchor="start"))

    flow(394, 58, "створено відповідь → задача в базу тайлів")
    f.append(arrow(CX, 452, CX, 484))

    flow(486, 58, "клітинка є в базі?", fill=FILL, stroke=NEG, bold=True)
    f.append(arrow(BX + BW, 515, AX, 515, color=FIELD))
    f.append(text((BX + BW + AX) / 2, 502, "так", size=13, color=FIELD))
    note(482, 66, "показ із диска\nмережа не потрібна",
         fill="#eaf7ef", stroke=FIELD)

    f.append(arrow(CX, 544, CX, 576))
    f.append(text(CX + 24, 564, "ні", size=13, color=MUTED, anchor="start"))

    flow(578, 58, "мережа: запит із заголовками", fill=WARM, stroke=POS)
    f.append(arrow(CX, 636, CX, 668))

    flow(670, 76,
         "формат ← getImageFormat(байти)\n"
         "три сигнатури, інакше ваш _imageFormat → запис у базу",
         fill=OWN, stroke=FIELD, size=15)

    f.append(text(W / 2, 792,
                  "перевірка адреси стоїть ВИЩЕ за базу — тому порожня адреса вимикає й кеш",
                  size=15, color=POS))

    render(os.path.join(OUT, 'custom-source-hooks.svg'), W, H, *f,
           title="Шлях клітинки крізь гачки власного провайдера")


# ── Номер провайдера пливе між складаннями ──────────────────────────────────
def provider_id_drift():
    W, H = 1120, 660
    f = []

    LX, RX, CW = 50, 590, 480
    f.append(fitbox(LX, 62, CW, 54,
                    "настільна збірка — 41 провайдер", size=16, bold=True,
                    fill=SOFT, stroke=NEG))
    f.append(fitbox(RX, 62, CW, 54,
                    "збірка під iOS: QGC_NO_GOOGLE_MAPS", size=16, bold=True,
                    fill=WARM, stroke=POS))

    left = ["1 — Google Street Map", "5 — Google Labels", "6 — Bing Road",
            "36 — LINZ Basemap", "39 — CustomURL Custom", "41 — SkyOrtho Aerial"]
    right = ["google-провайдерів немає", "—", "1 — Bing Road",
             "31 — LINZ Basemap", "34 — CustomURL Custom", "36 — SkyOrtho Aerial"]

    y0, rh, gap = 134, 40, 8
    for i, (l, r) in enumerate(zip(left, right)):
        y = y0 + i * (rh + gap)
        mine = (i == len(left) - 1)
        f.append(fitbox(LX, y, CW, rh, l, size=15,
                        fill=(OWN if mine else BG),
                        stroke=(FIELD if mine else MUTED), bold=mine))
        f.append(fitbox(RX, y, CW, rh, r, size=15,
                        fill=(OWN if mine else BG),
                        stroke=(FIELD if mine else MUTED), bold=mine))

    ky = y0 + len(left) * (rh + gap) + 16
    f.append(fitbox(LX, ky, CW, 54,
                    "ключ  0000000041 00153296 00088388 018", size=15, fill=FILL))
    f.append(fitbox(RX, ky, CW, 54,
                    "ключ  0000000036 00153296 00088388 018", size=15, fill=FILL))

    ny = ky + 84
    f.append(arrow(RX + CW / 2, ky + 54, LX + CW / 2, ny, color=POS))
    f.append(fitbox(LX, ny, RX + CW - LX, 62,
                    "база з планшета, прочитана на десктопі: провайдер 36 — це LINZ Basemap;"
                    " помилки немає, знімки чужі",
                    size=15, fill="#fdeeea", stroke=POS))

    render(os.path.join(OUT, 'provider-id-drift.svg'), W, H, *f,
           title="Номер провайдера залежить від складання, а ключ кеша — від номера")


engine_layers()
tile_read_path()
zoom_ladder()
provider_contract()
custom_source_hooks()
provider_id_drift()
print("ok")
