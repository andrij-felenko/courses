# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, rect, text, mtext, line, arrow, circle, textbox, FILL, LINE, INK, MUTED, POS, NEG, FIELD

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def draw_spdm_flow():
    w, h = 720, 500
    frags = []
    
    # Заголовок та дві колонки: Host (Requestor) та PCIe Device (Responder)
    frags.append(rect(60, 40, 240, 45, fill="#e8f4fc", stroke="#2980b9", sw=2, rx=6))
    frags.append(text(180, 68, "Host / Kernel (Requestor)", size=14, bold=True, color="#1c5980"))
    
    frags.append(rect(420, 40, 240, 45, fill="#fef9e7", stroke="#f39c12", sw=2, rx=6))
    frags.append(text(540, 68, "PCIe Device (Responder)", size=14, bold=True, color="#7f8c8d"))
    
    # Пунктирні лінії життєвого циклу
    frags.append(line(180, 85, 180, 470, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(540, 85, 540, 470, color=MUTED, sw=1.5, dash="4,4"))
    
    # Фаза 1: Discovery & Negotiation
    y = 115
    frags.append(rect(40, y-10, 640, 70, fill="#f8f9fa", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(360, y+10, "1. Discovery & Negotiation", size=12, bold=True, color=MUTED))
    frags.append(arrow(180, y+30, 540, y+30, color="#2980b9", sw=1.8))
    frags.append(text(360, y+24, "GET_VERSION / GET_CAPABILITIES / NEGOTIATE_ALGORITHMS", size=11, bold=True, color="#2980b9"))
    frags.append(arrow(540, y+50, 180, y+50, color="#27ae60", sw=1.8))
    frags.append(text(360, y+44, "VERSION / CAPABILITIES / ALGORITHMS", size=11, bold=True, color="#27ae60"))
    
    # Фаза 2: Identity & Certificates
    y = 205
    frags.append(rect(40, y-10, 640, 70, fill="#f8f9fa", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(360, y+10, "2. Identity & Certificate Chain", size=12, bold=True, color=MUTED))
    frags.append(arrow(180, y+30, 540, y+30, color="#2980b9", sw=1.8))
    frags.append(text(360, y+24, "GET_DIGESTS / GET_CERTIFICATE (Slot 0..7)", size=11, bold=True, color="#2980b9"))
    frags.append(arrow(540, y+50, 180, y+50, color="#27ae60", sw=1.8))
    frags.append(text(360, y+44, "DIGESTS / CERTIFICATE (Device Root of Trust Chain)", size=11, bold=True, color="#27ae60"))
    
    # Фаза 3: Challenge & Attestation Measurements
    y = 295
    frags.append(rect(40, y-10, 640, 70, fill="#f8f9fa", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(360, y+10, "3. Challenge & Measurement Attestation", size=12, bold=True, color=MUTED))
    frags.append(arrow(180, y+30, 540, y+30, color="#2980b9", sw=1.8))
    frags.append(text(360, y+24, "CHALLENGE (Nonce) / GET_MEASUREMENTS (Slot 1..N)", size=11, bold=True, color="#2980b9"))
    frags.append(arrow(540, y+50, 180, y+50, color="#27ae60", sw=1.8))
    frags.append(text(360, y+44, "CHALLENGE_AUTH / MEASUREMENTS (Signed Hash Block)", size=11, bold=True, color="#27ae60"))
    
    # Фаза 4: Session & Key Exchange (IDE Setup)
    y = 385
    frags.append(rect(40, y-10, 640, 70, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(360, y+10, "4. Session Establishment & IDE Key Exchange", size=12, bold=True, color="#1e8449"))
    frags.append(arrow(180, y+30, 540, y+30, color="#2980b9", sw=1.8))
    frags.append(text(360, y+24, "KEY_EXCHANGE (Diffie-Hellman / Ephemeral Key)", size=11, bold=True, color="#2980b9"))
    frags.append(arrow(540, y+50, 180, y+50, color="#27ae60", sw=1.8))
    frags.append(text(360, y+44, "KEY_EXCHANGE_RSP / FINISH (Shared Keys Established)", size=11, bold=True, color="#27ae60"))

    render(os.path.join(IMG_DIR, "spdm-flow.svg"), w, h, *frags)

def draw_ide():
    w, h = 720, 360
    frags = []
    
    # Root Complex Box
    frags.append(rect(30, 60, 200, 240, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=8))
    frags.append(text(130, 90, "PCIe Root Complex", size=14, bold=True, color="#1b4f72"))
    frags.append(rect(45, 120, 170, 50, fill="#ffffff", stroke="#2980b9", sw=1, rx=4))
    frags.append(text(130, 140, "Host Memory / CPU", size=11, bold=True))
    frags.append(text(130, 158, "(IOMMU Translation)", size=10, color=MUTED))
    
    frags.append(rect(45, 200, 170, 80, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(130, 225, "Host IDE Controller", size=12, bold=True, color="#1e8449"))
    frags.append(text(130, 245, "AES-256-GCM Engine", size=11, color="#1e8449"))
    frags.append(text(130, 265, "Session Key K_enc/K_mac", size=10, color=MUTED))
    
    # PCIe Bus Link Box
    frags.append(rect(260, 100, 200, 180, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=8))
    frags.append(text(360, 125, "PCIe Bus Channel", size=13, bold=True, color="#7e5109"))
    frags.append(rect(275, 145, 170, 115, fill="#ffffff", stroke="#f39c12", sw=1, rx=4))
    frags.append(text(360, 168, "IDE TLP Packet", size=11, bold=True, color="#7e5109"))
    frags.append(rect(285, 180, 150, 24, fill="#fadbd8", stroke="#e74c3c", sw=1, rx=2))
    frags.append(text(360, 196, "Encrypted Payload (C)", size=10, color="#78281f"))
    frags.append(rect(285, 208, 150, 22, fill="#d5f5e3", stroke="#27ae60", sw=1, rx=2))
    frags.append(text(360, 223, "IDE Prefix + MAC (96-bit)", size=10, color="#1e8449"))
    frags.append(text(360, 248, "Stream ID + Replay Counter", size=9, color=MUTED))
    
    # PCIe Endpoint Device Box
    frags.append(rect(490, 60, 200, 240, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=8))
    frags.append(text(590, 90, "PCIe Endpoint Device", size=14, bold=True, color="#1b4f72"))
    
    frags.append(rect(505, 200, 170, 80, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(590, 225, "Device IDE Controller", size=12, bold=True, color="#1e8449"))
    frags.append(text(590, 245, "AES-256-GCM Engine", size=11, color="#1e8449"))
    frags.append(text(590, 265, "Session Key K_enc/K_mac", size=10, color=MUTED))
    
    frags.append(rect(505, 120, 170, 50, fill="#f5eeed", stroke="#c0392b", sw=1, rx=4))
    frags.append(text(590, 140, "Device Firmware / RoT", size=11, bold=True, color="#78281f"))
    frags.append(text(590, 158, "(SPDM Measurement Engine)", size=10, color=MUTED))
    
    # Arrows between controllers
    frags.append(arrow(215, 225, 260, 225, color="#27ae60", sw=2))
    frags.append(arrow(460, 225, 490, 225, color="#27ae60", sw=2))
    
    # SPDM Key loading arrow from RoT to Device IDE
    frags.append(arrow(590, 170, 590, 200, color="#c0392b", sw=1.5))
    frags.append(text(600, 188, "Key Sync", size=9, bold=True, color="#c0392b", anchor="start"))
    
    render(os.path.join(IMG_DIR, "pcie-ide.svg"), w, h, *frags)

def draw_doe_cma_stack():
    w, h = 680, 360
    frags = []
    
    frags.append(text(340, 30, "Стек протоколів атестації та шифрування PCIe", size=15, bold=True))
    
    layers = [
        ("SPDM / IDE Control Protocol", "Формування запитів атестації, вимірювань та підписів", "#e8f8f5", "#16a085"),
        ("CMA (Component Measurement & Auth)", "Стандартний сабпротокол PCI SIG над SPDM", "#eaf2f8", "#2980b9"),
        ("MCTP / DOE Data Transfer", "Data Object Exchange / Management Component Protocol", "#fef9e7", "#f39c12"),
        ("PCIe Extended Capability Space", "Регістри DOE Mailbox (Cap ID 0x002E) у конфіг-просторі", "#f4ecf7", "#8e44ad"),
        ("PCIe Data Link & Physical Layer", "Фізична шина, TLP транзакції, шифрування IDE (AES-GCM)", "#fadbd8", "#c0392b")
    ]
    
    y = 60
    for title_text, desc_text, bg_color, border_color in layers:
        frags.append(rect(60, y, 560, 50, fill=bg_color, stroke=border_color, sw=1.5, rx=6))
        frags.append(text(340, y + 22, title_text, size=13, bold=True, color=border_color))
        frags.append(text(340, y + 40, desc_text, size=11, color=MUTED))
        y += 58

    render(os.path.join(IMG_DIR, "doe-cma-stack.svg"), w, h, *frags)

if __name__ == "__main__":
    draw_spdm_flow()
    draw_ide()
    draw_doe_cma_stack()
    print("Figures generated successfully.")
