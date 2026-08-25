# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Архітектура керуючої площини та робочих вузлів ───────────────────
def fig_control_plane_architecture():
    W, H = 1040, 580
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Ліва частина: Керуюча площина (Control Plane)
    cp_x, cp_y, cp_w, cp_h = 30, 30, 460, 520
    p.append(rect(cp_x, cp_y, cp_w, cp_h, fill="#f8fafc", stroke="#3b82f6", sw=1.8, rx=8))
    p.append(text(cp_x + cp_w / 2, cp_y + 28, "Керуюча площина (Control Plane)", size=15, color="#1e40af", bold=True))
    p.append(text(cp_x + cp_w / 2, cp_y + 48, "Централізований консенсус та узгодження стану", size=11, color="#64748b"))
    
    # API Server
    api_x, api_y, api_w, api_h = cp_x + 25, cp_y + 68, 410, 75
    p.append(rect(api_x, api_y, api_w, api_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(api_x + api_w / 2, api_y + 24, "API Server (kube-apiserver)", size=13.5, color="#1d4ed8", bold=True))
    p.append(text(api_x + api_w / 2, api_y + 44, "Автентифікація, валідація схем, Admission Webhooks", size=10.5, color="#334155"))
    p.append(text(api_x + api_w / 2, api_y + 60, "Єдина точка входу, stateless REST/gRPC шлюз", size=10, color="#64748b"))
    
    # etcd
    etcd_x, etcd_y, etcd_w, etcd_h = cp_x + 25, cp_y + 175, 410, 75
    p.append(rect(etcd_x, etcd_y, etcd_w, etcd_h, fill="#fef2f2", stroke="#dc2626", sw=1.6, rx=6))
    p.append(text(etcd_x + etcd_w / 2, etcd_y + 24, "etcd (Raft Storage)", size=13.5, color="#b91c1c", bold=True))
    p.append(text(etcd_x + etcd_w / 2, etcd_y + 44, "Розподілений транзакційний журнал (MVCC key-value)", size=10.5, color="#334155"))
    p.append(text(etcd_x + etcd_w / 2, etcd_y + 60, "Єдине джерело правди; Watch API для змін revision", size=10, color="#7f1d1d"))
    
    # Двосторонній зв'язок API Server <-> etcd
    p.append(arrow(cp_x + cp_w / 2, api_y + api_h + 2, cp_x + cp_w / 2, etcd_y - 2, color="#dc2626", sw=2.0))
    p.append(arrow(cp_x + cp_w / 2 - 25, etcd_y - 2, cp_x + cp_w / 2 - 25, api_y + api_h + 2, color="#2563eb", sw=1.5))
    
    # Controller Manager
    cm_x, cm_y, cm_w, cm_h = cp_x + 25, cp_y + 280, 195, 85
    p.append(rect(cm_x, cm_y, cm_w, cm_h, fill="#ecfdf5", stroke="#059669", sw=1.4, rx=6))
    p.append(text(cm_x + cm_w / 2, cm_y + 22, "Controller Manager", size=12, color="#047857", bold=True))
    p.append(text(cm_x + cm_w / 2, cm_y + 42, "DeploymentController", size=10, color="#334155"))
    p.append(text(cm_x + cm_w / 2, cm_y + 58, "ReplicaSetController", size=10, color="#334155"))
    p.append(text(cm_x + cm_w / 2, cm_y + 74, "NodeLifeCycleController", size=10, color="#334155"))
    
    # Scheduler
    sc_x, sc_y, sc_w, sc_h = cp_x + 240, cp_y + 280, 195, 85
    p.append(rect(sc_x, sc_y, sc_w, sc_h, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(sc_x + sc_w / 2, sc_y + 22, "Scheduler", size=12, color="#b45309", bold=True))
    p.append(text(sc_x + sc_w / 2, sc_y + 42, "1. Фільтрація (Predicates)", size=10, color="#334155"))
    p.append(text(sc_x + sc_w / 2, sc_y + 58, "2. Пріоритети (Scoring)", size=10, color="#334155"))
    p.append(text(sc_x + sc_w / 2, sc_y + 74, "3. Binding (Призначення)", size=10, color="#334155"))
    
    # Зв'язки контролерів та шедулера з API Server
    p.append(arrow(cm_x + cm_w / 2, cm_y - 2, api_x + 70, api_y + api_h + 2, color="#059669", sw=1.4))
    p.append(arrow(sc_x + sc_w / 2, sc_y - 2, api_x + api_w - 70, api_y + api_h + 2, color="#d97706", sw=1.4))
    
    # Зовнішній користувач / CLI
    usr_x, usr_y, usr_w, usr_h = cp_x + 25, cp_y + 395, 410, 95
    p.append(rect(usr_x, usr_y, usr_w, usr_h, fill="#f5f3ff", stroke="#7c3aed", sw=1.4, rx=6))
    p.append(text(usr_x + usr_w / 2, usr_y + 22, "Клієнт / Декларативний маніфест (kubectl apply)", size=12, color="#6d28d9", bold=True))
    p.append(text(usr_x + usr_w / 2, usr_y + 44, "Маніфест: опис бажаного стану (Desired State)", size=10.5, color="#334155"))
    p.append(text(usr_x + usr_w / 2, usr_y + 62, "spec: replicas: 5, template: { image: 'app:v2' }", size=10, color="#475569"))
    p.append(text(usr_x + usr_w / 2, usr_y + 80, "Асинхронна відправка через REST без блокування", size=10, color="#6b7280"))
    p.append(arrow(usr_x + usr_w / 2, usr_y - 2, api_x + api_w / 2, api_y + api_h + 2, color="#7c3aed", sw=1.6))
    
    # Права частина: Робочі вузли (Worker Nodes)
    nodes_x, nodes_y, nodes_w, nodes_h = 520, 30, 490, 520
    p.append(rect(nodes_x, nodes_y, nodes_w, nodes_h, fill="#f8fafc", stroke="#0284c7", sw=1.8, rx=8))
    p.append(text(nodes_x + nodes_w / 2, nodes_y + 28, "Робочі вузли кластера (Worker Nodes)", size=15, color="#0369a1", bold=True))
    p.append(text(nodes_x + nodes_w / 2, nodes_y + 48, "Локальне виконання контейнерів та маршрутизація трафіку", size=11, color="#64748b"))
    
    # Вузол 1 (Node 1)
    n1_x, n1_y, n1_w, n1_h = nodes_x + 20, nodes_y + 65, 450, 210
    p.append(rect(n1_x, n1_y, n1_w, n1_h, fill="#ffffff", stroke="#0284c7", sw=1.4, rx=6))
    p.append(text(n1_x + 15, n1_y + 22, "Вузол 1 (Worker Node A)", size=13, color="#0c4a6e", bold=True, anchor="start"))
    
    # Компоненти Node 1: Kubelet
    k1_x, k1_y, k1_w, k1_h = n1_x + 15, n1_y + 35, 200, 75
    p.append(rect(k1_x, k1_y, k1_w, k1_h, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(k1_x + k1_w / 2, k1_y + 20, "Kubelet (Node Agent)", size=11.5, color="#0369a1", bold=True))
    p.append(text(k1_x + k1_w / 2, k1_y + 38, "Синхронізація подів (PLEG)", size=10, color="#334155"))
    p.append(text(k1_x + k1_w / 2, k1_y + 54, "CRI gRPC / cgroup v2", size=9.5, color="#64748b"))
    p.append(text(k1_x + k1_w / 2, k1_y + 68, "Звіт стану в API Server", size=9.5, color="#0369a1"))
    
    # kube-proxy / eBPF
    kp1_x, kp1_y, kp1_w, kp1_h = n1_x + 230, n1_y + 35, 205, 75
    p.append(rect(kp1_x, kp1_y, kp1_w, kp1_h, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(kp1_x + kp1_w / 2, kp1_y + 20, "kube-proxy / eBPF", size=11.5, color="#b45309", bold=True))
    p.append(text(kp1_x + kp1_w / 2, kp1_y + 38, "Трансляція ClusterIP VIP", size=10, color="#334155"))
    p.append(text(kp1_x + kp1_w / 2, kp1_y + 54, "iptables / IPVS / sock_ops", size=9.5, color="#64748b"))
    p.append(text(kp1_x + kp1_w / 2, kp1_y + 68, "Балансування бекендів", size=9.5, color="#b45309"))
    
    # Поди на Node 1
    pod1_x, pod1_y, pod1_w, pod1_h = n1_x + 15, n1_y + 120, 200, 78
    p.append(rect(pod1_x, pod1_y, pod1_w, pod1_h, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    p.append(text(pod1_x + pod1_w / 2, pod1_y + 20, "Pod: app-v2-7f9a", size=10.5, color="#047857", bold=True))
    p.append(text(pod1_x + pod1_w / 2, pod1_y + 38, "IP: 10.244.1.5 (NetNS)", size=9.5, color="#334155"))
    p.append(text(pod1_x + pod1_w / 2, pod1_y + 54, "containerd: nginx + app", size=9.5, color="#334155"))
    p.append(text(pod1_x + pod1_w / 2, pod1_y + 69, "cpu=500m, mem=256Mi", size=9.5, color="#64748b"))
    
    pod2_x, pod2_y, pod2_w, pod2_h = n1_x + 230, n1_y + 120, 205, 78
    p.append(rect(pod2_x, pod2_y, pod2_w, pod2_h, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    p.append(text(pod2_x + pod2_w / 2, pod2_y + 20, "Pod: worker-3k8c", size=10.5, color="#047857", bold=True))
    p.append(text(pod2_x + pod2_w / 2, pod2_y + 38, "IP: 10.244.1.6 (NetNS)", size=9.5, color="#334155"))
    p.append(text(pod2_x + pod2_w / 2, pod2_y + 54, "CSI PersistentVolume", size=9.5, color="#334155"))
    p.append(text(pod2_x + pod2_w / 2, pod2_y + 69, "cpu=1000m, mem=1Gi", size=9.5, color="#64748b"))
    
    # Вузол 2 (Node 2)
    n2_x, n2_y, n2_w, n2_h = nodes_x + 20, nodes_y + 290, 450, 210
    p.append(rect(n2_x, n2_y, n2_w, n2_h, fill="#ffffff", stroke="#0284c7", sw=1.4, rx=6))
    p.append(text(n2_x + 15, n2_y + 22, "Вузол 2 (Worker Node B)", size=13, color="#0c4a6e", bold=True, anchor="start"))
    
    # Kubelet & Proxy на Node 2
    k2_x, k2_y, k2_w, k2_h = n2_x + 15, n2_y + 35, 200, 75
    p.append(rect(k2_x, k2_y, k2_w, k2_h, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(k2_x + k2_w / 2, k2_y + 20, "Kubelet (Node Agent)", size=11.5, color="#0369a1", bold=True))
    p.append(text(k2_x + k2_w / 2, k2_y + 38, "Синхронізація подів (PLEG)", size=10, color="#334155"))
    p.append(text(k2_x + k2_w / 2, k2_y + 54, "CRI gRPC / cgroup v2", size=9.5, color="#64748b"))
    p.append(text(k2_x + k2_w / 2, k2_y + 68, "Звіт стану в API Server", size=9.5, color="#0369a1"))
    
    kp2_x, kp2_y, kp2_w, kp2_h = n2_x + 230, n2_y + 35, 205, 75
    p.append(rect(kp2_x, kp2_y, kp2_w, kp2_h, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(kp2_x + kp2_w / 2, kp2_y + 20, "kube-proxy / eBPF", size=11.5, color="#b45309", bold=True))
    p.append(text(kp2_x + kp2_w / 2, kp2_y + 38, "Трансляція ClusterIP VIP", size=10, color="#334155"))
    p.append(text(kp2_x + kp2_w / 2, kp2_y + 54, "iptables / IPVS / sock_ops", size=9.5, color="#64748b"))
    p.append(text(kp2_x + kp2_w / 2, kp2_y + 68, "Балансування бекендів", size=9.5, color="#b45309"))
    
    # Поди на Node 2
    pod3_x, pod3_y, pod3_w, pod3_h = n2_x + 15, n2_y + 120, 200, 78
    p.append(rect(pod3_x, pod3_y, pod3_w, pod3_h, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    p.append(text(pod3_x + pod3_w / 2, pod3_y + 20, "Pod: app-v2-4m1p", size=10.5, color="#047857", bold=True))
    p.append(text(pod3_x + pod3_w / 2, pod3_y + 38, "IP: 10.244.2.8 (NetNS)", size=9.5, color="#334155"))
    p.append(text(pod3_x + pod3_w / 2, pod3_y + 54, "containerd: nginx + app", size=9.5, color="#334155"))
    p.append(text(pod3_x + pod3_w / 2, pod3_y + 69, "cpu=500m, mem=256Mi", size=9.5, color="#64748b"))
    
    pod4_x, pod4_y, pod4_w, pod4_h = n2_x + 230, n2_y + 120, 205, 78
    p.append(rect(pod4_x, pod4_y, pod4_w, pod4_h, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    p.append(text(pod4_x + pod4_w / 2, pod4_y + 20, "Pod: app-v2-9x2q", size=10.5, color="#047857", bold=True))
    p.append(text(pod4_x + pod4_w / 2, pod4_y + 38, "IP: 10.244.2.9 (NetNS)", size=9.5, color="#334155"))
    p.append(text(pod4_x + pod4_w / 2, pod4_y + 54, "containerd: nginx + app", size=9.5, color="#334155"))
    p.append(text(pod4_x + pod4_w / 2, pod4_y + 69, "cpu=500m, mem=256Mi", size=9.5, color="#64748b"))
    
    # Головні потоки зв'язку між CP та Nodes
    p.append(arrow(api_x + api_w, api_y + 30, k1_x, k1_y + 35, color="#2563eb", sw=1.8))
    p.append(arrow(k1_x, k1_y + 50, api_x + api_w, api_y + 45, color="#0284c7", sw=1.4))
    
    p.append(arrow(api_x + api_w, api_y + 55, k2_x, k2_y + 35, color="#2563eb", sw=1.8))
    p.append(arrow(k2_x, k2_y + 50, api_x + api_w, api_y + 65, color="#0284c7", sw=1.4))
    
    render(os.path.join(OUT, "control-plane-architecture.svg"), W, H, *p)


# ── Фіг. 2: Цикл узгодження стану (Reconciliation Loop) ───────────────────────
def fig_reconciliation_loop():
    W, H = 960, 500
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 40, "Цикл узгодження стану (Reconciliation Loop)", size=16, color="#1e3a8a", bold=True))
    p.append(text(W / 2, 62, "Безперервний порівняльний автомат: Бажаний стан (Spec) проти Реального стану (Status)", size=11, color="#64748b"))
    
    cx, cy = W / 2, 275
    
    # Вузол 1: Observe
    n1_x, n1_y, n1_w, n1_h = cx - 145, 95, 290, 75
    p.append(rect(n1_x, n1_y, n1_w, n1_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(cx, n1_y + 24, "1. Спостереження (Observe)", size=13.5, color="#1d4ed8", bold=True))
    p.append(text(cx, n1_y + 44, "Watch HTTP/gRPC потік з API Server", size=10.5, color="#334155"))
    p.append(text(cx, n1_y + 62, "Локальний Informer Cache (Reflector/Lister)", size=10, color="#64748b"))
    
    # Вузол 2: Analyze & Diff
    n2_x, n2_y, n2_w, n2_h = cx + 185, cy - 40, 270, 80
    p.append(rect(n2_x, n2_y, n2_w, n2_h, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(n2_x + n2_w / 2, n2_y + 24, "2. Аналіз різниці (Diff)", size=13.5, color="#b45309", bold=True))
    p.append(text(n2_x + n2_w / 2, n2_y + 44, "Δ = Desired.Spec - Actual.Status", size=10.5, color="#0f172a", bold=True))
    p.append(text(n2_x + n2_w / 2, n2_y + 60, "Виявлено дефіцит або зміну образу", size=10, color="#475569"))
    
    # Вузол 3: Act / Mutate
    n3_x, n3_y, n3_w, n3_h = cx - 145, cy + 120, 290, 80
    p.append(rect(n3_x, n3_y, n3_w, n3_h, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(cx, n3_y + 24, "3. Виправлення (Act / Mutate)", size=13.5, color="#047857", bold=True))
    p.append(text(cx, n3_y + 44, "Асинхронний виклик API: POST / PATCH / DELETE", size=10.5, color="#334155"))
    p.append(text(cx, n3_y + 62, "Ідемпотентне створення/видалення подів", size=10, color="#047857"))
    
    # Вузол 4: Update Status
    n4_x, n4_y, n4_w, n4_h = cx - 455, cy - 40, 270, 80
    p.append(rect(n4_x, n4_y, n4_w, n4_h, fill="#f5f3ff", stroke="#7c3aed", sw=1.6, rx=6))
    p.append(text(n4_x + n4_w / 2, n4_y + 24, "4. Фіксація статусу (Status)", size=13.5, color="#6d28d9", bold=True))
    p.append(text(n4_x + n4_w / 2, n4_y + 44, "Оптимістичне блокування (resourceVersion)", size=10, color="#334155"))
    p.append(text(n4_x + n4_w / 2, n4_y + 62, "Черга з експоненційним backoff при збоях", size=10, color="#dc2626"))
    
    # Стрілки циклу по колу
    p.append(arrow(cx + 147, n1_y + 37, n2_x + 135, n2_y - 2, color="#2563eb", sw=2.0))
    p.append(arrow(n2_x + 135, n2_y + n2_h + 2, cx + 147, n3_y + 37, color="#d97706", sw=2.0))
    p.append(arrow(cx - 147, n3_y + 37, n4_x + 135, n4_y + n4_h + 2, color="#059669", sw=2.0))
    p.append(arrow(n4_x + 135, n4_y - 2, cx - 147, n1_y + 37, color="#7c3aed", sw=2.0))
    
    # Центральний блок (Властивості моделі)
    center_w, center_h = 250, 105
    p.append(rect(cx - center_w / 2, cy - center_h / 2, center_w, center_h, fill="#fafafa", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(cx, cy - 28, "Фундаментальні гарантії", size=11.5, color="#1e293b", bold=True))
    p.append(text(cx, cy - 9, "• Level-triggered (чутливий до стану)", size=10, color="#334155"))
    p.append(text(cx, cy + 9, "• Self-healing (самовідновлення)", size=10, color="#334155"))
    p.append(text(cx, cy + 27, "• Сходження до ідеалу при збоях", size=10, color="#059669", bold=True))
    
    render(os.path.join(OUT, "reconciliation-loop.svg"), W, H, *p)


# ── Фіг. 3: Конвеєр планування (Two-Phase Scheduling Pipeline) ────────────────
def fig_scheduling_pipeline():
    W, H = 980, 500
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Двофазний конвеєр планування (Two-Phase Scheduler)", size=16, color="#1e3a8a", bold=True))
    p.append(text(W / 2, 60, "Трансформація черги непризначених подів у точне прив'язування до вузлів", size=11, color="#64748b"))
    
    col_w = 210
    col_h = 380
    gap = 25
    start_x = 30
    y_top = 85
    
    # Колонка 1: Черга подів
    c1_x = start_x
    p.append(rect(c1_x, y_top, col_w, col_h, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))
    p.append(text(c1_x + col_w / 2, y_top + 24, "1. Черга планування", size=13, color="#334155", bold=True))
    p.append(text(c1_x + col_w / 2, y_top + 42, "ActiveQ / UnschedulableQ", size=10, color="#64748b"))
    
    p.append(rect(c1_x + 12, y_top + 65, col_w - 24, 80, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(c1_x + col_w / 2, y_top + 84, "Pod: web-backend", size=11, color="#1d4ed8", bold=True))
    p.append(text(c1_x + col_w / 2, y_top + 102, "spec.nodeName == ''", size=9.5, color="#dc2626"))
    p.append(text(c1_x + col_w / 2, y_top + 118, "req: CPU=2, RAM=4Gi", size=9.5, color="#334155"))
    p.append(text(c1_x + col_w / 2, y_top + 134, "affinity: zone=eu-west-1a", size=9.5, color="#475569"))
    
    p.append(rect(c1_x + 12, y_top + 155, col_w - 24, 70, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(c1_x + col_w / 2, y_top + 175, "Pod: worker-task", size=10.5, color="#475569", bold=True))
    p.append(text(c1_x + col_w / 2, y_top + 193, "req: CPU=0.5, RAM=1Gi", size=9.5, color="#64748b"))
    p.append(text(c1_x + col_w / 2, y_top + 209, "tolerations: [gpu=true]", size=9.5, color="#64748b"))
    
    p.append(rect(c1_x + 12, y_top + 235, col_w - 24, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(c1_x + col_w / 2, y_top + 256, "Pod: cron-job-report", size=10, color="#64748b"))
    p.append(text(c1_x + col_w / 2, y_top + 274, "req: CPU=1, RAM=2Gi", size=9.5, color="#94a3b8"))
    
    p.append(text(c1_x + col_w / 2, y_top + 320, "Пріоритет за чергою", size=10, color="#1e293b", bold=True))
    p.append(text(c1_x + col_w / 2, y_top + 340, "FIFO з витісненням", size=9.5, color="#64748b"))
    p.append(text(c1_x + col_w / 2, y_top + 356, "та BackoffQueue", size=9.5, color="#64748b"))
    
    # Колонка 2: Фаза 1 - Фільтрація
    c2_x = c1_x + col_w + gap
    p.append(rect(c2_x, y_top, col_w, col_h, fill="#eff6ff", stroke="#2563eb", sw=1.4, rx=6))
    p.append(text(c2_x + col_w / 2, y_top + 24, "2. Фільтрація (Predicates)", size=13, color="#1d4ed8", bold=True))
    p.append(text(c2_x + col_w / 2, y_top + 42, "Відсікання непридатних вузлів", size=10, color="#64748b"))
    
    predicates = [
        ("Вузол 1 (8 CPU, 16G)", "OK: ресурсів вистачає", "#ecfdf5", "#059669"),
        ("Вузол 2 (1 CPU, 2G)", "FAIL: брак пам'яті", "#fef2f2", "#dc2626"),
        ("Вузол 3 (16 CPU, 32G)", "OK: ресурсів вистачає", "#ecfdf5", "#059669"),
        ("Вузол 4 (Tainted: GPU)", "FAIL: немає toleration", "#fef2f2", "#dc2626")
    ]
    for idx, (node_name, status_str, bg, strk) in enumerate(predicates):
        py = y_top + 65 + idx * 58
        p.append(rect(c2_x + 10, py, col_w - 20, 50, fill=bg, stroke=strk, sw=1.1, rx=4))
        p.append(text(c2_x + col_w / 2, py + 20, node_name, size=10, color="#0f172a", bold=True))
        p.append(text(c2_x + col_w / 2, py + 37, status_str, size=9.5, color=strk))
        
    p.append(text(c2_x + col_w / 2, y_top + 320, "Вхід: N = 1000 вузлів", size=10, color="#1e40af", bold=True))
    p.append(text(c2_x + col_w / 2, y_top + 340, "Вихід: M = 2 придатних", size=10, color="#059669", bold=True))
    p.append(text(c2_x + col_w / 2, y_top + 358, "Паралельне відсікання", size=9.5, color="#64748b"))
    
    # Колонка 3: Фаза 2 - Оцінювання
    c3_x = c2_x + col_w + gap
    p.append(rect(c3_x, y_top, col_w, col_h, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(c3_x + col_w / 2, y_top + 24, "3. Оцінювання (Scoring)", size=13, color="#b45309", bold=True))
    p.append(text(c3_x + col_w / 2, y_top + 42, "Ранжування кандидатів 0..100", size=10, color="#64748b"))
    
    # Вузол 1 Scoring
    p.append(rect(c3_x + 10, y_top + 65, col_w - 20, 100, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(c3_x + col_w / 2, y_top + 84, "Вузол 1 (Рахунок: 84)", size=11.5, color="#b45309", bold=True))
    p.append(text(c3_x + col_w / 2, y_top + 102, "• ImageLocality: 100 (кеш)", size=9.5, color="#059669"))
    p.append(text(c3_x + col_w / 2, y_top + 118, "• LeastAllocated: 70", size=9.5, color="#334155"))
    p.append(text(c3_x + col_w / 2, y_top + 134, "• TopologySpread: 90", size=9.5, color="#334155"))
    p.append(text(c3_x + col_w / 2, y_top + 152, "Weighted Sum = 84.0", size=10, color="#b45309", bold=True))
    
    # Вузол 3 Scoring
    p.append(rect(c3_x + 10, y_top + 175, col_w - 20, 100, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(c3_x + col_w / 2, y_top + 194, "Вузол 3 (Рахунок: 62)", size=11.5, color="#475569", bold=True))
    p.append(text(c3_x + col_w / 2, y_top + 212, "• ImageLocality: 0 (немає)", size=9.5, color="#dc2626"))
    p.append(text(c3_x + col_w / 2, y_top + 228, "• LeastAllocated: 95", size=9.5, color="#334155"))
    p.append(text(c3_x + col_w / 2, y_top + 244, "• TopologySpread: 60", size=9.5, color="#334155"))
    p.append(text(c3_x + col_w / 2, y_top + 262, "Weighted Sum = 62.0", size=10, color="#475569", bold=True))
    
    p.append(text(c3_x + col_w / 2, y_top + 320, "Вибір максимуму:", size=10, color="#1e293b", bold=True))
    p.append(text(c3_x + col_w / 2, y_top + 340, "max(Score) → Вузол 1", size=11.5, color="#059669", bold=True))
    p.append(text(c3_x + col_w / 2, y_top + 358, "Нормалізація плагінів", size=9.5, color="#64748b"))
    
    # Колонка 4: Binding & Reserve
    c4_x = c3_x + col_w + gap
    p.append(rect(c4_x, y_top, col_w, col_h, fill="#ecfdf5", stroke="#059669", sw=1.4, rx=6))
    p.append(text(c4_x + col_w / 2, y_top + 24, "4. Прив'язка (Binding)", size=13, color="#047857", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 42, "Атомарне закріплення за нодою", size=10, color="#64748b"))
    
    p.append(rect(c4_x + 10, y_top + 65, col_w - 20, 115, fill="#ffffff", stroke="#059669", sw=1.2, rx=4))
    p.append(text(c4_x + col_w / 2, y_top + 86, "Binding API Request", size=11.5, color="#047857", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 106, "POST /api/v1/namespaces/", size=9.5, color="#334155"))
    p.append(text(c4_x + col_w / 2, y_top + 122, "default/pods/web/binding", size=9.5, color="#047857"))
    p.append(text(c4_x + col_w / 2, y_top + 142, "target: Node-1", size=10, color="#0f172a", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 162, "Запис у etcd успішний!", size=9.5, color="#059669", bold=True))
    
    p.append(rect(c4_x + 10, y_top + 190, col_w - 20, 85, fill="#e0f2fe", stroke="#0284c7", sw=1.1, rx=4))
    p.append(text(c4_x + col_w / 2, y_top + 210, "Kubelet на Node 1", size=10.5, color="#0369a1", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 228, "PLEG ініціює запуск CRI", size=9.5, color="#334155"))
    p.append(text(c4_x + col_w / 2, y_top + 245, "CNI виділяє IP, cgroup активна", size=9.5, color="#334155"))
    p.append(text(c4_x + col_w / 2, y_top + 263, "Статус: Running", size=10, color="#059669", bold=True))
    
    p.append(text(c4_x + col_w / 2, y_top + 320, "Латентність планування:", size=10, color="#1e293b", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 340, "2–20 мс на один под", size=10.5, color="#059669", bold=True))
    p.append(text(c4_x + col_w / 2, y_top + 358, "Неблокуючий конвеєр", size=9.5, color="#64748b"))
    
    # Стрілки між колонками
    p.append(arrow(c1_x + col_w + 3, y_top + 180, c2_x - 3, y_top + 180, color="#3b82f6", sw=1.8))
    p.append(arrow(c2_x + col_w + 3, y_top + 180, c3_x - 3, y_top + 180, color="#2563eb", sw=1.8))
    p.append(arrow(c3_x + col_w + 3, y_top + 180, c4_x - 3, y_top + 180, color="#d97706", sw=1.8))
    
    render(os.path.join(OUT, "scheduling-pipeline.svg"), W, H, *p)


# ── Фіг. 4: Маршрутизація пакетів та Service Mesh ────────────────────────────
def fig_service_proxy_routing():
    W, H = 1080, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Маршрутизація трафіку: Віртуальні IP, eBPF та CNI Overlay", size=16, color="#1e3a8a", bold=True))
    p.append(text(W / 2, 60, "Шлях мережевого пакета від клієнтського сокета до цільового контейнера на іншому вузлі", size=11, color="#64748b"))
    
    # Лівий блок: Клієнтський вузол
    na_x, na_y, na_w, na_h = 25, 85, 420, 410
    p.append(rect(na_x, na_y, na_w, na_h, fill="#f8fafc", stroke="#0284c7", sw=1.6, rx=8))
    p.append(text(na_x + na_w / 2, na_y + 24, "Вузол відправника (Node A, IP: 192.168.1.10)", size=13, color="#0369a1", bold=True))
    
    # Клієнтський под
    cp_x, cp_y, cp_w, cp_h = na_x + 15, na_y + 45, 390, 85
    p.append(rect(cp_x, cp_y, cp_w, cp_h, fill="#eff6ff", stroke="#3b82f6", sw=1.3, rx=6))
    p.append(text(cp_x + cp_w / 2, cp_y + 20, "Клієнтський Pod (10.244.1.15)", size=11.5, color="#1d4ed8", bold=True))
    p.append(text(cp_x + cp_w / 2, cp_y + 38, "Запит на Service DNS: http://payment-service:8080", size=10, color="#0f172a"))
    p.append(text(cp_x + cp_w / 2, cp_y + 56, "CoreDNS повертає ClusterIP: 10.96.0.45:8080", size=10, color="#059669", bold=True))
    p.append(text(cp_x + cp_w / 2, cp_y + 72, "Пакет відправлено в інтерфейс eth0 (veth)", size=9.5, color="#64748b"))
    
    # Ядро Linux вузла А
    kn_x, kn_y, kn_w, kn_h = na_x + 15, na_y + 145, 390, 135
    p.append(rect(kn_x, kn_y, kn_w, kn_h, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(kn_x + kn_w / 2, kn_y + 22, "Ядро Linux: eBPF / iptables KUBE-SERVICES", size=11.5, color="#b45309", bold=True))
    p.append(text(kn_x + kn_w / 2, kn_y + 44, "1. Перехоплення пакету до ClusterIP (10.96.0.45)", size=9.5, color="#334155"))
    p.append(text(kn_x + kn_w / 2, kn_y + 62, "2. Таблиця EndpointSlice: бекенди [10.244.2.8, 10.244.2.9]", size=9.5, color="#475569"))
    p.append(text(kn_x + kn_w / 2, kn_y + 80, "3. Балансування (Random / Maglev Hash)", size=9.5, color="#b45309", bold=True))
    p.append(text(kn_x + kn_w / 2, kn_y + 98, "4. DNAT: 10.96.0.45:8080 → 10.244.2.8:8080", size=10, color="#dc2626", bold=True))
    p.append(text(kn_x + kn_w / 2, kn_y + 118, "В eBPF: підміна прямо на рівні sock_ops", size=9.5, color="#047857"))
    
    # CNI Інтерфейс та інкапсуляція
    cni_x, cni_y, cni_w, cni_h = na_x + 15, na_y + 295, 390, 90
    p.append(rect(cni_x, cni_y, cni_w, cni_h, fill="#f5f3ff", stroke="#7c3aed", sw=1.3, rx=6))
    p.append(text(cni_x + cni_w / 2, cni_y + 20, "CNI Плагін (Cilium / Calico / Flannel)", size=11.5, color="#6d28d9", bold=True))
    p.append(text(cni_x + cni_w / 2, cni_y + 40, "Маршрут: підмережа 10.244.2.0/24 на 192.168.1.20", size=9.5, color="#334155"))
    p.append(text(cni_x + cni_w / 2, cni_y + 58, "Інкапсуляція VXLAN / Geneve тунелю", size=9.5, color="#475569"))
    p.append(text(cni_x + cni_w / 2, cni_y + 76, "Зовнішній пакет: 192.168.1.10 → 192.168.1.20", size=9.5, color="#6d28d9", bold=True))
    
    # Стрілки всередині Node A
    p.append(arrow(cp_x + cp_w / 2, cp_y + cp_h + 2, kn_x + kn_w / 2, kn_y - 2, color="#3b82f6", sw=1.6))
    p.append(arrow(kn_x + kn_w / 2, kn_y + kn_h + 2, cni_x + cni_w / 2, cni_y - 2, color="#d97706", sw=1.6))
    
    # Правий блок: Цільовий вузол
    nb_x, nb_y, nb_w, nb_h = 635, 85, 420, 410
    p.append(rect(nb_x, nb_y, nb_w, nb_h, fill="#f8fafc", stroke="#059669", sw=1.6, rx=8))
    p.append(text(nb_x + nb_w / 2, nb_y + 24, "Цільовий вузол (Node B, IP: 192.168.1.20)", size=13, color="#047857", bold=True))
    
    # CNI Прийом на Node B
    cni_b_x, cni_b_y, cni_b_w, cni_b_h = nb_x + 15, nb_y + 295, 390, 90
    p.append(rect(cni_b_x, cni_b_y, cni_b_w, cni_b_h, fill="#f5f3ff", stroke="#7c3aed", sw=1.3, rx=6))
    p.append(text(cni_b_x + cni_b_w / 2, cni_b_y + 20, "CNI Декапсуляція (VXLAN Tunnel Endpoint)", size=11.5, color="#6d28d9", bold=True))
    p.append(text(cni_b_x + cni_b_w / 2, cni_b_y + 40, "Зняття UDP заголовка VXLAN (Port 4789)", size=9.5, color="#334155"))
    p.append(text(cni_b_x + cni_b_w / 2, cni_b_y + 58, "Вилучення внутрішнього пакета: Dst=10.244.2.8", size=9.5, color="#475569"))
    p.append(text(cni_b_x + cni_b_w / 2, cni_b_y + 76, "Скерування у локальний veth інтерфейс", size=9.5, color="#6d28d9", bold=True))
    
    # Локальний мережевий простір
    net_b_x, net_b_y, net_b_w, net_b_h = nb_x + 15, nb_y + 175, 390, 105
    p.append(rect(net_b_x, net_b_y, net_b_w, net_b_h, fill="#ecfdf5", stroke="#10b981", sw=1.3, rx=6))
    p.append(text(net_b_x + net_b_w / 2, net_b_y + 20, "Мережевий міст cbr0 / veth пара", size=11.5, color="#047857", bold=True))
    p.append(text(net_b_x + net_b_w / 2, net_b_y + 40, "Доставка пакета у Network Namespace пода", size=10, color="#334155"))
    p.append(text(net_b_x + net_b_w / 2, net_b_y + 58, "Підтримка Conntrack зв'язку для відповіді", size=9.5, color="#475569"))
    p.append(text(net_b_x + net_b_w / 2, net_b_y + 76, "NetworkPolicy фільтрація (Ingress правила)", size=10, color="#059669", bold=True))
    p.append(text(net_b_x + net_b_w / 2, net_b_y + 92, "Пакет успішно верифіковано", size=9.5, color="#64748b"))
    
    # Цільовий под
    tp_x, tp_y, tp_w, tp_h = nb_x + 15, nb_y + 45, 390, 115
    p.append(rect(tp_x, tp_y, tp_w, tp_h, fill="#eff6ff", stroke="#2563eb", sw=1.4, rx=6))
    p.append(text(tp_x + tp_w / 2, tp_y + 22, "Цільовий Pod: payment-service-5c8f", size=11.5, color="#1d4ed8", bold=True))
    p.append(text(tp_x + tp_w / 2, tp_y + 42, "IP: 10.244.2.8:8080 (Контейнер приймає HTTP POST)", size=10, color="#0f172a"))
    p.append(text(tp_x + tp_w / 2, tp_y + 60, "Обробка платіжної транзакції бізнес-логікою", size=10, color="#334155"))
    p.append(text(tp_x + tp_w / 2, tp_y + 78, "Відповідь HTTP 200 повертається тим самим шляхом", size=9.5, color="#059669", bold=True))
    p.append(text(tp_x + tp_w / 2, tp_y + 96, "Клієнт не знав фізичної адреси вузла B", size=9.5, color="#64748b"))
    
    # Стрілки всередині Node B
    p.append(arrow(cni_b_x + cni_b_w / 2, cni_b_y - 2, net_b_x + net_b_w / 2, net_b_y + net_b_h + 2, color="#7c3aed", sw=1.6))
    p.append(arrow(net_b_x + net_b_w / 2, net_b_y - 2, tp_x + tp_w / 2, tp_y + tp_h + 2, color="#10b981", sw=1.6))
    
    # Міжвузловий фізичний тунель L3 Network
    tunnel_x1 = cni_x + cni_w + 3
    tunnel_x2 = cni_b_x - 3
    tunnel_y = cni_y + cni_h / 2
    p.append(arrow(tunnel_x1, tunnel_y, tunnel_x2, tunnel_y, color="#6d28d9", sw=2.2))
    p.append(text((tunnel_x1 + tunnel_x2) / 2, tunnel_y - 14, "Фізична L3 мережа", size=10.5, color="#6d28d9", bold=True))
    p.append(text((tunnel_x1 + tunnel_x2) / 2, tunnel_y + 20, "VXLAN UDP 4789", size=10, color="#475569"))
    
    render(os.path.join(OUT, "service-proxy-routing.svg"), W, H, *p)


def main():
    fig_control_plane_architecture()
    fig_reconciliation_loop()
    fig_scheduling_pipeline()
    fig_service_proxy_routing()
    print("Generated 4 SVG figures successfully.")

if __name__ == "__main__":
    main()
