# -*- coding: utf-8 -*-
"""Фігури до теми «Юзер-простори імен (User Namespaces) та відображення UID/GID»."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_uid_mapping_translation():
    """Схема двонапрямного відображення UID/GID між хостом та User Namespace."""
    W, H = 1050, 480
    f = []

    # Заголовок / підзаголовок
    f.append(text(W / 2, 35, "Двонапрямне відображення UID/GID у ядрі Linux", size=18, bold=True))
    f.append(text(W / 2, 60, "Ядро транслює ідентифікатори під час викликів VFS, getuid() та stat()", size=13, color=MUTED))

    # Контейнер Host Namespace
    f.append(rect(60, 95, 410, 340, fill="#f4f7fb", stroke="#2457d6", sw=2, rx=10))
    f.append(text(265, 125, "Хостовий простір імен (Host Namespace)", size=15, bold=True, color="#2457d6"))

    # Блоки хоста
    b1, _, _ = textbox(265, 185, "Основний користувач (Host UID 1000)\nвиклики у ядро VFS / sys_open", size=13, pad=12, fill="#ffffff", stroke="#2457d6", rx=6)
    f.append(b1)
    b2, _, _ = textbox(265, 305, "Діапазон SubUID (/etc/subuid)\nHost UID 100000 .. 165535", size=13, pad=12, fill="#ffffff", stroke="#2457d6", rx=6)
    f.append(b2)
    b3, _, _ = textbox(265, 395, "Невідображені UID хоста\nпоза 1000 та 100000..165535 -> nobody (65534)", size=12, pad=8, fill="#fff5f5", stroke="#c0392b", rx=6)
    f.append(b3)

    # Контейнер User Namespace
    f.append(rect(580, 95, 410, 340, fill="#f5fbf7", stroke="#27ae60", sw=2, rx=10))
    f.append(text(785, 125, "Новий User Namespace (Контейнер)", size=15, bold=True, color="#27ae60"))

    # Блоки контейнера
    b4, _, _ = textbox(785, 185, "Суперкористувач контейнера (UID 0)\nCAP_SYS_ADMIN лише в межах цього ns", size=13, pad=12, fill="#ffffff", stroke="#27ae60", rx=6)
    f.append(b4)
    b5, _, _ = textbox(785, 305, "Користувачі та сервіси контейнера\nUID 1 .. 65536 (daemon, www-data)", size=13, pad=12, fill="#ffffff", stroke="#27ae60", rx=6)
    f.append(b5)
    b6, _, _ = textbox(785, 395, "Спроба доступу до ресурсів хоста\nОбмежено перевіркою ns_capable()", size=12, pad=8, fill="#ffffff", stroke="#27ae60", rx=6)
    f.append(b6)

    # Стрілки відображення
    f.append(arrow(570, 185, 480, 185, color="#2457d6", sw=2))
    f.append(text(525, 172, "0 -> 1000", size=12, bold=True, color="#2457d6"))

    f.append(arrow(570, 305, 480, 305, color="#27ae60", sw=2))
    f.append(text(525, 292, "1..65536", size=12, bold=True, color="#27ae60"))

    render(os.path.join(OUT, 'uid-mapping-translation.svg'), W, H, *f,
           title="Двонапрямне відображення UID між хостом та User Namespace")


def fig_subuid_newuidmap_flow():
    """Послідовність налаштування підпорядкованих ідентифікаторів у rootless контейнерах."""
    W, H = 1100, 420
    f = []

    f.append(text(W / 2, 35, "Послідовність ініціалізації мапінгу через newuidmap", size=18, bold=True))
    f.append(text(W / 2, 60, "Авторизація subuid та запис у procfs непривілейованим користувачем", size=13, color=MUTED))

    steps = [
        ("1. unshare(CLONE_NEWUSER)", "Процес створює user_ns.\nПочатковий UID = 65534"),
        ("2. Виклики newuidmap", "Запуск setuid-хелпера\nnewuidmap PID 0 1000 1..."),
        ("3. Перевірка /etc/subuid", "Утиліта звіряє право\nкористувача на діапазон"),
        ("4. Запис у uid_map", "Хелпер з root-правами\nпише в /proc/PID/uid_map"),
        ("5. Готовий Namespace", "Процес отримує UID 0\nта 65536 subuid")
    ]

    for i, (title, desc) in enumerate(steps):
        x = 110 + i * 215
        y = 210
        b, _, _ = textbox(x, y, f"{title}\n\n{desc}", size=13, pad=12, fill="#ffffff", stroke="#2457d6", min_w=190, rx=8)
        f.append(b)

        if i < len(steps) - 1:
            f.append(arrow(x + 98, y, x + 117, y, color="#2457d6", sw=2))

    # Нижнє пояснення
    b_foot, _, _ = textbox(W / 2, 370,
                           "Захисний механізм: непривілейований процес не може сам записати чужий subuid;\n"
                           "setuid-утиліта newuidmap виступає арбітром між користувачем та ядром",
                           size=13, fill="#f4f7fb", stroke=LINE)
    f.append(b_foot)

    render(os.path.join(OUT, 'subuid-newuidmap-flow.svg'), W, H, *f,
           title="Послідовність роботи newuidmap та subuid")


def fig_idmapped_mounts_vfs():
    """Динамічне відображення інодів у VFS через ID-mapped mounts."""
    W, H = 1020, 460
    f = []

    f.append(text(W / 2, 35, "ID-mapped Mounts: Трансляція ідентифікаторів у VFS", size=18, bold=True))
    f.append(text(W / 2, 60, "Доступ до дискових файлів без модифікації chown та без перезапису інодів", size=13, color=MUTED))

    # Шари системи
    # 1. Physical Disk / FS Layer
    b_disk, _, _ = textbox(200, 240, "Дискова файлова система\n(ext4 / xfs / btrfs)\n\nInode owner: UID 1000\nФізичний вміст тома", size=14, pad=14, fill="#f4f6f8", stroke="#333333", rx=8)
    f.append(b_disk)

    # 2. VFS Layer (ID-mapped mount)
    b_vfs, _, _ = textbox(510, 240, "Шар VFS (ID-mapped Mount)\nmnt_userns відображення\n\nТрансляція на льоту:\nUID 1000 <-> UID 0", size=14, pad=14, fill="#eef3fd", stroke="#2457d6", rx=8)
    f.append(b_vfs)

    # 3. User Space / Container
    b_app, _, _ = textbox(820, 240, "User Namespace (Контейнер)\nПроцес із UID 0 (root)\n\nБачить файл як owner UID 0\nПовний доступ rwx", size=14, pad=14, fill="#eafaf1", stroke="#27ae60", rx=8)
    f.append(b_app)

    # Стрілки зв'язку
    f.append(arrow(330, 240, 385, 240, color="#2457d6", sw=2))
    f.append(arrow(635, 240, 690, 240, color="#27ae60", sw=2))

    # Пояснення внизу
    b_note, _, _ = textbox(W / 2, 400,
                           "Виклик mount_setattr(..., MOUNT_ATTR_IDMAP) прив'язує user namespace до точки монтування.\n"
                           "Різні контейнери можуть монтувати один том із різними відображеннями без повторного chown.",
                           size=13, fill="#ffffff", stroke="#2457d6")
    f.append(b_note)

    render(os.path.join(OUT, 'idmapped-mounts-vfs.svg'), W, H, *f,
           title="Динамічне відображення інодів через ID-mapped mounts")


def generate_all():
    fig_uid_mapping_translation()
    fig_subuid_newuidmap_flow()
    fig_idmapped_mounts_vfs()


if __name__ == '__main__':
    generate_all()
