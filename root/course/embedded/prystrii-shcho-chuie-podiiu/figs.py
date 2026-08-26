# -*- coding: utf-8 -*-
import os
import sys

# Підключаємо svgkit зі scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Багаторівневий каскад пробудження (Cascade Wakeup Pipeline) ──────────────
def fig_cascade_architecture():
    W, H = 820, 350
    p = []
    cy = 130

    stages = [
        ("Рівень 0: VAD / Компаратор", "Струм: < 50 мкА\nЧас: постійно (99.9%)\nПеревірка: поріг енергії", "#f4f6f8", LINE),
        ("Рівень 1: Спектральний аналіз", "Струм: 1–3 мА\nЧас: 10–20 мс на кадр\nПеревірка: MFCC банки (32)", "#eef4ff", NEG),
        ("Рівень 2: Згортка INT8 CNN", "Струм: 15–20 мА\nЧас: 5–10 мс на сплеск\nПеревірка: DS-CNN класифікатор", "#eafaf0", FIELD),
        ("Цільова дія", "Пробудження системи,\nзапис або тривожний\nпакет у радіоканал", "#fff7e6", "#b8860b"),
    ]

    n = len(stages)
    bw, bh, gap = 166, 96, 32
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2
    edges = []

    for i, (title, sub, fl, st) in enumerate(stages):
        p.append(fitbox(x, cy - bh / 2, bw, bh, title + "\n" + sub, size=11, bold=True, fill=fl, stroke=st, sw=1.8))
        edges.append((x, x + bw))
        if i > 0:
            p.append(arrow(edges[i - 1][1] + 2, cy, x - 2, cy, color=INK, sw=2.0))
        x += bw + gap

    # Зверху над блоками — фільтрація подій і відкидання шуму
    p.append(text((edges[0][0] + edges[0][1]) / 2, cy - bh / 2 - 20, "відсікає тишу й фоновий шум", size=10, color=MUTED, italic=True))
    p.append(text((edges[1][0] + edges[1][1]) / 2, cy - bh / 2 - 20, "відсікає нецільовий спектр", size=10, color=NEG, italic=True))
    p.append(text((edges[2][0] + edges[2][1]) / 2, cy - bh / 2 - 20, "розпізнає акустичний патерн", size=10, color=FIELD, italic=True))

    # Стрілки скидання назад у сон
    for i in range(3):
        ex = (edges[i][0] + edges[i][1]) / 2
        p.append(line(ex, cy + bh / 2 + 2, ex, cy + bh / 2 + 22, color=POS, sw=1.3))
        p.append(arrow(ex, cy + bh / 2 + 22, ex, cy + bh / 2 + 36, color=POS, sw=1.3))
        p.append(text(ex, cy + bh / 2 + 48, "хибна тривога → сон", size=9, color=POS))

    p.append(text(W / 2, cy + bh / 2 + 82, "середній струм автономного пристрою: < 80 мкА (понад 2 роки роботи від елемента 2000 мА·год)", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "cascade-architecture.svg"), W, H, *p, title="Ієрархічний каскад фільтрації та пробудження MCU")


# ── 2. Подвійна буферизація I2S DMA (Ping-Pong Buffer) ──────────────────────────
def fig_dma_ping_pong():
    W, H = 820, 330
    p = []

    # Верхній блок — кільцевий масив DMA
    bx, by, bw, bh = 70, 70, 680, 52
    half_w = bw / 2

    # Буфер 0 (ліва половина)
    p.append(rect(bx, by, half_w, bh, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(bx + half_w / 2, by + 22, "Буфер A (відліки 0 .. N-1)", size=12, color=NEG, bold=True))
    p.append(text(bx + half_w / 2, by + 40, "Half-Transfer блок", size=10, color=MUTED))

    # Буфер 1 (права половина)
    p.append(rect(bx + half_w, by, half_w, bh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(bx + half_w + half_w / 2, by + 22, "Буфер B (відліки N .. 2N-1)", size=12, color=FIELD, bold=True))
    p.append(text(bx + half_w + half_w / 2, by + 40, "Transfer-Complete блок", size=10, color=MUTED))

    # Мітка DMA запису
    p.append(text(bx + half_w / 2, by - 16, "DMA пише в Буфер A", size=11, color=NEG, bold=True))
    p.append(arrow(bx + half_w / 2, by - 8, bx + half_w / 2, by - 2, color=NEG, sw=1.8))

    # Подія Half Transfer (HT)
    ht_x = bx + half_w
    p.append(line(ht_x, by, ht_x, by + bh + 40, color=POS, sw=1.6, dash="4 3"))
    p.append(text(ht_x, by + bh + 54, "Переривання DMA_IT_HT", size=10, color=POS, bold=True))
    p.append(text(ht_x, by + bh + 68, "(Буфер A готовий до обробки)", size=9, color=MUTED))

    # Подія Transfer Complete (TC)
    tc_x = bx + bw
    p.append(line(tc_x, by, tc_x, by + bh + 40, color=POS, sw=1.6, dash="4 3"))
    p.append(text(tc_x, by + bh + 54, "Переривання DMA_IT_TC", size=10, color=POS, bold=True))
    p.append(text(tc_x, by + bh + 68, "(Буфер B готовий до обробки)", size=9, color=MUTED))

    # Робота CPU в нижньому блоці
    cpu_y = by + bh + 100
    p.append(rect(bx, cpu_y, half_w - 20, 44, fill="#fff7e6", stroke="#b8860b", sw=1.5))
    p.append(text(bx + (half_w - 20) / 2, cpu_y + 18, "CPU обробляє Буфер B", size=11, color="#b8860b", bold=True))
    p.append(text(bx + (half_w - 20) / 2, cpu_y + 34, "поки DMA безперервно пише в Буфер A", size=9, color=MUTED))

    p.append(rect(bx + half_w + 20, cpu_y, half_w - 20, 44, fill="#fff7e6", stroke="#b8860b", sw=1.5))
    p.append(text(bx + half_w + 20 + (half_w - 20) / 2, cpu_y + 18, "CPU обробляє Буфер A", size=11, color="#b8860b", bold=True))
    p.append(text(bx + half_w + 20 + (half_w - 20) / 2, cpu_y + 34, "поки DMA безперервно пише в Буфер B", size=9, color=MUTED))

    render(os.path.join(OUT, "dma-ping-pong.svg"), W, H, *p, title="Подвійна буферизація I2S через кільцевий DMA")


# ── 3. Банк мел-фільтрів (Mel Filterbank) ───────────────────────────────────────
def fig_mel_filterbank():
    W, H = 820, 360
    p = []

    ax0, ay0, aw, ah = 80, 80, 660, 180

    # Осі
    p.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=INK, sw=1.5))
    p.append(line(ax0, ay0, ax0, ay0 + ah, color=INK, sw=1.5))

    p.append(text(ax0 - 10, ay0 + 6, "1.0", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 10, ay0 + ah, "0.0", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 24, ay0 + ah / 2, "Вага фільтра", size=11, color=INK, anchor="middle"))

    p.append(text(ax0, ay0 + ah + 22, "0 Гц", size=10, color=MUTED, anchor="middle"))
    p.append(text(ax0 + aw * 0.25, ay0 + ah + 22, "1000 Гц", size=10, color=MUTED, anchor="middle"))
    p.append(text(ax0 + aw * 0.55, ay0 + ah + 22, "3000 Гц", size=10, color=MUTED, anchor="middle"))
    p.append(text(ax0 + aw, ay0 + ah + 22, "8000 Гц (f_s / 2)", size=10, color=MUTED, anchor="middle"))
    p.append(text(ax0 + aw / 2, ay0 + ah + 42, "Лінійна частота FFT бінів f (Гц) →", size=11, color=INK))

    # Створюємо трикутні фільтри, що розширюються нелінійно за шкалою Мела
    # Центри фільтрів у відносних координатах осі
    centers = [0.03, 0.07, 0.12, 0.18, 0.25, 0.34, 0.45, 0.58, 0.74, 0.94]
    filter_edges = [0.0] + centers + [1.0]

    for i in range(len(centers)):
        c = centers[i]
        left = filter_edges[i]
        right = filter_edges[i + 2]

        lx = ax0 + left * aw
        cx = ax0 + c * aw
        rx = ax0 + right * aw
        ty = ay0 + 10
        by = ay0 + ah

        # Колір трикутника чергується
        col = FIELD if i % 2 == 0 else NEG
        pts = f"{lx:.1f},{by:.1f} {cx:.1f},{ty:.1f} {rx:.1f},{by:.1f}"
        p.append(f'<polygon points="{pts}" fill="{col}" fill-opacity="0.15" stroke="{col}" stroke-width="1.6"/>')
        p.append(text(cx, ty - 6, f"M{i+1}", size=9, color=col, bold=True))

    p.append(text(ax0 + 60, ay0 + 30, "Вузькі смуги (низькі частоти)", size=10, color=FIELD, italic=True, anchor="start"))
    p.append(text(ax0 + aw - 10, ay0 + 30, "Широкі смуги (високі частоти)", size=10, color=NEG, italic=True, anchor="end"))

    p.append(text(W / 2, ay0 + ah + 72, "Формула шкали Мела:   m = 2595 · log10(1 + f / 700)", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "mel-filterbank.svg"), W, H, *p, title="Банк трикутних мел-фільтрів для частотного аналізу")


# ── 4. Архітектура DS-CNN та конвеєр INT8 квантування ───────────────────────────
def fig_ds_cnn_int8():
    W, H = 820, 360
    p = []
    cy = 130

    stages = [
        ("Вхідні ознаки", "MFCC матриця\n32 канали × 40 кадрів\nТип: int8_t", "#f4f6f8", LINE),
        ("Depthwise Conv", "Просторова згортка\n3×3 по кожному каналу\nБез крос-каналів", "#eef4ff", NEG),
        ("Pointwise Conv", "Згортка 1×1\nЛінійна комбінація\nміж усіма каналами", "#eafaf0", FIELD),
        ("INT8 Квантування", "Множення на M0\nАрифметичний зсув >> s\nНасичення __SSAT", "#fff7e6", "#b8860b"),
        ("Класифікація", "Softmax / Подія\nЙмовірність класу:\n[постріл, скло, голос]", "#f2ecf8", "#8a5fb0"),
    ]

    n = len(stages)
    bw, bh, gap = 142, 94, 24
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2
    edges = []

    for i, (title, sub, fl, st) in enumerate(stages):
        p.append(fitbox(x, cy - bh / 2, bw, bh, title + "\n" + sub, size=10, bold=True, fill=fl, stroke=st, sw=1.8))
        edges.append((x, x + bw))
        if i > 0:
            p.append(arrow(edges[i - 1][1] + 2, cy, x - 2, cy, color=INK, sw=1.8))
        x += bw + gap

    # Пояснення економії обчислень
    p.append(text(W / 2, cy - bh / 2 - 24, "Depthwise Separable Conv економить ~85% операцій множення (MAC) проти звичайної 2D згортки", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, cy + bh / 2 + 36, "Цілочисельний конвеєр Cortex-M: SIMD SMLAD інструкції + CMSIS-NN бібліотека", size=12, color=INK, bold=True))
    p.append(text(W / 2, cy + bh / 2 + 60, "Пам'ять ваг зменшено у 4 рази (INT8 проти Float32) — розмір моделі < 25 КБ Flash", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "ds-cnn-int8.svg"), W, H, *p, title="Архітектура DS-CNN та INT8 квантування для Cortex-M")


if __name__ == "__main__":
    fig_cascade_architecture()
    fig_dma_ping_pong()
    fig_mel_filterbank()
    fig_ds_cnn_int8()
    print("OK: 4 figures generated successfully in", OUT)
