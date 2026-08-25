# -*- coding: utf-8 -*-
"""Фігури до теми «Підкова Смейла».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

H0_COLOR = "#2457d6"    # Смуга H0 — холодне синє
H1_COLOR = "#c0392b"    # Смуга H1 — гаряче червоне
STRETCH_COLOR = "#27ae60" # Зона розтягування/згинання — зелене
GRID_COLOR = "#e2e8f0"

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))

# ── Фігура 1: Геометричне перетворення підкови Смейла ────────────────────────
def fig_horseshoe_geometry():
    W, H = 940, 390
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Геометричний механізм відображення підкови Смейла", size=16, bold=True))

    # Стадія 1: Початковий квадрат S з горизонтальними смугами H0 та H1
    x1, y1 = 40, 70
    s_size = 180
    frags.append(rect(x1, y1, s_size, s_size, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(x1 + s_size/2, y1 - 12, "1. Квадрат S", size=13, bold=True))

    # Смуга H0 (нижня)
    h0_y = y1 + s_size * 0.7
    h0_h = s_size * 0.25
    frags.append(rect(x1, h0_y, s_size, h0_h, fill="#eaf0fd", stroke=H0_COLOR, sw=1.8))
    frags.append(text(x1 + s_size/2, h0_y + h0_h/2 + 4, "H₀", size=13, color=H0_COLOR, bold=True))

    # Смуга H1 (верхня)
    h1_y = y1 + s_size * 0.05
    h1_h = s_size * 0.25
    frags.append(rect(x1, h1_y, s_size, h1_h, fill="#fdecea", stroke=H1_COLOR, sw=1.8))
    frags.append(text(x1 + s_size/2, h1_y + h1_h/2 + 4, "H₁", size=13, color=H1_COLOR, bold=True))

    # Стрілка переходу 1 -> 2
    frags.append(arrow(x1 + s_size + 15, y1 + s_size/2, x1 + s_size + 45, y1 + s_size/2, color=INK, sw=2))
    frags.append(text(x1 + s_size + 30, y1 + s_size/2 - 12, "Стискання/Розтяг", size=11, color=MUTED))

    # Стадія 2: Стиснута по горизонталі та розтягнута по вертикалі полоса
    x2, y2 = 280, 50
    w2, h2 = 55, 260
    frags.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke=MUTED, sw=1.5))
    frags.append(text(x2 + w2/2, y2 - 12, "2. Розтяг і стиск", size=13, bold=True))

    # Стиснуті H0 та H1
    frags.append(rect(x2, y2 + h2*0.7, w2, h2*0.25, fill="#eaf0fd", stroke=H0_COLOR, sw=1.8))
    frags.append(text(x2 + w2/2, y2 + h2*0.825 + 4, "H₀", size=12, color=H0_COLOR, bold=True))

    frags.append(rect(x2, y2 + h2*0.05, w2, h2*0.25, fill="#fdecea", stroke=H1_COLOR, sw=1.8))
    frags.append(text(x2 + w2/2, y2 + h2*0.175 + 4, "H₁", size=12, color=H1_COLOR, bold=True))

    # Стрілка переходу 2 -> 3
    frags.append(arrow(x2 + w2 + 15, y1 + s_size/2, x2 + w2 + 45, y1 + s_size/2, color=INK, sw=2))
    frags.append(text(x2 + w2 + 30, y1 + s_size/2 - 12, "Згинання", size=11, color=MUTED))

    # Стадія 3: Зігнута підкова
    x3, y3 = 450, 70
    frags.append(text(x3 + 70, y3 - 12, "3. Підкова f(S)", size=13, bold=True))
    
    # Малюємо підкову лініями та дугами
    # Ліва вертикальна гілка (H0)
    frags.append(rect(x3, y3 + 40, 45, 140, fill="#eaf0fd", stroke=H0_COLOR, sw=1.8))
    frags.append(text(x3 + 22.5, y3 + 110, "f(H₀)", size=12, color=H0_COLOR, bold=True))

    # Права вертикальна гілка (H1)
    frags.append(rect(x3 + 95, y3 + 40, 45, 140, fill="#fdecea", stroke=H1_COLOR, sw=1.8))
    frags.append(text(x3 + 117.5, y3 + 110, "f(H₁)", size=12, color=H1_COLOR, bold=True))

    # Верхня дуга підкови
    arc_d = f"M {x3} {y3+40} A 70 70 0 0 1 {x3+140} {y3+40} L {x3+95} {y3+40} A 25 25 0 0 0 {x3+45} {y3+40} Z"
    frags.append(path(arc_d, fill="#f4f6f8", stroke=INK, sw=1.8))

    # Стрілка переходу 3 -> 4
    frags.append(arrow(x3 + 155, y1 + s_size/2, x3 + 185, y1 + s_size/2, color=INK, sw=2))
    frags.append(text(x3 + 170, y1 + s_size/2 - 12, "Накладання", size=11, color=MUTED))

    # Стадія 4: Накладання підкови f(S) на початковий квадрат S
    x4, y4 = 700, 70
    frags.append(text(x4 + s_size/2, y4 - 12, "4. Перетин f(S) ∩ S", size=13, bold=True))
    frags.append(rect(x4, y4, s_size, s_size, fill="#ffffff", stroke=INK, sw=2))

    # Вертикальна смуга V0 (перетин f(H0) і S)
    v0_x = x4 + s_size * 0.1
    v0_w = s_size * 0.25
    frags.append(rect(v0_x, y4, v0_w, s_size, fill="#eaf0fd", stroke=H0_COLOR, sw=1.8))
    frags.append(text(v0_x + v0_w/2, y4 + s_size/2, "V₀", size=14, color=H0_COLOR, bold=True))

    # Вертикальна смуга V1 (перетин f(H1) і S)
    v1_x = x4 + s_size * 0.65
    v1_w = s_size * 0.25
    frags.append(rect(v1_x, y4, v1_w, s_size, fill="#fdecea", stroke=H1_COLOR, sw=1.8))
    frags.append(text(v1_x + v1_w/2, y4 + s_size/2, "V₁", size=14, color=H1_COLOR, bold=True))

    # Закупорений купол підкови поза квадратом
    arc_d4 = f"M {v0_x} {y4} A 65 65 0 0 1 {v1_x+v1_w} {y4} L {v1_x} {y4} A 20 20 0 0 0 {v0_x+v0_w} {y4} Z"
    frags.append(path(arc_d4, fill="#f4f6f8", stroke=INK, sw=1.5, dash="3,3"))

    # Пояснювальний підпис унизу
    tb, tw, th = textbox(W/2, 345, 
                         "Горизонтальні смуги H₀ та H₁ під дією відображення стискаються по X, розтягуються по Y та переходять у вертикальні смуги V₀ = f(H₀) ∩ S і V₁ = f(H₁) ∩ S",
                         size=12.5, pad=8, fill="#f8fafc", stroke=MUTED, sw=1)
    frags.append(tb)

    return render(os.path.join(IMG, 'horseshoe-mapping-geometry.svg'), W, H, *frags)


# ── Фігура 2: Утворення фракталу Кантора при ітераціях ───────────────────────
def fig_symbolic_cantor():
    W, H = 940, 390
    frags = []

    frags.append(text(W / 2, 28, "Фрактальна структура інваріантної множини (Кантор × Кантор)", size=16, bold=True))

    # Панель А: Перетин 1-ї прямої та зворотної ітерацій (4 квадратики)
    x1, y1 = 50, 70
    sz = 240
    frags.append(rect(x1, y1, sz, sz, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(x1 + sz/2, y1 - 12, "Перша ітерація: S ∩ f(S) ∩ f⁻¹(S)", size=13, bold=True))

    # Горизонтальні смуги H0, H1 (від f^-1)
    h0_y, h_w = y1 + sz*0.65, sz*0.25
    h1_y = y1 + sz*0.1
    frags.append(rect(x1, h0_y, sz, h_w, fill="#f4f6f8", stroke=MUTED, sw=1))
    frags.append(rect(x1, h1_y, sz, h_w, fill="#f4f6f8", stroke=MUTED, sw=1))

    # Вертикальні смуги V0, V1 (від f)
    v0_x, v_w = x1 + sz*0.1, sz*0.25
    v1_x = x1 + sz*0.65
    frags.append(rect(v0_x, y1, v_w, sz, fill="#f4f6f8", stroke=MUTED, sw=1))
    frags.append(rect(v1_x, y1, v_w, sz, fill="#f4f6f8", stroke=MUTED, sw=1))

    # 4 квадрати перетину H_i ∩ V_j
    intersections = [
        (v0_x, h0_y, "00", H0_COLOR),
        (v1_x, h0_y, "01", POS),
        (v0_x, h1_y, "10", FIELD),
        (v1_x, h1_y, "11", H1_COLOR)
    ]
    for ix, iy, code, col in intersections:
        frags.append(rect(ix, iy, v_w, h_w, fill="#ffffff", stroke=col, sw=2))
        frags.append(text(ix + v_w/2, iy + h_w/2 + 4, code, size=13, color=col, bold=True))

    # Пояснення до коду символів збоку від першої панелі
    frags.append(text(x1 + sz + 25, y1 + 50, "Кодування орбіт:", size=12, bold=True, anchor="start"))
    frags.append(text(x1 + sz + 25, y1 + 75, "Код (s₋₁, s₀) визначає,", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(x1 + sz + 25, y1 + 95, "де точка була вчора", size=11.5, color=MUTED, anchor="start"))
    frags.append(text(x1 + sz + 25, y1 + 115, "і де вона знаходиться сьогодні.", size=11.5, color=MUTED, anchor="start"))

    # Стрілка до другої панелі
    frags.append(arrow(x1 + sz + 155, y1 + sz/2, x1 + sz + 195, y1 + sz/2, color=INK, sw=2))

    # Панель Б: Друга ітерація (16 прямокутників)
    x2, y2 = 530, 70
    frags.append(rect(x2, y2, sz, sz, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(x2 + sz/2, y2 - 12, "Друга ітерація: 16 областей 4-символьних кодових слів", size=13, bold=True))

    # 4 подрібнені горизонтальні смуги
    h_sub = [y2 + sz*0.1, y2 + sz*0.26, y2 + sz*0.65, y2 + sz*0.81]
    sub_h = sz * 0.09
    
    # 4 подрібнені вертикальні смуги
    v_sub = [x2 + sz*0.1, x2 + sz*0.26, x2 + sz*0.65, x2 + sz*0.81]
    sub_w = sz * 0.09

    for vx in v_sub:
        for hy in h_sub:
            frags.append(rect(vx, hy, sub_w, sub_h, fill="#eaf0fd", stroke=H0_COLOR, sw=1.2))

    # Додаткові покажчики Канторових множин
    frags.append(arrow(x2 - 15, y2 + sz*0.15, x2 - 2, y2 + sz*0.15, color=H1_COLOR, sw=1.5))
    frags.append(arrow(x2 - 15, y2 + sz*0.73, x2 - 2, y2 + sz*0.73, color=H0_COLOR, sw=1.5))
    frags.append(text(x2 - 20, y2 + sz/2, "Кантор Y", size=11, color=MUTED, anchor="end"))

    frags.append(arrow(x2 + sz*0.18, y2 + sz + 15, x2 + sz*0.18, y2 + sz + 2, color=H0_COLOR, sw=1.5))
    frags.append(arrow(x2 + sz*0.73, y2 + sz + 15, x2 + sz*0.73, y2 + sz + 2, color=H1_COLOR, sw=1.5))
    frags.append(text(x2 + sz/2, y2 + sz + 30, "Кантор X", size=11, color=MUTED))

    # Нижній текст
    tb, tw, th = textbox(W/2, 348,
                         "Граничний інваріантний набір Λ є прямим добутком двох канторових множин. Динаміка на ньому еквівалентна зсуву Бернуллі.",
                         size=12.5, pad=8, fill="#f8fafc", stroke=MUTED, sw=1)
    frags.append(tb)

    return render(os.path.join(IMG, 'symbolic-dynamics-cantor.svg'), W, H, *frags)


# ── Фігура 3: Трансверсальна гомоклінічна плутанина ──────────────────────────
def fig_homoclinic_tangle():
    W, H = 940, 410
    frags = []

    frags.append(text(W / 2, 28, "Трансверсальний перетин стійкого та нестійкого многовидів (Гомоклінічна плутанина)", size=16, bold=True))

    cx, cy = 200, 220
    frags.append(circle(cx, cy, 6, fill=INK, stroke=INK))
    frags.append(text(cx - 15, cy + 20, "Сідлова точка p", size=13, bold=True, anchor="end"))

    # Осі / локальні многовиди
    frags.append(line(cx - 140, cy, cx + 550, cy, color="#cbd5e1", sw=1.2, dash="4,4"))
    frags.append(line(cx, cy - 150, cx, cy + 140, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Стійкий многовид W^s(p) — горизонтальна вісь X (синє)
    frags.append(line(cx, cy, cx + 640, cy, color=NEG, sw=2.5))
    frags.append(text(cx + 630, cy - 12, "Wˢ(p) (стійкий многовид)", size=13, color=NEG, bold=True, anchor="end"))

    # Первинна гомоклінічна точка q0
    q0_x = cx + 220
    frags.append(circle(q0_x, cy, 5, fill=POS, stroke=POS))
    frags.append(text(q0_x, cy + 25, "Гомоклінічна точка q₀", size=12.5, color=POS, bold=True))

    # Наступна гомоклінічна точка q1
    q1_x = cx + 380
    frags.append(circle(q1_x, cy, 4, fill=POS, stroke=POS))
    frags.append(text(q1_x, cy + 25, "q₁ = f(q₀)", size=11.5, color=POS))

    # Третя гомоклінічна точка q2
    q2_x = cx + 490
    frags.append(circle(q2_x, cy, 3.5, fill=POS, stroke=POS))
    frags.append(text(q2_x, cy + 25, "q₂ = f²(q₀)", size=11, color=POS))

    # Нестійкий многовид W^u(p) — закручена змійка (червоне)
    # Зростаючі за амплітудою осциляції, що перетинають W^s(p)
    tangle_path = (f"M {cx} {cy} "
                   f"C {cx+40} {cy-120}, {cx+100} {cy-140}, {cx+140} {cy-70} "
                   f"C {cx+160} {cy-20}, {cx+180} {cy+100}, {q0_x} {cy} "
                   f"C {cx+260} {cy-160}, {cx+320} {cy-180}, {cx+350} {cy-60} "
                   f"C {cx+360} {cy-10}, {cx+370} {cy+130}, {q1_x} {cy} "
                   f"C {cx+420} {cy-180}, {cx+460} {cy-190}, {cx+480} {cy-40} "
                   f"C {cx+485} {cy-10}, {cx+488} {cy+110}, {q2_x} {cy} "
                   f"C {cx+520} {cy-170}, {cx+550} {cy-170}, {cx+570} {cy}")

    frags.append(path(tangle_path, fill="none", stroke=POS, sw=2))
    tb_u, _, _ = textbox(360, 55, "Wᵘ(p) (нестійкий многовид)", size=12, pad=5, fill="#ffffff", stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(tb_u)

    tb_stretch, _, _ = textbox(660, 55, "Петельне розтягнення фазових об'ємів", size=11, pad=5, fill="#ffffff", stroke=MUTED, sw=1, color=MUTED)
    frags.append(tb_stretch)

    # Легенда у верхньому лівому кутку
    frags.append(rect(35, 45, 195, 75, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(132, 63, "Гомоклінічна структура", size=11.5, bold=True))
    frags.append(line(45, 80, 75, 80, color=NEG, sw=2))
    frags.append(text(82, 84, "Wˢ(p) — стискання", size=10.5, color=INK, anchor="start"))
    frags.append(line(45, 100, 75, 100, color=POS, sw=2))
    frags.append(text(82, 104, "Wᵘ(p) — розтягнення", size=10.5, color=INK, anchor="start"))

    # Пояснення теореми Смейла-Біркгофа
    tb, tw, th = textbox(W/2, 368,
                         "Теорема Смейла — Біркгофа: Наявність хоча б однієї трансверсальної гомоклінічної точки тягне за собою існування підкови Смейла та хаотичної динаміки.",
                         size=12, pad=8, fill="#f8fafc", stroke=MUTED, sw=1)
    frags.append(tb)

    return render(os.path.join(IMG, 'homoclinic-tangle-mesh.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_horseshoe_geometry()
    fig_symbolic_cantor()
    fig_homoclinic_tangle()
    print("Згенеровано фігури в ./img/")
