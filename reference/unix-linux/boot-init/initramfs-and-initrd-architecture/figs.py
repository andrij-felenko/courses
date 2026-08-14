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


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Порівняння архітектури initrd та initramfs ──────────────────────────
def fig_initrd_vs_initramfs_arch():
    W, H = 1240, 580
    p = []

    lx, rx, pw, py, ph = 40, 650, 550, 70, 460
    p.append(rect(lx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(rx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(text(lx + pw / 2, 104, "Класичний initrd (RAM Disk)", size=16, bold=True, color=POS))
    p.append(text(rx + pw / 2, 104, "Сучасний initramfs (rootfs / cpio)", size=16, bold=True, color=FIELD))

    # Ліва частина (initrd)
    p.append(fitbox(lx + 40, 136, 470, 54, "Образ ext2 / minix у пам'яті (ramdisk_size)", size=13, fill=RED_FILL, stroke=POS))
    p.append(arrow(lx + pw / 2, 190, lx + pw / 2, 220))
    p.append(fitbox(lx + 40, 220, 470, 54, "Блоковий драйвер /dev/ram0 + Buffer Cache", size=13, fill=WARM_FILL))
    p.append(arrow(lx + pw / 2, 274, lx + pw / 2, 304))
    p.append(fitbox(lx + 40, 304, 470, 54, "Драйвер ФС ext2 / vfs Page Cache", size=13, fill=WARM_FILL))
    p.append(arrow(lx + pw / 2, 358, lx + pw / 2, 388))
    p.append(fitbox(lx + 40, 388, 470, 54, "Виконання /linuxrc (pivot_root)", size=14, bold=True, fill=GREY_FILL))

    p.append(text(lx + pw / 2, 470, "Потрійне дублювання кшу + фіксований розмір", size=12, color=POS, bold=True))
    p.append(text(lx + pw / 2, 494, "Потрібні вбудовані драйвери блокового рівня та ext2", size=12, color=MUTED))

    # Права частина (initramfs)
    p.append(fitbox(rx + 40, 136, 470, 54, "Архів cpio (потоковий стиснений файл)", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(rx + pw / 2, 190, rx + pw / 2, 220))
    p.append(fitbox(rx + 40, 220, 470, 54, "Ядерний розпаковувач unpack_to_rootfs()", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(rx + pw / 2, 274, rx + pw / 2, 304))
    p.append(fitbox(rx + 40, 304, 470, 54, "rootfs / tmpfs (Прямо у VFS Page Cache)", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(rx + pw / 2, 358, rx + pw / 2, 388))
    p.append(fitbox(rx + 40, 388, 470, 54, "Виконання /init (switch_root)", size=14, bold=True, fill=BLUE_FILL))

    p.append(text(rx + pw / 2, 470, "Динамічна пам'ять, нуль блокового оверхеду", size=12, color=FIELD, bold=True))
    p.append(text(rx + pw / 2, 494, "Миттєве звільнення OAM при видаленні файлів", size=12, color=MUTED))

    render(os.path.join(IMG, 'initrd-vs-initramfs-arch.svg'), W, H, *p)


# ── 2. Структура кадру архіву cpio newc ────────────────────────────────────
def fig_cpio_newc_structure():
    W, H = 1240, 480
    p = []

    p.append(text(W / 2, 50, "Структурна анатомія кадру cpio newc (SVR4 Portable Format)", size=16, bold=True))

    y0, h0 = 90, 90
    # Кадр cpio
    p.append(fitbox(40, y0, 340, h0, "ASCII Header (110 байтів)\nMagic: '070701'\nino, mode, uid, gid, filesize...", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(380, y0, 280, h0, "Ім'я файлу (namesize)\nнаприклад: 'init' або 'bin/sh'\n+ NUL-символ", size=13, fill=WARM_FILL))
    p.append(fitbox(660, y0, 160, h0, "Падінг ім'я\n(0-3 байти)", size=12, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(820, y0, 260, h0, "Дані файлу (filesize)\nбінарне навантаження", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(1080, y0, 120, h0, "Падінг дані\n(0-3 байти)", size=12, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    # Лінія вирівнювання
    y1 = 230
    p.append(line(40, y1, 1200, y1, color=FIELD, sw=1.5, dash="4 4"))
    p.append(text(W / 2, y1 - 10, "Усі частини вирівнюються за межею 4 байтів: (offset % 4 == 0)", size=12, color=FIELD, bold=True))

    # Спеціальні випадки
    p.append(fitbox(40, 270, 560, 140,
                    "Маркер кінця архіву (TRAILER!!!):\n"
                    "• namesize = 11 ('TRAILER!!!\\0')\n"
                    "• filesize = 0\n"
                    "• Вказує ядерному парсеру зупинити витягування поточного cpio",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(640, 270, 560, 140,
                    "Типи файлів (c_mode & 0170000):\n"
                    "• 0100000 (S_IFREG): Звичайний файл\n"
                    "• 0040000 (S_IFDIR): Каталог\n"
                    "• 0120000 (S_IFLNK): Символьне посилання\n"
                    "• 0020000 (S_IFCHR) / 0060000 (S_IFBLK): Пристрої",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'cpio-newc-structure.svg'), W, H, *p)


# ── 3. Склеєний initramfs та ранній мікрокод ────────────────────────────────
def fig_concatenated_initramfs_boot():
    W, H = 1240, 480
    p = []

    p.append(text(W / 2, 50, "Багатокомпонентний склеєний initramfs у пам'яті", size=16, bold=True))

    y0, h0 = 100, 110
    p.append(fitbox(40, y0, 480, h0,
                    "Сегмент 1: Ранній мікрокод CPU\n"
                    "Незжиманий cpio архів\n"
                    "Файл: kernel/x86/microcode/GenuineIntel.bin",
                    size=13, fill=WARM_FILL, stroke=POS))

    p.append(fitbox(520, y0, 100, h0, "Падінг 512B\n(нулі)", size=12, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(fitbox(620, y0, 580, h0,
                    "Сегмент 2: Основний initramfs\n"
                    "Стиснений cpio (zstd / gzip / xz)\n"
                    "Повний ранній простір користувача (/init, udev, drivers)",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    # Стрілки парсингу
    y1 = 250
    p.append(text(W / 2, y1, "Послідовність розпакування ядром Linux (unpack_to_rootfs):", size=14, bold=True))

    p.append(fitbox(40, 280, 360, 120,
                    "1. Сканування без декомпресора\n"
                    "Ядро зчитує мікрокод ДО\n"
                    "ініціалізації менеджерів пам'яті",
                    size=12, fill=WARM_FILL))

    p.append(arrow(410, 340, 440, 340))

    p.append(fitbox(450, 280, 340, 120,
                    "2. Виявлення TRAILER!!!\n"
                    "Завершення першого cpio,\n"
                    "пропуск вирівнювальних нулів",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(arrow(800, 340, 830, 340))

    p.append(fitbox(840, 280, 360, 120,
                    "3. Визначення сигнатури стиснення\n"
                    "Автовиявлення (0x28B52FFD zstd)\n"
                    "та розпакування в rootfs",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'concatenated-initramfs-boot.svg'), W, H, *p)


# ── 4. Послідовність виконання switch_root ──────────────────────────────────
def fig_switch_root_execution():
    W, H = 1240, 540
    p = []

    p.append(text(W / 2, 45, "Анатомія виклику switch_root: передача управління PID 1", size=16, bold=True))

    step_w, step_h = 270, 380
    gap = 25
    x_start = 40

    steps = [
        ("Етап 1: Очищення",
         "1. Рекурсивне видалення\nусіх файлів у rootfs\n(unlink / rmdir).\n\n"
         "Звільнення всієї пам'яті RAM, зайнятої у initramfs.",
         WARM_FILL, POS),
        ("Етап 2: Перенесення",
         "2. Перенесення точок монтування:\n"
         "mount(\"/sysroot\", \"/\",\n      NULL, MS_MOVE, NULL)\n\n"
         "Монтування справжнього кореня поверх rootfs.",
         BLUE_FILL, NEG),
        ("Етап 3: Фіксація",
         "3. Зміна кореневої теки:\n"
         "chroot(\".\")\n"
         "chdir(\"/\")\n\n"
         "Процес переходить у новий корінь на диску.",
         GREEN_FILL, FIELD),
        ("Етап 4: Заміна PID 1",
         "4. Перенаправлення stdio\nна /dev/console.\n"
         "execve(\"/sbin/init\", ...)\n\n"
         "Підміна образу PID 1 на справжній systemd.",
         GREEN_FILL, FIELD)
    ]

    for i, (title, desc, fill, stroke) in enumerate(steps):
        cx = x_start + i * (step_w + gap)
        p.append(rect(cx, 80, step_w, step_h, fill=fill, stroke=stroke, sw=1.4, rx=8))
        p.append(text(cx + step_w / 2, 115, title, size=15, bold=True))
        p.append(line(cx + 15, 135, cx + step_w - 15, 135, color=MUTED, sw=1.2))
        p.append(fitbox(cx + 15, 150, step_w - 30, step_h - 90, desc, size=13, fill="#ffffff", stroke=MUTED, sw=1.0))

        if i < 3:
            arrow_x = cx + step_w + 3
            p.append(arrow(arrow_x, 270, arrow_x + gap - 6, 270, color=FIELD))

    p.append(text(W / 2, 490, "Номер процесу PID 1 НЕ змінюється протягом усіх 4 етапів", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'switch-root-execution.svg'), W, H, *p)


fig_initrd_vs_initramfs_arch()
fig_cpio_newc_structure()
fig_concatenated_initramfs_boot()
fig_switch_root_execution()
print("ok")
