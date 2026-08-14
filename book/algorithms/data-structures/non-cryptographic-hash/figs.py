# -*- coding: utf-8 -*-
"""Фігури до статті «Некриптографічні хеш-функції».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Конвеєр обробки в сучасній некриптографічній хеш-функції ───────
def fig_hash_pipeline():
    w, h = 920, 420
    parts = []
    parts.append(text(w / 2, 32, "Конвеєр обробки некриптографічної хеш-функції (MurmurHash / xxHash)", size=17, bold=True))
    
    # Вхідні дані
    parts.append(fitbox(40, 75, 140, 50, "Вхідний блок\n(ключ + len)", fill="#eaf0fd", stroke=LINE, bold=True, size=13))
    parts.append(fitbox(40, 155, 140, 45, "Затравка\n(Seed)", fill="#fff4e6", stroke="#d97706", bold=True, size=13))
    
    # Фаза 1: Ініціалізація стану
    parts.append(fitbox(220, 90, 170, 120, "1. Ініціалізація стану\n\nh1 = Seed ^ C1\nh2 = Seed ^ C2\n(ILP акумулятори)", fill="#f8fafc", stroke=LINE, size=12))
    
    parts.append(arrow(180, 100, 220, 125, color=LINE, sw=1.5))
    parts.append(arrow(180, 175, 220, 155, color="#d97706", sw=1.5))
    
    # Фаза 2: Основний цикл стиснення
    parts.append(fitbox(430, 70, 220, 180, "2. Цикл стиснення блоків\n\n• Читання 64-біт (SWAR/SIMD)\n• k = Read64(ptr)\n• k *= Prime1\n• k = ROTL(k, r1)\n• k *= Prime2\n• state ^= k; state = ROTL(state, r2)", fill="#e0f2fe", stroke="#0284c7", size=12))
    
    parts.append(arrow(390, 150, 430, 150, color=LINE, sw=1.8))
    
    # Фаза 3: Обробка хвоста та довжини
    parts.append(fitbox(430, 275, 220, 100, "3. Обробка хвоста та length\n\n• Решта 1..7 байтів\n• state ^= TailBytes\n• state ^= total_len", fill="#fef3c7", stroke="#d97706", size=12))
    
    parts.append(arrow(540, 250, 540, 275, color=LINE, sw=1.5))
    
    # Фаза 4: Фіналізатор (Avalanche Mixer)
    parts.append(fitbox(690, 130, 180, 150, "4. Avalanche Mixer\n(fmix64)\n\nh ^= h >> 33\nh *= 0xff51afd7565a1a5\nh ^= h >> 33\nh *= 0xc4ceb9fe1a85ec53\nh ^= h >> 33", fill="#fce7f3", stroke="#db2777", size=11))
    
    parts.append(arrow(650, 160, 690, 185, color=LINE, sw=1.8))
    parts.append(arrow(650, 325, 690, 235, color=LINE, sw=1.8))
    
    # Вихідне значення
    parts.append(fitbox(710, 320, 140, 55, "Вихідний хеш\n64-біт / 128-біт", fill="#dcfce7", stroke="#16a34a", bold=True, size=13))
    parts.append(arrow(780, 280, 780, 320, color="#16a34a", sw=2.0))
    
    render(os.path.join(IMG, 'hash-pipeline.svg'), w, h, *parts)


# ── Фігура 2: Лавинний ефект (Avalanche Effect) ─────────────────────────────
def fig_avalanche_effect():
    w, h = 860, 380
    parts = []
    parts.append(text(w / 2, 30, "Демонстрація лавинного ефекту (Strict Avalanche Criterion)", size=17, bold=True))
    
    # Початковий вхід А і хеш
    parts.append(fitbox(40, 75, 230, 45, "Вхід А:  01001101  01100001", fill="#f1f5f9", stroke=LINE, size=13))
    parts.append(fitbox(340, 75, 480, 45, "Хеш А:  10110100 00111001 11000101 01101010", fill="#e2e8f0", stroke=LINE, size=13))
    parts.append(arrow(270, 97, 340, 97, color=LINE, sw=1.5))
    
    # Вхід Б (інвертовано 1 біт!)
    parts.append(fitbox(40, 155, 230, 45, "Вхід Б:  01001101  01100000", fill="#fff1f2", stroke=POS, size=13, bold=True))
    parts.append(fitbox(340, 155, 480, 45, "Хеш Б:  01001011 10100101 00110110 10010111", fill="#fee2e2", stroke=POS, size=13, bold=True))
    parts.append(arrow(270, 177, 340, 177, color=POS, sw=1.5))
    
    # Пояснення інвертованих бітів
    parts.append(text(150, 133, "Зміна лише 1 біта на вході (0 -> 1)", size=12, color=POS, bold=True))
    parts.append(text(580, 225, "Зміна ~50% бітів у вихідному хеші на випадкові позиції", size=13, color=INK, bold=True))
    
    # Слабкий хеш проти якісного некриптографічного хешу
    parts.append(fitbox(40, 260, 370, 95, "Слабкий хеш (наприклад, sum(bytes)):\n\n• Зміна 1 біта вхідних даних змінює лише 1-2 біти виходу\n• Результат скупчується, колізії високі", fill="#fef2f2", stroke="#ef4444", size=12))
    
    parts.append(fitbox(450, 260, 370, 95, "Якісний хеш (Murmur3 / xxHash / Wyhash):\n\n• Кожен вхідний біт інвертує кожен вихідний біт із P = 50%\n• Проходить тести SMHasher, відсутні масиви колізій", fill="#f0fdf4", stroke="#22c55e", size=12))
    
    render(os.path.join(IMG, 'avalanche-effect.svg'), w, h, *parts)


# ── Фігура 3: Порівняння алгоритмів хешування ─────────────────────────────────
def fig_smhasher_comparison():
    w, h = 880, 440
    parts = []
    parts.append(text(w / 2, 30, "Порівняння некриптографічних та криптографічних хеш-функцій", size=17, bold=True))
    
    algs = [
        ("FNV-1a", 1.2, "#cbd5e1", "Слабка якість, для малих ключів"),
        ("SipHash-2-4", 2.1, "#fde68a", "Захист від HashDoS, сервіси web"),
        ("MurmurHash3", 4.5, "#93c5fd", "Стандарт де-факто для хеш-таблиць"),
        ("CityHash64", 10.5, "#a7f3d0", "Оптимізовано під Out-of-Order CPU"),
        ("Wyhash", 16.0, "#6ee7b7", "Швидкий на коротких і довгих ключах"),
        ("XXH3 (xxHash)", 24.0, "#34d399", "Надшвидкий (SIMD AVX2/AVX-512)"),
        ("SHA-256", 0.4, "#fca5a5", "Криптографічний (надто повільний для map)")
    ]
    
    start_y = 70
    bar_h = 36
    max_val = 26.0
    chart_w = 460
    
    parts.append(text(20, start_y - 10, "Алгоритм", size=13, bold=True, anchor="start"))
    parts.append(text(200 + chart_w / 2, start_y - 10, "Пропускна здатність (Гбайт/с на CPU RAM/L1)", size=13, bold=True))
    
    for i, (name, val, col, desc) in enumerate(algs):
        y = start_y + i * (bar_h + 12)
        bw = (val / max_val) * chart_w
        
        parts.append(text(140, y + bar_h / 2 + 4, name, size=13, bold=True, anchor="end"))
        parts.append(rect(150, y, bw, bar_h, fill=col, stroke=LINE, rx=4))
        parts.append(text(160 + bw, y + bar_h / 2 + 4, f"{val} GB/s", size=12, bold=True, anchor="start"))
        parts.append(text(640, y + bar_h / 2 + 4, desc, size=11, color=MUTED, anchor="start"))
    
    render(os.path.join(IMG, 'smhasher-comparison.svg'), w, h, *parts)


if __name__ == '__main__':
    fig_hash_pipeline()
    fig_avalanche_effect()
    fig_smhasher_comparison()
    print("Фігури згенеровано успішно.")
