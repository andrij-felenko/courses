# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Від живлення до запрошення входу'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_boot_chain_end_to_end():
    """Повний наскрізний ланцюг завантаження: 5 послідовних етапів з естафетою керування."""
    w, h = 980, 690
    frags = []

    # Загальна рамка полотна
    frags.append(rect(10, 10, 960, 670, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Етап 1: Прошивка (Firmware: UEFI / BIOS)
    frags.append(rect(25, 25, 930, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(490, 46, "1. АПАРАТНЕ ВКЛЮЧЕННЯ ТА ПРОШИВКА (FIRMWARE: UEFI / BIOS)", size=12, color="#334155", bold=True))
    frags.append(fitbox(40, 58, 260, 50, "Апаратне скидання CPU\nPOWER_GOOD -> Reset Vector\n(0xFFFFFFF0 / 16-bit real mode)", size=10, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(320, 58, 310, 50, "Фази UEFI (SEC -> PEI -> DXE)\nІніціалізація DRAM, шини PCIe\nЗавантаження драйверів дисків", size=10, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(650, 58, 290, 50, "Менеджер BDS & Secure Boot\nПеревірка підпису (PK, KEK, db)\nЗапуск завантажувача з ESP FAT32", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    # Стрілка 1 -> 2
    frags.append(arrow(490, 120, 490, 150, color="#475569", sw=2.0))
    frags.append(fitbox(505, 124, 250, 22, "UEFI передає PE-двійник у RAM", size=9, pad=3, fill="#f1f5f9", stroke="#94a3b8", color="#475569"))

    # Етап 2: Завантажувач (Bootloader: GRUB2 / systemd-boot / UKI)
    frags.append(rect(25, 150, 930, 95, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(490, 171, "2. ЗАВАНТАЖУВАЧ СИСТЕМИ (BOOTLOADER: GRUB2 / SYSTEMD-BOOT / UKI)", size=12, color="#1e40af", bold=True))
    frags.append(fitbox(40, 183, 270, 50, "Зчитування конфігурації\ngrub.cfg / loader.conf / UKI\nВибір ядра та опцій запуску", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(330, 183, 290, 50, "Завантаження компонентів у RAM\nvmlinuz + initramfs (AllocatePages)\nПідготовка структури boot_params", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(640, 183, 300, 50, "Передача керування ядру\nФормування cmdline (root=UUID=...)\nВиклик ExitBootServices() -> startup_64", size=10, pad=4, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a", bold=True))

    # Стрілка 2 -> 3
    frags.append(arrow(490, 245, 490, 275, color="#1e40af", sw=2.0))
    frags.append(fitbox(505, 249, 290, 22, "Стрибок у 64-бітний режим (Long Mode)", size=9, pad=3, fill="#eff6ff", stroke="#93c5fd", color="#1e40af"))

    # Етап 3: Ядро та initramfs (Kernel Init & Early Userspace)
    frags.append(rect(25, 275, 930, 105, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(490, 296, "3. ІНІЦІАЛІЗАЦІЯ ЯДРА ТА РАННІЙ ПРОСТІР (KERNEL & INITRAMFS)", size=12, color="#166534", bold=True))
    frags.append(fitbox(40, 308, 270, 60, "Декомпресія та start_kernel()\nMMU, Buddy Allocator, ACPI\ndo_initcalls() -> драйвери заліза\nЗапуск kthreadd (PID 2)", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(330, 308, 290, 60, "Розгортання initramfs (tmpfs)\nЗапуск /init, ранній udevd\nЗавантаження модулів сховищ\nLUKS дешифрування, LVM/mdadm", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(640, 308, 300, 60, "Монтування /sysroot & switch_root\nМонтування справжнього кореня (ro)\nПеренесення /dev, /proc, /sys, /run\nexecve('/sbin/init') -> заміна PID 1", size=10, pad=4, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))

    # Стрілка 3 -> 4
    frags.append(arrow(490, 380, 490, 410, color="#166534", sw=2.0))
    frags.append(fitbox(505, 384, 270, 22, "PID 1 стає повноцінним менеджером", size=9, pad=3, fill="#f0fdf4", stroke="#86efac", color="#166534"))

    # Етап 4: Менеджер служб systemd (PID 1 & Service Dependency Graph)
    frags.append(rect(25, 410, 930, 115, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(490, 431, "4. СИСТЕМНИЙ МЕНЕДЖЕР SYSTEMD (PID 1: ГРАФ ЦІЛЕЙ ТА СЛУЖБ)", size=12, color="#6b21a8", bold=True))
    frags.append(fitbox(40, 443, 270, 70, "Генератори та cgroups v2\nМонтування /sys/fs/cgroup\nsystemd-fstab-generator (/etc/fstab)\nЗапуск systemd-journald", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(330, 443, 290, 70, "Базові бар'єри синхронізації\nsysinit.target (диски, udev, sysctl)\nbasic.target (сокети, таймери, D-Bus)\nПаралельний старт за сокетом", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(640, 443, 300, 70, "Фінальні цілі завантаження\nmulti-user.target (мережі, sshd, cron)\ngraphical.target (DM: gdm/sddm)\nАктивація getty.target на консолях", size=10, pad=4, fill="#f3e8ff", stroke="#9333ea", color="#581c87", bold=True))

    # Стрілка 4 -> 5
    frags.append(arrow(490, 525, 490, 555, color="#6b21a8", sw=2.0))
    frags.append(fitbox(505, 529, 290, 22, "Spawn agetty / Display Manager", size=9, pad=3, fill="#faf5ff", stroke="#d8b4fe", color="#6b21a8"))

    # Етап 5: Запрошення входу та сеанс (Login Prompt, PAM & User Shell)
    frags.append(rect(25, 555, 930, 105, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(490, 576, "5. ШЛЮЗ АВТЕНТИФІКАЦІЇ ТА СЕАНС КОРИСТУВАЧА (LOGIN & USER SHELL)", size=12, color="#9a3412", bold=True))
    frags.append(fitbox(40, 588, 270, 60, "Відкриття віртуальної TTY\nagetty відкриває /dev/tty1\nНалаштування termios (ECHO, ICRNL)\nВивід /etc/issue та 'login: '", size=10, pad=4, fill="#ffffff", stroke="#f97316"))
    frags.append(fitbox(330, 588, 290, 60, "Автентифікація через PAM\n/etc/pam.d/login (pam_unix.so)\nПеревірка хешу в /etc/shadow\npam_systemd -> реєстрація сесії", size=10, pad=4, fill="#ffffff", stroke="#f97316"))
    frags.append(fitbox(640, 588, 300, 60, "Запуск оболонки користувача\nsystemd-logind: user-1000.slice\nsetuid/setgid, змінні оточення\nexecve('/bin/bash', ['-bash'], ...)", size=10, pad=4, fill="#ffedd5", stroke="#ea580c", color="#7c2d12", bold=True))

    render(os.path.join(OUT_DIR, "boot-chain-end-to-end.svg"), w, h, *frags)


def fig_initramfs_switch_root():
    """Анатомія переходу від initramfs до реального кореня через switch_root."""
    w, h = 960, 520
    frags = []

    frags.append(rect(10, 10, 940, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 36, "МЕХАНІЗМ ПЕРЕМИКАННЯ КОРЕНЯ: ВІД INITRAMFS ДО СПРАВЖНЬОЇ СИСТЕМИ", size=13, color="#0f172a", bold=True))

    # Ліва колонка: Тимчасовий простір initramfs (tmpfs у RAM)
    frags.append(rect(30, 60, 425, 430, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(242, 85, "1. РАННІЙ ПРОСТІР (INITRAMFS / TMPFS)", size=12, color="#1e40af", bold=True))

    frags.append(fitbox(50, 105, 385, 45, "Корінь у RAM (rootfs / tmpfs)\nМістить мінімальний набір: /init, udevd, cryptsetup", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(50, 160, 385, 55, "Монтування віртуальних API-ФС:\n/dev (devtmpfs) -> виявлення блокових пристроїв\n/proc, /sys, /run -> взаємодія з ядром", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(50, 225, 385, 60, "Підготовка цільового сховища:\n1. Завантаження драйверів nvme.ko / ahci.ko\n2. Дешифрування LUKS -> /dev/mapper/root\n3. Збирання LVM тома /dev/vg0/root", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(50, 295, 385, 55, "Монтування реального диска:\nmount -t ext4 -o ro /dev/mapper/root /sysroot\nФайлове дерево диска стає доступним у /sysroot", size=10, pad=4, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a", bold=True))
    frags.append(fitbox(50, 360, 385, 115, "Чому chroot недостатньо:\n- Залишає старий tmpfs змонтованим у RAM (витік пам'яті)\n- Старі відкриті дескриптори блокують розмонтування\n- Процес /init залишається предком, а не стає PID 1\nПотрібна спеціальна системна утиліта: switch_root", size=9, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    # Центральна стрілка переходу
    frags.append(arrow(460, 270, 495, 270, color="#2563eb", sw=2.5))
    frags.append(text(480, 255, "switch_root", size=10, color="#1d4ed8", bold=True))

    # Права колонка: Справжня коренева система
    frags.append(rect(500, 60, 430, 430, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(715, 85, "2. ПОСТІЙНА СИСТЕМА (РЕАЛЬНИЙ ROOTFS)", size=12, color="#166534", bold=True))

    frags.append(fitbox(520, 105, 390, 65, "Крок 1: Перенесення точок монтування\nmount --move /dev /sysroot/dev\nmount --move /proc /sysroot/proc\nmount --move /sys /sysroot/sys\nmount --move /run /sysroot/run", size=9, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(520, 180, 390, 65, "Крок 2: Рекурсивне очищення RAM\nВидалення всіх файлів і каталогів з tmpfs initramfs\nЗвільнення оперативної пам'яті ядра\n(пам'ять initramfs повністю повертається системі)", size=9, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(520, 255, 390, 65, "Крок 3: Зміна кореневого каталогу\nchroot('/sysroot') та chdir('/')\nКоренем процесу стає фізичний накопичувач\nТочка /sysroot стає новим глобальним '/'", size=9, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(520, 330, 390, 75, "Крок 4: Передача керування PID 1\nexecve('/sbin/init', ['/sbin/init'], envp)\nPID 1 (колишній скрипт /init) замінює свій двійковий код\nна справжній менеджер /lib/systemd/systemd", size=9, pad=4, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))
    frags.append(fitbox(520, 415, 390, 60, "Результат:\nПовноцінне середовище дистрибутиву готове до роботи,\nжодного сліду initramfs у пам'яті не залишається.", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "initramfs-switch-root.svg"), w, h, *frags)


def fig_systemd_target_dag():
    """Орієнтований ациклічний граф цілей та фаз запуску служб у systemd."""
    w, h = 960, 560
    frags = []

    frags.append(rect(10, 10, 940, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 34, "ГРАФ ЗАЛЕЖНОСТЕЙ SYSTEMD: БАР'ЄРИ СИНХРОНІЗАЦІЇ ТА ПАРАЛЕЛЬНИЙ ЗАПУСК", size=13, color="#1e293b", bold=True))

    # Фаза 1: sysinit.target
    frags.append(rect(30, 55, 895, 105, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(120, 75, "sysinit.target", size=12, color="#334155", bold=True))
    frags.append(text(520, 75, "[Низькорівнева ініціалізація обладнання та ранніх ФС]", size=11, color="#64748b", italic=True))

    frags.append(fitbox(45, 90, 200, 55, "systemd-udevd.service\nСканування шини,\nстворення нод у /dev", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(260, 90, 205, 55, "local-fs.target\nМонтування /etc/fstab,\nfsck перевірка дисків", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(480, 90, 205, 55, "systemd-sysctl.service\nЗастосування параметрів\n/etc/sysctl.d/*.conf", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(700, 90, 210, 55, "systemd-tmpfiles-setup\nСтворення каталогів\nу /tmp, /run, /var/run", size=9, pad=3, fill="#ffffff", stroke="#64748b"))

    # Стрілка вниз sysinit -> basic
    frags.append(arrow(480, 160, 480, 185, color="#475569", sw=2.0))
    frags.append(text(540, 175, "After=sysinit.target", size=9, color="#64748b", bold=True))

    # Фаза 2: basic.target
    frags.append(rect(30, 185, 895, 105, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(110, 205, "basic.target", size=12, color="#1e40af", bold=True))
    frags.append(text(520, 205, "[Базові системні примітиви, IPC шина та сокети активації]", size=11, color="#3b82f6", italic=True))

    frags.append(fitbox(45, 220, 200, 55, "sockets.target\nСлухаючі сокети:\nsystemd-journald.socket", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(260, 220, 205, 55, "timers.target\nТаймери періодичних дій:\nlogrotate.timer, fstrim.timer", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(480, 220, 205, 55, "paths.target\nМоніторинг файлових змін\nчерез inotify юніти", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(700, 220, 210, 55, "dbus.socket / dbus.service\nСистемна шина D-Bus\nміжпроцесна комунікація", size=9, pad=3, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a", bold=True))

    # Стрілки від basic до паралельних служб
    frags.append(arrow(260, 290, 260, 315, color="#2563eb", sw=1.8))
    frags.append(arrow(480, 290, 480, 315, color="#2563eb", sw=1.8))
    frags.append(arrow(700, 290, 700, 315, color="#2563eb", sw=1.8))

    # Фаза 3: Паралельні служби та multi-user.target
    frags.append(rect(30, 315, 895, 115, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(125, 335, "multi-user.target", size=12, color="#166534", bold=True))
    frags.append(text(540, 335, "[Багатокористувацьке середовище: мережа, демони та віддалений доступ]", size=11, color="#16a34a", italic=True))

    frags.append(fitbox(45, 350, 200, 65, "NetworkManager.service\n/ systemd-networkd\nІніціалізація IP-адрес,\nмаршрутів та DNS", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(260, 350, 205, 65, "sshd.service\nДемон віддаленого входу\n(запуск по сокету або\nяк фонова служба)", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(480, 350, 205, 65, "systemd-logind.service\nКерування сеансами,\nробочими місцями (seats)\nта живленням ACPI", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(700, 350, 210, 65, "getty.target\nЕкземпляри agetty на\n/dev/tty1 ... /dev/tty6\n(текстовий login prompt)", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))

    # Стрілка вниз multi-user -> graphical
    frags.append(arrow(480, 430, 480, 455, color="#16a34a", sw=2.0))
    frags.append(text(540, 445, "Wants=graphical.target", size=9, color="#166534", bold=True))

    # Фаза 4: graphical.target
    frags.append(rect(30, 455, 895, 75, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(120, 475, "graphical.target", size=12, color="#6b21a8", bold=True))
    frags.append(text(540, 475, "[Графічний дисплейний менеджер: Wayland композитор або Xorg сервер]", size=11, color="#7e22ce", italic=True))

    frags.append(fitbox(45, 490, 420, 32, "display-manager.service (GDM / SDDM / LightDM)", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(480, 490, 430, 32, "Графічне вікно автентифікації користувача на /dev/tty7", size=10, pad=4, fill="#f3e8ff", stroke="#9333ea", color="#581c87", bold=True))

    render(os.path.join(OUT_DIR, "systemd-target-dag.svg"), w, h, *frags)


def fig_tty_session_spawn():
    """Шлях від генератора getty до інтерактивного сеансу оболонки користувача."""
    w, h = 960, 520
    frags = []

    frags.append(rect(10, 10, 940, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 34, "ВІД AGETTY ДО ОБОЛОНКИ: СТВОРЕННЯ СЕАНСУ ТА АВТЕНТИФІКАЦІЯ", size=13, color="#1e293b", bold=True))

    # Колонка 1: agetty та TTY пристрій
    frags.append(rect(30, 55, 275, 435, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(167, 78, "1. AGETTY ТА TTY НОДА", size=11, color="#334155", bold=True))
    frags.append(fitbox(45, 95, 245, 60, "systemd-getty-generator\nДинамічно створює юніт\ngetty@tty1.service\nпри відкритті консолі", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(45, 165, 245, 75, "Відкриття /dev/tty1\nСистемний виклик open()\nНалаштування termios:\n- Baud rate (38400)\n- ICRNL (переклад CR у NL)\n- ECHO (відображення вводу)", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(45, 250, 245, 65, "Вивід запрошення\nЗчитування /etc/issue\nВивід на екран рядка:\n'Ubuntu 24.04 LTS'\n'hostname login: '", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(45, 325, 245, 75, "Зчитування імені\nКористувач вводить логін\nagetty очищає буфер\nі викликає через execve:\n/bin/login username", size=9, pad=3, fill="#f1f5f9", stroke="#475569", color="#1e293b", bold=True))
    frags.append(fitbox(45, 410, 245, 65, "Результат фази 1:\nПроцес agetty передає TTY дескриптор програмі login", size=9, pad=3, fill="#ffffff", stroke="#64748b"))

    # Стрілка 1 -> 2
    frags.append(arrow(305, 270, 335, 270, color="#475569", sw=2.0))

    # Колонка 2: PAM автентифікація
    frags.append(rect(335, 55, 290, 435, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(480, 78, "2. КОНВЕЄР PAM ТА LOGIND", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(350, 95, 260, 60, "Стек /etc/pam.d/login\nПослідовний запуск модулів\nauth, account, password,\nsession", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(350, 165, 260, 75, "pam_unix.so (auth)\nЗапит пароля користувача\n(прихований ввід без echo)\nОбчислення SHA-512 / yescrypt\nЗвірка з /etc/shadow", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(350, 250, 260, 65, "pam_systemd.so (session)\nРеєстрація у systemd-logind\nчерез D-Bus метод:\nCreateSession()", size=9, pad=3, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a", bold=True))
    frags.append(fitbox(350, 325, 260, 75, "Виділення ресурсів сесії\nlogind створює cgroup:\nuser-1000.slice/session-1.scope\nМонтує /run/user/1000 (tmpfs)\nПризначає права на seat0", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(350, 410, 260, 65, "Результат фази 2:\nКористувача автентифіковано,\nсеанс зареєстровано в ядрі", size=9, pad=3, fill="#eff6ff", stroke="#2563eb", color="#1e40af", bold=True))

    # Стрілка 2 -> 3
    frags.append(arrow(625, 270, 655, 270, color="#2563eb", sw=2.0))

    # Колонка 3: Запуск оболонки
    frags.append(rect(655, 55, 275, 435, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(792, 78, "3. ІНТЕРАКТИВНИЙ SHELL", size=11, color="#166534", bold=True))
    frags.append(fitbox(670, 95, 245, 60, "Зниження привілеїв\nlogin отримує дані з /etc/passwd:\nUID=1000, GID=1000\nsetgid(1000) -> initgroups()", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(670, 165, 245, 75, "Зміна ідентифікатора\nsetuid(1000)\nПроцес остаточно втрачає\nправа суперкористувача root\nі стає звичайним користувачем", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(670, 250, 245, 65, "Змінні середовища\nHOME=/home/user\nUSER=user\nSHELL=/bin/bash\nPATH=/usr/bin:...", size=9, pad=3, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(670, 325, 245, 75, "Перехід у домашній каталог\nchdir('/home/user')\nВиклик системної функції:\nexecve('/bin/bash', ['-bash'], envp)\nМінус означає 'login shell'", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))
    frags.append(fitbox(670, 410, 245, 65, "Результат фази 3:\nКористувач бачить запрошення:\n'user@host:~$ ' — система готова!", size=9, pad=3, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "tty-session-spawn.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_boot_chain_end_to_end()
    fig_initramfs_switch_root()
    fig_systemd_target_dag()
    fig_tty_session_spawn()
    print("Всі фігури згенеровано успішно в img/")
