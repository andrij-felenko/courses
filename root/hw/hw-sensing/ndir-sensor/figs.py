# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми NDIR-давач газу (ndir-sensor)."""
import math
import os
import sys

# Підключаємо спільний svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_co2_spectrum():
    """Фігура 1: Спектр поглинання газів у середньому ІЧ та вікна фільтрів NDIR."""
    w, h = 880, 500
    frags = []

    # Верхній блок з виносними картками для фільтрів (поза сіткою графіка)
    # Активний канал CO2: 4.26 мкм
    box_act, _, _ = textbox(600, 42, "Активний канал CO₂: λ = 4.26 мкм (смуга ν₃)\nВузькосмуговий фільтр (FWHM ~ 180 нм)", size=12, fill="#fdecea", stroke=POS, bold=True)
    frags.append(box_act)

    # Опорний канал: 3.91 мкм
    box_ref, _, _ = textbox(260, 42, "Опорний канал: λ = 3.91 мкм (чисте тло)\nВузькосмуговий фільтр (FWHM ~ 100 нм)", size=12, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(box_ref)

    # Фон графіка
    gx, gy, gw, gh = 80, 95, 740, 310
    frags.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=4))

    # X: Довжина хвилі 2.0 - 6.0 мкм (4 мкм діапазон)
    def x_of(wl):
        return gx + (wl - 2.0) / 4.0 * gw

    # Y: Поглинання 0 - 100%
    def y_of(abs_pct):
        return gy + gh - (abs_pct / 100.0) * gh

    # Смуги пропускання оптичних фільтрів NDIR (підсвічування колонок на графіку)
    x_ref_l = x_of(3.86)
    x_ref_r = x_of(3.96)
    frags.append(rect(x_ref_l, gy, x_ref_r - x_ref_l, gh, fill="rgba(36, 87, 214, 0.12)", stroke="none"))
    frags.append(line(x_of(3.91), gy, x_of(3.91), gy + gh, color=NEG, sw=2, dash="3,3"))

    x_act_l = x_of(4.17)
    x_act_r = x_of(4.35)
    frags.append(rect(x_act_l, gy, x_act_r - x_act_l, gh, fill="rgba(192, 57, 43, 0.15)", stroke="none"))
    frags.append(line(x_of(4.26), gy, x_of(4.26), gy + gh, color=POS, sw=2, dash="3,3"))

    # Стрілки від верхніх карток до смуг на графіку
    frags.append(arrow(260, 68, x_of(3.91), gy + 5, color=NEG))
    frags.append(arrow(600, 68, x_of(4.26), gy + 5, color=POS))

    # Вертикальні лінії сітки (2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0 мкм)
    for wl in [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]:
        frags.append(line(x_of(wl), gy, x_of(wl), gy + gh, color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(x_of(wl), gy + gh + 22, f"{wl:.1f}", size=13, color=MUTED))

    frags.append(text(x_of(2.0), gy + gh + 22, "2.0", size=13, color=MUTED))
    frags.append(text(gx + gw / 2, gy + gh + 48, "Довжина хвилі λ (мкм)", size=14, bold=True))

    # Горизонтальні лінії сітки (20%, 40%, 60%, 80%, 100%)
    for pct in [20, 40, 60, 80, 100]:
        frags.append(line(gx, y_of(pct), gx + gw, y_of(pct), color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(gx - 12, y_of(pct) + 5, f"{pct}%", size=12, color=MUTED, anchor="end"))
    frags.append(text(gx - 12, y_of(0) + 5, "0%", size=12, color=MUTED, anchor="end"))
    frags.append(text(gx - 45, gy + gh / 2, "Поглинання", size=13, bold=True, anchor="middle"))

    # Спектри поглинання газів
    # 1. H2O (водяна пара)
    pts_h2o = [
        (2.0, 5), (2.4, 10), (2.6, 45), (2.7, 75), (2.8, 50), (3.0, 15),
        (3.4, 5), (3.8, 2), (4.0, 2), (4.3, 3), (4.8, 8), (5.2, 35),
        (5.6, 80), (5.9, 95), (6.0, 98)
    ]
    path_h2o = "M " + " L ".join(f"{x_of(x):.1f},{y_of(y):.1f}" for x, y in pts_h2o)
    frags.append(f'<path d="{path_h2o}" fill="none" stroke="#8e44ad" stroke-width="2.2"/>')

    # 2. CH4 (метан)
    pts_ch4 = [
        (2.0, 0), (3.0, 2), (3.2, 25), (3.3, 70), (3.4, 30), (3.6, 2), (6.0, 0)
    ]
    path_ch4 = "M " + " L ".join(f"{x_of(x):.1f},{y_of(y):.1f}" for x, y in pts_ch4)
    frags.append(f'<path d="{path_ch4}" fill="none" stroke="#d35400" stroke-width="2"/>')

    # 3. CO (чадний газ)
    pts_co = [
        (2.0, 0), (4.4, 0), (4.55, 20), (4.67, 65), (4.8, 25), (5.0, 0), (6.0, 0)
    ]
    path_co = "M " + " L ".join(f"{x_of(x):.1f},{y_of(y):.1f}" for x, y in pts_co)
    frags.append(f'<path d="{path_co}" fill="none" stroke="#7f8c8d" stroke-width="2"/>')

    # 4. CO2 (двоокис вуглецю)
    pts_co2 = [
        (2.0, 0), (2.6, 5), (2.7, 30), (2.8, 8), (3.0, 0),
        (3.9, 0), (4.1, 15), (4.2, 60), (4.26, 98), (4.32, 65), (4.42, 12), (4.6, 0),
        (6.0, 0)
    ]
    path_co2 = "M " + " L ".join(f"{x_of(x):.1f},{y_of(y):.1f}" for x, y in pts_co2)
    frags.append(f'<path d="{path_co2}" fill="none" stroke="{POS}" stroke-width="3.2"/>')

    # Легенда газів у вільному куті графіка (ліворуч угорі)
    lx, ly = gx + 20, gy + 20
    frags.append(rect(lx, ly, 175, 105, fill="#ffffff", stroke="#cbd5e1", rx=4))
    frags.append(line(lx + 10, ly + 18, lx + 35, ly + 18, color=POS, sw=3))
    frags.append(text(lx + 42, ly + 22, "CO₂ (4.26 мкм)", size=12, anchor="start", bold=True))

    frags.append(line(lx + 10, ly + 42, lx + 35, ly + 42, color="#8e44ad", sw=2.2))
    frags.append(text(lx + 42, ly + 46, "H₂O (водяна пара)", size=12, anchor="start"))

    frags.append(line(lx + 10, ly + 66, lx + 35, ly + 66, color="#d35400", sw=2))
    frags.append(text(lx + 42, ly + 70, "CH₄ (метан 3.3 мкм)", size=12, anchor="start"))

    frags.append(line(lx + 10, ly + 90, lx + 35, ly + 90, color="#7f8c8d", sw=2))
    frags.append(text(lx + 42, ly + 94, "CO (чадний газ)", size=12, anchor="start"))

    return render(os.path.join(IMG_DIR, "co2-absorption-spectrum.svg"), w, h, *frags)


def fig_ndir_chamber():
    """Фігура 2: Конструкція оптичної NDIR-камери та двоканального детектора."""
    w, h = 900, 480
    frags = []

    # Головний корпус оптичної кювети
    cx, cy, cw, ch = 60, 50, 780, 310
    frags.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke="#475569", sw=2, rx=12))

    # Золоте внутрішнє дзеркальне покриття
    frags.append(rect(cx + 12, cy + 35, cw - 24, ch - 50, fill="#fffbeb", stroke="#f59e0b", sw=2.5, rx=8))
    frags.append(text(cx + cw / 2, cy + 24, "Оптична камера NDIR із золотим дзеркальним покриттям (R > 98% у діапазоні 3–5 мкм)", size=13, color="#b45309", bold=True))

    # Дифузійні вікна для газу з PTFE-мембраною
    frags.append(rect(cx + 310, cy + 42, 160, 24, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(cx + 390, cy + 58, "PTFE-фільтр (дифузія CO₂)", size=11, color="#334155", bold=True))

    # Молекули CO2 усередині камери
    for mx, my in [(cx + 220, cy + 110), (cx + 310, cy + 160), (cx + 260, cy + 220),
                   (cx + 420, cy + 120), (cx + 510, cy + 180), (cx + 380, cy + 230)]:
        frags.append(circle(mx, my, 12, fill="#fee2e2", stroke=POS, sw=1.5))
        frags.append(text(mx, my + 4, "CO₂", size=10, color=POS, bold=True))

    # Ліва частина: ІЧ-джерело (лампа / MEMS-випромінювач)
    lx, ly = cx + 25, cy + 70
    frags.append(rect(lx, ly, 115, 175, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=6))
    frags.append(text(lx + 57, ly + 28, "ІЧ-джерело", size=13, color="#991b1b", bold=True))
    frags.append(text(lx + 57, ly + 48, "(MEMS / лампа)", size=11, color="#b91c1c"))

    # Спіраль лампи / нагрівальний мікроелемент
    frags.append(circle(lx + 57, ly + 95, 24, fill="#fee2e2", stroke="#dc2626", sw=2))
    frags.append(text(lx + 57, ly + 100, "1–10 Гц", size=11, color="#b91c1c", bold=True))
    frags.append(text(lx + 57, ly + 145, "Модуляція пучка I₀", size=11, color="#4b5563"))

    # Промені світла від джерела (напрямлені до детектора)
    rays = [
        f'<line x1="{lx + 115}" y1="{ly + 95}" x2="{cx + cw - 165}" y2="{cy + 125}" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4"/>',
        f'<line x1="{lx + 115}" y1="{ly + 60}" x2="{cx + 420}" y2="{cy + 75}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4"/>',
        f'<line x1="{cx + 420}" y1="{cy + 75}" x2="{cx + cw - 165}" y2="{cy + 205}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4"/>',
        f'<line x1="{lx + 115}" y1="{ly + 130}" x2="{cx + 250}" y2="{cy + ch - 22}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4"/>',
        f'<line x1="{cx + 250}" y1="{cy + ch - 22}" x2="{cx + cw - 165}" y2="{cy + 130}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4"/>',
    ]
    frags.extend(rays)

    # Оптична довжина шляху L (у чистому прямокутнику)
    frags.append(line(lx + 125, cy + ch - 40, cx + cw - 175, cy + ch - 40, color="#64748b", sw=1.5))
    frags.append(circle(lx + 125, cy + ch - 40, 3, fill="#64748b", stroke="#64748b"))
    frags.append(circle(cx + cw - 175, cy + ch - 40, 3, fill="#64748b", stroke="#64748b"))
    box_path, _, _ = textbox(cx + 380, cy + ch - 58, "Оптична довжина шляху L (складений хід променів)", size=11, fill="#ffffff", stroke="#cbd5e1", sw=1, pad=4)
    frags.append(box_path)

    # Права частина: Двоканальний приймач (Dual Channel Detector)
    rx, ry = cx + cw - 160, cy + 65
    frags.append(rect(rx, ry, 145, 185, fill="#f1f5f9", stroke="#334155", sw=2, rx=6))
    frags.append(text(rx + 72, ry + 22, "Двоканальний приймач", size=11, color="#1e293b", bold=True))

    # Канал 1: Активний 4.26 мкм
    frags.append(rect(rx + 10, ry + 40, 125, 55, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(rx + 72, ry + 58, "Фільтр 4.26 мкм", size=11, color=POS, bold=True))
    frags.append(text(rx + 72, ry + 78, "Активний (CO₂) → I_act", size=10, color="#991b1b"))

    # Канал 2: Опорний 3.91 мкм
    frags.append(rect(rx + 10, ry + 110, 125, 55, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(rx + 72, ry + 128, "Фільтр 3.91 мкм", size=11, color=NEG, bold=True))
    frags.append(text(rx + 72, ry + 148, "Опорний (тло) → I_ref", size=10, color="#1e40af"))

    # Вихідний блок обробки сигналу (Ratio R = I_act / I_ref) знизу
    bx, by, bw, bh = cx + 180, cy + ch + 20, 420, 48
    box_calc, _, _ = textbox(bx + bw / 2, by + bh / 2, "Диференційне відношення R = I_act / I_ref\n(усуває старіння лампи та дрейф відбиття дзеркал)", size=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(box_calc)
    frags.append(arrow(rx + 72, ry + 185, bx + bw - 40, by + 10, color=FIELD))

    return render(os.path.join(IMG_DIR, "ndir-chamber-optics.svg"), w, h, *frags)


def fig_beer_lambert_ratio():
    """Фігура 3: Закон Бугера-Ламберта-Бера та компенсація старіння лампи двома каналами."""
    w, h = 860, 420
    frags = []

    # Лівий графік: Одноканальний давач (деградація джерела веде до катастрофічного хибного CO2)
    g1_x, g1_y, gw, gh = 70, 70, 330, 240
    frags.append(rect(g1_x, g1_y, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=4))
    frags.append(text(g1_x + gw / 2, g1_y - 16, "Одноканальний NDIR: дрейф нуля", size=13, color=POS, bold=True))

    # Осі лівого графіка
    frags.append(line(g1_x + 35, g1_y + gh - 30, g1_x + gw - 15, g1_y + gh - 30, color=LINE, sw=1.5))
    frags.append(line(g1_x + 35, g1_y + gh - 30, g1_x + 35, g1_y + 20, color=LINE, sw=1.5))
    frags.append(text(g1_x + gw / 2, g1_y + gh - 8, "Концентрація CO₂ (ppm)", size=11, color=MUTED))
    frags.append(text(g1_x + 20, g1_y + 20, "I", size=12, bold=True))

    # Криві для лівого графіка: нова лампа (I0) vs стара лампа (0.80*I0)
    pts_new = []
    pts_aged = []
    for step in range(25):
        c_val = step / 24.0
        px = g1_x + 35 + c_val * (gw - 60)
        val_new = math.exp(-1.4 * c_val)
        val_aged = 0.80 * math.exp(-1.4 * c_val)
        py_new = (g1_y + gh - 30) - val_new * (gh - 70)
        py_aged = (g1_y + gh - 30) - val_aged * (gh - 70)
        pts_new.append(f"{px:.1f},{py_new:.1f}")
        pts_aged.append(f"{px:.1f},{py_aged:.1f}")

    frags.append(f'<path d="M {" L ".join(pts_new)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    frags.append(f'<path d="M {" L ".join(pts_aged)}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="5,4"/>')

    frags.append(text(g1_x + gw - 40, g1_y + 60, "Нова лампа I₀", size=11, color=FIELD, bold=True, anchor="end"))
    frags.append(text(g1_x + gw - 40, g1_y + 110, "Зношена лампа (−20% I₀)", size=11, color=POS, bold=True, anchor="end"))

    # Показник фальшивого CO2: на нульовому CO2 постаріла лампа дає сигнал як при 800 ppm!
    frags.append(line(g1_x + 35, (g1_y + gh - 30) - 0.80 * (gh - 70), g1_x + 105, (g1_y + gh - 30) - 0.80 * (gh - 70), color=POS, sw=1.5, dash="3,3"))
    frags.append(line(g1_x + 105, (g1_y + gh - 30) - 0.80 * (gh - 70), g1_x + 105, g1_y + gh - 30, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(g1_x + 105, g1_y + gh + 14, "Хибний приріст +800 ppm", size=11, color=POS, bold=True))

    # Правий графік: Двоканальний NDIR (відношення R = I_act / I_ref повністю стабільне)
    g2_x = 460
    frags.append(rect(g2_x, g1_y, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=4))
    frags.append(text(g2_x + gw / 2, g1_y - 16, "Двоканальний NDIR: співвідношення каналів", size=13, color=FIELD, bold=True))

    # Осі правого графіка
    frags.append(line(g2_x + 35, g1_y + gh - 30, g2_x + gw - 15, g1_y + gh - 30, color=LINE, sw=1.5))
    frags.append(line(g2_x + 35, g1_y + gh - 30, g2_x + 35, g1_y + 20, color=LINE, sw=1.5))
    frags.append(text(g2_x + gw / 2, g1_y + gh - 8, "Концентрація CO₂ (ppm)", size=11, color=MUTED))
    frags.append(text(g2_x + 15, g1_y + 20, "R", size=12, bold=True))

    # Крива відношення R(c) = exp(-alpha * c) - незмінна при зміні I0
    pts_ratio = []
    for step in range(25):
        c_val = step / 24.0
        px = g2_x + 35 + c_val * (gw - 60)
        val_r = math.exp(-1.4 * c_val)
        py_r = (g1_y + gh - 30) - val_r * (gh - 70)
        pts_ratio.append(f"{px:.1f},{py_r:.1f}")

    frags.append(f'<path d="M {" L ".join(pts_ratio)}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    frags.append(text(g2_x + gw - 35, g1_y + 65, "R(c) = I_act(c) / I_ref", size=12, color=NEG, bold=True, anchor="end"))
    frags.append(text(g2_x + gw - 35, g1_y + 88, "= I₀·e^(−α·c·L) / (I₀·1)", size=11, color=MUTED, anchor="end"))
    frags.append(text(g2_x + gw - 35, g1_y + 110, "= e^(−α·c·L)  [I₀ скоротилось!]", size=11, color=FIELD, bold=True, anchor="end"))

    # Підсумкова плашка знизу
    bx, by, bw, bh = 70, 345, 720, 50
    box_sum, _, _ = textbox(bx + bw / 2, by + bh / 2, "Висновок: ділення на опорний сигнал 3.91 мкм компенсує дрейф яскравості лампи,\nзабруднення дзеркал та коливання напруги живлення без втрати чутливості.", size=12, fill="#f8fafc", stroke="#64748b", bold=False)
    frags.append(box_sum)

    return render(os.path.join(IMG_DIR, "beer-lambert-dual-channel.svg"), w, h, *frags)


def fig_abc_timeline():
    """Фігура 4: Алгоритм автоматичного фонового калібрування (ABC)."""
    w, h = 880, 500
    frags = []

    # Верхня інформаційна картка про пошук мінімуму (поза сіткою графіка)
    box_abc, _, _ = textbox(440, 42, "ABC-алгоритм шукає найнижчий вимір у ковзному 7-денному вікні (тут: 460 ppm).\nКорекція нульового зсуву: Δ = 460 − 400 = +60 ppm → базову лінію калібрування зсунуто вниз!", size=12, fill="#fef2f2", stroke=POS, bold=True)
    frags.append(box_abc)

    # Графік часового ряду CO2 за 7 днів
    gx, gy, gw, gh = 70, 95, 740, 240
    frags.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=4))

    # Осі
    frags.append(line(gx + 45, gy + gh - 35, gx + gw - 15, gy + gh - 35, color=LINE, sw=1.5))
    frags.append(line(gx + 45, gy + gh - 35, gx + 45, gy + 15, color=LINE, sw=1.5))

    # Позначки рівнів CO2 (400, 800, 1200, 1600 ppm)
    def y_ppm(ppm):
        return (gy + gh - 35) - (ppm / 1800.0) * (gh - 60)

    for ppm in [400, 800, 1200, 1600]:
        frags.append(line(gx + 45, y_ppm(ppm), gx + gw - 15, y_ppm(ppm), color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(gx + 38, y_ppm(ppm) + 4, f"{ppm}", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx + 38, y_ppm(0) + 4, "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx + 12, gy + 20, "ppm", size=12, bold=True))

    # Еталонна лінія 400 ppm (базовий рівень атмосфери)
    frags.append(line(gx + 45, y_ppm(400), gx + gw - 15, y_ppm(400), color=FIELD, sw=2, dash="5,3"))
    frags.append(text(gx + gw - 20, y_ppm(400) - 8, "Чисте вуличне повітря (400–420 ppm)", size=11, color=FIELD, bold=True, anchor="end"))

    # Дні тижня на осі X (Пн, Вт, Ср, Чт, Пт, Сб, Нд)
    day_w = (gw - 65) / 7.0
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб (вих)", "Нд (вих)"]
    for i, d in enumerate(days):
        dx = gx + 45 + i * day_w
        frags.append(line(dx, gy + gh - 35, dx, gy + 15, color="#f1f5f9", sw=1))
        frags.append(text(dx + day_w / 2, gy + gh - 15, d, size=12, color=MUTED, bold=(i >= 5)))

    # Профіль концентрації CO2 за тиждень
    co2_curve = []
    for day in range(7):
        is_weekend = (day >= 5)
        d_start = gx + 45 + day * day_w
        drift_offset = 60
        peak = 600 if is_weekend else 1450
        pts = [
            (d_start, 400 + drift_offset + 50),
            (d_start + day_w * 0.35, peak),
            (d_start + day_w * 0.70, (400 + drift_offset + (150 if is_weekend else 400))),
            (d_start + day_w * 0.95, 400 + drift_offset)
        ]
        for px, ppm_val in pts:
            co2_curve.append(f"{px:.1f},{y_ppm(ppm_val):.1f}")

    frags.append(f'<path d="M {" L ".join(co2_curve)}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')

    # Позначення нічного мінімуму
    min_x = gx + 45 + 6 * day_w + day_w * 0.95
    min_y = y_ppm(460)
    frags.append(circle(min_x, min_y, 6, fill=POS, stroke="#991b1b", sw=2))
    frags.append(line(gx + 45, min_y, min_x, min_y, color=POS, sw=1.5, dash="3,3"))

    # Попередження про пастку ABC
    bx, by, bw, bh = 70, 365, 740, 85
    box_warn, _, _ = textbox(bx + bw / 2, by + bh / 2, "⚠️ Пастка ABC у приміщеннях з постійними людьми або в теплицях:\nЯкщо приміщення ніколи не провітрюється до вуличного стану (мінімум лишається 800 ppm),\nABC помилково прийме 800 ppm за чисте повітря 400 ppm і почне занижувати всі покази на 400 ppm!\nДля таких об'єктів ABC вимикають або використовують двоканальні NDIR-давачі.", size=12, fill="#fffbeb", stroke="#d97706", bold=False)
    frags.append(box_warn)

    return render(os.path.join(IMG_DIR, "abc-algorithm-timeline.svg"), w, h, *frags)


def main():
    print("Генерація SVG-фігур для ndir-sensor...")
    fig_co2_spectrum()
    fig_ndir_chamber()
    fig_beer_lambert_ratio()
    fig_abc_timeline()
    print("Фігури успішно згенеровано у img/.")


if __name__ == "__main__":
    main()
