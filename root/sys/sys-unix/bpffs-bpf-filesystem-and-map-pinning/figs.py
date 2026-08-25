# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"
DARK_BLUE = "#1a237e"


def fig_bpffs_lifecycle():
    """Схема життєвого циклу об'єкта eBPF та лічильника посилань refcnt під час пінінгу."""
    W, H = 1400, 720
    p = []

    # Загальний фоновий блок
    p.append(rect(30, 30, 1340, 660, fill="#fafafa", stroke="#cfd8dc", sw=1.5, rx=8))

    # Сонце/Заголовок
    p.append(text(700, 60, "Життєвий цикл eBPF-об'єкта та лічильник refcnt при пінінгу у bpffs", size=18, bold=True, color="#1a237e"))

    # Етап 1: Створення мапи Процесом 1
    p.append(rect(60, 100, 380, 250, fill=BLUE, stroke="#1976d2", sw=2, rx=6))
    p.append(text(250, 130, "Етап 1: Створення об'єкта", size=15, bold=True, color="#0d47a1"))
    p.append(text(250, 160, "Процес 1 викликає bpf(BPF_MAP_CREATE)", size=13, color="#37474f"))
    p.append(rect(80, 185, 340, 75, fill="#ffffff", stroke="#90caf9", sw=1.5, rx=4))
    p.append(text(250, 210, "Kernel Heap: struct bpf_map", size=14, bold=True))
    p.append(text(250, 235, "refcnt = 1 (1 FD у Процесу 1)", size=13, bold=True, color="#2e7d32"))
    p.append(text(250, 320, "Об'єкт доступний лише Процесу 1", size=13, italic=True, color="#555555"))

    # Етап 2: Фіксація у bpffs
    p.append(rect(510, 100, 380, 250, fill=WARM, stroke="#f57c00", sw=2, rx=6))
    p.append(text(700, 130, "Етап 2: BPF_OBJ_PIN у bpffs", size=15, bold=True, color="#e65100"))
    p.append(text(700, 160, "bpf(BPF_OBJ_PIN, '/sys/fs/bpf/map')", size=13, color="#37474f"))
    p.append(rect(530, 185, 340, 75, fill="#ffffff", stroke="#ffcc80", sw=1.5, rx=4))
    p.append(text(700, 210, "VFS: struct inode у bpffs", size=14, bold=True))
    p.append(text(700, 235, "refcnt = 2 (1 FD + 1 VFS inode)", size=13, bold=True, color="#e65100"))
    p.append(text(700, 320, "Створено віртуальний файл у VFS", size=13, italic=True, color="#555555"))

    # Етап 3: Вихід Процесу 1
    p.append(rect(960, 100, 380, 250, fill=GREEN, stroke="#388e3c", sw=2, rx=6))
    p.append(text(1150, 130, "Етап 3: Вихід Процесу 1", size=15, bold=True, color="#1b5e20"))
    p.append(text(1150, 160, "Процес 1 завершується (exit/close)", size=13, color="#37474f"))
    p.append(rect(980, 185, 340, 75, fill="#ffffff", stroke="#a5d6a7", sw=1.5, rx=4))
    p.append(text(1150, 210, "FD закрито. VFS inode живе!", size=14, bold=True))
    p.append(text(1150, 235, "refcnt = 1 (0 FD + 1 VFS inode)", size=13, bold=True, color="#2e7d32"))
    p.append(text(1150, 320, "Об'єкт зберігається в пам'яті ядра", size=13, italic=True, color="#555555"))

    # Нижній ряд стрілок та етапів
    p.append(arrow(440, 225, 510, 225, color="#1976d2", sw=2))
    p.append(arrow(890, 225, 960, 225, color="#f57c00", sw=2))

    # Етап 4: Відкриття Процесом 2
    p.append(rect(60, 400, 580, 250, fill="#f3e5f5", stroke="#8e24aa", sw=2, rx=6))
    p.append(text(350, 430, "Етап 4: BPF_OBJ_GET Процесом 2", size=15, bold=True, color="#4a148c"))
    p.append(text(350, 460, "Процес 2 отримує FD за шляхом '/sys/fs/bpf/map'", size=13, color="#37474f"))
    p.append(rect(80, 485, 540, 75, fill="#ffffff", stroke="#ce93d8", sw=1.5, rx=4))
    p.append(text(350, 510, "Ядро відкриває VFS інод і створює новий FD", size=14, bold=True))
    p.append(text(350, 535, "refcnt = 2 (1 FD Процесу 2 + 1 VFS inode)", size=13, bold=True, color="#8e24aa"))
    p.append(text(350, 620, "Спільний доступ до стану мапи відновлено", size=13, italic=True, color="#555555"))

    # Етап 5: Unlink та видалення (RCU cleanup)
    p.append(rect(760, 400, 580, 250, fill=RED, stroke="#d32f2f", sw=2, rx=6))
    p.append(text(1050, 430, "Етап 5: Видалення файлу та RCU-очищення", size=15, bold=True, color="#b71c1c"))
    p.append(text(1050, 460, "Виконується unlink('/sys/fs/bpf/map') та close(FD)", size=13, color="#37474f"))
    p.append(rect(780, 485, 540, 75, fill="#ffffff", stroke="#ef9a9a", sw=1.5, rx=4))
    p.append(text(1050, 510, "inode видалено з VFS, всі FD закриті", size=14, bold=True))
    p.append(text(1050, 535, "refcnt = 0 -> bpf_map_free_deferred() (RCU)", size=13, bold=True, color="#c62828"))
    p.append(text(1050, 620, "Пам'ять ядра остаточно звільняється", size=13, italic=True, color="#555555"))

    p.append(arrow(640, 525, 760, 525, color="#8e24aa", sw=2))

    render(os.path.join(IMG, 'bpffs-lifecycle.svg'), W, H, *p)


def fig_bpffs_vfs_architecture():
    """Схема архітектури ядра: взаємодія VFS, системного виклику bpf() та драйвера bpffs."""
    W, H = 1420, 680
    p = []

    # Головний контейнер
    p.append(rect(30, 30, 1360, 620, fill="#f8f9fa", stroke="#b0bec5", sw=1.5, rx=8))

    # Зона User Space
    p.append(text(60, 65, "Простір користувача (User Space)", size=16, bold=True, color="#37474f"))
    p.append(rect(60, 85, 1300, 100, fill="#ffffff", stroke="#1565c0", sw=2, rx=6))
    p.append(text(250, 120, "Застосунки користувача (Cilium, bpftrace, libbpf)", size=15, bold=True))
    p.append(text(250, 155, "bpf_obj_pin(fd, path) / bpf_obj_get(path) / open() / unlink() / chmod()", size=14, italic=True, color="#455a64"))

    # Роздільна лінія між User та Kernel
    p.append(line(40, 210, 1380, 210, color="#d32f2f", dash="6 4", sw=2))
    p.append(text(60, 235, "Простір ядра (Kernel Space)", size=16, bold=True, color="#c62828"))

    # Блок 1: Системні виклики та VFS
    p.append(rect(60, 260, 390, 360, fill=BLUE, stroke="#1976d2", sw=2, rx=6))
    p.append(text(255, 290, "Шар VFS та системні виклики", size=16, bold=True, color="#0d47a1"))
    p.append(rect(80, 320, 350, 65, fill="#ffffff", stroke="#90caf9", sw=1.5, rx=4))
    p.append(text(255, 345, "sys_bpf(BPF_OBJ_PIN / GET)", size=14, bold=True))
    p.append(text(255, 368, "Обробка bpf_attr.pathname", size=13, color="#555555"))

    p.append(rect(80, 405, 350, 65, fill="#ffffff", stroke="#90caf9", sw=1.5, rx=4))
    p.append(text(255, 430, "VFS lookup & permission", size=14, bold=True))
    p.append(text(255, 453, "user_path_at() / inode_permission()", size=13, color="#555555"))

    p.append(rect(80, 490, 350, 110, fill="#ffffff", stroke="#90caf9", sw=1.5, rx=4))
    p.append(text(255, 515, "struct path & struct dentry", size=14, bold=True))
    p.append(text(255, 540, "Перевірка dir->i_op == &bpf_dir_iops", size=13, color="#37474f"))
    p.append(text(255, 565, "Контроль атрибутів mode/uid/gid", size=13, color="#37474f"))

    # Блок 2: Драйвер bpffs (kernel/bpf/inode.c)
    p.append(rect(510, 260, 410, 360, fill=WARM, stroke="#f57c00", sw=2, rx=6))
    p.append(text(715, 290, "Драйвер bpffs (kernel/bpf/inode.c)", size=16, bold=True, color="#e65100"))

    p.append(rect(530, 320, 370, 75, fill="#ffffff", stroke="#ffcc80", sw=1.5, rx=4))
    p.append(text(715, 345, "bpf_obj_do_pin() / bpf_mkobj_ops()", size=14, bold=True))
    p.append(text(715, 373, "Створення struct inode у bpf_fs", size=13, color="#555555"))

    p.append(rect(530, 415, 370, 75, fill="#ffffff", stroke="#ffcc80", sw=1.5, rx=4))
    p.append(text(715, 440, "inode->i_private = bpf_ptr", size=14, bold=True))
    p.append(text(715, 468, "Збереження покажчика на об'єкт BPF", size=13, color="#555555"))

    p.append(rect(530, 510, 370, 90, fill="#ffffff", stroke="#ffcc80", sw=1.5, rx=4))
    p.append(text(715, 535, "Оператори: bpf_dir_iops & bpffs_obj_fops", size=14, bold=True))
    p.append(text(715, 560, "bpf_destroy_inode() -> decrement refcnt", size=13, color="#37474f"))
    p.append(text(715, 580, "Захист від паралельних unlink", size=13, color="#37474f"))

    # Блок 3: Об'єкти ядра BPF Subsystem
    p.append(rect(970, 260, 390, 360, fill=GREEN, stroke="#2e7d32", sw=2, rx=6))
    p.append(text(1165, 290, "Об'єкти ядра підсистеми BPF", size=16, bold=True, color="#1b5e20"))

    p.append(rect(990, 320, 350, 65, fill="#ffffff", stroke="#81c784", sw=1.5, rx=4))
    p.append(text(1165, 345, "struct bpf_map", size=14, bold=True))
    p.append(text(1165, 368, "atomic64_t refcnt, map_ops", size=13, color="#555555"))

    p.append(rect(990, 405, 350, 65, fill="#ffffff", stroke="#81c784", sw=1.5, rx=4))
    p.append(text(1165, 430, "struct bpf_prog", size=14, bold=True))
    p.append(text(1165, 453, "insnsi, aux->refcnt (atomic64_t)", size=13, color="#555555"))

    p.append(rect(990, 490, 350, 110, fill="#ffffff", stroke="#81c784", sw=1.5, rx=4))
    p.append(text(1165, 515, "struct bpf_link", size=14, bold=True))
    p.append(text(1165, 540, "Зв'язок програми з хуком ядра", size=13, color="#37474f"))
    p.append(text(1165, 565, "bpf_iter_link / cgroup_link", size=13, color="#37474f"))

    # Стрілки з'єднань
    p.append(arrow(255, 185, 255, 260, color="#1565c0", sw=2))
    p.append(arrow(450, 355, 510, 355, color="#1976d2", sw=2))
    p.append(arrow(920, 357, 990, 357, color="#e65100", sw=2))
    p.append(arrow(920, 442, 990, 442, color="#e65100", sw=2))
    p.append(arrow(920, 545, 990, 545, color="#e65100", sw=2))

    render(os.path.join(IMG, 'bpffs-vfs-architecture.svg'), W, H, *p)


if __name__ == '__main__':
    fig_bpffs_lifecycle()
    fig_bpffs_vfs_architecture()
    print("Всі фігури для bpffs успішно згенеровано.")
