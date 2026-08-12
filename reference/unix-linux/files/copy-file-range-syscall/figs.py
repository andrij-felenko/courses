import sys
import os

# Append the scripts directory to sys.path to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

import svgkit

def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    svg_path = os.path.join(img_dir, "copy-file-range-arch.svg")

    w, h = 820, 380

    # Title
    t1 = svgkit.text(410, 30, "Порівняння копіювання файлів у Linux", size=18, bold=True)

    # Column 1: Traditional Read / Write
    col1_title = svgkit.text(205, 65, "Традиційний шлях: read() / write()", size=15, color=svgkit.POS, bold=True)
    b1_src, _, _ = svgkit.textbox(205, 115, "Вихідний файл\n(NVMe / Storage)", size=13, pad=12, fill="#eef2f7", stroke="#4a5568")
    b1_u, _, _   = svgkit.textbox(205, 195, "User Space Buffer\n(Перемикання контексту & RAM)", size=13, pad=12, fill="#fff5f5", stroke=svgkit.POS)
    b1_dst, _, _ = svgkit.textbox(205, 280, "Цільовий файл\n(NVMe / Storage)", size=13, pad=12, fill="#eef2f7", stroke="#4a5568")

    a1_in  = svgkit.arrow(205, 140, 205, 170, color=svgkit.POS, sw=2)
    lbl1_in = svgkit.text(250, 160, "1. read() sys_call", size=11, color=svgkit.POS, anchor="start")
    a1_out = svgkit.arrow(205, 222, 205, 253, color=svgkit.POS, sw=2)
    lbl1_out = svgkit.text(250, 242, "2. write() sys_call", size=11, color=svgkit.POS, anchor="start")

    # Divider line
    div = svgkit.line(410, 55, 410, 340, color="#cbd5e1", sw=1.5, dash="4,4")

    # Column 2: In-Kernel / Offload copy_file_range
    col2_title = svgkit.text(615, 65, "Zero-Copy: copy_file_range()", size=15, color=svgkit.FIELD, bold=True)
    b2_src, _, _ = svgkit.textbox(615, 115, "Вихідний файл\n(fd_in)", size=13, pad=12, fill="#eef2f7", stroke="#4a5568")
    b2_vfs, _, _ = svgkit.textbox(615, 195, "VFS / Kernel Layer\n(CoW Reflink / Server-Side Copy)", size=13, pad=12, fill="#e6f4ea", stroke=svgkit.FIELD)
    b2_dst, _, _ = svgkit.textbox(615, 280, "Цільовий файл\n(fd_out)", size=13, pad=12, fill="#eef2f7", stroke="#4a5568")

    a2_vfs1 = svgkit.arrow(615, 140, 615, 170, color=svgkit.FIELD, sw=2)
    lbl2_in = svgkit.text(655, 160, "Offload / CoW", size=11, color=svgkit.FIELD, anchor="start")
    a2_vfs2 = svgkit.arrow(615, 222, 615, 253, color=svgkit.FIELD, sw=2)
    lbl2_out = svgkit.text(655, 242, "O(1) Metadata update", size=11, color=svgkit.FIELD, anchor="start")

    # Direct fast arrow (bypassing user space completely)
    a2_direct = svgkit.arrow(530, 125, 530, 270, color=svgkit.FIELD, sw=2.5)
    lbl2_fast = svgkit.text(440, 195, "Пряма передача\nбез User Space", size=11, color=svgkit.FIELD, anchor="middle", bold=True)

    # Footnote note
    note = svgkit.text(410, 355, "copy_file_range виконує копіювання в ядрі або делегує його апаратному сховищу (NFS SSC / CoW)", size=12, color=svgkit.MUTED, italic=True)

    frags = [
        t1,
        col1_title, b1_src, b1_u, b1_dst, a1_in, lbl1_in, a1_out, lbl1_out,
        div,
        col2_title, b2_src, b2_vfs, b2_dst, a2_vfs1, lbl2_in, a2_vfs2, lbl2_out, a2_direct, lbl2_fast,
        note
    ]

    svgkit.render(svg_path, w, h, *frags)
    print(f"Generated SVG: {svg_path}")

if __name__ == "__main__":
    main()
