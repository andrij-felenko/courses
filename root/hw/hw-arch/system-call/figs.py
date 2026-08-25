# -*- coding: utf-8 -*-
"""Фігури для теми «Системний виклик»."""
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


def box(cx, cy, s, **kw):
    """textbox із центром (cx,cy) — повертає лише SVG-фрагмент."""
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag


# ── 1. Три спроби потрапити в код ядра ─────────────────────────────────────
def fig_three_attempts():
    W, H = 1240, 660
    F = []

    KX, KW = 680, 300          # панель «код ядра»
    RH = 36                    # висота рядка панелі
    VX, VW = 1010, 210         # колонка присуду

    rows = [
        dict(
            title="1. Звичайний виклик підпрограми",
            left="Застосунок\nрівень 3",
            mid=["стрибок за адресою,", "рівень НЕ міняється"],
            hit=0,
            arrow_color=NEG,
            verdict=["Рівень так і лишився 3.",
                     "Ядро падає на першій же",
                     "привілейованій команді."],
            ok=False,
        ),
        dict(
            title="2. Виклик, що сам піднімає рівень",
            left="Застосунок\nрівень 3",
            mid=["рівень піднімає апаратура,", "але адресу обирає той,", "хто просить"],
            hit=2,
            arrow_color=POS,
            verdict=["Указано адресу одразу",
                     "після перевірок —",
                     "захисту не існує."],
            ok=False,
        ),
        dict(
            title="3. Команда-пастка (syscall / svc / ecall)",
            left="Застосунок\nрівень 3",
            mid=["у регістрі — НОМЕР послуги;", "адресу входу апаратура бере", "з регістра, який пише ядро"],
            hit=0,
            arrow_color=FIELD,
            verdict=["Вхід завжди згори,",
                     "перевірки не обійти.",
                     "Так і має бути."],
            ok=True,
        ),
    ]

    krows = ["перевірити права", "перевірити межі", "виконати запис"]

    for i, r in enumerate(rows):
        top = 64 + i * 196
        cy = top + 1.5 * RH
        # заголовок спроби
        F.append(text(46, top - 16, r["title"], size=15, bold=True, anchor="start"))
        F.append(text(KX + KW / 2, top - 16, "код ядра", size=12, color=MUTED))
        # ліворуч — застосунок
        F.append(box(126, cy, r["left"], size=13, fill=BLU_F, min_w=160))
        # посередині — механіка
        F.append(box(440, cy, r["mid"], size=13, fill=YEL_F, min_w=300))
        # панель ядра — три суміжні рядки
        for j, kr in enumerate(krows):
            fill = RED_F if (i == 1 and j < 2) else FILL
            F.append(fitbox(KX, top + j * RH, KW, RH, kr, size=13, fill=fill))
        # стрілки
        F.append(arrow(212, cy, 268, cy, color=LINE, sw=2))
        F.append(arrow(614, cy, KX - 8, top + r["hit"] * RH + RH / 2,
                       color=r["arrow_color"], sw=2.4))
        # присуд
        F.append(fitbox(VX, cy - 46, VW, 92, r["verdict"], size=12,
                        fill=(GRN_F if r["ok"] else RED_F),
                        stroke=(FIELD if r["ok"] else POS)))

    render(os.path.join(IMG, 'three-attempts.svg'), W, H, *F,
           title="Три способи потрапити в код ядра — і чому вцілів лише третій")


# ── 2. Що змінюється в мить переходу ───────────────────────────────────────
def fig_crossing():
    W, H = 1240, 580
    F = []

    C1, W1 = 46, 210
    C2, W2 = 286, 290
    C3, W3 = 606, 340
    C4, W4 = 976, 218

    head = [("Складова стану", C1, W1), ("До переходу — код користувача", C2, W2),
            ("Після переходу — код ядра", C3, W3), ("Хто це робить", C4, W4)]
    for s, x, w in head:
        F.append(fitbox(x, 58, w, 44, s, size=13, bold=True, fill=BLU_F))

    rows = [
        ("Рівень привілею",
         ["рівень 3:", "небезпечні команди заборонені"],
         ["рівень 0:", "повна влада над машиною"],
         "апаратура"),
        ("Лічильник команд",
         ["наступна команда", "самої програми"],
         ["адреса з IA32_LSTAR —", "її записало ядро при старті"],
         "апаратура"),
        ("Прапорці",
         ["такі, як лишила", "програма"],
         ["небезпечні біти згашено", "маскою IA32_FMASK"],
         "апаратура"),
        ("Покажчик стека",
         ["стек програми —", "довіри йому немає"],
         ["окремий стек ядра", "саме цієї задачі"],
         ["ARM64 — апаратура;", "x86-64 — перші", "команди ядра"]),
    ]

    y = 116
    RH = 82
    for name, a, b, who in rows:
        F.append(fitbox(C1, y, W1, RH, name, size=13, bold=True))
        F.append(fitbox(C2, y, W2, RH, a, size=12, fill=BLU_F))
        F.append(fitbox(C3, y, W3, RH, b, size=12, fill=GRN_F))
        F.append(fitbox(C4, y, W4, RH, who, size=12, fill=YEL_F))
        y += RH + 8

    F.append(fitbox(C1, y + 14, W - 2 * C1, 56,
                    ["Куди сховано дорогу назад: x86-64 — адреса повернення в rcx, старі прапорці в r11;",
                     "ARM64 — ELR_EL1 і SPSR_EL1; RISC-V — sepc. Парна команда повернення читає це й опускає рівень."],
                    size=12, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'crossing.svg'), W, H, *F,
           title="Одна команда — чотири зміни стану машини воднораз")


# ── 3. Подвійне читання аргументу ──────────────────────────────────────────
def fig_double_fetch():
    W, H = 1140, 560
    F = []

    T0, T1 = 300, 1092         # межі часової осі
    TSW = 748                  # мить підміни

    F.append(text(46, 108, "Ядро", size=14, bold=True, anchor="start"))
    F.append(text(46, 128, "обробник виклику", size=12, color=MUTED, anchor="start"))
    F.append(text(46, 296, "len у пам'яті", size=14, bold=True, anchor="start"))
    F.append(text(46, 316, "програми", size=14, bold=True, anchor="start"))
    F.append(text(46, 434, "Другий потік", size=14, bold=True, anchor="start"))
    F.append(text(46, 454, "тієї самої програми", size=12, color=MUTED, anchor="start"))

    # вісь часу
    F.append(arrow(T0 - 20, 496, T1, 496, color=MUTED, sw=1.6))
    F.append(text(T1 - 30, 520, "час", size=12, color=MUTED, anchor="end"))

    # верхня доріжка — кроки ядра
    F.append(box(390, 148, ["читає len", "→ 64"], size=13, fill=BLU_F))
    F.append(box(614, 148, "перевіряє: 64 ≤ 64 — гаразд", size=13, fill=BLU_F))
    F.append(box(936, 148, ["читає len ВДРУГЕ → 4096", "і копіює 4096 Б", "у буфер на 64 Б"],
                 size=13, fill=RED_F, stroke=POS))

    # смуга значення
    F.append(fitbox(T0, 264, TSW - T0, 48, "len = 64", size=14, bold=True, fill=GRN_F, stroke=FIELD))
    F.append(fitbox(TSW, 264, T1 - TSW, 48, "len = 4096", size=14, bold=True, fill=RED_F, stroke=POS))

    # нижня доріжка — чужий потік
    F.append(box(TSW, 414, "пише len = 4096", size=13, fill=YEL_F, stroke=POS))

    # мить підміни
    F.append(line(TSW, 190, TSW, 258, color=POS, sw=1.6, dash="5 4"))
    F.append(line(TSW, 318, TSW, 386, color=POS, sw=1.6, dash="5 4"))

    render(os.path.join(IMG, 'double-fetch.svg'), W, H, *F,
           title="Перевірка стосується першого читання, копіювання — другого")


# ── 4. Чотири щаблі уникання перетинів ─────────────────────────────────────
def fig_avoid_crossings():
    W, H = 1180, 560
    F = []

    C1, W1 = 44, 262
    BX, BW = 326, 500
    C3, W3 = 846, 292

    F.append(fitbox(C1, 58, W1, 42, "Підхід", size=13, bold=True, fill=BLU_F))
    F.append(fitbox(BX, 58, BW, 42, "Перетини межі на тисячу операцій", size=13, bold=True, fill=BLU_F))
    F.append(fitbox(C3, 58, W3, 42, "Скільки їх виходить", size=13, bold=True, fill=BLU_F))

    rows = [
        (["Виклик ядра", "на кожну операцію"], 40, FILL, ["1000 перетинів —", "повна ціна щоразу"]),
        (["Буфер у просторі", "користувача"], 4, FILL, ["≈1 перетин", "на 4 КіБ даних"]),
        (["vDSO: дані ядра", "видно на читання"], 0, GRN_F, ["0 — межу", "не перетнуто взагалі"]),
        (["Кільця подань", "у спільній пам'яті"], 1, GRN_F, ["1 на сотні операцій,", "а в режимі опитування — 0"]),
    ]

    y = 122
    RH = 78
    for name, ticks, bfill, note in rows:
        F.append(fitbox(C1, y, W1, RH, name, size=13, bold=True))
        F.append(rect(BX, y + 14, BW, RH - 28, fill=bfill, stroke=MUTED, sw=1.2))
        if ticks:
            step = BW / (ticks + 1.0)
            for k in range(1, ticks + 1):
                F.append(line(BX + k * step, y + 16, BX + k * step, y + RH - 16,
                              color=POS, sw=2.2))
        F.append(fitbox(C3, y, W3, RH, note, size=12, fill=YEL_F))
        y += RH + 12

    F.append(fitbox(C1, y + 12, W - 2 * C1, 48,
                    "Жоден зі щаблів не робить перехід дешевшим — усі роблять переходів менше.",
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'avoid-crossings.svg'), W, H, *F,
           title="Чотири щаблі уникання перетинів межі")


# ── 5. Родовід команди-пастки (для вставки hist-trap-instruction) ──────────
def fig_trap_lineage():
    W, H = 1340, 640
    F = []

    CW = 206
    X = [40, 288, 536, 800]          # ліві краї колонок 1..4
    X5, CW5 = 1080, 220

    def cap(x, w, y, s):
        fs = fit_font(s, w, 15, True)
        return text(x + w / 2, y, s, size=fs, color=MUTED, bold=True)

    # спільний стовбур: три віхи
    trunk = [
        (X[0], "1962 · Atlas", [
            "екстракод",
            "номер функції —",
            "у самій команді",
            "≈250 кодів із 512,",
            "близько половини —",
            "функції супервізора",
        ], BLU_F),
        (X[1], "1964 · IBM System/360", [
            "SVC n",
            "8-бітний номер",
            "прямо в байті команди",
            "стеля — 256 послуг",
            "проблемний стан",
            "проти супервізорного",
        ], BLU_F),
        (X[2], "1991 · Linux 0.01", [
            "int 0x80",
            "вектор — у команді,",
            "номер послуги — в EAX",
            "стелю номерів знято",
            "але кожен вхід іде",
            "через таблиці в пам'яті",
        ], BLU_F),
    ]
    TY, TH = 225, 190
    for x, title, lines, fill in trunk:
        F.append(cap(x, CW, TY - 14, title))
        F.append(fitbox(x, TY, CW, TH, "\n".join(lines), size=13, fill=fill))

    # розкол: дві швидкі пари
    UY, LY, BH = 88, 380, 178
    F.append(cap(X[3], CW, UY - 14, "1997 · Intel Pentium II"))
    F.append(fitbox(X[3], UY, CW, BH, "\n".join([
        "SYSENTER / SYSEXIT",
        "вхід — із трьох MSR",
        "жодного звернення",
        "до таблиць",
        "не зберігає ні адреси",
        "повернення, ні стека",
    ]), size=13, fill=RED_F))

    F.append(cap(X[3], CW, LY - 14, "1997–98 · AMD K6"))
    F.append(fitbox(X[3], LY, CW, BH, "\n".join([
        "SYSCALL / SYSRET",
        "вхід — із MSR LSTAR,",
        "селектори — зі STAR",
        "RIP → RCX,",
        "RFLAGS → R11",
        "стек ядро ставить саме",
    ]), size=13, fill=GRN_F))

    # перетин
    F.append(cap(X5, CW5, 186, "2003–2004 · x86-64"))
    F.append(fitbox(X5, 200, CW5, 240, "\n".join([
        "AMD не має SYSENTER",
        "у довгому режимі;",
        "Intel не має SYSCALL",
        "у сумісному.",
        "",
        "Перетин у 64 бітах —",
        "лише SYSCALL,",
        "у 32-бітному сумісному —",
        "лише SYSENTER",
    ]), size=13, fill=YEL_F))

    MY = TY + TH / 2
    F.append(arrow(X[0] + CW, MY, X[1] - 6, MY, color=LINE))
    F.append(arrow(X[1] + CW, MY, X[2] - 6, MY, color=LINE))
    F.append(arrow(X[2] + CW, MY, X[3] - 6, UY + BH / 2 + 18, color=POS))
    F.append(arrow(X[2] + CW, MY, X[3] - 6, LY + BH / 2 - 18, color=FIELD))
    F.append(arrow(X[3] + CW, UY + BH / 2, X5 - 6, 268, color=POS))
    F.append(arrow(X[3] + CW, LY + BH / 2, X5 - 6, 372, color=FIELD))

    F.append(fitbox(40, 570, W - 80, 44,
                    "Номер послуги переїхав із самої команди в регістр, а адреса входу — "
                    "з таблиці в пам'яті в регістр процесора.",
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'trap-lineage.svg'), W, H, *F,
           title="Родовід команди-пастки: від екстракодів Atlas до x86-64")


# ── 6. Три входи в ядро на x86: що робить апаратура ────────────────────────
def fig_fast_pairs():
    W, H = 1300, 690
    F = []

    LX, LW = 30, 300
    CX = [340, 650, 960]
    CWD = 300

    HY, HH = 26, 74
    F.append(fitbox(LX, HY, LW, HH, "Що робить апаратура",
                    size=14, bold=True, fill=FILL, color=MUTED))
    heads = [
        ("INT 0x80\nвектор загального\nпризначення", BLU_F),
        ("SYSENTER / SYSEXIT\nIntel, 1997", RED_F),
        ("SYSCALL / SYSRET\nAMD, 1997–98", GRN_F),
    ]
    for x, (s, fill) in zip(CX, heads):
        F.append(fitbox(x, HY, CWD, HH, s, size=14, bold=True, fill=fill))

    rows = [
        ("Звідки адреса входу",
         "з дескриптора в таблиці IDT",
         "з регістра\nIA32_SYSENTER_EIP",
         "з регістра IA32_LSTAR"),
        ("Що читає з пам'яті",
         "дескриптор IDT,\nпотім CS із GDT",
         "нічого",
         "нічого"),
        ("Адреса повернення",
         "CS:EIP лягає\nна стек ядра",
         "не зберігається взагалі",
         "у регістрі RCX"),
        ("Прапорці",
         "EFLAGS лягають\nна стек ядра",
         "не зберігаються",
         "у регістрі R11"),
        ("Стек ядра",
         "апаратура бере SS:ESP\nіз TSS",
         "з IA32_SYSENTER_ESP",
         "ядро перемикає само"),
        ("Як вертаються",
         "IRET знімає все\nзі стека",
         "SYSEXIT — у EDX:ECX,\nякі мусить дати ОС",
         "SYSRET — із RCX і R11"),
    ]

    y, RH = HY + HH + 12, 72
    for label, a, b, c in rows:
        F.append(fitbox(LX, y, LW, RH, label, size=13, bold=True, fill=FILL))
        for x, s, fill in zip(CX, (a, b, c), (BG, BG, BG)):
            F.append(fitbox(x, y, CWD, RH, s, size=13, fill=fill))
        y += RH + 10

    F.append(fitbox(LX, y + 8, W - 2 * LX, 44,
                    "Швидкість обох пар — з одного джерела: вони не читають із пам'яті нічого. "
                    "Різняться лише тим, що лишають по собі.",
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'fast-pairs.svg'), W, H, *F,
           title="Три входи в ядро на x86: що бере на себе апаратура")


# ── Одне число: результат чи помилка ───────────────────────────────────────
def fig_retval_window():
    W, H = 1280, 560
    F = []

    BX, BY, BW, BH = 70, 120, 1140, 78
    ERR_W = 34                      # вузенький хвостик — остання сторінка
    F.append(rect(BX, BY, BW - ERR_W, BH, fill=GRN_F, stroke=FIELD, sw=2))
    F.append(rect(BX + BW - ERR_W, BY, ERR_W, BH, fill=RED_F, stroke=POS, sw=2))
    F.append(mtext(BX + (BW - ERR_W) / 2, BY + BH / 2 - 2,
                   ["ЗАКОННИЙ РЕЗУЛЬТАТ", "кількість байтів · номер дескриптора · адреса"],
                   size=15))

    F.append(text(BX, BY - 44, "0", size=13, color=MUTED, anchor="start"))
    F.append(text(BX + BW, BY - 44, "2⁶⁴ − 1", size=13, color=MUTED, anchor="end"))
    F.append(text(BX + BW / 2, BY - 44,
                  "усе, що поміщається в rax (x86-64) або x0 (aarch64)",
                  size=13, color=MUTED))

    # Виноска до збільшеного хвоста
    ZX, ZY, ZW, ZH = 320, 306, 880, 100
    F.append(line(BX + BW - ERR_W, BY + BH, ZX, ZY, color=POS, sw=1.4, dash="5,4"))
    F.append(line(BX + BW, BY + BH, ZX + ZW, ZY, color=POS, sw=1.4, dash="5,4"))
    F.append(text(ZX + ZW / 2, ZY - 20,
                  "остання сторінка, збільшено: рівно 4096 значень", size=14, bold=True))

    cell = ZW / 3.0
    F.append(fitbox(ZX, ZY, cell, ZH,
                    ["−4096", "(тобто 2⁶⁴ − 4096)", "не вживають"],
                    size=13, fill=FILL, color=MUTED))
    F.append(fitbox(ZX + cell, ZY, cell, ZH,
                    ["−4095 … −2", "коди помилок", "4095 … 2"], size=13, fill=RED_F))
    F.append(fitbox(ZX + 2 * cell, ZY, cell, ZH,
                    ["−1", "код помилки 1", "(EPERM)"], size=13, fill=RED_F))

    F.append(fitbox(60, ZY - 8, 220, ZH + 16,
                    ["Ядро ніколи не віддає", "цю сторінку. Тому жодна", "законна адреса сюди", "не влучить."],
                    size=12, fill=YEL_F))

    F.append(fitbox(320, 466, 880, 64,
                    ["Уся перевірка — одне беззнакове порівняння:",
                     "r > −4096UL   ⇒   це помилка, errno = −r"],
                    size=14, fill=BLU_F, bold=True))

    render(os.path.join(IMG, 'retval-window.svg'), W, H, *F,
           title="Одне число назад: помилці віддано рівно одну сторінку значень")


# ── Чому четвертий аргумент їде в r10 ──────────────────────────────────────
def fig_rcx_clobber():
    W, H = 1300, 630
    F = []

    PW, PH = 590, 496
    PX = [50, 670]
    titles = ["Так, як велить ЗВИЧАЙНА угода System V",
              "Так, як велить угода СИСТЕМНОГО ВИКЛИКУ"]
    a4regs = ["rcx", "r10"]
    after = [
        (["rcx = адреса повернення", "четвертого аргументу більше немає"], RED_F, POS),
        (["rcx = адреса повернення", "r10 = четвертий аргумент, цілий"], GRN_F, FIELD),
    ]
    verdicts = [
        ["Аргумент зник ще до того, як ядро його прочитало.",
         "openat(fd, path, flags, mode) створить файл",
         "із випадковими правами."],
        ["Команда не чіпає r10 — аргумент доїжджає.",
         "Зате rcx і r11 мусять стояти у списку затертих:",
         "компілятор сам не знає, що команда їх псує."],
    ]

    for k in (0, 1):
        x = PX[k]
        F.append(rect(x, 58, PW, PH, fill=BG, stroke=MUTED, sw=1.6))
        F.append(fitbox(x + 20, 74, PW - 40, 46, titles[k], size=13, bold=True,
                        fill=(RED_F if k == 0 else GRN_F)))

        F.append(text(x + PW / 2, 156, "у регістрах перед командою", size=12, color=MUTED))
        chips = [("rdi", "арг 1"), ("rsi", "арг 2"), ("rdx", "арг 3"), (a4regs[k], "арг 4")]
        cw, gap = 124, 10
        x0 = x + (PW - (4 * cw + 3 * gap)) / 2
        for i, (r, a) in enumerate(chips):
            hot = (i == 3)
            F.append(fitbox(x0 + i * (cw + gap), 174, cw, 58, [r, a], size=13,
                            fill=(YEL_F if hot else FILL),
                            stroke=(POS if (hot and k == 0) else (FIELD if hot else LINE))))

        F.append(arrow(x + PW / 2, 238, x + PW / 2, 258, color=INK))
        F.append(fitbox(x + 70, 262, PW - 140, 44,
                        "syscall:  RCX := RIP,  R11 := RFLAGS", size=13, fill=BLU_F))
        F.append(arrow(x + PW / 2, 310, x + PW / 2, 330, color=INK))

        F.append(text(x + PW / 2, 350, "у регістрах одразу після команди", size=12, color=MUTED))
        txt, fill, stroke = after[k]
        F.append(fitbox(x + 30, 360, PW - 60, 64, txt, size=12.5, fill=fill, stroke=stroke))

        F.append(fitbox(x + 20, 442, PW - 40, 88, verdicts[k], size=12, fill=FILL))

    render(os.path.join(IMG, 'rcx-clobber.svg'), W, H, *F,
           title="Чому четвертий аргумент їде в r10, а rcx і r11 оголошують затертими")


def fig_abi_stack_switch():
    W, H = 1340, 560
    F = []

    LX, LW = 30, 210          # колонка «архітектура»
    TX, TW = 265, 640         # доріжка «перші команди обробника»
    NX, NW = 925, 385         # колонка приміток
    LH = 78                   # висота доріжки
    STEP = 100
    Y0 = 92

    F.append(text(LX + LW / 2, 62, "архітектура", size=13, color=MUTED, bold=True))
    F.append(text(TX + TW / 2, 62, "перші команди обробника", size=13, color=MUTED, bold=True))
    F.append(text(NX + NW / 2, 62, "хто ставить покажчик стека ядра", size=13, color=MUTED, bold=True))
    F.append(text(TX - 12, 84, "пастка", size=11, color=POS))

    lanes = [
        ("x86-64\nsyscall", 168,
         "swapgs підмінює базу GS на ядерну,\nз неї дістають sp — і лише тоді\nстек перестає бути чужим"),
        ("aarch64\nsvc #0", 0,
         "при вході в EL1 апаратура сама\nбере SP_EL1 — жодної команди\nна стеку програми"),
        ("riscv64\necall", 148,
         "csrrw міняє tp зі sscratch, а sp\nдістають уже з task-структури —\nтеж вручну"),
        ("i386\nint $0x80", 0,
         "апаратура бере ss0:esp0 із TSS\nще до першої команди\nобробника"),
    ]

    for i, (name, red_w, note) in enumerate(lanes):
        y = Y0 + i * STEP
        F.append(fitbox(LX, y, LW, LH, name, size=15, bold=True, fill=BLU_F))
        F.append(line(TX - 12, y + 6, TX - 12, y + LH - 6, color=POS, sw=3))
        if red_w:
            F.append(fitbox(TX, y, red_w, LH, "на стеку\nпрограми", size=12,
                            fill=RED_F, stroke=POS, color=POS, bold=True))
        F.append(fitbox(TX + red_w, y, TW - red_w, LH, "на стеку ядра", size=13,
                        fill=GRN_F, stroke=FIELD, color=FIELD, bold=True))
        F.append(fitbox(NX, y, NW, LH, note, size=12, fill=YEL_F))

    F.append(fitbox(LX, Y0 + 4 * STEP + 6, W - 2 * LX, 46,
                    "Червоне — команди ядра, що виконуються ще на стеку, який лишила програма: "
                    "вузьке вікно, де кожен рядок пишуть з особливою обережністю.",
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'abi-stack-switch.svg'), W, H, *F,
           title="Стек ядра: де його перемикає апаратура, а де ядро мусить саме")


# ── Драбина цін: скільки коштує спитати ────────────────────────────────────
def fig_cost_ladder():
    import math
    W, H = 1280, 520
    F = []

    LX, LW = 40, 292               # колонка назв
    AX0, AX1 = 350, 1140           # вісь
    LO, HI = 0.5, 1000.0           # наносекунди, логарифмічна шкала
    SPAN = math.log10(HI / LO)
    PX = (AX1 - AX0) / SPAN

    def x_of(v):
        return AX0 + PX * math.log10(v / LO)

    Y0, STEP, RH, BH = 78, 72, 48, 34

    rows = [
        (["звичайний виклик", "функції"], 1.0, "≈ 1 нс", GRN_F, FIELD),
        (["clock_gettime", "через vDSO"], 20.0, "13…24 нс", BLU_F, NEG),
        (["голий syscall,", "пом'якшення вимкнено"], 90.0, "< 100 нс", YEL_F, MUTED),
        (["голий syscall,", "пом'якшення ввімкнено"], 550.0, "440…660 нс", RED_F, POS),
    ]

    for i, (name, val, label, fill, stroke) in enumerate(rows):
        y = Y0 + i * STEP
        F.append(fitbox(LX, y, LW, RH, name, size=13, fill=FILL))
        xe = x_of(val)
        F.append(rect(AX0, y + (RH - BH) / 2, xe - AX0, BH, fill=fill, stroke=stroke, sw=2))
        F.append(text(xe + 14, y + RH / 2 + 5, label, size=13, anchor="start", bold=True))

    # вісь під смугами: підписи стоять НИЖЧЕ лінії, тому нічого не перетинають
    BASE = Y0 + 4 * STEP - 12
    F.append(line(AX0, BASE, AX1, BASE, color=MUTED, sw=1.5))
    for v, cap in ((1, "1 нс"), (10, "10 нс"), (100, "100 нс"), (1000, "1 мкс")):
        x = x_of(v)
        F.append(line(x, BASE, x, BASE + 9, color=MUTED, sw=1.5))
        F.append(text(x, BASE + 28, cap, size=13, color=MUTED))

    F.append(fitbox(LX, BASE + 52, W - 2 * LX, 62,
                    ["Вісь логарифмічна: кожна поділка — удесятеро. "
                     "Значення — з опублікованих вимірів на різних машинах, а не константи архітектури;",
                      "власні числа завжди інші, стала лише відстань між щаблями."],
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'cost-ladder.svg'), W, H, *F,
           title="Скільки коштує спитати: три способи на логарифмічній осі")


if __name__ == '__main__':
    fig_three_attempts()
    fig_crossing()
    fig_double_fetch()
    fig_avoid_crossings()
    fig_trap_lineage()
    fig_fast_pairs()
    fig_retval_window()
    fig_rcx_clobber()
    fig_abi_stack_switch()
    fig_cost_ladder()
    print("ok:", os.listdir(IMG))
