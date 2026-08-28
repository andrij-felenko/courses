# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Колір як вимірювання' (color-sensor).
Вивід: ./img/*.svg
"""

import sys
import os
import math

# Підключаємо svgkit з кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_cie_curves():
    """Фігура 1: Криві колірного узгодження CIE 1931 (x_bar, y_bar, z_bar)."""
    w, h = 800, 440
    frags = []

    # Рамка графіка
    gx, gy, gw, gh = 80, 60, 660, 310
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=4))

    # Сітка та мітки довжин хвиль (380 - 700 нм, крок 50 нм)
    wavelengths = [400, 450, 500, 550, 600, 650, 700]
    for wl in wavelengths:
        px = gx + (wl - 380) / (720 - 380) * gw
        frags.append(line(px, gy, px, gy + gh, color="#f0f2f5", sw=1.0))
        frags.append(text(px, gy + gh + 20, "%d нм" % wl, size=11, color=MUTED))

    # Горизонтальна сітка (0.0, 0.5, 1.0, 1.5, 2.0)
    for v in [0.0, 0.5, 1.0, 1.5, 2.0]:
        py = gy + gh - (v / 2.0) * gh
        frags.append(line(gx, py, gx + gw, py, color="#f0f2f5", sw=1.0))
        frags.append(text(gx - 12, py + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))

    # Осі
    frags.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.5))
    frags.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.5))

    # Аналітичні наближення кривих CIE 1931
    def x_bar(l):
        a1 = 1.056 * math.exp(-0.5 * ((l - 599.8) / 37.9) ** 2)
        a2 = 0.362 * math.exp(-0.5 * ((l - 442.0) / 16.0) ** 2)
        a3 = -0.065 * math.exp(-0.5 * ((l - 501.1) / 20.4) ** 2)
        return max(0.0, a1 + a2 + a3)

    def y_bar(l):
        return 1.011 * math.exp(-0.5 * ((math.log(l) - math.log(555.0)) / 0.085) ** 2)

    def z_bar(l):
        return 1.773 * math.exp(-0.5 * ((math.log(l) - math.log(446.0)) / 0.075) ** 2)

    def curve_path(fn, color, sw=2.5, dash=None):
        pts = []
        for wl_i in range(380, 721, 2):
            px = gx + (wl_i - 380) / (720 - 380) * gw
            val = fn(wl_i)
            py = gy + gh - (val / 2.0) * gh
            pts.append("%.1f,%.1f" % (px, py))
        d_str = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (" ".join(pts), color, sw, d_str)

    frags.append(curve_path(z_bar, "#2457d6", sw=2.5)) # z̄(λ) - синій
    frags.append(curve_path(y_bar, "#27ae60", sw=2.5)) # ȳ(λ) - зелений (фотометрична крива V(λ))
    frags.append(curve_path(x_bar, "#c0392b", sw=2.5)) # x̄(λ) - червоний

    # Підписи кривих
    frags.append(text(210, 115, "z̄(λ) [короткохвильовий пік 446 нм]", size=12, color="#2457d6", bold=True, anchor="start"))
    frags.append(text(435, 175, "ȳ(λ) ≡ V(λ) [пік 555 нм, світлова віддача]", size=12, color="#27ae60", bold=True, anchor="start"))
    frags.append(text(505, 125, "x̄(λ) [двогорбий: 442 нм і 600 нм]", size=12, color="#c0392b", bold=True, anchor="start"))

    # Підписи осей
    frags.append(text(gx + gw / 2, gy + gh + 42, "Довжина оптичної хвилі λ (нанометри)", size=13, color=INK, bold=True))
    frags.append(text(gx + 15, gy - 20, "Чутливість / Коефіцієнт тристимулусу", size=13, color=INK, bold=True, anchor="start"))

    render(os.path.join(OUT, "cie-tristimulus-curves.svg"), w, h, *frags)


def fig_rgbc_stack():
    """Фігура 2: Структура пікселя колірного сенсора RGBC з інтерференційними фільтрами."""
    w, h = 820, 450
    frags = []

    # Верхній блок: Оптичний вхід (падаюче біле світло)
    frags.append(fitbox(60, 20, 700, 36, "Падаюче оптичне випромінювання (видиме світло 380–700 нм + фонове ІЧ > 700 нм)", size=13, fill="#fff9db", stroke="#f59f00", bold=True))

    # 4 канали: Red, Green, Blue, Clear
    channels = [
        ("Канал RED (R)", "#ffe3e3", "#c0392b", 60, "Інтерференційний фільтр 580–650 нм"),
        ("Канал GREEN (G)", "#d3f9d8", "#27ae60", 240, "Інтерференційний фільтр 490–570 нм"),
        ("Канал BLUE (B)", "#d0ebff", "#2457d6", 420, "Інтерференційний фільтр 420–490 нм"),
        ("Канал CLEAR (C)", "#f1f3f5", "#495057", 600, "Широкосмуговий IR-cut фільтр 400–680 нм")
    ]

    for title, fill_c, strk_c, x_pos, filter_desc in channels:
        # Мікролінза
        frags.append(rect(x_pos, 75, 160, 24, fill="#e7f5ff", stroke="#339af0", sw=1.5, rx=12))
        frags.append(text(x_pos + 80, 91, "Мікролінза (фокусування)", size=10, color="#1971c2"))

        # Промінь світла
        frags.append(arrow(x_pos + 80, 56, x_pos + 80, 75, color="#f59f00", sw=1.5))
        frags.append(arrow(x_pos + 80, 99, x_pos + 80, 115, color=strk_c, sw=1.5))

        # Інтерференційний фільтр Фабрі-Перо
        frags.append(rect(x_pos, 115, 160, 48, fill=fill_c, stroke=strk_c, sw=1.8, rx=4))
        frags.append(text(x_pos + 80, 134, title, size=12, color=strk_c, bold=True))
        frags.append(text(x_pos + 80, 152, filter_desc, size=9, color=INK))

        # Пасивація та екранування металом
        frags.append(rect(x_pos, 175, 160, 22, fill="#e9ecef", stroke="#868e96", sw=1.2, rx=2))
        frags.append(text(x_pos + 80, 190, "Екранування металом (Al/Cu)", size=10, color="#495057"))

        # Збіднена область p-n переходу фотодіода
        frags.append(rect(x_pos, 205, 160, 65, fill="#fff4e6", stroke="#d9480f", sw=1.5, rx=4))
        frags.append(text(x_pos + 80, 228, "Кремнієвий фотодіод", size=12, color="#d9480f", bold=True))
        frags.append(text(x_pos + 80, 246, "Збіднена область p-n", size=10, color=INK))
        frags.append(text(x_pos + 80, 260, "Генерація фотоструму I_ph", size=10, color=MUTED))

        # Сигнал у схему
        frags.append(arrow(x_pos + 80, 270, x_pos + 80, 305, color="#1a1a1a", sw=1.5))

    # Нижній шар: Інтегратор, мультиплексор та АЦП
    frags.append(fitbox(60, 305, 700, 45, "Аналогові інтегратори струму (Current-to-Frequency / Sigma-Delta АЦП 16-біт)", size=13, fill="#f8f9fa", stroke="#212529", bold=True))
    frags.append(arrow(410, 350, 410, 385, color="#1a1a1a", sw=1.8))
    frags.append(fitbox(180, 385, 460, 40, "Цифровий інтерфейс I2C / SPI: Регістри сирих відліків (CDATA, RDATA, GDATA, BDATA)", size=12, fill="#e7f5ff", stroke="#1c7ed6", bold=True))

    render(os.path.join(OUT, "rgbc-filter-stack.svg"), w, h, *frags)


def fig_pipeline_flow():
    """Фігура 3: Блок-схема колориметричного конвеєра обробки."""
    w, h = 840, 460
    frags = []

    # Крок 1: Сирі відліки
    frags.append(rect(40, 40, 220, 110, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=6))
    frags.append(text(150, 65, "1. Сирі відліки АЦП", size=13, color=INK, bold=True))
    frags.append(text(150, 88, "R_raw, G_raw, B_raw, C_raw", size=11, color="#c0392b"))
    frags.append(text(150, 108, "Час накопичення ATIME", size=10, color=MUTED))
    frags.append(text(150, 126, "Аналогове підсилення AGAIN", size=10, color=MUTED))

    frags.append(arrow(260, 95, 310, 95, color=LINE, sw=1.8))

    # Крок 2: Нормування та компенсація
    frags.append(rect(310, 40, 230, 110, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5, rx=6))
    frags.append(text(425, 65, "2. Нормування та ІЧ-відсікання", size=13, color="#1c7ed6", bold=True))
    frags.append(text(425, 88, "N = Raw / (ATIME · AGAIN)", size=11, color=INK))
    frags.append(text(425, 108, "Віднімання темнового струму", size=10, color=MUTED))
    frags.append(text(425, 126, "Компенсація ІЧ-хвоста (Clear/IR)", size=10, color=MUTED))

    frags.append(arrow(540, 95, 590, 95, color=LINE, sw=1.8))

    # Крок 3: Колірна матриця CCM
    frags.append(rect(590, 40, 210, 110, fill="#f3f0ff", stroke="#7950f2", sw=1.5, rx=6))
    frags.append(text(695, 65, "3. Матриця корекції (CCM)", size=13, color="#7950f2", bold=True))
    frags.append(text(695, 90, "[X, Y, Z]ᵀ = M · [R, G, B]ᵀ", size=12, color=INK))
    frags.append(text(695, 115, "Калібрування ColorChecker", size=10, color=MUTED))
    frags.append(text(695, 133, "Опорний ілюмінант D65/A", size=10, color=MUTED))

    # Стрілка вниз до результатів
    frags.append(arrow(695, 150, 695, 200, color=LINE, sw=1.8))

    # Крок 4: Простір CIE 1931
    frags.append(rect(560, 200, 250, 100, fill="#e6fcf5", stroke="#0ca678", sw=1.5, rx=6))
    frags.append(text(685, 225, "4. Тристимулус CIE 1931", size=13, color="#0ca678", bold=True))
    frags.append(text(685, 250, "x = X / (X + Y + Z)", size=12, color=INK))
    frags.append(text(685, 272, "y = Y / (X + Y + Z)", size=12, color=INK))

    # Розгалуження на CCT, sRGB та Lux
    frags.append(arrow(560, 250, 480, 250, color=LINE, sw=1.8))

    # Крок 5А: CCT (McCamy)
    frags.append(rect(240, 195, 240, 105, fill="#fff9db", stroke="#f59f00", sw=1.5, rx=6))
    frags.append(text(360, 220, "5А. Колірна температура CCT", size=13, color="#f59f00", bold=True))
    frags.append(text(360, 245, "n = (x - 0.3320)/(0.1858 - y)", size=11, color=INK))
    frags.append(text(360, 268, "CCT = 449n³+3525n²+6823n+5520", size=10, color=INK))
    frags.append(text(360, 288, "Формула МакКамі (McCamy)", size=10, color=MUTED))

    # Крок 5Б: sRGB
    frags.append(rect(40, 330, 360, 105, fill="#ffe3e3", stroke="#e03131", sw=1.5, rx=6))
    frags.append(text(220, 355, "5Б. Перетворення у sRGB (D65)", size=13, color="#e03131", bold=True))
    frags.append(text(220, 380, "[R_lin, G_lin, B_lin]ᵀ = M_srgb · [X, Y, Z]ᵀ", size=11, color=INK))
    frags.append(text(220, 400, "Гамма-корекція (γ ≈ 2.2) + кліпування [0..255]", size=10, color=MUTED))
    frags.append(text(220, 418, "Готовий колір для дисплеїв та UI", size=10, color=MUTED))

    # Крок 5В: Освітленість Lux
    frags.append(rect(440, 330, 360, 105, fill="#ebfbee", stroke="#2b8a3e", sw=1.5, rx=6))
    frags.append(text(620, 355, "5В. Освітленість у Люксах (Lux)", size=13, color="#2b8a3e", bold=True))
    frags.append(text(620, 380, "Lux = 683 · Y  (з координати Y CIE 1931)", size=11, color=INK))
    frags.append(text(620, 400, "або зважена сума c_r·R + c_g·G + c_b·B", size=10, color=MUTED))
    frags.append(text(620, 418, "Фотометричний світловий потік", size=10, color=MUTED))

    # Зв'язок від CIE до 5Б і 5В
    frags.append(arrow(685, 300, 685, 330, color=LINE, sw=1.5))
    frags.append(arrow(580, 290, 320, 330, color=LINE, sw=1.5))

    render(os.path.join(OUT, "pipeline-flow.svg"), w, h, *frags)


def fig_chromaticity_diagram():
    """Фігура 4: Діаграма колірності CIE 1931 (x, y) з локусом Планка та трикутником sRGB."""
    w, h = 800, 520
    frags = []

    # Система координат x, y
    ox, oy, gw, gh = 90, 430, 640, 370

    # Сітка x: 0.0 .. 0.8, y: 0.0 .. 0.9
    for i in range(9):
        vx = i * 0.1
        px = ox + (vx / 0.8) * gw
        frags.append(line(px, oy, px, oy - gh, color="#f0f2f5", sw=1.0))
        frags.append(text(px, oy + 20, "%.1f" % vx, size=11, color=MUTED))

    for i in range(10):
        vy = i * 0.1
        py = oy - (vy / 0.9) * gh
        frags.append(line(ox, py, ox + gw, py, color="#f0f2f5", sw=1.0))
        frags.append(text(ox - 15, py + 4, "%.1f" % vy, size=11, color=MUTED, anchor="end"))

    # Осі
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    frags.append(text(ox + gw / 2, oy + 42, "Координата колірності x", size=13, color=INK, bold=True))
    frags.append(text(ox - 35, oy - gh / 2, "Координата колірності y", size=13, color=INK, bold=True, anchor="middle"))

    # Точки спектрального локусу (приблизні табличні точки CIE 1931 2-deg)
    locus_data = [
        (380, 0.1741, 0.0050), (450, 0.1566, 0.0177), (470, 0.1241, 0.0578),
        (480, 0.0913, 0.1327), (490, 0.0454, 0.2950), (500, 0.0082, 0.5384),
        (510, 0.0139, 0.7502), (520, 0.0743, 0.8338), (530, 0.1547, 0.8059),
        (540, 0.2296, 0.7543), (550, 0.3016, 0.6923), (560, 0.3731, 0.6245),
        (570, 0.4441, 0.5547), (580, 0.5125, 0.4866), (590, 0.5752, 0.4242),
        (600, 0.6270, 0.3725), (620, 0.6915, 0.3083), (650, 0.7260, 0.2740),
        (700, 0.7347, 0.2653)
    ]

    locus_pts = []
    for wl, lx, ly in locus_data:
        px = ox + (lx / 0.8) * gw
        py = oy - (ly / 0.9) * gh
        locus_pts.append((px, py, wl, lx, ly))

    # Полілінія спектрального локусу
    pts_str = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in locus_pts)
    # Замкнути лінією пурпурних тонів (від 700 нм до 380 нм)
    frags.append('<polygon points="%s" fill="#f8f9fa" stroke="#495057" stroke-width="2.0"/>' % pts_str)

    # Підписи ключових довжин хвиль на локусі
    for px, py, wl, lx, ly in locus_pts:
        if wl in [470, 500, 520, 540, 560, 580, 600, 700]:
            frags.append(circle(px, py, 3, fill="#c0392b", stroke="#1a1a1a", sw=1.0))
            # Зсув підпису залежно від положення
            dx = 15 if lx > 0.3 else -25
            dy = -10 if ly > 0.5 else 12
            if wl == 520: dx, dy = 0, -14
            if wl == 700: dx, dy = 15, 10
            frags.append(text(px + dx, py + dy, "%d нм" % wl, size=10, color="#495057", bold=True))

    # Лінія пурпурних тонів (пунктир)
    p_380 = locus_pts[0]
    p_700 = locus_pts[-1]
    frags.append(line(p_380[0], p_380[1], p_700[0], p_700[1], color="#862e9c", sw=1.8, dash="4,4"))
    frags.append(text((p_380[0] + p_700[0]) / 2 - 20, (p_380[1] + p_700[1]) / 2 + 16, "Лінія пурпурних тонів", size=10, color="#862e9c", italic=True))

    # Трикутник колірного охоплення sRGB (R: 0.64, 0.33; G: 0.30, 0.60; B: 0.15, 0.06)
    srgb_r = (ox + (0.64 / 0.8) * gw, oy - (0.33 / 0.9) * gh)
    srgb_g = (ox + (0.30 / 0.8) * gw, oy - (0.60 / 0.9) * gh)
    srgb_b = (ox + (0.15 / 0.8) * gw, oy - (0.06 / 0.9) * gh)

    srgb_poly = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (srgb_r[0], srgb_r[1], srgb_g[0], srgb_g[1], srgb_b[0], srgb_b[1])
    frags.append('<polygon points="%s" fill="#e7f5ff" fill-opacity="0.6" stroke="#1c7ed6" stroke-width="2.0"/>' % srgb_poly)
    frags.append(text(srgb_r[0] + 10, srgb_r[1] + 5, "R (sRGB)", size=11, color="#c0392b", bold=True))
    frags.append(text(srgb_g[0] - 10, srgb_g[1] - 10, "G (sRGB)", size=11, color="#27ae60", bold=True))
    frags.append(text(srgb_b[0] - 15, srgb_b[1] + 15, "B (sRGB)", size=11, color="#2457d6", bold=True))

    # Точка білого D65 (0.3127, 0.3290)
    d65_x, d65_y = ox + (0.3127 / 0.8) * gw, oy - (0.3290 / 0.9) * gh
    frags.append(circle(d65_x, d65_y, 4.5, fill="#ffffff", stroke="#d9480f", sw=2.0))
    frags.append(text(d65_x + 10, d65_y - 8, "D65 (6504 K)", size=11, color="#d9480f", bold=True))

    # Локус абсолютно чорного тіла (Planckian Locus): 2000K, 3000K, 4000K, 6500K, 10000K
    planck_pts = [
        (2000, 0.5267, 0.4133), (2500, 0.4870, 0.4153), (3000, 0.4369, 0.4041),
        (4000, 0.3804, 0.3768), (5000, 0.3451, 0.3516), (6500, 0.3138, 0.3236),
        (10000, 0.2807, 0.2884), (20000, 0.2520, 0.2480)
    ]
    pl_coords = []
    for t_k, px_val, py_val in planck_pts:
        cx_p = ox + (px_val / 0.8) * gw
        cy_p = oy - (py_val / 0.9) * gh
        pl_coords.append((cx_p, cy_p, t_k))

    pl_str = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pl_coords)
    frags.append('<polyline points="%s" fill="none" stroke="#e8590c" stroke-width="2.5"/>' % pl_str)

    # Відмітки колірних температур
    for cx_p, cy_p, t_k in pl_coords:
        if t_k in [2000, 3000, 4000, 10000]:
            frags.append(circle(cx_p, cy_p, 3.0, fill="#e8590c", stroke="#1a1a1a", sw=1.0))
            frags.append(text(cx_p + 8, cy_p + 14, "%dK" % t_k, size=9, color="#e8590c", bold=True))

    # Епіцентр МакКамі (0.3320, 0.1858)
    ep_x = ox + (0.3320 / 0.8) * gw
    ep_y = oy - (0.1858 / 0.9) * gh
    frags.append(circle(ep_x, ep_y, 4.0, fill="#7950f2", stroke="#1a1a1a", sw=1.5))
    frags.append(text(ep_x + 12, ep_y + 4, "Епіцентр МакКамі (x_e, y_e)", size=10, color="#7950f2", bold=True))

    render(os.path.join(OUT, "chromaticity-diagram.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_cie_curves()
    fig_rgbc_stack()
    fig_pipeline_flow()
    fig_chromaticity_diagram()
    print("Всі фігури успішно згенеровано.")
