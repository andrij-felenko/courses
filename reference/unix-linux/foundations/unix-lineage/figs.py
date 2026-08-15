# -*- coding: utf-8 -*-
"""Фігури до теми «Родовід Unix: AT&T, BSD і поява Linux»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

SOFT = "#eef2f7"
WARM = "#fdf1ec"
COOL = "#eaf1ea"


# ── 1. Режими доступу до коду в часі ───────────────────────────────────────
def fig_regimes():
    W, H = 940, 470
    frags = []

    rows = [
        ("1969–1983\nмирова угода\n1956 року",
         "AT&T не має права продавати Unix.\nЛіцензія університетам — за вартість\nстрічки, разом із вихідним кодом.",
         "BSD, коментар Лайонса,\nпокоління, навчене\nна справжньому коді",
         SOFT),
        ("1984–1991\nпісля розпаду\nBell System",
         "Код стає товаром: ліцензія System V\nкоштує тисячі доларів; вивчати код\nна курсах заборонено ще з 1979-го.",
         "Власні Unix виробників;\nPOSIX як опис поведінки\nзамість спільного коду",
         WARM),
        ("1991–1994\nнові вільні\nрежими",
         "Linux виходить під GPL (1992);\nпозов USL завершується мировою,\nз'являється 4.4BSD-Lite (1994).",
         "Два вільні родоводи,\nщо ростуть далі\nпаралельно",
         COOL),
    ]

    y = 62
    for period, regime, result, tone in rows:
        frags.append(fitbox(30, y, 180, 108, period, size=13, bold=True, fill=tone))
        frags.append(fitbox(232, y, 352, 108, regime, size=13))
        frags.append(arrow(596, y + 54, 640, y + 54))
        frags.append(fitbox(652, y, 258, 108, result, size=13, fill=tone))
        y += 134

    render(os.path.join(IMG, 'code-access-regimes.svg'), W, H, *frags,
           title="Правовий режим коду — і що з нього виростало")


# ── 2. Дві лінії спадку ────────────────────────────────────────────────────
def fig_two_lines():
    W, H = 960, 540
    frags = []

    # зовнішнє коло сумісності
    frags.append('<rect x="20" y="48" width="920" height="440" rx="14" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="9 6"/>' % MUTED)
    # межа між панелями
    frags.append(line(630, 62, 630, 430, color=MUTED, sw=1.2, dash="6 6"))

    frags.append(text(315, 80, "успадкували вихідний ТЕКСТ", size=14, bold=True, color=MUTED))
    frags.append(text(785, 80, "успадкували лише ОПИС", size=14, bold=True, color=MUTED))

    def box(cx, cy, s, size=13, fill=FILL, bold=False):
        body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold)
        frags.append(body)
        return h

    # ліва панель — дерево коду
    box(315, 118, "Research Unix (Bell Labs)", bold=True)
    box(165, 193, "System V (AT&T)", fill=WARM)
    box(465, 193, "BSD (Берклі), 1978–1993", fill=SOFT)
    box(165, 268, "SunOS · HP-UX · AIX · IRIX", size=12, fill=WARM)
    box(465, 268, "4.4BSD-Lite (1994)", fill=SOFT)
    box(465, 343, "FreeBSD · NetBSD · OpenBSD", size=12, fill=SOFT)
    box(465, 410, "macOS (Darwin)", fill=SOFT)

    frags.append(arrow(300, 136, 190, 174))
    frags.append(arrow(330, 136, 440, 174))
    frags.append(arrow(165, 211, 165, 249))
    frags.append(arrow(465, 211, 465, 249))
    frags.append(arrow(465, 286, 465, 324))
    frags.append(arrow(465, 361, 465, 392))

    # права панель — незалежні реалізації
    box(785, 193, "Linux (1991)", fill=COOL, bold=True)
    box(785, 268, "MINIX (1987)", fill=COOL)
    frags.append(text(785, 335, "жодного рядка коду AT&T", size=12, color=MUTED))

    body, _, _ = textbox(480, 458,
                         "усі вони виконують той самий опис інтерфейсу — POSIX / SUS",
                         size=13, fill=BG, stroke=MUTED, color=MUTED)
    frags.append(body)

    render(os.path.join(IMG, 'lineage-two-lines.svg'), W, H, *frags,
           title="Спадок тексту й спадок поведінки — це різні дерева")


# ── 3. Три спадки ──────────────────────────────────────────────────────────
def fig_three():
    W, H = 900, 430
    frags = []

    cols = [(30, 210), (250, 205), (465, 205), (680, 190)]
    header = ["система", "успадкувала код", "виконує POSIX", "право на назву UNIX®"]

    rows = [
        ["Linux",     "ні — написаний з нуля", "так (без сертифіката)", "ні"],
        ["FreeBSD",   "так — 4.4BSD-Lite",     "так",                   "ні"],
        ["macOS",     "так — BSD-частина",     "так",                   "так — UNIX 03"],
        ["AIX (IBM)", "так — System V",        "так",                   "так"],
        ["MINIX 3",   "ні — написаний з нуля", "здебільшого",           "ні"],
    ]

    y = 58
    for (x, w), h in zip(cols, header):
        frags.append(fitbox(x, y, w, 44, h, size=12, bold=True, fill=SOFT))

    y = 102
    for r in rows:
        for i, ((x, w), cell) in enumerate(zip(cols, r)):
            if i == 0:
                tone, bold = SOFT, True
            elif cell.startswith("ні"):
                tone, bold = "#f7f7f8", False
            else:
                tone, bold = COOL, False
            frags.append(fitbox(x, y, w, 52, cell, size=13, fill=tone, bold=bold))
        y += 52

    frags.append(text(450, 400,
                      "«UNIX» означає різне: успадкований код, виконуваний опис або сплачений сертифікат",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'three-inheritances.svg'), W, H, *frags,
           title="Три спадки, які розійшлися")


# ── 4. Однорівневе сховище Multics проти явного введення-виведення ─────────
def fig_single_level_store():
    W, H = 1000, 500
    frags = []

    LX, LW = 34, 440
    RX, RW = 526, 440

    frags.append(fitbox(LX, 48, LW, 42,
                        "Явне введення-виведення: два світи",
                        size=15, bold=True, fill=SOFT))
    frags.append(fitbox(RX, 48, RW, 42,
                        "Однорівневе сховище: один світ",
                        size=15, bold=True, fill=COOL))

    left = [
        "файл лежить на диску,\nпам'ять процесу — окремо",
        "open(): процес дістає дескриптор,\nале ще жодного байта",
        "read(): ядро КОПІЮЄ n байтів\nз диска в буфер процесу",
        "правки йдуть у копію; щоб вони\nстали файлом, потрібен write()",
    ]
    right = [
        "сегмент — це і запис у каталозі,\nі ділянка адресного простору",
        "процес дістає сегментові номер\nу власній таблиці дескрипторів",
        "звичайне звернення до слова;\nнемає сторінки — апарат підкачує",
        "змінена сторінка сама йде\nна диск: копії не було ніколи",
    ]

    y = 106
    for i in range(4):
        tone = "#f7f7f8" if i else SOFT
        frags.append(fitbox(LX, y, LW, 62, left[i], size=13, fill=tone))
        tone2 = "#f2f7f2" if i else COOL
        frags.append(fitbox(RX, y, RW, 62, right[i], size=13, fill=tone2))
        if i < 3:
            frags.append(arrow(LX + LW / 2, y + 62, LX + LW / 2, y + 82))
            frags.append(arrow(RX + RW / 2, y + 62, RX + RW / 2, y + 82))
        y += 82

    frags.append(fitbox(LX, 424, W - 2 * LX, 54,
                        "Ціна елегантності праворуч: зміщення в адресі — 18 бітів, тобто сегмент "
                        "не більший за 256 тисяч слів (≈1.1 МіБ).\nФайл, що переріс сегмент, "
                        "перестає бути сегментом: його доводиться складати з кількох (multisegment file).",
                        size=13, fill=WARM))

    render(os.path.join(IMG, 'single-level-store.svg'), W, H, *frags,
           title="Копія в буфері проти сегмента, який і є файлом")


# ── 5. Одна структура — три розкладки (вставка proj-portable-c) ────────────
def fig_struct_layouts():
    W, H = 950, 420
    frags = []

    CW, CH, X0 = 28, 44, 215
    C_KIND = "#eef2f7"
    C_PAD  = "#f0f0f2"
    C_ID   = "#fdf1ec"
    C_TS   = "#eaf1ea"
    C_LEN  = "#f1ecf7"

    def strip(y, cells):
        """cells — список (підпис, колір); малює смугу байтів від X0."""
        for i, (lab, col) in enumerate(cells):
            x = X0 + i * CW
            frags.append(rect(x, y, CW, CH, fill=col, sw=1.0, rx=2))
            frags.append(text(x + CW / 2, y + CH / 2 + 4, lab, size=10))

    # лінійка номерів байтів
    for i in (0, 4, 8, 12, 16, 20):
        frags.append(text(X0 + i * CW + CW / 2, 68, str(i), size=10, color=MUTED))

    pad = ("pad", C_PAD)

    le4 = lambda n, c: [("%s%s" % (n, s), c) for s in ("₀", "₁", "₂", "₃")]
    be4 = lambda n, c: [("%s%s" % (n, s), c) for s in ("₃", "₂", "₁", "₀")]
    le8 = lambda n, c: [("%s%s" % (n, s), c) for s in ("₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇")]

    rows = [
        (78,  "x86-64 Linux\nLP64 · little-endian\nsizeof = 24",
         [("kind", C_KIND), pad, pad, pad] + le4("id", C_ID) + le8("ts", C_TS)
         + [("len₀", C_LEN), ("len₁", C_LEN)] + [pad] * 6),
        (152, "ARM32 роутер\nILP32 · little-endian\nsizeof = 16",
         [("kind", C_KIND), pad, pad, pad] + le4("id", C_ID) + le4("ts", C_TS)
         + [("len₀", C_LEN), ("len₁", C_LEN)] + [pad] * 2),
        (226, "MIPS мережевий\nILP32 · big-endian\nsizeof = 16",
         [("kind", C_KIND), pad, pad, pad] + be4("id", C_ID) + be4("ts", C_TS)
         + [("len₁", C_LEN), ("len₀", C_LEN)] + [pad] * 2),
    ]

    for y, label, cells in rows:
        frags.append(fitbox(18, y, 190, CH, label, size=10, fill=BG, stroke=MUTED))
        strip(y, cells)

    body, _, _ = textbox(475, 320,
                         "struct rec { char kind; int id; long ts; short len; };\n"
                         "fwrite(&rec, sizeof rec, 1, f) пише на цих трьох машинах ТРИ РІЗНІ файли:\n"
                         "різна довжина, різні зміщення полів, різний порядок байтів усередині поля.",
                         size=12, fill=WARM)
    frags.append(body)

    frags.append(text(475, 392,
                      "Формат на диску треба описати явно — інакше його «описує» ABI тієї машини, де зібрали",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'struct-layouts.svg'), W, H, *frags,
           title="Одна структура мовою C — три різні розкладки в пам'яті")


# ── 6. Дві осі умовної компіляції (вставка proj-portable-c) ────────────────
def fig_two_axes():
    W, H = 940, 430
    frags = []

    LX, RX, BW = 30, 500, 410

    frags.append(fitbox(LX, 52, BW, 44, "вісь МАШИН: перелічуємо імена",
                        size=15, bold=True, fill=WARM))
    frags.append(fitbox(RX, 52, BW, 44, "вісь ВЛАСТИВОСТЕЙ: перелічуємо факти",
                        size=15, bold=True, fill=COOL))

    frags.append(fitbox(LX, 112, BW, 124,
                        "#if   defined(__x86_64__)\n"
                        "#elif defined(__arm__)\n"
                        "#elif defined(__sparc__)\n"
                        "#else\n"
                        "#  error «невідома машина»",
                        size=12, fill=BG, stroke=MUTED))
    frags.append(fitbox(RX, 112, BW, 124,
                        "#if SIZEOF_LONG == 8\n"
                        "#if WORDS_BIGENDIAN\n"
                        "#if HAVE_UNALIGNED_LOAD\n"
                        "значення вимірює ./configure\n"
                        "на тій самій машині, де збирає",
                        size=12, fill=BG, stroke=MUTED))

    frags.append(arrow(LX + BW / 2, 244, LX + BW / 2, 276))
    frags.append(arrow(RX + BW / 2, 244, RX + BW / 2, 276))

    frags.append(fitbox(LX, 282, BW, 92,
                        "Список імен скінченний.\nМашина, якої автор не знав, або впаде\n"
                        "на #error, або тихо піде не в ту гілку.",
                        size=13, fill=WARM))
    frags.append(fitbox(RX, 282, BW, 92,
                        "Список питань скінченний, відповіді — ні.\nМашина, якої автор не знав,\n"
                        "відповідає на ті самі питання сама.",
                        size=13, fill=COOL))

    frags.append(text(470, 406,
                      "Обряд ./configure — це і є друга вісь: десятки крихітних програм, "
                      "які питають систему про неї саму",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'two-axes-ifdef.svg'), W, H, *frags,
           title="Про що питає умовна компіляція")


# ── 7. Три правові щити (вставка hist-usl-bsdi) ────────────────────────────
def fig_three_shields():
    W, H = 1100, 455
    frags = []

    cols = [(30, 200), (250, 250), (520, 250), (790, 280)]
    header = ["щит", "що він захищає", "від чого гине",
              "що з ним сталося у справі"]

    rows = [
        ["Торгова марка\nUNIX®",
         "назву — не текст\nі не ідею",
         "недбалість власника;\nперетворення на\nзагальну назву",
         "BSDi прибрала з реклами\nномер 1-800-ITS-UNIX —\nі претензія майже зникла"],
        ["Комерційна\nтаємниця",
         "зміст, поки він\nсправді таємний",
         "будь-яке публічне\nрозкриття — і назавжди",
         "код роздавали тисячам\nуніверситетів і друкували\nв коментарі Лайонса"],
        ["Авторське право",
         "конкретний текст —\nне ідею й не інтерфейс",
         "за законом 1976 року —\nпублікація без знака ©,\nне виправлена за 5 років",
         "32V роздали без ©,\nзареєстрували аж 1992-го;\nсуд визнав шанси слабкими"],
    ]

    y = 60
    for (x, w), h in zip(cols, header):
        frags.append(fitbox(x, y, w, 46, h, size=13, bold=True, fill=SOFT))

    y = 112
    tones = [SOFT, FILL, WARM, COOL]
    for r in rows:
        for i, ((x, w), cell) in enumerate(zip(cols, r)):
            frags.append(fitbox(x, y, w, 94, cell, size=12,
                                fill=tones[i], bold=(i == 0)))
        y += 100

    frags.append(text(550, 436,
                      "щити падають незалежно — тому питати треба не «чи ваше?», "
                      "а «на якій підставі й що з нею сталося раніше?»",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'usl-three-shields.svg'), W, H, *frags,
           title="Три щити коду — і чим кожен із них уразливий")


# ── 8. Дві доріжки: суд і код (вставка hist-usl-bsdi) ──────────────────────
def fig_two_tracks():
    W, H = 1010, 830
    frags = []

    frags.append(fitbox(222, 50, 390, 34, "правова доріжка",
                        size=13, bold=True, fill=SOFT))
    frags.append(fitbox(634, 50, 346, 34, "код, що виходив",
                        size=13, bold=True, fill=SOFT))

    rows = [
        ("червень 1991", "—",
         "Net/2: майже повна система\nбез коду AT&T, ~18 000 файлів"),
        ("січень 1992", "лист USL: приберіть із реклами\nномер 1-800-ITS-UNIX",
         "BSDi продає BSD/386\nз вихідними текстами за $995"),
        ("квітень 1992", "позов USL проти BSDi; згодом\nдругим відповідачем додано\nКаліфорнійський університет",
         "386BSD 0.1 (липень)"),
        ("кінець 1992", "суддя Дебевойз відмовляє в забороні\nй лишає два пункти позову\nз чотирьох",
         "Linux уже під GPL,\nверсія 0.99"),
        ("1993", "університет подає зустрічний позов;\n14 червня Novell завершує\nкупівлю USL",
         "NetBSD 0.8 (квітень),\nFreeBSD 1.0 (кінець року)"),
        ("4 лютого 1994", "мирова угода; більшість умов —\nконфіденційні (розкриті аж 2004-го)",
         "Linux 1.0 (березень)"),
        ("червень 1994", "3 файли вилучено,\n~70 — зі знаком © USL",
         "4.4BSD-Lite"),
        ("кінець 1994", "правова невизначеність знята",
         "NetBSD 1.0 (жовтень)\nі FreeBSD 2.0 (листопад) —\nперезасновані на 4.4BSD-Lite"),
    ]

    y = 96
    for when, legal, code in rows:
        frags.append(fitbox(30, y, 170, 76, when, size=12, bold=True, fill=SOFT))
        frags.append(fitbox(222, y, 390, 76, legal, size=12, fill=WARM))
        frags.append(fitbox(634, y, 346, 76, code, size=12, fill=COOL))
        y += 88

    frags.append(text(505, 808,
                      "двадцять два місяці правової невизначеності — "
                      "і жодної паузи на сусідній доріжці",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'usl-two-tracks.svg'), W, H, *frags,
           title="Поки BSD стояла в суді, код виходив далі")


if __name__ == '__main__':
    fig_regimes()
    fig_two_lines()
    fig_three()
    fig_single_level_store()
    fig_struct_layouts()
    fig_two_axes()
    fig_three_shields()
    fig_two_tracks()
    print("ok")
