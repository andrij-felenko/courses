# -*- coding: utf-8 -*-
"""Фігури для теми «Перший закон термодинаміки» (book/physics/thermal-statistical/first-law-thermodynamics)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
RED_F, RED_S = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S = "#f8fafc", "#475569"

def polyline(pts, color="#333333", sw=1.5, fill="none"):
    pts_str = " ".join("%g,%g" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, color, sw)

def fig_p_v_work():
    """p-v-work.svg: Робота як площа під кривою в P-V координатах та залежність від шляху процесу."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Робота розширення як площа під кривою на P-V діаграмі", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Шлях А (ізобарний + ізохорний)
    frags.append(rect(30, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(230, 78, "Шлях А: розширення при P₁ , далі охолодження", size=12, bold=True, color=BLUE_S))

    # Осі для Лівої панелі
    frags.append(line(70, 340, 390, 340, color="#475569", sw=2))  # V
    frags.append(line(70, 340, 70, 95, color="#475569", sw=2))    # P
    frags.append(text(390, 360, "Об'єм V", size=11, bold=True, color="#1e293b"))
    frags.append(text(45, 95, "P", size=11, bold=True, color="#1e293b"))

    # Зафарбована площа під Шляхом А (великий прямокутник під P1)
    frags.append(rect(110, 130, 230, 210, fill=BLUE_F, stroke="none"))
    frags.append(line(110, 130, 340, 130, color=BLUE_S, sw=3))
    frags.append(line(340, 130, 340, 270, color=BLUE_S, sw=3))

    # Пунктири до осей
    frags.append(line(110, 130, 110, 340, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(340, 270, 340, 340, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(70, 130, 110, 130, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(70, 270, 340, 270, color="#94a3b8", sw=1, dash="4,4"))

    frags.append(text(110, 355, "V₁", size=11, bold=True, color="#475569"))
    frags.append(text(340, 355, "V₂", size=11, bold=True, color="#475569"))
    frags.append(text(55, 134, "P₁", size=11, bold=True, color="#475569"))
    frags.append(text(55, 274, "P₂", size=11, bold=True, color="#475569"))

    # Точки станів 1 і 2
    frags.append(circle(110, 130, 6, fill=RED_S, stroke="#1e293b", sw=1.5))
    frags.append(text(110, 118, "Стан 1", size=11, bold=True, color=RED_S))
    frags.append(circle(340, 270, 6, fill=GREEN_S, stroke="#1e293b", sw=1.5))
    frags.append(text(355, 280, "Стан 2", size=11, bold=True, color=GREEN_S))

    # Напис роботи Площа А
    frags.append(text(225, 220, "W_A = P₁ · (V₂ - V₁)", size=12, bold=True, color=BLUE_S))

    # Права панель: Шлях Б (ізохорний + ізобарний)
    frags.append(rect(450, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(650, 78, "Шлях Б: охолодження до P₂ , далі розширення", size=12, bold=True, color=AMBER_S))

    # Осі для Правої панелі
    frags.append(line(490, 340, 810, 340, color="#475569", sw=2))  # V
    frags.append(line(490, 340, 490, 95, color="#475569", sw=2))    # P
    frags.append(text(810, 360, "Об'єм V", size=11, bold=True, color="#1e293b"))
    frags.append(text(465, 95, "P", size=11, bold=True, color="#1e293b"))

    # Зафарбована площа під Шляхом Б (малий прямокутник під P2)
    frags.append(rect(530, 270, 230, 70, fill=AMBER_F, stroke="none"))
    frags.append(line(530, 130, 530, 270, color=AMBER_S, sw=3))
    frags.append(line(530, 270, 760, 270, color=AMBER_S, sw=3))

    # Пунктири до осей
    frags.append(line(530, 130, 530, 340, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(760, 270, 760, 340, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(490, 130, 530, 130, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(490, 270, 760, 270, color="#94a3b8", sw=1, dash="4,4"))

    frags.append(text(530, 355, "V₁", size=11, bold=True, color="#475569"))
    frags.append(text(760, 355, "V₂", size=11, bold=True, color="#475569"))
    frags.append(text(475, 134, "P₁", size=11, bold=True, color="#475569"))
    frags.append(text(475, 274, "P₂", size=11, bold=True, color="#475569"))

    # Точки станів 1 і 2
    frags.append(circle(530, 130, 6, fill=RED_S, stroke="#1e293b", sw=1.5))
    frags.append(text(530, 118, "Стан 1", size=11, bold=True, color=RED_S))
    frags.append(circle(760, 270, 6, fill=GREEN_S, stroke="#1e293b", sw=1.5))
    frags.append(text(775, 280, "Стан 2", size=11, bold=True, color=GREEN_S))

    # Напис роботи Площа Б
    frags.append(text(645, 305, "W_Б = P₂ · (V₂ - V₁)", size=12, bold=True, color=AMBER_S))

    # Підпис висновку
    frags.append(text(440, 385, "Висновок: W_A ≠ W_Б при однаковому ΔU = U₂ - U₁ ⇒ Робота W залежить від шляху (неточний диференціал δW)", size=11, bold=True, color=RED_S))

    render(os.path.join(IMG, "p-v-work.svg"), W, H, *frags)


def fig_energy_balance_system():
    """energy-balance-system.svg: Баланс енергії закритої термодинамічної системи."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Баланс енергії закритої термодинамічної системи", size=16, bold=True, color="#1e293b"))

    # Контур системи (контрольний об'єм)
    frags.append(rect(240, 80, 400, 220, fill="#ffffff", stroke="#2563eb", sw=3, rx=15))
    frags.append(text(440, 105, "ТЕРМОДИНАМІЧНА СИСТЕМА", size=13, bold=True, color=BLUE_S))

    # Внутрішній стан U
    b_u, _, _ = textbox(440, 185, "Внутрішня енергія U\n(Функція стану: ΔU = U₂ - U₁)\nE_кінетична + E_потенціальна частинок", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_u)

    # Вхідне тепло Q (стрілка зліва)
    frags.append(line(80, 185, 225, 185, color=RED_S, sw=4))
    # Стрілка налітання
    frags.append(line(205, 175, 225, 185, color=RED_S, sw=4))
    frags.append(line(205, 195, 225, 185, color=RED_S, sw=4))

    b_q, _, _ = textbox(140, 135, "Підведене тепло Q > 0\n(Теплообмін крізь межу)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_q)

    # Виконана робота W (стрілка справа)
    frags.append(line(655, 185, 800, 185, color=GREEN_S, sw=4))
    # Стрілка налітання
    frags.append(line(780, 175, 800, 185, color=GREEN_S, sw=4))
    frags.append(line(780, 195, 800, 185, color=GREEN_S, sw=4))

    b_w, _, _ = textbox(730, 135, "Виконана робота W > 0\n(Механічна робота на поршень)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_w)

    # Межа системи
    frags.append(text(440, 285, "Гнучка межа (рухомий поршень)", size=11, italic=True, color="#475569"))

    # Нижнє підсумкове рівняння
    b_eq, _, _ = textbox(440, 335, "Перший закон термодинаміки:  Q = ΔU + W   (або   ΔU = Q - W)", size=13, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_eq)

    render(os.path.join(IMG, "energy-balance-system.svg"), W, H, *frags)


def fig_joule_expansion():
    """joule-expansion.svg: Дослід Джоуля з вільним розширенням газу у вакуум."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Дослід Джоуля: вільне розширення ідеального газу у вакуум (Q = 0, W = 0)", size=15, bold=True, color="#1e293b"))

    # Калориметричний бак з водою
    frags.append(rect(50, 60, 780, 270, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=12))
    frags.append(text(440, 85, "ТЕПЛОІЗОЛЬОВАНИЙ КАЛОРИМЕТР З ВОДОЮ (Q_зовн = 0)", size=12, bold=True, color="#0369a1"))

    # Лівий балон (Газ під тиском P₁)
    frags.append(rect(140, 120, 240, 150, fill=BLUE_F, stroke=BLUE_S, sw=2.5, rx=20))
    frags.append(text(260, 150, "Балон А", size=13, bold=True, color=BLUE_S))
    frags.append(text(260, 185, "Стиснутий газ\nP₁, V₁, T₁", size=12, bold=True, color="#1e293b"))

    # Правий балон (Ваккум)
    frags.append(rect(500, 120, 240, 150, fill="#f1f5f9", stroke="#64748b", sw=2.5, rx=20))
    frags.append(text(620, 150, "Балон Б", size=13, bold=True, color="#475569"))
    frags.append(text(620, 185, "ВАКУУМ\nP = 0, V₂", size=12, bold=True, color="#64748b"))

    # Трубка із краном по центру (два окремих сегменти)
    frags.append(rect(380, 180, 50, 30, fill="#cbd5e1", stroke="#475569", sw=2))
    frags.append(rect(450, 180, 50, 30, fill="#cbd5e1", stroke="#475569", sw=2))
    # Кран (вентиль)
    frags.append(rect(430, 160, 20, 70, fill=RED_S, stroke="#7f1d1d", sw=2, rx=3))
    frags.append(circle(440, 142, 12, fill=RED_F, stroke=RED_S, sw=2))
    frags.append(text(440, 145, "Кран", size=10, bold=True, color=RED_S))

    # Прецизійний термометр у воді
    frags.append(rect(750, 100, 18, 180, fill="#ffffff", stroke="#475569", sw=1.5, rx=9))
    frags.append(circle(759, 275, 15, fill=RED_S, stroke="#475569", sw=1.5))
    frags.append(text(759, 85, "Термометр ΔT = 0", size=10, bold=True, color=RED_S))

    # Нижній висновок експерименту
    b_res, _, _ = textbox(440, 355, "Результат Вільнера-Джоуля:   W = 0 (розширення проти 0 тиску), Q = 0   ⇒   ΔU = 0\nДля ідеального газу внутрішня енергія залежить ЛИШЕ від температури: U = U(T)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_res)

    render(os.path.join(IMG, "joule-expansion.svg"), W, H, *frags)


def fig_thermo_processes():
    """thermo-processes.svg: Порівняння класичних ізопроцесів і адіабати на P-V діаграмі."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 30, "Чотири базові термодинамічні процеси з початкового стану (P₁, V₁)", size=15, bold=True, color="#1e293b"))

    # Осі P-V
    frags.append(line(80, 370, 520, 370, color="#475569", sw=2))  # V
    frags.append(line(80, 370, 80, 60, color="#475569", sw=2))     # P
    frags.append(text(520, 390, "Об'єм V", size=11, bold=True, color="#1e293b"))
    frags.append(text(55, 60, "Тиск P", size=11, bold=True, color="#1e293b"))

    # Початковий стан 1 (180, 140)
    x1, y1 = 180, 140

    # 1. Ізобарний (P = const): горизонтальна лінія вправо (180, 140) -> (460, 140)
    frags.append(line(x1, y1, 460, y1, color=BLUE_S, sw=3))
    frags.append(circle(460, y1, 5, fill=BLUE_S, stroke="#1e293b", sw=1))
    frags.append(text(475, 144, "1. Ізобарний (P = const)", size=11, bold=True, color=BLUE_S))

    # 2. Ізотермічний (T = const): гіпербола P ~ 1/V
    pts_iso = []
    for t in range(0, 101):
        vx = x1 + t * 2.8
        vy = y1 + 0.003 * (t ** 2) + 0.9 * t
        pts_iso.append((vx, vy))
    frags.append(polyline(pts_iso, color=GREEN_S, sw=3))
    end_iso = pts_iso[-1]
    frags.append(circle(end_iso[0], end_iso[1], 5, fill=GREEN_S, stroke="#1e293b", sw=1))
    frags.append(text(end_iso[0] + 12, end_iso[1] + 4, "2. Ізотермічний (T = const)", size=11, bold=True, color=GREEN_S))

    # 3. Адіабатний (Q = 0): стрімкіша крива P ~ 1/V^γ
    pts_adiab = []
    for t in range(0, 101):
        vx = x1 + t * 2.3
        vy = y1 + 0.008 * (t ** 2) + 1.2 * t
        pts_adiab.append((vx, vy))
    frags.append(polyline(pts_adiab, color=PURPLE_S, sw=3))
    end_adiab = pts_adiab[-1]
    frags.append(circle(end_adiab[0], end_adiab[1], 5, fill=PURPLE_S, stroke="#1e293b", sw=1))
    frags.append(text(end_adiab[0] + 12, end_adiab[1] + 4, "3. Адіабатний (Q = 0)", size=11, bold=True, color=PURPLE_S))

    # 4. Ізохорний (V = const): вертикальна лінія вниз (180, 140) -> (180, 330)
    frags.append(line(x1, y1, x1, 330, color=RED_S, sw=3))
    frags.append(circle(x1, 330, 5, fill=RED_S, stroke="#1e293b", sw=1))
    frags.append(text(x1 - 10, 350, "4. Ізохорний (V = const)", size=11, bold=True, color=RED_S, anchor="middle"))

    # Початкова точка Стан 1
    frags.append(circle(x1, y1, 7, fill=AMBER_S, stroke="#1e293b", sw=2))
    frags.append(text(x1 - 10, y1 - 12, "Стан 1 (P₁, V₁, T₁)", size=11, bold=True, color=AMBER_S))

    # Права таблиця з формулами
    frags.append(rect(540, 60, 310, 320, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(695, 82, "Формули Першого закону", size=13, bold=True, color="#1e293b"))

    b_t1, _, _ = textbox(695, 130, "Ізобарний (P = const):\nQ = n C_p ΔT ,  W = P ΔV\nΔU = n C_v ΔT", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_t1)

    b_t2, _, _ = textbox(695, 200, "Ізотермічний (T = const):\nΔU = 0  ⇒  Q = W\nW = n R T ln(V₂ / V₁)", size=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_t2)

    b_t3, _, _ = textbox(695, 270, "Адіабатний (Q = 0):\nQ = 0  ⇒  W = -ΔU\nP V^γ = const  (γ = C_p / C_v)", size=10, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_t3)

    b_t4, _, _ = textbox(695, 340, "Ізохорний (V = const):\nW = 0  ⇒  Q = ΔU\nQ = n C_v ΔT", size=10, fill=RED_F, stroke=RED_S)
    frags.append(b_t4)

    render(os.path.join(IMG, "thermo-processes.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_p_v_work()
    fig_energy_balance_system()
    fig_joule_expansion()
    fig_thermo_processes()
    print("Всі фігури для first-law-thermodynamics успішно згенеровано.")
