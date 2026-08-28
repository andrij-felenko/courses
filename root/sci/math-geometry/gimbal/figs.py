# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def dot(x, y, r=4.5, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, color)


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


def arcpts(cx, cy, r, a0, a1, n=60):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ───────────────────────────────────────────────────────────────────────────
# Фігура 1: Кінематичний ланцюг підвісу
# ───────────────────────────────────────────────────────────────────────────
def fig_kinematic_chain():
    W, H = 960, 440
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Кінематичний ланцюг триосьового підвісу (Z-Y-X)", size=16, bold=True))

    # Чотири послідовні системи координат / кільця
    nodes = [
        (130, 140, "Корпус F_b", "Базова рамка\n(апарат)", "#e8f4fd", NEG),
        (370, 140, "Кільце рискання F_1", "Обертання навколо Z_b\nКут ψ (Yaw)", "#eef9e8", FIELD),
        (610, 140, "Кільце тангажу F_2", "Обертання навколо Y_1\nКут θ (Pitch)", "#fff8e7", "#d35400"),
        (840, 140, "Платформа крену F_3", "Обертання навколо X_2\nКут φ (Roll & Камера)", "#fde8e8", POS),
    ]

    for cx, cy, title, desc, fcol, scol in nodes:
        b, bw, bh = textbox(cx, cy, desc, size=12, pad=8, fill=fcol, stroke=scol, sw=1.8, min_w=170)
        frags.append(b)
        frags.append(text(cx, cy - bh / 2 - 12, title, size=13, bold=True, color=scol))

    # Стрілки між вузлами
    trans = [
        (225, 140, 275, 140, "R_z(ψ)", FIELD),
        (465, 140, 515, 140, "R_y(θ)", "#d35400"),
        (705, 140, 745, 140, "R_x(φ)", POS),
    ]
    for x1, y1, x2, y2, lbl, col in trans:
        frags.append(arrow(x1, y1, x2, y2, color=col, sw=2.2))
        frags.append(text((x1 + x2) / 2, y1 - 12, lbl, size=12, bold=True, color=col))

    # Нижній блок: Матрична композиція та геометрія осей
    cy_bot = 310
    b_mat, _, _ = textbox(W / 2, cy_bot,
                          "Результуюча орієнтація корисного навантаження відносно корпусу:\n"
                          "R_g = R_z(ψ) · R_y(θ) · R_x(φ) ∈ SO(3)\n"
                          "Абсолютна орієнтація камери у світі:  R_cam = R_body · R_g",
                          size=13, pad=12, fill="#f8fafc", stroke=LINE, sw=1.5, min_w=620)
    frags.append(b_mat)

    # Підписи осей внизу
    frags.append(text(W / 2, 395,
                      "Вкладені шарніри реалізують послідовні внутрішні повороти (intrinsic): кожна вісь обертається разом із попереднім кільцем",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "gimbal-kinematic-chain.svg"), W, H, *frags,
           title="Кінематичний ланцюг триосьового підвісу")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 2: Складання рамок (Gimbal Lock)
# ───────────────────────────────────────────────────────────────────────────
def fig_gimbal_lock():
    W, H = 960, 440
    frags = []

    frags.append(text(W / 2, 28, "Геометрія карданового замка (Gimbal Lock) при тангажі θ = ±90°", size=16, bold=True))

    # Ліва панель: Нормальний стан θ = 0°
    cx1 = 250
    frags.append(text(cx1, 65, "Нормальний стан (θ = 0°): 3 DOF", size=15, bold=True, color=FIELD))

    # 3 перпендикулярні осі
    y_cen = 175
    frags.append(arrow(cx1, y_cen, cx1, y_cen - 80, color=FIELD, sw=2.5))
    frags.append(text(cx1 + 12, y_cen - 70, "Z_yaw (зовнішня)", size=12, bold=True, color=FIELD, anchor="start"))

    frags.append(arrow(cx1, y_cen, cx1 + 90, y_cen + 30, color="#d35400", sw=2.5))
    frags.append(text(cx1 + 95, y_cen + 35, "Y_pitch (середня)", size=12, bold=True, color="#d35400", anchor="start"))

    frags.append(arrow(cx1, y_cen, cx1 - 80, y_cen + 40, color=POS, sw=2.5))
    frags.append(text(cx1 - 85, y_cen + 45, "X_roll (внутрішня)", size=12, bold=True, color=POS, anchor="end"))

    frags.append(dot(cx1, y_cen, 5, INK))

    b1, _, _ = textbox(cx1, 320,
                       "Осі Z_yaw, Y_pitch, X_roll\n"
                       "взаємно перпендикулярні.\n"
                       "Система покриває повний\n"
                       "тривимірний простір обертань.",
                       size=12, pad=8, fill="#f4faf4", stroke=FIELD, min_w=240)
    frags.append(b1)

    # Розділювач
    frags.append(line(W / 2, 50, W / 2, 380, color=MUTED, sw=1.2, dash="4 4"))

    # Права панель: Gimbal Lock при θ = +90°
    cx2 = 710
    frags.append(text(cx2, 65, "Карданів замок (θ = +90°): Втрата 1 DOF", size=15, bold=True, color=POS))

    # Осі: Z_yaw і X_roll стають на одну лінію!
    frags.append(arrow(cx2 - 12, y_cen + 20, cx2 - 12, y_cen - 80, color=FIELD, sw=2.5))
    frags.append(text(cx2 - 18, y_cen - 70, "Z_yaw (зовнішня)", size=12, bold=True, color=FIELD, anchor="end"))

    frags.append(arrow(cx2 + 12, y_cen + 20, cx2 + 12, y_cen - 80, color=POS, sw=2.5))
    frags.append(text(cx2 + 18, y_cen - 70, "X_roll (повернута вгору)", size=12, bold=True, color=POS, anchor="start"))

    frags.append(arrow(cx2, y_cen, cx2 + 90, y_cen + 30, color="#d35400", sw=2.5))
    frags.append(text(cx2 + 95, y_cen + 35, "Y_pitch", size=12, bold=True, color="#d35400", anchor="start"))

    frags.append(dot(cx2, y_cen, 5, INK))

    # Позначення блокування
    frags.append(line(cx2 - 70, y_cen + 40, cx2 - 20, y_cen + 40, color=MUTED, sw=1.5, dash="3 3"))
    frags.append(text(cx2 - 75, y_cen + 43, "Втрачена вісь (немає мотора)", size=11, color=POS, anchor="end", bold=True))

    b2, _, _ = textbox(cx2, 320,
                       "Вісь крену X_roll збіглася з Z_yaw.\n"
                       "Обертання ψ та φ діють навколо однієї прямої.\n"
                       "Підвіс не може парирувати рух навколо\n"
                       "поперечної осі. det(J) = cos(θ) = 0.",
                       size=12, pad=8, fill="#fdf2f2", stroke=POS, min_w=280)
    frags.append(b2)

    frags.append(text(W / 2, 410,
                      "При вирівнюванні зовнішньої та внутрішньої осей тривісний підвіс втрачає один ступінь вільності у просторі",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "gimbal-lock-singularity.svg"), W, H, *frags,
           title="Геометрія карданового замка")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 3: Чотириосьовий підвіс (Redundant Gimbal)
# ───────────────────────────────────────────────────────────────────────────
def fig_four_axis_gimbal():
    W, H = 960, 420
    frags = []

    frags.append(text(W / 2, 28, "Чотириосьовий надлишковий підвіс (4-Axis Redundant Gimbal)", size=16, bold=True))

    # Схема кілець: База -> Зовнішній Yaw (грубий) -> Внутрішній Yaw (точний) -> Pitch -> Roll
    stages = [
        (110, 140, "Корпус", "База літака\nчи БПЛА", "#f4f6f8", LINE),
        (310, 140, "Зовнішній Yaw", "Грубе стеження\n(відводить рамку від 90°)", "#e8f4fd", NEG),
        (520, 140, "Внутрішній Yaw", "Точна стабілізація\nкурсу", "#eef9e8", FIELD),
        (720, 140, "Pitch & Roll", "Тангаж і крен\n|θ| < 60° (безпечна зона)", "#fff8e7", "#d35400"),
        (880, 140, "Камера", "Корисне\nнавантаження", "#fde8e8", POS),
    ]

    for cx, cy, title, desc, fcol, scol in stages:
        b, bw, bh = textbox(cx, cy, desc, size=11, pad=6, fill=fcol, stroke=scol, sw=1.6, min_w=140)
        frags.append(b)
        frags.append(text(cx, cy - bh / 2 - 10, title, size=12, bold=True, color=scol))

    # Стрілки між блоками
    arrows_list = [
        (185, 140, 235, 140),
        (385, 140, 445, 140),
        (595, 140, 645, 140),
        (795, 140, 830, 140),
    ]
    for x1, y1, x2, y2 in arrows_list:
        frags.append(arrow(x1, y1, x2, y2, color=LINE, sw=1.8))

    # Пояснення механізму запобігання замку
    cy_info = 290
    b_info, _, _ = textbox(W / 2, cy_info,
                           "Принцип уникнення сингулярності:\n"
                           "Коли тангаж наближається до небезпечної зони (|θ| > 60°), зовнішня рамка рискання (Outer Yaw)\n"
                           "розвертає всю проміжну вісь підвісу, утримуючи кут внутрішнього тангажу в робочому безпечному діапазоні.\n"
                           "Результат: повна сферична свобода 360°×360° без втрати керованості у зеніті чи надирі.",
                           size=12, pad=10, fill="#f8fafc", stroke=FIELD, sw=1.5, min_w=740)
    frags.append(b_info)

    frags.append(text(W / 2, 385,
                      "Четверта надлишкова вісь дозволяє розімкнути геометричну сингулярність без переривання стабілізації",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "four-axis-gimbal.svg"), W, H, *frags,
           title="Чотириосьовий підвіс для усунення карданового замка")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 4: Пряма та зворотна кінематика цілевказівки камери
# ───────────────────────────────────────────────────────────────────────────
def fig_camera_targeting():
    W, H = 960, 440
    frags = []

    frags.append(text(W / 2, 28, "Пряма та зворотна кінематика оптичного підвісу", size=16, bold=True))

    # Лівий блок: Пряма кінематика (Forward Kinematics)
    cx_l = 250
    frags.append(text(cx_l, 65, "Пряма кінематика (Forward)", size=14, bold=True, color=NEG))
    b_fwd, _, _ = textbox(cx_l, 175,
                          "Вхід:\n"
                          "• Орієнтація носія R_body\n"
                          "• Кути моторів підвісу (ψ, θ, φ)\n\n"
                          "Обчислення:\n"
                          "R_g = R_z(ψ) · R_y(θ) · R_x(φ)\n"
                          "R_cam = R_body · R_g\n\n"
                          "Вихід: Куди дивиться оптична вісь у світі:\n"
                          "v_cam = R_cam · [1, 0, 0]^T",
                          size=12, pad=10, fill="#edf4fc", stroke=NEG, min_w=280)
    frags.append(b_fwd)

    # Центральна частина: зв'язок рамки апарата й камери
    cx_m = W / 2
    frags.append(text(cx_m, 170, "⇄", size=32, color=LINE))
    frags.append(text(cx_m, 210, "R_g = R_body^T · R_target", size=12, bold=True, color=LINE))

    # Правий блок: Зворотна кінематика (Inverse Kinematics / Targeting)
    cx_r = 710
    frags.append(text(cx_r, 65, "Зворотна кінематика (Inverse / Targeting)", size=14, bold=True, color=POS))
    b_inv, _, _ = textbox(cx_r, 175,
                          "Вхід:\n"
                          "• Бажаний вектор на ціль у світі v_target\n"
                          "• Поточна орієнтація носія R_body\n\n"
                          "Обчислення:\n"
                          "Вектор цілі в рамці носія: v_b = R_body^T · v_target\n"
                          "Кут рискання: ψ = atan2(v_b.y, v_b.x)\n"
                          "Кут тангажу:  θ = atan2(-v_b.z, √(v_b.x² + v_b.y²))\n\n"
                          "Вихід: Завдання моторам підвісу (ψ, θ, φ=0)",
                          size=12, pad=10, fill="#fdf2f2", stroke=POS, min_w=310)
    frags.append(b_inv)

    # Нижня плашка: Компенсація збурень корпусу
    cy_b = 340
    b_comp, _, _ = textbox(W / 2, cy_b,
                           "Компенсація збурень носія в реальному часі (Attitude Stabilization):\n"
                           "Коли безпілотник виконує маневр (крен, рискання), контролер підвісу розраховує R_g = R_body^T · R_inertial,\n"
                           "миттєво відпрацьовуючи кути моторів так, щоб вектор візування оптичної осі лишався нерухомим у світі.",
                           size=12, pad=10, fill="#f8fafc", stroke=FIELD, sw=1.5, min_w=800)
    frags.append(b_comp)

    frags.append(text(W / 2, 415,
                      "Зворотна кінематика перетворює бажаний світовий напрямок огляду на кутові уставки для моторів підвісу",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "gimbal-camera-targeting.svg"), W, H, *frags,
           title="Пряма та зворотна кінематика підвісу камери")


def main():
    fig_kinematic_chain()
    fig_gimbal_lock()
    fig_four_axis_gimbal()
    fig_camera_targeting()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
