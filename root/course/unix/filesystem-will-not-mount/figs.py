# -*- coding: utf-8 -*-
"""Генератор схем для теми 'ФС не монтується: розбір за моделлю'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_mount_kernel_pipeline():
    """Схема перевірки та реєстрації суперблоку у ядрі під час виклику mount."""
    w, h = 960, 620
    frags = []

    frags.append(rect(10, 10, 940, 600, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 34, "ВНУТРІШНІЙ ПАЙПЛАЙН ЯДРА: ВІД СИСТЕМНОГО ВИКЛИКУ MOUNT(2) ДО РЕЄСТРАЦІЇ VFS", size=13, color="#0f172a", bold=True))

    # Рівень 1: Простір користувача та перевірка аргументів
    frags.append(rect(25, 55, 910, 80, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(480, 72, "1. ПРОСТІР КОРИСТУВАЧА ТА ВХІДНИЙ СИСТЕМНИЙ ВИКЛИК", size=11, color="#334155", bold=True))
    frags.append(fitbox(40, 82, 275, 42, "mount(dev, dir, type, flags, data)\nабо fsopen() + fsconfig() + fsmount()", size=10, pad=4, fill="#ffffff", stroke="#0284c7", bold=True))
    frags.append(fitbox(335, 82, 280, 42, "Копіювання шляхів у простір ядра:\ngetname() / user_path_at()", size=10, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(635, 82, 285, 42, "Помилки валідації шляхів / прав:\nENOENT (нема точки) | EPERM (CAP_SYS_ADMIN)", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(480, 135, 480, 160, color="#0284c7", sw=1.8))

    # Рівень 2: VFS та пошук драйвера
    frags.append(rect(25, 160, 910, 85, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(480, 178, "2. РІВЕНЬ VFS: ПОШУК ДРАЙВЕРА ТА ЗАХОПЛЕННЯ БЛОКОВОГО ПРИСТРОЮ", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(40, 190, 275, 44, "get_fs_type(fstype)\nПошук у списку file_systems", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(335, 190, 280, 44, "blkdev_get_by_path(FMODE_EXCL)\nЕксклюзивне захоплення носія", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(635, 190, 285, 44, "Точки відмови:\nENODEV (модуль не завантажено)\nEBUSY (пристрій зайнятий LVM/холдером)", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(480, 245, 480, 270, color="#1e40af", sw=1.8))

    # Рівень 3: Читання та перевірка суперблоку
    frags.append(rect(25, 270, 910, 95, fill="#fefce8", stroke="#fde047", sw=1.5, rx=8))
    frags.append(text(480, 288, "3. ДРАЙВЕР ФС: ЗЧИТУВАННЯ ТА ВАЛІДАЦІЯ СТРУКТУРИ SUPER_BLOCK", size=11, color="#854d0e", bold=True))
    frags.append(fitbox(40, 300, 275, 54, "Зчитування суперблоку з диска:\nsb_bread(sb, offset)\n(1024B ext4, 0B xfs, 64KiB btrfs)", size=10, pad=4, fill="#ffffff", stroke="#eab308"))
    frags.append(fitbox(335, 300, 280, 54, "Перевірка валідності:\nMagic number (0xEF53 / XFSB)\nСумісність Incompat Flags\nКонтрольна сума CRC32C", size=10, pad=4, fill="#ffffff", stroke="#eab308"))
    frags.append(fitbox(635, 300, 285, 54, "Помилка валідації (EINVAL):\n«wrong fs type, bad option, bad superblock»\nПошкоджено сектор або несумісні прапорці", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(480, 365, 480, 390, color="#854d0e", sw=1.8))

    # Рівень 4: Журнал та відновлення
    frags.append(rect(25, 390, 910, 85, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(480, 408, "4. ТРАНЗАКЦІЙНИЙ ЖУРНАЛ: JOURNAL REPLAY ТА УЗГОДЖЕНІСТЬ МЕТАДАНИХ", size=11, color="#166534", bold=True))
    frags.append(fitbox(40, 420, 275, 44, "Перевірка прапорця відновлення:\nEXT4_FEATURE_INCOMPAT_RECOVER\nабо XFS log dirty check", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(335, 420, 280, 44, "Відтворення журналу (Journal Replay):\nПрогравання committed транзакцій\nОновлення метаданих на диску", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(635, 420, 285, 44, "Помилка відновлення (EIO / EROFS):\nПошкоджений журнал блокує монтування\n(потрібен fsck або -o ro,noload)", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(480, 475, 480, 500, color="#166534", sw=1.8))

    # Рівень 5: Фіксація у просторі імен
    frags.append(rect(25, 500, 910, 95, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(480, 518, "5. ФІКСАЦІЯ ТОЧКИ МОНТУВАННЯ ТА СТВОРЕННЯ STRUCT VFSMOUNT", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(40, 530, 275, 54, "Створення struct vfsmount\nІніціалізація кореневого dentry:\nsb->s_root (inode 2 для ext4)", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(335, 530, 280, 54, "Прикріплення до дерева простору:\nattach_recursive_mnt()\nОновлення /proc/mounts", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(635, 530, 285, 54, "Успіх операції:\nКод повернення 0\nФС готова до операцій вводу-виводу", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "mount-kernel-pipeline.svg"), w, h, *frags)


def fig_ext4_superblock_geometry():
    """Схема розташування основного та резервних суперблоків у Ext4."""
    w, h = 960, 520
    frags = []

    frags.append(rect(10, 10, 940, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 34, "ГЕОМЕТРІЯ ГРУП БЛОКІВ EXT4 ТА РОЗТАШУВАННЯ РЕЗЕРВНИХ СУПЕРБЛОКІВ", size=13, color="#0f172a", bold=True))

    # Пояснення структури носія
    frags.append(fitbox(30, 55, 900, 48, "Файлова система Ext4 розбивається на Block Groups (типово 32 768 блоків по 4 КіБ = 128 МіБ на групу).\nОсновний суперблок розташований у Групі 0. Завдяки прапорцю sparse_super резервні суперблоки зберігаються лише у вибраних групах.", size=10, pad=4, fill="#f8fafc", stroke="#94a3b8"))

    # Група 0: Первинний суперблок
    frags.append(rect(30, 120, 210, 240, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=8))
    frags.append(fitbox(40, 128, 190, 26, "Група блоків 0 (LBA 0..128M)", size=10, pad=2, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True))
    frags.append(fitbox(40, 160, 190, 36, "Зміщення 0..1023 байти:\nx86 Boot / MBR Padding", size=9, pad=3, fill="#f1f5f9", stroke="#94a3b8"))
    frags.append(fitbox(40, 202, 190, 52, "ОСНОВНИЙ СУПЕРБЛОК\nБлок 0 (1K) або Блок 0..1 (4K)\nMagic: 0xEF53 (Offset 1024B)", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(40, 260, 190, 32, "Group Descriptors (GDT)", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(40, 298, 190, 52, "Block / Inode Bitmaps\nТаблиця Inode (Inode Table)\nБлоки даних користувача", size=9, pad=3, fill="#ffffff", stroke="#64748b"))

    # Група 1: Резервний суперблок 1
    frags.append(rect(260, 120, 210, 240, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    frags.append(fitbox(270, 128, 190, 26, "Група блоків 1 (3¹)", size=10, pad=2, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(270, 160, 190, 48, "РЕЗЕРВНИЙ СУПЕРБЛОК #1\nБлок 32768 (для блоку 4 КіБ)\nТочна копія суперблоку", size=9, pad=3, fill="#fef9c3", stroke="#eab308", color="#854d0e", bold=True))
    frags.append(fitbox(270, 214, 190, 34, "Резервна таблиця GDT", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(270, 254, 190, 96, "Block / Inode Bitmaps\nТаблиця Inode\nБлоки даних користувача\n\n(Використовується для\ne2fsck -b 32768)", size=9, pad=3, fill="#ffffff", stroke="#64748b"))

    # Група 3: Резервний суперблок 2
    frags.append(rect(490, 120, 210, 240, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    frags.append(fitbox(500, 128, 190, 26, "Група блоків 3 (3¹)", size=10, pad=2, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(500, 160, 190, 48, "РЕЗЕРВНИЙ СУПЕРБЛОК #2\nБлок 98304 (для блоку 4 КіБ)\n(3 × 32768)", size=9, pad=3, fill="#fef9c3", stroke="#eab308", color="#854d0e", bold=True))
    frags.append(fitbox(500, 214, 190, 34, "Резервна таблиця GDT", size=9, pad=3, fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(500, 254, 190, 96, "Block / Inode Bitmaps\nТаблиця Inode\nБлоки даних користувача\n\n(Використовується для\ne2fsck -b 98304)", size=9, pad=3, fill="#ffffff", stroke="#64748b"))

    # Групи без суперблоків та група 5, 7, 9
    frags.append(rect(720, 120, 210, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(fitbox(730, 128, 190, 26, "Решта груп (sparse_super)", size=10, pad=2, fill="#e2e8f0", stroke="#64748b", color="#334155", bold=True))
    frags.append(fitbox(730, 160, 190, 68, "Групи 2, 4, 6, 8...:\nНЕ МІСТЯТЬ копій суперблоку!\n(економія місця на диску)\n\nГрупи 5 (163840), 7 (229376),\n9 (294912) МІСТЯТЬ копії (степені 3, 5, 7)", size=9, pad=3, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(730, 234, 190, 116, "Степені 3, 5, 7:\n• 3⁰=1, 3¹=3, 3²=9, 3³=27\n• 5¹=5, 5²=25, 5³=125\n• 7¹=7, 7²=49, 7³=343\n\nКоманда розрахунку:\nmke2fs -n -b 4096 /dev/sdX", size=9, pad=3, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    # Панель команд відновлення
    frags.append(rect(30, 380, 900, 105, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    frags.append(text(480, 400, "ПРАКТИЧНИЙ АЛГОРИТМ ВІДНОВЛЕННЯ ПРИ ПОШКОДЖЕННІ ГОЛОВНОГО СУПЕРБЛОКУ", size=11, color="#991b1b", bold=True))
    frags.append(fitbox(45, 415, 415, 60, "1. Зчитування геометрії без запису (Dry-Run):\n$ dumpe2fs /dev/sdX | grep -i superblock\nабо $ mke2fs -n -b 4096 /dev/sdX", size=10, pad=4, fill="#ffffff", stroke="#fca5a5"))
    frags.append(fitbox(475, 415, 440, 60, "2. Відновлення з резервної копії:\n$ e2fsck -b 32768 -y /dev/sdX\n(e2fsck копіює валідний резервний суперблок у Групу 0)", size=10, pad=4, fill="#ffffff", stroke="#fca5a5", bold=True))

    render(os.path.join(OUT_DIR, "ext4-superblock-geometry.svg"), w, h, *frags)


def fig_mount_failure_decision_tree():
    """Діагностичне дерево розбору причин відмови монтування."""
    w, h = 960, 600
    frags = []

    frags.append(rect(10, 10, 940, 580, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 34, "ДІАГНОСТИЧНА МАТРИЦЯ РОЗБОРУ ТИПОВИХ ВІДМОВ MOUNT(8)", size=13, color="#0f172a", bold=True))

    # Корінь проблеми
    frags.append(fitbox(340, 55, 280, 36, "ЗБІЙ ВИКЛИКУ MOUNT(8)\nКод повернення != 0", size=11, pad=4, fill="#fee2e2", stroke="#ef4444", color="#991b1b", bold=True))

    # Стрілки розгалуження
    frags.append(arrow(380, 91, 140, 120, color="#64748b", sw=1.5))
    frags.append(arrow(430, 91, 370, 120, color="#64748b", sw=1.5))
    frags.append(arrow(530, 91, 590, 120, color="#64748b", sw=1.5))
    frags.append(arrow(580, 91, 820, 120, color="#64748b", sw=1.5))

    # Гілка 1: ENODEV (Unknown FS)
    frags.append(rect(25, 120, 215, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(fitbox(35, 128, 195, 36, "«unknown filesystem type»\nПомилка: ENODEV", size=10, pad=3, fill="#e2e8f0", stroke="#64748b", bold=True))
    frags.append(fitbox(35, 170, 195, 75, "Джерело збою:\nЯдро не знає типу ФС.\nМодуль не завантажено або\nвідсутній у збірці ядра чи\nврізаному initramfs.", size=9, pad=3, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(35, 252, 195, 80, "Діагностика:\n$ cat /proc/filesystems\n$ lsmod | grep <fs>\n$ modinfo <fs_name>\n$ ls /lib/modules/$(uname -r)", size=9, pad=3, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(35, 340, 195, 100, "Усунення:\n1. $ modprobe <fs_name>\n2. В initramfs: оновити конфіг\nта перегенерувати образ:\n$ dracut -f\nабо $ update-initramfs -u", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(35, 448, 195, 90, "Пастка:\nОновлення ядра без ребуту:\nстарі модулі видалено з диска,\nmodprobe не знайде шляху\nдоки вузол не перезавантажено.", size=9, pad=3, fill="#fef2f2", stroke="#f87171", color="#991b1b"))

    # Гілка 2: EINVAL (Bad Superblock)
    frags.append(rect(250, 120, 225, 430, fill="#fefce8", stroke="#fde047", sw=1.5, rx=8))
    frags.append(fitbox(260, 128, 205, 36, "«bad superblock / wrong fs»\nПомилка: EINVAL", size=10, pad=3, fill="#fef9c3", stroke="#ca8a04", color="#854d0e", bold=True))
    frags.append(fitbox(260, 170, 205, 75, "Джерело збою:\nПошкоджено магічне число,\nрозмір блоку чи контрольні\nсуми; хибна опція mount; або\nзсув таблиці розділів.", size=9, pad=3, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(260, 252, 205, 80, "Діагностика:\n$ dmesg | tail -n 20\n$ blkid /dev/sdX\n$ file -s /dev/sdX\n$ dumpe2fs -h /dev/sdX", size=9, pad=3, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(260, 340, 205, 100, "Усунення:\n1. Прибрати хибні опції -o\n2. Знайти резервний SB:\n$ mke2fs -n -b 4096 /dev/sdX\n3. Відновити суперблок:\n$ e2fsck -b 32768 /dev/sdX", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(260, 448, 205, 90, "Пастка:\nЗапуск fsck на живій ФС\nгарантовано руйнує дані!\nЗавжди перевіряти статус:\n$ findmnt /dev/sdX", size=9, pad=3, fill="#fef2f2", stroke="#f87171", color="#991b1b"))

    # Гілка 3: EBUSY (Device / Target Busy)
    frags.append(rect(485, 120, 225, 430, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(fitbox(495, 128, 205, 36, "«target is busy / EBUSY»\nПомилка: EBUSY", size=10, pad=3, fill="#dbeafe", stroke="#3b82f6", color="#1e40af", bold=True))
    frags.append(fitbox(495, 170, 205, 75, "Джерело збою:\n1. Відкриті дескриптори в точці.\n2. Вкладене активне монтування.\n3. Блоковий пристрій захоплено\nLVM, LUKS, RAID чи multipath.", size=9, pad=3, fill="#ffffff", stroke="#bfdbfe"))
    frags.append(fitbox(495, 252, 205, 80, "Діагностика:\n$ fuser -vm /mnt/point\n$ lsof +f -- /mnt/point\n$ lsblk -f\n$ ls -l /sys/class/block/*/holders", size=9, pad=3, fill="#ffffff", stroke="#bfdbfe"))
    frags.append(fitbox(495, 340, 205, 100, "Усунення:\n1. Завершити процеси (fuser -k)\n2. Монтувати розшифрований\n/dev/mapper/xxx замість сирого\n3. Зупинити конфліктний VG:\n$ vgchange -an <vg_name>", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(495, 448, 205, 90, "Пастка:\nЛедаче відмонтування (umount -l)\nховає точку з VFS, але пристрій\nзалишається зайнятим у ядрі\nпоки процеси тримають fd!", size=9, pad=3, fill="#fef2f2", stroke="#f87171", color="#991b1b"))

    # Гілка 4: FSTAB / EMERGENCY MODE
    frags.append(rect(720, 120, 215, 430, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(fitbox(730, 128, 195, 36, "«Emergency Mode / fstab»\nЗбій завантаження systemd", size=10, pad=3, fill="#f3e8ff", stroke="#a855f7", color="#6b21a8", bold=True))
    frags.append(fitbox(730, 170, 195, 75, "Джерело збою:\nВідсутній диск з /etc/fstab,\nзмінився UUID після клонування,\nабо мережевий диск монтується\nдо ініціалізації мережі.", size=9, pad=3, fill="#ffffff", stroke="#e9d5ff"))
    frags.append(fitbox(730, 252, 195, 80, "Діагностика:\n$ journalctl -xb\n$ systemctl --failed\n$ blkid\n$ cat /etc/fstab", size=9, pad=3, fill="#ffffff", stroke="#e9d5ff"))
    frags.append(fitbox(730, 340, 195, 100, "Усунення:\n1. Додати опцію `nofail`\n2. Для NFS/iSCSI: `_netdev`\n3. Оновити UUID у /etc/fstab:\nUUID=xxx /data ext4 defaults,nofail 0 2\n4. $ systemctl daemon-reload", size=9, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(fitbox(730, 448, 195, 90, "Пастка:\nЗабутий `nofail` на некритичному\nдиску зупиняє завантаження всього\nсервера на 90-секундному таймауті\nз падінням в emergency.target!", size=9, pad=3, fill="#fef2f2", stroke="#f87171", color="#991b1b"))

    render(os.path.join(OUT_DIR, "mount-failure-decision-tree.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_mount_kernel_pipeline()
    fig_ext4_superblock_geometry()
    fig_mount_failure_decision_tree()
    print("Всі 3 фігури згенеровано успішно.")
