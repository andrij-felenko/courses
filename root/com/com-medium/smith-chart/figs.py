# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COLOR_Z = NEG       # Синій (імпеданс)
COLOR_Y = FIELD     # Зелений (адмітанс)
COLOR_PATH = POS    # Червоний (траєкторія / узгодження)
COLOR_GRID = "#d0d7de" # Світло-сірий для допоміжних кіл

def render(w, h, elements):
    """Скласти підсумковий SVG-документ з оголошенням стрілок."""
    defs = '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
    <marker id="arrow-pos" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
  </defs>''' % (INK, POS)
    body = "\n  ".join(elements)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  %s\n  %s\n</svg>' % (w, h, w, h, defs, body))

def save_svg(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Збережено: %s" % path)


# ── Фігура 1: Відображення з Декартових координат у коло Гамма ───────────────
def fig_mapping_smith():
    W, H = 820, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    # Ліва частина: Декартова площина (R, X)
    p.append(rect(20, 20, 320, 320, fill="#ffffff", stroke=COLOR_Z, sw=1.2, rx=8))
    p.append(textbox(180, 45, "Прямокутна площина (Z = R + jX)", size=12, fill="#ffffff", stroke=COLOR_Z, bold=True)[0])
    
    # Осі R та X
    p.append(line(50, 290, 310, 290, color=LINE, sw=1.5)) # R вісь
    p.append(line(50, 290, 50, 70, color=LINE, sw=1.5))   # X вісь
    p.append(textbox(240, 310, "R (Активний опір) → ∞", size=10, fill="#ffffff", stroke=LINE)[0])
    p.append(textbox(135, 80, "+jX (Індуктивний)", size=10, fill="#ffffff", stroke=POS)[0])
    p.append(textbox(135, 270, "-jX (Ємнісний)", size=10, fill="#ffffff", stroke=NEG)[0])

    # Трішки сітки Декарта (прогалина для центральної рамки)
    for r_val in [60, 120, 180]:
        p.append(line(50 + r_val, 70, 50 + r_val, 120, color="#e5e7eb", sw=1.0, dash="3,3"))
        p.append(line(50 + r_val, 230, 50 + r_val, 280, color="#e5e7eb", sw=1.0, dash="3,3"))
    p.append(textbox(180, 175, "Нескінченна область R ≥ 0\nНе влазить на папір\nСкладні спіралі Z(x)", size=11, fill="#fff5f5", stroke=POS, min_w=190)[0])

    # Центральна стрілка конформного відображення
    p.append(arrow(350, 180, 420, 180, color=POS, sw=2.5))
    p.append(textbox(385, 145, "Мебіус", size=11, fill="#ffffff", stroke=POS, bold=True)[0])
    p.append(textbox(385, 215, "Γ = (z−1)/(z+1)", size=10, fill="#ffffff", stroke=LINE, bold=True)[0])

    # Права частина: Одиничне коло Гамма
    p.append(rect(435, 20, 365, 320, fill="#ffffff", stroke=FIELD, sw=1.2, rx=8))
    p.append(textbox(615, 45, "Площина |Γ| ≤ 1 (Діаграма Сміта)", size=12, fill="#ffffff", stroke=FIELD, bold=True)[0])

    cx, cy, R = 615, 190, 105
    # Граничне коло |Γ| = 1
    p.append(circle(cx, cy, R, fill="#f2fdf5", stroke=LINE, sw=2.0))
    p.append(line(cx - R, cy, cx + R, cy, color=LINE, sw=1.2)) # Дійсна вісь

    # Ключові точки
    # Z = 0 (коротке)
    p.append(circle(cx - R, cy, 4, fill=POS, stroke=POS))
    p.append(textbox(cx - R + 25, cy + 25, "Z = 0 (Γ = −1)", size=9, fill="#fff5f5", stroke=POS)[0])

    # Z = Z0 (узгоджено)
    p.append(circle(cx, cy, 4, fill=FIELD, stroke=FIELD))
    p.append(textbox(cx, cy - 20, "Z = Z₀ (Γ = 0)", size=10, fill="#ffffff", stroke=FIELD, bold=True)[0])

    # Z = \infty (холостий)
    p.append(circle(cx + R, cy, 4, fill=NEG, stroke=NEG))
    p.append(textbox(cx + R - 25, cy + 25, "Z = ∞ (Γ = +1)", size=9, fill="#f5f8ff", stroke=NEG)[0])

    # +jZ0 та -jZ0
    p.append(circle(cx, cy - R, 3, fill=INK, stroke=INK))
    p.append(textbox(cx, cy - R + 15, "+jZ₀", size=9, fill="#ffffff", stroke=LINE)[0])
    p.append(circle(cx, cy + R, 3, fill=INK, stroke=INK))
    p.append(textbox(cx, cy + R - 15, "-jZ₀", size=9, fill="#ffffff", stroke=LINE)[0])

    save_svg("mapping-smith.svg", render(W, H, p))


# ── Фігура 2: Анатомія сітки імпедансів ──────────────────────────────────────
def fig_anatomy_smith():
    W, H = 720, 560
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    cx, cy, R = 360, 280, 190
    p.append(textbox(W/2, 30, "Анатомія кругової діаграми Сміта: R-кола та X-дуги", size=14, fill="#ffffff", stroke=LINE, bold=True)[0])

    # Граничне коло r = 0
    p.append(circle(cx, cy, R, fill="#fdfdfd", stroke=LINE, sw=2.0))
    # Горизонтальна дійсна вісь (x = 0)
    p.append(line(cx - R, cy, cx + R, cy, color=LINE, sw=1.5))

    # R-кола
    r_list = [0.2, 0.5, 1.0, 2.0]
    for r_val in r_list:
        r_cx = cx + R * (r_val / (r_val + 1.0))
        r_rad = R / (r_val + 1.0)
        sw = 1.8 if r_val == 1.0 else 1.0
        col = COLOR_Z if r_val == 1.0 else COLOR_GRID
        p.append(circle(r_cx, cy, r_rad, fill="none", stroke=col, sw=sw))

    # Для X-дуг використовуємо дуги з обрізанням по межі |Γ|=1 щоб не виходити за полотно
    # Тонкі внутрішні дуги реактивності
    for x_val in [0.5, 1.0, 2.0, -0.5, -1.0, -2.0]:
        # Координати центрів обітнуті або умовні арки
        col = POS if x_val > 0 else NEG
        sw = 1.4 if abs(x_val) == 1.0 else 0.9
        d_str = ' stroke-dasharray="4,4"' if abs(x_val) != 1.0 else ''
        # Створимо дугу через path для акуратності в межах кола R
        # Для x = 1.0 дуга іде від (cx, cy-R) до (cx+R, cy)
        if x_val == 1.0:
            p.append('<path d="M %f,%f A %f,%f 0 0,1 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"/>' %
                     (cx, cy - R, R, R, cx + R, cy, col, sw))
        elif x_val == -1.0:
            p.append('<path d="M %f,%f A %f,%f 0 0,0 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"/>' %
                     (cx, cy + R, R, R, cx + R, cy, col, sw))
        elif x_val == 0.5:
            p.append('<path d="M %f,%f A %f,%f 0 0,1 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
                     (cx - R*0.6, cy - R*0.8, R*2, R*2, cx + R, cy, col, sw, d_str))
        elif x_val == -0.5:
            p.append('<path d="M %f,%f A %f,%f 0 0,0 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
                     (cx - R*0.6, cy + R*0.8, R*2, R*2, cx + R, cy, col, sw, d_str))
        elif x_val == 2.0:
            p.append('<path d="M %f,%f A %f,%f 0 0,1 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
                     (cx + R*0.6, cy - R*0.8, R*0.5, R*0.5, cx + R, cy, col, sw, d_str))
        elif x_val == -2.0:
            p.append('<path d="M %f,%f A %f,%f 0 0,0 %f,%f" fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
                     (cx + R*0.6, cy + R*0.8, R*0.5, R*0.5, cx + R, cy, col, sw, d_str))

    # Коло постійного КСХ (SWR = 2.0)
    swr_val = 2.0
    gamma_swr = (swr_val - 1.0) / (swr_val + 1.0)
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6,4"/>' % (cx, cy, R * gamma_swr, FIELD))
    p.append(circle(cx + R * gamma_swr, cy, 4, fill=FIELD, stroke=FIELD))
    p.append(textbox(cx + R * gamma_swr + 45, cy - 15, "r = SWR = 2.0", size=10, fill="#ffffff", stroke=FIELD, bold=True)[0])

    # Пояснювальні виноси
    p.append(textbox(130, 110, "Верхня півплощина:\nІндуктивна (+jX)\nСтрум відстає", size=10, fill="#fff5f5", stroke=POS, min_w=150)[0])
    p.append(textbox(130, 440, "Нижня півплощина:\nЄмнісна (-jX)\nСтрум випереджає", size=10, fill="#f5f8ff", stroke=NEG, min_w=150)[0])

    p.append(textbox(580, 110, "Коло r = 1.0\nПроходить через центр\n(Z = Z₀)", size=10, fill="#f2f5ff", stroke=COLOR_Z, min_w=160)[0])
    p.append(textbox(580, 440, "Зелене пунктирне коло:\nПостійний КСХ (SWR = 2:1)", size=10, fill="#f2fdf5", stroke=FIELD, min_w=170)[0])

    save_svg("anatomy-smith.svg", render(W, H, p))


# ── Фігура 3: Обертання вздовж лінії передачі ───────────────────────────────
def fig_line_rotation():
    W, H = 740, 500
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    cx, cy, R = 370, 250, 170
    p.append(textbox(W/2, 30, "Трансформація імпедансу вздовж лінії передачі", size=14, fill="#ffffff", stroke=LINE, bold=True)[0])

    # Граничне коло
    p.append(circle(cx, cy, R, fill="#fafbfc", stroke=LINE, sw=1.8))
    p.append(line(cx - R, cy, cx + R, cy, color=LINE, sw=1.2))

    # Коло КСХ для лінії без втрат
    g_rad = R * 0.45
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="5,4"/>' % (cx, cy, g_rad, COLOR_Z))

    # Початкова точка Z_L
    angle_deg = 45
    rad = math.radians(angle_deg)
    zl_x = cx + g_rad * math.cos(rad)
    zl_y = cy - g_rad * math.sin(rad)
    p.append(circle(zl_x, zl_y, 5, fill=POS, stroke=POS))
    p.append(textbox(zl_x + 60, zl_y - 15, "Z_L (Навантаження)", size=10, fill="#ffffff", stroke=POS, bold=True)[0])

    # Стрілка обертання
    rot_angle = math.radians(-45)
    rot_x = cx + g_rad * math.cos(rot_angle)
    rot_y = cy - g_rad * math.sin(rot_angle)
    p.append(arrow(zl_x, zl_y + 10, rot_x + 10, rot_y - 10, color=POS, sw=2.5))
    p.append(textbox(cx + g_rad + 65, cy, "Обертання ЗА годинниковою\n(До генератора)", size=10, fill="#ffffff", stroke=POS, bold=True)[0])

    # Точка lambda/4
    z_q_x = cx - g_rad * math.cos(rad)
    z_q_y = cy + g_rad * math.sin(rad)
    p.append(circle(z_q_x, z_q_y, 5, fill=NEG, stroke=NEG))
    p.append(textbox(z_q_x - 70, z_q_y + 20, "Z(l = λ/4) = Z₀²/Z_L\n(Інверсія імпедансу)", size=10, fill="#ffffff", stroke=NEG, bold=True)[0])

    # Спіраль втрат
    spiral_pts = []
    for deg in range(45, 45 + 540, 10):
        r_curr = g_rad * math.exp(-0.003 * (deg - 45))
        a_rad = math.radians(deg)
        sx = cx + r_curr * math.cos(a_rad)
        sy = cy - r_curr * math.sin(a_rad)
        spiral_pts.append((sx, sy))
    
    path_d = "M " + " L ".join("%.1f,%.1f" % pt for pt in spiral_pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' % (path_d, FIELD))
    p.append(textbox(cx, cy + 45, "Спіраль згасання в лінії з втратами", size=10, fill="#ffffff", stroke=FIELD, bold=True)[0])

    p.append(textbox(140, 90, "Повне коло (360° на діаграмі) =\nЗміщення на λ/2 вздовж лінії", size=10, fill="#fff5f5", stroke=POS, min_w=190)[0])
    p.append(textbox(600, 430, "Шкала WTG:\nWavelengths Toward Generator", size=10, fill="#f5f8ff", stroke=NEG, min_w=190)[0])

    save_svg("line-rotation.svg", render(W, H, p))


# ── Фігура 4: Суміщена ZY-діаграма (імпеданс + адмітанс) ─────────────────────
def fig_zy_overlay():
    W, H = 720, 520
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    cx, cy, R = 360, 260, 180
    p.append(textbox(W/2, 30, "Суміщена ZY-діаграма (Імпеданси + Адмітанси)", size=14, fill="#ffffff", stroke=LINE, bold=True)[0])

    # Граничне коло
    p.append(circle(cx, cy, R, fill="#fafbfc", stroke=LINE, sw=1.8))
    p.append(line(cx - R, cy, cx + R, cy, color=LINE, sw=1.2))

    # Z-кола (Сині)
    r_cx1 = cx + R * (1.0 / 2.0)
    p.append(circle(r_cx1, cy, R / 2.0, fill="none", stroke=COLOR_Z, sw=1.8))

    # Y-кола (Зелені)
    g_cx1 = cx - R * (1.0 / 2.0)
    p.append(circle(g_cx1, cy, R / 2.0, fill="none", stroke=COLOR_Y, sw=1.8))

    # Точка Z_A і Y_A
    za_x, za_y = cx + 60, cy - 70
    ya_x, ya_y = cx - 60, cy + 70

    p.append(line(za_x, za_y, ya_x, ya_y, color=POS, sw=1.5, dash="4,4"))
    p.append(circle(cx, cy, 4, fill=INK, stroke=INK))

    p.append(circle(za_x, za_y, 6, fill=COLOR_Z, stroke=COLOR_Z))
    p.append(textbox(za_x + 60, za_y - 20, "z = r + jx\n(Імпеданс)", size=10, fill="#ffffff", stroke=COLOR_Z, bold=True)[0])

    p.append(circle(ya_x, ya_y, 6, fill=COLOR_Y, stroke=COLOR_Y))
    p.append(textbox(ya_x - 40, ya_y - 20, "y = g + jb = 1/z\n(Адмітанс)", size=10, fill="#ffffff", stroke=COLOR_Y, bold=True)[0])

    # Виноси правил додавання
    p.append(textbox(150, 110, "Послідовні елементи (Z-сітка):\nR додається вздовж r-кіл\n+jX (L) — за стрілкою\n-jX (C) — проти стрілки", size=10, fill="#f2f5ff", stroke=COLOR_Z, min_w=200)[0])
    p.append(textbox(570, 410, "Паралельні елементи (Y-сітка):\nG додається вздовж g-кіл\n+jB (C) — за стрілкою\n-jB (L) — проти стрілки", size=10, fill="#f2fdf5", stroke=COLOR_Y, min_w=200)[0])

    save_svg("zy-overlay.svg", render(W, H, p))


# ── Фігура 5: Траєкторія узгодження L-мережею ────────────────────────────────
def fig_l_matching_path():
    W, H = 740, 540
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    cx, cy, R = 370, 270, 190
    p.append(textbox(W/2, 30, "Траєкторія узгодження L-мережею (Приклад 2.45 ГГц)", size=14, fill="#ffffff", stroke=LINE, bold=True)[0])

    # Граничне коло
    p.append(circle(cx, cy, R, fill="#fafbfc", stroke=LINE, sw=1.8))
    p.append(line(cx - R, cy, cx + R, cy, color=LINE, sw=1.2))

    # Ключові кола
    g_val = 0.4
    g_cx = cx - R * (g_val / (g_val + 1.0))
    g_rad = R / (g_val + 1.0)
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4,4"/>' % (g_cx, cy, g_rad, COLOR_Y))

    r_cx = cx + R * 0.5
    r_rad = R * 0.5
    p.append(circle(r_cx, cy, r_rad, fill="none", stroke=COLOR_Z, sw=1.8))

    # Точка 1: z_L
    pt1_x = cx + R * 0.0769
    pt1_y = cy - R * 0.6154
    p.append(circle(pt1_x, pt1_y, 6, fill=POS, stroke=POS))
    p.append(textbox(470, 90, "1. z_L = 0.5 + j1.0\n(y_L = 0.4 − j0.8)", size=10, fill="#fff5f5", stroke=POS, bold=True)[0])

    # Точка 2: Перетин
    pt2_x = cx + R * 0.27
    pt2_y = cy - R * 0.44
    p.append(circle(pt2_x, pt2_y, 6, fill=FIELD, stroke=FIELD))
    p.append(textbox(580, 160, "2. Перетин з r = 1.0\n(y_1 = 0.4 + j0.49)", size=10, fill="#ffffff", stroke=FIELD, bold=True)[0])

    # Точка 3: Центр
    pt3_x, pt3_y = cx, cy
    p.append(circle(pt3_x, pt3_y, 7, fill=COLOR_Z, stroke=COLOR_Z))
    p.append(textbox(270, 290, "3. Узгоджено!\n(z = 1.0 + j0)", size=10, fill="#ffffff", stroke=COLOR_Z, bold=True)[0])

    # Стрілки траєкторії
    p.append(arrow(pt1_x, pt1_y, pt2_x, pt2_y, color=FIELD, sw=2.5))
    p.append(textbox(600, 310, "Крок 1: Паралельний C\n(+jΔb = +1.29, C = 1.68 пФ)", size=9, fill="#f2fdf5", stroke=FIELD, bold=True)[0])

    p.append(arrow(pt2_x, pt2_y, pt3_x, pt3_y, color=COLOR_Z, sw=2.5))
    p.append(textbox(340, 200, "Крок 2: Послідовна L\n(+jΔx = +1.225, L = 3.98 нГн)", size=9, fill="#f2f5ff", stroke=COLOR_Z, bold=True)[0])

    p.append(textbox(150, 460, "Результат:\nПочатковий КСХ = 4.26:1\nПідсумковий КСХ = 1.00:1!", size=10, fill="#f2fdf5", stroke=FIELD, min_w=190)[0])

    save_svg("l-matching-path.svg", render(W, H, p))


if __name__ == "__main__":
    fig_mapping_smith()
    fig_anatomy_smith()
    fig_line_rotation()
    fig_zy_overlay()
    fig_l_matching_path()
