# -*- coding: utf-8 -*-
import sys, os

# Path to scripts for svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Шість опорних підсистем дистрибутива ──────────────────────────────
def fig_distro_architecture_layers():
    W, H = 940, 560
    p = []

    # Заголовок полотна
    p.append(fitbox(20, 20, W - 40, 36, "Шість опорних підсистем будь-якого Unix/Linux дистрибутива",
                    size=16, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    cards = [
        (40.0, 80.0, 260.0, 200.0, "1. Ядро (Kernel)",
         ["• Версія ядра та архітектура (ABI)",
          "• Системні виклики (syscalls)",
          "• Драйвери та пам'ять",
          "• Псевдофайлові системи (/proc, /sys)",
          "• Конфігурація під час завантаження"],
         "#eaf0fd", NEG),

        (340.0, 80.0, 260.0, 200.0, "2. Бібліотека C (libc)",
         ["• Шлюз до системних викликів",
          "• glibc vs musl vs uClibc vs Bionic",
          "• Алокатор пам'яті (malloc)",
          "• Реалізація потоків (pthreads)",
          "• Розв'язання імен та NSS"],
         "#eef7f0", FIELD),

        (640.0, 80.0, 260.0, 200.0, "3. Динамічний лінкер",
         ["• Шлях у заголовку ELF (PT_INTERP)",
          "• ld-linux.so vs ld-musl.so",
          "• Пошук і завантаження .so бібліотек",
          "• Таблиці GOT/PLT та символи",
          "• Сумісність двійкового коду"],
         "#fdf0dc", "#e08a1e"),

        (40.0, 310.0, 260.0, 190.0, "4. Процес 1 (Init / PID 1)",
         ["• Корінь дерева процесів",
          "• systemd, OpenRC, runit, SysV, s6",
          "• Прибирання зомбі-процесів",
          "• Життєвий цикл служб і демонів",
          "• Збирання журналів (journald / syslog)"],
         "#fdecea", POS),

        (340.0, 310.0, 260.0, 190.0, "5. Пакетний менеджер",
         ["• База даних встановлених програм",
          "• deb, rpm, apk, pacman, xbps",
          "• Декларативні сховища (Nix, Guix)",
          "• Розв'язання залежностей",
          "• Модель оновлення та цілісність"],
         "#f3e8fd", "#8e44ad"),

        (640.0, 310.0, 260.0, 190.0, "6. Ієрархія ФС та Утиліти",
         ["• Стандарт FHS та UsrMerge (/usr/bin)",
          "• Традиційні vs безстатусні (/etc vs /usr/etc)",
          "• Набір утиліт: GNU coreutils vs BusyBox",
          "• Типова оболонка (/bin/sh -> bash/dash/ash)",
          "• Змінні середовища та конфігурація"],
         "#e8f8f5", "#16a085"),
    ]

    for x, y, w, h, title, items, fill_col, border_col in cards:
        p.append(rect(x, y, w, h, fill="#ffffff", stroke=border_col, sw=1.8, rx=8))
        p.append(fitbox(x + 10, y + 10, w - 20, 28, title, size=13, bold=True,
                        fill=fill_col, stroke=border_col, color=INK))
        iy = y + 48
        for it in items:
            p.append(text(x + 16, iy, it, size=11, color=INK, anchor="start"))
            iy += 26

    # Підсумок унизу
    p.append(fitbox(20, 514, W - 40, 32,
                    "Дистрибутив — це не одна назва, а контракт між шістьма конкретними підсистемами",
                    size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "distro-architecture-layers.svg"), W, H, *p,
           title="Шість опорних підсистем дистрибутива")


# ── Фіг. 2: Механізм PT_INTERP та виклик динамічного лінкера ─────────────────
def fig_elf_pt_interp_resolution():
    W, H = 940, 520
    p = []

    p.append(fitbox(20, 16, W - 40, 34, "Чому бінарник не запускається: перевірка PT_INTERP у ядрі",
                    size=15, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    # Ліва колонка: виконуваний файл ELF
    p.append(rect(40, 70, 250, 410, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=8))
    p.append(fitbox(55, 85, 220, 30, "Двійковий файл ELF (./app)", size=13, bold=True,
                    fill="#eaf0fd", stroke=NEG, color=INK))
    p.append(rect(55, 128, 220, 42, fill="#ffffff", stroke="#cdd6e0", sw=1.2, rx=4))
    p.append(text(165, 154, "ELF Header (e_ident, arch)", size=11.5, color=INK))

    p.append(rect(55, 180, 220, 110, fill="#fff6e6", stroke="#e08a1e", sw=1.6, rx=4))
    p.append(text(165, 204, "Program Header Table", size=12, bold=True, color="#e08a1e"))
    p.append(rect(65, 216, 200, 64, fill="#ffffff", stroke="#e08a1e", sw=1.2, rx=4))
    p.append(text(165, 238, "Сегмент PT_INTERP:", size=11, bold=True, color=INK))
    p.append(text(165, 260, "\"/lib64/ld-linux-x86-64.so.2\"", size=10.5, color=POS))

    p.append(rect(55, 300, 220, 55, fill="#ffffff", stroke="#cdd6e0", sw=1.2, rx=4))
    p.append(text(165, 324, "Сегменти коду (PT_LOAD)", size=11.5, color=INK))
    p.append(text(165, 342, ".text, .rodata", size=10, color=MUTED))

    p.append(rect(55, 365, 220, 100, fill="#ffffff", stroke="#cdd6e0", sw=1.2, rx=4))
    p.append(text(165, 388, "Динамічна секція (PT_DYNAMIC)", size=11.5, color=INK))
    p.append(text(165, 410, "DT_NEEDED: libc.so.6", size=10.5, color=MUTED))
    p.append(text(165, 430, "DT_NEEDED: libm.so.6", size=10.5, color=MUTED))
    p.append(text(165, 450, "Символи та релокації", size=10, color=MUTED))

    # Центральна колонка: Дії ядра при виклику execve()
    p.append(rect(330, 70, 280, 410, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=8))
    p.append(fitbox(345, 85, 250, 30, "Ядро Linux (sys_execve)", size=13, bold=True,
                    fill="#eef7f0", stroke=FIELD, color=INK))

    ksteps = [
        (130, "1. Зчитування ELF заголовка\nі таблиці сегментів"),
        (190, "2. Виявлення PT_INTERP:\nпошук інтерпретатора на ФС"),
        (260, "3. Перевірка наявності шляху\nу кореневій файловій системі"),
        (335, "4. Якщо шлях відсутній:\nнегайне повернення ENOENT"),
        (405, "5. Якщо шлях є: мапування\nлінкера та передача керування"),
    ]
    for ky, ktxt in ksteps:
        p.append(fitbox(345, ky, 250, 50, ktxt, size=11, bold=False,
                        fill="#ffffff", stroke="#cdd6e0", color=INK))

    # Стрілки від ELF до ядра
    p.append(arrow(275, 248, 345, 215, color="#e08a1e", sw=1.8))

    # Права колонка: Результати на цільовій системі
    p.append(rect(650, 70, 250, 195, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(fitbox(665, 85, 220, 28, "Alpine Linux (musl)", size=12.5, bold=True,
                    fill="#ffffff", stroke=POS, color=POS))
    p.append(text(775, 130, "Шлях у файловій системі:", size=11, color=INK))
    p.append(text(775, 150, "/lib/ld-musl-x86_64.so.1", size=10.5, bold=True, color=FIELD))
    p.append(text(775, 175, "Помилка ядра: ENOENT (-2)", size=11.5, bold=True, color=POS))
    p.append(rect(665, 195, 220, 55, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(775, 216, "bash: ./app:", size=10.5, color=POS))
    p.append(text(775, 236, "No such file or directory", size=11, bold=True, color=POS))

    p.append(rect(650, 285, 250, 195, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    p.append(fitbox(665, 300, 220, 28, "Ubuntu / Debian (glibc)", size=12.5, bold=True,
                    fill="#ffffff", stroke=FIELD, color=FIELD))
    p.append(text(775, 345, "Шлях у файловій системі:", size=11, color=INK))
    p.append(text(775, 365, "/lib64/ld-linux-x86-64.so.2", size=10.5, bold=True, color=FIELD))
    p.append(text(775, 395, "Лінкер знайдено успішно", size=11.5, bold=True, color=FIELD))
    p.append(rect(665, 415, 220, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(775, 436, "Завантаження бібліотек", size=10.5, color=FIELD))
    p.append(text(775, 452, "і запуск main()", size=10.5, bold=True, color=FIELD))

    # Стрілки від ядра до правої колонки
    p.append(arrow(595, 360, 650, 220, color=POS, sw=1.8))
    p.append(arrow(595, 430, 650, 420, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "elf-pt-interp-resolution.svg"), W, H, *p,
           title="Механізм розпізнавання PT_INTERP ядром")


# ── Фіг. 3: Послідовний алгоритм обстеження дистрибутива ──────────────────────
def fig_distro_triage_flowchart():
    W, H = 940, 580
    p = []

    p.append(fitbox(20, 16, W - 40, 34, "Послідовний протокол обстеження невідомого оточення",
                    size=15, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    steps = [
        (40.0, 70.0, 410.0, 68.0, "Крок 1. Метадані та версія ядра",
         "cat /etc/os-release  ||  uname -mrs  ||  cat /proc/version\n-> Визначає назву дистрибутива, версію ядра та архітектуру ЦП",
         "#eaf0fd", NEG),

        (490.0, 70.0, 410.0, 68.0, "Крок 2. Хто керує системою (PID 1)",
         "readlink -f /proc/1/exe  ||  cat /proc/1/comm\n-> systemd (systemctl) / OpenRC (rc-service) / runit / контейнер",
         "#fdecea", POS),

        (40.0, 165.0, 410.0, 68.0, "Крок 3. Системна бібліотека C (libc)",
         "readelf -l /bin/sh | grep interpreter  ||  ldd /bin/sh\n-> glibc (ld-linux.so) чи musl (ld-musl.so) чи статичний BusyBox",
         "#eef7f0", FIELD),

        (490.0, 165.0, 410.0, 68.0, "Крок 4. Файлова система та монтування",
         "mount | grep ' on / '  &&  ls -ld /bin /sbin /lib\n-> Виявляє UsrMerge (/usr/bin), read-only корінь та OverlayFS",
         "#fdf0dc", "#e08a1e"),

        (40.0, 260.0, 410.0, 68.0, "Крок 5. Пакетний менеджер і сховища",
         "ls /var/lib/dpkg /var/lib/rpm /lib/apk /var/lib/pacman /nix\n-> dpkg (apt) / rpm (dnf) / apk / pacman / nix / відсутній",
         "#f3e8fd", "#8e44ad"),

        (490.0, 260.0, 410.0, 68.0, "Крок 6. Базові утиліти та оболонка",
         "ls --version 2>&1 | head -n 1  &&  ls -l /bin/sh\n-> GNU coreutils vs BusyBox, оболонка bash vs dash vs ash",
         "#e8f8f5", "#16a085"),
    ]

    for x, y, w, h, stitle, sbody, sfill, sstroke in steps:
        p.append(rect(x, y, w, h, fill="#ffffff", stroke=sstroke, sw=1.5, rx=6))
        p.append(fitbox(x + 8, y + 6, w - 16, 22, stitle, size=11.5, bold=True,
                        fill=sfill, stroke=sstroke, color=INK))
        p.append(fitbox(x + 8, y + 30, w - 16, 32, sbody, size=10, bold=False,
                        fill="#ffffff", stroke="none", color=INK))

    # Стрілки послідовності між кроками
    p.append(arrow(450, 104, 490, 104, color=LINE, sw=1.5))
    p.append(arrow(695, 138, 245, 165, color=LINE, sw=1.5))
    p.append(arrow(450, 199, 490, 199, color=LINE, sw=1.5))
    p.append(arrow(695, 233, 245, 260, color=LINE, sw=1.5))
    p.append(arrow(450, 294, 490, 294, color=LINE, sw=1.5))

    # Нижня частина: Шпаргалка типових архетипів
    p.append(rect(40, 350, W - 80, 210, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=8))
    p.append(fitbox(55, 360, W - 110, 26, "Шпаргалка архетипів сучасних Unix/Linux систем",
                    size=12.5, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    rows_arch = [
        ("Архетип", "Ядро / ABI", "Бібліотека libc", "Init / PID 1", "Пакунки", "ФС / Утиліти"),
        ("Серверний (Debian/Ubuntu/RHEL)", "Linux x86/arm64", "glibc", "systemd", "dpkg / rpm", "UsrMerge, GNU coreutils"),
        ("Контейнерний (Alpine)", "Linux x86/arm64", "musl", "OpenRC / dumb-init", "apk", "BusyBox, стандартний FHS"),
        ("Декларативний (NixOS)", "Linux", "glibc", "systemd", "nix store", "/nix/store, ізольовані бінарники"),
        ("Вбудований (OpenWrt/Yocto)", "Linux MIPS/ARM", "musl / uClibc", "procd / busybox", "opkg / немає", "SquashFS + Overlay, BusyBox"),
        ("Мобільний (Android)", "Linux (AOSP)", "Bionic", "Android init.rc", "APK (ART)", "A/B read-only, Toybox"),
    ]

    rx0, ry0 = 55.0, 395.0
    col_w = [180.0, 120.0, 110.0, 130.0, 110.0, 180.0]
    r_h = 24.0

    for ridx, row in enumerate(rows_arch):
        cx = rx0
        is_hdr = (ridx == 0)
        for cidx, cell in enumerate(row):
            w = col_w[cidx]
            bg_col = "#eaf0fd" if is_hdr else ("#ffffff" if ridx % 2 == 1 else "#f4f6f8")
            p.append(rect(cx, ry0 + ridx * r_h, w, r_h, fill=bg_col, stroke="#dfe4ea", sw=1, rx=0))
            p.append(text(cx + w / 2, ry0 + ridx * r_h + 16, cell,
                          size=10.5 if not is_hdr else 11, bold=is_hdr,
                          color=INK if not is_hdr else NEG))
            cx += w

    render(os.path.join(OUT, "distro-triage-flowchart.svg"), W, H, *p,
           title="Послідовний протокол обстеження дистрибутива")


if __name__ == "__main__":
    fig_distro_architecture_layers()
    fig_elf_pt_interp_resolution()
    fig_distro_triage_flowchart()
    print("OK figs")
