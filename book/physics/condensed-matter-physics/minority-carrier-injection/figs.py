# -*- coding: utf-8 -*-
import sys
import os
import math

# Path to scripts/ folder at repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "img")

def draw_injection_pn_boundary():
    """Малюнок 1: Кордон p-n переходу при прямому зміщенні та розподіл інжектованих меншинних носіїв."""
    w, h = 800, 480
    out = []
    
    # Заголовок / рамка
    out.append(rect(10, 10, w - 20, h - 20, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(w / 2, 35, "Розподіл носіїв заряду в p-n переході при прямому зміщенні", size=16, bold=True, color=INK))
    
    # Області: p-область (ліворуч), Збіднена зона (центр), n-область (праворуч)
    x_p_end = 260
    x_dep_start = 260
    x_dep_end = 380
    x_n_start = 380
    y_top = 70
    y_bot = 420
    
    # Заливка областей
    out.append(rect(40, y_top, x_p_end - 40, y_bot - y_top, fill="#fdeded", stroke="#f5c6cb", sw=1, rx=0))
    out.append(rect(x_dep_start, y_top, x_dep_end - x_dep_start, y_bot - y_top, fill="#fff3cd", stroke="#ffeeba", sw=1, rx=0))
    out.append(rect(x_dep_end, y_top, w - 50 - x_dep_end, y_bot - y_top, fill="#e8f4f8", stroke="#b8daff", sw=1, rx=0))
    
    # Підписи областей
    out.append(text(150, 95, "p-область", size=15, bold=True, color="#721c24"))
    out.append(text(320, 95, "Збіднена\nзона (W)", size=13, bold=True, color="#856404"))
    out.append(text(550, 95, "n-область", size=15, bold=True, color="#0c5460"))
    
    # Межі
    out.append(line(x_dep_start, y_top, x_dep_start, y_bot, color="#e0a800", sw=1.5, dash="4,4"))
    out.append(line(x_dep_end, y_top, x_dep_end, y_bot, color="#e0a800", sw=1.5, dash="4,4"))
    out.append(line(320, y_top, 320, y_bot, color="#dc3545", sw=1.5, dash="2,2"))
    out.append(text(320, y_bot - 15, "Металургійна межа (x = 0)", size=11, color="#dc3545", italic=True))
    
    # Вісь X
    out.append(arrow(40, 360, w - 40, 360, color=INK, sw=1.5))
    out.append(text(w - 30, 365, "x", size=14, bold=True))
    
    # Рівноважні рівні
    y_eq_n = 340 # p_n0 рівноважна в n
    y_eq_p = 340 # n_p0 рівноважна в p
    out.append(line(x_dep_end, y_eq_n, w - 60, y_eq_n, color=MUTED, sw=1, dash="3,3"))
    out.append(text(w - 110, y_eq_n + 18, "p_n0 (рівноважні)", size=12, color=MUTED))
    
    out.append(line(50, y_eq_p, x_dep_start, y_eq_p, color=MUTED, sw=1, dash="3,3"))
    out.append(text(90, y_eq_p + 18, "n_p0 (рівноважні)", size=12, color=MUTED))
    
    # Експоненційний спад інжектованих дірок у n-області
    points_p = []
    y_inj_p0 = 140 # висока концентрація при x = x_dep_end (x_n = 0)
    L_p_px = 90.0 # масштабна дифузійна довжина у пікселях
    
    for px in range(int(x_dep_end), int(w - 60), 4):
        x_rel = px - x_dep_end
        val = (y_eq_n - y_inj_p0) * math.exp(-x_rel / L_p_px)
        py = y_eq_n - val
        points_p.append((px, py))
    
    path_p_str = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in points_p])
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_p_str, POS))
    
    # Точка межової концентрації p_n(0)
    out.append(circle(x_dep_end, y_inj_p0, 5, fill=POS, stroke="#ffffff", sw=1.5))
    out.append(text(x_dep_end + 15, y_inj_p0 - 5, "p_n(0) = p_n0 · exp(qV / kT)", size=12, bold=True, color=POS, anchor="start"))
    
    # Стрілка показує дифузійну довжину L_p
    x_Lp = x_dep_end + L_p_px
    y_Lp = y_eq_n - (y_eq_n - y_inj_p0) * math.exp(-1.0)
    out.append(line(x_dep_end, y_Lp, x_Lp, y_Lp, color=POS, sw=1.5, dash="2,2"))
    out.append(arrow(x_dep_end, y_Lp - 15, x_Lp, y_Lp - 15, color=POS, sw=1.5))
    out.append(arrow(x_Lp, y_Lp - 15, x_dep_end, y_Lp - 15, color=POS, sw=1.5))
    out.append(text(x_dep_end + L_p_px / 2, y_Lp - 25, "L_p = √(D_p · τ_p)", size=12, bold=True, color=POS))
    
    # Експоненційний спад інжектованих електронів у p-області
    points_n = []
    y_inj_n0 = 170 # інжектовані електрони при x = x_dep_start
    L_n_px = 80.0
    
    for px in range(int(x_dep_start), 50, -4):
        x_rel = x_dep_start - px
        val = (y_eq_p - y_inj_n0) * math.exp(-x_rel / L_n_px)
        py = y_eq_p - val
        points_n.append((px, py))
        
    path_n_str = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in points_n])
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_n_str, NEG))
    
    # Точка межової концентрації n_p(0)
    out.append(circle(x_dep_start, y_inj_n0, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    out.append(text(x_dep_start - 15, y_inj_n0 - 5, "n_p(0) = n_p0 · exp(qV / kT)", size=12, bold=True, color=NEG, anchor="end"))
    
    # Пояснювальні рамки
    tb_p, _, _ = textbox(565, 270, "Інжектовані дірки (Δp_n)\nДифундують углиб n-області\nРекомбінація за час τ_p", size=12, fill="#fff5f5", stroke=POS, pad=6)
    out.append(tb_p)
    
    tb_n, _, _ = textbox(150, 270, "Інжектовані електрони (Δn_p)\nДифундують углиб p-області\nРекомбінація за час τ_n", size=12, fill="#f0f4ff", stroke=NEG, pad=6)
    out.append(tb_n)

    return render(os.path.join(IMG_DIR, "injection-pn-boundary.svg"), w, h, "".join(out))


def draw_haynes_shockley_setup():
    """Малюнок 2: Схема експериментальної установки Гейнса — Шоклі."""
    w, h = 800, 440
    out = []
    
    out.append(rect(10, 10, w - 20, h - 20, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(w / 2, 32, "Принципова схема експерименту Гейнса — Шоклі (1949)", size=16, bold=True, color=INK))
    
    # Напівпровідниковий стрижень (Ge n-типу)
    rod_x = 120
    rod_y = 160
    rod_w = 560
    rod_h = 70
    out.append(rect(rod_x, rod_y, rod_w, rod_h, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    out.append(text(rod_x + rod_w / 2, rod_y + rod_h / 2 + 5, "Нейтральний напівпровідниковий зразок (Ge / Si n-типу)", size=13, bold=True, color="#334155"))
    
    # Джерелотягнучого поля E (Батарея між торцями)
    out.append(line(rod_x, rod_y + rod_h / 2, 60, rod_y + rod_h / 2, color=INK, sw=2))
    out.append(line(60, rod_y + rod_h / 2, 60, 310, color=INK, sw=2))
    out.append(line(rod_x + rod_w, rod_y + rod_h / 2, 740, rod_y + rod_h / 2, color=INK, sw=2))
    out.append(line(740, rod_y + rod_h / 2, 740, 310, color=INK, sw=2))
    
    # Схема батареї
    out.append(line(60, 310, 360, 310, color=INK, sw=2))
    out.append(line(740, 310, 440, 310, color=INK, sw=2))
    out.append(line(360, 295, 360, 325, color=POS, sw=3)) # +
    out.append(line(380, 302, 380, 318, color=NEG, sw=1.5))
    out.append(line(400, 295, 400, 325, color=POS, sw=3))
    out.append(line(420, 302, 420, 318, color=NEG, sw=1.5))
    out.append(line(440, 295, 440, 325, color=NEG, sw=3)) # -
    
    out.append(text(400, 345, "Протягувальне поле E (постійна напруга V_sweep)", size=12, bold=True, color=INK))
    out.append(plus(330, 310, r=8))
    out.append(minus(470, 310, r=8))
    
    # Внутрішнє електричне поле E
    out.append(arrow(rod_x + 50, rod_y - 20, rod_x + rod_w - 50, rod_y - 20, color=FIELD, sw=2.5))
    out.append(text(rod_x + rod_w / 2, rod_y - 32, "Електричне поле E_sweep →", size=13, bold=True, color=FIELD))
    
    # Інжекторний контакт (Емітер)
    x_emit = rod_x + 90
    out.append(line(x_emit, rod_y - 5, x_emit, rod_y + 15, color=POS, sw=3))
    out.append(polygon_head(x_emit, rod_y + 15))
    out.append(line(x_emit, rod_y - 5, x_emit, rod_y - 45, color=POS, sw=2))
    out.append(circle(x_emit, rod_y - 45, 4, fill=POS, stroke=POS, sw=1))
    
    tb_em, _, _ = textbox(x_emit, rod_y - 75, "Короткий імпульс\nін'єкції (Емітер)", size=11, fill="#fdeded", stroke=POS, pad=5)
    out.append(tb_em)
    
    # Колекторний контакт (Детектор)
    x_coll = rod_x + 430
    out.append(line(x_coll, rod_y - 5, x_coll, rod_y + 15, color=NEG, sw=3))
    out.append(polygon_head(x_coll, rod_y + 15))
    out.append(line(x_coll, rod_y - 5, x_coll, rod_y - 45, color=NEG, sw=2))
    
    tb_col, _, _ = textbox(x_coll + 40, rod_y - 75, "Збиральний точковий\nконтакт (Колектор)", size=11, fill="#eaf0fd", stroke=NEG, pad=5)
    out.append(tb_col)
    
    # Відстань d
    out.append(line(x_emit, rod_y + rod_h + 15, x_coll, rod_y + rod_h + 15, color=MUTED, sw=1.5, dash="3,3"))
    out.append(arrow(x_emit, rod_y + rod_h + 15, x_coll, rod_y + rod_h + 15, color=INK, sw=1.5))
    out.append(arrow(x_coll, rod_y + rod_h + 15, x_emit, rod_y + rod_h + 15, color=INK, sw=1.5))
    out.append(text((x_emit + x_coll) / 2, rod_y + rod_h + 32, "Відстань d", size=13, bold=True, color=INK))
    
    # Осцилограф (Праворуч зверху)
    osc_x = 650
    osc_y = 65
    osc_w = 120
    osc_h = 90
    out.append(rect(osc_x, osc_y, osc_w, osc_h, fill="#1e293b", stroke="#475569", sw=2, rx=6))
    out.append(text(osc_x + osc_w / 2, osc_y + 18, "Осцилограф", size=11, bold=True, color="#ffffff"))
    out.append(rect(osc_x + 10, osc_y + 25, osc_w - 20, osc_h - 35, fill="#0f172a", stroke="#334155", sw=1, rx=2))
    
    path_osc = "M %d,%d L %d,%d Q %d,%d %d,%d Q %d,%d %d,%d L %d,%d" % (
        osc_x + 15, osc_y + 75,
        osc_x + 45, osc_y + 75,
        osc_x + 60, osc_y + 35,
        osc_x + 75, osc_y + 75,
        osc_x + 85, osc_y + 75,
        osc_x + 105, osc_y + 75,
        osc_x + 105, osc_y + 75
    )
    out.append('<path d="%s" fill="none" stroke="#22c55e" stroke-width="2"/>' % path_osc)
    
    out.append(line(x_coll, rod_y - 45, osc_x, osc_y + 60, color=NEG, sw=1.5, dash="4,4"))

    return render(os.path.join(IMG_DIR, "haynes-shockley-setup.svg"), w, h, "".join(out))


def polygon_head(x, y):
    return '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        x - 5, y - 8, x + 5, y - 8, x, y, INK
    )


def draw_pulse_evolution():
    """Малюнок 3: Еволюція сгустка меншинних носіїв у часі (дрейф, дифузне розширення, рекомбінаційне загасання)."""
    w, h = 800, 420
    out = []
    
    out.append(rect(10, 10, w - 20, h - 20, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(w / 2, 32, "Еволюція інжектованого хмарки носіїв у просторі й часі", size=16, bold=True, color=INK))
    
    # Вісь X та Y
    x_0 = 80
    y_axis = 350
    out.append(arrow(x_0, y_axis, w - 50, y_axis, color=INK, sw=1.5))
    out.append(arrow(x_0, y_axis, x_0, 60, color=INK, sw=1.5))
    out.append(text(w - 40, y_axis + 5, "x", size=14, bold=True))
    out.append(text(x_0 - 25, 70, "Δp(x,t)", size=13, bold=True))
    
    # 3 гаусові імпульси у моменти часу t1 < t2 < t3
    times = [
        {"t": "t = 0 (початок ін'єкції)", "x_c": 120, "amp": 240, "sigma": 15, "color": "#dc2626"},
        {"t": "t = t_1 (дрейф + дифузія)", "x_c": 330, "amp": 140, "sigma": 35, "color": "#d97706"},
        {"t": "t = t_2 (дрейф + рекомбінація)", "x_c": 580, "amp": 65, "sigma": 60, "color": "#2563eb"}
    ]
    
    for item in times:
        xc = item["x_c"]
        amp = item["amp"]
        sig = item["sigma"]
        col = item["color"]
        
        pts = []
        for px in range(int(xc - 3.5 * sig), int(xc + 3.5 * sig), 3):
            if px < x_0 or px > w - 60:
                continue
            dx = px - xc
            val = amp * math.exp(- (dx * dx) / (2 * sig * sig))
            py = y_axis - val
            pts.append((px, py))
            
        if pts:
            path_str = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts])
            out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_str, col))
            out.append(line(xc, y_axis, xc, y_axis - amp, color=col, sw=1, dash="2,2"))
            out.append(circle(xc, y_axis - amp, 4, fill=col, stroke="#ffffff", sw=1))
            
            out.append(text(xc, y_axis - amp - 12, item["t"], size=11, bold=True, color=col))
            
    out.append(arrow(120, 100, 580, 100, color=FIELD, sw=2))
    out.append(text(350, 88, "Дрейф центра сгустка зі швидкістю v_d = μ_p · E", size=12, bold=True, color=FIELD))
    
    out.append(line(330 - 35, y_axis - 70, 330 + 35, y_axis - 70, color="#d97706", sw=1.5))
    out.append(arrow(330, y_axis - 70, 330 + 35, y_axis - 70, color="#d97706", sw=1.5))
    out.append(arrow(330, y_axis - 70, 330 - 35, y_axis - 70, color="#d97706", sw=1.5))
    out.append(text(330, y_axis - 82, "Дифузне розпливання: σ ∝ √(D · t)", size=11, bold=True, color="#d97706"))
    
    out.append(arrow(580, y_axis - 140, 580, y_axis - 75, color=NEG, sw=1.5))
    out.append(text(640, y_axis - 110, "Експоненційний спад:\nA(t) ∝ exp(-t / τ)", size=11, bold=True, color=NEG))

    return render(os.path.join(IMG_DIR, "pulse-evolution.svg"), w, h, "".join(out))


def draw_low_vs_high_injection():
    """Малюнок 4: Порівняння низького та високого рівнів ін'єкції (амбіполярне поле та ефект Вебстера)."""
    w, h = 800, 400
    out = []
    
    out.append(rect(10, 10, w - 20, h - 20, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(w / 2, 32, "Порівняння режимів ін'єкції неосновних носіїв", size=16, bold=True, color=INK))
    
    # Ліва панель: Низький рівень ін'єкції (Δp << n0)
    w_box = 360
    h_box = 310
    x_l = 30
    y_b = 60
    out.append(rect(x_l, y_b, w_box, h_box, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    out.append(text(x_l + w_box / 2, y_b + 25, "1. Низький рівень ін'єкції (Δp << n_n0)", size=14, bold=True, color="#1e293b"))
    
    out.append(rect(x_l + 40, y_b + 80, 90, 180, fill="#dbeafe", stroke=NEG, sw=1.5))
    out.append(text(x_l + 85, y_b + 170, "n_n0\n(Основні\nелектрони)", size=12, bold=True, color=NEG))
    
    out.append(rect(x_l + 160, y_b + 235, 90, 25, fill="#fee2e2", stroke=POS, sw=1.5))
    out.append(text(x_l + 205, y_b + 252, "Δp << n_n0", size=11, bold=True, color=POS))
    
    tb_low, _, _ = textbox(x_l + w_box / 2, y_b + 280, "• Концентрація основних носіїв не змінюється\n• Транспорт — суто дифузійний (E ≈ 0)\n• Час життя τ_p = const (лінійна рекомбінація)", size=11, fill="#f8fafc", stroke="#cbd5e1", pad=5)
    out.append(tb_low)
    
    # Права панель: Високий рівень ін'єкції (Δp >= n0)
    x_r = 410
    out.append(rect(x_r, y_b, w_box, h_box, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    out.append(text(x_r + w_box / 2, y_b + 25, "2. Високий рівень ін'єкції (Δp ≥ n_n0)", size=14, bold=True, color="#1e293b"))
    
    out.append(rect(x_r + 40, y_b + 140, 90, 120, fill="#dbeafe", stroke=NEG, sw=1.5))
    out.append(text(x_r + 85, y_b + 200, "n_n0", size=12, bold=True, color=NEG))
    
    out.append(rect(x_r + 40, y_b + 80, 90, 60, fill="#bfdbfe", stroke=NEG, sw=1.5))
    out.append(text(x_r + 85, y_b + 110, "+ Δn", size=11, bold=True, color=NEG))
    
    out.append(rect(x_r + 160, y_b + 80, 90, 180, fill="#fee2e2", stroke=POS, sw=1.5))
    out.append(text(x_r + 205, y_b + 170, "Δp ≈ n_n0\n(Висока\nін'єкція)", size=12, bold=True, color=POS))
    
    tb_high, _, _ = textbox(x_r + w_box / 2, y_b + 280, "• Квазінейтральність залучає Δn ≈ Δp\n• Виникає внутрішнє амбіполярне поле E_amb\n• Зниження коефіцієнта підсилення (Вебстер)", size=11, fill="#f8fafc", stroke="#cbd5e1", pad=5)
    out.append(tb_high)

    return render(os.path.join(IMG_DIR, "low-vs-high-injection.svg"), w, h, "".join(out))


if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)
    draw_injection_pn_boundary()
    draw_haynes_shockley_setup()
    draw_pulse_evolution()
    draw_low_vs_high_injection()
    print("SVG figures generated successfully in", IMG_DIR)
