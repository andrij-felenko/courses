# -*- coding: utf-8 -*-
"""Фігури до теми «POSIX: що саме стандартизовано»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

OKF = "#eaf7ef"   # заливка «описано»
NOF = "#f2f2f4"   # заливка «поза стандартом»


# ── 1. Поверхня контракту: які шари описано, а які ні ──────────────────────
def fig_surface():
    W, H = 940, 610
    BX, BW, BH, GAP = 50, 520, 62, 18
    SX, SW = 610, 290
    y0 = 66

    layers = [
        ("Застосунок\nвживає лише те, що дозволено контрактом",
         "інший бік контракту", FIELD, OKF),
        ("Оболонка й утиліти\nмова sh, sed, awk, find, sort",
         "описано в POSIX", FIELD, OKF),
        ("Бібліотека C\nopen(), fork(), pthread_create()",
         "описано в POSIX", FIELD, OKF),
        ("Системний виклик\nномери, регістри, формат ELF",
         "поза стандартом", MUTED, NOF),
        ("Ядро\nпланувальник, VFS, драйвери",
         "поза стандартом", MUTED, NOF),
        ("Залізо\nархітектура процесора, шини",
         "поза стандартом", MUTED, NOF),
    ]

    frags = []
    for i, (body, mark, col, fill) in enumerate(layers):
        y = y0 + i * (BH + GAP)
        frags.append(fitbox(BX, y, BW, BH, body, size=14, fill=fill, stroke=col, sw=1.8))
        frags.append(fitbox(SX, y + 11, SW, BH - 22, mark, size=13,
                            fill=BG, stroke=col, sw=1.5, color=col, bold=True))

    ny = y0 + len(layers) * (BH + GAP) + 8
    frags.append(fitbox(BX, ny, SX + SW - BX, 56,
                        "Контракт живе на рівні вихідного коду:\n"
                        "перекомпілювати — так, перенести двійковий файл — ні",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'posix-surface.svg'), W, H, *frags,
           title="Що POSIX описує, а що лишає системі")


# ── 2. Три зони контракту ──────────────────────────────────────────────────
def fig_zones():
    W, H = 980, 470
    CW, CG, MX = 296, 20, 24
    heads = [
        ("Обов'язкове ядро", FIELD, OKF),
        ("Необов'язкові опції", "#b8860b", "#fdf6e3"),
        ("Свідомо вільна зона", MUTED, NOF),
    ]
    bodies = [
        ["open, read, write, close",
         "fork, execve, waitpid",
         "сигнали, канали, сокети",
         "мова оболонки sh",
         "sed, awk, find, sort, grep"],
        ["реальночасове планування",
         "черги повідомлень",
         "спільна пам'ять",
         "posix_spawn  _POSIX_SPAWN",
         "розширення XSI"],
        ["implementation-defined:",
         "   своє, але задокументоване",
         "unspecified:",
         "   різниться, покладатись не можна",
         "undefined:",
         "   програма не має права так робити"],
    ]
    foot = [
        "є завжди — питати не треба",
        "спитати: макрос, sysconf, getconf",
        "приклади: порядок readdir,\nповедінка echo -n",
    ]

    frags = []
    for i in range(3):
        x = MX + i * (CW + CG)
        col, fill = heads[i][1], heads[i][2]
        frags.append(fitbox(x, 58, CW, 44, heads[i][0], size=16,
                            fill=fill, stroke=col, sw=2, bold=True))
        bh = 216
        frags.append(rect(x, 116, CW, bh, fill=BG, stroke=col, sw=1.5))
        frags.append(mtext(x + 16, 146, bodies[i], size=13, anchor="start", lh=1.55))
        frags.append(fitbox(x, 348, CW, 62, foot[i], size=13,
                            fill=fill, stroke=col, sw=1.5))

    frags.append(fitbox(MX, 424, 3 * CW + 2 * CG, 34,
                        "Питання при перенесенні: це ядро контракту, опція чи вільна зона?",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'posix-zones.svg'), W, H, *frags,
           title="Три зони тексту стандарту")


# ── 3. Дві гілки документів і їхнє злиття ──────────────────────────────────
def fig_streams():
    W, H = 1420, 340
    BW, BH = 180, 60
    yA, yB, yM = 100, 250, 176

    def box(cx, cy, s, fill=FILL, col=LINE):
        return fitbox(cx - BW / 2, cy - BH / 2, BW, BH, s, size=13,
                      fill=fill, stroke=col, sw=1.6)

    frags = [
        text(24, yA + 5, "Гілка IEEE", size=15, anchor="start", bold=True, color=MUTED),
        text(24, yB + 5, "Гілка X/Open", size=15, anchor="start", bold=True, color=MUTED),

        box(300, yA, "1988\nPOSIX.1: виклики C"),
        box(540, yA, "1992\nPOSIX.2: sh і утиліти"),
        arrow(392, yA, 448, yA),

        box(300, yB, "1994\nSingle UNIX Spec"),
        box(540, yB, "1997\nSUSv2"),
        arrow(392, yB, 448, yB),

        arrow(636, 110, 700, 150),
        arrow(636, 240, 700, 202),

        text(1010, 116, "Austin Group (з 1998): один спільний документ",
             size=15, bold=True, color=INK),

        box(800, yM, "2001\nIssue 6", fill=OKF, col=FIELD),
        box(1010, yM, "2008\nIssue 7", fill=OKF, col=FIELD),
        box(1220, yM, "2024\nIssue 8", fill=OKF, col=FIELD),
        arrow(892, yM, 918, yM),
        arrow(1102, yM, 1128, yM),

        text(700, 306, "той самий текст виходить як IEEE 1003.1, як стандарт "
                       "The Open Group і як ISO/IEC 9945", size=14, color=MUTED),
    ]
    render(os.path.join(IMG, 'posix-streams.svg'), W, H, *frags,
           title="Два потоки стандартизації сходяться в один документ")


# ── 4. Шари оголошень і макрос, що кожен відмикає (до вставки api-) ────────
def fig_ftm_layers():
    W, H = 1160, 450
    CW, GAP, MX = 260, 20, 30
    heads = [
        ("ISO C", LINE, FILL),
        ("+ POSIX", FIELD, OKF),
        ("+ XSI", "#b8860b", "#fdf6e3"),
        ("+ GNU", NEG, "#eef3fd"),
    ]
    bodies = [
        ["printf()", "malloc()", "strcpy()", "fopen()", "qsort()", "time()"],
        ["open()", "fork()", "read()", "popen()", "fileno()",
         "getline()", "pthread_create()"],
        ["shmget()", "msgget()", "semop()", "crypt()", "strptime()"],
        ["asprintf()", "strcasestr()", "secure_getenv()", "gettid()",
         "CPU_SET()"],
    ]
    macros = [
        "нічого визначати\nне треба",
        "_POSIX_C_SOURCE\n≥ 200809L",
        "_XOPEN_SOURCE\n≥ 700",
        "_GNU_SOURCE",
    ]

    frags = []
    for i in range(4):
        x = MX + i * (CW + GAP)
        col, fill = heads[i][1], heads[i][2]
        frags.append(fitbox(x, 46, CW, 46, heads[i][0], size=17,
                            fill=fill, stroke=col, sw=2, bold=True))
        frags.append(rect(x, 110, CW, 152, fill=BG, stroke=col, sw=1.5))
        frags.append(mtext(x + 20, 138, bodies[i], size=13,
                           anchor="start", lh=1.6))
        frags.append(fitbox(x, 286, CW, 72, macros[i], size=14,
                            fill=fill, stroke=col, sw=1.6, bold=True))

    frags.append(fitbox(MX, 382, 4 * CW + 3 * GAP, 44,
                        "кожен макрос праворуч відмикає все, що ліворуч, плюс своє",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'ftm-layers.svg'), W, H, *frags,
           title="Що відмикає кожен макрос перевірки можливостей")


# ── 5. Чотири стани макроса опції — три відповіді (до вставки api-) ────────
def fig_option_decision():
    W, H = 1100, 546
    CW, GAP, MX = 240, 22, 37
    xs = [MX + i * (CW + GAP) for i in range(4)]
    cxs = [x + CW / 2 for x in xs]

    states = ["не визначено", "= -1", "= 0", "> 0   (202405L)"]
    means = [
        "опції немає\nні на компіляції,\nні на виконанні",
        "те саме, тільки\nсказано прямо",
        "на компіляції\nневідомо: залежить\nвід машини запуску",
        "опція є завжди;\nчисло називає\nредакцію стандарту",
    ]
    acts = [
        "писати обхід\nабо відмовитись",
        "писати обхід\nабо відмовитись",
        "спитати на виконанні:\nsysconf(_SC_SPAWN)\n> 0 — опція є\n-1 — опції немає",
        "вживати прямо,\nпитати не треба",
    ]
    cols = [(MUTED, NOF), (MUTED, NOF), ("#b8860b", "#fdf6e3"), (FIELD, OKF)]

    frags = [fitbox(330, 52, 440, 56,
                    "макрос опції в unistd.h\nнаприклад _POSIX_SPAWN",
                    size=15, fill=BG, stroke=INK, sw=1.8, bold=True)]
    for i in range(4):
        col, fill = cols[i]
        frags.append(arrow(550, 112, cxs[i], 146))
        frags.append(fitbox(xs[i], 152, CW, 50, states[i], size=16,
                            fill=fill, stroke=col, sw=2, bold=True))
        frags.append(arrow(cxs[i], 204, cxs[i], 228))
        frags.append(fitbox(xs[i], 234, CW, 82, means[i], size=13,
                            fill=BG, stroke=col, sw=1.5))
        frags.append(arrow(cxs[i], 318, cxs[i], 342))
        frags.append(fitbox(xs[i], 348, CW, 106, acts[i], size=13,
                            fill=fill, stroke=col, sw=1.5))

    frags.append(fitbox(MX, 480, 4 * CW + 3 * GAP, 44,
                        "нуль — єдиний стан, у якому sysconf обов'язковий; "
                        "в усіх інших він просто підтверджує",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'option-decision.svg'), W, H, *frags,
           title="Чотири стани макроса опції і що з ними робити")


# ── 6. Три класи несумісності скрипта (вставка proj-portable-shell) ────────
def fig_shell_classes():
    W, H = 1220, 606
    MX, CW, GAP = 45, 360, 25

    heads = [
        ("1. Синтаксис\nшел узагалі не розбере", FIELD, OKF),
        ("2. Поведінка\nрозібрав, робить інше", "#b8860b", "#fdf6e3"),
        ("3. Утиліти й оточення\nвидно лише на чужій машині", POS, "#fdecea"),
    ]
    bodies = [
        ["[[ -n $x ]] — подвійні дужки",
         "files=(a b c) — масив",
         "cmd <<< \"$s\" — рядок-документ",
         "function f { … } — ключове слово",
         "$'\\t' — на sh, старших за 2024"],
        ["echo -n і echo \"$x\" з \\t усередині",
         "local у функції",
         ". config.sh — шукає ще й у PATH",
         "[ $x = y ] без лапок",
         "set -e мовчить у конвеєрі"],
        ["sed -i, grep -P, readlink -f",
         "head -c: немає до Issue 8",
         "sort і comm під LC_COLLATE",
         "[a-z] поза локаллю C",
         "awk: кома замість крапки"],
    ]
    catch = [
        "dash -n script.sh\nрозбір без запуску, миттєво",
        "запуск під dash і busybox sh\nплюс shellcheck -s sh і set -eu",
        "PATH=$(command -p getconf PATH)\nLC_ALL=C і справжній цільовий образ",
    ]
    ticks = ["розбір скрипта", "перший запуск", "чужа машина, за тиждень"]

    frags = []
    for i in range(3):
        x = MX + i * (CW + GAP)
        col, fill = heads[i][1], heads[i][2]
        frags.append(fitbox(x, 58, CW, 54, heads[i][0], size=16,
                            fill=fill, stroke=col, sw=2, bold=True))
        frags.append(rect(x, 126, CW, 224, fill=BG, stroke=col, sw=1.5))
        frags.append(mtext(x + 18, 158, bodies[i], size=13, anchor="start", lh=1.62))
        frags.append(fitbox(x, 364, CW, 76, catch[i], size=13,
                            fill=fill, stroke=col, sw=1.5))

    frags.append(text(MX, 468, "коли б'є", size=13, anchor="start",
                      color=MUTED, italic=True))
    frags.append(arrow(MX, 484, MX + 3 * CW + 2 * GAP, 484, color=MUTED, sw=1.6))
    for i in range(3):
        cx = MX + i * (CW + GAP) + CW / 2
        frags.append(line(cx, 476, cx, 492, color=MUTED, sw=1.4))
        frags.append(text(cx, 516, ticks[i], size=13, color=MUTED))

    frags.append(fitbox(MX, 534, 3 * CW + 2 * GAP, 46,
                        "перші два класи вичерпуються вдома; "
                        "третій — це вже не про шел, а про те, що навколо нього",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'shell-classes.svg'), W, H, *frags,
           title="Три класи несумісності й коли кожен дається взнаки")


# ── 7. Масив проти позиційних параметрів (вставка proj-portable-shell) ─────
def fig_shell_array():
    W, H = 1140, 484
    LX, LW = 30, 100
    CX, CW = 146, 424
    AX = 590
    WX = 660

    rows = [
        ("bash", FIELD, OKF,
         'files=("звіт травень.log" "cron.log")\ngzip -- "${files[@]}"',
         [("звіт травень.log", 186), ("cron.log", 122)], True),
        ("sh — наївно", POS, "#fdecea",
         "files='звіт травень.log cron.log'\ngzip -- $files",
         [("звіт", 94), ("травень.log", 148), ("cron.log", 122)], False),
        ("sh — правильно", FIELD, OKF,
         'set -- "звіт травень.log" "cron.log"\ngzip -- "$@"',
         [("звіт травень.log", 186), ("cron.log", 122)], True),
    ]

    frags = [
        text(CX + CW / 2, 62, "як пишемо", size=14, color=MUTED, italic=True),
        text(WX + 170, 62, "що дістане gzip окремими аргументами",
             size=14, color=MUTED, italic=True),
    ]

    for i, (label, col, fill, code, words, ok) in enumerate(rows):
        cy = 122 + i * 118
        frags.append(fitbox(LX, cy - 22, LW, 44, label, size=13,
                            fill=fill, stroke=col, sw=1.6, bold=True))
        frags.append(fitbox(CX, cy - 32, CW, 64, code, size=13,
                            fill=BG, stroke=col, sw=1.6))
        frags.append(arrow(AX, cy, AX + 48, cy, color=col, sw=1.8))
        wx = WX
        for w_text, w_w in words:
            frags.append(fitbox(wx, cy - 20, w_w, 40, w_text, size=13,
                                fill=fill, stroke=col, sw=1.6))
            wx += w_w + 14
        frags.append(text(wx + 14, cy + 7, "✓" if ok else "✗",
                          size=22, color=col, bold=True))

    frags.append(fitbox(LX, 424, W - 2 * LX, 44,
                        "у стандарті є рівно один масив — позиційні параметри; "
                        "додати елемент: set -- \"$@\" \"$новий\"",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'shell-array.svg'), W, H, *frags,
           title="Масив bash і його заміна: чому лапки тут вирішують усе")


# ── 8. Три претенденти на роль єдиного тексту (вставка hist-standard-wars) ─
def fig_claimants():
    W, H = 1100, 530
    MX, CW, CG = 30, 320, 40

    heads = [
        ("SVID · 1985\nAT&T", POS, "#fdeeec"),
        ("/usr/group 1984 →\nIEEE 1003 з 1985", MUTED, FILL),
        ("X/Open XPG\nконсорціум із 1984", NEG, "#eef2fd"),
    ]
    bodies = [
        ["Що це: опис поведінки",
         "System V плюс набір",
         "перевірок SVVS",
         "",
         "Питання, на яке відповідає:",
         "«чий Unix справжній?»",
         "",
         "Сила: ліцензія на код"],
        ["Що це: перетин того,",
         "що фактично є в усіх",
         "системах одразу",
         "",
         "Питання:",
         "«що я маю право",
         "викликати з програми?»",
         "",
         "Сила: акредитований орган"],
        ["Що це: посібник",
         "із переносності мовою",
         "тендерних вимог",
         "",
         "Питання:",
         "«що я маю право",
         "вимагати в договорі?»",
         "",
         "Сила: гаманець покупця"],
    ]
    foots = [
        "Належить одному учаснику ринку —\nрешта не може на нього спертися",
        "Нейтральний, але сам нічого\nне сертифікує й марки не має",
        "Ширший за POSIX — і саме він\nзгодом видаватиме марку UNIX",
    ]

    frags = []
    for i in range(3):
        x = MX + i * (CW + CG)
        col, fill = heads[i][1], heads[i][2]
        frags.append(fitbox(x, 54, CW, 66, heads[i][0], size=15,
                            fill=fill, stroke=col, sw=2, bold=True))
        frags.append(rect(x, 138, CW, 208, fill=BG, stroke=col, sw=1.5))
        frags.append(mtext(x + 18, 166, bodies[i], size=13, anchor="start", lh=1.55))
        frags.append(fitbox(x, 362, CW, 70, foots[i], size=13,
                            fill=fill, stroke=col, sw=1.5))

    frags.append(fitbox(MX, 458, 3 * CW + 2 * CG, 46,
                        "Переміг не найкращий текст, а той, що не належав "
                        "жодному з тих, хто воював",
                        size=15, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'hist-claimants.svg'), W, H, *frags,
           title="Три претенденти на роль єдиного опису Unix")


# ── 9. Дві коаліції й вихід із пату (вставка hist-standard-wars) ───────────
def fig_wars():
    W, H = 1460, 590
    BW, BH = 236, 104
    yT, yM, yB = 108, 276, 444

    def box(cx, cy, s, fill=FILL, col=LINE, size=13):
        return fitbox(cx - BW / 2, cy - BH / 2, BW, BH, s, size=size,
                      fill=fill, stroke=col, sw=1.7)

    x1, x2, x3, x4, x5 = 160, 470, 780, 1055, 1310
    half = BW / 2

    frags = [
        text(20, 114, "Табір OSF", size=14, anchor="start", bold=True, color=MUTED),
        text(20, 450, "Табір Unix", size=14, anchor="start", bold=True, color=MUTED),
        text(20, 470, "International", size=14, anchor="start", bold=True, color=MUTED),

        box(x1, yM, "1987\nAT&T і Sun домовляються\nпро спільний SVR4",
            fill="#fdeeec", col=POS),

        box(x2, yT, "травень 1988\nOpen Software Foundation\nDEC · HP · Apollo · IBM\n"
                    "Nixdorf · Siemens · Bull"),
        box(x2, yB, "1988\nUnix International\nAT&T · Sun"),

        box(x3, yM, "березень 1993\nCOSE: шестеро учасників\nз обох таборів"),
        box(x4, yM, "1994\nSpec 1170 →\nSingle UNIX Specification\nмарка UNIX → X/Open",
            fill="#eaf7ef", col=FIELD),
        box(x5, yM, "1996 The Open Group\n1998 Austin Group\nодин спільний текст",
            fill="#eaf7ef", col=FIELD),

        arrow(x1 + half, yM - 24, x2 - half, yT + 34),
        arrow(x1 + half, yM + 24, x2 - half, yB - 34),
        arrow(x2 + half, yT + 34, x3 - half, yM - 24),
        arrow(x2 + half, yB - 34, x3 - half, yM + 24),
        arrow(x3 + half, yM, x4 - half, yM),
        arrow(x4 + half, yM, x5 - half, yM),

        text(x2, yT + BH / 2 + 30, "Motif · DCE · OSF/1", size=13, color=MUTED),
        text(x2, yB - BH / 2 - 18, "System V Release 4", size=13, color=MUTED),
    ]

    frags.append(fitbox(x1 - half, 506, x3 + half - (x1 - half), 66,
                        "Ані OSF, ані Unix International не перемогли — і саме тому\n"
                        "нейтральний текст лишився єдиним, під яким могли "
                        "підписатися всі",
                        size=14, fill=BG, stroke=INK, sw=1.8, bold=True))

    render(os.path.join(IMG, 'hist-unix-wars.svg'), W, H, *frags,
           title="Дві коаліції війни за Unix і вихід із пату")


fig_surface()
fig_zones()
fig_streams()
fig_ftm_layers()
fig_option_decision()
fig_shell_classes()
fig_shell_array()
fig_claimants()
fig_wars()
print("ok")
