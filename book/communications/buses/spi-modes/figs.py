# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра для сигналів
CLK = NEG          # SCLK — синій
DAT = "#7a5fb0"    # MOSI/MISO — фіолетовий
CAP = FIELD        # Вибірка (захоплення) — зелений
CHG = POS          # Зміна даних (виштовхування) — червоний
CS_CLR = "#d35400"  # Chip Select — помаранчевий
GRID_CLR = "#e5e7eb"

def draw_bus_data(x_starts, bit_labels, ymid, amp, fill_color="#f8f9fa"):
    """Малює осередки шини даних (очі/діаманти) з підписами бітів."""
    frags = []
    h = amp
    for i in range(len(x_starts) - 1):
        x1 = x_starts[i]
        x2 = x_starts[i+1]
        w = x2 - x1
        cx = (x1 + x2) / 2
        # Скошені кути для зміни біта
        pts = [
            (x1 + 4, ymid - h), (x2 - 4, ymid - h),
            (x2, ymid),
            (x2 - 4, ymid + h), (x1 + 4, ymid + h),
            (x1, ymid)
        ]
        poly_pts = " ".join("%.1f,%.1f" % p for p in pts)
        frags.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (poly_pts, fill_color, DAT))
        if i < len(bit_labels):
            frags.append(text(cx, ymid + 4, bit_labels[i], size=11, color=INK, bold=True))
    return "".join(frags)

# ─────────────────────────────────────────────────────────────────────────────
# 1. modes-matrix.svg : 2x2 матриця режимів SPI (CPOL/CPHA)
# ─────────────────────────────────────────────────────────────────────────────
def make_modes_matrix():
    w, h = 820, 480
    frags = []
    
    # Заголовок та шапка колонок/рядків
    frags.append(text(w / 2, 30, "Матриця чотирьох режимів SPI (Motorola)", size=18, bold=True))
    
    # Колонки (CPOL)
    frags.append(textbox(290, 75, "CPOL = 0\n(SCLK спокій = 0 В, низький)", size=13, pad=8, fill="#eef2ff", stroke=NEG)[0])
    frags.append(textbox(610, 75, "CPOL = 1\n(SCLK спокій = 3.3 В, високий)", size=13, pad=8, fill="#fef2f2", stroke=POS)[0])
    
    # Рядки (CPHA)
    frags.append(textbox(85, 195, "CPHA = 0\n1-й фронт:\nвибірка даних", size=13, pad=8, fill="#f0fdf4", stroke=FIELD)[0])
    frags.append(textbox(85, 365, "CPHA = 1\n2-й фронт:\nвибірка даних", size=13, pad=8, fill="#fffbeb", stroke="#d97706")[0])
    
    # Картки 4 режимів
    # Mode 0
    m0_body = [
        "Mode 0 (0, 0)",
        "• 1-й фронт (наростання): ВИБІРКА (Sample)",
        "• 2-й фронт (спадання): ЗМІНА (Shift)",
        "• MSB виставляється по спаду /CS",
        "★ Стандарт де-факто (Flash, SD, АЦП)"
    ]
    frags.append(fitbox(170, 120, 240, 150, "\n".join(m0_body), size=12, pad=10, fill="#ffffff", stroke=LINE, sw=2))
    
    # Mode 2
    m2_body = [
        "Mode 2 (1, 0)",
        "• 1-й фронт (спадання): ВИБІРКА (Sample)",
        "• 2-й фронт (наростання): ЗМІНА (Shift)",
        "• MSB виставляється по спаду /CS",
        "Рідкісний інверсний режим"
    ]
    frags.append(fitbox(490, 120, 240, 150, "\n".join(m2_body), size=12, pad=10, fill="#ffffff", stroke=LINE, sw=1.5))
    
    # Mode 1
    m1_body = [
        "Mode 1 (0, 1)",
        "• 1-й фронт (наростання): ЗМІНА (Shift)",
        "• 2-й фронт (спадання): ВИБІРКА (Sample)",
        "• MSB виставляється на 1-му фронті SCLK",
        "Використовується в деяких DSP / ASIC"
    ]
    frags.append(fitbox(170, 290, 240, 150, "\n".join(m1_body), size=12, pad=10, fill="#ffffff", stroke=LINE, sw=1.5))
    
    # Mode 3
    m3_body = [
        "Mode 3 (1, 1)",
        "• 1-й фронт (спадання): ЗМІНА (Shift)",
        "• 2-й фронт (наростання): ВИБІРКА (Sample)",
        "• MSB виставляється на 1-му фронті SCLK",
        "★ Стандарт Flash-пам'яті (сумісний з Mode 0)"
    ]
    frags.append(fitbox(490, 290, 240, 150, "\n".join(m3_body), size=12, pad=10, fill="#ffffff", stroke=LINE, sw=2))
    
    render(os.path.join(OUT, "modes-matrix.svg"), w, h, "".join(frags))

# ─────────────────────────────────────────────────────────────────────────────
# 2. mode0-mode1-timing.svg : Детальні часові діаграми Mode 0 та Mode 1 (CPOL=0)
# ─────────────────────────────────────────────────────────────────────────────
def make_mode0_mode1_timing():
    w, h = 880, 520
    frags = []
    
    frags.append(text(w / 2, 28, "Часові діаграми CPOL = 0: Mode 0 (CPHA=0) та Mode 1 (CPHA=1)", size=16, bold=True))
    
    # Розділ Mode 0
    frags.append(textbox(90, 65, "Mode 0 (0,0)\nСпокій SCLK = 0\nВибірка на 1-му", size=12, pad=6, fill="#f0fdf4", stroke=FIELD)[0])
    
    # Сигнали Mode 0
    # Часові координати
    t_cs_fall = 170
    t_edges_m0 = [220, 270, 320, 370, 420, 470, 520, 570] # 4 імпульси = 8 фронтів
    t_cs_rise = 620
    
    # Сітка стробів для Mode 0
    for i, x in enumerate(t_edges_m0):
        is_sample = (i % 2 == 0) # парні індекси (0, 2, 4, 6) = 1-й фронт такту (наростання)
        clr = CAP if is_sample else CHG
        dash = "3,3"
        frags.append(line(x, 90, x, 240, color=clr, sw=1.2, dash=dash))
        if is_sample:
            frags.append(arrow(x, 88, x, 108, color=CAP, sw=1.6))
            frags.append(text(x, 82, "Smpl", size=10, color=CAP, bold=True))
        else:
            frags.append(arrow(x, 88, x, 108, color=CHG, sw=1.6))
            frags.append(text(x, 82, "Shift", size=10, color=CHG, bold=True))
            
    # /CS
    frags.append(text(150, 115, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    cs_pts_m0 = [(155, 105), (t_cs_fall, 105), (t_cs_fall, 125), (t_cs_rise, 125), (t_cs_rise, 105), (650, 105)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in cs_pts_m0), CS_CLR))
    
    # SCLK (CPOL=0)
    frags.append(text(150, 165, "SCLK", size=12, color=CLK, bold=True, anchor="end"))
    sclk_pts_m0 = [(155, 175), (t_edges_m0[0], 175)]
    for i in range(0, len(t_edges_m0), 2):
        sclk_pts_m0.extend([
            (t_edges_m0[i], 150),
            (t_edges_m0[i+1], 150),
            (t_edges_m0[i+1], 175),
            (t_edges_m0[i+2] if i+2 < len(t_edges_m0) else t_cs_rise + 10, 175)
        ])
    sclk_pts_m0.append((650, 175))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_pts_m0), CLK))
    
    # DATA (MOSI / MISO) Mode 0
    frags.append(text(150, 215, "DATA", size=12, color=DAT, bold=True, anchor="end"))
    # Лінія в Hi-Z до CS fall
    frags.append(line(155, 215, t_cs_fall, 215, color=MUTED, sw=1.5, dash="4,4"))
    # Осередки даних: Bit 7 виставляється по спаду CS!
    data_x_m0 = [t_cs_fall, t_edges_m0[1], t_edges_m0[3], t_edges_m0[5], t_edges_m0[7], t_cs_rise]
    frags.append(draw_bus_data(data_x_m0, ["Bit 7 (MSB)", "Bit 6", "Bit 5", "Bit 4", "Bit 3"], 215, 14))
    frags.append(line(t_cs_rise, 215, 650, 215, color=MUTED, sw=1.5, dash="4,4"))
    
    # Позначка t_CSS
    frags.append(line(t_cs_fall, 245, t_edges_m0[0], 245, color=LINE, sw=1.2))
    frags.append(text((t_cs_fall + t_edges_m0[0]) / 2, 258, "t_CSS (підготовка MSB)", size=11, color=INK, bold=True))
    
    # Розділювач
    frags.append(line(40, 275, 840, 275, color=GRID_CLR, sw=2))
    
    # Розділ Mode 1
    frags.append(textbox(90, 315, "Mode 1 (0,1)\nСпокій SCLK = 0\nВибірка на 2-му", size=12, pad=6, fill="#fffbeb", stroke="#d97706")[0])
    
    t_edges_m1 = [220, 270, 320, 370, 420, 470, 520, 570]
    
    # Сітка стробів для Mode 1
    for i, x in enumerate(t_edges_m1):
        is_shift = (i % 2 == 0) # 1-й фронт = ЗМІНА
        clr = CHG if is_shift else CAP
        dash = "3,3"
        frags.append(line(x, 340, x, 490, color=clr, sw=1.2, dash=dash))
        if is_shift:
            frags.append(arrow(x, 338, x, 358, color=CHG, sw=1.6))
            frags.append(text(x, 332, "Shift", size=10, color=CHG, bold=True))
        else:
            frags.append(arrow(x, 338, x, 358, color=CAP, sw=1.6))
            frags.append(text(x, 332, "Smpl", size=10, color=CAP, bold=True))
            
    # /CS
    frags.append(text(150, 365, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    cs_pts_m1 = [(155, 355), (t_cs_fall, 355), (t_cs_fall, 375), (t_cs_rise, 375), (t_cs_rise, 355), (650, 355)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in cs_pts_m1), CS_CLR))
    
    # SCLK (CPOL=0)
    frags.append(text(150, 415, "SCLK", size=12, color=CLK, bold=True, anchor="end"))
    sclk_pts_m1 = [(155, 425), (t_edges_m1[0], 425)]
    for i in range(0, len(t_edges_m1), 2):
        sclk_pts_m1.extend([
            (t_edges_m1[i], 400),
            (t_edges_m1[i+1], 400),
            (t_edges_m1[i+1], 425),
            (t_edges_m1[i+2] if i+2 < len(t_edges_m1) else t_cs_rise + 10, 425)
        ])
    sclk_pts_m1.append((650, 425))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_pts_m1), CLK))
    
    # DATA Mode 1: Bit 7 виставляється на 1-му фронті SCLK!
    frags.append(text(150, 465, "DATA", size=12, color=DAT, bold=True, anchor="end"))
    frags.append(line(155, 465, t_edges_m1[0], 465, color=MUTED, sw=1.5, dash="4,4"))
    data_x_m1 = [t_edges_m1[0], t_edges_m1[2], t_edges_m1[4], t_edges_m1[6], t_cs_rise]
    frags.append(draw_bus_data(data_x_m1, ["Bit 7 (MSB)", "Bit 6", "Bit 5", "Bit 4"], 465, 14))
    frags.append(line(t_cs_rise, 465, 650, 465, color=MUTED, sw=1.5, dash="4,4"))
    
    # Підказка справа
    legend_box = [
        "Позначення стробів:",
        "▲ Smpl (зелений): момент",
        "  фіксації сигналу D-тригером",
        "▼ Shift (червоний): момент",
        "  перемикання зсувного регістра"
    ]
    frags.append(fitbox(670, 180, 195, 160, "\n".join(legend_box), size=11, pad=8, fill="#f8fafc", stroke=MUTED))
    
    render(os.path.join(OUT, "mode0-mode1-timing.svg"), w, h, "".join(frags))

# ─────────────────────────────────────────────────────────────────────────────
# 3. mode2-mode3-timing.svg : Детальні часові діаграми Mode 2 та Mode 3 (CPOL=1)
# ─────────────────────────────────────────────────────────────────────────────
def make_mode2_mode3_timing():
    w, h = 880, 520
    frags = []
    
    frags.append(text(w / 2, 28, "Часові діаграми CPOL = 1: Mode 2 (CPHA=0) та Mode 3 (CPHA=1)", size=16, bold=True))
    
    # Розділ Mode 2
    frags.append(textbox(90, 65, "Mode 2 (1,0)\nСпокій SCLK = 1\nВибірка на 1-му", size=12, pad=6, fill="#fef2f2", stroke=POS)[0])
    
    t_cs_fall = 170
    t_edges = [220, 270, 320, 370, 420, 470, 520, 570]
    t_cs_rise = 620
    
    # Сітка стробів для Mode 2
    for i, x in enumerate(t_edges):
        is_sample = (i % 2 == 0) # 1-й фронт = СПАДАННЯ (вибірка)
        clr = CAP if is_sample else CHG
        dash = "3,3"
        frags.append(line(x, 90, x, 240, color=clr, sw=1.2, dash=dash))
        if is_sample:
            frags.append(arrow(x, 88, x, 108, color=CAP, sw=1.6))
            frags.append(text(x, 82, "Smpl", size=10, color=CAP, bold=True))
        else:
            frags.append(arrow(x, 88, x, 108, color=CHG, sw=1.6))
            frags.append(text(x, 82, "Shift", size=10, color=CHG, bold=True))
            
    # /CS
    frags.append(text(150, 115, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    cs_pts = [(155, 105), (t_cs_fall, 105), (t_cs_fall, 125), (t_cs_rise, 125), (t_cs_rise, 105), (650, 105)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in cs_pts), CS_CLR))
    
    # SCLK (CPOL=1, спокій = HIGH = 150)
    frags.append(text(150, 165, "SCLK", size=12, color=CLK, bold=True, anchor="end"))
    sclk_pts_m2 = [(155, 150), (t_edges[0], 150)]
    for i in range(0, len(t_edges), 2):
        sclk_pts_m2.extend([
            (t_edges[i], 175),
            (t_edges[i+1], 175),
            (t_edges[i+1], 150),
            (t_edges[i+2] if i+2 < len(t_edges) else t_cs_rise + 10, 150)
        ])
    sclk_pts_m2.append((650, 150))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_pts_m2), CLK))
    
    # DATA Mode 2: Bit 7 по спаду CS
    frags.append(text(150, 215, "DATA", size=12, color=DAT, bold=True, anchor="end"))
    frags.append(line(155, 215, t_cs_fall, 215, color=MUTED, sw=1.5, dash="4,4"))
    data_x_m2 = [t_cs_fall, t_edges[1], t_edges[3], t_edges[5], t_edges[7], t_cs_rise]
    frags.append(draw_bus_data(data_x_m2, ["Bit 7 (MSB)", "Bit 6", "Bit 5", "Bit 4", "Bit 3"], 215, 14))
    frags.append(line(t_cs_rise, 215, 650, 215, color=MUTED, sw=1.5, dash="4,4"))
    
    # Розділювач
    frags.append(line(40, 275, 840, 275, color=GRID_CLR, sw=2))
    
    # Розділ Mode 3
    frags.append(textbox(90, 315, "Mode 3 (1,1)\nСпокій SCLK = 1\nВибірка на 2-му", size=12, pad=6, fill="#fdf2f8", stroke="#db2777")[0])
    
    # Сітка стробів для Mode 3
    for i, x in enumerate(t_edges):
        is_shift = (i % 2 == 0) # 1-й фронт (спадання) = ЗМІНА
        clr = CHG if is_shift else CAP
        dash = "3,3"
        frags.append(line(x, 340, x, 490, color=clr, sw=1.2, dash=dash))
        if is_shift:
            frags.append(arrow(x, 338, x, 358, color=CHG, sw=1.6))
            frags.append(text(x, 332, "Shift", size=10, color=CHG, bold=True))
        else:
            frags.append(arrow(x, 338, x, 358, color=CAP, sw=1.6))
            frags.append(text(x, 332, "Smpl", size=10, color=CAP, bold=True))
            
    # /CS
    frags.append(text(150, 365, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    cs_pts_m3 = [(155, 355), (t_cs_fall, 355), (t_cs_fall, 375), (t_cs_rise, 375), (t_cs_rise, 355), (650, 355)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in cs_pts_m3), CS_CLR))
    
    # SCLK (CPOL=1, спокій = HIGH = 400)
    frags.append(text(150, 415, "SCLK", size=12, color=CLK, bold=True, anchor="end"))
    sclk_pts_m3 = [(155, 400), (t_edges[0], 400)]
    for i in range(0, len(t_edges), 2):
        sclk_pts_m3.extend([
            (t_edges[i], 425),
            (t_edges[i+1], 425),
            (t_edges[i+1], 400),
            (t_edges[i+2] if i+2 < len(t_edges) else t_cs_rise + 10, 400)
        ])
    sclk_pts_m3.append((650, 400))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_pts_m3), CLK))
    
    # DATA Mode 3: Bit 7 виставляється на 1-му фронті (спадання SCLK)
    frags.append(text(150, 465, "DATA", size=12, color=DAT, bold=True, anchor="end"))
    frags.append(line(155, 465, t_edges[0], 465, color=MUTED, sw=1.5, dash="4,4"))
    data_x_m3 = [t_edges[0], t_edges[2], t_edges[4], t_edges[6], t_cs_rise]
    frags.append(draw_bus_data(data_x_m3, ["Bit 7 (MSB)", "Bit 6", "Bit 5", "Bit 4"], 465, 14))
    frags.append(line(t_cs_rise, 465, 650, 465, color=MUTED, sw=1.5, dash="4,4"))
    
    # Підказка справа
    legend_box = [
        "Інверсія полярності CPOL=1:",
        "• 1-й фронт завжди спадний",
        "• 2-й фронт завжди наростаючий",
        "• У Mode 3 вибірка знову",
        "  відбувається за наростанням!"
    ]
    frags.append(fitbox(670, 180, 195, 160, "\n".join(legend_box), size=11, pad=8, fill="#f8fafc", stroke=MUTED))
    
    render(os.path.join(OUT, "mode2-mode3-timing.svg"), w, h, "".join(frags))

# ─────────────────────────────────────────────────────────────────────────────
# 4. dual-mode-0-3.svg : Чому мікросхеми сумісні одночасно з Mode 0 та Mode 3
# ─────────────────────────────────────────────────────────────────────────────
def make_dual_mode_0_3():
    w, h = 860, 460
    frags = []
    
    frags.append(text(w / 2, 28, "Секрет дуальної сумісності Mode 0 та Mode 3 (Flash-пам'ять, АЦП)", size=16, bold=True))
    
    t_cs_fall = 160
    # Фронти: наростання при x=220, 320, 420; спадання при x=270, 370, 470
    t_rises = [220, 320, 420, 520]
    t_falls = [270, 370, 470, 570]
    t_cs_rise = 620
    
    # Вертикальні лінії для наростань (ВИБІРКА в обох режимах!)
    for xr in t_rises:
        frags.append(line(xr, 60, xr, 340, color=CAP, sw=1.5, dash="3,3"))
        frags.append(text(xr, 55, "▲ Вибірка", size=10, color=CAP, bold=True))
        
    # Вертикальні лінії для спадань (ЗМІНА в обох режимах!)
    for xf in t_falls:
        frags.append(line(xf, 60, xf, 340, color=CHG, sw=1.5, dash="3,3"))
        frags.append(text(xf, 55, "▼ Зміна", size=10, color=CHG, bold=True))
        
    # /CS
    frags.append(text(140, 95, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    cs_pts = [(145, 85), (t_cs_fall, 85), (t_cs_fall, 105), (t_cs_rise, 105), (t_cs_rise, 85), (660, 85)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in cs_pts), CS_CLR))
    
    # Mode 0 SCLK
    frags.append(text(140, 150, "SCLK (Mode 0)", size=12, color=CLK, bold=True, anchor="end"))
    sclk_m0 = [(145, 160), (t_rises[0], 160)]
    for i in range(len(t_rises)):
        sclk_m0.extend([
            (t_rises[i], 135),
            (t_falls[i], 135),
            (t_falls[i], 160),
            (t_rises[i+1] if i+1 < len(t_rises) else t_cs_rise + 10, 160)
        ])
    sclk_m0.append((660, 160))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_m0), CLK))
    
    # Mode 3 SCLK
    frags.append(text(140, 225, "SCLK (Mode 3)", size=12, color=CLK, bold=True, anchor="end"))
    # Mode 3: спадання відбувається ПЕРШИМ на початку першого біта або в точці t_cs_fall / t_falls[0]
    # На діаграмі Mode 3: в спокої SCLK=1 (210). Після CS fall перший фронт - це спад при t_falls_pre або при першому напівперіоді
    # У класичному Flash: SCLK у Mode 3 утримується на 1, а перший спад відбувається перед наростанням (x=180)
    t_first_fall_m3 = 175
    frags.append(line(t_first_fall_m3, 200, t_first_fall_m3, 340, color=CHG, sw=1.2, dash="3,3"))
    frags.append(text(t_first_fall_m3, 352, "Поч. спад", size=9, color=CHG))
    
    sclk_m3 = [(145, 210), (t_first_fall_m3, 210), (t_first_fall_m3, 235), (t_rises[0], 235)]
    for i in range(len(t_rises)):
        sclk_m3.extend([
            (t_rises[i], 210),
            (t_falls[i], 210),
            (t_falls[i], 235),
            (t_rises[i+1] if i+1 < len(t_rises) else t_cs_rise + 10, 235)
        ])
    sclk_m3.append((660, 210))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_m3), CLK))
    
    # DATA (однакова для обох!)
    frags.append(text(140, 295, "DATA (Спільна)", size=12, color=DAT, bold=True, anchor="end"))
    data_x = [t_cs_fall, t_falls[0], t_falls[1], t_falls[2], t_cs_rise]
    frags.append(draw_bus_data(data_x, ["Bit 7 (MSB)", "Bit 6", "Bit 5", "Bit 4"], 295, 14))
    
    # Пояснювальний блок унизу
    explain_txt = (
        "Чому це працює без перемикання регістра веденого:\n"
        "1. В обох режимах ВИБІРКА відбувається точно на НАРОСТАЮЧОМУ фронті (0→1), коли лінія стабільна.\n"
        "2. В обох режимах ЗМІНА даних відбувається точно на СПАДНОМУ фронті (1→0).\n"
        "3. Різниця лише в рівні SCLK під час неактивного /CS (HIGH vs LOW), який ведений просто ігнорує!"
    )
    frags.append(fitbox(50, 370, 760, 80, explain_txt, size=11, pad=8, fill="#f0fdf4", stroke=FIELD))
    
    render(os.path.join(OUT, "dual-mode-0-3.svg"), w, h, "".join(frags))

# ─────────────────────────────────────────────────────────────────────────────
# 5. cpha-mismatch-shift.svg : Зсув на 1 біт через неузгодженість CPHA
# ─────────────────────────────────────────────────────────────────────────────
def make_cpha_mismatch_shift():
    w, h = 880, 470
    frags = []
    
    frags.append(text(w / 2, 28, "Пастка невідповідності CPHA: втрата MSB та зміщення потоку бітів", size=16, bold=True))
    
    t_cs_fall = 160
    t_edges = [210, 260, 310, 360, 410, 460, 510, 560]
    t_cs_rise = 610
    
    # SCLK (Ведучий у Mode 0: CPOL=0, CPHA=0)
    frags.append(text(140, 85, "SCLK (Mode 0)", size=12, color=CLK, bold=True, anchor="end"))
    sclk_pts = [(145, 95), (t_edges[0], 95)]
    for i in range(0, len(t_edges), 2):
        sclk_pts.extend([
            (t_edges[i], 70),
            (t_edges[i+1], 70),
            (t_edges[i+1], 95),
            (t_edges[i+2] if i+2 < len(t_edges) else t_cs_rise + 10, 95)
        ])
    sclk_pts.append((650, 95))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_pts), CLK))
    
    # Ведений налаштований на Mode 1 (CPHA=1): виставляє дані за 1-м наростанням SCLK!
    frags.append(text(140, 160, "MISO Веденого\n(Mode 1)", size=11, color=DAT, bold=True, anchor="end"))
    frags.append(line(145, 160, t_edges[0], 160, color=MUTED, sw=1.5, dash="4,4"))
    # Зміна бітів веденим у точках t_edges[0], t_edges[2], t_edges[4]...
    miso_x = [t_edges[0], t_edges[2], t_edges[4], t_edges[6], t_cs_rise]
    frags.append(draw_bus_data(miso_x, ["D7 (MSB)", "D6", "D5", "D4"], 160, 14, fill_color="#fee2e2"))
    
    # Моменти вибірки Ведучого (Mode 0, CPHA=0 -> вибірка на наростаннях t_edges[0], t_edges[2], t_edges[4]...)
    for i in range(0, len(t_edges), 2):
        x = t_edges[i]
        # Строб ведучого
        frags.append(line(x, 100, x, 240, color=POS, sw=1.8))
        frags.append(arrow(x, 100, x, 140, color=POS, sw=1.8))
        
    # Позначка першого хибного зчитування
    frags.append(circle(t_edges[0], 160, 16, fill="none", stroke=POS, sw=2.2))
    frags.append(text(t_edges[0], 215, "Хибна вибірка!\n(MISO ще в Hi-Z або перемикається)", size=10, color=POS, bold=True))
    
    # Що зчитує ведучий
    frags.append(text(140, 270, "Зчитано Ведучим\n(Зсув на 1 біт)", size=11, color=POS, bold=True, anchor="end"))
    read_x = [t_edges[0], t_edges[2], t_edges[4], t_edges[6], t_cs_rise]
    frags.append(draw_bus_data(read_x, ["Сміття / 1", "D7 (замість D6)", "D6 (замість D5)", "D5 (замість D4)"], 270, 14, fill_color="#fef2f2"))
    
    # Практичний числовий приклад у рамці
    num_example = (
        "Наслідок у прошивці:\n"
        "• Ведений передає байт 0x95 (10010101b)\n"
        "• Ведучий замість MSB зчитує 1 (стан підтяжки лінії), а D7 зчитує як D6\n"
        "• Отримане значення: 0xCB (11001011b) — суцільне спотворення кадру!\n"
        "• Ознака зсуву CPHA: значення вдвічі більше або вдвічі менше за очікуване."
    )
    frags.append(fitbox(50, 325, 780, 130, num_example, size=11, pad=10, fill="#fff1f2", stroke=POS))
    
    render(os.path.join(OUT, "cpha-mismatch-shift.svg"), w, h, "".join(frags))

# ─────────────────────────────────────────────────────────────────────────────
# 6. first-edge-trap.svg : Пастка першого фронту в режимах CPHA=0 (t_CSS)
# ─────────────────────────────────────────────────────────────────────────────
def make_first_edge_trap():
    w, h = 860, 460
    frags = []
    
    frags.append(text(w / 2, 28, "Пастка першого фронту в CPHA=0: часові обмеження t_CSS та затримка MISO", size=16, bold=True))
    
    t_cs_fall = 140
    t_sclk_first_edge_bad = 170   # Занадто швидкий перший такт SCLK!
    t_sclk_first_edge_good = 260  # Правильний такт із дотриманням t_CSS
    
    # /CS
    frags.append(text(120, 85, "/CS", size=12, color=CS_CLR, bold=True, anchor="end"))
    frags.append(line(130, 75, t_cs_fall, 75, color=CS_CLR, sw=2.2))
    frags.append(line(t_cs_fall, 75, t_cs_fall, 95, color=CS_CLR, sw=2.2))
    frags.append(line(t_cs_fall, 95, 620, 95, color=CS_CLR, sw=2.2))
    
    # MISO вихід веденого: потрібен час t_EN + t_V, щоб з'явився MSB!
    frags.append(text(120, 160, "MISO (Ведений)", size=12, color=DAT, bold=True, anchor="end"))
    frags.append(line(130, 160, t_cs_fall, 160, color=MUTED, sw=1.5, dash="4,4"))
    # Перехідний процес (t_EN)
    t_miso_valid = 210
    frags.append(line(t_cs_fall, 160, t_miso_valid, 160, color=POS, sw=2.5, dash="2,2"))
    frags.append(text((t_cs_fall + t_miso_valid)/2, 145, "t_EN + t_V (вихід з Hi-Z)", size=10, color=POS, bold=True))
    # Стабільні дані після t_miso_valid
    data_x = [t_miso_valid, 340, 480, 620]
    frags.append(draw_bus_data(data_x, ["Bit 7 (MSB) валідний", "Bit 6", "Bit 5"], 160, 14, fill_color="#f0fdf4"))
    
    # Випадок А: Помилка (SCLK занадто рано, порушення t_CSS)
    frags.append(text(120, 240, "SCLK (Помилка:\nt_CSS < t_EN)", size=11, color=POS, bold=True, anchor="end"))
    sclk_bad = [(130, 250), (t_sclk_first_edge_bad, 250), (t_sclk_first_edge_bad, 225), (t_sclk_first_edge_bad + 40, 225), (t_sclk_first_edge_bad + 40, 250), (330, 250)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_bad), POS))
    
    # Строб помилки
    frags.append(arrow(t_sclk_first_edge_bad, 215, t_sclk_first_edge_bad, 178, color=POS, sw=2))
    frags.append(circle(t_sclk_first_edge_bad, 160, 12, fill="none", stroke=POS, sw=2))
    frags.append(text(t_sclk_first_edge_bad, 130, "Строб у зоні Hi-Z!", size=10, color=POS, bold=True))
    
    # Випадок Б: Норма (SCLK після витримки t_CSS >= t_EN + t_SU)
    frags.append(text(120, 320, "SCLK (Норма:\nt_CSS >= t_EN)", size=11, color=FIELD, bold=True, anchor="end"))
    sclk_good = [(130, 330), (t_sclk_first_edge_good, 330), (t_sclk_first_edge_good, 305), (t_sclk_first_edge_good + 40, 305), (t_sclk_first_edge_good + 40, 330), (390, 330)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % p for p in sclk_good), FIELD))
    
    # Строб успіху
    frags.append(arrow(t_sclk_first_edge_good, 295, t_sclk_first_edge_good, 178, color=FIELD, sw=2))
    frags.append(circle(t_sclk_first_edge_good, 160, 12, fill="none", stroke=FIELD, sw=2))
    frags.append(text(t_sclk_first_edge_good, 130, "Стабільний MSB", size=10, color=FIELD, bold=True))
    
    # Інженерна порада
    tip_txt = (
        "Правило проєктування прошивки для CPHA = 0:\n"
        "Між програмним опусканням CS у 0 (GPIO LOW) та стартом апаратної передачі SPI обов'язково\n"
        "потрібна затримка t_CSS (зазвичай 20–100 нс або кілька тактів NOP), щоб ведений встиг активувати буфер MISO."
    )
    frags.append(fitbox(50, 375, 760, 75, tip_txt, size=11, pad=8, fill="#f8fafc", stroke=MUTED))
    
    render(os.path.join(OUT, "first-edge-trap.svg"), w, h, "".join(frags))

if __name__ == "__main__":
    make_modes_matrix()
    make_mode0_mode1_timing()
    make_mode2_mode3_timing()
    make_dual_mode_0_3()
    make_cpha_mismatch_shift()
    make_first_edge_trap()
    print("All figures successfully generated in %s" % OUT)
