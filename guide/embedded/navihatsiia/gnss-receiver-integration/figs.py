# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки поверх палітри svgkit
SKY_FILL = "#eef4ff"   # «зовнішнє / небо»
SKY_STK  = "#c9d6f0"
CHIP_FILL = "#f4f6f8"  # модуль
TXT_FILL = "#fef6e7"   # текстова мова (NMEA) — тепле
TXT_STK  = "#e9d8a6"
BIN_FILL = "#eafaf1"   # двійкова мова (UBX) — холодне
BIN_STK  = "#bfe6cf"


# ── blackbox: модуль усе рахує всередині, назовні лише UART ───────────────────
# Ідея поділу праці: RF + фікс живуть у чипі; прошивка бачить лише готове рішення
# на TX і може налаштувати модуль по RX. Прошивка НЕ рахує координати.
def fig_blackbox():
    W, H = 760, 340
    p = []
    p.append(text(W/2, 30, "GNSS-модуль: усе рахує сам, назовні — лише UART", size=16, bold=True))

    # супутники + небо ліворуч
    sky_x = 40
    for i, sx in enumerate([sky_x + 10, sky_x + 55, sky_x + 30]):
        sy = 70 + (i % 2) * 26
        p.append(circle(sx, sy, 7, fill=SKY_FILL, stroke=SKY_STK, sw=1.5))
    p.append(text(sky_x + 40, 118, "супутники", size=11.5, color=MUTED))
    # хвиля-стрілка до антени
    p.append(arrow(sky_x + 40, 130, sky_x + 78, 168, color=MUTED, sw=1.5))

    # модуль — велика чорна скринька
    mx, my, mw, mh = 130, 150, 300, 150
    p.append(rect(mx, my, mw, mh, fill=CHIP_FILL, stroke=LINE, sw=2.0))
    p.append(text(mx + mw/2, my + 26, "GNSS-модуль (u-blox NEO-M8/M9)", size=13, bold=True))
    inner = ["антена + радіочастина", "власний процесор:", "ефемериди · трилатерація · Δt"]
    iy = my + 52
    for i, s in enumerate(inner):
        p.append(text(mx + mw/2, iy + i*24, s, size=12,
                      color=NEG if i == 1 else INK, bold=(i == 1)))
    p.append(text(mx + mw/2, my + mh - 12, "1–10 разів/с видає готове рішення", size=11, color=MUTED))

    # мікроконтролер праворуч
    ux, uy, uw, uh = 560, 175, 160, 100
    p.append(rect(ux, uy, uw, uh, fill=SKY_FILL, stroke=SKY_STK, sw=1.8))
    p.append(text(ux + uw/2, uy + 34, "мікроконтролер", size=13, bold=True))
    p.append(text(ux + uw/2, uy + 58, "(наша прошивка):", size=12, color=MUTED))
    p.append(text(ux + uw/2, uy + 78, "РОЗБИРАЄ потік", size=12, color=FIELD, bold=True))

    # TX: модуль → мікроконтролер (дані)
    p.append(arrow(mx + mw + 4, my + 55, ux - 4, uy + 30, color=FIELD, sw=2.2))
    p.append(text((mx + mw + ux)/2 + 4, my + 46, "TX  готові дані", size=12, color=FIELD, bold=True))
    # RX: мікроконтролер → модуль (налаштування)
    p.append(arrow(ux - 4, uy + 70, mx + mw + 4, my + 100, color=POS, sw=2.0))
    p.append(text((mx + mw + ux)/2 + 4, my + 116, "RX  налаштування", size=12, color=POS, bold=True))

    p.append(text(W/2, 326, "Усе до UART-виводу — не наше; наше починається на потоці байтів", size=11.5, color=MUTED))
    render(os.path.join(OUT, "blackbox.svg"), W, H, *p)


# ── formats: анатомія NMEA-речення проти UBX-пакета ───────────────────────────
# Ідея: та сама відповідь двома мовами — текст, зручний людині, проти двійкового
# каркаса, зручного машині. Показати структуру обох в одному кадрі.
def fig_formats():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 30, "Дві мови модуля: текстова NMEA проти двійкової UBX", size=16, bold=True))

    # NMEA — угорі
    ny = 70
    p.append(text(40, ny, "NMEA 0183 — текст ASCII (читаєш очима)", size=13, bold=True, anchor="start"))
    fields = [("$", "поч."), ("GNGGA", "формат"), ("123519", "час"),
              ("4916.45,N", "широта"), ("03038.71,E", "довгота"),
              ("1", "фікс"), ("08", "супут."), ("0.9", "HDOP"), ("*4F", "сума")]
    x = 40
    cell_h = 30
    cy = ny + 16
    for val, lab in fields:
        w = max(52, text_width(val, 12) + 14)
        fill = TXT_FILL
        stk = TXT_STK
        p.append(rect(x, cy, w, cell_h, fill=fill, stroke=stk, sw=1.4))
        p.append(text(x + w/2, cy + 20, val, size=12, color=INK))
        p.append(text(x + w/2, cy + cell_h + 15, lab, size=10.5, color=MUTED))
        x += w + 6
    p.append(text(40, cy + cell_h + 40, "поля через кому · XOR-сума · градуси-хвилини, обмежена точність",
                  size=11, color=MUTED, anchor="start"))

    # UBX — унизу
    uy = 210
    p.append(text(40, uy, "UBX — двійковий пакет (зручно машині)", size=13, bold=True, anchor="start"))
    ub = [("B5 62", "сигнатура", BIN_STK), ("01", "клас", BIN_FILL), ("07", "ID", BIN_FILL),
          ("5C 00", "довжина", BIN_FILL), ("… 92 байти …", "дані: lat/lon/alt/vel/час", CHIP_FILL),
          ("CK_A CK_B", "сума Флетчера", BIN_STK)]
    x = 40
    cy2 = uy + 16
    for val, lab, fl in ub:
        w = max(60, text_width(val, 12) + 16)
        if "дані" in lab:
            w = 210
        p.append(rect(x, cy2, w, cell_h, fill=fl, stroke=BIN_STK, sw=1.4))
        p.append(text(x + w/2, cy2 + 20, val, size=12, color=INK))
        p.append(text(x + w/2, cy2 + cell_h + 15, lab, size=10.5, color=MUTED))
        x += w + 6
    p.append(text(40, cy2 + cell_h + 40, "жорсткий каркас · довжина каже, скільки читати · числа — повні цілі (lat × 1e7)",
                  size=11, color=MUTED, anchor="start"))

    p.append(text(W/2, 348, "Один модуль зазвичай уміє обидві — питання, що ти наказав видавати", size=11.5, color=MUTED))
    render(os.path.join(OUT, "formats.svg"), W, H, *p)


# ── parser: неблокуючий скінченний автомат, годований по байту ────────────────
# Ідея: дані течуть без меж; не можна чекати цілий пакет у циклі — годуємо
# автомат по одному байту, він посувається станами й віддає готове повідомлення.
def fig_parser():
    W, H = 820, 300
    p = []
    p.append(text(W/2, 30, "Розбір потоку без блокування: автомат по одному байту", size=16, bold=True))

    # потік байтів згори
    bx, by = 40, 78
    p.append(text(bx, by - 16, "UART: байти течуть без меж", size=11.5, color=MUTED, anchor="start"))
    for i, ch in enumerate(["B5", "62", "01", "07", "..", "CK"]):
        cx = bx + i * 30
        p.append(rect(cx, by, 26, 24, fill="#f0f0f0", stroke=MUTED, sw=1.0, rx=3))
        p.append(text(cx + 13, by + 17, ch, size=11, color=INK))
    p.append(text(bx + 6*30 + 8, by + 17, "→ по одному в автомат", size=11.5, color=MUTED, anchor="start"))

    # ланцюг станів
    sy = 165
    states = [("чекай\nB5 62", CHIP_FILL, LINE), ("читай\nclass·id", CHIP_FILL, LINE),
              ("читай\nдовжину", TXT_FILL, TXT_STK), ("набирай\nдані", CHIP_FILL, LINE),
              ("звір\nсуму", BIN_FILL, BIN_STK)]
    bw, bh, gap = 118, 62, 22
    x0 = (W - (len(states)*bw + (len(states)-1)*gap)) / 2
    xs = []
    for i, (lab, fl, stk) in enumerate(states):
        x = x0 + i * (bw + gap)
        xs.append(x)
        p.append(fitbox(x, sy, bw, bh, lab, size=12.5, fill=fl, stroke=stk, bold=True))
        if i < len(states) - 1:
            p.append(arrow(x + bw + 2, sy + bh/2, x + bw + gap - 2, sy + bh/2, color=INK, sw=1.8))

    # готове повідомлення вниз
    lastx = xs[-1] + bw/2
    p.append(arrow(lastx, sy + bh + 2, lastx, sy + bh + 34, color=FIELD, sw=2.2))
    fbw = 250
    fbx = min(lastx - fbw/2, W - fbw - 10)
    p.append(fitbox(fbx, sy + bh + 36, fbw, 34, "валідний NAV-PVT → оцінювачу",
                    size=12.5, fill=BIN_FILL, stroke=BIN_STK, bold=True))

    # петля-скидання при збої
    p.append(text(x0, sy - 14, "збій (не той байт / сума) → назад у пошук сигнатури",
                  size=11, color=POS, anchor="start"))
    render(os.path.join(OUT, "parser.svg"), W, H, *p)


# ── two-lineages: дві родоводи двох мов на одній осі часу ─────────────────────
# Ідея вставки-історії: NMEA й UBX народилися в різних світах з різних потреб.
# Верхня доріжка — морська галузь США (дилери → асоціація → текстовий стандарт).
# Нижня — швейцарська лабораторія ETH (студенти → чип → двійковий протокол).
# Око бачить одразу: чому одна мова текстова й повільна, а друга двійкова й щільна.
def fig_two_lineages():
    W, H = 820, 380
    p = []
    p.append(text(W/2, 30, "Дві мови GNSS — дві родоводи: морський стандарт і швейцарський чип",
                  size=15.5, bold=True))

    # спільна вісь часу
    ax0, ax1, axy = 60, W - 40, 200
    p.append(line(ax0, axy, ax1, axy, color=MUTED, sw=1.4))
    years = [(1957, "1957"), (1983, "1983"), (1997, "1997"), (2000, "2000")]
    def X(year):  # 1955 → ax0, 2005 → ax1
        return ax0 + (year - 1955) * (ax1 - ax0) / (2005 - 1955)
    for yr, lab in years:
        x = X(yr)
        p.append(line(x, axy - 5, x, axy + 5, color=MUTED, sw=1.4))
        p.append(text(x, axy + 20, lab, size=11, color=MUTED))

    # верхня доріжка — NMEA (текст, тепле)
    ty = 90
    p.append(text(ax0, ty - 20, "NMEA 0183 — морська електроніка США (галузева асоціація)",
                  size=12.5, bold=True, anchor="start", color="#9a7b1f"))
    p.append(fitbox(X(1957) - 58, ty, 116, 46,
                    "1957\nдилери на\nBoat Show → NMEA", size=10.5,
                    fill=TXT_FILL, stroke=TXT_STK))
    p.append(fitbox(X(1983) - 62, ty, 124, 46,
                    "1983\nтекст ASCII,\n4800 бод, RS-422", size=10.5,
                    fill=TXT_FILL, stroke=TXT_STK, bold=True))
    p.append(arrow(X(1957) + 58, ty + 23, X(1983) - 64, ty + 23, color=TXT_STK, sw=1.8))

    # нижня доріжка — u-blox / UBX (двійкове, холодне)
    uy = 250
    p.append(text(ax0, uy + 70, "UBX — швейцарська u-blox (спін-оф ETH Zürich)",
                  size=12.5, bold=True, anchor="start", color="#2f7d54"))
    # роки 1997 і 2000 близькі на осі — рознесемо бокси вручну, щоб не налазили
    b1x = X(1997) - 130
    b2x = 690
    p.append(fitbox(b1x, uy, 118, 46,
                    "1997\n3 інженери ETH\n→ u-blox, Тальвіль", size=10.5,
                    fill=BIN_FILL, stroke=BIN_STK, bold=True))
    p.append(fitbox(b2x, uy, 118, 46,
                    "~2000\nдвійковий UBX:\nсигнатура · довжина", size=10.5,
                    fill=BIN_FILL, stroke=BIN_STK))
    p.append(arrow(b1x + 118 + 2, uy + 23, b2x - 2, uy + 23, color=BIN_STK, sw=1.8))

    # короткі прив'язки до осі — лише «вусики» біля самої осі, щоб НЕ різати підписи боксів
    for yr in (1957, 1983):
        p.append(line(X(yr), axy - 16, X(yr), axy - 5, color=TXT_STK, sw=1.0, dash="3,3"))
    for yr in (1997, 2000):
        p.append(line(X(yr), axy + 5, X(yr), axy + 16, color=BIN_STK, sw=1.0, dash="3,3"))

    p.append(text(W/2, H - 12,
                  "40 років різниці й різні світи → різні мови: текст для приладів, байти для чипа",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "two-lineages.svg"), W, H, *p)


# ══════════════════════════════════════════════════════════════════════════════
#  ДЕТАЛЬНА (-d): глибші фігури — числова анатомія, байтова карта, Флетчер,
#  граничні умови автомата, стартовий ритуал CFG.
# ══════════════════════════════════════════════════════════════════════════════

# ── scale-ladder: точність двох форматів на одній драбині ─────────────────────
# Ідея: NMEA пише «градуси-хвилини» з 4 знаками у хвилинах → крок ~0.19 м;
# UBX пише ціле × 10⁻⁷° → крок ~11 мм; а cos(φ) ще стискає довготу на широтах.
# Око бачить: обидва формати мають ЖОРСТКУ межу молодшого біта, і вони різні.
def fig_scale_ladder():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 30, "Найдрібніший крок координати: що NMEA й UBX фізично вміщають", size=15.5, bold=True))

    # ліва колонка — NMEA (тепле)
    lx = 60
    p.append(fitbox(lx, 66, 300, 40, "NMEA GGA: ГГММ.mmmm — градуси й хвилини",
                    size=12.5, fill=TXT_FILL, stroke=TXT_STK, bold=True))
    nmea_rows = [
        "4916.4590,N",
        "= 49° + 16.4590′",
        "молодший знак = 0.0001′",
        "1′ широти ≈ 1852 м",
        "крок ≈ 0.0001 × 1852 ≈ 0.19 м",
    ]
    ry = 122
    for i, s in enumerate(nmea_rows):
        bold = (i == 4)
        col = POS if i == 4 else INK
        p.append(text(lx + 8, ry + i*30, s, size=12.5, color=col, bold=bold, anchor="start"))
    p.append(text(lx + 8, ry + 5*30 + 6, "текст фіксованої розрядності — глибше не запишеш",
                  size=11, color=MUTED, anchor="start"))

    # права колонка — UBX (холодне)
    rx = 420
    p.append(fitbox(rx, 66, 300, 40, "UBX NAV-PVT: int32 × 10⁻⁷ градуса",
                    size=12.5, fill=BIN_FILL, stroke=BIN_STK, bold=True))
    ubx_rows = [
        "lat = 492741500  (ціле)",
        "→ 49.2741500°",
        "молодший біт = 10⁻⁷°",
        "1° широти ≈ 111 320 000 мм",
        "крок ≈ 10⁻⁷ × 111.32e6 ≈ 11 мм",
    ]
    for i, s in enumerate(ubx_rows):
        bold = (i == 4)
        col = FIELD if i == 4 else INK
        p.append(text(rx + 8, ry + i*30, s, size=12.5, color=col, bold=bold, anchor="start"))
    p.append(text(rx + 8, ry + 5*30 + 6, "ціле — крок у ~17 разів дрібніший за NMEA",
                  size=11, color=MUTED, anchor="start"))

    # низ — застереження про cos φ (довгота стискається)
    cy = 320
    p.append(line(50, cy, W-50, cy, color=MUTED, sw=1.0, dash="4,4"))
    p.append(fitbox(90, cy + 18, W-180, 70,
                    "УВАГА: 1° ДОВГОТИ коротшає з широтою — 1°λ ≈ 111.32 км × cos φ.\n"
                    "На φ = 50° cos φ ≈ 0.643 → 1°λ ≈ 71.6 км, крок 10⁻⁷° по довготі ≈ 7.2 мм.\n"
                    "Той самий int32 дає РІЗНИЙ метричний крок по широті й по довготі.",
                    size=12, fill=SKY_FILL, stroke=SKY_STK))
    render(os.path.join(OUT, "scale-ladder.svg"), W, H, *p)


# ── pvt-layout: байтова карта UBX-NAV-PVT зі зсувами й типами ─────────────────
# Ідея: двійкове повідомлення читається за ЗСУВАМИ; показати реальну розкладку
# ключових полів 92-байтового payload у вигляді таблиці (зсув · тип · поле ·
# одиниця), а окремо — розклад критичного байта flags по бітах. Без ліній-виносок
# крізь текст: кожен напис у своїй клітині.
def fig_pvt_layout():
    W, H = 780, 560
    p = []
    p.append(text(W/2, 30, "Байтова карта UBX-NAV-PVT: ключові поля за зсувами (payload 92 байти)", size=15, bold=True))

    # таблиця у дві колонки, щоб влізло без стискання
    # (offset, type, name, unit, fill-акцент)
    rows = [
        (0,  "u32", "iTOW",   "мс тижня",        CHIP_FILL),
        (4,  "6×",  "дата/час", "рік·міс·…·с UTC", TXT_FILL),
        (11, "u8",  "valid",  "біти дійсності",  BIN_STK),
        (20, "u8",  "fixType","0/2/3 (рівень)",  BIN_STK),
        (21, "u8",  "flags",  "gnssFixOK, carrSoln", BIN_STK),
        (23, "u8",  "numSV",  "супутників",      TXT_FILL),
        (24, "i32", "lon",    "10⁻⁷ градуса",    BIN_FILL),
        (28, "i32", "lat",    "10⁻⁷ градуса",    BIN_FILL),
        (32, "i32", "height", "мм (еліпсоїд)",   BIN_FILL),
        (36, "i32", "hMSL",   "мм (над морем)",  BIN_FILL),
        (40, "u32", "hAcc",   "мм, оцінка похибки", CHIP_FILL),
        (44, "u32", "vAcc",   "мм, по висоті",   CHIP_FILL),
        (48, "i32", "velN/E/D","мм/с по осях",   TXT_FILL),
        (60, "i32", "gSpeed", "мм/с (модуль)",   TXT_FILL),
        (64, "i32", "headMot","10⁻⁵° (курс руху)", TXT_FILL),
        (68, "u32", "sAcc",   "мм/с, похибка швид.", CHIP_FILL),
        (76, "u16", "pDOP",   "× 0.01 (геометрія)", BIN_STK),
    ]
    # заголовок таблиці
    col_x = [40, 400]        # x двох колонок
    cw = 340
    hy = 58
    rh = 25
    half = (len(rows) + 1) // 2
    for c in range(2):
        cx = col_x[c]
        p.append(rect(cx, hy, cw, rh, fill=FILL, stroke=LINE, sw=1.2, rx=4))
        p.append(text(cx + 8,  hy + 17, "зсув", size=11, color=MUTED, anchor="start", bold=True))
        p.append(text(cx + 58, hy + 17, "тип",  size=11, color=MUTED, anchor="start", bold=True))
        p.append(text(cx + 108,hy + 17, "поле", size=11, color=MUTED, anchor="start", bold=True))
        p.append(text(cx + 200,hy + 17, "що це", size=11, color=MUTED, anchor="start", bold=True))
    for i, (off, typ, name, unit, fl) in enumerate(rows):
        c = 0 if i < half else 1
        r = i if i < half else i - half
        cx = col_x[c]
        ry = hy + rh + r * rh
        p.append(rect(cx, ry, cw, rh, fill=fl, stroke=LINE, sw=0.8, rx=3))
        p.append(text(cx + 8,   ry + 17, str(off), size=11, color=INK, anchor="start"))
        p.append(text(cx + 58,  ry + 17, typ,      size=10.5, color=MUTED, anchor="start"))
        p.append(text(cx + 108, ry + 17, name,     size=11, color=INK, anchor="start", bold=True))
        p.append(text(cx + 200, ry + 17, unit,     size=10.5, color=INK, anchor="start"))

    table_bot = hy + rh + half * rh

    # окремо — розкладка байта flags (зсув 21) по бітах
    fy = table_bot + 30
    p.append(text(40, fy, "Байт flags (зсув 21) по бітах — тут «чи вірити рішенню»:", size=12, bold=True, anchor="start"))
    bits = [
        ("0",   "gnssFixOK", POS),
        ("1",   "diffSoln",  NEG),
        ("2-4", "psmState",  MUTED),
        ("5",   "headVehVal",MUTED),
        ("6-7", "carrSoln",  FIELD),
    ]
    bx = 40
    bw = 138
    for b, lab, col in bits:
        p.append(rect(bx, fy + 14, bw, 48, fill="#ffffff", stroke=col, sw=1.6, rx=4))
        p.append(text(bx + bw/2, fy + 33, "біт " + b, size=11, color=col, bold=True))
        p.append(text(bx + bw/2, fy + 52, lab, size=10.5, color=INK))
        bx += bw + 8

    # висновок
    p.append(fitbox(40, fy + 78, W - 80, 48,
                    "Читання = накласти struct і взяти поле за зсувом (числа little-endian, тож на ARM/ESP32 — як є).\n"
                    "fixType каже РІВЕНЬ фікса (2D/3D), а flags.gnssFixOK — чи це рішення взагалі валідне;\n"
                    "carrSoln (0/1/2) розрізняє звичайний фікс, float-RTK і fixed-RTK.",
                    size=11.5, fill=BIN_FILL, stroke=BIN_STK))
    render(os.path.join(OUT, "pvt-layout.svg"), W, H, *p)


# ── fletcher: чому XOR сліпий до перестановки, а сума Флетчера — ні ────────────
# Ідея: два різні порядки тих самих байтів дають ОДНАКОВИЙ XOR (сліпо),
# але РІЗНІ (a,b) Флетчера. Показати ручний прогін обох на двох порядках.
def fig_fletcher():
    W, H = 800, 420
    p = []
    p.append(text(W/2, 30, "Чому XOR сліпий до перестановки, а сума Флетчера — ні", size=15.5, bold=True))

    # два ряди байтів: оригінал і переставлений (обмін двох сусідів)
    seq_a = [0x01, 0x07, 0x10, 0x20]
    seq_b = [0x01, 0x07, 0x20, 0x10]   # обміняли останні два

    def hexs(v): return "%02X" % v

    # верх — XOR обох (однаковий)
    yx = 78
    p.append(text(50, yx, "XOR усіх байтів (наївна сума NMEA):", size=12.5, bold=True, anchor="start"))
    p.append(text(60, yx + 26, "порядок A: 01 ⊕ 07 ⊕ 10 ⊕ 20 = 36", size=12, color=INK, anchor="start"))
    p.append(text(60, yx + 48, "порядок B: 01 ⊕ 07 ⊕ 20 ⊕ 10 = 36", size=12, color=INK, anchor="start"))
    p.append(fitbox(560, yx - 6, 200, 44, "однаковий!\nперестановку НЕ спіймав",
                    size=11.5, fill="#fdecea", stroke=POS, bold=True))

    # низ — Флетчер обох (різний)
    yf = 190
    p.append(text(50, yf, "Сума Флетчера: a += байт;  b += a  (обидва mod 256):", size=12.5, bold=True, anchor="start"))

    # таблиця прогону для A
    def fletcher_table(x, title, seq, col):
        rows = ["крок  байт   a    b"]
        a = b = 0
        for v in seq:
            a = (a + v) & 0xFF
            b = (b + a) & 0xFF
            rows.append(" +%s   %3d  %3d" % (hexs(v), a, b))
        out = [text(x, yf + 26, title, size=12, color=col, bold=True, anchor="start")]
        for i, r in enumerate(rows):
            out.append(text(x, yf + 48 + i*20, r, size=11.5, color=INK, anchor="start"))
        return out, a, b

    ta, aa, ba = fletcher_table(60, "порядок A: 01 07 10 20", seq_a, NEG)
    tb, ab, bb = fletcher_table(440, "порядок B: 01 07 20 10", seq_b, FIELD)
    p += ta
    p += tb

    p.append(fitbox(60, yf + 160, 330, 34, "A → (a,b) = (%d, %d)" % (aa, ba),
                    size=12.5, fill=BIN_FILL, stroke=BIN_STK, bold=True))
    p.append(fitbox(440, yf + 160, 330, 34, "B → (a,b) = (%d, %d)  ≠  A" % (ab, bb),
                    size=12.5, fill=BIN_FILL, stroke=BIN_STK, bold=True))
    p.append(text(W/2, H - 14,
                  "b накопичує суму часткових сум → «пам'ятає» позицію байта; тому Флетчер ловить те, на що XOR сліпий",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "fletcher.svg"), W, H, *p)


# ── resync: граничні умови автомата — де він може збитися й як відновлюється ──
# Ідея: показати три пастки потокового парсера й реакцію на них: фальшива
# сигнатура всередині даних, брехлива довжина, обрив пачки (timeout).
def fig_resync():
    W, H = 820, 400
    p = []
    p.append(text(W/2, 30, "Граничні умови автомата: де він збивається й як відновлюється", size=15.5, bold=True))

    cases = [
        ("B5 62 всередині даних",
         "у payload трапилась пара\nB5 62 як звичайні байти",
         "довжина веде облік — автомат\nу стані GET_PAYLOAD НЕ шукає\nсигнатуру, лічить байти → не збивається",
         FIELD),
        ("брехлива довжина",
         "шум зіпсував поле length →\nвелетенське число (напр. 60000)",
         "перевірка len ≤ sizeof(buf):\nне влазить → скидання у WAIT_B5,\nчекаємо нову сигнатуру",
         POS),
        ("пачку обірвано",
         "модуль перезавантажився\nпосеред пакета — решта не прийде",
         "таймер міжбайтового простою:\nмовчання > T → скидання автомата,\nщоб напівпакет не завис навічно",
         NEG),
    ]
    cw = 250
    gap = 20
    x0 = (W - (3*cw + 2*gap)) / 2
    for i, (title, problem, fix, col) in enumerate(cases):
        x = x0 + i*(cw + gap)
        # заголовок
        p.append(fitbox(x, 62, cw, 38, title, size=13, fill="#ffffff", stroke=col, bold=True))
        # проблема
        p.append(fitbox(x, 112, cw, 66, problem, size=11.5, fill="#fdecea", stroke=POS))
        # стрілка вниз
        p.append(arrow(x + cw/2, 182, x + cw/2, 208, color=INK, sw=1.8))
        # розв'язок
        p.append(fitbox(x, 210, cw, 90, fix, size=11.5, fill=BIN_FILL, stroke=BIN_STK))

    p.append(fitbox(90, 322, W-180, 54,
                    "Спільний принцип: автомат ніколи не довіряє потоку сліпо. Довжина обмежена стелею буфера,\n"
                    "контрольна сума відкидає биті пакети, а таймер рятує від вічного зависання на обірваній пачці.\n"
                    "Будь-який збій → детермінований відкат у пошук сигнатури, без витоків стану.",
                    size=12, fill=SKY_FILL, stroke=SKY_STK))
    render(os.path.join(OUT, "resync.svg"), W, H, *p)


# ── cfg-ritual: стартовий ритуал налаштування модуля з ACK і зміною швидкості ─
# Ідея: показати послідовність CFG-команд, критичний момент зміни baud і те,
# що кожну команду треба ДОЧЕКАТИСЯ підтвердженням ACK-ACK (або ретрай на NAK).
def fig_cfg_ritual():
    W, H = 800, 430
    p = []
    p.append(text(W/2, 30, "Стартовий ритуал драйвера: налаштувати модуль і дочекатися ACK", size=15.5, bold=True))

    steps = [
        ("CFG-PRT", "порт UART:\n9600 → 115200 бод", "далі MCU сам\nговорить на 115200!", POS),
        ("CFG-MSG", "вимкнути всі NMEA,\nувімкнути NAV-PVT", "канал більше не\nмарнує байти на текст", FIELD),
        ("CFG-RATE", "measRate 100 мс\n→ 10 оновлень/с", "потрібний темп\nдля контуру", FIELD),
        ("CFG-GNSS", "GPS+Galileo+\nГЛОНАСС+BeiDou", "більше супутників\n→ менший pDOP", FIELD),
        ("CFG-CFG", "зберегти в flash\nмодуля", "після живлення\nне налаштовувати знов", NEG),
    ]
    n = len(steps)
    bw = 130
    gap = 18
    x0 = (W - (n*bw + (n-1)*gap)) / 2
    top = 76
    for i, (cmd, what, why, col) in enumerate(steps):
        x = x0 + i*(bw + gap)
        # команда
        p.append(fitbox(x, top, bw, 34, cmd, size=13, fill="#ffffff", stroke=col, bold=True))
        # що робить
        p.append(fitbox(x, top + 40, bw, 56, what, size=10.5, fill=CHIP_FILL, stroke=LINE))
        # → ACK
        p.append(arrow(x + bw/2, top + 100, x + bw/2, top + 124, color=POS, sw=1.6))
        p.append(fitbox(x, top + 126, bw, 30, "чекай ACK-ACK", size=10, fill=BIN_FILL, stroke=BIN_STK, bold=True))
        # чому
        p.append(fitbox(x, top + 162, bw, 52, why, size=10, fill=SKY_FILL, stroke=SKY_STK))
        # стрілка до наступного
        if i < n - 1:
            p.append(arrow(x + bw + 2, top + 17, x + bw + gap - 2, top + 17, color=INK, sw=1.6))

    # застереження про baud під першою колонкою
    p.append(fitbox(x0, top + 224, bw, 44, "ORDER-критично:\nзмінив швидкість —\nперемкнись і сам",
                    size=9.5, fill="#fdecea", stroke=POS, bold=True))

    p.append(fitbox(90, 358, W-180, 52,
                    "Кожна CFG-команда — не «вистрелив і забув»: модуль відповідає ACK-ACK на прийняту або ACK-NAK\n"
                    "на відкинуту. Драйвер чекає підтвердження з таймаутом і ретраєм; без ACK крок вважається невдалим.\n"
                    "Найтонше місце — зміна швидкості: після неї весь подальший діалог іде вже на новій швидкості.",
                    size=11.5, fill=SKY_FILL, stroke=SKY_STK))
    render(os.path.join(OUT, "cfg-ritual.svg"), W, H, *p)


# ══════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-ubx-driver: цілісний модуль драйвера — шари й ACK-очікування.
# ══════════════════════════════════════════════════════════════════════════════

# ── driver-layers: із чого складається драйвер як конвеєр ──────────────────────
# Ідея: показати драйвер не як «одну функцію», а як конвеєр шарів, кожен зі
# своєю відповідальністю: ISR складає байти в кільце → цикл згодовує їх автомату
# (сума Флетчера рахується на льоту) → декодер бере поля за зсувами через memcpy
# → ворота здоров'я пускають лише валідний свіжий фікс → оцінювач. Стрілка знизу —
# окремий канал старту: конфіг-ритуал по RX із очікуванням ACK.
def fig_driver_layers():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 30, "Драйвер GNSS як конвеєр шарів: від байта на дроті до довіреного фікса",
                  size=15, bold=True))

    # вертикальний стек шарів (кожен — широка смуга з роллю)
    lx, lw = 150, 520
    ly0 = 62
    lh = 58
    gap = 20
    layers = [
        ("1 · ISR UART → кільцевий буфер",
         "залізо складає прийняте саме; прошивку будить, коли є шматок", CHIP_FILL, LINE),
        ("2 · цикл: годуй автомат по байту",
         "ubx_feed(byte) — неблокуючий; сума Флетчера копиться на льоту", TXT_FILL, TXT_STK),
        ("3 · декодер NAV-PVT за зсувами",
         "memcpy кожного поля з буфера → без strict-aliasing і пакування", BIN_FILL, BIN_STK),
        ("4 · ворота здоров'я фікса",
         "fixType≥3 & gnssFixOK & numSV & pDOP & hAcc & свіжість", BIN_STK, POS),
    ]
    ys = []
    for i, (title, sub, fl, stk) in enumerate(layers):
        y = ly0 + i * (lh + gap)
        ys.append(y)
        p.append(rect(lx, y, lw, lh, fill=fl, stroke=stk, sw=1.8))
        p.append(text(lx + 14, y + 24, title, size=12.5, color=INK, anchor="start", bold=True))
        p.append(text(lx + 14, y + 44, sub, size=11, color=MUTED, anchor="start"))
        if i < len(layers) - 1:
            cxr = lx + lw / 2
            p.append(arrow(cxr, y + lh + 1, cxr, y + lh + gap - 1, color=INK, sw=1.8))

    # оцінювач унизу
    ey = ys[-1] + lh + gap
    p.append(arrow(lx + lw/2, ys[-1] + lh + 1, lx + lw/2, ey - 1, color=FIELD, sw=2.2))
    p.append(fitbox(lx + 90, ey, lw - 180, 36,
                    "оцінювач стану (фільтр Калмана) — злиття з IMU",
                    size=12.5, fill=BIN_FILL, stroke=BIN_STK, bold=True))

    # лівий канал: RX-старт (конфіг + ACK) — окрема стрілка вгору повз шари
    sx = 60
    p.append(fitbox(sx - 26, ly0, 96, lh, "СТАРТ:\nконфіг по RX",
                    size=11, fill="#ffffff", stroke=POS, bold=True))
    p.append(text(sx + 22, ly0 + lh + 26, "MON-VER →", size=10.5, color=MUTED))
    p.append(text(sx + 22, ly0 + lh + 42, "покоління?", size=10.5, color=MUTED))
    p.append(text(sx + 22, ly0 + lh + 70, "M8: CFG-PRT/", size=10, color=INK))
    p.append(text(sx + 22, ly0 + lh + 84, "MSG/RATE/GNSS", size=10, color=INK))
    p.append(text(sx + 22, ly0 + lh + 106, "M9/M10:", size=10, color=INK))
    p.append(text(sx + 22, ly0 + lh + 120, "CFG-VALSET", size=10, color=INK))
    p.append(text(sx + 22, ly0 + lh + 142, "чекай ACK", size=10.5, color=POS, bold=True))
    # стрілка від старту у шар 2 (модуль тепер шле NAV-PVT)
    p.append(arrow(sx + 70, ly0 + lh/2, lx - 2, ly0 + lh + gap + lh/2, color=POS, sw=1.6))

    p.append(text(W/2, H - 14,
                  "Кожен шар має одну відповідальність; збій на будь-якому не валить сусідні. Довіру дає лише шар 4.",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "driver-layers.svg"), W, H, *p)


# ── ack-wait: очікування ACK як автомат із таймаутом і ретраєм ────────────────
# Ідея: надіслати CFG — не «вистрелив і забув». Драйвер шле команду й крутить
# приймання, шукаючи ACK-ACK саме на цей class/id, поки не збіжить таймаут.
# ACK-ACK → далі; ACK-NAK → команда відкинута; таймаут → ретрай N разів, потім
# помилка. Показати три виходи й лічильник спроб.
def fig_ack_wait():
    W, H = 880, 400
    p = []
    p.append(text(W/2, 30, "Надіслати CFG і дочекатися: ACK-очікування з таймаутом і ретраєм",
                  size=15, bold=True))

    # центральний стан — «шлю й чекаю»
    cx, cy = W/2, 150
    p.append(fitbox(cx - 130, cy - 34, 260, 68,
                    "шлю CFG-команду →\nкручу приймання, ловлю ACK\nна цей class/id (таймер тікає)",
                    size=12, fill=CHIP_FILL, stroke=LINE, bold=True))

    # три виходи
    # ACK-ACK → успіх (праворуч)
    p.append(arrow(cx + 130, cy - 10, cx + 210, cy - 40, color=FIELD, sw=2.0))
    p.append(fitbox(cx + 214, cy - 62, 190, 44, "ACK-ACK →\nкрок ОК, далі",
                    size=12, fill=BIN_FILL, stroke=BIN_STK, bold=True))

    # ACK-NAK → відмова (праворуч нижче)
    p.append(arrow(cx + 130, cy + 10, cx + 210, cy + 40, color=POS, sw=2.0))
    p.append(fitbox(cx + 214, cy + 20, 190, 44, "ACK-NAK →\nкоманда відкинута",
                    size=12, fill="#fdecea", stroke=POS, bold=True))

    # таймаут → ретрай (петля ліворуч)
    p.append(arrow(cx - 130, cy + 22, cx - 214, cy + 60, color=NEG, sw=2.0))
    p.append(fitbox(cx - 404, cy + 40, 200, 48,
                    "таймаут (ACK не прийшов):\nретрай, поки спроб < N",
                    size=11.5, fill="#eaf0fd", stroke=NEG, bold=True))
    # петля назад у центр
    p.append(arrow(cx - 204 + 40, cy + 40, cx - 90, cy + 20, color=NEG, sw=1.4))

    # вичерпано спроби → помилка (ліворуч, нижче)
    p.append(arrow(cx - 304, cy + 88, cx - 304, cy + 120, color=POS, sw=1.8))
    p.append(fitbox(cx - 404, cy + 122, 200, 40,
                    "спроби вичерпано →\nстоп у помилку модуля",
                    size=11.5, fill="#fdecea", stroke=POS, bold=True))

    p.append(fitbox(90, H - 66, W - 180, 44,
                    "Причина, чому не можна слати наосліп: на 9600 бод старт-пакети легко губляться, а на неправильному\n"
                    "поколінні модуль відповість суцільним NAK. Підтвердження перетворює «сподіваюся, дійшло» на «знаю, що дійшло».",
                    size=11.5, fill=SKY_FILL, stroke=SKY_STK))
    render(os.path.join(OUT, "ack-wait.svg"), W, H, *p)


if __name__ == "__main__":
    fig_blackbox()
    fig_formats()
    fig_parser()
    fig_two_lineages()
    # детальна (-d):
    fig_scale_ladder()
    fig_pvt_layout()
    fig_fletcher()
    fig_resync()
    fig_cfg_ritual()
    # вставка proj-ubx-driver:
    fig_driver_layers()
    fig_ack_wait()
    print("OK figs ->", OUT)
