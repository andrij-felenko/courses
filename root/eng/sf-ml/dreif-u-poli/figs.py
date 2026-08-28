#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація діаграм для теми dreif-u-poli (Дрейф у полі: як помітити його на борту)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, circle, text, mtext, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_adwin_sliding_window():
    """Схема адаптивного вікна ADWIN з експоненційними бакетами та поділом на підвікна W0 і W1."""
    w, h = 880, 480
    frags = []

    # Заголовок схеми
    frags.append(text(440, 28, "Адаптивне вікно ADWIN: поділ ковзного буфера та перевірка за Гоффдінгом", size=15, bold=True))

    # Верхній блок: потік вхідних вимірювань x_t
    frags.append(rect(40, 55, 800, 75, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(150, 78, "Потік вимірювань у часі (t →)", size=13, color=MUTED, bold=True))
    frags.append(arrow(280, 74, 810, 74, color=LINE, sw=1.5))

    # Елементи потоку (точки/значення)
    samples = ["x₁", "x₂", "...", "x_{t-k}", "...", "x_{t-2}", "x_{t-1}", "x_t"]
    for i, s in enumerate(samples):
        cx = 100 + i * 90
        cy = 105
        frags.append(circle(cx, cy, 14, fill="#ffffff", stroke=LINE, sw=1.2))
        frags.append(text(cx, cy + 4, s, size=11, bold=True))

    # Загальне вікно W (поточна вибірка без зафіксованого дрейфу)
    frags.append(rect(40, 150, 800, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(440, 172, "Поточне адаптивне вікно спостережень W (розмір |W| = n₀ + n₁)", size=13, bold=True))

    # Підвікно W0 (старіші дані)
    frags.append(rect(60, 190, 360, 100, fill="#edf2f7", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(240, 215, "Підвікно W₀ (старіші спостереження)", size=13, color=NEG, bold=True))
    frags.append(text(240, 240, "Кількість зразків: n₀  |  Середнє значення: μ₀", size=12))
    frags.append(text(240, 265, "Гістограма бакетів розміру 2ʲ (пам'ять O(log W))", size=11, color=MUTED))

    # Розділювач / точка розрізу
    frags.append(line(440, 185, 440, 300, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(440, 320, "Точка розрізу (cut)", size=11, color=MUTED, bold=True))

    # Підвікно W1 (новіші дані)
    frags.append(rect(460, 190, 360, 100, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(640, 215, "Підвікно W₁ (найновіші спостереження)", size=13, color=POS, bold=True))
    frags.append(text(640, 240, "Кількість зразків: n₁  |  Середнє значення: μ₁", size=12))
    frags.append(text(640, 265, "Свіжі бакети малого розміру (актуальний стан)", size=11, color=MUTED))

    # Нижній блок: критерій розщеплення та скорочення вікна
    frags.append(rect(40, 345, 800, 115, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(440, 370, "Статистична умова виявлення дрейфу (Нерівність Гоффдінга):", size=13, bold=True))

    # Формула критерію
    frags.append(text(440, 400, "|μ₀ − μ₁|  ≥  ε_cut = √ [ (1 / (2·m)) · ln (4 / δ) ]", size=13, color=POS, bold=True))
    frags.append(text(440, 425, "де m = 1 / (1/n₀ + 1/n₁) — гармонійне середнє обсягів, δ — рівень хибної тривоги", size=11, color=MUTED))
    frags.append(text(440, 445, "Якщо умову виконано: старі бакети з W₀ видаляються, розмір вікна W зменшується до |W₁|", size=11, color=FIELD, bold=True))

    svg_path = os.path.join(OUT_DIR, "adwin-sliding-window.svg")
    render(svg_path, w, h, *frags)


def make_cusum_time_series():
    """Часова діаграма детекції стрибка середнього детектором CUSUM."""
    w, h = 880, 460
    frags = []

    # Заголовок
    frags.append(text(440, 28, "Детекція розладки за кумулятивними сумами (Двобічний CUSUM)", size=15, bold=True))

    # Верхній графік: Сигнал y(t) зі зміною середнього
    frags.append(rect(60, 50, 780, 170, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(170, 72, "Вхідний сигнал y(t) та номінальне середнє μ₀", size=12, bold=True))

    # Вісь часу та значення
    frags.append(line(90, 185, 820, 185, color=LINE, sw=1.2)) # вісь X
    frags.append(line(90, 65, 90, 185, color=LINE, sw=1.2))  # вісь Y
    frags.append(text(825, 189, "t", size=12, bold=True, anchor="start"))
    frags.append(text(85, 62, "y", size=12, bold=True, anchor="end"))

    # Базова лінія номінального середнього mu0
    frags.append(line(90, 140, 430, 140, color=FIELD, sw=1.5, dash="5,3"))
    frags.append(text(110, 134, "μ₀ (номінал)", size=11, color=FIELD, bold=True, anchor="start"))

    # Зміщене середнє mu1
    frags.append(line(430, 100, 810, 100, color=POS, sw=1.5, dash="5,3"))
    frags.append(text(440, 94, "μ₁ = μ₀ + Δ (дрейф)", size=11, color=POS, bold=True, anchor="start"))

    # Вертикальна лінія моменту стрибка
    frags.append(line(430, 50, 430, 420, color="#cbd5e1", sw=1.5, dash="4,4"))
    frags.append(text(430, 45, "Момент стрибка (t = t_drift)", size=11, color=MUTED, bold=True))

    # Звивиста лінія сигналу y(t)
    pts_pre = [
        (100, 142), (130, 135), (160, 145), (190, 138), (220, 143),
        (250, 133), (280, 144), (310, 139), (340, 142), (370, 136),
        (400, 144), (430, 138)
    ]
    pts_post = [
        (430, 138), (460, 105), (490, 95), (520, 108), (550, 92),
        (580, 102), (610, 96), (640, 104), (670, 94), (700, 98),
        (730, 95), (760, 102), (790, 96)
    ]
    
    # Малюємо полілінії сигналу
    for i in range(len(pts_pre) - 1):
        x1, y1 = pts_pre[i]
        x2, y2 = pts_pre[i+1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=1.8))
    for i in range(len(pts_post) - 1):
        x1, y1 = pts_post[i]
        x2, y2 = pts_post[i+1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=1.8))

    # Нижній графік: Кумулятивна сума S_h^+(t)
    frags.append(rect(60, 240, 780, 195, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(230, 262, "Кумулятивна сума S⁺(t) = max(0, S⁺(t−1) + y(t) − μ₀ − δ)", size=12, bold=True))

    # Вісь часу для CUSUM
    frags.append(line(90, 395, 820, 395, color=LINE, sw=1.2))
    frags.append(line(90, 255, 90, 395, color=LINE, sw=1.2))
    frags.append(text(825, 399, "t", size=12, bold=True, anchor="start"))
    frags.append(text(85, 252, "S⁺", size=12, bold=True, anchor="end"))

    # Поріг h
    frags.append(line(90, 305, 810, 305, color=POS, sw=1.5, dash="6,3"))
    frags.append(text(110, 299, "Поріг тривоги h", size=11, color=POS, bold=True, anchor="start"))

    # Рівень 0
    frags.append(text(100, 410, "Нульовий рівень S⁺ = 0", size=11, color=MUTED, anchor="start"))

    # Траєкторія S^+(t)
    cusum_pts = [
        (100, 395), (130, 395), (160, 395), (190, 395), (220, 395),
        (250, 395), (280, 395), (310, 395), (340, 395), (370, 395),
        (400, 395), (430, 395), (460, 380), (490, 360), (520, 345),
        (550, 325), (580, 305), (610, 280), (640, 255)
    ]
    for i in range(len(cusum_pts) - 1):
        x1, y1 = cusum_pts[i]
        x2, y2 = cusum_pts[i+1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.2))

    # Точка спрацювання тривоги (перетин порогу h при x=580, y=305)
    frags.append(circle(580, 305, 5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(line(580, 305, 580, 420, color=POS, sw=1.2, dash="3,3"))
    frags.append(text(580, 435, "Фіксація тривоги (t = t_alarm)", size=11, color=POS, bold=True))

    # Стрілка затримки детекції
    frags.append(arrow(430, 415, 580, 415, color=MUTED, sw=1.4))
    frags.append(text(505, 410, "Затримка детекції (ADD)", size=10, color=MUTED))

    svg_path = os.path.join(OUT_DIR, "cusum-time-series.svg")
    render(svg_path, w, h, *frags)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_adwin_sliding_window()
    make_cusum_time_series()
    print("Діаграми згенеровано успішно.")
