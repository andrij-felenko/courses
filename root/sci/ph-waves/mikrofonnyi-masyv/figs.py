# -*- coding: utf-8 -*-
"""Фігури до статті «Мікрофонний масив: напрям на джерело».
Запуск із кореня репо або з теки теми: python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Геометрія лінійного масиву та затримка TDoA ─────────────────────
def fig_array_geometry():
    W, H = 880, 520

    # Опорна лінія масиву
    ax_y = 380
    m_xs = [160, 280, 400, 520, 640]
    labels = ["M₀ (x=0)", "M₁ (x=d)", "M₂ (x=2d)", "M₃ (x=3d)", "M₄ (x=4d)"]

    elems = []
    # Тіло плати/балки
    elems.append(rect(110, ax_y - 12, 580, 24, fill="#e8edf5", stroke="#7a8b9e", sw=1.5, rx=4))
    elems.append(line(80, ax_y, 740, ax_y, color=MUTED, sw=1.0, dash="4,4"))
    elems.append(text(760, ax_y + 4, "Вісь масиву X", size=12, color=MUTED, anchor="start"))

    # Нормаль до масиву (θ = 0)
    elems.append(line(400, ax_y, 400, 80, color=MUTED, sw=1.2, dash="3,3"))
    elems.append(text(400, 65, "Акустична нормаль (θ = 0°)", size=13, color=MUTED, anchor="middle", bold=True))

    theta_deg = 35.0
    theta_rad = math.radians(theta_deg)

    # Промені від віддаленого джерела (плоска хвиля)
    ray_len = 290
    for i, mx in enumerate(m_xs):
        rx1 = mx - ray_len * math.sin(theta_rad)
        ry1 = ax_y - ray_len * math.cos(theta_rad)
        elems.append(line(rx1, ry1, mx, ax_y, color=NEG, sw=1.6))
        # Стрілка напрямку хвилі
        mid_x = mx - 120 * math.sin(theta_rad)
        mid_y = ax_y - 120 * math.cos(theta_rad)
        elems.append(line(mid_x - 15 * math.sin(theta_rad), mid_y - 15 * math.cos(theta_rad),
                          mid_x, mid_y, color=NEG, sw=2.2))

    # Хвильовий фронт, що проходить через M₀
    wf_len = 450
    wfx2 = m_xs[0] + wf_len * math.cos(theta_rad)
    wfy2 = ax_y - wf_len * math.sin(theta_rad)
    elems.append(line(m_xs[0], ax_y, wfx2, wfy2, color=FIELD, sw=2.2))
    elems.append(text(wfx2 + 10, wfy2 - 8, "Плоский хвильовий фронт", size=13, color=FIELD, anchor="start", bold=True))

    # Різниця ходу до M₁: Δr = d · sin(θ)
    d_pix = m_xs[1] - m_xs[0]
    p1_x = m_xs[0] + d_pix * (math.cos(theta_rad) ** 2)
    p1_y = ax_y - d_pix * math.sin(theta_rad) * math.cos(theta_rad)
    elems.append(line(m_xs[1], ax_y, p1_x, p1_y, color=POS, sw=2.0, dash="3,3"))

    # Прямокутний кут
    k_len = 10
    corner_x = p1_x + k_len * math.cos(theta_rad)
    corner_y = p1_y - k_len * math.sin(theta_rad)
    elems.append(line(p1_x, p1_y, corner_x, corner_y, color=POS, sw=1.0))
    elems.append(line(corner_x, corner_y, corner_x + k_len * math.sin(theta_rad), corner_y + k_len * math.cos(theta_rad), color=POS, sw=1.0))

    # Дуга кута падіння θ
    arc_r = 75
    arc_pts = []
    for deg in range(int(theta_deg) + 1):
        rad = math.radians(deg)
        arc_pts.append("%.1f,%.1f" % (400 - arc_r * math.sin(rad), ax_y - arc_r * math.cos(rad)))
    elems.append('<polyline fill="none" stroke="%s" stroke-width="1.6" points="%s"/>' % (INK, " ".join(arc_pts)))
    elems.append(text(370, ax_y - 85, "θ", size=16, color=INK, bold=True))

    # Позначення кроку d між мікрофонами
    elems.append(line(m_xs[0], ax_y + 35, m_xs[1], ax_y + 35, color=LINE, sw=1.4))
    elems.append(line(m_xs[0], ax_y + 28, m_xs[0], ax_y + 42, color=LINE, sw=1.4))
    elems.append(line(m_xs[1], ax_y + 28, m_xs[1], ax_y + 42, color=LINE, sw=1.4))
    elems.append(text((m_xs[0] + m_xs[1]) / 2, ax_y + 52, "Крок d", size=13, color=INK, anchor="middle", bold=True))

    # Мікрофони (кола та підписи)
    for i, mx in enumerate(m_xs):
        elems.append(circle(mx, ax_y, 9, fill="#ffffff", stroke=POS, sw=2.5))
        elems.append(circle(mx, ax_y, 4, fill=POS, stroke=POS, sw=1.0))
        elems.append(text(mx, ax_y + 24, labels[i], size=12, color=INK, anchor="middle", bold=True))

    # Пояснювальний блок формули
    box, _, _ = textbox(660, 190,
                        "Різниця ходу променя:\n"
                        "  Δr = d · sin(θ)\n"
                        "Затримка приходу TDoA:\n"
                        "  τ = Δr / c = (d · sin(θ)) / c\n"
                        "Фазовий зсув на частоті f:\n"
                        "  Δφ = 2π f τ = (2π f d sin(θ)) / c",
                        size=13, fill="#f8fafc", stroke="#94a3b8", pad=12)
    elems.append(box)

    render(os.path.join(IMG, "array-interference-geometry.svg"), W, H,
           *elems, title="Геометрія лінійного масиву та різниця ходу хвиль")


# ── Фігура 2: Принцип алгоритму GCC-PHAT ───────────────────────────────────────
def fig_gcc_phat():
    W, H = 900, 480
    elems = []

    # Входи сигналів
    elems.append(rect(40, 70, 130, 48, fill="#eef2ff", stroke="#6366f1", sw=1.8, rx=6))
    elems.append(text(105, 98, "Сигнал x₁(t)", size=14, color="#312e81", anchor="middle", bold=True))

    elems.append(rect(40, 190, 130, 48, fill="#eef2ff", stroke="#6366f1", sw=1.8, rx=6))
    elems.append(text(105, 218, "Сигнал x₂(t)", size=14, color="#312e81", anchor="middle", bold=True))

    # Блоки БПФ
    elems.append(arrow(170, 94, 215, 94, color="#6366f1", sw=1.8))
    elems.append(arrow(170, 214, 214, 214, color="#6366f1", sw=1.8))

    elems.append(rect(220, 70, 110, 48, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    elems.append(text(275, 98, "FFT → X₁(f)", size=13, color=INK, anchor="middle", bold=True))

    elems.append(rect(220, 190, 110, 48, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    elems.append(text(275, 218, "FFT → X₂(f)", size=13, color=INK, anchor="middle", bold=True))

    # Перемноження та спряження
    elems.append(arrow(330, 94, 385, 140, color=LINE, sw=1.6))
    elems.append(arrow(330, 214, 385, 168, color=LINE, sw=1.6))

    elems.append(rect(390, 130, 130, 50, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    elems.append(text(455, 153, "Взаємний спектр", size=11, color="#92400e", anchor="middle"))
    elems.append(text(455, 169, "G₁₂(f) = X₁ · X₂*", size=12, color="#92400e", anchor="middle", bold=True))

    # Фільтр PHAT (відбілювання амплітуди)
    elems.append(arrow(520, 155, 575, 155, color="#d97706", sw=1.8))
    elems.append(rect(580, 125, 140, 60, fill="#ecfdf5", stroke=FIELD, sw=2.0, rx=6))
    elems.append(text(650, 148, "Фазове зважування", size=11, color="#065f46", anchor="middle"))
    elems.append(text(650, 168, "Ψ_PHAT = 1 / |G₁₂|", size=13, color="#065f46", anchor="middle", bold=True))

    # Зворотне БПФ (IFFT)
    elems.append(arrow(720, 155, 775, 155, color=FIELD, sw=1.8))
    elems.append(rect(780, 130, 90, 50, fill="#ffffff", stroke=LINE, sw=1.6, rx=6))
    elems.append(text(825, 153, "IFFT", size=12, color=INK, anchor="middle", bold=True))
    elems.append(text(825, 169, "R(τ)", size=12, color=MUTED, anchor="middle"))

    # Порівняння графіків внизу
    # Графік 1: Стандартна взаємна кореляція (CC)
    g1_x, g1_y, gw, gh = 80, 290, 320, 130
    elems.append(rect(g1_x, g1_y, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    elems.append(line(g1_x + 10, g1_y + gh - 20, g1_x + gw - 10, g1_y + gh - 20, color=MUTED, sw=1.0))
    elems.append(line(g1_x + gw / 2, g1_y + 10, g1_x + gw / 2, g1_y + gh - 10, color=MUTED, sw=1.0, dash="3,3"))
    elems.append(text(g1_x + gw / 2, g1_y + 22, "Звичайна кореляція (розмиті піки відлуння)", size=11, color=POS, anchor="middle", bold=True))

    # Хвиля звичайної кореляції (розмита)
    pts_cc = []
    for i in range(120):
        t = (i - 60) / 15.0
        val = math.exp(-0.5 * (t - 1.2) ** 2) * math.cos(2.2 * t) + 0.6 * math.exp(-0.3 * (t + 2.5) ** 2) * math.cos(1.8 * t)
        py = g1_y + gh - 25 - max(0, val * 45)
        pts_cc.append("%.1f,%.1f" % (g1_x + 20 + i * (gw - 40) / 120.0, py))
    elems.append('<polyline fill="none" stroke="%s" stroke-width="1.8" points="%s"/>' % (POS, " ".join(pts_cc)))

    # Графік 2: GCC-PHAT (гострий дельта-пік)
    g2_x, g2_y = 480, 290
    elems.append(rect(g2_x, g2_y, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    elems.append(line(g2_x + 10, g2_y + gh - 20, g2_x + gw - 10, g2_y + gh - 20, color=MUTED, sw=1.0))
    elems.append(line(g2_x + gw / 2, g2_y + 10, g2_x + gw / 2, g2_y + gh - 10, color=MUTED, sw=1.0, dash="3,3"))
    elems.append(text(g2_x + gw / 2, g2_y + 22, "GCC-PHAT (гострий пік справжньої затримки τ₀)", size=11, color=FIELD, anchor="middle", bold=True))

    pts_phat = []
    for i in range(120):
        t = (i - 60) / 15.0
        val = math.exp(-4.5 * (t - 1.2) ** 2) + 0.08 * math.sin(7.0 * t) * math.exp(-0.1 * abs(t))
        py = g2_y + gh - 25 - max(0, val * 75)
        pts_phat.append("%.1f,%.1f" % (g2_x + 20 + i * (gw - 40) / 120.0, py))
    elems.append('<polyline fill="none" stroke="%s" stroke-width="2.2" points="%s"/>' % (FIELD, " ".join(pts_phat)))

    # Відмітка справжньої затримки
    tau_x = g2_x + 20 + (1.2 * 15.0 + 60) * (gw - 40) / 120.0
    elems.append(line(tau_x, g2_y + gh - 25, tau_x, g2_y + 35, color=FIELD, sw=1.2, dash="2,2"))
    elems.append(text(tau_x + 5, g2_y + 45, "τ = τ₀", size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, "gcc-phat-cross-correlation.svg"), W, H,
           *elems, title="Конвеєр GCC-PHAT та порівняння форми піку кореляції")


# ── Фігура 3: Delay-and-Sum Beamformer ─────────────────────────────────────────
def fig_delay_and_sum():
    W, H = 880, 500
    elems = []

    m_names = ["Мікрофон 0: x₀(t)", "Мікрофон 1: x₁(t)", "Мікрофон 2: x₂(t)", "Мікрофон 3: x₃(t)"]
    delays = ["Затримка τ₀(θ)", "Затримка τ₁(θ)", "Затримка τ₂(θ)", "Затримка τ₃(θ)"]
    weights = ["Вага w₀", "Вага w₁", "Вага w₂", "Вага w₃"]

    y_spacing = 80
    y_start = 80

    for i in range(4):
        y = y_start + i * y_spacing

        # Вхід мікрофона
        elems.append(rect(40, y - 20, 160, 40, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=5))
        elems.append(text(120, y + 5, m_names[i], size=12, color=INK, anchor="middle", bold=True))

        # Стрілка до затримки
        elems.append(arrow(200, y, 255, y, color=LINE, sw=1.5))

        # Блок затримки
        elems.append(rect(260, y - 20, 140, 40, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=5))
        elems.append(text(330, y + 5, delays[i], size=12, color="#0369a1", anchor="middle", bold=True))

        # Стрілка до ваги
        elems.append(arrow(400, y, 455, y, color=LINE, sw=1.5))

        # Блок аподизації / ваги
        elems.append(rect(460, y - 20, 110, 40, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=5))
        elems.append(text(515, y + 5, weights[i], size=12, color="#854d0e", anchor="middle", bold=True))

        # Стрілка до суматора
        elems.append(line(570, y, 670, y, color=LINE, sw=1.5))
        elems.append(arrow(670, y, 710, 200, color=LINE, sw=1.5))

    # Суматор (велике коло)
    sum_cx, sum_cy = 730, 200
    elems.append(circle(sum_cx, sum_cy, 30, fill="#ecfdf5", stroke=FIELD, sw=2.5))
    elems.append(text(sum_cx, sum_cy + 8, "Σ", size=26, color=FIELD, anchor="middle", bold=True))

    # Вихід
    elems.append(arrow(sum_cx + 30, sum_cy, 800, sum_cy, color=FIELD, sw=2.2))
    elems.append(rect(805, sum_cy - 25, 65, 50, fill="#dcfce7", stroke=FIELD, sw=2.0, rx=6))
    elems.append(text(837, sum_cy - 2, "Вихід", size=11, color="#15803d", anchor="middle"))
    elems.append(text(837, sum_cy + 15, "y(t)", size=12, color="#15803d", anchor="middle", bold=True))

    # Пояснювальний блок унизу
    box, _, _ = textbox(440, 435,
                        "Принцип фазування променя (Beamforming):\n"
                        "• Сигнали з цільового напрямку θ компенсуються затримками τ_m(θ) і складаються СИНФАЗНО (+6 dB на кожне подвоєння M)\n"
                        "• Некорельований шум середовища та звуки з інших напрямків інтерферують деструктивно й придушуються",
                        size=12, fill="#f8fafc", stroke="#cbd5e1", pad=10)
    elems.append(box)

    render(os.path.join(IMG, "delay-and-sum-beamformer.svg"), W, H,
           *elems, title="Структурна схема алгоритму Delay-and-Sum")


# ── Фігура 4: Просторове накладання та ґраткові пелюстки (Aliasing) ───────────
def fig_spatial_aliasing():
    W, H = 880, 460
    elems = []

    # Три графіки діаграми спрямованості для d = λ/4, d = λ/2, d = λ
    xs = [160, 440, 720]
    titles = ["(а) Крок d = λ / 4", "(б) Крок d = λ / 2 (критичний)", "(в) Крок d = λ (аліасинг)"]
    subtitles = ["Широкий головний промінь", "Оптимальна роздільність", "Хибні пелюстки (Grating lobes)"]
    colors = [NEG, FIELD, POS]

    for k in range(3):
        cx = xs[k]
        cy = 240
        w_box = 230
        h_box = 240

        elems.append(rect(cx - w_box / 2, cy - h_box / 2, w_box, h_box, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
        elems.append(text(cx, cy - h_box / 2 + 20, titles[k], size=13, color=colors[k], anchor="middle", bold=True))
        elems.append(text(cx, cy - h_box / 2 + 36, subtitles[k], size=11, color=MUTED, anchor="middle"))

        # Осі координат
        gx0 = cx - 95
        gx1 = cx + 95
        gy0 = cy + 80
        elems.append(line(gx0, gy0, gx1, gy0, color=MUTED, sw=1.0))
        elems.append(line(cx, gy0 + 5, cx, cy - 60, color=MUTED, sw=1.0, dash="2,2"))

        # Підписи кутів
        elems.append(text(gx0, gy0 + 15, "-90°", size=10, color=MUTED, anchor="middle"))
        elems.append(text(cx, gy0 + 15, "0°", size=10, color=MUTED, anchor="middle"))
        elems.append(text(gx1, gy0 + 15, "+90°", size=10, color=MUTED, anchor="middle"))

        # Розрахунок діаграми масиву з M=6 елементів
        M = 6
        pts = []
        d_ratio = [0.25, 0.5, 1.0][k]
        for i in range(181):
            deg = i - 90
            rad = math.radians(deg)
            psi = 2.0 * math.pi * d_ratio * math.sin(rad)
            if abs(psi) < 1e-6:
                af = 1.0
            else:
                af = abs(math.sin(M * psi / 2.0) / (M * math.sin(psi / 2.0)))

            px = cx + (deg / 90.0) * 90.0
            py = gy0 - af * 120.0
            pts.append("%.1f,%.1f" % (px, py))

        elems.append('<polyline fill="none" stroke="%s" stroke-width="2.0" points="%s"/>' % (colors[k], " ".join(pts)))

        if k == 2:
            # Стрілки на ґраткові пелюстки при d = λ
            elems.append(text(cx - 75, gy0 - 128, "0 dB", size=11, color=POS, anchor="middle", bold=True))
            elems.append(text(cx + 75, gy0 - 128, "0 dB", size=11, color=POS, anchor="middle", bold=True))
            elems.append(arrow(cx - 75, gy0 - 115, cx - 85, gy0 - 100, color=POS, sw=1.4))
            elems.append(arrow(cx + 75, gy0 - 115, cx + 85, gy0 - 100, color=POS, sw=1.4))

    # Висновок внизу
    box, _, _ = textbox(440, 410,
                        "Критерій просторової дискретизації Найквіста: d ≤ λ / 2  (або f_max ≤ c / 2d)\n"
                        "При d > λ/2 виникають хибні головні пелюстки однакової потужності — масив «чує привидів»",
                        size=12, fill="#f8fafc", stroke="#94a3b8", pad=10)
    elems.append(box)

    render(os.path.join(IMG, "spatial-aliasing-grating-lobes.svg"), W, H,
           *elems, title="Просторове накладання спектрів та виникнення ґраткових пелюсток")


# ── Фігура 5: Геометрії масивів та їх просторовий огляд ───────────────────────
def fig_array_geometries():
    W, H = 880, 480
    elems = []

    # 1. Лінійний масив (1D ULA)
    c1_x, c1_y = 155, 210
    w1, h1 = 250, 340
    elems.append(rect(c1_x - w1 / 2, c1_y - h1 / 2, w1, h1, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    elems.append(text(c1_x, c1_y - h1 / 2 + 25, "1D Лінійний (ULA)", size=14, color=INK, anchor="middle", bold=True))
    elems.append(text(c1_x, c1_y - h1 / 2 + 45, "Одновимірна апертура", size=12, color=MUTED, anchor="middle"))

    # Схема 1D мікрофонів
    elems.append(line(c1_x - 90, c1_y - 20, c1_x + 90, c1_y - 20, color="#94a3b8", sw=2.0))
    for dx in [-75, -45, -15, 15, 45, 75]:
        elems.append(circle(c1_x + dx, c1_y - 20, 6, fill=POS, stroke=POS, sw=1.0))

    # Конус неоднозначності
    elems.append(line(c1_x, c1_y - 20, c1_x + 70, c1_y - 100, color=FIELD, sw=1.5, dash="3,3"))
    elems.append(line(c1_x, c1_y - 20, c1_x + 70, c1_y + 60, color=FIELD, sw=1.5, dash="3,3"))
    elems.append(text(c1_x, c1_y + 80, "Дзеркальна неоднозначність:\nкут θ не відрізняється від -θ\n(перед/зад однакові)", size=11, color=POS, anchor="middle"))

    # 2. Кільцевий масив (2D UCA)
    c2_x, c2_y = 440, 210
    w2, h2 = 250, 340
    elems.append(rect(c2_x - w2 / 2, c2_y - h2 / 2, w2, h2, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    elems.append(text(c2_x, c2_y - h2 / 2 + 25, "2D Кільцевий (UCA)", size=14, color=INK, anchor="middle", bold=True))
    elems.append(text(c2_x, c2_y - h2 / 2 + 45, "Круговий азимут 360°", size=12, color=MUTED, anchor="middle"))

    # Кільце мікрофонів
    elems.append(circle(c2_x, c2_y - 20, 55, fill="none", stroke="#94a3b8", sw=1.5))
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        elems.append(circle(c2_x + 55 * math.cos(rad), c2_y - 20 + 55 * math.sin(rad), 6, fill=FIELD, stroke=FIELD, sw=1.0))

    elems.append(text(c2_x, c2_y + 80, "Повний круговий огляд 360°:\nоднакова роздільність у всіх\nнапрямках площини азимута", size=11, color=FIELD, anchor="middle"))

    # 3. Матричний / Планарний масив (2D URA)
    c3_x, c3_y = 725, 210
    w3, h3 = 250, 340
    elems.append(rect(c3_x - w3 / 2, c3_y - h3 / 2, w3, h3, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    elems.append(text(c3_x, c3_y - h3 / 2 + 25, "2D Матричний (URA)", size=14, color=INK, anchor="middle", bold=True))
    elems.append(text(c3_x, c3_y - h3 / 2 + 45, "Азимут (θ) + Елевація (φ)", size=12, color=MUTED, anchor="middle"))

    # Матриця 4x4
    for gx in [-45, -15, 15, 45]:
        for gy in [-65, -35, -5, 25]:
            elems.append(circle(c3_x + gx, c3_y + gy, 5, fill=NEG, stroke=NEG, sw=1.0))
    elems.append(rect(c3_x - 55, c3_y - 75, 110, 110, fill="none", stroke="#94a3b8", sw=1.2, rx=4))

    elems.append(text(c3_x, c3_y + 80, "3D просторова пеленгація:\nлокалізація джерела у півсфері\nпо куту азимута та місця", size=11, color=NEG, anchor="middle"))

    # Загальний підпис унизу
    box, _, _ = textbox(440, 435,
                        "Вибір топології: 1D — для вузьких балок (телевізори, саундбари); 2D кільцеві — для смарт-колонок і конференцій;\n"
                        "2D планарні та сферичні — для акустичних камер, дронів і локалізації шуму промислового обладнання",
                        size=12, fill="#f8fafc", stroke="#94a3b8", pad=8)
    elems.append(box)

    render(os.path.join(IMG, "array-geometries-comparison.svg"), W, H,
           *elems, title="Порівняння геометрій мікрофонних масивів та їхніх властивостей")


if __name__ == "__main__":
    fig_array_geometry()
    fig_gcc_phat()
    fig_delay_and_sum()
    fig_spatial_aliasing()
    fig_array_geometries()
    print("Усі 5 фігур успішно згенеровано у ./img/")
