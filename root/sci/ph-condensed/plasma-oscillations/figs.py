# -*- coding: utf-8 -*-
"""Фігури до теми «Плазмові коливання і плазмони».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
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

# ── Фігура 1: Зміщення електронного газу та повертальна сила ─────────────────
def fig_plasma_displacement():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 28, "Колективне зміщення електронного газу відносно іонного остова", size=16, bold=True, color=INK))

    # Рамка фону для плазми
    x_start, y_start = 80, 70
    width, height = 600, 220
    
    f.append(rect(x_start, y_start, width, height, fill="#f8fafc", stroke=MUTED, rx=8, sw=1.5))
    
    # 1. Позитивний іонний остов (нерухомий)
    f.append(text(x_start + 20, y_start + 25, "Нерухомий іонний остов (+n_0)", size=12, bold=True, color=POS, anchor="start"))
    for row in range(3):
        for col in range(8):
            cx = x_start + 60 + col * 70
            cy = y_start + 65 + row * 60
            f.append(circle(cx, cy, 16, fill="#fef2f2", stroke=POS, sw=2))
            f.append(text(cx, cy + 5, "+", size=18, bold=True, color=POS))

    # 2. Зміщений електронний хмарка (зміщення x вправо)
    dx = 30
    f.append(text(x_start + width - 20, y_start + 25, "Зміщений електронний газ (-e)", size=12, bold=True, color=NEG, anchor="end"))
    
    # Область нескомпенсованого позитивного заряду ліворуч
    f.append(rect(x_start + 20, y_start + 40, dx, height - 55, fill="rgba(220, 38, 38, 0.15)", stroke=POS, sw=1.5, rx=0))
    f.append(text(x_start + 20 + dx / 2, y_start + height / 2 + 10, "+σ", size=13, bold=True, color=POS))

    # Область нескомпенсованого негативного заряду праворуч
    f.append(rect(x_start + width - 20 - dx, y_start + 40, dx, height - 55, fill="rgba(36, 87, 214, 0.15)", stroke=NEG, sw=1.5, rx=0))
    f.append(text(x_start + width - 20 - dx / 2, y_start + height / 2 + 10, "-σ", size=13, bold=True, color=NEG))

    # Вектор електричного поля E всередині
    y_e = y_start + height - 35
    f.append(arrow(x_start + width - 70, y_e, x_start + 70, y_e, color="#d97706", sw=2.5))
    f.append(text(W / 2, y_e - 10, "Внутрішнє електричне поле E = (n_0 · e / ε_0) · x", size=12, bold=True, color="#d97706"))

    # Повертальна сила F
    y_f = y_start + 45
    f.append(arrow(x_start + width / 2 + 60, y_f, x_start + width / 2 - 60, y_f, color=NEG, sw=2.5))
    f.append(text(W / 2, y_f - 10, "Повертальна сила F = -e · E = -m · ω_p² · x", size=12, bold=True, color=NEG))

    # Позначення зміщення x
    f.append(arrow(x_start + width / 2 - 40, y_start + height + 25, x_start + width / 2 - 40 + dx, y_start + height + 25, color=INK, sw=1.5))
    f.append(text(x_start + width / 2 - 40 + dx / 2, y_start + height + 42, "зміщення x", size=12, bold=True, color=INK))

    f.append(text(W / 2, H - 12, "Розділення зарядів викликає електричне поле, що повертає електрони в стан рівноваги з частотою ω_p", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig1-plasma-displacement.svg'), W, H, "\n".join(f))

# ── Фігура 2: Дійсна частина ε(ω) та коефіцієнт відбивання R(ω) ──────────────
def fig_drude_reflectivity():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28, "Диелектрична проникність Re(ε) та відбивання R(ω) за моделлю Друде", size=16, bold=True, color=INK))

    x0, y0 = 90, 330
    xw, yh = 580, 240
    x_wp = x0 + xw * 0.55

    # Області: металеве відбивання vs оптична прозорість
    f.append(rect(x0, y0 - yh, x_wp - x0, yh, fill="#f0f9ff", stroke="none"))
    f.append(rect(x_wp, y0 - yh, x0 + xw - x_wp, yh, fill="#fffbebe6", stroke="none"))

    f.append(text((x0 + x_wp) / 2, y0 - yh + 20, "Металеве відбивання (Re(ε) < 0, R ≈ 1)", size=12, bold=True, color="#0369a1"))
    f.append(text((x_wp + x0 + xw) / 2, y0 - yh + 20, "Прозорість металу (Re(ε) > 0, R → 0)", size=12, bold=True, color="#b45309"))

    # Вісь ω / ω_p
    f.append(arrow(x0, y0, x0 + xw + 30, y0, color=INK, sw=1.5))
    f.append(text(x0 + xw + 45, y0 + 4, "ω / ω_p", size=13, bold=True, italic=True, color=INK))

    # Вісь значень
    f.append(arrow(x0, y0, x0, y0 - yh - 15, color=INK, sw=1.5))
    f.append(text(x0 - 25, y0 - yh - 10, "Re(ε), R", size=12, bold=True, color=INK))

    # Пунктирна лінія ω = ω_p
    f.append(path_svg(f"M {x_wp} {y0 - yh} L {x_wp} {y0}", stroke="#dc2626", sw=2, dash="4,4"))
    f.append(text(x_wp, y0 + 20, "ω = ω_p", size=12, bold=True, color="#dc2626"))

    # Горизонтальна лінія ε = 0 та R = 1
    y_eps0 = y0 - yh * 0.4
    y_r1 = y0 - yh * 0.85
    f.append(path_svg(f"M {x0} {y_eps0} L {x0 + xw} {y_eps0}", stroke=MUTED, sw=1, dash="2,2"))
    f.append(text(x0 - 20, y_eps0 + 4, "ε = 0", size=11, color=MUTED))

    f.append(path_svg(f"M {x0} {y_r1} L {x0 + xw} {y_r1}", stroke=MUTED, sw=1, dash="2,2"))
    f.append(text(x0 - 20, y_r1 + 4, "R = 1", size=11, color=MUTED))

    # Графік Re(ε) = 1 - (ω_p/ω)²
    pts_eps = []
    for i in range(1, 101):
        w_ratio = 0.2 + (i / 100.0) * 1.6
        x = x0 + ((w_ratio - 0.2) / 1.6) * xw
        eps = 1.0 - 1.0 / (w_ratio**2 + 0.01)
        # Масштабуємо eps: eps=0 в y_eps0, eps=1 у y_r1
        y = y_eps0 - eps * (y_eps0 - y_r1)
        y = max(y0 - yh + 5, min(y0 - 5, y))
        pts_eps.append((x, y))

    d_eps = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_eps)
    f.append(path_svg(d_eps, stroke="#2563eb", sw=3))
    f.append(text(x0 + xw * 0.75, y_eps0 - 35, "Re(ε(ω)) = 1 - ω_p² / ω²", size=12, bold=True, color="#2563eb"))

    # Графік R(ω)
    pts_r = []
    for i in range(0, 101):
        w_ratio = 0.2 + (i / 100.0) * 1.6
        x = x0 + ((w_ratio - 0.2) / 1.6) * xw
        if w_ratio <= 1.0:
            val_r = 1.0 - 0.05 * (w_ratio**2)
        else:
            n_val = math.sqrt(1.0 - 1.0 / (w_ratio**2))
            val_r = ((n_val - 1.0) / (n_val + 1.0))**2
        y = y0 - val_r * (y0 - y_r1)
        pts_r.append((x, y))

    d_r = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_r)
    f.append(path_svg(d_r, stroke="#059669", sw=3, dash="6,3"))
    f.append(text(x0 + xw * 0.2, y_r1 + 25, "Коефіцієнт відбивання R(ω)", size=12, bold=True, color="#059669"))

    f.append(text(W / 2, H - 12, "При ω < ω_p метал дзеркально відбиває світло (R ≈ 1); при ω > ω_p стає прозорим (R → 0)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig2-drude-reflectivity.svg'), W, H, "\n".join(f))

# ── Фігура 3: Дисперсійна діаграма поверхневих плазмонів (SPP) ───────────────
def fig_spp_dispersion():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Дисперсійна крива поверхневих плазмон-поляритонів (SPP)", size=16, bold=True, color=INK))

    x0, y0 = 90, 350
    xw, yh = 580, 270

    # Вісь k (хвильове число)
    f.append(arrow(x0, y0, x0 + xw + 30, y0, color=INK, sw=1.5))
    f.append(text(x0 + xw + 40, y0 + 4, "k", size=13, bold=True, italic=True, color=INK))

    # Вісь ω (частота)
    f.append(arrow(x0, y0, x0, y0 - yh - 15, color=INK, sw=1.5))
    f.append(text(x0 - 25, y0 - yh - 10, "ω", size=13, bold=True, color=INK))

    # Асимптоти та рівні
    y_wp = y0 - yh * 0.85
    y_wsp = y0 - yh * 0.85 / math.sqrt(2.0)  # ω_sp = ω_p / √2

    f.append(path_svg(f"M {x0} {y_wp} L {x0 + xw} {y_wp}", stroke="#dc2626", sw=1.5, dash="4,4"))
    f.append(text(x0 - 15, y_wp + 4, "ω_p", size=12, bold=True, color="#dc2626"))
    f.append(text(x0 + xw - 80, y_wp - 8, "Об'ємний плазмон", size=11, color="#dc2626"))

    f.append(path_svg(f"M {x0} {y_wsp} L {x0 + xw} {y_wsp}", stroke="#d97706", sw=1.5, dash="4,4"))
    f.append(text(x0 - 25, y_wsp + 4, "ω_sp = ω_p/√2", size=11, bold=True, color="#d97706"))

    # Світлова лінія в діелектрику (ω = c·k / √ε_d)
    x_light_end = x0 + xw * 0.55
    y_light_end = y0 - yh * 0.95
    f.append(path_svg(f"M {x0} {y0} L {x_light_end} {y_light_end}", stroke=MUTED, sw=2))
    f.append(text(x_light_end - 40, y_light_end - 10, "Світлова лінія (ω = c·k)", size=11, bold=True, color=MUTED))

    # Світлова лінія у призмі (більший показник заломлення, похиліша)
    x_prism_end = x0 + xw * 0.35
    f.append(path_svg(f"M {x0} {y0} L {x_prism_end} {y_light_end}", stroke="#7c3aed", sw=2, dash="5,3"))
    f.append(text(x_prism_end + 15, y_light_end + 30, "Світло у призмі (n > 1)", size=11, bold=True, color="#7c3aed"))

    # Крива SPP: k_spp = (ω/c) * sqrt(ε_m*ε_d / (ε_m+ε_d))
    pts_spp = []
    for i in range(1, 101):
        w_ratio = (i / 100.0) * (0.85 / math.sqrt(2.0)) * 0.96
        y = y0 - w_ratio * yh
        # k_spp прямує до нескінченності при ω -> ω_sp
        eps_m = 1.0 - 1.0 / (w_ratio * math.sqrt(2.0) * 1.15)**2 if w_ratio > 0 else -10
        if eps_m < -1.0:
            k_val = w_ratio * math.sqrt(eps_m / (eps_m + 1.0))
        else:
            k_val = w_ratio * 3.0
        x = x0 + k_val * xw * 0.6
        if x <= x0 + xw:
            pts_spp.append((x, y))

    d_spp = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_spp)
    f.append(path_svg(d_spp, stroke="#2563eb", sw=3.5))
    f.append(text(x0 + xw * 0.7, y_wsp + 25, "Дисперсія SPP k_spp(ω)", size=12, bold=True, color="#2563eb"))

    # Позначення розсогласування (незбіг хвильових векторів Δk)
    y_mismatch = y0 - yh * 0.45
    x_light = x0 + (y0 - y_mismatch) / (y0 - y_light_end) * (x_light_end - x0)
    x_spp = x0 + xw * 0.32
    f.append(arrow(x_light, y_mismatch, x_spp, y_mismatch, color="#dc2626", sw=2))
    f.append(text((x_light + x_spp) / 2, y_mismatch - 8, "Незбіг Δk", size=11, bold=True, color="#dc2626"))

    f.append(text(W / 2, H - 12, "Крива SPP лежить праворуч від світлової лінії; для збудження потрібна призма або дифракційна ґратка", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig3-spp-dispersion.svg'), W, H, "\n".join(f))

# ── Фігура 4: Спектр втрат енергії електронів (EELS) ─────────────────────────
def fig_eels_spectrum():
    W, H = 760, 390
    f = []

    f.append(text(W / 2, 28, "Спектр втрат енергії електронів (EELS) у тонкій фользі алюмінію", size=16, bold=True, color=INK))

    x0, y0 = 90, 320
    xw, yh = 580, 230

    # Вісь енергії втрат ΔE (eV)
    f.append(arrow(x0, y0, x0 + xw + 30, y0, color=INK, sw=1.5))
    f.append(text(x0 + xw + 45, y0 + 4, "ΔE (eV)", size=13, bold=True, color=INK))

    # Вісь інтенсивності I
    f.append(arrow(x0, y0, x0, y0 - yh - 15, color=INK, sw=1.5))
    f.append(text(x0 - 25, y0 - yh - 10, "Інтенсивність I", size=12, bold=True, color=INK))

    # Піки: ZLP (0 eV), Surface plasmon (7 eV), Bulk plasmon (15 eV), 2x Bulk (30 eV)
    def ev_to_x(ev):
        return x0 + (ev / 35.0) * xw

    # Пік 1: ZLP (0 eV) - пружне розсіяння
    x_zlp = ev_to_x(0)
    f.append(path_svg(f"M {x_zlp} {y0} L {x_zlp} {y0 - yh * 0.95} L {ev_to_x(2.5)} {y0}", fill="rgba(37, 99, 235, 0.2)", stroke="#2563eb", sw=2))
    f.append(text(ev_to_x(2), y0 - yh * 0.75, "Пік пружного розсіяння (ZLP, 0 eV)", size=11, bold=True, color="#2563eb", anchor="start"))

    # Пік 2: Поверхневий плазмон (7 eV)
    x_sp = ev_to_x(7)
    y_sp = y0 - yh * 0.35
    f.append(path_svg(f"M {ev_to_x(5)} {y0} Q {x_sp} {y_sp - 30} {ev_to_x(9)} {y0}", fill="rgba(217, 119, 6, 0.2)", stroke="#d97706", sw=2))
    f.append(text(x_sp, y_sp - 40, "Поверхневий плазмон\nℏω_sp ≈ 7 eV", size=11, bold=True, color="#d97706"))

    # Пік 3: Об'ємний плазмон (15 eV)
    x_bp = ev_to_x(15)
    y_bp = y0 - yh * 0.75
    f.append(path_svg(f"M {ev_to_x(12)} {y0} Q {x_bp} {y_bp - 40} {ev_to_x(18)} {y0}", fill="rgba(220, 38, 38, 0.25)", stroke="#dc2626", sw=2.5))
    f.append(text(x_bp, y_bp - 50, "Об'ємний плазмон (Al)\nℏω_p ≈ 15 eV", size=12, bold=True, color="#dc2626"))

    # Пік 4: Подвійний об'ємний плазмон (30 eV)
    x_2bp = ev_to_x(30)
    y_2bp = y0 - yh * 0.25
    f.append(path_svg(f"M {ev_to_x(27)} {y0} Q {x_2bp} {y_2bp - 20} {ev_to_x(33)} {y0}", fill="rgba(124, 58, 237, 0.2)", stroke="#7c3aed", sw=2))
    f.append(text(x_2bp, y_2bp - 30, "Кратно-2 плазмон\n2·ℏω_p ≈ 30 eV", size=11, bold=True, color="#7c3aed"))

    f.append(text(W / 2, H - 12, "Електрони втрачають енергію дискретними порціями ℏω_p при квантовому збудженні плазмонів у металі", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig4-eels-spectrum.svg'), W, H, "\n".join(f))

if __name__ == "__main__":
    fig_plasma_displacement()
    fig_drude_reflectivity()
    fig_spp_dispersion()
    fig_eels_spectrum()
    print("Всі фігури успішно згенеровано у img/")
