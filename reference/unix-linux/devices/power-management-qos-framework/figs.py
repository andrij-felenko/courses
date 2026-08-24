# -*- coding: utf-8 -*-
"""Фігури до теми «Фреймворк гарантій продуктивності PM QoS»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG  = "#eaf0fd"
GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
PURPLE_BG = "#f3e8ff"
ORANGE_BG = "#fff7ed"


# ── 0. Агрегація вимог за мінімумом ─────────────────────────────────────────
def fig_aggregation():
    W, H = 980, 430

    P = []
    LX = 210          # центр стовпця споживачів
    AX0, AY0, AW, AH = 470, 150, 170, 130   # рамка агрегації
    RX = 830          # центр рамки результату

    consumers = [
        (110, "Процес A", "не більше 100 мкс"),
        (215, "Процес B", "не більше 10 мкс"),
        (320, "Мережевий драйвер", "не більше 50 мкс"),
    ]

    edges = []
    for cy, who, what in consumers:
        body, w, h = textbox(LX, cy, who + "\n" + what, size=14,
                             fill=BLUE_BG, stroke=NEG, sw=1.6)
        P.append(body)
        edges.append((LX + w / 2, cy))

    P.append(fitbox(AX0, AY0, AW, AH,
                    "PM QoS\nсписок вимог\nCPU latency QoS\nагрегація min()",
                    size=14, fill=GREEN_BG, stroke=FIELD, sw=1.8))

    res, rw, rh = textbox(RX, AY0 + AH / 2, "cpuidle\nціль 10 мкс", size=14,
                          fill=RED_BG, stroke=POS, sw=1.8)
    P.append(res)

    targets = [(AX0 - 6, AY0 + 24), (AX0 - 6, AY0 + AH / 2), (AX0 - 6, AY0 + AH - 24)]
    for (x1, y1), (x2, y2) in zip(edges, targets):
        P.append(arrow(x1 + 6, y1, x2, y2, color=NEG))

    P.append(arrow(AX0 + AW + 6, AY0 + AH / 2, RX - rw / 2 - 6, AY0 + AH / 2))

    P.append(text(LX, 385, "три незалежні вимоги", size=12.5, color=MUTED))
    P.append(text(AX0 + AW / 2, 385, "min(100, 10, 50) = 10", size=12.5, color=MUTED))
    P.append(text(RX, 385, "глибші стани заборонено", size=12.5, color=MUTED))

    P.append(text(W / 2, 412,
                  "виграє найжорсткіша вимога: щойно процес B закриє дескриптор, "
                  "ціллю стане 50 мкс",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "pm-qos-aggregation.svg"), W, H, *P,
           title="Об'єднання вимог у єдине обмеження CPU latency QoS")


# ── 1. Загальна архітектура PM QoS ──────────────────────────────────────────
def fig_architecture():
    W, H = 1000, 480
    P = []

    # Колонка 1: Джерела вимог (Клієнти)
    P.append(rect(40, 40, 240, 390, fill=FILL, stroke=MUTED, sw=1.5))
    P.append(text(160, 65, "Джерела вимог (Clients)", size=15, bold=True, color=INK))
    
    b1, w1, h1 = textbox(160, 120, "User Space Application\n/dev/cpu_dma_latency", size=13, fill=BLUE_BG, stroke=NEG)
    b2, w2, h2 = textbox(160, 225, "Device Drivers (Kernel)\nNetwork, Storage, GPU", size=13, fill=BLUE_BG, stroke=NEG)
    b3, w3, h3 = textbox(160, 330, "Thermal Governors / Sysfs\nscaling_min_freq", size=13, fill=BLUE_BG, stroke=NEG)
    P.extend([b1, b2, b3])

    # Колонка 2: Менеджери PM QoS
    P.append(rect(340, 40, 320, 390, fill=FILL, stroke=LINE, sw=1.8))
    P.append(text(500, 65, "Фреймворк PM QoS (kernel/power/qos.c)", size=15, bold=True, color=INK))
    
    m1, mw1, mh1 = textbox(500, 120, "CPU Latency QoS\n(cpu_latency_constraints)", size=13, fill=GREEN_BG, stroke=FIELD)
    m2, mw2, mh2 = textbox(500, 225, "Per-Device PM QoS\n(struct dev_pm_qos)", size=13, fill=GREEN_BG, stroke=FIELD)
    m3, mw3, mh3 = textbox(500, 330, "Frequency QoS\n(struct freq_constraints)", size=13, fill=GREEN_BG, stroke=FIELD)
    P.extend([m1, m2, m3])

    # Колонка 3: Споживачі підсистем
    P.append(rect(720, 40, 240, 390, fill=FILL, stroke=MUTED, sw=1.5))
    P.append(text(840, 65, "Ядерні підсистеми", size=15, bold=True, color=INK))

    c1, cw1, ch1 = textbox(840, 120, "cpuidle Governor\n(C-states Selection)", size=13, fill=RED_BG, stroke=POS)
    c2, cw2, ch2 = textbox(840, 225, "Device Power Domains\nPCIe LTR / Runtime PM", size=13, fill=RED_BG, stroke=POS)
    c3, cw3, ch3 = textbox(840, 330, "cpufreq / devfreq\nDVFS Policy Governors", size=13, fill=RED_BG, stroke=POS)
    P.extend([c1, c2, c3])

    # Зв'язки (Стрілки)
    P.append(arrow(160 + w1/2 + 4, 120, 500 - mw1/2 - 4, 120, color=NEG))
    P.append(arrow(160 + w2/2 + 4, 225, 500 - mw2/2 - 4, 225, color=NEG))
    P.append(arrow(160 + w3/2 + 4, 330, 500 - mw3/2 - 4, 330, color=NEG))

    P.append(arrow(500 + mw1/2 + 4, 120, 840 - cw1/2 - 4, 120, color=POS))
    P.append(arrow(500 + mw2/2 + 4, 225, 840 - cw2/2 - 4, 225, color=POS))
    P.append(arrow(500 + mw3/2 + 4, 330, 840 - cw3/2 - 4, 330, color=POS))

    # Підпис
    P.append(text(W / 2, 455, "Запити вимог від системних процесів та драйверів агрегуються у PM QoS і транслюються у підсистеми управління живленням", size=12.5, color=MUTED))

    render(os.path.join(OUT, "pm-qos-architecture.svg"), W, H, *P, title="Архітектура фреймворку PM QoS")


# ── 2. Внутрішній устрій pm_qos_constraints та plist ─────────────────────────
def fig_plist_flow():
    W, H = 960, 460
    P = []

    P.append(rect(40, 30, 880, 380, fill=FILL, stroke=LINE, sw=1.8))
    P.append(text(480, 55, "Структура pm_qos_constraints (kernel/power/qos.c)", size=15, bold=True, color=INK))

    P.append(rect(60, 75, 530, 245, fill=GREEN_BG, stroke=FIELD, sw=1.5))
    P.append(text(325, 100, "Пріоритетний список запитів (struct plist_head)", size=14, bold=True, color=INK))

    n1, nw1, nh1 = textbox(150, 160, "Req 1: Process A\npriority = 10 µs", size=12, fill=BLUE_BG, stroke=NEG)
    n2, nw2, nh2 = textbox(325, 160, "Req 2: Driver B\npriority = 50 µs", size=12, fill=BLUE_BG, stroke=NEG)
    n3, nw3, nh3 = textbox(490, 160, "Req 3: Process C\npriority = 100 µs", size=12, fill=BLUE_BG, stroke=NEG)
    P.extend([n1, n2, n3])

    P.append(arrow(150 + nw1/2 + 3, 160, 325 - nw2/2 - 3, 160, color=NEG))
    P.append(arrow(325 + nw2/2 + 3, 160, 490 - nw3/2 - 3, 160, color=NEG))

    P.append(text(325, 230, "plist: вставка за O(K) пріоритетів, вибір min/max за O(1)", size=12, color=MUTED, bold=False))
    P.append(text(325, 260, "Агреговане значення: target_value = plist_first() = 10 µs", size=13, color=POS, bold=True))

    P.append(rect(610, 75, 290, 245, fill=ORANGE_BG, stroke=POS, sw=1.5))
    P.append(text(755, 100, "Ланцюжок сповіщень", size=14, bold=True, color=POS))
    P.append(text(755, 120, "(blocking_notifier_head)", size=12, color=MUTED))

    notif, ntw, nth = textbox(755, 190, "blocking_notifier_call_chain()\n\nСпрацьовує при зміні\nагрегованого ліміту", size=12, fill=BG, stroke=POS)
    P.append(notif)

    P.append(arrow(590, 190, 610, 190, color=POS, sw=2.0))

    P.append(rect(60, 335, 840, 55, fill=PURPLE_BG, stroke=MUTED, sw=1.2))
    P.append(text(480, 368, "Кроки: 1. add/update/remove request  →  2. plist_add/del  →  3. Перерахунок target  →  4. Notifier Call Chain", size=12.5, color=INK, bold=True))

    P.append(text(W / 2, 440, "Сортована структура plist забезпечує миттєвий вибір найжорсткішої вимоги PM_QOS_MIN / PM_QOS_MAX", size=12.5, color=MUTED))

    render(os.path.join(OUT, "plist-aggregation-flow.svg"), W, H, *P, title="Агрегація за допомогою plist та сповіщення")


# ── 3. Взаємодія з апаратурою ──────────────────────────────────────────────
def fig_device_mapping():
    W, H = 960, 440
    P = []

    P.append(rect(30, 30, 430, 360, fill=GREEN_BG, stroke=FIELD, sw=1.5))
    P.append(text(245, 55, "Per-Device PM QoS (struct dev_pm_qos)", size=14, bold=True, color=INK))
    
    d1, dw1, dh1 = textbox(245, 105, "Resume Latency Constraint\npm_qos_resume_latency_us", size=12.5, fill=BLUE_BG, stroke=NEG)
    d2, dw2, dh2 = textbox(245, 185, "Latency Tolerance (LTR)\npm_qos_latency_tolerance_us", size=12.5, fill=BLUE_BG, stroke=NEG)
    d3, dw3, dh3 = textbox(245, 265, "Flags Constraint\nPM_QOS_FLAG_NO_POWER_OFF", size=12.5, fill=BLUE_BG, stroke=NEG)
    P.extend([d1, d2, d3])

    P.append(rect(500, 30, 430, 360, fill=ORANGE_BG, stroke=POS, sw=1.5))
    P.append(text(715, 55, "Frequency QoS (struct freq_constraints)", size=14, bold=True, color=INK))

    f1, fw1, fh1 = textbox(715, 120, "Minimum Frequency Limit\nFREQ_QOS_MIN (PM_QOS_MAX aggregation)", size=12.5, fill=RED_BG, stroke=POS)
    f2, fw2, fh2 = textbox(715, 230, "Maximum Frequency Limit\nFREQ_QOS_MAX (PM_QOS_MIN aggregation)", size=12.5, fill=RED_BG, stroke=POS)
    P.extend([f1, f2])

    P.append(arrow(245, 295, 245, 335, color=NEG))
    P.append(text(245, 360, "Трансляція в PCIe LTR пакети, Power Domains та ASPM", size=12, color=INK, bold=True))

    P.append(arrow(715, 275, 715, 335, color=POS))
    P.append(text(715, 360, "Обмеження діапазону DVFS / OPP у cpufreq & devfreq", size=12, color=INK, bold=True))

    P.append(text(W / 2, 420, "Спеціалізовані QoS фреймворку керують апаратними станами шин, енергодоменів та робочими частотами", size=12.5, color=MUTED))

    render(os.path.join(OUT, "device-and-freq-qos-mapping.svg"), W, H, *P, title="Взаємодія Per-Device та Frequency QoS з апаратурою")


if __name__ == "__main__":
    fig_aggregation()
    fig_architecture()
    fig_plist_flow()
    fig_device_mapping()
    print("ok")
