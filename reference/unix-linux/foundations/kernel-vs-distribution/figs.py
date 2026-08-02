# -*- coding: utf-8 -*-
"""Фігури до теми «Ядро, дистрибутив і що між ними»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Шари й дві межі ──────────────────────────────────────────────────────
def fig_layers():
    W, H = 940, 560
    LX, LW = 50, 500          # колонка шарів
    AX, AW = 580, 330         # колонка приміток
    f = []

    # верхні два шари — простір користувача
    f.append(fitbox(LX, 55, LW, 62,
                    "Програми: оболонка, служби, застосунки",
                    size=15, bold=True))
    f.append(fitbox(AX, 58, AW, 56,
                    "обирає й супроводжує\nдистрибутив", size=13, color=MUTED,
                    fill=BG, stroke=MUTED, sw=1.0))

    f.append(fitbox(LX, 129, LW, 70,
                    "Бібліотеки простору користувача:\nlibc (glibc / musl / bionic) та інші .so",
                    size=14))
    f.append(fitbox(AX, 134, AW, 60,
                    "базова лінія ABI —\nвибір дистрибутива", size=13, color=MUTED,
                    fill=BG, stroke=MUTED, sw=1.0))

    # межа системних викликів
    f.append(line(LX, 214, LX + LW, 214, color=POS, sw=2.5, dash="9,6"))
    f.append(text(LX + LW / 2, 246,
                  "МЕЖА ABI СИСТЕМНИХ ВИКЛИКІВ — заморожена назавжди",
                  size=13, color=POS, bold=True))

    # ядро
    f.append(rect(LX, 265, LW, 200, fill=BG, stroke=LINE, sw=2.0))
    f.append(fitbox(LX + 16, 278, LW - 32, 56,
                    "Ядро: планувальник, пам'ять, VFS, стек мережі",
                    size=15, bold=True))
    f.append(line(LX + 16, 352, LX + LW - 16, 352, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(LX + LW / 2, 382,
                  "внутрішній API ядра — змінюється щоверсії",
                  size=12, color=MUTED))
    f.append(fitbox(LX + 16, 395, LW - 32, 56,
                    "Модулі й драйвери", size=15, bold=True))
    f.append(fitbox(AX, 278, AW, 56,
                    "спільне для всіх —\nдоговір не змінюється", size=13, color=MUTED,
                    fill=BG, stroke=MUTED, sw=1.0))
    f.append(fitbox(AX, 395, AW, 56,
                    "зібрані під конкретну\nверсію ядра", size=13, color=MUTED,
                    fill=BG, stroke=MUTED, sw=1.0))

    f.append(fitbox(LX, 490, LW, 52, "Залізо", size=15))

    render(os.path.join(IMG, 'layers.svg'), W, H, *f,
           title="Шари системи і дві межі між ними")


# ── 2. Несиметрія сумісности glibc ──────────────────────────────────────────
def fig_glibc():
    W, H = 870, 345
    f = []

    def row(y, built, host, ok, verdict):
        col = FIELD if ok else POS
        out = [fitbox(40, y, 250, 80, built, size=14),
               arrow(302, y + 40, 380, y + 40),
               fitbox(392, y, 230, 80, host, size=14),
               fitbox(650, y, 180, 80, verdict, size=15, bold=True,
                      color=col, stroke=col, fill=BG, sw=2.0)]
        return out

    f += row(60, "Бінарник зібрано\nна glibc 2.28", "Система\nз glibc 2.35",
             True, "працює")
    f.append(text(435, 168,
                  "усі мітки версій, які просить бінарник, у новій бібліотеці збережено",
                  size=13, color=MUTED))

    f += row(200, "Бінарник зібрано\nна glibc 2.35", "Система\nз glibc 2.28",
             False, "не працює")
    f.append(text(435, 308,
                  "version `GLIBC_2.34' not found — такої мітки в старій бібліотеці немає",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'glibc-versions.svg'), W, H, *f,
           title="Сумісність glibc працює лише в один бік")


# ── 3. Що обирає дистрибутив ────────────────────────────────────────────────
def fig_distro():
    W, H = 940, 460
    X0, LW, CW = 30, 220, 165
    cols = ["Debian", "Fedora", "Alpine", "Arch"]
    f = []

    def cx(i):
        return X0 + LW + i * CW

    # шапка
    for i, c in enumerate(cols):
        f.append(fitbox(cx(i), 52, CW, 48, c, size=15, bold=True, fill=FILL))

    rows = [
        (100, 54, "libc", ["glibc", "glibc", "musl", "glibc"], 13),
        (154, 54, "базові утиліти",
         ["GNU coreutils", "GNU coreutils", "BusyBox", "GNU coreutils"], 12),
        (208, 54, "PID 1 і служби",
         ["systemd", "systemd", "BusyBox init\n+ OpenRC", "systemd"], 12),
        (262, 54, "пакунки", ["dpkg / apt", "rpm / dnf", "apk", "pacman"], 13),
        (316, 64, "модель випусків",
         ["стабільні,\n~кожні 2 роки", "кожні ~6 міс.,\nпідтримка 13 міс.",
          "~кожні 6 міс.,\nпідтримка 2 роки", "безперервна"], 12),
    ]
    for y, h, label, cells, sz in rows:
        f.append(fitbox(X0, y, LW, h, label, size=13, bold=True, fill=FILL))
        for i, c in enumerate(cells):
            f.append(fitbox(cx(i), y, CW, h, c, size=sz, fill=BG))

    f.append(fitbox(X0, 392, LW + 4 * CW, 50,
                    "ядро в усіх — Linux; у кожного свій конфіг, свої патчі, свій набір модулів",
                    size=13, color=MUTED, fill=FILL))

    render(os.path.join(IMG, 'distro-choices.svg'), W, H, *f,
           title="Що саме обирає дистрибутив")


# ── 4. Хронологія 1991–1995 ─────────────────────────────────────────────────
def fig_timeline():
    W, H = 960, 620
    AX = 268                 # вісь часу
    DX, DW = 34, 200         # колонка дат
    EX, EW = 316, 610        # колонка подій
    f = []

    events = [
        ("17 вересня 1991", "ядро 0.01: збирається лише крос-компіляцією з-під Minix"),
        ("16 січня 1992", "ядро 0.12 виходить під GPL — постачати за гроші стало можна"),
        ("початок 1992", "дискети boot/root Г. Дж. Лу: система запускається, але не встановлюється"),
        ("лютий 1992", "MCC Interim Linux 0.12: перший інсталятор на голу машину"),
        ("травень 1992", "SLS: перший повний набір — ядро, GNU, X Window"),
        ("16 липня 1993", "Slackware 1.00: полагоджений набір, 24 дискети, серії A і X"),
        ("16 серпня 1993", "оголошення Debian: предметом роботи стає сама інтеграція"),
        ("1994 – листопад 1995", "dpkg із полями залежностей; іменований супровідник на кожен пакунок"),
    ]

    y0, step = 66, 66
    f.append(line(AX, y0 - 6, AX, y0 + (len(events) - 1) * step + 6,
                  color=MUTED, sw=2.0))

    for i, (d, e) in enumerate(events):
        cy = y0 + i * step
        f.append(text(DX + DW, cy + 5, d, size=13, anchor="end", bold=True, color=MUTED))
        f.append(circle(AX, cy, 7, fill=BG, stroke=POS, sw=2.5))
        f.append(fitbox(EX, cy - 23, EW, 46, e, size=13, fill=BG))

    render(os.path.join(IMG, 'distro-timeline.svg'), W, H, *f,
           title="Як роль дистрибутива наростала: 1991 – 1995")


# ── 5. Чия це робота ────────────────────────────────────────────────────────
def fig_whose_work():
    W, H = 980, 470
    X0, LW, CW = 26, 230, 178
    cols = ["1991\nядро 0.01", "1992\nMCC, SLS", "1993\nSlackware",
            "1994–95\nDebian"]
    f = []

    def cx(i):
        return X0 + LW + i * CW

    for i, c in enumerate(cols):
        f.append(fitbox(cx(i), 50, CW, 56, c, size=14, bold=True, fill=FILL))

    rows = [
        (110, 62, "зібрати ядро",
         ["крос-збірка\nз-під Minix", "уже зібране", "уже зібране",
          "уже зібране,\nокремий пакунок"]),
        (174, 62, "дістати програми",
         ["вручну\nз кількох FTP", "готовий набір\nна дискетах", "серії A і X",
          "репозиторій"]),
        (238, 62, "розмітити диск\nі поставити систему",
         ["hex-редактор\nMBR", "меню-інсталятор", "інсталятор\nіз дискети",
          "інсталятор\n+ базова система"]),
        (302, 62, "узгодити версії",
         ["сам", "сам", "упорядник\nнабору", "поля залежностей\nу пакунку"]),
        (366, 62, "оновити частину",
         ["переставити все", "переставити все", "переставити все",
          "поставити\nновий пакунок"]),
    ]
    for y, h, label, cells in rows:
        f.append(fitbox(X0, y, LW, h, label, size=13, bold=True, fill=FILL))
        for i, c in enumerate(cells):
            col = POS if c in ("сам", "переставити все") else INK
            f.append(fitbox(cx(i), y, CW, h, c, size=12, fill=BG, color=col))

    render(os.path.join(IMG, 'distro-whose-work.svg'), W, H, *f,
           title="Що щоразу переставало бути роботою користувача")


# ── Ланцюг збирання найменшої «системи» (вставка proj-min-userland) ─────────
def fig_min_pipeline():
    W, H = 1220, 315
    BW, BH, BY = 180, 100, 70
    xs = [30, 350, 670, 990]
    f = []

    boxes = [
        "init.c\nжодного #include,\nп'ять syscall-ів",
        "init\nстатичний ELF\n≈9 КБ",
        "initramfs.cpio.gz\ncpio newc + gzip",
        "ядро в QEMU\nрозпаковує архів\nі виконує /init",
    ]
    for x, s in zip(xs, boxes):
        f.append(fitbox(x, BY, BW, BH, s, size=13))

    labels = [
        ("gcc -static -nostdlib", "-nostartfiles"),
        ("cpio -o -H newc", "| gzip -9"),
        ("qemu-system-x86_64", "-kernel … -initrd …"),
    ]
    for i, (l1, l2) in enumerate(labels):
        cxm = (xs[i] + BW + xs[i + 1]) / 2
        f.append(arrow(xs[i] + BW + 6, BY + BH / 2, xs[i + 1] - 4, BY + BH / 2))
        f.append(text(cxm, BY + BH / 2 + 31, l1, size=11, color=MUTED))
        f.append(text(cxm, BY + BH / 2 + 48, l2, size=11, color=MUTED))

    f.append(fitbox(30, 228, 1140, 58,
                    "Єдине, що цей файл просить у системи, — заморожений ABI системних викликів",
                    size=14, fill=FILL))

    render(os.path.join(IMG, 'min-userland-pipeline.svg'), W, H, *f,
           title="Від одного .c до працюючої «системи»")


# ── Як ядро шукає init і до якої паніки веде кожна невдача ──────────────────
def fig_init_search():
    W, H = 1030, 700
    SX, SW = 120, 520          # спина
    RX, RW = 680, 310          # права колонка приміток
    f = []

    def spine(y, h, s, **kw):
        f.append(fitbox(SX, y, SW, h, s, size=13, **kw))

    def note(y, h, s, **kw):
        f.append(fitbox(RX, y, RW, h, s, size=12, **kw))

    spine(56, 58, "initramfs розпаковано в rootfs;\n/dev/console відкрито як 0, 1, 2")
    f.append(arrow(SX + SW / 2, 118, SX + SW / 2, 140))

    spine(144, 58, "чи існує /init?   (init_eaccess)")
    f.append(arrow(SX + SW + 4, 173, RX - 4, 173))
    note(130, 86,
         "немає → prepare_namespace():\nмонтувати корінь із root=\npanic: «Unable to mount root fs»",
         color=POS, stroke=POS, sw=2.0, fill=BG)

    f.append(arrow(SX + SW / 2, 202, SX + SW / 2, 258))
    spine(262, 58, "execve(\"/init\")")
    f.append(arrow(SX + SW + 4, 291, RX - 4, 291))
    note(253, 76, "успіх → /init стає PID 1,\nядро більше нічого не запускає",
         color=FIELD, stroke=FIELD, sw=2.0, fill=BG)

    f.append(arrow(SX + SW / 2, 320, SX + SW / 2, 376))
    spine(380, 58, "невдача → «Failed to execute /init (error −N)»")
    f.append(arrow(SX + SW + 4, 409, RX - 4, 409))
    note(371, 76,
         "−2 (ENOENT): бінарник динамічний,\nа завантажувача в архіві немає\n−13 (EACCES): забули chmod +x")

    f.append(arrow(SX + SW / 2, 438, SX + SW / 2, 464))
    spine(468, 76, "по черзі: /sbin/init → /etc/init →\n/bin/init → /bin/sh")

    f.append(arrow(SX + SW / 2, 544, SX + SW / 2, 588))
    spine(592, 70, "panic: «No working init found.\nTry passing init= option to kernel.»",
          color=POS, stroke=POS, sw=2.0, fill=BG, bold=True)

    render(os.path.join(IMG, 'init-search.svg'), W, H, *f,
           title="Дві різні паніки: не знайдено кореня і не вдалося виконати init")


if __name__ == '__main__':
    fig_layers()
    fig_glibc()
    fig_distro()
    fig_timeline()
    fig_whose_work()
    fig_min_pipeline()
    fig_init_search()
    print("ok")
