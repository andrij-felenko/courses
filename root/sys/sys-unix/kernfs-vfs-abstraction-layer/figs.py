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


# ── 1. Архітектура kernfs та розвантаження VFS ─────────────────────────────
def fig_kernfs_vfs_architecture():
    W, H = 1200, 680
    p = []

    # Рамка фону
    p.append(rect(20, 20, 1160, 640, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # Заголовки шарів
    p.append(fitbox(40, 40, 1120, 50, "АРХІТЕКТУРНЕ РОЗДІЛЕННЯ VFS ТА КЕРУВАННЯ ВУЗЛАМИ KERNFS", size=15, bold=True, fill=WARM_FILL))

    # Верхній шар: VFS (Простір системних викликів)
    p.append(fitbox(50, 110, 1100, 140,
                    "Шар VFS (Virtual Filesystem Switch)\n"
                    "• Об'єкти dentry (~192 B) та inode (~600 B) створюються ЛІНИВО (On-Demand) при відкритті або lookup\n"
                    "• Очищаються з пам'яті під тиском VFS shrinker (dcache/icache prune) без втрати структури деревоподібної ФС\n"
                    "• Операції: open(), read(), write(), readdir(), stat() через VFS file_operations та inode_operations",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    # Стрілка між VFS та kernfs
    p.append(arrow(600, 250, 600, 290, color=LINE, sw=2.5))
    p.append(text(615, 273, "динамічний зв'язок за вимогою (kernfs_iop_lookup / kernfs_get_inode)", size=11, color=MUTED, anchor="start"))

    # Середній шар: kernfs (Центральний шар абстракції)
    p.append(fitbox(50, 290, 1100, 220,
                    "Ядро абстракції: kernfs (struct kernfs_root / struct kernfs_node)\n"
                    "• Єдине джерело правди у пам'яті: компактні вузли kernfs_node (128 B на x86_64) живуть у RAM постійно\n"
                    "• Дочірні вузли впорядковано у червоно-чорне дерево (rb_node) для швидкого пошуку за O(log N)\n"
                    "• Активний лічильник посилань (atomic_t active) та kernfs_drain() усувають гонитви при гарячому вилученні\n"
                    "• Ліниве виділення метаданих: атрибути iattr (права, uid/gid, timestamps) створюються лише при chmod/chown",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=2.0))

    # Стрілки від kernfs до підсистем
    p.append(arrow(250, 510, 250, 550, color=LINE, sw=2))
    p.append(arrow(600, 510, 600, 550, color=LINE, sw=2))
    p.append(arrow(950, 510, 950, 550, color=LINE, sw=2))

    # Нижній шар: Підсистеми ядра
    p.append(fitbox(50, 550, 340, 90,
                    "Підсистема sysfs\n"
                    "• kobject->sd вказує на kernfs_node\n"
                    "• Обгортка sysfs_ops -> kernfs_ops",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    p.append(fitbox(430, 550, 340, 90,
                    "Підсистема cgroup v2\n"
                    "• cgroup_root будується на kernfs_root\n"
                    "• Єдине ієрархічне дерево керування",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    p.append(fitbox(810, 550, 340, 90,
                    "Власні псевдо-ФС ядра\n"
                    "• Створення через kernfs_create_root()\n"
                    "• Легковаговий віртуальний інтерфейс",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'kernfs-vfs-architecture.svg'), W, H, *p)


# ── 2. Життєвий цикл вузла та механізм active / kernfs_drain ─────────────
def fig_kernfs_node_lifecycle():
    W, H = 1200, 620
    p = []

    p.append(rect(20, 20, 1160, 580, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(40, 40, 1120, 50, "БЕЗПЕКА ГАРЯЧОГО ВІДКЛЮЧЕННЯ: АКТИВНИЙ ЛІЧИЛЬНИК ТА KERNFS_DRAIN()", size=15, bold=True, fill=WARM_FILL))

    # 3 Фази життєвого циклу
    # Фаза 1: Нормальна робота
    p.append(fitbox(50, 110, 340, 460,
                    "1. Нормальне виконання\n(Активний стан)\n\n"
                    "• VFS отримує запит read/write\n\n"
                    "• Викликається kernfs_get_active(kn):\n"
                    "  - Перевіряється знак atomic_t active\n"
                    "  - Збільшується atomic_t active\n\n"
                    "• Виконується метод драйвера:\n"
                    "  kernfs_ops->seq_show() / write()\n\n"
                    "• Після завершення:\n"
                    "  kernfs_put_active(kn)\n"
                    "  (зменшує active)",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(arrow(390, 340, 430, 340, color=LINE, sw=2))

    # Фаза 2: Гаряче відключення
    p.append(fitbox(430, 110, 340, 460,
                    "2. Ініціація вилучення\n(kernfs_remove / drain)\n\n"
                    "• Драйвер/пристрій відключається\n"
                    "  та викликає kernfs_remove(kn)\n\n"
                    "• Викликається kernfs_drain(kn):\n"
                    "  - Додається від'ємне зміщення\n"
                    "    KN_DEACTIVATED_BIAS = INT_MIN + 1\n"
                    "  - Нові kernfs_get_active() повертають NULL, VFS віддає -ENODEV\n"
                    "  - Потік БЛОКУЄТЬСЯ (wait_event), доки\n"
                    "    active не впаде назад до зміщення",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.5))

    p.append(arrow(770, 340, 810, 340, color=LINE, sw=2))

    # Фаза 3: Безпечне вилучення
    p.append(fitbox(810, 110, 340, 460,
                    "3. Завершення та очищення\n(Звільнення ресурсів)\n\n"
                    "• Останній метод у польоті викликає\n"
                    "  kernfs_put_active(): active впало\n"
                    "  назад до KN_DEACTIVATED_BIAS\n\n"
                    "• kernfs_drain() розблоковується\n"
                    "  та повертає керування драйверу\n\n"
                    "• Драйвер БЕЗПЕЧНО виконує kfree()\n"
                    "  для своїх внутрішніх структур!\n\n"
                    "• Гарантія 100%: жоден потік\n"
                    "  більше НЕ виконає код драйвера",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    render(os.path.join(IMG, 'kernfs-node-lifecycle.svg'), W, H, *p)


# ── 3. Внутрішня структура kernfs_node та червоно-чорне дерево ─────────────
def fig_kernfs_rb_tree_structure():
    W, H = 1200, 600
    p = []

    p.append(rect(20, 20, 1160, 560, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(40, 40, 1120, 50, "ОРГАНІЗАЦІЯ ДОЧІРНІХ ВУЗЛІВ У ЧЕРВОНО-ЧОРНЕ ДЕРЕВО ТА ЛІНИВІ АТРИБУТИ", size=15, bold=True, fill=WARM_FILL))

    # Батьківський каталог
    p.append(fitbox(50, 110, 1100, 110,
                    "Батьківський каталог kernfs_node (KERNFS_DIR, наприклад /sys/devices/)\n"
                    "• kn->dir.children : корінь червоно-чорного дерева (struct rb_root)\n"
                    "• kn->name : ім'я каталогу   • kn->priv : вказівник на об'єкт підсистеми\n"
                    "• kn->ns : вказівник на простір імен (namespace tag, наприклад netns)",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    p.append(arrow(600, 220, 600, 260, color=LINE, sw=2))

    # Дочірні вузли в rb-tree
    p.append(fitbox(50, 260, 340, 150,
                    "Дочірній вузол (rb_node)\n"
                    "kernfs_node (\"cpu0\")\n"
                    "• type: KERNFS_DIR\n"
                    "• hash = kernfs_name_hash(\"cpu0\")\n"
                    "• rb_left / rb_right",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(430, 260, 340, 150,
                    "Дочірній вузол (rb_node)\n"
                    "kernfs_node (\"uevent\")\n"
                    "• type: KERNFS_FILE\n"
                    "• hash = kernfs_name_hash(\"uevent\")\n"
                    "• attr: show/store ops",
                    size=12, fill=WARM_FILL, stroke=LINE))

    p.append(fitbox(810, 260, 340, 150,
                    "Дочірній вузол (rb_node)\n"
                    "kernfs_node (\"subsystem\")\n"
                    "• type: KERNFS_LINK\n"
                    "• hash = kernfs_name_hash(\"subsystem\")\n"
                    "• target_kn: вказівник",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    # Нижня частина: Ліниве виділення iattr
    p.append(fitbox(50, 440, 1100, 110,
                    "Оптимізація пам'яті: Ліниве виділення атрибутів struct kernfs_iattrs\n"
                    "• kn->iattr == NULL за замовчуванням: права mode (0644/0444), uid=0, gid=0 та часові мітки обчислюються на льоту!\n"
                    "• Динамічне виділення iattr відбувається ЛИШЕ при явному виклику chmod(), chown() або utimes()\n"
                    "• Економія: знімає понад сотню байтів додаткової пам'яті з 99,9 % стандартних віртуальних файлів ядра",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'kernfs-rb-tree-structure.svg'), W, H, *p)


if __name__ == '__main__':
    fig_kernfs_vfs_architecture()
    fig_kernfs_node_lifecycle()
    fig_kernfs_rb_tree_structure()
    print("Figures generated successfully.")
