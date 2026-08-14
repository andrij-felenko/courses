# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

def generate_nspawn_architecture(img_dir):
    w, h = 840, 520
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Архітектура ізоляції systemd-nspawn у ядрі Linux", size=17, bold=True))

    # Host Kernel Layer (Bottom panel)
    frags.append(rect(30, 360, 780, 130, fill="#eef2f7", stroke="#34495e", sw=2, rx=8))
    frags.append(text(420, 382, "Ядро Linux (Kernel Primitives)", size=15, bold=True, color="#2c3e50"))
    
    # Kernel primitives boxes inside bottom panel
    p1 = fitbox(45, 400, 235, 75, "Namespaces\nCLONE_NEWPID · CLONE_NEWNS\nCLONE_NEWNET · CLONE_NEWUSER", size=12, fill="#ffffff", stroke="#2980b9")
    p2 = fitbox(295, 400, 240, 75, "Cgroups v2 & Security\nmachine.slice resource limits\nSeccomp & Capability Set", size=12, fill="#ffffff", stroke="#27ae60")
    p3 = fitbox(550, 400, 245, 75, "Virtual File System (VFS)\nID-mapped mounts · overlayfs\nprocfs/sysfs masking", size=12, fill="#ffffff", stroke="#8e44ad")
    frags.extend([p1, p2, p3])

    # Host Userspace (Middle Left panel)
    frags.append(rect(30, 60, 340, 270, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(200, 82, "Хостовий системний простір", size=14, bold=True, color="#2c3e50"))
    
    u1 = fitbox(50, 100, 300, 50, "systemd (PID 1 Host Init)\nМенеджер системних юнітів", size=12, fill="#ffffff", stroke="#7f8c8d")
    u2 = fitbox(50, 165, 300, 50, "systemd-machined\nСлужба реєстрації контейнерів/ВМ", size=12, fill="#ffffff", stroke="#2980b9")
    u3 = fitbox(50, 230, 300, 45, "machinectl CLI\nУправління контейнерами", size=12, fill="#ffffff", stroke="#16a085")
    u4 = fitbox(50, 285, 300, 35, "D-Bus (org.freedesktop.machine1)", size=11, fill="#eaf2f8", stroke="#2980b9")
    frags.extend([u1, u2, u3, u4])

    # Container Sandbox (Middle Right panel)
    frags.append(rect(410, 60, 400, 270, fill="#eafaf1", stroke="#27ae60", sw=2, rx=8))
    frags.append(text(610, 82, "Контейнерний сендбокс (nspawn)", size=14, bold=True, color="#1e8449"))

    c1 = fitbox(430, 100, 360, 45, "systemd-nspawn (Host Process)\nМенеджер запуску та ізоляції", size=12, fill="#ffffff", stroke="#27ae60")
    c2 = fitbox(430, 155, 360, 55, "Контейнерний PID 1 (systemd / PID 1 stub)\nВласне дерево процесів та послуг", size=12, fill="#ffffff", stroke="#16a085")
    c3 = fitbox(430, 220, 175, 95, "Ізольований VFS Root\n/proc (masked)\n/sys (read-only)\n/dev (devtmpfs subset)", size=11, fill="#ffffff", stroke="#8e44ad")
    c4 = fitbox(615, 220, 175, 95, "Мережа & Юзери\nhost0 (veth interface)\nUser NS (UID mapping)\nCap Bounding Set", size=11, fill="#ffffff", stroke="#d35400")
    frags.extend([c1, c2, c3, c4])

    # Arrows connecting components
    frags.append(arrow(350, 190, 430, 125, color="#2980b9", sw=2))
    frags.append(arrow(610, 145, 610, 155, color="#27ae60", sw=2))
    frags.append(arrow(200, 330, 160, 400, color="#34495e", sw=1.5))
    frags.append(arrow(610, 330, 670, 400, color="#27ae60", sw=1.5))

    out_path = os.path.join(img_dir, "nspawn-architecture.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def generate_chroot_vs_nspawn(img_dir):
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Порівняння межі ізоляції: chroot проти systemd-nspawn", size=17, bold=True))

    # Left box: chroot
    frags.append(rect(30, 60, 375, 370, fill="#fdf2e9", stroke="#e67e22", sw=2, rx=8))
    frags.append(text(217, 85, "Класичний chroot", size=15, bold=True, color="#d35400"))

    l1 = fitbox(45, 105, 345, 55, "Зміна лише кореня ВФС\n`struct path root` у `struct fs_struct`", size=12, fill="#ffffff", stroke="#e67e22")
    l2 = fitbox(45, 170, 345, 55, "Спільний PID Namespace\nБачить усі хостові процеси в /proc", size=12, fill="#ffffff", stroke="#c0392b")
    l3 = fitbox(45, 235, 345, 55, "Спільний мережевий стек\nПрямий доступ до сокетів та портів", size=12, fill="#ffffff", stroke="#c0392b")
    l4 = fitbox(45, 300, 345, 55, "Спільні пристрої та IPC\nНебезпека fchdir втечі та mknod", size=12, fill="#ffffff", stroke="#c0392b")
    l5 = fitbox(45, 365, 345, 50, "UID 0 = Хостовий root (без обмежень cgroups)", size=12, fill="#fbeee6", stroke="#c0392b")
    frags.extend([l1, l2, l3, l4, l5])

    # Right box: systemd-nspawn
    frags.append(rect(435, 60, 375, 370, fill="#eafaf1", stroke="#27ae60", sw=2, rx=8))
    frags.append(text(622, 85, "Контейнер systemd-nspawn", size=15, bold=True, color="#1e8449"))

    r1 = fitbox(450, 105, 345, 55, "Повна ізоляція Mount NS\nМаскування /proc, /sys та devtmpfs", size=12, fill="#ffffff", stroke="#27ae60")
    r2 = fitbox(450, 170, 345, 55, "Ізольований PID Namespace\nВласний PID 1 init (без доступу до хосту)", size=12, fill="#ffffff", stroke="#27ae60")
    r3 = fitbox(450, 235, 345, 55, "Приватна мережа (Network NS)\nveth пара, міст br0, порт-форвардинг", size=12, fill="#ffffff", stroke="#27ae60")
    r4 = fitbox(450, 300, 345, 55, "Обмеження Capability & Seccomp\nФільтрація небезпечних системних викликів", size=12, fill="#ffffff", stroke="#27ae60")
    r5 = fitbox(450, 365, 345, 50, "User NS + cgroups v2 (machine.slice)", size=12, fill="#e8f8f5", stroke="#16a085")
    frags.extend([r1, r2, r3, r4, r5])

    out_path = os.path.join(img_dir, "chroot-vs-nspawn.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def generate_nspawn_network_modes(img_dir):
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Мережеві режими systemd-nspawn", size=17, bold=True))

    # Top: Host Network Stack
    frags.append(rect(30, 55, 780, 75, fill="#f4f6f8", stroke="#34495e", sw=2, rx=8))
    frags.append(text(410, 75, "Мережевий стек хоста (Host Network Namespace)", size=14, bold=True, color="#2c3e50"))
    h_net = fitbox(50, 85, 740, 35, "Хостові інтерфейси: eth0 (192.168.1.50) · br0 (10.0.0.1) · systemd-networkd", size=12, fill="#ffffff", stroke="#7f8c8d")
    frags.append(h_net)

    # 3 Mode Columns below
    # Mode 1: Host Shared (Default)
    frags.append(rect(30, 155, 240, 280, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    frags.append(text(150, 180, "1. Загальний стек", size=13, bold=True, color="#d35400"))
    m1_1 = fitbox(42, 195, 216, 50, "Без прапорів мережі\n(Default / Direct)", size=11, fill="#ffffff", stroke="#f39c12")
    m1_2 = fitbox(42, 255, 216, 100, "Контейнер ділить eth0\nі всі сокети з хостом.\nМаксимальна швидкість,\nале відсутня ізоляція.", size=11, fill="#ffffff", stroke="#7f8c8d")
    m1_3 = fitbox(42, 365, 216, 55, "Конфлікти портів\nз хостовими службами", size=11, fill="#fbeee6", stroke="#c0392b")
    frags.extend([m1_1, m1_2, m1_3])

    # Mode 2: Private Network
    frags.append(rect(300, 155, 240, 280, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=8))
    frags.append(text(420, 180, "2. Приватна мережа", size=13, bold=True, color="#1b4f72"))
    m2_1 = fitbox(312, 195, 216, 50, "--private-network\n--port=8080:80", size=11, fill="#ffffff", stroke="#2980b9")
    m2_2 = fitbox(312, 255, 216, 100, "Окремий Network NS.\nЛише інтерфейс lo.\nДоступ ззовні тільки\nчерез проксі портів.", size=11, fill="#ffffff", stroke="#7f8c8d")
    m2_3 = fitbox(312, 365, 216, 55, "Повна локальна\nізоляція сокетів", size=11, fill="#e8f8f5", stroke="#27ae60")
    frags.extend([m2_1, m2_2, m2_3])

    # Mode 3: Virtual Ethernet / Bridge
    frags.append(rect(570, 155, 240, 280, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(690, 180, "3. veth пара / міст", size=13, bold=True, color="#1e8449"))
    m3_1 = fitbox(582, 195, 216, 50, "--network-veth\n--network-bridge=br0", size=11, fill="#ffffff", stroke="#27ae60")
    m3_2 = fitbox(582, 255, 216, 100, "Створюється veth пара:\nve-<name> на хості,\nhost0 у контейнері.\nАвто-DHCP в networkd.", size=11, fill="#ffffff", stroke="#7f8c8d")
    m3_3 = fitbox(582, 365, 216, 55, "Повноцінний L2/L3\nмережевий вузол", size=11, fill="#e8f8f5", stroke="#16a085")
    frags.extend([m3_1, m3_2, m3_3])

    # Connectors from top host box to 3 modes
    frags.append(arrow(150, 130, 150, 155, color="#f39c12", sw=1.5))
    frags.append(arrow(420, 130, 420, 155, color="#2980b9", sw=1.5))
    frags.append(arrow(690, 130, 690, 155, color="#27ae60", sw=1.5))

    out_path = os.path.join(img_dir, "nspawn-network-modes.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    generate_nspawn_architecture(img_dir)
    generate_chroot_vs_nspawn(img_dir)
    generate_nspawn_network_modes(img_dir)

if __name__ == "__main__":
    main()
