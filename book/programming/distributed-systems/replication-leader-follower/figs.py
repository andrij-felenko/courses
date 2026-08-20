# -*- coding: utf-8 -*-
"""Фігури до теми «Лідер-фоловер / мультилідер / leaderless: три топології реплікації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # конфлікт / збій / увага
COOL = "#eaf0fd"   # лідер / координатор / запис
GOOD = "#e8f6ee"   # успіх / кворум / читання
WARN = "#fef9e7"   # тимчасовий стан / лаг / реплікація


# ── 1. Порівняння трьох фундаментальних топологій реплікації ───────────────────
def three_topologies_comparison():
    W, H = 1180, 520
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "СПЕКТР ПРАВА НА ЗАПИС: ТРИ АРХІТЕКТУРНІ ТОПОЛОГІЇ РЕПЛІКАЦІЇ ДАНИХ",
                    size=14, bold=True, fill=COOL, stroke=LINE, sw=1.5))

    col_w = 340
    gap = 40
    x_base = 40

    # ── Колонка 1: Single-Leader (Лідер-Фоловер) ──
    x1 = x_base
    f.append(fitbox(x1, 80, col_w, 400, "", fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(x1 + 10, 90, col_w - 20, 36, "1. ОДИН ЛІДЕР (Single-Leader)", size=13, bold=True, fill=COOL))

    # Клієнти
    f.append(fitbox(x1 + 25, 140, 120, 32, "Клієнт (Запис)", size=11, bold=True, fill="#fff2e6", stroke=POS))
    f.append(fitbox(x1 + 195, 140, 120, 32, "Клієнти (Читання)", size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Вузли
    f.append(fitbox(x1 + 25, 210, 120, 50, "ЛІДЕР\n(Primary)", size=12, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    f.append(fitbox(x1 + 195, 210, 120, 50, "Фоловер 1\n(Standby)", size=11, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(x1 + 195, 280, 120, 50, "Фоловер 2\n(Standby)", size=11, bold=True, fill=FILL, stroke=LINE))

    # Стрілки клієнтів
    f.append(arrow(x1 + 85, 172, x1 + 85, 208, color=POS, sw=1.8))
    f.append(arrow(x1 + 255, 172, x1 + 255, 208, color=FIELD, sw=1.5))

    # Реплікаційний потік
    f.append(arrow(x1 + 145, 225, x1 + 193, 225, color=NEG, sw=1.5))
    f.append(text(x1 + 170, 215, "WAL", size=10, color=NEG, bold=True))
    f.append(arrow(x1 + 145, 245, x1 + 193, 295, color=NEG, sw=1.5))

    # Пояснення
    f.append(fitbox(x1 + 15, 350, col_w - 30, 115,
                    "• Запис: ТІЛЬКИ через одного лідера\n"
                    "• Читання: з лідера або фоловерів\n"
                    "• Перевага: простий тотальний порядок\n"
                    "• Вузьке місце: ліміт CPU/диска лідера,\n"
                    "  складний failover при збої",
                    size=10.5, fill=FILL, stroke=MUTED))

    # ── Колонка 2: Multi-Leader (Мультилідер) ──
    x2 = x_base + col_w + gap
    f.append(fitbox(x2, 80, col_w, 400, "", fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(x2 + 10, 90, col_w - 20, 36, "2. МУЛЬТИЛІДЕР (Multi-Leader)", size=13, bold=True, fill=WARN))

    # ДЦ 1 і ДЦ 2
    f.append(fitbox(x2 + 20, 140, 135, 140, "Датацентр А (ЄС)", size=11, bold=True, fill=FILL, stroke=MUTED, dash="3,3"))
    f.append(fitbox(x2 + 30, 175, 115, 45, "Лідер A\n(Франкфурт)", size=11, bold=True, fill=COOL, stroke=NEG))
    f.append(fitbox(x2 + 30, 230, 115, 38, "Фоловер A", size=10, fill=BG, stroke=MUTED))
    f.append(arrow(x2 + 87, 220, x2 + 87, 228, color=MUTED, sw=1.2))

    x_dc2 = x2 + 185
    f.append(fitbox(x_dc2, 140, 135, 140, "Датацентр Б (США)", size=11, bold=True, fill=FILL, stroke=MUTED, dash="3,3"))
    f.append(fitbox(x_dc2 + 10, 175, 115, 45, "Лідер B\n(Вірджинія)", size=11, bold=True, fill=COOL, stroke=NEG))
    f.append(fitbox(x_dc2 + 10, 230, 115, 38, "Фоловер B", size=10, fill=BG, stroke=MUTED))
    f.append(arrow(x_dc2 + 67, 220, x_dc2 + 67, 228, color=MUTED, sw=1.2))

    # Міжлідерний асинхронний міст
    f.append(arrow(x2 + 145, 190, x_dc2 + 8, 190, color=POS, sw=1.8))
    f.append(arrow(x_dc2 + 8, 205, x2 + 145, 205, color=POS, sw=1.8))
    f.append(text(x2 + 165, 182, "WAN", size=10, color=POS, bold=True))

    # Пояснення
    f.append(fitbox(x2 + 15, 350, col_w - 30, 115,
                    "• Запис: у будь-який локальний лідер\n"
                    "• Реплікація: асинхронна між лідерами\n"
                    "• Перевага: низька затримка у мультирегіоні\n"
                    "• Головний виклик: неминучі конфлікти\n"
                    "  одночасного запису (LWW / CRDT)",
                    size=10.5, fill=FILL, stroke=MUTED))

    # ── Колонка 3: Leaderless (Безлідерна / Dynamo-style) ──
    x3 = x_base + (col_w + gap) * 2
    f.append(fitbox(x3, 80, col_w, 400, "", fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(x3 + 10, 90, col_w - 20, 36, "3. БЕЗЛІДЕРНА (Leaderless)", size=13, bold=True, fill=GOOD))

    # Координатор / Клієнт
    f.append(fitbox(x3 + 95, 140, 150, 34, "Клієнт / Координатор", size=11, bold=True, fill="#fff2e6", stroke=POS))

    # Однорангові вузли
    f.append(fitbox(x3 + 20, 210, 85, 45, "Вузол 1\n(Peer)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x3 + 125, 210, 85, 45, "Вузол 2\n(Peer)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x3 + 230, 210, 85, 45, "Вузол 3\n(Peer)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x3 + 70, 275, 85, 45, "Вузол 4\n(Peer)", size=11, bold=True, fill=FILL, stroke=MUTED))
    f.append(fitbox(x3 + 180, 275, 85, 45, "Вузол 5\n(Peer)", size=11, bold=True, fill=FILL, stroke=MUTED))

    # Паралельні стрілки запису/читання
    f.append(arrow(x3 + 130, 174, x3 + 65, 208, color=POS, sw=1.5))
    f.append(arrow(x3 + 170, 174, x3 + 167, 208, color=POS, sw=1.5))
    f.append(arrow(x3 + 210, 174, x3 + 270, 208, color=POS, sw=1.5))

    # Пояснення
    f.append(fitbox(x3 + 15, 350, col_w - 30, 115,
                    "• Запис/Читання: паралельно на N вузлів\n"
                    "• Консистентність: кворум W + R > N\n"
                    "• Перевага: найвища відмовостійкість,\n"
                    "  немає точки виборів лідера\n"
                    "• Механізми: Read Repair, Anti-Entropy",
                    size=10.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'three-topologies-comparison.svg'), W, H, *f)


# ── 2. Перетин кворумів (Pigeonhole Principle в Leaderless) ────────────────────
def quorum_intersection():
    W, H = 1050, 480
    f = []

    f.append(fitbox(40, 20, 970, 42,
                    "МАТЕМАТИКА КВОРУМУ: ЧОМУ W + R > N ГАРАНТУЄ СВІЖЕ ЧИТАННЯ",
                    size=14, bold=True, fill=COOL, stroke=LINE, sw=1.5))

    # Параметри N=5, W=3, R=3
    f.append(fitbox(60, 80, 930, 36,
                    "Конфігурація кластера: Реплікаційний фактор N = 5 | Кворум запису W = 3 | Кворум читання R = 3 (3 + 3 = 6 > 5)",
                    size=12, bold=True, fill=FILL, stroke=MUTED))

    node_w = 160
    node_h = 240
    gap = 25
    x0 = 60
    y0 = 140

    nodes = [
        ("Вузол 1", "Отримав запис v2", GOOD, True, False),
        ("Вузол 2", "Отримав запис v2", GOOD, True, False),
        ("Вузол 3", "Отримав запис v2\n+ Відповів на читання", WARM, True, True),
        ("Вузол 4", "Має старе v1\n+ Відповів на читання", COOL, False, True),
        ("Вузол 5", "Має старе v1\n(не опитувався)", FILL, False, False),
    ]

    for i, (title, desc, fill_col, in_w, in_r) in enumerate(nodes):
        x = x0 + i * (node_w + gap)

        # Рамка вузла
        f.append(fitbox(x, y0, node_w, node_h, "", fill=fill_col, stroke=LINE, sw=1.8))
        f.append(fitbox(x + 10, y0 + 10, node_w - 20, 32, title, size=13, bold=True, fill=BG))

        # Опис вмісту
        f.append(fitbox(x + 8, y0 + 55, node_w - 16, 50, desc, size=10.5, fill=BG, stroke=MUTED))

        # Бейджі належності
        y_b = y0 + 120
        if in_w:
            f.append(fitbox(x + 15, y_b, node_w - 30, 26, "∈ Кворум Запису W", size=10, bold=True, fill="#ffebe6", stroke=POS))
            y_b += 32
        if in_r:
            f.append(fitbox(x + 15, y_b, node_w - 30, 26, "∈ Кворум Читання R", size=10, bold=True, fill="#e6f4ea", stroke=FIELD))
            y_b += 32

        if i == 2: # Вузол перетину
            f.append(fitbox(x + 8, y0 + 185, node_w - 16, 42, "★ ВУЗОЛ ПЕРЕТИНУ\n(версія v2 перемагає)", size=10, bold=True, fill="#fff0b3", stroke=POS, sw=1.6))

    # Фігурні дужки / смуги підсумовування
    f.append(rect(x0, y0 + node_h + 15, 3 * node_w + 2 * gap, 24, fill="#ffebe6", stroke=POS, sw=1.4, rx=4))
    f.append(text(x0 + (3 * node_w + 2 * gap) / 2, y0 + node_h + 32, "Кворум запису W = 3 (вузли 1, 2, 3 зафіксували версію v2)", size=11, color=POS, bold=True))

    f.append(rect(x0 + 2 * (node_w + gap), y0 + node_h + 45, 2 * node_w + gap, 24, fill="#e6f4ea", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(x0 + 2 * (node_w + gap) + (2 * node_w + gap) / 2, y0 + node_h + 62, "Кворум читання R = 2 (помилка) / R = 3 (вузли 3, 4, 5)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'quorum-intersection.svg'), W, H, *f)


# ── 3. Розходження та конфлікти у Multi-Leader ────────────────────────────────
def multi_leader_conflict_divergence():
    W, H = 1100, 520
    f = []

    f.append(fitbox(40, 20, 1020, 42,
                    "АНАТОМІЯ КОНФЛІКТУ: ОДНОЧАСНІ ЗАПИСИ В МУЛЬТИЛІДЕРНІЙ СИСТЕМІ",
                    size=14, bold=True, fill=WARM, stroke=LINE, sw=1.5))

    # Часова шкала зверху вниз
    y_start = 85
    col1_x = 80
    col2_x = 600
    box_w = 420

    # Шапки лідерів
    f.append(fitbox(col1_x, y_start, box_w, 42, "Лідер 1 (Датацентр Франкфурт)", size=13, bold=True, fill=COOL, stroke=NEG, sw=1.6))
    f.append(fitbox(col2_x, y_start, box_w, 42, "Лідер 2 (Датацентр Сінгапур)", size=13, bold=True, fill=COOL, stroke=NEG, sw=1.6))

    # Стан t0: Початкове значення
    f.append(fitbox(440, y_start + 55, 220, 32, "Початковий стан: key='title', val='A'", size=11, bold=True, fill=FILL, stroke=MUTED))

    # Подія t1: Одночасні клієнтські записи
    y1 = y_start + 105
    f.append(fitbox(col1_x + 10, y1, box_w - 20, 52,
                    "t=10:00.001 | Клієнт 1 надсилає: UPDATE title='B'\nЛокальний комміт OK (миттєво)",
                    size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(col2_x + 10, y1, box_w - 20, 52,
                    "t=10:00.003 | Клієнт 2 надсилає: UPDATE title='C'\nЛокальний комміт OK (миттєво)",
                    size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Подія t2: Асинхронна трансляція через WAN (затримка 120 мс)
    y2 = y1 + 75
    f.append(arrow(col1_x + box_w - 40, y1 + 52, col2_x + 40, y2 + 50, color=POS, sw=2))
    f.append(arrow(col2_x + 40, y1 + 52, col1_x + box_w - 40, y2 + 50, color=POS, sw=2))
    f.append(fitbox(450, y2 + 10, 200, 35, "Трансляція WAN (120 мс)\nПакети летять назустріч", size=10, bold=True, fill="#fff2e6", stroke=POS))

    # Подія t3: Зіткнення мутацій та розходження
    y3 = y2 + 65
    f.append(fitbox(col1_x + 10, y3, box_w - 20, 60,
                    "Отримано зміну 'title=C' із Сінгапуру.\n"
                    "Локальне значення вже змінено на 'B'!\n"
                    "⚠ КОНФЛІКТ: порядок застосування (B -> C) ≠ (C -> B)",
                    size=10.5, bold=True, fill=WARM, stroke=POS, sw=1.6))

    f.append(fitbox(col2_x + 10, y3, box_w - 20, 60,
                    "Отримано зміну 'title=B' із Франкфурта.\n"
                    "Локальне значення вже змінено на 'C'!\n"
                    "⚠ КОНФЛІКТ: порядок застосування (C -> B) ≠ (B -> C)",
                    size=10.5, bold=True, fill=WARM, stroke=POS, sw=1.6))

    # Шляхи розв'язання конфлікту знизу
    y4 = y3 + 80
    f.append(fitbox(80, y4, 940, 75,
                    "СТРАТЕГІЇ ЗБІЖНОСТІ (CONVERGENCE):\n"
                    "1. Last-Write-Wins (LWW): Перемагає більший таймстемп (ризик: похибка годинників NTP стирає дані безслідно)\n"
                    "2. CRDT (Conflict-Free Replicated Data Types): Детерміністичне об'єднання за математичною напівґраткою (Lattice Join)\n"
                    "3. Conflict Avoidance: Маршрутизація всіх записів конкретного користувача в єдиний визначений датацентр",
                    size=10.5, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, 'multi-leader-conflict-divergence.svg'), W, H, *f)


# ── 4. Механізми відновлення: Read Repair та Hinted Handoff ───────────────────
def read_repair_and_hinted_handoff():
    W, H = 1140, 520
    f = []

    f.append(fitbox(40, 20, 1060, 42,
                    "САМОЗЦІЛЕННЯ В LEADERLESS: READ REPAIR ТА HINTED HANDOFF",
                    size=14, bold=True, fill=GOOD, stroke=LINE, sw=1.5))

    half_w = 510
    x_left = 40
    x_right = 590

    # ── Ліва половина: Read Repair ──
    f.append(fitbox(x_left, 75, half_w, 420, "", fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(x_left + 10, 85, half_w - 20, 36, "A. READ REPAIR (Відновлення під час читання)", size=12.5, bold=True, fill=GOOD))

    # Клієнт і вузли
    f.append(fitbox(x_left + 180, 135, 150, 35, "Клієнт / Координатор", size=11, bold=True, fill=COOL))

    f.append(fitbox(x_left + 25, 215, 135, 45, "Вузол 1\n(версія v3, ts=100)", size=10.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x_left + 185, 215, 135, 45, "Вузол 2\n(версія v3, ts=100)", size=10.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x_left + 345, 215, 140, 45, "Вузол 3 (Застарілий)\n(версія v2, ts=80)", size=10.5, bold=True, fill=WARM, stroke=POS))

    # Стрілки читання
    f.append(fitbox(x_left + 150, 175, 180, 24, "1. Опитування R=3 вузлів", size=10, bold=True, fill=BG, stroke=MUTED))
    f.append(arrow(x_left + 180, 195, x_left + 90, 212, color=MUTED, sw=1.3))
    f.append(arrow(x_left + 240, 199, x_left + 252, 212, color=MUTED, sw=1.3))
    f.append(arrow(x_left + 300, 195, x_left + 380, 212, color=MUTED, sw=1.3))

    # Зворотний запис Read Repair
    f.append(arrow(x_left + 345, 155, x_left + 440, 212, color=POS, sw=2))
    f.append(fitbox(x_left + 360, 175, 135, 24, "3. Запис свіжого v3", size=9.5, bold=True, fill="#fff2e6", stroke=POS))

    f.append(fitbox(x_left + 15, 280, half_w - 30, 195,
                    "Послідовність кроків:\n"
                    "1. Координатор зчитує стан з R=3 вузлів\n"
                    "2. Виявляє розходження версій: Вузол 3 має застарілу v2\n"
                    "3. Клієнту негайно повертається свіже значення v3\n"
                    "4. У фоновому режимі надсилається дельта v3 на Вузол 3,\n"
                    "   оновлюючи його стан без участі оператора",
                    size=10.5, fill=FILL, stroke=MUTED))

    # ── Права половина: Hinted Handoff ──
    f.append(fitbox(x_right, 75, half_w, 420, "", fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(x_right + 10, 85, half_w - 20, 36, "B. HINTED HANDOFF (Тимчасова перетримка)", size=12.5, bold=True, fill=WARN))

    f.append(fitbox(x_right + 30, 140, 120, 45, "Клієнт\n(Запис v4)", size=11, bold=True, fill=COOL))
    f.append(fitbox(x_right + 185, 140, 135, 45, "Вузол A (Цільовий)\n🔴 ТИМЧАСОВО ВПАВ", size=10.5, bold=True, fill=WARM, stroke=POS))
    f.append(fitbox(x_right + 345, 140, 140, 45, "Вузол X (Сурогат)\nПриймає «натяк»", size=10.5, bold=True, fill=WARN, stroke=LINE))

    # Маршрутизація запису
    f.append(arrow(x_right + 150, 155, x_right + 180, 155, color=POS, sw=1.5))
    f.append(line(x_right + 172, 148, x_right + 188, 162, color=POS, sw=2.5))
    f.append(arrow(x_right + 90, 195, x_right + 415, 195, color=FIELD, sw=1.8))
    f.append(fitbox(x_right + 140, 205, 240, 24, "1. Запис іде на Вузол X з міткою для A", size=10, bold=True, fill=BG, stroke=FIELD))

    # Передача після одужання
    f.append(fitbox(x_right + 185, 245, 135, 45, "Вузол A (Цільовий)\n🟢 ПОВЕРНУВСЯ В СТРОЙ", size=10.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(x_right + 395, 188, x_right + 325, 255, color=NEG, sw=2))
    f.append(fitbox(x_right + 340, 245, 155, 24, "2. Handoff дельти", size=10, bold=True, fill=BG, stroke=NEG))

    f.append(fitbox(x_right + 15, 300, half_w - 30, 175,
                    "Послідовність кроків:\n"
                    "1. Цільовий вузол репліки A недоступний через збій мережі\n"
                    "2. Сусідній вузол X погоджується тимчасово зберегти мутацію\n"
                    "   у спеціальній локальній черзі натяків (Hints Queue)\n"
                    "3. Коли Gossip-протокол сигналізує, що вузол A ожив,\n"
                    "   вузол X вивантажує накопичені дельти на вузол A",
                    size=10.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'read-repair-and-hinted-handoff.svg'), W, H, *f)


if __name__ == '__main__':
    three_topologies_comparison()
    quorum_intersection()
    multi_leader_conflict_divergence()
    read_repair_and_hinted_handoff()
    print("All figures generated successfully.")
