# -*- coding: utf-8 -*-
"""Фігури до теми «Спінові хвилі та магнони».
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

def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Структура спінової хвилі у феромагнітному ланцюжку ───────────────
def fig_spin_precession_chain():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 25, "Прецесія спінів у кристалічному ланцюжку при поширенні спінової хвилі", size=15, bold=True, color=INK))

    # Верхня панель: Основний стан (T = 0 K, усі спіни паралельні)
    y1_top = 50
    h1 = 140
    w_panel = 730
    x_panel = 25
    f.append(rect(x_panel, y1_top, w_panel, h1, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(x_panel + 15, y1_top + 22, "Основний феромагнітний стан (T = 0 K): усі спіни вишикувані вздовж осі Z", size=12, anchor="start", bold=True, color="#1e293b"))

    n_spins = 12
    x_start = 70
    dx = 58
    y_lattice1 = y1_top + 95

    # Вісь ланцюжка
    f.append(line(x_start - 20, y_lattice1, x_start + (n_spins - 1) * dx + 20, y_lattice1, color="#94a3b8", sw=1, dash="3,3"))

    for i in range(n_spins):
        cx = x_start + i * dx
        f.append(circle(cx, y_lattice1, 5, fill="#3b82f6", stroke="#1d4ed8", sw=1))
        # Стрілка спіна вгору
        f.append(arrow(cx, y_lattice1, cx, y_lattice1 - 42, color="#2563eb", sw=2))

    f.append(text(x_start + (n_spins - 1) * dx + 20, y_lattice1 - 20, "S_z = S", size=11, anchor="start", bold=True, color="#2563eb"))

    # Нижня панель: Спінова хвиля з хвильовим вектором q
    y2_top = 210
    h2 = 200
    f.append(rect(x_panel, y2_top, w_panel, h2, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    f.append(text(x_panel + 15, y2_top + 22, "Теплове або мікрохвильове збудження: спінова хвиля з хвильовим вектором q", size=12, anchor="start", bold=True, color="#0369a1"))

    y_lattice2 = y2_top + 120
    f.append(line(x_start - 20, y_lattice2, x_start + (n_spins - 1) * dx + 20, y_lattice2, color="#94a3b8", sw=1, dash="3,3"))

    # Малюємо синусоїду огинаючої поперечних компонент S_x
    pts_wave = []
    for px in range(int(x_start - 20), int(x_start + (n_spins - 1) * dx + 25)):
        phi = (px - x_start) / (dx * 6) * 2 * math.pi
        py = y_lattice2 - math.sin(phi) * 28
        pts_wave.append((px, py))
    d_wave = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_wave)
    f.append(path_svg(d_wave, stroke="#0284c7", sw=1.5, dash="4,3"))

    for i in range(n_spins):
        cx = x_start + i * dx
        phi = (i / 6.0) * math.pi  # фазовий зсув вздовж ланцюжка
        
        # Поперечні компоненти прецесії
        sx = math.sin(phi) * 28
        sz = math.cos(phi * 0.1) * 38  # невелике зменшення Z-компоненти
        
        # Еліпс прецесії для кожного вузла
        f.append(ellipse_svg(cx, y_lattice2 - 35, 12, 6, fill="none", stroke="#94a3b8", sw=1, dash="2,2"))
        f.append(circle(cx, y_lattice2, 5, fill="#0ea5e9", stroke="#0284c7", sw=1))
        
        # Стрілка відхиленого спіна
        tip_x = cx + sx * 0.6
        tip_y = y_lattice2 - sz
        f.append(arrow(cx, y_lattice2, tip_x, tip_y, color="#dc2626", sw=2))

    f.append(text(W / 2, y2_top + 182, "Сусідні спіни прецесують навколо осі Z із постійним фазовим зсувом Δφ = q · a", size=11, italic=True, color="#0369a1"))

    render(os.path.join(IMG_DIR, 'spin-precession-chain.svg'), W, H, "\n".join(f))

# ── Фігура 2: Дисперсійні співвідношення для феромагнетиків та антиферомагнетиків ─
def fig_spin_wave_dispersion():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 25, "Дисперсійні співвідношення спінових хвиль ħω(k)", size=15, bold=True, color=INK))

    x_zero = 380
    x_min = 90
    x_max = 670
    y_bot = 350
    y_top = 65

    # Оси
    f.append(arrow(x_min - 20, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "k", size=13, bold=True, italic=True, color=INK))

    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero + 15, y_top - 10, "ħω", size=13, bold=True, italic=True, color=INK))

    # Межі зони Бріллюена -pi/a та +pi/a
    x_bz_left = x_zero - 220
    x_bz_right = x_zero + 220
    f.append(line(x_bz_left, y_top, x_bz_left, y_bot, color="#94a3b8", sw=1.5, dash="4,4"))
    f.append(line(x_bz_right, y_top, x_bz_right, y_bot, color="#94a3b8", sw=1.5, dash="4,4"))
    f.append(text(x_bz_left, y_bot + 20, "-π/a", size=12, bold=True, color=MUTED))
    f.append(text(x_bz_right, y_bot + 20, "+π/a", size=12, bold=True, color=MUTED))
    f.append(text(x_zero, y_bot + 20, "0", size=12, bold=True, color=INK))

    # 1. Феромагнетик: ħω = D*k^2 + g*mu_B*B (квадратичний закон при малих k)
    pts_ferro = []
    gap_ferro = 25  # анізотропна/зовнішня щілина
    for i in range(-220, 221, 4):
        k_norm = i / 220.0
        x = x_zero + i
        val = gap_ferro + (y_bot - y_top - gap_ferro - 30) * (0.5 * (1.0 - math.cos(k_norm * math.pi)))
        y = y_bot - val
        pts_ferro.append((x, y))

    d_ferro = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_ferro)
    f.append(path_svg(d_ferro, stroke="#2563eb", sw=3))

    # Позначка анізотропної щелини g*mu_B*H
    f.append(line(x_zero - 15, y_bot - gap_ferro, x_zero + 15, y_bot - gap_ferro, color="#2563eb", sw=1.5, dash="2,2"))
    f.append(text(x_zero + 140, y_bot - gap_ferro - 5, "Щілина анізотропії g·μ_B·B_0", size=10, color="#2563eb"))

    # 2. Антиферомагнетик: ħω = ħ*v*|k| (лінійний закон при малих k)
    pts_antiferro = []
    for i in range(-220, 221, 4):
        k_norm = i / 220.0
        x = x_zero + i
        val = (y_bot - y_top - 40) * math.sin(abs(k_norm) * math.pi / 2.0)
        y = y_bot - val
        pts_antiferro.append((x, y))

    d_antiferro = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_antiferro)
    f.append(path_svg(d_antiferro, stroke="#dc2626", sw=2.5, dash="6,3"))

    # Аннотації
    f.append(rect(x_zero + 40, y_top + 20, 220, 55, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=4))
    f.append(text(x_zero + 150, y_top + 38, "Феромагнетик: ħω ∝ k²", size=12, bold=True, color="#2563eb"))
    f.append(text(x_zero + 150, y_top + 58, "Квадратична акустична мода", size=10, color=MUTED))

    f.append(rect(x_min + 20, y_top + 20, 230, 55, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=4))
    f.append(text(x_min + 135, y_top + 38, "Антиферомагнетик: ħω ∝ |k|", size=12, bold=True, color="#dc2626"))
    f.append(text(x_min + 135, y_top + 58, "Лінійна спінова хвиля (фоноподібна)", size=10, color=MUTED))

    f.append(text(W / 2, H - 12, "Перша зона Бріллюена: у малій околиці k = 0 квазічастинки магнони поводяться по-різному", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-wave-dispersion.svg'), W, H, "\n".join(f))

# ── Фігура 3: Температурне зменшення намагніченості (Закон Блоха T^3/2) ───────
def fig_magnon_thermal_reduction():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 25, "Зменшення спонтанної намагніченості феромагнетика за законом Блоха T³/²", size=15, bold=True, color=INK))

    x_zero = 80
    x_max = 680
    y_top = 65
    y_bot = 330

    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 45, y_bot + 4, "T / T_C", size=12, bold=True, color=INK))

    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 30, y_top - 10, "M(T)/M_0", size=12, bold=True, color=INK))

    f.append(text(x_zero - 15, y_top + 10, "1.0", size=11, bold=True, color=INK))
    f.append(text(x_zero, y_bot + 18, "0 K", size=11, color=MUTED))

    # Пунктир T_C
    x_tc = x_zero + 0.8 * (x_max - x_zero)
    f.append(line(x_tc, y_top, x_tc, y_bot, color="#dc2626", sw=1.5, dash="4,4"))
    f.append(text(x_tc, y_bot + 18, "T_C", size=12, bold=True, color="#dc2626"))

    # 1. Закон Блоха M(T) = M0 * (1 - B * T^(3/2)) при низьких T
    pts_bloch = []
    for i in range(101):
        t_rel = (i / 100.0) * 0.8
        x = x_zero + t_rel * (x_max - x_zero)
        val = 1.0 - 0.45 * (t_rel**1.5)
        if t_rel > 0.6:
            val = (1.0 - (t_rel / 0.8)**2)**0.33
        y = y_bot - max(0.0, val) * (y_bot - y_top - 10)
        pts_bloch.append((x, y))

    d_bloch = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_bloch)
    f.append(path_svg(d_bloch, stroke="#2563eb", sw=3))

    # 2. Молекулярне поле Вейсса (класичне наближення)
    pts_weiss = []
    for i in range(101):
        t_rel = (i / 100.0) * 0.8
        x = x_zero + t_rel * (x_max - x_zero)
        val = 1.0 - 0.35 * t_rel - 0.5 * (t_rel**3)
        y = y_bot - max(0.0, val) * (y_bot - y_top - 10)
        pts_weiss.append((x, y))

    d_weiss = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_weiss)
    f.append(path_svg(d_weiss, stroke="#94a3b8", sw=2, dash="5,3"))

    # Картки пояснень
    f.append(rect(x_zero + 40, y_top + 130, 260, 60, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=5))
    f.append(text(x_zero + 170, y_top + 150, "Закон Блоха: ΔM ∝ T³/²", size=12, bold=True, color="#2563eb"))
    f.append(text(x_zero + 170, y_top + 172, "Збудження довгохвильових магнонів", size=10, color="#1e40af"))

    f.append(rect(x_zero + 280, y_top + 30, 250, 55, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=5))
    f.append(text(x_zero + 405, y_top + 48, "Класична теорія Вейсса (MFT)", size=11, bold=True, color="#64748b"))
    f.append(text(x_zero + 405, y_top + 68, "Помилково дає лінійний спад при T → 0", size=10, color=MUTED))

    f.append(text(W / 2, H - 12, "Кожен збуджений магнон зменшує макроскопічну намагніченість кристала строго на один квант ℏ", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'magnon-thermal-reduction.svg'), W, H, "\n".join(f))

# ── Фігура 4: Схема магнонного хвилеводу та магнонного кристала ───────────────
def fig_magnonic_crystal_waveguide():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 25, "Принцип дії магнонного хвилеводу та періодичного магнонного кристала", size=15, bold=True, color=INK))

    x_wg = 50
    y_wg = 130
    w_wg = 680
    h_wg = 65

    # Підкладка з монокристалу ГГГ (Gadolinium Gallium Garnet)
    f.append(rect(x_wg, y_wg + h_wg, w_wg, 35, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    f.append(text(x_wg + w_wg / 2, y_wg + h_wg + 22, "Підкладка: Гадоліній-Галієвий Гранат (GGG, Gd₃Ga₅O₁₂)", size=11, bold=True, color="#475569"))

    # Магнонна плівка YIG (Залізо-Ітрієвий Гранат)
    f.append(rect(x_wg, y_wg, w_wg, h_wg, fill="#dbeafe", stroke="#2563eb", sw=2, rx=3))
    f.append(text(x_wg + 80, y_wg + h_wg / 2, "Плівка YIG (Y₃Fe₅O₁₂)", size=12, bold=True, color="#1e40af"))

    # Періодична канавочна структура (Магнонний кристал)
    n_grooves = 7
    x_gr_start = 280
    d_gr = 32
    w_gr = 16
    h_gr = 22

    for i in range(n_grooves):
        gx = x_gr_start + i * d_gr
        f.append(rect(gx, y_wg, w_gr, h_gr, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=1))

    f.append(text(x_gr_start + (n_grooves * d_gr) / 2 - 8, y_wg - 18, "Магнонний кристал (Bragg-решітка)", size=11, bold=True, color="#2563eb"))
    f.append(arrow(x_gr_start + (n_grooves * d_gr) / 2 - 8, y_wg - 10, x_gr_start + (n_grooves * d_gr) / 2 - 8, y_wg + 5, color="#2563eb", sw=1.5))

    # Мікросмужкові антени (вхід і вихід)
    # Вхідна антена
    f.append(rect(x_wg + 120, y_wg - 35, 18, 35, fill="#f59e0b", stroke="#d97706", sw=1.5, rx=2))
    f.append(text(x_wg + 129, y_wg - 45, "Вхід ВЧ (RF in)", size=10, bold=True, color="#b45309"))

    # Вихідна антена
    f.append(rect(x_wg + w_wg - 120, y_wg - 35, 18, 35, fill="#10b981", stroke="#047857", sw=1.5, rx=2))
    f.append(text(x_wg + w_wg - 111, y_wg - 45, "Вихід ВЧ (RF out)", size=10, bold=True, color="#047857"))

    # Збудження хвилі від вхідної антени
    f.append(arrow(x_wg + 138, y_wg + h_wg / 2, x_gr_start - 10, y_wg + h_wg / 2, color="#dc2626", sw=2.5))
    f.append(text(x_wg + 200, y_wg + h_wg / 2 - 12, "Спінова хвиля", size=11, bold=True, color="#dc2626"))

    # Зовнішнє підмагнічувальне поле H_0
    f.append(rect(x_wg + 20, H - 75, 170, 45, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    f.append(arrow(x_wg + 35, H - 52, x_wg + 85, H - 52, color="#dc2626", sw=2))
    f.append(text(x_wg + 125, H - 52, "Поле H_0", size=11, bold=True, color="#b91c1c"))

    # Заборонена зона (Bandgap)
    f.append(rect(x_gr_start + 230, H - 75, 450, 45, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4))
    f.append(text(x_gr_start + 455, H - 52, "Заборонені частотні смуги (Magnonic Bandgaps) у спектрі поширення", size=10, bold=True, color="#334155"))

    render(os.path.join(IMG_DIR, 'magnonic-crystal-waveguide.svg'), W, H, "\n".join(f))

def main():
    fig_spin_precession_chain()
    fig_spin_wave_dispersion()
    fig_magnon_thermal_reduction()
    fig_magnonic_crystal_waveguide()
    print("Фігури для spin-wave успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
