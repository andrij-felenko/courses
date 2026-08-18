# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path(d, color=LINE, sw=1.5, fill="none"):
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"/>'

# ── 1. Local Frames: NED vs ENU ─────────────────────────────────────────────
def fig_frames_ned_enu():
    W, H = 840, 360
    p = []
    
    # Outer container
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Локальні системи координат: авіаційна NED та робототехнічна ENU", size=14, color=INK, bold=True))
    
    # Left Card: NED
    p.append(rect(30, 55, 370, 280, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(215, 80, "NED (North — East — Down)", size=13, color=POS, bold=True))
    p.append(text(215, 98, "Авіаційний стандарт (MAVLink, аеронавігація)", size=10.5, color=MUTED))
    
    # Center origin for NED
    cx1, cy1 = 180, 200
    # Tangent plane ground patch
    p.append(path(f"M {cx1-110} {cy1-20} L {cx1+40} {cy1-50} L {cx1+120} {cy1+10} L {cx1-30} {cy1+40} Z", color="#c0c8d0", sw=1, fill="#e8edf2"))
    p.append(text(cx1 - 75, cy1 - 25, "Горизонт (дотична площина)", size=9.5, color=MUTED, italic=True))
    
    # North (X) - pointing forward-left along ground
    p.append(arrow(cx1, cy1, cx1 - 85, cy1 + 28, color=POS, sw=2.5))
    p.append(text(cx1 - 100, cy1 + 35, "+X (North / Північ)", size=11, color=POS, bold=True))
    
    # East (Y) - pointing right along ground
    p.append(arrow(cx1, cy1, cx1 + 95, cy1 + 8, color=FIELD, sw=2.5))
    p.append(text(cx1 + 105, cy1 + 25, "+Y (East / Схід)", size=11, color=FIELD, bold=True))
    
    # Down (Z) - pointing straight down toward Earth center
    p.append(arrow(cx1, cy1, cx1, cy1 + 90, color=NEG, sw=2.5))
    p.append(text(cx1 + 15, cy1 + 85, "+Z (Down / Вниз)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(cx1 + 15, cy1 + 100, "Вздовж вектора гравітації g", size=9.5, color=MUTED, anchor="start"))
    
    # Right Card: ENU
    p.append(rect(440, 55, 370, 280, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(625, 80, "ENU (East — North — Up)", size=13, color=NEG, bold=True))
    p.append(text(625, 98, "Стандарт робототехніки й геодезії (ROS REP 103)", size=10.5, color=MUTED))
    
    # Center origin for ENU
    cx2, cy2 = 590, 230
    # Tangent plane ground patch
    p.append(path(f"M {cx2-110} {cy2-20} L {cx2+40} {cy2-50} L {cx2+120} {cy2+10} L {cx2-30} {cy2+40} Z", color="#c0c8d0", sw=1, fill="#e8edf2"))
    p.append(text(cx2 - 75, cy2 - 25, "Горизонт (дотична площина)", size=9.5, color=MUTED, italic=True))
    
    # East (X) - pointing right along ground
    p.append(arrow(cx2, cy2, cx2 + 95, cy2 + 8, color=FIELD, sw=2.5))
    p.append(text(cx2 + 105, cy2 + 25, "+X (East / Схід)", size=11, color=FIELD, bold=True))
    
    # North (Y) - pointing forward-left along ground
    p.append(arrow(cx2, cy2, cx2 - 85, cy2 + 28, color=POS, sw=2.5))
    p.append(text(cx2 - 100, cy2 + 35, "+Y (North / Північ)", size=11, color=POS, bold=True))
    
    # Up (Z) - pointing straight up away from Earth center
    p.append(arrow(cx2, cy2, cx2, cy2 - 100, color=NEG, sw=2.5))
    p.append(text(cx2 + 15, cy2 - 90, "+Z (Up / Вгору)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(cx2 + 15, cy2 - 75, "Проти вектора гравітації g", size=9.5, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "fig-frames-ned-enu.svg"), W, H, *p)


# ── 2. Body Frames: FRD vs FLU ──────────────────────────────────────────────
def fig_body_frd_flu():
    W, H = 840, 370
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Зв'язані системи координат апарата: FRD (авіація) та FLU (робототехніка)", size=14, color=INK, bold=True))
    
    # Left Box: FRD
    p.append(rect(30, 55, 370, 290, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(215, 78, "Body FRD (Forward — Right — Down)", size=12.5, color=POS, bold=True))
    p.append(text(215, 96, "Авіаційний стандарт (кути Тейта-Браяна: Roll, Pitch, Yaw)", size=10, color=MUTED))
    
    cx1, cy1 = 200, 195
    # Drone schematic in FRD
    p.append(circle(cx1, cy1, 14, fill="#ffffff", stroke=INK, sw=2))
    p.append(line(cx1 - 50, cy1 - 35, cx1 + 50, cy1 + 35, color="#888888", sw=3))
    p.append(line(cx1 - 50, cy1 + 35, cx1 + 50, cy1 - 35, color="#888888", sw=3))
    p.append(circle(cx1 - 50, cy1 - 35, 12, fill="#e8f4fd", stroke="#0288d1", sw=1.5))
    p.append(circle(cx1 + 50, cy1 + 35, 12, fill="#e8f4fd", stroke="#0288d1", sw=1.5))
    p.append(circle(cx1 - 50, cy1 + 35, 12, fill="#feeef0", stroke=POS, sw=1.5))
    p.append(circle(cx1 + 50, cy1 - 35, 12, fill="#feeef0", stroke=POS, sw=1.5))
    
    # Forward (X) - along nose
    p.append(arrow(cx1, cy1, cx1 - 70, cy1 - 45, color=POS, sw=2.5))
    p.append(text(cx1 - 75, cy1 - 55, "+X_b (Forward / Ніс)", size=10.5, color=POS, bold=True))
    
    # Right (Y) - right wing/arm
    p.append(arrow(cx1, cy1, cx1 + 75, cy1 - 35, color=FIELD, sw=2.5))
    p.append(text(cx1 + 85, cy1 - 40, "+Y_b (Right / Праворуч)", size=10.5, color=FIELD, bold=True, anchor="start"))
    
    # Down (Z) - down through belly
    p.append(arrow(cx1, cy1, cx1, cy1 + 80, color=NEG, sw=2.5))
    p.append(text(cx1 + 10, cy1 + 75, "+Z_b (Down / Днище)", size=10.5, color=NEG, bold=True, anchor="start"))
    
    # Rotation conventions note box
    p.append(rect(45, 275, 340, 55, fill="#ffffff", stroke="#d0d7de", rx=4))
    p.append(text(215, 293, "Правило правого гвинта:", size=10, color=INK, bold=True))
    p.append(text(215, 310, "Roll (крен): праве крило вниз (+) | Pitch (тангаж): ніс вгору (+)", size=9.5, color=MUTED))
    p.append(text(215, 323, "Yaw (рискання): поворот за годинниковою стрілкою (+)", size=9.5, color=MUTED))
    
    # Right Box: FLU
    p.append(rect(440, 55, 370, 290, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(625, 78, "Body FLU (Forward — Left — Up)", size=12.5, color=NEG, bold=True))
    p.append(text(625, 96, "Робототехнічний стандарт (ROS REP 103, орієнтація камер)", size=10, color=MUTED))
    
    cx2, cy2 = 610, 215
    # Drone schematic in FLU
    p.append(circle(cx2, cy2, 14, fill="#ffffff", stroke=INK, sw=2))
    p.append(line(cx2 - 50, cy2 - 35, cx2 + 50, cy2 + 35, color="#888888", sw=3))
    p.append(line(cx2 - 50, cy2 + 35, cx2 + 50, cy2 - 35, color="#888888", sw=3))
    p.append(circle(cx2 - 50, cy2 - 35, 12, fill="#feeef0", stroke=POS, sw=1.5))
    p.append(circle(cx2 + 50, cy2 + 35, 12, fill="#feeef0", stroke=POS, sw=1.5))
    p.append(circle(cx2 - 50, cy2 + 35, 12, fill="#e8f4fd", stroke="#0288d1", sw=1.5))
    p.append(circle(cx2 + 50, cy2 - 35, 12, fill="#e8f4fd", stroke="#0288d1", sw=1.5))
    
    # Forward (X) - along nose
    p.append(arrow(cx2, cy2, cx2 - 70, cy2 - 45, color=POS, sw=2.5))
    p.append(text(cx2 - 75, cy2 - 55, "+X_b (Forward / Ніс)", size=10.5, color=POS, bold=True))
    
    # Left (Y) - left wing/arm
    p.append(arrow(cx2, cy2, cx2 - 75, cy2 + 35, color=FIELD, sw=2.5))
    p.append(text(cx2 - 85, cy2 + 50, "+Y_b (Left / Ліворуч)", size=10.5, color=FIELD, bold=True, anchor="end"))
    
    # Up (Z) - up through roof
    p.append(arrow(cx2, cy2, cx2, cy2 - 80, color=NEG, sw=2.5))
    p.append(text(cx2 + 10, cy2 - 70, "+Z_b (Up / Верх)", size=10.5, color=NEG, bold=True, anchor="start"))
    
    # Rotation conventions note box
    p.append(rect(455, 275, 340, 55, fill="#ffffff", stroke="#d0d7de", rx=4))
    p.append(text(625, 293, "Зв'язок осей FRD та FLU:", size=10, color=INK, bold=True))
    p.append(text(625, 310, "X_flu = X_frd", size=9.5, color=MUTED))
    p.append(text(625, 323, "Y_flu = -Y_frd  |  Z_flu = -Z_frd", size=9.5, color=MUTED))
    
    render(os.path.join(OUT, "fig-body-frd-flu.svg"), W, H, *p)


# ── 3. WGS84 Geodetic Altitudes: Ellipsoid vs Geoid vs Terrain ─────────────
def fig_wgs84_altitudes():
    W, H = 840, 360
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Глобальні висоти: WGS84 еліпсоїд, геоїд (AMSL) та рельєф (AGL)", size=14, color=INK, bold=True))
    
    # Left Reference: Earth center and curves
    # Surface 1: WGS84 Ellipsoid (Blue line)
    p.append(path("M 50 280 Q 420 270 790 280", color=NEG, sw=2, fill="none"))
    p.append(text(795, 284, "Еліпсоїд WGS84 (математична модель, h = 0)", size=10, color=NEG, anchor="start", bold=True))
    
    # Surface 2: Geoid / Mean Sea Level EGM96 (Green wavy line)
    p.append(path("M 50 235 Q 250 215 450 245 T 790 220", color=FIELD, sw=2.5, fill="none"))
    p.append(text(795, 224, "Геоїд / Середній рівень моря (AMSL, H = 0)", size=10, color=FIELD, anchor="start", bold=True))
    
    # Surface 3: Terrain / Mountains (Brown/Dark line with fill)
    p.append(path("M 50 310 L 50 210 Q 180 140 280 180 T 480 120 T 650 160 T 790 140 L 790 310 Z", color="#8d6e63", sw=1.5, fill="#efebe9"))
    p.append(text(795, 144, "Фізичний рельєф поверхні Землі (Terrain)", size=10, color="#5d4037", anchor="start", bold=True))
    
    # Aircraft / Drone position
    dx, dy = 480, 75
    p.append(circle(dx, dy, 7, fill=POS, stroke=INK, sw=1.5))
    p.append(text(dx, dy - 15, "БПЛА у польоті", size=11, color=POS, bold=True))
    
    # Vertical plumb line from drone to ellipsoid
    p.append(line(dx, dy, dx, 275, color=INK, sw=1.2, dash="3,3"))
    
    # Altitude 1: AGL (Drone to Terrain)
    p.append(line(dx - 55, dy, dx - 55, 120, color="#d84315", sw=1.8))
    p.append(line(dx - 60, dy, dx - 50, dy, color="#d84315", sw=1.5))
    p.append(line(dx - 60, 120, dx - 50, 120, color="#d84315", sw=1.5))
    p.append(text(dx - 65, (dy + 120) / 2 + 4, "h_AGL (Above Ground Level)", size=10, color="#d84315", bold=True, anchor="end"))
    p.append(text(dx - 65, (dy + 120) / 2 + 17, "Висота над поверхнею", size=9, color=MUTED, anchor="end"))
    
    # Altitude 2: AMSL (Drone to Geoid)
    p.append(line(dx + 25, dy, dx + 25, 245, color=FIELD, sw=1.8))
    p.append(line(dx + 20, dy, dx + 30, dy, color=FIELD, sw=1.5))
    p.append(line(dx + 20, 245, dx + 30, 245, color=FIELD, sw=1.5))
    p.append(text(dx + 35, (dy + 245) / 2 + 4, "H (AMSL / Orthometric)", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(dx + 35, (dy + 245) / 2 + 18, "Висота над рівнем моря", size=9, color=MUTED, anchor="start"))
    
    # Altitude 3: HAE (Drone to Ellipsoid)
    p.append(line(dx + 200, dy, dx + 200, 275, color=NEG, sw=1.8))
    p.append(line(dx + 195, dy, dx + 205, dy, color=NEG, sw=1.5))
    p.append(line(dx + 195, 275, dx + 205, 275, color=NEG, sw=1.5))
    p.append(text(dx + 210, (dy + 275) / 2 + 4, "h (HAE / Ellipsoid Height)", size=10.5, color=NEG, bold=True, anchor="start"))
    p.append(text(dx + 210, (dy + 275) / 2 + 18, "Сира геодезична висота GNSS", size=9, color=MUTED, anchor="start"))
    
    # Geoid Undulation N
    p.append(line(dx - 55, 245, dx - 55, 275, color=INK, sw=1.8))
    p.append(line(dx - 60, 245, dx - 50, 245, color=INK, sw=1.5))
    p.append(line(dx - 60, 275, dx - 50, 275, color=INK, sw=1.5))
    p.append(text(dx - 65, 264, "N (Хвиля геоїда / Undulation)", size=9.5, color=INK, bold=True, anchor="end"))
    
    # Key Formula Box bottom left
    p.append(rect(40, 60, 260, 50, fill="#ffffff", stroke="#d0d7de", rx=4))
    p.append(text(170, 80, "Фундаментальне співвідношення:", size=10, color=MUTED))
    p.append(text(170, 98, "h = H + N  =>  H = h - N", size=12, color=POS, bold=True))
    
    render(os.path.join(OUT, "fig-wgs84-altitudes.svg"), W, H, *p)


# ── 4. Gimbal Lock Singularity ──────────────────────────────────────────────
def fig_gimbal_lock():
    W, H = 840, 360
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Сингулярність кутів Ейлера: втрата ступеня вільності (Gimbal Lock)", size=14, color=INK, bold=True))
    
    # Left Card: Normal 3-DOF Gimbal State
    p.append(rect(30, 55, 370, 280, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(215, 80, "Нормальний стан: 3 незалежні осі", size=12.5, color=FIELD, bold=True))
    p.append(text(215, 98, "Тангаж θ = 0° (ніс по горизонту)", size=10.5, color=MUTED))
    
    cx1, cy1 = 215, 205
    # Outer ring (Yaw - Blue)
    p.append(f'<ellipse cx="{cx1}" cy="{cy1}" rx="80" ry="80" stroke="{NEG}" stroke-width="3" fill="none"/>')
    p.append(text(cx1, cy1 - 90, "Вісь Yaw (Z) [зовнішнє кільце]", size=10, color=NEG, bold=True))
    
    # Middle ring (Pitch - Red, tilted horizontal)
    p.append(f'<ellipse cx="{cx1}" cy="{cy1}" rx="60" ry="25" stroke="{POS}" stroke-width="3" fill="none"/>')
    p.append(text(cx1 + 75, cy1 + 10, "Вісь Pitch (Y)", size=10, color=POS, bold=True, anchor="start"))
    
    # Inner ring (Roll - Green, vertical tilt)
    p.append(f'<ellipse cx="{cx1}" cy="{cy1}" rx="20" ry="45" stroke="{FIELD}" stroke-width="2.5" fill="none"/>')
    p.append(text(cx1, cy1 + 65, "Вісь Roll (X) [внутрішнє]", size=10, color=FIELD, bold=True))
    p.append(circle(cx1, cy1, 5, fill=INK, stroke="none"))
    
    # Right Card: Gimbal Lock State (Pitch = +90 deg)
    p.append(rect(440, 55, 370, 280, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(625, 80, "Шарнірний замок: Pitch θ = +90°", size=12.5, color=POS, bold=True))
    p.append(text(625, 98, "Ніс вертикально вгору — осі Roll і Yaw збіглися!", size=10.5, color=POS))
    
    cx2, cy2 = 625, 205
    # Outer ring (Yaw - Blue)
    p.append(f'<ellipse cx="{cx2}" cy="{cy2}" rx="80" ry="80" stroke="{NEG}" stroke-width="3" fill="none"/>')
    p.append(text(cx2, cy2 - 90, "Вісь Yaw (Z)", size=10, color=NEG, bold=True))
    
    # Middle ring (Pitch - Red, rotated 90 deg into vertical plane)
    p.append(f'<ellipse cx="{cx2}" cy="{cy2}" rx="15" ry="60" stroke="{POS}" stroke-width="3" fill="none"/>')
    p.append(text(cx2 + 30, cy2 - 40, "Pitch повернуто на 90°", size=9.5, color=POS, bold=True, anchor="start"))
    
    # Inner ring (Roll - Green, now in exact same plane as Yaw!)
    p.append(f'<ellipse cx="{cx2}" cy="{cy2}" rx="70" ry="70" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="4,4" fill="none"/>')
    p.append(text(cx2, cy2 + 90, "Вісь Roll (X) лягла у площину Yaw (Z)", size=10, color=POS, bold=True))
    
    # Lock warning box
    p.append(rect(460, 275, 330, 45, fill="#feeef0", stroke=POS, rx=4))
    p.append(text(625, 293, "Втрата 1 ступеня вільності:", size=10, color=POS, bold=True))
    p.append(text(625, 309, "Поворот за креном і рисканням виконує однаковий рух", size=9.5, color=INK))
    
    render(os.path.join(OUT, "fig-gimbal-lock.svg"), W, H, *p)


# ── 5. GPS Scaling: Float32 Loss vs Int32 10^7 Precision ───────────────────
def fig_scaling_fixed_vs_float():
    W, H = 840, 360
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfdfd", stroke="#e0e0e0", sw=1, rx=8))
    p.append(text(W / 2, 34, "Числове представлення координат: небезпека float32 проти int32 10^7", size=14, color=INK, bold=True))
    
    # Top Section: Single Precision Float32 breakdown
    p.append(rect(30, 55, 780, 125, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(420, 78, "Одинарна точність IEEE 754 float (4 байти): лише 24 біти мантиси (~7.2 знаки)", size=12, color=POS, bold=True))
    
    # Float bitfield illustration
    bx, by = 50, 95
    p.append(rect(bx, by, 30, 30, fill="#feeef0", stroke=POS, sw=1.5))
    p.append(text(bx + 15, by + 20, "s", size=11, color=POS, bold=True))
    p.append(text(bx + 15, by + 45, "1 біт", size=9, color=MUTED))
    
    p.append(rect(bx + 35, by, 160, 30, fill="#fff8e1", stroke="#ffa000", sw=1.5))
    p.append(text(bx + 115, by + 20, "Експонента (8 бітів)", size=10.5, color="#b78103", bold=True))
    p.append(text(bx + 115, by + 45, "Діапазон 2^-126 .. 2^127", size=9, color=MUTED))
    
    p.append(rect(bx + 200, by, 300, 30, fill="#e8f4fd", stroke="#0288d1", sw=1.5))
    p.append(text(bx + 350, by + 20, "Мантиса (23 явні + 1 неявний біт = 24 біти)", size=10.5, color="#0288d1", bold=True))
    p.append(text(bx + 350, by + 45, "Точність: 2^-23 ≈ 1.19 × 10^-7", size=9, color=MUTED))
    
    p.append(rect(570, 90, 220, 55, fill="#feeef0", stroke=POS, rx=4))
    p.append(text(680, 108, "Наслідок на широті 50°:", size=10, color=POS, bold=True))
    p.append(text(680, 124, "1° ≈ 111.3 км  =>  похибка ~1.1 метра!", size=10, color=INK, bold=True))
    p.append(text(680, 138, "Непридатно для RTK/точного зависання", size=9.5, color=MUTED))
    
    # Bottom Section: Fixed Point Int32 breakdown
    p.append(rect(30, 195, 780, 140, fill=FILL, stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(420, 218, "Цілочисельне масштабування MAVLink int32_t (10^7 градусів): гарантовані 1.11 см", size=12, color=FIELD, bold=True))
    
    # Int32 field illustration
    bx2, by2 = 50, 235
    p.append(rect(bx2, by2, 495, 30, fill="#e8f8f0", stroke=FIELD, sw=1.5))
    p.append(text(bx2 + 247, by2 + 20, "32-бітне знакове ціле: діапазон від -2 147 483 648 до +2 147 483 647", size=10.5, color=FIELD, bold=True))
    p.append(text(bx2 + 247, by2 + 45, "Довгота ±180° => ±1 800 000 000 одиниць (ідеально вміщується в int32_t)", size=9.5, color=MUTED))
    
    p.append(rect(570, 230, 220, 65, fill="#e8f8f0", stroke=FIELD, rx=4))
    p.append(text(680, 248, "Гарантована роздільність:", size=10, color=FIELD, bold=True))
    p.append(text(680, 265, "Крок: 10^-7 deg = 0.0000001°", size=10, color=INK, bold=True))
    p.append(text(680, 280, "Похибка на місцевості ≈ 1.11 сантиметра!", size=9.5, color=FIELD, bold=True))
    p.append(text(680, 294, "Компактно: лише 4 байти без втрат", size=9.5, color=MUTED))
    
    render(os.path.join(OUT, "fig-scaling-fixed-vs-float.svg"), W, H, *p)


def main():
    fig_frames_ned_enu()
    fig_body_frd_flu()
    fig_wgs84_altitudes()
    fig_gimbal_lock()
    fig_scaling_fixed_vs_float()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
