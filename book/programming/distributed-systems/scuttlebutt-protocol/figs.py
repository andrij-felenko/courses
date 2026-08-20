#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми scuttlebutt-protocol."""

import sys
import os

# scripts/ у корені репо (4 рівні вище)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_state_hierarchy():
    """Ієрархія стану: Вузол -> Покоління та Версія -> Атрибути."""
    w, h = 860, 420
    frags = []

    # Заголовок вузла
    frags.append(rect(40, 50, 780, 340, fill="#f8fafc", stroke="#334155", sw=2, rx=8))
    frags.append(text(430, 80, "Локальний стан вузла Node-1 (EndpointState)", size=16, bold=True, color="#0f172a"))

    # Блок метаданих HeartBeatState
    frags.append(rect(70, 110, 340, 100, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(240, 135, "Метадані життя (HeartBeatState)", size=14, bold=True, color="#1e293b"))
    frags.append(text(240, 165, "Generation = 1718900000 (епоха запуску)", size=13, color="#334155"))
    frags.append(text(240, 190, "MaxVersion = 42 (глобальний лічильник)", size=13, bold=True, color=POS))

    # Стрілка інкременту версії
    frags.append(arrow(410, 160, 470, 160, color="#64748b", sw=2))
    frags.append(text(440, 145, "монотонне", size=11, color="#64748b"))
    frags.append(text(440, 180, "зростання", size=11, color="#64748b"))

    # Блок дайджесту
    frags.append(rect(480, 110, 310, 100, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(635, 135, "Дайджест для пірів (GossipDigest)", size=14, bold=True, color="#92400e"))
    frags.append(text(635, 165, "Node-1: Gen=1718900000, MaxVer=42", size=13, bold=True, color="#78350f"))
    frags.append(text(635, 190, "Розмір у мережі: рівно 1 рядок O(1)", size=12, color="#b45309"))

    # Блок таблиці ключів ApplicationState
    frags.append(rect(70, 230, 720, 140, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(430, 255, "Таблиця значень стану вузла (ApplicationState Map)", size=14, bold=True, color="#0f172a"))

    # Рядки таблиці ключів
    keys_data = [
        ("STATUS", "\"NORMAL\"", "Версія: 12", "#f1f5f9"),
        ("LOAD", "\"1.42\"", "Версія: 39", "#f1f5f9"),
        ("SCHEMA", "\"v2.1.0\"", "Версія: 40", "#f1f5f9"),
        ("DC_RACK", "\"eu-west:rack-3\"", "Версія: 42 (найсвіжіша)", "#fee2e2"),
    ]

    for i, (k, val, ver, bg) in enumerate(keys_data):
        kx = 85 + i * 175
        frags.append(rect(kx, 275, 165, 80, fill=bg, stroke="#94a3b8", sw=1.2, rx=4))
        frags.append(text(kx + 82, 298, k, size=13, bold=True, color="#1e293b"))
        frags.append(text(kx + 82, 320, val, size=12, color="#475569"))
        frags.append(text(kx + 82, 342, ver, size=11, bold=(i == 3), color=(POS if i == 3 else "#64748b")))

    render(os.path.join(IMG_DIR, 'scuttlebutt-state-hierarchy.svg'), w, h, *frags)


def fig_handshake_flow():
    """Трифазне узгодження: SYN -> ACK -> ACK2."""
    w, h = 880, 480
    frags = []

    # Колони вузлів
    frags.append(rect(60, 40, 240, 410, fill="#f8fafc", stroke="#0284c7", sw=2, rx=8))
    frags.append(text(180, 70, "Вузол A (Ініціатор)", size=16, bold=True, color="#0369a1"))
    frags.append(text(180, 95, "Має: Node-1 -> v10, Node-2 -> v50", size=12, color="#475569"))

    frags.append(rect(580, 40, 240, 410, fill="#f8fafc", stroke="#16a34a", sw=2, rx=8))
    frags.append(text(700, 70, "Вузол B (Партнер)", size=16, bold=True, color="#15803d"))
    frags.append(text(700, 95, "Має: Node-1 -> v15, Node-2 -> v30", size=12, color="#475569"))

    # Фаза 1: SYN (A -> B)
    frags.append(arrow(300, 140, 580, 140, color="#0284c7", sw=2.5))
    frags.append(rect(340, 115, 200, 45, fill="#e0f2fe", stroke="#38bdf8", sw=1.5, rx=6))
    frags.append(text(440, 133, "1. SYN (GossipDigestSyn)", size=13, bold=True, color="#0369a1"))
    frags.append(text(440, 151, "Дайджест: {N1: 10, N2: 50}", size=11, color="#0c4a6e"))

    # Обчислення на B
    frags.append(rect(595, 175, 210, 60, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    frags.append(text(700, 195, "B бачить розбіжності:", size=11, bold=True, color="#166534"))
    frags.append(text(700, 212, "• Потрібно A: N1 (версії 11..15)", size=11, color="#15803d"))
    frags.append(text(700, 227, "• Потрібно B: N2 (версії > 30)", size=11, color="#15803d"))

    # Фаза 2: ACK (B -> A)
    frags.append(arrow(580, 280, 300, 280, color="#16a34a", sw=2.5))
    frags.append(rect(330, 255, 220, 50, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=6))
    frags.append(text(440, 274, "2. ACK (GossipDigestAck)", size=13, bold=True, color="#15803d"))
    frags.append(text(440, 294, "Дельта N1 (v11..15) + Дайджест {N2: 30}", size=11, color="#14532d"))

    # Застосування і підготовка на A
    frags.append(rect(75, 315, 210, 50, fill="#e0f2fe", stroke="#7dd3fc", sw=1, rx=4))
    frags.append(text(180, 335, "A застосовує дельту N1", size=11, bold=True, color="#0369a1"))
    frags.append(text(180, 352, "Готує дельту N2 (v31..50)", size=11, color="#0284c7"))

    # Фаза 3: ACK2 (A -> B)
    frags.append(arrow(300, 395, 580, 395, color="#0284c7", sw=2.5))
    frags.append(rect(340, 372, 200, 45, fill="#e0f2fe", stroke="#38bdf8", sw=1.5, rx=6))
    frags.append(text(440, 390, "3. ACK2 (GossipDigestAck2)", size=13, bold=True, color="#0369a1"))
    frags.append(text(440, 408, "Дельта N2 (версії 31..50)", size=11, color="#0c4a6e"))

    # Підсумок узгодження
    frags.append(text(180, 435, "Стан A: N1=15, N2=50 ✓", size=12, bold=True, color="#059669"))
    frags.append(text(700, 435, "Стан B: N1=15, N2=50 ✓", size=12, bold=True, color="#059669"))

    render(os.path.join(IMG_DIR, 'scuttlebutt-handshake-flow.svg'), w, h, *frags)


def fig_packet_ordering():
    """Впорядкування дельт за MTU: монотонний префікс версій без дірок."""
    w, h = 860, 430
    frags = []

    # Неправильний підхід: дірки у версіях
    frags.append(rect(40, 40, 370, 360, fill="#fff1f2", stroke="#f43f5e", sw=1.8, rx=8))
    frags.append(text(225, 70, "Помилкове сортування (хаотичне)", size=15, bold=True, color="#9f1239"))
    frags.append(text(225, 92, "Пакет обрізано за MTU на версії 18", size=12, color="#be123c"))

    bad_deltas = [
        ("N1 / Key: STATUS", "Версія 11", "#ffe4e6"),
        ("N1 / Key: SCHEMA", "Версія 15", "#ffe4e6"),
        ("N1 / Key: DC_RACK", "Версія 18", "#ffe4e6"),
    ]
    for i, (k, v, bg) in enumerate(bad_deltas):
        frags.append(rect(60, 115 + i * 50, 330, 40, fill=bg, stroke="#fb7185", sw=1, rx=4))
        frags.append(text(140, 140 + i * 50, k, size=12, bold=True, color="#881337"))
        frags.append(text(310, 140 + i * 50, v, size=12, color="#e11d48"))

    # Лінія ліміту MTU
    frags.append(line(50, 275, 400, 275, color=POS, sw=2, dash="4,4"))
    frags.append(text(225, 292, "── МЕЖА ПАКЕТА (MTU TRUNCATION) ──", size=11, bold=True, color=POS))

    frags.append(rect(60, 305, 330, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(140, 330, "N1 / Key: LOAD (пропущено!)", size=12, bold=True, color="#475569"))
    frags.append(text(310, 330, "Версія 12 (втрачено)", size=12, color="#64748b"))

    frags.append(text(225, 375, "Катастрофа: MaxVer піднято до 18,", size=12, bold=True, color="#9f1239"))
    frags.append(text(225, 393, "версію 12 ніколи більше не буде запитано!", size=12, color="#9f1239"))

    # Правильний підхід: строгий порядок за зростанням версій
    frags.append(rect(450, 40, 370, 360, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    frags.append(text(635, 70, "Канон Scuttlebutt (строгий порядок)", size=15, bold=True, color="#166534"))
    frags.append(text(635, 92, "Сортування за монотонним зростанням версій", size=12, color="#15803d"))

    good_deltas = [
        ("N1 / Key: STATUS", "Версія 11", "#dcfce7"),
        ("N1 / Key: LOAD", "Версія 12", "#dcfce7"),
        ("N1 / Key: SCHEMA", "Версія 13", "#dcfce7"),
    ]
    for i, (k, v, bg) in enumerate(good_deltas):
        frags.append(rect(470, 115 + i * 50, 330, 40, fill=bg, stroke="#86efac", sw=1, rx=4))
        frags.append(text(550, 140 + i * 50, k, size=12, bold=True, color="#14532d"))
        frags.append(text(720, 140 + i * 50, v, size=12, color="#16a34a"))

    frags.append(line(460, 275, 810, 275, color=FIELD, sw=2, dash="4,4"))
    frags.append(text(635, 292, "── МЕЖА ПАКЕТА (MTU TRUNCATION) ──", size=11, bold=True, color=FIELD))

    frags.append(rect(470, 305, 330, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(550, 330, "N1 / Key: DC_RACK", size=12, color="#475569"))
    frags.append(text(720, 330, "Версія 14 (наст. раунд)", size=12, color="#64748b"))

    frags.append(text(635, 375, "Безпечно: MaxVer піднято до 13,", size=12, bold=True, color="#166534"))
    frags.append(text(635, 393, "в наступному раунді запитають версії > 13.", size=12, color="#166534"))

    render(os.path.join(IMG_DIR, 'scuttlebutt-packet-ordering.svg'), w, h, *frags)


def fig_epoch_generation():
    """Епохи генерації при холодному перезавантаженні вузла."""
    w, h = 860, 380
    frags = []

    # Лінія часу зліва направо
    frags.append(rect(40, 40, 780, 300, fill="#f8fafc", stroke="#475569", sw=1.5, rx=8))
    frags.append(text(430, 70, "Вузол після перезавантаження: скидання лічильника версій", size=16, bold=True, color="#0f172a"))

    # Стан ДО падіння
    frags.append(rect(70, 110, 210, 130, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(175, 135, "1. До аварії", size=14, bold=True, color="#1e293b"))
    frags.append(text(175, 165, "Generation: 100", size=13, color="#334155"))
    frags.append(text(175, 190, "MaxVersion: 5000", size=13, bold=True, color="#0f172a"))
    frags.append(text(175, 220, "Кластер знає v=5000", size=11, color="#64748b"))

    # Аварія
    frags.append(arrow(280, 175, 340, 175, color=POS, sw=2))
    frags.append(rect(340, 125, 160, 100, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(420, 150, "💥 Аварійне", size=14, bold=True, color="#991b1b"))
    frags.append(text(420, 175, "перезавантаження", size=14, bold=True, color="#991b1b"))
    frags.append(text(420, 205, "пам'ять очищено", size=11, color="#b91c1c"))

    # Стан ПІСЛЯ падіння з новим Generation
    frags.append(arrow(500, 175, 560, 175, color=FIELD, sw=2))
    frags.append(rect(560, 110, 230, 130, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(675, 135, "2. Новий старт", size=14, bold=True, color="#166534"))
    frags.append(text(675, 165, "Generation: 200 (Gen_new > 100)", size=13, bold=True, color="#15803d"))
    frags.append(text(675, 190, "MaxVersion: 1 (скинуто)", size=13, color="#166534"))
    frags.append(text(675, 220, "Старий стан повністю анулюється", size=11, color="#15803d"))

    # Пояснення внизу
    frags.append(rect(70, 260, 720, 60, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(430, 285, "Правило домінування: (Gen_A > Gen_B) або (Gen_A == Gen_B і Ver_A > Ver_B)", size=13, bold=True, color="#0f172a"))
    frags.append(text(430, 305, "Вищий Generation беззастережно заміщує всі старі версії попереднього життя вузла.", size=12, color="#475569"))

    render(os.path.join(IMG_DIR, 'scuttlebutt-epoch-generation.svg'), w, h, *frags)


if __name__ == '__main__':
    fig_state_hierarchy()
    fig_handshake_flow()
    fig_packet_ordering()
    fig_epoch_generation()
    print("Всі 4 фігури успішно згенеровано.")
