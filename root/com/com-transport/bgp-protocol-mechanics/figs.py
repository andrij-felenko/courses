# -*- coding: utf-8 -*-
"""Фігури до теми «BGP: протокол між провайдерами».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# 1. Topology eBGP and iBGP
def fig_ebgp_ibgp_topology():
    W, H = 820, 460
    f = [text(W / 2, 28, "Архітектурний поділ BGP: eBGP (зовнішній) та iBGP (внутрішній)", size=15, bold=True)]

    # AS 64500 (Border AS Left)
    f.append(rect(30, 60, 180, 260, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(120, 85, "AS 64500", size=13, bold=True, color=NEG))
    f.append(text(120, 105, "Провайдер A", size=11, color=MUTED))

    f.append(rect(50, 140, 140, 60, fill="#eef3ff", stroke=NEG, sw=1.6, rx=6))
    f.append(text(120, 165, "Роутер R1", size=12, bold=True, color=NEG))
    f.append(text(120, 185, "198.51.100.1", size=10, color=MUTED))

    # AS 64501 (Transit AS Right)
    f.append(rect(280, 60, 510, 260, fill="#fdfefe", stroke=LINE, sw=1.4, rx=8))
    f.append(text(535, 85, "AS 64501 (Транзитна автономна система)", size=13, bold=True, color=FIELD))

    # Boundary Router R2
    f.append(rect(310, 140, 130, 60, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(375, 165, "Роутер R2 (Edge)", size=12, bold=True, color=FIELD))
    f.append(text(375, 185, "198.51.100.2", size=10, color=MUTED))

    # Core Router R3
    f.append(rect(470, 230, 130, 60, fill="#fff7e6", stroke=MUTED, sw=1.6, rx=6))
    f.append(text(535, 255, "Роутер R3 (Core)", size=12, bold=True))
    f.append(text(535, 275, "10.0.0.3 (iBGP)", size=10, color=MUTED))

    # Boundary Router R4
    f.append(rect(630, 140, 130, 60, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(695, 165, "Роутер R4 (Edge)", size=12, bold=True, color=FIELD))
    f.append(text(695, 185, "203.0.113.1", size=10, color=MUTED))

    # eBGP Link R1 <-> R2
    f.append(arrow(190, 170, 310, 170, color=POS, sw=2))
    f.append(arrow(310, 170, 190, 170, color=POS, sw=2))
    f.append(text(250, 155, "eBGP сесія", size=11, color=POS, bold=True))
    f.append(text(250, 195, "TTL = 1", size=10, color=POS))

    # iBGP Sessions inside AS 64501
    f.append(line(440, 170, 630, 170, color=NEG, sw=1.8, dash="4,4"))
    f.append(text(535, 155, "iBGP Full-Mesh сесія", size=11, color=NEG, bold=True))

    f.append(line(375, 200, 470, 240, color=NEG, sw=1.4, dash="4,4"))
    f.append(line(695, 200, 600, 240, color=NEG, sw=1.4, dash="4,4"))

    # Comparison panel below
    f.append(fitbox(30, 340, 365, 100,
                    "Правила eBGP (між різними AS):\n"
                    "- Змінює NEXT_HOP на власну IP інтерфейсу.\n"
                    "- Дописує власний ASN на початок AS_PATH.\n"
                    "- Типово TTL=1 (прямий L2-лінк між шлюзами).",
                    size=11, fill="#fdf2f2", stroke=POS, sw=1.2, color=INK))

    f.append(fitbox(425, 340, 365, 100,
                    "Правила iBGP (всередині однієї AS):\n"
                    "- Зберігає початковий NEXT_HOP (потрібен next-hop-self).\n"
                    "- Не змінює AS_PATH і не додає свій ASN.\n"
                    "- Split Horizon: не передає iBGP маршрут іншим iBGP-пірам.",
                    size=11, fill="#edf4ff", stroke=NEG, sw=1.2, color=INK))

    render(os.path.join(IMG, "ebgp-ibgp-topology.svg"), W, H, *f)


# 2. Classification of BGP path attributes
def fig_bgp_attributes_classification():
    W, H = 820, 440
    f = [text(W / 2, 28, "Класифікація атрибутів шляху BGP (Path Attributes)", size=15, bold=True)]

    # Byte Flags layout
    f.append(text(W / 2, 58, "Байт прапорців атрибута (Attribute Flags Byte)", size=12, color=MUTED, bold=True))
    f.append(rect(110, 72, 600, 40, fill=FILL, stroke=LINE, sw=1.5, rx=4))

    # Flag bits
    # Bit 0: Optional (1) / Well-Known (0)
    f.append(rect(110, 72, 150, 40, fill="#eef3ff", stroke=NEG, sw=1.2, rx=0))
    f.append(text(185, 88, "Bit 0: Optional", size=11, bold=True, color=NEG))
    f.append(text(185, 104, "0: Well-Known, 1: Optional", size=9, color=MUTED))

    # Bit 1: Transitive (1) / Non-Transitive (0)
    f.append(rect(260, 72, 150, 40, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=0))
    f.append(text(335, 88, "Bit 1: Transitive", size=11, bold=True, color=FIELD))
    f.append(text(335, 104, "1: Transitive, 0: Non-Trans", size=9, color=MUTED))

    # Bit 2: Partial
    f.append(rect(410, 72, 150, 40, fill="#fff7e6", stroke=MUTED, sw=1.2, rx=0))
    f.append(text(485, 88, "Bit 2: Partial", size=11, bold=True))
    f.append(text(485, 104, "1: Неповний / транзит", size=9, color=MUTED))

    # Bit 3: Extended Length
    f.append(rect(560, 72, 150, 40, fill=FILL, stroke=LINE, sw=1.2, rx=0))
    f.append(text(635, 88, "Bit 3: Ext. Length", size=11, bold=True))
    f.append(text(635, 104, "0: 1 байт, 1: 2 байти", size=9, color=MUTED))

    # 4 Quadrants of Attributes
    # Quadrant 1: Well-Known Mandatory
    f.append(rect(30, 135, 365, 135, fill="#eef3ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(212, 158, "Well-Known Mandatory (Обов'язкові)", size=12, bold=True, color=NEG))
    f.append(text(212, 178, "Мусять розпізнаватися й бути в кожному UPDATE", size=10, color=MUTED))
    f.append(line(45, 188, 380, 188, color=NEG, sw=1, dash="2,2"))
    f.append(text(60, 210, "- ORIGIN (код 1): джерело маршруту (IGP, EGP, INCOMPLETE)", size=10, anchor="start"))
    f.append(text(60, 230, "- AS_PATH (код 2): послідовність автономних систем", size=10, anchor="start"))
    f.append(text(60, 250, "- NEXT_HOP (код 3): IP-адреса наступного шлюзу", size=10, anchor="start"))

    # Quadrant 2: Well-Known Discretionary
    f.append(rect(425, 135, 365, 135, fill="#edf4ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(607, 158, "Well-Known Discretionary (Дискреційні)", size=12, bold=True, color=NEG))
    f.append(text(607, 178, "Розпізнаються всіма, але присутні за потреби", size=10, color=MUTED))
    f.append(line(440, 188, 775, 188, color=NEG, sw=1, dash="2,2"))
    f.append(text(450, 215, "- LOCAL_PREF (код 5): пріоритет виходу з AS (в iBGP)", size=10, anchor="start"))
    f.append(text(450, 240, "- ATOMIC_AGGREGATE (код 6): позначка агрегованого шляху", size=10, anchor="start"))

    # Quadrant 3: Optional Transitive
    f.append(rect(30, 285, 365, 135, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(212, 308, "Optional Transitive (Опційні транзитивні)", size=12, bold=True, color=FIELD))
    f.append(text(212, 328, "Передаються сусіднім AS, навіть якщо не підтримуються", size=10, color=MUTED))
    f.append(line(45, 338, 380, 338, color=FIELD, sw=1, dash="2,2"))
    f.append(text(60, 360, "- AGGREGATOR (код 7): IP та ASN маршрутизатора агрегації", size=10, anchor="start"))
    f.append(text(60, 380, "- COMMUNITY (код 8): числові теги політики (32 біти)", size=10, anchor="start"))
    f.append(text(60, 400, "- LARGE_COMMUNITY (код 32): розширені теги (96 бітів)", size=10, anchor="start"))

    # Quadrant 4: Optional Non-Transitive
    f.append(rect(425, 285, 365, 135, fill="#fff7e6", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(607, 308, "Optional Non-Transitive (Опційні нетранзитивні)", size=12, bold=True))
    f.append(text(607, 328, "Не підтримуються -> видаляються при передачі далі", size=10, color=MUTED))
    f.append(line(440, 338, 775, 338, color=MUTED, sw=1, dash="2,2"))
    f.append(text(450, 360, "- MED (код 4): Multi-Exit Discriminator (метрика до сусіда)", size=10, anchor="start"))
    f.append(text(450, 380, "- ORIGINATOR_ID (код 9): захист від петель Route Reflector", size=10, anchor="start"))
    f.append(text(450, 400, "- CLUSTER_LIST (код 10): послідовність кластерів RR", size=10, anchor="start"))

    render(os.path.join(IMG, "bgp-attributes-classification.svg"), W, H, *f)


# 3. Flow of BGP Best Path Selection
def fig_bgp_best_path_flow():
    W, H = 820, 520
    f = [text(W / 2, 26, "Алгоритм вибору найкращого маршруту BGP (Best Path Decision Engine)", size=15, bold=True)]

    steps = [
        ("0. Перевірка досяжності NEXT_HOP", "Чи є маршрут до Next-Hop в IGP/RIB? Якщо ні -> шлях відкидається", "#fdf2f2", POS),
        ("1. Найвищий LOCAL_PREF", "Порівнює локальний пріоритет виходу з AS (типово 100). Більше -> краще", "#eef3ff", NEG),
        ("2. Локально згенерований маршрут", "Власний префікс (network / redistribute / aggregate) переважає отриманий", "#f8fafc", LINE),
        ("3. Найкоротший AS_PATH", "Найменша кількість ASN у послідовності AS_SEQUENCE (без prepending)", "#eafaf0", FIELD),
        ("4. Найнижчий код ORIGIN", "Порядок пріоритету: IGP (0) < EGP (1) < INCOMPLETE (2)", "#fff7e6", MUTED),
        ("5. Найменший MED", "Дискримінатор виходу між шляхами від однієї й тієї самої сусідньої AS", "#fff7e6", MUTED),
        ("6. eBGP перед iBGP", "Зовнішній маршрут eBGP завжди переважає внутрішній маршрут iBGP", "#eef3ff", NEG),
        ("7. Найменша метрика IGP до NEXT_HOP", "Гаряча картопля (Hot Potato Routing): якнайшвидший вихід із власної AS", "#eafaf0", FIELD),
        ("8. Тайбрейкери детермінізму", "Найстаріший eBGP -> Найменший BGP Router ID -> Найменша IP піра", "#f8fafc", LINE),
    ]

    x, y, w, h = 120, 52, 580, 42
    for i, (title, desc, fill_col, stroke_col) in enumerate(steps):
        f.append(rect(x, y, w, h, fill=fill_col, stroke=stroke_col, sw=1.4, rx=6))
        f.append(text(x + 15, y + 18, title, size=11, bold=True, color=stroke_col, anchor="start"))
        f.append(text(x + 15, y + 34, desc, size=9.5, color=INK, anchor="start"))

        if i < len(steps) - 1:
            f.append(arrow(x + w / 2, y + h, x + w / 2, y + h + 8, color=LINE, sw=1.4))
            y += h + 8

    render(os.path.join(IMG, "bgp-best-path-flow.svg"), W, H, *f)


if __name__ == '__main__':
    fig_ebgp_ibgp_topology()
    fig_bgp_attributes_classification()
    fig_bgp_best_path_flow()
    print('All figures generated successfully.')


