# -*- coding: utf-8 -*-
import os
import sys
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(OUT_DIR, exist_ok=True)

def path(d, fill="none", color=LINE, sw=1.5, dash=None):
    stroke_dash = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{stroke_dash}/>'

def make_magnetic_sector_geometry():
    """Фігура 1: Подвійно-фокусуючий мас-спектрометр (сектори E та B)."""
    w, h = 860, 500
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Заголовок
    out.append(text(w/2, 30, "Принцип подвійного фокусування у мас-спектрометрії", size=18, bold=True))
    
    # Джерело іонів
    out.append(rect(40, 200, 90, 60, fill="#e8f8f5", stroke="#16a085", sw=2, rx=6))
    out.append(mtext(85, 222, "Джерело\nіонів", size=13, color="#117a65", bold=True))
    
    # Колімаційна щілина S1
    out.append(rect(145, 180, 10, 40, fill="#34495e", stroke="#2c3e50", sw=1, rx=2))
    out.append(rect(145, 240, 10, 40, fill="#34495e", stroke="#2c3e50", sw=1, rx=2))
    out.append(text(150, 170, "Щілина S1", size=11, color=MUTED))
    
    # Електростатичний сектор E (циліндричний конденсатор)
    out.append(path("M 160 230 C 240 230, 290 200, 340 150", color="#2980b9", sw=3))
    out.append(path("M 155 210 C 235 210, 285 180, 330 135", color="#7f8c8d", sw=2, dash="4,4"))
    out.append(path("M 165 250 C 245 250, 295 220, 350 165", color="#7f8c8d", sw=2, dash="4,4"))
    
    # Позначення Е-сектора
    out.append(rect(220, 140, 110, 36, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    out.append(mtext(275, 155, "Електростатичний\nсектор (Е-аналізатор)", size=11, color="#1b4f72", bold=True))
    
    # Проміжна енергетична щілина S2
    out.append(rect(365, 105, 35, 10, fill="#34495e", stroke="#2c3e50", sw=1, rx=2))
    out.append(rect(365, 135, 35, 10, fill="#34495e", stroke="#2c3e50", sw=1, rx=2))
    out.append(text(382, 95, "Щілина S2", size=11, color=MUTED))
    
    # Магнітний сектор B
    out.append(path("M 385 125 C 470 125, 560 160, 630 250", color="#d35400", sw=3))
    out.append(path("M 380 120 C 460 120, 545 150, 610 235", color="#e67e22", sw=1.5, dash="4,4"))
    out.append(path("M 390 130 C 480 130, 575 170, 650 265", color="#e67e22", sw=1.5, dash="4,4"))
    
    # Позначення В-сектора
    out.append(rect(460, 200, 110, 36, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=4))
    out.append(mtext(515, 215, "Магнітний сектор\n(В-аналізатор)", size=11, color="#7e5109", bold=True))
    
    # Детекторна площина та розділення за маса m1, m2
    out.append(line(610, 320, 710, 220, color=LINE, sw=3))
    out.append(text(685, 210, "Фокальна площина", size=12, bold=True))
    
    # Точки фокусування
    out.append(circle(645, 285, 6, fill="#e74c3c", stroke="#922b21", sw=1.5))
    out.append(text(710, 290, "Маса m1 (легша)", size=12, color="#922b21", bold=True, anchor="start"))
    
    out.append(circle(675, 255, 6, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    out.append(text(740, 260, "Маса m2 (важча)", size=12, color="#1b4f72", bold=True, anchor="start"))
    
    # Пояснювальні написи фокусування
    out.append(rect(180, 370, 230, 75, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, rx=6))
    out.append(mtext(295, 388, "Енергетичне фокусування:\nВідбирає іони за швидкістю/енергією\nΔE / E -> мінімум", size=12, color=INK))
    
    out.append(rect(460, 370, 230, 75, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, rx=6))
    out.append(mtext(575, 388, "Кутове фокусування:\nЗбирає пучок з кутовим розбігом\nΔα -> фокальна точка", size=12, color=INK))
    
    # Стрілки зв'язку
    out.append(arrow(295, 365, 275, 220, color="#2980b9"))
    out.append(arrow(575, 365, 550, 260, color="#d35400"))
    
    with open(os.path.join(OUT_DIR, "magnetic-sector-geometry.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n</svg>")

def make_penning_trap_motion():
    """Фігура 2: Структура електродів пастки Пеннінга та моди руху іона."""
    w, h = 860, 520
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Заголовок
    out.append(text(w/2, 30, "Конструкція пастки Пеннінга та моди руху іона", size=18, bold=True))
    
    # Схема електродів (зліва)
    out.append(path("M 80 120 Q 180 160 280 120 L 280 90 Q 180 130 80 90 Z", color="#34495e", sw=1.5))
    out.append(rect(130, 70, 100, 25, fill="#34495e", stroke="#2c3e50", sw=1, rx=3))
    out.append(text(180, 87, "+U0 (Торцевий)", size=11, color=BG, bold=True))
    
    out.append(path("M 80 340 Q 180 300 280 340 L 280 370 Q 180 330 80 370 Z", color="#34495e", sw=1.5))
    out.append(rect(130, 365, 100, 25, fill="#34495e", stroke="#2c3e50", sw=1, rx=3))
    out.append(text(180, 382, "+U0 (Торцевий)", size=11, color=BG, bold=True))
    
    out.append(path("M 60 190 Q 110 230 60 270 L 40 270 Q 90 230 40 190 Z", color="#e74c3c", sw=1.5))
    out.append(path("M 300 190 Q 250 230 300 270 L 320 270 Q 270 230 320 190 Z", color="#e74c3c", sw=1.5))
    out.append(rect(130, 218, 100, 25, fill="#e74c3c", stroke="#c0392b", sw=1, rx=3))
    out.append(text(180, 235, "-U0 (Кільцевий)", size=11, color=BG, bold=True))
    
    # Магнітне поле B0 (аксіальне)
    for bx in [90, 130, 230, 270]:
        out.append(arrow(bx, 420, bx, 50, color="#27ae60", sw=2))
    out.append(text(285, 70, "B0", size=16, color="#27ae60", bold=True))
    
    # Центр пастки та іон
    out.append(circle(180, 230, 7, fill="#f1c40f", stroke="#d4ac0d", sw=2))
    out.append(text(180, 212, "q", size=13, color="#b7950b", bold=True))
    
    # Справа: розкладання трьох мод руху
    out.append(rect(380, 75, 440, 115, fill="#fdfefe", stroke="#a6acaf", sw=1.5, rx=6))
    out.append(text(400, 100, "1. Аксіальні коливання (ωz)", size=14, color="#1b4f72", bold=True, anchor="start"))
    out.append(text(400, 122, "Гармонічні осциляції вздовж магнітного поля B0", size=11, color=MUTED, anchor="start"))
    out.append(line(720, 90, 720, 170, color=LINE, sw=1.5, dash="2,2"))
    path_z = []
    for t in range(0, 81, 2):
        zy = 130 + 35 * math.sin(t * 0.2)
        zx = 680 + t * 1.0
        path_z.append(f"{zx:.1f},{zy:.1f}")
    out.append(f'<polyline points="{" ".join(path_z)}" fill="none" stroke="#2980b9" stroke-width="2"/>')
    out.append(text(400, 168, "ωz = √( q · U0 / (m · d²) ) ~ 100-500 кГц", size=12, color=INK, anchor="start"))
    
    out.append(rect(380, 210, 440, 125, fill="#fdfefe", stroke="#a6acaf", sw=1.5, rx=6))
    out.append(text(400, 233, "2. Модифікований циклотронний рух (ω+)", size=14, color="#922b21", bold=True, anchor="start"))
    out.append(text(400, 255, "Швидкі колові обертання у радіальній площині", size=11, color=MUTED, anchor="start"))
    cx_cyc, cy_cyc = 720, 275
    path_cyc = []
    for deg in range(0, 720, 10):
        rad = math.radians(deg)
        r_c = 28
        px = cx_cyc + r_c * math.cos(rad)
        py = cy_cyc + r_c * math.sin(rad)
        path_cyc.append(f"{px:.1f},{py:.1f}")
    out.append(f'<polyline points="{" ".join(path_cyc)}" fill="none" stroke="#c0392b" stroke-width="2"/>')
    out.append(circle(cx_cyc, cy_cyc, 3, fill=LINE, stroke=LINE, sw=1))
    out.append(text(400, 310, "ω+ ≈ q·B/m - ω- ~ 10-100 МГц (домінує)", size=12, color=INK, anchor="start"))
    
    out.append(rect(380, 355, 440, 125, fill="#fdfefe", stroke="#a6acaf", sw=1.5, rx=6))
    out.append(text(400, 378, "3. Магнетронний дрейф (ω-)", size=14, color="#1e8449", bold=True, anchor="start"))
    out.append(text(400, 400, "Повільний дрейф центру циклотронної орбіти (E × B)", size=11, color=MUTED, anchor="start"))
    cx_mag, cy_mag = 720, 420
    path_mag = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        R_m = 32
        r_c = 6
        px = cx_mag + R_m * math.cos(rad) + r_c * math.cos(rad * 12)
        py = cy_mag + R_m * math.sin(rad) + r_c * math.sin(rad * 12)
        path_mag.append(f"{px:.1f},{py:.1f}")
    out.append(f'<polyline points="{" ".join(path_mag)}" fill="none" stroke="#27ae60" stroke-width="1.8"/>')
    out.append(text(400, 455, "ω- ≈ U0 / (2 · d² · B) ~ 1-10 кГц (незалежна від маси!)", size=12, color=INK, anchor="start"))
    
    out.append(rect(60, 435, 290, 45, fill="#f4f6f8", stroke="#2c3e50", sw=1.5, rx=6))
    out.append(text(205, 462, "Інваріант: ωc² = ω+² + ω-² + ωz²", size=13, bold=True, color="#1a5276"))
    
    with open(os.path.join(OUT_DIR, "penning-trap-motion.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n</svg>")

def make_tof_icr_resonance():
    """Фігура 3: TOF-ICR резонансна крива часу прольоту."""
    w, h = 860, 480
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Заголовок
    out.append(text(w/2, 30, "Резонансна крива TOF-ICR вимірювання маси у пастці Пеннінга", size=18, bold=True))
    
    # Осі координат
    ox, oy = 140, 410
    gw, gh = 660, 260
    
    # Сітка Y (Час прольоту T_TOF, мкс)
    for i, val in enumerate([150, 130, 110, 90, 70]):
        y_pos = oy - (i / 4.0) * gh
        out.append(line(ox, y_pos, ox + gw, y_pos, color="#eaeded", sw=1, dash="4,4"))
        out.append(text(ox - 15, y_pos + 4, f"{val}", size=12, anchor="end"))
    
    # Сітка X (Зсув частоти ν_rf - ν_c, Гц)
    for i, f_off in enumerate([-100, -50, 0, 50, 100]):
        x_pos = ox + (i / 4.0) * gw
        out.append(line(x_pos, oy, x_pos, oy - gh, color="#eaeded", sw=1, dash="4,4"))
        out.append(text(x_pos, oy + 25, f"{f_off:+d}", size=12, anchor="middle"))
    
    # Основні осі
    out.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh - 15, color=LINE, sw=2))
    
    # Підписи осей
    out.append(text(ox + gw / 2, oy + 55, "Зсув ВЧ-частоти збудження (ν_rf - ν_c), Гц", size=14, bold=True))
    out.append(text(25, oy - gh / 2, "Час прольоту T_TOF (мкс)", size=13, bold=True, anchor="start"))
    
    # Побудова кривої точечного профілю TOF-ICR
    pts = []
    for px_step in range(0, 661, 4):
        x_val = (px_step / 660.0) * 240.0 - 120.0 # -120 to +120 Hz
        df = x_val / 25.0
        sinc_val = math.sin(math.pi * df) / (math.pi * df) if abs(df) > 1e-4 else 1.0
        t_tof = 150.0 - 80.0 * (sinc_val ** 2)
        
        px = ox + px_step
        py = oy - ((t_tof - 70.0) / 80.0) * gh
        pts.append((px, py))
    
    # Шлях кривої
    path_str = " ".join([f"{px:.1f},{py:.1f}" for px, py in pts])
    out.append(f'<polyline points="{path_str}" fill="none" stroke="#2980b9" stroke-width="2.5"/>')
    
    # Точка точного резонансу (найнижча точка кривої у y = oy)
    res_x = ox + gw / 2
    res_y = oy - ((70.0 - 70.0) / 80.0) * gh # = oy (410)
    out.append(circle(res_x, res_y, 7, fill="#e74c3c", stroke="#922b21", sw=2))
    
    # Текст-бокс резонансу розміщено у верхній чистій зоні над кривою (y=55..97)
    out.append(rect(res_x + 80, 55, 240, 42, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=4))
    out.append(mtext(res_x + 200, 70, "Точний резонанс ν_rf = ν_c\nМінімальний час прольоту T_min", size=11.5, color="#78281f", bold=True))
    out.append(arrow(res_x + 80, 100, res_x + 15, res_y - 15, color="#e74c3c", sw=1.5))
    
    # Ширина резонансної лінії FWHM
    fwhm_y = oy - ((110.0 - 70.0) / 80.0) * gh
    out.append(line(res_x - 70, fwhm_y, res_x + 70, fwhm_y, color="#d35400", sw=2, dash="4,4"))
    out.append(text(res_x, fwhm_y - 10, "FWHM = 1 / T_ex", size=12, color="#d35400", bold=True, anchor="middle"))
    
    with open(os.path.join(OUT_DIR, "tof-icr-resonance.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n</svg>")

def make_storage_ring_mass_spectrometry():
    """Фігура 4: Накопичувальне кільце (SMS vs IMS)."""
    w, h = 860, 520
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Заголовок
    out.append(text(w/2, 30, "Мас-спектрометрія у накопичувальних кільцях важких іонів", size=18, bold=True))
    
    # Схема накопичувального кільця (y=110, h=190, rx=95)
    out.append(rect(100, 110, 660, 190, fill="#f4f6f8", stroke="#34495e", sw=2.5, rx=95))
    out.append(rect(180, 150, 500, 110, fill=BG, stroke="#34495e", sw=1.5, rx=55))
    
    # Траєкторії іонів різної маси
    out.append('<rect x="105.0" y="115.0" width="650.0" height="180.0" rx="90" fill="none" stroke="#2980b9" stroke-width="2.0" stroke-dasharray="6,4"/>')
    out.append('<rect x="115.0" y="125.0" width="630.0" height="160.0" rx="80" fill="none" stroke="#e74c3c" stroke-width="2.0" stroke-dasharray="6,4"/>')
    
    # Позначення інжекції
    out.append(arrow(40, 205, 100, 205, color="#27ae60", sw=3))
    out.append(text(70, 190, "Пучок іонів", size=12, color="#1e8449", bold=True))
    
    # Система електронного охолодження (Е-cooler) - зверху ліворуч (x=220)
    out.append(rect(190, 60, 200, 36, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    out.append(text(290, 82, "Електронне охолодження", size=12, color="#1b4f72", bold=True))
    
    # Детектор Шотткі (Schottky Pickup) - зверху праворуч (x=470)
    out.append(rect(470, 60, 180, 36, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=4))
    out.append(text(560, 82, "Детектор Шотткі", size=12, color="#7e5109", bold=True))
    
    # TOF фольговий детектор для IMS - знизу кільця (y=310)
    out.append(rect(350, 310, 160, 32, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=4))
    out.append(text(430, 331, "TOF-детектор (IMS)", size=12, color="#117a65", bold=True))
    
    # Порівняльна таблиця внизу
    # Режим SMS
    out.append(rect(60, 360, 350, 135, fill="#fcf3cf", stroke="#f1c40f", sw=1.5, rx=6))
    out.append(text(235, 383, "Schottky Mass Spectrometry (SMS)", size=14, color="#7d6608", bold=True))
    out.append(mtext(235, 408, "• Потребує електронного охолодження (Δv/v -> 10⁻⁷)\n• Вимірювання частоти обертання неруйнівним способом\n• Тривалість вимірювання: t > 1-10 секунд\n• Точність маси: δm/m ~ 10⁻⁶...10⁻⁷", size=11.5, color=INK, anchor="middle"))
    
    # Режим IMS
    out.append(rect(450, 360, 350, 135, fill="#d5f5e3", stroke="#2ecc71", sw=1.5, rx=6))
    out.append(text(625, 383, "Isochronous Mass Spectrometry (IMS)", size=14, color="#196f3d", bold=True))
    out.append(mtext(625, 408, "• Налаштування кільця у режим γ = γ_t (ізохронізм)\n• Період обертання не залежить від розкиду швидкостей\n• Рекордний час вимірювання: t_1/2 > 10-50 мкс!\n• Ідеально для ультракороткоживучих нуклідів", size=11.5, color=INK, anchor="middle"))
    
    with open(os.path.join(OUT_DIR, "storage-ring-mass-spectrometry.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n</svg>")

if __name__ == "__main__":
    make_magnetic_sector_geometry()
    make_penning_trap_motion()
    make_tof_icr_resonance()
    make_storage_ring_mass_spectrometry()
    print("Figures generated successfully in img/")
