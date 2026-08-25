import sys
import os

# Four levels up to get to scripts/
script_dir = os.path.dirname(os.path.abspath(__file__))
courses_dir = os.path.abspath(os.path.join(script_dir, '../../../..'))
sys.path.insert(0, os.path.join(courses_dir, 'scripts'))

from svgkit import render, fitbox, rect, line, arrow, text, mtext, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

def draw_arch():
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "incfs-arch.svg")

    w, h = 760, 420
    frags = []

    # Title / Areas
    # Userspace zone
    frags.append(rect(10, 40, 740, 150, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(30, 62, "КОРИСТУВАЦЬКИЙ ПРОСТІР (USERSPACE)", size=13, color=MUTED, bold=True, anchor="start"))

    # Kernel space zone
    frags.append(rect(10, 205, 740, 140, fill="#fff7ed", stroke="#fed7aa", rx=8))
    frags.append(text(30, 227, "ЯДРО LINUX (KERNEL SPACE)", size=13, color=MUTED, bold=True, anchor="start"))

    # Storage & Network zone
    frags.append(rect(10, 355, 740, 55, fill="#f0fdf4", stroke="#bbf7d0", rx=8))
    frags.append(text(30, 377, "ДИСК ТА МЕРЕЖА", size=13, color=MUTED, bold=True, anchor="start"))

    # Blocks in Userspace
    # 1. Android Application
    frags.append(fitbox(30, 80, 210, 90, "Android App\n(Гра / Додаток)\nread() / mmap()", size=13, fill="#e0f2fe", stroke="#0284c7", bold=True))
    
    # 2. Incremental Service / Data Loader
    frags.append(fitbox(480, 80, 250, 90, "Incremental Service\n(Userspace Daemon)\n.pending_reads & ioctl", size=13, fill="#fef3c7", stroke="#d97706", bold=True))

    # Blocks in Kernel Space
    # 3. VFS Layer
    frags.append(fitbox(30, 245, 210, 80, "VFS Layer\n(sys_read, page fault)", size=13, fill="#fae8ff", stroke="#c084fc", bold=True))

    # 4. IncFS Module
    frags.append(fitbox(280, 245, 220, 80, "IncFS Module\n(Stacked VFS, block bitmap,\nwait queues, verity)", size=13, fill="#ffe4e6", stroke="#e11d48", bold=True))

    # Blocks in Disk/Net
    # 5. Backing Storage
    frags.append(fitbox(280, 365, 220, 40, "Backing FS (ext4/f2fs)", size=12, fill="#dcfce7", stroke="#16a34a", bold=True))

    # 6. Remote CDN
    frags.append(fitbox(530, 365, 200, 40, "Play Store / CDN", size=12, fill="#f3e8ff", stroke="#9333ea", bold=True))

    # Arrows
    # App to VFS
    frags.append(arrow(135, 170, 135, 245, color="#0284c7", sw=2))

    # VFS to IncFS
    frags.append(arrow(240, 285, 280, 285, color="#c084fc", sw=2))

    # IncFS to Data counter / pending reads
    frags.append(arrow(390, 245, 520, 170, color="#e11d48", sw=2))

    # DataLoader to Network
    frags.append(arrow(630, 170, 630, 365, color="#d97706", sw=2))

    # DataLoader to IncFS (INCFS_IOC_FILL_BLOCKS)
    frags.append(arrow(540, 170, 450, 245, color="#16a34a", sw=2))

    # IncFS to Backing FS
    frags.append(arrow(390, 325, 390, 365, color="#16a34a", sw=2))

    render(out_path, w, h, *frags)

def draw_block_load():
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "incfs-block-load.svg")

    w, h = 760, 340
    frags = []

    # Sequence boxes
    steps = [
        ("1. Читання", "Додаток викликає\nread() або mmap()\nна відсутній блок", "#e0f2fe", "#0284c7"),
        ("2. Блокування", "IncFS блокує потік,\nстворює запит у\n.pending_reads", "#ffe4e6", "#e11d48"),
        ("3. Отримання", "Демон читає подію,\nзавантажує 4KB з\nмережі/USB", "#fef3c7", "#d97706"),
        ("4. Заповнення", "Демон робить ioctl\nFILL_BLOCKS з\nперевіркою хешу", "#dcfce7", "#16a34a"),
        ("5. Розблокування", "IncFS пише блок на\nдиск і розблоковує\nпотік читання", "#f3e8ff", "#9333ea")
    ]

    box_w = 135
    spacing = 18
    start_x = 20

    for i, (title, desc, fill_c, stroke_c) in enumerate(steps):
        bx = start_x + i * (box_w + spacing)
        frags.append(fitbox(bx, 60, box_w, 200, f"{title}\n\n{desc}", size=12, fill=fill_c, stroke=stroke_c, bold=True))
        if i < len(steps) - 1:
            arrow_start_x = bx + box_w
            arrow_end_x = arrow_start_x + spacing
            frags.append(arrow(arrow_start_x, 160, arrow_end_x, 160, color=LINE, sw=1.8))

    # Loop back arrow showing unblock / read completes
    frags.append(line(695, 260, 695, 295, color="#9333ea", sw=1.8))
    frags.append(line(695, 295, 87, 295, color="#9333ea", sw=1.8))
    frags.append(arrow(87, 295, 87, 260, color="#9333ea", sw=1.8))
    frags.append(text(390, 312, "Результат: read() повертає дані, додаток продовжує виконання", size=12, color="#9333ea", bold=True))

    render(out_path, w, h, *frags)

if __name__ == "__main__":
    draw_arch()
    draw_block_load()
