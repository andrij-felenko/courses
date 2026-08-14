import os
import sys

# Ensure scripts directory is in sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")
    ),
)
from svgkit import *

def generate_arch_fig():
    """Generates ethtool-arch.svg showing ioctl vs Generic Netlink architecture."""
    w, h = 800, 420
    body = []
    
    # Background & Title
    body.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    body.append(text(400, 32, "Еволюція архітектури ethtool: ioctl vs Generic Netlink", size=18, bold=True, color=INK))
    
    # Boundary lines
    body.append(line(40, 140, 760, 140, color=MUTED, sw=1.5, dash="6,4"))
    body.append(text(740, 128, "Межа ядра (Kernel Boundary)", size=11, color=MUTED, anchor="end", italic=True))
    
    # User space block
    body.append(rect(40, 48, 720, 72, fill="#f0f7ff", stroke="#2563eb", sw=1.5, rx=6))
    body.append(text(400, 68, "Простір користувача (User Space)", size=14, bold=True, color="#1e40af"))
    
    # User space apps
    b1 = fitbox(60, 80, 200, 30, "ethtool (CLI)", size=12, fill="#ffffff", stroke="#3b82f6")
    b2 = fitbox(300, 80, 200, 30, "NetworkManager / systemd", size=11, fill="#ffffff", stroke="#3b82f6")
    b3 = fitbox(540, 80, 200, 30, "Custom Netlink Application", size=11, fill="#ffffff", stroke="#3b82f6")
    body.extend([b1, b2, b3])
    
    # Kernel Space block
    body.append(rect(40, 160, 720, 240, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    body.append(text(400, 182, "Простір ядра (Kernel Space)", size=14, bold=True, color="#166534"))
    
    # Left Path: Legacy ioctl
    body.append(rect(60, 200, 320, 120, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    body.append(text(220, 220, "Традиційний ioctl (SIOCETHTOOL)", size=13, bold=True, color="#991b1b"))
    body.append(text(220, 242, "• Фіксовані структури ethtool_cmd", size=11, color="#7f1d1d"))
    body.append(text(220, 260, "• Синхронний блокуючий запит", size=11, color="#7f1d1d"))
    body.append(text(220, 278, "• Немає подій та розширених помилок", size=11, color="#7f1d1d"))
    body.append(text(220, 296, "• Вимагає повний CAP_NET_ADMIN", size=11, color="#7f1d1d"))
    
    # Right Path: Generic Netlink
    body.append(rect(420, 200, 320, 120, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    body.append(text(580, 220, "Generic Netlink ethtool API", size=13, bold=True, color="#1e40af"))
    body.append(text(580, 242, "• Гнучкий формат TLV (Netlink Attributes)", size=11, color="#1e3a8a"))
    body.append(text(580, 260, "• Асинхронні сповіщення (Multicast)", size=11, color="#1e3a8a"))
    body.append(text(580, 278, "• Детальні помилки extack (NLMSGERR)", size=11, color="#1e3a8a"))
    body.append(text(580, 296, "• Масовий запит стану кількох NIC", size=11, color="#1e3a8a"))
    
    # Driver Dispatch Layer
    body.append(rect(180, 340, 440, 48, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=6))
    body.append(text(400, 358, "Ядро: ethnl_ops → ethtool_ops драйвера NIC", size=13, bold=True, color="#854d0e"))
    body.append(text(400, 376, "(netdev->ethtool_ops->get_link_ksettings)", size=11, color="#713f12", italic=True))
    
    # Connection lines
    body.append(line(220, 120, 220, 200, color="#dc2626", sw=2))
    body.append(line(580, 120, 580, 200, color="#2563eb", sw=2))
    body.append(line(220, 320, 310, 340, color="#dc2626", sw=1.5))
    body.append(line(580, 320, 490, 340, color="#2563eb", sw=1.5))
    
    svg_content = assemble_svg(body, w, h)
    return svg_content

def generate_msg_fig():
    """Generates netlink-msg-structure.svg showing structure of ethtool Netlink frame."""
    w, h = 800, 380
    body = []
    
    # Background & Title
    body.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    body.append(text(400, 30, "Анатомія повідомлення ethtool Generic Netlink", size=18, bold=True, color=INK))
    
    # Outer frame
    body.append(rect(30, 55, 740, 300, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    body.append(text(400, 75, "Кадр Netlink (sk_buff / buffer)", size=13, bold=True, color="#334155"))
    
    # Layer 1: Netlink Header (nlmsghdr)
    body.append(rect(50, 95, 160, 235, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    body.append(text(130, 118, "nlmsghdr (16B)", size=13, bold=True, color="#0369a1"))
    body.append(text(130, 148, "nlmsg_len", size=11, color="#075985"))
    body.append(text(130, 178, "nlmsg_type (ethtool)", size=11, color="#075985"))
    body.append(text(130, 208, "nlmsg_flags (NLM_F_*)", size=11, color="#075985"))
    body.append(text(130, 238, "nlmsg_seq (послідовність)", size=11, color="#075985"))
    body.append(text(130, 268, "nlmsg_pid (порт)", size=11, color="#075985"))
    
    # Layer 2: Generic Netlink Header (genlmsghdr)
    body.append(rect(220, 95, 150, 235, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    body.append(text(295, 118, "genlmsghdr (4B)", size=13, bold=True, color="#b45309"))
    body.append(text(295, 158, "cmd:", size=11, bold=True, color="#92400e"))
    body.append(text(295, 178, "ETHTOOL_MSG_", size=10, color="#92400e"))
    body.append(text(295, 193, "LINKMODES_GET", size=10, bold=True, color="#92400e"))
    body.append(text(295, 238, "version: 1", size=11, color="#92400e"))
    body.append(text(295, 268, "reserved: 0", size=11, color="#92400e"))
    
    # Layer 3: Ethtool Header Attribute (ETHTOOL_A_HEADER)
    body.append(rect(380, 95, 180, 235, fill="#fce7f3", stroke="#db2777", sw=1.5, rx=6))
    body.append(text(470, 118, "ETHTOOL_A_HEADER", size=13, bold=True, color="#be185d"))
    body.append(text(470, 145, "Вкладений NLA атрибут", size=10, italic=True, color="#9d174d"))
    body.append(text(470, 180, "DEV_INDEX: 2", size=11, bold=True, color="#9d174d"))
    body.append(text(470, 210, "DEV_NAME: \"eth0\"", size=11, bold=True, color="#9d174d"))
    body.append(text(470, 240, "FLAGS: COMPACT_BITSETS", size=10, color="#9d174d"))
    
    # Layer 4: Command Payload Attributes (NLA TLV)
    body.append(rect(570, 95, 200, 235, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    body.append(text(670, 118, "Корисне навантаження", size=13, bold=True, color="#15803d"))
    body.append(text(670, 143, "TLVs (Type-Length-Value)", size=10, italic=True, color="#166534"))
    body.append(text(670, 178, "LINKMODES_AUTONEG", size=11, color="#166534"))
    body.append(text(670, 208, "LINKMODES_OURS (bitmap)", size=11, color="#166534"))
    body.append(text(670, 238, "LINKMODES_SPEED: 10000", size=11, color="#166534"))
    body.append(text(670, 268, "LINKMODES_DUPLEX: 1", size=11, color="#166534"))
    
    svg_content = assemble_svg(body, w, h)
    return svg_content

def assemble_svg(body_elements, w, h):
    """Assembles final SVG string with appropriate headers and styling."""
    svg = []
    svg.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h))
    svg.append('  <defs>')
    svg.append('    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">')
    svg.append('      <path d="M 0 0 L 8 4 L 0 8 z" fill="%s"/>' % LINE)
    svg.append('    </marker>')
    svg.append('  </defs>')
    svg.extend(body_elements)
    svg.append('</svg>')
    return "\n".join(svg)

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    # Remove old files if present
    for old_file in ["ethtool_arch.svg", "netlink_msg_structure.svg"]:
        p = os.path.join(img_dir, old_file)
        if os.path.exists(p):
            os.remove(p)
            
    figs = {
        os.path.join(img_dir, "ethtool-arch.svg"): generate_arch_fig(),
        os.path.join(img_dir, "netlink-msg-structure.svg"): generate_msg_fig()
    }
    for filepath, content in figs.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    render()
