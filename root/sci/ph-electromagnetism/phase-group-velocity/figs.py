# -*- coding: utf-8 -*-
"""Фігури до теми «Фазова й групова швидкість».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_phase_vs_group():
    """Фігура 1: Інтерференція двох хвильових гармонік — фазова vs групова швидкість."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Фазова й групова швидкість у біттях двох хвиль", size=16, bold=True))

    # Секція 1: Окремі гармоніки k1 та k2
    f.append(rect(20, 48, W - 40, 110, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(35, 70, "Гармоніки k₁ та k₂ (близькі частоти ω₀ ± Δω):", size=13, bold=True, anchor="start"))

    # Синусоїда 1 (синя)
    pts1 = []
    for x in range(160, 710):
        y = 95 - 20 * math.sin((x - 160) * 0.08)
        pts1.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts1)}" fill="none" stroke="{NEG}" stroke-width="1.8"/>')
    f.append(text(150, 98, "E₁", size=12, color=NEG, bold=True, anchor="end"))

    # Синусоїда 2 (червона)
    pts2 = []
    for x in range(160, 710):
        y = 135 - 20 * math.sin((x - 160) * 0.095)
        pts2.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts2)}" fill="none" stroke="{POS}" stroke-width="1.8"/>')
    f.append(text(150, 138, "E₂", size=12, color=POS, bold=True, anchor="end"))

    # Секція 2: Результуюча хвиля (біття та огинаюча)
    f.append(rect(20, 170, W - 40, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(35, 192, "Сумарна хвиля E = E₁ + E₂ = 2E₀ · cos(Δω·t − Δk·x) · cos(ω₀·t − k₀·x)", size=13, bold=True, anchor="start"))

    # Базова вісь
    f.append(line(160, 290, 710, 290, color=MUTED, sw=1, dash="3,3"))

    # Огинаюча (зелена пунктирна)
    pts_env_up = []
    pts_env_dn = []
    for x in range(160, 710):
        env = 45 * math.cos((x - 160) * 0.015)
        pts_env_up.append(f"{x:.1f},{290 - env:.1f}")
        pts_env_dn.append(f"{x:.1f},{290 + env:.1f}")

    f.append(f'<polyline points="{" ".join(pts_env_up)}" fill="none" stroke="{FIELD}" stroke-width="2" stroke-dasharray="4,4"/>')
    f.append(f'<polyline points="{" ".join(pts_env_dn)}" fill="none" stroke="{FIELD}" stroke-width="2" stroke-dasharray="4,4"/>')

    # Швидке несуче коливання в межах огинаючої
    pts_sum = []
    for x in range(160, 710):
        env = 45 * math.cos((x - 160) * 0.015)
        y = 290 - env * math.sin((x - 160) * 0.0875)
        pts_sum.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_sum)}" fill="none" stroke="{INK}" stroke-width="1.8"/>')

    # Маркери та стрілки швидкостей
    # Фазова швидкість vp (рух гребеня)
    f.append(circle(370, 246, 5, fill=POS, stroke=BG, sw=1.5))
    f.append(arrow(370, 222, 425, 222, color=POS, sw=2))
    f.append(text(400, 212, "v_p = ω₀ / k₀ (рух гребеня фази)", size=12, color=POS, bold=True))

    # Групова швидкість vg (рух огинаючої)
    f.append(circle(160, 245, 5, fill=FIELD, stroke=BG, sw=1.5))
    f.append(arrow(160, 355, 240, 355, color=FIELD, sw=2.2))
    f.append(text(200, 375, "v_g = dω / dk (рух обвідної / пакета)", size=12, color=FIELD, bold=True))

    # Пояснення збоку
    f.append(textbox(85, 290, "Хвильовий\nпакет\n(огинаюча)", size=12, fill="#eefdff", stroke="#0284c7", sw=1.5)[0])

    return render(os.path.join(IMG, "phase-vs-group-waves.svg"), W, H, *f)


def fig_dispersion_curves():
    """Фігура 2: Дисперсійні співвідношення ω(k) для різних середовищ."""
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Дисперсійні співвідношення ω(k) та типи середовищ", size=16, bold=True))

    # Ліва панель: Криві ω(k)
    f.append(rect(20, 48, 360, 310, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(200, 70, "Залежність частоти від хвильового числа", size=13, bold=True))

    # Осі
    f.append(arrow(50, 320, 350, 320, color=LINE, sw=1.5))  # k
    f.append(text(355, 324, "k", size=14, bold=True, anchor="start"))
    f.append(arrow(50, 320, 50, 85, color=LINE, sw=1.5))   # ω
    f.append(text(50, 75, "ω", size=14, bold=True))

    # Бездисперсне середовище (вакуум): ω = c·k (пряма)
    f.append(line(50, 320, 320, 120, color=MUTED, sw=2, dash="4,4"))
    f.append(text(325, 125, "Вакуум (v_p = v_g = c)", size=11, color=MUTED, anchor="start"))

    # Хвилевід / Плазма: ω = √(ω_p² + c² k²)
    pts_plas = []
    for k in range(0, 270, 5):
        w_val = math.sqrt(100**2 + (0.75 * k)**2)
        x = 50 + k
        y = 320 - w_val
        pts_plas.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_plas)}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    f.append(text(275, 175, "Плазма / хвилевід", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(275, 190, "(v_p > c, v_g < c)", size=11, color=POS, anchor="start"))

    # Нормальна дисперсія (скло, воду): ω(k) опукла вгору (v_g < v_p)
    pts_norm = []
    for k in range(0, 270, 5):
        w_val = 1.3 * (k ** 0.85) * 1.8
        x = 50 + k
        y = 320 - w_val
        pts_norm.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_norm)}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    f.append(text(275, 235, "Нормальна дисперсія", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(275, 250, "(v_g < v_p)", size=11, color=NEG, anchor="start"))

    # Права панель: Фізичний зміст дотичної та січної
    f.append(rect(395, 48, 345, 310, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(567, 70, "Геометричний зміст v_p та v_g", size=13, bold=True))

    # Схематична крива ω(k)
    f.append(arrow(420, 310, 710, 310, color=LINE, sw=1.2))
    f.append(text(715, 314, "k", size=13, bold=True, anchor="start"))
    f.append(arrow(420, 310, 420, 110, color=LINE, sw=1.2))
    f.append(text(420, 100, "ω", size=13, bold=True))

    # Крива
    pts_c = []
    for x_i in range(0, 240, 5):
        y_i = 120 * math.sin(x_i * 0.008) + 0.4 * x_i
        pts_c.append(f"{420 + x_i:.1f},{310 - y_i:.1f}")
    f.append(f'<polyline points="{" ".join(pts_c)}" fill="none" stroke="{INK}" stroke-width="2.5"/>')

    # Точка P0
    px, py = 560, 200
    f.append(circle(px, py, 4, fill=INK, stroke=BG, sw=1.5))
    f.append(text(px + 8, py - 8, "P(k₀, ω₀)", size=11, bold=True, anchor="start"))

    # Січна (з початку координат через P0) -> тангенс кута = v_p = ω0/k0
    f.append(line(420, 310, 645, 133, color=NEG, sw=1.8, dash="5,3"))
    f.append(text(650, 138, "Січна: tg α = v_p = ω₀ / k₀", size=11, color=NEG, bold=True, anchor="start"))

    # Дотична у точці P0 -> тангенс кута = v_g = dω/dk
    f.append(line(480, 242, 640, 158, color=FIELD, sw=2))
    f.append(text(645, 172, "Дотична: tg β = v_g = dω / dk", size=11, color=FIELD, bold=True, anchor="start"))

    # Пояснювальний бокс знизу
    f.append(textbox(567, 325, "v_p — нахил січної від 0\nv_g — нахил дотичної в точці", size=11, fill="#f4f6f8", stroke=LINE)[0])

    return render(os.path.join(IMG, "dispersion-curves.svg"), W, H, *f)


def fig_wave_packet_broadening():
    """Фігура 3: Уширення хвильового пакета через дисперсію групової швидкості (GVD)."""
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Розпливання хвильового імпульсу у дисперсійному середовищі (GVD)", size=16, bold=True))

    # Схематичний світловод / середовище
    f.append(rect(40, 48, 680, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))

    # Вхідний вузький імпульс z = 0 (центриємо по y=200)
    f.append(line(130, 270, 130, 95, color=MUTED, sw=1, dash="3,3"))
    f.append(text(130, 75, "Вхідний імпульс (z = 0)", size=12, bold=True))

    # Гаусів пакет на вході (амплітуда 80px, центр у y=190)
    pts_in = []
    for x in range(80, 180):
        dx = (x - 130) / 14.0
        g = math.exp(-dx * dx)
        y = 190 - 80 * g * math.cos(dx * 10)
        pts_in.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_in)}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    f.append(text(130, 325, "Ширина τ₀ (стислий)", size=11, color=MUTED))

    # Стрілка поширення в середовищі
    f.append(arrow(220, 185, 480, 185, color=FIELD, sw=2.5))
    f.append(text(350, 165, "Поширення у середовищі з β₂ = d²k/dω² > 0", size=12, color=FIELD, bold=True))
    f.append(text(350, 205, "Різні частотні складові рухаються з різною v_g", size=11, color=MUTED))

    # Вихідний уширений імпульс z = L (центриємо по y=190)
    f.append(line(590, 270, 590, 95, color=MUTED, sw=1, dash="3,3"))
    f.append(text(590, 75, "Вихідний імпульс (z = L)", size=12, bold=True))

    # Гаусів пакет на виході
    pts_out = []
    for x in range(480, 700):
        dx = (x - 590) / 38.0
        g = math.exp(-dx * dx)
        freq = 6 + 4 * dx
        y = 190 - 50 * g * math.cos(dx * freq)
        pts_out.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_out)}" fill="none" stroke="{POS}" stroke-width="2"/>')
    f.append(text(590, 325, "Ширина τ(z) > τ₀ (уширений + чирп)", size=11, color=POS))

    # Підписи спектральних фаз поза зоною коливань пакета
    f.append(text(490, 105, "Низькі частоти (НЧ)", size=10, color=POS, bold=True))
    f.append(text(680, 105, "Високі частоти (ВЧ)", size=10, color=NEG, bold=True))

    return render(os.path.join(IMG, "wave-packet-broadening.svg"), W, H, *f)


if __name__ == "__main__":
    fig_phase_vs_group()
    fig_dispersion_curves()
    fig_wave_packet_broadening()
    print("Фігури згенеровано успішно.")
