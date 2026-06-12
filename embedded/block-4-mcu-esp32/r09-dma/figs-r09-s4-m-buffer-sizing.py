# -*- coding: utf-8 -*-
"""
Фігури для вставки 🧮 r09-s4-m-buffer-sizing (Розмір ping-pong буфера).
Дві фігури:
  fig-r09-4m-1-pingpong-timeline.svg  — часова шкала ping-pong
  fig-r09-4m-2-tradeoff.svg           — компроміс N: overrun ↔ RAM/затримка

Запуск: python figs-r09-s4-m-buffer-sizing.py
Вивід → ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Рис. 4.9.4m.1 — Часова шкала ping-pong ────────────────────────────────────
def fig1_timeline():
    W, H = 860, 400

    parts = []

    # ── Заголовок ──
    parts.append(text(W / 2, 28, "Подвійна буферизація: часова шкала DMA + ядро", size=16, bold=True))
    parts.append(text(W / 2, 50,
        "поки DMA пише B → ядро читає A; умова t_half ≥ t_proc, інакше overrun",
        size=11, color=MUTED))

    # ── Параметри ──
    X0 = 80       # початок шкали
    X1 = 800      # кінець шкали
    DMA_Y  = 100  # вісь DMA
    CORE_Y = 200  # вісь ядра
    BAR_H  = 44   # висота смуги
    HALF_W = 180  # ширина однієї половини (px)

    DMA_COL  = "#2457d6"   # синій DMA
    CORE_COL = "#27ae60"   # зелений ядро
    OVR_COL  = "#c0392b"   # червоний overrun

    # ── Мітки осей ──
    parts.append(text(X0 - 10, DMA_Y  + BAR_H / 2 + 5, "DMA",  size=13, color=DMA_COL,  anchor="end", bold=True))
    parts.append(text(X0 - 10, CORE_Y + BAR_H / 2 + 5, "Ядро", size=13, color=CORE_COL, anchor="end", bold=True))

    # ── DMA-смуги: A → B → A → B ──
    labels_dma = ["Пише A", "Пише B", "Пише A", "Пише B"]
    fills_dma  = ["#dbeafe", "#bfdbfe", "#dbeafe", "#bfdbfe"]
    strokes_dma = [DMA_COL, DMA_COL, DMA_COL, DMA_COL]

    for i, (lbl, fill) in enumerate(zip(labels_dma, fills_dma)):
        x = X0 + i * HALF_W
        if x + HALF_W > X1:
            break
        parts.append(rect(x, DMA_Y, HALF_W - 3, BAR_H, fill=fill, stroke=DMA_COL, sw=1.8, rx=6))
        parts.append(text(x + HALF_W / 2, DMA_Y + BAR_H / 2 + 5, lbl, size=12, color=DMA_COL, bold=True))

    # ── Ядро-смуги: (пауза), обробляє A, обробляє B, обробляє A ──
    # Ядро починає після першого повного заповнення A (зсув = HALF_W)
    proc_w = int(HALF_W * 0.75)  # t_proc < t_half (правильний випадок)
    core_start = X0 + HALF_W   # ядро хапає A щойно DMA переключилося на B
    labels_core = ["Обробляє A", "Обробляє B", "Обробляє A"]

    for i, lbl in enumerate(labels_core):
        x = core_start + i * HALF_W
        if x + proc_w > X1 + 20:
            break
        parts.append(rect(x, CORE_Y, proc_w - 3, BAR_H, fill="#d1fae5", stroke=CORE_COL, sw=1.8, rx=6))
        parts.append(text(x + proc_w / 2, CORE_Y + BAR_H / 2 + 5, lbl, size=12, color=CORE_COL, bold=True))

    # ── Вертикальні пунктирні межі переключення DMA ──
    for i in range(1, 4):
        xv = X0 + i * HALF_W
        if xv > X1:
            break
        parts.append(line(xv, DMA_Y - 14, xv, CORE_Y + BAR_H + 30, color="#aaaaaa", sw=1.2, dash="5,4"))

    # ── Двосторонні стрілки: t_half і t_proc (для першого циклу) ──
    arrow_y_half = DMA_Y - 18
    arrow_y_proc = CORE_Y + BAR_H + 22

    # t_half (перша половина DMA: X0 → X0+HALF_W)
    parts.append(line(X0, arrow_y_half, X0 + HALF_W, arrow_y_half, color=DMA_COL, sw=1.6))
    parts.append(line(X0, arrow_y_half - 6, X0, arrow_y_half + 6, color=DMA_COL, sw=1.6))
    parts.append(line(X0 + HALF_W, arrow_y_half - 6, X0 + HALF_W, arrow_y_half + 6, color=DMA_COL, sw=1.6))
    parts.append(text(X0 + HALF_W / 2, arrow_y_half - 6,
                      "t_half = N / Rₛ", size=11, color=DMA_COL, bold=True))

    # t_proc (перший блок ядра: core_start → core_start+proc_w)
    parts.append(line(core_start, arrow_y_proc, core_start + proc_w, arrow_y_proc, color=CORE_COL, sw=1.6))
    parts.append(line(core_start, arrow_y_proc - 6, core_start, arrow_y_proc + 6, color=CORE_COL, sw=1.6))
    parts.append(line(core_start + proc_w, arrow_y_proc - 6, core_start + proc_w, arrow_y_proc + 6, color=CORE_COL, sw=1.6))
    parts.append(text(core_start + proc_w / 2, arrow_y_proc + 16,
                      "t_proc", size=11, color=CORE_COL, bold=True))

    # ── Умова-рамка ──
    cond_tb, cw, ch = textbox(W / 2, 330,
        "Умова без втрат:  t_half ≥ t_proc  →  N ≥ Rₛ · t_proc",
        size=13, pad=12, fill="#f0fff4", stroke=CORE_COL, sw=2, bold=True, min_w=480)
    parts.append(cond_tb)

    # ── Підпис overrun (попередження) ──
    ovr_tb, ow, oh = textbox(X0 + HALF_W * 2 + HALF_W * 0.65, CORE_Y + BAR_H / 2 + 5,
        "Якщо t_proc > t_half\n→ overrun!", size=11, pad=8,
        fill="#fef2f2", stroke=OVR_COL, sw=1.8, color=OVR_COL, min_w=150)
    # тільки якщо вліз
    if X0 + HALF_W * 2 + HALF_W * 0.65 + ow / 2 < X1 + 10:
        parts.append(ovr_tb)

    render(os.path.join(OUT, "fig-r09-4m-1-pingpong-timeline.svg"), W, H, *parts)
    print("wrote fig-r09-4m-1-pingpong-timeline.svg")


# ── Рис. 4.9.4m.2 — Компроміс: latency ↔ RAM ─────────────────────────────────
def fig2_tradeoff():
    W, H = 800, 420

    parts = []

    # ── Заголовок ──
    parts.append(text(W / 2, 28, "Вибір N: дві стіни — overrun і RAM/затримка", size=16, bold=True))
    parts.append(text(W / 2, 50,
        "ліворуч — замало (втрати даних), праворуч — забагато (марна SRAM + лаг)",
        size=11, color=MUTED))

    # ── Параметри вісей ──
    X0, X1 = 100, 720   # горизонталь (вісь N)
    Y0, Y1 = 320, 80    # вертикаль (ось «небезпека» — 0 внизу)
    CHART_H = Y0 - Y1

    # Значення N на лог-шкалі для меток: 64, 128, 256, 512, 1024, 2048, 4096
    import math
    n_vals = [64, 128, 200, 256, 400, 512, 1024, 2048, 4096]
    n_min, n_max = 64, 4096

    def nx(n):
        """Перетворення N → x (логарифмічна шкала)."""
        return X0 + (math.log2(n) - math.log2(n_min)) / (math.log2(n_max) - math.log2(n_min)) * (X1 - X0)

    # ── Осі ──
    parts.append(arrow(X0 - 10, Y0, X1 + 20, Y0, color=LINE, sw=2))  # горизонталь
    parts.append(text(X1 + 30, Y0 + 5, "N", size=14, color=LINE, bold=True, anchor="start"))

    # Мітки N на осі
    for n in [64, 128, 256, 512, 1024, 2048, 4096]:
        xn = nx(n)
        parts.append(line(xn, Y0 - 5, xn, Y0 + 5, color=LINE, sw=1.2))
        parts.append(text(xn, Y0 + 20, str(n), size=10, color=MUTED))

    # ── Зона overrun (червона, ліво) ──
    # Мінімум N (Rₛ·t_proc) позначимо умовно: N=200 відліків
    n_min_safe = 200
    n_work = 512      # робоча точка з прикладу
    x_safe = nx(n_min_safe)
    x_work = nx(n_work)
    x_margin = nx(400)   # з запасом k=2

    # Червона зона
    ovr_fill = "#fef2f2"
    ovr_stroke = "#c0392b"
    parts.append(rect(X0, Y1, x_safe - X0, CHART_H, fill=ovr_fill, stroke="none", sw=0, rx=0))
    # Вертикальна межа overrun
    parts.append(line(x_safe, Y1 - 10, x_safe, Y0 + 5, color="#c0392b", sw=2, dash="6,3"))

    ovr_tb, ow, oh = textbox(X0 + (x_safe - X0) / 2, Y0 - CHART_H * 0.55,
        "OVERRUN\n(N < Rₛ·t_proc)\nDMA дожене\nядро → втрата",
        size=11, pad=9, fill="#fef2f2", stroke="#c0392b", sw=1.8, color="#c0392b", min_w=110)
    parts.append(ovr_tb)

    # ── Зелена зона (робоча) ──
    green_fill = "#f0fff4"
    parts.append(rect(x_safe, Y1, nx(2048) - x_safe, CHART_H, fill=green_fill, stroke="none", sw=0, rx=0))

    # Межа запасу (k=2, N=400→512)
    parts.append(line(x_margin, Y1 - 10, x_margin, Y0 + 5, color="#27ae60", sw=1.5, dash="4,4"))
    parts.append(text(x_margin, Y1 - 18, "Rₛ·t_proc·k", size=10, color="#27ae60", bold=True))

    # ── Синя зона праворуч: RAM і лаг ──
    ram_x = nx(2048)
    blue_fill = "#eff6ff"
    parts.append(rect(ram_x, Y1, X1 - ram_x, CHART_H, fill=blue_fill, stroke="none", sw=0, rx=0))
    ram_tb, rw, rh = textbox(ram_x + (X1 - ram_x) / 2, Y0 - CHART_H * 0.55,
        "Надмір RAM\n+ зростання\nзатримки",
        size=11, pad=9, fill="#eff6ff", stroke="#2457d6", sw=1.8, color="#2457d6", min_w=110)
    parts.append(ram_tb)

    # ── Лінія "B_total = 2N·bytes" — зростає вправо (схематична) ──
    # малюємо її як нахилену пряму у верхній частині
    import math as m
    pts_ram = []
    for n in range(128, 4097, 64):
        xn = nx(n)
        # B_total = 2*n*2 байт (для прикладу АЦП, 2 байти/відлік)
        # нормуємо до [Y1+20, Y0-20]
        b_max = 2 * 4096 * 2
        b = 2 * n * 2
        yn = Y0 - 20 - (b / b_max) * (CHART_H - 50)
        pts_ram.append((xn, yn))

    # Полілінія синя (RAM)
    pstr = " ".join("%.1f,%.1f" % (px, py) for px, py in pts_ram)
    parts.append('<polyline points="%s" stroke="%s" stroke-width="2" fill="none" '
                 'stroke-dasharray="5,3" opacity="0.7"/>' % (pstr, "#2457d6"))
    parts.append(text(nx(3000), pts_ram[-30][1] - 14, "B_total=2N·байт", size=10, color="#2457d6", bold=False))

    # ── Три приклади-точки ──
    for n, lbl, col, dy in [(200, "200\n(впритул,\noverrun)", "#c0392b", -35),
                             (512, "512\n(робоча)", "#27ae60",  -35),
                             (4096, "4096\n(надмір)", "#2457d6", -35)]:
        xn = nx(n)
        parts.append(circle(xn, Y0, 8, fill=col, stroke=col, sw=2))
        parts.append(text(xn, Y0 + dy, lbl, size=10, color=col, bold=True))

    # ── Підсумкова рамка ──
    summ_tb, sw_, sh_ = textbox(W / 2, 390,
        "Робоча зона: N = Rₛ·t_proc·k, округлити вгору до степеня 2",
        size=12, pad=10, fill="#f0fff4", stroke="#27ae60", sw=1.8, bold=True, min_w=520)
    parts.append(summ_tb)

    # Рамки-межі видимості (ліво/право)
    parts.append(line(X0, Y1, X0, Y0, color="#cccccc", sw=1))
    parts.append(line(X1, Y1, X1, Y0, color="#cccccc", sw=1))

    render(os.path.join(OUT, "fig-r09-4m-2-tradeoff.svg"), W, H, *parts)
    print("wrote fig-r09-4m-2-tradeoff.svg")


if __name__ == "__main__":
    fig1_timeline()
    fig2_tradeoff()
    print("Done.")
