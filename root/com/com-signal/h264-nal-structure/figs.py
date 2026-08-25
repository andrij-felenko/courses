# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#fdecea"
BLUE  = "#eaf0fd"
GREEN = "#e8f6ec"
GRAY  = "#e6e8eb"
YELL  = "#fdf3d8"


# ── nal-header: один байт заголовка й приклади реальних байтів ────────────────
# Ідея: три поля в одному байті — 1 + 2 + 5 бітів; за одним байтом видно тип.

def fig_nal_header():
    W, H = 800, 440
    p = []

    p.append(text(50, 34, "один байт на початку кожної NAL-одиниці",
                  size=12, color=MUTED, anchor="start", italic=True))

    x0, y0, cw, ch = 50, 56, 56, 48
    groups = [(0, 1, RED, POS, "1 біт"),
              (1, 3, BLUE, NEG, "2 біти"),
              (3, 8, GREEN, FIELD, "5 бітів")]
    for a, b, fill, stroke, lab in groups:
        gx = x0 + a * cw
        gw = (b - a) * cw
        p.append(rect(gx, y0, gw, ch, fill=fill, stroke=stroke, sw=1.8, rx=5))
        p.append(text(gx + gw / 2, y0 + ch / 2 + 5, lab, size=13, color=INK, bold=True))
    # поділки бітів — короткі риски по верхньому краю, далеко від написів
    for i in range(1, 8):
        p.append(line(x0 + i * cw, y0, x0 + i * cw, y0 + 10, color=MUTED, sw=1.0))
    # номери бітів під смугою
    for i in range(8):
        p.append(text(x0 + i * cw + cw / 2, y0 + ch + 18, str(7 - i), size=10, color=MUTED))

    # ── легенда полів (кольором, без ліній-виносок) ───────────────────────────
    rows = [(RED, POS,   "forbidden_zero_bit — має бути 0; одиниця означає пошкодження"),
            (BLUE, NEG,  "nal_ref_idc — 0: неопорна одиниця, 1…3: опорна (тим важливіша)"),
            (GREEN, FIELD, "nal_unit_type — номер типу, 0…31: що саме лежить усередині")]
    ry = 158
    for fill, stroke, s in rows:
        p.append(rect(50, ry - 13, 18, 18, fill=fill, stroke=stroke, sw=1.6, rx=3))
        p.append(text(80, ry + 1, s, size=12, color=INK, anchor="start"))
        ry += 34

    # ── приклади байтів ───────────────────────────────────────────────────────
    px, py, pw, ph = 50, 272, 700, 148
    p.append(rect(px, py, pw, ph, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(px + 20, py + 26, "приклади байтів із реального потоку",
                  size=12, color=MUTED, anchor="start", italic=True))
    ex = [("0x67", "0 · 11 · 00111", "тип 7 — SPS"),
          ("0x65", "0 · 11 · 00101", "тип 5 — слайс IDR-кадру"),
          ("0x41", "0 · 10 · 00001", "тип 1 — слайс, опорний"),
          ("0x01", "0 · 00 · 00001", "тип 1 — слайс, неопорний")]
    ey = py + 54
    for a, b, c in ex:
        p.append(text(px + 20, ey, a, size=13, color=INK, bold=True, anchor="start"))
        p.append(text(px + 110, ey, b, size=13, color=NEG, anchor="start"))
        p.append(text(px + 300, ey, c, size=13, color=INK, anchor="start"))
        ey += 26

    render(os.path.join(OUT, "nal-header.svg"), W, H, *p,
           title="Байт заголовка NAL-одиниці: три поля в одному байті")


# ── emulation-prevention: захисний байт 0x03 і його оборотність ───────────────
# Ідея: кодувальник уставляє 0x03, декодер його викидає — трійка 00 00 01
# усередині вантажу стає неможливою, а перетворення лишається оборотним.

def _byterow(x, y, bw, bh, cells, p):
    for i, (s, fill, stroke) in enumerate(cells):
        bx = x + i * (bw + 6)
        p.append(fitbox(bx, y, bw, bh, s, size=15, fill=fill, stroke=stroke, sw=1.6, bold=True))


def fig_emulation_prevention():
    W, H = 720, 330
    p = []
    bw, bh, bx = 54, 42, 210

    lab_x = 40
    p.append(text(lab_x, 66, "до кодування", size=12, color=MUTED, anchor="start"))
    _byterow(bx, 44, bw, bh, [("4A", FILL, LINE), ("00", FILL, LINE), ("00", FILL, LINE),
                              ("01", YELL, "#c9a227"), ("7C", FILL, LINE)], p)

    p.append(text(lab_x, 156, "у потоці", size=12, color=MUTED, anchor="start"))
    _byterow(bx, 134, bw, bh, [("4A", FILL, LINE), ("00", FILL, LINE), ("00", FILL, LINE),
                               ("03", RED, POS), ("01", YELL, "#c9a227"), ("7C", FILL, LINE)], p)

    p.append(text(lab_x, 246, "після декодування", size=12, color=MUTED, anchor="start"))
    _byterow(bx, 224, bw, bh, [("4A", FILL, LINE), ("00", FILL, LINE), ("00", FILL, LINE),
                               ("01", YELL, "#c9a227"), ("7C", FILL, LINE)], p)

    ax = bx + 3 * (bw + 6)
    p.append(arrow(ax, 92, ax, 128, color=POS, sw=1.8))
    p.append(text(ax + 14, 114, "уставити 0x03", size=12, color=POS, anchor="start"))
    p.append(arrow(ax, 182, ax, 218, color=NEG, sw=1.8))
    p.append(text(ax + 14, 204, "викинути 0x03", size=12, color=NEG, anchor="start"))

    p.append(text(40, 300, "трійка 00 00 01 усередині вантажу стає неможливою — і перетворення оборотне",
                  size=12, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "emulation-prevention.svg"), W, H, *p,
           title="Захисний байт 0x03: уставляння й вилучення")


# ── annexb-vs-avcc: два пакування тих самих одиниць ───────────────────────────
# Ідея: у потоці межі шукають скануванням стартових кодів і параметри
# повторюють; у файлі межа — довжина, а параметри винесені в опис доріжки.

def fig_annexb_vs_avcc():
    W, H = 800, 440
    p = []

    p.append(text(200, 40, "Annex B — потік", size=14, color=INK, bold=True))
    p.append(text(600, 40, "MP4 — довжини", size=14, color=INK, bold=True))

    # ліва колонка
    lx, lw = 60, 280
    items = [("00 00 00 01", 22, GRAY, MUTED),
             ("SPS", 36, GREEN, FIELD),
             ("00 00 00 01", 22, GRAY, MUTED),
             ("PPS", 36, GREEN, FIELD),
             ("00 00 01", 22, GRAY, MUTED),
             ("слайс IDR-кадру", 46, RED, POS),
             ("00 00 01", 22, GRAY, MUTED),
             ("слайс звичайного кадру", 46, BLUE, NEG)]
    y = 70
    for s, h, fill, stroke in items:
        p.append(fitbox(lx, y, lw, h, s, size=13, fill=fill, stroke=stroke, sw=1.5))
        y += h + 8
    p.append(text(lx + lw / 2, y + 16, "межу шукають скануванням", size=11, color=MUTED, italic=True))

    # права колонка
    rx, rw = 460, 280
    p.append(rect(rx, 70, rw, 74, fill=YELL, stroke="#c9a227", sw=1.6, rx=6))
    p.append(mtext(rx + rw / 2, 96, ["avcC — опис доріжки, поза потоком",
                                     "SPS · PPS · довжина префікса = 4"],
                   size=12, color=INK, lh=1.5))

    y = 176
    p.append(text(rx + rw / 2, y - 12, "далі — самі кадри:", size=11, color=MUTED, italic=True))
    for s, h, fill, stroke, ln in [("слайс IDR-кадру", 46, RED, POS, "00 00 0A 3B"),
                                   ("слайс звичайного кадру", 46, BLUE, NEG, "00 00 04 C2")]:
        p.append(fitbox(rx, y, 120, 22, ln, size=12, fill=GRAY, stroke=MUTED, sw=1.4))
        p.append(fitbox(rx, y + 28, rw, h, s, size=13, fill=fill, stroke=stroke, sw=1.5))
        y += h + 44
    p.append(text(rx + rw / 2, y + 8, "межу читають із префікса", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "annexb-vs-avcc.svg"), W, H, *p,
           title="Annex B і MP4: два пакування тих самих NAL-одиниць")


# ── param-set-chain: подвійне посилання слайс → PPS → SPS ────────────────────
# Ідея: кадр не описує себе, а називає номер набору; кілька легких PPS
# спираються на один важкий SPS.

def fig_param_set_chain():
    W, H = 800, 340
    p = []

    p.append(text(150, 34, "заголовки слайсів", size=13, color=INK, bold=True))
    p.append(text(420, 34, "PPS", size=13, color=INK, bold=True))
    p.append(text(680, 34, "SPS", size=13, color=INK, bold=True))

    slices = [(60, "слайс кадру A\npic_parameter_set_id = 0"),
              (190, "слайс кадру B\npic_parameter_set_id = 1")]
    for y, s in slices:
        p.append(fitbox(45, y, 210, 72, s, size=12, fill=BLUE, stroke=NEG, sw=1.5))

    ppss = [(52, "PPS 0\nCABAC · базовий QP 26"),
            (182, "PPS 1\nCABAC · базовий QP 32")]
    for y, s in ppss:
        p.append(fitbox(315, y, 210, 88, s, size=12, fill=GREEN, stroke=FIELD, sw=1.5))

    p.append(fitbox(585, 96, 190, 110,
                    "SPS 0\n1920×1080 · 4:2:0\n4 опорні кадри\nпрофіль 100, рівень 4.0",
                    size=12, fill=YELL, stroke="#c9a227", sw=1.6))

    p.append(arrow(258, 96, 312, 96, color=INK, sw=1.6))
    p.append(arrow(258, 226, 312, 226, color=INK, sw=1.6))
    p.append(arrow(528, 96, 582, 130, color=INK, sw=1.6))
    p.append(arrow(528, 226, 582, 178, color=INK, sw=1.6))

    p.append(text(45, 306, "кадр не описує себе — він називає номер набору; набір називає номер наступного",
                  size=12, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "param-set-chain.svg"), W, H, *p,
           title="Ланцюг посилань: слайс → PPS → SPS")


# ── access-unit: потік, розділений на одиниці доступу ─────────────────────────
# Ідея: одиниця доступу — усі NAL-одиниці одного кадру; набори параметрів
# повторюють перед точкою входу, щоб приймач міг увійти будь-де.

def fig_access_unit():
    W, H = 800, 240
    p = []
    p.append(text(40, 42, "потік Annex B", size=12, color=MUTED, anchor="start", italic=True))

    au1 = [("AUD", 56, GRAY, MUTED, "тип 9"),
           ("SPS", 60, GREEN, FIELD, "тип 7"),
           ("PPS", 60, GREEN, FIELD, "тип 8"),
           ("SEI", 56, GRAY, MUTED, "тип 6"),
           ("слайс", 92, RED, POS, "тип 5"),
           ("слайс", 92, RED, POS, "тип 5")]
    au2 = [("AUD", 56, GRAY, MUTED, "тип 9"),
           ("слайс", 88, BLUE, NEG, "тип 1"),
           ("слайс", 88, BLUE, NEG, "тип 1")]

    x = 40
    y, h = 92, 48
    bounds = []
    for group in (au1, au2):
        start = x
        for s, w, fill, stroke, t in group:
            p.append(fitbox(x, y, w, h, s, size=13, fill=fill, stroke=stroke, sw=1.5))
            p.append(text(x + w / 2, y - 12, t, size=10, color=MUTED))
            x += w + 6
        bounds.append((start, x - 6))
        x += 26

    labels = ["одиниця доступу — кадр із точкою входу", "одиниця доступу — звичайний кадр"]
    for (a, b), lab in zip(bounds, labels):
        p.append(line(a, 158, b, 158, color=INK, sw=1.4))
        p.append(line(a, 152, a, 158, color=INK, sw=1.4))
        p.append(line(b, 152, b, 158, color=INK, sw=1.4))
        p.append(text((a + b) / 2, 180, lab, size=11, color=INK))

    p.append(text(40, 216, "тип видно за одним байтом — розбирати вміст не треба",
                  size=12, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "access-unit.svg"), W, H, *p,
           title="Одиниці доступу в потоці Annex B")


# ── nal-timeline: дорога від зрощених із транспортом кодеків до NAL ───────────
# Ідея (для вставки hist-nal-layer): до 2001-го кожен стандарт мав «свій» дріт;
# JVT відрізав транспорт від відео, після чого транспорт переписували окремо.

def fig_nal_timeline():
    W, H = 1080, 400
    p = []
    p.append(text(40, 34, "хто до чого був прив'язаний і коли це розчепили",
                  size=12, color=MUTED, anchor="start", italic=True))

    AX = 200
    p.append(line(50, AX, 1030, AX, color=MUTED, sw=1.6))

    marks = [
        ("1990", ["H.261", "канал ISDN, p×64 кбіт/с"],            GRAY,  MUTED),
        ("1995", ["MPEG-2 + Transport Stream", "пакет 188 байтів"], GRAY,  MUTED),
        ("1996", ["H.263", "мультиплекс H.223 у H.324"],           GRAY,  MUTED),
        ("1998", ["виклик VCEG на H.26L", "мета — удвічі менший потік"], YELL, "#b8860b"),
        ("1999", ["перший чорновик", "модель TML"],                YELL,  "#b8860b"),
        ("12.2001", ["створено Joint Video Team", "у меті — network friendliness"], GREEN, FIELD),
        ("05.2003", ["H.264 = ISO/IEC 14496-10", "два рівні: VCL і NAL"], GREEN, FIELD),
        ("02.2005", ["RFC 3984", "пакування NAL у RTP"],           BLUE,  NEG),
        ("05.2011", ["RFC 6184", "переписаний, відео те саме"],    BLUE,  NEG),
    ]

    x0, step = 100, 108
    for i, (year, lines, fill, stroke) in enumerate(marks):
        x = x0 + i * step
        p.append(circle(x, AX, 8, fill=fill, stroke=stroke, sw=1.8))
        up = (i % 2 == 0)
        ys = [96, 120, 144] if up else [256, 280, 304]
        p.append(text(x, ys[0], year, size=12, color=INK, bold=True))
        for k, s in enumerate(lines):
            p.append(text(x, ys[k + 1], s, size=10, color=MUTED))

    p.append(text(50, 372, "сірі роки — кодек і транспорт росли одним шматком;   "
                           "зелені — рік, коли їх розділили;   "
                           "сині — транспорт, дописаний потім, без правки відео",
                  size=11, color=INK, anchor="start", italic=True))

    render(os.path.join(OUT, "nal-timeline.svg"), W, H, *p,
           title="Від кодеків, зрощених із транспортом, до поділу VCL/NAL")


# ── avcc-layout: avcDecoderConfigurationRecord байт за байтом ────────────────
# Ідея: сталі шість байтів, далі повторювані блоки; два байти пакують поля
# не по байтовій межі — саме на них ламаються саморобні розбирачі.

def fig_avcc_layout():
    W, H = 960, 500
    p = []

    p.append(text(40, 30, "avcDecoderConfigurationRecord — те, що в MP4 лежить "
                          "замість SPS і PPS у самому потоці",
                  size=12, color=MUTED, anchor="start", italic=True))

    x0, bw, gap, bh = 40, 145, 8, 60

    def col(i):
        return x0 + i * (bw + gap)

    # ── сталі шість байтів ──────────────────────────────────────────────────
    yA = 66
    fixed = [
        ("0", "configurationVersion\n= 1",                GREEN),
        ("1", "AVCProfileIndication\nprofile_idc з SPS",  BLUE),
        ("2", "profile_compatibility\nбайт прапорців",    BLUE),
        ("3", "AVCLevelIndication\nlevel_idc з SPS",      BLUE),
        ("4", "111111 +\nlengthSizeMinusOne",             YELL),
        ("5", "111 +\nчисло наборів SPS",                 YELL),
    ]
    for i, (off, s, fill) in enumerate(fixed):
        p.append(text(col(i) + bw / 2, yA - 10, "байт " + off, size=10, color=MUTED))
        p.append(fitbox(col(i), yA, bw, bh, s, size=11, fill=fill))

    # ── змінна частина ──────────────────────────────────────────────────────
    yB = 190
    p.append(text(col(0) + bw + gap / 2, yB - 10,
                  "повторюється для кожного SPS", size=10, color=MUTED))
    p.append(text(col(3) + bw + gap / 2, yB - 10,
                  "повторюється для кожного PPS", size=10, color=MUTED))

    varying = [
        ("довжина SPS\n2 байти, старший перший", GRAY),
        ("байти SPS\nпочинаються з 0x67",        GREEN),
        ("число наборів PPS\nцілий байт",        YELL),
        ("довжина PPS\n2 байти",                 GRAY),
        ("байти PPS\nпочинаються з 0x68",        GREEN),
        ("хвіст: формат кольору\nй глибини бітів", RED),
    ]
    for i, (s, fill) in enumerate(varying):
        p.append(fitbox(col(i), yB, bw, bh, s, size=11, fill=fill))

    p.append(text(col(5) + bw / 2, yB + bh + 18,
                  "лише для профілів 100, 110, 122, 144", size=10, color=MUTED))

    # ── два байти, розібрані побітово ───────────────────────────────────────
    yC, cw, cg, chh = 320, 48, 5, 42
    p.append(text(40, yC - 10, "байт 4 побітово", size=11, color=INK,
                  anchor="start", bold=True))
    p.append(text(500, yC - 10, "байт 5 побітово", size=11, color=INK,
                  anchor="start", bold=True))

    def bits(bx, n_res, tail):
        out = []
        for k in range(n_res):
            out.append(fitbox(bx + k * (cw + cg), yC, cw, chh, "1",
                              size=15, fill=GRAY, color=MUTED))
        wide = (8 - n_res) * cw + (7 - n_res) * cg
        out.append(fitbox(bx + n_res * (cw + cg), yC, wide, chh, tail,
                          size=11, fill=YELL))
        return out

    p += bits(40, 6, "lengthSize\nMinusOne")
    p += bits(500, 3, "numOfSequence\nParameterSets")

    p.append(mtext(40, yC + chh + 26,
                   ["шість старших бітів — резерв, усі одиниці",
                    "0 → префікс 1 байт · 1 → 2 байти · 3 → 4 байти"],
                   size=11, color=INK, anchor="start"))
    p.append(mtext(500, yC + chh + 26,
                   ["три старші біти — резерв, усі одиниці",
                    "до 31 набору; на практиці рівно один"],
                   size=11, color=INK, anchor="start"))

    p.append(text(40, 470, "байти 4 і 5 — єдине місце запису, де поля не збігаються "
                           "з байтовою межею; саме на них ламаються саморобні розбирачі",
                  size=11, color=INK, anchor="start", italic=True))

    render(os.path.join(OUT, "avcc-layout.svg"), W, H, *p,
           title="Розкладка avcDecoderConfigurationRecord")


# ── допоміжне: клітинка байта ────────────────────────────────────────────────

def _cell(p, x, y, w, h, label, fill=FILL, stroke=LINE, size=13):
    p.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4))
    p.append(text(x + w / 2, y + h / 2 + size * 0.36, label, size=size, color=INK, bold=True))


# ── start-code-scan: автомат сканера й розбір реальної низки байтів ───────────
# Ідея: лічильник нулів — і є весь стан; назад по буферу вертатися не треба.

def fig_start_code_scan():
    W, H = 880, 390
    p = []

    p.append(text(50, 30, "сканер стартових кодів: один байт — один перехід, назад не вертаємось",
                  size=12, color=MUTED, anchor="start", italic=True))

    # ── ряд станів ───────────────────────────────────────────────────────────
    cy = 104
    xs = [130, 350, 570, 790]
    st_lbl = ["нулів: 0", "нулів: 1", "нулів: ≥2", "стартовий код"]
    st_fill = [FILL, BLUE, BLUE, GREEN]
    st_line = [LINE, NEG, NEG, FIELD]
    bw, bh = 150, 40
    for x, s, f, ln in zip(xs, st_lbl, st_fill, st_line):
        _cell(p, x - bw / 2, cy - bh / 2, bw, bh, s, fill=f, stroke=ln, size=13)

    for i, lab in enumerate(["байт 00", "байт 00", "байт 01"]):
        a = xs[i] + bw / 2 + 8
        b = xs[i + 1] - bw / 2 - 8
        p.append(arrow(a, cy, b, cy, color=INK, sw=1.8))
        p.append(text((a + b) / 2, cy - 14, lab, size=11, color=INK))

    # ── повернення в перший стан ─────────────────────────────────────────────
    p.append(line(570, cy + bh / 2 + 2, 570, 160, color=MUTED, sw=1.4, dash="5,4"))
    p.append(line(570, 160, 130, 160, color=MUTED, sw=1.4, dash="5,4"))
    p.append(arrow(130, 160, 130, cy + bh / 2 + 3, color=MUTED, sw=1.4))
    p.append(text(350, 151, "будь-який інший байт — лічильник у нуль",
                  size=11, color=MUTED))

    # ── низка байтів і стан після кожного ────────────────────────────────────
    seq = ["7C", "00", "00", "03", "01", "9A", "00", "00", "00", "01", "67"]
    cnt = ["0", "1", "2", "0", "0", "0", "1", "2", "3", "межа", "0"]
    hl = {3: (YELL, "#b8860b"), 9: (GREEN, FIELD), 10: (BLUE, NEG)}
    bx, by, cw, ch = 70, 214, 68, 40
    for i, s in enumerate(seq):
        f, ln = hl.get(i, (FILL, LINE))
        _cell(p, bx + i * cw, by, cw, ch, s, fill=f, stroke=ln, size=13)
        col = FIELD if cnt[i] == "межа" else MUTED
        p.append(text(bx + i * cw + cw / 2, by + ch + 20, cnt[i],
                      size=11, color=col, bold=(cnt[i] == "межа")))

    # ── дужки: що вантаж, а що вже стартовий код ─────────────────────────────
    gy = by + ch + 42
    spans = [(0, 6, "вантаж попередньої одиниці"),
             (6, 10, "стартовий код — усі три нулі його"),
             (10, 11, "далі")]
    for a, b, lab in spans:
        x1 = bx + a * cw + 3
        x2 = bx + b * cw - 3
        p.append(line(x1, gy, x2, gy, color=MUTED, sw=1.2))
        p.append(line(x1, gy, x1, gy + 6, color=MUTED, sw=1.2))
        p.append(line(x2, gy, x2, gy + 6, color=MUTED, sw=1.2))
        p.append(text((x1 + x2) / 2, gy + 22, lab, size=11, color=INK))

    p.append(text(70, gy + 52, "байт 03 усередині вантажу лічильник скидає — і 01 після нього межею не стає",
                  size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "start-code-scan.svg"), W, H, *p,
           title="Сканер стартових кодів: лічильник нулів і є весь стан")


# ── unescape-inplace: зняття захисних байтів поверх джерела ──────────────────
# Ідея: записувач ніколи не випереджає читача, тому копія не потрібна.

def fig_unescape_inplace():
    W, H = 840, 340
    p = []

    src = ["41", "9A", "00", "00", "03", "01", "D4", "7F"]
    dst = ["41", "9A", "00", "00", "01", "D4", "7F"]
    x0, cw, ch = 80, 80, 44

    p.append(text(x0, 84, "у потоці (EBSP)", size=12, color=MUTED,
                  anchor="start", italic=True))
    sy = 100
    for i, s in enumerate(src):
        f, ln = (RED, POS) if i == 4 else (FILL, LINE)
        _cell(p, x0 + i * cw, sy, cw, ch, s, fill=f, stroke=ln, size=14)

    p.append(text(x0, 216, "після зняття (RBSP)", size=12, color=MUTED,
                  anchor="start", italic=True))
    dy = 232
    for i, s in enumerate(dst):
        f, ln = (GREEN, FIELD) if i == 4 else (FILL, LINE)
        _cell(p, x0 + i * cw, dy, cw, ch, s, fill=f, stroke=ln, size=14)

    # ── читач ────────────────────────────────────────────────────────────────
    rx = x0 + 5 * cw + cw / 2
    p.append(text(rx, 58, "читач r", size=11, color=POS, bold=True))
    p.append(arrow(rx, 66, rx, sy - 4, color=POS, sw=1.8))

    # ── записувач ────────────────────────────────────────────────────────────
    wx = x0 + 4 * cw + cw / 2
    p.append(text(wx, 310, "записувач w", size=11, color=NEG, bold=True))
    p.append(arrow(wx, 300, wx, dy + ch + 4, color=NEG, sw=1.8))

    p.append(text(x0 + 4 * cw + cw / 2, 186, "захисний байт 03 у вихід не йде",
                  size=11, color=POS))

    render(os.path.join(OUT, "unescape-inplace.svg"), W, H, *p,
           title="Зняття захисних байтів просто в буфері: w ніколи не випереджає r")


if __name__ == "__main__":
    fig_nal_timeline()
    fig_nal_header()
    fig_emulation_prevention()
    fig_annexb_vs_avcc()
    fig_param_set_chain()
    fig_access_unit()
    fig_avcc_layout()
    fig_start_code_scan()
    fig_unescape_inplace()
    print("ok")
