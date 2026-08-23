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

def fig_multi_region_topologies_overview():
    """Схематичне порівняння трьох основних топологій мультирегіону: Active-Passive, Global Read / Single Write та Active-Active з партиціюванням."""
    W, H = 1080, 460
    f = []

    # Топологія 1: Active-Passive (Панель 1)
    f.append(rect(30, 40, 330, 390, fill=NEUT, stroke=INK, rx=8))
    f.append(text(195, 65, "1. Active-Passive (Failover)", size=13, bold=True, color=INK))

    f.append(fitbox(55, 90, 280, 55, "Регіон A (Frankfurt - Primary)\nMaster DB (100% Записи + Читання)", size=11, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(195, 145, 195, 205, color=AMBER, sw=2))
    f.append(text(205, 178, "WAN Async Sync", size=10, color=AMBER, anchor="start"))
    f.append(fitbox(55, 205, 280, 55, "Регіон B (Virginia - Standby)\nPassive Replica (0% Трафіку)", size=11, fill=RED_T, stroke=POS))

    f.append(mtext(45, 280, "• RTO: 1–5 хв · RPO: 1–10 сек\n• Небезпека: Split-brain при паніці\n• Найпростіший старт для DR", size=11, color=INK, anchor="start"))

    # Топологія 2: Global Read / Single Write (Панель 2)
    f.append(rect(375, 40, 330, 390, fill=NEUT, stroke=INK, rx=8))
    f.append(text(540, 65, "2. Global Read / Single Write", size=13, bold=True, color=INK))

    f.append(fitbox(400, 90, 280, 55, "Регіон A (Primary Master)\nЄдине джерело запису", size=11, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(470, 145, 440, 205, color=NEG, sw=1.8))
    f.append(arrow(610, 145, 640, 205, color=NEG, sw=1.8))
    f.append(text(540, 178, "Async Replication", size=10, color=MUTED, anchor="middle"))

    f.append(fitbox(390, 205, 135, 55, "Регіон B (US)\nRead Replica", size=10, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(555, 205, 135, 55, "Регіон C (Asia)\nRead Replica", size=10, fill=BLUE_T, stroke=NEG))

    f.append(mtext(390, 280, "• Швидке читання по всьому світу\n• Записи йдуть через океан (WAN)\n• Ризик Replication Lag & RAW", size=11, color=INK, anchor="start"))

    # Топологія 3: Active-Active (Partitioned) (Панель 3)
    f.append(rect(720, 40, 330, 390, fill=NEUT, stroke=INK, rx=8))
    f.append(text(885, 65, "3. Active-Active (Home-Region)", size=13, bold=True, color=INK))

    f.append(fitbox(735, 90, 140, 65, "Регіон A (EU)\nMaster EU\n(EU Будинки)", size=10, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(895, 90, 140, 65, "Регіон B (US)\nMaster US\n(US Будинки)", size=10, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(arrow(875, 115, 895, 115, color=PURPLE_T, sw=1.8))
    f.append(arrow(895, 130, 875, 130, color="#8b5cf6", sw=1.8))
    f.append(text(885, 178, "Global Sync / CRDT", size=10, color="#8b5cf6", anchor="middle"))

    f.append(mtext(735, 280, "• Zero WAN latency на записи\n• Повна локальна автономність\n• Вимагає партиціювання ключа", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'multi-region-topologies-overview.svg'), W, H, *f,
           title="Основні архітектурні топології мультирегіону")

def fig_rtt_read_after_write():
    """Послідовність обробки запиту з забезпеченням Read-After-Write узгодженості."""
    W, H = 1000, 430
    f = []

    # Компоненти нагорі
    f.append(fitbox(40, 40, 180, 50, "Клієнт (Tokyo)\nМобільний застосунок", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(300, 40, 180, 50, "Geo-Router (Tokyo)\nEdge Ingress / API", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(560, 40, 180, 50, "Read Replica (Tokyo)\nAsync Replica (Lag 200ms)", size=12, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(800, 40, 160, 50, "Primary DB (Frankfurt)\nSource of Truth", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Пунктирні вертикальні осі часу
    f.append(line(130, 95, 130, 400, color=MUTED, sw=1, dash="2 2"))
    f.append(line(390, 95, 390, 240, color=MUTED, sw=1, dash="2 2"))
    f.append(line(390, 300, 390, 400, color=MUTED, sw=1, dash="2 2"))
    f.append(line(650, 95, 650, 400, color=MUTED, sw=1, dash="2 2"))
    f.append(line(880, 95, 880, 400, color=MUTED, sw=1, dash="2 2"))

    # Крок 1: Запис (Write Path)
    f.append(arrow(130, 120, 390, 120, color=AMBER, sw=2))
    f.append(text(260, 110, "1. PUT /devices/light (Write)", size=11, color=AMBER, anchor="middle"))

    f.append(arrow(390, 140, 880, 140, color=AMBER, sw=2))
    f.append(text(635, 130, "WAN Route to Primary (RTT 220ms)", size=11, color=AMBER, anchor="middle"))

    f.append(arrow(880, 175, 130, 175, color=FIELD, sw=2))
    f.append(text(505, 165, "2. 200 OK + Header: X-LSN=4200 (RAW Token)", size=11, color=FIELD, anchor="middle"))

    # Крок 2: Негайне читання (Read Path з перевіркою токена)
    f.append(arrow(130, 225, 390, 225, color=NEG, sw=2))
    f.append(text(260, 215, "3. GET /devices (Read + LSN=4200)", size=11, color=NEG, anchor="middle"))

    # Блок перевірки в Router (x: 305..475, y: 245..295)
    f.append(fitbox(305, 245, 170, 50, "Check Tokyo LSN:\nReplica LSN = 4150\n(Lag detected!)", size=10, fill=RED_T, stroke=POS))

    # Маршрутизація на Primary через лаг
    f.append(arrow(390, 335, 880, 335, color=POS, sw=2))
    f.append(text(635, 325, "4. Lag > Target → Fallback to Primary DB (Frankfurt)", size=11, color=POS, anchor="middle"))

    f.append(arrow(880, 375, 130, 375, color=FIELD, sw=2))
    f.append(text(505, 365, "5. 200 OK (Guaranteed Consistent Data)", size=11, color=FIELD, anchor="middle"))

    render(os.path.join(OUT, 'multi-region-topologies-overview.svg'), W, H, *f,
           title="Основні архітектурні топології мультирегіону")
    render(os.path.join(OUT, 'rtt-read-after-write.svg'), W, H, *f,
           title="Механіка Read-After-Write при міжрегіональній реплікації")

if __name__ == '__main__':
    fig_multi_region_topologies_overview()
    fig_rtt_read_after_write()
    print("Figures generated successfully!")
