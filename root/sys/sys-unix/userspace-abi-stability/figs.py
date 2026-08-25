# -*- coding: utf-8 -*-
"""Фігури для теми «Що саме заморожено: ABI до простору користувача»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_F = "#fdecea"
GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
YEL_F = "#fff5e0"


# ── 1. Чотири сімейства поверхні ABI ───────────────────────────────────────
def fig_surface():
    W, H = 1440, 760
    F = []

    # смуги
    F.append(rect(45, 56, 1366, 74, fill=BLU_F, stroke=MUTED, sw=1.6))
    F.append(text(65, 84, "ПРОСТІР КОРИСТУВАЧА", size=15, bold=True, anchor="start"))
    F.append(text(65, 110, "зібраний файл, у машинному коді якого числа вже стоять — і перезбирати його ніхто не буде",
                  size=12, color=MUTED, anchor="start"))

    F.append(rect(45, 648, 1366, 74, fill=GRN_F, stroke=FIELD, sw=2))
    F.append(text(65, 676, "ЯДРО", size=15, bold=True, anchor="start"))
    F.append(text(65, 702, "усередині переписується від версії до версії; назовні не має права змінити жодного з цих чисел",
                  size=12, color=MUTED, anchor="start"))

    cols = [
        ("Старт процесу", YEL_F, [
            "заголовки ELF, точка входу",
            "розкладка початкового стека",
            "ключі допоміжного вектора",
            "стан регістрів на вході",
        ]),
        ("Виклики й загальні двері", BLU_F, [
            "номер виклику цієї архітектури",
            "аргументи по регістрах",
            "зміщення полів у структурах",
            "значення бітів, коди помилок",
        ]),
        ("Ядро стукає назад", RED_F, [
            "номери сигналів",
            "кадр сигналу на стеку",
            "siginfo і rt_sigreturn",
            "символи vDSO та їхні версії",
        ]),
        ("Текст і імена", GRN_F, [
            "позиції полів у /proc/PID/stat",
            "назви рядків у /proc/meminfo",
            "шляхи й назви файлів у /sys",
            "імена sysctl, номери пристроїв",
        ]),
    ]

    x0, cw, gap = 45, 322, 26
    top, ch = 160, 372
    for i, (name, fill, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        F.append(rect(x, top, cw, ch, fill=BG, stroke=MUTED, sw=1.4))
        F.append(fitbox(x + 12, top + 14, cw - 24, 54, name, size=14, bold=True, fill=fill))
        for j, it in enumerate(items):
            F.append(fitbox(x + 12, top + 82 + j * 68, cw - 24, 54, it, size=12, fill=FILL))
        F.append(arrow(cx, 132, cx, top - 4))
        F.append(arrow(cx, top + ch + 4, cx, 646))

    return render(os.path.join(IMG, 'abi-surface.svg'), W, H, *F)


# ── 2. Довжина структури як рукостискання ──────────────────────────────────
def fig_size():
    W, H = 1320, 620
    F = []

    def bar(x, y, n, extra_from, extra_label, extra_fill):
        """Смужка полів: n полів, з них із extra_from — «зайві»."""
        out = []
        fw, fg = 84, 8
        for k in range(n):
            fx = x + k * (fw + fg)
            if k >= extra_from:
                out.append(fitbox(fx, y, fw, 46, extra_label, size=11,
                                  fill=extra_fill, stroke=MUTED))
            else:
                out.append(fitbox(fx, y, fw, 46, "поле %d" % (k + 1), size=11, fill=FILL))
        return "".join(out)

    panels = [
        (40, "Програма старіша за ядро", BLU_F,
         "структура від програми · size = 24", 3, 3, "", FILL,
         "що знає ядро · sizeof = 40", 5, 3, "нулі", GRN_F,
         ["ядро добиває хвіст нулями", "й поводиться так, ніби нових", "властивостей ніхто не просив"]),
        (700, "Програма новіша за ядро", YEL_F,
         "структура від програми · size = 40", 5, 3, "нове", YEL_F,
         "що знає ядро · sizeof = 24", 3, 3, "", FILL,
         None),
    ]

    for (px, title, tfill, l1, n1, e1, lab1, f1, l2, n2, e2, lab2, f2, res) in panels:
        F.append(rect(px, 50, 580, 520, fill=BG, stroke=MUTED, sw=1.5))
        F.append(fitbox(px + 20, 66, 540, 48, title, size=15, bold=True, fill=tfill))

        F.append(text(px + 30, 152, l1, size=12, color=MUTED, anchor="start"))
        F.append(bar(px + 30, 162, n1, e1, lab1, f1))

        F.append(text(px + 30, 246, l2, size=12, color=MUTED, anchor="start"))
        F.append(bar(px + 30, 256, n2, e2, lab2, f2))

        if res:
            F.append(fitbox(px + 30, 340, 520, 96, res, size=13, fill=GRN_F, stroke=FIELD))

    # праворуч — два різні кінці
    F.append(fitbox(730, 340, 520, 88,
                    ["хвіст увесь нульовий:", "ядро працює зі своєю частиною"],
                    size=13, fill=GRN_F, stroke=FIELD))
    F.append(fitbox(730, 444, 520, 88,
                    ["у хвості щось є — прохання,", "якого ядро виконати не вміє: E2BIG"],
                    size=13, fill=RED_F, stroke=POS))

    return render(os.path.join(IMG, 'size-handshake.svg'), W, H, *F)


# ── 3. Обіцяне і те, від чого справді залежать ─────────────────────────────
def fig_declared():
    W, H = 1240, 470
    F = []

    F.append(rect(70, 90, 630, 64, fill=BLU_F, stroke=NEG, sw=1.8))
    F.append(text(385, 128, "Задокументовано як стабільне", size=15, bold=True, color=NEG))

    F.append(rect(430, 180, 740, 64, fill=GRN_F, stroke=FIELD, sw=1.8))
    F.append(text(800, 218, "Від чого справді залежать наявні програми", size=15, bold=True, color=FIELD))

    F.append(arrow(250, 158, 250, 296))
    F.append(arrow(565, 250, 565, 296))
    F.append(arrow(935, 250, 935, 296))

    F.append(fitbox(80, 300, 340, 110,
                    ["обіцяне, але нікому", "не потрібне:", "гарантія вхолосту"], size=13, fill=FILL))
    F.append(fitbox(440, 300, 250, 110,
                    ["справжня опора:", "виклики, формати,", "коди помилок"], size=13, fill=GRN_F, stroke=FIELD))
    F.append(fitbox(735, 300, 400, 110,
                    ["заморожене мовчки:", "файл у debugfs, точний текст,", "поведінка-помилка"],
                    size=13, fill=YEL_F, stroke=POS))

    return render(os.path.join(IMG, 'declared-vs-relied.svg'), W, H, *F)


# ── 4. Розкладка номера ioctl по бітах ─────────────────────────────────────
def fig_ioctl_bits():
    W, H = 1400, 660
    F = []

    segs = [
        (200, "напрям", "біти 31–30 · 2 біти", BLU_F,
         ["_IOC_NONE = 0", "_IOC_WRITE = 1", "_IOC_READ = 2"]),
        (420, "розмір структури", "біти 29–16 · 14 бітів", RED_F,
         ["sizeof того, що передають,", "до 16383 байтів;", "саме тут ховається пастка"]),
        (300, "літера підсистеми", "біти 15–8 · 8 бітів", YEL_F,
         ["'f' = 0x66 — файлові", "системи; перелік літер —", "ioctl-number.rst"]),
        (300, "номер операції", "біти 7–0 · 8 бітів", GRN_F,
         ["1 — GETFLAGS,", "2 — SETFLAGS,", "11 — FIEMAP"]),
    ]

    x = 90
    for (w, name, bits, fill, note) in segs:
        F.append(fitbox(x, 120, w, 84, [name, bits], size=14, bold=True, fill=fill))
        F.append(fitbox(x, 232, w, 108, note, size=12, fill=BG, stroke=MUTED, sw=1.2))
        x += w + 10

    F.append(text(90, 104, "32-бітне число, яке програма передає другим аргументом ioctl",
                  size=13, color=MUTED, anchor="start"))

    F.append(fitbox(90, 390, 1220, 66,
                    "_IOR('f', 1, long)  на 64-бітній машині:  sizeof(long) = 8  →  0x80086601",
                    size=16, fill=GRN_F, stroke=FIELD))
    F.append(fitbox(90, 468, 1220, 66,
                    "_IOR('f', 1, int)   той самий запит для 32-бітної:  sizeof(int) = 4  →  0x80046601",
                    size=16, fill=YEL_F, stroke=POS))
    F.append(fitbox(90, 556, 1220, 62,
                    "одна операція — два різні числа, тому в дереві ядра поруч стоять FS_IOC_GETFLAGS і FS_IOC32_GETFLAGS",
                    size=14, fill=FILL))

    return render(os.path.join(IMG, 'ioctl-number-bits.svg'), W, H, *F)


# ── 5. Початковий стан стека ───────────────────────────────────────────────
def fig_initial_stack():
    W, H = 1260, 650
    F = []

    rows = [
        (58, "рядки: аргументи, оточення, шлях AT_EXECFN, 16 байтів AT_RANDOM", YEL_F),
        (42, "AT_NULL (0) · 0  — кінець допоміжного вектора", FILL),
        (58, "допоміжний вектор: пари «ключ · значення»", BLU_F),
        (38, "NULL", FILL),
        (50, "envp[0] … envp[m−1] — вказівники на рядки оточення", GRN_F),
        (38, "NULL", FILL),
        (50, "argv[0] … argv[n−1] — вказівники на рядки аргументів", GRN_F),
        (46, "argc", RED_F),
    ]

    CX, CW = 90, 500
    y = 90
    auxv_mid = None
    argc_mid = None
    for i, (h, label, fill) in enumerate(rows):
        F.append(fitbox(CX, y, CW, h, label, size=13, fill=fill))
        if i == 2:
            auxv_mid = y + h / 2
        if i == 7:
            argc_mid = y + h / 2
        y += h + 12
    bottom = y - 12

    F.append(text(CX, 76, "↑ вищі адреси", size=12, color=MUTED, anchor="start"))
    F.append(text(CX, bottom + 26, "↓ нижчі адреси", size=12, color=MUTED, anchor="start"))

    # праворуч — таблиця ключів
    BX, BW = 650, 560
    F.append(rect(BX, 90, BW, 410, fill=BG, stroke=MUTED, sw=1.4))
    F.append(text(BX + 20, 122, "ключі допоміжного вектора — числа заморожені",
                  size=13, bold=True, anchor="start"))
    keys = [
        "AT_PHDR = 3 — адреса таблиці заголовків",
        "AT_PHENT = 4 — розмір одного заголовка",
        "AT_PHNUM = 5 — скільки їх",
        "AT_PAGESZ = 6 — розмір сторінки в байтах",
        "AT_BASE = 7 — база динамічного завантажувача",
        "AT_ENTRY = 9 — точка входу програми",
        "AT_SECURE = 23 — режим підвищених прав",
        "AT_RANDOM = 25 — адреса 16 випадкових байтів",
        "AT_SYSINFO_EHDR = 33 — база vDSO",
    ]
    for i, k in enumerate(keys):
        F.append(text(BX + 20, 162 + i * 36, k, size=13, anchor="start"))

    F.append(arrow(CX + CW + 6, auxv_mid, BX - 6, auxv_mid))
    F.append(arrow(BX - 6, argc_mid, CX + CW + 6, argc_mid))
    F.append(text(BX + 4, argc_mid + 5, "вказівник стека на вході в програму",
                  size=13, anchor="start"))

    return render(os.path.join(IMG, 'initial-stack.svg'), W, H, *F)


# ── Пастка замість коду: емуляція vsyscall (вставка hist-vsyscall-trap) ────
def fig_vsyscall_trap():
    W, H = 1400, 640
    F = []

    F.append(rect(50, 90, 330, 200, fill=BLU_F, stroke=NEG, sw=1.8))
    F.append(text(215, 122, "Статичний файл 2009 року", size=14, bold=True, color=NEG))
    F.append(text(215, 152, "у машинному коді стоїть", size=12, color=MUTED))
    F.append(text(215, 188, "call 0xffffffffff600400", size=14, bold=True))
    F.append(text(215, 224, "перезібрати його ніхто", size=12, color=MUTED))
    F.append(text(215, 248, "не буде — джерел немає", size=12, color=MUTED))

    F.append(rect(470, 70, 420, 320, fill=FILL, stroke=LINE, sw=1.8))
    F.append(text(680, 100, "Сторінка за сталою адресою", size=14, bold=True))
    F.append(text(680, 124, "позначена «виконувати не можна»", size=11, color=MUTED))

    slots = [("…ff600000", "gettimeofday"), ("…ff600400", "time"), ("…ff600800", "getcpu")]
    for i, (a, n) in enumerate(slots):
        y = 146 + i * 62
        F.append(rect(494, y, 372, 50, fill=YEL_F, stroke=MUTED, sw=1.4))
        F.append(text(514, y + 31, a, size=13, bold=True, anchor="start"))
        F.append(text(846, y + 31, n, size=13, color=MUTED, anchor="end"))

    F.append(text(680, 366, "між входами — добивка байтами 0xcc", size=11, color=MUTED))

    F.append(rect(980, 70, 370, 320, fill=GRN_F, stroke=FIELD, sw=1.8))
    F.append(text(1165, 102, "Ядро, обробник збою", size=14, bold=True, color=FIELD))
    steps = [
        "1 · це вибірка інструкції?",
        "2 · адреса — точно вхід?",
        "3 · зняти адресу повернення",
        "     з верхівки стека процесу",
        "4 · виконати справжній виклик",
        "5 · повернути керування туди,",
        "     звідки прийшли",
    ]
    for i, s in enumerate(steps):
        F.append(text(1004, 146 + i * 33, s, size=12, anchor="start"))

    F.append(arrow(380, 190, 494, 190))
    F.append(text(437, 176, "виклик", size=11, color=MUTED))
    F.append(arrow(890, 190, 980, 190))
    F.append(text(935, 176, "збій", size=11, color=MUTED))

    F.append(line(1165, 390, 1165, 448, color=FIELD, sw=2))
    F.append(line(1165, 448, 215, 448, color=FIELD, sw=2))
    F.append(arrow(215, 448, 215, 292, color=FIELD, sw=2))
    F.append(text(690, 436, "відповідь така сама, як була у 2009-му — лише повільніша",
                  size=12, color=FIELD))

    F.append(rect(50, 496, 700, 106, fill=RED_F, stroke=POS, sw=1.8))
    F.append(text(400, 528, "Стрибок у середину сторінки — те, заради чого її брали в атаках",
                  size=13, bold=True, color=POS))
    F.append(text(400, 558, "адреса не збігається з жодним входом: ядро не емулює нічого,",
                  size=12))
    F.append(text(400, 582, "процес дістає звичайний SIGSEGV", size=12))

    F.append(arrow(756, 549, 894, 549, color=POS))
    F.append(rect(900, 508, 450, 82, fill=FILL, stroke=POS, sw=1.6))
    F.append(text(1125, 542, "жодного байта сторінки процесор не виконує —", size=12))
    F.append(text(1125, 566, "виконуваного гаджета за сталою адресою немає", size=12))

    return render(os.path.join(IMG, 'vsyscall-trap.svg'), W, H, *F,
                  title="Що зробили з дверима, які не можна ні лишити, ні прибрати")


# ── Режими vsyscall у часі (вставка hist-vsyscall-trap) ────────────────────
def fig_vsyscall_modes():
    W, H = 1500, 400
    F = []

    F.append(line(80, 268, 1420, 268, color=LINE, sw=2))

    marks = [
        ("2002 · серія 2.5", ["натив: у сторінці", "справжній код", "із syscall"], YEL_F, MUTED),
        ("2011 · 3.1", ["емуляція: код лишили,", "сторінку позначили", "«не виконувати»"], BLU_F, NEG),
        ("2018 · 4.17", ["натив прибрано:", "несумісний з ізоляцією", "таблиць сторінок"], BLU_F, NEG),
        ("2019 · 5.3", ["xonly типово:", "виконувати — так,", "читати — ні"], GRN_F, FIELD),
        ("2022", ["конфіг «емуляція»", "прибрано: лишились", "xonly і none"], GRN_F, FIELD),
        ("сьогодні", ["частина систем ставить", "none — старі образи", "падають на старті"], RED_F, POS),
    ]

    x0, bw = 80, 215
    step = (1340 - bw) / (len(marks) - 1)
    for i, (year, lines, fill, col) in enumerate(marks):
        cx = x0 + bw / 2 + i * step
        F.append(fitbox(cx - bw / 2, 92, bw, 110, lines, size=12, fill=fill, stroke=col, sw=1.6))
        F.append(line(cx, 202, cx, 258, color=col, sw=1.6, dash="4,4"))
        F.append(circle(cx, 268, 7, fill=fill, stroke=col, sw=2))
        F.append(text(cx, 304, year, size=13, bold=True, color=col))

    F.append(text(750, 356, "кожен крок забирає лише те, чого ядро ніколи не обіцяло: "
                            "швидкість, виконуваність, читаність",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'vsyscall-modes.svg'), W, H, *F,
                  title="Двадцять років повільного зачинення дверей")


# ── Прохід ланцюгом атрибутів «довжина–тип–дані» ───────────────────────────
def fig_tlv():
    W, H = 1200, 490
    F = []

    F.append(text(600, 66,
                  "Хвіст повідомлення: ланцюг «довжина–тип–дані», який можна читати, не знаючи жодного типу",
                  size=14, color=MUTED))

    y, h = 175, 66
    blocks = [
        (60, 112, ["len = 10", "2 Б"], BLU_F),
        (172, 112, ["type = 3", "2 Б"], BLU_F),
        (284, 252, ["корисні дані", "6 Б"], FILL),
        (536, 112, ["заповнювач", "2 Б"], YEL_F),
        (648, 112, ["len = 12", "2 Б"], BLU_F),
        (760, 112, ["type = 7", "2 Б"], BLU_F),
        (872, 268, ["корисні дані", "8 Б"], FILL),
    ]
    for (bx, bw, label, fill) in blocks:
        F.append(fitbox(bx, y, bw, h, label, size=12, fill=fill, stroke=MUTED))

    for (x1, x2, cap) in ((60, 648, "атрибут A · крок = ALIGN(10) = 12 Б"),
                          (648, 1140, "атрибут B · крок = ALIGN(12) = 12 Б")):
        F.append(line(x1, 150, x2, 150, color=MUTED, sw=1.4))
        F.append(line(x1, 150, x1, 166, color=MUTED, sw=1.4))
        F.append(line(x2, 150, x2, 166, color=MUTED, sw=1.4))
        F.append(text((x1 + x2) / 2, 138, cap, size=12, color=MUTED))

    F.append(text(60, 268, "off = 0", size=12, anchor="start"))
    F.append(text(652, 268, "off = 12", size=12, anchor="start"))
    F.append(text(1140, 268, "off = 24 == len → кінець", size=12, anchor="end"))
    F.append(arrow(64, 292, 640, 292))
    F.append(arrow(656, 292, 1132, 292))

    F.append(fitbox(60, 336, 520, 118,
                    ["у ПРОХАННІ невідомий type — відмова:",
                     "виконати не зможемо, а мовчки",
                     "проігнорувати не маємо права"],
                    size=13, fill=RED_F, stroke=POS))
    F.append(fitbox(620, 336, 520, 118,
                    ["у ЗВІТІ невідомий type — переступити",
                     "через нього за довжиною й читати далі:",
                     "зайвий факт нікому не шкодить"],
                    size=13, fill=GRN_F, stroke=FIELD))

    return render(os.path.join(IMG, 'tlv-walk.svg'), W, H, *F,
                  title="Прохід ланцюгом атрибутів")


if __name__ == '__main__':
    for f in (fig_surface, fig_size, fig_declared, fig_ioctl_bits, fig_initial_stack,
              fig_vsyscall_trap, fig_vsyscall_modes, fig_tlv):
        print(f())
