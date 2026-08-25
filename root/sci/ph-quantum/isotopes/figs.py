# -*- coding: utf-8 -*-
import os
import sys
import math

# Add path to scripts/ in repo root (4 levels up from book/physics/nuclear-physics/isotopes)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(OUT_DIR, exist_ok=True)

def make_isotopes_isobars_isotones():
    """Figure 1: Nuclide classification: Isotopes, Isobars, Isotones, and Isomers."""
    w, h = 880, 540
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w/2, 32, "Класифікація нуклідів: Ізотопи, Ізобари, Ізотони та Ізомери", size=18, bold=True))

    ox, oy = 120, 440
    gw, gh = 420, 360

    for z in range(4, 10):
        y_pos = oy - (z - 4) * (gh / 5.0)
        out.append(line(ox, y_pos, ox + gw, y_pos, color="#f0f0f0", sw=1, dash="4,4"))
        out.append(text(ox - 18, y_pos + 5, f"Z = {z}", size=13, anchor="end", color=MUTED))

    for n in range(4, 10):
        x_pos = ox + (n - 4) * (gw / 5.0)
        out.append(line(x_pos, oy, x_pos, oy - gh, color="#f0f0f0", sw=1, dash="4,4"))
        out.append(text(x_pos, oy + 24, f"N = {n}", size=13, anchor="middle", color=MUTED))

    out.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))

    out.append(text(ox + gw / 2, oy + 54, "Кількість нейтронів N (N = A - Z)", size=14, bold=True))
    out.append(text(ox - 50, oy - gh - 15, "Кількість протонів Z", size=14, bold=True, anchor="start"))

    def get_coords(z, n):
        x = ox + (n - 4) * (gw / 5.0)
        y = oy - (z - 4) * (gh / 5.0)
        return x, y

    r_node = 18

    x1, y1 = get_coords(6, 6)
    x2, y2 = get_coords(6, 7)
    x3, y3 = get_coords(6, 8)
    out.append(line(x1 + r_node, y1, x2 - r_node, y2, color=NEG, sw=4))
    out.append(line(x2 + r_node, y2, x3 - r_node, y3, color=NEG, sw=4))

    tx1, ty1 = get_coords(5, 7)
    tx2, ty2 = get_coords(6, 7)
    tx3, ty3 = get_coords(7, 7)
    tx4, ty4 = get_coords(8, 7)
    out.append(line(tx1, ty1 - r_node, tx2, ty2 + r_node, color=FIELD, sw=4))
    out.append(line(tx2, ty2 - r_node, tx3, ty3 + r_node, color=FIELD, sw=4))
    out.append(line(tx3, ty3 - r_node, tx4, ty4 + r_node, color=FIELD, sw=4))

    bx1, by1 = get_coords(6, 8)
    bx2, by2 = get_coords(7, 7)
    bx3, by3 = get_coords(8, 6)
    out.append(line(bx1 - 14.6, by1 - 12.5, bx2 + 14.6, by2 + 12.5, color=POS, sw=4))
    out.append(line(bx2 - 14.6, by2 - 12.5, bx3 + 14.6, by3 + 12.5, color=POS, sw=4))

    nuclides = [
        (6, 6, "¹²C", "#ffffff", NEG),
        (6, 7, "¹³C", "#ffffff", NEG),
        (6, 8, "¹⁴C", "#ffffff", POS),
        (5, 7, "¹²B", "#ffffff", FIELD),
        (7, 7, "¹⁴N", "#ffffff", FIELD),
        (8, 7, "¹⁵O", "#ffffff", FIELD),
        (8, 6, "¹⁴O", "#ffffff", POS),
        (7, 6, "¹³N", "#ffffff", INK),
        (5, 8, "¹³B", "#ffffff", INK),
    ]

    for z, n, label, bg_col, border_col in nuclides:
        nx, ny = get_coords(z, n)
        out.append(textbox(nx, ny, label, size=13, pad=7, fill=bg_col, stroke=border_col, sw=2, bold=True)[0])

    panel_x = ox + gw + 40
    out.append(textbox(panel_x + 110, 100, "ІЗОТОПИ (Z = const)\nОднакова кількість протонів (Z),\nрізна кількість нейтронів (N).\nПриклад: ¹²C, ¹³C, ¹⁴C.", size=12, pad=8, fill="#e8f0fe", stroke=NEG, sw=1.5)[0])
    out.append(textbox(panel_x + 110, 210, "ІЗОБАРИ (A = Z + N = const)\nОднакова атомна маса (A),\nрізні хімічні елементи.\nПриклад: ¹⁴C, ¹⁴N, ¹⁴O.", size=12, pad=8, fill="#fcedec", stroke=POS, sw=1.5)[0])
    out.append(textbox(panel_x + 110, 320, "ІЗОТОНИ (N = const)\nОднакова кількість нейтронів (N),\nрізні заряди ядер (Z).\nПриклад: ¹²B, ¹³C, ¹⁴N, ¹⁵O.", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, sw=1.5)[0])
    out.append(textbox(panel_x + 110, 430, "ЯДЕРНІ ІЗОМЕРИ (m)\nОднакові Z та N, але різний\nметастабільний квантовий стан.\nПриклад: ⁹⁹ᵐTc та ⁹⁹Tc.", size=12, pad=8, fill="#fef9e7", stroke="#d35400", sw=1.5)[0])

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'isotopes-isobars-isotones.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_valley_of_stability():
    """Figure 2: Valley of Nuclear Stability (Nuclide Chart)."""
    w, h = 900, 560
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w/2, 32, "Нуклідна карта та Долина ядерної стійкості (Valley of Stability)", size=18, bold=True))

    ox, oy = 110, 470
    gw, gh = 460, 390

    for z_val in range(0, 91, 20):
        y_pos = oy - (z_val / 90.0) * gh
        out.append(line(ox, y_pos, ox + 180, y_pos, color="#f0f0f0", sw=1, dash="4,4"))
        out.append(text(ox - 15, y_pos + 5, f"{z_val}", size=12, anchor="end", color=MUTED))

    for n_val in range(0, 141, 20):
        x_pos = ox + (n_val / 140.0) * gw
        out.append(line(x_pos, oy, x_pos, oy - gh, color="#f0f0f0", sw=1, dash="4,4"))
        out.append(text(x_pos, oy + 22, f"{n_val}", size=12, anchor="middle", color=MUTED))

    ref_x2 = ox + (90.0 / 140.0) * gw
    ref_y2 = oy - gh
    out.append(line(ox + 45, oy - 40, ox + 140, oy - 120, color="#b0bec5", sw=1.5, dash="6,6"))
    out.append(line(ox + 230, oy - 200, ox + 260, oy - 230, color="#b0bec5", sw=1.5, dash="6,6"))

    out.append(textbox(ox + 185, oy - 160, "Лінія N = Z", size=11, pad=4, fill="#ffffff", stroke="#b0bec5", sw=1)[0])

    out.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))

    out.append(text(ox + gw / 2, oy + 50, "Кількість нейтронів N", size=14, bold=True))
    out.append(text(ox - 45, oy - gh - 15, "Кількість протонів Z", size=14, bold=True, anchor="start"))

    valley_pts = [
        (0, 0), (2, 2), (6, 6), (8, 8), (12, 12), (16, 16), (20, 20),
        (28, 24), (35, 30), (45, 36), (50, 40), (60, 46), (70, 50),
        (82, 56), (90, 60), (100, 66), (110, 72), (120, 78), (126, 82), (138, 88)
    ]

    path_coords = []
    for n_val, z_val in valley_pts:
        px = ox + (n_val / 140.0) * gw
        py = oy - (z_val / 90.0) * gh
        path_coords.append((px, py))

    for i in range(len(path_coords) - 1):
        x1, y1 = path_coords[i]
        x2, y2 = path_coords[i+1]
        out.append(line(x1, y1, x2, y2, color=FIELD, sw=5))

    doubly_magic = [
        (2, 2, "⁴He", 30, -30),
        (8, 8, "¹⁶O", 30, -30),
        (20, 20, "⁴⁰Ca", -28, -24),
        (28, 20, "⁴⁸Ca", 28, -24),
        (126, 82, "²⁰⁸Pb", -30, -24),
    ]
    for n_val, z_val, label, dx, dy in doubly_magic:
        px = ox + (n_val / 140.0) * gw
        py = oy - (z_val / 90.0) * gh
        out.append(textbox(px + dx, py + dy, label, size=10, pad=3, fill="#ffffff", stroke=LINE, sw=1, bold=True)[0])

    out.append(textbox(ox + 230, oy - 310, "β⁻ розпад (трансформація n → p)\nНадлишок нейтронів над лінією стійкості", size=11, pad=6, fill="#e8f0fe", stroke=NEG, sw=1.2)[0])
    out.append(textbox(ox + 160, oy - 70, "β⁺ розпад / Електронне захоплення (p → n)\nНадлишок протонів нижче лінії стійкості", size=11, pad=6, fill="#fcedec", stroke=POS, sw=1.2)[0])
    out.append(textbox(ox + 360, oy - 380, "α-розпад та спонтанний поділ\nОбласть важких нуклідів (A > 200, Z > 82)", size=11, pad=6, fill="#fef9e7", stroke="#d35400", sw=1.2)[0])

    panel_x = ox + gw + 35
    out.append(textbox(panel_x + 100, 130, "ПАРНІСТЬ НУКЛОНІВ\n• Парні Z / Парні N: 254 стійких\n• Парні Z / Непарні N: 53 стійких\n• Непарні Z / Парні N: 50 стійких\n• Непарні Z / Непарні N: лише 4!\n  (²H, ⁶Li, ¹⁰B, ¹⁴N)", size=11, pad=8, fill="#ffffff", stroke=LINE, sw=1.5)[0])
    out.append(textbox(panel_x + 100, 310, "МАГІЧНІ ЧИСЛА\n2, 8, 20, 28, 50, 82, 126\nНукліди з магічним числом\nпротонів або нейтронів володіють\nпідвищеною енергією зв'язку\nта поширеністю у Всесвіті.", size=11, pad=8, fill="#e8f8f5", stroke=FIELD, sw=1.5)[0])
    out.append(textbox(panel_x + 100, 450, "ОСНОВНИЙ ТРЕНД N/Z\n• Легкі елементи: N/Z ≈ 1.0\n• Важкі елементи: N/Z ≈ 1.54\nКулонівське відштовхування Z²\nвимагає більше нейтронів.", size=11, pad=8, fill="#f4f6f8", stroke=MUTED, sw=1.5)[0])

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'valley-of-stability.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_isotope_effect_energy_levels():
    """Figure 3: Quantum Isotope Effect on vibrational energy levels and bond strength."""
    w, h = 860, 520
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w/2, 30, "Квантовий ізотопний ефект: Нульові коливання та міцність зв'язку", size=18, bold=True))

    ox, oy = 110, 440
    gw, gh = 420, 360

    pts = []
    for r_idx in range(20, 420, 4):
        r = r_idx / 100.0
        v = 300 * ((1 - math.exp(-1.4 * (r - 1.2))) ** 2)
        px = ox + r_idx
        py = oy - 320 + v
        if py < oy + 20:
            pts.append((px, py))

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        out.append(line(x1, y1, x2, y2, color=LINE, sw=2.5))

    out.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    out.append(text(ox + gw / 2, oy + 45, "Міжатомна відстань r", size=14, bold=True))
    out.append(text(ox - 45, oy - gh + 15, "Потенціальна енергія V(r)", size=14, bold=True, anchor="start"))

    y_ch = oy - 270
    y_cd = oy - 295

    out.append(line(ox + 45, y_ch, ox + 195, y_ch, color=POS, sw=3))
    out.append(textbox(ox + 310, y_ch, "E₀(C-H) = ½·ħ·ω_H (вищий рівень)", size=11, pad=4, fill="#ffffff", stroke=POS, sw=1.2, bold=True)[0])

    out.append(line(ox + 55, y_cd, ox + 185, y_cd, color=NEG, sw=3))
    out.append(textbox(ox + 310, y_cd, "E₀(C-D) = ½·ħ·ω_D (нижчий рівень)", size=11, pad=4, fill="#ffffff", stroke=NEG, sw=1.2, bold=True)[0])

    out.append(line(ox + 130, y_ch, ox + 130, y_cd, color=FIELD, sw=2))
    out.append(textbox(ox + 155, (y_ch + y_cd)/2, "ΔE₀", size=10, pad=3, fill="#ffffff", stroke=FIELD, sw=1, bold=True)[0])

    out.append(textbox(ox + 120, oy - 40, "Мінімум ями V_min\n(класична рівновага)", size=11, pad=5, fill="#f4f6f8", stroke=MUTED, sw=1)[0])

    panel_x = ox + gw + 40
    out.append(textbox(panel_x + 100, 110, "ЗВЕДЕНА МАСА (μ)\nμ = (m₁ · m₂) / (m₁ + m₂)\nДля зв'язку C-H: μ ≈ 0.923 а.о.м.\nДля зв'язку C-D: μ ≈ 1.714 а.о.м.\nВажчий дейтерій збільшує μ!", size=12, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.5)[0])
    out.append(textbox(panel_x + 100, 260, "ЧАСТОТА КОЛИВАНЬ (ω)\nω = √(k / μ)\nВища маса μ дає меншу частоту\nнульових коливань ω_D < ω_H.\nЕнергія E₀(C-D) лежить глибше!", size=12, pad=8, fill="#e8f0fe", stroke=NEG, sw=1.5)[0])
    out.append(textbox(panel_x + 100, 410, "КІНЕТИЧНИЙ ІЗОТОПНИЙ ЕФЕКТ\nЕнергія активації розриву зв'язку:\nE_a(C-D) > E_a(C-H)\nЗв'язок C-D міцніший на ~5 кДж/моль.\nРеакції C-D ідуть у 2–7 разів повільніше!", size=11, pad=8, fill="#fcedec", stroke=POS, sw=1.5)[0])

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'isotope-effect-energy-levels.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_gas_centrifuge_cascade():
    """Figure 4: Gas Centrifuge Rotor and Enrichment Cascade."""
    w, h = 900, 560
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w/2, 30, "Розділення ізотопів: Ротор газової центрифуги та збагачувальний каскад", size=17, bold=True))

    out.append('<g transform="translate(0,0)">')
    rx, ry = 230, 290
    rw, rh = 160, 360

    out.append(rect(rx - rw/2, ry - rh/2, rw, rh, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    out.append(textbox(rx, ry - rh/2 - 25, "Газова центрифуга (UF₆)", size=12, pad=4, fill="#ffffff", stroke=LINE, sw=1, bold=True)[0])

    out.append(line(rx - rw/2 + 20, ry - rh/2 + 40, rx + rw/2 - 20, ry - rh/2 + 40, color=MUTED, sw=1.5))
    out.append(line(rx - rw/2 + 20, ry + rh/2 - 40, rx + rw/2 - 20, ry + rh/2 - 40, color=MUTED, sw=1.5))
    out.append(line(rx - rw/2 + 20, ry - rh/2 + 40, rx - rw/2 + 20, ry + rh/2 - 40, color=MUTED, sw=1.5))
    out.append(line(rx + rw/2 - 20, ry - rh/2 + 40, rx + rw/2 - 20, ry + rh/2 - 40, color=MUTED, sw=1.5))

    out.append(line(rx, ry - rh/2 + 10, rx, ry + rh/2 - 10, color=POS, sw=1.5, dash="6,4"))
    out.append(textbox(rx, ry + rh/2 + 20, "Ось обертання (~100,000 об/хв)", size=10, pad=4, fill="#ffffff", stroke=POS, sw=1)[0])

    out.append(textbox(rx - 25, ry - 70, "Важкий ²³⁸UF₆ (до стінки)", size=9.5, pad=3, fill="#ffffff", stroke=NEG, sw=1)[0])
    out.append(textbox(rx + 25, ry + 20, "Легкий ²³⁵UF₆ (поблизу осі)", size=9.5, pad=3, fill="#ffffff", stroke=FIELD, sw=1)[0])

    out.append(arrow(rx - 170, ry, rx - rw/2 - 2, ry, color=INK, sw=2))
    out.append(textbox(rx - 175, ry, "Сировина (Feed)", size=10, pad=4, fill="#ffffff", stroke=LINE, sw=1)[0])

    out.append(arrow(rx, ry - rh/2 - 2, rx, ry - rh/2 - 45, color=FIELD, sw=2))
    out.append(textbox(rx + 85, ry - rh/2 - 45, "Збагачений потік (Product)", size=10, pad=4, fill="#ffffff", stroke=FIELD, sw=1)[0])

    out.append(arrow(rx + rw/2 - 20, ry + rh/2 + 2, rx + rw/2 - 20, ry + rh/2 + 45, color=NEG, sw=2))
    out.append(textbox(rx + rw/2 + 55, ry + rh/2 + 45, "Збіднений відвал (Tails)", size=10, pad=4, fill="#ffffff", stroke=NEG, sw=1)[0])
    out.append('</g>')

    cx = 660
    cy_stages = [150, 290, 430]
    stage_labels = ["Ступінь N + 1 (Збагачення)", "Ступінь N (Робочий)", "Ступінь N - 1 (Збіднення)"]

    for i, s_y in enumerate(cy_stages):
        out.append(textbox(cx, s_y, f"ЦЕНТРИФУЖНА БАТАРЕЯ\n{stage_labels[i]}", size=12, pad=8, fill="#ffffff", stroke=LINE, sw=1.8)[0])

    out.append(arrow(cx + 40, cy_stages[2] - 25, cx + 40, cy_stages[1] + 25, color=FIELD, sw=2))
    out.append(arrow(cx + 40, cy_stages[1] - 25, cx + 40, cy_stages[0] + 25, color=FIELD, sw=2))
    out.append(textbox(cx + 65, (cy_stages[1] + cy_stages[2])/2, "²³⁵U", size=10, pad=3, fill="#ffffff", stroke=FIELD, sw=1)[0])

    out.append(arrow(cx - 40, cy_stages[0] + 25, cx - 40, cy_stages[1] - 25, color=NEG, sw=2))
    out.append(arrow(cx - 40, cy_stages[1] + 25, cx - 40, cy_stages[2] - 25, color=NEG, sw=2))
    out.append(textbox(cx - 65, (cy_stages[0] + cy_stages[1])/2, "²³⁸U", size=10, pad=3, fill="#ffffff", stroke=NEG, sw=1)[0])

    out.append(arrow(cx - 160, cy_stages[1], cx - 90, cy_stages[1], color=INK, sw=2))
    out.append(textbox(cx - 175, cy_stages[1], "Вхід F", size=11, pad=4, fill="#ffffff", stroke=LINE, sw=1)[0])

    out.append(arrow(cx, cy_stages[0] - 25, cx, cy_stages[0] - 60, color=FIELD, sw=2.5))
    out.append(textbox(cx, cy_stages[0] - 75, "Продукт P (Високозбагачений ²³⁵U)", size=11, pad=4, fill="#ffffff", stroke=FIELD, sw=1.2, bold=True)[0])

    out.append(arrow(cx, cy_stages[2] + 25, cx, cy_stages[2] + 60, color=NEG, sw=2.5))
    out.append(textbox(cx, cy_stages[2] + 75, "Відвал W (Збіднений ²³⁸U)", size=11, pad=4, fill="#ffffff", stroke=NEG, sw=1.2, bold=True)[0])

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'valley-of-stability.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def main():
    make_isotopes_isobars_isotones()
    make_valley_of_stability()
    make_isotope_effect_energy_levels()
    make_gas_centrifuge_cascade()
    print("Successfully generated all SVG figures for isotopes!")

if __name__ == '__main__':
    main()
