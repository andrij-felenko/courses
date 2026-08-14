# -*- coding: utf-8 -*-
import sys
import os

# Скрипт лежить у book/algorithms/data-structures/write-amplification/
# Шлях до scripts/ — чотири рівні вгору:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')

def make_waf_concept():
    w, h = 800, 380
    frags = []
    
    # Блок ліворуч: Host (Застосунок)
    b1 = fitbox(40, 60, 200, 100, "Застосунок / Хост\n(Host Write)\n4 KB Data", fill="#eaf0fd", stroke=NEG, size=13, bold=True)
    frags.append(b1)
    
    # Стрілка від Хоста до Драйвера / Сховища
    frags.append(arrow(240, 110, 310, 110, color=NEG, sw=2))
    frags.append(text(275, 95, "Логічний запис", size=11, color=NEG, italic=True))
    
    # Блок по центру: Система зберігання (DB Engine / FTL Controller)
    b2 = fitbox(310, 60, 220, 120, "Система зберігання\n(FTL / LSM Compaction / WAL)\nМноження записів", fill="#fbf2e9", stroke="#e67e22", size=13, bold=True)
    frags.append(b2)
    
    # Стрілки від системи до Фізичного носія
    frags.append(arrow(530, 90, 600, 70, color=POS, sw=2))
    frags.append(arrow(530, 110, 600, 110, color=POS, sw=2))
    frags.append(arrow(530, 130, 600, 150, color=POS, sw=2))
    
    # Блок праворуч: Physical Storage (NAND / NVMe / Disk)
    b3 = fitbox(600, 50, 160, 140, "Фізичний носій\n(NAND Flash / Disk)\n16 KB WAL + 20 KB GC\n= 36 KB Physical Write", fill="#fdecea", stroke=POS, size=12, bold=True)
    frags.append(b3)
    
    # Нижня частина: Формула та розшифровка WAF
    b_formula = fitbox(80, 230, 640, 110, "Формула підсилення запису (Write Amplification Factor):\n\nWAF = (Фізичний обсяг запису на носій) / (Логічний обсяг запису від хоста)\n\nПриклад: WAF = 36 KB / 4 KB = 9.0 (на 1 KB даних пишеться 9 KB на диск)", fill="#f4f6f8", stroke=LINE, size=13, bold=True)
    frags.append(b_formula)
    
    path = os.path.join(OUT_DIR, "waf-concept.svg")
    render(path, w, h, *frags, title="Концепція підсилення запису (Write Amplification Factor)")

def make_ftl_gc_amplification():
    w, h = 820, 420
    frags = []
    
    # Блок 1: Джерельний блок з живими й застарілими сторінками
    frags.append(text(180, 55, "Блок джерела A (Erase Block)", size=13, bold=True, color=INK))
    
    # 4 сторінки в блоці A
    frags.append(fitbox(60, 80, 240, 40, "Сторінка 1: Валідні дані X", fill="#e8f8f5", stroke=FIELD, size=11))
    frags.append(fitbox(60, 130, 240, 40, "Сторінка 2: ЗАСТАРІЛІ дані", fill="#fef9e7", stroke=MUTED, size=11))
    frags.append(fitbox(60, 180, 240, 40, "Сторінка 3: Валідні дані Y", fill="#e8f8f5", stroke=FIELD, size=11))
    frags.append(fitbox(60, 230, 240, 40, "Сторінка 4: ЗАСТАРІЛІ дані", fill="#fef9e7", stroke=MUTED, size=11))
    
    # Стрілка зчитування живих сторінок в RAM / GC Buffer
    frags.append(arrow(300, 100, 380, 140, color=FIELD, sw=2))
    frags.append(arrow(300, 200, 380, 160, color=FIELD, sw=2))
    
    # Блок контролера FTL / RAM буфер
    frags.append(fitbox(380, 110, 160, 80, "Буфер FTL GC\nКопіювання лише\nвалідних (X, Y)", fill="#eaf0fd", stroke=NEG, size=12, bold=True))
    
    # Стрілка запису з буфера в новий блок B
    frags.append(arrow(540, 150, 600, 150, color=NEG, sw=2))
    
    # Блок 2: Цільовий блок B
    frags.append(text(690, 55, "Приймач Блок B", size=13, bold=True, color=INK))
    frags.append(fitbox(590, 80, 200, 40, "Сторінка 1: Валідні X", fill="#e8f8f5", stroke=FIELD, size=11))
    frags.append(fitbox(590, 130, 200, 40, "Сторінка 2: Валідні Y", fill="#e8f8f5", stroke=FIELD, size=11))
    frags.append(fitbox(590, 180, 200, 40, "Сторінка 3: Нові дані Z", fill="#fdecea", stroke=POS, size=11))
    frags.append(fitbox(590, 230, 200, 40, "Сторінка 4: Вільна", fill="#ffffff", stroke=MUTED, size=11))
    
    # Підпис стирання блоку A
    frags.append(arrow(180, 280, 180, 320, color=POS, sw=2))
    frags.append(fitbox(80, 330, 200, 50, "Очищення Блоку A\nPHYSICAL ERASE (BLOCK)", fill="#fdecea", stroke=POS, size=11, bold=True))
    
    # Текстове пояснення WAF
    frags.append(fitbox(330, 330, 460, 55, "Ампліфікація в FTL:\nЗапис 1 нової сторінки (Z) вимагає перенесення 2 живих (X,Y) + стирання блоку.\nWAF = (2 перенесені + 1 нова) / 1 нова = 3.0", fill="#f4f6f8", stroke=LINE, size=11))
    
    path = os.path.join(OUT_DIR, "ftl-gc-amplification.svg")
    render(path, w, h, *frags, title="Механізм збирання сміття (Garbage Collection) у FTL")

def make_lsm_compaction_waf():
    w, h = 820, 400
    frags = []
    
    # LSM рівні
    frags.append(fitbox(40, 60, 140, 50, "MemTable (RAM)\nЗапис: WAF = 0", fill="#eaf0fd", stroke=NEG, size=11, bold=True))
    frags.append(arrow(180, 85, 230, 85, color=NEG, sw=2))
    
    frags.append(fitbox(230, 60, 150, 50, "L0 SSTables (Disk)\nFlush з RAM", fill="#e8f8f5", stroke=FIELD, size=11, bold=True))
    frags.append(arrow(380, 85, 430, 85, color=FIELD, sw=2))
    
    frags.append(fitbox(430, 60, 160, 50, "L1 SSTables (10 MB)\nLeveled Compaction", fill="#fbf2e9", stroke="#e67e22", size=11, bold=True))
    frags.append(arrow(590, 85, 640, 85, color="#e67e22", sw=2))
    
    frags.append(fitbox(640, 60, 150, 50, "L2 SSTables (100 MB)\nДалі L3... LN", fill="#fdecea", stroke=POS, size=11, bold=True))
    
    # Пояснювальна схема перекриття та злиття
    b_merge = fitbox(60, 150, 700, 110, "Процес Leveled Compaction між L1 та L2:\n\n1. Вибір 1 SSTable з L1 (наприклад, 10 MB).\n2. Пошук перекритих за ключами SSTables в L2 (типово 10 SSTables по 10 MB = 100 MB).\n3. Зчитування 110 MB -> Сортування й злиття (Merge Sort) -> Запис 110 MB нових SSTables у L2.\n\nWAF для 1 рівня Compaction ≈ 10x. Для L рівнів WAF ≈ L × T.", fill="#f4f6f8", stroke=LINE, size=12)
    frags.append(b_merge)
    
    b_summary = fitbox(120, 285, 580, 80, "Порівняння підходів WAF:\n- B-Tree (In-place): WAF високий при випадковому записі (Random IO), малий при послідовному.\n- LSM-Tree (Leveled): WAF передбачуваний L × T (типово 10..30), оптимізований для запису.\n- LSM-Tree (Size-Tiered): WAF менший (4..8), але висока ампліфікація простору (Space Amplification).", fill="#ffffff", stroke=MUTED, size=11)
    frags.append(b_summary)
    
    path = os.path.join(OUT_DIR, "lsm-compaction-waf.svg")
    render(path, w, h, *frags, title="Підсилення запису при ущільненні (Compaction) у LSM-дереві")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    make_waf_concept()
    make_ftl_gc_amplification()
    make_lsm_compaction_waf()
    print("Figures generated successfully in", OUT_DIR)

if __name__ == "__main__":
    main()
