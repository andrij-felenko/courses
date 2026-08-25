# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема Такенса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

MAIN = "#2457d6"
ACCENT = "#c0392b"
BORDER = "#d0d7de"
GREEN = "#27ae60"
PURPLE = "#8e44ad"

def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))

def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

# ── Фігура 1: Концепція реконструкції фазового простору за затримками ────────
def fig_takens_embedding_concept():
    W, H = 840, 420
    f = []
    
    # Ліва панель: Одномірний часовий ряд s(t)
    f.append(rect(20, 50, 390, 340, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(215, 75, "1D вимірюваний часовий ряд s(t)", size=13, bold=True, color=INK))
    
    # Осі часового ряду
    f.append(line(50, 340, 380, 340, color=MUTED, sw=1.5)) # t axis
    f.append(line(50, 100, 50, 350, color=MUTED, sw=1.5)) # s axis
    f.append(text(380, 355, "t", size=12, color=MUTED, bold=True))
    f.append(text(35, 105, "s(t)", size=12, color=MUTED, bold=True))
    
    # Гармонічна/хаотична крива s(t)
    pts_s = []
    for px in range(0, 310, 2):
        t_val = px * 0.04
        val = math.sin(t_val) + 0.6 * math.sin(2.3 * t_val + 0.5)
        sy = 220 - val * 70
        sx = 60 + px
        pts_s.append((sx, sy))
    
    p_str = " ".join("%.1f,%.1f" % pt for pt in pts_s)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_str, MAIN))
    
    # Точки відліку t, t-tau, t-2tau
    t_idx = 120
    t_tau1 = 85
    t_tau2 = 50
    
    pt_t = pts_s[t_idx]
    pt_t1 = pts_s[t_tau1]
    pt_t2 = pts_s[t_tau2]
    
    # Вертикальні пунктири
    f.append(line(pt_t2[0], pt_t2[1], pt_t2[0], 340, color=PURPLE, sw=1.2, dash="3,3"))
    f.append(line(pt_t1[0], pt_t1[1], pt_t1[0], 340, color=GREEN, sw=1.2, dash="3,3"))
    f.append(line(pt_t[0], pt_t[1], pt_t[0], 340, color=ACCENT, sw=1.2, dash="3,3"))
    
    f.append(circle(pt_t2[0], pt_t2[1], 5, fill=PURPLE))
    f.append(circle(pt_t1[0], pt_t1[1], 5, fill=GREEN))
    f.append(circle(pt_t[0], pt_t[1], 5, fill=ACCENT))
    
    f.append(text(pt_t2[0], 358, "t - 2τ", size=11, color=PURPLE, bold=True))
    f.append(text(pt_t1[0], 358, "t - τ", size=11, color=GREEN, bold=True))
    f.append(text(pt_t[0], 358, "t", size=11, color=ACCENT, bold=True))
    
    # Формула вектора станом на t
    f.append(rect(60, 365, 310, 20, fill='#FFFFFF', stroke=BORDER, sw=1.0, rx=4))
    f.append(text(215, 379, "Y(t) = ( s(t), s(t-τ), s(t-2τ) )", size=11, bold=True, color=INK))
    
    # Стрілка переходу від 1D до 3D
    f.append(varrow(420, 220, 460, 220, color=MAIN, sw=2.5, head=10))
    f.append(text(440, 205, "Мапа Такенса Φ", size=11, color=MAIN, bold=True))
    
    # Права панель: Відновлений 3D фазовий простір R^3
    f.append(rect(470, 50, 350, 340, fill='#F4F6F8', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(645, 75, "3D Відновлений атрактор у R^3", size=13, bold=True, color=INK))
    
    # Осі 3D
    ox, oy = 620, 240
    f.append(line(ox, oy, ox + 140, oy, color=MUTED, sw=1.5)) # s(t)
    f.append(line(ox, oy, ox, oy - 130, color=MUTED, sw=1.5)) # s(t-tau)
    f.append(line(ox, oy, ox - 90, oy + 90, color=MUTED, sw=1.5)) # s(t-2tau)
    
    f.append(text(ox + 145, oy + 5, "s(t)", size=12, color=ACCENT, bold=True))
    f.append(text(ox - 15, oy - 125, "s(t-τ)", size=12, color=GREEN, bold=True))
    f.append(text(ox - 110, oy + 105, "s(t-2τ)", size=12, color=PURPLE, bold=True))
    
    # Петельна орбіта (атрактор Лоренца чи схожа хаотична петля)
    pts_3d = []
    for step in range(0, 300, 3):
        t_val = step * 0.04
        v1 = math.sin(t_val) + 0.6 * math.sin(2.3 * t_val + 0.5)
        v2 = math.sin(t_val - 0.7) + 0.6 * math.sin(2.3 * (t_val - 0.7) + 0.5)
        v3 = math.sin(t_val - 1.4) + 0.6 * math.sin(2.3 * (t_val - 1.4) + 0.5)
        
        # Проекція (v1, v2, v3) на 2D екрані
        px_3d = ox + v1 * 80 - v3 * 45
        py_3d = oy - v2 * 75 + v3 * 45
        pts_3d.append((px_3d, py_3d))
    
    p3_str = " ".join("%.1f,%.1f" % pt for pt in pts_3d)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (p3_str, MAIN))
    
    # Виділена точка Y(t)
    vy1 = math.sin(120 * 0.04) + 0.6 * math.sin(2.3 * 120 * 0.04 + 0.5)
    vy2 = math.sin(120 * 0.04 - 0.7) + 0.6 * math.sin(2.3 * (120 * 0.04 - 0.7) + 0.5)
    vy3 = math.sin(120 * 0.04 - 1.4) + 0.6 * math.sin(2.3 * (120 * 0.04 - 1.4) + 0.5)
    pty_x = ox + vy1 * 80 - vy3 * 45
    pty_y = oy - vy2 * 75 + vy3 * 45
    f.append(circle(pty_x, pty_y, 6, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(pty_x + 10, pty_y - 8, "Y(t)", size=12, color=ACCENT, bold=True))
    
    render(os.path.join(IMG_DIR, "takens-embedding-concept.svg"), W, H, "".join(f), title="Реконструкція фазового простору за часовим рядом (Метод часових затримок)")

# ── Фігура 2: Самоперетин проти гладкого вкладення (Дифеоморфізм) ─────────────
def fig_diffeomorphism_projection():
    W, H = 840, 420
    f = []
    
    # Ліва панель: m < 2d (m = 2): Проекційні самоперетини
    f.append(rect(20, 50, 390, 340, fill='#FFF5F5', stroke='#E57373', sw=1.2, rx=6))
    f.append(text(215, 75, "Мала вимірність m < 2d_A (наприклад m = 2)", size=13, bold=True, color=ACCENT))
    
    cx1, cy1 = 215, 230
    # Петля у формі вісімки з самоперетином
    pts_loop1 = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        # Самоперетин у центрі
        rx = 130 * math.sin(rad)
        ry = 90 * math.sin(2 * rad) / 2.0
        pts_loop1.append((cx1 + rx, cy1 + ry))
    
    p1_str = " ".join("%.1f,%.1f" % pt for pt in pts_loop1)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p1_str, ACCENT))
    
    # Точка самоперетину у центрі
    f.append(circle(cx1, cy1, 7, fill="#FFEB3B", stroke=ACCENT, sw=2.0))
    f.append(text(cx1, cy1 - 15, "Хибний самоперетин!", size=12, color=ACCENT, bold=True))
    
    # Пояснення самоперетину
    f.append(rect(40, 335, 350, 45, fill='#FFFFFF', stroke='#E57373', sw=1.0, rx=4))
    f.append(text(215, 352, "Траєкторії перетинаються у 2D проекції:", size=11, bold=True, color=INK))
    f.append(text(215, 368, "порушується однозначність детермінованого руху", size=11, color=MUTED))
    
    # Права панель: m >= 2d_A + 1 (m = 3): Гладке вкладення без самоперетинів
    f.append(rect(430, 50, 390, 340, fill='#E8F5E9', stroke='#81C784', sw=1.2, rx=6))
    f.append(text(625, 75, "Достатня вимірність m ≥ 2d_A + 1 (наприклад m = 3)", size=13, bold=True, color=GREEN))
    
    cx2, cy2 = 625, 230
    # Просторова спіраль / петля, розведена по третій осі z
    pts_loop2 = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        rx = 120 * math.sin(rad)
        # У 3D третя координата розводить петлю по висоті у центрі
        z_offset = 35 * math.cos(rad)
        ry = 85 * math.sin(2 * rad) / 2.0 + z_offset
        pts_loop2.append((cx2 + rx, cy2 + ry))
    
    p2_str = " ".join("%.1f,%.1f" % pt for pt in pts_loop2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p2_str, GREEN))
    
    # Замість самоперетину — чіткий зазор між вітками
    f.append(line(cx2 - 15, cy2 - 20, cx2 + 15, cy2 - 20, color=GREEN, sw=1.5, dash="2,2"))
    f.append(line(cx2 - 15, cy2 + 20, cx2 + 15, cy2 + 20, color=GREEN, sw=1.5, dash="2,2"))
    f.append(varrow(cx2, cy2 - 18, cx2, cy2 + 18, color=GREEN, sw=1.5, head=6))
    f.append(text(cx2 + 25, cy2 + 4, "Зазор у R^m (без перетинів)", size=11, color=GREEN, bold=True))
    
    # Пояснення гладкого вкладення
    f.append(rect(450, 335, 350, 45, fill='#FFFFFF', stroke='#81C784', sw=1.0, rx=4))
    f.append(text(625, 352, "Дифеоморфізм Ф: фазовий атрактор вкладено", size=11, bold=True, color=INK))
    f.append(text(625, 368, "збережено топологію, вимірність d_2 та показники Ляпунова", size=11, color=MUTED))
    
    render(os.path.join(IMG_DIR, "diffeomorphism-projection.svg"), W, H, "".join(f), title="Вплив вимірності вкладення m: хибні самоперетини проти дифеоморфізму")

# ── Фігура 3: Вибір параметрів tau та m (Взаємна інформація та FNN) ───────────
def fig_tau_m_selection():
    W, H = 840, 420
    f = []
    
    # Ліва панель: Середня взаємна інформація I(tau) для вибору tau
    f.append(rect(20, 50, 390, 340, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(215, 75, "1. Вибір часової затримки τ: Взаємна інформація I(τ)", size=12, bold=True, color=INK))
    
    # Осі графика I(tau)
    f.append(line(50, 330, 380, 330, color=MUTED, sw=1.5)) # tau axis
    f.append(line(50, 100, 50, 340, color=MUTED, sw=1.5)) # I axis
    f.append(text(380, 345, "τ", size=12, color=MUTED, bold=True))
    f.append(text(30, 105, "I(τ)", size=12, color=MUTED, bold=True))
    
    # Крива I(tau) з першим мінімумом
    pts_mi = []
    tau_opt_x = 0
    tau_opt_y = 0
    min_val = 999
    
    for step in range(0, 310, 2):
        t_val = step / 40.0
        # Затухаючі коливання з першим мінімумом при t_val ~ 2.0 (step ~ 80)
        val = math.exp(-0.4 * t_val) * (1.2 + 0.8 * math.cos(math.pi * t_val))
        sx = 60 + step
        sy = 320 - val * 130
        pts_mi.append((sx, sy))
        if step > 20 and val < min_val:
            min_val = val
            tau_opt_x = sx
            tau_opt_y = sy
    
    pmi_str = " ".join("%.1f,%.1f" % pt for pt in pts_mi)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pmi_str, MAIN))
    
    # Маркер першого мінімуму
    f.append(circle(tau_opt_x, tau_opt_y, 6, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(line(tau_opt_x, tau_opt_y, tau_opt_x, 330, color=ACCENT, sw=1.5, dash="3,3"))
    f.append(text(tau_opt_x, 345, "τ_opt (Перший мінімум)", size=11, color=ACCENT, bold=True))
    f.append(text(tau_opt_x + 10, tau_opt_y - 10, "min I(τ)", size=11, color=ACCENT, bold=True))
    
    # Текст пояснення
    f.append(text(215, 375, "Мінімум взаємної інформації мінімізує нелінійну залежність", size=11, color=MUTED))
    
    # Права панель: Дріб хибних сусідів FNN(m) для вибору m
    f.append(rect(430, 50, 390, 340, fill='#F4F6F8', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(625, 75, "2. Вибір вимірності m: Хибні найближчі сусіди (FNN)", size=12, bold=True, color=INK))
    
    # Осі графика FNN
    f.append(line(460, 330, 790, 330, color=MUTED, sw=1.5)) # m axis
    f.append(line(460, 100, 460, 340, color=MUTED, sw=1.5)) # FNN % axis
    f.append(text(790, 345, "m", size=12, color=MUTED, bold=True))
    f.append(text(420, 105, "FNN (%)", size=12, color=MUTED, bold=True))
    
    # Точки FNN від m=1 до m=6
    fnn_data = [(1, 92), (2, 65), (3, 12), (4, 1.2), (5, 0.2), (6, 0.0)]
    pts_fnn = []
    for m_val, pct in fnn_data:
        mx = 470 + m_val * 50
        my = 330 - (pct / 100.0) * 210
        pts_fnn.append((mx, my, m_val, pct))
    
    # Лінія спадання FNN
    pfnn_str = " ".join("%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_fnn)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pfnn_str, PURPLE))
    
    for mx, my, m_val, pct in pts_fnn:
        f.append(circle(mx, my, 5, fill=PURPLE))
        f.append(text(mx, 345, str(m_val), size=11, color=INK, bold=True))
        if m_val <= 3:
            f.append(text(mx + 8, my - 8, "%.0f%%" % pct, size=10, color=PURPLE))
    
    # Поріг m_opt при FNN -> 0
    m_opt_x = pts_fnn[3][0] # m=4
    m_opt_y = pts_fnn[3][1]
    f.append(circle(m_opt_x, m_opt_y, 7, fill=GREEN, stroke=INK, sw=1.5))
    f.append(line(m_opt_x, m_opt_y, m_opt_x, 330, color=GREEN, sw=1.5, dash="3,3"))
    f.append(text(m_opt_x, 360, "m_opt (FNN → 0)", size=11, color=GREEN, bold=True))
    
    # Текст пояснення
    f.append(text(625, 385, "При m ≥ m_opt хибні геометрічні проекції зникають", size=11, color=MUTED))
    
    render(os.path.join(IMG_DIR, "tau-m-selection.svg"), W, H, "".join(f), title="Методи вибору оптимальних параметрів реконструкції (τ та m)")

if __name__ == '__main__':
    fig_takens_embedding_concept()
    fig_diffeomorphism_projection()
    fig_tau_m_selection()
    print("Успішно згенеровано 3 фігури у ./img/")
