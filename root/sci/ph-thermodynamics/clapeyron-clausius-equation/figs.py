# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — P-T діаграма фазових переходів (звичайна і аномальна)
# ════════════════════════════════════════════════════════════════════════════
def fig_pt_diagram():
    W, H = 780, 520
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 30, "P-T діаграма фазового рівноваженого стану речовини", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 440
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Температура T", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 20, 45, "Тиск P", size=12.5, bold=True, color=DARK, anchor="end"))

    # Потрійна точка T_t, P_t
    xt, yt = 260, 310

    # Критична точка C
    xc, yc = 620, 110

    # Лінія сублімації (Тверде тіло -> Пара)
    f.append(svg_path("M 110 420 Q 180 380 260 310", stroke="#e67e22", sw=3.0))

    # Лінія випаровування (Рідина -> Пара)
    f.append(svg_path("M 260 310 Q 420 250 620 110", stroke="#2980b9", sw=3.0))

    # Лінія плавлення звичайна (dP/dT > 0, dV > 0)
    f.append(svg_path("M 260 310 Q 310 200 370 70", stroke="#27ae60", sw=3.0))

    # Лінія плавлення аномальна (вода/лід, dP/dT < 0, dV < 0)
    f.append(svg_path("M 260 310 Q 230 200 205 70", stroke="#c0392b", sw=3.0, dash="6 3"))

    # Підписи фазових областей
    f.append(text(150, 200, "Тверда фаза", size=14, bold=True, color="#2c3e50", anchor="middle"))
    f.append(text(150, 220, "(Кристал)", size=11, color=MUTED, anchor="middle"))

    f.append(text(430, 140, "Рідина", size=14, bold=True, color="#1b4f72", anchor="middle"))

    f.append(text(480, 360, "Газоподібна фаза", size=14, bold=True, color="#d35400", anchor="middle"))
    f.append(text(480, 380, "(Пара)", size=11, color=MUTED, anchor="middle"))

    # Потрійна точка
    f.append(circle(xt, yt, 6, fill="#8e44ad", stroke="#ffffff", sw=1.5))
    f.append(line(xt, yt, xt, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(xt, yt, ox, yt, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(xt, oy + 16, "T_t", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox - 10, yt + 4, "P_t", size=11, color=MUTED, anchor="end"))
    f.append(text(xt + 12, yt + 18, "Потрійна точка (T_t, P_t)", size=11.5, bold=True, color="#8e44ad", anchor="start"))

    # Критична точка
    f.append(circle(xc, yc, 6, fill="#c0392b", stroke="#ffffff", sw=1.5))
    f.append(line(xc, yc, xc, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(xc, yc, ox, yc, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(xc, oy + 16, "T_c", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox - 10, yc + 4, "P_c", size=11, color=MUTED, anchor="end"))
    f.append(text(xc - 12, yc - 12, "Критична точка C", size=11.5, bold=True, color="#c0392b", anchor="end"))

    # Легенда та математичний підпис
    f.append(rect(430, 405, 330, 100, fill="#f8f9f9", stroke=MUTED, sw=1.0, rx=4))
    f.append(line(445, 422, 470, 422, color="#2980b9", sw=2.5))
    f.append(text(480, 426, "Випаровування: dP/dT = L_vap / (T·ΔV) > 0", size=10.5, color=INK))

    f.append(line(445, 442, 470, 442, color="#e67e22", sw=2.5))
    f.append(text(480, 446, "Сублімація: dP/dT = L_sub / (T·ΔV) > 0", size=10.5, color=INK))

    f.append(line(445, 462, 470, 462, color="#27ae60", sw=2.5))
    f.append(text(480, 466, "Плавлення (звич.): dP/dT > 0 (ΔV > 0)", size=10.5, color=INK))

    f.append(line(445, 482, 470, 482, color="#c0392b", sw=2.5, dash="4 2"))
    f.append(text(480, 486, "Плавлення вологи/льоду: dP/dT < 0 (ΔV < 0)", size=10.5, color=INK))

    # Стрілочки підписів ліній
    f.append(text(285, 120, "Плавлення (вода: dP/dT < 0)", size=10, bold=True, color="#c0392b", anchor="end"))
    f.append(text(340, 100, "Плавлення (звичайне)", size=10, bold=True, color="#27ae60", anchor="start"))

    return f

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Гіббсів потенціал G(T) для переходів I роду
# ════════════════════════════════════════════════════════════════════════════
def fig_gibbs_transition():
    W, H = 780, 460
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 30, "Термодинамічний потенціал Гіббса G(T) при фазовому переході I роду", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 400
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Температура T", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 15, 35, "Потенціал G", size=12.5, bold=True, color=DARK, anchor="end"))

    # Точка фазового переходу T_c
    xc = 360
    yc = 220

    # Крива G1(T) — фаза 1 (наприклад, рідка або тверда)
    f.append(svg_path("M 120 120 Q 240 160 360 220 Q 480 280 600 350", stroke="#2980b9", sw=3.0))

    # Крива G2(T) — фаза 2 (наприклад, газова)
    f.append(svg_path("M 140 70 Q 250 130 360 220 Q 470 310 580 400", stroke="#e67e22", sw=3.0))

    # Пунктири для метастабільних станів
    f.append(svg_path("M 360 220 Q 480 280 600 350", stroke="#2980b9", sw=2.0, fill="none", dash="4 3"))
    f.append(svg_path("M 140 70 Q 250 130 360 220", stroke="#e67e22", sw=2.0, fill="none", dash="4 3"))

    # Суцільні лінії стійких фаз
    # При T < Tc стійка фаза 1 (нижчий G)
    f.append(svg_path("M 120 120 Q 240 160 360 220", stroke="#1b4f72", sw=4.0))
    # При T > Tc стійка фаза 2 (нижчий G)
    f.append(svg_path("M 360 220 Q 470 310 580 400", stroke="#d35400", sw=4.0))

    # Позначення T_c
    f.append(line(xc, yc, xc, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(xc, yc, ox, yc, color=MUTED, sw=1.0, dash="3 3"))
    f.append(circle(xc, yc, 6, fill="#8e44ad", stroke="#ffffff", sw=1.5))

    f.append(text(xc, oy + 16, "T_c (Температура переходу)", size=11.5, bold=True, color="#8e44ad", anchor="middle"))
    f.append(text(ox - 10, yc + 4, "G_c", size=11, color=MUTED, anchor="end"))

    # Підписи нахилу dG/dT = -S (розміщено з боків від кривих)
    f.append(text(110, 250, "Фаза 1: стійка при T < T_c", size=11.5, bold=True, color="#1b4f72", anchor="start"))
    f.append(text(110, 268, "(∂G₁/∂T)_P = -S₁", size=10.5, color="#2980b9", anchor="start"))

    f.append(text(600, 360, "Фаза 2: стійка при T > T_c", size=11.5, bold=True, color="#d35400", anchor="start"))
    f.append(text(600, 378, "(∂G₂/∂T)_P = -S₂", size=10.5, color="#e67e22", anchor="start"))

    # Інформаційна рамка вгорі праворуч
    f.append(rect(430, 65, 330, 120, fill="#f8f9f9", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(445, 87, "Ознаки фазового переходу I роду:", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(445, 107, "• Потенціал G(T,P) є неперервним: G₁ = G₂", size=10.5, color=INK, anchor="start"))
    f.append(text(445, 125, "• Перші похідні мають стрибок:", size=10.5, color=INK, anchor="start"))
    f.append(text(460, 145, "ΔS = S₂ - S₁ = L / T_c ≠ 0  (ентропія)", size=10.5, bold=True, color="#c0392b", anchor="start"))
    f.append(text(460, 165, "ΔV = V₂ - V₁ ≠ 0            (об'єм)", size=10.5, bold=True, color="#27ae60", anchor="start"))

    return f

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Елементарний цикл Карно у двофазній області
# ════════════════════════════════════════════════════════════════════════════
def fig_carnot_phase_cycle():
    W, H = 780, 500
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 30, "Нескінченно малий цикл Карно у двофазній області співіснування", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 430
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Об'єм V", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 20, 45, "Тиск P", size=12.5, bold=True, color=DARK, anchor="end"))

    # Двофазна купоподібна крива (бінодаль)
    f.append(svg_path("M 140 430 Q 360 120 400 120 Q 440 120 660 430", stroke="#7f8c8d", sw=2.0, fill="#f2f4f4"))
    f.append(text(400, 100, "Критична точка", size=11, bold=True, color="#7f8c8d", anchor="middle"))
    f.append(text(400, 275, "Двофазна область (Рідина + Пара)", size=13, bold=True, color="#95a5a6", anchor="middle"))

    # Верхня ізотерма T + dT (тиск P + dP)
    y_top = 160
    x1_top = 220
    x2_top = 580

    # Нижня ізотерма T (тиск P)
    y_bot = 220
    x1_bot = 195
    x2_bot = 605

    # Зафарбування циклу
    f.append(polygon([(x1_top, y_top), (x2_top, y_top), (x2_bot, y_bot), (x1_bot, y_bot)], fill="#ebf5fb", stroke="none"))

    # Верхня горизонтальна ізотерма (двофазна частина)
    f.append(line(x1_top, y_top, x2_top, y_top, color="#c0392b", sw=3.0))
    # Нижня горизонтальна ізотерма (двофазна частина)
    f.append(line(x1_bot, y_bot, x2_bot, y_bot, color="#2980b9", sw=3.0))

    # Бічні адіабати
    f.append(line(x1_bot, y_bot, x1_top, y_top, color="#27ae60", sw=2.5))
    f.append(line(x2_top, y_top, x2_bot, y_bot, color="#8e44ad", sw=2.5))

    # Стрілочки напрямку циклу
    f.append(polygon([(390, y_top - 5), (405, y_top), (390, y_top + 5)], fill="#c0392b"))
    f.append(polygon([(410, y_bot + 5), (395, y_bot), (410, y_bot - 5)], fill="#2980b9"))

    # Лінії тиску на осі Y
    f.append(line(x1_top, y_top, ox, y_top, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(x1_bot, y_bot, ox, y_bot, color=MUTED, sw=1.0, dash="3 3"))

    f.append(text(ox - 10, y_top + 4, "P + dP", size=11, bold=True, color="#c0392b", anchor="end"))
    f.append(text(ox - 10, y_bot + 4, "P", size=11, bold=True, color="#2980b9", anchor="end"))

    # Опори об'єму V_liq та V_vap
    f.append(line(x1_bot, y_bot, x1_bot, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(x2_bot, y_bot, x2_bot, oy, color=MUTED, sw=1.0, dash="3 3"))

    f.append(text(x1_bot, oy + 16, "V_1 (Рідина)", size=11, color=MUTED, anchor="middle"))
    f.append(text(x2_bot, oy + 16, "V_2 (Пара)", size=11, color=MUTED, anchor="middle"))

    # Двостороння стрілка ΔV
    f.append(line(x1_bot + 10, 340, x2_bot - 10, 340, color=DARK, sw=1.5))
    f.append(polygon([(x1_bot + 15, 336), (x1_bot, 340), (x1_bot + 15, 344)], fill=DARK))
    f.append(polygon([(x2_bot - 15, 336), (x2_bot, 340), (x2_bot - 15, 344)], fill=DARK))
    f.append(text((x1_bot + x2_bot) // 2, 332, "ΔV = V_2 - V_1", size=11.5, bold=True, color=DARK, anchor="middle"))

    # Підписи тепла та роботи
    f.append(text(400, y_top - 15, "Підведення тепла: Q_H = L  (при T + dT)", size=11, bold=True, color="#c0392b", anchor="middle"))
    f.append(text(400, y_bot + 22, "Відведення тепла: Q_C = L - dL  (при T)", size=11, bold=True, color="#2980b9", anchor="middle"))

    f.append(text(400, 185, "dW = dP · ΔV", size=12, bold=True, color="#1b4f72", anchor="middle"))

    # Блок-схема підсумку у правому нижньому кутку
    f.append(rect(460, 420, 250, 65, fill="#f8f9f9", stroke="#c0392b", sw=1.5, rx=4))
    f.append(text(475, 442, "ККД: η = dW/Q_H = dT/T", size=10.5, color=INK))
    f.append(text(475, 466, "⇒ dP / dT = L / (T · ΔV)", size=12.5, bold=True, color="#c0392b"))

    return f

# ════════════════════════════════════════════════════════════════════════════
# Основний виклик генерації
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    render(os.path.join(OUT, "phase-diagram-pt.svg"), 780, 520, *fig_pt_diagram())
    print("Generated phase-diagram-pt.svg")

    render(os.path.join(OUT, "gibbs-potential-transition.svg"), 780, 460, *fig_gibbs_transition())
    print("Generated gibbs-potential-transition.svg")

    render(os.path.join(OUT, "carnot-phase-cycle.svg"), 780, 500, *fig_carnot_phase_cycle())
    print("Generated carnot-phase-cycle.svg")
