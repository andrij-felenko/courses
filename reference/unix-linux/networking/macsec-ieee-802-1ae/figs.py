import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_svg():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. MACsec Frame Diagram
    path1 = os.path.join(out_dir, "macsec-frame.svg")
    frags1 = []
    
    # Ethernet Header
    frags1.append(svgkit.rect(20, 70, 90, 45, fill="#e8edf5", stroke="#3b6998"))
    frags1.append(svgkit.text(65, 92, "Dest MAC", size=12, bold=True))
    frags1.append(svgkit.text(65, 107, "(6 байт)", size=10, color="#6b7280"))
    
    frags1.append(svgkit.rect(110, 70, 90, 45, fill="#e8edf5", stroke="#3b6998"))
    frags1.append(svgkit.text(155, 92, "Src MAC", size=12, bold=True))
    frags1.append(svgkit.text(155, 107, "(6 байт)", size=10, color="#6b7280"))
    
    # SecTAG (802.1AE)
    frags1.append(svgkit.rect(200, 70, 150, 45, fill="#fde8e8", stroke="#c0392b"))
    frags1.append(svgkit.text(275, 89, "SecTAG (802.1AE)", size=12, bold=True, color="#c0392b"))
    frags1.append(svgkit.text(275, 104, "ET=0x88E5 | TCI | PN | SCI", size=9, color="#7f1d1d"))
    
    # EtherType / Length
    frags1.append(svgkit.rect(350, 70, 80, 45, fill="#e8edf5", stroke="#3b6998"))
    frags1.append(svgkit.text(390, 92, "EtherType", size=11, bold=True))
    frags1.append(svgkit.text(390, 107, "(2 байти)", size=10, color="#6b7280"))
    
    # Encrypted Payload
    frags1.append(svgkit.rect(430, 70, 210, 45, fill="#e6f4ea", stroke="#27ae60"))
    frags1.append(svgkit.text(535, 89, "Зашифроване навантаження", size=12, bold=True, color="#1e7e34"))
    frags1.append(svgkit.text(535, 104, "IP-пакет / ARP / LLDP / VLAN", size=9, color="#145a32"))
    
    # ICV
    frags1.append(svgkit.rect(640, 70, 100, 45, fill="#fde8e8", stroke="#c0392b"))
    frags1.append(svgkit.text(690, 89, "ICV", size=12, bold=True, color="#c0392b"))
    frags1.append(svgkit.text(690, 104, "AES-GCM (16B)", size=10, color="#7f1d1d"))
    
    # FCS
    frags1.append(svgkit.rect(740, 70, 70, 45, fill="#e8edf5", stroke="#3b6998"))
    frags1.append(svgkit.text(775, 92, "FCS", size=11, bold=True))
    frags1.append(svgkit.text(775, 107, "(4 байти)", size=10, color="#6b7280"))
    
    # Encryption bracket
    frags1.append(svgkit.line(430, 50, 640, 50, color="#27ae60", sw=2))
    frags1.append(svgkit.line(430, 50, 430, 58, color="#27ae60", sw=2))
    frags1.append(svgkit.line(640, 50, 640, 58, color="#27ae60", sw=2))
    frags1.append(svgkit.text(535, 40, "Конфіденційність: AES-GCM шифрування", size=11, color="#1e7e34", bold=True))
    
    # Authentication bracket
    frags1.append(svgkit.line(200, 135, 740, 135, color="#c0392b", sw=2))
    frags1.append(svgkit.line(200, 135, 200, 127, color="#c0392b", sw=2))
    frags1.append(svgkit.line(740, 135, 740, 127, color="#c0392b", sw=2))
    frags1.append(svgkit.text(470, 152, "Цілісність та автентичність: охоплення підписом ICV (MACsec Protection)", size=11, color="#c0392b", bold=True))
    
    svgkit.render(path1, 830, 175, *frags1, title="MACsec Frame Format")
    
    # 2. Kernel Packet Path Diagram
    path2 = os.path.join(out_dir, "macsec-kernel-path.svg")
    frags2 = []
    
    # User space box
    frags2.append(svgkit.rect(20, 20, 760, 50, fill="#f8f9fa", stroke="#6c757d", rx=8))
    frags2.append(svgkit.text(400, 40, "Простір користувача: додатки / wpa_supplicant (MKA)", size=13, bold=True, color="#212529"))
    frags2.append(svgkit.text(400, 56, "Сокети AF_INET/AF_PACKET | RTNETLINK API управління ключами SAK/CAK", size=10, color="#6c757d"))
    
    # Kernel Space container box
    frags2.append(svgkit.rect(20, 85, 760, 235, fill="#f4f6f8", stroke="#333333", rx=8))
    frags2.append(svgkit.text(90, 105, "Ядро Linux (Kernel space)", size=12, bold=True, color="#1a1a1a"))
    
    # Virtual macsec0 box
    frags2.append(svgkit.rect(40, 125, 190, 60, fill="#e8edf5", stroke="#2457d6", rx=6))
    frags2.append(svgkit.text(135, 148, "macsec0 (віртуальний)", size=12, bold=True, color="#2457d6"))
    frags2.append(svgkit.text(135, 166, "net_device (чистий skb)", size=10, color="#3b6998"))
    
    # MACsec module (Software Crypto / AES-GCM)
    frags2.append(svgkit.rect(260, 125, 270, 175, fill="#fff3cd", stroke="#ffc107", rx=6))
    frags2.append(svgkit.text(395, 143, "Модуль macsec.ko & Crypto API", size=12, bold=True, color="#856404"))
    frags2.append(svgkit.text(395, 163, "• macsec_start_xmit() (TX)", size=10, color="#533f03"))
    frags2.append(svgkit.text(395, 181, "• macsec_handle_frame() (RX)", size=10, color="#533f03"))
    frags2.append(svgkit.text(395, 199, "• crypto_aead_encrypt/decrypt", size=10, color="#533f03"))
    frags2.append(svgkit.text(395, 217, "• Перевірка вікна Replay Window", size=10, color="#533f03"))
    frags2.append(svgkit.text(395, 235, "• Вставка заголовка SecTAG & ICV", size=10, color="#533f03"))
    frags2.append(svgkit.text(395, 255, "• SW Fallback (без розвантаження)", size=10, bold=True, color="#c0392b"))
    
    # Physical eth0 box
    frags2.append(svgkit.rect(560, 125, 200, 60, fill="#e8edf5", stroke="#2457d6", rx=6))
    frags2.append(svgkit.text(660, 148, "eth0 (фізичний NIC)", size=12, bold=True, color="#2457d6"))
    frags2.append(svgkit.text(660, 166, "dev_queue_xmit / rx_handler", size=10, color="#3b6998"))
    
    # Hardware Offload Path (NIC HW / SmartNIC ASIC)
    frags2.append(svgkit.rect(560, 215, 200, 75, fill="#e6f4ea", stroke="#27ae60", rx=6))
    frags2.append(svgkit.text(660, 235, "SmartNIC MACsec HW", size=12, bold=True, color="#1e7e34"))
    frags2.append(svgkit.text(660, 253, "macsec_ops (HW Offload)", size=10, color="#145a32"))
    frags2.append(svgkit.text(660, 270, "Апаратний AES-GCM (100G+)", size=9, color="#145a32"))
    
    # Arrows
    frags2.append(svgkit.arrow(230, 145, 260, 145, color="#2457d6", sw=2))
    frags2.append(svgkit.arrow(530, 145, 560, 145, color="#2457d6", sw=2))
    frags2.append(svgkit.text(245, 138, "TX", size=9, color="#2457d6"))
    frags2.append(svgkit.text(545, 138, "Enc", size=9, color="#2457d6"))
    
    frags2.append(svgkit.arrow(560, 165, 530, 165, color="#c0392b", sw=2))
    frags2.append(svgkit.arrow(260, 165, 230, 165, color="#c0392b", sw=2))
    frags2.append(svgkit.text(545, 176, "RX", size=9, color="#c0392b"))
    frags2.append(svgkit.text(245, 176, "Dec", size=9, color="#c0392b"))
    
    # Offload Bypass Line & Arrow
    frags2.append(svgkit.line(135, 185, 135, 250, color="#27ae60", sw=2))
    frags2.append(svgkit.line(135, 250, 560, 250, color="#27ae60", sw=2))
    frags2.append(svgkit.arrow(550, 250, 560, 250, color="#27ae60", sw=2))
    frags2.append(svgkit.text(340, 243, "HW Offload Path (обхід CPU)", size=10, color="#1e7e34", bold=True))
    
    svgkit.render(path2, 800, 335, *frags2, title="Linux Kernel MACsec Architecture & Offload Path")

if __name__ == "__main__":
    render_svg()
