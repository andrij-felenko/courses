# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки під уже усталений вигляд цих фігур (рамки-світлі заливки).
BLUE   = "#1f47b5"
RED    = "#c0271e"
GREEN  = "#1f8a3b"
GOLD   = "#b8860b"
F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"


# ── contract: ISA — мова-контракт між софтом і залізом ────────────────────────
# Ідея: ISA лежить посередині й розділяє два світи — програми згори, залізо знизу;
# домовившись про мову, обидві сторони вільні розвиватися окремо.

def fig_contract():
    W, H = 760, 380
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Набір інструкцій (ISA) — мова-контракт між програмами й залізом",
                  size=16, bold=True))
    p.append(text(cx, 52, "повний словник команд процесора плюс правило, як кожну закодувати числом",
                  size=11, color=MUTED, italic=True))

    # софт згори
    p.append(rect(150, 78, 460, 56, fill=F_BLUE, stroke=BLUE, sw=2, rx=12))
    p.append(text(cx, 100, "ПРОГРАМИ (софт)", size=13, color=BLUE, bold=True))
    p.append(text(cx, 121, "застосунки, ОС, ваш код — усе зрештою зводиться до інструкцій",
                  size=10, color=MUTED))
    p.append(arrow(cx, 136, cx, 168, color=INK, sw=2.2))
    p.append(text(cx + 96, 158, "говорять інструкціями", size=10, color=MUTED, italic=True, anchor="start"))

    # ISA посередині
    p.append(rect(120, 172, 520, 70, fill=F_GRN, stroke=GREEN, sw=2.4, rx=12))
    p.append(text(cx, 196, "ISA — набір інструкцій", size=14, color=GREEN, bold=True))
    p.append(text(cx, 216, "ADD, LD, ST, JMP, CMP…  +  як саме кожна закодована в біти",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 233, "сталий контракт: софт пише такі команди, залізо вміє їх виконувати",
                  size=10, color=MUTED, italic=True))
    p.append(arrow(cx, 244, cx, 276, color=INK, sw=2.2))
    p.append(text(cx + 96, 266, "залізо виконує", size=10, color=MUTED, italic=True, anchor="start"))

    # залізо знизу
    p.append(rect(150, 280, 460, 56, fill=F_RED, stroke=RED, sw=2, rx=12))
    p.append(text(cx, 302, "ЗАЛІЗО (процесор)", size=13, color=RED, bold=True))
    p.append(text(cx, 323, "транзистори, що декодують і виконують саме ці команди",
                  size=10, color=MUTED))

    p.append(text(cx, 362, "ISA — межа між «що робити» (софт) і «як це зроблено» (залізо): домовилися про мову — і обидві сторони вільні.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "contract.svg"), W, H, *p)


# ── encoding: команда — число, розбите на поля ────────────────────────────────
# Ідея: одна 16-бітна команда «ДОДАЙ R3←R1+R2» = чотири поля по 4 біти; усі
# разом дають число 0x1312, яке й лежить у пам'яті як команда.

def fig_encoding():
    W, H = 760, 420
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Анатомія машинної команди: число, розбите на поля", size=16, bold=True))
    p.append(text(cx, 52, "біти команди діляться на поля: КОД операції (що робити) і ОПЕРАНДИ (над чим) — схема спрощена",
                  size=11, color=MUTED, italic=True))
    p.append(text(cx, 88, "людською:  ДОДАЙ R3 ← R1 + R2   (ADD R3, R1, R2)", size=13.5, bold=True))
    p.append(arrow(cx, 100, cx, 130, color=INK, sw=2))

    fields = [
        (120, "0001", "код операції", "ADD = додати", RED, F_RED),
        (280, "0011", "призначення", "R3", GREEN, F_GRN),
        (440, "0001", "операнд 1", "R1", BLUE, F_BLUE),
        (600, "0010", "операнд 2", "R2", BLUE, F_BLUE),
    ]
    fw = 130
    for fx, bits, lab, sub, col, fill in fields:
        cxf = fx + fw / 2
        p.append(text(cxf, 142, lab, size=11, color=col, bold=True))
        p.append(rect(fx, 150, fw, 54, fill=fill, stroke=col, sw=2, rx=6))
        p.append(text(cxf, 184, bits, size=15, color=INK, bold=True))
        p.append(text(cxf, 224, sub, size=11, color=MUTED))

    p.append(text(cx, 250, "16 бітів = 4 поля по 4 біти (4 hex-цифри)", size=11, color=MUTED, italic=True))
    p.append(text(cx, 290, "усе разом — одне число:", size=12.5, bold=True))
    p.append(text(cx, 318, "0001 0011 0001 0010", size=18, bold=True))
    p.append(text(cx, 344, "= 0x1312", size=18, color=GREEN, bold=True))

    p.append(rect(50, 366, 660, 44, fill="#f4f7f4", stroke=GREEN, sw=1.6, rx=10))
    p.append(text(cx, 388, "Саме це число лежить у пам'яті як команда. Декодер ріже його на поля й розуміє наказ:",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 404, "біти не мають сенсу самі по собі — ISA робить із числа 0x1312 саме «ДОДАЙ R3,R1,R2».",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "encoding.svg"), W, H, *p)


# ── asm: те саме трьома мовами ────────────────────────────────────────────────
# Ідея: одна команда у трьох виглядах — асемблер, двійковий, hex; машина бачить
# число, асемблер — його читабельний правопис, один-в-один.

def fig_asm():
    W, H = 760, 360
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Те саме трьома мовами: асемблер, двійковий, шістнадцятковий", size=15.5, bold=True))
    p.append(text(cx, 52, "машина бачить ЧИСЛО; асемблер — лише читабельний для людини «правопис» того самого числа (один-в-один)",
                  size=10.5, color=MUTED, italic=True))

    rows = [
        (96, "асемблер (для людини)", "ADD R3, R1, R2", "мнемоніка — слово замість коду", GOLD),
        (166, "машинний код (двійковий)", "0001 0011 0001 0010", "те, що НАСПРАВДІ лежить у пам'яті", BLUE),
        (236, "шістнадцятковий запис", "0x1312", "той самий машинний код, стисло", GREEN),
    ]
    bx, bw = 120, 300
    for ry, lab, val, note, col in rows:
        p.append(rect(bx, ry, bw, 54, fill="#fafafa", stroke=col, sw=1.8, rx=10))
        p.append(text(bx + bw / 2, ry + 22, lab, size=11.5, color=col, bold=True))
        p.append(text(bx + bw / 2, ry + 43, val, size=15, color=INK, bold=True))
        p.append(text(bx + bw + 14, ry + 32, note, size=11, color=MUTED, anchor="start"))

    p.append(arrow(bx + bw / 2, 150, bx + bw / 2, 166, color=INK, sw=2))
    p.append(arrow(bx + bw / 2, 220, bx + bw / 2, 236, color=INK, sw=2))
    p.append(text(bx + bw / 2 + 14, 160, "асемблер ↔ дизасемблер", size=10, color=MUTED, italic=True, anchor="start"))

    p.append(text(cx, 326, "Асемблер один-в-один відповідає машинному коду. Як із вищих мов (C) народжується цей код — окрема велика тема.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "asm.svg"), W, H, *p)


# ── families: словник процесора — родини команд ───────────────────────────────
# Ідея: майже всі команди будь-якого процесора падають у чотири родини;
# словник крихітний, попри безмежжя програм.

def fig_families():
    W, H = 780, 420
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Словник процесора: кілька родин примітивних команд", size=16, bold=True))
    p.append(text(cx, 52, "попри тисячі програм, набір команд невеликий — кілька десятків, що групуються у чотири родини",
                  size=11, color=MUTED, italic=True))

    fams = [
        (90, "Пересилання даних", "возити числа: пам'ять ↔ регістри, регістр → регістр",
         "LD · ST · MOV", BLUE),
        (170, "Арифметика й логіка", "рахувати в АЛП; виставляють прапорці",
         "ADD · SUB · AND · OR · XOR · SHIFT", GREEN),
        (250, "Керування плином", "стрибки й розгалуження: міняють лічильник команд PC",
         "JMP · BEQ · BNE · CALL · RET", RED),
        (330, "Порівняння / тест", "порівняти числа й виставити прапорці Z/N/C/V",
         "CMP · TST", GOLD),
    ]
    for fy, title, sub, mnem, col in fams:
        p.append(rect(50, fy, 680, 66, fill="#fafafa", stroke=col, sw=1.8, rx=10))
        p.append(text(74, fy + 27, title, size=14, color=col, bold=True, anchor="start"))
        p.append(text(74, fy + 50, sub, size=11, color=MUTED, anchor="start"))
        p.append(rect(440, fy + 16, 270, 34, fill=BG, stroke=col, sw=1.4, rx=6))
        p.append(text(575, fy + 38, mnem, size=12, color=INK, bold=True))

    p.append(text(cx, 408, "Усі великі дії — це довгі ланцюги цих дрібних команд. Опанувавши чотири родини, ви читатимете будь-який асемблер.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "families.svg"), W, H, *p)


# ── different: різні процесори — різні мови ───────────────────────────────────
# Ідея: та сама дія «додати» виглядає по-різному на ARM / x86 / RISC-V / AVR;
# машинний код одного для іншого — нісенітниця, тож програму компілюють під ціль.

def fig_different():
    W, H = 780, 420
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Різні процесори — різні мови: «додати» виглядає по-різному", size=15.5, bold=True))
    p.append(text(cx, 52, "кожне сімейство має ВЛАСНИЙ набір інструкцій; машинний код одного для іншого — повна нісенітниця",
                  size=10.5, color=MUTED, italic=True))

    cards = [
        (50, 92, "ARM", "телефони, багато МК", "ADD R3, R1, R2", BLUE),
        (400, 92, "x86 / x86-64", "ПК, ноутбуки (Intel/AMD)", "add eax, ebx", RED),
        (50, 218, "RISC-V", "відкрита ISA; нові ESP32-C", "add x3, x1, x2", GREEN),
        (400, 218, "AVR", "8-біт Arduino Uno", "add r1, r2", GOLD),
    ]
    cw, ch = 330, 104
    for kx, ky, name, who, code, col in cards:
        p.append(rect(kx, ky, cw, ch, fill="#fafafa", stroke=col, sw=1.8, rx=12))
        p.append(text(kx + 20, ky + 30, name, size=14.5, color=col, bold=True, anchor="start"))
        p.append(text(kx + cw - 16, ky + 30, who, size=10, color=MUTED, italic=True, anchor="end"))
        p.append(rect(kx + 20, ky + 44, cw - 40, 36, fill=BG, stroke=col, sw=1.4, rx=6))
        p.append(text(kx + cw / 2, ky + 67, code, size=14, color=INK, bold=True))
        p.append(text(kx + 20, ky + 96, "те саме «додай R1,R2» — інша мнемоніка й ЦІЛКОМ інше число",
                      size=9.5, color=MUTED, anchor="start"))

    p.append(rect(50, 340, 680, 48, fill=F_GLD, stroke=GOLD, sw=1.6, rx=10))
    p.append(text(cx, 362, "Тому програму КОМПІЛЮЮТЬ під конкретний процесор: код для ARM не побіжить на x86. ESP32 — Xtensa (нові — RISC-V).",
                  size=10.5, color=INK, bold=True))
    p.append(text(cx, 380, "ISA — лінія розмежування світів софту: за нею починається «чужа мова», якої ваш процесор не розуміє.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "different.svg"), W, H, *p)


# ── stable: сила ISA — у сталості ─────────────────────────────────────────────
# Ідея: ISA посередині — стабільний інтерфейс; згори програми різних років,
# знизу чипи різних поколінь; поки чипи виконують ту саму ISA, старий софт живе.

def fig_stable():
    W, H = 780, 420
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Сила ISA — у сталості: один контракт, багато поколінь заліза", size=15.5, bold=True))
    p.append(text(cx, 52, "поки нові чипи чесно виконують ту саму ISA, старі програми працюють на них без змін — десятиліттями",
                  size=10.5, color=MUTED, italic=True))

    cols = [(120, "програма 1995", "чип 1995"),
            (320, "програма 2010", "чип 2010"),
            (520, "ваш код сьогодні", "чип 2025")]
    bw = 160
    # програми згори
    for bxx, prog, _ in cols:
        p.append(rect(bxx, 80, bw, 42, fill=F_BLUE, stroke=BLUE, sw=1.6, rx=8))
        p.append(text(bxx + bw / 2, 106, prog, size=11.5, color=BLUE, bold=True))
        p.append(arrow(bxx + bw / 2, 122, bxx + bw / 2, 156, color=INK, sw=1.8))

    # ISA посередині
    p.append(rect(110, 160, 580, 58, fill=F_GRN, stroke=GREEN, sw=2.4, rx=12))
    p.append(text(cx, 186, "ISA (напр. x86 або ARM) — стабільний інтерфейс", size=14, color=GREEN, bold=True))
    p.append(text(cx, 206, "та сама мова команд рік у рік", size=10.5, color=MUTED, italic=True))

    # чипи знизу
    for bxx, _, chip in cols:
        p.append(arrow(bxx + bw / 2, 218, bxx + bw / 2, 252, color=INK, sw=1.8))
        p.append(rect(bxx, 256, bw, 46, fill=F_RED, stroke=RED, sw=1.6, rx=8))
        p.append(text(bxx + bw / 2, 278, chip, size=11.5, color=RED, bold=True))
        p.append(text(bxx + bw / 2, 295, "інше залізо всередині", size=9, color=MUTED, italic=True))

    p.append(rect(50, 322, 680, 76, fill="#f4f7f4", stroke=GREEN, sw=1.6, rx=10))
    p.append(text(cx, 345, "Залізо під ISA вільно переробляють (швидше, економніше) — а софт цього навіть не помічає, бо мова та сама.",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 366, "Саме тому процесори Intel 2025-го досі виконують команди, написані для 1980-х, а ARM-код — на тисячах чипів.",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 387, "ISA — одна з найдовговічніших абстракцій в усій техніці: межа, що дала софту й залізу рости окремо.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "stable.svg"), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури історичної вставки hist-riscv.md (RISC-V: відкрита ISA з Берклі)
# ════════════════════════════════════════════════════════════════════════════

# ── timeline: п'ять поколінь RISC у Берклі — і вихід ISA у відкритий світ ──────
# Ідея: RISC-V — не випадковий стрибок, а п'яте покоління дослідницьких RISC-машин
# Берклі; вертикальна шкала подій від 1981 до сьогодні, червоний вузол — старт 2010.

def fig_timeline():
    W, H = 900, 690
    cx = W / 2
    axx = 250                # вертикальна вісь часу
    p = []
    p.append(text(cx, 36, "П'ять поколінь RISC у Берклі — і вихід ISA у відкритий світ", size=21, bold=True))
    p.append(text(cx, 58, "«V» — це і римська П'ЯТІРКА (п'яте покоління), і Vector, і Variations (варіанти-розширення)",
                  size=12.5, color=MUTED, italic=True))
    p.append(line(axx, 96, axx, 666, color=MUTED, sw=3))

    events = [
        (122, "1981", "RISC-I, RISC-II",
         "Паттерсон зі студентами: прості команди — простий і швидкий кремній. Народження ідеї RISC", False),
        (208.3, "1984", "SOAR (≈ «RISC-III»)",
         "Наступний дослідницький чип лабораторії — лінія Берклі триває", False),
        (294.7, "1988", "SPUR (≈ «RISC-IV»)",
         "Четверте покоління; усе це — навчально-дослідні ISA, не для продажу", False),
        (381.0, "2010", "RISC-V — старт у Par Lab",
         "Асанович, Вотерман, Лі (дир. Паттерсон): чиста ISA з нуля, щоб НЕ платити за чужу мову", True),
        (467.3, "2011", "перший том специфікації",
         "Опубліковано опис базового набору — RISC-V виходить за межі однієї лабораторії", False),
        (553.7, "2015", "RISC-V Foundation + SiFive",
         "Стандарт віддали незалежній спільноті; трійця засновує першу RISC-V-компанію", False),
        (640.0, "донині", "у мільярдах чипів",
         "Від крихітних МК (ESP32-C) до серверів — і все на ОДНІЙ відкритій, безплатній ISA", False),
    ]
    for cy, year, head, sub, hot in events:
        col = RED if hot else INK
        if hot:
            p.append(circle(axx, cy, 10.0, fill=BG, stroke=RED, sw=3.2))
            p.append(circle(axx, cy, 4.5, fill=RED, stroke=RED, sw=1))
        else:
            p.append(circle(axx, cy, 7.0, fill=BG, stroke=INK, sw=2.6))
        p.append(text(axx - 22, cy + 5, year, size=14, color=col, anchor="end", bold=True))
        p.append(text(axx + 24, cy - 4, head, size=15.5, color=col, anchor="start", bold=True))
        p.append(text(axx + 24, cy + 16, sub, size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p)


# ── open-vs-closed: дві моделі однієї й тієї самої речі — мови процесора ───────
# Ідея: ліворуч закрита (пропрієтарна) ISA з платою й дозволом; праворуч відкрита
# RISC-V — спільне надбання без роялті. Та сама річ, дві моделі володіння.

def fig_open_vs_closed():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 34, "Дві моделі однієї й тієї самої речі — мови процесора (ISA)", size=20, bold=True))

    # ── ліва картка: ЗАКРИТА ───────────────────────────────────────────────
    p.append(rect(40, 70, 380, 360, fill=F_RED, stroke=RED, sw=2.4, rx=10))
    p.append(text(230, 100, "ЗАКРИТА (пропрієтарна) ISA", size=16, color=RED, bold=True))
    p.append(text(230, 120, "власник тримає мову й бере плату", size=12, color=MUTED, italic=True))
    left_lines = [
        "• належить одній фірмі (напр. ARM, x86)",
        "• щоб робити чипи — купуєш ліцензію",
        "• роялті: невеликий платіж із кожного",
        "   проданого чипа",
        "• не можна вільно додати свою команду",
        "• порядок узгоджуєш із власником мови",
    ]
    ly = 158
    for ln in left_lines:
        p.append(text(64, ly, ln, size=13, color=INK, anchor="start"))
        ly += 26
    # замок — зачинений (дужка вниз)
    p.append(rect(204, 322, 52, 44, fill=BG, stroke=RED, sw=2.6, rx=6))
    p.append('<path d="M214,322 v-14 a16,16 0 0 1 32,0 v14" fill="none" stroke="%s" stroke-width="2.6"/>' % RED)
    p.append(circle(230, 344, 6.0, fill=RED, stroke=RED, sw=1))
    p.append(text(230, 396, "вхід — за гроші й дозволом", size=12.5, color=RED, bold=True))

    # ── права картка: ВІДКРИТА ──────────────────────────────────────────────
    p.append(rect(480, 70, 380, 360, fill=F_GRN, stroke=GREEN, sw=2.4, rx=10))
    p.append(text(670, 100, "ВІДКРИТА ISA (RISC-V)", size=16, color=GREEN, bold=True))
    p.append(text(670, 120, "мова — спільне надбання, без роялті", size=12, color=MUTED, italic=True))
    right_lines = [
        "• специфікація вільна (ліцензія BSD-типу)",
        "• робити чипи може будь-хто — без плати",
        "• базовий набір «заморожено» — стабільний",
        "• решта — модульні розширення (M, A, C, F…)",
        "• стандарт веде незалежна спільнота",
        "• можна додати власні команди під задачу",
    ]
    ry = 158
    for ln in right_lines:
        p.append(text(504, ry, ln, size=13, color=INK, anchor="start"))
        ry += 26
    # замок — відчинений (дужка піднята збоку)
    p.append(rect(644, 322, 52, 44, fill=BG, stroke=GREEN, sw=2.6, rx=6))
    p.append('<path d="M654,322 v-14 a16,16 0 0 1 32,0" fill="none" stroke="%s" stroke-width="2.6"/>' % GREEN)
    p.append(circle(670, 344, 6.0, fill=GREEN, stroke=GREEN, sw=1))
    p.append(text(670, 396, "вхід вільний для всіх", size=12.5, color=GREEN, bold=True))

    render(os.path.join(OUT, "open-vs-closed.svg"), W, H, *p)


# ── modular: ядро + розширення — з однієї ISA і крихітний МК, і сервер ─────────
# Ідея: у центрі обов'язкове цілочислове ядро RV32I (заморожене), навколо —
# стандартні розширення M/A/C/F/D/V плюс свої команди; чип бере лише потрібне.

def fig_modular():
    W, H = 900, 430
    cx, cy = 450, 250
    p = []
    p.append(text(cx, 34, "Чому з однієї ISA виходять і крихітний МК, і сервер: ядро + розширення", size=19, bold=True))
    p.append(text(cx, 56, "обов'язкове — лише мала цілочислова основа; усе інше домовляєшся ДОДАВАТИ за потребою",
                  size=12.5, color=MUTED, italic=True))

    # розширення-кубики: (x, y, лінія від, лінія до, мітка, опис, колір рамки)
    exts = [
        (236, 108, (399, 209.2), (324, 149.2), "M",   "множення / ділення",     GREEN),
        (536, 108, (501, 209.2), (576, 149.2), "A",   "атомарні (багатоядерні)", GREEN),
        (176, 238, (378.6, 253.4), (273.6, 258.4), "C",   "стислі 16-біт команди", GREEN),
        (596, 238, (521.4, 253.4), (626.4, 258.4), "F / D", "числа з комою",       GREEN),
        (236, 358, (399, 294.2), (324, 359.2), "V",   "вектори (масиви даних)", GREEN),
        (536, 358, (501, 294.2), (576, 359.2), "своє", "власні команди під задачу", GOLD),
    ]
    # лінії-зв'язки (під рамками)
    for bx, by, (x1, y1), (x2, y2), lab, desc, col in exts:
        p.append(line(x1, y1, x2, y2, color=GREEN, sw=2, dash="4,3"))
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" '
                 'stroke-dasharray="4,3" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, GREEN))

    # центральне ядро
    p.append(circle(cx, cy, 64.0, fill=F_BLUE, stroke=BLUE, sw=3))
    p.append(text(cx, 242, "RV32I", size=22, color=BLUE, bold=True))
    p.append(text(cx, 264, "базове ядро", size=12.5, color=INK))
    p.append(text(cx, 281, "(заморожене)", size=11.5, color=MUTED, italic=True))
    p.append(text(cx, 340, "≈ 40 цілочислових команд — спільний фундамент УСІХ RISC-V", size=12.5, color=INK))

    # кубики-розширення поверх ліній
    for bx, by, _, _, lab, desc, col in exts:
        p.append(rect(bx, by, 128, 44, fill=BG, stroke=col, sw=2.4, rx=8))
        p.append(text(bx + 64, by + 20, lab, size=15, color=col, bold=True))
        p.append(text(bx + 64, by + 38, desc, size=11, color=INK))

    p.append(text(cx, 414, "Бере чип лише те, що йому треба: ESP32-C тягне RV32I + M + C; великий процесор — ще A, F, D, V",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "modular.svg"), W, H, *p)


# ── market: чому відкрита ISA зрушила саме ринок мікроконтролерів ──────────────
# Ідея: чотири наслідки відкритості, кожен особливо вагомий для дешевих чипів —
# нуль роялті, своє ядро без дозволу, спільні інструменти, свобода від геополітики.

def fig_market():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 34, "Чому відкрита ISA зрушила саме ринок мікроконтролерів", size=20, bold=True))

    cards = [
        (28, 70, "Нуль роялті", BLUE, [
            "За саму мову не платять. У копійчаному МК, де кожен",
            "цент рахують, зекономлений роялті — це вже перевага",
            "в ціні.",
        ]),
        (462, 70, "Своє ядро без дозволу", GREEN, [
            "Виробник робить власний RISC-V-процесор сам, не",
            "питаючи власника ISA й не чекаючи його умов.",
        ]),
        (28, 226, "Спільні інструменти", GOLD, [
            "Один компілятор, один асемблер, одна документація —",
            "для чипів різних фірм. Не треба городити власну мову",
            "з нуля.",
        ]),
        (462, 226, "Свобода від геополітики", RED, [
            "Відкритий стандарт важче перекрити санкціями — тому",
            "2020-го його стандарт-орган переїхав у нейтральну",
            "Швейцарію.",
        ]),
    ]
    for bx, by, title, col, lines in cards:
        p.append(rect(bx, by, 410, 132, fill=BG, stroke=col, sw=2.4, rx=10))
        p.append(rect(bx, by, 8, 132, fill=col, stroke=col, sw=0, rx=0))
        p.append(text(bx + 26, by + 32, title, size=16, color=col, anchor="start", bold=True))
        ty = by + 58
        for ln in lines:
            p.append(text(bx + 26, ty, ln, size=12.5, color=INK, anchor="start"))
            ty += 19

    render(os.path.join(OUT, "market.svg"), W, H, *p)


# ── credit: RISC-V — праця багатьох рук, а не одне ім'я ────────────────────────
# Ідея: чотири картки-ролі від ідеї RISC (Паттерсон) через керівника проєкту
# (Асанович) і авторів специфікації (Вотерман, Лі) до спільноти й SiFive.

def fig_credit():
    W, H = 900, 400
    p = []
    p.append(text(W / 2, 34, "RISC-V — праця багатьох рук, а не одне ім'я", size=20, bold=True))
    p.append(text(W / 2, 56, "точна атрибуція: хто заклав ідею RISC, хто зробив саму ISA, хто доніс її до залізного світу",
                  size=12.5, color=MUTED, italic=True))

    cards = [
        (30.0, "Девід Паттерсон", BLUE,
         ["ідея RISC (1980-ті) +", "директор Par Lab"],
         ["заклав напрям; «дідусь»", "лінії RISC у Берклі"]),
        (243.3, "Крсте Асанович", GREEN,
         ["очолив проєкт RISC-V", "(2010)"],
         ["повів розробку нової", "відкритої ISA"]),
        (456.7, "Е. Вотерман, Ю. Лі", GREEN,
         ["автори перших специфікацій"],
         ["написали й виточили сам", "набір команд"]),
        (670.0, "Спільнота й SiFive", GOLD,
         ["Foundation (2015) → Int'l", "(2020)"],
         ["перетворили ISA на", "світовий стандарт"]),
    ]
    cw = 200
    for i, (bx, name, col, sub, body) in enumerate(cards):
        ccx = bx + cw / 2
        p.append(rect(bx, 96, cw, 250, fill=BG, stroke=col, sw=2.4, rx=10))
        # піктограма-«людина»: голова + плечі
        p.append(circle(ccx, 148, 16.0, fill=BG, stroke=col, sw=2.6))
        p.append('<path d="M%.1f,192 Q%.1f,162 %.1f,192" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (ccx - 26, ccx, ccx + 26, col))
        p.append(text(ccx, 228, name, size=14, color=INK, bold=True))
        sy = 252
        for ln in sub:
            p.append(text(ccx, sy, ln, size=11.5, color=MUTED, italic=True))
            sy += 18
        # тіло-опис починаємо нижче, з невеликим відступом якщо sub коротке
        byy = 292 if len(sub) > 1 else 274
        for ln in body:
            p.append(text(ccx, byy, ln, size=11.5, color=col))
            byy += 18
        if i < len(cards) - 1:
            ax = bx + cw - 5.3
            p.append('<line x1="%.1f" y1="221.0" x2="%.1f" y2="221.0" stroke="%s" stroke-width="2" '
                     'marker-end="url(#arrow)"/>' % (ax, ax + 24, INK))

    p.append(text(W / 2, 386, "Велике в техніці майже завжди колективне — пам'ять лише зручно чіпляється за одне ім'я",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "credit.svg"), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки comp-isa-in-boards.md (які ISA живуть у хобі-платах)
#  та proj-reading-disassembly.md (читаємо дизасемблер)
# ════════════════════════════════════════════════════════════════════════════

# Додаткові локальні відтінки під уже усталений вигляд цих фігур.
VIOLET = "#6b4fa0"   # Xtensa-гілка (фірмова ISA)
PURPLE = "#7a3fb0"   # керування плином / байти команди в дизасемблері
ORANGE = "#e08030"   # RISC-V-блок у порівнянні асемблерів
MONO   = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    """Моноширинний рядок коду — той самий <text>, лише з м(mono)-сімейством."""
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── isa-map: яка хобі-плата якою ISA «говорить» ───────────────────────────────
# Ідея: ISA — мова ЯДРА, а не плати; згори три родини ISA, знизу плати, стрілка
# веде плату до її мови. Читати згори вниз: плата → ядро → ISA.

def fig_isa_map():
    W, H = 820, 470
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Яку ISA «говорить» популярна хобі-плата", size=20, bold=True))
    p.append(text(cx, 51, "ISA — це мова ядра, а не сама плата: одна мова накриває багато різних чипів",
                  size=13, color=MUTED, italic=True))

    # три ISA згори
    p.append(rect(60, 78, 300, 50, fill="#dfe6f6", stroke=BLUE, sw=2.4, rx=8))
    p.append(text(210, 100, "ARM Cortex-M", size=16, color=BLUE, bold=True))
    p.append(text(210, 118, "(ARMv6-M … ARMv8-M)", size=11, color=BLUE, italic=True))
    p.append(rect(330, 78, 250, 50, fill=F_GRN, stroke=GREEN, sw=2.4, rx=8))
    p.append(text(455, 100, "RISC-V", size=16, color=GREEN, bold=True))
    p.append(text(455, 118, "(RV32, відкрита)", size=11, color=GREEN, italic=True))
    p.append(rect(600, 78, 160, 50, fill="#e9e1f3", stroke=VIOLET, sw=2.4, rx=8))
    p.append(text(680, 100, "Xtensa", size=16, color=VIOLET, bold=True))
    p.append(text(680, 118, "(Tensilica, фірмова)", size=11, color=VIOLET, italic=True))

    # плати знизу
    boards = [
        (40, 168, "Raspberry Pi Pico", "RP2040 · 2×Cortex-M0+"),
        (222, 150, "STM32-плати", "Cortex-M0…M7/M33"),
        (386, 176, "Raspberry Pi Pico 2", "RP2350 · M33 АБО RV"),
        (576, 110, "ESP32-C3 / C6", "RISC-V RV32"),
        (700, 96, "ESP32 / -S2 / -S3", "Xtensa LX6 / LX7"),
    ]
    for bx, bw, name, sub in boards:
        p.append(rect(bx, 250, bw, 64, fill=BG, stroke=INK, sw=1.8, rx=7))
        p.append(text(bx + bw / 2, 275, name, size=13.5, color=INK, bold=True))
        p.append(text(bx + bw / 2, 294, sub, size=11, color=MUTED))

    aB = 'marker-end="url(#arrow)"'
    def conn(x1, y1, x2, y2, col, dash=False):
        d = ' stroke-dasharray="5,4"' if dash else ''
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="2"%s %s/>' % (x1, y1, x2, y2, col, d, aB))
    # Pico → ARM; STM32 → ARM; Pico 2 → ARM (пунктир) і → RISC-V (пунктир);
    # ESP32-C3/C6 → RISC-V; ESP32 → Xtensa
    p.append(conn(124, 248, 210, 130, BLUE))
    p.append(conn(297, 248, 210, 130, BLUE))
    p.append(conn(452, 248, 210, 130, BLUE, dash=True))
    p.append(conn(496, 248, 455, 130, GREEN, dash=True))
    p.append(conn(631, 248, 455, 130, GREEN))
    p.append(conn(748, 248, 680, 130, VIOLET))
    p.append(text(474, 332, "↑ перемикане ядро: M33 або RISC-V", size=10.5, color=GOLD, bold=True))

    # підвал
    p.append(rect(40, 392, 360, 58, fill=F_GLD, stroke=GOLD, sw=1.8, rx=7))
    p.append(text(54, 414, "Для контрасту: Arduino Uno → AVR (8-біт)", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(54, 433, "ще одна, окрема мова — у цю карту 32-бітних ISA не лягає.", size=11.5, color=INK, anchor="start"))
    p.append(rect(420, 392, 360, 58, fill=F_GRN, stroke=GREEN, sw=1.8, rx=7))
    p.append(text(600, 414, "Читати згори вниз, не навпаки:", size=12.5, color=GREEN, bold=True))
    p.append(text(600, 433, "плата → ядро → ISA. Цільову ISA й обираєш у IDE.", size=11.5, color=INK))
    render(os.path.join(OUT, "isa-map.svg"), W, H, *p)


# ── esp32-split: одна родина ESP32 — дві різні ISA ────────────────────────────
# Ідея: під одним брендом ESP — дві несумісні гілки: Xtensa (фірмова) і RISC-V
# (відкрита); машинний код між гілками не переносний.

def fig_esp32_split():
    W, H = 820, 440
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Одна родина ESP32 — дві різні ISA", size=20, bold=True))
    p.append(text(cx, 51, "однаковий бренд і середовище, та машинний код несумісний між гілками",
                  size=13, color=MUTED, italic=True))

    # корінь
    p.append(rect(320, 70, 180, 44, fill="#e4e4e4", stroke=INK, sw=2, rx=8))
    p.append(text(cx, 90, "Espressif ESP", size=15, color=INK, bold=True))
    p.append(text(cx, 107, "сімейство Wi-Fi МК", size=11, color=MUTED))

    aB = 'marker-end="url(#arrow)"'
    p.append('<line x1="380" y1="114" x2="200" y2="158" stroke="%s" stroke-width="2.2" %s/>' % (VIOLET, aB))
    p.append('<line x1="440" y1="114" x2="620" y2="158" stroke="%s" stroke-width="2.2" %s/>' % (GREEN, aB))

    # гілка Xtensa (ліворуч)
    p.append(rect(65, 168, 260, 44, fill="#e9e1f3", stroke=VIOLET, sw=2.2, rx=8))
    p.append(text(195, 188, "Гілка Xtensa (фірмова Tensilica)", size=13.5, color=VIOLET, bold=True))
    p.append(text(195, 205, "класичні й «великі» моделі", size=11, color=VIOLET))
    xt = [
        (236, "ESP8266", "Xtensa L106 · 80 МГц · 1 ядро"),
        (282, "ESP32", "Xtensa LX6 · 240 МГц · 2 ядра"),
        (328, "ESP32-S2", "Xtensa LX7 · 1 ядро"),
        (374, "ESP32-S3", "Xtensa LX7 · 2 ядра"),
    ]
    for ry, name, sub in xt:
        p.append(rect(45, ry, 300, 38, fill=BG, stroke=VIOLET, sw=1.5, rx=6))
        p.append(text(57, ry + 16, name, size=12.5, color=INK, bold=True, anchor="start"))
        p.append(text(57, ry + 32, sub, size=10.8, color=MUTED, anchor="start"))

    # гілка RISC-V (праворуч)
    p.append(rect(495, 168, 260, 44, fill=F_GRN, stroke=GREEN, sw=2.2, rx=8))
    p.append(text(625, 188, "Гілка RISC-V (відкрита ISA)", size=13.5, color=GREEN, bold=True))
    p.append(text(625, 205, "новіші моделі серії «C»", size=11, color=GREEN))
    rv = [
        (236, "ESP32-C3", "RISC-V RV32IMC · 1 ядро"),
        (282, "ESP32-C6", "RISC-V · + Wi-Fi 6"),
        (328, "ESP32-H2", "RISC-V · Thread/Zigbee"),
    ]
    for ry, name, sub in rv:
        p.append(rect(475, ry, 300, 38, fill=BG, stroke=GREEN, sw=1.5, rx=6))
        p.append(text(487, ry + 16, name, size=12.5, color=INK, bold=True, anchor="start"))
        p.append(text(487, ry + 32, sub, size=10.8, color=MUTED, anchor="start"))

    # центральна засторога
    p.append(line(cx, 150, cx, 410, color=GOLD, sw=1.6, dash="2,6"))
    p.append(rect(318, 250, 184, 60, fill=F_GLD, stroke=GOLD, sw=1.8, rx=8))
    p.append(text(cx, 272, "Код НЕ переносний", size=12.5, color=GOLD, bold=True))
    p.append(text(cx, 290, "між гілками:", size=11, color=INK))
    p.append(text(cx, 305, "перекомпілюй під ціль", size=10.5, color=INK))
    render(os.path.join(OUT, "esp32-split.svg"), W, H, *p)


# ── block-firstword: блок-схема плати МК зсередини + драбина «першого байта» ───
# Ідея: каркас плати однаковий для всіх ISA — мова замкнена в ядрі; праворуч —
# чотири кроки, як заговорити з платою через правильну ISA-ціль.

def fig_block_firstword():
    W, H = 820, 470
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Хобі-плата МК зсередини й «перший байт»", size=20, bold=True))
    p.append(text(cx, 51, "однаковий каркас плати; ISA живе всередині ядра — і її ж обираєш як ціль",
                  size=13, color=MUTED, italic=True))

    # ── ліва половина: плата зсередини ──
    p.append(rect(36, 74, 470, 356, fill="#fafafa", stroke=INK, sw=2.2, rx=10))
    p.append(text(50, 96, "плата (модуль розробника)", size=12.5, color=MUTED, bold=True, anchor="start"))
    aI = 'marker-end="url(#arrow)"'

    # USB-роз'єм
    p.append(rect(22, 224, 22, 44, fill="#e4e4e4", stroke=INK, sw=1.8, rx=3))
    p.append(text(33, 218, "USB", size=11, color=INK, bold=True))
    # USB↔UART
    p.append(rect(76, 224, 96, 46, fill="#dfe6f6", stroke=BLUE, sw=1.8, rx=6))
    p.append(text(124, 244, "USB↔UART", size=11.5, color=BLUE, bold=True))
    p.append(text(124, 261, "(або вбуд.)", size=10, color=MUTED))
    p.append('<line x1="44" y1="246" x2="74" y2="247" stroke="%s" stroke-width="1.8" %s/>' % (INK, aI))
    # стабілізатор
    p.append(rect(76, 110, 120, 42, fill="#f6dcd9", stroke=RED, sw=1.8, rx=6))
    p.append(text(136, 128, "Стабілізатор", size=11.5, color=RED, bold=True))
    p.append(text(136, 144, "5 В → 3.3 В", size=11, color=INK))
    # чип МК
    p.append(rect(232, 184, 230, 150, fill=BG, stroke=INK, sw=2.4, rx=10))
    p.append(text(347, 208, "Чип МК (SoC)", size=14, color=INK, bold=True))
    p.append(rect(258, 224, 178, 60, fill=F_GRN, stroke=GREEN, sw=2, rx=8))
    p.append(text(347, 247, "ЯДРО + ISA", size=13.5, color=GREEN, bold=True))
    p.append(text(347, 266, "Cortex-M / RISC-V / Xtensa", size=11, color=INK))
    p.append(text(347, 320, "+ Flash, RAM, периферія на кристалі", size=10.5, color=MUTED))
    p.append('<line x1="136" y1="152" x2="347" y2="182" stroke="%s" stroke-width="1.8" %s/>' % (RED, aI))
    p.append(text(353, 176, "3.3 В", size=10.5, color=RED, bold=True, anchor="start"))
    p.append('<line x1="172" y1="247" x2="230" y2="254" stroke="%s" stroke-width="1.8" %s/>' % (BLUE, aI))
    p.append(text(202, 248, "прошивка/лог", size=10, color=BLUE))
    # GPIO-піни
    for py in (208, 234, 260, 286, 312):
        p.append(line(462, py, 496, py, color=INK, sw=1.6))
        p.append(circle(500, py, 3.0, fill=BG, stroke=INK, sw=1.4))
    p.append(text(498, 350, "GPIO-піни", size=10.5, color=MUTED, bold=True, anchor="end"))
    p.append(text(50, 416, "рівні логіки 3.3 В — не 5 В на входи!", size=10.5, color=GOLD, bold=True, anchor="start"))

    # ── права половина: «перший байт» ──
    p.append(rect(528, 74, 256, 356, fill=BG, stroke=MUTED, sw=1.8, rx=10))
    p.append(text(656, 100, "«Перший байт»:", size=15, color=INK, bold=True))
    p.append(text(656, 119, "як заговорити з платою", size=12, color=MUTED, italic=True))
    steps = [
        (138, "#dfe6f6", BLUE, "1. Дізнайся ядро плати",
         ["RP2040 → ARM; ESP32-C3 → RISC-V;", "ESP32 → Xtensa."]),
        (208, F_GRN, GREEN, "2. Обери ту саму ISA-ціль",
         ["у IDE: «board / target» = саме", "цей чип, не «якийсь ESP»."]),
        (278, "#dfe6f6", BLUE, "3. Постав потрібний toolchain",
         ["компілятор кодує під ISA;", "чужий дасть несумісний код."]),
        (348, F_GRN, GREEN, "4. Залий і поглянь у лог",
         ["перший рядок по UART (115200)", "= плата ожила й говорить."]),
    ]
    for sy, fill, col, head, lines in steps:
        p.append(rect(540, sy, 232, 60, fill=fill, stroke=col, sw=1.5, rx=6))
        p.append(text(550, sy + 19, head, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(550, sy + 36, lines[0], size=10.5, color=INK, anchor="start"))
        p.append(text(550, sy + 51, lines[1], size=10.5, color=INK, anchor="start"))
    render(os.path.join(OUT, "block-firstword.svg"), W, H, *p)


# ── loop-to-asm: один цикл на C — і що з нього зробив компілятор двома ISA ──────
# Ідея: та сама сума масиву; кожен рядок C розгортається в кілька машинних команд,
# і вони РІЗНІ для Xtensa та RISC-V — але ідеї (load/add/крок/лічильник/стрибок) спільні.

def fig_loop_to_asm():
    W, H = 960, 540
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Один цикл на C — і що з нього зробив компілятор двома мовами процесора",
                  size=18.5, bold=True))
    p.append(text(cx, 51, "та сама сума масиву; кожен рядок C розгортається в кілька машинних команд — і вони РІЗНІ для різних ISA",
                  size=11, color=MUTED, italic=True))

    # вихідний C
    p.append(rect(24, 78, 250, 200, fill="#fbfbff", stroke=BLUE, sw=1.8, rx=12))
    p.append(text(149, 100, "вихідний код (C)", size=12.5, color=BLUE, bold=True))
    p.append(mono(40, 130, "int sum = 0;", size=13.5))
    p.append(mono(40, 156, "for (int i = 0; i < n; i++)", size=13.5))
    p.append(mono(40, 182, "    sum += a[i];", size=13.5))
    p.append(mono(40, 208, "return sum;", size=13.5))
    p.append(rect(38, 142, 222, 20, fill="none", stroke=GREEN, sw=1.3, rx=5))
    p.append(rect(38, 168, 222, 20, fill="none", stroke=RED, sw=1.3, rx=5))
    p.append(text(149, 262, "4 короткі рядки людською мовою", size=10, color=MUTED, italic=True))

    aI = 'marker-end="url(#arrow)"'
    p.append('<line x1="280" y1="150" x2="314" y2="150" stroke="%s" stroke-width="2.4" %s/>' % (INK, aI))
    p.append(mono(297, 142, "gcc", size=10, color=INK, anchor="middle", bold=True))
    p.append('<line x1="280" y1="360" x2="314" y2="360" stroke="%s" stroke-width="2.4" %s/>' % (INK, aI))
    p.append(mono(297, 352, "gcc", size=10, color=INK, anchor="middle", bold=True))

    # Xtensa
    p.append(rect(322, 78, 632, 198, fill="#f6fbf6", stroke=GREEN, sw=1.8, rx=12))
    p.append(text(338, 100, "Xtensa  (ядро ESP32)", size=12.5, color=GREEN, bold=True, anchor="start"))
    p.append(mono(940, 100, "objdump -d", size=11, color=MUTED, anchor="end"))
    xt = [
        (124, "  movi   a8, 0", GREEN, False, "; sum = 0  (поклади 0 у регістр)"),
        (143, "  blti   a3, 1, .Lend", PURPLE, True, "; якщо n<1 — одразу в кінець"),
        (162, ".Lloop:", MUTED, False, "; — початок тіла циклу —"),
        (181, "  l32i   a9, a2, 0", INK, True, "; завантаж a[i] з пам'яті"),
        (200, "  add.n  a8, a8, a9", RED, True, "; sum += a[i]"),
        (219, "  addi   a2, a2, 4", INK, True, "; крок покажчика на наступне слово"),
        (238, "  addi   a3, a3, -1", INK, True, "; лічильник n--"),
        (257, "  bnez   a3, .Lloop", PURPLE, True, "; ще лишилось? — назад у .Lloop"),
    ]
    for ry, code, col, bold, cm in xt:
        p.append(mono(336, ry, code, size=13, color=col, bold=bold))
        p.append(text(612, ry, cm, size=10.5, color=MUTED, anchor="start"))

    # RISC-V
    p.append(rect(322, 288, 632, 198, fill="#fff8f0", stroke=ORANGE, sw=1.8, rx=12))
    p.append(text(338, 310, "RISC-V  (новіші ESP32-C, Pico 2…)", size=12.5, color=ORANGE, bold=True, anchor="start"))
    p.append(mono(940, 310, "objdump -d", size=11, color=MUTED, anchor="end"))
    rv = [
        (334, "  li     a5, 0", GREEN, "; sum = 0"),
        (353, "  blez   a1, .Lend", PURPLE, "; якщо n<=0 — у кінець"),
        (372, ".Lloop:", MUTED, "; — початок тіла циклу —"),
        (391, "  lw     a4, 0(a0)", INK, "; завантаж a[i]"),
        (410, "  add    a5, a5, a4", RED, "; sum += a[i]"),
        (429, "  addi   a0, a0, 4", INK, "; покажчик += 4 байти"),
        (448, "  addi   a1, a1, -1", INK, "; n--"),
        (467, "  bnez   a1, .Lloop", PURPLE, "; ще є — назад"),
    ]
    for ry, code, col, cm in rv:
        p.append(mono(336, ry, code, size=13, color=col))
        p.append(text(612, ry, cm, size=10.5, color=MUTED, anchor="start"))

    # що видно одразу
    p.append(rect(24, 296, 250, 150, fill="#fafafa", stroke=MUTED, sw=1.4, rx=10))
    p.append(text(149, 318, "що видно одразу", size=11.5, color=INK, bold=True))
    notes = [
        "• кожен рядок C → кілька команд",
        "• ідеї ті самі: load, add,",
        "   крок покажчика, лічильник,",
        "   умовний стрибок назад = ЦИКЛ",
        "• мнемоніки й імена регістрів",
        "   різні (a8 проти a5, l32i/lw)",
        "• «sum += a[i]» — це 3 команди,",
        "   а не одна",
    ]
    ny = 338
    for ln in notes:
        p.append(text(36, ny, ln, size=10, color=INK, anchor="start"))
        ny += 14
    render(os.path.join(OUT, "loop-to-asm.svg"), W, H, *p)


# ── anatomy: анатомія одного рядка дизасемблера — чотири колонки ───────────────
# Ідея: objdump показує і число-команду, і її людський «правопис» рядок-у-рядок;
# чотири колонки — адреса, байти команди, мнемоніка, операнди.

def fig_anatomy():
    W, H = 960, 470
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Анатомія одного рядка дизасемблера: чотири колонки", size=18.5, bold=True))
    p.append(text(cx, 51, "objdump показує і число-команду, і її людський «правопис» — рядок у рядок",
                  size=11, color=MUTED, italic=True))

    # сам рядок
    p.append(rect(60, 90, 840, 56, fill="#fbfbff", stroke=INK, sw=1.6, rx=10))
    p.append(mono(92, 120, "400d12a8:", size=17, color=BLUE, bold=True))
    p.append(mono(250, 120, "00b50533", size=17, color=PURPLE, bold=True))
    p.append(mono(430, 120, "add", size=17, color=RED, bold=True))
    p.append(mono(540, 120, "a0, a0, a1", size=17, color=GREEN, bold=True))

    aB = lambda c: 'marker-end="url(#arrow)"'
    cols = [
        (104, 70, 148, "АДРЕСА", BLUE, 73,
         ["де команда лежить", "(сюди вказував PC)"]),
        (264, 240, 318, "БАЙТИ КОМАНДИ", PURPLE, 90,
         ["те саме число, що", "в пам'яті; декодер", "ріже його на поля"]),
        (442, 422, 500, "МНЕМОНІКА", RED, 73,
         ["що робити:", "тут — додати", "(opcode → дія)"]),
        (552, 712, 790, "ОПЕРАНДИ", GREEN, 73,
         ["над чим:", "a0 = a0 + a1", "(куди ← що, що)"]),
    ]
    for lx, bx, bcx, head, col, bh, lines in cols:
        p.append('<line x1="%.1f" y1="136" x2="%.1f" y2="192" stroke="%s" stroke-width="1.6" %s/>'
                 % (lx, bcx, col, aB(col)))
        p.append(rect(bx, 200, 156, bh, fill=BG, stroke=col, sw=1.5, rx=8))
        p.append(text(bcx, 218, head, size=11.5, color=col, bold=True))
        ty = 238
        for ln in lines:
            p.append(text(bx + 10, ty, ln, size=10, color=INK, anchor="start"))
            ty += 16

    # підвал: одна команда — три погляди
    p.append(rect(60, 360, 840, 86, fill="#fafafa", stroke=MUTED, sw=1.4, rx=10))
    p.append(text(cx, 382, "одна команда — три погляди", size=12.5, color=INK, bold=True))
    p.append(mono(120, 412, "0x00b50533", size=14, color=PURPLE, bold=True))
    p.append(text(120, 430, "число в пам'яті", size=10, color=MUTED, anchor="start"))
    p.append(text(330, 412, "→", size=18, color=INK, anchor="start"))
    p.append(mono(380, 412, "add  a0, a0, a1", size=14, color=RED, bold=True))
    p.append(text(380, 430, "асемблер (мнемоніка)", size=10, color=MUTED, anchor="start"))
    p.append(text(640, 412, "→", size=18, color=INK, anchor="start"))
    p.append(mono(690, 412, "a0 = a0 + a1", size=14, color=GREEN, bold=True))
    p.append(text(690, 430, "що це означає", size=10, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "anatomy.svg"), W, H, *p)


# ── optimization: той самий код -O0 проти -O2 ─────────────────────────────────
# Ідея: компілятор перекладає не рядок-у-рядок, а за змістом; -O0 ганяє все через
# стек (≈15 команд у тілі), -O2 тримає все в регістрах (≈4 команди) — той самий зміст.

def fig_optimization():
    W, H = 960, 500
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Сюрприз дизасемблера: компілятор НЕ перекладає рядок-у-рядок", size=18.5, bold=True))
    p.append(text(cx, 51, "той самий цикл суми з -O0 і з -O2 — оптимізатор перебудовує код до невпізнанності",
                  size=11, color=MUTED, italic=True))

    # вихідний C
    p.append(rect(280, 70, 400, 64, fill="#fbfbff", stroke=BLUE, sw=1.6, rx=10))
    p.append(text(cx, 90, "вихідний C (однаковий для обох):", size=11, color=BLUE, bold=True))
    p.append(mono(cx, 116, "for (i=0;i<n;i++) sum += a[i];", size=14, anchor="middle"))

    aI = 'marker-end="url(#arrow)"'
    p.append('<line x1="330" y1="140" x2="260" y2="178" stroke="%s" stroke-width="2.2" %s/>' % (INK, aI))
    p.append(mono(330, 162, "-O0", size=11, color=MUTED, anchor="middle", bold=True))
    p.append('<line x1="630" y1="140" x2="700" y2="178" stroke="%s" stroke-width="2.2" %s/>' % (INK, aI))
    p.append(mono(630, 162, "-O2", size=11, color=MUTED, anchor="middle", bold=True))

    # -O0
    p.append(rect(30, 184, 440, 286, fill="#fff6f6", stroke=RED, sw=1.8, rx=12))
    p.append(text(46, 206, "-O0  (без оптимізації)", size=13, color=RED, bold=True, anchor="start"))
    p.append(text(46, 224, "буквально, через пам'ять — довго, але «як написано»",
                  size=10, color=MUTED, italic=True, anchor="start"))
    o0 = [
        (244, "  sw    zero, sum(sp)      ; sum=0 у стек", INK),
        (258.7, ".L2:", MUTED),
        (273.4, "  lw    t0, i(sp)          ; узяти i зі стека", INK),
        (288.1, "  bge   t0, n, .Lend       ; i<n ?", INK),
        (302.8, "  lw    t0, i(sp)          ; i знову", INK),
        (317.5, "  slli  t1, t0, 2          ; i*4 (зсув)", INK),
        (332.2, "  add   t1, base, t1       ; &a[i]", INK),
        (346.9, "  lw    t1, 0(t1)          ; a[i]", INK),
        (361.6, "  lw    t2, sum(sp)        ; sum зі стека", INK),
        (376.3, "  add   t2, t2, t1         ; sum + a[i]", INK),
        (391.0, "  sw    t2, sum(sp)        ; назад у стек", INK),
        (405.7, "  lw    t0, i(sp)          ; i++ ...", INK),
        (420.4, "  addi  t0, t0, 1", INK),
        (435.1, "  sw    t0, i(sp)", INK),
        (449.8, "  j     .L2                ; знову", INK),
    ]
    for ry, code, col in o0:
        p.append(mono(44, ry, code, size=11, color=col))
    p.append(text(250, 466, "≈ 15 команд у тілі · усе ганяє через стек", size=10, color=RED, bold=True))

    # -O2
    p.append(rect(490, 184, 440, 286, fill="#f6fbf6", stroke=GREEN, sw=1.8, rx=12))
    p.append(text(506, 206, "-O2  (оптимізовано)", size=13, color=GREEN, bold=True, anchor="start"))
    p.append(text(506, 224, "усе в регістрах, тіло стиснуте — те саме за змістом",
                  size=10, color=MUTED, italic=True, anchor="start"))
    o2 = [
        (250, "  li    a5, 0             ; sum=0 (регістр)", INK),
        (268, "  blez  a1, .Lend         ; n<=0 ? вийти", INK),
        (286, ".L3:", MUTED),
        (304, "  lw    a4, 0(a0)         ; a[i]", INK),
        (322, "  addi  a0, a0, 4         ; покажчик далі", INK),
        (340, "  add   a5, a5, a4        ; sum += a[i]", INK),
        (358, "  bne   a0, a3, .L3       ; не кінець? — назад", INK),
        (376, "  ...", MUTED),
        (394, "  mv    a0, a5            ; повернути sum", INK),
        (412, "  ret", INK),
    ]
    for ry, code, col in o2:
        p.append(mono(504, ry, code, size=12, color=col))
    p.append(text(710, 466, "≈ 4 команди у тілі · жодного звертання в стек", size=10, color=GREEN, bold=True))
    render(os.path.join(OUT, "optimization.svg"), W, H, *p)


if __name__ == "__main__":
    fig_contract()
    fig_encoding()
    fig_asm()
    fig_families()
    fig_different()
    fig_stable()
    fig_timeline()
    fig_open_vs_closed()
    fig_modular()
    fig_market()
    fig_credit()
    fig_isa_map()
    fig_esp32_split()
    fig_block_firstword()
    fig_loop_to_asm()
    fig_anatomy()
    fig_optimization()
    print("OK: figures written to", OUT)
