# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path_builder(points, stroke=INK, sw=2, fill="none", dash=None):
    d_str = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in points)
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Механізми розсіювання носіїв у твердому тілі
# ════════════════════════════════════════════════════════════════════════════
def fig_scattering_mechanisms():
    W, H = 840, 360
    f = []

    f.append(text(420, 25, "Основні механізми розсіювання носіїв заряду в кристалі", size=16, bold=True, color=INK))

    # 3 панелі
    # Панель 1: Фононне розсіювання (20, 50, 250, 280)
    f.append(rect(20, 50, 250, 280, fill="#fafafa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(145, 75, "1. Фонони (ґратка)", size=14, bold=True, color=INK))
    f.append(text(145, 95, "Теплові коливання іонів", size=11, color=MUTED))

    # Схема ґратки з коливаннями
    ions_p1 = [(60, 150), (145, 135), (230, 160),
               (70, 230), (140, 245), (220, 225)]
    for ix, iy in ions_p1:
        f.append(circle(ix, iy, 12, fill="#e8f8f5", stroke=POS, sw=1.8))
        f.append(text(ix, iy + 4, "+", size=14, bold=True, color=POS))
    # Хвиля коливань
    f.append(path_builder([(40, 190), (90, 175), (140, 205), (190, 180), (240, 195)], stroke="#16a085", sw=1.5, dash="3 3"))
    # Траєкторія електрона з відхиленням
    e_traj1 = [(35, 140), (145, 135), (225, 270)]
    f.append(path_builder(e_traj1, stroke=NEG, sw=2))
    f.append(circle(35, 140, 5, fill=NEG, stroke=INK, sw=1))
    f.append(text(145, 305, "Температурне зростання: 1/tau ∝ T", size=11, bold=True, color=INK))

    # Панель 2: Іонізовані домішки (295, 50, 250, 280)
    f.append(rect(295, 50, 250, 280, fill="#fafafa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(420, 75, "2. Іонізовані домішки", size=14, bold=True, color=INK))
    f.append(text(420, 95, "Кулонівське відхилення", size=11, color=MUTED))

    # Домішковий центр (великий іон)
    f.append(circle(420, 180, 18, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(420, 186, "+Z", size=13, bold=True, color=POS))
    # Екрановане поле (пунктирне коло)
    f.append('<circle cx="420" cy="180" r="55" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 4"/>' % POS)
    f.append(text(420, 115, "r_TF (екранування)", size=10, color=POS))

    # Гіперболічні траєкторії електронів
    f.append(path_builder([(315, 130), (390, 150), (450, 240)], stroke=NEG, sw=2))
    f.append(circle(315, 130, 5, fill=NEG, stroke=INK, sw=1))
    f.append(path_builder([(315, 230), (380, 200), (460, 120)], stroke=NEG, sw=1.5, dash="4 2"))

    f.append(text(420, 305, "Залишковий опір при T → 0 K", size=11, bold=True, color=INK))

    # Панель 3: Граничне розсіювання (570, 50, 250, 280)
    f.append(rect(570, 50, 250, 280, fill="#fafafa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(695, 75, "3. Поверхні та межі", size=14, bold=True, color=INK))
    f.append(text(695, 95, "Розмірний ефект (d ≤ lambda)", size=11, color=MUTED))

    # Межі плівки
    f.append(line(585, 130, 805, 130, color=INK, sw=2.5))
    f.append(line(585, 250, 805, 250, color=INK, sw=2.5))
    f.append(text(800, 120, "Верхня межа", size=10, color=MUTED))
    f.append(text(800, 265, "Нижня межа", size=10, color=MUTED))

    # Двостороння стрілка товщини d
    f.append(arrow(605, 130, 605, 250, color=FIELD, sw=1.5))
    f.append(arrow(605, 250, 605, 130, color=FIELD, sw=1.5))
    f.append(text(615, 195, "d", size=13, bold=True, color=FIELD))

    # Траєкторія з відбиванням від поверхонь
    surf_traj = [(620, 190), (670, 130), (730, 250), (780, 170)]
    f.append(path_builder(surf_traj, stroke=NEG, sw=2))
    f.append(circle(620, 190, 5, fill=NEG, stroke=INK, sw=1))

    f.append(text(695, 305, "Дифузне розсіювання на межах", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "scattering-mechanisms.svg"), W, H, "\n".join(f))

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Залежність питомого опору від температури та правило Маттіссена
# ════════════════════════════════════════════════════════════════════════════
def fig_matthiessen_rule():
    W, H = 760, 400
    f = []

    f.append(text(380, 25, "Температурна залежність питомого опору та правило Маттіссена", size=16, bold=True, color=INK))

    # Осі координат
    f.append(arrow(80, 340, 700, 340, color=INK, sw=2)) # X axis: T
    f.append(arrow(80, 340, 80, 50, color=INK, sw=2))   # Y axis: rho
    f.append(text(710, 345, "Т (К)", size=13, bold=True, color=INK))
    f.append(text(45, 50, "ρ (Ом·м)", size=13, bold=True, color=INK))

    # Позначка абсолютного нуля
    f.append(text(80, 360, "0 K", size=11, bold=True, color=INK))

    # Пунктирна горизонтальна лінія залишкового опору rho_res
    f.append(line(80, 260, 680, 260, color=POS, sw=1.8, dash="5 4"))
    f.append(text(200, 250, "Залишковий опір ρ_res (домішки, дефекти)", size=12, bold=True, color=POS))
    f.append(line(75, 260, 85, 260, color=POS, sw=2))
    f.append(text(40, 264, "ρ_res", size=11, bold=True, color=POS))

    # Крива фононного внеску rho_ph(T)
    pts_ph = [(80, 340), (150, 338), (220, 330), (320, 290), (450, 220), (680, 100)]
    f.append(path_builder(pts_ph, stroke="#2980b9", sw=2, dash="4 3"))
    f.append(text(540, 190, "Фононний внесок ρ_ph(T)", size=12, bold=True, color="#2980b9"))

    # Загальна крива rho_total(T) = rho_res + rho_ph(T)
    pts_tot = [(80, 260), (150, 258), (220, 250), (320, 210), (450, 140), (680, 20)]
    f.append(path_builder(pts_tot, stroke=NEG, sw=2.8))
    f.append(text(500, 45, "ρ_total(T) = ρ_res + ρ_ph(T)", size=13, bold=True, color=NEG))

    # Температура Дебая Theta_D
    f.append(line(320, 340, 320, 70, color=MUTED, sw=1.2, dash="3 3"))
    f.append(circle(320, 340, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(320, 360, "Θ_D (Температура Дебая)", size=11, bold=True, color=MUTED))

    # Пояснення областей
    f.append(text(180, 375, "Область Блоха — Грюнайзена (ρ ∝ T⁵)", size=11, color=MUTED))
    f.append(text(520, 375, "Високотемпературна область (ρ ∝ T)", size=11, color=MUTED))

    render(os.path.join(OUT, "matthiessen-rule.svg"), W, H, "\n".join(f))

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Повний час між зіткненнями vs транспортний час релаксації
# ════════════════════════════════════════════════════════════════════════════
def fig_transport_scattering():
    W, H = 800, 360
    f = []

    f.append(text(400, 25, "Порівняння малокутового та ізотропного розсіювання імпульсу", size=16, bold=True, color=INK))

    # Розділювач
    f.append(line(400, 45, 400, 340, color=MUTED, sw=1.5, dash="4 4"))

    # Ліва панель: Малокутове розсіювання
    f.append(text(200, 55, "а) Малокутове розсіювання (θ ≪ 90°)", size=14, bold=True, color=INK))
    f.append(text(200, 75, "Низькі T (акустичні фонони), макроскопічні дефекти", size=11, color=MUTED))

    # Вхідний вектор k
    f.append(arrow(40, 200, 180, 200, color=FIELD, sw=2.5))
    f.append(text(100, 190, "Вхідний імпульс k", size=12, bold=True, color=FIELD))

    # Центр розсіювання
    f.append(circle(180, 200, 8, fill=POS, stroke=INK, sw=1.5))

    # Вихідний вектор k' під малим кутом
    f.append(arrow(180, 200, 330, 160, color=NEG, sw=2.5))
    f.append(text(270, 165, "k'", size=12, bold=True, color=NEG))

    # Пунктирне продовження початкового напрямку
    f.append(line(180, 200, 340, 200, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(240, 215, "Кут θ ≪ 1", size=11, bold=True, color=INK))

    # Формула для лівої панелі
    f.append(rect(40, 250, 320, 75, fill="#f4f6f7", stroke=LINE, sw=1, rx=5))
    f.append(text(200, 275, "(1 - cos θ) ≪ 1  ⟹  Втрата імпульсу мала", size=12, bold=True, color=INK))
    f.append(text(200, 305, "Транспортний час tau_tr ≫ tau_0", size=12, bold=True, color=POS))

    # Права панель: Ізотропне/великокутове розсіювання
    f.append(text(600, 55, "б) Ізотропне розсіювання (⟨cos θ⟩ = 0)", size=14, bold=True, color=INK))
    f.append(text(600, 75, "Високі T, короткосяжні точкові дефекти", size=11, color=MUTED))

    # Вхідний вектор k
    f.append(arrow(440, 200, 580, 200, color=FIELD, sw=2.5))
    f.append(text(500, 190, "Вхідний імпульс k", size=12, bold=True, color=FIELD))

    # Центр розсіювання
    f.append(circle(580, 200, 8, fill=POS, stroke=INK, sw=1.5))

    # Веєрна розбіжність вихідних векторів у всі боки
    out_angles = [(-130, 670, 110), (-70, 680, 150), (40, 680, 250), (110, 650, 280), (160, 510, 260)]
    for _, ox, oy in out_angles:
        f.append(arrow(580, 200, ox, oy, color=NEG, sw=1.8))

    # Формула для правої панелі
    f.append(rect(440, 250, 320, 75, fill="#f4f6f7", stroke=LINE, sw=1, rx=5))
    f.append(text(600, 275, "⟨cos θ⟩ = 0  ⟹  Повна втрата пам'яті", size=12, bold=True, color=INK))
    f.append(text(600, 305, "Транспортний час tau_tr = tau_0", size=12, bold=True, color=NEG))

    render(os.path.join(OUT, "transport-vs-total-scattering.svg"), W, H, "\n".join(f))

if __name__ == "__main__":
    fig_scattering_mechanisms()
    fig_matthiessen_rule()
    fig_transport_scattering()
    print("All figures successfully generated in img/")
