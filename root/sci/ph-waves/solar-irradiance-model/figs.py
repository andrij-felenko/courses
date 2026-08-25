# -*- coding: utf-8 -*-
"""Фігури до теми «Модель сонячної інсоляції».
Запуск: python figs.py -> створює SVG у ./img/
Використовує svgkit з теки scripts/"""
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

ACCENT_SUN    = "#d97706"  # Жовто-помаранчевий (Сонце / пряме випромінювання)
ACCENT_SKY    = "#2563eb"  # Синій (Атмосфера / дифузне розсіяння)
ACCENT_PANEL  = "#1e293b"  # Темно-сірий (Сонячна панель)
ACCENT_GREEN  = "#16a34a"  # Зелений (Земля / альбедо)
ACCENT_RED    = "#dc2626"  # Червоний (Нормаль / кути)
DARK          = "#0f172a"  # Основний колір тексту
MUTED         = "#64748b"  # Допоміжний сірий колір
BG            = "#ffffff"  # Біле тло

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Геометрія зенітного кута та оптична маса повітря (Air Mass) ───────
def fig_airmass_geometry():
    W, H = 820, 480
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Геометрія сонячного зенітного кута та атмосферного шляху (Air Mass)", size=15, bold=True))

    # Шар атмосфери
    y_ground = 380
    y_top = 140
    f.append(rect(40, y_top, 740, y_ground - y_top, fill="#f0f9ff", stroke=ACCENT_SKY, sw=1.5, rx=0))
    f.append(line(40, y_ground, 780, y_ground, color=DARK, sw=2))

    # Підписи шарів
    f.append(text(50, y_top - 12, "Верхня межа атмосфери (Extraterrestrial TOA, G_sc = 1361 Вт/м²)", size=11, color=MUTED, bold=True, anchor="start"))
    f.append(text(50, y_ground + 24, "Поверхня Землі (приймач випромінювання)", size=11, color=DARK, bold=True, anchor="start"))

    # Станція спостереження (точка на Землі)
    x_obs, y_obs = 300, y_ground
    f.append(circle(x_obs, y_obs, 5, fill=DARK, stroke='none'))

    # Вертикаль (Зеніт)
    f.append(line(x_obs, y_obs, x_obs, y_top - 30, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(x_obs, y_top - 40, "Зеніт (θ_z = 0°)", size=12, color=MUTED, bold=True))

    # Прямий промінь у зеніті (AM = 1.0)
    f.append(arrow(x_obs, y_top, x_obs, y_obs - 10, color=ACCENT_SUN, sw=2.5))
    f.append(text(x_obs - 15, (y_top + y_obs) / 2, "h_atm (AM1.0)", size=11, color=ACCENT_SUN, bold=True, anchor="end"))

    # Похилий промінь під кутом θ_z = 50°
    theta_deg = 50
    theta_rad = math.radians(theta_deg)
    x_top_sun = x_obs + (y_ground - y_top) * math.tan(theta_rad)  # ≈ 300 + 240 * 1.19 = 586

    f.append(arrow(x_top_sun, y_top, x_obs + 6, y_obs - 8, color=ACCENT_SUN, sw=3))

    # Дуга зенітного кута θ_z
    arc_r = 75
    arc_path = f'<path d="M {x_obs:.1f} {y_obs - arc_r:.1f} A {arc_r} {arc_r} 0 0 1 {x_obs + arc_r * math.sin(theta_rad):.1f} {y_obs - arc_r * math.cos(theta_rad):.1f}" fill="none" stroke="{ACCENT_RED}" stroke-width="2"/>'
    f.append(arc_path)
    f.append(text(x_obs + 35, y_obs - 85, "θ_z", size=14, color=ACCENT_RED, bold=True))

    # Позначення Сонця
    sun_r = 18
    f.append(circle(x_top_sun, y_top - 20, sun_r, fill="#f59e0b", stroke="#d97706", sw=2))
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        f.append(line(x_top_sun + (sun_r + 3) * math.cos(rad), (y_top - 20) + (sun_r + 3) * math.sin(rad),
                      x_top_sun + (sun_r + 9) * math.cos(rad), (y_top - 20) + (sun_r + 9) * math.sin(rad),
                      color="#f59e0b", sw=2))

    # Текстовий блок 1 (Оптичний шлях) — розміщуємо праворуч
    tb1, _, _ = textbox(670, y_top + 100,
                         "Оптичний шлях S:\nS = h_atm / cos(θ_z)\nМаса повітря AM ≈ 1 / cos(θ_z)\nДля θ_z = 50° → AM ≈ 1.55",
                         size=11, fill="#ffffff", stroke=ACCENT_SUN, sw=1.5, rx=6)
    f.append(tb1)

    # Текстовий блок 2 (Втрати) — розміщуємо ліворуч у центрі шару
    tb2, _, _ = textbox(175, y_ground - 80,
                         "Атмосферні втрати (Бугер):\n• Релеєвське розсіяння (молекули)\n• Мі-розсіяння (аерозолі, пил)\n• Поглинання H₂O, O₃, CO₂",
                         size=11, fill="#ffffff", stroke=ACCENT_SKY, sw=1.5, rx=6)
    f.append(tb2)

    f.append(text(W / 2, H - 15, "Збільшення зенітного кута θ_z подовжує шлях світла крізь атмосферу та підсилює згасання", size=12, color=MUTED, bold=True))

    out_file = os.path.join(IMG_DIR, 'airmass-geometry.svg')
    render(out_file, W, H, *f)
    print(f"Generated {out_file}")


# ── Фігура 2: Компоненти сонячної інсоляції на похилій поверхні ────────────────
def fig_irradiance_components():
    W, H = 840, 500
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Компоненти інсоляції на похилій поверхні (Direct, Diffuse, Albedo)", size=15, bold=True))

    # Ґрунт
    y_g = 400
    f.append(rect(40, y_g, 760, 35, fill="#f0fdf4", stroke=ACCENT_GREEN, sw=1.5, rx=0))
    f.append(text(120, y_g + 22, "Поверхня землі (Альбедо ρ_g ≈ 0.2)", size=11, color=ACCENT_GREEN, bold=True))

    # Купол неба
    f.append('<path d="M 80 400 A 340 340 0 0 1 760 400" fill="none" stroke="#93c5fd" stroke-width="2" stroke-dasharray="4,4"/>')
    f.append(text(660, 110, "Небесна напівсфера (DHI)", size=12, color=ACCENT_SKY, bold=True))

    # Сонячна панель
    x_p, y_p = 440, y_g
    panel_len = 160
    beta_deg = 35
    beta_rad = math.radians(beta_deg)

    x_top_p = x_p - panel_len * math.cos(beta_rad)
    y_top_p = y_p - panel_len * math.sin(beta_rad)

    # Лінії панелі
    f.append(line(x_top_p, y_top_p, x_p, y_p, color=ACCENT_PANEL, sw=10))
    f.append(line(x_top_p, y_top_p, x_p, y_p, color="#38bdf8", sw=3))

    x_mid = (x_top_p + x_p) / 2
    y_mid = (y_top_p + y_p) / 2

    # Нормаль до панелі
    norm_len = 100
    nx = x_mid + norm_len * math.sin(beta_rad)
    ny = y_mid - norm_len * math.cos(beta_rad)
    f.append(arrow(x_mid, y_mid, nx, ny, color=ACCENT_RED, sw=2))
    f.append(text(nx + 30, ny - 15, "Нормаль n̂", size=12, color=ACCENT_RED, bold=True, anchor="start"))

    # Горизонталь та кут нахилу β
    f.append(line(x_p - 80, y_g, x_p + 30, y_g, color=MUTED, sw=1, dash="3,3"))
    arc_beta = f'<path d="M {x_p - 50:.1f} {y_g:.1f} A 50 50 0 0 1 {x_p - 50 * math.cos(beta_rad):.1f} {y_g - 50 * math.sin(beta_rad):.1f}" fill="none" stroke="{DARK}" stroke-width="1.8"/>'
    f.append(arc_beta)
    f.append(text(x_p - 65, y_g - 14, "β", size=13, color=DARK, bold=True))

    # 1. Прямий промінь (Direct Normal Irradiance DNI)
    x_sun, y_sun = 160, 110
    f.append(circle(x_sun, y_sun, 20, fill="#f59e0b", stroke="#d97706", sw=2))
    f.append(text(x_sun, y_sun - 28, "Сонце", size=12, color=ACCENT_SUN, bold=True))

    # Промінь DNI до панелі
    f.append(arrow(x_sun + 15, y_sun + 15, x_mid - 5, y_mid - 5, color=ACCENT_SUN, sw=3.5))
    f.append(text(x_sun + 120, y_sun + 45, "Пряме випромінювання (DNI · cos θ)", size=12, color=ACCENT_SUN, bold=True))

    # 2. Дифузне випромінювання (DHI від неба)
    diff_rays = [(560, 140), (630, 200), (510, 230)]
    for dx, dy in diff_rays:
        f.append(arrow(dx, dy, x_mid + (dx - x_mid) * 0.35, y_mid + (dy - y_mid) * 0.35, color=ACCENT_SKY, sw=2))
    f.append(text(600, 270, "Дифузне розсіяння неба (DHI · (1 + cos β)/2)", size=11, color=ACCENT_SKY, bold=True))

    # 3. Відбите від землі (Albedo)
    f.append(arrow(250, y_g - 10, x_mid - 25, y_mid + 25, color=ACCENT_GREEN, sw=2))
    f.append(text(180, y_g - 50, "Відбиття від землі (GHI · ρ_g · (1 - cos β)/2)", size=11, color=ACCENT_GREEN, bold=True))

    # Резюме формули інсоляції в нижньому прямокутнику
    tb_sum, _, _ = textbox(W / 2, H - 45,
                           "Загальна інсоляція POA (G_T):\nG_T = DNI · cos(θ) + DHI · (1 + cos β)/2 + GHI · ρ_g · (1 - cos β)/2",
                           size=11, fill="#ffffff", stroke=DARK, sw=1.5, rx=6)
    f.append(tb_sum)

    out_file = os.path.join(IMG_DIR, 'irradiance-components.svg')
    render(out_file, W, H, *f)
    print(f"Generated {out_file}")


if __name__ == "__main__":
    fig_airmass_geometry()
    fig_irradiance_components()
