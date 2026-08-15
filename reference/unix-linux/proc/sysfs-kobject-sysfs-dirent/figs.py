# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#eceff1"


# ── 1. Ієрархія kobject, kset, ktype та зв'язок із sysfs ──────────────────────
def fig_kobject_hierarchy():
    W, H = 1200, 680
    p = []

    # Заголовок панелей
    p.append(rect(30, 20, 1140, 630, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # Сонце/Об'єкти простору ядра
    p.append(text(280, 55, "ПРОСТІР ЯДРА (Kernel Space)", size=16, bold=True, color=NEG))
    p.append(text(910, 55, "ПРОСТІР КОРИСТУВАЧА (/sys)", size=16, bold=True, color=POS))

    # Вертикальна роздільна лінія
    p.append(line(600, 30, 600, 630, color=MUTED, sw=1.5, dash="6,6"))

    # 1. kset (каталог підсистеми)
    p.append(fitbox(50, 90, 500, 120,
                    "struct kset (наприклад: kernel_kobj)\n"
                    "• Містить власний kobject (створює /sys/kernel)\n"
                    "• Голова списку елементів list_head list\n"
                    "• Обробляє події uevent для всіх підпорядкованих об'єктів",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    # Стрілка від kset до kobject
    p.append(arrow(300, 210, 300, 250, color=LINE, sw=2))
    p.append(text(315, 233, "член списку / child", size=11, color=MUTED, anchor="start"))

    # 2. struct kobject
    p.append(fitbox(50, 250, 500, 170,
                    "struct kobject (наприклад: demo_kobj)\n"
                    "• name: \"demo_kobj\"  (ім'я каталогу)\n"
                    "• kref: refcount_t (лічильник посилань)\n"
                    "• parent: вказівник на kset->kobj\n"
                    "• ktype: вказівник на kobj_type\n"
                    "• sd: вказівник на kernfs_node (sysfs_dirent)",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.5))

    # Стрілки від kobject до ktype та kernfs_node
    p.append(arrow(180, 420, 180, 470, color=LINE, sw=2))
    p.append(text(190, 445, "визначає поведінку", size=11, color=MUTED, anchor="start"))

    # 3. struct kobj_type & sysfs_ops
    p.append(fitbox(50, 470, 500, 150,
                    "struct kobj_type & sysfs_ops\n"
                    "• release(kobj): очищення пам'яті при kref == 0\n"
                    "• show(kobj, attr, buf): читання атрибута\n"
                    "• store(kobj, attr, buf, count): запис атрибута\n"
                    "• default_groups: масив атрибутів (status, control)",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # Права сторона: відображення у /sys
    # Каталог /sys/kernel
    p.append(fitbox(640, 110, 500, 80,
                    "Каталог /sys/kernel/\n"
                    "(створений об'єктом kernel_kobj)",
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(600, 150, 640, 150, color=NEG, sw=2))

    # Каталог /sys/kernel/demo_kobj/
    p.append(fitbox(670, 275, 470, 120,
                    "Каталог /sys/kernel/demo_kobj/\n"
                    "(створений об'єктом demo_kobj)\n\n"
                    "├── status   (0444, show -> status_show)\n"
                    "└── control  (0644, show/store)",
                    size=13, fill=WARM_FILL, stroke=LINE))

    p.append(arrow(550, 335, 670, 335, color=LINE, sw=2))
    p.append(text(610, 323, "відображення", size=11, color=MUTED))

    # Виклик процедур при читанні/записі
    p.append(fitbox(640, 480, 500, 130,
                    "Операції користувача в терміналі:\n"
                    "• cat /sys/kernel/demo_kobj/status\n"
                    "   └─ VFS -> sysfs -> ktype->sysfs_ops->show()\n"
                    "• echo 'val' > /sys/kernel/demo_kobj/control\n"
                    "   └─ VFS -> sysfs -> ktype->sysfs_ops->store()",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(550, 545, 640, 545, color=FIELD, sw=2))

    render(os.path.join(IMG, 'sysfs-kobject-hierarchy.svg'), W, H, *p)


# ── 2. Оптимізація пам'яті: kobject -> kernfs_node (sysfs_dirent) -> VFS ──
def fig_sysfs_dirent_kernfs_vfs():
    W, H = 1240, 640
    p = []

    p.append(rect(20, 20, 1200, 600, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # Заголовки систем
    p.append(fitbox(50, 40, 350, 50, "1. ОБ'ЄКТИ ЯДРА (Kernel)", size=14, bold=True, fill=WARM_FILL))
    p.append(fitbox(445, 40, 350, 50, "2. ДЕРЕВО KERNFS (sysfs_dirent)", size=14, bold=True, fill=GREEN_FILL))
    p.append(fitbox(840, 40, 350, 50, "3. СТРУКТУРИ VFS (On-demand)", size=14, bold=True, fill=BLUE_FILL))

    # Ліва колонка: struct kobject
    p.append(fitbox(50, 120, 350, 160,
                    "struct kobject\n"
                    "• розмір: ~64 байти\n"
                    "• тримає граф пристроїв\n"
                    "• kref: лічильник посилань\n"
                    "• sd ───► вказівник на\n"
                    "          kernfs_node",
                    size=13, fill=WARM_FILL, stroke=LINE))

    p.append(arrow(400, 200, 445, 200, color=LINE, sw=2))

    # Середня колонка: struct kernfs_node (історично sysfs_dirent)
    p.append(fitbox(445, 120, 350, 220,
                    "struct kernfs_node\n(історично sysfs_dirent)\n"
                    "• розмір: ВСЬОГО ~48-64 байти!\n"
                    "• автономне компактне дерево в RAM\n"
                    "• зберігає ім'я, права, тип вузла\n"
                    "• ПОСТІЙНО живе в пам'яті ядра\n"
                    "• НЕ створює об'єктів VFS до звернення!",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    # Права колонка: VFS dentry & inode
    p.append(fitbox(840, 120, 350, 220,
                    "Структури VFS в RAM\n"
                    "• struct dentry (~192 B)\n"
                    "• struct inode (~600 B)\n"
                    "• Створюються ДИНАМІЧНО при lookup/open\n"
                    "• Автоматично ВИДАЛЯЮТЬСЯ\n"
                    "  під тиском пам'яті (VFS shrinker)!",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    # Пунктирна стрілка звернення
    p.append(arrow(795, 230, 840, 230, color=NEG, sw=2))
    p.append(text(817, 215, "open() / ls", size=11, color=NEG))

    # Блок порівняння витрат пам'яті (Нижня частина)
    p.append(rect(50, 380, 1140, 210, fill=GREY_FILL, stroke=MUTED, sw=1.2, rx=8))

    p.append(text(620, 410, "ЕКОНОМІЯ ПАМ'ЯТІ НА СЕРВЕРІ З 500 000 АТРИБУТАМИ SYSFS", size=14, bold=True))

    p.append(fitbox(70, 440, 520, 130,
                    "Стара схема sysfs (перші випуски Linux 2.6):\n"
                    "500 000 атрибутів × (dentry 192 B + inode 600 B)\n"
                    "= ~400 МБ НЕСВАПОВАНОЇ ПАМ'ЯТІ SLAB\n"
                    "(виділялося постійно, навіть якщо /sys не відкривали)",
                    size=12, fill=RED_FILL, stroke=POS))

    p.append(fitbox(630, 440, 540, 130,
                    "Сучасна схема (sysfs_dirent з 2.6.10, kernfs з 3.14):\n"
                    "500 000 атрибутів × kernfs_node 48 B = ~24 МБ ПАМ'ЯТІ!\n"
                    "VFS dentry/inode виділяються лише для відкритих файлів\n"
                    "Економія: понад 370 МБ RAM на порожньому місці",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'sysfs-dirent-kernfs-vfs.svg'), W, H, *p)


if __name__ == '__main__':
    fig_kobject_hierarchy()
    fig_sysfs_dirent_kernfs_vfs()
    print("Figures generated successfully.")
