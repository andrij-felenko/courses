# -*- coding: utf-8 -*-
"""Фігури до теми «PDM і децимація (CIC-фільтри)».
Запуск:  python figs.py   → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pdm_bitstream():
    """1. PDM бітовий потік: аналогова хвиля, імпульси та спектр із формуванням шуму."""
    w, h = 800, 360
    dw, dh = 800, 360
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    # Заголовок лівої панелі
    out.append(text(200, 24, "Часова область: PDM-імпульси", size=13, color=INK, bold=True))
    
    # Аналоговий сигнал і бітовий потік
    ax_y1 = 90
    out.append(line(40, ax_y1, 370, ax_y1, color=MUTED, sw=1, dash="3,3"))
    out.append(text(35, ax_y1 + 4, "0", size=10, color=MUTED, anchor="end"))
    
    # Синусоїда
    pts = []
    for i in range(320):
        x = 50 + i
        y = ax_y1 - 40 * math.sin(2 * math.pi * i / 160)
        pts.append("%.1f,%.1f" % (x, y))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), FIELD))
    out.append(text(375, ax_y1 - 25, "Аналоговий сигнал", size=11, color=FIELD, anchor="start", bold=True))

    # PDM потік унизу
    ax_y2 = 180
    out.append(line(40, ax_y2, 370, ax_y2, color=LINE, sw=1.5))
    out.append(text(35, ax_y2 + 4, "PDM", size=11, color=INK, anchor="end", bold=True))
    
    # Генеруємо показові 1-бітні імпульси PDM
    pdm_bits = [
        # Крок 0..80 (позитивна півхвиля: багато 1)
        0,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,0,1,0,1,0,
        # Крок 80..160 (негативна півхвиля: багато 0)
        0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,0,1,1,0,1,0,
        # Крок 160..240 (позитивна півхвиля)
        1,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,0,1,0,1,0,0,1,0,0,0,0,1,0,0
    ]
    pulse_w = 4.2
    for idx, bit in enumerate(pdm_bits[:70]):
        px = 50 + idx * pulse_w
        if bit == 1:
            out.append(rect(px, ax_y2 - 32, pulse_w - 0.8, 32, fill=POS, stroke=POS, sw=0.5, rx=1))
        else:
            out.append(line(px, ax_y2, px + pulse_w - 0.8, ax_y2, color=MUTED, sw=1.5))

    out.append(text(120, 215, "Висока густина '1'", size=10, color=POS, bold=True))
    out.append(text(270, 215, "Низька густина '1'", size=10, color=NEG, bold=True))
    out.append(text(210, 240, "Частота тактування: f_clk = 1.024 ... 3.072 МГц (1 біт)", size=11, color=INK))

    # Розділювач панелей
    out.append(line(410, 20, 410, 340, color=MUTED, sw=1, dash="4,4"))

    # Права панель: Частотна область і формування шуму (Noise Shaping)
    out.append(text(600, 24, "Частотна область: формування шуму", size=13, color=INK, bold=True))
    
    # Осі спектра
    sp_x0, sp_x1 = 450, 750
    sp_y0 = 240
    out.append(line(sp_x0, sp_y0, sp_x1, sp_y0, color=LINE, sw=1.5))
    out.append(line(sp_x0, sp_y0, sp_x0, 60, color=LINE, sw=1.5))
    out.append(text(sp_x1 - 10, sp_y0 + 20, "Частота f", size=11, color=INK, italic=True))
    out.append(text(sp_x0 - 8, 70, "дБ", size=11, color=INK, italic=True))

    # Смуга аудіо
    out.append(rect(sp_x0, 75, 45, sp_y0 - 75, fill="#e8f8f0", stroke="none", rx=0))
    out.append(text(sp_x0 + 22, sp_y0 + 16, "20 кГц", size=10, color=FIELD, bold=True))
    out.append(text(sp_x0 + 22, 110, "Звук", size=11, color=FIELD, bold=True, italic=True))

    # Спектр корисного тону
    out.append(line(sp_x0 + 15, sp_y0, sp_x0 + 15, 90, color=FIELD, sw=2.5))

    # Крива шуму квантування з noise shaping
    noise_pts = []
    for i in range(100):
        t = i / 99.0
        nx = sp_x0 + t * (sp_x1 - sp_x0 - 15)
        ny = sp_y0 - 8 - 150 * (t ** 2.2)
        noise_pts.append("%.1f,%.1f" % (nx, ny))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(noise_pts), POS))
    out.append(text(660, 120, "Шум квантування", size=11, color=POS, bold=True))
    out.append(text(660, 136, "(виштовхнутий у МГц)", size=10, color=POS))

    # Підписи частот
    out.append(line(sp_x1 - 20, sp_y0 - 3, sp_x1 - 20, sp_y0 + 3, color=LINE, sw=1.5))
    out.append(text(sp_x1 - 20, sp_y0 + 16, "f_s / 2", size=10, color=MUTED))

    # Пояснення внизу
    tb, _, _ = textbox(600, 305, "Сигма-дельта модулятор виштовхує весь шум у МГц.\nЗавдання дециматора — зрізати його без множників.", size=11, pad=8, fill=FILL, stroke=MUTED)
    out.append(tb)

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "pdm-bitstream.svg"), "w", encoding="utf-8") as f:
        f.write(full)


def fig_boxcar_to_hogenauer():
    """2. Перетворення каскаду ковзних середніх на структуру Хогенауера."""
    w, h = 820, 390
    dw, dh = 820, 390
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    # Секція А: Каскад ковзних середніх
    out.append(text(30, 30, "А. Пряма реалізація: каскад прямокутних вікон (Boxcar)", size=13, color=INK, anchor="start", bold=True))
    
    # Блоки верхньої схеми
    out.append(text(40, 75, "x[n]", size=12, color=INK, bold=True))
    out.append(text(40, 92, "на f_s", size=10, color=MUTED))
    out.append(arrow(60, 75, 100, 75))

    tb1, _, _ = textbox(165, 75, "Ковзне середнє\nдовжини D = R·M", size=11, pad=8, fill=FILL, stroke=LINE)
    out.append(tb1)
    out.append(arrow(230, 75, 270, 75))

    tb2, _, _ = textbox(335, 75, "Ковзне середнє\nдовжини D = R·M", size=11, pad=8, fill=FILL, stroke=LINE)
    out.append(tb2)
    out.append(arrow(400, 75, 440, 75))

    out.append(text(460, 75, "...", size=16, color=INK, bold=True))
    out.append(arrow(480, 75, 520, 75))

    tb_dec1, _, _ = textbox(560, 75, "↓ R", size=14, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    out.append(tb_dec1)
    out.append(arrow(595, 75, 660, 75))

    out.append(text(710, 75, "y[k]", size=12, color=INK, bold=True))
    out.append(text(710, 92, "на f_s / R", size=10, color=MUTED))

    out.append(text(410, 130, "Потребує D комірок пам'яті на кожен каскад і працює на максимальній частоті f_s", size=11, color=POS, italic=True))

    out.append(line(40, 155, 780, 155, color=MUTED, sw=1, dash="4,4"))
    out.append(text(410, 175, "Тотожність благородства: перенесення диференціатора за дециматор ↓R", size=12, color=FIELD, bold=True))

    # Секція Б: Структура Хогенауера
    out.append(text(30, 205, "Б. Структура Хогенауера (CIC): інтегратори → проріджувач → гребінки", size=13, color=INK, anchor="start", bold=True))

    out.append(text(40, 260, "x[n]", size=12, color=INK, bold=True))
    out.append(text(40, 277, "на f_s", size=10, color=MUTED))
    out.append(arrow(60, 260, 95, 260))

    tb_int1, _, _ = textbox(145, 260, "Інтегратор 1\n1 / (1 − z⁻¹)", size=11, pad=8, fill="#fee2e2", stroke=POS)
    out.append(tb_int1)
    out.append(arrow(195, 260, 225, 260))

    tb_int2, _, _ = textbox(275, 260, "Інтегратор N\n1 / (1 − z⁻¹)", size=11, pad=8, fill="#fee2e2", stroke=POS)
    out.append(tb_int2)
    out.append(arrow(325, 260, 365, 260))

    tb_dec2, _, _ = textbox(405, 260, "↓ R", size=14, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    out.append(tb_dec2)
    out.append(arrow(445, 260, 485, 260))

    tb_cmb1, _, _ = textbox(535, 260, "Гребінка 1\n1 − z⁻ᴹ", size=11, pad=8, fill="#dbeafe", stroke=NEG)
    out.append(tb_cmb1)
    out.append(arrow(585, 260, 615, 260))

    tb_cmb2, _, _ = textbox(665, 260, "Гребінка N\n1 − z⁻ᴹ", size=11, pad=8, fill="#dbeafe", stroke=NEG)
    out.append(tb_cmb2)
    out.append(arrow(715, 260, 750, 260))

    out.append(text(780, 260, "y[k]", size=12, color=INK, bold=True))
    out.append(text(780, 277, "на f_s / R", size=10, color=MUTED))

    out.append(rect(90, 305, 240, 65, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    out.append(text(210, 328, "N інтеграторів", size=12, color=POS, bold=True))
    out.append(text(210, 350, "Частота f_s (додавання)", size=11, color=INK))

    out.append(rect(480, 305, 240, 65, fill="#dbeafe", stroke=NEG, sw=1, rx=4))
    out.append(text(600, 328, "N гребінок (диференціаторів)", size=12, color=NEG, bold=True))
    out.append(text(600, 350, "Частота f_s / R (віднімання)", size=11, color=INK))

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "boxcar-to-hogenauer.svg"), "w", encoding="utf-8") as f:
        f.write(full)


def fig_hogenauer_structure():
    """3. Детальна схема апаратного конвеєра дециматора Хогенауера з регістрами."""
    w, h = 820, 320
    dw, dh = 820, 320
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    out.append(text(410, 24, "Конвеєр дециматора Хогенауера: розрядна сітка та синхронізація", size=13, color=INK, bold=True))

    out.append(rect(40, 50, 310, 200, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    out.append(text(195, 75, "Каскад інтегратора (тактування f_clk = f_s)", size=11, color=POS, bold=True))

    out.append(text(55, 140, "Вхід", size=10, color=MUTED))
    out.append(arrow(65, 150, 115, 150))
    out.append(circle(125, 150, 10, fill=FILL, stroke=LINE, sw=1.5))
    out.append(text(125, 154, "+", size=14, color=POS, bold=True))

    out.append(arrow(135, 150, 205, 150))
    tb_z1, _, _ = textbox(235, 150, "Регістр z⁻¹\n(B_max біт)", size=10, pad=6, fill=FILL, stroke=LINE)
    out.append(tb_z1)

    out.append(line(275, 150, 305, 150))
    out.append(line(305, 150, 305, 210))
    out.append(line(305, 210, 125, 210))
    out.append(arrow(125, 210, 125, 160))
    out.append(text(215, 225, "Накопичення y[n] = y[n-1] + x[n]", size=10, color=MUTED, italic=True))

    out.append(arrow(305, 150, 375, 150))

    out.append(rect(375, 115, 70, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    out.append(text(410, 145, "↓ R", size=16, color="#b45309", bold=True))
    out.append(text(410, 165, "1 з R тактів", size=9, color=MUTED))

    out.append(arrow(445, 150, 505, 150))

    out.append(rect(470, 50, 310, 200, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    out.append(text(625, 75, "Каскад гребінки (тактування f_out = f_s / R)", size=11, color=NEG, bold=True))

    out.append(circle(515, 150, 3, fill=LINE, stroke=LINE, sw=0))
    out.append(arrow(515, 150, 565, 150))
    tb_zm, _, _ = textbox(605, 150, "Затримка z⁻ᴹ\n(M = 1 або 2)", size=10, pad=6, fill=FILL, stroke=LINE)
    out.append(tb_zm)

    out.append(line(515, 150, 515, 205))
    out.append(line(515, 205, 695, 205))
    out.append(arrow(695, 205, 695, 160))

    out.append(arrow(645, 150, 685, 150))
    out.append(circle(695, 150, 10, fill=FILL, stroke=LINE, sw=1.5))
    out.append(text(695, 154, "−", size=14, color=NEG, bold=True))

    out.append(arrow(705, 150, 760, 150))
    out.append(text(765, 154, "Вихід", size=10, color=MUTED, anchor="start"))
    out.append(text(605, 225, "Різниця w[k] = v[k] − v[k-M]", size=10, color=MUTED, italic=True))

    tb_bit, _, _ = textbox(410, 285, "Усі суматори та регістри працюють у розрядності B_max = B_in + N · log₂(R · M)\nАрифметика в доповняльному коді гарантує точність попри переповнення інтеграторів", size=11, pad=8, fill=FILL, stroke=MUTED)
    out.append(tb_bit)

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "hogenauer-structure.svg"), "w", encoding="utf-8") as f:
        f.write(full)


def fig_modulo_arithmetic():
    """4. Арифметика за модулем 2^B на числовому колі: усунення похибки переповнення."""
    w, h = 800, 360
    dw, dh = 800, 360
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    out.append(text(400, 24, "Числове коло 2's Complement: чому переповнення інтегратора не спотворює результат", size=13, color=INK, bold=True))

    cx, cy, r = 220, 180, 100
    out.append(circle(cx, cy, r, fill="#fdfdfd", stroke=LINE, sw=2))

    out.append(text(cx, cy - r - 12, "0", size=12, color=INK, bold=True))
    out.append(text(cx + r + 24, cy + 4, "+(2^(B-1) - 1)", size=10, color=POS, bold=True))
    out.append(text(cx, cy + r + 18, "Мітка переповнення (rollover)", size=10, color=MUTED))
    out.append(text(cx - r - 28, cy + 4, "-(2^(B-1))", size=10, color=NEG, bold=True))

    ang1 = math.radians(40)
    p1_x = cx + r * math.sin(ang1)
    p1_y = cy - r * math.cos(ang1)
    out.append(circle(p1_x, p1_y, 5, fill=NEG, stroke=LINE, sw=1))
    out.append(text(p1_x + 12, p1_y - 8, "s[k-1]", size=11, color=NEG, bold=True))

    ang2 = math.radians(110)
    p2_x = cx + r * math.sin(ang2)
    p2_y = cy - r * math.cos(ang2)
    out.append(circle(p2_x, p2_y, 5, fill=POS, stroke=LINE, sw=1))
    out.append(text(p2_x + 14, p2_y + 12, "s[k]", size=11, color=POS, bold=True))

    out.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="4" stroke-dasharray="2,2"/>'
               % (p1_x, p1_y, r, r, p2_x, p2_y, FIELD))
    out.append(text(cx + 45, cy - 20, "Справжня різниця Δs", size=10, color=FIELD, bold=True))

    tx0 = 440
    out.append(rect(tx0 - 15, 60, 350, 260, fill=FILL, stroke=MUTED, sw=1, rx=6))
    out.append(text(tx0 + 160, 85, "Теорема про модульну різницю", size=12, color=INK, bold=True))

    lines = [
        "1. Інтегратор неперервно накопичує суму:",
        "   y[n] невпинно зростає і робить повні оберти",
        "   довкола кільця 2^B (переповнюється).",
        "",
        "2. Гребінка обчислює різницю відліків:",
        "   Δ = (s[k] − s[k−1]) mod 2^B",
        "",
        "3. Доки повний динамічний діапазон сигналу",
        "   на виході фільтра вміщується в 2^B,",
        "   віднімання точно повертає довжину дуги Δs,",
        "   незалежно від кількості повних обертів!"
    ]
    for idx, ln in enumerate(lines):
        bold = ("1." in ln or "2." in ln or "3." in ln)
        color = POS if "1." in ln else (NEG if "2." in ln else (FIELD if "3." in ln else INK))
        out.append(text(tx0, 115 + idx * 17, ln, size=10.5, color=color, anchor="start", bold=bold))

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "modulo-arithmetic.svg"), "w", encoding="utf-8") as f:
        f.write(full)


def fig_cic_frequency_droop():
    """5. Амплітудно-частотна характеристика: спад у смузі (Passband Droop) та компенсуючий КІХ."""
    w, h = 820, 360
    dw, dh = 820, 360
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    out.append(text(410, 24, "АЧХ CIC-фільтра: спад у смузі пропускання (Passband Droop) та його компенсація", size=13, color=INK, bold=True))

    g1_x0, g1_x1 = 50, 370
    g1_y0 = 260
    out.append(text(210, 52, "АЧХ CIC у широкій смузі (sincᴺ)", size=11, color=INK, bold=True))
    out.append(line(g1_x0, g1_y0, g1_x1, g1_y0, color=LINE, sw=1.5))
    out.append(line(g1_x0, g1_y0, g1_x0, 75, color=LINE, sw=1.5))
    out.append(text(g1_x1 - 10, g1_y0 + 18, "f / f_out", size=10, color=INK, italic=True))
    out.append(text(g1_x0 - 8, 85, "дБ", size=10, color=INK, italic=True))

    pts_sinc = []
    for i in range(1, 300):
        t = i / 100.0
        val = math.sin(math.pi * t) / (math.pi * t)
        mag = (abs(val)) ** 3
        db = 20 * math.log10(max(mag, 1e-4))
        gy = 90 - (db / 80.0) * 160
        gy = min(max(gy, 90), g1_y0)
        gx = g1_x0 + (t / 3.0) * (g1_x1 - g1_x0)
        pts_sinc.append("%.1f,%.1f" % (gx, gy))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_sinc), POS))

    for k in [1, 2]:
        zx = g1_x0 + (k / 3.0) * (g1_x1 - g1_x0)
        out.append(line(zx, g1_y0 - 3, zx, g1_y0 + 3, color=LINE, sw=1.5))
        out.append(text(zx, g1_y0 + 16, "%d·f_out" % k, size=9, color=MUTED))
        out.append(text(zx, 230, "Нуль", size=9, color=POS, italic=True))

    g2_x0, g2_x1 = 440, 770
    g2_y0 = 260
    out.append(text(605, 52, "Компенсація спаду в звуковій смузі [0 .. 20 кГц]", size=11, color=INK, bold=True))
    out.append(line(g2_x0, g2_y0, g2_x1, g2_y0, color=LINE, sw=1.5))
    out.append(line(g2_x0, g2_y0, g2_x0, 75, color=LINE, sw=1.5))
    out.append(text(g2_x1 - 10, g2_y0 + 18, "Частота", size=10, color=INK, italic=True))
    out.append(text(g2_x0 - 8, 85, "дБ", size=10, color=INK, italic=True))

    out.append(line(g2_x0, 120, g2_x1, 120, color=MUTED, sw=1, dash="3,3"))
    out.append(text(g2_x0 - 6, 124, "0 дБ", size=9, color=MUTED, anchor="end"))

    pts_droop = []
    pts_comp = []
    pts_flat = []

    for i in range(100):
        t = i / 100.0
        f_norm = t * 0.45
        val = math.sin(math.pi * f_norm) / (math.pi * max(f_norm, 1e-5)) if f_norm > 0 else 1.0
        mag = val ** 4
        db_droop = 20 * math.log10(max(mag, 1e-4))
        
        gx = g2_x0 + t * (g2_x1 - g2_x0 - 20)
        y_droop = 120 - db_droop * 25
        y_comp = 120 + db_droop * 25
        y_flat = 120 + 1.2 * math.sin(t * 12)

        pts_droop.append("%.1f,%.1f" % (gx, y_droop))
        pts_comp.append("%.1f,%.1f" % (gx, y_comp))
        pts_flat.append("%.1f,%.1f" % (gx, y_flat))

    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (" ".join(pts_droop), POS))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (" ".join(pts_comp), NEG))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_flat), FIELD))

    out.append(text(660, 185, "— · Спад CIC (Passband Droop)", size=10, color=POS, bold=True))
    out.append(text(660, 95, "— · Компенсуючий КІХ (1 / sinc)", size=10, color=NEG, bold=True))
    out.append(text(660, 140, "— Сумарна пласка АЧХ", size=10.5, color=FIELD, bold=True))

    tb_bot, _, _ = textbox(410, 315, "Двоступенева децимація: CIC (збиває МГц) + 2-й ступінь КІХ (вирівнює спад і дає крутий зріз)", size=11, pad=8, fill=FILL, stroke=MUTED)
    out.append(tb_bot)

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "cic-frequency-droop.svg"), "w", encoding="utf-8") as f:
        f.write(full)


def fig_pdm_audio_pipeline():
    """6. Повний конвеєр мікрофонного тракту PDM -> PCM."""
    w, h = 820, 240
    dw, dh = 820, 240
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke=LINE, sw=1))

    out.append(text(410, 24, "Повний цифровий тракт PDM-мікрофона: 2-ступенева децимація та нормалізація", size=13, color=INK, bold=True))

    tb1, _, _ = textbox(90, 95, "MEMS-мікрофон\nPDM потік 1 біт\n3.072 МГц", size=10.5, pad=8, fill="#fee2e2", stroke=POS, bold=True)
    out.append(tb1)
    out.append(arrow(155, 95, 195, 95))

    tb2, _, _ = textbox(275, 95, "Ступінь 1: CIC (N=4, R=32)\nБез множень, 21-біт цілі\nВихід: 96 кГц", size=10.5, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    out.append(tb2)
    out.append(arrow(355, 95, 395, 95))

    tb3, _, _ = textbox(485, 95, "Ступінь 2: Half-Band FIR (↓2)\nКомпенсація спаду sinc⁴\nВихід: 48 кГц (24 біти)", size=10.5, pad=8, fill="#dbeafe", stroke=NEG, bold=True)
    out.append(tb3)
    out.append(arrow(575, 95, 615, 95))

    tb4, _, _ = textbox(705, 95, "DC-блокер (ФВЧ)\nЗріз ~10 Гц\nГотовий PCM 16/24 біт", size=10.5, pad=8, fill="#e8f8f0", stroke=FIELD, bold=True)
    out.append(tb4)

    out.append(rect(40, 160, 740, 55, fill=FILL, stroke=MUTED, sw=1, rx=4))
    out.append(text(100, 182, "Апаратний I2S/SPI DMA", size=10, color=POS, bold=True))
    out.append(text(100, 198, "Захоплення бітів", size=9.5, color=MUTED))

    out.append(text(285, 182, "Цілочисельне ядро", size=10, color="#d97706", bold=True))
    out.append(text(285, 198, "Швидкий спуск МГц → кГц", size=9.5, color=MUTED))

    out.append(text(485, 182, "Аудіоядро DSP", size=10, color=NEG, bold=True))
    out.append(text(485, 198, "Пласка смуга 20 Гц .. 20 кГц", size=9.5, color=MUTED))

    out.append(text(700, 182, "Вихідний звук", size=10, color=FIELD, bold=True))
    out.append(text(700, 198, "Аудіобуфер / WAV / Кодек", size=9.5, color=MUTED))

    raw = "".join(out)
    full = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n%s\n</svg>'
            % (dw, dh, dw, dh, LINE, raw))
    with open(os.path.join(IMG, "pdm-audio-pipeline.svg"), "w", encoding="utf-8") as f:
        f.write(full)


if __name__ == "__main__":
    fig_pdm_bitstream()
    fig_boxcar_to_hogenauer()
    fig_hogenauer_structure()
    fig_modulo_arithmetic()
    fig_cic_frequency_droop()
    fig_pdm_audio_pipeline()
    print("Всі 6 фігур успішно згенеровано у ./img/")
