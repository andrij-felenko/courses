# -*- coding: utf-8 -*-
"""Фігури до теми «Зв'язані таймери: майстер, підлеглий, внутрішній тригер».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і компоненти — зі спільного svgkit.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Внутрішня тригерна матриця таймерів (Master TRGO → Slave TRGI) ────────
def fig_trigger_matrix():
    W, H = 960, 520
    f = []

    # Загальне тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 42, "Внутрішня тригерна матриця таймерів (Master TRGO → Crossbar → Slave TRGI)", size=15, bold=True, color=INK))

    # --- БЛОК 1: Master Timer (Ліворуч) ---
    mx, my, mw, mh = 40, 75, 270, 410
    f.append(rect(mx, my, mw, mh, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(mx + mw / 2, my + 25, "Master Timer (TIMx)", size=13, bold=True, color=NEG))

    # Внутрішні вузли майстра
    b_cnt, _, _ = textbox(mx + mw / 2, my + 70, "Лічильник CNT (16 / 32 біт)", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=220)
    f.append(b_cnt)

    b_arr, _, _ = textbox(mx + mw / 2, my + 130, "Автоперезавантаження ARR\n(Подія оновлення UEV)", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=220)
    f.append(b_arr)

    b_ccr, _, _ = textbox(mx + mw / 2, my + 195, "Канали порівняння CCR1..CCR4\n(OC1REF .. OC4REF)", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=220)
    f.append(b_ccr)

    b_mms, _, _ = textbox(mx + mw / 2, my + 300, "Селектор Master Mode (CR2.MMS)\n000: Reset | 001: CEN | 010: UEV\n011: CC1IF | 100..111: OCxREF", size=9.5, bold=True, fill="#dbeafe", stroke=NEG, min_w=235)
    f.append(b_mms)

    # Зв'язки між вузлами майстра до селектора MMS
    f.append(arrow(mx + mw / 2, my + 88, mx + mw / 2, my + 102, color=NEG, sw=1.5))
    f.append(arrow(mx + mw / 2, my + 158, mx + mw / 2, my + 167, color=NEG, sw=1.5))
    f.append(arrow(mx + mw / 2, my + 223, mx + mw / 2, my + 262, color=NEG, sw=1.5))

    # Вихід TRGO
    f.append(arrow(mx + mw, my + 300, mx + mw + 50, my + 300, color=POS, sw=2.2))
    f.append(text(mx + mw + 25, my + 288, "TRGO", size=11, bold=True, color=POS, anchor="middle"))

    # --- БЛОК 2: Внутрішня кросбар-матриця ITR0..ITR3 (Центр) ---
    cx, cy, cw, ch = 360, 75, 230, 410
    f.append(rect(cx, cy, cw, ch, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    f.append(text(cx + cw / 2, cy + 25, "Внутрішня шинна матриця", size=12.5, bold=True, color="#b45309"))
    f.append(text(cx + cw / 2, cy + 42, "(On-chip ITR Interconnect)", size=10, color=MUTED))

    # 4 шини ITR
    itr_y = [cy + 100, cy + 170, cy + 240, cy + 310]
    itr_labels = [
        "ITR0 (напр. TIM1 TRGO)",
        "ITR1 (напр. TIM2 TRGO)",
        "ITR2 (напр. TIM3 TRGO)",
        "ITR3 (напр. TIM4 / TIM8 TRGO)"
    ]
    for i in range(4):
        f.append(line(cx + 15, itr_y[i], cx + cw - 15, itr_y[i], color="#d97706", sw=2.5))
        f.append(circle(cx + 15, itr_y[i], 3.5, fill="#d97706", stroke="#d97706"))
        f.append(text(cx + cw / 2, itr_y[i] - 10, itr_labels[i], size=9.5, bold=True, color="#92400e"))

    # З'єднання TRGO майстра до матриці (ITR1)
    f.append(line(mx + mw + 50, my + 300, cx - 15, my + 300, color=POS, sw=2.0))
    f.append(line(cx - 15, my + 300, cx - 15, cy + 170, color=POS, sw=2.0))
    f.append(arrow(cx - 15, cy + 170, cx + 15, cy + 170, color=POS, sw=2.0))

    # Виходи матриці до слейва
    for i in range(4):
        f.append(arrow(cx + cw - 15, itr_y[i], cx + cw + 45, itr_y[i], color="#d97706", sw=1.8))

    # --- БЛОК 3: Slave Timer (Праворуч) ---
    sx, sy, sw, sh = 640, 75, 280, 410
    f.append(rect(sx, sy, sw, sh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(sx + sw / 2, sy + 25, "Slave Timer (TIMy)", size=13, bold=True, color=FIELD))

    # Мультиплексор входу тригера (SMCR.TS)
    b_ts, _, _ = textbox(sx + 70, sy + 205, "Trigger Mux\n(SMCR.TS)\n000: ITR0\n001: ITR1\n010: ITR2\n011: ITR3", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=90)
    f.append(b_ts)

    # Вихід TRGI
    f.append(arrow(sx + 120, sy + 205, sx + 170, sy + 205, color=POS, sw=2.0))
    f.append(text(sx + 145, sy + 192, "TRGI", size=10.5, bold=True, color=POS, anchor="middle"))

    # Контролер слейв-режимів (SMCR.SMS)
    b_sms, _, _ = textbox(sx + sw - 55, sy + 205, "Slave Mode\nController\n(SMCR.SMS)", size=9.5, bold=True, fill="#dcfce7", stroke=FIELD, min_w=80)
    f.append(b_sms)

    # Керовані вузли слейва
    b_s_rst, _, _ = textbox(sx + sw / 2, sy + 80, "Скидання лічильника (Reset Mode)", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=220)
    f.append(b_s_rst)

    b_s_gate, _, _ = textbox(sx + sw / 2, sy + 310, "Дозвіл тактування (Gated Mode)", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=220)
    f.append(b_s_gate)

    b_s_ext, _, _ = textbox(sx + sw / 2, sy + 370, "Тактовий імпульс (Ext Clock 1)", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=220)
    f.append(b_s_ext)

    # Керуючі лінії від SMS до вузлів слейва
    f.append(arrow(sx + sw - 55, sy + 165, sx + sw - 55, sy + 102, color=FIELD, sw=1.5))
    f.append(arrow(sx + sw - 55, sy + 245, sx + sw - 55, sy + 288, color=FIELD, sw=1.5))
    f.append(arrow(sx + sw - 55, sy + 332, sx + sw - 55, sy + 348, color=FIELD, sw=1.5))

    return render(os.path.join(IMG_DIR, "timer-trigger-matrix.svg"), W, H, *f)


# ── 2. Часові діаграми слейв-режимів (Slave Modes Timing) ────────────────────
def fig_slave_modes():
    W, H = 940, 560
    f = []

    # Загальне тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 40, "Часові діаграми режимів Slave-таймера відносно сигналу TRGI", size=15, bold=True, color=INK))

    # Загальна шкала часу / сітка
    x_start = 180
    x_end = 890
    t_steps = [x_start + i * 70 for i in range(11)]

    for tx in t_steps:
        f.append(line(tx, 65, tx, H - 40, color="#e2e8f0", sw=1.0, dash="3 3"))

    # Рівень 1: Вхідний сигнал тригера TRGI (від Master TRGO)
    y_trgi = 95
    f.append(text(30, y_trgi + 12, "TRGI (Master TRGO)", size=11, bold=True, color=POS, anchor="start"))
    trgi_path = f"M {x_start} {y_trgi+20} L {t_steps[2]} {y_trgi+20} L {t_steps[2]} {y_trgi-10} L {t_steps[3]} {y_trgi-10} L {t_steps[3]} {y_trgi+20} L {t_steps[6]} {y_trgi+20} L {t_steps[6]} {y_trgi-10} L {t_steps[8]} {y_trgi-10} L {t_steps[8]} {y_trgi+20} L {x_end} {y_trgi+20}"
    f.append(f'<path d="{trgi_path}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    # Рівень 2: Reset Mode (SMS = 0100)
    y_rst = 180
    f.append(text(30, y_rst + 5, "1. Reset Mode\n(SMS = 0100)", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(30, y_rst + 30, "CNT скидається в 0 за фронтом", size=9, color=MUTED, anchor="start"))

    f.append(line(x_start, y_rst + 25, t_steps[2], y_rst - 15, color=NEG, sw=2.0))
    f.append(line(t_steps[2], y_rst - 15, t_steps[2], y_rst + 25, color=NEG, sw=1.5, dash="2 2"))
    f.append(line(t_steps[2], y_rst + 25, t_steps[6], y_rst - 25, color=NEG, sw=2.0))
    f.append(line(t_steps[6], y_rst - 25, t_steps[6], y_rst + 25, color=NEG, sw=1.5, dash="2 2"))
    f.append(line(t_steps[6], y_rst + 25, x_end, y_rst - 20, color=NEG, sw=2.0))

    f.append(text(t_steps[1], y_rst + 10, "0 1 2 3", size=9.5, color=NEG, bold=True))
    f.append(text(t_steps[4], y_rst + 10, "0 1 2 3 4 5 6 7", size=9.5, color=NEG, bold=True))
    f.append(text(t_steps[8], y_rst + 10, "0 1 2 3 4 5", size=9.5, color=NEG, bold=True))

    # Рівень 3: Gated Mode (SMS = 0101)
    y_gate = 280
    f.append(text(30, y_gate + 5, "2. Gated Mode\n(SMS = 0101)", size=10.5, bold=True, color="#d97706", anchor="start"))
    f.append(text(30, y_gate + 30, "Рахує лише коли TRGI = '1'", size=9, color=MUTED, anchor="start"))

    f.append(line(x_start, y_gate + 25, t_steps[2], y_gate + 25, color="#d97706", sw=2.0))
    f.append(line(t_steps[2], y_gate + 25, t_steps[3], y_gate - 5, color="#d97706", sw=2.0))
    f.append(line(t_steps[3], y_gate - 5, t_steps[6], y_gate - 5, color="#d97706", sw=2.0))
    f.append(line(t_steps[6], y_gate - 5, t_steps[8], y_gate - 35, color="#d97706", sw=2.0))
    f.append(line(t_steps[8], y_gate - 35, x_end, y_gate - 35, color="#d97706", sw=2.0))

    f.append(text((t_steps[0] + t_steps[2]) / 2, y_gate + 15, "Стоїть (0)", size=9, color=MUTED))
    f.append(text((t_steps[2] + t_steps[3]) / 2, y_gate + 8, "0 1 2", size=9.5, color="#b45309", bold=True))
    f.append(text((t_steps[3] + t_steps[6]) / 2, y_gate - 18, "Пауза (CNT = 2)", size=9, color=MUTED))
    f.append(text((t_steps[6] + t_steps[8]) / 2, y_gate - 12, "3 4 5 6", size=9.5, color="#b45309", bold=True))
    f.append(text((t_steps[8] + x_end) / 2, y_gate - 48, "Пауза (CNT = 6)", size=9, color=MUTED))

    # Рівень 4: Trigger Mode (SMS = 0110)
    y_trig = 385
    f.append(text(30, y_trig + 5, "3. Trigger Mode\n(SMS = 0110)", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(30, y_trig + 30, "Старт за 1-м фронтом (CEN=1)", size=9, color=MUTED, anchor="start"))

    f.append(line(x_start, y_trig + 25, t_steps[2], y_trig + 25, color=FIELD, sw=2.0))
    f.append(line(t_steps[2], y_trig + 25, x_end, y_trig - 35, color=FIELD, sw=2.0))

    f.append(text((x_start + t_steps[2]) / 2, y_trig + 15, "Вимкнено (CEN=0)", size=9, color=MUTED))
    f.append(text((t_steps[2] + x_end) / 2, y_trig + 5, "Автономний лік: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11... (CEN=1)", size=9.5, color=FIELD, bold=True))

    # Рівень 5: External Clock Mode 1 (SMS = 0111)
    y_ext = 485
    f.append(text(30, y_ext + 5, "4. Ext Clock 1\n(SMS = 0111)", size=10.5, bold=True, color="#7c3aed", anchor="start"))
    f.append(text(30, y_ext + 30, "Тік лічильника = фронт TRGI", size=9, color=MUTED, anchor="start"))

    f.append(line(x_start, y_ext + 25, t_steps[2], y_ext + 25, color="#7c3aed", sw=2.0))
    f.append(line(t_steps[2], y_ext + 25, t_steps[2], y_ext + 5, color="#7c3aed", sw=2.0))
    f.append(line(t_steps[2], y_ext + 5, t_steps[6], y_ext + 5, color="#7c3aed", sw=2.0))
    f.append(line(t_steps[6], y_ext + 5, t_steps[6], y_ext - 15, color="#7c3aed", sw=2.0))
    f.append(line(t_steps[6], y_ext - 15, x_end, y_ext - 15, color="#7c3aed", sw=2.0))

    f.append(text((x_start + t_steps[2]) / 2, y_ext + 15, "CNT = 0", size=9.5, color="#7c3aed", bold=True))
    f.append(text((t_steps[2] + t_steps[6]) / 2, y_ext - 5, "CNT = 1 (фронт 1)", size=9.5, color="#7c3aed", bold=True))
    f.append(text((t_steps[6] + x_end) / 2, y_ext - 25, "CNT = 2 (фронт 2)", size=9.5, color="#7c3aed", bold=True))

    return render(os.path.join(IMG_DIR, "slave-modes-timing.svg"), W, H, *f)


# ── 3. Каскадування лічильників (32-бітний віртуальний таймер) ──────────────
def fig_cascaded_counters():
    W, H = 940, 500
    f = []

    # Загальне тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 42, "Каскадування двох 16-бітних таймерів у 32-бітний лічильник", size=15, bold=True, color=INK))

    # Блок Master (Молодші 16 біт)
    m_x, m_y, m_w, m_h = 50, 85, 360, 240
    f.append(rect(m_x, m_y, m_w, m_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(m_x + m_w / 2, m_y + 25, "Master Timer (TIM2) — Молодші 16 біт", size=12.5, bold=True, color=NEG))

    f.append(text(m_x + 30, m_y + 65, "Вхідний такт CK_INT (84 МГц)", size=10, color=MUTED, anchor="start"))
    f.append(arrow(m_x + 20, m_y + 85, m_x + 60, m_y + 85, color=NEG, sw=1.5))

    b_mpsc, _, _ = textbox(m_x + 110, m_y + 85, "PSC = 0\n(÷1)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=70)
    f.append(b_mpsc)

    f.append(arrow(m_x + 155, m_y + 85, m_x + 195, m_y + 85, color=NEG, sw=1.5))

    b_mcnt, _, _ = textbox(m_x + 270, m_y + 85, "Лічильник CNT_L\n(0x0000 .. 0xFFFF)", size=10, bold=True, fill="#dbeafe", stroke=NEG, min_w=120)
    f.append(b_mcnt)

    b_marr, _, _ = textbox(m_x + 270, m_y + 150, "Регістр ARR = 0xFFFF\n(Період 65536 тактів)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=120)
    f.append(b_marr)

    b_mcfg, _, _ = textbox(m_x + m_w / 2, m_y + 205, "CR2.MMS = 010 (Update Event UEV на TRGO)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=280)
    f.append(b_mcfg)

    # Вихід TRGO майстра
    f.append(arrow(m_x + m_w, m_y + 85, m_x + m_w + 110, m_y + 85, color=POS, sw=2.2))
    f.append(text(m_x + m_w + 55, m_y + 72, "TRGO (UEV такт)", size=10.5, bold=True, color=POS, anchor="middle"))
    f.append(text(m_x + m_w + 55, m_y + 102, "1 такт / 65536 імпульсів", size=9, color=MUTED, anchor="middle"))

    # Блок Slave (Старші 16 біт)
    s_x, s_y, s_w, s_h = 530, 85, 360, 240
    f.append(rect(s_x, s_y, s_w, s_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(s_x + s_w / 2, s_y + 25, "Slave Timer (TIM3) — Старші 16 біт", size=12.5, bold=True, color=FIELD))

    b_stsel, _, _ = textbox(s_x + 80, s_y + 85, "Вхід ITR1 (TRGI)\nSMCR.TS = 001", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=95)
    f.append(b_stsel)

    f.append(arrow(s_x + 135, s_y + 85, s_x + 185, s_y + 85, color=FIELD, sw=1.5))

    b_smode, _, _ = textbox(s_x + 265, s_y + 85, "Ext Clock Mode 1\nSMCR.SMS = 111", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=120)
    f.append(b_smode)

    b_scnt, _, _ = textbox(s_x + 265, s_y + 150, "Лічильник CNT_H\n(0x0000 .. 0xFFFF)", size=10, bold=True, fill="#dcfce7", stroke=FIELD, min_w=120)
    f.append(b_scnt)

    f.append(arrow(s_x + 265, s_y + 115, s_x + 265, s_y + 130, color=FIELD, sw=1.5))

    b_scfg, _, _ = textbox(s_x + s_w / 2, s_y + 205, "Інкремент CNT_H строго за переповненням Master", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=280)
    f.append(b_scfg)

    # Нижня частина: Формування 32-бітного значення та атомарне читання
    f.append(rect(50, 350, W - 100, 120, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(W / 2, 375, "Формування 32-бітного віртуального таймера: uint32_t T = (CNT_H << 16) | CNT_L", size=11.5, bold=True, color=INK))

    # Схема подвійного читання (Double Read Loop)
    f.append(text(80, 410, "Алгоритм атомарного захисту від гонки переповнення:", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(80, 430, "1. high1 = TIM3->CNT;  2. low = TIM2->CNT;  3. high2 = TIM3->CNT;", size=9.5, color=INK, anchor="start"))
    f.append(text(80, 450, "4. Якщо high1 == high2 → значення узгоджене. Якщо ні → повторити зчитування.", size=9.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG_DIR, "cascaded-counters.svg"), W, H, *f)


# ── 4. Синхронізація ШІМ інвертора та вибірки АЦП ───────────────────────────
def fig_inverter_adc():
    W, H = 940, 540
    f = []

    # Загальне тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 40, "Синхронізація Center-Aligned ШІМ інвертора та вибірки АЦП (TRGO на піку)", size=15, bold=True, color=INK))

    x0 = 160
    x_peak = 520
    x_end = 880
    y_carrier = 160

    # 1. Трикутний сигнал носія (Center-Aligned Counter CNT)
    f.append(text(30, y_carrier + 10, "TIM1 CNT\n(Up-Down Mode)", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(line(x0, y_carrier + 40, x_peak, y_carrier - 60, color=NEG, sw=2.2)) # вгору
    f.append(line(x_peak, y_carrier - 60, x_end, y_carrier + 40, color=NEG, sw=2.2)) # вниз

    # Рівні ARR та CCR
    f.append(line(x0 - 20, y_carrier - 60, x_end + 20, y_carrier - 60, color="#94a3b8", sw=1.0, dash="3 3"))
    f.append(text(x0 - 25, y_carrier - 56, "ARR (Пік)", size=9.5, color=MUTED, anchor="end"))

    f.append(line(x0 - 20, y_carrier, x_end + 20, y_carrier, color="#94a3b8", sw=1.0, dash="3 3"))
    f.append(text(x0 - 25, y_carrier + 4, "CCR1 (Поріг ШІМ)", size=9.5, color=MUTED, anchor="end"))

    # Вертикальна лінія піку
    f.append(line(x_peak, y_carrier - 70, x_peak, H - 40, color=POS, sw=1.5, dash="4 3"))

    # 2. Комплементарні виходи на затвори транзисторів
    # High-Side FET
    y_hs = 245
    f.append(text(30, y_hs + 10, "High-Side FET\n(Верхній ключ)", size=10, bold=True, color=INK, anchor="start"))
    hs_path = f"M {x0} {y_hs+15} L {x0+140} {y_hs+15} L {x0+140} {y_hs-15} L {x_end-140} {y_hs-15} L {x_end-140} {y_hs+15} L {x_end} {y_hs+15}"
    f.append(f'<path d="{hs_path}" fill="none" stroke="{INK}" stroke-width="2.0"/>')

    # Low-Side FET (з мертвим часом Dead-Time)
    y_ls = 325
    f.append(text(30, y_ls + 10, "Low-Side FET\n(Нижній ключ, шунт)", size=10, bold=True, color=INK, anchor="start"))
    ls_path = f"M {x0} {y_ls-15} L {x0+110} {y_ls-15} L {x0+110} {y_ls+15} L {x_end-110} {y_ls+15} L {x_end-110} {y_ls-15} L {x_end} {y_ls-15}"
    f.append(f'<path d="{ls_path}" fill="none" stroke="{INK}" stroke-width="2.0"/>')

    # Позначення мертвого часу (Dead-Time)
    f.append(rect(x0 + 110, y_ls - 22, 30, 44, fill="#fee2e2", stroke=POS, sw=1.0))
    f.append(text(x0 + 125, y_ls - 26, "DT", size=9.5, color=POS, bold=True))

    # 3. Вихідний тригер TRGO (MMS = Update / Compare 4)
    y_trgo = 405
    f.append(text(30, y_trgo + 10, "TRGO Імпульс\n(CR2.MMS = Update)", size=10, bold=True, color=POS, anchor="start"))
    trgo_path = f"M {x0} {y_trgo+15} L {x_peak-20} {y_trgo+15} L {x_peak-20} {y_trgo-15} L {x_peak+20} {y_trgo-15} L {x_peak+20} {y_trgo+15} L {x_end} {y_trgo+15}"
    f.append(f'<path d="{trgo_path}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    # 4. Вікно вибірки АЦП (ADC Sample & Hold Window)
    y_adc = 475
    f.append(text(30, y_adc + 10, "ADC1/ADC2\nInjected Trigger", size=10, bold=True, color=FIELD, anchor="start"))

    f.append(rect(x_peak - 20, y_adc - 15, 90, 30, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(x_peak + 25, y_adc + 5, "Вибірка струму S&H", size=9.5, bold=True, color=FIELD))

    # Пояснювальний блок
    f.append(rect(x_peak + 80, y_carrier - 50, 240, 60, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=6))
    f.append(text(x_peak + 200, y_carrier - 32, "Ідеальна точка заміру струму:", size=9.5, bold=True, color="#0284c7"))
    f.append(text(x_peak + 200, y_carrier - 14, "Комутаційний шум dV/dt згас (шунт стабільний)", size=9.5, color=MUTED))

    return render(os.path.join(IMG_DIR, "inverter-adc-synchronization.svg"), W, H, *f)


# ── 5. Апаратний частотомір на зв'язаних таймерах ────────────────────────────
def fig_frequency_meter():
    W, H = 940, 500
    f = []

    # Загальне тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 42, "Апаратний частотомір: стробування лічильника імпульсів через TRGO", size=15, bold=True, color=INK))

    # Блок 1: Master Timer (Timebase 1.000000 с)
    m_x, m_y, m_w, m_h = 50, 85, 370, 240
    f.append(rect(m_x, m_y, m_w, m_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(m_x + m_w / 2, m_y + 25, "Master Timer (TIM2) — База часу (Gate Time)", size=12, bold=True, color=NEG))

    b_clk, _, _ = textbox(m_x + 95, m_y + 80, "Кварцовий такт\n84 МГц (±5 ppm)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=105)
    f.append(b_clk)

    f.append(arrow(m_x + 155, m_y + 80, m_x + 205, m_y + 80, color=NEG, sw=1.5))

    b_psc, _, _ = textbox(m_x + 275, m_y + 80, "PSC = 8399\n(Частота 10 кГц)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=105)
    f.append(b_psc)

    b_arr, _, _ = textbox(m_x + m_w / 2, m_y + 150, "ARR = 9999 (Період T_gate = 1.000000 с)\nCCR1 = 5000 (ШІМ 50% або строб CEN)", size=9.5, bold=True, fill="#dbeafe", stroke=NEG, min_w=280)
    f.append(b_arr)

    b_mms, _, _ = textbox(m_x + m_w / 2, m_y + 210, "CR2.MMS = 001 (CEN) або 100 (OC1REF строб)", size=9.5, bold=True, fill="#ffffff", stroke=NEG, min_w=280)
    f.append(b_mms)

    # Вихід TRGO до Slave
    f.append(arrow(m_x + m_w, m_y + 150, m_x + m_w + 100, m_y + 150, color=POS, sw=2.2))
    f.append(text(m_x + m_w + 50, m_y + 135, "TRGO (ITR1)", size=10.5, bold=True, color=POS, anchor="middle"))
    f.append(text(m_x + m_w + 50, m_y + 170, "Строб t = 1.0 с", size=9, color=MUTED, anchor="middle"))

    # Блок 2: Slave Timer (Pulse Counter)
    s_x, s_y, s_w, s_h = 520, 85, 370, 240
    f.append(rect(s_x, s_y, s_w, s_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(s_x + s_w / 2, s_y + 25, "Slave Timer (TIM3) — Лічильник імпульсів", size=12, bold=True, color=FIELD))

    # Зовнішній сигнал частоти
    f.append(text(s_x + 30, m_y + 65, "Вхід f_in (Pin ETR / TI1)", size=9.5, bold=True, color=INK, anchor="start"))
    f.append(arrow(s_x + 20, m_y + 85, s_x + 70, m_y + 85, color=INK, sw=1.8))

    b_extin, _, _ = textbox(s_x + 125, s_y + 85, "External Clock\n(f_in ≤ 50 МГц)", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=90)
    f.append(b_extin)

    f.append(arrow(s_x + 175, s_y + 85, s_x + 225, s_y + 85, color=FIELD, sw=1.5))

    b_gate, _, _ = textbox(s_x + 285, s_y + 85, "Gated Mode\nSMCR.SMS = 0101", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=95)
    f.append(b_gate)

    b_scnt, _, _ = textbox(s_x + s_w / 2, s_y + 150, "Лічильник CNT акумулює імпульси при TRGI = '1'\nЗа 1 секунду CNT накопичує N = f_in × 1.0", size=9.5, bold=True, fill="#dcfce7", stroke=FIELD, min_w=280)
    f.append(b_scnt)

    b_dma, _, _ = textbox(s_x + s_w / 2, s_y + 210, "DMA / IRQ по спаду TRGI: читання без затримок CPU", size=9.5, bold=True, fill="#ffffff", stroke=FIELD, min_w=280)
    f.append(b_dma)

    # Нижня частина: Формула та переваги
    f.append(rect(50, 350, W - 100, 120, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(W / 2, 375, "Результат: Частота f_in = N_pulses / T_gate [Гц]", size=12, bold=True, color=INK))

    f.append(text(80, 410, "• 0% навантаження CPU: апаратний строб відкриває і закриває лічбу без переривань;", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 430, "• 0 нс програмного джитеру: тривалість стробу квантована виключно стабільністю кварцу;", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 450, "• Похибка вимірювання становить ±1 імпульс (дискретність лічби) + похибка кварцу (ppm).", size=10, color=MUTED, anchor="start"))

    return render(os.path.join(IMG_DIR, "frequency-meter-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trigger_matrix()
    fig_slave_modes()
    fig_cascaded_counters()
    fig_inverter_adc()
    fig_frequency_meter()
    print("All figures generated successfully.")
