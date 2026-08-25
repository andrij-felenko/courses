# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f2f3f5"


# ── 1. Два шляхи до того самого байта ─────────────────────────────────────────
def fig_two_paths():
    W, H = 1240, 700
    p = []

    LX, RX, CW = 70, 690, 430
    ys = [110, 240, 370, 500]
    BH = 74

    p.append(text(LX + CW / 2, 60, "звичайний носій: обмін блоками", size=15, bold=True, color=INK))
    p.append(text(RX + CW / 2, 60, "постійна пам'ять: обмін байтами", size=15, bold=True, color=INK))

    left = [
        ("буфер програми", "власна пам'ять процесу", COOL, NEG),
        ("сторінка кешу сторінок", "друга копія вмісту в оперативній пам'яті", WARM, POS),
        ("черга запитів блокового пристрою", "запит на блок, передача через DMA", WARM, POS),
        ("носій: блоки по 4096 байтів", "окремий байт узяти неможливо", GREY, MUTED),
    ]
    for i, (head, sub, tint, accent) in enumerate(left):
        y = ys[i]
        p.append(rect(LX, y, CW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(LX + CW / 2, y + 30, head, size=13, bold=True, color=INK))
        p.append(text(LX + CW / 2, y + 52, sub, size=10.5, color=MUTED))

    gaps = [
        "копіювання в межах пам'яті",
        "читання або запис цілого блоку",
        "поїздка до пристрою: мікросекунди",
    ]
    for i, lab in enumerate(gaps):
        y0, y1 = ys[i] + BH, ys[i + 1]
        p.append(arrow(LX + 60, y0 + 8, LX + 60, y1 - 8, color=MUTED, sw=2))
        p.append(text(LX + 78, (y0 + y1) / 2 + 4, lab, size=10.5, color=MUTED, anchor="start"))

    right = [
        ("буфер програми або відображення", "власна пам'ять процесу", COOL, NEG),
        ("кеш сторінок тут не виникає", "другої копії вмісту в пам'яті немає", SOFT, MUTED),
        ("черга блокових запитів не потрібна", "жодного запиту до пристрою не йде", SOFT, MUTED),
        ("носій: адресується байтами", "процесор читає його інструкцією mov", GREEN, FIELD),
    ]
    for i, (head, sub, tint, accent) in enumerate(right):
        y = ys[i]
        dash = "6 5" if i in (1, 2) else None
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
                 'stroke="%s" stroke-width="1.8"%s/>'
                 % (RX, y, CW, BH, tint, accent, ' stroke-dasharray="6 5"' if dash else ''))
        p.append(text(RX + CW / 2, y + 30, head, size=13, bold=True,
                      color=INK if i in (0, 3) else MUTED))
        p.append(text(RX + CW / 2, y + 52, sub, size=10.5, color=MUTED))

    p.append(arrow(640, ys[0] + BH + 8, 640, ys[3] + 30, color=FIELD, sw=2.6))
    p.append(mtext(624, 330, ["запис у таблиці сторінок", "веде просто на носій"],
                   size=11, color=FIELD, anchor="end"))

    p.append(text(W / 2, 648, "ліворуч вміст лежить у пам'яті двічі; праворуч — жодного разу",
                  size=12, color=INK))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p)


# ── 2. Де саме починається довговічність ──────────────────────────────────────
def fig_persistence_domain():
    W, H = 1300, 520
    p = []

    BX = [50, 370, 690, 1010]
    BW, BY, BH = 240, 170, 96

    stages = [
        ("інструкція store", "запис у відображення", COOL, NEG),
        ("кеш процесора", "зникає з живленням", WARM, POS),
        ("черга контролера пам'яті", "переживе зникнення живлення", GREEN, FIELD),
        ("комірки носія", "остаточне місце даних", GREEN, FIELD),
    ]
    for i, (head, sub, tint, accent) in enumerate(stages):
        p.append(rect(BX[i], BY, BW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(BX[i] + BW / 2, BY + 42, head, size=13.5, bold=True, color=INK))
        p.append(text(BX[i] + BW / 2, BY + 66, sub, size=10.5, color=MUTED))

    arrows = [
        ["сама лише", "інструкція"],
        ["CLWB або", "нетемпоральний store"],
        ["далі — без участі", "програми"],
    ]
    for i, lab in enumerate(arrows):
        x0, x1 = BX[i] + BW, BX[i + 1]
        p.append(arrow(x0 + 6, BY + BH / 2, x1 - 6, BY + BH / 2, color=INK, sw=2.2))
        p.append(mtext((x0 + x1) / 2, BY - 34, lab, size=11, color=INK))

    p.append(line(BX[0], 316, BX[1] + BW, 316, color=POS, sw=2.4))
    p.append(mtext((BX[0] + BX[1] + BW) / 2, 346,
                   ["летюче: усе, що не пішло далі,", "зникає разом із живленням"],
                   size=12, color=POS))

    p.append(line(BX[2], 316, BX[3] + BW, 316, color=FIELD, sw=2.4))
    p.append(mtext((BX[2] + BX[3] + BW) / 2, 346,
                   ["захищений домен: живлення зникло —", "вміст черги все одно дійде до комірок"],
                   size=12, color=FIELD))

    p.append(mtext(W / 2, 434,
                   ["межа між двома половинами і є справжнім моментом «записано»;",
                    "SFENCE потрібен, щоб знати, що попередні CLWB уже перетнули цю межу"],
                   size=12, color=INK))

    render(os.path.join(OUT, "persistence-domain.svg"), W, H, *p)


# ── 3. Чому знадобився MAP_SYNC ───────────────────────────────────────────────
def fig_map_sync():
    W, H = 1300, 700
    p = []

    p.append(fitbox(390, 40, 520, 62,
                    "запис у ще не виділену ділянку відображення →\nпомилка сторінки, керування переходить до ядра",
                    size=12.5, fill=COOL, stroke=NEG, sw=1.8))

    LX, RX, CW = 60, 700, 540
    p.append(text(LX + CW / 2, 148, "звичайне відображення", size=14.5, bold=True, color=POS))
    p.append(text(RX + CW / 2, 148, "MAP_SYNC | MAP_SHARED_VALIDATE", size=14.5, bold=True, color=FIELD))

    ys = [178, 292, 406, 520]
    BH = 78

    left = [
        ("файлова система виділяє блок під запис", GREY, MUTED),
        ("зміна метаданих лягає в журнал у пам'яті", WARM, POS),
        ("ядро віддає керування програмі одразу", WARM, POS),
        ("живлення зникло: байти на носії є,\nа файл про свій новий блок не знає", "#fdecea", POS),
    ]
    right = [
        ("файлова система виділяє блок під запис", GREY, MUTED),
        ("журнал доводиться до носія тут-таки", GREEN, FIELD),
        ("лише тепер ядро віддає керування", GREEN, FIELD),
        ("живлення зникло: усе, що програма\nвстигла скинути, лишилося на місці", "#eafaf0", FIELD),
    ]

    for col_x, items in ((LX, left), (RX, right)):
        for i, (txt, tint, accent) in enumerate(items):
            p.append(fitbox(col_x, ys[i], CW, BH, txt, size=12.5,
                            fill=tint, stroke=accent, sw=1.8))
            if i < len(items) - 1:
                p.append(arrow(col_x + CW / 2, ys[i] + BH + 4,
                               col_x + CW / 2, ys[i + 1] - 4, color=MUTED, sw=2))

    p.append(arrow(500, 108, 300, ys[0] - 6, color=NEG, sw=2))
    p.append(arrow(800, 108, 1000, ys[0] - 6, color=NEG, sw=2))

    p.append(text(W / 2, 648,
                  "різниця лише в тому, коли ядро вважає помилку сторінки залагодженою",
                  size=12.5, color=INK))

    render(os.path.join(OUT, "map-sync.svg"), W, H, *p)


# ── 4. Смуга часу: від xip до dax ─────────────────────────────────────────────
def fig_timeline():
    rows = [
        ("червень 2005\nядро 2.6.13", "Carsten Otte (IBM) додає ext2 параметр -o xip:\nкод виконується просто з адресованого носія на s390", WARM),
        ("2006 — 2013", "код лишається без догляду: лише ext2, лише читання,\nа в дереві вже три різні речі під назвою XIP", GREY),
        ("жовтень 2014", "Matthew Wilcox переписує механізм і перейменовує на DAX:\nакцент із виконання коду зміщено на доступ до даних", COOL),
        ("квітень 2015\nядро 4.0", "DAX для ext4", GREEN),
        ("серпень 2015\nядро 4.2", "DAX для XFS", GREEN),
        ("січень 2018\nядро 4.15", "MAP_SYNC і MAP_SHARED_VALIDATE: метадані доводяться\nдо носія ще в обробнику помилки сторінки", COOL),
        ("серпень 2020\nядро 5.8", "тристанний dax=always|inode|never й позначка FS_XFLAG_DAX\nна файлі (серії Ira Weiny для ext4 і XFS)", COOL),
        ("липень 2022", "Intel згортає Optane — єдину масову планку постійної пам'яті;\nDAX лишається в ядрі й дістає virtiofs та erofs", SOFT),
    ]

    W = 1180
    TOP, STEP, BH = 56, 96, 74
    H = TOP + STEP * (len(rows) - 1) + BH + 46
    p = []

    SPINE = 330
    p.append(line(SPINE, TOP - 18, SPINE, TOP + STEP * (len(rows) - 1) + BH + 10,
                  color=MUTED, sw=2.5))

    for i, (when, what, tint) in enumerate(rows):
        y = TOP + STEP * i
        cy = y + BH / 2
        p.append(fitbox(50, y + 8, 236, BH - 16, when, size=13, fill="#ffffff",
                        stroke=MUTED, sw=1.6))
        p.append(circle(SPINE, cy, 8, fill=tint, stroke=INK, sw=2))
        p.append(line(SPINE + 10, cy, SPINE + 40, cy, color=MUTED, sw=1.6))
        p.append(fitbox(SPINE + 44, y, W - SPINE - 94, BH, what, size=13,
                        fill=tint, stroke=INK, sw=1.6))

    render(os.path.join(OUT, "xip-to-dax-timeline.svg"), W, H, *p)


# ── 5. Порядок фіксації запису й вікна аварії ─────────────────────────────────
def fig_commit_order():
    W, H = 1340, 706
    p = []

    LX, RX, CW = 60, 720, 560
    BH, STEP = 70, 88
    ys = [96 + STEP * i for i in range(6)]

    p.append(text(LX + CW / 2, 60, "порядок дій під час додавання запису",
                  size=14.5, bold=True, color=INK))
    p.append(text(RX + CW / 2, 60, "що побачить перевірка, якщо аварія сталася тут",
                  size=14.5, bold=True, color=INK))

    steps = [
        ("1. звичайні store: тіло, довжина, контрольна сума", COOL, NEG),
        ("2. CLWB на кожен рядок кешу під тілом", COOL, NEG),
        ("3. SFENCE: чекаємо, поки виштовхування дійдуть", GREEN, FIELD),
        ("4. один вирівняний 8-байтовий store ознаки", WARM, POS),
        ("5. CLWB на рядок з ознакою", COOL, NEG),
        ("6. SFENCE: запис зафіксовано остаточно", GREEN, FIELD),
    ]
    for i, (txt, tint, accent) in enumerate(steps):
        p.append(fitbox(LX, ys[i], CW, BH, txt, size=13,
                        fill=tint, stroke=accent, sw=1.8))
        if i < len(steps) - 1:
            p.append(arrow(LX + 44, ys[i] + BH + 3, LX + 44, ys[i + 1] - 3,
                           color=MUTED, sw=2))

    zones = [
        (ys[0], ys[2] + BH, GREY, MUTED,
         "ознаки немає — слот при відновленні пропускається,\n"
         "журнал лишається таким, яким був до додавання"),
        (ys[3], ys[3] + BH, "#eafaf0", FIELD,
         "8 байтів, вирівняних і в одному рядку кешу: на носії\n"
         "буде або старий нуль, або нове слово цілком"),
        (ys[4], ys[5] + BH, GREY, MUTED,
         "ознака могла ще не перетнути межу домену —\n"
         "це той самий безпечний випадок «запису не було»"),
    ]
    for y0, y1, tint, accent, txt in zones:
        p.append(fitbox(RX, y0, CW, y1 - y0, txt, size=12.5,
                        fill=tint, stroke=accent, sw=1.8))
        p.append(line(LX + CW + 14, (y0 + y1) / 2, RX - 14, (y0 + y1) / 2,
                      color=MUTED, sw=1.6, dash="5 5"))

    p.append(mtext(W / 2, 650,
                   ["небезпечний порядок — виставити ознаку раніше, ніж тіло перетне межу домену:",
                    "тоді відновлення повірить у запис, тіла якого на носії немає"],
                   size=12.5, color=POS))

    render(os.path.join(OUT, "commit-order.svg"), W, H, *p)


# ── 6. Шари й важелі: де саме вмикають пряме звертання ────────────────────────
def fig_dax_stack():
    W = 1240
    LX, LW = 60, 300
    RX, RW = 410, 770
    TOP, STEP, BH = 76, 108, 88
    H = TOP + STEP * 4 + BH + 76

    rows = [
        ("виклик mmap()",
         "MAP_SHARED_VALIDATE | MAP_SYNC\n"
         "без MAP_SHARED_VALIDATE прапорець MAP_SYNC мовчки ігнорується",
         COOL, NEG),
        ("inode файлу",
         "постійна позначка FS_XFLAG_DAX (0x00008000)\n"
         "ставлять: xfs_io -c 'chattr +x' · chattr +x · FS_IOC_FSSETXATTR",
         COOL, NEG),
        ("змонтована ext4 або XFS",
         "параметр монтування dax=always | dax=inode | dax=never\n"
         "діючий стан S_DAX читають через statx: STATX_ATTR_DAX",
         GREEN, FIELD),
        ("простір імен на пристрої",
         "ndctl create-namespace -m fsdax|devdax --map=mem|dev\n"
         "fsdax дає блоковий /dev/pmemN, devdax — символьний /dev/daxN.M",
         WARM, POS),
        ("планка й область пам'яті",
         "/sys/bus/nd/devices: nmemN → regionN → namespaceN.M\n"
         "те саме в машинному вигляді показує ndctl list -BDRN",
         GREY, MUTED),
    ]

    p = []
    p.append(text(LX + LW / 2, 46, "шар", size=14, bold=True, color=INK))
    p.append(text(RX + RW / 2, 46, "важіль цього шару", size=14, bold=True, color=INK))

    for i, (layer, lever, tint, accent) in enumerate(rows):
        y = TOP + STEP * i
        cy = y + BH / 2
        p.append(fitbox(LX, y, LW, BH, layer, size=13.5, bold=True,
                        fill="#ffffff", stroke=accent, sw=1.8))
        p.append(fitbox(RX, y, RW, BH, lever, size=12.5,
                        fill=tint, stroke=accent, sw=1.8))
        p.append(line(LX + LW + 14, cy, RX - 14, cy, color=MUTED, sw=1.6, dash="5 5"))
        if i < len(rows) - 1:
            p.append(arrow(LX + LW / 2, y + BH + 4, LX + LW / 2, y + STEP - 4,
                           color=MUTED, sw=2))

    p.append(mtext(W / 2, TOP + STEP * 4 + BH + 40,
                   ["пряме звертання виникає лише тоді, коли жоден із шарів не сказав «ні»;",
                    "будь-який один із них вимикає його для всіх, хто вище"],
                   size=12.5, color=INK))

    render(os.path.join(OUT, "dax-stack.svg"), W, H, *p)


fig_two_paths()
fig_persistence_domain()
fig_map_sync()
fig_timeline()
fig_commit_order()
fig_dax_stack()
print("ok")
