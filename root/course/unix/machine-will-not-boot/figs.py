# -*- coding: utf-8 -*-
"""Генератор векторних схем для теми 'Машина не піднялася: аварійна ціль, рятувальний носій і ремонт із chroot'."""

import sys, os

# Шлях до спільних помічників svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_boot_failure_stages():
    """Схема чотирьох стадій завантаження та характерних точок відмов."""
    w, h = 980, 680
    frags = []

    # Загальне полотно
    frags.append(rect(10, 10, 960, 660, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 36, "КАРТА СТАДІЙ ЗАВАНТАЖЕННЯ LINUX ТА ХАРАКТЕРНІ ТОЧКИ ВІДМОВ", size=13, color="#0f172a", bold=True))

    # Рівень 1: Прошивка та EFI
    frags.append(rect(25, 55, 930, 125, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(490, 74, "1. АПАРАТНА ПРОШИВКА ТА ІНІЦІАЛІЗАЦІЯ (UEFI / NVRAM)", size=11, color="#334155", bold=True))
    frags.append(fitbox(40, 86, 280, 82, "Апаратний POST -> Зчитування NVRAM\nВибір завантажувального запису BootXXXX\nМонтування ESP (FAT32) -> запуск grubx64.efi\nПеревірка Secure Boot підписів shim", size=10, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(340, 86, 280, 82, "Нормальний стан:\nЗавантажувач Grub успішно\nзнаходить свій розділ /boot\nта зчитує grub.cfg", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(640, 86, 295, 82, "ТОЧКА ВІДМОВИ: Застрягання в grub rescue>\nСимптом: error: no such partition / unknown fs\nПричина: Зміщення номерів розділів GPT,\nвтрата UUID /boot або пошкодження ESP", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(490, 180, 490, 205, color="#0284c7", sw=2.0))

    # Рівень 2: Завантажувач Grub
    frags.append(rect(25, 205, 930, 125, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(490, 224, "2. ЗАВАНТАЖУВАЧ GRUB: ЗАВАНТАЖЕННЯ ЯДРА ТА INITRAMFS", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(40, 236, 280, 82, "Зчитування ядра vmlinuz у пам'ять\nЗчитування образу initramfs / initrd.img\nФормування рядка kernel cmdline:\n(root=UUID=... ro quiet splash mitigations=...)", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(340, 236, 280, 82, "Нормальний стан:\nПередача керування точці входу ядра\nРозпакування initramfs у ramfs/tmpfs\nСтарт раннього простору /init", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(640, 236, 295, 82, "ТОЧКА ВІДМОВИ: Kernel Panic / Bad Magic\nСимптом: Kernel panic - not syncing: VFS...\nПричина: Пошкоджено vmlinuz або initrd,\nнесумісні параметри cmdline", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(490, 330, 490, 355, color="#1e40af", sw=2.0))

    # Рівень 3: Ранній простір користувача initramfs
    frags.append(rect(25, 355, 930, 135, fill="#fefce8", stroke="#fde047", sw=1.5, rx=8))
    frags.append(text(490, 374, "3. РАННІЙ ПРОСТІР КОРИСТУВАЧА: ДРАЙВЕРИ, LUKS, LVM ТА ПІДКЛЮЧЕННЯ КОРЕНЯ", size=11, color="#854d0e", bold=True))
    frags.append(fitbox(40, 386, 280, 92, "Завантаження модулів сховища (nvme, ahci)\nuudevd перелічує диски та формує /dev/disk/by-uuid\nРозблокування LUKS (cryptsetup) та LVM (vgchange)\nМонтування справжнього кореня /sysroot\nВиклик switch_root або pivot_root", size=10, pad=4, fill="#ffffff", stroke="#eab308"))
    frags.append(fitbox(340, 386, 280, 92, "Нормальний стан:\nКоренева ФС змонтована в /sysroot\nКерування передається /sbin/init\n(systemd як PID 1 справжнього кореня)", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(640, 386, 295, 92, "ТОЧКА ВІДМОВИ: Застрягання в (initramfs) shell\nСимптом: Gave up waiting for root device\nПричина: Невідповідність root=UUID=...,\nвідсутній драйвер дискового контролера,\nне відкрився криптоконтейнер LUKS", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(490, 490, 490, 515, color="#854d0e", sw=2.0))

    # Рівень 4: Systemd Targets та простір користувача
    frags.append(rect(25, 515, 930, 135, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(490, 534, "4. СИСТЕМНИЙ МЕНЕДЖЕР SYSTEMD: ТАБЛИЦЯ FSTAB ТА ДЕРЕВО ЮНІТІВ", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(40, 546, 280, 92, "systemd-fstab-generator генерує *.mount юніти\nПідключення local-fs.target та sysinit.target\nЗапуск системних служб basic.target\nДосягнення цільового стану default.target\n(multi-user.target або graphical.target)", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(340, 546, 280, 92, "Нормальний стан:\nУсі юніти та розділи змонтовані\nСлужби запущені без критичних помилок\nЗапрошення входу login: на TTY", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(640, 546, 295, 92, "ТОЧКА ВІДМОВИ: Падіння в emergency.target\nСимптом: You are in emergency mode. Press Enter...\nПричина: Помилка монтування запису в /etc/fstab\nбез опції nofail, збій fsck другорядного диска,\nжорстка циклічна залежність юнітів", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    render(os.path.join(OUT_DIR, "boot-failure-stages.svg"), w, h, *frags)


def fig_chroot_pseudo_fs_hierarchy():
    """Схема зв'язування псевдо-ФС ядра при підготовці chroot."""
    w, h = 980, 580
    frags = []

    frags.append(rect(10, 10, 960, 560, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 34, "АРХІТЕКТУРА ЗВ'ЯЗУВАННЯ ПСЕВДО-ФС ДЛЯ РЕМОНТНОГО ОТОЧЕННЯ CHROOT", size=13, color="#0f172a", bold=True))

    # Хостова система LiveCD (зліва)
    frags.append(rect(30, 60, 425, 485, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    frags.append(text(242, 85, "СЕРЕДОВИЩЕ НОСІЯ ВІДНОВЛЕННЯ (LIVECD HOST)", size=11, color="#1e293b", bold=True))
    frags.append(fitbox(45, 105, 395, 45, "Ядро Linux хоста (Active Running Kernel)\nПідтримує таблиці процесів, драйвери пристроїв та IPC", size=10, pad=4, fill="#ffffff", stroke="#94a3b8"))

    # Джерела псевдо-ФС хоста
    frags.append(fitbox(45, 165, 395, 75, "/proc (procfs) — Таблиця процесів ядра, /proc/cmdline,\n/proc/mounts, /proc/cpuinfo, /proc/meminfo\n(Потрібно для утиліт пакунків, ps, grub-probe)", size=10, pad=4, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(fitbox(45, 255, 395, 75, "/sys (sysfs) — Дерево пристроїв, шини PCI/NVMe,\n/sys/firmware/efi/efivars (Змінні NVRAM)\n(Потрібно для grub-install, dracut, udev)", size=10, pad=4, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(fitbox(45, 345, 395, 75, "/dev (devtmpfs) — Спеціальні файли символьних/блокових носіїв:\n/dev/nvme*, /dev/null, /dev/urandom, /dev/pts/*\n(Потрібно для доступу до дисків та терміналів)", size=10, pad=4, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(fitbox(45, 435, 395, 95, "/run (tmpfs) — Тимчасовий стан підсистем:\n/run/udev (База пристроїв), /run/cryptsetup,\n/run/lvm (Блокування томів та сокети)\n(Потрібно для коректної роботи LVM та cryptsetup)", size=10, pad=4, fill="#eff6ff", stroke="#3b82f6"))

    # Стрілки з операціями монтування посередині
    frags.append(arrow(440, 202, 505, 202, color="#2563eb", sw=1.8))
    frags.append(arrow(440, 292, 505, 292, color="#2563eb", sw=1.8))
    frags.append(arrow(440, 382, 505, 382, color="#2563eb", sw=1.8))
    frags.append(arrow(440, 482, 505, 482, color="#2563eb", sw=1.8))

    # Цільове ремонтне дерево /mnt (справа)
    frags.append(rect(520, 60, 430, 485, fill="#faf5ff", stroke="#9333ea", sw=1.8, rx=8))
    frags.append(text(735, 85, "ЗЛАМАНА СИСТЕМА У ТОЧЦІ МОНТУВАННЯ /mnt", size=11, color="#581c87", bold=True))
    frags.append(fitbox(535, 105, 400, 45, "Кореневий розділ цільової ОС (Змонтовано у /mnt)\nМістить /mnt/etc, /mnt/usr, /mnt/boot, /mnt/var", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))

    frags.append(fitbox(535, 165, 400, 75, "mount -t proc proc /mnt/proc\nПряме монтування procfs у простір цільового кореня\n-> Відкриває процеси та системну статистику", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    frags.append(fitbox(535, 255, 400, 75, "mount --rbind /sys /mnt/sys && mount --make-rslave /mnt/sys\nРекурсивне прив'язування дерева sysfs + ізоляція rslave\n-> Доступ до EFI змінних без ризику для хоста", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    frags.append(fitbox(535, 345, 400, 75, "mount --rbind /dev /mnt/dev && mount --make-rslave /mnt/dev\nРекурсивне прив'язування devtmpfs + pts + shm\n-> Усі носії та псевдотермінали доступні у chroot", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    frags.append(fitbox(535, 435, 400, 95, "mount --rbind /run /mnt/run && mount --make-rslave /mnt/run\nРекурсивне прив'язування /run (udev database + lvm locks)\n+ cp /etc/resolv.conf /mnt/etc/resolv.conf\n-> Повна працездатність пакетних менеджерів та утиліт", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "chroot-pseudo-fs-hierarchy.svg"), w, h, *frags)


def fig_recovery_workflow_decision_tree():
    """Діагностичне дерево рішень для усунення збоїв завантаження."""
    w, h = 980, 640
    frags = []

    frags.append(rect(10, 10, 960, 620, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 34, "ДІАГНОСТИЧНИЙ АЛГОРИТМ: ВІД СИМПТОМУ ВІДМОВИ ДО ВІДНОВЛЕННЯ СИСТЕМИ", size=13, color="#0f172a", bold=True))

    # Корінь: Симптом на моніторі / консолі
    frags.append(fitbox(340, 55, 300, 48, "СИМПТОМ НА СИСТЕМНІЙ КОНСОЛІ:\nЯка підсистема зупинила завантаження?", size=11, pad=4, fill="#f1f5f9", stroke="#475569", bold=True))

    # Розгалуження на 3 головні шляхи
    frags.append(arrow(400, 103, 160, 140, color="#475569", sw=1.8))
    frags.append(arrow(490, 103, 490, 140, color="#475569", sw=1.8))
    frags.append(arrow(580, 103, 820, 140, color="#475569", sw=1.8))

    # Стовпчик 1: Збій Grub (зліва)
    frags.append(rect(25, 140, 275, 470, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(162, 160, "КОНСОЛЬ GRUB RESCUE", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(35, 175, 255, 60, "Симптом: grub rescue>\nПовідомлення: no such device / unknown fs\nВтрачено зв'язок із каталогом /boot/grub", size=9, pad=3, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(35, 245, 255, 100, "Діагностика на місці:\nls -> список розділів (hd0,gpt1)...\nls (hd0,gpt2)/boot/grub\nset root=(hd0,gpt2)\nset prefix=(hd0,gpt2)/boot/grub\ninsmod normal; normal", size=9, pad=3, fill="#f8fafc", stroke="#64748b"))
    frags.append(fitbox(35, 355, 255, 110, "Капітальний ремонт:\n1. Завантаження з LiveCD\n2. Монтування /mnt та /mnt/boot/efi\n3. rbind псевдо-ФС та вхід у chroot\n4. grub-install --target=x86_64-efi\n5. update-grub (grub-mkconfig)", size=9, pad=3, fill="#fefce8", stroke="#eab308", color="#854d0e", bold=True))
    frags.append(fitbox(35, 475, 255, 120, "Фінальний результат:\nВідновлено bootloader у ESP,\nоновлено змінні NVRAM efibootmgr,\nсистема стартує штатно", size=9, pad=3, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    # Стовпчик 2: Збій Initramfs (посередині)
    frags.append(rect(345, 140, 290, 470, fill="#fefce8", stroke="#fde047", sw=1.5, rx=8))
    frags.append(text(490, 160, "АВАРІЙНИЙ SHELL INITRAMFS", size=11, color="#854d0e", bold=True))
    frags.append(fitbox(355, 175, 270, 60, "Симптом: (initramfs) prompt\nПовідомлення: Gave up waiting for root device\nНе вдалося змонтувати кореневий розділ", size=9, pad=3, fill="#ffffff", stroke="#eab308"))
    frags.append(fitbox(355, 245, 270, 100, "Діагностика в BusyBox:\ncat /proc/cmdline -> перевірка root=UUID\nblkid -> реальні UUID дисків\nls /dev/mapper -> стан LUKS / LVM\ncryptsetup luksOpen ... -> ручний тест\nexit -> продовження спроби", size=9, pad=3, fill="#f8fafc", stroke="#64748b"))
    frags.append(fitbox(355, 355, 270, 110, "Капітальний ремонт у chroot:\n1. Виправлення UUID у /etc/fstab\n2. Оновлення /etc/crypttab для LUKS\n3. dracut -f / update-initramfs -u -k all\n(включення модулів nvme/dm-crypt)\n4. Оновлення grub.cfg", size=9, pad=3, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True))
    frags.append(fitbox(355, 475, 270, 120, "Фінальний результат:\nНовий initramfs містить потрібні\nдрайвери та конфігурацію, корінь\nуспішно монтується у /sysroot", size=9, pad=3, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    # Стовпчик 3: Збій Systemd Emergency Target (справа)
    frags.append(rect(675, 140, 280, 470, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(815, 160, "EMERGENCY / RESCUE TARGET", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(685, 175, 260, 60, "Симптом: Emergency mode консоль\nПовідомлення: Failed to mount /data...\nDependency failed for Local File Systems", size=9, pad=3, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(685, 245, 260, 100, "Діагностика в Emergency Shell:\njournalctl -xb | grep -i mount\nsystemctl --failed -> збійний юніт\ncat /etc/fstab -> перевірка записів\nblkid -> звірка UUID дисків", size=9, pad=3, fill="#f8fafc", stroke="#64748b"))
    frags.append(fitbox(685, 355, 260, 110, "Ремонт на місці (без LiveCD):\n1. mount -o remount,rw /\n2. nano /etc/fstab -> додати nofail\nдо необов'язкових дисків або виправити UUID\n3. systemctl daemon-reload\n4. systemctl default", size=9, pad=3, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True))
    frags.append(fitbox(685, 475, 260, 120, "Фінальний результат:\nsystemd успішно підключає\nlocal-fs.target та піднімає всі\nсервіси до default.target", size=9, pad=3, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "recovery-workflow-decision-tree.svg"), w, h, *frags)


if __name__ == '__main__':
    print("Генерація схем...")
    fig_boot_failure_stages()
    fig_chroot_pseudo_fs_hierarchy()
    fig_recovery_workflow_decision_tree()
    print("Усі схеми успішно згенеровано у img/")
