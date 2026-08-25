# -*- coding: utf-8 -*-
"""Фігури до теми «Абсолютно тверде тіло».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.0, head=8):
    """Дуга-стрілка для позначення обертання."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty)
    if L > 1e-6:
        tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


# ── Фігура 1: Шість ступенів вільностей твердого тіла ─────────────────────────
def fig_dof_six():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    # Заголовок
    f.append(text(W / 2, 32, "Шість незалежних ступенів вільностей твердого тіла", size=17, bold=True))

    # Лабораторна система відліку (Оси X, Y, Z)
    Ox, Oy = 160, 380
    f.append(arrow(Ox, Oy, Ox + 140, Oy, color=LINE, sw=2))
    f.append(text(Ox + 155, Oy + 5, "X", size=15, bold=True))
    
    f.append(arrow(Ox, Oy, Ox, Oy - 140, color=LINE, sw=2))
    f.append(text(Ox - 5, Oy - 150, "Z", size=15, bold=True))
    
    f.append(arrow(Ox, Oy, Ox - 80, Oy + 60, color=LINE, sw=2))
    f.append(text(Ox - 95, Oy + 75, "Y", size=15, bold=True))

    # Тіло довільної форми (контур)
    Cx, Cy = 520, 220
    body_path = ('<path d="M 380,200 C 400,120 540,110 640,160 C 720,200 700,320 620,360 '
                 'C 520,400 420,360 380,300 C 350,250 360,220 380,200 Z" '
                 'fill="#f4f6f8" stroke="%s" stroke-width="2.5"/>' % INK)
    f.append(body_path)

    # Радіус-вектор центру мас r_CM
    f.append(arrow(Ox, Oy, Cx, Cy, color=NEG, sw=2.5))
    f.append(textbox((Ox + Cx) / 2 - 20, (Oy + Cy) / 2 + 10, "r_CM (3 поступальні)", size=13, color=NEG, bold=True)[0])

    # Точка центру мас
    f.append(circle(Cx, Cy, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(Cx + 15, Cy - 12, "ЦМ (x, y, z)", size=13, bold=True, color=POS))

    # Зв'язані осі обертання навколо ЦМ
    # Вісь X'
    f.append(line(Cx - 60, Cy + 30, Cx + 120, Cy - 60, color=FIELD, sw=2, dash="4,3"))
    f.append(text(Cx + 135, Cy - 65, "X'", size=13, bold=True, color=FIELD))
    f.append(arc_arrow(Cx + 70, Cy - 35, 22, -40, 140, color=FIELD, sw=1.8))
    f.append(text(Cx + 95, Cy - 15, "ψ", size=13, italic=True, color=FIELD))

    # Вісь Y'
    f.append(line(Cx - 50, Cy - 80, Cx + 70, Cy + 110, color=FIELD, sw=2, dash="4,3"))
    f.append(text(Cx + 80, Cy + 120, "Y'", size=13, bold=True, color=FIELD))
    f.append(arc_arrow(Cx + 35, Cy + 55, 20, 20, 200, color=FIELD, sw=1.8))
    f.append(text(Cx + 60, Cy + 65, "θ", size=13, italic=True, color=FIELD))

    # Вісь Z'
    f.append(line(Cx, Cy + 90, Cx, Cy - 130, color=FIELD, sw=2, dash="4,3"))
    f.append(text(Cx, Cy - 140, "Z'", size=13, bold=True, color=FIELD))
    f.append(arc_arrow(Cx, Cy - 75, 24, 10, 190, color=FIELD, sw=1.8))
    f.append(text(Cx + 30, Cy - 85, "φ", size=13, italic=True, color=FIELD))

    # Пояснювальні картки внизу
    f.append(textbox(240, 440, "3 Поступальні координати:\nх_CM, y_CM, z_CM (позиція ЦМ)", size=12, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(600, 440, "3 Обертальні координати:\nφ, θ, ψ (кути Ойлера орієнтації)", size=12, fill="#eafaf1", stroke=FIELD)[0])

    render(os.path.join(IMG, "dof-six-rigid.svg"), W, H, "".join(f))


# ── Фігура 2: Теорема Шаля ──────────────────────────────────────────────────
def fig_chasles():
    W, H = 840, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 30, "Теорема Шаля: Переміщення = Поступальний рух + Обертання", size=17, bold=True))

    # Стан 1 (початкове положення)
    O1 = (180, 230)
    b1_path = ('<path d="M 120,220 C 130,160 210,150 250,190 C 280,220 260,290 210,310 '
               'C 160,320 110,280 120,220 Z" fill="#f4f6f8" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % MUTED)
    f.append(b1_path)
    f.append(circle(O1[0], O1[1], 5, fill=MUTED, stroke=INK, sw=1))
    f.append(text(O1[0] - 15, O1[1] - 10, "O₁", size=13, bold=True, color=MUTED))

    # Стан 2 (проміжний — після переносу)
    O2 = (440, 170)
    b2_path = ('<path d="M 380,160 C 390,100 470,90 510,130 C 540,160 520,230 470,250 '
               'C 420,260 370,220 380,160 Z" fill="#f4f6f8" stroke="%s" stroke-width="1.8" stroke-dasharray="2,2"/>' % NEG)
    f.append(b2_path)
    f.append(circle(O2[0], O2[1], 5, fill=NEG, stroke=INK, sw=1))
    f.append(text(O2[0] - 15, O2[1] - 10, "O₂", size=13, bold=True, color=NEG))

    # Вектор перенесення
    f.append(arrow(O1[0], O1[1], O2[0], O2[1], color=NEG, sw=2.5))
    f.append(textbox(310, 180, "Поступальне переміщення Δr", size=12, color=NEG, fill="#eaf0fd", stroke=NEG)[0])

    # Стан 3 (кінцеве положення — після повороту)
    O3 = (680, 240)
    # Повернутий контур тіла навколо O3
    b3_path = ('<path d="M 640,160 C 700,150 750,210 740,260 C 730,310 650,340 610,290 '
               'C 580,250 600,180 640,160 Z" fill="#eafaf1" stroke="%s" stroke-width="2.5"/>' % FIELD)
    f.append(b3_path)
    f.append(circle(O3[0], O3[1], 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(O3[0] + 15, O3[1] + 5, "O₃ (Полюс)", size=13, bold=True, color=POS))

    # Дуга повороту від стану 2 до стану 3
    f.append(arc_arrow(O2[0], O2[1], 110, -20, 45, color=FIELD, sw=2.2, head=9))
    f.append(textbox(600, 110, "Поворот на кут Δθ\nнавколо миттєвої осі", size=12, color=FIELD, fill="#eafaf1", stroke=FIELD)[0])

    # Пояснення
    f.append(textbox(W / 2, 390, "Довільне переміщення твердого тіла = сума паралельного переносу полюса O та обертання навколо нього", size=13, bold=True, fill=FILL, stroke=LINE)[0])

    render(os.path.join(IMG, "chasles-theorem.svg"), W, H, "".join(f))


# ── Фігура 3: Поле швидкостей і розподіл Ейлера ───────────────────────────────
def fig_euler_velocity():
    W, H = 840, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 30, "Поле швидкостей Ейлера: v_P = v_O + ω × r_PO", size=17, bold=True))

    # Контур тіла
    body_path = ('<path d="M 220,180 C 260,100 500,80 680,150 C 760,220 740,360 620,400 '
                 'C 450,430 250,380 200,280 C 180,240 190,200 220,180 Z" '
                 'fill="#f4f6f8" stroke="%s" stroke-width="2.5"/>' % INK)
    f.append(body_path)

    # Полюс O
    Ox, Oy = 340, 260
    f.append(circle(Ox, Oy, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(Ox - 25, Oy + 5, "Полюс O", size=14, bold=True, color=POS))

    # Швидкість полюса v_O
    f.append(arrow(Ox, Oy, Ox + 100, Oy - 40, color=NEG, sw=2.5))
    f.append(text(Ox + 110, Oy - 45, "v_O", size=14, bold=True, italic=True, color=NEG))

    # Вектор кутової швидкості ω через полюс
    f.append(arrow(Ox, Oy + 80, Ox, Oy - 140, color=FIELD, sw=2.8))
    f.append(text(Ox + 15, Oy - 145, "ω (глобальний вектор)", size=14, bold=True, italic=True, color=FIELD))
    f.append(arc_arrow(Ox, Oy - 80, 24, 20, 210, color=FIELD, sw=2))

    # Довільна точка P
    Px, Py = 580, 200
    f.append(circle(Px, Py, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(Px + 15, Py - 10, "Точка P", size=14, bold=True))

    # Радіус-вектор r_PO
    f.append(arrow(Ox, Oy, Px, Py, color=LINE, sw=2))
    f.append(textbox((Ox + Px) / 2, (Oy + Py) / 2 + 20, "r_PO", size=13)[0])

    # Компоненти швидкості в точці P
    # 1. Поступальна v_O
    f.append(arrow(Px, Py, Px + 100, Py - 40, color=NEG, sw=2))
    f.append(text(Px + 105, Py - 45, "v_O", size=13, italic=True, color=NEG))

    # 2. Обертальна v_rot = ω × r_PO
    # Перпендикулярно до r_PO
    f.append(arrow(Px, Py, Px + 40, Py + 90, color=FIELD, sw=2.2))
    f.append(text(Px + 50, Py + 100, "ω × r_PO", size=13, bold=True, italic=True, color=FIELD))

    # 3. Сумарна швидкість v_P
    f.append(arrow(Px, Py, Px + 140, Py + 50, color=POS, sw=3))
    f.append(textbox(Px + 150, Py + 90, "v_P (повна швидкість)", size=13, bold=True, color=POS, fill="#fdecea", stroke=POS)[0])

    # Пунктирний паралелограм суми швидкостей
    f.append(line(Px + 100, Py - 40, Px + 140, Py + 50, color=MUTED, sw=1.5, dash="2,2"))
    f.append(line(Px + 40, Py + 90, Px + 140, Py + 50, color=MUTED, sw=1.5, dash="2,2"))

    render(os.path.join(IMG, "euler-velocity-field.svg"), W, H, "".join(f))


# ── Фігура 4: Кути Ейлера ────────────────────────────────────────────────────
def fig_euler_angles():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 30, "Кути Ейлера (φ, θ, ψ): зв'язок лабораторної та зв'язаної систем", size=17, bold=True))

    Ox, Oy = 420, 260

    # Лабораторна система (xyz)
    f.append(arrow(Ox, Oy, Ox + 180, Oy, color=MUTED, sw=1.8))
    f.append(text(Ox + 195, Oy + 5, "x (лабораторна)", size=13, bold=True, color=MUTED))

    f.append(arrow(Ox, Oy, Ox - 120, Oy + 100, color=MUTED, sw=1.8))
    f.append(text(Ox - 135, Oy + 115, "y", size=13, bold=True, color=MUTED))

    f.append(arrow(Ox, Oy, Ox, Oy - 180, color=MUTED, sw=1.8))
    f.append(text(Ox, Oy - 195, "z (вертикаль)", size=13, bold=True, color=MUTED))

    # Лінія вузлів N (перетин площин xy та x'y')
    Nx, Ny = Ox + 140, Oy + 60
    f.append(line(Ox - 140, Oy - 60, Nx, Ny, color=LINE, sw=2, dash="5,3"))
    f.append(text(Nx + 20, Ny + 10, "N (лінія вузлів)", size=13, bold=True, color=INK))

    # Зв'язана система тіла (x'y'z')
    # Зв'язана вісь z'
    Zbx, Zby = Ox + 70, Oy - 160
    f.append(arrow(Ox, Oy, Zbx, Zby, color=POS, sw=2.5))
    f.append(text(Zbx + 15, Zby - 5, "z' (вісь симетрії тіла)", size=14, bold=True, color=POS))

    # Зв'язана вісь x'
    Xbx, Xby = Ox + 160, Oy - 20
    f.append(arrow(Ox, Oy, Xbx, Xby, color=FIELD, sw=2.2))
    f.append(text(Xbx + 15, Xby, "x'", size=13, bold=True, color=FIELD))

    # Зв'язана вісь y'
    Ybx, Yby = Ox - 60, Oy + 140
    f.append(arrow(Ox, Oy, Ybx, Yby, color=FIELD, sw=2.2))
    f.append(text(Ybx - 15, Yby + 10, "y'", size=13, bold=True, color=FIELD))

    # Кути:
    # 1. φ (Прецесія) — кут між x та N у площині xy
    f.append(arc_arrow(Ox, Oy, 70, 0, -22, color=NEG, sw=2))
    f.append(text(Ox + 90, Oy + 25, "φ (прецесія)", size=13, bold=True, color=NEG))

    # 2. θ (Нутація) — кут між z та z'
    f.append(arc_arrow(Ox, Oy, 80, 90, 66, color=POS, sw=2))
    f.append(text(Ox + 35, Oy - 100, "θ (нутація)", size=13, bold=True, color=POS))

    # 3. ψ (Власне обертання) — кут між N та x' у площині тіла
    f.append(arc_arrow(Ox, Oy, 90, -22, 8, color=FIELD, sw=2))
    f.append(text(Ox + 130, Oy + 10, "ψ (обертання)", size=13, bold=True, color=FIELD))

    # Легенда кутів внизу
    f.append(textbox(200, 440, "1. φ: Поворот навколо z до лінії вузлів N", size=12, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(430, 440, "2. θ: Нахил осі z' відносно z", size=12, fill="#fdecea", stroke=POS)[0])
    f.append(textbox(660, 440, "3. ψ: Поворот навколо z' від N до x'", size=12, fill="#eafaf1", stroke=FIELD)[0])

    render(os.path.join(IMG, "euler-angles.svg"), W, H, "".join(f))


# ── Фігура 5: Нестійкість обертання навколо проміжної осі ───────────────────────
def fig_intermediate_axis():
    W, H = 840, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 30, "Теорема про проміжну вісь (Ефект Джанібекова)", size=17, bold=True))

    # Три панелі для трьох головних осей інерції
    # 1. Найменший момент інерції I₁ (Стійке)
    cx1 = 160
    f.append(rect(cx1 - 110, 70, 220, 310, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    f.append(text(cx1, 95, "Ось 1: Малий I₁", size=15, bold=True, color=POS))
    f.append(text(cx1, 118, "(Витягнуте тіло)", size=12, color=MUTED))
    
    # Витягнутий прямокутник
    f.append(rect(cx1 - 25, 160, 50, 140, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(arrow(cx1, 320, cx1, 130, color=POS, sw=2.5))
    f.append(arc_arrow(cx1, 230, 35, 10, 200, color=POS, sw=2))
    f.append(text(cx1, 345, "ω₁, L₁", size=14, bold=True, color=POS))
    f.append(textbox(cx1, 365, "СТІЙКЕ обертання", size=12, bold=True, color=POS, fill="#eafaf1", stroke=POS)[0])

    # 2. Проміжний момент інерції I₂ (Нестійке)
    cx2 = 420
    f.append(rect(cx2 - 110, 70, 220, 310, fill="#fdecea", stroke=POS, sw=2, rx=8))
    f.append(text(cx2, 95, "Ось 2: Проміжний I₂", size=15, bold=True, color=POS))
    f.append(text(cx2, 118, "(I₁ < I₂ < I₃)", size=12, color=POS))
    
    # Прямокутник плашмя з хвилястою траєкторією траєкторії перекидання
    f.append(rect(cx2 - 50, 200, 100, 60, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(arrow(cx2, 320, cx2, 130, color=POS, sw=2.5))
    
    # Спіральне перекидання
    spiral_path = ('<path d="M 420,290 C 470,270 470,220 420,210 C 370,200 370,160 420,140" '
                   'fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    f.append(spiral_path)
    f.append(text(cx2 + 55, 150, "Перекидання!", size=13, bold=True, color=POS))
    f.append(textbox(cx2, 365, "НЕСТІЙКЕ (перекидання 180°)", size=12, bold=True, color=POS, fill="#fdecea", stroke=POS)[0])

    # 3. Найбільший момент інерції I₃ (Стійке)
    cx3 = 680
    f.append(rect(cx3 - 110, 70, 220, 310, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    f.append(text(cx3, 95, "Ось 3: Великий I₃", size=15, bold=True, color=FIELD))
    f.append(text(cx3, 118, "(Плоский диск)", size=12, color=MUTED))
    
    # Широкий плоский диск
    f.append(rect(cx3 - 70, 210, 140, 40, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(arrow(cx3, 320, cx3, 130, color=FIELD, sw=2.5))
    f.append(arc_arrow(cx3, 230, 45, 10, 200, color=FIELD, sw=2))
    f.append(text(cx3, 345, "ω₃, L₃", size=14, bold=True, color=FIELD))
    f.append(textbox(cx3, 365, "СТІЙКЕ обертання", size=12, bold=True, color=FIELD, fill="#eafaf1", stroke=FIELD)[0])

    # Підпис під усім графіком
    f.append(textbox(W / 2, 415, "Обертання навколо осі з найменшим (I₁) та найбільшим (I₃) моментом інерції стійке; навколо проміжної (I₂) — нестійке", size=12, bold=True)[0])

    render(os.path.join(IMG, "intermediate-axis-theorem.svg"), W, H, "".join(f))


if __name__ == "__main__":
    fig_dof_six()
    fig_chasles()
    fig_euler_velocity()
    fig_euler_angles()
    fig_intermediate_axis()
    print("Всі фігури успішно згенеровано в ./img/")
