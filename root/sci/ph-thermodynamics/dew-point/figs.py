# -*- coding: utf-8 -*-
"""Фігури до теми «Точка роси і конденсація».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Термодинамічна фазова P-T діаграма водяної пари ────────────────
def fig1_phase_diagram():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Фазова P-T діаграма водяної пари та Точка роси", size=16, bold=True))
    f.append(text(W / 2, 48, "Шляхи переходу ненасиченої пари у стан насичення: ізобарне охолодження та ізотермічне стиснення", size=12, color=MUTED))

    ox, oy = 90, H - 60
    gx_w, gy_h = 600, 290

    # Вісі
    f.append(arrow(ox, oy, ox + gx_w + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gy_h - 20, color=LINE, sw=1.8))

    f.append(text(ox + gx_w + 25, oy + 4, "Температура T (°C)", size=12, bold=True, anchor="start"))
    f.append(text(ox, oy - gy_h - 28, "Тиск пари p (кПа)", size=12, bold=True))

    # Крива насичення p_sat(T)
    sat_pts = []
    for step in range(50):
        t_val = step / 49.0
        x = ox + t_val * gx_w
        y = oy - 25 - 240 * math.exp(2.8 * (t_val - 1.0))
        sat_pts.append((x, y))

    for i in range(len(sat_pts) - 1):
        f.append(line(sat_pts[i][0], sat_pts[i][1], sat_pts[i+1][0], sat_pts[i+1][1], color="#1a73e8", sw=3.0))

    # Підписи областей фаз
    body_liq, _, _ = textbox(ox + 120, oy - gy_h + 50, "Рідка вода\n(конденсат)", size=12, bold=True, color="#1557b0", pad=6, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body_liq)

    body_vap, _, _ = textbox(ox + 420, oy - 70, "Ненасичена перегріта пара\n(p_v < p_sat)", size=12, bold=True, color="#b06000", pad=6, fill="#fef7e0", stroke="#fce8b2", sw=1.0)
    f.append(body_vap)

    # Точки станів: А (початковий), Б (точка роси), В (ізотермічна конденсація)
    xA, yA = ox + 450, oy - 110  # Початковий стан (T0, p_v0)
    xB, yB = ox + 265, oy - 110  # Перетин із кривою насичення при p = const (T_d, p_v0)
    xC, yC = ox + 450, oy - 215  # Перетин при T = const (T0, p_sat(T0))

    # Ізобарне охолодження (А -> Б)
    f.append(line(xA, yA, xB, yB, color="#d93025", sw=2.2, dash="5,5"))
    f.append(arrow(xA - 10, yA, xB + 15, yB, color="#d93025", sw=2.2))

    # Ізотермічне стиснення (А -> В)
    f.append(line(xA, yA, xC, yC, color="#34a853", sw=2.2, dash="5,5"))
    f.append(arrow(xA, yA - 10, xC, yC + 15, color="#34a853", sw=2.2))

    # Проекції температури на вісь X
    f.append(line(xB, yB, xB, oy, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(xA, yA, xA, oy, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(xB, yB, ox, yB, color=MUTED, sw=1.2, dash="3,3"))

    f.append(text(xB, oy + 18, "T_d (Точка роси)", size=11, bold=True, color="#d93025"))
    f.append(text(xA, oy + 18, "T_0 (Початкова T)", size=11, bold=True, color=INK))
    f.append(text(ox - 10, yB + 4, "p_v0", size=11, bold=True, anchor="end"))

    # Позначення точок А, Б, В
    f.append(circle(xA, yA, 6, fill="#f9ab00", stroke=INK, sw=1.5))
    f.append(text(xA + 12, yA + 14, "А (стан повітря)", size=11, bold=True))

    f.append(circle(xB, yB, 7, fill="#d93025", stroke=INK, sw=1.5))
    f.append(text(xB - 12, yB - 12, "Б (конденсація: T = T_d)", size=11, bold=True, color="#b31412", anchor="end"))

    f.append(circle(xC, yC, 6, fill="#34a853", stroke=INK, sw=1.5))
    f.append(text(xC + 12, yC - 8, "В (p_v = p_sat)", size=11, bold=True, color="#137333", anchor="start"))

    # Напис лінії насичення
    f.append(text(ox + 490, oy - 250, "Лінія насичення p_sat(T) (RH = 100%)", size=11, bold=True, color="#1557b0"))

    return render(os.path.join(IMG, "fig1-phase-diagram-dewpoint.svg"), W, H, *f)


# ── Фігура 2: Зародкоутворення крапель ──────────────────────────────────────
def fig2_droplet_nucleation():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Мікроскопічна фізика зародкоутворення крапель", size=16, bold=True))
    f.append(text(W / 2, 48, "Термодинамічний бар'єр Гіббса ΔG*, критичний радіус r_c та гетерогенні центри", size=12, color=MUTED))

    pw = 340
    ph = 300
    py = 68

    # --- Панель А: Термодинамічний потенціал зародка ---
    px1 = 28
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 22, "А. Гомогенний бар'єр у перенасиченій парі", size=13, bold=True, color=INK))

    ox1, oy1 = px1 + 45, py + ph / 2 + 20
    f.append(arrow(ox1, oy1 + 90, ox1, py + 45, color=LINE, sw=1.5))
    f.append(arrow(ox1, oy1, ox1 + 270, oy1, color=LINE, sw=1.5))
    f.append(text(ox1 + 280, oy1 + 4, "r (радіус)", size=11, bold=True))
    f.append(text(ox1 - 8, py + 40, "ΔG", size=11, bold=True))

    surf_pts = [(ox1 + r, oy1 - 0.22 * r**1.6) for r in range(0, 180, 5)]
    for i in range(len(surf_pts) - 1):
        f.append(line(surf_pts[i][0], surf_pts[i][1], surf_pts[i+1][0], surf_pts[i+1][1], color="#d93025", sw=1.5, dash="4,4"))
    f.append(text(ox1 + 175, oy1 - 85, "+Поверхня (~ r²)", size=10, color="#d93025"))

    vol_pts = [(ox1 + r, oy1 + 0.004 * r**2.2) for r in range(0, 180, 5)]
    for i in range(len(vol_pts) - 1):
        f.append(line(vol_pts[i][0], vol_pts[i][1], vol_pts[i+1][0], vol_pts[i+1][1], color="#1a73e8", sw=1.5, dash="4,4"))
    f.append(text(ox1 + 175, oy1 + 75, "−Об'єм (~ r³)", size=10, color="#1a73e8"))

    total_pts = []
    for r in range(0, 200, 4):
        val = 0.22 * r**1.6 - 0.004 * r**2.2
        total_pts.append((ox1 + r, oy1 - val))
    for i in range(len(total_pts) - 1):
        f.append(line(total_pts[i][0], total_pts[i][1], total_pts[i+1][0], total_pts[i+1][1], color="#34a853", sw=2.5))

    rc_x = ox1 + 78
    rc_y = oy1 - 58
    f.append(line(rc_x, oy1, rc_x, rc_y, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(ox1, rc_y, rc_x, rc_y, color=MUTED, sw=1.2, dash="3,3"))
    f.append(circle(rc_x, rc_y, 5, fill="#34a853", stroke=INK, sw=1.2))

    f.append(text(rc_x, oy1 + 16, "r_c", size=11, bold=True, color="#137333"))
    f.append(text(ox1 - 10, rc_y + 4, "ΔG*", size=11, bold=True, anchor="end", color="#137333"))

    f.append(text(rc_x - 30, rc_y - 12, "випаровування", size=9, color=MUTED))
    f.append(text(rc_x + 45, rc_y - 12, "ріст краплі", size=9, color="#137333", bold=True))

    # --- Панель Б: Гетерогенна конденсація ---
    px2 = 392
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 22, "Б. Зниження бар'єра на частинках і стінках", size=13, bold=True, color=INK))

    sub_y = py + 210
    f.append(rect(px2 + 30, sub_y, pw - 60, 25, fill="#e0e0e0", stroke=LINE, sw=1.5, rx=2))
    f.append(text(px2 + pw / 2, sub_y + 16, "Тверда поверхня / Аерозоль (пил)", size=11, color=MUTED))

    cx, cy, r_drop = px2 + pw / 2, sub_y - 20, 55
    f.append('<path d="M %f %f A %f %f 0 0 1 %f %f" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2.5"/>' % (cx - 50, sub_y, r_drop, r_drop, cx + 50, sub_y))

    f.append(line(cx + 50, sub_y, cx + 80, sub_y - 35, color="#d93025", sw=1.5))
    f.append(text(cx + 42, sub_y - 12, "θ", size=12, bold=True, color="#d93025"))

    body_comp, _, _ = textbox(px2 + pw / 2, py + 85, "Гомогенно (чисте повітря):\n  потрібне перенасичення RH > 300%\nГетерогенно (пил/поверхня):\n  конденсація при RH = 100%", size=11, bold=False, color=INK, pad=6, fill="#f4f6f8", stroke="#ccc", sw=1.0)
    f.append(body_comp)

    return render(os.path.join(IMG, "fig2-droplet-nucleation.svg"), W, H, *f)


# ── Фігура 3: Психрометрична діаграма ───────────────────────────────────────
def fig3_psychrometric_chart():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Психрометрична діаграма (Мольє i-x) і точкування точок станів", size=16, bold=True))
    f.append(text(W / 2, 48, "Визначення точки роси T_d та температури вологого термометра T_w за станом повітря", size=12, color=MUTED))

    ox, oy = 85, H - 60
    gx_w, gy_h = 610, 290

    f.append(arrow(ox, oy, ox + gx_w + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gy_h - 20, color=LINE, sw=1.8))

    f.append(text(ox + gx_w + 25, oy + 4, "Температура сухого термометра T_dry (°C)", size=12, bold=True, anchor="start"))
    f.append(text(ox, oy - gy_h - 28, "Влоговміст w (г/кг)", size=12, bold=True))

    rh100_pts = []
    for step in range(50):
        t = step / 49.0
        x = ox + t * gx_w
        y = oy - 15 - 250 * (t ** 2.2)
        rh100_pts.append((x, y))

    for i in range(len(rh100_pts) - 1):
        f.append(line(rh100_pts[i][0], rh100_pts[i][1], rh100_pts[i+1][0], rh100_pts[i+1][1], color="#1a73e8", sw=3.0))
    f.append(text(ox + 500, oy - 275, "RH = 100% (лінія насичення)", size=11, bold=True, color="#1557b0"))

    rh50_pts = []
    for step in range(50):
        t = step / 49.0
        x = ox + t * gx_w
        y = oy - 15 - 125 * (t ** 2.2)
        rh50_pts.append((x, y))

    for i in range(len(rh50_pts) - 1):
        f.append(line(rh50_pts[i][0], rh50_pts[i][1], rh50_pts[i+1][0], rh50_pts[i+1][1], color="#f9ab00", sw=2.0, dash="6,4"))
    f.append(text(ox + 540, oy - 145, "RH = 50%", size=11, bold=True, color="#b06000"))

    xA, yA = ox + 420, oy - 85
    f.append(circle(xA, yA, 6, fill="#d93025", stroke=INK, sw=1.5))
    f.append(text(xA + 12, yA + 16, "Стан A (T_dry = 25°C, RH = 50%)", size=11, bold=True, color="#b31412"))

    xB = ox + 276
    yB = yA
    f.append(line(xA, yA, xB, yB, color="#d93025", sw=2.0, dash="4,4"))
    f.append(circle(xB, yB, 6, fill="#d93025", stroke=INK, sw=1.5))
    f.append(text(xB - 10, yB - 10, "Б (T_d)", size=11, bold=True, color="#d93025", anchor="end"))

    xC = ox + 335
    yC = oy - 138
    f.append(line(xA, yA, xC, yC, color="#34a853", sw=2.0, dash="4,4"))
    f.append(circle(xC, yC, 6, fill="#34a853", stroke=INK, sw=1.5))
    f.append(text(xC - 8, yC - 10, "В (T_w)", size=11, bold=True, color="#137333", anchor="end"))

    f.append(line(xB, yB, xB, oy, color="#d93025", sw=1.2, dash="2,2"))
    f.append(line(xC, yC, xC, oy, color="#34a853", sw=1.2, dash="2,2"))
    f.append(line(xA, yA, xA, oy, color=INK, sw=1.2, dash="2,2"))

    f.append(text(xB, oy + 18, "T_d = 13.8°C", size=11, bold=True, color="#d93025"))
    f.append(text(xC, oy + 32, "T_w = 17.8°C", size=11, bold=True, color="#137333"))
    f.append(text(xA, oy + 18, "T_dry = 25.0°C", size=11, bold=True, color=INK))

    body_rel, _, _ = textbox(ox + 160, oy - 220, "Фундаментальне співвідношення:\n  T_d  ≤  T_w  ≤  T_dry\nРівність виконується лише при RH = 100%", size=11, bold=True, color=INK, pad=6, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body_rel)

    return render(os.path.join(IMG, "fig3-psychrometric-chart.svg"), W, H, *f)


# ── Фігура 4: Автоматична система запобігання конденсації ───────────────────
def fig4_condensation_prevention():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Автоматизована система контролю точки роси та запобігання конденсації", size=16, bold=True))
    f.append(text(W / 2, 46, "Алгоритм керування мікроконтролером з урахуванням запізнення та гістерезису", size=12, color=MUTED))

    bw, bh = 150, 110
    by = 80

    # Блок 1: Давачі
    bx1 = 35
    f.append(rect(bx1, by, bw, bh, fill="#e8f0fe", stroke="#1a73e8", sw=1.8, rx=8))
    f.append(text(bx1 + bw/2, by + 22, "Вимірювальні давачі", size=12, bold=True, color="#1557b0"))
    f.append(mtext(bx1 + bw/2, by + 50, ["• T_air (повітря)", "• RH (вологість)", "• T_surf (поверхня)"], size=10, color=INK, anchor="middle"))

    # Стрілка 1 -> 2
    f.append(arrow(bx1 + bw, by + bh/2, bx1 + bw + 35, by + bh/2, color=LINE, sw=2.0))

    # Блок 2: Мікроконтролер
    bx2 = bx1 + bw + 35
    f.append(rect(bx2, by, bw, bh, fill="#fef7e0", stroke="#f9ab00", sw=1.8, rx=8))
    f.append(text(bx2 + bw/2, by + 22, "Мікроконтролер MCU", size=12, bold=True, color="#b06000"))
    f.append(mtext(bx2 + bw/2, by + 50, ["Формула Магнуса:", "T_d = f(T_air, RH)", "ΔT = T_surf − T_d"], size=10, color=INK, anchor="middle"))

    # Стрілка 2 -> 3
    f.append(arrow(bx2 + bw, by + bh/2, bx2 + bw + 35, by + bh/2, color=LINE, sw=2.0))

    # Блок 3: Перевірка умови
    bx3 = bx2 + bw + 35
    f.append(rect(bx3, by, bw, bh, fill="#fce8e6", stroke="#ea4335", sw=1.8, rx=8))
    f.append(text(bx3 + bw/2, by + 22, "Перевірка умови", size=12, bold=True, color="#c5221f"))
    f.append(mtext(bx3 + bw/2, by + 50, ["ΔT < ΔT_margin ?", "(напр., 3.0 °C)", "РИЗИК КОНДЕНСАЦІЇ"], size=10, color="#d93025", anchor="middle"))

    # Стрілка 3 -> 4
    f.append(arrow(bx3 + bw, by + bh/2, bx3 + bw + 35, by + bh/2, color=LINE, sw=2.0))

    # Блок 4: Виконавчі органи
    bx4 = bx3 + bw + 35
    f.append(rect(bx4, by, bw, bh, fill="#e6f4ea", stroke="#34a853", sw=1.8, rx=8))
    f.append(text(bx4 + bw/2, by + 22, "Захисні актуатори", size=12, bold=True, color="#137333"))
    f.append(mtext(bx4 + bw/2, by + 50, ["• Нагрівач оптики", "• Вентиляція обдуву", "• Осушувач повітря"], size=10, color=INK, anchor="middle"))

    # Текстовий блок під актуаторами
    body_fb, _, _ = textbox(W / 2, by + bh + 30, "Зміна температури поверхні або вологості середовища (замкнений контур)", size=11, bold=True, color="#137333", pad=5, fill="#e6f4ea", stroke="#ceead6", sw=1.0)
    f.append(body_fb)

    # Зворотна петля нижче текстового блоку
    y_fb = by + bh + 70
    f.append(line(bx4 + bw/2, by + bh + 6, bx4 + bw/2, y_fb, color="#34a853", sw=1.8))
    f.append(line(bx4 + bw/2, y_fb, bx1 + bw/2, y_fb, color="#34a853", sw=1.8, dash="5,5"))
    f.append(arrow(bx1 + bw/2, y_fb, bx1 + bw/2, by + bh + 6, color="#34a853", sw=1.8))

    return render(os.path.join(IMG, "fig4-condensation-prevention.svg"), W, H, *f)


if __name__ == '__main__':
    fig1_phase_diagram()
    fig2_droplet_nucleation()
    fig3_psychrometric_chart()
    fig4_condensation_prevention()
    print("Всі 4 фігури успішно згенеровано у ./img/")
