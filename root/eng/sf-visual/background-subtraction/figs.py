# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Різниця кадрів: рух без нейромережі'.
Вивід у ./img/
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_frame_differencing_defects():
    """Ілюстрація дефектів двокадрового віднімання проти трикадрового та еталону."""
    w, h = 820, 360
    frags = []

    # 4 колонки: Кадри t-1 і t -> Двокадрова різниця -> Трикадрова різниця -> Справжній об'єкт
    col_w = 175
    col_gap = 20
    x0 = 30
    top_y = 55
    box_h = 240

    cols = [
        ("Кадри t−1 та t", FILL),
        ("Двокадрова різниця", "#fff3f2"),
        ("Трикадрова різниця", "#f0f7ff"),
        ("Еталонна маска тла", "#f2faf4")
    ]

    for i, (title, fill_col) in enumerate(cols):
        bx = x0 + i * (col_w + col_gap)
        
        # Header rect
        frags.append(rect(bx, top_y, col_w, 32, fill=fill_col, stroke=LINE, sw=1.2, rx=4))
        frags.append(text(bx + col_w / 2, top_y + 20, title, size=12, bold=True, color=INK))
        
        # Content box below header
        frags.append(rect(bx, top_y + 36, col_w, box_h - 36, fill=fill_col, stroke=LINE, sw=1.2, rx=6))
        
        # Visual diagram inside box
        vy = top_y + 48
        if i == 0:
            # Draw moving object at t-1 (dashed) and t (solid)
            frags.append(rect(bx + 20, vy, 55, 60, fill="#d1d5db", stroke=MUTED, sw=1.5, rx=3))
            frags.append(text(bx + 47, vy + 35, "t−1", size=12, color=MUTED, bold=True))
            
            frags.append(rect(bx + 75, vy, 55, 60, fill="#9ca3af", stroke=INK, sw=1.8, rx=3))
            frags.append(text(bx + 102, vy + 35, "t", size=12, color=INK, bold=True))
            
            frags.append(arrow(bx + 55, vy + 75, bx + 95, vy + 75, color=POS, sw=1.5))
            frags.append(text(bx + 75, vy + 95, "вектор руху", size=11, color=POS))
            
            frags.append(text(bx + col_w/2, vy + 125, "Рух однорідного", size=11, color=INK))
            frags.append(text(bx + col_w/2, vy + 142, "нетекстурованого тіла", size=11, color=INK))
            
        elif i == 1:
            # 2-frame diff: hollow front + hollow ghost behind
            frags.append(rect(bx + 20, vy, 55, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
            frags.append(text(bx + 47, vy + 35, "Фантом", size=11, color=POS, bold=True))
            
            frags.append(rect(bx + 75, vy, 55, 60, fill="#ffffff", stroke=POS, sw=2.5, rx=3))
            frags.append(text(bx + 102, vy + 35, "Дірка!", size=12, color=POS, bold=True))
            
            frags.append(text(bx + col_w/2, vy + 85, "Різниця всередині = 0", size=11, color=POS, bold=True))
            frags.append(text(bx + col_w/2, vy + 105, "(порожнистий контур)", size=11, color=MUTED))
            frags.append(text(bx + col_w/2, vy + 130, "Старий слід не зникає", size=11, color=POS))
            
        elif i == 2:
            # 3-frame diff: ghost suppressed, but interior still hollow
            frags.append(rect(bx + 45, vy, 65, 60, fill="#ffffff", stroke=NEG, sw=2.2, rx=3))
            frags.append(text(bx + 77, vy + 35, "Контур t", size=11, color=NEG, bold=True))
            
            frags.append(text(bx + col_w/2, vy + 85, "Фантомний слід", size=11, color=FIELD, bold=True))
            frags.append(text(bx + col_w/2, vy + 103, "успішно пригнічено", size=11, color=FIELD))
            frags.append(text(bx + col_w/2, vy + 125, "Але середина об'єкта", size=11, color=POS))
            frags.append(text(bx + col_w/2, vy + 142, "все одно порожня", size=11, color=POS))
            
        elif i == 3:
            # True background subtraction: solid filled blob
            frags.append(rect(bx + 45, vy, 65, 60, fill="#22c55e", stroke="#15803d", sw=2, rx=3))
            frags.append(text(bx + 77, vy + 35, "Суцільний", size=12, color="#ffffff", bold=True))
            
            frags.append(text(bx + col_w/2, vy + 85, "Повний силует об'єкта", size=11, color=FIELD, bold=True))
            frags.append(text(bx + col_w/2, vy + 105, "Не зникає при зупинці", size=11, color=FIELD))
            frags.append(text(bx + col_w/2, vy + 128, "Чисті межі для трекінгу", size=11, color=INK))

        # Bottom summary
        frags.append(line(bx + 10, vy + 155, bx + col_w - 10, vy + 155, color=MUTED, sw=0.8, dash="3,3"))
        if i == 0:
            frags.append(text(bx + col_w/2, vy + 172, "Вхідний потік", size=11, color=MUTED, bold=True))
        elif i == 1:
            frags.append(text(bx + col_w/2, vy + 172, "Пам'ять: 1 кадр", size=11, color=POS, bold=True))
        elif i == 2:
            frags.append(text(bx + col_w/2, vy + 172, "Пам'ять: 2 кадри", size=11, color=NEG, bold=True))
        elif i == 3:
            frags.append(text(bx + col_w/2, vy + 172, "Пам'ять: модель B_t", size=11, color=FIELD, bold=True))

    return render(os.path.join(OUT_DIR, "frame-differencing-defects.svg"), w, h, *frags,
                  title="Порівняння двокадрової різниці, трикадрової різниці та моделі тла")


def fig_running_average_adaptation():
    """Ілюстрація біжучого середнього, селективного оновлення та адаптації до світла."""
    w, h = 820, 360
    frags = []

    p_w = 370
    p_h = 280
    top_y = 50

    # Panel 1: Неселективне оновлення
    frags.append(rect(25, top_y, p_w, 32, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(25 + p_w/2, top_y + 20, "Неселективне оновлення: B_t = (1−α)·B_{t−1} + α·I_t", size=12, bold=True, color=POS))
    
    frags.append(rect(25, top_y + 36, p_w, p_h - 36, fill="#fffaf9", stroke=LINE, sw=1.5, rx=8))

    # Timeline curve for Panel 1
    ax_x0, ax_y0 = 60, top_y + 190
    frags.append(line(ax_x0, ax_y0, ax_x0 + 300, ax_y0, color=LINE, sw=1.5))
    frags.append(line(ax_x0, ax_y0, ax_x0, ax_y0 - 120, color=LINE, sw=1.5))
    frags.append(text(ax_x0 + 305, ax_y0 + 4, "Час t", size=11, color=INK))
    frags.append(text(ax_x0 - 5, ax_y0 - 125, "Яскравість I", size=11, color=INK, anchor="end"))

    # True signal (step up during object stay)
    frags.append(line(ax_x0, ax_y0 - 30, ax_x0 + 80, ax_y0 - 30, color=NEG, sw=2))
    frags.append(line(ax_x0 + 80, ax_y0 - 30, ax_x0 + 80, ax_y0 - 100, color=NEG, sw=2))
    frags.append(line(ax_x0 + 80, ax_y0 - 100, ax_x0 + 200, ax_y0 - 100, color=NEG, sw=2))
    frags.append(line(ax_x0 + 200, ax_y0 - 100, ax_x0 + 200, ax_y0 - 30, color=NEG, sw=2))
    frags.append(line(ax_x0 + 200, ax_y0 - 30, ax_x0 + 280, ax_y0 - 30, color=NEG, sw=2))
    frags.append(text(ax_x0 + 140, ax_y0 - 108, "Об'єкт у кадрі", size=11, color=NEG, bold=True))

    # Background model curve (slowly rises towards object, then slowly falls -> ghost)
    frags.append(line(ax_x0, ax_y0 - 30, ax_x0 + 80, ax_y0 - 30, color=POS, sw=2, dash="4,3"))
    points_rise = [(ax_x0 + 80, ax_y0 - 30), (ax_x0 + 110, ax_y0 - 55), (ax_x0 + 150, ax_y0 - 80), (ax_x0 + 200, ax_y0 - 95)]
    for i in range(len(points_rise)-1):
        frags.append(line(points_rise[i][0], points_rise[i][1], points_rise[i+1][0], points_rise[i+1][1], color=POS, sw=2, dash="4,3"))
    points_fall = [(ax_x0 + 200, ax_y0 - 95), (ax_x0 + 230, ax_y0 - 65), (ax_x0 + 260, ax_y0 - 45), (ax_x0 + 280, ax_y0 - 35)]
    for i in range(len(points_fall)-1):
        frags.append(line(points_fall[i][0], points_fall[i][1], points_fall[i+1][0], points_fall[i+1][1], color=POS, sw=2, dash="4,3"))

    frags.append(text(ax_x0 + 155, ax_y0 - 50, "B_t впікає об'єкт!", size=11, color=POS, bold=True))
    frags.append(text(ax_x0 + 245, ax_y0 - 80, "Фантом після відходу", size=10, color=POS))
    frags.append(text(25 + p_w/2, top_y + p_h - 15, "Дефект: модель руйнується повільними або зупиненими об'єктами", size=11, color=POS))

    # Panel 2: Селективне оновлення
    bx2 = 425
    frags.append(rect(bx2, top_y, p_w, 32, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(bx2 + p_w/2, top_y + 20, "Селективне оновлення: оновлюємо лише якщо Mask == 0", size=12, bold=True, color=FIELD))

    frags.append(rect(bx2, top_y + 36, p_w, p_h - 36, fill="#f2faf5", stroke=LINE, sw=1.5, rx=8))

    # Timeline curve for Panel 2
    ax2_x0, ax2_y0 = bx2 + 35, top_y + 190
    frags.append(line(ax2_x0, ax2_y0, ax2_x0 + 300, ax2_y0, color=LINE, sw=1.5))
    frags.append(line(ax2_x0, ax2_y0, ax2_x0, ax2_y0 - 120, color=LINE, sw=1.5))
    frags.append(text(ax2_x0 + 305, ax2_y0 + 4, "Час t", size=11, color=INK))
    frags.append(text(ax2_x0 - 5, ax2_y0 - 125, "Яскравість I", size=11, color=INK, anchor="end"))

    # True signal with step and gentle slope
    frags.append(line(ax2_x0, ax2_y0 - 25, ax2_x0 + 80, ax2_y0 - 35, color=NEG, sw=2))
    frags.append(line(ax2_x0 + 80, ax2_y0 - 35, ax2_x0 + 80, ax2_y0 - 100, color=NEG, sw=2))
    frags.append(line(ax2_x0 + 80, ax2_y0 - 100, ax2_x0 + 200, ax2_y0 - 100, color=NEG, sw=2))
    frags.append(line(ax2_x0 + 200, ax2_y0 - 100, ax2_x0 + 200, ax2_y0 - 50, color=NEG, sw=2))
    frags.append(line(ax2_x0 + 200, ax2_y0 - 50, ax2_x0 + 280, ax2_y0 - 60, color=NEG, sw=2))

    # Background model tracking illumination change smoothly
    frags.append(line(ax2_x0, ax2_y0 - 25, ax2_x0 + 80, ax2_y0 - 35, color=FIELD, sw=2.5, dash="4,3"))
    frags.append(line(ax2_x0 + 80, ax2_y0 - 35, ax2_x0 + 200, ax2_y0 - 50, color=FIELD, sw=2.5, dash="4,3"))
    frags.append(line(ax2_x0 + 200, ax2_y0 - 50, ax2_x0 + 280, ax2_y0 - 60, color=FIELD, sw=2.5, dash="4,3"))

    frags.append(text(ax2_x0 + 140, ax2_y0 - 108, "Об'єкт виділено", size=11, color=NEG, bold=True))
    frags.append(text(ax2_x0 + 140, ax2_y0 - 25, "B_t заморожено (Mask=1)", size=11, color=FIELD, bold=True))
    frags.append(text(ax2_x0 + 245, ax2_y0 - 75, "Тло чисте!", size=11, color=FIELD, bold=True))

    frags.append(text(bx2 + p_w/2, top_y + p_h - 15, "Перевага: плавна адаптація до світла без втрати форми об'єктів", size=11, color=FIELD))

    return render(os.path.join(OUT_DIR, "running-average-adaptation.svg"), w, h, *frags,
                  title="Порівняння неселективного та селективного біжучого середнього тла")


def fig_gmm_multimodal_distribution():
    """Ілюстрація суміші гаусіанів (GMM/MoG) для мультимодального динамічного тла."""
    w, h = 820, 360
    frags = []

    p1_w = 400
    p2_w = 360
    top_y = 50
    p_h = 280

    # Left Panel: Multimodal distribution
    frags.append(rect(25, top_y, p1_w, 32, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(25 + p1_w/2, top_y + 20, "Мультимодальний піксель: коливання листя / вода", size=12, bold=True, color=INK))

    frags.append(rect(25, top_y + 36, p1_w, p_h - 36, fill="#fafaf9", stroke=LINE, sw=1.5, rx=8))

    # Coordinate system for histogram
    ax_x, ax_y = 60, top_y + 210
    frags.append(line(ax_x, ax_y, ax_x + 330, ax_y, color=LINE, sw=1.5))
    frags.append(line(ax_x, ax_y, ax_x, ax_y - 140, color=LINE, sw=1.5))
    frags.append(text(ax_x + 335, ax_y + 4, "Яскравість (0..255)", size=11, color=INK))
    frags.append(text(ax_x - 5, ax_y - 145, "Частота P(I)", size=11, color=INK, anchor="end"))

    # Draw Gaussian 1: Green leaf peak
    g1_pts = [(ax_x + 30, ax_y), (ax_x + 60, ax_y - 15), (ax_x + 80, ax_y - 80), (ax_x + 95, ax_y - 125),
              (ax_x + 110, ax_y - 80), (ax_x + 130, ax_y - 15), (ax_x + 160, ax_y)]
    for i in range(len(g1_pts)-1):
        frags.append(line(g1_pts[i][0], g1_pts[i][1], g1_pts[i+1][0], g1_pts[i+1][1], color=FIELD, sw=2.2))
    frags.append(text(ax_x + 95, ax_y - 132, "Гаусіан 1: Листя (μ₁=72, ω₁=0.55)", size=11, color=FIELD, bold=True))

    # Draw Gaussian 2: Sky peak
    g2_pts = [(ax_x + 180, ax_y), (ax_x + 210, ax_y - 12), (ax_x + 230, ax_y - 60), (ax_x + 245, ax_y - 95),
              (ax_x + 260, ax_y - 60), (ax_x + 280, ax_y - 12), (ax_x + 310, ax_y)]
    for i in range(len(g2_pts)-1):
        frags.append(line(g2_pts[i][0], g2_pts[i][1], g2_pts[i+1][0], g2_pts[i+1][1], color=NEG, sw=2.2))
    frags.append(text(ax_x + 245, ax_y - 102, "Гаусіан 2: Небо (μ₂=195, ω₂=0.35)", size=11, color=NEG, bold=True))

    # Draw Gaussian 3: Transient object
    g3_pts = [(ax_x + 100, ax_y), (ax_x + 130, ax_y - 10), (ax_x + 165, ax_y - 30), (ax_x + 180, ax_y - 35),
              (ax_x + 195, ax_y - 30), (ax_x + 230, ax_y - 10), (ax_x + 260, ax_y)]
    for i in range(len(g3_pts)-1):
        frags.append(line(g3_pts[i][0], g3_pts[i][1], g3_pts[i+1][0], g3_pts[i+1][1], color=POS, sw=1.8, dash="3,2"))
    frags.append(text(ax_x + 175, ax_y - 42, "Гаусіан 3: Об'єкт (ω₃=0.10)", size=11, color=POS))

    frags.append(text(25 + p1_w/2, top_y + p_h - 15, "Один піксель має 2 рівноправних стани тла (листя + просвіт)", size=11, color=INK))

    # Right Panel: GMM Matching & Sorting logic
    bx2 = 440
    frags.append(rect(bx2, top_y, p2_w, 32, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(bx2 + p2_w/2, top_y + 20, "Ранжування компонент: критерій ω / σ", size=12, bold=True, color=INK))

    frags.append(rect(bx2, top_y + 36, p2_w, p_h - 36, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    tbl_y = top_y + 50
    rows = [
        ("1. Листя", "ω₁=0.55", "σ₁=6", "ω₁/σ₁ = 0.091", "ТЛО (Background)", "#dcfce7", FIELD),
        ("2. Небо", "ω₂=0.35", "σ₂=8", "ω₂/σ₂ = 0.043", "ТЛО (Background)", "#dcfce7", FIELD),
        ("3. Тіло", "ω₃=0.10", "σ₃=20", "ω₃/σ₃ = 0.005", "РУХ (Foreground)", "#fee2e2", POS),
    ]

    for i, (name, w_val, sig_val, score, role, r_fill, r_col) in enumerate(rows):
        ry = tbl_y + i * 50
        frags.append(rect(bx2 + 15, ry, p2_w - 30, 42, fill=r_fill, stroke=r_col, sw=1.2, rx=5))
        frags.append(text(bx2 + 25, ry + 18, name, size=11, color=INK, bold=True, anchor="start"))
        frags.append(text(bx2 + 105, ry + 18, f"{w_val}, {sig_val}", size=11, color=MUTED, anchor="start"))
        frags.append(text(bx2 + 25, ry + 34, score, size=10, color=MUTED, anchor="start"))
        frags.append(text(bx2 + p2_w - 25, ry + 26, role, size=11, color=r_col, bold=True, anchor="end"))

    # Cutoff threshold T explanation
    frags.append(rect(bx2 + 15, tbl_y + 155, p2_w - 30, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(bx2 + p2_w/2, tbl_y + 175, "Поріг сумарної ваги: T_B = 0.75", size=11, color=INK, bold=True))
    frags.append(text(bx2 + p2_w/2, tbl_y + 192, "ω₁ + ω₂ = 0.90 ≥ 0.75  ⇒  перші 2 — ТЛО", size=11, color=FIELD, bold=True))
    frags.append(text(bx2 + p2_w/2, tbl_y + 206, "Третій не вмістився в T_B  ⇒  це РУХ", size=10, color=POS))

    return render(os.path.join(OUT_DIR, "gmm-multimodal-distribution.svg"), w, h, *frags,
                  title="Суміш Ґаусіанів (GMM): моделювання динамічного мультимодального тла")


def fig_morphology_blob_pipeline():
    """Конвеєр очищення бінарної маски: ерозія, дилатація та виділення плям (Blob Analysis)."""
    w, h = 820, 360
    frags = []

    step_w = 170
    step_h = 270
    step_gap = 25
    x0 = 25
    top_y = 50

    steps = [
        ("1. Сира маска", [
            ("Сольовий шум (noise)", 70),
            ("Розриви у силуеті", 110),
            ("Нерівні краї", 150),
            ("Дрібні хибні плями", 190)
        ], "#fee2e2", POS),
        ("2. Ерозія 3×3", [
            ("Видалення шуму", 70),
            ("Зменшення об'єкта", 110),
            ("Відсікання перемичок", 150),
            ("Чисте поле навколо", 190)
        ], "#fef3c7", "#b45309"),
        ("3. Дилатація 5×5", [
            ("Відновлення форми", 70),
            ("Затягування дірок", 110),
            ("Злиття частин", 150),
            ("Суцільний блоб", 190)
        ], "#dbeafe", NEG),
        ("4. Маркування CCL", [
            ("Зв'язні компоненти", 70),
            ("Bounding Box [x,y,w,h]", 110),
            ("Центроїд (x̄, ȳ)", 150),
            ("Фільтр площі > Min", 190)
        ], "#dcfce7", FIELD)
    ]

    for i, (title, items, fill_col, border_col) in enumerate(steps):
        bx = x0 + i * (step_w + step_gap)
        
        # Header rect
        frags.append(rect(bx, top_y, step_w, 28, fill=fill_col, stroke=border_col, sw=1.2, rx=4))
        frags.append(text(bx + step_w / 2, top_y + 18, title, size=11, bold=True, color=border_col))

        # Main box
        frags.append(rect(bx, top_y + 32, step_w, step_h - 32, fill=fill_col, stroke=border_col, sw=1.5, rx=6))

        # Mini visual area
        vy = top_y + 40
        vw = step_w - 20
        vh = 85
        frags.append(rect(bx + 10, vy, vw, vh, fill="#1e293b", stroke=LINE, sw=1, rx=4))

        if i == 0:
            # Noisy raw mask
            frags.append(rect(bx + 35, vy + 15, 60, 50, fill="#ffffff", stroke="#ffffff", sw=1, rx=4))
            frags.append(circle(bx + 55, vy + 35, 6, fill="#1e293b", stroke="#1e293b"))
            frags.append(circle(bx + 75, vy + 45, 5, fill="#1e293b", stroke="#1e293b"))
            frags.append(circle(bx + 20, vy + 20, 2, fill="#ffffff", stroke="#ffffff"))
            frags.append(circle(bx + 25, vy + 65, 3, fill="#ffffff", stroke="#ffffff"))
            frags.append(circle(bx + 115, vy + 30, 2, fill="#ffffff", stroke="#ffffff"))
            frags.append(circle(bx + 125, vy + 60, 2.5, fill="#ffffff", stroke="#ffffff"))
            
        elif i == 1:
            # Eroded mask
            frags.append(rect(bx + 40, vy + 20, 50, 40, fill="#ffffff", stroke="#ffffff", sw=1, rx=3))
            frags.append(circle(bx + 58, vy + 38, 8, fill="#1e293b", stroke="#1e293b"))
            
        elif i == 2:
            # Dilated mask
            frags.append(rect(bx + 32, vy + 12, 66, 56, fill="#ffffff", stroke="#ffffff", sw=1, rx=5))
            
        elif i == 3:
            # Blob labeled with green bounding box and centroid
            frags.append(rect(bx + 32, vy + 12, 66, 56, fill="#22c55e", stroke="#22c55e", sw=1, rx=5))
            frags.append(rect(bx + 28, vy + 8, 74, 64, fill="none", stroke=POS, sw=1.8, rx=2))
            frags.append(circle(bx + 65, vy + 40, 3, fill=POS, stroke=POS))
            frags.append(line(bx + 57, vy + 40, bx + 73, vy + 40, color=POS, sw=1.5))
            frags.append(line(bx + 65, vy + 32, bx + 65, vy + 48, color=POS, sw=1.5))

        # Text bullets inside step box
        ty = vy + vh + 15
        for t_label, offset in [
            (items[0][0], 0),
            (items[1][0], 25),
            (items[2][0], 50),
            (items[3][0], 75),
        ]:
            frags.append(text(bx + 12, ty + offset, "• " + t_label, size=10.5, color=INK, anchor="start"))

        # Arrow to next step
        if i < 3:
            ax1 = bx + step_w + 3
            ax2 = bx + step_w + step_gap - 3
            ay = top_y + step_h / 2
            frags.append(arrow(ax1, ay, ax2, ay, color=INK, sw=1.8))

    return render(os.path.join(OUT_DIR, "morphology-blob-pipeline.svg"), w, h, *frags,
                  title="Конвеєр пост-обробки: морфологічна фільтрація та виділення зв'язних компонент")


def fig_embedded_fixedpoint_simd():
    """Архітектура оптимізованого детектора на ARM Cortex-M / NEON (фіксована кома Q8.8 + SIMD)."""
    w, h = 820, 360
    frags = []

    p1_w = 370
    p2_w = 380
    top_y = 50
    p_h = 280

    # Left Panel: Fixed-point Q8.8
    frags.append(rect(25, top_y, p1_w, 32, fill="#f3e8ff", stroke="#7e22ce", sw=1.2, rx=4))
    frags.append(text(25 + p1_w/2, top_y + 20, "Арифметика Q8.8 на мікроконтролері (uint16_t)", size=12, bold=True, color="#7e22ce"))

    frags.append(rect(25, top_y + 36, p1_w, p_h - 36, fill="#faf5ff", stroke=LINE, sw=1.5, rx=8))

    # Bit layout box for uint16_t
    by = top_y + 50
    frags.append(rect(45, by, 330, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(rect(45, by, 165, 50, fill="#e9d5ff", stroke="#7e22ce", sw=1.2, rx=4))
    frags.append(text(45 + 82, by + 22, "Ціла частина (8 біт)", size=11, color="#7e22ce", bold=True))
    frags.append(text(45 + 82, by + 40, "Яскравість пікселя 0..255", size=10, color=MUTED))
    frags.append(text(45 + 165 + 82, by + 22, "Дробова частина (8 біт)", size=11, color=INK, bold=True))
    frags.append(text(45 + 165 + 82, by + 40, "Накопичувач згладжування 1/256", size=10, color=MUTED))

    # Formula box
    fy = by + 65
    frags.append(rect(45, fy, 330, 85, fill="#ffffff", stroke="#7e22ce", sw=1.2, rx=5))
    frags.append(text(45 + 165, fy + 20, "Оновлення без ділення й float:", size=11, color="#7e22ce", bold=True))
    frags.append(text(45 + 165, fy + 42, "B_q16 += ((I_t << 8) − B_q16) >> SHIFT", size=12, color=INK, bold=True))
    frags.append(text(45 + 165, fy + 65, "При α = 1/16 (SHIFT=4) — лише 1 зсув і 1 віднімання!", size=10.5, color=FIELD, bold=True))

    # Memory budget note
    frags.append(text(25 + p1_w/2, top_y + p_h - 40, "Пам'ять для кадру 320×240 (QVGA):", size=11, color=INK, bold=True))
    frags.append(text(25 + p1_w/2, top_y + p_h - 20, "Тло B (Q8.8) = 150 КБ RAM  (вміщається у SRAM STM32)", size=11, color=FIELD, bold=True))

    # Right Panel: SIMD Register Parallelism
    bx2 = 415
    frags.append(rect(bx2, top_y, p2_w, 32, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(bx2 + p2_w/2, top_y + 20, "SIMD: 4 пікселі за такт (ARM DSP / Cortex-M4/M7)", size=12, bold=True, color=NEG))

    frags.append(rect(bx2, top_y + 36, p2_w, p_h - 36, fill="#eff6ff", stroke=LINE, sw=1.5, rx=8))

    # 32-bit register breakdown
    ry = top_y + 50
    frags.append(text(bx2 + 20, ry + 15, "Регістр R0 (Кадр I_t):", size=11, color=INK, bold=True, anchor="start"))
    for b in range(4):
        frags.append(rect(bx2 + 20 + b * 85, ry + 25, 80, 30, fill="#bfdbfe", stroke=NEG, sw=1.2, rx=3))
        frags.append(text(bx2 + 20 + b * 85 + 40, ry + 44, f"P{b} (8-біт)", size=11, color=NEG, bold=True))

    ry2 = ry + 65
    frags.append(text(bx2 + 20, ry2 + 15, "Регістр R1 (Тло B_t):", size=11, color=INK, bold=True, anchor="start"))
    for b in range(4):
        frags.append(rect(bx2 + 20 + b * 85, ry2 + 25, 80, 30, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
        frags.append(text(bx2 + 20 + b * 85 + 40, ry2 + 44, f"B{b} (8-біт)", size=11, color=FIELD, bold=True))

    # Single instruction box
    ry3 = ry2 + 70
    frags.append(rect(bx2 + 20, ry3, 340, 65, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(bx2 + 190, ry3 + 22, "1 такт процесора: __UQSUB8 / __USUB8", size=12, color=POS, bold=True))
    frags.append(text(bx2 + 190, ry3 + 42, "Паралельне беззнакове насичене віднімання", size=11, color=INK))
    frags.append(text(bx2 + 190, ry3 + 57, "Швидкість: > 120 FPS для QVGA на 64 МГц MCU", size=11, color=FIELD, bold=True))

    return render(os.path.join(OUT_DIR, "embedded-fixedpoint-simd.svg"), w, h, *frags,
                  title="Оптимізована архітектура: Q8.8 фіксована кома та 4-піксельний SIMD на ARM Cortex-M")


def main():
    fig_frame_differencing_defects()
    fig_running_average_adaptation()
    fig_gmm_multimodal_distribution()
    fig_morphology_blob_pipeline()
    fig_embedded_fixedpoint_simd()
    print("All 5 figures generated successfully.")


if __name__ == "__main__":
    main()
