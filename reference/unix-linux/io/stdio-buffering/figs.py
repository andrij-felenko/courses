# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f1f2f4"
ROSE  = "#fdecea"


# ── 1. Два буфери на шляху одного рядка ────────────────────────────────────────
def fig_two_buffers():
    W, H = 1240, 760
    p = []

    CX, BW, BH = 380, 440, 66

    stages = [
        (70,  "рядок у програмі",        "аргументи printf, пам'ять процесу",      SOFT),
        (215, "буфер stdio у FILE",      "пам'ять процесу, типово 4096 байтів",    COOL),
        (440, "кеш сторінок",            "пам'ять ядра, спільна для всіх",         WARM),
        (600, "носій",                   "диск або твердотільний накопичувач",     GREEN),
    ]
    for (y, label, sub, tint) in stages:
        p.append(rect(CX - BW / 2, y, BW, BH, fill=tint, stroke=NEG, sw=1.8, rx=8))
        p.append(text(CX, y + 28, label, size=14, bold=True, color=INK))
        p.append(text(CX, y + 50, sub, size=10.5, color=MUTED))

    # межа простору користувача й ядра
    p.append(line(60, 372, 1170, 372, color="#c8ccd2", sw=1.4, dash="7 6"))
    p.append(text(70, 364, "межа: простір користувача ↕ ядро", size=11.5, color=MUTED, anchor="start"))

    # переходи
    p.append(arrow(CX, 70 + BH + 4, CX, 215 - 6, color=NEG, sw=2))
    p.append(mtext(CX + 240, 158, "printf, fputs, fwrite\nкопіювання в пам'яті",
                   size=11.5, color=INK, anchor="start", lh=1.35))

    p.append(arrow(CX, 215 + BH + 4, CX, 440 - 6, color=POS, sw=2.2))
    p.append(mtext(CX + 240, 300, "write(2): коли спрацював режим\nабо покликали fflush",
                   size=11.5, color=POS, anchor="start", lh=1.35))

    p.append(arrow(CX, 440 + BH + 4, CX, 600 - 6, color=NEG, sw=2))
    p.append(mtext(CX + 240, 528, "зворотний запис ядра\nабо fsync на вимогу",
                   size=11.5, color=INK, anchor="start", lh=1.35))

    # що саме гине в кожній аварії
    PX, PW, PH = 760, 430, 116
    p.append(fitbox(PX, 205, PW, PH,
                    "процес упав\nSIGKILL, SIGSEGV, _exit\n\nгине лише цей буфер; усе, що\nвже пішло write, у файлі буде",
                    size=11.5, fill=ROSE, stroke=POS))
    p.append(fitbox(PX, 430, PW, PH,
                    "зникло живлення\n\nгине те, що стоїть тут;\nfflush не рятує — потрібен fsync",
                    size=11.5, fill=WARM, stroke=FIELD))

    p.append(text(W / 2, H - 40,
                  "fflush долає першу межу, fsync — другу; це різні аварії й різні ліки",
                  size=13, bold=True, color=FIELD))

    render(os.path.join(OUT, "two-buffers.svg"), W, H, *p,
           title="Буфер stdio у пам'яті процесу й кеш сторінок у ядрі: дві різні межі на шляху одного рядка")


# ── 2. Три режими на спільній осі викликів ─────────────────────────────────────
def fig_three_modes():
    W, H = 1300, 700
    p = []

    X0, STEP = 360, 74
    xs = [X0 + k * STEP for k in range(8)]
    XGAP = X0 + 8 * STEP + 26
    XFAR = XGAP + 96

    p.append(text(W / 2, 44, "вісім викликів поспіль: непарний додає слова, парний завершує рядок",
                  size=15, bold=True, color=INK))

    # ряд викликів
    CY, CW, CH = 78, 62, 36
    for k, x in enumerate(xs):
        ends = (k % 2 == 1)
        p.append(rect(x - CW / 2, CY, CW, CH, fill=(GREEN if ends else GREY),
                      stroke=LINE, sw=1.3, rx=5))
        p.append(text(x, CY + 24, ("17⏎" if ends else "поступ"), size=11, color=INK))
    p.append(text(XGAP, CY + 24, "…", size=18, color=MUTED))
    p.append(rect(XFAR - CW / 2, CY, CW, CH, fill=GREY, stroke=LINE, sw=1.3, rx=5))
    p.append(text(XFAR, CY + 24, "виклик 137", size=9.5, color=INK))

    p.append(mtext(70, CY + 14, "виклики stdio\nпо ≈30 байтів", size=11.5, color=MUTED,
                   anchor="start", lh=1.3))

    rows = [
        (230, "без буфера", "_IONBF", POS, ROSE, xs, "кожен виклик — окремий write", None),
        (390, "порядкова", "_IOLBF", NEG, COOL, xs[1::2], "write на кожному завершеному рядку", None),
        (550, "поблокова", "_IOFBF", FIELD, GREEN, [], "мовчить, поки не набереться 4096 байтів", XFAR),
    ]

    for (y, name, macro, accent, tint, marks, note, far) in rows:
        p.append(mtext(70, y - 4, name, size=14, bold=True, color=accent, anchor="start"))
        p.append(mtext(70, y + 20, macro, size=11.5, color=MUTED, anchor="start"))
        p.append(line(X0 - 46, y + 6, XFAR + 60, y + 6, color="#c8ccd2", sw=1.2))
        for x in marks:
            p.append(rect(x - 26, y - 12, 52, 34, fill=tint, stroke=accent, sw=1.6, rx=4))
            p.append(text(x, y + 10, "write", size=10.5, color=accent))
        if far is not None:
            p.append(rect(far - 26, y - 12, 52, 34, fill=tint, stroke=accent, sw=1.6, rx=4))
            p.append(text(far, y + 10, "write", size=10.5, color=accent))
        p.append(text((X0 + XFAR) / 2, y + 54, note, size=11.5, color=MUTED))

    p.append(text(W / 2, H - 36,
                  "той самий код, той самий порядок викликів — різна кількість перетинів межі",
                  size=13, bold=True, color=FIELD))

    render(os.path.join(OUT, "three-modes.svg"), W, H, *p,
           title="Коли саме трапляється write у безбуферному, порядковому й поблоковому режимах")


# ── 3. Звідки береться режим ───────────────────────────────────────────────────
def fig_mode_choice():
    W, H = 1280, 700
    p = []

    LX = 330                       # вісь лівої колонки
    p.append(text(LX, 44, "як бібліотека обирає режим", size=15, bold=True, color=INK))

    p.append(rect(LX - 220, 74, 440, 62, fill=SOFT, stroke=NEG, sw=1.8, rx=8))
    p.append(text(LX, 100, "перше використання потоку", size=13, bold=True, color=INK))
    p.append(text(LX, 122, "перший printf, fputs або fread", size=10.5, color=MUTED))

    p.append(arrow(LX, 140, LX, 186, color=NEG, sw=2))

    p.append(rect(LX - 220, 190, 440, 62, fill=COOL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(LX, 216, "fstat, а для символьного — isatty", size=13, bold=True, color=INK))
    p.append(text(LX, 238, "єдине питання: це термінал?", size=10.5, color=MUTED))

    # дві гілки
    p.append(arrow(LX - 110, 256, LX - 160, 306, color=FIELD, sw=2))
    p.append(arrow(LX + 110, 256, LX + 160, 306, color=POS, sw=2))

    p.append(rect(LX - 300, 310, 270, 62, fill=GREEN, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(LX - 165, 336, "так → порядкова", size=12.5, bold=True, color=FIELD))
    p.append(text(LX - 165, 358, "рядок виходить одразу", size=10.5, color=MUTED))

    p.append(rect(LX + 30, 310, 270, 62, fill=ROSE, stroke=POS, sw=1.8, rx=8))
    p.append(text(LX + 165, 336, "ні → поблокова", size=12.5, bold=True, color=POS))
    p.append(text(LX + 165, 358, "чекає повного буфера", size=10.5, color=MUTED))

    p.append(fitbox(LX - 250, 420, 500, 92,
                    "stderr рахують окремо: стандарт забороняє йому\n"
                    "поблоковий режим, а glibc робить його безбуферним",
                    size=12, fill=WARM, stroke=FIELD))

    p.append(fitbox(LX - 250, 540, 500, 92,
                    "розмір буфера: st_blksize з того самого fstat,\n"
                    "якщо він між 1 і BUFSIZ (8192); інакше BUFSIZ",
                    size=12, fill=GREY, stroke=LINE))

    # права колонка: три запуски однієї двійки
    RX = 760
    p.append(text(RX, 44, "та сама програма, три запуски", size=15, bold=True, color=INK, anchor="start"))

    cases = [
        (90,  "./crunch",             "стандартний вивід веде на термінал",
              "порядкова: рядок поступу видно одразу", GREEN, FIELD),
        (250, "./crunch | tee log",   "стандартний вивід веде в канал",
              "поблокова: перший write аж на 4096 байтах", ROSE, POS),
        (410, "./crunch > out.txt",   "стандартний вивід веде у файл",
              "поблокова: те саме, вивід з'явиться пачками", ROSE, POS),
    ]
    for (y, cmd, dest, effect, tint, accent) in cases:
        p.append(rect(RX, y, 460, 118, fill=tint, stroke=accent, sw=1.7, rx=8))
        p.append(text(RX + 230, y + 32, cmd, size=13, bold=True, color=INK))
        p.append(text(RX + 230, y + 62, dest, size=11, color=MUTED))
        p.append(text(RX + 230, y + 92, effect, size=11.5, color=accent))

    p.append(mtext(RX, 580,
                   "Режим — не властивість програми,\n"
                   "а наслідок того, куди її запустили.",
                   size=13, bold=True, color=FIELD, anchor="start", lh=1.4))

    render(os.path.join(OUT, "mode-choice.svg"), W, H, *p,
           title="Бібліотека обирає режим за одним питанням — чи веде дескриптор на термінал")


# ── 4. Як дозрівали три режими ────────────────────────────────────────────────
def fig_stdio_history():
    W, H = 1180, 730
    p = []

    SPINE = 210
    BX, BW, BH = 250, 880, 118
    rows = [
        (90, "1975", "iolib Майка Леска", "шоста редакція Unix",
         "переносний пакет на PDP-11, GCOS і IBM 370",
         "диск — по 512 символів · телетайп — посимвольно", COOL, NEG),
        (240, "1979", "stdio Денніса Рітчі", "сьома редакція Unix",
         "стан у FILE, дескриптор зник з інтерфейсу, getc і putc — макроси",
         "той самий вибір за isatty: термінал — без буфера", GREEN, FIELD),
        (390, "1983", "прапорець _IOLBF", "4.2BSD",
         "швидкі екранні термінали замість телетайпа на 110 бодів",
         "термінал стає порядковим, з'являється setlinebuf", WARM, POS),
        (540, "1989", "три сталі й setvbuf", "ANSI C",
         "_IOFBF, _IOLBF, _IONBF — імена для того, що вже склалося",
         "поблоковий — лише коли пристрій не інтерактивний", GREY, INK),
    ]

    p.append(line(SPINE, 118, SPINE, 630, color=MUTED, sw=2))

    for (y, year, name, where, why, effect, tint, accent) in rows:
        cy = y + BH / 2
        p.append(text(120, cy - 8, year, size=19, bold=True, color=accent))
        p.append(text(120, cy + 16, where, size=11, color=MUTED))
        p.append(circle(SPINE, cy, 9, fill="#ffffff", stroke=accent, sw=2.5))
        p.append(line(SPINE + 9, cy, BX, cy, color=MUTED, sw=1.4))
        p.append(rect(BX, y, BW, BH, fill=tint, stroke=accent, sw=1.7, rx=8))
        p.append(text(BX + 26, y + 34, name, size=15, bold=True,
                      color=INK, anchor="start"))
        p.append(text(BX + 26, y + 64, why, size=12, color=MUTED, anchor="start"))
        p.append(text(BX + 26, y + 94, effect, size=12.5, color=accent, anchor="start"))

    p.append(text(W / 2, 690,
                  "Наскрізна лінія: порцію обирає бібліотека, бо про пристрій "
                  "знає вона, а не програма.",
                  size=13, bold=True, color=MUTED))

    render(os.path.join(OUT, "stdio-history.svg"), W, H, *p,
           title="Чотири кроки від переносного пакета Леска до трьох режимів стандарту")


# ── 5. Механізм stdbuf і його сліпі зони ──────────────────────────────────────
def fig_stdbuf_mechanism():
    W, H = 1300, 700
    p = []

    LX, LW, BH = 80, 540, 100
    p.append(text(LX + LW / 2, 46, "що робить stdbuf -oL ./prog",
                  size=15, bold=True, color=INK))

    steps = [
        (80,  "1 · stdbuf",
         "ставить _STDBUF_O=L і LD_PRELOAD=libstdbuf.so",
         "і робить execvp: сам зникає, лишається оточення", COOL, NEG),
        (210, "2 · динамічний завантажувач",
         "підтягує libstdbuf.so разом з рештою бібліотек",
         "ще до першої інструкції головної функції", GREY, MUTED),
        (340, "3 · конструктор libstdbuf",
         "читає _STDBUF_O і кличе setvbuf(stdout, NULL, _IOLBF, 0)",
         "потік ще не займаний — правило дотримано", GREEN, FIELD),
        (470, "4 · main",
         "перший printf потрапляє вже в порядковий режим",
         "рядок виходить на своєму переході рядка", SOFT, INK),
    ]
    for (y, head, l1, l2, tint, accent) in steps:
        p.append(rect(LX, y, LW, BH, fill=tint, stroke=accent, sw=1.7, rx=8))
        p.append(text(LX + 24, y + 30, head, size=13.5, bold=True,
                      color=accent, anchor="start"))
        p.append(text(LX + 24, y + 58, l1, size=11, color=INK, anchor="start"))
        p.append(text(LX + 24, y + 80, l2, size=11, color=MUTED, anchor="start"))
        if y < 470:
            p.append(arrow(LX + LW / 2, y + BH + 3, LX + LW / 2, y + 126,
                           color=MUTED, sw=1.8))

    RX, RW, RH = 690, 540, 150
    p.append(text(RX + RW / 2, 46, "де цей важіль нічого не змінить",
                  size=15, bold=True, color=INK))

    blind = [
        (80, "програма сама кличе setvbuf",
         "її виклик стається пізніше за конструктор\n"
         "і просто перезаписує режим; довідка coreutils\n"
         "наводить прикладом саме tee",
         ROSE, POS),
        (250, "програма не користується stdio",
         "dd і cat читають та пишуть напряму, read і write;\n"
         "буфера бібліотеки в них немає, отже перемикати\n"
         "нема чого — розмір порції там задає bs=",
         WARM, POS),
        (420, "лишається інший важіль: псевдотермінал",
         "script -qec './prog | tee log' /dev/null\n"
         "дає програмі tty; isatty каже «так», і бібліотека\n"
         "сама обирає порядковий режим",
         GREEN, FIELD),
    ]
    for (y, head, body, tint, accent) in blind:
        p.append(rect(RX, y, RW, RH, fill=tint, stroke=accent, sw=1.7, rx=8))
        p.append(text(RX + 24, y + 34, head, size=13.5, bold=True,
                      color=accent, anchor="start"))
        p.append(mtext(RX + 24, y + 68, body, size=11, color=INK,
                       anchor="start", lh=1.5))

    p.append(text(W / 2, 650,
                  "важіль діє лише там, де буфер stdio є і його ніхто не перевизначає",
                  size=13, bold=True, color=FIELD))

    render(os.path.join(OUT, "stdbuf-mechanism.svg"), W, H, *p,
           title="Як stdbuf дотягується до setvbuf через LD_PRELOAD і чому це не завжди спрацьовує")


fig_two_buffers()
fig_three_modes()
fig_mode_choice()
fig_stdio_history()
fig_stdbuf_mechanism()
print("готово")
