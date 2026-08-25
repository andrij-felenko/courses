# -*- coding: utf-8 -*-
"""Генератор векторних схем (SVG) для теми «Ємність каналу за Шенноном» (shannon-capacity).
Вивід: ./img/*.svg
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_sphere_packing():
    """Геометрична інтуїція Шеннона: пакування гіперсфер у просторі сигналів розмірності N = 2BT."""
    w, h = 820, 480
    frags = []

    # Заголовок / фонова зона простору сигналів
    frags.append(rect(15, 15, 790, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(410, 42, "Геометрична модель Шеннона: N-вимірний простір сигналів (N = 2·B·T)", size=15, bold=True))

    # Велика сфера прийнятого сигналу (сигнал + шум)
    # Центр (290, 255), радіус R = 175
    cx, cy, R = 290, 255, 175
    frags.append(circle(cx, cy, R, fill="#eff6ff", stroke=NEG, sw=2))

    # Радіус великої сфери: стрілка від центру до краю під кутом -55 градусів
    angle_r = math.radians(-55)
    rx_end = cx + R * math.cos(angle_r)
    ry_end = cy + R * math.sin(angle_r)
    frags.append(line(cx, cy, rx_end, ry_end, color=NEG, sw=1.8, dash="4,4"))
    b_rtot, _, _ = textbox(cx + 120, cy - 145, "R_tot = √(N·(P + N_noise))", size=11, pad=6, fill="#ffffff", stroke=NEG)
    frags.append(b_rtot)

    # Точки кодових слів і шумові сфери
    points = [
        (cx, cy, "s_0"),
        (cx - 95, cy - 65, "s_1"),
        (cx + 90, cy - 50, "s_2"),
        (cx - 85, cy + 70, "s_3"),
        (cx + 75, cy + 75, "s_4"),
        (cx - 110, cy + 5, "s_5"),
    ]
    r_noise = 38

    for px, py, label in points:
        # Шумова сфера навколо точки
        frags.append(circle(px, py, r_noise, fill="#fee2e2", stroke=POS, sw=1.2))
        # Кодова точка в центрі
        frags.append(circle(px, py, 4, fill=POS, stroke="#991b1b", sw=1))
        frags.append(text(px, py - 6, label, size=11, color="#991b1b", bold=True))

    # Стрілка радіуса однієї шумової сфери
    frags.append(line(cx + 75, cy + 75, cx + 75 + r_noise * math.cos(math.radians(30)),
                      cy + 75 + r_noise * math.sin(math.radians(30)), color=POS, sw=1.5))
    frags.append(text(cx + 122, cy + 105, "r_шуму = √(N·N_noise)", size=11, color=POS, bold=True))

    # Пояснювальний блок праворуч
    bx = 585
    b1, _, _ = textbox(bx, 110, "Об'єм у просторі N вимірів:\nVol(R) ∝ R^N", size=13, pad=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b1)

    b2, _, _ = textbox(bx, 220, "Кількість куль без перекриття:\nM = (R_tot / r_шуму)^N\nM = (1 + P / N_noise)^(N/2)", size=13, pad=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b2)

    b3, _, _ = textbox(bx, 345, "Кількість біт за час T (N = 2·B·T):\nI = log₂(M) = B·T · log₂(1 + SNR)\n\nЄмність каналу (біт/с):\nC = I / T = B · log₂(1 + SNR)", size=12, pad=10, fill="#f0fdf4", stroke=FIELD)
    frags.append(b3)

    # Нижній висновок
    frags.append(text(410, 448, "При N → ∞ шумова енергія концентрується на тонкій сфері: помилка декодування зникає", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, "sphere-packing.svg"), w, h, *frags)


def fig_bandwidth_power_tradeoff():
    """Спектральна ефективність eta = C/B проти Eb/N0 (дБ): межа Шеннона та робочі режими."""
    w, h = 820, 520
    frags = []

    frags.append(rect(15, 15, 790, 490, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(410, 42, "Спектральна ефективність η = C/B проти Eb/N0: межа Шеннона", size=15, bold=True))

    # Графік: осі
    ox, oy = 110, 430
    gw, gh = 660, 340

    # Сітка та координати
    # Eb/N0 від -2 дБ до +25 дБ
    # eta від 0 до 10 біт/с/Гц
    def to_x(eb_db):
        return ox + (eb_db - (-2.0)) / (26.0 - (-2.0)) * gw

    def to_y(eta_val):
        return oy - (eta_val / 10.0) * gh

    # Мітки та короткі поділки по осі X
    for eb in [0, 5, 10, 15, 20, 25]:
        gx = to_x(eb)
        frags.append(line(gx, oy, gx, oy + 6, color=LINE, sw=1.2))
        frags.append(text(gx, oy + 18, f"{eb:g} дБ", size=11, color=MUTED))

    # Мітки та короткі поділки по осі Y
    for eta in [2, 4, 6, 8, 10]:
        gy = to_y(eta)
        frags.append(line(ox - 6, gy, ox, gy, color=LINE, sw=1.2))
        frags.append(text(ox - 12, gy + 4, f"{eta}", size=11, color=MUTED, anchor="end"))

    # Осі
    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 10, oy + 32, "Eb / N0 (дБ)", size=12, bold=True, anchor="end"))
    frags.append(text(ox - 10, oy - gh - 12, "η = C/B (біт/с/Гц)", size=12, bold=True, anchor="end"))

    # Абсолютна межа Шеннона: вертикальна асимптота Eb/N0 = -1.59 dB
    x_shannon_lim = to_x(-1.59)
    frags.append(line(x_shannon_lim, oy, x_shannon_lim, oy - gh, color=POS, sw=2, dash="5,5"))
    frags.append(text(x_shannon_lim + 6, oy - gh - 8, "Абсолютна межа: -1.59 дБ (при η → 0, B → ∞)", size=10, color=POS, bold=True, anchor="start"))

    # Область неможливого (ліворуч від кривої)
    # Побудова теоретичної кривої Шеннона: Eb/N0 = (2^eta - 1) / eta
    pts_shannon = []
    for step in range(1, 201):
        eta = 0.05 + step * (9.95 / 200)
        eb_lin = (2.0**eta - 1.0) / eta
        eb_db = 10.0 * math.log10(eb_lin)
        if eb_db <= 25.5:
            pts_shannon.append((to_x(eb_db), to_y(eta)))

    path_d = ["M %.1f %.1f" % (x_shannon_lim, oy)]
    for px, py in pts_shannon:
        path_d.append("L %.1f %.1f" % (px, py))

    frags.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    frags.append(text(to_x(11), to_y(7.6), "Теоретична межа Шеннона C/B", size=13, color=FIELD, bold=True))

    # Практичні модуляції (з розривом Шеннона ~1.5 - 3 дБ)
    mods = [
        ("BPSK (1/2)", 0.5, 0.5, "#475569"),
        ("QPSK (3/4)", 1.5, 3.8, "#475569"),
        ("16-QAM (3/4)", 3.0, 8.0, "#2563eb"),
        ("64-QAM (5/6)", 5.0, 13.5, "#2563eb"),
        ("256-QAM (5/6)", 6.67, 18.8, "#7c3aed"),
        ("1024-QAM (5/6)", 8.33, 24.2, "#7c3aed"),
    ]
    for name, eta_m, eb_req, col in mods:
        mx = to_x(eb_req)
        my = to_y(eta_m)
        frags.append(circle(mx, my, 4.5, fill=col, stroke="#ffffff", sw=1.5))
        frags.append(text(mx + 8, my + 4, name, size=10, color=col, bold=True, anchor="start"))

    # Два режими: блоки у вільних зонах
    # Режим 1: Power-limited (ліворуч угорі)
    b_pwr, _, _ = textbox(245, 145, "Обмеження за потужністю\n(Power-limited regime)\n• SNR < 0 дБ, η < 1 біт/с/Гц\n• DSSS, CDMA, LoRa, GPS, Deep Space\n• Розширюємо смугу B для виграшу", size=11, pad=8, fill="#eff6ff", stroke=NEG)
    frags.append(b_pwr)

    # Режим 2: Bandwidth-limited (праворуч унизу)
    b_bw, _, _ = textbox(635, 345, "Обмеження за смугою\n(Bandwidth-limited regime)\n• SNR >> 0 дБ, η > 2..8 біт/с/Гц\n• Wi-Fi 6/7, 5G NR, DSL, Кабельні модеми\n• Зростання потужності дає лише log₂(SNR)", size=11, pad=8, fill="#fef2f2", stroke=POS)
    frags.append(b_bw)

    render(os.path.join(IMG_DIR, "bandwidth-power-tradeoff.svg"), w, h, *frags)


def fig_dmt_waterfilling():
    """Дискретна багаточастотна модуляція (DMT / OFDM) та розподіл бітів (Water-filling) за Шенноном."""
    w, h = 820, 460
    frags = []

    frags.append(rect(15, 15, 790, 430, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(410, 42, "Розподіл бітів за піднесучими у DSL / OFDM за формулою Шеннона", size=15, bold=True))

    ox, oy = 80, 380
    gw, gh = 680, 280

    # Осі
    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 15, oy + 25, "Частота піднесучих f (кГц / МГц)", size=12, bold=True, anchor="end"))
    frags.append(text(ox - 10, oy - gh - 10, "Потужність / Шум N(f) / H(f)", size=12, bold=True, anchor="end"))

    # Стовпчики піднесучих (DMT bins)
    num_bins = 24
    bin_w = (gw - 40) / num_bins
    water_level = oy - 230  # рівень «води» (сумарний рівень потужності)

    frags.append(line(ox + 20, water_level, ox + gw, water_level, color=FIELD, sw=2, dash="6,4"))
    frags.append(text(ox + gw - 10, water_level - 10, "Рівень розподілу потужності (Water-filling level λ)", size=11, color=FIELD, bold=True, anchor="end"))

    for i in range(num_bins):
        bx = ox + 25 + i * bin_w
        # Профіль шуму + згасання (росте з частотою)
        # Низькі частоти: низький рівень шуму, висока потужність сигналу
        noise_h = 40 + 1.2 * (i**1.6)
        noise_top = oy - noise_h

        # Нижня частина: профіль завад і згасання каналу N_k / |H_k|²
        frags.append(rect(bx, noise_top, bin_w - 4, noise_h, fill="#fee2e2", stroke="#f87171", sw=1, rx=2))

        # Верхня частина: потужність сигналу P_k (до рівня water_level)
        if noise_top > water_level:
            pwr_h = noise_top - water_level
            frags.append(rect(bx, water_level, bin_w - 4, pwr_h, fill="#dbeafe", stroke="#60a5fa", sw=1, rx=2))

            # Кількість біт на цій піднесучій b_k = log2(1 + SNR_k)
            bits = max(1, int(round(pwr_h / 14)))
            if i % 2 == 0:
                frags.append(text(bx + (bin_w - 4) / 2, water_level + pwr_h / 2 + 4, f"{bits}б", size=10, color=NEG, bold=True))
        else:
            # Канал занадто шумний: 0 біт (піднесуча вимкнена)
            frags.append(text(bx + (bin_w - 4) / 2, noise_top - 8, "0", size=10, color=POS, bold=True))

    # Пояснення зон
    frags.append(rect(ox + 40, 75, 230, 48, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(ox + 155, 95, "Сигнал P_k (виділена потужність)", size=11, color=NEG, bold=True))
    frags.append(text(ox + 155, 112, "b_k = log₂(1 + SNR_k / Γ) біт/символ", size=10, color=INK))

    frags.append(rect(ox + 290, 75, 230, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(ox + 405, 95, "Шум і згасання каналу N_k / |H_k|²", size=11, color=POS, bold=True))
    frags.append(text(ox + 405, 112, "Зростає на високих частотах у кабелі", size=10, color=INK))

    render(os.path.join(IMG_DIR, "dmt-waterfilling.svg"), w, h, *frags)


def fig_optical_nonlinear_limit():
    """Нелінійна межа Шеннона в оптичних волокнах (ефект Керра)."""
    w, h = 820, 480
    frags = []

    frags.append(rect(15, 15, 790, 450, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=10))
    frags.append(text(410, 42, "Нелінійна межа Шеннона в оптичному волокні (ефект Керра)", size=15, bold=True))

    ox, oy = 90, 400
    gw, gh = 660, 300

    # Осі
    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 10, oy + 28, "Оптична потужність випромінювання P (дБм / мВт)", size=12, bold=True, anchor="end"))
    frags.append(text(ox - 10, oy - gh - 10, "Ємність волокна C (Тбіт/с)", size=12, bold=True, anchor="end"))

    # Крива 1: Лінійна ємність Шеннона AWGN C = B * log2(1 + P / N_ase)
    pts_linear = []
    for step in range(1, 101):
        x_norm = step / 100.0
        p_val = x_norm * 10.0
        # Логарифмічне зростання
        c_lin = 40.0 * math.log2(1.0 + p_val * 4.0)
        px = ox + x_norm * gw
        py = oy - (c_lin / 240.0) * gh
        pts_linear.append((px, py))

    path_lin = ["M %.1f %.1f" % (ox, oy)] + ["L %.1f %.1f" % pt for pt in pts_linear]
    frags.append(f'<path d="{" ".join(path_lin)}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6,5"/>')
    frags.append(text(ox + gw - 30, oy - gh + 25, "Класичний лінійний Шеннон C = B·log₂(1 + SNR)", size=12, color=MUTED, bold=True, anchor="end"))

    # Крива 2: Реальна нелінійна межа оптичного волокна
    # C_opt = B * log2(1 + P / (N_ase + gamma^2 * P^3))
    pts_opt = []
    opt_peak_x, opt_peak_y = 0, 0
    max_c = 0
    for step in range(1, 101):
        x_norm = step / 100.0
        p_val = x_norm * 12.0
        n_ase = 0.4
        n_nl = 0.008 * (p_val**3)
        snr_eff = p_val / (n_ase + n_nl)
        c_opt = 36.0 * math.log2(1.0 + snr_eff)
        px = ox + x_norm * gw
        py = oy - (c_opt / 240.0) * gh
        pts_opt.append((px, py))
        if c_opt > max_c:
            max_c = c_opt
            opt_peak_x, opt_peak_y = px, py

    path_opt = ["M %.1f %.1f" % (ox, oy)] + ["L %.1f %.1f" % pt for pt in pts_opt]
    frags.append(f'<path d="{" ".join(path_opt)}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Пік ємності
    frags.append(circle(opt_peak_x, opt_peak_y, 6, fill=POS, stroke="#991b1b", sw=1.5))
    frags.append(line(opt_peak_x, oy, opt_peak_x, opt_peak_y, color=POS, sw=1.2, dash="4,4"))
    frags.append(text(opt_peak_x, oy + 16, "Оптимальна потужність P_opt", size=11, color=POS, bold=True))

    # Зони графіка
    b_lin, _, _ = textbox(240, 150, "Лінійна зона:\n• Домінує шум підсилювача (ASE)\n• Нарощування P піднімає ємність", size=11, pad=8, fill="#eff6ff", stroke=NEG)
    frags.append(b_lin)

    b_nlin, _, _ = textbox(600, 240, "Нелінійна зона (Керр):\n• Самомодуляція фази (SPM/XPM)\n• Нелінійні спотворення діють як шум ~ P³\n• Подальше зростання P ЗНИЖУЄ ємність!", size=11, pad=8, fill="#fee2e2", stroke=POS)
    frags.append(b_nlin)

    render(os.path.join(IMG_DIR, "optical-nonlinear-limit.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_sphere_packing()
    fig_bandwidth_power_tradeoff()
    fig_dmt_waterfilling()
    fig_optical_nonlinear_limit()
    print("All figures generated successfully.")
