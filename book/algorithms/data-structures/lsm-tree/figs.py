# -*- coding: utf-8 -*-
"""Фігури до статті «B-tree vs LSM-tree / log-structured».
Запуск із теки теми: python figs.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GOOD = FIELD      # зелений — сильна сторона / послідовний запис
WEAK = POS        # червоний — слабка сторона / довільний запис
HL   = "#e9f8ef"  # світло-зелена заливка виділеного
HL_BLUE = "#eef4ff" # світло-синя заливка
ACCENT_BLUE = "#3b82f6"

def box(x, y, w, h, s, size=13, fill=FILL, stroke=LINE, sw=1.5, bold=False, color=INK):
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw) + \
           text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, bold=bold, color=color)

# ── Фіг. 1: B-tree vs LSM-tree: довільний запис проти послідовного ────────────
def fig_btree_vs_lsm():
    W, H = 960, 440
    parts = [text(W / 2, 28, "Парадигми оновлення даних: in-place в B-tree проти append-only в LSM-tree", size=16, bold=True)]

    # Ліва панель: B-tree (In-place update)
    parts.append(rect(20, 50, 445, 370, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(242, 78, "B-tree (Оновлення на місці / In-place)", size=14, bold=True, color=INK))
    parts.append(text(242, 98, "Випадковий модифікуючий запис у 4 KB сторінки", size=12, color=MUTED))

    # B-tree вузли в RAM
    parts.append(rect(142, 115, 200, 36, fill=FILL, stroke=LINE, sw=1.5))
    parts.append(text(242, 137, "Корінь B-дерева в RAM", size=12, bold=True))

    # Дискові сторінки B-дерева
    parts.append(rect(40, 205, 405, 115, fill="#fafafa", stroke=MUTED, sw=1))
    parts.append(text(242, 222, "Файл БД на диску (випадково розташовані сторінки)", size=11, color=MUTED))

    pages = [("Сторінка A", 55), ("Сторінка B", 150), ("Сторінка C", 245), ("Сторінка D", 340)]
    for idx, (pname, px) in enumerate(pages):
        hit = (idx == 1 or idx == 3)
        parts.append(rect(px, 240, 80, 50, fill="#ffebee" if hit else FILL, stroke=WEAK if hit else LINE, sw=2 if hit else 1.5))
        parts.append(text(px + 40, 260, pname, size=11, bold=hit, color=WEAK if hit else INK))
        parts.append(text(px + 40, 276, "4 KB", size=10, color=MUTED))

    # Стрілки запису в B-tree (вертикальні прямі)
    parts.append(arrow(190, 151, 190, 240, color=WEAK, sw=1.8))
    parts.append(arrow(380, 151, 380, 240, color=WEAK, sw=1.8))
    parts.append(text(285, 163, "Випадкові I/O виклики", size=10.5, color=WEAK, bold=True))
    parts.append(text(285, 189, "(Seek / FTL Wear)", size=9.5, color=WEAK, bold=True))

    parts.append(fitbox(40, 335, 405, 70, 
                        "Властивість: читання O(log N) дуже швидке.\nНедолік: кожен новий або змінений запис переписує цілу 4 KB сторінку\nна диску -> високий WAF та знос накопичувача.",
                        size=11, fill=BG, stroke="none", color=INK))

    # Права панель: LSM-tree (Append-only)
    parts.append(rect(495, 50, 445, 370, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(717, 78, "LSM-tree (Журнально-пакетний / Append-only)", size=14, bold=True, color=INK))
    parts.append(text(717, 98, "Послідовний запис буфера у впорядковані файли", size=12, color=MUTED))

    # MemTable у RAM
    parts.append(rect(545, 120, 160, 45, fill=HL, stroke=GOOD, sw=2))
    parts.append(text(625, 140, "MemTable (RAM)", size=12, bold=True, color=GOOD))
    parts.append(text(625, 156, "Сортований буфер", size=10, color=MUTED))

    # WAL у RAM/диску
    parts.append(rect(745, 120, 160, 45, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
    parts.append(text(825, 140, "WAL (Журнал)", size=12, bold=True, color=ACCENT_BLUE))
    parts.append(text(825, 156, "Послідовний допис", size=10, color=MUTED))

    # Стрілка скидання на диск
    parts.append(arrow(625, 165, 625, 235, color=GOOD, sw=2))
    parts.append(text(695, 200, "Flush (Flush кран)", size=11, color=GOOD, bold=True))

    # SSTable дисковий шар
    parts.append(rect(515, 235, 405, 80, fill="#f1f8e9", stroke=GOOD, sw=1.5))
    parts.append(text(717, 252, "Диск: SSTables (Неперервні відсортовані блоки)", size=11, bold=True, color=GOOD))

    ssts = [("SST 1 (L0)", 530), ("SST 2 (L0)", 630), ("SST 3 (L1)", 730), ("SST 4 (L1)", 830)]
    for sname, sx in ssts:
        parts.append(rect(sx, 265, 80, 40, fill=FILL, stroke=GOOD, sw=1.5))
        parts.append(text(sx + 40, 285, sname, size=10, bold=True, color=INK))

    parts.append(fitbox(515, 335, 405, 70,
                        "Властивість: записи накопичуються в RAM і скидаються на диск\nєдиним послідовним потоком. Максимальна швидкість запису,\nнуль випадкового перезапису.",
                        size=11, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, "b-tree-vs-lsm-model.svg"), W, H, *parts)
    print("Generated b-tree-vs-lsm-model.svg")


# ── Фіг. 2: Архітектура LSM-tree: Write Path та Read Path ────────────────────
def fig_lsm_architecture():
    W, H = 960, 520
    parts = [text(W / 2, 28, "Архітектурні шляхи LSM-дерева: запис (Write Path) та пошук (Read Path)", size=16, bold=True)]

    # Оперативна пам'ять (RAM)
    parts.append(rect(20, 55, 920, 155, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    parts.append(text(80, 78, "ОПЕРАТИВНА ПАМ'ЯТЬ (RAM)", size=12, bold=True, color=MUTED))

    # Клієнтський запит
    parts.append(rect(40, 100, 130, 45, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
    parts.append(text(105, 120, "Запит Клієнта", size=12, bold=True, color=ACCENT_BLUE))
    parts.append(text(105, 136, "PUT(key, val)", size=10, color=MUTED))

    # WAL
    parts.append(rect(230, 100, 150, 45, fill="#fff3e0", stroke="#ff9800", sw=1.5))
    parts.append(text(305, 120, "WAL на диску", size=12, bold=True, color="#e65100"))
    parts.append(text(305, 136, "Append-only log", size=10, color=MUTED))

    # Active MemTable
    parts.append(rect(430, 90, 170, 55, fill=HL, stroke=GOOD, sw=2))
    parts.append(text(515, 112, "Active MemTable", size=13, bold=True, color=GOOD))
    parts.append(text(515, 130, "SkipList / Red-Black", size=10, color=MUTED))

    # Immutable MemTable
    parts.append(rect(640, 90, 170, 55, fill="#e8f5e9", stroke=GOOD, sw=1.5))
    parts.append(text(725, 112, "Immutable MemTable", size=12, bold=True, color=GOOD))
    parts.append(text(725, 130, "Готовий до скидання", size=10, color=MUTED))

    # Стрілки запису
    parts.append(arrow(170, 122, 230, 122, color=ACCENT_BLUE, sw=2))
    parts.append(arrow(380, 122, 430, 122, color=GOOD, sw=2))
    parts.append(arrow(600, 117, 640, 117, color=GOOD, sw=1.8))
    parts.append(text(620, 105, "Заповнено", size=9, color=MUTED))

    # Потік скидання на диск (Flush)
    parts.append(arrow(725, 145, 725, 230, color=GOOD, sw=2))
    parts.append(text(790, 185, "Flush (Послідовний сортований дамп)", size=11, bold=True, color=GOOD))

    # Накопичувач (Disk / SSD)
    parts.append(rect(20, 230, 920, 270, fill="#fafafa", stroke=MUTED, sw=1.2))
    parts.append(text(120, 252, "НАКОПИЧУВАЧ (SSD / HDD) — SSTables", size=12, bold=True, color=MUTED))

    # Рівні Compaction (L0, L1, L2)
    # L0
    parts.append(rect(40, 275, 880, 60, fill=FILL, stroke=LINE, sw=1.5))
    parts.append(text(90, 305, "Рівень 0 (L0):", size=12, bold=True))
    parts.append(text(90, 320, "Діапазони перетинаються", size=9, color=MUTED))
    l0_files = [("SST 1 (k: 1..50)", 220), ("SST 2 (k: 10..80)", 420), ("SST 3 (k: 5..60)", 620)]
    for fname, fx in l0_files:
        parts.append(rect(fx, 285, 170, 40, fill="#fff8e1", stroke="#ffa000", sw=1.5))
        parts.append(text(fx + 85, 305, fname, size=11, bold=True, color=INK))

    # Стрілка Compaction від L0 до L1
    parts.append(arrow(505, 335, 505, 375, color=WEAK, sw=2))
    parts.append(text(585, 355, "Compaction (Злиття та впорядкування)", size=11, bold=True, color=WEAK))

    # L1
    parts.append(rect(40, 375, 880, 60, fill=FILL, stroke=LINE, sw=1.5))
    parts.append(text(90, 405, "Рівень 1 (L1):", size=12, bold=True))
    parts.append(text(90, 420, "Неперетинні діапазони", size=9, color=MUTED))
    l1_files = [("SST A (k: 1..30)", 220), ("SST B (k: 31..60)", 420), ("SST C (k: 61..90)", 620)]
    for fname, fx in l1_files:
        parts.append(rect(fx, 385, 170, 40, fill=HL, stroke=GOOD, sw=1.5))
        parts.append(text(fx + 85, 405, fname, size=11, bold=True, color=INK))

    # Компоненти пошуку (Read path details)
    parts.append(rect(40, 450, 880, 40, fill="#ede7f6", stroke="#7e57c2", sw=1.5))
    parts.append(text(480, 473, "При читанні GET(key): MemTable -> Bloom Filter (пропускає відсутні SST) -> Index Block -> Data Block", 
                      size=11, bold=True, color="#4527a0"))

    render(os.path.join(OUT, "lsm-architecture.svg"), W, H, *parts)
    print("Generated lsm-architecture.svg")


# ── Фіг. 3: Compaction: Size-Tiered проти Levelled ───────────────────────────
def fig_compaction_strategies():
    W, H = 960, 460
    parts = [text(W / 2, 28, "Стратегії ущільнення (Compaction): Size-Tiered (STCS) проти Levelled (LCS)", size=16, bold=True)]

    # Ліва частина: Size-Tiered Compaction Strategy (STCS)
    parts.append(rect(20, 50, 445, 390, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(242, 78, "Size-Tiered (STCS)", size=14, bold=True, color=INK))
    parts.append(text(242, 98, "Оптимізовано під швидкий запис (Низький WAF)", size=12, color=MUTED))

    # Сейв одинакових за розміром SSTables
    parts.append(text(120, 130, "4 файли подібного розміру:", size=11, bold=True))
    for i in range(4):
        bx = 40 + i * 100
        parts.append(rect(bx, 145, 90, 45, fill="#fff3e0", stroke="#ff9800", sw=1.5))
        parts.append(text(bx + 45, 168, f"SST {i+1} (10 MB)", size=10, bold=True))

    parts.append(arrow(242, 195, 242, 245, color=ACCENT_BLUE, sw=2))
    parts.append(text(340, 220, "Merge-Sort ущільнення", size=11, color=ACCENT_BLUE, bold=True, anchor="start"))

    # 1 великий файл
    parts.append(rect(142, 250, 200, 60, fill="#ffe0b2", stroke="#f57c00", sw=2))
    parts.append(text(242, 275, "1 об'єднаний SSTable (40 MB)", size=12, bold=True, color=INK))

    parts.append(fitbox(40, 325, 405, 100,
                        "Перевага: менше перезаписів під час ущільнення -> низький WAF.\nНедолік: тимчасове подвоєння обсягу (Space Amp до 100%), дублювання ключів у файлах однієї ваговій категорії -> високий Read Amp.",
                        size=11, fill=BG, stroke="none", color=INK))

    # Права частина: Levelled Compaction Strategy (LCS)
    parts.append(rect(495, 50, 445, 390, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(717, 78, "Levelled (LCS)", size=14, bold=True, color=INK))
    parts.append(text(717, 98, "Оптимізовано під точкове читання та економію диска", size=12, color=MUTED))

    # Рівень L_i
    parts.append(text(575, 125, "Рівень L_i (10 MB):", size=11, bold=True))
    parts.append(rect(695, 115, 110, 35, fill="#ffebee", stroke=WEAK, sw=2))
    parts.append(text(750, 133, "SST X [10..20]", size=10, bold=True, color=WEAK))

    parts.append(arrow(750, 150, 750, 185, color=WEAK, sw=2))

    # Рівень L_{i+1}
    parts.append(text(575, 205, "Рівень L_{i+1} (100 MB):", size=11, bold=True))
    l1_boxes = [("SST A [1..12]", 510), ("SST B [13..25]", 612), ("SST C [26..40]", 714), ("SST D [41..60]", 816)]
    for bname, bx in l1_boxes:
        hit = (bx == 612 or bx == 510)
        parts.append(rect(bx, 220, 96, 45, fill=HL if hit else FILL, stroke=GOOD if hit else LINE, sw=2 if hit else 1.5))
        parts.append(text(bx + 48, 243, bname, size=9, bold=hit))

    parts.append(fitbox(515, 280, 405, 145,
                        "Перевага: жорсткі неперетинні діапазони на кожному рівні L1..LN -> унікальність ключів, низький Space Amp (~10%), точкове читання робить лише 1 I/O на рівень.\nНедолік: вищий WAF (один файл з L_i переписує ~10 файлів на L_{i+1}).",
                        size=11, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, "compaction-stcs-vs-lcs.svg"), W, H, *parts)
    print("Generated compaction-stcs-vs-lcs.svg")


if __name__ == "__main__":
    fig_btree_vs_lsm()
    fig_lsm_architecture()
    fig_compaction_strategies()
