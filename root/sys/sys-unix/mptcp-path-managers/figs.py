import sys
import os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import svgkit

def create_mptcp_path_management_svg():
    width = 860
    height = 480
    
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    out.append('<defs>')
    out.append('<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#333333" />')
    out.append('</marker>')
    out.append('<marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#2457d6" />')
    out.append('</marker>')
    out.append('<marker id="arrow-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#c0392b" />')
    out.append('</marker>')
    out.append('</defs>')
    
    # Background
    out.append(svgkit.rect(0, 0, width, height, fill="#ffffff", stroke="#ffffff", sw=0))
    
    # Title
    out.append(svgkit.text(width / 2, 25, "Архітектура розділення керування шляхами в Linux MPTCP", size=16, bold=True))
    
    # --- USER SPACE CONTAINER ---
    out.append(svgkit.rect(30, 45, 800, 175, fill="#fcf8f2", stroke="#d97706", sw=1.5, rx=8))
    out.append(svgkit.text(50, 72, "Простір користувача (Userspace)", size=13, color="#b45309", anchor="start", bold=True))
    
    # ip mptcp box
    box1, w1, h1 = svgkit.textbox(160, 135, "ip mptcp\nCLI-утиліта", size=13, pad=12, fill="#ffffff", stroke="#d97706")
    out.append(box1)
    
    # mptcpd daemon box
    box2, w2, h2 = svgkit.textbox(430, 135, "Демон mptcpd\nUserspace PM (pm_type=1)", size=13, pad=12, fill="#ffffff", stroke="#d97706", bold=True)
    out.append(box2)
    
    # plugin box
    box3, w3, h3 = svgkit.textbox(690, 135, "Динамічні плагіни\nsspi / custom policy", size=12, pad=10, fill="#fef3c7", stroke="#d97706")
    out.append(box3)
    
    # Line between mptcpd and plugins
    out.append(svgkit.line(540, 135, 605, 135, color="#d97706", sw=1.5))
    out.append(svgkit.text(572, 123, "dlopen / C API", size=10, color="#b45309", anchor="middle"))

    # --- KERNEL SPACE CONTAINER ---
    out.append(svgkit.rect(30, 250, 800, 205, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    out.append(svgkit.text(50, 275, "Простір ядра Linux (Kernel Space)", size=13, color="#0369a1", anchor="start", bold=True))
    
    # Generic Netlink API box
    box4, w4, h4 = svgkit.textbox(430, 315, "Generic Netlink API (GENL_NAME_MPTCP)\nMulticast події та Unicast команди", size=12, pad=10, fill="#ffffff", stroke="#0284c7")
    out.append(box4)
    
    # In-kernel PM box
    box5, w5, h5 = svgkit.textbox(160, 400, "In-Kernel Path Manager\npm_type=0 (static rules)", size=12, pad=10, fill="#e0f2fe", stroke="#0284c7")
    out.append(box5)
    
    # MPTCP Core & Socket layer box
    box6, w6, h6 = svgkit.textbox(600, 400, "Ядро MPTCP (struct mptcp_sock)\nПідпотоки & Опції ADD_ADDR / MP_JOIN", size=12, pad=10, fill="#ffffff", stroke="#0284c7", bold=True)
    out.append(box6)
    
    # Interconnections
    # 1. ip mptcp to In-kernel PM
    out.append(svgkit.arrow(160, 170, 160, 365, color="#0369a1", sw=1.5))
    out.append(svgkit.text(100, 238, "Netlink RT/GENL\nстатичні ліміти", size=10, color="#0369a1", anchor="middle"))

    # 2. Netlink to mptcpd (bidirectional IPC)
    out.append(svgkit.arrow(410, 280, 410, 175, color="#2457d6", sw=1.8))
    out.append(svgkit.text(355, 235, "Multicast події\nMPTCP_EVENT_*", size=10, color="#2457d6", anchor="end"))
    
    out.append(svgkit.arrow(450, 175, 450, 280, color="#c0392b", sw=1.8))
    out.append(svgkit.text(495, 235, "Unicast команди\nMPTCP_PM_CMD_*", size=10, color="#c0392b", anchor="start"))
    
    # 3. Generic Netlink to MPTCP Core
    out.append(svgkit.line(470, 345, 520, 370, color="#0284c7", sw=1.5))
    
    # 4. In-kernel PM to MPTCP Core
    out.append(svgkit.line(265, 400, 450, 400, color="#0284c7", sw=1.5))
    
    out.append('</svg>')
    return "\n".join(out)

def create_mptcp_netlink_flow_svg():
    width = 850
    height = 420
    
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    out.append('<defs>')
    out.append('<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#333333" />')
    out.append('</marker>')
    out.append('<marker id="arrow-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#c0392b" />')
    out.append('</marker>')
    out.append('<marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    out.append('<polygon points="0 0, 10 3.5, 0 7" fill="#2457d6" />')
    out.append('</marker>')
    out.append('</defs>')
    
    # Background
    out.append(svgkit.rect(0, 0, width, height, fill="#ffffff", stroke="#ffffff", sw=0))
    
    # Title
    out.append(svgkit.text(width / 2, 25, "Послідовність викликів Netlink при обробці події ADD_ADDR", size=16, bold=True))
    
    # Lifelines X coordinates
    x_remote = 100
    x_kernel = 360
    x_mptcpd = 620
    x_plugin = 770
    
    # Lifeline Headers
    box_r, _, _ = svgkit.textbox(x_remote, 60, "Віддалений вузол\n(Peer)", size=12, pad=8, fill="#f4f6f8", stroke="#333333")
    box_k, _, _ = svgkit.textbox(x_kernel, 60, "Ядро Linux\n(MPTCP Stack)", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7", bold=True)
    box_m, _, _ = svgkit.textbox(x_mptcpd, 60, "Демон mptcpd\n(Netlink Socket)", size=12, pad=8, fill="#fcf8f2", stroke="#d97706", bold=True)
    box_p, _, _ = svgkit.textbox(x_plugin, 60, "Плагін mptcpd\n(Policy Logic)", size=12, pad=8, fill="#fef3c7", stroke="#d97706")
    
    out.extend([box_r, box_k, box_m, box_p])
    
    # Lifeline Vertical dashed lines
    y_start = 90
    y_end = 390
    out.append(svgkit.line(x_remote, y_start, x_remote, y_end, color="#9ca3af", dash="4,4"))
    out.append(svgkit.line(x_kernel, y_start, x_kernel, y_end, color="#9ca3af", dash="4,4"))
    out.append(svgkit.line(x_mptcpd, y_start, x_mptcpd, y_end, color="#9ca3af", dash="4,4"))
    out.append(svgkit.line(x_plugin, y_start, x_plugin, y_end, color="#9ca3af", dash="4,4"))
    
    # Message 1: Peer sends TCP Option ADD_ADDR
    y1 = 125
    out.append(svgkit.arrow(x_remote, y1, x_kernel, y1, color="#333333", sw=1.8))
    out.append(svgkit.text((x_remote + x_kernel) / 2, y1 - 8, "TCP Packet з опцією ADD_ADDR", size=11, bold=True))
    
    # Message 2: Kernel fires MPTCP_EVENT_ANNOUNCED via Netlink
    y2 = 175
    out.append(svgkit.arrow(x_kernel, y2, x_mptcpd, y2, color="#2457d6", sw=1.8))
    out.append(svgkit.text((x_kernel + x_mptcpd) / 2, y2 - 8, "Generic Netlink: MPTCP_EVENT_ANNOUNCED", size=11, color="#2457d6"))
    
    # Message 3: mptcpd invokes plugin callback
    y3 = 225
    out.append(svgkit.arrow(x_mptcpd, y3, x_plugin, y3, color="#d97706", sw=1.5))
    out.append(svgkit.text((x_mptcpd + x_plugin) / 2, y3 - 8, "new_address()", size=11, color="#b45309"))
    
    # Message 4: Plugin returns order to create subflow
    y4 = 275
    out.append(svgkit.arrow(x_plugin, y4, x_mptcpd, y4, color="#d97706", sw=1.5))
    out.append(svgkit.text((x_mptcpd + x_plugin) / 2, y4 - 8, "add_subflow()", size=11, color="#b45309"))
    
    # Message 5: mptcpd sends MPTCP_PM_CMD_SUBFLOW_CREATE unicast command to kernel
    y5 = 325
    out.append(svgkit.arrow(x_mptcpd, y5, x_kernel, y5, color="#c0392b", sw=1.8))
    out.append(svgkit.text((x_kernel + x_mptcpd) / 2, y5 - 8, "Netlink CMD: MPTCP_PM_CMD_SUBFLOW_CREATE", size=11, color="#c0392b"))
    
    # Message 6: Kernel sends MP_JOIN SYN packet
    y6 = 370
    out.append(svgkit.arrow(x_kernel, y6, x_remote, y6, color="#333333", sw=1.8))
    out.append(svgkit.text((x_remote + x_kernel) / 2, y6 - 8, "TCP SYN з опцією MP_JOIN (новий підпотік)", size=11, bold=True))
    
    out.append('</svg>')
    return "\n".join(out)

def render():
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    # Remove any old file with underscores
    for f in os.listdir(img_dir):
        if "_" in f and f.endswith(".svg"):
            try:
                os.remove(os.path.join(img_dir, f))
            except Exception:
                pass
    
    f1_path = os.path.join(img_dir, "mptcp-path-management.svg")
    with open(f1_path, "w", encoding="utf-8") as f:
        f.write(create_mptcp_path_management_svg())
    print(f"Generated {f1_path}")
    
    f2_path = os.path.join(img_dir, "mptcp-netlink-flow.svg")
    with open(f2_path, "w", encoding="utf-8") as f:
        f.write(create_mptcp_netlink_flow_svg())
    print(f"Generated {f2_path}")

if __name__ == "__main__":
    render()
