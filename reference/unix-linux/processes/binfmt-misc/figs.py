# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: ланцюг обробників формату всередині execve ──────────────────────
# Ідея: binfmt_misc стоїть ОСТАННІМ, і саме тому відмова binfmt_elf на полі
# «цільова машина» працює як перепустка далі — на цьому й тримається запуск
# чужих архітектур.
def fig_format_chain():
    W, H = 1140, 740
    p = []

    LX, LW = 60.0, 460.0          # колонка обробників
    RX, RW = 570.0, 510.0         # колонка присудів
    CX = LX + LW / 2              # вісь стрілок ліворуч

    p.append(fitbox(LX, 54, W - 2 * LX, 50,
                    "execve відкрив файл і прочитав перші 256 байтів — далі треба вгадати формат",
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.5))

    p.append(arrow(CX, 106, CX, 138))

    # ── обробник 1: ELF ──
    p.append(fitbox(LX, 142, LW, 88,
                    ["binfmt_elf", "прикмета \\x7fELF, а далі —",
                     "поле «цільова машина» мусить", "збігтися з цим процесором"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(fitbox(RX, 142, RW, 40,
                    "рідний ELF x86-64:  образ побудовано, кінець",
                    size=13, fill="#eafaf1", stroke=FIELD, sw=1.5))
    p.append(fitbox(RX, 190, RW, 40,
                    "ELF AArch64:  машина не та  →  «не моє»",
                    size=13, fill="#fdeeec", stroke=POS, sw=1.5))

    p.append(arrow(CX, 232, CX, 262))

    # ── обробник 2: сценарій ──
    p.append(fitbox(LX, 266, LW, 66,
                    ["binfmt_script", "прикмета «#!» на самому початку"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(fitbox(RX, 278, RW, 42,
                    "перші два байти інші  →  «не моє»",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.4))

    p.append(arrow(CX, 334, CX, 364))

    # ── обробник 3: binfmt_misc ──
    p.append(fitbox(LX, 368, LW, 104,
                    ["binfmt_misc", "власного формату не знає:",
                     "перебирає рядки таблиці,", "заповненої з простору користувача"],
                    size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.8))
    p.append(fitbox(RX, 380, RW, 80,
                    ["двадцять байтів збіглися під маскою  →  підміна:",
                     "виконуваним файлом стає qemu-aarch64-static,",
                     "а початковий шлях переїжджає йому в аргументи"],
                    size=13, fill="#eafaf1", stroke=FIELD, sw=1.5))

    p.append(arrow(CX, 474, CX, 504))

    p.append(fitbox(LX, 508, LW, 78,
                    ["список вичерпано", "жоден обробник не впізнав файл"],
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(fitbox(RX, 520, RW, 54,
                    ["execve повертає ENOEXEC —",
                     "оболонка перекладає це як «Exec format error»"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.5))

    p.append(fitbox(LX, 610, W - 2 * LX, 86,
                    ["binfmt_misc додає себе в КІНЕЦЬ списку, і це несуча властивість.",
                     "Вбудовані обробники завжди мають першу відмову — рідну програму цієї машини перехопити не вийде.",
                     "І навпаки: відмова binfmt_elf на чужій архітектурі не є помилкою запуску, а перепусткою далі по ланцюгу."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "format-chain.svg"), W, H, *p,
           title="Кого ядро питає, що це за файл")


# ── Фіг. 2: прикмета й маска на справжньому заголовку ELF ───────────────────
# Ідея: маска перетворює точний збіг на збіг за СУТТЄВИМИ полями. Два нулі в
# ній мають різні причини: байт ABI викинуто цілком, у типі файлу погашено
# молодший біт — щоб один рядок накрив і ET_EXEC, і позиційно-незалежний.
def fig_magic_mask():
    W, H = 1200, 720
    p = []

    X0, CW = 156.0, 48.0          # початок сітки й ширина клітинки
    LBL = X0 - 16                 # правий край підписів рядків

    magic = ["7f", "45", "4c", "46", "02", "01", "01", "00",
             "00", "00", "00", "00", "00", "00", "00", "00",
             "02", "00", "b7", "00"]
    mask = ["ff", "ff", "ff", "ff", "ff", "ff", "ff", "00",
            "ff", "ff", "ff", "ff", "ff", "ff", "ff", "ff",
            "fe", "ff", "ff", "ff"]

    # колір клітинки: звичайна · викинута маскою · частково погашена
    def tone(i):
        if mask[i] == "00":
            return "#fdeeec", POS
        if mask[i] == "fe":
            return "#fdf6e3", "#b8860b"
        return "#eef3fb", NEG

    # рядок номерів байтів
    p.append(text(LBL, 78, "байт", size=13, color=MUTED, anchor="end", bold=True))
    for i in range(20):
        p.append(text(X0 + i * CW + CW / 2, 78, str(i), size=12, color=MUTED))

    # рядок magic
    p.append(text(LBL, 118, "magic", size=13, color=INK, anchor="end", bold=True))
    for i in range(20):
        fill, stroke = tone(i)
        p.append(fitbox(X0 + i * CW + 2, 94, CW - 4, 42, magic[i],
                        size=14, pad=4, fill=fill, stroke=stroke, sw=1.4))

    # рядок mask
    p.append(text(LBL, 170, "mask", size=13, color=INK, anchor="end", bold=True))
    for i in range(20):
        fill, stroke = tone(i)
        p.append(fitbox(X0 + i * CW + 2, 146, CW - 4, 42, mask[i],
                        size=14, pad=4, fill=fill, stroke=stroke, sw=1.4))

    # легенда груп — двома колонками, без виносок (щоб ніщо нічого не перетинало)
    groups_left = [
        ("байти 0–3", "підпис \\x7fELF", NEG),
        ("байт 4", "клас: 2 = 64-бітний файл", NEG),
        ("байт 5", "порядок байтів: 1 = молодший наперед", NEG),
        ("байт 6", "версія заголовка", NEG),
    ]
    groups_right = [
        ("байт 7", "ABI операційної системи — маску обнулено", POS),
        ("байти 8–15", "версія ABI і доповнення — нулі", NEG),
        ("байти 16–17", "тип файлу; у масці 0xfe погашено молодший біт", "#b8860b"),
        ("байти 18–19", "машина: 0x00b7 = 183 = AArch64", NEG),
    ]

    def legend(x, w, rows, y0):
        y = y0
        for name, body, color in rows:
            p.append(fitbox(x, y, 150, 42, name, size=12.5,
                            fill="#ffffff", stroke=color, sw=1.4, bold=True))
            p.append(fitbox(x + 158, y, w - 158, 42, body, size=12.5,
                            fill="#f4f6f8", stroke="#c8ced6", sw=1.2))
            y += 50

    legend(60, 520, groups_left, 220)
    legend(620, 520, groups_right, 220)

    # арифметика маски на найцікавішому байті
    p.append(fitbox(60, 434, W - 120, 40,
                    "чому саме 0xfe: один рядок таблиці має прийняти і виконуваний файл, і позиційно-незалежний",
                    size=14, fill="#fdf6e3", stroke="#b8860b", sw=1.6, bold=True))

    calc = [
        "позиційно-незалежний:   байт 16 = 0x03      0x03 & 0xfe = 0x02   =  прикмета  →  збіг",
        "за фіксованою адресою:  байт 16 = 0x02      0x02 & 0xfe = 0x02   =  прикмета  →  збіг",
    ]
    y = 486
    for ln in calc:
        p.append(fitbox(60, y, W - 120, 42, ln, size=13.5,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))
        y += 50

    p.append(fitbox(60, 596, W - 120, 84,
                    ["Перед звірянням ядро накладає маску на прочитане з файлу й лише тоді порівнює з прикметою.",
                     "Одиниця в масці означає «цей біт має збігтися», нуль — «байдуже, що там».",
                     "Тому один запис накриває цілу архітектуру, а не одну конкретну збірку."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "magic-mask.svg"), W, H, *p,
           title="Прикмета й маска: рядок, яким QEMU реєструє AArch64")


# ── Фіг. 3: як підміна переписує argv ───────────────────────────────────────
# Ідея: уся підміна формату ззовні зводиться до одного — як переписано масив
# аргументів. Прапорець P не «зберігає нульовий елемент на місці», а додає
# шлях зайвим аргументом, тож початковий argv[0] з'їжджає на третє місце.
def fig_argv_rewrite():
    W, H = 1160, 640
    p = []

    p.append(fitbox(60, 52, W - 120, 46,
                    "користувач набрав:   ./hello-arm --verbose file.txt",
                    size=14.5, fill="#ffffff", stroke=INK, sw=1.5))

    PW = 500.0
    LX, RX = 60.0, 600.0

    p.append(text(LX + PW / 2, 132, "типово (прапорця P немає)", size=15,
                  color=POS, bold=True))
    p.append(text(RX + PW / 2, 132, "з прапорцем P", size=15,
                  color=FIELD, bold=True))

    plain = [
        ("argv[0]", "/usr/bin/qemu-aarch64-static", "інтерпретатор із таблиці", NEG, "#eef3fb"),
        ("argv[1]", "/home/u/hello-arm", "повний шлях до файлу", FIELD, "#eafaf1"),
        ("argv[2]", "--verbose", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
        ("argv[3]", "file.txt", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
        ("—", "початковий «./hello-arm» затерто", "його місце зайняв шлях", POS, "#fdeeec"),
    ]
    kept = [
        ("argv[0]", "/usr/bin/qemu-aarch64-static", "інтерпретатор із таблиці", NEG, "#eef3fb"),
        ("argv[1]", "/home/u/hello-arm", "повний шлях до файлу", FIELD, "#eafaf1"),
        ("argv[2]", "./hello-arm", "початковий argv[0] — уцілів", FIELD, "#eafaf1"),
        ("argv[3]", "--verbose", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
        ("argv[4]", "file.txt", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
    ]

    def column(x, rows):
        y = 148.0
        for idx, val, note, color, fill in rows:
            p.append(fitbox(x, y, 74, 38, idx, size=12, pad=4,
                            fill="#ffffff", stroke=MUTED, sw=1.1, color=MUTED, bold=True))
            p.append(fitbox(x + 82, y, PW - 82, 38, val, size=12.5,
                            fill=fill, stroke=color, sw=1.5))
            p.append(fitbox(x, y + 40, PW, 26, note, size=11.5, pad=4,
                            fill="#ffffff", stroke="#dfe3e8", sw=1.0, color=MUTED))
            y += 74

    column(LX, plain)
    column(RX, kept)

    p.append(fitbox(60, 528, W - 120, 88,
                    ["Прапорець P не тримає початковий argv[0] на нульовому місці — він додає шлях до файлу ЗАЙВИМ",
                     "аргументом, тож початковий нульовий з'їжджає на третє місце. Щоб інтерпретатор розрізнив ці два",
                     "вигляди, ядро від версії 5.12 виставляє біт AT_FLAGS_PRESERVE_ARGV0 у допоміжному векторі."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "argv-rewrite.svg"), W, H, *p,
           title="Що бачить інтерпретатор: масив аргументів після підміни")


# ── Фіг. 4: чужа архітектура в контейнері й прапорець F ─────────────────────
# Ідея: F зсуває розв'язання шляху з моменту ЗАПУСКУ в момент РЕЄСТРАЦІЇ.
# Тому корінь контейнера, у якому емулятора немає, вже нічого не вирішує.
def fig_container_flow():
    W, H = 1180, 860
    p = []

    p.append(text(60, 58, "один раз на хості — реєстрація", size=14,
                  color=INK, anchor="start", bold=True))

    p.append(fitbox(60, 70, 450, 82,
                    ["рядок реєстрації з прапорцем F", "(docker … qemu-user-static --reset -p yes)"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(arrow(522, 111, 588, 111))
    p.append(fitbox(600, 70, 520, 82,
                    ["ядро ВІДКРИВАЄ /usr/bin/qemu-aarch64-static",
                     "і тримає відкритий файл у себе в таблиці"],
                    size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.8))

    p.append(line(60, 176, W - 60, 176, color=MUTED, sw=1.4, dash="8 6"))
    p.append(text(60, 200, "далі — при кожному запуску", size=14,
                  color=INK, anchor="start", bold=True))

    SX, SW = 210.0, 910.0
    TX, TW = 60.0, 130.0
    steps = [
        ("контейнер", NEG, "#eef3fb",
         ["контейнер: execve(\"/bin/sh\") — файл з образу AArch64,",
          "емулятора в цьому корені немає й не буде"]),
        ("ядро", MUTED, "#ffffff",
         ["binfmt_elf: підпис ELF на місці, але поле машини = 0x00b7",
          "→ «не моє», пошук іде далі"]),
        ("ядро", MUTED, "#ffffff",
         ["binfmt_misc: двадцять байтів збіглися під маскою",
          "→ виконуваний файл підміняють"]),
        ("ядро", FIELD, "#eafaf1",
         ["інтерпретатором стає КЛОН уже відкритого файлу з таблиці —",
          "шлях не розв'язують узагалі, тож корінь контейнера не важить"]),
        ("контейнер", NEG, "#eef3fb",
         ["qemu-aarch64-static (зібраний статично) відкриває /bin/sh",
          "у корені контейнера й виконує інструкції AArch64 на x86-64"]),
    ]

    y = 214.0
    for i, (tag, color, fill) in enumerate([(s[0], s[1], s[2]) for s in steps]):
        body = steps[i][3]
        p.append(fitbox(TX, y + 18, TW, 44, tag, size=12.5, pad=5,
                        fill="#ffffff", stroke=color, sw=1.4, color=color, bold=True))
        p.append(fitbox(SX, y, SW, 80, body, size=13.5,
                        fill=fill, stroke=color, sw=1.6))
        if i < len(steps) - 1:
            p.append(arrow(SX + SW / 2, y + 82, SX + SW / 2, y + 106))
        y += 108

    p.append(fitbox(60, 754, W - 120, 76,
                    ["Прапорець F переносить розв'язання шляху з моменту запуску в момент реєстрації.",
                     "Тому образ чужої архітектури лишається чистим: емулятор живе на хості, а користується ним контейнер."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "container-flow.svg"), W, H, *p,
           title="Запуск AArch64-образу на x86-64: де саме спрацьовує прапорець F")


# ── Фіг. 5 (вставка api): два бюджети реєстрації ────────────────────────────
# Ідея: обмежень насправді два й вони незалежні — скільки БАЙТІВ прикмети влазить
# у буфер, який execve уже прочитав, і скільки СИМВОЛІВ влазить у сам рядок.
def fig_budgets():
    W, H = 1160, 660
    p = []

    BX, BW = 300.0, 790.0          # смуга
    LX, LW = 50.0, 226.0           # колонка підписів ліворуч

    def bar_row(y, h, label, blocks, note, note_fill="#f4f6f8", note_stroke=INK):
        """blocks: список (частка_від_смуги, заливка, обвід, текст_усередині|None).
        Блоки викладаються встик, не налазячи; межу бюджету показує пунктир."""
        out = [fitbox(LX, y, LW, h, label, size=13, fill="#ffffff",
                      stroke=MUTED, sw=1.4)]
        cur = BX
        for frac, fill, stroke, inner in blocks:
            w = BW * frac
            if inner:
                out.append(fitbox(cur, y, w, h, inner, size=12.5, pad=6,
                                  fill=fill, stroke=stroke, sw=1.6, rx=4))
            else:
                out.append(rect(cur, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4))
            cur += w
        out.append(line(BX + BW, y - 10, BX + BW, y + h + 10,
                        color=INK, sw=1.6, dash="5,4"))
        out.append(fitbox(LX, y + h + 20, LW + 24 + BW, 34, note, size=13,
                          fill=note_fill, stroke=note_stroke, sw=1.4))
        return out

    # ── бюджет 1: байти буфера ──
    p.append(fitbox(LX, 50, LW + 24 + BW, 40,
                    "Бюджет буфера: offset + довжина прикмети ≤ BINPRM_BUF_SIZE = 256 байтів (у ядрах до 5.0 — 128)",
                    size=14, fill="#eef3fb", stroke=NEG, sw=1.6, bold=True))

    p += bar_row(112, 46,
                 ["рядок QEMU AArch64", "offset 0, прикмета 20 Б"],
                 [(20 / 256.0, "#eafaf1", FIELD, None),
                  (236 / 256.0, "#ffffff", MUTED, "вільно: 236 байтів буфера")],
                 "0 + 20 = 20 ≤ 256 — реєстрація проходить")

    p += bar_row(224, 46,
                 ["прикмета задалеко", "offset 240, прикмета 20 Б"],
                 [(240 / 256.0, "#f0f1f3", MUTED, "offset 240 байтів"),
                  (20 / 256.0, "#fdeeec", POS, None)],
                 "240 + 20 = 260 > 256 → EINVAL; найбільший дозволений offset для цієї прикмети — 256 − 20 = 236",
                 note_fill="#fdeeec", note_stroke=POS)

    # ── бюджет 2: символи рядка ──
    p.append(fitbox(LX, 344, LW + 24 + BW, 40,
                    "Бюджет рядка: увесь запис у файл register ≤ MAX_REGISTER_LENGTH = 1920 символів",
                    size=14, fill="#eef3fb", stroke=NEG, sw=1.6, bold=True))

    p += bar_row(406, 46,
                 ["той самий рядок QEMU", "200 символів"],
                 [(200 / 1920.0, "#eafaf1", FIELD, None),
                  (1720 / 1920.0, "#ffffff", MUTED,
                   "вільно: 20 байтів прикмети — 71 символ, маска — 80, решта на імʼя, шлях і роздільники")],
                 "запас величезний — межу в 1920 символів упирають самі лише дуже довгі прикмети")

    p += bar_row(518, 46,
                 ["межа екранування", "1024 + 1024 = 2048"],
                 [(2048 / 1920.0, "#fdeeec", POS,
                   "прикмета 256 Б і маска 256 Б, записані «\\xNN» повністю")],
                 "повний буфер із маскою в рядок не влазить: 2048 > 1920 — сирі друковані байти економлять по три символи",
                 note_fill="#fdeeec", note_stroke=POS)

    render(os.path.join(OUT, "budgets.svg"), W, H, *p,
           title="Два незалежні обмеження реєстрації: байти буфера й символи рядка")


fig_format_chain()
fig_magic_mask()
fig_argv_rewrite()
fig_container_flow()
fig_budgets()
print("готово:", OUT)


# ── Фіг: початок стека процесу й де там допоміжний вектор ──────────────────
# Ідея: у сигнатурі main() вектора немає, зате він лежить рівно за
# завершальним нулем envp — тому три рядки з покажчиками замінюють бібліотеку.
def fig_auxv_walk():
    W, H = 1120, 792
    p = []

    LX, LW = 60.0, 440.0
    RX, RW = 540.0, 520.0

    p.append(fitbox(60, 48, 1000, 44,
                    "Ядро розклало це на початку стека ще до першої інструкції програми",
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.5))

    rows = [
        (112.0, 46.0,
         ["argc = 4"],
         ["перший аргумент main()"],
         NEG, "#eef3fb"),
        (170.0, 100.0,
         ['argv[0] → "/home/dana/crslab/crsrun"',
          'argv[1] → "./hello.crs"',
          'argv[2] → "alpha"',
          'argv[3] → "beta"'],
         ["другий аргумент main():",
          "масив покажчиків на рядки аргументів"],
         NEG, "#eef3fb"),
        (282.0, 42.0,
         ["NULL"],
         ["нуль-роздільник: кінець масиву argv"],
         MUTED, "#ffffff"),
        (336.0, 78.0,
         ['envp[0] → "PATH=/usr/local/bin:/usr/bin:/bin"',
          'envp[1] → "HOME=/home/dana"',
          "…"],
         ["третій аргумент main():",
          "масив покажчиків на рядки оточення"],
         NEG, "#eef3fb"),
        (426.0, 58.0,
         ["NULL"],
         ["нуль-роздільник: кінець масиву envp —",
          "саме його шукає цикл  for (p = envp; *p; p++);"],
         FIELD, "#eafaf1"),
        (496.0, 104.0,
         ['AT_EXECFN  (31)  →  "./hello.crs"',          "AT_FLAGS    (8)  =  0x0",
          "AT_PAGESZ   (6)  =  4096",
          "…  решта пар від ядра"],
         ["допоміжний вектор: пари «тип, значення»,",
          "по два машинні слова кожна.",
          "У сигнатурі main() його немає — тільки тут."],
         FIELD, "#eafaf1"),
        (612.0, 46.0,
         ["AT_NULL     (0)  =  0"],
         ["пара з типом AT_NULL закриває вектор"],
         MUTED, "#ffffff"),
    ]

    for y, h, left, right, color, fill in rows:
        p.append(fitbox(LX, y, LW, h, left, size=13, fill=fill, stroke=color, sw=1.6))
        p.append(fitbox(RX, y, RW, h, right, size=13, fill="#ffffff",
                        stroke=MUTED, sw=1.3, color=MUTED))

    p.append(fitbox(60, 678, 1000, 68,
                    ["Три аргументи main() — це перші три ділянки цього блоку.",
                     "Допоміжний вектор лежить одразу за завершальним нулем envp,"
                     " тож дійти до нього можна лише пройшовши оточення до кінця."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "auxv-walk.svg"), W, H, *p,
           title="Початок стека нового процесу: argc, argv, envp і допоміжний вектор")


fig_auxv_walk()
