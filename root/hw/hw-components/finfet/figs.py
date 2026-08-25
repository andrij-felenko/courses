# -*- coding: utf-8 -*-
"""Фігури до теми «FinFET: тривимірний транзистор» (book/electronics/microelectronics/finfet)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "img")


def fig_planar_vs_finfet():
    w, h = 880, 420
    frags = []

    # Заголовки секцій
    t_pl, _, _ = textbox(220, 30, "Планарний MOSFET (2D)\nЗатвор лише зверху", size=13, bold=True, pad=8)
    frags.append(t_pl)

    t_fin, _, _ = textbox(660, 30, "FinFET / 3D Tri-Gate\nЗатвор охоплює ребро з трьох боків", size=13, bold=True, pad=8)
    frags.append(t_fin)

    # ── Ліва частина: Планарний MOSFET ──
    # Підкладка p-Si
    frags.append(rect(40, 160, 360, 160, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(220, 290, "p-підкладка (об'ємний кремній)", size=12, color=MUTED))

    # Витік (Source) і Стік (Drain)
    frags.append(rect(40, 160, 90, 60, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(85, 195, "n⁺ Витік", size=12, bold=True, color="#1e7e34"))

    frags.append(rect(310, 160, 90, 60, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(355, 195, "n⁺ Стік", size=12, bold=True, color="#1e7e34"))

    # Оксид і Затвор зверху
    frags.append(rect(140, 150, 160, 10, fill="#ffeeba", stroke="#d39e00", sw=1.2, rx=0))
    frags.append(text(220, 142, "Оксид SiO₂ / High-k", size=10, color="#856404"))

    frags.append(rect(140, 90, 160, 50, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(220, 118, "Затвор (Gate)", size=13, bold=True, color="#004085"))

    # Силові лінії поля стоку (витік у глибині)
    frags.append(line(310, 200, 130, 200, color=POS, sw=1.8, dash="4,3"))
    frags.append(line(310, 215, 130, 215, color=POS, sw=1.8, dash="4,3"))
    frags.append(line(310, 230, 130, 230, color=POS, sw=1.5, dash="4,3"))

    tb_leak, _, _ = textbox(220, 215, "Неконтрольований витік\nу глибині підкладки (SCE/DIBL)", size=11, color=POS, fill="#fff3cd", stroke=POS, pad=6)
    frags.append(tb_leak)

    tb_note1, _, _ = textbox(220, 375, "Поле затвора слабшає з глибиною.\nСтік відкриває підпороговий канал знизу.", size=11, color=INK, fill="#ffffff", stroke=MUTED, pad=6)
    frags.append(tb_note1)

    # Розділювач
    frags.append(line(440, 20, 440, 400, color="#d0d7de", sw=1.5, dash="5,5"))

    # ── Права частина: FinFET (Tri-Gate) ──
    # Діелектрик STI (ізоляція)
    frags.append(rect(480, 250, 360, 70, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(660, 290, "Діелектрична ізоляція STI (SiO₂)", size=12, color=MUTED))

    # Вертикальне кремнієве ребро (Fin)
    frags.append(rect(630, 120, 60, 130, fill="#d4edda", stroke="#27ae60", sw=1.8, rx=0))
    frags.append(text(660, 200, "Кремнієве\nребро (Fin)", size=11, bold=True, color="#1e7e34"))

    # Затвор, що огортає ребро з трьох боків (П-подібна форма)
    # Ліва щока затвора
    frags.append(rect(560, 100, 60, 150, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(590, 175, "Затвор\n(лівий)", size=10, bold=True, color="#004085"))

    # Права щока затвора
    frags.append(rect(700, 100, 60, 150, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(730, 175, "Затвор\n(правий)", size=10, bold=True, color="#004085"))

    # Верхня частина затвора
    frags.append(rect(560, 60, 200, 40, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(660, 84, "Затвор (верхній)", size=11, bold=True, color="#004085"))

    # Шар тонкого діелектрика навколо ребра
    frags.append(line(625, 115, 625, 250, color="#d39e00", sw=2))
    frags.append(line(625, 115, 695, 115, color="#d39e00", sw=2))
    frags.append(line(695, 115, 695, 250, color="#d39e00", sw=2))

    # Стрілки стискання поля (електростатичний контроль)
    frags.append(arrow(595, 140, 625, 140, color=FIELD, sw=1.8))
    frags.append(arrow(725, 140, 695, 140, color=FIELD, sw=1.8))
    frags.append(arrow(660, 95, 660, 115, color=FIELD, sw=1.8))

    tb_note2, _, _ = textbox(660, 375, "Повний об'ємний контроль з 3 боків.\nНемає глибоких шляхів витоку під затвором.", size=11, color=INK, fill="#ffffff", stroke=MUTED, pad=6)
    frags.append(tb_note2)

    render(os.path.join(IMG, "planar-vs-finfet-electrostatics.svg"), w, h, *frags)


def fig_fin_geometry_quantization():
    w, h = 880, 420
    frags = []

    # Ліва частина: Геометрія одного ребра
    tb_g1, _, _ = textbox(220, 30, "Геометрія одного ребра\nРозрахунок ефективної ширини каналу", size=13, bold=True, pad=8)
    frags.append(tb_g1)

    # Підкладка STI
    frags.append(rect(60, 280, 320, 50, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(220, 310, "Діелектрик підкладки (STI)", size=12, color=MUTED))

    # Одне ребро
    frags.append(rect(190, 130, 60, 150, fill="#d4edda", stroke="#27ae60", sw=2, rx=0))
    frags.append(text(220, 205, "Канал Si", size=12, bold=True, color="#1e7e34"))

    # Розмірні лінії
    # Ширина ребра W_fin
    frags.append(line(190, 115, 250, 115, color=INK, sw=1.5))
    frags.append(line(190, 110, 190, 120, color=INK, sw=1.5))
    frags.append(line(250, 110, 250, 120, color=INK, sw=1.5))
    frags.append(text(220, 105, "W_fin (товщина)", size=11, bold=True))

    # Висота ребра H_fin
    frags.append(line(265, 130, 265, 280, color=INK, sw=1.5))
    frags.append(line(260, 130, 270, 130, color=INK, sw=1.5))
    frags.append(line(260, 280, 270, 280, color=INK, sw=1.5))
    frags.append(text(315, 205, "H_fin (висота)", size=11, bold=True))

    # Формула W_eff
    tb_weff, _, _ = textbox(220, 370, "W_eff = 2·H_fin + W_fin\n(провідні дві бічні грані + верхня грань)", size=11, color="#004085", fill="#cce5ff", stroke="#004085", pad=6)
    frags.append(tb_weff)

    # Розділювач
    frags.append(line(440, 20, 440, 400, color="#d0d7de", sw=1.5, dash="5,5"))

    # Права частина: Квантування ширини каналу (Multi-fin)
    tb_g2, _, _ = textbox(660, 30, "Квантування ширини каналу (Multi-Fin)\nДискретний набір струмів керування", size=13, bold=True, pad=8)
    frags.append(tb_g2)

    # Підкладка STI справа
    frags.append(rect(470, 260, 380, 50, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(660, 290, "Спільна основа кристала", size=12, color=MUTED))

    # Три паралельні ребра
    fin_xs = [510, 630, 750]
    for i, fx in enumerate(fin_xs):
        frags.append(rect(fx, 140, 40, 120, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
        frags.append(text(fx + 20, 200, f"Fin #{i+1}", size=11, bold=True, color="#1e7e34"))

    # Спільний затвор над усіма ребрами
    frags.append(rect(480, 90, 360, 40, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(660, 115, "Єдиний металевий затвор (Gate)", size=12, bold=True, color="#004085"))

    # Крок між ребрами (Fin Pitch)
    frags.append(line(530, 270, 650, 270, color=INK, sw=1.5))
    frags.append(line(530, 265, 530, 275, color=INK, sw=1.5))
    frags.append(line(650, 265, 650, 275, color=INK, sw=1.5))
    frags.append(text(590, 282, "Fin Pitch", size=10, bold=True))

    tb_multi, _, _ = textbox(660, 370, "W_total = N_fin · W_eff (де N_fin = 1, 2, 3...)\nШирину не можна змінити неперервно!", size=11, color=POS, fill="#fff3cd", stroke=POS, pad=6)
    frags.append(tb_multi)

    render(os.path.join(IMG, "fin-geometry-quantization.svg"), w, h, *frags)


def fig_subthreshold_swing_dibl():
    w, h = 880, 400
    frags = []

    # Заголовок
    tb_hdr, _, _ = textbox(440, 30, "Вольт-амперні характеристики підпорогового струму (log I_d проти V_gs)\nПорівняння планарного MOSFET і FinFET", size=13, bold=True, pad=8)
    frags.append(tb_hdr)

    # Осі координат
    # Y-вісь (log I_d)
    frags.append(arrow(140, 330, 140, 70, color=INK, sw=2))
    frags.append(text(125, 80, "log I_d", size=13, bold=True, anchor="end"))
    frags.append(text(130, 110, "10⁻³ A (I_on)", size=10, color=MUTED, anchor="end"))
    frags.append(text(130, 190, "10⁻⁶ A", size=10, color=MUTED, anchor="end"))
    frags.append(text(130, 270, "10⁻⁹ A (I_off)", size=10, color=MUTED, anchor="end"))
    frags.append(text(130, 320, "10⁻¹² A", size=10, color=MUTED, anchor="end"))

    # X-вісь (V_gs)
    frags.append(arrow(140, 330, 800, 330, color=INK, sw=2))
    frags.append(text(780, 355, "Напруга затвора V_gs (В)", size=12, bold=True, anchor="end"))
    frags.append(text(140, 348, "0.0 В", size=10, color=MUTED))
    frags.append(text(340, 348, "0.3 В", size=10, color=MUTED))
    frags.append(text(540, 348, "0.6 В", size=10, color=MUTED))
    frags.append(text(720, 348, "0.9 В", size=10, color=MUTED))

    # Горизонтальні пунктирні рівні
    frags.append(line(140, 110, 760, 110, color="#e0e0e0", sw=1, dash="3,3"))
    frags.append(line(140, 190, 760, 190, color="#e0e0e0", sw=1, dash="3,3"))
    frags.append(line(140, 270, 760, 270, color="#e0e0e0", sw=1, dash="3,3"))

    # 1. Крива FinFET (крутий нахил SS ≈ 65 мВ/дек, ідеальний контроль)
    # Низька напруга стоку V_ds = 0.05 В (зелена суцільна)
    frags.append(line(160, 320, 380, 110, color="#27ae60", sw=2.5))
    frags.append(line(380, 110, 740, 95, color="#27ae60", sw=2.5))
    frags.append(text(480, 90, "FinFET (крутий підпороговий схил)", size=11, bold=True, color="#27ae60"))

    # Висока напруга стоку V_ds = 0.8 В (зелена пунктирна - мінімальний DIBL зсув)
    frags.append(line(145, 320, 365, 110, color="#27ae60", sw=2, dash="5,3"))
    frags.append(line(365, 110, 740, 90, color="#27ae60", sw=2, dash="5,3"))

    # 2. Крива планарного короткоканального MOSFET (пологий нахил SS ≈ 110 мВ/дек)
    # Низький V_ds (червона суцільна)
    frags.append(line(160, 260, 520, 110, color=POS, sw=2))
    frags.append(line(520, 110, 740, 100, color=POS, sw=2))
    frags.append(text(620, 130, "Планарний MOSFET (пологий схил)", size=11, bold=True, color=POS))

    # Високий V_ds (червона пунктирна - сильний DIBL зсув вліво!)
    frags.append(line(140, 200, 440, 110, color=POS, sw=2, dash="5,3"))
    frags.append(line(440, 110, 740, 95, color=POS, sw=2, dash="5,3"))

    # Пояснення DIBL зсуву
    frags.append(line(300, 180, 360, 180, color=POS, sw=1.5))
    frags.append(arrow(360, 180, 300, 180, color=POS, sw=1.5))
    tb_dibl, _, _ = textbox(330, 220, "Зсув DIBL у планарного:\nΔV_th до 100-150 мВ", size=10, color=POS, fill="#fff3cd", stroke=POS, pad=5)
    frags.append(tb_dibl)

    # Виноски характеристик
    tb_ss_fin, _, _ = textbox(280, 290, "FinFET:\nSS ≈ 65 мВ/дек\nI_off < 10⁻¹¹ A", size=11, color="#1e7e34", fill="#d4edda", stroke="#27ae60", pad=6)
    frags.append(tb_ss_fin)

    tb_ss_pl, _, _ = textbox(680, 220, "Планарний короткий канал:\nSS ≈ 110 мВ/дек\nВеличезний витік I_off > 10⁻⁷ A", size=11, color=POS, fill="#f8d7da", stroke=POS, pad=6)
    frags.append(tb_ss_pl)

    render(os.path.join(IMG, "subthreshold-swing-dibl.svg"), w, h, *frags)


def fig_self_heating_and_parasitics():
    w, h = 880, 420
    frags = []

    # Заголовок
    tb_hdr, _, _ = textbox(440, 30, "Поздовжній розріз FinFET: нарощений витік/стік, паразитні ємності та саморозігрів", size=13, bold=True, pad=8)
    frags.append(tb_hdr)

    # Нижня ізоляція STI
    frags.append(rect(60, 290, 760, 60, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(440, 325, "Оксидна підкладка STI (SiO₂, низька теплопровідність k ≈ 1.4 Вт/(м·К))", size=12, color=MUTED))

    # Тонке кремнієве ребро каналу посередині
    frags.append(rect(370, 160, 140, 130, fill="#fff3cd", stroke="#e67e22", sw=2, rx=0))
    frags.append(text(440, 210, "Гаряча зона каналу\n(Self-Heating, ΔT > 25 °C)", size=11, bold=True, color="#d35400"))

    # Нарощений епітаксійний Витік (Source) зліва (ромбоподібний/фасеточний)
    frags.append(rect(140, 130, 190, 160, fill="#d4edda", stroke="#27ae60", sw=2, rx=4))
    frags.append(text(235, 190, "Епітаксійний Витік\n(Raised SiGe / Si:P)", size=12, bold=True, color="#1e7e34"))
    frags.append(text(235, 230, "Зниження R_sd", size=10, color=MUTED))

    # Нарощений епітаксійний Стік (Drain) справа
    frags.append(rect(550, 130, 190, 160, fill="#d4edda", stroke="#27ae60", sw=2, rx=4))
    frags.append(text(645, 190, "Епітаксійний Стік\n(Raised SiGe / Si:P)", size=12, bold=True, color="#1e7e34"))
    frags.append(text(645, 230, "Зниження R_sd", size=10, color=MUTED))

    # Спейсери діелектрика (Low-k spacer)
    frags.append(rect(330, 120, 40, 170, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=0))
    frags.append(text(350, 270, "Spacer", size=9, color=MUTED))

    frags.append(rect(510, 120, 40, 170, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=0))
    frags.append(text(530, 270, "Spacer", size=9, color=MUTED))

    # Металевий затвор над каналом
    frags.append(rect(370, 70, 140, 90, fill="#cce5ff", stroke="#004085", sw=2, rx=2))
    frags.append(text(440, 110, "Металевий затвор (Gate)", size=12, bold=True, color="#004085"))
    frags.append(text(440, 130, "High-k оксид (HfO₂)", size=10, color="#004085"))

    # Паразитні ємності окантовки (Fringe capacitance C_fringe)
    frags.append(line(370, 90, 310, 140, color=POS, sw=1.5, dash="4,3"))
    frags.append(line(510, 90, 570, 140, color=POS, sw=1.5, dash="4,3"))
    tb_cf1, _, _ = textbox(300, 110, "C_fringe", size=10, color=POS, fill="#fff3cd", stroke=POS, pad=4)
    frags.append(tb_cf1)
    tb_cf2, _, _ = textbox(580, 110, "C_fringe", size=10, color=POS, fill="#fff3cd", stroke=POS, pad=4)
    frags.append(tb_cf2)

    # Теплові хвилі в каналі (пастка тепла через тонкий кремній і оксид)
    tb_heat, _, _ = textbox(440, 380, "Тепловий бар'єр: тонке ребро обмежує фононну теплопровідність (20–40 Вт/(м·К)),\nа нижній оксид блокує відведення тепла у масив кремнію.", size=11, color=INK, fill="#ffffff", stroke=MUTED, pad=6)
    frags.append(tb_heat)

    render(os.path.join(IMG, "self-heating-and-parasitics.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_planar_vs_finfet()
    fig_fin_geometry_quantization()
    fig_subthreshold_swing_dibl()
    fig_self_heating_and_parasitics()
    print("Всі 4 фігури успішно згенеровано.")
