# -*- coding: utf-8 -*-
"""Фігури до теми «Апаратний кодек H.264 (H.264 Hardware Codec)».
Запуск: python figs.py -> генерує SVG у ./img/
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Конвеєр апаратного кодека H.264 ──────────────────────────────────────
def fig_h264_hardware_pipeline():
    W, H = 820, 360
    f = [text(W / 2, 25, "Конвеєр апаратного кодека H.264 (Macroblock Pipeline)", size=16, bold=True)]

    # Зовнішня пам'ять / DMA
    f.append(fitbox(20, 60, 110, 260, "Оперативна\nпам'ять (RAM)\n\n• YUV Кадри\n• NAL Потік\n• DPB Буфер", size=12, fill="#eef2ff", stroke="#3b82f6"))
    
    # DMA стрілки
    f.append(arrow(130, 100, 180, 100, color="#3b82f6", sw=2))
    f.append(text(155, 90, "YUV", size=10, color="#3b82f6", bold=True))

    f.append(arrow(710, 280, 130, 280, color="#3b82f6", sw=2))
    f.append(text(420, 295, "NAL Бітстрім через DMA", size=11, color="#3b82f6", bold=True))

    # Конвеєр макроблока (прямий шлях)
    f.append(fitbox(180, 75, 110, 50, "Оцінка руху\n(ME / Intra)", size=12, fill="#f0fdf4", stroke="#16a34a"))
    f.append(arrow(290, 100, 320, 100, color=LINE, sw=1.8))

    f.append(fitbox(320, 75, 100, 50, "Віднімання\n(Залишок)", size=12, fill="#fefce8", stroke="#ca8a04"))
    f.append(arrow(420, 100, 450, 100, color=LINE, sw=1.8))

    f.append(fitbox(450, 75, 110, 50, "Цілочисельне\nDCT 4x4 + Q", size=12, fill="#fef2f2", stroke="#dc2626"))
    f.append(arrow(560, 100, 590, 100, color=LINE, sw=1.8))

    f.append(fitbox(590, 75, 120, 50, "Ентропійний\nкодер (CABAC)", size=12, fill="#faf5ff", stroke="#9333ea"))
    f.append(arrow(710, 100, 750, 100, color=LINE, sw=1.8))

    f.append(fitbox(750, 75, 55, 230, "FIFO\nБіт\nстріму", size=11, fill="#f3f4f6", stroke="#4b5563"))

    # Зворотний контур (Reconstruction Loop)
    f.append(arrow(505, 125, 505, 175, color=MUTED, sw=1.5))
    f.append(fitbox(450, 175, 110, 45, "Обернене Q\nта IQ-DCT 4x4", size=11, fill="#f8fafc", stroke="#64748b"))

    f.append(arrow(450, 197, 400, 197, color=MUTED, sw=1.5))
    f.append(fitbox(310, 175, 90, 45, "Додавання\nпрогнозу", size=11, fill="#f8fafc", stroke="#64748b"))

    f.append(arrow(310, 197, 270, 197, color=MUTED, sw=1.5))
    f.append(fitbox(170, 175, 100, 45, "Deblocking\nФільтр (DBF)", size=11, fill="#fff7ed", stroke="#ea580c"))

    # Зв'язок з DPB
    f.append(arrow(220, 220, 220, 260, color="#ea580c", sw=1.5))
    f.append(fitbox(170, 260, 110, 45, "Буфер опорних\nкадрів (DPB)", size=11, fill="#fff7ed", stroke="#ea580c"))

    f.append(arrow(225, 260, 225, 125, color="#16a34a", sw=1.5))
    f.append(text(250, 150, "Опорні\nпікселі", size=10, color="#16a34a", anchor="start"))

    render(os.path.join(IMG, 'h264-hardware-pipeline.svg'), W, H, *f)


# ── 2. Потік даних цілочисельного перетворення 4x4 ─────────────────────────
def fig_h264_integer_transform_flow():
    W, H = 760, 320
    f = [text(W / 2, 25, "Апаратне цілочисельне перетворення H.264 4x4 (Butterfly Pipeline)", size=16, bold=True)]

    # Вхідні відліки x[i]
    x_in = [50, 110, 170, 230]
    labels_in = ["x[0]", "x[1]", "x[2]", "x[3]"]
    for i in range(4):
        f.append(fitbox(40, x_in[i] - 15, 60, 30, labels_in[i], size=13, fill="#e0f2fe", stroke="#0284c7", bold=True))
        f.append(arrow(100, x_in[i], 160, x_in[i], color=LINE, sw=1.5))

    # Стадія 1: Перша комбінація (додавання / віднімання)
    f.append(rect(160, 35, 130, 220, fill="#f8fafc", stroke="#94a3b8", rx=6))
    f.append(text(225, 55, "Стадія 1: Суми", size=11, color=MUTED, bold=True))
    f.append(fitbox(175, 75, 100, 30, "a0 = x0 + x3", size=11, fill="#ffffff", stroke="#64748b"))
    f.append(fitbox(175, 120, 100, 30, "a1 = x1 + x2", size=11, fill="#ffffff", stroke="#64748b"))
    f.append(fitbox(175, 165, 100, 30, "a2 = x1 - x2", size=11, fill="#ffffff", stroke="#64748b"))
    f.append(fitbox(175, 210, 100, 30, "a3 = x0 - x3", size=11, fill="#ffffff", stroke="#64748b"))

    for i in range(4):
        f.append(arrow(275, x_in[i], 340, x_in[i], color=LINE, sw=1.5))

    # Стадія 2: Масштабування на 2 (зсув вліво << 1)
    f.append(rect(340, 35, 150, 220, fill="#fefce8", stroke="#ca8a04", rx=6))
    f.append(text(415, 55, "Стадія 2: Зсув бітів", size=11, color="#854d0e", bold=True))
    f.append(fitbox(355, 75, 120, 30, "y0 = a0 + a1", size=11, fill="#ffffff", stroke="#ca8a04"))
    f.append(fitbox(355, 120, 120, 30, "y1 = (a3<<1) + a2", size=11, fill="#ffffff", stroke="#ca8a04"))
    f.append(fitbox(355, 165, 120, 30, "y2 = a0 - a1", size=11, fill="#ffffff", stroke="#ca8a04"))
    f.append(fitbox(355, 210, 120, 30, "y3 = a2 - (a3<<1)", size=11, fill="#ffffff", stroke="#ca8a04"))

    for i in range(4):
        f.append(arrow(475, x_in[i], 540, x_in[i], color=LINE, sw=1.5))

    # Вихідні коефіцієнти y[i]
    labels_out = ["y[0] (DC)", "y[1] (AC1)", "y[2] (AC2)", "y[3] (AC3)"]
    for i in range(4):
        f.append(fitbox(540, x_in[i] - 15, 90, 30, labels_out[i], size=12, fill="#f0fdf4", stroke="#16a34a", bold=True))

    # Пояснення знизу
    f.append(rect(40, 270, 680, 35, fill="#fef2f2", stroke="#dc2626", rx=4))
    f.append(text(380, 292, "Жодного множника! Операції обмежені додавачами та бітовим зсувом (shift-and-add).", size=12, color="#991b1b", bold=True))

    render(os.path.join(IMG, 'h264-integer-transform-flow.svg'), W, H, *f)


# ── 3. Апаратний рушій CABAC ────────────────────────────────────────────────
def fig_cabac_hardware_engine():
    W, H = 800, 300
    f = [text(W / 2, 25, "Структура апаратного рушія CABAC (Binary Arithmetic Coder)", size=16, bold=True)]

    # Вхідні елементи
    f.append(fitbox(20, 80, 110, 50, "Синтаксичні\nелементи\n(MVD, Coeff)", size=11, fill="#f3f4f6", stroke="#4b5563"))
    f.append(arrow(130, 105, 170, 105, color=LINE, sw=1.8))

    # Бінаризатор
    f.append(fitbox(170, 80, 100, 50, "Бінаризатор\n(Unary / FL)", size=12, fill="#eff6ff", stroke="#2563eb"))
    f.append(arrow(270, 105, 310, 105, color=LINE, sw=1.8))
    f.append(text(290, 95, "Bins", size=10, color="#2563eb", bold=True))

    # Селектор контексту
    f.append(fitbox(310, 80, 120, 50, "Вибір моделі\nконтексту\n(ctxIdx)", size=11, fill="#fefce8", stroke="#ca8a04"))
    f.append(arrow(430, 105, 470, 105, color=LINE, sw=1.8))

    # Арифметичний кодер (BAC Engine)
    f.append(rect(470, 60, 170, 190, fill="#faf5ff", stroke="#9333ea", sw=2, rx=8))
    f.append(text(555, 80, "Арифметичний кодер", size=12, color="#7e22ce", bold=True))
    f.append(fitbox(485, 95, 140, 30, "Регістр Range (9 біт)", size=11, fill="#ffffff", stroke="#9333ea"))
    f.append(fitbox(485, 135, 140, 30, "Регістр Low (10 біт)", size=11, fill="#ffffff", stroke="#9333ea"))
    f.append(fitbox(485, 175, 140, 35, "Нормалізація та\nвивід бітів", size=11, fill="#f3e8ff", stroke="#7e22ce"))

    f.append(arrow(640, 192, 690, 192, color=LINE, sw=1.8))
    f.append(fitbox(690, 170, 90, 45, "Вихідний\nбітстрім", size=12, fill="#f0fdf4", stroke="#16a34a", bold=True))

    # Оновлення таблиці станів ймовірностей
    f.append(rect(310, 175, 120, 75, fill="#f0fdf4", stroke="#16a34a", rx=6))
    f.append(text(370, 195, "Таблиця станів", size=11, color="#15803d", bold=True))
    f.append(text(370, 215, "64 стани (pState)", size=10, color=MUTED))
    f.append(text(370, 230, "LPS / MPS transition", size=10, color=MUTED))

    # Двосторонні стрілки контекст <-> кодер
    f.append(arrow(430, 200, 470, 200, color="#16a34a", sw=1.5))
    f.append(arrow(470, 220, 430, 220, color="#16a34a", sw=1.5))

    render(os.path.join(IMG, 'cabac-hardware-engine.svg'), W, H, *f)


if __name__ == '__main__':
    fig_h264_hardware_pipeline()
    fig_h264_integer_transform_flow()
    fig_cabac_hardware_engine()
    print("Генерація SVG у ./img/ успішно завершена.")
