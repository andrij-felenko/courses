import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def generate_figures():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # -------------------------------------------------------------------------
    # 1. Trajectory of packets and cgroup hooks (fig-cgroup-skb-flow.svg)
    # -------------------------------------------------------------------------
    w, h = 840, 460
    frags = []

    # Regions
    frags.append(rect(20, 50, 800, 140, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(mtext(40, 75, ["User-Space (cgroup v2 container)"], size=13, color=MUTED, bold=True, anchor="start"))

    frags.append(rect(20, 210, 800, 230, fill="#f1f5f9", stroke="#94a3b8", rx=8))
    frags.append(mtext(40, 235, ["Kernel-Space (Мережевий стек Linux)"], size=13, color=MUTED, bold=True, anchor="start"))

    # App Process Box
    b_app, _, _ = textbox(150, 120, "Процес у cgroup\nsocket(), sendmsg(), recv()", size=13, pad=12, fill="#e0f2fe", stroke="#0288d1")
    frags.append(b_app)

    # SOCK_CREATE Hook
    b_sock, _, _ = textbox(420, 120, "BPF_CGROUP_INET_SOCK_CREATE\nПеревірка при socket()", size=12, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_sock)

    # Socket Layer
    b_sk, _, _ = textbox(150, 270, "Сокет ядра (struct sock)\nЧерги tx_queue / rx_queue", size=12, pad=10, fill="#ffffff", stroke="#0288d1")
    frags.append(b_sk)

    # EGRESS Hook
    b_egress, _, _ = textbox(380, 270, "BPF_CGROUP_INET_EGRESS\n(sk_buff context, early drop)", size=12, pad=10, fill="#fee2e2", stroke="#ef4444", bold=True)
    frags.append(b_egress)

    # INGRESS Hook
    b_ingress, _, _ = textbox(650, 270, "BPF_CGROUP_INET_INGRESS\n(sock lookup done, filter skb)", size=12, pad=10, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b_ingress)

    # Network Stack / Routing / NIC
    b_net, _, _ = textbox(515, 380, "IP Routing, Netfilter, TC, NIC Driver", size=12, pad=10, fill="#e2e8f0", stroke="#475569")
    frags.append(b_net)

    # Arrows
    # socket creation check
    frags.append(arrow(260, 120, 310, 120, color="#d97706", sw=1.8))
    # app <-> socket
    frags.append(arrow(150, 160, 150, 230, color="#0288d1", sw=1.8))

    # Egress path: Socket -> EGRESS hook -> Routing/NIC
    frags.append(arrow(240, 270, 290, 270, color="#ef4444", sw=2.0))
    frags.append(arrow(470, 270, 515, 335, color="#ef4444", sw=2.0))

    # Ingress path: Routing/NIC -> INGRESS hook -> Socket
    frags.append(arrow(540, 335, 650, 320, color="#16a34a", sw=2.0))
    frags.append(arrow(650, 220, 240, 260, color="#16a34a", sw=2.0))

    # Text labels on paths
    frags.append(mtext(360, 250, ["Вихідний пакет (EGRESS)"], size=11, color="#b91c1c", bold=True))
    frags.append(mtext(650, 350, ["Вхідний пакет (INGRESS)"], size=11, color="#15803d", bold=True))

    out_path1 = os.path.join(img_dir, "fig-cgroup-skb-flow.svg")
    render(out_path1, w, h, *frags, title="Траєкторія мережевих пакетів та eBPF cgroup хуки")
    print(f"Generated: {out_path1}")

    # -------------------------------------------------------------------------
    # 2. Hierarchy and Multi-Prog Evaluation (fig-cgroup-bpf-hierarchy.svg)
    # -------------------------------------------------------------------------
    w2, h2 = 840, 440
    frags2 = []

    # Title & background
    frags2.append(rect(20, 40, 800, 380, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags2.append(mtext(40, 65, ["Дерево cgroup v2 та обчислення програм із прапорцем BPF_F_ALLOW_MULTI"], size=13, color=MUTED, bold=True, anchor="start"))

    # Root Node
    b_root, _, _ = textbox(420, 110, "Корінь (/sys/fs/cgroup)\nProg 1 (Global Policy)", size=12, pad=10, fill="#e2e8f0", stroke="#475569", bold=True)
    frags2.append(b_root)

    # Level 1: kubepods
    b_kube, _, _ = textbox(260, 210, "cgroup: kubepods/\nProg 2 (Cluster Policy)", size=12, pad=10, fill="#dbeafe", stroke="#2563eb", bold=True)
    frags2.append(b_kube)

    # Level 2: pod-1
    b_pod, _, _ = textbox(260, 310, "cgroup: pod-123/\nProg 3 (Pod Policy)", size=12, pad=10, fill="#fee2e2", stroke="#ef4444", bold=True)
    frags2.append(b_pod)

    # Process inside pod-1
    b_proc, _, _ = textbox(600, 310, "Процес у контейнері\nГенерація/отримання SKB", size=12, pad=10, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags2.append(b_proc)

    # Evaluation logic panel
    frags2.append(rect(510, 100, 290, 150, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags2.append(mtext(655, 125, ["Логіка виконання (AND):"], size=12, color=INK, bold=True))
    frags2.append(mtext(525, 150, [
        "1. Запуск Prog 3 (Pod)",
        "2. Запуск Prog 2 (Cluster)",
        "3. Запуск Prog 1 (Root)",
        "• Якщо УСІ повертають 1 -> OK",
        "• Якщо ХОЧ Б ОДИН 0 -> DROP"
    ], size=11, color=INK, anchor="start"))

    # Lines connecting tree
    frags2.append(arrow(380, 140, 300, 180, color="#475569", sw=1.8))
    frags2.append(arrow(260, 240, 260, 280, color="#2563eb", sw=1.8))
    frags2.append(arrow(510, 310, 350, 310, color="#16a34a", sw=2.0))

    out_path2 = os.path.join(img_dir, "fig-cgroup-bpf-hierarchy.svg")
    render(out_path2, w2, h2, *frags2, title="Обчислення ієрархії cgroup v2 BPF-програм")
    print(f"Generated: {out_path2}")

if __name__ == "__main__":
    generate_figures()
