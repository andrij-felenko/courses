# -*- coding: utf-8 -*-
"""Фігури до теми «Надпровідність».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"

def path(d, color=LINE, sw=1.5, fill="none", dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{dash_attr}/>'

def save(filename, elements, w, h):
    render(filename, w, h, *elements)


# ── Фігура 1: Опір від температури (R vs T) ──────────────────────────────────
def fig_r_vs_temp():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Залежність електричного опору R від температури T", size=16, bold=True))

    ox, oy = 80, 320
    w_axis, h_axis = 620, 250

    # Осі координат
    f.append(arrow(ox, oy, ox + w_axis, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - h_axis, color=INK, sw=1.8))
    f.append(text(ox + w_axis - 10, oy + 25, "Температура T (К)", size=13, bold=True))
    f.append(text(ox - 30, oy - h_axis + 20, "Опір R (Ом)", size=13, bold=True, anchor="end"))

    # Позначка Tc та 0
    tc_x = ox + 260
    f.append(line(tc_x, oy, tc_x, oy - h_axis + 40, color="#bdc3c7", sw=1.2, dash="4,4"))
    f.append(text(tc_x, oy + 25, "T_c", size=14, bold=True, color=COLOR_RED))
    f.append(text(tc_x, oy + 42, "(критична)", size=11, color=MUTED))
    f.append(text(ox - 10, oy + 15, "0", size=12))

    # Крива звичайного металу (нормальний стан)
    r0_y = oy - 45
    f.append(line(ox - 5, r0_y, ox + 5, r0_y, color=COLOR_BLUE, sw=1.5))
    f.append(text(ox - 15, r0_y + 4, "R₀", size=12, bold=True, color=COLOR_BLUE, anchor="end"))

    path_normal = f"M {ox},{r0_y} C {ox+150},{r0_y-15} {ox+350},{oy-160} {ox+550},{oy-220}"
    f.append(path(path_normal, color=COLOR_BLUE, sw=2.5, dash="6,4"))
    f.append(text(ox + 460, oy - 200, "Звичайний метал (R₀ > 0 при T=0)", size=13, bold=True, color=COLOR_BLUE))

    # Крива надпровідника
    path_super = f"M {ox},{oy} L {tc_x},{oy} L {tc_x},{oy-130} C {ox+350},{oy-160} {ox+550},{oy-220}"
    f.append(path(path_super, color=COLOR_RED, sw=3))

    f.append(circle(tc_x, oy, 5, fill=COLOR_RED, stroke='#ffffff', sw=1.5))
    f.append(circle(tc_x, oy - 130, 5, fill=COLOR_RED, stroke='#ffffff', sw=1.5))

    f.append(rect(ox + 40, oy - 40, 160, 30, fill='#fdedec', stroke=COLOR_RED, sw=1.2, rx=4))
    f.append(text(ox + 120, oy - 20, "Надпровідний стан (R ≡ 0)", size=12, bold=True, color=COLOR_RED))

    f.append(rect(tc_x + 30, oy - 100, 150, 30, fill='#f4f6f8', stroke=MUTED, sw=1.2, rx=4))
    f.append(text(tc_x + 105, oy - 80, "Нормальний стан (R > 0)", size=12, bold=True, color=INK))

    save(os.path.join(IMG, "r-vs-temp.svg"), f, W, H)


# ── Фігура 2: Ефект Мейснера — Оксенфельда ──────────────────────────────────
def fig_meissner_effect():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Ефект Мейснера: виштовхування магнітного поля з надпровідника", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 45, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: T > Tc ---
    f.append(text(midx / 2, 54, "T > T_c (Нормальний стан: поле B проникає)", size=13, bold=True, color=INK))

    cx1, cy = midx / 2, 210
    r_sphere = 55

    for dy in [-80, -50, -20, 0, 20, 50, 80]:
        y_line = cy + dy
        f.append(arrow(cx1 - 140, y_line, cx1 + 140, y_line, color=COLOR_GREEN, sw=1.8))

    f.append(circle(cx1, cy, r_sphere, fill='#eaf2f8', stroke=COLOR_BLUE, sw=2))
    f.append(text(cx1, cy, "Метал", size=13, bold=True, color=COLOR_BLUE))
    f.append(text(cx1, cy + 18, "T > T_c", size=11, color=MUTED))

    # --- ПРАВА ЧАСТИНА: T < Tc ---
    f.append(text(midx + midx / 2, 54, "T < T_c (Надпровідність: поле B виштовхується)", size=13, bold=True, color=COLOR_RED))

    cx2 = midx + midx / 2

    for dy in [-80, -50, -20, 0, 20, 50, 80]:
        y_line = cy + dy
        if abs(dy) > 60:
            f.append(arrow(cx2 - 140, y_line, cx2 + 140, y_line, color=COLOR_GREEN, sw=1.8))
        else:
            sign = -1 if dy < 0 else (1 if dy > 0 else 0)
            if sign == 0:
                p1 = f"M {cx2-140},{cy} C {cx2-70},{cy} {cx2-70},{cy-75} {cx2},{cy-75} C {cx2+70},{cy-75} {cx2+70},{cy} {cx2+140},{cy}"
                f.append(path(p1, color=COLOR_GREEN, sw=1.8))
            else:
                bend_y = cy + sign * (r_sphere + 22 + abs(dy) * 0.4)
                p = f"M {cx2-140},{y_line} C {cx2-70},{y_line} {cx2-70},{bend_y} {cx2},{bend_y} C {cx2+70},{bend_y} {cx2+70},{y_line} {cx2+140},{y_line}"
                f.append(path(p, color=COLOR_GREEN, sw=1.8))

    f.append(circle(cx2, cy, r_sphere, fill='#fdedec', stroke=COLOR_RED, sw=2.5))
    f.append(text(cx2, cy - 8, "B = 0 всередині", size=12, bold=True, color=COLOR_RED))
    f.append(text(cx2, cy + 12, "χ = −1", size=12, bold=True, color=COLOR_PURPLE))

    f.append(path(f"M {cx2-r_sphere+4},{cy-10} A {r_sphere-4} {r_sphere-4} 0 0 1 {cx2-r_sphere+4},{cy+10}", color=COLOR_ORANGE, sw=2))
    f.append(arrow(cx2-r_sphere+4, cy+8, cx2-r_sphere+4, cy+14, color=COLOR_ORANGE, sw=2))
    f.append(text(cx2 - r_sphere - 35, cy + 4, "Струми I_s", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(cx2 - r_sphere - 35, cy + 18, "(шар λ_L)", size=10, color=MUTED))

    f.append(text(cx2, H - 35, "Ідеальний діамагнетизм: поверхневі струми гасять поле всередині", size=12, italic=True, color=INK))

    save(os.path.join(IMG, "meissner-effect.svg"), f, W, H)


# ── Фігура 3: Надпровідники I та II роду ────────────────────────────────────
def fig_type1_vs_type2():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Фазові діаграми надпровідників I та II роду в полях H(T)", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: I рід ---
    f.append(text(midx / 2, 54, "Надпровідники I роду (чисті метали)", size=13, bold=True, color=COLOR_BLUE))

    ox1, oy1 = 60, 310
    w_a, h_a = 280, 220
    f.append(arrow(ox1, oy1, ox1 + w_a, oy1, color=INK, sw=1.6))
    f.append(arrow(ox1, oy1, ox1, oy1 - h_a, color=INK, sw=1.6))
    f.append(text(ox1 + w_a - 10, oy1 + 22, "T", size=12, bold=True))
    f.append(text(ox1 - 15, oy1 - h_a + 15, "H", size=12, bold=True))

    tc1_x = ox1 + 220
    hc1_y = oy1 - 170

    p_type1 = f"M {ox1},{hc1_y} Q {ox1+140},{hc1_y+10} {tc1_x},{oy1}"
    f.append(path(p_type1, color=COLOR_BLUE, sw=2.5))
    f.append(text(tc1_x, oy1 + 22, "T_c", size=12, bold=True, color=COLOR_BLUE))
    f.append(text(ox1 - 25, hc1_y + 4, "H_c(0)", size=11, bold=True, color=COLOR_BLUE))

    f.append(rect(ox1 + 30, oy1 - 70, 110, 35, fill='#eaf2f8', stroke=COLOR_BLUE, sw=1, rx=4))
    f.append(text(ox1 + 85, oy1 - 55, "Стан Мейснера", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(ox1 + 85, oy1 - 40, "(B = 0, R = 0)", size=10, color=COLOR_BLUE))

    f.append(text(ox1 + 160, oy1 - 130, "Нормальний", size=12, bold=True, color=INK))
    f.append(text(ox1 + 160, oy1 - 115, "стан (R > 0)", size=11, color=MUTED))


    # --- ПРАВА ЧАСТИНА: II рід ---
    f.append(text(midx + midx / 2, 54, "Надпровідники II роду (сплави, ВТНП)", size=13, bold=True, color=COLOR_RED))

    ox2, oy2 = midx + 60, 310
    f.append(arrow(ox2, oy2, ox2 + w_a, oy2, color=INK, sw=1.6))
    f.append(arrow(ox2, oy2, ox2, oy2 - h_a, color=INK, sw=1.6))
    f.append(text(ox2 + w_a - 10, oy2 + 22, "T", size=12, bold=True))
    f.append(text(ox2 - 15, oy2 - h_a + 15, "H", size=12, bold=True))

    tc2_x = ox2 + 220
    hc1_2_y = oy2 - 50
    hc2_2_y = oy2 - 190

    p_hc1 = f"M {ox2},{hc1_2_y} Q {ox2+140},{hc1_2_y+5} {tc2_x},{oy2}"
    f.append(path(p_hc1, color=COLOR_GREEN, sw=2))

    p_hc2 = f"M {ox2},{hc2_2_y} Q {ox2+150},{hc2_2_y+20} {tc2_x},{oy2}"
    f.append(path(p_hc2, color=COLOR_RED, sw=2.5))

    f.append(text(tc2_x, oy2 + 22, "T_c", size=12, bold=True, color=COLOR_RED))
    f.append(text(ox2 - 25, hc1_2_y + 4, "H_c1", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(ox2 - 25, hc2_2_y + 4, "H_c2", size=11, bold=True, color=COLOR_RED))

    f.append(text(ox2 + 45, oy2 - 22, "Мейснер (B=0)", size=10, bold=True, color=COLOR_GREEN))

    f.append(rect(ox2 + 50, oy2 - 125, 125, 45, fill='#fef9e7', stroke=COLOR_ORANGE, sw=1.2, rx=4))
    f.append(text(ox2 + 112, oy2 - 107, "Змішаний стан", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(ox2 + 112, oy2 - 93, "(Вихори Абрикосова)", size=10, bold=True, color=COLOR_PURPLE))

    f.append(text(ox2 + 150, oy2 - 165, "Нормальний", size=11, bold=True, color=INK))

    save(os.path.join(IMG, "type1-vs-type2.svg"), f, W, H)


# ── Фігура 4: Ефект Джозефсона та СКВІД ─────────────────────────────────────
def fig_josephson_squid():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Джозефсонівський перехід та надпровідне квантове кільце (СКВІД)", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Джозефсонівський перехід ---
    f.append(text(midx / 2, 54, "Джозефсонівський контакт S-I-S", size=13, bold=True, color=COLOR_BLUE))

    cx1, cy1 = midx / 2, 190

    f.append(rect(cx1 - 130, cy1 - 50, 100, 100, fill='#fdedec', stroke=COLOR_RED, sw=2, rx=4))
    f.append(text(cx1 - 80, cy1 - 10, "Надпровідник 1", size=11, bold=True, color=COLOR_RED))
    f.append(text(cx1 - 80, cy1 + 10, "(фаза φ₁)", size=11, color=MUTED))

    f.append(rect(cx1 + 30, cy1 - 50, 100, 100, fill='#fdedec', stroke=COLOR_RED, sw=2, rx=4))
    f.append(text(cx1 + 80, cy1 - 10, "Надпровідник 2", size=11, bold=True, color=COLOR_RED))
    f.append(text(cx1 + 80, cy1 + 10, "(фаза φ₂)", size=11, color=MUTED))

    f.append(rect(cx1 - 30, cy1 - 50, 60, 100, fill='#e5e8e8', stroke=MUTED, sw=1.5, rx=2))
    f.append(text(cx1, cy1 - 25, "Ізолятор", size=10, bold=True, color=INK))
    # Тунелювання куперівських пар
    f.append(arrow(cx1 - 70, cy1 + 25, cx1 + 70, cy1 + 25, color=COLOR_PURPLE, sw=2))
    f.append(text(cx1, cy1 + 40, "Тунелювання 2e", size=11, bold=True, color=COLOR_PURPLE))

    f.append(rect(cx1 - 110, H - 75, 220, 35, fill='#f4f6f8', stroke=COLOR_BLUE, sw=1.2, rx=4))
    f.append(text(cx1, H - 53, "I = I_c · sin(φ₂ − φ₁)", size=13, bold=True, color=COLOR_BLUE))

    # --- ПРАВА ЧАСТИНА: СКВІД (SQUID) ---
    f.append(text(midx + midx / 2, 54, "Квантовий інтерферометр (DC SQUID)", size=13, bold=True, color=COLOR_PURPLE))

    cx2, cy2 = midx + midx / 2, 180

    f.append(circle(cx2, cy2, 70, fill='none', stroke=COLOR_RED, sw=14))
    f.append(circle(cx2, cy2, 56, fill=BG, stroke=COLOR_RED, sw=2))

    f.append(rect(cx2 - 12, cy2 - 76, 24, 14, fill='#e5e8e8', stroke=INK, sw=1.5))
    f.append(text(cx2, cy2 - 82, "J₁", size=11, bold=True, color=COLOR_BLUE))

    f.append(rect(cx2 - 12, cy2 + 62, 24, 14, fill='#e5e8e8', stroke=INK, sw=1.5))
    f.append(text(cx2, cy2 + 90, "J₂", size=11, bold=True, color=COLOR_BLUE))

    f.append(circle(cx2, cy2, 6, fill=COLOR_GREEN, stroke=INK, sw=1))
    f.append(text(cx2, cy2 - 14, "Магнітний потік Φ", size=11, bold=True, color=COLOR_GREEN))

    f.append(arrow(cx2 - 120, cy2, cx2 - 75, cy2, color=COLOR_PURPLE, sw=2))
    f.append(text(cx2 - 100, cy2 - 12, "I_in", size=11, bold=True, color=COLOR_PURPLE))

    f.append(arrow(cx2 + 75, cy2, cx2 + 120, cy2, color=COLOR_PURPLE, sw=2))
    f.append(text(cx2 + 100, cy2 - 12, "I_out", size=11, bold=True, color=COLOR_PURPLE))

    f.append(rect(cx2 - 120, H - 75, 240, 35, fill='#fef9e7', stroke=COLOR_PURPLE, sw=1.2, rx=4))
    f.append(text(cx2, H - 53, "Період осциляцій: ΔΦ = Φ₀ = h / (2e)", size=12, bold=True, color=COLOR_PURPLE))

    save(os.path.join(IMG, "josephson-squid.svg"), f, W, H)


if __name__ == '__main__':
    fig_r_vs_temp()
    fig_meissner_effect()
    fig_type1_vs_type2()
    fig_josephson_squid()
    print("Успішно згенеровано 4 фігури в img/")
