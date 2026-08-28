# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Гомографія: перетворення площини в площину'."""

import sys
import os

# scripts/ у корені репо: 4 рівні вгору від root/eng/sf-visual/homography
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")


def fig_homography_geometry():
    """Геометрична модель проекції площини між двома камерами та матриця гомографії."""
    W, H_CANVAS = 840, 480
    os.makedirs(OUT, exist_ok=True)
    p = []

    # 1. 3D Площина в просторі (внизу)
    # Полігон площини Pi
    p.append('<polygon points="120,380 720,380 640,460 40,460" fill="#f8fafc" stroke="#64748b" stroke-width="1.8"/>')
    p.append(text(390, 445, "Площина сцени Π : nᵀ X = d", size=14, color="#334155", bold=True))

    # Точка X на площині
    px_x, px_y = 380, 400
    p.append(circle(px_x, px_y, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(px_x + 18, px_y + 5, "X (3D-точка)", size=13, color=POS, bold=True))

    # Вектор нормалі n до площини
    p.append(arrow(px_x, px_y, px_x, px_y - 65, color=FIELD, sw=2))
    p.append(text(px_x - 22, px_y - 35, "n (нормаль)", size=13, color=FIELD, bold=True))

    # Відстань d до площини від центру C1 (пунктир)
    p.append(line(160, 110, 160, 410, color=MUTED, sw=1.2, dash="4,4"))
    p.append(text(145, 270, "d", size=13, color=MUTED, italic=True))

    # 2. Камера 1 (ліва)
    c1_x, c1_y = 160, 110
    p.append(circle(c1_x, c1_y, 6, fill="#3b82f6", stroke=LINE, sw=1.5))
    p.append(text(c1_x, c1_y - 14, "C₁ (Камера 1)", size=14, color=INK, bold=True))

    # Площина зображення 1 (трапеція / прямокутник у перспективі)
    p.append('<polygon points="100,190 220,190 200,260 80,260" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>')
    p.append(text(140, 210, "Зображення 1", size=11, color="#1e40af", bold=True))

    # Точка проекції x₁ на знімку 1
    x1_pt_x, x1_pt_y = 155, 225
    p.append(circle(x1_pt_x, x1_pt_y, 4, fill=POS, stroke=LINE, sw=1.2))
    p.append(text(x1_pt_x - 22, x1_pt_y + 4, "x₁", size=13, color=POS, bold=True))

    # Промінь з C1 через x1 до X
    p.append(line(c1_x, c1_y, px_x, px_y, color="#ef4444", sw=1.5, dash="5,3"))

    # 3. Камера 2 (права)
    c2_x, c2_y = 660, 130
    p.append(circle(c2_x, c2_y, 6, fill="#10b981", stroke=LINE, sw=1.5))
    p.append(text(c2_x, c2_y - 14, "C₂ (Камера 2)", size=14, color=INK, bold=True))

    # Площина зображення 2
    p.append('<polygon points="600,200 720,200 700,270 580,270" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>')
    p.append(text(665, 220, "Зображення 2", size=11, color="#065f46", bold=True))

    # Точка проекції x₂ на знімку 2
    x2_pt_x, x2_pt_y = 645, 235
    p.append(circle(x2_pt_x, x2_pt_y, 4, fill=POS, stroke=LINE, sw=1.2))
    p.append(text(x2_pt_x + 22, x2_pt_y + 4, "x₂", size=13, color=POS, bold=True))

    # Промінь з C2 через x2 до X
    p.append(line(c2_x, c2_y, px_x, px_y, color="#ef4444", sw=1.5, dash="5,3"))

    # 4. Базове перетворення між камерами: Поворот R та Зсув t
    p.append(arrow(c1_x + 15, c1_y, c2_x - 15, c2_y, color="#6366f1", sw=2))
    p.append(text(410, 105, "Поза камери: поворот R, зсув t", size=13, color="#4338ca", bold=True))

    # 5. Матриця гомографії H: дуга перенесення між площинами зображень
    p.append('<path d="M 215,225 Q 400,165 585,235" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="0" marker-end="url(#arrow)"/>')
    p.append(textbox(400, 200, "Гомографія: x₂ ≃ H · x₁", size=14, pad=7, fill="#fee2e2", stroke="#dc2626", bold=True)[0])

    # Блок формули структури гомографії
    p.append(fitbox(210, 290, 420, 60, "Алгебраїчна структура матриці H:\nH = K₂ · (R − t·nᵀ / d) · K₁⁻¹", size=13, fill="#f8fafc", stroke="#94a3b8", bold=False))

    render(os.path.join(OUT, "homography-geometry.svg"), W, H_CANVAS, *p,
           title="Геометрична модель гомографії: проєкція площини між двома камерами")


def fig_dlt_ransac_pipeline():
    """Конвеєр оцінки гомографії: нормалізація Гартлі, DLT, RANSAC та декомпозиція."""
    W, H_CANVAS = 860, 490
    os.makedirs(OUT, exist_ok=True)
    p = []

    # 5 етапів конвеєра згори донизу та зліва направо

    # Етап 1: Вхідні відповідності
    b1, _, _ = textbox(130, 90, "1. Вхідні пари точок\n{xᵢ ↔ x'ᵢ} (ORB / SIFT)\nШум + викиди (outliers)", size=12, pad=8, fill="#fef2f2", stroke="#ef4444", bold=True)
    p.append(b1)

    p.append(arrow(220, 90, 270, 90, color=LINE, sw=1.5))

    # Етап 2: Нормалізація Гартлі
    b2, _, _ = textbox(380, 90, "2. Нормалізація Гартлі\nx̃ = T·x,  x̃' = T'·x'\nЦентр (0,0), сер. відст. √2", size=12, pad=8, fill="#eff6ff", stroke="#3b82f6", bold=True)
    p.append(b2)

    p.append(arrow(490, 90, 540, 90, color=LINE, sw=1.5))

    # Етап 3: RANSAC цикл
    p.append(rect(545, 40, 300, 200, fill="#f8fafc", stroke="#6366f1", sw=1.8, rx=8))
    p.append(text(695, 62, "3. Робастний цикл RANSAC", size=13, color="#4338ca", bold=True))

    p.append(fitbox(560, 75, 270, 42, "Вибірка: 4 випадкові пари точок\n(жодні три не на одній прямій)", size=11, fill="#ffffff", stroke="#cbd5e1"))
    p.append(arrow(695, 117, 695, 130, color=LINE, sw=1.2))

    p.append(fitbox(560, 130, 270, 42, "Розв'язок DLT: A·h = 0 через SVD\nМінімальний правий вектор v₉", size=11, fill="#ffffff", stroke="#cbd5e1"))
    p.append(arrow(695, 172, 695, 185, color=LINE, sw=1.2))

    p.append(fitbox(560, 185, 270, 45, "Підрахунок inliers за похибкою\nСиметрична відстань перенесення < ε", size=11, fill="#ffffff", stroke="#cbd5e1"))

    # Стрілка від RANSAC до нелінійного уточнення
    p.append(arrow(695, 240, 695, 280, color=LINE, sw=1.5))

    # Етап 4: Нелінійне уточнення на inliers
    b4, _, _ = textbox(695, 320, "4. Нелінійна оптимізація\nЛевенберг–Марквардт на inliers\nМін. похибки перепроєкції", size=12, pad=8, fill="#fefce8", stroke="#eab308", bold=True)
    p.append(b4)

    # Денормалізація: H = T'⁻¹ · H_norm · T
    p.append(arrow(580, 320, 480, 320, color=LINE, sw=1.5))
    b_denorm, _, _ = textbox(380, 320, "Денормалізація матриці:\nH = (T')⁻¹ · H̃ · T", size=12, pad=8, fill="#f1f5f9", stroke="#64748b", bold=True)
    p.append(b_denorm)

    # Розгалуження на 2 застосування:
    p.append(arrow(280, 320, 210, 260, color="#059669", sw=1.8))
    p.append(arrow(280, 320, 210, 390, color="#2563eb", sw=1.8))

    # Застосування А: Декомпозиція пози (R, t, n)
    b5a, _, _ = textbox(110, 255, "5a. Декомпозиція пози\nH → {R, t/d, n}\nОдометрія / Посадка дрона", size=11, pad=7, fill="#ecfdf5", stroke="#10b981", bold=True)
    p.append(b5a)

    # Застосування Б: Inverse Perspective Mapping (BEV)
    b5b, _, _ = textbox(110, 395, "5b. Деварпінг і IPM\nBird's Eye View для автопілота\nЗворотний білінійний варпінг", size=11, pad=7, fill="#eff6ff", stroke="#3b82f6", bold=True)
    p.append(b5b)

    # Рамка пояснення внизу
    p.append(fitbox(280, 400, 560, 60, "Ключова гарантія: Hartley-нормалізація зменшує число обумовленості матриці AᵀA з 10¹² до 10²,\nщо забезпечує стійкість SVD до шуму дискретизації та запобігає виродженню.", size=12, fill="#f8fafc", stroke="#94a3b8", bold=False))

    render(os.path.join(OUT, "dlt-ransac-pipeline.svg"), W, H_CANVAS, *p,
           title="Конвеєр робастної оцінки гомографії: від точок до пози та деварпінгу")


if __name__ == "__main__":
    fig_homography_geometry()
    fig_dlt_ransac_pipeline()
    print("Figures generated successfully.")
