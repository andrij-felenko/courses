# -*- coding: utf-8 -*-
"""Фігури до теми «Ефективність ребра».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#d97706"
WARN = "#b45309"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def rtext(x, y, s, angle=-90, size=13, color=INK, anchor="middle", bold=True):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s transform="rotate(%d %.1f %.1f)">%s</text>' %
            (x, y, FONT, size, color, anchor, ' font-weight="700"' if bold else '', angle, x, y, esc(s)))


# ── Фігура 1: Тепловий баланс на елементі ребра dx ─────────────────────────
def fig_fin_heat_balance():
    W, H = 840, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тепловий баланс елемента ребра dx", size=18, bold=True))
    f.append(text(W / 2, 52, "Осьова теплопровідність Q(x) проти бічної конвекції dQ_conv",
                  size=12.5, color=MUTED))

    # Стінка основи
    f.append(rect(60, 100, 40, 260, fill="#dce4ec", stroke=INK, sw=2))
    f.append(text(80, 235, "Основа T_b", size=13, bold=True, anchor="middle", color=INK))

    # Тіло ребра
    f.append(rect(100, 140, 560, 180, fill="#f0f4f8", stroke=INK, sw=2.4))

    # Виділений елемент dx
    ex1, ex2 = 320, 420
    f.append(rect(ex1, 140, ex2 - ex1, 180, fill="#faeceb", stroke=NEG, sw=2.2, rx=0))
    f.append(text((ex1 + ex2) / 2, 230, "елемент dx", size=14, bold=True, color=NEG, anchor="middle"))

    # Стрілка теплового потоку на вході Q(x)
    f.append(varrow(130, 230, ex1 - 10, 230, color=ACCENT, sw=3.5, head=14))
    f.append(text(220, 215, "Q(x) = -k·A_c·(dT/dx)", size=13, bold=True, color=ACCENT, anchor="middle"))

    # Стрілка теплового потоку на виході Q(x+dx)
    f.append(varrow(ex2 + 10, 230, 620, 230, color=ACCENT, sw=2.5, head=12))
    f.append(text(520, 215, "Q(x+dx)", size=13, bold=True, color=ACCENT, anchor="middle"))

    # Стрілки конвекції вгору і вниз від елемента dx
    f.append(varrow(370, 140, 370, 90, color=WARN, sw=2.5, head=11))
    f.append(text(370, 78, "dQ_conv = h·(P·dx)·(T(x) - T_∞)", size=12.5, bold=True, color=WARN, anchor="middle"))

    f.append(varrow(370, 320, 370, 370, color=WARN, sw=2.5, head=11))
    f.append(text(370, 388, "dQ_conv (в довкілля T_∞)", size=12.5, bold=True, color=WARN, anchor="middle"))

    # Координатна вісь x
    f.append(varrow(100, 415, 680, 415, color=INK, sw=1.8, head=10))
    f.append(text(690, 420, "x", size=14, italic=True, bold=True, color=INK))
    f.append(line(100, 325, 100, 422, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(100, 436, "x = 0 (основа)", size=11.5, color=MUTED, anchor="middle"))
    f.append(line(660, 325, 660, 422, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(660, 436, "x = L (вершок)", size=11.5, color=MUTED, anchor="middle"))

    f.append(line(ex1, 320, ex1, 420, color=NEG, sw=1.2, dash="3 3"))
    f.append(line(ex2, 320, ex2, 420, color=NEG, sw=1.2, dash="3 3"))
    f.append(varrow((ex1+ex2)/2, 405, ex1, 405, color=NEG, sw=1.2, head=7))
    f.append(varrow((ex1+ex2)/2, 405, ex2, 405, color=NEG, sw=1.2, head=7))
    f.append(text((ex1 + ex2) / 2, 400, "dx", size=12, italic=True, bold=True, color=NEG, anchor="middle"))

    # Позначення площі поперечного перерізу A_c і периметра P
    f.append(rect(700, 180, 110, 100, fill="#f8fafc", stroke=INK, sw=1.5))
    f.append(text(755, 202, "Переріз ребра", size=12, bold=True, anchor="middle", color=INK))
    f.append(text(755, 230, "A_c — площа", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(755, 250, "P — периметр", size=11.5, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'fin-heat-balance.svg'), W, H, "".join(f))


# ── Фігура 2: Профіль температури уздовж ребра при різних m·L ─────────────
def fig_temperature_profile():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Розподіл температури уздовж ребра θ(x) / θ_b", size=18, bold=True))
    f.append(text(W / 2, 52, "Залежність від безрозмірного параметра mL: що більше mL, то холодніший вершок",
                  size=12.5, color=MUTED))

    ox, oy = 90, 400
    gw, gh = 480, 310

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2))
    for i in range(1, 5):
        y = oy - i * (gh / 5)
        f.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1.0))
        val = i * 0.2
        f.append(text(ox - 12, y + 4, "%.1f" % val, size=11.5, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy + 4, "0.0", size=11.5, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - gh + 4, "1.0", size=11.5, color=MUTED, anchor="end"))
    f.append(rtext(ox - 45, oy - gh / 2, "θ(x) / θ_b  =  (T(x) - T_∞) / (T_b - T_∞)", size=13, color=INK, anchor="middle"))

    for i in range(1, 6):
        x = ox + i * (gw / 5)
        f.append(line(x, oy - gh, x, oy, color="#e2e8f0", sw=1.0))
        val = i * 0.2
        f.append(text(x, oy + 22, "%.1f" % val, size=11.5, color=MUTED, anchor="middle"))
    f.append(text(ox, oy + 22, "0.0", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(ox + gw / 2, oy + 44, "Безрозмірна координата  x / L", size=13, bold=True, color=INK, anchor="middle"))

    # Криві для різних mL
    curves = [
        (0.3, POS, "mL = 0.3  (ізотермічне, η_f = 97%)"),
        (1.0, ACCENT, "mL = 1.0  (ефективне, η_f = 76%)"),
        (2.0, WARN, "mL = 2.0  (помірне, η_f = 48%)"),
        (4.0, NEG, "mL = 4.0  (згасання, η_f = 25%)"),
    ]

    for mL, col, lab in curves:
        pts = []
        denom = math.cosh(mL)
        for step in range(101):
            x_ratio = step / 100.0
            px = ox + x_ratio * gw
            theta_ratio = math.cosh(mL * (1.0 - x_ratio)) / denom
            py = oy - theta_ratio * gh
            pts.append((px, py))
        f.append(polyline(pts, color=col, sw=3.0))

    # Легенда праворуч від графіка
    lx, ly = 590, 140
    f.append(rect(lx, ly, 235, 130, fill=BG, stroke=LINE, sw=1.2, rx=6))
    for idx, (mL, col, lab) in enumerate(curves):
        yy = ly + 22 + idx * 28
        f.append(line(lx + 12, yy, lx + 38, yy, color=col, sw=3.0))
        f.append(text(lx + 46, yy + 4, lab, size=11, bold=True, color=col, anchor="start"))

    render(os.path.join(IMG, 'temperature-profile.svg'), W, H, "".join(f))


# ── Фігура 3: Графік ефективності ребра η_f проти m·L ──────────────────────
def fig_fin_efficiency_curve():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ефективність ребра η_f залежно від параметра mL", size=18, bold=True))
    f.append(text(W / 2, 52, "Порівняння прямокутного та трикутного профілів",
                  size=12.5, color=MUTED))

    ox, oy = 90, 400
    gw, gh = 480, 310

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2))
    for i in range(1, 5):
        y = oy - i * (gh / 5)
        f.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1.0))
        val = i * 20
        f.append(text(ox - 12, y + 4, "%d%%" % val, size=11.5, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy + 4, "0%", size=11.5, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - gh + 4, "100%", size=11.5, color=MUTED, anchor="end"))
    f.append(rtext(ox - 45, oy - gh / 2, "Ефективність ребра  η_f  =  Q_fin / Q_max", size=13, color=INK, anchor="middle"))

    for i in range(1, 8):
        val = i * 0.5
        x = ox + (val / 3.5) * gw
        f.append(line(x, oy - gh, x, oy, color="#e2e8f0", sw=1.0))
        f.append(text(x, oy + 22, "%.1f" % val, size=11.5, color=MUTED, anchor="middle"))
    f.append(text(ox, oy + 22, "0.0", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(ox + gw / 2, oy + 44, "Комплексний параметр ребра  mL  =  L · √(h·P / k·A_c)", size=13, bold=True, color=INK, anchor="middle"))

    # Крива 1: Прямокутне ребро
    pts_rect = []
    for step in range(1, 101):
        mL = step / 100.0 * 3.5
        eta = math.tanh(mL) / mL
        px = ox + (mL / 3.5) * gw
        py = oy - eta * gh
        pts_rect.append((px, py))
    f.append(polyline([(ox, oy - gh)] + pts_rect, color=ACCENT, sw=3.2))

    # Крива 2: Трикутне ребро
    pts_tri = []
    for step in range(1, 101):
        mL = step / 100.0 * 3.5
        eta = 1.0 / math.sqrt(1.0 + (4.0/3.0)*(mL**2))
        px = ox + (mL / 3.5) * gw
        py = oy - eta * gh
        pts_tri.append((px, py))
    f.append(polyline([(ox, oy - gh)] + pts_tri, color=POS, sw=2.6, dash="6 4"))

    # Легенда та опис зон праворуч від графіка
    lx, ly = 590, 140
    f.append(rect(lx, ly, 235, 200, fill=BG, stroke=LINE, sw=1.2, rx=6))

    f.append(line(lx + 12, ly + 25, lx + 38, ly + 25, color=ACCENT, sw=3.2))
    f.append(text(lx + 46, ly + 29, "Прямокутне: tanh(mL)/mL", size=11, bold=True, color=ACCENT, anchor="start"))

    f.append(line(lx + 12, ly + 55, lx + 46, ly + 55, color=POS, sw=2.6, dash="6 4"))
    f.append(text(lx + 46, ly + 59, "Трикутне (економне)", size=11, bold=True, color=POS, anchor="start"))

    f.append(line(lx + 10, ly + 80, lx + 225, ly + 80, color=LINE, sw=1.0))

    f.append(text(lx + 15, ly + 102, "Зони дизайну:", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(lx + 15, ly + 124, "• mL < 0.7: η_f > 80% (ізотерм.)", size=10.5, color=POS, anchor="start"))
    f.append(text(lx + 15, ly + 146, "• 0.7..1.8: компроміс маса/тепло", size=10.5, color=WARN, anchor="start"))
    f.append(text(lx + 15, ly + 168, "• mL > 1.8: η_f < 50% (перевитрата)", size=10.5, color=NEG, anchor="start"))

    render(os.path.join(IMG, 'fin-efficiency-curve.svg'), W, H, "".join(f))


# ── Фігура 4: Оребрена поверхня (масив ребер) та загальна ефективність η_o ─
def fig_fin_vs_array():
    W, H = 840, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Сумарна ефективність оребреної поверхні η_o", size=18, bold=True))
    f.append(text(W / 2, 52, "Поєднання коефіцієнта ребра η_f та незайнятої основи A_u",
                  size=12.5, color=MUTED))

    base_x, base_y = 80, 280
    base_w, base_h = 440, 40

    f.append(rect(base_x, base_y, base_w, base_h, fill="#cbd5e1", stroke=INK, sw=2))
    f.append(text(base_x + base_w / 2, base_y + 25, "Основа радіатора (температура T_b)", size=13, bold=True, color=INK, anchor="middle"))

    fin_w = 24
    fin_h = 140
    fin_gaps = [base_x + 30, base_x + 140, base_x + 250, base_x + 360]

    for fx in fin_gaps:
        f.append(rect(fx, base_y - fin_h, fin_w, fin_h, fill="#fee2e2", stroke=INK, sw=1.8))
        f.append(rect(fx, base_y - fin_h, fin_w, 40, fill="#e0f2fe", stroke='none'))
        f.append(rect(fx, base_y - fin_h, fin_w, fin_h, fill='none', stroke=INK, sw=1.8))
        f.append(varrow(fx - 15, base_y - 70, fx - 2, base_y - 70, color=WARN, sw=1.8, head=8))
        f.append(varrow(fx + fin_w + 15, base_y - 70, fx + fin_w + 2, base_y - 70, color=WARN, sw=1.8, head=8))

    u_x1 = fin_gaps[0] + fin_w
    u_x2 = fin_gaps[1]
    f.append(line(u_x1, base_y - 5, u_x2, base_y - 5, color=POS, sw=3.5))
    f.append(text((u_x1 + u_x2) / 2, base_y - 15, "площа основи A_u (температура T_b)", size=11, bold=True, color=POS, anchor="middle"))

    f.append(text(fin_gaps[0] + fin_w / 2, base_y - fin_h - 15, "поверхня ребра A_f", size=11.5, bold=True, color=ACCENT, anchor="middle"))

    bx, by = 550, 100
    bw, bh = 250, 270
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx + bw / 2, by + 30, "Загальна ефективність η_o", size=14, bold=True, color=INK, anchor="middle"))

    f.append(text(bx + 20, by + 70, "Повний потік тепла:", size=12, bold=True, color=INK))
    f.append(text(bx + 20, by + 92, "Q_tot = h·[ A_u + η_f·A_f_tot ]·θ_b", size=12, italic=True, color=ACCENT))

    f.append(text(bx + 20, by + 135, "Формула масиву:", size=12, bold=True, color=INK))
    f.append(text(bx + 20, by + 160, "η_o = 1 - (A_f / A_tot)·(1 - η_f)", size=13, bold=True, color=POS))

    f.append(text(bx + 20, by + 200, "Де A_tot = A_u + A_f_tot", size=11.5, color=MUTED))
    f.append(text(bx + 20, by + 220, "Якщо η_f = 1 (ідеальне),", size=11.5, color=MUTED))
    f.append(text(bx + 20, by + 240, "то й η_o = 100%", size=11.5, color=MUTED))

    f.append(varrow(base_x + base_w / 2, base_y + 90, base_x + base_w / 2, base_y + 45, color=NEG, sw=4.0, head=14))
    f.append(text(base_x + base_w / 2, base_y + 110, "Приплив тепла від деталі Q_in", size=13, bold=True, color=NEG, anchor="middle"))

    render(os.path.join(IMG, 'fin-vs-array.svg'), W, H, "".join(f))


if __name__ == '__main__':
    fig_fin_heat_balance()
    fig_temperature_profile()
    fig_fin_efficiency_curve()
    fig_fin_vs_array()
    print("Фігури згенеровано у ./img/")
