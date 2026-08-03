# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT   = "#fbfcff"
AMBER  = "#b7791f"


# ── 1. Два шляхи до байта у файлі: копія проти імені ────────────────────────────
def fig_two_paths():
    W, H = 1080, 600
    p = []

    PW = 500
    panels = [
        (30, "read(): байт переносять до вас", NEG, "#eaf0fd",
         ["буфер програми\n(сторінка у власній пам'яті процесу)",
          "сторінка кешу сторінок\n(вміст файлу в пам'яті ядра)",
          "диск"],
         ["копіювання з пам'яті в пам'ять,\nодин системний виклик на порцію",
          "читання з диска — лише якщо\nсторінки ще немає в кеші"],
         "у програми немає адреси, якою можна назвати сторінку кешу,\nтому вміст їй переносять у власний буфер"),
        (550, "mmap(): байт вам називають", FIELD, "#eafaf0",
         ["адреса в програмі",
          "сторінка кешу сторінок\n(та сама фізична сторінка)",
          "диск"],
         ["запис у таблиці сторінок\nвказує просто на цю сторінку",
          "читання з диска — лише при\nпершому доступі до сторінки"],
         "після першого сторінкового збою доступ — звичайна\nінструкція процесора, ядро в ньому не бере участі"),
    ]

    for px, head, accent, tint, boxes, gaps, note in panels:
        p.append(rect(px, 46, PW, H - 76, fill="#ffffff", stroke="#dfe3e8", sw=1.2, rx=12))
        p.append(fitbox(px + 20, 60, PW - 40, 40, head, size=14,
                        fill=tint, stroke=accent, sw=1.8, color=accent, bold=True))

        ys = [124, 242, 360]
        for i, b in enumerate(boxes):
            p.append(fitbox(px + 20, ys[i], PW - 40, 72, b, size=12,
                            fill=SOFT if i < 2 else "#eceff2",
                            stroke=accent if i < 2 else MUTED, sw=1.6, color=INK))
        for i, g in enumerate(gaps):
            ax = px + 70
            p.append(arrow(ax, ys[i] + 76, ax, ys[i + 1] - 4, color=accent, sw=1.7))
            p.append(mtext(px + 300, ys[i] + 92, g, size=10, color=MUTED, lh=1.25))

        p.append(fitbox(px + 20, 458, PW - 40, 62, note, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    p.append(text(W / 2, H - 14,
                  "фізична сторінка з вмістом файлу в обох випадках одна й та сама — різниця лише в тому, чи має до неї ім'я сам процес",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Той самий байт: перенести копію чи дати ім'я")


# ── 2. Спільне й приватне відображення до і після запису ───────────────────────
def fig_shared_vs_private():
    W, H = 1140, 520
    p = []

    PW = 530
    for px, head, accent, tint in [(30, "Обидва лише читають", NEG, "#eaf0fd"),
                                   (580, "Процес B щось записав", POS, "#fdecea")]:
        p.append(rect(px, 46, PW, H - 92, fill="#ffffff", stroke="#dfe3e8", sw=1.2, rx=12))
        p.append(fitbox(px + 20, 60, PW - 40, 38, head, size=14,
                        fill=tint, stroke=accent, sw=1.8, color=accent, bold=True))

    # ── ліва сцена ──────────────────────────────────────────────────────────────
    lx = 30
    p.append(fitbox(lx + 30, 118, 200, 62, "процес A\nMAP_SHARED", size=12,
                    fill=SOFT, stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(lx + 290, 118, 200, 62, "процес B\nMAP_PRIVATE", size=12,
                    fill=SOFT, stroke=PURPLE, sw=1.7, color=INK))
    p.append(arrow(lx + 130, 184, lx + 200, 234, color=FIELD, sw=1.7))
    p.append(arrow(lx + 390, 184, lx + 320, 234, color=PURPLE, sw=1.7))
    p.append(fitbox(lx + 60, 238, 400, 58, "одна фізична сторінка кешу сторінок", size=12,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(arrow(lx + 260, 300, lx + 260, 340, color=MUTED, sw=1.6))
    p.append(fitbox(lx + 130, 344, 260, 48, "файл на диску", size=12,
                    fill="#eceff2", stroke=MUTED, sw=1.4, color=INK))
    p.append(mtext(lx + 260, 412, "обидва бачать ті самі байти,\nбо це буквально та сама сторінка",
                   size=11, color=MUTED, lh=1.25))

    # ── права сцена ─────────────────────────────────────────────────────────────
    rx0 = 580
    p.append(fitbox(rx0 + 30, 118, 200, 62, "процес A\nMAP_SHARED", size=12,
                    fill=SOFT, stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(rx0 + 290, 118, 200, 62, "процес B\nMAP_PRIVATE", size=12,
                    fill=SOFT, stroke=POS, sw=1.7, color=INK))
    p.append(arrow(rx0 + 130, 184, rx0 + 130, 234, color=FIELD, sw=1.7))
    p.append(arrow(rx0 + 390, 184, rx0 + 390, 234, color=POS, sw=1.7))
    p.append(fitbox(rx0 + 20, 238, 220, 58, "сторінка кешу\nсторінок", size=12,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK))
    p.append(fitbox(rx0 + 280, 238, 220, 58, "приватна копія\nсторінки B", size=12,
                    fill="#fdecea", stroke=POS, sw=1.8, color=INK))
    p.append(arrow(rx0 + 130, 300, rx0 + 130, 340, color=MUTED, sw=1.6))
    p.append(fitbox(rx0 + 30, 344, 200, 48, "файл на диску", size=12,
                    fill="#eceff2", stroke=MUTED, sw=1.4, color=INK))
    p.append(mtext(rx0 + 390, 356, "з файлом більше\nне пов'язана", size=11, color=POS, lh=1.25))
    p.append(mtext(rx0 + 265, 412, "запис A змінив би сам файл,\nзапис B породив окрему сторінку",
                   size=11, color=MUTED, lh=1.25))

    p.append(text(W / 2, H - 14,
                  "одне слово у виклику вирішує, чи запис процесу є зміною файлу, чи лише його власною відгалуженою копією",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "shared-vs-private.svg"), W, H, *p,
           title="Спільне й приватне відображення того самого файлу")


# ── 3. Геометрія відображення: сторінки, кінець файлу і зона SIGBUS ────────────
def fig_mapping_geometry():
    W, H = 1080, 500
    p = []

    X0, CW, GAP = 48, 240, 8
    CELLS = 4
    CY, CH = 176, 96

    def cx(i):
        return X0 + i * (CW + GAP)

    end_x = cx(2) + int(CW * 0.2)   # 9000-й байт усередині третьої сторінки

    # смуга «що є у файлі»
    p.append(rect(X0, 106, end_x - X0, 42, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text((X0 + end_x) / 2, 133, "у файлі є 9000 байтів", size=12, color=FIELD, bold=True))
    right_end = cx(CELLS - 1) + CW
    p.append(rect(end_x, 106, right_end - end_x, 42, fill="#f3f4f6", stroke=MUTED, sw=1.4, rx=6))
    p.append(text((end_x + right_end) / 2, 133, "далі у файлі немає нічого", size=12, color=MUTED))

    labels = ["сторінка 0\n0…4095", "сторінка 1\n4096…8191",
              "сторінка 2\n8192…12287", "сторінка 3\n12288…16383"]
    for i in range(CELLS):
        x = cx(i)
        if i < 2:
            p.append(fitbox(x, CY, CW, CH, labels[i], size=13,
                            fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK))
        elif i == 2:
            head = int(CW * 0.2)
            p.append(rect(x, CY, head, CH, fill="#eafaf0", stroke=FIELD, sw=1.8))
            p.append(rect(x + head, CY, CW - head, CH, fill="#fdf6e3", stroke=AMBER, sw=1.8))
            p.append(mtext(x + head + (CW - head) / 2, CY + 40, labels[i], size=13, color=INK))
        else:
            p.append(fitbox(x, CY, CW, CH, labels[i], size=13,
                            fill="#fdecea", stroke=POS, sw=1.8, color=INK))

    notes = [
        (cx(0), CW * 2 + GAP, "вміст цілком береться з файлу", FIELD, "#f4fbf6"),
        (cx(2), CW, "хвіст за кінцем файлу ядро\nзанулює; те, що туди запишуть,\nу файл не потрапить", AMBER, "#fdf6e3"),
        (cx(3), CW, "цілком за кінцем файлу:\nзвертання дає сигнал SIGBUS,\nа не нулі й не помилку", POS, "#fdecea"),
    ]
    for x, w, s, accent, fill in notes:
        p.append(fitbox(x, CY + CH + 18, w, 86, s, size=11, fill=fill, stroke=accent, sw=1.4, color=INK))

    p.append(text(W / 2, H - 16,
                  "відображення міряють сторінками, а файл — байтами; уся різниця між цими двома мірками лишається на совісті програми",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mapping-geometry.svg"), W, H, *p,
           title="Відображення довжиною 16384 байти на файл із 9000 байтів")




# ── 4. Хроніка: від опису в довіднику до працюючої реалізації ──────────────────
def fig_hist_timeline():
    W, H = 1080, 730
    p = []

    p.append(text(W / 2, 40, "Виклик, описаний 1983 року, і його перша працююча реалізація",
                  size=17, bold=True))
    p.append(text(W / 2, 62, "зелене — там, де реалізація справді запрацювала; червоне — там, де був лише опис",
                  size=11.5 and 11, color=MUTED, italic=True))

    rows = [
        ("серпень 1983", "4.2BSD",
         "інтерфейс mmap описано в документі архітектури; система вийшла без нього — сили пішли на мережу",
         POS, "#fdecea"),
        ("червень 1986", "S. Kleiman, «Vnodes» (USENIX Summer)",
         "файл будь-якої файлової системи дістає в ядрі єдиний опис — vnode (уперше в SunOS 2.0, 1985)",
         NEG, "#eaf0fd"),
        ("червень 1986", "4.3BSD",
         "архітектуру переглянуто за участі понад 40 компаній і груп; реалізації знову немає",
         POS, "#fdecea"),
        ("червень 1987", "R. Gingell, J. Moran, W. Shannon (USENIX Summer)",
         "«Virtual Memory Architecture in SunOS» — опис єдиної системи пам'яті, де сторінки належать vnode",
         NEG, "#eaf0fd"),
        ("грудень 1988", "SunOS 4.0",
         "перша широко доступна працююча реалізація: сегментні драйвери (seg_vn) і кеш файлу як сторінки VM",
         FIELD, "#eafaf0"),
        ("грудень 1992", "Linux 0.99",
         "у дереві ядра з'являється mm/mmap.c — Linux будує пам'ять навколо кешу сторінок від початку",
         FIELD, "#eafaf0"),
        ("початок 1990", "4.3BSD-Reno",
         "Берклі бере систему пам'яті з Mach, бо реалізації Sun не дістав",
         NEG, "#eaf0fd"),
        ("1993", "POSIX.1b (IEEE 1003.1b-1993)",
         "mmap входить у стандарт як опція «відображувані файли» — не обов'язкова частина POSIX",
         MUTED, "#f4f6f8"),
        ("червень 1994", "4.4BSD",
         "у BSD виклик нарешті повноцінний — через одинадцять років після опису",
         FIELD, "#eafaf0"),
    ]
    # хронологічний порядок (Reno після Linux у списку вище — виправляємо тут)
    order = [0, 1, 2, 3, 4, 6, 5, 7, 8]
    rows = [rows[i] for i in order]

    AX, TOP, RH, BH = 250, 92, 68, 54
    BX, BW = 286, 764
    p.append(line(AX, TOP - 6, AX, TOP + len(rows) * RH - 8, color="#c8ccd2", sw=2.5))

    for i, (date, head, note, accent, fill) in enumerate(rows):
        y = TOP + i * RH
        p.append(text(AX - 26, y + BH / 2 + 4, date, size=13, color=MUTED, anchor="end"))
        p.append(circle(AX, y + BH / 2, 7, fill=fill, stroke=accent, sw=2.5))
        p.append(rect(BX, y, BW, BH, fill=fill, stroke=accent, sw=1.6))
        hs = fit_font(head, BW - 32, 13, bold=True)
        p.append(text(BX + 16, y + 21, head, size=hs, color=INK, anchor="start", bold=True))
        ns = fit_font(note, BW - 32, 12)
        p.append(text(BX + 16, y + 41, note, size=ns, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 22,
                  "дати релізів і публікацій перевірені за документацією систем; порядок подій — не порядок заслуг",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Хроніка появи mmap: 1983–1994")


# ── 5. Два світи проти одного ─────────────────────────────────────────────────
def fig_hist_two_worlds():
    W, H = 1080, 560
    p = []

    panels = [
        (30, "Ранній Unix: дві незалежні системи обліку", POS),
        (560, "SunOS 4.0: одна система, два способи назвати сторінку", FIELD),
    ]
    for x, title_s, accent in panels:
        p.append(rect(x, 26, 490, 466, fill="#fcfcfd", stroke=accent, sw=2))
        ts = fit_font(title_s, 460, 14, bold=True)
        p.append(text(x + 245, 52, title_s, size=ts, color=accent, bold=True))

    # ── ліва панель
    p.append(fitbox(60, 76, 430, 62,
                    "пам'ять процесу\nадреси, які перекладає таблиця сторінок",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, color=INK))
    p.append(arrow(230, 138, 230, 208, color=MUTED))
    p.append(arrow(320, 208, 320, 138, color=MUTED))
    p.append(text(275, 178, "копія", size=13, color=POS, bold=True))
    p.append(fitbox(60, 208, 430, 62,
                    "буферний кеш ядра\nблоки з ключем «пристрій + номер блока»",
                    size=13, fill="#fdf6e3", stroke=AMBER, sw=1.6, color=INK))
    p.append(fitbox(60, 300, 430, 168,
                    "У кеші немає поняття «сторінка процесу»,\n"
                    "у пам'яті процесу немає поняття «файл».\n"
                    "Спільної речі, на яку вказали б обидві\n"
                    "системи, просто не існує — тож єдиний\n"
                    "спосіб дістати байт файлу в програму\n"
                    "лишається один: скопіювати його.",
                    size=13, fill="#ffffff", stroke="#c8ccd2", sw=1.4, color=INK))

    # ── права панель
    p.append(fitbox(590, 76, 430, 58,
                    "ділянка адресного простору (seg_vn)\nправило: звідки брати сторінки",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, color=INK))
    p.append(arrow(805, 134, 805, 182, color=FIELD))
    p.append(fitbox(590, 182, 430, 58,
                    "сторінки, що належать vnode\nвони ж — увесь кеш цього файлу",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))
    p.append(arrow(805, 240, 805, 288, color=FIELD))
    p.append(fitbox(590, 288, 430, 50,
                    "vnode: файл будь-якої файлової системи",
                    size=13, fill="#f4f6f8", stroke="#8a8f98", sw=1.6, color=INK))
    p.append(fitbox(590, 364, 430, 104,
                    "Кеш файлу — це і є сторінки віртуальної\n"
                    "пам'яті. Ділянка процесу лише вказує\n"
                    "на них, тож копіювати нема чого.",
                    size=13, fill="#ffffff", stroke="#c8ccd2", sw=1.4, color=INK))

    p.append(text(W / 2, H - 24,
                  "mmap не додали до системи — систему перебудували так, що виклик став очевидним наслідком",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-two-worlds.svg"), W, H, *p,
           title="Буферний кеш і пам'ять процесу: до злиття й після")


# ── 6. Прапорці mmap: чотири незалежні осі одного слова ────────────────────────
def fig_mmap_axes():
    W, H = 1220, 640
    p = []

    LX, LW = 36, 214
    CX, CW_ALL = 272, 912
    BH, GAP, Y0 = 98, 22, 64

    bands = [
        ("джерело вмісту\n(оберіть одне)", NEG, "#eaf0fd",
         ["файл: fd і offset\nсторінки беруть із кешу цього файлу",
          "MAP_ANONYMOUS\nсторінки видають чистими, з нулів"]),
        ("видимість запису\n(рівно одне: це поле,\nа не окремі біти)", PURPLE, "#f3edfb",
         ["MAP_SHARED\nзапис змінює сам файл",
          "MAP_SHARED_VALIDATE\nте саме + перевірка прапорців",
          "MAP_PRIVATE\nзапис породжує власну копію"]),
        ("розміщення\n(оберіть одне)", AMBER, "#fdf6e3",
         ["addr як підказка\nядро вільне взяти сусідню адресу",
          "MAP_FIXED\nмовчки затирає те, що там було",
          "MAP_FIXED_NOREPLACE\nзіткнення дає EEXIST",
          "MAP_32BIT\nперші два гігабайти, лише x86-64"]),
        ("заповнення й резидентність\n(комбінуються вільно)", FIELD, "#eafaf0",
         ["MAP_POPULATE\nтаблиці заповнити одразу",
          "MAP_LOCKED\nтримати в пам'яті, без свопу",
          "MAP_NORESERVE\nмісця під своп не резервувати",
          "MAP_HUGETLB\nсторінки на 2 МіБ або 1 ГіБ"]),
    ]

    y = Y0
    for name, accent, tint, items in bands:
        p.append(fitbox(LX, y, LW, BH, name, size=13,
                        fill=tint, stroke=accent, sw=1.8, color=accent, bold=True))
        n = len(items)
        gap = 16
        w = (CW_ALL - gap * (n - 1)) / n
        for i, s in enumerate(items):
            p.append(fitbox(CX + i * (w + gap), y, w, BH, s, size=11,
                            fill=SOFT, stroke=accent, sw=1.5, color=INK))
        y += BH + GAP

    p.append(fitbox(LX, y + 6, CX + CW_ALL - LX, 64,
                    "права PROT_READ | PROT_WRITE | PROT_EXEC — це окремий аргумент prot, а не прапорець\n"
                    "PROT_NONE дорівнює нулю, тож додавати його через «або» сенсу немає: це відсутність прав",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))

    p.append(text(W / 2, H - 16,
                  "перші три осі — це вибір одного варіанта, четверта — набір незалежних побажань до ядра",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mmap-axes.svg"), W, H, *p,
           title="Чотири осі, які задає один виклик mmap")


# ── 7. Зсув мусить бути кратним сторінці ──────────────────────────────────────
def fig_offset_window():
    W, H = 1080, 460
    p = []

    X0, CW, CELLS, PS = 60, 192, 5, 4096
    CY, CH = 150, 74

    def bx(b):
        return X0 + b / PS * CW

    for i in range(CELLS):
        x = X0 + i * CW
        hot = i in (2, 3)
        p.append(rect(x, CY, CW, CH, fill="#eafaf0" if hot else "#f3f4f6",
                      stroke=FIELD if hot else MUTED, sw=1.8 if hot else 1.2, rx=0))
        p.append(mtext(x + CW / 2, CY + 30,
                       "сторінка %d\n%d…%d" % (i, i * PS, (i + 1) * PS - 1),
                       size=11, color=INK, lh=1.3))

    p.append(rect(bx(9000), 92, bx(13000) - bx(9000), 30, fill="#fdecea", stroke=POS, sw=1.7, rx=5))
    p.append(text((bx(9000) + bx(13000)) / 2, 80,
                  "потрібні байти 9000…12999", size=11, color=POS, bold=True))

    p.append(rect(bx(8192), 244, bx(16384) - bx(8192), 30, fill="#eaf0fd", stroke=NEG, sw=1.7, rx=5))
    p.append(text(700, 296,
                  "відображення 8192…16383 — від межі сторінки й до цілих сторінок",
                  size=11, color=NEG))

    p.append(line(bx(8192), 122, bx(8192), 300, color=MUTED, sw=1.1, dash="4,4"))
    p.append(line(bx(9000), 122, bx(9000), 300, color=POS, sw=1.1, dash="4,4"))
    p.append(arrow(bx(8192), 300, bx(9000), 300, color=INK, sw=1.5))
    p.append(text((bx(8192) + bx(9000)) / 2, 324,
                  "delta = 9000 − 8192 = 808", size=11, color=INK, bold=True))

    p.append(fitbox(X0, 348, CW * CELLS, 56,
                    "mmap повертає адресу початку сторінки 2 — адреса потрібного байта це base + delta\n"
                    "а в munmap треба передати саме base з повною довжиною, а не виправлений вказівник",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))

    p.append(text(W / 2, H - 14,
                  "зсув округлюють униз до межі сторінки, а різницю додають до довжини й потім до вказівника",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "offset-window.svg"), W, H, *p,
           title="Відображення вікна файлу, що починається не з межі сторінки")


# ── proj: fault-around — один збій заповнює цілу пачку записів ────────────────
def fig_proj_fault_around():
    W, H = 1020, 452
    p = []

    X0, CW, GAP = 65, 50, 6
    N = 16

    def cx(i):
        return X0 + i * (CW + GAP)

    p.append(text(W / 2, 64, "чого чекає арифметика: збій на кожній сторінці",
                  size=14, color=POS, bold=True))
    for i in range(N):
        p.append(rect(cx(i), 78, CW, 46, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
        p.append(text(cx(i) + CW / 2, 107, "збій", size=11, color=POS))
    p.append(text(W / 2, 152, "16 сторінок — 16 входів у ядро", size=12, color=MUTED))

    p.append(text(W / 2, 200, "що робить ядро: збій на першій сторінці вікна, решта — заразом",
                  size=14, color=FIELD, bold=True))
    for i in range(N):
        if i == 0:
            p.append(rect(cx(i), 214, CW, 46, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
            p.append(text(cx(i) + CW / 2, 243, "збій", size=11, color=POS))
        else:
            p.append(rect(cx(i), 214, CW, 46, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
            p.append(text(cx(i) + CW / 2, 243, "PTE", size=11, color=FIELD))
    p.append(text(W / 2, 288, "16 сторінок — 1 вхід у ядро і 16 готових записів у таблиці",
                  size=12, color=MUTED))

    p.append(fitbox(150, 312, 720, 92,
                    "вікно fault-around — 64 КіБ, тобто 16 сторінок по 4 КіБ\n"
                    "1048576 сторінок ділені на 65611 збоїв — 15.98 сторінки на збій",
                    size=13, fill=SOFT, stroke=PURPLE, sw=1.6, color=INK))

    p.append(text(W / 2, 434,
                  "заразом ядро підставляє лише ті сторінки, що вже лежать у кеші; по холодному файлу цієї знижки немає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "fault-around.svg"), W, H, *p,
           title="Один збій — шістнадцять записів у таблиці сторінок")


# ── proj: ціна одного звертання — де pread і mmap розходяться ─────────────────
def fig_proj_access_cost():
    import math
    W, H = 1020, 580
    p = []

    PX0, PX1, PY0, PY1 = 130, 930, 90, 460
    VMAX = 1.4                                   # мкс на звертання

    ks = [8192, 16384, 32768, 65536, 131072, 262144, 524288]
    pre = [1.23, 1.21, 1.21, 1.22, 1.21, 1.21, 1.21]
    mm = [1.18, 0.68, 0.43, 0.31, 0.24, 0.21, 0.20]
    tags = ["8k", "16k", "32k", "64k", "128k", "256k", "512k"]

    def X(k):
        return PX0 + (math.log(k, 2) - 13.0) / 6.0 * (PX1 - PX0)

    def Y(v):
        return PY1 - v / VMAX * (PY1 - PY0)

    # сітки НЕМАЄ навмисно: лінія крізь напис — це дефект
    p.append(line(PX0, PY0 - 10, PX0, PY1, color=INK, sw=1.6))
    p.append(line(PX0, PY1, PX1 + 10, PY1, color=INK, sw=1.6))
    for t in range(0, 8):
        v = t * 0.2
        p.append(line(PX0 - 7, Y(v), PX0, Y(v), color=INK, sw=1.4))
        p.append(text(PX0 - 14, Y(v) + 5, "%.1f" % v, size=12, color=MUTED, anchor="end"))
    p.append(text(PX0 - 14, PY0 - 26, "мкс", size=12, color=MUTED, anchor="end"))
    for k, tag in zip(ks, tags):
        p.append(line(X(k), PY1, X(k), PY1 + 7, color=INK, sw=1.4))
        p.append(text(X(k), PY1 + 26, tag, size=12, color=MUTED))

    for xs, ys, col in ((ks, pre, POS), (ks, mm, FIELD)):
        for i in range(len(xs) - 1):
            p.append(line(X(xs[i]), Y(ys[i]), X(xs[i + 1]), Y(ys[i + 1]), color=col, sw=2.6))
        for k, v in zip(xs, ys):
            p.append(circle(X(k), Y(v), 5, fill="#ffffff", stroke=col, sw=2.2))

    p.append(fitbox(600, 104, 300, 44, "pread: платить за кожне звертання",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6, color=INK))
    p.append(fitbox(470, 300, 340, 62,
                    "mmap: платить за сторінку один раз,\nдалі звертання коштує саме себе",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))

    p.append(fitbox(180, 152, 200, 42, "тут іще нічия", size=12,
                    fill=SOFT, stroke=PURPLE, sw=1.5, color=INK))
    p.append(arrow(180, 162, 139, 146, color=PURPLE, sw=1.6))

    p.append(text(W / 2, PY1 + 54, "звертань до тих самих 8192 сторінок (робочий набір 32 МіБ)",
                  size=13, color=INK))
    p.append(text(W / 2, PY1 + 82,
                  "третій шлях — прочитати весь файл у пам'ять — на цю шкалу не влазить: при 8192 звертаннях це 48 мкс на звертання",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "access-cost.svg"), W, H, *p,
           title="Ціна одного звертання до розкиданих сторінок")


if __name__ == "__main__":
    fig_two_paths()
    fig_shared_vs_private()
    fig_mapping_geometry()
    fig_hist_timeline()
    fig_hist_two_worlds()
    fig_mmap_axes()
    fig_offset_window()
    fig_proj_fault_around()
    fig_proj_access_cost()
    print("OK: figures written to", OUT)
