# -*- coding: utf-8 -*-
"""Фігури до статті «Операція Popcount».
Генерує векторні схеми SVG у теці ./img/:
1. swar-tree.svg — Дерево порозрядного паралельного додавання SWAR (SIMD within a register)
2. succinct-rank.svg — Дворівнева структура Rank9/Poppy для O(1) обчислення рангу у стиснених бітових векторах
3. hamt-indexing.svg — Індексація розріджених масивів у HAMT через popcount та маску молодших бітів
4. csa-vectorized.svg — Конвеєр компресорів Carry-Save Adder (CSA 3:2 / Harley-Seal) для векторизованого підрахунку
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Дерево порозрядного паралельного додавання SWAR
# ─────────────────────────────────────────────────────────────────────────────
def fig_swar_tree():
    W, H = 840, 560
    parts = []

    parts.append(rect(15, 15, 810, 530, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Дерево порозрядного паралельного додавання (SWAR)", size=16, color=INK, bold=True))
    parts.append(text(420, 68, "64 біти згортаються у 6 кроків порозрядного складання лічильників однакової ширини", size=12, color=MUTED))

    # Steps representation for an 8-bit slice for visual clarity
    steps = [
        ("Вхідне слово (8 біт)", "1  0  1  1  0  1  1  1", "8 окремих 1-бітних розрядів", "#f8fafc", "#64748b"),
        ("Крок 1: пари (маска 0x55)", "[0 1] [1 0] [0 1] [1 0]", "4 двобітні поля: 1 + 2 + 1 + 2 = 6", "#eff6ff", "#3b82f6"),
        ("Крок 2: четвірки (маска 0x33)", "[0 0 1 1]   [0 0 1 1]", "2 чотирибітні поля: 3 + 3 = 6", "#f0fdf4", "#22c55e"),
        ("Крок 3: вісімка (маска 0x0F)", "[0 0 0 0 0 1 1 0]", "1 восьмибітне поле: сума = 6", "#fefce8", "#eab308"),
        ("Множення на 0x01... >> 56", "Сума всіх 8 байтів у старшому байті слова = 6", "Згортка 64-бітного слова за 1 такт множення", "#faf5ff", "#a855f7"),
    ]

    y_pos = 90
    for title, bits_repr, desc, bg, border in steps:
        parts.append(rect(40, y_pos, 760, 64, fill=bg, stroke=border, sw=1.5, rx=6))
        parts.append(text(60, y_pos + 23, title, size=13, color=INK, anchor="start", bold=True))
        parts.append(text(380, y_pos + 23, bits_repr, size=13, color="#1e3a8a", anchor="start", bold=True))
        parts.append(text(60, y_pos + 48, desc, size=11, color=MUTED, anchor="start"))
        y_pos += 74

    # Bottom summary box
    parts.append(rect(40, y_pos + 5, 760, 48, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=6))
    parts.append(text(420, y_pos + 34, "Глибина обчислення: log₂(W) кроків замість W ітерацій послідовного циклу", size=12, color=INK, bold=True))

    svg_content = "\n".join(parts)
    with open(os.path.join(OUT, "swar-tree.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Дворівневий індекс Rank9 / Poppy для лаконічних структур
# ─────────────────────────────────────────────────────────────────────────────
def fig_succinct_rank():
    W, H = 840, 500
    parts = []

    parts.append(rect(15, 15, 810, 470, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Дворівнева лаконічна структура rank1(i) через popcount", size=16, color=INK, bold=True))
    parts.append(text(420, 68, "Суперблоки фіксують абсолютний ранг, блоки — відносний, залишок — апаратний popcount", size=12, color=MUTED))

    # Level 1: Superblock
    y1 = 100
    parts.append(rect(40, y1, 760, 75, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    parts.append(text(60, y1 + 25, "Рівень 1: Суперблок (512 або 2048 бітів)", size=13, color="#1e40af", anchor="start", bold=True))
    parts.append(text(60, y1 + 52, "Зберігає абсолютну кількість одиниць від початку бітового масиву: S[k] = rank1(k · L₁)", size=11, color=INK, anchor="start"))
    parts.append(rect(580, y1 + 15, 200, 45, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(680, y1 + 42, "S[k] = 1420 одиниць", size=12, color="#1e40af", bold=True))

    # Level 2: Basic Blocks inside Superblock
    y2 = 195
    parts.append(rect(40, y2, 760, 95, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(60, y2 + 25, "Рівень 2: Базові блоки (64-бітні слова всередині суперблока)", size=13, color="#15803d", anchor="start", bold=True))
    parts.append(text(60, y2 + 48, "Зберігає відносне зміщення рангу всередині суперблока (упаковані 9-бітні лічильники)", size=11, color=INK, anchor="start"))

    # Block cells
    for i in range(8):
        bx = 60 + i * 90
        parts.append(rect(bx, y2 + 58, 82, 28, fill="#ffffff", stroke="#22c55e", sw=1, rx=3))
        parts.append(text(bx + 41, y2 + 76, f"B[{i}]: +{i * 4}", size=11, color="#14532d"))

    # Level 3: Target Word & Masked Popcount
    y3 = 310
    parts.append(rect(40, y3, 760, 110, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    parts.append(text(60, y3 + 25, "Рівень 3: Цільове 64-бітне слово W та бітова маска залишку", size=13, color="#854d0e", anchor="start", bold=True))
    parts.append(text(60, y3 + 48, "Маска виділяє розряди, менші за (i mod 64): mask = (1ULL << (i mod 64)) - 1", size=11, color=INK, anchor="start"))
    parts.append(text(60, y3 + 70, "Апаратна інструкція обчислює одиниці в залишку: popcount(W & mask)", size=11, color=INK, anchor="start"))
    parts.append(rect(540, y3 + 35, 240, 50, fill="#ffffff", stroke="#eab308", sw=1.2, rx=4))
    parts.append(text(660, y3 + 65, "popcount(W & mask) = 5", size=12, color="#854d0e", bold=True))

    # Formula bar at bottom
    parts.append(rect(40, 435, 760, 36, fill="#f8fafc", stroke="#64748b", sw=1, rx=4))
    parts.append(text(420, 458, "Підсумок: rank1(i) = Superblock[i/L₁] + BlockOffset[i/64] + popcount(W & mask)", size=12, color=INK, bold=True))

    svg_content = "\n".join(parts)
    with open(os.path.join(OUT, "succinct-rank.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Індексація в HAMT через popcount
# ─────────────────────────────────────────────────────────────────────────────
def fig_hamt_indexing():
    W, H = 840, 500
    parts = []

    parts.append(rect(15, 15, 810, 470, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Індексація розрідженого вузла HAMT через popcount", size=16, color=INK, bold=True))
    parts.append(text(420, 68, "Бітова мапа вузла вказує наявні гілки; popcount маскованої частини визначає точний індекс", size=12, color=MUTED))

    # 1. 5-bit key chunk
    y1 = 95
    parts.append(rect(40, y1, 760, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    parts.append(text(60, y1 + 25, "1. Фрагмент хешу ключа на поточному рівні дерева", size=13, color="#1e40af", anchor="start", bold=True))
    parts.append(text(60, y1 + 48, "5 бітів дають номер гілки k ∈ [0..31]: k = (hash >> shift) & 0x1F = 11 (двійкове 01011)", size=11, color=INK, anchor="start"))

    # 2. Bitmap representation
    y2 = 175
    parts.append(rect(40, y2, 760, 120, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(60, y2 + 25, "2. 32-бітна мапа зайнятих слотів вузла (bitmap)", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(60, y2 + 48, "Одиниця в позиції k означає наявність піддерева або ключа у відповідному слоті", size=11, color=MUTED, anchor="start"))

    # Draw 32 bit slots
    slot_w = 21
    start_x = 75
    active_bits = {2, 5, 8, 11, 19, 25, 30}
    for b in range(32):
        bx = start_x + b * slot_w
        is_k = (b == 11)
        is_set = b in active_bits
        bg = "#ef4444" if is_k else ("#22c55e" if is_set else "#ffffff")
        txt_col = "#ffffff" if (is_k or is_set) else "#94a3b8"
        parts.append(rect(bx, y2 + 60, slot_w - 2, 26, fill=bg, stroke="#475569", sw=1, rx=2))
        parts.append(text(bx + (slot_w - 2) / 2, y2 + 78, "1" if is_set else "0", size=10, color=txt_col, bold=is_set))
        parts.append(text(bx + (slot_w - 2) / 2, y2 + 102, str(b), size=9, color=MUTED))

    # 3. Mask & Popcount calculation
    y3 = 310
    parts.append(rect(40, y3, 760, 85, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(60, y3 + 25, "3. Обчислення зміщення у щільному масиві вказівників", size=13, color="#15803d", anchor="start", bold=True))
    parts.append(text(60, y3 + 48, "Маска молодших бітів: mask = (1 << 11) - 1 (виділяє всі біти від 0 до 10)", size=11, color=INK, anchor="start"))
    parts.append(text(60, y3 + 68, "Індекс = popcount(bitmap & mask) = popcount(біти 2, 5, 8) = 3", size=12, color="#166534", anchor="start", bold=True))

    # 4. Dense array representation
    y4 = 410
    parts.append(rect(40, y4, 760, 60, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    parts.append(text(60, y4 + 25, "4. Компактний масив вказівників (довжина 7 замість 32):", size=12, color="#854d0e", anchor="start", bold=True))
    for idx in range(7):
        bx = 470 + idx * 42
        is_target = (idx == 3)
        bg = "#fde047" if is_target else "#ffffff"
        parts.append(rect(bx, y4 + 10, 38, 38, fill=bg, stroke="#a16207" if is_target else "#ca8a04", sw=1.5 if is_target else 1, rx=3))
        parts.append(text(bx + 19, y4 + 34, f"[{idx}]", size=11, color="#713f12", bold=is_target))

    svg_content = "\n".join(parts)
    with open(os.path.join(OUT, "hamt-indexing.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Конвеєр компресорів Carry-Save Adder (CSA / Harley-Seal)
# ─────────────────────────────────────────────────────────────────────────────
def fig_csa_vectorized():
    W, H = 840, 510
    parts = []

    parts.append(rect(15, 15, 810, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Векторизований підрахунок: компресори Carry-Save Adder (3:2 CSA)", size=16, color=INK, bold=True))
    parts.append(text(420, 68, "Алгоритм Харлі-Сіла згортає 3 вектори у суму та перенос без горизонтального розповсюдження бітів", size=12, color=MUTED))

    # Inputs A, B, C
    y1 = 100
    parts.append(rect(60, y1, 200, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(160, y1 + 28, "Векторне слово A (64/256/512b)", size=11, color="#1e40af", bold=True))

    parts.append(rect(320, y1, 200, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(420, y1 + 28, "Векторне слово B (64/256/512b)", size=11, color="#1e40af", bold=True))

    parts.append(rect(580, y1, 200, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(680, y1 + 28, "Векторне слово C (64/256/512b)", size=11, color="#1e40af", bold=True))

    # CSA 3:2 Compressor Block
    y_csa = 185
    parts.append(rect(180, y_csa, 480, 110, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=8))
    parts.append(text(420, y_csa + 30, "Повний тривходовий двійковий суматор (3:2 CSA)", size=14, color="#15803d", bold=True))
    parts.append(text(420, y_csa + 58, "Сума (Sum): s = A ⊕ B ⊕ C (побітове XOR)", size=12, color=INK))
    parts.append(text(420, y_csa + 84, "Перенос (Carry): c = (A ∧ B) ∨ (B ∧ C) ∨ (C ∧ A) [з вагою 2]", size=12, color=INK))

    # Outputs of CSA
    y_out = 335
    parts.append(rect(140, y_out, 240, 55, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    parts.append(text(260, y_out + 25, "Вихідний біт суми (вага 1)", size=12, color="#854d0e", bold=True))
    parts.append(text(260, y_out + 45, "Накопичується у лічильнику Onés", size=10, color=MUTED))

    parts.append(rect(460, y_out, 240, 55, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    parts.append(text(580, y_out + 25, "Вихідний біт переносу (вага 2)", size=12, color="#854d0e", bold=True))
    parts.append(text(580, y_out + 45, "Передається на наступний каскад CSA", size=10, color=MUTED))

    # Reduction tree summary at bottom
    y_tree = 425
    parts.append(rect(40, y_tree, 760, 55, fill="#faf5ff", stroke="#a855f7", sw=1.2, rx=6))
    parts.append(text(420, y_tree + 24, "Дерево компресорів 7:3 і 15:4 дозволяє згортати 16 слів пам'яті лише за кілька SIMD-інструкцій", size=12, color="#581c87", bold=True))
    parts.append(text(420, y_tree + 44, "Пропускна здатність: понад 15-20 ГБ/с підрахунку одиниць на одне ядро CPU", size=11, color=MUTED))

    svg_content = "\n".join(parts)
    with open(os.path.join(OUT, "csa-vectorized.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


if __name__ == "__main__":
    fig_swar_tree()
    fig_succinct_rank()
    fig_hamt_indexing()
    fig_csa_vectorized()
    print("Всі фігури згенеровано успішно.")
