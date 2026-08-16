# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

def generate_perovskite_pzt():
    w, h = 760, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(w/2, 28, "Перовськітна структура ABO₃ у PZT: параелектрична та сегнетоелектрична фази", size=15, bold=True, fill="#eef2f7")
    out.append(tb)

    out.append(rect(20, 60, 350, 280, fill="none", stroke=MUTED, sw=1, rx=8))
    t1, _, _ = textbox(195, 82, "Кубічна фаза (T > T_c, параелектрична)", size=13, bold=True, fill="#e2e8f0")
    out.append(t1)

    corners_left = [(100, 150), (220, 150), (220, 250), (100, 250),
                    (140, 120), (260, 120), (260, 220), (140, 220)]
    edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
    for e in edges:
        p1, p2 = corners_left[e[0]], corners_left[e[1]]
        out.append(line(p1[0], p1[1], p2[0], p2[1], color="#94a3b8", sw=1.2, dash="3,3" if e[0]>=4 or e[1]>=4 else None))

    out.append(circle(160, 200, 7, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(160, 150, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(160, 250, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(100, 200, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(220, 200, 6, fill=NEG, stroke=LINE, sw=1))

    out.append(circle(180, 185, 10, fill=POS, stroke=LINE, sw=1.5))
    out.append(text(180, 189, "Ti/Zr", size=9, color="#ffffff", bold=True))

    for c in corners_left:
        out.append(circle(c[0], c[1], 7, fill="#8e44ad", stroke=LINE, sw=1))

    t_left, _, _ = textbox(195, 305, "Центр симетрії збережено\nДипольний момент P = 0", size=12, fill="#ffffff", stroke=MUTED, rx=4)
    out.append(t_left)

    out.append(rect(390, 60, 350, 280, fill="none", stroke=POS, sw=1.2, rx=8))
    t2, _, _ = textbox(565, 82, "Тетрагональна фаза (T < T_c, сегнетоелектрична)", size=13, bold=True, color=POS, fill="#ffe3e3")
    out.append(t2)

    corners_right = [(470, 160), (590, 160), (590, 250), (470, 250),
                     (510, 130), (630, 130), (630, 220), (510, 220)]
    for e in edges:
        p1, p2 = corners_right[e[0]], corners_right[e[1]]
        out.append(line(p1[0], p1[1], p2[0], p2[1], color="#cbd5e1", sw=1.2, dash="3,3" if e[0]>=4 or e[1]>=4 else None))

    out.append(circle(530, 205, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(530, 160, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(530, 250, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(470, 205, 6, fill=NEG, stroke=LINE, sw=1))
    out.append(circle(590, 205, 6, fill=NEG, stroke=LINE, sw=1))

    out.append(circle(550, 175, 10, fill=POS, stroke=LINE, sw=1.5))
    out.append(text(550, 179, "Ti/Zr", size=9, color="#ffffff", bold=True))

    out.append(arrow(655, 230, 655, 150, color=POS, sw=3))
    out.append(text(675, 190, "P", size=16, color=POS, bold=True))
    out.append(text(675, 205, "(зсув Δz)", size=11, color=POS, italic=True))

    for c in corners_right:
        out.append(circle(c[0], c[1], 7, fill="#8e44ad", stroke=LINE, sw=1))

    t_right, _, _ = textbox(550, 305, "Асиметрія: зсув Ti⁴⁺/Zr⁴⁺ відносно O²⁻\nСпонтанна поляризація P ≠ 0", size=12, fill="#ffffff", stroke=POS, rx=4)
    out.append(t_right)

    out.append('</svg>')
    return "\n".join(out)


def generate_mpb_phase_diagram():
    w, h = 760, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(w/2, 25, "Фазова діаграма Pb(Zr_x Ti_{1-x})O₃ та пік п'єзомодуля на MPB (x ≈ 0.52)", size=15, bold=True, fill="#eef2f7")
    out.append(tb)

    ox, oy = 80, 250
    gw, gh = 600, 190

    out.append(rect(ox, oy - gh, gw, gh, fill="none", stroke=LINE, sw=1.5))

    # Лінія температури Кюрі
    tc_path = f"M {ox} {oy - 186} Q {ox + 300} {oy - 140} {ox + gw} {oy - 85}"
    out.append(f'<path d="{tc_path}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    out.append(text(540, oy - 150, "Температура Кюрі T_c", size=12, color=POS, bold=True))

    # MPB розірвана лінія
    mpb_x = ox + int(gw * 0.52) # 392
    out.append(line(mpb_x, oy - gh, mpb_x, oy - 155, color=FIELD, sw=2.5, dash="5,3"))
    out.append(line(mpb_x, oy - 105, mpb_x, oy - 5, color=FIELD, sw=2.5, dash="5,3"))

    out.append(text(280, 52, "Параелектрична кубічна фаза", size=13, color=MUTED, bold=True))
    out.append(text(175, oy - 75, "Тетрагональна фаза (T)\n(зсув [001], 6 станів P)", size=11, color="#2980b9", bold=True))
    out.append(text(540, oy - 75, "Ромбоедрична фаза (R)\n(зсув [111], 8 станів P)", size=11, color="#27ae60", bold=True))
    out.append(text(ox + 555, oy - 20, "Антисегнетоелектрична", size=10, color=MUTED))

    mpb_box, _, _ = textbox(mpb_x, oy - 130, "Морфотропна фазова межа\n(MPB, x ≈ 0.52, 14 станів P)", size=11, color="#ffffff", fill=FIELD, bold=True)
    out.append(mpb_box)

    out.append(text(w/2, oy + 42, "Мольна частка x у Pb(Zr_x Ti_{1-x})O₃  ───►", size=12, bold=True))
    out.append(text(ox, oy + 18, "0.0 (PbTiO₃)", size=11))
    out.append(text(mpb_x, oy + 18, "0.52 (MPB)", size=11, color=FIELD, bold=True))
    out.append(text(ox + gw, oy + 18, "1.0 (PbZrO₃)", size=11))

    out.append(text(22, oy - gh/2 - 20, "Т (°C)", size=13, bold=True))
    out.append(text(ox - 25, oy - gh + 10, "500", size=10))
    out.append(text(ox - 25, oy - gh/2, "250", size=10))
    out.append(text(ox - 20, oy - 5, "0", size=10))

    y_d = 365
    out.append(line(ox, y_d, ox + gw, y_d, color=LINE, sw=1))
    d33_path = f"M {ox} {y_d - 10} Q {mpb_x - 40} {y_d - 15} {mpb_x} {y_d - 65} Q {mpb_x + 40} {y_d - 15} {ox + gw} {y_d - 5}"
    out.append(f'<path d="{d33_path}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    out.append(circle(mpb_x, y_d - 65, 5, fill=POS, stroke=LINE, sw=1))
    out.append(text(mpb_x + 130, y_d - 60, "Максимум d₃₃ (300-600 pC/N) та ε_r", size=12, color=POS, bold=True))
    out.append(text(ox - 40, y_d - 30, "d₃₃ (pC/N)", size=11, color=POS, bold=True))

    out.append('</svg>')
    return "\n".join(out)


def generate_poling_process():
    w, h = 760, 350
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(w/2, 25, "Процес поляризації (Poling) полікристалічної п'єзокераміки PZT", size=15, bold=True, fill="#eef2f7")
    out.append(tb)

    steps = [
        ("1. Після спекання", "Хаотичні домени\nP_net = 0 (немає ефекту)", MUTED, [
            (50, 130, 20), (90, 110, 140), (130, 150, 290), (70, 170, 80), (120, 190, 210)
        ]),
        ("2. Поляризація E_pol", "Сильне поле E ~ 3 кВ/мм\nОрієнтація доменів", POS, [
            (290, 130, 85), (330, 110, 90), (370, 150, 95), (310, 170, 88), (360, 190, 92)
        ]),
        ("3. Залишкова P_r", "Після зняття поля\nP_r ≠ 0 (п'єзокераміка)", FIELD, [
            (530, 130, 75), (570, 110, 80), (610, 150, 85), (550, 170, 78), (600, 190, 82)
        ])
    ]

    for i, (title, sub, border_col, dipoles) in enumerate(steps):
        cx = 140 + i * 240
        cy = 160
        rw, rh = 210, 230

        out.append(rect(cx - rw/2, cy - rh/2 + 20, rw, rh, fill="none", stroke=border_col, sw=1.5, rx=8))

        t_box, _, _ = textbox(cx, cy - rh/2 + 35, title, size=13, bold=True, color=border_col, fill="#ffffff")
        out.append(t_box)

        out.append(rect(cx - 80, cy - 45, 160, 8, fill="#cbd5e1", stroke=LINE, sw=1))
        out.append(rect(cx - 80, cy + 45, 160, 8, fill="#cbd5e1", stroke=LINE, sw=1))

        if i == 1:
            out.append(arrow(cx + 95, cy + 40, cx + 95, cy - 40, color=POS, sw=2.5))
            out.append(text(cx + 105, cy, "E_pol", size=12, color=POS, bold=True))

        for dx, dy, angle in dipoles:
            out.append(arrow(dx - 10, dy + 10, dx + 10, dy - 10 if angle > 45 else dy + 10, color=border_col, sw=1.8))

        sub_box, _, _ = textbox(cx, cy + 75, sub, size=11, fill="#ffffff", stroke=border_col, rx=4)
        out.append(sub_box)

    out.append('</svg>')
    return "\n".join(out)


def generate_d33_d31_modes():
    w, h = 760, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(w/2, 25, "Основні моди п'єзоелектричної деформації PZT (d₃₃, d₃₁, d₁₅)", size=15, bold=True, fill="#eef2f7")
    out.append(tb)

    modes = [
        ("Поздовжня мода d₃₃", "Поле E₃ ║ Деформація S₃", "Зміна товщини Δt\n(актуатори, стеки)", 130),
        ("Поперечна мода d₃₁", "Поле E₃ ⊥ Деформація S₁", "Зміна довжини ΔL\n(біморфи, зумери)", 380),
        ("Зсувна мода d₁₅", "Поле E₁ ⊥ Поляризація P₃", "Зсув граней γ₅\n(гироскопи, датчики)", 630)
    ]

    for title, rule, app, cx in modes:
        cy = 180
        out.append(rect(cx - 110, cy - 120, 220, 270, fill="none", stroke=MUTED, sw=1, rx=8))

        t_b, _, _ = textbox(cx, cy - 105, title, size=13, bold=True, color=POS if "d₃₃" in title else (FIELD if "d₃₁" in title else NEG), fill="#ffffff")
        out.append(t_b)

        out.append(rect(cx - 45, cy - 35, 90, 70, fill="none", stroke=MUTED, sw=1))

        if "d₃₃" in title:
            out.append(rect(cx - 40, cy - 48, 80, 96, fill="#ffe3e3", stroke=POS, sw=2, rx=4))
            out.append(arrow(cx, cy + 55, cx, cy - 55, color=POS, sw=2))
            out.append(text(cx + 25, cy - 35, "E₃", size=12, color=POS, bold=True))
            out.append(arrow(cx - 55, cy - 48, cx - 55, cy + 48, color=LINE, sw=1.5))
            out.append(text(cx - 75, cy, "Δt", size=12, bold=True))
        elif "d₃₁" in title:
            out.append(rect(cx - 60, cy - 25, 120, 50, fill="#dcfce7", stroke=FIELD, sw=2, rx=4))
            out.append(arrow(cx, cy + 32, cx, cy - 32, color=POS, sw=2))
            out.append(text(cx + 25, cy - 15, "E₃", size=12, color=POS, bold=True))
            out.append(arrow(cx - 60, cy + 35, cx + 60, cy + 35, color=FIELD, sw=1.5))
            out.append(text(cx, cy + 48, "ΔL (d₃₁ < 0)", size=11, color=FIELD, bold=True))
        else:
            out.append(f'<polygon points="{cx-30},{cy-35} {cx+50},{cy-35} {cx+30},{cy+35} {cx-50},{cy+35}" fill="#dbeafe" stroke="{NEG}" stroke-width="2"/>')
            out.append(arrow(cx - 45, cy, cx + 45, cy, color=NEG, sw=2))
            out.append(text(cx, cy - 15, "E₁", size=12, color=NEG, bold=True))

        r_b, _, _ = textbox(cx, cy + 75, rule, size=11, bold=True, fill="#ffffff")
        out.append(r_b)
        a_b, _, _ = textbox(cx, cy + 120, app, size=11, fill="#ffffff", rx=4)
        out.append(a_b)

    out.append('</svg>')
    return "\n".join(out)


def generate_multilayer_langevin():
    w, h = 760, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(w/2, 25, "Конструкції PZT: Багатошаровий стек та перетворювач Ланжевена (Tonpilz)", size=15, bold=True, fill="#eef2f7")
    out.append(tb)

    # Ліва панель: PZT Stack
    out.append(rect(20, 55, 340, 305, fill="none", stroke=MUTED, sw=1, rx=8))
    t1, _, _ = textbox(190, 72, "Багатошаровий PZT-стек", size=13, bold=True, color=POS, fill="#ffe3e3")
    out.append(t1)

    sy = 115
    sh = 14
    for n in range(9):
        py = sy + n * (sh + 3)
        out.append(rect(115, py, 150, sh, fill="#fca5a5" if n%2==0 else "#f87171", stroke=LINE, sw=1))
        elec_side = 95 if n%2==0 else 245
        out.append(line(elec_side, py + sh/2, 265 if n%2==0 else 115, py + sh/2, color=LINE, sw=2))

    out.append(line(95, sy, 95, sy + 9*17, color=POS, sw=3))
    out.append(line(265, sy, 265, sy + 9*17, color=NEG, sw=3))
    out.append(circle(95, sy - 10, 8, fill=POS, stroke=LINE, sw=1))
    out.append(text(95, sy - 6, "+", size=12, color="#ffffff", bold=True))
    out.append(circle(265, sy - 10, 8, fill=NEG, stroke=LINE, sw=1))
    text_neg, _, _ = textbox(265, sy - 10, "−", size=14, color="#ffffff", bold=True)
    out.append(text_neg)

    stack_desc, _, _ = textbox(190, 320, "Низька напруга (50–150 В)\nЗусилля кН, точність < 1 нм", size=11, fill="#ffffff", stroke=POS, rx=4)
    out.append(stack_desc)

    # Права панель: Langevin Transducer
    out.append(rect(390, 55, 350, 305, fill="none", stroke=MUTED, sw=1, rx=8))
    t2, _, _ = textbox(565, 72, "Перетворювач Ланжевена", size=13, bold=True, color=FIELD, fill="#dcfce7")
    out.append(t2)

    out.append(rect(430, 110, 270, 45, fill="#94a3b8", stroke=LINE, sw=1.5, rx=4))
    out.append(text(490, 137, "Задня маса (сталь)", size=11, bold=True))

    out.append(rect(430, 158, 270, 22, fill="#fca5a5", stroke=POS, sw=1.5))
    out.append(text(490, 173, "PZT кільце 1", size=11, bold=True))
    out.append(rect(430, 184, 270, 22, fill="#fca5a5", stroke=POS, sw=1.5))
    out.append(text(490, 199, "PZT кільце 2", size=11, bold=True))

    out.append(rect(430, 210, 270, 55, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=4))
    out.append(text(490, 240, "Випромінювальна накладка (Al / Ti)", size=11, bold=True))

    # Болт з fill="none"
    out.append(rect(555, 95, 20, 170, fill="none", stroke=LINE, sw=1.5))
    out.append(text(565, 105, "Болт", size=9, bold=True))

    lang_desc, _, _ = textbox(565, 320, "Стиснення болтом захищає PZT від розриву\nВисока потужність ультразвуку (кВт)", size=11, fill="#ffffff", stroke=FIELD, rx=4)
    out.append(lang_desc)

    out.append('</svg>')
    return "\n".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    figs = {
        "perovskite-pzt.svg": generate_perovskite_pzt(),
        "mpb-phase-diagram.svg": generate_mpb_phase_diagram(),
        "poling-process.svg": generate_poling_process(),
        "d33-d31-modes.svg": generate_d33_d31_modes(),
        "multilayer-langevin.svg": generate_multilayer_langevin(),
    }

    for name, content in figs.items():
        path = os.path.join(img_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == "__main__":
    main()
