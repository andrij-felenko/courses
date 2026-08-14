import os
import sys

# Додаємо scripts/ до шляху пошуку для імпорту svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_proc_structure(img_dir):
    path = os.path.join(img_dir, "proc-structure.svg")
    w, h = 840, 480

    bg = svgkit.rect(0, 0, w, h, fill="#ffffff", stroke="none")

    # Вузли першого рівня (Root /proc)
    r_proc = svgkit.fitbox(340, 30, 160, 40, "/proc", size=16, bold=True, fill="#e3f2fd", stroke="#1e88e5", sw=2)

    # Лінії від /proc до трьох блоків
    l1 = svgkit.line(420, 70, 140, 120, color="#90caf9", sw=2)
    l2 = svgkit.line(420, 70, 420, 120, color="#90caf9", sw=2)
    l3 = svgkit.line(420, 70, 700, 120, color="#90caf9", sw=2)

    # Основні гілки (верхні рамки)
    box_pid = svgkit.fitbox(50, 120, 180, 45, "/proc/[PID]/\n(Процеси)", size=14, bold=True, fill="#e8f5e9", stroke="#2e7d32", sw=2)
    box_sys = svgkit.fitbox(330, 120, 180, 45, "/proc/sys/\n(Параметри ядра)", size=14, bold=True, fill="#fff3e0", stroke="#e65100", sw=2)
    box_stat = svgkit.fitbox(610, 120, 180, 45, "Глобальний стан\n(/proc/meminfo, cpuinfo)", size=13, bold=True, fill="#f3e5f5", stroke="#7b1fa2", sw=2)

    # 1. Гілка /proc/[PID]
    # Магістральна лінія ліворуч від блоків
    trunk_pid_down = svgkit.line(140, 165, 140, 195, color="#a5d6a7", sw=1.5)
    trunk_pid_left = svgkit.line(140, 195, 30, 195, color="#a5d6a7", sw=1.5)
    trunk_pid_vert = svgkit.line(30, 195, 30, 425, color="#a5d6a7", sw=1.5)

    pid_items = ["cmdline, environ", "status, stat, statm", "maps, smaps", "fd/, fdinfo/", "ns/, task/"]
    pid_nodes = []
    pid_branches = []
    for i, item in enumerate(pid_items):
        y = 210 + i * 45
        branch = svgkit.line(30, y + 17, 50, y + 17, color="#a5d6a7", sw=1.5)
        pid_branches.append(branch)
        node = svgkit.fitbox(50, y, 180, 34, item, size=12, fill="#ffffff", stroke="#43a047", sw=1.2)
        pid_nodes.append(node)

    # 2. Гілка /proc/sys
    trunk_sys_down = svgkit.line(420, 165, 420, 195, color="#ffcc80", sw=1.5)
    trunk_sys_left = svgkit.line(420, 195, 310, 195, color="#ffcc80", sw=1.5)
    trunk_sys_vert = svgkit.line(310, 195, 310, 375, color="#ffcc80", sw=1.5)

    sys_items = ["kernel/\n(ostype, pid_max)", "vm/\n(swappiness, drop_caches)", "net/\n(ipv4/ip_forward)"]
    sys_nodes = []
    sys_branches = []
    for i, item in enumerate(sys_items):
        y = 210 + i * 70
        branch = svgkit.line(310, y + 21, 330, y + 21, color="#ffcc80", sw=1.5)
        sys_branches.append(branch)
        node = svgkit.fitbox(330, y, 180, 42, item, size=12, fill="#ffffff", stroke="#fb8c00", sw=1.2)
        sys_nodes.append(node)

    # 3. Гілка системних файлів
    trunk_stat_down = svgkit.line(700, 165, 700, 195, color="#ce93d8", sw=1.5)
    trunk_stat_left = svgkit.line(700, 195, 590, 195, color="#ce93d8", sw=1.5)
    trunk_stat_vert = svgkit.line(590, 195, 590, 375, color="#ce93d8", sw=1.5)

    stat_items = ["/proc/meminfo\n(Пам'ять системи)", "/proc/stat\n(Метрики CPU та тиків)", "/proc/self/\n(Symlink на свій PID)"]
    stat_nodes = []
    stat_branches = []
    for i, item in enumerate(stat_items):
        y = 210 + i * 70
        branch = svgkit.line(590, y + 21, 610, y + 21, color="#ce93d8", sw=1.5)
        stat_branches.append(branch)
        node = svgkit.fitbox(610, y, 180, 42, item, size=12, fill="#ffffff", stroke="#8e24aa", sw=1.2)
        stat_nodes.append(node)

    all_frags = [bg, l1, l2, l3, r_proc, box_pid, box_sys, box_stat,
                 trunk_pid_down, trunk_pid_left, trunk_pid_vert,
                 trunk_sys_down, trunk_sys_left, trunk_sys_vert,
                 trunk_stat_down, trunk_stat_left, trunk_stat_vert]

    all_frags.extend(pid_branches)
    all_frags.extend(pid_nodes)
    all_frags.extend(sys_branches)
    all_frags.extend(sys_nodes)
    all_frags.extend(stat_branches)
    all_frags.extend(stat_nodes)

    svgkit.render(path, w, h, *all_frags, title=None)
    print(f"Згенеровано: {path}")

def render_proc_vfs_flow(img_dir):
    path = os.path.join(img_dir, "proc-vfs-flow.svg")
    w, h = 840, 340

    bg = svgkit.rect(0, 0, w, h, fill="#ffffff", stroke="none")

    # 4 етапи виконання read() на файлі procfs
    b1 = svgkit.fitbox(30, 90, 160, 100, "Користувацький простір\n\nread(fd, buf, size)\n(cat /proc/meminfo)", size=12, bold=True, fill="#e3f2fd", stroke="#1976d2", sw=1.8)
    a1 = svgkit.arrow(190, 140, 230, 140, color="#1976d2", sw=2)

    b2 = svgkit.fitbox(230, 90, 160, 100, "Шар VFS ядра\n\nvfs_read()\nПошук proc_dir_entry\nта proc_fops", size=12, bold=True, fill="#fff3e0", stroke="#f57c00", sw=1.8)
    a2 = svgkit.arrow(390, 140, 430, 140, color="#f57c00", sw=2)

    b3 = svgkit.fitbox(430, 90, 160, 100, "Механізм seq_file\n\nseq_read()\nВиклик show()\nФорматування тексту", size=12, bold=True, fill="#e8f5e9", stroke="#388e3c", sw=1.8)
    a3 = svgkit.arrow(590, 140, 630, 140, color="#388e3c", sw=2)

    b4 = svgkit.fitbox(630, 90, 160, 100, "Підсистеми ядра\n\nЗбір статистик\n(si_meminfo)\ncopy_to_user()", size=12, bold=True, fill="#f3e5f5", stroke="#7b1fa2", sw=1.8)

    # Пояснювальний пояс знизу
    lbl = svgkit.fitbox(150, 240, 540, 45, "Дані не існують на диску: ядро створює текстовий потік у пам'яті під час виклику read()", size=13, italic=True, fill="#f4f6f8", stroke="#6b7280", sw=1)

    svgkit.render(path, w, h, bg, b1, a1, b2, a2, b3, a3, b4, lbl, title=None)
    print(f"Згенеровано: {path}")

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render_proc_structure(img_dir)
    render_proc_vfs_flow(img_dir)

if __name__ == "__main__":
    render()
