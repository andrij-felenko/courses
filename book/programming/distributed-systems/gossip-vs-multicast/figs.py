# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Gossip vs IP Multicast'."""

import sys
import os
import math

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_multicast_vs_gossip_layers():
    """Фігура 1: Порівняння L3/L2 апаратного Multicast та L7/L4 оверлейного Gossip."""
    w, h = 900, 420
    frags = []

    frags.append(text(w / 2, 28, "Архітектурний розрив: апаратний IP Multicast проти оверлейного Gossip", size=16, bold=True))

    # Ліва колонка: IP Multicast
    frags.append(rect(25, 52, 410, 345, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(230, 78, "Апаратний IP Multicast (L3 / IGMP / PIM)", size=14, bold=True, color=NEG))

    # Джерело
    frags.append(circle(90, 140, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(90, 144, "S", size=13, bold=True, color=NEG))
    frags.append(text(90, 175, "Джерело", size=11, color=MUTED))

    # Маршрутизатор (L3 комутатор)
    frags.append(rect(185, 115, 90, 50, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    frags.append(text(230, 137, "Маршрутизатор", size=11, bold=True))
    frags.append(text(230, 153, "(TCAM таблиця)", size=9, color=POS))

    frags.append(arrow(115, 140, 180, 140, color=NEG, sw=2))
    frags.append(text(147, 130, "1 пакет", size=10, bold=True, color=NEG))

    # Одержувачі
    r_nodes = [(370, 105, "R1"), (370, 140, "R2"), (370, 175, "R3")]
    for rx_x, rx_y, r_label in r_nodes:
        frags.append(circle(rx_x, rx_y, 14, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(rx_x, rx_y + 4, r_label, size=10, bold=True, color=NEG))
        frags.append(arrow(280, 140, rx_x - 17, rx_y, color=NEG, sw=1.5))

    # Пояснення характеристик
    frags.append(rect(40, 205, 380, 175, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(55, 226, "• Дублювання в кремнії (ASIC) на швидкості дроту", size=11, color=INK, anchor="start"))
    frags.append(text(55, 248, "• Затримка: 1 переліт (фізичний ліміт оптоволокна)", size=11, color=INK, anchor="start"))
    frags.append(text(55, 270, "• Вузьке місце: обмежена пам'ять TCAM у роутерах", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(55, 292, "• Блокується публічним Інтернетом та SDN хмари", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(55, 314, "• Ненадійний UDP: втрата потребує NAK у застосунку", size=11, color=INK, anchor="start"))
    frags.append(text(55, 336, "• Динамічне членство перевантажує площину PIM", size=11, color=INK, anchor="start"))
    frags.append(text(55, 358, "• Використання: біржові канали (HFT), локальні LAN", size=11, color=MUTED, italic=True, anchor="start"))

    # Права колонка: Gossip
    frags.append(rect(465, 52, 410, 345, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(670, 78, "Оверлейний Gossip (L7 / Unicast UDP / TCP)", size=14, bold=True, color=FIELD))

    # Мережа Gossip
    g_nodes = [
        (530, 125, "N1 (Src)"),
        (630, 105, "N2"),
        (610, 165, "N3"),
        (720, 115, "N4"),
        (710, 170, "N5"),
        (800, 140, "N6"),
    ]
    for gx, gy, glabel in g_nodes:
        is_src = "Src" in glabel
        c_fill = "#eaf8ee" if is_src else "#f1f5f9"
        c_stroke = FIELD if is_src else "#475569"
        frags.append(circle(gx, gy, 17, fill=c_fill, stroke=c_stroke, sw=1.8))
        frags.append(text(gx, gy + 4, glabel.split()[0], size=9, bold=True, color=c_stroke))

    # Зв'язки Gossip
    g_edges = [
        (530, 125, 630, 105),
        (530, 125, 610, 165),
        (630, 105, 720, 115),
        (610, 165, 710, 170),
        (630, 105, 610, 165),
        (720, 115, 800, 140),
        (710, 170, 800, 140),
    ]
    for x1, y1, x2, y2 in g_edges:
        frags.append(arrow(x1 + (15 if x2 > x1 else -15), y1 + (5 if y2 > y1 else -5),
                           x2 + (-15 if x2 > x1 else 15), y2 + (-5 if y2 > y1 else 5),
                           color=FIELD, sw=1.3))

    # Пояснення характеристик Gossip
    frags.append(rect(480, 205, 380, 175, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(495, 226, "• Дублювання в оперативній пам'яті кінцевих хостів", size=11, color=INK, anchor="start"))
    frags.append(text(495, 248, "• Затримка: O(log N) раундів епідемічного обміну", size=11, color=INK, anchor="start"))
    frags.append(text(495, 270, "• Нульовий стан у роутерах: мережа — «тупа труба»", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(495, 292, "• Проходить крізь NAT, WAN, хмари (AWS/GCP/K8s)", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(495, 314, "• Ймовірнісна надійність: стійкість до втрат і крахів", size=11, color=INK, anchor="start"))
    frags.append(text(495, 336, "• Членство: легке масштабування до 100 000+ вузлів", size=11, color=INK, anchor="start"))
    frags.append(text(495, 358, "• Використання: кластери Cassandra, Consul, Dynamo", size=11, color=MUTED, italic=True, anchor="start"))

    return "\n".join(frags), w, h


def fig_nak_implosion_vs_gossip_repair():
    """Фігура 2: NAK-колапс класичного Reliable Multicast проти децентралізованого відновлення Gossip."""
    w, h = 900, 400
    frags = []

    frags.append(text(w / 2, 26, "Проблема надійності: шторм запитів NAK проти відновлення через Gossip", size=16, bold=True))

    # Ліва частина: NAK-колапс у класичному надійному Multicast
    frags.append(rect(25, 48, 410, 335, fill="#fffaf9", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(230, 72, "NAK-колапс (SRM / PGM Multicast)", size=14, bold=True, color=POS))

    # Відправник
    frags.append(circle(230, 105, 20, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(230, 109, "Sender", size=10, bold=True, color=POS))

    # Пакет втрачено на комутаторі
    frags.append(rect(160, 145, 140, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(230, 164, "Комутатор (Drop)", size=10, bold=True, color=POS))
    frags.append(arrow(230, 125, 230, 143, color=LINE, sw=1.5))

    # Одержувачі
    recvs = [(70, 245, "R1"), (150, 245, "R2"), (230, 245, "R3"), (310, 245, "R4"), (390, 245, "R...N")]
    for rx_x, rx_y, rlabel in recvs:
        frags.append(circle(rx_x, rx_y, 16, fill="#f1f5f9", stroke="#64748b", sw=1.5))
        frags.append(text(rx_x, rx_y + 4, rlabel, size=9, bold=True))
        # Стрілка вниз від комутатора до одержувачів
        frags.append(line(230, 175, rx_x, rx_y - 18, color="#cbd5e1", sw=1.2))

    # Стрілки NAK вгору по краях до відправника
    frags.append(arrow(60, 225, 205, 110, color=POS, sw=1.3))
    frags.append(text(125, 155, "NAK шторм", size=9, bold=True, color=POS))
    frags.append(arrow(400, 225, 255, 110, color=POS, sw=1.3))
    frags.append(text(335, 155, "NAK шторм", size=9, bold=True, color=POS))

    frags.append(rect(45, 285, 370, 85, fill="#ffffff", stroke="#fca5a5", sw=1, rx=5))
    frags.append(text(230, 305, "Шторм негативних підтверджень: O(N) NAK-пакетів", size=11, bold=True, color=POS))
    frags.append(text(230, 323, "Втрата пакета на магістралі викликає одночасні запити", size=10, color=INK))
    frags.append(text(230, 340, "від тисяч одержувачів, переповнюючи чергу відправника.", size=10, color=INK))
    frags.append(text(230, 357, "Результат: лавинна відмова джерела та втрата нових даних.", size=10, color=POS, bold=True))

    # Права частина: Gossip Anti-Entropy відновлення
    frags.append(rect(465, 48, 410, 335, fill="#f9fdfa", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(670, 72, "Gossip Anti-Entropy (Bimodal Multicast)", size=14, bold=True, color=FIELD))

    # Вузли оверлею
    g_nodes = [
        (530, 130, "A (Є)", FIELD),
        (670, 120, "B (Втрата)", POS),
        (800, 130, "C (Є)", FIELD),
        (580, 220, "D (Є)", FIELD),
        (730, 215, "E (Втрата)", POS),
    ]
    for gx, gy, glabel, gcolor in g_nodes:
        is_loss = gcolor == POS
        c_fill = "#fdecea" if is_loss else "#eaf8ee"
        frags.append(circle(gx, gy, 20, fill=c_fill, stroke=gcolor, sw=1.8))
        frags.append(text(gx, gy - 2, glabel.split()[0], size=10, bold=True, color=gcolor))
        frags.append(text(gx, gy + 11, glabel.split()[1], size=9, color=gcolor))

    # Локальний обмін та відновлення (A -> B, D -> E)
    frags.append(arrow(552, 130, 646, 122, color=FIELD, sw=1.5))
    frags.append(text(600, 116, "1. Digest / Pull", size=9, bold=True, color=MUTED))

    frags.append(arrow(602, 220, 706, 216, color=FIELD, sw=1.5))
    frags.append(text(655, 208, "2. Repair data", size=9, bold=True, color=FIELD))

    frags.append(arrow(780, 140, 745, 198, color=FIELD, sw=1.5))

    frags.append(rect(485, 285, 370, 85, fill="#ffffff", stroke="#86efac", sw=1, rx=5))
    frags.append(text(670, 305, "Децентралізований ремонт: O(1) навантаження на вузол", size=11, bold=True, color=FIELD))
    frags.append(text(670, 323, "Вузли періодично обмінюються дайджестами (історією)", size=10, color=INK))
    frags.append(text(670, 340, "з k випадковими сусідами. Втрачений пакет запитується", size=10, color=INK))
    frags.append(text(670, 357, "у найближчого однорангового піра, а не у першоджерела.", size=10, color=FIELD, bold=True))

    return "\n".join(frags), w, h


def fig_bimodal_multicast_architecture():
    """Фігура 3: Двофазний конвеєр Bimodal Multicast: швидкий Multicast + ремонт через Gossip."""
    w, h = 880, 380
    frags = []

    frags.append(text(w / 2, 26, "Двофазна модель Bimodal Multicast: швидкість апаратури + надійність пліток", size=16, bold=True))

    # Фаза 1: Оптимістична доставка через IP Multicast
    frags.append(rect(30, 55, 820, 130, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(45, 65, 190, 26, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(140, 82, "Фаза 1: Швидкий Multicast", size=11, bold=True, color=NEG))

    frags.append(circle(100, 135, 20, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(100, 139, "Sender", size=10, bold=True, color=NEG))

    frags.append(arrow(125, 135, 265, 135, color=NEG, sw=2))
    frags.append(text(195, 125, "IP Multicast (UDP)", size=10, bold=True, color=NEG))

    # Свічка прийому
    recv_x = [310, 440, 570, 700]
    recv_status = [("N1 (OK)", FIELD), ("N2 (OK)", FIELD), ("N3 (Втрата!)", POS), ("N4 (OK)", FIELD)]
    for (rx, (rlabel, rcol)) in zip(recv_x, recv_status):
        frags.append(circle(rx, 135, 18, fill="#ffffff", stroke=rcol, sw=1.8))
        frags.append(text(rx, 139, rlabel.split()[0], size=9, bold=True, color=rcol))
        if "Втрата" in rlabel:
            frags.append(text(rx, 165, "пакет дропнуто", size=9, bold=True, color=POS))
        else:
            frags.append(text(rx, 165, "отримано 99%", size=9, color=FIELD))

    # Фаза 2: Фоновий епідемічний ремонт через Gossip
    frags.append(rect(30, 205, 820, 150, fill="#f9fdfa", stroke="#86efac", sw=1.5, rx=8))
    frags.append(rect(45, 215, 220, 26, fill="#eaf8ee", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(155, 232, "Фаза 2: Gossip Anti-Entropy", size=11, bold=True, color=FIELD))

    # Діалог між N2, N3, N4
    frags.append(circle(310, 280, 18, fill="#eaf8ee", stroke=FIELD, sw=1.8))
    frags.append(text(310, 284, "N1", size=10, bold=True, color=FIELD))

    frags.append(circle(440, 280, 18, fill="#eaf8ee", stroke=FIELD, sw=1.8))
    frags.append(text(440, 284, "N2", size=10, bold=True, color=FIELD))

    frags.append(circle(570, 280, 18, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(570, 284, "N3", size=10, bold=True, color=POS))

    frags.append(circle(700, 280, 18, fill="#eaf8ee", stroke=FIELD, sw=1.8))
    frags.append(text(700, 284, "N4", size=10, bold=True, color=FIELD))

    # Стрілки раундів пліток
    frags.append(arrow(460, 275, 548, 275, color=MUTED, sw=1.5))
    frags.append(text(505, 265, "1. Gossip Digest", size=9, color=MUTED))

    frags.append(arrow(550, 288, 462, 288, color=POS, sw=1.5))
    frags.append(text(505, 302, "2. Repair Request (Unicast)", size=9, bold=True, color=POS))

    frags.append(arrow(680, 280, 592, 280, color=FIELD, sw=1.8))
    frags.append(text(636, 270, "3. Retransmit", size=9, bold=True, color=FIELD))

    frags.append(rect(45, 318, 240, 28, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(165, 336, "Гарантія: 100% збіжність за log(N) раундів", size=9, bold=True, color=FIELD))

    frags.append(rect(730, 280, 105, 58, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(782, 298, "Кінцевий стан:", size=9, bold=True))
    frags.append(text(782, 314, "Усі вузли", size=9, color=FIELD))
    frags.append(text(782, 328, "узгоджені", size=9, color=FIELD))

    return "\n".join(frags), w, h


def render_svg(name, frags, w, h):
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/>',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        frags,
        '</svg>'
    ]
    path = os.path.join(OUT, f"{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {path}")


if __name__ == "__main__":
    figures = [
        ("multicast-vs-gossip-layers", fig_multicast_vs_gossip_layers),
        ("nak-implosion-vs-gossip-repair", fig_nak_implosion_vs_gossip_repair),
        ("bimodal-multicast-architecture", fig_bimodal_multicast_architecture),
    ]
    for name, func in figures:
        frags, w, h = func()
        render_svg(name, frags, w, h)
