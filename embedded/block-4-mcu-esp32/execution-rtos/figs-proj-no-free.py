# -*- coding: utf-8 -*-
"""
Фігури для ⚙️-вставки §27.7a — «Жити без free(): статичні пули замість динамічної купи».

Дві фігури:
  fig-27-7a-no-free-1-pool-freelist.svg  — масив блоків + список вільних + операції
  fig-27-7a-no-free-2-heap-vs-pool.svg   — купа (фрагментація) vs пул (суцільна пам'ять)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Додаткові кольори для цих фігур ─────────────────────────────────────────
POOL_BG   = "#e9eefb"   # синювато-блакитний — зайнятий блок
FREE_BG   = "#eef6ef"   # зелений — вільний блок
USED_BG   = "#fbeaea"   # рожевий — «зайнятий» у купі
FRAG_BG   = "#f4f6f8"   # сірий — фрагмент (непридатна дірка)
POOL_STR  = "#1f47b5"   # синій контур пулу
FREE_STR  = "#1f8a3b"   # зелений контур вільного
USED_STR  = "#c0271e"   # червоний контур зайнятого
PTR_COL   = "#7a4fb0"   # фіолетовий — стрілки-вказівники
HEAD_COL  = "#d06c00"   # помаранчевий — голова freeList


# ═══════════════════════════════════════════════════════════════════════════
#  Рис. 4.10.7a.1 — Пул фіксованих блоків і список вільних
# ═══════════════════════════════════════════════════════════════════════════
def fig_pool_freelist():
    W, H = 900, 500
    parts = []

    # ── Заголовок ────────────────────────────────────────────────────────
    parts.append(text(W / 2, 30, "Пул фіксованих блоків: масив + список вільних (free list)",
                      size=16, bold=True))
    parts.append(text(W / 2, 50,
                      "«виділити» = зняти блок з голови O(1); «звільнити» = повернути в голову O(1)",
                      size=11, color=MUTED, italic=True))

    # ── Масив pool[N][S] — 8 блоків ─────────────────────────────────────
    BLK_W, BLK_H = 78, 46
    BLK_GAP = 10
    N = 8
    row_x0 = 50
    row_y = 110   # верхній край рядка блоків

    # Підпис масиву
    parts.append(text(row_x0 + (N * (BLK_W + BLK_GAP) - BLK_GAP) / 2, row_y - 18,
                      "static uint8_t pool[N][S]  —  N=8 блоків × S байтів кожен",
                      size=11.5, color=INK, bold=True))

    # Кольори блоків: 0=вільний,1=вільний,2=зайнятий,3=вільний,4=зайнятий,5=вільний,6=зайнятий,7=вільний
    block_free = [True, True, False, True, False, True, False, True]

    bx_list = []
    for i in range(N):
        bx = row_x0 + i * (BLK_W + BLK_GAP)
        by = row_y
        is_free = block_free[i]
        fill   = FREE_BG  if is_free else POOL_BG
        stroke = FREE_STR if is_free else POOL_STR
        parts.append(rect(bx, by, BLK_W, BLK_H, fill=fill, stroke=stroke, sw=2, rx=5))
        parts.append(text(bx + BLK_W / 2, by + BLK_H / 2 - 6,
                          "pool[%d]" % i, size=11, color=stroke, bold=True))
        if is_free:
            parts.append(text(bx + BLK_W / 2, by + BLK_H / 2 + 10,
                              "→ ptr", size=10, color=PTR_COL, italic=True))
        else:
            parts.append(text(bx + BLK_W / 2, by + BLK_H / 2 + 10,
                              "(дані)", size=10, color=MUTED, italic=True))
        bx_list.append(bx)

    # Легенда кольорів
    leg_x = row_x0
    leg_y = row_y + BLK_H + 16
    parts.append(rect(leg_x, leg_y, 14, 14, fill=FREE_BG, stroke=FREE_STR, sw=1.5, rx=3))
    parts.append(text(leg_x + 20, leg_y + 11, "вільний блок (у free list)", size=10.5, color=FREE_STR, anchor="start"))
    parts.append(rect(leg_x + 200, leg_y, 14, 14, fill=POOL_BG, stroke=POOL_STR, sw=1.5, rx=3))
    parts.append(text(leg_x + 220, leg_y + 11, "зайнятий (у задачі)", size=10.5, color=POOL_STR, anchor="start"))

    # ── freeList (голова) — вказівник на перший вільний ─────────────────
    HEAD_Y = 240
    head_cx = 88    # над pool[0]
    tb, tw, th = textbox(head_cx, HEAD_Y, "freeList\n(голова)",
                         size=12, fill="#fff6e0", stroke=HEAD_COL, sw=2.2,
                         color=HEAD_COL, bold=True, pad=10)
    parts.append(tb)

    # Стрілка від freeList вниз до pool[0]
    parts.append(arrow(head_cx, HEAD_Y + th / 2 + 2, bx_list[0] + BLK_W / 2, row_y + BLK_H,
                       color=HEAD_COL, sw=2.2))

    # ── Стрілки: free list pool[0]→pool[1]→pool[3]→pool[5]→pool[7]→NULL ─
    free_chain = [0, 1, 3, 5, 7]
    for idx in range(len(free_chain) - 1):
        src = free_chain[idx]
        dst = free_chain[idx + 1]
        sx = bx_list[src] + BLK_W - 4
        sy = row_y + BLK_H / 2
        ex = bx_list[dst] + 4
        ey = row_y + BLK_H / 2
        parts.append(arrow(sx, sy, ex, ey, color=PTR_COL, sw=1.8))

    # NULL після останнього вільного
    last_free = free_chain[-1]
    parts.append(text(bx_list[last_free] + BLK_W + 8, row_y + BLK_H / 2 + 5,
                      "NULL", size=12, color=PTR_COL, bold=True, anchor="start"))

    # ── Операції alloc і free ────────────────────────────────────────────
    OP_Y = 340
    # Ліво — ALLOC
    alloc_cx = 230
    tb2, tw2, th2 = textbox(alloc_cx, OP_Y,
                             "ALLOC — O(1)\nзняти блок з голови:\np = freeList\nfreeList = *p",
                             size=12, fill=FREE_BG, stroke=FREE_STR, sw=2, pad=12,
                             color=FREE_STR, bold=False)
    parts.append(tb2)
    # Заголовок операції
    parts.append(text(alloc_cx, OP_Y - th2 / 2 - 14, "pool_alloc()", size=13,
                      color=FREE_STR, bold=True))
    # Стрілка від freeList до alloc-блоку
    parts.append(arrow(head_cx + tw / 2 + 2, HEAD_Y, alloc_cx - tw2 / 2 - 2, OP_Y,
                       color=FREE_STR, sw=1.8))

    # Право — FREE
    free_cx = 640
    tb3, tw3, th3 = textbox(free_cx, OP_Y,
                             "FREE — O(1)\nповернути блок у голову:\n*p = freeList\nfreeList = p",
                             size=12, fill="#ffe9e9", stroke=USED_STR, sw=2, pad=12,
                             color=USED_STR, bold=False)
    parts.append(tb3)
    parts.append(text(free_cx, OP_Y - th3 / 2 - 14, "pool_free(p)", size=13,
                      color=USED_STR, bold=True))

    # Висновок
    parts.append(text(W / 2, H - 22,
                      "Жодного malloc/free! Уся «динаміка» — два перечеплення вказівника → O(1) і нуль фрагментації.",
                      size=12, color=INK, bold=False, italic=True))

    render(os.path.join(OUT, "fig-27-7a-no-free-1-pool-freelist.svg"), W, H,
           *parts, title=None)
    print("fig-27-7a-no-free-1-pool-freelist.svg — OK")


# ═══════════════════════════════════════════════════════════════════════════
#  Рис. 4.10.7a.2 — Купа проти пулу
# ═══════════════════════════════════════════════════════════════════════════
def fig_heap_vs_pool():
    W, H = 860, 480
    parts = []

    # ── Заголовок ────────────────────────────────────────────────────────
    parts.append(text(W / 2, 30, "Купа проти пулу на мікроконтролері",
                      size=16, bold=True))
    parts.append(text(W / 2, 50,
                      "однакова вихідна RAM — різна доля за тижні роботи",
                      size=11, color=MUTED, italic=True))

    PANEL_Y = 70
    PANEL_H = 370
    PANEL_W = 370

    # ═══ ЛІВА ПАНЕЛЬ — КУПА ══════════════════════════════════════════════
    HX = 40
    parts.append(rect(HX, PANEL_Y, PANEL_W, PANEL_H,
                      fill="#fff8f8", stroke=USED_STR, sw=2, rx=8))
    parts.append(text(HX + PANEL_W / 2, PANEL_Y + 26,
                      "Купа (heap)", size=15, color=USED_STR, bold=True))

    # Блоки різного розміру — симуляція фрагментації
    heap_blocks = [
        # (y_offset, height, is_free, label)
        (50,  44, False, "зайнято (A)"),
        (100, 28, True,  "вільно ← дірка"),
        (134, 56, False, "зайнято (B)"),
        (196, 20, True,  "вільно ← дірка"),
        (222, 72, False, "зайнято (C)"),
        (300, 36, True,  "вільно ← дірка"),
        (342, 44, False, "зайнято (D)"),
    ]
    BW = PANEL_W - 40
    for (yo, bh, is_free, label) in heap_blocks:
        bx = HX + 20
        by = PANEL_Y + yo
        if is_free:
            parts.append(rect(bx, by, BW, bh, fill=FRAG_BG, stroke="#aaaaaa", sw=1.2, rx=3))
            parts.append(text(bx + BW / 2, by + bh / 2 + 4,
                              label, size=10, color="#999999", italic=True))
        else:
            parts.append(rect(bx, by, BW, bh, fill=USED_BG, stroke=USED_STR, sw=1.5, rx=3))
            parts.append(text(bx + BW / 2, by + bh / 2 + 4,
                              label, size=10.5, color=USED_STR, bold=True))

    # Позначки проблем
    anno_x = HX + PANEL_W - 8
    parts.append(text(anno_x + 4, PANEL_Y + 114, "← фрагмент", size=9.5, color="#bb4444",
                      anchor="start", italic=True))
    parts.append(text(anno_x + 4, PANEL_Y + 206, "← фрагмент", size=9.5, color="#bb4444",
                      anchor="start", italic=True))
    parts.append(text(anno_x + 4, PANEL_Y + 318, "← фрагмент", size=9.5, color="#bb4444",
                      anchor="start", italic=True))

    # Підсумок купи
    sum_y = PANEL_Y + PANEL_H + 18
    tb_h, tw_h, th_h = textbox(HX + PANEL_W / 2, sum_y,
                                "рваний час malloc/free\nNULL зненацька через тижні\nфрагменти є — великий запит не влазить",
                                size=11, fill="#fbeaea", stroke=USED_STR, sw=1.8, pad=10,
                                color=USED_STR)
    parts.append(tb_h)

    # ═══ ПРАВА ПАНЕЛЬ — ПУЛ ════════════════════════════════════════════
    PX = W - 40 - PANEL_W
    parts.append(rect(PX, PANEL_Y, PANEL_W, PANEL_H,
                      fill="#f0f8f2", stroke=FREE_STR, sw=2, rx=8))
    parts.append(text(PX + PANEL_W / 2, PANEL_Y + 26,
                      "Пул (fixed-size pool)", size=15, color=FREE_STR, bold=True))

    # Рівні однакові блоки
    pool_bh = 42
    pool_gap = 6
    pool_labels = ["блок 0", "блок 1", "блок 2\n(у задачі)", "блок 3",
                   "блок 4\n(у задачі)", "блок 5", "блок 6"]
    pool_used   = [False, False, True, False, True, False, False]
    PBW = PANEL_W - 40
    py0 = PANEL_Y + 48
    for i, (lbl, used) in enumerate(zip(pool_labels, pool_used)):
        bx = PX + 20
        by = py0 + i * (pool_bh + pool_gap)
        fill   = POOL_BG  if used else FREE_BG
        stroke = POOL_STR if used else FREE_STR
        parts.append(rect(bx, by, PBW, pool_bh, fill=fill, stroke=stroke, sw=1.5, rx=3))
        parts.append(text(bx + PBW / 2, by + pool_bh / 2 + 4,
                          lbl, size=10.5, color=stroke, bold=used))

    # Позначка «N×S — відома наперед»
    parts.append(text(PX + PANEL_W / 2, PANEL_Y + PANEL_H - 14,
                      "N×S байтів — відомо НАПЕРЕД", size=10.5,
                      color=FREE_STR, bold=True))

    # Підсумок пулу
    tb_p, tw_p, th_p = textbox(PX + PANEL_W / 2, sum_y,
                                "O(1) завжди — детермінований час\nнуль фрагментації за роки роботи\nстеля пам'яті відома ще на етапі проєкту",
                                size=11, fill="#e8f6eb", stroke=FREE_STR, sw=1.8, pad=10,
                                color=FREE_STR)
    parts.append(tb_p)

    # ── Стрілка VS по середині ──────────────────────────────────────────
    mid_x = W / 2
    parts.append(text(mid_x, PANEL_Y + PANEL_H / 2 + 8,
                      "VS", size=26, color=MUTED, bold=True))

    render(os.path.join(OUT, "fig-27-7a-no-free-2-heap-vs-pool.svg"), W, H,
           *parts, title=None)
    print("fig-27-7a-no-free-2-heap-vs-pool.svg — OK")


if __name__ == "__main__":
    fig_pool_freelist()
    fig_heap_vs_pool()
    print("Усі фігури згенеровано.")
