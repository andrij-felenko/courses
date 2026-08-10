import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render_cow():
    if not svgkit: return
    frags = [
        svgkit.rect(50, 50, 150, 50, fill="#e2f0cb", stroke="#000", rx=5),
        svgkit.text(125, 75, "Original Block A", anchor="middle", size=14),
        svgkit.rect(50, 150, 150, 50, fill="#e2f0cb", stroke="#000", rx=5),
        svgkit.text(125, 175, "Original Block B", anchor="middle", size=14),
        svgkit.rect(350, 150, 150, 50, fill="#ffb7b2", stroke="#000", rx=5),
        svgkit.text(425, 175, "Modified Block B'", anchor="middle", size=14),
        svgkit.text(125, 30, "Old Snapshot", anchor="middle", bold=True),
        svgkit.text(425, 30, "Current State", anchor="middle", bold=True),
        svgkit.line(200, 75, 425, 75, color="#333", sw=2),
        svgkit.line(200, 175, 275, 175, color="#333", sw=2),
        svgkit.text(250, 160, "Copy-on-Write", size=12, italic=True)
    ]
    out_path = os.path.join(os.path.dirname(__file__), "btrfs-cow.svg")
    svgkit.render(out_path, 800, 300, *frags)

def render_trees():
    if not svgkit: return
    frags = [
        svgkit.rect(300, 20, 200, 50, fill="#d5e8d4", stroke="#82b366", rx=5),
        svgkit.text(400, 45, "Tree of Tree Roots", anchor="middle", bold=True)
    ]
    trees = [
        ("fs_tree", 100),
        ("extent_tree", 300),
        ("chunk_tree", 500),
        ("csum_tree", 700)
    ]
    for name, x in trees:
        frags.append(svgkit.rect(x - 75, 150, 150, 50, fill="#dae8fc", stroke="#6c8ebf", rx=5))
        frags.append(svgkit.text(x, 175, name, anchor="middle"))
        frags.append(svgkit.line(400, 70, x, 150, color="#333", sw=2))
        
    out_path = os.path.join(os.path.dirname(__file__), "btrfs-trees.svg")
    svgkit.render(out_path, 800, 300, *frags)

def render():
    render_cow()
    render_trees()

if __name__ == '__main__':
    render()
