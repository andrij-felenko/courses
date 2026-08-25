# -*- coding: utf-8 -*-
"""Генератор фігур для теми Time-Series Storage (Сховища часових рядів)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_data_model_and_index():
    """Фігура 1: Модель часового ряду та інвертований індекс (Label Index -> Series ID -> Samples)."""
    w, h = 900, 430
    frags = []

    # Заголовок секції вхідного потоку (зліва)
    b_in, _, _ = textbox(160, 45, "Вхідний вимір (Telemetry Sample)", size=14, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_in)

    sample_text = (
        "Метрика: node_cpu_seconds_total\n"
        "Мітки (Labels):\n"
        "  • job = \"node-exporter\"\n"
        "  • instance = \"srv-01\"\n"
        "  • mode = \"idle\"\n"
        "Точка: (t = 1718000000, v = 98.4)"
    )
    b_s, _, _ = textbox(160, 145, sample_text, size=12, pad=10, fill=FILL, stroke=LINE, min_w=280)
    frags.append(b_s)

    # Хешування міток у Series ID
    frags.append(arrow(160, 220, 160, 260, color=NEG))
    frags.append(text(160, 245, "Хешування / Fingerprint (64-bit FNV-1a)", size=11, color=MUTED))

    b_sid, _, _ = textbox(160, 290, "Series ID: 0x8F3A4C2B10D94E1A", size=13, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_sid)

    frags.append(arrow(160, 318, 160, 355, color=POS))
    b_pts, _, _ = textbox(160, 385, "Чанк точок ряду (Append-Only Chunks):\n[1718000000: 98.4] → [1718000015: 98.1] → ...", size=12, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=280)
    frags.append(b_pts)

    # Інвертований індекс (справа)
    b_idx_head, _, _ = textbox(620, 45, "Інвертований індекс (Inverted Postings Index)", size=14, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_idx_head)

    idx_text = (
        "Словник термів (Label Name = Value)  →  Списки Series ID (Postings List)\n\n"
        "__name__=\"node_cpu_seconds_total\"   →   [ 12,  45,  84,  109, ... ]\n"
        "job=\"node-exporter\"                 →   [ 12,  45,  84,  109, ... ]\n"
        "instance=\"srv-01\"                   →   [ 12,  84,  210, 305, ... ]\n"
        "mode=\"idle\"                         →   [ 12,  45,  512, ... ]"
    )
    b_idx, _, _ = textbox(620, 150, idx_text, size=12, pad=12, fill=FILL, stroke=LINE, min_w=480)
    frags.append(b_idx)

    # Операція пошуку (Intersects)
    b_query, _, _ = textbox(620, 275, "Запит: node_cpu_seconds_total{instance=\"srv-01\", mode=\"idle\"}\nПеретин списків (Bitwise AND / Merge Join): Series ID = 12", size=12, pad=10, fill="#fdecea", stroke=POS, min_w=480)
    frags.append(b_query)

    frags.append(arrow(620, 220, 620, 245, color=LINE))
    frags.append(arrow(620, 315, 620, 350, color=FIELD))

    b_read, _, _ = textbox(620, 385, "Зчитування стиснених блоків лише для знайдених Series ID\n(Висока селективність без повного сканування диску)", size=12, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=480)
    frags.append(b_read)

    render(os.path.join(IMG_DIR, "tsdb-data-model-and-index.svg"), w, h, *frags)


def fig_timestamp_delta():
    """Фігура 2: Стиснення часових міток за схемою Delta-of-Delta (Gorilla / Prometheus)."""
    w, h = 920, 420
    frags = []

    # Заголовок
    b_head, _, _ = textbox(460, 35, "Стиснення часових міток: Схема Delta-of-Delta (Δ-of-Δ)", size=15, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_head)

    # Ряд міток часу
    t_boxes = [
        ("t₀ = 1718000000", 110, 95),
        ("t₁ = 1718000060", 330, 95),
        ("t₂ = 1718000120", 550, 95),
        ("t₃ = 1718000182", 770, 95),
    ]
    for txt, cx, cy in t_boxes:
        b, _, _ = textbox(cx, cy, txt, size=12, bold=True, fill=FILL, stroke=LINE, pad=6)
        frags.append(b)

    # Стрілки перших дельт D_i
    frags.append(arrow(180, 95, 260, 95, color=LINE))
    frags.append(text(220, 80, "Δ₀ = 60s", size=11, color=MUTED))

    frags.append(arrow(400, 95, 480, 95, color=LINE))
    frags.append(text(440, 80, "Δ₁ = 60s", size=11, color=MUTED))

    frags.append(arrow(620, 95, 700, 95, color=LINE))
    frags.append(text(660, 80, "Δ₂ = 62s", size=11, color=MUTED))

    # Обчислення Delta-of-Delta (DOD)
    dod_text = (
        "Обчислення різниці між сусідніми інтервалами (DOD = Δᵢ − Δᵢ₋₁):\n"
        "• DOD₁ = Δ₁ − Δ₀ = 60 − 60 = 0  (Ідеальний фіксований інтервал опитування)\n"
        "• DOD₂ = Δ₂ − Δ₁ = 62 − 60 = +2  (Незначне тремтіння таймера / мережевий джитер)"
    )
    b_dod, _, _ = textbox(460, 175, dod_text, size=12, pad=10, fill="#e8f8f0", stroke=FIELD, min_w=820)
    frags.append(b_dod)

    # Таблиця бітових діапазонів
    enc_head, _, _ = textbox(460, 245, "Змінна префіксна бітова розкладка для DOD:", size=13, bold=True, fill="#fdecea", stroke=POS)
    frags.append(enc_head)

    enc_table = (
        "Значення DOD                Префікс        Біти значення            Загальна ціна\n"
        "DOD = 0                     '0'            (немає)                  1 біт\n"
        "DOD ∈ [-63, 64]             '10'           7 біт (двійковий код)    9 біт\n"
        "DOD ∈ [-255, 256]           '110'          9 біт (двійковий код)    12 біт\n"
        "DOD ∈ [-2047, 2048]         '1110'         12 біт (двійковий код)   16 біт\n"
        "DOD > 2048 або < -2047      '1111'         32 біти (повне число)    36 біт"
    )
    b_tbl, _, _ = textbox(460, 335, enc_table, size=11.5, pad=10, fill=FILL, stroke=LINE, min_w=820)
    frags.append(b_tbl)

    render(os.path.join(IMG_DIR, "timestamp-delta-compression.svg"), w, h, *frags)


def fig_gorilla_xor():
    """Фігура 3: Стиснення дійсних чисел (IEEE 754 float64) через XOR за алгоритмом Gorilla."""
    w, h = 920, 450
    frags = []

    b_head, _, _ = textbox(460, 35, "Стиснення чисел з рухомою комою (Gorilla Float XOR)", size=15, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_head)

    # Дві послідовні величини
    val_text = (
        "Попереднє vᵢ₋₁: 98.40000000000000  →  0x405899999999999A  (64 біти)\n"
        "Поточне    vᵢ:   98.40000000000000  →  0x405899999999999A  (64 біти)"
    )
    b_vals, _, _ = textbox(460, 100, val_text, size=12, pad=8, fill=FILL, stroke=LINE, min_w=780)
    frags.append(b_vals)

    # XOR операція
    frags.append(arrow(460, 130, 460, 160, color=LINE))
    frags.append(text(530, 145, "XOR = vᵢ ⊕ vᵢ₋₁", size=12, bold=True, color=POS))

    # Два випадки розгалуження
    # Випадок 1 (зліва): XOR == 0
    b_case1_h, _, _ = textbox(220, 200, "Випадок 1: XOR == 0 (Значення не змінилось)", size=12, bold=True, fill="#e8f8f0", stroke=FIELD)
    frags.append(b_case1_h)

    c1_desc = (
        "Записується рівно один біт '0'.\n\n"
        "Ціна збереження точки: 1 БІТ\n"
        "(96% стабільних метрик у моніторингу)"
    )
    b_c1, _, _ = textbox(220, 280, c1_desc, size=12, pad=10, fill=FILL, stroke=FIELD, min_w=360)
    frags.append(b_c1)

    # Випадок 2 (справа): XOR != 0
    b_case2_h, _, _ = textbox(660, 200, "Випадок 2: XOR ≠ 0 (Значення змінилось)", size=12, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_case2_h)

    c2_desc = (
        "Записується біт '1' + маска значущих бітів:\n\n"
        "• Якщо кількість провідних і кінцевих нулів\n"
        "  вписується у попереднє вікно:\n"
        "    біт '0' + лише значущі біти (довжина L)\n\n"
        "• Якщо межі вікна змінились:\n"
        "    біт '1' + 5 біт (провідні нулі) +\n"
        "    6 біт (довжина L) + L значущих бітів"
    )
    b_c2, _, _ = textbox(660, 295, c2_desc, size=11.5, pad=10, fill=FILL, stroke=POS, min_w=440)
    frags.append(b_c2)

    # Підсумок знизу
    sum_text = "Результат: середній розмір пари (timestamp, float64) зменшується з 16 байтів (128 біт) до 1.37 байта (~11 біт)"
    b_sum, _, _ = textbox(460, 405, sum_text, size=12.5, bold=True, fill="#eaf0fd", stroke=NEG, min_w=840)
    frags.append(b_sum)

    render(os.path.join(IMG_DIR, "gorilla-xor-float-compression.svg"), w, h, *frags)


def fig_storage_engine_layout():
    """Фігура 4: Архітектура TSDB рушія (Memory Head, WAL, Block Compaction, Chunks & Postings)."""
    w, h = 920, 460
    frags = []

    b_title, _, _ = textbox(460, 30, "Архітектура та життєвий цикл блоків TSDB (Prometheus / InfluxDB TSM)", size=15, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_title)

    # 1. Оперативна пам'ять (Head Block)
    b_mem_h, _, _ = textbox(210, 80, "Оперативна пам'ять: Head Block (Активне вікно 0..2h)", size=12, bold=True, fill="#fdecea", stroke=POS)
    frags.append(b_mem_h)

    mem_desc = (
        "1. Active Chunks (120 точок у буфері)\n"
        "2. Head Index (Словник міток та Postings)\n"
        "3. Append-only WAL на диску (захист від збоїв)"
    )
    b_mem, _, _ = textbox(210, 160, mem_desc, size=12, pad=10, fill=FILL, stroke=POS, min_w=360)
    frags.append(b_mem)

    # Стрілка скидання на диск
    frags.append(arrow(395, 160, 500, 160, color=LINE))
    frags.append(text(450, 145, "Flush / Cut", size=11, bold=True, color=MUTED))
    frags.append(text(450, 180, "кожні 2 год", size=11, color=MUTED))

    # 2. Незмінний блок на диску (Immutable 2h Block)
    b_blk_h, _, _ = textbox(690, 80, "Незмінний блок на диску (2h Block Structure)", size=12, bold=True, fill="#e8f8f0", stroke=FIELD)
    frags.append(b_blk_h)

    blk_desc = (
        "• meta.json   (ULID, minTime, maxTime, stats)\n"
        "• chunks/     (mmap-сегменти, Gorilla-стиснення)\n"
        "• index       (B-Tree / Postings, CRC32, Dictionary)\n"
        "• tombstones  (бітові маски видалених інтервалів)"
    )
    b_blk, _, _ = textbox(690, 160, blk_desc, size=12, pad=10, fill=FILL, stroke=FIELD, min_w=380)
    frags.append(b_blk)

    # 3. Фонова компактифікація (Compaction Tiering)
    frags.append(arrow(690, 225, 690, 275, color=FIELD))
    frags.append(text(765, 250, "Фонове ущільнення (Compaction)", size=11, bold=True, color=FIELD))

    b_tier_h, _, _ = textbox(460, 310, "Багаторівневе об'єднання блоків (Compaction & Downsampling)", size=13, bold=True, fill="#eaf0fd", stroke=NEG)
    frags.append(b_tier_h)

    tier_desc = (
        "[Блок 0..2h] + [Блок 2..4h] + [Блок 4..6h] + [Блок 6..8h]\n"
        "                                  ↓\n"
        "Об'єднаний незмінний блок 8h / 24h: дедуплікація словника, утилізація tombstones,\n"
        "перевпорядкування чанків для послідовного зчитування mmap з диску."
    )
    b_tier, _, _ = textbox(460, 395, tier_desc, size=11.5, pad=10, fill=FILL, stroke=LINE, min_w=840)
    frags.append(b_tier)

    render(os.path.join(IMG_DIR, "tsdb-storage-engine-layout.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_data_model_and_index()
    fig_timestamp_delta()
    fig_gorilla_xor()
    fig_storage_engine_layout()
    print("Всі 4 фігури успішно згенеровано.")
