# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми Bimodal Multicast (pbcast)."""
import sys, os

# 4 рівні вгору до теки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_bimodal_distribution():
    """Фігура 1: Бімодальний розподіл доставки проти класичного ненадійного мовлення."""
    w, h = 860, 480
    frags = []

    # Фон та сітка
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))

    # Заголовок блоку
    frags.append(text(w / 2, 40, "Розподіл частки вузлів (z), які отримали повідомлення", size=16, bold=True))

    # Вісі координат
    ox, oy = 90, 390
    gw, gh = 680, 290
    frags.append(arrow(ox, oy, ox + gw + 40, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))

    # Підписи осей
    frags.append(text(ox + gw + 45, oy + 5, "z (частка)", size=13, anchor="start", bold=True))
    frags.append(text(ox, oy - gh - 30, "Густина f(z)", size=13, anchor="middle", bold=True))

    # Позначки на осі X
    frags.append(line(ox, oy, ox, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox, oy + 22, "0.0", size=12, anchor="middle"))

    frags.append(line(ox + gw / 2, oy, ox + gw / 2, oy + 6, color="#9ca3af", sw=1.2, dash="3,3"))
    frags.append(text(ox + gw / 2, oy + 22, "0.5 (50%)", size=12, color=MUTED, anchor="middle"))

    frags.append(line(ox + gw, oy, ox + gw, oy + 6, color=LINE, sw=1.5))
    frags.append(text(ox + gw, oy + 22, "1.0 (100%)", size=12, anchor="middle", bold=True))

    # Розмитий купол класичного Multicast (ненадійний/smeared)
    # Крива Гауса з центром на 0.65 під навантаженням
    path_smeared = (
        f"M {ox+80} {oy} "
        f"C {ox+200} {oy-20}, {ox+300} {oy-130}, {ox+440} {oy-140} "
        f"C {ox+520} {oy-140}, {ox+590} {oy-60}, {ox+640} {oy}"
    )
    frags.append(f'<path d="{path_smeared}" fill="#fee2e2" stroke="{POS}" stroke-width="2.2" stroke-dasharray="6,4" fill-opacity="0.45"/>')

    # Підпис до розмитого розподілу
    box_s, _, _ = textbox(ox + 420, oy - 170, "Класичний ненадійний Multicast під навантаженням\n(непередбачувана частка втрат: 30–80%)",
                          size=12, pad=8, fill="#fff1f2", stroke=POS, sw=1.2, color=POS)
    frags.append(box_s)

    # Пік 1 (Mode 0): Відмова джерела на старті (z ≈ 0)
    frags.append(rect(ox - 8, oy - 260, 20, 260, fill=POS, stroke=LINE, sw=1.5, rx=3))
    box_m0, _, _ = textbox(ox + 90, oy - 275, "Мода 0 (z = 0):\nДжерело впало на початку\nІмовірність: ε",
                           size=11, pad=6, fill="#fee2e2", stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(box_m0)
    frags.append(arrow(ox + 50, oy - 275, ox + 15, oy - 230, color=POS, sw=1.4))

    # Пік 2 (Mode 1): Повна доставка всім здоровим вузлам (z ≈ 1)
    frags.append(rect(ox + gw - 12, oy - 280, 20, 280, fill=FIELD, stroke=LINE, sw=1.5, rx=3))
    box_m1, _, _ = textbox(ox + gw - 120, oy - 295, "Мода 1 (z ≈ 1.0):\nМайже ВСІ вузли отримали\nІмовірність: 1 − ε (>99.999%)",
                           size=11, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.2, color="#065f46", bold=True)
    frags.append(box_m1)
    frags.append(arrow(ox + gw - 70, oy - 295, ox + gw - 5, oy - 250, color=FIELD, sw=1.4))

    # Зона заборонених проміжних станів
    frags.append(line(ox + 35, oy - 15, ox + gw - 35, oy - 15, color="#0284c7", sw=2.0))
    box_void, _, _ = textbox(ox + gw / 2, oy - 50, "Проміжні стани зникаюче малоймовірні: P(0 < z < 1) → 0 при рості N\nСистема бінарна: або отримали ВСІ, або повідомлення не існує",
                             size=12, pad=8, fill="#f0f9ff", stroke="#0284c7", sw=1.2, color="#0369a1", bold=True)
    frags.append(box_void)

    return render(os.path.join(OUT_DIR, "bimodal-distribution.svg"), w, h, *frags)


def fig_pbcast_two_phases():
    """Фігура 2: Двофазна архітектура Bimodal Multicast (Фаза 1 Multicast + Фаза 2 Gossip Anti-Entropy)."""
    w, h = 900, 520
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(w / 2, 38, "Двофазна модель доставки Bimodal Multicast (pbcast)", size=16, bold=True))

    # Ліва колонка: Фаза 1 (Оптимістична трансляція)
    frags.append(rect(30, 65, 390, 425, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(225, 95, "Фаза 1: Оптимістична трансляція", size=14, color="#1e293b", bold=True))
    frags.append(text(225, 115, "Швидкий Best-Effort IP Multicast / UDP", size=11, color=MUTED))

    # Джерело S
    b_src, _, _ = textbox(225, 160, "Джерело даних S\n(Seq = 101, Data)", size=13, pad=8, fill="#eff6ff", stroke="#2563eb", color="#1e40af", bold=True)
    frags.append(b_src)

    # Дерево мовлення
    frags.append(arrow(225, 190, 225, 230, color="#2563eb", sw=2.0))
    frags.append(circle(225, 240, 12, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(text(225, 244, "L3", size=10, color="#1e40af", bold=True))

    # Вузли-одержувачі
    nodes_f1 = [
        (80, 310, "Вузол A\n✓ Отримав", "#ecfdf5", FIELD, "#065f46"),
        (175, 310, "Вузол B\n✓ Отримав", "#ecfdf5", FIELD, "#065f46"),
        (275, 310, "Вузол C\n✗ Втрата (Drop)", "#fef2f2", POS, "#991b1b"),
        (370, 310, "Вузол D\n✓ Отримав", "#ecfdf5", FIELD, "#065f46"),
    ]
    for nx, ny, lbl, fl, strk, clr in nodes_f1:
        frags.append(arrow(225, 252, nx, ny - 25, color="#2563eb", sw=1.5))
        b, _, _ = textbox(nx, ny, lbl, size=11, pad=6, fill=fl, stroke=strk, color=clr, bold=True)
        frags.append(b)

    box_f1_desc, _, _ = textbox(225, 410, "Затримка: O(1) мікросекунди\nОхоплення: (1 − p) ≈ 95–99% вузлів\nНавантаження джерела: O(1) пакет",
                                size=11, pad=8, fill="#ffffff", stroke="#94a3b8", sw=1.0, color="#334155")
    frags.append(box_f1_desc)

    # Права колонка: Фаза 2 (Децентралізоване відновлення через Gossip)
    frags.append(rect(460, 65, 410, 425, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(665, 95, "Фаза 2: Епідемічне відновлення (Gossip)", size=14, color="#1e293b", bold=True))
    frags.append(text(665, 115, "Anti-Entropy раунди між випадковими сусідами", size=11, color=MUTED))

    # Схема взаємодії вузла C з іншими
    b_c2, _, _ = textbox(665, 170, "Вузол C (дефіцит: немає #101)\nОбирає k випадкових пірів", size=12, pad=8, fill="#fef2f2", stroke=POS, color="#991b1b", bold=True)
    frags.append(b_c2)

    # Піри D та B
    b_b2, _, _ = textbox(530, 270, "Вузол B\n(Має #101)", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, color="#065f46", bold=True)
    b_d2, _, _ = textbox(800, 270, "Вузол D\n(Має #101)", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, color="#065f46", bold=True)
    frags.append(b_b2)
    frags.append(b_d2)

    # Стрілки обміну: 1. Digest / Solicitation, 2. Retransmit
    frags.append(arrow(630, 195, 545, 240, color="#d97706", sw=1.6))
    frags.append(text(560, 205, "1. Digest / NAK", size=10, color="#b45309", bold=True))

    frags.append(arrow(555, 245, 640, 200, color=FIELD, sw=1.6))
    frags.append(text(625, 235, "2. Repair Data", size=10, color="#047857", bold=True))

    frags.append(arrow(700, 195, 785, 240, color="#d97706", sw=1.6))
    frags.append(text(765, 205, "1. Digest", size=10, color="#b45309"))

    box_f2_desc, _, _ = textbox(665, 360, "Вузол C стягує втрачений #101 від сусіда B\nДжерело S НЕ турбують взагалі!\nНавантаження відновлення розмазане по кластеру",
                                size=11, pad=8, fill="#ecfdf5", stroke=FIELD, sw=1.2, color="#065f46")
    frags.append(box_f2_desc)

    box_f2_stats, _, _ = textbox(665, 440, "Час збіжності: O(log N) раундів\nБуферне вікно: T_round · r_max (очищення без 2PC)",
                                 size=11, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1.0, color="#334155")
    frags.append(box_f2_stats)

    return render(os.path.join(OUT_DIR, "pbcast-two-phases.svg"), w, h, *frags)


def fig_nak_implosion_vs_distributed_repair():
    """Фігура 3: Порівняння NAK-колапсу та розподіленого відновлення в pbcast."""
    w, h = 880, 480
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(w / 2, 38, "Анатомія відмови: NAK-колапс проти децентралізованого ремонту", size=16, bold=True))

    # Ліва частина: Класичний NAK-колапс (SRM / PGM)
    frags.append(rect(30, 65, 395, 390, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    frags.append(text(227, 95, "Традиційний Reliable Multicast", size=14, color=POS, bold=True))
    frags.append(text(227, 115, "Усі NAK летять до джерела S (NAK Storm)", size=11, color=MUTED))

    # Джерело перевантажене
    b_s1, _, _ = textbox(227, 165, "Джерело S (КОЛАПС!)\nБуфер переповнено (λ·N·p > μ)\nДроп пакетів і зависання",
                         size=11, pad=8, fill="#fee2e2", stroke=POS, color="#991b1b", bold=True)
    frags.append(b_s1)

    # 4 вузли шлють NAK джерелу
    r_nodes = [(75, 290, "R1"), (175, 290, "R2"), (275, 290, "R3"), (375, 290, "R4")]
    for rx, ry, name in r_nodes:
        b_r, _, _ = textbox(rx, ry, f"Вузол {name}\n(Втратив)", size=10, pad=5, fill="#ffffff", stroke=POS, color=POS)
        frags.append(b_r)
        frags.append(arrow(rx, ry - 25, 210 if rx < 227 else 245, 205, color=POS, sw=1.8))
        frags.append(text((rx + 227) / 2, (ry + 205) / 2 - 5, "NAK", size=9, color=POS, bold=True))

    box_srm_warn, _, _ = textbox(227, 390, "Вхідний потік: R_nak = λ · N · p\nПри N = 10 000 вузлів джерело отримує\n100 000 NAK/с → метастабільний збій!",
                                 size=11, pad=8, fill="#fee2e2", stroke=POS, sw=1.2, color="#991b1b")
    frags.append(box_srm_warn)

    # Права частина: Децентралізований ремонт у pbcast
    frags.append(rect(455, 65, 395, 390, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(652, 95, "Bimodal Multicast (pbcast)", size=14, color="#065f46", bold=True))
    frags.append(text(652, 115, "Ремонт P2P між випадковими сусідами", size=11, color=MUTED))

    # Джерело вільне
    b_s2, _, _ = textbox(652, 160, "Джерело S (Спокійне)\nТранслює лише новий потік\nНавантаження O(1) = const",
                         size=11, pad=8, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True)
    frags.append(b_s2)

    # Вузли самі обмінюються
    b_p1, _, _ = textbox(520, 270, "Вузол A\n✓ Має пакет", size=11, pad=6, fill="#ffffff", stroke=FIELD, color="#065f46")
    b_p2, _, _ = textbox(652, 310, "Вузол B\n✗ Потребує", size=11, pad=6, fill="#fef2f2", stroke=POS, color="#991b1b")
    b_p3, _, _ = textbox(780, 270, "Вузол C\n✓ Має пакет", size=11, pad=6, fill="#ffffff", stroke=FIELD, color="#065f46")
    frags.append(b_p1)
    frags.append(b_p2)
    frags.append(b_p3)

    # Взаємні стрілки між вузлами
    frags.append(arrow(620, 290, 565, 280, color="#d97706", sw=1.6))
    frags.append(text(585, 270, "1. Solicitation", size=9, color="#b45309", bold=True))

    frags.append(arrow(565, 290, 620, 305, color=FIELD, sw=1.6))
    frags.append(text(600, 315, "2. Retransmit", size=9, color="#047857", bold=True))

    box_pbcast_ok, _, _ = textbox(652, 400, "Навантаження на будь-який вузол: строго O(1)\nЖодних штормів до джерела\nСтабільна пропускна здатність при будь-якому N",
                                  size=11, pad=8, fill="#ecfdf5", stroke=FIELD, sw=1.2, color="#065f46", bold=True)
    frags.append(box_pbcast_ok)

    return render(os.path.join(OUT_DIR, "nak-implosion-vs-distributed-repair.svg"), w, h, *frags)


def fig_pbcast_buffer_retention():
    """Фігура 4: Кільцевий буфер, відстеження послідовностей (Sequence Tracking) та вікно утримання."""
    w, h = 880, 420
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(w / 2, 38, "Кільцевий буфер та структура дайджесту стану в pbcast", size=16, bold=True))

    # Схема послідовності пакетів у буфері
    ox, oy = 60, 110
    cell_w, cell_h = 75, 55

    slots = [
        ("100", "Очищено\n(GC)", "#f1f5f9", "#94a3b8", MUTED),
        ("101", "Очищено\n(GC)", "#f1f5f9", "#94a3b8", MUTED),
        ("102", "Low\nWatermark", "#dbeafe", "#2563eb", "#1e40af"),
        ("103", "Є в буфері\n(Bit 0 = 1)", "#ecfdf5", FIELD, "#065f46"),
        ("104", "Є в буфері\n(Bit 1 = 1)", "#ecfdf5", FIELD, "#065f46"),
        ("105", "ПРОПУСК!\n(Bit 2 = 0)", "#fee2e2", POS, "#991b1b"),
        ("106", "Є в буфері\n(Bit 3 = 1)", "#ecfdf5", FIELD, "#065f46"),
        ("107", "Є в буфері\n(Bit 4 = 1)", "#ecfdf5", FIELD, "#065f46"),
        ("108", "Очікується\n(Seq_max)", "#fef3c7", "#d97706", "#92400e"),
        ("109", "Порожньо", "#ffffff", "#cbd5e1", MUTED),
    ]

    for i, (seq, status, fl, strk, clr) in enumerate(slots):
        cx = ox + i * cell_w
        frags.append(rect(cx, oy, cell_w - 4, cell_h, fill=fl, stroke=strk, sw=1.5, rx=4))
        frags.append(text(cx + (cell_w - 4) / 2, oy + 20, seq, size=13, color=clr, bold=True))
        frags.append(mtext(cx + (cell_w - 4) / 2, oy + 38, status, size=9, color=clr))

    # Стрілка Low Watermark
    frags.append(arrow(ox + 2 * cell_w + 35, oy + cell_h + 35, ox + 2 * cell_w + 35, oy + cell_h + 5, color="#2563eb", sw=1.8))
    frags.append(text(ox + 2 * cell_w + 35, oy + cell_h + 50, "Low Watermark = 102", size=11, color="#2563eb", bold=True))
    frags.append(text(ox + 2 * cell_w + 35, oy + cell_h + 65, "(Усі пакети ≤ 102 отримано)", size=10, color=MUTED))

    # Стрілка Вікна утримання (Retention Window)
    frags.append(line(ox + 2 * cell_w, oy - 15, ox + 8 * cell_w + cell_w - 4, oy - 15, color="#0284c7", sw=2.0))
    frags.append(line(ox + 2 * cell_w, oy - 22, ox + 2 * cell_w, oy - 8, color="#0284c7", sw=2.0))
    frags.append(line(ox + 8 * cell_w + cell_w - 4, oy - 22, ox + 8 * cell_w + cell_w - 4, oy - 8, color="#0284c7", sw=2.0))
    frags.append(text(ox + 5 * cell_w + 30, oy - 28, "Вікно утримання (Buffer Retention Window): T_retain = r_max · T_round · S_f", size=12, color="#0284c7", bold=True))

    # Нижній блок: Структура Gossip-дайджесту
    frags.append(rect(40, 260, 800, 130, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    frags.append(text(440, 285, "Компактне повідомлення дайджесту стану (Gossip State Digest)", size=13, color="#1e293b", bold=True))

    # Поля дайджесту
    d_fields = [
        (60, 305, 140, 65, "Sender ID\n(uint64)\nІдентифікатор вузла", "#eff6ff", "#3b82f6"),
        (210, 305, 150, 65, "Low Watermark = 102\n(uint64)\nБазовий номер", "#dbeafe", "#2563eb"),
        (370, 305, 180, 65, "Bitmask = 0b11011\n(uint64 / [5..0])\nНаявність пакетів 103..107", "#ecfdf5", FIELD),
        (560, 305, 260, 65, "Age / Round Index\n(uint32)\nНомер епідемічного раунду", "#fef3c7", "#d97706"),
    ]
    for fx, fy, fw, fh, lbl, fl, strk in d_fields:
        frags.append(rect(fx, fy, fw, fh, fill=fl, stroke=strk, sw=1.4, rx=4))
        frags.append(mtext(fx + fw / 2, fy + 22, lbl, size=11, color="#1e293b", bold=False))

    return render(os.path.join(OUT_DIR, "pbcast-buffer-retention.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_bimodal_distribution()
    fig_pbcast_two_phases()
    fig_nak_implosion_vs_distributed_repair()
    fig_pbcast_buffer_retention()
    print("Всі фігури успішно згенеровано у", OUT_DIR)
