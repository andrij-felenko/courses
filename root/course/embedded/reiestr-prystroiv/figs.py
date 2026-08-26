# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Реєстр пристроїв: імена, групи, вибірки».

Фігури:
  1. device-entity-model.svg          — Модель сутності пристрою в реєстрі: шари метаданих та ідентифікація.
  2. hierarchical-vs-tag-topology.svg — Жорстка ієрархія проти багатовимірного простору тегів і вибірок.
  3. dynamic-fleet-indexing.svg       — Конвеєр динамічних вибірок: мутація стану, індекси, таргетинг кампаній.
  4. fleet-health-state-machine.svg   — Автомат життєвого циклу та моніторингу здоров'я вузла в парку.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_device_entity_model():
    """Фігура 1: Анатомія сутності пристрою: незмінні апаратні дані, системний стан і призначені теги."""
    w, h = 820, 470
    p = []

    p.append(text(w / 2, 48, "Розподіл атрибутів за походженням, мутабельністю та зонами відповідальності", size=12, color=MUTED))

    # Головна плашка унікального первинного ідентифікатора
    p.append(rect(40, 68, 740, 62, fill="#ebf3fd", stroke=NEG, sw=2.0, rx=8))
    p.append(text(70, 93, "Ключ сутності (Primary Identity Key): Device UUID / URN", size=14, bold=True, color=NEG, anchor="start"))
    p.append(text(70, 114, "urn:fleet:device:550e8400-e29b-41d4-a716-446655440000 · Прив'язаний до X.509 Subject Key ID", size=11, color=INK, anchor="start"))

    # Три колонки атрибутів
    col_w = 233
    gap = 20
    top_y = 148
    box_h = 240

    # Колонка 1: Незмінні апаратні атрибути (Immutable Hardware)
    x1 = 40
    p.append(rect(x1, top_y, col_w, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x1, top_y, col_w, 36, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x1 + col_w / 2, top_y + 23, "Незмінні апаратні дані", size=13, bold=True))

    items1 = [
        ("Silicon Chip UID", "96-бітний унікальний ID чипа"),
        ("Hardware Revision", "rev_v2.3 (друкована плата)"),
        ("Factory MAC / IMEI", "фізична мережева адреса"),
        ("Secure Element Cert", "SHA-256 fingerprint ключа"),
        ("Production Batch", "партія: 2026-W14-PL02"),
        ("Manufacture Date", "2026-04-03T10:15:00Z"),
    ]
    for idx, (lbl, val) in enumerate(items1):
        cy = top_y + 54 + idx * 30
        p.append(text(x1 + 12, cy, lbl, size=11, bold=True, anchor="start"))
        p.append(text(x1 + 12, cy + 13, val, size=10, color=MUTED, anchor="start"))

    # Колонка 2: Динамічний системний стан (Mutable System State)
    x2 = x1 + col_w + gap
    p.append(rect(x2, top_y, col_w, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x2, top_y, col_w, 36, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x2 + col_w / 2, top_y + 23, "Динамічний стан системи", size=13, bold=True))

    items2 = [
        ("Firmware Version", "v2.1.4-prod (SemVer)"),
        ("Bootloader Version", "v1.2.0 (Dual-Bank A/B)"),
        ("Connection Status", "ONLINE (LWT / KeepAlive)"),
        ("Current IP / Cell CID", "10.42.18.91 / eNodeB 4912"),
        ("Signal Quality (RSSI)", "-74 dBm (CSQ 22, LTE-M)"),
        ("Battery / Uptime", "3.92 V (85%) / 14d 6h 12m"),
    ]
    for idx, (lbl, val) in enumerate(items2):
        cy = top_y + 54 + idx * 30
        p.append(text(x2 + 12, cy, lbl, size=11, bold=True, anchor="start"))
        p.append(text(x2 + 12, cy + 13, val, size=10, color=MUTED, anchor="start"))

    # Колонка 3: Логічні метадані та теги (Logical Tags & Topology)
    x3 = x2 + col_w + gap
    p.append(rect(x3, top_y, col_w, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x3, top_y, col_w, 36, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x3 + col_w / 2, top_y + 23, "Користувацькі теги й групи", size=13, bold=True))

    items3 = [
        ("tenant_id", "energo-grid-west"),
        ("site / location", "dnipro-substation-14"),
        ("environment", "prod (канал оновлень)"),
        ("device_role", "edge-power-meter"),
        ("maintenance_tier", "sla-gold-24x7"),
        ("static_group", "pilot-wave-alpha"),
    ]
    for idx, (lbl, val) in enumerate(items3):
        cy = top_y + 54 + idx * 30
        p.append(text(x3 + 12, cy, lbl, size=11, bold=True, anchor="start"))
        p.append(text(x3 + 12, cy + 13, val, size=10, color=FIELD, anchor="start"))

    # Нижня стрічка інваріантів
    p.append(rect(40, 404, 740, 50, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    p.append(text(55, 424, "Інваріант цілісності:", size=11, bold=True, color="#7d6608", anchor="start"))
    p.append(text(55, 442, "Апаратні дані фіксуються при введенні в лад; стан мутує через телеметрію; теги змінюються виключно через API керування.", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "device-entity-model.svg"), w, h, *p, title="Анатомія сутності пристрою в хмарному реєстрі")


def fig_hierarchical_vs_tag_topology():
    """Фігура 2: Жорстка ієрархія проти багатовимірного простору тегів."""
    w, h = 820, 450
    p = []

    p.append(text(w / 2, 48, "Чому монолітна ієрархія ламається при багатокритеріальному таргетуванні", size=12, color=MUTED))

    half_w = 360
    top_y = 70
    box_h = 354

    # Ліва панель: Жорстка ієрархія
    x_l = 35
    p.append(rect(x_l, top_y, half_w, box_h, fill=FILL, stroke=POS, sw=1.4, rx=8))
    p.append(rect(x_l, top_y, half_w, 36, fill="#fde8e8", stroke=POS, sw=1.0, rx=8))
    p.append(text(x_l + half_w / 2, top_y + 23, "Жорстка ієрархія (Rigid Hierarchy)", size=13, bold=True, color=POS))

    # Деревоподібні вузли
    p.append(rect(x_l + 110, top_y + 50, 140, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(x_l + 180, top_y + 67, "Region: Western", size=11, bold=True))

    p.append(line(x_l + 180, top_y + 76, x_l + 100, top_y + 105, color=LINE, sw=1.2))
    p.append(line(x_l + 180, top_y + 76, x_l + 260, top_y + 105, color=LINE, sw=1.2))

    p.append(rect(x_l + 35, top_y + 105, 130, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(x_l + 100, top_y + 122, "City: Lviv", size=11, bold=True))

    p.append(rect(x_l + 195, top_y + 105, 130, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(x_l + 260, top_y + 122, "City: Ivano-Frankivsk", size=11, bold=True))

    p.append(line(x_l + 100, top_y + 131, x_l + 100, top_y + 155, color=LINE, sw=1.2))
    p.append(rect(x_l + 35, top_y + 155, 130, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(x_l + 100, top_y + 172, "Facility: Substation-1", size=11, bold=True))

    p.append(line(x_l + 100, top_y + 181, x_l + 100, top_y + 205, color=LINE, sw=1.2))
    p.append(rect(x_l + 35, top_y + 205, 130, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(x_l + 100, top_y + 222, "Device ID: #0421", size=11, bold=True))

    # Обмеження дерева
    p.append(rect(x_l + 15, top_y + 248, half_w - 30, 92, fill="#fff5f5", stroke=POS, sw=0.8, rx=4))
    p.append(text(x_l + 25, top_y + 268, "Проблеми монолітного дерева:", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(x_l + 25, top_y + 288, "• Пристрій належить лише ОДНІЙ гілці.", size=10, anchor="start"))
    p.append(text(x_l + 25, top_y + 306, "• Неможливо вибрати всі плати revB", size=10, anchor="start"))
    p.append(text(x_l + 25, top_y + 324, "  у різних містах без перебору всього дерева.", size=10, anchor="start"))

    # Права панель: Багатовимірні теги
    x_r = x_l + half_w + 30
    p.append(rect(x_r, top_y, half_w, box_h, fill=FILL, stroke=FIELD, sw=1.4, rx=8))
    p.append(rect(x_r, top_y, half_w, 36, fill="#e8f8f0", stroke=FIELD, sw=1.0, rx=8))
    p.append(text(x_r + half_w / 2, top_y + 23, "Багатовимірний простір тегів", size=13, bold=True, color=FIELD))

    # Візуалізація тегів
    tags_demo = [
        ("site = lviv", 15, 52, "#dcfce7", "#166534"),
        ("env = prod", 130, 52, "#e0e7ff", "#3730a3"),
        ("hw = revB", 230, 52, "#fef3c7", "#92400e"),
        ("role = meter", 15, 88, "#f3e8ff", "#6b21a8"),
        ("tier = gold", 130, 88, "#ffedd5", "#9a3412"),
        ("fw < 2.2.0", 230, 88, "#fee2e2", "#991b1b"),
    ]
    for tag_txt, tx, ty, bg_c, fg_c in tags_demo:
        tw = len(tag_txt) * 7.5 + 18
        p.append(rect(x_r + tx, top_y + ty, tw, 24, fill=bg_c, stroke=fg_c, sw=0.9, rx=12))
        p.append(text(x_r + tx + tw / 2, top_y + ty + 16, tag_txt, size=10, bold=True, color=fg_c))

    # Декларативний запит вибірки
    p.append(rect(x_r + 15, top_y + 130, half_w - 30, 96, fill="#1e293b", stroke="#0f172a", sw=1.0, rx=6))
    p.append(text(x_r + 25, top_y + 150, "Динамічний предикатний запит:", size=10, bold=True, color="#94a3b8", anchor="start"))
    p.append(text(x_r + 25, top_y + 172, "SELECT device_id WHERE", size=11, bold=True, color="#38bdf8", anchor="start"))
    p.append(text(x_r + 35, top_y + 192, "tags.hw == 'revB' AND", size=11, bold=True, color="#fde047", anchor="start"))
    p.append(text(x_r + 35, top_y + 210, "tags.env == 'prod' AND sys.fw < '2.2.0'", size=11, bold=True, color="#4ade80", anchor="start"))

    # Переваги простору тегів
    p.append(rect(x_r + 15, top_y + 248, half_w - 30, 92, fill="#f0fdf4", stroke=FIELD, sw=0.8, rx=4))
    p.append(text(x_r + 25, top_y + 268, "Переваги моделі тегів та вибірок:", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(x_r + 25, top_y + 288, "• Ортогональність вимірів (географія, роль, залізо).", size=10, anchor="start"))
    p.append(text(x_r + 25, top_y + 306, "• Членство в групах перераховується на льоту.", size=10, anchor="start"))
    p.append(text(x_r + 25, top_y + 324, "• Нульова вартість зміни топології об'єктів.", size=10, anchor="start"))

    render(os.path.join(IMG, "hierarchical-vs-tag-topology.svg"), w, h, *p, title="Організація парку: деревоподібна таксономія vs простір тегів")


def fig_dynamic_fleet_indexing():
    """Фігура 3: Архітектура конвеєра динамічних вибірок та індексації."""
    w, h = 840, 480
    p = []

    p.append(text(w / 2, 48, "Як зміни атрибутів у реальному часі активують цільові групи та кампанії оновлення", size=12, color=MUTED))

    bw = 175
    bh = 340
    gap = 26
    top_y = 75

    # Етап 1: Вхідний потік подій
    x1 = 30
    p.append(rect(x1, top_y, bw, bh, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x1, top_y, bw, 32, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x1 + bw / 2, top_y + 21, "1. Потік подій стану", size=12, bold=True))

    p.append(text(x1 + 12, top_y + 55, "MQTT / CoAP / HTTP", size=11, bold=True, color=NEG, anchor="start"))
    p.append(rect(x1 + 10, top_y + 70, bw - 20, 75, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x1 + 16, top_y + 90, "Telemetry Payload:", size=10, bold=True, anchor="start"))
    p.append(text(x1 + 16, top_y + 108, "fw_version: '2.1.4'", size=9, color=INK, anchor="start"))
    p.append(text(x1 + 16, top_y + 124, "battery_v: 3.85", size=9, color=INK, anchor="start"))
    p.append(text(x1 + 16, top_y + 138, "rssi: -72 dBm", size=9, color=INK, anchor="start"))

    p.append(text(x1 + 12, top_y + 170, "Admin Tag API:", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(rect(x1 + 10, top_y + 185, bw - 20, 60, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x1 + 16, top_y + 205, "PATCH /tags", size=10, bold=True, anchor="start"))
    p.append(text(x1 + 16, top_y + 223, "site: 'dnipro-14'", size=9, color=INK, anchor="start"))
    p.append(text(x1 + 16, top_y + 237, "tier: 'gold'", size=9, color=INK, anchor="start"))

    # Стрілка 1 -> 2
    p.append(arrow(x1 + bw, top_y + 170, x1 + bw + gap, top_y + 170, color=LINE, sw=1.8))

    # Етап 2: Реєстр та індекси
    x2 = x1 + bw + gap
    p.append(rect(x2, top_y, bw, bh, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x2, top_y, bw, 32, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x2 + bw / 2, top_y + 21, "2. Індекси реєстру", size=12, bold=True))

    p.append(rect(x2 + 10, top_y + 50, bw - 20, 80, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x2 + 16, top_y + 70, "B-Tree Indexes:", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(x2 + 16, top_y + 88, "• sys.fw_version", size=9, anchor="start"))
    p.append(text(x2 + 16, top_y + 104, "• sys.last_seen_ts", size=9, anchor="start"))
    p.append(text(x2 + 16, top_y + 120, "• sys.battery_soc", size=9, anchor="start"))

    p.append(rect(x2 + 10, top_y + 145, bw - 20, 85, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x2 + 16, top_y + 165, "GIN / Inverted Index:", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(x2 + 16, top_y + 183, "• tags.site -> BitMap", size=9, anchor="start"))
    p.append(text(x2 + 16, top_y + 199, "• tags.env -> BitMap", size=9, anchor="start"))
    p.append(text(x2 + 16, top_y + 215, "• tags.hw -> BitMap", size=9, anchor="start"))

    p.append(rect(x2 + 10, top_y + 245, bw - 20, 80, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x2 + 16, top_y + 265, "Device Shadow:", size=10, bold=True, anchor="start"))
    p.append(text(x2 + 16, top_y + 283, "Atomic State Store", size=9, color=MUTED, anchor="start"))
    p.append(text(x2 + 16, top_y + 301, "Reported vs Desired", size=9, color=MUTED, anchor="start"))

    # Стрілка 2 -> 3
    p.append(arrow(x2 + bw, top_y + 170, x2 + bw + gap, top_y + 170, color=LINE, sw=1.8))

    # Етап 3: Рушій вибірок (Query Evaluator)
    x3 = x2 + bw + gap
    p.append(rect(x3, top_y, bw, bh, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x3, top_y, bw, 32, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x3 + bw / 2, top_y + 21, "3. Рушій вибірок", size=12, bold=True))

    p.append(text(x3 + 12, top_y + 55, "Динамічні запити:", size=11, bold=True, color=INK, anchor="start"))

    p.append(rect(x3 + 10, top_y + 70, bw - 20, 115, fill="#eff6ff", stroke=NEG, sw=0.8, rx=4))
    p.append(text(x3 + 16, top_y + 90, "Group: 'Canary-Wave-1'", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(x3 + 16, top_y + 108, "Query Filter:", size=9, bold=True, anchor="start"))
    p.append(text(x3 + 16, top_y + 124, "tags.env == 'prod' AND", size=9, color=INK, anchor="start"))
    p.append(text(x3 + 16, top_y + 140, "sys.fw == '2.1.4' AND", size=9, color=INK, anchor="start"))
    p.append(text(x3 + 16, top_y + 156, "sys.battery > 0.40 AND", size=9, color=INK, anchor="start"))
    p.append(text(x3 + 16, top_y + 172, "hash(id) % 100 < 5", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(rect(x3 + 10, top_y + 200, bw - 20, 125, fill="#fdf4ff", stroke="#9333ea", sw=0.8, rx=4))
    p.append(text(x3 + 16, top_y + 220, "Continuous Match:", size=10, bold=True, color="#9333ea", anchor="start"))
    p.append(text(x3 + 16, top_y + 238, "При зміні fw -> 2.2.0", size=9, anchor="start"))
    p.append(text(x3 + 16, top_y + 254, "пристрій АВТОМАТИЧНО", size=9, bold=True, color=POS, anchor="start"))
    p.append(text(x3 + 16, top_y + 270, "вибуває з вибірки", size=9, bold=True, color=POS, anchor="start"))
    p.append(text(x3 + 16, top_y + 288, "без ручного втручання", size=9, color=MUTED, anchor="start"))
    p.append(text(x3 + 16, top_y + 306, "і без блокування бази.", size=9, color=MUTED, anchor="start"))

    # Стрілка 3 -> 4
    p.append(arrow(x3 + bw, top_y + 170, x3 + bw + gap, top_y + 170, color=LINE, sw=1.8))

    # Етап 4: Виконання цільових операцій (Targeted Operations)
    x4 = x3 + bw + gap
    p.append(rect(x4, top_y, bw, bh, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(rect(x4, top_y, bw, 32, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(x4 + bw / 2, top_y + 21, "4. Цільові кампанії", size=12, bold=True))

    p.append(rect(x4 + 10, top_y + 50, bw - 20, 80, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x4 + 16, top_y + 70, "Поетапне OTA (Canary):", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(x4 + 16, top_y + 88, "1% -> 10% -> 50% -> 100%", size=9, anchor="start"))
    p.append(text(x4 + 16, top_y + 104, "Автозупинка при помилках", size=9, color=POS, anchor="start"))
    p.append(text(x4 + 16, top_y + 120, "і відкат на слот B", size=9, color=POS, anchor="start"))

    p.append(rect(x4 + 10, top_y + 145, bw - 20, 80, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x4 + 16, top_y + 165, "Масова переконфігурація:", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(x4 + 16, top_y + 183, "Зміна URL брокера / ключів", size=9, anchor="start"))
    p.append(text(x4 + 16, top_y + 199, "за тегом region / site", size=9, anchor="start"))
    p.append(text(x4 + 16, top_y + 215, "без пікового шторму", size=9, color=MUTED, anchor="start"))

    p.append(rect(x4 + 10, top_y + 240, bw - 20, 85, fill="#ffffff", stroke=LINE, sw=0.8, rx=4))
    p.append(text(x4 + 16, top_y + 260, "Аудит та комплаєнс:", size=10, bold=True, anchor="start"))
    p.append(text(x4 + 16, top_y + 278, "Миттєвий підрахунок", size=9, anchor="start"))
    p.append(text(x4 + 16, top_y + 294, "вразливих або застарілих", size=9, anchor="start"))
    p.append(text(x4 + 16, top_y + 310, "вузлів у всій системі", size=9, anchor="start"))

    # Нижня стрічка пояснення
    p.append(rect(30, 425, 780, 44, fill="#f8fafc", stroke=LINE, sw=0.8, rx=6))
    p.append(text(w / 2, 452, "Запити виконуються декларативно над індексами реєстру без побайтового перебору парку (Full Table Scan).", size=11, color=INK))

    render(os.path.join(IMG, "dynamic-fleet-indexing.svg"), w, h, *p, title="Конвеєр динамічної індексації та цільових вибірок (Fleet Targeting)")


def fig_fleet_health_state_machine():
    """Фігура 4: Автомат станів життєвого циклу та моніторингу здоров'я вузла."""
    w, h = 820, 460
    p = []

    p.append(text(w / 2, 48, "Розрізнення штатного сну, обриву каналу (Silent) та лавинного перепідключення (Flapping)", size=12, color=MUTED))

    # Стан 1: PROVISIONED (Введено в лад)
    x1, y1 = 40, 85
    sw, sh = 175, 70
    p.append(rect(x1, y1, sw, sh, fill="#f1f5f9", stroke="#64748b", sw=1.4, rx=8))
    p.append(text(x1 + sw / 2, y1 + 28, "PROVISIONED", size=13, bold=True, color="#334155"))
    p.append(text(x1 + sw / 2, y1 + 50, "Створено запис у базі", size=10, color=MUTED))

    # Стан 2: ONLINE / HEALTHY (Здоровий)
    x2, y2 = 320, 85
    p.append(rect(x2, y2, sw, sh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x2 + sw / 2, y2 + 28, "ONLINE / HEALTHY", size=13, bold=True, color=FIELD))
    p.append(text(x2 + sw / 2, y2 + 50, "Heartbeat < T_ping, RSSI > -95", size=10, color=INK))

    # Стрілка 1 -> 2 (First Connect)
    p.append(arrow(x1 + sw, y1 + sh / 2, x2, y2 + sh / 2, color=LINE, sw=1.4))
    p.append(text((x1 + sw + x2) / 2, y1 + sh / 2 - 8, "Перший TLS / MQTT", size=10, color=INK))

    # Стан 3: DEGRADED (Деградований)
    x3, y3 = 600, 85
    p.append(rect(x3, y3, sw, sh, fill="#fefce8", stroke="#ca8a04", sw=1.4, rx=8))
    p.append(text(x3 + sw / 2, y3 + 28, "DEGRADED", size=13, bold=True, color="#a16207"))
    p.append(text(x3 + sw / 2, y3 + 50, "Втрати пакетів > 15%, Batt < 15%", size=10, color=INK))

    # Стрілка 2 -> 3 (Quality Drop)
    p.append(arrow(x2 + sw, y2 + sh / 2, x3, y3 + sh / 2, color="#ca8a04", sw=1.4))
    p.append(text((x2 + sw + x3) / 2, y2 + sh / 2 - 8, "RSSI / Batt drop", size=10, color="#ca8a04"))

    # Стан 4: SILENT / OFFLINE (Мовчазний / Офлайн)
    x4, y4 = 320, 240
    p.append(rect(x4, y4, sw, sh, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(x4 + sw / 2, y4 + 28, "SILENT / OFFLINE", size=13, bold=True, color=POS))
    p.append(text(x4 + sw / 2, y4 + 50, "Heartbeat > 3*T_ping / LWT", size=10, color=POS))

    # Стрілка 2 -> 4 (Timeout / Disconnect)
    p.append(arrow(x2 + sw / 2, y2 + sh, x4 + sw / 2, y4, color=POS, sw=1.4))
    p.append(text(x2 + sw / 2 + 10, (y2 + sh + y4) / 2, "Таймаут тиші", size=10, color=POS, anchor="start"))

    # Стрілка 4 -> 2 (Reconnect)
    p.append(arrow(x4 + 30, y4, x2 + 30, y2 + sh, color=FIELD, sw=1.4))
    p.append(text(x2 - 10, (y2 + sh + y4) / 2, "Повторний зв'язок", size=10, color=FIELD, anchor="end"))

    # Стан 5: FLAPPING / QUARANTINE (Лавинний збій)
    x5, y5 = 40, 240
    p.append(rect(x5, y5, sw, sh, fill="#faf5ff", stroke="#9333ea", sw=1.8, rx=8))
    p.append(text(x5 + sw / 2, y5 + 28, "FLAPPING (Карантин)", size=13, bold=True, color="#9333ea"))
    p.append(text(x5 + sw / 2, y5 + 50, "> 10 з'єднань / хв (шторм)", size=10, color=INK))

    # Стрілка 2 -> 5 (Flapping threshold exceeded)
    p.append(arrow(x2, y2 + sh - 10, x5 + sw, y5 + 20, color="#9333ea", sw=1.4))
    p.append(text((x2 + x5 + sw) / 2 - 20, (y2 + sh + y5) / 2 - 14, "Часті реконекти", size=10, color="#9333ea"))

    # Стан 6: DECOMMISSIONED (Виведений з експлуатації)
    x6, y6 = 600, 240
    p.append(rect(x6, y6, sw, sh, fill="#f8fafc", stroke="#475569", sw=1.4, rx=8))
    p.append(text(x6 + sw / 2, y6 + 28, "DECOMMISSIONED", size=13, bold=True, color="#475569"))
    p.append(text(x6 + sw / 2, y6 + 50, "Сертифікат відкликано (CRL)", size=10, color=MUTED))

    # Стрілка 4 -> 6 (Terminal retirement)
    p.append(arrow(x4 + sw, y4 + sh / 2, x6, y6 + sh / 2, color="#475569", sw=1.4))
    p.append(text((x4 + sw + x6) / 2, y4 + sh / 2 - 8, "Списання / Заміна", size=10, color="#475569"))

    # Нижня плашка правил діагностики
    p.append(rect(40, 360, 740, 80, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=6))
    p.append(text(55, 382, "Діагностичні правила реєстру здоров'я:", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(55, 402, "1. Шлейф тиші (Silent): вузол не шле LWT і не відповідає > 3 інтервалів -> фіксація обриву без блокування черги.", size=10, color=MUTED, anchor="start"))
    p.append(text(55, 418, "2. Деренчання (Flapping): вузол спамить Connect/Disconnect -> примусовий backoff та ізоляція сесії в шлюзі.", size=10, color=MUTED, anchor="start"))
    p.append(text(55, 434, "3. Індекс здоров'я: інтегральна формула FHI = f(Uptime, PacketLoss, RssiStability, ErrorRate).", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "fleet-health-state-machine.svg"), w, h, *p, title="Автомат станів доступності та виявлення аномальних вузлів")


def main():
    fig_device_entity_model()
    fig_hierarchical_vs_tag_topology()
    fig_dynamic_fleet_indexing()
    fig_fleet_health_state_machine()
    print("Усі 4 фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
