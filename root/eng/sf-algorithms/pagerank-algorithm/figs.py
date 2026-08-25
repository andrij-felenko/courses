# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
NODE_BG    = "#eef2f7"
NODE_LINE  = "#334155"
ACCENT_A   = "#2563eb"  # синій вузол A
ACCENT_D   = "#059669"  # зелений вузол D (найвищий ранг)
WARN_RED   = "#dc2626"  # пастка / тупик
TELEPORT   = "#7c3aed"  # телепортація (фіолетовий)
EDGE_COLOR = "#64748b"


def p_node(cx, cy, name, rank_str="", r=26, fill=NODE_BG, stroke=NODE_LINE, sw=2.0):
    """Круглий вузол графа з назвою та значенням рангу."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)
    out += text(cx, cy + (1 if not rank_str else -3), name, size=15, color=INK, bold=True)
    if rank_str:
        out += text(cx, cy + 14, rank_str, size=11, color=stroke if stroke != NODE_LINE else MUTED, bold=True)
    return out


def directed_edge(x1, y1, x2, y2, label="", r1=26, r2=26, col=EDGE_COLOR, sw=1.8, dash=None, label_side="top"):
    """Стрілка між вузлами з урахуванням радіусів та підписом ваги/частки."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * (r2 + 4), y2 - uy * (r2 + 4)
    
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    out = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
           'stroke-width="%.1f"%s marker-end="url(#arrow)"/>' % (ax, ay, bx, by, col, sw, d))
    
    if label:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        # зміщення підпису перпендикулярно до ребра
        nx, ny = -uy * 14, ux * 14
        if label_side == "bottom":
            nx, ny = uy * 14, -ux * 14
        out += circle(mx + nx, my + ny, 11, fill=BG, stroke="none", sw=0)
        out += text(mx + nx, my + ny + 4, label, size=11, color=col, bold=True)
    return out


# ── ФІГ.1 Перерозподіл ваги голосів між сторінками ────────────────────────────
def fig_flow():
    W, H = 760, 320
    p = []
    
    # Координати 4 вузлів
    ax, ay = 120.0, 160.0  # Вузол A (авторитетний донор)
    bx, by = 340.0, 80.0   # Вузол B
    cx, cy = 340.0, 240.0  # Вузол C
    dx, dy = 580.0, 160.0  # Вузол D (акумулятор ваги)
    
    # Ребра
    # A має 2 вихідні лінки: віддає по 1/2 свого рангу (0.40 / 2 = 0.20) до B і C
    p.append(directed_edge(ax, ay, bx, by, "1/2 (0.20)", r1=28, r2=28, col=ACCENT_A, sw=2.2))
    p.append(directed_edge(ax, ay, cx, cy, "1/2 (0.20)", r1=28, r2=28, col=ACCENT_A, sw=2.2, label_side="bottom"))
    
    # B має 1 вихідний лінк до D: віддає 100% (0.20)
    p.append(directed_edge(bx, by, dx, dy, "1/1 (0.20)", r1=28, r2=28, col=EDGE_COLOR, sw=2.0))
    
    # C має 1 вихідний лінк до D: віддає 100% (0.20)
    p.append(directed_edge(cx, cy, dx, dy, "1/1 (0.20)", r1=28, r2=28, col=EDGE_COLOR, sw=2.0, label_side="bottom"))
    
    # Вузли
    p.append(p_node(ax, ay, "A", "r = 0.40", r=28, fill="#eff6ff", stroke=ACCENT_A))
    p.append(p_node(bx, by, "B", "r = 0.20", r=28, fill=NODE_BG, stroke=NODE_LINE))
    p.append(p_node(cx, cy, "C", "r = 0.20", r=28, fill=NODE_BG, stroke=NODE_LINE))
    p.append(p_node(dx, dy, "D", "r = 0.40", r=28, fill="#ecfdf5", stroke=ACCENT_D))
    
    # Пояснювальний блок знизу
    b, bw, bh = textbox(W / 2, 280,
                        "Вузол A ділить свій ранг порівну: B і C отримують по r[A] / 2 = 0.20.\n"
                        "Вузол D акумулює вхідні внески: r[D] = r[B] + r[C] = 0.20 + 0.20 = 0.40.",
                        size=12, fill="#f8fafc", stroke="#cbd5e1", pad=8)
    p.append(b)
    
    render(os.path.join(OUT, "pagerank-flow.svg"), W, H, *p,
           title="Перерозподіл ваги голосів між сторінками")


# ── ФІГ.2 Патології графа: висячі вузли, пастки та телепортація ────────────────
def fig_traps():
    W, H = 820, 360
    p = []
    
    # Ліва панель: Тупик (Dangling node)
    p.append(rect(20, 45, 230, 240, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=8))
    p.append(text(135, 70, "Тупик (Dead End)", size=13, color=WARN_RED, bold=True))
    
    d1x, d1y = 80.0, 150.0
    d2x, d2y = 185.0, 150.0
    p.append(directed_edge(d1x, d1y, d2x, d2y, "", r1=22, r2=22, col=WARN_RED, sw=2.0))
    p.append(p_node(d1x, d1y, "A", "", r=22, fill=BG, stroke=NODE_LINE))
    p.append(p_node(d2x, d2y, "X", "deg=0", r=22, fill="#fee2e2", stroke=WARN_RED))
    
    tb1, _, _ = textbox(135, 235, "Ранг витікає у нікуди:\nсумарна вага графа згасає", size=11,
                        fill=BG, stroke="#f87171", pad=6)
    p.append(tb1)
    
    # Середня панель: Павутинна пастка (Spider Trap)
    p.append(rect(275, 45, 250, 240, fill="#fffbeb", stroke="#fcd34d", sw=1.2, rx=8))
    p.append(text(400, 70, "Павутинна пастка (Spider Trap)", size=13, color="#b45309", bold=True))
    
    s1x, s1y = 330.0, 150.0
    s2x, s2y = 410.0, 115.0
    s3x, s3y = 470.0, 175.0
    
    p.append(directed_edge(s1x, s1y, s2x, s2y, "", r1=20, r2=20, col=EDGE_COLOR))
    p.append(directed_edge(s2x, s2y, s3x, s3y, "", r1=20, r2=20, col="#b45309", sw=2.0))
    p.append(directed_edge(s3x, s3y, s2x, s2y, "", r1=20, r2=20, col="#b45309", sw=2.0))
    
    p.append(p_node(s1x, s1y, "U", "", r=20, fill=BG, stroke=NODE_LINE))
    p.append(p_node(s2x, s2y, "T1", "", r=20, fill="#fef3c7", stroke="#b45309"))
    p.append(p_node(s3x, s3y, "T2", "", r=20, fill="#fef3c7", stroke="#b45309"))
    
    tb2, _, _ = textbox(400, 235, "Ранг поглинається циклом:\nпастка стягує 100% ваги", size=11,
                        fill=BG, stroke="#f59e0b", pad=6)
    p.append(tb2)
    
    # Права панель: Телепортація (Рішення)
    p.append(rect(550, 45, 250, 240, fill="#f5f3ff", stroke="#c4b5fd", sw=1.2, rx=8))
    p.append(text(675, 70, "Телепортація (Damping d)", size=13, color=TELEPORT, bold=True))
    
    t1x, t1y = 600.0, 140.0
    t2x, t2y = 720.0, 140.0
    
    # Звичайний лінк з імовірністю d
    p.append(directed_edge(t1x, t1y, t2x, t2y, "d = 0.85", r1=20, r2=20, col=TELEPORT, sw=2.2))
    # Випадковий стрибок 1 - d
    p.append(directed_edge(t1x, t1y, t2x, t2y, "(1-d)/N", r1=20, r2=20, col="#8b5cf6", sw=1.5,
                           dash="4 3", label_side="bottom"))
    
    p.append(p_node(t1x, t1y, "i", "", r=20, fill=BG, stroke=NODE_LINE))
    p.append(p_node(t2x, t2y, "j", "", r=20, fill="#ede9fe", stroke=TELEPORT))
    
    tb3, _, _ = textbox(675, 235, "Мандрівник переходить за лінком (d)\nабо стрибає на будь-яку сторінку (1-d)", size=11,
                        fill=BG, stroke="#a78bfa", pad=6)
    p.append(tb3)
    
    # Підсумковий рядок
    b_foot, _, _ = textbox(W / 2, 325,
                           "Коефіцієнт згасання d перетворює граф на незвідний та аперіодичний марківський ланцюг.",
                           size=12, fill="#f8fafc", stroke="#cbd5e1", pad=6)
    p.append(b_foot)
    
    render(os.path.join(OUT, "traps-and-teleport.svg"), W, H, *p,
           title="Патології графа та їх розв'язання телепортацією")


# ── ФІГ.3 Геометричне стягування похибки у степеневому методі ──────────────────
def fig_power_iteration():
    W, H = 760, 330
    p = []
    
    # Осі графіка
    ox, oy = 80.0, 240.0
    gw, gh = 620.0, 180.0
    
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    
    # Підписи осей
    p.append(text(ox + gw - 20, oy + 25, "Ітерація k", size=12, color=INK, bold=True))
    p.append(text(ox - 10, oy - gh + 15, "Похибка ||r(k) - r*||", size=12, color=INK, bold=True, anchor="start"))
    
    # Експоненційне падіння похибки: e(k) = e(0) * (0.85)^k
    # k від 0 до 16
    steps = 16
    pts = []
    for k in range(steps + 1):
        x = ox + (k / steps) * (gw - 40)
        # похибка в логарифмічно-наочному масштабі
        err = math.pow(0.85, k)
        y = oy - err * (gh - 30)
        pts.append((x, y))
    
    # Малюємо криву
    path_d = ["M %.1f %.1f" % pts[0]]
    for x, y in pts[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), ACCENT_A))
    
    # Точки та позначки ітерацій
    for k in [0, 1, 2, 4, 8, 12, 16]:
        x, y = pts[k]
        p.append(circle(x, y, 4, fill=ACCENT_A, stroke=BG, sw=1.5))
        p.append(line(x, oy, x, oy + 4, color=LINE, sw=1.0))
        p.append(text(x, oy + 16, str(k), size=11, color=MUTED))
    
    # Позначка швидкості збіжності
    p.append(directed_edge(pts[2][0] + 50, pts[2][1] - 30, pts[3][0] + 5, pts[3][1] - 5, "",
                           r1=0, r2=0, col="#047857", sw=1.5))
    tb_rate, _, _ = textbox(pts[2][0] + 120, pts[2][1] - 40,
                            "Стискання похибки зі швидкістю d = 0.85:\n||r(k+1) - r*|| <= 0.85 · ||r(k) - r*||",
                            size=11, fill="#ecfdf5", stroke="#10b981", pad=6)
    p.append(tb_rate)
    
    # Підсумковий коментар
    b_msg, _, _ = textbox(W / 2, 295,
                          "Завдяки спектральному зазору 1 - d = 0.15 похибка зменшується в 10 разів кожні 15 ітерацій.",
                          size=12, fill="#f8fafc", stroke="#cbd5e1", pad=6)
    p.append(b_msg)
    
    render(os.path.join(OUT, "power-iteration.svg"), W, H, *p,
           title="Геометрична збіжність степеневого методу")


if __name__ == "__main__":
    fig_flow()
    fig_traps()
    fig_power_iteration()
    print("PageRank figures generated successfully.")
