# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_hard_and_soft_iron_distortion():
    """Тривимірні проекції магнітної сфери: ідеальна, зі зсувом твердого заліза, зі спотворенням м'якого заліза."""
    W, H = 840, 360
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Вплив спотворень твердого й м'якого заліза на сферу вимірювань магнітометра", size=15, bold=True))

    # Панель 1: Ідеальна сфера
    cx1, cy1 = 140, 185
    p.append(rect(20, 55, 240, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(cx1, 80, "1. Ідеальне поле", size=13, bold=True, color=INK))
    p.append(text(cx1, 98, "B_x² + B_y² + B_z² = B₀²", size=11, color=MUTED))

    # Осі
    p.append(line(cx1 - 85, cy1, cx1 + 85, cy1, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(line(cx1, cy1 - 80, cx1, cy1 + 80, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(text(cx1 + 95, cy1 + 4, "Bx", size=10, color=MUTED))
    p.append(text(cx1, cy1 - 88, "By", size=10, color=MUTED))

    # Коло вимірювань
    p.append(circle(cx1, cy1, 65, fill="#e0f2fe", stroke="#0284c7", sw=2.0))
    p.append(circle(cx1, cy1, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(text(cx1 + 18, cy1 + 16, "(0, 0)", size=10, bold=True, color=INK))
    p.append(line(cx1, cy1, cx1 + 46, cy1 - 46, color=POS, sw=1.5))
    p.append(text(cx1 + 30, cy1 - 28, "B₀", size=11, bold=True, color=POS))
    p.append(text(cx1, 305, "Сфера з центром у (0,0,0)", size=11, bold=True, color=FIELD))

    # Панель 2: Тверде залізо (Hard-Iron)
    cx2, cy2 = 420, 185
    p.append(rect(300, 55, 240, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(cx2, 80, "2. Тверде залізо (Hard-Iron)", size=13, bold=True, color=INK))
    p.append(text(cx2, 98, "B_meas = B + V_hard", size=11, color=MUTED))

    # Осі
    p.append(line(cx2 - 85, cy2, cx2 + 85, cy2, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(line(cx2, cy2 - 80, cx2, cy2 + 80, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(circle(cx2, cy2, 2.5, fill=MUTED, stroke=MUTED, sw=1.0))
    p.append(text(cx2 + 95, cy2 + 4, "Bx", size=10, color=MUTED))
    p.append(text(cx2, cy2 - 88, "By", size=10, color=MUTED))

    # Зсунута сфера
    ox, oy = 28, -24
    p.append(arrow(cx2, cy2, cx2 + ox, cy2 + oy, color=POS, sw=1.8))
    p.append(text(cx2 + 10, cy2 - 18, "V_hard", size=10, bold=True, color=POS))
    p.append(circle(cx2 + ox, cy2 + oy, 65, fill="#fee2e2", stroke=POS, sw=2.0))
    p.append(circle(cx2 + ox, cy2 + oy, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(text(cx2 + ox + 18, cy2 + oy + 16, "Центр (Vx, Vy)", size=10, bold=True, color=INK))
    p.append(text(cx2, 305, "Паралельний зсув сфери", size=11, bold=True, color=POS))

    # Панель 3: М'яке залізо + тверде (Soft-Iron + Hard-Iron)
    cx3, cy3 = 700, 185
    p.append(rect(580, 55, 240, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(cx3, 80, "3. М'яке + тверде залізо", size=13, bold=True, color=INK))
    p.append(text(cx3, 98, "B_meas = W_soft · B + V_hard", size=11, color=MUTED))

    # Осі
    p.append(line(cx3 - 85, cy3, cx3 + 85, cy3, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(line(cx3, cy3 - 80, cx3, cy3 + 80, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(circle(cx3, cy3, 2.5, fill=MUTED, stroke=MUTED, sw=1.0))
    p.append(text(cx3 + 95, cy3 + 4, "Bx", size=10, color=MUTED))
    p.append(text(cx3, cy3 - 88, "By", size=10, color=MUTED))

    # Повернутий еліпсоїд
    ecx, ecy = cx3 + ox, cy3 + oy
    ang = math.radians(28)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    rx, ry = 78, 46

    pts = []
    for i in range(73):
        t_ang = math.radians(i * 5)
        px_local = rx * math.cos(t_ang)
        py_local = ry * math.sin(t_ang)
        gx = ecx + px_local * cos_a - py_local * sin_a
        gy = ecy + px_local * sin_a + py_local * cos_a
        pts.append("%.1f,%.1f" % (gx, gy))

    p.append('<polygon points="%s" fill="#fef3c7" stroke="#d97706" stroke-width="2.0"/>' % " ".join(pts))
    p.append(circle(ecx, ecy, 3.5, fill=POS, stroke=POS, sw=1.0))

    # Головні півосі еліпса
    ax1_x = ecx + rx * cos_a
    ax1_y = ecy + rx * sin_a
    ax2_x = ecx - ry * sin_a
    ax2_y = ecy + ry * cos_a
    p.append(line(ecx, ecy, ax1_x, ax1_y, color="#b45309", sw=1.5, dash="2,2"))
    p.append(line(ecx, ecy, ax2_x, ax2_y, color="#b45309", sw=1.5, dash="2,2"))
    p.append(text(ax1_x + 8, ax1_y + 12, "a", size=10, bold=True, color="#b45309"))
    p.append(text(ax2_x - 10, ax2_y - 6, "b", size=10, bold=True, color="#b45309"))

    p.append(text(cx3, 305, "Еліпсоїд: зсув + деформація", size=11, bold=True, color="#b45309"))

    render(os.path.join(OUT, "hard-and-soft-iron-distortion.svg"), W, H, *p)


def fig_ellipsoid_fitting_and_recovery():
    """Схема алгоритму калібрування: від сирої вибірки через вписування еліпсоїда до сфери."""
    W, H = 840, 370
    p = []

    p.append(text(W / 2, 28, "Процес калібрування магнітометра: вписування еліпсоїда та зворотне відновлення сфери", size=15, bold=True))

    # Етап 1: Сирі точки
    p.append(rect(20, 55, 230, 285, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(135, 78, "1. Збір точок (Tumble)", size=12, bold=True, color=INK))
    p.append(text(135, 96, "Хмара сирих відліків {B_k}", size=10, color=MUTED))

    cx1, cy1 = 135, 195
    # Осі
    p.append(line(cx1 - 75, cy1, cx1 + 75, cy1, color="#cbd5e1", sw=1.0, dash="2,2"))
    p.append(line(cx1, cy1 - 75, cx1, cy1 + 75, color="#cbd5e1", sw=1.0, dash="2,2"))

    # Хмара точок навколо зміщеного еліпса
    ox, oy = 20, -15
    ecx1, ecy1 = cx1 + ox, cy1 + oy
    ang = math.radians(30)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    rx, ry = 65, 40

    pts_sample = [
        (0.0, 1.02), (0.15, 0.98), (0.3, 1.05), (0.5, 0.95), (0.7, 1.01),
        (0.85, 0.97), (1.0, 1.03), (1.15, 0.99), (1.3, 1.04), (1.5, 0.96),
        (1.7, 1.02), (1.85, 0.98), (2.0, 1.01), (2.2, 0.97), (2.4, 1.03),
        (2.6, 0.99), (2.8, 1.02), (3.0, 0.98), (3.2, 1.04), (3.4, 0.96),
        (3.6, 1.01), (3.8, 0.97), (4.0, 1.03), (4.2, 0.99), (4.4, 1.02),
        (4.6, 0.98), (4.8, 1.04), (5.0, 0.96), (5.2, 1.01), (5.4, 0.97),
        (5.6, 1.03), (5.8, 0.99), (6.0, 1.02), (6.2, 0.98)
    ]
    for t_val, r_scale in pts_sample:
        px = rx * math.cos(t_val) * r_scale
        py = ry * math.sin(t_val) * r_scale
        gx = ecx1 + px * cos_a - py * sin_a
        gy = ecy1 + px * sin_a + py * cos_a
        p.append(circle(gx, gy, 2.0, fill=NEG, stroke=NEG, sw=0.5))

    p.append(text(135, 310, "Спотворена 3D-хмара", size=11, color=NEG, bold=True))

    # Стрілка переходу 1 -> 2
    p.append(arrow(255, 195, 290, 195, color=LINE, sw=2.0))
    p.append(text(272, 185, "МНК", size=10, bold=True, color=MUTED))

    # Етап 2: Вписування квадрики
    p.append(rect(295, 55, 240, 285, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(415, 78, "2. Оцінка параметрів", size=12, bold=True, color=INK))
    p.append(text(415, 96, "xᵀAx + bᵀx + c = 0", size=10, color=MUTED))

    cx2, cy2 = 415, 195
    p.append(line(cx2 - 75, cy2, cx2 + 75, cy2, color="#cbd5e1", sw=1.0, dash="2,2"))
    p.append(line(cx2, cy2 - 75, cx2, cy2 + 75, color="#cbd5e1", sw=1.0, dash="2,2"))

    ecx2, ecy2 = cx2 + ox, cy2 + oy
    pts2 = []
    for i in range(73):
        t_ang = math.radians(i * 5)
        px_local = rx * math.cos(t_ang)
        py_local = ry * math.sin(t_ang)
        gx = ecx2 + px_local * cos_a - py_local * sin_a
        gy = ecy2 + px_local * sin_a + py_local * cos_a
        pts2.append("%.1f,%.1f" % (gx, gy))

    p.append('<polygon points="%s" fill="#fef3c7" stroke="#d97706" stroke-width="1.8" stroke-dasharray="3,2"/>' % " ".join(pts2))
    p.append(circle(ecx2, ecy2, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(arrow(cx2, cy2, ecx2, ecy2, color=POS, sw=1.5))
    p.append(text(ecx2 + 20, ecy2 + 16, "V_hard", size=10, bold=True, color=POS))
    p.append(text(415, 290, "V_hard = −A⁻¹(b/2)", size=10, bold=True, color=INK))
    p.append(text(415, 310, "T = W_soft⁻¹ (Холецький)", size=10, bold=True, color="#b45309"))

    # Стрілка переходу 2 -> 3
    p.append(arrow(540, 195, 575, 195, color=LINE, sw=2.0))
    p.append(text(558, 185, "Трансф.", size=10, bold=True, color=MUTED))

    # Етап 3: Відновлена сфера
    p.append(rect(580, 55, 240, 285, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(700, 78, "3. Відновлена сфера", size=12, bold=True, color=INK))
    p.append(text(700, 96, "B_cal = T · (B_raw − V_hard)", size=10, color=MUTED))

    cx3, cy3 = 700, 195
    p.append(line(cx3 - 75, cy3, cx3 + 75, cy3, color="#94a3b8", sw=1.0, dash="3,3"))
    p.append(line(cx3, cy3 - 75, cx3, cy3 + 75, color="#94a3b8", sw=1.0, dash="3,3"))

    p.append(circle(cx3, cy3, 55, fill="#e0f2fe", stroke="#0284c7", sw=2.0))
    p.append(circle(cx3, cy3, 3.5, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(text(cx3 + 18, cy3 + 14, "(0, 0)", size=10, bold=True, color=INK))

    for t_val, r_scale in pts_sample:
        r_cal = 55.0 * (1.0 + (r_scale - 1.0) * 0.2)
        gx = cx3 + r_cal * math.cos(t_val)
        gy = cy3 + r_cal * math.sin(t_val)
        p.append(circle(gx, gy, 1.8, fill="#0284c7", stroke="#0284c7", sw=0.5))

    p.append(text(700, 310, "Істинний вектор B_true", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "ellipsoid-fitting-and-recovery.svg"), W, H, *p)


def fig_drone_magnetic_environment_and_mast():
    """Джерела магнітних полів на борту дрона та ефект винесення компаса на щоглу."""
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 28, "Магнітне оточення дрона та закон кубічного спадання завади (1/r³)", size=15, bold=True))

    # Ліва панель: Компонування дрона збоку
    p.append(rect(20, 55, 410, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(225, 78, "Розподіл завад на борту квадрокоптера", size=12, bold=True, color=INK))

    # Корпус дрона
    p.append(rect(155, 230, 140, 45, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=4))
    p.append(text(225, 256, "PDB + LiPo + FC", size=11, bold=True, color=INK))

    # Промені
    p.append(line(70, 248, 155, 248, color="#475569", sw=5.0))
    p.append(line(295, 248, 380, 248, color="#475569", sw=5.0))

    # Мотори
    p.append(rect(55, 225, 25, 35, fill="#94a3b8", stroke=POS, sw=1.5, rx=3))
    p.append(rect(370, 225, 25, 35, fill="#94a3b8", stroke=POS, sw=1.5, rx=3))
    p.append(text(67, 215, "Мотор", size=9, bold=True, color=POS))
    p.append(text(382, 215, "Мотор", size=9, bold=True, color=POS))

    # Силові лінії струму та магнітного поля в центрі
    p.append('<circle cx="225" cy="250" r="65" fill="none" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="4,3"/>')
    p.append('<circle cx="225" cy="250" r="45" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,3"/>')
    p.append(text(225, 290, "Сильні поля: 50–150 А (80–120 мкТл)", size=10, bold=True, color=POS))

    # Внутрішній компас (на польотному контролері)
    p.append(rect(202, 233, 46, 17, fill="#fca5a5", stroke=POS, sw=1.2, rx=2))
    p.append(text(225, 245, "Mag #1", size=9, bold=True, color="#7f1d1d"))

    # Щогла GNSS/Compass
    p.append(line(225, 230, 225, 125, color="#1e293b", sw=3.0))
    p.append(circle(225, 120, 18, fill="#dcfce7", stroke=FIELD, sw=2.0))
    p.append(text(225, 124, "Mag #2", size=9, bold=True, color="#14532d"))
    p.append(text(225, 96, "GNSS + зовнішній компас", size=10, bold=True, color=FIELD))

    # Розмір щогли
    p.append(arrow(260, 230, 260, 125, color=MUTED, sw=1.2))
    p.append(arrow(260, 125, 260, 230, color=MUTED, sw=1.2))
    p.append(text(285, 180, "h ≈ 15 см", size=10, bold=True, color=MUTED))

    # Права панель: Графік спадання напруженості поля від відстані
    p.append(rect(445, 55, 375, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(632, 78, "Напруженість магнітної завади від відстані", size=12, bold=True, color=INK))

    # Осі графіка
    gx0, gy0 = 505, 315
    gw, gh = 285, 205
    p.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.5))
    p.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.5))
    p.append(text(gx0 + gw + 10, gy0 + 4, "r, см", size=10, bold=True, color=INK))
    p.append(text(gx0, gy0 - gh - 8, "B_dist, мкТл", size=10, bold=True, color=INK))

    # Поділки
    for cm in [2, 5, 10, 15, 20]:
        x_pos = gx0 + cm * (gw / 22.0)
        p.append(line(x_pos, gy0, x_pos, gy0 + 4, color=MUTED, sw=1.0))
        p.append(text(x_pos, gy0 + 16, str(cm), size=9, color=MUTED))

    # Рівень природного поля Землі (45 мкТл)
    y_b0 = gy0 - (45.0 / 140.0) * gh
    p.append(line(gx0, y_b0, gx0 + gw, y_b0, color=FIELD, sw=1.2, dash="4,3"))
    p.append(text(gx0 + gw - 45, y_b0 - 6, "B_землі (≈45 мкТл)", size=9, color=FIELD, bold=True))

    # Крива спадання
    curve_pts = []
    for step in range(20, 220):
        r_cm = step / 10.0
        b_val = min(135.0, 1050.0 / (r_cm ** 3) + 60.0 / (r_cm ** 1.5))
        px = gx0 + r_cm * (gw / 22.0)
        py = gy0 - (b_val / 140.0) * gh
        curve_pts.append("%.1f,%.1f" % (px, py))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(curve_pts), POS))

    # Позначення точок на графіку
    p1_x = gx0 + 2.0 * (gw / 22.0)
    p1_y = gy0 - (130.0 / 140.0) * gh
    p.append(circle(p1_x, p1_y, 4.0, fill=POS, stroke=POS, sw=1.0))
    p.append(text(p1_x + 45, p1_y - 4, "На платі (>100 мкТл)", size=9, bold=True, color=POS))

    p2_x = gx0 + 15.0 * (gw / 22.0)
    p2_y = gy0 - (2.0 / 140.0) * gh
    p.append(circle(p2_x, p2_y, 4.0, fill=FIELD, stroke=FIELD, sw=1.0))
    p.append(text(p2_x - 15, p2_y - 14, "На щоглі (<1.5 мкТл)", size=9, bold=True, color=FIELD))

    render(os.path.join(OUT, "drone-magnetic-environment-and-mast.svg"), W, H, *p)


if __name__ == "__main__":
    fig_hard_and_soft_iron_distortion()
    fig_ellipsoid_fitting_and_recovery()
    fig_drone_magnetic_environment_and_mast()
    print("Figures generated successfully in img/")
