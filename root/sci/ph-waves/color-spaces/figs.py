# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_fig1():
    """Taxonomy of Color Spaces."""
    w, h = 820, 430
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Title
    out.append(text(w/2, 25, "Ієрархія та класифікація колірних просторів", size=16, bold=True))
    
    # Root: LMS Cone Fundamentals
    tb_lms, w_lms, _ = textbox(160, 90, "Фізіологічний простір LMS\n(Рецептори сітківки L, M, S)", size=12, fill="#eef2ff", stroke="#3b82f6", pad=8)
    out.append(tb_lms)
    
    # CIE XYZ Standard
    tb_xyz, w_xyz, _ = textbox(520, 90, "Стандартний спостерігач CIE XYZ 1931\n(Апаратно-незалежний метамерний базис)", size=12, fill="#eef2ff", stroke="#3b82f6", pad=8)
    out.append(tb_xyz)
    
    x1_arrow = 160 + w_lms/2 + 2
    x2_arrow = 520 - w_xyz/2 - 2
    out.append(arrow(x1_arrow, 90, x2_arrow, 90, color="#3b82f6"))
    out.append(text((x1_arrow + x2_arrow)/2, 75, "Лінійна трансформація", size=10, color=MUTED, anchor="middle"))
    
    # Branch 1: Device-dependent RGB & CMYK
    tb_rgb, _, _ = textbox(220, 230, "Апаратно-залежні простори\n• RGB (sRGB, Adobe RGB, DCI-P3)\n• CMYK (Субтрактивний друк)", size=11, fill="#fef2f2", stroke="#ef4444", pad=8)
    out.append(tb_rgb)
    
    # Branch 2: Perceptually Uniform
    tb_lab, _, _ = textbox(620, 230, "Рівномірно-перцептивні простори\n• CIELAB (L*a*b* 1976)\n• Oklab / Oklch (2020)", size=11, fill="#f0fdf4", stroke="#22c55e", pad=8)
    out.append(tb_lab)
    
    out.append(arrow(480, 125, 270, 195, color=LINE))
    out.append(arrow(540, 125, 600, 195, color=LINE))
    
    # Sub-branch from RGB: Intuitive HSV/HSL
    tb_hsv, _, _ = textbox(220, 365, "Інтуїтивно-циліндричні простори\n• HSV (Тон, Насиченість, Значення)\n• HSL (Тон, Насиченість, Світлота)", size=11, fill="#fffbeb", stroke="#f59e0b", pad=8)
    out.append(tb_hsv)
    
    out.append(arrow(220, 270, 220, 325, color=LINE))
    
    # Sub-branch from Oklab: Cylindrical Oklch
    tb_oklch, _, _ = textbox(620, 365, "Полярний перцептивний простір Oklch\n• L (Перцептивна світлота)\n• C (Хрома), h (Колірний тон)", size=11, fill="#ecfdf5", stroke="#10b981", pad=8)
    out.append(tb_oklch)
    
    out.append(arrow(620, 270, 620, 325, color=LINE))
    
    out.append("</svg>")
    return "\n".join(out)

def build_fig2():
    """MacAdam Ellipses vs Oklab Perceptual Uniformity."""
    w, h = 760, 360
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Left Panel: CIE 1931 (Non-uniform)
    out.append(rect(20, 20, 350, 310, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(195, 45, "CIE 1931 xy (Нерівномірний простір)", size=13, bold=True))
    
    # Axes CIE
    out.append(line(50, 290, 340, 290, color=LINE))
    out.append(line(50, 290, 50, 70, color=LINE))
    out.append(text(340, 305, "x", size=12, italic=True))
    out.append(text(35, 70, "y", size=12, italic=True))
    
    # Non-uniform MacAdam ellipses (Green huge, Blue tiny)
    out.append('<ellipse cx="140" cy="120" rx="35" ry="18" transform="rotate(-30 140 120)" fill="none" stroke="#22c55e" stroke-width="2"/>')
    out.append(text(140, 85, "Еліпс у зеленій зоні (величезний)", size=9, color="#15803d"))
    
    out.append('<ellipse cx="90" cy="250" rx="10" ry="6" transform="rotate(45 90 250)" fill="none" stroke="#3b82f6" stroke-width="2"/>')
    out.append(text(130, 275, "У синій зоні (крихітний)", size=9, color="#1d4ed8"))
    
    out.append('<ellipse cx="270" cy="230" rx="20" ry="8" transform="rotate(10 270 230)" fill="none" stroke="#ef4444" stroke-width="2"/>')
    out.append(text(270, 205, "У червоній зоні", size=9, color="#b91c1c"))
    
    out.append(text(195, 318, "Поріг сприйняття ΔE змінюється в 20 разів!", size=10, color=POS, bold=True))
    
    # Right Panel: Oklab (Uniform)
    out.append(rect(390, 20, 350, 310, fill="#fafafa", stroke="#d1d5db", sw=1))
    out.append(text(565, 45, "Oklab ab (Рівномірно-перцептивний)", size=13, bold=True))
    
    # Axes Oklab
    out.append(line(420, 180, 710, 180, color=LINE))
    out.append(line(565, 300, 565, 70, color=LINE))
    out.append(text(710, 195, "a (зелений ↔ червоний)", size=10, color=MUTED))
    out.append(text(570, 65, "b (синій ↔ жовтий)", size=10, color=MUTED))
    
    # Uniform circles in Oklab
    out.append(circle(480, 130, 18, fill="none", stroke="#22c55e", sw=2))
    out.append(circle(500, 240, 18, fill="none", stroke="#3b82f6", sw=2))
    out.append(circle(640, 210, 18, fill="none", stroke="#ef4444", sw=2))
    
    out.append(text(565, 318, "Однакові кола однакового радіуса по всьому простору", size=10, color=FIELD, bold=True))
    
    out.append("</svg>")
    return "\n".join(out)

def build_fig3():
    """RGB Additive vs CMYK Subtractive Physics."""
    w, h = 760, 350
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Left Box: RGB Additive Synthesis
    out.append(rect(20, 20, 350, 305, fill="#0f172a", stroke="#334155", sw=1.5))
    out.append(text(195, 45, "Аддитивна модель RGB (Випромінювання)", size=13, color="#ffffff", bold=True))
    
    tb_rgb_desc, _, _ = textbox(195, 140, "Червоний + Зелений + Синій\nСвітлові промені додаються\n(Сума всіх = Біле світло)", size=11, fill="#1e293b", stroke="#3b82f6", color="#ffffff", pad=8)
    out.append(tb_rgb_desc)
    
    out.append(text(195, 255, "Темрява (0,0,0) + Світло променів", size=10, color="#94a3b8"))
    out.append(text(195, 280, "R + G + B = Всі довжини хвиль (Білий)", size=10, color="#38bdf8"))
    
    # Right Box: CMYK Subtractive Synthesis
    out.append(rect(390, 20, 350, 305, fill="#ffffff", stroke="#d1d5db", sw=1.5))
    out.append(text(565, 45, "Субтрактивна модель CMYK (Поглинання)", size=13, color=INK, bold=True))
    
    tb_cmyk_desc, _, _ = textbox(565, 140, "Блакитний + Пурпуровий + Жовтий\nПігменти поглинають спектр\n(Сума C+M+Y = Брудний брунатний)", size=11, fill="#f8fafc", stroke="#ec4899", pad=8)
    out.append(tb_cmyk_desc)
    
    out.append(text(565, 245, "Біле світло − Спектральне поглинання пігменту", size=10, color=MUTED))
    out.append(text(565, 265, "C+M+Y поглинають неідеально → K (Чорний)", size=9, color=POS, bold=True))
    out.append(text(565, 285, "Закон Бугера — Ламберта — Бера", size=10, color=MUTED, italic=True))
    
    out.append("</svg>")
    return "\n".join(out)

def build_fig4():
    """Mathematical Pipeline of Color Transformation."""
    w, h = 860, 260
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(text(w/2, 25, "Математичний конвеєр перетворення колірних просторів", size=15, bold=True))
    
    # Step 1: sRGB Non-linear
    tb1, w1, _ = textbox(90, 110, "sRGB 8-bit\n[0 .. 255]\nНелінійний", size=11, fill="#fef3c7", stroke="#f59e0b", pad=8)
    out.append(tb1)
    
    # Step 2: sRGB Linear
    tb2, w2, _ = textbox(270, 110, "sRGB Linear\n[0.0 .. 1.0]\nГамма-декомпандування", size=11, fill="#fef3c7", stroke="#d97706", pad=8)
    out.append(tb2)
    
    # Step 3: CIE XYZ
    tb3, w3, _ = textbox(470, 110, "CIE XYZ 1931\nBradford Матриця\n(Апаратно-незалежний)", size=11, fill="#e0e7ff", stroke="#4f46e5", pad=8)
    out.append(tb3)
    
    # Step 4: Oklab
    tb4, w4, _ = textbox(670, 110, "Oklab (L, a, b)\nКубічний корінь\nРівномірно-перцептивний", size=11, fill="#dcfce7", stroke="#16a34a", pad=8)
    out.append(tb4)
    
    # Step 5: Oklch
    tb5, w5, _ = textbox(800, 110, "Oklch\n(L, C, h)", size=11, fill="#dcfce7", stroke="#15803d", pad=6)
    out.append(tb5)
    
    # Arrows between boxes (leaving space for text above line)
    out.append(arrow(90 + w1/2 + 2, 110, 270 - w2/2 - 2, 110, color=LINE))
    out.append(text((90 + w1/2 + 270 - w2/2)/2, 90, "EOTF γ=2.2", size=9, color=MUTED))
    
    out.append(arrow(270 + w2/2 + 2, 110, 470 - w3/2 - 2, 110, color=LINE))
    out.append(text((270 + w2/2 + 470 - w3/2)/2, 90, "Матриця M", size=9, color=MUTED))
    
    out.append(arrow(470 + w3/2 + 2, 110, 670 - w4/2 - 2, 110, color=LINE))
    out.append(text((470 + w3/2 + 670 - w4/2)/2, 90, "M₁ → ∛ → M₂", size=9, color=MUTED))
    
    out.append(arrow(670 + w4/2 + 2, 110, 800 - w5/2 - 2, 110, color=LINE))
    out.append(text((670 + w4/2 + 800 - w5/2)/2, 90, "atan2", size=9, color=MUTED))
    
    # Bottom explanation box
    tb_note, _, _ = textbox(w/2, 210, "Пряма обробка світла (змішування, фільтри) вимагає sRGB Linear або CIE XYZ.\nОбчислення колірних відмінностей ΔE та вибір гармонійних палітр виконується в Oklab / Oklch.", size=11, fill="#f8fafc", stroke="#94a3b8", pad=8)
    out.append(tb_note)
    
    out.append("</svg>")
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'color-space-taxonomy.svg': build_fig1(),
        'macadam-ellipses-oklab.svg': build_fig2(),
        'rgb-cmyk-absorption.svg': build_fig3(),
        'color-conversion-pipeline.svg': build_fig4()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == '__main__':
    main()
