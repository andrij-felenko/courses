# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'hall-current-sensor' (Струм без розриву кола)."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_open_loop():
    """Топологія з відкритим контуром (Open-Loop Hall Sensor)."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 28, "Сенсор струму з відкритим контуром (Open-Loop Hall)", size=16, bold=True))

    cx, cy = 250, 230
    r_out, r_in = 140, 90
    
    # Тіло осердя
    frags.append(rect(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out, fill="#e2e8f0", stroke="#475569", sw=2.5, rx=18))
    frags.append(rect(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in, fill=BG, stroke="#475569", sw=2.5, rx=10))
    
    # Повітряний зазор праворуч (air gap)
    gap_y = cy - 22
    gap_h = 44
    frags.append(rect(cx + r_in - 2, gap_y, (r_out - r_in) + 4, gap_h, fill=BG, stroke=BG, sw=1))
    frags.append(line(cx + r_in, gap_y, cx + r_out, gap_y, color="#475569", sw=2.5))
    frags.append(line(cx + r_in, gap_y + gap_h, cx + r_out, gap_y + gap_h, color="#475569", sw=2.5))

    # Первинна силова шина (струм I_p) по центру
    frags.append(circle(cx, cy, 34, fill="#fee2e2", stroke=POS, sw=2.5))
    frags.append(circle(cx, cy, 7, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx, cy + 54, "Первинний струм I_p", size=13, color=POS, bold=True))
    frags.append(text(cx, cy - 44, "Силова шина", size=12, color=MUTED))

    # Лінії магнітного потоку в осерді
    frags.append(text(cx - 100, cy, "Феромагнітне", size=12, color="#334155", bold=True))
    frags.append(text(cx - 100, cy + 16, "осердя (μ_r >> 1)", size=11, color=MUTED))
    frags.append(arrow(cx - 115, cy - 70, cx - 70, cy - 115, color=FIELD, sw=2))
    frags.append(arrow(cx + 70, cy - 115, cx + 115, cy - 70, color=FIELD, sw=2))
    frags.append(arrow(cx - 70, cy + 115, cx - 115, cy + 70, color=FIELD, sw=2))
    frags.append(arrow(cx + 115, cy + 70, cx + 70, cy + 115, color=FIELD, sw=2))
    frags.append(text(cx, cy - 120, "Магнітний потік Φ", size=12, color=FIELD, bold=True))

    # Зазор і елемент Холла
    hall_x = cx + r_in + 12
    hall_y = cy - 14
    hall_w = 26
    hall_h = 28
    frags.append(rect(hall_x, hall_y, hall_w, hall_h, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    frags.append(text(hall_x + hall_w / 2, hall_y + 18, "H", size=14, color="#854d0e", bold=True))
    
    frags.append(text(cx + r_out + 18, cy - 28, "Зазор l_g", size=12, color="#1e293b", bold=True, anchor="start"))
    frags.append(text(cx + r_out + 18, cy - 10, "B_g ≈ μ₀·I_p / l_g", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(cx + r_out + 18, cy + 8, "Елемент Холла", size=11, color="#854d0e", anchor="start"))

    # Електронний тракт праворуч
    ax1, ay1 = 570, cy - 40
    frags.append(arrow(hall_x + hall_w + 2, cy, ax1 - 10, cy, color=LINE, sw=1.8))
    frags.append(text(ax1 - 38, cy - 10, "V_H (мВ)", size=11, color=MUTED))

    # Блок підсилювача та лінеаризації
    frags.append(rect(ax1, ay1, 160, 80, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(ax1 + 80, ay1 + 26, "Підсилювач", size=13, bold=True))
    frags.append(text(ax1 + 80, ay1 + 45, "й термокомпенсація", size=12, color=MUTED))
    frags.append(text(ax1 + 80, ay1 + 65, "V_out = V_0 + S · I_p", size=11, color=FIELD, bold=True))

    # Вихідний сигнал
    frags.append(arrow(ax1 + 160, cy, ax1 + 220, cy, color=LINE, sw=2))
    frags.append(circle(ax1 + 224, cy, 4, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(ax1 + 224, cy - 14, "V_out", size=13, color=POS, bold=True))
    frags.append(text(ax1 + 224, cy + 20, "до АЦП", size=11, color=MUTED))

    # Блок живлення сенсора
    frags.append(line(ax1 + 80, ay1, ax1 + 80, ay1 - 25, color=POS, sw=1.5))
    frags.append(text(ax1 + 80, ay1 - 30, "+V_cc (5 В / 3.3 В)", size=11, color=POS, bold=True))

    # Інформаційна плашка знизу
    bx, by, bw, bh = 50, 380, 720, 42
    frags.append(rect(bx, by, bw, bh, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(bx + bw / 2, by + 26, "Особливості: проста схема, нульові втрати на компенсацію, але чутливість до насичення та гістерезису осердя", size=12, color="#334155"))

    render(os.path.join(IMG_DIR, "core-open-loop.svg"), w, h, *frags)


def fig_closed_loop():
    """Топологія із замкненим контуром (Closed-Loop Zero-Flux Sensor)."""
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Сенсор струму із замкненим контуром (Closed-Loop / Zero-Flux)", size=16, bold=True))

    # Магнітне осердя
    cx, cy = 230, 240
    r_out, r_in = 135, 88

    frags.append(rect(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out, fill="#e2e8f0", stroke="#475569", sw=2.5, rx=18))
    frags.append(rect(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in, fill=BG, stroke="#475569", sw=2.5, rx=10))

    # Зазор праворуч
    gap_y = cy - 20
    gap_h = 40
    frags.append(rect(cx + r_in - 2, gap_y, (r_out - r_in) + 4, gap_h, fill=BG, stroke=BG, sw=1))
    frags.append(line(cx + r_in, gap_y, cx + r_out, gap_y, color="#475569", sw=2.5))
    frags.append(line(cx + r_in, gap_y + gap_h, cx + r_out, gap_y + gap_h, color="#475569", sw=2.5))

    # Первинна шина (струм I_p, N_p = 1)
    frags.append(circle(cx, cy, 32, fill="#fee2e2", stroke=POS, sw=2.5))
    frags.append(circle(cx, cy, 6, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx, cy + 50, "I_p (первинний)", size=12, color=POS, bold=True))
    frags.append(text(cx, cy - 42, "N_p = 1 виток", size=11, color=MUTED))

    # Вторинна компенсаційна обмотка N_s на лівій частині осердя (малюємо дротяні витки лініями)
    wx1 = cx - r_out - 6
    wx2 = cx - r_in + 6
    for i in range(7):
        wy = cy - 66 + i * 22
        frags.append(line(wx1, wy, wx2, wy, color="#ea580c", sw=3))
        frags.append(circle(wx1, wy, 3, fill="#ea580c", stroke="#ea580c", sw=1))
        frags.append(circle(wx2, wy, 3, fill="#ea580c", stroke="#ea580c", sw=1))

    frags.append(text(cx - r_out - 35, cy, "Обмотка N_s", size=11.5, color="#c2410c", bold=True))
    frags.append(text(cx - r_out - 35, cy + 16, "(1000..2000 витків)", size=10.5, color=MUTED))

    # Елемент Холла в зазорі як детектор нуля
    hall_x = cx + r_in + 12
    hall_y = cy - 13
    hall_w = 24
    hall_h = 26
    frags.append(rect(hall_x, hall_y, hall_w, hall_h, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    frags.append(text(hall_x + hall_w / 2, hall_y + 17, "H", size=13, color="#854d0e", bold=True))
    frags.append(text(cx + r_out + 12, cy - 14, "Детектор нуля", size=11, color="#854d0e", bold=True, anchor="start"))
    frags.append(text(cx + r_out + 12, cy + 2, "Φ_core = 0", size=12, color=FIELD, bold=True, anchor="start"))

    # Схема керування зворотним зв'язком (Операційний підсилювач / Драйвер)
    op_x, op_y = 520, cy - 50
    op_w, op_h = 130, 80
    frags.append(arrow(hall_x + hall_w + 2, cy, op_x - 10, cy - 10, color=LINE, sw=1.8))
    frags.append(rect(op_x, op_y, op_w, op_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(op_x + op_w / 2, op_y + 24, "Підсилювач-", size=12, bold=True))
    frags.append(text(op_x + op_w / 2, op_y + 40, "інтегратор", size=12, bold=True))
    frags.append(text(op_x + op_w / 2, op_y + 60, "Драйвер I_s", size=11, color=NEG, bold=True))

    # Лінія струму компенсації I_s від драйвера до обмотки N_s
    frags.append(line(op_x + op_w / 2, op_y, op_x + op_w / 2, 90, color=NEG, sw=2))
    frags.append(line(op_x + op_w / 2, 90, cx - r_out + 20, 90, color=NEG, sw=2))
    frags.append(arrow(cx - r_out + 20, 90, cx - r_out + 20, cy - 70, color=NEG, sw=2))
    frags.append(text(340, 78, "Струм компенсації I_s = I_p / N_s", size=12, color=NEG, bold=True))

    # Від нижньої частини обмотки N_s до вимірювального резистора R_m
    frags.append(line(cx - r_out + 20, cy + 70, cx - r_out + 20, 400, color=NEG, sw=2))
    frags.append(line(cx - r_out + 20, 400, 680, 400, color=NEG, sw=2))
    
    # Вимірювальний резистор R_m (Burden resistor)
    rm_x, rm_y = 680, 350
    frags.append(rect(rm_x - 12, rm_y, 24, 46, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=3))
    frags.append(text(rm_x, rm_y + 26, "R_m", size=12, color="#0369a1", bold=True))
    frags.append(line(rm_x, rm_y + 46, rm_x, 415, color=LINE, sw=1.8))
    frags.append(line(rm_x - 12, 415, rm_x + 12, 415, color=LINE, sw=1.8))
    frags.append(line(rm_x - 7, 419, rm_x + 7, 419, color=LINE, sw=1.5))
    frags.append(line(rm_x - 3, 423, rm_x + 3, 423, color=LINE, sw=1.2))
    frags.append(text(rm_x + 24, rm_y + 26, "Земля (GND)", size=10.5, color=MUTED, anchor="start"))

    # Вихідний сигнал напруги V_out з верхньої клеми R_m
    frags.append(line(680, 340, 680, 240, color=LINE, sw=2))
    frags.append(arrow(680, 240, 750, 240, color=LINE, sw=2))
    frags.append(circle(754, 240, 4, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(754, 224, "V_out", size=13, color=POS, bold=True))
    frags.append(text(754, 258, "V_out = I_s · R_m", size=11, color="#0369a1", bold=True))
    frags.append(text(754, 274, "= I_p · (R_m / N_s)", size=11, color=FIELD, bold=True))

    # З'єднання виходу драйвера з точкою R_m
    frags.append(line(op_x + op_w, cy - 10, 680, cy - 10, color=NEG, sw=2))
    frags.append(line(680, cy - 10, 680, 340, color=NEG, sw=2))

    render(os.path.join(IMG_DIR, "core-closed-loop.svg"), w, h, *frags)


def fig_coreless_diff():
    """Безсердечниковий сенсор струму з диференціальним придушенням завад."""
    w, h = 820, 430
    frags = []

    frags.append(text(w / 2, 28, "Диференціальне безсердечникове вимірювання (Coreless IC)", size=16, bold=True))

    # Корпус мікросхеми SOIC-8 (зовнішній контур)
    ic_x, ic_y, ic_w, ic_h = 100, 70, 620, 320
    frags.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#f8fafc", stroke="#334155", sw=2, rx=12))
    frags.append(text(ic_x + 24, ic_y + 28, "Корпус IC (SOIC-8 / QFN)", size=12, color=MUTED, anchor="start"))

    # Первинний U-подібний провідник (leadframe)
    p_x1, p_x2 = 180, 300
    p_y1, p_y2 = 120, 340
    p_w = 46

    # Доріжка IP+
    frags.append(rect(p_x1 - p_w / 2, p_y1, p_w, p_y2 - p_y1 - 30, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    frags.append(arrow(p_x1, p_y1 + 20, p_x1, p_y2 - 50, color=POS, sw=2.5))
    frags.append(text(p_x1, p_y1 - 14, "Вхід IP+", size=12, color=POS, bold=True))
    frags.append(text(p_x1, p_y2 - 20, "+I_p", size=12, color=POS, bold=True))

    # Перемичка внизу
    frags.append(rect(p_x1 - p_w / 2, p_y2 - 40, (p_x2 - p_x1) + p_w, 36, fill="#fee2e2", stroke=POS, sw=2, rx=4))

    # Доріжка IP- (струм тече вгору)
    frags.append(rect(p_x2 - p_w / 2, p_y1, p_w, p_y2 - p_y1 - 30, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    frags.append(arrow(p_x2, p_y2 - 50, p_x2, p_y1 + 20, color=POS, sw=2.5))
    frags.append(text(p_x2, p_y1 - 14, "Вихід IP−", size=12, color=POS, bold=True))
    frags.append(text(p_x2, p_y2 - 20, "−I_p", size=12, color=POS, bold=True))

    # Магнітні поля, створювані струмом
    frags.append(circle(p_x1, 210, 16, fill="#dcfce7", stroke=FIELD, sw=2))
    frags.append(text(p_x1, 215, "✕", size=16, color=FIELD, bold=True))
    frags.append(text(p_x1 - 36, 215, "+B_sig", size=12, color=FIELD, bold=True, anchor="end"))

    frags.append(circle(p_x2, 210, 16, fill="#dcfce7", stroke=FIELD, sw=2))
    frags.append(circle(p_x2, 210, 4, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(p_x2 + 36, 215, "−B_sig", size=12, color=FIELD, bold=True, anchor="start"))

    # Два чутливі елементи Холла на кристалі
    h1_x, h1_y = p_x1 - 14, 250
    h2_x, h2_y = p_x2 - 14, 250
    frags.append(rect(h1_x, h1_y, 28, 28, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    frags.append(text(h1_x + 14, h1_y + 18, "H1", size=11, color="#854d0e", bold=True))

    frags.append(rect(h2_x, h2_y, 28, 28, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    frags.append(text(h2_x + 14, h2_y + 18, "H2", size=11, color="#854d0e", bold=True))

    # Зовнішня однорідна магнітна завада B_ext
    frags.append(rect(140, 100, 200, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(240, 120, "Паразитна завада B_ext", size=11, color="#475569", bold=True))
    frags.append(arrow(170, 140, 170, 170, color="#94a3b8", sw=1.5))
    frags.append(arrow(290, 140, 290, 170, color="#94a3b8", sw=1.5))

    # Блок диференціального віднімання (Diff Subtractor)
    sub_x, sub_y, sub_w, sub_h = 420, 160, 260, 150
    frags.append(rect(sub_x, sub_y, sub_w, sub_h, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(sub_x + sub_w / 2, sub_y + 24, "Диференціальний підсилювач", size=12.5, bold=True))

    frags.append(arrow(h1_x + 28, h1_y + 14, sub_x + 10, sub_y + 60, color=LINE, sw=1.5))
    frags.append(text(sub_x + 20, sub_y + 54, "V₁ = S·(+B_sig + B_ext)", size=11, color="#334155", anchor="start"))

    frags.append(arrow(h2_x + 28, h2_y + 14, sub_x + 10, sub_y + 100, color=LINE, sw=1.5))
    frags.append(text(sub_x + 20, sub_y + 94, "V₂ = S·(−B_sig + B_ext)", size=11, color="#334155", anchor="start"))

    # Формула віднімання
    frags.append(line(sub_x + 15, sub_y + 112, sub_x + sub_w - 15, sub_y + 112, color="#cbd5e1", sw=1.2))
    frags.append(text(sub_x + sub_w / 2, sub_y + 132, "V_diff = V₁ − V₂ = 2 · S · B_sig", size=12, color=FIELD, bold=True))

    # Вихід
    frags.append(arrow(sub_x + sub_w, sub_y + sub_h / 2, sub_x + sub_w + 35, sub_y + sub_h / 2, color=LINE, sw=2))
    frags.append(circle(sub_x + sub_w + 38, sub_y + sub_h / 2, 4, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(sub_x + sub_w + 40, sub_y + sub_h / 2 - 12, "V_out", size=13, color=POS, bold=True, anchor="start"))
    frags.append(text(sub_x + sub_w + 40, sub_y + sub_h / 2 + 16, "Без впливу B_ext", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG_DIR, "coreless-differential.svg"), w, h, *frags)


def fig_signal_chain():
    """Тракт формування та цифрової обробки сигналу струмового сенсора."""
    w, h = 840, 360
    frags = []

    frags.append(text(w / 2, 28, "Тракт обробки сигналу: від кристала Холла до мікроконтролера", size=16, bold=True))

    # 4 блоки: Чутливий кристал -> Chopper/PGA -> Фільтр низьких частот -> MCU (ADC + DSP)
    b_w = 160
    b_h = 100
    y = 110

    # Блок 1: Міст Холла (Кристал)
    b1_x = 40
    frags.append(rect(b1_x, y, b_w, b_h, fill="#fef9c3", stroke="#ca8a04", sw=1.8, rx=8))
    frags.append(text(b1_x + b_w / 2, y + 24, "Кристал Холла", size=13, color="#854d0e", bold=True))
    frags.append(text(b1_x + b_w / 2, y + 46, "Магнітний міст", size=11.5, color=MUTED))
    frags.append(text(b1_x + b_w / 2, y + 68, "Сигнал: одиниці мВ", size=11, color=FIELD, bold=True))
    frags.append(text(b1_x + b_w / 2, y + 86, "+ зсув V_offset", size=10.5, color=POS))

    # Стрілка 1 -> 2
    frags.append(arrow(b1_x + b_w, y + b_h / 2, b1_x + b_w + 30, y + b_h / 2, color=LINE, sw=2))

    # Блок 2: Chopper + Підсилювач (PGA)
    b2_x = 230
    frags.append(rect(b2_x, y, b_w, b_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(b2_x + b_w / 2, y + 24, "Chopper + PGA", size=13, bold=True))
    frags.append(text(b2_x + b_w / 2, y + 46, "Динамічне обнулення", size=11, color=MUTED))
    frags.append(text(b2_x + b_w / 2, y + 64, "зсуву (1/f шум)", size=11, color=MUTED))
    frags.append(text(b2_x + b_w / 2, y + 86, "Підсилення G ≈ 100..500", size=10.5, color=FIELD, bold=True))

    # Стрілка 2 -> 3
    frags.append(arrow(b2_x + b_w, y + b_h / 2, b2_x + b_w + 30, y + b_h / 2, color=LINE, sw=2))

    # Блок 3: Антиаліасинговий ФНЧ (RC Low-Pass Filter)
    b3_x = 420
    frags.append(rect(b3_x, y, b_w, b_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(b3_x + b_w / 2, y + 24, "RC-фільтр (ФНЧ)", size=13, bold=True))
    frags.append(text(b3_x + b_w / 2, y + 46, "Антиаліасинг", size=11.5, color=MUTED))
    frags.append(text(b3_x + b_w / 2, y + 66, "Обмеження шуму", size=11, color=MUTED))
    frags.append(text(b3_x + b_w / 2, y + 86, "f_c = 10..80 кГц", size=11, color=FIELD, bold=True))

    # Стрілка 3 -> 4
    frags.append(arrow(b3_x + b_w, y + b_h / 2, b3_x + b_w + 30, y + b_h / 2, color=LINE, sw=2))

    # Блок 4: Мікроконтролер (MCU / DSP)
    b4_x = 610
    b4_w = 190
    frags.append(rect(b4_x, y, b4_w, b_h, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=8))
    frags.append(text(b4_x + b4_w / 2, y + 22, "Мікроконтролер (MCU)", size=13, color="#0369a1", bold=True))
    frags.append(text(b4_x + b4_w / 2, y + 42, "• 12/16-бітний АЦП", size=11, color="#334155"))
    frags.append(text(b4_x + b4_w / 2, y + 60, "• Автокалібрування нуля", size=11, color="#334155"))
    frags.append(text(b4_x + b4_w / 2, y + 78, "• Цифровий фільтр (IIR)", size=11, color="#334155"))
    frags.append(text(b4_x + b4_w / 2, y + 94, "• I = (V_adc − V_0) / S", size=11, color=FIELD, bold=True))

    # Нижня стрілка повернення / Калібрувальний зв'язок
    frags.append(rect(60, 240, 720, 75, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(420, 265, "Програмна обробка в прошивці:", size=12.5, color="#1e293b", bold=True))
    frags.append(text(420, 286, "1. Зняття V_0 при I_p = 0 під час старту. 2. Ратіометрична корекція опорної напруги V_ref.", size=11.5, color="#475569"))
    frags.append(text(420, 304, "3. Експоненційне згладжування I_filt[k] = α · I_raw + (1 − α) · I_filt[k−1].", size=11.5, color="#475569"))

    render(os.path.join(IMG_DIR, "signal-conditioning-chain.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_open_loop()
    fig_closed_loop()
    fig_coreless_diff()
    fig_signal_chain()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
