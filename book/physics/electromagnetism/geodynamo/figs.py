# -*- coding: utf-8 -*-
"""Фігури для теми «Геодинамо» (book/physics/electromagnetism/geodynamo)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
CORE_IN_F, CORE_IN_S   = "#fef2f2", "#dc2626"
CORE_OUT_F, CORE_OUT_S = "#fff7ed", "#ea580c"
MANTLE_F, MANTLE_S     = "#fefce8", "#ca8a04"
MAG_BLUE_F, MAG_BLUE_S = "#eff6ff", "#2563eb"
PURPLE_F, PURPLE_S     = "#faf5ff", "#9333ea"
TEAL_F, TEAL_S         = "#f0fdf4", "#16a34a"
GRAY_F, GRAY_S         = "#f8fafc", "#64748b"

def fig_core_structure():
    """core-structure.svg: Будова Землі та конвективні потоки в рідкому зовнішньому ядрі."""
    W, H = 840, 520
    frags = []

    # Заголовок
    frags.append(text(W/2, 28, "Будова ядра Землі та джерела енергії геодинамо", size=16, bold=True, color="#0f172a"))

    # Центральна геометрія (зсунута вліво)
    cx, cy = 250, 270

    # Мантія
    frags.append(circle(cx, cy, 200, fill=MANTLE_F, stroke=MANTLE_S, sw=2))
    frags.append(text(cx, cy - 175, "Мантія (силікати, R ≈ 6371 км)", size=11, color="#854d0e", bold=True))

    # Зовнішнє ядро
    frags.append(circle(cx, cy, 130, fill=CORE_OUT_F, stroke=CORE_OUT_S, sw=2))
    frags.append(text(cx, cy - 105, "Рідке зовнішнє ядро (Fe-Ni, 2260 км)", size=11, color="#c2410c", bold=True))

    # Тверде внутрішнє ядро
    frags.append(circle(cx, cy, 55, fill=CORE_IN_F, stroke=CORE_IN_S, sw=2))
    frags.append(mtext(cx, cy - 6, ["Тверде ядро", "R ≈ 1220 км"], size=10, color="#991b1b", bold=True))

    # Вісь обертання та Земна ротація Ω
    frags.append(line(cx, cy - 230, cx, cy + 230, color="#334155", sw=1.5, dash="4 4"))
    frags.append(text(cx + 15, cy - 215, "Вісь обертання (Ω)", size=11, bold=True, color="#334155"))

    # Конвективні плюми (стрілки в зовнішньому ядрі)
    frags.append(arrow(cx + 65, cy + 30, cx + 105, cy + 45, color="#d97706", sw=2))
    frags.append(arrow(cx - 65, cy - 30, cx - 105, cy - 45, color="#d97706", sw=2))
    frags.append(arrow(cx - 30, cy + 65, cx - 45, cy + 105, color="#dc2626", sw=2))
    frags.append(arrow(cx + 30, cy - 65, cx + 45, cy - 105, color="#dc2626", sw=2))

    # Інформаційні блоки праворуч
    b1, _, _ = textbox(630, 95, "Тверде внутрішнє ядро\n• Кристалізація чистого заліза (Fe-Ni)\n• Зростання радиуса: ~1 мм/рік\n• Виділення прихованої теплоти кристалізації", size=11, fill=CORE_IN_F, stroke=CORE_IN_S, min_w=340)
    frags.append(b1)

    b2, _, _ = textbox(630, 215, "Рідке зовнішнє ядро\n• Електропровідність σ ≈ 10⁶ Ом⁻¹м⁻¹\n• Кінематична в'язкість ν ≈ 10⁻⁶ м²/с\n• Швидкість конвективних потоків: U ≈ 0.2–1 мм/с", size=11, fill=CORE_OUT_F, stroke=CORE_OUT_S, min_w=340)
    frags.append(b2)

    b3, _, _ = textbox(630, 335, "Плавучість та джерела енергії (Q ≈ 12 ТВт)\n• Теплова конвекція: остигання + радіоактивний розпад\n• Композиційна плавучість: виштовхування легких\n  елементів (S, Si, O) на межі з внутрішнім ядром", size=11, fill=MANTLE_F, stroke=MANTLE_S, min_w=340)
    frags.append(b3)

    b4, _, _ = textbox(630, 445, "Магнітне число Рейнольдса\nRm = U·L / η ≈ 100–1000 >> 1\nПотік «вморожений» у провідну рідину", size=11, fill=MAG_BLUE_F, stroke=MAG_BLUE_S, min_w=340)
    frags.append(b4)

    # Зв'язувальні лінії
    frags.append(line(cx + 40, cy - 25, 455, 95, color="#cbd5e1", sw=1.2, dash="2 2"))
    frags.append(line(cx + 100, cy, 455, 215, color="#cbd5e1", sw=1.2, dash="2 2"))
    frags.append(line(cx + 160, cy + 100, 455, 335, color="#cbd5e1", sw=1.2, dash="2 2"))

    render(os.path.join(IMG, "core-structure.svg"), W, H, *frags)

def fig_alpha_omega_cycle():
    """alpha-omega-cycle.svg: Цикл Альфа-Омега динамо (генерація полів)."""
    W, H = 880, 480
    frags = []

    frags.append(text(W/2, 28, "Самозбуджуваний генераційний цикл Альфа-Омега динамо", size=16, bold=True, color="#0f172a"))

    # Ліва панель: Омега-ефект
    frags.append(rect(20, 60, 405, 395, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(222, 88, "Омега-ефект (Ω-effect)", size=14, bold=True, color=MAG_BLUE_S))
    frags.append(text(222, 110, "Полоїдальне поле → Тороїдальне поле", size=11, italic=True, color="#475569"))

    # Схема Ω-ефекту
    cx1, cy1 = 222, 230
    frags.append(circle(cx1, cy1, 75, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(line(cx1, cy1 - 90, cx1, cy1 + 90, color="#334155", sw=1.2, dash="3 3"))
    frags.append(text(cx1 + 10, cy1 - 80, "Ω(r,θ)", size=10, bold=True, color="#334155"))

    # Витягування силових ліній в тороїдальне поле
    frags.append(line(cx1 - 50, cy1 - 40, cx1 + 50, cy1 - 40, color=MAG_BLUE_S, sw=2))
    frags.append(line(cx1 - 65, cy1, cx1 + 65, cy1, color=MAG_BLUE_S, sw=2.5))
    frags.append(line(cx1 - 50, cy1 + 40, cx1 + 50, cy1 + 40, color=MAG_BLUE_S, sw=2))

    frags.append(arrow(cx1 + 40, cy1 - 40, cx1 + 58, cy1 - 40, color=MAG_BLUE_S, sw=2))
    frags.append(arrow(cx1 + 55, cy1, cx1 + 72, cy1, color=MAG_BLUE_S, sw=2.5))

    b_omega, _, _ = textbox(222, 390, "Диференціальне обертання (зсувний потік ∂Ω/∂r)\nвитягує меридіональне полоїдальне поле B_pol\nу потужне широтне тороїдальне поле B_tor", size=11, fill=MAG_BLUE_F, stroke=MAG_BLUE_S, min_w=370)
    frags.append(b_omega)

    # Права панель: Альфа-ефект
    frags.append(rect(455, 60, 405, 395, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(657, 88, "Альфа-ефект (α-effect)", size=14, bold=True, color=PURPLE_S))
    frags.append(text(657, 110, "Тороїдальне поле → Полоїдальне поле", size=11, italic=True, color="#475569"))

    # Схема α-ефекту
    cx2, cy2 = 657, 230
    frags.append(circle(cx2, cy2, 75, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    
    # Спіральний вихор конвекції (сила Коріоліса)
    frags.append(circle(cx2 - 25, cy2 - 20, 22, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5))
    frags.append(circle(cx2 + 25, cy2 + 20, 22, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5))
    frags.append(arrow(cx2 - 25, cy2 - 42, cx2 - 10, cy2 - 42, color=PURPLE_S, sw=1.8))
    frags.append(arrow(cx2 + 25, cy2 + 42, cx2 + 40, cy2 + 42, color=PURPLE_S, sw=1.8))
    frags.append(text(cx2, cy2, "h = v · (∇ × v)", size=11, bold=True, color=PURPLE_S))

    b_alpha, _, _ = textbox(657, 390, "Конвективні підйоми + сила Коріоліса\nзакручують тороїдальні трубки B_tor,\nутворюючи полоїдальні петлі B_pol", size=11, fill=PURPLE_F, stroke=PURPLE_S, min_w=370)
    frags.append(b_alpha)

    # Зв'язувальні стрілки циклу
    frags.append(arrow(425, 180, 455, 180, color=TEAL_S, sw=2.5))
    frags.append(text(440, 165, "B_tor", size=11, bold=True, color=TEAL_S))

    frags.append(arrow(455, 300, 425, 300, color=TEAL_S, sw=2.5))
    frags.append(text(440, 318, "B_pol", size=11, bold=True, color=TEAL_S))

    render(os.path.join(IMG, "alpha-omega-cycle.svg"), W, H, *frags)

def fig_rikitake_dynamo():
    """rikitake-dynamo.svg: Схема дводискового динамо Рікітаке та хаотичні інверсії."""
    W, H = 840, 460
    frags = []

    frags.append(text(W/2, 28, "Модель дводискового динамо Рікітаке та динаміка інверсій", size=16, bold=True, color="#0f172a"))

    # Лівий блок: Схема двох дисків
    frags.append(rect(20, 60, 440, 380, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(240, 88, "Електромеханічна система Рікітаке", size=13, bold=True, color="#1e293b"))

    # Диск 1
    frags.append(circle(130, 200, 45, fill="#e2e8f0", stroke="#475569", sw=2))
    frags.append(circle(130, 200, 10, fill="#64748b", stroke="#334155", sw=1.5))
    frags.append(text(130, 204, "D₁", size=12, bold=True, color="#ffffff"))
    frags.append(text(130, 260, "Диск 1 (Ω₁)", size=11, bold=True, color="#334155"))

    # Диск 2
    frags.append(circle(350, 200, 45, fill="#e2e8f0", stroke="#475569", sw=2))
    frags.append(circle(350, 200, 10, fill="#64748b", stroke="#334155", sw=1.5))
    frags.append(text(350, 204, "D₂", size=12, bold=True, color="#ffffff"))
    frags.append(text(350, 260, "Диск 2 (Ω₂)", size=11, bold=True, color="#334155"))

    # Перехресні котушки та струми
    frags.append(arrow(175, 180, 305, 180, color=CORE_OUT_S, sw=2))
    frags.append(text(240, 170, "Струм I₁ → Котушка 2", size=10, bold=True, color=CORE_OUT_S))

    frags.append(arrow(305, 220, 175, 220, color=MAG_BLUE_S, sw=2))
    frags.append(text(240, 235, "Струм I₂ → Котушка 1", size=10, bold=True, color=MAG_BLUE_S))

    b_eq, _, _ = textbox(240, 360, "Нелінійні рівняння руху:\ndx/dt = -μ·x + y·z\ndy/dt = -μ·y + (z - a)·x\ndz/dt = 1 - x·y", size=11, fill="#ffffff", stroke="#94a3b8", min_w=400)
    frags.append(b_eq)

    # Правий блок: Хаотичний атрактор та інверсії
    frags.append(rect(480, 60, 340, 380, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(650, 88, "Хаотична зміна полярності", size=13, bold=True, color="#1e293b"))

    # Графік інверсій (стилізований часовий ряд B(t))
    frags.append(rect(500, 120, 300, 140, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(line(500, 190, 800, 190, color="#94a3b8", sw=1, dash="2 2"))
    frags.append(text(510, 135, "B_z(t)", size=10, bold=True, color="#334155"))
    frags.append(text(780, 202, "t", size=10, bold=True, color="#334155"))

    # Синусоїдальні осциляції зі стрибками полярності
    pts = [(500,160), (520,140), (540,170), (560,145), (580,185), (595,220), (610,235), (630,210), (650,240), (670,205), (690,150), (710,135), (730,165), (750,140), (770,185), (800,145)]
    for i in range(len(pts)-1):
        frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=CORE_IN_S, sw=1.8))

    b_rev, _, _ = textbox(650, 345, "Властивості інверсій:\n• Нерегулярні інтервали (10⁵–10⁶ років)\n• Тривалість переходу: 2000–10000 років\n• Падіння напруженості на 80–90% під час інверсії", size=10.5, fill=CORE_IN_F, stroke=CORE_IN_S, min_w=310)
    frags.append(b_rev)

    render(os.path.join(IMG, "rikitake-dynamo.svg"), W, H, *frags)

def fig_igrf_harmonics():
    """igrf-harmonics.svg: Сферичні гармоніки геомагнітного поля (модель IGRF)."""
    W, H = 860, 440
    frags = []

    frags.append(text(W/2, 28, "Сферичний гармонічний аналіз поля (модель IGRF)", size=16, bold=True, color="#0f172a"))

    # Три основні компоненти гармонік (Диполь, Квадруполь, Октуполь)
    xs = [150, 430, 710]
    titles = ["Дипольний член (n=1)", "Квадрупольний член (n=2)", "Октупольний член (n=3)"]
    weights = ["~90% енергії поля", "~7% енергії поля", "~2% енергії поля"]
    fills = [MAG_BLUE_F, PURPLE_F, TEAL_F]
    strokes = [MAG_BLUE_S, PURPLE_S, TEAL_S]

    for x, t, w_lbl, f, s in zip(xs, titles, weights, fills, strokes):
        frags.append(rect(x - 120, 60, 240, 220, fill=f, stroke=s, rx=8))
        frags.append(text(x, 88, t, size=13, bold=True, color=s))
        frags.append(text(x, 108, w_lbl, size=10.5, italic=True, color="#475569"))
        
        # Сфера зі схематичними силовою конфігурацією
        frags.append(circle(x, 175, 45, fill="#ffffff", stroke=s, sw=1.5))
        frags.append(line(x, 125, x, 225, color="#64748b", sw=1, dash="2 2"))
        
        if "n=1" in t:
            frags.append(arrow(x - 25, 205, x - 25, 145, color=s, sw=1.8))
            frags.append(arrow(x + 25, 205, x + 25, 145, color=s, sw=1.8))
            frags.append(text(x, 248, "g₁⁰, g₁¹, h₁¹", size=11, bold=True, color=s))
        elif "n=2" in t:
            frags.append(circle(x - 18, 160, 10, fill=PURPLE_F, stroke=s, sw=1.2))
            frags.append(circle(x + 18, 190, 10, fill=PURPLE_F, stroke=s, sw=1.2))
            frags.append(text(x, 248, "g₂⁰, g₂¹, h₂¹, g₂², h₂²", size=11, bold=True, color=s))
        else:
            frags.append(circle(x - 20, 155, 8, fill=TEAL_F, stroke=s, sw=1))
            frags.append(circle(x + 20, 155, 8, fill=TEAL_F, stroke=s, sw=1))
            frags.append(circle(x, 195, 8, fill=TEAL_F, stroke=s, sw=1))
            frags.append(text(x, 248, "g₃⁰..g₃³, h₃¹..h₃³", size=11, bold=True, color=s))

    # Нижній блок: Рівняння Гаусса
    b_gauss, _, _ = textbox(W/2, 360, "Скалярний магнітний потенціал Гаусса:\nV(r,θ,φ) = a · ∑ₙ (a/r)ⁿ⁺¹ ∑ₘ [ gₙᵐ cos(mφ) + hₙᵐ sin(mφ) ] Pₙᵐ(cos θ)\n• Множник (a/r)ⁿ⁺¹ описує швидкість згасання гармонік з відстанню від ядра\n• Високі гармоніки (n > 13) відповідають намагніченості земної кори", size=11, fill="#f8fafc", stroke="#cbd5e1", min_w=800)
    frags.append(b_gauss)

    render(os.path.join(IMG, "igrf-harmonics.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_core_structure()
    fig_alpha_omega_cycle()
    fig_rikitake_dynamo()
    fig_igrf_harmonics()
    print("Всі фігури геодинамо згенеровано успішно.")
