import os
import sys

# Ensure scripts directory is in path for svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render_layered_stack():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title
    frags.append(svgkit.text(450, 25, "Шестирівневий Стек Архітектури ZFS (від диска до POSIX)", size=15, bold=True, anchor="middle", color="#1a252f"))

    layers = [
        ("ZPL / ZVOL (ZFS POSIX Layer / Volume)", "Представлення системних файлів (POSIX: files, dirs) або блокових томів (/dev/zvol)", "#dcfce7", "#16a34a", "#15803d"),
        ("DSL (Dataset and Snapshot Layer)", "Управління ієрархією датасетів, знімками, клонами та відстеженням простору", "#dbeafe", "#2563eb", "#1d4ed8"),
        ("ZAP (ZFS Attribute Processor)", "Хеш-індексований словник для атрибутів датасетів та вмісту каталогів (Micro/Fat-ZAP)", "#fef3c7", "#d97706", "#b45309"),
        ("DMU (Data Management Unit)", "Об'єктний шар: dnodes, транзакційні групи (TXG), CoW-семантика та атомарні зміни", "#e0e7ff", "#4338ca", "#3730a3"),
        ("SPA (Storage Pool Allocator)", "Виділення простору в пулі, Metaslabs, балансування stripe та вказівники блоків (blkptr_t)", "#fae8ff", "#c026d3", "#86198f"),
        ("VDEV (Virtual Device Layer)", "Абстракція фізичного заліза: диски, дзеркала, RAIDZ1/2/3, SLOG, L2ARC, Special VDEV", "#fee2e2", "#dc2626", "#991b1b")
    ]

    y_start = 55
    box_h = 42
    gap = 10

    for i, (name, desc, fill, stroke, text_col) in enumerate(layers):
        cy = y_start + i * (box_h + gap)
        # Rect
        frags.append(svgkit.rect(60, cy, 780, box_h, fill=fill, stroke=stroke, sw=1.8, rx=6))
        # Name
        frags.append(svgkit.text(80, cy + 25, name, size=12, bold=True, anchor="start", color=text_col))
        # Description
        frags.append(svgkit.text(370, cy + 25, desc, size=10, bold=False, anchor="start", color="#334155"))

        # Arrow down between layers
        if i < len(layers) - 1:
            arrow_y1 = cy + box_h
            arrow_y2 = cy + box_h + gap
            frags.append(svgkit.line(450, arrow_y1, 450, arrow_y2, color="#64748b", sw=1.5))

    out_path = os.path.join(img_dir, "zfs-layered-stack.svg")
    svgkit.render(out_path, 900, 375, *frags)

def render_merkle_tree_cow():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    frags.append(svgkit.text(450, 25, "Дерево Меркла ZFS: Контрольні Суми та Каскадне CoW-Оновлення", size=14, bold=True, anchor="middle", color="#1e293b"))

    # Uberblock Ring
    tb_ub, _, _ = svgkit.textbox(450, 65, "Uberblock (TXG N+1)\nВказує на кореневий Вказівник Блоку (Root blkptr_t)", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(tb_ub)

    # Level 2: Root Block Pointer
    tb_root_bp, _, _ = svgkit.textbox(450, 145, "Root Block Pointer (blkptr_t)\n[3x DVA | LSIZE/PSIZE | Fletcher4 Checksum | Birth TXG N+1]", size=10, fill="#dbeafe", stroke="#2563eb", bold=True)
    frags.append(tb_root_bp)

    # Connection UB -> Root BP
    frags.append(svgkit.line(450, 85, 450, 130, color="#d97706", sw=1.8))

    # Level 1: Indirect Blocks
    tb_ind1, _, _ = svgkit.textbox(240, 225, "Indirect Block A (Незмінний)\nbytenr: 0x1000 (TXG N)", size=10, fill="#f1f5f9", stroke="#94a3b8")
    tb_ind2, _, _ = svgkit.textbox(660, 225, "Indirect Block B' (Новий CoW)\nbytenr: 0x5000 (TXG N+1)", size=10, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.extend([tb_ind1, tb_ind2])

    frags.append(svgkit.line(380, 160, 240, 210, color="#64748b", sw=1.5, dash="3,3"))
    frags.append(svgkit.line(520, 160, 660, 210, color="#16a34a", sw=2))

    # Level 0: Data / Dnode Blocks
    tb_d1, _, _ = svgkit.textbox(140, 310, "Data Block D1\n(TXG N)", size=10, fill="#f1f5f9", stroke="#94a3b8")
    tb_d2, _, _ = svgkit.textbox(340, 310, "Data Block D2\n(TXG N)", size=10, fill="#f1f5f9", stroke="#94a3b8")
    tb_d3_old, _, _ = svgkit.textbox(550, 310, "Data Block D3 (Звільнено)\nbytenr: 0x3000 (TXG N)", size=10, fill="#fee2e2", stroke="#dc2626")
    tb_d3_new, _, _ = svgkit.textbox(770, 310, "Data Block D3' (Нові дані)\nbytenr: 0x8000 (TXG N+1)", size=10, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.extend([tb_d1, tb_d2, tb_d3_old, tb_d3_new])

    frags.append(svgkit.line(240, 240, 140, 295, color="#94a3b8", sw=1.5))
    frags.append(svgkit.line(240, 240, 340, 295, color="#94a3b8", sw=1.5))
    frags.append(svgkit.line(660, 240, 550, 295, color="#dc2626", sw=1.2, dash="3,3"))
    frags.append(svgkit.line(660, 240, 770, 295, color="#16a34a", sw=2))

    out_path = os.path.join(img_dir, "zfs-merkle-tree-cow.svg")
    svgkit.render(out_path, 900, 360, *frags)

def render_vdev_topology():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    frags.append(svgkit.text(450, 25, "Топологія ZPOOL: Основні VDEV, SLOG, L2ARC та Special Allocation Class", size=14, bold=True, anchor="middle", color="#0f172a"))

    # Top level pool box
    tb_pool, _, _ = svgkit.textbox(450, 65, "ZPOOL (Storage Pool Allocator - SPA)\nДинамічний Stripe між усіма Top-Level VDEV", size=12, fill="#e2e8f0", stroke="#475569", bold=True)
    frags.append(tb_pool)

    # Top level VDEVs
    # Mirror VDEV
    frags.append(svgkit.rect(40, 125, 190, 160, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(svgkit.text(135, 145, "Top-Level VDEV 0\n(Mirror)", size=11, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(svgkit.rect(55, 175, 160, 45, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(svgkit.text(135, 202, "Disk /dev/sda", size=10, anchor="middle", color="#1e40af"))
    frags.append(svgkit.rect(55, 228, 160, 45, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(svgkit.text(135, 255, "Disk /dev/sdb", size=10, anchor="middle", color="#1e40af"))

    # RAIDZ2 VDEV
    frags.append(svgkit.rect(255, 125, 210, 160, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(svgkit.text(360, 145, "Top-Level VDEV 1\n(RAIDZ2)", size=11, bold=True, anchor="middle", color="#15803d"))
    frags.append(svgkit.rect(270, 175, 180, 32, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(svgkit.text(360, 195, "Disk /dev/sdc (Data)", size=9, anchor="middle", color="#166534"))
    frags.append(svgkit.rect(270, 212, 180, 32, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(svgkit.text(360, 232, "Disk /dev/sdd (Data)", size=9, anchor="middle", color="#166534"))
    frags.append(svgkit.rect(270, 248, 180, 32, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(svgkit.text(360, 268, "Disk /dev/sde (Parity P+Q)", size=9, anchor="middle", color="#166534"))

    # Special VDEV
    frags.append(svgkit.rect(485, 125, 180, 160, fill="#fae8ff", stroke="#c026d3", sw=1.5, rx=6))
    frags.append(svgkit.text(575, 145, "Special VDEV\n(Metadata & Small Blocks)", size=10, bold=True, anchor="middle", color="#86198f"))
    frags.append(svgkit.rect(500, 185, 150, 80, fill="#ffffff", stroke="#f0abfc", sw=1, rx=4))
    frags.append(svgkit.text(575, 215, "NVMe Mirror\n/dev/nvme0n1", size=10, anchor="middle", color="#701a75"))
    frags.append(svgkit.text(575, 240, "/dev/nvme1n1", size=10, anchor="middle", color="#701a75"))

    # Aux VDEVs (SLOG & L2ARC)
    frags.append(svgkit.rect(685, 125, 175, 160, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(svgkit.text(772, 145, "Auxiliary VDEVs\n(SLOG & L2ARC)", size=11, bold=True, anchor="middle", color="#b45309"))
    frags.append(svgkit.rect(700, 175, 145, 45, fill="#ffffff", stroke="#fde047", sw=1, rx=4))
    frags.append(svgkit.text(772, 195, "SLOG (Log VDEV)", size=9, bold=True, anchor="middle", color="#92400e"))
    frags.append(svgkit.text(772, 210, "NVMe PLP", size=9, anchor="middle", color="#92400e"))
    frags.append(svgkit.rect(700, 228, 145, 45, fill="#ffffff", stroke="#fde047", sw=1, rx=4))
    frags.append(svgkit.text(772, 248, "L2ARC (Cache)", size=9, bold=True, anchor="middle", color="#92400e"))
    frags.append(svgkit.text(772, 263, "Fast SSD", size=9, anchor="middle", color="#92400e"))

    # Arrows from SPA
    frags.append(svgkit.line(350, 85, 135, 120, color="#475569", sw=1.5))
    frags.append(svgkit.line(400, 85, 360, 120, color="#475569", sw=1.5))
    frags.append(svgkit.line(500, 85, 575, 120, color="#c026d3", sw=1.5))
    frags.append(svgkit.line(550, 85, 772, 120, color="#d97706", sw=1.5))

    out_path = os.path.join(img_dir, "zfs-vdev-topology.svg")
    svgkit.render(out_path, 900, 310, *frags)

def render():
    render_layered_stack()
    render_merkle_tree_cow()
    render_vdev_topology()

if __name__ == '__main__':
    render()
