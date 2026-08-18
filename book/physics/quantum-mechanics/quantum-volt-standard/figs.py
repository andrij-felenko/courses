# -*- coding: utf-8 -*-
"""Фігури до теми «Квантовий стандарт вольта».
Запуск: python figs.py -> генерує SVG у ./img/
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
COLOR_DARK = "#2c3e50"


def fig_weston_vs_quantum():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Порівняння еталонів напруги: Хімічний елемент vs Квантовий стандарт", size=15, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 25, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Елемент Вестона ---
    f.append(text(midx / 2, 54, "Хімічний елемент Вестона (1893–1990)", size=13, bold=True, color=COLOR_RED))

    # Скляна H-подібна судина
    f.append(rect(60, 90, 40, 110, fill="#fdfefe", stroke=COLOR_DARK, sw=2, rx=4))
    f.append(rect(140, 90, 40, 110, fill="#fdfefe", stroke=COLOR_DARK, sw=2, rx=4))
    f.append(rect(100, 130, 40, 30, fill="#fdfefe", stroke=COLOR_DARK, sw=2, rx=0))
    # Ртуть та амальгама
    f.append(rect(62, 160, 36, 38, fill="#bdc3c7", stroke="none"))
    f.append(rect(142, 160, 36, 38, fill="#f39c12", stroke="none"))
    f.append(text(80, 180, "Hg", size=11, bold=True, color="#2c3e50"))
    f.append(text(160, 180, "Cd-Hg", size=10, bold=True, color="#2c3e50"))

    # Електроди
    f.append(line(80, 198, 80, 220, color=COLOR_DARK, sw=2))
    f.append(line(160, 198, 160, 220, color=COLOR_DARK, sw=2))
    f.append(text(80, 234, "+ (Катод)", size=11, color=COLOR_RED))
    f.append(text(160, 234, "- (Анод)", size=11, color=COLOR_BLUE))

    b1, w1, h1 = textbox(midx / 2, 290, 
                         "• Напруга V ≈ 1.01865 В\n"
                         "• Температурний дрейф: -40 мкВ/К\n"
                         "• Старіння й хімічний декремент\n"
                         "• Чутливість до струсів і транспорту",
                         size=11, pad=8, fill="#fff0f0", stroke="#ffb3b3", sw=1.2)
    f.append(b1)

    # --- ПРАВА ЧАСТИНА: Квантовий стандарт Джозефсона ---
    f.append(text(midx + midx / 2, 54, "Квантовий стандарт Джозефсона (з 1990 / SI 2019)", size=13, bold=True, color=COLOR_GREEN))

    # Схема квантування
    f.append(rect(430, 90, 120, 50, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8, rx=5))
    f.append(text(490, 110, "Атомний годинник", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(490, 126, "f = 75.000000000 ГГц", size=10, color=COLOR_DARK))

    f.append(arrow(550, 115, 590, 115, color=COLOR_BLUE, sw=1.8))

    f.append(rect(590, 90, 130, 50, fill="#eafaf1", stroke=COLOR_GREEN, sw=1.8, rx=5))
    f.append(text(655, 110, "Матриця Джозефсона", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(655, 126, "N = 6912 перехідників", size=10, color=COLOR_DARK))

    f.append(arrow(655, 140, 655, 175, color=COLOR_GREEN, sw=1.8))

    f.append(rect(580, 175, 150, 45, fill="#fef9e7", stroke=COLOR_ORANGE, sw=1.8, rx=5))
    f.append(text(655, 192, "V_N = N · h · f / 2e", size=12, bold=True, color=COLOR_ORANGE))
    f.append(text(655, 208, "Точно 1.000000000... В", size=11, color=COLOR_DARK))

    b2, w2, h2 = textbox(midx + midx / 2, 290,
                         "• Фундаментальні константи h та e\n"
                         "• Нульовий температурний дрейф\n"
                         "• Абсолютна відтворюваність у світі\n"
                         "• Точність краща за 10⁻¹⁰",
                         size=11, pad=8, fill="#eafaf1", stroke="#abebc6", sw=1.2)
    f.append(b2)

    render(os.path.join(IMG, 'weston-vs-quantum.svg'), W, H, *f)


def fig_shapiro_steps():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, "Вольт-амперна характеристика з квантовими сходинками Шапіро", size=15, bold=True))

    cx, cy = 340, 220
    scale_v = 85  # pixels per step V1

    # Вісі
    f.append(line(cx - 260, cy, cx + 280, cy, color=COLOR_DARK, sw=1.6)) # Вісь V
    f.append(arrow(cx + 280, cy, cx + 295, cy, color=COLOR_DARK, sw=1.6))
    f.append(text(cx + 305, cy + 4, "Напруга V", size=12, bold=True, color=COLOR_DARK))

    f.append(line(cx, cy + 160, cx, cy - 170, color=COLOR_DARK, sw=1.6)) # Вісь I
    f.append(arrow(cx, cy - 170, cx, cy - 182, color=COLOR_DARK, sw=1.6))
    f.append(text(cx, cy - 192, "Струм зсуву I", size=12, bold=True, color=COLOR_DARK))

    # Пунктирні лінії для сходинок n = -2, -1, 0, 1, 2
    steps = [-2, -1, 0, 1, 2]
    for n in steps:
        vx = cx + n * scale_v
        f.append(line(vx, cy - 160, vx, cy + 150, color="#eaeded", sw=1, dash="3,3"))
        if n != 0:
            label = f"V_{n} = {n}·hf/2e" if n > 0 else f"V_{{{n}}} = {n}·hf/2e"
            f.append(text(vx, cy + 168, label, size=10, bold=True, color=COLOR_BLUE))

    # Рисування ВАХ з плато (сходинками Шапіро)
    # n=0: V = 0, I від -Ic до +Ic
    f.append(line(cx, cy - 80, cx, cy + 80, color=COLOR_RED, sw=3))

    # n=1: V = V1, I від I_min1 до I_max1
    vx1 = cx + scale_v
    f.append(line(vx1, cy - 120, vx1, cy - 30, color=COLOR_RED, sw=3))
    # Перехід від n=0 до n=1
    f.append(line(cx, cy - 80, vx1, cy - 30, color=COLOR_RED, sw=1.2, dash="4,2"))

    # n=2: V = V2
    vx2 = cx + 2 * scale_v
    f.append(line(vx2, cy - 150, vx2, cy - 80, color=COLOR_RED, sw=3))
    f.append(line(vx1, cy - 120, vx2, cy - 80, color=COLOR_RED, sw=1.2, dash="4,2"))

    # n=-1: V = -V1
    vx_n1 = cx - scale_v
    f.append(line(vx_n1, cy + 30, vx_n1, cy + 120, color=COLOR_RED, sw=3))
    f.append(line(cx, cy + 80, vx_n1, cy + 30, color=COLOR_RED, sw=1.2, dash="4,2"))

    # n=-2: V = -V2
    vx_n2 = cx - 2 * scale_v
    f.append(line(vx_n2, cy + 80, vx_n2, cy + 150, color=COLOR_RED, sw=3))
    f.append(line(vx_n1, cy + 120, vx_n2, cy + 80, color=COLOR_RED, sw=1.2, dash="4,2"))

    # Позначки струму Ic
    f.append(line(cx - 5, cy - 80, cx + 5, cy - 80, color=COLOR_DARK, sw=1.5))
    f.append(text(cx - 24, cy - 80, "+I_c", size=11, bold=True, color=COLOR_DARK))
    f.append(line(cx - 5, cy + 80, cx + 5, cy + 80, color=COLOR_DARK, sw=1.5))
    f.append(text(cx - 24, cy + 80, "-I_c", size=11, bold=True, color=COLOR_DARK))

    # Виносні пояснення
    b1, w1, h1 = textbox(cx + 210, cy - 120, "Сходинка n = 1\n(Квантоване плато напруги)", size=11, pad=6, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.2)
    f.append(b1)
    f.append(arrow(cx + 130, cy - 120, vx1 + 5, cy - 90, color=COLOR_BLUE, sw=1.4))

    b2, w2, h2 = textbox(cx - 210, cy - 130, "Нульовий спад напруги\n(Надструм при V = 0)", size=11, pad=6, fill="#fff0f0", stroke=COLOR_RED, sw=1.2)
    f.append(b2)
    f.append(arrow(cx - 130, cy - 130, cx - 4, cy - 50, color=COLOR_RED, sw=1.4))

    render(os.path.join(IMG, 'shapiro-steps.svg'), W, H, *f)


def fig_pjvs_array_scheme():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, "Схема програмованого квантового стандарту напруги (PJVS)", size=15, bold=True))

    # 1. Атомний стандарт частоти
    f.append(rect(40, 70, 140, 70, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8, rx=6))
    f.append(text(110, 95, "Рубідієвий/Цезієвий", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(110, 112, "стандарт частоти", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(110, 128, "10 МГц (Δf/f < 10⁻¹²)", size=10, color=COLOR_DARK))

    # Сила генератора СВЧ
    f.append(arrow(180, 105, 230, 105, color=COLOR_BLUE, sw=2))

    # 2. Синтезатор СВЧ (70-75 ГГц)
    f.append(rect(230, 70, 140, 70, fill="#fcf3cf", stroke=COLOR_ORANGE, sw=1.8, rx=6))
    f.append(text(300, 95, "Генератор СВЧ", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(300, 112, "Gunn / БВіЧ", size=11, color=COLOR_DARK))
    f.append(text(300, 128, "f = 70...75 ГГц", size=10, bold=True, color=COLOR_DARK))

    # 3. Кріостат 4.2 К
    f.append(rect(430, 60, 310, 240, fill="#ebf5fb", stroke="#5dabf4", sw=2, rx=8))
    f.append(text(585, 82, "Кріостат рідкого гелію (T = 4.2 К)", size=12, bold=True, color="#1b4f72"))

    # СВЧ волновод
    f.append(line(370, 105, 470, 105, color=COLOR_ORANGE, sw=3))
    f.append(arrow(470, 105, 500, 105, color=COLOR_ORANGE, sw=2))
    f.append(text(435, 93, "Хвилевід СВЧ", size=10, color=COLOR_ORANGE))

    # 4. Чип матриці Джозефсона у кріостаті
    f.append(rect(500, 110, 180, 160, fill="#ffffff", stroke=COLOR_GREEN, sw=2, rx=5))
    f.append(text(590, 130, "Чип PJVS (Nb/NbSi/Nb)", size=11, bold=True, color=COLOR_GREEN))

    # Двійкові секції матриці
    sections = [("Секція 1 (1 перехід)", 150),
                ("Секція 2 (2 переходи)", 175),
                ("Секція 3 (4 переходи)", 200),
                ("...", 222),
                ("Секція N (4096 переходів)", 245)]
    for label, ypos in sections:
        f.append(rect(515, ypos - 10, 150, 18, fill="#eafaf1", stroke="#abebc6", sw=1, rx=3))
        f.append(text(590, ypos, label, size=9, color=COLOR_DARK))

    # 5. Програмоване джерело струму зсуву (Bias Controller)
    f.append(rect(120, 210, 220, 140, fill="#f4ecf7", stroke=COLOR_PURPLE, sw=1.8, rx=6))
    f.append(text(230, 232, "ЦАП і джерела струму зсуву", size=11, bold=True, color=COLOR_PURPLE))
    f.append(text(230, 250, "Комп'ютерне керування секціями", size=10, color=COLOR_DARK))
    f.append(text(230, 270, "Встановлення кроку напруги", size=10, color=COLOR_DARK))
    f.append(text(230, 290, "V_out = Σ (a_k · N_k · h f / 2e)", size=10, bold=True, color=COLOR_PURPLE))

    # Лінії струму зсуву до кріостата
    f.append(line(340, 280, 500, 280, color=COLOR_PURPLE, sw=1.8, dash="4,3"))
    f.append(arrow(340, 280, 500, 280, color=COLOR_PURPLE, sw=1.8))
    f.append(text(420, 270, "Керуючі струми I_bias", size=10, color=COLOR_PURPLE))

    # 6. Прецизійний квантований вихід V_out
    f.append(line(680, 190, 750, 190, color=COLOR_RED, sw=2.5))
    f.append(line(680, 230, 750, 230, color=COLOR_BLUE, sw=2.5))
    f.append(circle(750, 190, 4, fill=COLOR_RED, stroke="none"))
    f.append(circle(750, 230, 4, fill=COLOR_BLUE, stroke="none"))
    f.append(text(750, 175, "V_out (+)", size=11, bold=True, color=COLOR_RED))
    f.append(text(750, 245, "V_out (-)", size=11, bold=True, color=COLOR_BLUE))

    render(os.path.join(IMG, 'pjvs-array-scheme.svg'), W, H, *f)


if __name__ == "__main__":
    fig_weston_vs_quantum()
    fig_shapiro_steps()
    fig_pjvs_array_scheme()
    print("Фігури створено успішно у ./img/")
