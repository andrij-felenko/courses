# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"
DARK_GREY = "#eceff1"

def save_fig(name, p, w, h):
    path = os.path.join(IMG, name)
    render(path, w, h, *p)
    print(f"Generated {name}")

# ── 1. Архітектура sysctl ───────────────────────────────────────────────────
def fig_sysctl_architecture():
    W, H = 1200, 720
    p = []

    p.append(rect(20, 20, 1160, 680, fill="#ffffff", stroke="#cfd8dc", rx=10))

    # Зони
    p.append(rect(40, 50, 1120, 190, fill=BLUE_FILL, stroke="#90caf9", rx=8))
    p.append(text(60, 80, "ПРОСТІР КОРИСТУВАЧА (USERSPACE)", size=14, bold=True, color="#1565c0", anchor="start"))

    p.append(rect(40, 260, 1120, 420, fill=GREEN_FILL, stroke="#a5d6a7", rx=8))
    p.append(text(60, 290, "ПРОСТІР ЯДРА (KERNELSPACE)", size=14, bold=True, color="#2e7d32", anchor="start"))

    # Блоки користувача
    frag1, w1, h1 = textbox(200, 140, ["Утиліта sysctl(8)", "sysctl -w net.ipv4.ip_forward=1"], fill="#ffffff", stroke="#1565c0", rx=6)
    p.append(frag1)

    frag2, w2, h2 = textbox(600, 140, ["Файлові виклики", "open/read/write(\"/proc/sys/...\")"], fill="#ffffff", stroke="#1565c0", rx=6)
    p.append(frag2)

    frag3, w3, h3 = textbox(960, 140, ["Файли конфігурації", "/etc/sysctl.d/*.conf"], fill="#ffffff", stroke="#1565c0", rx=6)
    p.append(frag3)

    # Стрілки з юзерспейсу
    p.append(arrow(960, 190, 200, 190, color="#1565c0", sw=2))
    p.append(text(580, 210, "завантаження при старті (sysctl --system)", size=12, color="#1565c0"))

    p.append(arrow(200, 190, 600, 190, color="#1565c0", sw=2))
    p.append(arrow(600, 190, 600, 320, color="#1565c0", sw=2))
    p.append(text(620, 245, "системні виклики VFS", size=12, color="#1565c0", anchor="start"))

    # Блоки ядра
    frag4, w4, h4 = textbox(300, 370, ["Віртуальна ФС procfs", "Дерево каталогів /proc/sys/"], fill=DARK_GREY, stroke="#37474f", rx=6)
    p.append(frag4)

    frag5, w5, h5 = textbox(750, 370, ["Дерево реєстрації sysctl", "Таблиці struct ctl_table_header"], fill=WARM_FILL, stroke="#ffb74d", rx=6)
    p.append(frag5)

    frag6, w6, h6 = textbox(300, 530, ["Обробник VFS read/write", "proc_sys_read() / proc_sys_write()"], fill="#ffffff", stroke="#2e7d32", rx=6)
    p.append(frag6)

    frag7, w7, h7 = textbox(750, 530, ["Власний handler ctl_table", "proc_dointvec() / proc_dostring()"], fill=RED_FILL, stroke="#e57373", rx=6)
    p.append(frag7)

    frag8, w8, h8 = textbox(750, 640, ["Змінна в пам'яті ядра", "sysctl_net_ipv4_ipv4_forward"], fill="#ffffff", stroke="#2e7d32", rx=6)
    p.append(frag8)

    # Зв'язки ядра
    p.append(arrow(600, 370, 480, 370, color="#37474f", sw=2))
    p.append(arrow(300, 420, 300, 480, color="#2e7d32", sw=2))
    p.append(arrow(750, 420, 750, 480, color="#f57c00", sw=2))
    p.append(arrow(460, 530, 570, 530, color="#2e7d32", sw=2))
    p.append(text(515, 515, "перевірка прав та виклик", size=11, color="#2e7d32"))
    p.append(arrow(750, 580, 750, 610, color="#c62828", sw=2))
    p.append(text(765, 595, "модифікація бітів/числа", size=11, color="#c62828", anchor="start"))

    save_fig("sysctl-architecture.svg", p, W, H)

# ── 2. Порівняння /proc/sys, /proc та /sys ──────────────────────────────────
def fig_proc_vs_sysfs():
    W, H = 1200, 600
    p = []

    p.append(rect(20, 20, 1160, 560, fill="#ffffff", stroke="#cfd8dc", rx=10))

    # Три колонки
    c1x, c1w = 50, 340
    c2x, c2w = 430, 340
    c3x, c3w = 810, 340

    # Колонка 1: /proc/sys
    p.append(rect(c1x, 50, c1w, 500, fill=BLUE_FILL, stroke="#90caf9", rx=8))
    p.append(text(c1x + c1w/2, 90, "/proc/sys", size=18, bold=True, color="#1565c0"))
    p.append(text(c1x + c1w/2, 115, "Глобальний тюнінг ядра", size=13, color="#546e7a"))

    f1, _, _ = textbox(c1x + c1w/2, 240, [
        "Призначення:",
        "Динамічна зміна параметрів",
        "роботи підсистем ядра",
        "(мережі, пам'яті, ФС)",
        "",
        "Формат даних:",
        "Простий текст/числа",
        "(одне чи кілька чисел у рядку)",
        "",
        "Головні піддерева:",
        "/proc/sys/net/, /proc/sys/vm/",
        "/proc/sys/kernel/, /proc/sys/fs/"
    ], fill="#ffffff", stroke="#90caf9", rx=6)
    p.append(f1)

    # Колонка 2: /proc (решта)
    p.append(rect(c2x, 50, c2w, 500, fill=GREEN_FILL, stroke="#a5d6a7", rx=8))
    p.append(text(c2x + c2w/2, 90, "/proc (procfs)", size=18, bold=True, color="#2e7d32"))
    p.append(text(c2x + c2w/2, 115, "Стан процесів та системи", size=13, color="#546e7a"))

    f2, _, _ = textbox(c2x + c2w/2, 240, [
        "Призначення:",
        "Відображення стану процесів",
        "та загальної статистики ядра",
        "(пам'ять, CPU, переривання)",
        "",
        "Формат даних:",
        "Текстові звіти,",
        "форматовані таблиці та списки",
        "",
        "Головні елементи:",
        "/proc/[pid]/status, /proc/meminfo",
        "/proc/cpuinfo, /proc/stat"
    ], fill="#ffffff", stroke="#a5d6a7", rx=6)
    p.append(f2)

    # Колонка 3: /sys (sysfs)
    p.append(rect(c3x, 50, c3w, 500, fill=WARM_FILL, stroke="#ffb74d", rx=8))
    p.append(text(c3x + c3w/2, 90, "/sys (sysfs)", size=18, bold=True, color="#e65100"))
    p.append(text(c3x + c3w/2, 115, "Модель пристроїв та шин", size=13, color="#546e7a"))

    f3, _, _ = textbox(c3x + c3w/2, 240, [
        "Призначення:",
        "Ієрархія об'єктів kobject:",
        "пристрої, драйвери, шини,",
        "живлення, cgroups v2",
        "",
        "Формат даних:",
        "Один атрибут — один файл",
        "(суворий канон sysfs)",
        "",
        "Головні піддерева:",
        "/sys/devices/, /sys/bus/",
        "/sys/class/, /sys/fs/cgroup/"
    ], fill="#ffffff", stroke="#ffb74d", rx=6)
    p.append(f3)

    save_fig("proc-vs-sysfs.svg", p, W, H)

# ── 3. Ізоляція sysctl в Namespaces ──────────────────────────────────────────
def fig_sysctl_namespace_isolation():
    W, H = 1200, 650
    p = []

    p.append(rect(20, 20, 1160, 610, fill="#ffffff", stroke="#cfd8dc", rx=10))

    # Хост / Initial ns
    p.append(rect(40, 50, 1120, 240, fill=GREY_FILL, stroke="#78909c", rx=8))
    p.append(text(60, 80, "ПОЧАТКОВИЙ ПРОСТІР ІМЕН (INITIAL USER / NETWORK NAMESPACE)", size=14, bold=True, color="#37474f", anchor="start"))

    f_host_glob, _, _ = textbox(300, 170, [
        "Глобальні параметри sysctl",
        "(потрібен CAP_SYS_ADMIN у хості)",
        "",
        "fs.file-max, vm.swappiness",
        "kernel.pid_max, kernel.shmmax"
    ], fill="#ffffff", stroke="#37474f", rx=6)
    p.append(f_host_glob)

    f_host_net, _, _ = textbox(850, 170, [
        "Хостовий мережевий простір (netns)",
        "net.ipv4.ip_forward = 1",
        "net.core.somaxconn = 4096"
    ], fill=BLUE_FILL, stroke="#1565c0", rx=6)
    p.append(f_host_net)

    # Контейнери / Ізольовані ns
    p.append(rect(40, 320, 540, 280, fill=GREEN_FILL, stroke="#81c784", rx=8))
    p.append(text(60, 350, "КОНТЕЙНЕР А (Network NS #1)", size=14, bold=True, color="#2e7d32", anchor="start"))

    f_ct1, _, _ = textbox(310, 460, [
        "Ізольовані параметри netns",
        "(потрібен CAP_NET_ADMIN у Container NS)",
        "",
        "net.ipv4.ip_forward = 0",
        "net.core.somaxconn = 1024",
        "net.ipv4.tcp_rmem = 4096 87380..."
    ], fill="#ffffff", stroke="#2e7d32", rx=6)
    p.append(f_ct1)

    p.append(rect(620, 320, 540, 280, fill=WARM_FILL, stroke="#ffb74d", rx=8))
    p.append(text(640, 350, "КОНТЕЙНЕР Б (Network NS #2)", size=14, bold=True, color="#e65100", anchor="start"))

    f_ct2, _, _ = textbox(890, 460, [
        "Ізольовані параметри netns",
        "(потрібен CAP_NET_ADMIN у Container NS)",
        "",
        "net.ipv4.ip_forward = 1",
        "net.core.somaxconn = 8192",
        "net.ipv4.tcp_rmem = 8192 174760..."
    ], fill="#ffffff", stroke="#e65100", rx=6)
    p.append(f_ct2)

    # Заборона зміни глобальних sysctl із контейнера
    p.append(line(310, 380, 300, 250, color="#d32f2f", sw=2, dash="5,5"))
    p.append(text(190, 290, "EACCES / EPERM (спроба міняти fs.file-max)", size=11, color="#d32f2f", bold=True))

    save_fig("sysctl-namespace-isolation.svg", p, W, H)

if __name__ == "__main__":
    fig_sysctl_architecture()
    fig_proc_vs_sysfs()
    fig_sysctl_namespace_isolation()
