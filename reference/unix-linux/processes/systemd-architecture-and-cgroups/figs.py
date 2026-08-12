import sys
import os

# Four levels up to reach repository root scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import (
    render, textbox, text, line, arrow, rect, fit_font, INK, MUTED, FIELD, POS, NEG, FILL, BG
)

def build_cgroup_tree():
    # systemd-cgroup-tree.svg
    elements = []
    
    # Root VFS node
    elements.append(rect(300, 20, 200, 45, fill="#e8edf2", stroke=INK, rx=6))
    elements.append(text(400, 47, "/sys/fs/cgroup (Root Slice)", size=14, bold=True))
    
    # Connections from root to slices
    elements.append(line(400, 65, 150, 115, color=INK, sw=2))
    elements.append(line(400, 65, 400, 115, color=INK, sw=2))
    elements.append(line(400, 65, 650, 115, color=INK, sw=2))
    
    # Slice nodes (Grouping Containers)
    elements.append(rect(60, 115, 180, 45, fill="#dbeefd", stroke=INK, rx=6))
    elements.append(text(150, 137, "system.slice", size=14, bold=True, color="#1b4965"))
    elements.append(text(150, 152, "[Зріз системних служб]", size=11, italic=True, color=MUTED))

    elements.append(rect(310, 115, 180, 45, fill="#dbeefd", stroke=INK, rx=6))
    elements.append(text(400, 137, "user.slice", size=14, bold=True, color="#1b4965"))
    elements.append(text(400, 152, "[Зріз сесій користувачів]", size=11, italic=True, color=MUTED))

    elements.append(rect(560, 115, 180, 45, fill="#dbeefd", stroke=INK, rx=6))
    elements.append(text(650, 137, "machine.slice", size=14, bold=True, color="#1b4965"))
    elements.append(text(650, 152, "[Зріз ВМ і контейнерів]", size=11, italic=True, color=MUTED))

    # Lines down from system.slice
    elements.append(line(150, 160, 80, 220, color=INK, sw=1.5))
    elements.append(line(150, 160, 230, 220, color=INK, sw=1.5))

    # Services under system.slice
    elements.append(rect(10, 220, 140, 50, fill="#e2f0d9", stroke=INK, rx=6))
    elements.append(text(80, 242, "nginx.service", size=13, bold=True, color="#276749"))
    elements.append(text(80, 258, "Service (cgroup leaf)", size=10, color=MUTED))

    elements.append(rect(160, 220, 140, 50, fill="#e2f0d9", stroke=INK, rx=6))
    elements.append(text(230, 242, "dbus.service", size=13, bold=True, color="#276749"))
    elements.append(text(230, 258, "Service (cgroup leaf)", size=10, color=MUTED))

    # Lines down from user.slice
    elements.append(line(400, 160, 400, 220, color=INK, sw=1.5))

    # User sub-slice
    elements.append(rect(310, 220, 180, 45, fill="#dbeefd", stroke=INK, rx=6))
    elements.append(text(400, 242, "user-1000.slice", size=13, bold=True, color="#1b4965"))
    elements.append(text(400, 257, "UID 1000 slice", size=11, color=MUTED))

    # Lines down from user-1000.slice
    elements.append(line(400, 265, 335, 325, color=INK, sw=1.5))
    elements.append(line(400, 265, 505, 325, color=INK, sw=1.5))

    # Scope and user service under user-1000.slice
    elements.append(rect(260, 325, 150, 50, fill="#fff3cd", stroke=INK, rx=6))
    elements.append(text(335, 347, "session-2.scope", size=13, bold=True, color="#856404"))
    elements.append(text(335, 363, "Scope (SSH bash)", size=10, color=MUTED))

    elements.append(rect(430, 325, 150, 50, fill="#e2f0d9", stroke=INK, rx=6))
    elements.append(text(505, 347, "app.service", size=13, bold=True, color="#276749"))
    elements.append(text(505, 363, "User Service", size=10, color=MUTED))

    # Lines down from machine.slice
    elements.append(line(650, 160, 650, 220, color=INK, sw=1.5))
    elements.append(rect(570, 220, 160, 50, fill="#fff3cd", stroke=INK, rx=6))
    elements.append(text(650, 242, "vm-qemu.scope", size=13, bold=True, color="#856404"))
    elements.append(text(650, 258, "Scope (KVM / QEMU)", size=10, color=MUTED))

    # Processes inside leaves
    elements.append(line(80, 270, 80, 400, color=INK, sw=1, dash="3,3"))
    elements.append(rect(20, 400, 120, 35, fill="#ffffff", stroke="#276749", rx=4))
    elements.append(text(80, 422, "PID 1420 (nginx)", size=11, color=INK))

    elements.append(line(335, 375, 335, 400, color=INK, sw=1, dash="3,3"))
    elements.append(rect(275, 400, 120, 35, fill="#ffffff", stroke="#856404", rx=4))
    elements.append(text(335, 422, "PID 2891 (bash)", size=11, color=INK))

    return "".join(elements)


def build_dbus_flow():
    # systemd-dbus-cgroup-flow.svg
    elements = []

    # Column 1: Client Application
    elements.append(rect(40, 40, 200, 280, fill="#f8f9fa", stroke=INK, rx=8))
    elements.append(text(140, 70, "Клієнтський процес", size=14, bold=True))
    elements.append(text(140, 90, "(systemd-run / Podman)", size=11, color=MUTED))
    elements.append(rect(55, 120, 170, 45, fill="#ffffff", stroke=INK, rx=5))
    elements.append(text(140, 147, "1. StartTransientUnit()", size=12, bold=True, color="#2457d6"))

    # Column 2: System Bus & systemd (PID 1)
    elements.append(rect(300, 40, 220, 280, fill="#edf2f7", stroke=INK, rx=8))
    elements.append(text(410, 70, "systemd (PID 1)", size=14, bold=True, color="#1a202c"))
    elements.append(text(410, 90, "org.freedesktop.systemd1", size=11, color=MUTED))
    
    elements.append(rect(315, 120, 190, 45, fill="#ffffff", stroke=INK, rx=5))
    elements.append(text(410, 147, "2. Валідація лімітів", size=12, bold=True))

    elements.append(rect(315, 195, 190, 45, fill="#ffffff", stroke=INK, rx=5))
    elements.append(text(410, 222, "3. Створення vfs cgroup", size=12, bold=True))

    elements.append(rect(315, 255, 190, 45, fill="#ffffff", stroke=INK, rx=5))
    elements.append(text(410, 282, "4. Прив'язка PID до cgroup", size=12, bold=True))

    # Column 3: VFS /sys/fs/cgroup
    elements.append(rect(570, 40, 190, 280, fill="#e6fffa", stroke=INK, rx=8))
    elements.append(text(665, 70, "cgroups v2 VFS", size=14, bold=True, color="#234e52"))
    elements.append(text(665, 90, "/sys/fs/cgroup/...", size=11, color=MUTED))

    elements.append(rect(585, 180, 160, 45, fill="#ffffff", stroke="#234e52", rx=5))
    elements.append(text(665, 200, "memory.max = 1G", size=11, bold=True))
    elements.append(text(665, 215, "cpu.weight = 500", size=11, bold=True))

    elements.append(rect(585, 245, 160, 45, fill="#ffffff", stroke="#234e52", rx=5))
    elements.append(text(665, 270, "cgroup.procs = [PID]", size=11, bold=True, color="#c0392b"))

    # Arrows
    elements.append(arrow(225, 142, 315, 142, color="#2457d6", sw=2))
    elements.append(line(410, 165, 410, 195, color=INK, sw=2))
    elements.append(line(410, 240, 410, 255, color=INK, sw=2))
    elements.append(arrow(505, 217, 585, 202, color="#27ae60", sw=2))
    elements.append(arrow(505, 277, 585, 267, color="#27ae60", sw=2))

    return "".join(elements)


def build_delegation():
    # cgroup-delegation.svg
    elements = []

    # Outer Container Box
    elements.append(rect(20, 20, 760, 320, fill="#f7fafc", stroke=INK, rx=8))

    # Systemd Managed Zone (Top)
    elements.append(rect(40, 40, 720, 130, fill="#ebf8ff", stroke="#3182ce", rx=6))
    elements.append(text(200, 65, "Зона управління systemd (Single Writer)", size=13, bold=True, color="#2b6cb0"))
    
    elements.append(rect(60, 85, 200, 45, fill="#ffffff", stroke="#3182ce", rx=4))
    elements.append(text(160, 110, "system.slice", size=13, bold=True))

    elements.append(rect(300, 85, 440, 65, fill="#ffffff", stroke="#3182ce", rx=4))
    elements.append(text(520, 107, "docker.service (Delegate=yes)", size=13, bold=True, color="#2b6cb0"))
    elements.append(text(520, 127, "chown user:group + cgroup.subtree_control", size=11, color=MUTED))

    # Boundary Line (Delegation point)
    elements.append(line(40, 190, 760, 190, color="#c0392b", sw=2, dash="6,4"))
    elements.append(text(400, 185, "▼ МЕЖА ДЕЛЕГУВАННЯ (DELEGATION BOUNDARY) ▼", size=11, bold=True, color="#c0392b"))

    # Container Engine Managed Zone (Bottom)
    elements.append(rect(40, 200, 720, 120, fill="#f0fff4", stroke="#38a169", rx=6))
    elements.append(text(240, 220, "Зона управління контейнерного рушія (containerd / crun)", size=13, bold=True, color="#276749"))

    # Sub-cgroups inside container engine
    elements.append(line(520, 150, 520, 235, color=INK, sw=2))
    elements.append(line(520, 235, 230, 235, color=INK, sw=1.5))
    elements.append(line(520, 235, 590, 235, color=INK, sw=1.5))
    elements.append(line(230, 235, 230, 250, color=INK, sw=1.5))
    elements.append(line(590, 235, 590, 250, color=INK, sw=1.5))

    elements.append(rect(120, 250, 220, 55, fill="#ffffff", stroke="#38a169", rx=4))
    elements.append(text(230, 272, "container-a.scope", size=12, bold=True, color="#276749"))
    elements.append(text(230, 290, "memory.max = 512M", size=10, color=MUTED))

    elements.append(rect(480, 250, 220, 55, fill="#ffffff", stroke="#38a169", rx=4))
    elements.append(text(590, 272, "container-b.scope", size=12, bold=True, color="#276749"))
    elements.append(text(590, 290, "cpu.weight = 200", size=10, color=MUTED))

    return "".join(elements)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    render(os.path.join(img_dir, 'systemd-cgroup-tree.svg'), 800, 460, build_cgroup_tree())
    render(os.path.join(img_dir, 'systemd-dbus-cgroup-flow.svg'), 800, 360, build_dbus_flow())
    render(os.path.join(img_dir, 'cgroup-delegation.svg'), 800, 360, build_delegation())
    print("Figures generated successfully.")

if __name__ == '__main__':
    main()
