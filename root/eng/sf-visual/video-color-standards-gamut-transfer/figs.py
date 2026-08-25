# -*- coding: utf-8 -*-
"""Фігури до теми «Колірні простори у відео (color-spaces-video)».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Декореляція сигналів: RGB проти Y'CbCr ──────────────────────────────
def fig_rgb_vs_ycbcr():
    W, H = 820, 310
    f = [text(W / 2, 25, "Декореляція сигналів: перетворення R'G'B' у простір Y'CbCr", size=15, bold=True)]

    # Ліва частина: Вхідні колірні канали R'G'B' (корельовані)
    f.append(rect(30, 55, 230, 230, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    f.append(text(145, 80, "Вхідні сигнали R'G'B'", size=13, bold=True, color="#991b1b"))
    f.append(text(145, 98, "(висока кореляція, 100% смуги)", size=10, color=MUTED))

    # Канали R, G, B
    f.append(rect(50, 115, 190, 38, fill="#fee2e2", stroke="#ef4444", sw=1, rx=4))
    f.append(text(145, 139, "R' (Червоний канал)", size=11, bold=True, color="#b91c1c"))

    f.append(rect(50, 163, 190, 38, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    f.append(text(145, 187, "G' (Зелений канал)", size=11, bold=True, color="#15803d"))

    f.append(rect(50, 211, 190, 38, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    f.append(text(145, 235, "B' (Синій канал)", size=11, bold=True, color="#1d4ed8"))

    # Блок лінійної матричної трансформації по центру
    f.append(rect(300, 110, 220, 120, fill="#faf5ff", stroke="#c084fc", sw=1.5, rx=8))
    f.append(text(410, 138, "Матричний конвертер", size=13, bold=True, color="#6b21a8"))
    f.append(text(410, 158, "Y' = W_R·R' + W_G·G' + W_B·B'", size=10, color=INK))
    f.append(text(410, 178, "Cb = (B' - Y') / (2 - 2W_B)", size=10, color=INK))
    f.append(text(410, 198, "Cr = (R' - Y') / (2 - 2W_R)", size=10, color=INK))

    # Стрілки від RGB до матриці
    f.append(line(260, 134, 300, 140, color="#ef4444", sw=2))
    f.append(line(260, 182, 300, 170, color="#22c55e", sw=2))
    f.append(line(260, 230, 300, 200, color="#3b82f6", sw=2))

    # Права частина: Вихідні декорельовані канали Y'CbCr
    f.append(rect(560, 55, 230, 230, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(675, 80, "Вихідні канали Y'CbCr", size=13, bold=True, color="#166534"))
    f.append(text(675, 98, "(декорельовані, розділена чутливість)", size=10, color=MUTED))

    # Канали Y', Cb, Cr
    f.append(rect(580, 115, 190, 38, fill="#fef08a", stroke="#eab308", sw=1, rx=4))
    f.append(text(675, 139, "Y' (Яскравість, 100% смуги)", size=11, bold=True, color="#854d0e"))

    f.append(rect(580, 163, 190, 38, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=4))
    f.append(text(675, 187, "Cb (Синя різниця, 25-50% смуги)", size=11, bold=True, color="#0369a1"))

    f.append(rect(580, 211, 190, 38, fill="#ffe4e6", stroke="#f43f5e", sw=1, rx=4))
    f.append(text(675, 235, "Cr (Червона різниця, 25-50% смуги)", size=11, bold=True, color="#be123c"))

    # Стрілки від матриці до Y'CbCr
    f.append(line(520, 140, 580, 134, color="#eab308", sw=2))
    f.append(line(520, 170, 580, 182, color="#0284c7", sw=2))
    f.append(line(520, 200, 580, 230, color="#f43f5e", sw=2))

    render(os.path.join(IMG, 'rgb-vs-ycbcr-decoupling.svg'), W, H, *f)


# ── 2. Колірне охоплення BT.601 / BT.709 проти BT.2020 ─────────────────────
def fig_color_gamut():
    W, H = 760, 420
    f = [text(W / 2, 25, "Колірне охоплення у хроматичних координатах CIE 1931 (x, y)", size=15, bold=True)]

    # Система координат (хроматична діаграма CIE 1931)
    ox, oy = 100, 370
    sx, sy = 550, 420  # Масштаб для координатного поля x: 0..0.8, y: 0..0.9

    # Границі осей
    f.append(line(ox, oy, ox + 600, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - 330, color=INK, sw=1.5))

    f.append(text(ox + 580, oy + 22, "Координата x", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 15, oy - 320, "Координата y", size=11, color=MUTED, anchor="start"))

    # Сітка координат
    for i in range(1, 8):
        val = i * 0.1
        cx = ox + int(val * sx)
        cy = oy - int(val * sy)
        if cx < ox + 580:
            f.append(line(cx, oy, cx, oy - 320, color="#f1f5f9", sw=1))
            f.append(text(cx, oy + 15, f"{val:.1f}", size=9, color=MUTED))
        if cy > oy - 320:
            f.append(line(ox, cy, ox + 580, cy, color="#f1f5f9", sw=1))
            f.append(text(ox - 10, cy + 3, f"{val:.1f}", size=9, color=MUTED))

    # Спектральна локус-крива CIE 1931 (приблизний контур у координатній сітці)
    cie_pts = [
        (0.174, 0.005), (0.008, 0.538), (0.074, 0.834), (0.23, 0.75),
        (0.44, 0.56), (0.64, 0.33), (0.735, 0.265), (0.174, 0.005)
    ]
    cie_poly = " ".join(f"{ox + int(px*sx)},{oy - int(py*sy)}" for px, py in cie_pts)
    f.append(f'<polygon points="{cie_poly}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3,3"/>')

    # BT.2020 Гамут (UHDTV) - трикутник R(0.708, 0.292), G(0.170, 0.797), B(0.131, 0.046)
    r_2020 = (ox + int(0.708*sx), oy - int(0.292*sy))
    g_2020 = (ox + int(0.170*sx), oy - int(0.797*sy))
    b_2020 = (ox + int(0.131*sx), oy - int(0.046*sy))
    pts_2020 = f"{r_2020[0]},{r_2020[1]} {g_2020[0]},{g_2020[1]} {b_2020[0]},{b_2020[1]}"
    f.append(f'<polygon points="{pts_2020}" fill="#10b981" fill-opacity="0.15" stroke="#10b981" stroke-width="2.5"/>')

    # BT.709 / sRGB Гамут (HDTV) - трикутник R(0.64, 0.33), G(0.30, 0.60), B(0.15, 0.06)
    r_709 = (ox + int(0.64*sx), oy - int(0.33*sy))
    g_709 = (ox + int(0.30*sx), oy - int(0.60*sy))
    b_709 = (ox + int(0.15*sx), oy - int(0.06*sy))
    pts_709 = f"{r_709[0]},{r_709[1]} {g_709[0]},{g_709[1]} {b_709[0]},{b_709[1]}"
    f.append(f'<polygon points="{pts_709}" fill="#3b82f6" fill-opacity="0.25" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="5,4"/>')

    # Точка білого D65 (x = 0.3127, y = 0.3290)
    d65_x = ox + int(0.3127 * sx)
    d65_y = oy - int(0.3290 * sy)
    f.append(circle(d65_x, d65_y, 5, fill="#dc2626", stroke="#ffffff", sw=1.5))
    f.append(text(d65_x + 10, d65_y + 4, "D65 (0.3127, 0.3290)", size=10, bold=True, color="#991b1b"))

    # Пояснювальна легенда
    lx, ly = 450, 60
    f.append(rect(lx, ly, 270, 110, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))

    f.append(line(lx + 15, ly + 25, lx + 45, ly + 25, color="#10b981", sw=2.5))
    f.append(text(lx + 55, ly + 29, "BT.2020 / HDR (75.8% CIE)", size=11, color=INK, bold=True, anchor="start"))

    f.append(line(lx + 15, ly + 55, lx + 45, ly + 55, color="#2563eb", sw=2.5, dash="5,4"))
    f.append(text(lx + 55, ly + 59, "BT.709 / BT.601 / sRGB (35.9% CIE)", size=11, color=INK, bold=True, anchor="start"))

    f.append(circle(lx + 30, ly + 85, 4, fill="#dc2626"))
    f.append(text(lx + 55, ly + 89, "Точка білого D65 (6500 K)", size=11, color=INK, bold=True, anchor="start"))

    render(os.path.join(IMG, 'color-gamut-primaries.svg'), W, H, *f)


# ── 3. Діапазони квантування: Studio Range проти Full Range ────────────────
def fig_limited_vs_full():
    W, H = 800, 280
    f = [text(W / 2, 25, "8-бітні рівні квантування Y'CbCr: Studio Range проти Full Range", size=15, bold=True)]

    # 1. Full Range (0 .. 255)
    y1 = 60
    f.append(rect(40, y1, 720, 75, fill="#f8fafc", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(55, y1 + 22, "Full Range (0–255, JPEG / ПК-монітори)", size=12, bold=True, color=INK, anchor="start"))

    # Суцільна смуга 0..255
    bx, bw = 180, 550
    f.append(rect(bx, y1 + 35, bw, 25, fill="#3b82f6", rx=3))
    f.append(text(bx, y1 + 30, "0", size=10, bold=True, color=INK, anchor="middle"))
    f.append(text(bx + bw, y1 + 30, "255", size=10, bold=True, color=INK, anchor="middle"))
    f.append(text(bx + bw/2, y1 + 52, "Повний активний діапазон сигналів (256 рівнів)", size=10, color="#ffffff", bold=True))

    # 2. Studio / Limited Range (16 .. 235/240)
    y2 = 165
    f.append(rect(40, y2, 720, 95, fill="#f8fafc", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(55, y2 + 22, "Studio / Limited Range (16–235 для Y', 16–240 для Cb/Cr, ТБ / BT.601 / BT.709)", size=12, bold=True, color=INK, anchor="start"))

    # Сегменти: Footroom (0..15), Active (16..235), Headroom (236..255)
    w_foot = int(bw * (16 / 256))
    w_act = int(bw * (220 / 256))
    w_head = bw - w_foot - w_act

    # Footroom (0..15)
    f.append(rect(bx, y2 + 40, w_foot, 28, fill="#cbd5e1", stroke="#94a3b8", sw=1))
    f.append(text(bx + w_foot/2, y2 + 58, "Foot", size=9, color=INK, bold=True))

    # Active Range (16..235)
    f.append(rect(bx + w_foot, y2 + 40, w_act, 28, fill="#10b981", stroke="#059669", sw=1))
    f.append(text(bx + w_foot + w_act/2, y2 + 58, "Активний відеодіапазон (16–235 / 240)", size=10, color="#ffffff", bold=True))

    # Headroom (236..255)
    f.append(rect(bx + w_foot + w_act, y2 + 40, w_head, 28, fill="#cbd5e1", stroke="#94a3b8", sw=1))
    f.append(text(bx + w_foot + w_act + w_head/2, y2 + 58, "Head", size=9, color=INK, bold=True))

    # Засічки чисел
    f.append(text(bx, y2 + 35, "0", size=10, bold=True, color=INK, anchor="middle"))
    f.append(text(bx + w_foot, y2 + 35, "16", size=10, bold=True, color="#059669", anchor="middle"))
    f.append(text(bx + w_foot + w_act, y2 + 35, "235/240", size=10, bold=True, color="#059669", anchor="middle"))
    f.append(text(bx + bw, y2 + 35, "255", size=10, bold=True, color=INK, anchor="middle"))

    # Пояснення знизу
    f.append(text(bx + w_foot/2, y2 + 82, "Захист від викидів ФНЧ", size=9, color=MUTED, anchor="middle"))
    f.append(text(bx + w_foot + w_act/2, y2 + 82, "220 градацій яркості Y' (225 градацій колірності Cb/Cr)", size=9, color="#047857", anchor="middle", bold=True))
    f.append(text(bx + w_foot + w_act + w_head/2, y2 + 82, "Захист від перерегулювання", size=9, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'limited-vs-full-range.svg'), W, H, *f)


if __name__ == '__main__':
    fig_rgb_vs_ycbcr()
    fig_color_gamut()
    fig_limited_vs_full()
    print("Всі 3 SVG фігури успішно згенеровано.")
