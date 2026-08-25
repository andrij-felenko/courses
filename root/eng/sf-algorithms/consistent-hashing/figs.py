# -*- coding: utf-8 -*-
"""Фігури до статті «Консистентне хешування».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color, sw):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (d, color, sw)


# ── Фігура 1: Традиційне хешування проти Консистентного ────────────────────
def fig_traditional_vs_consistent():
    W, H = 960, 520
    parts = []
    
    parts.append(text(W / 2, 28, "Традиційний sharding  hash(k) mod N  проти  Консистентного кільця", size=16, bold=True))
    parts.append(line(W / 2, 50, W / 2, 490, color=MUTED, sw=1, dash="5,5"))
    
    # ── Ліва панель: Традиційний sharding ──
    parts.append(text(240, 60, "Традиційне: hash(k) mod N", size=14.5, bold=True, color=POS))
    parts.append(text(240, 80, "Вилучення 1 вузла змінює N → 3 з 4", size=12, color=MUTED))
    
    # Схема з N=4
    parts.append(text(40, 110, "При N = 4:", size=12.5, bold=True, anchor="start"))
    keys_4 = [
        ("k0: mod 4 = 0", "Вузол 0"),
        ("k1: mod 4 = 1", "Вузол 1"),
        ("k2: mod 4 = 2", "Вузол 2"),
        ("k3: mod 4 = 3", "Вузол 3 (впав)"),
        ("k4: mod 4 = 0", "Вузол 0"),
        ("k5: mod 4 = 1", "Вузол 1"),
    ]
    for i, (kstr, sstr) in enumerate(keys_4):
        y = 132 + i * 21
        col = POS if "впав" in sstr else INK
        parts.append(text(40, y, kstr, size=11.5, anchor="start", color=col))
        parts.append(text(210, y, "→  " + sstr, size=11.5, anchor="start", color=col))
        
    parts.append(text(40, 275, "При N = 3 (після збою Вузла 3):", size=12.5, bold=True, anchor="start", color=POS))
    keys_3 = [
        ("k0: mod 3 = 0", "Вузол 0 (без змін)"),
        ("k1: mod 3 = 1", "Вузол 1 (без змін)"),
        ("k2: mod 3 = 2", "Вузол 2 (без змін)"),
        ("k3: mod 3 = 0", "Вузол 0 (ПЕРЕЇЗД)"),
        ("k4: mod 3 = 1", "Вузол 1 (ПЕРЕЇЗД!)"),
        ("k5: mod 3 = 2", "Вузол 2 (ПЕРЕЇЗД!)"),
    ]
    for i, (kstr, sstr) in enumerate(keys_3):
        y = 297 + i * 21
        is_moved = "ПЕРЕЇЗД" in sstr
        col = POS if is_moved else FIELD
        parts.append(text(40, y, kstr, size=11.5, anchor="start", color=col))
        parts.append(text(210, y, "→  " + sstr, size=11.5, anchor="start", bold=is_moved, color=col))
        
    box_fail, _, _ = textbox(240, 465, "75% ключів змінили вузол → Каскадний шторм cache miss!", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(box_fail)

    # ── Права панель: Консистентне хешування ──
    parts.append(text(720, 60, "Консистентне кільце: hash(k) ∈ [0, 2³²−1]", size=14.5, bold=True, color=FIELD))
    parts.append(text(720, 80, "При збої ключі зміщуються лише до сусіда", size=12, color=MUTED))
    
    # Кільце на правій панелі
    rcx, rcy, rr = 720, 230, 95
    parts.append(circle(rcx, rcy, rr, fill=BG, stroke=MUTED, sw=2))
    
    # Вузли N0 (top), N1 (right), N2 (bottom), N3 (left)
    nodes = [
        (0, "N0", FIELD, 0, -rr),
        (90, "N1", FIELD, rr, 0),
        (180, "N2", FIELD, 0, rr),
        (270, "N3", POS, -rr, 0),
    ]
    for deg, name, col, dx, dy in nodes:
        nx, ny = rcx + dx, rcy + dy
        parts.append(circle(nx, ny, 14, fill=col, stroke=INK, sw=1.5))
        parts.append(text(nx, ny + 4, name, size=11, color=BG, bold=True))
        
    parts.append(arrow(rcx - rr + 5, rcy - 18, rcx - 18, rcy - rr + 5, color=POS, sw=1.8))
    parts.append(text(rcx - 90, rcy - 85, "ключі N3 → N0", size=11, color=POS, bold=True, anchor="start"))
    
    parts.append(text(720, 365, "Вузли N0, N1, N2 зберегли 100% своїх ключів.", size=12, color=FIELD, bold=True))
    parts.append(text(720, 390, "Лише ключі знівеченого N3 перейшли до N0.", size=11.5, color=INK))
    
    box_ok, _, _ = textbox(720, 465, "Лише 1/N = 25% ключів ребалансовано! Нуль шторму.", size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_ok)

    render(os.path.join(IMG, "traditional-vs-consistent.svg"), W, H, *parts)


# ── Фігура 2: Пошук за годинниковою стрілкою та ребалансування ─────────────
def fig_ring_rebalance():
    W, H = 840, 500
    parts = []
    
    parts.append(text(W / 2, 28, "Кільце хешування [0, 2³²−1]: додавання вузла N_new", size=15.5, bold=True))
    
    rcx, rcy, rr = 420, 225, 135
    parts.append(circle(rcx, rcy, rr, fill=BG, stroke=INK, sw=2.5))
    
    # Маркер 0 / 2³²-1
    parts.append(line(rcx, rcy - rr - 8, rcx, rcy - rr + 8, color=MUTED, sw=2))
    parts.append(text(rcx, rcy - rr - 15, "0 / 2³²−1", size=11.5, color=MUTED, bold=True))
    
    def polar_coords(deg, r_offset=0):
        rad = math.radians(deg - 90)
        r = rr + r_offset
        return rcx + r * math.cos(rad), rcy + r * math.sin(rad)
    
    # Зелена дуга (від A=30° до N_new=100°)
    arc_pts = [polar_coords(d, 0) for d in range(30, 101, 2)]
    parts.append(polyline(arc_pts, FIELD, 5.5))
    
    # Вузли
    n_A_x, n_A_y = polar_coords(30)
    parts.append(circle(n_A_x, n_A_y, 16, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(n_A_x, n_A_y + 4, "A", size=12, color=BG, bold=True))
    parts.append(text(*polar_coords(30, 26), "Вузол A", size=12, bold=True, color=NEG))

    n_new_x, n_new_y = polar_coords(100)
    parts.append(circle(n_new_x, n_new_y, 16, fill=FIELD, stroke=INK, sw=2))
    parts.append(text(n_new_x, n_new_y + 4, "N⁺", size=11, color=BG, bold=True))
    parts.append(text(*polar_coords(100, 28), "Новий N_new", size=12.5, bold=True, color=FIELD))

    n_B_x, n_B_y = polar_coords(160)
    parts.append(circle(n_B_x, n_B_y, 16, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(n_B_x, n_B_y + 4, "B", size=12, color=BG, bold=True))
    parts.append(text(*polar_coords(160, 26), "Вузол B", size=12, bold=True, color=NEG))

    n_C_x, n_C_y = polar_coords(270)
    parts.append(circle(n_C_x, n_C_y, 16, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(n_C_x, n_C_y + 4, "C", size=12, color=BG, bold=True))
    parts.append(text(*polar_coords(270, 26), "Вузол C", size=12, bold=True, color=NEG))

    # Ключ K1
    k1_x, k1_y = polar_coords(60)
    parts.append(circle(k1_x, k1_y, 6.5, fill=POS, stroke=INK, sw=1))
    parts.append(text(*polar_coords(60, -20), "K1", size=11.5, bold=True, color=POS))
    parts.append(arrow(*polar_coords(60, 8), *polar_coords(90, 8), color=POS, sw=1.6))

    # Ключ K2
    k2_x, k2_y = polar_coords(210)
    parts.append(circle(k2_x, k2_y, 6.5, fill=MUTED, stroke=INK, sw=1))
    parts.append(text(*polar_coords(210, -20), "K2 (на C)", size=11, color=MUTED))

    # Напрямок
    parts.append(arrow(rcx + 25, rcy - rr - 2, rcx + 55, rcy - rr + 8, color=INK, sw=1.8))
    parts.append(text(rcx + 105, rcy - rr - 30, "за годинниковою стрілкою ↻", size=11.5, color=INK, italic=True))

    # Пояснення
    parts.append(text(W / 2, 425, "Зелений сектор (A, N_new]: тільки ці ключі мігрують з вузла B до N_new.", size=12.5, color=FIELD, bold=True))
    parts.append(text(W / 2, 455, "Решта кілець (N_new, B], (B, C] та (C, A] залишаються незмінними.", size=12, color=INK))

    render(os.path.join(IMG, "ring-rebalance.svg"), W, H, *parts)


# ── Фігура 3: Нерівномірність без vnodes та рішення з vnodes ───────────────
def fig_virtual_nodes():
    W, H = 920, 480
    parts = []
    
    parts.append(text(W / 2, 28, "Проблема нерівномірності та її розв'язок через віртуальні вузли (vnodes)", size=15.5, bold=True))
    parts.append(line(W / 2, 55, W / 2, 460, color=MUTED, sw=1, dash="5,5"))
    
    # ── Ліва панель: Без vnodes ──
    parts.append(text(230, 60, "Без vnodes (3 фізичні вузли)", size=14.5, bold=True, color=POS))
    parts.append(text(230, 80, "Випадкове розставляння → дисбаланс до 500%", size=11.5, color=MUTED))
    
    lcx, lcy, lr = 230, 215, 100
    parts.append(circle(lcx, lcy, lr, fill=BG, stroke=INK, sw=2))
    
    def lcoords(deg, offset=0):
        rad = math.radians(deg - 90)
        r = lr + offset
        return lcx + r * math.cos(rad), lcy + r * math.sin(rad)
        
    parts.append(circle(*lcoords(10), 15, fill="#e74c3c", stroke=INK, sw=1.5))
    parts.append(text(*lcoords(10, 26), "A (8%)", size=11, color=POS, bold=True))
    
    parts.append(circle(*lcoords(40), 15, fill="#3498db", stroke=INK, sw=1.5))
    parts.append(text(*lcoords(40, 26), "B", size=11.5, color=INK, bold=True))
    
    parts.append(circle(*lcoords(220), 15, fill="#2ecc71", stroke=INK, sw=1.5))
    parts.append(text(*lcoords(220, 26), "C", size=11.5, color=INK, bold=True))
    
    carc = [lcoords(d, 0) for d in range(40, 221, 5)]
    parts.append(polyline(carc, FIELD, 4.5))
    parts.append(text(lcx, lcy, "Вузол C:\n50% навантаження", size=11.5, color=FIELD, bold=True))

    box_bad, _, _ = textbox(230, 410, "Дисперсія навантаження σ² висока!\nОдин вузол перевантажений, інші пустують.", size=11.5, fill="#fdecea", stroke=POS, color=POS)
    parts.append(box_bad)

    # ── Права панель: З vnodes ──
    parts.append(text(690, 60, "З віртуальними вузлами (vnodes)", size=14.5, bold=True, color=FIELD))
    parts.append(text(690, 80, "V = 100..250 vnodes → рівномірність ±5%", size=11.5, color=MUTED))
    
    rcx, rcy, rr = 690, 215, 100
    parts.append(circle(rcx, rcy, rr, fill=BG, stroke=INK, sw=2))
    
    def rcoords(deg, offset=0):
        rad = math.radians(deg - 90)
        r = rr + offset
        return rcx + r * math.cos(rad), rcy + r * math.sin(rad)
        
    vnodes = [
        (0, "A1", "#e74c3c"), (40, "B1", "#3498db"), (80, "C1", "#2ecc71"),
        (120, "A2", "#e74c3c"), (160, "B2", "#3498db"), (200, "C2", "#2ecc71"),
        (240, "A3", "#e74c3c"), (280, "B3", "#3498db"), (320, "C3", "#2ecc71"),
    ]
    for deg, label, col in vnodes:
        parts.append(circle(*rcoords(deg), 11, fill=col, stroke=INK, sw=1))
        parts.append(text(*rcoords(deg), label, size=9, color=BG, bold=True))
        
    parts.append(text(rcx, rcy, "Ідеальне\nпереплетення", size=11.5, color=INK, bold=True))
    
    box_good, _, _ = textbox(690, 410, "Кожен фізичний вузол отримує ~33.3%\nзавдяки закону великих чисел (ЗВЧ).", size=11.5, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_good)

    render(os.path.join(IMG, "virtual-nodes.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_traditional_vs_consistent()
    fig_ring_rebalance()
    fig_virtual_nodes()
    print("OK: 3 SVG згенеровано у", IMG)
