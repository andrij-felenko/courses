# -*- coding: utf-8 -*-
"""Фігури для теми «Спін електрона» (book/physics/quantum-mechanics/electron-spin)."""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def path_svg(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def ellipse_svg(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def fig_stern_gerlach():
    """fig1-stern-gerlach.svg: Схема досліду Штерна — Ґерлаха з розділенням пучка атомів у неоднорідному магнітному полі."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Експеримент Штерна — Ґерлаха: просторове квантування спіну (s = 1/2)", size=16, bold=True, color="#1e293b"))

    # Джерело атомів (піч)
    frags.append(rect(40, 160, 90, 120, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=6))
    frags.append(text(85, 205, "Піч (Ag)", size=13, bold=True, color=AMBER_S))
    frags.append(text(85, 230, "T = 1300 K", size=11, color="#64748b"))

    # Щілини коліматора
    frags.append(rect(160, 140, 10, 60, fill="#334155", stroke="#1e293b"))
    frags.append(rect(160, 240, 10, 60, fill="#334155", stroke="#1e293b"))
    frags.append(text(165, 320, "Коліматор", size=11, color="#475569"))

    # Вузький пучок атомів до магніту
    frags.append(line(130, 220, 240, 220, color=AMBER_S, sw=2.5))

    # Неоднорідний магніт
    # Верхній гострий полюс N
    frags.append(path_svg("M 250 90 L 450 90 L 360 170 L 340 170 Z", fill=RED_F, stroke=RED_S, sw=2.0))
    frags.append(text(350, 125, "N (гострий полюс)", size=12, bold=True, color=RED_S))

    # Нижній плоский полюс S
    frags.append(rect(250, 270, 200, 60, fill=BLUE_F, stroke=BLUE_S, sw=2.0, rx=4))
    frags.append(text(350, 305, "S (плоский полюс)", size=12, bold=True, color=BLUE_S))

    # Вектори градієнту та поля
    frags.append(line(470, 150, 470, 290, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(mtext(520, 210, "dB_z / dz > 0\n(градієнт)", size=11, bold=True, color="#475569"))

    # Пучок усередині магніту
    frags.append(line(240, 220, 350, 220, color=AMBER_S, sw=2.5))

    # Розщеплення пучка після магніту
    # Верхній пучок (m_s = +1/2)
    frags.append(path_svg("M 350 220 Q 480 210 680 130", fill="none", stroke=RED_S, sw=2.5))
    # Нижній пучок (m_s = -1/2)
    frags.append(path_svg("M 350 220 Q 480 230 680 310", fill="none", stroke=BLUE_S, sw=2.5))

    # Детектор (екран)
    frags.append(rect(680, 80, 20, 280, fill="#e2e8f0", stroke="#475569", sw=2.0, rx=3))
    frags.append(mtext(760, 100, "Детекторна\nпластина", size=12, bold=True, color="#1e293b"))

    # Плями на детекторі
    frags.append(ellipse_svg(690, 130, 6, 18, fill=RED_S, stroke=RED_S))
    b_up, _, _ = textbox(770, 140, "Спін «вгору»\nm_s = +1/2 (50%)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_up)

    frags.append(ellipse_svg(690, 310, 6, 18, fill=BLUE_S, stroke=BLUE_S))
    b_down, _, _ = textbox(770, 300, "Спін «вниз»\nm_s = -1/2 (50%)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_down)

    # Порожнє центр
    frags.append(circle(690, 220, 4, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(mtext(780, 220, "Класична середина\n(порожньо!)", size=10, bold=False, color="#64748b"))

    render(os.path.join(IMG, "fig1-stern-gerlach.svg"), W, H, *frags)


def fig_spinor_rotation():
    """fig2-spinor-rotation.svg: Сфера Блоха та 4п топологія обертання спінора."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Сфера Блоха та топологічна фаза обертання спінора s = 1/2", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Сфера Блоха
    cx, cy, R = 230, 210, 120

    # Сфера
    frags.append(circle(cx, cy, R, fill="#ffffff", stroke="#94a3b8", sw=1.8))
    frags.append(ellipse_svg(cx, cy, R, 35, fill="none", stroke="#cbd5e1", sw=1.2, dash="4,4"))

    # Осі координат
    frags.append(line(cx, cy - R - 20, cx, cy + R + 20, color="#334155", sw=1.8)) # Z
    frags.append(text(cx + 15, cy - R - 15, "+Z (|↑⟩)", size=12, bold=True, color=GREEN_S))
    frags.append(text(cx + 15, cy + R + 15, "-Z (|↓⟩)", size=12, bold=True, color=PURPLE_S))

    frags.append(line(cx - R - 20, cy, cx + R + 20, cy, color="#64748b", sw=1.2)) # Y
    frags.append(text(cx + R + 25, cy + 4, "+Y", size=11, color="#64748b"))

    frags.append(line(cx - 70, cy + 70, cx + 70, cy - 70, color="#64748b", sw=1.2)) # X
    frags.append(text(cx - 85, cy + 85, "+X", size=11, color="#64748b"))

    # Вектор стану |Psi>
    vx, vy = cx + 80, cy - 80
    frags.append(line(cx, cy, vx, vy, color=BLUE_S, sw=2.8))
    frags.append(circle(vx, vy, 5, fill=BLUE_S, stroke=BLUE_S))

    b_psi, _, _ = textbox(cx + 120, cy - 100, "|Ψ⟩ = cos(θ/2)|↑⟩ + e^(iφ)sin(θ/2)|↓⟩", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_psi)

    # Правий блок: Обертання на 2п та 4п
    frags.append(rect(460, 60, 390, 310, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 85, "Фазовий множник при обертанні U(θ)", size=13, bold=True, color="#1e293b"))

    # 2pi rotation
    b_2pi, _, _ = textbox(655, 140, "Обертання на θ = 2π (360°):\nU(2π)|Ψ⟩ = -|Ψ⟩\n(Зміна знаку спінорової хвильової функції)", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b_2pi)

    # 4pi rotation
    b_4pi, _, _ = textbox(655, 230, "Обертання на θ = 4π (720°):\nU(4π)|Ψ⟩ = +|Ψ⟩\n(Повне повернення в початковий квантовий стан)", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_4pi)

    frags.append(text(655, 335, "Група SU(2) є дволистам накриттям групи 3D-обертань SO(3)", size=10, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig2-spinor-rotation.svg"), W, H, *frags)


def fig_larmor_precession():
    """fig3-larmor-precession.svg: Прецесія Лармора спінового моменту в постійному магнітному полі."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Ларморова прецесія векторного середнього спіну ⟨S⟩ у магнітному полі B_z", size=16, bold=True, color="#1e293b"))

    cx, cy = 300, 240

    # Вісь Z та поле B_z
    frags.append(line(cx, cy + 90, cx, cy - 160, color=RED_S, sw=2.2))
    frags.append(text(cx + 15, cy - 145, "B = (0, 0, B_z)", size=13, bold=True, color=RED_S))

    # Конус прецесії (еліпс зверху)
    frags.append(ellipse_svg(cx, cy - 90, 110, 30, fill="none", stroke=BLUE_S, sw=1.5, dash="4,4"))

    # Траєкторія обертання (стрілка коло)
    frags.append(path_svg("M 410 240 Q 420 180 380 150", fill="none", stroke=TEAL_S, sw=2.0))
    frags.append(mtext(445, 175, "Частота Лармора:\nω_L = g_e μ_B B_z / ℏ", size=12, bold=True, color=TEAL_S))

    # Спіновий вектор <S>
    sx, sy = cx + 85, cy - 100
    frags.append(line(cx, cy, sx, sy, color=BLUE_S, sw=3.0))
    frags.append(circle(sx, sy, 6, fill=BLUE_S, stroke=BLUE_S))
    frags.append(text(sx + 15, sy - 5, "⟨S⟩(t)", size=14, bold=True, color=BLUE_S))

    # Проєкція <S_z>
    frags.append(line(cx, cy, cx, sy, color=GREEN_S, sw=2.0, dash="3,3"))
    frags.append(line(cx, sy, sx, sy, color="#94a3b8", sw=1.2, dash="3,3"))
    frags.append(text(cx - 60, (cy + sy) / 2, "⟨S_z⟩ = const", size=11, bold=True, color=GREEN_S))

    # Права панель з графіком часових осциляцій <Sx> та <Sy>
    frags.append(rect(530, 60, 320, 310, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(690, 85, "Часова динаміка проєкцій спіну", size=13, bold=True, color="#1e293b"))

    # Осі графіка
    frags.append(line(560, 210, 830, 210, color="#64748b", sw=1.5)) # Час t
    frags.append(line(560, 110, 560, 310, color="#64748b", sw=1.5)) # S
    frags.append(text(835, 214, "t", size=11, color="#64748b"))

    # Графік <Sx>(t) = cos(w_L t)
    pts_sx = []
    for x in range(0, 260, 4):
        t_val = x / 30.0
        y = 210 - 70 * math.cos(t_val)
        pts_sx.append((560 + x, y))
    
    path_sx = "M " + " L ".join(f"{px} {py:.1f}" for px, py in pts_sx)
    frags.append(path_svg(path_sx, fill="none", stroke=BLUE_S, sw=2.0))

    # Графік <Sy>(t) = sin(w_L t)
    pts_sy = []
    for x in range(0, 260, 4):
        t_val = x / 30.0
        y = 210 - 70 * math.sin(t_val)
        pts_sy.append((560 + x, y))

    path_sy = "M " + " L ".join(f"{px} {py:.1f}" for px, py in pts_sy)
    frags.append(path_svg(path_sy, fill="none", stroke=PURPLE_S, sw=2.0, dash="4,3"))

    b_leg, _, _ = textbox(690, 335, "— ⟨S_x⟩(t) = S_⊥ cos(ω_L t)\n- - ⟨S_y⟩(t) = S_⊥ sin(ω_L t)", size=10, fill=GRAY_F, stroke="#cbd5e1")
    frags.append(b_leg)

    render(os.path.join(IMG, "fig3-larmor-precession.svg"), W, H, *frags)


def fig_spin_orbit_splitting():
    """fig4-spin-orbit-splitting.svg: Схема спін-орбітального розщеплення енергетичних рівнів (тонку структуру)."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Спін-орбітальне розщеплення (тонку структуру спектральних ліній)", size=16, bold=True, color="#1e293b"))

    # Рівень 1: Безурахування спіну (незбуджений кулонівський рівень n=2, l=1)
    frags.append(line(60, 200, 220, 200, color="#334155", sw=3.0))
    b_unp, _, _ = textbox(140, 240, "Орбітальний рівень\n2P (l = 1, s = 1/2)\nНевироджений за L·S", size=11, fill="#ffffff", stroke="#475569")
    frags.append(b_unp)

    # Пунктирні лінії зв'язку до спін-орбітального розщеплення
    frags.append(line(220, 200, 380, 120, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(line(220, 200, 380, 280, color="#94a3b8", sw=1.2, dash="4,4"))

    # Текст механізму L·S
    frags.append(mtext(300, 185, "Спін-орбітальна\nвзаємодія\nH_SO = ξ(r) L · S", size=11, bold=True, color=PURPLE_S))

    # Рівень 2: Тонка структура (j = 3/2 та j = 1/2)
    # j = 3/2 (паралельні L і S, вища енергія)
    frags.append(line(380, 120, 540, 120, color=RED_S, sw=3.0))
    b_j32, _, _ = textbox(460, 85, "2P_3/2 (j = 3/2)\nL і S паралельні\n(виродження g_j = 4)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_j32)

    # j = 1/2 (антипаралельні L і S, нижча енергія)
    frags.append(line(380, 280, 540, 280, color=BLUE_S, sw=3.0))
    b_j12, _, _ = textbox(460, 315, "2P_1/2 (j = 1/2)\nL і S антипаралельні\n(виродження g_j = 2)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_j12)

    # Енергетичне розщеплення ΔE_SO
    frags.append(line(550, 120, 550, 280, color=PURPLE_S, sw=1.5))
    frags.append(mtext(610, 200, "Тонке розщеплення\nΔE_SO ∝ α² E_n", size=11, bold=True, color=PURPLE_S))

    # Пунктирні лінії до Зеєманівського розщеплення у зовнішньому полі B
    frags.append(line(540, 120, 680, 80, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(540, 120, 680, 160, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(540, 280, 680, 250, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(540, 280, 680, 310, color="#94a3b8", sw=1.0, dash="3,3"))

    # Рівень 3: Зеєманівські підрівні в магнітному полі B
    frags.append(line(680, 80, 820, 80, color=RED_S, sw=1.8))
    frags.append(line(680, 107, 820, 107, color=RED_S, sw=1.8))
    frags.append(line(680, 133, 820, 133, color=RED_S, sw=1.8))
    frags.append(line(680, 160, 820, 160, color=RED_S, sw=1.8))
    frags.append(text(750, 65, "m_j = +3/2, +1/2, -1/2, -3/2", size=9, color=RED_S))

    frags.append(line(680, 250, 820, 250, color=BLUE_S, sw=1.8))
    frags.append(line(680, 310, 820, 310, color=BLUE_S, sw=1.8))
    frags.append(text(750, 235, "m_j = +1/2, -1/2", size=9, color=BLUE_S))

    frags.append(text(750, 345, "Ефект Зеємана (у полі B)", size=11, bold=True, color="#1e293b"))

    render(os.path.join(IMG, "fig4-spin-orbit-splitting.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_stern_gerlach()
    fig_spinor_rotation()
    fig_larmor_precession()
    fig_spin_orbit_splitting()
    print("Всі фігури успішно згенеровано у", IMG)
