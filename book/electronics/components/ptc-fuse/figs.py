# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Мікроструктура композиту: провідні ланцюжки та фазовий перехід ───────
def fig_percolation_microstructure():
    W, H = 760, 360
    els = []

    # Тло двох панелей (прості прямокутники з відступами)
    els.append(rect(15, 15, 355, 330, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    els.append(rect(390, 15, 355, 330, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))

    # Заголовки панелей
    els.append(text(192, 42, "Холодний стан (T < T_trip)", size=13, color="#0f172a", bold=True))
    els.append(text(567, 42, "Гарячий стан після спрацювання (T > T_trip)", size=13, color=POS, bold=True))

    # ── Ліва панель: Холодний стан
    domains_left = [
        (45, 65, 80, 60), (155, 65, 80, 60), (265, 65, 80, 60),
        (45, 155, 80, 60), (155, 155, 80, 60), (265, 155, 80, 60),
        (45, 235, 80, 50), (155, 235, 80, 50), (265, 235, 80, 50)
    ]
    for x, y, w, h in domains_left:
        els.append(rect(x, y, w, h, fill="#e0f2fe", stroke="#7dd3fc", sw=1.2, rx=8))
        els.append(text(x + w/2, y + h/2 + 4, "Кристаліт", size=10, color="#0369a1"))

    cb_left = [
        (30, 140), (40, 138), (130, 138), (142, 140), (240, 138), (252, 140), (350, 140),
        (130, 85), (132, 105), (140, 180), (142, 205), (140, 255),
        (240, 85), (242, 105), (250, 180), (252, 205), (250, 255),
        (85, 138), (105, 140), (195, 138), (215, 140), (300, 138), (320, 140)
    ]
    for cx, cy in cb_left:
        els.append(circle(cx, cy, 5.5, fill="#0f172a", stroke="#334155", sw=1))

    els.append(line(25, 140, 360, 140, color=FIELD, sw=3, dash="6 3"))
    els.append(text(192, 315, "R_cold ~ 0.02...0.1 Ом (омічний контакт часток)", size=11, color=FIELD, bold=True))

    # ── Права панель: Гарячий стан
    domains_right = [
        (415, 65, 85, 60), (525, 65, 85, 60), (635, 65, 85, 60),
        (415, 155, 85, 60), (525, 155, 85, 60), (635, 155, 85, 60),
        (415, 235, 85, 50), (525, 235, 85, 50), (635, 235, 85, 50)
    ]
    for x, y, w, h in domains_right:
        els.append(rect(x, y, w, h, fill="#ffedd5", stroke="#fdba74", sw=1.2, rx=12))
        els.append(text(x + w/2, y + h/2 + 4, "Аморфна фаза", size=10, color="#c2410c"))

    cb_right = [
        (402, 130), (410, 152), (508, 130), (518, 152), (618, 130), (628, 152), (730, 135),
        (510, 80), (518, 105), (512, 185), (520, 210), (514, 255),
        (620, 80), (628, 105), (622, 185), (630, 210), (624, 255),
        (455, 132), (475, 152), (565, 132), (585, 152), (675, 132), (695, 152)
    ]
    for cx, cy in cb_right:
        els.append(circle(cx, cy, 5.5, fill="#475569", stroke="#64748b", sw=1))

    els.append(text(445, 142, "×", size=15, color=POS, bold=True))
    els.append(text(555, 142, "×", size=15, color=POS, bold=True))
    els.append(text(665, 142, "×", size=15, color=POS, bold=True))

    els.append(text(567, 315, "R_hot ~ 10...100 кОм (розрив ланцюжків)", size=11, color=POS, bold=True))

    content = "".join(els)
    with open(os.path.join(OUT, "percolation-microstructure.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>')


# ── 2. Залежність опору від температури R(T) і петля гістерезису ─────────────
def fig_rt_curve():
    W, H = 740, 390
    els = []

    ox, oy = 95, 330
    gw, gh = 600, 260

    log_ticks = [
        (0, "0.01 Ом"),
        (43, "0.1 Ом"),
        (86, "1 Ом"),
        (130, "10 Ом"),
        (173, "100 Ом"),
        (216, "10 кОм"),
        (260, "100 кОм")
    ]
    for yoff, lbl in log_ticks:
        y = oy - yoff
        els.append(line(ox, y, ox + gw, y, color="#f1f5f9", sw=1))
        els.append(text(ox - 10, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    temp_ticks = [
        (-40, 0),
        (0, 70),
        (25, 120),
        (60, 190),
        (85, 240),
        (125, 340),
        (135, 410),
        (160, 520)
    ]
    for deg, xoff in temp_ticks:
        x = ox + xoff
        els.append(line(x, oy, x, oy - gh, color="#f8fafc", sw=1))
        els.append(text(x, oy + 18, f"{deg}°C", size=10, color=MUTED))

    # Осі
    els.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    els.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    els.append(text(ox + gw, oy + 18, "Температура T", size=10, color=INK, anchor="end", bold=True))
    els.append(text(ox, oy - gh - 8, "Опір R (log)", size=10, color=INK, anchor="start", bold=True))

    # Крива нагрівання
    pts_heat = [
        (ox, oy - 15),
        (ox + 120, oy - 20),       # 25°C
        (ox + 240, oy - 30),       # 85°C
        (ox + 310, oy - 55),       # 115°C
        (ox + 340, oy - 130),      # 125°C
        (ox + 375, oy - 210),      # 130°C
        (ox + 410, oy - 250),      # 135°C
        (ox + 520, oy - 255)       # 160°C
    ]
    poly_pts = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_heat])
    els.append(f'<polyline points="{poly_pts}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Крива охолодження (гістерезис)
    pts_cool = [
        (ox + 520, oy - 255),
        (ox + 410, oy - 248),
        (ox + 350, oy - 230),
        (ox + 300, oy - 170),
        (ox + 240, oy - 100),
        (ox + 180, oy - 50),
        (ox + 120, oy - 32),       # 25°C: R_1max
        (ox + 30, oy - 25)
    ]
    poly_cool = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_cool])
    els.append(f'<polyline points="{poly_cool}" fill="none" stroke="{FIELD}" stroke-width="2.2" stroke-dasharray="5 3"/>')

    # Позначення T_trip ліворуч від точки зламу
    els.append(line(ox + 375, oy, ox + 375, oy - 210, color=POS, sw=1.2, dash="3 3"))
    els.append(rect(ox + 385, oy - 220, 205, 32, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    els.append(text(ox + 487, oy - 204, "T_trip ≈ 125...135 °C (плавлення)", size=9.5, color=POS, bold=True))

    # Позначення R_initial vs R_1max
    els.append(circle(ox + 120, oy - 20, 4, fill=POS, stroke="#ffffff", sw=1.5))
    els.append(circle(ox + 120, oy - 32, 4, fill=FIELD, stroke="#ffffff", sw=1.5))
    els.append(rect(ox + 20, oy - 110, 200, 32, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    els.append(text(ox + 120, oy - 94, "R_initial → R_1max (+30...50%)", size=9.5, color=FIELD, bold=True))

    # Легенда внизу
    els.append(rect(ox + 270, oy - 70, 270, 36, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    els.append(line(ox + 280, oy - 58, ox + 310, oy - 58, color=POS, sw=2.5))
    els.append(text(ox + 320, oy - 54, "Нагрівання під I²R", size=9.5, color=INK, anchor="start"))
    els.append(line(ox + 280, oy - 42, ox + 310, oy - 42, color=FIELD, sw=2, dash="4 2"))
    els.append(text(ox + 320, oy - 38, "Охолодження (гістерезис)", size=9.5, color=INK, anchor="start"))

    content = "".join(els)
    with open(os.path.join(OUT, "rt-curve-phase-transition.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>')


# ── 3. Теплова рівновага та біфуркація спрацювання ──────────────────────────
def fig_thermal_bifurcation():
    W, H = 740, 380
    els = []

    ox, oy = 80, 320
    gw, gh = 610, 250

    for yoff in [0, 60, 120, 180, 240]:
        els.append(line(ox, oy - yoff, ox + gw, oy - yoff, color="#f1f5f9", sw=1))
    for xoff in [0, 120, 240, 360, 480, 600]:
        els.append(line(ox + xoff, oy, ox + xoff, oy - gh, color="#f1f5f9", sw=1))

    els.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    els.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    els.append(text(ox + gw, oy + 18, "Температура компонента T", size=10, color=INK, anchor="end", bold=True))
    els.append(text(ox, oy - gh - 8, "Потужність P (Вт)", size=10, color=INK, anchor="start", bold=True))

    # Пряма тепловідводу в довкілля
    els.append(line(ox + 40, oy, ox + 560, oy - 230, color=NEG, sw=2.5))
    els.append(text(ox + 500, oy - 240, "P_diss = G_th · (T - T_amb)", size=10, color=NEG, bold=True))

    # Крива при робочому струмі I_norm <= I_hold
    pts_norm = [
        (ox + 40, oy - 15),
        (ox + 110, oy - 29),
        (ox + 200, oy - 45),
        (ox + 300, oy - 70),
        (ox + 360, oy - 140),
        (ox + 420, oy - 200),
        (ox + 500, oy - 210)
    ]
    poly_norm = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_norm])
    els.append(f'<polyline points="{poly_norm}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')
    els.append(circle(ox + 110, oy - 29, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    els.append(text(ox + 110, oy - 42, "Точка A (робоча)", size=9.5, color=FIELD, bold=True))

    # Крива при струмі перевантаження I_fault > I_trip
    pts_fault = [
        (ox + 40, oy - 75),
        (ox + 150, oy - 95),
        (ox + 250, oy - 120),
        (ox + 320, oy - 165),
        (ox + 380, oy - 225),
        (ox + 440, oy - 165),      # Перетин B
        (ox + 550, oy - 170)
    ]
    poly_fault = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_fault])
    els.append(f'<polyline points="{poly_fault}" fill="none" stroke="{POS}" stroke-width="2.6"/>')
    els.append(circle(ox + 440, oy - 165, 5, fill=POS, stroke="#ffffff", sw=1.5))
    els.append(text(ox + 490, oy - 150, "Точка B (фіксація Trip)", size=9.5, color=POS, bold=True))

    # Стрілка теплового розгону
    els.append(arrow(ox + 180, oy - 85, ox + 290, oy - 85, color=POS, sw=2))
    els.append(text(ox + 235, oy - 95, "Тепловий розгін P_gen > P_diss", size=9, color=POS, italic=True))

    # Пояснювальний блок
    els.append(rect(ox + 160, oy - 245, 300, 36, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    els.append(text(ox + 310, oy - 227, "I_fault розігріває деталь до точки B (~130°C)", size=9.5, color=INK))

    content = "".join(els)
    with open(os.path.join(OUT, "thermal-equilibrium-bifurcation.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>')


# ── 4. Схема захисту порту живлення USB ─────────────────────────────────────
def fig_usb_protection():
    W, H = 740, 320
    els = []

    # Вхідне живлення +5V
    els.append(line(40, 80, 150, 80, color=POS, sw=2.5))
    els.append(circle(40, 80, 4, fill=POS, stroke=LINE, sw=1.2))
    els.append(text(40, 60, "+5V VBUS", size=12, color=POS, bold=True))

    # PPTC Fuse прямокутник
    els.append(rect(150, 62, 100, 36, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    els.append(text(200, 84, "PPTC Запобіжник", size=10, color="#854d0e", bold=True))
    els.append(text(200, 115, "I_hold = 750 мА", size=9.5, color=MUTED))
    els.append(text(200, 128, "I_trip = 1.5 А", size=9.5, color=MUTED))

    # Лінія після запобіжника
    els.append(line(250, 80, 440, 80, color=POS, sw=2.5))

    # TVS-діод на землю
    els.append(line(340, 80, 340, 120, color=LINE, sw=1.8))
    els.append(rect(320, 120, 40, 30, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    els.append(text(340, 138, "TVS", size=9.5, color="#1e293b", bold=True))
    els.append(line(340, 150, 340, 180, color=LINE, sw=1.8))
    # Земля TVS
    els.append(line(325, 180, 355, 180, color=LINE, sw=2))
    els.append(line(330, 185, 350, 185, color=LINE, sw=1.5))
    els.append(line(335, 190, 345, 190, color=LINE, sw=1.2))
    els.append(text(340, 205, "ESD захист", size=9, color=MUTED))

    # Фільтрувальний конденсатор MLCC
    els.append(line(440, 80, 440, 120, color=LINE, sw=1.8))
    els.append(line(425, 120, 455, 120, color=LINE, sw=2.2))
    els.append(line(425, 130, 455, 130, color=LINE, sw=2.2))
    els.append(line(440, 130, 440, 180, color=LINE, sw=1.8))
    # Земля MLCC
    els.append(line(425, 180, 455, 180, color=LINE, sw=2))
    els.append(line(430, 185, 450, 185, color=LINE, sw=1.5))
    els.append(line(435, 190, 445, 190, color=LINE, sw=1.2))
    els.append(text(440, 205, "10 мкФ MLCC", size=9, color=MUTED))

    # Вихід на USB роз'єм
    els.append(line(440, 80, 560, 80, color=POS, sw=2.5))
    els.append(circle(560, 80, 4, fill=POS, stroke=LINE, sw=1.2))
    els.append(text(560, 60, "Вихід VBUS (USB)", size=12, color=POS, bold=True))

    # Стан 1: Штатний режим
    els.append(rect(40, 230, 300, 70, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    els.append(text(190, 250, "Штатний режим: I = 500 мА", size=10, color=FIELD, bold=True))
    els.append(text(190, 268, "ΔU = 0.5 А · 0.08 Ом = 40 мВ (падіння лише 0.8%)", size=9.5, color=INK))
    els.append(text(190, 285, "На USB порті стабільні 4.96 В", size=9.5, color=MUTED))

    # Стан 2: Коротке замикання
    els.append(rect(380, 230, 320, 70, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    els.append(text(540, 250, "Аварія (к.з. на порту): I_fault = 4 А", size=10, color=POS, bold=True))
    els.append(text(540, 268, "PPTC розігрівається за 120 мс і рве коло", size=9.5, color=INK))
    els.append(text(540, 285, "Струм витоку падає до I_leak ~ 2 мА (хост захищено)", size=9.5, color=MUTED))

    content = "".join(els)
    with open(os.path.join(OUT, "usb-port-protection-circuit.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>')


# ── 5. Температурний девейтинг та часострумові характеристики ────────────────
def fig_derating_triptime():
    W, H = 760, 380
    els = []

    # Дві панелі
    els.append(rect(15, 15, 355, 345, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    els.append(rect(390, 15, 355, 345, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    els.append(text(192, 42, "Температурний девейтинг I_hold", size=12, color=INK, bold=True))
    els.append(text(567, 42, "Час спрацювання Time-to-Trip", size=12, color=INK, bold=True))

    # ── Ліва панель
    lox, loy = 65, 290
    lgw, lgh = 280, 210

    for yoff in [0, 42, 84, 126, 168, 210]:
        els.append(line(lox, loy - yoff, lox + lgw, loy - yoff, color="#f1f5f9", sw=1))
    els.append(line(lox, loy, lox + lgw, loy, color=LINE, sw=1.5))
    els.append(line(lox, loy, lox, loy - lgh, color=LINE, sw=1.5))

    els.append(text(lox - 8, loy + 3, "0%", size=9.5, color=MUTED, anchor="end"))
    els.append(text(lox - 8, loy - 84 + 3, "50%", size=9.5, color=MUTED, anchor="end"))
    els.append(text(lox - 8, loy - 168 + 3, "100%", size=9.5, color=MUTED, anchor="end"))
    els.append(text(lox - 8, loy - 210 + 3, "130%", size=9.5, color=MUTED, anchor="end"))

    els.append(text(lox + 20, loy + 16, "-40°C", size=9.5, color=MUTED))
    els.append(text(lox + 90, loy + 16, "0°C", size=9.5, color=MUTED))
    els.append(text(lox + 145, loy + 16, "+25°C", size=9.5, color=MUTED))
    els.append(text(lox + 205, loy + 16, "+60°C", size=9.5, color=MUTED))
    els.append(text(lox + 260, loy + 16, "+85°C", size=9.5, color=MUTED))

    pts_derate = [
        (lox + 20, loy - 210),
        (lox + 90, loy - 185),
        (lox + 145, loy - 168),
        (lox + 205, loy - 120),
        (lox + 260, loy - 75)
    ]
    poly_derate = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_derate])
    els.append(f'<polyline points="{poly_derate}" fill="none" stroke="{NEG}" stroke-width="2.6"/>')
    els.append(circle(lox + 145, loy - 168, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    els.append(text(192, 332, "На морозі I_hold росте, на спеці падає удвічі", size=9.5, color=MUTED))

    # ── Права панель
    rox, roy = 440, 290
    rgw, rgh = 280, 210

    time_ticks = [(0, "0.01 с"), (52, "0.1 с"), (105, "1 с"), (157, "10 с"), (210, "100 с")]
    for yoff, tlbl in time_ticks:
        els.append(line(rox, roy - yoff, rox + rgw, roy - yoff, color="#f1f5f9", sw=1))
        els.append(text(rox - 6, roy - yoff + 3, tlbl, size=9.5, color=MUTED, anchor="end"))

    els.append(line(rox, roy, rox + rgw, roy, color=LINE, sw=1.5))
    els.append(line(rox, roy, rox, roy - rgh, color=LINE, sw=1.5))

    els.append(text(rox + 30, roy + 16, "2×", size=9.5, color=MUTED))
    els.append(text(rox + 90, roy + 16, "4×", size=9.5, color=MUTED))
    els.append(text(rox + 150, roy + 16, "6×", size=9.5, color=MUTED))
    els.append(text(rox + 210, roy + 16, "10×", size=9.5, color=MUTED))
    els.append(text(rox + rgw, roy - 8, "I / I_hold", size=9.5, color=INK, anchor="end", bold=True))

    pts_t_25 = [
        (rox + 30, roy - 180),
        (rox + 70, roy - 120),
        (rox + 120, roy - 75),
        (rox + 190, roy - 38),
        (rox + 250, roy - 15)
    ]
    poly_t_25 = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_t_25])
    els.append(f'<polyline points="{poly_t_25}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    pts_t_85 = [
        (rox + 30, roy - 130),
        (rox + 70, roy - 80),
        (rox + 120, roy - 42),
        (rox + 190, roy - 18),
        (rox + 250, roy - 5)
    ]
    poly_t_85 = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_t_85])
    els.append(f'<polyline points="{poly_t_85}" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="4 2"/>')

    # Акуратна рамка легенди вгорі праворуч
    els.append(rect(rox + 160, roy - 200, 110, 44, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    els.append(line(rox + 168, roy - 188, rox + 192, roy - 188, color=POS, sw=2.5))
    els.append(text(rox + 198, roy - 184, "+25 °C", size=9.5, color=POS, anchor="start", bold=True))
    els.append(line(rox + 168, roy - 168, rox + 192, roy - 168, color="#d97706", sw=2, dash="4 2"))
    els.append(text(rox + 198, roy - 164, "+85 °C", size=9.5, color="#d97706", anchor="start", bold=True))

    els.append(text(567, 332, "Крута залежність t_trip від кратності струму (I²R)", size=9.5, color=MUTED))

    content = "".join(els)
    with open(os.path.join(OUT, "time-to-trip-derating.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{content}\n</svg>')


if __name__ == "__main__":
    fig_percolation_microstructure()
    fig_rt_curve()
    fig_thermal_bifurcation()
    fig_usb_protection()
    fig_derating_triptime()
    print("All PPTC figures generated successfully.")
