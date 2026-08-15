# -*- coding: utf-8 -*-
"""Фігури до теми «Турбулентність».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

WARM = "#e67e22"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=1.8, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def varrow(x1, y1, x2, y2, color=LINE, sw=1.8, head=9):
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    bx, by = x2 - ux * head, y2 - uy * head
    nx, ny = -uy, ux
    p_head = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
              % (x2, y2, bx + nx * head * 0.4, by + ny * head * 0.4,
                 bx - nx * head * 0.4, by - ny * head * 0.4, color))
    return line(x1, y1, x2, y2, color=color, sw=sw) + p_head


def draw_vortex(cx, cy, r, color=NEG, sw=2.0, clockwise=True):
    """Малює закручену спіралеподібну лінію вихору."""
    pts = []
    turns = 1.3
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        angle = t * turns * 2 * math.pi * (1 if clockwise else -1)
        rad = r * (0.2 + 0.8 * t)
        x = cx + rad * math.cos(angle)
        y = cy + rad * math.sin(angle)
        pts.append((x, y))
    p_str = " ".join("%.1f,%.1f" % pt for pt in pts)
    out = ['<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (p_str, color, sw)]
    # стрілка на кінці
    x_end, y_end = pts[-1]
    x_prev, y_prev = pts[-3]
    dx, dy = x_end - x_prev, y_end - y_prev
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    head_size = 7
    bx, by = x_end - ux * head_size, y_end - uy * head_size
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
               % (x_end, y_end, bx + nx * head_size * 0.4, by + ny * head_size * 0.4,
                  bx - nx * head_size * 0.4, by - ny * head_size * 0.4, color))
    return "".join(out)


# ── 1. Енергетичний каскад Річардсона — Колмогорова ────────────────────────
def fig_cascade():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Енергетичний каскад Річардсона — Колмогорова", size=18, bold=True))
    f.append(text(W / 2, 48, "передавання енергії від великомасштабного збурення до в'язкої дисипації", size=12.5, color=MUTED))

    # Стовпчик 1: Інжекція енергії (великий вихор)
    b1, w1, h1 = textbox(150, 220, "Великий вихор L\n(інжекція енергії E)", size=13, pad=12, fill="#eef2ff", stroke=NEG, bold=True)
    f.append(b1)
    f.append(draw_vortex(150, 140, 36, color=NEG, sw=2.5, clockwise=True))
    f.append(text(150, 310, "Масштаб: L ~ 1 м..100 м", size=12, color=INK))
    f.append(text(150, 330, "Re_L >> 1 (інерційний рух)", size=11.5, color=MUTED))

    # Стрілка 1->2
    f.append(varrow(250, 220, 310, 220, color=LINE, sw=2.2))
    f.append(text(280, 205, "дроблення", size=11, color=MUTED))

    # Стовпчик 2: Інерційний інтервал (середні вихори)
    b2, w2, h2 = textbox(420, 220, "Інерційний інтервал\n(проміжні вихори r)", size=13, pad=12, fill="#f4f6f8", stroke=LINE, bold=True)
    f.append(b2)
    f.append(draw_vortex(390, 140, 20, color=INK, sw=2.0, clockwise=False))
    f.append(draw_vortex(450, 140, 16, color=INK, sw=1.8, clockwise=True))
    f.append(text(420, 310, "Масштаби: η << r << L", size=12, color=INK))
    f.append(text(420, 330, "Каскад без втрат енергії ε", size=11.5, color=MUTED))

    # Стрілка 2->3
    f.append(varrow(530, 220, 590, 220, color=LINE, sw=2.2))
    f.append(text(560, 205, "перенос ε", size=11, color=MUTED))

    # Стовпчик 3: Дисипативний інтервал (дрібні вихори)
    b3, w3, h3 = textbox(700, 220, "Дисипація η\n(перетворення в тепло)", size=13, pad=12, fill="#fef2f2", stroke=POS, bold=True)
    f.append(b3)
    f.append(draw_vortex(680, 140, 9, color=POS, sw=1.5, clockwise=True))
    f.append(draw_vortex(710, 140, 7, color=POS, sw=1.3, clockwise=False))
    f.append(draw_vortex(695, 160, 6, color=POS, sw=1.2, clockwise=True))
    f.append(text(700, 310, "Масштаб Колмогорова: η", size=12, color=INK))
    f.append(text(700, 330, "Re_η ~ 1 (в'язке згасання)", size=11.5, color=MUTED))

    # Нижня узагальнююча шкала
    f.append(line(80, 390, 760, 390, color=LINE, sw=2.0))
    f.append(varrow(750, 390, 760, 390, color=LINE, sw=2.0))
    f.append(text(420, 415, "Напрямок передачі енергії у тривимірному каскаді (від великого k крізь k^-5/3 до дисипації)", size=12, color=INK, bold=True))
    f.append(text(420, 435, "Швидкість дисипації ε = const уздовж усього інерційного інтервалу", size=11.5, color=MUTED))

    render(os.path.join(IMG, "cascade-richardson.svg"), W, H, "".join(f))


# ── 2. Енергетичний спектр Колмогорова ──────────────────────────────────────
def fig_spectrum():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Спектральний розподіл кінетичної енергії E(k)", size=18, bold=True))
    f.append(text(W / 2, 48, "подвійний логарифмічний масштаб: log E(k) залежно від log k", size=12.5, color=MUTED))

    # Осі
    ox, oy = 100, 400
    w_axis, h_axis = 680, 300
    f.append(varrow(ox, oy, ox + w_axis + 20, oy, color=INK, sw=2.0))
    f.append(varrow(ox, oy, ox, oy - h_axis - 20, color=INK, sw=2.0))
    f.append(text(ox + w_axis + 10, oy + 24, "Хвильове число k (log scale)", size=12.5, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - h_axis - 10, "E(k)", size=14, italic=True, color=INK, bold=True, anchor="middle"))

    # Зони на графіку
    # 1. Енерговмісний діапазон (k ~ 1/L)
    x1 = ox + 40
    x2 = ox + 220
    x3 = ox + 520
    x4 = ox + 650

    f.append(rect(ox + 10, oy - h_axis, x2 - ox - 10, h_axis, fill="#eff6ff", stroke="none", sw=0))
    f.append(rect(x2, oy - h_axis, x3 - x2, h_axis, fill="#f8fafc", stroke="none", sw=0))
    f.append(rect(x3, oy - h_axis, x4 - x3, h_axis, fill="#fef2f2", stroke="none", sw=0))

    # Вертикальні пунктири
    f.append(line(x2, oy, x2, oy - h_axis, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(x3, oy, x3, oy - h_axis, color=MUTED, sw=1.2, dash="4 4"))

    f.append(text((ox + 10 + x2) / 2, oy - h_axis + 20, "Енерговмісні вихори", size=12, color=NEG, bold=True))
    f.append(text((ox + 10 + x2) / 2, oy - h_axis + 38, "k ~ 1/L", size=11, color=MUTED))

    f.append(text((x2 + x3) / 2, oy - h_axis + 20, "Інерційний інтервал", size=13, color=INK, bold=True))
    f.append(text((x2 + x3) / 2, oy - h_axis + 38, "Закон Колмогорова: E(k) ~ k^(-5/3)", size=12, color=NEG, bold=True))

    f.append(text((x3 + x4) / 2, oy - h_axis + 20, "Дисипація", size=12, color=POS, bold=True))
    f.append(text((x3 + x4) / 2, oy - h_axis + 38, "k ≥ k_d ~ 1/η", size=11, color=MUTED))

    # Крива E(k)
    # Зростає до піку, потім пряма лінія зі нахилом -5/3 у лог-масштабі, потім стрімке падіння
    pts = []
    # Зростання
    for x_curr in range(ox + 15, x2, 5):
        t = (x_curr - (ox + 15)) / (x2 - (ox + 15))
        y_curr = oy - (40 + 200 * math.sin(t * math.pi / 2))
        pts.append((x_curr, y_curr))
    # Нахил -5/3 (лінійне спадання в лог координатах)
    y_start = pts[-1][1]
    y_end = oy - 90
    for x_curr in range(x2, x3, 5):
        t = (x_curr - x2) / (x3 - x2)
        y_curr = y_start + t * (y_end - y_start)
        pts.append((x_curr, y_curr))
    # Стрімке в'язке згасання
    y_start2 = pts[-1][1]
    for x_curr in range(x3, x4 + 10, 5):
        t = (x_curr - x3) / (x4 + 10 - x3)
        y_curr = y_start2 + (oy - 10 - y_start2) * (t ** 2.2)
        pts.append((x_curr, y_curr))

    p_str = " ".join("%.1f,%.1f" % pt for pt in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (p_str, NEG))

    # Трикутник нахилу -5/3
    tx1, ty1 = x2 + 100, y_start + 0.33 * (y_end - y_start)
    tx2, ty2 = tx1 + 80, ty1
    tx3, ty3 = tx2, ty1 + 48
    f.append(polyline([(tx1, ty1), (tx2, ty2), (tx3, ty3), (tx1, ty1)], color=POS, sw=1.8))
    f.append(text(tx1 + 40, ty1 - 8, "d(log k)", size=11, color=POS, anchor="middle"))
    f.append(text(tx2 + 28, ty1 + 24, "-5/3", size=12.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "energy-spectrum.svg"), W, H, "".join(f))


# ── 3. Профіль пристінної турбулентності u+(y+) ─────────────────────────────
def fig_wall_profile():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Універсальний профіль швидкості пристінної турбулентності", size=18, bold=True))
    f.append(text(W / 2, 48, "залежність безрозмірної швидкості u+ від відстані до стінки y+ у логарифмічній шкалі", size=12.5, color=MUTED))

    ox, oy = 100, 420
    w_axis, h_axis = 680, 320
    f.append(varrow(ox, oy, ox + w_axis + 20, oy, color=INK, sw=2.0))
    f.append(varrow(ox, oy, ox, oy - h_axis - 15, color=INK, sw=2.0))

    f.append(text(ox + w_axis + 10, oy + 24, "Відстань від стінки y+ (log scale)", size=12.5, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - h_axis - 5, "u+", size=14, italic=True, color=INK, bold=True, anchor="middle"))

    # Вертикальні межі зон: y+ = 5, y+ = 30
    x_sublayer = ox + 150   # y+ = 5
    x_buffer   = ox + 320   # y+ = 30
    x_log      = ox + 620   # y+ ~ 1000

    f.append(rect(ox + 2, oy - h_axis, x_sublayer - ox - 2, h_axis, fill="#f0fdf4", stroke="none", sw=0))
    f.append(rect(x_sublayer, oy - h_axis, x_buffer - x_sublayer, h_axis, fill="#fffbe6", stroke="none", sw=0))
    f.append(rect(x_buffer, oy - h_axis, x_log - x_buffer, h_axis, fill="#eff6ff", stroke="none", sw=0))

    f.append(line(x_sublayer, oy, x_sublayer, oy - h_axis, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(x_buffer, oy, x_buffer, oy - h_axis, color=MUTED, sw=1.2, dash="4 4"))

    # Підписи зон
    f.append(text((ox + x_sublayer) / 2, oy - h_axis + 22, "В'язкий підшар", size=12, color=FIELD, bold=True))
    f.append(text((ox + x_sublayer) / 2, oy - h_axis + 40, "u+ = y+ (y+ < 5)", size=11, color=MUTED))

    f.append(text((x_sublayer + x_buffer) / 2, oy - h_axis + 22, "Буферний шар", size=12, color=WARM, bold=True))
    f.append(text((x_sublayer + x_buffer) / 2, oy - h_axis + 40, "5 < y+ < 30", size=11, color=MUTED))

    f.append(text((x_buffer + x_log) / 2, oy - h_axis + 22, "Логарифмічний шар (Закон стіни)", size=13, color=NEG, bold=True))
    f.append(text((x_buffer + x_log) / 2, oy - h_axis + 40, "u+ = (1/κ)·ln(y+) + B   (κ ≈ 0.41, B ≈ 5.0)", size=12, color=NEG, bold=True))

    # Лінія u+ = y+ (лінійна у вихідних координатах -> вигинається в лог шкалі)
    pts_sublayer = []
    for x_curr in range(ox + 5, x_sublayer + 30, 5):
        t = (x_curr - ox) / (x_sublayer - ox)
        # лінійна залежність u+ ~ y+
        y_curr = oy - 40 * t * 4.5
        pts_sublayer.append((x_curr, y_curr))

    # Логарифмічний профіль
    pts_log = []
    for x_curr in range(x_sublayer - 10, ox + w_axis - 20, 5):
        t = (x_curr - x_sublayer) / (w_axis - (x_sublayer - ox))
        # логарифмічна крива
        y_curr = oy - (180 + 110 * math.log(1 + 4 * t))
        pts_log.append((x_curr, y_curr))

    p_sub = " ".join("%.1f,%.1f" % pt for pt in pts_sublayer)
    p_log = " ".join("%.1f,%.1f" % pt for pt in pts_log)

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 4"/>' % (p_sub, FIELD))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (p_log, NEG))

    # Точки-позначки на осі
    f.append(line(x_sublayer, oy - 4, x_sublayer, oy + 4, color=INK, sw=2.0))
    f.append(text(x_sublayer, oy + 20, "y+ = 5", size=11.5, color=INK, bold=True))

    f.append(line(x_buffer, oy - 4, x_buffer, oy + 4, color=INK, sw=2.0))
    f.append(text(x_buffer, oy + 20, "y+ = 30", size=11.5, color=INK, bold=True))

    render(os.path.join(IMG, "boundary-layer-wall.svg"), W, H, "".join(f))


# ── 4. Порівняння підходів чисельного моделювання (RANS, LES, DNS) ─────────
def fig_cfd_methods():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Порівняння методів моделювання турбулентності (CFD)", size=18, bold=True))
    f.append(text(W / 2, 48, "розподіл між моделюванням та чисельним розв'язанням вихорів", size=12.5, color=MUTED))

    def draw_method_box(cx, cy, title, subtitle, modeled_text, resolved_text, cost_text, fill_col, border_col):
        g = []
        b, w, h = textbox(cx, cy, "%s\n%s" % (title, subtitle), size=14, pad=12, fill=fill_col, stroke=border_col, bold=True)
        g.append(b)
        
        # Блок роздільної здатності
        g.append(rect(cx - 100, cy + 50, 200, 30, fill="#ffffff", stroke=LINE, sw=1.2))
        # Пропорція розв'язаного vs змодельованого
        if title == "RANS":
            w_res = 0
        elif title == "LES":
            w_res = 160
        else: # DNS
            w_res = 200
            
        if w_res > 0:
            g.append(rect(cx - 100, cy + 50, w_res, 30, fill=FIELD, stroke="none", sw=0))
        if 200 - w_res > 0:
            g.append(rect(cx - 100 + w_res, cy + 50, 200 - w_res, 30, fill=POS, stroke="none", sw=0))
            
        g.append(text(cx, cy + 70, "Змодельовано: %s" % modeled_text, size=11, color=INK, bold=True))
        g.append(text(cx, cy + 115, "Розв'язуються: %s" % resolved_text, size=11.5, color=INK))
        g.append(text(cx, cy + 135, "Обчислювальна ціна: %s" % cost_text, size=11.5, color=border_col, bold=True))
        return "".join(g)

    f.append(draw_method_box(160, 160, "RANS", "Рівняння Рейнольдса", "100% вихорів", "лише середній потік", "Низька (1x)", "#f4f6f8", LINE))
    f.append(draw_method_box(420, 160, "LES", "Метод великих вихорів", "~10-20% дрібних", "великі вихори > Δ", "Середня / Висока (10²x)", "#eff6ff", NEG))
    f.append(draw_method_box(680, 160, "DNS", "Пряме моделювання", "0% (без моделей)", "100% (до Колмогорова η)", "Екстремальна (10⁶x..10⁹x)", "#fef2f2", POS))

    # Пояснювальна легенда знизу
    f.append(rect(80, 370, 680, 80, fill="#fafafa", stroke=LINE, sw=1.2))
    f.append(rect(100, 390, 20, 16, fill=FIELD, stroke="none", sw=0))
    f.append(text(130, 403, "Розв'язаний спектр (безпосередній розрахунок Нав'є — Стокса)", size=12, color=INK, anchor="start"))

    f.append(rect(100, 420, 20, 16, fill=POS, stroke="none", sw=0))
    f.append(text(130, 433, "Змодельований спектр (турбулентна в'язкість / підсіткові моделі)", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "rans-les-dns.svg"), W, H, "".join(f))



if __name__ == "__main__":
    fig_cascade()
    fig_spectrum()
    fig_wall_profile()
    fig_cfd_methods()
    print("Успішно згенеровано 4 фігури в ./img/")
