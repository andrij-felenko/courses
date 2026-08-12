# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdecea"
COOL   = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"

# ── 1. Зони пам'яті та три пороги Watermarks ─────────────────────────────
def fig_watermark_levels():
    W, H = 1200, 700
    p = []

    # Заголовок
    p.append(text(60, 40, "Рівні водяних знаків (watermarks) у зоні пам'яті Linux",
                  size=16, color=INK, anchor="start", bold=True))

    # Ліва колонка — Резервуар / шкала вільної пам'яті
    scale_x = 180
    scale_w = 200
    p.append(rect(scale_x, 100, scale_w, 480, fill="none", stroke=LINE, sw=2, rx=8))
    
    # Зони на шкалі
    # 1. Понад HIGH — нормальний стан
    p.append(rect(scale_x + 4, 104, scale_w - 8, 116, fill=GREENF, stroke="none", rx=4))
    p.append(text(scale_x + scale_w/2, 160, "Нормальний стан\n(вільної пам'яті достатньо)", size=12, color=FIELD, bold=True))

    # 2. Між LOW та HIGH — зона роботи kswapd
    p.append(rect(scale_x + 4, 224, scale_w - 8, 116, fill=COOL, stroke="none", rx=0))
    p.append(text(scale_x + scale_w/2, 280, "Зона роботи kswapd\n(фонове витіснення)", size=12, color=NEG, bold=True))

    # 3. Між MIN та LOW — зона підвищеного тиску
    p.append(rect(scale_x + 4, 344, scale_w - 8, 116, fill=PALE, stroke="none", rx=0))
    p.append(text(scale_x + scale_w/2, 400, "Зона тиску пам'яті\n(kswapd працює агресивно)", size=12, color=MUTED, bold=True))

    # 4. Нижче MIN — критичний резерв
    p.append(rect(scale_x + 4, 464, scale_w - 8, 112, fill=WARM, stroke="none", rx=4))
    p.append(text(scale_x + scale_w/2, 520, "Аварійний резерв\n(лише GFP_ATOMIC)", size=12, color=POS, bold=True))

    # Горизонтальні лінії порогів
    p.append(line(140, 224, 440, 224, color=FIELD, sw=2.5, dash="6 3"))
    p.append(fitbox(530, 224, 160, 44, "WMARK_HIGH", size=13, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    p.append(line(140, 344, 440, 344, color=NEG, sw=2.5, dash="6 3"))
    p.append(fitbox(530, 344, 160, 44, "WMARK_LOW", size=13, fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))

    p.append(line(140, 464, 440, 464, color=POS, sw=2.5, dash="6 3"))
    p.append(fitbox(530, 464, 160, 44, "WMARK_MIN", size=13, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    # Пояснення праворуч
    p.append(fitbox(900, 224, 420, 68, "kswapd засинає при досягненні WMARK_HIGH\n(цільовий рівень вільної пам'яті)", size=12, fill=SOFT, stroke=FIELD, sw=1.4, color=INK))
    p.append(fitbox(900, 344, 420, 68, "kswapd прокидається при падінні нижче WMARK_LOW\n(асинхронний старт фонового витіснення)", size=12, fill=SOFT, stroke=NEG, sw=1.4, color=INK))
    p.append(fitbox(900, 464, 420, 68, "Падіння нижче WMARK_MIN вмикає Direct Reclaim\n(процеси занурюються у синхронне витіснення)", size=12, fill=SOFT, stroke=POS, sw=1.4, color=INK))

    # Стрілки-зв'язки
    p.append(arrow(615, 224, 685, 224, color=FIELD, sw=1.6))
    p.append(arrow(615, 344, 685, 344, color=NEG, sw=1.6))
    p.append(arrow(615, 464, 685, 464, color=POS, sw=1.6))

    # Блок про watermark_boost внизу
    p.append(rect(60, 600, 1080, 75, fill=PALE, stroke=LINE, sw=1.5, rx=8))
    p.append(text(80, 625, "Тимчасовий зсув (Watermark Boost):", size=13, color=INK, anchor="start", bold=True))
    p.append(text(80, 652, "При невдалій фрагментації для високих порядків ядро тимчасово піднімає пороги WMARK_LOW та WMARK_HIGH, змушуючи kswapd працювати агресивніше.", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "watermark-levels.svg"), W, H, *p,
           title="Рівні водяних знаків у зоні пам'яті Linux")


# ── 2. Списки LRU: ротація Active та Inactive ─────────────────────────────
def fig_lru_rotation_loop():
    W, H = 1200, 680
    p = []

    p.append(text(60, 40, "Структура списків LRU та алгоритм двократного дотику (Two-Touch)",
                  size=16, color=INK, anchor="start", bold=True))

    # Ліва рамка: File LRU (fill="none" щоб не вважатися закритим блоком)
    p.append(rect(50, 80, 520, 560, fill="none", stroke=LINE, sw=1.6, rx=10))
    p.append(text(310, 110, "File LRU (Кеш файлів / Page Cache)", size=15, color=NEG, bold=True))

    p.append(fitbox(310, 170, 420, 70, "Active File List\n(Гарячі сторінки файлового кешу)", size=13, fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))
    p.append(fitbox(310, 340, 420, 70, "Inactive File List\n(Холодні сторінки, кандидати на витіснення)", size=13, fill=PALE, stroke=MUTED, sw=1.6, color=INK, bold=True))

    # Стрілка зниження (Aging) Active -> Inactive
    p.append(arrow(200, 208, 200, 302, color=MUTED, sw=2))
    p.append(text(190, 255, "Demote (aging)\nshrink_active_list()", size=11, color=MUTED, anchor="end"))

    # Стрілка підвищення (Promotion) Inactive -> Active
    p.append(arrow(420, 302, 420, 208, color=NEG, sw=2))
    p.append(text(430, 255, "Promote (2-ий дотик)\nmark_page_accessed()", size=11, color=NEG, anchor="start"))

    # Звільнення з Inactive File
    p.append(fitbox(310, 520, 420, 80, "Звільнення kswapd:\nClean page -> миттєвий drop\nDirty page -> writeback на диск", size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))
    p.append(arrow(310, 378, 310, 477, color=FIELD, sw=2))

    # Права рамка: Anon LRU
    p.append(rect(630, 80, 520, 560, fill="none", stroke=LINE, sw=1.6, rx=10))
    p.append(text(890, 110, "Anon LRU (Анонімна пам'ять процесів)", size=15, color=POS, bold=True))

    p.append(fitbox(890, 170, 420, 70, "Active Anon List\n(Купа/стек процесів під активним доступом)", size=13, fill=WARM, stroke=POS, sw=1.6, color=INK, bold=True))
    p.append(fitbox(890, 340, 420, 70, "Inactive Anon List\n(Невикористовувані сторінки процесів)", size=13, fill=PALE, stroke=MUTED, sw=1.6, color=INK, bold=True))

    # Стрілка зниження (Aging) Active -> Inactive
    p.append(arrow(780, 208, 780, 302, color=MUTED, sw=2))
    p.append(text(770, 255, "Demote (aging)", size=11, color=MUTED, anchor="end"))

    # Стрілка підвищення (Promotion) Inactive -> Active
    p.append(arrow(1000, 302, 1000, 208, color=POS, sw=2))
    p.append(text(1010, 255, "Promote (2-ий дотик)", size=11, color=POS, anchor="start"))

    # Звільнення з Inactive Anon
    p.append(fitbox(890, 520, 420, 80, "Звільнення kswapd:\nЗапис у Swap -> звільнення RAM\n(регулюється vm.swappiness)", size=12, fill=WARM, stroke=POS, sw=1.6, color=INK))
    p.append(arrow(890, 378, 890, 477, color=POS, sw=2))

    render(os.path.join(OUT, "lru-rotation-loop.svg"), W, H, *p,
           title="Структура списків LRU та ротація сторінок в ядрі Linux")


# ── 3. Дерево рішень аллокатора сторінок ──────────────────────────────
def fig_reclaim_decision_tree():
    W, H = 1240, 720
    p = []

    p.append(text(60, 40, "Шлях виділення пам'яті (Page Allocation Path) та ескалація reclaim",
                  size=16, color=INK, anchor="start", bold=True))

    # Вхідна точка
    p.append(fitbox(620, 90, 360, 54, "Запит на виділення сторінки\nalloc_pages(gfp_mask)", size=13, fill=SOFT, stroke=LINE, sw=1.8, color=INK, bold=True))

    # Крок 1: Fast path (PCP)
    p.append(arrow(620, 120, 620, 175, color=LINE, sw=1.8))
    p.append(fitbox(620, 200, 440, 54, "Перевірка Per-CPU Page Sets (PCP)\nЧи є готова сторінка в локальному кеші CPU?", size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    p.append(arrow(843, 200, 995, 200, color=FIELD, sw=1.8))
    p.append(fitbox(1090, 200, 160, 50, "УСПІХ\nFast Path (O(1))", size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # Крок 2: Перевірка Watermark LOW
    p.append(arrow(620, 230, 620, 285, color=LINE, sw=1.8))
    p.append(fitbox(620, 310, 440, 54, "Перевірка Watermarks зони\nЧи Вільна Пам'ять > WMARK_LOW?", size=12, fill=PALE, stroke=MUTED, sw=1.5, color=INK))

    # Відгалуження: якщо < WMARK_LOW -> пробудження kswapd
    p.append(arrow(400, 310, 260, 310, color=NEG, sw=1.8))
    p.append(fitbox(150, 310, 200, 54, "wakeup_kswapd()\nАсинхронний reclaim", size=12, fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))

    # Крок 3: Перевірка Watermark MIN
    p.append(arrow(620, 340, 620, 395, color=LINE, sw=1.8))
    p.append(fitbox(620, 420, 440, 54, "Чи Вільна Пам'ять > WMARK_MIN\n(або є резерв GFP_ATOMIC)?", size=12, fill=PALE, stroke=MUTED, sw=1.5, color=INK))

    p.append(arrow(843, 420, 995, 420, color=FIELD, sw=1.8))
    p.append(fitbox(1090, 420, 160, 50, "Виділення з Buddy\nSlow path без stall", size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # Крок 4: Direct Reclaim
    p.append(arrow(620, 450, 620, 505, color=POS, sw=2))
    p.append(fitbox(620, 530, 480, 54, "Direct Reclaim (try_to_free_pages)\nПотік блокується (stall) та сам витісняє сторінки!", size=12, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(arrow(863, 530, 995, 530, color=FIELD, sw=1.8))
    p.append(fitbox(1090, 530, 160, 50, "Успіх reclaim\nПовернення до виконання", size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    # Крок 5: OOM Killer
    p.append(arrow(620, 560, 620, 615, color=POS, sw=2.2))
    p.append(fitbox(620, 645, 480, 54, "out_of_memory() — OOM Killer\nВибір та знищення процесу (SIGKILL) для звільнення RAM", size=12, fill=WARM, stroke=POS, sw=2.2, color=POS, bold=True))

    render(os.path.join(OUT, "reclaim-decision-tree.svg"), W, H, *p,
           title="Дерево рішень аллокатора сторінок та ескалація reclaim")


if __name__ == "__main__":
    fig_watermark_levels()
    fig_lru_rotation_loop()
    fig_reclaim_decision_tree()
