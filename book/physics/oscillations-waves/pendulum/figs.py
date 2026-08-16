# -*- coding: utf-8 -*-
"""Фігури до теми «Маятник».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Фігура model.svg: Схема математичного маятника ────────────────────────
def make_model_fig():
    W, H = 640, 480
    f = []
    
    ox, oy = 320, 70  # Точка підвісу O
    length = 260
    angle_deg = 28
    angle_rad = math.radians(angle_deg)
    
    # Точка маси (bob)
    bx = ox + length * math.sin(angle_rad)
    by = oy + length * math.cos(angle_rad)
    
    # Стеля (опора)
    f.append(line(ox - 90, oy, ox + 90, oy, color=INK, sw=3))
    xx = ox - 80
    while xx <= ox + 80:
        f.append(line(xx, oy, xx - 10, oy - 12, color=MUTED, sw=1.5))
        xx += 14
        
    # Точка підвісу O
    f.append(circle(ox, oy, 5, fill=INK, stroke=INK))
    f.append(text(ox - 18, oy - 12, "O", size=15, bold=True, color=INK))
    
    # Вертикальна вісь (пунктир)
    f.append(line(ox, oy, ox, oy + length + 40, color=MUTED, sw=1.5, dash="5,5"))
    
    # Дуга кута theta
    arc_r = 80
    arc_d = "M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" % (
        ox, oy + arc_r,
        arc_r, arc_r,
        ox + arc_r * math.sin(angle_rad), oy + arc_r * math.cos(angle_rad)
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,3"/>' % (arc_d, POS))
    f.append(text(ox + 22, oy + 58, "θ", size=18, bold=True, color=POS))
    
    # Нитка L
    f.append(line(ox, oy, bx, by, color=INK, sw=2.5))
    # Позначка довжини L
    lx = ox + (length / 2 - 15) * math.sin(angle_rad) - 22
    ly = oy + (length / 2 - 15) * math.cos(angle_rad)
    f.append(text(lx, ly, "L", size=17, bold=True, color=INK))
    
    # Дуга траєкторії руху s
    traj_r = length
    t_a1 = math.radians(-35)
    t_a2 = math.radians(45)
    t_x1 = ox + traj_r * math.sin(t_a1)
    t_y1 = oy + traj_r * math.cos(t_a1)
    t_x2 = ox + traj_r * math.sin(t_a2)
    t_y2 = oy + traj_r * math.cos(t_a2)
    traj_d = "M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" % (t_x1, t_y1, traj_r, traj_r, t_x2, t_y2)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (traj_d, MUTED))
    f.append(text(t_x2 + 10, t_y2 + 5, "s = L·θ", size=13, color=MUTED))
    
    # Маса m (bob)
    f.append(circle(bx, by, 18, fill=NEG, stroke=INK, sw=2))
    f.append(text(bx, by + 5, "m", size=15, bold=True, color="#ffffff"))
    
    # Вектори сил у точці маси
    # 1. Сила тяжіння F_g = m·g (донизу)
    fg_len = 110
    f.append(arrow(bx, by, bx, by + fg_len, color=POS, sw=2.5))
    f.append(text(bx + 38, by + fg_len - 10, "F_g = m·g", size=14, bold=True, color=POS))
    
    # Компоненти F_g: радіальна m·g·cos(θ) та дотична m·g·sin(θ)
    fr_len = fg_len * math.cos(angle_rad)
    fr_x = bx + fr_len * math.sin(angle_rad)
    fr_y = by + fr_len * math.cos(angle_rad)
    f.append(line(bx, by + fg_len, fr_x, fr_y, color=MUTED, sw=1.5, dash="3,3"))
    f.append(arrow(bx, by, fr_x, fr_y, color=MUTED, sw=1.8))
    f.append(text(fr_x + 40, fr_y + 5, "m·g·cos θ", size=12, color=MUTED))
    
    # Сила натягу нитки T (протилежна радіальній)
    t_len = fr_len + 15
    tx_end = bx - t_len * math.sin(angle_rad)
    ty_end = by - t_len * math.cos(angle_rad)
    f.append(arrow(bx, by, tx_end, ty_end, color=FIELD, sw=2.5))
    f.append(text(tx_end - 20, ty_end + 10, "T", size=15, bold=True, color=FIELD))
    
    # Дотична повертальна сила F_tau = -m·g·sin(θ)
    ftau_len = fg_len * math.sin(angle_rad)
    ftau_x = bx - ftau_len * math.cos(angle_rad)
    ftau_y = by + ftau_len * math.sin(angle_rad)
    f.append(line(bx, by + fg_len, ftau_x, ftau_y, color=MUTED, sw=1.5, dash="3,3"))
    f.append(arrow(bx, by, ftau_x, ftau_y, color=POS, sw=2.5))
    f.append(text(ftau_x - 70, ftau_y + 22, "F_τ = −m·g·sin θ", size=14, bold=True, color=POS))
    
    render(os.path.join(IMG, 'model.svg'), W, H, *f)


# ── 2. Фігура sine-approx.svg: Порівняння sin(θ) та θ ─────────────────────────
def make_sine_approx_fig():
    W, H = 640, 420
    f = []
    
    p1_x, p1_y, p1_w, p1_h = 60, 60, 240, 300
    p2_x, p2_y, p2_w, p2_h = 360, 60, 240, 300
    
    # --- Панель 1 ---
    f.append(arrow(p1_x, p1_y + p1_h, p1_x + p1_w + 20, p1_y + p1_h, color=INK, sw=1.8))
    f.append(arrow(p1_x, p1_y + p1_h, p1_x, p1_y - 20, color=INK, sw=1.8))
    f.append(text(p1_x + p1_w - 10, p1_y + p1_h + 30, "Кут θ (рад)", size=12, color=INK))
    f.append(text(p1_x - 10, p1_y - 10, "Значення", size=12, color=INK))
    f.append(text(p1_x + 100, p1_y - 35, "а) sin(θ) та тотожність θ", size=14, bold=True, color=INK))
    
    max_theta = math.pi / 2
    ticks_deg = [0, 30, 60, 90]
    for deg in ticks_deg:
        rad = math.radians(deg)
        cx = p1_x + (rad / max_theta) * p1_w
        f.append(line(cx, p1_y + p1_h, cx, p1_y + p1_h + 5, color=INK, sw=1.5))
        lbl = "0" if deg == 0 else ("π/6" if deg == 30 else ("π/3" if deg == 60 else "π/2"))
        f.append(text(cx, p1_y + p1_h + 20, lbl, size=11, color=INK))
        
    for val, lbl in [(0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5")]:
        cy = p1_y + p1_h - (val / 1.6) * p1_h
        f.append(line(p1_x - 5, cy, p1_x, cy, color=INK, sw=1.5))
        f.append(text(p1_x - 20, cy + 4, lbl, size=11, color=INK))
        f.append(line(p1_x, cy, p1_x + p1_w, cy, color=MUTED, sw=1, dash="2,4"))

    pts_lin = []
    pts_sin = []
    N = 100
    for i in range(N + 1):
        rad = (i / N) * max_theta
        cx = p1_x + (rad / max_theta) * p1_w
        cy_lin = p1_y + p1_h - (rad / 1.6) * p1_h
        pts_lin.append((cx, cy_lin))
        cy_sin = p1_y + p1_h - (math.sin(rad) / 1.6) * p1_h
        pts_sin.append((cx, cy_sin))
        
    d_lin = "M " + " L ".join("%.1f %.1f" % p for p in pts_lin)
    d_sin = "M " + " L ".join("%.1f %.1f" % p for p in pts_sin)
    
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,5"/>' % (d_lin, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_sin, POS))
    
    f.append(line(p1_x + 25, p1_y + 30, p1_x + 55, p1_y + 30, color=NEG, sw=2, dash="5,5"))
    f.append(text(p1_x + 110, p1_y + 34, "y = θ (лінійне)", size=11, color=NEG))
    f.append(line(p1_x + 25, p1_y + 50, p1_x + 55, p1_y + 50, color=POS, sw=2.5))
    f.append(text(p1_x + 110, p1_y + 54, "y = sin(θ) (точне)", size=11, color=POS))

    # --- Панель 2 ---
    f.append(arrow(p2_x, p2_y + p2_h, p2_x + p2_w + 20, p2_y + p2_h, color=INK, sw=1.8))
    f.append(arrow(p2_x, p2_y + p2_h, p2_x, p2_y - 20, color=INK, sw=1.8))
    f.append(text(p2_x + p2_w - 10, p2_y + p2_h + 30, "Кут θ (град)", size=12, color=INK))
    f.append(text(p2_x - 10, p2_y - 10, "Похибка (%)", size=12, color=INK))
    f.append(text(p2_x + 100, p2_y - 35, "б) Похибка наближення sin(θ) ≈ θ", size=14, bold=True, color=INK))
    
    for deg in [0, 30, 60, 90]:
        cx = p2_x + (deg / 90.0) * p2_w
        f.append(line(cx, p2_y + p2_h, cx, p2_y + p2_h + 5, color=INK, sw=1.5))
        f.append(text(cx, p2_y + p2_h + 20, "%d°" % deg, size=11, color=INK))
        
    max_err = 60.0
    for err_v in [10, 20, 30, 40, 50]:
        cy = p2_y + p2_h - (err_v / max_err) * p2_h
        f.append(line(p2_x - 5, cy, p2_x, cy, color=INK, sw=1.5))
        f.append(text(p2_x - 20, cy + 4, "%d%%" % err_v, size=11, color=INK))
        f.append(line(p2_x, cy, p2_x + p2_w, cy, color=MUTED, sw=1, dash="2,4"))
        
    pts_err = []
    for i in range(1, N + 1):
        deg = (i / N) * 90.0
        rad = math.radians(deg)
        err = ((rad - math.sin(rad)) / math.sin(rad)) * 100.0
        cx = p2_x + (deg / 90.0) * p2_w
        cy = p2_y + p2_h - (err / max_err) * p2_h
        pts_err.append((cx, cy))
        
    d_err = "M " + " L ".join("%.1f %.1f" % p for p in pts_err)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_err, POS))
    
    for deg_mark, lbl in [(30, "30° (4.7%)"), (60, "60° (20.9%)")]:
        rad = math.radians(deg_mark)
        err = ((rad - math.sin(rad)) / math.sin(rad)) * 100.0
        cx = p2_x + (deg_mark / 90.0) * p2_w
        cy = p2_y + p2_h - (err / max_err) * p2_h
        f.append(circle(cx, cy, 4, fill=POS, stroke=INK))
        f.append(text(cx, cy - 12, lbl, size=11, bold=True, color=POS))

    render(os.path.join(IMG, 'sine-approx.svg'), W, H, *f)


# ── 3. Фігура period-vs-amplitude.svg: Залежність періоду від амплітуди ────────
def make_period_amplitude_fig():
    W, H = 640, 420
    f = []
    
    px, py, pw, ph = 70, 70, 500, 300
    
    f.append(arrow(px, py + ph, px + pw + 25, py + ph, color=INK, sw=2))
    f.append(arrow(px, py + ph, px, py - 25, color=INK, sw=2))
    f.append(text(px + pw - 40, py + ph + 35, "Початкова амплітуда θ₀ (градуси)", size=13, bold=True, color=INK))
    f.append(text(px - 10, py - 12, "Період T / T₀", size=13, bold=True, color=INK))
    
    max_deg = 180.0
    for deg in [0, 30, 60, 90, 120, 150, 180]:
        cx = px + (deg / max_deg) * pw
        f.append(line(cx, py + ph, cx, py + ph + 6, color=INK, sw=1.5))
        lbl = "%d°" % deg
        f.append(text(cx, py + ph + 22, lbl, size=11, color=INK))
        if deg > 0 and deg < 180:
            f.append(line(cx, py, cx, py + ph, color=MUTED, sw=1, dash="2,4"))

    max_ratio = 3.0
    for r in [1.0, 1.2, 1.5, 2.0, 2.5, 3.0]:
        cy = py + ph - ((r - 1.0) / (max_ratio - 1.0)) * ph
        f.append(line(px - 6, cy, px, cy, color=INK, sw=1.5))
        f.append(text(px - 25, cy + 4, "%.1f" % r, size=11, color=INK))
        f.append(line(px, cy, px + pw, cy, color=MUTED, sw=1, dash="2,4"))

    cy_t0 = py + ph - ((1.0 - 1.0) / (max_ratio - 1.0)) * ph
    f.append(line(px, cy_t0, px + pw, cy_t0, color=NEG, sw=2, dash="6,4"))
    f.append(text(px + pw - 120, cy_t0 - 10, "Т = Т₀ (ізохронізм)", size=12, color=NEG))

    pts_exact = []
    N = 150
    for i in range(N):
        deg = (i / (N - 1)) * 172.0
        rad0 = math.radians(deg)
        k = math.sin(rad0 / 2.0)
        ratio = 1.0 + 0.25 * (k**2) + (9.0/64.0) * (k**4) + (225.0/2304.0) * (k**6) + (11025.0/147456.0) * (k**8) + (896070.0/14745600.0) * (k**10)
        
        cx = px + (deg / max_deg) * pw
        cy = py + ph - ((ratio - 1.0) / (max_ratio - 1.0)) * ph
        pts_exact.append((cx, cy))
        
    d_exact = "M " + " L ".join("%.1f %.1f" % p for p in pts_exact)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_exact, POS))

    key_points = [
        (60, 1.073, "60° (+7.3%)"),
        (90, 1.180, "90° (+18.0%)"),
        (120, 1.373, "120° (+37.3%)"),
        (150, 1.872, "150° (+87.2%)")
    ]
    for deg, ratio, lbl in key_points:
        cx = px + (deg / max_deg) * pw
        cy = py + ph - ((ratio - 1.0) / (max_ratio - 1.0)) * ph
        f.append(circle(cx, cy, 4.5, fill=POS, stroke=INK))
        f.append(text(cx, cy - 12, lbl, size=11, bold=True, color=POS))

    cx_180 = px + pw
    f.append(line(cx_180, py, cx_180, py + ph, color=POS, sw=1.5, dash="3,3"))
    f.append(text(cx_180 - 70, py + 25, "θ₀ → 180° (T → ∞)", size=12, bold=True, color=POS))

    render(os.path.join(IMG, 'period-vs-amplitude.svg'), W, H, *f)


# ── 4. Фігура physical-pendulum.svg: Фізичний маятник ─────────────────────────
def make_physical_pendulum_fig():
    W, H = 580, 460
    f = []
    
    ox, oy = 260, 80
    
    f.append(line(ox - 70, oy, ox + 70, oy, color=INK, sw=3))
    xx = ox - 60
    while xx <= ox + 60:
        f.append(line(xx, oy, xx - 10, oy - 10, color=MUTED, sw=1.5))
        xx += 14

    f.append(line(ox, oy, ox, oy + 340, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(ox + 40, oy + 335, "Вертикаль", size=11, color=MUTED))

    angle_deg = 22
    angle_rad = math.radians(angle_deg)
    
    body_local = [
        (-40, -20), (30, -25), (70, 40), (90, 140), (70, 240),
        (20, 290), (-50, 270), (-90, 180), (-80, 80), (-50, 20)
    ]
    body_world = []
    for lx, ly in body_local:
        wx = ox + lx * math.cos(angle_rad) - ly * math.sin(angle_rad)
        wy = oy + lx * math.sin(angle_rad) + ly * math.cos(angle_rad)
        body_world.append((wx, wy))
        
    d_body = "M " + " L ".join("%.1f %.1f" % p for p in body_world) + " Z"
    f.append('<path d="%s" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="2.5"/>' % (d_body, NEG, INK))

    f.append(circle(ox, oy, 6, fill=INK, stroke=INK))
    f.append(text(ox - 35, oy - 10, "O (вісь)", size=14, bold=True, color=INK))

    d_cm = 160
    cm_x = ox + d_cm * math.sin(angle_rad)
    cm_y = oy + d_cm * math.cos(angle_rad)
    
    f.append(line(ox, oy, cm_x, cm_y, color=INK, sw=2, dash="4,4"))
    
    arc_r = 70
    arc_d = "M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" % (
        ox, oy + arc_r,
        arc_r, arc_r,
        ox + arc_r * math.sin(angle_rad), oy + arc_r * math.cos(angle_rad)
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,3"/>' % (arc_d, POS))
    f.append(text(ox + 18, oy + 55, "θ", size=16, bold=True, color=POS))

    f.append(circle(cm_x, cm_y, 7, fill=POS, stroke=INK, sw=2))
    f.append(text(cm_x + 65, cm_y + 5, "C (центр мас)", size=14, bold=True, color=POS))

    mid_dx = ox + (d_cm / 2) * math.sin(angle_rad) - 15
    mid_dy = oy + (d_cm / 2) * math.cos(angle_rad)
    f.append(text(mid_dx, mid_dy, "d", size=16, bold=True, color=INK))

    fg_len = 90
    f.append(arrow(cm_x, cm_y, cm_x, cm_y + fg_len, color=POS, sw=2.5))
    f.append(text(cm_x + 45, cm_y + fg_len - 5, "F_g = m·g", size=14, bold=True, color=POS))

    leq = 230
    p_x = ox + leq * math.sin(angle_rad)
    p_y = oy + leq * math.cos(angle_rad)
    f.append(line(cm_x, cm_y, p_x, p_y, color=INK, sw=2, dash="4,4"))
    f.append(circle(p_x, p_y, 6, fill=FIELD, stroke=INK, sw=2))
    f.append(text(p_x + 75, p_y + 5, "P (центр качання)", size=14, bold=True, color=FIELD))

    f.append(line(ox - 50, oy, ox - 50, p_y, color=MUTED, sw=1.5))
    f.append(line(ox - 55, oy, ox - 45, oy, color=MUTED, sw=1.5))
    f.append(line(ox - 55, p_y, ox - 45, p_y, color=MUTED, sw=1.5))
    f.append(text(ox - 130, oy + leq / 2 + 5, "L_звед = I / (m·d)", size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, 'physical-pendulum.svg'), W, H, *f)


# ── 5. Фігура phase-portrait.svg: Фазовий портрет маятника ───────────────────
def make_phase_portrait_fig():
    W, H = 660, 460
    f = []
    
    ox, oy = 330, 230
    scale_x = 75
    scale_y = 60
    
    f.append(arrow(30, oy, 630, oy, color=INK, sw=2))
    f.append(arrow(ox, 430, ox, 30, color=INK, sw=2))
    f.append(text(600, oy + 25, "θ (рад)", size=13, bold=True, color=INK))
    f.append(text(ox + 70, 45, "ω = dθ/dt (рад/с)", size=13, bold=True, color=INK))
    
    pi_px = math.pi * scale_x
    ticks = [
        (-2 * math.pi, "-2π"),
        (-math.pi, "-π"),
        (0, "0"),
        (math.pi, "π"),
        (2 * math.pi, "2π")
    ]
    for val, lbl in ticks:
        cx = ox + val * scale_x
        f.append(line(cx, oy - 6, cx, oy + 6, color=INK, sw=1.5))
        f.append(text(cx, oy + 24, lbl, size=13, bold=True, color=INK))
        if val != 0:
            f.append(line(cx, 45, cx, 415, color=MUTED, sw=1, dash="2,4"))

    w0 = 1.0
    
    for theta0_deg in [30, 60, 90, 130, 160]:
        th0 = math.radians(theta0_deg)
        pts_top = []
        pts_bot = []
        N = 80
        for i in range(N + 1):
            th = -th0 + (2.0 * th0 * i) / N
            arg = 2.0 * (w0**2) * (math.cos(th) - math.cos(th0))
            if arg < 0: arg = 0
            om = math.sqrt(arg)
            
            cx = ox + th * scale_x
            cy_top = oy - om * scale_y
            cy_bot = oy + om * scale_y
            pts_top.append((cx, cy_top))
            pts_bot.append((cx, cy_bot))
            
        pts_loop = pts_top + pts_bot[::-1]
        d_loop = "M " + " L ".join("%.1f %.1f" % p for p in pts_loop) + " Z"
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_loop, NEG))

    for th_center in [-2 * math.pi, 0, 2 * math.pi]:
        f.append(circle(ox + th_center * scale_x, oy, 4.5, fill=NEG, stroke=INK))

    for center_offset in [-2 * math.pi, 0, 2 * math.pi]:
        pts_sep_top = []
        pts_sep_bot = []
        N = 100
        for i in range(N + 1):
            th = -math.pi + (2.0 * math.pi * i) / N
            om = 2.0 * w0 * math.cos(th / 2.0)
            
            cx = ox + (th + center_offset) * scale_x
            if 30 <= cx <= 630:
                pts_sep_top.append((cx, oy - om * scale_y))
                pts_sep_bot.append((cx, oy + om * scale_y))
                
        if pts_sep_top:
            d_s1 = "M " + " L ".join("%.1f %.1f" % p for p in pts_sep_top)
            d_s2 = "M " + " L ".join("%.1f %.1f" % p for p in pts_sep_bot)
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_s1, POS))
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_s2, POS))

    for th_saddle in [-math.pi, math.pi]:
        cx = ox + th_saddle * scale_x
        f.append(circle(cx, oy, 5.5, fill=POS, stroke=INK, sw=2))

    for C_val in [1.3, 2.2]:
        pts_rot_top = []
        pts_rot_bot = []
        N = 160
        for i in range(N + 1):
            th = -2.2 * math.pi + (4.4 * math.pi * i) / N
            arg = 2.0 * (w0**2) * (math.cos(th) + C_val)
            om = math.sqrt(arg)
            
            cx = ox + th * scale_x
            if 30 <= cx <= 630:
                pts_rot_top.append((cx, oy - om * scale_y))
                pts_rot_bot.append((cx, oy + om * scale_y))
                
        d_r1 = "M " + " L ".join("%.1f %.1f" % p for p in pts_rot_top)
        d_r2 = "M " + " L ".join("%.1f %.1f" % p for p in pts_rot_bot)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_r1, FIELD))
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_r2, FIELD))

    f.append(text(ox, oy - 45, "Лібрації (колювання)", size=12, bold=True, color=NEG))
    f.append(text(ox + pi_px / 2, oy - 2 * scale_y - 10, "Сепаратриса", size=12, bold=True, color=POS))
    f.append(text(ox, oy - 2.7 * scale_y, "Ротації (повний оберт)", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'phase-portrait.svg'), W, H, *f)


if __name__ == '__main__':
    make_model_fig()
    make_sine_approx_fig()
    make_period_amplitude_fig()
    make_physical_pendulum_fig()
    make_phase_portrait_fig()
    print("Успішно згенеровано 5 фігур маятника у ./img/")
