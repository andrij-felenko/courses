# -*- coding: utf-8 -*-
"""Фігури до теми «Коло під навантаженням» (circuit-under-real-load).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Еквівалентна схема реального джерела та спад напруги ──────────────────
def fig_power_sag_mechanism():
    W, H = 1100, 480
    f = [text(W / 2, 30, "Реальне джерело: внутрішній опір та індуктивність провідників провалюють напругу",
              size=15, bold=True)]

    # Блок «Джерело живлення» ліворуч
    sx, sy, sw, sh = 50, 70, 310, 340
    f.append(rect(sx, sy, sw, sh, fill="#f9fbfd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(sx + sw / 2, sy + 26, "Реальне джерело живлення", size=13, bold=True, color=NEG))
    f.append(text(sx + sw / 2, sy + 46, "акумулятор або стабілізатор", size=10.5, color=MUTED))

    # Ідеальна ЕРС
    ex, ey = 130, 240
    f.append(circle(ex, ey, 24, fill=BG, stroke=INK, sw=2))
    f.append(text(ex, ey - 4, "ЕРС", size=11, bold=True))
    f.append(text(ex, ey + 12, "E₀", size=10, color=MUTED))
    f.append(text(ex - 36, ey - 14, "+", size=14, bold=True, color=POS))
    f.append(text(ex - 36, ey + 22, "−", size=14, bold=True, color=NEG))

    # Внутрішній опір R_int
    rx, ry = 250, 160
    f.append(rect(rx - 25, ry - 14, 50, 28, fill="#fff2e6", stroke=POS, sw=1.8, rx=4))
    f.append(text(rx, ry + 4, "R_int", size=11, bold=True, color=POS))
    f.append(text(rx, ry - 22, "ESR джерела", size=10, color=MUTED))
    f.append(text(rx, ry + 28, "20–300 мОм", size=9.5, color=MUTED))

    # З'єднання всередині джерела
    f.append(line(ex, ey - 24, ex, ry, color=INK, sw=1.8))
    f.append(line(ex, ry, rx - 25, ry, color=INK, sw=1.8))
    f.append(line(rx + 25, ry, sx + sw, ry, color=POS, sw=2.2))
    f.append(circle(sx + sw, ry, 4, fill=POS, stroke=POS))
    f.append(text(sx + sw - 12, ry - 10, "V_bat+", size=10, bold=True, color=POS, anchor="end"))

    # Мінусова шина джерела
    gy = 350
    f.append(line(ex, ey + 24, ex, gy, color=INK, sw=1.8))
    f.append(line(ex, gy, sx + sw, gy, color=NEG, sw=2.2))
    f.append(circle(sx + sw, gy, 4, fill=NEG, stroke=NEG))
    f.append(text(sx + sw - 12, gy + 18, "GND_bat", size=10, bold=True, color=NEG, anchor="end"))

    # Блок «Кабель / Доріжки» посередині
    cx, cy, cw, ch = 400, 70, 310, 340
    f.append(rect(cx, cy, cw, ch, fill="#fdfbf7", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(cx + cw / 2, cy + 26, "Паразити провідників", size=13, bold=True, color=FIELD))
    f.append(text(cx + cw / 2, cy + 46, "доріжки плати, роз'єми, дріт", size=10.5, color=MUTED))

    # Верхня гілка (прямий провід): R_wire + L_wire
    rwx, rwy = 475, 160
    f.append(rect(rwx - 22, rwy - 14, 44, 28, fill="#fff2e6", stroke=POS, sw=1.8, rx=4))
    f.append(text(rwx, rwy + 4, "R_w+", size=11, bold=True, color=POS))
    f.append(text(rwx, rwy + 28, "50–500 мОм", size=9.5, color=MUTED))

    lwx, lwy = 625, 160
    # Котушка L_wire
    f.append(rect(lwx - 22, lwy - 14, 44, 28, fill="#eef3fb", stroke=NEG, sw=1.8, rx=4))
    f.append(text(lwx, lwy + 4, "L_w+", size=11, bold=True, color=NEG))
    f.append(text(lwx, lwy + 28, "10–200 нГн", size=9.5, color=MUTED))

    # З'єднання верхньої гілки
    f.append(line(sx + sw, ry, rwx - 22, ry, color=POS, sw=2.2))
    f.append(line(rwx + 22, ry, lwx - 22, ry, color=POS, sw=2.2))
    f.append(line(lwx + 22, ry, cx + cw, ry, color=POS, sw=2.2))
    f.append(circle(cx + cw, ry, 4, fill=POS, stroke=POS))

    # Стрілка струму
    f.append(arrow(rwx - 10, ry - 30, rwx + 60, ry - 30, color=POS, sw=2))
    f.append(text(rwx + 25, ry - 42, "Струм навантаження I(t)", size=10.5, bold=True, color=POS))

    # Нижня гілка (зворотний провід / земля): R_gnd + L_gnd
    rgx, rgy = 475, 350
    f.append(rect(rgx - 22, rgy - 14, 44, 28, fill="#fff2e6", stroke=POS, sw=1.8, rx=4))
    f.append(text(rgx, rgy + 4, "R_gnd", size=11, bold=True, color=POS))

    lgx, lgy = 625, 350
    f.append(rect(lgx - 22, lgy - 14, 44, 28, fill="#eef3fb", stroke=NEG, sw=1.8, rx=4))
    f.append(text(lgx, lgy + 4, "L_gnd", size=11, bold=True, color=NEG))

    f.append(line(sx + sw, gy, rgx - 22, gy, color=NEG, sw=2.2))
    f.append(line(rgx + 22, gy, lgx - 22, gy, color=NEG, sw=2.2))
    f.append(line(lgx + 22, gy, cx + cw, gy, color=NEG, sw=2.2))
    f.append(circle(cx + cw, gy, 4, fill=NEG, stroke=NEG))

    # Блок «Споживачі» праворуч
    lx, ly, lw, lh = 750, 70, 300, 340
    f.append(rect(lx, ly, lw, lh, fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, ly + 26, "Вузол споживачів", size=13, bold=True))
    f.append(text(lx + lw / 2, ly + 46, "мікроконтролер + динамічне навантаження", size=10.5, color=MUTED))

    # МК плата
    mx, my = 820, 240
    f.append(rect(mx - 40, my - 50, 80, 100, fill="#eef3fb", stroke=INK, sw=1.6, rx=6))
    f.append(text(mx, my - 24, "МК", size=13, bold=True))
    f.append(text(mx, my - 4, "MCU", size=10, color=MUTED))
    f.append(text(mx, my + 24, "I_mcu", size=10, color=POS))
    f.append(text(mx, my + 40, "~30 мА", size=9.5, color=MUTED))

    # Динамічне навантаження (мотор / радіомодуль)
    dx, dy = 970, 240
    f.append(rect(dx - 45, dy - 50, 90, 100, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    f.append(text(dx, dy - 24, "Мотор / RF", size=11.5, bold=True, color=POS))
    f.append(text(dx, dy - 4, "Кидок струму", size=10, color=POS))
    f.append(text(dx, dy + 18, "ΔI: 0.1 → 2.0 А", size=10, bold=True, color=POS))
    f.append(text(dx, dy + 36, "dI/dt: 10⁸ А/с", size=9.5, color=MUTED))

    # З'єднання споживачів
    f.append(line(cx + cw, ry, dx, ry, color=POS, sw=2.2))
    f.append(line(mx, ry, mx, my - 50, color=POS, sw=1.8))
    f.append(line(dx, ry, dx, dy - 50, color=POS, sw=1.8))

    f.append(line(cx + cw, gy, dx, gy, color=NEG, sw=2.2))
    f.append(line(mx, gy, mx, my + 50, color=NEG, sw=1.8))
    f.append(line(dx, gy, dx, dy + 50, color=NEG, sw=1.8))

    # Формула спаду напруги на навантаженні
    f.append(line(50, 430, W - 50, 430, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 458,
                  "U_load(t) = E₀ − I(t) · (R_int + R_w+ + R_gnd) − (L_w+ + L_gnd) · [dI(t)/dt]",
                  size=13.5, bold=True, color=POS))
    return W, H, f


# ── 2. Осцилограма кидка струму та просідання живлення (BOR) ──────────────────
def fig_inrush_and_voltage_droop():
    W, H = 1080, 520
    f = [text(W / 2, 30, "Перехідний процес: кидок струму при пуску мотора провалює шину живлення нижче порогу BOR",
              size=15, bold=True)]

    # Координати осей
    ox, oy1, oy2 = 120, 240, 460
    aw, ah = 880, 160

    # ── Верхній графік: Струм I(t)
    f.append(arrow(ox, oy1, ox + aw, oy1))
    f.append(arrow(ox, oy1, ox, oy1 - ah))
    f.append(text(ox + aw, oy1 + 24, "Час t (мс)", size=11, bold=True, anchor="end"))
    f.append(text(ox - 14, oy1 - ah + 10, "Струм I(t) (А)", size=11, bold=True, anchor="end"))

    # Шкала струму
    f.append(text(ox - 10, oy1 - 15, "0.0", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy1 - 35, "0.5", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy1 - 130, "2.5 (I_пуск)", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(line(ox, oy1 - 130, ox + aw - 40, oy1 - 130, color="#fdecea", sw=1, dash="3,3"))

    # Крива струму
    import math
    pts_i = [(ox, oy1 - 5)]
    for px in range(0, 100):
        pts_i.append((ox + px, oy1 - 6))
    for px in range(100, 125):
        t = (px - 100) / 25.0
        val = 6 + t * 124
        pts_i.append((ox + px, oy1 - val))
    for px in range(125, 800):
        t = (px - 125) / 160.0
        val = 26 + 104 * math.exp(-t)
        pts_i.append((ox + px, oy1 - val))
    path_i = "M %.1f %.1f " % pts_i[0] + " ".join("L %.1f %.1f" % p for p in pts_i[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_i, POS))

    f.append(text(ox + 160, oy1 - 140, "Пусковий струм мотора (I_stall)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(ox + 500, oy1 - 42, "Номінальний робочий струм (~0.4 А)", size=10.5, color=MUTED, anchor="start"))

    # ── Нижній графік: Напруга на МК U_mcu(t)
    f.append(arrow(ox, oy2, ox + aw, oy2))
    f.append(arrow(ox, oy2, ox, oy2 - ah))
    f.append(text(ox + aw, oy2 + 24, "Час t (мс)", size=11, bold=True, anchor="end"))
    f.append(text(ox - 14, oy2 - ah + 10, "Напруга U_mcu (В)", size=11, bold=True, anchor="end"))

    # Номінал 3.3 В
    y_nom = oy2 - 130
    f.append(line(ox, y_nom, ox + aw - 40, y_nom, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(ox - 10, y_nom + 4, "3.3 В (номінал)", size=10, bold=True, color=FIELD, anchor="end"))

    # Поріг Brownout Reset (2.7 В)
    y_bor = oy2 - 76
    f.append(line(ox, y_bor, ox + aw - 40, y_bor, color=NEG, sw=1.6, dash="5,3"))
    f.append(text(ox - 10, y_bor + 4, "2.7 В (поріг BOR)", size=10, bold=True, color=NEG, anchor="end"))

    # Крива напруги: 3.3 В -> різкий індуктивний провал L*dI/dt -> дно 2.2 В -> експоненційне відновлення
    pts_u = []
    for px in range(0, 100):
        pts_u.append((ox + px, y_nom))
    for px in range(100, 125):
        t = (px - 100) / 25.0
        val = y_nom + t * 90
        pts_u.append((ox + px, val))
    for px in range(125, 800):
        t = (px - 125) / 160.0
        ir_level = y_nom + 15
        val = ir_level + 75 * math.exp(-t)
        pts_u.append((ox + px, val))
    path_u = "M %.1f %.1f " % pts_u[0] + " ".join("L %.1f %.1f" % p for p in pts_u[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_u, INK))

    # Зона аварії BOR
    f.append(circle(ox + 125, y_nom + 90, 6, fill=POS, stroke=POS))
    f.append(line(ox + 125, y_nom + 90, ox + 220, y_nom + 120, color=POS, sw=1.2, dash="3,3"))
    f.append(mtext(ox + 230, y_nom + 115,
                   "Аварійний провал до 2.2 В!\nСпрацьовує Brownout Reset (BOD)\n→ МК раптово перезавантажується",
                   size=11, color=POS, anchor="start"))

    return W, H, f


# ── 3. Фізичний механізм Ground Bounce (підстрибування землі) ─────────────────
def fig_ground_bounce():
    W, H = 1080, 480
    f = [text(W / 2, 30, "Ground Bounce: швидкий спад струму крізь індуктивність землі спотворює логічний нуль",
              size=15, bold=True)]

    # Чіп-передавач (МК) ліворуч
    tx_x, tx_y, tx_w, tx_h = 80, 80, 260, 310
    f.append(rect(tx_x, tx_y, tx_w, tx_h, fill="#eef3fb", stroke=INK, sw=2, rx=10))
    f.append(text(tx_x + tx_w / 2, tx_y + 26, "Мікроконтролер (MCU)", size=13, bold=True))
    f.append(text(tx_x + tx_w / 2, tx_y + 46, "перемикає вихідні транзистори", size=10.5, color=MUTED))

    # Вихідний каскад МК
    cx, cy = tx_x + tx_w - 60, 240
    f.append(rect(cx - 24, cy - 35, 48, 70, fill=BG, stroke=INK, sw=1.6, rx=4))
    f.append(text(cx, cy - 8, "Вихід", size=10, bold=True))
    f.append(text(cx, cy + 12, "GPIO", size=10, color=FIELD))

    # Чіп-приймач (Сенсор / Периферія) праворуч
    rx_x, rx_y, rx_w, rx_h = 740, 80, 260, 310
    f.append(rect(rx_x, rx_y, rx_w, rx_h, fill="#fdfbf7", stroke=INK, sw=2, rx=10))
    f.append(text(rx_x + rx_w / 2, rx_y + 26, "Периферія / Сенсор", size=13, bold=True))
    f.append(text(rx_x + rx_w / 2, rx_y + 46, "приймає логічні рівні", size=10.5, color=MUTED))

    # Вхідний каскад сенсора
    rcx, rcy = rx_x + 60, 240
    f.append(rect(rcx - 24, rcy - 35, 48, 70, fill=BG, stroke=INK, sw=1.6, rx=4))
    f.append(text(rcx, rcy - 8, "Вхід", size=10, bold=True))
    f.append(text(rcx, rcy + 12, "RX / SCL", size=10, color=FIELD))

    # Лінія сигналу між чіпами
    sig_y = 240
    f.append(line(cx + 24, sig_y, rcx - 24, sig_y, color=FIELD, sw=2.4))
    f.append(circle(cx + 24, sig_y, 4, fill=FIELD, stroke=FIELD))
    f.append(circle(rcx - 24, sig_y, 4, fill=FIELD, stroke=FIELD))
    f.append(text((cx + 24 + rcx - 24) / 2, sig_y - 14, "Сигнальна лінія: логічний «0» (0 В)", size=11, bold=True, color=FIELD))

    # Земляна шина між чіпами з паразитною індуктивністю
    gnd_y = 350
    lx1 = 440
    f.append(rect(lx1 - 24, gnd_y - 14, 48, 28, fill="#eef3fb", stroke=NEG, sw=1.8, rx=4))
    f.append(text(lx1, gnd_y + 4, "L_gnd", size=11, bold=True, color=NEG))
    f.append(text(lx1, gnd_y + 28, "5–20 нГн (вивід + траса)", size=9.5, color=MUTED))

    f.append(line(tx_x + tx_w - 40, gnd_y, lx1 - 24, gnd_y, color=NEG, sw=2.4))
    f.append(line(lx1 + 24, gnd_y, rx_x + 40, gnd_y, color=NEG, sw=2.4))
    f.append(circle(tx_x + tx_w - 40, gnd_y, 4, fill=NEG, stroke=NEG))
    f.append(circle(rx_x + 40, gnd_y, 4, fill=NEG, stroke=NEG))

    # Стрілка струму розряду
    f.append(arrow(lx1 + 50, gnd_y - 25, lx1 - 30, gnd_y - 25, color=POS, sw=2))
    f.append(text(lx1 + 10, gnd_y - 38, "Швидкий кидок струму dI/dt (перемикання шини)", size=10.5, color=POS))

    # Локальні рівні землі
    f.append(text(tx_x + tx_w - 40, gnd_y - 14, "GND_чипа (зсунута!)", size=10, bold=True, color=POS, anchor="end"))
    f.append(text(rx_x + 40, gnd_y - 14, "GND_плати (0 В)", size=10, bold=True, color=NEG, anchor="start"))

    # Пояснювальний спайк напруги землі
    f.append(rect(430, 100, 240, 95, fill="#fff7e6", stroke=POS, sw=1.6, rx=6))
    f.append(text(550, 122, "V_bounce = L_gnd · (dI/dt)", size=12, bold=True, color=POS))
    f.append(text(550, 142, "Стрибок локальної землі МК:", size=10, color=INK))
    f.append(text(550, 160, "10 нГн · (100 мА / 1 нс) = 1.0 В!", size=10.5, bold=True, color=POS))
    f.append(text(550, 178, "Логічний «0» зчитується як «1»", size=10, color=MUTED))

    # Підсумок знизу
    f.append(line(60, 425, W - 60, 425, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 455,
                  "Підстрибування землі: сенсор бачить різницю між своїм GND і сигналом МК, що перевищує поріг V_IL",
                  size=12.5, bold=True))
    return W, H, f


# ── 4. RLC-контур та демпфування коливального дзвону ──────────────────────────
def fig_rlc_ringing_damping():
    W, H = 1080, 500
    f = [text(W / 2, 30, "RLC-дзвін живлення: компроміс між швидкістю відновлення та перерегулюванням",
              size=15, bold=True)]

    # Схема еквівалентного контуру вгорі
    cx, cy = 200, 90
    f.append(rect(50, 50, 360, 80, fill="#f9fbfd", stroke=INK, sw=1.5, rx=8))
    f.append(text(cx, 70, "Еквівалентний контур шини живлення", size=11.5, bold=True))
    f.append(text(cx, 114, "L_траси + R_втрат (ESR) + C_блокувальний", size=10, color=MUTED))

    # Графік перехідного процесу
    ox, oy = 120, 410
    aw, ah = 860, 240
    f.append(arrow(ox, oy, ox + aw, oy))
    f.append(arrow(ox, oy, ox, oy - ah))
    f.append(text(ox + aw, oy + 24, "Час t", size=11.5, bold=True, anchor="end"))
    f.append(text(ox - 14, oy - ah + 10, "Напруга на ємності U_c(t)", size=11.5, bold=True, anchor="end"))

    # Рівень встановленої напруги V0
    y_v0 = oy - ah * 0.65
    f.append(line(ox, y_v0, ox + aw - 30, y_v0, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox - 10, y_v0 + 4, "V₀ (усталена)", size=10.5, bold=True, color=MUTED, anchor="end"))

    # Крива 1: Недодемпфована (Underdamped, Q > 0.5)
    import math
    pts_under = []
    for px in range(0, 750):
        t = px / 60.0
        u = 1.0 - math.exp(-0.35 * t) * (math.cos(2.5 * t) + 0.14 * math.sin(2.5 * t))
        val = oy - u * (ah * 0.65)
        pts_under.append((ox + px, val))
    path_under = "M %.1f %.1f " % pts_under[0] + " ".join("L %.1f %.1f" % p for p in pts_under[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path_under, POS))

    # Крива 2: Критично демпфована (Critically damped, Q = 0.5)
    pts_crit = []
    for px in range(0, 750):
        t = px / 60.0
        u = 1.0 - (1.0 + 1.8 * t) * math.exp(-1.8 * t)
        val = oy - u * (ah * 0.65)
        pts_crit.append((ox + px, val))
    path_crit = "M %.1f %.1f " % pts_crit[0] + " ".join("L %.1f %.1f" % p for p in pts_crit[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path_crit, FIELD))

    # Крива 3: Передемпфована (Overdamped, Q < 0.5)
    pts_over = []
    for px in range(0, 750):
        t = px / 60.0
        u = 1.0 - 0.5 * (math.exp(-0.5 * t) + math.exp(-2.0 * t))
        val = oy - u * (ah * 0.65)
        pts_over.append((ox + px, val))
    path_over = "M %.1f %.1f " % pts_over[0] + " ".join("L %.1f %.1f" % p for p in pts_over[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,3"/>' % (path_over, NEG))

    # Підписи ліній у вільній зоні праворуч
    lx = 620
    # 1. Underdamped
    f.append(rect(lx, 80, 400, 60, fill="#fff2e6", stroke=POS, sw=1.6, rx=6))
    f.append(circle(lx + 20, 110, 5, fill=POS, stroke=POS))
    f.append(text(lx + 34, 102, "Недодемпфований (Q > 0.5, низький ESR):", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(lx + 34, 122, "Викид напруги до 1.8·V₀ — ризик пробою чіпа!", size=10, color=POS, anchor="start"))

    # 2. Critically damped
    f.append(rect(lx, 150, 400, 60, fill="#f2f8f2", stroke=FIELD, sw=1.6, rx=6))
    f.append(circle(lx + 20, 180, 5, fill=FIELD, stroke=FIELD))
    f.append(text(lx + 34, 172, "Критичне демпфування (Q = 0.5, R = 2·√(L/C)):", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(lx + 34, 192, "Найшвидший вихід на режим без перерегулювання", size=10, color=FIELD, anchor="start"))

    # 3. Overdamped
    f.append(rect(lx, 220, 400, 60, fill="#eef3fb", stroke=NEG, sw=1.6, rx=6))
    f.append(circle(lx + 20, 250, 5, fill=NEG, stroke=NEG))
    f.append(text(lx + 34, 242, "Передемпфований (Q < 0.5, високий опір):", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(lx + 34, 262, "Плавний, але повільний підйом без коливань", size=10, color=NEG, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "Керамічні конденсатори (MLCC) мають надмалий ESR → схильні до дзвону; потрібен паралельний демпфер або електроліт",
                  size=11, color=MUTED))
    return W, H, f


# ── 5. Ієрархія блокувальних конденсаторів та контурів струму ─────────────────
def fig_decoupling_hierarchy():
    W, H = 1100, 480
    f = [text(W / 2, 30, "Ієрархія живлення: локальна кераміка (MLCC) та об'ємний резервуар (Bulk) ділять частоти",
              size=15, bold=True)]

    # Блок «Батарея / Джерело»
    bx, by, bw, bh = 50, 120, 160, 220
    f.append(rect(bx, by, bw, bh, fill="#fff2e6", stroke=POS, sw=1.8, rx=8))
    f.append(text(bx + bw / 2, by + 26, "Джерело", size=13, bold=True, color=POS))
    f.append(text(bx + bw / 2, by + 46, "Акумулятор / LDO", size=10, color=MUTED))
    f.append(text(bx + bw / 2, by + 100, "Повільна реакція", size=10.5, bold=True, color=INK))
    f.append(text(bx + bw / 2, by + 118, "t > 10–100 мкс", size=10, color=MUTED))
    f.append(text(bx + bw / 2, by + 150, "Довгі дроти / траси", size=10, color=POS))
    f.append(text(bx + bw / 2, by + 168, "L_кабелю ~100 нГн", size=9.5, color=MUTED))

    # Блок «Об'ємна ємність Bulk»
    cx, cy, cw, ch = 350, 120, 220, 220
    f.append(rect(cx, cy, cw, ch, fill="#fdfbf7", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(cx + cw / 2, cy + 26, "Об'ємний Bulk-конденсатор", size=12, bold=True, color=FIELD))
    f.append(text(cx + cw / 2, cy + 46, "10–470 мкФ (електроліт / тантал)", size=10, color=MUTED))
    f.append(text(cx + cw / 2, cy + 100, "Резервуар енергії", size=10.5, bold=True, color=INK))
    f.append(text(cx + cw / 2, cy + 118, "t: 100 нс – 10 мкс", size=10, color=MUTED))
    f.append(text(cx + cw / 2, cy + 150, "Гасить просідання при старті", size=10, color=FIELD))
    f.append(text(cx + cw / 2, cy + 168, "Помірний ESR демпфує дзвін", size=9.5, color=MUTED))

    # Блок «Локальний MLCC»
    lx, ly, lw, lh = 680, 120, 210, 220
    f.append(rect(lx, ly, lw, lh, fill="#eef3fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(lx + lw / 2, ly + 26, "Локальний Decoupling MLCC", size=12, bold=True, color=NEG))
    f.append(text(lx + lw / 2, ly + 46, "0.1–1.0 мкФ (кераміка X7R/C0G)", size=10, color=MUTED))
    f.append(text(lx + lw / 2, ly + 100, "Швидкий розряд", size=10.5, bold=True, color=INK))
    f.append(text(lx + lw / 2, ly + 118, "t: 1 – 50 нс", size=10, color=MUTED))
    f.append(text(lx + lw / 2, ly + 150, "Стоїть впритул до ніжок!", size=10, bold=True, color=NEG))
    f.append(text(lx + lw / 2, ly + 168, "Мінімальна петля струму L", size=9.5, color=MUTED))

    # Блок «Кристал МК» праворуч
    kx, ky, kw, kh = 960, 140, 100, 180
    f.append(rect(kx, ky, kw, kh, fill="#1a1a1a", stroke=INK, sw=2, rx=6))
    f.append(text(kx + kw / 2, ky + 34, "Чип МК", size=12, bold=True, color=BG))
    f.append(text(kx + kw / 2, ky + 60, "Ядро", size=10, color="#9ca3af"))
    f.append(text(kx + kw / 2, ky + 110, "dI/dt", size=13, bold=True, color="#f87171"))
    f.append(text(kx + kw / 2, ky + 130, "10⁸ А/с", size=10, color="#fca5a5"))

    # Шини живлення зверху і знизу
    py, gy = 90, 370
    f.append(line(bx + bw, py, kx, py, color=POS, sw=2.4))
    f.append(line(bx + bw, gy, kx, gy, color=NEG, sw=2.4))

    # Відводи до компонентів
    f.append(line(cx + cw / 2, py, cx + cw / 2, cy, color=POS, sw=1.8))
    f.append(line(cx + cw / 2, cy + ch, cx + cw / 2, gy, color=NEG, sw=1.8))

    f.append(line(lx + lw / 2, py, lx + lw / 2, ly, color=POS, sw=1.8))
    f.append(line(lx + lw / 2, ly + lh, lx + lw / 2, gy, color=NEG, sw=1.8))

    # Стрілки петель струму
    f.append(arrow(kx, py, lx + lw / 2 + 10, py, color=POS, sw=2))
    f.append(text((lx + lw / 2 + kx) / 2, py - 12, "Коротка ВЧ-петля (~1 нГн)", size=10.5, bold=True, color=NEG))

    f.append(arrow(lx + lw / 2 - 10, py, cx + cw / 2 + 10, py, color=FIELD, sw=2))
    f.append(text((cx + cw / 2 + lx + lw / 2) / 2, py - 12, "Середня СЧ-петля", size=10, color=FIELD))

    # Підсумок
    f.append(line(50, 420, W - 50, 420, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 450,
                  "Конденсатор діє як місцевий акумулятор: чим швидший перехідний процес, тим ближче має стояти ємність",
                  size=12.5, bold=True))
    return W, H, f


for name, fn in [("power-sag-mechanism", fig_power_sag_mechanism),
                 ("inrush-and-voltage-droop", fig_inrush_and_voltage_droop),
                 ("ground-bounce", fig_ground_bounce),
                 ("rlc-ringing-damping", fig_rlc_ringing_damping),
                 ("decoupling-hierarchy", fig_decoupling_hierarchy)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
