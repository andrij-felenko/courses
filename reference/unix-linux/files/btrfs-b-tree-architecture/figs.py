import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render_leaf_layout():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title
    frags.append(svgkit.text(450, 25, "Анатомія Листка (Leaf) Btrfs Розміром 16 КБ (nodesize)", size=14, bold=True, anchor="middle", color="#1a252f"))

    # Outer Leaf Frame
    frags.append(svgkit.rect(50, 50, 800, 140, fill="#f8f9fa", stroke="#2c3e50", sw=2, rx=4))

    # Header section (0 .. 101 bytes)
    frags.append(svgkit.rect(50, 50, 160, 140, fill="#dae8fc", stroke="#6c8ebf", sw=1.5))
    frags.append(svgkit.text(130, 95, "btrfs_header", size=12, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(svgkit.text(130, 115, "csum, fsid, owner", size=10, anchor="middle", color="#3b82f6"))
    frags.append(svgkit.text(130, 130, "bytenr, gen, level=0", size=10, anchor="middle", color="#3b82f6"))
    frags.append(svgkit.text(130, 155, "Зсув: 0..101 байт", size=9, anchor="middle", color="#64748b"))

    # Item Headers array (growing forward)
    frags.append(svgkit.rect(210, 50, 240, 140, fill="#d5e8d4", stroke="#82b366", sw=1.5))
    frags.append(svgkit.text(330, 85, "Заголовки Елементів (btrfs_item[])", size=12, bold=True, anchor="middle", color="#15803d"))
    frags.append(svgkit.text(330, 110, "item[0] | item[1] | ... | item[N-1]", size=10, anchor="middle", color="#166534"))
    frags.append(svgkit.text(330, 130, "(key, offset, size)", size=10, anchor="middle", color="#166534"))
    frags.append(svgkit.text(330, 160, "Ростуть уперед (зсув →)", size=9, anchor="middle", color="#15803d"))

    # Free Space in middle
    frags.append(svgkit.rect(450, 50, 190, 140, fill="#fff2cc", stroke="#d6b656", sw=1.5))
    frags.append(svgkit.text(545, 105, "Вільний Простір", size=12, bold=True, anchor="middle", color="#b45309"))
    frags.append(svgkit.text(545, 130, "(Free Space)", size=11, anchor="middle", color="#d97706"))

    # Data Payloads (growing backward)
    frags.append(svgkit.rect(640, 50, 210, 140, fill="#ffe6cc", stroke="#d79b00", sw=1.5))
    frags.append(svgkit.text(745, 85, "Тіла Даних (Data Payloads)", size=12, bold=True, anchor="middle", color="#c2410c"))
    frags.append(svgkit.text(745, 110, "data[N-1] | ... | data[1] | data[0]", size=10, anchor="middle", color="#9a3412"))
    frags.append(svgkit.text(745, 130, "(INODE_ITEM, EXTENT_DATA)", size=10, anchor="middle", color="#9a3412"))
    frags.append(svgkit.text(745, 160, "Ростуть назад (← зсув)", size=9, anchor="middle", color="#c2410c"))

    # Arrows showing growth directions
    frags.append(svgkit.arrow(220, 175, 430, 175, color="#15803d", sw=2))
    frags.append(svgkit.arrow(830, 175, 650, 175, color="#c2410c", sw=2))

    out_path = os.path.join(img_dir, "btrfs-leaf-layout.svg")
    svgkit.render(out_path, 900, 220, *frags)

def render_cow_propagation():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Columns titles
    frags.append(svgkit.text(220, 25, "Транзакція N (Старий стан)", size=13, bold=True, anchor="middle", color="#475569"))
    frags.append(svgkit.text(680, 25, "Транзакція N+1 (Новий CoW стан)", size=13, bold=True, anchor="middle", color="#2563eb"))

    # Superblock
    tb_sb, _, _ = svgkit.textbox(450, 60, "Superblock\n(Вказує на поточне активне Root Tree)", size=11, fill="#e2e8f0", stroke="#64748b", bold=True)
    frags.append(tb_sb)

    # Old Tree
    tb_old_root, _, _ = svgkit.textbox(220, 140, "Root Node (Gen N)\nbytenr: 0x1000", size=11, fill="#dae8fc", stroke="#6c8ebf")
    tb_old_node, _, _ = svgkit.textbox(140, 220, "Node A (Gen N)\nbytenr: 0x2000", size=11, fill="#dae8fc", stroke="#6c8ebf")
    tb_old_node_b, _, _ = svgkit.textbox(300, 220, "Node B (Gen N-2)\nbytenr: 0x3000 (Незмінний)", size=11, fill="#e2e8f0", stroke="#94a3b8")
    tb_old_leaf, _, _ = svgkit.textbox(100, 300, "Leaf L1 (Gen N)\nbytenr: 0x4000 (Старий)", size=11, fill="#f8cecc", stroke="#b85450")
    frags.extend([tb_old_root, tb_old_node, tb_old_node_b, tb_old_leaf])

    # New Tree (CoW)
    tb_new_root, _, _ = svgkit.textbox(680, 140, "Root Node' (Gen N+1)\nbytenr: 0x5000 (Новий)", size=11, fill="#dbeafe", stroke="#2563eb", bold=True)
    tb_new_node, _, _ = svgkit.textbox(600, 220, "Node A' (Gen N+1)\nbytenr: 0x6000 (Новий)", size=11, fill="#dbeafe", stroke="#2563eb", bold=True)
    tb_new_leaf, _, _ = svgkit.textbox(560, 300, "Leaf L1' (Gen N+1)\nbytenr: 0x7000 (Новий CoW)", size=11, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.extend([tb_new_root, tb_new_node, tb_new_leaf])

    # Connections Old Tree
    frags.append(svgkit.line(220, 160, 140, 205, color="#6c8ebf", sw=1.5))
    frags.append(svgkit.line(220, 160, 300, 205, color="#6c8ebf", sw=1.5))
    frags.append(svgkit.line(140, 235, 100, 285, color="#6c8ebf", sw=1.5))

    # Connections New Tree
    frags.append(svgkit.line(680, 160, 600, 205, color="#2563eb", sw=1.8))
    frags.append(svgkit.line(680, 160, 300, 205, color="#2563eb", sw=1.5, dash="3,3")) # Sharing unchanged Node B
    frags.append(svgkit.line(600, 235, 560, 285, color="#2563eb", sw=1.8))

    # Pointer transition from Superblock
    frags.append(svgkit.line(400, 75, 220, 125, color="#64748b", sw=1.5, dash="2,2"))
    frags.append(svgkit.line(500, 75, 680, 125, color="#2563eb", sw=2))

    out_path = os.path.join(img_dir, "btrfs-cow-propagation.svg")
    svgkit.render(out_path, 900, 350, *frags)

def render_forest_of_trees():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Superblock
    tb_sb, _, _ = svgkit.textbox(450, 30, "Superblock Btrfs\n(Вказує на ROOT_TREE та CHUNK_TREE)", size=12, fill="#f1f5f9", stroke="#475569", bold=True)
    frags.append(tb_sb)

    # ROOT_TREE
    tb_root_tree, _, _ = svgkit.textbox(300, 110, "ROOT_TREE (ID 1)\nКаталог усіх системних дерев", size=12, fill="#dbeafe", stroke="#2563eb", bold=True)
    tb_chunk_tree, _, _ = svgkit.textbox(650, 110, "CHUNK_TREE (ID 3)\nЛогічна ➔ Фізична адресація", size=11, fill="#fef3c7", stroke="#d97706")
    frags.extend([tb_root_tree, tb_chunk_tree])

    frags.append(svgkit.line(420, 45, 300, 95, color="#475569", sw=1.5))
    frags.append(svgkit.line(480, 45, 650, 95, color="#475569", sw=1.5))

    # Children of ROOT_TREE
    children = [
        ("FS_TREE\n(ID 5: Головний субтом)", 120, "#dcfce7", "#16a34a"),
        ("FS_TREE / Snap\n(ID 256: Субтом/Снапшот)", 300, "#dcfce7", "#16a34a"),
        ("EXTENT_TREE\n(ID 2: Алокації та CoW-посилання)", 480, "#f3e8ff", "#9333ea"),
        ("CSUM_TREE\n(ID 7: Чексуми блоків)", 660, "#fee2e2", "#dc2626"),
        ("FREE_SPACE_TREE\n(ID 10: Вільні екстенти)", 840, "#fef3c7", "#d97706")
    ]

    for label, x, fill, stroke in children:
        tb, _, _ = svgkit.textbox(x, 210, label, size=10, fill=fill, stroke=stroke)
        frags.append(tb)
        frags.append(svgkit.line(300, 125, x, 195, color="#2563eb", sw=1.5))

    out_path = os.path.join(img_dir, "btrfs-forest-of-trees.svg")
    svgkit.render(out_path, 960, 270, *frags)

def render():
    render_leaf_layout()
    render_cow_propagation()
    render_forest_of_trees()

if __name__ == '__main__':
    render()
