# -*- coding: utf-8 -*-
"""Фігури теми «Скид вантажу: механізм і точність».
Генерація SVG: python figs.py -> ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_release_mechanisms():
    """Фігура 1: Порівняння сервопривідного та соленоїдного замків скиду."""
    W, H = 840, 380
    parts = []

    # Тло двох панелей
    parts.append(rect(20, 20, 385, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(435, 20, 385, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовки панелей
    tb1, _, _ = textbox(212, 45, "Сервопривідний штифтовий замок", size=14, bold=True, fill="#e2e8f0", stroke="#94a3b8")
    tb2, _, _ = textbox(627, 45, "Електромагнітний соленоїдний замок", size=14, bold=True, fill="#e2e8f0", stroke="#94a3b8")
    parts.extend([tb1, tb2])

    # Панель 1 (Сервопривід)
    # Корпус сервоприводу
    parts.append(rect(50, 90, 90, 70, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(95, 130, "Серво", size=13, color=INK, bold=True))

    # Важіль сервоприводу (качалка)
    parts.append(circle(140, 125, 6, fill=LINE, stroke=LINE))
    parts.append(line(140, 125, 175, 95, color=POS, sw=3))
    parts.append(circle(175, 95, 4, fill=POS, stroke=POS))

    # Тяга від качалки до штифта
    parts.append(line(175, 95, 240, 95, color=LINE, sw=2, dash="3 3"))

    # Напрямна втулка і штифт
    parts.append(rect(230, 85, 60, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    parts.append(line(220, 95, 320, 95, color=POS, sw=4)) # Штифт

    # Вушко підвісу вантажу
    parts.append(circle(290, 115, 12, fill="none", stroke="#0284c7", sw=3))
    parts.append(line(290, 127, 290, 175, color="#0284c7", sw=2)) # стропа
    parts.append(rect(260, 175, 60, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    parts.append(text(290, 202, "Вантаж m", size=12, color="#0369a1", bold=True))

    # Стрілки сил і тертя
    parts.append(arrow(290, 220, 290, 255, color=POS, sw=1.8))
    parts.append(text(305, 245, "F_g = m·g", size=11, color=POS, anchor="start"))

    parts.append(arrow(265, 95, 235, 95, color=NEG, sw=1.8))
    parts.append(text(250, 75, "F_тяг", size=11, color=NEG))

    parts.append(text(290, 148, "F_тер = μ·m·g", size=11, color="#b91c1c"))

    # Характеристики сервоприводу
    fb1 = fitbox(40, 265, 345, 80,
                 "Час відкриття: 80–150 мс\n"
                 "Момент: τ = F_тер · r_важеля\n"
                 "Ризик: клин при перевантаженні g",
                 size=12, pad=6, fill="#ffffff", stroke="#cbd5e1")
    parts.append(fb1)

    # Панель 2 (Соленоїд)
    # Верхня та нижня секції котушки (розріз соленоїда)
    parts.append(rect(470, 80, 110, 24, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    parts.append(text(525, 96, "Котушка (L)", size=11, color="#b45309", bold=True))
    parts.append(rect(470, 136, 110, 24, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    parts.append(text(525, 152, "N витків", size=11, color="#b45309"))

    # Сердечник-якір (рухомий штифт у каналі)
    parts.append(rect(510, 110, 170, 20, fill="#94a3b8", stroke=LINE, sw=1.5, rx=2))
    parts.append(line(680, 120, 715, 120, color=POS, sw=4)) # виступаючий кінчик

    # Зворотна пружина
    parts.append(line(460, 120, 510, 120, color=MUTED, sw=2, dash="2 2"))
    parts.append(text(485, 114, "Пружина", size=10, color=MUTED))

    # Захисний діод Flyback
    parts.append(rect(470, 175, 110, 30, fill="#ffffff", stroke="#d97706", sw=1.2, rx=3))
    parts.append(text(525, 194, "Flyback діод / TVS", size=11, color="#b45309"))

    # Вушко підвісу вантажу соленоїда
    parts.append(circle(700, 138, 11, fill="none", stroke="#0284c7", sw=3))
    parts.append(line(700, 149, 700, 185, color="#0284c7", sw=2))
    parts.append(rect(670, 185, 60, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    parts.append(text(700, 212, "Вантаж m", size=12, color="#0369a1", bold=True))

    parts.append(arrow(600, 120, 540, 120, color=NEG, sw=1.8))
    parts.append(text(570, 115, "F_магн", size=10, color=NEG))

    # Характеристики соленоїда
    fb2 = fitbox(455, 265, 345, 80,
                 "Час спрацьовування: 5–15 мс\n"
                 "Імпульсний струм: 2–6 А (BEC/MOSFET)\n"
                 "Ризик: залишкова намагніченість якоря",
                 size=12, pad=6, fill="#ffffff", stroke="#cbd5e1")
    parts.append(fb2)

    render(os.path.join(IMG, "servo-vs-solenoid-release.svg"), W, H, *parts)


def fig_drop_ballistics():
    """Фігура 2: Траєкторія вільного падіння вантажу (вакуум vs опір повітря + вітер)."""
    W, H = 840, 420
    parts = []

    # Оси координат
    L, R = 80, 780
    ground_y = 350
    drop_x, drop_y = 120, 90

    # Земля
    parts.append(line(L, ground_y, R, ground_y, color="#475569", sw=2))
    parts.append(rect(L, ground_y, R - L, 25, fill="#f1f5f9", stroke="none"))
    parts.append(text(R - 40, ground_y + 18, "Земля (z = 0)", size=12, color=MUTED))

    # БПЛА-носій у точці скиду
    parts.append(rect(drop_x - 30, drop_y - 15, 60, 25, fill="#38bdf8", stroke="#0284c7", sw=1.5, rx=4))
    parts.append(text(drop_x, drop_y + 2, "БПЛА", size=12, color="#0c4a6e", bold=True))
    parts.append(arrow(drop_x + 30, drop_y - 2, drop_x + 85, drop_y - 2, color="#0284c7", sw=2))
    parts.append(text(drop_x + 60, drop_y - 12, "V_x = 18 м/с", size=11, color="#0284c7", bold=True))

    # Висота скиду h
    parts.append(line(drop_x - 45, drop_y, drop_x - 45, ground_y, color=MUTED, sw=1.2, dash="3 3"))
    parts.append(arrow(drop_x - 45, drop_y + 35, drop_x - 45, drop_y, color=MUTED, sw=1.2))
    parts.append(arrow(drop_x - 45, ground_y - 35, drop_x - 45, ground_y, color=MUTED, sw=1.2))
    parts.append(text(drop_x - 55, (drop_y + ground_y) / 2 + 4, "h = 120 м", size=12, color=MUTED, anchor="end"))

    # Вакуумна траєкторія (парабола)
    vac_pts = []
    L_vac = 460
    for i in range(21):
        tau = i / 20.0
        x = drop_x + L_vac * tau
        y = drop_y + (ground_y - drop_y) * (tau ** 2)
        vac_pts.append((x, y))
    d_vac = "M " + " L ".join("%.1f %.1f" % p for p in vac_pts)
    parts.append('<path d="%s" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="5 4"/>' % d_vac)
    parts.append(circle(drop_x + L_vac, ground_y, 4, fill="#94a3b8", stroke="#64748b"))
    parts.append(text(drop_x + L_vac, ground_y - 12, "Вакуум (без опору)", size=11, color="#64748b", anchor="middle"))

    # Реальна траєкторія з опором повітря (C_d)
    drag_pts = []
    L_drag = 345
    for i in range(21):
        tau = i / 20.0
        x = drop_x + L_drag * (1.0 - math.exp(-1.5 * tau)) / (1.0 - math.exp(-1.5))
        y = drop_y + (ground_y - drop_y) * (0.85 * (tau ** 2) + 0.15 * tau)
        drag_pts.append((x, y))
    d_drag = "M " + " L ".join("%.1f %.1f" % p for p in drag_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_drag, POS))
    parts.append(circle(drop_x + L_drag, ground_y, 5, fill=POS, stroke="#991b1b"))
    parts.append(text(drop_x + L_drag, ground_y - 28, "Реальна з опором (C_d)", size=11, color=POS, bold=True))

    # Траєкторія з урахуванням попутного вітру
    wind_pts = []
    L_wind = 410
    for i in range(21):
        tau = i / 20.0
        x = drop_x + L_drag * (1.0 - math.exp(-1.5 * tau)) / (1.0 - math.exp(-1.5)) + 65 * (tau ** 1.6)
        y = drop_y + (ground_y - drop_y) * (0.85 * (tau ** 2) + 0.15 * tau)
        wind_pts.append((x, y))
    d_wind = "M " + " L ".join("%.1f %.1f" % p for p in wind_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3"/>' % (d_wind, FIELD))
    parts.append(circle(drop_x + L_wind, ground_y, 5, fill=FIELD, stroke="#166534"))
    parts.append(text(drop_x + L_wind, ground_y + 18, "Знос вітром (+W_x)", size=11, color=FIELD, bold=True))

    # Профіль вітру (стрілки праворуч)
    parts.append(line(720, 100, 720, 320, color=MUTED, sw=1))
    for wy, wlen in [(120, 50), (170, 42), (220, 34), (270, 24), (310, 14)]:
        parts.append(arrow(720, wy, 720 + wlen, wy, color="#0284c7", sw=1.5))
    parts.append(text(745, 85, "Профіль вітру W(z)", size=11, color="#0284c7", bold=True))

    # Пояснювальний блок знизу зліва
    fb = fitbox(80, 20, 280, 55,
                "ΔL = L_вакуум − L_опір ≈ 10–25 м\n"
                "Опір зрізає горизонтальну дальність!",
                size=11, pad=4, fill="#ffffff", stroke="#cbd5e1")
    parts.append(fb)

    render(os.path.join(IMG, "drop-ballistics-trajectory.svg"), W, H, *parts)


def fig_ccrp_geometry():
    """Фігура 3: Геометрія розрахунку точки скиду CCRP (Continuously Computed Release Point)."""
    W, H = 840, 400
    parts = []

    ground_y = 330
    target_x = 680

    # Земля
    parts.append(line(50, ground_y, 790, ground_y, color="#475569", sw=2))
    parts.append(rect(50, ground_y, 740, 25, fill="#f8fafc", stroke="none"))

    # Ціль на землі
    parts.append(circle(target_x, ground_y, 8, fill="#ef4444", stroke="#b91c1c", sw=2))
    parts.append('<circle cx="%.1f" cy="%.1f" r="16" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3 3"/>' % (target_x, ground_y))
    parts.append(text(target_x, ground_y + 22, "Ціль P_target", size=12, color="#b91c1c", bold=True))

    # Позиція БПЛА зараз
    uav_x, uav_y = 160, 100
    parts.append(rect(uav_x - 30, uav_y - 15, 60, 26, fill="#38bdf8", stroke="#0284c7", sw=1.5, rx=4))
    parts.append(text(uav_x, uav_y + 3, "БПЛА", size=12, color="#0c4a6e", bold=True))
    parts.append(arrow(uav_x + 30, uav_y - 2, uav_x + 85, uav_y - 2, color="#0284c7", sw=2))
    parts.append(text(uav_x + 58, uav_y - 12, "V_носія", size=11, color="#0284c7", bold=True))

    # Точка скиду CCRP
    release_x, release_y = 380, 100
    parts.append(line(release_x, release_y - 30, release_x, ground_y, color="#eab308", sw=1.5, dash="4 3"))
    parts.append(circle(release_x, release_y, 7, fill="#fef08a", stroke="#ca8a04", sw=2))
    parts.append(text(release_x, release_y - 38, "Точка скиду P_release", size=12, color="#a16207", bold=True))

    # Траєкторія від P_release до P_target
    traj_pts = []
    L_drop = target_x - release_x
    for i in range(21):
        tau = i / 20.0
        x = release_x + L_drop * (1.0 - math.exp(-1.4 * tau)) / (1.0 - math.exp(-1.4))
        y = release_y + (ground_y - release_y) * (0.8 * (tau ** 2) + 0.2 * tau)
        traj_pts.append((x, y))
    d_traj = "M " + " L ".join("%.1f %.1f" % p for p in traj_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_traj, FIELD))

    # Вектор балістичного виносу Δ_drop
    parts.append(line(release_x, ground_y - 15, target_x, ground_y - 15, color=FIELD, sw=1.5))
    parts.append(arrow(release_x + 50, ground_y - 15, release_x, ground_y - 15, color=FIELD, sw=1.5))
    parts.append(arrow(target_x - 50, ground_y - 15, target_x, ground_y - 15, color=FIELD, sw=1.5))
    parts.append(text((release_x + target_x) / 2, ground_y - 25, "Балістичний винос Δ_drop(V, h, W)", size=11, color=FIELD, bold=True))

    # Відстань до скиду D_ttr
    parts.append(line(uav_x, uav_y + 35, release_x, uav_y + 35, color=POS, sw=1.5))
    parts.append(arrow(uav_x + 35, uav_y + 35, uav_x, uav_y + 35, color=POS, sw=1.5))
    parts.append(arrow(release_x - 35, uav_y + 35, release_x, uav_y + 35, color=POS, sw=1.5))
    parts.append(text((uav_x + release_x) / 2, uav_y + 25, "D_ttr = V_x · TTR", size=11, color=POS, bold=True))

    # Апаратний лаг
    act_x = release_x - 45
    parts.append(line(act_x, release_y + 55, release_x, release_y + 55, color="#7c3aed", sw=1.5))
    parts.append(text((act_x + release_x) / 2, release_y + 72, "Δx_лаг = V_x · Δt_замок", size=10, color="#7c3aed"))

    # Пояснювальний блок алгоритму
    fb = fitbox(480, 35, 330, 95,
                "Алгоритм CCRP:\n"
                "1. Прогноз інтегратора: Δ_drop = f(V_now, h, W)\n"
                "2. P_release = P_target − Δ_drop − V·Δt_actuator\n"
                "3. Скид, коли |P_now − P_release| ≤ ε_gate",
                size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    parts.append(fb)

    render(os.path.join(IMG, "ccrp-geometry-timing.svg"), W, H, *parts)


def fig_mass_drop_dynamics():
    """Фігура 4: Динаміка носія при скиданні 40% MTOW: стрибок тяги, підкидання vs компенсація."""
    W, H = 840, 420
    parts = []

    L, R = 70, 780
    t_drop = 340 # координата X моменту скиду

    # Спільна лінія часу моменту скиду (вертикаль)
    parts.append(line(t_drop, 35, t_drop, 375, color=POS, sw=1.5, dash="4 3"))
    parts.append(text(t_drop, 25, "Скид вантажу (t = t₀)", size=12, color=POS, bold=True))

    # --- Верхній графік: Вертикальне прискорення a_z ---
    top_y = 110
    parts.append(line(L, top_y, R, top_y, color=MUTED, sw=1)) # нульова лінія
    parts.append(text(L - 10, top_y + 4, "a_z = 0", size=11, color=MUTED, anchor="end"))
    parts.append(text(R + 5, top_y - 20, "Прискорення a_z", size=12, color=INK, bold=True, anchor="end"))

    # Крива a_z без компенсації (стрибок +6.5 м/с2 і затухання PID)
    az_pts = [(L, top_y), (t_drop, top_y), (t_drop + 1, top_y - 65)]
    for i in range(1, 35):
        tau = i / 10.0
        val = 65.0 * math.exp(-1.2 * tau) * math.cos(2.8 * tau)
        az_pts.append((t_drop + 1 + i * 12, top_y - val))
    d_az = "M " + " L ".join("%.1f %.1f" % p for p in az_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_az, POS))
    parts.append(text(t_drop + 40, top_y - 72, "+0.67 g стрибок!", size=11, color=POS, bold=True))

    # --- Нижній графік: Зміна висоти z(t) ---
    bot_y = 290
    parts.append(line(L, bot_y, R, bot_y, color=MUTED, sw=1)) # цільова висота
    parts.append(text(L - 10, bot_y + 4, "z_target", size=11, color=MUTED, anchor="end"))
    parts.append(text(R + 5, bot_y - 45, "Висота z(t)", size=12, color=INK, bold=True, anchor="end"))

    # Крива z(t) без feed-forward (підкидання на +8 метрів)
    z_no_comp = [(L, bot_y), (t_drop, bot_y)]
    for i in range(1, 35):
        tau = i / 10.0
        dz = 75.0 * (tau * math.exp(-0.7 * tau)) * 1.8
        z_no_comp.append((t_drop + i * 12, bot_y - dz))
    d_znoc = "M " + " L ".join("%.1f %.1f" % p for p in z_no_comp)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % (d_znoc, POS))
    parts.append(text(t_drop + 150, bot_y - 80, "Без компенсації: підкидання +5–10 м", size=11, color=POS))

    # Крива z(t) з feed-forward зрізом газу
    z_comp = [(L, bot_y), (t_drop, bot_y)]
    for i in range(1, 35):
        tau = i / 10.0
        dz = 12.0 * (tau * math.exp(-2.2 * tau)) * math.sin(3.0 * tau)
        z_comp.append((t_drop + i * 12, bot_y - dz))
    d_zcomp = "M " + " L ".join("%.1f %.1f" % p for p in z_comp)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d_zcomp, FIELD))
    parts.append(text(t_drop + 170, bot_y - 12, "З Throttle Feed-Forward: просідання < 0.5 м", size=11, color=FIELD, bold=True))

    # Інформаційний блок про масу
    fb = fitbox(80, 40, 220, 50,
                "Маса: M₁ = 5.0 кг → M₂ = 3.0 кг\n"
                "Скид 40% злітної маси!",
                size=11, pad=4, fill="#ffffff", stroke="#cbd5e1")
    parts.append(fb)

    render(os.path.join(IMG, "mass-drop-dynamics.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_release_mechanisms()
    fig_drop_ballistics()
    fig_ccrp_geometry()
    fig_mass_drop_dynamics()
    print("Всі фігури згенеровано успішно.")
