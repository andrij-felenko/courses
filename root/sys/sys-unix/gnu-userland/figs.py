# -*- coding: utf-8 -*-
"""Фігури до теми «Інструментарій GNU і чому GNU/Linux»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GNU_FILL = "#eaf7ef"
KRN_FILL = "#eef2fb"
OTH_FILL = "#f4f6f8"


# ── 1. Дві половини й шов між ними ─────────────────────────────────────────
def fig_halves():
    W, H = 900, 620
    X, BW = 60, 600
    f = []

    # застосунки
    f.append(fitbox(X, 62, BW, 54, "Застосунки: редактор, браузер, сервер, ваша програма",
                    size=14, fill=OTH_FILL))

    # трійка простору користувача
    tw, gap = 190, 15
    labels = [("перший процес:\ninit / systemd — не GNU", OTH_FILL),
              ("bash, coreutils,\ngrep, sed, awk", GNU_FILL),
              ("gcc, as, ld,\nmake — тулчейн", GNU_FILL)]
    for i, (s, bg) in enumerate(labels):
        f.append(fitbox(X + i * (tw + gap), 146, tw, 78, s, size=13,
                        fill=bg, stroke=FIELD))

    # glibc
    f.append(fitbox(X, 254, BW, 56, "glibc — бібліотека C: open(), printf(), malloc(), pthread_create()",
                    size=14, fill=GNU_FILL, stroke=FIELD))

    # межа ABI
    f.append(line(X, 336, X + BW, 336, color=MUTED, sw=2, dash="8 6"))
    f.append(text(X + BW / 2, 360, "ABI системних викликів: номер у регістрі, аргументи в регістрах",
                  size=12, color=MUTED))

    # ядро
    f.append(fitbox(X, 374, BW, 88, "ЯДРО LINUX\nпроцеси · пам'ять · файлові системи · драйвери · мережа",
                    size=15, fill=KRN_FILL, stroke=NEG))

    # апаратура
    f.append(fitbox(X, 492, BW, 54, "Апаратура: процесор, пам'ять, диски, мережеві карти",
                    size=14, fill=OTH_FILL))

    # праві підписи
    f.append(line(670, 146, 670, 310, color=FIELD, sw=2))
    f.append(line(670, 146, 682, 146, color=FIELD, sw=2))
    f.append(line(670, 310, 682, 310, color=FIELD, sw=2))
    f.append(fitbox(696, 190, 178, 76, "GNU:\nмайже вся ця частина", size=14,
                    fill=GNU_FILL, stroke=FIELD, bold=True))

    f.append(line(670, 374, 670, 462, color=NEG, sw=2))
    f.append(line(670, 374, 682, 374, color=NEG, sw=2))
    f.append(line(670, 462, 682, 462, color=NEG, sw=2))
    f.append(fitbox(696, 386, 178, 64, "Linux:\nлише ця смуга", size=14,
                    fill=KRN_FILL, stroke=NEG, bold=True))

    f.append(text(W / 2, 588, "Ядро без другої половини завантажується — і одразу зупиняється: нема кого запустити",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'two-halves.svg'), W, H, *f,
           title="Що з цієї купи називається «Linux», а що — «GNU»")


# ── 2. Шлях printf крізь glibc до ядра ─────────────────────────────────────
def fig_printf_path():
    W, H = 900, 560
    X, BW = 50, 500
    f = []

    steps = [
        "printf(\"h=%.1f\\n\", h)  — рядок коду програми",
        "розбір формату, локаль, число → текст у буфер",
        "буфер stdout: до терміналу — скидання на '\\n'",
        "write(1, buf, n) — тонка обгортка glibc",
        "rax = 1, rdi/rsi/rdx = аргументи, інструкція syscall",
    ]
    ys = [62, 152, 242, 332, 422]
    for s, y in zip(steps, ys):
        fill = OTH_FILL if y == 62 else GNU_FILL
        stroke = LINE if y == 62 else FIELD
        f.append(fitbox(X, y, BW, 56, s, size=13, fill=fill, stroke=stroke))
    for y in ys[:-1]:
        f.append(arrow(X + BW / 2, y + 56, X + BW / 2, y + 88))

    # ядро внизу
    f.append(arrow(X + BW / 2, 478, X + BW / 2, 502))
    f.append(fitbox(X, 502, BW, 44, "ЯДРО: справжній запис у файл-дескриптор 1",
                    size=13, fill=KRN_FILL, stroke=NEG))

    # праві примітки
    notes = [
        (152, "цього ядро не вміє:\nвоно приймає лише байти"),
        (242, "тут зникає більшість\nсистемних викликів"),
        (422, "повернення −9 → glibc кладе\nerrno = EBADF і віддає −1"),
    ]
    for y, s in notes:
        f.append(line(X + BW, y + 28, 588, y + 28, color=MUTED, sw=1.5, dash="5 4"))
        f.append(fitbox(596, y, 268, 56, s, size=12, fill="#fbfbfc", stroke=MUTED))

    render(os.path.join(IMG, 'printf-path.svg'), W, H, *f,
           title="Один рядок коду: що з нього робить glibc, а що — ядро")


# ── 3. Одне ядро — три простори користувача ────────────────────────────────
def fig_three_userlands():
    W, H = 900, 540
    f = []
    cw, gap, x0 = 260, 30, 30

    cols = [
        ("Debian, Fedora, Arch",
         ["glibc", "bash + coreutils", "systemd", "gcc, binutils, make"],
         "GNU/Linux", GNU_FILL, FIELD),
        ("Alpine, вбудовані збірки",
         ["musl", "busybox (одна програма)", "OpenRC", "тулчейн — окремо"],
         "Linux, але не GNU", OTH_FILL, MUTED),
        ("Android",
         ["bionic", "toybox", "init від AOSP", "clang з NDK"],
         "Linux, але не GNU", OTH_FILL, MUTED),
    ]

    for i, (head, items, verdict, fill, stroke) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(fitbox(x, 56, cw, 44, head, size=13, bold=True, fill="#ffffff"))
        for j, s in enumerate(items):
            f.append(fitbox(x, 114 + j * 56, cw, 46, s, size=13, fill=fill, stroke=stroke))
        f.append(fitbox(x, 452, cw, 48, verdict, size=14, bold=True, fill=fill, stroke=stroke))

    f.append(fitbox(x0, 350, 3 * cw + 2 * gap, 62,
                    "ЯДРО LINUX — те саме в усіх трьох", size=15,
                    fill=KRN_FILL, stroke=NEG, bold=True))
    for i in range(3):
        x = x0 + i * (cw + gap) + cw / 2
        f.append(arrow(x, 348, x, 328))
        f.append(arrow(x, 414, x, 448))

    render(os.path.join(IMG, 'three-userlands.svg'), W, H, *f,
           title="Половина, яку можна зняти й замінити")


# ── 4. Дві нитки в часі (до вставки hist-two-halves) ───────────────────────
def fig_timeline():
    rows = [
        ('G', "27.09.1983 · оголошення GNU в net.unix-wizards"),
        ('G', "20.03.1985 · GNU Emacs 13 — перший випуск"),
        ('G', "22.03.1987 · GCC — перший випуск"),
        ('W', "1987–1990 · чекання на ліцензію Mach"),
        ('G', "08.06.1989 · bash — перший випуск"),
        ('G', "1990 · початок роботи над Hurd"),
        ('L', "25.08.1991 · допис Торвальдса в comp.os.minix"),
        ('L', "17.09.1991 · Linux 0.01 на ftp.funet.fi"),
        ('G', "листопад 1991 · Hurd — офіційне ядро GNU"),
        ('L', "05.01.1992 · випуск 0.12 переходить на GPL"),
        ('L', "1994 · форк Linux libc — шов роздвоївся"),
        ('G', "січень 1997 · glibc 2.0 — шов знову один"),
        ('L', "близько 1998 · супровід Linux libc припинено"),
    ]

    W = 960
    Y0, STEP, BH = 100, 48, 38
    H = Y0 + len(rows) * STEP + 46
    LX, RX, BW = 40, 520, 400
    MID = 480

    f = []
    f.append(fitbox(LX, 46, BW, 38, "Проєкт GNU: інструменти без ядра",
                    size=14, bold=True, fill=GNU_FILL, stroke=FIELD))
    f.append(fitbox(RX, 46, BW, 38, "Linux: ядро без інструментів",
                    size=14, bold=True, fill=KRN_FILL, stroke=NEG))
    f.append(line(MID, 94, MID, Y0 + len(rows) * STEP - 4,
                  color=MUTED, sw=1.5, dash="6 6"))

    for i, (side, s) in enumerate(rows):
        y = Y0 + i * STEP
        if side == 'L':
            f.append(fitbox(RX, y, BW, BH, s, size=13, fill=KRN_FILL, stroke=NEG))
        elif side == 'W':
            f.append(fitbox(LX, y, BW, BH, s, size=13, fill="#fbfbfc", stroke=MUTED))
        else:
            f.append(fitbox(LX, y, BW, BH, s, size=13, fill=GNU_FILL, stroke=FIELD))

    f.append(text(W / 2, H - 18,
                  "Дві нитки йшли нарізно вісім років і зійшлися восени 1991-го",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'two-threads-timeline.svg'), W, H, *f,
           title="Дві нитки: чого бракувало кожній")


# ── 5. Як з теки народжується образ initramfs ──────────────────────────────
def fig_initramfs_build():
    W, H = 900, 636
    X, BW = 46, 470
    f = []

    steps = [
        ("root/ — тека-заготовка: init, dev/console,\nпорожні proc/ sys/ dev/", OTH_FILL, LINE),
        ("find . | cpio -o -H newc\nдерево тек стає одним потоком байтів", GNU_FILL, FIELD),
        ("gzip -9  →  initramfs.cpio.gz", GNU_FILL, FIELD),
        ("QEMU: -kernel vmlinuz -initrd initramfs.cpio.gz\nдва файли лягають у пам'ять поруч", OTH_FILL, MUTED),
        ("ЯДРО розпаковує архів у rootfs (ramfs/tmpfs)\nі шукає в корені файл /init", KRN_FILL, NEG),
        ("exec /init — простір користувача живий", GNU_FILL, FIELD),
    ]
    ys = [46, 144, 242, 340, 438, 536]
    for (s, fill, stroke), y in zip(steps, ys):
        f.append(fitbox(X, y, BW, 64, s, size=13, fill=fill, stroke=stroke))
    for y in ys[:-1]:
        f.append(arrow(X + BW / 2, y + 64, X + BW / 2, y + 96))

    notes = [
        (144, "магія «070701»; без -H newc\nвийде старий формат, і ядро\nархіву не впізнає"),
        (438, "нема /init → panic:\n«No working init found»"),
    ]
    for y, s in notes:
        f.append(line(X + BW, y + 32, 556, y + 32, color=MUTED, sw=1.5, dash="5 4"))
        f.append(fitbox(564, y, 300, 64, s, size=12, fill="#fbfbfc", stroke=MUTED))

    f.append(text(W / 2, 620,
                  "Ані розділу, ані файлової системи на диску: увесь корінь приїхав у пам'яті",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'minimal-initramfs-build.svg'), W, H, *f,
           title="Шлях від теки з одним файлом до працюючого PID 1")


# ── 6. Що саме ламається, коли з образу вийняти деталь ─────────────────────
def fig_what_breaks():
    W, H = 940, 628
    LX, LW = 30, 330
    RX, RW = 400, 510
    BAD = "#fdecea"
    f = []

    f.append(text(LX + LW / 2, 62, "що лежить в образі", size=14, bold=True, color=MUTED))
    f.append(text(RX + RW / 2, 62, "що каже машина", size=14, bold=True, color=MUTED))
    f.append(line(LX, 76, RX + RW, 76, color=MUTED, sw=1.2, dash="6 5"))

    rows = [
        ("порожній образ", "Kernel panic — not syncing:\nNo working init found.", False),
        ("init, що повертається з main", "Kernel panic — not syncing:\nAttempted to kill init! exitcode=0x00000000", False),
        ("init, зв'язаний динамічно", "«No such file or directory» —\nхоча файл на місці: нема /lib/ld-linux", False),
        ("нема вузла /dev/console", "«unable to open an initial console»,\nдалі — цілковита тиша", False),
        ("нема змонтованого /proc", "ps порожній, free мовчить,\n/proc/self не існує", False),
        ("init + busybox + /proc + /dev", "запрошення оболонки;\nls, mount, ps, ping працюють", True),
    ]

    for i, (left, right, ok) in enumerate(rows):
        y = 96 + i * 84
        f.append(fitbox(LX, y, LW, 66, left, size=14, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(RX, y, RW, 66, right, size=13,
                        fill=GNU_FILL if ok else BAD,
                        stroke=FIELD if ok else POS))
        f.append(arrow(LX + LW + 6, y + 33, RX - 6, y + 33, color=MUTED, sw=1.4))

    f.append(text(W / 2, 610,
                  "Кожен рядок — окремий запуск: прибрали одну деталь і подивилися, що станеться",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'minimal-what-breaks.svg'), W, H, *f,
           title="П'ять способів зламати систему і один робочий")


# ── 7. Смуги переносності ключів (до вставки api-gnu-vs-posix) ─────────────
def fig_portability_bands():
    W = 980
    LX, LW = 34, 250
    RX, RW = 302, 644
    Y0, BH, GAP = 60, 96, 14
    WARN = "#fdf3e3"
    BAD = "#fdecea"
    f = []

    bands = [
        ("POSIX\nдавній шар — скрізь",
         "grep -E -F -i -c -l -q · sed -n -e -f · find -name -type -exec\n"
         "xargs -I -n · head -n · tail -n +N · sort -n -k -t -u · cp -R -p\n"
         "лише з Issue 8 (2024): sed -E · head -c · find -print0 · xargs -0 -r",
         GNU_FILL, FIELD),
        ("не POSIX, але скрізь\nсинтаксис той самий",
         "grep -r -R · readlink -f · mktemp -d ШАБЛОН\n"
         "find -maxdepth · du -h · df -h · ls -h",
         KRN_FILL, NEG),
        ("не POSIX, скрізь,\nАЛЕ СИНТАКСИС ІНШИЙ",
         "sed -i · stat формат · date крім -u · кольори ls\n"
         "mktemp -t -p · xargs на порожньому вході",
         WARN, POS),
        ("є у двох діалектах\nіз трьох",
         "GNU і BSD, нема в busybox:  sort -h · sort -V · grep --include\n"
         "GNU і busybox, нема в BSD:  date -d · stat -c ФОРМАТ · cp --parents",
         OTH_FILL, MUTED),
        ("лише GNU",
         "grep -P · find -printf · head -n -N\n"
         "ключі ПІСЛЯ операндів: sort f -o out працює тільки тут",
         BAD, POS),
    ]

    for i, (label, body, fill, stroke) in enumerate(bands):
        y = Y0 + i * (BH + GAP)
        f.append(fitbox(LX, y, LW, BH, label, size=14, bold=True,
                        fill="#ffffff", stroke=stroke))
        f.append(fitbox(RX, y, RW, BH, body, size=13, fill=fill, stroke=stroke))

    H = Y0 + len(bands) * (BH + GAP) + 34
    f.append(text(W / 2, H - 14,
                  "Чим нижче смуга, тим менше машин зрозуміє рядок; третя смуга небезпечніша за п'яту",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'portability-bands.svg'), W, H, *f,
           title="П'ять смуг переносності повсякденних ключів")


if __name__ == '__main__':
    fig_halves()
    fig_printf_path()
    fig_three_userlands()
    fig_timeline()
    fig_initramfs_build()
    fig_what_breaks()
    fig_portability_bands()
    print("ok")
