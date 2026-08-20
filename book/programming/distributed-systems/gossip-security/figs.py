# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Безпека пліток (Byzantine gossip, підписи, Sybil-атаки)'."""

import sys
import os
import math

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_byzantine_gossip_attacks():
    """Фігура 1: Вектори атак на епідемічні протоколи зв'язку."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Вектори атак на епідемічні протоколи зв'язку", size=16, bold=True))

    # Панель 1: Візантійська еквівокація (Equivocation / Double-gossip)
    frags.append(rect(20, 50, 265, 350, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(152, 75, "1. Візантійська еквівокація", size=13, bold=True, color=POS))

    # Зловмисний вузол M по центру
    mx, my = 152, 145
    frags.append(circle(mx, my, 22, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(mx, my + 4, "M (Rogue)", size=10, bold=True, color=POS))

    # Вузли-жертви N1 і N2
    n1x, n1y = 65, 235
    n2x, n2y = 240, 235
    frags.append(circle(n1x, n1y, 20, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(n1x, n1y + 4, "Вузол A", size=10, bold=True, color=NEG))

    frags.append(circle(n2x, n2y, 20, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(n2x, n2y + 4, "Вузол B", size=10, bold=True, color=NEG))

    # Стрілки з суперечливим станом
    frags.append(arrow(mx - 15, my + 15, n1x + 10, n1y - 15, color=POS, sw=1.6))
    frags.append(text(78, 175, "Стан V1 (seq=5)", size=9, bold=True, color=POS))

    frags.append(arrow(mx + 15, my + 15, n2x - 10, n2y - 15, color=POS, sw=1.6))
    frags.append(text(225, 175, "Стан V2 (seq=5)", size=9, bold=True, color=POS))

    frags.append(rect(32, 280, 240, 105, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(152, 300, "Подвійні плітки (Equivocation):", size=11, bold=True, color=POS))
    frags.append(text(152, 318, "• Суперечливі версії з одним seq", size=10, color=INK))
    frags.append(text(152, 335, "• Штучне роздування інкарнацій", size=10, color=INK))
    frags.append(text(152, 352, "• Розкол кластера (Split-Brain)", size=10, color=POS))
    frags.append(text(152, 368, "• Без підписів джерело не виявити", size=9, color=MUTED))

    # Панель 2: Sybil-атака та затемнення (Eclipse)
    frags.append(rect(305, 50, 270, 350, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(440, 75, "2. Sybil-атака та затемнення", size=13, bold=True, color=POS))

    # Жертва в центрі
    vx, vy = 440, 180
    frags.append(circle(vx, vy, 24, fill="#ffffff", stroke="#333333", sw=2))
    frags.append(text(vx, vy + 4, "Жертва (V)", size=10, bold=True, color=INK))

    # 4 Sybil-вузли навколо жертви
    s_nodes = [(370, 125), (510, 125), (370, 235), (510, 235)]
    for i, (sx, sy) in enumerate(s_nodes):
        frags.append(circle(sx, sy, 18, fill="#fdecea", stroke=POS, sw=1.5))
        frags.append(text(sx, sy + 4, "S%d" % (i + 1), size=10, bold=True, color=POS))
        # стрілки до жертви
        frags.append(arrow(sx + (12 if sx < vx else -12), sy + (12 if sy < vy else -12),
                           vx + (-16 if sx < vx else 16), vy + (-16 if sy < vy else 16), color=POS, sw=1.3))

    frags.append(rect(320, 280, 240, 105, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(440, 300, "Захоплення сусідства (Eclipse):", size=11, bold=True, color=POS))
    frags.append(text(440, 318, "• Створення тисяч псевдо-ідентичностей", size=10, color=INK))
    frags.append(text(440, 335, "• Заповнення routing-таблиць жертви", size=10, color=INK))
    frags.append(text(440, 352, "• Повна ізоляція від чесних вузлів", size=10, color=POS))
    frags.append(text(440, 368, "• Цензура та підміна оновлень", size=9, color=MUTED))

    # Панель 3: Отруєння стану та DoS-ампліфікація
    frags.append(rect(595, 50, 265, 350, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(727, 75, "3. Отруєння стану та DoS", size=13, bold=True, color=POS))

    # Атакуючий генерує лавину запитів
    ax, ay = 660, 130
    rx, ry = 795, 130
    tx, ty = 727, 235

    frags.append(circle(ax, ay, 20, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(ax, ay + 4, "Attacker", size=9, bold=True, color=POS))

    frags.append(circle(rx, ry, 20, fill="#f0fdf4", stroke=FIELD, sw=1.5))
    frags.append(text(rx, ry + 4, "Relay R", size=9, bold=True, color=FIELD))

    frags.append(circle(tx, ty, 20, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(tx, ty + 4, "Target T", size=9, bold=True, color=NEG))

    # Стрілка ping-req до релея
    frags.append(arrow(ax + 20, ay, rx - 20, ay, color=POS, sw=1.5))
    frags.append(text(727, 120, "Ping-Req(T)", size=9, bold=True, color=POS))

    # Стрілка від релея до цілі
    frags.append(arrow(rx - 10, ry + 15, tx + 12, ty - 15, color=LINE, sw=1.5))
    frags.append(text(775, 185, "Ампліфікація", size=9, color=POS))

    frags.append(rect(607, 280, 240, 105, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(727, 300, "Вичерпання ресурсів кластера:", size=11, bold=True, color=POS))
    frags.append(text(727, 318, "• Зловживання непрямим зондуванням", size=10, color=INK))
    frags.append(text(727, 335, "• Спам важкими підробленими даними", size=10, color=INK))
    frags.append(text(727, 352, "• Перевантаження CPU перевірками", size=10, color=POS))
    frags.append(text(727, 368, "• Забивання черг пам'яті та мережі", size=9, color=MUTED))

    return render(os.path.join(OUT, "byzantine-gossip-attacks.svg"), w, h, *frags)


def fig_gossip_defense_pipeline():
    """Фігура 2: Багаторівневий конвеєр валідації та фільтрації gossip-повідомлень."""
    w, h = 880, 390
    frags = []

    frags.append(text(w / 2, 26, "Багаторівневий конвеєр валідації та фільтрації gossip-повідомлень", size=15, bold=True))

    stages = [
        ("1. Ingress & Rate-limit", "Token Bucket per IP", "Відсікання flood/DoS", "#eaf0fd", NEG),
        ("2. Envelope & Ed25519", "Криптографічний підпис", "Перевірка автентичності", "#f0fdf4", FIELD),
        ("3. Seq & Replay Window", "Монотонні лічильники", "Захист від повторів", "#fff7ed", "#c2410c"),
        ("4. Equivocation Check", "Детектор подвійних пліток", "Генерація Fraud Proof", "#fdecea", POS),
        ("5. Peer Score & Mesh", "Gossipsub v1.1 скоринг", "Штрафи та ретрансляція", "#f0fdf4", FIELD),
    ]

    bw = 150
    bh = 190
    spacing = 22
    start_x = 25
    y = 55

    for i, (stitle, ssub1, ssub2, fill_c, stroke_c) in enumerate(stages):
        x = start_x + i * (bw + spacing)
        frags.append(rect(x, y, bw, bh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=6))
        frags.append(rect(x + 5, y + 5, bw - 10, 34, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(x + bw / 2, y + 26, stitle, size=10, bold=True, color=stroke_c))

        frags.append(text(x + bw / 2, y + 68, ssub1, size=9, bold=True, color=INK))
        frags.append(text(x + bw / 2, y + 86, ssub2, size=9, color=MUTED))

        # Внутрішній блок рішення
        frags.append(rect(x + 10, y + 105, bw - 20, 68, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        if i == 0:
            frags.append(text(x + bw / 2, y + 124, "Перевищено ліміт?", size=9, color=POS))
            frags.append(text(x + bw / 2, y + 142, "DROP (без парсингу)", size=9, bold=True, color=POS))
            frags.append(text(x + bw / 2, y + 158, "Нуль витрат CPU", size=9, color=MUTED))
        elif i == 1:
            frags.append(text(x + bw / 2, y + 124, "Підпис невірний?", size=9, color=POS))
            frags.append(text(x + bw / 2, y + 142, "DROP + Peer Ban", size=9, bold=True, color=POS))
            frags.append(text(x + bw / 2, y + 158, "Штраф у скоринг", size=9, color=MUTED))
        elif i == 2:
            frags.append(text(x + bw / 2, y + 124, "seq <= local_seq?", size=9, color=MUTED))
            frags.append(text(x + bw / 2, y + 142, "DROP (дублікат)", size=9, bold=True, color=MUTED))
            frags.append(text(x + bw / 2, y + 158, "Без ретрансляції", size=9, color=MUTED))
        elif i == 3:
            frags.append(text(x + bw / 2, y + 124, "Різні хеші на 1 seq?", size=9, color=POS))
            frags.append(text(x + bw / 2, y + 142, "SLASH ORIGIN", size=9, bold=True, color=POS))
            frags.append(text(x + bw / 2, y + 158, "Розсилка доказу", size=9, color=POS))
        elif i == 4:
            frags.append(text(x + bw / 2, y + 124, "Score >= Publish?", size=9, color=FIELD))
            frags.append(text(x + bw / 2, y + 142, "FORWARD k PEERS", size=9, bold=True, color=FIELD))
            frags.append(text(x + bw / 2, y + 158, "Оновлення стану", size=9, color=FIELD))

        # Стрілка до наступного етапу
        if i < len(stages) - 1:
            frags.append(arrow(x + bw + 2, y + bh / 2, x + bw + spacing - 2, y + bh / 2, color=LINE, sw=1.8))

    # Нижня підсумкова панель гарантій
    frags.append(rect(25, 260, 830, 110, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(440, 282, "Результат конвеєра: стійкість до візантійських збоїв f < N / 3", size=12, bold=True, color=FIELD))
    frags.append(text(440, 302, "• Негайне відсікання DoS на стадії 1 захищає криптографічний рушій від перевантаження.", size=10, color=INK))
    frags.append(text(440, 320, "• Підписи Ed25519 (стадія 2) унеможливлюють підробку чужого стану проміжними вузлами-ретрансляторами.", size=10, color=INK))
    frags.append(text(440, 338, "• Скоринг поведінки (стадія 5) ізолює повільні та шкідливі вузли, підтримуючи здорову топологію розповсюдження.", size=10, color=INK))
    frags.append(text(440, 355, "• Еквівокація (стадія 4) миттєво карається довічним баном і розсилкою криптографічного доказу зради.", size=9, color=POS))

    return render(os.path.join(OUT, "gossip-defense-pipeline.svg"), w, h, *frags)


def fig_brahms_peer_sampling():
    """Фігура 3: Захищена вибірка сусідів Brahms: протидія забрудненню топології."""
    w, h = 880, 410
    frags = []

    frags.append(text(w / 2, 26, "Захищена вибірка сусідів Brahms: протидія забрудненню топології", size=15, bold=True))

    # Ліва колонка: Наївний Peer Sampling під атакою
    frags.append(rect(20, 50, 405, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(222, 75, "Наївний Push-Pull Peer Sampling", size=13, bold=True, color=POS))

    # Схема отруєння
    frags.append(rect(35, 95, 375, 125, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    frags.append(text(222, 115, "Атака масовим Push-забрудненням (Sybil Flood):", size=10, bold=True, color=POS))

    frags.append(rect(45, 130, 95, 30, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(92, 149, "Sybil Botnet", size=9, bold=True, color=POS))

    frags.append(arrow(140, 145, 235, 145, color=POS, sw=1.6))
    frags.append(text(187, 137, "10 000 Push/s", size=9, bold=True, color=POS))

    frags.append(rect(240, 130, 155, 75, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(317, 147, "Routing Table жертви", size=9, bold=True, color=POS))
    frags.append(text(317, 163, "95% записів = Sybil IP", size=9, color=POS))
    frags.append(text(317, 178, "Чесні вузли витіснено", size=9, color=POS))
    frags.append(text(317, 193, "(Затемнення / Eclipse)", size=9, italic=True, color=POS))

    frags.append(rect(35, 235, 375, 140, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(222, 255, "Чому наївні алгоритми падають:", size=11, bold=True, color=POS))
    frags.append(text(222, 275, "• Вузол сліпо приймає адреси з чужих Push-повідомлень.", size=10, color=INK))
    frags.append(text(222, 295, "• Зловмисник генерує безліч фіктивних адрес (Sybil).", size=10, color=INK))
    frags.append(text(222, 315, "• Таблиця сусідів повністю заповнюється ботами за O(log N).", size=10, color=INK))
    frags.append(text(222, 335, "• Наслідок: вузол бачить лише отруєну версію реальності.", size=10, color=POS))
    frags.append(text(222, 355, "• Трафік на чесні вузли падає до нуля.", size=9, color=MUTED))

    # Права колонка: Архітектура Brahms
    frags.append(rect(455, 50, 405, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(657, 75, "Архітектура стійкої вибірки Brahms", size=13, bold=True, color=FIELD))

    # Три компоненти вибірки Brahms
    bx = 470
    bw_comp = 375

    frags.append(rect(bx, 95, bw_comp, 50, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(bx + 12, 115, "1. Push View (α = 10%):", size=10, bold=True, color=NEG, anchor="start"))
    frags.append(text(bx + 12, 133, "Обмежена частка прямого обміну. Захист від повного переповнення.", size=9, color=INK, anchor="start"))

    frags.append(rect(bx, 153, bw_comp, 50, fill="#ffffff", stroke="#c2410c", sw=1.2, rx=4))
    frags.append(text(bx + 12, 173, "2. Pull View (β = 10%):", size=10, bold=True, color="#c2410c", anchor="start"))
    frags.append(text(bx + 12, 191, "Активний запит випадкових сусідів з локальної перевіреної історії.", size=9, color=INK, anchor="start"))

    frags.append(rect(bx, 211, bw_comp, 65, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(bx + 12, 230, "3. Sampler View (γ = 80% — Незміщений семплер):", size=10, bold=True, color=FIELD, anchor="start"))
    frags.append(text(bx + 12, 248, "Випадкове блукання (Random Walk) + Min-Wise Hashing.", size=9, bold=True, color=INK, anchor="start"))
    frags.append(text(bx + 12, 264, "Імовірність потрапляння вузла строго пропорційна його чесній вазі.", size=9, color=MUTED, anchor="start"))

    frags.append(rect(bx, 285, bw_comp, 90, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(657, 305, "Математична гарантія Brahms:", size=11, bold=True, color=FIELD))
    frags.append(text(657, 323, "Якщо частка візантійських вузлів f < 0.2, частка ботів", size=10, color=INK))
    frags.append(text(657, 340, "у routing table чесного вузла ніколи не перевищить f,", size=10, bold=True, color=FIELD))
    frags.append(text(657, 357, "навіть якщо ботнет надсилає нескінченний потік Push-запитів.", size=9, color=MUTED))

    return render(os.path.join(OUT, "brahms-peer-sampling.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_byzantine_gossip_attacks()
    fig_gossip_defense_pipeline()
    fig_brahms_peer_sampling()
    print("All figures generated successfully.")
