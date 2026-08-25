# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Порівняння 1-RTT TLS 1.3 та 2-RTT TLS 1.2 ────────────────────
def fig_handshake_flow():
    W, H = 880, 520
    p = []
    
    # ── Панель TLS 1.2 (Ліворуч) ──
    x1_l, x1_r = 80.0, 360.0
    p.append(rect(30, 20, 380, 480, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(220, 50, "TLS 1.2 (2 RTT)", size=16, color=INK, bold=True))
    
    # Лінії клієнта і сервера
    p.append(line(x1_l, 70, x1_l, 440, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(x1_r, 70, x1_r, 440, color=MUTED, sw=1.5, dash="4 4"))
    p.append(text(x1_l, 65, "Клієнт", size=12.5, color=INK, bold=True))
    p.append(text(x1_r, 65, "Сервер", size=12.5, color=INK, bold=True))
    
    # RTT 1: ClientHello / ServerHello + Cert + KeyEx + Done
    p.append(arrow(x1_l, 100, x1_r, 130, color=NEG, sw=2.0))
    p.append(text((x1_l + x1_r)/2, 108, "ClientHello (CipherSuites, ClientRandom)", size=11, color=NEG, bold=True))
    
    p.append(arrow(x1_r, 160, x1_l, 190, color=POS, sw=2.0))
    p.append(text((x1_l + x1_r)/2, 168, "ServerHello, Certificate, ServerKeyExchange", size=11, color=POS, bold=True))
    p.append(text((x1_l + x1_r)/2, 182, "ServerHelloDone", size=10, color=MUTED))
    
    # RTT 2: ClientKeyEx + ChangeCipherSpec + Finished / ChangeCipherSpec + Finished
    p.append(arrow(x1_l, 230, x1_r, 260, color=NEG, sw=2.0))
    p.append(text((x1_l + x1_r)/2, 238, "ClientKeyExchange, ChangeCipherSpec", size=11, color=NEG, bold=True))
    p.append(text((x1_l + x1_r)/2, 252, "Finished [Encrypted]", size=10, color=NEG))
    
    p.append(arrow(x1_r, 290, x1_l, 320, color=POS, sw=2.0))
    p.append(text((x1_l + x1_r)/2, 298, "ChangeCipherSpec, Finished [Encrypted]", size=11, color=POS, bold=True))
    
    # Application Data
    p.append(line(35, 340, 405, 340, color=FIELD, sw=1.5, dash="6 4"))
    p.append(text(220, 355, "З'єднання захищено (2 RTT затримки)", size=11.5, color=FIELD, bold=True))
    
    p.append(arrow(x1_l, 380, x1_r, 410, color=FIELD, sw=2.2))
    p.append(text((x1_l + x1_r)/2, 388, "Application Data (HTTP/1.1 або HTTP/2)", size=11, color=FIELD, bold=True))
    
    
    # ── Панель TLS 1.3 (Праворуч) ──
    x2_l, x2_r = 520.0, 800.0
    p.append(rect(470, 20, 380, 480, fill="#eef7f0", stroke="#bfe6cd", sw=1.3, rx=10))
    p.append(text(660, 50, "TLS 1.3 (1 RTT)", size=16, color=FIELD, bold=True))
    
    # Лінії клієнта і сервера
    p.append(line(x2_l, 70, x2_l, 440, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(x2_r, 70, x2_r, 440, color=MUTED, sw=1.5, dash="4 4"))
    p.append(text(x2_l, 65, "Клієнт", size=12.5, color=INK, bold=True))
    p.append(text(x2_r, 65, "Сервер", size=12.5, color=INK, bold=True))
    
    # RTT 1: ClientHello + KeyShare / ServerHello + KeyShare + EncryptedExtensions + Cert + CertVerify + Finished
    p.append(arrow(x2_l, 100, x2_r, 130, color=NEG, sw=2.0))
    p.append(text((x2_l + x2_r)/2, 108, "ClientHello + key_share (ECDHE gⁿ)", size=11, color=NEG, bold=True))
    p.append(text((x2_l + x2_r)/2, 122, "+ cipher_suites (AES-GCM/CHACHA20)", size=10, color=MUTED))
    
    p.append(arrow(x2_r, 175, x2_l, 205, color=POS, sw=2.0))
    p.append(text((x2_l + x2_r)/2, 168, "ServerHello + key_share (ECDHE gᵐ)", size=11, color=POS, bold=True))
    p.append(text((x2_l + x2_r)/2, 184, "{EncryptedExt, Cert, CertVerify, Finished}", size=10, color=FIELD, bold=True))
    p.append(text((x2_l + x2_r)/2, 218, "* Все після ServerHello зашифровано Handshake-ключем", size=9, color=MUTED, italic=True))
    
    # Client Finished + App Data в тому ж RTT!
    p.append(arrow(x2_l, 260, x2_r, 290, color=FIELD, sw=2.2))
    p.append(text((x2_l + x2_r)/2, 268, "{Finished} + Application Data (HTTP/3 / HTTP/2)", size=11, color=FIELD, bold=True))
    
    # Application Data
    p.append(line(475, 340, 845, 340, color=FIELD, sw=1.5, dash="6 4"))
    p.append(text(660, 355, "Дані передаються вже після 1 RTT!", size=11.5, color=FIELD, bold=True))
    
    p.append(arrow(x2_r, 380, x2_l, 410, color=FIELD, sw=2.2))
    p.append(text((x2_l + x2_r)/2, 388, "Application Data (Response)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "tls-handshake-flow.svg"), W, H, *p,
           title="Порівняння затримки рукостискання: TLS 1.2 проти TLS 1.3")

# ── Фігура 2: Ієрархія ключів HKDF та їхня роль ─────────────────────────────
def fig_key_derivation():
    W, H = 840, 480
    p = []
    
    # Заголовок
    p.append(text(W/2, 30, "Граф деривації ключів HKDF у TLS 1.3", size=16, color=INK, bold=True))
    
    # Рівень 0: Early Secret
    b0, w0, h0 = textbox(W/2, 80, "IKM = 00...00  ⟶  HKDF-Extract  ⟶  Early Secret", size=12, fill="#f4f6f8", stroke="#aab4c0", bold=True)
    p.append(b0)
    
    # Стрілка вниз
    p.append(arrow(W/2, 105, W/2, 140, color=INK, sw=1.5))
    p.append(text(W/2 + 70, 122.0, "salt = Derive-Secret", size=10, color=MUTED))
    
    # Рівень 1: Handshake Secret
    b1, w1, h1 = textbox(W/2, 165, "IKM = ECDHE Shared Secret (gⁿᵐ)  ⟶  HKDF-Extract  ⟶  Handshake Secret", size=12.5, fill="#eef7f0", stroke=FIELD, bold=True)
    p.append(b1)
    
    # Відгалуження ключів Handshake
    p.append(arrow(W/2 - 120, 195, W/2 - 200, 240, color=NEG, sw=1.5))
    b_chs, _, _ = textbox(W/2 - 220, 265, "Client Handshake Traffic Key\n+ IV (AES-GCM)", size=11, fill="#eaf0fd", stroke=NEG)
    p.append(b_chs)
    
    p.append(arrow(W/2 + 120, 195, W/2 + 200, 240, color=POS, sw=1.5))
    b_shs, _, _ = textbox(W/2 + 220, 265, "Server Handshake Traffic Key\n+ IV (AES-GCM)", size=11, fill="#fdecea", stroke=POS)
    p.append(b_shs)
    
    # Перехід до Application Master Secret
    p.append(arrow(W/2, 195, W/2, 320, color=INK, sw=1.5))
    p.append(text(W/2 + 110, 300, "IKM = 00...00 + Derive-Secret", size=10, color=MUTED))
    
    # Рівень 2: Master Secret
    b2, w2, h2 = textbox(W/2, 345, "Master Secret (Головний секрет)", size=13, fill="#fff6e6", stroke="#e08a1e", bold=True)
    p.append(b2)
    
    # Відгалуження ключів Application Data
    p.append(arrow(W/2 - 140, 370, W/2 - 220, 410, color=FIELD, sw=1.8))
    b_cats, _, _ = textbox(W/2 - 240, 435, "Client Application Traffic Key\n(Шифрування запитів HTTP)", size=11, fill="#eef7f0", stroke=FIELD, bold=True)
    p.append(b_cats)
    
    p.append(arrow(W/2 + 140, 370, W/2 + 220, 410, color=FIELD, sw=1.8))
    b_sats, _, _ = textbox(W/2 + 240, 435, "Server Application Traffic Key\n(Шифрування відповідей HTTP)", size=11, fill="#eef7f0", stroke=FIELD, bold=True)
    p.append(b_sats)

    render(os.path.join(OUT, "tls-key-schedule.svg"), W, H, *p,
           title="Ієрархічний розгорт ключів HKDF у TLS 1.3")

if __name__ == "__main__":
    fig_handshake_flow()
    fig_key_derivation()
    print("OK TLS Handshake figures generated")
