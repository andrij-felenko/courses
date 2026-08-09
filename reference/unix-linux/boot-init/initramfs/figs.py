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
GREY_FILL = "#eceff1"


# ── 1. Дві дороги образу в пам'ять ──────────────────────────────────────────
def fig_initrd_vs_initramfs():
    W, H = 1260, 620
    p = []

    p.append(rect(40, 56, 560, 500, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(660, 56, 560, 500, fill=BG, stroke=MUTED, sw=1.2, rx=10))

    p.append(text(320, 96, "initrd — образ файлової системи", size=16, bold=True))
    p.append(text(940, 96, "initramfs — архів cpio", size=16, bold=True))

    # ліва колонка
    lx, lw = 80, 480
    p.append(fitbox(lx, 124, lw, 62, "стиснений образ у пам'яті", size=15, fill=WARM_FILL, stroke=MUTED))
    p.append(arrow(320, 186, 320, 218))
    p.append(fitbox(lx, 220, lw, 62,
                    "/dev/ram0 — блоковий пристрій\nрозмір задано ще під час збирання",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(320, 282, 320, 314))
    p.append(fitbox(lx, 316, lw, 62, "драйвер файлової системи читає блоки", size=14, fill=FILL, stroke=LINE))
    p.append(arrow(320, 378, 320, 410))
    p.append(fitbox(lx, 412, lw, 62,
                    "кеш сторінок — ті самі байти вдруге",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(text(320, 516, "пам'ять повертається лише разом з усім пристроєм", size=13, color=MUTED))

    # права колонка
    rx0, rw = 700, 480
    p.append(fitbox(rx0, 124, rw, 62, "стиснений архів у пам'яті", size=15, fill=WARM_FILL, stroke=MUTED))
    p.append(arrow(940, 186, 940, 246))
    p.append(fitbox(rx0, 248, rw, 62,
                    "розпакувальник ядра створює файли",
                    size=14, fill=FILL, stroke=LINE))
    p.append(arrow(940, 310, 940, 370))
    p.append(fitbox(rx0, 372, rw, 62,
                    "rootfs: файли в кеші сторінок — одна копія",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(text(940, 516, "видалили файл — його сторінки вільні тієї ж миті", size=13, color=MUTED))

    render(os.path.join(IMG, 'initrd-vs-initramfs.svg'), W, H, *p,
           title="initrd проти initramfs")


# ── 2. Буфер як склейка архівів ─────────────────────────────────────────────
def fig_initramfs_buffer():
    W, H = 1260, 500
    p = []

    p.append(fitbox(60, 86, 420, 92,
                    "архів 1 — без стиснення\nмікрокод процесора",
                    size=15, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(500, 86, 700, 92,
                    "архів 2 — стиснений (zstd, gzip, lz4…)\nосновний образ initramfs",
                    size=15, fill=BLUE_FILL, stroke=NEG))

    p.append(text(630, 216, "розпакувальник іде буфером уперед і рівно один раз", size=14, color=MUTED))

    p.append(text(630, 268, "розкладка одного запису", size=15, bold=True))

    zy, zh = 292, 78
    p.append(fitbox(170, zy, 90, zh, "ALGN\n(4)", size=13, fill=GREY_FILL, stroke=MUTED))
    p.append(fitbox(260, zy, 330, zh,
                    "шапка, 110 байтів ASCII\n070701 · режим · розмір · довжина імені",
                    size=13, fill=FILL, stroke=LINE))
    p.append(fitbox(590, zy, 190, zh, "ім'я + '\\0'", size=13, fill=FILL, stroke=LINE))
    p.append(fitbox(780, zy, 90, zh, "ALGN\n(4)", size=13, fill=GREY_FILL, stroke=MUTED))
    p.append(fitbox(870, zy, 220, zh, "дані файлу", size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(630, 424,
                  "запис з іменем TRAILER!!! завершує архів — стан скинуто, читаємо наступний",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'initramfs-buffer.svg'), W, H, *p,
           title="буфер initramfs")


# ── 3. Перехід у справжній корінь ───────────────────────────────────────────
def fig_switch_root_steps():
    W, H = 1300, 660
    p = []

    p.append(rect(40, 56, 560, 452, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(660, 56, 560, 452, fill=BG, stroke=MUTED, sw=1.2, rx=10))

    p.append(text(320, 94, "до переходу", size=16, bold=True))
    p.append(text(940, 94, "після переходу", size=16, bold=True))

    # ── ліва панель ──
    p.append(fitbox(90, 118, 440, 58,
                    "rootfs — кореневе монтування «/»",
                    size=15, fill=WARM_FILL, stroke=MUTED))
    p.append(line(150, 176, 150, 356, color=MUTED))
    p.append(line(150, 232, 216, 232, color=MUTED))
    p.append(fitbox(216, 204, 314, 58,
                    "/sysroot\nсправжня файлова система",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(line(150, 326, 216, 326, color=MUTED))
    p.append(fitbox(216, 298, 314, 58,
                    "/dev · /proc · /sys",
                    size=13, fill=FILL, stroke=LINE))
    p.append(text(320, 430, "тимчасовий корінь тримає все дерево", size=13, color=MUTED))

    # ── права панель ──
    p.append(fitbox(710, 118, 440, 54,
                    "справжня ФС — видимий корінь «/»",
                    size=15, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(710, 182, 440, 46,
                    "rootfs — порожній, лишається основою",
                    size=13, fill=GREY_FILL, stroke=MUTED))
    p.append(line(770, 228, 770, 326, color=MUTED))
    p.append(line(770, 296, 836, 296, color=MUTED))
    p.append(fitbox(836, 268, 314, 58,
                    "/dev · /proc · /sys\nперенесені, не підняті заново",
                    size=13, fill=FILL, stroke=LINE))
    p.append(text(940, 430, "файли rootfs видалено — пам'ять повернено", size=13, color=MUTED))

    # ── смуга кроків ──
    sy, sh, sw_ = 552, 66, 290
    steps = [
        "1 · видалити вміст rootfs",
        "2 · перенести службові\nмонтування",
        "3 · перенести новий корінь\nна «/»",
        "4 · chroot і exec /sbin/init",
    ]
    for i, s in enumerate(steps):
        p.append(fitbox(40 + i * (sw_ + 20), sy, sw_, sh, s, size=13, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'switch-root-steps.svg'), W, H, *p,
           title="switch_root")


# ── 4. Чотири кроки збирання і пастка на кожному ────────────────────────────
def fig_build_pipeline():
    W, H = 1400, 430
    p = []

    cols = [40, 380, 720, 1060]
    bw = 300

    heads = ["1 · зібрати", "2 · скласти дерево", "3 · запакувати", "4 · запустити"]
    cmds = [
        "cc -static -O2 -o root/init init.c\nchmod +x root/init",
        "root/proc  root/sys  root/dev\nnod /dev/console  c 5 1\n(gen_init_cpio або з-під root)",
        "cd root\nfind . | cpio -o -H newc | zstd\n> ../initramfs.cpio.zst",
        "qemu-system-x86_64 -kernel bzImage\n-initrd initramfs.cpio.zst\n-append \"console=ttyS0\"",
    ]
    traps = [
        "лишили динамічне лінкування:\nFailed to execute /init (error -2)\n— бракує не /init, а ld-linux.so",
        "немає вузла /dev/console:\nWarning: unable to open an\ninitial console — і далі жодного\nрядка від нашого /init",
        "пакували з батьківської теки:\nусі імена стали root/… ,\n/init у образі просто немає",
        "забули console=ttyS0:\nядро пише у віртуальний екран,\nа термінал мовчить",
    ]

    for i, x in enumerate(cols):
        p.append(text(x + bw / 2, 56, heads[i], size=15, bold=True))
        p.append(fitbox(x, 72, bw, 110, cmds[i], size=13, fill=BLUE_FILL, stroke=NEG))
        p.append(fitbox(x, 232, bw, 130, traps[i], size=13, fill=RED_FILL, stroke=POS))
        if i < 3:
            p.append(arrow(x + bw + 4, 127, x + bw + 34, 127))

    p.append(text(700, 214, "…і як саме воно ламається", size=14, color=MUTED))
    p.append(text(700, 400,
                  "усі чотири помилки виглядають майже однаково — машина мовчить або панікує; "
                  "розрізняє їх лише останній рядок ядра",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'build-pipeline.svg'), W, H, *p,
           title="чотири кроки збирання initramfs і пастка на кожному")


if __name__ == '__main__':
    fig_initrd_vs_initramfs()
    fig_initramfs_buffer()
    fig_switch_root_steps()
    fig_build_pipeline()
    print("ok")
