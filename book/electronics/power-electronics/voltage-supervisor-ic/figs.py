# -*- coding: utf-8 -*-
"""Фігури до статті «Супервізор напруги (клас ІС)»
   (book/electronics/power-electronics/voltage-supervisor-ic):
  - supervisor-architecture.svg   — внутрішня функціональна схема супервізора напруги
  - por-timing-diagram.svg        — часова діаграма пуску, затримки t_rst та аварійного скидання
  - mcu-blind-zone.svg            — сліпа зона внутрішнього BOD мікроконтролера vs зовнішній супервізор
  - wired-or-reset.svg            — схема монтажного «АБО» (wired-OR) на відкритому стоці
  - power-sequencing-diagram.svg  — часова діаграма секвенування 3 шин живлення (Core, DDR, I/O)
  - window-watchdog-timing.svg    — часові вікна віконного сторожового таймера (WWDT)
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── фіг. 1. Внутрішня архітектура супервізора напруги ──────────────────────────
def fig_supervisor_architecture():
    W, H = 840, 520
    f = [text(W / 2, 28, "Внутрішня функціональна архітектура прецизійного супервізора напруги",
              size=15.5, bold=True)]

    # Головний корпус ІС (пунктирний контур кристала)
    chip_x, chip_y, chip_w, chip_h = 100, 60, 640, 420
    f.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#fafbfc", stroke="#4b5563", sw=1.8, rx=8))
    f.append(text(chip_x + 16, chip_y + 24, "Кристал супервізора напруги (Supervisor IC)",
                  size=12, color="#4b5563", bold=True, anchor="start"))

    # Вивід VDD (живлення та моніторинг)
    f.append(line(30, 110, chip_x, 110, color=POS, sw=2.5))
    f.append(circle(chip_x, 110, 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(25, 114, "VDD / SENSE", size=11, bold=True, color=POS, anchor="end"))

    # Дільник напруги (лазерно підігнаний R1/R2)
    div_x = 180
    f.append(line(chip_x, 110, div_x, 110, color=POS, sw=2))
    f.append(line(div_x, 110, div_x, 135, color=INK, sw=1.8))
    f.append(rect(div_x - 18, 135, 36, 40, fill=BG, stroke=INK, sw=1.5, rx=0))
    f.append(text(div_x, 159, "R1", size=11, bold=True))
    node_v = 205
    f.append(line(div_x, 175, div_x, node_v, color=INK, sw=1.8))
    f.append(circle(div_x, node_v, 3, fill=INK, stroke=INK, sw=1))
    f.append(line(div_x, node_v, div_x, 235, color=INK, sw=1.8))
    f.append(rect(div_x - 18, 235, 36, 40, fill=BG, stroke=INK, sw=1.5, rx=0))
    f.append(text(div_x, 259, "R2", size=11, bold=True))
    f.append(line(div_x, 275, div_x, 305, color=INK, sw=1.8))
    # GND шина всередині
    f.append(line(div_x - 20, 305, div_x + 20, 305, color=INK, sw=1.8))
    f.append(line(div_x - 12, 311, div_x + 12, 311, color=INK, sw=1.8))
    f.append(line(div_x - 5, 317, div_x + 5, 317, color=INK, sw=1.8))
    f.append(text(div_x, 332, "GND", size=10, bold=True))

    # Вивід GND назовні
    f.append(line(div_x, 317, div_x, chip_y + chip_h, color=INK, sw=2))
    f.append(line(div_x, chip_y + chip_h, div_x, 500, color=INK, sw=2))
    f.append(text(div_x, 514, "GND", size=11, bold=True))

    # Джерело опорної напруги (Bandgap 1.2V)
    bg_x, bg_y = 290, 260
    f.append(rect(bg_x - 55, bg_y - 25, 110, 50, fill="#f0ecff", stroke="#6b46c1", sw=1.6, rx=5))
    f.append(text(bg_x, bg_y - 6, "Bandgap опора", size=11, bold=True, color="#6b46c1"))
    f.append(text(bg_x, bg_y + 12, "Vref = 1.20 В (±0.5%)", size=10, color="#6b46c1"))

    # Компаратор із гістерезисом
    comp_x, comp_y = 410, 205
    f.append('<path d="M %d,%d L %d,%d L %d,%d Z" fill="#eef2f7" stroke="%s" stroke-width="1.8"/>' %
             (comp_x - 35, comp_y - 45, comp_x - 35, comp_y + 45, comp_x + 35, comp_y, INK))
    f.append(text(comp_x - 12, comp_y - 6, "Компаратор", size=10, bold=True))
    f.append(text(comp_x - 12, comp_y + 10, "+ гістерезис", size=9.5, color=MUTED))

    # Входи компаратора
    f.append(line(div_x, node_v, comp_x - 35, node_v - 18, color=INK, sw=1.6))
    f.append(text(comp_x - 26, node_v - 14, "−", size=13, bold=True, color=NEG))
    f.append(line(bg_x + 55, bg_y, comp_x - 48, bg_y, color=INK, sw=1.6))
    f.append(line(comp_x - 48, bg_y, comp_x - 48, node_v + 18, color=INK, sw=1.6))
    f.append(line(comp_x - 48, node_v + 18, comp_x - 35, node_v + 18, color=INK, sw=1.6))
    f.append(text(comp_x - 26, node_v + 22, "+", size=13, bold=True, color=POS))

    # Фільтр викидів (Glitch Filter)
    gf_x, gf_y = 490, 205
    f.append(line(comp_x + 35, comp_y, gf_x - 30, gf_y, color=INK, sw=1.6))
    f.append(rect(gf_x - 30, gf_y - 22, 60, 44, fill="#fff6e6", stroke="#b5732e", sw=1.5, rx=4))
    f.append(text(gf_x, gf_y - 4, "Фільтр", size=10.5, bold=True, color="#b5732e"))
    f.append(text(gf_x, gf_y + 11, "викидів", size=9.5, color="#b5732e"))

    # Таймер затримки скидання (POR Delay Timer t_rst)
    tm_x, tm_y = 590, 205
    f.append(line(gf_x + 30, gf_y, tm_x - 40, tm_y, color=INK, sw=1.6))
    f.append(rect(tm_x - 40, tm_y - 30, 80, 60, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=5))
    f.append(text(tm_x, tm_y - 12, "Таймер POR", size=11, bold=True, color=FIELD))
    f.append(text(tm_x, tm_y + 4, "затримка t_rst", size=10, color=FIELD))
    f.append(text(tm_x, tm_y + 19, "50–200 мс", size=9.5, color=MUTED))

    # Вивід програмування конденсатора C_T
    f.append(line(tm_x, tm_y + 30, tm_x, chip_y + chip_h, color=FIELD, sw=1.6))
    f.append(line(tm_x, chip_y + chip_h, tm_x, 495, color=FIELD, sw=1.6))
    f.append(circle(tm_x, 495, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(tm_x + 8, 498, "CT (зовнішній C)", size=10, bold=True, color=FIELD, anchor="start"))

    # Вихідний каскад: NMOS Open-Drain
    nmos_x, nmos_y = 690, 205
    f.append(line(tm_x + 40, tm_y, nmos_x - 15, nmos_y, color=INK, sw=1.6))
    f.append(rect(nmos_x - 15, nmos_y - 15, 20, 30, fill=BG, stroke=INK, sw=1.4, rx=2))
    f.append(text(nmos_x - 5, nmos_y + 4, "Inv", size=9, bold=True))
    f.append(line(nmos_x + 5, nmos_y, nmos_x + 20, nmos_y, color=INK, sw=1.6))
    f.append(line(nmos_x + 20, nmos_y - 20, nmos_x + 20, nmos_y + 20, color=INK, sw=2))
    f.append(line(nmos_x + 26, nmos_y - 25, nmos_x + 26, nmos_y - 8, color=INK, sw=2))
    f.append(line(nmos_x + 26, nmos_y - 5, nmos_x + 26, nmos_y + 5, color=INK, sw=2))
    f.append(line(nmos_x + 26, nmos_y + 8, nmos_x + 26, nmos_y + 25, color=INK, sw=2))
    f.append(line(nmos_x + 26, nmos_y - 16, nmos_x + 40, nmos_y - 16, color=INK, sw=1.6))
    f.append(line(nmos_x + 40, nmos_y - 16, nmos_x + 40, nmos_y, color=INK, sw=1.6))
    f.append(line(nmos_x + 40, nmos_y, chip_x + chip_w, nmos_y, color=INK, sw=2))
    f.append(line(chip_x + chip_w, nmos_y, 800, nmos_y, color=INK, sw=2.5))
    f.append(circle(chip_x + chip_w, nmos_y, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(text(805, nmos_y - 8, "/RESET (nRESET)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(805, nmos_y + 8, "Open-Drain вихід", size=9.5, color=MUTED, anchor="start"))
    f.append(line(nmos_x + 26, nmos_y + 16, nmos_x + 40, nmos_y + 16, color=INK, sw=1.6))
    f.append(line(nmos_x + 40, nmos_y + 16, nmos_x + 40, 270, color=INK, sw=1.6))
    f.append(line(nmos_x + 40, 270, div_x, 270, color=INK, sw=1.4, dash="3,3"))

    # Вхід ручного скидання (Manual Reset /MR)
    mr_y = 390
    f.append(line(30, mr_y, chip_x, mr_y, color=NEG, sw=2))
    f.append(circle(chip_x, mr_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(25, mr_y + 4, "/MR", size=11, bold=True, color=NEG, anchor="end"))
    f.append(line(chip_x, mr_y, 340, mr_y, color=NEG, sw=1.6))
    f.append(rect(340, mr_y - 20, 110, 40, fill="#edf2f7", stroke="#4a5568", sw=1.5, rx=4))
    f.append(text(395, mr_y - 4, "Антибрязкіт /MR", size=10, bold=True))
    f.append(text(395, mr_y + 11, "підтяжка до VDD", size=9, color=MUTED))
    f.append(line(450, mr_y, tm_x, mr_y, color=NEG, sw=1.6))
    f.append(line(tm_x, mr_y, tm_x, tm_y + 30, color=NEG, sw=1.6))

    # Віконний сторожовий таймер (Windowed Watchdog)
    wdt_y = 390
    f.append(line(800, wdt_y, chip_x + chip_w, wdt_y, color="#d97706", sw=2))
    f.append(circle(chip_x + chip_w, wdt_y, 3.5, fill="#d97706", stroke="#d97706", sw=1))
    f.append(text(805, wdt_y + 4, "WDI (Watchdog In)", size=10.5, bold=True, color="#d97706", anchor="start"))
    f.append(rect(580, wdt_y - 22, 100, 44, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=4))
    f.append(text(630, wdt_y - 6, "Віконний WDT", size=10.5, bold=True, color="#d97706"))
    f.append(text(630, wdt_y + 10, "таймаут + вікно", size=9.5, color="#d97706"))
    f.append(line(chip_x + chip_w, wdt_y, 680, wdt_y, color="#d97706", sw=1.6))
    f.append(line(580, wdt_y, 520, wdt_y, color="#d97706", sw=1.6))
    f.append(line(520, wdt_y, 520, tm_y + 15, color="#d97706", sw=1.6))
    f.append(line(520, tm_y + 15, tm_x - 40, tm_y + 15, color="#d97706", sw=1.6))

    render(os.path.join(IMG, "supervisor-architecture.svg"), W, H, *f)


# ── фіг. 2. Часова діаграма пуску, затримки t_rst та аварійного скидання ──────
def fig_por_timing_diagram():
    W, H = 840, 460
    f = [text(W / 2, 28, "Хронограма роботи супервізора: пуск із затримкою t_rst та реакція на просідання",
              size=15, bold=True)]

    # Шкала часу
    t_start, t_end = 120, 780
    f.append(line(t_start, 410, t_end, 410, color=INK, sw=1.6))
    f.append(text(t_end, 428, "Час t →", size=11, color=MUTED, anchor="end"))

    # Рівні сигналів
    # 1. VDD (напруга живлення)
    y_vdd_top = 80
    y_vdd_bot = 160
    f.append(text(110, y_vdd_top + 30, "Напруга VDD", size=11, bold=True, color=POS, anchor="end"))
    f.append(line(t_start, y_vdd_bot, t_end, y_vdd_bot, color="#e2e8f0", sw=1, dash="3,3"))

    # Порогові рівні V_IT- та V_IT+
    y_thresh_fall = 115
    y_thresh_rise = 105
    f.append(line(t_start, y_thresh_fall, t_end, y_thresh_fall, color="#b5732e", sw=1.2, dash="4,4"))
    f.append(text(110, y_thresh_fall + 4, "V_IT− (поріг)", size=9.5, color="#b5732e", anchor="end", bold=True))
    f.append(line(t_start, y_thresh_rise, t_end, y_thresh_rise, color=FIELD, sw=1.2, dash="4,4"))
    f.append(text(110, y_thresh_rise - 3, "V_IT+ (+гіст.)", size=9.5, color=FIELD, anchor="end", bold=True))

    vdd_pts = [(120, y_vdd_bot), (150, 130), (170, y_thresh_rise), (200, y_vdd_top),
               (420, y_vdd_top), (430, 110), (440, y_vdd_top),
               (520, y_vdd_top), (540, 135), (560, 135), (600, y_thresh_rise), (630, y_vdd_top),
               (780, y_vdd_top)]
    poly_vdd = " ".join("%.1f,%.1f" % pt for pt in vdd_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_vdd, POS))

    # 2. Кварцовий генератор / тактування MCU (OSC)
    y_osc_base = 220
    f.append(text(110, y_osc_base + 15, "Тактовий ген.", size=11, bold=True, color="#6b46c1", anchor="end"))
    f.append(line(t_start, y_osc_base + 30, t_end, y_osc_base + 30, color="#e2e8f0", sw=1, dash="3,3"))
    f.append(text(220, y_osc_base - 8, "Нестабільна генерація (зрив частоти)", size=9.5, color="#6b46c1"))
    f.append(rect(170, y_osc_base, 110, 30, fill="#f5f3ff", stroke="#8b5cf6", sw=1, rx=3))
    f.append(text(225, y_osc_base + 18, "Старт кварцу / PLL", size=9.5, color="#6b46c1"))
    f.append(rect(280, y_osc_base, 240, 30, fill="#eafaf0", stroke=FIELD, sw=1, rx=3))
    f.append(text(400, y_osc_base + 18, "Стабільна тактова частота", size=10, color=FIELD))
    f.append(rect(540, y_osc_base, 60, 30, fill="#fdecea", stroke=POS, sw=1, rx=3))
    f.append(text(570, y_osc_base + 18, "Зрив", size=9.5, color=POS))
    f.append(rect(600, y_osc_base, 90, 30, fill="#f5f3ff", stroke="#8b5cf6", sw=1, rx=3))
    f.append(text(645, y_osc_base + 18, "Повторний старт", size=9.5, color="#6b46c1"))
    f.append(rect(690, y_osc_base, 90, 30, fill="#eafaf0", stroke=FIELD, sw=1, rx=3))
    f.append(text(735, y_osc_base + 18, "Стабільно", size=9.5, color=FIELD))

    # 3. Сигнал nRESET (активний низький)
    y_rst_top = 290
    y_rst_bot = 350
    f.append(text(110, y_rst_top + 30, "Вихід /RESET", size=11, bold=True, color=NEG, anchor="end"))
    f.append(line(t_start, y_rst_bot, t_end, y_rst_bot, color="#e2e8f0", sw=1, dash="3,3"))

    rst_pts = [(120, y_rst_bot), (290, y_rst_bot), (290, y_rst_top), (535, y_rst_top),
               (535, y_rst_bot), (710, y_rst_bot), (710, y_rst_top), (780, y_rst_top)]
    poly_rst = " ".join("%.1f,%.1f" % pt for pt in rst_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_rst, NEG))

    # Зони затримок t_rst
    f.append(rect(170, 70, 120, 310, fill="#e6f4ea", stroke="#34a853", sw=1.2, rx=0))
    f.append(line(170, 70, 170, 380, color="#34a853", sw=1.5, dash="4,4"))
    f.append(line(290, 70, 290, 380, color="#34a853", sw=1.5, dash="4,4"))
    f.append(arrow(170, 370, 290, 370, color="#2e7d32", sw=1.8))
    f.append(arrow(290, 370, 170, 370, color="#2e7d32", sw=1.8))
    f.append(text(230, 362, "Затримка t_rst (50–200 мс)", size=10, bold=True, color="#2e7d32"))

    # Фільтрація короткого викиду (Glitch)
    f.append(rect(415, 70, 35, 100, fill="#fff3cd", stroke="#ffc107", sw=1, rx=3))
    f.append(text(432, 60, "Короткий шум", size=9.5, bold=True, color="#b5732e"))
    f.append(text(432, 185, "фільтрується", size=9.5, color="#b5732e"))

    # Друга затримка t_rst
    f.append(rect(600, 70, 110, 310, fill="#e6f4ea", stroke="#34a853", sw=1.2, rx=0))
    f.append(line(535, 70, 535, 380, color=POS, sw=1.5, dash="4,4"))
    f.append(line(600, 70, 600, 380, color="#34a853", sw=1.5, dash="4,4"))
    f.append(line(710, 70, 710, 380, color="#34a853", sw=1.5, dash="4,4"))
    f.append(text(540, 50, "Аварія (Brownout)", size=9.5, bold=True, color=POS))
    f.append(arrow(600, 370, 710, 370, color="#2e7d32", sw=1.8))
    f.append(arrow(710, 370, 600, 370, color="#2e7d32", sw=1.8))
    f.append(text(655, 362, "Повторний t_rst", size=9.5, bold=True, color="#2e7d32"))

    f.append(text(W / 2, 444,
                  "Супервізор тримає скидання весь час наростання живлення + запас t_rst для стабілізації кварцу.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "por-timing-diagram.svg"), W, H, *f)


# ── фіг. 3. Сліпа зона внутрішнього BOD мікроконтролера ─────────────────────────
def fig_mcu_blind_zone():
    W, H = 840, 460
    f = [text(W / 2, 28, "Небезпека повільного спаду живлення: «сліпа зона» внутрішнього BOD мікроконтролера",
              size=14.5, bold=True)]

    # Вісь часу
    t0, t1 = 120, 780
    f.append(line(t0, 390, t1, 390, color=INK, sw=1.6))
    f.append(text(t1, 408, "Час розряду конденсаторів t →", size=11, color=MUTED, anchor="end"))

    # Рівні VDD
    y_vdd_3v3 = 80
    y_vdd_0v = 200
    f.append(text(110, y_vdd_3v3 + 10, "3.3 В (VDD)", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(text(110, 130, "2.7 В (BOD)", size=10, color="#b5732e", anchor="end"))
    f.append(text(110, 165, "1.2 В (Blind)", size=10, color=POS, anchor="end"))
    f.append(text(110, y_vdd_0v, "0.0 В (GND)", size=10.5, color=MUTED, anchor="end"))

    f.append(line(t0, 130, t1, 130, color="#b5732e", sw=1.2, dash="4,4"))
    f.append(line(t0, 165, t1, 165, color=POS, sw=1.4, dash="4,4"))
    f.append(line(t0, y_vdd_0v, t1, y_vdd_0v, color="#cbd5e1", sw=1))

    vdd_pts = [(120, y_vdd_3v3), (240, y_vdd_3v3), (360, 130), (520, 165), (740, 195)]
    poly_vdd = " ".join("%.1f,%.1f" % pt for pt in vdd_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_vdd, POS))

    # Зона 1: Норма (VDD > 2.7V)
    f.append(rect(120, 70, 240, 310, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=0))
    f.append(text(240, 60, "1. Нормальна робота", size=10.5, bold=True, color="#15803d"))

    # Зона 2: Спрацьовування BOD (2.7V > VDD > 1.2V)
    f.append(rect(360, 70, 160, 310, fill="#fffbeb", stroke="#f59e0b", sw=1, rx=0))
    f.append(text(440, 60, "2. Активне скидання", size=10.5, bold=True, color="#b45309"))

    # Зона 3: Сліпа зона (VDD < 1.2V)
    f.append(rect(520, 70, 260, 310, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=0))
    f.append(text(650, 60, "3. «СЛІПА ЗОНА» (BOD відмовляє!)", size=11, bold=True, color="#b91c1c"))

    # Сигнал RESET внутрішнього BOD MCU
    y_mcu_rst = 260
    f.append(text(110, y_mcu_rst + 10, "Внутрішній BOD MCU", size=10, bold=True, color=POS, anchor="end"))
    mcu_rst_pts = [(120, y_mcu_rst - 15), (360, y_mcu_rst - 15), (360, y_mcu_rst + 15),
                   (520, y_mcu_rst + 15), (550, y_mcu_rst - 5), (600, y_mcu_rst - 10),
                   (680, y_mcu_rst), (740, y_mcu_rst + 5)]
    poly_mcu = " ".join("%.1f,%.1f" % pt for pt in mcu_rst_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6,3"/>' % (poly_mcu, POS))
    f.append(text(650, y_mcu_rst - 16, "RESET «плаває» (Float)!", size=10, bold=True, color=POS))
    f.append(text(650, y_mcu_rst + 18, "Ядро виконує сміття → пошкодження Flash/EEPROM", size=9.5, color=POS))

    # Сигнал зовнішнього супервізора
    y_ext_rst = 330
    f.append(text(110, y_ext_rst + 10, "Зовнішній супервізор", size=10, bold=True, color=FIELD, anchor="end"))
    ext_rst_pts = [(120, y_ext_rst - 15), (360, y_ext_rst - 15), (360, y_ext_rst + 15), (740, y_ext_rst + 15)]
    poly_ext = " ".join("%.1f,%.1f" % pt for pt in ext_rst_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_ext, FIELD))
    f.append(text(650, y_ext_rst + 8, "Гарантований нуль до VDD = 0.5–0.8 В", size=10, bold=True, color=FIELD))

    f.append(text(W / 2, 442,
                  "Внутрішній BOD живиться від падаючої VDD і втрачає силу нижче 1.2 В. Зовнішній супервізор тримає 0 В надійно.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "mcu-blind-zone.svg"), W, H, *f)


# ── фіг. 4. Схема монтажного «АБО» (wired-OR) на відкритому стоці ─────────────
def fig_wired_or_reset():
    W, H = 840, 440
    f = [text(W / 2, 28, "Топологія монтажного «АБО» (wired-OR) на виході Open-Drain",
              size=15.5, bold=True)]

    # Шина VDD I/O (3.3V)
    rail_x0, rail_x1, rail_y = 120, 720, 75
    f.append(line(rail_x0, rail_y, rail_x1, rail_y, color=POS, sw=2.5))
    f.append(text(rail_x0 - 10, rail_y + 4, "VDD (3.3 В)", size=11, bold=True, color=POS, anchor="end"))

    # Резистор підтяжки R_pullup (4.7–10 кОм)
    pull_x = 420
    f.append(line(pull_x, rail_y, pull_x, 110, color=INK, sw=1.8))
    f.append(rect(pull_x - 18, 110, 36, 44, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(pull_x, 134, "R_PU", size=11, bold=True))
    f.append(text(pull_x + 24, 134, "10 кОм", size=9.5, color=MUTED, anchor="start"))
    node_rst_y = 190
    f.append(line(pull_x, 154, pull_x, node_rst_y, color=INK, sw=2))

    # Головна лінія nRESET (вузол wired-OR)
    line_x0, line_x1 = 150, 720
    f.append(line(line_x0, node_rst_y, line_x1, node_rst_y, color=NEG, sw=2.6))
    f.append(circle(pull_x, node_rst_y, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(pull_x, node_rst_y - 12, "Спільна лінія /RESET (Wired-OR)", size=11.5, bold=True, color=NEG))

    # 1. Супервізор ІС
    sup_x = 210
    f.append(rect(sup_x - 65, 240, 130, 110, fill="#faf5ff", stroke="#7c3aed", sw=1.6, rx=6))
    f.append(text(sup_x, 262, "Супервізор ІС", size=11, bold=True, color="#7c3aed"))
    f.append(text(sup_x, 280, "Open-Drain вихід", size=9.5, color=MUTED))
    f.append(line(sup_x, node_rst_y, sup_x, 305, color=INK, sw=1.6))
    f.append(circle(sup_x, node_rst_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(sup_x, 335, "NMOS ключик", size=9.5, color="#7c3aed", bold=True))

    # 2. Кнопка ручного скидання
    btn_x = 380
    f.append(rect(btn_x - 55, 240, 110, 110, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    f.append(text(btn_x, 262, "Кнопка скидання", size=11, bold=True, color="#2563eb"))
    f.append(text(btn_x, 280, "Тактова кнопка /MR", size=9.5, color=MUTED))
    f.append(line(btn_x, node_rst_y, btn_x, 305, color=INK, sw=1.6))
    f.append(circle(btn_x, node_rst_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(line(btn_x - 15, 310, btn_x + 15, 310, color=INK, sw=2))
    f.append(line(btn_x - 12, 320, btn_x + 12, 320, color=INK, sw=2))
    f.append(text(btn_x, 338, "замикає на GND", size=9, color="#2563eb"))

    # 3. Зневаджувач JTAG / SWD
    dbg_x = 550
    f.append(rect(dbg_x - 60, 240, 120, 110, fill="#fefce8", stroke="#ca8a04", sw=1.6, rx=6))
    f.append(text(dbg_x, 262, "Зневаджувач", size=11, bold=True, color="#ca8a04"))
    f.append(text(dbg_x, 280, "JTAG / SWD (nSRST)", size=9.5, color=MUTED))
    f.append(line(dbg_x, node_rst_y, dbg_x, 305, color=INK, sw=1.6))
    f.append(circle(dbg_x, node_rst_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(dbg_x, 335, "OD драйвер прогера", size=9, color="#ca8a04"))

    # 4. Приймач: MCU
    mcu_x = 690
    f.append(rect(mcu_x - 45, 150, 110, 180, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(mcu_x + 10, 175, "MCU / SoC", size=12, bold=True, color=FIELD))
    f.append(line(line_x1 - 30, node_rst_y, mcu_x - 45, node_rst_y, color=NEG, sw=2))
    f.append(circle(mcu_x - 45, node_rst_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(mcu_x - 40, node_rst_y - 8, "NRST", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(mcu_x + 10, 220, "Вхід скидання", size=9.5, color=MUTED))
    f.append(text(mcu_x + 10, 240, "тригера Шмітта", size=9.5, color=MUTED))

    # Спільний дріт GND
    f.append(line(150, 375, 620, 375, color=INK, sw=1.8))
    f.append(line(sup_x, 350, sup_x, 375, color=INK, sw=1.6))
    f.append(line(btn_x, 350, btn_x, 375, color=INK, sw=1.6))
    f.append(line(dbg_x, 350, dbg_x, 375, color=INK, sw=1.6))
    f.append(text(385, 395, "GND (спільна земля)", size=10, bold=True))

    f.append(text(W / 2, 424,
                  "Будь-який пристрій може безпечно притягнути шину до нуля, не ризикуючи коротким замиканням.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "wired-or-reset.svg"), W, H, *f)


# ── фіг. 5. Секвенування живлення трьох шин (Core, DDR, I/O) ──────────────────
def fig_power_sequencing_diagram():
    W, H = 840, 480
    f = [text(W / 2, 28, "Каскадне секвенування шин живлення сучасного процесора / FPGA",
              size=15, bold=True)]

    t_s, t_e = 130, 780
    f.append(line(t_s, 420, t_e, 420, color=INK, sw=1.6))
    f.append(text(t_e, 438, "Час t →", size=11, color=MUTED, anchor="end"))

    # 1. Core VDD (1.1 В)
    y_core = 90
    f.append(text(120, y_core + 12, "1. Core (1.1 В)", size=11, bold=True, color="#2563eb", anchor="end"))
    f.append(line(t_s, y_core + 25, t_e, y_core + 25, color="#e2e8f0", sw=1, dash="3,3"))
    core_pts = [(130, y_core + 25), (170, y_core + 25), (230, y_core - 15), (760, y_core - 15)]
    f.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.6"/>' % " ".join("%.1f,%.1f" % p for p in core_pts))

    # Power Good 1 (PG1 Core -> EN DDR)
    y_pg1 = 155
    f.append(text(120, y_pg1 + 10, "PG1 (Core OK)", size=10, bold=True, color="#059669", anchor="end"))
    f.append(line(t_s, y_pg1 + 18, t_e, y_pg1 + 18, color="#e2e8f0", sw=1, dash="3,3"))
    pg1_pts = [(130, y_pg1 + 18), (280, y_pg1 + 18), (280, y_pg1 - 10), (760, y_pg1 - 10)]
    f.append('<polyline points="%s" fill="none" stroke="#059669" stroke-width="2.2"/>' % " ".join("%.1f,%.1f" % p for p in pg1_pts))
    f.append(arrow(280, y_pg1 - 10, 310, 205, color="#059669", sw=1.6))
    f.append(text(310, 185, "EN DDR", size=9, bold=True, color="#059669"))

    # 2. DDR VDD (1.8 В)
    y_ddr = 215
    f.append(text(120, y_ddr + 12, "2. DDR (1.8 В)", size=11, bold=True, color="#d97706", anchor="end"))
    f.append(line(t_s, y_ddr + 25, t_e, y_ddr + 25, color="#e2e8f0", sw=1, dash="3,3"))
    ddr_pts = [(130, y_ddr + 25), (310, y_ddr + 25), (370, y_ddr - 15), (760, y_ddr - 15)]
    f.append('<polyline points="%s" fill="none" stroke="#d97706" stroke-width="2.6"/>' % " ".join("%.1f,%.1f" % p for p in ddr_pts))

    # Power Good 2 (PG2 DDR -> EN I/O)
    y_pg2 = 275
    f.append(text(120, y_pg2 + 10, "PG2 (DDR OK)", size=10, bold=True, color="#059669", anchor="end"))
    f.append(line(t_s, y_pg2 + 18, t_e, y_pg2 + 18, color="#e2e8f0", sw=1, dash="3,3"))
    pg2_pts = [(130, y_pg2 + 18), (420, y_pg2 + 18), (420, y_pg2 - 10), (760, y_pg2 - 10)]
    f.append('<polyline points="%s" fill="none" stroke="#059669" stroke-width="2.2"/>' % " ".join("%.1f,%.1f" % p for p in pg2_pts))
    f.append(arrow(420, y_pg2 - 10, 450, 325, color="#059669", sw=1.6))
    f.append(text(450, 305, "EN I/O", size=9, bold=True, color="#059669"))

    # 3. I/O VDD (3.3 В)
    y_io = 335
    f.append(text(120, y_io + 12, "3. I/O (3.3 В)", size=11, bold=True, color="#7c3aed", anchor="end"))
    f.append(line(t_s, y_io + 25, t_e, y_io + 25, color="#e2e8f0", sw=1, dash="3,3"))
    io_pts = [(130, y_io + 25), (450, y_io + 25), (510, y_io - 15), (760, y_io - 15)]
    f.append('<polyline points="%s" fill="none" stroke="#7c3aed" stroke-width="2.6"/>' % " ".join("%.1f,%.1f" % p for p in io_pts))

    # 4. Системний nRESET процесора
    y_sys_rst = 390
    f.append(text(120, y_sys_rst + 10, "System /RESET", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(line(t_s, y_sys_rst + 18, t_e, y_sys_rst + 18, color="#e2e8f0", sw=1, dash="3,3"))
    sys_rst_pts = [(130, y_sys_rst + 18), (660, y_sys_rst + 18), (660, y_sys_rst - 12), (760, y_sys_rst - 12)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (sys_rst_pts, POS))

    # Затримка скидання після останньої шини
    f.append(rect(510, 60, 150, 350, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=0))
    f.append(line(510, 60, 510, 410, color="#22c55e", sw=1.4, dash="4,4"))
    f.append(line(660, 60, 660, 410, color="#22c55e", sw=1.4, dash="4,4"))
    f.append(arrow(510, 400, 660, 400, color="#15803d", sw=1.6))
    f.append(arrow(660, 400, 510, 400, color="#15803d", sw=1.6))
    f.append(text(585, 392, "t_rst затримка (100–200 мс)", size=9.5, bold=True, color="#15803d"))

    f.append(text(W / 2, 464,
                  "Почергове ввімкнення (Core → DDR → I/O) усуває небезпеку тиристорного замикання (Latch-up).",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "power-sequencing-diagram.svg"), W, H, *f)


# ── фіг. 6. Віконний сторожовий таймер (Windowed Watchdog Timing) ──────────────
def fig_window_watchdog_timing():
    W, H = 840, 440
    f = [text(W / 2, 28, "Часові інтервали віконного сторожового таймера (Windowed Watchdog)",
              size=15, bold=True)]

    t0, t_w_open, t_w_close, t_max = 140, 340, 580, 740
    y_axis = 180
    f.append(line(t0, y_axis, t_max + 30, y_axis, color=INK, sw=2))
    f.append(text(t_max + 30, y_axis + 22, "Час від останнього скидання t →", size=11, color=MUTED, anchor="end"))

    # Вікно 1: ЗАЧИНЕНЕ ВІКНО
    f.append(rect(t0, 70, t_w_open - t0, 180, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=0))
    f.append(text((t0 + t_w_open) / 2, 95, "ЗАЧИНЕНЕ ВІКНО", size=12, bold=True, color="#b91c1c"))
    f.append(text((t0 + t_w_open) / 2, 115, "Скидання заборонено!", size=10, color="#b91c1c"))
    f.append(text((t0 + t_w_open) / 2, 135, "t < t_WD_min", size=10, bold=True, color="#b91c1c"))
    f.append(text((t0 + t_w_open) / 2, 215, "Аварія: збій лічильника /", size=9.5, color=POS))
    f.append(text((t0 + t_w_open) / 2, 230, "скажений пустий цикл", size=9.5, color=POS))

    # Вікно 2: ВІДЧИНЕНЕ ВІКНО
    f.append(rect(t_w_open, 70, t_w_close - t_w_open, 180, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=0))
    f.append(text((t_w_open + t_w_close) / 2, 95, "ВІДЧИНЕНЕ ВІКНО", size=12.5, bold=True, color="#15803d"))
    f.append(text((t_w_open + t_w_close) / 2, 115, "Дозволене скидання (Kick)", size=10.5, color="#15803d"))
    f.append(text((t_w_open + t_w_close) / 2, 135, "t_WD_min ≤ t ≤ t_WD_max", size=10, bold=True, color="#15803d"))
    f.append(circle((t_w_open + t_w_close) / 2, 180, 5, fill="#15803d", stroke="#15803d", sw=1))
    f.append(arrow((t_w_open + t_w_close) / 2, 230, (t_w_open + t_w_close) / 2, 190, color="#15803d", sw=2))
    f.append(text((t_w_open + t_w_close) / 2, 246, "Правильний WDI імпульс", size=10, bold=True, color="#15803d"))

    # Вікно 3: ТАЙМАУТ
    f.append(rect(t_w_close, 70, t_max - t_w_close, 180, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=0))
    f.append(text((t_w_close + t_max) / 2, 95, "ТАЙМАУТ", size=12, bold=True, color="#b91c1c"))
    f.append(text((t_w_close + t_max) / 2, 115, "Запізніле скидання", size=10, color="#b91c1c"))
    f.append(text((t_w_close + t_max) / 2, 135, "t > t_WD_max", size=10, bold=True, color="#b91c1c"))
    f.append(text((t_w_close + t_max) / 2, 215, "Аварія: зависання задачі /", size=9.5, color=POS))
    f.append(text((t_w_close + t_max) / 2, 230, "мертве блокування (Deadlock)", size=9.5, color=POS))

    # Межі вікон на осі
    f.append(line(t_w_open, 60, t_w_open, 260, color="#22c55e", sw=1.8, dash="4,4"))
    f.append(text(t_w_open, 275, "t_WD_min (початок вікна)", size=10, bold=True, color="#15803d"))
    f.append(line(t_w_close, 60, t_w_close, 260, color="#ef4444", sw=1.8, dash="4,4"))
    f.append(text(t_w_close, 275, "t_WD_max (кінець вікна)", size=10, bold=True, color="#b91c1c"))

    # Логіка спрацьовування
    y_rst_box = 320
    f.append(rect(140, y_rst_box, 600, 75, fill="#fafbfc", stroke="#4b5563", sw=1.5, rx=6))
    f.append(text(440, y_rst_box + 22, "Логіка спрацьовування апаратного скидання:", size=11, bold=True))
    f.append(text(440, y_rst_box + 44, "• Імпульс WDI у зачиненому вікні (t < t_WD_min) ⟹ Генерація /RESET (Аварія надшвидкого циклу)", size=9.5, color=POS))
    f.append(text(440, y_rst_box + 62, "• Відсутність WDI до таймауту (t > t_WD_max) ⟹ Генерація /RESET (Аварія зависання програми)", size=9.5, color=POS))

    f.append(text(W / 2, 424,
                  "Віконний сторож гарантує, що прошивка не просто жива, а виконує алгоритми з точно визначеним темпом.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "window-watchdog-timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_supervisor_architecture()
    fig_por_timing_diagram()
    fig_mcu_blind_zone()
    fig_wired_or_reset()
    fig_power_sequencing_diagram()
    fig_window_watchdog_timing()
    print("Готово: 6 фігур згенеровано у", IMG)
