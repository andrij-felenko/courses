# -*- coding: utf-8 -*-
"""Фігури до теми «Антена Яґі-Уда».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальна палітра кольорів
COLOR_BOOM = "#4a5568"       # Траверса (бум)
COLOR_REFLECTOR = "#2b6cb0"  # Рефлектор
COLOR_DRIVEN = "#c53030"     # Активний диполь
COLOR_DIRECTOR = "#2f855a"   # Директори
COLOR_WAVE = "#dd6b20"       # Напрямок випромінювання / хвиля
COLOR_ACCENT = "#ebf8ff"     # Тло підкреслених текстових блоків

def path(d, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ── 1. Конструкція та геометричні елементи антени Яґі-Уда ─────────────────────
def fig_yagi_structure():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 26, "Конструкція та геометричні елементи антени Яґі-Уда", size=16, bold=True))

    boom_y = 220
    boom_x1, boom_x2 = 60, 720

    # Металева траверса (бум)
    f.append(rect(boom_x1, boom_y - 6, boom_x2 - boom_x1, 12, fill=COLOR_BOOM, stroke=INK, sw=1.2, rx=3))
    tb_boom, _, _ = textbox(W / 2, boom_y + 34, "Несуча траверса (бум / boom)", size=11, pad=4, fill=FILL, stroke=LINE, color=COLOR_BOOM, bold=True)
    f.append(tb_boom)

    # Елементи антени (координати X)
    ref_x = 110
    drv_x = 240
    dir1_x = 380
    dir2_x = 520
    dir3_x = 650

    # 1. Рефлектор (найдовший)
    ref_h = 280
    f.append(line(ref_x, boom_y - ref_h / 2, ref_x, boom_y + ref_h / 2, color=COLOR_REFLECTOR, sw=5.0))
    tb_ref, _, _ = textbox(ref_x, boom_y - ref_h / 2 - 24, "Рефлектор (Reflector)\nL_R ≈ 0.48·λ", size=11, pad=4, fill=COLOR_ACCENT, stroke=COLOR_REFLECTOR, color=COLOR_REFLECTOR, bold=True)
    f.append(tb_ref)

    # 2. Активний диполь (з вузлом живлення)
    drv_h = 240
    f.append(line(drv_x, boom_y - drv_h / 2, drv_x, boom_y - 12, color=COLOR_DRIVEN, sw=5.0))
    f.append(line(drv_x, boom_y + 12, drv_x, boom_y + drv_h / 2, color=COLOR_DRIVEN, sw=5.0))
    # Вузол живлення (точка підключення кабелю)
    f.append(circle(drv_x, boom_y - 12, 4, fill=COLOR_DRIVEN, stroke=INK))
    f.append(circle(drv_x, boom_y + 12, 4, fill=COLOR_DRIVEN, stroke=INK))
    f.append(line(drv_x, boom_y - 12, drv_x - 30, boom_y - 12, color=INK, sw=1.5))
    f.append(line(drv_x, boom_y + 12, drv_x - 30, boom_y + 12, color=INK, sw=1.5))
    tb_drv, _, _ = textbox(drv_x + 10, boom_y - drv_h / 2 - 24, "Активний випромінювач\nL_D ≈ 0.45·λ (клемна коробка)", size=11, pad=4, fill="#fff5f5", stroke=COLOR_DRIVEN, color=COLOR_DRIVEN, bold=True)
    f.append(tb_drv)

    # 3. Директори (послідовно коротші)
    dirs = [
        (dir1_x, 220, "Директор 1\nL_D1 ≈ 0.42·λ"),
        (dir2_x, 204, "Директор 2\nL_D2 ≈ 0.41·λ"),
        (dir3_x, 190, "Директор 3\nL_D3 ≈ 0.40·λ"),
    ]
    for dx, dh, dlbl in dirs:
        f.append(line(dx, boom_y - dh / 2, dx, boom_y + dh / 2, color=COLOR_DIRECTOR, sw=5.0))
        tb_d, _, _ = textbox(dx, boom_y - dh / 2 - 24, dlbl, size=10, pad=3, fill="#f0fff4", stroke=COLOR_DIRECTOR, color=COLOR_DIRECTOR, bold=True)
        f.append(tb_d)

    # Розміри та відстані (курсори / стрілки)
    # Відстань S_R
    dim_y1 = boom_y + 110
    f.append(arrow(drv_x, dim_y1, ref_x, dim_y1, color=MUTED, sw=1.2))
    f.append(arrow(ref_x, dim_y1, drv_x, dim_y1, color=MUTED, sw=1.2))
    f.append(text((ref_x + drv_x) / 2, dim_y1 - 8, "S_R ≈ 0.15–0.25·λ", size=10, color=MUTED, bold=True))

    # Відстань S_D
    dim_y2 = boom_y + 110
    f.append(arrow(drv_x, dim_y2, dir1_x, dim_y2, color=MUTED, sw=1.2))
    f.append(arrow(dir1_x, dim_y2, drv_x, dim_y2, color=MUTED, sw=1.2))
    f.append(text((drv_x + dir1_x) / 2, dim_y2 - 8, "S_D1 ≈ 0.15–0.35·λ", size=10, color=MUTED, bold=True))

    # Вектор головного випромінювання (стрілка напрямку)
    f.append(arrow(100, 55, 700, 55, color=COLOR_WAVE, sw=3.5))
    tb_main, _, _ = textbox(W / 2, 55, "Напрямок максимального випромінювання (Головний промінь)", size=12, pad=6, fill="#fffaf0", stroke=COLOR_WAVE, color=COLOR_WAVE, bold=True)
    f.append(tb_main)

    render(os.path.join(IMG, "yagi-structure.svg"), W, H, *f)


# ── 2. Фізичний механізм пасивного випромінювання: фазовий зсув струму ───────
def fig_parasitic_phase():
    W, H = 780, 440
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 24, "Фізичний механізм пасивного випромінювання та формування хвилі", size=16, bold=True))

    cy = 210

    # 1. Ліва частина: Рефлектор (L > λ/2)
    f.append(rect(30, 60, 340, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(200, 85, "РЕФЛЕКТОР (L_R > λ/2)", size=14, color=COLOR_REFLECTOR, bold=True))

    # Схема активний -> рефлектор
    f.append(line(120, cy - 80, 120, cy + 80, color=COLOR_DRIVEN, sw=4.0))
    f.append(text(120, cy + 100, "Активний диполь", size=11, color=COLOR_DRIVEN, bold=True))

    f.append(line(280, cy - 100, 280, cy + 100, color=COLOR_REFLECTOR, sw=4.0))
    f.append(text(280, cy + 120, "Рефлектор", size=11, color=COLOR_REFLECTOR, bold=True))

    # Хвиля від активного до рефлектора (падаюча)
    f.append(arrow(130, cy - 30, 270, cy - 30, color=COLOR_WAVE, sw=1.8))
    f.append(text(200, cy - 42, "Падаюче поле E₀", size=10, color=COLOR_WAVE))

    # Фазові складові
    t1_text = "• Реактивність: Індуктивна (X > 0)\n• Зсув струму: Відстає по фазі\n• Просторова затримка: β·d ≈ 70°\n• Сумарна фаза ззаду: ≈ 180°\n  → Протифаза (гасіння назад!)\n• Сумарна фаза попереду: ≈ 0°\n  → Синфазність (підсилення вперед!)"
    tb_t1, _, _ = textbox(200, cy + 30, t1_text, size=10, pad=6, fill=COLOR_ACCENT, stroke=COLOR_REFLECTOR, color=INK)
    f.append(tb_t1)

    # 2. Права частина: Директор (L < λ/2)
    f.append(rect(410, 60, 340, 350, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(580, 85, "ДИРЕКТОР (L_D < λ/2)", size=14, color=COLOR_DIRECTOR, bold=True))

    f.append(line(480, cy - 80, 480, cy + 80, color=COLOR_DRIVEN, sw=4.0))
    f.append(text(480, cy + 100, "Активний диполь", size=11, color=COLOR_DRIVEN, bold=True))

    f.append(line(640, cy - 65, 640, cy + 65, color=COLOR_DIRECTOR, sw=4.0))
    f.append(text(640, cy + 120, "Директор", size=11, color=COLOR_DIRECTOR, bold=True))

    # Хвиля від активного до директора
    f.append(arrow(490, cy - 30, 630, cy - 30, color=COLOR_WAVE, sw=1.8))
    f.append(text(560, cy - 42, "Падаюче поле E₀", size=10, color=COLOR_WAVE))

    t2_text = "• Реактивність: Ємнісна (X < 0)\n• Зсув струму: Випереджає по фазі\n• Промені вільної хвилі наздоганяють\n  перевипромінене поле директора\n• Формується сповільнена хвиля\n  уздовж директорного ряду\n• Ефект лінзи: Концентрація\n  променя в напрямку директора"
    tb_t2, _, _ = textbox(580, cy + 30, t2_text, size=10, pad=6, fill="#f0fff4", stroke=COLOR_DIRECTOR, color=INK)
    f.append(tb_t2)

    render(os.path.join(IMG, "parasitic-phase.svg"), W, H, *f)


# ── 3. Діаграма спрямованості антени Яґі-Уда ─────────────────────────────────
def fig_yagi_radiation_pattern():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 24, "Діаграма спрямованості: порівняння диполя, 3 та 8-елементної Яґі-Уда", size=16, bold=True))

    cx, cy = 390, 230

    # Полярна сітка (концентричні кола)
    for r in [50, 100, 150]:
        f.append(circle(cx, cy, r, fill="none", stroke=MUTED, sw=0.8))
    f.append(line(cx - 170, cy, cx + 330, cy, color=MUTED, sw=1.0))
    f.append(line(cx, cy - 170, cx, cy + 170, color=MUTED, sw=1.0))

    # 1. Подиночний диполь (вісімка)
    dipole_pts = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        r_val = 50 * abs(math.cos(rad))
        px = cx + r_val * math.cos(rad)
        py = cy - r_val * math.sin(rad)
        dipole_pts.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polygon points="{" ".join(dipole_pts)}" fill="none" stroke="{COLOR_BOOM}" stroke-width="1.8" stroke-dasharray="4,3"/>')

    # 2. 3-елементна Яґі
    yagi3_pts = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        if abs(deg) <= 90 or deg >= 270:
            r_val = 110 * (0.3 + 0.7 * math.cos(rad)**2)
        else:
            r_val = 30 * (0.2 + 0.8 * abs(math.cos(rad)))
        px = cx + r_val * math.cos(rad)
        py = cy - r_val * math.sin(rad)
        yagi3_pts.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polygon points="{" ".join(yagi3_pts)}" fill="none" stroke="{COLOR_REFLECTOR}" stroke-width="2.2"/>')

    # 3. 8-елементна Яґі
    yagi8_pts = []
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        cos_val = math.cos(rad)
        if cos_val > 0:
            r_val = 160 * (max(0, math.cos(rad * 3.5))**3 if abs(deg) < 25 or deg > 335 else 0.15 * abs(math.sin(rad * 6)))
            r_val = max(r_val, 15 * max(0, math.cos(rad)))
        else:
            r_val = 22 * (0.3 + 0.7 * abs(math.cos(rad))**4)
        px = cx + r_val * math.cos(rad)
        py = cy - r_val * math.sin(rad)
        yagi8_pts.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polygon points="{" ".join(yagi8_pts)}" fill="rgba(221,107,32,0.15)" stroke="{COLOR_WAVE}" stroke-width="2.8"/>')

    # Легенда
    tb_leg1, _, _ = textbox(110, 80, "Одиночний диполь (G ≈ 2.15 dBi)", size=10, pad=4, fill=FILL, stroke=COLOR_BOOM, color=COLOR_BOOM)
    tb_leg2, _, _ = textbox(110, 115, "3-елементна Яґі (G ≈ 8.5 dBi)", size=10, pad=4, fill=COLOR_ACCENT, stroke=COLOR_REFLECTOR, color=COLOR_REFLECTOR, bold=True)
    tb_leg3, _, _ = textbox(110, 150, "8-елементна Яґі (G ≈ 13.5 dBi)", size=10, pad=4, fill="#fffaf0", stroke=COLOR_WAVE, color=COLOR_WAVE, bold=True)
    f.append(tb_leg1)
    f.append(tb_leg2)
    f.append(tb_leg3)

    # Підписи пелюстків
    f.append(arrow(cx + 175, cy, cx + 270, cy, color=COLOR_WAVE, sw=2.0))
    f.append(text(cx + 225, cy - 12, "Головний промінь (Main Lobe)", size=11, color=COLOR_WAVE, bold=True, anchor="middle"))

    f.append(arrow(cx - 30, cy, cx - 110, cy, color=COLOR_REFLECTOR, sw=1.5))
    f.append(text(cx - 70, cy - 12, "Заднє випромінювання (Back Lobe)", size=10, color=COLOR_REFLECTOR, anchor="middle"))

    # Пояснення F/B
    tb_fb, _, _ = textbox(W / 2, 385, "Відношення вперед/назад (Front-to-Back Ratio, F/B) = 20·log₁₀(E_forward / E_backward) ≈ 18–25 дБ",
                          size=11, pad=6, fill=FILL, stroke=LINE, color=INK, bold=True)
    f.append(tb_fb)

    render(os.path.join(IMG, "yagi-radiation-pattern.svg"), W, H, *f)


# ── 4. Схеми узгодження опору антени Яґі-Уда ──────────────────────────────────
def fig_yagi_matching_circuits():
    W, H = 780, 440
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 24, "Конструктивні рішення живлення та узгодження опору Яґі-Уда", size=16, bold=True))

    block_w = 230
    b1_x = 140
    b2_x = 390
    b3_x = 640
    top_y = 65

    # Блок 1: Розрізний диполь + Балун 4:1
    f.append(rect(b1_x - block_w / 2, top_y, block_w, 340, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(b1_x, top_y + 24, "Розрізний диполь + Балун", size=13, color=COLOR_DRIVEN, bold=True))

    f.append(line(b1_x, top_y + 60, b1_x, top_y + 130, color=COLOR_DRIVEN, sw=4.0))
    f.append(line(b1_x, top_y + 150, b1_x, top_y + 220, color=COLOR_DRIVEN, sw=4.0))
    f.append(circle(b1_x, top_y + 130, 4, fill=COLOR_DRIVEN))
    f.append(circle(b1_x, top_y + 150, 4, fill=COLOR_DRIVEN))

    f.append(path(f"M {b1_x} {top_y+130} C {b1_x-40} {top_y+130}, {b1_x-40} {top_y+190}, {b1_x} {top_y+150}", stroke=COLOR_REFLECTOR, sw=2.0))

    t1_txt = "• Низький опір: R_in ≈ 15–25 Ом\n• Потребує симетрування\n• Балун 4:1 (петля λ/2) трансформує\n  25 Ом → 100 Ом або 75 Ом\n• Узгодження з коаксіалом"
    tb_t1, _, _ = textbox(b1_x, top_y + 280, t1_txt, size=10, pad=5, fill="#fff5f5", stroke=COLOR_DRIVEN, color=INK)
    f.append(tb_t1)

    # Блок 2: Петльовий диполь (Folded Dipole)
    f.append(rect(b2_x - block_w / 2, top_y, block_w, 340, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(b2_x, top_y + 24, "Петльовий диполь (Folded)", size=13, color=COLOR_REFLECTOR, bold=True))

    p_path = f"M {b2_x-15} {top_y+135} L {b2_x-15} {top_y+60} A 15 15 0 0 1 {b2_x+15} {top_y+60} L {b2_x+15} {top_y+220} A 15 15 0 0 1 {b2_x-15} {top_y+220} L {b2_x-15} {top_y+145}"
    f.append(path(p_path, stroke=COLOR_REFLECTOR, sw=3.5))
    f.append(circle(b2_x - 15, top_y + 135, 4, fill=COLOR_REFLECTOR))
    f.append(circle(b2_x - 15, top_y + 145, 4, fill=COLOR_REFLECTOR))

    t2_txt = "• Трансформація опору: × 4\n• Власний R_in ≈ 4 · (18 Ом) = 72 Ом\n• Ідеально збігається з 75 Ом!\n• Розширене значення смуги частот\n• Найпопулярніше рішення"
    tb_t2, _, _ = textbox(b2_x, top_y + 280, t2_txt, size=10, pad=5, fill=COLOR_ACCENT, stroke=COLOR_REFLECTOR, color=INK)
    f.append(tb_t2)

    # Блок 3: Гамма-узгодження (Gamma Match)
    f.append(rect(b3_x - block_w / 2, top_y, block_w, 340, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(b3_x, top_y + 24, "Гамма-узгодження", size=13, color=COLOR_DIRECTOR, bold=True))

    f.append(line(b3_x, top_y + 60, b3_x, top_y + 220, color=COLOR_DIRECTOR, sw=4.0))
    f.append(line(b3_x - 30, top_y + 140, b3_x + 30, top_y + 140, color=COLOR_BOOM, sw=5.0))
    f.append(line(b3_x + 18, top_y + 140, b3_x + 18, top_y + 190, color=COLOR_WAVE, sw=2.5))
    f.append(line(b3_x, top_y + 190, b3_x + 18, top_y + 190, color=INK, sw=2.0))
    f.append(circle(b3_x + 18, top_y + 140, 5, fill=BG, stroke=COLOR_WAVE, sw=2.0))

    t3_txt = "• Нерозрізний цілісний диполь\n• Заземлений безпосередньо на бум\n• Регульована хомутом індуктивність\n• Серійний конденсатор компенсації\n• Живлення несиметричним кабелем"
    tb_t3, _, _ = textbox(b3_x, top_y + 280, t3_txt, size=10, pad=5, fill="#f0fff4", stroke=COLOR_DIRECTOR, color=INK)
    f.append(tb_t3)

    render(os.path.join(IMG, "yagi-matching-circuits.svg"), W, H, *f)


if __name__ == "__main__":
    fig_yagi_structure()
    fig_parasitic_phase()
    fig_yagi_radiation_pattern()
    fig_yagi_matching_circuits()
    print("Всі SVG фігури успішно згенеровано у ./img/")
