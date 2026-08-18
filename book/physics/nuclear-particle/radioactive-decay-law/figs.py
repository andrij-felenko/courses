# -*- coding: utf-8 -*-
"""Фігури до теми «Закон радіоактивного розпаду та період напіврозпаду».
Запуск: python figs.py -> генерує SVG-файли у ./img/
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

# ── Фігура 1: Крива експоненціального розпаду та період напіврозпаду ────────
def fig_exponential_decay_curve():
    W, H = 760, 440
    f = []

    title = "Експоненціальний закон радіоактивного розпаду N(t) = N₀ · e⁻ˡᵃᵐᵇᵈᵃᵗ"
    f.append(text(W / 2, 28, title, size=16, bold=True, color=INK))

    x0, y0 = 100, 360  # Початок координат (t=0, N=0)
    xmax, ymax = 700, 70
    plot_w = xmax - x0
    plot_h = y0 - ymax

    # Осі координат
    f.append(arrow(x0 - 15, y0, xmax + 30, y0, color=INK, sw=1.8))
    f.append(text(xmax + 45, y0 + 5, "t", size=14, bold=True, italic=True, color=INK))
    f.append(arrow(x0, y0 + 15, x0, ymax - 20, color=INK, sw=1.8))
    f.append(text(x0 - 25, ymax - 15, "N(t)", size=14, bold=True, italic=True, color=INK))

    # Мітки часу t в одиницях T_1/2 (від 0 до 5 T_1/2)
    t_steps = [0, 1, 2, 3, 4, 5]
    t_labels = ["0", "T₁/₂", "2T₁/₂", "3T₁/₂", "4T₁/₂", "5T₁/₂"]
    dx_step = plot_w / 5.2

    # Рівні N / N0
    n_levels = [1.0, 0.5, 0.25, 0.125, 0.0625]
    n_labels = ["N₀", "N₀ / 2", "N₀ / 4", "N₀ / 8", "N₀ / 16"]

    # Сітка та пунктирні лінії для періодів напіврозпаду
    for k, t_val in enumerate(t_steps[:-1]):
        x_k = x0 + t_val * dx_step
        val_k = n_levels[k]
        y_k = y0 - val_k * plot_h

        # Вертикальний пунктир до осі t
        if t_val > 0:
            f.append(line(x_k, y0, x_k, y_k, color=MUTED, sw=1.2, dash="4,4"))
            f.append(text(x_k, y0 + 20, t_labels[k], size=12, bold=True, color=INK))

        # Горизонтальний пунктир до осі N
        f.append(line(x0, y_k, x_k, y_k, color=MUTED, sw=1.2, dash="4,4"))
        f.append(text(x0 - 35, y_k + 4, n_labels[k], size=11, bold=True, color="#1e40af"))

        # Маркер точки (x_k, y_k)
        f.append(circle(x_k, y_k, 4.5, fill="#2563eb", stroke="#1e40af", sw=1.5))

    f.append(text(x0, y0 + 20, "0", size=12, bold=True, color=INK))

    # Побудова експоненціальної кривої
    pts = []
    num_pts = 100
    lam = math.log(2.0)  # λ в одиницях 1/T_1/2
    for i in range(num_pts + 1):
        t_rel = (i / num_pts) * 5.2
        x = x0 + t_rel * dx_step
        y_val = math.exp(-lam * t_rel)
        y = y0 - y_val * plot_h
        pts.append((x, y))

    d_curve = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    f.append(path_svg(d_curve, stroke="#2563eb", sw=3))

    # Дотична лінія при t=0, що перетинає вісь t в точці t = τ = 1/λ ≈ 1.443 T_1/2
    tau_rel = 1.0 / lam
    x_tau = x0 + tau_rel * dx_step
    y_tau = y0
    f.append(line(x0, y0 - plot_h, x_tau, y_tau, color="#dc2626", sw=1.5, dash="6,3"))
    f.append(circle(x_tau, y0, 4, fill="#dc2626", stroke="#991b1b", sw=1.5))
    f.append(text(x_tau, y0 + 35, "τ = 1/λ ≈ 1.44 T₁/₂", size=11, bold=True, color="#dc2626"))

    # Пояснювальна рамка про відсоток залишку
    info_str = "Зменшення кількості ядер:\n• 1 T₁/₂ → 50%\n• 2 T₁/₂ → 25%\n• 3 T₁/₂ → 12.5%\n• 4 T₁/₂ → 6.25%"
    f.append(fitbox(480, 110, 190, 110, info_str, size=11, fill="#eff6ff", stroke="#2563eb", rx=6))

    # Пояснювальний підпис унизу
    f.append(text(W / 2, H - 12, "Дотична в точці t=0 перетинає вісь часу в точці середнього часу життя τ = 1/λ", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'exponential-decay-curve.svg'), W, H, "\n".join(f))

# ── Фігура 2: Ланцюг розпаду та тимчасова рівновага Mo-99 -> Tc-99m ────────
def fig_decay_chain_equilibrium():
    W, H = 760, 440
    f = []

    title = "Динаміка активності в ланцюгу розпаду ⁹⁹Mo → ⁹⁹ᵐTc (Тимчасова рівновага)"
    f.append(text(W / 2, 28, title, size=16, bold=True, color=INK))

    x0, y0 = 90, 360
    xmax, ymax = 700, 70
    plot_w = xmax - x0
    plot_h = y0 - ymax

    # Осі
    f.append(arrow(x0 - 15, y0, xmax + 30, y0, color=INK, sw=1.8))
    f.append(text(xmax + 40, y0 + 5, "t (год)", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x0, y0 + 15, x0, ymax - 20, color=INK, sw=1.8))
    f.append(text(x0 - 25, ymax - 15, "Активність A(t)", size=13, bold=True, italic=True, color=INK))

    # Періоди напіврозпаду: T_A = 66 год (Mo-99), T_B = 6 год (Tc-99m)
    # На часовому інтервалі 0 .. 120 годин
    t_max_hours = 120.0
    lam_A = math.log(2.0) / 66.0
    lam_B = math.log(2.0) / 6.0
    branching_ratio = 0.876  # Частка розпадів Mo-99, що дає Tc-99m

    pts_A = []
    pts_B = []
    num_pts = 120

    # Шукаємо максимум A_B
    t_peak = math.log(lam_B / lam_A) / (lam_B - lam_A)

    for i in range(num_pts + 1):
        t_h = (i / num_pts) * t_max_hours
        x = x0 + (t_h / t_max_hours) * plot_w

        # Активність материнського ядра A_A(t) = A0 * e^(-lam_A * t)
        act_A = math.exp(-lam_A * t_h)

        # Активність дочірнього ядра A_B(t) за рівнянням Бейтмана
        act_B = branching_ratio * (lam_B / (lam_B - lam_A)) * (math.exp(-lam_A * t_h) - math.exp(-lam_B * t_h))

        y_A = y0 - act_A * plot_h
        y_B = y0 - act_B * plot_h

        pts_A.append((x, y_A))
        pts_B.append((x, y_B))

    # Малюємо криві
    d_A = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_A)
    d_B = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_B)

    f.append(path_svg(d_A, stroke="#dc2626", sw=2.8))
    f.append(path_svg(d_B, stroke="#059669", sw=2.8))

    # Максимум активності дочірнього ядра
    x_peak = x0 + (t_peak / t_max_hours) * plot_w
    act_B_peak = branching_ratio * (lam_B / (lam_B - lam_A)) * (math.exp(-lam_A * t_peak) - math.exp(-lam_B * t_peak))
    y_peak = y0 - act_B_peak * plot_h

    f.append(line(x_peak, y0, x_peak, y_peak, color="#059669", sw=1.2, dash="3,3"))
    f.append(circle(x_peak, y_peak, 4.5, fill="#059669", stroke="#047857", sw=1.5))
    f.append(text(x_peak, y0 + 18, f"t_max ≈ {t_peak:.0f} год", size=11, bold=True, color="#059669"))

    # Позначення осі часу (0, 24, 48, 72, 96, 120 год)
    for h_val in [24, 48, 72, 96, 120]:
        x_h = x0 + (h_val / t_max_hours) * plot_w
        f.append(line(x_h, y0 - 4, x_h, y0 + 4, color=INK, sw=1.2))
        f.append(text(x_h, y0 + 18, f"{h_val}", size=11, color=MUTED))
    f.append(text(x0, y0 + 18, "0", size=11, color=MUTED))

    # Легенда
    f.append(line(460, 95, 495, 95, color="#dc2626", sw=3))
    f.append(text(505, 99, "Материнське ядро ⁹⁹Mo (T₁/₂ = 66 год)", size=11, bold=True, color="#dc2626", anchor="start"))

    f.append(line(460, 120, 495, 120, color="#059669", sw=3))
    f.append(text(505, 124, "Дочірнє ядро ⁹⁹ᵐTc (T₁/₂ = 6 год)", size=11, bold=True, color="#059669", anchor="start"))

    # Тимчасова рівновага
    f.append(fitbox(550, 185, 230, 65, "Тимчасова рівновага:\nA_Tc(t) / A_Mo(t) ≈ const\n(активності спадають паралельно)", size=10, fill="#ecfdf5", stroke="#059669", rx=6))

    f.append(text(W / 2, H - 12, "При T_материнське > T_дочірнє встановлюється тимчасова рівновага, коли активність дочірнього ядра пропорційна материнському", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'decay-chain-equilibrium.svg'), W, H, "\n".join(f))

# ── Фігура 3: Статистичні флуктуації та розподіл Пуассона ─────────────────
def fig_poisson_fluctuations():
    W, H = 760, 440
    f = []

    title = "Статистичні флуктуації кількості відліків (Розподіл Пуассона при <N> = 100)"
    f.append(text(W / 2, 28, title, size=16, bold=True, color=INK))

    x0, y0 = 90, 360
    xmax, ymax = 700, 80
    plot_w = xmax - x0
    plot_h = y0 - ymax

    # Осі
    f.append(arrow(x0 - 15, y0, xmax + 30, y0, color=INK, sw=1.8))
    f.append(text(xmax + 40, y0 + 5, "k (число розпадів)", size=12, bold=True, italic=True, color=INK))
    f.append(arrow(x0, y0 + 15, x0, ymax - 20, color=INK, sw=1.8))
    f.append(text(x0 - 25, ymax - 15, "P(k)", size=12, bold=True, italic=True, color=INK))

    # Діапазон k від 70 до 130 (середнє mu = 100, sigma = 10)
    mu = 100.0
    sigma = math.sqrt(mu)  # 10.0
    k_min, k_max = 70, 130

    # Побудова стовпчиків гістограми Пуассона (наближення Гаусса для великих N)
    num_bars = k_max - k_min + 1
    bar_w = plot_w / num_bars

    max_p = 1.0 / (sigma * math.sqrt(2.0 * math.pi))  # ~ 0.03989

    for k in range(k_min, k_max + 1):
        p_k = (1.0 / (sigma * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * ((k - mu) / sigma)**2)
        x_bar = x0 + (k - k_min) * bar_w
        h_bar = (p_k / max_p) * plot_h * 0.85
        y_bar = y0 - h_bar

        # Колір залежно від зони (всередині ±1σ, ±2σ чи за межами)
        if abs(k - mu) <= sigma:
            col_fill = "#dbeafe"  # Всередині ±1σ
            col_stroke = "#3b82f6"
        elif abs(k - mu) <= 2 * sigma:
            col_fill = "#fef3c7"  # Всередині ±2σ
            col_stroke = "#f59e0b"
        else:
            col_fill = "#fee2e2"
            col_stroke = "#ef4444"

        f.append(rect(x_bar, y_bar, bar_w - 1, h_bar, fill=col_fill, stroke=col_stroke, sw=0.8, rx=1))

    # Огинаюча лінія Гаусса
    pts_g = []
    for i in range(101):
        k_val = k_min + (i / 100.0) * (k_max - k_min)
        x_g = x0 + (k_val - k_min) * bar_w
        p_g = (1.0 / (sigma * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * ((k_val - mu) / sigma)**2)
        y_g = y0 - (p_g / max_p) * plot_h * 0.85
        pts_g.append((x_g, y_g))

    d_g = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_g)
    f.append(path_svg(d_g, stroke="#1e40af", sw=2.2))

    # Вертикальні лінії для μ, μ - σ, μ + σ
    x_mu = x0 + (mu - k_min) * bar_w
    f.append(line(x_mu, y0, x_mu, ymax + 20, color="#1e40af", sw=2, dash="4,4"))
    f.append(text(x_mu, y0 + 20, "μ = 100", size=12, bold=True, color="#1e40af"))

    x_minus_sigma = x0 + ((mu - sigma) - k_min) * bar_w
    x_plus_sigma = x0 + ((mu + sigma) - k_min) * bar_w

    f.append(line(x_minus_sigma, y0, x_minus_sigma, ymax + 50, color="#f59e0b", sw=1.5, dash="3,3"))
    f.append(text(x_minus_sigma, y0 + 20, "μ - σ (90)", size=11, bold=True, color="#f59e0b"))

    f.append(line(x_plus_sigma, y0, x_plus_sigma, ymax + 50, color="#f59e0b", sw=1.5, dash="3,3"))
    f.append(text(x_plus_sigma, y0 + 20, "μ + σ (110)", size=11, bold=True, color="#f59e0b"))

    # Пояснення теорії похибки 1/sqrt(N)
    err_info = "Параметри Пуассонівського розподілу:\n• Дисперсія: Var(N) = σ² = <N>\n• Стандартне відхилення: σ = √<N> = 10\n• Відносна похибка: σ / <N> = 1 / √<N> = 10%\n• Двостороння довірча зона 68.3%: 100 ± 10"
    f.append(fitbox(530, 135, 250, 100, err_info, size=10, fill="#f8fafc", stroke="#475569", rx=6))

    f.append(text(W / 2, H - 12, "При збільшенні кількості відліків N відносна статистична похибка спадає пропорційно 1/√N", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'poisson-fluctuations.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_exponential_decay_curve()
    fig_decay_chain_equilibrium()
    fig_poisson_fluctuations()
    print("Всі 3 фігури згенеровано у ./img/")
