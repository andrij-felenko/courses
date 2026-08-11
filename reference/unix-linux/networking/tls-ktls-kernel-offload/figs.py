import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_fig_arch():
    w, h = 700, 450
    out = ""
    # Userspace TLS
    out += textbox(200, 50, "Користувацький простір", min_w=200, pad=10)[0]
    out += textbox(200, 120, "OpenSSL / GnuTLS\n(Шифрування)", min_w=180, pad=10, fill="#fdecea")[0]
    
    # Kernel Space
    out += textbox(200, 240, "Ядро ОС (TCP/IP)", min_w=200, pad=10, fill="#eaf0fd")[0]
    
    # Hardware
    out += textbox(200, 360, "NIC (Мережева карта)", min_w=200, pad=10, fill="#eaf0fd")[0]

    out += arrow(200, 160, 200, 200)
    out += arrow(200, 280, 200, 320)
    
    # Kernel TLS (kTLS - TLS_SW)
    out += textbox(500, 50, "Користувацький простір", min_w=200, pad=10)[0]
    out += textbox(500, 120, "OpenSSL\n(Тільки Handshake)", min_w=180, pad=10, fill="#fdecea")[0]
    
    out += textbox(500, 240, "Ядро ОС (kTLS / TLS_SW)\n(Шифрування In-Kernel)", min_w=200, pad=10, fill="#eaf0fd")[0]
    
    out += textbox(500, 360, "NIC (Мережева карта)", min_w=200, pad=10, fill="#eaf0fd")[0]
    
    out += arrow(500, 160, 500, 200)
    out += arrow(500, 280, 500, 320)
    
    render(os.path.join(IMG, 'fig-tls-arch.svg'), w, h, out, title="Порівняння Userspace TLS та Kernel TLS")

def render_fig_hw():
    w, h = 600, 350
    out = ""
    out += textbox(300, 50, "Користувацький простір\n(Handshake & Керування)", min_w=250, pad=10)[0]
    out += textbox(300, 150, "Ядро ОС (kTLS / TLS_HW Control)", min_w=250, pad=10, fill="#eaf0fd")[0]
    out += textbox(300, 270, "SmartNIC\n(Апаратне шифрування Inline)", min_w=250, pad=10, fill="#fdecea", stroke="#c0392b")[0]
    out += arrow(300, 90, 300, 120)
    out += arrow(300, 190, 300, 220)
    render(os.path.join(IMG, 'fig-tls-hw.svg'), w, h, out, title="Апаратне прискорення TLS_HW")

if __name__ == '__main__':
    render_fig_arch()
    render_fig_hw()
