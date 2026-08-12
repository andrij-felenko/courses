import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render_cow():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title / Headers
    frags.append(svgkit.text(200, 30, "Стан до модифікації (Gen 40)", size=14, bold=True, anchor="middle", color="#2457d6"))
    frags.append(svgkit.text(650, 30, "Стан після модифікації (Gen 41)", size=14, bold=True, anchor="middle", color="#c0392b"))

    # Old Root and New Root
    tb_old_root, _, _ = svgkit.textbox(200, 80, "Old Root (Gen 40)\nbytenr: 0x1000", size=12, fill="#dae8fc", stroke="#6c8ebf")
    tb_new_root, _, _ = svgkit.textbox(650, 80, "New Root (Gen 41)\nbytenr: 0x5000", size=12, fill="#f8cecc", stroke="#b85450")
    frags.extend([tb_old_root, tb_new_root])

    # Internal Nodes
    tb_old_node, _, _ = svgkit.textbox(200, 170, "Node A (Gen 40)\nbytenr: 0x2000", size=12, fill="#dae8fc", stroke="#6c8ebf")
    tb_new_node, _, _ = svgkit.textbox(650, 170, "Node A' (Gen 41)\nbytenr: 0x6000", size=12, fill="#f8cecc", stroke="#b85450")
    frags.extend([tb_old_node, tb_new_node])

    # Leaf Nodes
    tb_leaf_shared, _, _ = svgkit.textbox(425, 260, "Shared Leaf L1 (Gen 38)\nbytenr: 0x3000 (Спільний)", size=12, fill="#d5e8d4", stroke="#82b366")
    tb_leaf_old, _, _ = svgkit.textbox(150, 260, "Leaf L2 (Gen 40)\nbytenr: 0x4000 (Старий)", size=12, fill="#e1d5e7", stroke="#9673a6")
    tb_leaf_new, _, _ = svgkit.textbox(700, 260, "Leaf L2' (Gen 41)\nbytenr: 0x7000 (Новий CoW)", size=12, fill="#ffe6cc", stroke="#d79b00")
    frags.extend([tb_leaf_shared, tb_leaf_old, tb_leaf_new])

    # Connections Old Tree
    frags.append(svgkit.line(200, 100, 200, 150, color="#6c8ebf", sw=1.8))
    frags.append(svgkit.line(170, 190, 150, 240, color="#6c8ebf", sw=1.8))
    frags.append(svgkit.line(230, 190, 370, 240, color="#6c8ebf", sw=1.8))

    # Connections New Tree
    frags.append(svgkit.line(650, 100, 650, 150, color="#b85450", sw=1.8))
    frags.append(svgkit.line(620, 190, 480, 240, color="#82b366", sw=1.8))
    frags.append(svgkit.line(680, 190, 700, 240, color="#b85450", sw=1.8))

    out_path = os.path.join(img_dir, "btrfs-cow.svg")
    svgkit.render(out_path, 850, 310, *frags)

def render_trees():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Root of Trees
    tb_root, _, _ = svgkit.textbox(425, 40, "Root of Tree Roots (ROOT_TREE / ID 1)\nКаталог усіх коренів системних та користувацьких дерев", size=13, fill="#d5e8d4", stroke="#82b366", bold=True)
    frags.append(tb_root)

    # Subvolumes and Trees
    trees_info = [
        ("CHUNK_TREE\n(ID 2: Адресація)", 100, "#dae8fc", "#6c8ebf"),
        ("EXTENT_TREE\n(ID 2: Аллокації)", 260, "#dae8fc", "#6c8ebf"),
        ("CSUM_TREE\n(ID 7: Чексуми)", 420, "#dae8fc", "#6c8ebf"),
        ("Subvol @\n(ID 256: FS_TREE)", 580, "#ffe6cc", "#d79b00"),
        ("Snap @snap1\n(ID 258: Snapshot)", 740, "#e1d5e7", "#9673a6")
    ]

    for label, x, fill, stroke in trees_info:
        tb, _, _ = svgkit.textbox(x, 150, label, size=11, fill=fill, stroke=stroke)
        frags.append(tb)
        frags.append(svgkit.line(425, 65, x, 130, color="#333333", sw=1.5))

    # Shared Extents box
    tb_ext, _, _ = svgkit.textbox(660, 250, "Спільні Екстенти Даних на Диску (Shared Data Extents)\n[Extents #100..#150 використано одночасно Subvol 256 та Snap 258]", size=11, fill="#fff2cc", stroke="#d6b656")
    frags.append(tb_ext)

    frags.append(svgkit.line(580, 175, 630, 230, color="#d79b00", sw=1.5, dash="4,4"))
    frags.append(svgkit.line(740, 175, 690, 230, color="#9673a6", sw=1.5, dash="4,4"))

    out_path = os.path.join(img_dir, "btrfs-trees.svg")
    svgkit.render(out_path, 850, 300, *frags)

def render():
    render_cow()
    render_trees()

if __name__ == '__main__':
    render()
