# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. Геометрія камери-обскури ───────────────────────────────────────────────
def fig_pinhole_geometry():
    W, H = 880, 460
    p = []
    
    C = (120, 240)          # Оптичний центр C (апертура)
    plane_x = 320           # Площина зображення / сенсор
    P3D = (760, 90)         # 3D точка у просторі P = (X_c, Y_c, Z_c)
    
    # Обчислення точки перетину променя з площиною зображення
    # C=(120,240), P3D=(760,90) -> dx = 640, dy = -150
    # t = (320-120)/(760-120) = 200/640 = 5/16
    py = 240 + (5.0 / 16.0) * (-150) # = 193.125
    p_img = (plane_x, py)
    
    # Головна оптична вісь Z_c
    p.append(line(60, 240, 830, 240, color=MUTED, sw=1.5, dash="6,4"))
    p.append('<polygon points="840,240 830,235 830,245" fill="%s"/>' % MUTED)
    p.append(text(855, 244, "Z_c", size=14, color=MUTED, bold=True, anchor="start"))
    
    # Фрустум (поле зору камери)
    p.append(line(C[0], C[1], plane_x, 80, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(C[0], C[1], plane_x, 400, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(plane_x, 80, 820, 30, color=MUTED, sw=1.0, dash="3,3"))
    p.append(line(plane_x, 400, 820, 450, color=MUTED, sw=1.0, dash="3,3"))
    
    # Площина віртуального зображення (перед центром камери)
    p.append(rect(plane_x - 10, 70, 20, 340, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=3))
    p.append(line(plane_x, 70, plane_x, 410, color="#64748b", sw=2.0))
    p.append(text(plane_x, 52, "Площина сенсора (Z_c = f)", size=13, color=INK, bold=True, anchor="middle"))
    
    # Оптичний промінь від 3D точки до оптичного центру
    p.append(line(C[0], C[1], P3D[0], P3D[1], color=POS, sw=2.0))
    
    # Оптичний центр C (Camera center)
    p.append(circle(C[0], C[1], 6, fill=POS, stroke=INK, sw=1.5))
    p.append(text(C[0], C[1] + 28, "Оптичний центр C (0, 0, 0)", size=13, color=POS, bold=True, anchor="middle"))
    
    # Головна точка c = (c_x, c_y)
    p.append(circle(plane_x, 240, 5, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(plane_x - 18, 258, "c = (c_x, c_y)", size=12, color=FIELD, bold=True, anchor="end"))
    
    # Проектована точка p = (u, v)
    p.append(circle(p_img[0], p_img[1], 5, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(p_img[0] + 16, p_img[1] - 8, "p = (u, v) або (x, y)", size=13, color=NEG, bold=True, anchor="start"))
    
    # Проекція на площину (висота y над оптичною віссю)
    p.append(line(p_img[0], p_img[1], p_img[0], 240, color=NEG, sw=1.5, dash="3,2"))
    p.append(text(plane_x + 12, (p_img[1] + 240) / 2 + 4, "y", size=12, color=NEG, bold=True, anchor="start"))
    
    # 3D точка у просторі
    p.append(circle(P3D[0], P3D[1], 7, fill=FIELD, stroke=INK, sw=1.8))
    p.append(text(P3D[0] + 16, P3D[1] + 5, "P = (X_c, Y_c, Z_c)", size=14, color=FIELD, bold=True, anchor="start"))
    
    # Висота Y_c для 3D точки
    p.append(line(P3D[0], P3D[1], P3D[0], 240, color=FIELD, sw=1.5, dash="3,2"))
    p.append(text(P3D[0] + 12, (P3D[1] + 240) / 2 + 4, "Y_c", size=13, color=FIELD, bold=True, anchor="start"))
    
    # Розмірна лінія фокусної відстані f
    dim_y = 430
    p.append(line(C[0], dim_y, plane_x, dim_y, color=INK, sw=1.5))
    p.append(line(C[0], dim_y - 8, C[0], dim_y + 8, color=INK, sw=1.5))
    p.append(line(plane_x, dim_y - 8, plane_x, dim_y + 8, color=INK, sw=1.5))
    p.append(text((C[0] + plane_x) / 2, dim_y - 8, "Фокусна відстань f", size=13, color=INK, bold=True, anchor="middle"))
    
    # Розмірна лінія глибини Z_c
    dim_z_y = 430
    p.append(line(plane_x, dim_z_y, P3D[0], dim_z_y, color=MUTED, sw=1.3, dash="4,3"))
    p.append(line(C[0], dim_z_y + 18, P3D[0], dim_z_y + 18, color=MUTED, sw=1.5))
    p.append(line(C[0], dim_z_y + 10, C[0], dim_z_y + 26, color=MUTED, sw=1.5))
    p.append(line(P3D[0], dim_z_y + 10, P3D[0], dim_z_y + 26, color=MUTED, sw=1.5))
    p.append(text((C[0] + P3D[0]) / 2, dim_z_y + 36, "Глибина точки Z_c", size=13, color=MUTED, bold=True, anchor="middle"))
    
    # Подібність трикутників (пояснювальний бейдж)
    badge_x, badge_y = 470, 70
    p.append(rect(badge_x, badge_y, 240, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(badge_x + 120, badge_y + 24, "Подібність трикутників:", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(badge_x + 120, badge_y + 46, "x = f · (X_c / Z_c),   y = f · (Y_c / Z_c)", size=12, color=POS, bold=True, anchor="middle"))

    render(os.path.join(OUT, "pinhole-geometry.svg"), W, H, *p)

# ── 2. Ланцюг координатних просторів ──────────────────────────────────────────
def fig_coordinate_frames():
    W, H = 940, 360
    p = []
    
    # 5 блоків перетворень
    boxes = [
        {"x": 20, "y": 90, "w": 150, "h": 170, "title": "1. Світ (World)", "sub": "X_w, Y_w, Z_w\n(метри/мм)\n\nГлобальна сцена\nабо калібрувальна\nдошка", "col": "#0f766e"},
        {"x": 210, "y": 90, "w": 150, "h": 170, "title": "2. Камера (Camera)", "sub": "X_c, Y_c, Z_c\n(метри/мм)\n\nПочаток у центрі\nоб'єктива C", "col": "#2563eb"},
        {"x": 400, "y": 90, "w": 150, "h": 170, "title": "3. Нормовані", "sub": "x = X_c / Z_c\ny = Y_c / Z_c\n(безрозмірні)\n\nПроекція на\nідеальну площину", "col": "#7c3aed"},
        {"x": 590, "y": 90, "w": 150, "h": 170, "title": "4. З дисторсією", "sub": "x_d, y_d\n(безрозмірні)\n\nСпотворення\nлінзи (радіальні\nй тангенційні)", "col": "#c0392b"},
        {"x": 780, "y": 90, "w": 140, "h": 170, "title": "5. Сенсор (Пікселі)", "sub": "u, v\n(пікселі)\n\nДискретна матриця\nкадру W × H", "col": "#27ae60"}
    ]
    
    for b in boxes:
        p.append(rect(b["x"], b["y"], b["w"], b["h"], fill="#f8fafc", stroke=b["col"], sw=2.0, rx=8))
        p.append(rect(b["x"], b["y"], b["w"], 34, fill=b["col"], stroke=b["col"], sw=1.0, rx=6))
        p.append(text(b["x"] + b["w"]/2, b["y"] + 22, b["title"], size=12, color="#ffffff", bold=True, anchor="middle"))
        lines = b["sub"].split("\n")
        cur_y = b["y"] + 54
        for ln in lines:
            if not ln:
                cur_y += 6
                continue
            is_coord = any(k in ln for k in ["X_", "Y_", "Z_", "u,", "x =", "y =", "x_d"])
            sz = 12 if is_coord else 11
            col = INK if not is_coord else b["col"]
            p.append(text(b["x"] + b["w"]/2, cur_y, ln, size=sz, color=col, bold=is_coord, anchor="middle"))
            cur_y += 16

    # Стрілки та підписи перетворень над ними
    arrows = [
        {"x1": 170, "x2": 210, "label": "[R | t]", "sub": "Зовнішні\nпараметри"},
        {"x1": 360, "x2": 400, "label": "1 / Z_c", "sub": "Перспективне\nділення"},
        {"x1": 550, "x2": 590, "label": "D(k, p)", "sub": "Модель\nБрауна"},
        {"x1": 740, "x2": 780, "label": "Матриця K", "sub": "f_x, f_y,\nc_x, c_y"}
    ]
    
    for a in arrows:
        mid_x = (a["x1"] + a["x2"]) / 2
        p.append(line(a["x1"], 175, a["x2"] - 6, 175, color=INK, sw=2.0))
        p.append('<polygon points="%d,175 %d,170 %d,180" fill="%s"/>' % (a["x2"], a["x2"] - 8, a["x2"] - 8, INK))
        p.append(text(mid_x, 50, a["label"], size=13, color=POS, bold=True, anchor="middle"))
        sub_lines = a["sub"].split("\n")
        for i, sl in enumerate(sub_lines):
            p.append(text(mid_x, 285 + i * 16, sl, size=11, color=MUTED, bold=False, anchor="middle"))

    render(os.path.join(OUT, "coordinate-frames.svg"), W, H, *p)

# ── 3. Типи оптичної дисторсії ────────────────────────────────────────────────
def fig_lens_distortion_types():
    W, H = 900, 370
    p = []
    
    panels = [
        {"cx": 160, "cy": 180, "title": "Ідеальна сітка", "sub": "k_1 = 0, k_2 = 0", "desc": "Прямі лінії лишаються прямими", "mode": "none"},
        {"cx": 450, "cy": 180, "title": "Бочкоподібна (Barrel)", "sub": "k_1 < 0", "desc": "Ширококутні об'єктиви (Fish-eye)", "mode": "barrel"},
        {"cx": 740, "cy": 180, "title": "Подушкоподібна (Pincushion)", "sub": "k_1 > 0", "desc": "Телеоб'єктиви / зум", "mode": "pincushion"}
    ]
    
    grid_size = 180
    half = grid_size / 2
    steps = 6
    
    for pan in panels:
        cx, cy = pan["cx"], pan["cy"]
        
        p.append(rect(cx - half - 20, 20, grid_size + 40, 330, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=8))
        p.append(text(cx, 50, pan["title"], size=14, color=INK, bold=True, anchor="middle"))
        p.append(text(cx, 72, pan["sub"], size=12, color=POS if pan["mode"] != "none" else MUTED, bold=True, anchor="middle"))
        p.append(text(cx, 330, pan["desc"], size=11, color=MUTED, bold=False, anchor="middle"))
        
        pts = []
        for j in range(steps + 1):
            row = []
            for i in range(steps + 1):
                nx = (i - steps / 2.0) / (steps / 2.0)
                ny = (j - steps / 2.0) / (steps / 2.0)
                r2 = nx * nx + ny * ny
                
                if pan["mode"] == "barrel":
                    factor = 1.0 - 0.25 * r2
                elif pan["mode"] == "pincushion":
                    factor = 1.0 + 0.25 * r2
                else:
                    factor = 1.0
                
                px_val = cx + (nx * factor) * half
                py_val = cy + (ny * factor) * half
                row.append((px_val, py_val))
            pts.append(row)
            
        for j in range(steps + 1):
            d_path = ["M %.1f %.1f" % (pts[j][0][0], pts[j][0][1])]
            for i in range(1, steps + 1):
                d_path.append("L %.1f %.1f" % (pts[j][i][0], pts[j][i][1]))
            col = "#0284c7" if pan["mode"] == "none" else (POS if pan["mode"] == "barrel" else FIELD)
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(d_path), col))
            
        for i in range(steps + 1):
            d_path = ["M %.1f %.1f" % (pts[0][i][0], pts[0][i][1])]
            for j in range(1, steps + 1):
                d_path.append("L %.1f %.1f" % (pts[j][i][0], pts[j][i][1]))
            col = "#0284c7" if pan["mode"] == "none" else (POS if pan["mode"] == "barrel" else FIELD)
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(d_path), col))
            
        p.append(circle(cx, cy, 3.5, fill=INK, stroke=BG, sw=1.0))

    render(os.path.join(OUT, "lens-distortion-types.svg"), W, H, *p)

# ── 4. Пайплайн калібрування Чжана ─────────────────────────────────────────────
def fig_zhang_calibration_pipeline():
    W, H = 920, 440
    p = []
    
    # Блок 1: Зйомка калібрувальної дошки у різних позах
    p.append(rect(20, 30, 240, 380, fill="#f8fafc", stroke="#0f766e", sw=2.0, rx=8))
    p.append(rect(20, 30, 240, 34, fill="#0f766e", stroke="#0f766e", sw=1.0, rx=6))
    p.append(text(140, 52, "1. Зйомка плоского шаблону", size=13, color="#ffffff", bold=True, anchor="middle"))
    
    p.append(text(140, 84, "Шахівниця Z_w = 0 у N ракурсах", size=11, color=MUTED, bold=False, anchor="middle"))
    
    # Дошка 1
    p.append(rect(60, 100, 160, 75, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    for r_idx in range(3):
        for c_idx in range(6):
            if (r_idx + c_idx) % 2 == 1:
                p.append(rect(60 + c_idx * 26.6, 100 + r_idx * 25, 26.6, 25, fill="#334155", stroke="none"))
    p.append(text(140, 190, "Кадр 1: фронтальний", size=11, color=INK, bold=True, anchor="middle"))
    
    # Дошка 2 (нахилена)
    poly2 = [(65, 220), (210, 205), (200, 280), (75, 290)]
    poly_pts = " ".join("%.1f,%.1f" % pt for pt in poly2)
    p.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % (poly_pts, INK))
    p.append(text(140, 310, "Кадр 2: нахил за віссю X/Y", size=11, color=INK, bold=True, anchor="middle"))
    
    p.append(text(140, 350, "Мінімум N ≥ 3 ракурсів", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text(140, 370, "(рекомендовано 15–25)", size=11, color=MUTED, bold=False, anchor="middle"))
    
    # Стрілка 1 -> 2
    p.append(line(260, 220, 300, 220, color=INK, sw=2.0))
    p.append('<polygon points="300,220 292,215 292,225" fill="%s"/>' % INK)
    
    # Блок 2: Оцінка гомографій H_i
    p.append(rect(310, 80, 240, 280, fill="#f8fafc", stroke="#2563eb", sw=2.0, rx=8))
    p.append(rect(310, 80, 240, 34, fill="#2563eb", stroke="#2563eb", sw=1.0, rx=6))
    p.append(text(430, 102, "2. Гомографії H_i", size=13, color="#ffffff", bold=True, anchor="middle"))
    
    p.append(text(430, 140, "Для кожного кадру i:", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(430, 165, "s · m = H_i · M", size=13, color="#2563eb", bold=True, anchor="middle"))
    p.append(text(430, 195, "де H_i = K [r_1  r_2  t]", size=12, color=INK, bold=False, anchor="middle"))
    p.append(text(430, 230, "Оцінка через DLT + SVD", size=11, color=MUTED, bold=False, anchor="middle"))
    p.append(text(430, 255, "за знайденими кутами клітинок", size=11, color=MUTED, bold=False, anchor="middle"))
    p.append(rect(330, 280, 200, 60, fill="#eff6ff", stroke="#bfdbfe", sw=1.2, rx=4))
    p.append(text(430, 302, "Кожен кадр дає 2 рівняння", size=11, color="#1e40af", bold=True, anchor="middle"))
    p.append(text(430, 324, "на внутрішню матрицю B", size=11, color="#1e40af", bold=True, anchor="middle"))
    
    # Стрілка 2 -> 3
    p.append(line(550, 220, 590, 220, color=INK, sw=2.0))
    p.append('<polygon points="590,220 582,215 582,225" fill="%s"/>' % INK)
    
    # Блок 3: Закрита аналітична ініціалізація та нелінійна оптимізація
    p.append(rect(600, 30, 300, 380, fill="#f8fafc", stroke="#7c3aed", sw=2.0, rx=8))
    p.append(rect(600, 30, 300, 34, fill="#7c3aed", stroke="#7c3aed", sw=1.0, rx=6))
    p.append(text(750, 52, "3. Обчислення параметрів", size=13, color="#ffffff", bold=True, anchor="middle"))
    
    p.append(rect(620, 80, 260, 115, fill="#ffffff", stroke="#ddd6fe", sw=1.5, rx=6))
    p.append(text(750, 102, "Лінійний розв'язок (SVD):", size=12, color="#7c3aed", bold=True, anchor="middle"))
    p.append(text(750, 126, "V · b = 0  ⇒  B = K^(-T) K^(-1)", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(750, 150, "Аналітичне вилучення:", size=11, color=MUTED, bold=False, anchor="middle"))
    p.append(text(750, 172, "f_x, f_y, c_x, c_y, s та (R_i, t_i)", size=12, color=POS, bold=True, anchor="middle"))
    
    p.append(line(750, 205, 750, 225, color=INK, sw=1.5))
    p.append('<polygon points="750,225 745,217 755,217" fill="%s"/>' % INK)
    
    p.append(rect(620, 235, 260, 155, fill="#fdf4ff", stroke="#f5d0fe", sw=1.5, rx=6))
    p.append(text(750, 258, "Нелінійне уточнення (LM):", size=12, color="#c026d3", bold=True, anchor="middle"))
    p.append(text(750, 282, "Мінімізація перепроекції:", size=11, color=INK, bold=False, anchor="middle"))
    p.append(text(750, 308, "min Σ || m_ij - π(K, D, R_i, t_i, M_j) ||²", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(750, 335, "Оцінка дисторсії: k_1, k_2, p_1, p_2", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text(750, 362, "Субпіксельна точність (0.1–0.3 px)", size=11, color=MUTED, bold=False, anchor="middle"))

    render(os.path.join(OUT, "zhang-calibration-pipeline.svg"), W, H, *p)

# ── 5. Forward vs Inverse Mapping & LUT Remap ─────────────────────────────────
def fig_undistort_lut_mesh():
    W, H = 900, 370
    p = []
    
    # Ліва панель: Пряме відображення
    p.append(rect(20, 20, 410, 330, fill="#f8fafc", stroke="#fca5a5", sw=1.8, rx=8))
    p.append(rect(20, 20, 410, 34, fill="#fee2e2", stroke="#fca5a5", sw=1.0, rx=6))
    p.append(text(225, 42, "Пряме відображення (Forward Mapping)", size=13, color="#991b1b", bold=True, anchor="middle"))
    
    p.append(text(225, 75, "Сирий піксель (u_d, v_d) → Новий (u', v')", size=12, color=INK, bold=True, anchor="middle"))
    
    p.append(rect(60, 100, 130, 130, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(125, 120, "Сирий кадр", size=11, color=MUTED, bold=True, anchor="middle"))
    for r in range(4):
        for c in range(4):
            p.append(circle(85 + c * 26, 145 + r * 22, 3, fill="#2563eb", stroke="none"))
            
    p.append(line(200, 165, 240, 165, color=POS, sw=2.0))
    p.append('<polygon points="240,165 232,160 232,170" fill="%s"/>' % POS)
    p.append(text(220, 155, "x_d → x", size=10, color=POS, bold=True, anchor="middle"))
    
    p.append(rect(250, 100, 150, 130, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(325, 120, "Ректифікований", size=11, color=MUTED, bold=True, anchor="middle"))
    dist_pts = [
        (275, 140), (305, 142), (340, 143), (375, 140),
        (270, 165), (380, 165),
        (274, 190), (310, 188), (345, 187), (376, 190)
    ]
    for pt in dist_pts:
        p.append(circle(pt[0], pt[1], 3, fill=POS, stroke="none"))
    p.append(text(325, 170, "ДІРКА (?)", size=10, color="#dc2626", bold=True, anchor="middle"))
    
    p.append(text(225, 260, "✖ Потребує чисельної інверсії моделі", size=11, color="#b91c1c", bold=True, anchor="middle"))
    p.append(text(225, 285, "✖ Залишає порожні пікселі (дірки)", size=11, color="#b91c1c", bold=True, anchor="middle"))
    p.append(text(225, 310, "✖ Непридатне для виправлення всього кадру", size=11, color="#b91c1c", bold=True, anchor="middle"))
    
    # Права панель: Зворотне відображення + LUT
    p.append(rect(470, 20, 410, 330, fill="#f8fafc", stroke="#86efac", sw=1.8, rx=8))
    p.append(rect(470, 20, 410, 34, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=6))
    p.append(text(675, 42, "Зворотне відображення (Inverse Remap + LUT)", size=13, color="#166534", bold=True, anchor="middle"))
    
    p.append(text(675, 75, "Для кожного цільового (u', v') шукаємо у сирому", size=12, color=INK, bold=True, anchor="middle"))
    
    p.append(rect(500, 100, 140, 130, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(570, 120, "Цільовий кадр", size=11, color=MUTED, bold=True, anchor="middle"))
    for r in range(4):
        for c in range(4):
            col = POS if (r==1 and c==2) else "#16a34a"
            p.append(circle(530 + c * 26, 145 + r * 22, 3, fill=col, stroke="none"))
    p.append(text(582, 160, "(u', v')", size=10, color=POS, bold=True, anchor="start"))
    
    p.append(line(650, 165, 690, 165, color=FIELD, sw=2.0))
    p.append('<polygon points="690,165 682,160 682,170" fill="%s"/>' % FIELD)
    p.append(text(670, 155, "x → x_d", size=10, color=FIELD, bold=True, anchor="middle"))
    
    p.append(rect(700, 100, 150, 130, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(775, 120, "Сирий вхідний кадр", size=11, color=MUTED, bold=True, anchor="middle"))
    p.append(rect(735, 145, 50, 50, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=2))
    p.append(circle(745, 155, 3, fill=MUTED, stroke="none"))
    p.append(circle(775, 155, 3, fill=MUTED, stroke="none"))
    p.append(circle(745, 185, 3, fill=MUTED, stroke="none"))
    p.append(circle(775, 185, 3, fill=MUTED, stroke="none"))
    p.append(circle(762, 168, 4, fill=POS, stroke=INK, sw=1.0))
    p.append(text(775, 215, "Білінійна інтерполяція", size=10, color="#15803d", bold=True, anchor="middle"))
    
    p.append(text(675, 260, "✔ Прямий аналітичний розрахунок формули Брауна", size=11, color="#15803d", bold=True, anchor="middle"))
    p.append(text(675, 285, "✔ Карта Remap LUT рахується один раз", size=11, color="#15803d", bold=True, anchor="middle"))
    p.append(text(675, 310, "✔ 100% покриття пікселів без дірок і артефактів", size=11, color="#15803d", bold=True, anchor="middle"))

    render(os.path.join(OUT, "undistort-lut-mesh.svg"), W, H, *p)

if __name__ == "__main__":
    fig_pinhole_geometry()
    fig_coordinate_frames()
    fig_lens_distortion_types()
    fig_zhang_calibration_pipeline()
    fig_undistort_lut_mesh()
    print("5 figures generated in img/")
