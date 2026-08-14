# -*- coding: utf-8 -*-
"""Фігури до статті «Hash Array Mapped Trie (HAMT)».
Генерує векторні схеми SVG у теці ./img/:
1. hamt-indexing.svg — побітова декомпозиція хешу, бітова мапа та обчислення індексу через popcount
2. trie-structure.svg — багаторівневе дерево HAMT з внутрішніми вузлами та листовими кошиками
3. path-copying.svg — структурне суміщення (structural sharing) та персистентність при оновленні
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Побітова декомпозиція та popcount-індексація
# ─────────────────────────────────────────────────────────────────────────────
def fig_hamt_indexing():
    W, H = 840, 460
    parts = []

    parts.append(rect(20, 20, 800, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 48, "Декодування хешу та індексація через маску бітів і popcount", size=16, color=INK, bold=True))
    parts.append(text(420, 72, "32-бітний хеш розбивається на 5-бітні фрагменти (0..31). Бітова мапа відсікає порожні вказівники.", size=13, color=MUTED))

    # 1. Hash decomposition block
    y_hash = 100
    parts.append(text(70, y_hash + 22, "32-бітний хеш:", size=13, color=INK, bold=True))
    
    # 6 chunks of 5 bits (and 2 remainder bits)
    chunks = [
        ("Рівень 5", "00"),
        ("Рівень 4", "01100"),
        ("Рівень 3", "10101"),
        ("Рівень 2", "00010"),
        ("Рівень 1", "00111"),
        ("Рівень 0", "01101"), # 13 in decimal
    ]
    
    x_c = 160
    for idx, (lvl, val) in enumerate(chunks):
        w_box = 68 if idx > 0 else 36
        is_target = (idx == 5)
        bg_col = "#dbeafe" if is_target else "#f1f5f9"
        border_col = "#2563eb" if is_target else "#94a3b8"
        
        parts.append(rect(x_c, y_hash, w_box, 36, fill=bg_col, stroke=border_col, sw=1.5 if is_target else 1, rx=4))
        parts.append(text(x_c + w_box / 2, y_hash + 22, val, size=12, color="#1e40af" if is_target else INK, bold=is_target))
        parts.append(text(x_c + w_box / 2, y_hash + 50, lvl, size=9, color=MUTED))
        x_c += w_box + 5

    # Target slice annotation
    parts.append(rect(570, y_hash - 5, 235, 55, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(687, y_hash + 18, "Фрагмент Рівня 0 = 01101₂ = 13", size=12, color="#15803d", bold=True))
    parts.append(text(687, y_hash + 38, "Шукаємо біт №13 у мапі вузла", size=11, color="#166534"))

    # 2. Bitmap mask visualizer
    y_bmp = 200
    parts.append(text(70, y_bmp + 20, "Бітова мапа (32 біти):", size=13, color=INK, bold=True))
    
    # Draw 32 bits representation (summarized or cell grid)
    # Highlight bits at 2, 5, 13
    x_b = 200
    cell_w = 17.5
    active_bits = {2: "P0", 5: "P1", 13: "P2"}
    
    for bit_idx in range(31, -1, -1):
        is_active = bit_idx in active_bits
        is_target_bit = (bit_idx == 13)
        
        if is_target_bit:
            bg = "#3b82f6"
            txt_c = "#ffffff"
        elif is_active:
            bg = "#86efac"
            txt_c = "#14532d"
        else:
            bg = "#f8fafc"
            txt_c = "#94a3b8"
            
        stroke_c = "#2563eb" if is_target_bit else ("#16a34a" if is_active else "#cbd5e1")
        parts.append(rect(x_b, y_bmp, cell_w, 30, fill=bg, stroke=stroke_c, sw=1, rx=2))
        parts.append(text(x_b + cell_w / 2, y_bmp + 19, "1" if is_active else "0", size=11, color=txt_c, bold=is_active))
        
        if bit_idx % 4 == 0 or bit_idx == 13 or bit_idx in active_bits:
            parts.append(text(x_b + cell_w / 2, y_bmp + 42, str(bit_idx), size=9, color=MUTED))
            
        x_b += cell_w + 1.5

    # 3. Math popcount step
    y_math = 280
    parts.append(rect(70, y_math, 735, 60, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    parts.append(text(85, y_math + 25, "1. Маска молодших бітів: mask = (1 << 13) - 1  (біти 0..12 установлені в 1)", size=12, color=INK, anchor="start"))
    parts.append(text(85, y_math + 45, "2. Відфільтрована мапа: bitmap & mask  →  має 2 встановлені біти (позиції 2 та 5)", size=12, color=INK, anchor="start"))
    parts.append(text(650, y_math + 35, "popcount(masked) = 2", size=14, color="#2563eb", bold=True))

    # 4. Compact physical array
    y_arr = 370
    parts.append(text(70, y_arr + 22, "Компактний масив:", size=13, color=INK, bold=True))
    
    arr_x = 200
    slot_w = 120
    slots = [
        ("Індекс 0 (біт 2)", "Вказівник P0"),
        ("Індекс 1 (біт 5)", "Вказівник P1"),
        ("Індекс 2 (біт 13)", "Вказівник P2 🎯"),
    ]
    
    for idx, (label, val) in enumerate(slots):
        is_hit = (idx == 2)
        bg = "#dbeafe" if is_hit else "#f1f5f9"
        border = "#2563eb" if is_hit else "#cbd5e1"
        
        parts.append(rect(arr_x, y_arr, slot_w, 40, fill=bg, stroke=border, sw=2 if is_hit else 1, rx=4))
        parts.append(text(arr_x + slot_w / 2, y_arr + 18, label, size=10, color=MUTED))
        parts.append(text(arr_x + slot_w / 2, y_arr + 33, val, size=12, color="#1e40af" if is_hit else INK, bold=is_hit))
        arr_x += slot_w + 15

    parts.append(arrow(650, y_math + 50, 480, y_arr, color="#2563eb", sw=2))

    render(os.path.join(OUT, "hamt-indexing.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Структура багаторівневого HAMT
# ─────────────────────────────────────────────────────────────────────────────
def fig_trie_structure():
    W, H = 840, 440
    parts = []

    parts.append(rect(20, 20, 800, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 48, "Багаторівнева структура геш-дерева HAMT", size=16, color=INK, bold=True))
    parts.append(text(420, 72, "Внутрішні вузли містять бітову мапу та компактний масив вказівників на наступні рівні або листи", size=13, color=MUTED))

    # Root Node (Level 0)
    rx, ry = 330, 100
    parts.append(rect(rx, ry, 180, 65, fill="#eff6ff", stroke="#2563eb", sw=2, rx=6))
    parts.append(text(rx + 90, ry + 22, "Корінь (Рівень 0)", size=13, color="#1e40af", bold=True))
    parts.append(text(rx + 90, ry + 42, "Bitmap: 0x00002004 (2 біти)", size=11, color="#3b82f6"))
    parts.append(rect(rx + 20, ry + 48, 60, 14, fill="#ffffff", stroke="#93c5fd", sw=1, rx=2))
    parts.append(text(rx + 50, ry + 59, "P0 (біт 2)", size=9, color="#1e40af"))
    parts.append(rect(rx + 100, ry + 48, 60, 14, fill="#ffffff", stroke="#93c5fd", sw=1, rx=2))
    parts.append(text(rx + 130, ry + 59, "P1 (біт 13)", size=9, color="#1e40af"))

    # Level 1 Node
    n1_x, n1_y = 480, 220
    parts.append(rect(n1_x, n1_y, 190, 65, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    parts.append(text(n1_x + 95, n1_y + 22, "Внутрішній вузол (Рівень 1)", size=12, color="#1e40af", bold=True))
    parts.append(text(n1_x + 95, n1_y + 42, "Bitmap: 0x00000082 (2 біти)", size=11, color="#3b82f6"))
    parts.append(rect(n1_x + 25, n1_y + 48, 65, 14, fill="#ffffff", stroke="#93c5fd", sw=1, rx=2))
    parts.append(text(n1_x + 57, n1_y + 59, "P0 (біт 1)", size=9, color="#1e40af"))
    parts.append(rect(n1_x + 100, n1_y + 48, 65, 14, fill="#ffffff", stroke="#93c5fd", sw=1, rx=2))
    parts.append(text(n1_x + 132, n1_y + 59, "P1 (біт 7)", size=9, color="#1e40af"))

    # Leaf Nodes
    # Leaf 1 (direct from Root P0)
    l1_x, l1_y = 100, 230
    parts.append(rect(l1_x, l1_y, 170, 55, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(l1_x + 85, l1_y + 22, "Лист A (Key-Value)", size=12, color="#15803d", bold=True))
    parts.append(text(l1_x + 85, l1_y + 42, 'Ключ: "alpha" → Знач: 42', size=11, color="#166534"))

    # Leaf 2 (from Level 1 P0)
    l2_x, l2_y = 350, 340
    parts.append(rect(l2_x, l2_y, 170, 55, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(l2_x + 85, l2_y + 22, "Лист B (Key-Value)", size=12, color="#15803d", bold=True))
    parts.append(text(l2_x + 85, l2_y + 42, 'Ключ: "beta" → Знач: 99', size=11, color="#166534"))

    # Leaf 3 (from Level 1 P1)
    l3_x, l3_y = 560, 340
    parts.append(rect(l3_x, l3_y, 190, 55, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    parts.append(text(l3_x + 95, l3_y + 22, "Лист C (Колізійний кошик)", size=12, color="#991b1b", bold=True))
    parts.append(text(l3_x + 95, l3_y + 42, "Збіг хешів: [K1:V1, K2:V2]", size=11, color="#b91c1c"))

    # Connectors
    parts.append(arrow(rx + 50, ry + 62, l1_x + 85, l1_y, color="#2563eb", sw=1.8))
    parts.append(arrow(rx + 130, ry + 62, n1_x + 95, n1_y, color="#2563eb", sw=1.8))
    parts.append(arrow(n1_x + 57, n1_y + 62, l2_x + 85, l2_y, color="#2563eb", sw=1.8))
    parts.append(arrow(n1_x + 132, n1_y + 62, l3_x + 95, l3_y, color="#2563eb", sw=1.8))

    render(os.path.join(OUT, "trie-structure.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Персистентність та копіювання шляху (Path Copying)
# ─────────────────────────────────────────────────────────────────────────────
def fig_path_copying():
    W, H = 840, 460
    parts = []

    parts.append(rect(20, 20, 800, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 48, "Персистентність HAMT через копіювання шляху (Path Copying)", size=16, color=INK, bold=True))
    parts.append(text(420, 72, "При вставці або оновленні створюються копії лише вузлів уздовж шляху. Незмінні піддерева перевикористовуються.", size=13, color=MUTED))

    # Left Tree (Version 1)
    parts.append(text(230, 110, "Версія 1 (початкова)", size=14, color="#475569", bold=True))

    r1_x, r1_y = 170, 130
    parts.append(rect(r1_x, r1_y, 120, 45, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(r1_x + 60, r1_y + 26, "Корінь V1", size=12, color="#334155", bold=True))

    # V1 Left Child (Shared)
    s_x, s_y = 80, 230
    parts.append(rect(s_x, s_y, 130, 50, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=6))
    parts.append(text(s_x + 65, s_y + 22, "Піддерево A", size=12, color="#15803d", bold=True))
    parts.append(text(s_x + 65, s_y + 40, "♻️ Перевикористано", size=10, color="#166534"))

    # V1 Right Child (Original)
    n1_x, n1_y = 250, 230
    parts.append(rect(n1_x, n1_y, 110, 45, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(n1_x + 55, n1_y + 26, "Вузол B (V1)", size=12, color="#334155"))

    l1_x, l1_y = 250, 330
    parts.append(rect(l1_x, l1_y, 110, 45, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(l1_x + 55, l1_y + 26, 'Лист: "x"=10', size=12, color="#334155"))

    parts.append(arrow(r1_x + 30, r1_y + 45, s_x + 65, s_y, color="#64748b", sw=1.5))
    parts.append(arrow(r1_x + 90, r1_y + 45, n1_x + 55, n1_y, color="#64748b", sw=1.5))
    parts.append(arrow(n1_x + 55, n1_y + 45, l1_x + 55, l1_y, color="#64748b", sw=1.5))

    # Divider line
    parts.append(line(420, 100, 420, 410, color="#cbd5e1", sw=1, dash="4 4"))

    # Right Tree (Version 2)
    parts.append(text(610, 110, "Версія 2 (після оновлення \"x\"=42)", size=14, color="#2563eb", bold=True))

    r2_x, r2_y = 550, 130
    parts.append(rect(r2_x, r2_y, 120, 45, fill="#dbeafe", stroke="#2563eb", sw=2, rx=6))
    parts.append(text(r2_x + 60, r2_y + 26, "Корінь V2 ✨", size=12, color="#1e40af", bold=True))

    # V2 points to SAME Shared Subtree A!
    parts.append(arrow(r2_x + 30, r2_y + 45, s_x + 100, s_y, color="#16a34a", sw=2))

    # V2 New Copied Nodes along path
    n2_x, n2_y = 630, 230
    parts.append(rect(n2_x, n2_y, 120, 45, fill="#dbeafe", stroke="#2563eb", sw=2, rx=6))
    parts.append(text(n2_x + 60, n2_y + 26, "Вузол B (V2) ✨", size=12, color="#1e40af", bold=True))

    l2_x, l2_y = 630, 330
    parts.append(rect(l2_x, l2_y, 120, 45, fill="#dbeafe", stroke="#2563eb", sw=2, rx=6))
    parts.append(text(l2_x + 60, l2_y + 26, 'Новий лист: "x"=42', size=11, color="#1e40af", bold=True))

    parts.append(arrow(r2_x + 90, r2_y + 45, n2_x + 60, n2_y, color="#2563eb", sw=2))
    parts.append(arrow(n2_x + 60, n2_y + 45, l2_x + 60, l2_y, color="#2563eb", sw=2))

    render(os.path.join(OUT, "path-copying.svg"), W, H, "\n".join(parts))


if __name__ == "__main__":
    fig_hamt_indexing()
    fig_trie_structure()
    fig_path_copying()
    print("Всі 3 фігури HAMT успішно згенеровано.")
