# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F   = "#e8eefc"
RED_F    = "#fdecea"
GREEN_F  = "#e6f7ee"
PURPLE_F = "#f3e8fa"
YELLOW_F = "#fffde6"

def fig_sieve_cache_bottleneck():
    W, H = 1000, 480
    elements = []

    # Title
    elements.append(text(W / 2, 35, "Порівняння локальності даних: класичне vs сегментоване решето", size=17, color=INK, bold=True))

    # Panel 1: Classical Sieve (Left)
    elements.append(fitbox(40, 65, 440, 360, "", fill=RED_F, stroke=NEG, sw=2, rx=8))
    elements.append(text(260, 95, "Класичне решето Ератосфена", size=16, color=NEG, bold=True))
    elements.append(text(260, 120, "Масив розміром O(N) у DRAM (наприклад, 1–8 ГБ)", size=13.5, color=INK))

    # Big DRAM array visualization
    elements.append(fitbox(60, 145, 400, 50, "Суцільний масив is_prime[0 .. N]", size=13, fill=FILL, stroke=MUTED, sw=1.5, bold=True, color=INK))
    
    # Strided access arrows skipping across memory
    elements.append(fitbox(70, 215, 60, 35, "i = p", size=12, fill=YELLOW_F, stroke=NEG, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(170, 215, 60, 35, "i = 2p", size=12, fill=YELLOW_F, stroke=NEG, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(270, 215, 60, 35, "i = 3p", size=12, fill=YELLOW_F, stroke=NEG, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(370, 215, 60, 35, "i = 4p", size=12, fill=YELLOW_F, stroke=NEG, sw=1.5, bold=True, color=INK))

    elements.append(arrow(130, 232, 170, 232, color=NEG, sw=2))
    elements.append(arrow(230, 232, 270, 232, color=NEG, sw=2))
    elements.append(arrow(330, 232, 370, 232, color=NEG, sw=2))

    elements.append(fitbox(60, 270, 400, 65, "Кроковий стрибок p перевищує розмір L1/L2 кешу.\nКожен крок спричиняє Cache Miss і затримку DRAM (100+ нс).\nCPU застопорюється (Stall) в очікуванні пам'яті.", size=12.5, fill=RED_F, stroke=NEG, sw=1.2, color=NEG))
    elements.append(fitbox(60, 350, 400, 55, "Пам'ять: O(N) | Кроків: O(N log log N)\nКеш-промахи: O(N log log N)", size=13, fill=FILL, stroke=NEG, sw=1.8, bold=True, color=NEG))

    # Panel 2: Segmented Sieve (Right)
    elements.append(fitbox(520, 65, 440, 360, "", fill=GREEN_F, stroke=POS, sw=2, rx=8))
    elements.append(text(740, 95, "Сегментоване решето (Cache-Aware)", size=16, color=POS, bold=True))
    elements.append(text(740, 120, "Обробка блоками розміром S ≈ 32 KB (L1 Cache)", size=13.5, color=INK))

    # Base primes
    elements.append(fitbox(540, 145, 400, 40, "Базові прості числа до √N (у L2 кеші)", size=13, fill=BLUE_F, stroke=FIELD, sw=1.5, bold=True, color=INK))

    # Active Segment inside L1 Cache
    elements.append(fitbox(540, 200, 400, 55, "Сегмент [L, R] розміром S\n(Займає 32 KB — 100% L1 Cache Hit!)", size=13.5, fill=YELLOW_F, stroke=POS, sw=2, bold=True, color=POS))

    elements.append(fitbox(540, 270, 400, 65, "Викреслювання виконується виключно в межах 32 KB.\nНуль звернень до DRAM під час просіювання сегмента.\nЗатримка доступу: 1–2 нс (L1 Cache speed).", size=12.5, fill=GREEN_F, stroke=POS, sw=1.2, color=POS))
    elements.append(fitbox(540, 350, 400, 55, "Пам'ять: O(√N + S) | Кроків: O(N log log N)\nКеш-промахи: O(N / S)", size=13, fill=FILL, stroke=POS, sw=1.8, bold=True, color=POS))

    # Bottom summary box
    elements.append(fitbox(40, 435, 920, 35, "Результат: При однаковій кількості арифметичних дій сегментоване решето працює у 5–20 разів швидше за рахунок кеш-локальності!", size=13.5, fill=PURPLE_F, stroke=MUTED, sw=1.5, bold=True, color=INK))

    return render(os.path.join(OUT, "sieve-cache-bottleneck.svg"), W, H, *elements,
                  title="Порівняння локальності даних: класичне vs сегментоване решето")

def fig_segment_mapping():
    W, H = 1000, 460
    elements = []

    elements.append(text(W / 2, 35, "Механізм відносного адресування та пошуку першого кратного у блоці", size=17, color=INK, bold=True))

    # Global Range Bar [L, R]
    elements.append(fitbox(50, 70, 900, 50, "Глобальний інтервал [L, R]  (наприклад, L = 100, R = 150, S = 51)", size=15, fill=BLUE_F, stroke=FIELD, sw=2, bold=True, color=INK))

    # Base Prime p
    elements.append(fitbox(50, 140, 260, 45, "Базове просте число: p = 7", size=14, fill=PURPLE_F, stroke=MUTED, sw=1.8, bold=True, color=INK))

    # Formula Box
    elements.append(fitbox(330, 140, 620, 45, "Перше кратне p у [L, R]:  start = max(p², ⌈L / p⌉ · p) = max(49, 15 · 7) = 105", size=13.5, fill=YELLOW_F, stroke=NEG, sw=1.8, bold=True, color=INK))

    # Local Array mark[0 .. S-1]
    elements.append(fitbox(50, 210, 900, 120, "", fill=GREEN_F, stroke=POS, sw=2, rx=8))
    elements.append(text(500, 235, "Локальний булевий масив mark[0 .. S-1] (розмір S = R - L + 1)", size=15, color=POS, bold=True))

    # Array elements illustration
    x_positions = [80, 220, 360, 500, 640, 780]
    labels_global = ["100 (L)", "105 (start)", "112 (start+p)", "119 (start+2p)", "126 (start+3p)", "150 (R)"]
    labels_local  = ["idx = 0", "idx = 5", "idx = 12", "idx = 19", "idx = 26", "idx = 50"]
    status        = ["ПРОСТЕ", "СКЛАДЕНЕ", "СКЛАДЕНЕ", "СКЛАДЕНЕ", "СКЛАДЕНЕ", "ПРОСТЕ"]
    colors        = [POS, NEG, NEG, NEG, NEG, POS]

    for idx in range(len(x_positions)):
        xp = x_positions[idx]
        elements.append(fitbox(xp, 255, 120, 60, f"{labels_global[idx]}\n{labels_local[idx]}\n{status[idx]}", size=11.5, fill=FILL, stroke=colors[idx], sw=1.6, bold=True, color=colors[idx]))

    # Mapping Arrow formula
    elements.append(fitbox(50, 350, 900, 40, "Формула адресації у локальному масиві:  local_index = X - L   ⇒   mark[X - L] = false", size=14, fill=BLUE_F, stroke=FIELD, sw=1.8, bold=True, color=INK))

    # Bottom note
    elements.append(fitbox(50, 405, 900, 35, "Для кожного базового простого p викреслюємо елементи з кроком p: local_idx = (start - L), (start - L + p), (start - L + 2p)...", size=13, fill=PURPLE_F, stroke=MUTED, sw=1.5, color=INK))

    return render(os.path.join(OUT, "segment-mapping.svg"), W, H, *elements,
                  title="Механізм відносного адресування у сегментованому решетові")

def fig_wheel_factorization():
    W, H = 1000, 470
    elements = []

    elements.append(text(W / 2, 35, "Оптимізація колесом факторів Modulo 30 (Wheel 30)", size=17, color=INK, bold=True))

    elements.append(fitbox(50, 65, 900, 45, "З кожних 30 послідовних чисел лише 8 не діляться на 2, 3 та 5 (22 числа відсіюються автоматично)", size=14, fill=YELLOW_F, stroke=MUTED, sw=1.8, bold=True, color=INK))

    # Coprime residues mod 30
    coprimes = [1, 7, 11, 13, 17, 19, 23, 29]
    elements.append(text(500, 135, "8 взаємно простих остач за модулем 30 (кандидати у прості):", size=14, color=INK, bold=True))

    start_x = 70
    box_w = 100
    gap = 10
    for idx, c in enumerate(coprimes):
        bx = start_x + idx * (box_w + gap)
        elements.append(fitbox(bx, 150, box_w, 45, f"r = {c}", size=14, fill=GREEN_F, stroke=POS, sw=2, bold=True, color=POS))

    # Skipped residues panel
    elements.append(fitbox(50, 215, 900, 110, "", fill=RED_F, stroke=NEG, sw=1.8, rx=8))
    elements.append(text(500, 240, "22 виключені остачі за модулем 30 (відсіяні на етапі структури даних):", size=14, color=NEG, bold=True))
    elements.append(text(500, 270, "Кратні 2 (15 чисел): 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28\nКратні 3 (додатково 5 чисел): 3, 9, 15, 21, 27\nКратні 5 (додатково 2 числа): 5, 25", size=13, color=INK))

    # Statistics comparison
    elements.append(fitbox(50, 345, 435, 60, "Стандартне бітове решето:\n1 біт на кожне непарне число (15 біт / 30 чисел)\nРозмір масиву: 50% від N", size=13, fill=BLUE_F, stroke=FIELD, sw=1.5, bold=True, color=INK))
    elements.append(fitbox(515, 345, 435, 60, "Решето з колесом Modulo 30:\n8 біт на кожний блок із 30 чисел (1 байт / 30 чисел)\nРозмір масиву: 26.6% від N  (зменшення у 3.75 рази!)", size=13, fill=GREEN_F, stroke=POS, sw=2, bold=True, color=POS))

    # Bottom summary
    elements.append(fitbox(50, 420, 900, 35, "Колесо факторів прискорює просіювання та зменшує обсяг пам'яті сегмента, дозволяючи вмістити ще більший інтервал у L1 кеш!", size=13, fill=PURPLE_F, stroke=MUTED, sw=1.5, bold=True, color=INK))

    return render(os.path.join(OUT, "wheel-factorization.svg"), W, H, *elements,
                  title="Оптимізація колесом факторів Modulo 30")

if __name__ == "__main__":
    fig_sieve_cache_bottleneck()
    fig_segment_mapping()
    fig_wheel_factorization()
    print("All figures generated successfully.")
