import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import render as svg_render, textbox, rect, text, arrow

def render_dt_lifecycle(out_dir):
    w, h = 860, 420
    frags = []

    # Title
    frags.append(text(430, 30, "Життєвий цикл Device Tree: від сирців до драйвера", size=18, bold=True))

    # Phase 1: Development / Compilation
    frags.append(rect(15, 60, 250, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(140, 88, "Етап розробки", size=15, bold=True, color="#1e293b"))
    tb1, _, _ = textbox(140, 145, ".dts / .dtsi\nСирцевий опис плати", size=13, fill="#e0f2fe", stroke="#0284c7")
    frags.append(tb1)
    frags.append(arrow(140, 185, 140, 230, color="#0284c7"))
    frags.append(text(165, 210, "dtc", size=13, bold=True, color="#0369a1"))
    tb2, _, _ = textbox(140, 275, ".dtb (FDT Blob)\nБінарне дерево", size=13, fill="#dcfce7", stroke="#16a34a")
    frags.append(tb2)

    # Arrow between Phase 1 and Phase 2
    frags.append(arrow(265, 275, 295, 275, color="#334155"))

    # Phase 2: Bootloader
    frags.append(rect(295, 60, 270, 340, fill="#fffbe6", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(430, 88, "Завантажувач (U-Boot / OpenSBI)", size=14, bold=True, color="#78350f"))
    tb3, _, _ = textbox(430, 155, "1. Завантаження DTB у RAM\n2. Оновлення bootargs та RAM size", size=12, fill="#feefc3", stroke="#b45309")
    frags.append(tb3)
    frags.append(arrow(430, 210, 430, 245, color="#b45309"))
    tb4, _, _ = textbox(430, 285, "Передача в регістрах\nARM64: x0 | RISC-V: a1", size=12, fill="#fef3c7", stroke="#d97706")
    frags.append(tb4)

    # Arrow between Phase 2 and Phase 3
    frags.append(arrow(565, 285, 595, 285, color="#334155"))

    # Phase 3: Kernel
    frags.append(rect(595, 60, 250, 340, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(720, 88, "Ядро Linux", size=15, bold=True, color="#14532d"))
    tb5, _, _ = textbox(720, 155, "unflatten_device_tree()\nСтворення struct device_node", size=12, fill="#dcfce7", stroke="#15803d")
    frags.append(tb5)
    frags.append(arrow(720, 210, 720, 250, color="#15803d"))
    tb6, _, _ = textbox(720, 290, "of_match_table\nВиклик driver.probe()", size=12, fill="#bbf7d0", stroke="#166534")
    frags.append(tb6)

    svg_render(os.path.join(out_dir, "img", "dt-lifecycle.svg"), w, h, *frags)

def render_fdt_layout(out_dir):
    w, h = 820, 360
    frags = []

    frags.append(text(410, 25, "Структура бінарного Flattened Device Tree Blob (.dtb)", size=17, bold=True))

    # Outer container
    frags.append(rect(20, 50, 780, 280, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))

    # 1. Header block
    frags.append(rect(40, 80, 160, 220, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=6))
    frags.append(text(120, 105, "fdt_header", size=15, bold=True, color="#3730a3"))
    frags.append(text(120, 135, "magic: 0xd00dfeed", size=11, bold=True, color="#1e1b4b"))
    frags.append(text(120, 160, "totalsize", size=11, color="#312e81"))
    frags.append(text(120, 185, "off_dt_struct", size=11, color="#312e81"))
    frags.append(text(120, 210, "off_dt_strings", size=11, color="#312e81"))
    frags.append(text(120, 235, "off_mem_rsvmap", size=11, color="#312e81"))
    frags.append(text(120, 260, "version & boot_cpuid", size=11, color="#312e81"))

    # 2. Memory Reserve Map
    frags.append(rect(220, 80, 150, 220, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(295, 105, "Memory Reserve", size=13, bold=True, color="#92400e"))
    frags.append(text(295, 140, "struct fdt_reserve_entry", size=10, bold=True, color="#78350f"))
    frags.append(text(295, 175, "address (64-bit)", size=11, color="#78350f"))
    frags.append(text(295, 205, "size (64-bit)", size=11, color="#78350f"))
    frags.append(text(295, 250, "Terminator (0, 0)", size=10, italic=True, color="#b45309"))

    # 3. Structure Block
    frags.append(rect(390, 80, 210, 220, fill="#dcfce7", stroke="#15803d", sw=1.5, rx=6))
    frags.append(text(495, 105, "Structure Block", size=14, bold=True, color="#166534"))
    frags.append(text(495, 135, "FDT_BEGIN_NODE (0x0001)", size=11, color="#14532d"))
    frags.append(text(495, 160, "  node_name + padding", size=11, color="#14532d"))
    frags.append(text(495, 185, "FDT_PROP (0x0003)", size=11, bold=True, color="#166534"))
    frags.append(text(495, 210, "  len, nameoff, data...", size=11, color="#14532d"))
    frags.append(text(495, 235, "FDT_END_NODE (0x0002)", size=11, color="#14532d"))
    frags.append(text(495, 260, "FDT_END (0x0009)", size=11, bold=True, color="#166534"))

    # 4. Strings Block
    frags.append(rect(620, 80, 160, 220, fill="#fae8ff", stroke="#a21caf", sw=1.5, rx=6))
    frags.append(text(700, 105, "Strings Block", size=14, bold=True, color="#86198f"))
    frags.append(text(700, 140, "\"compatible\\0\"", size=11, color="#701a75"))
    frags.append(text(700, 170, "\"reg\\0\"", size=11, color="#701a75"))
    frags.append(text(700, 200, "\"interrupts\\0\"", size=11, color="#701a75"))
    frags.append(text(700, 230, "\"status\\0\"", size=11, color="#701a75"))
    frags.append(text(700, 260, "Нуль-терміновані", size=10, italic=True, color="#86198f"))

    # Arrow showing nameoff link from structure block to strings block
    frags.append(arrow(580, 210, 630, 170, color="#a21caf", sw=1.5))
    frags.append(text(600, 180, "nameoff", size=10, bold=True, color="#a21caf"))

    svg_render(os.path.join(out_dir, "img", "fdt-layout.svg"), w, h, *frags)

def render_dt_node_matching(out_dir):
    w, h = 820, 340
    frags = []

    frags.append(text(410, 25, "Зіставлення compatible між Device Tree та драйвером ядра", size=17, bold=True))

    # Left box: Device Tree node
    frags.append(rect(30, 50, 350, 260, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(205, 80, "Вузол у Device Tree (.dts)", size=15, bold=True, color="#0369a1"))
    frags.append(text(70, 120, "serial@101f1000 {", size=13, bold=True, color="#0f172a", anchor="start"))
    frags.append(text(90, 150, "compatible = \"arm,pl011\";", size=13, bold=True, color="#0284c7", anchor="start"))
    frags.append(text(90, 180, "reg = <0x101f1000 0x1000>;", size=12, color="#334155", anchor="start"))
    frags.append(text(90, 210, "interrupts = <1 14>;", size=12, color="#334155", anchor="start"))
    frags.append(text(90, 240, "status = \"okay\";", size=12, color="#334155", anchor="start"))
    frags.append(text(70, 270, "};", size=13, bold=True, color="#0f172a", anchor="start"))

    # Matching Arrow in the middle
    frags.append(arrow(380, 150, 440, 150, color="#16a34a", sw=2.5))
    frags.append(text(410, 135, "Збіг рядка", size=11, bold=True, color="#15803d"))
    frags.append(text(410, 170, "compatible", size=11, bold=True, color="#15803d"))

    # Right box: Driver code
    frags.append(rect(440, 50, 350, 260, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(615, 80, "Драйвер ядра Linux (C)", size=15, bold=True, color="#15803d"))
    frags.append(text(460, 120, "static const struct of_device_id", size=12, bold=True, color="#14532d", anchor="start"))
    frags.append(text(460, 140, "pl011_match[] = {", size=12, bold=True, color="#14532d", anchor="start"))
    frags.append(text(480, 165, "{ .compatible = \"arm,pl011\" },", size=12, bold=True, color="#16a34a", anchor="start"))
    frags.append(text(480, 190, "{ /* sentinel */ }", size=12, color="#64748b", anchor="start"))
    frags.append(text(460, 215, "};", size=12, bold=True, color="#14532d", anchor="start"))
    frags.append(text(460, 245, "-> .probe(struct platform_device*)", size=12, bold=True, color="#b91c1c", anchor="start"))

    svg_render(os.path.join(out_dir, "img", "dt-node-matching.svg"), w, h, *frags)

def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(out_dir, "img"), exist_ok=True)
    render_dt_lifecycle(out_dir)
    render_fdt_layout(out_dir)
    render_dt_node_matching(out_dir)

if __name__ == "__main__":
    render()
