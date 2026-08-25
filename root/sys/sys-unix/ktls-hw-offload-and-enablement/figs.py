import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_fig_arch():
    w, h = 760, 480
    out = ""
    
    # Left column: Userspace TLS
    out += textbox(190, 40, "Традиційний Userspace TLS", min_w=280, pad=10, fill="#f2f4f8")[0]
    out += textbox(190, 120, "Простір користувача\nOpenSSL / GnuTLS\n(Рукостискання + Шифрування)", min_w=260, pad=12, fill="#fdecea")[0]
    out += textbox(190, 260, "Ядро Linux (TCP/IP стек)\n(Буферизація та сегментація skb)", min_w=260, pad=12, fill="#eaf0fd")[0]
    out += textbox(190, 400, "Мережева карта (NIC)\n(Передача зашифрованих кадрів)", min_w=260, pad=12, fill="#eaf0fd")[0]

    out += arrow(190, 175, 190, 215)
    out += arrow(190, 315, 190, 355)

    # Right column: Kernel TLS (kTLS)
    out += textbox(570, 40, "Ядерне прискорення (kTLS)", min_w=280, pad=10, fill="#f2f4f8")[0]
    out += textbox(570, 120, "Простір користувача\nOpenSSL (Тільки Handshake)\nПередача ключів через setsockopt", min_w=260, pad=12, fill="#fdecea")[0]
    out += textbox(570, 260, "Ядро Linux (kTLS ULP / net/tls)\n(Шифрування records + Zero-Copy)", min_w=260, pad=12, fill="#d4efdf")[0]
    out += textbox(570, 400, "Мережева карта (NIC)\n(Передача зашифрованого трафіку)", min_w=260, pad=12, fill="#eaf0fd")[0]

    out += arrow(570, 175, 570, 215)
    out += arrow(570, 315, 570, 355)

    render(os.path.join(IMG, 'fig-tls-arch.svg'), w, h, out, title="Порівняння Userspace TLS та Kernel TLS")

def render_fig_hw():
    w, h = 650, 440
    out = ""
    out += textbox(325, 40, "Простір користувача\n(Control Plane: Handshake & X.509)", min_w=340, pad=12, fill="#fdecea")[0]
    out += textbox(325, 170, "Ядро Linux (kTLS Control / net/tls)\n(Передача криптоконтексту у драйвер NIC)", min_w=340, pad=12, fill="#eaf0fd")[0]
    out += textbox(325, 330, "SmartNIC (TLS_HW / Inline Accelerator)\n(Апаратне AES-GCM шифрування під час DMA)", min_w=340, pad=14, fill="#d4efdf", stroke="#27ae60")[0]

    out += arrow(325, 100, 325, 125)
    out += arrow(325, 230, 325, 275)

    render(os.path.join(IMG, 'fig-tls-hw.svg'), w, h, out, title="Апаратне прискорення TLS_HW")

def render_fig_pipeline():
    w, h = 720, 360
    out = ""
    out += textbox(120, 80, "Page Cache\n(Plaintext Data)", min_w=150, pad=12, fill="#fff2cc")[0]
    out += textbox(360, 80, "kTLS SW (Crypto API)\n(AES-GCM Encrypt)", min_w=180, pad=12, fill="#e1f5fe")[0]
    out += textbox(600, 80, "TCP / IP Stack\n(TCP Framing)", min_w=140, pad=12, fill="#eaf0fd")[0]

    out += arrow(195, 80, 270, 80)
    out += arrow(450, 80, 530, 80)

    out += textbox(120, 240, "Page Cache\n(Plaintext Data)", min_w=150, pad=12, fill="#fff2cc")[0]
    out += textbox(360, 240, "kTLS HW (Zero-CPU)\n(Plaintext skb + Tag)", min_w=180, pad=12, fill="#e8f5e9")[0]
    out += textbox(600, 240, "SmartNIC DMA\n(Inline Encryption)", min_w=140, pad=12, fill="#d4efdf", stroke="#27ae60")[0]

    out += arrow(195, 240, 270, 240)
    out += arrow(450, 240, 530, 240)

    render(os.path.join(IMG, 'fig-ktls-pipeline.svg'), w, h, out, title="Порівняння конвеєрів TLS_SW та TLS_HW під час sendfile()")

if __name__ == '__main__':
    render_fig_arch()
    render_fig_hw()
    render_fig_pipeline()
