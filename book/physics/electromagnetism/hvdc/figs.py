# -*- coding: utf-8 -*-
"""Фігури до теми «HVDC — постійний струм високої напруги».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#7f8c8d"


def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts_str, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw))


# ── Фігура 1: Пропускна здатність кабелю AC vs DC залежно від відстані ───────
def fig_ac_vs_dc_capacity():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Пропускна здатність кабелю: змінний струм (AC) vs HVDC", size=16, bold=True))

    ox, oy = 90, 330
    gw, gh = 620, 260

    # Сітка
    for y_val in range(100, 340, 50):
        f.append(line(ox, y_val, ox + gw, y_val, color="#e2e8f0", sw=1, dash="4,4"))
    for x_val in range(ox + 120, ox + gw, 120):
        f.append(line(x_val, oy - gh, x_val, oy, color="#e2e8f0", sw=1, dash="4,4"))

    # Вісь X та Y
    f.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))

    # Підписи осей
    f.append(text(ox + gw - 40, oy + 32, "Довжина лінії L (км)", size=12, bold=True, color=INK))
    f.append(text(ox - 65, oy - gh + 15, "Активна потужність P", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(ox - 65, oy - gh + 30, "(% від номіналу)", size=10, color=COLOR_GRAY, anchor="start"))

    # Позначки Y
    f.append(text(ox - 15, oy - 245, "100%", size=11, color=INK, anchor="end"))
    f.append(text(ox - 15, oy - 125, "50%", size=11, color=INK, anchor="end"))
    f.append(text(ox - 15, oy, "0%", size=11, color=INK, anchor="end"))

    # Позначки X
    f.append(text(ox, oy + 18, "0", size=11, color=INK))
    f.append(text(ox + 120, oy + 18, "50 км", size=11, color=INK))
    f.append(text(ox + 240, oy + 18, "100 км", size=11, color=INK))
    f.append(text(ox + 360, oy + 18, "500 км", size=11, color=INK))
    f.append(text(ox + 480, oy + 18, "1000 км", size=11, color=INK))
    f.append(text(ox + 600, oy + 18, "2000+ км", size=11, color=INK))

    # Крива DC
    dc_pts = [(ox, oy - 245), (ox + 150, oy - 243), (ox + 350, oy - 240), (ox + 600, oy - 235)]
    f.append(polyline(dc_pts, color=COLOR_BLUE, sw=3))
    f.append(text(ox + 420, oy - 255, "HVDC кабель (відсутній Ic)", size=12, bold=True, color=COLOR_BLUE, anchor="start"))

    # Крива AC підводного/підземного кабелю
    ac_cable_pts = [(ox, oy - 245), (ox + 60, oy - 200), (ox + 110, oy - 120), (ox + 160, oy - 30), (ox + 200, oy)]
    f.append(polyline(ac_cable_pts, color=COLOR_RED, sw=3))
    f.append(text(ox + 175, oy - 90, "AC кабель (Ic заповнює Імакс)", size=12, bold=True, color=COLOR_RED, anchor="start"))

    # Крива AC повітряної лінії
    ac_line_pts = [(ox, oy - 245), (ox + 180, oy - 210), (ox + 360, oy - 160), (ox + 480, oy - 110), (ox + 600, oy - 70)]
    f.append(polyline(ac_line_pts, color=COLOR_ORANGE, sw=2.5, dash="6,4"))
    f.append(text(ox + 350, oy - 130, "AC повітряна лінія (кутова стійкість)", size=11, bold=True, color=COLOR_ORANGE, anchor="start"))

    # Критична зона для кабелю AC
    f.append(line(ox + 160, oy - gh + 40, ox + 160, oy, color=COLOR_RED, sw=1.2, dash="3,3"))
    f.append(rect(ox + 115, oy - gh + 45, 90, 24, fill="#fbebe8", stroke=COLOR_RED, sw=1, rx=3))
    f.append(text(ox + 160, oy - gh + 61, "Lкрит ≈ 50-80 км", size=10, bold=True, color=COLOR_RED))

    return render(os.path.join(IMG_DIR, "ac-vs-dc-capacity.svg"), W, H, *f)


# ── Фігура 2: Топології HVDC систем ──────────────────────────────────────────
def fig_hvdc_topologies():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Топології систем HVDC: монополярна та біполярна", size=16, bold=True))

    midy = 215
    f.append(line(20, midy, W - 20, midy, color="#cbd5e1", sw=1.2, dash="4,4"))

    # === Верхній блок: Монополярна система ===
    f.append(text(40, 52, "1. Монополярна схема (один провідник + земля/море)", size=13, bold=True, color=COLOR_DARK, anchor="start"))

    # Перетворювач 1 (Випрямляч)
    f.append(rect(60, 75, 90, 60, fill="#eef6ff", stroke=COLOR_BLUE, sw=2, rx=5))
    f.append(text(105, 100, "Випрямляч", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(105, 118, "AC ➔ DC", size=10, color=COLOR_BLUE))

    # Перетворювач 2 (Інвертор)
    f.append(rect(270, 75, 90, 60, fill="#eef6ff", stroke=COLOR_BLUE, sw=2, rx=5))
    f.append(text(315, 100, "Інвертор", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(315, 118, "DC ➔ AC", size=10, color=COLOR_BLUE))

    # DC лінія (+U_dc)
    f.append(line(150, 90, 270, 90, color=COLOR_RED, sw=2.5))
    f.append(text(210, 80, "+U_dc (полюс)", size=11, bold=True, color=COLOR_RED))

    # Земляний повернення
    f.append(line(105, 135, 105, 165, color=COLOR_GRAY, sw=2))
    f.append(line(315, 135, 315, 165, color=COLOR_GRAY, sw=2))
    f.append(line(90, 165, 120, 165, color=COLOR_GRAY, sw=2))
    f.append(line(96, 170, 114, 170, color=COLOR_GRAY, sw=1.8))
    f.append(line(102, 175, 108, 175, color=COLOR_GRAY, sw=1.5))
    f.append(line(300, 165, 330, 165, color=COLOR_GRAY, sw=2))
    f.append(line(306, 170, 324, 170, color=COLOR_GRAY, sw=1.8))
    f.append(line(312, 175, 318, 175, color=COLOR_GRAY, sw=1.5))

    f.append(text(210, 170, "Земляний / морський зворотний шлях (I_dc)", size=10, color=COLOR_GRAY, italic=True))

    # === Правий верхній блок: Back-to-Back (B2B) ===
    f.append(text(450, 52, "2. Вставка постійного струму (B2B)", size=13, bold=True, color=COLOR_DARK, anchor="start"))
    f.append(rect(470, 75, 80, 60, fill="#f4f6f7", stroke=COLOR_DARK, sw=1.8, rx=4))
    f.append(text(510, 105, "LCC / VSC", size=11, bold=True, color=COLOR_DARK))
    f.append(rect(610, 75, 80, 60, fill="#f4f6f7", stroke=COLOR_DARK, sw=1.8, rx=4))
    f.append(text(650, 105, "VSC / LCC", size=11, bold=True, color=COLOR_DARK))
    f.append(line(550, 105, 610, 105, color=COLOR_RED, sw=2.5))
    f.append(text(580, 95, "DC шина", size=9, color=COLOR_RED, bold=True))
    f.append(text(580, 160, "Об'єднання несинхронних AC мереж", size=10, color=COLOR_DARK))
    f.append(text(580, 175, "(L = 0 км, різна частота/фаза)", size=9, color=COLOR_GRAY))

    # === Нижній блок: Біполярна система ===
    f.append(text(40, 240, "3. Біполярна схема (найпоширеніша: +U_dc та -U_dc, подвійна надійність)", size=13, bold=True, color=COLOR_DARK, anchor="start"))

    f.append(rect(60, 260, 100, 125, fill="#f0f9ff", stroke=COLOR_BLUE, sw=2, rx=6))
    f.append(text(110, 280, "Підстанція A", size=11, bold=True, color=COLOR_BLUE))
    f.append(rect(75, 292, 70, 30, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2, rx=3))
    f.append(text(110, 311, "Полюс +", size=10, bold=True, color=COLOR_RED))
    f.append(rect(75, 340, 70, 30, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2, rx=3))
    f.append(text(110, 359, "Полюс -", size=10, bold=True, color=COLOR_BLUE))

    f.append(rect(620, 260, 100, 125, fill="#f0f9ff", stroke=COLOR_BLUE, sw=2, rx=6))
    f.append(text(670, 280, "Підстанція B", size=11, bold=True, color=COLOR_BLUE))
    f.append(rect(635, 292, 70, 30, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2, rx=3))
    f.append(text(670, 311, "Полюс +", size=10, bold=True, color=COLOR_RED))
    f.append(rect(635, 340, 70, 30, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2, rx=3))
    f.append(text(670, 359, "Полюс -", size=10, bold=True, color=COLOR_BLUE))

    f.append(line(145, 307, 635, 307, color=COLOR_RED, sw=2.5))
    f.append(text(390, 298, "+U_dc (наприклад, +500 кВ)", size=11, bold=True, color=COLOR_RED))

    f.append(line(160, 326, 620, 326, color=COLOR_GRAY, sw=1.5, dash="5,5"))
    f.append(text(390, 323, "Нейтральний провідник / Земля (0 В)", size=9, color=COLOR_GRAY))

    f.append(line(145, 355, 635, 355, color=COLOR_BLUE, sw=2.5))
    f.append(text(390, 370, "-U_dc (наприклад, -500 кВ)", size=11, bold=True, color=COLOR_BLUE))

    return render(os.path.join(IMG_DIR, "hvdc-topologies.svg"), W, H, *f)


# ── Фігура 3: LCC vs VSC перетворювачі ───────────────────────────────────────
def fig_lcc_vs_vsc():
    W, H = 800, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Технології вентильних перетворювачів: LCC vs VSC (MMC)", size=16, bold=True))

    midx = 400
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # === ЛІВА СТОРОНА: LCC (Line-Commutated Converter) ===
    f.append(text(40, 54, "LCC / CSC (Класична технологія)", size=13, bold=True, color=COLOR_DARK, anchor="start"))
    f.append(text(40, 72, "Тиристори • Мережева комутація", size=11, color=COLOR_GRAY, anchor="start"))

    tx, ty = 80, 110
    f.append(line(tx, ty, tx + 240, ty, color=COLOR_RED, sw=2.5))
    f.append(text(tx + 255, ty + 4, "+U_dc", size=11, bold=True, color=COLOR_RED, anchor="start"))

    f.append(line(tx, ty + 150, tx + 240, ty + 150, color=COLOR_BLUE, sw=2.5))
    f.append(text(tx + 255, ty + 154, "-U_dc", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    phases = ["A", "B", "C"]
    for i in range(3):
        px = tx + 40 + i * 80
        f.append(line(px, ty, px, ty + 150, color=LINE, sw=1.8))
        f.append(polygon([(px - 10, ty + 30), (px + 10, ty + 30), (px, ty + 50)], fill="#eef6ff", stroke=COLOR_BLUE, sw=1.5))
        f.append(line(px - 10, ty + 50, px + 10, ty + 50, color=COLOR_BLUE, sw=1.5))
        f.append(polygon([(px - 10, ty + 100), (px + 10, ty + 100), (px, ty + 120)], fill="#eef6ff", stroke=COLOR_BLUE, sw=1.5))
        f.append(line(px - 10, ty + 120, px + 10, ty + 120, color=COLOR_BLUE, sw=1.5))
        f.append(line(px, ty + 75, px - 25, ty + 75, color=COLOR_ORANGE, sw=1.5))
        f.append(text(px - 35, ty + 78, phases[i], size=10, bold=True, color=COLOR_ORANGE, anchor="end"))

    f.append(rect(35, ty + 175, 330, 125, fill="#fcf8f2", stroke=COLOR_ORANGE, sw=1.2, rx=5))
    f.append(text(50, ty + 195, "Особливості LCC:", size=11, bold=True, color=COLOR_ORANGE, anchor="start"))
    f.append(text(50, ty + 215, "• Потужність до 12 ГВт, напруга до ±1100 кВ", size=10, color=INK, anchor="start"))
    f.append(text(50, ty + 233, "• Потребує потужної мережі AC для комутації", size=10, color=INK, anchor="start"))
    f.append(text(50, ty + 251, "• Споживає реактивну потужність (cos φ ≈ 0.7)", size=10, color=INK, anchor="start"))
    f.append(text(50, ty + 269, "• Ризик збоїв комутації (commutation failure)", size=10, color=COLOR_RED, anchor="start"))

    # === ПРАВА СТОРОНА: VSC (Voltage Source Converter - MMC) ===
    f.append(text(440, 54, "VSC / MMC (Сучасна технологія)", size=13, bold=True, color=COLOR_DARK, anchor="start"))
    f.append(text(440, 72, "IGBT • Самокомутація (ШІМ/MMC)", size=11, color=COLOR_GRAY, anchor="start"))

    vx, vy = 480, 110
    f.append(line(vx, vy, vx + 240, vy, color=COLOR_RED, sw=2.5))
    f.append(text(vx + 255, vy + 4, "+U_dc", size=11, bold=True, color=COLOR_RED, anchor="start"))
    f.append(line(vx, vy + 150, vx + 240, vy + 150, color=COLOR_BLUE, sw=2.5))
    f.append(text(vx + 255, vy + 154, "-U_dc", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    for i in range(3):
        px = vx + 40 + i * 80
        f.append(line(px, vy, px, vy + 150, color=LINE, sw=1.8))
        f.append(rect(px - 16, vy + 20, 32, 24, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5, rx=3))
        f.append(text(px, vy + 36, "SM", size=10, bold=True, color=COLOR_GREEN))
        f.append(rect(px - 16, vy + 105, 32, 24, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5, rx=3))
        f.append(text(px, vy + 121, "SM", size=10, bold=True, color=COLOR_GREEN))
        f.append(line(px, vy + 75, px + 25, vy + 75, color=COLOR_PURPLE, sw=1.5))
        f.append(text(px + 33, vy + 78, phases[i], size=10, bold=True, color=COLOR_PURPLE, anchor="start"))

    f.append(rect(435, vy + 175, 330, 125, fill="#f2f9f6", stroke=COLOR_GREEN, sw=1.2, rx=5))
    f.append(text(450, vy + 195, "Особливості VSC (MMC):", size=11, bold=True, color=COLOR_GREEN, anchor="start"))
    f.append(text(450, vy + 215, "• Незалежне керування P та Q у 4 квадрантах", size=10, color=INK, anchor="start"))
    f.append(text(450, vy + 233, "• Здатність до чорного старту (Black Start)", size=10, color=INK, anchor="start"))
    f.append(text(450, vy + 251, "• Працює зі слабкими та офшорними AC мережами", size=10, color=INK, anchor="start"))
    f.append(text(450, vy + 269, "• Майже ідеальна синусоїда (тисячі рівнів MMC)", size=10, color=COLOR_BLUE, anchor="start"))

    return render(os.path.join(IMG_DIR, "lcc-vs-vsc.svg"), W, H, *f)


# ── Фігура 4: Економічна точка рівноцінності (Break-even distance) ───────────
def fig_breakeven_distance():
    W, H = 740, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Економічна точка рівноцінності (Break-even distance) AC vs HVDC", size=16, bold=True))

    ox, oy = 90, 330
    gw, gh = 600, 260

    # Сітка
    for y_val in range(110, 340, 50):
        f.append(line(ox, y_val, ox + gw, y_val, color="#e2e8f0", sw=1, dash="4,4"))

    # Осі
    f.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))

    f.append(text(ox + gw - 20, oy + 32, "Довжина лінії L (км)", size=12, bold=True, color=INK))
    f.append(text(ox - 65, oy - gh + 15, "Сумарна вартість C", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(ox - 65, oy - gh + 30, "(капітал + втрати)", size=10, color=COLOR_GRAY, anchor="start"))

    ac_line = [(ox, oy - 50), (ox + 600, oy - 270)]
    f.append(polyline(ac_line, color=COLOR_RED, sw=2.5))
    f.append(text(ox + 460, oy - 250, "Сумарні витрати AC", size=12, bold=True, color=COLOR_RED, anchor="start"))

    dc_line = [(ox, oy - 140), (ox + 600, oy - 230)]
    f.append(polyline(dc_line, color=COLOR_BLUE, sw=2.5))
    f.append(text(ox + 460, oy - 205, "Сумарні витрати HVDC", size=12, bold=True, color=COLOR_BLUE, anchor="start"))

    ix = ox + 415
    iy = oy - 202

    f.append(circle(ix, iy, 7, fill=COLOR_GREEN, stroke="#ffffff", sw=2))
    f.append(line(ix, iy, ix, oy, color=COLOR_GREEN, sw=1.5, dash="4,4"))

    f.append(rect(ix - 85, iy - 45, 170, 32, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.2, rx=4))
    f.append(text(ix, iy - 32, "Точка рівноцінності L_break-even", size=10, bold=True, color=COLOR_GREEN))
    f.append(text(ix, iy - 18, "Повітряні лінії: 600-800 км", size=9, color=COLOR_DARK))

    f.append(text(ox + 10, oy - 62, "C_станцій (AC)", size=10, color=COLOR_RED, bold=True, anchor="start"))
    f.append(text(ox + 10, oy - 152, "C_станцій (HVDC)", size=10, color=COLOR_BLUE, bold=True, anchor="start"))

    f.append(text(ox + 180, oy - 30, "AC дешевше (короткі лінії)", size=11, bold=True, color=COLOR_RED))
    f.append(text(ox + 500, oy - 30, "HVDC дешевше (довгі лінії)", size=11, bold=True, color=COLOR_BLUE))

    return render(os.path.join(IMG_DIR, "breakeven-distance.svg"), W, H, *f)


if __name__ == '__main__':
    fig_ac_vs_dc_capacity()
    fig_hvdc_topologies()
    fig_lcc_vs_vsc()
    fig_breakeven_distance()
    print("Фігури HVDC успішно згенеровано у ./img/")
