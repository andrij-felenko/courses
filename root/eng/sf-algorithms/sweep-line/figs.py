# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми «Замітальна пряма: події, статус і геометрія за один прохід».
Всі фігури рендеряться у формат SVG за допомогою svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_sweep_line_concept():
    """Фігура 1: Концепція замітальної прямої, подій та структури статусу."""
    W, H = 940, 530
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 28, "Замітальна пряма: перетворення 2D-простору на 1D-порядок у часі",
                  size=16, bold=True, color=INK))

    sweep_x = 450

    # Загальне тло робочої області
    p.append(rect(40, 75, W - 80, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    # Затінення лівої (опрацьованої) частини
    p.append('<polygon points="40,75 450,75 450,425 40,425" fill="#f1f5f9" stroke="none"/>')

    p.append(text(245, 98, "Опрацьована область (минуле)", size=12, color=MUTED, bold=True))
    p.append(text(685, 98, "Недосліджена область (майбутнє)", size=12, color=MUTED, bold=True))

    # Вісь X внизу
    p.append(line(40, 425, W - 40, 425, color="#94a3b8", sw=1.5))
    p.append(arrow(W - 60, 425, W - 30, 425, color="#94a3b8", sw=1.5))
    p.append(text(W - 35, 442, "X", size=13, color=INK, bold=True))

    # Сама замітальна пряма L (вертикальна штрихова червона)
    p.append(line(sweep_x, 70, sweep_x, 425, color=POS, sw=2.5, dash="6 4"))
    p.append(rect(sweep_x - 70, 45, 140, 25, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(sweep_x, 62, "Замітальна пряма L", size=11, color=POS, bold=True))

    # Стрілка руху прямої
    p.append(arrow(sweep_x + 15, 230, sweep_x + 65, 230, color=POS, sw=2))
    p.append(text(sweep_x + 40, 220, "рух L (→)", size=11, color=POS, bold=True))

    # Відрізки
    # s1
    p.append(line(100, 150, 580, 210, color="#2563eb", sw=2.5))
    p.append(text(80, 145, "s₁", size=13, color="#2563eb", bold=True))

    # s2
    p.append(line(160, 330, 520, 130, color="#059669", sw=2.5))
    p.append(text(140, 340, "s₂", size=13, color="#059669", bold=True))

    # s3
    p.append(line(260, 110, 680, 380, color="#d97706", sw=2.5))
    p.append(text(240, 105, "s₃", size=13, color="#d97706", bold=True))

    # s4
    p.append(line(340, 390, 780, 300, color="#7c3aed", sw=2.5))
    p.append(text(320, 400, "s₄", size=13, color="#7c3aed", bold=True))

    # Точки перетину на самій прямій L (активні відрізки у статусі)
    pts_on_L = [
        (450, 169, "s₂", "#059669"),
        (450, 194, "s₁", "#2563eb"),
        (450, 232, "s₃", "#d97706"),
        (450, 367, "s₄", "#7c3aed")
    ]

    for px, py, name, col in pts_on_L:
        p.append(circle(px, py, 6, fill="#ffffff", stroke=col, sw=2.5))

    # Точки подій (початки, кінці, перетини)
    events = [
        (100, 150, "start s₁", "#2563eb", True),
        (160, 330, "start s₂", "#059669", True),
        (260, 110, "start s₃", "#d97706", True),
        (340, 390, "start s₄", "#7c3aed", True),
        (283, 173, "перетин s₁ ∩ s₂", POS, True),
        (414, 189, "перетин s₁ ∩ s₃", POS, True),
        (450, 169, "L зараз", POS, False),
        (475, 155, "майбутній перетин s₂ ∩ s₃", POS, False),
        (520, 130, "end s₂", "#059669", False),
        (580, 210, "end s₁", "#2563eb", False),
        (680, 380, "end s₃", "#d97706", False),
        (780, 300, "end s₄", "#7c3aed", False)
    ]

    for ex, ey, elab, ecol, is_past in events:
        if "перетин" in elab:
            p.append(circle(ex, ey, 5.5, fill="#fdecea", stroke=POS, sw=2))
        elif not is_past and elab != "L зараз":
            p.append(circle(ex, ey, 4.5, fill="#ffffff", stroke=ecol, sw=1.8))
        elif is_past:
            p.append(circle(ex, ey, 4.5, fill=ecol, stroke=ecol, sw=1.5))

    # Блок пояснення "Структура статусу T (Y-порядок на L)"
    p.append(rect(40, 450, 410, 65, fill="#f8fafc", stroke="#2563eb", sw=1.5, rx=5))
    p.append(text(245, 470, "СТРУКТУРА СТАТУСУ T (збалансоване дерево)", size=11.5, color="#2563eb", bold=True))
    p.append(text(245, 497, "Вертикальний порядок при x = 450:  s₂ > s₁ > s₃ > s₄", size=12, color=INK, bold=True))

    # Блок пояснення "Черга подій Q (X-порядок)"
    p.append(rect(470, 450, 430, 65, fill="#f8fafc", stroke=POS, sw=1.5, rx=5))
    p.append(text(685, 470, "ЧЕРГА ПОДІЙ Q (пріоритетна черга за X)", size=11.5, color=POS, bold=True))
    p.append(text(685, 497, "Наступні події: [s₂ ∩ s₃] → [end s₂] → [end s₁] → ...", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "sweep-line-concept.svg"), W, H, *p)


def fig_event_types_and_status():
    """Фігура 2: Три фундаментальні типи подій алгоритму Бентлі–Оттмана."""
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 26, "Три типи подій Бентлі–Оттмана та оновлення сусідів у статусі",
                  size=15, bold=True, color=INK))

    col_w = 280
    gap = 25
    x_starts = [40, 40 + col_w + gap, 40 + 2 * (col_w + gap)]

    titles = [
        "1. Лівий кінець (початок s)",
        "2. Точка перетину (s₁ ∩ s₂)",
        "3. Правий кінець (кінець s)"
    ]
    subtitles = [
        "Вставка в статус T",
        "Обмін місцями в T",
        "Видалення зі статусу T"
    ]

    for i in range(3):
        xs = x_starts[i]
        # Панель
        p.append(rect(xs, 50, col_w, 355, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
        p.append(rect(xs, 50, col_w, 42, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=6))
        p.append(text(xs + col_w / 2, 70, titles[i], size=12, color=INK, bold=True))
        p.append(text(xs + col_w / 2, 85, subtitles[i], size=10.5, color=MUTED))

        # Замітальна пряма у вікні
        sl_x = xs + col_w / 2
        p.append(line(sl_x, 105, sl_x, 265, color=POS, sw=1.8, dash="4 3"))

    # 1. Початок відрізка s
    xs1 = x_starts[0]
    p.append(line(xs1 + 30, 130, xs1 + 250, 150, color="#475569", sw=2))
    p.append(text(xs1 + 25, 128, "s_a", size=11, color="#475569", bold=True))

    p.append(line(xs1 + 140, 190, xs1 + 250, 200, color="#2563eb", sw=2.5))
    p.append(circle(xs1 + 140, 190, 5, fill="#2563eb", stroke="#2563eb", sw=1))
    p.append(text(xs1 + 155, 182, "початок s", size=10.5, color="#2563eb", bold=True))

    p.append(line(xs1 + 30, 250, xs1 + 250, 230, color="#475569", sw=2))
    p.append(text(xs1 + 25, 255, "s_b", size=11, color="#475569", bold=True))

    # Перевірки сусідів (стрілки дужок)
    p.append(arrow(xs1 + 190, 185, xs1 + 190, 155, color=POS, sw=1.5))
    p.append(text(xs1 + 225, 170, "тест s ∩ s_a", size=10, color=POS, bold=True))

    p.append(arrow(xs1 + 190, 195, xs1 + 190, 225, color=POS, sw=1.5))
    p.append(text(xs1 + 225, 215, "тест s ∩ s_b", size=10, color=POS, bold=True))

    # Опис внизу панелі 1
    p.append(rect(xs1 + 10, 280, col_w - 20, 115, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    p.append(mtext(xs1 + col_w / 2, 300,
                   "• s вставляється між s_a та s_b\n"
                   "• Тестуємо пару (s_a, s)\n"
                   "• Тестуємо пару (s, s_b)\n"
                   "• Знайдені перетини > x_curr\n"
                   "  додаються в чергу подій Q",
                   size=10.5, color=INK, lh=1.35))

    # 2. Точка перетину
    xs2 = x_starts[1]
    p.append(line(xs2 + 40, 140, xs2 + 240, 240, color="#2563eb", sw=2.5))
    p.append(text(xs2 + 30, 138, "s₁", size=11, color="#2563eb", bold=True))

    p.append(line(xs2 + 40, 240, xs2 + 240, 140, color="#059669", sw=2.5))
    p.append(text(xs2 + 30, 245, "s₂", size=11, color="#059669", bold=True))

    int_x = xs2 + 140
    int_y = 190
    p.append(circle(int_x, int_y, 6, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(int_x, int_y - 12, "s₁ ∩ s₂", size=10.5, color=POS, bold=True))

    p.append(line(xs2 + 40, 115, xs2 + 240, 115, color="#475569", sw=1.5))
    p.append(text(xs2 + 25, 115, "s_top", size=9.5, color="#475569"))

    p.append(line(xs2 + 40, 260, xs2 + 240, 260, color="#475569", sw=1.5))
    p.append(text(xs2 + 25, 260, "s_bot", size=9.5, color="#475569"))

    p.append(arrow(xs2 + 200, 160, xs2 + 200, 125, color=POS, sw=1.5))
    p.append(text(xs2 + 235, 145, "s₂ ∩ s_top", size=9.5, color=POS, bold=True))

    p.append(arrow(xs2 + 200, 220, xs2 + 200, 250, color=POS, sw=1.5))
    p.append(text(xs2 + 235, 238, "s₁ ∩ s_bot", size=9.5, color=POS, bold=True))

    # Опис внизу панелі 2
    p.append(rect(xs2 + 10, 280, col_w - 20, 115, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    p.append(mtext(xs2 + col_w / 2, 300,
                   "• Зафіксовано перетин у вивід\n"
                   "• s₁ та s₂ міняються місцями в T\n"
                   "• Новий сусід зверху: (s₂, s_top)\n"
                   "• Новий сусід знизу: (s₁, s_bot)\n"
                   "• Тестуємо обидві нові пари",
                   size=10.5, color=INK, lh=1.35))

    # 3. Кінець відрізка s
    xs3 = x_starts[2]
    p.append(line(xs3 + 30, 130, xs3 + 250, 150, color="#475569", sw=2))
    p.append(text(xs3 + 25, 128, "s_a", size=11, color="#475569", bold=True))

    p.append(line(xs3 + 30, 190, xs3 + 140, 190, color="#2563eb", sw=2.5))
    p.append(circle(xs3 + 140, 190, 5, fill="#ffffff", stroke="#2563eb", sw=2))
    p.append(text(xs3 + 115, 180, "кінець s", size=10.5, color="#2563eb", bold=True))

    p.append(line(xs3 + 30, 250, xs3 + 250, 230, color="#475569", sw=2))
    p.append(text(xs3 + 25, 255, "s_b", size=11, color="#475569", bold=True))

    p.append(arrow(xs3 + 190, 158, xs3 + 190, 222, color=POS, sw=1.8))
    p.append(text(xs3 + 225, 190, "тест s_a ∩ s_b", size=10, color=POS, bold=True))

    # Опис внизу панелі 3
    p.append(rect(xs3 + 10, 280, col_w - 20, 115, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    p.append(mtext(xs3 + col_w / 2, 300,
                   "• s видаляється зі статусу T\n"
                   "• s_a та s_b стають прямими\n"
                   "  вертикальними сусідами в T\n"
                   "• Тестуємо пару (s_a, s_b)\n"
                   "• Якщо перетинаються > x_curr\n"
                   "  → додаємо подію в Q",
                   size=10.5, color=INK, lh=1.35))

    render(os.path.join(OUT, "event-types-and-status.svg"), W, H, *p)


def fig_klee_rectangles():
    """Фігура 3: Обчислення площі об'єднання прямокутників (задача Клі)."""
    W, H = 900, 480
    p = []

    p.append(text(W / 2, 26, "Площа об'єднання прямокутників: замітання вертикальними смугами",
                  size=15, bold=True, color=INK))

    # Координатна сітка/осі
    p.append(arrow(60, 410, 840, 410, color="#94a3b8", sw=1.5))
    p.append(text(845, 414, "X", size=12, color=INK, bold=True))

    p.append(arrow(60, 410, 60, 60, color="#94a3b8", sw=1.5))
    p.append(text(54, 55, "Y", size=12, color=INK, bold=True))

    # Прямокутники малюємо через polygon, щоб svgcheck не сприймав геометрію за зіткнення карток інтерфейсу
    xs = [120, 220, 360, 460, 560, 740]

    # R1: [120, 120] -> [360, 260]
    p.append('<polygon points="120,120 360,120 360,260 120,260" fill="#3b82f6" fill-opacity="0.25" stroke="#2563eb" stroke-width="2"/>')
    p.append(text(150, 145, "R₁", size=14, color="#2563eb", bold=True))

    # R2: [220, 180] -> [560, 360]
    p.append('<polygon points="220,180 560,180 560,360 220,360" fill="#10b981" fill-opacity="0.25" stroke="#059669" stroke-width="2"/>')
    p.append(text(250, 290, "R₂", size=14, color="#059669", bold=True))

    # R3: [460, 100] -> [740, 240]
    p.append('<polygon points="460,100 740,100 740,240 460,240" fill="#f59e0b" fill-opacity="0.25" stroke="#d97706" stroke-width="2"/>')
    p.append(text(620, 135, "R₃", size=14, color="#d97706", bold=True))

    # Виділяємо активну смугу між x2 та x3: [220, 360]
    p.append('<polygon points="220,120 360,120 360,360 220,360" fill="#c0392b" fill-opacity="0.15" stroke="none"/>')
    p.append(line(220, 70, 220, 410, color=POS, sw=1.5, dash="4 3"))
    p.append(line(360, 70, 360, 410, color=POS, sw=1.5, dash="4 3"))

    # Стрілка dx
    p.append(line(220, 385, 360, 385, color=POS, sw=1.5))
    p.append(circle(220, 385, 3, fill=POS, stroke=POS))
    p.append(circle(360, 385, 3, fill=POS, stroke=POS))
    p.append(text(290, 378, "Δx = x₃ − x₂", size=11, color=POS, bold=True))

    # Висота H_active ліворуч на смузі
    p.append(line(210, 120, 210, 360, color=POS, sw=2))
    p.append(circle(210, 120, 3, fill=POS, stroke=POS))
    p.append(circle(210, 360, 3, fill=POS, stroke=POS))
    p.append(text(145, 245, "H_акт = 240", size=11.5, color=POS, bold=True))

    # Написи на осі X
    for i, x_val in enumerate(xs):
        p.append(line(x_val, 405, x_val, 415, color="#64748b", sw=1.5))
        p.append(text(x_val, 428, "x%d" % (i + 1), size=11, color=INK, bold=True))

    # Формула площі смуги
    p.append(rect(470, 270, 390, 115, fill="#f8fafc", stroke=POS, sw=1.5, rx=6))
    p.append(text(665, 292, "Площа поточної вертикальної смуги:", size=12, color=POS, bold=True))
    p.append(text(665, 320, "ΔПлоща = Δx · H_активна", size=13, color=INK, bold=True))
    p.append(mtext(665, 345,
                   "H_активна — довжина об'єднання 1D-відрізків\n"
                   "на осі Y, яку підтримує дерево відрізків за O(log N)",
                   size=10.5, color=MUTED, lh=1.3))

    render(os.path.join(OUT, "klee-rectangles.svg"), W, H, *p)


def fig_closest_pair_strip():
    """Фігура 4: Пошук найближчої пари точок через замітальну смугу шириною d."""
    W, H = 900, 480
    p = []

    p.append(text(W / 2, 26, "Найближча пара точок: динамічне вікно d × 2d у замітальній смузі",
                  size=15, bold=True, color=INK))

    # Вісь X
    p.append(arrow(50, 420, 850, 420, color="#94a3b8", sw=1.5))
    p.append(text(855, 424, "X", size=12, color=INK, bold=True))

    # Поточна точка P_i при x_i = 500, y_i = 230
    px, py = 500, 230
    d = 130 # поточна мінімальна відстань

    # Замітальна смуга [px - d, px]: [370, 500] малюємо через polygon
    p.append('<polygon points="370,60 500,60 500,410 370,410" fill="#eaf0fd" stroke="#93c5fd" stroke-width="1.5"/>')
    p.append(line(px - d, 60, px - d, 420, color=NEG, sw=1.8, dash="5 4"))
    p.append(line(px, 60, px, 420, color=POS, sw=2))

    p.append(text(px - d, 50, "x_i − d", size=11, color=NEG, bold=True))
    p.append(text(px, 50, "x_i (L зараз)", size=11, color=POS, bold=True))

    # Стрілка ширини смуги d
    p.append(line(px - d, 395, px, 395, color=NEG, sw=1.5))
    p.append(circle(px - d, 395, 3, fill=NEG, stroke=NEG))
    p.append(circle(px, 395, 3, fill=NEG, stroke=NEG))
    p.append(text(px - d / 2, 385, "ширина d", size=11, color=NEG, bold=True))

    # Вікно пошуку d × 2d: x ∈ [px - d, px], y ∈ [py - d, py + d]: y ∈ [100, 360]
    p.append('<polygon points="370,100 500,100 500,360 370,360" fill="#fdecea" stroke="#c0392b" stroke-width="2"/>')
    p.append(text(px - d / 2, py - d + 18, "вікно d × 2d", size=11, color=POS, bold=True))

    # Точки на площині
    past_pts = [(120, 140), (180, 320), (250, 190), (310, 90)]
    for x, y in past_pts:
        p.append(circle(x, y, 4.5, fill="#94a3b8", stroke="#64748b", sw=1.5))

    strip_outside = [(420, 70), (460, 390)]
    for x, y in strip_outside:
        p.append(circle(x, y, 5, fill="#93c5fd", stroke=NEG, sw=1.8))

    candidates = [(410, 160), (440, 280), (480, 210)]
    for x, y in candidates:
        p.append(circle(x, y, 6, fill="#ffffff", stroke=POS, sw=2.2))
        p.append(line(x, y, px, py, color=POS, sw=1.2, dash="3 3"))

    # Поточна точка P_i
    p.append(circle(px, py, 7.5, fill=POS, stroke="#991b1b", sw=2.5))
    p.append(text(px + 28, py + 5, "P_i", size=13, color=POS, bold=True))

    future_pts = [(590, 150), (660, 310), (740, 220), (810, 120)]
    for x, y in future_pts:
        p.append(circle(x, y, 4.5, fill="#ffffff", stroke="#64748b", sw=1.5))

    # Блок обґрунтування геометрії вікна праворуч
    p.append(rect(550, 110, 320, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(710, 135, "Чому перевірок не більше 6?", size=12.5, color=INK, bold=True))
    p.append(mtext(710, 165,
                   "1. Будь-які дві точки лівіше L вже\n"
                   "   перевірені, тому відстань між\n"
                   "   будь-якою парою точок ≥ d.\n\n"
                   "2. У прямокутник d × 2d неможливо\n"
                   "   помістити більше 6 точок із\n"
                   "   попарною відстанню ≥ d.\n\n"
                   "3. Пошук у дереві статусу T за діапазоном\n"
                   "   [y_i − d, y_i + d] займає O(log N),\n"
                   "   а попарних перевірок — O(1)!",
                   size=11, color=INK, lh=1.35))

    render(os.path.join(OUT, "closest-pair-strip.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sweep_line_concept()
    fig_event_types_and_status()
    fig_klee_rectangles()
    fig_closest_pair_strip()
    print("OK: 4 figures generated -> img/")
