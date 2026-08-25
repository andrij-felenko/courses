# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Онлайн-алгоритм проти Офлайн-пророка ──────────────────────────────
def fig_online_vs_offline():
    W, H = 880, 360
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Модель прийняття рішень: Онлайн (ALG) vs Офлайн (OPT)", size=16, color=INK, bold=True))

    # Ліва панель: Онлайн-алгоритм
    px1, py1, pw, ph = 40.0, 55.0, 380.0, 240.0
    p.append(rect(px1, py1, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    p.append(text(px1 + pw / 2, py1 + 28, "Онлайн-алгоритм (ALG)", size=15, color=NEG, bold=True))

    # Потік запитів для онлайну
    p.append(text(px1 + 20, py1 + 65, "Потік запитів σ (вхід по одному):", size=13, color=INK, bold=True, anchor="start"))
    
    # Квадратики запитів (3 відомих)
    reqs = ["r₁", "r₂", "r₃"]
    for i, r in enumerate(reqs):
        rx = px1 + 25 + i * 55
        ry = py1 + 80
        p.append(rect(rx, ry, 45, 35, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=5))
        p.append(text(rx + 22.5, ry + 22, r, size=13, color=INK, bold=True))
    
    # Невідоме майбутнє
    fx = px1 + 25 + 3 * 55 + 10
    fy = py1 + 80
    p.append(rect(fx, fy, 110, 35, fill="#fee2e2", stroke="#fca5a5", sw=1.0, rx=5))
    p.append(text(fx + 55, fy + 22, "Майбутнє ?", size=12, color=POS, bold=True))

    # Лінія бар'єра часу
    p.append(line(px1 + 195, py1 + 70, px1 + 195, py1 + 180, color=POS, sw=1.5, dash="4,4"))
    p.append(text(px1 + 195, py1 + 195, "Стіна невідання", size=11, color=POS, italic=True))

    # Опис рішень
    p.append(text(px1 + 20, py1 + 220, "• Приймає рішення негайно та незворотно", size=12, color=INK, anchor="start"))

    # Права панель: Офлайн-пророк (OPT)
    px2, py2 = 460.0, 55.0
    p.append(rect(px2, py2, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    p.append(text(px2 + pw / 2, py2 + 28, "Офлайн-пророк (OPT)", size=15, color=FIELD, bold=True))

    p.append(text(px2 + 20, py2 + 65, "Повна послідовність σ (відома наперед):", size=13, color=INK, bold=True, anchor="start"))
    
    # Квадратики повністю відомих запитів
    all_reqs = ["r₁", "r₂", "r₃", "r₄", "r₅", "..."]
    for i, r in enumerate(all_reqs):
        rx = px2 + 20 + i * 55
        ry = py2 + 80
        p.append(rect(rx, ry, 45, 35, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=5))
        p.append(text(rx + 22.5, ry + 22, r, size=13, color=FIELD, bold=True))

    p.append(text(px2 + 20, py2 + 150, "Глобальне бачення всього часового горизонту", size=12, color=MUTED, anchor="start"))
    p.append(text(px2 + 20, py2 + 180, "Будує математично мінімальну вартість C(OPT, σ)", size=12, color=INK, anchor="start"))
    p.append(text(px2 + 20, py2 + 220, "• Абсолютний бенчмарк для порівняння", size=12, color=INK, anchor="start"))

    # Нижня рамка з формулою c-competitive
    p.append(rect(40, 305, 800, 45, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(440, 332, "Конкурентна умова:  C(ALG, σ) ≤ c · C(OPT, σ) + α   (де c ≥ 1 — коефіцієнт конкурентності)", size=13, color=NEG, bold=True))

    render(os.path.join(OUT, "fig-online-vs-offline.svg"), W, H, *p)


# ── Фіг. 2: Задача про оренду лиж — графік витрат ────────────────────────────
def fig_ski_rental_bounds():
    W, H = 880, 400
    p = []

    p.append(text(W / 2, 26, "Задача про оренду лиж (Ski Rental): Динаміка витрат від кількості днів", size=16, color=INK, bold=True))

    # Графік: вісь X (дні d), вісь Y (вартість C)
    ax, ay = 80.0, 330.0
    gx, gy = 720.0, 260.0

    # Сітка та осі
    p.append(line(ax, ay, ax + gx, ay, color=INK, sw=1.5))
    p.append(line(ax, ay, ax, ay - gy, color=INK, sw=1.5))

    # Стрілки
    p.append(arrow(ax + gx, ay, ax + gx + 15, ay, color=INK, sw=1.5))
    p.append(arrow(ax, ay - gy, ax, ay - gy - 15, color=INK, sw=1.5))

    # Підписи осей
    p.append(text(ax + gx + 25, ay + 4, "Дні d", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(ax - 10, ay - gy - 20, "Вартість C", size=13, color=INK, bold=True))

    # Позначки на осі X: B (день купівлі)
    B_x = ax + 280.0
    p.append(line(B_x, ay, B_x, ay + 6, color=INK, sw=1.2))
    p.append(text(B_x, ay + 22, "B (ціна купівлі)", size=12, color=INK, bold=True))

    # Лінія порогу B на вертикалі
    B_y = ay - 140.0
    p.append(line(ax, B_y, ax + gx, B_y, color="#cbd5e1", sw=1.0, dash="3,3"))
    p.append(text(ax - 10, B_y + 4, "B", size=12, color=INK, anchor="end"))

    # 1. Стратегія: Завжди оренда (C = d) — червона пряма
    p.append(line(ax, ay, ax + 500, ay - 250, color=POS, sw=2.0))
    p.append(text(ax + 420, ay - 220, "Лише оренда: C = d (безкінечна шкода при d >> B)", size=11, color=POS, bold=True, anchor="start"))

    # 2. Оптимум OPT (C = min(d, B)) — зелена лінія (до B йде вгору як d, після B — горизонтально B)
    p.append(line(ax, ay, B_x, B_y, color=FIELD, sw=3.0))
    p.append(line(B_x, B_y, ax + gx, B_y, color=FIELD, sw=3.0))
    p.append(text(ax + gx - 20, B_y - 12, "OPT: min(d, B)", size=12, color=FIELD, bold=True, anchor="end"))

    # 3. Детермінований онлайновий ALG (Оренда B-1 днів, купівля на B-й день)
    # До B-1 вартість d, на день B додається B (стає (B-1) + B = 2B - 1)
    alg_x = ax + 252.0  # (B-1)
    p.append(line(ax, ay, alg_x, ay - 126, color=NEG, sw=2.5, dash="6,3"))
    # Стрибок у точці B
    p.append(line(alg_x, ay - 126, B_x, ay - 266, color=NEG, sw=2.5))
    p.append(line(B_x, ay - 266, ax + gx, ay - 266, color=NEG, sw=2.5))
    p.append(text(ax + gx - 20, ay - 276, "ALG (Break-even): max 2B − 1 (c = 2 − 1/B)", size=12, color=NEG, bold=True, anchor="end"))

    # Пояснювальна точка для найгіршого випадку ALG
    p.append(circle(B_x, ay - 266, 5, fill=NEG, stroke=INK, sw=1.0))
    p.append(text(B_x + 10, ay - 245, "Найгірший випадок: катання припинилося на день B", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig-ski-rental-bounds.svg"), W, H, *p)


# ── Фіг. 3: Пейджинг — змагання алгоритму кешу із супротивником ───────────────
def fig_paging_adversary():
    W, H = 880, 380
    p = []

    p.append(text(W / 2, 26, "Змагання детермінованого кешу (k = 3) із Супротивником (Adversary)", size=16, color=INK, bold=True))

    # Схема кроків 1..4
    steps = [
        {"step": "Крок 1", "req": "Сторінка 4", "cache": ["1", "2", "3"], "evict": "3", "miss": True, "new_cache": ["1", "2", "4"]},
        {"step": "Крок 2", "req": "Сторінка 3", "cache": ["1", "2", "4"], "evict": "2", "miss": True, "new_cache": ["1", "3", "4"]},
        {"step": "Крок 3", "req": "Сторінка 2", "cache": ["1", "3", "4"], "evict": "1", "miss": True, "new_cache": ["2", "3", "4"]},
        {"step": "Крок 4", "req": "Сторінка 1", "cache": ["2", "3", "4"], "evict": "4", "miss": True, "new_cache": ["1", "2", "3"]},
    ]

    box_w = 190.0
    for i, st in enumerate(steps):
        bx = 35.0 + i * 205.0
        by = 65.0
        p.append(rect(bx, by, box_w, 230.0, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=8))
        p.append(text(bx + box_w / 2, by + 22, st["step"], size=14, color=INK, bold=True))
        
        # Запит від супротивника
        p.append(text(bx + 15, by + 50, "Запит:", size=12, color=MUTED, anchor="start"))
        p.append(rect(bx + 65, by + 35, 100, 26, fill="#fee2e2", stroke="#ef4444", sw=1.0, rx=4))
        p.append(text(bx + 115, by + 52, st["req"], size=12, color=POS, bold=True))

        # Стан кешу до
        p.append(text(bx + 15, by + 85, "Кеш до:", size=11, color=MUTED, anchor="start"))
        for c_idx, pg in enumerate(st["cache"]):
            cx = bx + 70 + c_idx * 32
            p.append(rect(cx, by + 72, 28, 22, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=3))
            p.append(text(cx + 14, by + 87, pg, size=11, color=INK))

        # Промах!
        p.append(rect(bx + 20, by + 105, box_w - 40, 24, fill="#fef2f2", stroke="#fca5a5", sw=1.0, rx=4))
        p.append(text(bx + box_w / 2, by + 121, "⚠ Промах (Cache Miss)", size=11, color=POS, bold=True))

        # Вивантаження
        p.append(text(bx + 15, by + 150, "Виванташено: " + st["evict"], size=11, color=POS, anchor="start"))

        # Стан кешу після
        p.append(text(bx + 15, by + 185, "Кеш після:", size=11, color=MUTED, anchor="start"))
        for c_idx, pg in enumerate(st["new_cache"]):
            cx = bx + 70 + c_idx * 32
            p.append(rect(cx, by + 172, 28, 22, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=3))
            p.append(text(cx + 14, by + 187, pg, size=11, color=FIELD))

    # Висновок
    p.append(rect(35, 310, 810, 48, fill="#fff7ed", stroke="#fdba74", sw=1.2, rx=6))
    p.append(text(440, 330, "Результат: Супротивник робить 100% промахів ALG, тоді як OPT вивантажує сторінку з майбутнього і робить лише 1 промах за k запусків!", size=12, color=INK, bold=True))
    p.append(text(440, 348, "Конкурентна межа будь-якого детермінованого кешування: c = k", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "fig-paging-adversary.svg"), W, H, *p)


if __name__ == "__main__":
    fig_online_vs_offline()
    fig_ski_rental_bounds()
    fig_paging_adversary()
    print("SVG diagrams generated successfully in img/")
