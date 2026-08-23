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
PURPLE  = "#7e22ce"

def fig_traffic_shedding_funnel():
    """Фільтрація та відкидання трафіку за категоріями пріоритетів під час перевантаження."""
    W, H = 1040, 460
    f = []

    # Заголовок блоків
    f.append(fitbox(50, 40, 260, 44, "вхідний трафік (усі класи)", size=14, bold=True, fill=NEUT, stroke=INK))

    # Ліва частина — категорії запитів
    cats = [
        (96,  "P0 · Критичні команди (замок, тривога)", POS, RED_T),
        (160, "P1 · Оперативна телеметрія (опалення)", FIELD, GREEN_T),
        (224, "P2 · Статуси онлайн / Presence", AMBER, AMBER_T),
        (288, "P3 · Історія телеметрії / Аналітика", NEG, BLUE_T),
        (352, "P4 · Відео-архів / Важкі батчі", PURPLE, PURPLE_T),
    ]
    for y, label, col, tint in cats:
        f.append(fitbox(50, y, 260, 52, label, size=12, bold=True, stroke=col, fill=tint))
        f.append(arrow(310, y + 26, 380, y + 26, color=col))

    # Складові адаптивного воронкоподібного фільтра (Shedder Gateway)
    f.append(rect(380, 80, 280, 340, fill=BG, stroke=INK, sw=2, rx=6))
    f.append(text(520, 110, "Load Shedding Gateway", size=15, bold=True, anchor="middle"))
    f.append(line(400, 126, 640, 126, color="#c8ced6", sw=1.2))

    f.append(fitbox(400, 140, 240, 50, "вимірювання тиску\nCPU / Latency / Queue", size=12, fill=NEUT, stroke=MUTED))
    f.append(fitbox(400, 204, 240, 50, "активний Brownout Level\n(поріг відкидання L0..L4)", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(400, 268, 240, 50, "гістерезис відновлення\n(захист від осциляції)", size=12, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(400, 332, 240, 70, "Admission Filter\nIf Priority < Cutoff -> Drop 503\nElse -> Pass to Workers", size=11, bold=True, fill=GREEN_T, stroke=FIELD))

    # Права частина — результати при Brownout Level 2
    f.append(fitbox(740, 40, 250, 44, "результат (Brownout L2)", size=14, bold=True, fill=NEUT, stroke=INK))

    results = [
        (96,  "P0 · Пропущено (100%)", FIELD, GREEN_T, 380, 122),
        (160, "P1 · Пропущено (100%)", FIELD, GREEN_T, 380, 186),
        (224, "P2 · Частково (Drop 50%)", AMBER, AMBER_T, 380, 250),
        (288, "P3 · Відкинуто (503 Retry)", POS, RED_T, 380, 314),
        (352, "P4 · Відкинуто (503 Retry)", POS, RED_T, 380, 378),
    ]
    for y, res_label, col, tint, src_x, src_y in results:
        f.append(arrow(660, src_y - 26, 740, y + 26, color=col))
        f.append(fitbox(740, y, 250, 52, res_label, size=12, bold=True, stroke=col, fill=tint))

    render(os.path.join(OUT, 'traffic-shedding-funnel.svg'), W, H, *f,
           title="Фільтрація та відкидання трафіку за пріоритетами під тиском")


def fig_shedding_decision_tree():
    """Алгоритм перевірки та ухвалення рішення шлюзом Admission Control."""
    W, H = 1000, 440
    f = []

    # Крок 1: Вхід запиту
    f.append(fitbox(40, 185, 170, 70, "Вхідний запит\n(HTTP/gRPC/MQTT)", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(210, 220, 270, 220))

    # Крок 2: Валідація метаданих
    f.append(fitbox(270, 175, 200, 90, "Атрибуція пріоритету\nперевірка Auth/Context\n-> Присвоєння P0..P4", size=12, fill=BLUE_T, stroke=NEG))
    f.append(arrow(470, 220, 530, 220))

    # Крок 3: Перевірка порогового завантаження
    f.append(fitbox(530, 170, 210, 100, "Оцінка стану ноди\nSystem Load vs Threshold(P)\nQueue Delay > Max?", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка ТАК -> Відкидання (вгору)
    f.append(arrow(635, 170, 635, 110, color=POS))
    f.append(text(645, 140, "Load >= Cutoff", size=11, color=POS, bold=True))
    f.append(fitbox(530, 40, 210, 70, "ВІДКИДАННЯ (Shed)\n503 Service Unavailable\nRetry-After: N sec", size=12, bold=True, fill=RED_T, stroke=POS))

    # Гілка НІ -> Обробка (праворуч)
    f.append(arrow(740, 220, 800, 220, color=FIELD))
    f.append(text(750, 205, "Load < Cutoff", size=11, color=FIELD, bold=True))
    f.append(fitbox(800, 185, 160, 70, "ПРИЙОМ (Pass)\nПередача у воркер\nвиконання бізнес-логіки", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'shedding-decision-tree.svg'), W, H, *f,
           title="Дерево ухвалення рішення admission control при відкиданні")


def fig_brownout_staircase():
    """Сходи деградації (Brownout-план) на прикладі Digital Homes (DH)."""
    W, H = 1020, 450
    f = []

    levels = [
        (40,  320, 170, 80, "L0 · Норма (100%)\nУсі сервіси активні\nВідео, аналітика, робота", FIELD, GREEN_T),
        (220, 250, 170, 80, "L1 · Приглушення P4\nВимкнено відео-архів\n503 на аплоад медіа", FIELD, GREEN_T),
        (400, 180, 170, 80, "L2 · Приглушення P3\nЗупинено аналітику\nБуферизація історії", AMBER, AMBER_T),
        (580, 110, 170, 80, "L3 · Приглушення P2\nПригнічено presence\nHeartbeat 1 хв замість 5 с", AMBER, AMBER_T),
        (760, 40,  200, 80, "L4 · Аварійний (P0/P1)\nЛише замки, тривоги\nі термінове опалення", POS, RED_T),
    ]

    for x, y, w, h, label, col, tint in levels:
        f.append(fitbox(x, y, w, h, label, size=12, bold=True, stroke=col, fill=tint))

    # Стрілки наростання тиску під сходами
    f.append(arrow(50, 420, 950, 420, color=POS, sw=3))
    f.append(text(500, 405, "Наростання навантаження / системного тиску (CPU, Latency, Concurrency) →", size=13, bold=True, anchor="middle", color=POS))

    render(os.path.join(OUT, 'brownout-staircase.svg'), W, H, *f,
           title="Сходи деградації (Brownout Plan) системи Digital Homes")


def fig_priority_shedding_timeline():
    """Родовід та еволюція тактик пріоритезації трафіку та відкидання навантаження."""
    W, H = 1000, 750
    f = []

    ax = 240
    f.append(line(ax, 70, ax, 680, color="#c8ced6", sw=2))

    nodes = [
        (100, "1960-ті · Телефонні мережі (PSTN)", "ACR (Automatic Congestion Control): відкидання дзвінків на вході АТС", GREEN_T, FIELD),
        (190, "1980-ті · Електромережі (Power Grids)", "Brownout (просідання напруги) & Automatic Load Shedding за частотою 49.5 Гц", GREEN_T, FIELD),
        (280, "1990-ті · Ранній Інтернет (IP QoS)", "DiffServ / DSCP заголовки в IP-пакетах, Weighted Fair Queueing (WFQ) у роутерах", GREEN_T, FIELD),
        (370, "2000-ні · Ранній Веб & E-Commerce", "Голий 503 Service Unavailable, static rate limiting за IP-адресами", RED_T, POS),
        (460, "2010-ті · AWS / Google SRE", "Adaptive Concurrency Limiting, CoDel queue management, Priority Shedding", BLUE_T, NEG),
        (550, "2020-ті · Cloud-Native & Microservices", "Header-based Traffic Shedding, Brownout Automation, Envoy/Istio Adaptive Limiters", BLUE_T, NEG),
        (640, "Сучасність · Zero-Trust Priority", "Cryptographic Priority Headers, ML-driven Brownout Controllers, E2E Backpressure", BLUE_T, NEG),
    ]

    for cy, head, essence, tint, col in nodes:
        f.append(rect(290, cy - 30, 660, 60, fill=tint, stroke=col, sw=1.5))
        f.append(text(306, cy - 6, head, size=15, bold=True, anchor="start"))
        f.append(text(306, cy + 16, essence, size=12, color=MUTED, anchor="start"))
        f.append(circle(ax, cy, 7, fill=col, stroke=BG, sw=2))
        f.append(line(ax + 7, cy, 290, cy, color="#c8ced6", sw=1.4))

    eras = [
        (80,  310, FIELD, "Телеком і\nЕнергетика"),
        (340, 410, POS, "Примітивний\nВеб"),
        (430, 670, NEG, "Адаптивні\nХмари"),
    ]
    for y1, y2, col, label in eras:
        f.append(rect(205, y1, 5, y2 - y1, fill=col, stroke=col, sw=1, rx=2))
        f.append(mtext(110, (y1 + y2) / 2 - 4, label, size=13, color=col, bold=True))

    render(os.path.join(OUT, 'priority-shedding-timeline.svg'), W, H, *f,
           title="Родовід і еволюція тактик відкидання навантаження")


def fig_header_attribution_flow():
    """Атрибуція пріоритету запиту та прокидання контексту крізь мікросервіси."""
    W, H = 1040, 400
    f = []

    # Клієнт
    f.append(fitbox(40, 140, 180, 110, "Клієнт (Панель/App)\n\nНадсилає запит з\nX-Priority: P0-Critical\nабо OAuth Token", size=12, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(220, 195, 290, 195))

    # Edge Gateway
    f.append(rect(290, 110, 240, 170, fill=AMBER_T, stroke=AMBER, sw=1.8))
    f.append(text(410, 138, "Edge Gateway (Ingress)", size=14, bold=True, anchor="middle"))
    f.append(line(310, 150, 510, 150, color=AMBER, sw=1))
    f.append(mtext(410, 205, "1. Перевірка Auth/Token\n2. Захист від Spoofing\n3. Запис хмарного контексту\n(Priority=P0, TraceId=abc)", size=12, anchor="middle"))

    f.append(arrow(530, 195, 600, 195, color=FIELD))
    f.append(text(565, 180, "Internal gRPC\nMetadata", size=11, color=FIELD, bold=True))

    # Внутрішній мікросервіс А
    f.append(fitbox(600, 140, 180, 110, "Сервіс Дверей (P0)\n\nБачить Context P0\nВпустити без черги\nПрокидає context далі", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(780, 195, 840, 195, color=FIELD))

    # Сервіс Б
    f.append(fitbox(840, 140, 160, 110, "Сервіс Замка\n\nОтримує P0\nВиконує негайно", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'header-attribution-flow.svg'), W, H, *f,
           title="Атрибуція пріоритету та захищене прокидання контексту")


if __name__ == '__main__':
    fig_traffic_shedding_funnel()
    fig_shedding_decision_tree()
    fig_brownout_staircase()
    fig_priority_shedding_timeline()
    fig_header_attribution_flow()
    print("figures written to", OUT)
