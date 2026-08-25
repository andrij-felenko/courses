# -*- coding: utf-8 -*-
"""Фігури до теми «Спрямованість антени».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Кольори
WAVE = "#c0392b"      # промінь / напрямок випромінювання
WAVE2 = "#2457d6"     # сферична хвиля / ізотропний випромінювач
ACCENT = "#8e44ad"    # математичні параметри
GOOD = FIELD          # підсилення / фокусування
BORDER = INK

# ── 1. Ізотропний випромінювач проти спрямованої антени ───────────────────────
def fig_isotropic_vs_directional():
    W, H = 760, 360
    f = [text(W / 2, 26, "Концентрація енергії: ізотропне випромінювання проти спрямованого", size=15, bold=True)]

    # Ліва панель: Ізотропний випромінювач
    cxL, cyL = 190, 185
    f.append(rect(20, 50, 340, 280, fill="#fbfdff", stroke=MUTED, sw=1, rx=8))
    f.append(text(cxL, 74, "Ізотропний випромінювач (D = 1 = 0 dBi)", size=13, bold=True, color=WAVE2))

    # Сферичні хвилі (концентричні кола)
    for r in (30, 55, 80, 105):
        f.append(circle(cxL, cyL, r, fill="none", stroke=WAVE2, sw=1.4))
    
    # Радіальні однакові стрілки
    for angle in (0, 45, 90, 135, 180, 225, 270, 315):
        rad = math.radians(angle)
        x1 = cxL + 12 * math.cos(rad)
        y1 = cyL + 12 * math.sin(rad)
        x2 = cxL + 115 * math.cos(rad)
        y2 = cyL + 115 * math.sin(rad)
        f.append(arrow(x1, y1, x2, y2, color=WAVE2, sw=1.8))

    f.append(circle(cxL, cyL, 6, fill=INK, stroke=INK, sw=1))
    f.append(mtext(cxL, 290, "Енергія P_rad розсіюється\nрівномірно по всій сфері 4π стер", size=11, color=INK, lh=1.25))

    # Права панель: Спрямована антена
    cxR, cyR = 570, 185
    f.append(rect(400, 50, 340, 280, fill="#fbfdff", stroke=MUTED, sw=1, rx=8))
    f.append(text(cxR, 74, "Спрямована антена (D ≫ 1)", size=13, bold=True, color=WAVE))

    # Малювання пелюстків спрямованості (полярна крива)
    pts = []
    for deg in range(0, 361, 3):
        rad = math.radians(deg)
        # Формула пелюстка: cos^4(θ) для головного пелюстка при deg біля 0, і дрібні бокові
        if abs(deg) <= 60 or deg >= 300:
            a = deg if deg <= 60 else deg - 360
            r = 135 * (math.cos(math.radians(a * 1.4))) ** 4 + 8
        elif 120 <= deg <= 240:
            # Задній пелюсток
            a = deg - 180
            r = 25 * (math.cos(math.radians(a * 1.5))) ** 2 + 5
        else:
            # Бокові пелюстки
            r = 18 * abs(math.sin(rad * 3)) + 5
        
        x = cxR + r * math.cos(rad)
        y = cyR - r * math.sin(rad)
        pts.append("%.1f,%.1f" % (x, y))

    f.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2"/>' % (" ".join(pts), WAVE))

    # Головна стрілка U_max
    f.append(arrow(cxR, cyR, cxR + 140, cyR, color=WAVE, sw=2.8))
    f.append(text(cxR + 90, cyR - 12, "U_max ≫ U_avg", size=12, bold=True, color=WAVE, anchor="start"))
    f.append(circle(cxR, cyR, 6, fill=INK, stroke=INK, sw=1))

    f.append(mtext(cxR, 290, "Енергія стиснута у вузький промінь:\nвисока інтенсивність у напрямку максимуму", size=11, color=INK, lh=1.25))

    render(os.path.join(IMG, "isotropic-vs-directional.svg"), W, H, *f)


# ── 2. Інтенсивність випромінювання та тілесний кут ──────────────────────────
def fig_radiation_intensity():
    W, H = 760, 360
    f = [text(W / 2, 26, "Визначення спрямованості: інтенсивність U(θ, ϕ) та тілесний кут Ω_A", size=15, bold=True)]

    # Лівий блок: Сферична система та елемент тілесного кута
    ox, oy = 200, 200
    f.append(rect(20, 50, 350, 280, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(ox, 74, "Елемент сфери dΩ = sin(θ) dθ dϕ", size=13, bold=True, color=INK))

    # Осі
    f.append(arrow(ox, oy, ox, oy - 120, color=INK, sw=1.5)) # Z
    f.append(text(ox + 10, oy - 110, "Z (θ=0°)", size=11, color=INK, bold=True, anchor="start"))
    f.append(arrow(ox, oy, ox + 120, oy + 40, color=INK, sw=1.5)) # X
    f.append(text(ox + 125, oy + 42, "X", size=11, color=INK, bold=True, anchor="start"))
    f.append(arrow(ox, oy, ox - 100, oy + 50, color=INK, sw=1.5)) # Y
    f.append(text(ox - 108, oy + 52, "Y", size=11, color=INK, bold=True, anchor="end"))

    # Вектор випромінювання U(θ, ϕ)
    vx, vy = ox + 85, oy - 75
    f.append(line(ox, oy, vx, vy, color=WAVE, sw=2.5))
    f.append(circle(vx, vy, 4, fill=WAVE, stroke=WAVE, sw=0))
    f.append(text(vx + 10, vy - 6, "U(θ, ϕ) [Вт/ст]", size=12, color=WAVE, bold=True, anchor="start"))

    # Дуга кута θ
    f.append('<path d="M %d,%d A 45 45 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' %
             (ox, oy - 45, ox + 28, oy - 25, ACCENT))
    f.append(text(ox + 20, oy - 48, "θ", size=12, color=ACCENT, bold=True))

    f.append(mtext(ox, 292, "Спрямованість описує розподіл\nпотужності P_rad по сферичних кутах", size=11, color=MUTED, lh=1.25))

    # Правий блок: Еквівалентний конус променя Ω_A
    cx, cy = 570, 200
    f.append(rect(390, 50, 350, 280, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(cx, 74, "Тілесний кут променя Ω_A", size=13, bold=True, color=ACCENT))

    # Конус Ω_A
    cone_pts = ["%.1f,%.1f" % (cx, cy), "%.1f,%.1f" % (cx + 110, cy - 50), "%.1f,%.1f" % (cx + 110, cy + 50)]
    f.append('<polygon points="%s" fill="#f4eeef" stroke="%s" stroke-width="1.8"/>' % (" ".join(cone_pts), ACCENT))
    f.append('<ellipse cx="%d" cy="%d" rx="15" ry="50" fill="#e8daef" stroke="%s" stroke-width="1.8"/>' % (cx + 110, cy, ACCENT))

    f.append(arrow(cx, cy, cx + 135, cy, color=WAVE, sw=2.5))
    f.append(text(cx + 60, cy - 10, "U_max", size=12, color=WAVE, bold=True))
    f.append(text(cx + 45, cy + 25, "Ω_A", size=14, color=ACCENT, bold=True))

    # Формульне пояснення через fitbox
    f.append(fitbox(410, 255, 310, 60,
                    "Формула спрямованості:\nD = 4π · U_max / P_rad = 4π / Ω_A\n\nЧим менший кут Ω_A, тим більша спрямованість D",
                    size=11, fill="#fdfefe", stroke=ACCENT))

    render(os.path.join(IMG, "radiation-intensity.svg"), W, H, *f)


# ── 3. Параметри діаграми спрямованості ───────────────────────────────────────
def fig_hpbw_beamwidth():
    W, H = 760, 360
    f = [text(W / 2, 26, "Параметри діаграми: ширина променя HPBW, бокові пелюстки та F/B", size=15, bold=True)]

    cx, cy = 340, 210
    
    # Головний пелюсток (вертикально вгору) і бокові пелюстки
    # Побудова пелюстків під кутом відносно вертикалі
    pts = []
    for deg in range(0, 361, 2):
        # θ відраховується від верхньої осі (0° = вгору)
        rad = math.radians(deg)
        # Головний пелюсток біля 0° (ширина ~30-40°)
        norm_deg = (deg + 180) % 360 - 180 # -180..180
        abs_deg = abs(norm_deg)
        
        if abs_deg <= 45:
            r = 140 * (math.cos(math.radians(abs_deg * 2.0))) ** 2 + 6
        elif 135 <= abs_deg <= 180:
            # Задній пелюсток
            a = 180 - abs_deg
            r = 35 * (math.cos(math.radians(a * 2.2))) ** 2 + 5
        else:
            # Бокові пелюстки
            r = 24 * abs(math.sin(rad * 4)) + 6
            
        # x = cx + r*sin(θ), y = cy - r*cos(θ)
        x = cx + r * math.sin(rad)
        y = cy - r * math.cos(rad)
        pts.append("%.1f,%.1f" % (x, y))

    f.append('<polygon points="%s" fill="#eaf2ff" stroke="%s" stroke-width="2"/>' % (" ".join(pts), WAVE2))

    # Рівень −3 дБ (70.7% радіуса максимуму = 0.707 * 146 = 103)
    r3db = 103
    ang3db = 22.5 # deg
    x_left = cx - r3db * math.sin(math.radians(ang3db))
    y_left = cy - r3db * math.cos(math.radians(ang3db))
    x_right = cx + r3db * math.sin(math.radians(ang3db))
    y_right = cy - r3db * math.cos(math.radians(ang3db))

    # Штрихова лінія рівня -3 дБ
    f.append(line(cx - 120, y_left, cx + 120, y_right, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(cx + 128, y_left + 4, "−3 дБ (0.5 P_max)", size=10.5, color=MUTED, anchor="start"))

    # Дуга HPBW
    f.append(line(x_left, y_left, x_right, y_right, color=WAVE, sw=2))
    f.append(circle(x_left, y_left, 4, fill=WAVE, stroke=WAVE, sw=0))
    f.append(circle(x_right, y_right, 4, fill=WAVE, stroke=WAVE, sw=0))
    f.append(text(cx, y_left - 10, "HPBW (θ_3dB)", size=12, bold=True, color=WAVE))

    # Позначка головного випромінювання
    f.append(arrow(cx, cy, cx, cy - 150, color=WAVE2, sw=2))
    f.append(text(cx + 10, cy - 138, "0° (Головна вісь)", size=11, color=WAVE2, bold=True, anchor="start"))

    # Позначка бокових пелюстків (SLL)
    f.append(arrow(cx + 70, cy + 30, cx + 38, cy - 10, color=ACCENT, sw=1.5))
    f.append(text(cx + 75, cy + 42, "Бокові пелюстки (SLL)", size=10.5, color=ACCENT, bold=True, anchor="start"))

    # Позначка заднього пелюстка (F/B)
    f.append(arrow(cx - 110, cy + 50, cx - 15, cy + 30, color=POS, sw=1.5))
    f.append(text(cx - 240, cy + 54, "Задній пелюсток (F/B ratio)", size=11, color=POS, bold=True, anchor="start"))

    # Картка висновку праворуч
    f.append(fitbox(530, 75, 210, 240,
                    "Ключові метрики:\n\n1. HPBW (θ_3dB):\nКут між точками −3 дБ.\nЧим вужчий HPBW, тим вища спрямованість.\n\n2. SLL (Side Lobe Level):\nПридушення побічних пелюстків (типово −13…−25 дБ).\n\n3. F/B Ratio:\nСпіввідношення випромінювання вперед/назад.",
                    size=10.5, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "hpbw-beamwidth.svg"), W, H, *f)


# ── 4. Зв'язок спрямованості з апертурою та довжиною хвилі ───────────────────
def fig_aperture_directivity():
    W, H = 760, 360
    f = [text(W / 2, 26, "Апертурні антени: спрямованість D відносно площі A_e та частоти", size=15, bold=True)]

    # Ліва панель: Рупор / Дзеркало з апертурою
    f.append(rect(20, 50, 360, 280, fill="#fbfdff", stroke=MUTED, sw=1, rx=8))
    f.append(text(200, 74, "Ефективна апертура A_e = η_a · A_phys", size=13, bold=True, color=INK))

    # Схема рупорної антени
    horn_pts = ["60,180", "150,130", "150,230"]
    f.append('<polygon points="%s" fill="#e9edf2" stroke="%s" stroke-width="2"/>' % (" ".join(horn_pts), INK))
    f.append(line(30, 180, 60, 180, color=INK, sw=4)) # фланцева лінія живлення

    # Площина апертури A_phys
    f.append('<ellipse cx="150" cy="180" rx="14" ry="50" fill="#d5dbdb" stroke="%s" stroke-width="2"/>' % INK)
    f.append(line(150, 130, 150, 230, color=ACCENT, sw=2, dash="3,3"))
    f.append(text(150, 248, "Фізична апертура A_phys", size=11, color=INK, bold=True))

    # Хвильовий промінь з апертури
    f.append(arrow(150, 180, 340, 180, color=WAVE, sw=3))
    f.append(text(250, 168, "Вузький промінь", size=11, color=WAVE, bold=True))

    # Формула залежності
    f.append(fitbox(40, 260, 320, 55,
                    "Фундаментальне співвідношення:\nD = (4π / λ²) · A_e = (4π / λ²) · η_a · A_phys",
                    size=11.5, fill="#fdfefe", stroke=WAVE, bold=True))

    # Права панель: Розрахункова таблиця-порівняння для тарілки A_phys = 1 м²
    f.append(rect(400, 50, 340, 280, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(570, 74, "Вплив частоти (при дзеркалі D = 1.13 м)", size=12.5, bold=True, color=GOOD))

    headers = ["Частота f", "Довжина λ", "Спрямованість D", "dBi"]
    cols_x = [420, 500, 600, 680]
    y_start = 105

    # Заголовок таблиці
    f.append(rect(410, y_start, 320, 26, fill="#eaeeea", stroke=GOOD, sw=1))
    for x, h in zip(cols_x, headers):
        f.append(text(x + 20, y_start + 17, h, size=10, bold=True, color=GOOD))

    rows_data = [
        ("2.4 ГГц", "12.5 см", "316", "25.0 dBi"),
        ("5.8 ГГц", "5.17 см", "1860", "32.7 dBi"),
        ("10.0 ГГц", "3.00 см", "5480", "37.4 dBi"),
        ("24.0 ГГц", "1.25 см", "31500", "45.0 dBi"),
    ]

    y_cur = y_start + 26
    for f_str, l_str, d_str, dbi_str in rows_data:
        f.append(rect(410, y_cur, 320, 30, fill="#ffffff", stroke=MUTED, sw=0.8))
        f.append(text(cols_x[0] + 20, y_cur + 19, f_str, size=10.5, color=INK))
        f.append(text(cols_x[1] + 20, y_cur + 19, l_str, size=10.5, color=MUTED))
        f.append(text(cols_x[2] + 20, y_cur + 19, d_str, size=10.5, color=WAVE, bold=True))
        f.append(text(cols_x[3] + 20, y_cur + 19, dbi_str, size=10.5, color=GOOD, bold=True))
        y_cur += 30

    f.append(mtext(570, 292, "При однаковому розмірі антени:\nпідвищення частоти вдвічі дає +6 дБ спрямованості!", size=10.5, color=INK, lh=1.25))

    render(os.path.join(IMG, "aperture-directivity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_isotropic_vs_directional()
    fig_radiation_intensity()
    fig_hpbw_beamwidth()
    fig_aperture_directivity()
    print("OK: 4 figures created ->", IMG)
