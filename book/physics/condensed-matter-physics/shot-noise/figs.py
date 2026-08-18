# -*- coding: utf-8 -*-
"""Фігури до теми «Дробовий шум».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Механізм виникнення дробового шуму ─────────────────────────────
def fig_shot_noise_mechanism():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Механізм дробового шуму: дискретність заряду та випадковий час емісії", size=16, bold=True, color=INK))

    # Верхня панель: фіз. картина (барьєр і дискретні електрони)
    f.append(rect(40, 50, 680, 150, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    f.append(text(160, 72, "Катод / Емітер", size=13, bold=True, color="#1e3a8a"))
    f.append(text(600, 72, "Анод / Колектор", size=13, bold=True, color="#1e3a8a"))

    # Потенціальний бар'єр
    f.append(path_svg("M 240 180 L 300 100 L 360 180", stroke="#dc2626", sw=2.5))
    f.append(text(300, 92, "Потенціальний бар'єр Φ", size=11, bold=True, color="#dc2626"))

    # Електрони (дискретні носії q = e)
    electrons = [(100, 130), (140, 150), (180, 120), (220, 140),
                 (320, 120), (380, 150), (450, 130), (520, 140), (580, 125)]
    for x, y in electrons:
        f.append(circle(x, y, 9, fill="#2457d6", stroke="#1d4ed8"))
        f.append(text(x, y + 3.5, "e⁻", size=10, bold=True, color="#ffffff"))

    # Стрілка руху електронів
    f.append(arrow(230, 130, 280, 130, color="#2563eb", sw=2))
    f.append(arrow(370, 130, 420, 130, color="#2563eb", sw=2))

    # Нижня панель: Осцилограма струму I(t)
    f.append(rect(40, 220, 680, 160, fill="#ffffff", stroke="#cbd5e1", rx=6))

    # Осі
    x0, y0 = 80, 350
    x_max, y_top = 680, 245
    f.append(arrow(x0, y0, x_max, y0, color=INK, sw=1.5))
    f.append(text(x_max + 15, y0 + 4, "t", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x0, y0, x0, y_top, color=INK, sw=1.5))
    f.append(text(x0 - 20, y_top - 5, "I(t)", size=13, bold=True, color=INK))

    # Лінія середнього струму <I>
    y_avg = 295
    f.append(line(x0, y_avg, x_max - 20, y_avg, color="#059669", sw=2, dash="5,4"))
    f.append(text(x0 + 45, y_avg - 8, "Середній струм ⟨I⟩ = q · n̄", size=11, bold=True, color="#059669"))

    # Генерація імпульсів від окремих електронів (сума pulses)
    pulse_centers = [120, 175, 210, 310, 345, 410, 490, 530, 610]
    pts = []
    for px in range(x0, x_max - 20, 2):
        val = 0.0
        for pc in pulse_centers:
            dt = (px - pc) / 7.0
            val += math.exp(-dt * dt) * 35.0
        y = y_avg - val + 5.0
        pts.append((px, y))

    d_i = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    f.append(path_svg(d_i, stroke="#2457d6", sw=2))

    # Флуктуація ΔI(t)
    f.append(arrow(260, y_avg, 260, y_avg - 28, color="#dc2626", sw=1.5))
    f.append(text(265, y_avg - 14, "Флуктуація ΔI(t)", size=11, bold=True, color="#dc2626", anchor="start"))

    f.append(text(W / 2, H - 12, "Кожен електрон створює імпульс i_k(t); випадковий час емісії генерує білий шумовий спектр S_I = 2 q ⟨I⟩", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'shot-noise-mechanism.svg'), W, H, "\n".join(f))

# ── Фігура 2: Спектральна густина потужності шуму ───────────────────────────
def fig_spectral_density():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Спектральна густина потужності: дробовий, тепловий та 1/f шум", size=16, bold=True, color=INK))

    x0, y0 = 90, 350
    x_max, y_top = 700, 60
    f.append(rect(x0 - 10, y_top - 10, x_max - x0 + 20, y0 - y_top + 20, fill="#f8fafc", stroke="#cbd5e1", rx=4))

    # Осі
    f.append(arrow(x0, y0, x_max, y0, color=INK, sw=1.5))
    f.append(text(x_max + 15, y0 + 4, "f (Гц)", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x0, y0, x0, y_top - 15, color=INK, sw=1.5))
    f.append(text(x0 - 25, y_top - 10, "S_I(f) [А²/Гц]", size=12, bold=True, color=INK))

    # 1. Дробовий шум S_shot = 2 q I
    y_shot = 200
    x_tau = 540
    pts_shot = []
    for x in range(x0, x_tau):
        pts_shot.append((x, y_shot))
    for x in range(x_tau, x_max - 20):
        f_rel = (x - x_tau) / 35.0
        att = 1.0 / (1.0 + f_rel * f_rel)
        pts_shot.append((x, y0 - (y0 - y_shot) * att))

    d_shot = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_shot)
    f.append(path_svg(d_shot, stroke="#2457d6", sw=3))
    f.append(text(280, y_shot - 12, "Дробовий шум S_I = 2 q I (білий шум)", size=12, bold=True, color="#2457d6"))

    # 2. Тепловий шум S_thermal = 4 k_B T / R
    y_therm = 270
    f.append(line(x0, y_therm, x_max - 20, y_therm, color="#059669", sw=2.5, dash="6,3"))
    f.append(text(280, y_therm + 18, "Тепловий шум S_I = 4 k_B T / R (Джонсона — Найквіста)", size=11, bold=True, color="#059669"))

    # 3. Фліккер-шум 1/f
    pts_flicker = []
    for x in range(x0, 360):
        dx = (x - x0) / 25.0 + 0.3
        y = y0 - (240.0 / (dx**0.85))
        if y < y_top + 10:
            y = y_top + 10
        pts_flicker.append((x, y))
    d_flicker = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_flicker)
    f.append(path_svg(d_flicker, stroke="#dc2626", sw=2.5))
    f.append(text(140, 110, "Фліккер-шум 1/f (~1/f^α)", size=12, bold=True, color="#dc2626"))

    # Гранична частота прольоту f_c = 1 / (2 π τ)
    f.append(line(x_tau, y_top - 5, x_tau, y0, color="#6b7280", sw=1.5, dash="3,3"))
    f.append(text(x_tau, y0 + 20, "f_c ≈ 1/τ", size=11, bold=True, color="#6b7280"))
    f.append(text(x_tau + 5, y_shot - 35, "Зріз на частоті прольоту τ", size=10, color="#6b7280", anchor="start"))

    # Частота зрізу фліккер-шуму f_corner
    x_corner = 235
    f.append(circle(x_corner, y_shot, 5, fill="#dc2626", stroke="#ffffff"))
    f.append(line(x_corner, y_shot, x_corner, y0, color="#dc2626", sw=1.2, dash="3,3"))
    f.append(text(x_corner, y0 + 20, "f_corner", size=11, bold=True, color="#dc2626"))

    f.append(text(W / 2, H - 12, "Дробовий шум має плаский спектр до частот порядка оберненого часу прольоту τ носія через бар'єр", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spectral-density.svg'), W, H, "\n".join(f))

# ── Фігура 3: Фактор Фано в різних режимах переносу ──────────────────────────
def fig_fano_factor():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Фактор Фано F = S_I / (2 q I) у квантовому та класичному переносі", size=16, bold=True, color=INK))

    col_w = 210
    h_box = 300
    y_top = 60

    # 1. Субпуассонівський (F < 1)
    x1 = 40
    f.append(rect(x1, y_top, col_w, h_box, fill="#eff6ff", stroke="#93c5fd", rx=6))
    f.append(text(x1 + col_w / 2, y_top + 25, "Субпуассонівський", size=14, bold=True, color="#1e40af"))
    f.append(text(x1 + col_w / 2, y_top + 45, "F < 1 (Впорядкований)", size=13, bold=True, color="#2563eb"))

    f.append(text(x1 + col_w / 2, y_top + 80, "Механізми:", size=11, bold=True, color=INK))
    f.append(text(x1 + col_w / 2, y_top + 105, "• Кулонівська блокада", size=11, color=INK))
    f.append(text(x1 + col_w / 2, y_top + 125, "• Заборона Паулі (1D кл.)", size=11, color=INK))
    f.append(text(x1 + col_w / 2, y_top + 145, "• Балістичні QPC (F=0)", size=11, color=INK))

    # Схема носіїв
    f.append(rect(x1 + 15, y_top + 175, col_w - 30, 80, fill="#ffffff", stroke="#bfdbfe", rx=4))
    for px in [x1 + 35, x1 + 80, x1 + 125, x1 + 170]:
        f.append(circle(px, y_top + 215, 8, fill="#2563eb", stroke="#1d4ed8"))
        f.append(text(px, y_top + 218.5, "e⁻", size=9, bold=True, color="#ffffff"))
    f.append(text(x1 + col_w / 2, y_top + 272, "Регулярні інтервали Δt", size=10, italic=True, color="#1e40af"))

    # 2. Пуассонівський (F = 1)
    x2 = 275
    f.append(rect(x2, y_top, col_w, h_box, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    f.append(text(x2 + col_w / 2, y_top + 25, "Класичний Пуассонівський", size=14, bold=True, color="#334155"))
    f.append(text(x2 + col_w / 2, y_top + 45, "F = 1 (Незалежні події)", size=13, bold=True, color="#475569"))

    f.append(text(x2 + col_w / 2, y_top + 80, "Механізми:", size=11, bold=True, color=INK))
    f.append(text(x2 + col_w / 2, y_top + 105, "• Вакуумні діоди", size=11, color=INK))
    f.append(text(x2 + col_w / 2, y_top + 125, "• p-n перехід (зворотний)", size=11, color=INK))
    f.append(text(x2 + col_w / 2, y_top + 145, "• Тунельний бар'єр D ≪ 1", size=11, color=INK))

    # Схема носіїв
    f.append(rect(x2 + 15, y_top + 175, col_w - 30, 80, fill="#ffffff", stroke="#cbd5e1", rx=4))
    for px in [x2 + 30, x2 + 50, x2 + 110, x2 + 175]:
        f.append(circle(px, y_top + 215, 8, fill="#64748b", stroke="#334155"))
        f.append(text(px, y_top + 218.5, "e⁻", size=9, bold=True, color="#ffffff"))
    f.append(text(x2 + col_w / 2, y_top + 272, "Випадкові інтервали (Пуассон)", size=10, italic=True, color="#475569"))

    # 3. Суперпуассонівський (F > 1)
    x3 = 510
    f.append(rect(x3, y_top, col_w, h_box, fill="#fff7ed", stroke="#fed7aa", rx=6))
    f.append(text(x3 + col_w / 2, y_top + 25, "Суперпуассонівський", size=14, bold=True, color="#c2410c"))
    f.append(text(x3 + col_w / 2, y_top + 45, "F > 1 (Кластеризований)", size=13, bold=True, color="#ea580c"))

    f.append(text(x3 + col_w / 2, y_top + 80, "Механізми:", size=11, bold=True, color=INK))
    f.append(text(x3 + col_w / 2, y_top + 105, "• Лавинне множення M > 1", size=11, color=INK))
    f.append(text(x3 + col_w / 2, y_top + 125, "• Групування носіїв (bunching)", size=11, color=INK))
    f.append(text(x3 + col_w / 2, y_top + 145, "• Двобар'єрний резонанс", size=11, color=INK))

    # Схема носіїв
    f.append(rect(x3 + 15, y_top + 175, col_w - 30, 80, fill="#ffffff", stroke="#ffedd5", rx=4))
    for px in [x3 + 35, x3 + 45, x3 + 55, x3 + 155, x3 + 165]:
        f.append(circle(px, y_top + 215, 8, fill="#ea580c", stroke="#c2410c"))
        f.append(text(px, y_top + 218.5, "e⁻", size=9, bold=True, color="#ffffff"))
    f.append(text(x3 + col_w / 2, y_top + 272, "Згустки носіїв (пакети заряду)", size=10, italic=True, color="#c2410c"))

    f.append(text(W / 2, H - 12, "Фактор Фано F показує відхилення шуму від стандарту Пуассона через кореляції носіїв", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fano-factor.svg'), W, H, "\n".join(f))

# ── Фігура 4: Шум фотодетектора та еквівалентна схема ──────────────────────
def fig_photodiode_noise_sources():
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 26, "Джерела шуму фотодетектора: фотострум, темновий струм та навантаження", size=16, bold=True, color=INK))

    # Схема фотодіода
    f.append(rect(40, 50, 680, 220, fill="#f8fafc", stroke="#cbd5e1", rx=6))

    # Фотодіод
    f.append(rect(70, 90, 110, 140, fill="#eff6ff", stroke="#2563eb", rx=4))
    f.append(text(125, 115, "p-n Фотодіод", size=12, bold=True, color="#1e40af"))
    f.append(arrow(45, 145, 70, 145, color="#eab308", sw=2.5))
    f.append(arrow(45, 165, 70, 165, color="#eab308", sw=2.5))
    f.append(text(40, 130, "hν", size=12, bold=True, color="#ca8a04"))

    f.append(text(125, 160, "I_ph (фотострум)", size=10, bold=True, color="#2563eb"))
    f.append(text(125, 185, "I_dark (темновий)", size=10, bold=True, color="#475569"))

    # Джерело дробового шуму
    f.append(circle(260, 160, 28, fill="#ffffff", stroke="#dc2626", sw=2))
    f.append(text(260, 155, "i_shot", size=11, bold=True, color="#dc2626"))
    f.append(text(260, 172, "2q(I_ph+I_d)Δf", size=9, color="#dc2626"))

    # Резистор R_L
    f.append(rect(380, 135, 50, 50, fill="#ffffff", stroke="#059669", sw=2))
    f.append(text(405, 162, "R_L", size=12, bold=True, color="#059669"))

    f.append(circle(480, 160, 28, fill="#ffffff", stroke="#059669", sw=2))
    f.append(text(480, 155, "i_thermal", size=10, bold=True, color="#059669"))
    f.append(text(480, 172, "4k_BTΔf/R_L", size=9, color="#059669"))

    # Підсилювач
    f.append(path_svg("M 560 120 L 630 160 L 560 200 Z", fill="#f1f5f9", stroke="#1e293b", sw=2))
    f.append(text(585, 163, "TIA", size=11, bold=True, color="#1e293b"))
    f.append(arrow(630, 160, 680, 160, color=INK, sw=2))
    f.append(text(660, 145, "V_out", size=12, bold=True, color=INK))

    f.append(line(180, 160, 232, 160, color=INK, sw=1.5))
    f.append(line(288, 160, 380, 160, color=INK, sw=1.5))
    f.append(line(430, 160, 452, 160, color=INK, sw=1.5))
    f.append(line(508, 160, 560, 160, color=INK, sw=1.5))

    # Порівняльна таблиця
    f.append(rect(40, 285, 330, 115, fill="#eff6ff", stroke="#bfdbfe", rx=6))
    f.append(text(205, 305, "Дробово-шумовий предел (Shot-Noise Limit)", size=12, bold=True, color="#1e40af"))
    f.append(text(205, 325, "I_ph великий (висока інтенсивність світла)", size=10, color=INK))
    f.append(text(205, 345, "SNR ≈ I_ph / (2 q Δf)^0.5 = (N_photons)^0.5", size=11, bold=True, color="#1d4ed8"))
    f.append(text(205, 368, "Квантова границя чутливості детектора", size=10, italic=True, color="#1e40af"))

    f.append(rect(390, 285, 330, 115, fill="#ecfdf5", stroke="#a7f3d0", rx=6))
    f.append(text(555, 305, "Теплово-шумовий предел (Thermal-Noise Limit)", size=12, bold=True, color="#065f46"))
    f.append(text(555, 325, "I_ph малий (слабкі оптичні сигнали)", size=10, color=INK))
    f.append(text(555, 345, "SNR ≈ I_ph / (4 k_B T Δf / R_L)^0.5", size=11, bold=True, color="#047857"))
    f.append(text(555, 368, "Обмежено опором R_L та температурою T", size=10, italic=True, color="#065f46"))

    f.append(text(W / 2, H - 12, "При високій потужності оптичного сигналу SNR визначається виключно дробовим шумом фотонів", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'photodiode-noise-sources.svg'), W, H, "\n".join(f))

if __name__ == "__main__":
    fig_shot_noise_mechanism()
    fig_spectral_density()
    fig_fano_factor()
    fig_photodiode_noise_sources()
    print("Фігури успішно згенеровано у ./img/")
