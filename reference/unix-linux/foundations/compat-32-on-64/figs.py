# -*- coding: utf-8 -*-
"""Фігури теми «32-бітні програми на 64-бітному ядрі: шар сумісности»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Три станції перекладу коло межі ─────────────────────────────────────
def fig_stations():
    W, H = 1040, 640
    f = []

    # колонка «що приходить» / «що робить станція» / «що йде далі»
    heads = [(50, 280, "з боку 32-бітної програми"),
             (390, 300, "станція перекладу"),
             (730, 260, "у бік коду ядра")]
    for x, w, s in heads:
        f.append(fitbox(x, 54, w, 36, [s], size=14, bold=True, fill="#e8edf3"))

    rows = [
        (["вхід int 0x80,",
          "sysenter або syscall;",
          "номер 4 = write"],
         ["вибір таблиці",
          "за точкою входу"],
         ["номер 1 = write",
          "у рідній таблиці"]),
        (["EBX, ECX, EDX,",
          "ESI, EDI, EBP;",
          "старші половини — сміття"],
         ["звуження до 32 бітів",
          "і свідоме доповнення:",
          "нулями або знаком"],
         ["чисті значення",
          "у RDI, RSI, RDX…"]),
        (["struct compat_stat,",
          "old_timespec32,",
          "масив 4-байтових адрес"],
         ["перебудова полів",
          "за рідними зсувами;",
          "compat_ptr() для адрес"],
         ["struct stat,",
          "struct timespec,",
          "звичайні покажчики"]),
    ]

    y, rh, gap = 104, 96, 22
    for left, mid, right in rows:
        f.append(fitbox(50, y, 280, rh, left, size=12, fill=FILL))
        f.append(fitbox(390, y, 300, rh, mid, size=12, fill="#fff7e6",
                        stroke=POS, sw=2))
        f.append(fitbox(730, y, 260, rh, right, size=12, fill="#eaf3ec"))
        f.append(arrow(334, y + rh / 2, 386, y + rh / 2))
        f.append(arrow(694, y + rh / 2, 726, y + rh / 2))
        y += rh + gap

    f.append(line(360, 100, 360, y - gap + 6, color=POS, sw=2, dash="7 6"))
    f.append(line(712, 100, 712, y - gap + 6, color=FIELD, sw=2, dash="7 6"))

    f.append(fitbox(50, y + 14, 940, 56,
                    ["глибше цієї смуги ядро працює лише з рідними типами —",
                     "жодна функція нижче не питає, якої розрядности була програма"],
                    size=14, bold=True, fill="#eaf3ec", stroke=FIELD, sw=2))

    f.append(text(W / 2, y + 106,
                  "ліва штрихова лінія — межа привілею, права — межа перекладу",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'compat-stations.svg'), W, H, *f,
           title="Три станції перекладу на межі системного виклику")


# ── 2. Побайтова розкладка тієї самої структури ────────────────────────────
def fig_struct_layout():
    W, H = 1000, 560
    f = []

    CELL = 44
    X0 = 120

    def ruler(y):
        out = []
        for i in range(16):
            out.append(text(X0 + i * CELL + CELL / 2, y, str(i), size=12,
                            color=MUTED))
        return "".join(out)

    def band(y, spans):
        """spans: список (перший байт, кількість, підпис, заливка, колір рамки)"""
        out = []
        for start, count, label, fill, stroke in spans:
            out.append(fitbox(X0 + start * CELL, y, count * CELL - 4, 52,
                              [label], size=13, fill=fill, stroke=stroke, sw=2))
        return "".join(out)

    f.append(text(X0 - 14, 72, "байт:", size=12, color=MUTED, anchor="end"))
    f.append(ruler(72))

    # ILP32
    f.append(fitbox(20, 96, 90, 52, ["ILP32"], size=14, bold=True,
                    fill="#e8edf3"))
    f.append(band(96, [
        (0, 4, "code", FILL, LINE),
        (4, 8, "stamp", "#eaf3ec", FIELD),
    ]))
    f.append(line(X0 + 12 * CELL, 92, X0 + 12 * CELL, 156, color=POS, sw=2))
    f.append(text(X0 + 12 * CELL + 14, 128, "sizeof = 12", size=13,
                  color=POS, bold=True, anchor="start"))

    # LP64
    f.append(fitbox(20, 216, 90, 52, ["LP64"], size=14, bold=True,
                    fill="#e8edf3"))
    f.append(band(216, [
        (0, 4, "code", FILL, LINE),
        (4, 4, "набивка", "#fdecea", POS),
        (8, 8, "stamp", "#eaf3ec", FIELD),
    ]))
    f.append(line(X0 + 16 * CELL, 212, X0 + 16 * CELL, 276, color=POS, sw=2))
    f.append(text(X0 + 16 * CELL + 14, 248, "= 16", size=13,
                  color=POS, bold=True, anchor="start"))

    # чому саме так
    f.append(fitbox(120, 306, 380, 92,
                    ["вимога вирівнювання long long:",
                     "ILP32 — кратно 4 байтам",
                     "LP64 — кратно 8 байтам"],
                    size=13, fill="#fff7e6"))
    f.append(fitbox(540, 306, 400, 92,
                    ["звідси зсув другого поля:",
                     "у ILP32 stamp починається з байта 4,",
                     "у LP64 — аж із байта 8"],
                    size=13, fill="#fff7e6"))

    f.append(fitbox(120, 424, 820, 56,
                    ["розміри полів однакові в обох ABI — а структури різні; "
                     "тому кожна",
                     "структура на межі має в ядрі окремого 32-бітного двійника"],
                    size=14, bold=True, fill="#eaf3ec", stroke=FIELD, sw=2))

    f.append(text(W / 2, 516,
                  "struct sample { int code; long long stamp; }",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'struct-layout.svg'), W, H, *f,
           title="Та сама структура за двома домовленостями")


# ── 3. Адресний простір 32-бітної програми ─────────────────────────────────
def fig_address_space():
    W, H = 940, 590
    f = []

    TOP, BOT = 116, 456
    colw = 300

    def column(x, head, parts, note):
        """parts: список (частка висоти згори вниз, підпис, заливка, рамка)"""
        out = [fitbox(x, 62, colw, 42, [head], size=14, bold=True,
                      fill="#e8edf3")]
        y = TOP
        total = float(sum(p[0] for p in parts))
        for share, label, fill, stroke in parts:
            h = (BOT - TOP) * share / total
            out.append(fitbox(x, y, colw, h - 4, label, size=13, fill=fill,
                              stroke=stroke, sw=2))
            y += h
        out.append(fitbox(x, BOT + 20, colw, 56, note, size=13, fill="#ffffff",
                          color=MUTED))
        return "".join(out)

    f.append(column(60, "32-бітне ядро",
                    [(1.0, ["ядро — 1 ГіБ"], "#fdecea", POS),
                     (3.0, ["програма —", "3 ГіБ"], FILL, LINE)],
                    ["ядро мусить уміститися", "в ті самі 4 ГіБ"]))

    f.append(column(580, "64-бітне ядро",
                    [(4.0, ["програма —", "майже 4 ГіБ"], "#eaf3ec", FIELD)],
                    ["ядро живе у власному", "64-бітному діапазоні"]))

    # шкала посередині
    mid = 460
    f.append(line(mid, TOP, mid, BOT, color=MUTED, sw=1.5, dash="5 5"))
    f.append(text(mid, TOP - 12, "4 ГіБ", size=13, color=MUTED, bold=True))
    f.append(text(mid, BOT + 22, "0", size=13, color=MUTED, bold=True))

    f.append(fitbox(60, 536, 820, 40,
                    ["та сама програма, той самий процесор — "
                     "а доступної пам'яті майже на гігабайт більше"],
                    size=14, bold=True, fill="#eaf3ec", stroke=FIELD, sw=2))

    render(os.path.join(OUT, 'address-space.svg'), W, H, *f,
           title="Скільки простору бачить 32-бітна програма")


# ── 4. Дві дороги в 64 біти ──────────────────────────────────
def fig_two_roads():
    W, H = 1180, 480
    f = []
    BW, GAP, X0 = 212, 18, 208
    BH = 106

    f.append(fitbox(28, 112, 160, BH, ["Intel:", "новий набір", "IA-64"],
                    size=15, bold=True, fill="#fdecea", stroke=POS, sw=2))
    f.append(fitbox(28, 250, 160, BH, ["AMD:", "розширення", "старого x86"],
                    size=15, bold=True, fill="#eaf3ec", stroke=FIELD, sw=2))

    top = [["червень 2001", "Itanium (Merced):", "старий x86-код бере",
            "окремий вузол — повільно"],
           ["2003", "IA-32 EL: програмний", "перекладач виявився",
            "швидший за залізо"],
           ["2006", "Montecito: апаратний", "x86-вузол прибрано",
            "з кристала зовсім"],
           ["2020–2021", "останні замовлення", "й остання партія",
            "Itanium"]]
    bot = [["1999", "AMD оголошує 64-бітне", "розширення x86",
            "з рідним 32-бітним режимом"],
           ["квітень 2003", "Opteron: 32-бітні", "програми йдуть",
            "на повній швидкості"],
           ["вересень 2003", "Athlon 64: те саме", "на звичайному",
            "настільному столі"],
           ["червень 2004", "Intel бере чужий", "набір: EM64T",
            "у Xeon Nocona"]]

    for i, lines in enumerate(top):
        f.append(fitbox(X0 + i * (BW + GAP), 112, BW, BH, lines, size=13, fill="#fdf3f2", stroke=POS))
    for i, lines in enumerate(bot):
        f.append(fitbox(X0 + i * (BW + GAP), 250, BW, BH, lines, size=13, fill="#f0f7f2", stroke=FIELD))

    f.append(fitbox(28, 392, 1124, 52,
                    ["Ціна сумісности не зникла в переможця — її перенесли з кремнію в ядро операційної системи"],
                    size=15, bold=True, fill="#e8edf3", stroke=LINE, sw=2))

    render(os.path.join(OUT, 'two-roads.svg'), W, H, *f,
           title="Дві дороги в 64 біти й доля старих програм на кожній")


# ── 5. У що розгортається COMPAT_SYSCALL_DEFINE (вставка api) ──────────────
def fig_macro_expansion():
    W, H = 1120, 660
    f = []

    LX, LW = 56, 590          # ліва колонка — код
    RX, RW = 692, 372         # права колонка — пояснення

    f.append(fitbox(LX, 60, LW, 78,
                    ["COMPAT_SYSCALL_DEFINE3(ioctl,",
                     "        unsigned int, fd, unsigned int, cmd,",
                     "        compat_ulong_t, arg)"],
                    size=14, fill="#e8edf3", stroke=LINE, sw=2))
    f.append(fitbox(RX, 60, RW, 78,
                    ["один рядок, який пише автор",
                     "виклику; далі все робить",
                     "препроцесор"],
                    size=13, fill="#ffffff", color=MUTED))

    steps = [
        (168, 88,
         ["asmlinkage long compat_sys_ioctl(",
          "        unsigned int fd, unsigned int cmd,",
          "        compat_ulong_t arg);"],
         "#eaf3ec", FIELD,
         ["ім'я, яке стоїть у 32-бітній",
          "таблиці викликів;",
          "власного тіла не має —",
          "це псевдонім (alias)"]),
        (300, 100,
         ["asmlinkage long __se_compat_sys_ioctl(",
          "        long fd, long cmd, long arg)",
          "{ ... __SC_DELOUSE на кожному аргументі ... }"],
         "#fff7e6", POS,
         ["ЄДИНЕ місце звуження:",
          "усе прийшло як long,",
          "звідси виходить уже чистим;",
          "на s390 саме тут гасять",
          "старший біт покажчиків"]),
        (444, 88,
         ["static inline long __do_compat_sys_ioctl(",
          "        unsigned int fd, unsigned int cmd,",
          "        compat_ulong_t arg)"],
         FILL, LINE,
         ["тіло, яке пишете ви:",
          "типи вже оголошені,",
          "значення вже перевірені"]),
    ]

    prev_bottom = 138
    for y, h, code, fill, stroke, note in steps:
        f.append(arrow(LX + LW / 2, prev_bottom + 2, LX + LW / 2, y - 4))
        f.append(fitbox(LX, y, LW, h, code, size=13, fill=fill, stroke=stroke, sw=2))
        f.append(fitbox(RX, y, RW, h, note, size=13, fill="#ffffff", color=MUTED))
        prev_bottom = y + h

    f.append(fitbox(LX, 566, 1008, 60,
                    ["три імені на один макрос — і жодного розгалуження "
                     "«а якщо 32 біти»",
                     "нижче за __se_-обгортку"],
                    size=14, bold=True, fill="#eaf3ec", stroke=FIELD, sw=2))

    render(os.path.join(OUT, 'macro-expansion.svg'), W, H, *f,
           title="У що розгортається COMPAT_SYSCALL_DEFINE3")


# ── 6. Що лишається від покажчика по дорозі крізь int 0x80 (вставка proj) ──
def fig_int80_truncation():
    W, H = 1020, 500
    f = []

    C1X, C1W = 40, 300
    C2X, C2W = 390, 240
    C3X, C3W = 680, 300

    heads = [(C1X, C1W, "адреса рядка в програмі"),
             (C2X, C2W, "що дістає ядро"),
             (C3X, C3W, "чим кінчається write")]
    for x, w, s in heads:
        f.append(fitbox(x, 52, w, 36, [s], size=14, bold=True, fill="#e8edf3"))

    rows = [
        (110,
         ["збірка типова (PIE)",
          "&msg = 0x55f0a2c04010",
          "старша половина: 0x000055f0"],
         ["компат-вхід читає ECX —",
          "молодші 32 біти:",
          "0xa2c04010"],
         ["нижче за 4 ГіБ у процесі",
          "не відображено нічого",
          "write = −1, EFAULT"],
         "#fdecea", POS),
        (250,
         ["збірка -no-pie -fno-pic",
          "&msg = 0x00404010",
          "старша половина: 0x00000000"],
         ["компат-вхід читає ECX —",
          "молодші 32 біти:",
          "0x00404010"],
         ["адреса вціліла повністю",
          "рядок надруковано",
          "write = 15"],
         "#eaf3ec", FIELD),
    ]

    RH = 112
    for y, left, mid, right, fill, stroke in rows:
        f.append(fitbox(C1X, y, C1W, RH, left, size=13, fill=FILL))
        f.append(fitbox(C2X, y, C2W, RH, mid, size=13, fill="#fff7e6",
                        stroke=LINE, sw=1.5))
        f.append(fitbox(C3X, y, C3W, RH, right, size=13, fill=fill,
                        stroke=stroke, sw=2))
        f.append(arrow(C1X + C1W + 6, y + RH / 2, C2X - 6, y + RH / 2))
        f.append(arrow(C2X + C2W + 6, y + RH / 2, C3X - 6, y + RH / 2))

    f.append(fitbox(40, 400, 940, 62,
                    ["та сама інструкція в тому самому файлі: чи спрацює вона —",
                     "вирішує те, куди завантажувач поклав дані"],
                    size=15, bold=True, fill="#e8edf3", stroke=LINE, sw=2))

    render(os.path.join(OUT, 'int80-truncation.svg'), W, H, *f,
           title="Одна інструкція int 0x80, дві долі покажчика")


if __name__ == '__main__':
    fig_stations()
    fig_struct_layout()
    fig_address_space()
    fig_two_roads()
    fig_macro_expansion()
    fig_int80_truncation()
    print("ok")
