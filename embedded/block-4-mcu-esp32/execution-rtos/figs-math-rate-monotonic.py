# -*- coding: utf-8 -*-
"""
Фігури для вставки 🧮 «Rate Monotonic» (§4.10.8, вставка fig-27-8-m*).
Чистий Python; вивід → ./img/.

Імпортуємо спільний kit замість переписування примітивів.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── §27.8 вставка 🧮 rate-monotonic ─────────────────────────────────────────

# ── Рис. 4.10.8m.1 — модель завантаження: дві задачі на осі часу ──────────
def fig8m1_utilization_model():
    W, H = 840, 380
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Модель завантаження: звідки береться U = ΣCᵢ/Tᵢ",
                      size=16, bold=True))
    frags.append(text(W / 2, 48, "кожна задача забирає Cᵢ часу кожні Tᵢ — ця частка і є її завантаження",
                      size=11, color=MUTED))

    # Параметри осі
    ox, ow = 50, 680        # початок і ширина осі
    oy_a  = 110             # Y-середина стрічки задачі A
    oy_b  = 195             # Y-середина стрічки задачі B
    bh    = 36              # висота блоку
    scale = ow / 20.0       # 20 одиниць → ow px (T_A=4, T_B=12 у «одиницях»)

    # Осі часу
    frags.append(text(ox - 6, oy_a + 6, "A", size=13, bold=True, color="#2457d6", anchor="end"))
    frags.append(text(ox - 6, oy_b + 6, "B", size=13, bold=True, color="#c0392b", anchor="end"))

    # Задача A: T=4, C=1  (блоки на 0..1, 4..5, 8..9, 12..13, 16..17)
    T_A, C_A = 4, 1
    for k in range(5):
        t0 = k * T_A
        x0 = ox + t0 * scale
        xc = ox + (t0 + C_A) * scale
        xT = ox + (t0 + T_A) * scale
        # блок роботи
        frags.append(rect(x0, oy_a - bh / 2, C_A * scale, bh,
                           fill="#dce8fb", stroke="#2457d6", sw=2, rx=4))
        # вертикальна мітка дедлайну/початку нового
        if k < 4:
            frags.append(line(xT, oy_a - bh / 2 - 8, xT, oy_a + bh / 2 + 4,
                              color="#2457d6", sw=1, dash="3,3"))
            body, w, h = textbox(xT, oy_a - bh / 2 - 18, "Tₐ", size=10,
                                  fill="#dce8fb", stroke="#2457d6", sw=1, color="#2457d6")
            frags.append(body)
        # підпис Cₐ всередині першого блоку
        if k == 0:
            frags.append(text(x0 + C_A * scale / 2, oy_a + 5,
                               "Cₐ", size=10, color="#2457d6", anchor="middle", bold=True))

    # Задача B: T=12, C=3  (блоки на 0..3, 12..15)
    T_B, C_B = 12, 3
    for k in range(2):
        t0 = k * T_B
        x0 = ox + t0 * scale
        xc = ox + (t0 + C_B) * scale
        xT = ox + (t0 + T_B) * scale
        frags.append(rect(x0, oy_b - bh / 2, C_B * scale, bh,
                           fill="#fde8e8", stroke="#c0392b", sw=2, rx=4))
        if k == 0:
            frags.append(line(xT, oy_b - bh / 2 - 8, xT, oy_b + bh / 2 + 4,
                              color="#c0392b", sw=1, dash="3,3"))
            body, w, h = textbox(xT, oy_b - bh / 2 - 18, "T_b", size=10,
                                  fill="#fde8e8", stroke="#c0392b", sw=1, color="#c0392b")
            frags.append(body)
        if k == 0:
            frags.append(text(x0 + C_B * scale / 2, oy_b + 5,
                               "C_b", size=10, color="#c0392b", anchor="middle", bold=True))

    # Горизонтальна вісь часу
    frags.append(arrow(ox, oy_b + bh / 2 + 22, ox + ow + 16, oy_b + bh / 2 + 22,
                        color=INK, sw=1.5))
    frags.append(text(ox + ow + 20, oy_b + bh / 2 + 26, "час", size=11, color=MUTED))

    # Мітки 0, 4, 8, 12, 16, 20
    for tick in range(0, 21, 4):
        xt = ox + tick * scale
        frags.append(line(xt, oy_b + bh / 2 + 18, xt, oy_b + bh / 2 + 28, color=MUTED, sw=1))
        frags.append(text(xt, oy_b + bh / 2 + 40, str(tick), size=10, color=MUTED, anchor="middle"))

    # Формули завантаження — права колонка
    fx = ox + ow + 36
    frags.append(text(fx, oy_a - 12, "Uₐ = Cₐ / Tₐ", size=13, bold=True, color="#2457d6"))
    frags.append(text(fx, oy_a + 10, "= 1 / 4 = 0.25", size=12, color="#2457d6"))
    frags.append(text(fx, oy_b - 12, "U_b = C_b / T_b", size=13, bold=True, color="#c0392b"))
    frags.append(text(fx, oy_b + 10, "= 3 / 12 = 0.25", size=12, color="#c0392b"))

    # Підсумок U
    uy = oy_b + bh / 2 + 70
    body, w, h = textbox(W / 2, uy,
                          "U = ΣCᵢ/Tᵢ = Uₐ + U_b = 0.25 + 0.25 = 0.50 (50 %)",
                          size=13, bold=True,
                          fill="#f0f8e8", stroke=FIELD, sw=2)
    frags.append(body)
    frags.append(text(W / 2, uy + h / 2 + 18,
                       "саме це число порівнюють з межею Лю–Лейленда",
                       size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-27-8-m1-utilization-model.svg"), W, H,
           *frags, title=None)
    print("wrote fig-27-8-m1-utilization-model.svg")


# ── Рис. 4.10.8m.2 — RM vs зворотні пріоритети: дедлайни ──────────────────
def fig8m2_rm_vs_inverse():
    W, H = 860, 420
    frags = []

    frags.append(text(W / 2, 28, "Чому коротший період = вищий пріоритет",
                      size=16, bold=True))
    frags.append(text(W / 2, 48,
                       "те саме навантаження — два різних призначення пріоритетів",
                       size=11, color=MUTED))

    # Кольори задач
    COL = {"A": "#2457d6", "B": "#27ae60", "C": "#c0392b"}
    CFILL = {"A": "#dce8fb", "B": "#e8f8ee", "C": "#fde8e8"}

    # Параметри: A(T=4,C=1), B(T=8,C=2), C(T=16,C=3)
    tasks = [
        {"name": "A", "T": 4,  "C": 1},
        {"name": "B", "T": 8,  "C": 2},
        {"name": "C", "T": 16, "C": 3},
    ]
    total_time = 16
    scale = 520 / total_time
    ox = 110
    bh = 28

    def draw_schedule(y0, label, schedule_blocks, missed_deadline=None):
        """Малює одну стрічку розкладу."""
        # Мітка рядка
        body, w, h = textbox(ox - 56, y0 + bh + 6, label, size=12, bold=True,
                              fill=FILL, stroke=LINE, sw=1.5)
        frags.append(body)

        # Ось
        frags.append(arrow(ox, y0 + bh * 3 + 16, ox + total_time * scale + 12,
                            y0 + bh * 3 + 16, color=MUTED, sw=1.2))

        # Мітки часу
        for t in range(0, total_time + 1, 4):
            xt = ox + t * scale
            frags.append(line(xt, y0 + bh * 3 + 12, xt, y0 + bh * 3 + 22,
                              color=MUTED, sw=1))
            frags.append(text(xt, y0 + bh * 3 + 34, str(t), size=9,
                              color=MUTED, anchor="middle"))

        # Мітки задач ліворуч
        for i, tk in enumerate(tasks):
            frags.append(text(ox - 6, y0 + i * bh + bh * 0.65,
                              tk["name"], size=11, bold=True,
                              color=COL[tk["name"]], anchor="end"))

        # Блоки виконання
        for seg in schedule_blocks:
            name, t_start, t_end = seg
            row = {"A": 0, "B": 1, "C": 2}[name]
            x0 = ox + t_start * scale
            xw = (t_end - t_start) * scale
            frags.append(rect(x0, y0 + row * bh, xw, bh - 2,
                              fill=CFILL[name], stroke=COL[name], sw=1.5, rx=3))

        # Дедлайни (вертикальні мітки + значки)
        for tk in tasks:
            for k in range(1, total_time // tk["T"] + 2):
                td = k * tk["T"]
                if td > total_time:
                    break
                xt = ox + td * scale
                row = {"A": 0, "B": 1, "C": 2}[tk["name"]]
                yd = y0 + row * bh
                # Мітка дедлайну
                if missed_deadline and (tk["name"], td) in missed_deadline:
                    # Червоний хрест
                    frags.append(line(xt - 6, yd - 8, xt + 6, yd + 4,
                                      color="#c0392b", sw=2.5))
                    frags.append(line(xt + 6, yd - 8, xt - 6, yd + 4,
                                      color="#c0392b", sw=2.5))
                    body, w, h = textbox(xt + 2, yd - 18, "зрив!", size=9,
                                          fill="#fde8e8", stroke="#c0392b", sw=1.2,
                                          color="#c0392b")
                    frags.append(body)
                else:
                    # Зелена галочка
                    frags.append(line(xt - 5, yd - 2, xt - 1, yd + 4,
                                      color=FIELD, sw=2))
                    frags.append(line(xt - 1, yd + 4, xt + 6, yd - 6,
                                      color=FIELD, sw=2))

    # ── ВЕРХНЯ стрічка: RM — A(вис)>B(сер)>C(низ) ──────────────────────────
    # A: виконується 0-1, 4-5, 8-9, 12-13
    # B: виконується після A в кожному T_B вікні: 1-3, 5-7, 9-11, 13-15
    # C: виконується рештою: 3-4, 7-8, 11-12 (встигає до 16)
    rm_blocks = [
        ("A", 0, 1), ("A", 4, 5), ("A", 8, 9), ("A", 12, 13),
        ("B", 1, 3), ("B", 5, 7), ("B", 9, 11), ("B", 13, 15),
        ("C", 3, 4), ("C", 7, 8), ("C", 11, 12), ("C", 15, 16),
    ]
    draw_schedule(68, "RM\n(правильно)", rm_blocks, missed_deadline=None)

    # Підпис RM
    body, w, h = textbox(ox + total_time * scale / 2, 68 + bh * 3 + 50,
                          "RM: A (T=4) > B (T=8) > C (T=16) — усі дедлайни витримано ✓",
                          size=11, fill="#e8f8ee", stroke=FIELD, sw=1.5)
    frags.append(body)

    # ── НИЖНЯ стрічка: зворотні пріоритети C>B>A ───────────────────────────
    # C(вис): 0-3, 16 — блок довгий; A(низ): чекає C, виконується лише після
    # C: 0-3; потім B: 3-5; потім A: 5-6; C: 8-11; B: 11-13; A: 13-14
    # A має дедлайн t=4, але до t=5 навіть не починалась — ЗРИВ
    inv_blocks = [
        ("C", 0, 3), ("B", 3, 5), ("A", 5, 6),
        ("C", 8, 11), ("B", 11, 13), ("A", 13, 14),
        ("C", 16, 16),  # заглушка (не малює нічого)
    ]
    y_bot = 240
    draw_schedule(y_bot, "Навпаки\n(помилка)",
                  [b for b in inv_blocks if b[1] < b[2]],
                  missed_deadline={("A", 4), ("A", 8), ("A", 12)})

    body, w, h = textbox(ox + total_time * scale / 2, y_bot + bh * 3 + 50,
                          "Зворотні: C (T=16) > B (T=8) > A (T=4) — A зриває дедлайни ✗",
                          size=11, fill="#fde8e8", stroke="#c0392b", sw=1.5, color="#c0392b")
    frags.append(body)

    # Горизонтальний роздільник
    frags.append(line(30, y_bot - 14, W - 30, y_bot - 14, color=MUTED, sw=1, dash="4,4"))

    render(os.path.join(OUT, "fig-27-8-m2-rm-vs-inverse.svg"), W, H,
           *frags, title=None)
    print("wrote fig-27-8-m2-rm-vs-inverse.svg")


# ── Точка входу ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig8m1_utilization_model()
    fig8m2_rm_vs_inverse()
    print("done.")
