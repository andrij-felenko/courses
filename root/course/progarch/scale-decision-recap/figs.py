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

def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    points_str = ' '.join('%.1f,%.1f' % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (points_str, color, sw, d)

def fig_scaling_decision_tree():
    """Дерево прийняття рішень щодо доцільності та стратегії масштабування."""
    W, H = 1040, 520
    f = []

    # Заголовок
    f.append(fitbox(40, 30, 960, 42, "Алгоритм діагностики: Дерево рішень щодо масштабування",
                    size=15, bold=True, fill=BLUE_T, stroke=NEG))

    # Корінь
    f.append(fitbox(370, 95, 300, 48, "1. Виявлено деградацію latency / SLO\nАбо прогнозується зростання навантаження",
                    size=12, bold=True, fill=NEUT, stroke=LINE))

    f.append(arrow(520, 143, 520, 175, color=LINE, sw=2))

    # Перевірка 1: Профілювання
    f.append(fitbox(340, 175, 360, 48, "Питання A: Профілювання показує N+1 запити,\nвідсутність індексів чи витоки пам'яті?",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка Так -> Профілювання
    f.append(arrow(340, 199, 170, 199, color=POS, sw=2))
    f.append(text(250, 190, "ТАК", size=11, color=POS, bold=True))
    f.append(fitbox(40, 175, 230, 48, "Важіль 1: Оптимізація коду/SQL\nВиграш 10x-100x · 0$ витрат",
                    size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Гілка Ні -> Крок 2
    f.append(arrow(520, 223, 520, 255, color=LINE, sw=2))
    f.append(text(535, 240, "НІ", size=11, color=MUTED, bold=True))

    # Перевірка 2: Read vs Write
    f.append(fitbox(340, 255, 360, 48, "Питання B: Трафік є переважно читанням\n(Read/Write > 80/20) та допускає кешування?",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка Так -> Кешування
    f.append(arrow(700, 279, 870, 279, color=POS, sw=2))
    f.append(text(785, 270, "ТАК", size=11, color=POS, bold=True))
    f.append(fitbox(770, 255, 230, 48, "Важіль 2: Кешування / Read Replicas\nЗняття читання з головної БД",
                    size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Гілка Ні -> Крок 3
    f.append(arrow(520, 303, 520, 335, color=LINE, sw=2))
    f.append(text(535, 320, "НІ", size=11, color=MUTED, bold=True))

    # Перевірка 3: Стеля одного вузла
    f.append(fitbox(340, 335, 360, 48, "Питання C: Є запас вертикального масштабу\n(CPU < 128 cores, RAM < 1TB, NVMe IOPS)?",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка Так -> Scale Up
    f.append(arrow(340, 359, 170, 359, color=POS, sw=2))
    f.append(text(250, 350, "ТАК", size=11, color=POS, bold=True))
    f.append(fitbox(40, 335, 230, 48, "Важіль 3: Vertical Scale-Up\nОновлення сервера (CPU/RAM/NVMe)",
                    size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Гілка Ні -> Крок 4
    f.append(arrow(520, 383, 520, 415, color=LINE, sw=2))
    f.append(text(535, 400, "НІ", size=11, color=MUTED, bold=True))

    # Фінал -> Scale Out / Sharding / Cells
    f.append(fitbox(290, 415, 460, 52, "Важелі 4–6: Horizontal Scale-Out & Architecture Split\nШардинг даних по Tenant ID / Комірки (Cells) / Мультирегіон\n⚠️ Дорого: вимагає розподіленої консистентності й SRE-команди",
                    size=12, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'scaling-decision-tree.svg'), W, H, *f,
           title="Системне дерево рішень щодо вибору стратегії масштабування")


def fig_scaling_levers_ladder():
    """Порядок застосування важелів продуктивності та їхній ефективний виграш."""
    W, H = 1020, 440
    f = []

    f.append(fitbox(40, 30, 940, 42, "Ієрархія важелів масштабування: від найдешевших до найдорожчих",
                    size=15, bold=True, fill=BLUE_T, stroke=NEG))

    levers = [
        ("1. Оптимізація коду та SQL", "Усунення N+1, пропущені індекси, алгоритми", "10x – 100x", GREEN_T, FIELD),
        ("2. Кешування та читальні репліки", "Redis/Memcached, L2 кеш, Read-Replicas, CDN", "5x – 50x", GREEN_T, FIELD),
        ("3. Асинхронність та буферизація", "Черги фонових задач, батчинг записів WAL", "3x – 10x", GREEN_T, FIELD),
        ("4. Вертикальне розширення (Scale-Up)", "Більше CPU/RAM/NVMe IOPS на один сервер", "2x – 8x", AMBER_T, AMBER),
        ("5. Шардинг та партиціонування", "Горизонтальний розпил БД за Tenant/Hash ключем", "Лінійне N-х", RED_T, POS),
        ("6. Мультирегіон та Комірки (Cells)", "Ізольовані штампи інфраструктури по світу", "Гео-масштаб", RED_T, POS),
    ]

    y_start = 90
    step = 54
    for i, (title_str, desc_str, gain_str, bg_col, stroke_col) in enumerate(levers):
        y = y_start + i * step
        # Номер і назва важеля
        f.append(fitbox(40, y, 320, 44, title_str, size=13, bold=True, fill=bg_col, stroke=stroke_col))
        # Опис механізму
        f.append(fitbox(380, y, 420, 44, desc_str, size=12, fill=NEUT, stroke="#b8bfc8"))
        # Виграш / Складність
        f.append(fitbox(820, y, 160, 44, "Виграш: " + gain_str, size=12, bold=True, fill=bg_col, stroke=stroke_col))

    render(os.path.join(OUT, 'scaling-levers-ladder.svg'), W, H, *f,
           title="Порядок застосування важелів продуктивності та їхній ефективний виграш")


def fig_cost_complexity_tradeoff():
    """Залежність сукупної вартості володіння TCO від архітектурної складності та навантаження."""
    W, H = 1020, 450
    f = []

    # Шкала TCO проти RPS
    f.append(fitbox(40, 25, 940, 42, "Порівняння TCO: Моноліт / Vertical Scale vs Мікросервіси / Distributed Scale",
                    size=15, bold=True, fill=BLUE_T, stroke=NEG))

    # Осі координат
    f.append(line(80, 390, 960, 390, color=LINE, sw=2))
    f.append(line(80, 90, 80, 390, color=LINE, sw=2))

    # Позначки осі X (RPS)
    f.append(text(80, 412, "0", size=11, color=MUTED, anchor="middle"))
    f.append(text(300, 412, "10k RPS", size=11, color=MUTED, anchor="middle"))
    f.append(text(520, 412, "50k RPS", size=11, color=MUTED, anchor="middle"))
    f.append(text(740, 412, "200k RPS", size=11, color=MUTED, anchor="middle"))
    f.append(text(950, 412, "1M RPS", size=11, color=MUTED, anchor="middle"))
    f.append(text(520, 435, "Навантаження системи (Requests Per Second)", size=12, color=INK, bold=True, anchor="middle"))

    # Позначки осі Y (TCO $)
    f.append(text(70, 100, "$100k/mo", size=11, color=MUTED, anchor="end"))
    f.append(text(70, 240, "$20k/mo", size=11, color=MUTED, anchor="end"))
    f.append(text(70, 380, "$1k/mo", size=11, color=MUTED, anchor="end"))
    f.append(text(35, 240, "TCO (Специфікація + SRE / Зарплати)", size=12, color=INK, bold=True, anchor="middle"))

    # Крива 1: Scale-Up / Моноліт (Зелена)
    # Починається низько, зростає повільно, біля 100k вертикальна стеля
    f.append(polyline([(80, 380), (300, 370), (520, 350), (680, 310), (740, 180), (760, 100)],
                      color=FIELD, sw=3))
    f.append(fitbox(450, 310, 210, 32, "Scale-Up / Потужний вузол\n(Низькі витрати до 100k RPS)",
                    size=11, fill=GREEN_T, stroke=FIELD, color=FIELD, bold=True))

    # Крива 2: Microservices / Distributed (Червона)
    # Високий старт (Kubernetes, Kafka, Mesh, DevOps salaries), але плаский кут на ультра-масштабі
    f.append(polyline([(80, 240), (300, 235), (520, 220), (740, 190), (950, 130)],
                      color=POS, sw=3, dash="6 3"))
    f.append(fitbox(200, 175, 230, 42, "Мікросервіси / Distributed Scale\n(Висока фіксована ціна інфраструктури + SRE)",
                    size=11, fill=RED_T, stroke=POS, color=POS, bold=True))

    # Зона передчасного масштабування (Over-Engineering Gap)
    f.append(rect(120, 255, 340, 105, fill=AMBER_T, stroke=AMBER, sw=1.5, rx=6))
    f.append(mtext(290, 275, ["Зона передчасного овер-інжинірингу:",
                              "Витрати на мікросервіси в 5-10 разів вищі,",
                              "ніж реальна потреба системи"],
                   size=11, color=INK, bold=True))

    render(os.path.join(OUT, 'cost-complexity-tradeoff.svg'), W, H, *f,
           title="Залежність сукупної вартості володіння TCO від архітектурної складності та навантаження")


if __name__ == '__main__':
    fig_scaling_decision_tree()
    fig_scaling_levers_ladder()
    fig_cost_complexity_tradeoff()
    print("Figures generated successfully.")
