# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f2f3f5"
RED   = "#fdecea"


# ── 1. Чергування: чому одиницею є набір планок ───────────────────────────────
def fig_interleave_region():
    W, H = 1260, 630
    p = []

    p.append(text(W / 2, 44, "чотири планки, зведені прошивкою в один набір чергування",
                  size=15, bold=True, color=INK))

    tints = [COOL, WARM, GREEN, GREY]
    accents = [NEG, POS, FIELD, MUTED]
    BX, BW, BY, BH = [70, 360, 650, 940], 250, 70, 88
    for i in range(4):
        p.append(fitbox(BX[i], BY, BW, BH,
                        "планка %d\nвласні адреси всередині планки" % i,
                        size=13, fill=tints[i], stroke=accents[i], sw=1.8))
        p.append(arrow(BX[i] + BW / 2, BY + BH + 6, BX[i] + BW / 2, 236,
                       color=accents[i], sw=2))

    p.append(fitbox(70, 244, 1120, 74,
                    "контролер пам'яті: кожні кілька сотень байтів адрес переходять на наступну планку",
                    size=13.5, fill="#ffffff", stroke=INK, sw=1.8))
    p.append(arrow(630, 324, 630, 386, color=INK, sw=2.2))

    SX, SY, SH, N = 70, 394, 56, 24
    SW_ = 1120.0 / N
    for i in range(N):
        k = i % 4
        p.append(rect(SX + i * SW_, SY, SW_, SH, fill=tints[k], stroke=accents[k], sw=1.2, rx=2))
        p.append(text(SX + i * SW_ + SW_ / 2, SY + SH / 2 + 5, str(k),
                      size=13, color=MUTED))

    p.append(text(W / 2, SY + SH + 32,
                  "один суцільний діапазон системних фізичних адрес — це і є область",
                  size=13.5, bold=True, color=INK))

    p.append(mtext(W / 2, SY + SH + 78,
                   ["виймеш одну планку — нечитабельним стає весь діапазон, а не його чверть:",
                    "будь-яка структура даних розмазана по всіх чотирьох"],
                   size=12.5, color=POS))

    render(os.path.join(OUT, "interleave-region.svg"), W, H, *p)


# ── 2. Ланцюг найменування: де живе кожен рівень знання ───────────────────────
def fig_naming_chain():
    W = 1360
    LX, LW = 50, 250
    MX, MW = 330, 520
    RX, RW = 880, 430
    TOP, STEP, BH = 92, 106, 86
    H = TOP + STEP * 4 + BH + 92

    rows = [
        ("таблиця NFIT",
         "які діапазони фізичних адрес постійні\nі з яких планок кожен складений",
         "прошивка платформи:\nскладається наново при кожному вмиканні",
         COOL, NEG),
        ("область",
         "один набір чергування —\nодин суцільний діапазон адрес",
         "ядро будує з NFIT:\nживе лише в пам'яті ядра",
         COOL, NEG),
        ("мітки в планках",
         "кому належить кожен відрізок місткості\nі в якому він режимі",
         "окрема пам'ять на самій планці:\nпереживає навіть переїзд в іншу машину",
         GREEN, FIELD),
        ("простір імен",
         "відрізок місткості з власним UUID,\nрежимом і геометрією",
         "ядро збирає з міток\nпри кожному завантаженні",
         WARM, POS),
        ("файл пристрою",
         "/dev/pmem0 або /dev/dax0.0 —\nте, що відкриває програма",
         "створює udev:\nзникає разом із вимкненням",
         GREY, MUTED),
    ]

    p = []
    p.append(text(LX + LW / 2, 62, "рівень", size=14, bold=True, color=INK))
    p.append(text(MX + MW / 2, 62, "що на ньому відомо", size=14, bold=True, color=INK))
    p.append(text(RX + RW / 2, 62, "де це записано", size=14, bold=True, color=INK))

    for i, (lvl, know, where, tint, accent) in enumerate(rows):
        y = TOP + STEP * i
        cy = y + BH / 2
        p.append(fitbox(LX, y, LW, BH, lvl, size=13.5, bold=True,
                        fill="#ffffff", stroke=accent, sw=1.8))
        p.append(fitbox(MX, y, MW, BH, know, size=12.5, fill=tint, stroke=accent, sw=1.8))
        p.append(fitbox(RX, y, RW, BH, where, size=12, fill=SOFT, stroke=MUTED, sw=1.6))
        if i < len(rows) - 1:
            p.append(arrow(LX + LW / 2, y + BH + 4, LX + LW / 2, y + STEP - 4,
                           color=MUTED, sw=2))

    p.append(mtext(W / 2, TOP + STEP * 4 + BH + 52,
                   ["лише один рядок цього ланцюга зберігається на самому залізі —",
                    "і саме тому поділ місткості переживає геть усе інше"],
                   size=13, color=FIELD))

    render(os.path.join(OUT, "naming-chain.svg"), W, H, *p)


# ── 3. Режими простору імен ───────────────────────────────────────────────────
def fig_namespace_modes():
    W = 1320
    LX, LW = 50, 190
    MX, MW = 270, 400
    RX, RW = 700, 570
    TOP, STEP, BH = 90, 112, 92
    H = TOP + STEP * 3 + BH + 74

    rows = [
        ("fsdax", "блоковий /dev/pmem0",
         "файлова система, а на ній — пряме звертання до вмісту;\n"
         "частина місткості або DRAM іде під описувачі сторінок",
         GREEN, FIELD),
        ("devdax", "символьний /dev/dax0.0",
         "рівно одне відображення, вирівняне під великі сторінки;\n"
         "ні файлової системи, ні розділів, ні звичайного read",
         COOL, NEG),
        ("sector", "блоковий /dev/pmem0s",
         "сектор оновлюється цілком або ніяк — через таблицю переадресації;\n"
         "саме через неї пряме звертання тут неможливе",
         WARM, POS),
        ("raw", "блоковий /dev/pmem0\nбез службового блоку",
         "сумісність із чужими інструментами й іншими системами;\n"
         "описувачів сторінок немає, отже, немає й прямого звертання",
         GREY, MUTED),
    ]

    p = []
    p.append(text(LX + LW / 2, 60, "режим", size=14, bold=True, color=INK))
    p.append(text(MX + MW / 2, 60, "що з'являється", size=14, bold=True, color=INK))
    p.append(text(RX + RW / 2, 60, "що дає — і чим платиш", size=14, bold=True, color=INK))

    for i, (mode, dev, what, tint, accent) in enumerate(rows):
        y = TOP + STEP * i
        p.append(fitbox(LX, y, LW, BH, mode, size=15, bold=True,
                        fill="#ffffff", stroke=accent, sw=1.8))
        p.append(fitbox(MX, y, MW, BH, dev, size=13, fill=tint, stroke=accent, sw=1.8))
        p.append(fitbox(RX, y, RW, BH, what, size=12.5, fill=SOFT, stroke=MUTED, sw=1.6))

    p.append(text(W / 2, TOP + STEP * 3 + BH + 42,
                  "режим записано в мітці, тож він переживає перезавантаження разом із даними",
                  size=13, color=INK))

    render(os.path.join(OUT, "namespace-modes.svg"), W, H, *p)


# ── 4. Збійна комірка: коду помилки повернути нікуди ──────────────────────────
def fig_media_error():
    W, H = 1320, 690
    p = []

    LX, RX, CW = 60, 700, 560
    p.append(text(LX + CW / 2, 52, "звичайний накопичувач", size=14.5, bold=True, color=NEG))
    p.append(text(RX + CW / 2, 52, "постійна пам'ять", size=14.5, bold=True, color=POS))

    ys = [84, 190, 296, 402]
    BH = 84

    left = [
        ("програма кличе read()", COOL, NEG),
        ("контролер носія натрапляє на биту ділянку", GREY, MUTED),
        ("помилка їде назад тим самим шляхом,\nяким ішов запит", COOL, NEG),
        ("read() повертає EIO —\nзвичайна гілка коду, яку всі пишуть", GREEN, FIELD),
    ]
    right = [
        ("процесор виконує mov із відображення", WARM, POS),
        ("контролер пам'яті натрапляє на биту комірку", GREY, MUTED),
        ("повертати код нікуди: інструкція завантаження\nне має місця під помилку", RED, POS),
        ("machine check → SIGBUS процесові,\nа з контексту ядра — значно гірше", RED, POS),
    ]

    for col_x, items in ((LX, left), (RX, right)):
        for i, (txt, tint, accent) in enumerate(items):
            p.append(fitbox(col_x, ys[i], CW, BH, txt, size=12.5,
                            fill=tint, stroke=accent, sw=1.8))
            if i < len(items) - 1:
                p.append(arrow(col_x + CW / 2, ys[i] + BH + 4,
                               col_x + CW / 2, ys[i + 1] - 4, color=MUTED, sw=2))

    p.append(fitbox(60, 528, 1200, 104,
                    "єдиний захист — знати заздалегідь: команда прошивки обходить діапазон і повідомляє відомі збійні адреси,\n"
                    "ядро тримає їх у списку badblocks — і блоковий шар віддає EIO, а обробник помилки сторінки\n"
                    "відмовляє у відображенні ще до того, як процесор торкнеться комірки",
                    size=12.5, fill=GREEN, stroke=FIELD, sw=1.8))

    render(os.path.join(OUT, "media-error.svg"), W, H, *p)




# ---- 5. Хронологія: залізо, стандарт, ядро, ринок ----
def fig_nvdimm_timeline():
    W, H = 1320, 940
    p = []
    J = lambda *xs: chr(10).join(xs)

    p.append(text(W / 2, 42, "три різні речі, які легко сплутати в одну: залізо, папір, код",
                  size=15, bold=True, color=INK))

    lanes = [("залізо на ринку", POS, RED),
             ("стандарт на папері", NEG, COOL),
             ("код у ядрі Linux", FIELD, GREEN)]
    LW = 390
    for i, (name, accent, tint) in enumerate(lanes):
        p.append(fitbox(70 + i * (LW + 15), 72, LW, 48, name,
                        size=13.5, fill=tint, stroke=accent, sw=1.8))

    rows = [
        ("2008-2014", 0, J("планки з DRAM, флешем і суперконденсатором: NVvault, AGIGARAM, ArxCis-NV",
                           "у кожного виробника своя утиліта й свій спосіб описати себе системі")),
        ("квітень 2015", 1, J("ACPI 6.0 вносить таблицю NFIT: прошивка нарешті вміє сказати ядру,",
                              "які діапазони адрес постійні та з яких планок складені")),
        ("квітень 2015", 1, J("NVDIMM Namespace Specification 1.0 фіксує формат міток —",
                              "як поділ місткості зберігає своє ім'я на самій планці")),
        ("травень 2015", 1, J("JEDEC JC-45 ухвалює перші стандарти гібридних модулів DDR4:",
                              "NVDIMM-N і NVDIMM-F; NVDIMM-P як протокол виходить аж 2020-2021")),
        ("червень 2015", 2, J("ядро 4.1: драйвер pmem віддає блоковим пристроєм діапазон,",
                              "який людина сама вирізала з карти пам'яті параметром memmap=")),
        ("серпень 2015", 2, J("ядро 4.2: підсистема libnvdimm (серія Dan Williams, Intel) —",
                              "планки, області, мітки й простори імен як дерево пристроїв")),
        ("липень 2016", 2, J("ядро 4.7: device-dax — той самий діапазон віддається не файловою",
                             "системою, а окремим символьним пристроєм без блокового шару")),
        ("травень 2017", 1, J("UEFI 2.7 забирає протокол міток до себе: формат стає спільним",
                              "для прошивки й операційної системи, а не приватним для Linux")),
        ("травень 2019", 2, J("ядро 5.1: dax_kmem віддає діапазон розподільникові сторінок —",
                              "місткість стає вузлом NUMA, у якого є пам'ять і немає процесора")),
        ("травень 2022", 2, J("ядро 5.18: гілку BLK з блоковими вікнами викидають —",
                              "сім років коду під залізо, яке так і не вийшло на ринок")),
        ("2022-2023", 0, J("Intel згортає Optane, а серію 300 скасовує з 31 січня 2023 —",
                           "масових планок постійної пам'яті на ринку більше немає")),
    ]

    TOP, RH, GAP = 148, 62, 9
    for i, (when, lane, txt) in enumerate(rows):
        y = TOP + i * (RH + GAP)
        accent, tint = lanes[lane][1], lanes[lane][2]
        p.append(fitbox(70, y, 200, RH, when, size=13, fill="#ffffff", stroke=MUTED, sw=1.5))
        p.append(fitbox(290, y, 960, RH, txt, size=12.5, fill=tint, stroke=accent, sw=1.8))

    yb = TOP + len(rows) * (RH + GAP) + 18
    p.append(fitbox(70, yb, 1180, 62,
                    J("папір випереджав залізо, а ядро йшло за папером —",
                      "тому в ньому роками жив драйвер, для якого не існувало жодної планки"),
                    size=13, fill=SOFT, stroke=INK, sw=1.8))

    render(os.path.join(OUT, "nvdimm-timeline.svg"), W, H, *p)


# ---- 6. Безпечна точка: чому return з обробника не рятує (вставка proj) ----
def fig_safe_point():
    W, H = 1370, 706
    LX, LW = 70, 530
    RX, RW = 740, 550
    TOP, STEP, BH = 90, 100, 76
    p = []

    p.append(text(LX + LW / 2, 58, "повернення з обробника",
                  size=14.5, bold=True, color=POS))
    p.append(text(RX + RW / 2, 58, "стрибок у безпечну точку",
                  size=14.5, bold=True, color=FIELD))

    left = [
        "memcpy читає з відображення",
        "бита комірка → SIGBUS:\nядро вставляє кадр обробника",
        "обробник запам'ятав адресу\nй зробив return",
        "ядро відновило кадр\nі повторює ТУ САМУ інструкцію",
    ]
    right = [
        "sigsetjmp(env, 1): точка й маска\nсигналів запам'ятані, повернуто 0",
        "memcpy читає з відображення",
        "бита комірка → SIGBUS: обробник зберіг\nsi_addr, si_code, si_addr_lsb",
        "siglongjmp(env, 1)",
        "та сама перевірка повертає 1 — інша гілка:\nрозчистити відрізок і читати далі",
    ]

    for i, s in enumerate(left):
        y = TOP + STEP * i
        p.append(fitbox(LX, y, LW, BH, s, size=12.5, fill=RED, stroke=POS, sw=1.8))
        if i < len(left) - 1:
            p.append(arrow(LX + LW / 2, y + BH + 4, LX + LW / 2, y + STEP - 4,
                           color=MUTED, sw=2))

    for i, s in enumerate(right):
        y = TOP + STEP * i
        tint = WARM if i == 2 else GREEN
        p.append(fitbox(RX, y, RW, BH, s, size=12.5, fill=tint, stroke=FIELD, sw=1.8))
        if i < len(right) - 1:
            p.append(arrow(RX + RW / 2, y + BH + 4, RX + RW / 2, y + STEP - 4,
                           color=MUTED, sw=2))

    lb = TOP + STEP * 3 + BH                      # низ четвертої коробки ліворуч
    p.append(line(LX + LW / 2, lb + 4, LX + LW / 2, lb + 42, color=POS, sw=2))
    p.append(line(LX + LW / 2, lb + 42, 30, lb + 42, color=POS, sw=2))
    p.append(line(30, lb + 42, 30, TOP + BH / 2, color=POS, sw=2))
    p.append(arrow(30, TOP + BH / 2, LX - 4, TOP + BH / 2, color=POS, sw=2))
    p.append(text(LX + LW / 2, lb + 78,
                  "та сама інструкція: програма жива й зовсім нерухома",
                  size=13, bold=True, color=POS))

    jy = TOP + STEP * 3 + BH / 2                  # середина четвертої коробки праворуч
    p.append(line(RX + RW + 4, jy, 1340, jy, color=FIELD, sw=2, dash="7,5"))
    p.append(line(1340, jy, 1340, TOP + BH / 2, color=FIELD, sw=2, dash="7,5"))
    p.append(arrow(1340, TOP + BH / 2, RX + RW + 4, TOP + BH / 2, color=FIELD, sw=2))
    p.append(text(RX + RW / 2, TOP + STEP * 4 + BH + 38,
                  "інструкція, що не виконалася, не виконується вже ніколи",
                  size=13, bold=True, color=FIELD))

    p.append(mtext(W / 2, H - 48,
                   ["різниця не в тому, куди потрапляє керування,",
                    "а в тому, що бита адреса більше не читається"],
                   size=13, color=INK))

    render(os.path.join(OUT, "safe-point.svg"), W, H, *p)


fig_interleave_region()
fig_naming_chain()
fig_namespace_modes()
fig_media_error()
fig_nvdimm_timeline()
fig_safe_point()
print("ok")
