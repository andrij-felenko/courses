# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «MEMS-давач тиску».
Генерує SVG у ./img/ за допомогою svgkit з scripts/.
Всі шляхи без номерів, валідні для перевірки 03-figures / svgcheck.py.
"""
import sys, os, math

DIR = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(DIR, "img")
os.makedirs(IMG, exist_ok=True)

sys.path.insert(0, os.path.join(DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *


# ── 1. mems-cavity-bridge: переріз MEMS-кристала над вакуумною камерою ─────────
def fig_mems_cavity_bridge():
    W, H = 840, 420
    parts = []

    cx = W / 2
    top = 50

    # Зовнішній атмосферний тиск P_atm (стрілки зверху)
    for dx in (-160, -80, 0, 80, 160):
        parts.append(arrow(cx + dx, top, cx + dx, top + 42, color=POS, sw=2.2))
    parts.append(text(cx, top - 12, "зовнішній атмосферний тиск P (діє на всю площу)", size=13, bold=True, color=POS))

    # Кремнієва підкладка (Si substrate)
    sub_y = top + 80
    parts.append(rect(cx - 300, sub_y, 140, 180, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    parts.append(rect(cx + 160, sub_y, 140, 180, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    parts.append(mtext(cx - 230, sub_y + 90, "кремнієва\nпідкладка (Si)", size=12, color="#334155", bold=True))
    parts.append(mtext(cx + 230, sub_y + 90, "кремнієва\nпідкладка (Si)", size=12, color="#334155", bold=True))

    # Нижня основа (скляна або кремнієва підкладка для герметизації)
    parts.append(rect(cx - 300, sub_y + 180, 600, 30, fill="#cbd5e1", stroke="#475569", sw=2, rx=2))
    parts.append(text(cx, sub_y + 198, "нижня опорна пластина (герметичне зварювання / Anodic Bonding)", size=11, color="#475569"))

    # Вакуумна порожнина (sealed reference cavity)
    cav_y = sub_y + 20
    parts.append(rect(cx - 160, cav_y, 320, 160, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=0))
    parts.append(mtext(cx, cav_y + 70, "герметична вакуумована порожнина\n(опорний вакуум P_ref ≈ 0 Па)", size=12, color="#64748b", bold=True))

    # Кремнієва мембрана (гнучка плівка Si товщиною ~1.5-5 мкм), прогнута вниз
    mL, mR = cx - 160, cx + 160
    my = sub_y
    # Дуга прогину
    parts.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="5"/>' %
                 (mL, my, cx, my + 30, mR, my, NEG))

    # П'єзорезистори на краях мембрани (максимальне напруження)
    # R1, R2 зліва
    parts.append(rect(mL + 8, my - 2, 34, 12, fill="#f59e0b", stroke="#b45309", sw=1.8, rx=2))
    parts.append(text(mL + 25, my + 6, "R1", size=10, bold=True, color="#78350f"))

    parts.append(rect(mL + 48, my + 4, 34, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.8, rx=2))
    parts.append(text(mL + 65, my + 12, "R2", size=10, bold=True, color="#1e3a8a"))

    # R3, R4 справа
    parts.append(rect(mR - 82, my + 4, 34, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.8, rx=2))
    parts.append(text(mR - 65, my + 12, "R3", size=10, bold=True, color="#1e3a8a"))

    parts.append(rect(mR - 42, my - 2, 34, 12, fill="#f59e0b", stroke="#b45309", sw=1.8, rx=2))
    parts.append(text(mR - 25, my + 6, "R4", size=10, bold=True, color="#78350f"))

    # Виноски на п'єзорезистори
    parts.append(arrow(cx - 240, top + 40, mL + 25, my - 6, color="#b45309", sw=1.5))
    parts.append(text(cx - 240, top + 32, "поздовжній тензорезистор (+ΔR)", size=11, bold=True, color="#b45309", anchor="end"))

    parts.append(arrow(cx + 240, top + 40, mR - 65, my - 2, color="#1d4ed8", sw=1.5))
    parts.append(text(cx + 240, top + 32, "поперечний тензорезистор (-ΔR)", size=11, bold=True, color="#1d4ed8", anchor="start"))

    # Пояснювальний бокс унизу
    box, bw, bh = textbox(W / 2, H - 34,
                          "Перепад ΔP = P - P_ref прогинає мембрану → механічне напруження змінює опір вбудованих п'єзорезисторів",
                          size=12, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render(os.path.join(IMG, "mems-cavity-bridge.svg"), W, H, *parts,
           title="Переріз чутливого MEMS-елемента давача абсолютного тиску")


# ── 2. piezoresistive-bridge-circuit: міст Уїтстона та зчитування напруги ──────
def fig_piezoresistive_bridge_circuit():
    W, H = 840, 400
    parts = []

    cx = W / 2

    # Міст Уїтстона з 4 п'єзорезисторів
    bx, by = 240, 180
    r_len = 65

    # Вузли моста: Top (Vdd), Bottom (GND), Left (V-), Right (V+)
    top_x, top_y = bx, by - r_len
    bot_x, bot_y = bx, by + r_len
    left_x, left_y = bx - r_len, by
    right_x, right_y = bx + r_len, by

    # Лінії моста
    parts.append(line(top_x, top_y, left_x, left_y, color=INK, sw=2))
    parts.append(line(top_x, top_y, right_x, right_y, color=INK, sw=2))
    parts.append(line(left_x, left_y, bot_x, bot_y, color=INK, sw=2))
    parts.append(line(right_x, right_y, bot_x, bot_y, color=INK, sw=2))

    # Резистори моста
    # R1: top-left (+ΔR)
    parts.append(rect((top_x + left_x)/2 - 16, (top_y + left_y)/2 - 10, 32, 20, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=2))
    parts.append(text((top_x + left_x)/2, (top_y + left_y)/2 + 4, "R + ΔR", size=9, bold=True, color="#92400e"))

    # R2: top-right (-ΔR)
    parts.append(rect((top_x + right_x)/2 - 16, (top_y + right_y)/2 - 10, 32, 20, fill="#dbeafe", stroke="#2563eb", sw=1.8, rx=2))
    parts.append(text((top_x + right_x)/2, (top_y + right_y)/2 + 4, "R - ΔR", size=9, bold=True, color="#1e40af"))

    # R3: bot-left (-ΔR)
    parts.append(rect((bot_x + left_x)/2 - 16, (bot_y + left_y)/2 - 10, 32, 20, fill="#dbeafe", stroke="#2563eb", sw=1.8, rx=2))
    parts.append(text((bot_x + left_x)/2, (bot_y + left_y)/2 + 4, "R - ΔR", size=9, bold=True, color="#1e40af"))

    # R4: bot-right (+ΔR)
    parts.append(rect((bot_x + right_x)/2 - 16, (bot_y + right_y)/2 - 10, 32, 20, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=2))
    parts.append(text((bot_x + right_x)/2, (bot_y + right_y)/2 + 4, "R + ΔR", size=9, bold=True, color="#92400e"))

    # Живлення моста
    parts.append(line(top_x, top_y, top_x, top_y - 45, color=POS, sw=2.2))
    parts.append(circle(top_x, top_y - 45, 4, fill=POS, stroke=POS, sw=1))
    parts.append(text(top_x, top_y - 55, "V_bridge (опорне живлення)", size=11, bold=True, color=POS))

    parts.append(line(bot_x, bot_y, bot_x, bot_y + 40, color=MUTED, sw=2.2))
    parts.append(circle(bot_x, bot_y + 40, 4, fill=MUTED, stroke=MUTED, sw=1))
    parts.append(text(bot_x, bot_y + 55, "GND (земля)", size=11, bold=True, color=MUTED))

    # Виходи моста до підсилювача PGA / АЦП
    parts.append(line(right_x, right_y, right_x + 90, right_y - 20, color=NEG, sw=2))
    parts.append(line(left_x, left_y, left_x + 30, left_y + 30, color=NEG, sw=2))
    parts.append(line(left_x + 30, left_y + 30, right_x + 90, right_y + 20, color=NEG, sw=2))

    # Блок PGA + 24-bit Delta-Sigma ADC
    parts.append(rect(right_x + 90, by - 60, 260, 120, fill="#f1f5f9", stroke="#0284c7", sw=2, rx=6))
    parts.append(mtext(right_x + 220, by - 16, "Малошумний PGA\n(підсилювач ×32..×128)", size=12, bold=True, color="#0369a1"))
    parts.append(line(right_x + 100, by + 12, right_x + 340, by + 12, color="#cbd5e1", sw=1.5))
    parts.append(mtext(right_x + 220, by + 34, "24-бітний ΔΣ-АЦП\n(Delta-Sigma ADC)", size=12, bold=True, color="#0f172a"))

    # Вихід цифрового коду
    parts.append(arrow(right_x + 350, by, right_x + 420, by, color=POS, sw=2.4))
    parts.append(mtext(right_x + 430, by, "24-бітний код\nraw_pressure", size=11, bold=True, color=POS, anchor="start"))

    # Формула моста
    parts.append(fitbox(cx - 30, H - 75, 460, 48,
                        "Диференціальна напруга: V_diff = V_bridge · (ΔR / R) ∝ P\nПовний міст подвоює чутливість та компенсує синфазний дрейф",
                        size=11, fill="#f8fafc", stroke="#64748b", sw=1.2, bold=True))

    render(os.path.join(IMG, "piezoresistive-bridge-circuit.svg"), W, H, *parts,
           title="Повний міст Уїтстона з чотирьох інтегрованих п'єзорезисторів")


# ── 3. sensor-architecture-pipeline: повний конвеєр обробки сигналу ────────────
def fig_sensor_architecture_pipeline():
    W, H = 840, 360
    parts = []

    cx = W / 2
    y0 = 120
    bw, bh = 145, 95

    # 1. MEMS Core
    x1 = 40
    parts.append(rect(x1, y0, bw, bh, fill="#fef3c7", stroke="#d97706", sw=2, rx=5))
    parts.append(mtext(x1 + bw/2, y0 + 32, "MEMS-елемент\n+ PTAT-термодавач", size=12, bold=True, color="#92400e"))
    parts.append(text(x1 + bw/2, y0 + 74, "міст ΔR/R (P, T)", size=10, color="#b45309"))

    parts.append(arrow(x1 + bw + 4, y0 + bh/2, x1 + bw + 30, y0 + bh/2, color=INK, sw=1.8))

    # 2. AFE & 24-bit ADC
    x2 = x1 + bw + 34
    parts.append(rect(x2, y0, bw, bh, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=5))
    parts.append(mtext(x2 + bw/2, y0 + 30, "Аналоговий тракт\n+ 24-бітний ΔΣ-АЦП", size=12, bold=True, color="#0369a1"))
    parts.append(text(x2 + bw/2, y0 + 74, "Oversampling 1..64×", size=10, color="#0284c7"))

    parts.append(arrow(x2 + bw + 4, y0 + bh/2, x2 + bw + 30, y0 + bh/2, color=INK, sw=1.8))

    # 3. DSP / Calibration Engine
    x3 = x2 + bw + 34
    parts.append(rect(x3, y0, bw + 20, bh, fill="#dcfce7", stroke="#16a34a", sw=2, rx=5))
    parts.append(mtext(x3 + (bw+20)/2, y0 + 30, "Поліноміальна\nкомпенсація (DSP)", size=12, bold=True, color="#15803d"))
    parts.append(text(x3 + (bw+20)/2, y0 + 74, "NVM коефіцієнти", size=10, color="#166534"))

    # NVM блок зверху DSP
    parts.append(rect(x3 + 15, y0 - 55, bw - 10, 42, fill="#f1f5f9", stroke="#64748b", sw=1.4, rx=3))
    parts.append(mtext(x3 + (bw+20)/2, y0 - 36, "Заводська пам'ять NVM\n(калібрувальні trim-константи)", size=10, bold=True, color="#334155"))
    parts.append(arrow(x3 + (bw+20)/2, y0 - 13, x3 + (bw+20)/2, y0 - 2, color="#64748b", sw=1.5))

    parts.append(arrow(x3 + bw + 24, y0 + bh/2, x3 + bw + 50, y0 + bh/2, color=INK, sw=1.8))

    # 4. Digital Filter & Interface
    x4 = x3 + bw + 54
    parts.append(rect(x4, y0, bw + 30, bh, fill="#fae8ff", stroke="#a855f7", sw=2, rx=5))
    parts.append(mtext(x4 + (bw+30)/2, y0 + 30, "Апаратний IIR-фільтр\n+ FIFO / Інтерфейс", size=12, bold=True, color="#7e22ce"))
    parts.append(text(x4 + (bw+30)/2, y0 + 74, "I2C / SPI вихід", size=10, color="#9333ea"))

    # Стрілка назовні до MCU
    parts.append(arrow(x4 + bw + 34, y0 + bh/2, x4 + bw + 80, y0 + bh/2, color=POS, sw=2.4))
    parts.append(mtext(x4 + bw + 90, y0 + bh/2, "Тиск у Па\nВисота в метрах", size=11, bold=True, color=POS, anchor="start"))

    # Загальний підпис знизу
    parts.append(fitbox(cx, H - 45, 780, 44,
                        "Повний конвеєр: від мікровольтного зміщення п'єзорезистивного моста до каліброваного тиску та висоти",
                        size=11.5, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, bold=True))

    render(os.path.join(IMG, "sensor-architecture-pipeline.svg"), W, H, *parts,
           title="Архітектурний конвеєр обробки сигналу в цифровому MEMS-барометрі")


# ── 4. barometric-altitude-curve: залежність тиску від висоти ──────────────────
def fig_barometric_altitude_curve():
    W, H = 840, 420
    parts = []

    cx = W / 2

    # Вісь координат: ліворуч P (hPa) від 300 до 1050, знизу h (м) від 0 до 9000
    ox, oy = 100, 310
    w_ax, h_ax = 660, 230

    # Сітка та осі
    parts.append(line(ox, oy, ox + w_ax, oy, color="#64748b", sw=1.8))
    parts.append(line(ox, oy, ox, oy - h_ax, color="#64748b", sw=1.8))

    parts.append(text(ox + w_ax + 10, oy + 4, "Висота h (м)", size=12, bold=True, color=INK, anchor="start"))
    parts.append(text(ox - 10, oy - h_ax - 10, "Тиск P (гПа / hPa)", size=12, bold=True, color=INK, anchor="end"))

    # Позначки по висоті: 0, 2000, 4000, 6000, 8000 м
    for h_val in (0, 2000, 4000, 6000, 8000):
        gx = ox + (h_val / 9000.0) * w_ax
        parts.append(line(gx, oy, gx, oy - h_ax, color="#e2e8f0", sw=1, dash="2 2"))
        parts.append(line(gx, oy, gx, oy + 5, color="#64748b", sw=1.5))
        parts.append(text(gx, oy + 18, "%d м" % h_val, size=10, color="#475569"))

    # Позначки по тиску: 300, 500, 700, 900, 1013.25 гПа
    for p_val in (300, 500, 700, 900, 1013):
        gy = oy - ((p_val - 300) / 750.0) * h_ax
        parts.append(line(ox, gy, ox + w_ax, gy, color="#e2e8f0", sw=1, dash="2 2"))
        parts.append(line(ox - 5, gy, ox, gy, color="#64748b", sw=1.5))
        parts.append(text(ox - 10, gy + 4, "%d" % p_val, size=10, color="#475569", anchor="end"))

    # Побудова кривої P(h)
    pts = []
    for step in range(101):
        h_val = (step / 100.0) * 9000.0
        p_val = 1013.25 * ((1.0 - 0.0065 * h_val / 288.15) ** 5.255)
        px = ox + (h_val / 9000.0) * w_ax
        py = oy - ((p_val - 300) / 750.0) * h_ax
        pts.append((px, py))

    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (path_d, NEG))

    # Точка 1: Рівень моря (0 м, 1013.25 гПа)
    p0_x, p0_y = ox, oy - ((1013.25 - 300) / 750.0) * h_ax
    parts.append(circle(p0_x, p0_y, 5, fill=POS, stroke=POS, sw=1.5))
    parts.append(text(p0_x + 14, p0_y + 14, "Рівень моря: 0 м (1013.25 гПа) · Δh/ΔP ≈ 8.3 см / Па", size=10.5, bold=True, color=POS, anchor="start"))

    # Точка 2: Гора Говерла (~2061 м, ~790 гПа)
    h_gov = 2061
    p_gov = 1013.25 * ((1.0 - 0.0065 * h_gov / 288.15) ** 5.255)
    pg_x = ox + (h_gov / 9000.0) * w_ax
    pg_y = oy - ((p_gov - 300) / 750.0) * h_ax
    parts.append(circle(pg_x, pg_y, 4.5, fill="#d97706", stroke="#d97706", sw=1.5))
    parts.append(text(pg_x + 14, pg_y - 12, "Говерла: 2061 м (~790 гПа) · Δh/ΔP ≈ 10.4 см / Па", size=10, color="#92400e", bold=True, anchor="start"))

    # Точка 3: Вершина Евересту (8848 м, ~314 гПа)
    h_ev = 8848
    p_ev = 1013.25 * ((1.0 - 0.0065 * h_ev / 288.15) ** 5.255)
    pe_x = ox + (h_ev / 9000.0) * w_ax
    pe_y = oy - ((p_ev - 300) / 750.0) * h_ax
    parts.append(circle(pe_x, pe_y, 4.5, fill="#7c3aed", stroke="#7c3aed", sw=1.5))
    parts.append(text(pe_x - 14, pe_y - 14, "Еверест: 8848 м (~314 гПа) · Δh/ΔP ≈ 24.5 см / Па", size=10, color="#6d28d9", bold=True, anchor="end"))

    # Пояснення знизу
    parts.append(fitbox(cx, H - 40, 780, 42,
                        "Крива нелінійна: що вище вгору, то розрідженіше повітря, і то більший підйом потрібен на 1 гПа зміни тиску",
                        size=11.5, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, bold=True))

    render(os.path.join(IMG, "barometric-altitude-curve.svg"), W, H, *parts,
           title="Барометрична крива висоти: залежність тиску від висоти над рівнем моря")


# ── 5. iir-filtering-noise-reduction: шум vs IIR фільтрація ────────────────────
def fig_iir_filtering_noise_reduction():
    W, H = 840, 380
    parts = []

    cx = W / 2
    ox, oy = 80, 290
    w_ax, h_ax = 700, 220

    # Осі
    parts.append(line(ox, oy, ox + w_ax, oy, color="#64748b", sw=1.8))
    parts.append(line(ox, oy, ox, oy - h_ax, color="#64748b", sw=1.8))

    parts.append(text(ox + w_ax + 10, oy + 4, "Час t (відліки / вибірки)", size=11.5, bold=True, color=INK, anchor="start"))
    parts.append(text(ox - 10, oy - h_ax - 10, "Розрахована висота h (м)", size=11.5, bold=True, color=INK, anchor="end"))

    # Позначки рівнів висоти: 0.0 м (земля), 1.5 м
    y_ground = oy - 40
    y_step = oy - 160

    parts.append(line(ox, y_ground, ox + w_ax, y_ground, color="#cbd5e1", sw=1.2, dash="3 3"))
    parts.append(text(ox - 10, y_ground + 4, "0.0 м", size=10, color="#475569", anchor="end"))

    parts.append(line(ox, y_step, ox + w_ax, y_step, color="#cbd5e1", sw=1.2, dash="3 3"))
    parts.append(text(ox - 10, y_step + 4, "1.5 м", size=10, color="#475569", anchor="end"))

    # Ідеальна сходинка (підйом на 1.5 м на кроці t = 35)
    step_t = 35
    x_trans = ox + (step_t / 100.0) * w_ax
    parts.append(line(ox, y_ground, x_trans, y_ground, color="#94a3b8", sw=2))
    parts.append(line(x_trans, y_ground, x_trans, y_step, color="#94a3b8", sw=2))
    parts.append(line(x_trans, y_step, ox + w_ax, y_step, color="#94a3b8", sw=2))
    # Напис справа від лінії, anchor="start"
    parts.append(text(x_trans + 16, y_ground - 60, "Справжній підйом на 1.5 м", size=10, italic=True, color="#64748b", anchor="start"))

    # 1. Сирі шумні відліки (raw noisy samples) ±10-15 см розкиду
    raw_pts = []
    for i in range(101):
        x = ox + (i / 100.0) * w_ax
        base_y = y_ground if i < step_t else y_step
        noise = 14.0 * math.sin(i * 1.7) + 8.0 * math.cos(i * 3.4) + 6.0 * math.sin(i * 5.9)
        raw_pts.append((x, base_y + noise))

    # Малюємо сирий шум
    path_raw = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in raw_pts)
    parts.append('<path d="%s" fill="none" stroke="#fca5a5" stroke-width="1.6"/>' % path_raw)

    # 2. IIR-фільтрована крива (alpha = 0.14)
    iir_pts = []
    curr_val = y_ground
    alpha = 0.14
    for i in range(101):
        x = ox + (i / 100.0) * w_ax
        target_raw = raw_pts[i][1]
        curr_val = curr_val + alpha * (target_raw - curr_val)
        iir_pts.append((x, curr_val))

    path_iir = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in iir_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (path_iir, POS))

    # Легенда праворуч зверху
    leg_x, leg_y = cx + 100, 60
    parts.append(rect(leg_x, leg_y, 250, 72, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))

    parts.append(line(leg_x + 15, leg_y + 22, leg_x + 45, leg_y + 22, color="#f87171", sw=2))
    parts.append(text(leg_x + 55, leg_y + 26, "Сирі відліки (шум ±20 см)", size=11, color="#b91c1c", bold=True, anchor="start"))

    parts.append(line(leg_x + 15, leg_y + 48, leg_x + 45, leg_y + 48, color=POS, sw=3.5))
    parts.append(text(leg_x + 55, leg_y + 52, "IIR-фільтр (чистота ±3..5 см)", size=11, color=POS, bold=True, anchor="start"))

    # Пояснення знизу
    parts.append(fitbox(cx, H - 38, 780, 42,
                        "IIR-фільтр усуває високочастотний тепловий та акустичний шум ціною невеликої затримки реакції (фазового зсуву)",
                        size=11.5, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, bold=True))

    render(os.path.join(IMG, "iir-filtering-noise-reduction.svg"), W, H, *parts,
           title="Фільтрація шуму барометра: компроміс між роздільною здатністю та затримкою")


def main():
    fig_mems_cavity_bridge()
    fig_piezoresistive_bridge_circuit()
    fig_sensor_architecture_pipeline()
    fig_barometric_altitude_curve()
    fig_iir_filtering_noise_reduction()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
