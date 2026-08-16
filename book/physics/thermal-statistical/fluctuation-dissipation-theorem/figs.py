# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема флуктуації-дисипації».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# Кольорова палітра для теми
C_FLUC = "#e67e22"    # Флуктуації / шум (оранжевий / тепличний)
C_DISS = "#2980b9"    # Дисипація / відгук (синій / в'язкий)
C_EQUIL = "#27ae60"   # Рівновага / середовище (зелений)
C_QUANT = "#8e44ad"   # Квантові ефекти (фіолетовий)
C_AXIS = "#7f8c8d"    # Осі та другорядні лінії


def fig_fdt_bridge():
    """Фігура 1: Двосторонній місток між термодинамічним шумом та дисипацією."""
    W, H = 860, 340
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    frags.append(text(W / 2, 30, "Теорема флуктуації-дисипації як двосторонній місток", size=16, bold=True))

    # Лівий блок: Спонтанні флуктуації
    bx1 = fitbox(40, 70, 240, 210,
                 "Спонтанні флуктуації\n\n• Тепловий рух (k_B T)\n• Шум Найквіста U_ш\n• Броунівська тряска\n\nХаотичні поштовхи",
                 size=13, fill="#fef5e7", stroke=C_FLUC, sw=2.0, color=INK)
    frags.append(bx1)

    # Правий блок: Дисипативний відгук
    bx2 = fitbox(580, 70, 240, 210,
                 "Дисипативний відгук\n\n• В'язке тертя γ\n• Електричний опір R\n• Уявна сприйнятливість χ''\n\nВтрати енергії в тепло",
                 size=13, fill="#ebf5fb", stroke=C_DISS, sw=2.0, color=INK)
    frags.append(bx2)

    # Центральний блок: Термодинамічна середа / Рівновага
    bx_center = fitbox(315, 105, 230, 140,
                       "Тепловий батут (T)\n\nФДТ: S_A(ω) = (2 k_B T / ω) χ''(ω)\n\nМікроскопічний баланс",
                       size=12, fill="#eafaf1", stroke=C_EQUIL, sw=2.2, color=INK, bold=True)
    frags.append(bx_center)

    # Стрілки-містки між блоками
    frags.append(arrow(280, 145, 315, 145, color=C_FLUC, sw=2.5))
    frags.append(arrow(315, 205, 280, 205, color=C_FLUC, sw=2.5))

    frags.append(arrow(545, 145, 580, 145, color=C_DISS, sw=2.5))
    frags.append(arrow(580, 205, 545, 205, color=C_DISS, sw=2.5))

    # Підписи під стрілками
    frags.append(text(W / 2, 290, "Єдине мікроскопічне джерело: теплові зіткнення з термостатом", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, "fdt-bridge.svg"), W, H, *frags)


def fig_langevin_balance():
    """Фігура 2: Баланс сил у рівнянні Ланжевена."""
    W, H = 820, 320
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    frags.append(text(W / 2, 28, "Баланс сил у рівнянні Ланжевена: m (dv/dt) = -γ v + ξ(t)", size=16, bold=True))

    # Центральна частина: Частинка
    cx, cy = 410, 160
    frags.append(circle(cx, cy, 38, fill="#fdedec", stroke=C_FLUC, sw=2.5))
    frags.append(text(cx, cy - 6, "Частинка", size=13, bold=True, color=INK))
    frags.append(text(cx, cy + 12, "маса m, швидкість v", size=11, color=MUTED))

    # В'язке гальмування (Дисипація - ліворуч)
    frags.append(arrow(cx - 38, cy, cx - 180, cy, color=C_DISS, sw=3.0))
    frags.append(textbox(cx - 240, cy, "В'язке гальмування\nF_дисипації = -γ·v\n(Вивід енергії)",
                         size=12, fill="#ebf5fb", stroke=C_DISS, sw=1.5)[0])

    # Випадкові поштовхи (Флуктуації - праворуч)
    frags.append(arrow(cx + 38, cy, cx + 180, cy, color=C_FLUC, sw=3.0))
    frags.append(textbox(cx + 240, cy, "Тепловий шум\nF_флуктуації = ξ(t)\n(Вхід енергії)",
                         size=12, fill="#fef5e7", stroke=C_FLUC, sw=1.5)[0])

    # Нижня узгоджувальна умова
    frags.append(line(160, cy + 75, 660, cy + 75, color=C_AXIS, sw=1.2, dash="4,4"))
    frags.append(textbox(cx, cy + 95, "Умова термодинамічної рівноваги:\n⟨ξ(t) ξ(t')⟩ = 2 · γ · k_B · T · δ(t - t')",
                         size=13, fill="#eafaf1", stroke=C_EQUIL, sw=2.0, bold=True, color=INK)[0])

    render(os.path.join(IMG_DIR, "langevin-balance.svg"), W, H, *frags)


def fig_susceptibility_spectrum():
    """Фігура 3: Комплексна сприйнятливість χ(ω) = χ'(ω) + i χ''(ω) та спектр шуму S(ω)."""
    W, H = 840, 360
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    frags.append(text(W / 2, 28, "Комплексний відгук χ(ω) та спектральна густина шуму S(ω)", size=16, bold=True))

    # Вісь частот ω
    ox, oy = 90, 280
    axis_w = 680
    frags.append(line(ox, oy, ox + axis_w, oy, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox + axis_w - 10, oy, ox + axis_w + 15, oy, color=C_AXIS, sw=1.8))
    frags.append(text(ox + axis_w + 25, oy + 4, "Частота ω", size=13, bold=True, color=C_AXIS, anchor="start"))

    # Вісь амплітуд Y
    frags.append(line(ox, oy, ox, 60, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox, 70, ox, 45, color=C_AXIS, sw=1.8))
    frags.append(text(ox - 10, 50, "Амплітуда відгуку / шуму", size=12, bold=True, color=C_AXIS, anchor="end"))

    # Резонансна частота ω₀
    w0_x = ox + 320
    frags.append(line(w0_x, oy, w0_x, 70, color="#bdc3c7", sw=1.2, dash="3,4"))
    frags.append(text(w0_x, oy + 22, "ω₀ (резонанс)", size=12, bold=True, color=INK))

    pts_chi_pp = []
    pts_noise = []
    pts_chi_p = []

    for px in range(0, 600, 5):
        w_val = (px - 230) / 60.0    # відносне відхилення від резонансу
        gamma = 0.8
        denom = w_val**2 + gamma**2
        chi_pp = (gamma / denom) * 120.0
        chi_p = (-w_val / denom) * 70.0

        x_curr = ox + 90 + px
        y_chi_pp = oy - chi_pp
        y_chi_p = oy - chi_p - 40
        y_noise = oy - chi_pp * 0.95

        pts_chi_pp.append((x_curr, y_chi_pp))
        pts_chi_p.append((x_curr, y_chi_p))
        pts_noise.append((x_curr, y_noise))

    # Крива χ''(ω) — синя (дисипація)
    d_chi_pp = "M " + " L ".join("%.1f,%.1f" % p for p in pts_chi_pp)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_chi_pp, C_DISS))

    # Крива S(ω) — оранжева пунктирна (тепловий шум)
    d_noise = "M " + " L ".join("%.1f,%.1f" % p for p in pts_noise)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (d_noise, C_FLUC))

    # Крива χ'(ω) — сіра / дійсна
    d_chi_p = "M " + " L ".join("%.1f,%.1f" % p for p in pts_chi_p)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_chi_p, C_AXIS))

    # Легенда
    frags.append(textbox(640, 100, "— χ''(ω) Уявна сприйнятливість (Дисипація)\n- - S_A(ω) Спектральна густина шуму\n— χ'(ω) Дійсна сприйнятливість (Пружність)",
                         size=11.5, fill="#ffffff", stroke="#d6dbdf", pad=8)[0])

    frags.append(text(w0_x, oy - 145, "Пік поглинання = Пік шуму", size=12, color=C_DISS, bold=True))

    render(os.path.join(IMG_DIR, "susceptibility-spectrum.svg"), W, H, *frags)


def fig_quantum_classical_fdt():
    """Фігура 4: Квантова та класична межі ФДТ."""
    W, H = 840, 340
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    frags.append(text(W / 2, 28, "Перехід від класичної до квантової теореми флуктуації-дисипації", size=16, bold=True))

    ox, oy = 90, 270
    axis_w = 680
    frags.append(line(ox, oy, ox + axis_w, oy, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox + axis_w - 10, oy, ox + axis_w + 15, oy, color=C_AXIS, sw=1.8))
    frags.append(text(ox + axis_w + 25, oy + 4, "Частота ω (або ℏω / k_B T)", size=12, bold=True, color=C_AXIS, anchor="start"))

    frags.append(line(ox, oy, ox, 60, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox, 70, ox, 45, color=C_AXIS, sw=1.8))
    frags.append(text(ox - 10, 50, "Ефективна шумова енергія E_ефф", size=12, bold=True, color=C_AXIS, anchor="end"))

    # Класична лінія E_eff = k_B T (горизонтальна)
    y_classical = oy - 90
    frags.append(line(ox, y_classical, ox + axis_w - 40, y_classical, color=C_FLUC, sw=2.2, dash="6,4"))
    frags.append(text(ox + 460, y_classical - 12, "Класична межа: E_ефф = k_B T (Рівномірний розподіл)", size=12, color=C_FLUC, bold=True))

    # Квантова крива E_eff = (ħω / 2) coth(ħω / 2kBT)
    pts_quantum = []
    for px in range(0, 620, 8):
        x_val = px / 100.0  # відношення ℏω / k_B T
        if x_val < 0.05:
            eff = 1.0
        else:
            eff = (x_val / 2.0) / math.tanh(x_val / 2.0)
        y_curr = oy - 90 * eff
        pts_quantum.append((ox + px, y_curr))

    d_quant = "M " + " L ".join("%.1f,%.1f" % p for p in pts_quantum)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d_quant, C_QUANT))

    # Нульові квантові коливання (асимптота ℏω/2)
    frags.append(text(ox + 520, oy - 200, "Квантова межа: ℏω / 2\n(Нульові коливання вакууму)", size=12, color=C_QUANT, bold=True))

    # Зона кросоверу
    frags.append(line(ox + 200, oy, ox + 200, oy - 140, color="#bdc3c7", sw=1.2, dash="3,3"))
    frags.append(textbox(ox + 200, oy + 25, "Кросовер: ℏω ≈ k_B T", size=11.5, fill="#f4ecf7", stroke=C_QUANT, pad=6)[0])

    render(os.path.join(IMG_DIR, "quantum-classical-fdt.svg"), W, H, *frags)


if __name__ == '__main__':
    print("Генерація SVG-фігур для теореми флуктуації-дисипації...")
    fig_fdt_bridge()
    fig_langevin_balance()
    fig_susceptibility_spectrum()
    fig_quantum_classical_fdt()
    print("Генерацію завершено у теці:", IMG_DIR)
