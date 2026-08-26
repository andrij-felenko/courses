# -*- coding: utf-8 -*-
"""Figures for «Платформа їде до точки й повертається».
Import svgkit from scripts/ (do not copy it). Output to ./img/.
Run:  python figs.py    then  python ../../../../scripts/svgcheck.py img
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None, n=90):
    """Polyline arc around (cx,cy), radius r, angles a0..a1 (radians, SVG y-down)."""
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append('%.1f,%.1f' % (cx + r * math.cos(a), cy + r * math.sin(a)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (' '.join(pts), color, sw, d))


def dashed_circle(cx, cy, r, fill='none', stroke=LINE, sw=1.5, dash='4,4'):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))


def dashed_rect(x, y, w, h, fill='none', stroke=LINE, sw=1.5, rx=0, dash='4,4'):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' % (x, y, w, h, rx, fill, stroke, sw, dash))


# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — Pure Pursuit Geometry on Differential Platform
# ════════════════════════════════════════════════════════════════════════════
def fig_pure_pursuit_geometry():
    W, H = 720, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Robot pose (lower left)
    rx, ry = 180, 360
    theta_deg = -30  # facing up-right
    theta = math.radians(theta_deg)

    # Waypoint (target)
    gx, gy = 540, 140

    # Lookahead distance L_d
    dx = gx - rx
    dy = gy - ry
    L_d = math.hypot(dx, dy)
    angle_to_goal = math.atan2(dy, dx)
    alpha = angle_to_goal - theta  # heading error

    # World axes at bottom-left corner
    f.append(arrow(40, 440, 110, 440, color=MUTED, sw=1.5))
    f.append(arrow(40, 440, 40, 370, color=MUTED, sw=1.5))
    f.append(text(120, 444, 'X', 12, MUTED, 'start', bold=True))
    f.append(text(40, 360, 'Y', 12, MUTED, 'middle', bold=True))

    # Radius of curvature R = L_d / (2 * sin(alpha))
    sin_alpha = math.sin(alpha)
    R = L_d / (2.0 * sin_alpha) if abs(sin_alpha) > 1e-4 else 1e5

    # Center of curvature ICC (perpendicular to robot heading, to the left)
    perp_x = math.sin(theta)
    perp_y = -math.cos(theta)
    icc_x = rx + R * perp_x
    icc_y = ry + R * perp_y

    # Draw circular arc from robot to waypoint
    a_start = math.atan2(ry - icc_y, rx - icc_x)
    a_end = math.atan2(gy - icc_y, gx - icc_x)
    if a_start < a_end:
        a_start += 2 * math.pi
    f.append(arc_path(icc_x, icc_y, abs(R), a_start, a_end, POS, sw=2.5, dash='6,4'))

    # Lookahead chord line (robot -> goal)
    f.append(line(rx, ry, gx, gy, color=FIELD, sw=2.0, dash='4,3'))

    # Line of sight extension (heading vector)
    hx = math.cos(theta)
    hy = math.sin(theta)
    f.append(arrow(rx, ry, rx + 140 * hx, ry + 140 * hy, color=INK, sw=2.0))
    f.append(text(rx + 155 * hx, ry + 155 * hy, 'Курс θ', 12, INK, 'start', bold=True))

    # Heading error angle alpha arc
    f.append(arc_path(rx, ry, 55, theta, angle_to_goal, FIELD, sw=1.8))
    mid_a = (theta + angle_to_goal) / 2
    f.append(text(rx + 72 * math.cos(mid_a), ry + 72 * math.sin(mid_a) + 4, 'α', 13, FIELD, 'middle', bold=True))

    # ICC point and radius lines
    f.append(circle(icc_x, icc_y, 4.5, fill=INK, stroke=BG, sw=1.5))
    f.append(line(icc_x, icc_y, rx, ry, color=MUTED, sw=1.3, dash='3,3'))
    f.append(line(icc_x, icc_y, gx, gy, color=MUTED, sw=1.3, dash='3,3'))

    # Radius label R
    f.append(text((icc_x + rx) / 2 - 14, (icc_y + ry) / 2, 'R', 12, MUTED, 'middle', bold=True))

    # ICC label box
    b_icc, _, _ = textbox(icc_x + 56, icc_y + 16, 'ICC\n(центр дуги)', 11, pad=5, fill='#ffffff', stroke=MUTED)
    f.append(b_icc)

    # Robot body (oriented along heading)
    body_l, body_w = 64, 44
    ux, uy = -hy, hx  # lateral vector (perp to heading)
    corners = []
    for sgnf, sgns in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        px = rx + sgnf * (body_l / 2) * hx + sgns * (body_w / 2) * ux
        py = ry + sgnf * (body_l / 2) * hy + sgns * (body_w / 2) * uy
        corners.append('%.1f,%.1f' % (px, py))
    f.append('<polygon points="%s" fill="#e8f0fe" stroke="%s" stroke-width="2"/>' % (' '.join(corners), INK))

    # Wheels as thick bars
    for side, col in ((1, POS), (-1, NEG)):
        wx = rx + side * (body_w / 2) * ux
        wy = ry + side * (body_w / 2) * uy
        f.append(line(wx - 14 * hx, wy - 14 * hy, wx + 14 * hx, wy + 14 * hy, color=col, sw=5.5))

    # Robot center dot
    f.append(circle(rx, ry, 3.5, fill=INK, stroke=BG, sw=1.0))
    f.append(text(rx - 28, ry + 24, 'Поза (x, y, θ)', 11, INK, 'middle', bold=True))

    # Target Waypoint dot and label
    f.append(circle(gx, gy, 7, fill=FIELD, stroke=BG, sw=1.5))
    f.append(dashed_circle(gx, gy, 18, fill='none', stroke=FIELD, sw=1.2, dash='3,3'))
    b_wp, _, _ = textbox(gx + 78, gy - 12, 'Цільова точка\n(x_goal, y_goal)', 11, pad=6, fill='#eafaf1', stroke=FIELD)
    f.append(b_wp)

    # Lookahead distance L_d label
    mid_lx = (rx + gx) / 2
    mid_ly = (ry + gy) / 2
    b_ld, _, _ = textbox(mid_lx - 20, mid_ly - 22, 'L_d (Lookahead)', 11, pad=4, fill='#ffffff', stroke=FIELD)
    f.append(b_ld)

    # Formula explanatory panel (top-left)
    f.append(fitbox(20, 20, 290, 84,
                    'Кривина Pure Pursuit:\nκ = 2·sin(α) / L_d\nКутова швидкість: ω = v·κ',
                    size=12, pad=8, fill='#f8fafc', stroke=LINE))

    render(os.path.join(IMG, 'nav-geometry-pure-pursuit.svg'), W, H, *f,
           title='Геометрія Pure Pursuit для диференціальної платформи')


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — Navigation Drift & IMU Heading Fusion
# ════════════════════════════════════════════════════════════════════════════
def fig_dead_reckoning_drift():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Start point
    sx, sy = 80, 240
    # Target point
    tx, ty = 640, 240

    # Ideal nominal path (straight line)
    f.append(line(sx, sy, tx, ty, color=MUTED, sw=1.6, dash='6,4'))
    f.append(text((sx + tx) / 2, sy - 14, 'Ідеальна пряма траєкторія (5.0 м)', 11, MUTED, 'middle', italic=True))

    # Error cone (drift region)
    drift_top_y = 70
    drift_bot_y = 390
    cone_pts = ['%.1f,%.1f' % (sx, sy), '%.1f,%.1f' % (tx, drift_top_y), '%.1f,%.1f' % (tx, drift_bot_y)]
    f.append('<polygon points="%s" fill="#fff2f0" stroke="%s" stroke-width="1.0" stroke-dasharray="3,3"/>'
             % (' '.join(cone_pts), POS))

    # Uncorrected odometry trajectory (diverging arc)
    pts_raw = []
    for i in range(50):
        t = i / 49.0
        x = sx + t * (tx - sx)
        y = sy - 150.0 * (t ** 1.7)
        pts_raw.append('%.1f,%.1f' % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (' '.join(pts_raw), POS))

    # End position of raw odometry
    raw_end_x = float(pts_raw[-1].split(',')[0])
    raw_end_y = float(pts_raw[-1].split(',')[1])
    f.append(circle(raw_end_x, raw_end_y, 5, fill=POS, stroke=BG, sw=1.5))
    b_raw, _, _ = textbox(raw_end_x - 30, raw_end_y - 28, 'Лише енкодери:\nпромах 0.85 м', 11, pad=5, fill='#fff', stroke=POS)
    f.append(b_raw)

    # IMU-fused trajectory (tight straight line with minimal lateral noise)
    pts_fused = []
    for i in range(50):
        t = i / 49.0
        x = sx + t * (tx - sx)
        y = sy + 8.0 * math.sin(t * math.pi * 3) - 12.0 * t
        pts_fused.append('%.1f,%.1f' % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (' '.join(pts_fused), FIELD))

    # End position of fused odometry
    fused_end_x = float(pts_fused[-1].split(',')[0])
    fused_end_y = float(pts_fused[-1].split(',')[1])
    f.append(circle(fused_end_x, fused_end_y, 5, fill=FIELD, stroke=BG, sw=1.5))
    b_fused, _, _ = textbox(fused_end_x - 30, fused_end_y + 32, 'Енкодери + Гіроскоп:\nточність 0.04 м', 11, pad=5, fill='#fff', stroke=FIELD)
    f.append(b_fused)

    # Start and Goal markers
    f.append(circle(sx, sy, 6, fill=INK, stroke=BG, sw=1.5))
    f.append(text(sx, sy + 24, 'Старт (0,0)', 12, INK, 'middle', bold=True))

    f.append(circle(tx, ty, 6, fill=FIELD, stroke=BG, sw=1.5))
    f.append(dashed_circle(tx, ty, 16, fill='none', stroke=FIELD, sw=1.2, dash='3,3'))
    f.append(text(tx, ty + 24, 'Ціль (5.0, 0)', 12, FIELD, 'middle', bold=True))

    # Error comparison annotation
    f.append(fitbox(20, 20, 270, 78,
                    'Дрейф курсу роздуває похибку:\nБічна похибка e_lat ≈ s · δθ\nГіроскоп фіксує курс і зрізає конус',
                    size=11, pad=6, fill='#f8fafc', stroke=LINE))

    render(os.path.join(IMG, 'dead-reckoning-drift.svg'), W, H, *f,
           title='Накопичення навігаційного дрейфу та корекція гіроскопом')


# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — Mission Finite State Machine (FSM)
# ════════════════════════════════════════════════════════════════════════════
def fig_mission_fsm():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # State boxes
    states = {
        'IDLE': (90, 90, 'IDLE\nКалібрування IMU\nОчікування команди'),
        'ROTATE': (270, 90, 'ROTATE_TO_WP\nДоворот на місці\n|α| > α_порогу'),
        'TRACK': (450, 90, 'TRACK_WP\nРух за Pure Pursuit\nv > 0, регулювання ω'),
        'ACTION': (630, 90, 'ACTION\nЗупинка в точці\nВимір / таймер'),
        'RTB': (540, 260, 'RETURN_TO_BASE\nНавігація до (0,0)\nРеверс точок'),
        'PARKED': (180, 260, 'PARKED_HOME\nКінцевий доворот\nВимкнення моторів')
    }

    # Draw state boxes
    for k, (cx, cy, label) in states.items():
        col = FIELD if k in ('IDLE', 'PARKED') else (POS if k == 'RTB' else INK)
        b, _, _ = textbox(cx, cy, label, 11, pad=8, fill='#f4f7f9', stroke=col, sw=1.8, min_w=120)
        f.append(b)

    # Transitions Row 1
    f.append(arrow(155, 90, 205, 90, color=INK, sw=1.6))
    f.append(text(180, 78, 'Старт', 10, MUTED, 'middle'))

    f.append(arrow(335, 90, 385, 90, color=INK, sw=1.6))
    f.append(text(360, 78, '|α| < 15°', 10, MUTED, 'middle'))

    f.append(arrow(515, 90, 565, 90, color=INK, sw=1.6))
    f.append(text(540, 78, 'ρ < R_acc', 10, MUTED, 'middle'))

    # Loop back or RTB from ACTION
    f.append(arc_path(450, 90, 180, math.radians(-150), math.radians(-30), MUTED, sw=1.4, dash='4,3'))
    f.append(arrow(280, 20, 270, 50, color=MUTED, sw=1.4))
    f.append(text(450, 16, 'Є наступна точка місії (next WP)', 10, MUTED, 'middle'))

    # RTB transition: ACTION -> RTB
    f.append(arrow(630, 135, 590, 220, color=POS, sw=1.6))
    f.append(text(645, 185, 'Всі WP пройдені /\nКоманда RTB', 10, POS, 'middle'))

    # RTB -> PARKED
    f.append(arrow(475, 260, 245, 260, color=POS, sw=1.8))
    f.append(text(360, 248, 'Дистанція до старту < R_acc', 10, POS, 'middle', bold=True))

    # PARKED -> IDLE (ready for next)
    f.append(arrow(180, 220, 120, 135, color=FIELD, sw=1.4))
    f.append(text(110, 195, 'Курс вирівняно', 10, FIELD, 'middle'))

    render(os.path.join(IMG, 'nav-mission-fsm.svg'), W, H, *f,
           title='Скінченний автомат планувальника місії та повернення на базу')


# ════════════════════════════════════════════════════════════════════════════
# Figure 4 — UMBmark Square Calibration Test
# ════════════════════════════════════════════════════════════════════════════
def fig_umbmark_test():
    W, H = 720, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    panel_w = W / 2

    # Divider
    f.append(line(panel_w, 30, panel_w, H - 30, color='#e2e8f0', sw=1.2))

    # Panel 1: CW Run
    c1x, c1y = 180, 210
    sz = 160
    # Nominal square (dashed)
    f.append(dashed_rect(c1x - sz / 2, c1y - sz / 2, sz, sz, fill='none', stroke=MUTED, sw=1.4, dash='5,4', rx=0))
    # Actual CW distorted trajectory
    cw_pts = [
        '%.1f,%.1f' % (c1x - sz / 2, c1y + sz / 2),
        '%.1f,%.1f' % (c1x - sz / 2 - 12, c1y - sz / 2 - 8),
        '%.1f,%.1f' % (c1x + sz / 2 + 8, c1y - sz / 2 - 18),
        '%.1f,%.1f' % (c1x + sz / 2 + 18, c1y + sz / 2 + 6),
        '%.1f,%.1f' % (c1x - sz / 2 + 22, c1y + sz / 2 + 14)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (' '.join(cw_pts), POS))
    f.append(circle(c1x - sz / 2, c1y + sz / 2, 4.5, fill=INK, stroke=BG, sw=1.0))
    f.append(circle(c1x - sz / 2 + 22, c1y + sz / 2 + 14, 4.5, fill=POS, stroke=BG, sw=1.0))
    f.append(text(c1x - sz / 2 + 42, c1y + sz / 2 + 28, 'Кінець CW', 11, POS, 'middle', bold=True))

    f.append(text(c1x, 50, 'Тест за годинниковою (CW)', 13, INK, 'middle', bold=True))
    f.append(text(c1x, 70, '4 повороти праворуч на 90°', 11, MUTED, 'middle'))

    # Panel 2: CCW Run
    c2x, c2y = 540, 210
    f.append(dashed_rect(c2x - sz / 2, c2y - sz / 2, sz, sz, fill='none', stroke=MUTED, sw=1.4, dash='5,4', rx=0))
    ccw_pts = [
        '%.1f,%.1f' % (c2x - sz / 2, c2y + sz / 2),
        '%.1f,%.1f' % (c2x + sz / 2 + 14, c2y + sz / 2 + 8),
        '%.1f,%.1f' % (c2x + sz / 2 + 24, c2y - sz / 2 - 12),
        '%.1f,%.1f' % (c2x - sz / 2 - 6, c2y - sz / 2 - 20),
        '%.1f,%.1f' % (c2x - sz / 2 - 18, c2y + sz / 2 + 22)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (' '.join(ccw_pts), NEG))
    f.append(circle(c2x - sz / 2, c2y + sz / 2, 4.5, fill=INK, stroke=BG, sw=1.0))
    f.append(circle(c2x - sz / 2 - 18, c2y + sz / 2 + 22, 4.5, fill=NEG, stroke=BG, sw=1.0))
    f.append(text(c2x - sz / 2 - 38, c2y + sz / 2 + 34, 'Кінець CCW', 11, NEG, 'middle', bold=True))

    f.append(text(c2x, 50, 'Тест проти годинникової (CCW)', 13, INK, 'middle', bold=True))
    f.append(text(c2x, 70, '4 повороти ліворуч на 90°', 11, MUTED, 'middle'))

    # Bottom summary box
    f.append(fitbox(W / 2 - 250, H - 54, 500, 42,
                    'Розділення похибок: зсув колії L змінює радіус поворотів однаково,\nа різниця діаметрів коліс D_L ≠ D_R створює постійний бічний розворот',
                    size=10.5, pad=4, fill='#f8fafc', stroke=LINE))

    render(os.path.join(IMG, 'umbmark-square-test.svg'), W, H, *f,
           title='Калібрувальний тест UMBmark для диференціального приводу')


if __name__ == '__main__':
    fig_pure_pursuit_geometry()
    fig_dead_reckoning_drift()
    fig_mission_fsm()
    fig_umbmark_test()
    print('Done.')
