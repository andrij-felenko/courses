import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def generate_figures():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # 1. Архітектура прискорення сокетів BPF (SOCKMAP Redirection)
    w, h = 800, 480
    frags = []

    # Тло та блоки простору
    frags.append(rect(20, 50, 760, 160, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(mtext(40, 75, ["User-Space (Простір користувача)"], size=13, color=MUTED, bold=True, anchor="start"))

    frags.append(rect(20, 230, 760, 220, fill="#f1f5f9", stroke="#94a3b8", rx=8))
    frags.append(mtext(40, 255, ["Kernel-Space (Ядро Linux)"], size=13, color=MUTED, bold=True, anchor="start"))

    # Процес A (Proxy / Service A)
    b_a, _, _ = textbox(160, 130, "Process A (Envoy Proxy)\nFD: 5 (Socket 1)", size=13, pad=12, fill="#e0f2fe", stroke="#0288d1")
    frags.append(b_a)

    # Процес B (Backend Service)
    b_b, _, _ = textbox(640, 130, "Process B (Backend)\nFD: 8 (Socket 2)", size=13, pad=12, fill="#e0f2fe", stroke="#0288d1")
    frags.append(b_b)

    # Структури ядра сокетів
    b_sk1, _, _ = textbox(160, 300, "struct sock (Sock 1)\ntcp_bpf_sendmsg()", size=12, pad=10, fill="#ffffff", stroke="#0288d1")
    frags.append(b_sk1)

    b_sk2, _, _ = textbox(640, 300, "struct sock (Sock 2)\nsk_receive_queue", size=12, pad=10, fill="#ffffff", stroke="#0288d1")
    frags.append(b_sk2)

    # Стандартний стек (показаний пунктиром знизу)
    frags.append(rect(280, 380, 240, 50, fill="#fee2e2", stroke="#ef4444", rx=6))
    frags.append(mtext(400, 410, ["Традиційний TCP/IP Стек", "(IP, routing, loopback, TCP ACK)"], size=11, color="#b91c1c", anchor="middle"))

    # BPF SOCKMAP та програма verdict
    b_map, _, _ = textbox(400, 300, "BPF_MAP_TYPE_SOCKMAP\n[0]: Sock 1 -> [1]: Sock 2\nSK_SKB / SK_MSG Verdict Program", size=12, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_map)

    # Лінії зв'язку між User-Space та Kernel
    frags.append(arrow(160, 165, 160, 270, color="#0288d1", sw=1.5))
    frags.append(arrow(640, 270, 640, 165, color="#0288d1", sw=1.5))

    # Шлях байпасу BPF (Червона стрілка прямого перенаправлення без копіювання)
    frags.append(arrow(235, 300, 310, 300, color="#d97706", sw=2))
    frags.append(arrow(490, 300, 565, 300, color="#27ae60", sw=2.5))
    frags.append(mtext(400, 260, ["bpf_sk_redirect_map() / Zero-Copy Bypass"], size=12, color="#27ae60", bold=True))

    out_path = os.path.join(img_dir, "fig-sockmap-redir.svg")
    render(out_path, w, h, *frags, title="Прискорення сокетів за допомогою BPF SOCKMAP та sk_skb")
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_figures()
