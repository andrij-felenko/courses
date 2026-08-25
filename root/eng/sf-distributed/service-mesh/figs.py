# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Архітектура сервісної сітки (Data Plane та Control Plane) ───────
def fig_mesh_data_control_planes():
    W, H = 1000, 560
    frags = []

    # Заголовок зверху
    frags.append(text(500, 30, "Архітектура сервісної сітки: Площина даних і Площина управління", size=16, bold=True))

    # Зона Control Plane (зверху)
    frags.append(rect(40, 55, 920, 150, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(65, 80, "CONTROL PLANE (Площина управління: Istiod / Linkerd-controller)", size=13, bold=True, color=NEG, anchor="start"))

    frags.append(box(210, 135, "API Server (K8s)\nCRD: VirtualService, DR", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=170))
    frags.append(box(500, 135, "Контролер (Pilot)\nГенерація xDS-конфігурацій", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=190))
    frags.append(box(790, 135, "Центр сертифікації (CA)\nВидача X.509 (SPIFFE SVID)", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=190))

    frags.append(arrow(300, 135, 395, 135, color=NEG, sw=1.5))
    frags.append(arrow(600, 135, 685, 135, color=FIELD, sw=1.5))

    # Зона Data Plane (знизу)
    frags.append(rect(40, 245, 920, 290, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(65, 270, "DATA PLANE (Площина даних)", size=13, bold=True, color=INK, anchor="start"))

    # Pod 1 (Order Service)
    frags.append(rect(70, 295, 390, 215, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(90, 320, "Pod: Order Service (Вузол 1)", size=12, bold=True, anchor="start"))
    
    frags.append(box(170, 395, "Застосунок\n(Go / Node.js)\nПорт: 8080", size=11, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=120))
    frags.append(box(360, 395, "Sidecar Proxy\n(Envoy)\nПорти: 15001 / 15006", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=140))
    frags.append(arrow(235, 395, 280, 395, color=LINE, sw=1.5))
    frags.append(text(258, 380, "lo", size=10, color=MUTED))

    # Pod 2 (Payment Service)
    frags.append(rect(540, 295, 390, 215, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(560, 320, "Pod: Payment Service (Вузол 2)", size=12, bold=True, anchor="start"))
    
    frags.append(box(640, 395, "Sidecar Proxy\n(Envoy)\nПорти: 15001 / 15006", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=140))
    frags.append(box(830, 395, "Застосунок\n(Java / Rust)\nПорт: 9090", size=11, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=120))
    frags.append(arrow(720, 395, 765, 395, color=LINE, sw=1.5))
    frags.append(text(742, 380, "lo", size=10, color=MUTED))

    # Зв'язок між Pod 1 та Pod 2 (mTLS тунель)
    frags.append(arrow(435, 395, 565, 395, color=FIELD, sw=2.5))
    frags.append(text(500, 375, "mTLS Тунель (Шифрування + SPIFFE)", size=10, bold=True, color=FIELD))
    frags.append(text(500, 420, "Повтори / Таймаути / Трейсинг", size=10, color=MUTED))

    # Зв'язок Control Plane -> Data Plane (xDS)
    frags.append(line(460, 205, 360, 295, color=NEG, sw=1.5, dash="4 4"))
    frags.append(line(540, 205, 640, 295, color=NEG, sw=1.5, dash="4 4"))
    frags.append(text(370, 235, "xDS (LDS/RDS/CDS/EDS)", size=10, color=NEG))
    frags.append(text(640, 235, "xDS (LDS/RDS/CDS/EDS)", size=10, color=NEG))

    # Зв'язок CA -> Proxies (Сертифікати через SDS)
    frags.append(line(760, 205, 410, 295, color=FIELD, sw=1.2, dash="3 3"))
    frags.append(line(810, 205, 690, 295, color=FIELD, sw=1.2, dash="3 3"))

    return render(os.path.join(IMG, 'mesh-data-control-planes.svg'), W, H, *frags)


# ── Фігура 2: Перехоплення трафіку всередині Network Namespace (iptables/eBPF) 
def fig_pod_traffic_interception():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Шлях мережевого пакета у Pod: перехоплення правилами iptables", size=16, bold=True))

    # Зовнішня межа Pod
    frags.append(rect(40, 55, 920, 440, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(70, 80, "Мережевий простір імен Pod (Network Namespace)", size=13, bold=True, anchor="start"))

    # Мережевий інтерфейс eth0
    frags.append(box(120, 260, "Мережевий\nінтерфейс\neth0", size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=100))

    # Блок iptables PREROUTING
    frags.append(box(300, 160, "iptables PREROUTING\n(PREROUTING chain)\nREDIRECT → 15006", size=11, bold=True, fill="#fdecea", stroke=POS, min_w=170))

    # Блок iptables OUTPUT
    frags.append(box(300, 360, "iptables OUTPUT\n(OUTPUT chain)\nREDIRECT → 15001", size=11, bold=True, fill="#fdecea", stroke=POS, min_w=170))

    # Envoy Sidecar Proxy
    frags.append(rect(440, 110, 240, 330, fill="#f4f6f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(560, 135, "Envoy Sidecar Proxy", size=13, bold=True, color=NEG))
    
    frags.append(box(560, 190, "Ingress Listener\n(Порт 15006)\nmTLS термінація, AuthZ", size=10, fill="#ffffff", stroke=MUTED, min_w=190))
    frags.append(box(560, 275, "Фільтри L7 (HTTP/gRPC)\nТрейсинг, Метрики, RBAC", size=10, fill="#ffffff", stroke=MUTED, min_w=190))
    frags.append(box(560, 370, "Egress Listener\n(Порт 15001)\nМаршрутизація, Ретраї, CB", size=10, fill="#ffffff", stroke=MUTED, min_w=190))

    # Контейнер застосунку
    frags.append(rect(740, 150, 190, 240, fill="#fff8e7", stroke="#d35400", sw=1.5, rx=6))
    frags.append(text(835, 180, "App Container", size=13, bold=True, color="#d35400"))
    frags.append(box(835, 260, "Бізнес-логіка\n(Слухає 127.0.0.1:8080)", size=11, fill="#ffffff", stroke=MUTED, min_w=160))
    frags.append(text(835, 340, "Не знає про мережу,\nmTLS чи сертифікати", size=10, color=MUTED, italic=True))

    # Стрілки вхідного трафіку (сині/зелені)
    frags.append(arrow(175, 230, 215, 175, color=FIELD, sw=2))
    frags.append(text(175, 185, "1. Вхідний TCP", size=10, bold=True, color=FIELD))

    frags.append(arrow(385, 160, 460, 180, color=FIELD, sw=2))
    frags.append(text(415, 150, "2. Порт 15006", size=10, color=FIELD))

    frags.append(arrow(660, 190, 750, 240, color=FIELD, sw=2))
    frags.append(text(710, 205, "3. Чистий HTTP (lo:8080)", size=10, color=FIELD))

    # Стрілки вихідного трафіку (червоні)
    frags.append(arrow(750, 280, 390, 360, color=POS, sw=2))
    frags.append(text(580, 455, "4. Вихідний виклик на віддалений IP", size=10, bold=True, color=POS))

    frags.append(arrow(385, 370, 460, 370, color=POS, sw=2))
    frags.append(text(415, 395, "5. Порт 15001", size=10, color=POS))

    frags.append(arrow(460, 400, 180, 280, color=POS, sw=2))
    frags.append(text(280, 315, "6. mTLS назовні (eth0)", size=10, bold=True, color=POS))

    return render(os.path.join(IMG, 'pod-traffic-interception.svg'), W, H, *frags)


# ── Фігура 3: Динамічний життєвий цикл xDS (LDS, RDS, CDS, EDS) ───────────────
def fig_xds_discovery_lifecycle():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 30, "Ієрархія та життєвий цикл конфігурації Envoy xDS v3", size=16, bold=True))

    # Колонка 1: Джерело правди
    frags.append(box(130, 130, "Kubernetes API\nService / Endpoints\nVirtualService / DR", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=160))
    frags.append(box(130, 280, "Control Plane (Pilot)\nАгрегатор стану\nОбчислення Delta xDS", size=11, bold=True, fill="#f4f6f8", stroke=LINE, min_w=160))
    frags.append(arrow(130, 180, 130, 235, color=NEG, sw=1.8))
    frags.append(text(130, 205, "Події Watch", size=10, color=MUTED))

    # Зв'язок gRPC ADS
    frags.append(arrow(215, 280, 310, 280, color=FIELD, sw=2.2))
    frags.append(text(265, 260, "gRPC ADS Stream", size=10, bold=True, color=FIELD))
    frags.append(text(265, 300, "Bidirectional", size=9, color=MUTED))

    # Колонка 2: Ієрархія xDS ресурсів усередині Envoy
    frags.append(rect(320, 65, 640, 380, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(340, 90, "Внутрішній стан конфігурації Envoy Proxy", size=13, bold=True, anchor="start"))

    # LDS
    frags.append(box(450, 160, "1. LDS (Listener Discovery)\nIP:Port та ланцюжки фільтрів\n(HTTP Connection Manager)", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=220))
    
    # RDS
    frags.append(box(770, 160, "2. RDS (Route Discovery)\nПравила маршрутизації\n(Prefix, Headers → Cluster)", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=220))

    # CDS
    frags.append(box(450, 340, "3. CDS (Cluster Discovery)\nГрупи бекендів, TLS налаштування,\nCircuit Breaker, Health Checks", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=220))

    # EDS
    frags.append(box(770, 340, "4. EDS (Endpoint Discovery)\nДинамічні IP:Port інстансів,\nВаги та Locality Zones", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=220))

    # Зв'язки між xDS рівнями
    frags.append(arrow(565, 160, 655, 160, color=LINE, sw=1.5))
    frags.append(text(610, 145, "посилається", size=9, color=MUTED))

    frags.append(arrow(770, 210, 565, 320, color=LINE, sw=1.5))
    frags.append(text(690, 255, "вказує на Cluster", size=9, color=MUTED))

    frags.append(arrow(565, 340, 655, 340, color=LINE, sw=1.5))
    frags.append(text(610, 325, "містить", size=9, color=MUTED))

    frags.append(text(500, 420, "Гарантія безпеки: Асинхронний reload без розриву активних TCP-з'єднань", size=11, bold=True, color=FIELD))

    return render(os.path.join(IMG, 'xds-discovery-lifecycle.svg'), W, H, *frags)


# ── Фігура 4: Порівняння Sidecar vs Ambient Mesh (Sidecarless) ────────────────
def fig_sidecar_vs_ambient_mesh():
    W, H = 1000, 490
    frags = []

    frags.append(text(500, 30, "Еволюція архітектури: Sidecar проти Sidecarless (Ambient Mesh)", size=16, bold=True))

    # Ліва половина: Класичний Sidecar Mesh
    frags.append(rect(40, 60, 440, 400, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(260, 90, "Класична модель Sidecar", size=14, bold=True, color=INK))

    frags.append(rect(65, 120, 390, 140, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(80, 140, "Pod A", size=11, bold=True, anchor="start"))
    frags.append(box(150, 190, "App A", size=11, bold=True, fill="#fff3e0", stroke="#d35400", min_w=90))
    frags.append(box(310, 190, "Envoy Sidecar\n(L4 + L7)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=130))
    frags.append(arrow(200, 190, 240, 190, color=LINE, sw=1.5))

    frags.append(rect(65, 280, 390, 140, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(80, 300, "Pod B", size=11, bold=True, anchor="start"))
    frags.append(box(150, 350, "App B", size=11, bold=True, fill="#fff3e0", stroke="#d35400", min_w=90))
    frags.append(box(310, 350, "Envoy Sidecar\n(L4 + L7)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=130))
    frags.append(arrow(200, 350, 240, 350, color=LINE, sw=1.5))

    frags.append(text(260, 440, "Високе споживання пам'яті: 50MB × N подів", size=10, color=POS, bold=True))

    # Права половина: Ambient Mesh (Sidecarless)
    frags.append(rect(520, 60, 440, 400, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(740, 90, "Ambient Mesh (Безсайдкарна)", size=14, bold=True, color=FIELD))

    # Node Level
    frags.append(rect(545, 120, 390, 190, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(560, 140, "Вузол Kubernetes (Node)", size=11, bold=True, anchor="start"))

    frags.append(box(625, 190, "Pod A\n(Тільки App)", size=11, bold=True, fill="#fff3e0", stroke="#d35400", min_w=100))
    frags.append(box(855, 190, "Pod B\n(Тільки App)", size=11, bold=True, fill="#fff3e0", stroke="#d35400", min_w=100))

    frags.append(box(740, 265, "ztunnel (Per-Node L4 DaemonSet)\nТільки mTLS + L4 Zero Trust (Rust, низька пам'ять)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=330))
    frags.append(arrow(625, 220, 680, 245, color=FIELD, sw=1.5))
    frags.append(arrow(855, 220, 800, 245, color=FIELD, sw=1.5))

    # L7 Waypoint
    frags.append(box(740, 365, "Waypoint Proxy (Per-Namespace L7)\nОкремий розгортаний Envoy для L7 політик\n(Тільки коли потрібні складні правила)", size=10, bold=True, fill="#eaf0fd", stroke=NEG, min_w=330))
    frags.append(arrow(740, 295, 740, 335, color=NEG, sw=1.5))

    frags.append(text(740, 440, "Економія пам'яті до 80%, простіший апгрейд", size=10, color=FIELD, bold=True))

    return render(os.path.join(IMG, 'sidecar-vs-ambient-mesh.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_mesh_data_control_planes()
    fig_pod_traffic_interception()
    fig_xds_discovery_lifecycle()
    fig_sidecar_vs_ambient_mesh()
    print("Всі 4 фігури успішно згенеровано.")
