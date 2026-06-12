# -*- coding: utf-8 -*-
"""
Фігури для «📜 Історія до §5.1.9 — тензодавач, винайдений двічі: Сіммонс і Руге, 1938».
Окремий файл (не в основному figs.py), щоб не забруднювати головний скрипт.
Вивід → ./img/ (у ту саму папку, що й figs.py розділу).

Запуск:
    python E:/develop/courses/embedded/block-5-sensors-control/ch28-sensor-physics/figs-ch28-s9-history-strain-gauge.py

Перевірка:
    python E:/develop/courses/embedded/_tools/svgcheck.py \
        E:/develop/courses/embedded/block-5-sensors-control/ch28-sensor-physics --min-font 8
"""

import sys
import os

# ── спільний kit (НЕ переписувати — імпортувати) ─────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 5.1.9i.1 — Карта-схема подвійного незалежного винаходу 1938
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_coasts_1938():
    """
    Карта-схема: ліворуч — Сіммонс (Caltech), праворуч — Руге (MIT, 3 квітня 1938).
    Між ними «3000 км, без контакту». Внизу — спільний вузол: SR-4, патент 1944.
    Угорі — тонка лінія часу: 1856 Кельвін → 1938 прилад.
    """
    W, H = 760, 480
    frags = []

    # ── Лінія часу (угорі) ──────────────────────────────────────────────────
    tl_y = 46
    tl_x0, tl_x1 = 60, 700
    tl_mid = 380
    frags.append(line(tl_x0, tl_y, tl_x1, tl_y, MUTED, 1.5))
    # маркери
    def timeline_dot(x, y, label_top, label_bot, col=INK):
        frag = circle(x, y, 6, fill=col, stroke=col, sw=1)
        frag += text(x, y - 12, label_top, 10, col, "middle", bold=True)
        frag += text(x, y + 20, label_bot, 9, MUTED, "middle")
        return frag

    frags.append(timeline_dot(tl_x0 + 50, tl_y, "1856", "Кельвін\n(ефект)", MUTED))
    frags.append(timeline_dot(tl_mid, tl_y, "1938", "прилад\n(Сіммонс + Руге)", INK))
    frags.append(timeline_dot(tl_x1 - 30, tl_y, "1944", "патент\nSR-4", MUTED))
    # стрілка часу
    frags.append(arrow(tl_x0, tl_y, tl_x1, tl_y, MUTED, 1.5))
    # підпис лінії часу
    frags.append(text(W // 2, 18, "Від першого спостереження до приладу — 82 роки",
                      11, MUTED, "middle", italic=True))

    # ── Ліва панель — Сіммонс, Caltech ──────────────────────────────────────
    lx, ly, lw, lh = 30, 80, 295, 240
    frags.append(rect(lx, ly, lw, lh, fill="#fff8f4", stroke="#c0503a", sw=1.8, rx=10))
    frags.append(text(lx + lw // 2, ly + 24, "ЗАХІД — Caltech", 13, "#c0503a", "middle", bold=True))
    frags.append(text(lx + lw // 2, ly + 41, "Едвард Сіммонс · 1936–1938", 11, INK, "middle"))

    # три підписи-стрілки (ланцюжок)
    chain_y = [ly + 72, ly + 112, ly + 152]
    chain_texts = [
        ("удар на деталь", "F_удар"),
        ("динамометр\nз тонким дротом", "→ ΔR"),
        ("виміряти силу\nелектрично", "ΔR → F"),
    ]
    for i, (main, sub) in enumerate(chain_texts):
        bx = lx + 20
        bw2 = lw - 40
        b, _, _ = textbox(lx + lw // 2, chain_y[i], main, size=11,
                          fill="#fdefea", stroke="#c0503a", sw=1.2, pad=6,
                          color=INK, min_w=bw2 - 20)
        frags.append(b)
        frags.append(text(lx + lw - 28, chain_y[i] + 4, sub, 10, "#c0503a", "middle", bold=True))
        if i < len(chain_texts) - 1:
            frags.append(arrow(lx + lw // 2, chain_y[i] + 24, lx + lw // 2, chain_y[i + 1] - 22, MUTED, 1.4))

    frags.append(text(lx + lw // 2, ly + lh - 16,
                      "Caltech → суд 1949 → права Сіммонсу", 9, MUTED, "middle", italic=True))

    # ── Права панель — Руге, MIT ─────────────────────────────────────────────
    rx2, ry, rw, rh2 = W - 30 - 295, 80, 295, 240
    frags.append(rect(rx2, ry, rw, rh2, fill="#f4f8ff", stroke="#2457d6", sw=1.8, rx=10))
    frags.append(text(rx2 + rw // 2, ry + 24, "СХІД — MIT", 13, "#2457d6", "middle", bold=True))
    frags.append(text(rx2 + rw // 2, ry + 41, "Артур Руге · 3 квітня 1938", 11, INK, "middle"))

    chain_r = [ry + 72, ry + 112, ry + 152]
    chain_r_texts = [
        ("землетрус на модель\nводонапірного бака", "F_сейсм"),
        ("дріт на цигарковому\nпапері → ΔR", "→ ΔR"),
        ("виміряти деформацію\nелектрично", "ΔR → ε"),
    ]
    for i, (main, sub) in enumerate(chain_r_texts):
        b, _, _ = textbox(rx2 + rw // 2, chain_r[i], main, size=11,
                          fill="#eaf0fd", stroke="#2457d6", sw=1.2, pad=6,
                          color=INK, min_w=rw - 60)
        frags.append(b)
        frags.append(text(rx2 + rw - 28, chain_r[i] + 4, sub, 10, "#2457d6", "middle", bold=True))
        if i < len(chain_r_texts) - 1:
            frags.append(arrow(rx2 + rw // 2, chain_r[i] + 24,
                               rx2 + rw // 2, chain_r[i + 1] - 22, MUTED, 1.4))

    frags.append(text(rx2 + rw // 2, ry + rh2 - 16,
                      "MIT відмовився — права до Руге", 9, MUTED, "middle", italic=True))

    # ── Міжпанельний простір — «3000 км, без контакту» ───────────────────────
    gap_cx = W // 2
    gap_cy = 80 + 240 // 2
    frags.append(text(gap_cx, gap_cy - 16, "3 000 км", 12, MUTED, "middle", bold=True))
    frags.append(text(gap_cx, gap_cy + 2, "без контакту", 11, MUTED, "middle", italic=True))
    frags.append(text(gap_cx, gap_cy + 20, "незалежно", 10, MUTED, "middle", italic=True))
    # стрілки назустріч
    mid_y = gap_cy
    frags.append(arrow(lx + lw + 6, mid_y, gap_cx - 26, mid_y, MUTED, 1.4))
    frags.append(arrow(rx2 - 6, mid_y, gap_cx + 26, mid_y, MUTED, 1.4))

    # ── Нижня плашка — спільний вузол ────────────────────────────────────────
    bot_y = 340
    bot_box_w = 460
    bot_box_h = 96
    bot_bx = (W - bot_box_w) // 2
    frags.append(rect(bot_bx, bot_y, bot_box_w, bot_box_h,
                      fill="#f0f7f0", stroke=FIELD, sw=2, rx=10))
    frags.append(text(W // 2, bot_y + 22, "Той самий прилад — двічі незалежно",
                      13, FIELD, "middle", bold=True))
    frags.append(text(W // 2, bot_y + 44, "Назва: SR-4  (S = Simmons, R = Ruge)",
                      12, INK, "middle"))
    frags.append(text(W // 2, bot_y + 63, "Спільний патент видано 6 червня 1944 року",
                      11, MUTED, "middle", italic=True))
    frags.append(text(W // 2, bot_y + 82, "Перший висновок: «першість» тут — не дата, а збіг двох незалежних шляхів",
                      10, MUTED, "middle", italic=True))

    # стрілки від панелей до нижньої плашки
    frags.append(arrow(lx + lw // 2, ly + 240 + 2, bot_bx + 60, bot_y - 2, MUTED, 1.4))
    frags.append(arrow(rx2 + rw // 2, ry + 240 + 2, bot_bx + bot_box_w - 60, bot_y - 2, MUTED, 1.4))

    render(os.path.join(OUT, "fig-28-9h-1-two-coasts-1938.svg"),
           W, H, *frags,
           title="Рис. 5.1.9i.1. Подвійний незалежний винахід: Сіммонс і Руге, 1938")


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 5.1.9i.2 — Від Кельвіна (1856) до gauge factor
# ─────────────────────────────────────────────────────────────────────────────
def fig_kelvin_to_gaugefactor():
    """
    Угорі: дріт під натягом + міст Вітстона (мотив Рис. 5.1.2.3), 1856.
    Посередині: розклад формули GF = (1+2ν)·ε + (Δρ/ρ) з підписами членів.
    Внизу: контраст метал vs напівпровідник.
    """
    W, H = 720, 440
    frags = []

    # ── Верхня секція: дріт Кельвіна + міст Вітстона ─────────────────────────
    top_y = 56

    # Дріт-змійка під натягом (стилізовано: горизонтальна лінія з позначенням розтягу)
    wire_y = top_y + 28
    wire_x0, wire_x1 = 80, 290
    wire_cx = (wire_x0 + wire_x1) // 2
    frags.append(rect(wire_x0, wire_y - 10, wire_x1 - wire_x0, 20,
                      fill="#f2e8d8", stroke="#9a7050", sw=1.5, rx=4))
    frags.append(text(wire_cx, wire_y + 4, "дріт (Fe або Cu)", 11, "#9a7050", "middle"))
    # стрілки натягу
    frags.append(arrow(wire_x0 - 30, wire_y, wire_x0 - 4, wire_y, POS, 2))
    frags.append(arrow(wire_x1 + 30, wire_y, wire_x1 + 4, wire_y, POS, 2))
    frags.append(text(wire_x0 - 46, wire_y + 4, "F", 12, POS, "middle", bold=True))
    frags.append(text(wire_x1 + 46, wire_y + 4, "F", 12, POS, "middle", bold=True))

    # підпис Кельвіна
    frags.append(text(wire_cx, top_y, "Кельвін, 1856: розтяг змінює опір — і не лише від геометрії",
                      11, MUTED, "middle", italic=True))
    frags.append(text(wire_cx, wire_y + 28, "Δρ/ρ ≠ 0: залізо і мідь реагують по-різному",
                      10, MUTED, "middle", italic=True))

    # Спрощена схема моста Вітстона (мотив Рис. 5.1.2.3)
    bx, by = 360, top_y - 10
    bw, bh = 310, 110
    frags.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(bx + bw // 2, by + 14, "Міст Вітстона (§5.1.2)", 10, MUTED, "middle", bold=True))

    # вузли ромбу
    mx, my = bx + bw // 2, by + 58
    dx, dy = 76, 36
    nodes = {"top": (mx, my - dy), "bot": (mx, my + dy),
             "left": (mx - dx, my), "right": (mx + dx, my)}
    # плечі ромбу
    def bridge_arm(p1, p2, label, col=MUTED):
        cx_ = (p1[0] + p2[0]) // 2
        cy_ = (p1[1] + p2[1]) // 2
        frag = line(p1[0], p1[1], p2[0], p2[1], col, 2)
        frag += text(cx_ + 8, cy_, label, 10, col, "start")
        return frag

    frags.append(bridge_arm(nodes["top"], nodes["left"], "R"))
    frags.append(bridge_arm(nodes["top"], nodes["right"], "R"))
    frags.append(bridge_arm(nodes["left"], nodes["bot"], "R"))
    frags.append(bridge_arm(nodes["right"], nodes["bot"], "R+ΔR", FIELD))
    # вузли
    for pt in nodes.values():
        frags.append(circle(pt[0], pt[1], 4, fill=INK, stroke=INK, sw=1))
    # вольтметр між лівим і правим
    vm_x = mx
    frags.append(line(nodes["left"][0], nodes["left"][1], vm_x - 14, nodes["left"][1], INK, 1.2))
    frags.append(line(nodes["right"][0], nodes["right"][1], vm_x + 14, nodes["right"][1], INK, 1.2))
    frags.append(circle(vm_x, my, 13, fill="#fff", stroke=INK, sw=1.5))
    frags.append(text(vm_x, my + 5, "V", 11, FIELD, "middle", bold=True))
    frags.append(text(bx + bw // 2, by + bh - 8, "той самий міст — від 1856-го", 9, MUTED, "middle", italic=True))

    # ── Середня секція: формула gauge factor ──────────────────────────────────
    mid_y = top_y + 130
    sep_y = mid_y - 10

    # роздільник
    frags.append(line(40, sep_y, W - 40, sep_y, MUTED, 1, dash="4,3"))
    frags.append(text(W // 2, sep_y - 6, "Зерно gauge factor: що побачив Кельвін", 12, INK, "middle", bold=True))

    # формула — використовуємо fitbox для кожного члена
    form_y = mid_y + 20
    # Загальний вигляд
    frags.append(fitbox(40, form_y, W - 80, 36,
                        "GF = (ΔR/R) / ε  =  (1 + 2ν) · ε / ε  +  (Δρ/ρ) / ε",
                        size=14, bold=True, fill="#f0f7f0", stroke=FIELD, sw=1.8, color=INK))

    # Дві колонки-підписи
    col1_cx = W // 4
    col2_cx = 3 * W // 4
    ann_y = form_y + 60

    b1, w1, h1 = textbox(col1_cx, ann_y,
                          "геометричний член:\n(1 + 2ν)  ≈  1 + 2·0.3  =  1.6\n(ν — коефіцієнт Пуассона)",
                          size=11, fill="#fefaf4", stroke="#c0a060", sw=1.4, pad=8, color=INK, min_w=260)
    frags.append(b1)
    frags.append(text(col1_cx, ann_y - h1 // 2 - 12,
                      "те, що видно геометрично", 10, MUTED, "middle", italic=True))

    b2, w2, h2 = textbox(col2_cx, ann_y,
                          "п'єзорезистивний член:\nΔρ/ρ  ≠ 0 — те «зайве», що\nпобачив Кельвін",
                          size=11, fill="#fef4f4", stroke=POS, sw=1.4, pad=8, color=INK, min_w=260)
    frags.append(b2)
    frags.append(text(col2_cx, ann_y - h2 // 2 - 12,
                      "матеріалозалежний внесок", 10, MUTED, "middle", italic=True))

    # стрілки від формули до пояснень
    arrow_y_top = form_y + 36
    arrow_y_bot = ann_y - h1 // 2 - 2
    frags.append(arrow(col1_cx, arrow_y_top, col1_cx, arrow_y_bot, MUTED, 1.2))
    frags.append(arrow(col2_cx, arrow_y_top, col2_cx, arrow_y_bot, MUTED, 1.2))

    # Підсумок GF для металу
    sum_y = ann_y + h1 // 2 + 22
    frags.append(text(W // 2, sum_y, "→  Для металу (Fe, Cu, NiCr): GF ≈ 1.6 + мал. = 2.0…2.1",
                      13, FIELD, "middle", bold=True))
    frags.append(text(W // 2, sum_y + 18,
                      "Конкретний тип (напр. BLH AB-1): GF ≈ 2.07 — саме цей рядок у даташиті SR-4",
                      11, MUTED, "middle", italic=True))

    # ── Нижня секція: контраст з напівпровідником ────────────────────────────
    bot_y = H - 72
    frags.append(line(40, bot_y - 12, W - 40, bot_y - 12, MUTED, 1, dash="4,3"))

    half_w = (W - 100) // 2
    # Метал
    frags.append(fitbox(40, bot_y, half_w, 58,
                        "Метал (SR-4, NiCr-дріт):\nGF ≈ 2.0–2.1  |  лінійний  |  стабільний",
                        size=11, fill="#f4f8f4", stroke=FIELD, sw=1.5, color=INK))
    # Напівпровідник
    frags.append(fitbox(60 + half_w, bot_y, half_w, 58,
                        "Напівпровідник (Si):\nGF ≈ 100–200  |  нелінійний  |  термозалежний",
                        size=11, fill="#fef4f4", stroke=POS, sw=1.5, color=INK))

    render(os.path.join(OUT, "fig-28-9h-2-kelvin-to-gaugefactor.svg"),
           W, H, *frags,
           title="Рис. 5.1.9i.2. Від Кельвіна (1856) до gauge factor: фізичне зерно GF ≈ 2")


# ── Точка входу ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_two_coasts_1938()
    fig_kelvin_to_gaugefactor()
