# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема про центральний многовид».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

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

# ── Фігура 1: Геометрія фазового простору та вкладення W^c ────────────────────
def fig_center_manifold_geometry():
    W, H = 840, 460
    f = []
    
    f.append(text(W / 2, 28, "Геометрія фазового простору та вкладення центрального многовиду W^c", size=16, bold=True))
    
    # Ліва частина: Фазова площина (x, y) з інваріантними підпросторами та многовидами
    cx, cy = 250, 250
    f.append(rect(20, 60, 460, 370, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    
    # Осі координат / Лінійні інваріантні підпростори E^c та E^s
    f.append(line(40, cy, 450, cy, color=MUTED, sw=1.5, dash="4,4")) # E^c
    f.append(line(cx, 80, cx, 410, color=MUTED, sw=1.5, dash="4,4")) # E^s
    
    f.append(text(440, cy - 10, "E^c (Re(λ)=0)", size=12, color=MUTED, anchor="end", bold=True))
    f.append(text(cx + 10, 95, "E^s (Re(λ)<0)", size=12, color=MUTED, anchor="start", bold=True))
    
    # Точка рівноваги (0, 0)
    f.append(circle(cx, cy, 5, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(cx - 15, cy + 20, "О (0,0)", size=12, color=INK, bold=True))
    
    # Крива центрального многовиду W^c: y = h(x) -> y = k * x^2
    pts_wc = []
    for px in range(-190, 195, 5):
        x_val = px / 100.0
        y_val = 0.35 * (x_val ** 2) - 0.1 * (x_val ** 3)
        sx = cx + px
        sy = cy - y_val * 100.0
        pts_wc.append((sx, sy))
    
    p_str = " ".join("%.1f,%.1f" % pt for pt in pts_wc)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (p_str, MAIN))
    f.append(text(pts_wc[-1][0] - 10, pts_wc[-1][1] - 15, "W^c: y = h(x)", size=13, color=MAIN, bold=True))
    
    # Стійкий многовид W^s
    pts_ws = []
    for py in range(-150, 155, 5):
        y_val = py / 100.0
        x_val = 0.15 * (y_val ** 2)
        sx = cx + x_val * 100.0
        sy = cy + py
        pts_ws.append((sx, sy))
    p_ws_str = " ".join("%.1f,%.1f" % pt for pt in pts_ws)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (p_ws_str, GREEN))
    f.append(text(pts_ws[0][0] + 10, pts_ws[0][1] + 15, "W^s", size=13, color=GREEN, bold=True))
    
    # Фазові траєкторії
    traj1 = [(70, 110), (120, 210), (160, 240), (200, 246), (250, 250)]
    for i in range(len(traj1)-1):
        x1, y1 = traj1[i]
        x2, y2 = traj1[i+1]
        f.append(line(x1, y1, x2, y2, color=ACCENT, sw=1.8))
    f.append(head_at(traj1[2][0], traj1[2][1], traj1[2][0]-traj1[1][0], traj1[2][1]-traj1[1][1], color=ACCENT, size=7))
    
    traj2 = [(390, 390), (350, 300), (320, 265), (280, 255), (250, 250)]
    for i in range(len(traj2)-1):
        x1, y1 = traj2[i]
        x2, y2 = traj2[i+1]
        f.append(line(x1, y1, x2, y2, color=ACCENT, sw=1.8))
    f.append(head_at(traj2[2][0], traj2[2][1], traj2[2][0]-traj2[1][0], traj2[2][1]-traj2[1][1], color=ACCENT, size=7))
    
    # Права частина: Пояснювальна картка
    rx0 = 500
    f.append(rect(rx0, 60, 320, 370, fill='#F4F6F8', stroke=BORDER, sw=1.2, rx=6))
    
    f.append(text(rx0 + 160, 90, "Ключові властивості W^c", size=14, bold=True, color=INK))
    
    box1, _, _ = textbox(rx0 + 160, 130, "1. Дотичність у 0:\nW^c дотичний до E^c у точці рівноваги", size=11, pad=6, fill="#FFFFFF", stroke=BORDER)
    f.append(box1)
    
    box2, _, _ = textbox(rx0 + 160, 205, "2. Інваріантність:\nФазовий потік не залишає W^c:\nякщо (x(0),y(0)) ∈ W^c, то (x(t),y(t)) ∈ W^c", size=11, pad=6, fill="#FFFFFF", stroke=BORDER)
    f.append(box2)
    
    box3, _, _ = textbox(rx0 + 160, 295, "3. Атрактивність (Притягання):\nУсі сусідні траєкторії експоненційно\nнаближаються до W^c зі швидкістю ~ e^(Re(λ_s)t)", size=11, pad=6, fill="#FFFFFF", stroke=BORDER)
    f.append(box3)
    
    box4, _, _ = textbox(rx0 + 160, 385, "Динаміка на W^c визначає стійкість!", size=11, pad=6, fill="#EAF0FD", stroke=MAIN, color=MAIN, bold=True)
    f.append(box4)

    return render(os.path.join(IMG, "center-manifold-geometry.svg"), W, H, *f)

# ── Фігура 2: Принцип зведення (редукція вимірності) ─────────────────────────
def fig_reduction_principle():
    W, H = 840, 420
    f = []
    
    f.append(text(W / 2, 26, "Принцип зведення (редукції вимірності) на центральний многовид", size=16, bold=True))
    
    # Блок 1: Повна високовимірна система
    bx1, by1, bw, bh = 40, 70, 230, 220
    f.append(rect(bx1, by1, bw, bh, fill="#FAFBFD", stroke=ACCENT, sw=1.8, rx=8))
    f.append(text(bx1 + bw/2, by1 + 30, "Повна система", size=14, bold=True, color=ACCENT))
    f.append(text(bx1 + bw/2, by1 + 55, "Вимірність: n + m", size=12, color=MUTED))
    
    sys_eqs = "dx/dt = A·x + f(x, y)\ndy/dt = B·y + g(x, y)\n\nRe(λ_A) = 0 (n змінних)\nRe(λ_B) < 0 (m змінних)"
    f.append(mtext(bx1 + bw/2, by1 + 95, sys_eqs, size=12, color=INK, anchor="middle"))
    
    # Стрілка редукції
    ax1, ay = bx1 + bw + 15, by1 + bh/2
    ax2 = ax1 + 170
    f.append(varrow(ax1, ay, ax2, ay, color=MAIN, sw=3.0, head=10))
    
    f.append(text(ax1 + 85, ay - 35, "Експоненційне", size=12, color=MAIN, bold=True))
    f.append(text(ax1 + 85, ay - 18, "згасання y(t) -> h(x)", size=12, color=MAIN, bold=True))
    f.append(text(ax1 + 85, ay + 20, "Заміна: y = h(x)", size=12, color=INK))
    f.append(text(ax1 + 85, ay + 38, "N(h(x)) = 0", size=12, color=MUTED))
    
    # Блок 2: Редукована система на W^c
    bx2, by2 = ax2 + 15, by1
    f.append(rect(bx2, by2, bw, bh, fill="#EAF0FD", stroke=MAIN, sw=2.0, rx=8))
    f.append(text(bx2 + bw/2, by2 + 30, "Редукована система", size=14, bold=True, color=MAIN))
    f.append(text(bx2 + bw/2, by2 + 55, "Вимірність: n (лише W^c)", size=12, color=MAIN, bold=True))
    
    red_eqs = "dx/dt = A·x + f(x, h(x))\n\nЗахоплює точні:\n• Біфуркації\n• Граничні цикли\n• Стійкість точки 0"
    f.append(mtext(bx2 + bw/2, by2 + 105, red_eqs, size=12, color=INK, anchor="middle"))
    
    # Нижня панель
    f.append(rect(40, 315, 760, 80, fill="#FFFFFF", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(W/2, 338, "Практичне значення редукції для механіки та фізики", size=13, bold=True, color=INK))
    f.append(text(W/2, 362, "Замість розв'язувати складну система з сотень ступенів вільності (напр. флаттер крила чи конвекція),", size=12, color=MUTED))
    f.append(text(W/2, 380, "ми аналізуємо скалярне рівняння або 2D систему на W^c без втрати фізичної точності.", size=12, color=MUTED))

    return render(os.path.join(IMG, "reduction-principle.svg"), W, H, *f)

# ── Фігура 3: Тейлорівське наближення h(x) ───────────────────────────────────
def fig_taylor_approximation():
    W, H = 840, 440
    f = []
    
    f.append(text(W / 2, 26, "Спектральне наближення y = h(x) рядами Тейлора у околі точки 0", size=16, bold=True))
    
    # Графік порівняння наближень
    gx0, gy0, gw, gh = 60, 65, 430, 340
    f.append(rect(gx0, gy0, gw, gh, fill="#FAFBFD", stroke=BORDER, sw=1.2, rx=6))
    
    gcx, gcy = gx0 + gw/2, gy0 + gh/2 + 40
    
    # Осі координат
    f.append(varrow(gx0 + 20, gcy, gx0 + gw - 20, gcy, color=LINE, sw=1.5))
    f.append(varrow(gcx, gy0 + gh - 20, gcx, gy0 + 20, color=LINE, sw=1.5))
    
    f.append(text(gx0 + gw - 35, gcy + 20, "x (змінна E^c)", size=12, color=INK))
    f.append(text(gcx + 15, gy0 + 35, "y (змінна E^s)", size=12, color=INK))
    
    # 1. Лінійне наближення y = 0
    f.append(line(gx0 + 30, gcy, gx0 + gw - 30, gcy, color=MUTED, sw=2.0, dash="5,5"))
    
    # 2. Квадратичне наближення h_2(x) = 0.35 * x^2
    pts_h2 = []
    for px in range(-170, 175, 5):
        xv = px / 100.0
        yv = 0.35 * (xv ** 2)
        pts_h2.append((gcx + px, gcy - yv * 120))
    p2_str = " ".join("%.1f,%.1f" % pt for pt in pts_h2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,2"/>' % (p2_str, GREEN))
    
    # 3. Кубічне наближення h_3(x) = 0.35 * x^2 - 0.15 * x^3
    pts_h3 = []
    for px in range(-170, 175, 5):
        xv = px / 100.0
        yv = 0.35 * (xv ** 2) - 0.15 * (xv ** 3)
        pts_h3.append((gcx + px, gcy - yv * 120))
    p3_str = " ".join("%.1f,%.1f" % pt for pt in pts_h3)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (p3_str, MAIN))
    
    # Область збіжності
    f.append(line(gcx - 110, gy0 + 40, gcx - 110, gy0 + gh - 40, color=ACCENT, sw=1.2, dash="3,3"))
    f.append(line(gcx + 110, gy0 + 40, gcx + 110, gy0 + gh - 40, color=ACCENT, sw=1.2, dash="3,3"))
    f.append(text(gcx, gy0 + gh - 15, "Область локальної аналітичності |x| < δ", size=11, color=ACCENT, anchor="middle", bold=True))
    
    # Легенда праворуч
    lx0 = 510
    f.append(rect(lx0, 65, 300, 340, fill="#FFFFFF", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(lx0 + 150, 95, "Ієрархія Тейлорівських наближень", size=13, bold=True, color=INK))
    
    f.append(line(lx0 + 20, 135, lx0 + 60, 135, color=MUTED, sw=2.0, dash="5,5"))
    f.append(text(lx0 + 75, 139, "y = 0: Лінійне E^c (O(|x|^2) похибка)", size=11, anchor="start"))
    
    f.append(line(lx0 + 20, 175, lx0 + 60, 175, color=GREEN, sw=2.0, dash="4,2"))
    f.append(text(lx0 + 75, 179, "y = a₂ x²: Квадратичне h₂(x)", size=11, anchor="start", bold=True))
    
    f.append(line(lx0 + 20, 215, lx0 + 60, 215, color=MAIN, sw=3.0))
    f.append(text(lx0 + 75, 219, "y = a₂ x² + a₃ x³: Точне W^c", size=11, anchor="start", bold=True))
    
    box_coeff, _, _ = textbox(lx0 + 150, 290, "Обчислення коефіцієнтів:\nN(h(x)) = 0  ⇒\na₂ = g₂₀ / (2A - B)\na₃ = (g₃₀ + 2a₂f₂₀) / (3A - B)", size=11, pad=8, fill="#F4F6F8", stroke=BORDER)
    f.append(box_coeff)
    
    f.append(text(lx0 + 150, 375, "Похибка редукції: O(|x|^(k+1))", size=12, color=MAIN, bold=True))

    return render(os.path.join(IMG, "taylor-approximation.svg"), W, H, *f)

if __name__ == "__main__":
    fig_center_manifold_geometry()
    fig_reduction_principle()
    fig_taylor_approximation()
    print("Успішно згенеровано 3 фігури у ./img/")
