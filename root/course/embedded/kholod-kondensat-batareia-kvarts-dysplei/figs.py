# -*- coding: utf-8 -*-
"""Фігури для детальної статті «Холод: конденсат, батарея, кварц, дисплей»
(root/course/embedded/kholod-kondensat-batareia-kvarts-dysplei).
Чистий Python + svgkit, без зовнішніх залежностей. Вивід — ./img/*.svg."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def _axes(x0, y0, w, h, xlab, ylab, title=None):
    """Осі з підписами. Повертає список фрагментів."""
    frags = [line(x0, y0, x0 + w, y0, INK, 1.8),          # X
             line(x0, y0, x0, y0 - h, INK, 1.8)]          # Y (вгору)
    frags.append(text(x0 + w, y0 + 22, xlab, size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, y0 - h + 2, ylab, size=13, color=MUTED, anchor="end"))
    if title:
        frags.append(text(x0 + w / 2, y0 - h - 14, title, size=14, color=INK, bold=True))
    return frags


# ── 1. Графік: ESR батареї та просадка напруги під імпульсом при морозі ────────
def fig_battery_esr_sag():
    W, H = 760, 480
    x0, y0, w, h = 90, 410, 600, 310
    
    frags = [
        text(W / 2, 28, "Експоненційний стрибок ESR літієвої батареї та просадка напруги", size=16, bold=True),
        text(W / 2, 48, "При -40 °C опір зростає у 20 разів; імпульс радіомодуля (500 мА) провалює напругу нижче UVLO",
             size=12, color=MUTED, italic=True)
    ]
    frags += _axes(x0, y0, w, h, "температура довкілля T, °C", "ESR (мОм) / Напруга під імпульсом (В)")
    
    Tmin, Tmax = -40.0, 30.0
    def px(T): return x0 + (T - Tmin) / (Tmax - Tmin) * w
    
    # Шкала X
    for T in (-40, -30, -20, -10, 0, 10, 20, 30):
        xx = px(T)
        frags.append(line(xx, y0, xx, y0 + 5, INK, 1.3))
        frags.append(text(xx, y0 + 19, str(T), size=11, color=MUTED))
    
    # Ліва вісь Y: ESR (0..1200 мОм)
    def py_esr(r): return y0 - (r / 1200.0) * h
    for r in (0, 300, 600, 900, 1200):
        yy = py_esr(r)
        frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2))
        frags.append(text(x0 - 8, yy + 4, str(r), size=10.5, color=POS, anchor="end"))
    
    # Права вісь Y: Напруга під навантаженням (2.0..4.2 В)
    x_right = x0 + w
    frags.append(line(x_right, y0, x_right, y0 - h, INK, 1.8))
    def py_v(v): return y0 - ((v - 2.0) / (4.2 - 2.0)) * h
    for v in (2.0, 2.5, 2.8, 3.0, 3.5, 4.0):
        yy = py_v(v)
        frags.append(line(x_right, yy, x_right + 5, yy, INK, 1.2))
        frags.append(text(x_right + 8, yy + 4, "%.1f В" % v, size=10.5, color=NEG, anchor="start"))
    
    # Модель ESR(T): ESR(25°C) = 50 мОм, при -20°C ~ 350 мОм, при -40°C ~ 1100 мОм
    import math
    def esr_model(T):
        # Арреніусоподібне зростання:
        return 45.0 + 80.0 * math.exp(-0.065 * (T - 25.0)) + 60.0 * math.exp(-0.12 * (T - 20.0))
    
    # OCV = 3.8 В. Напруга під імпульсом I = 0.5 А: V = OCV - I * ESR
    def v_loaded(T):
        r_ohm = esr_model(T) / 1000.0
        return 3.8 - 0.5 * r_ohm
    
    pts_esr, pts_v = [], []
    for i in range(0, 71):
        T = Tmin + i
        r = esr_model(T)
        v = v_loaded(T)
        pts_esr.append("%.1f,%.1f" % (px(T), py_esr(min(1200.0, r))))
        pts_v.append("%.1f,%.1f" % (px(T), py_v(max(2.0, min(4.2, v)))))
    
    # Лінія порогу UVLO / Brownout Reset (2.8 В)
    y_uvlo = py_v(2.8)
    frags.append(line(x0, y_uvlo, x_right, y_uvlo, POS, 1.4, dash="5,4"))
    frags.append(text(x0 + 130, y_uvlo - 7, "Поріг відсічки живлення MCU / UVLO = 2.80 В", size=11, color=POS, bold=True))
    
    # Криві
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts_esr), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts_v), NEG))
    
    # Зона небезпечного провалу напруги нижче UVLO (T < -15 °C)
    t_crit = -15.0
    x_crit = px(t_crit)
    frags.append(line(x_crit, y0, x_crit, y0 - h, MUTED, 1.2, dash="3,3"))
    frags.append(circle(x_crit, y_uvlo, 5.0, fill="#ffffff", stroke=POS, sw=2))
    
    # Підпис критичної точки
    tb, _, _ = textbox(x_crit - 85, y_uvlo + 42, "T < -15 °C:\nПровал напруги\n→ Brownout Reset",
                       size=10.5, pad=6, fill="#fff0f0", stroke=POS)
    frags.append(tb)
    
    # Легенда
    lx = x0 + 15
    frags.append(line(lx, 74, lx + 30, 74, POS, 2.8))
    frags.append(text(lx + 36, 78, "Внутрішній опір комірки ESR (мОм)", size=11.5, color=INK, anchor="start"))
    frags.append(line(lx + 270, 74, lx + 300, 74, NEG, 2.8))
    frags.append(text(lx + 306, 78, "Напруга на клемах при імпульсі 500 мА", size=11.5, color=INK, anchor="start"))
    
    render(os.path.join(IMG, 'battery-esr-and-voltage-sag.svg'), W, H, *frags)


# ── 2. Схема: Випадання конденсату під BGA/QFN та електрохімічна міграція ─────
def fig_dew_point_bga():
    W, H = 780, 460
    
    frags = [
        text(W / 2, 28, "Фізика конденсату під BGA-чипом та утворення струмопровідних дендритів", size=15.5, bold=True),
        text(W / 2, 48, "При переході з холоду в тепло капілярний ефект втягує росу під корпус; виникає електрохімічна міграція",
             size=11.5, color=MUTED, italic=True)
    ]
    
    # Підкладка PCB
    pcb_y = 230
    frags.append(rect(60, pcb_y, 660, 24, fill="#27ae60", stroke="#1e8449", sw=1.5, rx=3))
    frags.append(text(80, pcb_y + 16, "Текстоліт PCB (холодна маса, -20 °C)", size=11, color="#ffffff", bold=True, anchor="start"))
    
    # Корпус BGA
    chip_y = 120
    chip_w = 420
    chip_x = (W - chip_w) / 2
    frags.append(rect(chip_x, chip_y, chip_w, 40, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    frags.append(text(W / 2, chip_y + 25, "Мікроконтролер / SoC (корпус BGA / QFN)", size=12.5, color="#ffffff", bold=True))
    
    # Кульки припою (BGA solder balls)
    ball_y = chip_y + 40
    ball_h = pcb_y - ball_y
    ball_xs = [chip_x + 35 + i * 50 for i in range(8)]
    
    # Водяна плівка (конденсат) у зазорі
    frags.append(rect(chip_x - 15, ball_y + 8, chip_w + 30, ball_h - 16, fill="#d4e6f1", stroke="#85c1e9", sw=1.2, rx=4))
    frags.append(text(W / 2, ball_y + 24, "Затягнута водяна плівка (капілярний конденсат + іони флюсу)", size=10.5, color=NEG, bold=True))
    
    for idx, bx in enumerate(ball_xs):
        # контактний майданчик зверху й знизу
        frags.append(rect(bx - 12, chip_y + 38, 24, 4, fill="#f39c12", stroke="#d68910", sw=1, rx=1))
        frags.append(rect(bx - 12, pcb_y - 2, 24, 4, fill="#f39c12", stroke="#d68910", sw=1, rx=1))
        
        # кулька припою
        b_color = "#bdc3c7"
        if idx == 2:
            # Анод (VBAT = 3.3 В)
            frags.append(circle(bx, (ball_y + pcb_y) / 2, 14, fill=b_color, stroke=POS, sw=2))
            frags.append(text(bx, pcb_y + 38, "VCC / VBAT\n(+3.3 В, Анод)", size=10, color=POS, bold=True))
        elif idx == 3:
            # Катод (GND = 0 В)
            frags.append(circle(bx, (ball_y + pcb_y) / 2, 14, fill=b_color, stroke=NEG, sw=2))
            frags.append(text(bx, pcb_y + 38, "GND\n(0 В, Катод)", size=10, color=NEG, bold=True))
        else:
            frags.append(circle(bx, (ball_y + pcb_y) / 2, 14, fill=b_color, stroke="#7f8c8d", sw=1.5))
            frags.append(text(bx, pcb_y + 38, "GPIO %d" % idx, size=9.5, color=MUTED))
            
    # Дендрит між кулькою 2 та 3
    b2_x = ball_xs[2]
    b3_x = ball_xs[3]
    mid_y = (ball_y + pcb_y) / 2
    
    # Зигзагоподібний дендрит від GND (катода) до VCC (анода)
    dendrite_pts = [
        "%.1f,%.1f" % (b3_x - 14, mid_y),
        "%.1f,%.1f" % (b3_x - 22, mid_y - 4),
        "%.1f,%.1f" % (b3_x - 28, mid_y + 3),
        "%.1f,%.1f" % (b3_x - 34, mid_y - 2),
        "%.1f,%.1f" % (b2_x + 14, mid_y)
    ]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(dendrite_pts), POS))
    frags.append(text((b2_x + b3_x) / 2, mid_y - 12, "Дендрит (Cu/Sn)", size=10, color=POS, bold=True))
    
    # Стрілка теплого вологого повітря
    frags.append(arrow(110, 85, 170, 115, POS, 2.0))
    frags.append(text(105, 75, "Тепле вологе повітря (+22 °C, RH 70%)", size=11, color=POS, bold=True, anchor="start"))
    
    # Нижня панель: 3 етапи руйнування
    box1, _, _ = textbox(160, 395, "1. Термічний перехід\nХолодна плата (-20 °C)\nохолоджує повітря < T_роси",
                         size=10.5, pad=6, fill="#f4f6f8", stroke=MUTED)
    box2, _, _ = textbox(400, 395, "2. Капілярний ефект\nВода затягується під BGA\nі розчиняє залишки солей",
                         size=10.5, pad=6, fill="#ebf5fb", stroke=NEG)
    box3, _, _ = textbox(635, 395, "3. Електрохімічна міграція\nІони металу утворюють місток\n→ КЗ та корозія доріжок",
                         size=10.5, pad=6, fill="#fdf2e9", stroke=POS)
    
    frags += [box1, box2, box3]
    frags.append(arrow(255, 395, 305, 395, LINE, 1.5))
    frags.append(arrow(495, 395, 545, 395, LINE, 1.5))
    
    render(os.path.join(IMG, 'dew-point-condensation-bga.svg'), W, H, *frags)


# ── 3. Графік: Дрейф частоти кварців: Парабола (32 кГц) проти Кубіки (AT-cut) ──
def fig_quartz_drift():
    W, H = 760, 480
    x0, y0, w, h = 90, 400, 600, 310
    cy = y0 - h * 0.70  # рівень Δf/f = 0
    
    frags = [
        text(W / 2, 28, "Температурний дрейф частоти: годинниковий 32.768 кГц проти AT-зрізу", size=15.5, bold=True),
        text(W / 2, 48, "Камертонний кварц RTC падає за параболою до -150 ppm при -40 °C (відставання 13 с/добу)",
             size=12, color=MUTED, italic=True)
    ]
    frags += _axes(x0, y0, w, h, "температура T, °C", "відхилення Δf/f, ppm")
    
    # горизонталь нуля
    frags.append(line(x0, cy, x0 + w, cy, MUTED, 1.0, dash="4,4"))
    frags.append(text(x0 - 8, cy + 4, "0", size=11, color=MUTED, anchor="end"))
    
    Tmin, Tmax = -40.0, 85.0
    def px(T): return x0 + (T - Tmin) / (Tmax - Tmin) * w
    
    for T in (-40, -20, 0, 25, 50, 70, 85):
        xx = px(T)
        frags.append(line(xx, y0, xx, y0 + 5, INK, 1.3))
        frags.append(text(xx, y0 + 19, str(T), size=11, color=MUTED))
    
    # Шкала Y: -180 .. +40 ppm
    ppm_min, ppm_max = -180.0, 40.0
    def py(v): return cy - (v / ppm_max) * (cy - (y0 - h)) if v >= 0 else cy - (v / ppm_min) * (y0 - cy)
    
    for v in (-150, -100, -50, 0, 25):
        if v == 0: continue
        yy = py(v)
        frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2))
        frags.append(text(x0 - 8, yy + 4, "%+d" % v, size=10.5, color=MUTED, anchor="end"))
    
    # 1. Tuning fork 32.768 kHz: Δf/f = -0.035 * (T - 25)^2
    pts_rtc = []
    for i in range(0, 126):
        T = Tmin + i
        v = -0.035 * ((T - 25.0) ** 2)
        pts_rtc.append("%.1f,%.1f" % (px(T), py(max(ppm_min, v))))
    
    # 2. AT-cut 16 MHz: Δf/f = a1*(T-25) + a3*(T-25)^3  (кубічна, ±25 ppm)
    pts_at = []
    for i in range(0, 126):
        T = Tmin + i
        d = T - 25.0
        v = -0.25 * d + 0.00012 * (d ** 3)
        pts_at.append("%.1f,%.1f" % (px(T), py(v)))
    
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (" ".join(pts_rtc), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_at), NEG))
    
    # Вершина параболи при 25 °C
    frags.append(circle(px(25), py(0), 4.5, fill="#fff", stroke=POS, sw=2))
    frags.append(text(px(25), py(0) - 10, "Вершина T₀ = +25 °C", size=10.5, color=POS, bold=True))
    
    # Точка -40 °C для RTC
    v_m40 = -0.035 * ((-40.0 - 25.0) ** 2)
    frags.append(circle(px(-40), py(v_m40), 5.0, fill="#fff", stroke=POS, sw=2))
    frags.append(text(px(-40) + 12, py(v_m40) - 8, "-40 °C: -148 ppm (-13 с/добу)", size=10.5, color=POS, bold=True, anchor="start"))
    
    # Легенда
    lx = x0 + 170
    frags.append(line(lx, 74, lx + 30, 74, POS, 3.0))
    frags.append(text(lx + 36, 78, "32.768 кГц (RTC, камертонний зріз — парабола)", size=11.5, color=INK, anchor="start"))
    frags.append(line(lx, 94, lx + 30, 94, NEG, 2.6))
    frags.append(text(lx + 36, 98, "16 МГц (AT-cut, високочастотний — кубічна крива)", size=11.5, color=INK, anchor="start"))
    
    render(os.path.join(IMG, 'quartz-drift-curves.svg'), W, H, *frags)


# ── 4. Блок-схема: Алгоритм та кінцевий автомат холодного старту ────────────────
def fig_cold_boot():
    W, H = 760, 480
    
    frags = [
        text(W / 2, 26, "Алгоритм адаптивного холодного старту вбудованої системи", size=16, bold=True),
        text(W / 2, 46, "Ступеневе розігрівання, захист від Brownout Reset та блокування заряду при T < 0 °C",
             size=12, color=MUTED, italic=True)
    ]
    
    # Блоки зверху вниз
    # 1. Подача живлення / Reset
    b1, w1, h1 = textbox(380, 85, "1. Старт ядра від вбудованого генератора (HSI / LSI)\n(Зовнішній кварц вимкнено, частота ядра знижена)",
                         size=11, pad=8, fill="#f4f6f8", stroke=LINE)
    
    # 2. Зчитування температури
    b2, w2, h2 = textbox(380, 160, "2. Вимірювання температури NTC / давача кристала\nОцінка точки роси та залишкового ESR батареї",
                         size=11, pad=8, fill="#eaf2f8", stroke=NEG)
    
    # 3. Розгалуження за температурою
    # Ліва гілка: Холодний режим (T < -10 °C)
    b3_cold, w3_c, h3_c = textbox(200, 260, "Режим «Глибокий холод» (T < -10 °C)\n• Увімкнення PCB Heater / Dummy Burn\n• Струм розряду обмежено (C/10)\n• Блокування заряджання при T < 0 °C",
                                  size=10.5, pad=8, fill="#fef9e7", stroke=POS)
    
    # Права гілка: Нормальний режим (T >= -10 °C)
    b3_norm, w3_n, h3_n = textbox(560, 260, "Режим «Нормальний старт»\n• ESR батареї в нормі\n• Запуск HSE кварцу з таймаутом\n• Перевірка працездатності LCD/OLED",
                                  size=10.5, pad=8, fill="#eafaf1", stroke=FIELD)
    
    # 4. Прогрів досяг порогу
    b4, w4, h4 = textbox(380, 360, "4. Валідація стабільності кварцу та напруги VBAT\nПеремикання тактування на PLL/HSE після виходу на режим",
                         size=11, pad=8, fill="#f4f6f8", stroke=LINE)
    
    # 5. Повнофункціональна робота
    b5, w5, h5 = textbox(380, 435, "5. Активація радіотракту (LTE/Wi-Fi) та периферії\nСтупеневе нарощування потужності",
                         size=11, pad=8, fill="#ebf5fb", stroke=NEG, bold=True)
    
    frags += [b1, b2, b3_cold, b3_norm, b4, b5]
    
    # Стрілки
    frags.append(arrow(380, 85 + h1 / 2, 380, 160 - h2 / 2, LINE, 1.8))
    
    # Розгалуження від блоку 2
    frags.append(arrow(380 - w2 / 4, 160 + h2 / 2, 200, 260 - h3_c / 2, POS, 1.8))
    frags.append(arrow(380 + w2 / 4, 160 + h2 / 2, 560, 260 - h3_n / 2, FIELD, 1.8))
    frags.append(text(250, 205, "T < -10 °C", size=10.5, color=POS, bold=True))
    frags.append(text(510, 205, "T ≥ -10 °C", size=10.5, color=FIELD, bold=True))
    
    # Зведення в блок 4
    frags.append(arrow(200, 260 + h3_c / 2, 380 - w4 / 4, 360 - h4 / 2, POS, 1.8))
    frags.append(text(250, 325, "Прогрів завершено", size=10, color=POS))
    
    frags.append(arrow(560, 260 + h3_n / 2, 380 + w4 / 4, 360 - h4 / 2, FIELD, 1.8))
    
    # Стрілка до блоку 5
    frags.append(arrow(380, 360 + h4 / 2, 380, 435 - h5 / 2, LINE, 1.8))
    
    render(os.path.join(IMG, 'cold-boot-sequence.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_battery_esr_sag()
    fig_dew_point_bga()
    fig_quartz_drift()
    fig_cold_boot()
    print("OK: 4 figures generated in", IMG)
