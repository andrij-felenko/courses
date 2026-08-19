# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми component-derating."""

import sys
import os
import math

# Підключаємо svgkit з каталогу scripts (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT,
    text, mtext, rect, line, arrow, circle, textbox, render
)

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_arrhenius_temperature():
    """Фігура 1: Крива температурного деретингу та інтенсивність відмов за Арреніусом."""
    W, H = 840, 500
    p = []
    
    # Заголовок графіка
    p.append(text(420, 30, "Експоненційне зростання інтенсивності відмов та зони деретингу", size=16, bold=True))
    
    # Вісі координат
    ox, oy = 95, 430
    gw, gh = 690, 330
    
    x_85 = ox + (85 - 25) / 125 * gw   # 95 + 60/125 * 690 = 426.2
    x_110 = ox + (110 - 25) / 125 * gw # 95 + 85/125 * 690 = 564.2
    x_150 = ox + gw                     # 785
    
    # Фонове підсвічування зон
    p.append(rect(ox, oy - gh, x_85 - ox, gh, fill="#eafaf1", stroke="none", rx=0))
    p.append(rect(x_85, oy - gh, x_110 - x_85, gh, fill="#fef9e7", stroke="none", rx=0))
    p.append(rect(x_110, oy - gh, x_150 - x_110, gh, fill="#fdeeed", stroke="none", rx=0))
    
    # Підписи зон у верхній шапці (над сіткою)
    p.append(text((ox + x_85)/2, oy - gh + 18, "Зона надійного деретингу", size=12, color=FIELD, bold=True))
    p.append(text((ox + x_85)/2, oy - gh + 34, "S_T ≤ 0.65 (T_j ≤ +85 °C)", size=10, color=FIELD))
    
    p.append(text((x_85 + x_110)/2, oy - gh + 18, "Допустима зона", size=12, color="#b7950b", bold=True))
    p.append(text((x_85 + x_110)/2, oy - gh + 34, "+85 °C < T_j ≤ +110 °C", size=10, color="#b7950b"))
    
    p.append(text((x_110 + x_150)/2, oy - gh + 18, "Критична зона", size=12, color=POS, bold=True))
    p.append(text((x_110 + x_150)/2, oy - gh + 34, "T_j > +110 °C", size=10, color=POS))
    
    # Розділові вертикальні пунктири
    p.append(line(x_85, oy, x_85, oy - gh, color=FIELD, sw=1.5, dash="4,4"))
    p.append(line(x_110, oy, x_110, oy - gh, color=POS, sw=1.5, dash="4,4"))
    p.append(line(x_150, oy, x_150, oy - gh, color=POS, sw=2, dash="2,2"))
    
    # Горизонтальні лінії сітки
    for i in range(1, 6):
        y_grid = oy - i * (gh / 5)
        p.append(line(ox, y_grid, ox + gw, y_grid, color="#e5e7eb", sw=1, dash="2,2"))
    
    # Вісь X (Температура, °C)
    p.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=2))
    p.append(text(ox + gw + 20, oy + 28, "Температура кристала T_j (°C)", size=12, color=INK, anchor="end", bold=True))
    
    # Вісь Y (Інтенсивність відмов / коефіцієнт прискорення)
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))
    p.append(text(ox - 10, oy - gh - 10, "Інтенсивність відмов λ (FIT) / AF_T", size=12, color=INK, anchor="start", bold=True))
    
    # Поділки по X
    ticks_x = [
        (25, "+25 °C"),
        (50, "+50 °C"),
        (75, "+75 °C"),
        (85, "+85 °C"),
        (100, "+100 °C"),
        (110, "+110 °C"),
        (125, "+125 °C"),
        (150, "+150 °C")
    ]
    for temp, lbl in ticks_x:
        tx = ox + (temp - 25) / 125 * gw
        p.append(line(tx, oy, tx, oy + 6, color=LINE, sw=1.5))
        p.append(text(tx, oy + 20, lbl, size=10, color=INK))
    
    # Поділки по Y
    ticks_y = [
        (0.0, "1× (базовий)"),
        (0.2, "5×"),
        (0.4, "20×"),
        (0.6, "50×"),
        (0.8, "100×"),
        (1.0, "300× (Abs Max)")
    ]
    for frac, lbl in ticks_y:
        ty = oy - frac * gh
        p.append(line(ox - 6, ty, ox, ty, color=LINE, sw=1.5))
        p.append(text(ox - 10, ty + 4, lbl, size=10, color=INK, anchor="end"))
    
    # Крива Арреніуса
    pts = []
    for step in range(126):
        temp = 25 + step
        t_k = temp + 273.15
        af = math.exp(8123.0 * (1.0/298.15 - 1.0/t_k))
        y_val = min(1.0, (af - 1.0) / 280.0)
        px = ox + (temp - 25) / 125 * gw
        py = oy - (y_val ** 0.55) * gh
        pts.append((px, py))
    
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    p.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="3.5" stroke-linecap="round"/>')
    
    # Ключові маркерні точки
    p25 = pts[0]
    p85 = pts[85 - 25]
    p110 = pts[110 - 25]
    p150 = pts[150 - 25]
    
    p.append(circle(p25[0], p25[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    p.append(circle(p85[0], p85[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    p.append(circle(p110[0], p110[1], 5, fill="#f39c12", stroke=INK, sw=1.5))
    p.append(circle(p150[0], p150[1], 6, fill=POS, stroke=INK, sw=2))
    
    # Виноски до точок
    tb1, _, _ = textbox(p85[0] - 110, p85[1] - 70, "Деретинг T_j ≤ +85 °C\nНизька швидкість старіння\nAF_T ≈ 3.2×", size=10, fill="#ffffff", stroke=FIELD)
    p.append(tb1)
    p.append(line(p85[0] - 50, p85[1] - 40, p85[0], p85[1], color=FIELD, sw=1.5))
    
    tb2, _, _ = textbox(p150[0] - 120, p150[1] + 75, "T_j = +150 °C (Abs Max)\nКатастрофічна деградація\nAF_T > 250×", size=10, fill="#ffffff", stroke=POS)
    p.append(tb2)
    p.append(line(p150[0] - 55, p150[1] + 55, p150[0], p150[1], color=POS, sw=1.5))
    
    return render(os.path.join(OUT, "arrhenius-temperature-derating.svg"), W, H, *p)

def fig_derating_margins():
    """Фігура 2: Матриця меж безпеки та коефіцієнтів деретингу для різних класів компонентів."""
    W, H = 840, 520
    p = []
    
    p.append(text(420, 30, "Межі електричного та теплового деретингу за класами компонентів", size=16, bold=True))
    
    ox, oy = 250, 75
    bar_w = 460
    bar_h = 42
    gap = 22
    
    categories = [
        ("Танталові конденсатори (MnO₂)", "Напруга V_op / V_rated", 0.50, POS, "50% (захист від займання)"),
        ("Керамічні конденсатори (MLCC)", "Напруга V_op / V_rated", 0.60, "#2980b9", "50–60% (DC-bias та TDDB)"),
        ("Алюмінієві електроліти", "Пульсація I_rip та Напруга", 0.70, "#8e44ad", "70% V, T_core ≤ +85 °C"),
        ("Силові MOSFET / IGBT", "Напруга V_ds / V_ds_max", 0.75, "#d35400", "70–80% V_ds, T_j ≤ 110 °C"),
        ("Резистори (SMD плівкові)", "Потужність P_op / P_max", 0.50, FIELD, "50% P_max, 80% V_max"),
        ("Магнітні дроселі / котушки", "Струм I_op / I_sat", 0.70, "#16a085", "70% I_sat, T_core ≤ +90 °C")
    ]
    
    scale_y = oy - 15
    for pct in [0, 25, 50, 75, 100]:
        sx = ox + (pct / 100.0) * bar_w
        p.append(line(sx, scale_y, sx, scale_y + 8, color=LINE, sw=1.5))
        p.append(text(sx, scale_y - 6, f"{pct}%", size=11, bold=True, color=INK))
        p.append(line(sx, scale_y + 8, sx, oy + len(categories)*(bar_h+gap) - gap, color="#e5e7eb", sw=1, dash="3,3"))
    
    abs_x = ox + bar_w
    p.append(line(abs_x, scale_y - 20, abs_x, oy + len(categories)*(bar_h+gap) - gap + 15, color=POS, sw=2.5))
    p.append(text(abs_x, oy + len(categories)*(bar_h+gap) - gap + 30, "Absolute Maximum (100%)", size=11, color=POS, bold=True))
    
    for idx, (name, param, ratio, col, note) in enumerate(categories):
        cy = oy + idx * (bar_h + gap)
        
        p.append(text(ox - 14, cy + 16, name, size=12, color=INK, anchor="end", bold=True))
        p.append(text(ox - 14, cy + 34, param, size=10, color=MUTED, anchor="end"))
        
        p.append(rect(ox, cy, bar_w, bar_h, fill="#f4f6f8", stroke="#d1d5db", sw=1.2, rx=4))
        
        w_safe = ratio * bar_w
        p.append(rect(ox, cy, w_safe, bar_h, fill=col, stroke=col, sw=1.5, rx=4))
        
        w_danger = bar_w - w_safe
        p.append(rect(ox + w_safe, cy, w_danger, bar_h, fill="#fdedec", stroke="none", rx=0))
        
        p.append(line(ox + w_safe, cy, ox + w_safe, cy + bar_h, color=LINE, sw=2))
        
        p.append(text(ox + w_safe / 2, cy + 26, f"{int(ratio*100)}%", size=12, color="#ffffff", bold=True))
        p.append(text(ox + w_safe + 10, cy + 26, note, size=10, color=INK, anchor="start", bold=True))
    
    return render(os.path.join(OUT, "component-derating-margins.svg"), W, H, *p)

def fig_soa_envelope():
    """Фігура 3: Деретинг області безпечної роботи (Safe Operating Area, SOA) силового MOSFET."""
    W, H = 840, 520
    p = []
    
    p.append(text(420, 30, "Деретинг області безпечної роботи (SOA) силового транзистора", size=16, bold=True))
    
    ox, oy = 110, 440
    gw, gh = 660, 350
    
    p.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=2))
    p.append(text(ox + gw + 25, oy + 28, "Напруга стік-витік V_DS (В, лог. шкала)", size=12, bold=True, anchor="end"))
    
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))
    p.append(text(ox - 15, oy - gh - 10, "Струм стоку I_D (А, лог. шкала)", size=12, bold=True, anchor="start"))
    
    for i in range(1, 6):
        y_g = oy - i * (gh / 5)
        p.append(line(ox, y_g, ox + gw, y_g, color="#edf0f2", sw=1, dash="2,2"))
        x_g = ox + i * (gw / 5)
        p.append(line(x_g, oy, x_g, oy - gh, color="#edf0f2", sw=1, dash="2,2"))
    
    soa_orig = [
        (ox + 40, oy - 270),
        (ox + 90, oy - gh + 20),
        (ox + 270, oy - gh + 20),
        (ox + 430, oy - 190),
        (ox + 540, oy - 75),
        (ox + 600, oy - 20),
        (ox + 40, oy - 20)
    ]
    
    soa_derated = [
        (ox + 40, oy - 200),
        (ox + 90, oy - gh + 90),
        (ox + 220, oy - gh + 90),
        (ox + 370, oy - 170),
        (ox + 450, oy - 80),
        (ox + 490, oy - 20),
        (ox + 40, oy - 20)
    ]
    
    path_orig = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in soa_orig[:-1]) + f" L {soa_orig[-1][0]:.1f},{soa_orig[-1][1]:.1f} Z"
    path_derated = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in soa_derated[:-1]) + f" L {soa_derated[-1][0]:.1f},{soa_derated[-1][1]:.1f} Z"
    
    p.append(f'<path d="{path_orig}" fill="#fdeeed" stroke="{POS}" stroke-width="2.5" stroke-dasharray="5,4"/>')
    p.append(f'<path d="{path_derated}" fill="#e8f8f0" stroke="{FIELD}" stroke-width="3"/>')
    
    p.append(text(ox + 120, oy - gh + 10, "Паспортна межа струму I_D(max)", size=10, color=POS, bold=True))
    p.append(text(ox + 155, oy - gh + 80, "Деретований струм: S_I ≤ 0.60", size=10, color=FIELD, bold=True))
    
    # Винесений вільний текст для межі потужності
    p.append(text(ox + 510, oy - 270, "Межа потужності P_max\nта вторинного пробою", size=10, color=POS))
    p.append(line(ox + 480, oy - 250, ox + 410, oy - 190, color=POS, sw=1.2))
    
    p.append(text(ox + 600, oy + 20, "V_DS(max)", size=11, color=POS, bold=True))
    p.append(line(ox + 600, oy, ox + 600, oy - 20, color=POS, sw=2))
    
    p.append(text(ox + 490, oy + 20, "0.8·V_DS(max)", size=11, color=FIELD, bold=True))
    p.append(line(ox + 490, oy, ox + 490, oy - 20, color=FIELD, sw=2))
    
    tb_safe, _, _ = textbox(ox + 200, oy - 80, "БЕЗПЕЧНА РОБОЧА ЗОНА\n- Запас за напругою 20–30 %\n- Запас за струмом 40–50 %\n- T_j ≤ +110 °C", size=11, fill="#ffffff", stroke=FIELD, bold=False)
    p.append(tb_safe)
    
    tb_risk, _, _ = textbox(ox + 570, oy - 120, "НЕБЕЗПЕЧНА ЗОНА ДАТАШИТУ\nРизик лавинного пробою,\nтермонестійкості та відмови\nчерез паразитні індуктивності", size=10, fill="#ffffff", stroke=POS, bold=False)
    p.append(tb_risk)
    
    return render(os.path.join(OUT, "soar-derating-envelope.svg"), W, H, *p)

def fig_capacitor_stress():
    """Фігура 4: Вплив напругового стресу на діелектрик (DC-bias та пробій TDDB)."""
    W, H = 840, 480
    p = []
    
    p.append(text(420, 30, "Вплив коефіцієнта напруги на надійність та ємність конденсаторів", size=16, bold=True))
    
    # Лівий графік (MLCC DC-bias)
    ox1, oy1 = 75, 410
    gw1, gh1 = 305, 290
    
    p.append(text(ox1 + gw1/2, oy1 - gh1 - 25, "Кераміка X7R/X5R: Втрата ємності (DC-bias)", size=12, bold=True))
    p.append(arrow(ox1, oy1, ox1 + gw1 + 20, oy1, color=LINE, sw=1.8))
    p.append(text(ox1 + gw1 + 15, oy1 + 24, "V_DC / V_rated (%)", size=10, color=INK, anchor="end", bold=True))
    
    p.append(arrow(ox1, oy1, ox1, oy1 - gh1 - 15, color=LINE, sw=1.8))
    p.append(text(ox1 - 10, oy1 - gh1 - 5, "ΔC/C₀ (%)", size=10, color=INK, anchor="start", bold=True))
    
    for pct in [0, 25, 50, 75, 100]:
        gx = ox1 + (pct / 100.0) * gw1
        p.append(line(gx, oy1, gx, oy1 + 5, color=LINE, sw=1.2))
        p.append(text(gx, oy1 + 18, f"{pct}%", size=9, color=INK))
        
    for frac, lbl in [(0.0, "0%"), (0.25, "-20%"), (0.5, "-40%"), (0.75, "-60%"), (1.0, "-80%")]:
        gy = oy1 - (1.0 - frac) * gh1
        p.append(line(ox1 - 4, gy, ox1, gy, color=LINE, sw=1.2))
        p.append(text(ox1 - 8, gy + 4, lbl, size=9, color=INK, anchor="end"))
        p.append(line(ox1, gy, ox1 + gw1, gy, color="#f0f2f5", sw=1, dash="2,2"))
        
    p.append(rect(ox1, oy1 - gh1, gw1 * 0.5, gh1, fill="#e8f8f0", stroke="none", rx=0))
    p.append(text(ox1 + gw1*0.25, oy1 - gh1 + 20, "Зона дератингу\n(Втрата ємності < 25%)", size=9, color=FIELD, bold=True))
    
    pts_bias = []
    for step in range(101):
        v_pct = step / 100.0
        c_loss = 1.0 - (1.0 / (1.0 + (v_pct / 0.4)**2.2))
        px = ox1 + v_pct * gw1
        py = oy1 - gh1 + c_loss * 0.8 * gh1
        pts_bias.append((px, py))
        
    path_bias = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_bias)
    p.append(f'<path d="{path_bias}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    
    # Правий графік (Voltage Acceleration Factor)
    ox2, oy2 = 475, 410
    gw2, gh2 = 305, 290
    
    p.append(text(ox2 + gw2/2, oy2 - gh2 - 25, "Прискорення відмов (AF_V = (V_op/V_rated)ⁿ)", size=12, bold=True))
    p.append(arrow(ox2, oy2, ox2 + gw2 + 20, oy2, color=LINE, sw=1.8))
    p.append(text(ox2 + gw2 + 15, oy2 + 24, "Коефіцієнт напруги S_V (%)", size=10, color=INK, anchor="end", bold=True))
    
    p.append(arrow(ox2, oy2, ox2, oy2 - gh2 - 15, color=LINE, sw=1.8))
    p.append(text(ox2 - 10, oy2 - gh2 - 5, "AF_V (логарифмічний)", size=10, color=INK, anchor="start", bold=True))
    
    for pct in [0, 50, 70, 80, 100]:
        gx = ox2 + (pct / 100.0) * gw2
        p.append(line(gx, oy2, gx, oy2 + 5, color=LINE, sw=1.2))
        p.append(text(gx, oy2 + 18, f"{pct}%", size=9, color=INK))
        
    for frac, lbl in [(0.0, "1×"), (0.33, "10×"), (0.66, "100×"), (1.0, "1000×")]:
        gy = oy2 - frac * gh2
        p.append(line(ox2 - 4, gy, ox2, gy, color=LINE, sw=1.2))
        p.append(text(ox2 - 8, gy + 4, lbl, size=10, color=INK, anchor="end"))
        p.append(line(ox2, gy, ox2 + gw2, gy, color="#f0f2f5", sw=1, dash="2,2"))
        
    p.append(rect(ox2, oy2 - gh2, gw2 * 0.6, gh2, fill="#e8f8f0", stroke="none", rx=0))
    p.append(text(ox2 + gw2*0.3, oy2 - gh2 + 20, "Зона високої надійності\n(AF_V < 0.05×)", size=9, color=FIELD, bold=True))
    
    pts_v = []
    for step in range(101):
        v_pct = step / 100.0
        af_log = (v_pct ** 5.0)
        px = ox2 + v_pct * gw2
        py = oy2 - af_log * gh2
        pts_v.append((px, py))
        
    path_v = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_v)
    p.append(f'<path d="{path_v}" fill="none" stroke="{POS}" stroke-width="3"/>')
    
    tx_50 = ox2 + 0.5 * gw2
    p.append(circle(tx_50, oy2 - (0.5**5)*gh2, 4, fill=FIELD, stroke=INK, sw=1.2))
    tb_tan, _, _ = textbox(tx_50 + 85, oy2 - 150, "Тантал при 50% V:\nІнтенсивність відмов\nпадає у ~32 рази!", size=10, fill="#ffffff", stroke=FIELD)
    p.append(tb_tan)
    p.append(line(tx_50 + 25, oy2 - 120, tx_50, oy2 - (0.5**5)*gh2, color=FIELD, sw=1.2))
    
    return render(os.path.join(OUT, "capacitor-voltage-stress-curves.svg"), W, H, *p)

def main():
    fig_arrhenius_temperature()
    fig_derating_margins()
    fig_soa_envelope()
    fig_capacitor_stress()
    print("Всі SVG-фігури згенеровано успішно.")

if __name__ == "__main__":
    main()
