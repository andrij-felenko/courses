# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"
PURPLE_T= "#f3e8ff"

def fig_compute_cost_curves():
    """Криві витрат TCO для Serverless, Kubernetes та Bare Metal/VM залежно від утилізації."""
    W, H = 1040, 480
    f = []

    # Заголовок та сітка
    f.append(fitbox(40, 30, 960, 45, "Криві витрат TCO: Serverless vs Kubernetes vs Bare Metal / VM", size=15, bold=True, fill=NEUT, stroke=INK))

    # Вісі графіка
    ox, oy = 90, 410
    gx_w, gy_h = 620, 300

    # Вісь X (Навантаження / Утилізація %)
    f.append(line(ox, oy, ox + gx_w + 30, oy, color=INK, sw=2))
    f.append(arrow(ox + gx_w + 20, oy, ox + gx_w + 35, oy, color=INK, sw=2))
    f.append(text(ox + gx_w + 40, oy + 5, "Середня утилізація / RPS", size=12, color=INK, anchor="start", bold=True))

    # Вісь Y (Щомісячний TCO $)
    f.append(line(ox, oy, ox, oy - gy_h - 20, color=INK, sw=2))
    f.append(arrow(ox, oy - gy_h - 10, ox, oy - gy_h - 25, color=INK, sw=2))
    f.append(text(ox - 10, oy - gy_h - 30, "Щомісячні витрати TCO ($)", size=12, color=INK, anchor="start", bold=True))

    # Засічки та сітка по X
    for pct, px in [(0, ox), (25, ox + 155), (50, ox + 310), (75, ox + 465), (100, ox + 620)]:
        f.append(line(px, oy, px, oy + 6, color=INK, sw=1.5))
        f.append(text(px, oy + 22, f"{pct}%", size=11, color=MUTED, anchor="middle"))
        if pct > 0:
            f.append(line(px, oy, px, oy - gy_h, color="#e5e7eb", sw=1, dash="3 3"))

    # Засічки по Y
    f.append(text(ox - 10, oy - 20, "$0", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 140, "Базовий кворум", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 270, "Високий фіксований TCO", size=11, color=MUTED, anchor="end"))

    # Крива 1: Serverless (AWS Lambda / Fargate) - зелена
    f.append(line(ox, oy, ox + 620, oy - 290, color=FIELD, sw=3.5))
    f.append(text(ox + 500, oy - 250, "Serverless / Fargate", size=12, color=FIELD, bold=True, anchor="start"))

    # Крива 2: Kubernetes (EKS / Managed K8s) - синя
    f.append(line(ox, oy - 90, ox + 620, oy - 220, color=NEG, sw=3.5))
    f.append(text(ox + 520, oy - 175, "Managed Kubernetes", size=12, color=NEG, bold=True, anchor="start"))

    # Крива 3: Bare Metal / VM (Фіксовані сервери) - червона
    f.append(line(ox, oy - 210, ox + 620, oy - 225, color=POS, sw=3.5))
    f.append(text(ox + 450, oy - 105, "Bare Metal / VM Fleet", size=12, color=POS, bold=True, anchor="start"))

    # Перетиналися криві (Breakeven Points)
    p1_x = ox + 110
    p1_y = oy - 51
    f.append(circle(p1_x, p1_y, 6, fill=AMBER, stroke=INK, sw=1.5))
    f.append(line(p1_x, p1_y, p1_x, oy, color=AMBER, sw=1.5, dash="4 3"))
    f.append(fitbox(p1_x - 55, p1_y - 45, 115, 36, "U_crit1 ≈ 15-20%\nServerless ↔ K8s", size=10, bold=True, fill=AMBER_T, stroke=AMBER))

    p2_x = ox + 405
    p2_y = oy - 218
    f.append(circle(p2_x, p2_y, 6, fill=AMBER, stroke=INK, sw=1.5))
    f.append(line(p2_x, p2_y, p2_x, oy, color=AMBER, sw=1.5, dash="4 3"))
    f.append(fitbox(p2_x - 60, p2_y - 45, 125, 36, "U_crit2 ≈ 65-70%\nK8s ↔ Bare Metal", size=10, bold=True, fill=AMBER_T, stroke=AMBER))

    # Права панель з поясненнями режимів
    px_start = 765
    f.append(fitbox(px_start, 95, 235, 100, "1. Зона Serverless (0–18%)\n• Нульова плата за простій\n• Оплата за ms виконання\n• Вигідна для пилкоподібного / спалахового навантаження", size=11, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(px_start, 210, 235, 100, "2. Зона Kubernetes (18–68%)\n• Автомасштабування (HPA)\n• Щільне пакування (Bin-packing)\n• Баланс між Ops та ціною", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(px_start, 325, 235, 95, "3. Зона Bare Metal (68–100%)\n• Мінімальна ціна 1 core/sec\n• Нульовий Virtualization Overhead\n• Висока операційна складність", size=11, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'compute-cost-curves.svg'), W, H, *f,
           title="Порівняння кривих TCO обчислювальних платформ залежно від утилізації")

def fig_platform_tradeoff_radar():
    """Матриця компромісів між Serverless/Fargate, Kubernetes та Bare Metal/VM за 4 критеріями."""
    W, H = 1040, 440
    f = []

    # Заголовок
    f.append(fitbox(40, 25, 960, 45, "Порівняльний шар компромісів обчислювальних платформ (DH Matrix)", size=15, bold=True, fill=NEUT, stroke=INK))

    # 3 великі колонки для трьох моделей
    col_w = 300
    gap = 25
    left_m = 45

    # 1. Serverless / Fargate
    c1_x = left_m
    f.append(fitbox(c1_x, 85, col_w, 55, "Serverless / Fargate\n(AWS Lambda, Cloud Run, Fargate)", size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(c1_x, 150, col_w, 260, 
                    "• Затримка p99: Низька / Cold Start (50ms–2s)\n"
                    "• Утилізація: Ідеальна (Pay-per-use, 0% idle)\n"
                    "• Ціна 24/7: Дуже висока ($/GB-sec)\n"
                    "• Операційне навантаження: Мінімальне (No OS/K8s)\n"
                    "• Контроль ядра/Hardware: Відсутній (Sandbox)\n\n"
                    "🎯 Найкраще для: Webhooks, Crons, Spiky REST API",
                    size=11, fill=BG, stroke=FIELD))

    # 2. Kubernetes
    c2_x = left_m + col_w + gap
    f.append(fitbox(c2_x, 85, col_w, 55, "Kubernetes Cluster\n(Managed EKS / GKE / Self-hosted)", size=13, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(c2_x, 150, col_w, 260,
                    "• Затримка p99: Стабільна (< 5ms), без cold start\n"
                    "• Утилізація: Висока (Bin-packing HPA/KEDA)\n"
                    "• Ціна 24/7: Поміркована (Spot + Savings Plans)\n"
                    "• Операційне навантаження: Помірне/Високе (K8s Ops)\n"
                    "• Контроль ядра/Hardware: Частковий (cgroups/Device)\n\n"
                    "🎯 Найкраще для: Microservices, Core API, Ingress",
                    size=11, fill=BG, stroke=NEG))

    # 3. Bare Metal / VM Fleet
    c3_x = left_m + (col_w + gap) * 2
    f.append(fitbox(c3_x, 85, col_w, 55, "Bare Metal / Direct VM\n(Physical Rack / IaaS EC2/KVM)", size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(c3_x, 150, col_w, 260,
                    "• Затримка p99: Ультра-низька (< 1ms, CPU Pinning)\n"
                    "• Утилізація: Погана при спалахах (Fixed Limit)\n"
                    "• Ціна 24/7: Мінімальна за 1 core (При U > 70%)\n"
                    "• Операційне навантаження: Максимальне (OS, HW, Network)\n"
                    "• Контроль ядра/Hardware: Повний (eBPF, DPDK, GPU)\n\n"
                    "🎯 Найкраще для: IoT Stream Ingest, Video AI, DB",
                    size=11, fill=BG, stroke=POS))

    render(os.path.join(OUT, 'platform-tradeoff-radar.svg'), W, H, *f,
           title="Порівняльний шар компромісів обчислювальних платформ")

if __name__ == "__main__":
    fig_compute_cost_curves()
    fig_platform_tradeoff_radar()
    print("Figures generated successfully!")
