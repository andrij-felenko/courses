# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми measurement-uncertainty (hw-sensing)."""

import sys
import os
import math

# Підключаємо svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_accuracy_precision():
    """Фігура 1: 4 квадранти ISO 5725 — Правильність (Trueness) проти Прецизійності (Precision)."""
    w, h = 900, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Матриця метрологічних якостей: Правильність (Trueness) проти Прецизійності (Precision)", size=16, bold=True))

    # Створюємо 4 квадранти
    cards = [
        # (x, y, w_c, h_c, title, desc, trueness, precision)
        (30, 50, 400, 195, "Висока правильність + Висока прецизійність", "Висока точність (Accuracy). Зсув нульовий, розкид мінімальний.", True, True),
        (470, 50, 400, 195, "Низька правильність + Висока прецизійність", "Стабільне систематичне зміщення (Bias). Виправляється калібруванням.", False, True),
        (30, 265, 400, 195, "Висока правильність + Низька прецизійність", "Центр вибірки в яблучку, але сильний випадковий шум. Лікується усередненням.", True, False),
        (470, 265, 400, 195, "Низька правильність + Низька прецизійність", "Найгірший стан: велике зміщення і високий шум. Потребує апаратного аудиту.", False, False),
    ]

    for cx, cy, cw, ch, title, desc, is_true, is_prec in cards:
        # Фон картки
        frags.append(rect(cx, cy, cw, ch, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=8))
        frags.append(text(cx + 15, cy + 24, title, size=13, bold=True, anchor="start", color=INK))
        frags.append(text(cx + 15, cy + 42, desc, size=11, color=MUTED, anchor="start"))

        # Мішень усередині картки
        tx = cx + 80
        ty = cy + 120
        # Кільця мішені
        frags.append(circle(tx, ty, 55, fill="#f3f4f6", stroke="#d1d5db", sw=1))
        frags.append(circle(tx, ty, 38, fill="#e5e7eb", stroke="#cbd5e1", sw=1))
        frags.append(circle(tx, ty, 20, fill="#fee2e2", stroke="#fca5a5", sw=1))
        frags.append(circle(tx, ty, 4, fill=POS, stroke=POS, sw=1))

        # Осі мішені
        frags.append(line(tx - 60, ty, tx + 60, ty, color="#9ca3af", sw=1, dash="2,2"))
        frags.append(line(tx, ty - 60, tx, ty + 60, color="#9ca3af", sw=1, dash="2,2"))

        # Точки вимірювань
        target_center_x = tx
        target_center_y = ty
        bias_x = 0 if is_true else 26
        bias_y = 0 if is_true else -24
        spread = 6 if is_prec else 24

        # Генерація детермінованих точок
        angles = [0.2, 1.1, 2.3, 3.5, 4.2, 5.1, 5.8, 1.8, 2.9, 0.7]
        radii = [0.3, 0.7, 0.5, 0.9, 0.4, 0.8, 0.6, 0.2, 0.95, 0.45]
        for a, r_k in zip(angles, radii):
            px = target_center_x + bias_x + r_k * spread * math.cos(a)
            py = target_center_y + bias_y + r_k * spread * math.sin(a)
            frags.append(circle(px, py, 3, fill=NEG, stroke="#1e3a8a", sw=1))

        # Пояснювальні плашки збоку від мішені
        bx = cx + 160
        by = cy + 70
        bw = cw - 175
        bh = 110
        frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=6))

        trueness_txt = "Зміщення (Bias): ~0 (Істина)" if is_true else "Зміщення (Bias): +2.4 σ (Зсув)"
        trueness_col = FIELD if is_true else POS
        prec_txt = "Розкид (σ): Малий (Висока купність)" if is_prec else "Розкид (σ): Великий (Шум)"
        prec_col = FIELD if is_prec else POS

        frags.append(text(bx + 10, by + 24, "Метрологічний статус:", size=11, bold=True, anchor="start", color=INK))
        frags.append(text(bx + 10, by + 46, "• " + trueness_txt, size=11, color=trueness_col, anchor="start", bold=True))
        frags.append(text(bx + 10, by + 68, "• " + prec_txt, size=11, color=prec_col, anchor="start", bold=True))
        status_line = "✓ Точний вимір" if (is_true and is_prec) else ("⚠ Потребує калібрування" if is_prec else ("⚠ Потребує фільтрації" if is_true else "✖ Непридатний результат"))
        frags.append(text(bx + 10, by + 92, status_line, size=11, color=INK, anchor="start", italic=True))

    return render(os.path.join(IMG_DIR, "accuracy-precision-matrix.svg"), w, h, *frags)


def fig_resolution_vs_lod_noise():
    """Фігура 2: Роздільність проти Шуму, Межа виявлення (LOD) та Межа кількісного визначення (LOQ)."""
    w, h = 900, 460
    frags = []

    frags.append(text(w / 2, 26, "Роздільна здатність (Resolution), Шум квантування, LOD (3σ) та LOQ (10σ)", size=16, bold=True))

    # Ліва панель: Аналоговий сигнал, сходинки АЦП і помилка квантування
    lx, ly, lw, lh = 30, 50, 410, 390
    frags.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(lx + lw/2, ly + 24, "Квантування АЦП та шум e_q ∈ [−Δ/2, +Δ/2]", size=13, bold=True, color=INK))

    # Графік сходинок
    gx, gy, gw, gh = lx + 50, ly + 60, 320, 200
    frags.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.5)) # вісь X
    frags.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.5))           # вісь Y
    frags.append(text(gx + gw - 20, gy + gh + 18, "Вхід Vin", size=11, color=MUTED))
    frags.append(text(gx - 25, gy + 15, "Код", size=11, color=MUTED))

    # Сходинки
    step_w = gw / 4
    step_h = gh / 4
    for i in range(4):
        # Горизонтальна сходинка
        frags.append(line(gx + i * step_w, gy + gh - (i + 1) * step_h, gx + (i + 1) * step_w, gy + gh - (i + 1) * step_h, color=POS, sw=2.2))
        if i < 3:
            # Вертикальний перехід
            frags.append(line(gx + (i + 1) * step_w, gy + gh - (i + 1) * step_h, gx + (i + 1) * step_w, gy + gh - (i + 2) * step_h, color=POS, sw=1.5, dash="3,3"))
        # Позначки рівнів LSB
        frags.append(line(gx - 4, gy + gh - (i + 1) * step_h, gx, gy + gh - (i + 1) * step_h, color=LINE, sw=1.2))
        frags.append(text(gx - 18, gy + gh - (i + 1) * step_h + 4, "%d LSB" % (i + 1), size=10, color=MUTED, anchor="end"))

    # Ідеальна пряма
    frags.append(line(gx, gy + gh, gx + gw, gy, color=NEG, sw=1.5, dash="4,4"))

    # Пояснення під графіком
    info_y = gy + gh + 35
    frags.append(rect(lx + 20, info_y, lw - 40, 75, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(lx + 30, info_y + 20, "• Крок квантування: Δ = Vref / 2^N (Роздільність)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(lx + 30, info_y + 40, "• Рівномірний розподіл похибки: u_q = Δ / √12 ≈ 0.289 Δ", size=11, color=NEG, anchor="start"))
    frags.append(text(lx + 30, info_y + 60, "• Висока розрядність не рятує від шуму аналогового тракту", size=11, color=MUTED, anchor="start", italic=True))

    # Права панель: Рівень фонового шуму, LOD та LOQ
    rx, ry, rw, rh = 460, 50, 410, 390
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(rx + rw/2, ry + 24, "Межі виявлення сигналу в аналоговому шумі", size=13, bold=True, color=INK))

    pgx, pgy, pgw, pgh = rx + 60, ry + 60, 300, 200
    frags.append(line(pgx, pgy + pgh, pgx + pgw, pgy + pgh, color=LINE, sw=1.5))
    frags.append(line(pgx, pgy, pgx, pgy + pgh, color=LINE, sw=1.5))
    frags.append(text(pgx + pgw - 20, pgy + pgh + 18, "Час t", size=11, color=MUTED))
    frags.append(text(pgx - 25, pgy + 15, "Сигнал", size=11, color=MUTED))

    # Шумова доріжка навколо 0 (Blank Noise)
    noise_points = [
        (0, 5), (20, -7), (40, 8), (60, -4), (80, 6), (100, -8),
        (120, 7), (140, -5), (160, 9), (180, -6), (200, 8), (220, -7),
        (240, 6), (260, -8), (280, 5), (300, -6)
    ]
    baseline_y = pgy + pgh - 30
    for i in range(len(noise_points) - 1):
        x1, y1 = pgx + noise_points[i][0], baseline_y - noise_points[i][1]
        x2, y2 = pgx + noise_points[i+1][0], baseline_y - noise_points[i+1][1]
        frags.append(line(x1, y1, x2, y2, color="#94a3b8", sw=1.2))

    # Рівні LOD (3σ) та LOQ (10σ)
    sigma_px = 8
    lod_y = baseline_y - 3 * sigma_px
    loq_y = baseline_y - 10 * sigma_px

    # Смуга 3σ (LOD)
    frags.append(line(pgx, lod_y, pgx + pgw, lod_y, color="#f59e0b", sw=1.8, dash="5,3"))
    frags.append(text(pgx + pgw - 5, lod_y - 6, "LOD = 3·σ_noise (Межа виявлення)", size=10, color="#b45309", anchor="end", bold=True))

    # Смуга 10σ (LOQ)
    frags.append(line(pgx, loq_y, pgx + pgw, loq_y, color=FIELD, sw=1.8, dash="5,3"))
    frags.append(text(pgx + pgw - 5, loq_y - 6, "LOQ = 10·σ_noise (Кількісний вимір)", size=10, color="#15803d", anchor="end", bold=True))

    # Рівень нульової лінії
    frags.append(line(pgx, baseline_y, pgx + pgw, baseline_y, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(pgx - 10, baseline_y + 4, "0", size=10, color=MUTED, anchor="end"))

    # Пояснення правої панелі
    rinfo_y = pgy + pgh + 35
    frags.append(rect(rx + 20, rinfo_y, rw - 40, 75, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(rx + 30, rinfo_y + 20, "• Шум шумує: сигнал < 3σ невідрізнимий від флуктуацій", size=11, color=POS, anchor="start"))
    frags.append(text(rx + 30, rinfo_y + 40, "• 3σ (LOD): впевненість 99.7% у присутності явища", size=11, color="#b45309", anchor="start", bold=True))
    frags.append(text(rx + 30, rinfo_y + 60, "• 10σ (LOQ): допустима точність кількісної оцінки (RSD ≤ 10%)", size=11, color=FIELD, anchor="start", bold=True))

    return render(os.path.join(IMG_DIR, "resolution-vs-lod-noise.svg"), w, h, *frags)


def fig_gum_uncertainty_framework():
    """Фігура 3: Архітектура оцінювання невизначеності за ISO/IEC Guide 98-3 (GUM)."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 26, "Структура оцінювання сумарної невизначеності (GUM Framework)", size=16, bold=True))

    # Джерело Типу A (ліворуч)
    ax, ay, aw, ah = 40, 60, 380, 150
    frags.append(rect(ax, ay, aw, ah, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(ax + 20, ay + 26, "Оцінювання за Типом A (Статистичне)", size=13, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(ax + 20, ay + 50, "Базується на серії N незалежних повторних спостережень", size=11, color=MUTED, anchor="start"))
    frags.append(text(ax + 20, ay + 74, "• Вибіркове середнє: x̄ = (1/N) Σ x_k", size=11, color=INK, anchor="start"))
    frags.append(text(ax + 20, ay + 96, "• Вибіркова дисперсія (Бессель): s² = Σ(x_k − x̄)² / (N − 1)", size=11, color=INK, anchor="start"))
    frags.append(text(ax + 20, ay + 124, "➜ Стандартна невизначеність: u_A = s / √N", size=12, bold=True, color="#1e40af", anchor="start"))

    # Джерело Типу B (праворуч)
    bx, by, bw, bh = 480, 60, 380, 150
    frags.append(rect(bx, by, bw, bh, fill="#fefce8", stroke="#eab308", sw=1.5, rx=8))
    frags.append(text(bx + 20, by + 26, "Оцінювання за Типом B (Апріорне)", size=13, bold=True, color="#854d0e", anchor="start"))
    frags.append(text(bx + 20, by + 50, "Паспорти, сертифікати калібрування, крок АЦП, термодрейф", size=11, color=MUTED, anchor="start"))
    frags.append(text(bx + 20, by + 74, "• Рівномірний (прямокутний) [−a, +a]: u_B = a / √3", size=11, color=INK, anchor="start"))
    frags.append(text(bx + 20, by + 96, "• Трикутний розподіл [−a, +a]: u_B = a / √6", size=11, color=INK, anchor="start"))
    frags.append(text(bx + 20, by + 124, "• Нормальний паспортний (довідковий k): u_B = U_spec / k", size=11, color=INK, anchor="start"))

    # Стрілки від Типу A і B до блоку комбінування
    frags.append(arrow(ax + aw/2, ay + ah, w/2 - 40, 250, color=LINE, sw=2))
    frags.append(arrow(bx + bw/2, by + bh, w/2 + 40, 250, color=LINE, sw=2))

    # Центральний блок: Закон поширення та сумарна невизначеність u_c
    cx, cy, cw, ch = 180, 250, 540, 100
    frags.append(rect(cx, cy, cw, ch, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(w / 2, cy + 24, "Сумарна стандартна невизначеність (Combined Uncertainty)", size=13, bold=True, color="#166534"))
    frags.append(text(w / 2, cy + 50, "Модель вимірювання: Y = f(X₁, X₂, ..., X_m),  c_i = ∂f/∂x_i (чутливість)", size=11, color=INK))
    frags.append(text(w / 2, cy + 78, "u_c(y) = √ [ Σ (c_i · u(x_i))² + 2 Σ c_i c_j cov(x_i, x_j) ]", size=12, bold=True, color="#15803d"))

    # Стрілка вниз до розширеної невизначеності
    frags.append(arrow(w / 2, cy + ch, w / 2, 385, color=LINE, sw=2))

    # Нижній блок: Розширена невизначеність U та звіт
    ex, ey, ew, eh = 180, 385, 540, 75
    frags.append(rect(ex, ey, ew, eh, fill="#fdf2f8", stroke="#db2777", sw=1.5, rx=8))
    frags.append(text(w / 2, ey + 24, "Розширена невизначеність (Expanded Uncertainty): U = k · u_c(y)", size=13, bold=True, color="#9d174d"))
    frags.append(text(w / 2, ey + 46, "k = 2.00 для довірчої ймовірності P ≈ 95.45% (або t-коефіцієнт Стьюдента за Велчем-Саттерзвейтом)", size=11, color=INK))
    frags.append(text(w / 2, ey + 64, "Метрологічний запис результату:  Y = ȳ ± U  (з вказанням k та P)", size=11, bold=True, color=INK))

    return render(os.path.join(IMG_DIR, "gum-uncertainty-framework.svg"), w, h, *frags)


def fig_systematic_vs_random():
    """Фігура 4: Механізми похибок — Зсув, Масштаб, Дрейф проти Флуктуаційного шуму."""
    w, h = 900, 440
    frags = []

    frags.append(text(w / 2, 26, "Класифікація спотворень вимірювального тракту: Систематичні проти Випадкових", size=16, bold=True))

    # Ліва частина: Систематичні похибки (Offset, Gain, Non-linearity)
    sx, sy, sw, sh = 30, 55, 410, 365
    frags.append(rect(sx, sy, sw, sh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(sx + sw/2, sy + 24, "Систематичні похибки (Детерміновані / Bias)", size=13, bold=True, color=POS))

    # Міні-графік систематичних ефектів
    sgx, sgy, sgw, sgh = sx + 45, sy + 45, 320, 160
    frags.append(line(sgx, sgy + sgh, sgx + sgw, sgy + sgh, color=LINE, sw=1.2))
    frags.append(line(sgx, sgy, sgx, sgy + sgh, color=LINE, sw=1.2))
    frags.append(text(sgx + sgw - 10, sgy + sgh + 16, "Vin", size=10, color=MUTED))
    frags.append(text(sgx - 15, sgy + 12, "Vout", size=10, color=MUTED))

    # Ідеальна лінія
    frags.append(line(sgx, sgy + sgh, sgx + sgw, sgy, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(sgx + sgw - 40, sgy + 20, "Ідеал (1:1)", size=9, color=MUTED))

    # Лінія з Offset (зсув нуля)
    frags.append(line(sgx, sgy + sgh - 25, sgx + sgw, sgy - 25 + 30, color="#ea580c", sw=1.8))
    frags.append(text(sgx + 10, sgy + sgh - 35, "+ Offset (Vos)", size=10, color="#ea580c", bold=True, anchor="start"))

    # Лінія з Gain error (масштабна похибка)
    frags.append(line(sgx, sgy + sgh, sgx + sgw, sgy + 40, color=POS, sw=1.8))
    frags.append(text(sgx + sgw - 20, sgy + 60, "Gain error", size=10, color=POS, bold=True, anchor="end"))

    # Опис систематичних компонентів
    sinfo_y = sy + 220
    frags.append(rect(sx + 15, sinfo_y, sw - 30, 135, fill="#fff7ed", stroke="#fed7aa", sw=1, rx=6))
    frags.append(text(sx + 25, sinfo_y + 20, "1. Зсув нуля (Offset / Bias):", size=11, bold=True, color="#9a3412", anchor="start"))
    frags.append(text(sx + 35, sinfo_y + 38, "Термоелектричні ЕРС (Seebeck), струми витоку, Vos ОП", size=10, color=INK, anchor="start"))
    frags.append(text(sx + 25, sinfo_y + 58, "2. Масштабна похибка (Gain Error):", size=11, bold=True, color="#9a3412", anchor="start"))
    frags.append(text(sx + 35, sinfo_y + 76, "Допуск опорної напруги Vref, відхилення дільників R1/R2", size=10, color=INK, anchor="start"))
    frags.append(text(sx + 25, sinfo_y + 96, "3. Температурний дрейф (Drift):", size=11, bold=True, color="#9a3412", anchor="start"))
    frags.append(text(sx + 35, sinfo_y + 114, "Повільна зміна параметрів у часі (ppm/°C, ppm/рік)", size=10, color=INK, anchor="start"))

    # Права частина: Випадкові похибки (Noise, Fluctuations)
    rx, ry, rw, rh = 460, 55, 410, 365
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(rx + rw/2, ry + 24, "Випадкові похибки (Стохастичні / Noise)", size=13, bold=True, color=NEG))

    # Міні-графік спектру та часового ряду
    rgx, rgy, rgw, rgh = rx + 45, ry + 45, 320, 160
    frags.append(line(rgx, rgy + rgh, rgx + rgw, rgy + rgh, color=LINE, sw=1.2))
    frags.append(line(rgx, rgy, rgx, rgy + rgh, color=LINE, sw=1.2))
    frags.append(text(rgx + rgw - 10, rgy + rgh + 16, "Час", size=10, color=MUTED))
    frags.append(text(rgx - 15, rgy + 12, "V(t)", size=10, color=MUTED))

    # Шум (сира вибірка)
    raw_noise = [
        (0, 0), (15, 22), (30, -18), (45, 28), (60, -32), (75, 14),
        (90, -25), (105, 30), (120, -12), (135, 24), (150, -28),
        (165, 16), (180, -20), (195, 34), (210, -18), (225, 26),
        (240, -30), (255, 12), (270, -22), (285, 18), (300, -5)
    ]
    for i in range(len(raw_noise) - 1):
        x1, y1 = rgx + raw_noise[i][0], rgy + rgh/2 - raw_noise[i][1]
        x2, y2 = rgx + raw_noise[i+1][0], rgy + rgh/2 - raw_noise[i+1][1]
        frags.append(line(x1, y1, x2, y2, color="#93c5fd", sw=1.2))

    # Усереднений сигнал (N=16)
    for i in range(len(raw_noise) - 1):
        x1, y1 = rgx + raw_noise[i][0], rgy + rgh/2 - raw_noise[i][1] * 0.25
        x2, y2 = rgx + raw_noise[i+1][0], rgy + rgh/2 - raw_noise[i+1][1] * 0.25
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2))

    frags.append(text(rgx + 20, rgy + 20, "Сирий шум σ", size=10, color="#60a5fa", anchor="start"))
    frags.append(text(rgx + 20, rgy + 36, "Усереднене (N=16): σ/√16 = σ/4", size=10, color=NEG, bold=True, anchor="start"))

    # Опис випадкових компонентів
    rinfo_y = ry + 220
    frags.append(rect(rx + 15, rinfo_y, rw - 30, 135, fill="#eff6ff", stroke="#bfdbfe", sw=1, rx=6))
    frags.append(text(rx + 25, rinfo_y + 20, "1. Тепловий шум Найквіста-Джонсона:", size=11, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(rx + 35, rinfo_y + 38, "Vn = √(4 k_B T R Δf) — білий шум резистивного опору кола", size=10, color=INK, anchor="start"))
    frags.append(text(rx + 25, rinfo_y + 58, "2. Дробовий шум (Shot noise):", size=11, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(rx + 35, rinfo_y + 76, "In = √(2 q I Δf) — квантова дискретність носіїв заряду", size=10, color=INK, anchor="start"))
    frags.append(text(rx + 25, rinfo_y + 96, "3. Флікер-шум (1/f noise):", size=11, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(rx + 35, rinfo_y + 114, "Низькочастотні флуктуації контактів та напівпровідників", size=10, color=INK, anchor="start"))

    return render(os.path.join(IMG_DIR, "systematic-vs-random.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_accuracy_precision()
    fig_resolution_vs_lod_noise()
    fig_gum_uncertainty_framework()
    fig_systematic_vs_random()
    print("All figures generated successfully.")
