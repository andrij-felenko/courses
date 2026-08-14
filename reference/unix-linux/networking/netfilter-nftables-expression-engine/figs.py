import sys
import os

# Add scripts directory to path to find svgkit
script_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")
sys.path.insert(0, os.path.normpath(script_dir))

from svgkit import (
    render, textbox, fitbox, rect, text, arrow, line, circle,
    FILL, LINE, INK, POS, NEG, FIELD, MUTED, BG
)

def generate_nftables_arch():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "nftables-arch.svg")
    
    w, h = 830, 480
    frags = []
    
    # Outer panels for Userspace and Kernel Space
    # Userspace panel (left: 20 to 330)
    frags.append(rect(20, 20, 310, 440, fill="#f8fafd", stroke="#94a3b8", sw=1.5, rx=10))
    frags.append(text(175, 48, "Простір користувача", size=15, bold=True, color="#1e293b"))
    frags.append(text(175, 68, "(Userspace)", size=13, color="#64748b"))
    
    # Bridge area (middle: 340 to 480)
    frags.append(rect(340, 210, 140, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(410, 235, "Netlink (nfnetlink)", size=12, bold=True, color="#92400e"))
    
    # Kernel Space panel (right: 490 to 800)
    frags.append(rect(490, 20, 320, 440, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=10))
    frags.append(text(650, 48, "Ядро Linux", size=15, bold=True, color="#0f172a"))
    frags.append(text(650, 68, "(Kernel Space)", size=13, color="#64748b"))
    
    # Userspace Components
    tb_nft, _, _ = textbox(175, 115, "Утиліта nft\n(CLI & парсер правил)", size=12, pad=8, fill="#ffffff", stroke="#0284c7", sw=1.5)
    frags.append(tb_nft)
    
    tb_lib, _, _ = textbox(175, 230, "Бібліотека libnftnl\n(Компіляція байт-коду)", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7", sw=1.5)
    frags.append(tb_lib)
    
    # Arrow nft -> libnftnl
    frags.append(arrow(175, 145, 175, 198, color="#0284c7", sw=2))
    
    # Arrows through Netlink
    frags.append(arrow(260, 230, 335, 230, color="#d97706", sw=2))
    frags.append(arrow(485, 230, 540, 230, color="#d97706", sw=2))
    
    # Kernel Components
    tb_vm, _, _ = textbox(650, 115, "Віртуальна машина nftables\n(Цикл nft_do_chain)", size=12, pad=8, fill="#dcfce7", stroke="#16a34a", sw=1.5)
    frags.append(tb_vm)
    
    tb_regs, _, _ = textbox(650, 230, "Регістри та Вирази\n(struct nft_regs & nft_expr)", size=12, pad=8, fill="#ffffff", stroke="#16a34a", sw=1.5)
    frags.append(tb_regs)
    
    tb_sets, _, _ = textbox(650, 335, "Набори та Карти O(1)\n(rhashtable / rbtree)", size=12, pad=8, fill="#fef2f2", stroke="#dc2626", sw=1.5)
    frags.append(tb_sets)
    
    # Netfilter hooks box at bottom of kernel space
    tb_hooks, _, _ = textbox(650, 420, "Хуки Netfilter (PRE_ROUTING / LOCAL_IN ...)\nsk_buff пакет", size=11, pad=8, fill="#f3e8ff", stroke="#9333ea", sw=1.5)
    frags.append(tb_hooks)
    
    # Kernel internal arrows
    frags.append(arrow(650, 395, 650, 365, color="#9333ea", sw=2))
    frags.append(arrow(650, 305, 650, 260, color="#16a34a", sw=2))
    frags.append(arrow(650, 200, 650, 145, color="#16a34a", sw=2))
    
    render(out_file, w, h, *frags)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    generate_nftables_arch()
