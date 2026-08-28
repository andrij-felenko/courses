# -*- coding: utf-8 -*-
"""Фігури до теми «Люмен, люкс, кандела: фотометрія проти радіометрії».
Запуск: python figs.py  → записує SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_RAD = "#c0392b"    # червоний / радіометрія / енергія
COLOR_PHOT = "#27ae60"   # зелений / фотометрія / око
COLOR_BLUE = "#2457d6"   # синій / скотопічний зір / хвилі
COLOR_GOLD = "#d35400"   # помаранчевий / світловий потік
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#7f8c8d"


# ── Фігура 1: Радіометрія проти фотометрії (фільтрація людським оком) ─────────
def fig_radiometry_vs_photometry():
    W, H = 820, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Радіометрія (об'єктивна енергія) проти фотометрії (зір людини)", size=16, bold=True))

    # Ліва колонка: Радіометрія
    box_rad = fitbox(30, 56, 220, 270,
                     "РАДІОМЕТРІЯ\n\n"
                     "Об'єктивна фізична енергія\n"
                     "• Довжини хвиль: будь-які (УФ, видиме, ІЧ)\n"
                     "• Приймач: болометр, калориметр\n"
                     "• Чутливість: спектрально пласка\n"
                     "• Базова одиниця: Ват (Вт, Дж/с)\n\n"
                     "Випромінювач 1 Вт на 1064 нм (ІЧ) = 1 Вт\n"
                     "Випромінювач 1 Вт на 555 нм (зелене) = 1 Вт",
                     size=12, pad=10, fill="#fdf2f0", stroke=COLOR_RAD, sw=1.6)
    f.append(box_rad)

    # Центральний блок: Спектральний фільтр ока V(lambda)
    f.append(arrow(255, 190, 295, 190, color=LINE, sw=2))

    box_eye = fitbox(300, 70, 220, 240,
                     "БІОЛОГІЧНИЙ ФІЛЬТР\n\n"
                     "Крива чутливості ока V(λ)\n"
                     "• Колбочки сітківки (L, M, S)\n"
                     "• Пік чутливості: 555 нм (зелене)\n"
                     "• V(555 нм) = 1.0  (683 лм/Вт)\n"
                     "• V(1064 нм) = 0.0 (невидиме ІЧ)\n"
                     "• V(350 нм) = 0.0  (невидиме УФ)\n\n"
                     "Зважування: Φ_v = Km · ∫ Φ_e(λ)·V(λ) dλ",
                     size=12, pad=10, fill="#f0f9f4", stroke=COLOR_PHOT, sw=1.8)
    f.append(box_eye)

    f.append(arrow(525, 190, 565, 190, color=LINE, sw=2))

    # Права колонка: Фотометрія
    box_phot = fitbox(570, 56, 220, 270,
                      "ФОТОМЕТРІЯ\n\n"
                      "Суб'єктивне зорове відчуття\n"
                      "• Довжини хвиль: лише 380–780 нм\n"
                      "• Приймач: око, люксметр із V(λ)\n"
                      "• Чутливість: вибіркова до кольору\n"
                      "• Базова одиниця: Люмен (лм, кд·ср)\n\n"
                      "Лазер 1 Вт на 1064 нм (ІЧ) = 0 лм\n"
                      "Лазер 1 Вт на 555 нм (зелене) = 683 лм",
                      size=12, pad=10, fill="#edf7ff", stroke=COLOR_BLUE, sw=1.6)
    f.append(box_phot)

    render(os.path.join(IMG, "fig-radiometry-vs-photometry.svg"), W, H, *f)


# ── Фігура 2: Фотопічна та скотопічна криві чутливості (CIE V(lambda) та V'(lambda)) ──
def fig_photopic_scotopic():
    W, H = 840, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Спектральна світлова ефективність: фотопічний V(λ) та скотопічний V'(λ) зір", size=16, bold=True))

    # Інформаційні блоки вгорі (поза графіком)
    f.append(fitbox(80, 48, 290, 60,
                    "Скотопічний зір V'(λ) (палички, ніч)\n"
                    "Пік чутливості: 507 нм | K'm = 1700 лм/Вт",
                    size=11, fill="#edf7ff", stroke=COLOR_BLUE, sw=1.4))

    f.append(fitbox(470, 48, 290, 60,
                    "Фотопічний зір V(λ) (колбочки, день)\n"
                    "Пік чутливості: 555 нм | Km = 683 лм/Вт",
                    size=11, fill="#f0f9f4", stroke=COLOR_PHOT, sw=1.4))

    # Стрілка зсуву Пуркинє
    f.append(arrow(465, 78, 375, 78, color=COLOR_DARK, sw=1.8))
    f.append(text(420, 70, "Зсув", size=10, bold=True, color=COLOR_DARK))

    # Область графіка
    gx, gy, gw, gh = 80, 130, 680, 240
    f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Спектральна кольорова підкладка знизу
    colors = [
        (380, 440, "#e8d5f5"),  # фіолетовий
        (440, 490, "#d5e5f5"),  # синій
        (490, 560, "#d5f5df"),  # зелений
        (560, 590, "#fef3cd"),  # жовтий
        (590, 630, "#ffe5d0"),  # помаранчевий
        (630, 750, "#ffd8d8"),  # червоний
    ]
    for l1, l2, col in colors:
        x1 = gx + (l1 - 380) / (750 - 380) * gw
        x2 = gx + (l2 - 380) / (750 - 380) * gw
        f.append(rect(x1, gy + gh - 18, x2 - x1, 18, fill=col, stroke="none", sw=0, rx=0))

    # Сітка та підписи осей
    for v in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y = gy + gh - v * gh
        f.append(line(gx, y, gx + gw, y, color="#e5e9f0", sw=1, dash="4,4"))
        f.append(text(gx - 8, y + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))

    f.append(text(gx - 42, gy + gh / 2, "Відносна чутливість", size=12, color=INK, anchor="middle", bold=True))

    for wl in range(400, 750, 50):
        x = gx + (wl - 380) / (750 - 380) * gw
        f.append(line(x, gy, x, gy + gh, color="#e5e9f0", sw=1, dash="4,4"))
        f.append(text(x, gy + gh + 16, "%d" % wl, size=11, color=MUTED))

    f.append(text(gx + gw / 2, gy + gh + 34, "Довжина хвилі λ (нм)", size=12, color=INK, bold=True))

    # Побудова кривих за гаусіанами CIE
    def v_photopic(l):
        if l < 555:
            return math.exp(-0.5 * ((l - 555) / 46.0) ** 2)
        else:
            return math.exp(-0.5 * ((l - 555) / 52.0) ** 2)

    def v_scotopic(l):
        if l < 507:
            return math.exp(-0.5 * ((l - 507) / 38.0) ** 2)
        else:
            return math.exp(-0.5 * ((l - 507) / 44.0) ** 2)

    pts_phot = []
    pts_scot = []
    for wl_i in range(380, 751, 2):
        x = gx + (wl_i - 380) / (750 - 380) * gw
        y_p = gy + gh - v_photopic(wl_i) * gh
        y_s = gy + gh - v_scotopic(wl_i) * gh
        pts_phot.append((x, y_p))
        pts_scot.append((x, y_s))

    for i in range(len(pts_scot) - 1):
        f.append(line(pts_scot[i][0], pts_scot[i][1], pts_scot[i+1][0], pts_scot[i+1][1], color=COLOR_BLUE, sw=2.6))
    for i in range(len(pts_phot) - 1):
        f.append(line(pts_phot[i][0], pts_phot[i][1], pts_phot[i+1][0], pts_phot[i+1][1], color=COLOR_PHOT, sw=2.6))

    # Маркери піків
    x_507 = gx + (507 - 380) / (750 - 380) * gw
    y_507 = gy + gh - 1.0 * gh
    f.append(circle(x_507, y_507, 5, fill=COLOR_BLUE, stroke=BG, sw=2))

    x_555 = gx + (555 - 380) / (750 - 380) * gw
    y_555 = gy + gh - 1.0 * gh
    f.append(circle(x_555, y_555, 5, fill=COLOR_PHOT, stroke=BG, sw=2))

    render(os.path.join(IMG, "fig-photopic-scotopic.svg"), W, H, *f)


# ── Фігура 3: Чотири головні фотометричні величини ───────────────────────────
def fig_four_photometric_quantities():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чотири базові фотометричні величини в єдиній геометрії", size=16, bold=True))

    # Джерело світла ліворуч (x=100, y=210)
    sx, sy = 100, 210
    f.append(circle(sx, sy, 22, fill="#fff9db", stroke="#f59f00", sw=2.5))
    f.append(text(sx, sy + 5, "Джерело", size=10, bold=True, color="#d35400"))

    # 1. Сила світла I_v (кандела, cd)
    f.append(line(sx + 22, sy, sx + 90, sy - 45, color=COLOR_GOLD, sw=1.8))
    f.append(line(sx + 22, sy, sx + 90, sy + 45, color=COLOR_GOLD, sw=1.8))
    f.append(line(sx + 90, sy - 45, sx + 90, sy + 45, color=COLOR_GOLD, sw=1.4, dash="3,3"))

    f.append(fitbox(sx - 70, sy - 145, 190, 80,
                    "1. СИЛА СВІТЛА I_v\nОдиниця: Кандела (кд = лм/ср)\nI_v = dΦ_v / dΩ\nГустина потоку в тілесному куті dΩ",
                    size=11, fill="#fffbf0", stroke=COLOR_GOLD, sw=1.4))

    # 2. Світловий потік Phi_v (люмен, lm)
    f.append(arrow(sx + 90, sy - 25, sx + 220, sy - 60, color="#f59f00", sw=2))
    f.append(arrow(sx + 90, sy, sx + 230, sy, color="#f59f00", sw=2))
    f.append(arrow(sx + 90, sy + 25, sx + 220, sy + 60, color="#f59f00", sw=2))

    f.append(fitbox(sx + 50, sy + 90, 240, 75,
                    "2. СВІТЛОВИЙ ПОТІК Φ_v\nОдиниця: Люмен (лм)\nЗагальна потужність видимого випромінювання,\nзважена за чутливістю ока V(λ)",
                    size=11, fill="#fff9db", stroke="#f59f00", sw=1.4))

    # 3. Освітленість E_v (люкс, lx) на поверхні приймача (x=460, y=210)
    rx, ry, rw, rh = 440, 140, 16, 140
    f.append(rect(rx, ry, rw, rh, fill="#e8f4fd", stroke=COLOR_BLUE, sw=2, rx=2))
    f.append(text(rx + 8, ry + rh + 18, "Площа dA", size=11, color=COLOR_BLUE, bold=True))

    # Стрілка відстані r
    f.append(line(sx, sy + 60, rx, sy + 60, color=MUTED, sw=1.2, dash="4,4"))
    f.append(arrow(sx + 40, sy + 60, sx, sy + 60, color=MUTED, sw=1.2))
    f.append(arrow(rx - 40, sy + 60, rx, sy + 60, color=MUTED, sw=1.2))
    f.append(text((sx + rx) / 2, sy + 52, "Відстань r", size=11, color=MUTED))

    f.append(fitbox(rx - 100, sy - 145, 220, 80,
                    "3. ОСВІТЛЕНІСТЬ E_v\nОдиниця: Люкс (лк = лм/м²)\nE_v = dΦ_v / dA = (I_v / r²) · cos θ\nГустина світлового потоку на поверхні",
                    size=11, fill="#edf7ff", stroke=COLOR_BLUE, sw=1.4))

    # 4. Яскравість L_v (кд/м²) - спостереження поверхні під кутом тета
    ox, oy = 720, 120
    f.append(circle(ox, oy, 18, fill="#ffffff", stroke=COLOR_PHOT, sw=2))
    f.append(circle(ox + 4, oy, 8, fill=COLOR_DARK, stroke="none", sw=0))
    f.append(circle(ox + 6, oy - 2, 2.5, fill="#ffffff", stroke="none", sw=0))
    f.append(text(ox, oy + 32, "Спостерігач", size=11, color=COLOR_PHOT, bold=True))

    f.append(arrow(rx + rw, ry + rh / 2, ox - 20, oy + 5, color=COLOR_PHOT, sw=2))
    f.append(line(rx + rw, ry + rh / 2, rx + rw + 70, ry + rh / 2, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(rx + rw + 50, ry + rh / 2 - 12, "θ", size=12, color=COLOR_PHOT, bold=True))

    f.append(fitbox(550, 270, 260, 90,
                    "4. ЯСКРАВІСТЬ L_v\nОдиниця: кд/м² (ніт)\nL_v = d²Φ_v / (dA · cos θ · dΩ)\nЗорова світність поверхні у напрямку ока;\nєдина величина, яку безпосередньо бачить зір",
                    size=11, fill="#f0f9f4", stroke=COLOR_PHOT, sw=1.4))

    render(os.path.join(IMG, "fig-four-photometric-quantities.svg"), W, H, *f)


# ── Фігура 4: Закон Ламберта та косинусний розсіювач ──────────────────────────
def fig_lambert_cosine_diffuser():
    W, H = 840, 370
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Косинусний закон освітленості та конструкція вимірювального розсіювача", size=16, bold=True))

    midx = 410
    f.append(line(midx, 50, midx, H - 20, color="#d0d7de", sw=1.2, dash="4,4"))
    f.append(text(midx / 2, 54, "Геометрія: проєкція площі під кутом θ", size=13, bold=True, color=COLOR_DARK))

    px, py = 80, 240
    f.append(line(px - 40, py, px + 180, py, color=LINE, sw=2.5))
    f.append(text(px + 70, py + 18, "Приймальна поверхня dA", size=11, color=INK))

    f.append(line(px + 70, py, px + 70, py - 130, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(px + 75, py - 135, "Нормаль n", size=10, color=MUTED))

    bx, by = px - 10, py - 110
    f.append(arrow(bx, by, px + 30, py, color=COLOR_RAD, sw=2))
    f.append(arrow(bx + 40, by, px + 70, py, color=COLOR_RAD, sw=2))
    f.append(arrow(bx + 80, by, px + 110, py, color=COLOR_RAD, sw=2))

    f.append(text(px + 45, py - 70, "θ", size=13, bold=True, color=COLOR_RAD))

    f.append(fitbox(30, 275, 350, 70,
                    "E_v(θ) = E_0 · cos θ\n"
                    "Світловий потік розмазується по більшій площі dA / cos θ,\n"
                    "тому густина потоку (освітленість) спадає як cos θ",
                    size=11, fill="#fdf2f0", stroke=COLOR_RAD, sw=1.4))

    rx_center = (midx + W) / 2
    f.append(text(rx_center, 54, "Конструкція косинусної насадки люксметра", size=13, bold=True, color=COLOR_PHOT))

    cx, cy = rx_center, 175

    f.append(rect(cx - 90, cy + 20, 180, 50, fill="#34495e", stroke=LINE, sw=2, rx=4))
    f.append(text(cx, cy + 50, "Металевий корпус з обмежувачем", size=11, color="#ecf0f1"))

    f.append(rect(cx - 35, cy + 5, 70, 15, fill="#2c3e50", stroke="#3498db", sw=1.5, rx=2))
    f.append(text(cx, cy + 16, "Кремнієвий фотодіод", size=10, color="#ffffff"))

    f.append(rect(cx - 45, cy - 10, 90, 12, fill="#a8e6cf", stroke=COLOR_PHOT, sw=1.4, rx=2))
    f.append(text(cx, cy - 1, "Фільтр V(λ)", size=9, bold=True, color=COLOR_PHOT))

    dome_path = ('<path d="M %.1f %.1f A 55 55 0 0 1 %.1f %.1f Z" fill="#ffffff" stroke="#95a5a6" stroke-width="2"/>'
                 % (cx - 55, cy - 12, cx + 55, cy - 12))
    f.append(dome_path)
    f.append(text(cx, cy - 35, "Дифузний купол (PTFE / опал)", size=10, bold=True, color=INK))

    f.append(arrow(cx - 100, cy - 65, cx - 40, cy - 30, color=COLOR_GOLD, sw=1.8))
    f.append(arrow(cx - 85, cy - 85, cx - 25, cy - 45, color=COLOR_GOLD, sw=1.8))

    f.append(fitbox(midx + 20, 265, 380, 85,
                    "Чому необхідний купол:\n"
                    "Плоский фотодіод на великих кутах відбиває світло (закон Френеля),\n"
                    "занижуючи сигнал. Опаловий купол розсіює промені з усіх кутів,\n"
                    "відновлюючи точну характеристику cos θ (похибка f₂ < 1.5–3%).",
                    size=11, fill="#f0f9f4", stroke=COLOR_PHOT, sw=1.4))

    render(os.path.join(IMG, "fig-lambert-cosine-diffuser.svg"), W, H, *f)


if __name__ == '__main__':
    fig_radiometry_vs_photometry()
    fig_photopic_scotopic()
    fig_four_photometric_quantities()
    fig_lambert_cosine_diffuser()
    print("All figures rendered successfully.")
