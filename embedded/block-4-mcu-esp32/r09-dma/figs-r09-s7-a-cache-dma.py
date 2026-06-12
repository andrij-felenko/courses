# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки ⚙️ r09-s7-a-cache-dma.md
«Кеш проти DMA: інвалідація, write-back і вирівнювання буферів»

Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-4-9-7a-1-coherency.svg  — два напрямки розбіжності кеш↔DMA
  fig-4-9-7a-2-alignment.svg  — чому вирівнювання на кешлінію обов'язкове

Стиль svgkit: RAM/DMA-шлях — INK/MUTED, «свіже/правильне» — FIELD,
«старе/застаріле» — POS. Рамки через textbox()/fitbox().
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1: Кеш і DMA — дві версії однієї RAM (два симетричні сценарії)
# ─────────────────────────────────────────────────────────────────────────────
def fig_coherency():
    W, H = 820, 420
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 30, "Когерентність кешу і DMA: два напрямки розбіжності",
                      size=15, bold=True))

    # ── Спільна колонка RAM (центр) ──────────────────────────────────────────
    ram_cx, ram_cy = W // 2, 200
    tb, tw, th = textbox(ram_cx, ram_cy, "RAM\n(фізична пам'ять)", size=13,
                         fill="#e8eaf6", stroke="#5c6bc0", sw=2, min_w=120)
    frags.append(tb)

    # ── Сценарій RX (ліворуч): DMA пише свіже в RAM, у кеші — старе ─────────
    rx_cx = 175
    # DMA Controller — внизу ліворуч
    dma_cx, dma_cy = rx_cx, 330
    tb2, _, _ = textbox(dma_cx, dma_cy, "DMA\nконтролер", size=13,
                        fill="#e3f2fd", stroke=MUTED, sw=1.5, min_w=110)
    frags.append(tb2)

    # Кеш — вгорі ліворуч
    cache_rx_cx, cache_rx_cy = rx_cx, 100
    tb3, _, _ = textbox(cache_rx_cx, cache_rx_cy,
                        "Кеш даних\n(стара копія)", size=13,
                        fill="#fce4ec", stroke=POS, sw=2, min_w=120)
    frags.append(tb3)

    # Стрілка DMA → RAM (свіже, зелена)
    frags.append(arrow(dma_cx + 60, dma_cy, ram_cx - 65, ram_cy + 30, color=FIELD, sw=2.2))
    frags.append(text((dma_cx + 60 + ram_cx - 65) // 2, dma_cy - 12,
                      "пише свіже", size=11, color=FIELD))

    # Стрілка Ядро → Кеш (читає старе, червона)
    frags.append(arrow(cache_rx_cx + 60, cache_rx_cy, ram_cx - 65, ram_cy - 30,
                       color=MUTED, sw=1.5))
    frags.append(text((cache_rx_cx + 60 + ram_cx - 65) // 2, cache_rx_cy + 20,
                      "кеш ← старе", size=11, color=POS))

    # Ядро читає з кешу (стрілка вгору від кешу)
    core_rx_cx, core_rx_cy = rx_cx - 20, cache_rx_cy - 60
    tb_core, _, _ = textbox(core_rx_cx, core_rx_cy, "Ядро", size=13,
                            fill=FILL, stroke=LINE, sw=1.5, min_w=70)
    frags.append(tb_core)
    frags.append(arrow(cache_rx_cx, cache_rx_cy - 25, core_rx_cx + 10, core_rx_cy + 20,
                       color=POS, sw=2))
    frags.append(text(rx_cx - 50, (cache_rx_cy - 25 + core_rx_cy + 20) // 2,
                      "читає СТАРЕ!", size=11, color=POS, bold=True))

    # Підпис-ліки RX
    fix_rx, _, _ = textbox(rx_cx, 390,
                           "invalidate перед читанням", size=12,
                           fill="#e8f5e9", stroke=FIELD, sw=2, min_w=180)
    frags.append(fix_rx)

    # Заголовок сценарію RX
    frags.append(text(rx_cx, 58, "RX: DMA → RAM → ядро", size=13, bold=True, color=INK))

    # ── Сценарій TX (праворуч): ядро пише в кеш, у RAM — старе ──────────────
    tx_cx = W - 175
    # Кеш TX — вгорі праворуч
    cache_tx_cx, cache_tx_cy = tx_cx, 100
    tb4, _, _ = textbox(cache_tx_cx, cache_tx_cy,
                        "Кеш даних\n(свіжий запис)", size=13,
                        fill="#e8f5e9", stroke=FIELD, sw=2, min_w=120)
    frags.append(tb4)

    # DMA TX — внизу праворуч
    dma_tx_cx, dma_tx_cy = tx_cx, 330
    tb5, _, _ = textbox(dma_tx_cx, dma_tx_cy, "DMA\nконтролер", size=13,
                        fill="#e3f2fd", stroke=MUTED, sw=1.5, min_w=110)
    frags.append(tb5)

    # Ядро пише в кеш
    core_tx_cx, core_tx_cy = tx_cx + 20, cache_tx_cy - 60
    tb_core2, _, _ = textbox(core_tx_cx, core_tx_cy, "Ядро", size=13,
                             fill=FILL, stroke=LINE, sw=1.5, min_w=70)
    frags.append(tb_core2)
    frags.append(arrow(core_tx_cx - 10, core_tx_cy + 20, cache_tx_cx, cache_tx_cy - 25,
                       color=FIELD, sw=2))
    frags.append(text(tx_cx + 55, (core_tx_cy + 20 + cache_tx_cy - 25) // 2,
                      "пише свіже", size=11, color=FIELD))

    # Кеш → RAM відкладено (write-back іще не відбувся) — пунктир
    frags.append(line(cache_tx_cx - 60, cache_tx_cy, ram_cx + 65, ram_cy - 30,
                      color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text((cache_tx_cx - 60 + ram_cx + 65) // 2, cache_tx_cy + 18,
                      "write-back ще не відбувся", size=10, color=MUTED))

    # DMA читає з RAM — бере старе
    frags.append(arrow(ram_cx + 65, ram_cy + 30, dma_tx_cx - 55, dma_tx_cy,
                       color=POS, sw=2.2))
    frags.append(text((ram_cx + 65 + dma_tx_cx - 55) // 2, dma_tx_cy - 14,
                      "везе СТАРЕ!", size=11, color=POS, bold=True))

    # Підпис-ліки TX
    fix_tx, _, _ = textbox(tx_cx, 390,
                           "write-back перед стартом DMA", size=12,
                           fill="#e8f5e9", stroke=FIELD, sw=2, min_w=200)
    frags.append(fix_tx)

    # Заголовок сценарію TX
    frags.append(text(tx_cx, 58, "TX: ядро → кеш → DMA → RAM", size=13, bold=True, color=INK))

    # ── Роздільник ────────────────────────────────────────────────────────────
    frags.append(line(W // 2, 55, W // 2, 375, color=MUTED, sw=1, dash="4,4"))

    path = os.path.join(OUT, "fig-4-9-7a-1-coherency.svg")
    render(path, W, H, *frags)
    print("Написано:", path)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2: Вирівнювання буфера на кешлінію
# ─────────────────────────────────────────────────────────────────────────────
def fig_alignment():
    W, H = 820, 380
    LINE_SZ = 32   # байти в кешлінії ESP32-S3
    frags = []

    frags.append(text(W // 2, 28, "Вирівнювання DMA-буфера на кешлінію (32 байти, ESP32-S3)",
                      size=15, bold=True))

    # ── Параметри стрічки пам'яті ─────────────────────────────────────────────
    stripe_x0 = 60
    stripe_w = W - 120
    cell_w = stripe_w / 7   # 7 клітинок (кешліній), видимих на схемі
    stripe_h = 36

    def draw_stripe(y, label_y_off=0):
        """Намалювати стрічку з 7 кешліній + підписати межі."""
        cells = []
        for i in range(7):
            cx = stripe_x0 + i * cell_w
            cells.append(rect(cx, y, cell_w, stripe_h, fill="#f5f5f5", stroke=MUTED, sw=1))
            # Межа лінії — підпис (кожна 2-га для читабельності)
            if i % 2 == 0:
                cells.append(text(cx + 2, y + stripe_h + 14 + label_y_off,
                                  "+%d" % (i * LINE_SZ), size=10, color=MUTED, anchor="start"))
        return cells

    # ── ПОГАНО: невирівняний буфер ────────────────────────────────────────────
    bad_y = 70
    frags.append(text(stripe_x0, bad_y - 14, "Невирівняний буфер — небезпечно", size=13,
                      bold=True, color=POS, anchor="start"))
    frags.extend(draw_stripe(bad_y))

    # Буфер починається посередині лінії 1, закінчується посередині лінії 4
    buf_start_frac = 1.4   # у клітинках від початку стрічки
    buf_end_frac = 3.7
    bx0 = stripe_x0 + buf_start_frac * cell_w
    bw = (buf_end_frac - buf_start_frac) * cell_w
    frags.append(rect(bx0, bad_y, bw, stripe_h,
                      fill="#ffe0e0", stroke=POS, sw=2.5, rx=3))
    frags.append(text(bx0 + bw / 2, bad_y + stripe_h / 2 + 5,
                      "буфер (не вирівняний)", size=11, color=POS))

    # Позначити «чужі» дані у крайніх лініях
    alien_w = (buf_start_frac - 1) * cell_w
    frags.append(rect(stripe_x0 + 1 * cell_w, bad_y, alien_w, stripe_h,
                      fill="#ffccbc", stroke=POS, sw=1.5, rx=2))
    frags.append(text(stripe_x0 + 1 * cell_w + alien_w / 2, bad_y + stripe_h / 2 + 5,
                      "чуже", size=10, color=POS))

    alien_w2 = (3 - (buf_end_frac - 3)) * cell_w
    # Просто виділити небезпечну зону без точного обчислення
    frags.append(rect(stripe_x0 + buf_end_frac * cell_w, bad_y,
                      (4 - buf_end_frac) * cell_w, stripe_h,
                      fill="#ffccbc", stroke=POS, sw=1.5, rx=2))
    frags.append(text(stripe_x0 + (buf_end_frac + (4 - buf_end_frac) / 2) * cell_w,
                      bad_y + stripe_h / 2 + 5, "чуже", size=10, color=POS))

    # Підпис наслідку
    bad_box, _, _ = textbox(W // 2, bad_y + stripe_h + 42,
                            "invalidate/write-back цілої лінії → «чужі» дані знищено!", size=12,
                            fill="#fce4ec", stroke=POS, sw=2, min_w=460)
    frags.append(bad_box)

    # ── ДОБРЕ: вирівняний буфер ───────────────────────────────────────────────
    good_y = 230
    frags.append(text(stripe_x0, good_y - 14, "Вирівняний на 32 Б і доповнений — безпечно", size=13,
                      bold=True, color=FIELD, anchor="start"))
    frags.extend(draw_stripe(good_y, label_y_off=4))

    # Буфер точно займає лінії 1, 2, 3 — вирівняно і кратно
    buf_g_start = 1   # клітинка
    buf_g_end = 4     # клітинка (не включно)
    gx0 = stripe_x0 + buf_g_start * cell_w
    gw = (buf_g_end - buf_g_start) * cell_w
    frags.append(rect(gx0, good_y, gw, stripe_h,
                      fill="#c8e6c9", stroke=FIELD, sw=2.5, rx=3))
    frags.append(text(gx0 + gw / 2, good_y + stripe_h / 2 + 5,
                      "буфер (вирівняний + кратний 32 Б)", size=11, color=FIELD))

    good_box, _, _ = textbox(W // 2, good_y + stripe_h + 42,
                             "invalidate/write-back чіпає лише свої лінії — сусіди не постраждають", size=12,
                             fill="#e8f5e9", stroke=FIELD, sw=2, min_w=520)
    frags.append(good_box)

    # Підписи кешліній на обох стрічках
    frags.append(text(stripe_x0, bad_y + stripe_h + 28, "↕ 32 Б", size=10,
                      color=MUTED, anchor="start"))

    path = os.path.join(OUT, "fig-4-9-7a-2-alignment.svg")
    render(path, W, H, *frags)
    print("Написано:", path)


if __name__ == "__main__":
    fig_coherency()
    fig_alignment()
    print("Усі фігури згенеровано.")
