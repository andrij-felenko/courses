# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Де стоїть seccomp на шляху виклику і що він бачить ───────────────────
def fig_syscall_gate():
    W, H = 1300, 900
    p = []

    # простір користувача
    p.append(fitbox(60, 60, 560, 68,
                    "процес: код застосунку і libc",
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(60, 148, 560, 74,
                    "інструкція входу в ядро: номер виклику й шість аргументів\n"
                    "покладено в регістри",
                    size=14, fill=FILL, stroke=LINE))

    # пам'ять процесу збоку
    p.append(fitbox(700, 148, 540, 118,
                    "пам'ять процесу\n"
                    "за адресою з args[0] лежить рядок \"/tmp/ok\",\n"
                    "але сусідній потік може переписати його будь-якої миті",
                    size=13, fill=WARM_FILL, stroke=WARM))

    p.append(line(60, 250, 1240, 250, color=MUTED, dash="7,6"))
    p.append(text(150, 272, "простір користувача", size=13, color=MUTED))
    p.append(text(1140, 272, "ядро", size=13, color=MUTED))

    p.append(arrow(340, 222, 340, 300))

    # точка входу
    p.append(fitbox(60, 300, 560, 62, "точка входу в ядро",
                    size=15, bold=True, fill=FILL, stroke=LINE))
    p.append(arrow(340, 362, 340, 400))

    # блок seccomp
    p.append(rect(60, 400, 560, 250, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(text(340, 432, "перевірка seccomp: прогін програми фільтра",
                  size=15, bold=True, color=NEG))
    p.append(fitbox(88, 452, 504, 172,
                    "усе, що подано на вхід фільтрові:\n"
                    "nr — номер виклику\n"
                    "arch — у якій саме таблиці шукати цей номер\n"
                    "instruction_pointer — звідки зроблено виклик\n"
                    "args[0..5] — шість аргументів як голі числа",
                    size=14, fill=BG, stroke=NEG))

    # заборонена стрілка в пам'ять
    p.append(line(620, 500, 940, 500, color=POS, sw=2, dash="8,6"))
    p.append(line(760, 476, 800, 524, color=POS, sw=3))
    p.append(line(800, 476, 760, 524, color=POS, sw=3))
    p.append(fitbox(700, 552, 540, 96,
                    "читати цю пам'ять фільтрові заборонено:\n"
                    "перевірене значення можна підмінити між перевіркою\n"
                    "і вжитком, тож перевіряють лише числа",
                    size=13, fill=RED_FILL, stroke=POS))

    # вироки
    p.append(arrow(220, 650, 220, 706, color=FIELD, sw=2))
    p.append(fitbox(60, 706, 320, 118,
                    "вирок дозволяє\n"
                    "таблиця системних викликів → обробник →\n"
                    "звичайне повернення результату",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(470, 650, 470, 706, color=POS, sw=2))
    p.append(fitbox(400, 706, 840, 118,
                    "вирок не дозволяє\n"
                    "обробник не запускається взагалі: процес отримує помилку,\n"
                    "сигнал SIGSYS, передачу наглядачеві — або гине",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'syscall-gate.svg'), W, H, *p,
           title="Фільтр стоїть на вході в ядро й бачить лише регістри")


# ── 2. Слово вироку, шкала суворості й складання фільтрів ───────────────────
def fig_verdict_word():
    W, H = 1320, 880
    p = []

    # слово вироку
    p.append(text(360, 72, "32-бітне слово, яке повертає програма фільтра",
                  size=15, bold=True))
    p.append(fitbox(60, 92, 300, 78, "старші 16 бітів\nДІЯ",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(360, 92, 300, 78, "молодші 16 бітів\nДАНІ ДО ДІЇ",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(60, 186, 600, 74,
                    "для ERRNO тут номер помилки (EPERM чи ENOSYS),\n"
                    "для TRAP і TRACE — довільне число для обробника чи наглядача",
                    size=13, fill=FILL, stroke=MUTED))

    # шкала дій
    p.append(text(1000, 72, "шкала дій: від найдозвільнішої до найсуворішої",
                  size=15, bold=True))
    rows = [
        ("ALLOW",        "0x7fff0000", "виклик виконується як завжди",           GREEN_FILL, FIELD),
        ("LOG",          "0x7ffc0000", "виконується, але лишає запис в аудиті",  GREEN_FILL, FIELD),
        ("TRACE",        "0x7ff00000", "рішення передано наглядачеві ptrace",    BLUE_FILL,  NEG),
        ("USER_NOTIF",   "0x7fc00000", "рішення передано процесу-наглядачеві",   BLUE_FILL,  NEG),
        ("ERRNO",        "0x00050000", "обробник не запускається, повертається помилка", WARM_FILL, WARM),
        ("TRAP",         "0x00030000", "потокові надсилається сигнал SIGSYS",    WARM_FILL,  WARM),
        ("KILL_THREAD",  "0x00000000", "гине потік, решта процесу живе",         RED_FILL,   POS),
        ("KILL_PROCESS", "0x80000000", "гине весь процес",                       RED_FILL,   POS),
    ]
    y = 100
    for name, val, note, fill, stroke in rows:
        p.append(fitbox(700, y, 210, 56, name, size=15, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(920, y, 150, 56, val, size=14, fill=BG, stroke=MUTED))
        p.append(fitbox(1080, y, 200, 56, note, size=11, fill=BG, stroke=MUTED))
        y += 70

    p.append(fitbox(700, 676, 580, 74,
                    "як ЗНАКОВІ 32-бітні числа цей стовпчик спадає:\n"
                    "0x80000000 — найменше від'ємне, 0x7fff0000 — найбільше додатне",
                    size=13, fill=FILL, stroke=LINE, bold=True))

    # складання фільтрів
    p.append(text(360, 320, "три встановлені фільтри проганяються всі", size=15, bold=True))
    xs = [60, 260, 460]
    verdicts = [("фільтр 1", "ALLOW", GREEN_FILL, FIELD),
                ("фільтр 2", "ERRNO", WARM_FILL, WARM),
                ("фільтр 3", "ALLOW", GREEN_FILL, FIELD)]
    for x, (nm, v, fill, stroke) in zip(xs, verdicts):
        p.append(fitbox(x, 344, 170, 96, nm + "\n↓\n" + v,
                        size=14, bold=True, fill=fill, stroke=stroke))
        p.append(arrow(x + 85, 440, 360, 500))

    p.append(fitbox(200, 500, 320, 70, "мінімум", size=18, bold=True,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(360, 570, 360, 616))
    p.append(fitbox(200, 616, 320, 70, "ERRNO", size=18, bold=True,
                    fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(60, 716, 600, 96,
                    "тому доданий фільтр ніколи не розширює дозволеного:\n"
                    "щоб вирок став дозвільнішим, мінімум мав би зрости,\n"
                    "а новий доданок мінімум лише зменшує",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'verdict-word.svg'), W, H, *p,
           title="Вирок фільтра і чому суворіший завжди перемагає")


# ── 3. Спадковість фільтра й умова допуску (no_new_privs) ───────────────────
def fig_nnp_gate():
    W, H = 1300, 780
    p = []

    p.append(fitbox(70, 70, 520, 122,
                    "процес-запускач\n"
                    "1. виставляє no_new_privs\n"
                    "2. встановлює фільтр\n"
                    "3. робить exec",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(330, 192, 330, 250))
    p.append(text(430, 226, "exec", size=14, color=MUTED))

    p.append(fitbox(70, 250, 520, 104,
                    "нова програма на місці старої\n"
                    "образ замінено, а фільтр і прапорець лишилися",
                    size=15, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(330, 354, 330, 412))
    p.append(text(430, 388, "fork", size=14, color=MUTED))

    p.append(fitbox(70, 412, 520, 104,
                    "нащадок\n"
                    "успадкував і фільтр, і прапорець, зняти не може ні той, ні той",
                    size=15, fill=BLUE_FILL, stroke=NEG))

    # умова допуску
    p.append(fitbox(660, 70, 570, 176,
                    "щоб узагалі встановити фільтр, потрібне одне з двох:\n\n"
                    "· CAP_SYS_ADMIN у своєму просторі імен користувачів\n"
                    "· виставлений прапорець no_new_privs",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(660, 280, 570, 150,
                    "no_new_privs означає рівно одне:\n"
                    "exec більше ніколи не додасть повноважень —\n"
                    "біти setuid і setgid та файлові можливості\n"
                    "перестають діяти для цього процесу й усіх нащадків",
                    size=14, fill=FILL, stroke=LINE))

    p.append(fitbox(660, 464, 570, 210,
                    "чого це не дає статися\n\n"
                    "без прапорця фільтр пережив би exec програми з бітом setuid\n"
                    "і змусив би її скидання привілеїв провалитися;\n"
                    "програма, яка не перевіряє код повернення,\n"
                    "лишилася б root, гадаючи, що вже ні",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(70, 570, 520, 104,
                    "фільтр не знімається ніколи:\n"
                    "інтерфейсу зняття немає, бо вихід із пісочниці\n"
                    "коштував би один системний виклик",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'nnp-gate.svg'), W, H, *p,
           title="Фільтр незворотний і успадковується — звідси й умова допуску")


# ── 4. Як улаштований масив інструкцій і чому зсуви такі дивні ──────────────
def fig_bpf_chain():
    W, H = 1360, 870
    p = []

    p.append(text(380, 84, "масив struct sock_filter: індекс — це просто позиція в масиві",
                  size=15, bold=True))
    p.append(text(1050, 84, "як читати зсуви переходів", size=15, bold=True))

    rows = [
        ("0",  "LD   arch",                                  BLUE_FILL, NEG),
        ("1",  "JEQ  arch == AUDIT_ARCH_X86_64   jt=1 jf=0", BLUE_FILL, NEG),
        ("2",  "RET  KILL_PROCESS",                          RED_FILL,  POS),
        ("3",  "LD   nr",                                    BLUE_FILL, NEG),
        ("4",  "JGE  nr >= 0x40000000            jt=0 jf=1", BLUE_FILL, NEG),
        ("5",  "RET  KILL_PROCESS",                          RED_FILL,  POS),
        ("6",  "JEQ  nr == __NR_read             jt=0 jf=1", FILL,      LINE),
        ("7",  "RET  ALLOW",                                 GREEN_FILL, FIELD),
        ("8",  "JEQ  nr == __NR_write            jt=0 jf=1", FILL,      LINE),
        ("9",  "RET  ALLOW",                                 GREEN_FILL, FIELD),
        ("…",  "решта дозволених пар, так само по дві",      FILL,      MUTED),
        ("n",  "RET  ERRNO(ENOSYS)",                         WARM_FILL, WARM),
    ]
    y0, step, h = 112, 58, 48
    for i, (idx, txt, fill, stroke) in enumerate(rows):
        y = y0 + step * i
        p.append(fitbox(80, y, 58, h, idx, size=14, bold=True, fill=BG, stroke=MUTED))
        p.append(fitbox(146, y, 534, h, txt, size=14, fill=fill, stroke=stroke))

    # перехід рядка 1 за jt=1 → рядок 3
    y1 = y0 + step * 1 + h // 2
    y3 = y0 + step * 3 + h // 2
    p.append(line(680, y1, 712, y1, color=NEG, sw=1.6))
    p.append(line(712, y1, 712, y3, color=NEG, sw=1.6))
    p.append(arrow(712, y3, 680, y3, color=NEG, sw=1.6))
    p.append(text(716, (y1 + y3) // 2, "jt=1", size=11, color=NEG, anchor="start"))

    # перехід рядка 6 за jf=1 → рядок 8
    y6 = y0 + step * 6 + h // 2
    y8 = y0 + step * 8 + h // 2
    p.append(line(680, y6, 712, y6, color=MUTED, sw=1.6))
    p.append(line(712, y6, 712, y8, color=MUTED, sw=1.6))
    p.append(arrow(712, y8, 680, y8, color=MUTED, sw=1.6))
    p.append(text(716, (y6 + y8) // 2, "jf=1", size=11, color=MUTED, anchor="start"))

    p.append(fitbox(790, 112, 540, 150,
                    "jt і jf — не адреси, а зсуви:\n"
                    "скільки інструкцій пропустити,\n"
                    "рахуючи від НАСТУПНОЇ.\n"
                    "тому jt=0 означає «перейти на наступну»,\n"
                    "а не «нікуди не переходити»",
                    size=13, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(790, 290, 540, 180,
                    "звідси прийом «пара»:\n"
                    "порівняння, а одразу за ним RET ALLOW.\n\n"
                    "збіг (jt=0) — падаємо на RET ALLOW\n"
                    "не збіг (jf=1) — перестрибуємо RET\n"
                    "і йдемо на наступне порівняння.\n"
                    "усі зсуви лишаються 0 і 1, рахувати нічого",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(790, 498, 540, 150,
                    "ціна прийому: дві інструкції\n"
                    "на кожен дозволений виклик.\n"
                    "сто дозволених — двісті інструкцій поспіль,\n"
                    "і останній у ланцюзі платить за всіх",
                    size=13, fill=FILL, stroke=LINE))

    p.append(fitbox(790, 676, 540, 122,
                    "arch перевіряють ПЕРШИМ: номер без таблиці\n"
                    "не означає нічого. одразу за ним —\n"
                    "відсів x32 за бітом 0x40000000,\n"
                    "бо arch у нього той самий",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'bpf-chain.svg'), W, H, *p,
           title="Масив інструкцій фільтра і зсуви переходів")


fig_syscall_gate()
fig_verdict_word()
fig_nnp_gate()
fig_bpf_chain()
print("ok")
