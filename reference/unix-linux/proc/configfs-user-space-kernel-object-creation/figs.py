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
PURPLE_FILL = "#f3e8ff"


# ── 1. Порівняння архітектур: sysfs vs configfs ──────────────────────────────────
def fig_configfs_vs_sysfs():
    W, H = 1180, 620
    p = []

    # Головна рамка
    p.append(rect(20, 20, 1140, 580, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # Заголовки панелей
    p.append(rect(40, 35, 530, 45, fill=BLUE_FILL, stroke=NEG, rx=6))
    p.append(text(305, 63, "sysfs: Напрямок Kernel ──► Userspace", size=16, bold=True, color=NEG))

    p.append(rect(610, 35, 530, 45, fill=GREEN_FILL, stroke=FIELD, rx=6))
    p.append(text(875, 63, "configfs: Напрямок Userspace ──► Kernel", size=16, bold=True, color=FIELD))

    # Ліва панель (sysfs)
    p.append(fitbox(50, 100, 510, 110,
                    "1. Драйвер або ядро виявляє пристрій\n"
                    "• Виклики kobject_add() / device_register()\n"
                    "• Створення kobject у пам'яті ядра\n"
                    "• Автоматичне відображення у /sys/devices/",
                    size=13, fill=WARM_FILL, stroke=LINE))

    p.append(arrow(305, 210, 305, 245, color=LINE, sw=2))

    p.append(fitbox(50, 245, 510, 110,
                    "2. Відображення об'єкта в VFS (/sys/)\n"
                    "• Ядро створює каталоги та атрибути\n"
                    "• Простір користувача бачить готову топологію\n"
                    "• mkdir повернув би помилку -EPERM",
                    size=13, fill=WARM_FILL, stroke=LINE))

    p.append(arrow(305, 355, 305, 390, color=LINE, sw=2))

    p.append(fitbox(50, 390, 510, 170,
                    "3. Доступ із простору користувача\n"
                    "• Читання стан: cat /sys/class/net/eth0/operstate\n"
                    "• Запис значень: echo 1 > /sys/block/sda/device/rescan\n"
                    "• Обмеження: користувач НЕ може створювати нові\n"
                    "  екземпляри об'єктів ядра через файлові виклики",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    # Роздільна лінія між панелями
    p.append(line(590, 35, 590, 575, color=MUTED, sw=1.5, dash="6,6"))

    # Права панель (configfs)
    p.append(fitbox(620, 100, 510, 110,
                    "1. Модуль реєструє підсистему configfs\n"
                    "• configfs_register_subsystem()\n"
                    "• Створюється порожній каталог у /sys/kernel/config/\n"
                    "• Модуль очікує дій простору користувача",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(875, 210, 875, 245, color=FIELD, sw=2))

    p.append(fitbox(620, 245, 510, 110,
                    "2. Юзерспейс виконує mkdir\n"
                    "• mkdir /sys/kernel/config/target/core\n"
                    "• VFS прехоплює vfs_mkdir() ──► configfs_mkdir()\n"
                    "• Викликається zmake_group() / make_item()",
                    size=13, fill=PURPLE_FILL, stroke=NEG))

    p.append(arrow(875, 355, 875, 390, color=FIELD, sw=2))

    p.append(fitbox(620, 390, 510, 170,
                    "3. Динамічне створення та знищення\n"
                    "• Ядро виділяє пам'ять під новий config_item\n"
                    "• Юзерспейс налаштовує параметри та symlink\n"
                    "• Виклик rmdir видаляє ядерний об'єкт:\n"
                    "  drop_item() ──► refcount == 0 ──► release()",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'configfs-vs-sysfs.svg'), W, H, *p)


# ── 2. Дерево структур та зв'язок із kernfs/VFS ──────────────────────────────────
def fig_configfs_hierarchy():
    W, H = 1180, 640
    p = []

    p.append(rect(20, 20, 1140, 600, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(text(280, 50, "ПРОСТІР ЯДРА (Контекст configfs)", size=16, bold=True, color=NEG))
    p.append(text(900, 50, "ДЕРЕВО VFS (/sys/kernel/config/)", size=16, bold=True, color=POS))
    p.append(line(580, 30, 580, 600, color=MUTED, sw=1.5, dash="6,6"))

    # 1. configfs_subsystem
    p.append(fitbox(40, 80, 510, 110,
                    "struct configfs_subsystem\n"
                    "• struct config_group su_group (коренева група)\n"
                    "• struct mutex su_mutex (синхронізація дерев)\n"
                    "• Реєстрація: configfs_register_subsystem()",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    p.append(arrow(295, 190, 295, 225, color=LINE, sw=2))
    p.append(text(310, 210, "вміщує групу", size=11, color=MUTED))

    # 2. struct config_group
    p.append(fitbox(40, 225, 510, 130,
                    "struct config_group\n"
                    "• struct config_item cg_item (базовий атом)\n"
                    "• struct list_head cg_children (список дочірніх)\n"
                    "• struct configfs_group_operations *cg_ops\n"
                    "   └─ make_item(), make_group(), drop_item()",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.5))

    p.append(arrow(295, 355, 295, 390, color=LINE, sw=2))
    p.append(text(310, 375, "базовий атом", size=11, color=MUTED))

    # 3. struct config_item & cit
    p.append(fitbox(40, 390, 510, 190,
                    "struct config_item & struct config_item_type\n"
                    "• ci_name: ім'я елемента в дерево каталогів\n"
                    "• ci_kref: refcount_t (лічильник посилань)\n"
                    "• ci_type (cit): таблиця методів config_item_type\n"
                    "   ├─ ct_item_ops: release(), allow_link(), drop_link()\n"
                    "   └─ ct_attrs: масив атрибутів configfs_attribute\n"
                    "       └─ show(), store() через container_of()",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # Права сторона (VFS / kernfs)
    p.append(fitbox(610, 80, 520, 100,
                    "Каталог підсистеми у VFS\n"
                    "/sys/kernel/config/my_subsys/\n"
                    "(створений під час завантаження модуля)",
                    size=13, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(550, 130, 610, 130, color=NEG, sw=2))

    p.append(fitbox(610, 235, 520, 110,
                    "Підкаталог групи у VFS\n"
                    "/sys/kernel/config/my_subsys/my_group/\n"
                    "(створений користувачем через mkdir)",
                    size=13, fill=WARM_FILL, stroke=LINE))

    p.append(arrow(550, 290, 610, 290, color=LINE, sw=2))

    p.append(fitbox(610, 400, 520, 180,
                    "Вузол елемента та атрибути у VFS\n"
                    "/sys/kernel/config/my_subsys/my_group/item_1/\n"
                    "├── attr_enabled  (0644, show/store)\n"
                    "├── attr_target   (0444, show)\n"
                    "└── link_to_dev   ──► symbolic link\n"
                    "    (створений через ln -s, викликає allow_link)",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(550, 485, 610, 485, color=FIELD, sw=2))

    render(os.path.join(IMG, 'configfs-item-group-hierarchy.svg'), W, H, *p)


# ── 3. Послідовність подій mkdir та rmdir ─────────────────────────────────────────
def fig_configfs_lifecycle():
    W, H = 1180, 620
    p = []

    p.append(rect(20, 20, 1140, 580, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(rect(40, 35, 530, 45, fill=GREEN_FILL, stroke=FIELD, rx=6))
    p.append(text(305, 63, "Створення об'єкта: mkdir node_1", size=16, bold=True, color=FIELD))

    p.append(rect(610, 35, 530, 45, fill=RED_FILL, stroke=NEG, rx=6))
    p.append(text(875, 63, "Знищення об'єкта: rmdir node_1", size=16, bold=True, color=NEG))

    p.append(line(590, 35, 590, 575, color=MUTED, sw=1.5, dash="6,6"))

    # Ліва колонка: mkdir
    p.append(fitbox(50, 100, 510, 95,
                    "1. Юзерспейс: mkdir /sys/kernel/config/.../node_1\n"
                    "Системний виклик sys_mkdir() звертається до VFS\n"
                    "і викликає inode_operations->mkdir() у configfs.",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(305, 195, 305, 225, color=LINE, sw=2))

    p.append(fitbox(50, 225, 510, 110,
                    "2. Виклик make_item() / make_group()\n"
                    "Драйвер виділяє пам'ять: kzalloc(sizeof(*my_item))\n"
                    "Ініціалізація: config_item_init_type_name()\n"
                    "Встановлюється лічильник ci_kref = 1.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(305, 335, 305, 365, color=LINE, sw=2))

    p.append(fitbox(50, 365, 510, 175,
                    "3. Зв'язування з VFS та kernfs\n"
                    "configfs створює вузол kernfs_node і dentry.\n"
                    "Створюються файли атрибутів (ct_attrs).\n"
                    "Повертається 0 (успіх) у простір користувача.\n"
                    "Об'єкт повністю готовий до роботи.",
                    size=12, fill=WARM_FILL, stroke=LINE))

    # Права колонка: rmdir
    p.append(fitbox(620, 100, 510, 95,
                    "1. Юзерспейс: rmdir /sys/kernel/config/.../node_1\n"
                    "Системний виклик sys_rmdir() передає управління\n"
                    "до configfs_rmdir() у шарі VFS.",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(875, 195, 875, 225, color=NEG, sw=2))

    p.append(fitbox(620, 225, 510, 110,
                    "2. Перевірка залежностей та drop_item()\n"
                    "configfs перевіряє відсутність симлінків та вкладених груп.\n"
                    "Викликається group_ops->drop_item().\n"
                    "Драйвер відключає об'єкт від активної роботи.",
                    size=12, fill=PURPLE_FILL, stroke=NEG))

    p.append(arrow(875, 335, 875, 365, color=NEG, sw=2))

    p.append(fitbox(620, 365, 510, 175,
                    "3. Зменшення kref та release()\n"
                    "config_item_put(item) ──► refcount зменшується.\n"
                    "Коли ci_kref досягає 0 ──► викликається release().\n"
                    "Зворотний виклик release() виконує kfree(my_item).\n"
                    "Пам'ять ядра безпечно звільняється.",
                    size=12, fill=RED_FILL, stroke=NEG))

    render(os.path.join(IMG, 'configfs-lifecycle-events.svg'), W, H, *p)


if __name__ == '__main__':
    fig_configfs_vs_sysfs()
    fig_configfs_hierarchy()
    fig_configfs_lifecycle()
    print("Figures generated successfully.")
