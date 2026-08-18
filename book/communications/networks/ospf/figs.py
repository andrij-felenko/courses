# -*- coding: utf-8 -*-
"""Фігури до теми «OSPF: протокол стану каналів».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Концепція Link-State: розсилка LSA та побудова карти LSDB ─────────────
def fig_link_state_concept():
    W, H = 840, 430
    frags = [
        text(W / 2, 28, "Принцип Link-State: лавинна розсилка LSA та ідентична база LSDB", size=16, bold=True),

        # Left panel: Distance Vector
        rect(30, 55, 360, 310, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8),
        text(210, 80, "Дистанційно-векторний підхід (RIP)", size=13, bold=True, color=POS),
        text(210, 100, "«Маршрутизація з чужих слів» (Routing by Rumor)", size=10.5, color=MUTED, italic=True),

        # Routers in Distance Vector
        circle(90, 160, 24, fill="#ffffff", stroke=POS, sw=1.8),
        text(90, 165, "R1", size=12, bold=True),

        circle(210, 160, 24, fill="#ffffff", stroke=POS, sw=1.8),
        text(210, 165, "R2", size=12, bold=True),

        circle(330, 160, 24, fill="#ffffff", stroke=POS, sw=1.8),
        text(330, 165, "R3", size=12, bold=True),

        arrow(115, 150, 185, 150, color=POS, sw=1.6),
        arrow(185, 170, 115, 170, color=POS, sw=1.6),
        arrow(235, 150, 305, 150, color=POS, sw=1.6),
        arrow(305, 170, 235, 170, color=POS, sw=1.6),

        text(150, 138, "Таблиця R1", size=9.5, color=POS),
        text(270, 138, "Таблиця R2", size=9.5, color=POS),

        fitbox(45, 215, 330, 135,
               "• Роутер передає лише готові вектори (дистанції) сусідам.\n"
               "• Немає карти топології: вузол знає лише куди віддати пакет.\n"
               "• Повільна збіжність, небезпека зациклення (Count to Infinity).\n"
               "• Метрика — кількість хопів (без урахування швидкості лінії).",
               size=11, fill="#ffffff", stroke=LINE, sw=1),

        # Right panel: Link-State
        rect(430, 55, 380, 310, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8),
        text(620, 80, "Підхід стану каналів (OSPF Link-State)", size=13, bold=True, color=FIELD),
        text(620, 100, "Кожен вузол має повну топологічну карту мережі", size=10.5, color=MUTED, italic=True),

        # Routers in Link-State
        circle(490, 145, 22, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(490, 150, "R1", size=11, bold=True),

        circle(620, 135, 22, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(620, 140, "R2", size=11, bold=True),

        circle(750, 145, 22, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(750, 150, "R3", size=11, bold=True),

        circle(550, 205, 20, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(550, 210, "R4", size=11, bold=True),

        circle(690, 205, 20, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(690, 210, "R5", size=11, bold=True),

        # Links
        line(512, 145, 598, 137, color=FIELD, sw=1.5),
        line(642, 137, 728, 145, color=FIELD, sw=1.5),
        line(504, 162, 536, 192, color=FIELD, sw=1.5),
        line(620, 157, 564, 192, color=FIELD, sw=1.5),
        line(620, 157, 676, 192, color=FIELD, sw=1.5),
        line(736, 162, 704, 192, color=FIELD, sw=1.5),
        line(570, 205, 670, 205, color=FIELD, sw=1.5),

        fitbox(445, 240, 350, 110,
               "1. Кожен роутер анонсує стан своїх лінків (LSA).\n"
               "2. LSA розливаються лавиною (Flooding) по всій зоні.\n"
               "3. Усі вузли формують ідентичну базу стану каналів (LSDB).\n"
               "4. Кожен запускає SPF (Дейкстру) і будує власне дерево шляхів.",
               size=10.5, fill="#ffffff", stroke=LINE, sw=1),

        # Bottom summary box
        fitbox(30, 375, 780, 42,
               "OSPF гарантує відсутність петель усередині зони: математично неможливо створити петлю,\n"
               "коли кожен пристрій обчислює найкоротший шлях на єдиному глобальному графі топології.",
               size=10.5, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-ospf-link-state-concept.svg"), W, H, *frags)


# ── 2. Скінченний автомат сусідства (FSM Adjacency) ──────────────────────────
def fig_adjacency_fsm():
    W, H = 840, 460
    frags = [
        text(W / 2, 26, "Скінченний автомат станів сусідства OSPF (Neighbor FSM)", size=16, bold=True),

        # States vertical chain
        rect(50, 55, 160, 42, fill="#f5f5f5", stroke=MUTED, sw=1.5, rx=6),
        text(130, 80, "1. Down", size=13, bold=True),

        rect(50, 115, 160, 42, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6),
        text(130, 140, "2. Init", size=13, bold=True, color=NEG),

        rect(50, 175, 160, 42, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6),
        text(130, 200, "3. 2-Way", size=13, bold=True, color=FIELD),

        rect(50, 235, 160, 42, fill="#fff7e6", stroke=MUTED, sw=1.5, rx=6),
        text(130, 260, "4. ExStart", size=13, bold=True),

        rect(50, 295, 160, 42, fill="#fff7e6", stroke=MUTED, sw=1.5, rx=6),
        text(130, 320, "5. Exchange", size=13, bold=True),

        rect(50, 355, 160, 42, fill="#fff7e6", stroke=MUTED, sw=1.5, rx=6),
        text(130, 380, "6. Loading", size=13, bold=True),

        rect(50, 410, 160, 42, fill="#eafaf0", stroke=FIELD, sw=2, rx=6),
        text(130, 435, "7. Full", size=14, bold=True, color=FIELD),

        # Arrows between states
        arrow(130, 97, 130, 115, color=LINE, sw=1.6),
        arrow(130, 157, 130, 175, color=LINE, sw=1.6),
        arrow(130, 217, 130, 235, color=LINE, sw=1.6),
        arrow(130, 277, 130, 295, color=LINE, sw=1.6),
        arrow(130, 337, 130, 355, color=LINE, sw=1.6),
        arrow(130, 397, 130, 410, color=LINE, sw=1.6),

        # Explanations and packet exchanges on the right
        rect(230, 60, 580, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=6),
        text(245, 80, "Відправка Hello: отримано перший Hello без нашого Router ID у списку сусідів.", size=10.5, anchor="start"),
        text(245, 96, "Пакет: Hello (тип 1) на мультикаст 224.0.0.5 (AllSPFRouters)", size=10, anchor="start", color=MUTED),

        rect(230, 116, 580, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=6),
        text(245, 136, "Двосторонній зв'язок: отримано Hello, де наш Router ID є в списку сусідів.", size=10.5, anchor="start"),
        text(245, 152, "У широкомовних мережах на цьому етапі обираються DR та BDR.", size=10, anchor="start", color=MUTED),

        rect(230, 172, 580, 52, fill="#fdf7f7", stroke=POS, sw=1.2, rx=6),
        text(245, 192, "⚠️ Увага: між двома DROther-роутерами стан залишається 2-Way назавжди!", size=10.5, anchor="start", color=POS, bold=True),
        text(245, 210, "Повне сусідство (Full) встановлюється виключно з DR та BDR.", size=10, anchor="start", color=MUTED),

        rect(230, 232, 580, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=6),
        text(245, 252, "Початок обміну: визначення Master/Slave та стартового Sequence Number.", size=10.5, anchor="start"),
        text(245, 268, "Пакет: порожні DBD з прапорцями I=1 (Init), M=1 (More), MS=1 (Master).", size=10, anchor="start", color=MUTED),

        rect(230, 290, 580, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=6),
        text(245, 310, "Обмін описами баз: передача заголовків усіх відомих LSA.", size=10.5, anchor="start"),
        text(245, 326, "Пакет: DBD (Database Description, тип 2), порівняння версій за Sequence Number.", size=10, anchor="start", color=MUTED),

        rect(230, 348, 580, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=6),
        text(245, 368, "Запит та передача повних LSA: вивантаження відсутніх або новіших записів.", size=10.5, anchor="start"),
        text(245, 384, "Пакети: LSR (тип 3 запит) → LSU (тип 4 оновлення) → LSAck (тип 5 квитанція).", size=10, anchor="start", color=MUTED),

        rect(230, 406, 580, 46, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6),
        text(245, 426, "Повна синхронізація: бази LSDB маршрутизаторів стовідсотково ідентичні.", size=11, anchor="start", bold=True, color=FIELD),
        text(245, 442, "Маршрутизатор запускає SPF і записує найкращі маршрути в таблицю IP (FIB).", size=10, anchor="start", color=MUTED)
    ]
    render(os.path.join(IMG, "fig-ospf-adjacency-fsm.svg"), W, H, *frags)


# ── 3. Оптимізація DR/BDR у широкомовних мережах ─────────────────────────────
def fig_dr_bdr():
    W, H = 840, 420
    frags = [
        text(W / 2, 28, "Оптимізація широкомовного сегмента: вибір DR/BDR", size=16, bold=True),

        # Left: Without DR (Full Mesh explosion)
        rect(30, 55, 370, 300, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8),
        text(215, 80, "Без DR/BDR (Повна сітка)", size=13, bold=True, color=POS),
        text(215, 98, "Кількість зв'язків: N · (N − 1) / 2", size=11, color=MUTED, bold=True),

        # Routers in full mesh (5 routers: 10 links)
        line(215, 140, 295, 190, color=POS, sw=1.2),
        line(215, 140, 265, 270, color=POS, sw=1.2),
        line(215, 140, 165, 270, color=POS, sw=1.2),
        line(215, 140, 135, 190, color=POS, sw=1.2),
        line(295, 190, 265, 270, color=POS, sw=1.2),
        line(295, 190, 165, 270, color=POS, sw=1.2),
        line(295, 190, 135, 190, color=POS, sw=1.2),
        line(265, 270, 165, 270, color=POS, sw=1.2),
        line(265, 270, 135, 190, color=POS, sw=1.2),
        line(165, 270, 135, 190, color=POS, sw=1.2),

        circle(215, 140, 18, fill="#ffffff", stroke=POS, sw=1.8),
        text(215, 145, "R1", size=10, bold=True),

        circle(295, 190, 18, fill="#ffffff", stroke=POS, sw=1.8),
        text(295, 195, "R2", size=10, bold=True),

        circle(265, 270, 18, fill="#ffffff", stroke=POS, sw=1.8),
        text(265, 275, "R3", size=10, bold=True),

        circle(165, 270, 18, fill="#ffffff", stroke=POS, sw=1.8),
        text(165, 275, "R4", size=10, bold=True),

        circle(135, 190, 18, fill="#ffffff", stroke=POS, sw=1.8),
        text(135, 195, "R5", size=10, bold=True),

        fitbox(45, 305, 340, 42,
               "Для N = 5: 10 сусідств.\n"
               "Для N = 50: 1 225 сусідств (лавинний шторм синхронізацій).",
               size=10, fill="#ffffff", stroke=LINE, sw=1),

        # Right: With DR / BDR
        rect(430, 55, 380, 300, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8),
        text(620, 80, "З виділеними DR та BDR (Зіркова схема)", size=13, bold=True, color=FIELD),
        text(620, 98, "Кількість сусідств зменшується до 2N − 3", size=11, color=MUTED, bold=True),

        # DR and BDR at top
        rect(500, 125, 90, 45, fill="#eafaf0", stroke=FIELD, sw=2, rx=6),
        text(545, 145, "DR", size=13, bold=True, color=FIELD),
        text(545, 160, "224.0.0.6", size=9, color=MUTED),

        rect(640, 125, 90, 45, fill="#eef3ff", stroke=NEG, sw=2, rx=6),
        text(685, 145, "BDR", size=13, bold=True, color=NEG),
        text(685, 160, "224.0.0.6", size=9, color=MUTED),

        # DROther routers at bottom
        circle(480, 240, 20, fill="#ffffff", stroke=LINE, sw=1.5),
        text(480, 245, "R3", size=10, bold=True),
        text(480, 272, "DROther", size=10, color=MUTED),

        circle(615, 240, 20, fill="#ffffff", stroke=LINE, sw=1.5),
        text(615, 245, "R4", size=10, bold=True),
        text(615, 272, "DROther", size=10, color=MUTED),

        circle(750, 240, 20, fill="#ffffff", stroke=LINE, sw=1.5),
        text(750, 245, "R5", size=10, bold=True),
        text(750, 272, "DROther", size=10, color=MUTED),

        # Links from DROthers to DR and BDR
        line(480, 220, 530, 170, color=FIELD, sw=1.5),
        line(480, 220, 660, 170, color=NEG, sw=1.2, dash="3,3"),

        line(615, 220, 555, 170, color=FIELD, sw=1.5),
        line(615, 220, 675, 170, color=NEG, sw=1.2, dash="3,3"),

        line(750, 220, 580, 170, color=FIELD, sw=1.5),
        line(750, 220, 700, 170, color=NEG, sw=1.2, dash="3,3"),

        # Dashed line between DROthers (2-Way state)
        line(500, 240, 595, 240, color=MUTED, sw=1.2, dash="4,4"),
        line(635, 240, 730, 240, color=MUTED, sw=1.2, dash="4,4"),
        text(547, 230, "2-Way", size=9, color=MUTED, italic=True),
        text(682, 230, "2-Way", size=9, color=MUTED, italic=True),

        fitbox(445, 295, 350, 52,
               "• DROther шлють оновлення до DR/BDR на адресу 224.0.0.6.\n"
               "• DR розсилає оновлення всім маршрутизаторам на 224.0.0.5.\n"
               "• BDR пасивно слухає і миттєво підхоплює роль у разі відмови DR.",
               size=9.5, fill="#ffffff", stroke=LINE, sw=1),

        # Bottom info
        fitbox(30, 368, 780, 42,
               "Алгоритм вибору DR/BDR: 1) Найвищий пріоритет інтерфейсу (Router Priority, 0..255; 0 — ніколи не стає DR).\n"
               "2) За однакового пріоритету перемагає найбільший Router ID. Вибір є непереривним (Non-preemptive).",
               size=10.5, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-ospf-dr-bdr.svg"), W, H, *frags)


# ── 4. Ієрархія зон (Area Hierarchy) та типи LSA ─────────────────────────────
def fig_area_hierarchy():
    W, H = 840, 440
    frags = [
        text(W / 2, 26, "Ієрархія зон OSPF, типи маршрутизаторів та розподіл LSA", size=16, bold=True),

        # Central Backbone Area 0
        rect(260, 55, 320, 160, fill="#eef3ff", stroke=NEG, sw=2, rx=10),
        text(420, 80, "Backbone Area 0 (0.0.0.0)", size=14, bold=True, color=NEG),
        text(420, 98, "Центральна транзитна зона", size=10.5, color=MUTED),

        # Backbone routers
        circle(350, 150, 22, fill="#ffffff", stroke=NEG, sw=1.8),
        text(350, 155, "ABR 1", size=10, bold=True),

        circle(490, 150, 22, fill="#ffffff", stroke=NEG, sw=1.8),
        text(490, 155, "ABR 2", size=10, bold=True),

        line(372, 150, 468, 150, color=NEG, sw=1.8),
        text(420, 140, "Type 1, 2, 3", size=9, color=NEG),

        # Left: Standard Area 1
        rect(30, 235, 230, 140, fill="#fdfbf4", stroke=MUTED, sw=1.5, rx=8),
        text(145, 258, "Standard Area 1", size=12, bold=True),
        text(145, 274, "Повна інформація", size=10, color=MUTED),

        circle(80, 325, 18, fill="#ffffff", stroke=LINE, sw=1.5),
        text(80, 330, "R1", size=10, bold=True),

        circle(180, 325, 18, fill="#ffffff", stroke=LINE, sw=1.5),
        text(180, 330, "R2", size=10, bold=True),

        line(98, 325, 162, 325, color=LINE, sw=1.4),
        line(180, 307, 335, 165, color=LINE, sw=1.5),
        text(145, 360, "LSA: Type 1, 2, 3, 4, 5", size=9.5, color=INK, bold=True),

        # Middle: Stub / Totally Stubby Area 2
        rect(305, 235, 230, 140, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8),
        text(420, 258, "Stub / Totally Stubby 2", size=12, bold=True, color=POS),
        text(420, 274, "Без зовнішніх LSA", size=10, color=MUTED),

        circle(370, 325, 18, fill="#ffffff", stroke=LINE, sw=1.5),
        text(370, 330, "R3", size=10, bold=True),

        circle(470, 325, 18, fill="#ffffff", stroke=LINE, sw=1.5),
        text(470, 330, "R4", size=10, bold=True),

        line(388, 325, 452, 325, color=LINE, sw=1.4),
        line(370, 307, 350, 172, color=LINE, sw=1.5),
        line(470, 307, 490, 172, color=LINE, sw=1.5),
        text(420, 360, "Stub: LSA 1, 2, 3 + Default\nTotally: LSA 1, 2 + Def 3", size=9, color=POS, bold=True),

        # Right: NSSA Area 3 + External AS
        rect(580, 235, 230, 140, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8),
        text(695, 258, "NSSA Area 3", size=12, bold=True, color=FIELD),
        text(695, 274, "Дозволено власний ASBR", size=10, color=MUTED),

        circle(640, 325, 18, fill="#ffffff", stroke=FIELD, sw=1.8),
        text(640, 330, "ASBR", size=9.5, bold=True, color=FIELD),

        rect(710, 310, 85, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(752, 328, "RIP / BGP", size=9, bold=True),

        line(658, 325, 710, 325, color=FIELD, sw=1.6),
        line(640, 307, 505, 168, color=FIELD, sw=1.5),
        text(695, 360, "LSA Type 7 → на ABR у Type 5", size=9, color=FIELD, bold=True),

        # Bottom summary box
        fitbox(30, 385, 780, 48,
               "• ABR (Area Border Router) — з'єднує звичайну зону з магістральною Area 0 і генерує LSA Type 3.\n"
               "• ASBR (Autonomous System Boundary Router) — імпортує зовнішні маршрути (LSA Type 5 або Type 7).\n"
               "• Зони ізолюють лавинну розсилку LSA: топологічні зміни в одній зоні не змушують перераховувати SPF у сусідніх.",
               size=10, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-ospf-area-hierarchy.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_link_state_concept()
    fig_adjacency_fsm()
    fig_dr_bdr()
    fig_area_hierarchy()
    print("All figures generated successfully.")
