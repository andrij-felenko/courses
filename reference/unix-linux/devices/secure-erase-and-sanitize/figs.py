# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

CLEAN_FILL = "#dff0e6"     # свіжозаписане, чисте
OLD_FILL   = "#fbe6e3"     # старі дані, що вціліли
COLD_FILL  = "#dfe8fc"
WARM_FILL  = "#fff4e0"
WARM       = "#b8860b"


# ── 1. Куди дотягується запис через блоковий інтерфейс ─────────────────────
def fig_reach():
    W, H = 1460, 700
    p = []
    p.append(text(700, 42, "куди дотягується запис через блоковий інтерфейс",
                  size=18, bold=True, color=INK))

    BX, UW = 380, 34
    NL = 12

    # ── логічні номери
    p.append(text(350, 132, "логічні номери", size=15.5, bold=True, color=INK, anchor="end"))
    p.append(text(350, 156, "(усе, що бачить write)", size=13, color=MUTED, anchor="end"))
    for i in range(NL):
        p.append(rect(BX + i * UW, 108, UW, 54, fill=CLEAN_FILL, stroke=FIELD, sw=1.4, rx=2))
        p.append(text(BX + i * UW + UW / 2, 141, "0", size=13, color=FIELD))
    p.append(text(BX + NL * UW + 30, 141,
                  "після повного проходу нулями кожен читається нулем",
                  size=13.5, color=MUTED, anchor="start"))

    # ── межа досяжности
    p.append(line(70, 236, 1330, 236, color=MUTED, sw=1.2, dash="7,7"))
    p.append(text(70, 226, "нижче блоковий інтерфейс не має жодного імені",
                  size=13.5, bold=True, color=MUTED, anchor="start"))

    p.append(arrow(BX + NL * UW / 2, 168, BX + NL * UW / 2, 292, color=FIELD, sw=2))

    # ── фізичні сторінки: чотири класи, ширина пропорційна кількості
    p.append(text(350, 306, "фізичні сторінки", size=15.5, bold=True, color=INK, anchor="end"))

    rows = [
        (296, 12, CLEAN_FILL, FIELD, "дійсні сторінки",
         "нулі, що їх щойно поклав туди прохід запису"),
        (376, 4, OLD_FILL, POS, "недійсні сторінки",
         "старі дані цілі, доки блока не дійде збирання сміття"),
        (456, 3, OLD_FILL, POS, "запас понад заявлену місткість",
         "жодного логічного номера не мали ніколи"),
        (536, 1, OLD_FILL, POS, "виведені з обігу блоки",
         "вміст заморожено назавжди, відображення на них немає"),
    ]
    for y, n, fill, stroke, name, note in rows:
        for i in range(n):
            p.append(rect(BX + i * UW, y, UW, 54, fill=fill, stroke=stroke, sw=1.4, rx=2))
        p.append(text(350, y + 26, name, size=13.5, bold=True, color=INK, anchor="end"))
        p.append(text(BX + 12 * UW + 30, y + 32, note, size=13, color=MUTED, anchor="start"))

    p.append(fitbox(BX, 620, 480, 56,
                    ["стерти може лише той, хто бачить усі чотири ряди —",
                     "прошивка носія"],
                    size=13.5, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'reach.svg'), W, H, *p)


# ── 2. Три способи, якими прошивка стирає ──────────────────────────────────
def fig_three_ways():
    W, H = 1300, 700
    p = []
    p.append(text(W / 2, 42, "три способи, якими прошивка робить дані невідновними",
                  size=18, bold=True, color=INK))

    COLW, GAP, X0 = 380, 40, 60
    cols = [
        ("крипто-стирання", NEG, COLD_FILL,
         ["знищити ключ,", "яким шифрується вся медіа"],
         ["біти на чипах лишаються", "всі до одного —", "але стають шумом"],
         ["секунди"],
         ["уся ціна довіри —", "у прошивці: чи ключ був один", "і чи він справді зник"]),
        ("блокове стирання", FIELD, CLEAN_FILL,
         ["подати NAND-стирання", "на кожен фізичний блок"],
         ["дістає і запас,", "і недійсні сторінки —", "прошивка знає їх усі"],
         ["хвилини"],
         ["виведені блоки —", "на совісті прошивки:", "ззовні не перевірити"]),
        ("перезапис", POS, OLD_FILL,
         ["прошивка сама пише візерунок", "крізь усю медіа"],
         ["єдиний спосіб,", "що має сенс", "на магнітному диску"],
         ["години"],
         ["на флеші зношує ресурс,", "а до виведених блоків", "не дістає взагалі"]),
    ]

    for i, (name, col, fill, a, b, t, c) in enumerate(cols):
        x = X0 + i * (COLW + GAP)
        p.append(text(x + COLW / 2, 96, name, size=17, bold=True, color=col))
        p.append(fitbox(x, 116, COLW, 62, a, size=13.5, bold=True, fill=fill, stroke=col, sw=2))
        p.append(arrow(x + COLW / 2, 182, x + COLW / 2, 218, color=col, sw=1.8))
        p.append(fitbox(x, 222, COLW, 84, b, size=13.5, fill=FILL, stroke=MUTED, sw=1.5))
        p.append(fitbox(x + COLW / 2 - 80, 330, 160, 46, t, size=15, bold=True,
                        fill=fill, stroke=col, sw=1.8))
        p.append(fitbox(x, 400, COLW, 84, c, size=13, fill=WARM_FILL, stroke=WARM, sw=1.5))
        p.append(arrow(x + COLW / 2, 490, x + COLW / 2, 542, color=col, sw=1.8))

    p.append(fitbox(X0, 546, COLW * 3 + GAP * 2, 58,
                    ["жоден із трьох не є операцією над діапазоном блоків:",
                     "усі три — дії над носієм цілком"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=2))

    render(os.path.join(IMG, 'three-ways.svg'), W, H, *p)


# ── 3. Два шляхи команди в Linux ───────────────────────────────────────────
def fig_paths():
    W, H = 1320, 790
    p = []
    p.append(text(W / 2, 42, "два шляхи команди до носія", size=18, bold=True, color=INK))

    LX, RX, CW = 70, 690, 520
    p.append(line(645, 88, 645, 400, color=MUTED, sw=1.2, dash="7,7"))

    p.append(text(LX + CW / 2, 88, "звичайний шлях", size=16, bold=True, color=FIELD))
    p.append(text(RX + CW / 2, 88, "наскрізна команда", size=16, bold=True, color=POS))

    # ліва колонка
    p.append(fitbox(LX, 108, CW, 52, ["процес: write() · fstrim · blkdiscard"],
                    size=14, bold=True, fill=CLEAN_FILL, stroke=FIELD, sw=2))
    p.append(arrow(LX + CW / 2, 164, LX + CW / 2, 198, color=FIELD, sw=1.8))
    p.append(fitbox(LX, 202, CW, 52, ["файлова система · device mapper · RAID"],
                    size=14, fill=FILL, stroke=MUTED, sw=1.5))
    p.append(arrow(LX + CW / 2, 258, LX + CW / 2, 292, color=FIELD, sw=1.8))
    p.append(fitbox(LX, 296, CW, 74,
                    ["блоковий шар: REQ_OP_WRITE ·",
                     "REQ_OP_DISCARD · REQ_OP_SECURE_ERASE"],
                    size=13.5, fill=FILL, stroke=MUTED, sw=1.5))
    p.append(arrow(LX + CW / 2, 374, LX + CW / 2, 434, color=FIELD, sw=1.8))

    # права колонка
    p.append(fitbox(RX, 108, CW, 52, ["hdparm · sg_sanitize · nvme-cli"],
                    size=14, bold=True, fill=OLD_FILL, stroke=POS, sw=2))
    p.append(arrow(RX + CW / 2, 164, RX + CW / 2, 198, color=POS, sw=1.8))
    p.append(fitbox(RX, 202, CW, 74,
                    ["ioctl наскрізної команди:",
                     "SG_IO · NVME_IOCTL_ADMIN_CMD"],
                    size=13.5, bold=True, fill=OLD_FILL, stroke=POS, sw=2))
    p.append(arrow(RX + CW / 2, 280, RX + CW / 2, 434, color=POS, sw=2))
    p.append(mtext(RX + CW / 2 + 30, 340,
                   ["повз файлову систему,", "повз усі шари,", "повз блоковий шар"],
                   size=13, color=POS, anchor="start"))

    # спільний низ
    p.append(fitbox(LX, 438, 1140, 54, ["драйвер транспорту: libata · sd · nvme"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=2))
    p.append(arrow(LX + 570, 496, LX + 570, 532, color=LINE, sw=2))
    p.append(fitbox(LX, 536, 1140, 54, ["прошивка носія"],
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM, sw=2))
    p.append(arrow(LX + 570, 594, LX + 570, 630, color=LINE, sw=2))
    p.append(fitbox(LX, 634, 1140, 54, ["фізичні сторінки"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=2))

    p.append(fitbox(LX, 712, 1140, 60,
                    ["REQ_OP_SECURE_ERASE у блоковому шарі є, але реалізують його тільки mmc і xen-blkfront:",
                     "на SATA і NVMe команда blkdiscard --secure повертає «операція не підтримується»"],
                    size=13.5, fill=COLD_FILL, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'paths.svg'), W, H, *p)


# ── 4. Хронологія: коли ритуал народився і коли стандарти від нього пішли ──
def fig_timeline():
    W, H = 1420, 700
    p = []
    p.append(text(W / 2, 42, "ритуал і стандарти: тридцять років нарізно",
                  size=18, bold=True, color=INK))

    X0, X1 = 120, 1320
    AXY = 360
    p.append(line(X0, AXY, X1, AXY, color=LINE, sw=2))

    def px(year):
        return X0 + (year - 1994) * (X1 - X0) / 32.0

    # ряд «ритуал» — угору, ряд «стандарти» — униз
    up = [
        (1995, "NISPOM (DoD 5220.22-M)",
         ["перезапис символ → доповнення →", "випадковий; ніколи для Top Secret"]),
        (1996, "Ґутман, USENIX Security VI",
         ["35 проходів під MFM і RLL —", "по проходу на кожен код"]),
    ]
    down = [
        (2001, "зміна до NISPOM",
         ["перезапис прибрано"]),
        (2007, "матриця DSS",
         ["для магнітних носіїв лишились", "розмагнічення і руйнування"]),
        (2008, "Wright, Kleiman, Sundhar",
         ["вимір мікроскопом:", "біт — майже монетка"]),
        (2012, "ACS-2",
         ["SANITIZE як окрема", "операція над носієм"]),
        (2014, "NIST SP 800-88 r1",
         ["Clear · Purge · Destroy;", "жодних 35 проходів"]),
        (2025, "SP 800-88 r2",
         ["NVMe й самошифрувальні", "носії"]),
    ]

    p.append(text(X0 - 40, 96, "звідки взявся ритуал", size=15, bold=True,
                  color=POS, anchor="start"))
    p.append(text(X0 - 40, 640, "куди пішли стандарти", size=15, bold=True,
                  color=FIELD, anchor="start"))

    for i, (year, name, body) in enumerate(up):
        x = px(year)
        y = 130 + i * 96
        p.append(line(x, AXY - 8, x, y + 74, color=POS, sw=1.6, dash="5,5"))
        p.append(circle(x, AXY, 7, fill=OLD_FILL, stroke=POS, sw=2))
        p.append(text(x, AXY + 26, str(year), size=14, bold=True, color=POS))
        p.append(fitbox(x - 210, y, 420, 74, [name] + body, size=13,
                        fill=OLD_FILL, stroke=POS, sw=1.8))

    for i, (year, name, body) in enumerate(down):
        x = px(year)
        y = 430 + (i % 3) * 66
        p.append(line(x, AXY + 8, x, y, color=FIELD, sw=1.6, dash="5,5"))
        p.append(circle(x, AXY, 7, fill=CLEAN_FILL, stroke=FIELD, sw=2))
        p.append(text(x, AXY - 18, str(year), size=14, bold=True, color=FIELD))
        p.append(fitbox(x - 150, y, 300, 60, [name] + body, size=12.5,
                        fill=CLEAN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'erasure-timeline.svg'), W, H, *p)


# ── 5. Що показав мікроскоп: шанс відгадати попередній вміст ───────────────
def fig_recovery_odds():
    import math
    W, H = 1420, 640
    p = []
    p.append(text(W / 2, 40, "шанс відновити попередній вміст після ОДНОГО проходу",
                  size=18, bold=True, color=INK))
    p.append(text(W / 2, 68, "виміряно магнітно-силовим мікроскопом; Wright, Kleiman, Sundhar, 2008",
                  size=13.5, color=MUTED))

    rows = [
        ("1 біт", 0.92, 0.56, "0.92", "0.56"),
        ("8 бітів — один символ", 0.51321887, 0.0096721, "0.51", "0.0097"),
        ("32 біти — IP-адреса", 0.06937619, 8.75e-9, "0.069", "8.8·10⁻⁹"),
        ("64 біти", 0.00481306, 7.66e-17, "0.0048", "7.7·10⁻¹⁷"),
        ("128 бітів", 2.3166e-5, 5.86e-33, "2.3·10⁻⁵", "5.9·10⁻³³"),
        ("1024 біти — файл на кілобіт", 8.2934e-38, 1.4e-258, "8.3·10⁻³⁸", "1.4·10⁻²⁵⁸"),
    ]

    LX, CW = 60, 300
    C1, C2 = 400, 920
    BARW = 300

    p.append(text(C1 + 235, 116, "незайманий диск", size=15, bold=True, color=POS, anchor="end"))
    p.append(text(C2 + 235, 116, "уживаний диск", size=15, bold=True, color=FIELD, anchor="end"))
    p.append(text(C1 + 235, 138, "(записаний уперше в житті)", size=12.5, color=MUTED, anchor="end"))
    p.append(text(C2 + 235, 138, "(півроку в щоденній роботі)", size=12.5, color=MUTED, anchor="end"))

    def bar(v):
        s = (40.0 + math.log10(v)) / 40.0
        return max(3.0, min(1.0, max(0.0, s)) * BARW)

    y = 176
    for name, a, b, sa, sb in rows:
        p.append(text(LX, y + 22, name, size=14, color=INK, anchor="start"))
        p.append(rect(C1, y, bar(a), 34, fill=OLD_FILL, stroke=POS, sw=1.6, rx=3))
        p.append(text(C1 + 470, y + 22, sa, size=13.5, bold=True, color=POS, anchor="end"))
        p.append(rect(C2, y, bar(b), 34, fill=CLEAN_FILL, stroke=FIELD, sw=1.6, rx=3))
        p.append(text(C2 + 470, y + 22, sb, size=13.5, bold=True, color=FIELD, anchor="end"))
        y += 62

    p.append(fitbox(LX, y + 16, 1300, 58,
                    ["довжина стовпчика — за логарифмом: уся шкала від одиниці до 10⁻⁴⁰;",
                     "на диску 2006 року найкраще відгадування дало 49.18 % — гірше за підкидання монетки"],
                    size=13.5, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'recovery-odds.svg'), W, H, *p)


# ── 6. Звідки береться відсоток: дані проти регістрів ─────────────────────
def fig_status_paths():
    W, H = 1560, 640
    p = []
    p.append(text(W / 2, 40, "звідки береться відсоток виконаного",
                  size=18, bold=True, color=INK))

    LX, RX, CW = 60, 840, 660

    p.append(line(770, 76, 770, 500, color=MUTED, sw=1.2, dash="7,7"))

    p.append(text(LX + CW / 2, 84, "NVMe: окрема сторінка журналу",
                  size=16, bold=True, color=FIELD))
    p.append(text(RX + CW / 2, 84, "ATA через SG_IO: регістри повернення",
                  size=16, bold=True, color=POS))

    # ── рядок A: команда
    p.append(fitbox(LX, 104, CW, 58,
                    ["Get Log Page · opcode 02h", "LID 81h · 512 байтів даних"],
                    size=13.5, bold=True, fill=CLEAN_FILL, stroke=FIELD, sw=2))
    p.append(fitbox(RX, 104, CW, 58,
                    ["ATA PASS-THROUGH (16) · CDB[0] = 85h",
                     "CDB[14] = B4h · FEATURE = 0000h"],
                    size=13.5, bold=True, fill=OLD_FILL, stroke=POS, sw=2))

    p.append(arrow(LX + CW / 2, 168, LX + CW / 2, 204, color=FIELD, sw=1.8))
    p.append(arrow(RX + CW / 2, 168, RX + CW / 2, 204, color=POS, sw=1.8))

    # ── рядок B: чим приходить відповідь
    p.append(fitbox(LX, 208, CW, 66,
                    ["контролер кладе сторінку в буфер,",
                     "який виділили ви — звичайні дані"],
                    size=13.5, fill=FILL, stroke=MUTED, sw=1.5))
    p.append(fitbox(RX, 208, CW, 66,
                    ["протокол Non-data: жодного байта даних;",
                     "регістри віддає лише CK_COND = 1 — у sense-буфері"],
                    size=13.5, fill=FILL, stroke=MUTED, sw=1.5))

    p.append(arrow(LX + CW / 2, 280, LX + CW / 2, 314, color=FIELD, sw=1.8))
    p.append(arrow(RX + CW / 2, 280, RX + CW / 2, 314, color=POS, sw=1.8))

    # ── рядок C: розкладка байтів
    lcells = [("0:1", "SPROG", True), ("2:3", "SSTAT", True),
              ("4:7", "SCDW10", False), ("8:31", "оцінки часу", False),
              ("32:511", "резерв", False)]
    lw = CW / len(lcells)
    for i, (rng, name, hot) in enumerate(lcells):
        p.append(fitbox(LX + i * lw, 318, lw - 6, 68, [rng, name], size=12.5,
                        bold=hot, fill=CLEAN_FILL if hot else FILL,
                        stroke=FIELD if hot else MUTED, sw=1.8 if hot else 1.3))

    rcells = [("0", "09h", False), ("1", "0Ch", False), ("3", "ERROR", False),
              ("4", "COUNT hi", True), ("7 · 9", "LBA lo · mid", True),
              ("13", "STATUS", False)]
    rw = CW / len(rcells)
    for i, (rng, name, hot) in enumerate(rcells):
        p.append(fitbox(RX + i * rw, 318, rw - 6, 68, [rng, name], size=12.5,
                        bold=hot, fill=OLD_FILL if hot else FILL,
                        stroke=POS if hot else MUTED, sw=1.8 if hot else 1.3))

    # ── рядок D: що з цього рахують
    p.append(fitbox(LX, 404, CW, 76,
                    ["стан = SSTAT біти 2:0",
                     "відсоток = SPROG · 100 / 65536"],
                    size=13.5, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(fitbox(RX, 404, CW, 76,
                    ["стан = біти 7:4 байта COUNT (15:8)",
                     "відсоток = (LBA_MID·256 + LBA_LOW) · 100 / 65535"],
                    size=13.5, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8))

    p.append(fitbox(LX, 520, CW * 2 + 120, 62,
                    ["запитання те саме — «скільки вже зроблено»;",
                     "різниця лише в тому, чи має транспорт канал для даних, чи самі регістри"],
                    size=14, bold=True, fill=FILL, stroke=LINE, sw=2))

    render(os.path.join(IMG, 'status-paths.svg'), W, H, *p)


fig_reach()
fig_three_ways()
fig_paths()
fig_timeline()
fig_recovery_odds()
fig_status_paths()
print("ok")
