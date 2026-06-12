# -*- coding: utf-8 -*-
"""
Фігури для вставки r09-s2-a-memcpy-vs-dma.md
Рис. 4.9.2a.1 — модель порога доцільності: час копії vs розмір блоку (CPU vs DMA)
Рис. 4.9.2a.2 — дві стрічки часу: CPU-memcpy vs DMA (busy-wait / паралельна робота)

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.2a.1 — модель порога: дві прямі час(розмір)
# ══════════════════════════════════════════════════════════════════════════════
def fig1_threshold():
    W, H = 720, 420
    frags = []

    # ── Відступи та геометрія ─────────────────────────────────────────────────
    ox, oy = 80, 350    # початок координат (лівий нижній кут осей)
    aw, ah = 580, 290   # ширина і висота зони графіка

    # ── Осі ──────────────────────────────────────────────────────────────────
    frags.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))          # вісь X
    frags.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))           # вісь Y
    frags.append(text(ox + aw + 10, oy + 4, "Розмір блоку N (байти)", size=12, color=INK, anchor="start"))
    frags.append(text(ox - 8, oy - ah - 10, "Час\n(такти)", size=12, color=INK, anchor="end"))

    # ── Параметри прямих ────────────────────────────────────────────────────
    # CPU: час = 0 + N * slope_cpu  (майже нульовий оверхед)
    # DMA: час = overhead_dma + N * slope_dma  (той самий нахил — та сама пам'ять)
    # Для візуалізації: slope_cpu = slope_dma = однаковий (паралельні прямі)
    # Використовуємо "демонстраційні" числа у піксельному просторі

    n_max = aw          # піксельна ширина ~ "max N"
    slope = 0.40        # такти/байт (однаковий для обох)
    overhead_dma = 80   # пікселів — "фіксований оверхед DMA" (≈2000 тактів демо)

    # Точки прямих у піксельному просторі відносно початку осей
    # CPU: y(n) = n * slope  → у SVG: oy - n * slope
    # DMA: y(n) = overhead_dma + n * slope  → oy - overhead_dma - n * slope
    cpu_x1, cpu_y1 = ox,           oy
    cpu_x2, cpu_y2 = ox + n_max,   oy - n_max * slope

    dma_x1, dma_y1 = ox,           oy - overhead_dma
    dma_x2, dma_y2 = ox + n_max,   oy - overhead_dma - n_max * slope

    # ── Заштрихована зона між прямими (вивільнені такти ядра) ────────────────
    # Полігон: від dma_x1,dma_y1 → dma_x2,dma_y2 → cpu_x2,cpu_y2 → cpu_x1,cpu_y1
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        dma_x1, dma_y1, dma_x2, dma_y2, cpu_x2, cpu_y2, cpu_x1, cpu_y1)
    frags.append('<polygon points="%s" fill="#eef6ef" fill-opacity="0.75" stroke="none"/>' % pts)

    # ── Штрихування всередині зони (діагональний патерн — просто кілька ліній) ─
    for k in range(1, 10):
        frac = k / 10.0
        # Точка на DMA-прямій
        px_d = dma_x1 + frac * (dma_x2 - dma_x1)
        py_d = dma_y1 + frac * (dma_y2 - dma_y1)
        # Відповідна точка на CPU-прямій
        px_c = cpu_x1 + frac * (cpu_x2 - cpu_x1)
        py_c = cpu_y1 + frac * (cpu_y2 - cpu_y1)
        frags.append(line(px_d, py_d, px_c, py_c, color=FIELD, sw=1.0))

    # ── Прямі ────────────────────────────────────────────────────────────────
    frags.append(line(cpu_x1, cpu_y1, cpu_x2, cpu_y2, color=NEG, sw=2.5))
    frags.append(line(dma_x1, dma_y1, dma_x2, dma_y2, color=POS, sw=2.5))

    # ── Мітка оверхеду DMA на осі Y ─────────────────────────────────────────
    frags.append(line(ox - 8, oy - overhead_dma, ox + 8, oy - overhead_dma, color=POS, sw=1.5))
    frags.append(text(ox - 12, oy - overhead_dma + 4, "O_dma", size=11, color=POS, anchor="end", bold=True))

    # ── Підписи прямих ───────────────────────────────────────────────────────
    # CPU — кінець прямої
    label_cpu_x = cpu_x2 + 6
    label_cpu_y = cpu_y2 + 4
    tb, w, h = textbox(label_cpu_x + 50, label_cpu_y, "CPU memcpy\n(оверхед ≈ 0)", size=11,
                       fill="#eaf0fd", stroke=NEG, bold=False)
    frags.append(tb)
    frags.append(line(label_cpu_x, label_cpu_y, label_cpu_x + 50 - w / 2, label_cpu_y, color=NEG, sw=1.0, dash="4,3"))

    # DMA — кінець прямої
    label_dma_x = dma_x2 + 6
    label_dma_y = dma_y2 + 4
    tb2, w2, h2 = textbox(label_dma_x + 55, label_dma_y, "DMA (M2M)\n(старт коштує O_dma)", size=11,
                          fill="#fdecea", stroke=POS, bold=False)
    frags.append(tb2)
    frags.append(line(label_dma_x, label_dma_y, label_dma_x + 55 - w2 / 2, label_dma_y, color=POS, sw=1.0, dash="4,3"))

    # ── Підпис заштрихованої зони ────────────────────────────────────────────
    zone_cx = (dma_x1 + dma_x2) / 2
    zone_cy = (dma_y1 + dma_y2 + cpu_y1 + cpu_y2) / 4 - 10
    tb3, _, _ = textbox(zone_cx, zone_cy, "Вивільнені такти ядра\n(= виграш DMA)", size=12,
                        fill="#eef6ef", stroke=FIELD, bold=True)
    frags.append(tb3)

    # ── Пояснення: DMA паралельні прямі ──────────────────────────────────────
    # Зазначаємо, що нахили рівні — обидві прямі паралельні
    mid_x = ox + n_max * 0.45
    frags.append(text(mid_x, oy + 28, "Нахили рівні: та сама шина / пам'ять → однакова пропускна", size=10,
                      color=MUTED, anchor="middle", italic=True))

    # ── Легенда ───────────────────────────────────────────────────────────────
    legend_x, legend_y = ox + 20, oy - ah + 20
    frags.append(line(legend_x, legend_y + 10, legend_x + 30, legend_y + 10, color=NEG, sw=2.5))
    frags.append(text(legend_x + 36, legend_y + 14, "CPU memcpy", size=11, color=NEG, anchor="start"))
    frags.append(line(legend_x, legend_y + 28, legend_x + 30, legend_y + 28, color=POS, sw=2.5))
    frags.append(text(legend_x + 36, legend_y + 32, "DMA (M2M)", size=11, color=POS, anchor="start"))
    frags.append('<rect x="%d" y="%d" width="30" height="10" fill="#eef6ef" fill-opacity="0.85" '
                 'stroke="%s" stroke-width="1.0"/>' % (legend_x, legend_y + 42, FIELD))
    frags.append(text(legend_x + 36, legend_y + 51, "Вивільнені такти ядра", size=11, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "fig-r09-2a-1-threshold.svg"), W, H, *frags,
           title="Рис. 4.9.2a.1. Час копії проти розміру блоку: CPU vs DMA (M2M)")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.2a.2 — дві стрічки часу: CPU-memcpy vs DMA
# ══════════════════════════════════════════════════════════════════════════════
def fig2_timeline():
    W, H = 720, 380
    frags = []

    # ── Геометрія ─────────────────────────────────────────────────────────────
    # Два ряди: CPU-memcpy (зверху) і DMA (знизу, два варіанти)
    row_cpu   = 110   # центр смуги CPU
    row_dma   = 250   # центр DMA-смуги (верхній, ядро)
    row_dma2  = 310   # другий підрядок DMA (смуга "DMA апаратура")
    bar_h = 36        # висота смуги

    # Часова шкала (піксельна)
    t0 = 60           # початок часу
    t_copy_end = 500  # кінець копії (однаковий для CPU і DMA по "заповненню")
    t_dma_start_end = 120  # кінець старту DMA (оверхед налаштування)
    t_callback = t_copy_end + 30  # мітка колбеку готовності

    # ── РЯДОК 1: CPU-memcpy ───────────────────────────────────────────────────
    frags.append(text(t0 - 10, row_cpu - bar_h // 2 - 10, "CPU memcpy:", size=12, bold=True, color=INK, anchor="end"))

    # Суцільна смуга "ядро копіює"
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (t0, row_cpu - bar_h // 2, t_copy_end - t0, bar_h, "#eaf0fd", NEG))
    frags.append(text((t0 + t_copy_end) // 2, row_cpu + 5, "ядро копіює (займає CPU)", size=11,
                      color=NEG, anchor="middle", bold=True))

    # Вісь часу під CPU
    frags.append(arrow(t0, row_cpu + bar_h // 2 + 12, t_callback + 30, row_cpu + bar_h // 2 + 12, color=MUTED))
    frags.append(text(t_callback + 40, row_cpu + bar_h // 2 + 16, "t", size=11, color=MUTED, anchor="start", italic=True))

    # ── РЯДОК 2: DMA ─────────────────────────────────────────────────────────
    frags.append(text(t0 - 10, row_dma - bar_h // 2 - 24, "DMA:", size=12, bold=True, color=POS, anchor="end"))

    # Підписи рядків DMA
    frags.append(text(t0 - 10, row_dma + 5, "ядро:", size=11, color=INK, anchor="end", italic=True))
    frags.append(text(t0 - 10, row_dma2 + 5, "DMA hw:", size=11, color=POS, anchor="end", italic=True))

    # Смуга: старт DMA (налаштування) — ядро
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (t0, row_dma - bar_h // 2, t_dma_start_end - t0, bar_h, "#fdecea", POS))
    frags.append(text((t0 + t_dma_start_end) // 2, row_dma + 5, "старт\n(O_dma)", size=10,
                      color=POS, anchor="middle"))

    # Смуга ядра: ВАРІАНТ А — busy-wait (змарновано)
    bw_start = t_dma_start_end
    bw_end   = t_copy_end
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.5" stroke-dasharray="6,3"/>'
                 % (bw_start, row_dma - bar_h // 2, bw_end - bw_start, bar_h, "#fff6e0", "#c0a020"))
    frags.append(text((bw_start + bw_end) // 2, row_dma - 5, "busy-wait", size=10, color="#b07800", anchor="middle"))
    frags.append(text((bw_start + bw_end) // 2, row_dma + 10, "(змарновано)", size=10, color="#b07800", anchor="middle"))

    # Смуга ядра: ВАРІАНТ Б — корисна паралельна робота
    par_y = row_dma + bar_h // 2 + 8
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (bw_start, par_y, bw_end - bw_start, 28, "#eef6ef", FIELD))
    frags.append(text((bw_start + bw_end) // 2, par_y + 16, "або: ядро робить корисне (вивільнено!)", size=10,
                      color=FIELD, anchor="middle", bold=True))

    # Смуга DMA апаратури (копіює у фоні)
    dma_hw_start = t_dma_start_end
    dma_hw_end   = t_copy_end
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (dma_hw_start, row_dma2 - 14, dma_hw_end - dma_hw_start, 28, "#fdecea", POS))
    frags.append(text((dma_hw_start + dma_hw_end) // 2, row_dma2 + 2, "DMA апаратура копіює у фоні", size=10,
                      color=POS, anchor="middle"))

    # ── Мітка готовності: колбек/переривання ─────────────────────────────────
    cb_x = t_callback
    # Вертикальна лінія-мітка
    frags.append(line(cb_x, row_dma - bar_h // 2 - 10, cb_x, row_dma2 + 22, color=FIELD, sw=2.0, dash="5,3"))
    # Стрілка зверху
    frags.append(arrow(cb_x, row_dma2 + 22, cb_x, row_dma2 + 48, color=FIELD, sw=2.0))
    tb, _, _ = textbox(cb_x + 70, row_dma2 + 56, "колбек готовності\n(§4.5.6 ISR / volatile)", size=10,
                       fill="#eef6ef", stroke=FIELD)
    frags.append(tb)

    # ── Вісь часу під DMA ────────────────────────────────────────────────────
    axis_y = row_dma2 + 50
    frags.append(arrow(t0, axis_y, t_callback + 30, axis_y, color=MUTED))
    frags.append(text(t_callback + 40, axis_y + 4, "t", size=11, color=MUTED, anchor="start", italic=True))

    # ── Підписи оверхеду ─────────────────────────────────────────────────────
    frags.append(line(t0, row_dma - bar_h // 2 - 18, t_dma_start_end, row_dma - bar_h // 2 - 18,
                      color=POS, sw=1.2))
    frags.append(line(t0, row_dma - bar_h // 2 - 22, t0, row_dma - bar_h // 2 - 14, color=POS, sw=1.2))
    frags.append(line(t_dma_start_end, row_dma - bar_h // 2 - 22, t_dma_start_end, row_dma - bar_h // 2 - 14,
                      color=POS, sw=1.2))
    frags.append(text((t0 + t_dma_start_end) // 2, row_dma - bar_h // 2 - 24, "O_dma", size=9,
                      color=POS, anchor="middle"))

    # ── Підрядок-вивід ────────────────────────────────────────────────────────
    frags.append(text(W // 2, H - 18,
                      "Busy-wait → ядро не вивільнене. Корисна робота паралельно → ось де вигода DMA.",
                      size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, "fig-r09-2a-2-timeline.svg"), W, H, *frags,
           title="Рис. 4.9.2a.2. Часові стрічки: CPU memcpy vs DMA (busy-wait / паралельно)")


if __name__ == "__main__":
    fig1_threshold()
    print("OK: fig-r09-2a-1-threshold.svg")
    fig2_timeline()
    print("OK: fig-r09-2a-2-timeline.svg")
