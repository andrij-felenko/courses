# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))

# ── 1. frames-ned-enu-body.svg ──────────────────────────────────────────────
def fig_frames():
    W, H = 920, 420
    p = []

    # Left Column: Навігаційні системи (Світ / Навігація)
    p.append(rect(20, 20, 430, 380, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(235, 48, "Навігаційні системи (World / Navigation)", size=15, color=INK, bold=True))

    # NED Card
    p.append(rect(35, 65, 400, 150, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(50, 90, "NED (North-East-Down)", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(50, 108, "Авіація, морська навігація, PX4, ArduPilot", size=11, color=MUTED, anchor="start"))
    # Axes NED
    # X - North (up-left)
    p.append(arrow(150, 175, 105, 135, color=POS, sw=2.2))
    p.append(text(95, 130, "X (North)", size=11, color=POS, bold=True))
    # Y - East (right)
    p.append(arrow(150, 175, 215, 175, color=FIELD, sw=2.2))
    p.append(text(225, 180, "Y (East)", size=11, color=FIELD, bold=True, anchor="start"))
    # Z - Down (down)
    p.append(arrow(150, 175, 150, 208, color=NEG, sw=2.2))
    p.append(text(155, 208, "Z (Down / +Глибина)", size=10, color=NEG, bold=True, anchor="start"))
    # Feature note
    p.append(text(260, 135, "• Z спрямовано до центру Землі", size=11, color=INK, anchor="start"))
    p.append(text(260, 153, "• Вектор гравітації: g = [0, 0, +g]", size=11, color=INK, anchor="start"))

    # ENU Card
    p.append(rect(35, 230, 400, 155, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(50, 255, "ENU (East-North-Up)", size=13, color=NEG, bold=True, anchor="start"))
    p.append(text(50, 273, "Наземна робототехніка, геодезія, ROS (REP-103)", size=11, color=MUTED, anchor="start"))
    # Axes ENU
    # X - East (right)
    p.append(arrow(150, 345, 215, 345, color=FIELD, sw=2.2))
    p.append(text(225, 350, "X (East)", size=11, color=FIELD, bold=True, anchor="start"))
    # Y - North (up-left)
    p.append(arrow(150, 345, 105, 305, color=POS, sw=2.2))
    p.append(text(95, 300, "Y (North)", size=11, color=POS, bold=True))
    # Z - Up (up)
    p.append(arrow(150, 345, 150, 285, color=NEG, sw=2.2))
    p.append(text(155, 290, "Z (Up / +Висота)", size=10, color=NEG, bold=True, anchor="start"))
    # Feature note
    p.append(text(260, 305, "• Z спрямовано в небо", size=11, color=INK, anchor="start"))
    p.append(text(260, 323, "• Вектор гравітації: g = [0, 0, −g]", size=11, color=INK, anchor="start"))

    # Right Column: Зв'язані з тілом системи (Body Frames)
    p.append(rect(470, 20, 430, 380, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(685, 48, "Зв'язані з тілом системи (Body Frames)", size=15, color=INK, bold=True))

    # FRD Card
    p.append(rect(485, 65, 400, 150, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(500, 90, "FRD (Forward-Right-Down)", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(500, 108, "Базовий стандарт БПЛА / літаків (партнер NED)", size=11, color=MUTED, anchor="start"))
    # Axes FRD
    p.append(arrow(600, 175, 555, 135, color=POS, sw=2.2))
    p.append(text(545, 130, "X (Forward / Ніс)", size=11, color=POS, bold=True))
    p.append(arrow(600, 175, 665, 175, color=FIELD, sw=2.2))
    p.append(text(675, 180, "Y (Right / Праве крило)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(arrow(600, 175, 600, 208, color=NEG, sw=2.2))
    p.append(text(605, 208, "Z (Down / Дно)", size=11, color=NEG, bold=True, anchor="start"))
    # Notes
    p.append(text(710, 135, "• Крен +: праве крило вниз", size=11, color=INK, anchor="start"))
    p.append(text(710, 153, "• Тангаж +: ніс догори", size=11, color=INK, anchor="start"))

    # FLU Card
    p.append(rect(485, 230, 400, 155, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(500, 255, "FLU (Forward-Left-Up)", size=13, color=NEG, bold=True, anchor="start"))
    p.append(text(500, 273, "Базовий стандарт ROS / мобільних роботів (партнер ENU)", size=11, color=MUTED, anchor="start"))
    # Axes FLU
    p.append(arrow(600, 345, 555, 305, color=POS, sw=2.2))
    p.append(text(545, 300, "X (Forward / Ніс)", size=11, color=POS, bold=True))
    p.append(arrow(600, 345, 535, 345, color=FIELD, sw=2.2))
    p.append(text(525, 350, "Y (Left)", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(arrow(600, 345, 600, 285, color=NEG, sw=2.2))
    p.append(text(605, 290, "Z (Up / Дах)", size=11, color=NEG, bold=True, anchor="start"))
    # Notes
    p.append(text(710, 305, "• Крен +: лівий бік вниз", size=11, color=INK, anchor="start"))
    p.append(text(710, 323, "• Тангаж +: ніс униз", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "frames-ned-enu-body.svg"), W, H, *p)


# ── 2. sensor-mounting-misalignment.svg ─────────────────────────────────────
def fig_misalignment():
    W, H = 920, 380
    p = []

    # Section 1: Physical Drone & Misaligned Chip
    p.append(rect(20, 20, 330, 340, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(185, 48, "Фізичний перекіс у конструкції", size=14, color=INK, bold=True))

    # Drone Outline representation
    p.append(circle(185, 160, 65, fill="#e8edf2", stroke=MUTED, sw=1.5))
    p.append(line(120, 160, 250, 160, color=MUTED, sw=2))
    p.append(line(185, 95, 185, 225, color=MUTED, sw=2))
    # Body Frame axes (FRD)
    p.append(arrow(185, 160, 185, 80, color=POS, sw=2.5))
    p.append(text(195, 85, "X_body (Forward)", size=11, color=POS, bold=True, anchor="start"))
    p.append(arrow(185, 160, 265, 160, color=FIELD, sw=2.5))
    p.append(text(265, 175, "Y_body (Right)", size=11, color=FIELD, bold=True, anchor="start"))

    # PCB & Sensor tilted
    # PCB rectangle tilted
    p.append(rect(160, 135, 50, 50, fill="#d5e8d4", stroke="#27ae60", sw=1.5))
    # Chip inside PCB
    p.append(rect(171, 146, 28, 28, fill="#333333", stroke="#111111", sw=1))
    p.append(text(185, 163, "IMU", size=10, color="#ffffff", bold=True))

    # Sensor tilted axes
    p.append(arrow(185, 160, 165, 95, color="#e67e22", sw=2))
    p.append(text(150, 95, "X_sensor", size=11, color="#e67e22", bold=True))
    p.append(arrow(185, 160, 250, 140, color="#8e44ad", sw=2))
    p.append(text(255, 135, "Y_sensor", size=11, color="#8e44ad", bold=True, anchor="start"))

    # Angle arc label
    p.append(text(185, 250, "1. Дискретний поворот (Board: 0°/90°/180°)", size=10, color=INK, bold=True))
    p.append(text(185, 270, "2. Монтажний перекіс паяння (Δθ ≈ 0.5°–2°)", size=10, color=POS))
    p.append(text(185, 290, "3. Неортогональність осей кристала", size=10, color=MUTED))

    # Section 2: Calibration Transformation Pipeline
    p.append(rect(370, 20, 530, 340, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(635, 48, "Конвеєр перетворення: Сенсор → Тіло", size=14, color=INK, bold=True))

    # Pipeline blocks
    # Step 1: Raw Sensor Data
    p.append(rect(390, 80, 140, 55, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(460, 102, "Сирі виміри", size=12, color=INK, bold=True))
    p.append(text(460, 122, "v_raw = [ax, ay, az]", size=10, color=MUTED))

    p.append(arrow(530, 107, 560, 107, color=LINE, sw=1.5))

    # Step 2: Bias & Scale & Non-orthogonality
    p.append(rect(560, 80, 150, 55, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(635, 102, "Калібрування шкали", size=12, color=POS, bold=True))
    p.append(text(635, 122, "v_cal = S · (v_raw − b)", size=10, color=INK))

    p.append(arrow(710, 107, 740, 107, color=LINE, sw=1.5))

    # Step 3: Misalignment Matrix
    p.append(rect(740, 80, 145, 55, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(812, 102, "Матриця перекосу", size=12, color=FIELD, bold=True))
    p.append(text(812, 122, "v_align = R_align · v_cal", size=10, color=INK))

    # Arrow down to Step 4
    p.append(arrow(812, 135, 812, 175, color=LINE, sw=1.5))

    # Step 4: Board Orientation Matrix (discrete 90 deg steps)
    p.append(rect(670, 175, 215, 60, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(777, 198, "Орієнтація плати (Board)", size=12, color=NEG, bold=True))
    p.append(text(777, 218, "v_body = R_board · v_align", size=10, color=INK))

    # Arrow left to Output Body Vector
    p.append(arrow(670, 205, 560, 205, color=LINE, sw=1.5))

    # Result Block
    p.append(rect(390, 175, 170, 60, fill="#e8f4fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(475, 198, "Вектор у системі тіла", size=12, color=NEG, bold=True))
    p.append(text(475, 218, "v_body (FRD / FLU)", size=11, color=INK, bold=True))

    # Mathematical Formula Box below
    p.append(rect(390, 260, 495, 80, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(637, 285, "Підсумкове матричне рівняння вирівнювання:", size=11, color=MUTED))
    p.append(text(637, 312, "v_body = R_board · R_align · S_ortho · (v_raw − b_bias)", size=13, color=INK, bold=True))

    render(os.path.join(OUT, "sensor-mounting-misalignment.svg"), W, H, *p)


# ── 3. gimbal-lock-singularity.svg ──────────────────────────────────────────
def fig_gimbal_lock():
    W, H = 920, 390
    p = []

    # Left: Normal state (3 DoF)
    p.append(rect(20, 20, 430, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(235, 48, "Нормальний стан: Pitch = 0° (3 ступені вільності)", size=13, color=FIELD, bold=True))

    # Concentric Gimbal rings schematic (Pitch = 0)
    # Outer ring: Yaw (Z axis - vertical)
    p.append(ellipse(235, 180, 120, 95, fill="none", stroke=POS, sw=3))
    p.append(line(235, 65, 235, 295, color=POS, sw=1.5, dash="4,4"))
    p.append(text(235, 80, "Вісь Рискання (Yaw, Z)", size=10, color=POS, bold=True))

    # Middle ring: Pitch (Y axis - horizontal)
    p.append(ellipse(235, 180, 95, 75, fill="none", stroke=FIELD, sw=3))
    p.append(line(125, 180, 345, 180, color=FIELD, sw=1.5, dash="4,4"))
    p.append(text(348, 185, "Вісь Тангажу (Pitch, Y)", size=10, color=FIELD, bold=True, anchor="start"))

    # Inner ring: Roll (X axis - depth)
    p.append(ellipse(235, 180, 70, 50, fill="none", stroke=NEG, sw=3))
    p.append(line(175, 135, 295, 225, color=NEG, sw=1.5, dash="4,4"))
    p.append(text(300, 230, "Вісь Крену (Roll, X)", size=10, color=NEG, bold=True, anchor="start"))

    # Status note
    p.append(text(235, 325, "Усі 3 осі взаємно ортогональні.", size=11, color=INK, bold=True))
    p.append(text(235, 345, "Обертання навколо будь-якої осі є незалежним.", size=11, color=MUTED))

    # Right: Gimbal Lock state (Pitch = 90°)
    p.append(rect(470, 20, 430, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(685, 48, "Gimbal Lock: Pitch = +90° (Втрата 1 ступеня)", size=13, color=POS, bold=True))

    # Concentric Gimbal rings schematic (Pitch = +90°)
    # Outer ring: Yaw (Z axis - vertical)
    p.append(ellipse(685, 180, 120, 95, fill="none", stroke=POS, sw=3))
    p.append(line(685, 65, 685, 295, color=POS, sw=2, dash="4,4"))

    # Middle ring: Pitch rotated 90°
    p.append(ellipse(685, 180, 95, 25, fill="none", stroke=FIELD, sw=3))
    p.append(line(575, 180, 795, 180, color=FIELD, sw=1.5, dash="4,4"))
    p.append(text(798, 185, "Pitch повернуто на 90°", size=10, color=FIELD, bold=True, anchor="start"))

    # Inner ring: Roll aligned with Yaw!
    p.append(ellipse(685, 180, 70, 95, fill="none", stroke=NEG, sw=3))
    p.append(line(685, 75, 685, 285, color=NEG, sw=2))

    # Danger callout
    p.append(rect(510, 90, 350, 48, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(685, 110, "Вісь Крену (Roll) лягла на вісь Рискання (Yaw)!", size=11, color=POS, bold=True))
    p.append(text(685, 128, "Неможливо розрізнити крен і курс: (ψ − φ) = const", size=10, color=INK))

    # Status note
    p.append(text(685, 325, "Математична сингулярність: ділення на cos(90°) = 0", size=11, color=POS, bold=True))
    p.append(text(685, 345, "Кінематичні похідні кутів Ейлера прямують до нескінченності!", size=10, color=MUTED))

    render(os.path.join(OUT, "gimbal-lock-singularity.svg"), W, H, *p)


# ── 4. quaternion-rotation-s3.svg ──────────────────────────────────────────
def fig_quaternions():
    W, H = 920, 390
    p = []

    # Left: Geometric representation of Euler axis-angle to quaternion
    p.append(rect(20, 20, 380, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(210, 48, "Теорема Ейлера та Кватерніон", size=14, color=INK, bold=True))

    # 3D Sphere projection representation
    p.append(circle(210, 165, 80, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(ellipse(210, 165, 80, 25, fill="none", stroke=MUTED, sw=1, dash="3,3"))

    # Rotation Axis u (Euler axis)
    p.append(arrow(210, 165, 270, 100, color=POS, sw=2.5))
    p.append(text(280, 95, "Одинична вісь u = [ux, uy, uz]", size=11, color=POS, bold=True, anchor="start"))

    # Rotation angle theta around axis u
    p.append(ellipse(235, 137, 28, 14, fill="none", stroke=FIELD, sw=2))
    p.append(arrow(255, 142, 258, 135, color=FIELD, sw=2))
    p.append(text(268, 145, "Кут θ", size=12, color=FIELD, bold=True, anchor="start"))

    # Vector rotation from v to v'
    p.append(arrow(210, 165, 150, 185, color=NEG, sw=2))
    p.append(text(140, 195, "Вектор v", size=11, color=NEG, bold=True, anchor="end"))
    p.append(arrow(210, 165, 185, 235, color=NEG, sw=2))
    p.append(text(185, 250, "Повернутий v'", size=11, color=NEG, bold=True))

    # Quaternion formula card
    p.append(rect(35, 275, 350, 80, fill=BG, stroke=MUTED, sw=1, rx=6))
    p.append(text(210, 298, "Одиничний кватерніон орієнтації:", size=11, color=MUTED))
    p.append(text(210, 320, "q = [cos(θ/2),  u · sin(θ/2)]", size=13, color=INK, bold=True))
    p.append(text(210, 342, "Умова норми: ||q||² = w² + x² + y² + z² = 1", size=10, color=FIELD))

    # Right: Comparison Matrix of Rotation Representations
    p.append(rect(420, 20, 480, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    p.append(text(660, 48, "Порівняння способів представлення орієнтації", size=14, color=INK, bold=True))

    # Table Header
    y_t = 75
    p.append(rect(435, y_t, 450, 30, fill="#e2e8f0", stroke="none", rx=4))
    p.append(text(500, y_t + 20, "Властивість", size=11, color=INK, bold=True))
    p.append(text(600, y_t + 20, "Кути Ейлера", size=11, color=INK, bold=True))
    p.append(text(710, y_t + 20, "Матриця DCM (3×3)", size=11, color=INK, bold=True))
    p.append(text(830, y_t + 20, "Кватерніон (4D)", size=11, color=INK, bold=True))

    # Row 1: Пам'ять (змінні)
    y_t += 38
    p.append(line(435, y_t + 25, 885, y_t + 25, color="#cbd5e1", sw=1))
    p.append(text(445, y_t + 18, "Пам'ять (floats)", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(600, y_t + 18, "3", size=10, color=INK))
    p.append(text(710, y_t + 18, "9", size=10, color=INK))
    p.append(text(830, y_t + 18, "4 (ідеально)", size=10, color=FIELD, bold=True))

    # Row 2: Сингулярності
    y_t += 35
    p.append(line(435, y_t + 25, 885, y_t + 25, color="#cbd5e1", sw=1))
    p.append(text(445, y_t + 18, "Сингулярності", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(600, y_t + 18, "Є (Gimbal Lock)", size=10, color=POS, bold=True))
    p.append(text(710, y_t + 18, "Немає", size=10, color=FIELD))
    p.append(text(830, y_t + 18, "Немає (гладке S³)", size=10, color=FIELD, bold=True))

    # Row 3: Поворот вектора
    y_t += 35
    p.append(line(435, y_t + 25, 885, y_t + 25, color="#cbd5e1", sw=1))
    p.append(text(445, y_t + 18, "Поворот вектора", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(600, y_t + 18, "Через DCM", size=10, color=MUTED))
    p.append(text(710, y_t + 18, "9 множень", size=10, color=INK))
    p.append(text(830, y_t + 18, "15 множень (швидко)", size=10, color=INK))

    # Row 4: Інтегрування гіроскопа
    y_t += 35
    p.append(line(435, y_t + 25, 885, y_t + 25, color="#cbd5e1", sw=1))
    p.append(text(445, y_t + 18, "Кінематика (інтеграл)", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(600, y_t + 18, "sin/cos (повільно)", size=10, color=POS))
    p.append(text(710, y_t + 18, "R_dot = R · [ω×]", size=10, color=INK))
    p.append(text(830, y_t + 18, "q_dot = 0.5·q ⊗ ω", size=10, color=FIELD, bold=True))

    # Row 5: Ренормалізація
    y_t += 35
    p.append(line(435, y_t + 25, 885, y_t + 25, color="#cbd5e1", sw=1))
    p.append(text(445, y_t + 18, "Ренормалізація", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(600, y_t + 18, "wrap [-π, π]", size=10, color=MUTED))
    p.append(text(710, y_t + 18, "Грам-Шмідт (важко)", size=10, color=POS))
    p.append(text(830, y_t + 18, "q / ||q|| (дуже легко)", size=10, color=FIELD, bold=True))

    # Bottom summary
    p.append(rect(435, 305, 450, 50, fill="#e8f4fd", stroke=NEG, sw=1, rx=6))
    p.append(text(660, 325, "Висновок: Кватерніони — безальтернативний обчислювальний", size=10, color=INK, bold=True))
    p.append(text(660, 342, "рушій оцінки орієнтації для мікроконтролерів (IMU/AHRS).", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "quaternion-rotation-s3.svg"), W, H, *p)


if __name__ == "__main__":
    fig_frames()
    fig_misalignment()
    fig_gimbal_lock()
    fig_quaternions()
    print("Figures generated successfully.")
