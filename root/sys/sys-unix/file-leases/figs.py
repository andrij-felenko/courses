# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOOD = "#eaf7ee"
BAD  = "#fdecea"
COOL = "#eef3fb"
NEUT = "#f4f6f8"


# ── Фіг. 1: два види оренди — обіцянка, умова, привід до перерви ────────────
def fig_lease_kinds():
    W, H = 1060, 470
    p = []

    LX, LW = 30, 316
    CW, GAP = 330, 12
    C0 = LX + LW + GAP

    def cx(i):
        return C0 + i * (CW + GAP)

    heads = ["F_RDLCK\nоренда на читання",
             "F_WRLCK\nоренда на запис"]
    for i, h in enumerate(heads):
        p.append(fitbox(cx(i), 40, CW, 58, h, size=15, bold=True,
                        fill=COOL, stroke=NEG, sw=1.6))

    rows = [
        ("Яку обіцянку дає ядро",
         ("цього файлу\nніхто не пише", COOL),
         ("цей файл не відкритий\nбільш ніким", COOL)),
        ("За якої умови видається",
         ("файл не відкрито на запис —\nані іншими, ані прохачем", NEUT),
         ("інших відкритих дескрипторів\nна файл немає", NEUT)),
        ("Що її рве",
         ("чуже відкриття на запис,\ntruncate", BAD),
         ("будь-яке чуже відкриття,\ntruncate", BAD)),
        ("Прийшов чужий читач",
         ("нічого не стається", GOOD),
         ("досить знизити\nоренду до F_RDLCK", GOOD)),
        ("Прийшов чужий письменник",
         ("оренду треба віддати", BAD),
         ("оренду треба віддати", BAD)),
    ]

    y, RH = 116, 62
    for label, *cells in rows:
        p.append(fitbox(LX, y, LW, RH, label, size=14, pad=10,
                        fill="#ffffff", stroke=MUTED, sw=1.2))
        for i, (txt, col) in enumerate(cells):
            p.append(fitbox(cx(i), y, CW, RH, txt, size=13, pad=10,
                            fill=col, stroke=MUTED, sw=1.2))
        y += RH + 8

    p.append(text(LX, y + 26,
                  "Умови у другому рядку не свавільні: ядро видає лише ту обіцянку, "
                  "яка істинна вже в мить видачі.",
                  size=14, anchor="start", color=MUTED))

    render(os.path.join(OUT, "lease-kinds.svg"), W, H, *p,
           title="Два види оренди й що з чого випливає")


# ── Фіг. 2: перерва оренди по кроках і хто в який момент спить ─────────────
def fig_lease_break():
    W, H = 1160, 720
    p = []

    AX, AW = 96, 330      # орендар
    BX, BW = 452, 250     # ядро
    CX, CW = 728, 300     # третій процес
    RX = 1052             # дужка строку

    p.append(text(AX + AW / 2, 46, "орендар", size=15, bold=True))
    p.append(text(BX + BW / 2, 46, "ядро", size=15, bold=True))
    p.append(text(CX + CW / 2, 46, "третій процес", size=15, bold=True))

    p.append(text(46, 74, "час", size=13, color=MUTED))
    p.append(arrow(46, 92, 46, 616, color=MUTED, sw=1.6))

    RH = 58
    ys = [86, 166, 246, 326, 406, 486, 566]

    steps = [
        (0, 'fcntl(fd, F_SETLEASE, F_WRLCK)\n— «файл мій, попередьте про чужих»', COOL),
        (2, 'open("doc", O_RDONLY)', "#f7f2ea"),
        (1, "оренда на цьому inode є:\nвідкривача — спати,\nорендареві — сигнал", BAD),
        (0, "обробник: si_fd → у самотрубу\nголовний цикл: скинути кеш", GOOD),
        (0, "fcntl(fd, F_SETLEASE, F_RDLCK)\n— зниження, читати я ще можу", GOOD),
        (1, "будить того, хто відкривав", COOL),
        (2, "open повертає дескриптор", "#f7f2ea"),
    ]

    lanes = {0: (AX, AW), 1: (BX, BW), 2: (CX, CW)}
    for (lane, txt, col), y in zip(steps, ys):
        x, w = lanes[lane]
        p.append(fitbox(x, y, w, RH, txt, size=13, pad=10,
                        fill=col, stroke=INK if lane == 1 else MUTED, sw=1.4))

    # стрілки між кроками
    p.append(arrow(CX, ys[1] + RH / 2, BX + BW + 6, ys[2] + RH / 2 - 8, color=INK, sw=1.8))
    p.append(arrow(BX, ys[2] + RH / 2, AX + AW + 6, ys[3] + RH / 2 - 8, color=POS, sw=2))
    p.append(arrow(AX + AW, ys[4] + RH / 2, BX - 6, ys[5] + RH / 2 - 8, color=FIELD, sw=2))
    p.append(arrow(BX + BW, ys[5] + RH / 2, CX - 6, ys[6] + RH / 2 - 8, color=INK, sw=1.8))

    # сон третього процесу
    p.append(rect(CX - 16, ys[2] + 6, 8, ys[6] - ys[2] - 12,
                  fill="#f0d9d6", stroke=POS, sw=1.2, rx=4))
    p.append(text(CX + CW / 2, ys[4] + RH / 2 + 4, "спить в open", size=14, color=POS))

    # дужка строку
    p.append(line(RX, ys[2] + 8, RX, ys[4] + RH - 8, color=NEG, sw=2))
    p.append(line(RX - 10, ys[2] + 8, RX, ys[2] + 8, color=NEG, sw=2))
    p.append(line(RX - 10, ys[4] + RH - 8, RX, ys[4] + RH - 8, color=NEG, sw=2))
    p.append(text(RX + 8, ys[3] + 10, "не більше", size=13, color=NEG, anchor="start"))
    p.append(text(RX + 8, ys[3] + 30, "45 секунд", size=13, color=NEG, anchor="start", bold=True))

    p.append(text(AX, 664,
                  "Промовчав орендар усі 45 секунд — ядро знімає оренду саме "
                  "й будить відкривача без нього.",
                  size=14, anchor="start"))
    p.append(text(AX, 692,
                  "Окремого сповіщення про це не буде: орендар дізнається лише з F_GETLEASE.",
                  size=14, anchor="start", color=MUTED))

    render(os.path.join(OUT, "lease-break.svg"), W, H, *p,
           title="Перерва оренди: хто спить, хто діє і скільки на це часу")


# ── Фіг. 3: вузькі ворота — що рве оренду, а що йде повз ───────────────────
def fig_what_breaks():
    W, H = 1140, 620
    p = []

    LX, LW = 30, 430
    GX, GW = 530, 128     # ворота
    IX, IW = 760, 320     # inode

    p.append(fitbox(IX, 96, IW, 420,
                    "inode файлу\n\nвміст, метадані,\nсписок оренд",
                    size=15, pad=14, fill=NEUT, stroke=INK, sw=1.8))

    p.append(fitbox(GX, 96, GW, 190,
                    "перевірка\nоренди",
                    size=15, bold=True, pad=10, fill="#f0d9d6", stroke=POS, sw=2))
    p.append(text(GX + GW / 2, 314, "open і truncate", size=13, color=POS))
    p.append(text(GX + GW / 2, 336, "— і більше ніде", size=13, color=POS))

    through = [
        'open(…, O_RDONLY)',
        'open(…, O_WRONLY)',
        'truncate(…, 0)',
    ]
    around = [
        'write у вже відкритий fd',
        'запис у наявне відображення mmap',
        'rename і unlink імені файлу',
        'запис із іншої машини по NFS',
    ]

    y, RH = 100, 56
    for t in through:
        p.append(fitbox(LX, y, LW, RH, t, size=14, pad=10,
                        fill=BAD, stroke=POS, sw=1.4))
        p.append(arrow(LX + LW + 6, y + RH / 2, GX - 6, y + RH / 2, color=POS, sw=2))
        y += RH + 8
    p.append(text(LX, y + 20, "рве оренду — орендар дізнається до того, як доступ станеться",
                  size=14, anchor="start", color=POS))

    y = 344
    for t in around:
        p.append(fitbox(LX, y, LW, RH, t, size=14, pad=10,
                        fill=COOL, stroke=NEG, sw=1.4))
        p.append(arrow(LX + LW + 6, y + RH / 2, IX - 6, y + RH / 2, color=NEG, sw=1.8))
        y += RH + 8
    p.append(text(LX, y + 20, "оренда мовчить — ядро тут її просто не питає",
                  size=14, anchor="start", color=NEG))

    render(os.path.join(OUT, "what-breaks.svg"), W, H, *p,
           title="Вузькі ворота оренди: що крізь них іде, а що повз")


fig_lease_kinds()
fig_lease_break()
fig_what_breaks()
print("ok")


# ── Фіг. 4 (вставка hist): дві лінії походження сходяться в коді оренд ──────
def fig_lease_lineages():
    W, H = 1080, 470
    p = []

    BW, BH = 230, 96
    XS = [30, 290, 550]
    Y_SMB, Y_NFS = 96, 336
    CX, CY, CW, CH = 830, 194, 220, 128

    p.append(text(30, 40, "Дві лінії, що прийшли до однієї конструкції",
                  size=17, anchor="start", bold=True))

    p.append(text(30, 78, "лінія SMB", size=13, anchor="start", color=NEG))
    smb = [
        ["SMB / LAN Manager", "оплок: клієнт кешує,", "сервер шле oplock break"],
        ["NT LM 0.12 (CIFS)", "рівень II: кеш читання", "для кількох клієнтів"],
        ["Samba на Linux", "обіцяє за ядро,", "а чужих відкрить не бачить"],
    ]
    for i, lines in enumerate(smb):
        p.append(fitbox(XS[i], Y_SMB, BW, BH, lines, size=14, pad=10,
                        fill=COOL, stroke=NEG, sw=1.4))
        if i < 2:
            p.append(arrow(XS[i] + BW + 4, Y_SMB + BH / 2,
                           XS[i + 1] - 4, Y_SMB + BH / 2, color=NEG, sw=1.8))

    p.append(text(30, 318, "лінія NFSv4", size=13, anchor="start", color=POS))
    nfs = [
        ["NFSv4, RFC 3010 (2000)", "делегування + CB_RECALL", "зворотним каналом"],
        ["RFC 3530 (2003)", "заміна RFC 3010,", "конструкцію збережено"],
        ["nfsd у Linux", "делегування — ті самі оренди", "з прапорцем FL_DELEG"],
    ]
    for i, lines in enumerate(nfs):
        p.append(fitbox(XS[i], Y_NFS, BW, BH, lines, size=14, pad=10,
                        fill=GOOD, stroke=POS, sw=1.4))
        if i < 2:
            p.append(arrow(XS[i] + BW + 4, Y_NFS + BH / 2,
                           XS[i + 1] - 4, Y_NFS + BH / 2, color=POS, sw=1.8))

    p.append(fitbox(CX, CY, CW, CH,
                    ["ядро Linux, fs/locks.c", "обіцянка · відкликання", "· таймер",
                     "F_SETLEASE — з версії 2.4"],
                    size=14, pad=10, fill=NEUT, stroke=INK, sw=1.6))

    p.append(arrow(XS[2] + BW + 4, Y_SMB + BH / 2, CX - 6, CY + 34, color=NEG, sw=1.8))
    p.append(arrow(XS[2] + BW + 4, Y_NFS + BH / 2, CX - 6, CY + CH - 26, color=POS, sw=1.8))

    render(os.path.join(OUT, "lease-lineages.svg"), W, H, *p,
           title="Дві лінії походження оренд сходяться в одному коді ядра")


fig_lease_lineages()


# ── Фіг. 5 (вставка api): ланцюг перевірок F_SETLEASE і звідки яка помилка ──
def fig_setlease_gates():
    W, H = 990, 760
    p = []

    GX, GW, GH = 74, 520, 56
    EX, EW, EH = 664, 232, 44
    SX = 46                     # хребет «проходить далі»
    y0, STEP = 66, 76

    gates = [
        ("arg — не F_RDLCK, не F_WRLCK\nі не F_UNLCK", "EINVAL", BAD, POS),
        ("власник файлу ≠ fsuid процесу\nі немає CAP_LEASE", "EACCES", BAD, POS),
        ("заборонив модуль безпеки\n(SELinux, AppArmor)", "EACCES / EPERM", BAD, POS),
        ("не звичайний файл\nабо ФС оренд не вміє", "EINVAL", BAD, POS),
        ("файл відкрито так, що заявлена\nобіцянка вже хибна", "EAGAIN", BAD, POS),
        ("на файлі чужа оренда\nабо її саме рвуть", "EAGAIN", BAD, POS),
        ("це зміна ВЛАСНОЇ оренди\nна цьому ж описі файлу", "успіх, далі не питають", GOOD, FIELD),
        ("leases-enable = 0", "EINVAL", BAD, POS),
    ]

    ys = [y0 + i * STEP for i in range(len(gates))]

    for (label, err, col, stroke), y in zip(gates, ys):
        p.append(fitbox(GX, y, GW, GH, label, size=14, pad=10,
                        fill=NEUT, stroke=MUTED, sw=1.3))
        p.append(arrow(GX + GW + 6, y + GH / 2, EX - 6, y + GH / 2,
                       color=stroke, sw=1.7))
        p.append(fitbox(EX, y + (GH - EH) / 2, EW, EH, err, size=14, bold=True,
                        pad=8, fill=col, stroke=stroke, sw=1.5))

    y_ok = ys[-1] + STEP
    p.append(fitbox(GX, y_ok, GW, GH, "оренду видано — fcntl повертає 0",
                    size=15, bold=True, pad=10, fill=GOOD, stroke=FIELD, sw=1.8))

    p.append(arrow(SX, y0 - 12, SX, y_ok + GH / 2, color=MUTED, sw=1.8))
    for y in ys + [y_ok]:
        p.append(line(SX, y + GH / 2, GX - 6, y + GH / 2, color=MUTED, sw=1.2))

    p.append(text(EX + EW / 2, y0 - 22, "виходить сюди", size=13, color=MUTED))
    p.append(text(SX + 4, y0 - 30, "перевірки", size=13, color=MUTED, anchor="start"))
    p.append(text(SX + 4, y0 - 12, "йдуть згори вниз", size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "setlease-gates.svg"), W, H, *p,
           title="Порядок перевірок у F_SETLEASE: перша, що спрацювала, і дає errno")


fig_setlease_gates()


# ── Фіг. 5 (вставка proj): дві зони орендаря і самотруба між ними ───────────
def fig_holder_inside():
    W, H = 1020, 580
    p = []

    AX, AW = 20, 350
    PX, PW = 420, 180
    BX, BW = 650, 350
    SH, GAP = 56, 12

    p.append(fitbox(AX, 36, AW, 46,
                    "обробник сигналу: руки звʼязані",
                    size=15, bold=True, fill=BAD, stroke=POS, sw=1.6))
    p.append(fitbox(BX, 36, BW, 46,
                    "головний цикл: тут можна все",
                    size=15, bold=True, fill=GOOD, stroke=NEG, sw=1.6))

    a_steps = [
        ("прилетів SIGRTMIN,\nу siginfo si_fd = 3", COOL),
        ("зберегти errno", NEUT),
        ("write(wake[1], &fd, 1)", GOOD),
        ("повернути errno", NEUT),
    ]
    y = 104
    for txt, col in a_steps:
        p.append(fitbox(AX, y, AW, SH, txt, size=14, pad=10,
                        fill=col, stroke=MUTED, sw=1.3))
        y += SH + GAP

    p.append(fitbox(AX, 386, AW, 70,
                    "тут заборонено:\nfsync · malloc · замок\nмережа · printf",
                    size=14, pad=10, fill=BAD, stroke=POS, sw=1.5))

    p.append(fitbox(PX, 240, PW, SH,
                    "самотруба:\n1 байт = 1 подія",
                    size=13, pad=8, fill=NEUT, stroke=INK, sw=1.6))

    p.append(fitbox(BX, 104, BW, SH,
                    "поки труба порожня —\nцикл спить у poll()",
                    size=14, pad=10, fill=NEUT, stroke=MUTED, sw=1.3))

    b_steps = [
        ("poll() прокинувся,\nчитаємо байт", COOL),
        ("доводимо файл до ладу\n(скидаємо свій кеш)", NEUT),
        ("fcntl(fd, F_GETLEASE):\nчого від нас чекає ядро", COOL),
    ]
    y = 240
    for txt, col in b_steps:
        p.append(fitbox(BX, y, BW, SH, txt, size=14, pad=10,
                        fill=col, stroke=MUTED, sw=1.3))
        y += SH + GAP

    OW = (BW - 14) / 2
    p.append(fitbox(BX, 444, OW, 76,
                    "F_RDLCK — прийшов\nчитач: знижуємо,\nкеш лишається", size=13, pad=8,
                    fill=GOOD, stroke=NEG, sw=1.4))
    p.append(fitbox(BX + OW + 14, 444, OW, 76,
                    "F_UNLCK — прийшов\nписьменник: віддаємо\nоренду зовсім", size=13, pad=8,
                    fill=BAD, stroke=POS, sw=1.4))

    p.append(arrow(AX + AW + 4, 268, PX - 6, 268, color=NEG, sw=1.8))
    p.append(arrow(PX + PW + 4, 268, BX - 6, 268, color=NEG, sw=1.8))
    p.append(arrow(BX + BW / 4, 432 + 8, BX + OW / 2, 440, color=MUTED, sw=1.4))
    p.append(arrow(BX + BW * 3 / 4, 432 + 8, BX + OW * 1.5 + 14, 440, color=MUTED, sw=1.4))

    p.append(text(W / 2, 562,
                  "від сигналу до відповіді — не більш як lease-break-time (45 с)",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(OUT, "holder-inside.svg"), W, H, *p,
           title="Обробник лише переносить факт у дескриптор — працює цикл")


fig_holder_inside()
